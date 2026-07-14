# Territory Radar

An automated **territory-intelligence tool for Account Executives**. It scores the accounts in a sales territory on real buying signals - hiring, funding, leadership moves, and expansion - and tracks which accounts are heating up over time, so account planning starts from "why now," not a static list.

**[→ Pick an industry on the live demo](https://eric-hastie.github.io/territory-radar/)**

> I prototyped this from my [remote-AE job-search tool](https://github.com/eric-hastie/remote-ae-job-hunt) - the same verify-and-track engine, re-pointed from finding jobs to finding buying signals. (Turns out the two problems are nearly identical under the hood.)

## What it does

- Scores each target account on a transparent, weighted signal model: open relevant roles, recent funding, new leadership, and expansion.
- Ranks the territory **Hot / Warm / Watch** with a "why now" outreach angle per account - exactly what I want in hand before I write a single line of outbound.
- Tracks **momentum** - the week-over-week change in each account's signal - so you can see who's accelerating. (The three new territories start fresh; momentum appears as weekly snapshots accumulate.)
- Re-scores the *same tool* through whatever ICP you sell - which is the whole point of the demo below.

## The demo: three industries, one engine

The landing page offers three demo territories of 20 real companies each. Click an industry box to open its ranked board, then click any account for the source behind its signals:

1. **[Cloud Data Warehousing](https://eric-hastie.github.io/territory-radar/data-warehouse/)** - run as if the vendor were MotherDuck. The ICP is midmarket companies hiring data engineers and analytics leadership, feeling warehouse cost pain.
2. **[Product Analytics](https://eric-hastie.github.io/territory-radar/product-analytics/)** - run as if the vendor were PostHog. The ICP is engineering-led software companies where the buyer is the builder.
3. **[Observability](https://eric-hastie.github.io/territory-radar/observability/)** - run as if the vendor were an unnamed observability platform. The ICP is midmarket companies with production infrastructure pain, where uptime is business risk.

Same companies sometimes appear on two boards with very different scores (Baseten, Supabase, Ramp) - that's the engine doing its job: the ICP changes, so the ranking changes.

**Illustrative demos only.** None of the vendors named is affiliated with or has endorsed this project. The companies, job postings, funding rounds, and leadership moves are real, verified July 13, 2026 against live ATS job boards (Greenhouse / Lever / Ashby) and public sources; the scoring and tiering are this tool's own. A live deployment runs against a real book of business in a **private** repo.

The original June-July 2026 demo board (a cloud infrastructure territory with four weeks of tracked momentum) is preserved at [legacy.html](https://eric-hastie.github.io/territory-radar/legacy.html), with its [history](https://eric-hastie.github.io/territory-radar/history.html) and [open-roles inventory](https://eric-hastie.github.io/territory-radar/roles.html).

## How it works

Each territory's accounts live in `data/territories/<slug>/latest.csv`, with dated snapshots (`YYYY-MM-DD.csv`) alongside for momentum. `build.py` recomputes every score and tier from the CSV signal columns, then generates the whole site in one pass: the landing page, the three territory boards, and the legacy pages. A weekly cloud agent re-verifies signals, rewrites the CSVs, snapshots them, runs `build.py`, and pushes - so the live demo stays current without me touching it during the week.

## Reconfigure for a new territory

Add an entry to the `TERRITORIES` list in `build.py` (industry, ICP, tier thresholds) and drop a `latest.csv` in `data/territories/<your-slug>/`. The page copy, scoring explainer, and landing card are all generated from that config.

---

*I'm Eric Hastie - an Account Executive who built this with AI pair-programming tools as a demonstration of GTM research, signal modeling, and workflow design.*
