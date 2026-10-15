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
