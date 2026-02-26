"""Sample queries showcasing the SEC 10-K knowledge graph."""

from __future__ import annotations

from neo4j import Driver

_W = 70


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def _header(title: str, description: str) -> None:
    print(f"\n{'=' * _W}")
    print(f"  {title}")
    print(f"{'=' * _W}")
    print(f"\n  {description}\n")


def _cypher(query: str) -> None:
    lines = query.strip().splitlines()
    indents = [len(ln) - len(ln.lstrip()) for ln in lines if ln.strip()]
    base = min(indents) if indents else 0
    print("  Cypher:")
    for ln in lines:
        print(f"    {ln[base:]}")
    print()


def _table(headers: list[str], rows: list[list], widths: list[int] | None = None) -> None:
    if not rows:
        print("  (no results)\n")
        return
    if widths is None:
        widths = []
        for i, h in enumerate(headers):
            col_max = len(h)
            for row in rows:
                col_max = max(col_max, len(str(row[i] if i < len(row) else "")))
            widths.append(min(col_max + 1, 50))
    print("  " + "  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  " + "  ".join("-" * w for w in widths))
    for row in rows:
        cells = []
        for val, w in zip(row, widths):
            s = str(val) if val is not None else "--"
            if len(s) > w:
                s = s[: w - 1] + "..."
            cells.append(s.ljust(w))
        print("  " + "  ".join(cells))
    print()


def _val(v, max_len: int = 0) -> str:
    s = str(v) if v is not None else "--"
    if max_len and len(s) > max_len:
        s = s[: max_len - 1] + "..."
    return s


# ---------------------------------------------------------------------------
# 1. Company overview
# ---------------------------------------------------------------------------

_COMPANIES_Q = """\
MATCH (c:Company)
OPTIONAL MATCH (c)-[:FACES_RISK]->(r:RiskFactor)
OPTIONAL MATCH (c)-[:OFFERS]->(p:Product)
OPTIONAL MATCH (c)-[:HAS_EXECUTIVE]->(e:Executive)
WITH c, count(DISTINCT r) AS risks, count(DISTINCT p) AS products,
     count(DISTINCT e) AS executives
RETURN c.name AS company, c.ticker AS ticker, risks, products, executives
ORDER BY c.name"""


def _company_overview(driver: Driver) -> None:
    _header(
        "1. Company Overview",
        "Companies with entity counts from SEC 10-K filings.",
    )
    _cypher(_COMPANIES_Q)
    rows, _, _ = driver.execute_query(_COMPANIES_Q)
    _table(
        ["Company", "Ticker", "Risks", "Products", "Executives"],
        [[r["company"], r["ticker"], r["risks"], r["products"], r["executives"]]
         for r in rows],
    )


# ---------------------------------------------------------------------------
# 2. Risk factors
# ---------------------------------------------------------------------------

_RISKS_Q = """\
MATCH (c:Company)-[:FACES_RISK]->(r:RiskFactor)
RETURN c.name AS company, r.name AS risk, r.description AS description
ORDER BY c.name
LIMIT $limit"""


def _risk_factors(driver: Driver, limit: int) -> None:
    _header("2. Risk Factors", "Risk factors disclosed in 10-K filings.")
    _cypher(_RISKS_Q)
    rows, _, _ = driver.execute_query(_RISKS_Q, limit=limit)
    _table(
        ["Company", "Risk", "Description"],
        [[r["company"], _val(r["risk"], 25), _val(r["description"], 40)]
         for r in rows],
    )


# ---------------------------------------------------------------------------
# 3. Products & services
# ---------------------------------------------------------------------------

_PRODUCTS_Q = """\
MATCH (c:Company)-[:OFFERS]->(p:Product)
RETURN c.name AS company, p.name AS product
ORDER BY c.name, p.name
LIMIT $limit"""


def _products(driver: Driver, limit: int) -> None:
    _header("3. Products & Services", "Products and services offered by companies.")
    _cypher(_PRODUCTS_Q)
    rows, _, _ = driver.execute_query(_PRODUCTS_Q, limit=limit)
    _table(
        ["Company", "Product"],
        [[r["company"], r["product"]] for r in rows],
    )


# ---------------------------------------------------------------------------
# 4. Executives
# ---------------------------------------------------------------------------

_EXECUTIVES_Q = """\
MATCH (c:Company)-[:HAS_EXECUTIVE]->(e:Executive)
RETURN c.name AS company, e.name AS name, e.title AS title
ORDER BY c.name, e.name
LIMIT $limit"""


def _executives(driver: Driver, limit: int) -> None:
    _header("4. Executives", "Company executives and board members.")
    _cypher(_EXECUTIVES_Q)
    rows, _, _ = driver.execute_query(_EXECUTIVES_Q, limit=limit)
    _table(
        ["Company", "Name", "Title"],
        [[r["company"], r["name"], _val(r["title"], 30)] for r in rows],
    )


# ---------------------------------------------------------------------------
# 5. Financial metrics
# ---------------------------------------------------------------------------

_METRICS_Q = """\
MATCH (c:Company)-[:REPORTS]->(m:FinancialMetric)
RETURN c.name AS company, m.name AS metric, m.value AS value, m.period AS period
ORDER BY c.name
LIMIT $limit"""


def _financial_metrics(driver: Driver, limit: int) -> None:
    _header("5. Financial Metrics", "Key financial metrics reported by companies.")
    _cypher(_METRICS_Q)
    rows, _, _ = driver.execute_query(_METRICS_Q, limit=limit)
    _table(
        ["Company", "Metric", "Value", "Period"],
        [[r["company"], _val(r["metric"], 25), _val(r["value"], 15), _val(r["period"])]
         for r in rows],
    )


