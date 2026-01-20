"""CSAF library for generating, parsing and validating CSAF documents (VEX and Advisory)."""

try:
    from importlib.metadata import version

    __version__ = version("csaf-lib")
except Exception:
    # Fallback for development (running from source without installation)
    __version__ = "unknown"
