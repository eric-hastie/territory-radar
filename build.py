#!/usr/bin/env python3
"""Regenerate the Territory Radar site.

Inputs:
  data/latest.csv        - one row per target account, with raw signal components
                           (incl. Total Open Roles and Relevant Roles).
  data/roles-latest.csv  - one row per open position across all accounts
                           (Account, Title, Location, Matched, URL) for review.
  data/YYYY-MM-DD.csv     - weekly snapshots of latest.csv (for momentum/trends).

Outputs:
  index.html    - ranked territory board (signal score, tier, momentum)
  history.html  - momentum view: total + relevant roles and hot accounts over time
  roles.html    - full open-roles inventory for manual review (spot missed titles)

No third-party dependencies.

--- RECONFIGURE FOR A NEW ROLE ---
Edit the CONFIG block (what you sell + signal weights), and point the weekly
research routine at your real account list. Copy is generated from CONFIG.
"""
import csv, json, os, datetime, glob, re

ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(ROOT, "data", "latest.csv")
ROLES_PATH = os.path.join(ROOT, "data", "roles-latest.csv")
REPO = "eric-hastie/territory-radar"

# ---------------- CONFIG (edit when you change what you sell) -----------------
CONFIG = {
    "product": "a cloud infrastructure / DevOps platform (IaC, observability, Kubernetes ops, cloud-cost)",
    "signal_desc": "an account investing in its platform / infrastructure org - hiring SRE, platform, DevOps or infrastructure engineers, raising fresh capital, or bringing on engineering leadership",
    "weights": {"roles": 10, "funding": 20, "leadership": 20, "expansion": 12},
    "hot": 80,
    "warm": 40,
}
W = CONFIG["weights"]

def clean(v):
    return v.replace("—", "-").replace("–", "-") if isinstance(v, str) else v

def to_int(v):
    try:
        return int(float(str(v).strip()))
    except (ValueError, TypeError):
        return 0

def score_of(r):
    return (r["roles"] * W["roles"] + r["funding_sig"] * W["funding"]
            + r["leadership_sig"] * W["leadership"] + r["expansion_sig"] * W["expansion"])

def tier_of(s):
    return "Hot" if s >= CONFIG["hot"] else "Warm" if s >= CONFIG["warm"] else "Watch"

def read_csv(path):
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
            "signals": clean(x.get("Key Signals", "")),
            "why": clean(x.get("Why Now", "")),
            "url": clean(x.get("Source URL", "")),
        }
        r["score"] = score_of(r)
        r["tier"] = tier_of(r["score"])
        out.append(r)
    return out

