"""CSAF VEX library for generating, parsing and validating CSAF VEX files."""

try:
    from importlib.metadata import version

    __version__ = version("csaf-vex")
except Exception:
    # Fallback for development (running from source without installation)
    __version__ = "unknown"
