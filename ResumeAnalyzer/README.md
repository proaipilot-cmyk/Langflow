# 📄 Resume Analyzer RAG

An AI-powered resume search and analysis system using Retrieval-Augmented Generation (RAG). Upload multiple resume PDFs and ask natural language questions to get intelligent answers powered by LangChain, Mistral AI, and MongoDB.

## 🎯 Features

- **🔍 Intelligent Search:** Ask natural questions about candidate profiles
- **📤 Batch Upload:** Upload multiple PDFs at once
- **⚡ Fast Retrieval:** Vector similarity search on 615+ documents
- **🤖 AI-Powered Answers:** LLM-generated responses based on resume content
- **📊 Real-time Statistics:** Monitor document collection status
- **💻 Professional UI:** Clean, intuitive Streamlit interface
- **🔧 RESTful API:** FastAPI with interactive documentation
- **🛡️ Robust Error Handling:** Comprehensive validation and logging

## 🏗️ Architecture

```
┌─────────────────────┐
│  Streamlit Frontend │ ← User Interface
└──────────┬──────────┘
           │ HTTP
┌──────────▼──────────────┐
│   FastAPI Backend       │ ← REST API
│  ├─ Upload Handler     │
│  ├─ Search Processor   │
│  └─ Health Checks      │
└──────────┬──────────────┘
           │
    ┌──────┴────────────────┬─────────────┐
    │                       │             │
┌───▼────────┐    ┌────────▼─────┐  ┌───▼──────────┐
│  MongoDB   │    │ Mistral AI   │  │ OpenRouter   │
│  Atlas VDB │    │ Embeddings   │  │ LLM Model    │
└────────────┘    └──────────────┘  └──────────────┘
```

## 📋 Prerequisites

- **Python:** 3.12+ (3.14 recommended)
- **UV:** Fast Python package manager
- **MongoDB Atlas:** Cloud database with vector search
- **API Keys:**
  - Mistral AI (for embeddings)
  - OpenRouter (for LLM)
  - Optional: Groq, OpenAI

## 🚀 Quick Start

### 1. Clone and Setup
```powershell
# Navigate to project
cd C:\TrainingDocs\PracticeFiles\ResumeAnalyzer

# Run setup script (automated)
.\setup.ps1
# OR for batch file
setup.bat
```

### 2. Manual Setup (if needed)
```powershell
# Create virtual environment
uv venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv sync
```

### 3. Configure Environment
Create a `.env` file in the project root:
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MISTRAL_API_KEY=your-mistral-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
```

### 4. Test Connectivity
```powershell
uv run python test_connections.py
```

Expected output: **5/5 tests PASSED**

### 5. Run the Application

**Terminal 1 - Start API Server:**
```powershell
uv run python run_server.py
```
API available at: http://localhost:8000

**Terminal 2 - Start Streamlit Frontend:**
```powershell
uv run streamlit run frontend/app.py
```
Frontend available at: http://localhost:8501

## 📚 Usage

### Upload Resumes
1. Go to **Upload Resumes** tab
2. Select one or multiple PDF files
3. Click **Upload Files**
4. Monitor progress and chunk count

### Search Resumes
1. Go to **Search** tab
2. Enter your query (e.g., "Find Python developers with 5+ years experience")
3. Click **Search**
4. View AI-generated answer
5. Check search history for previous queries

### API Documentation
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### API Endpoints

```
GET /health
├─ Status: Service health check
└─ Response: {"status": "healthy", "service": "Resume Analyzer RAG API"}

POST /upload
├─ Body: {file: PDF file}
├─ Validation: PDF only, max 50MB
└─ Response: {"status": "uploaded", "filename": "...", "chunks_ingested": N}

POST /search
├─ Body: {"query": "...", "top_k": 5}
├─ Validation: Non-empty, max 500 characters
└─ Response: {"answer": "...", "sources": [...]}

