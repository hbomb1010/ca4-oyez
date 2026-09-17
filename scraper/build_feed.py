#!/usr/bin/env python3
"""Builds data/feed.xml (podcast RSS) from data/cases.json.

Unlike build_dataset.py, this script makes no requests to
ca4.uscourts.gov -- it only reads the local data/cases.json (already
populated by build_dataset.py) and writes local XML. Enclosures point
straight at ca4.uscourts.gov's own mp3 URLs (see PLAN.md Phase 4) rather
than re-hosting audio.

Only cases with a downloaded audio file are included, since an accurate
enclosure needs a byte length -- see build_dataset.py's audio_bytes
field, set at download time.

Show identity (title/description/category/etc.) reflects the decisions
in docs/podcast-notes.md -- update both together if they change.

Usage:
    python build_feed.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

from feedgen.feed import FeedGenerator

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

SITE_URL = "https://hbomb1010.github.io/ca4-oyez"

SHOW_TITLE = "4thCir?Oyez"
SHOW_DESCRIPTION = (
    "A running archive of oral arguments before the United States Court "
    "of Appeals for the Fourth Circuit -- every argued case, audio "
    "straight from the court, with the docket number, panel, counsel, "
    "and argument date for each. Not affiliated with the Fourth Circuit "
    "or with oyez.org."
)
SHOW_AUTHOR = "hbomb1010"
SHOW_LANGUAGE = "en-us"
SHOW_CATEGORY = "Government"
SHOW_EXPLICIT = "no"


def episode_title(case: dict) -> str:
    return f"{case['case_name']} (No. {case['docket_number']})"


def episode_description(case: dict) -> str:
    lines = [
        f"Docket: {case['docket_number']}",
        f"Argued: {case['argument_date']}",
        f"Panel: {', '.join(case['panel'])}",
        f"Counsel: {', '.join(case['counsel'])}",
    ]
    return "\n".join(lines)


def build(cases: list[dict]) -> FeedGenerator:
    fg = FeedGenerator()
    fg.load_extension("podcast")

    fg.title(SHOW_TITLE)
    fg.description(SHOW_DESCRIPTION)
    fg.link(href=SITE_URL, rel="alternate")
    fg.language(SHOW_LANGUAGE)
    fg.podcast.itunes_author(SHOW_AUTHOR)
    fg.podcast.itunes_explicit(SHOW_EXPLICIT)
    fg.podcast.itunes_category(SHOW_CATEGORY)
    fg.podcast.itunes_image(f"{SITE_URL}/cover-1400.jpg")
    fg.image(url=f"{SITE_URL}/cover-1400.jpg", title=SHOW_TITLE, link=SITE_URL)

    episodes = [c for c in cases if c.get("audio_file") and c.get("audio_bytes")]
    print(f"{len(episodes)} of {len(cases)} cases have a downloaded audio file "
          f"and byte size -- only those get an episode.", file=sys.stderr)

    for case in episodes:
        fe = fg.add_entry()
        fe.id(case["docket_number"])
        fe.guid(case["docket_number"], permalink=False)
        # TODO: point at a real per-case page once Part 2's web UI is deployed (Phase 15)
        fe.link(href=SITE_URL)
        fe.title(episode_title(case))
        fe.description(episode_description(case))
        fe.enclosure(case["audio_url"], str(case["audio_bytes"]), "audio/mpeg")
        argument_date = dt.date.fromisoformat(case["argument_date"])
        pub_dt = dt.datetime.combine(argument_date, dt.time(), tzinfo=dt.timezone.utc)
        fe.pubDate(pub_dt)

    return fg


def main() -> None:
    cases = json.loads((DATA_DIR / "cases.json").read_text())
    fg = build(cases)
    out = DATA_DIR / "feed.xml"
    fg.rss_file(str(out))
    print(f"Wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
