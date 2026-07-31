"""
Favicon-hash + Shodan technique (the same idea favicon.hash.kmsec.uk
automates):

  1. Fetch the target's favicon.
  2. Hash it with Shodan's favicon-hash algorithm (base64-encode the raw
     bytes the same way Shodan does internally, then mmh3/murmur3 hash it).
  3. Search Shodan for `http.favicon.hash:<hash>` — finds every host on the
     internet serving the SAME favicon, often other subdomains/assets of the
     same organization sharing a common app template or CDN favicon.
  4. Each Shodan match includes a `hostnames` list for its IP — pull out any
     hostname matching our target domain, deduplicating automatically.

Requires SHODAN_API_KEY (same key as sources/shodan.py) and the `mmh3`
package (see requirements.txt).
"""

import base64
import os
import sys
from typing import Optional, Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains
from sources.shodan import shodan_search

try:
    import mmh3
except ImportError:
    mmh3 = None


def fetch_favicon_bytes(domain: str, timeout: int = 15) -> Optional[bytes]:
    headers = {"User-Agent": USER_AGENT}

    # 1) try the conventional path directly
    for scheme in ("https", "http"):
        try:
            resp = requests.get(f"{scheme}://{domain}/favicon.ico", headers=headers,
                                 timeout=timeout, allow_redirects=True)
            if resp.status_code == 200 and resp.content:
                return resp.content
        except requests.RequestException:
            continue

    # 2) fall back to parsing the homepage for a <link rel="icon"> tag
    for scheme in ("https", "http"):
        try:
            resp = requests.get(f"{scheme}://{domain}/", headers=headers,
                                 timeout=timeout, allow_redirects=True)
            if resp.status_code != 200:
                continue
            import re
            match = re.search(
                r'<link[^>]+rel=["\'](?:shortcut )?icon["\'][^>]+href=["\']([^"\']+)["\']',
                resp.text, re.IGNORECASE,
            )
            if not match:
                continue
            href = match.group(1)
            if href.startswith("//"):
                icon_url = f"{scheme}:{href}"
            elif href.startswith("http"):
                icon_url = href
            elif href.startswith("/"):
                icon_url = f"{scheme}://{domain}{href}"
            else:
                icon_url = f"{scheme}://{domain}/{href}"
            icon_resp = requests.get(icon_url, headers=headers, timeout=timeout)
            if icon_resp.status_code == 200 and icon_resp.content:
                return icon_resp.content
        except requests.RequestException:
            continue

    return None


def shodan_favicon_hash(favicon_bytes: bytes) -> int:
    """Shodan's exact algorithm: base64-encode with 76-char line wrapping
    (the standard MIME encoding Python's base64.encodebytes produces), then
    murmur3 (32-bit, signed) hash the result."""
    b64 = base64.encodebytes(favicon_bytes)
    return mmh3.hash(b64)


@register
class FaviconShodanSource(BaseSource):
    name = "favicon_shodan"
    display_name = "Favicon Hash + Shodan"
    requires_key = "SHODAN_API_KEY"

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()

        if mmh3 is None:
            print("[!] favicon_shodan requires the 'mmh3' package "
                  "(pip install mmh3). Skipping.", file=sys.stderr)
            return results

        favicon = fetch_favicon_bytes(domain)
        if not favicon:
            print(f"[!] favicon_shodan: couldn't fetch a favicon for {domain}.",
                  file=sys.stderr)
            return results

        fhash = shodan_favicon_hash(favicon)
        print(f"[i] favicon_shodan: hash={fhash}, searching Shodan for "
              f"http.favicon.hash:{fhash} ...", file=sys.stderr)

        api_key = os.environ.get("SHODAN_API_KEY")
        matches = shodan_search(f"http.favicon.hash:{fhash}", api_key)

        for match in matches:
            for hostname in match.get("hostnames", []) or []:
                results |= extract_subdomains(hostname, domain, bundle.host)
            for hostname in match.get("domains", []) or []:
                results |= extract_subdomains(hostname, domain, bundle.host)

        return results