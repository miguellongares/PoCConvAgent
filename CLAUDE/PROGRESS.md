# Progress

Status per build step from `Documentation/WHO_AGENT_PROTOTYPE.md` section 6.
"Written" = code exists. "Verified" = run and the step's "done when" met.

| Step | Written | Verified |
|---|---|---|
| 1. Model connection (`llm_factory.py`) | yes | partly: plain chat DE/EN and tool calling work (direct API test) |
| 2. WHO tool (`tools/who.py`) | yes | yes: Germany 2019 = 81.0 with code, country, year (tested via agent in container) |
| 3. Chat UI (Chainlit, in-memory session, streaming) | yes | partly: app starts, UI returns HTTP 200; follow-up not tested in browser |
| 4. Ingest + retrieval (Docling, bge-m3, Qdrant, reranker) | yes | no |
| Extra: PADI-web news tool (`tools/news.py`) | yes | partly: API query checked with curl (text, country, ordering); tool not run in container (Docker was off) |
| Extra: MOOD STAC catalogue tool (`tools/stac.py`) | yes | partly: `q` and `bbox` collection search checked with curl; tool not run in container |
| Extra: map tool (`plot_dataset_map` in `tools/stac.py`) | yes | partly: `_render` run locally and in container (MODIS LST 2019-07: -18.8 to 65.6 °C; seasonal EVI asset; unknown year returns error); not run in container or via chat |
| 5. Vision | no | no |
| 6. Evaluation | no | no |

## Log
- 2026-10-19: Project scaffolded: Dockerfile, docker-compose (Qdrant + agent), `.env.example`, source for steps 1-4, README. Nothing has been run yet.
- 2026-10-19: Moved CLAUDE.md, PROGRESS.md, TODO.md into the CLAUDE/ folder.
- 2026-10-19: Fixed agent container crash: torch and torchvision must both come from the CPU index (mismatch broke `transformers` imports). Fixed in Dockerfile.
- 2026-10-19: Fixed `.env` model name to `ternary-bonsai-27b` (typo gave 403). Bonsai API verified: plain chat and tool calling work.
- 2026-10-19: Answers now stream to Chainlit (`Runner.run_streamed`).
- 2026-10-19: WHO API returns 502 for every `$filter`. `tools/who.py` now downloads unfiltered tables, filters in Python, caches 1 hour. First call per indicator is slow (WHOSIS_000001 is about 8 MB).
- 2026-10-20: Added `src/test_who.py`: manual CLI test for the WHO tools (search, data, raw API call), no LLM needed. Run in container: search, data and default checks pass (Germany 2019 = 81.0). `raw "Indicator?$top=3"` still gives 502, so `$filter`/`$top` are still broken server-side (checked 2026-10-20).
- 2026-10-22: `$filter` works again: `WHOSIS_000001?$filter=SpatialDim eq 'DEU' and TimeDim eq 2020` returns 200 with Germany 2020 = 80.8 (both sexes). Earlier 502 was seen with `Indicator?$top=3`. `who.py` still downloads unfiltered tables.
- 2026-10-26: Added `search_health_news` (`tools/news.py`) for the PADI-web API (`PADI_TOKEN` in `.env`, auth header `Token`, newest first via `ordering=-published_at`, text search via `text=`). Wired into `agent.py`. Limits: 1000 requests/hour per token. Not yet run in the container.
- 2026-10-26: Added `search_environmental_datasets` (`tools/stac.py`) for the MOOD STAC API (https://stac.mood-platform.eu, no auth, 40 collections). Catalogue search only (`/collections?q=&bbox=`), no raster values. Wired into `agent.py`. Not yet run in the container.
- 2026-10-26: Fixed STAC tool after live agent log: multi-word `q` (e.g. "climate temperature") needs ALL words to match and returned []. Comma-separated words ("tick,mosquito") act as OR; empty query lists all 40 collections. Tool docstring and agent instructions updated.
- 2026-10-27: Added `plot_dataset_map(collection_id, date, asset)` to `tools/stac.py`. Picks an item (filtered by `datetime` interval, else random from first 100), reads the COG downsampled with rasterio, applies nodata/scale (K to °C), saves PNG to `data/maps/` and sends it to Chainlit as `cl.Image` from inside the tool. Added `rasterio`, `matplotlib` to requirements (image rebuild needed). Maps have no coastlines or lon/lat axes (raw EPSG:3857 grid).
- 2026-10-27: Container crashed on start (`ImportError: libexpat.so.1` from rasterio). Fixed: Dockerfile installs `libexpat1` via apt. Rebuilt; app starts on :8000 and `_render` works in the container (MODIS LST 2019-07 PNG written to /app/data/maps). Chat flow still untested.
