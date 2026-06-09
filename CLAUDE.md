# FIFA World Cup 2026 — AI Prediction Project

## Project Purpose

Generate AI-powered match-by-match predictions for the entire FIFA World Cup 2026 tournament (June 11 – July 19, 2026). Every match gets a predicted winner and exact scoreline. Results are stored in Markdown files under `data/` and visualized as HTML pages in `html/`.

---

## Repository Structure

```
WorldCup26AI/
├── CLAUDE.md                      # This file
├── data/
│   ├── WorldCup2026.md            # Tournament overview, format, venues, schedule
│   ├── countries.md               # All 48 teams with group assignments & analysis
│   ├── <CountryName>.md           # Per-team historical analysis (48 files)
│   ├── GroupStage.md              # Group stage predictions (all 72 matches)
│   ├── RoundOf32.md               # Round of 32 predictions (16 matches)
│   ├── RoundOf16.md               # Round of 16 predictions (8 matches)
│   ├── Quarterfinals.md           # Quarterfinal predictions (4 matches)
│   ├── Semifinals.md              # Semifinal predictions (2 matches)
│   ├── ThirdPlace.md              # Third place match prediction
│   └── Final.md                   # Final prediction + tournament champion
└── html/
    ├── images/                    # Team flag images (48 PNG files, already present)
    ├── index.html                 # Tournament home — groups overview, top contenders
    ├── group_<A-L>.html           # One page per group (12 pages) with match results
    ├── knockout.html              # Full knockout bracket visualization
    └── team_<name>.html           # Per-team page (optional, generated on demand)
```

---

## Tournament Format (Reference)

- **48 teams**, 12 groups (A–L) of 4 teams each
- **Group stage:** Each team plays 3 matches. Top 2 per group + 8 best 3rd-place teams → 32 teams advance
- **Knockout rounds:** Round of 32 (16 matches) → Round of 16 (8 matches) → Quarterfinals (4 matches) → Semifinals (2 matches) → Third Place + Final
- **Total matches:** 104
- **Final:** July 19, 2026 at MetLife Stadium, New Jersey

---

## Group Compositions (from `countries.md`)

| Group | Teams |
|-------|-------|
| A | Argentina, Jamaica, Morocco, Egypt |
| B | Spain, Japan, USA, Ghana |
| C | Brazil, South Korea, Switzerland, Cameroon |
| D | France, Canada, Uruguay, Saudi Arabia |
| E | Portugal, Croatia, Tunisia, Ecuador |
| F | Germany, Colombia, Nigeria, Honduras |
| G | Netherlands, Serbia, Mexico, Australia |
| H | England, Slovenia, Paraguay, Tonga |
| I | Italy, Wales, Qatar, Fiji |
| J | Senegal, Poland, Costa Rica, New Zealand |
| K | Iran, Sweden, Panama, Bolivia |
| L | Ukraine, Turkey, South Africa, Guinea |

> Note: `countries.md` documents Groups A–G with full scouting profiles. Groups H–L were constructed (seeded snake-draft of the remaining 20 teams) since the source left them as TODO. The **authoritative machine-readable group + rating list is `tools/ratings.csv`** (48 teams).

---

## Prediction Methodology & Skills

Predictions are produced by a reproducible engine, not freehand guessing. Six **Claude Code skills** in `.claude/skills/` encode the best statistical methods from football analytics, and the deterministic, seeded engine `tools/predict.py` (pure Python stdlib — no pip installs) implements them.

### The pipeline

```
FIFA ranking + profile (data/*.md, tools/ratings.csv)
   └─► [1] Strength rating  (Elo scale, e.g. Argentina 2140, Tonga 1100)
          └─► attack & defence indices vs field average
                └─► [2] λ_home, λ_away  (expected goals each side)
                       └─► [4] nudge λ for form / injuries / host / set-pieces
                              └─► [3] Poisson + Dixon-Coles score matrix
                                     └─► winner + most-likely exact scoreline
Tournament-wide: [5] Monte Carlo (10,000 seeded sims) → advancement & title odds
```

### The skills (run `/<name>` or read `.claude/skills/<name>/SKILL.md`)

| # | Skill | Category | Role |
|---|-------|----------|------|
| 1 | `football-strength-ratings` | Statistics | Team → Elo rating (backbone) |
| 2 | `football-poisson-score` | How to predict | Elo → λ → exact score + W/D/L % |
| 3 | `football-dixon-coles` | Methodology | Low-score / draw correction (ρ) + time-weighting |
| 4 | `football-form-context` | Statistics + History | Form / xG / injury / host nudges from `data/*.md` |
| 5 | `football-tournament-sim` | Methodology | Monte Carlo bracket → title odds |
| 6 | `football-predict` | Orchestrator | End-to-end; chains 1–5, writes `data/` + `html/` |

