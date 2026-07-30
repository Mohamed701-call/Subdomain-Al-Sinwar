"""Search-engine dork generator (Google, Bing, DuckDuckGo). Doesn't scrape
any search engine directly — that's against their ToS and gets blocked
immediately. Instead this hands back ready-to-use dork queries/URLs the user
can open manually or feed into a compliant SERP API.

NOT registered as a BaseSource: it doesn't return subdomains, it returns
(engine, query, url) tuples for reporting alongside the real results."""

from typing import Iterable, Tuple
from urllib.parse import quote

DORK_TEMPLATES = [
    'site:{domain}',
    'site:*.{domain}',
    'site:{domain} -www',
    'site:{domain} inurl:login',
    'site:{domain} inurl:admin',
    'site:{domain} intitle:"index of"',
    'site:{domain} ext:log OR ext:env OR ext:sql OR ext:bak',
    'site:pastebin.com "{domain}"',
    'site:github.com "{domain}"',
]

ENGINES = {
    "google": "https://www.google.com/search?q=",
    "bing": "https://www.bing.com/search?q=",
    "duckduckgo": "https://duckduckgo.com/?q=",
}


def generate_dorks(domain: str) -> Iterable[Tuple[str, str, str]]:
    """Yields (engine_name, query, url) for every engine x template combo."""
    for template in DORK_TEMPLATES:
        query = template.format(domain=domain)
        for engine, base_url in ENGINES.items():
            yield engine, query, base_url + quote(query)