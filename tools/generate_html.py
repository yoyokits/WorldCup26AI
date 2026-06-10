#!/usr/bin/env python3
"""Generate docs/ pages for FIFA World Cup 2026 predictions.
Run: python tools/generate_html.py
Output: docs/index.html, docs/group_*.html, docs/knockout.html
(docs/ is the GitHub Pages publishing source.)
"""

import csv
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
HTML = ROOT / "docs"   # GitHub Pages source folder
HTML.mkdir(exist_ok=True)

# ──────────────────────────────────────────────
# 1. TEAM DATA
# ──────────────────────────────────────────────
TEAMS = {}
with open(ROOT / "tools" / "ratings.csv") as f:
    for row in csv.DictReader(f):
        TEAMS[row["team"]] = {
            "slug": row["slug"],
            "group": row["group"],
            "conf": row["confederation"],
            "rank": int(row["fifa_rank"]),
            "elo": int(row["elo"]),
            "host": row["host"] == "1",
        }

# Title odds from Simulation.md (top 32 extracted)
TITLE_ODDS = {
    "Argentina": 15.1, "France": 10.2, "Spain": 9.3, "England": 7.2,
    "Brazil": 6.6, "Netherlands": 5.5, "Portugal": 5.3, "Italy": 4.8,
    "Germany": 4.1, "Uruguay": 3.0, "Croatia": 2.9, "Morocco": 2.5,
    "Colombia": 2.4, "Senegal": 2.2, "Switzerland": 2.2, "Japan": 1.4,
    "USA": 1.4, "Serbia": 1.4, "Ecuador": 1.3, "Turkey": 1.3,
    "Iran": 1.2, "Mexico": 1.1, "South Korea": 1.0, "Ukraine": 1.0,
    "Sweden": 0.9, "Paraguay": 0.7, "Egypt": 0.7, "Poland": 0.6,
    "Wales": 0.6, "Nigeria": 0.6, "Australia": 0.3, "Canada": 0.3,
    "Slovenia": 0.2, "Cameroon": 0.1, "South Africa": 0.1, "Panama": 0.1,
    "Ghana": 0.1, "Qatar": 0.1, "Costa Rica": 0.1, "Tunisia": 0.1,
    "Guinea": 0.1, "Jamaica": 0.1, "Honduras": 0.0, "Bolivia": 0.0,
    "Saudi Arabia": 0.0, "New Zealand": 0.0, "Fiji": 0.0, "Tonga": 0.0,
}

# ──────────────────────────────────────────────
# 2. GROUP STAGE MATCHES (from data/GroupStage.md)
# ──────────────────────────────────────────────
# Format: (match_id, date, home, away, pred_home, pred_away, venue)
GROUP_MATCHES = {
    "A": [
        ("A-1","Jun 12","Argentina","Morocco",1,0,"AT&T Stadium, Dallas"),
        ("A-2","Jun 12","Jamaica","Egypt",1,2,"Hard Rock, Miami"),
        ("A-3","Jun 18","Argentina","Jamaica",2,0,"AT&T Stadium, Dallas"),
        ("A-4","Jun 18","Morocco","Egypt",2,1,"Levi's, Santa Clara"),
        ("A-5","Jun 25","Argentina","Egypt",2,0,"MetLife, NJ"),
        ("A-6","Jun 25","Morocco","Jamaica",2,1,"Arrowhead, KC"),
    ],
    "B": [
        ("B-1","Jun 12","Spain","Japan",1,0,"SoFi, Los Angeles"),
        ("B-2","Jun 12","USA","Ghana",2,1,"SoFi, Los Angeles"),
        ("B-3","Jun 19","Spain","USA",2,1,"AT&T Stadium, Dallas"),
        ("B-4","Jun 19","Japan","Ghana",2,1,"Mercedes-Benz, Atlanta"),
        ("B-5","Jun 26","Spain","Ghana",2,0,"Gillette, Boston"),
        ("B-6","Jun 26","Japan","USA",1,2,"Lumen, Seattle"),
    ],
    "C": [
        ("C-1","Jun 13","Brazil","Switzerland",2,1,"NRG, Houston"),
        ("C-2","Jun 13","South Korea","Cameroon",2,1,"Lincoln, Philadelphia"),
        ("C-3","Jun 19","Brazil","South Korea",1,0,"NRG, Houston"),
        ("C-4","Jun 19","Switzerland","Cameroon",2,1,"Arrowhead, KC"),
        ("C-5","Jun 26","Brazil","Cameroon",2,0,"AT&T, Dallas"),
        ("C-6","Jun 26","Switzerland","South Korea",2,1,"Gillette, Boston"),
    ],
    "D": [
        ("D-1","Jun 13","France","Uruguay",1,0,"MetLife, NJ"),
        ("D-2","Jun 13","Canada","Saudi Arabia",2,1,"BMO Field, Toronto"),
        ("D-3","Jun 20","France","Canada",1,0,"Lincoln, Philadelphia"),
        ("D-4","Jun 20","Uruguay","Saudi Arabia",1,0,"Mercedes-Benz, Atlanta"),
        ("D-5","Jun 27","France","Saudi Arabia",2,0,"MetLife, NJ"),
        ("D-6","Jun 27","Uruguay","Canada",2,1,"Arrowhead, KC"),
    ],
    "E": [
        ("E-1","Jun 14","Portugal","Croatia",2,1,"SoFi, Los Angeles"),
        ("E-2","Jun 14","Ecuador","Tunisia",2,1,"Hard Rock, Miami"),
        ("E-3","Jun 20","Portugal","Ecuador",2,1,"NRG, Houston"),
        ("E-4","Jun 20","Croatia","Tunisia",1,0,"Lumen, Seattle"),
        ("E-5","Jun 27","Portugal","Tunisia",1,0,"AT&T, Dallas"),
        ("E-6","Jun 27","Croatia","Ecuador",2,1,"Mercedes-Benz, Atlanta"),
    ],
    "F": [
        ("F-1","Jun 14","Germany","Colombia",2,1,"Levi's, Santa Clara"),
        ("F-2","Jun 14","Nigeria","Honduras",2,1,"Lincoln, Philadelphia"),
        ("F-3","Jun 21","Germany","Nigeria",2,1,"AT&T, Dallas"),
        ("F-4","Jun 21","Colombia","Honduras",1,0,"NRG, Houston"),
        ("F-5","Jun 28","Germany","Honduras",2,0,"Gillette, Boston"),
        ("F-6","Jun 28","Colombia","Nigeria",2,1,"Arrowhead, KC"),
    ],
    "G": [
        ("G-1","Jun 11","Mexico","Australia",2,1,"Estadio Azteca, Mexico City"),
        ("G-2","Jun 11","Netherlands","Serbia",2,1,"Estadio Akron, Guadalajara"),
        ("G-3","Jun 17","Netherlands","Mexico",2,1,"Estadio BBVA, Monterrey"),
        ("G-4","Jun 17","Serbia","Australia",2,1,"Estadio Azteca, Mexico City"),
        ("G-5","Jun 24","Netherlands","Australia",1,0,"Estadio Akron, Guadalajara"),
        ("G-6","Jun 24","Mexico","Serbia",2,1,"Estadio BBVA, Monterrey"),
    ],
    "H": [
        ("H-1","Jun 15","England","Slovenia",1,0,"Lincoln, Philadelphia"),
        ("H-2","Jun 15","Paraguay","Tonga",2,0,"Hard Rock, Miami"),
        ("H-3","Jun 21","England","Paraguay",1,0,"Gillette, Boston"),
        ("H-4","Jun 21","Slovenia","Tonga",2,0,"MetLife, NJ"),
        ("H-5","Jun 28","England","Tonga",3,0,"AT&T, Dallas"),
        ("H-6","Jun 28","Slovenia","Paraguay",1,2,"Lumen, Seattle"),
    ],
    "I": [
        ("I-1","Jun 15","Italy","Wales",2,1,"Mercedes-Benz, Atlanta"),
        ("I-2","Jun 15","Qatar","Fiji",2,0,"Arrowhead, KC"),
        ("I-3","Jun 22","Italy","Qatar",1,0,"NRG, Houston"),
        ("I-4","Jun 22","Wales","Fiji",2,0,"Levi's, Santa Clara"),
        ("I-5","Jun 29","Italy","Fiji",2,0,"AT&T, Dallas"),
        ("I-6","Jun 29","Wales","Qatar",2,1,"MetLife, NJ"),
    ],
    "J": [
        ("J-1","Jun 16","Senegal","Poland",2,1,"Gillette, Boston"),
        ("J-2","Jun 16","Costa Rica","New Zealand",2,1,"Lumen, Seattle"),
        ("J-3","Jun 22","Senegal","Costa Rica",2,1,"Mercedes-Benz, Atlanta"),
        ("J-4","Jun 22","Poland","New Zealand",1,0,"Hard Rock, Miami"),
        ("J-5","Jun 29","Senegal","New Zealand",2,0,"Gillette, Boston"),
        ("J-6","Jun 29","Poland","Costa Rica",2,1,"AT&T, Dallas"),
    ],
    "K": [
        ("K-1","Jun 16","Iran","Sweden",2,1,"SoFi, Los Angeles"),
        ("K-2","Jun 16","Panama","Bolivia",2,1,"Levi's, Santa Clara"),
        ("K-3","Jun 23","Iran","Panama",2,1,"NRG, Houston"),
        ("K-4","Jun 23","Sweden","Bolivia",2,1,"Lincoln, Philadelphia"),
        ("K-5","Jun 30","Iran","Bolivia",2,1,"Mercedes-Benz, Atlanta"),
        ("K-6","Jun 30","Sweden","Panama",2,1,"Arrowhead, KC"),
    ],
    "L": [
        ("L-1","Jun 17","Ukraine","Turkey",1,2,"Gillette, Boston"),
        ("L-2","Jun 17","South Africa","Guinea",2,1,"Lumen, Seattle"),
        ("L-3","Jun 23","Ukraine","South Africa",2,1,"Lincoln, Philadelphia"),
        ("L-4","Jun 23","Turkey","Guinea",2,1,"Hard Rock, Miami"),
        ("L-5","Jun 30","Ukraine","Guinea",2,1,"Gillette, Boston"),
        ("L-6","Jun 30","Turkey","South Africa",2,1,"Lumen, Seattle"),
    ],
}

