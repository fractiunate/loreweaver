# Objective: Project-local CLI

## Intent

Loreweaver provides a simple project-local command-line interface for manually initializing, updating, and querying project knowledge.

This is the best first runnable version because it is simple, easy to debug, and good for early development.

## Desired commands

In a project repo:

```bash
loreweaver init
loreweaver update
loreweaver query "Does this project use Postgres?"
```

With the current prototype setup:

```bash
uv run cocoindex update src/loreweaver/main.py
uv run python src/loreweaver/main.py "Does this project use Postgres?"
```

## Flow

```text
project files -> manual update -> local Postgres index -> query
```

## Uses

```text
.lore/lore.yaml
local files
Postgres/pgvector
manual updates
```

## Desired behavior

- `loreweaver init` creates the project-local `.lore/` structure and starter `.lore/lore.yaml` config.
- `loreweaver update` loads `.lore/lore.yaml` and indexes configured local files.
- `loreweaver query "..."` searches the current project knowledge index.
- Updates are manual and explicit in this phase.
- The implementation should keep the current CocoIndex + Postgres/pgvector flow working while moving toward the Loreweaver CLI shape.

## Pros

- Simple.
- Easy to debug.
- Good for early development.

## Cons

- Not live.
- User must remember to update.

## Principle

Keep this phase small and local before adding watch mode, daemon mode, GitHub integration, or agent integrations.
