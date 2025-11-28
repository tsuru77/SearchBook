"""
Utility script to ingest a corpus of books into Elasticsearch.

Usage:
    python load_books.py --corpus-path ../datasets/sample_books --index searchbook
"""

from __future__ import annotations

import argparse
import json
import pathlib

from elasticsearch import Elasticsearch, helpers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest books into Elasticsearch")
    parser.add_argument("--corpus-path", type=pathlib.Path, required=True, help="Directory containing .txt files")
    parser.add_argument("--index", type=str, default="searchbook")
    parser.add_argument("--host", type=str, default="http://localhost:9200")
    parser.add_argument("--username", type=str, default="elastic")
    parser.add_argument("--password", type=str, default="changeme")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for smoke testing")
    return parser.parse_args()


def load_text(file_path: pathlib.Path) -> dict[str, str | int]:
    text = file_path.read_text(encoding="utf-8")
    return {
        "id": file_path.stem,
        "title": file_path.stem.replace("_", " ").title(),
        "author": "Unknown",
        "text": text,
        "word_count": len(text.split()),
    }


def main() -> None:
    args = parse_args()
    client = Elasticsearch(args.host, basic_auth=(args.username, args.password))

    docs = []
    for idx, path in enumerate(sorted(args.corpus_path.glob("*.txt"))):
        if args.limit is not None and idx >= args.limit:
            break
        docs.append(load_text(path))

    actions = [
        {
            "_op_type": "index",
            "_index": args.index,
            "_id": doc["id"],
            "_source": doc,
        }
        for doc in docs
    ]

    if not actions:
        raise SystemExit("No documents found. Check --corpus-path.")

    helpers.bulk(client, actions)
    print(f"Ingested {len(actions)} documents into index '{args.index}'.")


if __name__ == "__main__":
    main()


