---
name: football-form-context
description: Adjust a team's expected goals for the qualitative context that pure ratings miss — recent form, expected goals (xG), key-player injuries, host advantage, set-piece threat, and motivation. Use to fine-tune a match prediction with the scouting notes in data/*.md before finalizing a scoreline.
user-invocable: true
allowed-tools:
  - Read
  - Edit
  - Bash(python *)
---

# Form / xG / Context Adjustment (Statistics + History)

**Category:** Statistics + History · **Method #4 of 5** · the human-judgement layer over the math.

Ratings ([football-strength-ratings](../football-strength-ratings/SKILL.md)) capture baseline quality but not *this month's* reality. This skill adjusts the expected-goals λ from [football-poisson-score](../football-poisson-score/SKILL.md) using the scouting profiles in `data/countries.md` and `data/<Country>.md`.

## Adjustment checklist (read `data/<Country>.md` first)

| Factor | Where to find it | Typical λ / Elo nudge |
|--------|------------------|------------------------|
| **Recent form** (last 5–10) | "Recent form" lines in `data/countries.md` | ±0.1–0.2 λ |
| **Expected goals (xG)** | club-level scoring notes in team file | aligns λ up/down |
| **Key-player injury** | "Key players" list | −0.15 to −0.4 λ if a Messi/Mbappé-tier player is out |
| **Host advantage** | `host=1` in `tools/ratings.csv` | +70 Elo at home (auto) |
| **Set-piece threat** | "Strengths" notes | +0.1 λ vs weak-aerial sides |
| **Motivation / must-win** | group situation | small ± |
| **Altitude / travel** | venue notes in `WorldCup2026.md` | situational |

## How to apply

Two routes:
1. **Engine route (preferred):** encode durable context as an Elo tweak in `tools/ratings.csv` (e.g. drop a team's Elo if their talisman is injured for the tournament), then re-run `tools/predict.py`. Keeps everything reproducible.
2. **Per-match route:** after running `--match`, manually shift the predicted score by one goal when a one-off factor is decisive (e.g. star striker suspended for *this* game), and record the reason in the match note.

## xG primer

Expected goals (xG) scores chance quality, not just shot count — a better signal of true team strength than raw goals over small samples. When a team's results outrun their xG, regress your λ toward the xG; when xG > goals, nudge λ up (they're due).

## Guardrail

Adjustments are **small nudges**, not overrides. If your context tweak flips a heavy favourite into a loss, you are probably over-weighting a narrative. Trust [football-strength-ratings](../football-strength-ratings/SKILL.md) as the prior; let context move the margin, not the outcome, except for genuine upset setups (elite team resting players in a dead rubber).

## Verify

Compare engine output to your adjusted call and make sure the delta is defensible from a line you can cite in `data/<Country>.md`.
