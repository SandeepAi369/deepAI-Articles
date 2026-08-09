"""
Reddit — OAuth2 REST API (no PRAW dependency)
https://www.reddit.com/dev/api/

Shares the published XeL Studio article link to configured subreddits.
Uses resubmit=False to prevent duplicate URL posting natively.

Secrets:
  REDDIT_CLIENT_ID
  REDDIT_CLIENT_SECRET
  REDDIT_USERNAME
  REDDIT_PASSWORD
  REDDIT_SUBREDDITS  (comma-separated, e.g. "artificial,MachineLearning,technology")

Default subreddits (optimized for AI/tech developer reach):
  r/artificial (800K+ members), r/ArtificialIntelligence (500K+ members)
"""

import os
import requests
from platforms.base import BasePlatform

DEFAULT_SUBREDDITS = "artificial,ArtificialIntelligence"
USER_AGENT = "XeL-Studio-Syndication/1.0 by /u/{}"


def _get_oauth_token(client_id, client_secret, username, password):
    """Obtain a Reddit OAuth2 bearer token via password grant."""
    resp = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=(client_id, client_secret),
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
        },
        headers={"User-Agent": USER_AGENT.format(username)},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


class RedditPlatform(BasePlatform):
    name = "Reddit"

    def is_configured(self) -> bool:
        return all([
            os.environ.get("REDDIT_CLIENT_ID"),
            os.environ.get("REDDIT_CLIENT_SECRET"),
            os.environ.get("REDDIT_USERNAME"),
            os.environ.get("REDDIT_PASSWORD"),
        ])

    def publish(self, title, body_md, category, canonical_url, image_url=None):
        client_id = os.environ["REDDIT_CLIENT_ID"]
        client_secret = os.environ["REDDIT_CLIENT_SECRET"]
        username = os.environ["REDDIT_USERNAME"]
        password = os.environ["REDDIT_PASSWORD"]
        subreddits_str = os.environ.get("REDDIT_SUBREDDITS", DEFAULT_SUBREDDITS)
        subreddits = [s.strip() for s in subreddits_str.split(",") if s.strip()]

        try:
            token = _get_oauth_token(client_id, client_secret, username, password)
            headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": USER_AGENT.format(username),
            }

            posted_urls = []
            for sr in subreddits:
                try:
                    resp = requests.post(
                        "https://oauth.reddit.com/api/submit",
                        headers=headers,
                        data={
                            "kind": "link",
                            "sr": sr,
                            "title": title,
                            "url": canonical_url,
                            "resubmit": False,  # Prevents duplicate URL posting
                            "sendreplies": False,
                        },
                        timeout=15,
                    )
                    if resp.ok:
                        data = resp.json()
                        # Reddit returns nested JSON structure
                        post_url = ""
                        try:
                            post_url = data["json"]["data"]["url"]
                        except (KeyError, TypeError):
                            post_url = f"https://reddit.com/r/{sr}"
                        print(f"  ✅ Reddit r/{sr}: posted → {post_url}")
                        posted_urls.append(post_url)
                    else:
                        print(f"  ❌ Reddit r/{sr}: {resp.status_code} — {resp.text[:150]}")
                except Exception as e:
                    print(f"  ❌ Reddit r/{sr}: exception — {e}")

            return posted_urls[0] if posted_urls else None

        except Exception as e:
            print(f"  ❌ {self.name}: OAuth failed — {e}")
            return None
