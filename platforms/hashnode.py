"""
Hashnode — Native GitHub Repo Sync (no API calls needed)
https://hashnode.com/headless

Hashnode natively syncs articles from a GitHub repository.
Once configured, every .md file pushed to articles/ is auto-published.

This module is a structural placeholder — it logs the canonical URL
but does NOT make any API calls since Hashnode handles it natively.

┌─────────────────────────────────────────────────────────────────┐
│  MANUAL SETUP REQUIRED (one-time)                               │
│                                                                 │
│  1. Create a Hashnode account at https://hashnode.com            │
│  2. Create a blog (choose your subdomain, e.g. sandeep.hashnode │
│     .dev)                                                       │
│  3. Go to Blog Dashboard → Settings → GitHub                    │
│  4. Click "Install Hashnode GitHub App" to connect your account  │
│  5. Select repo: SandeepAi369/deepAI-Articles                   │
│  6. Set source directory: articles/                              │
│  7. Enable "Auto-publish new articles"                           │
│  8. Under "Post settings", enable:                               │
│     - Use filename as slug                                       │
│     - Use frontmatter title                                      │
│  9. Click "Save"                                                 │
│  10. Done — every sync.yml push auto-publishes to your blog     │
│                                                                 │
│  FRONTMATTER MAPPING (already handled by sync.py):               │
│    title  → Hashnode post title                                  │
│    date   → Publication date                                     │
│    category → Tag                                                │
│                                                                 │
│  NOTE: Hashnode GitHub App needs "Contents: Read" permission     │
│  on the deepAI-Articles repo. The install wizard handles this.  │
└─────────────────────────────────────────────────────────────────┘
"""

import os
from platforms.base import BasePlatform


class HashnodePlatform(BasePlatform):
    name = "Hashnode"

    def is_configured(self) -> bool:
        # Hashnode uses native GitHub sync — always "configured"
        # unless explicitly disabled via env var.
        return os.environ.get("HASHNODE_ENABLED", "true").lower() != "false"

    def publish(self, title, body_md, category, canonical_url, image_url=None):
        # No API call needed — Hashnode's GitHub integration auto-syncs
        # the .md file when sync.yml pushes to the repo.
        print(f"  ✅ {self.name}: handled via native GitHub repo sync")
        print(f"      (article .md file was pushed by sync.yml)")
        return f"hashnode://native-sync/{canonical_url}"