# Predicted standings: (pos, team, P, W, D, L, GF, GA, GD, Pts, qualifier)
# qualifier: "✅" = top-2, "🟡" = possible best 3rd, "" = out
GROUP_STANDINGS = {
    "A": [
        (1,"Argentina",3,3,0,0,5,0,5,9,"✅"),
        (2,"Morocco",3,2,0,1,4,3,1,6,"✅"),
        (3,"Egypt",3,1,0,2,3,5,-2,3,"🟡"),
        (4,"Jamaica",3,0,0,3,2,6,-4,0,""),
    ],
    "B": [
        (1,"Spain",3,3,0,0,5,1,4,9,"✅"),
        (2,"USA",3,2,0,1,5,4,1,6,"✅"),
        (3,"Japan",3,1,0,2,3,4,-1,3,"🟡"),
        (4,"Ghana",3,0,0,3,2,6,-4,0,""),
    ],
    "C": [
        (1,"Brazil",3,3,0,0,5,1,4,9,"✅"),
        (2,"Switzerland",3,2,0,1,5,4,1,6,"✅"),
        (3,"South Korea",3,1,0,2,3,4,-1,3,"🟡"),
        (4,"Cameroon",3,0,0,3,2,6,-4,0,""),
    ],
    "D": [
        (1,"France",3,3,0,0,4,0,4,9,"✅"),
        (2,"Uruguay",3,2,0,1,3,2,1,6,"✅"),
        (3,"Canada",3,1,0,2,3,4,-1,3,"🟡"),
        (4,"Saudi Arabia",3,0,0,3,1,5,-4,0,""),
    ],
    "E": [
        (1,"Portugal",3,3,0,0,5,2,3,9,"✅"),
        (2,"Croatia",3,2,0,1,4,3,1,6,"✅"),
        (3,"Ecuador",3,1,0,2,4,5,-1,3,"🟡"),
        (4,"Tunisia",3,0,0,3,1,4,-3,0,""),
    ],
    "F": [
        (1,"Germany",3,3,0,0,6,2,4,9,"✅"),
        (2,"Colombia",3,2,0,1,4,3,1,6,"✅"),
        (3,"Nigeria",3,1,0,2,4,5,-1,3,"🟡"),
        (4,"Honduras",3,0,0,3,1,5,-4,0,""),
    ],
    "G": [
        (1,"Netherlands",3,3,0,0,5,2,3,9,"✅"),
        (2,"Mexico",3,2,0,1,5,4,1,6,"✅"),
        (3,"Serbia",3,1,0,2,4,5,-1,3,"🟡"),
        (4,"Australia",3,0,0,3,2,5,-3,0,""),
    ],
    "H": [
        (1,"England",3,3,0,0,5,0,5,9,"✅"),
        (2,"Paraguay",3,2,0,1,4,2,2,6,"✅"),
        (3,"Slovenia",3,1,0,2,3,3,0,3,"🟡"),
        (4,"Tonga",3,0,0,3,0,7,-7,0,""),
    ],
    "I": [
        (1,"Italy",3,3,0,0,5,1,4,9,"✅"),
        (2,"Wales",3,2,0,1,5,3,2,6,"✅"),
        (3,"Qatar",3,1,0,2,3,3,0,3,"🟡"),
        (4,"Fiji",3,0,0,3,0,6,-6,0,""),
    ],
    "J": [
        (1,"Senegal",3,3,0,0,6,2,4,9,"✅"),
        (2,"Poland",3,2,0,1,4,3,1,6,"✅"),
        (3,"Costa Rica",3,1,0,2,4,5,-1,3,"🟡"),
        (4,"New Zealand",3,0,0,3,1,5,-4,0,""),
    ],
    "K": [
        (1,"Iran",3,3,0,0,6,3,3,9,"✅"),
        (2,"Sweden",3,2,0,1,5,4,1,6,"✅"),
        (3,"Panama",3,1,0,2,4,5,-1,3,"🟡"),
        (4,"Bolivia",3,0,0,3,3,6,-3,0,""),
    ],
    "L": [
        (1,"Turkey",3,3,0,0,6,3,3,9,"✅"),
        (2,"Ukraine",3,2,0,1,5,4,1,6,"✅"),
        (3,"South Africa",3,1,0,2,4,5,-1,3,"🟡"),
        (4,"Guinea",3,0,0,3,3,6,-3,0,""),
    ],
}

