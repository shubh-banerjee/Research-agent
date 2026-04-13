from __future__ import annotations

import json

from openai import OpenAI

from research_agent.rss import NewsItem


SYSTEM_PROMPT = """Return JSON only:
{
  "top_10_summary": "concise synthesis of the top 10 items",
  "key_trends": [
    {"trend": "trend name", "detail": "1-2 sentence explanation"}
  ],
  "company_product_updates": [
    {"company_or_product": "name", "update": "what they are doing"}
  ],
  "startup_ideas": [
    {"name": "idea name", "description": "1-2 sentence description"}
  ]
}

Rules:
- Use only the news items provided.
- Keep it concise and under 800 tokens total.
- 3 to 5 key trends.
- 5 to 8 company/product updates.
- Exactly 5 startup ideas.
"""


def analyze_news(
    *,
    api_key: str,
    model: str,
    news_items: list[NewsItem],
    log_context: str,
) -> dict:
    client = OpenAI(api_key=api_key, max_retries=1)
    user_prompt = _build_user_prompt(news_items, log_context)

    response = client.responses.create(
        model=model,
        reasoning={"effort": "medium"},
        max_output_tokens=800,
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "ai_research_report",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "top_10_summary": {"type": "string"},
                        "key_trends": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 5,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "trend": {"type": "string"},
                                    "detail": {"type": "string"},
                                },
                                "required": ["trend", "detail"],
                            },
                        },
                        "company_product_updates": {
                            "type": "array",
                            "minItems": 5,
                            "maxItems": 8,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "company_or_product": {"type": "string"},
                                    "update": {"type": "string"},
                                },
                                "required": ["company_or_product", "update"],
                            },
                        },
                        "startup_ideas": {
                            "type": "array",
                            "minItems": 5,
                            "maxItems": 5,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                },
                                "required": ["name", "description"],
                            },
                        },
                    },
                    "required": [
                        "top_10_summary",
                        "key_trends",
                        "company_product_updates",
                        "startup_ideas",
                    ],
                },
            }
        },
    )

    return json.loads(response.output_text)


def _build_user_prompt(news_items: list[NewsItem], log_context: str) -> str:
    serialized_items = [
        {
            "rank": index,
            "title": item.title,
            "source": item.source,
            "published_at": item.published_at,
            "summary": item.summary,
        }
        for index, item in enumerate(news_items[:10], start=1)
    ]

    payload = {
        "recent_log_context": log_context,
        "top_10_news_items": serialized_items,
    }
    return json.dumps(payload, separators=(",", ":"))
