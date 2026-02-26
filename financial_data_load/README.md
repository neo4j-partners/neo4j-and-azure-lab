# Financial Data Load Workshop

Build AI agents using Microsoft Agent Framework with Azure AI Foundry, integrated with Neo4j graph database capabilities via the neo4j-graphrag-python library.

## Prerequisites

- Azure subscription with access to Azure AI Foundry
- Neo4j Aura instance (or local Neo4j database)
- Python 3.12.x
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [uv](https://docs.astral.sh/uv/) package manager

## Quick Start

All commands below assume you are in the `financial_data_load/` directory:

```bash
cd financial_data_load
```

### 1. Deploy Azure AI Infrastructure

```bash
# Login to Azure
az login --use-device-code
azd auth login --use-device-code

# Configure region and initialize azd
./scripts/setup_azure.sh

# Deploy infrastructure (AI Services + model deployments)
azd up

# Sync Azure outputs to .env
uv run python setup_env.py
```

### 2. Configure Neo4j

Edit the `.env` file and update the Neo4j credentials:

```bash
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

### 3. Install Dependencies

From the **project root**:

```bash
uv sync --prerelease=allow
```

This project uses a local fork of `neo4j-graphrag-python`. After making changes to the library, force reinstall to pick them up:

```bash
uv pip install --force-reinstall ~/projects/neo4j-graphrag-python
```

### 4. Test Connections

```bash
uv run python main.py test
```

### 5. Load Data

Load all SEC 10-K filings using the SimpleKGPipeline. Data files are in `financial-data/`:

```bash
# Test with 1 PDF first
uv run python main.py load --limit 1 --clear

# Once that works, load all 8 PDFs
uv run python main.py load --clear
```

**All data commands:**

| Command | Description |
|---------|-------------|
| `main.py test` | Test Neo4j and Azure AI connections |
| `main.py load [--limit N] [--clear]` | Full load: metadata + PDFs + constraints + indexes |
| `main.py verify` | Counts + enrichment checks + end-to-end search validation |
| `main.py clean` | Clear all data |
| `main.py samples [--limit N]` | Run sample queries showcasing the graph |

**Pipeline Flow:**
1. Loads company metadata from `financial-data/Company_Filings.csv`
2. Creates Company nodes from CSV metadata
3. Processes PDFs through SimpleKGPipeline:
   - Chunks documents (27 chunks per PDF typical)
   - Generates embeddings (1536 dimensions via text-embedding-ada-002)
   - Extracts entities using GPT-5.2 (RiskFactor, Product, Executive, FinancialMetric)
   - Creates relationships (FACES_RISK, OFFERS, HAS_EXECUTIVE, etc.)
4. Runs fuzzy entity resolution (via `FuzzyMatchResolver`) to merge near-duplicate entities (e.g. "Apple" vs "Apple Inc.")
5. Creates uniqueness constraints, embedding indexes, and fulltext indexes
6. Creates AssetManager nodes and OWNS relationships from `Asset_Manager_Holdings.csv`

**Expected Output (1 PDF):**
```
NODE COUNTS BY LABEL:
   __KGBuilder__: 170
   __Entity__: 142
   RiskFactor: 67
   Product: 58
   Chunk: 27
   Company: 12
   ...

TOTALS: 505 nodes, 310 relationships
```

### 6. Run Workshop Solutions

```bash
# Interactive menu
uv run python main.py solutions

# Run specific solution
uv run python main.py solutions 4

# Run all (from option 4 onwards)
uv run python main.py solutions A
```

## Workshop Solutions

### Data Pipeline (01_xx)

These solutions build the knowledge graph — **WARNING: they will delete existing data**:

| # | Solution | Description |
|---|----------|-------------|
| 1 | `01_01_data_loading.py` | Load financial documents into Neo4j |
| 2 | `01_02_embeddings.py` | Generate and store vector embeddings |
| 3 | `01_03_entity_extraction.py` | Extract entities and relationships |
| 4 | `01_04_full_dataset_queries.py` | Explore the loaded data |

### Retrievers (02_xx)

GraphRAG patterns using neo4j-graphrag with Azure AI:

| # | Solution | Description |
|---|----------|-------------|
| 5 | `02_01_vector_retriever.py` | Basic vector search |
| 6 | `02_02_vector_cypher_retriever.py` | Vector search + custom Cypher |
| 7 | `02_03_text2cypher_retriever.py` | Natural language to Cypher |

### Agents (03_xx)

Microsoft Agent Framework with Azure AI Foundry:

| # | Solution | Description |
|---|----------|-------------|
| 8 | `03_01_simple_agent.py` | Basic agent with schema tool |
| 9 | `03_02_vector_graph_agent.py` | Agent with vector search + graph traversal |
| 10 | `03_03_text2cypher_agent.py` | Multi-tool agent with Text2Cypher |

### Search (05_xx)

Advanced search patterns:

| # | Solution | Description |
|---|----------|-------------|
| 11 | `05_01_fulltext_search.py` | Full-text search capabilities |
| 12 | `05_02_hybrid_search.py` | Hybrid vector + keyword search |

## Architecture

- **Azure AI Foundry** — Model hosting (GPT-5.2, text-embedding-ada-002)
- **Microsoft Agent Framework** — Agent creation and tool management
- **neo4j-graphrag-python** — Graph retrieval capabilities
- **Neo4j** — Graph database with vector search

## File Structure

```
financial_data_load/
├── azure.yaml              # azd deployment configuration
├── main.py                 # CLI entry point (load, enrich, verify, clean, samples, solutions)
├── setup_env.py            # Sync azd outputs to .env
├── infra/
│   ├── main.bicep          # Azure AI Foundry infrastructure
│   └── main.parameters.json
├── scripts/
│   └── setup_azure.sh      # Azure region configuration
├── financial-data/         # SEC 10-K data files
│   ├── Company_Filings.csv
│   ├── Asset_Manager_Holdings.csv
│   └── form10k-sample/     # PDF files (8 companies)
├── src/                    # Data loader modules
│   ├── config.py           # Settings, Azure auth, Neo4j connection
│   ├── schema.py           # Graph schema, constraints, indexes
│   ├── loader.py           # CSV loading, company/asset manager nodes
│   ├── pipeline.py         # SimpleKGPipeline, PDF processing
│   └── samples.py          # Sample queries
└── solution_srcs/          # Workshop solution files
    ├── config.py           # Shared config for solutions
    ├── test_connection.py  # Connection test script
    ├── 01_01_data_loading.py
    ├── 01_02_embeddings.py
    ├── 01_03_entity_extraction.py
    ├── 01_04_full_dataset_queries.py
    ├── 02_01_vector_retriever.py
    ├── 02_02_vector_cypher_retriever.py
    ├── 02_03_text2cypher_retriever.py
    ├── 03_01_simple_agent.py
    ├── 03_02_vector_graph_agent.py
    ├── 03_03_text2cypher_agent.py
    ├── 05_01_fulltext_search.py
    └── 05_02_hybrid_search.py
```

## Environment Variables

After running `setup_env.py`, your `.env` file will contain:

```bash
# Azure AI (from azd)
AZURE_AI_EMBEDDING_NAME=text-embedding-ada-002
AZURE_AI_MODEL_NAME=gpt-5.2
AZURE_AI_PROJECT_ENDPOINT=https://...
AZURE_AI_SERVICES_ENDPOINT=https://...
AZURE_RESOURCE_GROUP=rg-...
AZURE_TENANT_ID=...

# Neo4j Database Connection
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

## Cleanup

To remove deployed Azure resources:

```bash
azd down
```
