# Slides Sync Proposal

The slide decks in `graphacademy/slides/` were written against an earlier lab numbering. The labs have since been reorganized and three new labs added (5, 6, 7). This proposal brings the slides in sync with the current lab structure without deleting any existing content.

## Current State

### Slide folders → Lab mapping

| Slide Folder | Covers | Current Lab(s) |
|---|---|---|
| `lab-1-neo4j-aura` (slides 01-07) | Neo4j Aura, GenAI limits, RAG, GraphRAG, SEC filings, Aura Agents, Fabric Workload | Lab 0, Lab 1, Lab 2 |
| `lab-2-foundry` (slides 01-03) | What is an Agent, MCP, Microsoft Foundry | Lab 3 |
| _(no slides)_ | — | Lab 4 (Start Codespace — setup only, no slides needed) |
| _(no slides)_ | — | **Lab 5 (Foundry Agents — MAF basics, tools, context providers)** |
| _(no slides)_ | — | **Lab 6 (Context Providers — Neo4j context providers)** |
| _(no slides)_ | — | **Lab 7 (Agent Memory — neo4j-agent-memory)** |
| `lab-5-knowledge-graph` (slides 01-07) | GenAI, RAG, KG pipeline, schema, chunking, entity resolution, vectors | Lab 8 |
| `lab-6-retrievers` (slides 01-04) | Retrievers overview, vector, vector+cypher, text2cypher | Lab 10, Lab 11 |
| `lab-7-agents` (slides 01-05) | Retrievers→agents, MAF, building agent, design patterns, congratulations | Lab 9 |

### Gaps

1. **Labs 5, 6, 7 have no slides.** These are the new MAF hands-on labs.
2. **Slide folder names don't match current lab numbers.** `lab-5-knowledge-graph` is actually Lab 8, etc.
3. **The "Microsoft Agent Framework" slide (`lab-7-agents/02`)** uses an older API surface (`AzureAIClient`, `ChatAgent`, `create_agent`, threads) that doesn't match the current MAF API (`AzureOpenAIResponsesClient`, `as_agent()`, `run_stream()`, sessions, context providers).
4. **No slides cover context providers or agent memory** — the two key concepts introduced in the new labs.

## Proposed Changes

### 1. Add new slide folder: `lab-5-foundry-agents` (2 decks)

Covers Lab 5 — introduces MAF with hands-on tools and context providers.

**01-microsoft-agent-framework-slides.md** (~8 slides)
- What is the Microsoft Agent Framework and why it exists (LLMs are stateless)
- Core concepts: Agents, Tools, Context Providers, Sessions, Middleware
- The agent lifecycle: context providers `before_run()` → LLM invocation → `after_run()`
- Tools vs context providers (when each runs, best for)
- Key API: `AzureOpenAIResponsesClient`, `as_agent()`, `run_stream()`
- Architecture diagram (same as Lab 5 README)

**02-tools-and-context-providers-slides.md** (~6 slides)
- Defining tools: Python functions with `Annotated` + `Field` type annotations
- How the agent reads function name + docstring to decide tool selection
- Context providers: `BaseContextProvider` with `before_run()` / `after_run()`
- `SessionContext`: `extend_instructions()` and `extend_messages()`
- `AgentSession` and persistent state across turns
- Extracting structured data with Pydantic in `after_run()`

### 2. Add new slide folder: `lab-6-context-providers` (2 decks)

Covers Lab 6 — Neo4j context providers from `agent-framework-neo4j`.

**01-neo4j-context-provider-slides.md** (~8 slides)
- What is `Neo4jContextProvider` (from `agent-framework-neo4j`)
- How `before_run()` works: recent messages → concatenate → search index → format results → inject
- Three search modes: vector (cosine similarity), fulltext (BM25), hybrid (combined)
- Comparison table of search modes (when to use each)
- Graph enrichment: `retrieval_query` parameter for Cypher traversal after index match
- Retriever selection logic table (index_type × retrieval_query → retriever class)
- Result formatting: `[Score: 0.892] [company: Apple Inc] ...`
- Configuration: `top_k`, `message_history_count`, `context_prompt`, `filter_stop_words`

