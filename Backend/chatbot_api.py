#!/usr/bin/env python3
"""
REST API for Enhanced Hybrid MOSDAC + ISRO Chatbot
Serves as a backend for the Next.js frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import json
from minimal_chatbot import MinimalMOSDACChatbot
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for all origins (more permissive for deployment)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:3001", "http://127.0.0.1:3001", "https://mosdac-chatbot-frontend.onrender.com", "https://dhruvtara1.onrender.com"], supports_credentials=True)  # Enable CORS for all frontends

# Load API key
api_key = os.getenv("GEMINI_API_KEY", "")
if not api_key:
    logger.warning("⚠️ GEMINI_API_KEY not found in environment variables. Chatbot will use fallback responses.")

# Initialize chatbot
chatbot = None

# Initialize chatbot on first use instead of using before_first_request
def get_chatbot():
    global chatbot
    if chatbot is None:
        try:
            logger.info("Initializing chatbot...")
            chatbot = MinimalMOSDACChatbot(api_key)
            logger.info("✅ Chatbot initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize chatbot: {e}")
            raise
    return chatbot

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat requests
    """
    try:
        # Get request data
        data = request.json
        query = data.get('query')
        user_id = data.get('user_id', 'api_user')
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        # Get or initialize chatbot
        try:
            chatbot = get_chatbot()
        except Exception as e:
            logger.error(f"❌ Failed to initialize chatbot: {e}")
            return jsonify({"error": "Failed to initialize chatbot", "details": str(e)}), 500
        
        # Process query
        logger.info(f"Processing chat request: {query}")
        try:
            response = chatbot.chat(query, user_id)
            logger.info(f"Chat response generated successfully")
            return jsonify({"response": response})
        except Exception as chat_error:
            logger.error(f"❌ Chat processing error: {chat_error}")
            # Return a fallback response instead of failing
            fallback_response = "I apologize, but I'm experiencing some technical difficulties. Please try again later."
            return jsonify({"response": fallback_response, "status": "fallback"})
        
    except Exception as e:
        logger.error(f"❌ Error processing chat request: {e}")
        return jsonify({"error": "An error occurred while processing your request", "details": str(e)}), 500

@app.route('/system-info', methods=['GET'])
def system_info():
    """
    Get system information
    """
    try:
        # Get or initialize chatbot
        try:
            chatbot = get_chatbot()
        except Exception as e:
            logger.error(f"❌ Failed to initialize chatbot: {e}")
            return jsonify({"error": "Failed to initialize chatbot", "details": str(e)}), 500
        
        info = chatbot.get_system_info()
        return jsonify(info)
        
    except Exception as e:
        logger.error(f"❌ Error getting system info: {e}")
        return jsonify({"error": "An error occurred while getting system info", "details": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check if chatbot can be initialized
        bot = get_chatbot()
        
        # Check Neo4j connection
        neo4j_status = "unknown"
        try:
            if hasattr(bot, 'driver') and bot.driver:
                with bot.driver.session() as session:
                    session.run("RETURN 1")
                neo4j_status = "connected"
        except Exception:
            neo4j_status = "disconnected"
        
        # Check vector store
        vector_store_status = "unknown"
        try:
            if hasattr(bot, 'vector_store') and bot.vector_store:
                vector_store_status = "loaded"
            elif os.path.exists('enhanced_vector_store'):
                vector_store_status = "available"
            else:
                vector_store_status = "missing"
        except Exception:
            vector_store_status = "error"
        
        return jsonify({
            'status': 'healthy',
            'chatbot': 'initialized',
            'neo4j': neo4j_status,
            'vector_store': vector_store_status,
            'timestamp': str(os.getpid())
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': str(os.getpid())
        }), 500

@app.route('/', methods=['GET'])
def index():
    """
    API root endpoint
    """
    return jsonify({
        "name": "MOSDAC + ISRO Chatbot API",
        "version": "1.0.0",
        "endpoints": [
            {
                "path": "/chat",
                "method": "POST",
                "description": "Chat with the MOSDAC + ISRO bot",
                "parameters": ["query", "user_id (optional)"]
            },
            {
                "path": "/system-info",
                "method": "GET",
                "description": "Get system information"
            },
            {
                "path": "/health",
                "method": "GET",
                "description": "Health check endpoint"
            }
        ]
    })

if __name__ == "__main__":
    # Change to the Backend directory to ensure correct relative paths
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    logger.info(f"Changed working directory to: {backend_dir}")
    
    # Use environment variables for host and port if available
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 5000))
    
    # Run the app
    logger.info(f"Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=True)
