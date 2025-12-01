"""
Remote Git tool for analyzing repos without cloning to disk.
Uses GitHub API for reliable, fast access to commit history.
"""

import subprocess
import json
from typing import List, Dict, Any, Optional
from collections import Counter

try:
    import requests
except ImportError:
    requests = None


class RemoteGitTool:
    """Analyze Git repositories remotely using GitHub API."""
    
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.repo_path = self._extract_repo_path()
        self.is_github = "github.com" in repo_url
        
        if self.is_github:
            self._validate_github_repo()
    
    def _extract_repo_path(self) -> str:
        """Extract owner/repo from URL."""
        url = self.repo_url.replace("https://github.com/", "").replace(".git", "").replace("http://github.com/", "")
        return url
    
    def _validate_github_repo(self) -> bool:
        """Validate that the GitHub repo exists."""
        if not requests:
            print("[RemoteGitTool] requests library not available, skipping validation")
            return False
        
        try:
            api_url = f"https://api.github.com/repos/{self.repo_path}"
            response = requests.get(api_url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"Repository not found (HTTP {response.status_code})")
            return True
        except Exception as e:
            raise Exception(f"Invalid GitHub repository: {str(e)}")
    
    def get_remote_commits(self, max_commits: int = 100) -> List[Dict[str, Any]]:
        """Fetch commit history from GitHub API."""
        if not self.is_github or not requests:
            print("[RemoteGitTool] GitHub API unavailable, trying git command")
            return self._get_commits_via_git()
        
        try:
            commits = []
            api_url = f"https://api.github.com/repos/{self.repo_path}/commits"
            
            # Paginate through commits
            page = 1
            per_page = min(100, max_commits)
            
            while len(commits) < max_commits:
                params = {
                    "per_page": per_page,
                    "page": page
                }
                
                response = requests.get(api_url, params=params, timeout=15)
                
                if response.status_code != 200:
                    print(f"[RemoteGitTool] GitHub API error: {response.status_code}")
                    break
                
                batch = response.json()
                if not batch:
                    break
                
                for commit in batch:
                    if len(commits) >= max_commits:
                        break
                    
                    commit_obj = {
                        "hash": commit["sha"][:7],
                        "author": commit["commit"]["author"].get("name", "Unknown"),
                        "email": commit["commit"]["author"].get("email", ""),
                        "date": commit["commit"]["author"].get("date", ""),
                        "message": commit["commit"]["message"].split('\n')[0]
                    }
                    commits.append(commit_obj)
                
                if len(batch) < per_page:
                    break
                
                page += 1
            
            print(f"[RemoteGitTool] Fetched {len(commits)} commits from GitHub API")
            return commits
            
        except Exception as e:
            print(f"[RemoteGitTool] GitHub API error: {e}")
            return []
    
    def _get_commits_via_git(self) -> List[Dict[str, Any]]:
        """Fallback: try git command with shorter timeout."""
        try:
            cmd = [
                "git", "log",
                f"--max-count=50",
                "--pretty=format:%H|%an|%ae|%ai|%s",
                f"{self.repo_url}@HEAD"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            commits = []
            
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    parts = line.split('|')
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0][:7],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": parts[4]
                        })
                return commits
        except Exception as e:
            print(f"[RemoteGitTool] Git command failed: {e}")
        
        return []
    
    def get_repo_info(self) -> Dict[str, Any]:
        """Get repository information from GitHub API."""
        if not self.is_github or not requests:
            return {}
        
        try:
            api_url = f"https://api.github.com/repos/{self.repo_path}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code != 200:
                return {}
            
            data = response.json()
            return {
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "language": data.get("language", ""),
                "updated_at": data.get("updated_at", ""),
                "url": data.get("html_url", ""),
            }
        except Exception as e:
            print(f"[RemoteGitTool] Could not fetch repo info: {e}")
            return {}
    
    def analyze_commit_patterns(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns from commit messages."""
        keywords = Counter()
        message_types = Counter()
        authors = Counter()
        
        for c in commits:
            msg = c.get('message', '').lower()
            author = c.get('author', 'unknown')
            authors[author] += 1
            
            # Classify commit type
            if any(w in msg for w in ['fix', 'bug', 'issue', 'resolve', 'patch', 'hotfix']):
                message_types['bug_fix'] += 1
            elif any(w in msg for w in ['feat', 'feature', 'add', 'new', 'implement', 'introduce']):
                message_types['feature'] += 1
            elif any(w in msg for w in ['refactor', 'clean', 'improve', 'optimize', 'perf', 'performance']):
                message_types['refactor'] += 1
            elif any(w in msg for w in ['doc', 'readme', 'comment', 'docs', 'documentation']):
                message_types['documentation'] += 1
            elif any(w in msg for w in ['test', 'tests', 'testing', 'coverage']):
                message_types['tests'] += 1
            else:
                message_types['other'] += 1
            
            # Extract keywords
            words = [w for w in msg.split() if len(w) > 4 and not w.startswith('#') and not w.startswith('(')]
            keywords.update(words)
        
        return {
            "types": dict(message_types),
            "keywords": dict(keywords.most_common(15)),
            "top_authors": dict(authors.most_common(10))
        }
