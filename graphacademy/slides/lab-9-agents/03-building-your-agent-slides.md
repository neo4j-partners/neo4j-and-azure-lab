---
marp: true
theme: default
paginate: true
---

<style>
section {
  --marp-auto-scaling-code: false;
}

li {
  opacity: 1 !important;
  animation: none !important;
  visibility: visible !important;
}

/* Disable all fragment animations */
.marp-fragment {
  opacity: 1 !important;
  visibility: visible !important;
}

ul > li,
ol > li {
  opacity: 1 !important;
}
</style>


# Building Your Agent

---

## Progressive Enhancement

Build agents progressively:

1. **Start with one tool**: Understand how agents use tools
2. **Add semantic search**: Handle content questions
3. **Add database queries**: Handle factual questions

Each step adds capability while keeping the system testable.

---

## Tool 1: Schema Introspection

**Purpose:** Let users explore what data exists.

**When the agent uses it:**
- "What types of data are in this database?"
- "What relationships exist?"
- "What can I ask about?"

```python
def get_graph_schema() -> str:
    """Get the schema of the graph database including node labels,
    relationships, and properties."""
    return get_schema(driver)
```

**Why start here:** Simple, deterministic, helps users understand possibilities.

---

## Tool 2: Semantic Search

**Purpose:** Find content about topics and concepts.

**Based on:** Vector Retriever from Lab 6.

**When the agent uses it:**
- "What is Apple's business strategy?"
- "Tell me about cybersecurity threats"
- "What risks do tech companies face?"

```python
def search_content(query: str) -> str:
    """Search for content about topics using semantic search.
    Use for 'What is...', 'Tell me about...', 'Explain...'"""
    return vector_retriever.search(query)
```

---

## Tool 3: Database Queries

**Purpose:** Answer factual questions with precision.

**Based on:** Text2Cypher Retriever from Lab 6.

**When the agent uses it:**
- "How many companies are in the database?"
- "What companies does BlackRock own?"
- "Which company has the most risk factors?"

```python
def query_database(query: str) -> str:
    """Query the database for specific facts, counts, lists, and relationships.
    Use for 'How many...', 'List all...', 'Who owns...'"""
    return text2cypher_retriever.search(query)
```

---

## How the Agent Chooses

With three tools, the agent matches questions to descriptions:

| Question | Agent Reasoning | Tool |
|----------|-----------------|------|
| "What data types exist?" | About structure | Schema |
| "What is Apple's strategy?" | Content/concept | Semantic Search |
| "How many companies?" | Count/fact | Database Query |
| "Tell me about AI" | Topic exploration | Semantic Search |
| "Who owns Microsoft?" | Relationship fact | Database Query |

---

## Example: Schema Question

**Question:** "What types of data are in this database?"

```
Agent thinks: "Asking about data structure"
Agent calls: get_graph_schema()
Agent observes: "Node labels: Company, RiskFactor, Product..."
Agent responds: "The database contains Companies, Risk Factors,
                Products, Executives, and their relationships..."
```

---

## Example: Content Question

**Question:** "What does Apple say about AI?"

```
Agent thinks: "Asking about content on a topic"
Agent calls: search_content("Apple AI")
Agent observes: Chunks about Apple's AI initiatives
Agent responds: "Apple discusses AI in several contexts,
                including privacy-focused machine learning..."
```

---

## Example: Fact Question

**Question:** "How many risk factors does Apple face?"

```
Agent thinks: "Asking for a count"
Agent calls: query_database("How many risk factors does Apple face?")
Agent observes: "45"
Agent responds: "Apple faces 45 risk factors according to
                their SEC filing."
```

---

## Testing Your Agent

Test each tool type:

**Schema questions:**
- "What entities exist?"
- "What relationships are there?"

**Content questions:**
- "What is [topic]?"
- "Tell me about [concept]"

**Fact questions:**
- "How many [entities]?"
- "Who [relationship] [entity]?"

Verify the agent selects the correct tool.

---

## Common Issues

| Problem | Solution |
|---------|----------|
| Wrong tool selected | Improve docstrings to be more specific |
| Overlapping tools | Ensure each tool has distinct purpose |
| No tool selected | Make sure a tool covers the question type |
| Poor results | Check underlying retrievers work correctly |

---

## The Complete Agent

With all three tools, your agent handles:

| Category | Tool | Examples |
|----------|------|----------|
| Structure | Schema | "What data exists?" |
| Content | Semantic Search | "What is...?", "Tell me about..." |
| Facts | Database Query | "How many...?", "List all..." |

This covers the full range of GraphRAG queries.

---

## Summary

- **Build progressively:** Start with one tool, add more
- **Three tools:** Schema (structure), Semantic Search (content), Database Query (facts)
- **Selection via docstrings:** Clear descriptions guide correct choice
- **Test incrementally:** Verify each tool before adding more

**Next:** Learn design patterns for effective multi-tool agents.
