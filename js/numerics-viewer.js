/**
 * numerics-viewer.js  v0.7
 * JSON-only viewer for simulation results.
 * Sources: default runs (data/runs/) and user uploads.
 */

const PALETTE = {
  bg_figure: '#f2dcd6', bg_axes: '#faf3f0', grid: '#d4a99e',
  text: '#3a2520', text_muted: '#8c6e63', accent: '#a0453a', border: '#d4a99e',
  sigma_x: '#a0453a', sigma_y: '#3a5a8a', sigma_z: '#c08a20',
  coherence: '#3a2520', entropy: '#3a2520',
};

let runsManifest = [];
let activeCard = null;

/* ── Init ────────────────────────────────────────────────── */
async function init() {
  try {
    const resp = await fetch('data/runs/manifest.json');
    const rm = await resp.json();
    runsManifest = rm.runs || [];
  } catch (e) {
    console.warn('Could not load runs manifest:', e);
    runsManifest = [];
  }
  renderGrid();

  // Wire upload
  document.getElementById('finput').addEventListener('change', handleUpload);
}

function renderGrid() {
  const grid = document.getElementById('grid-runs');
  if (!grid) return;
  grid.innerHTML = '';
  runsManifest.forEach((ds, i) => {
    const card = document.createElement('div');
    card.className = 'dataset-card';
    card.innerHTML = `
      <div class="dc-alpha">α = ${ds.alpha}</div>
      <div class="dc-label">${ds.label || 'α = ' + ds.alpha}</div>
    `;
    card.addEventListener('click', () => selectRun(i, card));
    grid.appendChild(card);
  });
}

/* ── Source switching ─────────────────────────────────────── */
window.switchSource = function(src) {
  document.getElementById('panel-runs').style.display = src === 'runs' ? 'block' : 'none';
  document.getElementById('panel-upload').style.display = src === 'upload' ? 'block' : 'none';
  document.getElementById('tab-runs').style.borderWidth = src === 'runs' ? '2px' : '1px';
  document.getElementById('tab-runs').classList.toggle('active', src === 'runs');
  document.getElementById('tab-upload').style.borderWidth = src === 'upload' ? '2px' : '1px';
  document.getElementById('tab-upload').classList.toggle('active', src === 'upload');
};

/* ── Run selection ───────────────────────────────────────── */
async function selectRun(idx, card) {
  setActiveCard(card);
  const ds = runsManifest[idx];
  setStatus('sigma', 'Loading ' + ds.path + '…');
  setStatus('entropy', '');
  try {
    const resp = await fetch(ds.path);
    const json = await resp.json();
    plotJSON(json);
  } catch (e) {
    setStatus('sigma', 'Error: ' + e.message);
  }
}

/* ── Upload ──────────────────────────────────────────────── */
function handleUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  setStatus('sigma', 'Reading ' + file.name + '…');
  setStatus('entropy', '');
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const json = JSON.parse(e.target.result);
      plotJSON(json);
    } catch (err) {
      setStatus('sigma', 'Error parsing JSON: ' + err.message);
    }
  };
  reader.readAsText(file);
}

/* ── Plot JSON ───────────────────────────────────────────── */
function plotJSON(json) {
  const d = json.data;
  const m = json.manifest || {};
  const p = m.parameters || {};

  if (!d || !d.detuning || !d.sigma_x) {
    setStatus('sigma', 'Invalid JSON: missing data arrays.');
    return;
  }

  const hasNoise = d.noisy_sigma_x && d.noisy_sigma_x.length > 0 && (p.n_rep > 0);

  plotData(d, hasNoise, p.n_rep || 0);

  // Convergence
  const conv = m.convergence;
  if (conv) showConvInfo(conv);
  else hideConvInfo();

  // Metadata
  const items = [];
  if (p.alpha !== undefined) items.push(['α', p.alpha]);
  if (p.eta) items.push(['η', p.eta]);
  if (p.omega_m) items.push(['ω_m', p.omega_m + ' MHz']);
  if (p.nmax) items.push(['N_max', p.nmax]);
  if (p.n_pulses) items.push(['Pulses', p.n_pulses]);
  if (conv) items.push(['Leakage', (conv.max_fock_leakage * 100).toFixed(4) + '%']);
  if (p.T1 > 0) items.push(['T₁', p.T1 + ' μs']);
  if (p.T2 > 0) items.push(['T₂', p.T2 + ' μs']);
  if (p.heating > 0) items.push(['dn/dt', p.heating + ' q/ms']);
  if (p.n_rep > 0) items.push(['N_rep', p.n_rep]);
  if (m.provenance_hash) items.push(['Hash', m.provenance_hash.substring(0, 12) + '…']);
  showMetaDirect(items);

  // Download link
  const blob = new Blob([JSON.stringify(json, null, 2)], { type: 'application/json' });
  showDownload(URL.createObjectURL(blob), 'simulation_results.json');
}

/* ── Convergence display ─────────────────────────────────── */
function showConvInfo(conv) {
  const el = document.getElementById('conv-info');
  if (!el) return;
  const pct = (conv.max_fock_leakage * 100).toFixed(3);
  if (conv.converged) {
    el.style.background = '#e4f2e4'; el.style.color = '#4a7a4a';
    el.textContent = '✓ Converged — boundary population: ' + pct + '%';
  } else {
    el.style.background = '#fce4e4'; el.style.color = '#a04040';
    el.textContent = '✗ Not converged — boundary population: ' + pct + '%. Increase N_max.';
  }
  el.style.display = 'block';
}

