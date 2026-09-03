from __future__ import annotations

from .. import client
from ..app import mcp


@mcp.tool()
def get_profile() -> dict:
    """Get the Google Health profile for the connected account."""
    return client.get_profile()


@mcp.tool()
def list_paired_devices() -> dict:
    """List devices paired to the Google Health account, e.g. the Fitbit Air.

    Useful to confirm the tracker is actually connected and syncing.
    """
    return client.list_paired_devices()
