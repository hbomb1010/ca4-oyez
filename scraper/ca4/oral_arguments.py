"""Parses the Fourth Circuit's Oral Argument Audio Files page.

That page (https://www.ca4.uscourts.gov/oral-argument/oral-argument-audio-files)
is a single ASP.NET GridView table (id ...GridView1) with every argued case
back to May 2011 -- no pagination, one GET returns everything (~5,000+ rows
as of 2026), so we fetch once and filter client-side.

Row shape (confirmed by inspecting the live DOM):

    <tr>
        <td>9/15/2026</td>
        <td><a href="../OAarchive/mp3/25-1464-20260915.mp3">25-1464</a></td>
        <td>Felix Mejia-Rodriguez v. Todd Blanche</td>
        <td>J. Harvie Wilkinson III, James Andrew Wynn, Nicole G. Berner</td>
        <td>Jennifer Bibby-Gerth, Anna Juarez</td>
    </tr>
"""
from __future__ import annotations

import dataclasses
import datetime as dt
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from . import http

URL = "https://www.ca4.uscourts.gov/oral-argument/oral-argument-audio-files"


@dataclasses.dataclass
class OralArgument:
    argument_date: dt.date
    docket_number: str
    case_name: str
    panel: list[str]
    counsel: list[str]
    audio_url: str


def _split_names(cell_text: str) -> list[str]:
    return [n.strip() for n in cell_text.split(",") if n.strip()]


def fetch(*, since: dt.date | None = None) -> list[OralArgument]:
    """Fetch and parse the full oral argument table.

    `since` filters to arguments on or after that date (recommended --
    the table covers 2011-present and is large).
    """
    resp = http.get(URL)
    soup = BeautifulSoup(resp.text, "lxml")

    table = soup.find("th", string=lambda s: s and "Argument Date" in s)
    table = table.find_parent("table") if table else soup.find("table")
    if table is None:
        raise RuntimeError("Could not find the oral argument table -- page layout may have changed")

    rows = table.find_all("tr")[1:]  # skip header row
    results: list[OralArgument] = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        date_text, case_num_cell, name_text, panel_text, counsel_text = cells[:5]

        try:
            argument_date = dt.datetime.strptime(date_text.get_text(strip=True), "%m/%d/%Y").date()
        except ValueError:
            continue

        if since and argument_date < since:
            continue

        link = case_num_cell.find("a")
        docket_number = case_num_cell.get_text(strip=True)
        audio_url = urljoin(URL, link["href"]) if link and link.get("href") else ""

        results.append(
            OralArgument(
                argument_date=argument_date,
                docket_number=docket_number,
                case_name=name_text.get_text(strip=True),
                panel=_split_names(panel_text.get_text()),
                counsel=_split_names(counsel_text.get_text()),
                audio_url=audio_url,
            )
        )
    return results
