---
name: football-strength-ratings
description: Convert a national football team into a numeric strength rating (Elo blended with FIFA ranking + squad quality). The backbone every other prediction method consumes. Use when you need a single number for how strong a team is, or to seed/update tools/ratings.csv.
user-invocable: true
allowed-tools:
  - Read
  - Edit
  - Bash(python *)
---

# Football Strength Ratings (Statistics)

**Category:** Statistics · **Method #1 of 5** · feeds every other skill.

## What this is

Every prediction starts by reducing a team to one number: its **strength rating** on an Elo-style scale (roughly 1100 = weakest WC team, 2150 = strongest). This is the input to [football-poisson-score](../football-poisson-score/SKILL.md) and [football-tournament-sim](../football-tournament-sim/SKILL.md).

Source basis: the **Elo rating system** (eloratings.net) and the **Bradley–Terry–Davidson** model, blended with the official **FIFA World Ranking** and qualitative squad quality from `data/<Country>.md`.

## The rating scale (World Cup 2026 field)

| Tier | Elo | Example teams |
|------|-----|---------------|
| Elite | 2000–2150 | Argentina, France, Spain, Brazil, England |
| Strong | 1850–1999 | Portugal, Netherlands, Germany, Italy, Croatia, Uruguay |
| Solid | 1750–1849 | Japan, USA, Mexico, Senegal, Serbia, Iran |
| Mid | 1650–1749 | Tunisia, Qatar, Cameroon, Costa Rica, Panama |
| Weak | 1500–1649 | Saudi Arabia, Honduras, Bolivia, New Zealand |
| Minnow | 1100–1499 | Fiji, Tonga |

Ratings live in `tools/ratings.csv` (`team,slug,group,confederation,fifa_rank,elo,host`).

## How to derive / update a rating

1. **Anchor on FIFA rank** — lower rank = higher Elo. The CSV already encodes the 48-team field.
2. **Adjust for squad quality** from `data/<Country>.md`: key-player availability, club level, recent major-tournament results (Copa America, AFCON, Nations League, Euros).
3. **Host nations** (USA, Mexico, Canada) carry `host=1`; the engine adds a temporary home Elo bonus only when they play at home — do **not** bake it into the base Elo.
4. To change a rating, edit the `elo` column in `tools/ratings.csv`, then re-run predictions.

## Why Elo, not FIFA points directly

Elo differences map cleanly onto win probability via the logistic curve
`We = 1 / (1 + 10^(-(EloA - EloB)/400))`, which is what [football-tournament-sim](../football-tournament-sim/SKILL.md) uses for penalty shootouts and what [football-poisson-score](../football-poisson-score/SKILL.md) converts into expected goals.

## Verify

```bash
python tools/predict.py --match "Argentina vs Tonga"   # huge Elo gap -> blowout
python tools/predict.py --match "France vs Spain"       # small gap -> tight
```
A correct rating set makes elite teams beat minnows ~90%+ and peers ~40–45% each (rest draw).