def snapshots():
    snaps = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "*.csv"))):
        m = re.match(r'(\d{4}-\d{2}-\d{2})\.csv$', os.path.basename(f))
        if not m:
            continue
        recs = read_csv(f)
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
CSS = r'''
:root{--bg:#0f1115;--panel:#171a21;--panel2:#1d212a;--line:#2a2f3a;--txt:#e7eaf0;--muted:#9aa3b2;--accent:#6c8cff;--accent2:#41d3a3;
--hot:#ff6b5d;--hotbg:#3a1f1d;--warm:#e3b341;--warmbg:#352d18;--watch:#5a6172;--watchbg:#22262f;--up:#41d3a3;--down:#ff7a7a;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header{padding:60px 0 26px;border-bottom:1px solid var(--line)}
.eyebrow{color:var(--accent2);font-weight:600;letter-spacing:.08em;text-transform:uppercase;font-size:12px;margin:0 0 13px}
h1{font-size:38px;line-height:1.12;margin:0 0 13px;font-weight:740;letter-spacing:-.02em}
.sub{color:var(--muted);font-size:18px;max-width:700px;margin:0}
.byline{margin-top:18px;color:var(--muted);font-size:14px}.byline b{color:var(--txt)}
.callout{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:10px;padding:14px 16px;margin:22px 0 0;font-size:14px;color:#cdd3de;max-width:760px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0 0}
@media(max-width:720px){.stats{grid-template-columns:repeat(2,1fr)}h1{font-size:29px}}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
.stat .n{font-size:26px;font-weight:720;letter-spacing:-.02em}.stat .l{color:var(--muted);font-size:12.5px;margin-top:3px}
section{padding:34px 0 0}h2{font-size:21px;margin:0 0 13px;letter-spacing:-.01em}
.about p{color:#cdd3de;max-width:780px}
.score-help{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px;font-size:13px;color:var(--muted)}
.score-help code{background:var(--panel2);padding:2px 7px;border-radius:6px;color:#cdd3de}
.controls{position:sticky;top:0;z-index:5;background:var(--bg);padding:20px 0 12px;margin-top:30px;border-bottom:1px solid var(--line);display:flex;gap:12px;flex-wrap:wrap;align-items:center}
#q{flex:1;min-width:220px;background:var(--panel2);border:1px solid var(--line);color:var(--txt);padding:11px 14px;border-radius:10px;font-size:14px;outline:none}
#q:focus{border-color:var(--accent)}
.seg{display:flex;gap:6px;background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:4px}
.seg button{background:transparent;border:0;color:var(--muted);padding:7px 13px;border-radius:7px;cursor:pointer;font-size:13px;font-weight:600}
.seg button.on{background:var(--accent);color:#0b0d12}
.count{color:var(--muted);font-size:13px;white-space:nowrap}
.tablewrap{overflow-x:auto;margin:16px 0 60px;border:1px solid var(--line);border-radius:12px}
table{width:100%;border-collapse:collapse;font-size:14px;min-width:920px}
thead th{position:sticky;top:0;background:var(--panel2);text-align:left;padding:12px 14px;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--line);cursor:pointer;user-select:none;white-space:nowrap}
thead th:hover{color:var(--txt)}.arw{opacity:.5;font-size:10px}
tbody td{padding:13px 14px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:last-child td{border-bottom:0}tbody tr:hover{background:var(--panel)}
.acct{font-weight:650;font-size:15px}.meta{color:var(--muted);font-size:12.5px;margin-top:2px}
.scorewrap{display:flex;align-items:center;gap:9px}.scoren{font-size:19px;font-weight:740;font-variant-numeric:tabular-nums}
.tier{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px;white-space:nowrap}
.t-Hot{background:var(--hotbg);color:var(--hot)}.t-Warm{background:var(--warmbg);color:var(--warm)}.t-Watch{background:var(--watchbg);color:var(--watch)}
.mom{font-weight:700;font-size:14px}.m-up{color:var(--up)}.m-down{color:var(--down)}.m-flat{color:var(--muted)}.m-new{color:var(--accent2);font-size:11px;font-weight:700}
.roles{font-variant-numeric:tabular-nums;font-weight:650}
.sig{font-size:12.5px;color:#cdd3de}.sig .p{display:inline-block;background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:2px 7px;margin:2px 3px 0 0}
.why{font-size:12.5px;color:var(--muted);font-style:italic;max-width:240px}
.yes{color:var(--accent2);font-weight:700}.no{color:var(--muted)}
.muted{color:var(--muted)}
footer{border-top:1px solid var(--line);padding:28px 0 64px;color:var(--muted);font-size:13px}footer .wrap{max-width:780px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}
.legend{display:flex;gap:18px;margin-top:10px;font-size:12.5px;color:var(--muted)}.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:middle}
.wk{border-bottom:1px solid var(--line);padding:14px 0}.wk:last-child{border-bottom:0}.wkhead{font-size:14.5px;margin-bottom:8px}
.wkrow{display:flex;gap:8px;align-items:baseline;margin:4px 0;flex-wrap:wrap}.lbl{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);min-width:68px}
.chip{display:inline-block;font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;margin:2px 0}.chip.up{background:var(--hotbg);color:var(--up)}.chip.down{background:var(--watchbg);color:var(--down)}
.nav a{margin-right:4px}
'''

NAV = ('<p class="byline" style="margin-top:6px" class="nav">__NAV__</p>')

