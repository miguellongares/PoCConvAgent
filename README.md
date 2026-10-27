# WHO conversational agent (prototype)

See `Documentation/WHO_AGENT_PROTOTYPE.md` for the design.

1. Edit `.env` (Bonsai 2 base URL, model name, API key).
2. `docker compose up --build`
3. Open http://localhost:8000. Attach PDFs/images to a message to ingest them, then ask about them.

The first ingest/search downloads bge-m3 and the reranker (a few GB, cached in a volume).
Bulk ingest: `docker compose exec agent python -m tools.ingest /app/data/uploads`
