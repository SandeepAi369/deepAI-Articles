"""
Platform Registry — deepAI-Articles Syndication Pipeline

Plug-and-play architecture: to add a new platform, create a module
in this package implementing BasePlatform, then register it here.
"""

from platforms.devto import DevToPlatform
from platforms.medium import MediumPlatform
from platforms.reddit import RedditPlatform
from platforms.hashnode import HashnodePlatform

ALL_PLATFORMS = [
    DevToPlatform(),
    MediumPlatform(),
    RedditPlatform(),
    HashnodePlatform(),
]

def get_configured_platforms():
    """Return only platforms whose required env vars are set."""
    configured = []
    for p in ALL_PLATFORMS:
        if p.is_configured():
            configured.append(p)
        else:
            print(f"  ⏭️  {p.name}: skipped (not configured)")
    return configured
