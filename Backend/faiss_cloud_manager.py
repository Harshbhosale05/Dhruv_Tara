"""
FAISS Vector Store Cloud Manager for Render Deployment
This script handles uploading and downloading FAISS vector store to/from cloud storage
"""

import os
import json
import shutil
import requests
from pathlib import Path
import zipfile
import tempfile

class FAISSCloudManager:
    def __init__(self):
        self.vector_store_path = "enhanced_vector_store"
        self.github_repo = None  # You can use GitHub as free storage for small files
        self.backup_url = None   # Or use a free file hosting service
        
    def zip_vector_store(self):
        """Zip the vector store directory for upload"""
        zip_path = "vector_store_backup.zip"
        
        if os.path.exists(self.vector_store_path):
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.vector_store_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start='.')
                        zipf.write(file_path, arcname)
            
            print(f"Vector store zipped to {zip_path}")
            return zip_path
        else:
            print("Vector store directory not found!")
            return None
    
    def download_vector_store_from_github(self, repo_url, branch="main"):
        """Download vector store from GitHub repository"""
        try:
            # Example: https://github.com/username/repo/archive/refs/heads/main.zip
            download_url = f"{repo_url}/archive/refs/heads/{branch}.zip"
            
            print(f"Downloading vector store from: {download_url}")
            response = requests.get(download_url)
            
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
                
                # Extract the zip file
                with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                    zip_ref.extractall('temp_extract')
                
                # Move the vector store directory
                extracted_dirs = os.listdir('temp_extract')
                if extracted_dirs:
                    source_path = os.path.join('temp_extract', extracted_dirs[0], 'enhanced_vector_store')
                    if os.path.exists(source_path):
                        if os.path.exists(self.vector_store_path):
                            shutil.rmtree(self.vector_store_path)
                        shutil.move(source_path, self.vector_store_path)
                        print("Vector store downloaded and extracted successfully!")
                        return True
                
                # Cleanup
                os.unlink(tmp_path)
                shutil.rmtree('temp_extract', ignore_errors=True)
                
            else:
                print(f"Failed to download: Status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error downloading vector store: {e}")
            return False
    
    def download_from_direct_url(self, file_url):
        """Download vector store from a direct URL (like Google Drive, Dropbox, etc.)"""
        try:
            print(f"Downloading vector store from: {file_url}")
            response = requests.get(file_url, stream=True)
            
            if response.status_code == 200:
                zip_path = "downloaded_vector_store.zip"
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract the downloaded zip
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall('.')
                
                os.remove(zip_path)
                print("Vector store downloaded and extracted successfully!")
                return True
            else:
                print(f"Failed to download: Status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error downloading vector store: {e}")
            return False
    
    def create_vector_store_if_missing(self):
        """Create a minimal vector store structure if missing"""
        if not os.path.exists(self.vector_store_path):
            os.makedirs(self.vector_store_path, exist_ok=True)
            
            # Create minimal metadata file
            metadata = {
                "created": "auto-generated",
                "chunks_count": 0,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
            
            with open(os.path.join(self.vector_store_path, "index_info.json"), 'w') as f:
                json.dump(metadata, f)
            
            # Create empty chunks metadata
            with open(os.path.join(self.vector_store_path, "chunks_metadata.json"), 'w') as f:
                json.dump([], f)
            
            print("Created minimal vector store structure")
            return True
        
        return False

def setup_vector_store_for_render():
    """Main function to set up vector store for Render deployment"""
    manager = FAISSCloudManager()
    
    # Method 1: Try to download from GitHub (if you have uploaded it there)
    # github_repo_url = "https://github.com/yourusername/your-vector-store-repo"
    # if manager.download_vector_store_from_github(github_repo_url):
    #     return True
    
    # Method 2: Try to download from direct URL (Google Drive, Dropbox, etc.)
    # direct_url = "https://your-file-hosting-service.com/vector_store.zip"
    # if manager.download_from_direct_url(direct_url):
    #     return True
    
    # Method 3: Create minimal structure if nothing else works
    print("Creating minimal vector store structure...")
    manager.create_vector_store_if_missing()
    return True

if __name__ == "__main__":
    setup_vector_store_for_render()
