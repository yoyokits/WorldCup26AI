---
name: football-predict
description: Predict World Cup 2026 results end-to-end — winner and exact score for any match, a full group, or the whole tournament. Orchestrates the strength-ratings, Poisson, Dixon-Coles, form-context, and Monte-Carlo skills and writes results to data/ and html/. Use whenever the user asks "who wins / what's the score" for any 2026 fixture or the tournament.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(python *)
---

# /football-predict — World Cup 2026 Prediction Orchestrator

The **entry point**. Chains the five methodology skills into one answer: a winner + exact scoreline for any fixture, or full group tables and tournament odds. Arguments: `$ARGUMENTS`.

## The five methods it orchestrates

1. [football-strength-ratings](../football-strength-ratings/SKILL.md) — Elo per team (`tools/ratings.csv`)
2. [football-poisson-score](../football-poisson-score/SKILL.md) — Elo → λ → exact score
3. [football-dixon-coles](../football-dixon-coles/SKILL.md) — low-score / draw correction
4. [football-form-context](../football-form-context/SKILL.md) — form / injury / host nudges
5. [football-tournament-sim](../football-tournament-sim/SKILL.md) — Monte Carlo title odds

All five are implemented in the reproducible engine `tools/predict.py` (pure stdlib — no pip installs).

## How to respond to a request

**Single match** ("who wins X vs Y", "score of X v Y"):
```bash
python tools/predict.py --match "France vs USA"            # group-stage
python tools/predict.py --match "France vs USA" --knockout # forces a winner (aet/pens)
```
Then read `data/<X>.md` / `data/<Y>.md` and apply [football-form-context](../football-form-context/SKILL.md) before stating the final call. Report: **winner, exact score, win/draw/loss %, one-line reasoning**.

**A whole group:**
```bash
python tools/predict.py --group C
```

**The whole tournament:**
```bash
python tools/predict.py --all        # writes data/GroupStage.md + data/Simulation.md
python tools/predict.py --sim 10000  # title odds to stdout
```

## Producing the knockout prediction files

The engine writes group stage + simulation. For the deterministic knockout rounds (`data/RoundOf32.md` … `data/Final.md`), take the qualifiers from `data/GroupStage.md`, then call `--match ... --knockout` for each tie round by round, recording winner + score. Declare the champion in `data/Final.md`.

## Output format (always)

For each match:
```
[Team A] [score] [Team B]  — Winner: [team] (note if pens)
Win/Draw/Loss: 50% / 26% / 24%   λ 1.67–1.09
Reasoning: <1–2 lines grounded in ratings + data/*.md>
```

## Visualization

After predictions exist in `data/`, build the HTML in `html/` per `CLAUDE.md` (index, `group_<a-l>.html`, `knockout.html`) using flag images in `html/images/<slug>.png`. Slugs are the `slug` column of `tools/ratings.csv`.

## Golden rules

- **Reproducible first:** prefer the seeded engine over freehand guesses; same input → same score.
- **Ground every call** in a rating and a line from `data/*.md` — no vibes-only predictions.
- **Context nudges the margin, not the outcome** (see [football-form-context](../football-form-context/SKILL.md)), except genuine upset setups.
- Keep `tools/ratings.csv` the single source of truth for team strength.
