from __future__ import annotations

import hashlib

import pathlib


from datetime import datetime, timezone

import asyncpg

from typing import AsyncIterator

from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder


import cocoindex as coco
from cocoindex.connectors import localfs, postgres
from cocoindex.ops.text import RecursiveSplitter
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.resources.id import IdGenerator

from loreweaver.index.context import EMBEDDER, PG_DB
from loreweaver.index.schema import ChunkEmbedding, IndexedChunk
from loreweaver.transforms.markdown import heading_path_at


from loreweaver.config import (
    DATABASE_URL,
    MARKDOWN_DIR,
    PG_SCHEMA_NAME,
    TABLE_NAME,
    EMBED_MODEL,
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


@coco.fn
async def process_chunk(
    indexed: IndexedChunk,
    source_path: str,
    file_modified_at: datetime,
    full_text: str,
    id_gen: IdGenerator,
    table: postgres.TableTarget[ChunkEmbedding],
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
        row=ChunkEmbedding(
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
    table: postgres.TableTarget[ChunkEmbedding],
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
            ChunkEmbedding,
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