# ---------------------------------------------------------------------------
# 6. Competitive landscape
# ---------------------------------------------------------------------------

_COMPETE_Q = """\
MATCH (c1:Company)-[:COMPETES_WITH]->(c2:Company)
RETURN c1.name AS company, c2.name AS competitor
ORDER BY c1.name"""


def _competitive_landscape(driver: Driver) -> None:
    _header("6. Competitive Landscape", "Companies that compete with each other.")
    _cypher(_COMPETE_Q)
    rows, _, _ = driver.execute_query(_COMPETE_Q)
    _table(
        ["Company", "Competitor"],
        [[r["company"], r["competitor"]] for r in rows],
    )


# ---------------------------------------------------------------------------
# 7. Asset manager holdings
# ---------------------------------------------------------------------------

_HOLDINGS_Q = """\
MATCH (a:AssetManager)-[r:OWNS]->(c:Company)
RETURN a.managerName AS manager, c.name AS company, r.shares AS shares
ORDER BY r.shares DESC
LIMIT $limit"""


def _asset_manager_holdings(driver: Driver, limit: int) -> None:
    _header("7. Asset Manager Holdings", "Top asset manager positions by share count.")
    _cypher(_HOLDINGS_Q)
    rows, _, _ = driver.execute_query(_HOLDINGS_Q, limit=limit)
    _table(
        ["Manager", "Company", "Shares"],
        [[r["manager"], r["company"], f"{r['shares']:,}"] for r in rows],
    )


# ---------------------------------------------------------------------------
# 8. Document-Chunk structure
# ---------------------------------------------------------------------------

_DOCS_Q = """\
MATCH (d:Document)
OPTIONAL MATCH (d)<-[:FROM_DOCUMENT]-(c:Chunk)
WITH d, count(c) AS chunks,
     sum(CASE WHEN c.embedding IS NOT NULL THEN 1 ELSE 0 END) AS embedded
RETURN d.path AS path, chunks, embedded
ORDER BY d.path NULLS LAST"""

_CHAIN_Q = """\
MATCH (c:Chunk)-[:FROM_DOCUMENT]->(d:Document)
WITH d, c ORDER BY d.path NULLS LAST, c.index NULLS LAST
WITH d, c LIMIT $limit
OPTIONAL MATCH (c)-[:NEXT_CHUNK]->(next:Chunk)
RETURN d.path AS doc, c.index AS idx,
       substring(c.text, 0, 60) AS preview,
       next.index AS next_idx"""


def _document_chunks(driver: Driver, limit: int) -> None:
    _header(
        "8. Document-Chunk Structure",
        "Documents with chunk counts and embedding stats.",
    )
    _cypher(_DOCS_Q)
    rows, _, _ = driver.execute_query(_DOCS_Q)
    if not rows:
        print("  (no documents -- run 'load' or 'enrich' first)\n")
        return
    _table(
        ["Document", "Chunks", "Embedded"],
        [[_val(r["path"], 40), r["chunks"], r["embedded"]] for r in rows],
    )

    print(f"  Chunk chain (first {limit}):\n")
    rows, _, _ = driver.execute_query(_CHAIN_Q, limit=limit)
    for r in rows:
        arrow = f" -> Chunk {r['next_idx']}" if r["next_idx"] is not None else " (end)"
        print(f"    Chunk {r['idx']:>3} | {r['preview']}...{arrow}")
    print()


# ---------------------------------------------------------------------------
# 9. Vector similarity search
# ---------------------------------------------------------------------------

_VECTOR_Q = """\
MATCH (seed:Chunk)
WHERE seed.embedding IS NOT NULL
WITH seed, rand() AS r ORDER BY r LIMIT 1
CALL db.index.vector.queryNodes(
    'chunkEmbeddings', $top_k, seed.embedding
) YIELD node, score
WHERE node <> seed
WITH seed, node, score ORDER BY score DESC LIMIT $limit
RETURN substring(seed.text, 0, 100) AS seed_text,
       score AS similarity,
       substring(node.text, 0, 100) AS match_text"""


def _vector_similarity(driver: Driver, limit: int) -> None:
    _header(
        "9. Vector Similarity Search",
        "Picks a random chunk and finds similar chunks via vector index\n"
        "  (reuses stored embeddings -- no API key needed).",
    )
    _cypher(_VECTOR_Q)
    try:
        rows, _, _ = driver.execute_query(_VECTOR_Q, limit=limit, top_k=limit + 1)
    except Exception:
        print("  (vector index not available -- run 'load' or 'enrich' first)\n")
        return
    if not rows:
        print("  (no chunks with embeddings -- run 'load' or 'enrich' first)\n")
        return
    print(f"  Seed: \"{rows[0]['seed_text']}...\"\n")
    print(f"  {'Score':<8}  Similar chunk")
    print(f"  {'-' * 8}  {'-' * 56}")
    for r in rows:
        print(f"  {r['similarity']:.4f}    {r['match_text']}...")
    print()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run_all_samples(driver: Driver, sample_size: int = 10) -> None:
    """Run all sample queries with formatted output."""
    print(f"\n{'#' * _W}")
    print("  SEC 10-K Knowledge Graph -- Sample Queries")
    print(f"{'#' * _W}")
    print(f"\n  Sample size: {sample_size} rows per section\n")

    _company_overview(driver)
    _risk_factors(driver, sample_size)
    _products(driver, sample_size)
    _executives(driver, sample_size)
    _financial_metrics(driver, sample_size)
    _competitive_landscape(driver)
    _asset_manager_holdings(driver, sample_size)
    _document_chunks(driver, sample_size)
    _vector_similarity(driver, sample_size)

    print(f"{'#' * _W}")
    print("  All samples complete.")
    print(f"{'#' * _W}\n")
