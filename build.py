#!/usr/bin/env python3
"""Regenerate the Territory Radar site: landing page + five demo territory
boards + the original (legacy) demo board, all in the "Monday briefing" look.

Site layout:
  index.html                    - landing page: pick an industry
  data-warehouse/index.html     - Cloud Data Warehousing board (unnamed vendor)
  product-analytics/index.html  - Product Analytics board (unnamed vendor)
  observability/index.html      - Observability board (unnamed vendor)
  machine-health/index.html     - Industrial Machine Health board (run as if the
                                  vendor were TRACTIAN; illustrative, not affiliated)
  test-automation/index.html    - Software Test Automation board (run as if the
                                  vendor were ContextQA; illustrative, not affiliated)
  legacy.html                   - the original demo board (June-July 2026)
  history.html / roles.html     - momentum + open-roles inventory for the legacy board

Inputs:
  data/territories/<slug>/latest.csv     - current account rows for each territory
  data/territories/<slug>/YYYY-MM-DD.csv - weekly snapshots of latest.csv (momentum)
  data/latest.csv                        - legacy board accounts
  data/roles-latest.csv                  - legacy open-roles inventory
  data/YYYY-MM-DD.csv                    - legacy weekly snapshots

No third-party dependencies. Scores and tiers are always recomputed at build
time from the CSV signal columns, so the CSVs are the single source of truth.
Each board opens with a Monday-briefing narrative: once a territory has two or
more dated snapshots it spotlights the biggest week-over-week movers; until
then it spotlights the strongest live signals (an honest first-snapshot mode).
The "Happy <day>!" greeting uses the build date's actual day of week.

--- WEEKLY CLOUD REFRESH ROUTINE (what the weekly agent should do) ---
1. For each of the five territory folders in data/territories/ (any or all):
   re-verify every account's signals against its live ATS job board and
   public sources, rewrite latest.csv in the same column schema, and save an
   identical copy as YYYY-MM-DD.csv (today's date) in the same folder - the
   dated snapshots are what power the momentum column and the movers briefing.
   Some territories (test-automation) carry extra trailing "Est Devs" and
   "Est Testers" columns (rough estimated developer / dedicated-QA counts)
   and use an estimated RANGE like "200-500" in Headcount - keep all of
   these when rewriting, refresh only on real evidence. New accounts get
   both estimates researched at add-time (LinkedIn title sampling, req
   history as a floor, industry priors: modern SaaS ~10-15 devs per tester,
   regulated/enterprise ~5-8; sample offshore hubs too) - record the full
   estimate in ratio_research.csv (Account, Est Testers, Testers Range,
   Est Devs, Ratio, Confidence, Evidence) in the same folder. build.py
   computes the dev:tester ratio and applies the coverage-gap score boost
   (>=12:1 +10, >=8:1 +5) and the >=12:1 messaging flag automatically.
1b. ACTION QUEUE - if the folder has an outreach.csv, maintain it:
   - PRESERVE the Status and Notes columns exactly as found; they are the
     AE's working state, not generated data. Only the AE (or an explicit
     instruction) moves an account between statuses. Status values are
     ONLY: To contact / Contacted / Replied / Meeting / Hold / Not
     started. A tier (Hot/Warm/Watch) is NEVER a status - when an
     account changes tier, Status stays untouched (2026-07-21 the
     weekly agent wrote "Hot" into Alarm.com's Status and its sequences
     vanished from the queue page).
   - Refresh each account's Angle if its signals materially changed.
   - Message content lives in sequences.csv (Account, Level, Email
     Subject, Email Body, Second Touch Email, Third Touch Email, Fourth
     Touch Email, LinkedIn Note): THREE rows per drafted account, Level =
     Executive | Director | BTL, so the message matches the buyer's
     altitude. Fourth Touch Email is EXECUTIVE-ONLY (blank on
     Director/BTL rows - they run three touches).
       Executive: CTO / VP Eng - business outcomes, release risk,
       headcount economics; under ~80 words; no tool lists.
       Director: Dir QA / Dir Eng / EM - operational: coverage, cycle
       time, team leverage, the tooling decision.
       BTL: QA leads / SDETs - peer-to-peer, names the account's actual
       stack from roles.csv, empathizes with script maintenance and
       flake, champion-building tone, extra-low-friction CTA.
   - Any account that is (or newly became) Hot and has no sequences gets
     all three levels written, status To contact.
     TOUCH FORMATS BY LEVEL:
     Executive T1 (spec v3.1, 2026-07-20 - supersedes all earlier exec
       formats): opens "[First] - "; TIGHT (40-65 words incl. CTA);
       STRICTLY what we know or can imply about the business and the
       risk it faces (velocity risk, bug risk with low test coverage) -
       and every risk statement is followed by its impact / negative
       consequence, never left hanging; ZERO ContextQA mention; zero
       product detail. ATL RULE (Skip Miller, Selling Above and Below
       the Line): DUMB IT DOWN for executives - every line must make
       sense to someone who never worked in engineering; say "bugs"
       never "regressions", state consequences as customers / revenue /
       risk, no process language ("bug ticket", "shows up in the
       quarter" = too deep / awkward). CTA = a thoughtful tailored
       question offering the tool-vs-headcount choice, e.g. "Have you
       considered solving with a tool instead of adding headcount?" /
       "Open to AI tooling to close that gap, or committed to hiring
       your way there?" / "Do you have a plan in the meantime, or is
       everything on hold until that seat is filled?" - say "AI
       tooling" or "AI solution", NEVER "next-gen"; NEVER "Relevant?" /
       "Top of mind?"; NEVER ask an executive for time.
     Executive T2: opens "[First] - "; ~40 words; a short plain impact
       statement (what goes wrong if the QA problem stays unsolved)
       then the FIRST ContextQA mention as a VARIATION of the canonical
       line: "ContextQA has a novel, AI-native approach that [allows
       teams to scale test coverage quickly / benefit fit to the
       account], without adding headcount." NEVER "the first AI-native
       solution" (retired 2026-07-20). CTA "Worth a chat?" (a sharper
       contextual variant like "Worth adding to the eval?" is allowed
       when the account earns it). Signed Eric.
     DASH RULE (all exec touches): at most TWO spaced hyphens " - "
       per email INCLUDING the "[First] - " opener; three reads as
       AI-written.
     Executive T3: reply-in-thread one-question bump: opens
       "Hey [First] - ", one sharp exec-altitude question, no pitch,
       no signature, ends on the question.
     Executive T4: no greeting; REAL public proof point only (Clari 10x
       release-testing story; two-weeks-to-two-days regression story
       always caveated "shift-left plus AI"); ties back to the T1 risk;
       no sequence-ending language; CTA exactly "If relevant - would
       love to connect with the right person on your team to discuss."
     Director/BTL T1: opens "Happy [Day], [First]! "; body under ~100
       words; one verified signal as hook. BTL T1 CTA: "worth 20
       minutes?". BTL leans into practitioner benefits: multiplies
       output, hands back bandwidth for edge cases and exploratory work.
     DIFFERENTIATION HOOK (Director + BTL): these buyers drown in
       identical QA-vendor pitches (fast test creation, less
       maintenance). Position ContextQA as a different category -
       agentic/autonomous testing, AI agents that exercise the product
       like a user and build/maintain coverage themselves, handling
       dynamic flows script-based tools can't. No hype words, no
       invented stats.
     Touch 2 (Director/BTL): reply-in-thread one-question bump, 2-4
       days later. Opens "Hey [First] - ". One sharp discovery question
       at that buyer's altitude. No pitch, no signature, end on
       question. Every question must parse literally - no nonsense.
       (Executive T2/T3 formats are defined above and differ.)
     Director/BTL T3: no greeting; REAL public proof point only (Clari
       10x release-testing story; two-weeks-to-two-days regression story
       always caveated "shift-left plus AI"); close "Happy to share a
       short clip if that's easier than a call." and sign "Eric".
     OFFSHORE VARIANT of director T3 (accounts with offshore QA
       reqs): offshore-ROI frame - compliment the cost-per-coverage
       strategy, compare fully-loaded seat economics to platform
       coverage, aim at the NEXT req, never disparage the team, target
       US economic buyers, no invented ROI numbers.
     LinkedIn notes (every level): format "Hi [First], just sent you an
       email. We usually hear from [teams like theirs, personalized to
       seniority] when [challenge] - thought it might be valuable to
       connect, thanks!" (BTL may use a warmer peer variant: "...would
       love to learn about your testing setup / compare notes"). A note
       must NEVER repeat its level's T1 email hook - email and invite go
       out back to back. EXCEPTION: DeepIntent's notes are approved as
       written - do not regenerate them.
     BANNED WORDS/PHRASES (all content): "promise", "matrix",
       "exam-grade scrutiny" (use "regulatory scrutiny"), "genuinely" in
       LinkedIn notes, hype words, em/en dashes, invented stats. Ground
       every draft in latest.csv / roles.csv - never invent a signal.
1b3. PEOPLE SIGNALS - data/territories/<slug>/people_signals.csv
   (Account,Type,Person,Title,Date,Note). Types and score boosts (applied
   at build time, shown on the boards):
     new-exec (+25): CTO / CIO / relevant VP or chief (engineering,
       software, quality, AI) newly in seat within ~4 MONTHS. Verify via
       WebSearch during the leadership pass. When one exists: write a
       DEDICATED sequence for that person (sequences.csv row with
       Level=Special; use their real first name). Greeting is EXACTLY
       "congrats on the new role!" - for AI-titled execs (Chief AI
       Officer etc.) use "congrats on the new role... and RIP to your
       inbox [sobbing emoji]". NEVER "congrats on the new mandate" or
       any mandate-speak. NO FLUFF anywhere in exec-altitude copy: no
       trailing justification clauses ("Asking because...", "worth
       making deliberately"), no consultant patter; observation, risk
       with impact, question - nothing else. Exec formats + dash rule
       apply. - the page renders it in red above the
       Executive sequence titled "Sequence for new <Title> - for <First>"
       and marks the Executive sequence "do not send to <First>".
     new-director (+15): same, for new Directors (QA / Eng).
     qa-role-filled (+25): a QA/QE director or manager REQ that was in
       last week's roles.csv is GONE from the board this week (position
       filled = a buyer just landed). Detect by diffing roles.csv against
       the prior committed version (git show HEAD:...). Date = removal
       date. Write a Level=Special sequence tailored to the incoming
       hire; the page shows a red banner with days-since-removal above
       Find the buyer.
   Maintenance: drop new-exec/new-director rows once the person passes ~4
   months in seat (the boost expires; keep the bold overview mention by
   moving it into Key Signals if still relevant). Never invent a person
   or date - only verified events enter this file.
   - If a persona named in a draft's Notes (e.g. "check if the QA Manager
     req was filled") can be verified, update the note.
1b2. RELEVANT-REQ INVENTORY - territories with an outreach.csv also carry
   data/territories/<slug>/roles.csv (Account,Title,Location,URL,Tools):
   one row per relevant open req, where Tools is a pipe-separated list of
   testing tools/frameworks named in that posting's description (Selenium,
   Playwright, Cypress, Appium, JMeter, ...). Rebuild it each run from the
   same board fetches used for the counts (Greenhouse ?content=true, Lever
   JSON, Ashby posting-api all include descriptions). Keep it consistent
   with latest.csv's Relevant Roles counts. Software roles only - exclude
   hardware/RF/validation/system-test titles and interns. Accounts on
   Workday/Workable (no public JSON API) simply have no rows here; the
   page omits the req list for them automatically.
1c. GROW THE TERRITORY (only territories that have an outreach.csv) - each
   week hunt for up to 3 NEW companies that match the territory's ICP and
   newly show a trigger (fresh funding, new QA / eng-leadership req,
   expansion). Verify against their live ATS board, then
   append them to latest.csv (momentum will show them as NEW) and add an
   outreach.csv row (status Not started, personas + angle only). Companies
   with zero relevant signal may be dropped after 4+ consecutive quiet weeks
   - note the drop in the commit message.
2. Never edit HTML by hand. Run:  python3 build.py
   It regenerates all five territory boards AND the landing page AND the
   legacy pages in one pass, so a data refresh can never clobber the landing.
3. Commit and push to main; GitHub Pages serves the result.
Notes: the legacy board (data/latest.csv + data/*.csv snapshots) may be
refreshed on the same cadence or left frozen - build.py handles both, and
skips any board whose latest.csv is missing.
"""
import csv, json, os, datetime, glob, re, html, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = "eric-hastie/territory-radar"

