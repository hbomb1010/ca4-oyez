"""Parses the Fourth Circuit's opinions listings (a Sitefinity news list).

https://www.ca4.uscourts.gov/opinions/recent-opinions shows the last 30
days of opinions. Each entry is an <li class="sfnewsListItem"> shaped like:

    <li class="sfnewsListItem sflistitem">
        <h3 class="sfnewsTitle sftitle">252109.U Elshan Bayramov v. Jolene Wee</h3>
        <div class="sfnewsContent sfcontent">Unpublished opinion after submission on briefs</div>
        <div class="sfnewsContent sfcontent">
            <strong>Author: </strong>per curiam<br>
            <strong>Decision: </strong>Affirmed<br>
            <strong>Case Type: </strong>Bankruptcy-District Court<br>
            <strong>Appeal From: </strong>EDVA<br>
            <strong>Originating Judge: </strong>Hilton<br>
            <strong>Link: </strong><a href="https://www.ca4.uscourts.gov/opinions/252109.U.pdf">...</a>
        </div>
        <div class="sfnewsMetaInfo sfmetainfo">September 15, 2026</div>
    </li>

Days with nothing to report render as a placeholder item ("No Opinions of
the Court released on ...") with empty content divs -- those are skipped.

NOTE: "recent-opinions" only covers the trailing 30 days. For a full
backfill to an arbitrary start date, iterate /opinions/daily-opinions for
each date in range, or use /opinions/search-opinions (a full-text search
covering 1996-present) -- not implemented here yet; this module is enough
for ongoing incremental runs (run it at least monthly and nothing is
missed).
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import re

from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from . import http

RECENT_URL = "https://www.ca4.uscourts.gov/opinions/recent-opinions"

_TITLE_RE = re.compile(r"^(?P<opinion_no>\S+)\s+(?P<case_name>.+)$")


@dataclasses.dataclass
class Opinion:
    opinion_number: str  # e.g. "252109.U" or "247049.P"
    case_name: str
    published: bool
    after_argument: bool  # False => "submitted on briefs" (out of scope)
    author: str | None
    decision: str | None
    case_type: str | None
    appeal_from: str | None
    originating_judge: str | None
    pdf_url: str | None
    date_issued: dt.date | None


def _parse_detail_block(div) -> dict[str, str]:
    """Turns the <strong>Label: </strong>value<br>... block into a dict."""
    out: dict[str, str] = {}
    label = None
    for node in div.children:
        name = getattr(node, "name", None)
        if name == "strong":
            label = node.get_text(strip=True).rstrip(":")
        elif name == "a" and label:
            out[label] = node.get("href", "").strip()
            label = None
        elif name == "br":
            continue
        else:
            text = str(node).strip()
            if label and text:
                out[label] = text
                label = None
    return out


def _fetch_list(url: str) -> list[Opinion]:
    resp = http.get(url)
    soup = BeautifulSoup(resp.text, "lxml")

    results: list[Opinion] = []
    for li in soup.select("li.sfnewsListItem"):
        title = li.select_one("h3.sftitle")
        title_text = title.get_text(strip=True) if title else ""
        if title_text.startswith("No Opinion") or title_text.startswith("No Published"):
            continue

        m = _TITLE_RE.match(title_text)
        if not m:
            continue
        opinion_no = m.group("opinion_no")
        case_name = m.group("case_name")

        content_divs = li.select("div.sfcontent")
        type_line = content_divs[0].get_text(strip=True) if content_divs else ""
        details = _parse_detail_block(content_divs[1]) if len(content_divs) > 1 else {}

        meta = li.select_one("div.sfmetainfo")
        date_issued = None
        if meta:
            try:
                date_issued = dateparser.parse(meta.get_text(strip=True)).date()
            except (ValueError, OverflowError):
                pass

        results.append(
            Opinion(
                opinion_number=opinion_no,
                case_name=case_name,
                published=opinion_no.upper().endswith(".P"),
                after_argument="after argument" in type_line.lower(),
                author=details.get("Author"),
                decision=details.get("Decision"),
                case_type=details.get("Case Type"),
                appeal_from=details.get("Appeal From"),
                originating_judge=details.get("Originating Judge"),
                pdf_url=details.get("Link") or None,
                date_issued=date_issued,
            )
        )
    return results


def fetch_recent(*, since: dt.date | None = None) -> list[Opinion]:
    """Fetch the last-30-days opinions list, optionally filtered by date."""
    opinions = _fetch_list(RECENT_URL)
    if since:
        opinions = [o for o in opinions if o.date_issued and o.date_issued >= since]
    return opinions
