# scraper

Pulls Fourth Circuit oral argument + opinion data into `../data/cases.json`
(plus downloaded PDFs/MP3s under `../data/files/`).

**Run this yourself**, not as an automated agent action — see the root
README's note on `ca4.uscourts.gov`'s `robots.txt`, which disallows
Claude's crawlers site-wide. Nothing here is technically restricted for a
human-directed script, but be a polite scraper:

- The included `http.py` helper rate-limits requests (1 per ~2s by default)
  and sends a descriptive `User-Agent` with contact info — **edit
  `USER_AGENT` in `http.py` to put your own contact info in it** before
  running this against the live site.
- Don't parallelize requests against ca4.uscourts.gov.
- Cache aggressively (the scripts already skip re-downloading files that
  exist on disk) so re-runs don't re-fetch everything.

## Usage

```bash
pip install -r requirements.txt

# Pulls both source tables, joins them, filters to argued cases since the
# given date, downloads opinion PDFs and oral argument MP3s, and writes
# data/cases.json
python build_dataset.py --since 2026-01-01
```

Run it again later (e.g. via cron/launchd) to pick up newly argued/decided
cases — it's incremental.

## Files

- `ca4/oral_arguments.py` — parses the Oral Argument Audio Files table
- `ca4/opinions.py` — parses the Recent/Daily Opinions listings
- `ca4/opinion_pdf.py` — splits an opinion PDF into majority/concurrence/
  dissent sections by author (best-effort text heuristics; not perfect,
  hand-check important ones)
- `ca4/http.py` — polite `requests` wrapper (rate limiting, UA, on-disk
  cache for downloaded files)
- `build_dataset.py` — CLI entry point that ties it all together
