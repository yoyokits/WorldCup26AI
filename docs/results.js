/**
 * Real match results — prediction comparison badges on the RIGHT side.
 * Add new results here as matches are played.
 * Key format: "HomeTeam vs AwayTeam" (must match team-name spans exactly)
 */
var REAL_RESULTS = {
  // June 11
  "Mexico vs South Africa": { home: 2, away: 0 },
  "South Korea vs Czechia": { home: 2, away: 1 },
  // June 12
  "Canada vs Bosnia & Herzegovina": { home: 1, away: 1 },
  "USA vs Paraguay": { home: 4, away: 1 },
  // June 13
  "Switzerland vs Qatar": { home: 1, away: 1 },
  "Brazil vs Morocco": { home: 1, away: 1 },
  "Scotland vs Haiti": { home: 1, away: 0 },
  // June 14
  "Türkiye vs Australia": { home: 0, away: 2 },
  "Germany vs Curaçao": { home: 7, away: 1 },
  "Ecuador vs Ivory Coast": { home: 0, away: 1 },
  "Netherlands vs Japan": { home: 2, away: 2 },
  "Sweden vs Tunisia": { home: 5, away: 1 },
  // June 15
  "Spain vs Cape Verde": { home: 0, away: 0 },
  "Belgium vs Egypt": { home: 1, away: 1 },
  "Iran vs New Zealand": { home: 2, away: 2 },
  "Uruguay vs Saudi Arabia": { home: 1, away: 1 },
  // June 16
  "France vs Senegal": { home: 3, away: 1 },
  "Norway vs Iraq": { home: 0, away: 0 }
};

function getOutcome(h, a) {
  if (h > a) return "home";
  if (a > h) return "away";
  return "draw";
}

function classifyPrediction(predH, predA, realH, realA) {
  if (predH === realH && predA === realA) return { tier: "perfect", pts: 4, cls: "rr-perfect" };
  var predOut = getOutcome(predH, predA);
  var realOut = getOutcome(realH, realA);
  if (predOut === realOut && (predH - predA) === (realH - realA)) return { tier: "winner_gd", pts: 3, cls: "rr-gd" };
  if (predOut === realOut) return { tier: "winner", pts: 2, cls: "rr-winner" };
  return { tier: "miss", pts: 0, cls: "rr-miss" };
}

function parsePredScore(scoreStr) {
  var parts = scoreStr.trim().split("-");
  return { h: parseInt(parts[0], 10), a: parseInt(parts[1], 10) };
}

function injectResultBadges() {
  var icons = { perfect: "⭐", winner_gd: "✅", winner: "🟢", miss: "❌" };
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

    // Replace center score with actual result
    scoreEl.textContent = real.home + "-" + real.away;

    // Add right-side badge showing predicted score + accuracy
    var header = card.querySelector(".match-header");
    if (header) {
      var badge = document.createElement("div");
      badge.className = "rr-right-badge " + c.cls;
      badge.innerHTML =
        '<span class="rr-icon">' + icons[c.tier] + '</span>' +
        '<span class="rr-pred">' + pred.h + ':' + pred.a + '</span>' +
        '<span class="rr-pts">+' + c.pts + '</span>';
      header.appendChild(badge);
    }

    card.setAttribute("data-result-injected", "1");
  });
}

document.addEventListener("DOMContentLoaded", function() {
  injectResultBadges();
  var calMatches = document.getElementById("calendarMatches");
  if (calMatches) {
    var observer = new MutationObserver(function() {
      setTimeout(injectResultBadges, 50);
    });
    observer.observe(calMatches, { childList: true, subtree: true });
  }
});