# ------------------------- CONFIG: the demo territories -----------------------
WEIGHTS = {"roles": 10, "funding": 20, "leadership": 20, "expansion": 12}
W = WEIGHTS

TERRITORIES = [
    {
        "slug": "data-warehouse",
        "industry": "Cloud Data Warehousing",
        "caption": "Run as if selling a serverless cloud data warehouse.",
        "vendor_line": "run as if selling <b>a serverless cloud data warehouse</b> (an illustrative demo, not modeled on any real vendor)",
        "icp": "Midmarket companies (roughly 150 to 2,500 employees) with a real data and analytics function: actively hiring data engineers, analytics engineers, or data leadership, running a modern data stack, and plausibly feeling cloud warehouse cost or complexity pain. Recent funding, new technical leadership, or expansion moves signal budget and appetite to rethink the analytics stack.",
        "hot": 60, "warm": 40,
        "verified": "July 13, 2026",
        "desc": "Demo sales territory for cloud data warehousing: 20 real companies scored on live hiring, funding, and leadership buying signals.",
    },
    {
        "slug": "product-analytics",
        "industry": "Product Analytics",
        "caption": "Run as if selling a product analytics platform: analytics, session replay, feature flags, experiments.",
        "vendor_line": "run as if selling <b>a product analytics platform</b> covering analytics, session replay, feature flags, and experiments (an illustrative demo, not modeled on any real vendor)",
        "icp": "Engineering led, product led software companies with roughly 20 to 500 engineers, where developers pick and champion their own tooling. Typically venture backed (YC seed through growth stage) or strongly revenue funded, and shipping product fast enough to need analytics, feature flags, session replay, and experimentation as core infrastructure rather than afterthoughts. The buyer is the builder: technical founders, product engineers, growth engineers, and first PM or data hires. AI first teams weight extra. Excludes hobbyists, cost driven bootstrappers, and orgs where a central tools committee buys software over engineers' heads.",
        "hot": 80, "warm": 40,
        "verified": "July 13, 2026",
        "desc": "Demo sales territory for product analytics: 20 real companies scored on live hiring, funding, and leadership buying signals.",
    },
    {
        "slug": "observability",
        "industry": "Observability",
        "caption": "Run as if selling an observability platform: logs, metrics, traces, uptime.",
        "vendor_line": "run as if selling <b>an observability platform</b> covering logs, metrics, traces, and uptime (an illustrative demo, not modeled on any real vendor)",
        "icp": "Midmarket companies (roughly 200 to 3,000 employees) with production infrastructure pain: scaling cloud and Kubernetes footprints, SRE or platform teams forming or growing, and uptime as direct business risk (consumer apps, fintech, marketplaces, streaming, logistics).",
        "hot": 80, "warm": 40,
        "verified": "July 13, 2026",
        "desc": "Demo sales territory for observability: 20 real companies scored on live hiring, funding, and leadership buying signals.",
    },
    {
        "slug": "machine-health",
        "industry": "Industrial Machine Health",
        "caption": "Run as if the vendor were TRACTIAN: condition monitoring, CMMS, energy management (not affiliated).",
        "vendor_line": "run as if the vendor were <b>TRACTIAN</b>, selling condition monitoring, CMMS, and energy management to industrial maintenance teams (an illustrative demo, not affiliated with or endorsed by TRACTIAN)",
        "icp": "Mid-market industrial and manufacturing companies, roughly 200 to 3,000 employees, ideally running multiple plants in North America: food and beverage processing, packaging, automotive suppliers, building products, chemicals, consumer goods, pulp and paper, and metals. The buyers are maintenance managers, reliability engineers, plant engineers, plant managers, and VPs of Operations - teams with real rotating equipment (compressors, conveyors, blow molders, corrugators, extruders, paper machines) and chronic maintenance-staffing pressure, where condition monitoring, CMMS, and energy monitoring pay back fast.",
        "hot": 40, "warm": 20,
        "verified": "July 13 to 14, 2026",
        "desc": "Demo sales territory for industrial machine health: 20 real mid-market manufacturers scored on live maintenance hiring, funding, leadership, and plant-expansion buying signals.",
    },
    {
        "slug": "test-automation",
        "industry": "Software Test Automation",
        "caption": "Run as if the vendor were ContextQA: AI-powered autonomous testing for web, mobile, and API (not affiliated).",
        "vendor_line": "run as if the vendor were <b>ContextQA</b>, selling AI-powered autonomous testing for web, mobile, and API to QA and engineering teams (an illustrative demo, not affiliated with or endorsed by ContextQA)",
        "icp": "Mid-market software companies (roughly 200 to 2,000 employees) building high-stakes, compliance-heavy, or complex-integration products - logistics and supply chain, BFSI (banking, financial services, insurance), HR tech and payroll, CRM and customer platforms, health tech - where testing is genuinely painful and release risk is real money. They ship web and mobile products on fast release cycles, and the tell is an active req list for QA engineers, SDETs, and test automation engineers: test-coverage pain that AI-powered autonomous testing (web, mobile, API) can absorb. Primary buyers are QA leads and managers, engineering managers, and VPs of Engineering; a QA leadership req, fresh funding, or a new engineering executive is the timing trigger.",
        "hot": 52, "warm": 22,
        "verified": "July 19 to 20, 2026",
        "desc": "Demo sales territory for software test automation: 50 real software companies in high-stakes verticals scored on live QA and SDET hiring, funding, and leadership buying signals.",
    },
]

# Legacy board config (the original June-July 2026 demo)
LEGACY = {
    "product": "a cloud infrastructure / DevOps platform (IaC, observability, Kubernetes ops, cloud-cost)",
    "signal_desc": "an account investing in its platform / infrastructure org - hiring SRE, platform, DevOps or infrastructure engineers, raising fresh capital, or bringing on engineering leadership",
    "hot": 80, "warm": 40,
}

VERIFIED_HUMAN = "July 13 to 19, 2026"   # when the five demo territories were researched

TIER_VAR = {"Hot": "var(--hot)", "Warm": "var(--warm)", "Watch": "var(--watch)"}

def clean(v):
    # normalize em / en dashes (written as escapes so this file carries none)
    return v.replace("\u2014", "-").replace("\u2013", "-") if isinstance(v, str) else v

def to_int(v):
    try:
        return int(float(str(v).strip()))
    except (ValueError, TypeError):
        return 0

# Dev:tester ratio boost (test-automation): a territory row that carries both
# Est Devs and Est Testers gets a coverage-gap boost. Thresholds, not
# percentiles, so the cutoff is stable and explainable as the territory grows.
RATIO_BOOSTS = [(12, 10), (8, 5)]   # ratio >= 12:1 -> +10, >= 8:1 -> +5
RATIO_FLAG_AT = 12                  # messaging flag on the queue card

def ratio_of(r):
    """Estimated devs per dedicated tester, or None if either estimate is
    missing. Older snapshots without Est Testers simply score without it."""
    devs, testers = to_int(r.get("est_devs")), to_int(r.get("est_testers"))
    return round(devs / testers, 1) if devs and testers else None

def ratio_boost(r):
    ratio = ratio_of(r)
    if ratio is None:
        return 0
    return next((b for t, b in RATIO_BOOSTS if ratio >= t), 0)

def score_of(r):
    return (r["roles"] * W["roles"] + r["funding_sig"] * W["funding"]
            + r["leadership_sig"] * W["leadership"] + r["expansion_sig"] * W["expansion"]
            + ratio_boost(r))

def tier_of(s, hot, warm):
    return "Hot" if s >= hot else "Warm" if s >= warm else "Watch"

