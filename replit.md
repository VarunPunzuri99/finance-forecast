# TCS Financial Forecasting Agent

## Overview

A multi-agent FastAPI backend that generates comprehensive business outlook forecasts for Tata Consultancy Services (TCS). The system analyzes quarterly financial reports and earnings call transcripts using LangChain orchestration, OpenAI GPT-5, and RAG-based qualitative analysis to produce structured, data-driven forecasts.

The application employs a coordinated multi-agent architecture where specialized agents handle document scraping, financial metric extraction, and qualitative transcript analysis. These agents work together under a master orchestrator to synthesize findings into actionable business forecasts.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Multi-Agent Orchestration Pattern

The system implements a **coordinator-executor pattern** where a master orchestrator (`ForecastOrchestrator`) coordinates three specialized agents:

1. **Document Scraper Agent** - Handles web scraping and document retrieval from screener.in
2. **Financial Extractor Tool** - Performs structured data extraction using GPT-5 function calling
3. **Qualitative Analysis Tool** - Conducts RAG-based semantic analysis of earnings transcripts

**Rationale**: This separation of concerns allows each agent to specialize in a specific domain (web scraping, numerical extraction, or qualitative analysis) while the orchestrator manages workflow and synthesis. This makes the system more maintainable and allows independent scaling or replacement of components.

### API Layer Architecture

**FastAPI Application** serves as the REST interface with these key endpoints:
- `/forecast` - Main endpoint triggering the multi-agent workflow
- `/health` - System health checks and configuration validation
- `/` - Basic status endpoint

**Design Decision**: FastAPI was chosen for its async capabilities, automatic OpenAPI documentation, and native Pydantic integration for request/response validation.

### Data Extraction Strategy

**Financial Metrics Extraction** uses OpenAI's function calling with strict Pydantic schemas (`FinancialMetrics` model) to extract:
- Revenue and profit figures with proper units
- Growth percentages (YoY/QoQ)
- Operating margins
- Key highlights from reports

**Rationale**: Function calling ensures structured, validated output rather than unstructured LLM responses. The schema prevents hallucination by requiring explicit field definitions and validation rules.

### RAG-Based Qualitative Analysis

**Vector Store Implementation** uses FAISS (Facebook AI Similarity Search) with OpenAI embeddings:
- Transcript text is chunked using `RecursiveCharacterTextSplitter` (1000 char chunks, 200 char overlap)
- Chunks are embedded and stored in FAISS index for semantic search
- Management insights, sentiment, and strategic themes are extracted via retrieval-augmented prompts

**Rationale**: RAG allows the system to ground qualitative analysis in actual transcript content rather than relying on LLM world knowledge. FAISS provides fast similarity search without requiring external vector database infrastructure.

**Alternatives Considered**: Chroma or Pinecone vector stores were considered but FAISS was chosen for its simplicity, speed, and ability to run in-process without external dependencies.

### LLM Configuration

**Model Selection**: GPT-5 (released August 7, 2025) is used across all agents for:
- Financial metric extraction with function calling
- Qualitative analysis and synthesis
- Forecast generation

**Design Decision**: A single model version ensures consistent behavior across agents. The 4096 max completion tokens provides sufficient output length for comprehensive analyses.

### Document Processing Pipeline

**Web Scraping** targets screener.in with:
- Custom User-Agent headers for reliability
- BeautifulSoup for HTML parsing
- Support for both PDF and HTML document formats
- pdfplumber for PDF text extraction

**Workflow**:
1. Scrape document metadata from screener.in
2. Download PDFs/HTML for specified quarters
3. Extract text content
4. Pass to specialized analysis tools

**Rationale**: This pipeline separates retrieval from analysis, allowing documents to be cached or processed independently. The dual format support (PDF/HTML) provides flexibility as source formats change.

### Data Persistence Layer

**PostgreSQL Database** with two primary tables:
- `forecast_logs` - Stores complete forecast results as JSONB with request tracking
- `error_logs` - Captures failures for debugging and monitoring

**Schema Design**:
- JSONB column type allows flexible storage of forecast structure without rigid schema constraints
- Indexed by company and timestamp for efficient querying
- Unique request IDs prevent duplicate processing

**Rationale**: PostgreSQL's JSONB type provides the flexibility of document storage with the reliability and querying power of relational databases. This supports both structured queries and schema evolution as forecast formats evolve.

**Pros**: ACID compliance, JSON querying capabilities, mature ecosystem
**Cons**: Requires PostgreSQL infrastructure (addressed via environment variable configuration)

### Error Handling and Logging

**Logging Strategy**:
- Python's built-in logging framework at INFO level
- Structured database logging for forecasts and errors
- Request ID tracking for correlation

**Design Decision**: Multi-level logging (application logs + database logs) provides both real-time debugging and historical analysis capabilities.

## External Dependencies

### AI/ML Services
- **OpenAI API** (GPT-5) - Primary LLM for all text analysis and generation tasks
- **OpenAI Embeddings API** - Text embeddings for RAG vector search
- Configuration via `OPENAI_API_KEY` environment variable

### Database
- **PostgreSQL** - Primary data store for forecast logs and error tracking
- Connection via `DATABASE_URL` environment variable
- Uses psycopg2 driver with RealDictCursor for JSON-friendly results

### Web Scraping
- **screener.in** - Source for TCS quarterly reports and earnings transcripts
- No authentication required, uses user-agent spoofing for reliability

### Python Libraries
- **LangChain** (v0.1.0) - Agent orchestration, chains, and tool framework
- **langchain-openai** - OpenAI integration for LangChain
- **langchain-community** - Community tools including FAISS vector store
- **FAISS-CPU** - Vector similarity search (Facebook AI)
- **BeautifulSoup4** - HTML parsing and web scraping
- **pdfplumber** - PDF text extraction
- **FastAPI** - Web framework for REST API
- **Pydantic** - Data validation and schema definition
- **psycopg2-binary** - PostgreSQL database driver

### System Requirements
- Python 3.10+
- Sufficient memory for FAISS in-memory vector store (scales with transcript volume)
- Network access to OpenAI API and screener.in