function hideConvInfo() {
  const el = document.getElementById('conv-info');
  if (el) el.style.display = 'none';
}

/* ── Helpers ──────────────────────────────────────────────── */
function setActiveCard(card) {
  if (activeCard) activeCard.classList.remove('active');
  card.classList.add('active');
  activeCard = card;
}

function setStatus(panel, msg) {
  const el = document.getElementById('status-' + panel);
  if (el) el.textContent = msg;
}

/* ── Plotly ───────────────────────────────────────────────── */
const LY = {
  paper_bgcolor: PALETTE.bg_figure, plot_bgcolor: PALETTE.bg_axes,
  font: { family: 'Source Serif 4, Georgia, serif', color: PALETTE.text, size: 13 },
  margin: { l: 56, r: 20, t: 8, b: 4 },
  xaxis: { gridcolor: PALETTE.grid, gridwidth: 0.6, linecolor: PALETTE.border,
           linewidth: 0.7, tickfont: { size: 11, color: PALETTE.text_muted }, zeroline: false },
  yaxis: { gridcolor: PALETTE.grid, gridwidth: 0.6, linecolor: PALETTE.border,
           linewidth: 0.7, tickfont: { size: 11, color: PALETTE.text_muted }, zeroline: false },
  showlegend: true,
  legend: { bgcolor: PALETTE.bg_axes, bordercolor: PALETTE.border, borderwidth: 1,
            font: { size: 11 }, x: 1, xanchor: 'right', y: 1, yanchor: 'top' },
};

function contrast(arr) {
  const mn = Math.min(...arr), mx = Math.max(...arr);
  return ((mx - mn) / 2).toFixed(2);
}

function plotData(data, hasNoise, nrep) {
  const xs = data.detuning;
  const traces = [];
  const map = [
    ['sigma_x', PALETTE.sigma_x, 'σₓ'],
    ['sigma_y', PALETTE.sigma_y, 'σᵧ'],
    ['sigma_z', PALETTE.sigma_z, 'σ_z'],
  ];

  for (const [key, color, label] of map) {
    if (!data[key]) continue;
    traces.push({
      x: xs, y: data[key],
      name: label + '  C=' + contrast(data[key]) + (hasNoise ? ' (ideal)' : ''),
      mode: hasNoise ? 'lines' : 'lines+markers',
      line: { color, width: hasNoise ? 1.0 : 1.2, dash: hasNoise ? 'dot' : 'solid' },
      marker: hasNoise ? undefined : { color, size: 3 },
    });
    if (hasNoise && data['noisy_' + key]) {
      traces.push({
        x: xs, y: data['noisy_' + key],
        error_y: data['err_' + key] ? {
          type: 'data', array: data['err_' + key],
          visible: true, color, thickness: 0.8, width: 2
        } : undefined,
        name: label + ' (N=' + nrep + ')',
        mode: 'markers', marker: { color, size: 3, opacity: 0.7 },
      });
    }
  }

  if (data.coherence) {
    traces.push({
      x: xs, y: data.coherence, name: 'Coherence',
      mode: 'lines+markers', line: { color: PALETTE.coherence, width: 1.2, dash: 'dot' },
      marker: { color: PALETTE.coherence, size: 3 },
    });
  }

  const plotDiv = document.getElementById('plot-sigma');
  plotDiv.innerHTML = '';
  Plotly.newPlot(plotDiv, traces, {
    ...LY,
    yaxis: { ...LY.yaxis, title: { text: '⟨σᵢ⟩', font: { size: 13 } }, range: [-1.08, 1.08] },
    xaxis: { ...LY.xaxis, title: '' },
    height: hasNoise ? 380 : 320,
  }, { responsive: true, displayModeBar: true, modeBarButtonsToRemove: ['lasso2d', 'select2d'] });

  // Entropy
  const entropyDiv = document.getElementById('plot-entropy');
  entropyDiv.innerHTML = '';
  if (data.entropy) {
    Plotly.newPlot(entropyDiv,
      [{ x: xs, y: data.entropy, name: 'Entropy', mode: 'lines+markers',
         line: { color: PALETTE.entropy, width: 1.2 },
         marker: { color: PALETTE.entropy, size: 3 } }],
      { ...LY,
        yaxis: { ...LY.yaxis, title: { text: 'Entropy', font: { size: 13 } }, rangemode: 'tozero' },
        xaxis: { ...LY.xaxis, title: { text: 'Detuning (ω_m)', font: { size: 13 } } },
        height: 180, showlegend: false, margin: { l: 56, r: 20, t: 4, b: 40 },
      }, { responsive: true, displayModeBar: false });
  }
}

function showMetaDirect(items) {
  const div = document.getElementById('meta-readout');
  div.innerHTML = items.map(
    ([k, v]) => '<span class="meta-item"><span class="meta-key">' + k + ':</span> ' + v + '</span>'
  ).join('');
  div.style.display = 'flex';
}

function showDownload(href, filename) {
  const area = document.getElementById('download-area');
  const link = document.getElementById('download-link');
  link.href = href;
  link.download = filename;
  area.style.display = 'block';
}

/* ── Boot ────────────────────────────────────────────────── */
init();
