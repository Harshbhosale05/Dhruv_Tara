#!/bin/bash

# Render Deployment Script for MOSDAC Chatbot
echo "🚀 Starting MOSDAC Chatbot deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set up vector store
echo "🔍 Setting up FAISS vector store..."
python faiss_cloud_manager.py

# Download any additional models if needed
echo "🤖 Downloading AI models..."
python -c "
import sentence_transformers
try:
    model = sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2')
    print('✅ Sentence transformer model loaded successfully')
except Exception as e:
    print(f'⚠️ Warning: Could not load sentence transformer: {e}')

try:
    import google.generativeai as genai
    print('✅ Google Generative AI imported successfully')
except Exception as e:
    print(f'⚠️ Warning: Could not import Google Generative AI: {e}')
"

echo "✅ Deployment setup complete!"
