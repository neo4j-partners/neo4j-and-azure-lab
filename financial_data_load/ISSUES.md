# Known Issues

## 1. Text2Cypher Token Overflow (Intermittent)

**Affects:** Solution 7 (`02_03_text2cypher_retriever.py`), Solution 11 (`03_03_text2cypher_agent.py`), Lab_10 notebooks using Text2Cypher

**Symptom:** `context_length_exceeded` error (318k tokens vs 272k limit) when the LLM generates Cypher that returns `Chunk.embedding` (a 1536-float vector per row).

**Root cause:** `get_schema(driver)` exposes `Chunk {index: INTEGER, text: STRING, embedding: LIST}` to the LLM. The LLM sometimes generates Cypher that selects chunk nodes with all properties, including the large embedding vectors. When many chunks are returned, the serialized embeddings exceed the model's context window.

**Reproducibility:** Intermittent. Depends on what Cypher the LLM generates. Broad queries like "Summarise the products mentioned in the company filings" are most likely to trigger it.

**Fix options (pick one or both):**

### Option A: Add prompt instruction (simple)

Add to `TEXT2CYPHER_PROMPT` and `CYPHER_PROMPT` in the affected files:

```
- NEVER return or select the Chunk.embedding property — it contains large binary vector data that will exceed context limits.
- When returning Chunk data, only select specific properties like text and index.
```

Files to update:
- `solution_srcs/02_03_text2cypher_retriever.py` — `TEXT2CYPHER_PROMPT`
- `solution_srcs/03_03_text2cypher_agent.py` — `CYPHER_PROMPT`
- `Lab_9_Advanced_Agents/03_text2cypher_agent.ipynb` — cell 9

### Option B: Filter schema before passing to Text2Cypher (robust)

Strip the `embedding` property from the schema string before passing it to `Text2CypherRetriever`. This prevents the LLM from ever seeing it:

```python
schema = get_schema(driver)
# Remove embedding property from schema to prevent LLM from selecting it
schema = schema.replace(", embedding: LIST", "")
```

Files to update: same as Option A, at the point where `get_schema()` is called.

**Recommendation:** Do both. Option B prevents the LLM from knowing about the property; Option A acts as a safety net for any other large properties.

---

## 2. Memory Embedder Requires OPENAI_API_KEY — FIXED

**Affects:** Solution 17 (`07_01_memory_context_provider.py`), Solution 18 (`07_02_memory_tools_agent.py`), Lab_7 notebooks

**Symptom:** After the agent responds, a non-blocking error appears:
```
Error saving messages to memory: The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
```

**Root cause:** `neo4j-agent-memory` defaults to OpenAI's embedding API. This workshop uses Azure AI Foundry, not OpenAI directly.

**Fix applied:** Created `shared/azure_embedder.py` with `AzureFoundryEmbedder` implementing `BaseEmbedder`. Uses `AsyncOpenAI` pointed at the Azure AI Foundry inference endpoint with Azure CLI token auth. A `get_memory_embedder()` factory returns the configured embedder (or `None` for direct OpenAI setups).

All memory solution files and Lab_7 notebooks now pass `embedder=get_memory_embedder()` to `MemoryClient`.

**Note:** The Azure CLI token expires after ~1 hour. For long-running sessions, the embedder would need token refresh logic. For workshop demos this is fine.

---

## Completed Fixes (for reference)

The following issues were found and fixed during the Cypher review:

### Wrong relationship types in notebooks
- `FILED` (doesn't exist) replaced with `FROM_CHUNK` traversal pattern
- `MENTIONS` (doesn't exist) replaced with shared-chunk pattern `(Company)-[:FROM_CHUNK]->(Chunk)<-[:FROM_CHUNK]-(Product)`
- `OWNS` direction corrected to `(AssetManager)-[:OWNS]->(Company)`
- Fixed in: Lab_8, Lab_9, Lab_10, Lab_11 notebooks

### Old MAF API in solution files and notebooks
- `async_credential=` replaced with `credential=`
- `client.create_agent()` replaced with `client.as_agent()`
- `agent.run_stream(query)` replaced with `agent.run(query, stream=True)`
- Fixed in: `03_02_*.py`, `03_03_*.py`, Lab_5, Lab_9 notebooks
