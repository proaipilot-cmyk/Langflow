# Resume Analyzer RAG - UV Setup & Usage Guide

## Quick Start with UV

### 1. Install UV (if not already installed)
```powershell
# Option A: Using pipx (recommended)
pipx install uv

# Option B: Using pip
pip install uv

# Option C: Using Windows installer
# Download from: https://github.com/astral-sh/uv/releases
```

### 2. Verify UV Installation
```powershell
uv --version
# Should output: uv 0.x.x
```

### 3. Create Virtual Environment & Install Dependencies
```powershell
# Navigate to project directory
cd C:\TrainingDocs\PracticeFiles\ResumeAnalyzer

# Create virtual environment (uv automatically creates .venv)
uv venv

# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies from pyproject.toml
uv sync

# Install with dev dependencies (optional)
uv sync --extra dev
```

### 4. Verify Installation
```powershell
# Check installed packages
uv pip list

# Run connectivity tests
uv run python test_connections.py

# Run integration tests
uv run python test_chain.py
```

---

## Running the Application

### Option 1: Run API Server
```powershell
# Start FastAPI server
uv run python run_server.py

# Server will be available at:
# - http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Option 2: Run Streamlit Frontend
```powershell
# In a separate terminal, run the Streamlit app
uv run streamlit run frontend/app.py

# App will open at http://localhost:8501
```

### Option 3: Run Both (Recommended)
```powershell
# Terminal 1: Start API Server
uv run python run_server.py

# Terminal 2: Start Streamlit Frontend
uv run streamlit run frontend/app.py
```

---

## Common UV Commands

### Managing Dependencies

```powershell
# Add a new dependency
uv pip install <package-name>
uv add <package-name>  # Adds to pyproject.toml

# Add a dev dependency
uv add --dev <package-name>

# Update dependencies
uv sync

# Update specific package
uv pip install --upgrade <package-name>

# List installed packages
uv pip list

# Show package details
uv pip show <package-name>

# Remove a package
uv pip uninstall <package-name>
```

### Running Python Code

```powershell
# Run a Python script
uv run python script.py

# Run a Python command
uv run python -c "print('Hello')"

# Run pytest
uv run pytest

# Run tests with coverage
uv run pytest --cov=backend
```

### Environment Management

```powershell
# Show environment info
uv venv --python 3.14

# List Python versions
uv python list

# Use specific Python version
uv venv --python 3.13

# Clean environment
rm -r .venv
uv venv
uv sync
```

---

## Project Structure

```
ResumeAnalyzer/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── rag_pipeline.py      # RAG chain implementation
│   ├── database.py          # MongoDB setup
│   └── __pycache__/
├── frontend/
│   └── app.py               # Streamlit application
├── test_connections.py      # Service connectivity tests
├── test_chain.py            # RAG chain integration tests
├── run_server.py            # API server launcher
├── pyproject.toml           # UV/Python project config
├── .env                     # Environment variables (CREATE THIS)
├── .venv/                   # Virtual environment (auto-created)
└── README.md
```

---

## Environment Setup

### Create .env File

Create a `.env` file in the project root with:

```env
# MongoDB Connection
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

# Mistral AI (for embeddings)
MISTRAL_API_KEY=your-mistral-api-key-here

# OpenRouter (for LLM)
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Optional: Groq
GROQ_API_KEY=your-groq-api-key-here

# Optional: OpenAI
OPENAI_API_KEY=your-openai-api-key-here
```

⚠️ **Never commit .env to version control!** Add to `.gitignore`:
```
.env
.env.local
.env.*.local
```

---

## Testing & Validation

### Run Connectivity Tests
```powershell
# Test all services (MongoDB, Mistral AI, OpenRouter, Vector Search)
uv run python test_connections.py

# Expected output:
# ✓ Environment Variables: PASSED
# ✓ MongoDB Connection: PASSED
# ✓ Mistral AI Embeddings: PASSED
# ✓ OpenRouter API: PASSED
# ✓ Vector Search Integration: PASSED
```

### Run Integration Tests
```powershell
# Test the complete RAG chain
uv run python test_chain.py

# Expected output:
# ✓ RAG chain built successfully
# ✓ All tests PASSED
```

### Run API Tests
```powershell
# Test API endpoints (requires server running)
uv run pytest tests/ -v

# Test with coverage
uv run pytest tests/ --cov=backend --cov-report=html
```

---

## Troubleshooting

### Issue: "uv: command not found"
```powershell
# Solution: Reinstall UV
pip install --upgrade uv
```

### Issue: Virtual environment not activating
```powershell
# Solution: Manually activate
.\.venv\Scripts\Activate.ps1

# If you get permission error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

### Issue: Dependency conflicts
```powershell
# Solution: Clean and resync
rm -r .venv
uv venv
uv sync
```

### Issue: API not connecting
```powershell
# Check if server is running
# Terminal: uv run python run_server.py

# Verify connectivity
uv run python test_connections.py

# Check logs
# Look for error messages in server terminal
```

### Issue: "ModuleNotFoundError"
```powershell
# Solution: Ensure dependencies are synced
uv sync

# Verify package is installed
uv pip list | findstr <package-name>
```

---

## Performance Tips

### Speed Up Dependencies
```powershell
# UV is faster than pip by default, but you can optimize further:

# 1. Use precompiled wheels
uv sync  # Already uses wheels by default

# 2. Cache packages
# UV caches by default in ~/.cache/uv

# 3. Parallel installation
uv sync  # Parallel by default
```

### Development Workflow
```powershell
# Install with dev dependencies
uv sync --extra dev

# Format code
uv run black .

# Sort imports
uv run isort .

# Lint code
uv run ruff check .

# Type checking
uv run mypy backend/
```

---

## Deployment

### Build Package
```powershell
# Create distribution
uv build

# Creates:
# - dist/resume_analyzer-1.0.0.tar.gz
# - dist/resume_analyzer-1.0.0-py3-none-any.whl
```

### Production Installation
```powershell
# Install from built package
uv pip install dist/resume_analyzer-1.0.0-py3-none-any.whl

# Or from wheel file directly
uv pip install ./dist/*.whl
```

### Docker Deployment
```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install UV
RUN pip install uv

# Copy project
COPY . .

# Create venv and install
RUN uv venv
RUN uv sync

# Activate venv
ENV PATH="/app/.venv/bin:$PATH"

# Run API
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## UV Configuration

### Configure UV (optional)

Create `.uvrc` or set environment variables:

```powershell
# Set Python version preference
$env:UV_PYTHON="3.14"

# Show all options
uv help config
```

---

## Resources

- **UV Documentation**: https://docs.astral.sh/uv/
- **UV GitHub**: https://github.com/astral-sh/uv
- **Python Packaging**: https://packaging.python.org/

---

## Summary

**UV Command Flow:**
```powershell
# 1. Setup (one-time)
uv venv
uv sync

# 2. Development (regular)
uv run python script.py
uv run streamlit run app.py
uv run pytest

# 3. Dependency management
uv add <package>
uv pip list
uv sync
```

**That's it! You're ready to develop with UV.** 🚀
