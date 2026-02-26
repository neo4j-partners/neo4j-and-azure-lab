# Neo4j And Azure Lab - GraphRAG Workshop Program Template, 2026

## Program Name

Build Generative AI & GraphRAG Agents with Neo4j and Microsoft Foundry

## Landing Page

Join us for an immersive hands-on workshop with Neo4j and GenAI agents without writing any code. You'll set up a Neo4j Aura instance, explore a pre-built knowledge graph of SEC 10-K financial filings, and build AI agents that use GraphRAG with both Neo4j Aura Agents and Microsoft Foundry's visual tools. For those ready to go deeper, we'll dive into a developer section where you'll build and deploy intelligent multi-tool agents using the Microsoft Agent Framework. Whether you're a seasoned developer, an AI enthusiast, or just curious about the future of GenAI, this is your hands-on introduction to explainable, relationship-aware AI.

## Workshop Overview

This workshop will give participants real-world experience with combining Neo4j's graph database platform with Microsoft Foundry AI capabilities to build explainable, context-aware AI applications using GraphRAG and agentic patterns.

Participants will work with a real-world dataset—SEC 10-K financial filings—to experience how knowledge graphs enhance AI applications with structured context and relationship-aware retrieval.

Through a series of guided exercises, attendees will:

- Deploy and explore Neo4j Aura, the fully managed cloud graph platform
- Build no-code AI agents with Neo4j Aura Agents
- Create AI agents using Microsoft Foundry with MCP tools
- Understand foundational GenAI and retrieval strategies
- Build GraphRAG pipelines using Microsoft Foundry APIs for embeddings and text generation
- Create intelligent multi-tool agents using the Microsoft Agent Framework
- Deploy agents to Microsoft Foundry for production use
- Implement advanced retrieval patterns including Text2Cypher and hybrid search

---

## Lab Agenda

### Part 1 – No-Code Getting Started (Beginner Friendly)

Get hands-on with Neo4j and AI agents without writing any code. You'll set up a Neo4j Aura instance, explore a pre-built knowledge graph of SEC 10-K financial filings, and build AI agents using both Neo4j Aura Agents and Microsoft Foundry's visual tools. By the end of Part 1, you'll have working agents that can answer natural language questions about company financials, risks, and relationships.

#### Introductions & Lecture — Introduction to Neo4j Aura and AI Agents

- Neo4j Aura: A fully managed, cloud-native graph database platform
- Neo4j Aura on Azure: Native deployment via Azure Marketplace with seamless integration
- Aura Agents: Build, test, and deploy AI agents grounded in your graph data without writing code
- Microsoft Foundry: Azure's unified AI platform for building and deploying AI applications

#### Labs

- **Lab 0 – Sign In**: Sign into Azure Console and workshop environment
- **Lab 1 – Neo4j Aura Setup**:
  - Provision Neo4j Aura via Azure Marketplace
  - Restore a pre-built SEC 10-K knowledge graph
  - Explore relationships using Neo4j Explore
- **Lab 2 – Aura Agents**:
  - Create a no-code AI agent using Neo4j Aura Agents
  - Configure semantic search and Text2Cypher tools
  - Enable natural language queries against your graph
- **Lab 3 – Foundry Agents**:
  - Create a Microsoft Foundry project
  - Deploy gpt-5.2 and embedding models
  - Build an AI agent with MCP tools connecting to Neo4j

---

### Part 2 – Core GraphRAG with Neo4j and Microsoft Foundry (Intermediate)

Dive into Python-based development to build production-ready GraphRAG applications. You'll learn how to construct knowledge graphs from documents, generate embeddings for semantic search, and implement graph-enhanced retrieval patterns that leverage entity relationships for richer context. The section culminates in building intelligent agents using the Microsoft Agent Framework that can autonomously select the right tools to answer complex questions.

#### Lecture — Neo4j + Generative AI Concepts

- GraphRAG: Graph Retrieval-Augmented Generation and why graphs matter for AI
- Retrieval Patterns: Vector search, graph-enhanced retrieval, and context-aware generation

#### Lecture — Microsoft Foundry and the Agent Framework

- Microsoft Foundry: Azure's unified platform for AI application development
- Microsoft Agent Framework: Building intelligent agents with tools and reasoning
- Model Context Protocol (MCP): The open standard for connecting AI agents to external tools and data sources

#### Labs

- **Lab 4 – Start Codespace**:
  - Launch GitHub Codespace
  - Configure environment variables
  - Deploy Azure infrastructure
- **Lab 5 – Building a Knowledge Graph for GraphRAG**:
  - Load documents and create chunk embeddings
  - Implement VectorRetriever for semantic search
  - Use VectorCypherRetriever for graph-enhanced context
- **Lab 6 – Foundry Agents**:
  - Build agents using the Microsoft Agent Framework
  - Create tools for schema exploration and semantic search
  - Combine graph traversal with Text2Cypher capabilities
  - Deploy agents to Microsoft Foundry

---

### Part 3 – Advanced GraphRAG (Advanced)

Take your GraphRAG skills to the next level with advanced retrieval techniques. You'll implement Text2Cypher to translate natural language questions directly into Cypher queries, use LLMs to automatically extract entities and relationships from unstructured text, and combine keyword and semantic search for optimal retrieval accuracy. These patterns are essential for building robust, production-grade AI applications.

> **Optional Section:** This part of the workshop is designed for all-day sessions or as advanced material that participants can complete independently. It builds on the skills from Parts 1 and 2.

#### What You'll Learn

- Text2Cypher: Natural language to Cypher query generation using LLMs
- Entity Extraction: Automated extraction of entities and relationships from unstructured text
- Hybrid Search: Combining keyword (fulltext) and semantic (vector) search for improved retrieval

#### Labs

- **Lab 7 – Advanced GraphRAG Retrievers**:
  - Implement Text2Cypher for natural language to Cypher translation
  - Use LLMs for automated entity extraction
  - Build knowledge graphs from unstructured text
- **Lab 8 – GraphRAG for Hybrid Search**:
  - Create fulltext indexes for keyword search
  - Implement HybridRetriever combining keyword and semantic search
  - Use HybridCypherRetriever for graph-enhanced hybrid results
