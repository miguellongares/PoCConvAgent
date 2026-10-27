"""Embedding and reranker models, loaded once on first use."""
from functools import cache

from FlagEmbedding import BGEM3FlagModel, FlagReranker
from qdrant_client import QdrantClient
from qdrant_client.models import SparseVector

from config import settings

COLLECTION = "documents"


@cache
def embedder() -> BGEM3FlagModel:
    return BGEM3FlagModel("BAAI/bge-m3", use_fp16=False)


@cache
def reranker() -> FlagReranker:
    return FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=False)


@cache
def qdrant() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def embed(texts: list[str]) -> list[tuple[list[float], SparseVector]]:
    """Return (dense, sparse) vectors for each text."""
    out = embedder().encode(texts, return_dense=True, return_sparse=True)
    sparse = [SparseVector(indices=[int(k) for k in w], values=[float(v) for v in w.values()])
              for w in out["lexical_weights"]]
    return list(zip(out["dense_vecs"].tolist(), sparse))
