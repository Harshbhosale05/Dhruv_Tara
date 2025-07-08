# Cloud Deployment Guide for Hybrid Chatbot

## 🚀 Recommended Cloud Platforms

### 1. **RENDER** (Easiest for beginners)
**Best for:** Quick deployment, auto-scaling, simple setup
- **Free Tier:** Yes (750 hours/month)
- **Database Support:** PostgreSQL, Redis
- **Pros:** Easy deployment, automatic HTTPS, GitHub integration
- **Cons:** No Neo4j managed service

### 2. **Railway** 
**Best for:** Full-stack apps with databases
- **Free Tier:** $5 credit/month
- **Database Support:** PostgreSQL, MySQL, Redis, MongoDB
- **Pros:** Very easy setup, great for Node.js/Python
- **Cons:** Limited free tier

### 3. **Google Cloud Platform (GCP)**
**Best for:** Production apps, AI/ML workloads
- **Free Tier:** $300 credit for 90 days
- **Database Support:** All major databases
- **Pros:** Vertex AI integration, Gemini API native support
- **Cons:** More complex setup

### 4. **DigitalOcean App Platform**
**Best for:** Scalable applications
- **Free Tier:** Static sites only
- **Pros:** Simple pricing, good performance
- **Cons:** No free backend hosting

## 🗄️ Neo4j Database Cloud Options

### 1. **Neo4j AuraDB** (Recommended)
```python
# Cloud Neo4j connection
URI = "neo4j+s://your-instance.databases.neo4j.io"
AUTH = ("neo4j", "your-password")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
```
- **Free Tier:** Yes (1 instance, 50k nodes)
- **Setup:** Create account at neo4j.com/cloud/aura
- **Pros:** Managed, secure, auto-backups
- **Cost:** Free tier → $65/month for production

### 2. **Neo4j on Cloud VMs**
- Deploy Neo4j on AWS EC2, GCP Compute, or DigitalOcean Droplets
- **Cost:** $5-20/month for small instances
- **Setup:** Manual but more control

## 📊 Vector Database Cloud Options

### 1. **Pinecone** (Easiest)
```python
import pinecone

pinecone.init(
    api_key="your-api-key",
    environment="your-env"
)

index = pinecone.Index("your-index-name")
```
- **Free Tier:** 1M vectors, 1 index
- **Pros:** Managed, fast, simple API
- **Cons:** Limited free tier

### 2. **Weaviate Cloud**
```python
import weaviate

client = weaviate.Client(
    url="https://your-instance.weaviate.network",
    auth_client_secret=weaviate.AuthApiKey("your-api-key")
)
```
- **Free Tier:** 1 cluster for 14 days
- **Pros:** Open source, GraphQL API
- **Cons:** Limited free tier

### 3. **Qdrant Cloud**
```python
from qdrant_client import QdrantClient

client = QdrantClient(
    url="https://your-instance.qdrant.tech",
    api_key="your-api-key"
)
```
- **Free Tier:** 1GB storage
- **Pros:** Fast, efficient, good free tier
- **Cons:** Newer platform

### 4. **FAISS on Cloud Storage** (Current approach)
```python
# Upload FAISS index to cloud storage
# AWS S3, Google Cloud Storage, or Azure Blob
import boto3

s3 = boto3.client('s3')
s3.upload_file('faiss_index.bin', 'your-bucket', 'faiss_index.bin')
```
- **Cost:** Very cheap ($0.023/GB/month on AWS S3)
- **Pros:** Keep current code, minimal changes
- **Cons:** Manual scaling, no query optimization

## 🛠️ Deployment Steps

### Option A: Render Deployment (Recommended for beginners)

1. **Prepare your project:**
```bash
# Add to requirements.txt
python-dotenv==1.0.0
gunicorn==21.2.0
```

2. **Create render.yaml:**
```yaml
services:
  - type: web
    name: chatbot-api
    env: python
    buildCommand: pip install -r Backend/requirements.txt
    startCommand: cd Backend && gunicorn --bind 0.0.0.0:$PORT chatbot_api:app
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: NEO4J_URI
        sync: false
      - key: NEO4J_PASSWORD
        sync: false
```

