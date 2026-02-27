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


# Entity Resolution

---

## The Duplicate Entity Problem

When entities are extracted from text, the same real-world entity can appear with different names:

- "Neo4j" vs "Neo4j Graph Database" vs "Neo4j, Inc."
- "Apple" vs "Apple Inc" vs "Apple Inc." vs "the Company"
- "Tim Cook" vs "Timothy Cook" vs "CEO Tim Cook"

**Without resolution:** Your graph contains multiple nodes representing the same thing.

---

## Why This Breaks Queries

```cypher
// This might miss risks if Apple appears under different names
MATCH (c:Company {name: 'Apple Inc'})-[:FACES_RISK]->(r:RiskFactor)
RETURN r.name
```

If some risks are connected to "Apple" and others to "APPLE INC", your query returns incomplete results.

**You can't trust basic queries like "How many risk factors does Apple face?"**

---

## Why Entity Resolution Matters

Entity resolution ensures:

- **Query accuracy**: One node per real-world entity
- **Relationship completeness**: All relationships connect to the canonical entity
- **Aggregation correctness**: Counts and summaries reflect reality

---

## Default Resolution in SimpleKGPipeline

By default, `SimpleKGPipeline` performs basic resolution:

- Entities with the **same label** and **identical name** are merged
- "Company: Apple Inc" + "Company: Apple Inc" = one node

**But it misses variations:**
- "Apple Inc" and "APPLE INC" (case difference)
- "Apple Inc" and "Apple Inc." (punctuation)
- "Apple" and "Apple Inc" (name variation)

---

## Resolution Trade-offs

<div style="display: flex; gap: 2rem;">

<div style="flex: 1;">

### Too Aggressive

- "Apple Inc" (tech) merged with "Apple Records" (music)
- Distinct entities incorrectly combined
- Relationships become meaningless

</div>

<div style="flex: 1;">

### Too Conservative

- "Apple Inc" and "APPLE INC" remain separate
- Queries miss connections
- Aggregations are wrong

</div>

</div>

**The right balance depends on your domain.**

---

## Resolution Strategies

**Strategy 1: Upstream Normalization**

Guide the LLM during extraction:

```python
prompt_template = """
When extracting company names, normalize to official names:
- "Apple", "Apple Inc", "the Company" → "APPLE INC"
- Use uppercase for company names
- Use the full legal name when known
"""
```

---

## Strategy 2: Reference Lists

Provide a canonical list of entities:

```python
prompt_template = """
Only extract companies from this approved list:
- APPLE INC
- MICROSOFT CORP
- ALPHABET INC

Match variations to the canonical name.
"""
```

This works well when you know the entities in advance.

---

## Strategy 3: Post-Processing Resolvers

Apply resolvers after extraction:

```python
from neo4j_graphrag.experimental.components.entity_resolvers import FuzzyMatchResolver

resolver = FuzzyMatchResolver(
    driver=driver,
    similarity_threshold=0.85,  # How similar names must be to merge
)

# Run after pipeline completion
resolver.resolve()
```

**Available Resolvers:**
- **SpacySemanticMatchResolver**: Semantic similarity using spaCy
- **FuzzyMatchResolver**: String similarity using RapidFuzz

---

## Disabling Resolution

You can disable entity resolution entirely:

```python
pipeline = SimpleKGPipeline(
    driver=driver,
    llm=llm,
    embedder=embedder,
    entities=entities,
    relations=relations,
    perform_entity_resolution=False,  # No resolution
)
```

Useful for debugging or applying custom resolution logic later.

---

## Validating Resolution

After resolution, verify your entity counts:

```cypher
// Check for potential duplicates
MATCH (c:Company)
WITH c.name AS name, collect(c) AS nodes
WHERE size(nodes) > 1
RETURN name, size(nodes) AS duplicates

// Check company name variations
MATCH (c:Company)
WHERE c.name CONTAINS 'Apple' OR c.name CONTAINS 'APPLE'
RETURN c.name, count{(c)-[:FACES_RISK]->()} AS risks
```

---

## Summary

In this lesson, you learned:

- **Entity resolution** merges duplicate nodes representing the same real-world entity
- **Default resolution** catches exact matches only
- **Post-processing resolvers** catch variations using semantic or fuzzy matching
- **The trade-off**: Too aggressive merges distinct entities; too conservative keeps duplicates
- **Strategies include**: Upstream normalization, reference lists, post-processing resolvers

**Next:** Learn about vectors and semantic search.
