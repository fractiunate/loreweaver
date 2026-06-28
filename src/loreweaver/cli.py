from __future__ import annotations

import argparse
import asyncio

from loreweaver.init import init_project
from loreweaver.query.search import QueryFilters, query
from loreweaver.update import update_index


def main() -> None:
    parser = argparse.ArgumentParser(prog="loreweaver")
    subcommands = parser.add_subparsers(dest="command", required=True)

    init_parser = subcommands.add_parser("init")
    init_parser.add_argument("--force", action="store_true")

    update_parser = subcommands.add_parser("update")
    update_parser.add_argument("--full-reprocess", action="store_true")
    update_parser.add_argument("--reset", action="store_true")
    update_parser.add_argument("--force", action="store_true")

    query_parser = subcommands.add_parser("query")
    query_parser.add_argument("query")
    query_parser.add_argument("--source")
    query_parser.add_argument("--heading")
    query_parser.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args()

    if args.command == "init":
        init_project(force=args.force)
        return

    if args.command == "update":
        update_index(
            full_reprocess=args.full_reprocess,
            reset=args.reset,
            force=args.force,
        )
        return

    if args.command == "query":

        filters = QueryFilters(
            source_path=args.source,
            heading=args.heading,
        )
        asyncio.run(query(args.query, filters=filters, top_k=args.top_k))
        return

    parser.error(f"Unknown command: {args.command}")
