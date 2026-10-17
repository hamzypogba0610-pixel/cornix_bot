
/* =========================================================
   THE ORACLE — Analyse multi-matchs
   ========================================================= */
let ORACLE_RESULTS = [];

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
      home: parts[0],
      away: parts[1],
      league: parts[2],
      date: parts[3],
      odds_1: o1,
      odds_x: ox,
      odds_2: o2
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
    stage1.innerHTML = '<div class="card" style="color:#f85149">Aucun match valide. Format : Eq1,Eq2,Championnat,Date,Cote1,CoteX,Cote2</div>';
    return;
  }

  stage1.innerHTML = '<div class="loading">Analyse de ' + matches.length + ' matchs en cours... (' + (matches.length * 30) + ' sec environ)</div>';

  let done = 0;
  for (let i = 0; i < matches.length; i++) {
    const m = matches[i];
    stage1.innerHTML = '<div class="loading">Analyse ' + (i + 1) + '/' + matches.length + ' : ' + m.home + ' vs ' + m.away + '</div>';
    try {
      const resp = await fetch('/predict', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          home: m.home,
          away: m.away,
          league: m.league,
          date: m.date,
          n_simulations: 2000,
          odds_1: m.odds_1,
          odds_x: m.odds_x,
          odds_2: m.odds_2
        })
      });
      const d = await resp.json();
      if (!d.detail) {
        ORACLE_RESULTS.push({
          match_label: m.home + ' vs ' + m.away,
          data: d
        });
      }
      done++;
    } catch (e) {
      console.error('Erreur match ' + (i + 1), e);
    }
  }

  oracleRenderStage1();
}

function oracleRenderStage1() {
  const stage1 = document.getElementById('oracle-stage1');
  if (ORACLE_RESULTS.length === 0) {
    stage1.innerHTML = '<div class="card" style="color:#f85149">Aucun résultat. Réessaie.</div>';
    return;
  }

  const candidates = [];

  ORACLE_RESULTS.forEach((r, idx) => {
    const d = r.data;
    const tpf = d.top_per_family || {};

    ['team1', 'team2', 'total', 'multicorner', 'result', 'goals_total', 'handicap'].forEach(fam => {
      const m = tpf[fam];
      if (!m) return;
      const justOdds = m.prob > 0 ? (1.0 / m.prob) : 999;
      if (justOdds < 1.05 || justOdds > 3.5) return;
      candidates.push({
        oracle_idx: idx,
        match_label: r.match_label,
        market_id: m.market_id,
        family: fam,
        sport: m.sport,
        prob: m.prob,
        cote_juste: justOdds,
        edge: m.edge
      });
    });
  });

  candidates.sort((a, b) => b.edge - a.edge);
  const top = candidates.slice(0, 15);

  if (top.length === 0) {
    stage1.innerHTML = '<div class="card" style="color:#f85149">Aucun marché intéressant trouvé.</div>';
    return;
  }

  let html = '<div class="card"><h2>TOP 15 marchés à coter</h2>';
  html += '<div style="font-size:12px; color:#8b949e; margin-bottom:10px;">' +
    ORACLE_RESULTS.length + ' matchs analysés. Saisis les cotes réelles de ton bookmaker.</div>';

  top.forEach((c, i) => {
    const mid = 'oracle_' + i;
    html += '<div class="oracle-market" data-mid="' + mid + '" style="background:#0d1117; border:1px solid #30363d; border-radius:8px; padding:10px; margin-bottom:8px;">';
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
    html += '</div>';
    html += '</div>';
  });

  html += '<button type="button" class="secondary" onclick="oracleComputePortfolio()" style="margin-top:12px;">CALCULER LE PORTEFEUILLE ORACLE</button>';
  html += '</div>';

  stage1.innerHTML = html;
  stage1._candidates = top;
  stage1._results = ORACLE_RESULTS;
      }


