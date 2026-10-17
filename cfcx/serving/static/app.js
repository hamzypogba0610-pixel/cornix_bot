const MARGIN_BOOK = 0.03;
const VAR_MODEL = 0.08 * 0.08;
const VAR_MARKET = 0.12 * 0.12;
const KELLY_SAFE = 0.25;
const MAX_TOTAL_STAKE = 0.30;
const BOOK_KEY = 'cornix_book_v1';
const H2H_KEY = 'cornix_h2h_v1';
const SHADOW_KEY = 'cornix_shadow_v1';
const H2H_COUNT = 5;

let LAST_MARKETS = [];
let ORACLE_RESULTS = [];

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

function getField(name) {
  return document.querySelector('input[name="' + name + '"]');
}

function sigmoid(x) {
  return 1 / (1 + Math.exp(-Math.max(-50, Math.min(50, x))));
}

function logit(p) {
  const eps = 1e-9;
  const pc = Math.max(eps, Math.min(1 - eps, p));
  return Math.log(pc / (1 - pc));
}

function matrixInvert(M) {
  const n = M.length;
  const A = M.map((r, i) => r.concat(Array(n).fill(0).map((_, j) => i === j ? 1 : 0)));
  for (let i = 0; i < n; i++) {
    let pivot = i;
    for (let j = i + 1; j < n; j++)
      if (Math.abs(A[j][i]) > Math.abs(A[pivot][i])) pivot = j;
    const tmp = A[i]; A[i] = A[pivot]; A[pivot] = tmp;
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
    verdict.textContent = "BET (+" + (ev * 100).toFixed(1) + "%)";
    verdict.className = "verdict ok";
  } else {
    verdict.textContent = "NO BET (" + (ev * 100).toFixed(1) + "%)";
    verdict.className = "verdict ko";
  }

  if (!analysis) return;

  const kellyPct = (kelly * 100).toFixed(1);
  const barWidth = Math.min(100, kelly * 100 * 4);

  analysis.innerHTML = '<div class="analysis-grid">' +
    '<div class="k">Prob implicite book :</div><div class="v">' + fmtPct(p_imp) + '</div>' +
    '<div class="k">Prob juste (de-marg.) :</div><div class="v">' + fmtPct(p_market) + '</div>' +
    '<div class="k">Prob modele :</div><div class="v">' + fmtPct(p_model) + '</div>' +
    '<div class="k">Prob posterieure :</div><div class="v">' + fmtPct(p_post) + '</div>' +
    '<div class="k">Edge bayesien :</div><div class="v">' + fmtPct(p_post - p_market) + '</div>' +
    '<div class="k">EV posterieur :</div><div class="v">' + (ev * 100).toFixed(2) + '%</div>' +
    '<div class="k">Kelly (sur 25%) :</div><div class="v">' + kellyPct + '%</div>' +
    '</div>' +
    '<div class="kelly-bar"><div class="kelly-fill" style="width:' + barWidth + '%"></div></div>' +
    '<div class="grade-badge grade-' + grade + '">Grade ' + grade + '</div>';
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
    el.innerHTML = '<div class="coherence-warn"><b>ARBITRAGE DETECTE</b><br>' +
      'Somme implicite : ' + sumImplied.toFixed(4) + ' (< 1)<br>' +
      'Gain garanti : <b>+' + arbGain.toFixed(2) + '%</b></div>';
  } else if (sumImplied > 1.15) {
    el.innerHTML = '<div class="coherence-warn">Marge book tres elevee sur 1X2 : ' + overround.toFixed(1) + '%</div>';
  } else {
    el.innerHTML = '<div class="coherence-ok">Coherence 1X2 OK — Marge book : ' + overround.toFixed(2) + '%</div>';
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
    return Object.assign({}, m, { p_post: p_post, ev: ev, kelly: kelly });
  }).sort((a, b) => b.ev - a.ev).slice(0, 10);

  const candidates = withEV.filter(m => m.ev > 0.005);
  if (candidates.length < 2) {
    box.innerHTML = '<div class="card" style="color:#f85149">Pas assez de paris a EV positif.</div>';
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
    box.innerHTML = '<div class="card" style="color:#f85149">Matrice singuliere.</div>';
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
        strongCorr.push({ a: candidates[i].market_id, b: candidates[j].market_id, rho: rho });
    }

  let html = '<div class="card">';
  html += '<h2>Portefeuille optimal — Kelly 25%</h2>';
  const sorted = candidates.map((m, i) => Object.assign({}, m, { alloc: f[i] }))
    .sort((a, b) => b.alloc - a.alloc);
  const maxA = Math.max.apply(null, sorted.map(x => x.alloc).concat([0.001]));

  sorted.forEach((m, idx) => {
    const pct = (m.alloc * 100).toFixed(2);
    const barW = (m.alloc / maxA) * 60;
    const zero = m.alloc < 0.001 ? ' zero' : '';
    html += '<div class="portfolio-item">' +
      '<span class="portfolio-rank">' + (idx + 1) + '.</span>' +
      '<span class="portfolio-name">' + m.market_id + '</span>' +
      '<span class="portfolio-pct' + zero + '">' + pct + '%</span>' +
      '<span class="portfolio-bar"><span class="portfolio-fill" style="width:' + barW + 'px"></span></span>' +
      '</div>';
  });

  html += '<div class="metrics-grid">';
  html += '<div class="k">Capital total :</div><div class="v">' +
    (f.reduce((a, b) => a + b, 0) * 100).toFixed(2) + '%</div>';
  html += '<div class="k">Esperance :</div><div class="v">+' +
    (pRet * 100).toFixed(2) + '%</div>';
  html += '<div class="k">Volatilite :</div><div class="v">' +
    (pStd * 100).toFixed(2) + '%</div>';
  html += '<div class="k">Sharpe :</div><div class="v">' +
    sharpe.toFixed(3) + '</div>';
  html += '</div>';

  if (strongCorr.length > 0) {
    html += '<div class="corr-warning">Correlations :<br>';
    strongCorr.forEach(c => {
      html += '&nbsp;&nbsp;' + c.a + ' / ' + c.b + ' (r=' + c.rho.toFixed(2) + ')<br>';
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
    odds: null
  });

  return '<div class="' + cls + '">' +
    '<div class="market-title">' + title + ' — ' + m.market_id + '</div>' +
    '<div class="market-detail">' +
      'Probabilite calibree : <span>' + fmtPct(m.prob) + '</span> | ' +
      'Cote juste : <span>' + justOdds + '</span><br>' +
      'Edge modele : <span>' + fmtPct(m.edge) + '</span> | ' +
      'Robustesse : <span>' + fmtPct(m.rob) + '</span>' +
    '</div>' +
    '<div class="odds-row">' +
      '<label>Ta cote :</label>' +
      '<input type="number" step="0.01" min="1.01" placeholder="1.20" ' +
        'oninput="analyze(this, ' + m.prob + ', \'' + m.market_id + '\', \'' + m.sport + '\', \'' + m.family + '\', ' + (m.line || 0) + ');">' +
      '<span class="verdict none">—</span>' +
    '</div>' +
    '<div class="analysis"></div>' +
    '</div>';
}

