"""
Agent orchestration manager.
- supports sequential orchestration (Excavator -> Historian -> Narrator)
- parallel execution for batches using ThreadPoolExecutor or asyncio.gather
- looped tasks for iterative refinement
This module wires agents together and exposes simple high-level APIs.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Callable, Optional
import time


class AgentManager:
    def __init__(self, excavator, historian, narrator, long_term_memory=None, session_memory=None, max_workers: int = 4):
        self.excavator = excavator
        self.historian = historian
        self.narrator = narrator
        self.long_term_memory = long_term_memory
        self.session_memory = session_memory
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)

    # -----------------------------
    # Sequential flow
    # -----------------------------
    def run_sequential(self) -> Dict[str, Any]:
        """
        Run full sequential pipeline:
        1) Excavator.run() -> collect commits/files
        2) Historian.run(excavation_data) -> timeline summary
        3) Narrator.generate_report(...) -> final narrative
        """
        start = time.time()
        excavation_data = self.excavator.run()
        hist_out = self.historian.run(excavation_data)
        narrative = self.narrator.generate_report({**excavation_data, **hist_out})
        end = time.time()
        return {
            "excavation": excavation_data,
            "historian": hist_out,
            "narrative": narrative,
            "duration_seconds": end - start
        }

    # -----------------------------
    # Parallel processing for list of items
    # -----------------------------
    def run_parallel_on_commits(self, commits: List[Any], worker_fn: Callable[[Any], Any]) -> List[Any]:
        """
        Process commits in parallel using ThreadPoolExecutor.
        worker_fn(commit) is a synchronous function that returns a result.
        """
        futures = []
        results = []
        with self._executor as ex:
            futures = [ex.submit(worker_fn, c) for c in commits]
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append({"error": str(e)})
        return results

    # -----------------------------
    # Async loop for iterative refinement
    # -----------------------------
    async def run_loop_refine(self, initial_task, refine_fn: Callable[[Any], Optional[Any]], max_iters: int = 5):
        """
        Run an iterative loop:
        - initial_task: initial data object
        - refine_fn: async function that takes current state and returns either
                     new_state (to continue) or None to stop.
        """
        state = initial_task
        for i in range(max_iters):
            new_state = await refine_fn(state)
            if new_state is None:
                break
            state = new_state
        return state

    # -----------------------------
    # Convenience: parallel historian worker
    # -----------------------------
    def historian_parallel_worker(self, commit_obj):
        """
        Example worker that summarizes one commit using historian logic.
        This expects historian.summarize_commit to exist; if not, adapt accordingly.
        """
        try:
            # try to use historian.summarize_commit if implemented
            if hasattr(self.historian, "summarize_commit"):
                return self.historian.summarize_commit(commit_obj)
            # fallback: call external summarizer or return commit message
            return {"commit": getattr(commit_obj, "hexsha", str(commit_obj)), "message": str(commit_obj)}
        except Exception as e:
            return {"error": str(e)}
