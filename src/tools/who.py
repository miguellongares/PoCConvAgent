import time

import httpx
from agents import function_tool

BASE = "https://ghoapi.azureedge.net/api"
CACHE_SECONDS = 30
_cache: dict[str, tuple[float, list[dict]]] = {}


async def _fetch(path: str) -> list[dict]:
    """Download a whole GHO table and cache it.

    The server currently answers 502 to every $filter query, so we download
    unfiltered and filter in Python.
    """
    cached = _cache.get(path)
    if cached and time.time() - cached[0] < CACHE_SECONDS:
        return cached[1]
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.get(f"{BASE}/{path}")
        r.raise_for_status()
    rows = r.json()["value"]
    _cache[path] = (time.time(), rows)
    return rows


@function_tool
async def search_indicators(keyword: str) -> list[dict]:
    """Find WHO indicators whose name contains the keyword (English)."""
    kw = keyword.lower()
    return [{"code": i["IndicatorCode"], "name": i["IndicatorName"]}
            for i in await _fetch("Indicator") if kw in i["IndicatorName"].lower()][:20]


@function_tool
async def get_indicator_data(
    indicator_code: str,
    country_iso3: str | None = None,
    year: int | None = None,
) -> list[dict]:
    """Fetch values for one WHO indicator, optionally for one country (ISO3) and year."""
    rows = await _fetch(indicator_code)
    if country_iso3:
        rows = [v for v in rows if v.get("SpatialDim") == country_iso3.upper()]
    if year:
        rows = [v for v in rows if v.get("TimeDim") == year]
    rows = sorted(rows, key=lambda v: v.get("TimeDim") or 0, reverse=True)[:50]
    return [{"country": v.get("SpatialDim"), "year": v.get("TimeDim"),
             "sex": v.get("Dim1"), "value": v.get("NumericValue"),
             "display": v.get("Value")} for v in rows]
