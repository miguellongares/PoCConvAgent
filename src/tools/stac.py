import calendar
import os
import random
from pathlib import Path

import chainlit as cl
import httpx
import matplotlib
import numpy as np
import rasterio
from agents import function_tool

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from config import settings

OUT = Path(os.environ.get("MAP_DIR", "/app/data/maps"))


@function_tool
async def search_environmental_datasets(query: str = "", bbox: str | None = None) -> list[dict]:
    """Search the MOOD STAC catalogue of environmental datasets (English keywords).

    query: single words separated by commas, any word may match, e.g. "tick,mosquito".
    Several words without commas must ALL match, so avoid them. Empty query lists every dataset.
    Returns dataset descriptions, not data values. bbox: optional "west,south,east,north".
    """
    params = {"limit": 100}
    if query.strip():
        params["q"] = query.strip()
    if bbox:
        params["bbox"] = bbox
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.get(f"{settings.stac_base_url}/collections", params=params)
        r.raise_for_status()
    return [{"id": d["id"], "title": d["title"], "description": d["description"][:200],
             "time_range": d["extent"]["temporal"]["interval"][0],
             "license": d.get("license"),
             "source": next((l["href"] for l in d["links"] if l["rel"] == "via"), None)}
            for d in r.json()["collections"]]


def _interval(date: str) -> str:
    """'2019', '2019-07' or '2019-07-15' -> STAC datetime interval."""
    y, m, d = (date.split("-") + [None, None])[:3]
    if m is None:
        return f"{y}-01-01T00:00:00Z/{y}-12-31T23:59:59Z"
    last = calendar.monthrange(int(y), int(m))[1] if d is None else int(d)
    first = "01" if d is None else d
    return f"{y}-{m}-{first}T00:00:00Z/{y}-{m}-{last:02d}T23:59:59Z"


def _render(collection_id: str, date: str | None, asset: str | None) -> dict:
    """Pick one item of the collection, read its GeoTIFF (downsampled) and save a PNG."""
    base = settings.stac_base_url
    params = {"limit": 100}
    if date:
        params["datetime"] = _interval(date)
    items = httpx.get(f"{base}/collections/{collection_id}/items", params=params, timeout=60).json()["features"]
    if not items:
        return {"error": f"No item for date {date}. Try another date or omit it."}
    item = random.choice(items)
    names = list(item["assets"])
    name = asset if asset in item["assets"] else names[0]
    a = item["assets"][name]
    band = a["bands"][0]
    with rasterio.open(a["href"]) as src:
        step = max(1, src.width // 1000)
        arr = src.read(1, out_shape=(src.height // step, src.width // step)).astype(float)
    arr[arr == band.get("nodata", 0)] = np.nan
    arr = arr * band.get("raster:scale", 1) + band.get("raster:offset", 0)
    unit = band.get("unit") or ""
    if unit == "K":
        arr, unit = arr - 273.15, "°C"
    title = httpx.get(f"{base}/collections/{collection_id}", timeout=60).json()["title"]
    label = f"{title}, {a.get('title', name)}, {item['properties'].get('title', '')}"
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(arr, cmap="viridis")
    plt.colorbar(im, label=unit)
    ax.set_title(label, fontsize=9)
    ax.axis("off")
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{item['id']}-{name}.png"
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return {"path": str(path), "dataset": title, "item": item["properties"].get("title"),
            "asset": name, "other_assets": names, "unit": unit,
            "min": float(np.nanmin(arr)), "max": float(np.nanmax(arr)), "mean": float(np.nanmean(arr)),
            "source": next((l["href"] for l in item["links"] if l["rel"] == "via"), None)}


@function_tool
async def plot_dataset_map(collection_id: str, date: str | None = None, asset: str | None = None) -> dict:
    """Draw a map of one MOOD dataset and show it in the chat.

    collection_id: id from search_environmental_datasets. date: "YYYY", "YYYY-MM" or "YYYY-MM-DD";
    omit it for a random item. asset: layer name (see other_assets in the result); default is the first.
    Returns min/max/mean of the plotted values with unit, dataset and date.
    """
    result = await cl.make_async(_render)(collection_id, date, asset)
    if "path" in result:
        await cl.Message(content="", elements=[cl.Image(path=result.pop("path"), name="map", display="inline")]).send()
    return result
