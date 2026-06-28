from __future__ import annotations

from pathlib import Path

DEFAULT_LORE_YAML = """\
files:
  exclude:
    - .env
    - .venv/**
    - __pycache__/**
    - cocoindex.db/**

  include:
    - pattern: .lore/objectives/**/*.md
      role: objective

    - pattern: .lore/MISSION.md
      role: mission

    - pattern: docs/adr/**/*.md
      role: adr

    - pattern: docs/**/*.md
      role: documentation

    - pattern: README.md
      role: documentation

    - pattern: src/**/*.py
      role: code

github:
  issues:
    - label: bug
      role: bug_report

    - label: feature
      role: feature_request

  pull_requests:
    - label: adr
      role: adr_proposal
"""


def ensure_dir(path: Path) -> None:
    if path.exists():
        print(f"Exists: {path}")
        return

    path.mkdir(parents=True)
    print(f"Created: {path}")


def write_file_if_missing(path: Path, content: str, *, force: bool = False) -> None:
    if path.exists() and not force:
        print(f"Exists: {path}; leaving unchanged.")
        return

    action = "Overwrote" if path.exists() else "Created"
    path.write_text(content, encoding="utf-8")
    print(f"{action}: {path}")


def init_project(project_root: Path | None = None, *, force: bool = False) -> None:
    root = project_root or Path.cwd()

    lore_dir = root / ".lore"
    objectives_dir = lore_dir / "objectives"
    config_path = lore_dir / "lore.yaml"

    ensure_dir(lore_dir)
    ensure_dir(objectives_dir)
    write_file_if_missing(config_path, DEFAULT_LORE_YAML, force=force)
