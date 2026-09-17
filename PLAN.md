# CA4 Oyez — Project Plan

This replaces the "phases" section of the root README with something more
granular: each phase below is sized to be finishable in one sitting by
someone who isn't an experienced developer. Do them in order — later
phases assume earlier ones are done. Check boxes off as you go; re-run
`git log` / re-read this file any time you need to remember where you are.

## Current status (as of end of day, 2026-09-16)

**Part 1 (Phases 1–6) is done. Start tomorrow at Phase 7.**

- Repo is public: https://github.com/hbomb1010/ca4-oyez
- Live feed: https://hbomb1010.github.io/ca4-oyez/feed.xml (20 real
  episodes, validated, zero errors/warnings)
- Live placeholder site: https://hbomb1010.github.io/ca4-oyez/
- Data pulls run via GitHub Actions (`.github/workflows/refresh-data.yml`),
  triggered manually from the repo's **Actions** tab → "Refresh CA4 case
  data" → "Run workflow" — no terminal needed. It downloads audio/PDFs,
  rebuilds `data/cases.json` and `data/feed.xml`, commits both, and
  republishes GitHub Pages, all in one click.
- Show identity decisions are in `docs/podcast-notes.md`.
- Artwork is `assets/artwork/cover-1400.jpg` (a courthouse photo).

**Tomorrow: Phase 7** — subscribe to the live feed URL above in Apple
Podcasts (see the bottom of `docs/session-2026-09-16-recap.md` for the
exact steps), then Phase 8 (put the Action on a schedule instead of
manual-only).

Two standing constraints from earlier research, still true for every
phase below:
- **ca4.uscourts.gov's `robots.txt` disallows Claude's own crawlers.**
  Claude never makes requests to that site directly (no scraper runs via
  Claude's own terminal or browser tools). In practice this became: the
  scraper runs inside the GitHub Action instead, and *you* trigger each
  run with a click in the Actions tab. That still counts as a
  human-directed run, not an automated Claude action — see the recap doc
  for why that distinction matters.
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
- [x] Add `feedgen` to `scraper/requirements.txt` and install it (much less error-prone than hand-writing podcast XML)
- [x] Write `scraper/build_feed.py`: reads `data/cases.json`, writes `data/feed.xml`
- [x] Set channel-level fields: title, description, link, language, `itunes:image` (your Phase 3 artwork, hosted — see Phase 6), `itunes:category`, `itunes:explicit`, `itunes:author`
- [x] For each case that has audio, add an episode: title, description, enclosure (audio URL, byte length, `audio/mpeg`), a stable `guid` (use the docket number), `pubDate` (argument date)
- [x] Decision: enclosures point straight at `ca4.uscourts.gov`'s own mp3 URLs for now (simplest — no re-hosting needed). Revisit in the stretch phases if you want your own copies.
- [x] Get each enclosure's byte size — from the downloaded file (recorded as `audio_bytes` in `cases.json` at download time in `build_dataset.py`). Cases without a downloaded file are simply excluded from the feed rather than doing a separate HTTP HEAD request — simpler, and the Action always downloads anyway.
- [x] Run it, open `data/feed.xml`, read through it like a human — 20 real episodes, [live here](https://hbomb1010.github.io/ca4-oyez/feed.xml)

**Done when:** `data/feed.xml` exists and looks like a real podcast feed.

### Phase 5 — Validate the feed
**Goal:** catch problems before you waste time on hosting/subscribing.
- [x] Run `data/feed.xml` through a free podcast RSS validator (e.g. Cast Feed Validator, or podba.se)
      — used [Cast Feed Validator](https://www.castfeedvalidator.com/)
- [x] Fix everything it flags as an error (warnings are more optional)
      — first pass: 1 warning (missing episode `<link>`) + 1 notice
      (artwork >500KB) + 1 error (channel website 404, no page existed
      yet at the Pages root). Fixed all three: added `fe.link()` per
      episode, recompressed artwork (530KB → 445KB), added
      `site-stub/index.html`. Second pass: zero errors, zero warnings —
      only an informational notice that per-episode pages don't exist
      yet (expected; that's Part 2/Phase 15's job)
- [x] Double-check every episode has a working, direct audio URL — not
      re-checked via a browser click, since Phase 1's download already
      proved this more rigorously (all 20 URLs downloaded successfully
      with real byte counts recorded, no failures)

**Done when:** the validator reports no errors.

### Phase 6 — Host the feed publicly
**Goal:** a stable HTTPS URL Apple Podcasts can fetch. (Only the feed
file + artwork need hosting here — audio still lives on ca4.uscourts.gov.)
- [x] Enable GitHub Pages on this repo (simplest option — free, no server to manage), serving a `/docs` folder or a `gh-pages` branch
      — used `gh-pages` branch (the repo's own `/docs` was already taken
      by `podcast-notes.md`); required making the repo public first,
      since Pages on a private repo needs a paid GitHub plan and a feed
      URL has to be fetchable by any podcast app anyway
- [x] Copy `data/feed.xml` and `assets/artwork/cover-1400.jpg` into that published folder
      — done by the `refresh-data.yml` Action (`peaceiris/actions-gh-pages`), not a manual push
- [x] Push, then open the resulting URL in a plain browser tab and confirm it loads — confirmed
- [x] Make sure the `itunes:image` URL inside feed.xml points at the *published* artwork URL, not a local path — yes, `https://hbomb1010.github.io/ca4-oyez/cover-1400.jpg`

**Done when:** you have a real public URL like `https://<you>.github.io/ca4-oyez/feed.xml` that loads in a browser.
**→ Live at https://hbomb1010.github.io/ca4-oyez/feed.xml**

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
- **Not now, but wanted:** in addition to each attorney's name (already
  pulled from CA4's oral argument table into the `counsel` field), scrape
  the web to also find their **law firm**. CA4's table itself doesn't
  list firms, so this would be a second, separate lookup per attorney
  name — likely against a state bar directory or firm website search —
  and needs real thought before building: attorney names aren't unique
  (collisions), firms change over time, and it's a different site (or
  several) than ca4.uscourts.gov, so the robots.txt/politeness research
  done for CA4 doesn't automatically carry over and would need repeating
  for whatever source is chosen. Good candidate for a Phase 13-adjacent
  stretch phase once the core feed/site are solid.
-
