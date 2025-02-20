from crewai.tools import BaseTool
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from .graph_interface import MarketGraphDB
import os
import logging
from pydantic import Field, ConfigDict
import numpy as np

class MarketQueryTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "market_query_tool"
    description: str = """
    Advanced market analysis tool that leverages graph relationships to uncover market patterns and insights.
    Available commands:

    1) price_history: ticker=<str>, days=<int>
       Get historical price data with volume analysis
       Example: 'price_history: ticker=AAPL, days=30'

    2) correlation_analysis: symbol1=<str>, symbol2=<str>, timeframe=<str>
       Analyze relationship between two assets with statistical metrics
       Example: 'correlation_analysis: symbol1=AAPL, symbol2=MSFT, timeframe=1y'

    3) event_impact: ticker=<str>, event_date=<YYYY-MM-DD>, window=<int>
       Analyze price movement around an event with pre/post comparison
       Example: 'event_impact: ticker=AAPL, event_date=2024-01-15, window=5'

    4) supply_chain_impact: ticker=<str>, depth=<int>
       Analyze impact on supply chain partners
       Example: 'supply_chain_impact: ticker=AAPL, depth=2'

    5) news_sentiment_correlation: ticker=<str>, days=<int>
       Analyze correlation between news sentiment and price movements
       Example: 'news_sentiment_correlation: ticker=AAPL, days=30'
    """
    
    # Define all class fields with Pydantic
    graph_db: MarketGraphDB = Field(default=None, exclude=True)
    query_audit: List[Dict] = Field(default_factory=list, exclude=True)
    logger: Optional[logging.Logger] = Field(default=None, exclude=True)

    def __init__(self, db_config: dict):
        super().__init__()
        self.graph_db = MarketGraphDB(**db_config)
        
        # Add error handling for env vars
        if not all([os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")]):
            raise EnvironmentError("Missing required Neo4j environment variables")

        # Add basic logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _run(self, command: str) -> str:
        self.query_audit.append({
            'query': command,
            'timestamp': datetime.now().isoformat()
        })

        cmd = command.strip().lower()
        
        try:
            if cmd.startswith("price_history:"):
                params = self._parse_params(cmd.split(":", 1)[1])
                result = self.graph_db.get_price_history(
                    params.get("ticker"),
                    int(params.get("days", 30))
                )
                return self._format_price_history(result)
                
            elif cmd.startswith("correlation_analysis:"):
                params = self._parse_params(cmd.split(":", 1)[1])
                result = self._analyze_correlation(
                    params.get("symbol1"),
                    params.get("symbol2"),
                    params.get("timeframe", "1y")
                )
                return self._format_correlation(result)

            elif cmd.startswith("supply_chain_impact:"):
                params = self._parse_params(cmd.split(":", 1)[1])
                result = self._analyze_supply_chain(
                    params.get("ticker"),
                    int(params.get("depth", 2))
                )
                return self._format_supply_chain(result)

            elif cmd.startswith("news_sentiment_correlation:"):
                params = self._parse_params(cmd.split(":", 1)[1])
                result = self._analyze_news_sentiment(
                    params.get("ticker"),
                    int(params.get("days", 30))
                )
                return self._format_news_sentiment(result)

            elif cmd.startswith("event_impact:"):
                params = self._parse_params(cmd.split(":", 1)[1])
                result = self._analyze_event_impact(
                    params.get("ticker"),
                    params.get("event_date"),
                    int(params.get("window", 5))
                )
                return self._format_event_impact(result)
                
        except Exception as e:
            return f"Error executing query: {str(e)}"

    def _parse_params(self, param_str: str) -> Dict:
        """Parse parameters from command string"""
        params = {}
        for param in param_str.split(','):
            if '=' in param:
                key, value = param.split('=')
                params[key.strip()] = value.strip()
        return params

    def _validate_params(self, params: Dict, required: List[str]) -> None:
        """Validate required parameters are present and correctly formatted"""
        for param in required:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
            
            # Validate specific parameter formats
            if param == "ticker":
                if not isinstance(params[param], str) or not params[param].isalpha():
                    raise ValueError(f"Invalid ticker format: {params[param]}")
                
            elif param == "event_date":
                try:
                    datetime.strptime(params[param], "%Y-%m-%d")
                except ValueError:
                    raise ValueError(f"Invalid date format: {params[param]}. Use YYYY-MM-DD")

    def _format_price_history(self, data: List[Dict]) -> str:
        """Format price history data for agent consumption"""
        return "\n".join([
            f"Date: {d['date']}, Close: ${d['close']:.2f}, Volume: {d['volume']:,}"
            for d in data
        ])

    def _format_correlation(self, data: List[Dict]) -> str:
        """Format correlation analysis data for agent consumption"""
        return "\n".join([
            f"Ticker: {d['ticker']}, Correlation: {d['correlation_coefficient']:.2f}"
            for d in data
        ])

    def _analyze_correlation(self, symbol1: str, symbol2: str, timeframe: str) -> List[Dict]:
        """Analyze correlation between two assets with advanced metrics"""
        # Use interface method instead of direct query
        prices1 = self.graph_db.get_correlation_data(symbol1, timeframe)
        prices2 = self.graph_db.get_correlation_data(symbol2, timeframe)
        
        if not prices1 or not prices2:
            return []
        
        # Calculate correlation
        prices1_arr = np.array([p['price'] for p in prices1])
        prices2_arr = np.array([p['price'] for p in prices2])
        correlation = np.corrcoef(prices1_arr, prices2_arr)[0,1]
        
        return [{
            'ticker': symbol2,
            'correlation_coefficient': float(correlation),
            'period': timeframe,
            'data_points': len(prices1)
        }]

    def _analyze_supply_chain(self, ticker: str, depth: int) -> Dict:
        """Analyze supply chain relationships and impacts"""
        suppliers = self.graph_db.get_supply_chain(ticker)
        
        result = []
        for supplier in suppliers:
            # Get recent price impact
            price_history = self.graph_db.get_price_history(supplier['ticker'], days=30)
            price_change = self._calculate_price_change(price_history)
            
            result.append({
                'ticker': supplier['ticker'],
                'name': supplier['name'],
                'impact': price_change,
                'relationship_strength': supplier['relationship_strength'],
                'relationship_type': supplier['relationship_types'][0]
            })
        
        return result

    def _analyze_news_sentiment(self, ticker: str, days: int) -> Dict:
        """Analyze correlation between news sentiment and price movements"""
        # Use interface method
        data = self.graph_db.get_news_correlation(ticker, days)
        
        result = []
        if data['news'] and data['prices']:
            avg_sentiment = sum(n['sentiment'] for n in data['news']) / len(data['news'])
            price_change = self._calculate_price_change(data['prices'])
            
            result.append({
                'ticker': ticker,
                'sentiment': avg_sentiment,
                'price_change': price_change,
                'news_count': len(data['news'])
            })
        
        return result

    def _calculate_correlation(self, series1: List, series2: List) -> float:
        """Helper method to calculate correlation between two price series"""
        # Simple correlation calculation
        # In production, you'd want to use numpy/pandas for this
        x = [p[1] for p in series1]
        y = [p[1] for p in series2]
        
        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denominator = (
            (sum((xi - mean_x) ** 2 for xi in x) * 
             sum((yi - mean_y) ** 2 for yi in y)) ** 0.5
        )
        
        return numerator / denominator if denominator != 0 else 0

    def _calculate_price_change(self, price_history: List[Dict]) -> float:
        """Helper method to calculate price change percentage"""
        if not price_history or len(price_history) < 2:
            return 0.0
        
        start_price = price_history[0]['close']
        end_price = price_history[-1]['close']
        
        return ((end_price - start_price) / start_price) * 100

    def _format_supply_chain(self, data: Dict) -> str:
        """Format supply chain analysis data for agent consumption"""
        return "\n".join([
            f"Ticker: {d['ticker']}, Impact: {d['impact']:.2f}"
            for d in data
        ])

    def _format_news_sentiment(self, data: Dict) -> str:
        """Format news sentiment analysis data for agent consumption"""
        return "\n".join([
            f"Ticker: {d['ticker']}, Sentiment: {d['sentiment']:.2f}"
            for d in data
        ])

    def _analyze_event_impact(self, ticker: str, event_date: str, window: int) -> List[Dict]:
        """Analyze price movement around an event"""
        from datetime import datetime, timedelta
        
        # Calculate date range
        event_dt = datetime.strptime(event_date, "%Y-%m-%d")
        start_date = (event_dt - timedelta(days=window)).strftime("%Y-%m-%d")
        end_date = (event_dt + timedelta(days=window)).strftime("%Y-%m-%d")
        
        # Get prices using date range
        prices = self.graph_db.get_price_history(
            ticker,
            start_date=start_date,
            end_date=end_date
        )
        
        if not prices:
            return []
        
        # Find event index
        event_idx = next((i for i, p in enumerate(prices) 
                         if p['date'].strftime("%Y-%m-%d") == event_date), None)
                         
        if event_idx is None:
            return []
        
        # Calculate pre/post metrics
        pre_prices = [p['price'] for p in prices[:event_idx]]
        post_prices = [p['price'] for p in prices[event_idx+1:]]
        
        pre_change = ((pre_prices[-1] - pre_prices[0]) / pre_prices[0]) * 100 if pre_prices else 0
        post_change = ((post_prices[-1] - post_prices[0]) / post_prices[0]) * 100 if post_prices else 0
        
        pre_vol = sum(p['volume'] for p in prices[:event_idx]) / len(prices[:event_idx]) if prices[:event_idx] else 0
        post_vol = sum(p['volume'] for p in prices[event_idx+1:]) / len(prices[event_idx+1:]) if prices[event_idx+1:] else 0
        
        return [{
            'ticker': ticker,
            'event_date': event_date,
            'pre_event_change': pre_change,
            'post_event_change': post_change,
            'volume_change': post_vol - pre_vol
        }]

    def _format_event_impact(self, data: List[Dict]) -> str:
        """Format event impact analysis data"""
        return "\n".join([
            f"Event Date: {d['event_date']}\n"
            f"Pre-event Change: {d['pre_event_change']:.2f}%\n"
            f"Post-event Change: {d['post_event_change']:.2f}%\n"
            f"Volume Change: {d['volume_change']:,.0f}"
            for d in data
        ]) 