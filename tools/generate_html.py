#!/usr/bin/env python3
"""Generate HTML visualization pages for FIFA World Cup 2026 predictions.

Reads prediction data from data/*.md and tools/ratings.csv,
produces all HTML pages in docs/.

Run: python tools/generate_html.py
"""

import calendar
import csv
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import predict

DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
RATINGS = os.path.join(HERE, "ratings.csv")
SCHEDULE_FILE = os.path.join(DATA, "WorldCup2026.md")

GROUPS = list("ABCDEFGHIJKL")
GITHUB_URL = "https://github.com/yoyokits/WorldCup26AI"

# ── Data loading ──────────────────────────────────────────────────────────


def load_teams():
    return predict.load_ratings(RATINGS)


def _norm(name):
    return (
        name.strip()
        .lower()
        .replace("ü", "u")
        .replace("ç", "c")
        .replace("é", "e")
        .replace("ö", "o")
        .replace("á", "a")
        .replace("í", "i")
        .replace("İ", "i")
        .replace("Ç", "c")
        .replace("Ü", "u")
        .replace("Ö", "o")
        .replace("É", "e")
        .replace("Ú", "u")
    )


def _date_to_iso(date_str):
    months = {"january": "01", "jan": "01", "february": "02", "feb": "02",
              "march": "03", "mar": "03", "april": "04", "apr": "04",
              "may": "05", "june": "06", "jun": "06", "july": "07", "jul": "07",
              "august": "08", "aug": "08"}
    parts = date_str.strip().split()
    if len(parts) >= 2:
        m = months.get(parts[0].lower().strip("."), "06")
        d = parts[1].strip(",").zfill(2)
        return f"2026-{m}-{d}"
    return "2026-06-11"


def _iso_to_date(iso):
    months = {"06": "June", "07": "July"}
    parts = iso.split("-")
    if len(parts) == 3:
        return f"{months.get(parts[1], 'June')} {int(parts[2])}"
    return iso


def _parse_results_js_dates():
    """Read docs/results.js and return {frozenset(team_a, team_b): iso_date} for knockout matches."""
    path = os.path.join(ROOT, "docs", "results.js")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        text = f.read()
    out = {}
    for m in re.finditer(
        r'"([^"]+?)\s+vs\s+([^"]+?)":\s*\{[^}]*?\bd:\s*"([^"]+)"',
        text,
    ):
        home, away, date_str = m.group(1), m.group(2), m.group(3)
        key = frozenset({_norm(home), _norm(away)})
        out[key] = _date_to_iso(date_str)
    return out


def _et_to_utc(time_et):
    m = re.match(r"(\d+):(\d+)\s*(AM|PM)", time_et, re.I)
    if not m:
        return "T19:00:00Z"
    h, mi = int(m.group(1)), int(m.group(2))
    if m.group(3).upper() == "PM" and h != 12:
        h += 12
    elif m.group(3).upper() == "AM" and h == 12:
        h = 0
    h_utc = h + 4
    if h_utc >= 24:
        h_utc -= 24
    return f"T{h_utc:02d}:{mi:02d}:00Z"


def parse_schedule():
    with open(SCHEDULE_FILE, encoding="utf-8") as f:
        text = f.read()

    schedule = {}
    by_date = defaultdict(list)

    gs = re.search(
        r"### Group Stage.*?(?=---\s*\n\s*### Round of 32)", text, re.DOTALL
    )
    if gs:
        current_date = None
        for line in gs.group().split("\n"):
            dm = re.match(r"####\s+\w+,\s+(.*)", line)
            if dm:
                current_date = dm.group(1).strip()
                continue
            m = re.match(
                r"\|\s*(\d+)\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
                line,
            )
            if m and current_date:
                num = int(m.group(1))
                time_et = m.group(2).strip()
                home = m.group(3).strip()
                away = m.group(4).strip()
                venue = re.sub(r"\s*[\U0001F1E0-\U0001F1FF]+", "", m.group(5)).strip()
                date_iso = _date_to_iso(current_date)
                info = dict(
                    match_num=num,
                    date=current_date,
                    time_et=time_et,
                    home=home,
                    away=away,
                    venue=venue,
                    date_iso=date_iso,
                    time_utc=_et_to_utc(time_et),
                )
                key = frozenset({_norm(home), _norm(away)})
                schedule[key] = info
                by_date[current_date].append(info)

    ko_schedule = {}
    for section_re, label in [
        (r"### Round of 32.*?(?=---)", "R32"),
        (r"### Round of 16.*?(?=---)", "R16"),
        (r"### Quarterfinals.*?(?=---)", "QF"),
        (r"### Semifinals.*?(?=---)", "SF"),
        (r"### Third-Place Match.*?(?=---)", "3rd"),
        (r"### .+ Final \(July.*?(?=---)", "Final"),
    ]:
        sec = re.search(section_re, text, re.DOTALL)
        if not sec:
            continue
        matches = []
        for line in sec.group().split("\n"):
            m = re.match(
                r"\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
                line,
            )
            if m:
                date_str = m.group(2).strip()
                date_clean = re.sub(r"^\w+,\s*", "", date_str)
                date_clean = (
                    date_clean.replace("Jun ", "June ")
                    .replace("Jul ", "July ")
                )
                matches.append(
                    dict(
                        match_num=int(m.group(1)),
                        date=date_clean,
                        time_et=m.group(3).strip(),
                        venue=re.sub(
                            r"\s*[\U0001F1E0-\U0001F1FF]+", "", m.group(5)
                        ).strip(),
                        date_iso=_date_to_iso(date_clean),
                        time_utc=_et_to_utc(m.group(3).strip()),
                    )
                )
        ko_schedule[label] = matches

    return schedule, by_date, ko_schedule


