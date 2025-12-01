"""Agents module with lazy imports."""

def __getattr__(name):
    """Lazy import on first access."""
    if name == "ExcavatorAgent":
        from .excavator import ExcavatorAgent
        return ExcavatorAgent
    elif name == "HistorianAgent":
        from .historian import HistorianAgent
        return HistorianAgent
    elif name == "NarratorAgent":
        from .narrator import NarratorAgent
        return NarratorAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
