"""Startup banner."""

from core import TOOL_NAME, __version__

BANNER = rf"""
   _____       _         _                       _____ _
  / ____|     | |       | |                     / ____(_)
 | (___  _   _| |__   __| | ___  _ __ ___   __ _| (___  _ _ ____      ____ _ _ __
  \___ \| | | | '_ \ / _` |/ _ \| '_ ` _ \ / _` |\___ \| | '_ \ \ /\ / / _` | '__|
  ____) | |_| | |_) | (_| | (_) | | | | | | (_| |____) | | | | \ V  V / (_| | |
 |_____/ \__,_|_.__/ \__,_|\___/|_| |_| |_|\__,_|_____/|_|_| |_|\_/\_/ \__,_|_|

  {TOOL_NAME} v{__version__} — passive + active subdomain enumeration
"""


def print_banner() -> None:
    import sys
    print(BANNER, file=sys.stderr)