def parse_group_stage():
    with open(os.path.join(DATA, "GroupStage.md"), encoding="utf-8") as f:
        text = f.read()

    groups = {}
    for g in GROUPS:
        pat = re.compile(rf"^## Group {g}\n(.*?)(?=^## Group [A-L]\n|\Z)", re.DOTALL | re.MULTILINE)
        sec = pat.search(text)
        if not sec:
            continue
        body = sec.group(1)

        matches = []
        for m in re.finditer(
            r"\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(\d+)-(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
            body,
        ):
            matches.append(
                dict(
                    num=int(m.group(1)),
                    home=m.group(2).strip(),
                    score_a=int(m.group(3)),
                    score_b=int(m.group(4)),
                    away=m.group(5).strip(),
                    winner=m.group(6).strip(),
                )
            )

        standings = []
        stand_sec = re.search(
            r"### Group [^\n]+ Predicted Standings\s*\n(.*)", body, re.DOTALL
        )
        if stand_sec:
            for s in re.finditer(
                r"\|\s*(\d+)\s*[^\|]*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([+-]?\d+)\s*\|\s*(\d+)\s*\|",
                stand_sec.group(1),
            ):
                standings.append(
                    dict(
                        pos=int(s.group(1)),
                        team=s.group(2).strip(),
                        P=int(s.group(3)),
                        W=int(s.group(4)),
                        D=int(s.group(5)),
                        L=int(s.group(6)),
                        GF=int(s.group(7)),
                        GA=int(s.group(8)),
                        GD=int(s.group(9)),
                        Pts=int(s.group(10)),
                    )
                )
        groups[g] = dict(matches=matches, standings=standings)
    return groups


def parse_knockout_file(filename):
    path = os.path.join(DATA, filename)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        text = f.read()

    matches = []
    for m in re.finditer(
        r"## Match (\d+) — (.+?) vs (.+?)\n.*?"
        r"\*\*Prediction:\*\*\s*(.+?)\s+wins\s+(\d+)-(\d+)(.*?)\n"
        r".*?\*\*Win prob:\*\*\s*.+?\s+(\d+)%\s*\|\s*Draw\s+(\d+)%\s*\|\s*.+?\s+(\d+)%",
        text,
        re.DOTALL,
    ):
        note = ""
        extra = m.group(7).strip()
        if "aet" in extra or "pens" in extra:
            note = extra.strip("() ")
        home = m.group(2).strip()
        away = m.group(3).strip()
        winner = m.group(4).strip()
        winner_goals = int(m.group(5))
        loser_goals = int(m.group(6))
        # Map "{winner} wins X-Y" (winner-loser scoreline) to home-away scoreline.
        # Without this swap the score renders backwards whenever the away team wins.
        if winner == away:
            score_a, score_b = loser_goals, winner_goals
        else:
            score_a, score_b = winner_goals, loser_goals
        matches.append(
            dict(
                num=int(m.group(1)),
                home=home,
                away=away,
                winner=winner,
                score_a=score_a,
                score_b=score_b,
                note=note,
                p_home=int(m.group(8)),
                p_draw=int(m.group(9)),
                p_away=int(m.group(10)),
            )
        )
    return matches


def parse_simulation():
    with open(os.path.join(DATA, "Simulation.md"), encoding="utf-8") as f:
        text = f.read()
    results = []
    for m in re.finditer(
        r"\|\s*\d+\s*\|\s*(.+?)\s*\|\s*([\d.]+)%\s*\|\s*([\d.]+)%\s*\|\s*([\d.]+)%\s*\|",
        text,
    ):
        results.append(
            dict(
                team=m.group(1).strip(),
                champ_pct=float(m.group(2)),
                final_pct=float(m.group(3)),
                sf_pct=float(m.group(4)),
            )
        )
    return results


# ── Slug cache ────────────────────────────────────────────────────────────

_SLUGS = None


def get_slug(name):
    global _SLUGS
    if _SLUGS is None:
        teams = load_teams()
        _SLUGS = {t["team"]: t["slug"] for t in teams.values()}
    return _SLUGS.get(name, name.lower().replace(" ", "-").replace("&", "").strip("-"))


# ── HTML helpers ──────────────────────────────────────────────────────────


def html_head(title):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | WC2026 AI</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
"""


def html_nav(active="home"):
    items = [
        ("home", "index.html", "Home"),
        ("groups", "#", "Groups ▾"),
        ("knockout", "knockout.html", "Knockout"),
        ("method", "prediction_method.html", "Method"),
    ]
    links = ""
    for key, href, label in items:
        cls = ' class="active"' if key == active else ""
        if key == "groups":
            sub = "".join(
                f'<li><a href="group_{g.lower()}.html">Group {g}</a></li>'
                for g in GROUPS
            )
            links += (
                f'<li class="nav-dropdown">'
                f'<a href="#"{cls} onclick="toggleGroupMenu(event)">{label}</a>'
                f'<ul class="group-submenu" id="groupSubmenu">{sub}</ul></li>'
            )
        else:
            links += f'<li><a href="{href}"{cls}>{label}</a></li>'
    links += (
        f'<li><a href="{GITHUB_URL}" class="github-link" target="_blank"'
        f' rel="noopener">GitHub</a></li>'
    )
    return f"""<nav class="nav">
  <a href="index.html" class="nav-brand">WC2026 <span>AI</span></a>
  <button class="nav-toggle" onclick="document.querySelector('.nav-links').classList.toggle('open')" aria-label="Menu">☰</button>
  <ul class="nav-links">{links}</ul>
</nav>
"""


def html_disclaimer():
    return (
        '<div class="disclaimer">'
        "⚠️ <strong>Disclaimer:</strong> This is a personal AI prediction "
        "project — not for gambling. All results are generated by a statistical "
        "model for educational and internal use only. Do not use these predictions "
        "for real betting or wagering.</div>"
    )


def html_footer():
    return f"""<footer class="footer">
  <p>FIFA World Cup 2026 AI Predictions &middot;
  <a href="index.html">Home</a> &middot;
  <a href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub</a> &middot;
  <a href="prediction_method.html">Methodology</a></p>
  <p>By <strong>Yohanes Wahyu Nurcahyo</strong> &middot; Built with Python + Claude AI &middot; Not affiliated with FIFA</p>