# ---------------------------------- index ------------------------------------
INDEX = r'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Territory Radar - Account buying-signal intelligence for AEs</title>
<meta name="description" content="An automated territory-intelligence tool that scores target accounts on buying signals from hiring, funding, and leadership activity.">
<style>__CSS__</style></head><body>
<header><div class="wrap">
  <p class="eyebrow">B2B Sales · Territory Intelligence</p>
  <h1>Territory Radar</h1>
  <p class="sub">An automated territory-research tool for Account Executives. It scores the accounts in a sales territory on real buying signals - hiring, funding, and leadership moves - and tracks which ones are heating up, so account planning starts from "why now," not a static list.</p>
  <p class="byline">Built by <b>Eric Hastie</b> · sample territory · updated __DATEHUMAN__ · <span class="muted">a portfolio project</span></p>
  <p class="byline" style="margin-top:6px"><b>Territory board</b> &nbsp;·&nbsp; <a href="history.html">Momentum &amp; history</a> &nbsp;·&nbsp; <a href="roles.html">All open roles →</a></p>
  <div class="callout"><b>What this models:</b> an AE selling __PRODUCT__. A <b>buying signal</b> here means __SIGNAL_DESC__. Swap the config and the account list, and the same engine works for any product and territory.</div>
  <div class="stats">
    <div class="stat"><div class="n">__ACCOUNTS__</div><div class="l">accounts in territory</div></div>
    <div class="stat"><div class="n">__HOT__</div><div class="l">🔥 hot right now</div></div>
    <div class="stat"><div class="n">__ROLES__<span style="color:var(--muted);font-size:16px"> / __TOTALROLES__</span></div><div class="l">relevant / total open roles</div></div>
    <div class="stat"><div class="n">__MOVERS__</div><div class="l">moved this week</div></div>
  </div>
</div></header>

<section class="about"><div class="wrap">
  <h2>About this project</h2>
  <p>This started as the engine behind a <a href="https://eric-hastie.github.io/remote-ae-job-hunt/" target="_blank" rel="noopener">remote-AE job search</a> - a pipeline that screens companies against a profile, verifies live job postings, and tracks change week over week. That job-hunt build was the prototype; <b>Territory Radar</b> re-points the same engine at the other side of the desk: instead of finding jobs, it finds buying signals across a sales territory. Job postings are one of the cleanest, earliest intent signals in B2B - a company scaling its platform team or hiring an infra leader is telling you about budget and initiatives before any intent-data vendor flags it.</p>
  <h2 style="margin-top:30px">How the signal score works</h2>
  <p>Each account's score is a transparent, weighted sum of verified signals, so the ranking is explainable - no black box:</p>
  <div class="score-help">
    <code>relevant open role &times; __W_ROLES__</code>
    <code>recent funding +__W_FUNDING__</code>
    <code>new eng leadership +__W_LEADERSHIP__</code>
    <code>expansion / new region +__W_EXPANSION__</code>
  </div>
  <div class="score-help" style="margin-top:8px">
    <span><span class="tier t-Hot">Hot</span> &nbsp;score &ge; __HOT_T__</span>
    <span><span class="tier t-Warm">Warm</span> &nbsp;&ge; __WARM__</span>
    <span><span class="tier t-Watch">Watch</span> &nbsp;below __WARM__</span>
  </div>
</div></section>

<div class="wrap">
  <div class="controls">
    <input id="q" type="search" placeholder="Search account, industry, signal…" autocomplete="off">
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
      <th data-k="account">Account <span class="arw"></span></th>
      <th data-k="score">Signal <span class="arw">▼</span></th>
      <th data-k="mom">Momentum <span class="arw"></span></th>
      <th data-k="roles">Roles (rel / total) <span class="arw"></span></th>
      <th>Key signals</th>
      <th>Why now</th>
    </tr></thead>
    <tbody id="rows"></tbody>
  </table></div>
</div>

