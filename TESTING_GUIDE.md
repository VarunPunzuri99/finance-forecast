# Testing Guide for TCS Financial Forecasting Agent

## Quick Start Testing

### 1. Testing WITHOUT OpenAI API Key

Without an API key, you can still test these endpoints:

#### Health Check (Works without API key)
```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "openai_configured": false,
  "database": "connected"
}
```

#### Root Endpoint (Works without API key)
```bash
curl http://localhost:5000/
```

**Expected Response:**
```json
{
  "status": "online",
  "service": "TCS Financial Forecasting Agent",
  "version": "1.0.0"
}
```

#### API Documentation (Works without API key)
Open in browser: `http://localhost:5000/docs`

This shows interactive API documentation where you can see all endpoints and test them.

---

### 2. Testing WITH OpenAI API Key

#### Step A: Add OpenAI API Key in Replit

1. Click on **Tools** (left sidebar in Replit)
2. Click on **Secrets**
3. Add a new secret:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (get from https://platform.openai.com/api-keys)
4. Click **Add Secret**

#### Step B: Restart the Application

After adding the API key, the workflow will automatically restart. Wait 10-15 seconds.

#### Step C: Test the Forecast Endpoint

**Using curl:**
```bash
curl -X POST http://localhost:5000/forecast \
  -H "Content-Type: application/json" \
  -d '{"company": "TCS", "quarters": 2}'
```

**Using the API Documentation:**
1. Go to `http://localhost:5000/docs`
2. Click on `POST /forecast`
3. Click **Try it out**
4. Edit the request body if needed
5. Click **Execute**

**Expected Response:**
```json
{
  "request_id": "req_1234567890",
  "timestamp": "2024-01-15T10:30:00Z",
  "financial_trends": {
    "quarterly_metrics": [...],
    "trend_analysis": "...",
    "quarters_analyzed": 2
  },
  "qualitative_summary": {
    "management_outlook": {...},
    "recurring_themes": [...],
    "sentiment": "..."
  },
  "risks_opportunities": [...],
  "forward_outlook": "..."
}
```

---

## Database Testing

### Method 1: Using Execute SQL Tool (In Replit)

1. Click on **Tools** in left sidebar
2. Click on **Database**
3. Run these queries:

**Check all forecasts:**
```sql
SELECT * FROM forecast_logs ORDER BY created_at DESC LIMIT 5;
```

**Check errors:**
```sql
SELECT * FROM error_logs ORDER BY created_at DESC LIMIT 5;
```

**Count total forecasts:**
```sql
SELECT COUNT(*) as total_forecasts FROM forecast_logs;
```

**View latest forecast details:**
```sql
SELECT 
  request_id, 
  company, 
  forecast_data->>'forward_outlook' as outlook,
  created_at 
FROM forecast_logs 
ORDER BY created_at DESC 
LIMIT 1;
```

### Method 2: Using the API

**View forecast history:**
```bash
curl http://localhost:5000/history?limit=10
```

This returns the last 10 forecasts from the database.

---

## Running Locally (Outside Replit)

### Prerequisites
- Python 3.10 or higher
- PostgreSQL database
- OpenAI API key

### Steps:

#### 1. Clone/Download the Project
```bash
# If using git
git clone <your-repo-url>
cd <project-folder>

# Or download ZIP and extract
```

#### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate on Linux/Mac:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables

Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/tcs_forecasting
```

**For local PostgreSQL:**
```bash
# Install PostgreSQL if not installed
# Create database
createdb tcs_forecasting

# Update .env with your local credentials
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/tcs_forecasting
```

#### 5. Run the Application
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

#### 6. Access the Application
- API: http://localhost:5000
- Interactive Docs: http://localhost:5000/docs
- Health Check: http://localhost:5000/health

---

## For Your Interviewer

### Demo Script

**1. Show the Architecture**
- Open `README.md` and explain the multi-agent system
- Show the project structure in `agents/` folder

**2. Show the Running Application**
- Navigate to `http://localhost:5000/docs`
- Show interactive API documentation
- Explain each endpoint

**3. Test the Health Check**
```bash
curl http://localhost:5000/health
```

**4. Generate a Forecast (if API key available)**
- Use the `/forecast` endpoint
- Explain how it:
  1. Scrapes screener.in
  2. Extracts financial metrics
  3. Analyzes transcripts with RAG
  4. Generates comprehensive forecast

**5. Show Database Persistence**
```bash
curl http://localhost:5000/history?limit=5
```

**6. Explain the Technology**
- FastAPI for async API
- LangChain for agent orchestration
- OpenAI GPT-5 for analysis
- FAISS for RAG vector search
- PostgreSQL for persistence

### What to Highlight

✅ **Multi-agent architecture** - Specialized agents for different tasks
✅ **RAG implementation** - Semantic search over earnings transcripts
✅ **Structured extraction** - GPT-5 function calling with Pydantic schemas
✅ **Grounding safeguards** - Prevents hallucinations
✅ **Database logging** - Complete audit trail
✅ **Production-ready** - Error handling, validation, async operations

---

## Troubleshooting

### "OpenAI API key not configured"
- Add the API key to Replit Secrets or `.env` file
- Restart the application

### "Database connection failed"
- In Replit: Database is auto-configured, just restart workflow
- Locally: Ensure PostgreSQL is running and DATABASE_URL is correct

### "No documents found"
- Check internet connection
- Verify screener.in is accessible
- May need to update scraper if website structure changed

### Forecast takes long time
- This is normal! The system:
  - Downloads 2+ PDF documents
  - Extracts text from PDFs
  - Makes multiple OpenAI API calls
  - Performs RAG analysis
- Expected time: 30-60 seconds

---

## Quick Demo Without API Key

If you don't have an OpenAI API key for the demo:

1. **Show the architecture** in README.md
2. **Show the code structure** - explain each agent
3. **Test health endpoint** - shows it's running
4. **Show API docs** at `/docs` - demonstrates the interface
5. **Show database schema** - explain logging strategy
6. **Walk through the code**:
   - `agents/orchestrator.py` - master workflow
   - `agents/financial_extractor.py` - GPT-5 extraction
   - `agents/transcript_analyst.py` - RAG implementation

This demonstrates your understanding of the architecture even without live API calls.
