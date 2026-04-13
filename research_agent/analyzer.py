from __future__ import annotations

import json

from research_agent.rss import NewsItem


SYSTEM_PROMPT = """You are an AI market research analyst.
Return valid JSON only with this exact shape:
{
  "summary": "short paragraph",
  "product_company_insights": [
    {"company_or_product": "name", "insight": "insight"}
  ],
  "startup_ideas": [
    {"name": "idea name", "description": "1-2 sentence description"}
  ]
}

Rules:
- Base your answer only on the provided news items.
- Keep the summary concise.
- Provide 5 to 8 product/company insights.
- Provide exactly 5 startup ideas.
- Do not wrap the JSON in markdown fences.
"""


def analyze_news(
    *,
    api_key: str | None,
    model: str,
    news_items: list[NewsItem],
) -> dict:
    if not api_key:
        return _build_fallback_analysis(news_items)

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    user_prompt = _build_user_prompt(news_items)

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
        ],
    )

    return json.loads(response.output_text)


def _build_user_prompt(news_items: list[NewsItem]) -> str:
    serialized_items = []
    for index, item in enumerate(news_items, start=1):
        serialized_items.append(
            {
                "rank": index,
                "title": item.title,
                "source": item.source,
                "published_at": item.published_at,
                "link": item.link,
                "summary": item.summary,
            }
        )

    return "Analyze these AI news items:\n" + json.dumps(serialized_items, indent=2)


def _build_fallback_analysis(news_items: list[NewsItem]) -> dict:
    top_titles = [item.title for item in news_items[:3]]
    summary = "This run used the local fallback analyzer because no LLM API key was configured. "
    if top_titles:
        summary += "Top themes came from: " + "; ".join(top_titles) + "."
    else:
        summary += "No news items were available."

    insights = []
    for item in news_items[:6]:
        company_or_product = _guess_company_or_product(item.title, item.source)
        insights.append(
            {
                "company_or_product": company_or_product,
                "insight": f"{company_or_product} appears active in current AI news momentum, with attention driven by '{item.title}'.",
            }
        )

    startup_ideas = [
        {
            "name": "AI News Signal Dashboard",
            "description": "Track AI company launches, funding, and model releases across major feeds and surface momentum changes for operators and investors.",
        },
        {
            "name": "Model Launch Sales Copilot",
            "description": "Turn fresh AI product announcements into account-specific sales angles for B2B teams selling infrastructure or services.",
        },
        {
            "name": "Competitive Research Agent",
            "description": "Monitor competitor announcements, summarize strategy shifts, and generate weekly product implications for startup leadership teams.",
        },
        {
            "name": "AI Feature Trend Finder",
            "description": "Cluster news by use case and suggest which AI features product teams should prioritize based on market movement.",
        },
        {
            "name": "Enterprise AI Risk Briefing",
            "description": "Convert daily AI headlines into short compliance, vendor, and procurement briefs for enterprise decision-makers.",
        },
    ]

    return {
        "summary": summary,
        "product_company_insights": insights,
        "startup_ideas": startup_ideas,
    }


def _guess_company_or_product(title: str, source: str) -> str:
    words = [word.strip(",:") for word in title.split()]
    for word in words:
        if word[:1].isupper() and len(word) > 2:
            return word
    return source
