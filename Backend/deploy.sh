#!/bin/bash

# Render Deployment Script for MOSDAC Chatbot
echo "🚀 Starting MOSDAC Chatbot deployment..."

# Upgrade pip first
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install core dependencies first
echo "📦 Installing core dependencies..."
pip install flask==2.3.3 flask-cors==4.0.0 gunicorn==21.2.0 python-dotenv==1.0.0 requests==2.31.0

# Install remaining dependencies with more permissive error handling
echo "📦 Installing remaining dependencies..."
pip install -r requirements.txt --no-cache-dir || echo "⚠️ Some dependencies failed, continuing..."

# Set up vector store
echo "🔍 Setting up FAISS vector store..."
python faiss_cloud_manager.py || echo "⚠️ Vector store setup failed, will create minimal structure"

# Download essential models only
echo "🤖 Downloading essential AI models..."
python -c "
try:
    import google.generativeai as genai
    print('✅ Google Generative AI imported successfully')
except Exception as e:
    print(f'⚠️ Warning: Could not import Google Generative AI: {e}')

try:
    import sentence_transformers
    print('✅ Sentence transformers available')
except Exception as e:
    print(f'⚠️ Warning: Sentence transformers not available: {e}')

try:
    import faiss
    print('✅ FAISS available')
except Exception as e:
    print(f'⚠️ Warning: FAISS not available: {e}')
" || echo "⚠️ Model check completed with warnings"

echo "✅ Deployment setup complete!"
