# Neo4j And Azure Lab
Neo4j is the [leading graph database](https://db-engines.com/en/ranking/graph+dbms) vendor.  We've worked closely with Microsoft Azure engineering for years.  Our products, AuraDB and AuraDS are offered as managed services on Azure.  Neo4j Aura Professional Edition is offered in the [Azure Marketplace](https://portal.azure.com/#create/neo4j.neo4j_aura_professional).

In this hands-on lab, you'll learn about Neo4j, Microsoft Foundry, and the [Microsoft Agent Framework](https://github.com/microsoft/agent-framework). The lab is designed for data scientists, data engineers, and AI developers who want to master GraphRAG (Graph Retrieval-Augmented Generation) techniques and build production-ready agentic AI applications.

In today's landscape, organizations need AI systems that can extract deep insights from unstructured documents, understand complex entity relationships, and build intelligent systems that can autonomously reason over vast information networks. This hands-on lab addresses this need directly by providing mastery in the most powerful pattern available for complex document intelligence: Graph Retrieval-Augmented Generation (GraphRAG).

You'll work with a real-world dataset of SEC 10-K company filings to learn fundamental GraphRAG patterns. We'll start by building a knowledge graph from unstructured text using generative AI for entity extraction. Then you'll implement multiple retrieval strategies: vector similarity search for semantic retrieval, graph-enhanced retrievers that leverage entity relationships, and natural language to Cypher query generation. Finally, you'll build intelligent agents using the Microsoft Agent Framework that can autonomously reason over your knowledge graph to answer complex questions.

By the end of this lab, you'll have hands-on experience with:
- Building knowledge graphs from unstructured documents
- Implementing semantic search with vector embeddings
- Creating graph-enhanced retrieval patterns for richer context
- Developing agentic AI systems that combine multiple tools and reasoning strategies
- Deploying GraphRAG applications on Azure infrastructure

These techniques apply to any domain where you need to extract insights from documents, understand entity relationships, and build AI systems that can reason over complex information networks.

## Knowledge Graph Data Model

The workshop builds a hybrid knowledge graph that combines **lexical structure** (documents and chunks) with **semantic knowledge** (entities and relationships extracted by LLM). This architecture enables multiple retrieval strategies.

### Graph Structure

```
                      NEXT_CHUNK
                 ┌──────────────────┐
                 │                  │
                 v                  │
┌──────────┐       ┌──────────┐       ┌──────────┐
│  Chunk   │──────>│  Chunk   │──────>│  Chunk   │
│          │       │          │       │          │
│ text     │       │ text     │       │ text     │
│ embedding│       │ embedding│       │ embedding│
└──────────┘       └──────────┘       └──────────┘
     │                  │                  │
     │ FROM_DOCUMENT    │                  │
     v                  v                  v
┌─────────────────────────────────────────────────┐
│                    Document                      │
│                                                  │
│  path: "sec-10k-filings/apple-10k.pdf"          │
└─────────────────────────────────────────────────┘

     ^                  ^                  ^
     │ FROM_CHUNK       │                  │
     │                  │                  │
┌──────────┐       ┌──────────┐       ┌──────────┐
│ Company  │       │ Product  │       │RiskFactor│
│          │       │          │       │          │
│ Apple    │       │ iPhone   │       │ Supply   │
│ Inc.     │       │          │       │ Chain    │
└──────────┘       └──────────┘       └──────────┘
     │                                      ^
     │ FACES_RISK                           │
     └──────────────────────────────────────┘
```

### Node Types

| Node Label | Description | Key Properties |
|------------|-------------|----------------|
| `Document` | Source PDF file | `path`, `createdAt` |
| `Chunk` | Text segment from document | `text`, `index`, `embedding` (1536-dim vector) |
| `Company` | Extracted company entity | `name`, `ticker` |
| `Product` | Products/services mentioned | `name` |
| `RiskFactor` | Business risks identified | `name` |
| `Executive` | Key personnel | `name`, `title` |
| `FinancialMetric` | Financial data points | `name`, `value` |
| `AssetManager` | Institutional investors | `managerName` |

### Relationship Types

| Relationship | Direction | Description |
|--------------|-----------|-------------|
| `FROM_DOCUMENT` | `(Chunk)->(Document)` | Links chunk to source document |
| `NEXT_CHUNK` | `(Chunk)->(Chunk)` | Sequential chunk ordering |
| `FROM_CHUNK` | `(Entity)->(Chunk)` | Provenance: where entity was extracted |
| `FACES_RISK` | `(Company)->(RiskFactor)` | Company faces this risk |
| `OFFERS` | `(Company)->(Product)` | Company offers this product |
| `HAS_EXECUTIVE` | `(Company)->(Executive)` | Company has this executive |
| `REPORTS` | `(Company)->(FinancialMetric)` | Company reports this metric |
| `OWNS` | `(AssetManager)->(Company)` | Investor owns shares in company |

### Search Indexes

The data pipeline creates three indexes to support different retrieval strategies:

| Index Name | Type | Target | Purpose |
|------------|------|--------|---------|
| `chunkEmbeddings` | Vector | `Chunk.embedding` | Semantic similarity search |
| `chunkText` | Fulltext | `Chunk.text` | Keyword search for hybrid retrieval |
| `search_entities` | Fulltext | Entity `.name` properties | Entity lookup by name |

### Retrieval Strategies

**1. Vector Search** - Find semantically similar content using embeddings:
```cypher
CALL db.index.vector.queryNodes('chunkEmbeddings', 5, $embedding)
YIELD node, score
RETURN node.text, score
```

**2. Graph-Enhanced Retrieval** - Combine vector search with graph traversal:
```cypher
-- Find chunks, then traverse to related entities
CALL db.index.vector.queryNodes('chunkEmbeddings', 5, $embedding)
YIELD node AS chunk, score
MATCH (company:Company)-[:FROM_CHUNK]->(chunk)
OPTIONAL MATCH (company)-[:FACES_RISK]->(risk:RiskFactor)
RETURN chunk.text, company.name, collect(risk.name) AS risks
```

**3. Hybrid Search** - Combine keyword and semantic search:
```cypher
-- Uses both chunkEmbeddings (vector) and chunkText (fulltext) indexes
-- Alpha parameter controls the balance: 1.0 = pure vector, 0.0 = pure keyword
```

**4. Text2Cypher** - Natural language to Cypher query generation using LLM.

This hybrid architecture enables rich, context-aware retrieval that leverages both the semantic understanding from embeddings and the structural relationships in the knowledge graph.

## Starting the Lab

To get started, follow the labs in the agenda below in order.

**Quick Start Options:**
- **No-Code Track Only (1 hour):** Complete Part 1 (Labs 0-3) to explore Neo4j and AI agents without coding
- **Full Workshop (3-4 hours):** Complete both Part 1 and Part 2 for the full development experience
- **Skip to Coding:** If you already have your Azure account and Aura credentials, go straight to [Lab 4 - Start Codespace](Lab_4_Start_Codespace)

## Duration
3-4 hours (full workshop) or 1 hour (no-code track only).

## Prerequisites
You'll need a laptop with a web browser. Your browser will need to be able to access the Azure Console. If your laptop has a firewall you can't control on it, you may want to bring your personal laptop.

## Agenda

### Part 1 - No-Code Getting Started
*This section requires no coding. You'll use visual tools and pre-built interfaces to explore Neo4j and AI agents.*

* Introductions
* [Lecture - Introduction to Neo4j](https://docs.google.com/presentation/d/1mEXn02TMYJ0nGFj7u5VANQBl1jBJcLGp6dYHB_xY0pQ/edit?usp=sharing) (10 min)
    * What is Neo4j?
    * How is it deployed and managed on Azure?
* [Lab 0 - Sign In](Lab_0_Sign_In) (5 min)
    * Improving the Labs
    * Sign into Azure
* [Lab 1 - Neo4j Aura Setup](Lab_1_Aura_Setup) (15 min)
    * Signing up for Neo4j Aura through Azure Marketplace
    * Restoring the pre-built knowledge graph
    * Visual exploration with Neo4j Explore
* [Lab 2 - Aura Agents](Lab_2_Aura_Agents) (20 min)
    * Building AI agents using Neo4j Aura Agent (no-code)
    * Creating Cypher template tools
    * Adding semantic search and Text2Cypher capabilities
* [Lab 3 - Microsoft Foundry Agents](Lab_3_Foundry_Agents) (15 min)
    * Access Microsoft Foundry
    * Create a Foundry Project
    * Deploy gpt-5.2 model
    * Build an agent with MCP tools
* Break (5 min)

---

### Part 2 - Core Labs
*This section involves Python programming using Jupyter notebooks.*

* [Lab 4 - Start Codespace](Lab_4_Start_Codespace) (10 min)
    * Launch GitHub Codespace
    * Configure environment variables
    * Deploy Azure infrastructure
* [Lecture - Neo4j and Generative AI](https://docs.google.com/presentation/d/1iHu9vgEG0s6yjKMLUw9XqWGiJrY7Z1oNv0QPa75BCtc/edit?usp=sharing) (15 min)
    * Generating Knowledge Graphs
    * Retrieval Augmented Generation
    * Semantic Search
* [Lecture - Microsoft Foundry](https://docs.google.com/presentation/d/1KPHoVJivbinHg-UtrnTIUbMiFHB8mPEnDO0v0OvvcPM/edit?usp=sharing) (15 min)
    * What is Microsoft Foundry?
    * Generative AI
* [Lab 5 - Foundry Agents](Lab_5_Foundry_Agents) (15 min)
    * Simple Schema Agent with Microsoft Agent Framework
* [Lab 6 - MAF Context Providers](Lab_6_Context_Providers) (30 min)
    * Fulltext Context Provider for keyword-based retrieval
    * Vector Context Provider for semantic search
    * Graph-Enriched Provider with relationship traversal
* [Lab 7 - Agent Memory](Lab_7_Agent_Memory) (30 min)
    * Memory Context Provider with Neo4j Agent Memory
    * Agent with Memory Tools for persistent learning
* Break (5 min)
* [Lab 8 - Building a Knowledge Graph](Lab_8_Knowledge_Graph) (30 min)
    * Data Loading and Embeddings
    * GraphRAG Retrievers (Vector and VectorCypher)
* [Lab 9 - Advanced Agents](Lab_9_Advanced_Agents) (30 min)
    * Vector + Graph Agent for Semantic Search with Context
    * Multi-Tool Agent with Text2Cypher

---

### Part 3 - Advanced Labs
*Optional advanced topics building on the core workshop.*

* [Lab 10 - Advanced Retrievers](Lab_10_Retrievers) (30 min)
    * Text2Cypher Retriever for Natural Language Queries
    * Entity Extraction
    * Working with the Full Dataset
* [Lab 11 - Hybrid Search](Lab_11_Hybrid_Search) (20 min)
    * Fulltext Search with Neo4j indexes
    * Combining keyword and semantic search
* [Questions and Next Steps](Questions%20and%20Next%20Steps.md) (5 min)

## Windows Setup Guide for VS Code

This guide will help you set up your Windows machine with VS Code to run this project locally.

### Prerequisites

Before starting, ensure you have:
- Windows 10 or Windows 11
- Administrator access on your machine
- An active Azure subscription
- Neo4j Aura credentials (see [Lab 1 - Neo4j Aura Setup](Lab_1_Aura_Setup))

### Step 1: Download the Project

1. Go to https://github.com/neo4j-partners/neo4j-and-azure-lab
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file to a location on your computer (e.g., `C:\Projects\neo4j-and-azure-lab`)

### Step 2: Install Python 3.12

This project requires Python 3.12 (not 3.13 or later).

1. Download Python 3.12 from https://www.python.org/downloads/
   - Select a **3.12.x** version (e.g., 3.12.7)
   - Do NOT install Python 3.13 or later as this project requires Python 3.12
2. Run the installer:
   - Check "Add Python 3.12 to PATH"
   - Click "Install Now"
   - Note: pip (Python package installer) is included automatically with Python
3. Verify installation:
   ```powershell
   python --version
   ```
   Should output: `Python 3.12.x`
4. Verify pip is installed:
   ```powershell
   pip --version
   ```

### Step 3: Install uv (Python Package Manager)

uv is a fast Python package installer and resolver used by this project.

1. Open PowerShell as Administrator
2. Install uv using pip:
   ```powershell
   pip install uv
   ```
3. Verify installation:
   ```powershell
   uv --version
   ```

### Step 4: Install Azure CLI

The Azure CLI (az) is required for authenticating with Azure and managing resources.

1. Download the Azure CLI installer from https://aka.ms/installazurecliwindows
2. Run the MSI installer and follow the prompts
3. Restart your terminal (close and reopen PowerShell)
4. Verify installation:
   ```powershell
   az --version
   ```
5. Sign in to Azure:
   ```powershell
   az login
   ```
   This will open a browser window for authentication

   **Note:** If you already have Azure CLI installed and are logged in with different credentials, you must log out first and then log in with your workshop credentials:
   ```powershell
   az logout
   az login
   ```
   Verify you're logged in with the correct account:
   ```powershell
   az account show
   ```

### Step 5: Install Azure Developer CLI (azd)

The Azure Developer CLI (azd) simplifies deploying and managing Azure resources.

1. Open PowerShell as Administrator
2. Install azd using the following command:
   ```powershell
   winget install microsoft.azd
   ```
   If `winget` is not available, download the installer from https://aka.ms/azure-dev/install
3. Restart your terminal
4. Verify installation:
   ```powershell
   azd version
   ```
5. Sign in to Azure Developer CLI:
   ```powershell
   azd auth login
   ```

   **Note:** If you already have Azure Developer CLI installed and are logged in with different credentials, log out first and then log in with your workshop credentials:
   ```powershell
   azd auth logout
   azd auth login
   ```

### Step 6: Install Visual Studio Code

1. Download VS Code from https://code.visualstudio.com/
2. Run the installer with default settings
3. Launch VS Code

### Step 7: Install VS Code Extensions

Install the following extensions for an optimal development experience:

1. **Python Extension**
   - Open VS Code
   - Click the Extensions icon (or press `Ctrl+Shift+X`)
   - Search for "Python" by Microsoft
   - Click Install

2. **Jupyter Extension**
   - Search for "Jupyter" by Microsoft
   - Click Install

3. **Azure Account Extension** (optional but recommended)
   - Search for "Azure Account"
   - Click Install

### Step 8: Open the Project in VS Code

1. Open VS Code
2. Click "File" > "Open Folder"
3. Navigate to where you extracted the project (e.g., `C:\Projects\neo4j-and-azure-lab`)
4. Click "Select Folder"

### Step 9: Set Up Python Environment

1. Open a terminal in VS Code (`Ctrl+``)
2. Create the Python environment and install dependencies:
   ```powershell
   uv sync
   ```
   This will create a virtual environment and install all required dependencies

3. Select the Python interpreter:
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose the interpreter from `.venv` folder (e.g., `.venv\Scripts\python.exe`)

### Step 10: Configure Environment Variables

1. Copy the sample environment file:
   ```powershell
   copy .env.sample .env
   ```

2. Edit `.env` file and add your Neo4j credentials:
   - Open `.env` in VS Code
   - Fill in the following values:
     ```
     NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
     NEO4J_USERNAME=neo4j
     NEO4J_PASSWORD=your-password-here
     ```

### Step 11: Deploy Azure Infrastructure

1. Initialize the Azure Developer environment:
   ```powershell
   azd env new
   ```
   - Enter an environment name (e.g., "dev")

2. Set your Azure location (must be one of: eastus2, swedencentral, or westus2):
   ```powershell
   azd env set AZURE_LOCATION eastus2
   ```

3. Set your Azure resource group name:
   ```powershell
   azd env set AZURE_RESOURCE_GROUP your-resource-group-name
   ```

4. Deploy the Azure infrastructure:
   ```powershell
   azd up
   ```
   This will provision:
   - Microsoft Foundry project with gpt-5.2 and text-embedding-ada-002 models
   - Azure Container Registry
   - Azure Monitor and Application Insights

5. Sync Azure configuration to your `.env` file:
   ```powershell
   uv run setup_env.py
   ```

### Step 12: Run the Notebooks

1. In VS Code, navigate to a lab folder (e.g., `Lab_8_Knowledge_Graph`)
2. Open a notebook file (e.g., `01_data_loading.ipynb`)
3. When prompted to select a kernel:
   - Click "Select Kernel" in the top right
   - Choose "Python Environments..."
   - Select the "neo4j-azure-ai-workshop" environment (.venv)
4. Run the notebook cells using `Shift+Enter` or the Run button

### Troubleshooting

**Problem: Python version is not 3.12**
- Solution: Uninstall other Python versions and ensure 3.12.x is installed and in your PATH

**Problem: `uv` command not found**
- Solution: Close and reopen your terminal, or add Python Scripts folder to PATH manually

**Problem: Azure CLI authentication fails**
- Solution: Run `az logout` then `az login` again

**Problem: `azd up` fails with region error**
- Solution: Ensure you set AZURE_LOCATION to one of the supported regions (eastus2, swedencentral, westus2)

**Problem: Jupyter kernel not found**
- Solution: Run `uv sync` again and restart VS Code

**Problem: Import errors in notebooks**
- Solution: Ensure you've selected the correct Python interpreter from the `.venv` folder

### Additional Resources

- [Azure CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/)
- [Azure Developer CLI Documentation](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [VS Code Python Documentation](https://code.visualstudio.com/docs/python/python-tutorial)
