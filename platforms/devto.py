"""
dev.to — REST API publisher
https://developers.forem.com/api/v1

Secret: DEVTO_API_KEY

Duplicate prevention: checks canonical_url against existing published articles
before posting. If the canonical URL already exists, skips publishing.
"""

import os
import requests
from platforms.base import BasePlatform

# ─── Intelligent Tag Mapping ─────────────────────────────────────
# dev.to allows max 4 tags per article.

CATEGORY_MAP = {
    "ai":                   ["ai", "machinelearning", "programming", "technology"],
    "artificial intelligence": ["ai", "machinelearning", "deeplearning", "technology"],
    "machine learning":     ["machinelearning", "ai", "datascience", "python"],
    "ml":                   ["machinelearning", "ai", "datascience", "python"],
    "llm":                  ["ai", "llm", "machinelearning", "programming"],
    "cybersecurity":        ["security", "cybersecurity", "programming", "technology"],
    "cyber security":       ["security", "cybersecurity", "programming", "technology"],
    "security":             ["security", "cybersecurity", "programming", "technology"],
    "technology":           ["technology", "programming", "webdev", "ai"],
    "tech":                 ["technology", "programming", "webdev", "ai"],
    "programming":          ["programming", "webdev", "javascript", "python"],
    "web development":      ["webdev", "javascript", "programming", "react"],
    "web":                  ["webdev", "javascript", "programming", "react"],
    "review":               ["ai", "technology", "programming", "productivity"],
    "open source":          ["opensource", "programming", "github", "technology"],
    "agentic ai":           ["ai", "machinelearning", "programming", "productivity"],
}

# Content keyword fallback — scans body for these keywords
KEYWORD_TAGS = {
    "python":       "python",
    "javascript":   "javascript",
    "react":        "react",
    "next.js":      "nextjs",
    "langchain":    "ai",
    "langgraph":    "ai",
    "openai":       "ai",
    "gpt":          "ai",
    "claude":       "ai",
    "gemini":       "ai",
    "llama":        "ai",
    "docker":       "docker",
    "kubernetes":   "devops",
    "rust":         "rust",
    "supabase":     "webdev",
    "firebase":     "webdev",
}

DEFAULT_TAGS = ["ai", "technology", "programming", "machinelearning"]


def auto_tags(category: str, body: str) -> list[str]:
    """Generate up to 4 optimal dev.to tags from category + content."""
    cat = (category or "").strip().lower()

    # 1. Try exact category match
    if cat in CATEGORY_MAP:
        return CATEGORY_MAP[cat][:4]

    # 2. Try partial category match
    for key, tags in CATEGORY_MAP.items():
        if key in cat or cat in key:
            return tags[:4]

    # 3. Content-based keyword scan
    body_lower = body.lower()
    found = []
    for keyword, tag in KEYWORD_TAGS.items():
        if keyword in body_lower and tag not in found:
            found.append(tag)
        if len(found) >= 4:
            break

    if found:
        return found[:4]

    return DEFAULT_TAGS


class DevToPlatform(BasePlatform):
    name = "dev.to"

    def is_configured(self) -> bool:
        return bool(os.environ.get("DEVTO_API_KEY"))

    def publish(self, title, body_md, category, canonical_url, image_url=None):
        api_key = os.environ["DEVTO_API_KEY"]
        base = "https://dev.to/api"

        try:
            # ── Duplicate check: search own articles by canonical_url ──
            check = requests.get(
                f"{base}/articles/me/published",
                headers={"api-key": api_key},
                params={"per_page": 1000},
                timeout=15,
            )
            if check.ok:
                for existing in check.json():
                    if existing.get("canonical_url") == canonical_url:
                        url = existing.get("url", "")
                        print(f"  ✅ {self.name}: already published → {url}")
                        return url

            # ── Build payload ──
            tags = auto_tags(category, body_md)
            payload = {
                "article": {
                    "title": title,
                    "body_markdown": body_md,
                    "published": True,
                    "canonical_url": canonical_url,
                    "tags": tags,
                }
            }
            if image_url:
                payload["article"]["main_image"] = image_url

            resp = requests.post(
                f"{base}/articles",
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )

            if resp.status_code in (200, 201):
                url = resp.json().get("url", "")
                print(f"  ✅ {self.name}: published → {url}")
                return url
            else:
                print(f"  ❌ {self.name}: {resp.status_code} — {resp.text[:200]}")
                return None

        except Exception as e:
            print(f"  ❌ {self.name}: exception — {e}")
            return None
