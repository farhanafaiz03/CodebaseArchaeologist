# Quick Start Guide - Codebase Archaeologist

## 🚀 Get Running in 2 Minutes

### Option 1: Web Dashboard (Recommended)
```bash
cd e:\CodebaseArchaeologist
streamlit run ui/streamlit_ui.py
```
Then open: **http://localhost:8501**

### Option 2: Command Line
```bash
cd e:\CodebaseArchaeologist
python main.py --repo ./examples/sample_repo
```

## 📊 Try These Examples

### Example 1: Analyze Flask (Public GitHub)
1. Open http://localhost:8501
2. Enter: `https://github.com/pallets/flask.git`
3. Click "Run Analysis"
4. Ask: "Why does Flask use Werkzeug?"

### Example 2: Analyze Any GitHub Repo
1. Enter any public GitHub repo URL: `https://github.com/user/repo.git`
2. Wait for analysis (30-60 seconds)
3. View metrics and patterns
4. Ask questions about the architecture

### Example 3: Local Repository
1. Enter a local path: `/path/to/repo`
2. Repo must have `.git` directory
3. Analysis runs faster for local repos
4. All code gets embedded for Q&A

## ❓ Example Questions to Try

```
"Why do we use this library instead of that one?"
"What were the major refactoring efforts?"
"Who are the main contributors?"
"What libraries were recently adopted?"
"How did the architecture evolve?"
"Which files change the most?"
"What are the common commit patterns?"
```

## 🎯 What You'll See

### Dashboard Shows:
- 📊 Commit statistics (count, authors, velocity)
- 📈 Commit types (features, bugs, refactors)
- 🔤 Top keywords from commit messages
- 🏗️ Major architecture changes detected
- 👥 Contributor distribution

### AI-Generated Report:
- 📜 Historical narrative of the project
- 🔄 Library changes and tech shifts
- ♻️ Refactoring events
- 🎯 Project evolution story

### Q&A System:
- 🤖 Ask ANY question about the code
- 📚 Get answers grounded in actual history
- 🔗 Commit references for evidence
- ⚡ Real-time responses

## 🔧 System Requirements

- Python 3.11+
- 2GB RAM minimum
- Virtual environment (venv) - Already set up
- Dependencies installed (see requirements.txt)

## 📁 Project Structure

```
CodebaseArchaeologist/
├── ui/streamlit_ui.py         # Main web interface
├── main.py                     # CLI entry point
├── agents/                     # AI agents
│   ├── excavator.py           # Code scanner
│   ├── historian.py           # Pattern analyzer
│   ├── narrator.py            # Report generator
│   └── remote_excavator.py    # GitHub API crawler
├── tools/                      # Utilities
│   ├── rag_tool.py            # Vector store (FAISS)
│   ├── git_tool.py            # Git interface
│   ├── remote_git_tool.py     # GitHub API
│   └── file_tool.py           # File operations
└── requirements.txt           # Dependencies
```

## ⚙️ Configuration

### Enable Advanced Features (Optional)
```bash
# Set OpenAI API key for better AI responses
export OPENAI_API_KEY="sk-your-key-here"
```

Without API key, system uses stub responses (still works!).

## 🐛 Troubleshooting

### Streamlit won't start
```bash
# Kill existing process
taskkill /F /IM streamlit.exe

# Restart
streamlit run ui/streamlit_ui.py
```

### "No commits found"
```bash
# Check if repo has git history
git log --oneline | head -5
```

### Missing dependencies
```bash
# Reinstall requirements
pip install -r requirements.txt
```

## 📊 System Flow

```
┌─ Local Repo ───────────────────────────────────┐
│                                                 │
│ 1. Excavator scans code + git history          │
│ 2. Historian analyzes commit patterns          │
│ 3. Narrator generates report                   │
│ 4. Q&A system ready                            │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┴───────────┐
        │                      │
        ▼                      ▼
  ┌─────────────┐      ┌─────────────┐
  │   Report    │      │   Q&A Chat  │
  │   View      │      │   System    │
  └─────────────┘      └─────────────┘
```

## 🎓 What You're Seeing

### The Three Agents in Action

**1. EXCAVATOR** 🔍
- Reads every source file
- Extracts 100+ commits
- Embeds code for searching
- Finds "hotspots" (most-changed files)

**2. HISTORIAN** 📜
- Classifies each commit (feature/bug/refactor)
- Detects library changes
- Finds refactoring efforts
- Generates AI insights

**3. NARRATOR** 🎭
- Creates readable narrative
- Answers developer questions
- Grounds answers in actual code
- Provides commit references

## 💡 Tips

1. **Start Small**: Try Flask first (well-documented project)
2. **Read the Narrative**: Understand project evolution
3. **Ask Questions**: The more specific, the better
4. **Check References**: Commit hashes validate answers
5. **Explore Patterns**: Learn project's development style

## 🎯 Success Indicators

Your system is working correctly when:
- ✓ Dashboard loads in <5 seconds
- ✓ Metrics show actual repository data
- ✓ Report text makes sense
- ✓ Q&A responses are contextual
- ✓ Commit hashes are referenced in answers

## 🚀 Ready to Demo?

1. Start the app: `streamlit run ui/streamlit_ui.py`
2. Open: http://localhost:8501
3. Analyze: https://github.com/pallets/flask.git
4. Ask: "Why do we use Jinja2?"
5. Get: Evidence-based answer with commit reference

That's it! You're now using an AI-powered codebase archaeology system.

---

## For Hackathon Judges

### Problem Solved ✓
- Developers understand legacy code faster
- Architectural decisions are explained
- Onboarding time reduced
- Risk of misunderstandings eliminated

### Technical Approach ✓
- Multi-agent AI system (Excavator → Historian → Narrator)
- RAG for grounded answers (FAISS + embeddings)
- Git history mining for pattern detection
- LLM integration for natural language explanations

### Innovation ✓
- No code cloning (GitHub API)
- Semantic code search (vector embeddings)
- Automated pattern detection
- Interactive Q&A interface

### Production Ready ✓
- 90 dependencies managed
- Error handling + fallbacks
- Works with/without OpenAI key
- Scales to large repos
- Beautiful web UI

---

## Questions?

See:
- PROJECT_IMPLEMENTATION.md - Full requirements coverage
- TESTING_AND_VERIFICATION.md - Technical details
- README.md - Complete documentation

**Let's go! Start with: `streamlit run ui/streamlit_ui.py`**
