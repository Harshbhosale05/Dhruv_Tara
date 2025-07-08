#!/usr/bin/env python3
"""
🔄 Comprehensive Data Processing Pipeline
Handles the complete workflow from crawled data to final chatbot
"""

import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
import re

# Import existing modules
from rag_chunker import TextChunker
from vector_store_embedder import VectorStoreEmbedder
from nlp_entity_extractor import EntityExtractor
from import_to_neo4j import Neo4jImporter

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

class ComprehensiveDataProcessor:
    def __init__(self):
        self.base_dir = "mosdac_data"
        self.processed_dir = "final_processed_data"
        self.setup_directories()
        
    def setup_directories(self):
        """Create final processing directories"""
        dirs = [
            self.processed_dir,
            f"{self.processed_dir}/combined_text",
            f"{self.processed_dir}/combined_pdfs",
            f"{self.processed_dir}/vector_store",
            f"{self.processed_dir}/knowledge_graph",
            f"{self.processed_dir}/chatbot_data"
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    def merge_all_data(self):
        """Merge all crawled data into a unified structure"""
        logger.info("🔄 Starting data merge process...")
        
        # Merge text files
        self.merge_text_files()
        
        # Merge PDFs
        self.merge_pdfs()
        
        # Merge metadata
        self.merge_metadata()
        
        # Merge structured data
        self.merge_structured_data()
        
        logger.info("✅ Data merge completed!")
    
    def merge_text_files(self):
        """Merge all text files from different sources"""
        logger.info("📝 Merging text files...")
        
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
                            combined_text.append({
                                'source_file': str(file_path),
                                'content': content,
                                'type': 'text'
                            })
                    except Exception as e:
                        logger.warning(f"Failed to read {file_path}: {e}")
        
        # Save combined text
        output_file = f"{self.processed_dir}/combined_text/all_text_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_text, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Merged {len(combined_text)} text files")
    
    def merge_pdfs(self):
        """Merge all PDF files"""
        logger.info("📄 Merging PDF files...")
        
        pdf_sources = [
            f"{self.base_dir}/pdfs"
        ]
        
        for source in pdf_sources:
            if Path(source).exists():
                for pdf_file in Path(source).glob("*.pdf"):
                    try:
                        dest_file = f"{self.processed_dir}/combined_pdfs/{pdf_file.name}"
                        shutil.copy2(pdf_file, dest_file)
                    except Exception as e:
                        logger.warning(f"Failed to copy {pdf_file}: {e}")
        
        logger.info("✅ PDF merge completed!")
    
    def merge_metadata(self):
        """Merge all metadata files"""
        logger.info("🏷️ Merging metadata...")
        
        metadata_sources = [
            f"{self.base_dir}/metadata"
        ]
        
        all_metadata = []
        
        for source in metadata_sources:
            if Path(source).exists():
                for meta_file in Path(source).glob("*.json"):
                    try:
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            all_metadata.extend(metadata)
                    except Exception as e:
                        logger.warning(f"Failed to read {meta_file}: {e}")
        
        # Save combined metadata
        output_file = f"{self.processed_dir}/combined_metadata.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Merged {len(all_metadata)} metadata entries")
    
    def merge_structured_data(self):
        """Merge structured data (tables, links, etc.)"""
        logger.info("📊 Merging structured data...")
        
        structured_sources = [
            f"{self.base_dir}/tables",
            f"{self.base_dir}/links",
            f"{self.base_dir}/structured_data"
        ]
        
        all_structured = {
            'tables': [],
            'links': [],
            'entities': []
        }
        
        for source in structured_sources:
            if Path(source).exists():
                for data_file in Path(source).glob("*.json"):
                    try:
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if 'tables' in str(data_file):
                                all_structured['tables'].extend(data)
                            elif 'links' in str(data_file):
                                all_structured['links'].extend(data)
                            else:
                                all_structured['entities'].extend(data)
                    except Exception as e:
                        logger.warning(f"Failed to read {data_file}: {e}")
        
        # Save combined structured data
        output_file = f"{self.processed_dir}/combined_structured_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_structured, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Structured data merge completed!")
    
    def process_text_chunking(self):
        """Process text chunking for RAG"""
        logger.info("✂️ Starting text chunking process...")
        
        # Load combined text data
        text_file = f"{self.processed_dir}/combined_text/all_text_data.json"
        with open(text_file, 'r', encoding='utf-8') as f:
            text_data = json.load(f)
        
        # Initialize chunker
        chunker = TextChunker()
        
        # Process all text content
        all_chunks = []
        for item in text_data:
            try:
                chunks = chunker.chunk_text(item['content'], item['source_file'])
                all_chunks.extend(chunks)
            except Exception as e:
                logger.warning(f"Failed to chunk {item['source_file']}: {e}")
        
        # Save chunks
        chunks_file = f"{self.processed_dir}/combined_text/rag_chunks.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Created {len(all_chunks)} text chunks")
        return all_chunks
    
    def create_vector_store(self, chunks):
        """Create vector store from chunks"""
        logger.info("🔍 Creating vector store...")
        
        # Initialize embedder
        embedder = VectorStoreEmbedder()
        
        # Create vector store
        vector_store_path = f"{self.processed_dir}/vector_store"
        embedder.create_vector_store(chunks, vector_store_path)
        
        logger.info("✅ Vector store created!")
    
    def extract_entities_and_relationships(self):
        """Extract entities and relationships for knowledge graph"""
        logger.info("🏷️ Extracting entities and relationships...")
        
        # Load combined text data
        text_file = f"{self.processed_dir}/combined_text/all_text_data.json"
        with open(text_file, 'r', encoding='utf-8') as f:
            text_data = json.load(f)
        
        # Initialize entity extractor
        extractor = EntityExtractor()
        
        # Process all text content
        all_triples = []
        for item in text_data:
            try:
                triples = extractor.extract_entities_and_relationships(item['content'])
                all_triples.extend(triples)
            except Exception as e:
                logger.warning(f"Failed to extract from {item['source_file']}: {e}")
        
        # Save triples
        triples_file = f"{self.processed_dir}/knowledge_graph/triples.csv"
        df = pd.DataFrame(all_triples, columns=['subject', 'relationship', 'object'])
        df.to_csv(triples_file, index=False)
        
        logger.info(f"✅ Extracted {len(all_triples)} triples")
        return all_triples
    
    def import_to_neo4j(self, triples):
        """Import triples to Neo4j"""
        logger.info("🗄️ Importing to Neo4j...")
        
        # Initialize Neo4j importer
        importer = Neo4jImporter()
        
        # Import triples
        importer.import_triples(triples)
        
        logger.info("✅ Neo4j import completed!")
    
    def create_final_chatbot_data(self):
        """Create final chatbot configuration"""
        logger.info("🤖 Creating final chatbot data...")
        
        # Copy necessary files to chatbot data directory
        chatbot_data_dir = f"{self.processed_dir}/chatbot_data"
        
        # Copy vector store
        vector_store_src = f"{self.processed_dir}/vector_store"
        vector_store_dest = f"{chatbot_data_dir}/vector_store"
        if Path(vector_store_src).exists():
            shutil.copytree(vector_store_src, vector_store_dest, dirs_exist_ok=True)
        
        # Create chatbot config
        config = {
            'vector_store_path': 'vector_store',
            'neo4j_connection': {
                'uri': 'neo4j://127.0.0.1:7687',
                'user': 'neo4j',
                'password': 'Hbhosale@05'
            },
            'gemini_api_key': 'AIzaSyDKrNSwJGKbZJ9NbQtpj9b-QHUtWlpimQU',
            'data_sources': {
                'text_files': len(list(Path(f"{self.processed_dir}/combined_text").glob("*.json"))),
                'pdf_files': len(list(Path(f"{self.processed_dir}/combined_pdfs").glob("*.pdf"))),
                'total_chunks': 0,
                'total_triples': 0
            },
            'last_updated': datetime.now().isoformat()
        }
        
        # Update counts
        chunks_file = f"{self.processed_dir}/combined_text/rag_chunks.json"
        if Path(chunks_file).exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
                config['data_sources']['total_chunks'] = len(chunks)
        
        triples_file = f"{self.processed_dir}/knowledge_graph/triples.csv"
        if Path(triples_file).exists():
            df = pd.read_csv(triples_file)
            config['data_sources']['total_triples'] = len(df)
        
        # Save config
        config_file = f"{chatbot_data_dir}/chatbot_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Final chatbot data created!")
    
    def run_complete_pipeline(self):
        """Run the complete data processing pipeline"""
        logger.info("🚀 Starting complete data processing pipeline...")
        
        try:
            # Step 1: Merge all data
            self.merge_all_data()
            
            # Step 2: Process text chunking
            chunks = self.process_text_chunking()
            
            # Step 3: Create vector store
            self.create_vector_store(chunks)
            
            # Step 4: Extract entities and relationships
            triples = self.extract_entities_and_relationships()
            
            # Step 5: Import to Neo4j
            self.import_to_neo4j(triples)
            
            # Step 6: Create final chatbot data
            self.create_final_chatbot_data()
            
            logger.info("🎉 Complete pipeline finished successfully!")
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise

def main():
    """Main function to run the complete pipeline"""
    processor = ComprehensiveDataProcessor()
    processor.run_complete_pipeline()

if __name__ == "__main__":
    main() 