function saveBookInfo() {
  const save = document.getElementById('save_book');
  if (!save || !save.checked) return;
  const data = {};
  ['line_team1','line_team2','line_total','line_goals','line_handicap','odds_1','odds_x','odds_2'].forEach(k => {
    const f = getField(k);
    if (f) data[k] = f.value;
  });
  try { localStorage.setItem(BOOK_KEY, JSON.stringify(data)); } catch (e) {}
}

function loadBookInfo() {
  try {
    const raw = localStorage.getItem(BOOK_KEY);
    if (!raw) return;
    const data = JSON.parse(raw);
    Object.keys(data).forEach(k => {
      const f = getField(k);
      if (f && data[k]) f.value = data[k];
    });
  } catch (e) {}
}

function generateH2HGrid() {
  const body = document.getElementById('h2h-grid-body');
  if (!body) return;
  let html = '';
  for (let i = 0; i < H2H_COUNT; i++) {
    html += '<div class="h2h-row">';
    html += '<div class="h2h-idx">#' + (i + 1) + '</div>';
    html += '<input type="number" min="0" max="20" step="1" data-h2h="' + i + '" data-f="c1mt_1" placeholder="0">';
    html += '<input type="number" min="0" max="20" step="1" data-h2h="' + i + '" data-f="c1mt_2" placeholder="0">';
    html += '<input type="number" min="0" max="20" step="1" data-h2h="' + i + '" data-f="c2mt_1" placeholder="0">';
    html += '<input type="number" min="0" max="20" step="1" data-h2h="' + i + '" data-f="c2mt_2" placeholder="0">';
    html += '<input type="number" min="0" max="5" step="1" data-h2h="' + i + '" data-f="b1mt_1" placeholder="0">';
    html += '<input type="number" min="0" max="5" step="1" data-h2h="' + i + '" data-f="b1mt_2" placeholder="0">';
    html += '<input type="number" min="0" max="5" step="1" data-h2h="' + i + '" data-f="b2mt_1" placeholder="0">';
    html += '<input type="number" min="0" max="5" step="1" data-h2h="' + i + '" data-f="b2mt_2" placeholder="0">';
    html += '</div>';
  }
  body.innerHTML = html;
}

function switchH2HTab(tab) {
  const gridView = document.getElementById('h2h-grid-view');
  const csvView = document.getElementById('h2h-csv-view');
  const tabs = document.querySelectorAll('#h2h-section .mc-tab');
  tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  if (tab === 'grid') {
    gridView.style.display = '';
    csvView.style.display = 'none';
  } else {
    gridView.style.display = 'none';
    csvView.style.display = '';
  }
}

function collectH2H() {
  const gridView = document.getElementById('h2h-grid-view');
  const gridVisible = gridView && gridView.style.display !== 'none';
  const matches = [];

  if (gridVisible) {
    for (let i = 0; i < H2H_COUNT; i++) {
      const inputs = document.querySelectorAll('input[data-h2h="' + i + '"]');
      const row = {};
      inputs.forEach(inp => {
        const v = parseInt(inp.value);
        if (!isNaN(v) && v >= 0) row[inp.dataset.f] = v;
      });
      if (Object.keys(row).length === 8) matches.push(row);
    }
  } else {
    const ta = document.getElementById('h2h-csv');
    if (ta && ta.value.trim()) {
      ta.value.trim().split('\n').forEach(line => {
        const parts = line.split(/[,\t;]+/).map(s => parseFloat(s.trim()));
        if (parts.length >= 8 && parts.every(p => !isNaN(p) && p >= 0)) {
          matches.push({
            c1mt_1: Math.round(parts[0]), c1mt_2: Math.round(parts[1]),
            c2mt_1: Math.round(parts[2]), c2mt_2: Math.round(parts[3]),
            b1mt_1: Math.round(parts[4]), b1mt_2: Math.round(parts[5]),
            b2mt_1: Math.round(parts[6]), b2mt_2: Math.round(parts[7])
          });
        }
      });
    }
  }

  return matches.length > 0 ? { matches: matches } : null;
}

function saveH2H() {
  const save = document.getElementById('save_h2h');
  if (!save || !save.checked) return;
  const h2h = collectH2H();
  if (!h2h) return;
  try { localStorage.setItem(H2H_KEY, JSON.stringify(h2h)); } catch (e) {}
}

function loadH2H() {
  try {
    const raw = localStorage.getItem(H2H_KEY);
    if (!raw) return;
    const data = JSON.parse(raw);
    if (!data.matches) return;
    data.matches.forEach((m, i) => {
      if (i >= H2H_COUNT) return;
      Object.keys(m).forEach(f => {
        const inp = document.querySelector('input[data-h2h="' + i + '"][data-f="' + f + '"]');
        if (inp) inp.value = m[f];
      });
    });
  } catch (e) {}
}

function renderH2HBlock(h2hStats) {
  if (!h2hStats) return '';
  let html = '<div class="card"><h2>H2H - 5 dernieres confrontations</h2>';
  html += '<div class="market-detail">';
  html += '<b>' + h2hStats.n_matches + ' matchs analyses</b><br><br>';
  html += 'MC1 H2H : <span>' + h2hStats.mc1_avg.toFixed(2) + '</span><br>';
  html += 'MC2 H2H : <span>' + h2hStats.mc2_avg.toFixed(2) + '</span><br>';
  html += 'MC Global H2H : <span>' + h2hStats.mc_global_avg.toFixed(2) + '</span><br><br>';
  html += 'Corners Eq1 (total) : <span>' + h2hStats.corners1_avg.toFixed(1) + '</span><br>';
  html += 'Corners Eq2 (total) : <span>' + h2hStats.corners2_avg.toFixed(1) + '</span><br>';
  html += 'Buts Eq1 : <span>' + h2hStats.goals1_avg.toFixed(1) + '</span><br>';
  html += 'Buts Eq2 : <span>' + h2hStats.goals2_avg.toFixed(1) + '</span>';
  html += '</div></div>';
  return html;
}

