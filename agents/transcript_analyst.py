import os
import logging
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document

logger = logging.getLogger(__name__)

class QualitativeAnalysisTool:
    """
    LangChain RAG-based tool for analyzing earnings call transcripts.
    Performs semantic search and qualitative analysis to extract:
    - Management outlook and sentiment
    - Recurring business themes
    - Strategic priorities and initiatives
    - Risks and opportunities
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
        
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def create_vector_store(self, transcripts: List[Dict]) -> FAISS:
        """
        Create FAISS vector store from transcript texts
        
        Args:
            transcripts: List of transcript dictionaries with 'text' and 'title'
            
        Returns:
            FAISS vector store for semantic search
        """
        try:
            documents = []
            
            for transcript in transcripts:
                text = transcript.get('text', '')
                title = transcript.get('title', 'Untitled')
                
                if text and len(text.strip()) > 100:
                    chunks = self.text_splitter.split_text(text)
                    
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                'source': title,
                                'chunk': i
                            }
                        )
                        documents.append(doc)
            
            if not documents:
                raise ValueError("No valid transcript content to create vector store")
            
            logger.info(f"Creating vector store with {len(documents)} chunks")
            vector_store = FAISS.from_documents(documents, self.embeddings)
            
            return vector_store
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    def analyze_transcripts(self, transcripts: List[Dict]) -> Dict[str, Any]:
        """
        Perform comprehensive qualitative analysis on transcripts using RAG
        
        Args:
            transcripts: List of transcript dictionaries
            
        Returns:
            Dictionary with qualitative insights
        """
        try:
            logger.info(f"Analyzing {len(transcripts)} transcripts")
            
            if not transcripts:
                return {"error": "No transcripts provided"}
            
            vector_store = self.create_vector_store(transcripts)
            
            management_outlook = self._extract_management_outlook(vector_store)
            business_themes = self._extract_business_themes(vector_store)
            risks_opportunities = self._extract_risks_opportunities(vector_store)
            sentiment_analysis = self._analyze_sentiment(vector_store)
            
            return {
                "management_outlook": management_outlook,
                "recurring_themes": business_themes,
                "risks_opportunities": risks_opportunities,
                "sentiment": sentiment_analysis,
                "transcripts_analyzed": len(transcripts)
            }
            
        except Exception as e:
            logger.error(f"Error in qualitative analysis: {str(e)}")
            return {
                "error": str(e),
                "transcripts_analyzed": 0
            }
    
    def _extract_management_outlook(self, vector_store: FAISS) -> Dict[str, Any]:
        """Extract management's forward-looking statements and outlook"""
        try:
            query = "What is management's outlook for future quarters? What are their growth expectations and business forecasts?"
            
            relevant_docs = vector_store.similarity_search(query, k=5)
            
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert financial analyst analyzing earnings call transcripts.
                
Extract management's forward-looking outlook and expectations. Focus on:
1. Revenue and growth projections
2. Strategic initiatives for upcoming quarters
3. Market expectations and guidance
4. Key focus areas for the business

IMPORTANT: Only cite information explicitly stated in the context. Include direct quotes where relevant."""),
                ("user", "Context from transcripts:\n{context}\n\nProvide a structured summary of management's outlook.")
            ])
            
            response = self.llm.invoke(prompt.format(context=context))
            
            return {
                "outlook_summary": response.content,
                "sources": [doc.metadata.get('source', 'Unknown') for doc in relevant_docs[:3]]
            }
            
        except Exception as e:
            return {"outlook_summary": f"Error: {str(e)}"}
    
    def _extract_business_themes(self, vector_store: FAISS) -> List[str]:
        """Identify recurring business themes and strategic priorities"""
        try:
            query = "What are the recurring business themes, strategic priorities, and key initiatives mentioned by management?"
            
            relevant_docs = vector_store.similarity_search(query, k=5)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            prompt = f"""Based on the following transcript excerpts, identify 5-7 recurring business themes and strategic priorities:

{context}

List the themes as concise bullet points, citing specific mentions from the transcripts."""
            
            response = self.llm.invoke(prompt)
            
            themes = [line.strip() for line in response.content.split('\n') if line.strip() and ('•' in line or '-' in line or any(char.isdigit() for char in line[:3]))]
            
            return themes[:7]
            
        except Exception as e:
            return [f"Error extracting themes: {str(e)}"]
    
    def _extract_risks_opportunities(self, vector_store: FAISS) -> Dict[str, List[str]]:
        """Extract risks and opportunities mentioned by management"""
        try:
            risks_query = "What risks, challenges, or concerns does management mention?"
            opportunities_query = "What opportunities, growth drivers, or positive factors does management highlight?"
            
            risks_docs = vector_store.similarity_search(risks_query, k=4)
            opps_docs = vector_store.similarity_search(opportunities_query, k=4)
            
            risks_context = "\n\n".join([doc.page_content for doc in risks_docs])
            opps_context = "\n\n".join([doc.page_content for doc in opps_docs])
            
            risks_prompt = f"List 3-5 key risks or challenges mentioned:\n{risks_context}"
            opps_prompt = f"List 3-5 key opportunities or growth drivers mentioned:\n{opps_context}"
            
            risks_response = self.llm.invoke(risks_prompt)
            opps_response = self.llm.invoke(opps_prompt)
            
            risks = [line.strip() for line in risks_response.content.split('\n') if line.strip() and any(c in line for c in ['•', '-', '1', '2', '3', '4', '5'])]
            opportunities = [line.strip() for line in opps_response.content.split('\n') if line.strip() and any(c in line for c in ['•', '-', '1', '2', '3', '4', '5'])]
            
            return {
                "risks": risks[:5],
                "opportunities": opportunities[:5]
            }
            
        except Exception as e:
            return {
                "risks": [f"Error: {str(e)}"],
                "opportunities": []
            }
    
    def _analyze_sentiment(self, vector_store: FAISS) -> Dict[str, Any]:
        """Analyze overall sentiment and management confidence"""
        try:
            query = "What is the overall tone and sentiment of management's statements?"
            
            relevant_docs = vector_store.similarity_search(query, k=4)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            prompt = f"""Analyze the sentiment and tone of management's statements:

{context}

Provide:
1. Overall sentiment (positive/neutral/cautious/negative)
2. Confidence level (high/moderate/low)
3. Key sentiment indicators with brief quotes

Be objective and cite specific evidence."""
            
            response = self.llm.invoke(prompt)
            
            return {
                "sentiment_analysis": response.content
            }
            
        except Exception as e:
            return {"sentiment_analysis": f"Error: {str(e)}"}
