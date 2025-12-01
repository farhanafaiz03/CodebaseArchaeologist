"""
Entry point for running Codebase Archaeologist locally (CLI version).
"""

import argparse
from agents.excavator import ExcavatorAgent
from agents.historian import HistorianAgent
from agents.narrator import NarratorAgent
from orchestrator.agent_manager import AgentManager
from memory.session_memory import SessionMemory
from memory.long_term_memory import LongTermMemory
from tools.rag_tool import RAGTool


def run_cli(repo_path: str):
    session_mem = SessionMemory()
    long_mem = LongTermMemory()
    vector_store = RAGTool()

    excavator = ExcavatorAgent(repo_path, vector_store=vector_store)
    historian = HistorianAgent(vector_store=vector_store)
    narrator = NarratorAgent(historian_agent=historian)

    manager = AgentManager(
        excavator=excavator,
        historian=historian,
        narrator=narrator,
        session_memory=session_mem,
        long_term_memory=long_mem
    )

    print("\n🔍 Running multi-agent codebase analysis...\n")
    result = manager.run_sequential()

    print("\n--- Excavator Output ---")
    print(result["excavation"])

    print("\n--- Historian Output ---")
    print(result["historian"])

    print("\n--- Final Narrative ---")
    print(result["narrative"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="./examples/sample_repo", help="Path to repo")
    args = parser.parse_args()

    run_cli(args.repo)
