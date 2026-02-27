# Lab 11 - Hybrid Search

> **Advanced Lab** - This lab builds on the core workshop (Labs 4-9) with advanced search techniques.

In this lab, you'll learn how to combine fulltext (keyword) search with vector (semantic) search for improved retrieval accuracy. Hybrid search gives you the precision of keyword matching with the semantic understanding of vector search.

## Prerequisites

Before starting, make sure you have:
- Completed **Lab 0** (Azure sign-in)
- Completed **Lab 1** (Neo4j Aura setup)
- Completed **Lab 4** (Codespace setup with environment variables configured)
- Completed **Lab 8** (Knowledge graph built with embeddings)

## Lab Overview

This lab consists of two notebooks that demonstrate fulltext and hybrid search strategies:

### 01_fulltext_search.ipynb - Fulltext Search
Learn the fundamentals of keyword-based search with Neo4j fulltext indexes:
- Create and use fulltext indexes for exact keyword matching
- Perform fuzzy searches to handle typos and spelling variations
- Use wildcard and boolean operators for complex queries
- Combine fulltext search with graph traversal

### 02_hybrid_search.ipynb - Hybrid Search
Combine vector and fulltext search for best-of-both-worlds retrieval:
- Use the `HybridRetriever` from neo4j-graphrag package
- Tune the `alpha` parameter to balance keyword vs semantic matching
- Use `HybridCypherRetriever` for graph-enhanced hybrid results
- Compare pure vector, pure fulltext, and hybrid approaches

## Getting Started

1. Ensure the fulltext index exists by running:
   ```bash
   uv run python scripts/restore_neo4j.py --full-text
   ```
2. Open the first notebook: `01_fulltext_search.ipynb`
3. Work through each notebook in order

## Key Concepts

- **Fulltext Search**: Uses Lucene-based indexes for exact keyword matching, fuzzy search, and boolean operators
- **Hybrid Search**: Combines vector similarity scores with fulltext relevance scores for improved retrieval
- **Alpha Parameter**: Controls the balance between vector (alpha=1.0) and fulltext (alpha=0.0) scores
- **HybridRetriever**: Simple hybrid search returning matched nodes
- **HybridCypherRetriever**: Hybrid search with graph traversal for enriched context

## When to Use Each Search Type

| Search Type | Best For |
|-------------|----------|
| **Fulltext** | Known entity names, exact terms, filtering by specific keywords |
| **Vector** | Semantic similarity, concept matching, natural language questions |
| **Hybrid** | Queries with both specific names AND semantic concepts |

## Fulltext Query Syntax Reference

| Feature | Syntax | Example |
|---------|--------|---------|
| Basic search | `term` | `Apple` |
| Fuzzy search | `term~` | `Aplle~` |
| Wildcard | `term*` | `Micro*` |
| Boolean AND | `term1 AND term2` | `supply AND chain` |
| Boolean OR | `term1 OR term2` | `Apple OR Microsoft` |
| Boolean NOT | `term1 NOT term2` | `risk NOT financial` |
| Phrase | `"term1 term2"` | `"supply chain"` |

## Summary

Congratulations on completing all the labs! You have learned:

**Part 1 - No-Code (Labs 0-3):**
- Neo4j Aura setup
- Aura Agents
- Microsoft Foundry Agents

**Part 2 - Core Labs (Labs 4-9):**
- Codespace setup and environment configuration
- Building a simple Foundry Agent
- MAF context providers for automatic knowledge retrieval
- Agent memory with Neo4j Agent Memory
- Building knowledge graphs with embeddings
- Creating advanced agents with graph tools

**Part 3 - Advanced Labs (Labs 10-11):**
- Text2Cypher and entity extraction for advanced retrieval
- Hybrid search combining keyword and semantic matching

You now have the skills to build production-ready GraphRAG applications that combine the power of knowledge graphs with large language models.
