from neo4j import GraphDatabase, Driver
from typing import Dict, List, Any, Optional
import pandas as pd

class MarketGraphDB:
    def __init__(self, uri: str, user: str, password: str):
        self._driver: Optional[Driver] = None
        self._uri = uri
        self._user = user
        self._password = password
        
    @property
    def driver(self) -> Driver:
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )
        return self._driver
        
    def close(self):
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            
    def query(self, cypher: str, params: Dict = None) -> List[Dict]:
        try:
            with self.driver.session() as session:
                result = session.run(cypher, params or {})
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Query failed: {e}")
            raise
            
    def entity_search(self, query: str, entity_type: str = None) -> List[Dict]:
        """Semantic search for entities"""
        cypher = """
        CALL db.index.fulltext.queryNodes("entityIndex", $query) 
        YIELD node, score
        WHERE $type IS NULL OR node.type = $type
        RETURN node, score
        LIMIT 10
        """
        return self.query(cypher, {"query": query, "type": entity_type})
    
    def pattern_search(self, pattern_query: str) -> List[Dict]:
        """Find market patterns matching description"""
        # Would require:
        # 1. Converting pattern_query to vector embedding
        # 2. Using Neo4j's vector search capabilities
        # 3. Matching against stored pattern vectors
        
        # Example implementation:
        """
        cypher = '''
        CALL db.index.vector.queryNodes(
            "patterns",
            20,  // num results
            $pattern_vector
        ) YIELD node, score
        RETURN node.pattern, score
        ORDER BY score DESC
        '''
        return self.query(cypher, {
            "pattern_vector": get_embedding(pattern_query)
        })
        """
        pass

    def get_entity_relationships(self, entity_id: str, depth: int = 2) -> Dict:
        """Get graph neighborhood around entity"""
        cypher = """
        MATCH path = (start)-[*1..{depth}]-(related)
        WHERE id(start) = $entity_id
        RETURN path
        """
        return self.query(cypher, {"entity_id": entity_id, "depth": depth})

    def get_price_history(self, symbol: str, days: int = None, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get historical price data for a symbol
        
        Args:
            symbol: Stock ticker
            days: Number of days of history (if using rolling window)
            start_date: Start date in YYYY-MM-DD format (if using date range)
            end_date: End date in YYYY-MM-DD format (if using date range)
        """
        if days:
            cypher = """
            MATCH (c:Company {ticker: $ticker})-[:HAS_PRICE]->(p:PricePoint)
            WHERE p.date >= datetime() - duration({days: $days})
            RETURN p.date as date, p.close as price, p.volume as volume, p.open as open
            ORDER BY p.date
            """
            return self.query(cypher, {"ticker": symbol, "days": days})
        else:
            cypher = """
            MATCH (c:Company {ticker: $ticker})-[:HAS_PRICE]->(p:PricePoint)
            WHERE date(p.date) >= date($start_date)
              AND date(p.date) <= date($end_date)
            RETURN p.date as date, p.close as price, p.volume as volume, p.open as open
            ORDER BY p.date
            """
            return self.query(cypher, {
                "ticker": symbol,
                "start_date": start_date,
                "end_date": end_date
            })

    def get_news_sentiment(self, ticker: str, days: int = 30) -> List[Dict]:
        """Get news sentiment data for a company"""
        cypher = """
        MATCH (c:Company {ticker: $ticker})-[:HAS_NEWS]->(n:News)
        WHERE n.date >= datetime() - duration({days: $days})
        RETURN n.date as date, n.sentiment as sentiment, n.title as title
        ORDER BY n.date
        """
        return self.query(cypher, {"ticker": ticker, "days": days})

    def get_supply_chain(self, ticker: str) -> List[Dict]:
        """Get supply chain relationships"""
        cypher = """
        MATCH (supplier:Company)-[:SUPPLIES]->(c:Company {ticker: $ticker})
        RETURN 
            supplier.ticker as ticker,
            supplier.name as name,
            1 as relationship_strength,
            ['SUPPLIES'] as relationship_types
        """
        return self.query(cypher, {"ticker": ticker})

    def get_correlated_stocks(self, symbol: str, min_correlation: float = 0.7) -> List[Dict]:
        """Find stocks with price correlation above threshold"""
        cypher = """
        MATCH (c1:Company {ticker: $ticker})-[:CORRELATES_WITH]->(c2:Company)
        WHERE c2.correlation_coefficient >= $min_correlation
        RETURN c2.ticker, c2.correlation_coefficient
        ORDER BY c2.correlation_coefficient DESC
        """
        return self.query(cypher, {"ticker": symbol, "min_correlation": min_correlation})

    def get_correlation_data(self, symbol: str, timeframe: str = "1y") -> List[Dict]:
        """Get price data for correlation analysis"""
        cypher = """
        MATCH (c:Company {ticker: $ticker})-[:HAS_PRICE]->(p:PricePoint)
        RETURN p.date as date, p.close as price
        ORDER BY p.date
        """
        return self.query(cypher, {"ticker": symbol})

    def get_news_correlation(self, ticker: str, days: int) -> Dict:
        """Get news and price data for correlation analysis"""
        news = self.get_news_sentiment(ticker, days)
        prices = self.get_price_history(ticker, days=days)
        return {
            'news': news,
            'prices': prices
        } 