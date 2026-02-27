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


# What is MCP?

## Model Context Protocol

---

## The Problem: Tool Integration

Every AI framework has its own way of defining tools:

- **OpenAI**: Function calling with JSON schemas
- **Anthropic**: Tool use with specific formats
- **LangChain**: Tool wrappers and chains
- **Custom Agents**: Proprietary integrations

**Result:** Building tools once means rebuilding for each framework.

---

## The Solution: MCP

**Model Context Protocol (MCP)** is an open standard for connecting AI models to external tools and data sources.

Think of it as **USB for AI tools**:

| USB | MCP |
|-----|-----|
| Standard port for devices | Standard protocol for AI tools |
| Plug any device into any computer | Plug any tool into any AI model |
| One cable, many devices | One server, many clients |

---

## MCP vs Standard APIs: Who Is It Built For?

The biggest difference is **who the server is built for**.

| Standard API (REST/GraphQL) | MCP Server |
|-----------------------------|------------|
| **Built for Programmers** | **Built for AI Models** |
| Assumes you've read the manual | Assumes the AI knows nothing |
| You must know endpoints exist | Server tells AI what's available |
| `/users`, `/invoices`, etc. | "Here are 5 things I can do" |

---

## "Read the Manual" vs "Ask Me"

**Standard API:** Passive. If you don't know the magic words, you get an error.

**MCP Server:** Active and self-documenting. Discovery is built-in.

```
AI: "Hello, what can you do?"

MCP Server: "I can read these 3 files (Resources), and I have
            a tool called query_graph that requires a cypher
            parameter (Tool)."

AI: "Great, I'll use that."
```

**The AI doesn't need documentation—it asks the server directly.**

---

## MCP Architecture

**How an Agent fits in:**

| Component | Role | Example |
|-----------|------|---------|
| **Agent** | The AI client hosted in Foundry | Foundry Agent |
| **Tools** | Capabilities the agent can use | MCP Servers |
| **MCP Server** | Provides tools via the protocol | Neo4j MCP Server |

The Agent has tools—MCP servers are one way to provide those tools.

---

## What MCP Servers Provide

MCP servers can expose:

- **Tools** - Functions the AI can call (query database, search, etc.)
- **Resources** - Data the AI can read (files, database schemas)
- **Prompts** - Pre-defined prompt templates

---

## Benefits of MCP

| Benefit | Description |
|---------|-------------|
| **Standardization** | One protocol for all tools |
| **Reusability** | Build once, use everywhere |
| **Security** | Controlled access to resources |
| **Composability** | Combine multiple servers |
| **Ecosystem** | Growing library of servers |

---

## Neo4j MCP Server

The **Neo4j MCP Server** is an official MCP implementation that gives AI agents the ability to:

- **Explore** your graph schema
- **Read** data using Cypher queries
- **Write** data (only when explicitly enabled)

It's the bridge between natural language questions and graph database answers.

---

## Core Tools Provided

The Neo4j MCP Server exposes three main tools:

| Tool | Purpose | Default |
|------|---------|---------|
| **get_neo4j_schema** | Retrieve graph structure | Always enabled |
| **read_neo4j_cypher** | Execute read queries | Always enabled |
| **write_neo4j_cypher** | Execute write queries | **Disabled by default** |

---

## Tool 1: Get Schema

```
get_neo4j_schema
```

Returns the structure of your knowledge graph:

- **Node labels** (e.g., Company, RiskFactor, Filing)
- **Relationship types** (e.g., HAS_RISK, FILED)
- **Properties** on nodes and relationships

**Why it matters:** The AI needs to understand your data model before it can write correct Cypher queries.

---

## Tool 2: Read Cypher

```
read_neo4j_cypher
```

Executes **read-only** Cypher queries against the database.

**Example flow:**
```
User: "What risks does Apple face?"

AI uses read_neo4j_cypher:
MATCH (c:Company {name: 'Apple Inc'})-[:HAS_RISK]->(r:RiskFactor)
RETURN r.description

Result: [List of risk factors from SEC filings]
```

**Safe by design:** Cannot modify any data.

---

## Tool 3: Write Cypher

```
write_neo4j_cypher
```

Executes queries that **create, update, or delete** data.

**Important:** This tool is **disabled by default** for safety.

To enable, you must explicitly configure:
```json
{
  "neo4j_write_enabled": true
}
```

---

## In This Lab

We'll use the Neo4j MCP Server with:

- **get_neo4j_schema** - To help the agent understand our SEC filings graph
- **read_neo4j_cypher** - To answer questions about companies and risks

**Write access is not needed** - we're analyzing existing data.

---

## Summary

- **MCP** is an open standard for AI tool integration
- Works like **USB for AI** - one protocol, many tools
- **Neo4j MCP Server** provides three tools for graph access
- **Secure-by-default** design prevents accidental data modification
- **Microsoft Foundry** supports MCP out of the box

**Next:** Learn about Microsoft Foundry and deploy your agent.
