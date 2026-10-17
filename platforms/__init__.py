"""
Platform Registry — deepAI-Articles Syndication Pipeline

Plug-and-play: to add a link-sharing platform (e.g. Bluesky, Mastodon,
Telegram), create a module in this package implementing BasePlatform,
then add an instance to ALL_PLATFORMS. Unconfigured platforms (no
GitHub secrets) are skipped, so a new module is safe to merge before
its tokens exist.

No platforms are registered yet: the pipeline currently runs only the
credential-free discovery pings (IndexNow, WebSub) in syndicate.py.
"""

from platforms.base import BasePlatform

ALL_PLATFORMS: list[BasePlatform] = []


def get_configured_platforms() -> list[BasePlatform]:
    """Return only platforms whose required env vars are set."""
    configured = []
    for p in ALL_PLATFORMS:
        if p.is_configured():
            configured.append(p)
        else:
            print(f"  ⏭️  {p.name}: skipped (not configured)")
    return configured
