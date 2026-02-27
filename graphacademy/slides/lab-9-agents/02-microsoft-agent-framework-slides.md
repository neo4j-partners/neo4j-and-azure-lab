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

## Framework Components

The Microsoft Agent Framework provides infrastructure for building agents:

| Component | Purpose |
|-----------|---------|
| **AzureOpenAIResponsesClient** | Connects to Microsoft Foundry services |
| **`as_agent()`** | Creates an agent with tools and context providers |
| **Tools** | Python functions with docstrings |
| **Sessions** | Conversation history and persistent state |

---

## Creating an Agent

```python
agent = client.as_agent(
    name="graphrag-agent",
    model=os.environ["AZURE_AI_MODEL_NAME"],
    instructions="You are a helpful assistant that answers questions "
                 "about a knowledge graph.",
    tools=[get_graph_schema, search_content, query_database],
)

session = AgentSession()
async for update in agent.run_stream(input=query, session=session):
    if update.text:
        print(update.text, end="", flush=True)
```

**Key elements:**
- `as_agent()`: Creates the agent with instructions and tools
- `tools`: List of callable functions
- `run_stream`: Execute and stream responses
- `session`: Maintains conversation state across turns

---

## How Tool Selection Works

Tools are Python functions with descriptive docstrings:

```python
def get_graph_schema() -> str:
    """Get the schema of the graph database including node labels,
    relationships, and properties."""
    return get_schema(driver)
```

**The framework:**
1. Reads function name and docstring
2. Registers tool with agent
3. Matches questions to tool descriptions
4. Calls the best-matching tool

---

## Why Docstrings Matter

**Vague docstring (poor selection):**
```python
def search(query: str) -> str:
    """Search the database."""
```

**Specific docstring (accurate selection):**
```python
def search_content(query: str) -> str:
    """Search for content about topics and concepts using semantic search.
    Use for questions like 'What is...', 'Tell me about...', 'Explain...'"""
```

**The agent reads docstrings to decide when to use each tool.**

---

## The ReAct Loop

The framework implements ReAct automatically:

```
User: "How many companies are in the database?"
    ↓
Agent thinks: "This asks for a count—use database query tool"
    ↓
Agent calls: query_database("How many companies...")
    ↓
Agent observes: Result = 523
    ↓
Agent responds: "There are 523 companies in the database."
```

This loop can iterate multiple times for complex questions.

---

## Agent Instructions

Instructions guide agent behavior:

**Generic (less effective):**
```
"You are a helpful assistant."
```

**Specific (more effective):**
```
"You are a helpful assistant that answers questions about a knowledge
graph containing SEC filings data. You have three tools:

1. get_graph_schema - Use for questions about data structure
2. search_content - Use for semantic questions about topics
3. query_database - Use for specific facts, counts, and lookups

Choose the appropriate tool based on the question type."
```

---

## Session Management

For multi-turn conversations:

```python
# Create a session for conversation context
session = AgentSession()

# First message
result1 = await agent.run(input="What companies are in the database?", session=session)

# Follow-up maintains context
result2 = await agent.run(input="Tell me more about the first one", session=session)
```

The session preserves conversation history and persistent state.

---

## Streaming Responses

For real-time output:

```python
async for update in agent.run_stream(input=query, session=session):
    if update.text:
        print(update.text, end="", flush=True)
```

**Benefits:**
- Users see responses as they're generated
- Better experience (no waiting)
- Can observe tool selection in progress

---

## Summary

The Microsoft Agent Framework provides:

- **AzureOpenAIResponsesClient** for Microsoft Foundry integration
- **`as_agent()`** for creating agents with tools and context providers
- **Automatic tool selection** based on docstrings
- **ReAct pattern** for reasoning and acting
- **Session management** for conversations and persistent state
- **Streaming** for real-time responses

**Next:** Build your agent progressively—starting with one tool.
