# Local setup

Minimal Loreweaver + CocoIndex + PostgreSQL/pgvector setup.

## Setup

```bash
uv sync
podman compose up -d
```

Create or check `.env`:

```env
POSTGRES_URL=postgresql://cocoindex:cocoindex@localhost:15000/cocoindex
COCOINDEX_DB=./cocoindex.db
```

Project knowledge files currently live in `docs/`, `knowledge/`, and `.lore/`.

## Index documents

```bash
uv run cocoindex update src/loreweaver/main.py
```

To rerun processing for all files, even if memoized inputs are unchanged:

```bash
uv run cocoindex update src/loreweaver/main.py --full-reprocess
```

For a clean CocoIndex DB reset/rebuild after schema changes:

```bash
uv run cocoindex update src/loreweaver/main.py --reset
```

To skip the confirmation prompt:

```bash
uv run cocoindex update src/loreweaver/main.py --reset --force
```

## Query

```bash
uv run python src/loreweaver/main.py "your search question"
```

## Stop Postgres

```bash
podman compose down
```
