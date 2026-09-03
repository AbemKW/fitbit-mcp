"""stdio MCP server entry point.

Run with: uv run python -m fitbit_mcp.server
(or configure as a stdio MCP server: `uv run --directory <repo> python -m fitbit_mcp.server`)

Requires credentials already stored via `uv run python -m fitbit_mcp.authorize`.
This module never triggers the OAuth browser flow itself.
"""

from __future__ import annotations

from .app import mcp
from . import tools  # noqa: F401  (import registers all @mcp.tool() functions)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
