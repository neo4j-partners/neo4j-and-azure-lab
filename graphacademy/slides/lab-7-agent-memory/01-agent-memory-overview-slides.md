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


# Neo4j Agent Memory

---

## The Problem: Agents Forget

In Lab 6, context providers injected knowledge from a **static** knowledge graph.

But the agent itself has no memory:
- It doesn't remember what you discussed last session
- It can't learn your preferences over time
- It forgets which approaches worked and which failed
- Every conversation starts from zero

**Agents need persistent, searchable memory.**

---

## What is neo4j-agent-memory?

The `neo4j-agent-memory` package is a **graph-native memory system** for AI agents. It stores memory in Neo4j, making it persistent, searchable, and connected.

Unlike the knowledge graph context providers in Lab 6 that retrieve from a pre-built knowledge base, **agent memory is dynamic** — it grows with every conversation.

**Three types of memory work together:**
- Short-term memory
- Long-term memory
- Reasoning memory

---

## Short-Term Memory

Stores **conversation history** as Message nodes with embeddings.

**What it stores:**
- Messages with role (user/assistant/system) and content
- Embedding vectors for each message
- Conversation grouping by session ID

**What it enables:**
- Semantic search over past messages (not just replay in order)
- Find the most relevant past exchanges for the current question
- Maintain conversation context across turns

---

## Long-Term Memory

Stores **structured knowledge** extracted from conversations.

**Three kinds of long-term memory:**

| Type | What It Stores | Example |
|------|---------------|---------|
| **Entities** | People, organizations, locations, concepts | "Apple Inc", "Tim Cook", "Cupertino" |
| **Facts** | Subject-Predicate-Object triples | "Apple → manufactures → iPhone" |
| **Preferences** | User-specific information with category | "Prefers Python over Java" |

Entities are **automatically deduplicated** using configurable strategies: exact match, fuzzy match, semantic similarity, or composite.

---

## Reasoning Memory

Stores **traces of past agent behavior** for learning.

**What it captures:**
- Task description and outcome (success/failure)
- Each reasoning step the agent took
- Tool calls with parameters, results, and duration
- Timing information for performance tracking

**What it enables:**
- When the agent encounters a similar task, it retrieves past traces
- Learn from what worked and what failed
- Track tool reliability and performance over time

---

## Three Memory Types Compared

| Memory Type | What It Stores | How It Helps |
|-------------|---------------|--------------|
| **Short-Term** | Recent messages and conversation chains | Maintains conversation context |
| **Long-Term** | Entities, facts, preferences | Personalizes responses over time |
| **Reasoning** | Past task traces and tool usage | Learns from previous experience |

**Short-term** is what happened. **Long-term** is what was learned. **Reasoning** is how things were done.

---

## The Graph Data Model

All memory is stored as a connected graph in Neo4j:

```
(Conversation)─[:HAS_MESSAGE]─>(Message)
                                    │
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              [:MENTIONS]    [:EXTRACTED_FROM]  [:INITIATED_BY]
                    ↓               ↓               ↓
               (Entity)         (Entity)    (ReasoningTrace)
                    │                           │
              [:RELATED_TO]              [:HAS_STEP]
                    ↓                           ↓
               (Entity)              (ReasoningStep)
                                            │
                                      [:USES_TOOL]
                                            ↓
                                        (ToolCall)
```

Entities, messages, and reasoning traces are all connected — enabling rich graph traversal.

---

## How Memory Differs from Lab 6

| Aspect | Lab 6: Knowledge Graph Context | Lab 7: Agent Memory |
|--------|-------------------------------|---------------------|
| **Data source** | Pre-built knowledge graph (SEC filings) | Dynamic, grows from conversations |
| **Content** | Document chunks, entities from filings | Messages, preferences, facts, traces |
| **Changes** | Static (updated by data pipeline) | Evolves with every interaction |
| **Purpose** | Ground answers in domain knowledge | Remember and personalize over time |

Both use `Neo4jContextProvider` — but with different data and different goals.

---

## Summary

In this lesson, you learned:

- **Agents are stateless by default** — they forget everything between sessions
- **`neo4j-agent-memory`** provides graph-native persistent memory
- **Short-term memory**: conversation history with semantic search
- **Long-term memory**: entities, facts (SPO triples), and preferences
- **Reasoning memory**: traces of past tool usage and outcomes
- **All memory is stored in Neo4j** as a connected graph
- **Memory is dynamic** — it grows with every conversation, unlike static knowledge graphs

**Next:** Use memory context providers and memory tools.