function submitForm(e) {
  e.preventDefault();
  LAST_MARKETS = [];
  saveBookInfo();
  saveH2H();

  const homeF = getField('home');
  const awayF = getField('away');
  const leagueF = getField('league');
  const dateF = getField('date');
  const simsF = getField('n_simulations');
  const o1F = getField('odds_1');
  const oxF = getField('odds_x');
  const o2F = getField('odds_2');

  const data = {
    home: homeF ? homeF.value : '',
    away: awayF ? awayF.value : '',
    league: leagueF ? leagueF.value : 'E0',
    date: dateF ? dateF.value : null,
    n_simulations: simsF ? parseInt(simsF.value) : 5000,
    h2h: collectH2H(),
  };

  const o1 = o1F ? parseFloat(o1F.value) : NaN;
  const ox = oxF ? parseFloat(oxF.value) : NaN;
  const o2 = o2F ? parseFloat(o2F.value) : NaN;
  if (o1 > 1 && ox > 1 && o2 > 1) {
    data.odds_1 = o1;
    data.odds_x = ox;
    data.odds_2 = o2;
  }

  const result = document.getElementById("result");
  document.getElementById("portfolio-section").style.display = "none";
  document.getElementById("portfolio-result").innerHTML = "";
  result.style.display = "block";
  result.innerHTML = '<div class="loading">Analyse en cours... (20-40 secondes)</div>';

  fetch("/predict", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  })
  .then(r => r.json())
  .then(d => {
    if (d.detail) {
      result.innerHTML = '<div class="card" style="color:#f85149">Erreur : ' + JSON.stringify(d.detail) + '</div>';
      return;
    }
    const decClass = d.decision === "BET" ? "bet" : "nobet";
    let html = '<div class="card">';
    html += '<h2>' + d.team1 + ' vs ' + d.team2 + '</h2>';
    html += '<div style="margin-bottom:12px"><span class="badge ' + decClass + '">' + d.decision + '</span></div>';
    html += '<div class="market-detail">' + d.reason + '</div>';
    if (d.boost1 && d.boost2) {
      html += '<div style="margin-top:8px; font-size:12px; color:#6e7681;">';
      html += 'Boost Eq1 : x' + d.boost1.toFixed(3) + ' | Boost Eq2 : x' + d.boost2.toFixed(3);
      html += '</div>';
    }
    html += '</div>';

    html += '<div class="card"><h2>Meilleur marche global</h2>';
    html += marketBlock("TOP", d.top, true);
    html += '</div>';

    html += '<div class="card"><h2>Corners</h2>';
    html += marketBlock("Equipe 1", d.top_per_family.team1, false);
    html += marketBlock("Equipe 2", d.top_per_family.team2, false);
    html += marketBlock("Total", d.top_per_family.total, false);
    html += marketBlock("Multi Corner", d.top_per_family.multicorner, false);
    html += '</div>';

    html += '<div class="card"><h2>Buts</h2>';
    html += marketBlock("1X2", d.top_per_family.result, false);
    html += marketBlock("Over/Under", d.top_per_family.goals_total, false);
    html += marketBlock("Handicap", d.top_per_family.handicap, false);
    html += '<div id="coherence-display" style="margin-top:12px;"></div>';
    if (d.goals_outcomes) {
      html += '<h3>Repartition 1X2</h3>';
      html += '<div class="market-detail">';
      html += 'Domicile : <span>' + fmtPct(d.goals_outcomes.home_win) + '</span> | ';
      html += 'Nul : <span>' + fmtPct(d.goals_outcomes.draw) + '</span> | ';
      html += 'Exterieur : <span>' + fmtPct(d.goals_outcomes.away_win) + '</span>';
      html += '</div>';
    }
    html += '</div>';

    html += renderH2HBlock(d.h2h_stats);

    html += '<div class="card"><h2>Technique</h2>';
    html += '<div class="market-detail">';
    html += '<b>Corners</b><br>';
    html += 'l1 : <span>' + (d.lam1 ? d.lam1.toFixed(2) : "—") + '</span> | ';
    html += 'l2 : <span>' + (d.lam2 ? d.lam2.toFixed(2) : "—") + '</span><br>';
    html += '<b>Buts</b><br>';
    html += 'l dom : <span>' + (d.lam_h_goals ? d.lam_h_goals.toFixed(2) : "—") + '</span> | ';
    html += 'l ext : <span>' + (d.lam_a_goals ? d.lam_a_goals.toFixed(2) : "—") + '</span><br>';
    html += 'MDS : <span>' + (d.dominance.mds ? d.dominance.mds.toFixed(3) : "—") + '</span>';
    html += '</div></div>';

    result.innerHTML = html;
    document.getElementById("portfolio-section").style.display = "block";
  })
  .catch(err => {
    result.innerHTML = '<div class="card" style="color:#f85149">Erreur reseau : ' + err.message + '</div>';
  });
    }


const MC_BLOCKS = [
  { id: 'mc1d', label: 'Eq1 - 10 matchs a DOMICILE', team: 1, n: 10 },
  { id: 'mc1g', label: 'Eq1 - 5 matchs GLOBAUX', team: 1, n: 5 },
  { id: 'mc2e', label: 'Eq2 - 10 matchs a l EXTERIEUR', team: 2, n: 10 },
  { id: 'mc2g', label: 'Eq2 - 5 matchs GLOBAUX', team: 2, n: 5 }
];

function poissonSampleFast(lam, randFn) {
  if (lam <= 0) return 0;
  if (lam > 20) {
    const u1 = Math.max(1e-9, randFn());
    const u2 = randFn();
    const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    return Math.max(0, Math.round(lam + Math.sqrt(lam) * z));
  }
  const L = Math.exp(-lam);
  let k = 0, p = 1;
  do { k++; p *= randFn(); } while (p > L);
  return k - 1;
}

function simulateLatentFusion(lam_H1, lam_H2, lam_A1, lam_A2, nSims, seed) {
  const A_COEFF = 0.20;
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

  const mc1 = [];
  const mc2 = [];
  const mcGlobal = [];

  for (let i = 0; i < nSims; i++) {
    const U = randn();
    const factor = Math.exp(A_COEFF * U);
    const H1 = poissonSampleFast(lam_H1 * factor, rand);
    const H2 = poissonSampleFast(lam_H2 * factor, rand);
    const A1 = poissonSampleFast(lam_A1 * factor, rand);
    const A2 = poissonSampleFast(lam_A2 * factor, rand);
    const m1 = H1 * H2;
    const m2 = A1 * A2;
    mc1.push(m1);
    mc2.push(m2);
    mcGlobal.push(m1 + m2);
  }

  const exp2a2 = Math.exp(2 * A_COEFF * A_COEFF);
  const E_MC1 = lam_H1 * lam_H2 * exp2a2;
  const E_MC2 = lam_A1 * lam_A2 * exp2a2;

  return {
    mc1: mc1,
    mc2: mc2,
    mcGlobal: mcGlobal,
    a_coeff: A_COEFF,
    E_MC1_analytic: E_MC1,
    E_MC2_analytic: E_MC2,
    E_MCglobal_analytic: E_MC1 + E_MC2
  };
}

