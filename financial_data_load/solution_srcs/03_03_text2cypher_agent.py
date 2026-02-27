"""
Multi-Tool Agent with Text2Cypher

This workshop demonstrates an agent with three tools: schema retrieval,
vector search, and natural language to Cypher queries using the Microsoft
Agent Framework with Microsoft Foundry (V2 SDK - azure-ai-projects) and
neo4j-graphrag-python.

Run with: uv run python main.py solutions 11
"""

import asyncio
from typing import Annotated, Final

from neo4j import Driver
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers import VectorCypherRetriever, Text2CypherRetriever
from neo4j_graphrag.schema import get_schema
from pydantic import Field

from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential

from config import get_neo4j_driver, get_agent_config, get_embedder, _get_azure_token

# Retrieval query for vector search with graph context
# Path: (Company)-[:FROM_CHUNK]->(Chunk) - companies mentioned in chunks
RETRIEVAL_QUERY: Final[str] = """
OPTIONAL MATCH (company:Company)-[:FROM_CHUNK]->(node)
OPTIONAL MATCH (company)-[:FACES_RISK]->(risk:RiskFactor)
WITH node, score, company, collect(DISTINCT risk.name)[0..20] AS risks
WHERE score IS NOT NULL
RETURN
    node.text AS text,
    score,
    {company: company.name, risks: risks} AS metadata
ORDER BY score DESC
"""

# Custom prompt for Cypher generation with modern Cypher best practices
CYPHER_PROMPT: Final[str] = """Task: Generate a Cypher statement to query a graph database.

Instructions:
- Use only the provided relationship types and properties in the schema.
- Do not use any other relationship types or properties that are not provided.
- Only filter by name when a specific entity name is mentioned in the question.
  When filtering by name, use case-insensitive matching:
  `WHERE toLower(node.name) CONTAINS toLower('ActualEntityName')`
- Do NOT add name filters if no specific entity name is mentioned in the question.

Modern Cypher Requirements:
- Use `elementId(node)` instead of `id(node)` (id() is removed in Neo4j 5+).
- Use `count{{pattern}}` instead of `size((pattern))` for counting patterns.
- Use `EXISTS {{MATCH pattern}}` instead of `exists((pattern))` for existence checks.
- When using ORDER BY, filter NULL values first: `WHERE property IS NOT NULL ORDER BY property`.
- Use explicit grouping with WITH clauses for aggregations.
- Limit collected results when appropriate: `collect(item)[0..20]`.

Schema:
{schema}

Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.

The question is:
{query_text}"""


def create_tools(driver: Driver) -> list:
    """Create tools with the given Neo4j driver.

    Args:
        driver: Neo4j driver instance for database connections.

    Returns:
        List of tool functions for the agent.
    """
    config = get_agent_config()
    embedder = get_embedder()

    # LLM for Cypher generation
    if config.use_openai:
        cypher_llm = OpenAILLM(
            model_name=config.model_name,
            api_key=config.openai_api_key,
        )
    else:
        token = _get_azure_token()
        cypher_llm = OpenAILLM(
            model_name=config.model_name,
            base_url=config.inference_endpoint,
            api_key=token,
        )

    vector_retriever = VectorCypherRetriever(
        driver=driver,
        index_name="chunkEmbeddings",
        embedder=embedder,
        retrieval_query=RETRIEVAL_QUERY,
    )

    text2cypher_retriever = Text2CypherRetriever(
        driver=driver,
        llm=cypher_llm,
        neo4j_schema=get_schema(driver),
        custom_prompt=CYPHER_PROMPT,
    )

    def get_graph_schema() -> str:
        """Get the schema of the graph database including node labels, relationships, and properties."""
        return get_schema(driver)

    def retrieve_financial_documents(
        query: Annotated[str, Field(description="The search query to find relevant documents")]
    ) -> str:
        """Find details about companies in their financial documents using semantic search."""
        try:
            results = vector_retriever.search(query_text=query, top_k=3)
            if not results.items:
                return "No documents found matching the query."
            return "\n\n".join(item.content for item in results.items)
        except Exception as e:
            return f"Error searching documents: {e}"

    def query_database(
        query: Annotated[str, Field(description="A natural language question about companies, risks, or financial metrics")]
    ) -> str:
        """Get answers to specific questions about companies, risks, and financial metrics by querying the database directly."""
        try:
            results = text2cypher_retriever.search(query_text=query)
            if not results.items:
                return "No results found for the query."
            return "\n\n".join(item.content for item in results.items)
        except Exception as e:
            return f"Error querying database: {e}"

    return [get_graph_schema, retrieve_financial_documents, query_database]


async def run_agent(query: str):
    """Run the agent with the given query."""
    config = get_agent_config()

    with get_neo4j_driver() as driver:
        tools = create_tools(driver)

        async with AzureCliCredential() as credential:
            async with AzureAIClient(
                project_endpoint=config.project_endpoint,
                model_deployment_name=config.model_name,
                credential=credential,
            ) as client:
                agent = client.as_agent(
                    name="workshop-multi-tool-agent",
                    instructions=(
                        "You are a helpful assistant that can answer questions about "
                        "a graph database containing financial documents. You have three tools:\n"
                        "1. get_graph_schema - Get the database schema\n"
                        "2. retrieve_financial_documents - Search documents semantically\n"
                        "3. query_database - Query specific facts from the database\n\n"
                        "Choose the appropriate tool based on the question type. "
                        "When a tool returns data, use that data to answer the question directly."
                    ),
                    tools=tools,
                )
                print(f"User: {query}\n")
                print("Assistant: ", end="", flush=True)

                async for update in agent.run(query, stream=True):
                    if update.text:
                        print(update.text, end="", flush=True)

                print("\n")

    # Allow background tasks to complete before event loop closes
    await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(run_agent("What stock has Microsoft issued?"))


# Example queries to try:
# - What stock has Microsoft issued?
# - How does the graph model relate to financial documents and risk factors?
# - What are the top risk factors that Apple faces?
# - Summarize what risk factors are mentioned in Apple's financial documents?
# - How many risk facts does Apple face and what are the top ones?
# - What products does Microsoft mention in its financial documents?
