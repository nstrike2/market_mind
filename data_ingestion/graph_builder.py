import yfinance as yf
from sec_api import QueryApi
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from typing import Dict, List
import os
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from knowledge_graph.graph_interface import MarketGraphDB

class MarketDataIngestion:
    def __init__(self, graph_db: MarketGraphDB):
        self.graph_db = graph_db
        self.news_api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
        self.sec_api = QueryApi(api_key=os.getenv("SEC_API_KEY"))
        self.retry_attempts = 3
        self.retry_delay = 5  # seconds

    def ingest_stock_data(self, symbol: str, period: str = "1y"):
        """Ingest historical stock data with error handling and retries"""
        for attempt in range(self.retry_attempts):
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(
                    start="2023-08-01",  # Start before iPhone event
                    end="2023-10-01"     # End after iPhone event
                )
                if hist.empty:
                    raise ValueError(f"No data returned for {symbol}")
                    
                # Create company node if doesn't exist
                company_info = stock.info
                self.graph_db.query("""
                MERGE (c:Company {ticker: $ticker})
                SET c.name = $name, c.sector = $sector
                """, {"ticker": symbol, "name": company_info.get('longName', symbol), 
                      "sector": company_info.get('sector', 'Unknown')})
                
                # First, delete existing price nodes to avoid duplicates
                self.graph_db.query("""
                MATCH (c:Company {ticker: $ticker})-[r:HAS_PRICE]->(p:PricePoint)
                DELETE r, p
                """, {"ticker": symbol})
                
                # Create price nodes and relationships
                for date, row in hist.iterrows():
                    self.graph_db.query("""
                    MATCH (c:Company {ticker: $ticker})
                    CREATE (p:PricePoint {
                        date: datetime($date),
                        open: $open,
                        close: $close,
                        volume: $volume
                    })
                    CREATE (c)-[:HAS_PRICE]->(p)
                    """, {
                        "ticker": symbol,
                        "date": date.strftime("%Y-%m-%d"),
                        "open": float(row['Open']),
                        "close": float(row['Close']),
                        "volume": int(row['Volume'])
                    })
                
                return True
                
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    print(f"Failed to ingest {symbol} after {self.retry_attempts} attempts: {e}")
                    raise
                time.sleep(self.retry_delay) 