function oracleComputePortfolio() {
  const stage1 = document.getElementById('oracle-stage1');
  const stage2 = document.getElementById('oracle-stage2');
  const candidates = stage1._candidates || [];
  const results = stage1._results || [];

  if (candidates.length === 0) {
    stage2.innerHTML = '<div class="card" style="color:#f85149">Aucun marché.</div>';
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
      match_label: c.match_label,
      market_id: c.market_id,
      family: c.family,
      sport: c.sport,
      odds: odds,
      prob: c.prob,
      p_post: p_post,
      p_market: p_market,
      ev: ev,
      kelly: kelly,
      grade: grade
    });
  });

  if (allMarkets.length === 0) {
    stage2.innerHTML = '<div class="card" style="color:#f85149">Saisis au moins une cote pour calculer le portefeuille.</div>';
    return;
  }

  // ---- TOP 5 paris ----
  const positives = allMarkets.filter(m => m.ev > 0);
  positives.sort((a, b) => b.ev - a.ev);
  const top5 = positives.slice(0, 5);

  // ---- Paris à éviter ----
  const negatives = allMarkets.filter(m => m.ev < 0);
  negatives.sort((a, b) => a.ev - b.ev);
  const worst = negatives.slice(0, 5);

  // ---- Portefeuille Kelly multi-match ----
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
          // Matchs différents → corrélation quasi-nulle
          // Même match → corrélation heuristique
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
        expected: pRet,
        volatility: pStd,
        sharpe: sharpe
      };
    }
  }

  // ---- Rendu ----
  let html = '';

  // TOP 5
  if (top5.length > 0) {
    html += '<div class="card"><h2>TOP 5 Paris du jour</h2>';
    top5.forEach((m, i) => {
      const emoji = ['1.', '2.', '3.', '4.', '5.'][i];
      const gradeClass = 'grade-' + m.grade;
      html += '<div style="padding:8px 0; border-bottom:1px solid #21262d;">';
      html += '<div style="font-size:13px; color:#e6edf3;"><b>' + emoji + '</b> ' + m.match_label + '</div>';
      html += '<div style="font-size:12px; color:#8b949e; margin-top:4px;">';
      html += '<span style="color:#58a6ff;">' + m.market_id + '</span> @ ' + m.odds.toFixed(2);
      html += ' | EV <b style="color:#3fb950;">+' + (m.ev * 100).toFixed(1) + '%</b>';
      html += ' | Kelly ' + (m.kelly * 100).toFixed(1) + '%';
      html += '</div>';
      html += '<div class="grade-badge ' + gradeClass + '" style="margin-top:4px;">Grade ' + m.grade + '</div>';
      html += '</div>';
    });
    html += '</div>';
  } else {
    html += '<div class="card"><h2>TOP 5 Paris du jour</h2>';
    html += '<div style="color:#f85149; font-size:13px;">Aucun pari à EV positif. Pas de value bet détecté.</div>';
    html += '</div>';
  }

  // PORTEFEUILLE
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
    html += '<div class="k">Espérance :</div><div class="v" style="color:#3fb950;">+' + (portfolio.expected * 100).toFixed(2) + '%</div>';
    html += '<div class="k">Volatilité :</div><div class="v">' + (portfolio.volatility * 100).toFixed(2) + '%</div>';
    html += '<div class="k">Sharpe :</div><div class="v">' + portfolio.sharpe.toFixed(3) + '</div>';
    html += '</div></div>';
  }

  // À ÉVITER
  if (worst.length > 0) {
    html += '<div class="card"><h2>À éviter absolument</h2>';
    worst.forEach(m => {
      html += '<div style="padding:6px 0; border-bottom:1px solid #21262d; font-size:12px;">';
      html += '<span style="color:#f85149;">X</span> ';
      html += m.match_label + ' — <span style="color:#58a6ff;">' + m.market_id + '</span> ';
      html += '@ ' + m.odds.toFixed(2) + ' → EV <b style="color:#f85149;">' + (m.ev * 100).toFixed(1) + '%</b>';
      html += '</div>';
    });
    html += '<div class="mc-hint" style="margin-top:8px;">Marge book trop élevée ou probabilité modèle insuffisante.</div>';
    html += '</div>';
  }

  stage2.innerHTML = html;
}

