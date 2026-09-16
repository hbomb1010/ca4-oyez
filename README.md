# CA4 Oyez

An Oyez.org-style site for the U.S. Court of Appeals for the Fourth Circuit,
scoped to oral arguments (and their associated opinions) from 2026 onward.

## Why / scope

Oyez covers SCOTUS: rich case pages with synced audio+transcript, editorial
"Facts of the Case" / "Question Presented" / "Conclusion" write-ups, opinion
text broken out by author, and a vote-breakdown visualization.

This project reproduces that *look and feel* for the Fourth Circuit, using
only cases with oral argument, starting 2026. It intentionally does **not**
attempt full case coverage (submitted-on-briefs cases are out of scope) or
Oyez's exact codebase/assets — just the genre of the experience.

## Data sources

| Data | Source | Notes |
|---|---|---|
| Oral argument list (date, docket #, case name, panel, counsel) | `ca4.uscourts.gov/oral-argument/oral-argument-audio-files` | One big sortable HTML table, audio posted next business day |
| Oral argument audio (MP3) | `ca4.uscourts.gov/OAarchive/mp3/{docket}-{YYYYMMDD}.mp3` | Predictable URL pattern, derived from the table |
| Opinions (disposition, author, published/unpublished, PDF) | `ca4.uscourts.gov/opinions/recent-opinions` and `/opinions/daily-opinions` | Also states whether a case was decided "after argument" vs "on briefs" — this is how we filter to argued cases |
| Opinion full text (majority/concurrence/dissent) | Parsed from the opinion PDF | No API — needs PDF text extraction + heuristics to split by opinion/author |
| Party briefs | **Not published by CA4.** Only on PACER (paid, per-page) or partially mirrored free on CourtListener/RECAP | Stretch goal, not in early phases |
| Oral argument transcript | **Does not exist.** CA4 has no official transcript service like SCOTUS | Out of scope for now (per project decision — audio-only player) |
| "Facts of the Case" / "Question" / "Conclusion" editorial prose | No source exists | Placeholder fields, to be hand-written per case later (per project decision) |

### Important: robots.txt

`ca4.uscourts.gov/robots.txt` explicitly disallows the `Claude-Web` and
`ClaudeBot` user agents site-wide. Claude (this assistant) does not run bulk
automated fetches against that site as a result — the `scraper/` tooling
below is meant to be run by you, from your own machine/identity, at a
reasonable rate. Claude can maintain and debug the scraper code, just not
be the one issuing the requests at scale.

## Repo layout

```
scraper/     Python tooling that pulls CA4 data into data/cases.json
data/        Normalized case records + downloaded PDFs/MP3s (gitignored, except a small sample)
web/         Next.js (TypeScript + Tailwind) frontend, styled after Oyez
```

## Roadmap

- **Phase 1 — Data pipeline (metadata only).** Scraper joins the oral
  argument table with the opinions listing on docket number, filters to
  argued (not submitted-on-briefs) cases from 2026 onward, downloads the
  opinion PDF, and writes one normalized JSON record per case. No audio or
  PDF parsing yet.
- **Phase 2 — Site shell with real data.** Next.js app: browse/list page
  (by argument date, like Oyez's term browsing) and a case detail page
  (parties, panel, dates, docket, disposition, embedded MP3 player, link to
  opinion PDF). Styled with an Oyez-like navy/gold theme.
- **Phase 3 — Opinion PDF parsing.** Extract majority/concurrence/dissent
  as separate readable sections with authors, instead of just linking the
  raw PDF.
- **Phase 4 — Editorial content.** Per-case "Facts of the Case" / "Question
  Presented" / "Conclusion" fields, hand-written, with a simple CMS-ish
  workflow (edit the JSON, or a tiny admin form) — not AI-generated, per
  project decision.
- **Phase 5 — Polish.** Search, browse-by-term, panel/judge index pages,
  deployment.
- **Stretch — Transcripts.** Whisper + speaker diarization on the MP3s, if
  wanted later.
- **Stretch — Briefs.** PACER or RECAP integration, per-case, opt-in given
  cost/coverage limits.

## Getting started

```bash
# 1. Run the scraper yourself (see scraper/README.md)
cd scraper
pip install -r requirements.txt
python build_dataset.py --since 2026-01-01

# 2. Run the site
cd ../web
npm install
npm run dev
```
