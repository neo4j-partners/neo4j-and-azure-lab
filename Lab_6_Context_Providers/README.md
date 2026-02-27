# Lab 6 - MAF Context Providers

In this lab, you'll learn how to use **context providers** with the Microsoft Agent Framework (MAF) to automatically inject knowledge graph context into agent conversations. Instead of defining tools that the agent must explicitly call, context providers run automatically before each agent invocation, enriching the LLM with relevant information from your Neo4j knowledge graph.

## What is Neo4jContextProvider?

The notebooks in this lab use `Neo4jContextProvider` from the [`agent-framework-neo4j`](https://github.com/neo4j-labs/agent-framework-neo4j) package. It's a MAF context provider that connects your agent to a Neo4j knowledge graph, automatically searching for relevant content and injecting it into the LLM's context window before every invocation.

### How It Works

When the agent receives a query, the provider's `before_run()` hook:

1. Takes the most recent messages from the conversation (configurable via `message_history_count`, default 10)
2. Concatenates the message text into a single search query
3. Executes a search against a Neo4j index (vector, fulltext, or hybrid)
4. Formats the results with scores and metadata (e.g., `[Score: 0.892] [company: Apple Inc]`)
5. Injects the formatted context into the agent's session via `context.extend_messages()`

The LLM then sees this context alongside the user's question and can ground its answer in real knowledge graph data.

### Search Modes

The provider supports three search modes via the `index_type` parameter:

| Mode | How It Works | Best For |
|------|-------------|----------|
| **`vector`** | Converts query to an embedding, searches a vector index by cosine similarity | Finding conceptually related content even when keywords don't match |
| **`fulltext`** | Tokenizes query, searches a fulltext index using BM25 scoring | Finding content with specific terms and exact phrases |
| **`hybrid`** | Runs both vector and fulltext searches, combines scores | Comprehensive retrieval combining semantic understanding and keyword matching |

### Graph Enrichment

The provider's most powerful feature is **graph enrichment** via the `retrieval_query` parameter. After the initial index search finds matching nodes, a custom Cypher query traverses the graph to pull in related entities — company names, products, risk factors, executives — giving the LLM much richer context than the matched text alone.

The provider automatically selects the right underlying retriever based on your configuration:

| index_type | retrieval_query | Retriever Used |
|------------|-----------------|----------------|
| `vector` | Not set | `VectorRetriever` |
| `vector` | Set | `VectorCypherRetriever` |
| `fulltext` | Any | `FulltextRetriever` |
| `hybrid` | Not set | `HybridRetriever` |
| `hybrid` | Set | `HybridCypherRetriever` |

## Prerequisites

Before starting, make sure you have:
- Completed **Lab 0** (Azure sign-in)
- Completed **Lab 1** (Neo4j Aura setup)
- Completed **Lab 4** (Codespace setup with environment variables configured)
- Completed **Lab 5** (Foundry Agents — tools and context provider basics)

## Lab Overview

This lab consists of three notebooks that progressively demonstrate context providers:

### 01_vector_context_provider.ipynb - Vector Search Provider
Add semantic search capabilities using embeddings:
- Create an `AzureAIEmbedder` for generating query embeddings
- Configure the provider with vector search (`index_type="vector"`)
- Understand how semantic similarity finds conceptually related content

### 02_graph_enriched_provider.ipynb - Graph-Enriched Provider
Combine vector search with graph traversal for rich context:
- Define a `retrieval_query` that traverses graph relationships
- Use `VectorCypherRetriever` internally for graph-enriched results
- Get company names, products, and risk factors alongside search results
- Build a fully context-aware agent with graph-enriched knowledge

### 03_fulltext_context_provider.ipynb - Fulltext Search Provider (Optional)
Use keyword-based search to automatically inject context:
- Understand the MAF context provider lifecycle (`before_run` / `after_run`)
- Create a `Neo4jContextProvider` with fulltext search
- See how context is automatically injected before each agent response
- Compare agent responses with and without context

## Getting Started

### Select the Python Kernel

Before running any notebook, make sure you have the correct Python kernel selected:

1. Click **Select Kernel** in the top right of the notebook, then select **Python Environments...**
2. Select the **neo4j-azure-ai-workshop** environment (marked as Recommended)

### Work Through the Notebooks

1. Open the first notebook: `01_vector_context_provider.ipynb`
2. Work through each notebook in order
3. Each notebook builds on concepts from the previous one

## Key Concepts

- **Context Provider**: A MAF component that runs automatically before/after agent invocations to inject or extract context
- **`before_run()`**: Called before the LLM is invoked — retrieves and injects context from Neo4j
- **`after_run()`**: Called after the LLM responds — can process or store response data
- **Neo4jContextProvider**: Uses neo4j-graphrag retrievers to search your knowledge graph
- **Index Types**: `fulltext` (keyword), `vector` (semantic), `hybrid` (combined)
- **Graph Enrichment**: Custom Cypher queries that traverse relationships beyond the matched nodes
- **`context_prompt`**: Custom text prepended to search results to guide the LLM

## Context Provider vs Tools

| Aspect | Context Provider | Tools |
|--------|-----------------|-------|
| **Invocation** | Automatic (every request) | Agent decides when to call |
| **Visibility** | Transparent to user | Visible in agent reasoning |
| **Best For** | Background knowledge enrichment | Specific actions and queries |
| **Control** | Framework-managed | Agent-managed |

## Next Steps

After completing this lab, continue to [Lab 7 - Agent Memory](../Lab_7_Agent_Memory) to learn how to give agents persistent memory using Neo4j Agent Memory context providers.
