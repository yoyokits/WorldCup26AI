---
name: football-poisson-score
description: Predict an exact football scoreline from team strength using the Poisson model — convert Elo into expected goals (lambda), then a full score-probability matrix, then the most-likely score and win/draw/loss odds. Use when you need a single match's predicted score and winner.
user-invocable: true
allowed-tools:
  - Read
  - Bash(python *)
---

# Poisson Scoreline Model (How to Predict)

**Category:** How to predict · **Method #2 of 5** · ~60–65% outcome accuracy on real data.

The workhorse of football prediction (Maher 1982; popularised by Pinnacle, penaltyblog, dashee87). Goals scored by a team in a match follow a **Poisson distribution**, so if we know each side's expected goals λ, we can compute the probability of every scoreline.

## The pipeline

```
Elo (football-strength-ratings)
  └─► attack & defence indices (relative to field-average Elo)
        └─► lambda_home, lambda_away   (expected goals each side)
              └─► Poisson score-probability matrix (0..8 goals each)
                    └─► most-likely cell = predicted exact score
                    └─► sum triangles    = win / draw / loss probabilities
```

## Step 1 — Elo to expected goals (λ)

Implemented in `tools/predict.py::expected_goals`. Stronger teams both score more and concede fewer:

```
mean   = field-average Elo (~1772 across the 48 teams)
atk_i  = exp(ALPHA * (elo_i - mean) / 100)        # ALPHA = 0.10
def_i  = exp(-ALPHA * (elo_i - mean) / 100)        # weaker -> leak more
lambda_home = BASE_GOALS * atk_home * def_away     # BASE_GOALS = 1.35
lambda_away = BASE_GOALS * atk_away * def_home
```
`BASE_GOALS = 1.35` gives a neutral match total of ~2.70 goals (the international rate). Host nations get `+70` Elo only at home.

## Step 2 — Poisson probability of k goals

```
P(k; lambda) = (lambda^k * e^-lambda) / k!
```
The joint probability of an exact scoreline (i home, j away) is `P(i;λ_home) * P(j;λ_away)` — then refined by [football-dixon-coles](../football-dixon-coles/SKILL.md) for low scores.

## Step 3 — read the matrix

- **Predicted exact score** = the single most-probable cell (`most_likely_score`).
- **Win / Draw / Loss** = sum of cells below / on / above the diagonal (`outcome_probs`).

## Run it

```bash
python tools/predict.py --match "Brazil vs Switzerland"
# -> lambda 1.9-0.9, win% 60/24/16, predicted 2-0 Brazil
```

## Limits (when to layer other skills)

Plain Poisson **underestimates draws** (fix: [football-dixon-coles](../football-dixon-coles/SKILL.md)) and ignores form/injuries/motivation (fix: [football-form-context](../football-form-context/SKILL.md)). For tournament-wide odds rather than a single score, use [football-tournament-sim](../football-tournament-sim/SKILL.md).
