# 🚀 Resume Analyzer RAG - Quick Reference

## ⚡ Start the Application

### One-Command Setup (First Time)
```powershell
.\setup.ps1              # Windows PowerShell (Recommended)
# OR
setup.bat               # Windows Batch
```

### Manual Startup (After Setup)
```powershell
# Terminal 1: API Server
uv run python run_server.py

# Terminal 2: Frontend
uv run streamlit run frontend/app.py
```

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:8501 | Upload & Search |
| API | http://localhost:8000 | REST endpoints |
| API Docs | http://localhost:8000/docs | Interactive documentation |
| ReDoc | http://localhost:8000/redoc | API reference |

## 📦 UV Commands (Most Used)

```powershell
# Setup
uv venv                 # Create virtual environment
uv sync                 # Install dependencies

# Running Code
uv run python script.py # Run Python script
uv run streamlit run app.py  # Run Streamlit

# Package Management
uv add package-name     # Add dependency
uv pip list             # List installed packages
uv pip show package     # Show package info

# Development
uv run black .          # Format code
uv run isort .          # Sort imports
uv run ruff check .     # Lint code
uv run pytest tests/    # Run tests
```

## 🧪 Testing

```powershell
# Connectivity Test (all services)
uv run python test_connections.py

# Integration Test (RAG chain)
uv run python test_chain.py

# Expected: All tests PASSED ✓
```

## 🔧 Environment Setup

### Create .env file in project root:
```env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MISTRAL_API_KEY=your-mistral-key
OPENROUTER_API_KEY=your-openrouter-key
```

⚠️ Never commit `.env` to git!

## 📝 API Endpoints

```powershell
# Health Check
curl http://localhost:8000/health

# Get Stats
curl http://localhost:8000/stats

# Upload Resume (requires PDF file)
curl -X POST http://localhost:8000/upload -F "file=@resume.pdf"

# Search Resumes
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Python developer","top_k":5}'
```

## 📁 Project Structure

```
ResumeAnalyzer/
├── backend/
│   ├── main.py         # FastAPI app
│   ├── rag_pipeline.py # RAG chain
│   └── database.py     # MongoDB
├── frontend/
│   └── app.py          # Streamlit UI
├── run_server.py       # Start API
├── test_*.py           # Tests
├── pyproject.toml      # Config
├── .env                # Secrets (CREATE THIS)
└── README.md           # Documentation
```

## 🆘 Troubleshooting

### API won't start
```powershell
# Port 8000 in use?
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### Dependencies error
```powershell
rm -r .venv
uv venv
uv sync
```

### Permission error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Can't find API
- Check .env file exists in project root
- Check all API keys are valid
- Run: `uv run python test_connections.py`

## 💡 Tips & Tricks

```powershell
# Fast dependency check
uv pip list

# Update single package
uv add package-name --upgrade

# Run with specific Python version
uv venv --python 3.14

# Check Python versions
uv python list

# Update all dependencies
uv sync --upgrade

# Clean cache
uv cache clean

# Verbose logging
uv run --verbose python script.py
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Complete documentation |
| UV_SETUP_GUIDE.md | Detailed UV instructions |
| APPLICATION_IMPROVEMENTS.md | Changes summary |
| FAILURE_ANALYSIS.md | Troubleshooting guide |
| CONNECTIVITY_FIXES.md | Technical details |
| FINAL_SUMMARY.md | Project overview |

## 🔐 Security Checklist

- [ ] .env file created
- [ ] API keys filled in .env
- [ ] .env added to .gitignore
- [ ] No API keys in code
- [ ] SSL/TLS for production
- [ ] Rate limiting enabled
- [ ] Database backups configured

## 🎯 Common Workflows

### Develop Feature
```powershell
uv run python run_server.py    # Terminal 1
uv run streamlit run frontend/app.py  # Terminal 2
# Make changes...
uv run black .     # Format
uv run isort .     # Sort imports
uv run ruff check .  # Lint
```

### Deploy to Production
```powershell
uv build           # Create package
docker build -t resume-analyzer .
docker push resume-analyzer:latest
```

### Run Tests
```powershell
uv run python test_connections.py
uv run python test_chain.py
uv run pytest tests/ -v
```

## 📊 Performance Monitoring

### Check Logs
- Terminal 1: API logs with request details
- Terminal 2: Streamlit logs with UI interactions

### Monitor API
```powershell
# Health status
curl http://localhost:8000/health

# Collection stats
curl http://localhost:8000/stats
```

### Monitor Resources
```powershell
# CPU/Memory
Get-Process python | Select-Object Name, CPU, Memory

# Port usage
netstat -ano | findstr :8000 :8501
```

## 🚢 Deployment Checklist

- [ ] All tests passing
- [ ] .env configured on server
- [ ] MongoDB Atlas accessible
- [ ] API keys valid
- [ ] Firewall rules configured
- [ ] SSL certificate installed
- [ ] Logs monitoring setup
- [ ] Backups automated

## 📞 Quick Support

**Issue:** API won't start
- Check ports: `netstat -ano | findstr :8000`
- Check logs in terminal window
- Verify .env file exists

**Issue:** Connectivity test fails
- Check .env file with correct keys
- Verify MongoDB connection
- Test internet connectivity

**Issue:** Slow performance
- Check server resources
- Review MongoDB indexes
- Monitor API logs

## 🎓 Learning Path

1. **Start Here:** README.md
2. **Setup Guide:** UV_SETUP_GUIDE.md
3. **API Docs:** http://localhost:8000/docs
4. **Code:** backend/ and frontend/
5. **Advanced:** Deployment guides

## 💬 Example Queries

```
"Find candidates with Python experience"
"Who has experience with machine learning?"
"List senior developers with 10+ years experience"
"Show me people with cloud platform experience"
"Find backend developers with database skills"
```

---

**Need help?** Check the documentation or run: `uv run python test_connections.py`

**Ready to go?** Run: `.\setup.ps1`

---

*Last Updated: March 14, 2026*
*Version: 1.0.0*