# Knockout bracket predictions
KNOCKOUT = [
    # R32
    ("R32-1","Jul 1","Argentina","Slovenia","2-0","Argentina"),
    ("R32-2","Jul 1","France","Wales","2-0","France"),
    ("R32-3","Jul 2","Spain","Turkey","2-1","Spain"),
    ("R32-4","Jul 2","England","Poland","2-0","England"),
    ("R32-5","Jul 2","Brazil","Canada","2-0","Brazil"),
    ("R32-6","Jul 2","Netherlands","Paraguay","2-0","Netherlands"),
    ("R32-7","Jul 3","Portugal","Sweden","2-1","Portugal"),
    ("R32-8","Jul 3","Italy","Serbia","2-1","Italy"),
    ("R32-9","Jul 3","Germany","Ukraine","2-1","Germany"),
    ("R32-10","Jul 3","Uruguay","Ecuador","2-1","Uruguay"),
    ("R32-11","Jul 4","Croatia","Nigeria","2-1","Croatia"),
    ("R32-12","Jul 4","Morocco","South Korea","2-1","Morocco"),
    ("R32-13","Jul 4","Senegal","Japan","2-1","Senegal"),
    ("R32-14","Jul 4","Switzerland","Iran","2-1","Switzerland"),
    ("R32-15","Jul 5","Colombia","Egypt","2-1","Colombia"),
    ("R32-16","Jul 5","Mexico","USA","1-2","USA"),
    # R16
    ("R16-1","Jul 6","Argentina","France","1-0","Argentina"),
    ("R16-2","Jul 6","Spain","England","1-1 (3-2p)","Spain"),
    ("R16-3","Jul 7","Brazil","Netherlands","2-1","Brazil"),
    ("R16-4","Jul 7","Portugal","Italy","1-0","Portugal"),
    ("R16-5","Jul 7","Germany","Uruguay","2-1","Germany"),
    ("R16-6","Jul 7","Croatia","Morocco","1-0","Croatia"),
    ("R16-7","Jul 8","Senegal","Switzerland","1-2","Switzerland"),
    ("R16-8","Jul 8","Colombia","USA","1-0","Colombia"),
    # QF
    ("QF-1","Jul 9","Argentina","Brazil","1-0","Argentina"),
    ("QF-2","Jul 9","Spain","Portugal","1-1 (4-3p)","Spain"),
    ("QF-3","Jul 10","Germany","Croatia","2-1","Germany"),
    ("QF-4","Jul 10","Switzerland","Colombia","1-0","Switzerland"),
    # SF
    ("SF-1","Jul 14","Argentina","Spain","2-1","Argentina"),
    ("SF-2","Jul 14","Germany","Switzerland","2-0","Germany"),
    # 3PL
    ("3PL","Jul 18","Spain","Switzerland","2-1","Spain"),
    # Final
    ("FIN","Jul 19","Argentina","Germany","2-1","Argentina"),
]


