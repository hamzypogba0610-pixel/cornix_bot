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
  .warn-badge { display: inline-block; padding: 2px 8px;
    border-radius: 10px; font-size: 11px; font-weight: 600;
    background: #9e6a03; color: white; margin-left: 6px; }
  /* ===== MULTI-CORNER SECTION ===== */
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
  details.mc-section > *:not(summary):first-of-type { margin-top: 0; }
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
  .mc-csv-area { width: 100%; min-height: 120px;
    font-family: monospace; font-size: 12px;
    padding: 10px; line-height: 1.6; }
  .mc-actions { display: flex; gap: 8px; margin-top: 12px; }
  .mc-actions button { flex: 1; padding: 10px; font-size: 13px; }
  .mc-hint { font-size: 11px; color: #6e7681; margin-top: 8px;
    line-height: 1.5; }
  .mc-result-item { background: #0d1117; border: 1px solid #30363d;
    border-radius: 8px; padding: 12px; margin-bottom: 10px; }
  .mc-result-title { font-weight: 600; color: #58a6ff;
    margin-bottom: 6px; font-size: 13px; }
  .mc-result-detail { font-size: 12px; color: #8b949e; line-height: 1.7; }
  .mc-result-detail span { color: #e6edf3; }
  .mc-dist-bar { height: 8px; background: #30363d; border-radius: 4px;
    overflow: hidden; margin-top: 6px; position: relative; }
  .mc-dist-fill { height: 100%;
    background: linear-gradient(90deg, #1f6feb, #58a6ff, #238636); }
  .mc-dist-labels { display: flex; justify-content: space-between;
    font-size: 10px; color: #6e7681; margin-top: 2px; }
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

  <div class="footnote">
    Kelly-Bayesian Portfolio Engine — fusion bayésienne + dé-marginalisation + Kelly multi-actifs<br>
    Calibrateurs : corners (9154 paires) et buts (3327 paires) — Isotonic.
  </div>
</div>

<script>
"""
