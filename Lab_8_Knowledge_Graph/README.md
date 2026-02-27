# Lab 8 - Building a Knowledge Graph

In this lab, you'll learn how to build a knowledge graph in Neo4j for GraphRAG (Graph Retrieval-Augmented Generation) applications. You'll cover the complete pipeline from loading text data and generating embeddings, through to implementing retrieval strategies that leverage graph relationships.

## Prerequisites

Before starting, make sure you have:
- Completed **Lab 0** (Azure sign-in)
- Completed **Lab 1** (Neo4j Aura setup)
- Completed **Lab 4** (Codespace setup with environment variables configured)

## Lab Overview

This lab consists of two notebooks that cover the full GraphRAG workflow:

### 01_data_and_embeddings.ipynb - Data Preparation
Build the foundation for GraphRAG by preparing your knowledge graph:
- Understand the Document → Chunk graph structure
- Connect to Neo4j from a Jupyter notebook
- Create Document and Chunk nodes with relationships
- Generate embeddings using Microsoft Foundry
- Create a vector index in Neo4j
- Perform similarity search to verify your setup

### 02_graphrag_retrievers.ipynb - Retrieval Strategies
Learn retrieval patterns from simple to graph-enhanced:
- Set up a VectorRetriever using Neo4j's vector index
- Use GraphRAG to combine vector search with LLM-generated answers
- Create custom Cypher queries with VectorCypherRetriever
- Discover relationships like shared risks among companies
- Compare standard vs. graph-enhanced retrieval results

## Getting Started

### Select the Python Kernel

Before running any notebook, make sure you have the correct Python kernel selected:

1. Click **Select Kernel** in the top right of the notebook, then select **Python Environments...**

   ![Select Kernel](images/select%20kernel.png)

2. Select the **neo4j-azure-ai-workshop** environment (marked as Recommended)

   ![Select neo4j-azure-ai-workshop](images/neo4j-azure-ai-workshop.png)

### Work Through the Notebooks

1. Open the first notebook: `01_data_and_embeddings.ipynb`
2. Work through each notebook in order
3. Notebook 2 assumes you've completed Notebook 1

## Key Concepts

- **Chunks**: Smaller pieces of text split from documents for efficient retrieval
- **Embeddings**: Numerical vectors that capture semantic meaning of text
- **Vector Index**: Enables fast similarity search across embeddings
- **VectorRetriever**: Simple semantic search over embedded chunks
- **VectorCypherRetriever**: Graph-enhanced retrieval using custom Cypher queries
- **GraphRAG**: Combining retrieval with LLM generation for context-aware answers

## Next Steps

After completing this lab, continue to [Lab 9 - Advanced Agents](../Lab_9_Advanced_Agents) to build advanced agents that use your knowledge graph as a tool.
