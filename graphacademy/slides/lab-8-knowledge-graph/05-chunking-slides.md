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


# Chunking Strategies

---

## Why Chunking Matters

LLMs have context limits. You can't pass an entire 200-page SEC filing to an LLM for entity extraction.

Documents must be broken into smaller pieces—**chunks**—that fit within processing limits.

**But chunking isn't just a technical necessity.** How you chunk documents affects both:
- **Extraction quality**
- **Retrieval quality**

---

## The Dual Impact of Chunk Size

Chunk size creates a fundamental trade-off:

**For Entity Extraction:**
- Larger chunks provide more context for understanding entities
- The LLM sees more surrounding text, making better extraction decisions
- "The Company" can be resolved to "Apple Inc" when full context is visible

**For Retrieval:**
- Smaller chunks enable more precise matches
- When searching, you want the most relevant *portion*, not a huge blob
- Less irrelevant content mixed with relevant content

---

## The Trade-off Illustrated

<div style="display: flex; gap: 2rem;">

<div style="flex: 1;">

### Large Chunks (2000 chars)

```
[Full paragraph about Apple's
risk factors, mentioning
cybersecurity, supply chain,
and regulatory risks with
full context about each]
```

- ✅ Better entity extraction
- ❌ Less precise retrieval
- ❌ Returns more than needed

</div>

<div style="flex: 1;">

### Small Chunks (200 chars)

```
[Apple faces cybersecurity...]
[Supply chain disruptions...]
[Regulatory changes in...]
```

- ❌ Less context for extraction
- ✅ More precise retrieval
- ✅ Focused search results

</div>

</div>

---

## Chunk Size Parameters

The `FixedSizeSplitter` has two key parameters:

**`chunk_size`**: Maximum number of characters per chunk

**`chunk_overlap`**: Characters shared between consecutive chunks

```python
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter

splitter = FixedSizeSplitter(chunk_size=500, chunk_overlap=50)
```

Overlap ensures context isn't lost at chunk boundaries.

---

## Configuring the Pipeline

Pass a custom text splitter to SimpleKGPipeline:

```python
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter

# Create a splitter with your preferred settings
splitter = FixedSizeSplitter(chunk_size=500, chunk_overlap=50)

# Pass it to the pipeline
pipeline = SimpleKGPipeline(
    driver=driver,
    llm=llm,
    embedder=embedder,
    entities=entities,
    relations=relations,
    text_splitter=splitter,  # Custom splitter
)
```

---

## Typical Chunk Sizes

| Chunk Size | Best For |
|------------|----------|
| 200-500 chars | High-precision retrieval, FAQ-style content |
| 500-1000 chars | Balanced extraction and retrieval |
| 1000-2000 chars | Context-heavy extraction, narrative documents |
| 2000+ chars | Maximum context, fewer chunks |

For SEC filings with complex, interconnected information, **500-1000 characters** often provides a good balance.

---

## Evaluating Chunk Quality

After chunking, evaluate the results:

```cypher
// Check chunk count per document
MATCH (d:Document)<-[:FROM_DOCUMENT]-(c:Chunk)
RETURN d.path, count(c) AS chunkCount
ORDER BY chunkCount DESC

// Check chunk size distribution
MATCH (c:Chunk)
RETURN
    min(size(c.text)) AS minSize,
    max(size(c.text)) AS maxSize,
    avg(size(c.text)) AS avgSize
```

---

## What to Look For

**Good chunks:**
- Reasonable count per document
- Consistent sizes
- Contain coherent, complete thoughts

**Signs of problems:**
- Too few chunks → may be too large
- Highly variable sizes → inconsistent processing
- Incomplete sentences → overlap may be too small

---

## Experiment and Iterate

The best chunk size depends on:
- Document type and structure
- Query patterns you expect
- Balance between extraction and retrieval needs

**Start with a moderate size (500-800 characters), evaluate results, and adjust.**

---

## Summary

In this lesson, you learned:

- **Chunking breaks documents** into processable pieces
- **Chunk size affects both** entity extraction quality and retrieval precision
- **Larger chunks** = better context for extraction, less precise retrieval
- **Smaller chunks** = more precise retrieval, less context for extraction
- **Overlap** helps preserve context across chunk boundaries
- **Experimentation** is key to finding the right balance

**Next:** Learn about entity resolution—handling duplicate entities.
