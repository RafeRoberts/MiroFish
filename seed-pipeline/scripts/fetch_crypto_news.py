#!/usr/bin/env python3
"""Fetch DeFi news from cryptocurrency.cv and write as daily markdown seed docs.

Pulls multiple DeFi-relevant categories and merges into one daily file.
No API key required — browser headers needed to bypass bot filter.

Output: seed-pipeline/seeds/crypto_news/YYYY-MM-DD.md
Idempotent: skips if today's file already exists.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "seed-pipeline" / "seeds" / "crypto_news"
BASE_URL = "https://cryptocurrency.cv/api/news"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://cryptocurrency.cv/",
}

# Categories most relevant to our DeFi prediction domains
CATEGORIES = ["defi", "ethereum", "altl1", "stablecoin", "layer2", "onchain", "security"]
LIMIT_PER_CATEGORY = 20


def fetch_category(category: str) -> list[dict]:
    r = requests.get(
        BASE_URL,
        params={"limit": LIMIT_PER_CATEGORY, "category": category},
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("articles", [])


def dedupe(articles: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for a in articles:
        key = a.get("id") or a.get("link") or a.get("title")
        if key and key not in seen:
            seen.add(key)
            out.append(a)
    return out


def article_to_md(i: int, a: dict) -> str:
    title = a.get("title", "").strip()
    source = a.get("source", "")
    pub = a.get("pubDate", a.get("publishedAt", ""))[:10]
    link = a.get("link", a.get("url", ""))
    sentiment = a.get("sentiment", "")
    tags = ", ".join(a.get("tags", []))
    desc = a.get("description", "").strip()

    lines = [f"### {i}. {title}"]
    meta = " | ".join(filter(None, [source, pub, sentiment, tags]))
    if meta:
        lines.append(f"*{meta}*")
    if link:
        lines.append(f"[{link}]({link})")
    if desc:
        lines.append(f"\n{desc}")
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out_path = OUT_DIR / f"{today}.md"

    if out_path.exists():
        print(f"Already exists: {out_path.name} — skipping.")
        return

    all_articles: list[dict] = []
    for cat in CATEGORIES:
        articles = fetch_category(cat)
        print(f"  {cat}: {len(articles)} articles")
        all_articles.extend(articles)

    articles = dedupe(all_articles)

    if not articles:
        print("No articles returned — upstream feed may be empty. No file written.")
        sys.exit(0)

    frontmatter = (
        f"---\n"
        f"date: {today}\n"
        f"source: cryptocurrency.cv\n"
        f"article_count: {len(articles)}\n"
        f"categories: {', '.join(CATEGORIES)}\n"
        f"---\n\n"
    )

    body = f"# DeFi News — {today}\n\n"
    body += "\n\n---\n\n".join(article_to_md(i + 1, a) for i, a in enumerate(articles))

    out_path.write_text(frontmatter + body + "\n")
    print(f"Wrote {len(articles)} articles → {out_path.name}")


if __name__ == "__main__":
    main()