</footer>
<!-- Default Statcounter code for WorldCup26AI https://yoyokits.github.io/WorldCup26AI -->
<script type="text/javascript">
var sc_project=13290639;
var sc_invisible=0;
var sc_security="f4b5a0b5";
var scJsHost = "https://";
document.write("<sc"+"ript type='text/javascript' src='" + scJsHost + "statcounter.com/counter/counter.js'></"+"script>");
</script>
<noscript><div class="statcounter"><a title="Web Analytics Made Easy - Statcounter" href="https://statcounter.com/" target="_blank"><img class="statcounter" src="https://c.statcounter.com/13290639/0/f4b5a0b5/0/" alt="Web Analytics Made Easy - Statcounter" referrerPolicy="no-referrer-when-downgrade"></a></div></noscript>
<!-- End of Statcounter Code -->
<script src="results.js"></script>
<script src="app.js"></script>"""


def _prediction_tracker_block():
    """Collapsible accuracy tracker. Body is filled by buildPredictionTracker() in results.js."""
    return (
        '<div class="pt-wrapper" id="predictionTrackerWrap">'
        '  <div class="pt-header" onclick="this.parentElement.classList.toggle(\'open\')">'
        '    <span>📊 Prediction Accuracy Tracker</span>'
        '    <span class="pt-chevron">▼</span>'
        '  </div>'
        '  <div class="pt-body" id="predictionTracker"></div>'
        '</div>'
    )


def _round_picker_block():
    """Dropdown that jumps to a knockout round on knockout.html."""
    return (
        '<div style="background:#f0f4ff;border:2px solid #002868;border-radius:12px;'
        'padding:20px 16px;margin:0 0 24px;display:flex;align-items:center;flex-wrap:wrap;gap:12px;">'
        '<span style="font-family:Montserrat,sans-serif;font-weight:800;font-size:1rem;color:#002868;">'
        '&#127942; View Predictions by Round</span>'
        '<select id="roundPicker" onchange="navigateToDay(this.value)" '
        'style="padding:10px 14px;border:2px solid #002868;border-radius:8px;font-size:0.9rem;'
        'font-weight:600;background:white;color:#0a1628;cursor:pointer;flex:1;min-width:200px;max-width:340px;">'
        '<option value="">-- Select a round --</option>'
        '<option value="knockout.html#round-of-32">Round of 32 (16 matches)</option>'
        '<option value="knockout.html#round-of-16">Round of 16 (8 matches)</option>'
        '<option value="knockout.html#quarterfinals">Quarterfinals (4 matches)</option>'
        '<option value="knockout.html#semifinals">Semifinals (2 matches)</option>'
        '<option value="knockout.html#third-place">Third Place Match</option>'
        '<option value="knockout.html#final">Final &mdash; Predicted Champion</option>'
        '</select></div>'
    )


def _team_compare_block():
    """Two team selectors + comparison panel. Populated by renderComparison() in _index_widgets_js."""
    return (
        '<div style="background:#f8fafc;border:2px solid #002868;border-radius:12px;padding:20px 16px;margin:0 0 24px;">'
        '<div style="font-family:Montserrat,sans-serif;font-weight:800;font-size:1rem;color:#002868;margin-bottom:12px;">'
        '⚔️ Team Comparison</div>'
        '<div style="display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;">'
        '<select id="teamLeft" onchange="renderComparison()" '
        'style="padding:10px 14px;border:2px solid #002868;border-radius:8px;font-size:0.9rem;'
        'font-weight:600;background:white;color:#0a1628;cursor:pointer;flex:1;min-width:140px;max-width:260px;">'
        '<option value="">-- Select left team --</option></select>'
        '<span style="font-weight:800;font-size:1.2rem;color:#002868;">VS</span>'
        '<select id="teamRight" onchange="renderComparison()" '
        'style="padding:10px 14px;border:2px solid #002868;border-radius:8px;font-size:0.9rem;'
        'font-weight:600;background:white;color:#0a1628;cursor:pointer;flex:1;min-width:140px;max-width:260px;">'
        '<option value="">-- Select right team --</option></select>'
        '</div>'
        '<div id="comparisonPanel" style="margin-top:16px;"></div>'
        '</div>'
    )


def _index_widgets_js(teams):
    """Inline JS: TEAM_DATA + navigateToDay + renderComparison.

    Required by the three index-only widgets (tracker, round picker, team
    comparison). Keep in sync with _prediction_tracker_block,
    _round_picker_block, _team_compare_block.
    """
    team_data = {}
    for t in teams.values():
        team_data[t["team"]] = {
            "slug": t.get("slug", get_slug(t["team"])),
            "group": t.get("group", ""),
            "conf": t.get("confederation", ""),
            "rank": int(t["fifa_rank"]),
            "elo": int(t["elo"]),
            "atk": float(t.get("attack_avg", 0)),
            "def": float(t.get("defense_avg", 0)),
            "host": 1 if t.get("host") else 0,
            "form": float(t.get("form", 0)),
            "injury": float(t.get("injury_impact", 0)),
            "depth": int(t.get("squad_depth", 0)),
            "age": float(t.get("avg_age", 0)),
            "wcExp": int(t.get("wc_experience", 0)),
            "spOff": int(t.get("set_piece_off", 0)),
            "spDef": int(t.get("set_piece_def", 0)),
            "pressure": int(t.get("pressure_rating", 0)),
            "coach": int(t.get("coach_rating", 0)),
            "fatigue": float(t.get("fatigue", 0)),
        }
    return "\nvar TEAM_DATA=" + json.dumps(team_data, ensure_ascii=False) + ";\n" + r"""
