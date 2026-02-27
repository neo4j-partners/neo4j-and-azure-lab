# Workshop Slides

This folder contains presentation-ready slides extracted from the workshop lessons. All slides are formatted for [Marp](https://marp.app/), a markdown presentation tool.

## 📊 Available Presentations

All slides are organized by lab module for easy navigation.

### Lab 1: Neo4j Aura & Aura Agents (Slides 1-6) 🆕

**01. Neo4j Aura Overview** (3.5 KB) 🆕
   - What is Neo4j Aura
   - Cloud Graph Database Benefits
   - Value for AI/GenAI Applications
   - Getting Started

**02. The GenAI Promise and Its Limits** (4.2 KB) 🆕
   - What Generative AI Does Well
   - The Three Core Limitations
   - Hallucination, Knowledge Cutoff, Relationship Blindness
   - The Solution: Providing Context

**03. Traditional RAG: Chunking and Vector Search** (5.5 KB) 🆕
   - How Traditional RAG Works
   - Why Chunking Matters
   - Common Chunking Strategies
   - What is a Vector / What are Embeddings
   - The Smart Librarian Analogy
   - Without Vectors vs With Vectors
   - Similarity Search

**04. Context and the Limits of Traditional RAG** (4.5 KB) 🆕
   - The Power of Context
   - The Problem with Traditional RAG
   - What Traditional RAG Misses
   - Questions RAG Can't Answer
   - The GraphRAG Solution

**05. The SEC Filings Knowledge Graph** (3.5 KB) 🆕
   - SEC 10-K Filings Example
   - From PDF to Graph
   - What the Graph Enables
   - Your Pre-Built Knowledge Graph
   - Processing Pipeline Preview

**06. Aura Agents** (6.5 KB) 🆕
   - No-Code GraphRAG Platform
   - Three-Tool Architecture (Cypher Templates, Similarity Search, Text2Cypher)
   - Tool Selection and Reasoning
   - Agent Configuration
   - Testing and Deployment
   - Bridge to Code-Based Implementation

### Lab 3: Microsoft Foundry & MCP (Slides 1-3)

**01. What is an AI Agent** (4.0 KB)
   - Evolution of AI Assistants
   - Agent Components (Perception, Reasoning, Action, Response)
   - Tools and How Agents Choose Them
   - The ReAct Pattern
   - Multi-Tool Examples

**02. What is MCP (Model Context Protocol)** (3.5 KB)
   - The Tool Integration Problem
   - MCP as "USB for AI Tools"
   - MCP Architecture (Host, Client, Server)
   - Neo4j MCP Server
   - Benefits of Standardization

**03. Microsoft Foundry** (5.0 KB)
   - Evolution: Azure AI Studio → Microsoft Foundry
   - Foundry by the Numbers (11,000+ models, 1,400+ connectors)
   - Key Components (Foundry Models, Model Router, Agent Service, Foundry IQ)
   - MCP Tool Catalogue
   - Enterprise Governance (Control Plane)

### Lab 5: Foundry Agents (Slides 1-2)

**01. The Microsoft Agent Framework**
   - Why Agents Need a Framework (LLMs Are Stateless)
   - Core Concepts: Agents, Tools, Context Providers, Sessions, Middleware
   - The Agent Lifecycle (before_run → LLM → after_run)
   - Tools vs Context Providers Comparison
   - Key API: AzureOpenAIResponsesClient, as_agent(), run_stream()
   - Sessions and Persistent State

**02. Tools and Context Providers**
   - Defining Tools with Type Annotations
   - Annotated + Field for Parameter Descriptions
   - How Tool Selection Works (Docstrings)
   - BaseContextProvider Lifecycle Hooks
   - before_run(): Injecting Instructions and Messages
   - after_run(): Extracting Structured Data with Pydantic
   - Session State Persistence

### Lab 6: Neo4j Context Providers (Slides 1-2)

**01. Neo4j Context Providers**
   - What is Neo4jContextProvider (agent-framework-neo4j)
   - How before_run() Works (Messages → Search → Format → Inject)
   - Three Search Modes: Vector, Fulltext, Hybrid
   - Configuration Options (top_k, message_history_count, context_prompt)
   - Result Formatting with Scores and Metadata
   - Retriever Selection Logic

**02. Graph-Enriched Context**
   - Why Vector Search Alone Isn't Enough
   - The retrieval_query Parameter
   - Two-Step Process: Index Search → Cypher Traversal
   - Example Retrieval Query (Company → Risks, Products)
   - Before/After: Plain Chunk vs Graph-Enriched Context

### Lab 7: Agent Memory (Slides 1-2)

**01. Neo4j Agent Memory**
   - The Problem: Agents Forget Between Sessions
   - What is neo4j-agent-memory
   - Short-Term Memory: Messages with Embeddings
   - Long-Term Memory: Entities, Facts (SPO Triples), Preferences
   - Reasoning Memory: Tool Call Traces and Outcomes
   - Graph Data Model
   - How Memory Differs from Knowledge Graph Context

**02. Memory Context Provider and Tools**
   - Memory Context Provider: before_run() and after_run()
   - What Gets Injected from Each Memory Type
   - The Six Memory Tools
   - Context Provider vs Memory Tools
   - Combining Both Approaches
   - Entity Extraction and Deduplication

### Lab 8: Building Knowledge Graphs (Slides 1-7)

**01. The GenAI Promise and Its Limits** (4.2 KB)
   - What Generative AI Does Well
   - The Three Core Limitations
   - Hallucination, Knowledge Cutoff, Relationship Blindness
   - The Solution: Providing Context

**02. Context and RAG** (4.5 KB)
   - Importance of Context
   - Retrieval Augmented Generation (RAG)
   - How RAG Works
   - The Problem with Traditional RAG
   - The GraphRAG Solution

**03. Building Knowledge Graphs** (11 KB) ⭐ **Largest**
   - Complete GraphRAG Pipeline
   - EDGAR SEC Filings Processing
   - Entity Extraction
   - Schema-Driven Knowledge Graphs
   - Structured Data Integration

**04. Schema Design** (4.7 KB)
   - Schema Purpose & Benefits
   - Node and Relationship Definitions
   - Pattern Specifications
   - Iterative Schema Development
   - Balancing Flexibility and Structure

**05. Chunking Strategies** (5.1 KB)
   - Chunk Size Optimization
   - Large vs Small Chunk Trade-offs
   - FixedSizeSplitter Configuration
   - Chunk Overlap Strategies
   - Impact on Entity Extraction
   - Best Practices by Document Type

**06. Entity Resolution** (6.3 KB)
   - Entity Duplication Problem
   - Default Resolution Strategies
   - Post-Processing Resolvers (Spacy, FuzzyMatch)
   - Conservative vs Aggressive Resolution
   - Best Practices and Testing

**07. Vectors** (4.8 KB)
   - Vector Fundamentals
   - Embeddings & Similarity
   - Vector Search in Neo4j
   - Document Chunking

### Lab 10: GraphRAG Retrievers (Slides 1-4)

**01. Retrievers Overview** (5.2 KB)
   - What is GraphRAG?
   - Benefits of GraphRAG
   - Retriever Types Overview

**02. Vector Retriever** (6.0 KB)
   - Vector Retriever Fundamentals
   - How Vector Search Works (5-step process)
   - Components: Embedder, Vector Index, Similarity, Top-K
   - Configuration and Code Examples
   - Best Practices and Use Cases

**03. Vector + Cypher Retriever** (8.9 KB)
   - Hybrid Retrieval (Semantic + Graph)
   - Two-Step Process Explained
   - Custom Retrieval Query Patterns
   - OPTIONAL MATCH Usage
   - Advanced Traversals and Metadata

**04. Text2Cypher Retriever** (8.1 KB)
   - Natural Language to Cypher Conversion
   - Schema's Critical Role
   - LLM Query Generation Process
   - Modern Cypher Syntax Best Practices
   - Complex Query Handling

### Lab 9: Intelligent Agents (Slides 1-5)

**01. From Retrievers to Agents** (3.7 KB)
   - What are Agents?
   - Agents vs Retrievers
   - Agent Reasoning & Tools

**02. Microsoft Agent Framework** (3.6 KB)
   - Building Agents with Microsoft Agent Framework
   - AzureOpenAIResponsesClient Setup
   - Schema Tools
   - Agent Architecture
   - Tool Definition as Python Functions

**03. Building Your Agent** (8.9 KB)
   - Single-Tool to Multi-Tool Progression
   - Schema Tool, Vector Tool, Text2Cypher Tool
   - How Agents Decide Which Tool to Use
   - Agent Instructions and Streaming

**04. Agent Design Patterns** (11.8 KB)
   - Tool Selection Process
   - Progressive Enhancement Pattern
   - Tool Specialization Principles
   - Design Patterns (Naming, Docstrings, Composition)
   - Anti-Patterns to Avoid
   - The GraphRAG "Sweet Spot" (3 Tools)

**05. Congratulations** (2.0 KB)
   - Workshop Summary
   - What You Built
   - Next Steps

## 🚀 How to Use These Slides

### Option 1: Marp CLI (Recommended)

Install Marp CLI:
```bash
npm install -g @marp-team/marp-cli
```

**Present slides:**
```bash
cd /path/to/slides
marp 01-what-is-genai-slides.md --server
```

**Export to PDF:**
```bash
marp 01-what-is-genai-slides.md --pdf
```

**Export to HTML:**
```bash
marp 01-what-is-genai-slides.md --html
```

**Export all slides:**
```bash
marp *.md --pdf --allow-local-files
```

### Option 2: VS Code with Marp Extension

1. Install the [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) extension
2. Open any slide file
3. Click "Open Preview" button or press `Cmd+K V`
4. Present using the preview window

### Option 3: Marp Web

1. Visit [Marp Web](https://web.marp.app/)
2. Copy and paste slide content
3. Present directly in browser

## 📝 Slide Format

All slides use Marp markdown format:

```markdown
---
marp: true
theme: default
paginate: true
---

# Slide Title

Content here

---

# Next Slide

More content
```

### Features Included

✅ **Pagination** - Automatic slide numbering
✅ **Images** - All images linked to `../images/`
✅ **Code Blocks** - Syntax-highlighted Cypher and Python
✅ **Tables** - Comparison and decision matrices
✅ **Two-Column Layouts** - Where appropriate
✅ **Consistent Styling** - Professional appearance

## 🎨 Customizing Theme

To use a different Marp theme, change the YAML frontmatter:

```markdown
---
marp: true
theme: gaia
paginate: true
backgroundColor: #fff
---
```

Available themes:
- `default` - Clean, professional
- `gaia` - Colorful, modern
- `uncover` - Minimalist, centered

Or create your own custom theme!

## 📊 Presentation Order

### For Full Workshop (5 hours):

**Part 1: GenAI Fundamentals (90 min)**
1. Slide 01: What is Generative AI (15 min)
2. Slide 02: LLM Limitations (15 min)
3. Slide 03: Context (10 min)
4. Slide 04: Building the Graph (20 min)
5. Slide 05: Schema Design (10 min)
6. Slide 06: Chunking Strategies (10 min)
7. Slide 07: Entity Resolution (10 min)

**Part 2: Vectors & Full Scale (40 min)**
8. Slide 08: Vectors (20 min)
9. Slide 09: Working with Full Datasets (20 min)

**Part 3: GraphRAG Retrievers (90 min)**
10. Slide 10: GraphRAG Explained (15 min)
11. Slide 11: What is a Retriever (15 min)
12. Slide 12: Vector Retriever (15 min)
13. Slide 13: Vector + Cypher Retriever (20 min)
14. Slide 14: Text2Cypher Retriever (15 min)
15. Slide 15: Choosing the Right Retriever (10 min)

**Part 4: Intelligent Agents (90 min)**
16. Slide 16: What is an Agent (10 min)
17. Slide 17: Microsoft Agent Framework (15 min)
18. Slide 18: Simple Schema Agent (15 min)
19. Slide 19: Vector Graph Agent (15 min)
20. Slide 20: Text2Cypher Agent (15 min)
21. Slide 21: Multi-Tool Agent Design (10 min)
22. Slide 22: Aura Agents (10 min)

### For Short Workshop (2.5 hours):

**Essential Slides:**
1. Slide 01: What is Generative AI (10 min)
2. Slide 02: LLM Limitations (10 min)
3. Slide 04: Building the Graph (15 min)
4. Slide 08: Vectors (15 min)
5. Slide 11: What is a Retriever (15 min)
6. Slide 15: Choosing the Right Retriever (10 min)
7. Slide 16: What is an Agent (10 min)
8. Slide 18: Simple Schema Agent (15 min)
9. Slide 21: Multi-Tool Agent Design (10 min)
10. Slide 22: Aura Agents (10 min)

### For Theory-Only Session (1.5 hours):

**Conceptual Overview:**
1. Slide 01: What is Generative AI (10 min)
2. Slide 02: LLM Limitations (10 min)
3. Slide 05: Schema Design (10 min)
4. Slide 08: Vectors (15 min)
5. Slide 10: GraphRAG Explained (10 min)
6. Slide 11: What is a Retriever (10 min)
7. Slide 15: Choosing the Right Retriever (10 min)
8. Slide 16: What is an Agent (10 min)
9. Slide 21: Multi-Tool Agent Design (10 min)

## 🖼️ Images

All slides reference images in the `../images/` directory. Make sure the images folder is at the same level as the graphacademy folder:

```
neo4j-and-azure-lab/
├── images/              ← Images here
└── graphacademy/
    └── slides/          ← Slides here
```

## 💡 Tips for Presenting

1. **Test beforehand** - Run through slides before presenting
2. **Use presenter mode** - Marp CLI has a presenter mode with notes
3. **Adjust timing** - Each slide deck has suggested duration
4. **Interactive demos** - Pause slides for hands-on exercises in labs
5. **Export PDFs** - Create backup PDFs in case of technical issues
6. **Know your audience** - Use short vs full workshop timing based on audience

## 🔧 Troubleshooting

**Images not showing?**
- Ensure `images/` folder is at correct location (../images from slides/)
- Use `--allow-local-files` flag with Marp CLI

**Formatting issues?**
- Update Marp CLI: `npm update -g @marp-team/marp-cli`
- Try different themes

**PDF export fails?**
- Install Chromium: `npx @marp-team/marp-cli --version`
- Use `--allow-local-files` flag

## 📦 Export All Presentations

**Create PDFs for all slides:**
```bash
cd /path/to/slides
for file in [0-9]*.md; do
  marp "$file" --pdf --allow-local-files
done
```

**Create HTML presentations:**
```bash
for file in [0-9]*.md; do
  marp "$file" --html --allow-local-files
done
```

## 📚 Additional Resources

- [Marp Documentation](https://marpit.marp.app/)
- [Marp CLI Usage](https://github.com/marp-team/marp-cli)
- [Marp Themes](https://github.com/marp-team/marp-core/tree/main/themes)
- [Creating Custom Themes](https://marpit.marp.app/theme-css)
- [GraphAcademy Lessons](../README.md) - Corresponding lesson content

## 🎯 Quick Start

```bash
# Install Marp
npm install -g @marp-team/marp-cli

# Navigate to slides
cd /path/to/graphacademy/slides

# Start presenting first slide
marp 01-what-is-genai-slides.md --server

# Browser will open with presentation
# Use arrow keys to navigate
# Press 'F' for fullscreen
```

---

## 📈 Slide Statistics

**Total Presentations:** 31
**Total Slide Pages:** ~360 individual slides
**Format:** Marp Markdown
**Status:** ✅ Ready to present

### Lab Breakdown
- **Lab 1:** 6 presentations (Neo4j Aura, GenAI Limits, Traditional RAG, GraphRAG Limits, SEC Filings Graph, Aura Agents)
- **Lab 3:** 3 presentations (What is an Agent, MCP, Microsoft Foundry)
- **Lab 5:** 2 presentations (Microsoft Agent Framework, Tools and Context Providers)
- **Lab 6:** 2 presentations (Neo4j Context Providers, Graph-Enriched Context)
- **Lab 7:** 2 presentations (Agent Memory Overview, Memory Tools)
- **Lab 8:** 7 presentations (GenAI Fundamentals, Knowledge Graphs)
- **Lab 9:** 5 presentations (Intelligent Agents)
- **Lab 10:** 4 presentations (GraphRAG Retrievers)

### New Slides Added (February 27, 2026)
- 01: The Microsoft Agent Framework (lab-5-foundry-agents)
- 02: Tools and Context Providers (lab-5-foundry-agents)
- 01: Neo4j Context Providers (lab-6-context-providers)
- 02: Graph-Enriched Context (lab-6-context-providers)
- 01: Neo4j Agent Memory (lab-7-agent-memory)
- 02: Memory Context Provider and Tools (lab-7-agent-memory)

### Previous Updates
- December 3, 2025: Added Lab 3 slides covering AI Agents, MCP, and Microsoft Foundry

**Latest Update:** Added Lab 5, 6, 7 slides; renamed folders to match current lab numbers; updated Lab 9 MAF slide API references
**Version:** 3.0 (February 27, 2026)