# ──────────────────────────────────────────────
# 3. HTML HELPERS
# ──────────────────────────────────────────────
STYLES = """/* FIFA World Cup 2026 — modern stylesheet (generated by tools/generate_html.py) */
:root{
  --blue:#0033A0;--blue-600:#1a4fd6;--blue-300:#6f9bff;
  --red:#C8102E;--gold:#F5B83D;--gold-deep:#E09600;
  --ink:#0B1020;--ink-soft:#1c2540;
  --bg:#eef2fb;--surface:#ffffff;--surface-2:#f6f8ff;
  --line:#e6eaf3;--grey:#6b7280;--grey-soft:#9aa3b2;--green:#16A34A;
  --radius:18px;--radius-sm:12px;
  --shadow-sm:0 1px 2px rgba(11,16,32,.06),0 2px 8px rgba(11,16,32,.05);
  --shadow-md:0 8px 24px rgba(11,16,32,.10);
  --shadow-lg:0 18px 50px rgba(11,16,32,.18);
  --ring:0 0 0 1px rgba(11,16,32,.06);
  --grad-blue:linear-gradient(135deg,#0a2a8c 0%,#0033A0 45%,#1a4fd6 100%);
  --grad-hero:radial-gradient(1200px 600px at 15% -10%,rgba(111,155,255,.35),transparent 60%),radial-gradient(900px 500px at 110% 10%,rgba(245,184,61,.22),transparent 55%),linear-gradient(135deg,#070b1f 0%,#0a1230 50%,#0b1f5c 100%);
  --grad-gold:linear-gradient(135deg,#F5B83D,#E09600);
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0a0e1c;--surface:#121830;--surface-2:#0e1428;
    --ink:#eef2ff;--ink-soft:#c7cee6;--line:#222b48;
    --grey:#9aa3b2;--grey-soft:#6b7488;--ring:0 0 0 1px rgba(255,255,255,.05);
    --shadow-sm:0 1px 2px rgba(0,0,0,.4);
    --shadow-md:0 10px 28px rgba(0,0,0,.45);
    --shadow-lg:0 20px 60px rgba(0,0,0,.6);
  }
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.5;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
}
a{color:var(--blue-600);text-decoration:none}
a:hover{color:var(--blue);text-decoration:none}
::selection{background:var(--gold);color:var(--ink)}

/* SCROLL PROGRESS */
.scroll-progress{position:fixed;top:0;left:0;height:3px;width:0;z-index:120;
  background:var(--grad-gold);box-shadow:0 0 12px rgba(245,184,61,.6);transition:width .1s linear}

/* HEADER */
.site-header{position:sticky;top:0;z-index:100;
  background:var(--grad-blue);color:#fff;padding:.9rem 1.5rem;
  display:flex;align-items:center;gap:1rem;flex-wrap:wrap;
  box-shadow:0 6px 22px rgba(10,42,140,.28);
  border-bottom:1px solid rgba(255,255,255,.08)}
.site-header .logo{font-size:1.9rem;line-height:1;filter:drop-shadow(0 2px 6px rgba(0,0,0,.3))}
.site-header h1{font-family:'Sora','Inter',sans-serif;font-size:1.2rem;font-weight:800;letter-spacing:-.02em}
.site-header .subtitle{font-size:.78rem;opacity:.82;font-weight:500}
.badge{background:rgba(255,255,255,.14);color:#fff;padding:.32rem .7rem;border-radius:999px;
  font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em;
  border:1px solid rgba(255,255,255,.18);backdrop-filter:blur(6px)}
.badge.gold{background:var(--grad-gold);color:var(--ink);border:none;box-shadow:0 4px 14px rgba(224,150,0,.4)}
.site-header .badge:last-child{margin-left:auto}

/* NAV */
nav{position:sticky;top:56px;z-index:90;display:flex;gap:.25rem;
  background:color-mix(in srgb,var(--surface) 82%,transparent);
  backdrop-filter:saturate(160%) blur(12px);
  padding:.5rem 1.5rem;overflow-x:auto;white-space:nowrap;
  border-bottom:1px solid var(--line);scrollbar-width:thin}
nav::-webkit-scrollbar{height:0}
nav a{color:var(--grey);font-size:.82rem;font-weight:600;padding:.4rem .7rem;border-radius:999px;
  transition:background .18s,color .18s,transform .18s}
nav a:hover{background:var(--surface-2);color:var(--blue);transform:translateY(-1px)}
nav a.active{background:var(--grad-blue);color:#fff;box-shadow:0 4px 12px rgba(10,42,140,.35)}

/* MAIN LAYOUT */
main{max-width:1140px;margin:0 auto;padding:1.6rem 1.4rem 0}
.section-reveal{opacity:0;transform:translateY(14px);transition:opacity .6s ease,transform .6s ease}
.section-reveal.in{opacity:1;transform:none}
h2{font-family:'Sora','Inter',sans-serif;font-size:1.22rem;font-weight:800;letter-spacing:-.01em;
   margin:1.8rem 0 .9rem;display:flex;align-items:center;gap:.55rem;color:var(--ink)}
h2::before{content:"";width:6px;height:1.05em;border-radius:4px;background:var(--grad-gold);flex:none}
h3{font-size:.95rem;font-weight:700;margin:0 0 .7rem;color:var(--ink-soft);
   display:flex;align-items:center;gap:.4rem}

/* CARDS */
.card{background:var(--surface);border-radius:var(--radius);box-shadow:var(--shadow-sm);
  border:1px solid var(--line);padding:1.25rem;margin-bottom:1rem;transition:box-shadow .2s,transform .2s}
.card:hover{box-shadow:var(--shadow-md)}
.card.flush{padding:0;overflow:hidden}
.card-header{display:flex;align-items:center;gap:.6rem;margin-bottom:.8rem}
.card-header h2{margin:0;font-size:1rem}

/* FLAGS */
.flag{width:28px;height:21px;object-fit:cover;border-radius:4px;
  box-shadow:0 0 0 1px rgba(11,16,32,.12),0 1px 3px rgba(11,16,32,.18);flex:none}
.flag-lg{width:42px;height:31px;border-radius:5px}

/* MATCH TABLE */
.match-table{width:100%;border-collapse:collapse;font-size:.88rem}
.match-table thead th{background:var(--surface-2);color:var(--grey);
  padding:.6rem .7rem;text-align:left;font-weight:700;font-size:.72rem;
  text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--line)}
.match-table td{padding:.6rem .7rem;border-bottom:1px solid var(--line);vertical-align:middle}
.match-table tr:last-child td{border-bottom:none}
.match-table tbody tr{transition:background .15s}
.match-table tbody tr:hover td{background:var(--surface-2)}
.team-cell{display:flex;align-items:center;gap:.5rem;min-width:130px;font-weight:600}
.score-cell{text-align:center;font-family:'JetBrains Mono',ui-monospace,monospace;font-weight:700;
  white-space:nowrap;min-width:96px;font-size:.92rem}
.pred{display:inline-block;color:var(--grey);font-style:normal;font-weight:700;
  background:var(--surface-2);border:1px solid var(--line);border-radius:999px;padding:.12rem .55rem}
.actual{color:var(--ink)}
.date-cell{color:var(--grey);font-size:.78rem;white-space:nowrap;font-weight:600}
.venue-cell{color:var(--grey-soft);font-size:.76rem}

/* STANDINGS TABLE */
.stand-table{width:100%;border-collapse:collapse;font-size:.86rem}
.stand-table thead th{background:var(--surface-2);color:var(--grey);padding:.55rem .6rem;text-align:center;
  font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em;border-bottom:1px solid var(--line)}
.stand-table th:first-child,.stand-table th:nth-child(2){text-align:left}
.stand-table td{padding:.55rem .6rem;border-bottom:1px solid var(--line);text-align:center}
.stand-table td:nth-child(2){text-align:left}
.stand-table tr:last-child td{border-bottom:none}
.stand-table tr.qualify-1 td:first-child{box-shadow:inset 4px 0 0 var(--blue)}
.stand-table tr.qualify-2 td:first-child{box-shadow:inset 4px 0 0 var(--blue-300)}
.stand-table tr.qualify-3rd td:first-child{box-shadow:inset 4px 0 0 var(--gold)}
.stand-table td.pts{font-weight:800;color:var(--blue)}
.stand-table tbody tr{transition:background .15s}
.stand-table tbody tr:hover td{background:var(--surface-2)}

/* ODDS / ELO BARS */
.odds-team{display:flex;align-items:center;gap:.6rem;margin-bottom:.55rem}
.odds-bar-track{flex:1;height:12px;border-radius:999px;background:var(--surface-2);
  border:1px solid var(--line);overflow:hidden;min-width:60px}
.odds-bar{height:100%;background:linear-gradient(90deg,var(--blue),var(--blue-300));
  border-radius:999px;min-width:3px;
  animation:growBar 1s cubic-bezier(.22,1,.36,1) both}
.odds-bar.gold{background:var(--grad-gold)}
@keyframes growBar{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
.odds-pct{font-size:.8rem;font-weight:800;color:var(--blue);min-width:42px;text-align:right;
  font-family:'JetBrains Mono',monospace}
.odds-team-name{font-size:.82rem;font-weight:600;min-width:108px}

/* GROUP GRID */
.group-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:1rem}
.group-card{background:var(--surface);border-radius:var(--radius);box-shadow:var(--shadow-sm);
  border:1px solid var(--line);padding:1.1rem;transition:transform .18s,box-shadow .18s;position:relative;overflow:hidden}
.group-card::before{content:"";position:absolute;inset:0 0 auto 0;height:4px;background:var(--grad-blue)}
.group-card:hover{transform:translateY(-4px);box-shadow:var(--shadow-lg)}
.group-label{font-family:'Sora',sans-serif;font-size:.72rem;font-weight:800;text-transform:uppercase;
  color:var(--blue);letter-spacing:.1em;margin-bottom:.6rem}
.group-team{display:flex;align-items:center;gap:.45rem;padding:.32rem 0;
  font-size:.85rem;border-bottom:1px solid var(--line)}
.group-team:last-child{border-bottom:none}
.group-team.top1{font-weight:800;color:var(--blue)}
.group-team.top2{font-weight:700}
.group-team .qual-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.dot-q{background:var(--blue);box-shadow:0 0 0 3px rgba(0,51,160,.15)}
.dot-q3{background:var(--gold);box-shadow:0 0 0 3px rgba(245,184,61,.2)}
.dot-out{background:var(--line)}

/* KNOCKOUT BRACKET */
.bracket-wrap{overflow-x:auto;padding-bottom:1rem}
.bracket{display:flex;gap:.4rem;min-width:940px}
.bracket-round{display:flex;flex-direction:column;min-width:178px;gap:.4rem}
.bracket-round-label{text-align:center;font-family:'Sora',sans-serif;font-size:.7rem;font-weight:800;
  text-transform:uppercase;color:#fff;background:var(--grad-blue);padding:.4rem;border-radius:999px;letter-spacing:.07em}
.bracket-matches{display:flex;flex-direction:column;justify-content:space-around;flex:1;gap:.4rem}
.b-match{background:var(--surface);border-radius:var(--radius-sm);box-shadow:var(--shadow-sm);
  overflow:hidden;border:1px solid var(--line);transition:transform .15s,box-shadow .15s}
.b-match:hover{transform:translateY(-2px);box-shadow:var(--shadow-md)}
.b-match.champion{border:2px solid var(--gold);box-shadow:0 8px 24px rgba(224,150,0,.28)}
.b-team{display:flex;align-items:center;gap:.45rem;padding:.4rem .55rem;font-size:.78rem}
.b-team.winner{background:linear-gradient(90deg,rgba(0,51,160,.08),transparent);font-weight:800}
.b-team-name{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.b-score{font-family:'JetBrains Mono',monospace;font-size:.74rem;color:var(--grey);font-weight:700}
.b-divider{height:1px;background:var(--line)}
.champion-box{position:relative;overflow:hidden;
  background:radial-gradient(600px 200px at 50% -40%,rgba(245,184,61,.35),transparent),linear-gradient(135deg,var(--surface),var(--surface-2));
  border:1.5px solid var(--gold);border-radius:var(--radius);padding:1.6rem 1rem;text-align:center;margin:.5rem 0 1.5rem;box-shadow:var(--shadow-md)}
.champion-box .ch-label{font-family:'Sora',sans-serif;font-size:.72rem;text-transform:uppercase;letter-spacing:.18em;
  color:var(--gold-deep);font-weight:800}
.champion-box .ch-team{font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;color:var(--ink);margin:.5rem 0;
  display:flex;align-items:center;justify-content:center;gap:.6rem}
.champion-box .ch-score{font-size:.9rem;color:var(--grey)}

/* HERO */
.hero{position:relative;overflow:hidden;background:var(--grad-hero);color:#fff;
  padding:3.4rem 1.5rem 3rem;text-align:center}
.hero::after{content:"";position:absolute;inset:0;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40'%3E%3Cpath d='M0 39h40M39 0v40' stroke='rgba(255,255,255,.04)' stroke-width='1'/%3E%3C/svg%3E");pointer-events:none}
.hero>*{position:relative;z-index:1}
.hero .eyebrow{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.18em;text-transform:uppercase;
  color:var(--gold);background:rgba(245,184,61,.12);border:1px solid rgba(245,184,61,.3);
  padding:.3rem .8rem;border-radius:999px;margin-bottom:1rem}
.hero h1{font-family:'Sora','Inter',sans-serif;font-size:2.6rem;font-weight:800;letter-spacing:-.03em;line-height:1.05}
.hero .tagline{opacity:.85;font-size:.95rem;margin:.7rem auto 1.2rem;max-width:620px}
.hero .champ-line{display:inline-flex;align-items:center;gap:.5rem;flex-wrap:wrap;justify-content:center;
  font-size:.86rem;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);
  padding:.5rem 1rem;border-radius:999px;backdrop-filter:blur(6px)}
.hero .champ-line strong{color:var(--gold)}
.hero .meta-row{display:flex;gap:1.6rem;justify-content:center;flex-wrap:wrap;margin-top:1.6rem}
.hero .meta-item{font-size:.82rem;opacity:.9}
.hero .meta-item span{font-weight:700;opacity:1}

/* STATS ROW */
.stats-row{display:grid;grid-template-columns:repeat(5,1fr);gap:1rem;margin:-2.5rem auto 1.8rem;
  max-width:1140px;padding:0 1.4rem;position:relative;z-index:5}
.stat-box{background:var(--surface);border-radius:var(--radius);padding:1.1rem 1rem;
  box-shadow:var(--shadow-md);border:1px solid var(--line);text-align:center;transition:transform .18s}
.stat-box:hover{transform:translateY(-3px)}
.stat-box .sv{font-family:'Sora',sans-serif;font-size:1.7rem;font-weight:800;
  background:var(--grad-blue);-webkit-background-clip:text;background-clip:text;color:transparent}
.stat-box .sl{font-size:.74rem;color:var(--grey);margin-top:.25rem;font-weight:600}

/* SECTION LABEL */
.section-pill{display:inline-flex;align-items:center;background:var(--surface-2);color:var(--grey);
  font-size:.66rem;font-weight:800;padding:.1rem .45rem;border-radius:999px;border:1px solid var(--line);
  text-transform:uppercase;letter-spacing:.05em}

/* UPCOMING */
.upcoming-list{display:flex;flex-direction:column;gap:.55rem}
.upcoming-item{background:var(--surface);border-radius:var(--radius-sm);padding:.7rem .9rem;
  box-shadow:var(--shadow-sm);border:1px solid var(--line);display:flex;align-items:center;gap:.55rem;
  font-size:.85rem;font-weight:600;transition:transform .15s,box-shadow .15s}
.upcoming-item:hover{transform:translateX(3px);box-shadow:var(--shadow-md)}
.upcoming-date{font-size:.72rem;color:#fff;background:var(--grad-blue);font-weight:700;
  min-width:54px;text-align:center;padding:.2rem .4rem;border-radius:999px}
.upcoming-pred{font-family:'JetBrains Mono',monospace;font-weight:700;color:var(--grey);
  background:var(--surface-2);border:1px solid var(--line);border-radius:999px;padding:.1rem .5rem;margin:0 .2rem}

/* GENERIC TABLE */
table{width:100%}

/* BACK TO TOP */
.to-top{position:fixed;right:1.1rem;bottom:1.1rem;z-index:80;width:44px;height:44px;border:none;
  border-radius:50%;background:var(--grad-blue);color:#fff;font-size:1.1rem;cursor:pointer;
  box-shadow:var(--shadow-md);opacity:0;transform:translateY(12px) scale(.9);pointer-events:none;
  transition:opacity .25s,transform .25s}
.to-top.show{opacity:1;transform:none;pointer-events:auto}
.to-top:hover{transform:translateY(-2px)}

/* FOOTER */
footer{margin-top:3rem;background:var(--ink);color:#cfd6ea;padding:2.2rem 1.4rem 2.4rem}
footer .foot-inner{max-width:1140px;margin:0 auto;text-align:center;font-size:.78rem;line-height:1.7}
footer .foot-meta{opacity:.7}
footer .foot-author{margin-top:1rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,.1);
  font-size:.9rem;font-weight:600;color:#fff;letter-spacing:.01em}
footer .foot-author span{color:var(--gold);font-family:'Sora',sans-serif;font-weight:800}
footer a{color:var(--gold)}

/* MOTION-SAFE */
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto}}

/* RESPONSIVE */
@media(max-width:900px){
  .stats-row{grid-template-columns:repeat(3,1fr)}
}
@media(max-width:600px){
  .hero{padding:2.4rem 1.2rem}
  .hero h1{font-size:1.8rem}
  .stats-row{grid-template-columns:repeat(2,1fr);margin-top:-2rem}
  .group-grid{grid-template-columns:1fr}
  .site-header h1{font-size:1rem}
  .site-header .badge:last-child{margin-left:0}
}
"""

