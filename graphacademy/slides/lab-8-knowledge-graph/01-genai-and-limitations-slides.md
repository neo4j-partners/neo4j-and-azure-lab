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


# The GenAI Promise and Its Limits

---

## What Generative AI Does Well

LLMs excel at tasks that rely on pattern recognition and language fluency:

- **Text generation**: Creating human-like responses, summaries, explanations
- **Language understanding**: Parsing intent, extracting meaning, following instructions
- **Pattern completion**: Continuing sequences, filling in blanks, generating variations
- **Translation and transformation**: Converting between formats, styles, languages

These capabilities emerge from training on vast amounts of text data.

---

![bg contain](../../images/gen_ai_gaps.jpg)

---

## 1. Hallucination: Confident But Wrong

LLMs generate responses based on statistical likelihood, not factual verification.

**The Problem:**
- Produces the most *probable* continuation, not the most *accurate*
- Doesn't say "I don't know"—generates plausible-sounding text instead
- Complete with fabricated details and citations

**Real Example:** In 2023, US lawyers were sanctioned for submitting an LLM-generated brief with six fictitious case citations.

---

## 2. Knowledge Cutoff: No Access to Your Data

LLMs are trained at a specific point in time on publicly available data.

**They don't know:**
- Recent events after their training cutoff
- Your company's documents, databases, or internal knowledge
- Real-time data: current prices, live statistics, changing conditions

**The Risk:** Ask about your Q3 results or last week's board meeting, and the LLM may still generate a confident (and wrong) response.

---

## 3. Relationship Blindness: Can't Connect the Dots

LLMs process text sequentially and treat each piece in isolation.

**Questions they struggle with:**
- "Which asset managers own companies facing cybersecurity risks?"
- "What products are mentioned by companies that share risk factors?"
- "How are these two companies connected through their executives?"

These questions require *reasoning over relationships*—connecting entities across documents and traversing chains of connections.

---

## Why These Limitations Matter

| Limitation | Impact | Example |
|------------|--------|---------|
| Hallucination | Can't trust answers without verification | Legal brief with fabricated citations |
| Knowledge cutoff | Can't answer questions about your data | "What did our CEO say last quarter?" |
| Relationship blindness | Can't reason across connected information | "Which investors are exposed to these risks?" |

Building production AI systems means addressing these limitations directly.

---

## The Solution: Providing Context

All three limitations have a common solution—**providing context**.

When you give an LLM relevant information in its prompt:
- It has facts to work with (reduces hallucination)
- It can access your specific data (overcomes knowledge cutoff)
- You can structure that information to show relationships (enables reasoning)

This is the foundation of **Retrieval-Augmented Generation (RAG)**.

---

## Summary

In this lesson, you learned about the fundamental limitations of LLMs:

- **Hallucination**: LLMs generate probable responses, not verified facts
- **Knowledge cutoff**: LLMs can't access recent events or your private data
- **Relationship blindness**: LLMs struggle with cross-document reasoning

The solution is providing context—which leads us to RAG.

**Next:** Learn how traditional RAG works and why it has its own limitations.
