import logging
from typing import Dict, Any
from agents.document_scraper import DocumentScraper
from agents.financial_extractor import FinancialDataExtractorTool
from agents.transcript_analyst import QualitativeAnalysisTool

logger = logging.getLogger(__name__)

class ForecastOrchestrator:
    """
    Master orchestrator that coordinates all agents to generate comprehensive forecast.
    
    Workflow:
    1. Scrape documents from screener.in
    2. Extract financial metrics using FinancialDataExtractorTool
    3. Analyze transcripts using QualitativeAnalysisTool with RAG
    4. Synthesize findings into structured forecast
    """
    
    def __init__(self):
        self.scraper = DocumentScraper()
        self.financial_extractor = FinancialDataExtractorTool()
        self.transcript_analyst = QualitativeAnalysisTool()
    
    async def generate_forecast(self, company: str = "TCS", num_quarters: int = 2) -> Dict[str, Any]:
        """
        Generate comprehensive financial forecast
        
        Args:
            company: Company ticker/name (default: TCS)
            num_quarters: Number of quarters to analyze
            
        Returns:
            Structured forecast dictionary
        """
        try:
            logger.info(f"Starting forecast generation for {company} - {num_quarters} quarters")
            
            logger.info("Step 1: Scraping documents...")
            documents = self.scraper.get_tcs_documents(num_quarters)
            
            reports = documents.get('reports', [])
            transcripts_meta = documents.get('transcripts', [])
            
            logger.info(f"Found {len(reports)} reports and {len(transcripts_meta)} transcripts")
            
            logger.info("Step 2: Downloading and extracting document content...")
            report_texts = []
            for report in reports:
                text = self.scraper.download_and_extract_text(report)
                if text:
                    report_texts.append({
                        'text': text,
                        'title': report['title']
                    })
            
            transcript_texts = []
            for transcript in transcripts_meta:
                text = self.scraper.download_and_extract_text(transcript)
                if text:
                    transcript_texts.append({
                        'text': text,
                        'title': transcript['title']
                    })
            
            logger.info("Step 3: Extracting financial metrics...")
            financial_metrics = self.financial_extractor.extract_multiple_quarters(report_texts)
            financial_trends = self.financial_extractor.analyze_trends(financial_metrics)
            
            logger.info("Step 4: Performing qualitative analysis on transcripts...")
            qualitative_analysis = self.transcript_analyst.analyze_transcripts(transcript_texts)
            
            logger.info("Step 5: Synthesizing forecast...")
            forecast = self._synthesize_forecast(
                financial_metrics,
                financial_trends,
                qualitative_analysis
            )
            
            logger.info("Forecast generation complete")
            return forecast
            
        except Exception as e:
            logger.error(f"Error in forecast generation: {str(e)}")
            raise
    
    def _synthesize_forecast(
        self,
        financial_metrics: list,
        financial_trends: dict,
        qualitative_analysis: dict
    ) -> Dict[str, Any]:
        """
        Synthesize all findings into final forecast structure
        """
        
        risks = qualitative_analysis.get('risks_opportunities', {}).get('risks', [])
        opportunities = qualitative_analysis.get('risks_opportunities', {}).get('opportunities', [])
        
        risks_opportunities = []
        for risk in risks:
            risks_opportunities.append({
                'type': 'risk',
                'description': risk
            })
        for opp in opportunities:
            risks_opportunities.append({
                'type': 'opportunity',
                'description': opp
            })
        
        outlook_summary = qualitative_analysis.get('management_outlook', {}).get('outlook_summary', 'No outlook data available')
        sentiment = qualitative_analysis.get('sentiment', {}).get('sentiment_analysis', 'No sentiment data')
        themes = qualitative_analysis.get('recurring_themes', [])
        
        forward_outlook = f"""
MANAGEMENT OUTLOOK:
{outlook_summary}

SENTIMENT ANALYSIS:
{sentiment}

RECURRING BUSINESS THEMES:
{chr(10).join(['- ' + theme for theme in themes])}

FINANCIAL TRAJECTORY:
{financial_trends.get('trend_analysis', 'Insufficient data for trend analysis')}
        """.strip()
        
        return {
            "financial_trends": {
                "quarterly_metrics": financial_metrics,
                "trend_analysis": financial_trends.get('trend_analysis', ''),
                "quarters_analyzed": len(financial_metrics)
            },
            "qualitative_summary": {
                "management_outlook": qualitative_analysis.get('management_outlook', {}),
                "recurring_themes": themes,
                "sentiment": sentiment,
                "transcripts_analyzed": qualitative_analysis.get('transcripts_analyzed', 0)
            },
            "risks_opportunities": risks_opportunities,
            "forward_outlook": forward_outlook,
            "market_data": None
        }
