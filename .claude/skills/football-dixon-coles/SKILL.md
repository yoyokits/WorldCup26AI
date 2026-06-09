---
name: football-dixon-coles
description: Apply the Dixon-Coles correction to a Poisson football model — fixes the well-known underestimation of 0-0/1-0/0-1/1-1 results and adds time-weighting so recent matches count more. Use when calibrating low-scoring/draw probabilities or tuning the rho/time-decay parameters.
user-invocable: true
allowed-tools:
  - Read
  - Bash(python *)
---

# Dixon–Coles Correction (Methodology)

**Category:** Methodology · **Method #3 of 5** · refines [football-poisson-score](../football-poisson-score/SKILL.md).

From **Dixon & Coles (1997), *Modelling Association Football Scores and Inefficiencies in the Football Betting Market***. Independent Poisson treats home and away goals as uncorrelated, which **under-counts low-scoring draws** (0-0 and 1-1 happen more than the math predicts). Dixon-Coles patches exactly the four low-score cells.

## The τ (tau) correction

Multiply these four scoreline probabilities by a factor before renormalising:

```
tau(0,0) = 1 - lambda_home * lambda_away * rho
tau(0,1) = 1 + lambda_home * rho
tau(1,0) = 1 + lambda_away * rho
tau(1,1) = 1 - rho
otherwise = 1
```
`rho` is negative (we use **rho = -0.08**). Negative rho **raises** P(0-0) and P(1-1) and **lowers** P(1-0)/P(0-1) — matching reality. Implemented in `tools/predict.py::_dc_tau`, applied in `score_matrix`, then the whole grid is renormalised to sum to 1.

## Time-weighting (recent form counts more)

Dixon-Coles also down-weights old matches when fitting ratings, via an exponential decay `phi(t) = exp(-xi * t)` where `t` = days since the match. In this project that role is played by:
- the **Elo ratings** already reflecting recent results, and
- [football-form-context](../football-form-context/SKILL.md), which nudges λ for current form/injuries.

If you later fit ratings from a match database, apply `exp(-xi * age_in_days)` with `xi ≈ 0.0018–0.003` (half-life ~1 year).

## Why it matters

Against plain Poisson, Dixon-Coles gives a 1–3% log-likelihood gain on 1X2 and noticeably better **correct-score** and **under/over** calibration — the 0-0 and 1-1 markets specifically. That precision is what makes knockout draw/penalty calls trustworthy.

## Tune & verify

```bash
python tools/predict.py --match "Tunisia vs Qatar"   # two cagey sides -> watch draw%
```
Edit `RHO` in `tools/predict.py` to recalibrate: more negative = more draws. Keep `rho ∈ [-0.15, -0.03]`.
