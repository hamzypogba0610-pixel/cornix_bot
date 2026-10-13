FORM_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cornix — Kelly-Bayesian Value Engine</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #0d1117; color: #e6edf3;
    padding: 20px; line-height: 1.5;
  }
  .container { max-width: 520px; margin: 0 auto; }
  h1 { font-size: 22px; margin-bottom: 6px; color: #58a6ff; }
  .sub { font-size: 13px; color: #8b949e; margin-bottom: 22px; }
  .card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 18px; margin-bottom: 16px;
  }
  .card h2 {
    font-size: 14px; color: #58a6ff;
    margin-bottom: 14px; text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .card h3 {
    font-size: 13px; color: #8b949e;
    margin: 14px 0 8px 0; text-transform: uppercase;
    letter-spacing: 0.5px;
    border-top: 1px solid #30363d;
    padding-top: 12px;
  }
  label {
    display: block; font-size: 12px; color: #8b949e;
    margin-bottom: 5px; margin-top: 10px;
  }
  label:first-of-type { margin-top: 0; }
  input, select {
    width: 100%; padding: 10px 12px;
    background: #0d1117; border: 1px solid #30363d;
    border-radius: 6px; color: #e6edf3; font-size: 14px;
  }
  input:focus, select:focus { outline: none; border-color: #58a6ff; }
  .row { display: flex; gap: 10px; }
  .row > div { flex: 1; }
  button {
    width: 100%; padding: 14px;
    background: #238636; color: white; border: none;
    border-radius: 8px; font-size: 15px; font-weight: 600;
    cursor: pointer; margin-top: 8px;
  }
  button:active { background: #1a6e2a; }
  #result { margin-top: 20px; display: none; }
  .badge {
    display: inline-block; padding: 4px 10px;
    border-radius: 12px; font-size: 12px; font-weight: 600;
  }
  .bet { background: #238636; color: white; }
  .nobet { background: #6e7681; color: white; }
  .warn {
    display: inline-block; padding: 2px 8px;
    border-radius: 10px; font-size: 11px; font-weight: 600;
    background: #9e6a03; color: white; margin-left: 6px;
  }
  .market {
    background: #0d1117; border: 1px solid #30363d;
    border-radius: 8px; padding: 12px; margin-bottom: 10px;
  }
  .market-title { font-weight: 600; color: #58a6ff; margin-bottom: 6px; }
  .market-detail { font-size: 13px; color: #8b949e; }
  .market-detail span { color: #e6edf3; }
  .best { border-color: #238636; border-width: 2px; }
  .odds-row {
    margin-top: 10px; padding-top: 10px;
    border-top: 1px solid #30363d;
    display: flex; align-items: center; gap: 10px;
  }
  .odds-row label {
    margin: 0; flex-shrink: 0;
    font-size: 12px; color: #8b949e;
  }
  .odds-row input {
    width: 80px; padding: 6px 8px; font-size: 14px;
  }
  .verdict {
    margin-left: auto; font-size: 13px;
    font-weight: 600; padding: 4px 10px;
    border-radius: 12px;
  }
  .verdict.ok { background: #238636; color: white; }
  .verdict.ko { background: #da3633; color: white; }
  .verdict.none { background: #30363d; color: #8b949e; }
  .analysis {
    margin-top: 12px; padding: 12px;
    background: #0a0d12; border: 1px solid #30363d;
    border-radius: 6px; font-size: 12px;
    display: none;
  }
  .analysis.show { display: block; }
  .analysis-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 6px 12px; color: #8b949e;
  }
  .analysis-grid .k { color: #8b949e; }
  .analysis-grid .v { color: #e6edf3; font-weight: 500; }
  .grade-badge {
    display: inline-block; padding: 4px 12px;
    border-radius: 12px; font-weight: 700;
    font-size: 13px; margin-top: 10px;
  }
  .grade-S { background: #6e40c9; color: white; }
  .grade-A { background: #238636; color: white; }
  .grade-B { background: #1f6feb; color: white; }
  .grade-C { background: #9e6a03; color: white; }
  .grade-D { background: #6e7681; color: white; }
  .kelly-bar {
    margin-top: 8px; height: 6px;
    background: #30363d; border-radius: 3px;
    overflow: hidden;
  }
  .kelly-fill {
    height: 100%; background: #58a6ff;
    transition: width 0.3s;
  }
  .loading {
    text-align: center; padding: 20px;
    color: #8b949e; font-size: 14px;
  }
  .footnote {
    font-size: 11px; color: #6e7681;
    text-align: center; margin-top: 20px;
    line-height: 1.6;
  }
</style>
</head>
<body>
<div class="container">
  <h1>🎯 Cornix</h1>
  <p class="sub">Kelly-Bayesian Value Engine</p>

  <form id="form" onsubmit="submitForm(event)">
    <div class="card">
      <h2>📋 Match</h2>
      <label>Équipe 1 (domicile)</label>
      <input name="home" placeholder="Ex: Liverpool" required>
      <label>Équipe 2 (extérieur)</label>
      <input name="away" placeholder="Ex: Arsenal" required>
      <div class="row">
        <div>
          <label>Championnat</label>
          <select name="league">
            <option value="E0">Premier League</option>
            <option value="SP1">La Liga</option>
            <option value="I1">Serie A</option>
            <option value="D1">Bundesliga</option>
            <option value="F1">Ligue 1</option>
          </select>
        </div>
        <div>
          <label>Date</label>
          <input name="date" type="date" required>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>⚙️ Options</h2>
      <label>Simulations Monte Carlo</label>
      <select name="n_simulations">
        <option value="2000">Rapide (2000)</option>
        <option value="5000" selected>Équilibré (5000)</option>
        <option value="10000">Précis (10000)</option>
      </select>
    </div>

    <button type="submit">🔍 ANALYSER LE MATCH</button>
  </form>

  <div id="result"></div>

  <div class="footnote">
    Kelly-Bayesian Value Engine — fusion bayésienne + dé-marginalisation + Kelly fractionnel (25%)<br>
    Les probabilités calibrées proviennent de 9154 paires d'entraînement (Isotonic).
  </div>
</div>

<script>
const MARGIN_BOOK = 0.03;
const VAR_MODEL = 0.08 * 0.08;
const VAR_MARKET = 0.12 * 0.12;
const KELLY_SAFE = 0.25;

function fmtPct(x) {
  if (x === null || x === undefined || isNaN(x)) return "—";
  return (x * 100).toFixed(1) + "%";
}

function impliedFromOdds(odds) {
  if (!odds || odds <= 1) return null;
  return 1.0 / odds;
}

function fairFromImplied(p_imp) {
  if (p_imp === null) return null;
  return Math.min(0.99, p_imp * (1 - MARGIN_BOOK));
}

function bayesianFusion(p_model, p_market) {
  if (p_model === null || p_market === null) return p_model;
  const w_model = 1.0 / VAR_MODEL;
  const w_market = 1.0 / VAR_MARKET;
  return (w_model * p_model + w_market * p_market) / (w_model + w_market);
}

function kellyFraction(p, odds) {
  if (!odds || odds <= 1) return 0;
  const b = odds - 1;
  const q = 1 - p;
  return (b * p - q) / b;
}

function computeEV(p, odds) {
  if (!p || !odds || odds <= 1) return null;
  return p * odds - 1.0;
}

function gradeValue(ev, kelly, p_post, p_market) {
  if (ev === null || ev <= 0) return "D";
  const strongEdge = p_post - p_market;

  if (ev > 0.10 && kelly > 0.08 && strongEdge > 0.05) return "S";
  if (ev > 0.05 && kelly > 0.04 && strongEdge > 0.03) return "A";
  if (ev > 0.03 && kelly > 0.02) return "B";
  if (ev > 0.01) return "C";
  return "D";
}

function analyze(el, p_model) {
  const input = el.parentElement.querySelector('input');
  const verdict = el.parentElement.querySelector('.verdict');
  const analysis = el.parentElement.querySelector('.analysis');

  const odds = parseFloat(input.value);

  if (!odds || odds <= 1) {
    verdict.textContent = "—";
    verdict.className = "verdict none";
    analysis.classList.remove("show");
    return;
  }

  const p_implied = impliedFromOdds(odds);
  const p_market = fairFromImplied(p_implied);
  const p_post = bayesianFusion(p_model, p_market);
  const ev = computeEV(p_post, odds);
  const kelly_raw = kellyFraction(p_post, odds);
  const kelly = Math.max(0, kelly_raw * KELLY_SAFE);
  const grade = gradeValue(ev, kelly, p_post, p_market);

  if (ev > 0) {
    verdict.textContent = "✅ BET (+" + (ev * 100).toFixed(1) + "%)";
    verdict.className = "verdict ok";
  } else {
    verdict.textContent = "❌ NO BET (" + (ev * 100).toFixed(1) + "%)";
    verdict.className = "verdict ko";
  }

  const kellyPct = (kelly * 100).toFixed(1);
  const barWidth = Math.min(100, kelly * 100 * 4);

  analysis.innerHTML = `
    <div class="analysis-grid">
      <div class="k">Prob implicite book :</div>
      <div class="v">${fmtPct(p_implied)}</div>
      <div class="k">Prob juste (dé-marg.) :</div>
      <div class="v">${fmtPct(p_market)}</div>
      <div class="k">Prob modèle :</div>
      <div class="v">${fmtPct(p_model)}</div>
      <div class="k">Prob postérieure :</div>
      <div class="v">${fmtPct(p_post)}</div>
      <div class="k">Edge bayésien :</div>
      <div class="v">${fmtPct(p_post - p_market)}</div>
      <div class="k">EV postérieur :</div>
      <div class="v">${ev !== null ? (ev * 100).toFixed(2) + "%" : "—"}</div>
      <div class="k">Kelly (sûr 25%) :</div>
      <div class="v">${kellyPct}%</div>
    </div>
    <div class="kelly-bar">
      <div class="kelly-fill" style="width:${barWidth}%"></div>
    </div>
    <div class="grade-badge grade-${grade}">Grade ${grade}</div>
  `;
  analysis.classList.add("show");
}

function marketBlock(title, m, isBest) {
  if (!m) return "";
  const cls = isBest ? "market best" : "market";
  const justOdds = m.prob > 0 ? (1.0 / m.prob).toFixed(2) : "—";

  const isCalibrated = m.sport !== "goals";
  const calibBadge = isCalibrated
    ? ""
    : '<span class="warn">⚠️ non calibré</span>';

  const probLabel = isCalibrated
    ? "Probabilité calibrée"
    : "Probabilité (brute)";

  return `
    <div class="${cls}">
      <div class="market-title">
        ${title} — ${m.market_id}${calibBadge}
      </div>
      <div class="market-detail">
        ${probLabel} : <span>${fmtPct(m.prob)}</span> |
        Cote juste : <span>${justOdds}</span><br>
        Edge modèle : <span>${fmtPct(m.edge)}</span> |
        Robustesse : <span>${fmtPct(m.rob)}</span>
      </div>
      <div class="odds-row">
        <label>Ta cote :</label>
        <input type="number" step="0.01" min="1.01" placeholder="1.20"
               oninput="analyze(this, ${m.prob});">
        <span class="verdict none">—</span>
      </div>
      <div class="analysis"></div>
    </div>
  `;
}

function submitForm(e) {
  e.preventDefault();
  const form = e.target;
  const data = {
    home: form.home.value,
    away: form.away.value,
    league: form.league.value,
    date: form.date.value,
    n_simulations: parseInt(form.n_simulations.value)
  };

  const result = document.getElementById("result");
  result.style.display = "block";
  result.innerHTML = '<div class="loading">⏳ Analyse en cours... (20-40 secondes)</div>';

  fetch("/predict", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  })
  .then(r => r.json())
  .then(d => {
    if (d.detail) {
      result.innerHTML = '<div class="card" style="color:#f85149">Erreur : ' + d.detail + '</div>';
      return;
    }

    const decClass = d.decision === "BET" ? "bet" : "nobet";
    let html = '<div class="card">';
    html += '<h2>' + d.team1 + ' vs ' + d.team2 + '</h2>';
    html += '<div style="margin-bottom:12px"><span class="badge ' + decClass + '">' + d.decision + '</span></div>';
    html += '<div class="market-detail">' + d.reason + '</div>';
    html += '</div>';

    html += '<div class="card"><h2>🎯 Meilleur marché global</h2>';
    html += marketBlock("TOP", d.top, true);
    html += '</div>';

    html += '<div class="card"><h2>🟦 Corners</h2>';
    html += marketBlock("🏠 Équipe 1", d.top_per_family.team1, false);
    html += marketBlock("✈️ Équipe 2", d.top_per_family.team2, false);
    html += marketBlock("🏆 Total", d.top_per_family.total, false);
    html += marketBlock("🎲 Multi Corner", d.top_per_family.multicorner, false);
    html += '</div>';

    html += '<div class="card"><h2>⚽ Buts</h2>';
    html += marketBlock("🎯 1X2", d.top_per_family.result, false);
    html += marketBlock("📊 Over/Under", d.top_per_family.goals_total, false);
    html += marketBlock("⚖️ Handicap", d.top_per_family.handicap, false);

    if (d.goals_outcomes) {
      html += '<h3>Répartition 1X2</h3>';
      html += '<div class="market-detail">';
      html += '🏠 Domicile : <span>' + fmtPct(d.goals_outcomes.home_win) + '</span> | ';
      html += '⚖️ Nul : <span>' + fmtPct(d.goals_outcomes.draw) + '</span> | ';
      html += '✈️ Extérieur : <span>' + fmtPct(d.goals_outcomes.away_win) + '</span>';
      html += '</div>';
    }
    html += '</div>';

    html += '<div class="card"><h2>📈 Technique</h2>';
    html += '<div class="market-detail">';
    html += '<b>Corners</b><br>';
    html += 'λ1 : <span>' + (d.lam1 ? d.lam1.toFixed(2) : "—") + '</span> | ';
    html += 'λ2 : <span>' + (d.lam2 ? d.lam2.toFixed(2) : "—") + '</span><br>';
    html += '<b>Buts</b><br>';
    html += 'λ domicile : <span>' + (d.lam_h_goals ? d.lam_h_goals.toFixed(2) : "—") + '</span> | ';
    html += 'λ extérieur : <span>' + (d.lam_a_goals ? d.lam_a_goals.toFixed(2) : "—") + '</span><br>';
    html += 'MDS : <span>' + (d.dominance.mds ? d.dominance.mds.toFixed(3) : "—") + '</span>';
    html += '</div></div>';

    result.innerHTML = html;
  })
  .catch(err => {
    result.innerHTML = '<div class="card" style="color:#f85149">Erreur réseau : ' + err.message + '</div>';
  });
}

document.querySelector('input[name="date"]').valueAsDate = new Date();
</script>
</body>
</html>
"""