GET /stats
├─ Response: {"total_documents": N, "status": "ready|empty"}
```

## 🧪 Testing

### Connectivity Tests
```powershell
# Test all services
uv run python test_connections.py
```

Validates:
- ✓ Environment variables loaded
- ✓ MongoDB connection
- ✓ Mistral AI API
- ✓ OpenRouter API
- ✓ Vector search index

### Integration Tests
```powershell
# Test RAG chain with sample queries
uv run python test_chain.py
```

Validates:
- ✓ RAG chain building
- ✓ Query execution
- ✓ Response generation

## 📁 Project Structure

```
ResumeAnalyzer/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── rag_pipeline.py      # RAG chain & embeddings
│   ├── database.py          # MongoDB connection
│   └── __pycache__/
├── frontend/
│   └── app.py               # Streamlit UI
├── test_connections.py      # Service tests
├── test_chain.py            # Integration tests
├── run_server.py            # API server launcher
├── setup.ps1 / setup.bat    # Setup scripts
├── pyproject.toml           # Project config (UV)
├── .env                     # Environment variables (CREATE THIS)
├── .gitignore              # Git ignore rules
├── requirements.txt         # Legacy pip requirements
└── README.md               # This file
```

## 🔧 Configuration

### UV Commands
```powershell
# Install dependencies
uv sync

# Add a package
uv add <package-name>

# Update packages
uv sync --upgrade

# Run Python with UV
uv run python script.py

# Run tests
uv run pytest tests/ -v
```

### pyproject.toml
Configured for:
- Python 3.12+
- All required dependencies
- Optional dev dependencies
- Tool configurations (black, isort, ruff, mypy)

See `UV_SETUP_GUIDE.md` for detailed UV documentation.

## 🛠️ Troubleshooting

### API Won't Start
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F
```

### Connection Issues
```powershell
# Test MongoDB connection
uv run python test_connections.py

# Check .env file is in project root
# Ensure all required API keys are set
```

### Dependencies Error
```powershell
# Clean and reinstall
rm -r .venv
uv venv
uv sync
```

### Permission Issues
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

## 📖 Documentation

- **[UV Setup Guide](UV_SETUP_GUIDE.md)** - Detailed UV usage and commands
- **[Failure Analysis](FAILURE_ANALYSIS.md)** - Troubleshooting guide
- **[Connectivity Fixes](CONNECTIVITY_FIXES.md)** - Connection improvements
- **[Application Improvements](APPLICATION_IMPROVEMENTS.md)** - Code changes summary

## 🔐 Security

- API keys stored in `.env` (not in code)
- Input validation on all endpoints
- File size limits (50MB max)
- Query length limits (500 characters)
- Error messages don't leak sensitive data
- MongoDB connection pooling

## 📊 Performance

- **Async operations** for non-blocking requests
- **Connection pooling** (10-50 MongoDB connections)
- **Timeouts** configured to prevent hanging
- **Retry logic** with exponential backoff
- **Vector search** for fast similarity matching

## 🚢 Deployment

### Docker Deployment
```dockerfile
FROM python:3.14-slim
WORKDIR /app
RUN pip install uv
COPY . .
RUN uv venv && uv sync
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Settings
```powershell
# Run without reload
uv run python -c "import uvicorn; uvicorn.run('backend.main:app', host='0.0.0.0', port=8000)"

# Use Gunicorn for ASGI
uv run pip install gunicorn
uv run gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📦 Dependencies

### Core
- **FastAPI** - Web framework
- **Streamlit** - Frontend
- **LangChain** - RAG framework
- **MongoDB** - Vector database
- **Mistral AI** - Embeddings
- **OpenRouter** - LLM provider

### Utilities
- **Tenacity** - Retry logic
- **Pydantic** - Data validation
- **UV** - Package manager

See `pyproject.toml` for complete list.

## 📝 API Examples

### Upload Resume
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@resume.pdf"
```

### Search Resumes
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "Python developer", "top_k": 5}'
```

### Get Statistics
```bash
curl "http://localhost:8000/stats"
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Format code: `uv run black .`
3. Sort imports: `uv run isort .`
4. Lint: `uv run ruff check .`
5. Test: `uv run pytest tests/`
6. Commit: `git commit -m "Add amazing feature"`
7. Push: `git push origin feature/amazing-feature`

## 📄 License

This project is provided as-is for educational and commercial use.

## 🆘 Support

For issues and questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review documentation files
3. Run connectivity tests: `uv run python test_connections.py`
4. Check logs in terminal windows

## 🎉 What's Included

✅ Production-ready backend API  
✅ Professional frontend UI  
✅ Comprehensive error handling  
✅ Detailed logging  
✅ Input validation  
✅ Service health monitoring  
✅ Complete test suite  
✅ API documentation  
✅ Setup automation  
✅ Security best practices  

---

**Ready to analyze resumes with AI?** 🚀

Start with `.\setup.ps1` or check [Quick Start](#-quick-start) section!
