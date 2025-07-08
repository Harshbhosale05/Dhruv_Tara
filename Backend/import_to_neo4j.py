import pandas as pd
from neo4j import GraphDatabase
import logging
from pathlib import Path
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MOSDACNeo4jImporter:
    def __init__(self, uri="neo4j://127.0.0.1:7687", user="neo4j", password="password"):
        """
        Initialize Neo4j connection for MOSDAC data
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info(f"🔗 Connected to Neo4j at {uri}")
    
    def close(self):
        """
        Close the database connection
        """
        self.driver.close()
    
    def test_connection(self):
        """
        Test the Neo4j connection
        """
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    logger.info("✅ Neo4j connection successful!")
                    return True
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {str(e)}")
            return False
    
    def clear_database(self):
        """
        Clear all nodes and relationships from the database
        """
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("🧹 Cleared all nodes and relationships from database")
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
    
    def create_constraints(self):
        """
        Create constraints for better performance
        """
        try:
            with self.driver.session() as session:
                # Create constraints for unique entities
                session.run("CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
                logger.info("✅ Created constraint for Entity.name")
        except Exception as e:
            logger.warning(f"Constraint creation failed (might already exist): {e}")
    
    def import_triples(self, csv_file_path):
        """
        Import triples from CSV file into Neo4j
        """
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            logger.info(f"📊 Loaded {len(df)} triples from {csv_file_path}")
            
            # Clean and prepare data
            df = df.dropna()  # Remove rows with missing values
            logger.info(f"📋 Processing {len(df)} valid triples")
            
            imported_count = 0
            skipped_count = 0
            
            with self.driver.session() as session:
                # Import entities and relationships
                for index, row in df.iterrows():
                    if index % 1000 == 0:
                        logger.info(f"⏳ Processing triple {index}/{len(df)}")
                    
                    subject = str(row['subject']).strip()
                    relation = str(row['relation']).strip()
                    object_text = str(row['object']).strip()
                    source_file = str(row.get('source_file', 'unknown')).strip()
                    
                    # Skip if any field is empty or too short
                    if len(subject) < 2 or len(relation) < 2 or len(object_text) < 2:
                        skipped_count += 1
                        continue
                    
                    try:
                        # Create Cypher query to merge nodes and create relationship
                        cypher_query = """
                        MERGE (s:Entity {name: $subject})
                        MERGE (o:Entity {name: $object})
                        MERGE (s)-[r:`%s`]->(o)
                        SET s.source_file = $source_file
                        SET o.source_file = $source_file
                        """ % relation
                        
                        session.run(cypher_query, 
                                  subject=subject, 
                                  object=object_text, 
                                  source_file=source_file)
                        imported_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Skipped triple due to error: {e}")
                        skipped_count += 1
                        continue
                
                logger.info(f"✅ Successfully imported {imported_count} triples into Neo4j")
                logger.info(f"⚠️ Skipped {skipped_count} triples")
                
        except Exception as e:
            logger.error(f"❌ Error importing triples: {str(e)}")
            raise
    
    def get_statistics(self):
        """
        Get database statistics
        """
        try:
            with self.driver.session() as session:
                # Count nodes
                node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                
                # Count relationships
                rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                
                # Count unique entity types
                entity_types = session.run("MATCH (n:Entity) RETURN DISTINCT labels(n) as labels").data()
                
                # Count relationship types
                rel_types = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) as type").data()
                
                logger.info("📊 Database Statistics:")
                logger.info(f"  📈 Total nodes: {node_count}")
                logger.info(f"  🔗 Total relationships: {rel_count}")
                logger.info(f"  🏷️ Entity types: {len(entity_types)}")
                logger.info(f"  🔄 Relationship types: {len(rel_types)}")
                
                return {
                    'nodes': node_count,
                    'relationships': rel_count,
                    'entity_types': len(entity_types),
                    'relationship_types': len(rel_types)
                }
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return None
    
    def run_sample_queries(self):
        """
        Run some sample queries to demonstrate the knowledge graph
        """
        try:
            with self.driver.session() as session:
                logger.info("🔍 Sample Queries Results:")
                
                # Query 1: Find all satellites
                satellites = session.run("""
                    MATCH (n:Entity) 
                    WHERE n.name CONTAINS 'INSAT' OR n.name CONTAINS 'OCEANSAT' OR n.name CONTAINS 'SCATSAT'
                    RETURN n.name as satellite
                    LIMIT 10
                """).data()
                
                logger.info("🛰️ Satellites found:")
                for sat in satellites:
                    logger.info(f"  - {sat['satellite']}")
                
                # Query 2: Find entities that provide products
                providers = session.run("""
                    MATCH (s:Entity)-[r:PROVIDES]->(o:Entity)
                    RETURN s.name as subject, o.name as object
                    LIMIT 5
                """).data()
                
                logger.info("📦 Entities providing products:")
                for prov in providers:
                    logger.info(f"  - {prov['subject']} provides {prov['object']}")
                
                # Query 3: Find MOSDAC-related entities
                mosdac_entities = session.run("""
                    MATCH (n:Entity)
                    WHERE n.name CONTAINS 'MOSDAC' OR n.name CONTAINS 'ISRO'
                    RETURN n.name as entity
                    LIMIT 5
                """).data()
                
                logger.info("🏛️ MOSDAC/ISRO related entities:")
                for ent in mosdac_entities:
                    logger.info(f"  - {ent['entity']}")
                    
        except Exception as e:
            logger.error(f"Error running sample queries: {str(e)}")

def main():
    """
    Main function to import triples into Neo4j
    """
    # Neo4j connection parameters for your setup
    NEO4J_URI = "neo4j://127.0.0.1:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "Hbhosale@05"  # Your actual password
    
    # CSV file path
    csv_file = Path("mosdac_data/triples.csv")
    
    if not csv_file.exists():
        logger.error(f"❌ CSV file not found: {csv_file}")
        return
    
    try:
        # Initialize importer
        importer = MOSDACNeo4jImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        
        # Test connection first
        if not importer.test_connection():
            logger.error("❌ Cannot proceed without Neo4j connection")
            return
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        logger.info("🧹 Clearing existing data...")
        importer.clear_database()
        
        # Create constraints
        logger.info("🔧 Creating constraints...")
        importer.create_constraints()
        
        # Import triples
        logger.info("📥 Importing triples...")
        importer.import_triples(csv_file)
        
        # Get statistics
        logger.info("📊 Getting statistics...")
        stats = importer.get_statistics()
        
        # Run sample queries
        logger.info("🔍 Running sample queries...")
        importer.run_sample_queries()
        
        logger.info("🎉 Neo4j import completed successfully!")
        logger.info("💡 You can now query your knowledge graph using Cypher queries in Neo4j Browser.")
        
    except Exception as e:
        logger.error(f"❌ Import failed: {str(e)}")
        raise
    finally:
        if 'importer' in locals():
            importer.close()

if __name__ == "__main__":
    main() 