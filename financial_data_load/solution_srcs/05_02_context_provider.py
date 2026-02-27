"""
Context Provider Introduction

This workshop demonstrates context providers using the Microsoft Agent Framework.
A UserInfoMemory context provider automatically extracts and remembers user info
(name, age) across conversation turns using structured LLM output.

Run with: uv run python main.py solutions <N>
"""

import asyncio
from typing import Any

from agent_framework import (
    AgentSession,
    BaseContextProvider,
    SessionContext,
    SupportsChatGetResponse,
)
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from pydantic import BaseModel

from config import get_agent_config


class UserInfo(BaseModel):
    name: str | None = None
    age: int | None = None


class UserInfoMemory(BaseContextProvider):
    """Context provider that extracts and remembers user info (name, age)."""

    def __init__(self, client: SupportsChatGetResponse):
        super().__init__("user-info-memory")
        self._chat_client = client

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Inject dynamic instructions based on stored user info."""
        my_state = state.setdefault(self.source_id, {})
        user_info = my_state.setdefault("user_info", UserInfo())

        instructions: list[str] = []

        if user_info.name is None:
            instructions.append(
                "Ask the user for their name and politely decline to answer any questions until they provide it."
            )
        else:
            instructions.append(f"The user's name is {user_info.name}.")

        if user_info.age is None:
            instructions.append(
                "Ask the user for their age and politely decline to answer any questions until they provide it."
            )
        else:
            instructions.append(f"The user's age is {user_info.age}.")

        context.extend_instructions(self.source_id, " ".join(instructions))

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Extract user info from the conversation after each turn."""
        my_state = state.setdefault(self.source_id, {})
        user_info = my_state.setdefault("user_info", UserInfo())
        if user_info.name is not None and user_info.age is not None:
            return  # Already have everything

        request_messages = context.get_messages(include_input=True, include_response=True)
        user_messages = [
            msg for msg in request_messages
            if hasattr(msg, "role") and msg.role == "user"
        ]
        if not user_messages:
            return

        try:
            result = await self._chat_client.get_response(
                messages=request_messages,
                instructions="Extract the user's name and age from the message if present. "
                "If not present return nulls.",
                options={"response_format": UserInfo},
            )
            extracted = result.value
            if extracted and user_info.name is None and extracted.name:
                user_info.name = extracted.name
            if extracted and user_info.age is None and extracted.age:
                user_info.age = extracted.age
            state.setdefault(self.source_id, {})["user_info"] = user_info
        except Exception:
            pass  # Failed to extract, continue without updating


async def run_agent(query: str):
    """Run the context provider agent with a multi-turn conversation."""
    config = get_agent_config()

    credential = AzureCliCredential()
    client = AzureOpenAIResponsesClient(
        project_endpoint=config.project_endpoint,
        deployment_name=config.model_name,
        credential=credential,
    )

    agent = client.as_agent(
        name="workshop-context-provider-agent",
        instructions="You are a friendly assistant. Always address the user by their name when you know it.",
        context_providers=[UserInfoMemory(client)],
    )

    session = agent.create_session()

    async def ask(q: str):
        print(f"User: {q}\n")
        print("Assistant: ", end="", flush=True)
        response = await agent.run(q, session=session)
        print(response.text)
        print()

    # Multi-turn conversation demonstrating the context provider
    await ask(query)
    await ask("My name is Alex")
    await ask("I am 30 years old")
    await ask("Now, what is the square root of 9?")

    # Show extracted state
    user_info = session.state.get("user-info-memory", {}).get("user_info", UserInfo())
    print(f"Extracted Name: {user_info.name}")
    print(f"Extracted Age: {user_info.age}")


async def main():
    """Run demo."""
    await run_agent("Hello, what is the square root of 9?")


if __name__ == "__main__":
    asyncio.run(main())
