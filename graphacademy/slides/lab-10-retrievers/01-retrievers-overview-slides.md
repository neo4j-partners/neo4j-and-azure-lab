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


# Neo4j GraphRAG Retrievers Overview

---

## From Knowledge Graph to Answers

You have a knowledge graph with:
- **Entities**: Companies, products, risks, executives
- **Relationships**: OWNS, FACES_RISK, MENTIONS, WORKS_FOR
- **Embeddings**: Vector representations for semantic search

**The question**: How do you *retrieve* the right information to answer user questions?

---

## What is a Retriever?

A **retriever** searches your knowledge graph and returns relevant information.

**Three retrieval patterns:**

| Retriever | What It Does |
|-----------|--------------|
| **Vector** | Semantic similarity search across text chunks |
| **Vector Cypher** | Semantic search + graph traversal for relationships |
| **Text2Cypher** | Natural language → Cypher query for precise facts |

Each pattern excels at different question types.

---

## The GraphRAG Class

Retrievers work with the **GraphRAG** class, which combines retrieval with LLM generation:

```
User Question
    ↓
Retriever finds relevant context
    ↓
Context passed to LLM
    ↓
LLM generates grounded answer
```

The retriever's job is finding the right context. The LLM's job is generating a coherent answer from that context.

---

## Vector Retriever

**How it works:**
- Converts your question to an embedding
- Finds chunks with similar embeddings
- Returns semantically related content

**Best for:**
- "What is Apple's strategy?"
- "Tell me about cybersecurity threats"
- Conceptual, exploratory questions

**Limitation:** Returns text chunks only—no entity relationships.

---

## Vector Cypher Retriever

**How it works:**
- Vector search finds relevant chunks
- Custom Cypher query traverses from chunks to related entities
- Returns content + structured data

**Best for:**
- "Which asset managers are affected by crypto regulations?"
- "What risks do tech companies face?"
- Questions needing both content and relationships

**Key insight:** The chunk is the anchor—you traverse from what vector search finds.

---

## Text2Cypher Retriever

**How it works:**
- LLM converts natural language to Cypher
- Query executes against the graph
- Returns precise, structured results

**Best for:**
- "How many risk factors does Apple face?"
- "List all companies owned by BlackRock"
- Counts, lists, specific lookups

**Limitation:** Question must map to graph schema.

---

## Choosing the Right Retriever

| Question Pattern | Best Retriever |
|-----------------|----------------|
| "What is...", "Tell me about..." | Vector |
| "Which [entities] are affected by..." | Vector Cypher |
| "How many...", "List all..." | Text2Cypher |
| Content about topics | Vector |
| Content + relationships | Vector Cypher |
| Facts, counts, aggregations | Text2Cypher |

---

## The Decision Framework

**Ask yourself:**

1. **Am I looking for content or facts?**
   - Content → Vector or Vector Cypher
   - Facts → Text2Cypher

2. **Do I need related entities?**
   - No → Vector
   - Yes → Vector Cypher

3. **Is this about relationships?**
   - Traversals → Vector Cypher or Text2Cypher
   - Semantic → Vector

---

## Summary

In this lesson, you learned:

- **Retrievers** search and return relevant information from your knowledge graph
- **Vector Retriever**: Semantic similarity search across chunks
- **Vector Cypher Retriever**: Semantic search + graph traversal
- **Text2Cypher Retriever**: Natural language to precise database queries
- **Each excels at different question types**—choosing the right one matters

**Next:** Deep dive into each retriever type.
