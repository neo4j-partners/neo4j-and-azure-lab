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


# Memory Context Provider and Tools

---

## Two Ways to Use Memory

The `neo4j-agent-memory` package provides two complementary approaches:

| Approach | How It Works | Best For |
|----------|-------------|----------|
| **Context Provider** | Runs automatically before/after each invocation | Background recall — agent always has relevant memory |
| **Memory Tools** | Agent explicitly calls memory functions | Active management — agent saves and searches on demand |

You can use either approach alone, or **combine both** for full capability.

---

## Memory Context Provider

The memory context provider injects relevant memory before each LLM call:

**`before_run()` retrieves:**
1. Recent conversation history (short-term)
2. Semantically relevant past messages (short-term)
3. Matching user preferences (long-term)
4. Related entities and facts (long-term)
5. Similar past reasoning traces (reasoning)

**`after_run()` stores:**
1. New messages from the conversation
2. Automatically extracted entities (people, organizations, concepts)

---

## Setting Up the Memory Provider

```python
from neo4j_agent_memory import Neo4jMicrosoftMemory

memory = Neo4jMicrosoftMemory(
    session_id=session_id,
    neo4j_driver=driver,
    embedder=embedder,
    llm=llm,
)

provider = memory.as_context_provider(
    include_short_term=True,
    include_long_term=True,
    include_reasoning=True,
    max_context_items=10,
)
```

`Neo4jMicrosoftMemory` wraps all three memory types into a single interface.

---

## The Six Memory Tools

`create_memory_tools()` generates callable tools the agent can use explicitly:

| Tool | Purpose |
|------|---------|
| **`search_memory`** | Search across all memory types (messages, entities, preferences) |
| **`remember_preference`** | Save a user preference with category and context |
| **`recall_preferences`** | Retrieve saved preferences by topic |
| **`search_knowledge`** | Query the knowledge graph for entities by type |
| **`remember_fact`** | Store a factual relationship as a Subject-Predicate-Object triple |
| **`find_similar_tasks`** | Retrieve similar past reasoning traces |

---

## Creating Memory Tools

```python
from neo4j_agent_memory import create_memory_tools

tools = create_memory_tools(memory)

agent = client.as_agent(
    name="memory-agent",
    model=os.environ["AZURE_AI_MODEL_NAME"],
    instructions="You are a helpful assistant with persistent memory. "
                 "Remember user preferences and facts for future use.",
    tools=tools,
    context_providers=[provider],
)
```

The agent can now both **passively recall** (via context provider) and **actively manage** (via tools) its memory.

---

## Context Provider vs Memory Tools

| Aspect | Context Provider | Memory Tools |
|--------|-----------------|--------------|
| **Invocation** | Automatic every turn | Agent decides when |
| **Direction** | Recall and store | Search, save, recall on demand |
| **User visibility** | Transparent | Visible in agent reasoning |
| **Control** | Framework-managed | Agent-managed |

**Context provider**: "I automatically remember relevant things."
**Memory tools**: "I can explicitly search, save, and recall."

---

## Entity Extraction

When `after_run()` processes a conversation, it automatically identifies entities:

```
User: "I work at Microsoft in the Seattle office."
             ↓
Entity extraction identifies:
  - Microsoft (ORGANIZATION)
  - Seattle (LOCATION)
             ↓
Stored in Neo4j with embeddings and relationships:
  (User)-[:WORKS_AT]->(Microsoft:Entity {type: "ORGANIZATION"})
  (Microsoft)-[:LOCATED_IN]->(Seattle:Entity {type: "LOCATION"})
```

Entities are **deduplicated** — if "Microsoft" already exists, it merges rather than creating a duplicate.

---

## Combining Both Approaches

The most capable agents use both context providers and memory tools:

```
Turn 1: "I prefer Python and work in data engineering."
    → after_run() extracts: preference(Python), role(data engineer)
    → Tools: remember_preference("language", "Python")

Turn 2: "What framework should I use for this project?"
    → before_run() injects: "User prefers Python, works in data engineering"
    → Agent tailors recommendation based on memory

Turn 3: "What did we discuss about frameworks last week?"
    → Tools: search_memory("frameworks discussion")
    → Returns relevant past messages
```

---

## Summary

In this lesson, you learned:

- **Memory context provider**: `before_run()` retrieves from all three memory types, `after_run()` stores and extracts entities
- **Six memory tools**: search, remember preferences/facts, recall, find similar tasks
- **Context provider vs tools**: automatic background recall vs explicit agent-controlled operations
- **Entity extraction**: automatic identification and deduplication of entities from conversations
- **Combining both**: context providers for passive recall + tools for active memory management

**Next:** Build a knowledge graph from unstructured documents.
