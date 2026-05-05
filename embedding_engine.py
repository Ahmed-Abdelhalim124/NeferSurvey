# embedding_engine.py
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, TOP_K_RESULTS
from database import fetch_embeddings

print("⏳ Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print("✅ Embedding model loaded.")


def get_embedding(text: str) -> np.ndarray:
    """Convert text to normalized 384-dim embedding vector."""
    embedding = model.encode(text, convert_to_numpy=True).astype(np.float32)
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding


def build_faiss_index():
    """Build FAISS cosine similarity index from all stored embeddings."""
    records = fetch_embeddings()
    if not records:
        print("⚠️  No embeddings found in DB.")
        return None, []

    vectors = np.stack([r["embedding"] for r in records]).astype(np.float32)
    norms   = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / np.where(norms > 0, norms, 1)

    dim   = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    print(f"✅ FAISS index built with {index.ntotal} vectors (cosine similarity).")
    return index, records


def retrieve_top_k(question: str, index, records: list, k: int = TOP_K_RESULTS) -> list:
    """Retrieve top-k most relevant feedback entries for a question."""
    if index is None or not records:
        return []

    query_vec          = get_embedding(question).reshape(1, -1)
    distances, indices = index.search(query_vec, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        results.append({
            "id"   : records[idx]["id"],
            "text" : records[idx]["text"],
            "score": float(dist)
        })

    return results
