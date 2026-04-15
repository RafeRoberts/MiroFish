#!/usr/bin/env python3
"""Fetch DeFi-relevant Farcaster casts via Neynar API and write as daily markdown seed docs.

Reads NEYMAR_API_KEY from repo-root .env.
Uses cast search (free tier) — channel feed requires paid plan.
Output: seed-pipeline/seeds/farcaster/YYYY-MM-DD.md
Idempotent: skips if today's file already exists.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"
OUT_DIR = REPO_ROOT / "seed-pipeline" / "seeds" / "farcaster"

NEYNAR_BASE = "https://api.neynar.com/v2/farcaster"

# Search terms to pull DeFi-relevant casts (free tier uses cast search)
SEARCH_TERMS = ["defi", "ethereum", "solana", "arbitrum", "base", "yield", "liquidity", "rwa"]
CASTS_PER_TERM = 25


def load_api_key() -> str:
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("NEYMAR_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("NEYMAR_API_KEY not found in .env")


def fetch_casts(term: str, api_key: str) -> list[dict]:
    r = requests.get(
        f"{NEYNAR_BASE}/cast/search",
        params={"q": term, "limit": CASTS_PER_TERM},
        headers={"api_key": api_key, "accept": "application/json"},
        timeout=30,
    )
    if r.status_code in (402, 404):
        return []
    r.raise_for_status()
    return r.json().get("result", {}).get("casts", [])


def cast_to_md(i: int, cast: dict, term: str) -> str:
    author = cast.get("author", {})
    username = author.get("username", "unknown")
    display = author.get("display_name", username)
    text = cast.get("text", "").strip()
    timestamp = cast.get("timestamp", "")[:10]
    hash_ = cast.get("hash", "")
    url = f"https://warpcast.com/{username}/{hash_[:10]}" if hash_ else ""
    reactions = cast.get("reactions", {})
    likes = reactions.get("likes_count", 0)
    recasts = reactions.get("recasts_count", 0)

    lines = [f"### {i}. @{username} ({display}) — #{term}"]
    meta = " | ".join(filter(None, [timestamp, f"likes:{likes}", f"recasts:{recasts}"]))
    if meta:
        lines.append(f"*{meta}*")
    if url:
        lines.append(f"[{url}]({url})")
    if text:
        lines.append(f"\n{text}")
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out_path = OUT_DIR / f"{today}.md"

    if out_path.exists():
        print(f"Already exists: {out_path.name} — skipping.")
        return

    api_key = load_api_key()
    seen_hashes: set[str] = set()
    all_sections: list[str] = []
    total = 0

    for term in SEARCH_TERMS:
        casts = fetch_casts(term, api_key)
        # dedupe across terms by hash
        unique = [c for c in casts if c.get("hash") not in seen_hashes]
        seen_hashes.update(c.get("hash", "") for c in unique)
        print(f"  #{term}: {len(unique)} casts")
        if not unique:
            continue
        section = f"## #{term}\n\n"
        section += "\n\n---\n\n".join(
            cast_to_md(i + 1, c, term) for i, c in enumerate(unique)
        )
        all_sections.append(section)
        total += len(unique)

    if not all_sections:
        print("No casts returned. No file written.")
        sys.exit(0)

    frontmatter = (
        f"---\n"
        f"date: {today}\n"
        f"source: farcaster\n"
        f"terms: {', '.join(SEARCH_TERMS)}\n"
        f"cast_count: {total}\n"
        f"---\n\n"
    )

    body = f"# Farcaster DeFi Casts — {today}\n\n"
    body += "\n\n---\n\n".join(all_sections)

    out_path.write_text(frontmatter + body + "\n")
    print(f"Wrote {total} casts → {out_path.name}")


if __name__ == "__main__":
    main()
