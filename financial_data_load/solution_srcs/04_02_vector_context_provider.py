"""
Vector Context Provider

This workshop demonstrates a Neo4j context provider with vector (semantic)
search using the Microsoft Agent Framework. The provider embeds queries and
finds semantically similar content.

Run with: uv run python main.py solutions 14
"""

import asyncio

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


async def run_agent(query: str):
    """Run the agent with vector context provider."""
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
        embedder=embedder,
        top_k=5,
        context_prompt=(
            "## Semantic Search Results\n"
            "Use the following semantically relevant information from the "
            "knowledge graph to answer questions:"
        ),
    )

    try:
        async with AzureCliCredential() as credential:
            async with provider:
                async with AzureAIClient(
                    project_endpoint=config.project_endpoint,
                    model_deployment_name=config.model_name,
                    async_credential=credential,
                ) as client:
                    async with client.create_agent(
                        name="workshop-vector-agent",
                        instructions=(
                            "You are a helpful assistant that answers questions about companies "
                            "using the provided semantic search context. Be concise and accurate. "
                            "When the context contains relevant information, cite it in your response."
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
    finally:
        embedder.close()


async def main():
    """Run demo."""
    await run_agent("What are the main business activities of tech companies?")


if __name__ == "__main__":
    asyncio.run(main())


# Example queries to try:
# - What are the main business activities of tech companies?
# - Describe challenges and risks in the technology sector
# - How do companies generate revenue and measure performance?
