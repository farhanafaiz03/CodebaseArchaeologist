import subprocess
from pathlib import Path
from typing import List, Optional

try:
    from git import Repo
except ImportError:
    Repo = None


class GitTool:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo = None

        if Repo is not None:
            try:
                self.repo = Repo(self.repo_path)
            except Exception:
                self.repo = None

    # -----------------------------
    # Get list of files tracked
    # -----------------------------
    def list_files(self) -> List[str]:
        if self.repo:
            return [str(f) for f in self.repo.git.ls_files().split("\n")]

        # CLI fallback
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.splitlines()

    # -----------------------------
    # Read commit history
    # -----------------------------
    def get_commit_history(self, max_commits: Optional[int] = 30):
        if self.repo:
            return list(self.repo.iter_commits())[:max_commits]

        # CLI fallback
        result = subprocess.run(
            ["git", "log", f"--max-count={max_commits}", "--pretty=%H|%an|%s"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        commits = []
        for line in result.stdout.splitlines():
            parts = line.split("|")
            if len(parts) == 3:
                commits.append({"hash": parts[0], "author": parts[1], "message": parts[2]})
        return commits

    # -----------------------------
    # Read a file at a specific commit
    # -----------------------------
    def get_file_at_commit(self, filepath: str, commit_hash: str) -> Optional[str]:
        try:
            if self.repo:
                return self.repo.git.show(f"{commit_hash}:{filepath}")

            # CLI fallback
            result = subprocess.run(
                ["git", "show", f"{commit_hash}:{filepath}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout if result.returncode == 0 else None
        except Exception:
            return None


# Module-level convenience functions
def get_commits(repo):
    """Get commit history from a GitPython Repo object."""
    try:
        return list(repo.iter_commits())
    except Exception:
        return []


def get_file_changes(repo, filepath: str):
    """Get file change history (simplified)."""
    try:
        commits = get_commits(repo)
        changes = []
        for commit in commits:
            try:
                if filepath in commit.stats.files:
                    changes.append({
                        "commit": commit.hexsha[:7],
                        "author": commit.author.name,
                        "message": commit.message.strip().split('\n')[0],
                        "stats": commit.stats.files[filepath]
                    })
            except Exception:
                pass
        return changes
    except Exception:
        return []
