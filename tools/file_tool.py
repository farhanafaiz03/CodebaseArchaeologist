import os
from pathlib import Path
from typing import List, Optional


class FileTool:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    # -----------------------------
    # Read a file safely
    # -----------------------------
    def read_file(self, filepath: str) -> Optional[str]:
        path = self.base_path / filepath
        if not path.exists():
            return None

        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None

    # -----------------------------
    # List all project files
    # -----------------------------
    def list_all_files(self) -> List[str]:
        file_paths = []
        for root, dirs, files in os.walk(self.base_path):
            for f in files:
                file_paths.append(str(Path(root) / f))
        return file_paths


# Module-level convenience function
def read_file_safe(filepath: str) -> Optional[str]:
    """Read a file safely with error handling."""
    try:
        path = Path(filepath)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
