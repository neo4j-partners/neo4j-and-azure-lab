#!/usr/bin/env python3
"""CLI entry point for SEC 10-K financial data loading and workshop solutions.

Usage from financial_data_load directory:

    Data loading commands:
        uv run python main.py test
        uv run python main.py load [--limit N] [--clear]
        uv run python main.py verify
        uv run python main.py clean
        uv run python main.py samples [--limit N]

    Workshop solution runner:
        uv run python main.py solutions          # Interactive menu
        uv run python main.py solutions 4        # Run solution 4 directly
        uv run python main.py solutions A        # Run all from option 4 onwards
"""

import argparse
import asyncio
import importlib
import sys
import time
from pathlib import Path

# Add solution_srcs to path so solution files can import their config module.
sys.path.insert(0, str(Path(__file__).parent / "solution_srcs"))

# Data directory -- relative to this script.
DATA_DIR = Path(__file__).parent / "financial-data"
PDF_DIR = DATA_DIR / "form10k-sample"
COMPANY_CSV = DATA_DIR / "Company_Filings.csv"
ASSET_MANAGER_CSV = DATA_DIR / "Asset_Manager_Holdings.csv"


def _fmt_elapsed(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"


# ============================================================================
# Data loading commands
# ============================================================================


def cmd_load(args):
    """Full data load: clear → metadata → pipeline → constraints → indexes → verify."""
    from src.config import connect
    from src.loader import (
        clear_database, create_company_nodes, create_asset_manager_relationships,
        load_company_metadata, load_asset_managers, verify,
    )
    from src.schema import (
        create_all_constraints, create_fulltext_indexes,
        create_embedding_indexes,
    )
    from src.pipeline import process_all_pdfs, run_entity_resolution, validate_enrichment

    start = time.monotonic()

    with connect() as driver:
        if args.clear:
            clear_database(driver)
            print()

        # Load metadata (no constraints yet -- pipeline needs to write freely)
        company_meta = {}
        if COMPANY_CSV.exists():
            company_meta = load_company_metadata(COMPANY_CSV)
            create_company_nodes(driver, company_meta)

        # Get PDFs
        pdf_files = sorted(PDF_DIR.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in: {PDF_DIR}")
            return

        if args.limit:
            pdf_files = pdf_files[:args.limit]

        # Run pipeline
        print(f"\nProcessing {len(pdf_files)} PDFs...")
        process_all_pdfs(driver, pdf_files, company_meta)

        # Fuzzy-merge near-duplicate entities (e.g. "Apple" vs "Apple Inc.")
        run_entity_resolution(driver)

        # Constraints are created AFTER the pipeline and entity resolution
        # because Neo4jWriter uses MERGE which can create temporary duplicates
        # that the fuzzy resolver then merges.
        print("\nCreating constraints...")
        create_all_constraints(driver)

        print("\nCreating indexes...")
        create_embedding_indexes(driver)
        create_fulltext_indexes(driver)

        # Asset managers
        if ASSET_MANAGER_CSV.exists():
            print()
            holdings = load_asset_managers(ASSET_MANAGER_CSV)
            create_asset_manager_relationships(driver, holdings)

        verify(driver)
        validate_enrichment(driver)

    elapsed = time.monotonic() - start
    print(f"\nDone in {_fmt_elapsed(elapsed)}.")


def cmd_verify(args):
    """Print node/relationship counts and run end-to-end search checks."""
    from src.config import connect
    from src.loader import verify
    from src.pipeline import validate_enrichment, verify_searches

    with connect() as driver:
        verify(driver)
        validate_enrichment(driver)
        verify_searches(driver)


def cmd_clean(args):
    """Clear all nodes and relationships from the database."""
    from src.config import connect
    from src.loader import clear_database

    with connect() as driver:
        clear_database(driver)
    print("\nDone.")


def cmd_test(args):
    """Test Neo4j and Azure AI connections."""
    import test_connection
    test_connection.main()


def cmd_samples(args):
    """Run sample queries showcasing the knowledge graph (read-only)."""
    from src.config import connect
    from src.samples import run_all_samples

    with connect() as driver:
        run_all_samples(driver, sample_size=args.limit or 10)


# ============================================================================
# Workshop solution runner
# ============================================================================

# Solution definitions: (module_name, title, is_async, entry_func)
# Module prefixes align with workshop labs:
#   01_xx = Lab 8 (Building a Knowledge Graph)
#   02_xx = Lab 10 (Advanced Retrievers)
#   03_xx = Lab 5 + Lab 9 (Foundry Agents + Advanced Agents)
#   04_xx = Lab 6 (Context Providers)
#   05_xx = Lab 11 (Hybrid Search)
#   06_xx = Lab 7 (Agent Memory)
SOLUTIONS = [
    ("solution_srcs.01_01_data_loading", "Data Loading Fundamentals", False, "main"),
    ("solution_srcs.01_02_embeddings", "Embeddings", True, "main"),
    ("solution_srcs.01_03_entity_extraction", "Entity Extraction", True, "main"),
    ("solution_srcs.01_04_full_dataset_queries", "Full Dataset Queries", False, "main"),
    ("solution_srcs.02_01_vector_retriever", "Vector Retriever", False, "main"),
    ("solution_srcs.02_02_vector_cypher_retriever", "Vector Cypher Retriever", False, "main"),
    ("solution_srcs.02_03_text2cypher_retriever", "Text2Cypher Retriever", False, "main"),
    ("solution_srcs.05_01_simple_agent", "Simple Agent", True, "run_agent"),
    ("solution_srcs.05_02_context_provider", "Context Provider Intro", True, "run_agent"),
    ("solution_srcs.03_02_vector_graph_agent", "Vector Graph Agent", True, "run_agent"),
    ("solution_srcs.03_03_text2cypher_agent", "Text2Cypher Agent", True, "run_agent"),
    ("solution_srcs.05_01_fulltext_search", "Fulltext Search", False, "main"),
    ("solution_srcs.05_02_hybrid_search", "Hybrid Search", False, "main"),
    ("solution_srcs.04_01_fulltext_context_provider", "Fulltext Context Provider", True, "run_agent"),
    ("solution_srcs.04_02_vector_context_provider", "Vector Context Provider", True, "run_agent"),
    ("solution_srcs.04_03_graph_enriched_provider", "Graph-Enriched Provider", True, "run_agent"),
    ("solution_srcs.06_01_memory_context_provider", "Memory Context Provider", True, "run_agent"),
    ("solution_srcs.06_02_memory_tools_agent", "Memory Tools Agent", True, "run_agent"),
]

AGENT_QUERIES = {
    "solution_srcs.05_01_simple_agent": "Summarise the schema of the graph database.",
    "solution_srcs.05_02_context_provider": "Hello, what is the square root of 9?",
    "solution_srcs.03_02_vector_graph_agent": "What risk factors are mentioned in Apple's financial documents?",
    "solution_srcs.03_03_text2cypher_agent": "What stock has Microsoft issued?",
    "solution_srcs.04_01_fulltext_context_provider": "What products does Microsoft offer?",
    "solution_srcs.04_02_vector_context_provider": "What are the main business activities of tech companies?",
    "solution_srcs.04_03_graph_enriched_provider": "What are Apple's main products and what risks does the company face?",
    "solution_srcs.06_01_memory_context_provider": "Hi! I'm interested in learning about Apple's products.",
    "solution_srcs.06_02_memory_tools_agent": "I prefer concise technical explanations over high-level overviews.",
}


def _print_solutions_menu():
    print("\n" + "=" * 50)
    print("Workshop Solutions")
    print("=" * 50)
    print("\nData Pipeline - WARNING! These will delete all data:")
    print("  1. Data Loading Fundamentals")
    print("  2. Embeddings")
    print("  3. Entity Extraction")
    print("\nExploration:")
    print("  4. Full Dataset Queries")
    print("\nRetrievers:")
    print("  5. Vector Retriever")
    print("  6. Vector Cypher Retriever")
    print("  7. Text2Cypher Retriever")
    print("\nFoundry Agents (Lab 5):")
    print("  8. Simple Agent")
    print("  9. Context Provider Intro")
    print("\nAdvanced Agents (Lab 9):")
    print(" 10. Vector Graph Agent")
    print(" 11. Text2Cypher Agent")
    print("\nSearch:")
    print(" 12. Fulltext Search")
    print(" 13. Hybrid Search")
    print("\nContext Providers (Lab 6):")
    print(" 14. Fulltext Context Provider")
    print(" 15. Vector Context Provider")
    print(" 16. Graph-Enriched Provider")
    print("\nAgent Memory (Lab 7):")
    print(" 17. Memory Context Provider")
    print(" 18. Memory Tools Agent")
    print("\n  A. Run all (from option 4 onwards)")
    print("  0. Exit")
    print("=" * 50)


def _run_solution(choice: int) -> bool:
    """Run the selected solution. Returns False to exit."""
    if choice == 0:
        return False
    if choice < 1 or choice > len(SOLUTIONS):
        print("Invalid choice.")
        return True

    module_name, title, is_async, entry_func = SOLUTIONS[choice - 1]
    print(f"\n>>> Running: {title}")
    print("-" * 50)

    try:
        module = importlib.import_module(module_name)
        func = getattr(module, entry_func)
        if is_async:
            if entry_func == "run_agent":
                query = AGENT_QUERIES.get(module_name, "Hello")
                asyncio.run(func(query))
            else:
                asyncio.run(func())
        else:
            func()
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        raise
    except Exception as e:
        print(f"Error: {e}")

    print("-" * 50)
    return True


def cmd_solutions(args):
    """Launch workshop solution runner."""
    if args.choice:
        choice = args.choice
        if choice.upper() == "A":
            try:
                for i in range(4, len(SOLUTIONS) + 1):
                    _run_solution(i)
                print("\n>>> All solutions completed!")
            except KeyboardInterrupt:
                print("\n\nExiting.")
                sys.exit(0)
            return
        try:
            _run_solution(int(choice))
        except ValueError:
            print(f"Invalid: {choice}. Use 1-17 or A.")
        return

    # Interactive menu
    while True:
        _print_solutions_menu()
        try:
            choice = input("\nSelect solution (0-18, A):").strip()
            if not choice:
                continue
            if choice.upper() == "A":
                try:
                    for i in range(4, len(SOLUTIONS) + 1):
                        _run_solution(i)
                except KeyboardInterrupt:
                    print("\n\nExiting.")
                    sys.exit(0)
                continue
            choice_int = int(choice)
        except ValueError:
            print("Please enter a number or 'A'.")
            continue
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        try:
            if not _run_solution(choice_int):
                print("Goodbye!")
                break
        except KeyboardInterrupt:
            print("\n\nExiting.")
            break


# ============================================================================
# CLI entry point
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="SEC 10-K financial data loader and workshop runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # load
    p_load = subparsers.add_parser(
        "load", help="Full data load: metadata + PDFs + indexes")
    p_load.add_argument(
        "--limit", type=int, help="Limit number of PDFs to process")
    p_load.add_argument(
        "--clear", action="store_true", help="Clear database first")
    p_load.set_defaults(func=cmd_load)

    # verify
    p_verify = subparsers.add_parser(
        "verify", help="Print node and relationship counts (read-only)")
    p_verify.set_defaults(func=cmd_verify)

    # clean
    p_clean = subparsers.add_parser(
        "clean", help="Clear all data from database")
    p_clean.set_defaults(func=cmd_clean)

    # samples
    p_samples = subparsers.add_parser(
        "samples", help="Run sample queries showcasing the graph (read-only)")
    p_samples.add_argument(
        "--limit", type=int, default=10, help="Rows per section (default: 10)")
    p_samples.set_defaults(func=cmd_samples)

    # test
    p_test = subparsers.add_parser(
        "test", help="Test Neo4j and Azure AI connections")
    p_test.set_defaults(func=cmd_test)

    # solutions
    p_solutions = subparsers.add_parser(
        "solutions", help="Workshop solution runner")
    p_solutions.add_argument(
        "choice", nargs="?", help="Solution number (1-18) or A for all")
    p_solutions.set_defaults(func=cmd_solutions)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
