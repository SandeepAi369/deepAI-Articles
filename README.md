# deepAI Articles

Auto-synced Markdown articles from Supabase database via GitHub Actions.

## How it works
- A daily GitHub Actions workflow fetches all articles from Supabase (READ-ONLY).
- Each article is saved as a `.md` file inside the `/articles/` folder.
- Filenames are derived from the article title (kebab-case).

## Markdown Format
```markdown
---
title: "Article Title"
date: "2026-01-01"
category: "AI"
---

![Article Title](https://cloudinary.com/...)

# Article Title

Article content here...
```

## Secrets Required
| Secret | Description |
|--------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Your Supabase anon/public key |
