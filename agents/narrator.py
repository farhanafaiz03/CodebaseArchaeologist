from typing import Optional, Any, Dict
from tools.rag_tool import search_context
from agents.llm import call_llm


class NarratorAgent:
    """
    The Narrator creates readable explanations and stories from the
    technical analysis produced by the other agents. It also answers
    user queries with evidence from code and history.
    """

    def __init__(self, historian_agent: Optional[Any] = None, vector_store: Optional[Any] = None):
        self.historian = historian_agent
        self.vector_store = vector_store

    def generate_report(self, data: Dict[str, Any]) -> str:
        """Create a comprehensive narrative from all agent outputs."""
        
        # Extract key data
        commit_count = data.get("commit_count", 0)
        author_count = data.get("author_count", 0)
        top_authors = data.get("top_authors", {})
        timeline = data.get("timeline_summary", "")
        patterns = data.get("commit_patterns", {})
        languages = data.get("languages", {})
        library_changes = data.get("library_changes", [])
        refactors = data.get("refactor_events", [])
        hotspots = data.get("hotspots", {})
        
        report = call_llm(
            f"""
            You are a technical storyteller writing an executive report about a software project's evolution.

            ## Project Analysis Summary

            **Metrics:**
            - Total Commits: {commit_count}
            - Contributors: {author_count}
            - Top Contributors: {", ".join([f"{k} ({v})" for k, v in list(top_authors.items())[:3]])}
            - Languages: {", ".join([f"{k} ({v})" for k, v in list(languages.items())[:3]])}

            **Commit Types:** {patterns.get('types', {})}
            **Common Focus Areas:** {", ".join(list(patterns.get('keywords', {}).keys())[:5])}

            **Notable Events:**
            - Library/Dependency Changes: {library_changes}
            - Major Refactoring Efforts: {refactors}
            - Hotspot Files (most changed): {list(hotspots.keys())[:5]}

            **Historical Analysis:**
            {timeline}

            ---

            Now write a compelling narrative (3-4 paragraphs) that tells the story of this codebase:
            1. Origins and purpose
            2. Evolution and major decisions
            3. Current state and architecture patterns
            4. Key technical decisions and their implications

            Make it engaging, specific, and grounded in the data provided.
            """
        )
        
        return report

    def answer(self, question: str, excavation_data: Optional[Dict] = None, historian_data: Optional[Dict] = None) -> str:
        """Answer developer questions using RAG context and historical data."""
        
        # Retrieve relevant code context
        rag_context = search_context(question, self.vector_store, k=5)
        
        # Build enriched context
        context_parts = [rag_context]
        
        # Add historical context if available
        if historian_data:
            timeline = historian_data.get("timeline_summary", "")
            if timeline:
                context_parts.append(f"Historical Context:\n{timeline}")
            
            library_changes = historian_data.get("library_changes", [])
            if library_changes:
                context_parts.append(f"Recent Library Changes:\n" + "\n".join(library_changes))
            
            refactors = historian_data.get("refactor_events", [])
            if refactors:
                context_parts.append(f"Recent Refactoring:\n" + "\n".join(refactors))
        
        full_context = "\n\n".join(context_parts)
        
        answer = call_llm(
            f"""
            You are an expert code archaeologist helping developers understand legacy code.

            **Developer Question:**
            {question}

            **Retrieved Context:**
            {full_context}

            ---

            Provide a clear, specific answer grounded in the context above. If asking about "why" decisions were made,
            explain the likely architectural or business reasons. Reference specific code patterns or commit messages
            when possible to support your answer.
            """
        )
        
        return answer

    def answer_why(self, query: str) -> str:
        """Specialized method for 'why' questions about architecture and design decisions."""
        
        rag_context = search_context(query, self.vector_store, k=8)
        
        return call_llm(
            f"""
            You are a code historian explaining architectural decisions.

            **Question:** {query}

            **Code and Commit Context:**
            {rag_context}

            ---

            Explain the "why" behind this decision. Consider:
            1. What problem was this solving?
            2. What alternatives might have been considered?
            3. What trade-offs were made?
            4. Is this still the right choice today?

            Ground your answer in the specific code patterns and commit messages shown above.
            """
        )
