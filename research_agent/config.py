from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    rss_urls: list[str]
    output_dir: Path
    top_n: int
    openai_api_key: str | None
    openai_model: str


def load_settings() -> Settings:
    rss_urls = [
        "https://openai.com/blog/rss.xml",
        "https://www.anthropic.com/news/rss",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://venturebeat.com/ai/feed/",
        "https://huggingface.co/blog/feed.xml",
    ]

    api_key = os.environ.get("OPENAI_API_KEY", "").strip() or None

    return Settings(
        rss_urls=rss_urls,
        output_dir=Path("data"),
        top_n=10,
        openai_api_key=api_key,
        openai_model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
    )
