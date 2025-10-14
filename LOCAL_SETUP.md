# Running TCS Forecasting Agent on Your Local Machine

## Quick Setup Guide

### 1. Prerequisites

Before starting, ensure you have:
- **Python 3.10+** installed ([Download](https://www.python.org/downloads/))
- **PostgreSQL** installed ([Download](https://www.postgresql.org/download/))
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

Check Python version:
```bash
python --version
# Should show Python 3.10 or higher
```

### 2. Download the Project

**Option A: From Replit**
1. In Replit, click the three dots menu
2. Select "Download as ZIP"
3. Extract the ZIP file to your desired location

**Option B: Clone from Git** (if pushed to GitHub)
```bash
git clone <your-repo-url>
cd <project-folder>
```

### 3. Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn
- LangChain & OpenAI
- PostgreSQL driver
- Web scraping tools (BeautifulSoup, pdfplumber)
- All other required packages

### 5. Set Up PostgreSQL Database

**On macOS:**
```bash
# Install PostgreSQL (if not installed)
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb tcs_forecasting
```

**On Windows:**
```bash
# After installing PostgreSQL from the website
# Use psql or pgAdmin to create database
createdb tcs_forecasting
```

**On Linux (Ubuntu/Debian):**
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb tcs_forecasting
```

### 6. Configure Environment Variables

Create a file named `.env` in the project root:

```bash
# Create .env file
touch .env  # On macOS/Linux
# Or create manually on Windows
```

Add these lines to `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=postgresql://localhost/tcs_forecasting
```

**For custom PostgreSQL credentials:**
```
DATABASE_URL=postgresql://username:password@localhost:5432/tcs_forecasting
```

### 7. Run the Application

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### 8. Test the Application

**Open your browser:**
- API Docs: http://localhost:5000/docs
- Health Check: http://localhost:5000/health

**Test with curl:**
```bash
# Health check
curl http://localhost:5000/health

# Generate forecast
curl -X POST http://localhost:5000/forecast \
  -H "Content-Type: application/json" \
  -d '{"company": "TCS", "quarters": 2}'
```

---

## For Interview Demonstration

### Setup Before Interview

1. **Install everything ahead of time**
2. **Test the forecast endpoint** to ensure it works
3. **Prepare database queries** to show persistence
4. **Open README.md** to explain architecture
5. **Have API docs open** at http://localhost:5000/docs

### Demo Flow (10-15 minutes)

**1. Introduction (2 min)**
- Show project structure
- Explain multi-agent architecture

**2. Code Walkthrough (3 min)**
- `main.py` - FastAPI endpoints
- `agents/orchestrator.py` - Master coordinator
- `agents/financial_extractor.py` - GPT-5 extraction with Pydantic
- `agents/transcript_analyst.py` - RAG implementation with FAISS

**3. Live Demo (5 min)**
- Show health check endpoint
- Generate a forecast (explain it takes ~30 sec)
- While it runs, explain the workflow
- Show the JSON response

**4. Database Demo (2 min)**
```sql
-- Show stored forecasts
SELECT request_id, company, created_at 
FROM forecast_logs 
ORDER BY created_at DESC 
LIMIT 5;

-- Show forecast details
SELECT forecast_data->'forward_outlook' as outlook
FROM forecast_logs 
ORDER BY created_at DESC 
LIMIT 1;
```

**5. Q&A (3 min)**
- Answer technical questions
- Discuss architecture decisions
- Mention potential improvements

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution:** 
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Database connection failed"
**Solution:**
```bash
# Check PostgreSQL is running
# macOS:
brew services list

# Linux:
sudo systemctl status postgresql

# Verify database exists
psql -l | grep tcs_forecasting
```

### Issue: "OpenAI API key not configured"
**Solution:**
- Check `.env` file exists in project root
- Verify `OPENAI_API_KEY=sk-...` is set correctly
- Restart the application

### Issue: Port 5000 already in use
**Solution:**
```bash
# Use a different port
uvicorn main:app --host 0.0.0.0 --port 8000

# Or kill the process using port 5000
# macOS/Linux:
lsof -ti:5000 | xargs kill -9

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

## Alternative: Run Without OpenAI API

If you don't have an OpenAI API key for demo purposes:

### What Works:
- Health check endpoint
- API documentation
- Database schema inspection
- Code review and architecture explanation

### Demo Strategy Without API:
1. **Show code quality** - Clean, modular architecture
2. **Explain the flow** - Walk through orchestrator logic
3. **Show RAG implementation** - FAISS vector store setup
4. **Discuss design decisions** - Why GPT-5, why FAISS, etc.
5. **Show sample output** - Use README examples
6. **Database design** - Explain JSONB storage strategy

---

## File Checklist for Interviewer

Make sure these files are ready:
- [ ] `README.md` - Complete documentation
- [ ] `TESTING_GUIDE.md` - This guide
- [ ] All `agents/*.py` files - Core logic
- [ ] `main.py` - API implementation
- [ ] `requirements.txt` - All dependencies
- [ ] `.env.example` - Template for environment variables

---

## Tips for Success

1. **Practice the demo flow** before the interview
2. **Prepare to explain trade-offs** (FAISS vs Pinecone, GPT-5 vs others)
3. **Know your code** - Be ready to dive into any file
4. **Have backup plan** - If API fails, show code and architecture
5. **Highlight key features**:
   - Multi-agent orchestration
   - RAG for grounded analysis
   - Structured extraction with Pydantic
   - Production-ready error handling

Good luck with your interview! 🚀
