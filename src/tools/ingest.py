"""Parse a file (OCR on), chunk it, embed it and store it in Qdrant.

Run for a folder:  python -m tools.ingest ../data/uploads
"""
import sys
import uuid
from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from qdrant_client.models import Distance, PointStruct, SparseVectorParams, VectorParams

from tools.models import COLLECTION, embed, qdrant


def ensure_collection() -> None:
    if not qdrant().collection_exists(COLLECTION):
        qdrant().create_collection(
            COLLECTION,
            vectors_config={"dense": VectorParams(size=1024, distance=Distance.COSINE)},
            sparse_vectors_config={"sparse": SparseVectorParams()},
        )


def ingest_file(path: str | Path) -> int:
    """Ingest one file. Returns the number of chunks stored."""
    path = Path(path)
    doc = DocumentConverter().convert(path).document
    chunks = list(HybridChunker().chunk(doc))
    texts = [c.text for c in chunks]
    if not texts:
        return 0

    ensure_collection()
    points = []
    for chunk, text, (dense, sparse) in zip(chunks, texts, embed(texts)):
        pages = {p.page_no for item in chunk.meta.doc_items for p in item.prov}
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector={"dense": dense, "sparse": sparse},
            payload={"source": path.name, "page": min(pages) if pages else None, "text": text},
        ))
    qdrant().upsert(COLLECTION, points)
    return len(points)


if __name__ == "__main__":
    for f in sorted(Path(sys.argv[1]).iterdir()):
        if f.is_file() and not f.name.startswith("."):
            print(f"{f.name}: {ingest_file(f)} chunks")
