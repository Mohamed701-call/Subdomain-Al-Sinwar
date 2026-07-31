# Subdomain-Al-Sinwar

Passive + active subdomain enumeration tool. Aggregates results from 15+
sources, deduplicates them, and DNS/HTTP-verifies brute-force results.

## Install

```bash
git clone https://github.com/Mohamed701-call/Subdomain-Al-Sinwar.git
cd Subdomain-Al-Sinwar
pip install -e .
```

On Kali/Debian, if you get `externally-managed-environment`, add
`--break-system-packages` to the command above, or use a venv:
`python3 -m venv venv && source venv/bin/activate` first.

## Usage

```bash
subdomain-al-sinwar example.com

# save results
subdomain-al-sinwar example.com -o subs.txt --json results.json

# specific sources only
subdomain-al-sinwar example.com --sources crtsh,github,bruteforce

# DNS-verify all results (wildcard-aware)
subdomain-al-sinwar example.com --resolve

# brute-force with HTTP confirmation pass
subdomain-al-sinwar example.com --sources bruteforce --http-verify

# show which source found what
subdomain-al-sinwar example.com --breakdown
```

Full flag list: `subdomain-al-sinwar --help`

## API keys

Some sources need a key — missing ones are just skipped automatically.

```bash
mkdir -p ~/.config/subdomain-al-sinwar
cp config.API.env ~/.config/subdomain-al-sinwar/config
nano ~/.config/subdomain-al-sinwar/config
```

```ini
GITHUB_TOKEN=
SECURITYTRAILS_API_KEY=
VIRUSTOTAL_API_KEY=
URLSCAN_API_KEY=
SHODAN_API_KEY=
FOFA_EMAIL=
FOFA_KEY=
```

## Sources

| Source | Key needed? | Notes |
|---|---|---|
| crt.sh | No | Certificate Transparency logs |
| GitHub | Yes | Code, commits, issues/PRs — multiple targeted queries + regexes |
| SecurityTrails | Yes | Historical DNS |
| VirusTotal | Yes (free tier) | Passive DNS |
| Shodan | Yes | DNS-domain dataset |
| Favicon Hash + Shodan | Yes (Shodan) | Hashes the favicon, finds other hosts serving the same one |
| FOFA | Yes | Asset search engine |
| ProjectDiscovery Cloud DNS | No | Free public dataset |
| Anubis | No | Free public dataset (jldc.me) |
| Wayback Machine | No | Archived URLs, catches old/retired subdomains |
| urlscan.io | Optional | Indexed pages |
| HackerTarget | No | Free passive DNS |
| AlienVault OTX | No | Free passive DNS |
| RapidDNS.io | No | Free passive DNS |
| ThreatCrowd | No | Free, but often unreliable/offline |
| Brute-force + Permutation | No | Wordlist + mutation guessing, DNS/HTTP-verified |
| Search-engine dorks | No | Generates dork URLs (`--show-dorks`), doesn't scrape |

`subfinder` is not used — everything above is implemented natively.

## License

MIT — see [LICENSE](LICENSE).
