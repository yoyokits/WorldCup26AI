/**
 * Real match results — prediction comparison badges + tracker view.
 * Add new results here as matches are played.
 * Key format: "HomeTeam vs AwayTeam" (must match team-name spans exactly)
 * Fields: home/away = actual score, ph/pa = predicted score, d = date
 */
var REAL_RESULTS = {
  // June 11
  "Mexico vs South Africa":              { home: 2, away: 0, ph: 2, pa: 1, d: "Jun 11" },
  "South Korea vs Czechia":              { home: 2, away: 1, ph: 1, pa: 1, d: "Jun 11" },
  // June 12
  "Canada vs Bosnia & Herzegovina":      { home: 1, away: 1, ph: 2, pa: 1, d: "Jun 12" },
  "USA vs Paraguay":                     { home: 4, away: 1, ph: 2, pa: 1, d: "Jun 12" },
  // June 13
  "Switzerland vs Qatar":                { home: 1, away: 1, ph: 2, pa: 0, d: "Jun 13" },
  "Brazil vs Morocco":                   { home: 1, away: 1, ph: 2, pa: 1, d: "Jun 13" },
  "Scotland vs Haiti":                   { home: 1, away: 0, ph: 2, pa: 0, d: "Jun 13" },
  // June 14
  "Türkiye vs Australia":                { home: 0, away: 2, ph: 2, pa: 1, d: "Jun 14" },
  "Germany vs Curaçao":                  { home: 7, away: 1, ph: 2, pa: 0, d: "Jun 14" },
  "Ecuador vs Ivory Coast":              { home: 0, away: 1, ph: 1, pa: 1, d: "Jun 14" },
  "Netherlands vs Japan":                { home: 2, away: 2, ph: 2, pa: 1, d: "Jun 14" },
  "Sweden vs Tunisia":                   { home: 5, away: 1, ph: 1, pa: 0, d: "Jun 14" },
  // June 15
  "Spain vs Cape Verde":                 { home: 0, away: 0, ph: 2, pa: 0, d: "Jun 15" },
  "Belgium vs Egypt":                    { home: 1, away: 1, ph: 1, pa: 1, d: "Jun 15" },
  "Iran vs New Zealand":                 { home: 2, away: 2, ph: 1, pa: 0, d: "Jun 15" },
  "Uruguay vs Saudi Arabia":             { home: 1, away: 1, ph: 2, pa: 0, d: "Jun 15" },
  // June 16
  "France vs Senegal":                   { home: 3, away: 1, ph: 2, pa: 1, d: "Jun 16" },
  "Norway vs Iraq":                      { home: 0, away: 0, ph: 2, pa: 1, d: "Jun 16" },
  "Argentina vs Algeria":                { home: 3, away: 0, ph: 2, pa: 0, d: "Jun 16" },
  // June 17
  "Portugal vs DR Congo":                { home: 1, away: 1, ph: 2, pa: 0, d: "Jun 17" },
  "Colombia vs Uzbekistan":              { home: 3, away: 1, ph: 2, pa: 0, d: "Jun 17" },
  "Austria vs Jordan":                   { home: 3, away: 1, ph: 2, pa: 0, d: "Jun 17" },
  "England vs Croatia":                  { home: 4, away: 2, ph: 1, pa: 0, d: "Jun 17" },
  "Panama vs Ghana":                     { home: 0, away: 1, ph: 0, pa: 1, d: "Jun 17" },
  // June 18
  "Mexico vs South Korea":               { home: 1, away: 0, ph: 2, pa: 1, d: "Jun 18" },
  "Czechia vs South Africa":             { home: 1, away: 1, ph: 1, pa: 1, d: "Jun 18" },
  "Switzerland vs Bosnia & Herzegovina":  { home: 4, away: 1, ph: 1, pa: 0, d: "Jun 18" },
  "Canada vs Qatar":                     { home: 6, away: 0, ph: 2, pa: 0, d: "Jun 18" },
  // June 19
  "Morocco vs Scotland":                 { home: 1, away: 0, ph: 1, pa: 0, d: "Jun 19" },
  "Brazil vs Haiti":                     { home: 3, away: 0, ph: 2, pa: 0, d: "Jun 19" },
  "USA vs Australia":                    { home: 2, away: 0, ph: 2, pa: 1, d: "Jun 19" },
  "Türkiye vs Paraguay":                 { home: 0, away: 1, ph: 2, pa: 1, d: "Jun 19" },
  // June 20
  "Germany vs Ivory Coast":              { home: 2, away: 1, ph: 2, pa: 1, d: "Jun 20" },
  "Ecuador vs Curaçao":                  { home: 0, away: 0, ph: 2, pa: 0, d: "Jun 20" },
  "Netherlands vs Sweden":               { home: 5, away: 1, ph: 2, pa: 1, d: "Jun 20" },
  "Japan vs Tunisia":                    { home: 4, away: 0, ph: 1, pa: 0, d: "Jun 20" },
  // June 21
  "Belgium vs Iran":                     { home: 0, away: 0, ph: 1, pa: 1, d: "Jun 21" },
  "Egypt vs New Zealand":                { home: 3, away: 1, ph: 2, pa: 0, d: "Jun 21" },
  "Spain vs Saudi Arabia":               { home: 4, away: 0, ph: 2, pa: 0, d: "Jun 21" },
  "Uruguay vs Cape Verde":               { home: 2, away: 2, ph: 2, pa: 0, d: "Jun 21" },
  // June 22
  "France vs Iraq":                      { home: 3, away: 0, ph: 2, pa: 0, d: "Jun 22" },
  "Senegal vs Norway":                   { home: 2, away: 3, ph: 1, pa: 1, d: "Jun 22" },
  "Argentina vs Austria":                { home: 2, away: 0, ph: 2, pa: 0, d: "Jun 22" },
  "Algeria vs Jordan":                   { home: 2, away: 1, ph: 1, pa: 0, d: "Jun 22" },
  // June 23
  "Portugal vs Uzbekistan":              { home: 5, away: 0, ph: 2, pa: 0, d: "Jun 23" },
  "Colombia vs DR Congo":                { home: 1, away: 0, ph: 2, pa: 0, d: "Jun 23" },
  "England vs Ghana":                    { home: 0, away: 0, ph: 2, pa: 0, d: "Jun 23" },
  "Croatia vs Panama":                   { home: 1, away: 0, ph: 1, pa: 0, d: "Jun 23" },
  // June 24
  "Switzerland vs Canada":                { home: 2, away: 1, ph: 1, pa: 0, d: "Jun 24" },
  "Bosnia & Herzegovina vs Qatar":        { home: 3, away: 1, ph: 2, pa: 1, d: "Jun 24" }
};

