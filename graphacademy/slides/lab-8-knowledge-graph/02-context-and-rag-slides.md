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


# Context and the Limits of Traditional RAG

---

## The Power of Context

Providing context in prompts dramatically improves LLM responses.

**When you include relevant information, the model can:**
- Generate accurate summaries grounded in actual documents
- Answer questions about your specific data
- Reduce hallucination by having facts to reference

This insight leads to **Retrieval-Augmented Generation (RAG)**.

---

## How Traditional RAG Works

Traditional RAG follows a simple pattern:

1. **Index documents**: Break documents into chunks and create embeddings
2. **Receive query**: User asks a question
3. **Retrieve context**: Find chunks with embeddings similar to the query
4. **Generate response**: Pass retrieved chunks to LLM as context

This works well for many use cases. But it has fundamental limitations.

---

## The Problem with Traditional RAG

Traditional RAG treats documents as isolated, unstructured blobs.

**What traditional RAG sees:**
```
Chunk 1: "Apple Inc. faces cybersecurity risks including..."
Chunk 2: "BlackRock Inc. holds shares in technology companies..."
Chunk 3: "The semiconductor supply chain impacts..."
```

**What traditional RAG misses:**
- Which specific companies does BlackRock own?
- Do any of those companies face cybersecurity risks?
- How are supply chain issues connected to specific products?

---

## Retrieves Similar Content, Not Connected Information

Traditional RAG can find text about cybersecurity and text about BlackRock.

**But it can't tell you:**
- Which asset managers are exposed to cybersecurity risks through their holdings

**Why?** Each chunk is independent—there's no understanding of how information connects.

---

## Questions Traditional RAG Can't Answer

| Question | Why Traditional RAG Struggles |
|----------|------------------------------|
| "Which asset managers own companies facing cyber risks?" | Requires connecting ownership data to risk mentions |
| "What products are mentioned by companies that share risk factors?" | Requires finding shared entities across documents |
| "How many companies mention supply chain issues?" | Requires aggregation, not similarity search |
| "What executives work for companies in the tech sector?" | Requires traversing entity relationships |

These questions need *structured context* that preserves relationships.

---

## From Unstructured to Structured

**The core insight:** Information isn't truly unstructured.

Documents contain:
- **Entities**: Companies, people, products, risks
- **Relationships**: Owns, faces, mentions, works for

Traditional RAG ignores this structure. It treats a document as a bag of words to embed and search.

---

## The GraphRAG Solution

GraphRAG extracts structure, creating a *knowledge graph* that preserves:

- **Entities**: The things mentioned in documents
- **Relationships**: How those things connect
- **Properties**: Attributes and details about entities

**Traditional RAG asks**: "What chunks are similar to this query?"

**GraphRAG asks**: "What entities and relationships are relevant to this query?"

---

## Three Retrieval Patterns

GraphRAG enables three retrieval patterns:

| Pattern | What It Does |
|---------|--------------|
| **Vector search** | Find semantically similar content (what traditional RAG does) |
| **Graph traversal** | Follow relationships from relevant content to connected entities |
| **Database queries** | Answer precise questions about entities and relationships |

The combination is more powerful than any single approach.

---

## Summary

In this lesson, you learned:

- **Context improves LLM responses** by providing relevant information
- **Traditional RAG** retrieves similar chunks based on vector similarity
- **The limitation**: Traditional RAG treats documents as isolated blobs, missing relationships
- **Questions requiring relationships** can't be answered with similarity search alone
- **GraphRAG** extracts structure from documents, preserving entities and relationships

**Next:** Learn how to transform documents into knowledge graphs.
