# cocoindex-psql

Minimal CocoIndex + PostgreSQL/pgvector Markdown embedding demo.

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

Put Markdown files in `markdown_files/`.

## Index documents

```bash
uv run cocoindex update main.py
```

To rerun processing for all files, even if memoized inputs are unchanged:

```bash
uv run cocoindex update main --full-reprocess
```

For a clean CocoIndex DB reset/rebuild after schema changes:

```bash
uv run cocoindex update main --reset
```

To skip the confirmation prompt:

```bash
uv run cocoindex update main --reset --force
```

## Query

```bash
uv run python main.py "your search question"
```

## Stop Postgres

```bash
podman compose down
```
