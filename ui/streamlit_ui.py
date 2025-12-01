import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import asyncio
from orchestrator.agent_manager import AgentManager
from agents.excavator import ExcavatorAgent
from agents.remote_excavator import RemoteExcavatorAgent
from agents.historian import HistorianAgent
from agents.narrator import NarratorAgent
from memory.session_memory import SessionMemory
from memory.long_term_memory import LongTermMemory
from tools.rag_tool import RAGTool



# ----------- Helper to run async inside Streamlit -----------
def run_async(coro):
    return asyncio.run(coro)


def is_git_url(text: str) -> bool:
    """Check if text is a GitHub/Git URL."""
    return text.startswith(("http://", "https://", "git@")) and ".git" in text.lower()


def load_repo(repo_path):
    """Check if path is a valid git repository."""
    return os.path.isdir(os.path.join(repo_path, ".git"))


def main():
    st.set_page_config(page_title="Codebase Archaeologist", layout="wide")

    st.title("🧭 Codebase Archaeologist – Remote Analysis")
    st.caption("🌐 Analyze any GitHub repository without downloading to your system")

    # Initialize session state for storing analysis results
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "current_repo" not in st.session_state:
        st.session_state.current_repo = None

    # Input section with tabs for local and remote repos
    col1, col2 = st.columns([3, 1])
    
    with col1:
        repo_input = st.text_input(
            "Repository URL or Local Path",
            value="https://github.com/pallets/flask.git",
            help="Enter a GitHub URL (ending with .git) or local repo path"
        )
    
    with col2:
        st.write("") # spacing
        st.write("") # spacing
        input_type = "🌐 Remote" if is_git_url(repo_input) else "💾 Local"
        st.caption(f"{input_type}")

    # Show examples and info
    tab1, tab2 = st.tabs(["📚 Example Repos", "ℹ️ How It Works"])
    
    with tab1:
        st.markdown("""
        **Public GitHub repositories to test (no cloning needed!):**
        
        Small & Fast:
        - `https://github.com/pallets/flask.git` ⚡
        - `https://github.com/psf/requests.git` ⚡
        
        Medium:
        - `https://github.com/microsoft/TypeScript.git`
        - `https://github.com/facebook/react.git`
        
        Large:
        - `https://github.com/torvalds/linux.git` (may take a moment)
        """)
    
    with tab2:
        st.markdown("""
        **Why Remote Analysis?**
        - ✅ No disk space needed
        - ✅ No temp files or cleanup issues
        - ✅ Works from anywhere
        - ✅ Fast (API-based)
        - ✅ Perfect for shared/cloud environments
        
        **What Gets Analyzed:**
        1. Commit history (from Git/GitHub API)
        2. Author statistics
        3. Commit message patterns
        4. Repository metadata
        5. AI-generated insights
        """)

    if st.button("🚀 Run Analysis"):
        repo_path = repo_input
        
        try:
            # Handle GitHub URLs - NO CLONING, analyze remotely
            if is_git_url(repo_input):
                with st.spinner(f"🔗 Connecting to remote repository {repo_input}..."):
                    # Initialize remote excavator (no cloning!)
                    vector_store = RAGTool()
                    excavator = RemoteExcavatorAgent(repo_input, vector_store=vector_store)
                    historian = HistorianAgent(vector_store=vector_store)
                    narrator = NarratorAgent(historian_agent=historian, vector_store=vector_store)
                    
                    # Note: Using simplified orchestration for remote repos
                    with st.spinner("🔍 Analyzing commits remotely..."):
                        excavation_data = excavator.run()
                    
                    with st.spinner("📜 Analyzing timeline..."):
                        hist_output = historian.run(excavation_data)
                    
                    with st.spinner("📖 Generating narrative..."):
                        narrative = narrator.generate_report({**excavation_data, **hist_output})
                    
                    result = {
                        "excavation": excavation_data,
                        "historian": hist_output,
                        "narrative": narrative,
                        "duration_seconds": 0,  # Not tracking for remote
                        "vector_store": vector_store,
                        "narrator": narrator
                    }
            else:
                # Local repo analysis
                if not load_repo(repo_path):
                    st.error("❌ Invalid repository (no .git directory found)")
                    return

                # Initialize memory and vector store
                session_mem = SessionMemory()
                long_term = LongTermMemory()
                vector_store = RAGTool()

                # Initialize agents
                excavator = ExcavatorAgent(repo_path, vector_store=vector_store)
                historian = HistorianAgent(vector_store=vector_store)
                narrator = NarratorAgent(historian_agent=historian, vector_store=vector_store)

                # Orchestrator
                manager = AgentManager(
                    excavator=excavator,
                    historian=historian,
                    narrator=narrator,
                    session_memory=session_mem,
                    long_term_memory=long_term
                )

                with st.spinner("🔍 Agents are analyzing the repository..."):
                    result = manager.run_sequential()
                    result["vector_store"] = vector_store
                    result["narrator"] = narrator

            st.success("✔ Analysis complete")
            st.session_state.analysis_result = result
            st.session_state.current_repo = repo_input

            # Display results in better format
            st.subheader("📊 Repository Overview")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Commits Analyzed", result["historian"].get("commit_count", 0))
            with col2:
                st.metric("Unique Authors", result["historian"].get("author_count", 0))
            with col3:
                repo_info = result["excavation"].get("repo_info", {})
                st.metric("Stars", repo_info.get("stars", "N/A"))
            with col4:
                st.metric("Language", repo_info.get("language", "N/A"))

            # Repository info if available
            if result["excavation"].get("repo_info"):
                st.subheader("ℹ️ Repository Information")
                info = result["excavation"]["repo_info"]
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {info.get('name', 'N/A')}")
                    st.write(f"**Stars:** {info.get('stars', 0)}")
                with col2:
                    st.write(f"**Language:** {info.get('language', 'N/A')}")
                    st.write(f"**Updated:** {info.get('updated_at', 'N/A')}")
                
                if info.get('description'):
                    st.write(f"**Description:** {info.get('description')}")

            # Commit Pattern Analysis
            if result["historian"].get("commit_patterns"):
                st.subheader("📈 Commit Patterns")
                patterns = result["historian"]["commit_patterns"]
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Commit Types:**")
                    st.bar_chart(patterns.get("types", {}))
                with col2:
                    st.write("**Top Authors:**")
                    st.bar_chart(patterns.get("top_authors", {}))

            # Top Keywords
            if result["historian"].get("commit_patterns", {}).get("keywords"):
                st.subheader("🔤 Top Keywords in Commits")
                keywords = result["historian"]["commit_patterns"]["keywords"]
                st.bar_chart(keywords)

            # Library changes and refactors
            if result["historian"].get("library_changes") or result["historian"].get("refactor_events"):
                st.subheader("🔄 Notable Architecture Changes")
                col1, col2 = st.columns(2)
                with col1:
                    if result["historian"].get("library_changes"):
                        st.write("**Library/Dependency Changes:**")
                        for change in result["historian"]["library_changes"]:
                            st.caption(change)
                with col2:
                    if result["historian"].get("refactor_events"):
                        st.write("**Major Refactors:**")
                        for refactor in result["historian"]["refactor_events"]:
                            st.caption(refactor)

            # Timeline Summary (LLM Analysis)
            st.subheader("📜 Historical Analysis")
            st.write(result["historian"]["timeline_summary"])

            # Q&A Section
            st.subheader("❓ Ask Questions About This Code")
            st.write("Use AI to understand why specific libraries were chosen or how the code evolved:")
            
            question = st.text_input(
                "What would you like to know about this repository?",
                placeholder="e.g., 'Why does this project use Flask?' or 'What were the major refactoring efforts?'"
            )
            
            if question and st.button("🤖 Get Answer"):
                with st.spinner("🔎 Searching code context and history..."):
                    answer = result["narrator"].answer(
                        question, 
                        excavation_data=result.get("excavation"),
                        historian_data=result.get("historian")
                    )
                st.info(f"**Answer:** {answer}")

            # Full JSON for advanced users
            with st.expander("📋 Full Analysis JSON"):
                # Remove non-serializable objects for JSON display
                display_result = {k: v for k, v in result.items() if k not in ["vector_store", "narrator"]}
                st.json(display_result)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Tip: For GitHub repos, ensure the URL ends with `.git` (e.g., `https://github.com/user/repo.git`)")
    
    # Display Q&A for previously analyzed repo (in sidebar or continuity section)
    elif st.session_state.analysis_result:
        st.divider()
        st.subheader("❓ Continue Asking Questions")
        st.caption(f"Current repo: {st.session_state.current_repo}")
        
        question = st.text_input(
            "Ask another question about this repository:",
            placeholder="e.g., 'What are the main dependencies?' or 'How did the architecture evolve?'"
        )
        
        if question and st.button("🤖 Get Answer"):
            result = st.session_state.analysis_result
            with st.spinner("🔎 Searching code context and history..."):
                answer = result["narrator"].answer(
                    question,
                    excavation_data=result.get("excavation"),
                    historian_data=result.get("historian")
                )
            st.info(f"**Answer:** {answer}")


if __name__ == "__main__":
    main()
