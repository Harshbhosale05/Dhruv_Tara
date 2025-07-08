#!/usr/bin/env python3
"""
🔄 Simple Data Processing Pipeline
Processes crawled data and updates the chatbot system
"""

import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_processing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.base_dir = "mosdac_data"
        self.setup_directories()
        
    def setup_directories(self):
        """Ensure all necessary directories exist"""
        dirs = [
            f"{self.base_dir}/combined_text",
            f"{self.base_dir}/combined_pdfs",
            f"{self.base_dir}/final_vector_store"
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory: {dir_path}")
    
    def merge_text_data(self):
        """Merge all text data from different sources"""
        logger.info("📝 Merging text data...")
        
        # Sources to merge
        text_sources = [
            f"{self.base_dir}/text",
            f"{self.base_dir}/text_from_pdfs"
        ]
        
        combined_text = []
        
        for source in text_sources:
            if Path(source).exists():
                for file_path in Path(source).glob("*.txt"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.strip():  # Only add non-empty content
                                combined_text.append({
                                    'source_file': str(file_path),
                                    'content': content,
                                    'type': 'text'
                                })
                    except Exception as e:
                        logger.warning(f"Failed to read {file_path}: {e}")
        
        # Save combined text
        output_file = f"{self.base_dir}/combined_text/all_text_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_text, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Merged {len(combined_text)} text files")
        return combined_text
    
    def merge_pdf_data(self):
        """Merge all PDF files"""
        logger.info("📄 Merging PDF data...")
        
        pdf_sources = [
            f"{self.base_dir}/pdfs"
        ]
        
        pdf_count = 0
        for source in pdf_sources:
            if Path(source).exists():
                for pdf_file in Path(source).glob("*.pdf"):
                    try:
                        dest_file = f"{self.base_dir}/combined_pdfs/{pdf_file.name}"
                        shutil.copy2(pdf_file, dest_file)
                        pdf_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to copy {pdf_file}: {e}")
        
        logger.info(f"✅ Merged {pdf_count} PDF files")
    
    def update_rag_chunks(self, text_data):
        """Update RAG chunks with new data"""
        logger.info("✂️ Updating RAG chunks...")
        
        # Load existing chunks
        existing_chunks_file = f"{self.base_dir}/rag_chunks.json"
        existing_chunks = []
        
        if Path(existing_chunks_file).exists():
            with open(existing_chunks_file, 'r', encoding='utf-8') as f:
                existing_chunks = json.load(f)
        
        # Create new chunks from text data
        from rag_chunker import RAGChunker
        chunker = RAGChunker()
        
        new_chunks = []
        for item in text_data:
            try:
                # Create a temporary file for chunking
                temp_file = Path(f"temp_{item['source_file'].replace('/', '_')}.txt")
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(item['content'])
                
                chunks = chunker.chunk_text_file(temp_file)
                new_chunks.extend(chunks)
                
                # Clean up temp file
                temp_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to chunk {item['source_file']}: {e}")
        
        # Combine existing and new chunks
        all_chunks = existing_chunks + new_chunks
        
        # Save updated chunks
        with open(existing_chunks_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Updated RAG chunks: {len(existing_chunks)} existing + {len(new_chunks)} new = {len(all_chunks)} total")
        return all_chunks
    
    def update_vector_store(self, chunks):
        """Update vector store with new chunks"""
        logger.info("🔍 Updating vector store...")
        
        from vector_store_embedder import VectorStoreEmbedder
        embedder = VectorStoreEmbedder()
        
        # Create new vector store
        vector_store_path = f"{self.base_dir}/final_vector_store"
        embedder.create_vector_store(chunks, vector_store_path)
        
        logger.info("✅ Vector store updated!")
    
    def update_neo4j_data(self, text_data):
        """Update Neo4j with new entities and relationships"""
        logger.info("🗄️ Updating Neo4j data...")
        
        from nlp_entity_extractor import EntityExtractor
        from import_to_neo4j import Neo4jImporter
        
        # Extract entities and relationships
        extractor = EntityExtractor()
        all_triples = []
        
        for item in text_data:
            try:
                triples = extractor.extract_entities_and_relationships(item['content'])
                all_triples.extend(triples)
            except Exception as e:
                logger.warning(f"Failed to extract from {item['source_file']}: {e}")
        
        # Load existing triples
        existing_triples_file = f"{self.base_dir}/triples.csv"
        existing_triples = []
        
        if Path(existing_triples_file).exists():
            import pandas as pd
            df = pd.read_csv(existing_triples_file)
            existing_triples = df.values.tolist()
        
        # Combine triples
        all_triples = existing_triples + all_triples
        
        # Save updated triples
        import pandas as pd
        df = pd.DataFrame(all_triples, columns=['subject', 'relationship', 'object'])
        df.to_csv(existing_triples_file, index=False)
        
        # Import to Neo4j
        importer = Neo4jImporter()
        importer.import_triples(all_triples)
        
        logger.info(f"✅ Neo4j updated: {len(existing_triples)} existing + {len(all_triples) - len(existing_triples)} new triples")
    
    def update_chatbot_config(self):
        """Update chatbot configuration"""
        logger.info("🤖 Updating chatbot configuration...")
        
        # Count files
        text_count = len(list(Path(f"{self.base_dir}/combined_text").glob("*.json")))
        pdf_count = len(list(Path(f"{self.base_dir}/combined_pdfs").glob("*.pdf")))
        
        # Load chunk count
        chunks_file = f"{self.base_dir}/rag_chunks.json"
        chunk_count = 0
        if Path(chunks_file).exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
                chunk_count = len(chunks)
        
        # Load triple count
        triples_file = f"{self.base_dir}/triples.csv"
        triple_count = 0
        if Path(triples_file).exists():
            import pandas as pd
            df = pd.read_csv(triples_file)
            triple_count = len(df)
        
        # Create config
        config = {
            'vector_store_path': 'final_vector_store',
            'neo4j_connection': {
                'uri': os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687'),
                'user': os.getenv('NEO4J_USER', 'neo4j'),
                'password': os.getenv('NEO4J_PASSWORD', 'Hbhosale@05')
            },
            'gemini_api_key': os.getenv('GEMINI_API_KEY', ''),
            'data_sources': {
                'text_files': text_count,
                'pdf_files': pdf_count,
                'total_chunks': chunk_count,
                'total_triples': triple_count
            },
            'last_updated': datetime.now().isoformat()
        }
        
        # Save config
        config_file = f"{self.base_dir}/chatbot_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Chatbot configuration updated!")
        logger.info(f"📊 Final stats: {text_count} text files, {pdf_count} PDFs, {chunk_count} chunks, {triple_count} triples")
    
    def run_complete_pipeline(self):
        """Run the complete data processing pipeline"""
        logger.info("🚀 Starting complete data processing pipeline...")
        
        try:
            # Step 1: Merge text data
            text_data = self.merge_text_data()
            
            # Step 2: Merge PDF data
            self.merge_pdf_data()
            
            # Step 3: Update RAG chunks
            chunks = self.update_rag_chunks(text_data)
            
            # Step 4: Update vector store
            self.update_vector_store(chunks)
            
            # Step 5: Update Neo4j data
            self.update_neo4j_data(text_data)
            
            # Step 6: Update chatbot config
            self.update_chatbot_config()
            
            logger.info("🎉 Complete pipeline finished successfully!")
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise

def main():
    """Main function to run the complete pipeline"""
    processor = DataProcessor()
    processor.run_complete_pipeline()

if __name__ == "__main__":
    main() 