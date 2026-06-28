import asyncpg
import cocoindex as coco
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder

PG_DB = coco.ContextKey[asyncpg.Pool]("text_embedding_db")

EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder](
    "embedder",
    detect_change=True,
)