**02-graph-enrichment-slides.md** (~5 slides)
- Why vector search alone isn't enough (returns chunks, not knowledge)
- The two-step process: index search finds nodes → Cypher traversal enriches with relationships
- Example retrieval query: match company → optional match risks, products → return enriched context
- Before/after comparison: plain chunk text vs graph-enriched context with company, ticker, risks, products
- Connecting it to Lab 5: context providers inject this automatically — no tool calls needed

### 3. Add new slide folder: `lab-7-agent-memory` (2 decks)

Covers Lab 7 — persistent agent memory from `neo4j-agent-memory`.

**01-agent-memory-overview-slides.md** (~8 slides)
- The problem: agents forget everything between sessions
- What is `neo4j-agent-memory` — graph-native persistent memory
- Three memory types:
  - **Short-term**: conversation messages with embeddings (semantic search over past messages)
  - **Long-term**: entities, facts (SPO triples), preferences (extracted from conversations)
  - **Reasoning**: traces of past tool calls, success/failure, duration (learn from experience)
- Memory types comparison table (what it stores, how it helps)
- Neo4j graph model: Conversation → Message, Entity, Preference, Fact, ReasoningTrace → ReasoningStep → ToolCall
- How memory differs from Lab 6 context providers: static knowledge graph vs dynamic memory that grows

**02-memory-tools-slides.md** (~6 slides)
- Memory context provider: `before_run()` retrieves from all three types, `after_run()` stores + extracts entities
- Memory tools: the six callable tools (`search_memory`, `remember_preference`, `recall_preferences`, `search_knowledge`, `remember_fact`, `find_similar_tasks`)
- Context provider vs memory tools: automatic background recall vs explicit agent-controlled operations
- Combining both: context provider for passive recall + tools for active memory management
- Entity extraction: automatic identification of people, organizations, concepts from messages
- Entity deduplication: configurable strategies (exact, fuzzy, semantic, composite)

### 4. Rename slide folders to match current lab numbers

Rename the existing folders so the slide directory names align with the lab numbers:

| Current Folder | New Folder | Lab |
|---|---|---|
| `lab-1-neo4j-aura` | `lab-1-neo4j-aura` | Labs 0-2 (no change) |
| `lab-2-foundry` | `lab-3-foundry` | Lab 3 |
| _(new)_ | `lab-5-foundry-agents` | Lab 5 |
| _(new)_ | `lab-6-context-providers` | Lab 6 |
| _(new)_ | `lab-7-agent-memory` | Lab 7 |
| `lab-5-knowledge-graph` | `lab-8-knowledge-graph` | Lab 8 |
| `lab-6-retrievers` | `lab-10-retrievers` | Lab 10 |
| `lab-7-agents` | `lab-9-agents` | Lab 9 |

### 5. Update existing `lab-7-agents/02-microsoft-agent-framework-slides.md`

The current slide uses an older API surface that no longer matches the workshop code:

| Current (old API) | Should Be (current API) |
|---|---|
| `AzureAIClient` | `AzureOpenAIResponsesClient` |
| `client.create_agent()` | `client.as_agent()` |
| `ChatAgent` | Agent created via `as_agent()` |
| Threads (`get_new_thread()`, `thread=thread`) | Sessions (`AgentSession`, `session.state`) |

This slide should be updated to match the API used in Lab 5 notebooks. The conceptual content (tool selection, docstrings, ReAct loop, instructions, streaming) is all still correct — only the code examples and API names need updating.

### 6. Update `graphacademy/slides/README.md`

Update the README to:
- Add the three new slide sections (Lab 5, Lab 6, Lab 7)
- Update folder references if renamed
- Update the presentation order to include the new decks
- Update slide statistics (total count)

**No existing content in the README should be deleted** — only additions and reference updates.

## What Is NOT Changing

- All existing slide content is preserved (no deletions)
- Lab 1 slides (01-07) stay as-is
- Lab 2/Foundry slides (01-03) stay as-is
- Lab 5/Knowledge Graph slides (01-07) stay as-is
- Lab 6/Retrievers slides (01-04) stay as-is
- Lab 7/Agents slides (01, 03, 04, 05) stay as-is
- Lab 7/Agents slide 02 gets API updates only (conceptual content unchanged)
- The `clean-html.sh` script and `images/` directory are untouched

## Summary

| Action | Count |
|---|---|
| New slide decks to write | 6 |
| Folders to rename | 3 |
| Existing slides to update | 1 (API names only) |
| Existing slides deleted | 0 |
| README updates | 1 |
