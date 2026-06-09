# FIFA World Cup 2026 — Index Page Content
<!-- Feeds: html/index.html -->
<!-- Update: tournament_status, latest_results, and phase after each round -->

---

## meta

```yaml
page_title: "FIFA World Cup 2026 — AI Predictions"
description: "AI-powered predictions for every match of the 48-team FIFA World Cup 2026 (June 11 – July 19)"
last_updated: "2026-06-10"
tournament_status: "Starting Tomorrow"   # update this as tournament progresses
current_phase: "Pre-Tournament"          # Pre-Tournament | Group Stage | R32 | R16 | QF | SF | Final
matches_played: 0
matches_total: 104
```

---

## hero_section

```yaml
title: "FIFA World Cup 2026"
subtitle: "AI Match Predictions — Every Game · Every Score"
tagline: "Powered by Elo + Poisson + Dixon-Coles + Monte Carlo (10,000 simulations)"
dates: "June 11 – July 19, 2026"
hosts: "🇺🇸 USA · 🇲🇽 Mexico · 🇨🇦 Canada"
final_venue: "MetLife Stadium, East Rutherford, New Jersey"
opening_match: "Mexico vs Australia — June 11 at Estadio Azteca, Mexico City"
predicted_champion: "Argentina 🇦🇷"
predicted_final_score: "Argentina 2–1 Germany"
mascots: "Maple (🦌 Canada) · Zayu (🐆 Mexico) · Clutch (🦅 USA)"
official_ball: "Adidas Riva"
```

---

## tournament_facts

```yaml
total_teams: 48
total_groups: 12
total_matches: 104
days_duration: 39
host_nations: 3
venues: 16
defending_champion: "Argentina (2022, Qatar)"
largest_stadium: "AT&T Stadium, Dallas — 94,000"
final_stadium: "MetLife Stadium, NJ — 82,500"
```

---

## phase_banner
<!-- Update this section when phases change -->

```yaml
banner_text: "🏟️ Tournament kicks off tomorrow — June 11, 2026"
next_match:
  id: G-1
  date: "June 11, 2026"
  home: "Mexico"
  away: "Australia"
  venue: "Estadio Azteca, Mexico City"
  prediction: "Mexico 2–1 Australia"
```

---

## top_contenders
<!-- Top 8 from TitleOdds.md — regenerate after each round -->
<!-- Source: data/Website/TitleOdds.md -->

```yaml
- rank: 1
  team: Argentina
  slug: argentina
  group: A
  title_odds: "15.1%"
  note: "Defending champion · Highest Elo (2140)"
- rank: 2
  team: France
  slug: france
  group: D
  title_odds: "10.2%"
  note: "2022 runner-up · Mbappé era"
- rank: 3
  team: Spain
  slug: spain
  group: B
  title_odds: "9.3%"
  note: "Youngest squad · 3 World Cup titles"
- rank: 4
  team: England
  slug: england
  group: H
  title_odds: "7.2%"
  note: "2022 QF · Premier League core"
- rank: 5
  team: Brazil
  slug: brazil
  group: C
  title_odds: "6.6%"
  note: "5× champions · Elo 2050"
- rank: 6
  team: Netherlands
  slug: netherlands
  group: G
  title_odds: "5.5%"
  note: "Van Dijk–Gakpo generation"
- rank: 7
  team: Portugal
  slug: portugal
  group: E
  title_odds: "5.3%"
  note: "Ronaldo's last WC chance"
- rank: 8
  team: Italy
  slug: italy
  group: I
  title_odds: "4.8%"
  note: "Euro 2020 winners · rebuilding"
```

---

## groups_grid
<!-- 12 group cards for the homepage grid -->
<!-- top2_predicted: fill from Standings.md predicted standings -->

