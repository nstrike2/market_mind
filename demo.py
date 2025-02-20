# demo.py
from crewai import Agent, Task, Crew, Process
from knowledge_graph.query_tools import MarketQueryTool
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    market_analyst = Agent(
        role="Financial Market Analyst",
        goal="Analyze market patterns and relationships to answer complex questions",
        backstory="An expert financial analyst with deep understanding of market dynamics and supply chain relationships",
        tools=[MarketQueryTool(db_config={
            "uri": os.getenv("NEO4J_URI"),
            "user": os.getenv("NEO4J_USER"),
            "password": os.getenv("NEO4J_PASSWORD")
        })],
        llm_config={
            "model": "gpt-4-turbo-preview",
            "temperature": 0.3
        }
    )

    # Example question demonstrating graph analysis capabilities
    analysis_task = Task(
        description="""
        Analyze the impact of Apple's iPhone 15 launch on its semiconductor supply chain:
        1. How did TSMC, Qualcomm, and other key suppliers perform around the announcement?
        2. Were there any notable supply chain disruptions or changes?
        3. Compare this launch's impact with previous iPhone releases.
        """,
        agent=market_analyst,
        expected_output="""
        A detailed analysis report covering:
        1. Performance metrics for key suppliers
        2. Supply chain impact analysis
        3. Comparative analysis with historical launches
        Include specific numbers, trends, and insights.
        """
    )

    crew = Crew(
        agents=[market_analyst],
        tasks=[analysis_task],
        process=Process.sequential
    )

    result = crew.kickoff()
    print("\n=== Analysis Results ===\n")
    print(result)

if __name__ == "__main__":
    main()