<footer><div class="wrap">
  <p><b>Methodology.</b> Sample territory, signals verified __DATEHUMAN__ against company career pages / ATS and public sources; re-verified weekly. Signal counts and firmographics are best-effort from public data. This is illustrative demo data on real companies - a live deployment would run against your actual book of business in a <b>private</b> repo.</p>
  <p>Prototyped from the remote-AE job-hunt tool. Built by Eric Hastie · auto-refreshed weekly.</p>
</div></footer>

<script>
const DATA = __DATA__;
const tbody=document.getElementById('rows'),q=document.getElementById('q'),count=document.getElementById('count');
let seg='all',sortK='score',sortDir=-1;
const MOM={up:'<span class="mom m-up">▲</span>',down:'<span class="mom m-down">▼</span>',flat:'<span class="mom m-flat">▬</span>',new:'<span class="mom m-new">NEW</span>'};
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
  tbody.innerHTML=list.map(r=>`<tr>
    <td><div class="acct">${r.url?`<a href="${r.url}" target="_blank" rel="noopener">${r.account}</a>`:r.account}</div>
        <div class="meta">${[r.industry,r.hq,r.headcount,r.funding].filter(Boolean).join(' · ')}</div></td>
    <td><div class="scorewrap"><span class="scoren">${r.score}</span><span class="tier t-${r.tier}">${r.tier}</span></div></td>
    <td>${MOM[r.mom]||''} ${r.mom_delta?`<span class="muted" style="font-size:12px">${r.mom_delta>0?'+':''}${r.mom_delta}</span>`:''}</td>
    <td><span class="roles">${r.roles}</span> <span class="muted">/ ${r.total_roles||0}</span></td>
    <td class="sig">${sigChips(r.signals)}</td>
    <td class="why">${r.why||''}</td>
  </tr>`).join('');
  count.textContent=list.length+' of '+DATA.length+' accounts';
}
document.querySelectorAll('#seg button').forEach(b=>b.onclick=()=>{seg=b.dataset.seg;document.querySelectorAll('#seg button').forEach(x=>x.classList.remove('on'));b.classList.add('on');render();});
document.querySelectorAll('thead th[data-k]').forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(sortK===k){sortDir*=-1}else{sortK=k;sortDir=(k==='score'||k==='roles')?-1:1}document.querySelectorAll('.arw').forEach(a=>a.textContent='');th.querySelector('.arw').textContent=sortDir>0?'▲':'▼';render();});
q.oninput=render;render();
</script>
</body></html>'''

# ---------------------------------- history ----------------------------------
HISTORY = r'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Momentum & History - Territory Radar</title>
<style>__CSS__</style></head><body>
<header><div class="wrap">
  <p class="eyebrow">B2B Sales · Territory Intelligence</p>
  <h1>Momentum &amp; History</h1>
  <p class="sub">How the territory is moving over time. Each weekly run is snapshotted, so you can see which accounts are heating up, which are cooling, and how overall hiring signal in the territory is trending.</p>
  <p class="byline"><a href="./">← Territory board</a> &nbsp;·&nbsp; <a href="roles.html">All open roles</a> &nbsp;·&nbsp; <span class="muted">updated __DATEHUMAN__</span></p>
  <div class="stats">
    <div class="stat"><div class="n">__WEEKS__</div><div class="l">weekly snapshots</div></div>
    <div class="stat"><div class="n">__HOT__</div><div class="l">hot accounts now</div></div>
    <div class="stat"><div class="n">__TOTALROLES__</div><div class="l">total open roles now</div></div>
    <div class="stat"><div class="n">__NETTOTAL__</div><div class="l">total roles vs start</div></div>
  </div>
</div></header>
<div class="wrap">
  <section><h2>Hiring signal across the territory</h2><div class="panel"><div id="chart"></div></div></section>
  <section><h2>Weekly movers</h2><div class="panel" id="log"></div></section>
</div>
<footer><div class="wrap">Total open roles is the aggregate of every open position across the territory; relevant roles are the subset that match the signal profile. Momentum is the week-over-week change in each account's signal score, from the dated snapshots in <code>data/</code>. Built by Eric Hastie · auto-refreshed weekly.</div></footer>
<script>
const M=__METRICS__;
function drawChart(){
  const w=720,h=300,pad={l:44,r:16,t:16,b:42},iw=w-pad.l-pad.r,ih=h-pad.t-pad.b,n=M.length;
  const maxv=Math.max(...M.map(d=>d.total_roles),1);
  const X=i=>n<=1?pad.l+iw/2:pad.l+iw*i/(n-1),Y=v=>pad.t+ih*(1-v/maxv);
  const S=[{k:'total_roles',c:'#6c8cff',l:'Total open roles'},{k:'roles',c:'#41d3a3',l:'Relevant roles'}];
  let s=`<svg viewBox="0 0 ${w} ${h}" width="100%" role="img" aria-label="Hiring signal across the territory over time">`;
  for(let g=0;g<=4;g++){const v=Math.round(maxv*g/4),yy=Y(v);s+=`<line x1="${pad.l}" y1="${yy}" x2="${w-pad.r}" y2="${yy}" stroke="#2a2f3a"/><text x="${pad.l-8}" y="${yy+4}" fill="#9aa3b2" font-size="11" text-anchor="end">${v}</text>`;}
  const step=Math.max(1,Math.ceil(n/8));
  M.forEach((d,i)=>{if(i%step===0||i===n-1)s+=`<text x="${X(i)}" y="${h-pad.b+18}" fill="#9aa3b2" font-size="10" text-anchor="middle">${d.date.slice(5)}</text>`;});
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
<title>All open roles - Territory Radar</title>
<style>__CSS__</style></head><body>
<header><div class="wrap">
  <p class="eyebrow">B2B Sales · Territory Intelligence</p>
  <h1>All open roles</h1>
  <p class="sub">Every open position across the territory - the full inventory behind the signal scores. Use the "unmatched" filter to scan for titles that <i>should</i> count as a buying signal but don't yet, then they can be added to the signal profile.</p>
  <p class="byline"><a href="./">← Territory board</a> &nbsp;·&nbsp; <a href="history.html">Momentum &amp; history</a> &nbsp;·&nbsp; <span class="muted">updated __DATEHUMAN__</span></p>
  <div class="stats">
    <div class="stat"><div class="n">__TOTAL__</div><div class="l">open roles tracked</div></div>
    <div class="stat"><div class="n">__MATCHED__</div><div class="l">count as a signal</div></div>
    <div class="stat"><div class="n">__UNMATCHED__</div><div class="l">not matched (review)</div></div>
    <div class="stat"><div class="n">__NACCT__</div><div class="l">accounts covered</div></div>
  </div>
</div></header>
<div class="wrap">
  <div class="controls">
    <input id="q" type="search" placeholder="Search title, account, location…" autocomplete="off">
    <div class="seg" id="seg">
      <button data-seg="all" class="on">All</button>
      <button data-seg="match">Counts as signal</button>
      <button data-seg="unmatch">Unmatched</button>
    </div>
    <span class="count" id="count"></span>
  </div>
  <div class="tablewrap"><table>
    <thead><tr>
      <th data-k="account">Account <span class="arw"></span></th>
      <th data-k="title">Title <span class="arw"></span></th>
      <th data-k="location">Location <span class="arw"></span></th>
      <th data-k="matched">Signal? <span class="arw"></span></th>
    </tr></thead>
    <tbody id="rows"></tbody>
  </table></div>
</div>
<footer><div class="wrap">"Signal?" marks whether a title matched the current signal profile (SRE / platform / DevOps / infrastructure / cloud / Kubernetes / observability). Spot one that should match? It gets added to the profile and re-scored on the next run. Built by Eric Hastie · auto-refreshed weekly.</div></footer>
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
    <td>${r.account}</td>
    <td>${r.url?`<a href="${r.url}" target="_blank" rel="noopener">${r.title}</a>`:r.title}</td>
    <td class="muted">${r.location||''}</td>
    <td>${r.matched?'<span class="yes">✓ yes</span>':'<span class="no">-</span>'}</td>
  </tr>`).join('');
  count.textContent=list.length+' of '+ROLES.length+' roles';
}
document.querySelectorAll('#seg button').forEach(b=>b.onclick=()=>{seg=b.dataset.seg;document.querySelectorAll('#seg button').forEach(x=>x.classList.remove('on'));b.classList.add('on');render();});
document.querySelectorAll('thead th[data-k]').forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(sortK===k){sortDir*=-1}else{sortK=k;sortDir=1}document.querySelectorAll('.arw').forEach(a=>a.textContent='');th.querySelector('.arw').textContent=sortDir>0?'▲':'▼';render();});
q.oninput=render;render();
</script>
</body></html>'''

