# Codebase Archaeologist - AI Assistant for Understanding Legacy Code

> *"Understand why your code was written the way it is, not just what it does."*

## What is Codebase Archaeologist?

Codebase Archaeologist is a multi-agent AI system that analyzes legacy code and git history to answer developer questions like:

- **"Why do we use this library instead of that one?"**
- **"What major refactoring efforts happened in this project?"**
- **"Who are the main contributors and what do they focus on?"**
- **"How did the architecture evolve over time?"**

Instead of manually reading hundreds of commits, Codebase Archaeologist uses AI to explain the reasoning behind code decisions, grounded in actual commit history and source code.

## The Problem It Solves

When joining a new project:
- 🔴 Code is old and complex (legacy)
- 🔴 Documentation is missing or outdated
- 🔴 Understanding **why** decisions were made is hard
- 🔴 Onboarding takes weeks, debugging is risky

## The Solution: Three-Agent System

### 1. **Excavator Agent** 🔍
Scans the entire codebase and git history:
- Reads all source code files
- Extracts commit history with authors and timestamps
- Embeds code into a vector database for semantic search
- Identifies "hotspots" (most-changed files)
- Maps programming language distribution

### 2. **Historian Agent** 📜
Analyzes changes and detects patterns:
- Classifies commits (features, bug fixes, refactors, docs)
- Detects library/dependency switches
- Identifies major refactoring events
- Extracts keywords showing technical focus
- Generates AI-powered historical insights

### 3. **Narrator Agent** 🎭
Creates narratives and answers questions:
- Generates readable project history report
- Answers developer questions using AI
- Grounds answers in actual code and commits
- Provides evidence with commit references

## Example Output

### Question
```
"Why did we switch from SimpleDB to FastDBX?"
```

### Answer
```
In June 2022, SimpleDB caused performance issues during high load tests.
The team replaced it with FastDBX to improve performance.

Evidence:
- Commit abc123: "Switch to FastDBX for better performance"
- Performance improved by 3x in benchmarks
- Main contributors: Alice (5 commits), Bob (3 commits)
```

## Features

✅ **Multi-Agent System** - Sequential, parallel, and iterative execution  
✅ **RAG (Retrieval-Augmented Generation)** - Answers grounded in actual code  
✅ **Remote Analysis** - Works with GitHub URLs (no cloning needed)  
✅ **Interactive Q&A** - Ask questions, get instant answers  
✅ **Web Dashboard** - Beautiful Streamlit interface  
✅ **Memory Systems** - Session and long-term storage  
✅ **Git Integration** - Local repos and GitHub API  
✅ **LLM-Powered** - Uses OpenAI GPT-3.5-turbo  

## Quick Start

### Option 1: Web Interface (Recommended)
```bash
streamlit run ui/streamlit_ui.py
```
Then open `http://localhost:8501` in your browser.

### Option 2: Command Line
```bash
python main.py --repo /path/to/your/repo
```

### Option 3: Analyze Public GitHub Repository
In the web interface, enter:
```
https://github.com/pallets/flask.git
```
(No cloning required!)

## Usage Examples

### Test with Flask
```bash
streamlit run ui/streamlit_ui.py
# Enter: https://github.com/pallets/flask.git
# Ask: "Why does Flask use Werkzeug?"
```

### Test with Requests
```bash
streamlit run ui/streamlit_ui.py
# Enter: https://github.com/psf/requests.git
# Ask: "What are the core dependencies?"
```

### Test with Local Repository
```bash
python main.py --repo ./examples/sample_repo
```

## How It Works

```
┌─────────────────────────────────────┐
│  Developer Question or Git History  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    EXCAVATOR AGENT                  │
│  - Scans codebase                   │
│  - Reads git history                │
│  - Embeds code in vector store      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    HISTORIAN AGENT                  │
│  - Analyzes commit patterns         │
│  - Detects library changes          │
│  - Identifies refactors             │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    NARRATOR AGENT                   │
│  - Generates narrative report       │
│  - Answers developer questions      │
│  - Grounds answers in code/commits  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Human-Readable Explanation         │
│  with Evidence & Commit References  │
└─────────────────────────────────────┘
```

## Architecture

### Agents
- **excavator.py** - Scans local repositories
- **remote_excavator.py** - Analyzes GitHub repositories via API
- **historian.py** - Detects patterns and generates insights
- **narrator.py** - Generates reports and answers questions

### Tools
- **git_tool.py** - Git command interface
- **remote_git_tool.py** - GitHub API interface
- **rag_tool.py** - Vector store (FAISS + Sentence Transformers)
- **file_tool.py** - File system operations

### Core Components
- **agent_manager.py** - Orchestrates agent execution
- **session_memory.py** - Short-term data storage
- **long_term_memory.py** - Persistent vector store
- **llm.py** - OpenAI integration with fallback
- **streamlit_ui.py** - Web interface

