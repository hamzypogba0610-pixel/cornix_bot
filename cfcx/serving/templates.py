FORM_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cornix — Multi-Corner 360 Ultimate</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div class="container">
  <h1>Cornix</h1>
  <p class="sub">Multi-Corner 360 Ultimate — Kelly-Bayesian Portfolio Engine</p>

  <form id="form" onsubmit="submitForm(event)">
    <div class="card">
      <h2>Match</h2>
      <label>Equipe 1 (domicile)</label>
      <input name="home" placeholder="Ex: Liverpool" required>
      <label>Equipe 2 (exterieur)</label>
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
      <h2>Options</h2>
      <label>Simulations Monte Carlo</label>
      <select name="n_simulations">
        <option value="2000">Rapide (2000)</option>
        <option value="5000" selected>Equilibre (5000)</option>
        <option value="10000">Precis (10000)</option>
      </select>
    </div>

    <button type="submit">ANALYSER LE MATCH</button>
  </form>

  <div id="result"></div>
  <div id="portfolio-section" style="display:none; margin-top:16px;">
    <button class="secondary" onclick="computePortfolio()">OPTIMISER LE PORTEFEUILLE</button>
    <div id="portfolio-result" style="margin-top:16px;"></div>
  </div>

  <details class="mc-section">
    <summary>Multi-Corner 360 — donnees mi-temps (optionnel)</summary>
    <p class="mc-hint" style="margin-top:0; margin-bottom:14px;">
      Fournis les corners 1re MT et 2e MT des derniers matchs.
      Le bot calcule MC1 = A1xA2, MC2 = B1xB2, Global = MC1+MC2
      et genere une distribution par Monte Carlo bivarie.
    </p>
    <div id="mc-forms"></div>
    <button type="button" class="tertiary" onclick="computeMultiCorner()">CALCULER MULTI-CORNER</button>
    <div id="mc-result" style="margin-top:14px;"></div>
  </details>

  <details class="mc-section" id="shadow-section">
    <summary>Cornix Shadow — carnet secret + calibration en ligne</summary>
    <p class="mc-hint" style="margin-top:0; margin-bottom:14px;">
      Enregistre tes analyses et leurs resultats. Le bot calcule son VRAI track record
      (win rate, ROI, ECE) et entraine une calibration Temperature Scaling en direct.
      Tout est stocke localement sur ton telephone.
    </p>
    <div style="display:flex; gap:8px; margin-bottom:14px;">
      <button type="button" class="tertiary" style="flex:1;" onclick="shadowSaveCurrent()">Enregistrer analyse</button>
      <button type="button" class="secondary" style="flex:1;" onclick="shadowExport()">Exporter JSON</button>
    </div>
    <div id="shadow-stats"></div>
  </details>

  <div class="footnote">
    Kelly-Bayesian Portfolio Engine — fusion bayesienne + de-marginalisation + Kelly multi-actifs<br>
    Calibrateurs : corners (9154 paires) et buts (3327 paires) — Isotonic.<br>
    Shadow + Online Temperature Scaling : calibration en continu.
  </div>
</div>
<script src="/static/app.js"></script>
</body>
</html>
"""
