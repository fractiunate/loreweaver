from __future__ import annotations

from collections.abc import Iterable

# from loreweaver.core.interfaces import Classifier, Indexer, SourceAdapter, Transformer --> Not needed Python Protocols use structural typing
from loreweaver.core.models import Chunk, Classification, Document, SourceArtifact
from loreweaver.core.pipeline import IndexingPipeline


class FakeSource:
    """Adapter example: produces SourceArtifact objects."""

    def collect(self) -> Iterable[SourceArtifact]:
        yield SourceArtifact(
            source_kind="local_file",
            source_id="README.md",
            source_path="README.md",
            content="# Loreweaver\n\nLoreweaver builds project knowledge.",
            metadata={"example": "true"},
        )


class FakeClassifier:
    """Classifier example: assigns role and format."""

    def classify(self, artifact: SourceArtifact) -> Classification:
        return Classification(
            content_role="documentation",
            content_format="markdown",
        )


class FakeTransformer:
    """Transformer example: turns a document into chunks."""

    def transform(self, document: Document) -> Iterable[Chunk]:
        yield Chunk(
            source_id="README.md",
            chunk_index=0,
            content="...",
            start_char=0,
            end_char=42,
            heading_path="Loreweaver",
            metadata={
                "chunk_index": "0",
                "heading_path": "Loreweaver",
                "content_role": document.classification.content_role,
                "content_format": document.classification.content_format,
            },
        )


class PrintingIndexer:
    """Indexer example: stores nothing, only prints chunks."""

    def index_chunks(self, chunks: Iterable[Chunk]) -> None:
        for chunk in chunks:
            print("Indexed chunk")
            print(f"  source: {chunk.source_id}")
            print(f"  span: {chunk.start_char}..{chunk.end_char}")
            print(f"  content: {chunk.content!r}")
            print(f"  metadata: {chunk.metadata}")


def main() -> None:
    pipeline = IndexingPipeline(
        source=FakeSource(),
        classifier=FakeClassifier(),
        transformer=FakeTransformer(),
        indexer=PrintingIndexer(),
    )

    pipeline.run()


if __name__ == "__main__":
    main()