function getOutcome(h, a) {
  if (h > a) return "home";
  if (a > h) return "away";
  return "draw";
}

function classifyPrediction(predH, predA, realH, realA) {
  if (predH === realH && predA === realA) return { tier: "perfect", pts: 6, cls: "rr-perfect", icon: "⭐", label: "Perfect" };
  var predOut = getOutcome(predH, predA);
  var realOut = getOutcome(realH, realA);
  if (predOut === realOut && (predH - predA) === (realH - realA)) return { tier: "winner_gd", pts: 4, cls: "rr-gd", icon: "✅", label: "Winner+GD" };
  if (predOut === realOut) return { tier: "winner", pts: 2, cls: "rr-winner", icon: "🟢", label: "Winner" };
  return { tier: "miss", pts: 0, cls: "rr-miss", icon: "❌", label: "Miss" };
}

function parsePredScore(scoreStr) {
  var parts = scoreStr.trim().split("-");
  return { h: parseInt(parts[0], 10), a: parseInt(parts[1], 10) };
}

function injectResultBadges() {
  var cards = document.querySelectorAll(".match-card");
  cards.forEach(function(card) {
    if (card.getAttribute("data-result-injected")) return;

    var names = card.querySelectorAll(".team-name");
    if (names.length < 2) return;
    var home = names[0].textContent.trim();
    var away = names[1].textContent.trim();
    var key = home + " vs " + away;
    var real = REAL_RESULTS[key];
    if (!real) return;

    var scoreEl = card.querySelector(".match-score");
    if (!scoreEl) return;
    var pred = parsePredScore(scoreEl.textContent);
    var c = classifyPrediction(pred.h, pred.a, real.home, real.away);

    scoreEl.textContent = real.home + "-" + real.away;

    var header = card.querySelector(".match-header");
    if (header) {
      var badge = document.createElement("div");
      badge.className = "rr-right-badge " + c.cls;
      badge.innerHTML =
        '<span class="rr-icon">' + c.icon + '</span>' +
        '<span class="rr-pred">' + pred.h + ':' + pred.a + '</span>' +
        '<span class="rr-pts">+' + c.pts + '</span>';
      header.appendChild(badge);
    }

    card.setAttribute("data-result-injected", "1");
  });
}

