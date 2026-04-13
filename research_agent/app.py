from __future__ import annotations

from datetime import datetime, timezone

from research_agent.analyzer import analyze_news
from research_agent.config import load_settings
from research_agent.rss import fetch_top_items
from research_agent.storage import append_system_log, read_log_context, save_report


def run() -> None:
    settings = load_settings()
    generated_at = datetime.now(timezone.utc).isoformat()
    log_context = read_log_context(settings.output_dir.parent / "system_log.md")
    news_items = fetch_top_items(settings.rss_urls, settings.top_n)
    analysis = analyze_news(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        news_items=news_items,
        log_context=log_context,
    )

    payload = {
        "generated_at": generated_at,
        "news_items": [
            {
                "title": item.title,
                "link": item.link,
                "published_at": item.published_at,
                "source": item.source,
                "summary": item.summary,
                "score": item.score,
            }
            for item in news_items
        ],
        "analysis": analysis,
    }

    output_path = save_report(settings.output_dir, payload)
    append_system_log(
        log_path=settings.output_dir.parent / "system_log.md",
        timestamp=generated_at,
        analysis=analysis,
    )
    print(f"Saved report to {output_path.resolve()}")
