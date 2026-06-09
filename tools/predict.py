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
            teams[row["team"]] = row
    if not teams:
        raise SystemExit("No teams loaded from %s" % path)
    mean_elo = sum(t["elo"] for t in teams.values()) / len(teams)
    for t in teams.values():
        t["mean_elo"] = mean_elo
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

    Attack/defence indices are exponential in the Elo gap to the field mean,
    so stronger sides both score more and concede less. Host nations receive
    a temporary Elo bonus when host_aware is set.
    """
    mean = a["mean_elo"]
    elo_a = a["elo"] + (HOME_ELO_BONUS if (host_aware and a["host"]) else 0.0)
    elo_b = b["elo"] + (HOME_ELO_BONUS if (host_aware and b["host"]) else 0.0)

    atk_a = math.exp(ALPHA * (elo_a - mean) / 100.0)
    atk_b = math.exp(ALPHA * (elo_b - mean) / 100.0)
    def_a = math.exp(-ALPHA * (elo_a - mean) / 100.0)  # weaker -> concede more
    def_b = math.exp(-ALPHA * (elo_b - mean) / 100.0)

    lam_a = BASE_GOALS * atk_a * def_b
    lam_b = BASE_GOALS * atk_b * def_a
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
        # modal outcome, then modal score within that outcome
        outcome = max((("home", ph), ("draw", pd), ("away", pa)),
                      key=lambda kv: kv[1])[0]
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
    # penalties: weight by neutral win expectancy
    pa = 1.0 / (1.0 + 10 ** (-(a["elo"] - b["elo"]) / 400.0))
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
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
