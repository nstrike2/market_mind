from knowledge_graph.query_tools import MarketQueryTool
from knowledge_graph.graph_interface import MarketGraphDB
import os
from dotenv import load_dotenv
import time

def print_section(title):
    """Helper to print formatted section headers"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}\n")

def demo_features():
    load_dotenv()
    
    # Initialize our query tool
    tool = MarketQueryTool(db_config={
        "uri": os.getenv("NEO4J_URI"),
        "user": os.getenv("NEO4J_USER"),
        "password": os.getenv("NEO4J_PASSWORD")
    })
    
    # 1. Supply Chain Analysis
    print_section("1. Supply Chain Relationship Analysis")
    print("Finding Apple's semiconductor suppliers and their relationships...")
    # Use the graph_db directly for clearer results
    suppliers = tool.graph_db.query("""
    MATCH (supplier:Company)-[:SUPPLIES]->(c:Company {ticker: 'AAPL'})
    RETURN supplier.ticker as supplier, supplier.name as name
    """)
    print("\nSupply Chain Results:")
    for s in suppliers:
        print(f"- {s['name']} ({s['supplier']}) supplies to Apple")
    time.sleep(1)
    
    # 2. Price Correlation
    print_section("2. Price Correlation Analysis")
    print("Analyzing correlation between Apple and Qualcomm...")
    corr = tool._analyze_correlation("AAPL", "QCOM", "1y")
    print("\nCorrelation Results:")
    for c in corr:
        print(f"- Correlation coefficient: {c['correlation_coefficient']:.2f}")
        print(f"- Period: {c['period']}")
        print(f"- Data points: {c['data_points']}")
    time.sleep(1)
    
    # 3. News Sentiment
    print_section("3. News Sentiment Integration")
    print("Analyzing news sentiment around iPhone 15 launch...")
    news = tool.graph_db.query("""
    MATCH (c:Company {ticker: 'AAPL'})-[:HAS_NEWS]->(n:News)
    WHERE date(n.date) >= date('2023-09-01')
    RETURN n.title as title, n.sentiment as sentiment, n.date as date
    ORDER BY n.date
    """)
    print("\nNews Sentiment Results:")
    for n in news:
        print(f"- [{n['date']}] {n['title']} (Sentiment: {n['sentiment']:.2f})")
    time.sleep(1)
    
    # 4. Event Impact
    print_section("4. Event Impact Analysis")
    print("Analyzing impact of iPhone 15 launch (Sept 12, 2023)...")
    
    # Debug: Check if we have price data
    prices = tool.graph_db.query("""
    MATCH (c:Company {ticker: 'AAPL'})-[:HAS_PRICE]->(p:PricePoint)
    RETURN p.date as date, p.close as price, p.volume as volume
    ORDER BY p.date DESC
    LIMIT 5
    """)
    print("\nDebug - Recent Price Data:")
    for p in prices:
        print(f"Date: {p['date']}, Price: ${p['price']}, Volume: {p['volume']}")
    
    impact = tool._analyze_event_impact("AAPL", "2023-09-12", 5)
    print("\nEvent Impact Results:")
    if impact:
        for i in impact:
            print(f"Pre-event price change: {i['pre_event_change']:.2f}%")
            print(f"Post-event price change: {i['post_event_change']:.2f}%")
            print(f"Volume change: {i['volume_change']:,.0f}")
    else:
        print("No impact data found - check if we have price data for this date range")
    
    # Also show impact on key supplier
    print("\nAnalyzing impact on key supplier (Qualcomm)...")
    
    # Debug: Check Qualcomm price data
    prices = tool.graph_db.query("""
    MATCH (c:Company {ticker: 'QCOM'})-[:HAS_PRICE]->(p:PricePoint)
    RETURN p.date as date, p.close as price, p.volume as volume
    ORDER BY p.date DESC
    LIMIT 5
    """)
    print("\nDebug - Recent QCOM Price Data:")
    for p in prices:
        print(f"Date: {p['date']}, Price: ${p['price']}, Volume: {p['volume']}")
    
    impact = tool._analyze_event_impact("QCOM", "2023-09-12", 5)
    print("\nSupplier Impact Results:")
    if impact:
        for i in impact:
            print(f"Pre-event price change: {i['pre_event_change']:.2f}%")
            print(f"Post-event price change: {i['post_event_change']:.2f}%")
            print(f"Volume change: {i['volume_change']:,.0f}")
    else:
        print("No impact data found - check if we have price data for this date range")

def main():
    try:
        print("\nStarting Market Intelligence System Feature Demo...")
        print("Connecting to Neo4j database and initializing tools...")
        demo_features()
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        print("Please ensure:")
        print("1. Neo4j database is running")
        print("2. All environment variables are set")
        print("3. Sample data has been ingested (run ingest_data.py first)")

if __name__ == "__main__":
    main() 