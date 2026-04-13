from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def save_report(output_dir: Path, payload: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = output_dir / f"research_report_{timestamp}.json"
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path
