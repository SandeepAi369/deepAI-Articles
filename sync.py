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
import textwrap
import base64
import html

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


def generate_svg_card(article, filename, cards_dir):
    """Generate a responsive SVG card embedding the Cloudinary image and text."""
    title = article.get("title", "Untitled")
    date = format_date(article.get('date', ''))
    image_url = fix_cloudinary_url(article.get("image", ""))
    
    b64_img = ""
    if image_url:
        try:
            r = requests.get(image_url, timeout=10)
            if r.status_code == 200:
                ctype = r.headers.get("Content-Type", "image/jpeg")
                b64_img = "data:" + ctype + ";base64," + base64.b64encode(r.content).decode('utf-8')
        except Exception as e:
            print(f"    ⚠️ Failed to download image for SVG: {e}")
            pass
            
    # Wrap text to ~35 characters
    lines = textwrap.wrap(title, width=35)[:2]
    title_line1 = html.escape(lines[0] if len(lines) > 0 else "Untitled")
    title_line2 = html.escape(lines[1] if len(lines) > 1 else "")
    if len(textwrap.wrap(title, width=35)) > 2:
        title_line2 = html.escape(lines[1][:-3] + "...")
        
    svg = f'''<svg width="320" height="250" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <clipPath id="img-clip">
      <path d="M10,10 a10,10 0 0 1 10,-10 h280 a10,10 0 0 1 10,10 v140 h-300 v-140 z" />
    </clipPath>
    <filter id="shadow">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-opacity="0.2"/>
    </filter>
  </defs>
  <rect width="296" height="236" x="12" y="5" fill="#1c1c1c" rx="10" filter="url(#shadow)" />
  <rect width="296" height="236" x="12" y="5" fill="#1c1c1c" rx="10" stroke="#333" stroke-width="1" />
  <image href="{b64_img}" x="12" y="5" width="296" height="150" preserveAspectRatio="xMidYMid slice" clip-path="url(#img-clip)"/>
  <text x="25" y="185" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="16" font-weight="600" fill="#ffffff">{title_line1}</text>
  <text x="25" y="207" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="16" font-weight="600" fill="#ffffff">{title_line2}</text>
  <text x="25" y="229" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="12" fill="#aaaaaa">📅 {date}</text>
</svg>'''

    card_name = filename.replace(".md", ".svg")
    filepath = os.path.join(cards_dir, card_name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)
    return card_name

def build_gallery_readme(articles: list, article_filenames: dict, cards_dir: str) -> str:
    """Build the root README.md as a visual article gallery."""
    lines = []

    lines.append("# 📰 deepAI Articles")
    lines.append("")
    lines.append("> Auto-synced from Supabase · Updated daily via GitHub Actions")
    lines.append("")
    lines.append(f"**{len(articles)} Articles**")
    lines.append("")
    lines.append("---")
    lines.append("<div align='center'>")
    lines.append("")

    for art in articles:
        title = art.get("title", "").strip() or "Untitled"
        filename = article_filenames.get(title, "")
        if not filename:
            continue
            
        link = f"articles/{filename}"
        
        # Generate SVG card
        svg_name = generate_svg_card(art, filename, cards_dir)
        svg_path = f"articles/cards/{svg_name}"
        
        # Output inline image anchor (wraps automatically on mobile!)
        lines.append(f"  <a href='{link}' style='text-decoration:none;'>")
        lines.append(f"    <img src='{svg_path}' width='320' alt='{html.escape(title)}'>")
        lines.append(f"  </a>")

    lines.append("")
    lines.append("</div>")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*[XeL Studio](https://xel-studio.vercel.app) | Auto-generated*")

    return "\n".join(lines)


def sync():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cards_dir = os.path.join(OUTPUT_DIR, "cards")
    os.makedirs(cards_dir, exist_ok=True)

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
    readme_content = build_gallery_readme(articles, article_filenames, cards_dir)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"\n🎨 Gallery README.md overwritten at repo root with {written} articles.")
    print(f"✅ Sync complete — {written} articles written to /{OUTPUT_DIR}/")


if __name__ == "__main__":
    sync()
