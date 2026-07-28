from __future__ import annotations

import logging
from config import LOG_DIR

log_file = LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
    ],
)

logger = logging.getLogger("Subdomain-Al-Sinwar")