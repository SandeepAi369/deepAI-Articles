#!/usr/bin/env python3
"""
Supabase → GitHub Articles Sync
================================
Fetches articles from Supabase and creates/updates Markdown files
in this repository. READ-ONLY access to Supabase.
"""

import os
import re
import json
import requests

# ─── Config ──────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
OUTPUT_DIR = "articles"

# ─── Helpers ─────────────────────────────────────────────

def to_kebab(title: str) -> str:
    """Convert title to kebab-case filename."""
    title = title.lower().strip()
    title = re.sub(r"[^\w\s-]", "", title)
    title = re.sub(r"[\s_]+", "-", title)
    title = re.sub(r"-+", "-", title)
    return title[:100]  # max 100 chars


def fetch_articles() -> list:
    """Fetch all articles from Supabase (READ-ONLY SELECT)."""
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }
    url = f"{SUPABASE_URL}/rest/v1/articles"
    params = {
        "select": "id,title,content,image,date,category",
        "order": "created_at.desc",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    articles = resp.json()
    print(f"✅ Fetched {len(articles)} articles from Supabase.")
    return articles


def build_markdown(article: dict) -> str:
    """Build a Markdown file from a single article."""
    title = article.get("title", "Untitled")
    content = article.get("content", "")
    image_url = article.get("image", "")
    date = article.get("date", "")
    category = article.get("category", "")

    lines = []

    # YAML front-matter
    lines.append("---")
    lines.append(f"title: \"{title}\"")
    if date:
        lines.append(f"date: \"{date[:10]}\"")
    if category:
        lines.append(f"category: \"{category}\"")
    lines.append("---")
    lines.append("")

    # Cloudinary image at the top
    if image_url:
        lines.append(f"![{title}]({image_url})")
        lines.append("")

    lines.append(f"# {title}")
    lines.append("")
    lines.append(content or "")

    return "\n".join(lines)


def sync():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    articles = fetch_articles()
    if not articles:
        print("⚠️  No articles found. Nothing to sync.")
        return

    written = 0
    for article in articles:
        title = article.get("title", "").strip()
        if not title:
            print(f"  ⚠️  Skipping article with no title (id={article.get('id')})")
            continue

        filename = to_kebab(title) + ".md"
        filepath = os.path.join(OUTPUT_DIR, filename)
        md_content = build_markdown(article)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"  📝 Written: {filepath}")
        written += 1

    print(f"\n✅ Sync complete — {written} articles written to /{OUTPUT_DIR}/")


if __name__ == "__main__":
    sync()
