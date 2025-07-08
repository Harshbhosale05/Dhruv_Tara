import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorStoreEmbedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize the vector store embedder with SentenceTransformer
        """
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        
        try:
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"✅ Successfully loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"❌ Error loading embedding model: {str(e)}")
            raise
        
        # Initialize FAISS index
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.chunks = []
        self.chunk_ids = []
        
        logger.info(f"Initialized FAISS index with dimension: {self.dimension}")
    
    def load_chunks(self, chunks_file: str) -> List[Dict[str, Any]]:
        """
        Load chunks from JSON file
        """
        try:
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            logger.info(f"Loaded {len(chunks)} chunks from {chunks_file}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error loading chunks: {str(e)}")
            raise
    
    def embed_chunks(self, chunks: List[Dict[str, Any]], batch_size=32) -> np.ndarray:
        """
        Embed chunks using SentenceTransformer
        """
        logger.info(f"Starting embedding of {len(chunks)} chunks...")
        
        # Extract text content
        texts = [chunk['content'] for chunk in chunks]
        
        # Embed in batches
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(batch_texts, show_progress_bar=True)
            embeddings.append(batch_embeddings)
            
            logger.info(f"Embedded batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        # Concatenate all embeddings
        all_embeddings = np.vstack(embeddings)
        
        logger.info(f"✅ Completed embedding. Shape: {all_embeddings.shape}")
        return all_embeddings
    
    def build_faiss_index(self, embeddings: np.ndarray, chunks: List[Dict[str, Any]]):
        """
        Build FAISS index from embeddings
        """
        logger.info("Building FAISS index...")
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Store chunks and IDs for retrieval
        self.chunks = chunks
        self.chunk_ids = [chunk['id'] for chunk in chunks]
        
        logger.info(f"✅ FAISS index built with {self.index.ntotal} vectors")
    
    def save_index(self, output_dir: str):
        """
        Save FAISS index and metadata
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save FAISS index
        faiss_index_path = output_path / "faiss_index.bin"
        faiss.write_index(self.index, str(faiss_index_path))
        
        # Save chunks metadata
        chunks_metadata_path = output_path / "chunks_metadata.json"
        with open(chunks_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
        
        # Save index info
        index_info = {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "total_vectors": self.index.ntotal,
            "index_type": "IndexFlatIP",
            "chunk_ids": self.chunk_ids
        }
        
        index_info_path = output_path / "index_info.json"
        with open(index_info_path, 'w', encoding='utf-8') as f:
            json.dump(index_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved FAISS index to: {faiss_index_path}")
        logger.info(f"✅ Saved chunks metadata to: {chunks_metadata_path}")
        logger.info(f"✅ Saved index info to: {index_info_path}")
    
    def test_search(self, query: str, k=5):
        """
        Test semantic search functionality
        """
        logger.info(f"Testing search with query: '{query}'")
        
        # Embed the query
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        logger.info("Search results:")
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            chunk = self.chunks[idx]
            logger.info(f"  {i+1}. Score: {score:.4f}")
            logger.info(f"     Source: {chunk['source_file']}")
            logger.info(f"     Content: {chunk['content'][:100]}...")
            logger.info("")
        
        return scores[0], indices[0]

def main():
    """
    Main function to embed chunks and build vector store
    """
    # Configuration
    chunks_file = "mosdac_data/rag_chunks.json"
    output_dir = "mosdac_data/vector_store"
    
    try:
        # Initialize embedder
        logger.info("Initializing vector store embedder...")
        embedder = VectorStoreEmbedder()
        
        # Load chunks
        logger.info("Loading chunks...")
        chunks = embedder.load_chunks(chunks_file)
        
        if not chunks:
            logger.error("No chunks found!")
            return
        
        # Embed chunks
        logger.info("Embedding chunks...")
        embeddings = embedder.embed_chunks(chunks)
        
        # Build FAISS index
        logger.info("Building FAISS index...")
        embedder.build_faiss_index(embeddings, chunks)
        
        # Save index
        logger.info("Saving index...")
        embedder.save_index(output_dir)
        
        # Test search functionality
        logger.info("Testing search functionality...")
        test_queries = [
            "INSAT-3D satellite",
            "ocean surface temperature",
            "weather forecasting",
            "MOSDAC data access"
        ]
        
        for query in test_queries:
            embedder.test_search(query, k=3)
        
        logger.info("✅ Vector store creation completed successfully!")
        logger.info(f"Index saved to: {output_dir}")
        logger.info("Ready for Step 6: Building LangChain RAG Chatbot")
        
    except Exception as e:
        logger.error(f"Error during vector store creation: {str(e)}")
        raise

if __name__ == "__main__":
    main() 