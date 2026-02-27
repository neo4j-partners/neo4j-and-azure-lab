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


# Neo4j Context Providers

---

## From Manual Tools to Automatic Context

In Lab 5, agents used **tools** — the agent decides when to call them.

Now we use **context providers** — they run automatically before every invocation, injecting knowledge graph context without the agent needing to decide.

**The agent doesn't "search" your knowledge graph. It already has the relevant context.**

---

## What is Neo4jContextProvider?

`Neo4jContextProvider` comes from the `agent-framework-neo4j` package. It connects your agent to a Neo4j knowledge graph and automatically searches for relevant content before each LLM call.

```python
from agent_framework_neo4j import Neo4jContextProvider

provider = Neo4jContextProvider(
    index_name="chunkEmbeddings",
    index_type="vector",
    embedder=embedder,
    top_k=5,
)
```

The provider handles connection, search, formatting, and injection.

---

## How before_run() Works

Each time the agent receives a query, the provider's `before_run()` executes:

```
1. Take recent messages from the conversation
       ↓
2. Concatenate message text into a search query
       ↓
3. Execute search against Neo4j index
       ↓
4. Format results with scores and metadata
       ↓
5. Inject formatted context via context.extend_messages()
```

The LLM then sees this context alongside the user's question.

---

## Three Search Modes

The provider supports three search strategies via `index_type`:

| Mode | Algorithm | How It Finds Content |
|------|-----------|---------------------|
| **`vector`** | Cosine similarity | Converts query to embedding, finds semantically similar chunks |
| **`fulltext`** | BM25 scoring | Tokenizes query, matches keywords in a fulltext index |
| **`hybrid`** | Combined | Runs both vector and fulltext, combines scores |

---

## When to Use Each Mode

| Mode | Best For | Example Questions |
|------|----------|-------------------|
| **Vector** | Conceptual, exploratory questions | "What is Apple's AI strategy?" |
| **Fulltext** | Specific terms and exact phrases | "Find mentions of cryptocurrency regulation" |
| **Hybrid** | Comprehensive retrieval | "What risks does BlackRock face from ESG?" |

**Vector** understands meaning. **Fulltext** matches keywords. **Hybrid** combines both.

---

## Configuration Options

```python
provider = Neo4jContextProvider(
    index_name="chunkEmbeddings",       # Neo4j index to search
    index_type="vector",                 # vector | fulltext | hybrid
    embedder=embedder,                   # Required for vector/hybrid
    top_k=5,                             # Number of results to return
    message_history_count=10,            # Recent messages to use as query
    context_prompt="## Knowledge Graph Context\n"
                   "Use the following information to answer:",
)
```

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `top_k` | 5 | Number of search results |
| `message_history_count` | 10 | How many recent messages to search with |
| `context_prompt` | Built-in | Text prepended to results to guide the LLM |

---

## Result Formatting

The provider formats each result for the LLM:

```
[Score: 0.892] [company: Apple Inc] [ticker: AAPL]
The Company's products include iPhone, Mac, iPad, and Apple Watch.
Apple faces competition from companies that offer similar hardware,
software, and services at competitive prices...
```

- **Score** — relevance ranking from the search
- **Metadata fields** — structured data from the graph (company, ticker, risks)
- **Text** — the matched content from the knowledge graph

---

## Creating an Embedder

For vector and hybrid search, you need an embedder:

```python
from agent_framework_neo4j import AzureAIEmbedder
from azure.identity import AzureCliCredential

embedder = AzureAIEmbedder(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=AzureCliCredential(),
    model=os.environ["AZURE_AI_EMBEDDING_NAME"],
)
```

`AzureAIEmbedder` converts text to vector embeddings using Azure AI. It implements the `neo4j-graphrag` Embedder interface.

---

## Retriever Selection Logic

The provider automatically selects the right retriever based on your configuration:

| index_type | retrieval_query | Retriever Used |
|------------|-----------------|----------------|
| `vector` | Not set | `VectorRetriever` |
| `vector` | Set | `VectorCypherRetriever` |
| `fulltext` | Any | `FulltextRetriever` |
| `hybrid` | Not set | `HybridRetriever` |
| `hybrid` | Set | `HybridCypherRetriever` |

When you add a `retrieval_query`, the provider upgrades to a Cypher-capable retriever.

---

## Summary

In this lesson, you learned:

- **`Neo4jContextProvider`** automatically searches your knowledge graph before each LLM call
- **Three search modes**: vector (semantic), fulltext (keyword), hybrid (combined)
- **`before_run()`** takes recent messages, searches the index, formats results, and injects context
- **Configuration** controls result count, message window, and prompt formatting
- **Retriever selection** is automatic based on `index_type` and `retrieval_query`

**Next:** Use graph enrichment to go beyond text chunks.