function navigateToDay(url){if(url)window.location.href=url;}
(function(){
  var teams=Object.keys(TEAM_DATA).sort();
  var selL=document.getElementById('teamLeft');
  var selR=document.getElementById('teamRight');
  if(!selL||!selR)return;
  teams.forEach(function(t){
    var d=TEAM_DATA[t];
    var label=t+' (Group '+d.group+')';
    selL.innerHTML+='<option value="'+t+'">'+label+'</option>';
    selR.innerHTML+='<option value="'+t+'">'+label+'</option>';
  });
})();
function renderComparison(){
  var panel=document.getElementById('comparisonPanel');
  if(!panel)return;
  var lName=document.getElementById('teamLeft').value;
  var rName=document.getElementById('teamRight').value;
  if(!lName&&!rName){panel.innerHTML='';return;}
  var stats=[
    {key:'rank',label:'FIFA Rank',fmt:function(v){return '#'+v;},better:'low'},
    {key:'elo',label:'Elo Rating',fmt:null,better:'high'},
    {key:'group',label:'Group',fmt:null,better:null},
    {key:'conf',label:'Confederation',fmt:null,better:null},
    {key:'atk',label:'Attack Index',fmt:null,better:'high'},
    {key:'def',label:'Defence Index',fmt:null,better:'low'},
    {key:'form',label:'Form',fmt:function(v){return(v*100).toFixed(0)+'%';},better:'high'},
    {key:'depth',label:'Squad Depth',fmt:function(v){return v+'/10';},better:'high'},
    {key:'coach',label:'Coach Rating',fmt:function(v){return v+'/10';},better:'high'},
    {key:'pressure',label:'Pressure Rating',fmt:function(v){return v+'/10';},better:'high'},
    {key:'wcExp',label:'WC Experience',fmt:function(v){return v+' apps';},better:'high'},
    {key:'spOff',label:'Set Piece Off.',fmt:function(v){return v+'/10';},better:'high'},
    {key:'spDef',label:'Set Piece Def.',fmt:function(v){return v+'/10';},better:'high'},
    {key:'age',label:'Avg Age',fmt:null,better:null},
    {key:'injury',label:'Injury Impact',fmt:function(v){return(v*100).toFixed(0)+'%';},better:'low'},
    {key:'fatigue',label:'Fatigue',fmt:function(v){return(v*100).toFixed(0)+'%';},better:'low'},
    {key:'host',label:'Host Nation',fmt:function(v){return v?'Yes':'No';},better:null}
  ];
  function teamCard(name){
    if(!name)return'<div class="tc-side tc-empty"><p style="color:#9ca3af;">Select a team</p></div>';
    var d=TEAM_DATA[name];
    var h='<div class="tc-side">';
    h+='<div class="tc-header"><img src="images/'+d.slug+'.png" alt="'+name+'" class="tc-flag"><span class="tc-name">'+name+'</span></div>';
    h+='<div class="tc-stats">';
    stats.forEach(function(s){
      var v=d[s.key]; var display=s.fmt?s.fmt(v):v;
      h+='<div class="tc-row"><span class="tc-label">'+s.label+'</span><span class="tc-val">'+display+'</span></div>';
    });
    h+='</div></div>';
    return h;
  }
  function barRow(s,lVal,rVal){
    var lDisp=s.fmt?s.fmt(lVal):lVal;
    var rDisp=s.fmt?s.fmt(rVal):rVal;
    var lWin='',rWin='';
    if(s.better==='high'){if(lVal>rVal)lWin=' tc-win';else if(rVal>lVal)rWin=' tc-win';}
    else if(s.better==='low'){if(lVal<rVal)lWin=' tc-win';else if(rVal<lVal)rWin=' tc-win';}
    return'<div class="tc-bar-row"><span class="tc-bar-val'+lWin+'">'+lDisp+'</span><span class="tc-bar-label">'+s.label+'</span><span class="tc-bar-val'+rWin+'">'+rDisp+'</span></div>';
  }
  var html='';
  if(lName&&rName){
    var ld=TEAM_DATA[lName],rd=TEAM_DATA[rName];
    html='<div class="tc-vs"><div class="tc-vs-header">';
    html+='<div class="tc-vs-team"><img src="images/'+ld.slug+'.png" class="tc-flag"><span class="tc-name">'+lName+'</span></div>';
    html+='<span class="tc-vs-label">VS</span>';
    html+='<div class="tc-vs-team"><img src="images/'+rd.slug+'.png" class="tc-flag"><span class="tc-name">'+rName+'</span></div>';
    html+='</div><div class="tc-bar-grid">';
    stats.forEach(function(s){html+=barRow(s,ld[s.key],rd[s.key]);});
    html+='</div></div>';
  } else {
    html=teamCard(lName||rName);
  }
  panel.innerHTML=html;
}
"""


def _shared_js():
    return """
