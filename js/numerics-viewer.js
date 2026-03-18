/**
 * numerics-viewer.js  v0.6
 * Client-side viewer for Harbour Breakwater dossier.
 * Handles three data sources:
 *   1. Pre-computed HDF5 (via jsfive)
 *   2. Default simulation runs (JSON from data/runs/)
 *   3. User-uploaded JSON (from simulate.html)
 *
 * Dependencies (loaded in numerics.html): Plotly (CDN)
 */

/* ── Harbour palette ─────────────────────────────────────── */
const PALETTE = {
  bg_figure:  '#f2dcd6', bg_axes: '#faf3f0', grid: '#d4a99e',
  text: '#3a2520', text_muted: '#8c6e63', accent: '#a0453a', border: '#d4a99e',
  sigma_x: '#a0453a', sigma_y: '#3a5a8a', sigma_z: '#c08a20',
  coherence: '#3a2520', entropy: '#3a2520',
};

/* ── jsfive loader ───────────────────────────────────────── */
let jsfiveReady = false;
function loadJsfive() {
  return new Promise((resolve, reject) => {
    if (window.jsfive) { jsfiveReady = true; resolve(); return; }
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/jsfive@0.3.10/dist/browser/hdf5.js';
    s.onload = () => { jsfiveReady = true; resolve(); };
    s.onerror = () => reject(new Error('Failed to load jsfive'));
    document.head.appendChild(s);
  });
}

/* ── State ───────────────────────────────────────────────── */
let hdf5Manifest = [];
let runsManifest = [];
let activeCard = null;
let currentSource = 'hdf5';

/* ── Init ────────────────────────────────────────────────── */
async function init() {
  // Load HDF5 manifest
  try {
    const resp = await fetch('data/manifest.json');
    hdf5Manifest = await resp.json();
  } catch {
    hdf5Manifest = [
      { alpha: 0, label: 'Ground state', nbar: 0, path: 'data/alpha_0/detuning_scan.h5' },
      { alpha: 1, label: '⟨n⟩ = 1',     nbar: 1, path: 'data/alpha_1/detuning_scan.h5' },
      { alpha: 3, label: '⟨n⟩ = 9',     nbar: 9, path: 'data/alpha_3/detuning_scan.h5' },
      { alpha: 5, label: '⟨n⟩ = 25',    nbar: 25, path: 'data/alpha_5/detuning_scan.h5' },
    ];
  }
  renderGrid('hdf5', hdf5Manifest);

  // Load runs manifest
  try {
    const resp2 = await fetch('data/runs/manifest.json');
    const rm = await resp2.json();
    runsManifest = rm.runs || [];
  } catch {
    runsManifest = [];
  }
  renderGrid('runs', runsManifest);

  await loadJsfive();
}

function renderGrid(type, items) {
  const gridId = type === 'hdf5' ? 'dataset-grid-hdf5' : 'dataset-grid-runs';
  const grid = document.getElementById(gridId);
  if (!grid) return;
  grid.innerHTML = '';
  items.forEach((ds, i) => {
    const card = document.createElement('div');
    card.className = 'dataset-card';
    const alpha = ds.alpha !== undefined ? ds.alpha : '?';
    const label = ds.label || `α = ${alpha}`;
    card.innerHTML = `
      <div class="dc-alpha">α = ${alpha}</div>
      <div class="dc-label">${label}</div>
    `;
    card.addEventListener('click', () => {
      if (type === 'hdf5') selectHDF5(i, card);
      else selectRun(i, card);
    });
    grid.appendChild(card);
  });
}

/* ── Source switching ─────────────────────────────────────── */
window.switchSource = function(src) {
  currentSource = src;
  ['hdf5', 'runs', 'upload'].forEach(s => {
    const panel = document.getElementById('panel-' + s);
    const tab = document.getElementById('tab-' + s);
    if (panel) panel.style.display = s === src ? 'block' : 'none';
    if (tab) tab.style.borderWidth = s === src ? '2px' : '1px';
  });
};