APP_JS = """// FIFA World Cup 2026 — light interactions (generated by tools/generate_html.py)
(function(){
  // Scroll progress bar + back-to-top visibility
  var bar=document.querySelector('.scroll-progress');
  var top=document.querySelector('.to-top');
  function onScroll(){
    var h=document.documentElement;
    var max=h.scrollHeight-h.clientHeight;
    var p=max>0?(h.scrollTop/max)*100:0;
    if(bar)bar.style.width=p+'%';
    if(top)top.classList.toggle('show',h.scrollTop>360);
  }
  document.addEventListener('scroll',onScroll,{passive:true});
  onScroll();
  if(top)top.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});

  // Reveal sections on scroll
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});
  },{threshold:.12});
  document.querySelectorAll('.section-reveal').forEach(function(el){io.observe(el);});

  // Count-up for stat values
  var co=new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting)return; co.unobserve(e.target);
      var el=e.target, raw=el.getAttribute('data-val')||el.textContent.trim();
      var m=raw.match(/^([0-9]+(?:\\.[0-9]+)?)(.*)$/); if(!m){return;}
      var end=parseFloat(m[1]), suffix=m[2], dec=(m[1].split('.')[1]||'').length, t0=null, dur=900;
      function step(ts){ if(!t0)t0=ts; var k=Math.min((ts-t0)/dur,1);
        var v=(end*(1-Math.pow(1-k,3))).toFixed(dec); el.textContent=v+suffix;
        if(k<1)requestAnimationFrame(step);}
      el.textContent='0'+suffix; requestAnimationFrame(step);
    });
  },{threshold:.6});
  document.querySelectorAll('.stat-box .sv').forEach(function(el){co.observe(el);});
})();
"""