function toggleGroupMenu(e){
  e.preventDefault();
  var s=document.getElementById('groupSubmenu');
  s.style.display=s.style.display==='flex'?'none':'flex';
}
document.addEventListener('click',function(e){
  var s=document.getElementById('groupSubmenu');
  if(s&&!e.target.closest('.nav-dropdown'))s.style.display='none';
});
document.querySelectorAll('.local-time').forEach(function(el){
  var u=el.getAttribute('data-utc');
  if(u){try{el.textContent=new Date(u).toLocaleTimeString(undefined,{hour:'2-digit',minute:'2-digit'})+' local';}catch(e){}}
});
"""


def match_card_html(match, teams, schedule_info=None):
    home, away = match["home"], match["away"]
    sa, sb = match["score_a"], match["score_b"]
    winner = match.get("winner", "")
    note = match.get("note", "")
    h_slug, a_slug = get_slug(home), get_slug(away)
    score_str = f"{sa}-{sb}"
    if note:
        score_str += f" ({note})"

    h_data, a_data = teams.get(home), teams.get(away)
    lam_a = lam_b = 0.0
    p_home = p_draw = p_away = 0.0
    if h_data and a_data:
        lam_a, lam_b = predict.expected_goals(h_data, a_data)
        grid = predict.score_matrix(lam_a, lam_b)
        p_home, p_draw, p_away = predict.outcome_probs(grid)

    if "p_home" in match and isinstance(match["p_home"], (int, float)):
        p_home = match["p_home"] / 100.0
        p_draw = match["p_draw"] / 100.0
        p_away = match["p_away"] / 100.0

    date_str = time_utc = venue_str = ""
    if schedule_info:
        date_str = schedule_info.get("date", "")
        time_utc = (
            schedule_info.get("date_iso", "2026-06-11")
            + schedule_info.get("time_utc", "T19:00:00Z")
        )
        venue_str = schedule_info.get("venue", "")

    h_tag = a_tag = ""
    if winner == home:
        h_tag = '<span class="match-winner-tag tag-win">W</span>'
        a_tag = '<span class="match-winner-tag tag-loss">L</span>'
    elif winner == away:
        h_tag = '<span class="match-winner-tag tag-loss">L</span>'
        a_tag = '<span class="match-winner-tag tag-win">W</span>'
    elif winner == "Draw":
        h_tag = '<span class="match-winner-tag tag-draw">D</span>'
        a_tag = '<span class="match-winner-tag tag-draw">D</span>'

    def sv(t, k):
        v = t.get(k, "—") if t else "—"
        if isinstance(v, float):
            return f"{v:.2f}" if v < 10 else f"{v:.1f}"
        return str(v)

    hs, als = h_data or {}, a_data or {}

    stat_rows = ""
    stat_pairs = [
        ("Elo", "elo"), ("FIFA Rank", "fifa_rank"),
        ("Exp. Goals (λ)", None), ("Form", "form"),
        ("Coach", "coach_rating"), ("Squad Depth", "squad_depth"),
        ("Pressure", "pressure_rating"), ("Injury Impact", "injury_impact"),
        ("Avg Age", "avg_age"), ("WC Experience", "wc_experience"),
        ("Fatigue", "fatigue"), ("Set Piece Off", "set_piece_off"),
    ]
    for label, key in stat_pairs:
        if key is None:
            hv, av = f"{lam_a:.2f}", f"{lam_b:.2f}"
        elif key == "fifa_rank":
            hv, av = f"#{sv(hs, key)}", f"#{sv(als, key)}"
        else:
            hv, av = sv(hs, key), sv(als, key)
        stat_rows += (
            f'<div class="stat-item"><div class="stat-label">{label}</div>'
            f'<div class="stat-value">{hv}</div>'
            f'<div class="stat-label">{home[:3].upper()}</div></div>'
            f'<div class="stat-item"><div class="stat-label">{label}</div>'
            f'<div class="stat-value">{av}</div>'
            f'<div class="stat-label">{away[:3].upper()}</div></div>'
        )

    return f"""<div class="match-card" onclick="this.classList.toggle('expanded')">
  <div class="match-header">
    <div class="match-team home">
      {h_tag}
      <span class="team-name">{home}</span>
      <img src="images/{h_slug}.png" alt="{home}">
    </div>
    <div class="match-score">{score_str}</div>
    <div class="match-team away">
      <img src="images/{a_slug}.png" alt="{away}">
      <span class="team-name">{away}</span>
      {a_tag}
    </div>
  </div>
  <div class="match-meta">
    {f'<span>{date_str}</span>' if date_str else ''}
    {f'<span class="local-time" data-utc="{time_utc}"></span>' if time_utc else ''}
    {f'<span>{venue_str}</span>' if venue_str else ''}
  </div>
  <div class="expand-hint">▼</div>
  <div class="match-details">
    <div class="match-details-inner">
      <div class="prob-bar">
        <div class="win" style="width:{p_home*100:.0f}%">{home[:3].upper()} {p_home*100:.0f}%</div>
        <div class="draw" style="width:{p_draw*100:.0f}%">{p_draw*100:.0f}%</div>
        <div class="loss" style="width:{p_away*100:.0f}%">{away[:3].upper()} {p_away*100:.0f}%</div>
      </div>
      <div class="stats-grid">{stat_rows}</div>
    </div>
  </div>
