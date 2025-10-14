# TCS Financial Forecasting Agent

A multi-agent FastAPI backend that generates rigorous, qualitative business outlook forecasts for Tata Consultancy Services (TCS) using quarterly financial reports and earnings call transcripts. Built with LangChain, OpenAI GPT-5, and PostgreSQL.

## 🏗️ Architecture Overview

This system implements a **multi-agent orchestration architecture** using LangChain to analyze financial documents and generate comprehensive forecasts:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application Layer                     │
│                     (main.py - /forecast endpoint)                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Forecast Orchestrator                          │
│              (agents/orchestrator.py)                            │
│  Coordinates all agents and synthesizes final forecast           │
└───────────┬──────────────────────────────────────┬──────────────┘
            │                                       │
            ↓                                       ↓
┌──────────────────────────┐          ┌────────────────────────────┐
│  Document Scraper Agent  │          │  Financial Extractor Tool  │
│  (document_scraper.py)   │          │  (financial_extractor.py)  │
│                          │          │                            │
│ - Scrapes screener.in    │          │ - Extracts metrics from    │
│ - Downloads PDFs/HTML    │          │   quarterly reports        │
│ - Extracts text content  │          │ - Uses GPT-5 function      │
│                          │          │   calling for structured   │
│                          │          │   data extraction          │
└──────────────────────────┘          │ - Analyzes trends          │
                                      └────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────────────────┐
│            Qualitative Analysis Tool (RAG-Based)                 │
│                  (transcript_analyst.py)                         │
│                                                                   │
│  - Creates FAISS vector store from transcripts                   │
│  - Semantic search for management insights                       │
│  - Extracts outlook, themes, risks, opportunities                │
│  - Sentiment analysis                                            │
└─────────────────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                           │
│                         (db.py)                                  │
│                                                                   │
│  - Logs all forecasts (forecast_logs table)                      │
│  - Logs errors (error_logs table)                                │
│  - Audit trail and historical analysis                           │
└─────────────────────────────────────────────────────────────────┘
```

## 🧠 Agent Tools & Prompts

### 1. FinancialDataExtractorTool

**Purpose**: Extract precise financial metrics from quarterly reports using LangChain structured output.

**System Prompt**:
```
You are a financial analyst expert specializing in extracting precise financial metrics from quarterly reports.

CRITICAL INSTRUCTIONS:
1. Extract ONLY explicit values stated in the document
2. Never hallucinate or estimate numbers
3. Always cite values exactly as they appear in tables or text
4. If a value is not found, mark it as "N/A"
5. Include currency symbols and units exactly as stated
6. For growth percentages, extract from year-over-year or quarter-over-quarter comparisons
7. Extract 3-5 key financial highlights that are explicitly mentioned

Your analysis must be grounded entirely in the source document.
```

**Extraction Schema**:
- Quarter (e.g., "Q1 FY2024")
- Total Revenue with units
- Net Profit with units
- Operating Margin percentage
- Revenue Growth (YoY/QoQ)
- Profit Growth
- Key Highlights (3-5 points)

**Technology**: GPT-5 with structured output (Pydantic models) for guaranteed JSON schema compliance.

### 2. QualitativeAnalysisTool (RAG-Based)

**Purpose**: Perform semantic analysis of earnings call transcripts to extract management outlook, themes, and sentiment.

**RAG Implementation**:
- **Text Splitting**: RecursiveCharacterTextSplitter (1000 char chunks, 200 overlap)
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Store**: FAISS (in-memory, fast similarity search)
- **Retrieval**: Top-k similarity search (k=4-5)

**Analysis Queries**:

1. **Management Outlook**:
   - Query: "What is management's outlook for future quarters? Growth expectations?"
   - Extracts forward-looking statements and guidance

2. **Business Themes**:
   - Query: "Recurring business themes, strategic priorities, and key initiatives?"
   - Identifies 5-7 core themes from transcripts

3. **Risks & Opportunities**:
   - Risk Query: "What risks, challenges, or concerns does management mention?"
   - Opportunity Query: "What opportunities, growth drivers, or positive factors?"

4. **Sentiment Analysis**:
   - Query: "Overall tone and sentiment of management's statements?"
   - Returns: sentiment (positive/neutral/cautious/negative), confidence level

**Grounding Strategy**: All analyses cite specific excerpts from transcripts with source attribution.

### 3. DocumentScraper

**Purpose**: Automatically download quarterly reports and transcripts from screener.in.

**Scraping Logic**:
- Targets: `https://www.screener.in/company/TCS/consolidated/#documents`
- Extracts links matching keywords: "quarterly", "Q1-Q4", "results", "transcript", "concall"
- Downloads latest N quarters (default: 2)
- Handles both PDF (via pdfplumber) and HTML (via BeautifulSoup) documents

**Text Extraction**:
- **PDF**: pdfplumber for precise table and text extraction
- **HTML**: BeautifulSoup with script/style removal for clean text

## 📊 Output Schema

The `/forecast` endpoint returns a structured JSON forecast:

