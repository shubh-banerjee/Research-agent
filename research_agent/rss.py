from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Iterable
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


USER_AGENT = "minimal-ai-research-agent/0.1"
KEYWORDS = {
    "ai",
    "agent",
    "agents",
    "llm",
    "model",
    "models",
    "openai",
    "anthropic",
    "google",
    "meta",
    "microsoft",
    "nvidia",
    "startup",
    "funding",
    "launch",
    "inference",
}


@dataclass
class NewsItem:
    title: str
    link: str
    published_at: str
    source: str
    summary: str
    score: float


def fetch_top_items(rss_urls: Iterable[str], limit: int) -> list[NewsItem]:
    items: list[NewsItem] = []
    for url in rss_urls:
        items.extend(_fetch_feed(url))

    deduped = _dedupe_items(items)
    ranked = sorted(deduped, key=lambda item: item.score, reverse=True)
    return ranked[:limit]


def _fetch_feed(url: str) -> list[NewsItem]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=20) as response:
        payload = response.read()

    root = ET.fromstring(payload)
    channel = root.find("channel")
    source = channel.findtext("title", default=url) if channel is not None else url

    entries = root.findall(".//item")
    if not entries:
        entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    return [_parse_entry(entry, source) for entry in entries if _has_title(entry)]


def _parse_entry(entry: ET.Element, source: str) -> NewsItem:
    title = _clean(entry.findtext("title") or entry.findtext("{http://www.w3.org/2005/Atom}title", ""))
    link = _extract_link(entry)
    summary = _clean(
        entry.findtext("description")
        or entry.findtext("{http://www.w3.org/2005/Atom}summary", "")
        or entry.findtext("{http://www.w3.org/2005/Atom}content", "")
    )
    published_raw = (
        entry.findtext("pubDate")
        or entry.findtext("{http://www.w3.org/2005/Atom}published")
        or entry.findtext("{http://www.w3.org/2005/Atom}updated")
        or ""
    )
    published_at = _to_iso_timestamp(published_raw)
    score = _score_item(title=title, summary=summary, published_at=published_at)
    return NewsItem(
        title=title,
        link=link,
        published_at=published_at,
        source=source,
        summary=summary,
        score=score,
    )


def _extract_link(entry: ET.Element) -> str:
    link = entry.findtext("link")
    if link:
        return link.strip()

    atom_link = entry.find("{http://www.w3.org/2005/Atom}link")
    if atom_link is not None:
        return (atom_link.attrib.get("href") or "").strip()

    return ""


def _to_iso_timestamp(value: str) -> str:
    if not value.strip():
        return datetime.now(timezone.utc).isoformat()

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def _score_item(title: str, summary: str, published_at: str) -> float:
    text = f"{title} {summary}".lower()
    keyword_hits = sum(1 for keyword in KEYWORDS if keyword in text)
    recency_bonus = _recency_bonus(published_at)
    return keyword_hits * 10 + recency_bonus


def _recency_bonus(published_at: str) -> float:
    published = datetime.fromisoformat(published_at)
    age_hours = max((datetime.now(timezone.utc) - published).total_seconds() / 3600, 0)
    return max(0.0, 100.0 - min(age_hours, 100.0))


def _dedupe_items(items: Iterable[NewsItem]) -> list[NewsItem]:
    seen: set[str] = set()
    unique_items: list[NewsItem] = []

    for item in items:
        key = item.link or item.title.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_items.append(item)

    return unique_items


def _has_title(entry: ET.Element) -> bool:
    return bool(entry.findtext("title") or entry.findtext("{http://www.w3.org/2005/Atom}title"))


def _clean(value: str) -> str:
    return " ".join((value or "").split())
