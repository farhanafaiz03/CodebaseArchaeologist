"""
Long-term memory backed by FAISS (via tools.rag_tool.RAGTool or direct usage).
Provides add/search/save/load helper wrappers.
"""

import os
import json
from typing import List, Tuple, Optional
from tools.rag_tool import RAGTool


class LongTermMemory:
    def __init__(self, persist_path: str = "memory_store"):
        os.makedirs(persist_path, exist_ok=True)
        self.persist_path = persist_path
        self.rag = RAGTool()  # encapsulated sentence-transformers + faiss index
        # a simple metadata list parallel to rag.text_store for persistence
        self._meta_file = os.path.join(self.persist_path, "meta.json")
        self._load_meta_if_exists()

    def _load_meta_if_exists(self):
        if os.path.exists(self._meta_file):
            try:
                with open(self._meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    # If meta contains texts, re-add them to the RAG tool
                    texts = [m.get("text") for m in meta if m.get("text")]
                    if texts:
                        self.rag.add_documents(texts)
            except Exception:
                pass

    def add(self, text: str, metadata: dict = None):
        """Add a document to long-term memory."""
        metadata = metadata or {}
        self.rag.add_documents([text])
        # persist minimal metadata
        meta_entry = {"text": text, "metadata": metadata}
        self._persist_meta_entry(meta_entry)

    def _persist_meta_entry(self, entry: dict):
        try:
            meta = []
            if os.path.exists(self._meta_file):
                with open(self._meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            meta.append(entry)
            with open(self._meta_file, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """Return top-k similar documents (text, distance)."""
        return self.rag.query(query, k=k)

    def get_all_texts(self) -> List[str]:
        return self.rag.text_store
