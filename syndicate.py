#!/usr/bin/env python3
"""
Article Syndication Orchestrator
=================================
Event-driven: receives a single article_id from GitHub Actions,
fetches it from Supabase, and publishes to all configured platforms.

No state files, no cron loops. Pure 1-to-1 event processing.

Duplicate Prevention (stateless):
  - dev.to:  canonical_url check against existing published articles
  - Medium:  canonical_url set (Medium dedupes display in search)
  - Reddit:  resubmit=False flag prevents duplicate URL submissions
  - Hashnode: native GitHub sync (no API call)

Usage:
  python syndicate.py                  # reads ARTICLE_ID from env
  python syndicate.py <article_id>     # CLI argument
"""

import os
import re
import sys
import requests

# ─── Config ──────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SITE_URL = "https://xel-studio.vercel.app"


def fetch_article(article_id: str) -> dict | None:
    """Fetch a single article from Supabase by ID."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ SUPABASE_URL or SUPABASE_ANON_KEY not set.")
        return None

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }
    url = f"{SUPABASE_URL}/rest/v1/articles"
    params = {
        "select": "id,title,content,image,date,category",
        "id": f"eq.{article_id}",
        "limit": "1",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data and len(data) > 0:
            return data[0]
        print(f"⚠️  Article '{article_id}' not found in Supabase.")
        return None
    except Exception as e:
        print(f"❌ Failed to fetch article: {e}")
        return None


def fix_cloudinary_url(url: str) -> str:
    """Append .jpg to Cloudinary URLs if they lack a file extension."""
    if not url:
        return url
    if re.search(r'\.(jpg|jpeg|png|webp|gif|avif)(\?.*)?$', url, re.IGNORECASE):
        return url
    if "cloudinary.com" in url:
        return url.split("?")[0] + ".jpg"
    return url


def build_canonical_url(article_id: str) -> str:
    """Build the canonical XeL Studio article URL."""
    return f"{SITE_URL}/articles/{article_id}"


def syndicate(article_id: str):
    """Main entry: fetch article, publish to all configured platforms."""
    print(f"\n{'='*60}")
    print(f"📡 Article Syndication Pipeline")
    print(f"   Article ID: {article_id}")
    print(f"{'='*60}\n")

    # 1. Fetch article from Supabase
    article = fetch_article(article_id)
    if not article:
        print("\n💀 Syndication aborted — article not found.")
        sys.exit(1)

    title = article.get("title", "Untitled").strip()
    content = article.get("content", "")
    category = article.get("category", "")
    image_url = fix_cloudinary_url(article.get("image", ""))
    canonical_url = build_canonical_url(article_id)

    print(f"📰 Title:     {title}")
    print(f"📂 Category:  {category or 'N/A'}")
    print(f"🔗 Canonical: {canonical_url}")
    print(f"🖼️  Image:     {image_url or 'none'}")
    print(f"📝 Content:   {len(content)} chars")
    print()

    # 2. Build markdown body (same format sync.py uses)
    body_md = f"# {title}\n\n{content}"

    # 3. Load configured platforms
    from platforms import get_configured_platforms
    platforms = get_configured_platforms()

    if not platforms:
        print("\n⚠️  No platforms configured. Add API keys to GitHub Secrets.")
        return

    print(f"\n🚀 Publishing to {len(platforms)} platform(s)...\n")

    # 4. Publish to each platform
    results = {}
    for platform in platforms:
        print(f"  ── {platform.name} ──")
        try:
            url = platform.publish(
                title=title,
                body_md=body_md,
                category=category,
                canonical_url=canonical_url,
                image_url=image_url,
            )
            results[platform.name] = url or "failed"
        except Exception as e:
            print(f"  ❌ {platform.name}: unhandled exception — {e}")
            results[platform.name] = "error"
        print()

    # 5. Summary
    print(f"{'='*60}")
    print(f"📊 Syndication Results")
    print(f"{'='*60}")
    for name, url in results.items():
        status = "✅" if url and url not in ("failed", "error") else "❌"
        print(f"  {status} {name}: {url}")
    print()


if __name__ == "__main__":
    # Accept article_id from CLI arg or environment variable
    aid = None
    if len(sys.argv) > 1:
        aid = sys.argv[1]
    else:
        aid = os.environ.get("ARTICLE_ID", "")

    if not aid:
        print("❌ No article ID provided.")
        print("   Usage: python syndicate.py <article_id>")
        print("   Or set ARTICLE_ID environment variable.")
        sys.exit(1)

    syndicate(aid)
