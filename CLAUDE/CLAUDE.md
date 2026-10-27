# WHO conversational agent (prototype)

Chat agent that answers health questions using the WHO GHO API and a small set of ingested documents.
Design: `Documentation/WHO_AGENT_PROTOTYPE.md` and `Documentation/architecture.svg`.

## Principles
- Prototype: keep code simple, short and easy to follow. No extra abstractions.
- Everything runs in Docker (`docker compose up --build`). Frontend is Chainlit on port 8000.
- Scope limits: no conversation storage, no user accounts, one machine.
- Ask the user when in doubt.

## Stack
`openai-agents` (agent loop), Bonsai 2 via OpenAI-compatible API (`AsyncOpenAI`), `chainlit`, `httpx`,
`docling` (parse + OCR), `bge-m3` + `bge-reranker-v2-m3` (FlagEmbedding), Qdrant, `pydantic-settings`.

## Layout
- `src/app.py`: Chainlit entry point. Attached files are ingested, then the agent runs.
- `src/agent.py`: agent instructions and tool list.
- `src/llm_factory.py`: `make_model()`, the only place the LLM is configured (via `.env`).
- `src/config.py`: settings from env vars.
- `src/tools/`: `who.py`, `news.py` (PADI-web outbreak news API), `stac.py` (MOOD STAC catalogue search + `plot_dataset_map`), `retrieval.py`, `ingest.py`, `models.py` (shared model/Qdrant loaders), later `vision.py`.
- `eval/questions.jsonl`: test questions (not written yet).

## Conventions
- Configuration only through `.env` / `config.py`. Never hardcode keys or URLs. `.env` is git-ignored.
- Tracing is disabled on purpose (no data leaves to OpenAI's platform).
- The agent must never state a number that did not come from a tool, and must cite indicator code, country, year, or document and page.
- Update `PROGRESS.md` and `TODO.md` (in this folder) after each piece of work.