3. **Deploy:**
   - Connect GitHub repo to Render
   - Set environment variables in Render dashboard
   - Deploy!

### Option B: Railway Deployment

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
railway login
```

2. **Deploy:**
```bash
cd Backend
railway init
railway add --service postgresql  # If needed
railway deploy
```

### Option C: Google Cloud Run (Advanced)

1. **Create Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY Backend/requirements.txt .
RUN pip install -r requirements.txt

COPY Backend/ .
EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 chatbot_api:app
```

2. **Deploy:**
```bash
gcloud run deploy chatbot-api --source . --platform managed --region us-central1
```

## 🔧 FAISS Vector Database on Render

Since Render doesn't have persistent storage, here are 3 ways to handle your FAISS vector store:

### Method 1: GitHub Repository (Recommended for small files)
```bash
# 1. Create a separate GitHub repo for your vector store
# 2. Upload your enhanced_vector_store/ folder there
# 3. In faiss_cloud_manager.py, set the GitHub repo URL
# 4. During Render build, it will download the vector store

# Example:
github_repo_url = "https://github.com/yourusername/mosdac-vector-store"
```

### Method 2: File Hosting Services
Upload your vector store zip to:
- **Google Drive** (make publicly accessible)
- **Dropbox** (get direct download link)
- **GitHub Releases** (for larger files)
- **Mega.nz** (50GB free)

### Method 3: Rebuild on First Request
```python
# In your chatbot code, add logic to rebuild vector store if missing
def ensure_vector_store_exists():
    if not os.path.exists('enhanced_vector_store/faiss_index.bin'):
        print("Vector store not found, rebuilding...")
        # Call your RAG chunker and embedder
        rebuild_vector_store()
```

### Method 4: Use Render's Build Cache
```yaml
# In render.yaml, cache the vector store between builds
services:
  - type: web
    buildCommand: |
      cd Backend
      # Check if vector store exists from previous build
      if [ ! -d "enhanced_vector_store" ]; then
        python faiss_cloud_manager.py
      fi
      pip install -r requirements.txt
```

## 🔧 Code Changes for Cloud Deployment

### 1. Update environment variable loading:

```python
# In your Python files
import os
from dotenv import load_dotenv

load_dotenv()

# Replace hardcoded values with:
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
```

### 2. Add health check endpoint:

```python
# In chatbot_api.py
@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200
```

### 3. Add CORS for frontend:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://your-frontend-domain.com'])
```

## 💰 Cost Breakdown (Monthly)

### Budget Option ($0-10/month):
- **Backend:** Render Free Tier
- **Database:** Neo4j Aura Free + Pinecone Free
- **Vector Store:** FAISS on cloud storage
- **Total:** ~$5/month

### Production Option ($50-100/month):
- **Backend:** Railway Pro or GCP Cloud Run
- **Database:** Neo4j Aura Professional
- **Vector Store:** Pinecone Standard
- **Total:** ~$80/month

### Enterprise Option ($200+/month):
- **Backend:** Auto-scaling cloud services
- **Database:** Neo4j Enterprise Cloud
- **Vector Store:** Weaviate/Qdrant Pro
- **Total:** $200+/month

## 📝 Next Steps

1. **Choose your platform** (I recommend starting with Render)
2. **Set up Neo4j AuraDB** (free tier)
3. **Choose vector database** (Pinecone for simplicity)
4. **Update your code** to use environment variables
5. **Deploy and test**

## 🔗 Useful Links

- [Render Documentation](https://render.com/docs)
- [Neo4j AuraDB](https://neo4j.com/cloud/aura/)
- [Pinecone](https://www.pinecone.io/)
- [Railway](https://railway.app/)
- [Google Cloud Run](https://cloud.google.com/run)

Let me know which option you'd like to proceed with, and I can help you set it up step by step!
