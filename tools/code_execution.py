import subprocess
from typing import Optional


class CodeExecutor:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    # -----------------------------
    # Run a shell command safely
    # -----------------------------
    def run_command(self, command: str) -> str:
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                shell=True,
                capture_output=True,
                text=True
            )
            return result.stdout + ("\nERR:" + result.stderr if result.stderr else "")
        except Exception as e:
            return f"Execution failed: {e}"

    # -----------------------------
    # Run pytest tests
    # -----------------------------
    def run_tests(self):
        return self.run_command("pytest -q")

    # -----------------------------
    # Run flake8 or pylint
    # -----------------------------
    def run_static_analysis(self):
        return self.run_command("flake8 .")
