import os
import json
from pathlib import Path
import logging
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGChunker:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        """
        Initialize the RAG chunker with LangChain's RecursiveCharacterTextSplitter
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
        logger.info(f"Initialized RAG chunker with chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for better chunking
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove common HTML artifacts
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        
        # Remove excessive newlines
        text = text.replace("\n\n\n", "\n\n")
        
        return text.strip()
    
    def chunk_text_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Chunk a single text file and return structured chunks
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Clean the text
            cleaned_text = self.clean_text(text)
            
            if not cleaned_text:
                logger.warning(f"Empty or invalid text in {file_path}")
                return []
            
            # Split the text into chunks
            chunks = self.text_splitter.split_text(cleaned_text)
            
            # Create structured chunk objects
            structured_chunks = []
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:  # Skip very short chunks
                    continue
                
                # Create a unique ID for the chunk
                chunk_id = hashlib.md5(f"{file_path.name}_{i}_{chunk[:100]}".encode()).hexdigest()
                
                structured_chunk = {
                    "id": chunk_id,
                    "content": chunk.strip(),
                    "source_file": file_path.name,
                    "chunk_index": i,
                    "chunk_size": len(chunk),
                    "metadata": {
                        "file_type": "text" if "text_from_pdfs" not in str(file_path) else "pdf_extracted",
                        "file_path": str(file_path),
                        "total_chunks": len(chunks)
                    }
                }
                
                structured_chunks.append(structured_chunk)
            
            logger.info(f"Created {len(structured_chunks)} chunks from {file_path.name}")
            return structured_chunks
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return []
    
    def process_all_text_files(self, text_dirs: List[str]) -> List[Dict[str, Any]]:
        """
        Process all text files from multiple directories
        """
        all_chunks = []
        
        for text_dir in text_dirs:
            dir_path = Path(text_dir)
            if not dir_path.exists():
                logger.warning(f"Directory not found: {text_dir}")
                continue
            
            # Get all text files
            text_files = list(dir_path.glob("*.txt"))
            logger.info(f"Found {len(text_files)} text files in {text_dir}")
            
            # Process each file
            for text_file in text_files:
                chunks = self.chunk_text_file(text_file)
                all_chunks.extend(chunks)
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def save_chunks_to_json(self, chunks: List[Dict[str, Any]], output_file: str):
        """
        Save chunks to JSON file
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(chunks)} chunks to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving chunks: {str(e)}")
            raise
    
    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the chunks
        """
        if not chunks:
            return {}
        
        # Calculate statistics
        total_chunks = len(chunks)
        avg_chunk_size = sum(chunk['chunk_size'] for chunk in chunks) / total_chunks
        min_chunk_size = min(chunk['chunk_size'] for chunk in chunks)
        max_chunk_size = max(chunk['chunk_size'] for chunk in chunks)
        
        # Count files
        unique_files = set(chunk['source_file'] for chunk in chunks)
        
        # Count file types
        file_types = {}
        for chunk in chunks:
            file_type = chunk['metadata']['file_type']
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        stats = {
            'total_chunks': total_chunks,
            'unique_files': len(unique_files),
            'average_chunk_size': round(avg_chunk_size, 2),
            'min_chunk_size': min_chunk_size,
            'max_chunk_size': max_chunk_size,
            'file_types': file_types
        }
        
        logger.info("Chunk Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        return stats

def main():
    """
    Main function to chunk all text files for RAG
    """
    # Define directories containing text files
    text_directories = [
        "mosdac_data/text",
        "mosdac_data/text_from_pdfs"
    ]
    
    # Output file
    output_file = "mosdac_data/rag_chunks.json"
    
    # Initialize chunker
    chunker = RAGChunker(chunk_size=500, chunk_overlap=50)
    
    try:
        # Process all text files
        logger.info("Starting text chunking for RAG...")
        chunks = chunker.process_all_text_files(text_directories)
        
        if not chunks:
            logger.warning("No chunks created. Check if text files exist.")
            return
        
        # Get statistics
        stats = chunker.get_chunk_statistics(chunks)
        
        # Save chunks to JSON
        chunker.save_chunks_to_json(chunks, output_file)
        
        # Show some sample chunks
        logger.info("Sample chunks:")
        for i, chunk in enumerate(chunks[:3]):
            logger.info(f"Chunk {i+1}:")
            logger.info(f"  ID: {chunk['id'][:20]}...")
            logger.info(f"  Source: {chunk['source_file']}")
            logger.info(f"  Size: {chunk['chunk_size']} characters")
            logger.info(f"  Content preview: {chunk['content'][:100]}...")
            logger.info("")
        
        logger.info("✅ Text chunking completed successfully!")
        logger.info(f"Chunks saved to: {output_file}")
        logger.info("Ready for Step 5: Embedding chunks into vector store")
        
    except Exception as e:
        logger.error(f"Error during chunking: {str(e)}")
        raise

if __name__ == "__main__":
    main() 