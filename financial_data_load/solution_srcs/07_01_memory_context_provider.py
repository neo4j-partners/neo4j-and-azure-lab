"""
Memory Context Provider

This workshop demonstrates Neo4j Agent Memory as a MAF context provider.
The memory system provides persistent conversation history, entity extraction,
and preference learning backed by Neo4j.

Run with: uv run python main.py solutions 17
"""

import asyncio

from pydantic import SecretStr

from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential

from neo4j_agent_memory import MemoryClient, MemorySettings
from neo4j_agent_memory.integrations.microsoft_agent import (
    Neo4jMicrosoftMemory,
)

from azure_embedder import get_memory_embedder
from config import get_agent_config, Neo4jConfig


async def run_agent(query: str):
    """Run the agent with memory context provider."""
    config = get_agent_config()
    neo4j_config = Neo4jConfig()

    settings = MemorySettings(
        neo4j={
            "uri": neo4j_config.uri,
            "username": neo4j_config.username,
            "password": SecretStr(neo4j_config.password),
        },
    )

    async with MemoryClient(settings, embedder=get_memory_embedder()) as memory_client:
        memory = Neo4jMicrosoftMemory.from_memory_client(
            memory_client=memory_client,
            session_id="workshop-demo",
            include_short_term=True,
            include_long_term=True,
            include_reasoning=True,
            extract_entities=True,
        )

        async with AzureCliCredential() as credential:
            async with AzureAIClient(
                project_endpoint=config.project_endpoint,
                model_deployment_name=config.model_name,
                credential=credential,
            ) as client:
                agent = client.as_agent(
                    name="workshop-memory-agent",
                    instructions=(
                        "You are a helpful assistant with persistent memory. "
                        "You can remember previous conversations and user preferences. "
                        "When you notice the user expressing a preference, acknowledge it."
                    ),
                    context_providers=[memory.context_provider],
                )
                session = agent.create_session()

                print(f"User: {query}\n")
                print("Assistant: ", end="", flush=True)

                response = await agent.run(query, session=session)
                print(response.text)
                print()

    await asyncio.sleep(0.1)


async def main():
    """Run demo."""
    await run_agent("Hi! I'm interested in learning about Apple's products.")


if __name__ == "__main__":
    asyncio.run(main())


# Example queries to try:
# - Hi! I'm interested in learning about Apple's products.
# - What about their risk factors?
# - Can you remind me what we discussed?
