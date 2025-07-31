# Setup Guide for Document Q&A System

This guide will help you set up and run the Document Q&A System on your local machine.

## Prerequisites

Before starting, ensure you have the following installed:

### 1. Python 3.8+
```bash
# Check Python version
python3 --version

# If not installed, download from https://python.org
```

### 2. Node.js 16+
```bash
# Check Node.js version
node --version

# If not installed, download from https://nodejs.org
```

### 3. Ollama
```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull the required model
ollama pull qwen2.5:1.5
```

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Make the startup script executable
chmod +x start.sh

# Run the automated setup
./start.sh
```

This script will:
- Install all Python dependencies
- Install all Node.js dependencies
- Start the backend server
- Start the frontend server
- Open the application in your browser

### Option 2: Manual Setup

#### Step 1: Install Python Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt
```

#### Step 2: Install Node.js Dependencies
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Return to root directory
cd ..
```

#### Step 3: Start Backend Server
```bash
# Start the FastAPI backend
python main.py
```

The backend will be available at `http://localhost:8000`

#### Step 4: Start Frontend Server
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Start the React development server
npm start
```

The frontend will be available at `http://localhost:3000`

## System Architecture

### Backend (FastAPI)
- **Port**: 8000
- **Features**:
  - Document upload and processing
  - Text chunking and embedding
  - FAISS vector storage
  - AI chat with Ollama integration
  - RESTful API endpoints

### Frontend (React)
- **Port**: 3000
- **Features**:
  - Modern, responsive UI
  - Drag-and-drop file upload
  - Real-time chat interface
  - Document management
  - Tabbed navigation

### AI Models Used
1. **Embedding Model**: `intfloat/multilingual-e5-large`
   - Used for creating vector embeddings of document chunks
   - Supports multiple languages

2. **Reranking Model**: `BAAI/bge-reranker-v2-m3`
   - Used to improve retrieval accuracy
   - Reranks initial search results

3. **Language Model**: `qwen2.5:1.5` (via Ollama)
   - Generates responses based on retrieved context
   - Runs locally for privacy and speed

## API Endpoints

### Backend API
- `GET /health` - Health check
- `POST /upload` - Upload and process documents
- `POST /chat` - Send chat messages
- `GET /documents` - Get list of uploaded documents

### Frontend Routes
- `/` - Main application with tabbed interface
- Chat tab - AI conversation interface
- Upload tab - Document upload interface
- Documents tab - Document management

## Usage

### 1. Upload Documents
1. Navigate to the "Upload Documents" tab
2. Drag and drop files or click to browse
3. Supported formats: `.txt`, `.md`, `.json`, `.csv`
4. Maximum file size: 10MB
5. Wait for processing to complete

### 2. Chat with AI
1. Navigate to the "Chat" tab
2. Ask questions about your uploaded documents
3. The AI will search through your documents and provide answers
4. View source documents for each response

### 3. Manage Documents
1. Navigate to the "Documents" tab
2. View uploaded documents and their statistics
3. See processing information (chunks, file size, etc.)

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Error
```
Error: Failed to connect to Ollama
```
**Solution**: Ensure Ollama is running and the model is available
```bash
# Start Ollama
ollama serve

# Check available models
ollama list

# Pull the required model if not available
ollama pull qwen2.5:1.5
```

#### 2. Port Already in Use
```
Error: Address already in use
```
**Solution**: Kill processes using the ports
```bash
# For port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# For port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

#### 3. Model Loading Issues
```
Error: CUDA out of memory
```
**Solution**: The models will run on CPU by default. If you have GPU issues, ensure you have sufficient RAM (8GB+ recommended).

#### 4. File Upload Errors
```
Error: File type not supported
```
**Solution**: Ensure you're uploading supported file types: `.txt`, `.md`, `.json`, `.csv`

### Performance Optimization

#### For Large Documents
- The system automatically chunks documents into smaller pieces
- Default chunk size: 512 characters with 50 character overlap
- You can modify these settings in `main.py`

#### For Better Response Quality
- Upload multiple related documents for comprehensive answers
- Ask specific questions rather than general ones
- The system retrieves top-5 most relevant chunks for each question

## Development

### Project Structure
```
Test_cursor/
├── main.py                 # FastAPI backend
├── requirements.txt        # Python dependencies
├── start.sh               # Startup script
├── README.md              # Project overview
├── SETUP.md               # This setup guide
├── frontend/              # React frontend
│   ├── package.json
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   └── index.css
│   └── public/
└── sample_documents/      # Test documents
    ├── sample.txt
    └── company_policy.md
```

### Customization

#### Modify Chunk Size
Edit the `CHUNK_SIZE` and `CHUNK_OVERLAP` variables in `main.py`:
```python
CHUNK_SIZE = 512      # Increase for larger chunks
CHUNK_OVERLAP = 50    # Adjust overlap as needed
```

#### Change AI Model
Modify the model name in `main.py`:
```python
# For embedding
embedder = SentenceTransformer("your-preferred-model")

# For reranking
reranker = CrossEncoder("your-preferred-reranker")

# For LLM (in Ollama)
payload = {"model": "your-preferred-model"}
```

#### Add New File Types
Extend the `extract_text_from_file` function in `main.py` to support additional file formats.

## Security Considerations

- The system runs locally, keeping your documents private
- No data is sent to external services (except Ollama API calls)
- Consider implementing authentication for production use
- Regularly update dependencies for security patches

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all prerequisites are installed
3. Check the console logs for error messages
4. Verify Ollama is running and accessible

For additional help, refer to the documentation of the individual components:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Ollama Documentation](https://ollama.ai/docs)
- [FAISS Documentation](https://faiss.ai/) 