def human_date(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%B %-d, %Y") if os.name != "nt" else d.strftime("%B %d, %Y")

def read_csv(path, hot, warm):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for x in rows:
        r = {
            "account": clean(x.get("Account", "")),
            "industry": clean(x.get("Industry", "")),
            "hq": clean(x.get("HQ", "")),
            "headcount": clean(x.get("Headcount", "")),
            "funding": clean(x.get("Funding", "")),
            "total_roles": to_int(x.get("Total Open Roles", 0)),
            "roles": to_int(x.get("Relevant Roles", 0)),
            "funding_sig": to_int(x.get("Funding Signal", 0)),
            "leadership_sig": to_int(x.get("Leadership Signal", 0)),
            "expansion_sig": to_int(x.get("Expansion Signal", 0)),
            "est_devs": clean(x.get("Est Devs", "")),
            "est_testers": clean(x.get("Est Testers", "")),
            "signals": clean(x.get("Key Signals", "")),
            "why": clean(x.get("Why Now", "")),
            "url": clean(x.get("Source URL", "")),
        }
        r["score"] = score_of(r)
        r["tier"] = tier_of(r["score"], hot, warm)
        out.append(r)
    return out

def snapshots(data_dir, hot, warm):
    snaps = []
    for f in sorted(glob.glob(os.path.join(data_dir, "*.csv"))):
        m = re.match(r'(\d{4}-\d{2}-\d{2})\.csv$', os.path.basename(f))
        if not m:
            continue
        recs = read_csv(f, hot, warm)
        snaps.append({
            "date": m.group(1),
            "accounts": len(recs),
            "hot": sum(1 for r in recs if r["tier"] == "Hot"),
            "roles": sum(r["roles"] for r in recs),
            "total_roles": sum(r["total_roles"] for r in recs),
            "scores": {r["account"]: r["score"] for r in recs},
        })
    snaps.sort(key=lambda s: s["date"])
    return snaps

def add_momentum(board, snaps):
    prev = snaps[-2]["scores"] if len(snaps) >= 2 else {}
    for r in board:
        if r["account"] not in prev:
            r["mom"], r["mom_delta"] = "new", None
        else:
            d = r["score"] - prev[r["account"]]
            r["mom"] = "up" if d > 0 else "down" if d < 0 else "flat"
            r["mom_delta"] = d
    return board

# ---------------------------------- styles -----------------------------------
# The "Monday briefing" look: warm cream paper, serif masthead, double rules,
# terracotta accent - with a warm coffee-dark variant via prefers-color-scheme.
CSS = r'''
:root{
  --paper:#FAF6EF;--paper2:#F3EDE2;--card:#FFFDF8;--ink:#2A2520;--ink2:#4A4238;--muted:#7A7060;
  --hairline:#E2D9C9;--rule:#2A2520;--accent:#B4432E;--accent-soft:#B4432E14;--link:#1F6E68;
  --hot:#B4432E;--warm:#8F6A1D;--watch:#6E6759;--up:#1F6E68;--down:#B4432E;--sigred:#E00000;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}
@media(prefers-color-scheme:dark){:root{
  --paper:#211C17;--paper2:#282219;--card:#2A241D;--ink:#E8DFD2;--ink2:#CFC5B4;--muted:#9C9284;
  --hairline:#3A3226;--rule:#E8DFD2;--accent:#FF9273;--accent-soft:#FF927318;--link:#5FBFA8;
  --hot:#FF9273;--warm:#E2B45A;--watch:#A39A8A;--up:#5FBFA8;--down:#FF9273;--sigred:#FF3B30;}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);line-height:1.62;-webkit-font-smoothing:antialiased;font-size:17px}
a{color:var(--link);text-decoration:none;border-bottom:1px solid color-mix(in srgb,var(--link) 40%,transparent)}
a:hover{border-bottom-color:var(--link)}
.wrap{max-width:960px;margin:0 auto;padding:0 22px}
.num{font-variant-numeric:tabular-nums}
header{padding:52px 0 0}
.kicker{font-family:var(--sans);font-size:12px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);margin:0 0 14px}
h1{font-size:42px;line-height:1.08;font-weight:600;letter-spacing:-.015em;margin:0 0 14px}
.dateline{font-family:var(--sans);font-size:13.5px;color:var(--muted);margin:0;line-height:1.7}
.dateline b{color:var(--ink);font-weight:600}
.doubling{border:0;border-top:3px double var(--rule);margin:26px 0 0;opacity:.75}
.lede{font-size:20px;line-height:1.55;color:var(--ink);margin:30px 0 6px;max-width:820px}
.lede .hi{font-style:italic}
.movers{margin:18px 0 8px}
.mover{display:flex;gap:18px;padding:22px 0;border-top:1px solid var(--hairline)}
.mover:first-child{border-top:0}
.badge{flex:none;width:74px;text-align:center;padding-top:3px}
.badge .score{font-family:var(--sans);font-size:30px;font-weight:750;letter-spacing:-.02em;line-height:1;font-variant-numeric:tabular-nums;display:block}
.badge .delta{font-family:var(--mono);font-size:12.5px;font-weight:600;margin-top:5px;display:block}
.badge .tierw{display:inline-block;font-family:var(--sans);font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;margin-top:7px;padding:2px 8px;border-radius:999px;background:var(--accent-soft)}
.mover.up .delta{color:var(--up)}.mover.down .delta{color:var(--down)}
.mover h3{font-size:20px;margin:0 0 6px;font-weight:650;letter-spacing:-.01em}
.mover h3 .move{font-family:var(--sans);font-size:12.5px;font-weight:600;color:var(--muted);margin-left:8px;letter-spacing:.02em}
.mover p{margin:0;color:var(--ink2);font-size:16.5px}
.alsonote{background:var(--paper2);border-left:3px solid var(--accent);padding:14px 18px;margin:14px 0 0;font-size:15.5px;color:var(--ink2)}
.alsonote b{font-weight:650;color:var(--ink)}
section.boardsec{margin-top:44px}
h2{font-size:26px;font-weight:600;letter-spacing:-.01em;margin:0 0 4px}
.secsub{font-family:var(--sans);font-size:13.5px;color:var(--muted);margin:0 0 16px;max-width:800px}
.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:0 0 12px;font-family:var(--sans)}
#q{flex:1;min-width:200px;background:var(--card);border:1px solid var(--hairline);color:var(--ink);padding:10px 14px;border-radius:6px;font-size:14px;font-family:var(--sans);outline:none}
#q:focus{border-color:var(--accent)}
#q::placeholder{color:var(--muted)}
.seg{display:flex;gap:4px;background:var(--paper2);border:1px solid var(--hairline);border-radius:999px;padding:3px}
.seg button{background:transparent;border:0;color:var(--muted);padding:6px 13px;border-radius:999px;cursor:pointer;font-size:13px;font-weight:600;font-family:var(--sans)}
.seg button.on{background:var(--accent);color:var(--card)}
.count{color:var(--muted);font-size:13px;white-space:nowrap}
.tablewrap{overflow-x:auto;border:1px solid var(--hairline);background:var(--card);border-radius:6px}
table{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:14px;min-width:980px}
thead th{text-align:left;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding:12px 14px;border-bottom:1px solid var(--hairline);white-space:nowrap}
thead th[data-k]{cursor:pointer;user-select:none}
thead th[data-k]:hover{color:var(--ink)}
.arw{opacity:.6;font-size:10px}
tbody td{padding:13px 14px;border-bottom:1px solid var(--hairline);vertical-align:top}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--paper2)}
td.rk{color:var(--muted);width:34px}
.co{font-weight:650;font-size:15px;font-family:var(--serif)}
.co a{color:var(--ink);border-bottom:0}
.co a:hover{color:var(--link)}
.meta{color:var(--muted);font-size:12px;margin-top:1px}
td.sc{white-space:nowrap}
.scoren{font-size:17px;font-weight:700;font-variant-numeric:tabular-nums}
.tier{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-left:9px}
.tier i{width:8px;height:8px;border-radius:50%;display:inline-block}
.t-Hot{color:var(--hot)}.t-Hot i{background:var(--hot)}
.t-Warm{color:var(--warm)}.t-Warm i{background:var(--warm)}
.t-Watch{color:var(--watch)}.t-Watch i{background:var(--watch)}
td.mo{white-space:nowrap;font-variant-numeric:tabular-nums;font-weight:600}
.m-up{color:var(--up)}.m-down{color:var(--down)}.m-flat{color:var(--muted)}
.m-new{color:var(--muted);font-size:10px;font-weight:700;letter-spacing:.1em}
td.mo small{color:var(--muted);font-weight:500;margin-left:3px}
td.ro{font-variant-numeric:tabular-nums;white-space:nowrap}
td.ro b{font-weight:700}td.ro span{color:var(--muted)}
.sig{font-size:12.5px;color:var(--ink2);min-width:220px}
.sig .p{display:inline-block;background:var(--paper2);border:1px solid var(--hairline);border-radius:4px;padding:2px 7px;margin:2px 3px 0 0}
td.why{color:var(--ink2);font-size:13px;line-height:1.5;min-width:240px;font-family:var(--serif);font-style:italic}
.tablenote{font-family:var(--sans);font-size:12.5px;color:var(--muted);margin:10px 2px 0}
.keyrow{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 0;font-family:var(--sans);font-size:12.5px;color:var(--ink2)}
.keyrow span{background:var(--paper2);border:1px solid var(--hairline);border-radius:999px;padding:4px 12px}
.keyrow b{font-weight:700}
.about{margin-top:46px;border-top:1px solid var(--hairline);padding-top:28px}
.about p{color:var(--ink2);font-size:16px;max-width:820px;margin:0 0 14px}
.about b{color:var(--ink);font-weight:650}
footer{margin-top:44px;border-top:3px double var(--rule);padding:24px 0 64px}
footer p{font-family:var(--sans);font-size:13px;color:var(--muted);max-width:820px;margin:0 0 10px}
footer b{color:var(--ink2)}
.byline{font-family:var(--sans);font-size:13.5px;color:var(--ink2);margin-top:16px}
.byline b{color:var(--ink)}
.cards{display:grid;grid-template-columns:1fr;gap:14px;margin:26px 0 0}
@media(min-width:620px){.cards{grid-template-columns:repeat(2,1fr)}.cards a.card:last-child:nth-child(odd){grid-column:1/-1}}
@media(min-width:1000px){.cards{grid-template-columns:repeat(3,1fr)}.cards a.card:last-child:nth-child(odd){grid-column:auto}}
a.card{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--hairline);border-top:3px solid var(--accent);border-radius:6px;padding:20px 18px;color:var(--ink);transition:transform .15s ease,box-shadow .15s ease}
a.card:hover{transform:translateY(-2px);box-shadow:0 6px 18px rgba(42,37,32,.08)}
.card .ind{font-size:19px;font-weight:650;letter-spacing:-.01em;margin:0 0 7px;line-height:1.25}
.card .cap{font-family:var(--sans);color:var(--muted);font-size:12.5px;margin:0 0 14px;line-height:1.5}
.card .mini{display:flex;gap:14px;font-family:var(--sans);font-size:12px;color:var(--muted);margin-top:auto}
.card .mini b{color:var(--ink);font-size:15px;font-variant-numeric:tabular-nums}
.card .mini .hotn b{color:var(--hot)}
.card .go{margin-top:12px;font-family:var(--sans);color:var(--accent);font-size:12.5px;font-weight:600}
.histsec{margin-top:38px}
.panel{background:var(--card);border:1px solid var(--hairline);border-radius:6px;padding:18px}
.legend{display:flex;gap:18px;margin-top:10px;font-family:var(--sans);font-size:12.5px;color:var(--muted)}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:middle}
.qgroup{margin-top:38px}
.qgroup h2 .n{color:var(--muted);font-weight:500;font-size:17px}
.acct{background:var(--card);border:1px solid var(--hairline);border-radius:6px;padding:18px 20px;margin:14px 0}
.acct.compact{padding:14px 20px}
.aline{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}
.aline .co{font-size:18px}
.aline .sc{margin-left:auto;white-space:nowrap}
.status{display:inline-block;font-family:var(--sans);font-size:10.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:3px 10px;border-radius:999px;border:1px solid var(--hairline);background:var(--paper2)}
.status.s-now{color:var(--accent)}
.status.s-active{color:var(--up)}
.status.s-idle{color:var(--muted)}
.status[data-acct]{cursor:pointer}
.status[data-acct]:hover{border-color:currentColor}
.angle{color:var(--ink2);font-size:15.5px;margin:8px 0 10px;line-height:1.5}
.hunt{font-family:var(--sans);font-size:12.5px;color:var(--muted);margin:0}
.hunt .p{display:inline-block;background:var(--paper2);border:1px solid var(--hairline);border-radius:4px;padding:3px 9px;margin:3px 5px 0 0}
.hunt a.p{color:var(--link)}
details.draft{margin-top:12px;border-top:1px solid var(--hairline);padding-top:10px;font-family:var(--sans)}
details.draft summary{cursor:pointer;font-size:13px;font-weight:600;color:var(--link)}
details.seq{margin-top:12px;border:1px solid var(--hairline);border-radius:6px;padding:0 16px 4px;background:var(--paper2)}
details.seq>summary{cursor:pointer;font-family:var(--sans);font-size:13.5px;font-weight:700;color:var(--ink);padding:11px 0}
details.seq>summary .who{font-weight:500;color:var(--muted);font-size:12.5px}
details.seq[open]>summary{border-bottom:1px solid var(--hairline)}
details.seq details.draft{border-top:0;margin-top:2px;padding-top:8px}
details.seq details.draft+details.draft{border-top:1px solid var(--hairline)}
details.seq pre.dbody{background:var(--card)}
details.seq.special{border-color:var(--sigred);border-width:1.5px;background:color-mix(in srgb,var(--sigred) 4%,transparent)}
details.seq.special>summary{color:var(--sigred)}
.dns{color:var(--sigred);font-weight:700;font-size:12px}
p.alert{font-family:var(--sans);font-size:13.5px;font-weight:700;color:var(--sigred);border:1px solid color-mix(in srgb,var(--sigred) 45%,transparent);background:color-mix(in srgb,var(--sigred) 8%,transparent);border-radius:6px;padding:9px 13px;margin:10px 0}
p.ratioflag{font-family:var(--sans);font-size:13.5px;font-weight:700;color:var(--warm);border:1px solid color-mix(in srgb,var(--warm) 45%,transparent);background:color-mix(in srgb,var(--warm) 8%,transparent);border-radius:6px;padding:9px 13px;margin:10px 0}
.subj{font-size:13px;color:var(--muted);margin:10px 0 6px}.subj b{color:var(--ink)}
pre.dbody{white-space:pre-wrap;font-family:var(--serif);font-size:15px;line-height:1.55;background:var(--paper2);border:1px solid var(--hairline);border-radius:6px;padding:14px 16px;margin:0 0 8px}
button.copy{font-family:var(--sans);font-size:12px;font-weight:600;background:var(--accent);color:var(--card);border:0;border-radius:999px;padding:6px 14px;cursor:pointer}
button.copy.ok{background:var(--up)}
.anote{font-family:var(--sans);font-size:12.5px;color:var(--muted);margin:10px 0 0}
.wk{border-bottom:1px solid var(--hairline);padding:14px 0}.wk:last-child{border-bottom:0}
.wkhead{font-size:15px;margin-bottom:8px}
.wkrow{display:flex;gap:8px;align-items:baseline;margin:4px 0;flex-wrap:wrap;font-family:var(--sans)}
.lbl{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);min-width:80px;font-weight:700}
.chip{display:inline-block;font-family:var(--sans);font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;margin:2px 0;background:var(--paper2);border:1px solid var(--hairline)}
.chip.up{color:var(--up)}.chip.down{color:var(--down)}
.yes{color:var(--up);font-weight:700}.no{color:var(--muted)}
.muted{color:var(--muted)}
@media(max-width:600px){h1{font-size:32px}.badge{width:60px}.badge .score{font-size:25px}.mover{gap:12px}}
'''

# --------------------------------- landing -----------------------------------
LANDING = r'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Territory Radar - The weekly territory briefing for Account Executives</title>
<meta name="description" content="An automated territory-intelligence tool that scores target accounts on buying signals from hiring, funding, and leadership activity. Five demo industries: cloud data warehousing, product analytics, observability, industrial machine health, software test automation.">
<style>__CSS__</style></head><body>
<header><div class="wrap">
  <p class="kicker">B2B Sales · Territory Intelligence</p>
  <h1>Territory Radar</h1>
  <p class="dateline"><b>The Monday territory briefing for Account Executives</b> &nbsp;·&nbsp; five demo industries, __NACCTS__ accounts &nbsp;·&nbsp; updated __DATEHUMAN__ &nbsp;·&nbsp; built by Eric Hastie</p>
  <hr class="doubling">
</div></header>

<main><div class="wrap">
  <p class="lede"><span class="hi">__GREETING__</span> Territory Radar reads a whole sales territory every week - live job boards, funding news, leadership moves, expansion announcements - scores every account on a transparent signal model, and hands back a ranked briefing. Account planning starts from "why now," not a static list.</p>

  <section class="boardsec">
    <h2>Pick an industry</h2>
    <p class="secsub">The engine doesn't care what I'm selling. I point it at a market, describe the ideal customer profile, and it re-scores a universe of companies through that lens. Five demo territories below - same tool, five different products, five different answers to "who do I call first?"</p>
    <div class="cards">__CARDS__</div>
    <div class="alsonote" style="margin-top:22px"><b>Illustrative demos.</b> Three boards are run against unnamed hypothetical products; the other two are run as if the vendor were a real company - TRACTIAN for industrial machine health and ContextQA for software test automation - neither of which is affiliated with or has endorsed this project. The companies, job postings, funding rounds, and leadership moves are all real, verified __VERIFIED__ against live ATS job boards (Greenhouse / Lever / Ashby / Workday and others) and public sources; the scoring and tiering are this tool's own. A live deployment runs against a real book of business in a <b>private</b> repo.</div>
  </section>

  <section class="about">
    <h2>Why job postings?</h2>
    <p>Job postings are one of the cleanest, earliest intent signals in B2B - a company scaling its platform team or hiring an infra leader is telling you about budget and initiatives before any intent-data vendor flags it.</p>
    <p>They're also a pain to actually use. Checking postings by hand across a whole territory - twenty accounts, twenty different job boards, every single week - is tedious, slow, and easy to let slide (I know, because I used to do it that way). Work that valuable and that repetitive is a perfect target for automation, so I automated it: the tool does the checking and hands me the ranked briefing.</p>
    <p>Every score is a <b>transparent weighted sum</b>, so when someone asks "why is this account ranked third," there's an actual answer (no black box, no vibes).</p>
  </section>
</div></main>

<footer><div class="wrap">
  <p><b>Scoring.</b> Every account's score is a transparent, weighted sum of verified signals: relevant open roles &times;__W_ROLES__, recent funding +__W_FUNDING__, new leadership +__W_LEADERSHIP__, expansion +__W_EXPANSION__. Each board explains its own Hot / Warm / Watch tiers.</p>
  <p><b>The archive.</b> <a href="legacy.html">The original demo board (June-July 2026)</a> - a cloud-infrastructure territory tracked across weekly snapshots - is still live, with its <a href="history.html">momentum history</a> and <a href="roles.html">open-roles inventory</a>.</p>
  <p><a href="https://github.com/__REPO__" target="_blank" rel="noopener">Source on GitHub</a> · refreshed by a weekly cloud agent.</p>
  <p class="byline">Built by <b>Eric Hastie</b> · auto-refreshed weekly · see you next Monday</p>
</div></footer>
</body></html>'''

CARD = r'''<a class="card" href="__SLUG__/">
  <p class="ind">__INDUSTRY__</p>
  <p class="cap">__CAPTION__</p>
  <div class="mini"><span><b>__ACCOUNTS__</b> accounts</span><span class="hotn"><b>__HOT__</b> hot</span></div>
  <div class="go">Open the board &rarr;</div>
</a>'''

# ------------------------------- board (shared) -------------------------------
BOARD = r'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<style>__CSS__</style></head><body>
<header><div class="wrap">
  <p class="kicker">__EYEBROW__</p>
  <h1>__H1__</h1>
  <p class="dateline"><b>Week of __DATEHUMAN__</b> &nbsp;·&nbsp; signals verified __VERIFIED__ &nbsp;·&nbsp; __ACCOUNTS__ accounts, __HOT__ hot &nbsp;·&nbsp; __ROLES__ relevant / __TOTALROLES__ open roles</p>
  <p class="dateline" style="margin-top:4px">This board is __VENDORLINE__.</p>
  <p class="dateline" style="margin-top:8px">__NAV__</p>
  <hr class="doubling">
</div></header>

<main><div class="wrap">
__BRIEFING__
  <div class="alsonote" style="margin-top:24px"><b>The ICP this board scores against:</b> __ICP__</div>

  <section class="boardsec">
    <h2>The board</h2>
    <p class="secsub">Every account, ranked by signal score. Score = relevant roles &times;__W_ROLES__, recent funding +__W_FUNDING__, new leadership +__W_LEADERSHIP__, expansion +__W_EXPANSION__, plus people-signal boosts (new senior tech exec &le;4 months or QA-leadership req filled +25, new director +15) and a dev:tester coverage-gap boost where both estimates exist (&ge;12:1 +10, &ge;8:1 +5). Hot &ge; __HOT_T__, Warm &ge; __WARM__. Click any column to re-sort, or any account for the source behind its signals.</p>
    <div class="controls">
      <input id="q" type="search" placeholder="Search account, signal, HQ..." autocomplete="off">
      <div class="seg" id="seg">
        <button data-seg="all" class="on">All</button>
        <button data-seg="Hot">Hot</button>
        <button data-seg="Warm">Warm</button>
        <button data-seg="Watch">Watch</button>
      </div>
      <span class="count" id="count"></span>
    </div>
    <div class="tablewrap"><table>
      <thead><tr>
        <th>#</th>
        <th data-k="account">Account <span class="arw"></span></th>
        <th data-k="score">Signal <span class="arw">&#9660;</span></th>
__MOMTH__
        <th data-k="roles">Roles rel / total <span class="arw"></span></th>
        <th>Key signals</th>
        <th>Why now</th>
      </tr></thead>
      <tbody id="rows"></tbody>
    </table></div>
    <div class="keyrow" aria-label="Scoring weights">
      <span>relevant open role <b>&times;__W_ROLES__</b></span>
      <span>recent funding <b>+__W_FUNDING__</b></span>
      <span>new leadership <b>+__W_LEADERSHIP__</b></span>
      <span>expansion / new region <b>+__W_EXPANSION__</b></span>
      <span>new senior tech exec in seat (&le;4 mo) <b>+25</b></span>
      <span>QA-leadership req filled <b>+25</b></span>
      <span>new director in seat <b>+15</b></span>
      <span>Hot <b>&ge; __HOT_T__</b> · Warm <b>&ge; __WARM__</b> · Watch below</span>
    </div>
  </section>

__ABOUT__
</div></main>

<footer><div class="wrap">
__FOOTER__
  <p class="byline">Built by <b>Eric Hastie</b> · auto-refreshed weekly · see you next Monday</p>
</div></footer>

<script>
const DATA = __DATA__;
const HASHIST = __HASHIST__;
const tbody=document.getElementById('rows'),q=document.getElementById('q'),count=document.getElementById('count');
let seg='all',sortK='score',sortDir=-1;
const MOM={up:'<span class="m-up">&#9650;</span>',down:'<span class="m-down">&#9660;</span>',flat:'<span class="m-flat">&#9644;</span>',new:'<span class="m-new">NEW</span>'};
function sigChips(s){return s? s.split('|').map(x=>`<span class="p">${x.trim()}</span>`).join('') : '<span class="muted">-</span>';}
function render(){
  const t=q.value.trim().toLowerCase();
  let list=DATA.filter(r=>{
    if(seg!=='all' && r.tier!==seg)return false;
    if(!t)return true;
    return (r.account+' '+r.industry+' '+r.signals+' '+r.hq).toLowerCase().includes(t);
  });
  list=list.slice().sort((a,b)=>{
    let av=a[sortK],bv=b[sortK];
    if(sortK==='score'||sortK==='roles')return (av-bv)*sortDir;
    return String(av).localeCompare(String(bv))*sortDir;
  });
  tbody.innerHTML=list.map((r,i)=>`<tr>
    <td class="rk num">${i+1}</td>
    <td><div class="co">${r.url?`<a href="${r.url}" target="_blank" rel="noopener">${r.account}</a>`:r.account}</div>
        <div class="meta">${[r.industry,r.hq,r.headcount,r.funding].filter(Boolean).join(' · ')}</div></td>
    <td class="sc"><span class="scoren num">${r.score}</span><span class="tier t-${r.tier}"><i></i>${r.tier}</span></td>
    ${HASHIST?`<td class="mo">${MOM[r.mom]||''}${r.mom_delta?`<small>${r.mom_delta>0?'+':''}${r.mom_delta}</small>`:''}</td>`:''}
    <td class="ro"><b>${r.roles}</b> <span>/ ${r.total_roles||0}</span></td>
    <td class="sig">${sigChips(r.signals)}</td>
    <td class="why">${r.why||''}</td>
  </tr>`).join('');
  count.textContent=list.length+' of '+DATA.length+' accounts';
}
document.querySelectorAll('#seg button').forEach(b=>b.onclick=()=>{seg=b.dataset.seg;document.querySelectorAll('#seg button').forEach(x=>x.classList.remove('on'));b.classList.add('on');render();});
document.querySelectorAll('thead th[data-k]').forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(sortK===k){sortDir*=-1}else{sortK=k;sortDir=(k==='score'||k==='roles')?-1:1}document.querySelectorAll('.arw').forEach(a=>a.textContent='');th.querySelector('.arw').innerHTML=sortDir>0?'&#9650;':'&#9660;';render();});
q.oninput=render;render();
</script>
</body></html>'''

MOM_TH = '        <th data-k="mom">Momentum <span class="arw"></span></th>'

SCORE_HELP = r'''  <section class="about">
  <h2>How the signal score works</h2>
  <p>Every account's score is a transparent, weighted sum of verified signals, so the ranking is explainable - no black box, no vibes. A relevant open role is worth &times;__W_ROLES__, recent funding +__W_FUNDING__, new leadership +__W_LEADERSHIP__, and an expansion or new region +__W_EXPANSION__. On top of that, verified people signals add a boost: a senior tech executive (CTO / CIO / relevant VP or chief) newly in seat within about 4 months +25, a QA-leadership req that just disappeared from the board (position filled - a buyer landing) +25, and a new director in seat +15. Territories that carry developer and tester estimates also add a coverage-gap boost from the estimated dev:tester ratio - +10 at 12:1 or wider, +5 at 8:1 - fixed thresholds rather than percentiles, so the cutoff stays stable and explainable as the territory grows. Both counts are labeled estimates (LinkedIn title sampling, req history, and industry norms), so the ratio feeds coarse buckets, never precise ranking.</p>
  <p><b>Tiers:</b> <span class="tier t-Hot"><i></i>Hot</span> at score &ge; __HOT_T__, <span class="tier t-Warm"><i></i>Warm</span> at &ge; __WARM__, <span class="tier t-Watch"><i></i>Watch</span> below that. The thresholds flex per territory because a "lot of hiring" means different things in different markets.</p>
  </section>'''

LEGACY_ABOUT = r'''  <section class="about">
  <h2>About this board</h2>
  <p>This is the original Territory Radar territory: 16 real mid-market and enterprise companies scored on buying signals for a cloud infrastructure / DevOps platform, tracked across weekly snapshots since June 2026. Job postings are one of the cleanest, earliest intent signals in B2B - a company scaling its platform team or hiring an infra leader is telling you about budget and initiatives before any intent-data vendor flags it. The site has since grown into <a href="./">five industry demo territories</a>; this page is preserved because it carries the longest momentum history.</p>
  </section>''' + SCORE_HELP

# ---------------------------------- history ----------------------------------
HISTORY = r'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Momentum & History - Territory Radar</title>
<style>__CSS__</style></head><body>
<header><div class="wrap">
  <p class="kicker">Territory Radar · The Archive</p>
  <h1>Momentum &amp; History</h1>
  <p class="dateline"><b>How the original demo territory moved over time.</b> Each weekly run is snapshotted, so you can see which accounts heated up, which cooled, and how overall hiring signal trended.</p>
  <p class="dateline" style="margin-top:8px"><a href="legacy.html">&larr; The original demo board</a> &nbsp;·&nbsp; <a href="./">All industries</a> &nbsp;·&nbsp; <a href="roles.html">All open roles</a> &nbsp;·&nbsp; <span class="muted">updated __DATEHUMAN__</span> &nbsp;·&nbsp; <span class="muted">__WEEKS__ weekly snapshots · __HOT__ hot now · __TOTALROLES__ open roles (__NETTOTAL__ vs start)</span></p>
  <hr class="doubling">
</div></header>
<main><div class="wrap">
  <section class="histsec"><h2>Hiring signal across the territory</h2><div class="panel"><div id="chart"></div></div></section>
  <section class="histsec"><h2>Weekly movers</h2><div class="panel" id="log"></div></section>
</div></main>
<footer><div class="wrap">
  <p>Total open roles is the aggregate of every open position across the territory; relevant roles are the subset that match the signal profile. Momentum is the week-over-week change in each account's signal score, from the dated snapshots in <code>data/</code>.</p>
  <p class="byline">Built by <b>Eric Hastie</b> · auto-refreshed weekly</p>
</div></footer>
<script>
const M=__METRICS__;
function drawChart(){
  const w=720,h=300,pad={l:44,r:16,t:16,b:42},iw=w-pad.l-pad.r,ih=h-pad.t-pad.b,n=M.length;
  const maxv=Math.max(...M.map(d=>d.total_roles),1);
  const X=i=>n<=1?pad.l+iw/2:pad.l+iw*i/(n-1),Y=v=>pad.t+ih*(1-v/maxv);
  const S=[{k:'total_roles',c:'var(--link)',l:'Total open roles'},{k:'roles',c:'var(--accent)',l:'Relevant roles'}];
  let s=`<svg viewBox="0 0 ${w} ${h}" width="100%" role="img" aria-label="Hiring signal across the territory over time">`;
  for(let g=0;g<=4;g++){const v=Math.round(maxv*g/4),yy=Y(v);s+=`<line x1="${pad.l}" y1="${yy}" x2="${w-pad.r}" y2="${yy}" stroke="var(--hairline)"/><text x="${pad.l-8}" y="${yy+4}" fill="var(--muted)" font-size="11" text-anchor="end">${v}</text>`;}
  const step=Math.max(1,Math.ceil(n/8));
  M.forEach((d,i)=>{if(i%step===0||i===n-1)s+=`<text x="${X(i)}" y="${h-pad.b+18}" fill="var(--muted)" font-size="10" text-anchor="middle">${d.date.slice(5)}</text>`;});
  S.forEach(se=>{if(n>1)s+=`<polyline points="${M.map((d,i)=>X(i)+','+Y(d[se.k])).join(' ')}" fill="none" stroke="${se.c}" stroke-width="2.5"/>`;M.forEach((d,i)=>s+=`<circle cx="${X(i)}" cy="${Y(d[se.k])}" r="3.5" fill="${se.c}"/>`);});
  s+=`</svg><div class="legend">`+S.map(se=>`<span><i style="background:${se.c}"></i>${se.l}</span>`).join('')+`</div>`;
  document.getElementById('chart').innerHTML=s;
}
function drawLog(){
  const chips=(a,c)=>a.length?a.map(x=>`<span class="chip ${c}">${x}</span>`).join(' '):'<span class="muted">-</span>';
  document.getElementById('log').innerHTML=M.slice().reverse().map((d,ri)=>{
    const prev=M[M.length-2-ri];
    const td=prev?d.total_roles-prev.total_roles:0;
    const tdtxt=prev?` (<span class="${td>0?'m-up':td<0?'m-down':'muted'}">${td>0?'+':''}${td}</span>)`:'';
    const head=`<div class="wkhead"><b>${d.date}</b> · ${d.accounts} accounts · ${d.hot} hot · <b>${d.total_roles}</b> open roles${tdtxt} · ${d.roles} relevant</div>`;
    if(d.first)return `<div class="wk">${head}<div class="wkrow"><span class="muted">Baseline snapshot.</span></div></div>`;
    return `<div class="wk">${head}
      <div class="wkrow"><span class="lbl">Heating up</span> ${chips(d.up,'up')}</div>
      <div class="wkrow"><span class="lbl">Cooling</span> ${chips(d.down,'down')}</div></div>`;
  }).join('');
}
drawChart();drawLog();
</script>
</body></html>'''

# ----------------------------------- roles -----------------------------------
ROLES = r'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>All open roles - Territory Radar</title>
<style>__CSS__</style></head><body>
<header><div class="wrap">
  <p class="kicker">Territory Radar · The Archive</p>
  <h1>All open roles</h1>
  <p class="dateline"><b>Every open position across the original demo territory</b> - the full inventory behind the signal scores. Use the "unmatched" filter to scan for titles that <i>should</i> count as a buying signal but don't yet.</p>
  <p class="dateline" style="margin-top:8px"><a href="legacy.html">&larr; The original demo board</a> &nbsp;·&nbsp; <a href="./">All industries</a> &nbsp;·&nbsp; <a href="history.html">Momentum &amp; history</a> &nbsp;·&nbsp; <span class="muted">updated __DATEHUMAN__</span> &nbsp;·&nbsp; <span class="muted">__TOTAL__ roles tracked · __MATCHED__ count as a signal · __UNMATCHED__ unmatched · __NACCT__ accounts</span></p>
  <hr class="doubling">
</div></header>
<main><div class="wrap">
  <section class="boardsec">
  <div class="controls">
    <input id="q" type="search" placeholder="Search title, account, location..." autocomplete="off">
    <div class="seg" id="seg">
      <button data-seg="all" class="on">All</button>
      <button data-seg="match">Counts as signal</button>
      <button data-seg="unmatch">Unmatched</button>
    </div>
    <span class="count" id="count"></span>
  </div>
  <div class="tablewrap"><table style="min-width:760px">
    <thead><tr>
      <th data-k="account">Account <span class="arw"></span></th>
      <th data-k="title">Title <span class="arw"></span></th>
      <th data-k="location">Location <span class="arw"></span></th>
      <th data-k="matched">Signal? <span class="arw"></span></th>
    </tr></thead>
    <tbody id="rows"></tbody>
  </table></div>
  </section>
</div></main>
<footer><div class="wrap">
  <p>"Signal?" marks whether a title matched the original board's signal profile (SRE / platform / DevOps / infrastructure / cloud / Kubernetes / observability). Spot one that should match? It gets added to the profile and re-scored on the next run.</p>
  <p class="byline">Built by <b>Eric Hastie</b> · auto-refreshed weekly</p>
</div></footer>
<script>
const ROLES=__ROLES__;
const tbody=document.getElementById('rows'),q=document.getElementById('q'),count=document.getElementById('count');
let seg='all',sortK='account',sortDir=1;
function render(){
  const t=q.value.trim().toLowerCase();
  let list=ROLES.filter(r=>{
    if(seg==='match'&&!r.matched)return false;
    if(seg==='unmatch'&&r.matched)return false;
    if(!t)return true;
    return (r.account+' '+r.title+' '+r.location).toLowerCase().includes(t);
  });
  list=list.slice().sort((a,b)=>{
    if(sortK==='matched')return (a.matched-b.matched)*sortDir;
    return String(a[sortK]).localeCompare(String(b[sortK]))*sortDir;
  });
  tbody.innerHTML=list.map(r=>`<tr>
    <td class="co">${r.account}</td>
    <td>${r.url?`<a href="${r.url}" target="_blank" rel="noopener">${r.title}</a>`:r.title}</td>
    <td class="muted">${r.location||''}</td>
    <td>${r.matched?'<span class="yes">&#10003; yes</span>':'<span class="no">-</span>'}</td>
  </tr>`).join('');
  count.textContent=list.length+' of '+ROLES.length+' roles';
}
document.querySelectorAll('#seg button').forEach(b=>b.onclick=()=>{seg=b.dataset.seg;document.querySelectorAll('#seg button').forEach(x=>x.classList.remove('on'));b.classList.add('on');render();});
document.querySelectorAll('thead th[data-k]').forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(sortK===k){sortDir*=-1}else{sortK=k;sortDir=1}document.querySelectorAll('.arw').forEach(a=>a.textContent='');th.querySelector('.arw').innerHTML=sortDir>0?'&#9650;':'&#9660;';render();});
q.oninput=render;render();
</script>
</body></html>'''

def read_roles(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for x in rows:
        out.append({
            "account": clean(x.get("Account", "")),
            "title": clean(x.get("Title", "")),
            "location": clean(x.get("Location", "")),
            "matched": to_int(x.get("Matched", 0)),
            "url": clean(x.get("URL", "")),
        })
    return out

# ------------------------------- action queue --------------------------------
OUTREACH_PAGE = r'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Action Queue - __INDUSTRY__ - Territory Radar</title>
<meta name="description" content="The working outreach queue for the __INDUSTRY__ demo territory: buyer personas, one-click people searches, and signal-grounded first-touch drafts.">
<style>__CSS__</style></head><body>
<header><div class="wrap">
  <p class="kicker">Territory Radar · Action Queue</p>
  <h1>This week's outreach</h1>
  <p class="dateline"><b>__INDUSTRY__</b> &nbsp;·&nbsp; week of __DATEHUMAN__ &nbsp;·&nbsp; __COUNTS__</p>
  <p class="dateline" style="margin-top:8px">__NAV__</p>
  <hr class="doubling">
</div></header>

<main><div class="wrap">
  <p class="lede">The <a href="./">board</a> answers "who's heating up and why." This page turns the top of that board into actual pipeline work: the buyer personas to hunt down, one-click people searches, and a first-touch draft grounded in each account's verified signals - ready to personalize and send.</p>
  <div class="alsonote"><b>How to work it.</b> Each drafted account carries <b>three sequences</b> - Executive, Director, and BTL - so the message matches the altitude of whoever the persona hunt turns up: outcomes and economics for a CTO, coverage and cycle time for a director, the actual stack and the script-maintenance grind for the practitioner. Drafts use <b>[First]</b> and <b>[Day]</b> placeholders - put a real name in and adjust to their profile before sending. When a touch goes out, <b>click the status chip</b> - it flips between To contact and Contacted right on the page (saved in this browser). The canonical status lives in <code style="font-family:var(--mono);font-size:13px">outreach.csv</code>; report what happened (contacted, replied, meeting) and the next build writes it back and regroups the page. Only the top of the board gets sequences; when an account heats up, they get written that week.</div>
__GROUPS__
</div></main>

<footer><div class="wrap">
  <p><b>Methodology.</b> Every draft's hook is a signal verified on the <a href="./">territory board</a> - nothing is invented. This board is __VENDORLINE__. The drafts are illustrative demo copy in my own outbound voice, not sent mail.</p>
  <p><a href="./">&larr; Back to the board</a> · <a href="../">All industries</a> · <a href="https://github.com/__REPO__" target="_blank" rel="noopener">source on GitHub</a>.</p>
  <p class="byline">Built by <b>Eric Hastie</b> · auto-refreshed weekly · see you next Monday</p>
</div></footer>
<script>
document.querySelectorAll('button.copy').forEach(b=>b.onclick=()=>{
  const el=document.getElementById(b.dataset.t);
  navigator.clipboard.writeText(el.textContent).then(()=>{
    const old=b.textContent;b.textContent='copied!';b.classList.add('ok');
    setTimeout(()=>{b.textContent=old;b.classList.remove('ok')},1600);
  });
});
const KEY='trq-status-'+location.pathname;
const saved=JSON.parse(localStorage.getItem(KEY)||'{}');
document.querySelectorAll('.status[data-acct]').forEach(ch=>{
  const a=ch.dataset.acct;
  const apply=v=>{ch.textContent=v;
    ch.classList.toggle('s-active',v==='Contacted');
    ch.classList.toggle('s-now',v==='To contact');};
  if(saved[a])apply(saved[a]);
  ch.title='Click to toggle: To contact / Contacted (saved in this browser until the CSV catches up)';
  ch.onclick=()=>{const v=ch.textContent.trim()==='To contact'?'Contacted':'To contact';
    apply(v);saved[a]=v;localStorage.setItem(KEY,JSON.stringify(saved));};
});
</script>
</body></html>'''

STATUS_CLASS = {"To contact": "s-now", "Contacted": "s-active", "Replied": "s-active",
                "Meeting": "s-active", "Hold": "s-idle", "Not started": "s-idle"}

QUEUE_GROUPS = [
    ("Contact this week", ["To contact"],
     "Hot accounts with a draft ready. Hunt the persona, drop in a name, personalize, send."),
    ("In motion", ["Contacted", "Replied", "Meeting"],
     "Touched and waiting, or moving. Keep the thread warm."),
    ("On hold", ["Hold"],
     "Deliberately paused - the notes say why."),
    ("The bench", ["Not started"],
     "Signal on the board but not yet worth a draft. Personas and the angle are pre-staged so promotion is a five-minute job, not a research project."),
]

def read_outreach(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for x in rows:
        out.append({
            "account": clean(x.get("Account", "")),
            "status": clean(x.get("Status", "")) or "Not started",
            "personas": clean(x.get("Personas", "")),
            "angle": clean(x.get("Angle", "")),
            "notes": clean(x.get("Notes", "")),
        })
    return out

SEQ_LEVELS = [
    ("Executive", "CTO / VP Engineering"),
    ("Director", "Directors of QA / Engineering, EMs"),
    ("BTL", "QA leads / SDETs / practitioners"),
]

# people_signals.csv: verified person-level events that boost an account's
# score and unlock a dedicated red sequence. Types:
#   new-exec        - CTO / CIO / relevant VP or chief (eng, software, quality,
#                     AI) new in seat within ~4 months            -> +25
#   new-director    - new Director (QA / Eng) in seat, ~4 months  -> +15
#   qa-role-filled  - a QA/QE director or manager REQ disappeared from the
#                     board (position filled); Date = removal date -> +25
PEOPLE_BOOSTS = {"new-exec": 25, "new-director": 15, "qa-role-filled": 25}

def read_people_signals(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, newline="") as f:
        for x in csv.DictReader(f):
            out.setdefault(clean(x.get("Account", "")), []).append({
                "type": clean(x.get("Type", "")).strip(),
                "person": clean(x.get("Person", "")),
                "title": clean(x.get("Title", "")),
                "date": clean(x.get("Date", "")).strip(),
                "note": clean(x.get("Note", "")),
            })
    return out

def signal_month(date_s):
    """'2026-05' or '2026-05-12' -> 'May 2026' (best effort)."""
    try:
        parts = date_s.split("-")
        d = datetime.date(int(parts[0]), int(parts[1]), 1)
        return d.strftime("%B %Y")
    except (ValueError, IndexError):
        return date_s

def apply_people_boosts(board, people, hot, warm):
    for r in board:
        sigs = people.get(r["account"], [])
        boost = sum(PEOPLE_BOOSTS.get(s["type"], 0) for s in sigs)
        if boost:
            r["score"] += boost
            r["tier"] = tier_of(r["score"], hot, warm)
    return board

def read_sequences(path):
    """sequences.csv -> {account: {level: {subject, body, touch2, touch3, touch4, linote}}}"""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, newline="") as f:
        for x in csv.DictReader(f):
            out.setdefault(clean(x.get("Account", "")), {})[clean(x.get("Level", ""))] = {
                "subject": clean(x.get("Email Subject", "")),
                "body": clean(x.get("Email Body", "")),
                "touch2": clean(x.get("Second Touch Email", "")),
                "touch3": clean(x.get("Third Touch Email", "")),
                "touch4": clean(x.get("Fourth Touch Email", "")),
                "linote": clean(x.get("LinkedIn Note", "")),
            }
    return out

def read_territory_roles(path):
    """roles.csv -> {account: [{title, location, url, tools}]}. Accounts absent
    from the file were not API-verifiable (Workday/Workable boards)."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, newline="") as f:
        for x in csv.DictReader(f):
            out.setdefault(clean(x.get("Account", "")), []).append({
                "title": clean(x.get("Title", "")),
                "location": clean(x.get("Location", "")),
                "url": clean(x.get("URL", "")),
                "tools": [t.strip() for t in clean(x.get("Tools", "")).split("|") if t.strip()],
            })
    return out

def persona_links(account, personas):
    short = account.split(" (")[0].strip()
    chips = []
    for p in [x.strip() for x in personas.split("|") if x.strip()]:
        label = p
        # searches work better without our parenthetical annotations
        p_clean = re.sub(r"\s*\(.*?\)", "", p).strip()
        q = urllib.parse.quote(f'"{short}" "{p_clean}"')
        chips.append(f'<a class="p" href="https://www.linkedin.com/search/results/people/'
                     f'?keywords={q}" target="_blank" rel="noopener">{esc(label)} &#8599;</a>')
    return "".join(chips)

def days_ago(date_s):
    try:
        d = datetime.date.fromisoformat(date_s)
        return (datetime.date.today() - d).days
    except ValueError:
        return None

def outreach_card(o, r, idx, roles=None, seqs=None, psigs=None):
    """One account card. r is the board row (score/tier/meta) or None; roles is
    the account's verified relevant-req list from roles.csv; seqs is the
    account's per-level sequence dict from sequences.csv; psigs is the
    account's people_signals rows (or None)."""
    psigs = psigs or []
    score_html = ""
    meta_bits = []
    rr = ratio_of(r) if r else None
    if r:
        tcolor = TIER_VAR[r["tier"]]
        score_html = (f'<span class="sc"><span class="scoren num" style="color:{tcolor}">{r["score"]}</span>'
                      f'<span class="tier t-{r["tier"]}"><i></i>{r["tier"]}</span></span>')
        meta_bits = [r["industry"], r["hq"]]
        if r["headcount"]:
            meta_bits.append(f'{r["headcount"]} employees')
        if r.get("est_devs"):
            meta_bits.append(f'~{r["est_devs"]} devs (est.)')
        if rr is not None:
            meta_bits.append(f'~{rr:g}:1 dev:tester (est.)')
    meta = " · ".join(b for b in meta_bits if b)
    scls = STATUS_CLASS.get(o["status"], "s-idle")
    toggle = ' data-acct="%s"' % html.escape(o["account"], quote=True) \
        if o["status"] in ("To contact", "Contacted") else ""
    has_draft = bool(seqs)
    parts = [f'<div class="acct{"" if has_draft else " compact"}">',
             f'<div class="aline"><span class="co">{esc(o["account"])}</span>'
             f'<span class="status {scls}"{toggle}>{esc(o["status"])}</span>{score_html}</div>']
    if meta:
        parts.append(f'<div class="meta">{esc(meta)}</div>')
    if o["angle"]:
        parts.append(f'<p class="angle">{esc(o["angle"])}</p>')
    for s in psigs:
        if s["type"] in ("new-exec", "new-director"):
            parts.append(f'<p class="angle"><b>New {esc(s["title"])} as of '
                         f'{esc(signal_month(s["date"]))}: {esc(s["person"])}.</b></p>')
    for s in psigs:
        if s["type"] == "qa-role-filled":
            n = days_ago(s["date"])
            ago = f' - {n} days ago' if n is not None else ""
            parts.append(f'<p class="alert">{esc(s["title"])} posting removed '
                         f'{esc(s["date"])}{ago}; check LinkedIn to find the new '
                         f'{esc(s["title"])}. Use the dedicated sequence below.</p>')
    if rr is not None and rr >= RATIO_FLAG_AT:
        parts.append(f'<p class="ratioflag">~{rr:g} devs per tester (est.) - '
                     'the outnumbered-maintainers angle applies at Director and BTL.</p>')
    parts.append(f'<p class="hunt"><b>Find the buyer:</b> {persona_links(o["account"], o["personas"])}</p>')
    if r and r["url"]:
        ats = ("Greenhouse" if "greenhouse" in r["url"] else "Lever" if "lever.co" in r["url"]
               else "Ashby" if "ashbyhq" in r["url"] else "Workday" if "myworkdayjobs" in r["url"]
               else "Workable" if "workable" in r["url"] else "careers site")
        label = f'{r["roles"]} relevant / {r["total_roles"]} open roles on {ats}'
        parts.append(f'<p class="hunt" style="margin-top:6px"><b>Jobs board:</b> '
                     f'<a class="p" href="{html.escape(r["url"], quote=True)}" target="_blank" '
                     f'rel="noopener">{label} &#8599;</a></p>')
    if roles:
        req_links = "".join(
            f'<a class="p" href="{html.escape(j["url"], quote=True)}" target="_blank" '
            f'rel="noopener" title="{html.escape(j["location"], quote=True)}">'
            f'{esc(j["title"])} &#8599;</a>' for j in roles)
        parts.append(f'<p class="hunt" style="margin-top:6px"><b>Relevant reqs:</b> {req_links}</p>')
        tools = sorted({t for j in roles for t in j["tools"]})
        stack = ("".join(f'<span class="p">{esc(t)}</span>' for t in tools)
                 if tools else '<span class="muted">none named in the postings</span>')
        parts.append(f'<p class="hunt" style="margin-top:6px"><b>Stack in the reqs:</b> {stack}</p>')
    new_exec = next((s for s in psigs if s["type"] == "new-exec"), None)
    filled = next((s for s in psigs if s["type"] in ("qa-role-filled", "new-director")), None)
    levels = []
    if (seqs or {}).get("Special") and (new_exec or filled):
        sig = new_exec or filled
        label = f'Sequence for new {sig["title"]}'
        if new_exec:
            label += f' - for {sig["person"].split()[0]}'
        levels.append(("Special", label, "", "seq special", ""))
    for level, who in SEQ_LEVELS:
        dns = (f'do not send to {new_exec["person"].split()[0]}'
               if level == "Executive" and new_exec else "")
        levels.append((level, f'{level} sequence', who, "seq", dns))
    for lv, (level, label, who, cls, dns) in enumerate(levels):
        s = (seqs or {}).get(level)
        if not s or not s["body"].strip():
            continue
        p = f'd{idx}v{lv}'
        inner = [
            f'<details class="draft"><summary>First-touch email</summary>'
            f'<p class="subj">subject: <b>{esc(s["subject"])}</b></p>'
            f'<pre class="dbody" id="{p}a">{esc(s["body"])}</pre>'
            f'<button class="copy" data-t="{p}a">copy email</button></details>']
        exec_seq = level == "Executive"
        if s["touch2"].strip():
            l2 = ("Second touch - impact + how ContextQA helps, reply in thread (2-4 days later)"
                  if exec_seq else
                  "Second touch - one-question bump, reply in thread (2-4 days later)")
            inner.append(
                f'<details class="draft"><summary>{l2}</summary>'
                f'<p class="subj">subject: <b>re: {esc(s["subject"])}</b></p>'
                f'<pre class="dbody" id="{p}b">{esc(s["touch2"])}</pre>'
                f'<button class="copy" data-t="{p}b">copy reply</button></details>')
        if s["touch3"].strip():
            l3 = ("Third touch - one-question bump, reply in thread"
                  if exec_seq else
                  "Third touch - proof point, reply in thread (about a week later)")
            inner.append(
                f'<details class="draft"><summary>{l3}</summary>'
                f'<p class="subj">subject: <b>re: {esc(s["subject"])}</b></p>'
                f'<pre class="dbody" id="{p}c">{esc(s["touch3"])}</pre>'
                f'<button class="copy" data-t="{p}c">copy reply</button></details>')
        if s.get("touch4", "").strip():
            inner.append(
                f'<details class="draft"><summary>Fourth touch - proof point, reply in thread (about a week later)</summary>'
                f'<p class="subj">subject: <b>re: {esc(s["subject"])}</b></p>'
                f'<pre class="dbody" id="{p}e">{esc(s["touch4"])}</pre>'
                f'<button class="copy" data-t="{p}e">copy reply</button></details>')
        if s["linote"].strip():
            inner.append(
                f'<details class="draft"><summary>LinkedIn connection note</summary>'
                f'<pre class="dbody" id="{p}d">{esc(s["linote"])}</pre>'
                f'<button class="copy" data-t="{p}d">copy note</button></details>')
        who_html = f' <span class="who">· {who}</span>' if who else ""
        dns_html = f' <span class="dns">· {esc(dns)}</span>' if dns else ""
        parts.append(
            f'<details class="{cls}"><summary>{esc(label)}{who_html}{dns_html}'
            f'</summary>{"".join(inner)}</details>')
    if o["notes"]:
        parts.append(f'<p class="anote"><b>Note:</b> {esc(o["notes"])}</p>')
    parts.append('</div>')
    return "".join(parts)

def build_outreach(t, board, updated, people=None):
    """Render <slug>/outreach.html if the territory has an outreach.csv."""
    people = people or {}
    path = os.path.join(ROOT, "data", "territories", t["slug"], "outreach.csv")
    queue = read_outreach(path)
    if not queue:
        return False
    by_account = {r["account"]: r for r in board}
    territory_roles = read_territory_roles(
        os.path.join(ROOT, "data", "territories", t["slug"], "roles.csv"))
    sequences = read_sequences(
        os.path.join(ROOT, "data", "territories", t["slug"], "sequences.csv"))
    def score_of_row(o):
        r = by_account.get(o["account"])
        return r["score"] if r else 0
    groups_html = []
    idx = 0
    for title, statuses, sub in QUEUE_GROUPS:
        rows = sorted([o for o in queue if o["status"] in statuses],
                      key=score_of_row, reverse=True)
        if not rows:
            continue
        cards = []
        for o in rows:
            cards.append(outreach_card(o, by_account.get(o["account"]), idx,
                                       territory_roles.get(o["account"]),
                                       sequences.get(o["account"]),
                                       people.get(o["account"])))
            idx += 1
        groups_html.append(
            f'<section class="qgroup"><h2>{title} <span class="n">· {len(rows)}</span></h2>'
            f'<p class="secsub">{sub}</p>{"".join(cards)}</section>')
    n_now = sum(1 for o in queue if o["status"] == "To contact")
    n_active = sum(1 for o in queue if o["status"] in ("Contacted", "Replied", "Meeting"))
    counts = f'{n_now} to contact this week'
    if n_active:
        counts += f' · {n_active} in motion'
    counts += f' · {len(queue)} accounts tracked'
    others = [x for x in TERRITORIES if x["slug"] != t["slug"]]
    nav = (f'<a href="./">&larr; {t["industry"]} board</a> &nbsp;·&nbsp; <a href="../">All industries</a>'
           + "".join(f' &nbsp;·&nbsp; <a href="../{o["slug"]}/">{o["industry"]}</a>' for o in others))
    html_s = (OUTREACH_PAGE
              .replace("__CSS__", CSS)
              .replace("__INDUSTRY__", t["industry"])
              .replace("__DATEHUMAN__", updated)
              .replace("__COUNTS__", counts)
              .replace("__NAV__", nav)
              .replace("__GROUPS__", "".join(groups_html))
              .replace("__VENDORLINE__", t["vendor_line"])
              .replace("__REPO__", REPO))
    with open(os.path.join(ROOT, t["slug"], "outreach.html"), "w") as f:
        f.write(html_s)
    print(f'built {t["slug"]}/outreach.html: {n_now} to contact, {len(queue)} tracked')
    return True

def fill_weights(html_s, hot, warm):
    return (html_s
            .replace("__W_ROLES__", str(W["roles"]))
            .replace("__W_FUNDING__", str(W["funding"]))
            .replace("__W_LEADERSHIP__", str(W["leadership"]))
            .replace("__W_EXPANSION__", str(W["expansion"]))
            .replace("__HOT_T__", str(hot))
            .replace("__WARM__", str(warm)))

# ------------------------------ briefing opener -------------------------------
def greeting():
    return "Happy " + datetime.date.today().strftime("%A") + "!"

def esc(s):
    return html.escape(s, quote=False)

def signal_label(r):
    bits = []
    if r["roles"]:
        bits.append(f'{r["roles"]} relevant role{"s" if r["roles"] != 1 else ""} open')
    if r["funding_sig"]:
        bits.append("fresh capital")
    if r["leadership_sig"]:
        bits.append("new leadership")
    if r["expansion_sig"]:
        bits.append("expansion underway")
    return " + ".join(bits[:2]) if bits else "on the radar"

def mover_block(r, label, delta=None):
    cls = "up" if (delta or 0) > 0 else "down" if (delta or 0) < 0 else ""
    tcolor = TIER_VAR[r["tier"]]
    delta_html = ""
    if delta is not None and delta != 0:
        arrow = "&#9650;" if delta > 0 else "&#9660;"
        delta_html = f'<span class="delta">{arrow} {"+" if delta > 0 else ""}{delta}</span>'
    return (f'<div class="mover {cls}">'
            f'<div class="badge"><span class="score num" style="color:{tcolor}">{r["score"]}</span>{delta_html}'
            f'<span class="tierw" style="color:{tcolor}">{r["tier"]}</span></div>'
            f'<div><h3><span class="co">{esc(r["account"])}</span><span class="move">{esc(label)}</span></h3>'
            f'<p>{esc(r["why"] or r["signals"])}</p></div></div>')

def briefing_html(board, has_history):
    """The editorial opener. With two or more snapshots it narrates the biggest
    week-over-week movers; on a first snapshot it honestly narrates the
    strongest live signals instead, and the movers take over automatically
    once the second snapshot exists."""
    hi = f'<span class="hi">{greeting()}</span>'
    if has_history:
        movers = [r for r in board if r.get("mom") in ("up", "down")]
        movers.sort(key=lambda r: abs(r.get("mom_delta") or 0), reverse=True)
        top = movers[:3]
        if not top:
            lede = (f'<p class="lede">{hi} A quiet week - no account changed its signal score. '
                    'The board below still ranks who to call first, and the momentum column shows the longer arc.</p>')
            return lede
        n_up = sum(1 for r in board if r.get("mom") == "up")
        n_down = sum(1 for r in board if r.get("mom") == "down")
        moved = []
        if n_up:
            moved.append(f'{n_up} heating up')
        if n_down:
            moved.append(f'{n_down} cooling')
        lede = (f'<p class="lede">{hi} {n_up + n_down} account{"s" if n_up + n_down != 1 else ""} moved this week '
                f'({" and ".join(moved)}). Here\'s where I\'d spend the first coffee.</p>')
        blocks = "".join(mover_block(r, "heating up" if r["mom_delta"] > 0 else "cooling off",
                                     r["mom_delta"]) for r in top)
        rest = (n_up + n_down) - len(top)
        note = ""
        if rest > 0:
            note = (f'<div class="alsonote"><b>Also moved:</b> {rest} more account{"s" if rest != 1 else ""} '
                    'changed score this week - the momentum column below has every arrow.</div>')
        return lede + f'<div class="movers">{blocks}</div>' + note
    # first snapshot: no week-over-week yet - narrate the strongest live signals
    top = board[:3]
    lede = (f'<p class="lede">{hi} This territory is on its first weekly snapshot, so there\'s no '
            'week-over-week movement to report yet. Instead, here\'s what\'s moving <i>inside</i> the '
            'territory right now - the three accounts with the strongest live signals, and why I\'d call them first.</p>')
    blocks = "".join(mover_block(r, signal_label(r)) for r in top)
    note = ('<div class="alsonote"><b>Momentum starts next week.</b> Every account below is at its baseline '
            'score; once the second weekly snapshot lands, real week-over-week movers take over this space automatically.</div>')
    return lede + f'<div class="movers">{blocks}</div>' + note

def render_board(out_path, board, ctx):
    html_s = (BOARD
              .replace("__CSS__", CSS)
              .replace("__TITLE__", ctx["title"])
              .replace("__DESC__", ctx["desc"])
              .replace("__EYEBROW__", ctx["eyebrow"])
              .replace("__H1__", ctx["h1"])
              .replace("__VENDORLINE__", ctx["vendorline"])
              .replace("__VERIFIED__", ctx["verified"])
              .replace("__NAV__", ctx["nav"])
              .replace("__ICP__", ctx["icp"])
              .replace("__BRIEFING__", briefing_html(board, ctx["has_history"]))
              .replace("__ABOUT__", ctx["about"])
              .replace("__FOOTER__", ctx["footer"])
              .replace("__MOMTH__", MOM_TH if ctx["has_history"] else "")
              .replace("__HASHIST__", "true" if ctx["has_history"] else "false")
              .replace("__DATA__", json.dumps(board))
              .replace("__DATEHUMAN__", ctx["updated"])
              .replace("__ACCOUNTS__", str(len(board)))
              .replace("__HOT__", str(sum(1 for r in board if r["tier"] == "Hot")))
              .replace("__ROLES__", str(sum(r["roles"] for r in board)))
              .replace("__TOTALROLES__", str(sum(r["total_roles"] for r in board))))
    html_s = fill_weights(html_s, ctx["hot"], ctx["warm"])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html_s)

def build_territory(t):
    data_dir = os.path.join(ROOT, "data", "territories", t["slug"])
    csv_path = os.path.join(data_dir, "latest.csv")
    if not os.path.exists(csv_path):
        print(f"no {csv_path} - skipping {t['slug']}")
        return None
    board = read_csv(csv_path, t["hot"], t["warm"])
    people = read_people_signals(os.path.join(data_dir, "people_signals.csv"))
    board = apply_people_boosts(board, people, t["hot"], t["warm"])
    snaps = snapshots(data_dir, t["hot"], t["warm"])
    board = add_momentum(board, snaps)
    board.sort(key=lambda r: r["score"], reverse=True)
    updated = human_date(snaps[-1]["date"]) if snaps else t["verified"]

    others = [x for x in TERRITORIES if x["slug"] != t["slug"]]
    has_queue = os.path.exists(os.path.join(data_dir, "outreach.csv"))
    queue_link = '<a href="outreach.html"><b>This week\'s action queue &rarr;</b></a> &nbsp;·&nbsp; ' if has_queue else ''
    nav = (queue_link + '<a href="../">&larr; All industries</a>'
           + "".join(f' &nbsp;·&nbsp; <a href="../{o["slug"]}/">{o["industry"]}</a>' for o in others))
    vendor_clause = t["vendor_line"]
    ctx = {
        "title": f'{t["industry"]} - Territory Radar',
        "desc": t["desc"],
        "eyebrow": "Territory Radar · Weekly Briefing",
        "h1": t["industry"],
        "vendorline": vendor_clause,
        "verified": t["verified"],
        "nav": nav,
        "icp": t["icp"],
        "about": SCORE_HELP,
        "footer": (f'<p><b>Methodology.</b> Demo territory of 20 real companies; signals verified {t["verified"]} '
                   'against live ATS job boards (Greenhouse / Lever / Ashby / Workday and others) and public sources, '
                   're-verified weekly. Signal counts and firmographics are best-effort from public data. '
                   f'This board is {vendor_clause}. All scoring and tiering are this tool\'s own. '
                   'A live deployment runs against a real book of business in a <b>private</b> repo.</p>'
                   '<p><a href="../">&larr; All industries</a> · <a href="https://github.com/' + REPO +
                   '" target="_blank" rel="noopener">source on GitHub</a>.</p>'),
        "updated": updated,
        "hot": t["hot"], "warm": t["warm"],
        "has_history": len(snaps) >= 2,
    }
    render_board(os.path.join(ROOT, t["slug"], "index.html"), board, ctx)
    if has_queue:
        build_outreach(t, board, updated, people)
    hot_n = sum(1 for r in board if r["tier"] == "Hot")
    print(f'built {t["slug"]}/index.html: {len(board)} accounts, {hot_n} hot')
    return {"slug": t["slug"], "industry": t["industry"], "caption": t["caption"],
            "accounts": len(board), "hot": hot_n,
            "last_date": snaps[-1]["date"] if snaps else None}

def build_legacy(today_human):
    csv_path = os.path.join(ROOT, "data", "latest.csv")
    if not os.path.exists(csv_path):
        print("no data/latest.csv - skipping legacy board")
        return
    hot, warm = LEGACY["hot"], LEGACY["warm"]
    board = read_csv(csv_path, hot, warm)
    snaps = snapshots(os.path.join(ROOT, "data"), hot, warm)
    board = add_momentum(board, snaps)
    board.sort(key=lambda r: r["score"], reverse=True)
    updated = human_date(snaps[-1]["date"]) if snaps else today_human

    ctx = {
        "title": "The original demo board (June-July 2026) - Territory Radar",
        "desc": "The original Territory Radar demo: a cloud infrastructure / DevOps territory of 16 real companies tracked across weekly snapshots.",
        "eyebrow": "Territory Radar · The Archive",
        "h1": "The original demo board",
        "vendorline": (f'run as if selling {LEGACY["product"]} - a <b>buying signal</b> here means '
                       f'{LEGACY["signal_desc"]}'),
        "verified": "weekly since June 2026",
        "nav": ('<a href="./">&larr; All industries</a> &nbsp;·&nbsp; <a href="history.html">Momentum &amp; history</a> '
                '&nbsp;·&nbsp; <a href="roles.html">All open roles &rarr;</a>'),
        "icp": ("mid-market and enterprise companies investing in their platform / infrastructure org: hiring SRE, "
                "platform, DevOps or infrastructure engineers, raising fresh capital, or bringing on engineering "
                "leadership. Swap the config and the account list, and the same engine works for any product and territory."),
        "about": LEGACY_ABOUT,
        "footer": ('<p><b>Methodology.</b> Sample territory, signals verified against company career pages / ATS and '
                   'public sources. Signal counts and firmographics are best-effort from public data. This is '
                   'illustrative demo data on real companies - a live deployment runs against a real book of business '
                   'in a <b>private</b> repo.</p>'
                   '<p><a href="./">&larr; All industries</a> · <a href="https://github.com/' + REPO +
                   '" target="_blank" rel="noopener">source on GitHub</a>.</p>'),
        "updated": updated,
        "hot": hot, "warm": warm,
        "has_history": len(snaps) >= 2,
    }
    render_board(os.path.join(ROOT, "legacy.html"), board, ctx)
    print(f"built legacy.html: {len(board)} accounts")

    # history
    metrics = []
    for i, s in enumerate(snaps):
        prev = snaps[i - 1]["scores"] if i else {}
        up = sorted([a for a, sc in s["scores"].items() if a in prev and sc > prev[a]])
        down = sorted([a for a, sc in s["scores"].items() if a in prev and sc < prev[a]])
        metrics.append({"date": s["date"], "accounts": s["accounts"], "hot": s["hot"],
                        "roles": s["roles"], "total_roles": s["total_roles"],
                        "up": up, "down": down, "first": (i == 0)})
    if metrics:
        net = metrics[-1]["total_roles"] - metrics[0]["total_roles"]
        hist = (HISTORY
                .replace("__CSS__", CSS)
                .replace("__METRICS__", json.dumps(metrics))
                .replace("__DATEHUMAN__", updated)
                .replace("__WEEKS__", str(len(metrics)))
                .replace("__HOT__", str(metrics[-1]["hot"]))
                .replace("__TOTALROLES__", str(metrics[-1]["total_roles"]))
                .replace("__NETTOTAL__", f"+{net}" if net >= 0 else str(net)))
        with open(os.path.join(ROOT, "history.html"), "w") as f:
            f.write(hist)
        print(f"built history.html: {len(metrics)} snapshots, net total roles {net:+d}")

    # roles inventory
    roles = read_roles(os.path.join(ROOT, "data", "roles-latest.csv"))
    if roles:
        matched = sum(1 for r in roles if r["matched"])
        rl = (ROLES
              .replace("__CSS__", CSS)
              .replace("__ROLES__", json.dumps(roles))
              .replace("__DATEHUMAN__", updated)
              .replace("__TOTAL__", str(len(roles)))
              .replace("__MATCHED__", str(matched))
              .replace("__UNMATCHED__", str(len(roles) - matched))
              .replace("__NACCT__", str(len({r["account"] for r in roles}))))
        with open(os.path.join(ROOT, "roles.html"), "w") as f:
            f.write(rl)
        print(f"built roles.html: {len(roles)} open roles ({matched} matched)")
    else:
        print("no data/roles-latest.csv - skipping roles.html")

def build_landing(cards_info, today_human):
    dates = [c["last_date"] for c in cards_info if c and c["last_date"]]
    updated = human_date(max(dates)) if dates else today_human
    cards = "".join(
        CARD.replace("__SLUG__", c["slug"])
            .replace("__INDUSTRY__", c["industry"])
            .replace("__CAPTION__", c["caption"])
            .replace("__ACCOUNTS__", str(c["accounts"]))
            .replace("__HOT__", str(c["hot"]))
        for c in cards_info if c)
    html_s = (LANDING
              .replace("__CSS__", CSS)
              .replace("__NACCTS__", str(sum(c["accounts"] for c in cards_info if c)))
              .replace("__CARDS__", cards)
              .replace("__GREETING__", greeting())
              .replace("__DATEHUMAN__", updated)
              .replace("__VERIFIED__", VERIFIED_HUMAN)
              .replace("__REPO__", REPO))
    html_s = fill_weights(html_s, 0, 0)
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(html_s)
    print(f"built index.html (landing): {len([c for c in cards_info if c])} territories")

def main():
    today = datetime.date.today()
    today_human = today.strftime("%B %-d, %Y") if os.name != "nt" else today.strftime("%B %d, %Y")
    cards_info = [build_territory(t) for t in TERRITORIES]
    build_landing(cards_info, today_human)
    build_legacy(today_human)

if __name__ == "__main__":
    main()
