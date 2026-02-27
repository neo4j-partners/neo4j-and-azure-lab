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


# The Microsoft Agent Framework

---

## The Problem: LLMs Are Stateless

Every time you call an LLM, it starts from scratch:

- **No memory** of previous conversations
- **No access** to your data or databases
- **No ability** to take actions in the real world

An LLM alone can answer questions, but it can't retrieve your data, remember what you told it, or call APIs on your behalf.

**We need a framework to bridge this gap.**

---

## What is the Microsoft Agent Framework?

The [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) orchestrates a lifecycle around each LLM call, turning a bare model into an agent that can retrieve, reason, and act.

| Component | Purpose |
|-----------|---------|
| **Agents** | AI systems with instructions, tools, and context providers |
| **Tools** | Python functions the agent can decide to call |
| **Context Providers** | Hooks that inject or extract information automatically |
| **Sessions** | Per-conversation containers with persistent state |
| **Middleware** | Interceptors for logging, validation, custom processing |

---

## The Agent Lifecycle

Every time the agent handles a query, this lifecycle runs:

```
Agent.run(query)
    │
    ├── 1. Context Providers: before_run()
    │       └── Inject instructions, messages, and tools
    │
    ├── 2. LLM Invocation
    │       ├── Process instructions + context + query
    │       ├── Decide which tools to call (if any)
    │       └── Generate response
    │
    └── 3. Context Providers: after_run()
            └── Extract data, store messages, update state
```

Context providers wrap each LLM call with automatic retrieval and storage.

---

## Tools vs Context Providers

This is the most important distinction in the framework:

| | Tools | Context Providers |
|---|---|---|
| **When** | Only when the agent decides | Automatically every invocation |
| **How** | Agent reads function name + docstring | `before_run()` injects into context |
| **Best for** | On-demand actions (lookups, API calls) | Background knowledge (RAG, memory) |
| **Visibility** | Agent explicitly chooses to call | Transparent — runs silently |

**Tools** give the agent capabilities. **Context providers** give the agent knowledge.

---

## Connecting to Azure

The framework connects to Azure OpenAI through Microsoft Foundry:

```python
from azure.ai.projects import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

client = AzureOpenAIResponsesClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=AzureCliCredential(),
)
```

`AzureOpenAIResponsesClient` handles authentication, model routing, and API communication.

---

## Creating an Agent

Use `as_agent()` to create an agent with a name, instructions, and tools:

```python
agent = client.as_agent(
    name="company-info-agent",
    model=os.environ["AZURE_AI_MODEL_NAME"],
    instructions="You are a helpful assistant that answers questions "
                 "about SEC 10-K company filings.",
    tools=[get_company_info],
)
```

**Key elements:**
- `instructions`: The agent's purpose and behavior
- `tools`: List of Python functions the agent can call
- `model`: Which LLM to use for reasoning

---

## Running and Streaming

Execute the agent and stream responses in real-time:

```python
session = AgentSession()

async for update in agent.run_stream(
    input="What products does Apple sell?",
    session=session,
):
    if update.text:
        print(update.text, end="", flush=True)
```

**`run_stream()`** yields response chunks as they're generated.

**`AgentSession`** maintains conversation history and state across turns.

---

## Sessions and State

Sessions persist across multiple interactions:

```python
session = AgentSession()

# First turn
await agent.run("My name is Alice", session=session)

# Second turn — agent remembers the first
await agent.run("What is my name?", session=session)
```

Sessions also carry a `state` dictionary for context providers to read and write:

```python
session.state["user_name"] = "Alice"
session.state["preferences"] = {"language": "Python"}
```

---

## Summary

The Microsoft Agent Framework provides:

- **Lifecycle orchestration** around each LLM call (before → LLM → after)
- **Tools** for on-demand actions the agent explicitly calls
- **Context providers** for automatic background knowledge injection
- **Sessions** for persistent state across conversation turns
- **`AzureOpenAIResponsesClient`** for Microsoft Foundry integration

**Next:** Define tools and context providers in detail.
