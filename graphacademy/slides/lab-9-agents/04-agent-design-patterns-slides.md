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


# Agent Design Patterns

---

## Pattern 1: Tool Specialization

Each tool should have a **distinct, non-overlapping purpose**.

**Bad design (overlapping):**
```
Tool 1: "Search for companies"
Tool 2: "Find company information"
Tool 3: "Look up companies"
```

**Good design (specialized):**
```
Tool 1: "Explore database structure and schema"
Tool 2: "Search content semantically about topics"
Tool 3: "Query specific facts, counts, relationships"
```

---

## Pattern 2: Descriptive Signatures

Tool names and docstrings guide selection. Be specific.

**Vague:**
```python
def search(query: str) -> str:
    """Search the database."""
```

**Specific:**
```python
def search_content_semantically(query: str) -> str:
    """Search for content about topics using semantic similarity.

    Use this tool when the user asks:
    - "What is..." or "Tell me about..."
    - Questions about strategies or concepts

    Do NOT use for counting or listing."""
```

---

## Pattern 3: Tool Composition

Complex questions may need multiple tools in sequence.

**Question:** "What are Apple's main risks and which investors are affected?"

**Agent process:**
1. Semantic search for Apple's risk content
2. Database query for investors owning Apple
3. Synthesize both results

**Agent instructions can help:**
```
"For complex questions requiring both content and facts,
use multiple tools and combine results."
```

---

## Pattern 4: Graceful Fallbacks

Handle empty results and errors gracefully.

**Poor handling:**
```
User: "What is XYZ Corp's strategy?"
Agent: Error: No results found.
```

**Graceful handling:**
```
User: "What is XYZ Corp's strategy?"
Agent: "I couldn't find specific information about XYZ Corp.
       You might want to check if XYZ Corp is in the database,
       or try a different company name."
```

---

## Pattern 5: Clear Error Messages

When tools can't answer, explain *why*.

**Unhelpful:**
```
"I don't know."
```

**Helpful:**
```
"I searched for content about quantum computing but found no relevant
documents. The database primarily contains SEC filings which may not
discuss this topic in detail."
```

This helps users understand system limitations and refine their questions.

---

## Anti-Pattern 1: Too Many Tools

Don't overwhelm the agent:

```python
tools = [
    get_schema, get_nodes, get_relationships,
    search_companies, search_products, search_risks,
    count_companies, count_products, count_risks,
    list_companies, list_products, list_risks,
    ...  # 20+ tools
]
```

**Problems:** Decision paralysis, high token costs, more errors.

**Rule of thumb:** 3-7 tools is optimal.

---

## Anti-Pattern 2: Tools That Do Everything

Don't create super-tools:

```python
def do_everything(query, mode, options, filters):
    """Does everything: schema, search, queries, aggregations..."""
    if mode == "schema":
        return get_schema()
    elif mode == "search":
        return vector_search(query)
    # ... 100 more lines
```

**Problems:** Agent doesn't know when to use it, hard to debug.

---

## Anti-Pattern 3: Vague Boundaries

Avoid ambiguous overlap:

```python
def search_documents(query):
    """Search for information in documents"""

def find_information(query):
    """Find information about topics"""
```

**When are they different?** Agent can't tell.

**Fix:** Consolidate or clearly differentiate.

---

## The GraphRAG Sweet Spot

**Three specialized tools:**

| Tool | Purpose |
|------|---------|
| Schema | Structure understanding |
| Semantic Search | Content discovery |
| Database Query | Precise facts |

**Why this works:**
- Clear non-overlapping purposes
- Covers all major question types
- Easy for agent to choose correctly
- Low token overhead

---

## Production Considerations

**Security:**
- Use read-only database credentials
- Validate generated queries
- Limit result sizes

**Performance:**
- Cache common queries
- Set appropriate timeouts
- Consider parallel tool execution

**Monitoring:**
- Log which tools are selected
- Track success/failure rates
- Monitor for improvement opportunities

---

## Summary

**Patterns:**
- **Tool Specialization:** Non-overlapping purposes
- **Descriptive Signatures:** Clear docstrings guide selection
- **Tool Composition:** Multiple tools for complex questions
- **Graceful Fallbacks:** Handle empty results informatively
- **Clear Error Messages:** Explain *why* something failed

**Anti-Patterns:**
- Too many tools (>10)
- Tools that do everything
- Vague/overlapping boundaries

**Sweet spot:** 3 specialized tools (schema, semantic search, database query).

**Next:** Workshop summary and next steps.
