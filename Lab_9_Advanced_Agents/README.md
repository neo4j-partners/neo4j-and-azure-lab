# Lab 9 - Advanced Agents

In this lab, you'll build increasingly capable agents using Microsoft Foundry that use your Neo4j knowledge graph as a tool. You'll add sophisticated tools including vector search with graph traversal and natural language to Cypher query generation.

## Prerequisites

Before starting, make sure you have:
- Completed **Lab 0** (Azure sign-in)
- Completed **Lab 1** (Neo4j Aura setup)
- Completed **Lab 4** (Codespace setup with environment variables configured)
- Completed **Lab 8** (Knowledge graph built with embeddings)

## Lab Overview

This lab consists of two notebooks that build increasingly capable agents:

### 02_vector_graph_agent.ipynb - Vector + Graph Agent
Add semantic search capabilities with graph context:
- Create a `VectorCypherRetriever` tool for the agent
- Define retrieval queries that traverse graph relationships
- Combine vector search with structured graph data
- Let the agent choose between schema and document retrieval tools

### 03_text2cypher_agent.ipynb - Multi-Tool Agent with Text2Cypher
Build a powerful multi-tool agent:
- Add a Text2Cypher tool for natural language database queries
- Configure custom Cypher generation prompts
- Give the agent three tools: schema, semantic search, and database queries
- Watch the agent intelligently select tools based on question type

## Getting Started

1. Open the first notebook: `02_vector_graph_agent.ipynb`
2. Work through each notebook in order
3. Each notebook adds new tools to the agent

### Running Locally

If you prefer to run the labs from the terminal instead of notebooks, first ensure everything is set up properly:

```bash
uv run setup_env.py
```

Then run the workshop menu:

```bash
cd financial_data_load && uv run python main.py solutions
```

Menu items 9 and 10 correspond to notebooks 2 and 3 respectively.

## Key Concepts

- **Agent**: An AI system that can use tools to accomplish tasks autonomously
- **Tools**: Python functions with docstrings that agents can invoke based on user queries
- **Microsoft Agent Framework**: Azure's framework for building agents with Microsoft Foundry
- **Tool Selection**: The agent reads tool names and docstrings to decide which tool to use
- **Streaming**: Real-time display of agent responses as they're generated

## When to Use Each Tool

| Tool | Best For |
|------|----------|
| **Schema Tool** | Understanding graph structure, planning queries |
| **Vector + Graph Tool** | Semantic questions requiring relationship context |
| **Text2Cypher Tool** | Specific facts, counts, and structured queries |

## Example Questions by Tool Type

**Schema queries:**
- "How does the graph model relate financial documents to risk factors?"
- "What questions can I answer using this graph database?"

**Semantic search queries:**
- "What are the main risk factors mentioned in Apple's documents?"
- "Summarize Microsoft's business strategy"

**Text2Cypher queries:**
- "Which company faces the most risk factors?"
- "What products does NVIDIA mention?"
- "How many risk factors does Apple face?"

## Next Steps

**Congratulations!** You have completed the core workshop (Labs 4-9). You now know how to:
- Build a simple agent with Microsoft Foundry
- Use context providers for automatic knowledge retrieval
- Give agents persistent memory with Neo4j Agent Memory
- Build knowledge graphs from unstructured documents
- Implement vector and graph-enhanced retrieval strategies
- Create intelligent agents that automatically choose the right tool for each question

For more advanced topics, continue to the **Advanced Labs**:
- [Lab 10 - Advanced Retrievers](../Lab_10_Retrievers) - Text2Cypher, entity extraction, and full dataset exploration
- [Lab 11 - Hybrid Search](../Lab_11_Hybrid_Search) - Combining keyword and semantic search