</div>"""


def standings_html(standings):
    rows = ""
    for s in standings:
        sl = get_slug(s["team"])
        cls = "qualify" if s["pos"] <= 2 else ("third" if s["pos"] == 3 else "")
        tag = " ✅" if s["pos"] <= 2 else (" \U0001f7e1" if s["pos"] == 3 else "")
        rows += (
            f'<tr class="{cls}">'
            f'<td>{s["pos"]}{tag}</td>'
            f'<td><div class="team-cell"><img src="images/{sl}.png" alt="">'
            f'{s["team"]}</div></td>'
            f'<td>{s["P"]}</td><td>{s["W"]}</td><td>{s["D"]}</td><td>{s["L"]}</td>'
            f'<td>{s["GF"]}</td><td>{s["GA"]}</td><td>{s["GD"]:+d}</td>'
            f'<td><strong>{s["Pts"]}</strong></td></tr>'
        )
    return (
        '<div class="card" style="overflow-x:auto">'
        '<table class="standings-table"><thead><tr>'
        "<th>Pos</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th>"
        "<th>GF</th><th>GA</th><th>GD</th><th>Pts</th>"
        f"</tr></thead><tbody>{rows}</tbody></table>"
        '<div class="standings-legend">'
        "<strong>P</strong> = Played &middot; "
        "<strong>W</strong> = Won &middot; "
        "<strong>D</strong> = Drawn &middot; "
        "<strong>L</strong> = Lost &middot; "
        "<strong>GF</strong> = Goals For &middot; "
        "<strong>GA</strong> = Goals Against &middot; "
        "<strong>GD</strong> = Goal Difference &middot; "
        "<strong>Pts</strong> = Points"
        "</div></div>"
    )


# ── Page generators ───────────────────────────────────────────────────────


def _build_bracket_tree():
    rounds = [
        ("R32", "Round of 32", "RoundOf32.md"),
        ("R16", "Round of 16", "RoundOf16.md"),
        ("QF", "Quarterfinals", "Quarterfinals.md"),
        ("SF", "Semifinals", "Semifinals.md"),
        ("Final", "Final", "Final.md"),
    ]
    bracket_data = {}
    for key, label, fn in rounds:
        matches = parse_knockout_file(fn)
        bracket_data[key] = [(m["home"], m["away"], m["score_a"], m["score_b"], m["winner"], m.get("note", "")) for m in matches]

    html = '<div class="bracket-wrap"><div class="bracket">'
    for key, label, _ in rounds:
        matches = bracket_data.get(key, [])
        html += f'<div class="bracket-round"><div class="bracket-round-title">{label}</div>'
        for home, away, sa, sb, winner, note in matches:
            h_slug, a_slug = get_slug(home), get_slug(away)
            score = f"{sa}-{sb}"
            if note:
                score += f" ({note})"
            h_cls = " bracket-winner" if winner == home else ""
            a_cls = " bracket-winner" if winner == away else ""
            html += (
                f'<div class="bracket-match">'
                f'<div class="bracket-team{h_cls}">'
                f'<img src="images/{h_slug}.png" alt="">'
                f'<span>{home}</span><span class="bracket-score">{sa}</span></div>'
                f'<div class="bracket-team{a_cls}">'
                f'<img src="images/{a_slug}.png" alt="">'
                f'<span>{away}</span><span class="bracket-score">{sb}</span></div>'
                f'</div>'
            )
        html += '</div>'

    final = bracket_data.get("Final", [])
    if final:
        champ = final[0][4]
        ch_slug = get_slug(champ)
        html += (
            f'<div class="bracket-round bracket-champion">'
            f'<div class="bracket-round-title">Champion</div>'
            f'<div class="bracket-match champion-match">'
            f'<img src="images/{ch_slug}.png" alt="{champ}" class="champion-flag">'
            f'<span class="champion-name">{champ}</span></div></div>'
        )

    html += '</div></div>'
    return html


def generate_index(teams, groups_data, sim_data, schedule, by_date, ko_schedule):
    gs_matches_by_key = {}
    for gd in groups_data.values():
        for m in gd.get("matches", []):
            key = frozenset({_norm(m["home"]), _norm(m["away"])})
            gs_matches_by_key[key] = m

    ko_match_data = {}
    ko_match_by_key = {}
    for fn in ["RoundOf32.md", "RoundOf16.md", "Quarterfinals.md", "Semifinals.md", "ThirdPlace.md", "Final.md"]:
        for m in parse_knockout_file(fn):
            ko_match_data[m["num"]] = m
            ko_match_by_key[frozenset({_norm(m["home"]), _norm(m["away"])})] = m

    ko_dates = _parse_results_js_dates()

    cal_cards_html = {}
    for date_str, sched_matches in by_date.items():
        d = _date_to_iso(date_str)
        cards = ""
        for sm in sched_matches:
            key = frozenset({_norm(sm["home"]), _norm(sm["away"])})
            gm = gs_matches_by_key.get(key)
            if gm:
                sinfo = {"date": sm["date"], "date_iso": sm["date_iso"],
                         "time_utc": sm["time_utc"], "venue": sm["venue"]}
                cards += match_card_html(gm, teams, sinfo)
        if cards:
            cal_cards_html[d] = cards

    for key, km in ko_match_by_key.items():
        date_iso = ko_dates.get(key)
        if not date_iso:
            continue
        date_str = _iso_to_date(date_iso)
        sinfo = {"date": date_str, "date_iso": date_iso,
                 "time_utc": "", "venue": ""}
        card = match_card_html(km, teams, sinfo)
        cal_cards_html.setdefault(date_iso, "")
        cal_cards_html[date_iso] += card

    cal_cards_json = {k: v for k, v in cal_cards_html.items()}

    group_cards = ""
    for g in GROUPS:
        gd = groups_data.get(g, {})
        team_rows = ""
        for s in gd.get("standings", []):
            sl = get_slug(s["team"])
            team_rows += (
                f'<div class="group-team">'
                f'<img src="images/{sl}.png" alt="">{s["team"]}'
                f'<span style="margin-left:auto;color:var(--wc-gray);font-size:0.75rem">'
                f'{s["Pts"]}pts</span></div>'
            )
        group_cards += (
            f'<a href="group_{g.lower()}.html" class="group-card">'
            f'<div class="group-card-header">Group {g}</div>'
            f'<div class="group-card-body">{team_rows}</div></a>'
        )

    contenders = ""
    for s in sim_data[:10]:
        sl = get_slug(s["team"])
        contenders += (
            f'<div class="contender-card">'
            f'<img src="images/{sl}.png" alt="{s["team"]}">'
            f'<div class="team-name">{s["team"]}</div>'
            f'<div class="odds">{s["champ_pct"]:.1f}%</div>'
            f'<div class="rank">Champion probability</div></div>'
        )

    bracket_html = _build_bracket_tree()

    html = html_head("Home")
    html += html_nav("home")
    html += '<div class="container">'
    html += (
        '<div class="hero">'
        "<h1>FIFA World Cup 2026</h1>"
        "<p>AI-Powered Match Predictions</p>"
        '<p class="subtitle">June 11 – July 19, 2026 · Canada · Mexico · USA · 48 Teams · 104 Matches</p>'
        '<div class="link-row" style="margin-top:16px">'
        '<a href="knockout.html" class="btn">View Knockout Bracket</a>'
        '<a href="prediction_method.html" class="btn btn-outline" style="border-color:white;color:white">Prediction Method</a>'
        "</div></div>"
    )
    # ── Three index-only widgets (DO NOT REMOVE) ─────────────────────────────
    # These three blocks (Prediction Tracker, Round Picker, Team Comparison)
    # have been silently dropped in past regenerations. They depend on
    # results.js + the TEAM_DATA payload + navigateToDay/renderComparison
    # JS at the bottom of the page. If you remove any of them, update this
    # comment and the matching note in CLAUDE.md "Index page contract".
    html += _prediction_tracker_block()
    html += _round_picker_block()
    html += _team_compare_block()
    html += '<h2 class="section-title">Predicted Knockout Bracket</h2>'
    html += bracket_html
    html += '<h2 class="section-title">Match Calendar</h2>'
    html += (
        '<div class="calendar">'
        '<div class="calendar-left">'
        '<div class="calendar-nav">'
        '<button class="cal-nav-btn" onclick="switchMonth(-1)">&#9664; Prev</button>'
        '<span class="calendar-title" id="calMonthTitle">June 2026</span>'
        '<button class="cal-nav-btn" onclick="switchMonth(1)">Next &#9654;</button>'
        '</div>'
        '<div id="calendarGrid"></div>'
        '</div>'
        '<div id="calendarMatches" class="calendar-matches"></div>'
        "</div>"
    )
    html += '<h2 class="section-title">Group Stage Predictions</h2>'
    html += f'<div class="group-grid">{group_cards}</div>'
    html += '<h2 class="section-title">Title Contenders (Monte Carlo 10,000 sims)</h2>'
    html += f'<div class="contenders-grid">{contenders}</div>'
    html += html_disclaimer()
    html += "</div>"
    html += html_footer()
    html += f"<script>\nvar calCards={json.dumps(cal_cards_json)};\n"
    html += _calendar_js()
    html += _shared_js()
    html += _index_widgets_js(teams)
    html += "\n</script></body></html>"

    _write_html("index.html", html)


def _calendar_js():
    return """