function generateMCForms() {
  const container = document.getElementById('mc-forms');
  if (!container) return;
  let html = '';
  MC_BLOCKS.forEach(block => {
    html += '<div class="mc-block" data-block="' + block.id + '">';
    html += '<div class="mc-block-title">' + block.label + ' <span class="badge-info">(' + block.n + ' matchs)</span></div>';
    html += '<div class="mc-tabs">';
    html += '<div class="mc-tab active" data-tab="grid" onclick="switchMCTab(\'' + block.id + '\', \'grid\')">Grille</div>';
    html += '<div class="mc-tab" data-tab="csv" onclick="switchMCTab(\'' + block.id + '\', \'csv\')">CSV</div>';
    html += '</div>';
    html += '<div class="mc-grid-view" data-view="grid">';
    html += '<div class="mc-grid-header"><span>#</span><span>1re MT</span><span>2e MT</span></div>';
    for (let i = 0; i < block.n; i++) {
      html += '<div class="mc-grid-row">';
      html += '<span class="mc-idx">' + (i + 1) + '</span>';
      html += '<input type="number" min="0" max="20" step="1" data-block="' + block.id + '" data-idx="' + i + '" data-half="1" placeholder="0">';
      html += '<input type="number" min="0" max="20" step="1" data-block="' + block.id + '" data-idx="' + i + '" data-half="2" placeholder="0">';
      html += '</div>';
    }
    html += '</div>';
    html += '<div class="mc-csv-view" data-view="csv" style="display:none;">';
    html += '<textarea class="mc-csv-area" data-block="' + block.id + '" placeholder="Format : 1re MT, 2e MT"></textarea>';
    html += '<div class="mc-hint">Une ligne = un match. Format : A1, A2</div>';
    html += '</div>';
    html += '</div>';
  });
  container.innerHTML = html;
}

function switchMCTab(blockId, tab) {
  const block = document.querySelector('[data-block="' + blockId + '"]');
  if (!block) return;
  block.querySelectorAll('.mc-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === tab);
  });
  block.querySelectorAll('[data-view]').forEach(v => {
    v.style.display = (v.dataset.view === tab) ? '' : 'none';
  });
}

function parseMCCSV(blockId) {
  const ta = document.querySelector('textarea[data-block="' + blockId + '"]');
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
    const gridView = document.querySelector('[data-block="' + block.id + '"] [data-view="grid"]');
    const gridVisible = gridView && gridView.style.display !== 'none';
    let pairs = [];
    if (gridVisible) {
      const inputs1 = document.querySelectorAll('input[data-block="' + block.id + '"][data-half="1"]');
      const inputs2 = document.querySelectorAll('input[data-block="' + block.id + '"][data-half="2"]');
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
    data[block.id] = { block: block, pairs: pairs };
  });
  return data;
}

function computeStats(pairs) {
  if (!pairs || pairs.length === 0) return null;
  const A1 = pairs.map(p => p[0]);
  const A2 = pairs.map(p => p[1]);
  const n = pairs.length;
  const mean1 = A1.reduce((a, b) => a + b, 0) / n;
  const mean2 = A2.reduce((a, b) => a + b, 0) / n;
  const var1 = A1.reduce((s, v) => s + Math.pow(v - mean1, 2), 0) / Math.max(1, n - 1);
  const var2 = A2.reduce((s, v) => s + Math.pow(v - mean2, 2), 0) / Math.max(1, n - 1);
  const std1 = Math.sqrt(var1);
  const std2 = Math.sqrt(var2);
  let cov = 0;
  for (let i = 0; i < n; i++) cov += (A1[i] - mean1) * (A2[i] - mean2);
  cov = cov / Math.max(1, n - 1);
  const rho = (std1 > 1e-9 && std2 > 1e-9) ? cov / (std1 * std2) : 0;
  const products = pairs.map(p => p[0] * p[1]);
  const zeroCount = products.filter(x => x === 0).length;
  const sorted = [].concat(products).sort((a, b) => a - b);
  const p10 = sorted[Math.floor(0.10 * n)];
  const p50 = sorted[Math.floor(0.50 * n)];
  const p90 = sorted[Math.min(n - 1, Math.floor(0.90 * n))];
  return {
    n: n, mean1: mean1, mean2: mean2, std1: std1, std2: std2,
    rho: rho, zeroCount: zeroCount,
    meanProduct: products.reduce((a, b) => a + b, 0) / n,
    p10: p10, p50: p50, p90: p90
  };
}


function mcProbabilities(samples) {
  const sorted = [].concat(samples).sort((a, b) => a - b);
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
    probs[L] = { over: over, under: 1 - over };
  });
  return { mean: mean, p10: p10, p50: p50, p90: p90, probs: probs };
}

