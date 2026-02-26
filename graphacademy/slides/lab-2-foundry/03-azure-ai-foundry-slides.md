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


# Microsoft Foundry

## Microsoft's AI App and Agent Factory

---

## What is Microsoft Foundry?

Microsoft describes it as:

> "An interoperable AI platform that enables developers to build faster and smarter, while organizations gain fleetwide security and governance in a unified portal."

**Key concept:** An "AI app and agent factory" for the enterprise.

---

## Key Foundry Components

| Component | Purpose |
|-----------|---------|
| **Foundry Models** | Access to 11,000+ AI models |
| **Model Router** | Auto-selects best model per task |
| **Foundry Agent Service** | Build autonomous, context-aware agents |
| **Foundry IQ** | Next-gen RAG for knowledge grounding |
| **MCP Tool Catalogue** | Unified tool discovery and management |

---

## Agents in Foundry

Foundry agents combine:

- **Instructions** - What the agent should do
- **Model** - Which LLM powers reasoning (or Model Router)
- **Tools** - MCP servers and built-in capabilities

```
┌─────────────────────────────────────────┐
│             Finance Agent               │
├─────────────────────────────────────────┤
│ Instructions: "You are a financial      │
│ analyst assistant specializing in       │
│ SEC 10-K filings analysis..."           │
├─────────────────────────────────────────┤
│ Model: gpt-5.2                           │
├─────────────────────────────────────────┤
│ Tools: Neo4j MCP Server                 │
└─────────────────────────────────────────┘
```

---

## Enterprise Governance

**Foundry Control Plane** provides:

| Capability | Description |
|------------|-------------|
| **Observability** | Monitor all agents fleet-wide |
| **Compliance** | Enforce policies across deployments |
| **Security** | Microsoft Defender + Entra ID integration |
| **Content Safety** | Built-in threat detection |

**Enterprise-ready from day one.**

---

## What We'll Build

A **Finance Agent** that:

| Capability | How |
|------------|-----|
| Understands SEC filings | Knowledge graph context |
| Queries company data | Neo4j MCP Server |
| Answers risk questions | Graph traversal |
| Analyzes relationships | Connected data |

**User:** "What risks does Apple face?"
**Agent:** Queries Neo4j, returns risk factors

---

## The Lab Flow

1. **Create** Foundry resource and project
2. **Deploy** gpt-5.2 model
3. **Create** finance-agent
4. **Add** Neo4j MCP tool
5. **Test** with SEC filing questions
6. **Publish** your agent