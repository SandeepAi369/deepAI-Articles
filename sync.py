#!/usr/bin/env python3
"""
Supabase → GitHub Articles Sync
================================
Fetches articles from Supabase and creates/updates Markdown files.
Also generates a root README.md gallery with working image URLs.
READ-ONLY access to Supabase.
"""

import os
import re
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
    return title[:100]


def fix_cloudinary_url(url: str) -> str:
    """
    Append .jpg to Cloudinary URLs if they don't already have
    a file extension, so GitHub can render them as images.
    """
    if not url:
        return url
    # If URL already has an image extension, return as-is
    if re.search(r'\.(jpg|jpeg|png|webp|gif|avif)(\?.*)?$', url, re.IGNORECASE):
        return url
    # For Cloudinary URLs, append .jpg
    if "cloudinary.com" in url:
        # Strip any existing query params before adding .jpg
        url_clean = url.split("?")[0]
        return url_clean + ".jpg"
    return url


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


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format."""
    if not date_str:
        return ""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return date_str[:10]


def build_markdown(article: dict) -> str:
    """Build a Markdown file from a single article."""
    title = article.get("title", "Untitled")
    content = article.get("content", "")
    image_url = fix_cloudinary_url(article.get("image", ""))
    date = article.get("date", "")
    category = article.get("category", "")

    lines = []

    # YAML front-matter
    lines.append("---")
    lines.append(f'title: "{title}"')
    if date:
        lines.append(f'date: "{date[:10]}"')
    if category:
        lines.append(f'category: "{category}"')
    lines.append("---")
    lines.append("")

    # Cloudinary image with HTML img tag (works on GitHub)
    if image_url:
        lines.append(f'<img src="{image_url}" alt="{title}" width="100%">')
        lines.append("")

    lines.append(f"# {title}")
    lines.append("")
    if date:
        lines.append(f"*{format_date(date)}*")
        lines.append("")
    lines.append(content or "")

    return "\n".join(lines)


def build_gallery_readme(articles: list, article_filenames: dict) -> str:
    """Build the root README.md as a visual article gallery."""
    lines = []

    lines.append("# 📰 deepAI Articles")
    lines.append("")
    lines.append("> Auto-synced from Supabase · Updated daily via GitHub Actions")
    lines.append("")
    lines.append(f"**{len(articles)} Articles**")
    lines.append("")
    lines.append("---")
    lines.append("")

    # HTML table — 3 columns
    COLS = 3
    lines.append("<table>")

    for i in range(0, len(articles), COLS):
        chunk = articles[i : i + COLS]
        lines.append("  <tr>")

        for art in chunk:
            title = art.get("title", "Untitled")
            image_url = fix_cloudinary_url(art.get("image", ""))
            date = format_date(art.get("date", ""))
            filename = article_filenames.get(title, "")
            link = f"articles/{filename}" if filename else "#"

            lines.append("    <td align='center' width='33%' valign='top'>")
            if image_url:
                lines.append(f"      <a href='{link}'>")
                lines.append(f"        <img src='{image_url}' alt='{title}' width='300' style='border-radius:8px;object-fit:cover;'>")
                lines.append(f"      </a>")
                lines.append(f"      <br>")
            lines.append(f"      <a href='{link}'><b>{title}</b></a>")
            if date:
                lines.append(f"      <br>")
                lines.append(f"      <sub>📅 {date}</sub>")
            lines.append("    </td>")

        # Pad incomplete rows with empty cells
        for _ in range(COLS - len(chunk)):
            lines.append("    <td></td>")

        lines.append("  </tr>")

    lines.append("</table>")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*[XeL Studio](https://xel-studio.vercel.app) | Auto-generated*")

    return "\n".join(lines)


def sync():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    articles = fetch_articles()
    if not articles:
        print("⚠️  No articles found. Nothing to sync.")
        return

    article_filenames = {}
    written = 0

    # Step 1: Write individual article .md files
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

        article_filenames[title] = filename
        print(f"  📝 Written: {filepath}")
        written += 1

    # Step 2: OVERWRITE root README.md with gallery
    readme_content = build_gallery_readme(articles, article_filenames)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"\n🎨 Gallery README.md overwritten at repo root with {written} articles.")
    print(f"✅ Sync complete — {written} articles written to /{OUTPUT_DIR}/")


if __name__ == "__main__":
    sync()