function renderMCBlock(title, samples, teamSide) {
  const stats = mcProbabilities(samples);
  let html = '<div class="mc-result-item" data-mc="' + teamSide + '">';
  html += '<div class="mc-result-title">' + title + '</div>';
  html += '<div class="mc-result-detail">';
  html += 'Moyenne : <span>' + stats.mean.toFixed(2) + '</span> | ';
  html += 'Mediane : <span>' + stats.p50 + '</span><br>';
  html += 'P10 : <span>' + stats.p10 + '</span> | P90 : <span>' + stats.p90 + '</span>';
  html += '</div>';
  html += '<div class="mc-dist-bar"><div class="mc-dist-fill" style="width:100%"></div></div>';
  html += '<div class="mc-dist-labels"><span>' + stats.p10 + '</span><span>' + stats.p50 + '</span><span>' + stats.p90 + '</span></div>';
  html += '<div style="margin-top:10px; font-size:12px; color:#8b949e;">';
  html += '<b>Probabilites Over :</b><br>';
  [5.5, 10.5, 15.5, 20.5, 25.5, 30.5, 35.5].forEach(L => {
    const p = stats.probs[L];
    if (p) {
      html += 'Over ' + L + ' : <span style="color:#58a6ff">' + (p.over * 100).toFixed(1) + '%</span> | ';
      html += 'Under ' + L + ' : <span style="color:#8b949e">' + (p.under * 100).toFixed(1) + '%</span><br>';
    }
  });
  html += '</div>';
  const mid = 'MC_' + teamSide;
  const pOver = stats.probs[20.5] ? stats.probs[20.5].over : 0.5;
  const pUnder = 1 - pOver;
  const best = pOver >= pUnder ? { dir: 'over', p: pOver, line: 20.5 } : { dir: 'under', p: pUnder, line: 20.5 };
  html += '<div class="odds-row" style="margin-top:10px; border-top:1px solid #30363d; padding-top:10px;">';
  html += '<label>Cote ' + best.dir.toUpperCase() + ' ' + best.line + ' :</label>';
  html += '<input type="number" step="0.01" min="1.01" placeholder="1.50" ';
  html += 'oninput="analyzeMC(this, \'' + mid + '\', ' + best.p + ');">';
  html += '<span class="verdict none">—</span>';
  html += '</div>';
  html += '<div class="analysis"></div>';
  html += '</div>';
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
      market_id: marketId, family: 'multicorner', sport: 'corners',
      direction: 'over', line: 20.5, prob: prob, odds: null
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
    verdict.textContent = "BET (+" + (ev * 100).toFixed(1) + "%)";
    verdict.className = "verdict ok";
  } else {
    verdict.textContent = "NO BET (" + (ev * 100).toFixed(1) + "%)";
    verdict.className = "verdict ko";
  }
  if (!analysis) return;
  analysis.innerHTML = '<div class="analysis-grid">' +
    '<div class="k">Prob implicite :</div><div class="v">' + fmtPct(p_imp) + '</div>' +
    '<div class="k">Prob juste :</div><div class="v">' + fmtPct(p_market) + '</div>' +
    '<div class="k">Prob modele :</div><div class="v">' + fmtPct(prob) + '</div>' +
    '<div class="k">Prob posterieure :</div><div class="v">' + fmtPct(p_post) + '</div>' +
    '<div class="k">Edge bayesien :</div><div class="v">' + fmtPct(p_post - p_market) + '</div>' +
    '<div class="k">EV :</div><div class="v">' + (ev * 100).toFixed(2) + '%</div>' +
    '<div class="k">Kelly :</div><div class="v">' + (kelly * 100).toFixed(1) + '%</div>' +
    '</div>' +
    '<div class="grade-badge grade-' + grade + '">Grade ' + grade + '</div>';
  analysis.classList.add("show");
}

function computeMultiCorner() {
  const box = document.getElementById('mc-result');
  const data = getMCData();
  const hasE1 = data['mc1d'].pairs.length >= 3 || data['mc1g'].pairs.length >= 3;
  const hasE2 = data['mc2e'].pairs.length >= 3 || data['mc2g'].pairs.length >= 3;
  if (!hasE1 || !hasE2) {
    box.innerHTML = '<div class="card" style="color:#f85149">Remplis au moins 3 matchs pour chaque equipe.</div>';
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
    coherenceWarn += '<div class="corr-warning">Eq1 : ecart > 30% entre domicile et global</div>';
  }
  if (s2e && s2g && Math.abs(s2e.meanProduct - s2g.meanProduct) / Math.max(1, s2g.meanProduct) > 0.30) {
    coherenceWarn += '<div class="corr-warning">Eq2 : ecart > 30% entre exterieur et global</div>';
  }

  const N_SIMS = 10000;
  const fusion = simulateLatentFusion(
    stats1.mean1, stats1.mean2,
    stats2.mean1, stats2.mean2,
    N_SIMS, 42
  );
  const mc1 = fusion.mc1;
  const mc2 = fusion.mc2;
  const mcGlobal = fusion.mcGlobal;

  const emp_MC1 = mc1.reduce((a, b) => a + b, 0) / mc1.length;
  const emp_MC2 = mc2.reduce((a, b) => a + b, 0) / mc2.length;
  const emp_MCglobal = mcGlobal.reduce((a, b) => a + b, 0) / mcGlobal.length;

  let html = '<div class="card">';
  html += '<h2>Resultats Multi-Corner</h2>';
  html += '<div style="font-size:11px; color:#6e7681; margin-bottom:10px;">';
  html += 'Modele : Poisson + facteur latent U (a=' + fusion.a_coeff.toFixed(2) + ')';
  html += '</div>';
  html += '<div class="mc-result-detail" style="margin-bottom:12px;">';
  html += 'Eq1 : ' + n1 + ' matchs (P(0)=' + (stats1.zeroCount / stats1.n * 100).toFixed(0) + '%)<br>';
  html += 'Eq2 : ' + n2 + ' matchs (P(0)=' + (stats2.zeroCount / stats2.n * 100).toFixed(0) + '%)';
  html += '</div>';

  html += '<div style="padding:10px; background:#0a0d12; border:1px solid #30363d; border-radius:6px; margin-bottom:12px; font-size:12px; color:#8b949e;">';
  html += '<b style="color:#58a6ff;">E[MC] analytique vs empirique</b><br>';
  html += 'MC1 : <span style="color:#e6edf3;">' + fusion.E_MC1_analytic.toFixed(2) + '</span> vs ' + emp_MC1.toFixed(2) + ' (sim)<br>';
  html += 'MC2 : <span style="color:#e6edf3;">' + fusion.E_MC2_analytic.toFixed(2) + '</span> vs ' + emp_MC2.toFixed(2) + ' (sim)<br>';
  html += 'MC Global : <span style="color:#e6edf3;">' + fusion.E_MCglobal_analytic.toFixed(2) + '</span> vs ' + emp_MCglobal.toFixed(2) + ' (sim)';
  html += '</div>';

  if (coherenceWarn) html += coherenceWarn;
  html += renderMCBlock('MC Equipe 1 = A1 x A2', mc1, 'T1');
  html += renderMCBlock('MC Equipe 2 = B1 x B2', mc2, 'T2');
  html += renderMCBlock('MC Global = MC1 + MC2', mcGlobal, 'GLOBAL');
  html += '</div>';

  box.innerHTML = html;
                         }


function shadowLoad() {
  try {
    const raw = localStorage.getItem(SHADOW_KEY);
    return raw ? JSON.parse(raw) : { bets: [] };
  } catch (e) { return { bets: [] }; }
}

function shadowSave(data) {
  try { localStorage.setItem(SHADOW_KEY, JSON.stringify(data)); } catch (e) {}
}

