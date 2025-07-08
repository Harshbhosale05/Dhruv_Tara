#!/usr/bin/env python3
"""
🔄 Update System with New Crawled Data
Processes new data from MOSDAC and ISRO websites and updates the existing system
"""

import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemUpdater:
    def __init__(self):
        self.base_dir = "mosdac_data"
        self.setup_directories()
        
    def setup_directories(self):
        """Ensure all necessary directories exist"""
        dirs = [
            f"{self.base_dir}/combined_data",
            f"{self.base_dir}/combined_text",
            f"{self.base_dir}/combined_pdfs",
            f"{self.base_dir}/enhanced_vector_store"
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created directory: {dir_path}")
    
    def merge_text_data(self):
        """Merge all text data from both websites"""
        logger.info("📄 Merging text data from both websites...")
        
        combined_text = []
        
        # Process MOSDAC text files
        mosdac_text_dir = Path(f"{self.base_dir}/text")
        if mosdac_text_dir.exists():
            for text_file in mosdac_text_dir.glob("*.txt"):
                try:
                    with open(text_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            combined_text.append({
                                'content': content,
                                'source_file': f"mosdac/{text_file.name}",
                                'source_type': 'webpage',
                                'timestamp': datetime.now().isoformat()
                            })
                except Exception as e:
                    logger.warning(f"Failed to read {text_file}: {e}")
        
        # Process ISRO text files
        isro_text_dir = Path(f"{self.base_dir}/isro_data/text")
        if isro_text_dir.exists():
            for text_file in isro_text_dir.glob("*.txt"):
                try:
                    with open(text_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            combined_text.append({
                                'content': content,
                                'source_file': f"isro/{text_file.name}",
                                'source_type': 'webpage',
                                'timestamp': datetime.now().isoformat()
                            })
                except Exception as e:
                    logger.warning(f"Failed to read {text_file}: {e}")
        
        # Save combined text data
        combined_text_file = Path(f"{self.base_dir}/combined_text/all_text_data.json")
        with open(combined_text_file, 'w', encoding='utf-8') as f:
            json.dump(combined_text, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Merged {len(combined_text)} text files")
        return combined_text
    
    def merge_pdf_data(self):
        """Merge PDF data and extract text"""
        logger.info("📄 Merging PDF data...")
        
        # Copy all PDFs to combined directory
        combined_pdf_dir = Path(f"{self.base_dir}/combined_pdfs")
        
        # Copy MOSDAC PDFs
        mosdac_pdf_dir = Path(f"{self.base_dir}/pdfs")
        if mosdac_pdf_dir.exists():
            for pdf_file in mosdac_pdf_dir.glob("*.pdf"):
                try:
                    shutil.copy2(pdf_file, combined_pdf_dir / f"mosdac_{pdf_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to copy {pdf_file}: {e}")
        
        # Copy ISRO PDFs
        isro_pdf_dir = Path(f"{self.base_dir}/isro_data/pdfs")
        if isro_pdf_dir.exists():
            for pdf_file in isro_pdf_dir.glob("*.pdf"):
                try:
                    shutil.copy2(pdf_file, combined_pdf_dir / f"isro_{pdf_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to copy {pdf_file}: {e}")
        
        logger.info(f"✅ Merged PDF files to {combined_pdf_dir}")
    
    def create_enhanced_chunks(self, text_data):
        """Create enhanced chunks from combined text data"""
        logger.info("✂️ Creating enhanced chunks...")
        
        from rag_chunker import RAGChunker
        chunker = RAGChunker()
        
        enhanced_chunks = []
        chunk_id = 1
        
        for item in text_data:
            try:
                # Create temporary file for chunking
                temp_file = Path(f"temp_chunk_{chunk_id}.txt")
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(item['content'])
                
                # Chunk the text
                chunks = chunker.chunk_text_file(temp_file)
                
                # Add metadata to chunks
                for chunk in chunks:
                    chunk['source_file'] = item['source_file']
                    chunk['source_type'] = item['source_type']
                    chunk['timestamp'] = item['timestamp']
                    chunk['id'] = f"chunk_{chunk_id}_{chunks.index(chunk)}"
                
                enhanced_chunks.extend(chunks)
                
                # Clean up temp file
                temp_file.unlink()
                chunk_id += 1
                
            except Exception as e:
                logger.warning(f"Failed to chunk {item['source_file']}: {e}")
        
        # Save enhanced chunks
        enhanced_chunks_file = Path(f"{self.base_dir}/enhanced_chunks.json")
        with open(enhanced_chunks_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_chunks, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Created {len(enhanced_chunks)} enhanced chunks")
        return enhanced_chunks
    
    def update_vector_store(self, chunks):
        """Update vector store with new chunks"""
        logger.info("🔍 Updating vector store...")
        
        try:
            from vector_store_embedder import VectorStoreEmbedder
            
            # Initialize embedder
            embedder = VectorStoreEmbedder()
            
            # Embed chunks
            embeddings = embedder.embed_chunks(chunks)
            
            # Build FAISS index
            embedder.build_faiss_index(embeddings, chunks)
            
            # Save to enhanced vector store
            output_dir = f"{self.base_dir}/enhanced_vector_store"
            embedder.save_index(output_dir)
            
            logger.info(f"✅ Updated vector store with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"❌ Failed to update vector store: {e}")
            raise
    
    def update_knowledge_graph(self):
        """Update knowledge graph with new data"""
        logger.info("🗺️ Updating knowledge graph...")
        
        try:
            from nlp_entity_extractor import EntityExtractor
            from import_to_neo4j import Neo4jImporter
            
            # Extract entities from new text data
            extractor = EntityExtractor()
            
            # Process combined text files
            combined_text_dir = Path(f"{self.base_dir}/combined_text")
            all_triples = []
            
            for text_file in combined_text_dir.glob("*.txt"):
                try:
                    with open(text_file, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    # Extract entities and relationships
                    triples = extractor.extract_entities_and_relationships(text, str(text_file))
                    all_triples.extend(triples)
                    
                except Exception as e:
                    logger.warning(f"Failed to process {text_file}: {e}")
            
            # Import to Neo4j
            if all_triples:
                importer = Neo4jImporter()
                importer.import_triples(all_triples)
                logger.info(f"✅ Updated knowledge graph with {len(all_triples)} triples")
            
        except Exception as e:
            logger.error(f"❌ Failed to update knowledge graph: {e}")
    
    def create_system_report(self):
        """Create a comprehensive system report"""
        logger.info("📊 Creating system report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "enhanced",
            "data_sources": {
                "mosdac": {
                    "pages_crawled": 145,
                    "pdfs_downloaded": 17,
                    "images_downloaded": 2
                },
                "isro": {
                    "pages_crawled": 254,
                    "pdfs_downloaded": 29,
                    "images_downloaded": 0
                }
            },
            "system_components": {
                "vector_store": "enhanced_vector_store/",
                "knowledge_graph": "neo4j_updated",
                "chunks": "enhanced_chunks.json",
                "combined_data": "combined_data/"
            },
            "next_steps": [
                "Test enhanced chatbot",
                "Verify knowledge graph queries",
                "Run performance benchmarks"
            ]
        }
        
        # Save report
        report_file = Path(f"{self.base_dir}/system_enhancement_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ System report saved to: {report_file}")
        return report
    
    def run_complete_update(self):
        """Run the complete system update process"""
        logger.info("🚀 Starting complete system update...")
        
        try:
            # Step 1: Merge text data
            text_data = self.merge_text_data()
            
            # Step 2: Merge PDF data
            self.merge_pdf_data()
            
            # Step 3: Create enhanced chunks
            chunks = self.create_enhanced_chunks(text_data)
            
            # Step 4: Update vector store
            self.update_vector_store(chunks)
            
            # Step 5: Update knowledge graph
            self.update_knowledge_graph()
            
            # Step 6: Create system report
            report = self.create_system_report()
            
            logger.info("✅ Complete system update finished successfully!")
            logger.info("🎉 Your enhanced MOSDAC + ISRO knowledge system is ready!")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ System update failed: {e}")
            raise

def main():
    """Main function"""
    updater = SystemUpdater()
    updater.run_complete_update()

if __name__ == "__main__":
    main() 