NAV_LINKS = """
<nav>
  <a href="index.html">🏠 Home</a>
  <a href="group_a.html">A</a><a href="group_b.html">B</a>
  <a href="group_c.html">C</a><a href="group_d.html">D</a>
  <a href="group_e.html">E</a><a href="group_f.html">F</a>
  <a href="group_g.html">G</a><a href="group_h.html">H</a>
  <a href="group_i.html">I</a><a href="group_j.html">J</a>
  <a href="group_k.html">K</a><a href="group_l.html">L</a>
  <a href="knockout.html">🏆 Bracket</a>
</nav>"""


def flag(slug, size=""):
    cls = "flag-lg" if size == "lg" else "flag"
    return f'<img class="{cls}" src="images/{slug}.png" alt="{slug}" loading="lazy">'


HEAD = """<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="author" content="Yohanes Wahyu Nurcahyo">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&family=JetBrains+Mono:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
<script defer src="app.js"></script>"""

SITE_HEADER = """<div class="scroll-progress"></div>
<header class="site-header">
  <span class="logo">⚽</span>
  <div>
    <h1>FIFA World Cup 2026 — AI Predictions</h1>
    <div class="subtitle">Elo · Poisson · Dixon-Coles · Monte Carlo · 10,000 simulations</div>
  </div>
  <span class="badge gold">Jun 11 – Jul 19, 2026</span>
</header>"""

FOOTER = """<footer>
  <div class="foot-inner">
    <div class="foot-meta">
      Predictions by Elo + Poisson + Dixon-Coles model (tools/predict.py) &nbsp;·&nbsp;
      10,000-run Monte Carlo · SEED=2026 &nbsp;·&nbsp;
      Methods: Dixon &amp; Coles 1997 · Maher 1982 · eloratings.net &nbsp;·&nbsp;
      <a href="https://github.com/yoyokits/WorldCup26AI">GitHub</a>
    </div>
    <div class="foot-author">Created by <span>Yohanes Wahyu Nurcahyo</span></div>
  </div>
</footer>
<button class="to-top" aria-label="Back to top">↑</button>"""


def page(title, body, active_nav=""):
    nav = NAV_LINKS.replace(f'href="{active_nav}"', f'href="{active_nav}" class="active"')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{HEAD}
<title>{title} | FIFA World Cup 2026 AI Predictions</title>
</head>
<body>
{SITE_HEADER}
{nav}
<main>
{body}
</main>
{FOOTER}
</body>
</html>"""


# ──────────────────────────────────────────────
# 4. INDEX PAGE
# ──────────────────────────────────────────────
def generate_index():
    # Stats row
    hero = """
<div class="hero">
  <span class="eyebrow">AI Tournament Predictions</span>
  <h1>FIFA World Cup 2026</h1>
  <div class="tagline">Every game, every scoreline — modelled with Elo ratings, Poisson goals, the Dixon-Coles correction, and 10,000 Monte-Carlo simulations.</div>
  <div class="champ-line">🏆 Predicted Champion: <strong>Argentina 🇦🇷</strong> · Final: Argentina 2–1 Germany · July 19, MetLife Stadium NJ</div>
  <div class="meta-row">
    <div class="meta-item">🇺🇸🇲🇽🇨🇦 <span>USA · Mexico · Canada</span></div>
    <div class="meta-item">🏟️ <span>16 venues</span></div>
    <div class="meta-item">⚽ <span>48 teams · 104 matches</span></div>
    <div class="meta-item">📅 <span>June 11 – July 19, 2026</span></div>
  </div>
</div>
<div class="stats-row">
  <div class="stat-box"><div class="sv">48</div><div class="sl">Teams</div></div>
  <div class="stat-box"><div class="sv">12</div><div class="sl">Groups</div></div>
  <div class="stat-box"><div class="sv">104</div><div class="sl">Matches</div></div>
  <div class="stat-box"><div class="sv">39</div><div class="sl">Days</div></div>
  <div class="stat-box"><div class="sv">15.1%</div><div class="sl">Argentina title odds</div></div>
</div>
<main>"""

    # Upcoming matches
    upcoming_matches = [
        ("Jun 11","mexico","Mexico","australia","Australia","2-1"),
        ("Jun 11","netherlands","Netherlands","serbia","Serbia","2-1"),
        ("Jun 12","argentina","Argentina","morocco","Morocco","1-0"),
        ("Jun 12","jamaica","Jamaica","egypt","Egypt","1-2"),
        ("Jun 12","spain","Spain","japan","Japan","1-0"),
    ]
    upcoming = '<h2>📅 Upcoming Matches</h2><div class="upcoming-list">'
    for date, hs, hn, as_, an, pred in upcoming_matches:
        upcoming += f"""<div class="upcoming-item">
  <span class="upcoming-date">{date}</span>
  {flag(hs)} {hn}
  <span class="upcoming-pred">{pred}</span>
  {flag(as_)} {an}
  <span style="font-size:.75rem;color:var(--grey);margin-left:auto">Pred.</span>
</div>"""
    upcoming += "</div>"

    # Group grid
    grid = '<h2>🗓️ Groups A – L</h2><div class="group-grid">'
    for g in "ABCDEFGHIJKL":
        rows = GROUP_STANDINGS[g]
        teams_html = ""
        for pos, team, *rest, qual in rows:
            t = TEAMS[team]
            dot_cls = "dot-q" if qual == "✅" else ("dot-q3" if qual == "🟡" else "dot-out")
            top_cls = "top1" if pos == 1 else ("top2" if pos == 2 else "")
            teams_html += f"""<div class="group-team {top_cls}">
  <span class="qual-dot {dot_cls}"></span>
  {flag(t['slug'])} <span>{team}</span>
</div>"""
        grid += f"""<a href="group_{g.lower()}.html" style="color:inherit;text-decoration:none">
<div class="group-card">
  <div class="group-label">Group {g}</div>
  {teams_html}
</div></a>"""
    grid += "</div>"

    # Title odds top 10
    top10 = sorted(TITLE_ODDS.items(), key=lambda x: -x[1])[:10]
    max_odds = top10[0][1]
    odds_html = '<h2>📊 Title Odds — Top 10</h2><div class="card">'
    for team, pct in top10:
        t = TEAMS[team]
        bar_w = round(pct / max_odds * 100)
        odds_html += f"""<div class="odds-team">
  {flag(t['slug'])}
  <span class="odds-team-name">{team}</span>
  <div class="odds-bar-track"><div class="odds-bar" style="width:{bar_w}%"></div></div>
  <span class="odds-pct">{pct}%</span>