function shadowSaveCurrent() {
  if (!LAST_MARKETS || LAST_MARKETS.length === 0) {
    alert('Analyse un match d\'abord.');
    return;
  }
  const homeF = getField('home');
  const awayF = getField('away');
  const home = homeF ? homeF.value : '?';
  const away = awayF ? awayF.value : '?';
  const data = shadowLoad();
  let count = 0;
  LAST_MARKETS.forEach(m => {
    if (m.odds && m.odds > 1) {
      data.bets.push({
        id: Date.now() + '_' + Math.random().toString(36).slice(2, 8),
        match: home + ' vs ' + away,
        market: m.market_id, prob: m.prob, odds: m.odds,
        date: new Date().toISOString(), result: null
      });
      count++;
    }
  });
  shadowSave(data);
  shadowRenderStats();
  alert(count + ' pari(s) enregistre(s) dans Shadow.');
}

function shadowMarkResult(betId, result) {
  const data = shadowLoad();
  const bet = data.bets.find(b => b.id === betId);
  if (!bet) return;
  bet.result = result;
  shadowSave(data);
  shadowRenderStats();
}

function shadowComputeMetrics() {
  const data = shadowLoad();
  const resolved = data.bets.filter(b => b.result === 'win' || b.result === 'loss');
  if (resolved.length === 0) {
    return { n: 0, wins: 0, losses: 0, winRate: 0, roi: 0, ece: 0, profit: 0, bins: null };
  }
  let wins = 0, losses = 0, profit = 0, totalStake = 0;
  const bins = [];
  for (let i = 0; i < 10; i++) bins.push({ p: 0, o: 0, n: 0 });
  resolved.forEach(b => {
    totalStake += 1;
    const isWin = b.result === 'win';
    if (isWin) { wins++; profit += (b.odds - 1); }
    else { losses++; profit -= 1; }
    const binIdx = Math.min(9, Math.floor(b.prob * 10));
    bins[binIdx].p += b.prob;
    bins[binIdx].o += isWin ? 1 : 0;
    bins[binIdx].n += 1;
  });
  let ece = 0;
  bins.forEach(bin => {
    if (bin.n > 0) {
      const avgP = bin.p / bin.n;
      const avgO = bin.o / bin.n;
      ece += (bin.n / resolved.length) * Math.abs(avgP - avgO);
    }
  });
  return {
    n: resolved.length, wins: wins, losses: losses,
    winRate: wins / resolved.length,
    roi: profit / totalStake, profit: profit, ece: ece, bins: bins
  };
}

function shadowRenderStats() {
  const box = document.getElementById('shadow-stats');
  if (!box) return;
  const data = shadowLoad();
  const m = shadowComputeMetrics();
  let html = '';
  if (data.bets.length === 0) {
    html = '<div class="shadow-empty">Aucun pari enregistre.</div>';
    box.innerHTML = html;
    return;
  }
  if (m.n > 0) {
    const roiClass = m.roi > 0 ? 'good' : (m.roi < 0 ? 'bad' : 'neutral');
    const wrClass = m.winRate > 0.55 ? 'good' : (m.winRate < 0.45 ? 'bad' : 'neutral');
    const eceClass = m.ece < 0.05 ? 'good' : (m.ece > 0.10 ? 'bad' : 'neutral');
    html += '<div class="shadow-stats-grid">';
    html += '<div class="k">Paris resolus :</div><div class="v">' + m.n + '</div>';
    html += '<div class="k">Gagnes :</div><div class="v good">' + m.wins + '</div>';
    html += '<div class="k">Perdus :</div><div class="v bad">' + m.losses + '</div>';
    html += '<div class="k">Win rate :</div><div class="v ' + wrClass + '">' + (m.winRate * 100).toFixed(1) + '%</div>';
    html += '<div class="k">ROI reel :</div><div class="v ' + roiClass + '">' + (m.roi >= 0 ? '+' : '') + (m.roi * 100).toFixed(2) + '%</div>';
    html += '<div class="k">Profit (unites) :</div><div class="v ' + roiClass + '">' + (m.profit >= 0 ? '+' : '') + m.profit.toFixed(2) + '</div>';
    html += '<div class="k">ECE reel :</div><div class="v ' + eceClass + '">' + m.ece.toFixed(4) + '</div>';
    html += '<div class="k">Total analyses :</div><div class="v">' + data.bets.length + '</div>';
    html += '</div>';
    html += shadowRenderReliability(m.bins);
  }
  html += '<div style="margin-top:12px; font-size:12px; color:#8b949e; text-transform:uppercase; letter-spacing:0.5px;">Derniers paris</div>';
  const recent = [].concat(data.bets).reverse().slice(0, 15);
  recent.forEach(b => {
    const cls = b.result === 'win' ? 'win' : (b.result === 'loss' ? 'loss' : '');
    const resolved = b.result ? 'resolved' : '';
    html += '<div class="shadow-bet ' + cls + ' ' + resolved + '">';
    html += '<div class="match">' + b.match + '</div>';
    html += '<div class="mkt">' + b.market + '</div>';
    html += '<div class="odds">' + b.odds.toFixed(2) + '</div>';
    if (b.result === 'win') html += '<div class="result-badge win">WIN</div>';
    else if (b.result === 'loss') html += '<div class="result-badge loss">LOSS</div>';
    else {
      html += '<div class="actions">';
      html += '<button class="win" onclick="shadowMarkResult(\'' + b.id + '\', \'win\')">V</button>';
      html += '<button class="loss" onclick="shadowMarkResult(\'' + b.id + '\', \'loss\')">X</button>';
      html += '</div>';
    }
    html += '</div>';
  });
  box.innerHTML = html;
}

function shadowRenderReliability(bins) {
  if (!bins) return '';
  let html = '<div class="reliability-chart"><h4>Courbe de fiabilite</h4>';
  bins.forEach((bin, i) => {
    if (bin.n === 0) return;
    const avgP = bin.p / bin.n;
    const avgO = bin.o / bin.n;
    html += '<div class="reliability-bar-row">';
    html += '<div class="label">' + (i * 10) + '%-' + ((i + 1) * 10) + '%</div>';
    html += '<div class="bar-bg">';
    html += '<div class="bar-pred" style="width:' + (avgP * 100) + '%"></div>';
    html += '<div class="bar-real" style="width:' + (avgO * 100) + '%"></div>';
    html += '</div>';
    html += '<div class="val">' + (avgO * 100).toFixed(0) + '%/' + (avgP * 100).toFixed(0) + '%</div>';
    html += '</div>';
  });
  html += '</div>';
  return html;
}

function shadowExport() {
  const data = shadowLoad();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'cornix_shadow_' + new Date().toISOString().slice(0, 10) + '.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
      }


