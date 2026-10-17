#!/usr/bin/env python3
"""
AI Readability Check
====================
Runs from GitHub's datacenter IPs (where AI fetchers live) and verifies
that every XeL Studio article is readable by AI agents and scrapers
WITHOUT JavaScript:

  - each AI user agent gets HTTP 200 (no firewall block / challenge)
  - the <article> text is in the initial HTML and not inside a hidden element
  - its word count roughly matches the article's Markdown copy
  - per-article OpenGraph tags and BlogPosting JSON-LD are present
  - `Accept: text/markdown` returns Markdown
  - a non-existent article returns a real 404

Exit code 1 on any failure, with a results table in the job summary.
Stdlib only; reads only public URLs.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

SITE_URL = "https://xel-studio.vercel.app"
FEED_URL = f"{SITE_URL}/articles/feed.xml"
MAX_ARTICLES = int(os.environ.get("MAX_ARTICLES", "5"))  # newest N articles

AGENTS = {
    "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.2; +https://openai.com/gptbot",
    "ChatGPT-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot",
    "ClaudeBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "Claude-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-User/1.0; +Claude-User@anthropic.com)",
    "PerplexityBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    "Google-Extended": "Mozilla/5.0 (compatible; Google-Extended)",
    "CCBot": "CCBot/2.0 (https://commoncrawl.org/faq/)",
    "python-requests": "python-requests/2.32",
}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def fetch(url, ua, accept="text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, "", str(e)


class ArticleText(HTMLParser):
    """Collects text inside <article>, skipping anything under a hidden element or script/style."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, hidden)
        self.in_article = 0
        self.article_hidden = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        parent_hidden = self.stack[-1][1] if self.stack else False
        hidden = parent_hidden or "hidden" in a or a.get("aria-hidden") == "true" or tag in ("script", "style", "template")
        self.stack.append((tag, hidden))
        if tag == "article":
            self.in_article += 1
            self.article_hidden = self.article_hidden or parent_hidden or "hidden" in a

    def handle_endtag(self, tag):
        # Ignore void/self-closing and stray end tags; only close what is open.
        if tag in VOID or tag not in (t for t, _ in self.stack):
            return
        while self.stack:
            t, _ = self.stack.pop()
            if t == "article":
                self.in_article -= 1
            if t == tag:
                break

    def handle_data(self, data):
        if self.in_article and self.stack and not self.stack[-1][1]:
            self.parts.append(data)

    def words(self):
        return len(" ".join(self.parts).split())


def main():
    status, _, body = fetch(FEED_URL, AGENTS["python-requests"])
    if status != 200:
        print(f"❌ feed HTTP {status}")
        return 1
    urls = [i.findtext("link") for i in ET.fromstring(body).iter("item")][:MAX_ARTICLES]
    rows, failures = [], 0

    def record(url, check, ok, detail=""):
        nonlocal failures
        failures += 0 if ok else 1
        rows.append(f"| {url.rsplit('/', 1)[-1]} | {check} | {'✅' if ok else '❌'} {detail} |")
        print(f"{'PASS' if ok else 'FAIL'} {url} {check} {detail}")

    for url in urls:
        _, _, md = fetch(url + ".md", AGENTS["python-requests"], accept="text/markdown")
        md_words = len(re.sub(r"^>.*$", "", md, flags=re.M).split())

        for name, ua in AGENTS.items():
            st, ctype, html = fetch(url, ua)
            if st != 200 or "text/html" not in ctype:
                record(url, name, False, f"HTTP {st} {ctype}")
                continue
            p = ArticleText()
            p.feed(html)
            w = p.words()
            ok = not p.article_hidden and w >= 0.7 * md_words
            record(url, name, ok, f"{w} visible article words vs {md_words} in .md"
                   + (" (article inside hidden element)" if p.article_hidden else ""))

        # Metadata (checked once per article)
        og = dict(re.findall(r'<meta property="(og:[a-z_:]+)" content="([^"]*)"', html))
        record(url, "og:url / og:type", og.get("og:url") == url and og.get("og:type") == "article",
               f"{og.get('og:url')} {og.get('og:type')}")
        lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        has_posting = any('"BlogPosting"' in x and '"articleBody"' in x for x in lds)
        record(url, "JSON-LD BlogPosting+articleBody", has_posting)
        record(url, "alternate text/markdown link", 'type="text/markdown"' in html)
        st, ctype, _ = fetch(url, AGENTS["Claude-User"], accept="text/markdown")
        record(url, "Accept: text/markdown", st == 200 and "text/markdown" in ctype, f"HTTP {st} {ctype}")

    st, _, _ = fetch(f"{SITE_URL}/articles/0000000000000-doesnotexist", AGENTS["GPTBot"])
    record(f"{SITE_URL}/articles/0000000000000-doesnotexist", "missing article → 404", st == 404, f"HTTP {st}")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"## 🤖 AI readability check ({len(urls)} newest articles)\n\n"
                    "| Article | Check | Result |\n|---|---|---|\n" + "\n".join(rows) + "\n")
    print(f"\n{'❌' if failures else '✅'} {failures} failed check(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
