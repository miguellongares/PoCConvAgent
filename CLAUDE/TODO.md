# TODO

## Next
- [x] Fill `.env` with the real Bonsai 2 base URL, model name and API key
- [x] `docker compose up --build` and fix whatever breaks
- [x] Verify step 1: model answers in German and English
- [x] Verify step 2: "life expectancy in Germany in 2019" returns value + indicator code + country + year, matching the API
- [ ] Verify step 3 in the browser: follow-up ("and for France?") works
- [ ] Verify step 4: upload a PDF, ask about it, get passage with file and page
- [x] Check Bonsai 2 supports tool calling reliably (risk in guide section 7)
- [ ] `$filter` works again (2026-10-22, flaky?): go back to server-side filtering in `tools/who.py`, keep unfiltered download as fallback
- [ ] Test tool calling on harder cases (several tools per question, German questions)

- [ ] Test `search_health_news` in the container (rebuild, ask "recent Zika news in Mexico"); add `PADI_TOKEN` to your `.env` if missing
- [ ] Test `search_environmental_datasets` in the container (ask "which datasets exist on ticks?")
- [ ] Rebuild image and test `plot_dataset_map` in chat ("plot land surface temperature for July 2019")
- [ ] Map polish: coastlines/lon-lat axes, clip to bbox/country; EVI seasonal asset shows raw 0-3595 (no `raster:scale` in metadata, check units)
- [ ] Random item only samples the first 100 items of a collection; page through for a truly random date
- [ ] Rotate the PADI token (it was pasted in chat)

## Later
- [ ] Step 5: vision (`tools/vision.py`, `describe_image`). Check if Bonsai 2 accepts images, else use a separate vision model
- [ ] Step 6: eval set, 20-30 DE/EN questions in `eval/questions.jsonl` plus a runner script
- [ ] MOOD STAC: read GeoTIFF values at a point/country (map tool already reads rasters), only if needed
- [x] Small time-limited cache for WHO calls
- [ ] Self-hosted tracing (e.g. Langfuse) if debugging needs it
- [ ] Check German questions translate keywords for `search_indicators`
