# MarketMind: Graph-Based Market Intelligence System

MarketMind leverages knowledge graphs to map complex dependencies and entity relationships in financial markets, enabling a human-like understanding of market movements. Unlike traditional analysis, it uncovers hidden network effects, supply chain dependencies, and sentiment-driven trends. By applying graph algorithms, MarketMind enhances event impact analysis, reduces noise, and improves predictive insights—transforming how markets are understood and analyzed.

## Technical Demo (demo_features.py)

See [here](https://youtu.be/ZbAoXYsBkuM) for my full technical demo!

Shows raw system capabilities and data analysis:
```python
# Example: Analyze iPhone 15 launch impact across supply chain
event_impact = tool.run("event_impact: ticker=AAPL, event_date=2023-09-12, window=5")
supply_chain = tool.run("supply_chain_impact: ticker=AAPL, depth=2")
```

## Why I Built This

Traditional market analysis treats stocks as isolated entities, analyzing price movements in a vacuum. But markets are deeply interconnected - a chip shortage in Taiwan can impact iPhone sales, which affects hundreds of suppliers. I've built trading algorithms before, which told me about _how_ markets were moving, but never actually _why_ - I wanted to create a system that could derive a human-like understanding of markets. MarketMind uses graph database technology to map these complex relationships and predict cascade effects across markets.

Knowledge graphs are an incredibly rich representation of data for any machine learning system to derive semantic undestanding, engendering immensely practical applications including the reduction of hallcuination in LLMs, more accurate information retrieval for applications such as RAG, and many more!

Key differentiators:
- **Supply Chain Mapping**: Automatically identifies and quantifies supplier relationships
- **Event Impact Analysis**: Measures how events (like product launches) ripple through related companies
- **Sentiment Integration**: Combines news sentiment with price data to spot early warning signs
- **Network Effects**: Uses graph algorithms to find hidden dependencies traditional analysis misses

## Example Analysis

### AI-Powered Analysis (demo.py)
Uses CrewAI and GPT-4 for intelligent market insights:
```python
# Example: AI analysis of supply chain impacts
crew = Crew(
    agents=[market_analyst],
    tasks=[analysis_task],
    process=Process.sequential
)
result = crew.kickoff()
```

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Neo4j Database (Community Edition is fine)
- News API Key (for sentiment analysis)
- SEC API Key (for financial data)
- OpenAI API Key (for AI-powered analysis)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/[your-username]/market_mind.git
cd market_mind

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the project root:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEWS_API_KEY=your_news_api_key
SEC_API_KEY=your_sec_api_key
OPENAI_API_KEY=your_openai_key  # Required for demo.py
```

### 4. Neo4j Setup
1. [Download and install Neo4j](https://neo4j.com/download/)
2. Create a new database
3. Set password to match your .env file
4. Start the database server

### 5. Data Ingestion
```bash
# Make sure your virtual environment is activated
PYTHONPATH=. python3 data_ingestion/ingest_data.py
```

### 6. Run the Demos
```bash
# Technical feature demonstration
PYTHONPATH=. python3 demo_features.py

# AI-powered analysis
PYTHONPATH=. python3 demo.py
```

## Project Structure
```
market_mind/
├── data_ingestion/          # Data collection and graph building
│   ├── __init__.py
│   ├── graph_builder.py     # Graph database population
│   └── ingest_data.py      # Main ingestion script
├── knowledge_graph/         # Core analysis tools
│   ├── __init__.py
│   ├── graph_interface.py   # Neo4j interface
│   └── query_tools.py      # Analysis methods
├── demo_features.py         # Technical feature demonstration
├── demo.py                  # AI-powered analysis demo
├── test_connections.py      # Connection testing
└── requirements.txt
```

## Features

### 1. Supply Chain Analysis
- Maps supplier relationships
- Quantifies relationship strengths
- Tracks cascading effects

### 2. Price Correlation
- Analyzes price relationships
- Identifies leading indicators
- Spots divergences

### 3. News Sentiment Integration
- Real-time news processing
- Sentiment scoring
- Event impact analysis

### 4. Event Impact Analysis
- Pre/post event comparison
- Volume analysis
- Supply chain effects

### 5. AI-Powered Insights (via demo.py)
- Complex pattern recognition
- Natural language queries
- Automated market research
- Historical comparisons

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/) 
