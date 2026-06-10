#!/usr/bin/env python3
"""
FIFA World Cup 2026 — Match & Tournament Prediction Engine
==========================================================

Pure standard-library implementation (no numpy/scipy/pip required).

Methodology pipeline (see .claude/skills/football-* and CLAUDE.md):
  1. Strength ratings  : each team -> Elo rating (tools/ratings.csv)
  2. Expected goals     : Elo -> attack/defence indices -> lambda (mean goals)
  3. Poisson + Dixon-Coles : full scoreline probability matrix, low-score
                             dependency correction (rho)
  4. Form / context     : host advantage applied to host nations at home
  5. Monte Carlo        : simulate the full 48-team bracket N times, seeded

CLI:
  python tools/predict.py --match "Argentina vs Jamaica"
  python tools/predict.py --group A
  python tools/predict.py --sim 10000
  python tools/predict.py --all            # regenerate every data/*.md
"""

import argparse
import csv
import math
import os
import random
from collections import defaultdict

# --------------------------------------------------------------------------
# Model constants (tuned for international / World Cup scoring rates)
# --------------------------------------------------------------------------
BASE_GOALS = 1.35      # half of the neutral expected match total (~2.70 goals)
ALPHA = 0.10           # Elo -> goal-strength sensitivity (per 100 Elo)
RHO = -0.08            # Dixon-Coles low-score correction (negative)
HOME_ELO_BONUS = 70.0  # host-nation advantage when playing in their country
MAX_GOALS = 8          # scoreline grid upper bound
SEED = 2026            # fixed seed -> reproducible simulations

# Skill #4 context-nudge weights
FORM_WEIGHT    = 0.15  # ±15% λ per unit of form (range: -1..+1)
INJURY_WEIGHT  = 0.40  # scale raw injury_impact → max ~12% λ reduction
FATIGUE_WEIGHT = 0.06  # up to 6% λ reduction at fatigue=1.0
SET_PIECE_MEAN = 6.0   # rating scale anchor (1–10)
SET_PIECE_WGHT = 0.04  # ±4% λ per net set-piece point above/below mean
COACH_MEAN     = 7.0   # anchor for coach_rating (1–10)
COACH_WEIGHT   = 0.03  # ±3% λ per coach_rating point above/below mean
DRAW_PULL      = 0.15  # predict draw when best win prob leads draw by < 15pp
AGE_MEAN       = 27.0  # neutral squad age; older/younger nudges λ
AGE_WEIGHT     = 0.012 # ±1.2% λ per year away from mean
DEPTH_MEAN     = 5.0   # anchor for squad_depth (1–10)
DEPTH_INJ_MOD  = 0.06  # each depth point above mean reduces injury impact by 6%
PRESSURE_MEAN  = 6.0   # anchor for pressure_rating (1–10)
PRESSURE_PENS  = 0.25  # weight of pressure_rating in penalty shoot-out
EXP_PENS_WGHT  = 0.10  # weight of wc_experience in penalty shoot-out

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
DEFAULT_RATINGS = os.path.join(HERE, "ratings.csv")

GROUPS = list("ABCDEFGHIJKL")  # 12 groups

# --------------------------------------------------------------------------
# 1. Strength ratings
# --------------------------------------------------------------------------
def load_ratings(path=DEFAULT_RATINGS):
    teams = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            row["fifa_rank"] = int(row["fifa_rank"])
            row["elo"] = float(row["elo"])
            row["host"] = bool(int(row["host"]))
            for col in ("attack_avg", "defense_avg",
                        "form", "injury_impact", "fatigue"):
                if row.get(col):
                    row[col] = float(row[col])
            for col in ("squad_depth", "wc_experience",
                        "set_piece_off", "set_piece_def",
                        "pressure_rating", "coach_rating"):
                if row.get(col):
                    row[col] = float(row[col])
            if row.get("avg_age"):
                row["avg_age"] = float(row["avg_age"])
            teams[row["team"]] = row
    if not teams:
        raise SystemExit("No teams loaded from %s" % path)
    tlist = list(teams.values())
    mean_elo = sum(t["elo"] for t in tlist) / len(tlist)
    # Field-average attack/defence for Dixon-Coles normalisation
    with_avg = [t for t in tlist if t.get("attack_avg")]
    if with_avg:
        mean_atk = sum(t["attack_avg"] for t in with_avg) / len(with_avg)
        mean_def = sum(t["defense_avg"] for t in with_avg) / len(with_avg)
    else:
        mean_atk = mean_def = BASE_GOALS
    for t in tlist:
        t["mean_elo"] = mean_elo
        t["mean_attack_avg"] = mean_atk
        t["mean_defense_avg"] = mean_def
    return teams


