"""
Medium — Publishing API
https://github.com/Medium/medium-api-docs

Publishes to the user's personal profile (best for independent developer
branding and maximum SEO juice — no publication gatekeeping).

Secret: MEDIUM_TOKEN (self-issued integration token from medium.com/me/settings)
"""

import os
import requests
from platforms.base import BasePlatform

BASE = "https://api.medium.com/v1"


def _get_user_id(token: str) -> str | None:
    """Fetch the authenticated user's Medium ID."""
    try:
        resp = requests.get(
            f"{BASE}/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.ok:
            return resp.json().get("data", {}).get("id")
    except Exception as e:
        print(f"  ❌ Medium: failed to fetch user ID — {e}")
    return None


def _category_to_tags(category: str) -> list[str]:
    """Map category to Medium tags (max 5)."""
    cat = (category or "").strip().lower()
    mapping = {
        "ai":                   ["artificial-intelligence", "machine-learning", "technology", "programming", "ai"],
        "artificial intelligence": ["artificial-intelligence", "machine-learning", "deep-learning", "technology", "ai"],
        "machine learning":     ["machine-learning", "artificial-intelligence", "data-science", "python", "technology"],
        "llm":                  ["artificial-intelligence", "machine-learning", "large-language-models", "programming", "technology"],
        "cybersecurity":        ["cybersecurity", "security", "programming", "technology", "hacking"],
        "technology":           ["technology", "programming", "software-development", "ai", "web-development"],
        "programming":          ["programming", "software-development", "web-development", "python", "javascript"],
        "open source":          ["open-source", "programming", "github", "software-development", "technology"],
        "review":               ["technology", "artificial-intelligence", "software-development", "review", "programming"],
    }
    for key, tags in mapping.items():
        if key in cat or cat in key:
            return tags[:5]
    return ["technology", "artificial-intelligence", "programming", "software-development", "ai"]


class MediumPlatform(BasePlatform):
    name = "Medium"

    def is_configured(self) -> bool:
        return bool(os.environ.get("MEDIUM_TOKEN"))

    def publish(self, title, body_md, category, canonical_url, image_url=None):
        token = os.environ["MEDIUM_TOKEN"]

        try:
            user_id = _get_user_id(token)
            if not user_id:
                print(f"  ❌ {self.name}: could not resolve user ID")
                return None

            tags = _category_to_tags(category)

            # Prepend hero image to markdown body if available
            full_body = body_md
            if image_url:
                full_body = f"![{title}]({image_url})\n\n{body_md}"

            payload = {
                "title": title,
                "contentFormat": "markdown",
                "content": full_body,
                "canonicalUrl": canonical_url,
                "tags": tags,
                "publishStatus": "public",
            }

            resp = requests.post(
                f"{BASE}/users/{user_id}/posts",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )

            if resp.status_code in (200, 201):
                url = resp.json().get("data", {}).get("url", "")
                print(f"  ✅ {self.name}: published → {url}")
                return url
            else:
                print(f"  ❌ {self.name}: {resp.status_code} — {resp.text[:200]}")
                return None

        except Exception as e:
            print(f"  ❌ {self.name}: exception — {e}")
            return None
