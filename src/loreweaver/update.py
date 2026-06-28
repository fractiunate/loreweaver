from __future__ import annotations

import subprocess
import sys


COCOINDEX_APP = "src/loreweaver/main.py"


def update_index(
    *,
    full_reprocess: bool = False,
    reset: bool = False,
    force: bool = False,
) -> None:
    command = ["cocoindex", "update", COCOINDEX_APP]

    if full_reprocess:
        command.append("--full-reprocess")

    if reset:
        command.append("--reset")

    if force:
        command.append("--force")

    result = subprocess.run(command, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
