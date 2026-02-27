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


# Text2Cypher Retriever

---

## From Natural Language to Database Queries

**The problem:** Some questions need precise facts, not semantic search.

**Text2Cypher solution:**
1. User asks a question in natural language
2. LLM generates a Cypher query from the question
3. Query executes against the graph
4. Precise, structured results returned

**Example:**
- Question: "How many risk factors does Apple face?"
- Generated: `MATCH (c:Company {name:'APPLE INC'})-[:FACES_RISK]->(r) RETURN count(r)`
- Result: `45`

---

## How It Works

```
User: "Which companies does BlackRock own?"
    ↓
[LLM + Schema] → Generate Cypher
    ↓
MATCH (am:AssetManager {managerName: 'BlackRock Inc.'})
      -[:OWNS]->(c:Company)
RETURN c.name
    ↓
[Execute Query]
    ↓
Result: Apple Inc., Microsoft Corp., Alphabet Inc., ...
```

---

## Creating a Text2Cypher Retriever

```python
from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.schema import get_schema

# Schema tells LLM what's queryable
schema = get_schema(driver)

text2cypher_retriever = Text2CypherRetriever(
    driver=driver,
    llm=llm,                    # LLM for Cypher generation
    neo4j_schema=schema         # Graph structure
)
```

**The schema is critical:** Without it, the LLM guesses (often incorrectly).

---

## The Role of Schema

**Schema tells the LLM:**
```
Node properties:
  Company {name: STRING, ticker: STRING}
  RiskFactor {name: STRING}
  AssetManager {managerName: STRING}

Relationships:
  (:Company)-[:FACES_RISK]->(:RiskFactor)
  (:AssetManager)-[:OWNS]->(:Company)
```

**With schema:** LLM knows exactly what entities and relationships exist.
**Without schema:** LLM invents non-existent properties and relationships.

---

## Best For

**Use Text2Cypher when:**

- You need precise facts, counts, or lists
- Question is about specific entities
- Aggregations are needed
- Direct graph queries (no semantic search)

**Example questions:**
- "How many risk factors does Apple face?"
- "List all companies owned by Vanguard"
- "Which company has the most products?"
- "What is the average number of risks per company?"

---

## Performing a Search

```python
query = "What companies does BlackRock own?"

results = text2cypher_retriever.search(query_text=query)

# Results contain:
# - The generated Cypher query
# - The query results
for record in results.records:
    print(record)
```

**Behind the scenes:** LLM analyzes your question, generates Cypher, executes it.

---

## Limitations

**Text2Cypher requires questions that map to schema:**

- Question: "What's the sentiment about AI regulation?"
- Problem: No "sentiment" property in schema
- Result: Cannot generate valid query

**Text2Cypher may struggle with:**
- Ambiguous questions
- Questions requiring interpretation
- Content that lives in text chunks (use Vector instead)

---

## Security Considerations

Text2Cypher executes LLM-generated queries. Important safeguards:

- **Use read-only credentials**: Prevent accidental data modification
- **Validate queries**: Check for dangerous operations (DELETE, DROP)
- **Limit results**: Ensure LIMIT clauses prevent unbounded returns
- **Monitor usage**: Log generated queries for review
- **Trust boundaries**: Don't expose to untrusted users

---

## Generated Query Quality

**LLMs may generate imperfect Cypher:**

- Syntax errors
- Deprecated syntax
- Non-existent properties
- Inefficient patterns

**Mitigation:**
- Use custom prompts to guide Cypher generation
- Validate generated queries
- Handle errors gracefully

---

## Comparing All Three Retrievers

| Question | Best Retriever | Why |
|----------|---------------|-----|
| "What is AI safety?" | Vector | Semantic content |
| "Which companies mention AI?" | Vector Cypher | Content + entities |
| "How many companies mention AI?" | Text2Cypher | Precise count |
| "Tell me about Apple" | Vector | Exploratory content |
| "List Apple's risks" | Text2Cypher | Specific entity facts |

---

## Summary

Text2Cypher Retriever converts natural language to database queries:

- **LLM generates Cypher** from your question
- **Schema guides generation** for accuracy
- **Best for:** Facts, counts, lists, specific entities
- **Limitation:** Questions must map to graph schema

**You now know all three retrieval patterns:**
- Vector: Semantic content
- Vector Cypher: Content + relationships
- Text2Cypher: Precise facts

**Next:** Learn to build agents that choose the right retriever automatically.