def read_roles():
    if not os.path.exists(ROLES_PATH):
        return []
    with open(ROLES_PATH, newline="") as f:
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

def main():
    today = datetime.date.today()
    human = today.strftime("%B %-d, %Y") if os.name != "nt" else today.strftime("%B %d, %Y")

    if not os.path.exists(CSV_PATH):
        print("no data/latest.csv yet - skipping build")
        return

    board = read_csv(CSV_PATH)
    snaps = snapshots()
    board = add_momentum(board, snaps)
    board.sort(key=lambda r: r["score"], reverse=True)
    movers = sum(1 for r in board if r.get("mom") in ("up", "down"))

    idx = (INDEX
           .replace("__CSS__", CSS)
           .replace("__DATA__", json.dumps(board))
           .replace("__DATEHUMAN__", human)
           .replace("__PRODUCT__", CONFIG["product"])
           .replace("__SIGNAL_DESC__", CONFIG["signal_desc"])
           .replace("__ACCOUNTS__", str(len(board)))
           .replace("__HOT__", str(sum(1 for r in board if r["tier"] == "Hot")))
           .replace("__ROLES__", str(sum(r["roles"] for r in board)))
           .replace("__TOTALROLES__", str(sum(r["total_roles"] for r in board)))
           .replace("__MOVERS__", str(movers))
           .replace("__W_ROLES__", str(W["roles"]))
           .replace("__W_FUNDING__", str(W["funding"]))
           .replace("__W_LEADERSHIP__", str(W["leadership"]))
           .replace("__W_EXPANSION__", str(W["expansion"]))
           .replace("__HOT_T__", str(CONFIG["hot"]))
           .replace("__WARM__", str(CONFIG["warm"])))
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(idx)
    print(f"built index.html: {len(board)} accounts, "
          f"{sum(1 for r in board if r['tier']=='Hot')} hot, "
          f"{sum(r['total_roles'] for r in board)} total roles, {movers} movers")

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
                .replace("__DATEHUMAN__", human)
                .replace("__WEEKS__", str(len(metrics)))
                .replace("__HOT__", str(metrics[-1]["hot"]))
                .replace("__TOTALROLES__", str(metrics[-1]["total_roles"]))
                .replace("__NETTOTAL__", f"+{net}" if net >= 0 else str(net)))
        with open(os.path.join(ROOT, "history.html"), "w") as f:
            f.write(hist)
        print(f"built history.html: {len(metrics)} snapshots, net total roles {net:+d}")

    # roles inventory
    roles = read_roles()
    if roles:
        matched = sum(1 for r in roles if r["matched"])
        rl = (ROLES
              .replace("__CSS__", CSS)
              .replace("__ROLES__", json.dumps(roles))
              .replace("__DATEHUMAN__", human)
              .replace("__TOTAL__", str(len(roles)))
              .replace("__MATCHED__", str(matched))
              .replace("__UNMATCHED__", str(len(roles) - matched))
              .replace("__NACCT__", str(len({r["account"] for r in roles}))))
        with open(os.path.join(ROOT, "roles.html"), "w") as f:
            f.write(rl)
        print(f"built roles.html: {len(roles)} open roles ({matched} matched)")
    else:
        print("no data/roles-latest.csv yet - skipping roles.html")

if __name__ == "__main__":
    main()