</div>"""
    odds_html += "</div>"

    # Bracket teaser
    bracket_teaser = """<h2>🏆 Predicted Knockout Path</h2>
<div class="card">
<table style="width:100%;font-size:.85rem;border-collapse:collapse">
<tr style="background:#f8fafc"><th style="padding:.4rem .6rem;text-align:left">Round</th><th style="padding:.4rem .6rem">Match</th><th style="padding:.4rem .6rem">Score</th></tr>"""
    path = [
        ("R32","Argentina vs Slovenia","2-0"),
        ("R16","Argentina vs France","1-0 🔥"),
        ("QF","Argentina vs Brazil","1-0 🔥"),
        ("SF","Argentina vs Spain","2-1"),
        ("FINAL","Argentina vs Germany","2-1 🏆"),
    ]
    for i, (rnd, match, score) in enumerate(path):
        bg = "#fff8e1" if rnd == "FINAL" else ("#f0f4ff" if i % 2 == 0 else "#fff")
        bold = "font-weight:700" if rnd == "FINAL" else ""
        bracket_teaser += f"""<tr style="background:{bg};{bold}">
  <td style="padding:.4rem .6rem;color:var(--grey);font-size:.78rem">{rnd}</td>
  <td style="padding:.4rem .6rem">{match}</td>
  <td style="padding:.4rem .6rem;font-family:monospace;text-align:center">{score}</td>
</tr>"""
    bracket_teaser += f"""</table>
<div style="text-align:right;margin-top:.6rem">
  <a href="knockout.html" style="font-size:.82rem">View full bracket →</a>
</div>
</div>"""

    latest = '<h2>⚽ Latest Results</h2><div class="card" style="color:var(--grey);font-size:.85rem;font-style:italic">Tournament begins June 11, 2026 — no results yet.</div>'

    nav = NAV_LINKS.replace('href="index.html"', 'href="index.html" class="active"')
    sections = "".join(
        f'<section class="section-reveal">{s}</section>'
        for s in (upcoming, grid, odds_html, bracket_teaser, latest)
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
{HEAD}
<title>FIFA World Cup 2026 — AI Predictions</title>
</head>
<body>
{SITE_HEADER}
{nav}
{hero}
{sections}
</main>
{FOOTER}
</body>
</html>"""
    (HTML / "index.html").write_text(html, encoding="utf-8")
    print("OK docs/index.html")


# ──────────────────────────────────────────────
# 5. GROUP PAGE
# ──────────────────────────────────────────────
def generate_group(g):
    matches = GROUP_MATCHES[g]
    standings = GROUP_STANDINGS[g]
    group_teams = [row[1] for row in standings]

    # Header flags
    flag_row = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:.3rem;margin-right:.8rem">'
        f'{flag(TEAMS[t]["slug"],"lg")} <strong>{t}</strong></span>'
        for t in group_teams
    )

    # Match table
    match_rows = ""
    for mid, date, home, away, ph, pa, venue in matches:
        hs, as_ = TEAMS[home]["slug"], TEAMS[away]["slug"]
        winner = home if ph > pa else (away if pa > ph else "Draw")
        score_html = f'<span class="pred">{ph}–{pa}</span>'
        match_rows += f"""<tr>
  <td class="date-cell">{date}</td>
  <td><div class="team-cell">{flag(hs)} {home}</div></td>
  <td class="score-cell">{score_html}</td>
  <td><div class="team-cell">{flag(as_)} {away}</div></td>
  <td class="venue-cell">{venue}</td>
</tr>"""

    match_table = f"""<table class="match-table">
<thead><tr>
  <th>Date</th><th>Home</th><th style="text-align:center">Score</th><th>Away</th><th>Venue</th>
</tr></thead>
<tbody>{match_rows}</tbody>
</table>"""

    # Standings table
    stand_rows = ""
    for pos, team, P, W, D, L, GF, GA, GD, Pts, qual in standings:
        t = TEAMS[team]
        row_cls = "qualify-1" if pos == 1 else ("qualify-2" if pos == 2 else ("qualify-3rd" if qual == "🟡" else ""))
        qual_badge = f'<span class="section-pill" style="background:{"var(--blue)" if qual=="✅" else ("var(--gold)" if qual=="🟡" else "#9ca3af")};font-size:.65rem">{qual if qual else "❌"}</span>'
        gd_str = f"+{GD}" if GD > 0 else str(GD)
        stand_rows += f"""<tr class="{row_cls}">
  <td>{pos}</td>
  <td><div style="display:flex;align-items:center;gap:.4rem">{flag(t["slug"])} {team} {qual_badge}</div></td>
  <td>{P}</td><td>{W}</td><td>{D}</td><td>{L}</td>
  <td>{GF}</td><td>{GA}</td><td>{gd_str}</td><td class="pts">{Pts}</td>
</tr>"""

    stand_table = f"""<table class="stand-table">
<thead><tr>
  <th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th>
  <th>GF</th><th>GA</th><th>GD</th><th>Pts</th>
</tr></thead>
<tbody>{stand_rows}</tbody>
</table>"""

    # Elo bar for the group
    elo_bars = ""
    max_elo = max(TEAMS[t]["elo"] for t in group_teams)
    for t in group_teams:
        ti = TEAMS[t]
        w = round((ti["elo"] - 1000) / (max_elo - 1000) * 100)
        elo_bars += f"""<div class="odds-team">
  {flag(ti["slug"])}
  <span class="odds-team-name">{t}</span>
  <div class="odds-bar-track"><div class="odds-bar gold" style="width:{w}%"></div></div>
  <span class="odds-pct" style="color:var(--grey)">{ti["elo"]}</span>
</div>"""

    # Title odds for group
    odds_bars = ""
    max_g = max((TITLE_ODDS.get(team, 0) for pos, team, *_ in standings), default=1) or 1
    for pos, team, *_ in standings:
        pct = TITLE_ODDS.get(team, 0)
        w = max(round(pct / max_g * 100), 2)
        ti = TEAMS[team]
        odds_bars += f"""<div class="odds-team">
  {flag(ti["slug"])}
  <span class="odds-team-name">{team}</span>
  <div class="odds-bar-track"><div class="odds-bar" style="width:{w}%"></div></div>
  <span class="odds-pct">{pct}%</span>
</div>"""

    note_qual = '<p style="font-size:.8rem;color:var(--grey);margin-top:.5rem">🔵 Qualifies &nbsp; 🟡 Potential best 3rd-place qualifier &nbsp; ❌ Eliminated</p>'

    body = f"""
<div style="display:flex;align-items:center;gap:.8rem;flex-wrap:wrap;margin-bottom:1.5rem">
  <span class="badge" style="font-size:1rem;padding:.3rem .8rem">Group {g}</span>
  {flag_row}
</div>

<h2>📋 Match Schedule & Predictions</h2>
<div class="card" style="padding:0;overflow:hidden">{match_table}</div>
<p style="font-size:.78rem;color:var(--grey);margin-top:.3rem">
  Scores shown in <em style="color:var(--grey)">grey italic</em> = AI prediction (not yet played)
</p>

<h2>📊 Predicted Final Standings</h2>
<div class="card" style="padding:0;overflow:hidden">{stand_table}</div>
{note_qual}

<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1.5rem">
  <div class="card">
    <h3>⚡ Elo Strength</h3>
    {elo_bars}
  </div>
  <div class="card">
    <h3>🏆 Title Odds</h3>
    {odds_bars}
  </div>
</div>
"""
    html = page(f"Group {g}", body, f"group_{g.lower()}.html")
    (HTML / f"group_{g.lower()}.html").write_text(html, encoding="utf-8")
    print(f"OK docs/group_{g.lower()}.html")


