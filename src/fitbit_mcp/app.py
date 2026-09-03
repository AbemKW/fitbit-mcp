"""Shared MCPServer instance — imported by every tools/*.py module to register
tools, and by server.py to run the server. Keeping this in its own module
avoids a circular import between server.py and tools/*.py.
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("fitbit-mcp")
