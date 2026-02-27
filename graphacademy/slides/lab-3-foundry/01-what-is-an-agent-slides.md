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


# What is an AI Agent?

---

## The Evolution of AI Assistants

From simple Q&A to intelligent agents:

| Generation | Capability | Limitation |
|------------|------------|------------|
| **Chatbots** | Pre-scripted responses | No real understanding |
| **LLMs** | Natural language understanding | No access to external data |
| **RAG** | Retrieval + Generation | Single retrieval strategy |
| **Agents** | Reasoning + Tools + Action | Full autonomy |

---

## What is an Agent?

An agent is an LLM with access to **tools**.

| Component | What It Does |
|-----------|--------------|
| **Reasoning** | LLM analyzes the question and decides what to do |
| **Tools** | Capabilities the agent can call (search, query, etc.) |
| **Action** | Executes the selected tool(s) and returns results |

---

## How Agents Use Tools

Agents take action by calling tools—functions that get information or perform tasks.

**How tool selection works:**

| Question | Agent Reasoning | Tool Selected |
|----------|-----------------|---------------|
| "How many companies?" | Needs a count | `query_database` |
| "What risks does Apple face?" | Needs content search | `search_content` |
| "What's in the database?" | Needs structure | `get_graph_schema` |

The agent matches the question to the best tool description.

---

## The ReAct Pattern

Agents follow **ReAct** (Reasoning + Acting):

```
1. Receive question: "How many risk factors does Apple face?"
2. Reason: "This asks for a count"
3. Act: Call Database Query Tool
4. Observe: Result = 45
5. Respond: "Apple faces 45 risk factors."
```

For complex questions, the agent may loop through multiple cycles.

---

## Multi-Tool Example

**Question:** "What are Apple's main risks and which investors are affected?"

**Agent process:**
1. **Reason:** Need risk content AND investor relationships
2. **Act:** Call Semantic Search for Apple's risks
3. **Observe:** Risk descriptions
4. **Reason:** Now need investors
5. **Act:** Call Database Query for Apple's investors
6. **Observe:** Investor list
7. **Respond:** Combine both into comprehensive answer

---

## Why Agents Matter

**Without agents:**
- Build separate interfaces for each capability
- Force users to choose which tool to use
- Complex user experience

**With agents:**
- Users ask natural questions
- System figures out how to answer
- Conversational, intuitive experience

---

## Agents vs Traditional Software

| Aspect | Traditional Software | AI Agents |
|--------|---------------------|-----------|
| **Input** | Structured commands | Natural language |
| **Logic** | Pre-programmed rules | LLM reasoning |
| **Flexibility** | Fixed workflows | Dynamic tool selection |
| **Adaptation** | Code changes needed | Learns from context |

---

## Summary

In this lesson, you learned:

- **Agents** have four components: Perception, Reasoning, Action, Response
- **Tools** are capabilities agents use to take action
- **Selection** happens through semantic matching to tool descriptions
- **ReAct pattern**: Reason → Act → Observe → Respond
- **Result**: Users ask naturally; agents figure out how to answer

**Next:** Learn about the Model Context Protocol (MCP).
