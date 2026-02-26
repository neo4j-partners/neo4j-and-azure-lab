"""
Test Neo4j connection and schema retrieval.

Run with: uv run python solutions/test_connection.py
"""

from azure.identity import DefaultAzureCredential
from neo4j_graphrag.schema import get_schema
from openai import OpenAI

from config import get_neo4j_driver, Neo4jConfig, get_agent_config


def print_section(title: str, items: list[str]) -> None:
    """Print a section with title and items."""
    print("=" * 50)
    print(title)
    print("=" * 50)
    if items:
        for item in items:
            print(f"  {item}")
    else:
        print("  (none found)")
    print()


def print_schema_sections(schema: str) -> None:
    """Parse and print schema in sections."""
    if not schema or not schema.strip():
        print("WARNING: Schema is empty. Database may not be populated.")
        return

    lines = schema.strip().split("\n")

    # Group lines by section
    node_lines = []
    rel_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("(:") or "Node" in line:
            node_lines.append(line)
        elif line.startswith("[:") or "Relationship" in line or "->" in line:
            rel_lines.append(line)
        else:
            # Default to node section for unrecognized lines
            node_lines.append(line)

    print_section("NODE LABELS", node_lines)
    print_section("RELATIONSHIPS", rel_lines)


def get_database_counts(driver) -> tuple[int, int]:
    """Get total count of nodes and relationships in the database."""
    node_records, _, _ = driver.execute_query("MATCH (n) RETURN count(n) AS cnt")
    rel_records, _, _ = driver.execute_query("MATCH ()-[r]->() RETURN count(r) AS cnt")
    node_count = node_records[0]["cnt"] if node_records else 0
    rel_count = rel_records[0]["cnt"] if rel_records else 0
    return node_count, rel_count


def get_entity_count(driver, entity_type: str, labels: list[str]) -> int | None:
    """Get count of entities matching the index."""
    if not labels:
        return None
    try:
        if entity_type == "NODE":
            label = labels[0]
            query = f"MATCH (n:`{label}`) RETURN count(n) AS cnt"
        elif entity_type == "RELATIONSHIP":
            rel_type = labels[0]
            query = f"MATCH ()-[r:`{rel_type}`]->() RETURN count(r) AS cnt"
        else:
            return None
        records, _, _ = driver.execute_query(query)
        return records[0]["cnt"] if records else None
    except Exception:
        return None


def get_indexes(driver) -> list[str]:
    """Get all indexes from the database."""
    indexes = []
    records, _, _ = driver.execute_query("SHOW INDEXES")
    for record in records:
        name = record.get("name", "unknown")
        index_type = record.get("type", "unknown")
        entity_type = record.get("entityType", "unknown")
        labels = record.get("labelsOrTypes", [])
        properties = record.get("properties", [])
        state = record.get("state", "unknown")

        labels_str = ":".join(labels) if labels else ""
        props_str = ", ".join(properties) if properties else ""

        # Get count of indexed entities
        count = get_entity_count(driver, entity_type, labels)
        count_str = f" - {count:,} entities" if count is not None else ""

        indexes.append(f"{name} ({index_type}) on {entity_type} {labels_str}({props_str}) [{state}]{count_str}")
    return indexes


def get_constraints(driver) -> list[str]:
    """Get all constraints from the database."""
    constraints = []
    records, _, _ = driver.execute_query("SHOW CONSTRAINTS")
    for record in records:
        name = record.get("name", "unknown")
        constraint_type = record.get("type", "unknown")
        entity_type = record.get("entityType", "unknown")
        labels = record.get("labelsOrTypes", [])
        properties = record.get("properties", [])

        labels_str = ":".join(labels) if labels else ""
        props_str = ", ".join(properties) if properties else ""
        constraints.append(f"{name} ({constraint_type}) on {entity_type} {labels_str}({props_str})")
    return constraints


def test_azure_model_connection() -> bool:
    """Test Microsoft Foundry model connection via OpenAI-compatible endpoint."""
    config = get_agent_config()
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")

    print(f"Endpoint: {config.inference_endpoint}")
    print(f"Model: {config.model_name}")
    print()

    client = OpenAI(
        base_url=config.inference_endpoint,
        api_key=token.token,
    )

    try:
        response = client.chat.completions.create(
            model=config.model_name,
            messages=[{"role": "user", "content": "Say 'hello' in one word."}],
            max_completion_tokens=10,
        )
        print(f"Model response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"Model connection failed: {e}")
        return False


def main():
    print("Testing Neo4j connection...")
    print("-" * 50)

    # Show configuration (without password)
    config = Neo4jConfig()
    print(f"URI: {config.uri}")
    print(f"Username: {config.username}")
    print()

    # Test connection
    with get_neo4j_driver() as driver:
        driver.verify_connectivity()
        print("Connection successful!")
        print()

        # Get database counts
        node_count, rel_count = get_database_counts(driver)
        print_section("DATABASE COUNTS", [
            f"Nodes: {node_count:,}",
            f"Relationships: {rel_count:,}",
        ])

        # Get schema
        print("GRAPH SCHEMA")
        print()
        schema = get_schema(driver)
        print_schema_sections(schema)

        # Get indexes
        indexes = get_indexes(driver)
        print_section("INDEXES", indexes)

        # Get constraints
        constraints = get_constraints(driver)
        print_section("CONSTRAINTS", constraints)

    # Test Microsoft Foundry model connection
    print("=" * 50)
    print("Microsoft Foundry Model")
    print("=" * 50)
    if test_azure_model_connection():
        print("Model connection successful!")
    else:
        print("WARNING: Model connection failed")
    print()


if __name__ == "__main__":
    main()
