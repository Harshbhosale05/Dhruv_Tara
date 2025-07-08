#!/usr/bin/env python3
"""
🤖 Enhanced Hybrid MOSDAC + ISRO Chatbot
Uses comprehensive data from both MOSDAC and ISRO websites
"""

import os
import json
import logging
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedHybridMOSDACChatbot:
    def __init__(self, gemini_api_key: str = None):
        """
        Initialize the enhanced hybrid chatbot with comprehensive data
        """
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Initialize components
        self.setup_vector_store()
        self.setup_neo4j()
        self.setup_gemini(gemini_api_key)
        
        # Conversation memory
        self.conversation_memory = {}
        
        logger.info("✅ Enhanced Hybrid MOSDAC + ISRO Chatbot initialized!")
    
    def setup_vector_store(self):
        """Setup enhanced vector store"""
        try:
            # Load enhanced vector store
            vector_store_dir = Path(self.base_dir) / "enhanced_vector_store"
            
            # Load FAISS index
            index_path = vector_store_dir / "faiss_index.bin"
            self.index = faiss.read_index(str(index_path))
            
            # Load chunks metadata
            chunks_path = vector_store_dir / "chunks_metadata.json"
            with open(chunks_path, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            
            # Load index info
            info_path = vector_store_dir / "index_info.json"
            with open(info_path, 'r', encoding='utf-8') as f:
                self.index_info = json.load(f)
            
            logger.info(f"✅ Loaded enhanced vector store with {len(self.chunks)} chunks")
            
        except Exception as e:
            logger.error(f"❌ Failed to load vector store: {e}")
            raise
    
    def setup_neo4j(self):
        """Setup Neo4j connection"""
        try:
            # Neo4j connection details
            uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
            username = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "Hbhosale@05")
            
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            
            # Test connection
            with self.driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) as count")
                count = result.single()["count"]
                logger.info(f"✅ Connected to Neo4j with {count} nodes")
                
        except Exception as e:
            logger.warning(f"⚠️ Neo4j connection failed: {e}")
            self.driver = None
    
    def setup_gemini(self, api_key: str = None):
        """Setup Gemini LLM"""
        try:
            if not api_key:
                api_key = os.getenv("GEMINI_API_KEY", "")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.gemini_available = True
                logger.info("✅ Gemini LLM configured")
            else:
                self.gemini_available = False
                logger.warning("⚠️ No Gemini API key provided - using fallback mode")
                
        except Exception as e:
            logger.warning(f"⚠️ Gemini setup failed: {e}")
            self.gemini_available = False
    
    def search_rag(self, query: str, k=5) -> List[Dict]:
        """Search using enhanced RAG (vector search)"""
        try:
            # Use SentenceTransformer for query embedding (matching the stored embeddings)
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as ie:
                logger.error(f"❌ SentenceTransformer import failed: {ie}")
                return []
            
            # Initialize SentenceTransformer model with error handling
            model_name = self.index_info.get('model_name', 'all-MiniLM-L6-v2')
            try:
                model = SentenceTransformer(model_name)
            except Exception as model_error:
                logger.error(f"❌ Failed to load SentenceTransformer model '{model_name}': {model_error}")
                # Try with a simpler model as fallback
                try:
                    model = SentenceTransformer('all-MiniLM-L6-v2')
                    logger.info("✅ Loaded fallback model: all-MiniLM-L6-v2")
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback model also failed: {fallback_error}")
                    return []
            
            # Encode query
            query_vector = model.encode([query], convert_to_tensor=False).astype('float32')
            faiss.normalize_L2(query_vector)
            
            # Search FAISS index
            scores, indices = self.index.search(query_vector, k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    results.append({
                        'score': float(score),
                        'content': chunk['content'],
                        'source_file': chunk['source_file'],
                        'source_type': chunk.get('source_type', 'unknown')
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ RAG search failed: {e}")
            return []
    
    def search_knowledge_graph(self, query: str) -> Dict:
        """Search using Neo4j knowledge graph"""
        if not self.driver:
            return {'entities': [], 'relationships': []}
        
        try:
            with self.driver.session() as session:
                # Search for entities
                entity_query = """
                MATCH (n)
                WHERE toLower(n.name) CONTAINS toLower($search_term)
                   OR toLower(n.type) CONTAINS toLower($search_term)
                RETURN n.name as name, n.type as type, labels(n) as labels
                LIMIT 5
                """
                entities = list(session.run(entity_query, search_term=query))
                
                # Get relationships
                rel_query = """
                MATCH (a)-[r]->(b)
                WHERE toLower(a.name) CONTAINS toLower($search_term)
                   OR toLower(b.name) CONTAINS toLower($search_term)
                   OR toLower(type(r)) CONTAINS toLower($search_term)
                RETURN a.name as source, type(r) as relationship, b.name as target
                LIMIT 5
                """
                relationships = list(session.run(rel_query, search_term=query))
                
                return {
                    'entities': [dict(e) for e in entities],
                    'relationships': [dict(r) for r in relationships]
                }
                
        except Exception as e:
            logger.error(f"❌ Knowledge graph search failed: {e}")
            return {'entities': [], 'relationships': []}
    
    def _build_prompt(self, query: str, rag_context: str, kg_context: str, conversation_history: str) -> str:
        """Build comprehensive prompt for Gemini"""
        prompt = f"""You are a helpful AI assistant for MOSDAC (Meteorological and Oceanographic Satellite Data Archival Centre) and ISRO (Indian Space Research Organisation). 
You have access to comprehensive documentation and knowledge graphs about satellites, weather, ocean data, space missions, and related topics from both organizations.

User Question: {query}

{conversation_history}

Available Information:

1. Documentation Context (RAG):
{rag_context if rag_context else "No relevant documentation found."}

2. Knowledge Graph Context:
{kg_context if kg_context else "No relevant knowledge graph information found."}

Instructions:
- FIRST try to answer using the provided MOSDAC and ISRO documentation and knowledge graph data
- If the provided data is insufficient, you may use your own general knowledge about space, satellites, weather, and oceanography
- For ISRO satellite questions, focus on satellites like INSAT-3D, INSAT-3DR, OCEANSAT-2, OCEANSAT-3, SCATSAT-1, SARAL-AltiKa, MeghaTropiques, etc.
- Be specific about sensor types (infrared, microwave, optical, etc.) and their applications
- Always cite your sources when possible
- Be accurate, helpful, and conversational
- If you're using your own knowledge, mention it clearly
- Focus on providing comprehensive, accurate information about ISRO satellites, MOSDAC data, weather forecasting, ocean monitoring, and related topics

Please provide a comprehensive answer:"""

        return prompt
    
    def _fallback_answer(self, query: str, rag_context: str, kg_context: str) -> str:
        """Fallback answer when Gemini is not available"""
        answer_parts = []
        
        if rag_context:
            answer_parts.append("📄 **From MOSDAC/ISRO Documentation:**")
            answer_parts.append(rag_context)
        
        if kg_context:
            answer_parts.append("\n🗺️ **From Knowledge Graph:**")
            answer_parts.append(kg_context)
        
        if answer_parts:
            return "\n".join(answer_parts)
        else:
            return "I couldn't find relevant information in the MOSDAC/ISRO documentation to answer your question. Please try rephrasing your query or ask about topics related to satellite data, weather forecasting, ocean monitoring, or ISRO missions."
    
    def _update_conversation_memory(self, user_id: str, query: str, response: str):
        """Update conversation memory"""
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = []
        
        self.conversation_memory[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response
        })
        
        # Keep only last 5 conversations
        if len(self.conversation_memory[user_id]) > 5:
            self.conversation_memory[user_id] = self.conversation_memory[user_id][-5:]
    
    def _get_conversation_history(self, user_id: str) -> str:
        """Get conversation history for user"""
        if user_id not in self.conversation_memory:
            return ""
        
        history = []
        for conv in self.conversation_memory[user_id][-3:]:  # Last 3 conversations
            history.append(f"User: {conv['query']}")
            history.append(f"Assistant: {conv['response'][:200]}...")
        
        return "\n".join(history) if history else ""
    
    def chat(self, query: str, user_id: str = "default") -> str:
        """
        Main chat method - processes query and returns response
        """
        logger.info(f"🤖 Processing query: {query}")
        
        try:
            # Step 1: Search RAG
            logger.info("🔍 Searching RAG...")
            rag_results = self.search_rag(query, k=3)
            rag_context = ""
            if rag_results:
                rag_context = "\n\n".join([
                    f"**Source: {r['source_file']}**\n{r['content'][:300]}..."
                    for r in rag_results
                ])
            
            # Step 2: Search Knowledge Graph
            logger.info("🗺️ Searching Knowledge Graph...")
            kg_results = self.search_knowledge_graph(query)
            kg_context = ""
            if kg_results['entities'] or kg_results['relationships']:
                kg_parts = []
                if kg_results['entities']:
                    kg_parts.append("**Entities:**")
                    for entity in kg_results['entities']:
                        kg_parts.append(f"- {entity['name']} ({entity['type']})")
                if kg_results['relationships']:
                    kg_parts.append("**Relationships:**")
                    for rel in kg_results['relationships']:
                        kg_parts.append(f"- {rel['source']} --[{rel['relationship']}]--> {rel['target']}")
                kg_context = "\n".join(kg_parts)
            
            # Step 3: Get conversation history
            conversation_history = self._get_conversation_history(user_id)
            
            # Step 4: Generate response
            if self.gemini_available:
                logger.info("🤖 Generating answer with Gemini...")
                prompt = self._build_prompt(query, rag_context, kg_context, conversation_history)
                
                response = self.gemini_model.generate_content(prompt)
                answer = response.text
            else:
                logger.info("🤖 Using fallback answer...")
                answer = self._fallback_answer(query, rag_context, kg_context)
            
            # Step 5: Update conversation memory
            self._update_conversation_memory(user_id, query, answer)
            
            logger.info("✅ Response generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Error in chat: {e}")
            return f"I apologize, but I encountered an error while processing your query: {str(e)}. Please try again."
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        return {
            "total_chunks": len(self.chunks),
            "vector_store_dimension": self.index_info.get('dimension', 'unknown'),
            "neo4j_connected": self.driver is not None,
            "gemini_available": self.gemini_available,
            "data_sources": ["MOSDAC", "ISRO"],
            "enhanced_data": True
        }

def main():
    """Main function for interactive chat"""
    print("🤖 Enhanced Hybrid MOSDAC + ISRO Chatbot")
    print("=" * 50)
    
    # Use provided Gemini API key
    api_key = "AIzaSyDz_C5YEYgvPOhSdY6cLe2yZBLbGfkffao"
    
    # Initialize chatbot
    chatbot = EnhancedHybridMOSDACChatbot(api_key)
    
    # Show system info
    info = chatbot.get_system_info()
    print(f"\n📊 System Info:")
    print(f"   Total chunks: {info['total_chunks']}")
    print(f"   Vector dimension: {info['vector_store_dimension']}")
    print(f"   Neo4j connected: {info['neo4j_connected']}")
    print(f"   Gemini available: {info['gemini_available']}")
    print(f"   Data sources: {', '.join(info['data_sources'])}")
    
    print("\n💬 Start chatting! (Type 'quit' to exit)")
    print("-" * 50)
    
    user_id = "interactive_user"
    
    while True:
        try:
            query = input("\n👤 You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'bye']:
                print("🤖 Goodbye! 👋")
                break
            
            if not query:
                continue
            
            print("🤖 Bot: ", end="", flush=True)
            response = chatbot.chat(query, user_id)
            print(response)
            
        except KeyboardInterrupt:
            print("\n🤖 Goodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 