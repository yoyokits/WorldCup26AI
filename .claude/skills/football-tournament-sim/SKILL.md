---
name: football-tournament-sim
description: Run a Monte Carlo simulation of the whole 48-team World Cup — play every group and knockout match thousands of times to get each team's probability of advancing, reaching the final, and winning the title. Use for tournament-wide odds and the most-likely champion, not a single scoreline.
user-invocable: true
allowed-tools:
  - Read
  - Bash(python *)
---

# Monte Carlo Tournament Simulation (Methodology)

**Category:** Methodology · **Method #5 of 5** · turns per-match models into tournament odds.

A single scoreline ([football-poisson-score](../football-poisson-score/SKILL.md)) can't tell you who *wins the tournament* — variance compounds across 7 knockout rounds. **Monte Carlo** runs the entire bracket thousands of times and counts outcomes, the same method behind public WC simulators (bracket2026, the open-source Elo+Dixon-Coles+MC models).

## How it works (`tools/predict.py`)

```
repeat N times (seeded RNG -> reproducible):
  for each of 12 groups:
     play all 6 fixtures, sampling goals ~ Poisson(lambda)   # sim_match
     rank by Pts, GD, GF, Elo
  qualifiers = 12 winners + 12 runners-up + 8 best 3rd-placed = 32
  seed single-elim bracket by Elo (1 vs 32, 2 vs 31, ...)
  play R32 -> R16 -> QF -> SF -> Final
     draws in knockout decided by penalty model (Elo win-expectancy)
  tally champion / finalist / semi-finalist
report each team's champ %, final %, SF %
```

- **Seeded** (`SEED = 2026`) so the same command always yields the same numbers.
- Goals sampled with Knuth's Poisson sampler (`_sample_poisson`).
- Penalty shootouts use `We = 1/(1 + 10^(-(EloA-EloB)/400))`.

## Run it

```bash
python tools/predict.py --sim 10000      # print ranked title odds
python tools/predict.py --all            # also writes data/Simulation.md
```

Sanity check: elite sides (Argentina, France, Spain, England, Brazil) should top the title odds; minnows (Fiji, Tonga) sit near 0%. If not, fix [football-strength-ratings](../football-strength-ratings/SKILL.md).

## Most-likely path vs probabilities

- **Probabilities** (champ %, etc.) come from the Monte Carlo run above.
- **The single predicted bracket** (one concrete champion + scorelines) comes from the deterministic most-likely path: chain [football-poisson-score](../football-poisson-score/SKILL.md) match-by-match with `--knockout`. Use [football-predict](../football-predict/SKILL.md) to produce both together.

## Bracket caveat

The R32 pairing here is a clean Elo-seeded bracket (a documented simplification of FIFA's group-cross pairing). Adjust `seed_bracket` in `tools/predict.py` if you want the exact official slotting once groups are final.
