"""
Agent with Memory Tools

This workshop demonstrates an agent with explicit memory tools alongside
the context provider. The agent can actively search, save, and recall
information using callable FunctionTool instances.

Run with: uv run python main.py solutions 17
"""

import asyncio

from pydantic import SecretStr

from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential

from neo4j_agent_memory import MemoryClient, MemorySettings
from neo4j_agent_memory.integrations.microsoft_agent import (
    Neo4jMicrosoftMemory,
    create_memory_tools,
)

from config import get_agent_config, Neo4jConfig


async def run_agent(query: str):
    """Run the agent with memory tools."""
    config = get_agent_config()
    neo4j_config = Neo4jConfig()

    settings = MemorySettings(
        neo4j={
            "uri": neo4j_config.uri,
            "username": neo4j_config.username,
            "password": SecretStr(neo4j_config.password),
        },
    )

    async with MemoryClient(settings) as memory_client:
        memory = Neo4jMicrosoftMemory.from_memory_client(
            memory_client=memory_client,
            session_id="workshop-tools-demo",
            include_short_term=True,
            include_long_term=True,
            extract_entities=True,
        )

        tools = create_memory_tools(memory)

        async with AzureCliCredential() as credential:
            async with AzureAIClient(
                project_endpoint=config.project_endpoint,
                model_deployment_name=config.model_name,
                async_credential=credential,
            ) as client:
                async with client.create_agent(
                    name="workshop-memory-tools-agent",
                    instructions=(
                        "You are a helpful assistant with persistent memory. You have access to "
                        "memory tools that let you:\n"
                        "1. Search your memory for relevant past conversations and facts\n"
                        "2. Save user preferences when they express them\n"
                        "3. Recall preferences to personalize your responses\n"
                        "4. Search the knowledge graph for entities\n"
                        "5. Remember important facts for future reference\n\n"
                        "Always use the appropriate memory tools to provide personalized assistance."
                    ),
                    tools=tools,
                    context_providers=[memory.context_provider],
                ) as agent:
                    print(f"User: {query}\n")
                    print("Assistant: ", end="", flush=True)

                    async for update in agent.run_stream(query):
                        if update.text:
                            print(update.text, end="", flush=True)

                    print("\n")

    await asyncio.sleep(0.1)


async def main():
    """Run demo."""
    await run_agent("I prefer concise technical explanations over high-level overviews.")


if __name__ == "__main__":
    asyncio.run(main())


# Example queries to try:
# - I prefer concise technical explanations over high-level overviews.
# - What can you tell me about supply chain risks in tech companies?
# - Remember that I'm particularly interested in Apple and Microsoft.
# - Based on what you know about my preferences, what should I focus on?
