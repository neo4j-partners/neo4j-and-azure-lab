"""CSV loading, company metadata, asset manager relationships, clearing, and verification."""

from __future__ import annotations

import csv
from pathlib import Path

from neo4j import Driver

# ---------------------------------------------------------------------------
# Company name normalization
# ---------------------------------------------------------------------------

# Canonical company names mapped from CSV uppercase variants.
COMPANY_NAME_MAPPINGS = {
    "AMAZON": "Amazon.com, Inc.",
    "NVIDIA CORPORATION": "NVIDIA Corporation",
    "APPLE INC": "Apple Inc.",
    "PAYPAL": "PayPal Holdings, Inc.",
    "INTEL CORP": "Intel Corporation",
    "AMERICAN INTL GROUP": "American International Group, Inc.",
    "PG&E CORP": "PG&E Corporation",
    "MCDONALDS CORP": "McDonald's Corporation",
    "MICROSOFT CORP": "Microsoft Corporation",
}


def normalize_company_name(name: str) -> str:
    """Normalize a company name to its canonical form."""
    if name in COMPANY_NAME_MAPPINGS:
        return COMPANY_NAME_MAPPINGS[name]
    upper_name = name.upper()
    if upper_name in COMPANY_NAME_MAPPINGS:
        return COMPANY_NAME_MAPPINGS[upper_name]
    return name


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------


def load_company_metadata(csv_path: Path) -> dict[str, dict]:
    """Load company metadata from CSV, keyed by PDF filename."""
    companies = {}
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            path = row.get("path_Mac_ix", "")
            filename = Path(path).name if path else None
            if filename:
                companies[filename] = {
                    "name": row.get("name", ""),
                    "ticker": row.get("ticker", ""),
                    "cik": row.get("cik", ""),
                    "cusip": row.get("cusip", ""),
                }
    return companies


def load_asset_managers(csv_path: Path) -> list[dict]:
    """Load asset manager holdings from CSV."""
    holdings = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            holdings.append({
                "manager_name": row.get("managerName", ""),
                "company_name": row.get("companyName", ""),
                "shares": int(row.get("shares", 0)),
            })
    return holdings


# ---------------------------------------------------------------------------
# Node and relationship creation
# ---------------------------------------------------------------------------


def create_company_nodes(driver: Driver, companies: dict[str, dict]) -> None:
    """Create Company nodes from CSV metadata."""
    print(f"Creating {len(companies)} Company nodes...")
    with driver.session() as session:
        for filename, meta in companies.items():
            normalized_name = normalize_company_name(meta["name"])
            session.run("""
                MERGE (c:Company:__Entity__ {name: $name})
                SET c.ticker = $ticker,
                    c.cik = $cik,
                    c.cusip = $cusip
            """, name=normalized_name, ticker=meta["ticker"],
                cik=meta["cik"], cusip=meta["cusip"])
    print(f"  [OK] Created {len(companies)} Company nodes.")


def create_asset_manager_relationships(
    driver: Driver,
    holdings: list[dict],
) -> None:
    """Create AssetManager nodes and OWNS relationships."""
    print(f"Creating {len(holdings)} asset manager relationships...")
    with driver.session() as session:
        for holding in holdings:
            normalized_company = normalize_company_name(holding["company_name"])
            session.run("""
                MERGE (a:AssetManager {managerName: $manager_name})
                WITH a
                MATCH (c:Company {name: $company_name})
                MERGE (a)-[r:OWNS]->(c)
                SET r.shares = $shares
            """, manager_name=holding["manager_name"],
                company_name=normalized_company,
                shares=holding["shares"])
    print(f"  [OK] Created {len(holdings)} asset manager relationships.")


# ---------------------------------------------------------------------------
# Clear and verify
# ---------------------------------------------------------------------------


def clear_database(driver: Driver) -> None:
    """Delete all nodes, relationships, constraints, and indexes."""
    print("Clearing database...")

    # Drop all constraints first (avoids conflicts on re-load)
    constraints, _, _ = driver.execute_query("SHOW CONSTRAINTS YIELD name RETURN name")
    for row in constraints:
        driver.execute_query(f"DROP CONSTRAINT {row['name']} IF EXISTS")
    if constraints:
        print(f"  Dropped {len(constraints)} constraints.")

    # Drop all indexes (vector, fulltext, etc.)
    indexes, _, _ = driver.execute_query(
        "SHOW INDEXES YIELD name, type WHERE type <> 'LOOKUP' RETURN name"
    )
    for row in indexes:
        driver.execute_query(f"DROP INDEX {row['name']} IF EXISTS")
    if indexes:
        print(f"  Dropped {len(indexes)} indexes.")

    # Delete all nodes and relationships in batches
    deleted_total = 0
    while True:
        records, _, _ = driver.execute_query(
            "MATCH (n) WITH n LIMIT 500 DETACH DELETE n RETURN count(*) AS deleted"
        )
        count = records[0]["deleted"]
        deleted_total += count
        if count > 0:
            print(f"  Deleted {deleted_total} nodes so far...", end="\r")
        if count == 0:
            break
    print(f"\n  [OK] Database cleared ({deleted_total} nodes deleted).")


def verify(driver: Driver) -> None:
    """Print node counts per label and total relationship count."""
    # Use explicit per-label counts to avoid inflation from multi-label nodes
    # (e.g. __Entity__ + Company would double-count in a labels(n)/UNWIND approach).
    node_counts, _, _ = driver.execute_query("""
        CALL () {
            MATCH (n:Company) RETURN 'Company' AS label, count(n) AS count
            UNION ALL
            MATCH (n:RiskFactor) RETURN 'RiskFactor' AS label, count(n) AS count
            UNION ALL
            MATCH (n:Product) RETURN 'Product' AS label, count(n) AS count
            UNION ALL
            MATCH (n:Executive) RETURN 'Executive' AS label, count(n) AS count
            UNION ALL
            MATCH (n:FinancialMetric) RETURN 'FinancialMetric' AS label, count(n) AS count
            UNION ALL
            MATCH (n:AssetManager) RETURN 'AssetManager' AS label, count(n) AS count
            UNION ALL
            MATCH (n:Document) RETURN 'Document' AS label, count(n) AS count
            UNION ALL
            MATCH (n:Chunk) RETURN 'Chunk' AS label, count(n) AS count
        }
        RETURN label, count
        ORDER BY count DESC
    """)

    total_nodes, _, _ = driver.execute_query(
        "MATCH (n) RETURN count(n) AS total"
    )

    print()
    print("=" * 50)
    print("Node Counts:")
    for row in node_counts:
        if row["count"] > 0:
            print(f"  {row['label']}: {row['count']:,}")
    print(f"  ---------------------")
    print(f"  Total Nodes: {total_nodes[0]['total']:,}")

    rel_records, _, _ = driver.execute_query("""
        MATCH ()-[r]->()
        RETURN type(r) AS type, count(r) AS count
        ORDER BY count DESC
    """)
    print(f"\nRelationship Counts:")
    total_rels = 0
    for row in rel_records:
        print(f"  {row['type']}: {row['count']:,}")
        total_rels += row["count"]
    print(f"  ---------------------")
    print(f"  Total Relationships: {total_rels:,}")
    print("=" * 50)
