from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Dict
from config import OUTPUT_DIR
from core.models import SubdomainRecord


def save_results(
    records: Dict[str, SubdomainRecord],
    domain: str,
    filename: str | None = None,
    json_output: bool = False,
    csv_output: bool = False,
) -> None:
    if not records:
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not filename:
        timestamp = int(time.time())
        ext = "json" if json_output else ("csv" if csv_output else "txt")
        clean_domain = domain.replace(".", "_") if domain else "target"
        filepath = OUTPUT_DIR / f"{clean_domain}_{timestamp}.{ext}"
    else:
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)

    if json_output:
        data = {
            host: {
                "hostname": rec.hostname,
                "confidence_score": rec.confidence_score,
                "sources": list(rec.sources),
                "evidence": rec.evidence,
            }
            for host, rec in records.items()
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    elif csv_output:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Hostname", "Confidence Score", "Sources Count", "Sources"])
            for rec in records.values():
                writer.writerow([
                    rec.hostname,
                    f"{rec.confidence_score}%",
                    len(rec.sources),
                    ", ".join(rec.sources),
                ])
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            for host in sorted(records.keys()):
                f.write(f"{host}\n")