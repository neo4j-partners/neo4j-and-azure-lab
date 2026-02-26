"""
Simple Agent with Schema Retrieval Tool

This workshop demonstrates a basic agent using the Microsoft Agent Framework
with Microsoft Foundry (V2 SDK - azure-ai-projects) and neo4j-graphrag-python
for schema retrieval.

Run with: uv run python solutions/03_01_simple_agent.py
"""

import asyncio

from neo4j_graphrag.schema import get_schema

from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential

from config import get_neo4j_driver, get_agent_config


def create_schema_tool(driver):
    """Create the schema retrieval tool with the given driver."""

    def get_graph_schema() -> str:
        """Get the schema of the graph database including node labels, relationships, and properties."""
        return get_schema(driver)

    return get_graph_schema


async def run_agent(query: str):
    """Run the agent with the given query using streaming output."""
    config = get_agent_config()

    with get_neo4j_driver() as driver:
        get_graph_schema = create_schema_tool(driver)

        async with AzureCliCredential() as credential:
            async with AzureAIClient(
                project_endpoint=config.project_endpoint,
                model_deployment_name=config.model_name,
                async_credential=credential,
            ) as client:
                async with client.create_agent(
                    name="workshop-schema-agent",
                    instructions="You are a helpful assistant that can answer questions about a graph database schema.",
                    tools=[get_graph_schema],
                ) as agent:
                    print(f"User: {query}\n")
                    print("Assistant: ", end="", flush=True)

                    async for update in agent.run_stream(query):
                        if update.text:
                            print(update.text, end="", flush=True)

                    print("\n")

    # Allow background tasks to complete before event loop closes
    await asyncio.sleep(0.1)


async def main():
    """Run demo."""
    await run_agent("Summarise the schema of the graph database.")


if __name__ == "__main__":
    asyncio.run(main())


# Example queries to try:
# - Summarise the schema of the graph database.
# - What questions can I answer using this graph database?
# - How are Products related to other entities?
# - How does the graph model relate financial documents to risk factors?
