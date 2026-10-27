import httpx
from agents import function_tool

from config import settings


@function_tool
async def search_health_news(
    query: str,
    country_iso2: str | None = None,
    published_after: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Search PADI-web news about disease outbreaks and health events (English keywords).

    country_iso2: e.g. "DE". published_after: date "YYYY-MM-DD".
    """
    params = {"text": query, "per_page": min(limit, 20), "include": "classification",
              "ordering": "-published_at"}
    if country_iso2:
        params["country"] = country_iso2.upper()
    if published_after:
        params["published_after"] = published_after
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.get(f"{settings.padi_base_url}/articles/", params=params,
                        headers={"Authorization": f"Token {settings.padi_token}"})
        r.raise_for_status()
    return [{"id": a["id"], "title": a["title"], "url": a["url"], "country": a["country"],
             "published_at": a["published_at"],
             "labels": [l["name"] for l in a["classification"]["machine"]]}
            for a in r.json()["results"]]
