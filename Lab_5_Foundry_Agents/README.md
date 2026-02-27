# Lab 5 - Foundry Agents

In this lab, you'll build your first intelligent agents using the **Microsoft Agent Framework (MAF)** with Microsoft Foundry.

## What is the Microsoft Agent Framework?

The [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) is a production-ready framework for building AI agents that can reason, use tools, and maintain context across conversations. It provides:

- **Agents** — AI systems that receive instructions, use tools, and generate responses via an LLM
- **Tools** — Python functions the agent can decide to call based on the user's query
- **Context Providers** — Hooks that run automatically before/after each agent invocation to inject or extract information
- **Sessions** — Per-conversation containers with persistent state that survives across turns
- **Middleware** — Interceptors for logging, validation, and custom processing at the agent, chat, and function layers

### Tools vs Context Providers

This is the most important distinction in the framework:

| | Tools | Context Providers |
|---|---|---|
| **When they run** | Only when the agent decides to call them | Automatically before every agent invocation |
| **How they work** | Agent sees the function name + docstring and chooses whether to call it | `before_run()` injects instructions/messages into the context |
| **Best for** | On-demand actions (lookups, calculations, API calls) | Always-available background knowledge (RAG, memory, user preferences) |

In Notebook 01, you'll use **tools**. In Notebook 02, you'll use **context providers**. The rest of the workshop combines both approaches with Neo4j.

### Architecture

```
Agent.run(query)
    │
    ├── 1. Context Providers: before_run()
    │       └── Inject instructions, messages, and tools into SessionContext
    │
    ├── 2. LLM Invocation
    │       ├── Process instructions + context + user query
    │       ├── Decide which tools to call (if any)
    │       └── Generate response
    │
    └── 3. Context Providers: after_run()
            └── Extract data, store messages, update session state
```

## Prerequisites

Before starting, make sure you have:
- Completed **Lab 0** (Azure sign-in)
- Completed **Lab 4** (Codespace setup with environment variables configured)

## Lab Overview

### 01_simple_agent.ipynb - Simple Company Info Agent
Build your first agent using the Microsoft Agent Framework:
- Connect to Microsoft Foundry using `AzureOpenAIResponsesClient`
- Define a tool as a Python function with a docstring and type annotations
- Create an agent that looks up company information from SEC 10-K filings
- Stream agent responses in real-time

### 02_context_provider.ipynb - Introduction to Context Providers
Learn how context providers automatically inject context before each agent invocation:
- Build a `UserInfoMemory` context provider using `BaseContextProvider`
- Use `before_run()` to inject dynamic instructions based on session state
- Use `after_run()` to extract structured data from conversations with Pydantic
- Inspect `session.state` to see extracted data persist across turns

## Getting Started

### Select the Python Kernel

Before running the notebook, make sure you have the correct Python kernel selected:

1. Click **Select Kernel** in the top right of the notebook, then select **Python Environments...**
2. Select the **neo4j-azure-ai-workshop** environment (marked as Recommended)

### Work Through the Notebooks

1. Open `01_simple_agent.ipynb` — build an agent with tools
2. Open `02_context_provider.ipynb` — learn about context providers
3. Read through the code and run each cell

## Key Concepts

- **`AzureOpenAIResponsesClient`** — Connects to Azure OpenAI via Microsoft Foundry
- **`as_agent()`** — Creates a local agent with a name, instructions, tools, and optional context providers
- **`run_stream()` / `run()`** — Sends a query to the agent and returns a streaming or complete response
- **`BaseContextProvider`** — Base class for building context providers with `before_run()` and `after_run()` lifecycle hooks
- **`SessionContext`** — Per-invocation context; providers use `extend_instructions()` and `extend_messages()` to inject data
- **`AgentSession`** — Per-conversation container with a `state` dict that persists across turns
- **`Annotated` + `Field`** — Type annotations that describe tool parameters to the agent

## Next Steps

After completing this lab, continue to [Lab 6 - MAF Context Providers](../Lab_6_Context_Providers) to use `Neo4jContextProvider` for automatic knowledge graph retrieval.