def resolve_team(teams, name):
    """Case-insensitive / partial team-name lookup."""
    name = name.strip()
    if name in teams:
        return name
    low = name.lower()
    for key in teams:
        if key.lower() == low:
            return key
    matches = [k for k in teams if low in k.lower()]
    if len(matches) == 1:
        return matches[0]
    raise SystemExit("Unknown or ambiguous team: %r (candidates: %s)"
                     % (name, ", ".join(matches) or "none"))


# --------------------------------------------------------------------------
# 2. Expected goals (lambda) from Elo
# --------------------------------------------------------------------------
def expected_goals(a, b, host_aware=True):
    """Return (lambda_a, lambda_b): mean goals for each side.

    When attack_avg/defense_avg are present in the ratings (actual goals scored
    and conceded per game), they are blended with the Elo-derived indices at
    55/45 weight — giving real historical data priority while Elo corrects for
    opponent quality. Host nations receive a temporary Elo bonus.
    """
    mean = a["mean_elo"]
    elo_a = a["elo"] + (HOME_ELO_BONUS if (host_aware and a["host"]) else 0.0)
    elo_b = b["elo"] + (HOME_ELO_BONUS if (host_aware and b["host"]) else 0.0)

    elo_atk_a = math.exp(ALPHA * (elo_a - mean) / 100.0)
    elo_atk_b = math.exp(ALPHA * (elo_b - mean) / 100.0)
    elo_def_a = math.exp(-ALPHA * (elo_a - mean) / 100.0)
    elo_def_b = math.exp(-ALPHA * (elo_b - mean) / 100.0)

    if a.get("attack_avg") and a.get("mean_attack_avg"):
        m_atk = a["mean_attack_avg"]
        m_def = a["mean_defense_avg"]
        # Normalise actual averages to the same scale as Elo indices (centred at 1.0)
        # defense_avg = goals conceded; lower is stronger → same direction as Elo def index
        atk_a = 0.55 * (a["attack_avg"]  / m_atk) + 0.45 * elo_atk_a
        atk_b = 0.55 * (b["attack_avg"]  / m_atk) + 0.45 * elo_atk_b
        def_a = 0.55 * (a["defense_avg"] / m_def) + 0.45 * elo_def_a
        def_b = 0.55 * (b["defense_avg"] / m_def) + 0.45 * elo_def_b
    else:
        atk_a, atk_b = elo_atk_a, elo_atk_b
        def_a, def_b = elo_def_a, elo_def_b

    lam_a = BASE_GOALS * atk_a * def_b
    lam_b = BASE_GOALS * atk_b * def_a

    # --- Skill #4: form / injury / fatigue / set-piece / coach nudges ---
    def _nudge(lam, team, opp):
        form   = float(team.get("form", 0.0))
        inj    = float(team.get("injury_impact", 0.0))
        fat    = float(team.get("fatigue", 0.2))
        spo    = float(team.get("set_piece_off", SET_PIECE_MEAN))
        spd_op = float(opp.get("set_piece_def", SET_PIECE_MEAN))
        coach  = float(team.get("coach_rating", COACH_MEAN))
        depth  = float(team.get("squad_depth", DEPTH_MEAN))

        lam *= (1.0 + form * FORM_WEIGHT)

        depth_reduction = max(0.0, (depth - DEPTH_MEAN) * DEPTH_INJ_MOD)
        effective_inj = inj * INJURY_WEIGHT * (1.0 - depth_reduction)
        lam *= (1.0 - min(effective_inj, 0.15))

        lam *= (1.0 - fat * FATIGUE_WEIGHT)

        sp_net = (spo - spd_op) / SET_PIECE_MEAN
        lam *= (1.0 + sp_net * SET_PIECE_WGHT)

        lam *= (1.0 + (coach - COACH_MEAN) * COACH_WEIGHT)

        age = float(team.get("avg_age", AGE_MEAN))
        age_dev = age - AGE_MEAN
        if age_dev > 0:
            lam *= (1.0 - age_dev * AGE_WEIGHT)
        elif age_dev < -1.5:
            lam *= (1.0 + age_dev * AGE_WEIGHT * 0.5)
        return lam

    lam_a = _nudge(lam_a, a, b)
    lam_b = _nudge(lam_b, b, a)
    return max(lam_a, 0.05), max(lam_b, 0.05)


