"""
Text Embedding / Markdown Knowledge Index with CocoIndex.

Index your Markdown files:

    cocoindex update src/loreweaver/main.py

Live mode, watching for Markdown file changes:

    cocoindex update -L src/loreweaver/main.py

Query the semantic index:

    python src/loreweaver/main.py "how do refresh tokens work?"

Expected folder structure:

    .
    ├── src/loreweaver/main.py
    └── docs/
        ├── notes.md
        └── architecture.md

Environment:

    export POSTGRES_URL="postgres://cocoindex:cocoindex@localhost/cocoindex"
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
import hashlib
import re

import argparse

from datetime import datetime, timezone

from dataclasses import dataclass
from typing import Annotated, AsyncIterator

import asyncpg
from dotenv import load_dotenv
from numpy.typing import NDArray
from pgvector.asyncpg import register_vector

import cocoindex as coco
from cocoindex.connectors import localfs, postgres
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder
from cocoindex.ops.text import RecursiveSplitter
from cocoindex.resources.chunk import Chunk
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.resources.id import IdGenerator

load_dotenv()


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DATABASE_URL = os.getenv(
    "POSTGRES_URL",
    "postgres://cocoindex:cocoindex@localhost/cocoindex",
)

TABLE_NAME = "doc_embeddings"
PG_SCHEMA_NAME = "coco_examples"

MARKDOWN_DIR = pathlib.Path("./docs")

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5


# -----------------------------------------------------------------------------
# CocoIndex shared context
# -----------------------------------------------------------------------------

PG_DB = coco.ContextKey[asyncpg.Pool]("text_embedding_db")

EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder](
    "embedder",
    detect_change=True,
)

_splitter = RecursiveSplitter()


@coco.lifespan
async def coco_lifespan(
    builder: coco.EnvironmentBuilder,
) -> AsyncIterator[None]:
    """
    Create shared resources once for the CocoIndex app.

    PG_DB:
        Async Postgres connection pool.

    EMBEDDER:
        SentenceTransformer model used to embed each Markdown chunk.
        detect_change=True tells CocoIndex that changing the model should
        invalidate/recompute dependent embeddings.
    """
    async with asyncpg.create_pool(DATABASE_URL) as pool:
        builder.provide(PG_DB, pool)
        builder.provide(EMBEDDER, SentenceTransformerEmbedder(EMBED_MODEL))
        yield


# -----------------------------------------------------------------------------
# Target table row
# -----------------------------------------------------------------------------


@dataclass
class DocEmbedding:
    """
    One row in Postgres.

    Each Markdown chunk becomes one row.

    id:
        Stable chunk id.

    filename:
        Source Markdown file path.

    chunk_start / chunk_end:
        Character offsets inside the source Markdown file.

    text:
        The raw Markdown chunk.

    embedding:
        Vector generated from the chunk text.
    """

    id: int

    source_path: str
    heading_path: str
    file_modified_at: datetime
    chunk_hash: str

    chunk_index: int
    chunk_start: int
    chunk_end: int
    text: str
    embedding: Annotated[NDArray, EMBEDDER]


# Heading Helper
def heading_path_at(text: str, start_offset: int, end_offset: int) -> str:
    stack: list[str] = []
    heading_regex = r"^(#{1,6})\s+(.+?)\s*$"

    for line in text[:start_offset].splitlines():
        match = re.match(heading_regex, line)
        if not match:
            continue

        level = len(match.group(1))
        title = match.group(2).strip().strip("#").strip()

        stack = stack[: level - 1]
        stack.append(title)

    if not stack:
        for line in text[start_offset:end_offset].splitlines():
            match = re.match(heading_regex, line)
            if not match:
                continue

            stack.append(match.group(2).strip())
            break

    return " > ".join(stack)


# -----------------------------------------------------------------------------
# Chunk processing
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class IndexedChunk:
    index: int
    chunk: Chunk


@coco.fn
async def process_chunk(
    indexed: IndexedChunk,
    source_path: str,
    file_modified_at: datetime,
    full_text: str,
    id_gen: IdGenerator,
    table: postgres.TableTarget[DocEmbedding],
) -> None:
    """
    Turn one Markdown chunk into one target table row.
    """

    chunk = indexed.chunk

    hash_input = (
        f"{source_path}\n"
        f"{indexed.index}\n"
        f"{chunk.start.char_offset}\n"
        f"{chunk.end.char_offset}\n"
        f"{chunk.text}"
    ).encode("utf-8")

    chunk_hash = hashlib.sha256(hash_input).hexdigest()

    heading_path = heading_path_at(
        full_text, chunk.start.char_offset, chunk.end.char_offset
    )

    table.declare_row(
        row=DocEmbedding(
            id=await id_gen.next_id(f"{source_path}:{indexed.index}:{chunk_hash}"),
            source_path=source_path,
            heading_path=heading_path,
            file_modified_at=file_modified_at,
            chunk_hash=chunk_hash,
            chunk_index=indexed.index,
            chunk_start=chunk.start.char_offset,
            chunk_end=chunk.end.char_offset,
            text=chunk.text,
            embedding=await coco.use_context(EMBEDDER).embed(chunk.text),
        ),
    )


@coco.fn(memo=True)
async def process_file(
    file: FileLike,
    table: postgres.TableTarget[DocEmbedding],
) -> None:
    """
    Read one Markdown file, split it into overlapping chunks, then process
    each chunk.

    memo=True is important: unchanged files can be skipped on later runs.
    """
    text = await file.read_text()

    chunks = _splitter.split(
        text,
        chunk_size=2000,
        chunk_overlap=500,
        language="markdown",
    )

    indexed_chunks = [
        IndexedChunk(index=i, chunk=chunk) for i, chunk in enumerate(chunks)
    ]

    source_path = file.file_path.path.as_posix()

    file_modified_at = datetime.fromtimestamp(
        file.file_path.resolve().stat().st_mtime, tz=timezone.utc
    )

    id_gen = IdGenerator()

    await coco.map(
        process_chunk,
        indexed_chunks,
        source_path,
        file_modified_at,
        text,
        id_gen,
        table,
    )


# -----------------------------------------------------------------------------
# Main CocoIndex app
# -----------------------------------------------------------------------------


@coco.fn
async def app_main(sourcedir: pathlib.Path) -> None:
    """
    Wire the source Markdown directory to the Postgres target table.
    """
    target_table = await postgres.mount_table_target(
        PG_DB,
        table_name=TABLE_NAME,
        table_schema=await postgres.TableSchema.from_class(
            DocEmbedding,
            primary_key=["id"],
        ),
        pg_schema_name=PG_SCHEMA_NAME,
    )

    # Ask CocoIndex/Postgres target to manage a vector index on this column.
    target_table.declare_vector_index(column="embedding")

    files = localfs.walk_dir(
        sourcedir,
        recursive=True,
        path_matcher=PatternFilePathMatcher(
            included_patterns=["**/*.md"],
        ),
        live=True,
    )

    await coco.mount_each(
        process_file,
        files.items(),
        target_table,
    )


app = coco.App(
    coco.AppConfig(name="TextEmbeddingV1"),
    app_main,
    sourcedir=MARKDOWN_DIR,
)


# -----------------------------------------------------------------------------
# Query demo
# -----------------------------------------------------------------------------

@dataclass
class QueryFilters:
    source_path: str | None = None
    heading: str | None = None


async def query_once(
    pool: asyncpg.Pool,
    embedder: SentenceTransformerEmbedder,
    query_text: str,
    filters: QueryFilters | None = None,
    *,
    top_k: int = TOP_K,
) -> None:
    """
    Embed the user's query and search nearest Markdown chunks in pgvector.

    pgvector's <=> operator is cosine distance.
    Lower distance means more similar.
    """
    query_vec = await embedder.embed(query_text)

    async with pool.acquire() as conn:
        conditions = []
        params = [query_vec]
        
        if filters and filters.source_path:
            params.append(f"%{filters.source_path}%")
            conditions.append(f"source_path ILIKE ${len(params)}")

        if filters and filters.heading:
            params.append(f"%{filters.heading}%")
            conditions.append(f"heading_path ILIKE ${len(params)}")

        where_clause = ""
        # Values are safely passed separately from SQL text. That prevents quoting bugs and SQL injection.

        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        limit_param = len(params) + 1
        params.append(top_k)

        rows = await conn.fetch(
            f"""
            SELECT
                source_path,
               heading_path,
                file_modified_at,
                chunk_hash,
                chunk_index,
                chunk_start,
                chunk_end,
                text,
                embedding <=> $1 AS distance
            FROM "{PG_SCHEMA_NAME}"."{TABLE_NAME}"
            {where_clause}
            ORDER BY distance ASC
            LIMIT ${limit_param}
            """,
            *params,
        )

    for row in rows:
        distance = float(row["distance"])
        score = 1.0 - distance

        print(f"[score={score:.3f} distance={distance:.3f}] {row['source_path']}")
        print(f"heading: {row['heading_path']}")
        print(f"chars: {row['chunk_start']}..{row['chunk_end']}")
        print(row["text"])
        print("---")


async def query(
    initial_query: str | None = None,
    filters: QueryFilters | None = None
) -> None:
    """
    Query mode.

    This is separate from CocoIndex update mode. First run:

        cocoindex update main

    Then run:

        python main.py "your question"
    """
    embedder = SentenceTransformerEmbedder(EMBED_MODEL)

    async with asyncpg.create_pool(
        DATABASE_URL,
        init=register_vector,
    ) as pool:
        if initial_query is not None:
            await query_once(pool, embedder, initial_query, filters)
            return

        while True:
            query_text = input("Enter search query, or Enter to quit: ").strip()
            if not query_text:
                break

            await query_once(pool, embedder, query_text, filters)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the Markdown semantic index.")

    parser.add_argument(
        "query",
        nargs="*",
        help="Search query text.",
    )

    parser.add_argument(
        "--source",
        help="Filter results to source paths containing this text.",
    )

    parser.add_argument(
        "--heading",
        help="Filter results to headings containing this text.",
    )

    args = parser.parse_args()

    filters = QueryFilters(
        source_path=args.source,
        heading=args.heading,
    )

    initial_query = " ".join(args.query) if args.query else None

    asyncio.run(query(initial_query, filters=filters))
