"""
Fulltext Context Provider

This workshop demonstrates a Neo4j context provider with fulltext search
using the Microsoft Agent Framework. The context provider automatically
injects knowledge graph context before each agent invocation.

Run with: uv run python main.py solutions 13
"""

import asyncio

from agent_framework.azure import AzureAIClient
from agent_framework_neo4j import Neo4jContextProvider, Neo4jSettings
from azure.identity.aio import AzureCliCredential

from config import get_agent_config


async def run_agent(query: str):
    """Run the agent with fulltext context provider."""
    config = get_agent_config()
    neo4j_settings = Neo4jSettings()

    provider = Neo4jContextProvider(
        uri=neo4j_settings.uri,
        username=neo4j_settings.username,
        password=neo4j_settings.get_password(),
        index_name=neo4j_settings.fulltext_index_name,
        index_type="fulltext",
        top_k=3,
        context_prompt=(
            "## Knowledge Graph Context\n"
            "Use the following information from the knowledge graph "
            "to answer questions about companies, products, and financials:"
        ),
    )

    async with AzureCliCredential() as credential:
        async with provider:
            async with AzureAIClient(
                project_endpoint=config.project_endpoint,
                model_deployment_name=config.model_name,
                async_credential=credential,
            ) as client:
                async with client.create_agent(
                    name="workshop-fulltext-agent",
                    instructions=(
                        "You are a helpful assistant that answers questions about companies "
                        "using the provided knowledge graph context. Be concise and cite "
                        "specific information from the context when available."
                    ),
                    context_providers=[provider],
                ) as agent:
                    session = agent.create_session()

                    print(f"User: {query}\n")
                    print("Assistant: ", end="", flush=True)

                    response = await agent.run(query, session=session)
                    print(response.text)
                    print()

    await asyncio.sleep(0.1)


async def main():
    """Run demo."""
    await run_agent("What products does Microsoft offer?")


if __name__ == "__main__":
    asyncio.run(main())


# Example queries to try:
# - What products does Microsoft offer?
# - Tell me about risk factors for technology companies
# - What are some financial metrics mentioned in SEC filings?
