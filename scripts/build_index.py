from __future__ import annotations

import argparse

from app.rag.indexer import RAGIndexer
from app.utils.logging import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and persist a RAG index.")
    parser.add_argument("--docs-dir", required=True, help="Path to source documents.")
    parser.add_argument("--persist-dir", required=True, help="Path to persist index.")
    args = parser.parse_args()

    setup_logging()
    indexer = RAGIndexer()
    indexer.persist_index(args.docs_dir, args.persist_dir)
    print(f"Index built successfully at: {args.persist_dir}")


if __name__ == "__main__":
    main()
