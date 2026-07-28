import re

STRICT_TEMPLATE = r"\b(?:[a-zA-Z0-9-]+\.)+{domain}\b"

RELAXED_TEMPLATE = r"(?:[a-zA-Z0-9_-]+\.)+{domain}"

WILDCARD_TEMPLATE = r"[a-zA-Z0-9-]+\.{domain}"


def build_patterns(domain: str):
    escaped = re.escape(domain)

    return [
        re.compile(STRICT_TEMPLATE.format(domain=escaped), re.IGNORECASE),
        re.compile(RELAXED_TEMPLATE.format(domain=escaped), re.IGNORECASE),
        re.compile(WILDCARD_TEMPLATE.format(domain=escaped), re.IGNORECASE),
    ]


def extract_subdomains(text: str, domain: str) -> set[str]:
    results = set()

    for pattern in build_patterns(domain):
        for match in pattern.findall(text):
            results.add(match.lower())

    return results