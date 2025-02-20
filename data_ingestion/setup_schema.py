from knowledge_graph.graph_interface import MarketGraphDB
import os
from dotenv import load_dotenv

def setup_schema(db: MarketGraphDB):
    """Setup Neo4j database schema and constraints"""
    
    # Create constraints
    constraints = [
        "CREATE CONSTRAINT company_ticker IF NOT EXISTS FOR (c:Company) REQUIRE c.ticker IS UNIQUE",
        "CREATE CONSTRAINT news_id IF NOT EXISTS FOR (n:News) REQUIRE n.id IS UNIQUE",
        "CREATE INDEX price_date IF NOT EXISTS FOR (p:PricePoint) ON (p.date)",
    ]
    
    # Create relationship indices
    indices = [
        "CREATE INDEX supply_chain IF NOT EXISTS FOR ()-[r:SUPPLIES]->() ON (r.strength)",
        "CREATE INDEX has_news IF NOT EXISTS FOR ()-[r:HAS_NEWS]->() ON (r.date)"
    ]
    
    for query in constraints + indices:
        try:
            db.query(query)
        except Exception as e:
            print(f"Error creating schema: {e}")

def main():
    load_dotenv()
    
    db = MarketGraphDB(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    
    setup_schema(db)
    print("Schema setup complete!")

if __name__ == "__main__":
    main() 