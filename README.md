# Territory Radar

An automated **territory-intelligence tool for Account Executives**. It scores the accounts in a sales territory on real buying signals - hiring, funding, and leadership moves - and tracks which accounts are heating up over time, so account planning starts from "why now," not a static list.

**[→ View the live demo](https://eric-hastie.github.io/territory-radar/)**

> Prototyped from a [remote-AE job-search tool](https://github.com/eric-hastie/remote-ae-job-hunt) - the same verify-and-track engine, re-pointed from finding jobs to finding buying signals.

## What it does

- Scores each target account on a transparent, weighted signal model: open relevant roles, recent funding, new engineering leadership, and expansion.
- Ranks the territory **Hot / Warm / Watch** with a "why now" outreach angle per account.
- Tracks **momentum** - the week-over-week change in each account's signal, plus total open roles across the territory - so you can see who's accelerating.
- Keeps a **full open-roles inventory** you can scan to tune the signal profile (spot titles that should count but don't).

## The demo

Models an AE selling a cloud infrastructure / DevOps platform, so a buying signal = an account investing in its platform/infra org (hiring SRE / platform / DevOps engineers, raising capital, new eng leadership). The sample territory is 16 real mid-market/enterprise companies with signals verified against their ATS and public sources. This is illustrative demo data - a live deployment runs against a real book of business in a **private** repo.

## How it works

`data/latest.csv` (accounts) and `data/roles-latest.csv` (open-roles inventory) drive `build.py`, which computes scores, tiers, and momentum, then generates the site: the territory board (`index.html`), momentum/history (`history.html`), and the open-roles inventory (`roles.html`). A weekly cloud agent re-verifies signals, rescans, writes a dated snapshot, rebuilds, and pushes - so the live demo and its history stay current automatically.

## Reconfigure for a new role

Edit the `CONFIG` block in `build.py` (what you sell + signal weights) and point the weekly routine at your real account list. The page copy, scoring, and explainer all read from `CONFIG`.

---

*Built by Eric Hastie as a demonstration of GTM research, signal modeling, and AI-assisted workflow design.*
