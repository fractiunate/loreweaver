from dataclasses import dataclass
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder
from pgvector.asyncpg import register_vector
import asyncpg

from loreweaver.config import (
    DATABASE_URL,
    EMBED_MODEL,
    PG_SCHEMA_NAME,
    TABLE_NAME,
    TOP_K,
)


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
    filters: QueryFilters | None = None,
    *,
    top_k: int = TOP_K,
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
            await query_once(pool, embedder, initial_query, filters, top_k=top_k)
            return

        while True:
            query_text = input("Enter search query, or Enter to quit: ").strip()
            if not query_text:
                break

            await query_once(pool, embedder, query_text, filters, top_k=top_k)