Sources: Dixon & Coles (1997); Maher (1982); Pinnacle / penaltyblog Poisson method; eloratings.net; public WC Monte Carlo simulators.

### Engine quick reference

```bash
python tools/predict.py --match "Argentina vs Jamaica"      # one game
python tools/predict.py --match "France vs USA" --knockout  # force a winner
python tools/predict.py --group C                           # full group table
python tools/predict.py --sim 10000                         # title odds
python tools/predict.py --all     # regenerate data/GroupStage.md + data/Simulation.md
```

Model constants live at the top of `tools/predict.py` (`BASE_GOALS`, `ALPHA`, `RHO`, `HOME_ELO_BONUS`, `SEED`). Team strength is edited in `tools/ratings.csv`.

### Score Format

Predictions should always include:
- **Winner** (or "Draw" for group stage)
- **Score** e.g. `2–1`, `1–0`, `0–0`, `3–2 (aet)`, `1–1 (4–3 pens)`
- **Brief reasoning** (1–2 sentences per match)

---

## Data Files — Specification

### `data/GroupStage.md`
Structure per group:
```
## Group A

| # | Date | Home | Score | Away | Venue |
|---|------|------|-------|------|-------|
| 1 | June 12 | Argentina | 3–0 | Jamaica | ... |
...

### Group A — Final Standings
| Pos | Team | P | W | D | L | GF | GA | GD | Pts |
```

### `data/RoundOf32.md` through `data/Final.md`
Structure:
```
## Match N — [Team A] vs [Team B]
- **Prediction:** Team A wins 2–1
- **Reasoning:** ...
```

---

## HTML Visualization — Specification

### `html/index.html`
- Tournament header with dates and host info
- Group grid (A–L) showing teams with flag images from `html/images/`
- Top contenders section
- Link to knockout bracket

### `html/group_<X>.html` (12 files, one per group A–L)
- Group table with match schedule and predicted scores
- Final predicted standings table

### `html/knockout.html`
- Visual bracket from Round of 32 to Final
- Each match box: flag + team name + predicted score
- Highlight predicted champion

### HTML style guidelines
- Self-contained HTML (no external CSS framework dependencies unless CDN-linked)
- Flag images referenced as `images/<country-slug>.png` (all present)
- Mobile-friendly layout preferred
- Color scheme: World Cup 2026 brand colors (blue, red, white)

---

## Work Plan

### Phase 1 — Group Stage Predictions
- [ ] Create `data/GroupStage.md` with all 72 match predictions (Groups A–L)
- [ ] Populate Groups H–L in `countries.md` from the draw

### Phase 2 — HTML Group Pages
- [ ] Create `html/index.html` with tournament overview and group grid
- [ ] Create `html/group_a.html` through `html/group_l.html` (12 files)

### Phase 3 — Knockout Stage Predictions
- [ ] Create `data/RoundOf32.md` (16 matches)
- [ ] Create `data/RoundOf16.md` (8 matches)
- [ ] Create `data/Quarterfinals.md` (4 matches)
- [ ] Create `data/Semifinals.md` (2 matches)
- [ ] Create `data/ThirdPlace.md`
- [ ] Create `data/Final.md` — declare tournament champion

### Phase 4 — Knockout HTML
- [ ] Create `html/knockout.html` with full bracket visualization

---

## Key Facts for Predictions

- **Defending champion:** Argentina 🇦🇷 (beat France in 2022 final on penalties)
- **Top favorites:** France, Spain, Brazil, England, Portugal, Germany
- **Dark horses:** Japan, Morocco, USA, Croatia, Colombia
- **Opening match:** Mexico vs. South Africa — June 11 at Estadio Azteca
- **Flag images available for:** argentina, australia, bolivia, brazil, cameroon, canada, colombia, costa-rica, croatia, ecuador, egypt, england, fiji, france, germany, ghana, guinea, honduras, iran, italy, jamaica, japan, mexico, morocco, netherlands, new-zealand, nigeria, panama, paraguay, poland, portugal, qatar, saudi-arabia, senegal, serbia, slovenia, south-africa, south-korea, spain, sweden, switzerland, tonga, tunisia, turkey, ukraine, uruguay, usa, wales
