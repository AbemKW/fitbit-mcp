"""Shared exception types."""

from __future__ import annotations


class FitbitMcpError(Exception):
    """Base error for fitbit-mcp."""


class NotAuthorizedError(FitbitMcpError):
    """No stored Google Health credentials — run authorize.py first."""


class GoogleHealthApiError(FitbitMcpError):
    """The Google Health API returned an error response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"Google Health API error {status_code}: {message}")
