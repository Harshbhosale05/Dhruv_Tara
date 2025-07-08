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
from enhanced_hybrid_chatbot import EnhancedHybridMOSDACChatbot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:3001", "http://127.0.0.1:3001"]}})  # Enable CORS for all frontends

# Load API key
api_key = "AIzaSyDKrNSwJGKbZJ9NbQtpj9b-QHUtWlpimQU"

# Initialize chatbot
chatbot = None

# Initialize chatbot on first use instead of using before_first_request
def get_chatbot():
    global chatbot
    if chatbot is None:
        try:
            logger.info("Initializing chatbot...")
            chatbot = EnhancedHybridMOSDACChatbot(api_key)
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
        response = chatbot.chat(query, user_id)
        
        return jsonify({"response": response})
        
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
            }
        ]
    })

if __name__ == "__main__":
    # Use environment variables for host and port if available
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 5000))
    
    # Run the app
    logger.info(f"Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=True)
