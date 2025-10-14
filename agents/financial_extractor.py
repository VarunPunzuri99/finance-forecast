import os
import json
import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class FinancialMetrics(BaseModel):
    """Schema for financial metrics extraction"""
    quarter: str = Field(description="Quarter and year (e.g., Q1 FY2024)")
    total_revenue: str = Field(description="Total revenue with units (e.g., '₹59,162 crores')")
    net_profit: str = Field(description="Net profit with units")
    operating_margin: str = Field(description="Operating margin percentage")
    revenue_growth: str = Field(description="Revenue growth percentage YoY or QoQ", default="N/A")
    profit_growth: str = Field(description="Profit growth percentage", default="N/A")
    key_highlights: List[str] = Field(description="3-5 key financial highlights from the report", default_factory=list)

class FinancialDataExtractorTool:
    """
    LangChain-based tool for extracting financial metrics from quarterly reports.
    Uses GPT-5 with function calling for structured data extraction.
    """
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        self.llm = ChatOpenAI(
            model="gpt-5",
            api_key=api_key,
            max_completion_tokens=4096
        )
        
        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial analyst expert specializing in extracting precise financial metrics from quarterly reports.

CRITICAL INSTRUCTIONS:
1. Extract ONLY explicit values stated in the document
2. Never hallucinate or estimate numbers
3. Always cite values exactly as they appear in tables or text
4. If a value is not found, mark it as "N/A"
5. Include currency symbols and units exactly as stated
6. For growth percentages, extract from year-over-year or quarter-over-quarter comparisons
7. Extract 3-5 key financial highlights that are explicitly mentioned

Your analysis must be grounded entirely in the source document."""),
            ("user", "Extract financial metrics from this quarterly report:\n\n{document_text}")
        ])
    
    def extract_metrics(self, document_text: str, document_title: str = "") -> Dict[str, Any]:
        """
        Extract financial metrics using LangChain function calling
        
        Args:
            document_text: Text content of the quarterly report
            document_title: Title/name of the document for context
            
        Returns:
            Dictionary with extracted financial metrics
        """
        try:
            logger.info(f"Extracting metrics from: {document_title}")
            
            if not document_text or len(document_text.strip()) < 100:
                raise ValueError("Document text is too short or empty")
            
            structured_llm = self.llm.with_structured_output(FinancialMetrics)
            
            chain = self.extraction_prompt | structured_llm
            
            result = chain.invoke({"document_text": document_text[:15000]})
            
            metrics_dict = result.dict()
            metrics_dict['source_document'] = document_title
            
            logger.info(f"Successfully extracted metrics for {metrics_dict.get('quarter', 'Unknown')}")
            
            return metrics_dict
            
        except Exception as e:
            logger.error(f"Error extracting financial metrics: {str(e)}")
            return {
                "error": str(e),
                "quarter": "Unknown",
                "source_document": document_title
            }
    
    def extract_multiple_quarters(self, documents: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract metrics from multiple quarterly reports
        
        Args:
            documents: List of document dictionaries with 'text' and 'title' keys
            
        Returns:
            List of extracted metrics for each quarter
        """
        all_metrics = []
        
        for doc in documents:
            metrics = self.extract_metrics(
                document_text=doc.get('text', ''),
                document_title=doc.get('title', 'Untitled')
            )
            all_metrics.append(metrics)
        
        return all_metrics
    
    def analyze_trends(self, metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trends across multiple quarters
        
        Args:
            metrics_list: List of financial metrics from different quarters
            
        Returns:
            Trend analysis dictionary
        """
        try:
            if not metrics_list or len(metrics_list) < 2:
                return {"trend_analysis": "Insufficient data for trend analysis"}
            
            valid_metrics = [m for m in metrics_list if 'error' not in m]
            
            if len(valid_metrics) < 2:
                return {"trend_analysis": "Insufficient valid quarters for comparison"}
            
            analysis_prompt = f"""Analyze the following financial metrics across quarters and identify key trends:

Quarters Data:
{json.dumps(valid_metrics, indent=2)}

Provide a concise trend analysis covering:
1. Revenue trajectory (growing/declining/stable)
2. Profitability trends
3. Margin performance
4. Notable changes or inflection points

Focus only on what the data explicitly shows."""

            response = self.llm.invoke(analysis_prompt)
            
            return {
                "trend_analysis": response.content,
                "quarters_analyzed": len(valid_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            return {"trend_analysis": f"Error: {str(e)}"}
