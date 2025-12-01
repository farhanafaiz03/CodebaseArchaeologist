"""
In-memory session memory service.
Keeps per-session state, short-term conversation history, and basic compaction.
"""

from typing import Any, Dict, List
import time
import threading


class SessionMemory:
    def __init__(self):
        # session_id -> { "created": ts, "last_active": ts, "history": [...] , "metadata": {} }
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_session(self, session_id: str, metadata: Dict[str, Any] = None):
        metadata = metadata or {}
        with self._lock:
            self._sessions[session_id] = {
                "created": time.time(),
                "last_active": time.time(),
                "history": [],
                "metadata": metadata
            }

    def append(self, session_id: str, role: str, content: str):
        """Append a message to session history; role typically 'user' or 'agent'."""
        with self._lock:
            if session_id not in self._sessions:
                self.create_session(session_id)
            self._sessions[session_id]["history"].append({"role": role, "content": content, "ts": time.time()})
            self._sessions[session_id]["last_active"] = time.time()

    def get_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Return last `limit` messages for the session."""
        with self._lock:
            s = self._sessions.get(session_id)
            if not s:
                return []
            return s["history"][-limit:]

    def get_metadata(self, session_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._sessions.get(session_id, {}).get("metadata", {})

    def update_metadata(self, session_id: str, key: str, value: Any):
        with self._lock:
            if session_id not in self._sessions:
                self.create_session(session_id)
            self._sessions[session_id]["metadata"][key] = value
            self._sessions[session_id]["last_active"] = time.time()

    def compact_history(self, session_id: str, compaction_fn, keep_last: int = 10):
        """
        Perform context compaction: summarize older messages using compaction_fn.
        compaction_fn(history_chunk) -> summary_str
        """
        with self._lock:
            s = self._sessions.get(session_id)
            if not s:
                return
            history = s["history"]
            if len(history) <= keep_last:
                return
            old_chunk = history[:-keep_last]
            summary = compaction_fn(old_chunk)
            # replace old chunk with a single summarized message
            s["history"] = [{"role": "system", "content": f"[COMPACTED]: {summary}", "ts": time.time()}] + history[-keep_last:]
            s["last_active"] = time.time()

    def delete_session(self, session_id: str):
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
