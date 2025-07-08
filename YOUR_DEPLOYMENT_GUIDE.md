# 🚀 Your MOSDAC Chatbot Deployment Guide

## ✅ What's Already Configured

Your Neo4j AuraDB details have been updated:
- **URI:** neo4j+s://94588e50.databases.neo4j.io
- **Username:** hbhosale2004@gmail.com
- **Password:** Hbhosale@05
- **Project ID:** f9df8f0a-e177-4347-944a-c7bea47336b7
- **Instance ID:** 94588e50

## 📋 Step-by-Step Deployment

### Step 1: Prepare FAISS Vector Store

#### Option A: Upload to GitHub (Recommended)
```bash
# 1. Create a new GitHub repository called "mosdac-vector-store"
# 2. Upload your enhanced_vector_store/ folder to it
# 3. Make it public or provide access token

# Commands to prepare:
cd enhanced_vector_store
git init
git add .
git commit -m "Initial vector store"
git branch -M main
git remote add origin https://github.com/yourusername/mosdac-vector-store.git
git push -u origin main
```

#### Option B: Upload to Google Drive
```bash
# 1. Zip your vector store
zip -r vector_store.zip enhanced_vector_store/

# 2. Upload to Google Drive
# 3. Get shareable link (make sure it's public)
# 4. Convert to direct download link:
# From: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
# To: https://drive.google.com/uc?export=download&id=FILE_ID
```

### Step 2: Update faiss_cloud_manager.py

Edit the file and uncomment/update the appropriate method:

```python
def setup_vector_store_for_render():
    manager = FAISSCloudManager()
    
    # If using GitHub:
    github_repo_url = "https://github.com/yourusername/mosdac-vector-store"
    if manager.download_vector_store_from_github(github_repo_url):
        return True
    
    # OR if using Google Drive:
    # direct_url = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"
    # if manager.download_from_direct_url(direct_url):
    #     return True
    
    # Fallback: create minimal structure
    manager.create_vector_store_if_missing()
    return True
```

### Step 3: Deploy to Render

1. **Push to GitHub:**
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Sign up/login with GitHub
   - Click "New +" → "Web Service"
   - Connect your repository

3. **Configure Render:**
   - **Name:** mosdac-chatbot-api
   - **Build Command:** `cd Backend && chmod +x deploy.sh && ./deploy.sh`
   - **Start Command:** `cd Backend && gunicorn --bind 0.0.0.0:$PORT --timeout 120 chatbot_api:app`

4. **Set Environment Variables in Render Dashboard:**
```
GEMINI_API_KEY=AIzaSyDz_C5YEYgvPOhSdY6cLe2yZBLbGfkffao
NEO4J_URI=neo4j+s://94588e50.databases.neo4j.io
NEO4J_USER=hbhosale2004@gmail.com
NEO4J_PASSWORD=Hbhosale@05
API_HOST=0.0.0.0
API_PORT=$PORT
```

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for build to complete (10-15 minutes)

### Step 4: Test Your Deployment

1. **Get your Render URL:**
   - Example: `https://mosdac-chatbot-api.onrender.com`

2. **Test endpoints:**
```bash
# Health check
curl https://your-app.onrender.com/health

# Chat endpoint
curl -X POST https://your-app.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, tell me about MOSDAC"}'
```

### Step 5: Update Frontend

Update your frontend to use the deployed backend:

```typescript
// In your React app
const API_BASE_URL = 'https://your-app.onrender.com';

const sendMessage = async (message: string) => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });
  return response.json();
};
```

## 🔍 Troubleshooting

### Common Issues:

1. **Build Timeout:**
   - Reduce model downloads in deploy.sh
   - Use smaller sentence transformer models

2. **Vector Store Not Found:**
   - Check faiss_cloud_manager.py logs
   - Verify GitHub repo/file URLs
   - Ensure files are publicly accessible

3. **Neo4j Connection Issues:**
   - Verify AuraDB is running
   - Check firewall settings in Neo4j console
   - Confirm credentials are correct

4. **Memory Issues:**
   - Reduce batch sizes in your code
   - Use lighter models
   - Upgrade to Render paid plan

### Logs and Monitoring:
```bash
# View Render logs in dashboard
# Or use Render CLI:
render logs --service your-service-id
```

## 💡 Tips for Success

1. **Start Small:** Deploy with minimal vector store first
2. **Monitor Logs:** Watch build and runtime logs carefully
3. **Test Locally:** Ensure everything works locally before deploying
4. **Backup Strategy:** Keep your vector store backed up in multiple places

## 🔄 Updating Your Deployment

When you make changes:
```bash
git add .
git commit -m "Update: description of changes"
git push origin main
# Render will auto-deploy
```

Your deployment is now ready! 🎉
