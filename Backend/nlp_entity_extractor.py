import spacy
import pandas as pd
import os
from pathlib import Path
import logging
from typing import List, Tuple, Dict
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EntityExtractor:
    def __init__(self):
        """Initialize spaCy model"""
        try:
            # Load English language model
            self.nlp = spacy.load("en_core_web_md")
            logger.info("Loaded spaCy model: en_core_web_md")
        except OSError:
            logger.error("spaCy model not found. Please install with: python -m spacy download en_core_web_md")
            raise
    
    def extract_entities_from_text(self, text: str) -> List[Dict]:
        """
        Extract named entities from text using spaCy
        """
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        return entities
    
    def extract_relationships(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Extract subject-verb-object relationships from text using robust regex with named groups.
        """
        relationships = []
        # Define relationship patterns with named groups
        relationship_patterns = [
            # Subject + Verb + Object
            (r'(?P<subject>\b[A-Z][A-Za-z0-9\- ]{2,}\b)\s+(provides|offers|monitors|measures|detects|generates|produces)\s+(?P<object>\b[A-Z][A-Za-z0-9\- ]{2,}\b)', 'PROVIDES'),
            # Subject is/are a/an Object
            (r'(?P<subject>\b[A-Z][A-Za-z0-9\- ]{2,}\b)\s+(is|are)\s+(a|an)\s+(?P<object>\b[A-Z][A-Za-z0-9\- ]{2,}\b)', 'IS_A'),
            # Subject launched/deployed/operated Object
            (r'(?P<subject>\b[A-Z][A-Za-z0-9\- ]{2,}\b)\s+(launched|deployed|operated)\s+(?P<object>\b[A-Z][A-Za-z0-9\- ]{2,}\b)', 'LAUNCHED'),
            # Subject satellite/mission/instrument Object
            (r'(?P<subject>\b[A-Z][A-Za-z0-9\- ]{2,}\b)\s+(satellite|mission|instrument)\s+(?P<object>\b[A-Z][A-Za-z0-9\- ]{2,}\b)', 'IS_SATELLITE'),
            # Subject data/product/information Object
            (r'(?P<subject>\b[A-Z][A-Za-z0-9\- ]{2,}\b)\s+(data|product|information)\s+(?P<object>\b[A-Z][A-Za-z0-9\- ]{2,}\b)', 'PRODUCES_DATA'),
        ]
        
        for pattern, relation_type in relationship_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                subject = match.groupdict().get('subject', '').strip()
                object_text = match.groupdict().get('object', '').strip()
                if subject and object_text and len(subject) > 2 and len(object_text) > 2:
                    relationships.append((subject, relation_type, object_text))
        return relationships
    
    def extract_mosdac_specific_entities(self, text: str) -> List[Dict]:
        """
        Extract MOSDAC-specific entities like satellite names, products, etc.
        """
        # Define MOSDAC-specific entity patterns
        satellite_patterns = [
            r'INSAT-3D[RS]?',
            r'OCEANSAT-[23]',
            r'SCATSAT-1',
            r'KALPANA-1',
            r'MeghaTropiques',
            r'SARAL-AltiKa',
            r'INSAT-3A',
            r'INSAT-3DS'
        ]
        
        product_patterns = [
            r'Sea Surface Temperature',
            r'Rainfall Product',
            r'Weather Forecast',
            r'Ocean Current',
            r'Soil Moisture',
            r'Cloud Properties',
            r'Cyclone Detection',
            r'Lightning Forecast',
            r'Monsoon Prediction',
            r'Wave Height',
            r'Air Quality',
            r'Coastal Product'
        ]
        
        entities = []
        
        # Extract satellites
        for pattern in satellite_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'text': match.group(),
                    'label': 'SATELLITE',
                    'start': match.start(),
                    'end': match.end()
                })
        
        # Extract products
        for pattern in product_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'text': match.group(),
                    'label': 'PRODUCT',
                    'start': match.start(),
                    'end': match.end()
                })
        
        return entities
    
    def process_text_file(self, file_path: Path) -> Tuple[List[Dict], List[Tuple]]:
        """
        Process a single text file and extract entities and relationships
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Extract general entities
            general_entities = self.extract_entities_from_text(text)
            
            # Extract MOSDAC-specific entities
            mosdac_entities = self.extract_mosdac_specific_entities(text)
            
            # Combine entities
            all_entities = general_entities + mosdac_entities
            
            # Extract relationships
            relationships = self.extract_relationships(text)
            
            logger.info(f"Extracted {len(all_entities)} entities and {len(relationships)} relationships from {file_path.name}")
            
            return all_entities, relationships
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return [], []

def main():
    """
    Main function to process all text files and create triples CSV
    """
    # Initialize extractor
    extractor = EntityExtractor()
    
    # Define paths
    text_folder = Path("mosdac_data/text")
    pdf_text_folder = Path("mosdac_data/text_from_pdfs")
    output_file = Path("mosdac_data/triples.csv")
    
    # Get all text files
    text_files = list(text_folder.glob("*.txt")) + list(pdf_text_folder.glob("*.txt"))
    
    if not text_files:
        logger.warning("No text files found")
        return
    
    logger.info(f"Found {len(text_files)} text files to process")
    
    all_entities = []
    all_relationships = []
    
    # Process each text file
    for text_file in text_files:
        logger.info(f"Processing: {text_file.name}")
        
        entities, relationships = extractor.process_text_file(text_file)
        
        # Add source file information
        for entity in entities:
            entity['source_file'] = text_file.name
        
        all_entities.extend(entities)
        all_relationships.extend(relationships)
    
    # Create triples DataFrame
    triples_data = []
    
    # Add entity triples
    for entity in all_entities:
        triples_data.append({
            'subject': entity['text'],
            'relation': f"IS_{entity['label']}",
            'object': entity['label'],
            'source_file': entity['source_file']
        })
    
    # Add relationship triples
    for subject, relation, object_text in all_relationships:
        triples_data.append({
            'subject': subject,
            'relation': relation,
            'object': object_text,
            'source_file': 'extracted_relationships'
        })
    
    # Create DataFrame and save to CSV
    if triples_data:
        df = pd.DataFrame(triples_data)
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(triples_data)} triples to {output_file}")
        
        # Print some statistics
        logger.info(f"Total entities extracted: {len(all_entities)}")
        logger.info(f"Total relationships extracted: {len(all_relationships)}")
        
        # Show some examples
        logger.info("Sample triples:")
        for i, triple in enumerate(triples_data[:10]):
            logger.info(f"  {triple['subject']} -- {triple['relation']} --> {triple['object']}")
    else:
        logger.warning("No triples extracted")

if __name__ == "__main__":
    main() 