# ──────────────────────────────────────────────
# 6. KNOCKOUT PAGE
# ──────────────────────────────────────────────
def generate_knockout():
    rounds = [
        ("R32", "Round of 32", [k for k in KNOCKOUT if k[0].startswith("R32")]),
        ("R16", "Round of 16", [k for k in KNOCKOUT if k[0].startswith("R16")]),
        ("QF",  "Quarterfinals", [k for k in KNOCKOUT if k[0].startswith("QF")]),
        ("SF",  "Semifinals", [k for k in KNOCKOUT if k[0].startswith("SF")]),
        ("FIN", "Final", [k for k in KNOCKOUT if k[0] in ("FIN",)]),
    ]

    def b_match(mid, date, ta, tb, score, winner, is_champ=False):
        sa, sb = (TEAMS[ta]["slug"], TEAMS[tb]["slug"]) if ta in TEAMS and tb in TEAMS else ("", "")
        wa_cls = "winner" if winner == ta else ""
        wb_cls = "winner" if winner == tb else ""
        box_cls = "b-match champion" if is_champ else "b-match"
        fa = flag(sa) if sa else ""
        fb = flag(sb) if sb else ""
        sc_cls = "b-score"
        return f"""<div class="{box_cls}">
  <div class="b-team {wa_cls}">{fa} <span class="b-team-name">{ta}</span> <span class="{sc_cls}">{score}</span></div>
  <div class="b-divider"></div>
  <div class="b-team {wb_cls}">{fb} <span class="b-team-name">{tb}</span></div>
  <span style="font-size:.65rem;color:var(--grey);padding:.1rem .4rem;display:block;text-align:right">{date}</span>
</div>"""

    # Build bracket columns
    cols = ""
    for rid, rname, matches in rounds:
        if rid == "FIN":
            continue
        match_html = "".join(b_match(*m) for m in matches)
        cols += f"""<div class="bracket-round">
  <div class="bracket-round-label">{rname}</div>
  <div class="bracket-matches">{match_html}</div>
</div>"""

    # Final + 3PL
    fin = next(m for m in KNOCKOUT if m[0] == "FIN")
    tpl = next(m for m in KNOCKOUT if m[0] == "3PL")

    fin_col = f"""<div class="bracket-round">
  <div class="bracket-round-label" style="background:var(--gold);color:var(--dark)">Final · Jul 19</div>
  <div class="bracket-matches">
    {b_match(*fin, is_champ=True)}
    <div style="margin-top:.5rem;font-size:.72rem;color:var(--grey);text-align:center">MetLife Stadium, NJ</div>
    <div style="margin-top:1rem">
      <div class="bracket-round-label" style="font-size:.65rem;background:#6B7280">3rd Place · Jul 18</div>
      {b_match(*tpl)}
    </div>
  </div>
</div>"""

    champ_box = f"""
<div class="champion-box">
  <div class="ch-label">🏆 Predicted World Cup Champion</div>
  <div class="ch-team">{flag(TEAMS["Argentina"]["slug"],"lg")} Argentina</div>
  <div class="ch-score">Predicted final: Argentina 2–1 Germany &nbsp;|&nbsp; July 19, MetLife Stadium</div>
  <div style="font-size:.8rem;color:var(--grey);margin-top:.4rem">Monte Carlo title probability: <strong>15.1%</strong> (highest of 48 teams)</div>
</div>"""

    # Full results table
    rows = ""
    for mid, date, ta, tb, score, winner in KNOCKOUT:
        if mid == "FIN":
            style = "background:#fff8e1;font-weight:700"
            mid_label = "🏆 FINAL"
        elif mid == "3PL":
            style = "background:#f8fafc"
            mid_label = "3rd Place"
        elif mid.startswith("SF"):
            style = "background:#f0f4ff"
            mid_label = mid
        else:
            style = ""
            mid_label = mid
        sa = TEAMS[ta]["slug"] if ta in TEAMS else ""
        sb = TEAMS[tb]["slug"] if tb in TEAMS else ""
        rows += f"""<tr style="{style}">
  <td style="padding:.4rem .6rem;font-size:.75rem;color:var(--grey)">{mid_label}</td>
  <td style="padding:.4rem .6rem">{date}</td>
  <td style="padding:.4rem .6rem"><div class="team-cell">{flag(sa) if sa else ""} {ta}</div></td>
  <td style="padding:.4rem .6rem;text-align:center;font-family:monospace;font-style:italic;color:var(--grey)">{score}</td>
  <td style="padding:.4rem .6rem"><div class="team-cell">{flag(sb) if sb else ""} {tb}</div></td>
  <td style="padding:.4rem .6rem;font-weight:600">{winner}</td>
</tr>"""

    table = f"""<table style="width:100%;border-collapse:collapse;font-size:.84rem">
<thead style="background:var(--blue);color:#fff">
  <tr>
    <th style="padding:.4rem .6rem;text-align:left">Round</th>
    <th style="padding:.4rem .6rem;text-align:left">Date</th>
    <th style="padding:.4rem .6rem;text-align:left">Team A</th>
    <th style="padding:.4rem .6rem;text-align:center">Pred. Score</th>
    <th style="padding:.4rem .6rem;text-align:left">Team B</th>
    <th style="padding:.4rem .6rem;text-align:left">Pred. Winner</th>
  </tr>
</thead>
<tbody>{rows}</tbody>
</table>"""

    body = f"""
{champ_box}

<h2>🏆 Knockout Bracket</h2>
<div class="bracket-wrap">
  <div class="bracket">{cols}{fin_col}</div>
</div>

<h2>📋 All Knockout Predictions</h2>
<div class="card" style="padding:0;overflow:hidden">{table}</div>
<p style="font-size:.78rem;color:var(--grey);margin-top:.5rem">
  All scores shown are AI predictions. Bracket seeded by Elo rating after group stage.
  Draws resolved by win-expectancy penalty model.
</p>
"""
    html = page("Knockout Bracket", body, "knockout.html")
    (HTML / "knockout.html").write_text(html, encoding="utf-8")
    print("OK docs/knockout.html")


# ──────────────────────────────────────────────
# 7. MAIN
# ──────────────────────────────────────────────
def write_assets():
    (HTML / "styles.css").write_text(STYLES, encoding="utf-8")
    (HTML / "app.js").write_text(APP_JS, encoding="utf-8")
    print("OK docs/styles.css")
    print("OK docs/app.js")


if __name__ == "__main__":
    print("Generating HTML pages...")
    write_assets()
    generate_index()
    for g in "ABCDEFGHIJKL":
        generate_group(g)
    generate_knockout()
    print(f"\nDone. Open docs/index.html in your browser.")