```yaml
- group: A
  teams: [Argentina, Morocco, Egypt, Jamaica]
  slugs: [argentina, morocco, egypt, jamaica]
  top2_predicted: [Argentina, Morocco]
  first_match: "Jun 12"

- group: B
  teams: [Spain, Japan, USA, Ghana]
  slugs: [spain, japan, usa, ghana]
  top2_predicted: [Spain, USA]
  first_match: "Jun 12"

- group: C
  teams: [Brazil, South Korea, Switzerland, Cameroon]
  slugs: [brazil, south-korea, switzerland, cameroon]
  top2_predicted: [Brazil, Switzerland]
  first_match: "Jun 13"

- group: D
  teams: [France, Canada, Uruguay, Saudi Arabia]
  slugs: [france, canada, uruguay, saudi-arabia]
  top2_predicted: [France, Uruguay]
  first_match: "Jun 13"

- group: E
  teams: [Portugal, Croatia, Tunisia, Ecuador]
  slugs: [portugal, croatia, tunisia, ecuador]
  top2_predicted: [Portugal, Croatia]
  first_match: "Jun 14"

- group: F
  teams: [Germany, Colombia, Nigeria, Honduras]
  slugs: [germany, colombia, nigeria, honduras]
  top2_predicted: [Germany, Colombia]
  first_match: "Jun 14"

- group: G
  teams: [Netherlands, Serbia, Mexico, Australia]
  slugs: [netherlands, serbia, mexico, australia]
  top2_predicted: [Netherlands, Mexico]
  first_match: "Jun 11 ⭐"
  note: "Opening Day"

- group: H
  teams: [England, Slovenia, Paraguay, Tonga]
  slugs: [england, slovenia, paraguay, tonga]
  top2_predicted: [England, Paraguay]
  first_match: "Jun 15"

- group: I
  teams: [Italy, Wales, Qatar, Fiji]
  slugs: [italy, wales, qatar, fiji]
  top2_predicted: [Italy, Wales]
  first_match: "Jun 15"

- group: J
  teams: [Senegal, Poland, Costa Rica, New Zealand]
  slugs: [senegal, poland, costa-rica, new-zealand]
  top2_predicted: [Senegal, Poland]
  first_match: "Jun 16"

- group: K
  teams: [Iran, Sweden, Panama, Bolivia]
  slugs: [iran, sweden, panama, bolivia]
  top2_predicted: [Iran, Sweden]
  first_match: "Jun 16"

- group: L
  teams: [Ukraine, Turkey, South Africa, Guinea]
  slugs: [ukraine, turkey, south-africa, guinea]
  top2_predicted: [Turkey, Ukraine]
  first_match: "Jun 17"
```

---

## latest_results
<!-- Update this section after each match: add up to 5 most-recent finished matches -->
<!-- Format: id, home, home_score, away_score, away, date, upset (true/false) -->

```yaml
latest_results: []   # empty — tournament has not started
```

---

## upcoming_matches
<!-- Next 5 scheduled matches from Schedule.md — auto-fill from Schedule.md -->

```yaml
- id: G-1
  date: "Jun 11"
  home: Mexico
  home_slug: mexico
  away: Australia
  away_slug: australia
  venue: "Estadio Azteca"
  prediction: "2-1"
  pred_winner: Mexico

- id: G-2
  date: "Jun 11"
  home: Netherlands
  home_slug: netherlands
  away: Serbia
  away_slug: serbia
  venue: "Estadio Akron, Guadalajara"
  prediction: "2-1"
  pred_winner: Netherlands

- id: A-1
  date: "Jun 12"
  home: Argentina
  home_slug: argentina
  away: Morocco
  away_slug: morocco
  venue: "AT&T Stadium, Dallas"
  prediction: "1-0"
  pred_winner: Argentina

- id: A-2
  date: "Jun 12"
  home: Jamaica
  home_slug: jamaica
  away: Egypt
  away_slug: egypt
  venue: "Hard Rock, Miami"
  prediction: "1-2"
  pred_winner: Egypt

- id: B-1
  date: "Jun 12"
  home: Spain
  home_slug: spain
  away: Japan
  away_slug: japan
  venue: "SoFi, Los Angeles"
  prediction: "1-0"
  pred_winner: Spain
```

---

## navigation_links

```yaml
- label: "Group A"
  href: "group_a.html"
  teams: [Argentina, Morocco]
- label: "Group B"
  href: "group_b.html"
  teams: [Spain, USA]
- label: "Group C"
  href: "group_c.html"
  teams: [Brazil, Switzerland]
- label: "Group D"
  href: "group_d.html"
  teams: [France, Uruguay]
- label: "Group E"
  href: "group_e.html"
  teams: [Portugal, Croatia]
- label: "Group F"
  href: "group_f.html"
  teams: [Germany, Colombia]
- label: "Group G"
  href: "group_g.html"
  teams: [Netherlands, Mexico]
- label: "Group H"
  href: "group_h.html"
  teams: [England, Paraguay]
- label: "Group I"
  href: "group_i.html"
  teams: [Italy, Wales]
- label: "Group J"
  href: "group_j.html"
  teams: [Senegal, Poland]
- label: "Group K"
  href: "group_k.html"
  teams: [Iran, Sweden]
- label: "Group L"
  href: "group_l.html"
  teams: [Turkey, Ukraine]
- label: "Knockout Bracket"
  href: "knockout.html"
  teams: []
```

---

## footer

```yaml
credits: "Predictions generated by Elo + Poisson + Dixon-Coles model (tools/predict.py)"
methodology_note: "10,000 Monte Carlo simulations · SEED=2026 · Pure Python stdlib"
disclaimer: "These are statistical predictions, not guaranteed outcomes."
sources:
  - "Dixon & Coles (1997) — Modelling Association Football Scores"
  - "Maher (1982) — Modelling Association Football Goal Scores"
  - "eloratings.net — World Football Elo Ratings"
  - "FIFA.com — Official rankings and tournament info"
github: "https://github.com/yoyokits/WorldCup26AI"
```
