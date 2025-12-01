"""Tools module with lazy imports to avoid loading heavy dependencies early."""

def __getattr__(name):
    """Lazy import on first access."""
    if name == "GitTool":
        from .git_tool import GitTool
        return GitTool
    elif name == "FileTool":
        from .file_tool import FileTool
        return FileTool
    elif name == "CodeExecutor":
        from .code_execution import CodeExecutor
        return CodeExecutor
    elif name == "RAGTool":
        from .rag_tool import RAGTool
        return RAGTool
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
