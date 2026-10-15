FORM_HTML_PART1 = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cornix — Multi-Corner 360° Ultimate</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #0d1117; color: #e6edf3; padding: 20px; line-height: 1.5; }
  .container { max-width: 520px; margin: 0 auto; }
  h1 { font-size: 22px; margin-bottom: 6px; color: #58a6ff; }
  .sub { font-size: 13px; color: #8b949e; margin-bottom: 22px; }
  .card { background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 18px; margin-bottom: 16px; }
  .card h2 { font-size: 14px; color: #58a6ff; margin-bottom: 14px;
    text-transform: uppercase; letter-spacing: 0.5px; }
  .card h3 { font-size: 13px; color: #8b949e; margin: 14px 0 8px 0;
    text-transform: uppercase; letter-spacing: 0.5px;
    border-top: 1px solid #30363d; padding-top: 12px; }
  label { display: block; font-size: 12px; color: #8b949e;
    margin-bottom: 5px; margin-top: 10px; }
  label:first-of-type { margin-top: 0; }
  input, select, textarea { width: 100%; padding: 10px 12px;
    background: #0d1117; border: 1px solid #30363d;
    border-radius: 6px; color: #e6edf3; font-size: 14px;
    font-family: inherit; }
  input:focus, select:focus, textarea:focus { outline: none;
    border-color: #58a6ff; }
  .row { display: flex; gap: 10px; }
  .row > div { flex: 1; }
  button { width: 100%; padding: 14px; background: #238636; color: white;
    border: none; border-radius: 8px; font-size: 15px; font-weight: 600;
    cursor: pointer; margin-top: 8px; }
  button:active { background: #1a6e2a; }
  button.secondary { background: #1f6feb; }
  button.secondary:active { background: #1552a8; }
  button.tertiary { background: #6e40c9; }
  button.tertiary:active { background: #5a34a8; }
  #result { margin-top: 20px; display: none; }
  .badge { display: inline-block; padding: 4px 10px;
    border-radius: 12px; font-size: 12px; font-weight: 600; }
  .bet { background: #238636; color: white; }
  .nobet { background: #6e7681; color: white; }
  .market { background: #0d1117; border: 1px solid #30363d;
    border-radius: 8px; padding: 12px; margin-bottom: 10px; }
  .market-title { font-weight: 600; color: #58a6ff; margin-bottom: 6px; }
  .market-detail { font-size: 13px; color: #8b949e; }
  .market-detail span { color: #e6edf3; }
  .best { border-color: #238636; border-width: 2px; }
  .odds-row { margin-top: 10px; padding-top: 10px;
    border-top: 1px solid #30363d; display: flex;
    align-items: center; gap: 10px; }
  .odds-row label { margin: 0; flex-shrink: 0;
    font-size: 12px; color: #8b949e; }
  .odds-row input { width: 80px; padding: 6px 8px; font-size: 14px; }
  .verdict { margin-left: auto; font-size: 13px; font-weight: 600;
    padding: 4px 10px; border-radius: 12px; }
  .verdict.ok { background: #238636; color: white; }
  .verdict.ko { background: #da3633; color: white; }
  .verdict.none { background: #30363d; color: #8b949e; }
  .analysis { margin-top: 12px; padding: 12px; background: #0a0d12;
    border: 1px solid #30363d; border-radius: 6px; font-size: 12px;
    display: none; }
  .analysis.show { display: block; }
  .analysis-grid { display: grid; grid-template-columns: 1fr 1fr;
    gap: 6px 12px; color: #8b949e; }
  .analysis-grid .k { color: #8b949e; }
  .analysis-grid .v { color: #e6edf3; font-weight: 500; }
  .grade-badge { display: inline-block; padding: 4px 12px;
    border-radius: 12px; font-weight: 700; font-size: 13px; margin-top: 10px; }
  .grade-S { background: #6e40c9; color: white; }
  .grade-A { background: #238636; color: white; }
  .grade-B { background: #1f6feb; color: white; }
  .grade-C { background: #9e6a03; color: white; }
  .grade-D { background: #6e7681; color: white; }
  .kelly-bar { margin-top: 8px; height: 6px; background: #30363d;
    border-radius: 3px; overflow: hidden; }
  .kelly-fill { height: 100%; background: #58a6ff; transition: width 0.3s; }
  .loading { text-align: center; padding: 20px;
    color: #8b949e; font-size: 14px; }
  .footnote { font-size: 11px; color: #6e7681; text-align: center;
    margin-top: 20px; line-height: 1.6; }
  .portfolio-item { display: flex; align-items: center; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid #21262d; font-size: 13px; }
  .portfolio-item:last-child { border-bottom: none; }
  .portfolio-rank { color: #6e7681; font-weight: 700; width: 22px; }
  .portfolio-name { flex: 1; color: #e6edf3; }
  .portfolio-pct { color: #58a6ff; font-weight: 600; font-family: monospace; }
  .portfolio-pct.zero { color: #6e7681; }
  .portfolio-bar { width: 60px; height: 6px; background: #30363d;
    border-radius: 3px; overflow: hidden; margin-left: 8px; }
  .portfolio-fill { height: 100%;
    background: linear-gradient(90deg, #58a6ff, #1f6feb); }
  .metrics-grid { display: grid; grid-template-columns: 1fr 1fr;
    gap: 8px 12px; margin-top: 12px; padding-top: 12px;
    border-top: 1px solid #21262d; font-size: 13px; }
  .metrics-grid .k { color: #8b949e; }
  .metrics-grid .v { color: #e6edf3; font-weight: 600; }
  .corr-warning { margin-top: 12px; padding: 8px 12px;
    background: #1c1406; border: 1px solid #9e6a03;
    border-radius: 6px; font-size: 12px; color: #d29922; }
  .coherence-warn { margin-top: 8px; padding: 8px 12px;
    background: #2d0f0f; border: 1px solid #da3633;
    border-radius: 6px; font-size: 12px; color: #f85149; }
  .coherence-ok { margin-top: 8px; padding: 8px 12px;
    background: #0d2818; border: 1px solid #238636;
    border-radius: 6px; font-size: 12px; color: #3fb950; }
  details.mc-section { background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 0; margin-bottom: 16px; }
  details.mc-section[open] { padding-bottom: 18px; }
  details.mc-section > summary {
    cursor: pointer; padding: 18px; font-weight: 600;
    color: #58a6ff; font-size: 14px; text-transform: uppercase;
    letter-spacing: 0.5px; list-style: none; outline: none;
    border-radius: 10px; user-select: none; }
  details.mc-section > summary::-webkit-details-marker { display: none; }
  details.mc-section > summary::after { content: ' ▼'; color: #6e7681;
    font-size: 11px; float: right; }
  details.mc-section[open] > summary::after { content: ' ▲'; }
  details.mc-section > *:not(summary) { margin-left: 18px;
    margin-right: 18px; }
  .mc-block { background: #0d1117; border: 1px solid #21262d;
    border-radius: 8px; padding: 12px; margin-bottom: 14px; }
  .mc-block-title { font-size: 13px; color: #e6edf3; font-weight: 600;
    margin-bottom: 10px; }
  .mc-block-title .badge-info { color: #6e7681; font-weight: 400;
    font-size: 11px; margin-left: 6px; }
  .mc-grid-header { display: grid;
    grid-template-columns: 30px 1fr 1fr; gap: 6px;
    font-size: 10px; color: #6e7681; text-transform: uppercase;
    margin-bottom: 4px; padding: 0 4px; }
  .mc-grid-row { display: grid;
    grid-template-columns: 30px 1fr 1fr; gap: 6px; margin-bottom: 4px; }
  .mc-grid-row .mc-idx { font-size: 11px; color: #6e7681;
    text-align: right; padding-top: 8px; }
  .mc-grid-row input { padding: 6px 8px; font-size: 13px;
    text-align: center; }
  .mc-tabs { display: flex; gap: 6px; margin-bottom: 12px; }
  .mc-tab { flex: 1; padding: 8px 12px; background: #0d1117;
    border: 1px solid #30363d; border-radius: 6px;
    font-size: 12px; color: #8b949e; cursor: pointer;
    text-align: center; font-weight: 600; }
  .mc-tab.active { background: #1f6feb; border-color: #1f6feb;
    color: white; }
  .mc-csv-area { width: 100%; min-height: 100px;
    font-family: monospace; font-size: 12px;
    padding: 10px; line-height: 1.6; }
  .mc-hint { font-size: 11px; color: #6e7681; margin-top: 8px;
    line-height: 1.5; }
</style>
</head>
<body>
<div class="container">
  <h1>🎯 Cornix</h1>
  <p class="sub">Multi-Corner 360° Ultimate — Kelly-Bayesian Portfolio Engine</p>

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
  <div id="portfolio-section" style="display:none; margin-top:16px;">
    <button class="secondary" onclick="computePortfolio()">
      🎯 OPTIMISER LE PORTEFEUILLE
    </button>
    <div id="portfolio-result" style="margin-top:16px;"></div>
  </div>

  <details class="mc-section">
    <summary>🎲 Multi-Corner 360° — données mi-temps (optionnel)</summary>
    <p class="mc-hint" style="margin-top:0; margin-bottom:14px;">
      Fournis les corners 1ʳᵉ MT et 2ᵉ MT des derniers matchs.
      Le bot calcule MC1 = A1×A2, MC2 = B1×B2, Global = MC1+MC2
      et génère une distribution par Monte Carlo bivarié.
    </p>
    <div id="mc-forms"></div>
    <button type="button" class="tertiary" onclick="computeMultiCorner()">
      🎲 CALCULER MULTI-CORNER
    </button>
    <div id="mc-result" style="margin-top:14px;"></div>
  </details>

  <div class="footnote">
    Kelly-Bayesian Portfolio Engine — fusion bayésienne + dé-marginalisation + Kelly multi-actifs<br>
    Calibrateurs : corners (9154 paires) et buts (3327 paires) — Isotonic.
  </div>
</div>

<script>
"""
const MARGIN_BOOK = 0.03;
const VAR_MODEL = 0.08 * 0.08;
const VAR_MARKET = 0.12 * 0.12;
const KELLY_SAFE = 0.25;
const MAX_TOTAL_STAKE = 0.30;

let LAST_MARKETS = [];

function fmtPct(x) {
  if (x === null || x === undefined || isNaN(x)) return "—";
  return (x * 100).toFixed(1) + "%";
}

function impliedFromOdds(odds) {
  if (!odds || odds <= 1) return null;
  return 1.0 / odds;
}

function fairFromImplied(p) {
  if (p === null) return null;
  return Math.min(0.99, p * (1 - MARGIN_BOOK));
}

function bayesianFusion(p_model, p_market) {
  if (p_model === null || p_market === null) return p_model;
  const wm = 1.0 / VAR_MODEL;
  const wk = 1.0 / VAR_MARKET;
  return (wm * p_model + wk * p_market) / (wm + wk);
}

function kellyFraction(p, odds) {
  if (!odds || odds <= 1) return 0;
  const b = odds - 1;
  return (b * p - (1 - p)) / b;
}

function computeEV(p, odds) {
  if (!p || !odds || odds <= 1) return null;
  return p * odds - 1.0;
}

function gradeValue(ev, kelly, p_post, p_market) {
  if (ev === null || ev <= 0) return "D";
  const edge = p_post - p_market;
  if (ev > 0.10 && kelly > 0.08 && edge > 0.05) return "S";
  if (ev > 0.05 && kelly > 0.04 && edge > 0.03) return "A";
  if (ev > 0.03 && kelly > 0.02) return "B";
  if (ev > 0.01) return "C";
  return "D";
}

function analyze(el, p_model, marketId, sport, family, line) {
  const market = el.closest('.market');
  const verdict = el.parentElement.querySelector('.verdict');
  const analysis = market ? market.querySelector('.analysis') : null;
  const odds = parseFloat(el.value);

  const entry = LAST_MARKETS.find(x => x.market_id === marketId);
  if (entry) entry.odds = (!odds || odds <= 1) ? null : odds;

  if (!odds || odds <= 1) {
    verdict.textContent = "—";
    verdict.className = "verdict none";
    if (analysis) analysis.classList.remove("show");
    return;
  }

  const p_imp = impliedFromOdds(odds);
  const p_market = fairFromImplied(p_imp);
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

  if (!analysis) return;

  const kellyPct = (kelly * 100).toFixed(1);
  const barWidth = Math.min(100, kelly * 100 * 4);

  analysis.innerHTML = `
    <div class="analysis-grid">
      <div class="k">Prob implicite book :</div>
      <div class="v">${fmtPct(p_imp)}</div>
      <div class="k">Prob juste (dé-marg.) :</div>
      <div class="v">${fmtPct(p_market)}</div>
      <div class="k">Prob modèle :</div>
      <div class="v">${fmtPct(p_model)}</div>
      <div class="k">Prob postérieure :</div>
      <div class="v">${fmtPct(p_post)}</div>
      <div class="k">Edge bayésien :</div>
      <div class="v">${fmtPct(p_post - p_market)}</div>
      <div class="k">EV postérieur :</div>
      <div class="v">${(ev * 100).toFixed(2)}%</div>
      <div class="k">Kelly (sûr 25%) :</div>
      <div class="v">${kellyPct}%</div>
    </div>
    <div class="kelly-bar">
      <div class="kelly-fill" style="width:${barWidth}%"></div>
    </div>
    <div class="grade-badge grade-${grade}">Grade ${grade}</div>
  `;
  analysis.classList.add("show");
  checkCoherence();
}

function checkCoherence() {
  const trio = ['1X2_1', '1X2_X', '1X2_2'];
  const odds = trio.map(id => {
    const m = LAST_MARKETS.find(x => x.market_id === id);
    return m ? m.odds : null;
  });
  if (odds.some(o => !o)) return;

  const sumImplied = odds.reduce((s, o) => s + (1 / o), 0);
  const overround = (sumImplied - 1) * 100;
  const el = document.getElementById('coherence-display');
  if (!el) return;

  if (sumImplied < 1.0) {
    const arbGain = ((1 / sumImplied) - 1) * 100;
    el.innerHTML = `<div class="coherence-warn">🚨 <b>ARBITRAGE DÉTECTÉ</b><br>
      Somme implicite : ${sumImplied.toFixed(4)} (< 1)<br>
      Gain garanti : <b>+${arbGain.toFixed(2)}%</b></div>`;
  } else if (sumImplied > 1.15) {
    el.innerHTML = `<div class="coherence-warn">⚠️ Marge book très élevée sur 1X2 : ${overround.toFixed(1)}%</div>`;
  } else {
    el.innerHTML = `<div class="coherence-ok">✅ Cohérence 1X2 OK — Marge book : ${overround.toFixed(2)}%</div>`;
  }
}

function correlationHeuristic(m1, m2) {
  if (m1.market_id === m2.market_id) return 1.0;
  const id1 = m1.market_id;
  const id2 = m2.market_id;

  if (id1.startsWith('1X2_') && id2.startsWith('1X2_')) return -0.5;

  const parse = (id) => {
    if (id.startsWith('T1_') || id.startsWith('T2_'))
      return { t: id.slice(0, 2), d: id[3], l: id.slice(4) };
    if (id.startsWith('GB_'))
      return { t: 'GOALS', d: id[3], l: id.slice(4) };
    return null;
  };
  const p1 = parse(id1), p2 = parse(id2);
  if (p1 && p2 && p1.t === p2.t && p1.l === p2.l) {
    return p1.d !== p2.d ? -0.95 : 0.98;
  }

  const isC1 = /^(T1_|T2_|TT_|MC_)/.test(id1);
  const isC2 = /^(T1_|T2_|TT_|MC_)/.test(id2);
  const isG1 = /^(GB_|1X2_|HC_)/.test(id1);
  const isG2 = /^(GB_|1X2_|HC_)/.test(id2);
  if ((isC1 && isG2) || (isG1 && isC2)) return 0.30;

  const sameFam = m1.family === m2.family;
  const sameDir = m1.direction === m2.direction;
  if (sameFam && sameDir) return 0.55;
  if (sameFam) return 0.10;
  return 0.05;
}

function matrixInvert(M) {
  const n = M.length;
  const A = M.map((r, i) => [...r, ...Array(n).fill(0).map((_, j) => i === j ? 1 : 0)]);
  for (let i = 0; i < n; i++) {
    let pivot = i;
    for (let j = i + 1; j < n; j++)
      if (Math.abs(A[j][i]) > Math.abs(A[pivot][i])) pivot = j;
    [A[i], A[pivot]] = [A[pivot], A[i]];
    if (Math.abs(A[i][i]) < 1e-12) return null;
    const piv = A[i][i];
    for (let j = 0; j < 2 * n; j++) A[i][j] /= piv;
    for (let k = 0; k < n; k++) {
      if (k === i) continue;
      const f = A[k][i];
      for (let j = 0; j < 2 * n; j++) A[k][j] -= f * A[i][j];
    }
  }
  return A.map(r => r.slice(n));
}

function matrixMulVec(M, v) {
  return M.map(row => row.reduce((s, x, i) => s + x * v[i], 0));
}

function computePortfolio() {
  const box = document.getElementById('portfolio-result');
  const active = LAST_MARKETS.filter(m => m.odds && m.odds > 1);
  if (active.length < 2) {
    box.innerHTML = '<div class="card" style="color:#f85149">Saisis au moins 2 cotes.</div>';
    return;
  }

  const withEV = active.map(m => {
    const p_imp = impliedFromOdds(m.odds);
    const p_market = fairFromImplied(p_imp);
    const p_post = bayesianFusion(m.prob, p_market);
    const ev = computeEV(p_post, m.odds);
    const kelly = Math.max(0, kellyFraction(p_post, m.odds) * KELLY_SAFE);
    return { ...m, p_post, ev, kelly };
  }).sort((a, b) => b.ev - a.ev).slice(0, 10);

  const candidates = withEV.filter(m => m.ev > 0.005);
  if (candidates.length < 2) {
    box.innerHTML = '<div class="card" style="color:#f85149">Pas assez de paris à EV positif.</div>';
    return;
  }

  const n = candidates.length;
  const mu = candidates.map(m => m.ev);
  const Sigma = [];
  for (let i = 0; i < n; i++) {
    const row = [];
    for (let j = 0; j < n; j++) {
      if (i === j) {
        const p = candidates[i].p_post;
        row.push(p * (1 - p));
      } else {
        const p1 = candidates[i].p_post;
        const p2 = candidates[j].p_post;
        const rho = correlationHeuristic(candidates[i], candidates[j]);
        row.push(rho * Math.sqrt(p1 * (1 - p1) * p2 * (1 - p2)));
      }
    }
    Sigma.push(row);
  }

  const SigmaInv = matrixInvert(Sigma);
  if (!SigmaInv) {
    box.innerHTML = '<div class="card" style="color:#f85149">Matrice singulière.</div>';
    return;
  }

  const f_raw = matrixMulVec(SigmaInv, mu);
  let f = f_raw.map(x => Math.max(0, x * KELLY_SAFE));

  const sum = f.reduce((a, b) => a + b, 0);
  if (sum > MAX_TOTAL_STAKE) {
    const scale = MAX_TOTAL_STAKE / sum;
    f = f.map(x => x * scale);
  }

  const pRet = f.reduce((s, x, i) => s + x * mu[i], 0);
  let pVar = 0;
  for (let i = 0; i < n; i++)
    for (let j = 0; j < n; j++)
      pVar += f[i] * f[j] * Sigma[i][j];
  const pStd = Math.sqrt(Math.max(0, pVar));
  const sharpe = pStd > 1e-9 ? pRet / pStd : 0;

  const strongCorr = [];
  for (let i = 0; i < n; i++)
    for (let j = i + 1; j < n; j++) {
      const rho = correlationHeuristic(candidates[i], candidates[j]);
      if (Math.abs(rho) > 0.3)
        strongCorr.push({ a: candidates[i].market_id, b: candidates[j].market_id, rho });
    }

  let html = '<div class="card">';
  html += '<h2>🎯 Portefeuille optimal — Kelly 25%</h2>';
  const sorted = candidates.map((m, i) => ({ ...m, alloc: f[i] }))
    .sort((a, b) => b.alloc - a.alloc);
  const maxA = Math.max(...sorted.map(x => x.alloc), 0.001);

  sorted.forEach((m, idx) => {
    const pct = (m.alloc * 100).toFixed(2);
    const barW = (m.alloc / maxA) * 60;
    const zero = m.alloc < 0.001 ? ' zero' : '';
    html += `
      <div class="portfolio-item">
        <span class="portfolio-rank">${idx + 1}.</span>
        <span class="portfolio-name">${m.market_id}</span>
        <span class="portfolio-pct${zero}">${pct}%</span>
        <span class="portfolio-bar"><span class="portfolio-fill" style="width:${barW}px"></span></span>
      </div>`;
  });

  html += '<div class="metrics-grid">';
  html += `<div class="k">Capital total :</div>
           <div class="v">${(f.reduce((a, b) => a + b, 0) * 100).toFixed(2)}%</div>`;
  html += `<div class="k">Espérance :</div>
           <div class="v">+${(pRet * 100).toFixed(2)}%</div>`;
  html += `<div class="k">Volatilité :</div>
           <div class="v">${(pStd * 100).toFixed(2)}%</div>`;
  html += `<div class="k">Sharpe :</div>
           <div class="v">${sharpe.toFixed(3)}</div>`;
  html += '</div>';

  if (strongCorr.length > 0) {
    html += '<div class="corr-warning">⚠️ <b>Corrélations</b> :<br>';
    strongCorr.forEach(c => {
      html += `&nbsp;&nbsp;${c.a} ↔ ${c.b} (r=${c.rho.toFixed(2)})<br>`;
    });
    html += '</div>';
  }

  html += '</div>';
  box.innerHTML = html;
}

function marketBlock(title, m, isBest) {
  if (!m) return "";
  const cls = isBest ? "market best" : "market";
  const justOdds = m.prob > 0 ? (1.0 / m.prob).toFixed(2) : "—";

  LAST_MARKETS.push({
    market_id: m.market_id,
    family: m.family,
    sport: m.sport,
    direction: m.direction,
    line: m.line,
    prob: m.prob,
    odds: null,
  });

  return `
    <div class="${cls}">
      <div class="market-title">${title} — ${m.market_id}</div>
      <div class="market-detail">
        Probabilité calibrée : <span>${fmtPct(m.prob)}</span> |
        Cote juste : <span>${justOdds}</span><br>
        Edge modèle : <span>${fmtPct(m.edge)}</span> |
        Robustesse : <span>${fmtPct(m.rob)}</span>
      </div>
      <div class="odds-row">
        <label>Ta cote :</label>
        <input type="number" step="0.01" min="1.01" placeholder="1.20"
               oninput="analyze(this, ${m.prob}, '${m.market_id}', '${m.sport}', '${m.family}', ${m.line || 0});">
        <span class="verdict none">—</span>
      </div>
      <div class="analysis"></div>
    </div>`;
}

function submitForm(e) {
  e.preventDefault();
  LAST_MARKETS = [];
  const form = e.target;
  const data = {
    home: form.home.value,
    away: form.away.value,
    league: form.league.value,
    date: form.date.value,
    n_simulations: parseInt(form.n_simulations.value)
  };

  const result = document.getElementById("result");
  document.getElementById("portfolio-section").style.display = "none";
  document.getElementById("portfolio-result").innerHTML = "";
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
    html += '<div id="coherence-display" style="margin-top:12px;"></div>';
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
    html += 'λ dom : <span>' + (d.lam_h_goals ? d.lam_h_goals.toFixed(2) : "—") + '</span> | ';
    html += 'λ ext : <span>' + (d.lam_a_goals ? d.lam_a_goals.toFixed(2) : "—") + '</span><br>';
    html += 'MDS : <span>' + (d.dominance.mds ? d.dominance.mds.toFixed(3) : "—") + '</span>';
    html += '</div></div>';

    result.innerHTML = html;
    document.getElementById("portfolio-section").style.display = "block";
  })
  .catch(err => {
    result.innerHTML = '<div class="card" style="color:#f85149">Erreur réseau : ' + err.message + '</div>';
  });
}

document.querySelector('input[name="date"]').valueAsDate = new Date();


/* =========================================================
   MULTI-CORNER 360° ULTIMATE
   ========================================================= */
const MC_BLOCKS = [
  { id: 'mc1d', label: '🏠 Éq1 — 10 matchs à DOMICILE', team: 1, n: 10 },
  { id: 'mc1g', label: '🏠 Éq1 — 5 matchs GLOBAUX',     team: 1, n: 5  },
  { id: 'mc2e', label: '✈️ Éq2 — 10 matchs à l\'EXTÉRIEUR', team: 2, n: 10 },
  { id: 'mc2g', label: '✈️ Éq2 — 5 matchs GLOBAUX',     team: 2, n: 5  },
];

let MC_DATA = {};

function generateMCForms() {
  const container = document.getElementById('mc-forms');
  if (!container) return;
  let html = '';
  MC_BLOCKS.forEach(block => {
    html += `<div class="mc-block" data-block="${block.id}">`;
    html += `<div class="mc-block-title">${block.label} <span class="badge-info">(${block.n} matchs)</span></div>`;
    html += `<div class="mc-tabs">`;
    html += `<div class="mc-tab active" data-tab="grid" onclick="switchMCTab('${block.id}', 'grid')">📋 Grille</div>`;
    html += `<div class="mc-tab" data-tab="csv" onclick="switchMCTab('${block.id}', 'csv')">📝 CSV</div>`;
    html += `</div>`;
    html += `<div class="mc-grid-view" data-view="grid">`;
    html += `<div class="mc-grid-header"><span>#</span><span>1ʳᵉ MT</span><span>2ᵉ MT</span></div>`;
    for (let i = 0; i < block.n; i++) {
      html += `<div class="mc-grid-row">`;
      html += `<span class="mc-idx">${i + 1}</span>`;
      html += `<input type="number" min="0" max="20" step="1" data-block="${block.id}" data-idx="${i}" data-half="1" placeholder="0">`;
      html += `<input type="number" min="0" max="20" step="1" data-block="${block.id}" data-idx="${i}" data-half="2" placeholder="0">`;
      html += `</div>`;
    }
    html += `</div>`;
    html += `<div class="mc-csv-view" data-view="csv" style="display:none;">`;
    html += `<textarea class="mc-csv-area" data-block="${block.id}" placeholder="Format : 1ʳᵉ MT, 2ᵉ MT (une ligne par match)"></textarea>`;
    html += `<div class="mc-hint">Une ligne = un match. Format : A1, A2</div>`;
    html += `</div>`;
    html += `</div>`;
  });
  container.innerHTML = html;
}

function switchMCTab(blockId, tab) {
  const block = document.querySelector(`[data-block="${blockId}"]`);
  if (!block) return;
  block.querySelectorAll('.mc-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === tab);
  });
  block.querySelectorAll('[data-view]').forEach(v => {
    v.style.display = (v.dataset.view === tab) ? '' : 'none';
  });
}

function parseMCCSV(blockId) {
  const ta = document.querySelector(`textarea[data-block="${blockId}"]`);
  if (!ta || !ta.value.trim()) return [];
  const pairs = [];
  ta.value.trim().split('\n').forEach(line => {
    const parts = line.split(/[,\t;]+/).map(s => parseFloat(s.trim()));
    if (parts.length >= 2 && !isNaN(parts[0]) && !isNaN(parts[1]) && parts[0] >= 0 && parts[1] >= 0) {
      pairs.push([Math.round(parts[0]), Math.round(parts[1])]);
    }
  });
  return pairs;
}

function getMCData() {
  const data = {};
  MC_BLOCKS.forEach(block => {
    const gridView = document.querySelector(`[data-block="${block.id}"] [data-view="grid"]`);
    const gridVisible = gridView && gridView.style.display !== 'none';

    let pairs = [];
    if (gridVisible) {
      const inputs1 = document.querySelectorAll(`input[data-block="${block.id}"][data-half="1"]`);
      const inputs2 = document.querySelectorAll(`input[data-block="${block.id}"][data-half="2"]`);
      for (let i = 0; i < inputs1.length; i++) {
        const v1 = parseFloat(inputs1[i].value);
        const v2 = parseFloat(inputs2[i].value);
        if (!isNaN(v1) && !isNaN(v2) && v1 >= 0 && v2 >= 0) {
          pairs.push([Math.round(v1), Math.round(v2)]);
        }
      }
    } else {
      pairs = parseMCCSV(block.id);
    }

    data[block.id] = { block, pairs };
  });
  return data;
}

/* --- Statistiques descriptives --- */
function computeStats(pairs) {
  if (!pairs || pairs.length === 0) return null;
  const A1 = pairs.map(p => p[0]);
  const A2 = pairs.map(p => p[1]);
  const n = pairs.length;
  const mean1 = A1.reduce((a, b) => a + b, 0) / n;
  const mean2 = A2.reduce((a, b) => a + b, 0) / n;
  const var1 = A1.reduce((s, v) => s + (v - mean1) ** 2, 0) / Math.max(1, n - 1);
  const var2 = A2.reduce((s, v) => s + (v - mean2) ** 2, 0) / Math.max(1, n - 1);
  const std1 = Math.sqrt(var1);
  const std2 = Math.sqrt(var2);
  let cov = 0;
  for (let i = 0; i < n; i++) cov += (A1[i] - mean1) * (A2[i] - mean2);
  cov = cov / Math.max(1, n - 1);
  const rho = (std1 > 1e-9 && std2 > 1e-9) ? cov / (std1 * std2) : 0;

  const products = pairs.map(p => p[0] * p[1]);
  const zeroCount = products.filter(x => x === 0).length;

  const sorted = [...products].sort((a, b) => a - b);
  const p10 = sorted[Math.floor(0.10 * n)];
  const p50 = sorted[Math.floor(0.50 * n)];
  const p90 = sorted[Math.min(n - 1, Math.floor(0.90 * n))];

  return {
    n, mean1, mean2, std1, std2, rho, zeroCount,
    meanProduct: products.reduce((a, b) => a + b, 0) / n,
    p10, p50, p90,
  };
}

/* --- Monte Carlo bivarié (copule gaussienne) --- */
function simulateBivariate(mean1, mean2, std1, std2, rho, nSims, seed) {
  const samples = [];
  const s1 = Math.max(std1, 0.5);
  const s2 = Math.max(std2, 0.5);
  let s = seed || 12345;
  const rand = () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
  const randn = () => {
    const u1 = Math.max(1e-9, rand());
    const u2 = rand();
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  };
  const rho_c = Math.max(-0.95, Math.min(0.95, rho));
  const a = Math.sqrt(1 - rho_c * rho_c);
  for (let i = 0; i < nSims; i++) {
    const z1 = randn();
    const z2 = rho_c * z1 + a * randn();
    let a1 = Math.round(mean1 + s1 * z1);
    let a2 = Math.round(mean2 + s2 * z2);
    if (a1 < 0) a1 = 0;
    if (a2 < 0) a2 = 0;
    samples.push(a1 * a2);
  }
  return samples;
}

/* --- Probabilités Over/Under --- */
function mcProbabilities(samples) {
  const sorted = [...samples].sort((a, b) => a - b);
  const n = sorted.length;
  const mean = samples.reduce((a, b) => a + b, 0) / n;
  const p10 = sorted[Math.floor(0.10 * n)];
  const p50 = sorted[Math.floor(0.50 * n)];
  const p90 = sorted[Math.min(n - 1, Math.floor(0.90 * n))];

  const lines = [5.5, 10.5, 15.5, 20.5, 25.5, 30.5, 35.5, 40.5];
  const probs = {};
  lines.forEach(L => {
    const threshold = Math.floor(L + 0.5);
    const over = samples.filter(x => x >= threshold).length / n;
    probs[L] = { over, under: 1 - over };
  });

  return { mean, p10, p50, p90, probs };
}

/* --- Affichage résultat MC --- */
function renderMCBlock(title, samples, teamSide) {
  const stats = mcProbabilities(samples);
  let html = `<div class="mc-result-item" data-mc="${teamSide}">`;
  html += `<div class="mc-result-title">${title}</div>`;
  html += `<div class="mc-result-detail">`;
  html += `Moyenne : <span>${stats.mean.toFixed(2)}</span> | `;
  html += `Médiane : <span>${stats.p50}</span><br>`;
  html += `P10 : <span>${stats.p10}</span> | P90 : <span>${stats.p90}</span>`;
  html += `</div>`;

  html += `<div class="mc-dist-bar"><div class="mc-dist-fill" style="width:100%"></div></div>`;
  html += `<div class="mc-dist-labels"><span>${stats.p10}</span><span>${stats.p50}</span><span>${stats.p90}</span></div>`;

  html += `<div style="margin-top:10px; font-size:12px; color:#8b949e;">`;
  html += `<b>Probabilités Over :</b><br>`;
  [5.5, 10.5, 15.5, 20.5, 25.5, 30.5, 35.5].forEach(L => {
    const p = stats.probs[L];
    if (p) {
      html += `Over ${L} : <span style="color:#58a6ff">${(p.over * 100).toFixed(1)}%</span> | `;
      html += `Under ${L} : <span style="color:#8b949e">${(p.under * 100).toFixed(1)}%</span><br>`;
    }
  });
  html += `</div>`;

  const mid = `MC_${teamSide}`;
  const pOver = stats.probs[20.5] ? stats.probs[20.5].over : 0.5;
  const pUnder = 1 - pOver;
  const best = pOver >= pUnder
    ? { dir: 'over', p: pOver, line: 20.5 }
    : { dir: 'under', p: pUnder, line: 20.5 };

  html += `<div class="odds-row" style="margin-top:10px; border-top:1px solid #30363d; padding-top:10px;">`;
  html += `<label>Cote ${best.dir.toUpperCase()} ${best.line} :</label>`;
  html += `<input type="number" step="0.01" min="1.01" placeholder="1.50" `;
  html += `oninput="analyzeMC(this, '${mid}', ${best.p});">`;
  html += `<span class="verdict none">—</span>`;
  html += `</div>`;
  html += `<div class="analysis"></div>`;

  html += `</div>`;
  return html;
}

function analyzeMC(el, marketId, prob) {
  const parent = el.closest('.mc-result-item');
  const verdict = el.parentElement.querySelector('.verdict');
  const analysis = parent.querySelector('.analysis');
  const odds = parseFloat(el.value);

  const entry = LAST_MARKETS.find(x => x.market_id === marketId);
  if (!entry) {
    LAST_MARKETS.push({
      market_id: marketId,
      family: 'multicorner',
      sport: 'corners',
      direction: 'over',
      line: 20.5,
      prob: prob,
      odds: null,
    });
  } else {
    entry.prob = prob;
    entry.odds = (!odds || odds <= 1) ? null : odds;
  }

  if (!odds || odds <= 1) {
    verdict.textContent = "—";
    verdict.className = "verdict none";
    if (analysis) analysis.classList.remove("show");
    return;
  }

  const p_imp = impliedFromOdds(odds);
  const p_market = fairFromImplied(p_imp);
  const p_post = bayesianFusion(prob, p_market);
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

  if (!analysis) return;
  analysis.innerHTML = `
    <div class="analysis-grid">
      <div class="k">Prob implicite :</div>
      <div class="v">${fmtPct(p_imp)}</div>
      <div class="k">Prob juste :</div>
      <div class="v">${fmtPct(p_market)}</div>
      <div class="k">Prob modèle :</div>
      <div class="v">${fmtPct(prob)}</div>
      <div class="k">Prob postérieure :</div>
      <div class="v">${fmtPct(p_post)}</div>
      <div class="k">Edge bayésien :</div>
      <div class="v">${fmtPct(p_post - p_market)}</div>
      <div class="k">EV :</div>
      <div class="v">${(ev * 100).toFixed(2)}%</div>
      <div class="k">Kelly :</div>
      <div class="v">${(kelly * 100).toFixed(1)}%</div>
    </div>
    <div class="grade-badge grade-${grade}">Grade ${grade}</div>
  `;
  analysis.classList.add("show");
}

/* --- Fonction principale --- */
function computeMultiCorner() {
  const box = document.getElementById('mc-result');
  const data = getMCData();

  const hasE1 = data['mc1d'].pairs.length >= 3 || data['mc1g'].pairs.length >= 3;
  const hasE2 = data['mc2e'].pairs.length >= 3 || data['mc2g'].pairs.length >= 3;

  if (!hasE1 || !hasE2) {
    box.innerHTML = '<div class="card" style="color:#f85149">Remplis au moins 3 matchs pour chaque équipe.</div>';
    return;
  }

  const s1d = computeStats(data['mc1d'].pairs);
  const s1g = computeStats(data['mc1g'].pairs);
  const s2e = computeStats(data['mc2e'].pairs);
  const s2g = computeStats(data['mc2g'].pairs);

  const stats1 = s1d || s1g;
  const stats2 = s2e || s2g;
  const n1 = data['mc1d'].pairs.length || data['mc1g'].pairs.length;
  const n2 = data['mc2e'].pairs.length || data['mc2g'].pairs.length;

  let coherenceWarn = '';
  if (s1d && s1g && Math.abs(s1d.meanProduct - s1g.meanProduct) / Math.max(1, s1g.meanProduct) > 0.30) {
    coherenceWarn += `<div class="corr-warning">⚠️ Éq1 : écart > 30% entre domicile (${s1d.meanProduct.toFixed(1)}) et global (${s1g.meanProduct.toFixed(1)})</div>`;
  }
  if (s2e && s2g && Math.abs(s2e.meanProduct - s2g.meanProduct) / Math.max(1, s2g.meanProduct) > 0.30) {
    coherenceWarn += `<div class="corr-warning">⚠️ Éq2 : écart > 30% entre extérieur (${s2e.meanProduct.toFixed(1)}) et global (${s2g.meanProduct.toFixed(1)})</div>`;
  }

  const N_SIMS = 10000;
  const mc1 = simulateBivariate(stats1.mean1, stats1.mean2, stats1.std1, stats1.std2, stats1.rho, N_SIMS, 42);
  const mc2 = simulateBivariate(stats2.mean1, stats2.mean2, stats2.std1, stats2.std2, stats2.rho, N_SIMS, 43);
  const mcGlobal = mc1.map((v, i) => v + mc2[i]);

  let html = '<div class="card">';
  html += '<h2>🎲 Résultats Multi-Corner</h2>';
  html += `<div class="mc-result-detail" style="margin-bottom:12px;">`;
  html += `Éq1 : ${n1} matchs (ρ=${stats1.rho.toFixed(2)}, P(0)=${(stats1.zeroCount / stats1.n * 100).toFixed(0)}%)<br>`;
  html += `Éq2 : ${n2} matchs (ρ=${stats2.rho.toFixed(2)}, P(0)=${(stats2.zeroCount / stats2.n * 100).toFixed(0)}%)`;
  html += `</div>`;
  if (coherenceWarn) html += coherenceWarn;
  html += renderMCBlock('🏠 MC Équipe 1 = A1 × A2', mc1, 'T1');
  html += renderMCBlock('✈️ MC Équipe 2 = B1 × B2', mc2, 'T2');
  html += renderMCBlock('🌍 MC Global = MC1 + MC2', mcGlobal, 'GLOBAL');
  html += '</div>';

  box.innerHTML = html;
}

/* --- Initialisation --- */
generateMCForms();
</script>
</body>
</html>
"""


FORM_HTML = FORM_HTML_PART1 + FORM_HTML_PART2