# --------------------------------------------------------------------------
# 3. Poisson + Dixon-Coles scoreline matrix
# --------------------------------------------------------------------------
def _poisson(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def _dc_tau(i, j, lam_a, lam_b, rho=RHO):
    if i == 0 and j == 0:
        return 1.0 - lam_a * lam_b * rho
    if i == 0 and j == 1:
        return 1.0 + lam_a * rho
    if i == 1 and j == 0:
        return 1.0 + lam_b * rho
    if i == 1 and j == 1:
        return 1.0 - rho
    return 1.0


def score_matrix(lam_a, lam_b):
    grid = [[0.0] * (MAX_GOALS + 1) for _ in range(MAX_GOALS + 1)]
    total = 0.0
    for i in range(MAX_GOALS + 1):
        for j in range(MAX_GOALS + 1):
            p = _poisson(i, lam_a) * _poisson(j, lam_b) * _dc_tau(i, j, lam_a, lam_b)
            p = max(p, 0.0)
            grid[i][j] = p
            total += p
    if total > 0:                       # renormalise after the DC correction
        for i in range(MAX_GOALS + 1):
            for j in range(MAX_GOALS + 1):
                grid[i][j] /= total
    return grid


def outcome_probs(grid):
    ph = pd = pa = 0.0
    for i in range(len(grid)):
        for j in range(len(grid)):
            if i > j:
                ph += grid[i][j]
            elif i == j:
                pd += grid[i][j]
            else:
                pa += grid[i][j]
    return ph, pd, pa


def most_likely_score(grid, outcome=None):
    """Most-probable scoreline. If `outcome` is 'home'/'draw'/'away', restrict
    to cells consistent with that result (modal score *given* the modal
    outcome) — avoids the artefact where 1-1 is the modal cell even when the
    favourite is more likely than not to win."""
    best, bi, bj = -1.0, 0, 0
    for i in range(len(grid)):
        for j in range(len(grid)):
            if outcome == "home" and not i > j:
                continue
            if outcome == "away" and not j > i:
                continue
            if outcome == "draw" and i != j:
                continue
            if grid[i][j] > best:
                best, bi, bj = grid[i][j], i, j
    return bi, bj, best


# --------------------------------------------------------------------------
# Single-match prediction (deterministic, most-likely)
# --------------------------------------------------------------------------
def predict_match(a, b, knockout=False):
    lam_a, lam_b = expected_goals(a, b)
    grid = score_matrix(lam_a, lam_b)
    ph, pd, pa = outcome_probs(grid)

    result = {
        "home": a["team"], "away": b["team"],
        "lam_a": lam_a, "lam_b": lam_b,
        "p_home": ph, "p_draw": pd, "p_away": pa,
        "knockout": knockout,
    }

    if not knockout:
        best_win = max(ph, pa)
        if pd >= best_win:
            outcome = "draw"
        elif (best_win - pd) < DRAW_PULL:
            outcome = "draw"
        elif ph >= pa:
            outcome = "home"
        else:
            outcome = "away"
        gi, gj, _ = most_likely_score(grid, outcome)
        result["score_a"], result["score_b"] = gi, gj
        result["winner"] = (a["team"] if outcome == "home"
                            else b["team"] if outcome == "away" else "Draw")
        result["note"] = ""
        return result

    # Knockout: a winner is required, so ignore the draw region. Pick the more
    # likely side, then its modal winning score; report penalties if the tie
    # would most likely be level in 90 minutes.
    winner_side = "home" if ph >= pa else "away"
    gi, gj, _ = most_likely_score(grid, winner_side)
    result["score_a"], result["score_b"] = gi, gj
    result["winner"] = a["team"] if winner_side == "home" else b["team"]
    result["note"] = "aet/pens" if pd >= max(ph, pa) else ""
    return result


def fmt_score(r):
    s = "%d-%d" % (r["score_a"], r["score_b"])
    if r.get("note"):
        winner_pens = r["winner"]
        s += " (%s, %s adv.)" % (r["note"], winner_pens)
    return s


# --------------------------------------------------------------------------
# 5. Monte Carlo simulation
# --------------------------------------------------------------------------
def sim_match(rng, a, b, host_aware=True):
    lam_a, lam_b = expected_goals(a, b, host_aware=host_aware)
    return _sample_poisson(rng, lam_a), _sample_poisson(rng, lam_b)


def _sample_poisson(rng, lam):
    # Knuth's algorithm (fine for the small lambdas here).
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= L:
            return k - 1


def group_of(teams, g):
    members = [t for t in teams.values() if t["group"] == g]
    return sorted(members, key=lambda t: t["fifa_rank"])


def round_robin(group):
    """Standard 4-team fixture order using seed positions 0..3."""
    i = group
    return [(i[0], i[1]), (i[2], i[3]),
            (i[0], i[2]), (i[1], i[3]),
            (i[0], i[3]), (i[1], i[2])]


def play_group(rng, group, host_aware=True):
    table = {t["team"]: dict(team=t, P=0, W=0, D=0, L=0, GF=0, GA=0, Pts=0)
             for t in group}
    for home, away in round_robin(group):
        gh, ga = sim_match(rng, home, away, host_aware)
        for side, gf, gaa in ((home, gh, ga), (away, ga, gh)):
            row = table[side["team"]]
            row["P"] += 1
            row["GF"] += gf
            row["GA"] += gaa
        if gh > ga:
            table[home["team"]]["W"] += 1
            table[home["team"]]["Pts"] += 3
            table[away["team"]]["L"] += 1
        elif ga > gh:
            table[away["team"]]["W"] += 1
            table[away["team"]]["Pts"] += 3
            table[home["team"]]["L"] += 1
        else:
            table[home["team"]]["D"] += 1
            table[away["team"]]["D"] += 1
            table[home["team"]]["Pts"] += 1
            table[away["team"]]["Pts"] += 1
    return table


def _standings_list(table):
    rows = list(table.values())
    for r in rows:
        r["GD"] = r["GF"] - r["GA"]
        r["team_elo"] = r["team"]["elo"] if isinstance(r["team"], dict) else 0
    rows.sort(key=lambda r: (r["Pts"], r["GD"], r["GF"], r["team"]["elo"]),
              reverse=True)
    return rows


def knockout_winner(rng, a, b):
    gh, ga = sim_match(rng, a, b, host_aware=False)
    if gh > ga:
        return a, b
    if ga > gh:
        return b, a
    # penalties: blend Elo expectancy + pressure_rating + wc_experience
    elo_pa = 1.0 / (1.0 + 10 ** (-(a["elo"] - b["elo"]) / 400.0))
    pres_a = float(a.get("pressure_rating", PRESSURE_MEAN))
    pres_b = float(b.get("pressure_rating", PRESSURE_MEAN))
    pres_pa = pres_a / (pres_a + pres_b)
    exp_a = float(a.get("wc_experience", 5))
    exp_b = float(b.get("wc_experience", 5))
    exp_pa = exp_a / max(exp_a + exp_b, 1)
    pa = ((1.0 - PRESSURE_PENS - EXP_PENS_WGHT) * elo_pa
          + PRESSURE_PENS * pres_pa
          + EXP_PENS_WGHT * exp_pa)
    return (a, b) if rng.random() < pa else (b, a)


def seed_bracket(qualifiers):
    """Standard single-elimination seeding (1 vs N, 2 vs N-1, ...)."""
    seeds = sorted(qualifiers, key=lambda t: t["elo"], reverse=True)
    n = len(seeds)
    return [(seeds[i], seeds[n - 1 - i]) for i in range(n // 2)]


def simulate_tournament(rng, teams, host_aware=True):
    """Return champion, finalists, and per-team furthest round reached.

    Each group is played exactly once so the RNG stream stays consistent.
    """
    winners_runners = []
    thirds_rows = []
    for g in GROUPS:
        grp = group_of(teams, g)
        rows = _standings_list(play_group(rng, grp, host_aware))
        winners_runners.append(rows[0]["team"])  # group winner
        winners_runners.append(rows[1]["team"])  # runner-up
        thirds_rows.append(rows[2])

    thirds_rows.sort(key=lambda r: (r["Pts"], r["GD"], r["GF"]), reverse=True)
    qualifiers = winners_runners + [r["team"] for r in thirds_rows[:8]]
    field = qualifiers[:32]

    reached = {t["team"]: "R32" for t in field}

    round_names = ["R16", "QF", "SF", "F"]
    pairs = seed_bracket(field)
    rn_idx = 0
    finalists = []
    while True:
        winners = []
        for a, b in pairs:
            w, _loser = knockout_winner(rng, a, b)
            winners.append(w)
            reached[w["team"]] = round_names[min(rn_idx, len(round_names) - 1)]
        if len(winners) == 2:
            finalists = winners[:]
        if len(winners) == 1:
            champion = winners[0]
            reached[champion["team"]] = "W"
            return champion, finalists, reached
        pairs = [(winners[i], winners[i + 1]) for i in range(0, len(winners), 2)]
        rn_idx += 1


def monte_carlo(teams, n=10000, host_aware=True):
    rng = random.Random(SEED)
    champions = defaultdict(int)
    finals = defaultdict(int)
    deep = defaultdict(int)  # reached SF or better
    for _ in range(n):
        champ, finalists, reached = simulate_tournament(rng, teams, host_aware)
        champions[champ["team"]] += 1
        for f in finalists:
            finals[f["team"]] += 1
        for name, rnd in reached.items():
            if rnd in ("SF", "F", "W"):
                deep[name] += 1
    out = []
    for name in teams:
        out.append({
            "team": name,
            "champ_pct": 100.0 * champions[name] / n,
            "final_pct": 100.0 * finals[name] / n,
            "sf_pct": 100.0 * deep[name] / n,
        })
    out.sort(key=lambda r: r["champ_pct"], reverse=True)
    return out


# --------------------------------------------------------------------------
# Output writers
# --------------------------------------------------------------------------
def write_group_stage(teams, path=None):
    path = path or os.path.join(DATA, "GroupStage.md")
    rng = random.Random(SEED)
    lines = ["# World Cup 2026 — Group Stage Predictions",
             "",
             "> Generated by `tools/predict.py` (Elo + Poisson + Dixon-Coles). "
             "Deterministic most-likely scorelines.",
             ""]
    for g in GROUPS:
        grp = group_of(teams, g)
        lines.append("## Group %s\n" % g)
        lines.append("| # | Home | Score | Away | Winner |")
        lines.append("|---|------|-------|------|--------|")
        table = {t["team"]: dict(team=t, P=0, W=0, D=0, L=0, GF=0, GA=0, Pts=0)
                 for t in grp}
        for n, (home, away) in enumerate(round_robin(grp), 1):
            r = predict_match(home, away, knockout=False)
            lines.append("| %d | %s | %d-%d | %s | %s |" % (
                n, home["team"], r["score_a"], r["score_b"], away["team"],
                r["winner"]))
            _apply_result(table, home, away, r["score_a"], r["score_b"])
        lines.append("")
        lines.append("### Group %s — Predicted Standings\n" % g)
        lines.append("| Pos | Team | P | W | D | L | GF | GA | GD | Pts |")
        lines.append("|-----|------|---|---|---|---|----|----|----|-----|")
        rows = _standings_list(table)
        for pos, r in enumerate(rows, 1):
            tag = " ✅" if pos <= 2 else (" 🟡" if pos == 3 else "")
            lines.append("| %d%s | %s | %d | %d | %d | %d | %d | %d | %+d | %d |" % (
                pos, tag, r["team"]["team"], r["P"], r["W"], r["D"], r["L"],
                r["GF"], r["GA"], r["GD"], r["Pts"]))
        lines.append("")
    _write(path, "\n".join(lines))
    return path


def _apply_result(table, home, away, gh, ga):
    for side, gf, gaa in ((home, gh, ga), (away, ga, gh)):
        row = table[side["team"]]
        row["P"] += 1
        row["GF"] += gf
        row["GA"] += gaa
    if gh > ga:
        table[home["team"]]["W"] += 1
        table[home["team"]]["Pts"] += 3
        table[away["team"]]["L"] += 1
    elif ga > gh:
        table[away["team"]]["W"] += 1
        table[away["team"]]["Pts"] += 3
        table[home["team"]]["L"] += 1
    else:
        for s in (home, away):
            table[s["team"]]["D"] += 1
            table[s["team"]]["Pts"] += 1


def write_simulation(teams, n=10000, path=None):
    path = path or os.path.join(DATA, "Simulation.md")
    results = monte_carlo(teams, n=n)
    lines = ["# World Cup 2026 — Monte Carlo Simulation (%d runs)" % n,
             "",
             "> Generated by `tools/predict.py`. Seeded (%d) for reproducibility."
             % SEED,
             "",
             "| Rank | Team | Champion % | Final % | Semi-final % |",
             "|------|------|-----------|---------|--------------|"]
    for i, r in enumerate(results, 1):
        if r["sf_pct"] < 0.05 and i > 24:
            continue
        lines.append("| %d | %s | %.1f%% | %.1f%% | %.1f%% |" % (
            i, r["team"], r["champ_pct"], r["final_pct"], r["sf_pct"]))
    _write(path, "\n".join(lines))
    return path, results


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")


# --------------------------------------------------------------------------
# Knockout stage: deterministic bracket from group stage results
# --------------------------------------------------------------------------
def _get_group_results(teams):
    """Replay the deterministic group stage and return qualifiers."""
    all_standings = {}
    thirds = []
    for g in GROUPS:
        grp = group_of(teams, g)
        table = {t["team"]: dict(team=t, P=0, W=0, D=0, L=0, GF=0, GA=0, Pts=0)
                 for t in grp}
        for home, away in round_robin(grp):
            r = predict_match(home, away, knockout=False)
            _apply_result(table, home, away, r["score_a"], r["score_b"])
        rows = _standings_list(table)
        all_standings[g] = rows
        thirds.append(rows[2])

    thirds.sort(key=lambda r: (r["Pts"], r["GD"], r["GF"]), reverse=True)
    qualifiers = []
    for g in GROUPS:
        qualifiers.append(all_standings[g][0]["team"])  # winner
        qualifiers.append(all_standings[g][1]["team"])  # runner-up
    qualifiers += [r["team"] for r in thirds[:8]]  # best 8 third-place
    return qualifiers[:32]


def _bracket_pairs(qualifiers):
    """Seed 32 qualifiers by Elo into a standard single-elimination bracket."""
    seeds = sorted(qualifiers, key=lambda t: t["elo"], reverse=True)
    n = len(seeds)
    return [(seeds[i], seeds[n - 1 - i]) for i in range(n // 2)]


def _fmt_knockout_match(num, r):
    """Format a single knockout match for Markdown output."""
    score_str = "%d-%d" % (r["score_a"], r["score_b"])
    if r.get("note"):
        score_str += " (%s)" % r["note"]
    lines = [
        "## Match %d — %s vs %s" % (num, r["home"], r["away"]),
        "",
        "- **Prediction:** %s wins %s" % (r["winner"], score_str),
        "- **Win prob:** %s %.0f%% | Draw %.0f%% | %s %.0f%%" % (
            r["home"], 100 * r["p_home"], 100 * r["p_draw"],
            r["away"], 100 * r["p_away"]),
        "",
    ]
    return lines


def write_knockout_stage(teams):
    """Generate RoundOf32.md through Final.md deterministically."""
    qualifiers = _get_group_results(teams)
    pairs = _bracket_pairs(qualifiers)
    paths = []

    round_configs = [
        ("RoundOf32", "Round of 32", pairs),
    ]

    # Play Round of 32
    r32_winners = []
    lines = ["# World Cup 2026 — Round of 32 Predictions", "",
             "> Generated by `tools/predict.py`. Knockout mode — every match has a winner.", ""]
    for i, (a, b) in enumerate(pairs, 1):
        r = predict_match(a, b, knockout=True)
        lines.extend(_fmt_knockout_match(i, r))
        winner = a if r["winner"] == a["team"] else b
        r32_winners.append(winner)
    path = os.path.join(DATA, "RoundOf32.md")
    _write(path, "\n".join(lines))
    paths.append(path)

    # Play Round of 16
    r16_pairs = [(r32_winners[i], r32_winners[i + 1]) for i in range(0, len(r32_winners), 2)]
    r16_winners = []
    lines = ["# World Cup 2026 — Round of 16 Predictions", "",
             "> Generated by `tools/predict.py`. Knockout mode.", ""]
    for i, (a, b) in enumerate(r16_pairs, 1):
        r = predict_match(a, b, knockout=True)
        lines.extend(_fmt_knockout_match(i, r))
        winner = a if r["winner"] == a["team"] else b
        r16_winners.append(winner)
    path = os.path.join(DATA, "RoundOf16.md")
    _write(path, "\n".join(lines))
    paths.append(path)

    # Quarterfinals
    qf_pairs = [(r16_winners[i], r16_winners[i + 1]) for i in range(0, len(r16_winners), 2)]
    qf_winners = []
    qf_losers = []
    lines = ["# World Cup 2026 — Quarterfinal Predictions", "",
             "> Generated by `tools/predict.py`. Knockout mode.", ""]
    for i, (a, b) in enumerate(qf_pairs, 1):
        r = predict_match(a, b, knockout=True)
        lines.extend(_fmt_knockout_match(i, r))
        winner = a if r["winner"] == a["team"] else b
        loser = b if r["winner"] == a["team"] else a
        qf_winners.append(winner)
        qf_losers.append(loser)
    path = os.path.join(DATA, "Quarterfinals.md")
    _write(path, "\n".join(lines))
    paths.append(path)

    # Semifinals
    sf_pairs = [(qf_winners[i], qf_winners[i + 1]) for i in range(0, len(qf_winners), 2)]
    sf_winners = []
    sf_losers = []
    lines = ["# World Cup 2026 — Semifinal Predictions", "",
             "> Generated by `tools/predict.py`. Knockout mode.", ""]
    for i, (a, b) in enumerate(sf_pairs, 1):
        r = predict_match(a, b, knockout=True)
        lines.extend(_fmt_knockout_match(i, r))
        winner = a if r["winner"] == a["team"] else b
        loser = b if r["winner"] == a["team"] else a
        sf_winners.append(winner)
        sf_losers.append(loser)
    path = os.path.join(DATA, "Semifinals.md")
    _write(path, "\n".join(lines))
    paths.append(path)

    # Third Place
    a, b = sf_losers[0], sf_losers[1]
    r = predict_match(a, b, knockout=True)
    lines = ["# World Cup 2026 — Third Place Match", "",
             "> Generated by `tools/predict.py`. Knockout mode.", ""]
    lines.extend(_fmt_knockout_match(1, r))
    third_place = a if r["winner"] == a["team"] else b
    lines.append("**Third place:** %s" % third_place["team"])
    path = os.path.join(DATA, "ThirdPlace.md")
    _write(path, "\n".join(lines))
    paths.append(path)

    # Final
    a, b = sf_winners[0], sf_winners[1]
    r = predict_match(a, b, knockout=True)
    lines = ["# World Cup 2026 — Final", "",
             "> Generated by `tools/predict.py`. Knockout mode.", ""]
    lines.extend(_fmt_knockout_match(1, r))
    champion = a if r["winner"] == a["team"] else b
    runner_up = b if r["winner"] == a["team"] else a
    lines.append("---")
    lines.append("")
    lines.append("## Tournament Champion: %s" % champion["team"])
    lines.append("")
    lines.append("**Runner-up:** %s" % runner_up["team"])
    lines.append("")
    lines.append("**Third place:** %s" % third_place["team"])
    path = os.path.join(DATA, "Final.md")
    _write(path, "\n".join(lines))
    paths.append(path)

    return paths


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def cmd_match(teams, spec, knockout):
    if " vs " in spec.lower():
        parts = spec.lower().split(" vs ")
    elif "-" in spec:
        parts = spec.split("-", 1)
    else:
        raise SystemExit('Use: --match "Team A vs Team B"')
    a = teams[resolve_team(teams, parts[0])]
    b = teams[resolve_team(teams, parts[1])]
    r = predict_match(a, b, knockout=knockout)
    print("%s vs %s" % (a["team"], b["team"]))
    print("  Expected goals (lambda): %.2f - %.2f" % (r["lam_a"], r["lam_b"]))
    print("  Win prob: %s %.0f%% | Draw %.0f%% | %s %.0f%%" % (
        a["team"], 100 * r["p_home"], 100 * r["p_draw"],
        b["team"], 100 * r["p_away"]))
    print("  Predicted score: %s %d-%d %s" % (
        a["team"], r["score_a"], r["score_b"], b["team"]))
    print("  Winner: %s%s" % (
        r["winner"], (" (%s)" % r["note"]) if r.get("note") else ""))


def cmd_group(teams, g):
    g = g.upper()
    grp = group_of(teams, g)
    print("Group %s\n" % g)
    table = {t["team"]: dict(team=t, P=0, W=0, D=0, L=0, GF=0, GA=0, Pts=0)
             for t in grp}
    for home, away in round_robin(grp):
        r = predict_match(home, away)
        print("  %-14s %d-%d %-14s  -> %s" % (
            home["team"], r["score_a"], r["score_b"], away["team"], r["winner"]))
        _apply_result(table, home, away, r["score_a"], r["score_b"])
    print("\n  %-14s Pts  GD  GF" % "Team")
    for pos, r in enumerate(_standings_list(table), 1):
        print("  %d. %-12s %3d %+3d %3d" % (
            pos, r["team"]["team"], r["Pts"], r["GD"], r["GF"]))


def main():
    ap = argparse.ArgumentParser(description="World Cup 2026 prediction engine")
    ap.add_argument("--ratings", default=DEFAULT_RATINGS)
    ap.add_argument("--match", help='e.g. "Argentina vs Jamaica"')
    ap.add_argument("--knockout", action="store_true",
                    help="treat --match as a knockout tie (force a winner)")
    ap.add_argument("--group", help="single group letter A-L")
    ap.add_argument("--sim", type=int, metavar="N",
                    help="run N Monte Carlo tournament simulations")
    ap.add_argument("--all", action="store_true",
                    help="regenerate data/GroupStage.md and data/Simulation.md")
    args = ap.parse_args()

    teams = load_ratings(args.ratings)

    if args.match:
        cmd_match(teams, args.match, args.knockout)
    elif args.group:
        cmd_group(teams, args.group)
    elif args.sim:
        for i, r in enumerate(monte_carlo(teams, n=args.sim), 1):
            if r["champ_pct"] < 0.05 and i > 20:
                continue
            print("%2d. %-14s champ %.1f%%  final %.1f%%  SF %.1f%%" % (
                i, r["team"], r["champ_pct"], r["final_pct"], r["sf_pct"]))
    elif args.all:
        p1 = write_group_stage(teams)
        print("wrote", p1)
        p2, _ = write_simulation(teams, n=10000)
        print("wrote", p2)
        for p in write_knockout_stage(teams):
            print("wrote", p)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
