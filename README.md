# Territory Radar

An automated **territory-intelligence tool for Account Executives**. It scores the accounts in a sales territory on real buying signals - hiring, funding, leadership moves, and expansion - and tracks which accounts are heating up over time, so account planning starts from "why now," not a static list.

**[Pick an industry on the live demo](https://eric-hastie.github.io/territory-radar/)**

## What it does

- Scores each target account on a transparent, weighted signal model: open relevant roles, recent funding, new leadership, and expansion.
- Ranks the territory **Hot / Warm / Watch** with a "why now" outreach angle per account - exactly what I want in hand before I write a single line of outbound.
- Opens every board with a **Monday briefing**: a short narrative on what's moving in the territory and where I'd spend the first coffee.
- Tracks **momentum** - the week-over-week change in each account's signal - so you can see who's accelerating. (New territories start fresh; the briefing narrates the strongest live signals until a second weekly snapshot exists, then real movers take over automatically.)
- Re-scores the *same tool* through whatever ICP you sell - which is the whole point of the demo below.

## Why job postings?

Job postings are one of the cleanest, earliest intent signals in B2B - a company scaling its platform team or hiring an infra leader is telling you about budget and initiatives before any intent-data vendor flags it.

They're also a pain to actually use. Checking postings by hand across a whole territory - twenty accounts, twenty different job boards, every single week - is tedious, slow, and easy to let slide (I know, because I used to do it that way). Work that valuable and that repetitive is a perfect target for automation, so I automated it: the tool does the checking, and I get the ranked briefing.

## The demo: four industries, one engine

The landing page offers four demo territories of 20 real companies each - 80 accounts in all. Click an industry box to open its ranked board, then click any account for the source behind its signals:

1. **[Cloud Data Warehousing](https://eric-hastie.github.io/territory-radar/data-warehouse/)** - run as if selling a serverless cloud data warehouse. The ICP is midmarket companies hiring data engineers and analytics leadership, feeling warehouse cost pain.
2. **[Product Analytics](https://eric-hastie.github.io/territory-radar/product-analytics/)** - run as if selling a product analytics platform (analytics, session replay, feature flags, experiments). The ICP is engineering-led software companies where the buyer is the builder.
3. **[Observability](https://eric-hastie.github.io/territory-radar/observability/)** - run as if selling an observability platform (logs, metrics, traces, uptime). The ICP is midmarket companies with production infrastructure pain, where uptime is business risk.
4. **[Industrial Machine Health](https://eric-hastie.github.io/territory-radar/machine-health/)** - run as if the vendor were TRACTIAN (an illustrative demo, not affiliated with or endorsed by TRACTIAN). The ICP is mid-market manufacturers with multiple plants, real rotating equipment, and chronic maintenance-staffing pressure.

Same companies sometimes appear on two boards with very different scores (Baseten, Supabase, Ramp) - that's the engine doing its job: the ICP changes, so the ranking changes.

**Illustrative demos only.** Three boards run against unnamed hypothetical products; TRACTIAN is the only named vendor and is not affiliated with, and has not endorsed, this project. The companies, job postings, funding rounds, and leadership moves are real, verified July 13 and 14, 2026 against live ATS job boards (Greenhouse / Lever / Ashby / Workday and others) and public sources; the scoring and tiering are this tool's own. A live deployment runs against a real book of business in a **private** repo.

The original June-July 2026 demo board (a cloud infrastructure territory with weekly tracked momentum) is preserved at [legacy.html](https://eric-hastie.github.io/territory-radar/legacy.html), with its [history](https://eric-hastie.github.io/territory-radar/history.html) and [open-roles inventory](https://eric-hastie.github.io/territory-radar/roles.html).

## How it works

Each territory's accounts live in `data/territories/<slug>/latest.csv`, with dated snapshots (`YYYY-MM-DD.csv`) alongside for momentum. `build.py` recomputes every score and tier from the CSV signal columns, then generates the whole site in one pass: the landing page, the four territory boards, and the legacy pages. A weekly cloud agent re-verifies signals, rewrites the CSVs, snapshots them, runs `build.py`, and pushes - so the live demo stays current without me touching it during the week.

## Reconfigure for a new territory

Add an entry to the `TERRITORIES` list in `build.py` (industry, ICP, tier thresholds) and drop a `latest.csv` in `data/territories/<your-slug>/`. The page copy, scoring explainer, and landing card are all generated from that config.

---

*I'm Eric Hastie - an Account Executive who built this with AI pair-programming tools as a demonstration of GTM research, signal modeling, and workflow design.*