## Installation

### Requirements
- Python 3.11+
- Virtual environment (recommended)
- Dependencies: See `requirements.txt`

### Setup
```bash
# Clone or navigate to repository
cd CodebaseArchaeologist

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# For OpenAI features (optional)
export OPENAI_API_KEY="your-key-here"
```

## Configuration

### Enable OpenAI Features
```bash
export OPENAI_API_KEY="sk-..."
```

Without an API key, the system uses stub responses for testing.

### Streamlit Configuration
```bash
streamlit run ui/streamlit_ui.py --server.port 8501
```

## Testing

### Test All Imports
```bash
python -c "from agents.excavator import ExcavatorAgent; from agents.historian import HistorianAgent; from agents.narrator import NarratorAgent; print('All imports OK')"
```

### Test CLI Version
```bash
python main.py --repo ./examples/sample_repo
```

### Test Web UI
```bash
streamlit run ui/streamlit_ui.py
# Navigate to http://localhost:8501
# Enter a GitHub URL and analyze
```

## Project Structure

```
CodebaseArchaeologist/
├── agents/              # AI agents
│   ├── excavator.py
│   ├── remote_excavator.py
│   ├── historian.py
│   ├── narrator.py
│   └── llm.py
├── tools/              # Utilities
│   ├── git_tool.py
│   ├── remote_git_tool.py
│   ├── rag_tool.py
│   └── file_tool.py
├── orchestrator/       # Agent orchestration
│   └── agent_manager.py
├── memory/             # Memory systems
│   ├── session_memory.py
│   └── long_term_memory.py
├── ui/                 # Web interface
│   └── streamlit_ui.py
├── main.py             # CLI entry point
├── requirements.txt    # Dependencies
└── README.md           # This file
```

## Key Technologies

- **LLM:** OpenAI GPT-3.5-turbo
- **Vector Store:** FAISS (Facebook AI Similarity Search)
- **Embeddings:** Sentence Transformers
- **Git:** GitPython + GitHub API
- **Web UI:** Streamlit
- **Orchestration:** LangChain
- **Python:** 3.11+

## Capabilities

### Analysis
- ✓ Code file scanning
- ✓ Git history parsing
- ✓ Commit pattern analysis
- ✓ Library change detection
- ✓ Refactoring identification
- ✓ Author statistics
- ✓ Language distribution

### Q&A
- ✓ Semantic code search
- ✓ Question answering
- ✓ Evidence-based responses
- ✓ Commit references
- ✓ Architecture reasoning

### Reporting
- ✓ Narrative generation
- ✓ Timeline summaries
- ✓ Pattern visualizations
- ✓ Hotspot identification
- ✓ Contributor tracking

## Example Questions

```
"Why do we use FastAPI?"
"What are the main architectural changes?"
"Who built the authentication system?"
"Why did we switch from X to Y?"
"What was the biggest refactoring effort?"
"Which files change the most?"
"What are the common commit patterns?"
```

## Limitations & Future Work

### Current Limitations
- Analysis based on commit messages (quality depends on commit message quality)
- LLM responses require OpenAI API key (optional, has fallback)
- Limited to public GitHub repositories for remote analysis

### Future Enhancements
- [ ] Code diff analysis for commit details
- [ ] Performance metrics over time
- [ ] Team collaboration patterns
- [ ] Automated documentation generation
- [ ] Multi-language support
- [ ] IDE plugins (VS Code, PyCharm)
- [ ] Self-hosted LLM option
- [ ] Batch analysis of multiple repos

## Troubleshooting

### "No commits found"
Ensure the repository has git history. Check:
```bash
git log --oneline | head -5
```

### "ModuleNotFoundError"
Install dependencies:
```bash
pip install -r requirements.txt
```

### "Streamlit stuck loading"
Check for errors:
```bash
streamlit run ui/streamlit_ui.py --logger.level=error
```

### "OpenAI API errors"
Set API key:
```bash
export OPENAI_API_KEY="sk-..."
```

## Contributing

Contributions welcome! Areas for enhancement:
- Better commit message parsing
- Advanced code pattern detection
- Performance optimizations
- UI/UX improvements
- Documentation

## License

MIT License - See LICENSE file for details

## Author

Built for Capstone Hackathon

## Support

- GitHub Issues: [Report bugs]
- Discussions: [Ask questions]
- Documentation: See PROJECT_IMPLEMENTATION.md

---

## Quick Links

- [Problem Implementation Details](PROJECT_IMPLEMENTATION.md)
- [Installation Guide](#installation)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)

## Summary

Codebase Archaeologist transforms legacy code from intimidating to understandable by:

1. 🔍 **Excavating** code and history
2. 📜 **Studying** patterns and changes
3. 🎭 **Narrating** the story behind the code

New developers can onboard faster. Experienced developers can make better decisions. Everyone wins.