function fitTemperature(bets) {
  const resolved = bets.filter(b => b.result === 'win' || b.result === 'loss');
  if (resolved.length < 10) return { T: 1.0, n: resolved.length, applied: false };
  let T = 1.0;
  const lr = 0.05, iters = 200;
  for (let it = 0; it < iters; it++) {
    let grad = 0;
    resolved.forEach(b => {
      const logitP = logit(b.prob);
      const z = logitP / T;
      const p_cal = sigmoid(z);
      const y = b.result === 'win' ? 1 : 0;
      grad += (p_cal - y) * (-logitP / (T * T));
    });
    T -= lr * grad / resolved.length;
    T = Math.max(0.3, Math.min(3.0, T));
  }
  return { T: T, n: resolved.length, applied: true };
}

function applyTemperature(prob, T) {
  if (!T || T === 1.0) return prob;
  const z = logit(prob) / T;
  return sigmoid(z);
}

function oracleParseMatches() {
  const ta = document.getElementById('oracle-matches');
  if (!ta || !ta.value.trim()) return [];
  const matches = [];
  ta.value.trim().split('\n').forEach(line => {
    if (!line.trim()) return;
    const parts = line.split(/[,\t;]+/).map(s => s.trim());
    if (parts.length < 7) return;
    const o1 = parseFloat(parts[4]);
    const ox = parseFloat(parts[5]);
    const o2 = parseFloat(parts[6]);
    if (isNaN(o1) || isNaN(ox) || isNaN(o2)) return;
    matches.push({
      home: parts[0], away: parts[1], league: parts[2], date: parts[3],
      odds_1: o1, odds_x: ox, odds_2: o2
    });
  });
  return matches;
}

async function oracleRun() {
  const stage1 = document.getElementById('oracle-stage1');
  const stage2 = document.getElementById('oracle-stage2');
  stage2.innerHTML = '';
  ORACLE_RESULTS = [];

  const matches = oracleParseMatches();
  if (matches.length === 0) {
    stage1.innerHTML = '<div class="card" style="color:#f85149">Aucun match valide.</div>';
    return;
  }

  stage1.innerHTML = '<div class="loading">Analyse de ' + matches.length + ' matchs...</div>';

  for (let i = 0; i < matches.length; i++) {
    const m = matches[i];
    stage1.innerHTML = '<div class="loading">Analyse ' + (i + 1) + '/' + matches.length + ' : ' + m.home + ' vs ' + m.away + '</div>';
    try {
      const resp = await fetch('/predict', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          home: m.home, away: m.away, league: m.league, date: m.date,
          n_simulations: 2000, odds_1: m.odds_1, odds_x: m.odds_x, odds_2: m.odds_2
        })
      });
      const d = await resp.json();
      if (!d.detail) ORACLE_RESULTS.push({ match_label: m.home + ' vs ' + m.away, data: d });
    } catch (e) { console.error('Erreur match ' + (i + 1), e); }
  }

  oracleRenderStage1();
}

function oracleRenderStage1() {
  const stage1 = document.getElementById('oracle-stage1');
  if (ORACLE_RESULTS.length === 0) {
    stage1.innerHTML = '<div class="card" style="color:#f85149">Aucun resultat.</div>';
    return;
  }

  const candidates = [];
  ORACLE_RESULTS.forEach((r, idx) => {
    const tpf = r.data.top_per_family || {};
    ['team1', 'team2', 'total', 'multicorner', 'result', 'goals_total', 'handicap'].forEach(fam => {
      const m = tpf[fam];
      if (!m) return;
      const justOdds = m.prob > 0 ? (1.0 / m.prob) : 999;
      if (justOdds < 1.05 || justOdds > 3.5) return;
      candidates.push({
        oracle_idx: idx, match_label: r.match_label, market_id: m.market_id,
        family: fam, sport: m.sport, prob: m.prob, cote_juste: justOdds, edge: m.edge
      });
    });
  });

  candidates.sort((a, b) => b.edge - a.edge);
  const top = candidates.slice(0, 15);

  if (top.length === 0) {
    stage1.innerHTML = '<div class="card" style="color:#f85149">Aucun marche interessant.</div>';
    return;
  }

  let html = '<div class="card"><h2>TOP 15 marches a coter</h2>';
  html += '<div style="font-size:12px; color:#8b949e; margin-bottom:10px;">' + ORACLE_RESULTS.length + ' matchs analyses.</div>';

  top.forEach((c, i) => {
    html += '<div class="oracle-market">';
    html += '<div style="font-size:13px; color:#e6edf3; margin-bottom:4px;"><b>' + (i + 1) + '.</b> ' + c.match_label + '</div>';
    html += '<div style="font-size:12px; color:#8b949e;">';
    html += '<span style="color:#58a6ff;">' + c.market_id + '</span> | ';
    html += 'Prob : ' + (c.prob * 100).toFixed(1) + '% | ';
    html += 'Cote juste : <b>' + c.cote_juste.toFixed(2) + '</b>';
    html += '</div>';
    html += '<div class="odds-row" style="margin-top:6px;">';
    html += '<label>Ta cote :</label>';
    html += '<input type="number" step="0.01" min="1.01" placeholder="' + c.cote_juste.toFixed(2) + '" ';
    html += 'data-oracle-idx="' + i + '" class="oracle-cote-input">';
    html += '</div></div>';
  });

  html += '<button type="button" class="secondary" onclick="oracleComputePortfolio()" style="margin-top:12px;">CALCULER LE PORTEFEUILLE ORACLE</button>';
  html += '</div>';

  stage1.innerHTML = html;
  stage1._candidates = top;
  stage1._results = ORACLE_RESULTS;
}