/* ── HDF5 selection ──────────────────────────────────────── */
async function selectHDF5(idx, card) {
  setActiveCard(card);
  const ds = hdf5Manifest[idx];
  setStatus('sigma', 'Loading ' + ds.path + ' …');
  setStatus('entropy', '');
  hideConvInfo();
  try {
    const buf = await fetchBinary(ds.path);
    const data = parseHDF5(buf);
    plotData(data, ds);
    showMeta([['α', ds.alpha], ['⟨n⟩', ds.nbar]], data.attrs);
    showDownload(ds.path, ds.path.split('/').pop());
  } catch (e) {
    setStatus('sigma', 'Error: ' + e.message);
  }
}

/* ── JSON run selection ──────────────────────────────────── */
async function selectRun(idx, card) {
  setActiveCard(card);
  const ds = runsManifest[idx];
  setStatus('sigma', 'Loading ' + ds.path + ' …');
  setStatus('entropy', '');
  try {
    const resp = await fetch(ds.path);
    const json = await resp.json();
    plotJSON(json, ds);
  } catch (e) {
    setStatus('sigma', 'Error: ' + e.message);
  }
}

/* ── Upload handling ─────────────────────────────────────── */
window.handleUpload = function(event) {
  const file = event.target.files[0];
  if (!file) return;
  setStatus('sigma', 'Reading ' + file.name + ' …');
  setStatus('entropy', '');
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const json = JSON.parse(e.target.result);
      plotJSON(json, { label: file.name });
    } catch (err) {
      setStatus('sigma', 'Error parsing JSON: ' + err.message);
    }
  };
  reader.readAsText(file);
};

