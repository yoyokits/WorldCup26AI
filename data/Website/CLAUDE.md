# data/Website — Living Data Layer for HTML Generation

## Purpose

This folder is the **single source of truth** for the AI that generates `html/` pages.
Every file here is a "living document" — predictions are pre-filled, real results are
added as matches are played. The AI reads these files and (re)generates HTML to match.

---

## File Map

| File | Feeds HTML | Updates when |
|------|------------|--------------|
| `Schedule.md` | All pages (scores everywhere) | A match result is confirmed |
| `Standings.md` | `group_<a-l>.html` | Any group-stage result |
| `MatchTree.md` | `knockout.html` | A knockout qualifier is known or match played |
| `Teams.md` | `team_<slug>.html`, header flags | Static (ratings; odds update post-sim) |
| `TitleOdds.md` | `index.html` top contenders | After each round (re-sim) |
| `Index.md` | `index.html` | Tournament milestones, latest results |

---

## Status Values (used in Schedule.md and MatchTree.md)

| Value | Meaning | Display |
|-------|---------|---------|
| `scheduled` | Match not yet played | Show prediction score in grey italic |
| `live` | Currently in progress | Show live score with pulsing green dot |
| `finished` | Full-time, result confirmed | Show final score in bold; update standings |
| `tbd` | Teams not yet known (knockout) | Show slot label, e.g. "W-A vs W-B" |

When a match moves from `scheduled` → `finished`:
1. Set `status: finished`
2. Fill `result` field with actual score, e.g. `2-1` (home-away)
3. If the result differs from `prediction`, add `upset: true`
4. For knockout: fill `winner` with the advancing team name

---

## HTML Generation Rules

### General
- Self-contained HTML files (inline CSS; no external framework).
- Flag images: `../images/<slug>.png` (relative to `html/`). Slug is the `slug` column in `Teams.md`.
- Re-generate a page any time any of its source files change.
- Every page has a **Last Updated** timestamp at the footer.

### `html/index.html` ← `Index.md` + `TitleOdds.md` + `Schedule.md` (latest results)
- Hero banner: tournament name, dates, host nations, mascots.
- "Tournament Status" ribbon: shows current phase (Group Stage / R32 / etc.) and match count played/remaining.
- Group grid (A–L): flag + team name for each group, 1st/2nd highlighted when standings are set.
- Top contenders: table from `TitleOdds.md`, top 8 rows.
- Latest results: last 5 finished matches from `Schedule.md`.
- Upcoming matches: next 5 scheduled matches from `Schedule.md`.

### `html/group_<x>.html` ← `Schedule.md` (group section) + `Standings.md` (group section)
- Group header: group letter, flag grid.
- Match list table: date | home flag+name | result/prediction | away flag+name | venue.
  - Finished matches: result bold black.
  - Live matches: pulsing dot + live score in green.
  - Scheduled: prediction score in grey italic with "Pred:" prefix.
- Standings table: live (actual results) with a "Predicted Final" toggle section.

### `html/knockout.html` ← `MatchTree.md`
- Visual bracket: 5 columns (R32 | R16 | QF | SF | Final + 3rd).
- Each match box: flag left team | score | flag right team. If `tbd`: show slot label.
- Winner of each box is highlighted (bold, slight background tint).
- Champion box at the centre-right; predicted champion shown even before Final is played.

### `html/team_<slug>.html` ← `Teams.md` (team row) + `Schedule.md` (team's matches) + `Standings.md`
- Team header: large flag, name, group, confederation badge.
- Stats row: Elo, FIFA rank, title odds %.
- All matches (group + knockout): result or prediction.
- Group standing (current or predicted).

---

## UI Style Guide

```css
/* World Cup 2026 brand palette */
--wc-blue:    #0033A0;   /* Primary brand blue */
--wc-red:     #C8102E;   /* Accent red */
--wc-gold:    #F0A500;   /* Gold / champion highlight */
--wc-white:   #FFFFFF;
--wc-light:   #F4F7FC;   /* Page background */
--wc-grey:    #6B7280;   /* Muted text */
--wc-dark:    #1A1A2E;   /* Dark headings */

/* Typography */
font-family: 'Segoe UI', system-ui, sans-serif;
heading: font-weight 700, letter-spacing -0.02em;
score: font-family monospace, font-weight 700;

/* Flags: always 28×21 px inline (or 40×30 in headers) */
/* Predictions shown in: color #9CA3AF (grey-400), font-style italic */
/* Live scores shown in: color #16A34A (green-600) */
/* Upset badge: background #FEF3C7, color #92400E, text "UPSET" */
```

### Layout patterns
- **Match row:** `[flag] Team Name   [00 – 00]   Team Name [flag]`  
  Score centred, teams right/left-aligned, 120 px min-width for score cell.
- **Standings row:** striped rows; top 2 highlighted with `--wc-blue` left border; 3rd-place border `--wc-gold` if they're a likely best-3rd qualifier.
- **Bracket box:** 200×70 px, rounded corners, team on top half / score on lower half.
- **Mobile:** single-column stack; bracket scrolls horizontally with `overflow-x: auto`.

---

## Update Workflow

When you receive a real result (e.g., "Argentina 2 – Jamaica 0 FT"):

1. Open `Schedule.md` → find the match row by `id` → set `status: finished`, `result: 2-0`.
2. Open `Standings.md` → update the affected group: add W/D/L, GF, GA, recalculate GD and Pts.
3. If a group is now complete → mark the top-2 qualifier slots in `MatchTree.md` with actual team names.
4. If a knockout match is finished → update `MatchTree.md` match row + propagate winner to next round slot.
5. Regenerate affected HTML files (run the generation prompt or edit HTML directly).

---

## Paths Quick Reference

```
data/Website/
├── CLAUDE.md        ← this file
├── Index.md         → html/index.html
├── Schedule.md      → all html/ pages (scores)
├── Standings.md     → html/group_*.html
├── MatchTree.md     → html/knockout.html
├── Teams.md         → html/team_*.html
└── TitleOdds.md     → html/index.html (contenders)

html/
├── images/<slug>.png   ← 48 flag images (already present)
├── index.html
├── group_a.html … group_l.html
├── knockout.html
└── team_<slug>.html  (generated on demand)
```
