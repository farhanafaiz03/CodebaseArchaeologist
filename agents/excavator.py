import os
from git import Repo
from typing import Dict, List, Any, Optional
from collections import Counter
from tools.git_tool import get_commits, get_file_changes
from tools.file_tool import read_file_safe
from tools.rag_tool import embed_and_store


class ExcavatorAgent:
    """
    The Excavator Agent scans the repository, extracts commit history,
    reads files, and prepares structured data for downstream agents.
    """

    def __init__(self, repo_path: str, vector_store: Optional[Any] = None):
        self.repo_path = repo_path
        self.vector_store = vector_store
        try:
            self.repo = Repo(repo_path)
        except Exception as e:
            print(f"[Excavator] Warning: Could not initialize repo: {e}")
            self.repo = None

    def run(self) -> Dict[str, Any]:
        """Main function to extract codebase + commit history."""
        print("[Excavator] Starting excavation...")

        commits = self._get_commits_summary()
        code_files = self._collect_code_files()
        file_metrics = self._analyze_files(code_files)
        hotspots = self._identify_hotspots(commits)
        language_breakdown = self._language_breakdown(code_files)

        # Store key file samples for RAG (not all files to avoid memory overload)
        self._embed_key_files(code_files)

        print(f"[Excavator] Found {len(commits)} commits, {len(code_files)} files, {len(hotspots)} hotspots")
        return {
            "commits": commits,
            "files_count": len(code_files),
            "file_metrics": file_metrics,
            "hotspots": hotspots,
            "language_breakdown": language_breakdown,
            "sample_files": code_files[:10]  # Show first 10 files as samples
        }

    def _collect_code_files(self) -> List[str]:
        """Return list of source code files only."""
        extensions = (".py", ".js", ".ts", ".java", ".md")
        code_files = []

        for root, _, files in os.walk(self.repo_path):
            for f in files:
                if f.endswith(extensions):
                    rel_path = os.path.relpath(os.path.join(root, f), self.repo_path)
                    code_files.append(rel_path)

        return code_files

    def _get_commits_summary(self) -> List[Dict[str, Any]]:
        """Extract and summarize commit history."""
        if not self.repo:
            return []
        
        try:
            commits = list(self.repo.iter_commits())
            return [
                {
                    "hash": c.hexsha[:7],
                    "author": c.author.name,
                    "date": c.committed_datetime.isoformat(),
                    "message": c.message.strip().split('\n')[0],
                    "files_changed": len(c.stats.files)
                }
                for c in commits[:100]  # Last 100 commits for analysis
            ]
        except Exception as e:
            print(f"[Excavator] Error getting commits: {e}")
            return []

    def _identify_hotspots(self, commits: List[Dict[str, Any]]) -> Dict[str, int]:
        """Find most frequently modified files (hotspots)."""
        if not self.repo:
            return {}
        
        try:
            file_change_count = Counter()
            for commit in commits:
                try:
                    c = self.repo.commit(commit["hash"])
                    for file_path in c.stats.files.keys():
                        file_change_count[file_path] += 1
                except Exception:
                    pass
            return dict(file_change_count.most_common(15))  # Top 15 hotspots
        except Exception as e:
            print(f"[Excavator] Error identifying hotspots: {e}")
            return {}

    def _language_breakdown(self, code_files: List[str]) -> Dict[str, int]:
        """Analyze programming language distribution."""
        ext_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.xml': 'XML',
            '.go': 'Go',
            '.rs': 'Rust',
        }
        
        lang_count = Counter()
        for f in code_files:
            ext = os.path.splitext(f)[1].lower()
            lang = ext_map.get(ext, 'Other')
            lang_count[lang] += 1
        
        return dict(lang_count.most_common())

    def _analyze_files(self, code_files: List[str]) -> Dict[str, Any]:
        """Analyze file statistics."""
        total_lines = 0
        largest_files = []
        
        for f in code_files[:50]:  # Sample first 50 files
            try:
                content = read_file_safe(os.path.join(self.repo_path, f))
                if content:
                    lines = len(content.split('\n'))
                    total_lines += lines
                    largest_files.append((f, lines))
            except Exception:
                pass
        
        largest_files.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "total_files": len(code_files),
            "estimated_total_lines": total_lines * (len(code_files) / max(50, len(code_files))),
            "largest_files": largest_files[:5]
        }

    def _embed_key_files(self, code_files: List[str]):
        """Embed key files and code chunks for RAG-based Q&A."""
        if not self.vector_store:
            return
        
        print(f"[Excavator] Embedding code files for RAG context...")
        embedded = 0
        
        # Strategy: embed top 50 files by size/importance
        files_to_embed = []
        
        # Priority 1: README, docs, config
        key_patterns = ('README', 'setup.py', 'main.py', 'index.', 'app.', 'package.json', 'requirements', 'config')
        for f in code_files:
            if any(pattern.lower() in f.lower() for pattern in key_patterns):
                files_to_embed.append(f)
        
        # Priority 2: Add more Python files if we have room
        for f in code_files:
            if f.endswith('.py') and len(files_to_embed) < 40:
                files_to_embed.append(f)
        
        # Remove duplicates while preserving order
        files_to_embed = list(dict.fromkeys(files_to_embed))[:40]
        
        for f in files_to_embed:
            try:
                full_path = os.path.join(self.repo_path, f)
                content = read_file_safe(full_path)
                
                if not content:
                    continue
                
                # Skip massive files
                if len(content) > 100000:
                    content = content[:100000]
                
                # Store full file content
                file_doc = f"# File: {f}\n\n{content}"
                embed_and_store(file_doc, metadata={"filename": f, "type": "file"}, store=self.vector_store)
                embedded += 1
                
                # Also store chunks for better retrieval
                for chunk in self._chunk_code(content, f):
                    embed_and_store(chunk, metadata={"filename": f, "type": "chunk"}, store=self.vector_store)
                    
            except Exception as e:
                pass  # Silent fail on individual files
        
        print(f"[Excavator] Embedded {embedded} files into RAG vector store")

    def _chunk_code(self, content: str, filename: str, chunk_size: int = 1000) -> List[str]:
        """Split code into semantically meaningful chunks."""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        
        for i, line in enumerate(lines):
            current_chunk.append(line)
            
            # Check if we should break at this line
            should_break = False
            
            # Break on class/function definitions (Python)
            if any(keyword in line for keyword in ['def ', 'class ', 'async def ', '@']):
                if current_chunk and len('\n'.join(current_chunk)) > 100:
                    should_break = True
            
            # Break when chunk gets large enough
            if len('\n'.join(current_chunk)) > chunk_size:
                should_break = True
            
            if should_break and current_chunk:
                chunk_text = f"### {filename} ###\n" + '\n'.join(current_chunk)
                chunks.append(chunk_text)
                current_chunk = []
        
        # Add remaining content
        if current_chunk:
            chunk_text = f"### {filename} ###\n" + '\n'.join(current_chunk)
            chunks.append(chunk_text)
        
        return chunks