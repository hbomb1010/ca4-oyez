#!/usr/bin/env python3
"""Builds data/cases.json by joining CA4's oral argument list with its
opinions list, downloading source files, and writing normalized records.

Run this yourself (see scraper/README.md for why) -- it makes real
requests to ca4.uscourts.gov.

Usage:
    python build_dataset.py --since 2026-01-01
    python build_dataset.py --since 2026-01-01 --no-download   # metadata only, fast, for iterating on the join logic
    python build_dataset.py --since 2026-01-01 --no-parse-pdf  # skip the majority/concurrence/dissent split
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import re
import sys
from pathlib import Path

from ca4 import http, opinion_pdf, opinions as ca4_opinions
from ca4 import oral_arguments as ca4_oral_arguments

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FILES_DIR = DATA_DIR / "files"

_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[.,'\"]")


def normalize_case_name(name: str) -> str:
    n = name.lower()
    n = n.replace("united states", "us")
    n = _PUNCT_RE.sub("", n)
    n = _WS_RE.sub(" ", n).strip()
    return n


def build(since: dt.date, *, download: bool, parse_pdf: bool) -> list[dict]:
    print(f"Fetching oral argument list (since {since})...", file=sys.stderr)
    arguments = ca4_oral_arguments.fetch(since=since)
    print(f"  {len(arguments)} arguments found.", file=sys.stderr)

    print("Fetching recent opinions (last 30 days -- see ca4/opinions.py note "
          "about backfilling further back)...", file=sys.stderr)
    all_opinions = ca4_opinions.fetch_recent()
    argued_opinions = [o for o in all_opinions if o.after_argument]
    print(f"  {len(all_opinions)} opinions total, {len(argued_opinions)} decided after argument.",
          file=sys.stderr)

    opinions_by_name: dict[str, ca4_opinions.Opinion] = {}
    for o in argued_opinions:
        opinions_by_name.setdefault(normalize_case_name(o.case_name), o)

    records: list[dict] = []
    for arg in arguments:
        key = normalize_case_name(arg.case_name)
        opinion = opinions_by_name.get(key)

        record: dict = {
            "docket_number": arg.docket_number,
            "case_name": arg.case_name,
            "argument_date": arg.argument_date.isoformat(),
            "panel": arg.panel,
            "counsel": arg.counsel,
            "audio_url": arg.audio_url,
            "audio_file": None,
            "audio_bytes": None,
            "opinion": None,
            # Editorial fields -- no free source for these (see README);
            # fill in by hand later.
            "facts_of_the_case": None,
            "question_presented": None,
            "conclusion_summary": None,
        }

        if download and arg.audio_url:
            dest = FILES_DIR / "audio" / f"{arg.docket_number}-{arg.argument_date.strftime('%Y%m%d')}.mp3"
            try:
                http.download(arg.audio_url, dest)
                record["audio_file"] = str(dest.relative_to(ROOT))
                record["audio_bytes"] = dest.stat().st_size
            except Exception as e:  # noqa: BLE001
                print(f"  WARN: failed to download audio for {arg.docket_number}: {e}", file=sys.stderr)

        if opinion:
            record["opinion"] = {
                "opinion_number": opinion.opinion_number,
                "published": opinion.published,
                "author": opinion.author,
                "decision": opinion.decision,
                "case_type": opinion.case_type,
                "appeal_from": opinion.appeal_from,
                "originating_judge": opinion.originating_judge,
                "pdf_url": opinion.pdf_url,
                "date_issued": opinion.date_issued.isoformat() if opinion.date_issued else None,
                "pdf_file": None,
                "sections": None,
            }

            if download and opinion.pdf_url:
                dest = FILES_DIR / "opinions" / f"{opinion.opinion_number}.pdf"
                try:
                    http.download(opinion.pdf_url, dest)
                    record["opinion"]["pdf_file"] = str(dest.relative_to(ROOT))

                    if parse_pdf:
                        sections = opinion_pdf.parse(dest)
                        record["opinion"]["sections"] = [dataclasses.asdict(s) for s in sections]
                except Exception as e:  # noqa: BLE001
                    print(f"  WARN: failed to download/parse opinion for {arg.docket_number}: {e}",
                          file=sys.stderr)

        records.append(record)

    return records


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", required=True, type=dt.date.fromisoformat,
                     help="Only include oral arguments on/after this date (YYYY-MM-DD)")
    ap.add_argument("--no-download", dest="download", action="store_false",
                     help="Skip downloading audio/PDF files (metadata only, fast)")
    ap.add_argument("--no-parse-pdf", dest="parse_pdf", action="store_false",
                     help="Skip splitting opinion PDFs into majority/concurrence/dissent sections")
    ap.add_argument("--out", type=Path, default=DATA_DIR / "cases.json")
    args = ap.parse_args()

    records = build(args.since, download=args.download, parse_pdf=args.parse_pdf)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} case records to {args.out}", file=sys.stderr)

    matched = sum(1 for r in records if r["opinion"])
    print(f"  ({matched} matched to a decided opinion, {len(records) - matched} still pending decision)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
