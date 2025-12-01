from typing import Dict, Any, List, Optional
from collections import Counter
from tools.git_tool import get_commits
from tools.rag_tool import search_context
from agents.llm import call_llm


class HistorianAgent:
    """
    The Historian analyzes commit evolution, infers intent behind changes,
    and summarizes important events in the codebase.
    """

    def __init__(self, vector_store: Optional[Any] = None):
        self.vector_store = vector_store

    def run(self, excavation_data: Dict[str, Any]) -> Dict[str, Any]:
        print("[Historian] Analyzing commit timeline...")

        commits = excavation_data.get("commits", [])
        patterns = excavation_data.get("commit_patterns", {})
        file_metrics = excavation_data.get("file_metrics", {})
        hotspots = excavation_data.get("hotspots", {})
        language_breakdown = excavation_data.get("language_breakdown", {})
        
        # For remote repos, patterns are already computed
        if not patterns:
            patterns = self._analyze_commit_patterns(commits)
        
        # Detect library changes and refactors
        library_changes = self._detect_library_changes(commits)
        refactor_events = self._detect_refactors(commits)

        # Use LLM to generate insights
        timeline_summary = call_llm(
            f"""
            Analyze this Git repository based on commit history:

            **Statistics:**
            - Total Commits: {len(commits)}
            - Commit Types: {patterns.get('types', {})}
            - Top Authors: {patterns.get('top_authors', {})}
            - Common Keywords: {list(patterns.get('keywords', {}).keys())[:5]}

            **Notable Events:**
            - Library Changes: {library_changes}
            - Major Refactors: {refactor_events}

            Based on this commit history, provide insights on:
            1. What is the nature of this project?
            2. What development patterns do you see?
            3. Who are the main contributors?
            4. What is the commit velocity and activity level?
            5. What technical focus areas are evident from commit messages?
            6. What major technology shifts or refactors happened?
            7. Why might they have made these architectural decisions?

            Be specific and actionable, not generic. Reference specific commits where relevant.
            """
        )

        print("[Historian] Timeline analysis complete.")

        return {
            "timeline_summary": timeline_summary,
            "commit_count": len(commits),
            "author_count": len(patterns.get("top_authors", {})),
            "top_authors": patterns.get("top_authors", {}),
            "hotspots": hotspots,
            "commit_patterns": patterns,
            "languages": language_breakdown,
            "library_changes": library_changes,
            "refactor_events": refactor_events
        }

    def _analyze_commit_patterns(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract patterns from commit messages."""
        keywords = Counter()
        message_types = Counter()
        
        for c in commits:
            msg = c.get('message', '').lower()
            
            # Classify commit type
            if any(w in msg for w in ['fix', 'bug', 'issue', 'resolve', 'patch']):
                message_types['bug_fix'] += 1
            elif any(w in msg for w in ['feat', 'feature', 'add', 'new', 'implement']):
                message_types['feature'] += 1
            elif any(w in msg for w in ['refactor', 'clean', 'improve', 'optimize', 'perf']):
                message_types['refactor'] += 1
            elif any(w in msg for w in ['doc', 'readme', 'comment', 'update docs']):
                message_types['documentation'] += 1
            else:
                message_types['other'] += 1
            
            # Extract keywords
            words = [w for w in msg.split() if len(w) > 4 and not w.startswith('#')]
            keywords.update(words)
        
        return {
            "types": dict(message_types),
            "keywords": dict(keywords.most_common(10))
        }

    def _analyze_authors(self, commits: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count commits per author."""
        return dict(Counter([c.get('author', 'unknown') for c in commits]).most_common(5))

    def _detect_library_changes(self, commits: List[Dict[str, Any]]) -> List[str]:
        """Detect when libraries/dependencies were added or changed."""
        changes = []
        keywords = ['import', 'require', 'install', 'pip', 'npm', 'maven', 'cargo', 'from', 'as']
        
        for commit in commits[:50]:  # Check recent commits
            msg = commit.get('message', '').lower()
            # Look for dependency/library mentions
            if any(word in msg for word in ['library', 'dependency', 'dependencies', 'package', 'upgrade', 'switch', 'migrate', 'adopt', 'integrate']):
                if any(keyword in msg for keyword in keywords):
                    changes.append(f"[{commit.get('hash')}] {commit.get('message')[:80]}")
        
        return changes[:5]  # Top 5 library changes

    def _detect_refactors(self, commits: List[Dict[str, Any]]) -> List[str]:
        """Detect major refactoring efforts."""
        refactors = []
        
        for commit in commits:
            msg = commit.get('message', '').lower()
            # Look for refactor/restructuring mentions
            if any(word in msg for word in ['refactor', 'restructure', 'rewrite', 'cleanup', 'reorganize', 'redesign', 'overhaul', 'consolidate', 'merge', 'split']):
                refactors.append(f"[{commit.get('hash')}] {commit.get('message')[:80]}")
        
        return refactors[:5]  # Top 5 refactors

    def answer_why(self, query: str) -> str:
        """Answer queries like: why was X library introduced?"""

        rag_context = search_context(query, self.vector_store)

        return call_llm(
            f"""
            You are a code historian.

            User question: {query}

            Context from codebase and commit history:
            {rag_context}

            Provide a clear and direct answer.
            """
        )
