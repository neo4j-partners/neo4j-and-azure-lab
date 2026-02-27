"""
Graph-Enriched Context Provider

This workshop demonstrates a Neo4j context provider with graph-enriched mode
using the Microsoft Agent Framework. Combines vector search with graph traversal
to provide company, product, and risk factor context.

Run with: uv run python main.py solutions 16
"""

import asyncio
from typing import Final

from azure.identity import DefaultAzureCredential
from azure.identity.aio import AzureCliCredential

from agent_framework.azure import AzureAIClient
from agent_framework_neo4j import (
    AzureAIEmbedder,
    AzureAISettings,
    Neo4jContextProvider,
    Neo4jSettings,
)

from config import get_agent_config

# Graph-enriched retrieval query
RETRIEVAL_QUERY: Final[str] = """
OPTIONAL MATCH (company:Company)-[:FROM_CHUNK]->(node)
OPTIONAL MATCH (company)-[:FACES_RISK]->(risk:RiskFactor)
WITH node, score, company,
     collect(DISTINCT risk.name)[0..5] AS risks
OPTIONAL MATCH (company)-[:OFFERS]->(product:Product)
WITH node, score, company, risks,
     collect(DISTINCT product.name)[0..5] AS products
RETURN
    node.text AS text,
    score,
    company.name AS company,
    company.ticker AS ticker,
    risks,
    products
ORDER BY score DESC
"""


async def run_agent(query: str):
    """Run the agent with graph-enriched context provider."""
    config = get_agent_config()
    neo4j_settings = Neo4jSettings()
    azure_settings = AzureAISettings()

    sync_credential = DefaultAzureCredential()
    embedder = AzureAIEmbedder(
        endpoint=azure_settings.inference_endpoint,
        credential=sync_credential,
        model=azure_settings.embedding_model,
    )

    provider = Neo4jContextProvider(
        uri=neo4j_settings.uri,
        username=neo4j_settings.username,
        password=neo4j_settings.get_password(),
        index_name=neo4j_settings.vector_index_name,
        index_type="vector",
        retrieval_query=RETRIEVAL_QUERY,
        embedder=embedder,
        top_k=5,
        context_prompt=(
            "## Graph-Enriched Knowledge Context\n"
            "The following information combines semantic search results with "
            "graph traversal to provide company, product, and risk context:"
        ),
    )

    try:
        async with AzureCliCredential() as credential:
            async with provider:
                async with AzureAIClient(
                    project_endpoint=config.project_endpoint,
                    model_deployment_name=config.model_name,
                    credential=credential,
                ) as client:
                    agent = client.as_agent(
                        name="workshop-graph-enriched-agent",
                        instructions=(
                            "You are a helpful assistant that answers questions about companies "
                            "using graph-enriched context. Your context includes:\n"
                            "- Semantic search matches from company filings\n"
                            "- Company names and ticker symbols\n"
                            "- Products the company mentions\n"
                            "- Risk factors the company faces\n\n"
                            "When answering, cite the company, relevant products, and risks. "
                            "Be specific and reference the enriched graph data."
                        ),
                        context_providers=[provider],
                    )
                    session = agent.create_session()

                    print(f"User: {query}\n")
                    print("Assistant: ", end="", flush=True)

                    response = await agent.run(query, session=session)
                    print(response.text)
                    print()

        await asyncio.sleep(0.1)
    finally:
        embedder.close()


async def main():
    """Run demo."""
    await run_agent("What are Apple's main products and what risks does the company face?")


if __name__ == "__main__":
    asyncio.run(main())


# Example queries to try:
# - What are Apple's main products and what risks does the company face?
# - Tell me about Microsoft's cloud services and business risks
# - What products and risks are mentioned in Amazon's filings?