function oracleComputePortfolio() {
  const stage2 = document.getElementById('oracle-stage2');
  try {
    const stage1 = document.getElementById('oracle-stage1');
    if (!stage1) {
      stage2.innerHTML = '<div class="card" style="color:#f85149">ERREUR : oracle-stage1 introuvable</div>';
      return;
    }
    const candidates = stage1._candidates || [];
    if (candidates.length === 0) {
      stage2.innerHTML = '<div class="card" style="color:#f85149">ERREUR : aucun candidat stocke. Relance Oracle sans rafraichir.</div>';
      return;
    }

    const allMarkets = [];
    candidates.forEach((c, i) => {
      const input = document.querySelector('input[data-oracle-idx="' + i + '"]');
      if (!input || !input.value) return;
      const odds = parseFloat(input.value);
      if (isNaN(odds) || odds <= 1) return;
      const p_imp = 1.0 / odds;
      const p_market = Math.min(0.99, p_imp * (1 - MARGIN_BOOK));
      const p_post = bayesianFusion(c.prob, p_market);
      const ev = p_post * odds - 1.0;
      const kelly = Math.max(0, kellyFraction(p_post, odds) * KELLY_SAFE);
      const grade = gradeValue(ev, kelly, p_post, p_market);
      allMarkets.push({
        match_label: c.match_label, market_id: c.market_id, family: c.family,
        sport: c.sport, odds: odds, prob: c.prob, p_post: p_post, p_market: p_market,
        ev: ev, kelly: kelly, grade: grade
      });
    });

    if (allMarkets.length === 0) {
      stage2.innerHTML = '<div class="card" style="color:#f85149">Saisis au moins une cote.</div>';
      return;
    }

    const positives = allMarkets.filter(m => m.ev > 0);
    positives.sort((a, b) => b.ev - a.ev);
    const top5 = positives.slice(0, 5);

    const negatives = allMarkets.filter(m => m.ev < 0);
    negatives.sort((a, b) => a.ev - b.ev);
    const worst = negatives.slice(0, 5);

    const candidates2 = positives.slice(0, 10);
    let portfolio = null;

    if (candidates2.length >= 2) {
      const n = candidates2.length;
      const mu = candidates2.map(m => m.ev);
      const Sigma = [];
      for (let i = 0; i < n; i++) {
        const row = [];
        for (let j = 0; j < n; j++) {
          if (i === j) {
            const p = candidates2[i].p_post;
            row.push(p * (1 - p));
          } else {
            const sameMatch = candidates2[i].match_label === candidates2[j].match_label;
            let rho = 0.05;
            if (sameMatch) {
              rho = correlationHeuristic(
                { market_id: candidates2[i].market_id, family: candidates2[i].family, direction: '' },
                { market_id: candidates2[j].market_id, family: candidates2[j].family, direction: '' }
              );
            }
            const p1 = candidates2[i].p_post;
            const p2 = candidates2[j].p_post;
            row.push(rho * Math.sqrt(p1 * (1 - p1) * p2 * (1 - p2)));
          }
        }
        Sigma.push(row);
      }

      const SigmaInv = matrixInvert(Sigma);
      if (SigmaInv) {
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
        portfolio = {
          items: candidates2.map((m, i) => Object.assign({}, m, { alloc: f[i] }))
            .sort((a, b) => b.alloc - a.alloc),
          total_stake: f.reduce((a, b) => a + b, 0),
          expected: pRet, volatility: pStd, sharpe: sharpe
        };
      }
    }

    let html = '';
    if (top5.length > 0) {
      html += '<div class="card"><h2>TOP 5 Paris du jour</h2>';
      top5.forEach((m, i) => {
        const emoji = ['1.', '2.', '3.', '4.', '5.'][i];
        html += '<div style="padding:8px 0; border-bottom:1px solid #21262d;">';
        html += '<div style="font-size:13px; color:#e6edf3;"><b>' + emoji + '</b> ' + m.match_label + '</div>';
        html += '<div style="font-size:12px; color:#8b949e; margin-top:4px;">';
        html += '<span style="color:#58a6ff;">' + m.market_id + '</span> @ ' + m.odds.toFixed(2);
        html += ' | EV <b style="color:#3fb950;">+' + (m.ev * 100).toFixed(1) + '%</b>';
        html += ' | Kelly ' + (m.kelly * 100).toFixed(1) + '%';
        html += '</div>';
        html += '<div class="grade-badge grade-' + m.grade + '" style="margin-top:4px;">Grade ' + m.grade + '</div>';
        html += '</div>';
      });
      html += '</div>';
    } else {
      html += '<div class="card"><h2>TOP 5 Paris du jour</h2><div style="color:#f85149; font-size:13px;">Aucun pari a EV positif.</div></div>';
    }

    if (portfolio) {
      html += '<div class="card"><h2>Portefeuille Oracle — Kelly 25%</h2>';
      portfolio.items.forEach((m, i) => {
        const pct = (m.alloc * 100).toFixed(2);
        const barW = Math.min(60, m.alloc * 400);
        const zero = m.alloc < 0.001 ? ' zero' : '';
        html += '<div class="portfolio-item">';
        html += '<span class="portfolio-rank">' + (i + 1) + '.</span>';
        html += '<span class="portfolio-name" style="font-size:11px;">' + m.match_label + ' — ' + m.market_id + '</span>';
        html += '<span class="portfolio-pct' + zero + '">' + pct + '%</span>';
        html += '<span class="portfolio-bar"><span class="portfolio-fill" style="width:' + barW + 'px"></span></span>';
        html += '</div>';
      });
      html += '<div class="metrics-grid">';
      html += '<div class="k">Capital total :</div><div class="v">' + (portfolio.total_stake * 100).toFixed(2) + '%</div>';
      html += '<div class="k">Esperance :</div><div class="v" style="color:#3fb950;">+' + (portfolio.expected * 100).toFixed(2) + '%</div>';
      html += '<div class="k">Volatilite :</div><div class="v">' + (portfolio.volatility * 100).toFixed(2) + '%</div>';
      html += '<div class="k">Sharpe :</div><div class="v">' + portfolio.sharpe.toFixed(3) + '</div>';
      html += '</div></div>';
    }

    if (worst.length > 0) {
      html += '<div class="card"><h2>A eviter absolument</h2>';
      worst.forEach(m => {
        html += '<div style="padding:6px 0; border-bottom:1px solid #21262d; font-size:12px;">';
        html += '<span style="color:#f85149;">X</span> ';
        html += m.match_label + ' — <span style="color:#58a6ff;">' + m.market_id + '</span> ';
        html += '@ ' + m.odds.toFixed(2) + ' → EV <b style="color:#f85149;">' + (m.ev * 100).toFixed(1) + '%</b>';
        html += '</div>';
      });
      html += '</div>';
    }
    stage2.innerHTML = html;
  } catch (err) {
    stage2.innerHTML = '<div class="card" style="color:#f85149"><b>ERREUR :</b> ' + err.message + '<br><br><pre style="font-size:10px; white-space:pre-wrap;">' + (err.stack || '') + '</pre></div>';
    console.error('Oracle error:', err);
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const dateInput = document.querySelector('input[name="date"]');
  if (dateInput) dateInput.valueAsDate = new Date();
  generateMCForms();
  generateH2HGrid();
  shadowRenderStats();
  loadBookInfo();
  loadH2H();
});

const _origAnalyze = analyze;
analyze = function(el, p_model, marketId, sport, family, line) {
  const data = shadowLoad();
  const metrics = shadowComputeMetrics();
  if (metrics.n >= 10) {
    const temp = fitTemperature(data.bets);
    if (temp.applied) p_model = applyTemperature(p_model, temp.T);
  }
  _origAnalyze(el, p_model, marketId, sport, family, line);
};
