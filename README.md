# 📄 Ask Your Data

This application allows you to interact with a Large Language Model (LLM) based on **your own data** using Retrieval-Augmented Generation (RAG). Upload documents, ask questions, and get intelligent, context-aware answers directly from your files.

---

## 🧠 Document Q&A System (RAG-Based)

A web application that enables:

- 📤 Uploading of various documents (PDFs, text, etc.)
- 🌐 Embedding using **multilingual sentence transformers**
- 🧠 Storage and similarity search using **FAISS** for efficient document retrieval
- 💬 Chatting with an LLM assistant that answers questions based only on the uploaded data (not its pretraining)

This is a classic **RAG (Retrieval-Augmented Generation)** pipeline:
1. **Retrieve**: Search relevant chunks from your documents using embeddings.
2. **Augment**: Inject retrieved chunks into the LLM’s prompt.
3. **Generate**: Get accurate, grounded answers that reference your actual data.

## Features

- **Document Upload**: Upload various document formats
- **Text Embedding**: Uses `intfloat/multilingual-e5-large` for multilingual embeddings
- **Vector Storage**: FAISS for efficient similarity search
- **Reranking**: Uses `BAAI/bge-reranker-v2-m3` for improved retrieval
- **AI Chat**: Powered by Ollama with qwen2.5 model
- **Modern UI**: React-based frontend with real-time chat

## Setup

### Prerequisites

1. Python 3.8+
2. Node.js 16+
3. Ollama installed and running with qwen2.5:1.5 model

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
python main.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

1. Open the application in your browser
2. Upload documents using the file upload interface
3. Wait for the documents to be processed and embedded
4. Start chatting with the AI assistant about your documents

## API Endpoints

- `POST /upload`: Upload and process documents
- `POST /chat`: Send chat messages and get AI responses
- `GET /health`: Health check endpoint

## Architecture

- **Backend**: FastAPI with async processing
- **Frontend**: React with modern UI components
- **Vector DB**: FAISS for similarity search
- **Embedding**: SentenceTransformer for document chunks
- **Reranking**: CrossEncoder for improved retrieval
- **LLM**: Ollama with qwen2.5:1.5 model 
