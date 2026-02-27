---
marp: true
theme: default
paginate: true
---

<style>
section {
  --marp-auto-scaling-code: false;
}

li {
  opacity: 1 !important;
  animation: none !important;
  visibility: visible !important;
}

/* Disable all fragment animations */
.marp-fragment {
  opacity: 1 !important;
  visibility: visible !important;
}

ul > li,
ol > li {
  opacity: 1 !important;
}
</style>


# Tools and Context Providers

---

## Defining a Tool

A tool is a Python function with type annotations and a docstring:

```python
from typing import Annotated
from pydantic import Field

def get_company_info(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g. AAPL)")]
) -> str:
    """Look up company information from SEC 10-K filings.
    Use for questions about specific companies."""
    return lookup_company(ticker)
```

The framework reads the **function name**, **docstring**, and **parameter annotations** to tell the agent what this tool does.

---

## How Tool Selection Works

The agent sees all registered tools and decides which to call:

```
User: "What does Apple do?"
    ↓
Agent sees tools:
  - get_company_info: "Look up company information..."
  - search_risks: "Search for risk factors..."
    ↓
Agent reasons: "User asks about a company → get_company_info"
    ↓
Agent calls: get_company_info(ticker="AAPL")
    ↓
Agent responds with the result
```

**Better docstrings lead to better tool selection.**

---

## Why Annotations Matter

Compare these two tool definitions:

**Vague (poor selection):**
```python
def search(query):
    """Search the database."""
```

**Specific (accurate selection):**
```python
def search_risks(
    query: Annotated[str, Field(description="Search query about risk factors")]
) -> str:
    """Search for risk factors and threats from SEC filings.
    Use for questions like 'What risks does X face?'"""
```

`Annotated` + `Field` tells the agent exactly what each parameter expects.

---

## What is a Context Provider?

A context provider runs **automatically** before and after each agent invocation:

```python
from agent_framework import BaseContextProvider

class UserInfoMemory(BaseContextProvider):
    async def before_run(self, *, agent, session, context, state):
        # Inject knowledge before the LLM sees the query
        context.extend_instructions(
            self.source_id,
            f"The user's name is {session.state.get('user_name', 'unknown')}."
        )

    async def after_run(self, *, agent, session, context, state):
        # Extract and store information after the response
        pass
```

---

## The Context Provider Lifecycle

| Hook | When It Runs | What It Does |
|------|-------------|--------------|
| **`before_run()`** | Before LLM invocation | Injects instructions, messages, or tools into the context |
| **`after_run()`** | After LLM responds | Extracts data, stores messages, updates session state |

**`before_run()`** has two injection methods:

- **`context.extend_instructions()`** — adds to the system prompt
- **`context.extend_messages()`** — adds context as conversation messages

---

## Extracting Data with after_run()

Use `after_run()` to extract structured data from conversations:

```python
from pydantic import BaseModel

class UserProfile(BaseModel):
    name: str | None = None
    role: str | None = None

class UserInfoMemory(BaseContextProvider):
    async def after_run(self, *, agent, session, context, state):
        # Parse the conversation to extract user info
        profile = extract_profile(context.output_messages)
        if profile.name:
            session.state["user_name"] = profile.name
```

Pydantic models give you structured, validated data from free-form conversations.

---

## Attaching Providers to an Agent

Pass context providers when creating the agent:

```python
memory = UserInfoMemory()

agent = client.as_agent(
    name="assistant",
    model=os.environ["AZURE_AI_MODEL_NAME"],
    instructions="You are a helpful assistant.",
    tools=[get_company_info],
    context_providers=[memory],
)
```

The framework calls `before_run()` on all providers before the LLM, and `after_run()` on all providers after the response.

---

## Inspecting Session State

Session state persists across turns and is visible to all providers:

```python
session = AgentSession()

# Turn 1: user introduces themselves
await agent.run("Hi, I'm Alice and I'm a data engineer.", session=session)

# After turn 1, after_run() extracted:
print(session.state)
# {"user_name": "Alice", "role": "data engineer"}

# Turn 2: before_run() injects this context automatically
await agent.run("What should I focus on?", session=session)
# Agent knows Alice is a data engineer and tailors the response
```

---

## Summary

In this lesson, you learned:

- **Tools** are Python functions with docstrings and `Annotated` type hints
- **Tool selection** works by matching questions to function descriptions
- **Context providers** use `before_run()` and `after_run()` lifecycle hooks
- **`extend_instructions()`** injects into the system prompt
- **`extend_messages()`** injects context as conversation messages
- **Pydantic** enables structured data extraction in `after_run()`
- **Session state** persists across turns for all providers to share

**Next:** Use Neo4j context providers for automatic knowledge graph retrieval.
