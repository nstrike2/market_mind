from neo4j import GraphDatabase
from newsapi import NewsApiClient
from sec_api import QueryApi
import os
from dotenv import load_dotenv

def test_connections():
    load_dotenv()
    
    print("\n=== Testing API Connections ===\n")

    # 1. Test Neo4j
    print("Testing Neo4j connection...")
    try:
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )
        driver.verify_connectivity()
        print("✅ Neo4j connection successful!")
    except Exception as e:
        print(f"❌ Neo4j connection failed: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.close()

    # 2. Test NewsAPI
    print("\nTesting NewsAPI connection...")
    try:
        news_api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
        # Make a simple test request
        news_api.get_everything(q="AAPL", page_size=1)
        print("✅ NewsAPI connection successful!")
    except Exception as e:
        print(f"❌ NewsAPI connection failed: {str(e)}")

    # 3. Test SEC API
    print("\nTesting SEC API connection...")
    try:
        sec_api = QueryApi(api_key=os.getenv("SEC_API_KEY"))
        # Make a simple test request
        sec_api.get_filings({
            "query": {"query_string": {"query": "ticker:AAPL"}},
            "from": "0",
            "size": "1"
        })
        print("✅ SEC API connection successful!")
    except Exception as e:
        print(f"❌ SEC API connection failed: {str(e)}")

if __name__ == "__main__":
    test_connections() 