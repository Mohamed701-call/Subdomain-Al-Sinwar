# Subdomain-Al-Sinwar

Passive + active subdomain enumeration tool. Aggregates results from 15+
free and paid sources, deduplicates them, and DNS/HTTP-verifies brute-force
results so you're not just guessing.

```
git clone https://github.com/Mohamed701-call/Subdomain-Al-Sinwar.git
cd Subdomain-Al-Sinwar
pip install -e .
subdomain-al-sinwar example.com

## Installation

**Requirements:** Python 3.8+

```bash
git clone https://github.com/Mohamed701-call/Subdomain-Al-Sinwar.git
cd Subdomain-Al-Sinwar
pip install -e .
```

This installs the `subdomain-al-sinwar` command on your PATH (via
`setup.py`'s entry point), so you can run it from anywhere by name — no
need to type `python3 main.py`.

> **On Kali / Debian / other externally-managed Python setups**, plain
> `pip install -e .` will fail with `error: externally-managed-environment`
> (PEP 668) — this is a safety restriction from the OS, not a bug in this
> tool. Use one of these instead:
>
> ```bash
> # Option A (recommended): isolated virtual environment
> python3 -m venv venv
> source venv/bin/activate
> pip install -e .
> # any new terminal: run `source venv/bin/activate` again before using the tool
> ```
>
> ```bash
> # Option B (quicker, less isolated)
> pip install -e . --break-system-packages


## Quick start

```bash
# Run every source against a domain
subdomain-al-sinwar example.com

# Save results to a file + full JSON report
subdomain-al-sinwar example.com -o subs.txt --json results.json

# Only specific sources
subdomain-al-sinwar example.com --sources crtsh,github,bruteforce

# DNS-verify every result (drops stale/dead entries, wildcard-aware)
subdomain-al-sinwar example.com --resolve

# Brute-force with an extra HTTP confirmation pass (highest confidence)
subdomain-al-sinwar example.com --sources bruteforce --http-verify

# See which source found each subdomain
subdomain-al-sinwar example.com --breakdown

# Use a bigger external wordlist for brute-force (e.g. SecLists)
subdomain-al-sinwar example.com --wordlist /path/to/subdomains.txt
```

Run `subdomain-al-sinwar --help` for the full list of flags.

---

## API keys (optional, but unlocks more sources)

Several sources need an API key. Sources missing a key are skipped
automatically — the tool never errors out because of a missing key, it just
runs everything it can with what you've configured.

Copy the example config once and fill in whatever keys you have:

```bash
mkdir -p ~/.config/subdomain-al-sinwar
cp config.example.env ~/.config/subdomain-al-sinwar/config
nano ~/.config/subdomain-al-sinwar/config
```

```ini
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
SECURITYTRAILS_API_KEY=
VIRUSTOTAL_API_KEY=
URLSCAN_API_KEY=
SHODAN_API_KEY=
FOFA_EMAIL=
FOFA_KEY=
```

You can also just `export` them as environment variables instead, or point
to a config file anywhere with `--config /path/to/file`. A real exported
env var always takes priority over the config file.

| Key | Free tier? | Get it at |
|---|---|---|
| `GITHUB_TOKEN` | Yes | github.com/settings/tokens |
| `SECURITYTRAILS_API_KEY` | Limited trial | securitytrails.com |
| `VIRUSTOTAL_API_KEY` | Yes (4 req/min) | virustotal.com |
| `URLSCAN_API_KEY` | Optional — works without one | urlscan.io |
| `SHODAN_API_KEY` | Limited free tier | shodan.io |
| `FOFA_EMAIL` / `FOFA_KEY` | Limited free tier | fofa.info |

---

## Where subdomains come from

| Source | Key needed? | What it does |
|---|---|---|
| **crt.sh** | No | Scans Certificate Transparency logs for every cert ever issued containing the domain |
| **GitHub** | Yes | Deep multi-endpoint search — see below, this one's not just a regex over code |
| **SecurityTrails** | Yes | Historical DNS records |
| **VirusTotal** | Yes (free) | Known subdomains from VT's passive DNS dataset |
| **Shodan** | Yes | Shodan's DNS-domain dataset for the target |
| **Favicon Hash + Shodan** | Yes (Shodan key) | Hashes the site's favicon the way Shodan does internally, searches Shodan for every other host serving the *same* favicon, and pulls subdomains out of their hostnames — catches related infrastructure that shares a common app/CDN template |
| **FOFA** | Yes | FOFA's asset search engine |
| **ProjectDiscovery Cloud DNS** | No | Free public passive-DNS dataset |
| **Anubis** | No | Free public subdomain dataset (jldc.me) |
| **Wayback Machine** | No | Archived URLs — surfaces old/retired subdomains that no longer show up anywhere else |
| **urlscan.io** | Optional | Indexed pages that mention the domain |
| **HackerTarget** | No | Free passive DNS lookup |
| **AlienVault OTX** | No | Free passive DNS |
| **RapidDNS.io** | No | Free passive DNS |
| **ThreatCrowd** | No | Free, but the public API is known to be unreliable/frequently offline |
| **Brute-force + Permutation** | No | Wordlist + smart mutation guessing, fully DNS/HTTP-verified — see below |
| **Search-engine dorks** | No | Generates ready-to-use Google/Bing/DuckDuckGo dork URLs (`--show-dorks`) — doesn't scrape search engines directly, since that's against their ToS |

