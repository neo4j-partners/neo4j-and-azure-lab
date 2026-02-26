"""Graph schema definitions: constraints, indexes, and extraction schema for SEC 10-K data."""

from __future__ import annotations

from neo4j import Driver

# ---------------------------------------------------------------------------
# Constraint and index definitions
# ---------------------------------------------------------------------------

# (constraint_name, label, property) triples -- one uniqueness constraint each.
CONSTRAINTS: list[tuple[str, str, str]] = [
    ("unique_company_name", "Company", "name"),
    ("unique_asset_manager_name", "AssetManager", "managerName"),
]

# Fulltext indexes: (index_name, label_clause, [properties]).
FULLTEXT_INDEXES: list[tuple[str, str, list[str]]] = [
    ("search_entities", "Company|Product|RiskFactor|Executive|FinancialMetric", ["name"]),
    ("chunkText", "Chunk", ["text"]),
]

# Constraints for entity types created by the pipeline.
# Applied AFTER pipeline runs because SimpleKGPipeline uses entity resolution
# to deduplicate -- pre-existing uniqueness constraints would cause failures
# when the same entity appears in multiple chunks.
EXTRACTION_CONSTRAINTS: list[tuple[str, str, str]] = [
    ("unique_riskfactor_name", "RiskFactor", "name"),
    ("unique_product_name", "Product", "name"),
    ("unique_executive_name", "Executive", "name"),
    ("unique_financialmetric_name", "FinancialMetric", "name"),
]


# ---------------------------------------------------------------------------
# DDL functions (all idempotent via IF NOT EXISTS)
# ---------------------------------------------------------------------------


def create_all_constraints(driver: Driver) -> None:
    """Create all uniqueness constraints (metadata + extraction)."""
    for name, label, prop in CONSTRAINTS + EXTRACTION_CONSTRAINTS:
        driver.execute_query(
            f"CREATE CONSTRAINT {name} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
        )
        print(f"  [OK] Constraint: {name} ({label}.{prop})")


def create_fulltext_indexes(driver: Driver) -> None:
    """Create fulltext indexes for search."""
    for name, label_clause, props in FULLTEXT_INDEXES:
        props_clause = ", ".join(f"n.{p}" for p in props)
        driver.execute_query(
            f"CREATE FULLTEXT INDEX {name} IF NOT EXISTS "
            f"FOR (n:{label_clause}) ON EACH [{props_clause}]"
        )
        print(f"  [OK] Fulltext index: {name}")


def create_embedding_indexes(driver: Driver, dimensions: int = 1536) -> None:
    """Create vector and fulltext indexes for Chunk embeddings.

    Imports neo4j_graphrag lazily so that other commands don't require it.
    """
    from neo4j_graphrag.indexes import create_vector_index

    try:
        create_vector_index(
            driver,
            name="chunkEmbeddings",
            label="Chunk",
            embedding_property="embedding",
            dimensions=dimensions,
            similarity_fn="cosine",
        )
        print("  [OK] Vector index: chunkEmbeddings")
    except Exception as e:
        print(f"  [WARN] Vector index: {e}")


# ---------------------------------------------------------------------------
# Extraction schema for SimpleKGPipeline
# ---------------------------------------------------------------------------


def build_extraction_schema():
    """Build a GraphSchema for SEC 10-K entity extraction.

    Defines Company, RiskFactor, Product, Executive, and FinancialMetric
    node types with their relationships.
    """
    from neo4j_graphrag.experimental.components.schema import GraphSchema

    return GraphSchema.model_validate({
        "node_types": [
            {
                "label": "Company",
                "description": "A publicly traded company",
                "properties": [
                    {"name": "name", "type": "STRING", "description": "Company name"},
                    {"name": "ticker", "type": "STRING", "description": "Stock ticker symbol"},
                ],
            },
            {
                "label": "RiskFactor",
                "description": "A risk factor disclosed in the 10-K filing",
                "properties": [
                    {"name": "name", "type": "STRING", "description": "Short name of the risk"},
                    {"name": "description", "type": "STRING", "description": "Detailed description"},
                ],
            },
            {
                "label": "Product",
                "description": "A product or service offered by the company",
                "properties": [
                    {"name": "name", "type": "STRING", "description": "Product name"},
                ],
            },
            {
                "label": "Executive",
                "description": "A company executive or board member",
                "properties": [
                    {"name": "name", "type": "STRING", "description": "Person's name"},
                    {"name": "title", "type": "STRING", "description": "Job title"},
                ],
            },
            {
                "label": "FinancialMetric",
                "description": "A financial metric or KPI",
                "properties": [
                    {"name": "name", "type": "STRING", "description": "Metric name"},
                    {"name": "value", "type": "STRING", "description": "Metric value"},
                    {"name": "period", "type": "STRING", "description": "Reporting period"},
                ],
            },
        ],
        "relationship_types": [
            {"label": "FACES_RISK", "description": "Company faces this risk factor"},
            {"label": "OFFERS", "description": "Company offers this product/service"},
            {"label": "HAS_EXECUTIVE", "description": "Company has this executive"},
            {"label": "REPORTS", "description": "Company reports this financial metric"},
            {"label": "COMPETES_WITH", "description": "Company competes with another company"},
            {"label": "PARTNERS_WITH", "description": "Company partners with another company"},
        ],
        "patterns": [
            ("Company", "FACES_RISK", "RiskFactor"),
            ("Company", "OFFERS", "Product"),
            ("Company", "HAS_EXECUTIVE", "Executive"),
            ("Company", "REPORTS", "FinancialMetric"),
            ("Company", "COMPETES_WITH", "Company"),
            ("Company", "PARTNERS_WITH", "Company"),
        ],
    })
