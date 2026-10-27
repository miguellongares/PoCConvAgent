from agents import function_tool
from qdrant_client.models import Fusion, FusionQuery, Prefetch

from tools.models import COLLECTION, embed, qdrant, reranker

CANDIDATES = 20  # fetched by hybrid search, then reranked down to TOP_K
TOP_K = 5


@function_tool
def search_documents(query: str) -> list[dict]:
    """Search the uploaded documents. Returns passages with source file and page."""
    if not qdrant().collection_exists(COLLECTION):
        return []
    dense, sparse = embed([query])[0]
    hits = qdrant().query_points(
        COLLECTION,
        prefetch=[
            Prefetch(query=dense, using="dense", limit=CANDIDATES),
            Prefetch(query=sparse, using="sparse", limit=CANDIDATES),
        ],
        query=FusionQuery(fusion=Fusion.RRF),  # merge dense + sparse rankings
        limit=CANDIDATES,
    ).points
    if not hits:
        return []
    scores = reranker().compute_score([[query, h.payload["text"]] for h in hits])
    if not isinstance(scores, list):  # single hit returns a float
        scores = [scores]
    best = sorted(zip(scores, hits), key=lambda x: x[0], reverse=True)[:TOP_K]
    return [{"source": h.payload["source"], "page": h.payload["page"], "text": h.payload["text"]}
            for _, h in best]
