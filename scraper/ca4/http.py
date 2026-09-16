"""Polite HTTP helpers for pulling public data from ca4.uscourts.gov.

ca4.uscourts.gov's robots.txt disallows the Claude-Web and ClaudeBot user
agents site-wide. This code is meant to be run by a human from their own
machine/identity -- not invoked as an automated Claude action. Keep the
rate limit in place and put real contact info in USER_AGENT below.
"""
from __future__ import annotations

import time
from pathlib import Path

import requests

USER_AGENT = "ca4-oyez-podcast-scraper/0.1 (+https://github.com/hbomb1010/ca4-oyez)"

RATE_LIMIT_SECONDS = 2.0

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})
_last_request_at = 0.0


def _throttle() -> None:
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    wait = RATE_LIMIT_SECONDS - elapsed
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def get(url: str, **kwargs) -> requests.Response:
    """Rate-limited GET. Raises for non-2xx responses."""
    _throttle()
    resp = _session.get(url, timeout=30, **kwargs)
    resp.raise_for_status()
    return resp


def download(url: str, dest: Path, *, force: bool = False) -> Path:
    """Rate-limited binary download, skipped if dest already exists."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        return dest
    _throttle()
    resp = _session.get(url, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return dest
