#!/usr/bin/env python3
"""Fetch Mantis Money Buttondown newsletter issues and write them as markdown seed docs.

Env: BUTTONDOWN_API_KEY (loaded from repo-root .env)
Output: seed-pipeline/seeds/buttondown/YYYY-MM-DD_slug.md
Idempotent: skips issues whose output file already exists.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"
OUT_DIR = REPO_ROOT / "seed-pipeline" / "seeds" / "buttondown"
API_URL = "https://api.buttondown.email/v1/emails"


def load_api_key() -> str:
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("BUTTONDOWN_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("BUTTONDOWN_API_KEY not found in .env")


def clean_body(body: str) -> str:
    body = re.sub(r"<!--.*?-->\s*", "", body, flags=re.DOTALL)
    body = re.sub(r"\{%\s*if[^%]*%\}", "", body)
    body = re.sub(r"\{%\s*else\s*%\}\s*(.*?)\{%\s*endif\s*%\}", "", body, flags=re.DOTALL)
    body = re.sub(r"\{%\s*endif\s*%\}", "", body)
    body = re.sub(r"\{\{[^}]*\}\}", "", body)
    return body.strip()


def write_issue(issue: dict) -> bool:
    date = issue["publish_date"][:10]
    slug = issue["slug"]
    out_path = OUT_DIR / f"{date}_{slug}.md"
    if out_path.exists():
        return False
    frontmatter = (
        f"---\n"
        f"date: {date}\n"
        f"subject: {issue['subject']}\n"
        f"url: {issue['absolute_url']}\n"
        f"source: buttondown\n"
        f"---\n\n"
    )
    out_path.write_text(frontmatter + clean_body(issue["body"]) + "\n")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    headers = {"Authorization": f"Token {load_api_key()}"}
    url = f"{API_URL}?ordering=-publish_date&page_size=100"
    written = skipped = 0
    while url:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        for issue in data["results"]:
            if issue.get("status") != "sent":
                continue
            if write_issue(issue):
                written += 1
            else:
                skipped += 1
        url = data.get("next")
    print(f"Wrote {written} new issues, skipped {skipped} existing.")


if __name__ == "__main__":
    main()
