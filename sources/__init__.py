"""
Individual subdomain data sources. Importing this package imports every
source module below, which triggers each one's @register decorator and
populates core.registry — nothing else needs to know the full list.

NOTE: subfinder is intentionally NOT included — this tool no longer shells
out to or depends on the external subfinder binary.
"""

from . import (
    alienvault,
    anubis,
    bruteforce,
    crtsh,
    favicon_shodan,
    fofa,
    github,
    hackertarget,
    projectdiscovery_cloud,
    rapiddns,
    securitytrails,
    shodan,
    threatcrowd,
    urlscan,
    virustotal,
    wayback,
)

# search_engines is intentionally not imported here — it's a plain dork
# generator (not a BaseSource), imported directly by main.py where needed.

__all__ = [
    "alienvault", "anubis", "bruteforce", "crtsh", "favicon_shodan", "fofa",
    "github", "hackertarget", "projectdiscovery_cloud", "rapiddns",
    "securitytrails", "shodan", "threatcrowd", "urlscan", "virustotal", "wayback",
]