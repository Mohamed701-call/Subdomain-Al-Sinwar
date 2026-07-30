"""
GitHub — deep multi-endpoint search, not a single generic regex pass.

Endpoints actually searched (everything GitHub's REST Search API supports):
  - /search/code      — file contents, across many targeted file types
  - /search/commits    — commit messages (leaks often show up in "fix DNS
                          for staging.example.com"-style commit messages)
  - /search/issues     — issues AND pull requests (title + body)

Targeted code-search queries cover the file types most likely to leak
subdomains: ENV, JSON, YAML, JS, TS, Terraform, Docker, Kubernetes, nginx,
Apache/.conf, hosts files, and CNAME files specifically (a repo's CNAME
file is literally the custom domain for its GitHub Pages site).

NOT supported by GitHub's public API (documented here rather than silently
skipped): Gist search, Wiki search, cross-repo Release search, and GitHub
Pages content search all have no REST search endpoint — GitHub only
exposes those through its (non-API, rate-limited, JS-rendered) web search,
which isn't reliably scrapable. Actions workflow *configs* (not runtime
logs) are covered indirectly via the `path:.github/workflows` code-search
query above, since workflow YAML often references real hostnames.

Every result — from code, commits, or issues/PRs — is run through the full
four-regex bundle (host/URL/wildcard/CNAME) via extractors.regex.extract_all,
then normalized, validated, and deduplicated.
"""

import os
import sys
import time
from typing import Set

import requests

from core import DEFAULT_TIMEOUT, USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_all

# Targeted code-search suffixes — each combined with the quoted domain.
CODE_SEARCH_QUALIFIERS = [
    "",                                # bare content search
    "extension:env",
    "extension:yml",
    "extension:yaml",
    "extension:json",
    "extension:js",
    "extension:ts",
    "extension:tf",                   # Terraform
    "filename:Dockerfile",
    "filename:docker-compose.yml",
    "filename:nginx.conf",
    "extension:conf",                 # generic *.conf (nginx/Apache/etc.)
    "filename:CNAME",                 # GitHub Pages custom domain files
    "path:.github/workflows",         # Actions workflow configs
    "filename:hosts",
]


class _GithubSearcher:
    """Shared session + paging logic for all three GitHub search endpoints."""

    def __init__(self, token: str):
        self.auth_failed = False
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.text-match+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
        })

    def search(self, endpoint: str, query: str, max_pages: int = 2) -> list:
        """Returns raw `items` across pages for one endpoint/query."""
        if self.auth_failed:
            return []
        items_out = []
        for page in range(1, max_pages + 1):
            url = f"https://api.github.com/search/{endpoint}"
            try:
                resp = self.session.get(url, params={"q": query, "per_page": 100, "page": page},
                                         timeout=DEFAULT_TIMEOUT)
            except requests.RequestException as e:
                print(f"[!] GitHub {endpoint} search error: {e}", file=sys.stderr)
                break

            if resp.status_code == 422:
                break  # invalid/empty query combo, nothing to do
            if resp.status_code == 401:
                print(f"[!] GitHub {endpoint} search: invalid/expired GITHUB_TOKEN "
                      f"(401 Unauthorized). Check your token. Skipping remaining GitHub queries.",
                      file=sys.stderr)
                self.auth_failed = True
                break
            if resp.status_code == 403:
                reset = resp.headers.get("X-RateLimit-Reset")
                print(f"[!] GitHub rate-limited on {endpoint} (resets at epoch {reset}).",
                      file=sys.stderr)
                break
            if resp.status_code != 200:
                print(f"[!] GitHub {endpoint} search returned {resp.status_code}: "
                      f"{resp.text[:200]}", file=sys.stderr)
                break

            data = resp.json()
            items = data.get("items", [])
            items_out.extend(items)
            if len(items) < 100:
                break
            time.sleep(2)
        return items_out


@register
class GithubSource(BaseSource):
    name = "github"
    display_name = "GitHub (code/commits/issues+PRs)"
    requires_key = "GITHUB_TOKEN"

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        token = os.environ.get("GITHUB_TOKEN")
        searcher = _GithubSearcher(token)

        # --- 1. Code search: multiple targeted queries across file types ---
        for qualifier in CODE_SEARCH_QUALIFIERS:
            if searcher.auth_failed:
                break
            query = f'"{domain}" {qualifier}'.strip()
            items = searcher.search("code", query, max_pages=2)
            for item in items:
                blob = " ".join([item.get("name", ""), item.get("path", ""),
                                  item.get("repository", {}).get("full_name", "")])
                results |= extract_all(blob, bundle)
                for tm in item.get("text_matches", []) or []:
                    results |= extract_all(tm.get("fragment", ""), bundle)
            if not searcher.auth_failed:
                time.sleep(3)  # stay well under GitHub's search rate limit across many queries

        # --- 2. Commit messages ---
        commit_items = searcher.search("commits", f'"{domain}"', max_pages=2)
        for item in commit_items:
            message = item.get("commit", {}).get("message", "")
            results |= extract_all(message, bundle)

        # --- 3. Issues + Pull Requests (title + body) ---
        issue_items = searcher.search("issues", f'"{domain}"', max_pages=2)
        for item in issue_items:
            blob = " ".join([item.get("title", "") or "", item.get("body", "") or ""])
            results |= extract_all(blob, bundle)

        return results