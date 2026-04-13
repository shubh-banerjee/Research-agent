from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from research_agent.rss import NewsItem


SYSTEM_PROMPT = """Return JSON only:
{
  "overall_summary": "concise synthesis of the top 10 items",
  "key_trends": [
    {"trend": "trend name", "detail": "1-2 sentence explanation"}
  ],
  "company_product_moves": [
    {"company_or_product": "name", "move": "what they are doing"}
  ],
  "startup_ideas": [
    {"name": "idea name", "description": "1-2 sentence description"}
  ]
}

Rules:
- Use only the news items provided.
- Keep it concise and under 800 tokens total.
- 3 to 5 key trends.
- 5 to 8 company/product moves.
- Exactly 5 startup ideas.
"""


def analyze_news(
    *,
    api_key: str,
    model: str,
    news_items: list[NewsItem],
) -> dict:
    try:
        return _call_openrouter(api_key=api_key, model=model, news_items=news_items)
    except Exception as error:
        print(f"[WARN] OpenRouter analysis failed: {error}")
        print("[WARN] Using fallback analysis.")
        return _fallback_analysis(news_items)


def _call_openrouter(*, api_key: str, model: str, news_items: list[NewsItem]) -> dict:
    user_prompt = _build_user_prompt(news_items)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 800,
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = json.dumps(payload).encode("utf-8")
    request = Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(request, timeout=35) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"OpenRouter HTTP {error.code}: {error_body}") from error
    except URLError as error:
        raise RuntimeError(f"OpenRouter network error: {error}") from error

    data = json.loads(raw)
    content = _extract_content(data)
    parsed = _parse_response_json(content)
    _validate_shape(parsed)
    return parsed


def _extract_content(data: dict) -> str:
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception as error:
        raise RuntimeError(f"Unexpected response shape: {data}") from error

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_chunks = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                text_chunks.append(item["text"])
        return "\n".join(text_chunks)

    raise RuntimeError(f"Unsupported message content type: {type(content)}")


def _parse_response_json(content: str) -> dict:
    text = content.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    if text.startswith("```"):
        text = text.replace("```json", "```")
        parts = [part.strip() for part in text.split("```") if part.strip()]
        for part in parts:
            if part.startswith("{") and part.endswith("}"):
                return json.loads(part)

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])

    raise RuntimeError("Model response did not contain valid JSON.")


def _validate_shape(result: dict) -> None:
    required = {"overall_summary", "key_trends", "company_product_moves", "startup_ideas"}
    missing = required - set(result.keys())
    if missing:
        raise RuntimeError(f"Missing required keys in model response: {sorted(missing)}")


def _fallback_analysis(news_items: list[NewsItem]) -> dict:
    top_items = news_items[:10]
    top_titles = [item.title for item in top_items[:3]]
    summary = "Fallback mode: OpenRouter was unavailable. " + " | ".join(top_titles) if top_titles else "Fallback mode: no items available."

    key_trends = []
    for item in top_items[:3]:
        key_trends.append(
            {
                "trend": item.title[:80],
                "detail": item.summary[:180] or "High activity in this topic.",
            }
        )

    company_product_moves = []
    for item in top_items[:6]:
        company_product_moves.append(
            {
                "company_or_product": _guess_name(item.title),
                "move": item.title,
            }
        )

    startup_ideas = [
        {"name": "AI News Copilot", "description": "Summarize daily AI updates for teams and founders."},
        {"name": "Competitive Watchtower", "description": "Track competitor AI announcements and strategy shifts."},
        {"name": "Model Launch Radar", "description": "Alert teams to new model launches and ecosystem impact."},
        {"name": "AI Product Teardown", "description": "Convert AI news into actionable product briefs."},
        {"name": "Trend-to-Idea Engine", "description": "Map AI trends to startup ideas with weekly reports."},
    ]

    return {
        "overall_summary": summary,
        "key_trends": key_trends,
        "company_product_moves": company_product_moves,
        "startup_ideas": startup_ideas,
    }


def _guess_name(title: str) -> str:
    for word in title.split():
        cleaned = word.strip(",:.()")
        if cleaned and cleaned[0].isupper():
            return cleaned
    return "AI Company"


def _build_user_prompt(news_items: list[NewsItem]) -> str:
    serialized_items = [
        {
            "rank": index,
            "title": item.title,
            "summary": item.summary,
        }
        for index, item in enumerate(news_items[:10], start=1)
    ]

    return json.dumps({"top_10_news_items": serialized_items}, separators=(",", ":"))
