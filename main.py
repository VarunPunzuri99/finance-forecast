from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import os

from agents.orchestrator import ForecastOrchestrator
from db import DatabaseLogger, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TCS Financial Forecasting Agent",
    description="Multi-agent system for generating financial forecasts using LangChain and OpenAI",
    version="1.0.0"
)

db_logger = DatabaseLogger()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info("Application started successfully")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "TCS Financial Forecasting Agent",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    openai_key_configured = bool(os.getenv("OPENAI_API_KEY"))
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "openai_configured": openai_key_configured,
        "database": "connected"
    }

class ForecastRequest(BaseModel):
    company: str = "TCS"
    quarters: int = 2

class ForecastResponse(BaseModel):
    request_id: str
    timestamp: str
    financial_trends: Dict[str, Any]
    qualitative_summary: Dict[str, Any]
    risks_opportunities: list
    forward_outlook: str
    market_data: Optional[Dict[str, Any]] = None

@app.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest):
    """
    Main endpoint to generate financial forecast for TCS.
    
    This endpoint:
    1. Scrapes latest quarterly reports from screener.in
    2. Extracts financial metrics using AI
    3. Analyzes earnings transcripts for qualitative insights
    4. Generates comprehensive forecast with risks and opportunities
    5. Logs everything to database
    """
    request_id = f"req_{int(datetime.utcnow().timestamp())}"
    
    try:
        logger.info(f"Starting forecast generation - Request ID: {request_id}")
        
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        orchestrator = ForecastOrchestrator()
        
        forecast_result = await orchestrator.generate_forecast(
            company=request.company,
            num_quarters=request.quarters
        )
        
        response_data = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            **forecast_result
        }
        
        db_logger.log_forecast(request_id, request.company, response_data)
        
        logger.info(f"Forecast generated successfully - Request ID: {request_id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        db_logger.log_error(request_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_forecast_history(limit: int = 10):
    """Retrieve recent forecast history from database"""
    try:
        history = db_logger.get_recent_forecasts(limit)
        return {"forecasts": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
