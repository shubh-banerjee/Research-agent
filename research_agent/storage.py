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
    write_report_index(output_dir)
    return output_path


def write_report_index(output_dir: Path) -> Path:
    reports = []
    for path in sorted(output_dir.glob("research_report_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        generated_at = payload.get("generated_at", "")
        date_part, year_part = _date_parts(generated_at)
        news_items = payload.get("news_items", [])
        title = news_items[0].get("title", "Research Report") if news_items else "Research Report"

        reports.append(
            {
                "file_name": path.name,
                "generated_at": generated_at,
                "generated_date": date_part,
                "generated_year": year_part,
                "title": title,
            }
        )

    reports.sort(key=lambda report: report.get("generated_at", ""), reverse=True)
    index_payload = {"reports": reports}
    index_path = output_dir / "index.json"
    index_path.write_text(json.dumps(index_payload, indent=2), encoding="utf-8")
    return index_path


def ensure_system_log(log_path: Path) -> None:
    if log_path.exists():
        return

    log_path.write_text("# System Log\n\n", encoding="utf-8")


def read_log_context(log_path: Path, max_chars: int = 3000) -> str:
    ensure_system_log(log_path)
    content = log_path.read_text(encoding="utf-8").strip()
    if len(content) <= max_chars:
        return content
    return content[-max_chars:]


def append_system_log(
    *,
    log_path: Path,
    timestamp: str,
    analysis: dict[str, Any],
) -> None:
    ensure_system_log(log_path)

    summary = analysis.get("top_10_summary", "").strip()
    key_trends = analysis.get("key_trends", [])
    company_updates = analysis.get("company_product_updates", [])

    lines = [
        f"## Run {timestamp}",
        "",
        f"- Timestamp: {timestamp}",
        f"- Summary: {summary}",
        "- Insights:",
    ]

    for trend in key_trends:
        lines.append(f"  - Trend: {trend.get('trend', '')} - {trend.get('detail', '')}")

    for update in company_updates:
        lines.append(
            f"  - Company/Product: {update.get('company_or_product', '')} - {update.get('update', '')}"
        )

    lines.append("")
    with log_path.open("a", encoding="utf-8") as file_handle:
        file_handle.write("\n".join(lines) + "\n")


def _date_parts(generated_at: str) -> tuple[str, str]:
    try:
        parsed = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    except ValueError:
        return "", ""
    return parsed.date().isoformat(), str(parsed.year)