/* ── Prediction Tracker View ── */
function buildPredictionTracker() {
  var container = document.getElementById("predictionTracker");
  if (!container) return;

  var keys = Object.keys(REAL_RESULTS);
  var rows = [];
  var totalPts = 0, maxPts = 0;
  var counts = { perfect: 0, winner_gd: 0, winner: 0, miss: 0 };

  keys.forEach(function(key) {
    var r = REAL_RESULTS[key];
    if (r.ph === undefined) return;
    var c = classifyPrediction(r.ph, r.pa, r.home, r.away);
    totalPts += c.pts;
    maxPts += 6;
    counts[c.tier]++;
    var parts = key.split(" vs ");
    rows.push({ date: r.d, home: parts[0], away: parts[1], pred: r.ph + "-" + r.pa, actual: r.home + "-" + r.away, c: c });
  });

  var matchCount = rows.length;
  var correctOutcomes = counts.perfect + counts.winner_gd + counts.winner;
  var pct = matchCount > 0 ? Math.round((correctOutcomes / matchCount) * 100) : 0;

  var html = '<div class="pt-summary">';
  html += '<div class="pt-stat"><span class="pt-stat-val">' + matchCount + '</span><span class="pt-stat-lbl">Matches</span></div>';
  html += '<div class="pt-stat"><span class="pt-stat-val">' + totalPts + '<span class="pt-stat-max">/' + maxPts + '</span></span><span class="pt-stat-lbl">Points</span></div>';
  html += '<div class="pt-stat"><span class="pt-stat-val">' + pct + '%</span><span class="pt-stat-lbl">Accuracy</span></div>';
  html += '<div class="pt-stat"><span class="pt-stat-val">' + counts.perfect + '</span><span class="pt-stat-lbl">⭐ Perfect</span></div>';
  html += '<div class="pt-stat"><span class="pt-stat-val">' + counts.winner_gd + '</span><span class="pt-stat-lbl">✅ W+GD</span></div>';
  html += '<div class="pt-stat"><span class="pt-stat-val">' + counts.winner + '</span><span class="pt-stat-lbl">🟢 Winner</span></div>';
  html += '<div class="pt-stat"><span class="pt-stat-val">' + counts.miss + '</span><span class="pt-stat-lbl">❌ Miss</span></div>';
  html += '</div>';

  html += '<div class="pt-legend">⭐ Exact score = +6 &nbsp;|&nbsp; ✅ Correct outcome & goal diff = +4 &nbsp;|&nbsp; 🟢 Correct winner = +2 &nbsp;|&nbsp; ❌ Wrong = +0</div>';

  html += '<div class="pt-table-wrap"><table class="pt-table">';
  html += '<thead><tr><th>Date</th><th>Home</th><th>Away</th><th>Pred</th><th>Actual</th><th>Pts</th></tr></thead>';
  html += '<tbody>';

  rows.forEach(function(row) {
    html += '<tr class="pt-row ' + row.c.cls + '">';
    html += '<td class="pt-date">' + row.date + '</td>';
    html += '<td class="pt-team">' + row.home + '</td>';
    html += '<td class="pt-team">' + row.away + '</td>';
    html += '<td class="pt-score">' + row.pred + '</td>';
    html += '<td class="pt-score">' + row.actual + '</td>';
    html += '<td class="pt-pts"><span class="pt-pts-badge ' + row.c.cls + '">' + row.c.icon + ' +' + row.c.pts + '</span></td>';
    html += '</tr>';
  });

  html += '</tbody></table></div>';

  container.innerHTML = html;
}

document.addEventListener("DOMContentLoaded", function() {
  injectResultBadges();
  buildPredictionTracker();
  var calMatches = document.getElementById("calendarMatches");
  if (calMatches) {
    var observer = new MutationObserver(function() {
      setTimeout(injectResultBadges, 50);
    });
    observer.observe(calMatches, { childList: true, subtree: true });
  }
});
