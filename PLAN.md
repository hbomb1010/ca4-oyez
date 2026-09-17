# CA4 Oyez — Project Plan

This replaces the "phases" section of the root README with something more
granular: each phase below is sized to be finishable in one sitting by
someone who isn't an experienced developer. Do them in order — later
phases assume earlier ones are done. Check boxes off as you go; re-run
`git log` / re-read this file any time you need to remember where you are.

## Current status (as of this plan)

Already built, in this repo:
- `scraper/` — Python tooling that can pull CA4's oral argument table and
  opinions listing, join them, and download audio/PDFs. **Not yet run for
  real** — only a hand-written sample dataset exists so far
  (`data/cases.sample.json`).
- `web/` — a Next.js site styled after Oyez (case list + case detail page
  with audio player), currently reading the sample data. Builds and runs
  successfully.
- One git commit. No feed, no artwork, no deployment, no judge pages yet.

Two standing constraints from earlier research, still true for every
phase below:
- **ca4.uscourts.gov's `robots.txt` disallows Claude's own crawlers.** Any
  scraping of that site happens from scripts *you* run yourself, not as
  an automated Claude action. Claude can keep writing/debugging the
  scraper code.
- **No party briefs or official transcripts exist for free** from CA4.
  Those stay out of scope until the stretch phases at the end, if ever.

---

## Part 1 — An excellent podcast feed

The goal of Part 1 is narrow on purpose: end up with a real RSS feed you
can follow in Apple Podcasts, with a thumbnail, that updates itself. No
web UI work happens in this part.

### Phase 1 — Baseline check & first real data pull
**Goal:** confirm what's already built actually works, and get one real
batch of scraped data on disk.
- [x] Put your real name/contact info into `USER_AGENT` in `scraper/ca4/http.py`
      (used a generic, non-personal project identifier instead — see commit history)
- [x] ~~`cd scraper && source .venv/bin/activate`~~ — superseded: runs happen via
      the `.github/workflows/refresh-data.yml` GitHub Action now, not locally
      (see "Open TODOs" below for why)
- [x] Run `python build_dataset.py --since 2026-01-01 --no-download` (fast, metadata only)
      — 217 arguments, 14 matched to a decided opinion
- [x] Read the printed summary line — does the "matched to a decided opinion" count look plausible? — yes
- [x] Open `data/cases.json` and skim 10 random records for obviously wrong joins (mismatched case names, wrong dates) — clean
- [x] Re-run for a **small** recent window (e.g. `--since` two weeks ago), this time *without* `--no-download`, to confirm audio + PDF downloads actually work
      — 20 arguments since 2026-09-02, all 20 downloaded audio successfully
- [x] Note anything broken as a TODO at the bottom of this file — don't fix scraper bugs yet unless they block reading the data at all — nothing broken

**Done when:** `data/cases.json` has real, plausible 2026 case records on your machine.

### Phase 2 — Decide the show's identity
**Goal:** make the handful of naming/scope decisions that every later
phase depends on, before writing code.
- [x] Pick a show title (e.g. "Fourth Circuit Oral Arguments") — "4thCir?Oyez"
- [x] Write a one-paragraph show description
- [x] Pick an episode title format (e.g. `No. 26-1234 — Appellant v. Appellee`)
      — `Appellant v. Appellee (No. 26-1234)`
- [x] Pick what goes in an episode's description (docket #, panel, counsel, argument date — pull straight from `cases.json`)
      — all four
- [x] Decide: **private feed you follow by URL**, or do you eventually want it **submitted to Apple's public podcast directory**? (Private is far less work — directory submission needs ownership verification and Apple review. Recommendation: start private; revisit later if you want it discoverable by strangers.)
      — private for now
- [x] Write these decisions down in a `docs/podcast-notes.md` file (a few lines is enough)

**Done when:** the decisions exist in writing. Nothing to run or test yet.

