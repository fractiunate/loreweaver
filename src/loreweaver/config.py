import os
import pathlib
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass(frozen=True)
class FileRule:
    pattern: str
    role: str

@dataclass(frozen=True)
class FileConfig:
    include: list[FileRule]
    exclude: list[str]

@dataclass(frozen=True)
class LoreConfig:
    files: FileConfig


load_dotenv()

DATABASE_URL = os.getenv(
    "POSTGRES_URL",
    "postgres://cocoindex:cocoindex@localhost/cocoindex",
)

TABLE_NAME = "doc_embeddings"
PG_SCHEMA_NAME = "coco_examples"

MARKDOWN_DIR = pathlib.Path("./docs")

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5


def load_lore_config(path: pathlib.Path = pathlib.Path(".lore/lore.yaml")) -> LoreConfig:
    pass