#!/usr/bin/env python3
"""
Article Syndication Orchestrator (feed-driven)
==============================================
Reads the PUBLIC XeL Studio articles feed, compares it with the ledger
committed in this repo, and for every article not handled yet:

  1. Discovery backstop (credential-free): IndexNow + WebSub pings.
     The website already fires these right after publishing; this
     catches any that were missed.
  2. Link sharing on every configured platform (platforms/), always
     linking back to the canonical XeL Studio URL.

Only successes are written to the ledger, so anything that failed is
retried automatically on the next run (dispatch or the scheduled backstop).

Design rules:
  - No Supabase access and no secrets needed for steps 1–2 today.
  - First run (no ledger yet) seeds the ledger with every existing article
    WITHOUT pinging or sharing, so old articles are never mass-posted.
  - Exit code 1 when the feed can't be read or any attempted step failed,
    so failures show up red in GitHub Actions instead of a silent green.

Env:
  FEED_URL   override the feed (default: production articles RSS)
  DRY_RUN    "true" → log what would happen, change nothing
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from platforms import get_configured_platforms
from platforms.base import FeedItem

# ─── Config ──────────────────────────────────────────────
SITE_URL = "https://xel-studio.vercel.app"
SITE_HOST = "xel-studio.vercel.app"
FEED_URL = os.environ.get("FEED_URL") or f"{SITE_URL}/articles/feed.xml"
FEED_URLS_FOR_WEBSUB = [f"{SITE_URL}/articles/feed.xml", f"{SITE_URL}/articles/atom.xml"]
WEBSUB_HUB = "https://pubsubhubbub.appspot.com/"
# Public by design: the key file is served at SITE_URL/<key>.txt
INDEXNOW_KEY = "d942c55b41224d45a963b655513ab0a9"
LEDGER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "syndication", "ledger.json")
DRY_RUN = os.environ.get("DRY_RUN", "").strip().lower() == "true"
USER_AGENT = "XeL-Studio-Syndication/2.0 (+https://github.com/SandeepAi369/deepAI-Articles)"

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "media": "http://search.yahoo.com/mrss/",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def http(url: str, data: bytes | None = None, headers: dict | None = None, timeout: int = 30) -> tuple[int, bytes]:
    """Minimal stdlib HTTP helper. Returns (status, body); status 0 on network error."""
    req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # network / TLS / timeout
        print(f"  ⚠️  {url}: {e}")
        return 0, b""


# ─── Feed ────────────────────────────────────────────────
def fetch_feed() -> list[FeedItem]:
    status, body = http(FEED_URL)
    if status != 200:
        raise RuntimeError(f"feed returned HTTP {status}")
    root = ET.fromstring(body)
    items = []
    for it in root.iter("item"):
        url = (it.findtext("link") or it.findtext("guid") or "").strip()
        if not url.startswith(f"{SITE_URL}/articles/"):
            continue
        media = it.find("media:content", NS)
        items.append(FeedItem(
            url=url,
            title=(it.findtext("title") or "Untitled").strip(),
            summary=(it.findtext("description") or "").strip(),
            published=(it.findtext("pubDate") or "").strip(),
            category=(it.findtext("category") or "").strip(),
            image_url=media.get("url", "") if media is not None else "",
        ))
    if not items:
        raise RuntimeError("feed parsed but contained no article items")
    return items


# ─── Ledger ──────────────────────────────────────────────
def load_ledger() -> dict | None:
    if not os.path.exists(LEDGER_PATH):
        return None
    with open(LEDGER_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_ledger(ledger: dict) -> None:
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    ledger["articles"] = dict(sorted(ledger["articles"].items()))
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ─── Discovery pings (credential-free) ───────────────────
def ping_indexnow(urls: list[str]) -> bool:
    payload = {
        "host": SITE_HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
        "urlList": urls + FEED_URLS_FOR_WEBSUB + [f"{SITE_URL}/articles", f"{SITE_URL}/sitemap.xml"],
    }
    status, body = http(
        "https://api.indexnow.org/IndexNow",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    ok = status in (200, 202)
    print(f"  {'✅' if ok else '❌'} IndexNow: HTTP {status} for {len(payload['urlList'])} URL(s)"
          + ("" if ok else f" — {body[:200]!r}"))
    return ok


def ping_websub() -> bool:
    all_ok = True
    for feed in FEED_URLS_FOR_WEBSUB:
        data = urllib.parse.urlencode({"hub.mode": "publish", "hub.url": feed}).encode()
        status, body = http(WEBSUB_HUB, data=data,
                            headers={"Content-Type": "application/x-www-form-urlencoded"})
        ok = 200 <= status < 300
        all_ok &= ok
        print(f"  {'✅' if ok else '❌'} WebSub publish {feed}: HTTP {status}"
              + ("" if ok else f" — {body[:200]!r}"))
    return all_ok


# ─── Summary ─────────────────────────────────────────────
def write_summary(lines: list[str]) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


def main() -> int:
    print(f"\n📡 Feed-driven syndication {'(DRY RUN) ' if DRY_RUN else ''}— {FEED_URL}\n")
    summary = ["## 📡 Article syndication" + (" (dry run)" if DRY_RUN else ""), "",
               f"Feed: {FEED_URL}", ""]

    try:
        items = fetch_feed()
    except Exception as e:
        print(f"❌ Could not read the articles feed: {e}")
        write_summary(summary + [f"❌ Could not read the articles feed: `{e}`"])
        return 1
    print(f"Feed has {len(items)} article(s).")

    ledger = load_ledger()
    if ledger is None:
        # First run: record what already exists, post nothing.
        ledger = {"version": 1, "articles": {}}
        for it in items:
            ledger["articles"][it.url] = {"title": it.title, "first_seen": now_iso(), "seeded": True}
        print(f"🌱 No ledger yet — seeded {len(items)} existing article(s); nothing pinged or shared.")
        if not DRY_RUN:
            save_ledger(ledger)
        write_summary(summary + [f"🌱 Seeded ledger with {len(items)} existing article(s). Nothing was posted."])
        return 0

    entries = ledger["articles"]
    for it in items:
        entries.setdefault(it.url, {"title": it.title, "first_seen": now_iso()})

    def pending(step: str) -> list[FeedItem]:
        return [it for it in reversed(items)  # oldest first
                if not entries[it.url].get("seeded") and step not in entries[it.url].get("done", {})]

    failures = 0
    rows = []

    # 1. Discovery backstop
    for step, run in (("indexnow", lambda todo: ping_indexnow([t.url for t in todo])),
                      ("websub", lambda todo: ping_websub())):
        todo = pending(step)
        if not todo:
            continue
        print(f"\n{step}: {len(todo)} new article(s)")
        if DRY_RUN:
            rows += [f"| {t.title} | {step} | would ping |" for t in todo]
            continue
        ok = run(todo)
        for t in todo:
            if ok:
                entries[t.url].setdefault("done", {})[step] = now_iso()
            rows.append(f"| {t.title} | {step} | {'✅' if ok else '❌ retry next run'} |")
        failures += 0 if ok else 1

    # 2. Link sharing on configured platforms
    print("\nPlatforms:")
    platforms = get_configured_platforms()
    if not platforms:
        print("  (none configured — add a platform module + its GitHub secrets to enable sharing)")
    for p in platforms:
        step = f"share:{p.name}"
        for t in pending(step):
            if DRY_RUN:
                rows.append(f"| {t.title} | {p.name} | would share |")
                continue
            post_url = p.share(t)
            if post_url:
                entries[t.url].setdefault("done", {})[step] = now_iso()
                entries[t.url].setdefault("shares", {})[p.name] = post_url
            else:
                failures += 1
            rows.append(f"| {t.title} | {p.name} | {post_url or '❌ retry next run'} |")

    if not DRY_RUN:
        save_ledger(ledger)

    if rows:
        summary += ["| Article | Step | Result |", "|---|---|---|", *rows]
    else:
        summary.append("✅ Nothing new — every article in the feed is already handled.")
    summary += ["", f"Platforms configured: {', '.join(p.name for p in platforms) or 'none (discovery pings only)'}"]
    write_summary(summary)

    print(f"\n{'❌' if failures else '✅'} Done — {failures} failed step(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
