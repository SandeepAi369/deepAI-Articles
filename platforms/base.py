"""
Abstract base class for all syndication platforms.

Every platform module MUST implement:
  - name (str)
  - is_configured() -> bool
  - publish(title, body_md, category, canonical_url, image_url) -> str | None
"""

from abc import ABC, abstractmethod


class BasePlatform(ABC):
    """Contract for a syndication target."""

    name: str = "unknown"

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if all required env vars / credentials exist."""
        ...

    @abstractmethod
    def publish(
        self,
        title: str,
        body_md: str,
        category: str,
        canonical_url: str,
        image_url: str | None = None,
    ) -> str | None:
        """
        Publish the article to this platform.

        Returns the published URL on success, or None on failure.
        Implementations MUST handle their own errors (try/except)
        and print diagnostic messages — a failure here must never
        crash the orchestrator or block other platforms.
        """
        ...
