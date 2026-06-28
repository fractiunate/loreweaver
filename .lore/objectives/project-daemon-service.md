# Objective: Project Daemon / Service

## Intent

Loreweaver runs continuously as a background process for a project.

## Desired commands

```bash
loreweaver daemon start
loreweaver daemon status
loreweaver daemon stop
```

## Flow

```text
daemon watches project -> keeps DB current -> CLI/UI queries daemon
```

## Desired behavior

- Watch configured local files and directories.
- Debounce file changes.
- Re-index changed sources.
- Keep chunks, claims, embeddings, and consistency results fresh.
- Expose status and query capabilities to local tools.

## Example uses

- Keep local project memory up to date while coding.
- Let a CLI query the current index without rebuilding it.
- Let an editor or agent ask the daemon for relevant project context.
