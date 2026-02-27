# Lab 7 - Agent Memory

In this lab, you'll learn how to give agents **persistent memory** using the `neo4j-agent-memory` package with the Microsoft Agent Framework. Unlike the knowledge graph context providers in Lab 6 that retrieve from a static knowledge base, agent memory enables agents to remember conversations, learn user preferences, extract entities, and recall similar past interactions — all stored in Neo4j.

## Prerequisites

Before starting, make sure you have:
- Completed **Lab 0** (Azure sign-in)
- Completed **Lab 1** (Neo4j Aura setup)
- Completed **Lab 4** (Codespace setup with environment variables configured)
- Completed **Lab 6** (Context Providers)

## Lab Overview

This lab consists of two notebooks that demonstrate persistent agent memory:

### 01_memory_context_provider.ipynb - Memory Context Provider
Use Neo4j Agent Memory as a MAF context provider:
- Understand the three memory types: short-term, long-term, and reasoning
- Create a `Neo4jMicrosoftMemory` unified memory interface
- Configure the `Neo4jContextProvider` for automatic context injection
- See how conversation history persists across interactions
- Watch entities get extracted from conversations automatically

### 02_memory_tools_agent.ipynb - Agent with Memory Tools
Build an agent with explicit memory tools:
- Create callable memory tools with `create_memory_tools()`
- Let the agent search memory, save preferences, and recall facts
- Combine context providers with memory tools for full capability
- Build a conversational agent that learns and remembers

## Getting Started

### Select the Python Kernel

Before running any notebook, make sure you have the correct Python kernel selected:

1. Click **Select Kernel** in the top right of the notebook, then select **Python Environments...**
2. Select the **neo4j-azure-ai-workshop** environment (marked as Recommended)

### Work Through the Notebooks

1. Open the first notebook: `01_memory_context_provider.ipynb`
2. Work through each notebook in order
3. Notebook 2 builds on concepts from Notebook 1

## Key Concepts

- **Short-Term Memory**: Conversation history with message chains and semantic search
- **Long-Term Memory**: Entities, preferences, and facts extracted from conversations
- **Reasoning Memory**: Traces of past agent reasoning and tool usage for learning
- **Neo4jMicrosoftMemory**: Unified interface combining context provider and chat history store
- **Memory Tools**: Callable `FunctionTool` instances for explicit memory operations (search, save, recall)
- **Entity Extraction**: Automatic identification of people, organizations, and concepts from messages
- **`create_memory_tools()`**: Factory function that creates bound memory tools for an agent

## Memory Types

| Memory Type | What It Stores | How It Helps |
|-------------|---------------|--------------|
| **Short-Term** | Recent messages, conversation chains | Maintains conversation context |
| **Long-Term** | Entities, preferences, facts | Personalizes responses over time |
| **Reasoning** | Past task traces, tool usage | Learns from previous successes/failures |

## Next Steps

After completing this lab, continue to [Lab 8 - Building a Knowledge Graph](../Lab_8_Knowledge_Graph) to learn how to build knowledge graphs from unstructured documents with embeddings and retrieval strategies.