/* ── Plot JSON data (from runs or upload) ────────────────── */
function plotJSON(json, ds) {
  const d = json.data;
  const m = json.manifest || {};
  const p = m.parameters || {};

  if (!d || !d.detuning || !d.sigma_x) {
    setStatus('sigma', 'Invalid JSON: missing data.detuning or data.sigma_x');
    return;
  }

  const data = {
    detuning:  d.detuning,
    sigma_x:   d.sigma_x,
    sigma_y:   d.sigma_y,
    sigma_z:   d.sigma_z,
    entropy:   d.entropy,
    coherence: d.coherence,
    noisy_sigma_x: d.noisy_sigma_x,
    noisy_sigma_y: d.noisy_sigma_y,
    noisy_sigma_z: d.noisy_sigma_z,
    err_sigma_x: d.err_sigma_x,
    err_sigma_y: d.err_sigma_y,
    err_sigma_z: d.err_sigma_z,
  };

  const hasNoise = data.noisy_sigma_x && data.noisy_sigma_x.length > 0 && (p.n_rep > 0);

  plotDataUnified(data, hasNoise, p.n_rep || 0);

  // Convergence info
  const conv = m.convergence;
  if (conv) showConvInfo(conv);
  else hideConvInfo();

  // Metadata
  const items = [];
  if (p.alpha !== undefined) items.push(['α', p.alpha]);
  if (p.eta)    items.push(['η', p.eta]);
  if (p.omega_m) items.push(['ω_m/(2π)', p.omega_m + ' MHz']);
  if (p.nmax)   items.push(['N_max', p.nmax]);
  if (p.n_pulses) items.push(['Pulses', p.n_pulses]);
  if (conv) items.push(['Leakage', (conv.max_fock_leakage * 100).toFixed(4) + '%']);
  if (p.T1 > 0) items.push(['T₁', p.T1 + ' μs']);
  if (p.T2 > 0) items.push(['T₂', p.T2 + ' μs']);
  if (p.heating > 0) items.push(['dn/dt', p.heating + ' q/ms']);
  if (p.n_rep > 0) items.push(['N_rep', p.n_rep]);
  if (m.provenance_hash) items.push(['Hash', m.provenance_hash.substring(0, 12) + '…']);

  showMetaDirect(items);

  // Download as JSON blob
  const blob = new Blob([JSON.stringify(json, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  showDownload(url, 'simulation_results.json');
}

/* ── Convergence display ─────────────────────────────────── */
function showConvInfo(conv) {
  const el = document.getElementById('run-conv-info') || document.getElementById('upload-conv-info');
  if (!el) return;
  const pct = (conv.max_fock_leakage * 100).toFixed(3);
  if (conv.converged) {
    el.style.background = '#e4f2e4'; el.style.color = '#4a7a4a';
    el.textContent = `✓ Converged — boundary population: ${pct}%`;
  } else {
    el.style.background = '#fce4e4'; el.style.color = '#a04040';
    el.textContent = `✗ Not converged — boundary population: ${pct}%. Increase N_max.`;
  }
  el.style.display = 'block';
  // Also show in the other panel's info area
  const other = el.id === 'run-conv-info' ? document.getElementById('upload-conv-info') : document.getElementById('run-conv-info');
  if (other) other.style.display = 'none';
}
function hideConvInfo() {
  ['run-conv-info', 'upload-conv-info'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });
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

async function fetchBinary(path) {
  const resp = await fetch(path);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.arrayBuffer();
}

function parseHDF5(buf) {
  if (!jsfiveReady) throw new Error('HDF5 library not loaded');
  const f = new jsfive.File(buf);
  function read(name) { const ds = f.get(name); return ds ? ds.value : null; }
  const detuning = read('detuning') || read('scan/detuning');
  const sigma_x  = read('sigma_x')  || read('scan/sigma_x');
  const sigma_y  = read('sigma_y')  || read('scan/sigma_y');
  const sigma_z  = read('sigma_z')  || read('scan/sigma_z');
  const entropy  = read('entropy')  || read('scan/entropy');
  let coherence  = read('coherence') || read('scan/coherence');
  if (!detuning || !sigma_x) throw new Error('Required datasets not found');
  if (!coherence && sigma_x && sigma_y && sigma_z) {
    coherence = new Float64Array(detuning.length);
    for (let i = 0; i < detuning.length; i++)
      coherence[i] = Math.sqrt(sigma_x[i]**2 + sigma_y[i]**2 + sigma_z[i]**2);
  }
  const attrs = {};
  if (f.attrs) for (const [k, v] of Object.entries(f.attrs)) attrs[k] = v;
  return { detuning, sigma_x, sigma_y, sigma_z, entropy, coherence, attrs };
}

/* ── Plotly rendering ────────────────────────────────────── */
const PLOTLY_LAYOUT = {
  paper_bgcolor: PALETTE.bg_figure, plot_bgcolor: PALETTE.bg_axes,
  font: { family: 'Source Serif 4, Georgia, serif', color: PALETTE.text, size: 13 },
  margin: { l: 56, r: 20, t: 8, b: 4 },
  xaxis: { gridcolor: PALETTE.grid, gridwidth: 0.6, linecolor: PALETTE.border, linewidth: 0.7,
           tickfont: { size: 11, color: PALETTE.text_muted }, zeroline: false },
  yaxis: { gridcolor: PALETTE.grid, gridwidth: 0.6, linecolor: PALETTE.border, linewidth: 0.7,
           tickfont: { size: 11, color: PALETTE.text_muted }, zeroline: false },
  showlegend: true,
  legend: { bgcolor: PALETTE.bg_axes, bordercolor: PALETTE.border, borderwidth: 1,
            font: { size: 11 }, x: 1, xanchor: 'right', y: 1, yanchor: 'top' },
};

function traceStyle(color) {
  return { mode: 'lines+markers', line: { color, width: 1.2 },
           marker: { color, size: 3, line: { width: 0 } } };
}

function contrast(arr) {
  const a = Array.from(arr);
  const mn = Math.min(...a), mx = Math.max(...a);
  return ((mx - mn) / 2).toFixed(2);
}

/* Plot HDF5 data (original format) */
function plotData(data, ds) {
  plotDataUnified({
    detuning: data.detuning, sigma_x: data.sigma_x, sigma_y: data.sigma_y,
    sigma_z: data.sigma_z, entropy: data.entropy, coherence: data.coherence,
  }, false, 0);
}

/* Unified plotter for both HDF5 and JSON */
function plotDataUnified(data, hasNoise, nrep) {
  const xs = Array.from(data.detuning);

  const traces = [];
  const map = [
    ['sigma_x', PALETTE.sigma_x, 'σₓ'],
    ['sigma_y', PALETTE.sigma_y, 'σᵧ'],
    ['sigma_z', PALETTE.sigma_z, 'σ_z'],
  ];

  for (const [key, color, label] of map) {
    if (!data[key]) continue;
    const arr = Array.from(data[key]);
    traces.push({
      x: xs, y: arr,
      name: `${label}  C=${contrast(arr)}${hasNoise ? ' (ideal)' : ''}`,
      mode: hasNoise ? 'lines' : 'lines+markers',
      line: { color, width: hasNoise ? 1.0 : 1.2, dash: hasNoise ? 'dot' : 'solid' },
      marker: hasNoise ? undefined : { color, size: 3, line: { width: 0 } },
    });
    if (hasNoise && data['noisy_' + key]) {
      traces.push({
        x: xs, y: Array.from(data['noisy_' + key]),
        error_y: data['err_' + key] ? {
          type: 'data', array: Array.from(data['err_' + key]),
          visible: true, color, thickness: 0.8, width: 2,
        } : undefined,
        name: `${label} (N=${nrep})`,
        mode: 'markers', marker: { color, size: 3, opacity: 0.7 },
      });
    }
  }

  if (data.coherence) {
    traces.push({
      x: xs, y: Array.from(data.coherence), name: 'Coherence',
      ...traceStyle(PALETTE.coherence),
      line: { ...traceStyle(PALETTE.coherence).line, dash: 'dot' },
    });
  }

  const layoutS = {
    ...PLOTLY_LAYOUT,
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: { text: '⟨σᵢ⟩', font: { size: 13 } }, range: [-1.08, 1.08] },
    xaxis: { ...PLOTLY_LAYOUT.xaxis, title: '' },
    height: hasNoise ? 380 : 320,
  };

  const plotDiv = document.getElementById('plot-sigma');
  plotDiv.innerHTML = '';
  Plotly.newPlot(plotDiv, traces, layoutS, { responsive: true, displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'] });

  // Entropy
  if (data.entropy) {
    const tracesE = [{ x: xs, y: Array.from(data.entropy), name: 'Entropy', ...traceStyle(PALETTE.entropy) }];
    const layoutE = {
      ...PLOTLY_LAYOUT,
      yaxis: { ...PLOTLY_LAYOUT.yaxis, title: { text: 'Entropy', font: { size: 13 } }, rangemode: 'tozero' },
      xaxis: { ...PLOTLY_LAYOUT.xaxis, title: { text: 'Detuning  (2π ω_LF)', font: { size: 13 } } },
      height: 180, showlegend: false, margin: { l: 56, r: 20, t: 4, b: 40 },
    };
    const entropyDiv = document.getElementById('plot-entropy');
    entropyDiv.innerHTML = '';
    Plotly.newPlot(entropyDiv, tracesE, layoutE, { responsive: true, displayModeBar: false });
  }
}

/* ── Metadata readout ────────────────────────────────────── */
function showMeta(items, attrs) {
  const extra = [];
  if (attrs) {
    if (attrs.eta) extra.push(['η', attrs.eta]);
    if (attrs.omega_rabi) extra.push(['Ω/(2π)', attrs.omega_rabi + ' MHz']);
  }
  showMetaDirect([...items, ...extra]);
}

function showMetaDirect(items) {
  const div = document.getElementById('meta-readout');
  div.innerHTML = items.map(
    ([k, v]) => `<span class="meta-item"><span class="meta-key">${k}:</span> ${v}</span>`
  ).join('');
  div.style.display = 'flex';
}

/* ── Download link ───────────────────────────────────────── */
function showDownload(href, filename) {
  const area = document.getElementById('download-area');
  const link = document.getElementById('download-link');
  link.href = href;
  link.download = filename;
  area.style.display = 'block';
}

/* ── Boot ────────────────────────────────────────────────── */
init();
