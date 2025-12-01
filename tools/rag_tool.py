from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


class RAGTool:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.text_store = []

    # -----------------------------
    # Build vector store
    # -----------------------------
    def add_documents(self, documents: List[str]):
        embeddings = self.model.encode(documents)
        embeddings = np.array(embeddings).astype("float32")

        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])

        self.index.add(embeddings)
        self.text_store.extend(documents)

    # -----------------------------
    # Query vector store
    # -----------------------------
    def query(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        if self.index is None:
            return []

        q_embed = self.model.encode([query]).astype("float32")
        distances, indices = self.index.search(q_embed, k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.text_store):
                results.append((self.text_store[idx], float(dist)))

        return results


# Module-level convenience functions
def embed_and_store(text: str, metadata: dict = None, store=None):
    """Embed text and store in a RAG vector store."""
    if store is None:
        return
    try:
        store.add_documents([text])
    except Exception:
        pass


def search_context(query: str, store=None, k: int = 5) -> str:
    """Search vector store for context related to a query."""
    if store is None:
        return ""
    try:
        results = store.query(query, k=k)
        context = "\n".join([text for text, _ in results])
        return context
    except Exception:
        return ""
