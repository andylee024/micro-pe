"""Raw snapshot persistence helpers."""

from __future__ import annotations

import json
from pathlib import Path


def persist_snapshot(root: Path, run_id: str, source: str, payload: dict[str, object]) -> str:
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / f"{source}.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return str(path)
