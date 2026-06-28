from dataclasses import dataclass
from datetime import datetime

from typing import Annotated, AsyncIterator
from cocoindex.resources.chunk import Chunk
from numpy.typing import NDArray

from loreweaver.index.context import EMBEDDER


@dataclass
class EmbeddedChunkRow:
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
    source_id: str
    source_path: str | None
    source_kind: str

    content_role: str
    content_format: str
    heading_path: str
    file_modified_at: datetime | None
    chunk_hash: str
    chunk_index: int
    chunk_start: int
    chunk_end: int
    text: str

    embedding: Annotated[NDArray, EMBEDDER]


# -----------------------------------------------------------------------------
# Chunk processing
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class IndexedChunk:
    index: int
    chunk: Chunk
