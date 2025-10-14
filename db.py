import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get PostgreSQL database connection"""
    database_url = "postgresql://postgres:Punzuri!1234@db.zcekdhjiltyxagbziwge.supabase.co:5432/postgres"
    if not database_url:
        raise Exception("DATABASE_URL environment variable not set")
    
    return psycopg2.connect(database_url)

def init_db():
    """Initialize database schema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecast_logs (
                id SERIAL PRIMARY KEY,
                request_id VARCHAR(255) UNIQUE NOT NULL,
                company VARCHAR(100) NOT NULL,
                forecast_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id SERIAL PRIMARY KEY,
                request_id VARCHAR(255),
                error_message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_forecast_company 
            ON forecast_logs(company, created_at DESC)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

class DatabaseLogger:
    """Database logging utility for forecasts and errors"""
    
    def log_forecast(self, request_id: str, company: str, forecast_data: dict):
        """Log forecast to database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO forecast_logs (request_id, company, forecast_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (request_id) DO UPDATE
                SET forecast_data = EXCLUDED.forecast_data
            """, (request_id, company, json.dumps(forecast_data)))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Logged forecast for request {request_id}")
            
        except Exception as e:
            logger.error(f"Error logging forecast: {str(e)}")
            raise
    
    def log_error(self, request_id: str, error_message: str):
        """Log error to database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO error_logs (request_id, error_message)
                VALUES (%s, %s)
            """, (request_id, error_message))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging error: {str(e)}")
    
    def get_recent_forecasts(self, limit: int = 10):
        """Retrieve recent forecasts from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT request_id, company, forecast_data, created_at
                FROM forecast_logs
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error retrieving forecasts: {str(e)}")
            raise
