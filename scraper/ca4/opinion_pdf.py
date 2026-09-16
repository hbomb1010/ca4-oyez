"""Best-effort splitter for a CA4 opinion PDF into majority/concurrence/
dissent sections, mimicking Oyez's "Opinion of the Court" / "Concurring
Opinion" / "Dissenting Opinion" breakdown.

CA4 opinions don't have a machine-readable structure -- this uses text
heuristics against the convention of a Circuit Judge's surname (in caps)
introducing their opinion, e.g.:

    WYNN, Circuit Judge:
    ...majority text...

    THACKER, Circuit Judge, dissenting:
    ...dissent text...

This is approximate. Treat it as a first draft to hand-review, not ground
truth -- flag anything user-facing as parsed/unverified if you skip review.
"""
from __future__ import annotations

import dataclasses
import re
from pathlib import Path

import pdfplumber

# Matches the mixed-case "Circuit Judge" / "District Judge" that actually
# appears in CA4 opinion text, while the name itself stays a strict
# all-caps match (real headings look like "WYNN, Circuit Judge:") so we
# don't false-match ordinary sentence-case prose.
_JUDGE_HEADING_RE = re.compile(
    r"^(?P<name>[A-Z][A-Z.,'\- ]{2,40}?),\s*"
    r"(?:[Ss]enior\s+|[Cc]hief\s+)?(?:[Cc]ircuit|[Dd]istrict)\s+[Jj]udge"
    r"(?P<qualifier>[^:]*):?\s*$"
)

_PER_CURIAM_RE = re.compile(r"^PER\s+CURIAM:?\s*$")


@dataclasses.dataclass
class OpinionSection:
    author: str
    kind: str  # "majority" | "concurrence" | "dissent" | "concurrence/dissent"
    text: str


def _classify(qualifier: str) -> str:
    q = qualifier.lower()
    has_concur = "concur" in q
    has_dissent = "dissent" in q
    if has_concur and has_dissent:
        return "concurrence/dissent"
    if has_dissent:
        return "dissent"
    if has_concur:
        return "concurrence"
    return "majority"


def extract_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def split_sections(full_text: str) -> list[OpinionSection]:
    lines = full_text.splitlines()
    headings: list[tuple[int, str, str]] = []  # (line_idx, author, kind)

    for i, line in enumerate(lines):
        stripped = line.strip()
        m = _JUDGE_HEADING_RE.match(stripped)
        if m:
            headings.append((i, m.group("name").title(), _classify(m.group("qualifier"))))
            continue
        if _PER_CURIAM_RE.match(stripped):
            headings.append((i, "Per Curiam", "majority"))

    if not headings:
        return [OpinionSection(author="Unknown", kind="majority", text=full_text.strip())]

    sections: list[OpinionSection] = []
    for idx, (line_no, author, kind) in enumerate(headings):
        end = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
        body = "\n".join(lines[line_no + 1 : end]).strip()
        if body:
            sections.append(OpinionSection(author=author, kind=kind, text=body))
    return sections


def parse(pdf_path: Path) -> list[OpinionSection]:
    return split_sections(extract_text(pdf_path))
