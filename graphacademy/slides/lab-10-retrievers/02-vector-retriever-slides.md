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


# Vector Retriever

---

## What is a Vector Retriever?

The **simplest retriever**—finds content by meaning, not keywords.

**How it works:**
1. Convert your question to an embedding
2. Search vector index for similar chunk embeddings
3. Return the most semantically similar chunks

**Key insight:** "Cybersecurity threats" finds content about "data breaches" and "hacking risks" even without exact word matches.

---

## Creating a Vector Retriever

```python
from neo4j_graphrag.retrievers import VectorRetriever

vector_retriever = VectorRetriever(
    driver=driver,                    # Neo4j connection
    index_name='chunkEmbeddings',     # Vector index name
    embedder=embedder,                # Embedding model
    return_properties=['text']        # Properties to return
)
```

**Components:**
- **Driver**: Connection to Neo4j
- **Index**: Where embeddings are stored
- **Embedder**: Model that creates embeddings (e.g., OpenAI)

---

## Performing a Search

```python
query = "What are the risks that Apple faces?"

results = vector_retriever.search(
    query_text=query,
    top_k=5  # Return 5 most similar chunks
)

for record in results.records:
    print(f"Score: {record['score']:.4f}")
    print(f"Text: {record['text'][:200]}...")
```

**Each result includes:**
- **text**: The chunk content
- **score**: Similarity score (0-1, higher = more similar)

---

## Understanding Similarity Scores

| Score Range | Interpretation |
|-------------|----------------|
| 0.95-1.0 | Extremely similar (near-exact match) |
| 0.90-0.95 | Highly relevant |
| 0.85-0.90 | Relevant |
| 0.80-0.85 | Moderately relevant |
| < 0.80 | Weak relevance |

Higher scores indicate stronger semantic matches.

---

## Best For

**Use Vector Retriever when:**

- Finding conceptually similar content
- Questions like "What is...", "Tell me about...", "Explain..."
- Exploratory questions about topics
- When exact keywords don't match but meaning does

**Example questions:**
- "What is Apple's business strategy?"
- "Describe cybersecurity threats"
- "What challenges do tech companies face?"

---

## Limitations

**Vector Retriever returns text only:**

- No entity relationships
- No structured data from the graph
- Can't aggregate across entities
- Can't traverse connections

**Example limitation:**
- Question: "What risks does Apple face?"
- Returns: Chunks about risks (may not be Apple-specific)
- Missing: Structured FACES_RISK relationships

**When you need more:** Use Vector Cypher Retriever.

---

## The top_k Parameter

**Controls how many results to return:**

| top_k | Trade-off |
|-------|-----------|
| 1-3 | Fastest, most relevant only |
| 5-10 | Balanced coverage |
| 15-20 | Maximum coverage, may include less relevant |

**Rule of thumb:** Start with 5, adjust based on results.

---

## Summary

Vector Retriever is your foundation for semantic search:

- **Converts queries to embeddings** for meaning-based search
- **Returns semantically similar chunks** regardless of keywords
- **Best for** content questions, topic exploration
- **Limitation:** No graph relationships or structured data

**Next:** Learn how Vector Cypher Retriever adds graph intelligence.
