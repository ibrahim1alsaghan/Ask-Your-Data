import os
import json
import asyncio
from typing import List, Dict, Any
from pathlib import Path
import tempfile
import shutil

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
import torch
import requests
import tiktoken

# Initialize FastAPI app
app = FastAPI(title="Document Q&A System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models and FAISS index
embedder = None
reranker = None
faiss_index = None
documents = []
document_embeddings = []

# Configuration
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K = 5
OLLAMA_URL = "http://localhost:11434/api/generate"

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: List[str]

def initialize_models():
    """Initialize the embedding and reranking models"""
    global embedder, reranker
    
    print("Loading embedding model...")
    embedder = SentenceTransformer("intfloat/multilingual-e5-large")
    
    print("Loading reranking model...")
    reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")
    
    print("Models loaded successfully!")

def create_faiss_index(dimension: int):
    """Create a new FAISS index"""
    global faiss_index
    faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    print(f"Created FAISS index with dimension {dimension}")

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks

def extract_text_from_file(file_path: str) -> str:
    """Extract text from various file formats"""
    file_extension = Path(file_path).suffix.lower()
    
    try:
        if file_extension in ['.txt']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_extension in ['.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_extension in ['.json']:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        else:
            # For other file types, try to read as text
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

async def process_document(file_path: str, filename: str):
    """Process a document: extract text, chunk it, embed it, and store in FAISS"""
    global documents, document_embeddings, faiss_index
    
    print(f"Processing document: {filename}")
    
    # Extract text from file
    text = extract_text_from_file(file_path)
    if not text.strip():
        print(f"No text extracted from {filename}")
        return
    
    # Chunk the text
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks from {filename}")
    
    # Embed chunks
    embeddings = embedder.encode(chunks, convert_to_tensor=True)
    embeddings = embeddings.cpu().numpy()
    
    # Add to FAISS index
    if faiss_index is None:
        create_faiss_index(embeddings.shape[1])
    
    faiss_index.add(embeddings)
    
    # Store document information
    for i, chunk in enumerate(chunks):
        documents.append({
            "filename": filename,
            "chunk_id": i,
            "text": chunk,
            "embedding_id": len(document_embeddings) + i
        })
    
    document_embeddings.extend(embeddings)
    
    print(f"Successfully processed {filename} with {len(chunks)} chunks")

async def query_ollama(prompt: str) -> str:
    """Query Ollama API"""
    try:
        payload = {
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "Sorry, I couldn't generate a response.")
    
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return "Sorry, there was an error connecting to the AI model."

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    initialize_models()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "models_loaded": embedder is not None and reranker is not None}

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Process document in background
        background_tasks.add_task(process_document, temp_path, file.filename)
        
        return {"message": f"File {file.filename} uploaded successfully and is being processed"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the AI assistant"""
    try:
        if faiss_index is None or len(documents) == 0:
            return ChatResponse(
                response="Please upload some documents first so I can help you with your questions.",
                sources=[]
            )
        
        # Embed the user's question
        question_embedding = embedder.encode([request.message], convert_to_tensor=True)
        question_embedding = question_embedding.cpu().numpy()
        
        # Search for similar documents
        scores, indices = faiss_index.search(question_embedding, min(TOP_K * 2, len(documents)))
        
        # Get the retrieved documents
        retrieved_docs = [documents[idx] for idx in indices[0] if idx < len(documents)]
        
        if not retrieved_docs:
            return ChatResponse(
                response="I couldn't find any relevant information in the uploaded documents.",
                sources=[]
            )
        
        # Prepare documents for reranking
        pairs = [[request.message, doc["text"]] for doc in retrieved_docs]
        
        # Rerank documents
        rerank_scores = reranker.predict(pairs)
        
        # Sort by rerank scores and get top 5
        doc_score_pairs = list(zip(retrieved_docs, rerank_scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        top_docs = doc_score_pairs[:TOP_K]
        
        # Prepare context for the AI
        context = "\n\n".join([f"Document {i+1} (from {doc['filename']}):\n{doc['text']}" 
                              for i, (doc, score) in enumerate(top_docs)])
        
        # Create prompt for Ollama
        prompt = f"""You are an AI assistant that will answer the question based on this data:

{context}

Question: {request.message}

Please provide a comprehensive answer based only on the information provided in the documents above. If the documents don't contain enough information to answer the question, please say so."""

        # Get response from Ollama
        response = await query_ollama(prompt)
        
        # Prepare sources
        sources = [f"{doc['filename']} (chunk {doc['chunk_id']})" for doc, _ in top_docs]
        
        return ChatResponse(response=response, sources=sources)
    
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.get("/documents")
async def get_documents():
    """Get information about uploaded documents"""
    if not documents:
        return {"documents": []}
    
    # Group documents by filename
    doc_groups = {}
    for doc in documents:
        filename = doc["filename"]
        if filename not in doc_groups:
            doc_groups[filename] = []
        doc_groups[filename].append(doc)
    
    return {
        "documents": [
            {
                "filename": filename,
                "chunks": len(chunks),
                "total_chars": sum(len(chunk["text"]) for chunk in chunks)
            }
            for filename, chunks in doc_groups.items()
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 