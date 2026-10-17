"""
Abstract base class for all link-sharing platforms.

Platforms share a link back to the canonical XeL Studio article
(they never re-host the full article). Every platform module MUST implement:
  - name (str)
  - is_configured() -> bool       (True only when its GitHub secrets exist)
  - share(item) -> str | None     (returns the post URL, or None on failure)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class FeedItem:
    """One article from the public XeL Studio articles feed."""

    url: str          # canonical https://xel-studio.vercel.app/articles/<id>
    title: str
    summary: str
    published: str    # RFC 822 date string from the feed
    category: str = ""
    image_url: str = ""


class BasePlatform(ABC):
    """Contract for a link-sharing target."""

    name: str = "unknown"

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if all required env vars / credentials exist."""
        ...

    @abstractmethod
    def share(self, item: FeedItem) -> str | None:
        """
        Share the article link on this platform.

        Returns the post URL on success, or None on failure.
        Implementations MUST handle their own errors and print a
        diagnostic — a failure must never crash the orchestrator.
        The orchestrator retries failed shares on the next run.
        """
        ...
