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


# Graph-Enriched Context

---

## Why Vector Search Alone Isn't Enough

Vector search returns **text chunks** — fragments of documents ranked by semantic similarity.

But chunks are isolated. They don't tell you:
- Which **company** the chunk belongs to
- What **products** that company sells
- What **risks** are connected to the topic
- Which **executives** are involved

**The knowledge graph has this information. We just need to traverse it.**

---

## The retrieval_query Parameter

Adding a `retrieval_query` to your provider enables **graph enrichment**:

```python
provider = Neo4jContextProvider(
    index_name="chunkEmbeddings",
    index_type="vector",
    embedder=embedder,
    retrieval_query=retrieval_query,   # Custom Cypher for traversal
    top_k=5,
)
```

When set, the provider uses `VectorCypherRetriever` instead of `VectorRetriever` — performing vector search first, then traversing the graph from each matched node.

---

## The Two-Step Process

```
Step 1: Vector Search
    Query embedding → find similar chunks → ranked by cosine similarity
        ↓
    Returns: node (matched chunk) + score

Step 2: Graph Traversal
    For each matched node, execute the retrieval_query
        ↓
    Traverse relationships: chunk → document → company → risks, products
        ↓
    Returns: enriched context with structured entity data
```

The chunk is the **anchor** — you traverse outward from what vector search found.

---

## Example Retrieval Query

```cypher
MATCH (node)-[:FROM_DOCUMENT]->(doc:Document)<-[:FILED]-(company:Company)
OPTIONAL MATCH (company)-[:FACES_RISK]->(risk:RiskFactor)
WITH node, score, company, doc, collect(DISTINCT risk.name)[0..5] AS risks
OPTIONAL MATCH (company)-[:MENTIONS]->(product:Product)
WITH node, score, company, doc, risks,
     collect(DISTINCT product.name)[0..5] AS products
RETURN
    node.text AS text,
    score,
    company.name AS company,
    company.ticker AS ticker,
    risks,
    products
ORDER BY score DESC
```

**`node`** and **`score`** come from the vector search. The rest is graph traversal.

---

## Before and After

**Without graph enrichment (plain vector search):**
```
The Company designs, manufactures, and markets smartphones,
personal computers, tablets, wearables, and accessories...
```

**With graph enrichment:**
```
[Score: 0.912] [company: Apple Inc] [ticker: AAPL]
[risks: Competition, Supply Chain Disruption, Regulatory Changes]
[products: iPhone, Mac, iPad, Apple Watch, AirPods]
The Company designs, manufactures, and markets smartphones,
personal computers, tablets, wearables, and accessories...
```

The LLM now has structured context alongside the text.

---

## Writing Retrieval Queries

**Rules for retrieval queries:**
- Use `node` and `score` — provided by the index search
- Must return at least `text` and `score` columns
- Use `OPTIONAL MATCH` for relationships that may not exist
- Use `ORDER BY score DESC` to maintain relevance ranking
- Limit collected lists (e.g., `[0..5]`) to control context size

**The query defines what "enriched context" means for your use case.**

---

## Putting It Together

```python
async with Neo4jContextProvider(
    index_name="chunkEmbeddings",
    index_type="vector",
    embedder=embedder,
    retrieval_query=retrieval_query,
    top_k=5,
) as provider:
    agent = client.as_agent(
        name="graph-enriched-agent",
        model=os.environ["AZURE_AI_MODEL_NAME"],
        instructions="You answer questions about SEC company filings.",
        context_providers=[provider],
    )
```

The agent gets graph-enriched context automatically — no tool calls needed.

---

## Summary

In this lesson, you learned:

- **Vector search alone** returns isolated text chunks without entity context
- **`retrieval_query`** enables Cypher traversal from matched chunks to related entities
- **Two-step process**: vector search finds nodes, Cypher traversal enriches with relationships
- **`node` and `score`** are provided by the index search; your query traverses from there
- **`OPTIONAL MATCH`** and list limits keep queries robust and context manageable
- **Result**: the LLM sees company names, products, risks, and more alongside the text

**Next:** Give agents persistent memory with Neo4j Agent Memory.
