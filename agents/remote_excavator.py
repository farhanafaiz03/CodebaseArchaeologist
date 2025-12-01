"""
Remote Excavator Agent - analyzes repositories without cloning to disk.
Works entirely with remote Git APIs and GitHub APIs.
"""

from typing import Dict, List, Any, Optional
from tools.remote_git_tool import RemoteGitTool


class RemoteExcavatorAgent:
    """
    Excavator for remote repositories.
    Fetches commit history and repository info without cloning.
    """

    def __init__(self, repo_url: str, vector_store: Optional[Any] = None):
        self.repo_url = repo_url
        self.vector_store = vector_store
        self.git_tool = RemoteGitTool(repo_url)

    def run(self) -> Dict[str, Any]:
        """Analyze remote repository."""
        print("[RemoteExcavator] Starting remote excavation...")

        # Get repository metadata
        repo_info = self.git_tool.get_repo_info()
        
        # Get commit history
        commits = self.git_tool.get_remote_commits(max_commits=100)
        
        # Analyze patterns
        patterns = self.git_tool.analyze_commit_patterns(commits)

        print(f"[RemoteExcavator] Found {len(commits)} commits")
        
        return {
            "repo_url": self.repo_url,
            "repo_info": repo_info,
            "commits": commits,
            "commits_count": len(commits),
            "commit_patterns": patterns,
            "authors_count": len(patterns.get("top_authors", {})),
            "sample_files": []  # No local files, working remote only
        }