### Phase 3 — Make the show artwork (thumbnail)
**Goal:** a cover image that meets Apple's spec — Apple Podcasts rejects
feeds with invalid artwork, so this has to happen before the feed can be
validated.
- [x] Confirm the spec: JPEG or PNG, RGB color space, **square**, between 1400×1400 and 3000×3000 px
- [x] Design something simple — used a real photo of the Lewis F. Powell
      Jr. U.S. Courthouse (CA4's home in Richmond), user-supplied
- [x] Export at exactly a valid square size — **1400×1400, not 3000×3000**:
      the source photo was only 1536×1024, so cropping to a 1024×1024
      square and upscaling to the 1400 minimum (instead of 3000) keeps
      the upscale factor small and avoids visible softness
- [x] Save it as `assets/artwork/cover-1400.jpg` in the repo (renamed
      from the plan's `cover-3000.jpg` to reflect the actual size)
- [x] Look at it at thumbnail size — reads well at ~200px (typical
      podcast-library tile size); degrades to a nonspecific blob at true
      icon scale (~60px). Accepted as a known tradeoff of photographic
      artwork vs. a simpler graphic/typographic cover.

**Done when:** you have one artwork file you're happy with, at a valid size.

### Phase 4 — Write the feed generator
**Goal:** a script that turns `data/cases.json` into a valid podcast RSS file.
- [ ] Add `feedgen` to `scraper/requirements.txt` and install it (much less error-prone than hand-writing podcast XML)
- [ ] Write `scraper/build_feed.py`: reads `data/cases.json`, writes `data/feed.xml`
- [ ] Set channel-level fields: title, description, link, language, `itunes:image` (your Phase 3 artwork, hosted — see Phase 6), `itunes:category`, `itunes:explicit`, `itunes:author`
- [ ] For each case that has audio, add an episode: title, description, enclosure (audio URL, byte length, `audio/mpeg`), a stable `guid` (use the docket number), `pubDate` (argument date)
- [ ] Decision: enclosures point straight at `ca4.uscourts.gov`'s own mp3 URLs for now (simplest — no re-hosting needed). Revisit in the stretch phases if you want your own copies.
- [ ] Get each enclosure's byte size — either from the file if you downloaded it in Phase 1, or an HTTP HEAD request otherwise
- [ ] Run it, open `data/feed.xml`, read through it like a human

**Done when:** `data/feed.xml` exists and looks like a real podcast feed.

### Phase 5 — Validate the feed
**Goal:** catch problems before you waste time on hosting/subscribing.
- [ ] Run `data/feed.xml` through a free podcast RSS validator (e.g. Cast Feed Validator, or podba.se)
- [ ] Fix everything it flags as an error (warnings are more optional)
- [ ] Double-check every episode has a working, direct audio URL (open a couple in a browser — they should start downloading/playing, not show an error page)

**Done when:** the validator reports no errors.

### Phase 6 — Host the feed publicly
**Goal:** a stable HTTPS URL Apple Podcasts can fetch. (Only the feed
file + artwork need hosting here — audio still lives on ca4.uscourts.gov.)
- [ ] Enable GitHub Pages on this repo (simplest option — free, no server to manage), serving a `/docs` folder or a `gh-pages` branch
- [ ] Copy `data/feed.xml` and `assets/artwork/cover-1400.jpg` into that published folder
- [ ] Push, then open the resulting URL in a plain browser tab and confirm it loads
- [ ] Make sure the `itunes:image` URL inside feed.xml points at the *published* artwork URL, not a local path

**Done when:** you have a real public URL like `https://<you>.github.io/ca4-oyez/feed.xml` that loads in a browser.

### Phase 7 — Subscribe in Apple Podcasts
**Goal:** the actual payoff moment for Part 1.
- [ ] Open the Podcasts app (iPhone or Mac)
- [ ] Use "Library → Follow a Show by URL" and paste your feed URL
- [ ] Confirm the show shows up with your title and artwork
- [ ] Confirm at least one episode downloads and plays
- [ ] Try the same URL on a second device (or send it to someone else) to confirm it's genuinely public, not just something cached locally

**Done when:** an episode has played, from your own feed, in real Apple Podcasts.

### Phase 8 — Automate the refresh
**Goal:** new arguments should show up on their own — no more manually re-running scripts.
- [ ] Write one shell script that: activates the venv → runs `build_dataset.py` → runs `build_feed.py` → copies the updated `feed.xml` into the GitHub Pages folder → commits and pushes
- [ ] Decide a cadence (daily is reasonable — matches how often CA4 posts audio)
- [ ] Set it up to actually run on that cadence (a `launchd`/cron job on your Mac, or a scheduled GitHub Action if you want it to run even when your computer is off)
- [ ] Run it manually once, end to end, to confirm nothing breaks
- [ ] Wait a few days and confirm a new episode actually appears in Apple Podcasts without you touching anything

**Done when:** you've watched at least one new episode appear automatically. **Part 1 is complete.**

---

## Part 2 — An excellent web UI

Builds on the existing `web/` scaffold, now with real data behind it.

### Phase 9 — Get the real site running on real data
- [ ] `cd web && npm run dev`, browse the list with real `data/cases.json` instead of the sample
- [ ] Fix whatever real data breaks that sample data didn't (missing fields, long counsel lists, unusual case names, cases with no opinion yet)
- [ ] Spot-check 5+ case detail pages against the actual CA4 listings to make sure the case-name join didn't mismatch anything

**Done when:** real cases browse and open cleanly, no obvious bugs.

### Phase 10 — Visual design pass
- [ ] Sit with oyez.org open side by side; write down 3–5 specific things about its feel you want here (typography, spacing, color use, player styling, hover states)
- [ ] Adjust theme/typography/spacing in `web/src/app/globals.css` and the page components to match your notes
- [ ] Give the home page a real header/hero treatment instead of a plain list
- [ ] Polish the case detail page layout — it's the page people actually spend time on
- [ ] Resize your browser to phone width and fix anything that breaks

**Done when:** you'd be proud to send someone the link.

### Phase 11 — Judge profile pages, with photos
- [ ] Investigate ca4.uscourts.gov's "Judges" section: URL structure, whether each judge has a bio page with an official photo (reminder: this is a step *you* run, per the robots.txt note at the top)
- [ ] Write a small scraper pulling each active judge's name/photo/short bio into `data/judges.json`
- [ ] Add a `/judges/[name]` route showing the photo, bio, and every case they sat on (cross-reference the `panel` field in `cases.json`)
- [ ] Link judge names everywhere they appear (case list, case detail) to their profile page

**Done when:** clicking any judge's name anywhere on the site opens a real profile page with their photo.

### Phase 12 — Better opinion parsing
- [ ] Run `ca4/opinion_pdf.py` against 10–15 real downloaded opinion PDFs; read the output by hand
- [ ] Write down every pattern it gets wrong (per curiam edge cases, multi-author concurrences, footnote/header noise, etc.)
- [ ] Improve the heuristics in `opinion_pdf.py` to handle what you found
- [ ] Re-run and re-check

**Done when:** you trust the parsed majority/concurrence/dissent sections enough to show them without a "PDF only" disclaimer on most cases.

### Phase 13 — Editorial content workflow
- [ ] Decide how you'll actually write "Facts of the Case" / "Question Presented" / "Conclusion" per case — editing `cases.json` directly is fine to start; a tiny local form is a nice-to-have if that gets tedious
- [ ] Hand-write real content for 3–5 cases you find interesting, as a trial run
- [ ] Confirm it renders well on the case detail page

**Done when:** a handful of your most interesting recent cases have real, hand-written write-ups.

### Phase 14 — Search & browse
- [ ] Add a text search box (case name / docket number) on the home page
- [ ] Add filters: by month/term, by disposition, by judge
- [ ] Add pagination or infinite scroll once the list is long enough to need it

**Done when:** you can find any specific case in a few seconds without scrolling.

### Phase 15 — Deployment
- [ ] Connect the `web/` app to Vercel (or similar) via your GitHub repo
- [ ] Pick a domain (a free `*.vercel.app` subdomain is fine to start)
- [ ] Move the podcast feed (Part 1) onto the same deployment as a `/feed.xml` route, so there's one canonical home instead of GitHub Pages + Vercel
- [ ] Update your Apple Podcasts subscription to the new feed URL if it moved
- [ ] Wire the Phase 8 automation to also trigger a redeploy when data updates

**Done when:** you can send anyone a real URL and they see the live site.

### Phase 16 — Polish & accessibility pass
- [ ] Keyboard navigation and screen-reader labels on the audio player and nav
- [ ] Loading/empty/error states (a case with no audio yet, a broken PDF link)
- [ ] Basic SEO (real page titles, meta descriptions per case)
- [ ] Run Lighthouse on the case list and a case detail page; fix what it flags

**Done when:** Lighthouse looks solid and nothing feels broken when you poke at edge cases.

---

## Stretch phases (optional, no pressure, in rough priority order)

- [ ] **Phase 17 — Self-hosted audio.** Copy audio into your own object storage (e.g. Cloudflare R2) instead of depending on CA4's URLs forever; lets you fix filenames/tags.
- [ ] **Phase 18 — Historical backfill.** `ca4/opinions.py` currently only sees the trailing 30 days; add a path through `/opinions/daily-opinions` or the full-text search tool to backfill opinions for cases argued earlier in 2026.
- [ ] **Phase 19 — Transcripts.** Whisper + speaker diarization on the audio, with a synced transcript player like Oyez's.
- [ ] **Phase 20 — Briefs.** PACER (paid) or RECAP/CourtListener (free, partial coverage) integration, per case, opt-in.
- [ ] **Phase 21 — Public podcast directory submission.** If Phase 2 chose "private" and you change your mind later: ownership verification, Apple Podcasts Connect submission, review wait.

---

## Open TODOs found along the way

(Add anything you notice during a phase that isn't worth stopping for right now.)

- Data pulls now run via `.github/workflows/refresh-data.yml` (manual
  "Run workflow" button on GitHub, not a local terminal command) — pulled
  Phase 8's automation idea forward early since the user prefers not to
  use the terminal. Still respects the "don't scrape as an automated
  Claude action" boundary: it's a human click triggering a job on GitHub's
  runners, not Claude's own crawler. Revisit Phase 8 to add a schedule
  (e.g. daily cron trigger) instead of manual-only.
-