var calMonth=6;
function renderCalendar(month){
  calMonth=month;
  var names=['','January','February','March','April','May','June','July'];
  document.getElementById('calMonthTitle').textContent=names[month]+' 2026';
  var grid=document.getElementById('calendarGrid');
  var days=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  var h='<div class="calendar-grid">';
  for(var i=0;i<7;i++) h+='<div class="cal-header">'+days[i]+'</div>';
  var d=new Date(2026,month-1,1);
  var startDay=d.getDay();
  for(var i=0;i<startDay;i++) h+='<div class="cal-day empty"></div>';
  var daysInMonth=new Date(2026,month,0).getDate();
  for(var day=1;day<=daysInMonth;day++){
    var iso='2026-'+(month<10?'0':'')+month+'-'+(day<10?'0':'')+day;
    var cls='cal-day';
    var attr='';
    if(calCards[iso]){
      if(iso==='2026-07-19') cls+=' has-match final';
      else if(iso>='2026-06-28') cls+=' has-match knockout';
      else cls+=' has-match';
      attr=' data-date="'+iso+'" onclick="showCalMatches(this)"';
    }
    h+='<div class="'+cls+'"'+attr+'>'+day+'</div>';
  }
  h+='</div>';
  grid.innerHTML=h;
  document.getElementById('calendarMatches').innerHTML='';
  document.getElementById('calendarMatches').classList.remove('active');
}
function switchMonth(dir){
  var next=calMonth+dir;
  if(next>=6&&next<=7) renderCalendar(next);
}
renderCalendar(6);
function showCalMatches(el){
  document.querySelectorAll('.cal-day.active').forEach(function(d){d.classList.remove('active');});
  el.classList.add('active');
  var date=el.getAttribute('data-date');
  var panel=document.getElementById('calendarMatches');
  var cards=calCards[date];
  if(!cards){
    panel.innerHTML='<p style="text-align:center;color:var(--wc-gray);padding:12px">No matches on this date.</p>';
    panel.classList.add('active');return;
  }
  var hdr=new Date(date+'T12:00:00Z').toLocaleDateString(undefined,{weekday:'long',month:'long',day:'numeric',year:'numeric'});
  panel.innerHTML='<div class="calendar-date-header">'+hdr+'</div>'+cards;
  panel.classList.add('active');
  panel.querySelectorAll('.local-time').forEach(function(el){
    var u=el.getAttribute('data-utc');
    if(u){try{el.textContent=new Date(u).toLocaleTimeString(undefined,{hour:'2-digit',minute:'2-digit'})+' local';}catch(e){}}
  });
}
"""


def generate_group_page(group, groups_data, teams, schedule):
    gd = groups_data.get(group, {})
    matches = gd.get("matches", [])
    standings = gd.get("standings", [])

    html = html_head(f"Group {group}")
    html += html_nav("groups")
    html += '<div class="container">'

    team_imgs = "".join(
        f'<img src="images/{get_slug(s["team"])}.png" alt="{s["team"]}" '
        f'style="width:40px;height:28px;border-radius:3px;margin:0 4px" title="{s["team"]}">'
        for s in standings
    )
    html += (
        f'<div class="hero" style="padding:24px 16px">'
        f"<h1>Group {group}</h1>"
        f'<div style="margin-top:8px">{team_imgs}</div></div>'
    )

    html += '<h2 class="section-title">Matches</h2>'
    for m in matches:
        key = frozenset({_norm(m["home"]), _norm(m["away"])})
        sched = schedule.get(key)
        html += match_card_html(m, teams, sched)

    html += '<h2 class="section-title">Predicted Standings</h2>'
    html += standings_html(standings)

    html += '<div class="link-row" style="margin-top:20px">'
    for g in GROUPS:
        cls = "btn btn-red" if g == group else "btn btn-outline"
        html += (
            f'<a href="group_{g.lower()}.html" class="{cls}" '
            f'style="padding:8px 14px;font-size:0.78rem">Group {g}</a>'
        )
    html += "</div>"

    html += html_disclaimer()
    html += "</div>"
    html += html_footer()
    html += f"<script>{_shared_js()}</script></body></html>"

    _write_html(f"group_{group.lower()}.html", html)


def generate_knockout(teams, ko_schedule):
    rounds = [
        ("Round of 32", "RoundOf32.md", "R32"),
        ("Round of 16", "RoundOf16.md", "R16"),
        ("Quarterfinals", "Quarterfinals.md", "QF"),
        ("Semifinals", "Semifinals.md", "SF"),
        ("Third Place", "ThirdPlace.md", "3rd"),
        ("Final", "Final.md", "Final"),
    ]

    html = html_head("Knockout Stage")
    html += html_nav("knockout")
    html += '<div class="container">'
    html += (
        '<div class="hero" style="padding:24px 16px">'
        "<h1>Knockout Stage</h1>"
        "<p>Round of 32 to Final — Every match has a winner</p></div>"
    )

    final_data = parse_knockout_file("Final.md")
    if final_data:
        fm = final_data[0]
        champ = fm["winner"]
        runner = fm["away"] if fm["winner"] == fm["home"] else fm["home"]
        html += (
            f'<div class="champion-banner">'
            f"<h2>Predicted Champion</h2>"
            f'<img src="images/{get_slug(champ)}.png" alt="{champ}">'
            f"<h2>{champ}</h2>"
            f"<p>Defeating {runner} {fm['score_a']}-{fm['score_b']} in the Final</p></div>"
        )

    for round_name, filename, ko_label in rounds:
        matches = parse_knockout_file(filename)
        if not matches:
            continue
        html += f'<h2 class="section-title">{round_name}</h2>'
        ko_sched = ko_schedule.get(ko_label, [])
        for i, m in enumerate(matches):
            si = ko_sched[i] if i < len(ko_sched) else None
            sinfo = (
                {
                    "date": si["date"],
                    "date_iso": si["date_iso"],
                    "time_utc": si["time_utc"],
                    "venue": si["venue"],
                }
                if si
                else None
            )
            html += match_card_html(m, teams, sinfo)

    html += html_disclaimer()
    html += "</div>"
    html += html_footer()
    html += f"<script>{_shared_js()}</script></body></html>"

    _write_html("knockout.html", html)


def generate_prediction_method():
    md_path = os.path.join(ROOT, "PREDICTION_ENGINE.md")
    with open(md_path, encoding="utf-8") as f:
        md_text = f.read()

    content = _md_to_html(md_text)

    html = html_head("Prediction Method")
    html += html_nav("method")
    html += '<div class="container">'
    html += (
        '<div class="hero" style="padding:24px 16px">'
        "<h1>Prediction Methodology</h1>"
        "<p>Elo + Poisson + Dixon-Coles Engine</p></div>"
    )
    html += f'<div class="method-content card" style="padding:20px">{content}</div>'
    html += html_disclaimer()
    html += "</div>"
    html += html_footer()
    html += f"<script>{_shared_js()}</script></body></html>"

    _write_html("prediction_method.html", html)


def _md_to_html(md):
    lines = md.split("\n")
    out = []
    in_code = in_table = in_list = False
    list_tag = "ul"

    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                out.append("<pre><code>")
                in_code = True
            continue
        if in_code:
            out.append(_esc(line))
            continue

        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().split("|")[1:-1]]
            if all(re.match(r"^[-:]+$", c) for c in cells if c):
                continue
            if not in_table:
                in_table = True
                out.append(
                    "<table><thead><tr>"
                    + "".join(f"<th>{_inl(c)}</th>" for c in cells)
                    + "</tr></thead><tbody>"
                )
            else:
                out.append(
                    "<tr>" + "".join(f"<td>{_inl(c)}</td>" for c in cells) + "</tr>"
                )
            continue
        elif in_table:
            out.append("</tbody></table>")
            in_table = False

        if re.match(r"^[-*]\s", line.strip()):
            if not in_list:
                out.append("<ul>")
                in_list = True
                list_tag = "ul"
            out.append(f"<li>{_inl(line.strip()[2:])}</li>")
            continue
        if re.match(r"^\d+\.\s", line.strip()):
            if not in_list:
                out.append("<ol>")
                in_list = True
                list_tag = "ol"
            out.append(f"<li>{_inl(re.sub(r'^[0-9]+.\\s*', '', line.strip()))}</li>")
            continue
        if in_list and not line.strip():
            out.append(f"</{list_tag}>")
            in_list = False

        hm = re.match(r"^(#{1,6})\s+(.*)", line)
        if hm:
            if in_list:
                out.append(f"</{list_tag}>")
                in_list = False
            lvl = len(hm.group(1))
            out.append(f"<h{lvl}>{_inl(hm.group(2))}</h{lvl}>")
            continue

        if line.strip() == "---":
            out.append("<hr>")
            continue

        if line.strip():
            out.append(f"<p>{_inl(line)}</p>")

    if in_table:
        out.append("</tbody></table>")
    if in_list:
        out.append(f"</{list_tag}>")
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inl(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', t)
    return t


def _write_html(filename, content):
    path = os.path.join(DOCS, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)


# ── Main ──────────────────────────────────────────────────────────────────


def main():
    print("Loading data...")
    teams = load_teams()
    schedule, by_date, ko_schedule = parse_schedule()
    groups_data = parse_group_stage()
    sim_data = parse_simulation()
    print(
        f"  {len(teams)} teams, {len(schedule)} scheduled matches, "
        f"{len(groups_data)} groups, {len(sim_data)} sim results"
    )

    print("\nGenerating HTML pages...")
    generate_index(teams, groups_data, sim_data, schedule, by_date, ko_schedule)
    for g in GROUPS:
        generate_group_page(g, groups_data, teams, schedule)
    generate_knockout(teams, ko_schedule)
    generate_prediction_method()
    print(f"\nDone! Generated {2 + len(GROUPS)} pages in {DOCS}/")


if __name__ == "__main__":
    main()
