from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceArtifact:
    source_kind: str
    source_id: str
    source_path: str | None
    content: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Classification:
    content_role: str
    content_format: str


@dataclass(frozen=True)
class Document:
    artifact: SourceArtifact
    classification: Classification

    @property
    def text(self) -> str:
        return self.artifact.content


@dataclass(frozen=True)
class Chunk:
    source_id: str
    chunk_index: int
    content: str
    start_char: int
    end_char: int
    heading_path: str
    metadata: dict[str, str] = field(default_factory=dict)
