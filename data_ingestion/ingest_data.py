from graph_builder import MarketDataIngestion
from knowledge_graph.graph_interface import MarketGraphDB
import os
from dotenv import load_dotenv

def add_sample_relationships(db):
    """Add sample supply chain relationships"""
    relationships = [
        ("TSMC", "AAPL", "SUPPLIES", "chips"),           # TSMC supplies to Apple
        ("QCOM", "AAPL", "SUPPLIES", "modems"),          # Qualcomm supplies to Apple
        ("AVGO", "AAPL", "SUPPLIES", "wireless"),        # Broadcom supplies to Apple
        ("SWKS", "AAPL", "SUPPLIES", "rf modules")       # Skyworks supplies to Apple
    ]
    
    print("\nAdding supply chain relationships...")
    for source, target, rel_type, product in relationships:
        try:
            db.query("""
            MATCH (s:Company {ticker: $source})
            MATCH (t:Company {ticker: $target})
            MERGE (s)-[:SUPPLIES {product: $product}]->(t)
            """, {
                "source": source,
                "target": target,
                "product": product
            })
            print(f"✅ Added relationship: {source} -> {target}")
        except Exception as e:
            print(f"❌ Failed to add relationship {source} -> {target}: {e}")

def add_sample_news(db):
    """Add sample news events"""
    news_items = [
        {
            "ticker": "AAPL",
            "date": "2023-09-12",  # iPhone 15 launch
            "title": "Apple Announces iPhone 15 Series",
            "sentiment": 0.8
        },
        {
            "ticker": "TSMC",
            "date": "2023-09-13",
            "title": "TSMC Reports Strong Demand from Apple",
            "sentiment": 0.7
        },
        {
            "ticker": "QCOM",
            "date": "2023-09-14",
            "title": "Qualcomm Supplies Key Components for iPhone 15",
            "sentiment": 0.6
        }
    ]
    
    print("\nAdding sample news items...")
    for news in news_items:
        try:
            db.query("""
            MATCH (c:Company {ticker: $ticker})
            CREATE (n:News {
                date: datetime($date),
                title: $title,
                sentiment: $sentiment
            })
            CREATE (c)-[:HAS_NEWS]->(n)
            """, news)
            print(f"✅ Added news for {news['ticker']}: {news['title']}")
        except Exception as e:
            print(f"❌ Failed to add news for {news['ticker']}: {e}")

def main():
    load_dotenv()
    
    # Initialize graph database
    db = MarketGraphDB(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    
    # Initialize ingestion
    ingestion = MarketDataIngestion(db)
    
    # Ingest sample stocks
    symbols = ['AAPL', 'TSMC', 'QCOM', 'AVGO', 'SWKS']
    print("\nIngesting stock data...")
    for symbol in symbols:
        try:
            print(f"Processing {symbol}...")
            ingestion.ingest_stock_data(symbol)
            print(f"✅ Successfully ingested {symbol}")
        except Exception as e:
            print(f"❌ Failed to ingest {symbol}: {e}")
    
    # Add relationships and news
    add_sample_relationships(db)
    add_sample_news(db)
    
    print("\nData ingestion complete!")
    db.close()

if __name__ == "__main__":
    main() 