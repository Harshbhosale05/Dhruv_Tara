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
        
        # Enhanced knowledge base with detailed ISRO satellite information
        self.knowledge_base = {
            "mosdac": "MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre) is ISRO's facility for satellite data archival and distribution.",
            "isro": "Indian Space Research Organisation (ISRO) is India's national space agency.",
            "satellite": "ISRO operates various satellites for Earth observation, communication, and navigation.",
            "data": "MOSDAC provides access to meteorological and oceanographic satellite data for research and applications.",
            "insat": "INSAT (Indian National Satellite) is a series of multipurpose geostationary satellites for telecommunications, broadcasting, meteorology, and search and rescue operations.",
            "insat-3d": "INSAT-3D launched in 2013, provides advanced meteorological observations with a 6-channel imager and 19-channel sounder for weather forecasting and disaster management.",
            "insat-3ds": "INSAT-3DS launched in 2024, is an advanced meteorological satellite with improved imaging capabilities, better temporal resolution, and enhanced data products for weather monitoring.",
            "gsat": "GSAT (Geosynchronous Satellite) series provides communication services across India with various transponder configurations.",
            "cartosat": "CARTOSAT series provides high-resolution Earth observation data for cartographic applications, urban planning, and infrastructure development.",
            "resourcesat": "RESOURCESAT series provides multispectral imagery for natural resource management, agriculture, and environmental monitoring.",
            "oceansat": "OCEANSAT series monitors ocean color, sea surface temperature, and coastal applications.",
            "chandrayaan": "India's lunar exploration missions - Chandrayaan-1 (2008) and Chandrayaan-2 (2019) studied lunar surface and composition.",
            "mangalyaan": "Mars Orbiter Mission (MOM) successfully entered Mars orbit in 2014, making India the first country to succeed in Mars mission on first attempt.",
            "aditya": "Aditya-L1 is India's first solar mission to study the Sun's corona and solar wind.",
            "pslv": "Polar Satellite Launch Vehicle (PSLV) is ISRO's reliable workhorse for launching satellites into polar and Sun-synchronous orbits.",
            "gslv": "Geosynchronous Satellite Launch Vehicle (GSLV) is designed for launching heavier satellites into geostationary orbit."
        }
        
        # Setup sample data if Neo4j is available
        if self.driver:
            self.setup_sample_data()
        
        logger.info("✅ Minimal MOSDAC Chatbot initialized successfully")

    def setup_gemini(self):
        """Setup Google Gemini AI"""
        try:
            logger.info(f"🔑 Gemini API key provided: {bool(self.gemini_api_key)}")
            if self.gemini_api_key:
                logger.info("🚀 Configuring Gemini AI...")
                genai.configure(api_key=self.gemini_api_key)
                
                # Try different model names in order of preference
                models_to_try = [
                    'gemini-1.5-flash',
                    'gemini-1.5-pro',  
                    'gemini-pro',
                    'gemini-1.0-pro'
                ]
                
                self.gemini_model = None
                for model_name in models_to_try:
                    try:
                        logger.info(f"🔧 Trying model: {model_name}")
                        self.gemini_model = genai.GenerativeModel(model_name)
                        # Test the model with a simple query
                        test_response = self.gemini_model.generate_content("Hello")
                        logger.info(f"✅ Gemini AI configured successfully with {model_name}")
                        break
                    except Exception as model_error:
                        logger.warning(f"⚠️ Model {model_name} failed: {model_error}")
                        continue
                
                if not self.gemini_model:
                    logger.error("❌ No working Gemini model found")
                    
            else:
                logger.warning("⚠️ No Gemini API key provided - using fallback responses only")
                self.gemini_model = None
        except Exception as e:
            logger.error(f"❌ Failed to setup Gemini: {e}")
            self.gemini_model = None

    def setup_neo4j(self):
        """Setup Neo4j connection with error handling"""
        # Check if Neo4j is enabled
        neo4j_enabled = os.getenv('NEO4J_ENABLED', 'false').lower() == 'true'
        
        if not neo4j_enabled:
            logger.info("ℹ️ Neo4j disabled - set NEO4J_ENABLED=true to enable")
            self.driver = None
            return
            
        try:
            neo4j_uri = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
            
            if not neo4j_password or neo4j_password == 'password':
                logger.warning("⚠️ Neo4j password not set properly - check NEO4J_PASSWORD environment variable")
            
            logger.info(f"🔌 Attempting Neo4j connection to: {neo4j_uri}")
            logger.info(f"🔑 Using username: {neo4j_user}")
            
            # Create driver with proper configuration for cloud databases
            self.driver = GraphDatabase.driver(
                neo4j_uri, 
                auth=(neo4j_user, neo4j_password),
                encrypted=True,  # Enable encryption for cloud databases
                trust=True       # Trust the server certificate
            )
            
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    logger.info("✅ Neo4j connected successfully")
                else:
                    raise Exception("Connection test failed")
            
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            logger.info("💡 Make sure to set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD environment variables")
            self.driver = None

    def simple_keyword_search(self, query: str) -> str:
        """Enhanced keyword-based search in knowledge base"""
        query_lower = query.lower()
        
        # Check for multiple keywords and return most relevant
        matched_keywords = []
        for keyword, info in self.knowledge_base.items():
            if keyword in query_lower:
                matched_keywords.append((keyword, info))
        
        if matched_keywords:
            # Return information from the most relevant keyword
            return f"Knowledge base match: {matched_keywords[0][1]}"
        
        return "Searching in knowledge base for relevant information."

    def get_neo4j_data(self, query: str) -> str:
        """Get relevant data from Neo4j if available"""
        if not self.driver:
            return "Database connection not available."
        
        try:
            with self.driver.session() as session:
                # First, try to find nodes with specific properties
                result = session.run("""
                    MATCH (n)
                    WHERE toLower(toString(n.name)) CONTAINS toLower($query)
                    OR toLower(toString(n.description)) CONTAINS toLower($query)
                    OR toLower(toString(n.type)) CONTAINS toLower($query)
                    RETURN n.name as name, n.description as description, n.type as type, labels(n) as labels
                    LIMIT 5
                """, query=query)
                
                records = []
                for record in result:
                    records.append({
                        'name': record.get('name', 'Unknown'),
                        'description': record.get('description', 'No description'),
                        'type': record.get('type', 'Unknown'),
                        'labels': record.get('labels', [])
                    })
                
                if records:
                    response = f"Found {len(records)} relevant items in Neo4j database:\n"
                    for i, record in enumerate(records, 1):
                        response += f"{i}. {record['name']} ({record['type']}): {record['description']}\n"
                    return response
                else:
                    return "No specific database records found for your query."
                    
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            return "Database query encountered an issue."

    def setup_sample_data(self):
        """Setup sample MOSDAC/ISRO data in Neo4j"""
        if not self.driver:
            logger.info("ℹ️ Skipping sample data setup - Neo4j not available")
            return
        
        try:
            with self.driver.session() as session:
                # Create sample MOSDAC and ISRO data
                session.run("""
                    MERGE (mosdac:Organization {name: 'MOSDAC', type: 'Data Center'})
                    SET mosdac.description = 'Meteorological & Oceanographic Satellite Data Archival Centre'
                    
                    MERGE (isro:Organization {name: 'ISRO', type: 'Space Agency'})
                    SET isro.description = 'Indian Space Research Organisation'
                    
                    MERGE (insat3d:Satellite {name: 'INSAT-3D', type: 'Meteorological Satellite'})
                    SET insat3d.description = 'Advanced meteorological satellite launched in 2013'
                    
                    MERGE (insat3ds:Satellite {name: 'INSAT-3DS', type: 'Meteorological Satellite'})
                    SET insat3ds.description = 'Next-generation meteorological satellite launched in 2024'
                    
                    MERGE (mosdac)-[:MANAGES]->(insat3d)
                    MERGE (mosdac)-[:MANAGES]->(insat3ds)
                    MERGE (isro)-[:OPERATES]->(insat3d)
                    MERGE (isro)-[:OPERATES]->(insat3ds)
                """)
                
                logger.info("✅ Sample data setup completed in Neo4j")
                
        except Exception as e:
            logger.error(f"❌ Failed to setup sample data: {e}")

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
            logger.info(f"🔄 Processing query: {user_message}")
            logger.info(f"📱 Gemini model available: {self.gemini_model is not None}")
            
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
                    logger.info("🤖 Using Gemini AI for response generation")
                    response = self.gemini_model.generate_content(context)
                    ai_response = response.text
                    logger.info("✅ Gemini AI response generated successfully")
                except Exception as e:
                    logger.error(f"❌ Gemini generation error: {e}")
                    ai_response = self.fallback_response(user_message)
            else:
                logger.warning("⚠️ Gemini model not available, using fallback")
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
        """Enhanced fallback response with specific knowledge"""
        
        query_lower = user_message.lower()
        
        # Check for specific satellite comparisons
        if 'insat' in query_lower and ('3d' in query_lower or '3ds' in query_lower):
            if 'difference' in query_lower or 'diff' in query_lower or 'between' in query_lower:
                return """🛰️ **INSAT-3D vs INSAT-3DS Comparison:**

**INSAT-3D (2013):**
• 6-channel imager for visible and infrared imagery
• 19-channel sounder for atmospheric profiling
• Hourly full disk imaging capability
• Data relay for weather buoys and stations
• Search and rescue transponder

**INSAT-3DS (2024):**
• Advanced 6-channel imager with improved resolution
• Enhanced 19-channel sounder with better accuracy
• 15-minute rapid scan capability for severe weather
• Advanced data products for nowcasting
• Better temporal resolution for real-time monitoring
• Improved disaster management support

**Key Differences:**
✅ INSAT-3DS has faster imaging (15-min vs 1-hour)
✅ Better spatial and temporal resolution
✅ Enhanced weather prediction capabilities
✅ More advanced data processing algorithms"""
        
        # Check for specific satellite information
        for keyword, info in self.knowledge_base.items():
            if keyword in query_lower:
                return f"📡 **{keyword.upper()} Information:**\n\n{info}"
        
        # Check for general categories
        if any(word in query_lower for word in ['mosdac', 'data', 'archival']):
            return """🏢 **MOSDAC (Meteorological & Oceanographic Satellite Data Archival Centre):**

MOSDAC is ISRO's premier facility that provides:

🛰️ **Satellite Data Services:**
• Real-time and archived satellite data
• Data from Indian satellites (INSAT, SCATSAT, OCEANSAT)
• International satellite data partnerships

📊 **Data Products:**
• Meteorological products for weather forecasting
• Oceanographic data for marine applications
• Climate datasets for research
• Specialized products for agriculture and disaster management

🌍 **Access Methods:**
• Online data portal (mosdac.gov.in)
• FTP services for bulk data
• API access for developers
• Custom data processing services"""
            
        elif any(word in query_lower for word in ['isro', 'space', 'launch', 'mission']):
            return """🚀 **ISRO (Indian Space Research Organisation):**

India's national space agency with remarkable achievements:

🛰️ **Satellite Programs:**
• INSAT series - Communication & meteorology
• CARTOSAT series - Earth observation
• RESOURCESAT series - Natural resource monitoring
• OCEANSAT series - Ocean studies

🌌 **Major Missions:**
• Mars Orbiter Mission (Mangalyaan) - 2014
• Chandrayaan-1 & 2 - Lunar exploration
• Aditya-L1 - Solar mission
• Upcoming: Chandrayaan-3, Gaganyaan (human spaceflight)

🚀 **Launch Vehicles:**
• PSLV - Polar Satellite Launch Vehicle
• GSLV - Geosynchronous Satellite Launch Vehicle
• GSLV Mark III - Heavy-lift capability"""
            
        else:
            return """🤖 **Dhruv_Tara Mission Control** - I can help you with:

🛰️ **MOSDAC Satellite Data:**
• Data access and products
• Satellite specifications
• Data processing services

🚀 **ISRO Missions:**
• Satellite programs (INSAT, CARTOSAT, etc.)
• Space missions (Mars, Moon, Sun)
• Launch vehicle information

🌍 **Earth Observation:**
• Remote sensing applications
• Weather and climate data
• Ocean and atmospheric studies

**Example Questions:**
• "What is the difference between INSAT-3D and INSAT-3DS?"
• "How can I access MOSDAC data?"
• "Tell me about ISRO's Mars mission"
• "What are the features of CARTOSAT satellites?"

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