```json
{
  "request_id": "req_1234567890",
  "timestamp": "2024-01-15T10:30:00Z",
  "financial_trends": {
    "quarterly_metrics": [
      {
        "quarter": "Q3 FY2024",
        "total_revenue": "₹59,162 crores",
        "net_profit": "₹11,342 crores",
        "operating_margin": "25.3%",
        "revenue_growth": "4.1% YoY",
        "profit_growth": "7.8% YoY",
        "key_highlights": [...]
      }
    ],
    "trend_analysis": "Revenue shows consistent growth trajectory...",
    "quarters_analyzed": 2
  },
  "qualitative_summary": {
    "management_outlook": {
      "outlook_summary": "Management expects strong demand in BFSI...",
      "sources": ["Q3 FY2024 Earnings Call Transcript"]
    },
    "recurring_themes": [
      "Focus on AI and GenAI capabilities",
      "Cloud transformation deals pipeline strong",
      ...
    ],
    "sentiment": "Positive with high confidence, citing..."
  },
  "risks_opportunities": [
    {
      "type": "risk",
      "description": "Currency headwinds in key markets"
    },
    {
      "type": "opportunity",
      "description": "AI/ML project acceleration"
    }
  ],
  "forward_outlook": "Comprehensive synthesis of all findings...",
  "market_data": null
}
```

## 🚀 Setup Instructions

### Prerequisites
- **Python**: 3.10+ (3.11 recommended)
- **OpenAI API Key**: Required for GPT-5 access
- **PostgreSQL Database**: Provided by Replit environment

### Step 1: Clone and Install

```bash
# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

The following environment variables are required:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# Database (auto-configured in Replit)
DATABASE_URL=your_postgres_connection_string
```

**Note**: In Replit, the database variables are automatically configured. You only need to provide your OpenAI API key.

### Step 3: Initialize Database

The database schema is automatically initialized on first run. Tables created:

1. **forecast_logs**: Stores all generated forecasts
   - request_id (unique)
   - company (VARCHAR)
   - forecast_data (JSONB)
   - created_at (timestamp)

2. **error_logs**: Stores error information
   - request_id
   - error_message
   - created_at

### Step 4: Run the Application

```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Production server
uvicorn main:app --host 0.0.0.0 --port 5000
```

The API will be available at `http://localhost:5000`

## 📡 API Endpoints

### POST /forecast

Generate a comprehensive financial forecast for TCS.

**Request Body**:
```json
{
  "company": "TCS",
  "quarters": 2
}
```

**Response**: See Output Schema above

**Example**:
```bash
curl -X POST http://localhost:5000/forecast \
  -H "Content-Type: application/json" \
  -d '{"company": "TCS", "quarters": 2}'
```

### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "openai_configured": true,
  "database": "connected"
}
```

### GET /history?limit=10

Retrieve recent forecast history from database.

**Response**:
```json
{
  "forecasts": [
    {
      "request_id": "req_123",
      "company": "TCS",
      "forecast_data": {...},
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

## 🔧 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | High-performance async API |
| **AI Orchestration** | LangChain | Agent coordination, RAG, chains |
| **LLM Provider** | OpenAI GPT-5 | Text analysis, extraction, synthesis |
| **Embeddings** | OpenAI Ada-002 | Semantic search in transcripts |
| **Vector Store** | FAISS | Fast similarity search (in-memory) |
| **Database** | PostgreSQL | Persistent logging and audit trail |
| **Web Scraping** | BeautifulSoup4 | HTML parsing from screener.in |
| **PDF Processing** | pdfplumber | Financial report text extraction |
| **Validation** | Pydantic | Data schema validation |

## 🛡️ Guardrails & Error Handling

### Hallucination Prevention

1. **Explicit Grounding Prompts**: All system prompts emphasize "extract only explicit values", "never hallucinate"
2. **Source Citation**: Every extraction includes source document reference
3. **Structured Output**: Pydantic models ensure schema compliance
4. **N/A Fallback**: Missing values marked as "N/A" rather than estimated

### Error Handling

- **Document Download Failures**: Gracefully logged, partial data returned
- **Parse Errors**: Caught and logged to database
- **API Rate Limits**: Exponential backoff (can be added)
- **Database Errors**: Transaction rollback, error table logging

### Validation Strategy

- Input validation via Pydantic models
- Output validation against expected schema
- Database transaction integrity
- Comprehensive logging for debugging

## 📝 Development Notes

### Adding New Companies

Currently hardcoded for TCS. To support other companies:

1. Update `DocumentScraper.get_tcs_documents()` to accept company parameter
2. Modify URL construction: `f"{self.base_url}/company/{company}/consolidated/#documents"`
3. Update extraction logic for different document formats

### Extending Analysis

To add more analysis types:

1. Create new tool in `agents/` directory
2. Add tool to orchestrator workflow
3. Update output schema in `main.py`
4. Extend database schema if needed

### Performance Optimization

- **Caching**: Add Redis for document caching
- **Async Processing**: Already async-ready with FastAPI
- **Vector Store**: Move to persistent store (Pinecone/Weaviate) for production
- **Batch Processing**: Process multiple companies in parallel

## 🐛 Troubleshooting

### "OpenAI API key not configured"
- Ensure `OPENAI_API_KEY` environment variable is set
- Check `.env` file or Replit Secrets

### "Database connection failed"
- Verify `DATABASE_URL` is set
- Check PostgreSQL service is running
- Review `db.py` connection logic

### "No documents found"
- Verify screener.in URL is accessible
- Check network connectivity
- Review scraper logs for parse errors

### "Empty or invalid forecast"
- Check input documents have sufficient content
- Review LangChain logs for extraction errors
- Verify GPT-5 API is responding

## 📚 References

- **LangChain Documentation**: https://python.langchain.com/
- **OpenAI API**: https://platform.openai.com/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **Screener.in**: https://www.screener.in/company/TCS/

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for all secrets
- Database credentials managed by Replit
- API rate limiting recommended for production

## 📄 License

This project is for educational and demonstration purposes.

---

**Built with ❤️ using LangChain, OpenAI GPT-5, and FastAPI**
