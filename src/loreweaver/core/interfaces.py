from __future__ import annotations
from typing import Iterable, Protocol

from loreweaver.core.models import (
    SourceArtifact,
    Classification,
    Document,
    Chunk,
)


class SourceAdapter(Protocol):
    def collect(self) -> Iterable[SourceArtifact]: ...


class Classifier(Protocol):
    def classify(self, artifact: SourceArtifact) -> Classification: ...

class Transformer(Protocol):
    def transform(self, document: Document) -> Iterable[Chunk]: ...


# Later you may want indexer to return stats:
#
# ```python
#   IndexResult(indexed_chunks=42)
# ```
# Because later you may have:
#
# ```python
#   index_sources
#   index_claims
# ````
class Indexer(Protocol):
    def index_chunks(self, chunks: Iterable[Chunk]) -> None: ...