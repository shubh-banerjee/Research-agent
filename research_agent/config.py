from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from research_agent.secrets import OPENROUTER_API_KEY, OPENROUTER_MODEL


@dataclass(frozen=True)
class Settings:
    rss_urls: list[str]
    output_dir: Path
    top_n: int
    openrouter_api_key: str
    model: str


def load_settings() -> Settings:
    rss_urls = [
        "https://openai.com/blog/rss.xml",
        "https://www.anthropic.com/news/rss",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://venturebeat.com/ai/feed/",
        "https://huggingface.co/blog/feed.xml",
    ]

    api_key = OPENROUTER_API_KEY.strip()
    model = OPENROUTER_MODEL.strip()

    return Settings(
        rss_urls=rss_urls,
        output_dir=Path("data"),
        top_n=10,
        openrouter_api_key=api_key,
        model=model,
    )
