"""Importing this package registers every tool module against the shared
FastMCP instance in app.py. server.py imports this package for that
side effect before calling mcp.run().
"""

from . import activity, heart, profile, raw, sleep, vitals  # noqa: F401
