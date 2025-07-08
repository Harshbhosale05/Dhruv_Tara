#!/usr/bin/env python3
"""
🤖 Minimal MOSDAC Chatbot for Render Deployment
A simplified version that works reliably in cloud environments
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinimalMOSDACChatbot:
    def __init__(self, gemini_api_key: str = None):
        """
        Initialize minimal chatbot with essential features only
        """
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        
        # Initialize Gemini AI
        self.setup_gemini()
        
        # Initialize Neo4j (optional - with error handling)
        self.setup_neo4j()
        
        # Basic knowledge base
        self.knowledge_base = {
            "mosdac": "MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre) is ISRO's facility for satellite data archival and distribution.",
            "isro": "Indian Space Research Organisation (ISRO) is India's national space agency.",
            "satellite": "ISRO operates various satellites for Earth observation, communication, and navigation.",
            "data": "MOSDAC provides access to meteorological and oceanographic satellite data for research and applications."
        }
        
        logger.info("✅ Minimal MOSDAC Chatbot initialized successfully")

    def setup_gemini(self):
        """Setup Google Gemini AI"""
        try:
            if self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Gemini AI configured successfully")
            else:
                logger.warning("⚠️ No Gemini API key provided")
                self.gemini_model = None
        except Exception as e:
            logger.error(f"❌ Failed to setup Gemini: {e}")
            self.gemini_model = None

    def setup_neo4j(self):
        """Setup Neo4j connection with error handling"""
        try:
            neo4j_uri = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
            
            self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            logger.info("✅ Neo4j connected successfully")
        except Exception as e:
            logger.warning(f"⚠️ Neo4j connection failed: {e}")
            self.driver = None

    def simple_keyword_search(self, query: str) -> str:
        """Simple keyword-based search in knowledge base"""
        query_lower = query.lower()
        
        for keyword, info in self.knowledge_base.items():
            if keyword in query_lower:
                return f"Based on our knowledge base: {info}"
        
        return "I found some general information that might help you."

    def get_neo4j_data(self, query: str) -> str:
        """Get relevant data from Neo4j if available"""
        if not self.driver:
            return "Database connection not available."
        
        try:
            with self.driver.session() as session:
                # Simple query to get some data
                result = session.run(
                    "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($query) OR toLower(n.description) CONTAINS toLower($query) RETURN n LIMIT 3",
                    query=query
                )
                
                records = [record["n"] for record in result]
                if records:
                    return f"Found {len(records)} relevant items in the database."
                else:
                    return "No specific database records found for your query."
                    
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            return "Database query encountered an issue."

    def chat(self, query: str, user_id: str = "default_user") -> str:
        """
        Chat method that matches the API interface
        """
        try:
            response_data = self.generate_response(query)
            return response_data.get('response', 'Sorry, I encountered an error.')
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "I apologize, but I'm having trouble processing your request right now."

    def generate_response(self, user_message: str) -> Dict[str, Any]:
        """
        Generate response using available methods
        """
        try:
            # Get context from different sources
            keyword_context = self.simple_keyword_search(user_message)
            db_context = self.get_neo4j_data(user_message)
            
            # Prepare context for Gemini
            context = f"""
            You are a helpful assistant for MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre) and ISRO.
            
            User question: {user_message}
            
            Available context:
            - Knowledge base: {keyword_context}
            - Database info: {db_context}
            
            Please provide a helpful response about MOSDAC, ISRO, satellites, or meteorological data.
            If you don't have specific information, provide general guidance about these topics.
            """
            
            # Generate response with Gemini or fallback
            if self.gemini_model:
                try:
                    response = self.gemini_model.generate_content(context)
                    ai_response = response.text
                except Exception as e:
                    logger.error(f"Gemini generation error: {e}")
                    ai_response = self.fallback_response(user_message)
            else:
                ai_response = self.fallback_response(user_message)
            
            return {
                'response': ai_response,
                'sources': ['gemini_ai', 'knowledge_base', 'neo4j'] if self.driver else ['gemini_ai', 'knowledge_base'],
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'response': self.fallback_response(user_message),
                'sources': ['fallback'],
                'status': 'error',
                'error': str(e)
            }

    def fallback_response(self, user_message: str) -> str:
        """Fallback response when AI is not available"""
        
        # Simple keyword-based responses
        query_lower = user_message.lower()
        
        if any(word in query_lower for word in ['mosdac', 'data', 'satellite']):
            return """MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre) is ISRO's facility that provides:
            
            🛰️ Satellite data from various Indian and international satellites
            📊 Meteorological and oceanographic datasets
            🌍 Earth observation data for research and applications
            📈 Data products for weather forecasting and climate studies
            
            You can access data through the MOSDAC portal for research and commercial purposes."""
            
        elif any(word in query_lower for word in ['isro', 'space', 'launch']):
            return """ISRO (Indian Space Research Organisation) is India's national space agency that:
            
            🚀 Develops and launches satellites
            🌌 Conducts space exploration missions
            🛰️ Operates Earth observation satellites
            📡 Provides satellite-based services
            
            ISRO has achieved remarkable milestones including Mars Orbiter Mission and Chandrayaan lunar missions."""
            
        else:
            return """I'm here to help you with information about:
            
            🛰️ MOSDAC satellite data and services
            🚀 ISRO missions and satellites
            🌍 Earth observation and remote sensing
            📊 Meteorological and oceanographic data
            
            Please feel free to ask specific questions about these topics!"""

    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

# For testing
if __name__ == "__main__":
    chatbot = MinimalMOSDACChatbot()
    
    # Test the chatbot
    test_queries = [
        "What is MOSDAC?",
        "Tell me about ISRO satellites",
        "How can I access satellite data?"
    ]
    
    for query in test_queries:
        print(f"\n🤔 Query: {query}")
        response = chatbot.generate_response(query)
        print(f"🤖 Response: {response['response']}")
    
    chatbot.close()