**subfinder is intentionally not used or bundled** — this tool doesn't
shell out to any external binary; every source above is implemented
natively.

### How GitHub search actually works here

Most tools do one generic regex search over GitHub code and call it done.
This one searches multiple endpoints with multiple targeted queries:

- **`/search/code`** — not just a bare domain search, but *15 targeted
  queries* covering `.env`, YAML, JSON, JS, TS, Terraform, Dockerfiles,
  docker-compose, nginx configs, generic `.conf` files, `hosts` files, and
  `.github/workflows/` (Actions configs). It also specifically searches for
  `filename:CNAME` — a repo's `CNAME` file is literally the custom domain
  configured for its GitHub Pages site.
- **`/search/commits`** — commit messages often leak hostnames ("fix DNS
  for staging.example.com").
- **`/search/issues`** — issues *and* pull requests (title + body).

Every result from every endpoint goes through **four separate regexes**
(host, URL-context, wildcard, and CNAME-zone-style), then gets normalized,
validated, and deduplicated.

Gist search, wiki search, cross-repo release search, and Pages *content*
search have no public REST API endpoint on GitHub's side, so they're not
included — scraping GitHub's web search directly is unreliable and against
their ToS, the same reason this tool doesn't scrape Google either.

### How brute-force verification works

Every brute-forced/permuted candidate is **verified**, not just guessed:

1. **DNS resolution** — must actually resolve to an A/AAAA record.
2. **Wildcard-DNS filtering (automatic)** — many domains have wildcard DNS,
   where `*.domain` resolves to *something* for literally any subdomain.
   Before brute-forcing, the tool probes a few random, essentially
   impossible-to-collide labels to fingerprint the wildcard's IP set. Any
   candidate whose resolved IPs are entirely explained by that wildcard is
   discarded automatically.
3. **HTTP verification (optional, `--http-verify`)** — an extra pass that
   makes a real HTTPS/HTTP request against each DNS-confirmed candidate.
   Only candidates that get an actual response are kept.

It also seeds smart permutations from whatever every other source already
found — e.g. if `api.example.com` is known to exist, it also tries
`api-dev.example.com`, `dev-api.example.com`, `api2.example.com`, etc.

---

## How results are combined

- Every source's raw output is filtered through the same domain-matching
  regex, so noise from one source can't leak unrelated hostnames in.
- The final list is deduplicated across **all** sources.
- When saving to file (`-o`), subdomains are ordered by source priority
  (default: GitHub → SecurityTrails → VirusTotal → Shodan → FOFA → ... →
  brute-force last) — configurable with `--source-order`. A subdomain found
  by multiple sources is listed once, credited to the first matching source.

---

## Project structure

```
Subdomain-Al-Sinwar/
├── main.py                     # orchestration entry point
├── cli.py                      # argument parsing
├── config.py                   # API-key config file loader
├── __main__.py                 # python -m entry point
├── setup.py / requirements.txt
├── core/
│   ├── base.py                 # BaseSource interface every source implements
│   ├── models.py                # SourceResult / ScanResult
│   ├── registry.py              # @register — auto-populates the source list
│   ├── events.py                 # event bus for progress reporting
│   └── manager.py                # runs sources in parallel, merges results
├── extractors/
│   └── regex.py                 # 4-regex extraction: host/URL/wildcard/CNAME
├── utils/
│   ├── dns_resolver.py           # DNS resolution, wildcard detection, HTTP verify
│   ├── output.py                 # source-priority ordering, file writing
│   ├── logger.py / banner.py / retry.py / helpers.py
└── sources/
    ├── crtsh.py, github.py, securitytrails.py, virustotal.py,
    ├── shodan.py, fofa.py, favicon_shodan.py, projectdiscovery_cloud.py,
    ├── anubis.py, wayback.py, urlscan.py, hackertarget.py, alienvault.py,
    ├── rapiddns.py, threatcrowd.py, bruteforce.py, search_engines.py
```

Adding a new source means dropping one file in `sources/` that implements
`BaseSource.run()` and decorating the class with `@register` — nothing else
needs to change.

---

## Full flag reference

```
subdomain-al-sinwar <domain> [options]

  --sources LIST          comma-separated source list (default: all)
  -o, --output FILE       save deduplicated, source-ordered plain-text list
  --json FILE             save full JSON report (per-source counts, errors, dorks, etc.)
  --config FILE           path to a config file with API keys
  --wordlist FILE         custom brute-force wordlist (one label per line)
  --no-permutations       skip permutation generation during brute-force
  --http-verify           extra HTTP confirmation pass for brute-force results
  --dns-workers N         parallel DNS resolution workers (default: 50)
  --dns-timeout N         per-lookup DNS timeout in seconds (default: 3.0)
  --http-timeout N        per-request HTTP verify timeout in seconds (default: 5.0)
  --resolve               DNS-verify ALL final results, wildcard-aware
  --breakdown             show which source(s) found each subdomain
  --show-dorks            print search-engine dork queries to stdout
  --source-order LIST     custom source priority for file output ordering
  --no-banner             skip the startup banner
```

---

## License

MIT — see [LICENSE](LICENSE).
