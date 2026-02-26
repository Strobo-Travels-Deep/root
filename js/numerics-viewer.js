/**
 * numerics-viewer.js
 * Client-side HDF5 viewer for Harbour Breakwater dossier.
 *
 * Dependencies (loaded in numerics.html):
 *   - Plotly  (CDN)
 *   - jsfive  (loaded dynamically below)
 *
 * Data contract:
 *   data/manifest.json  — array of dataset descriptors
 *   data/alpha_N/detuning_scan.h5 — HDF5 files with datasets:
 *     detuning, sigma_x, sigma_y, sigma_z, entropy, coherence
 *     + root-group attributes for metadata
 */

/* ── Harbour palette for Plotly ─────────────────────────────── */
const PALETTE = {
  bg_figure:  '#f2dcd6',
  bg_axes:    '#faf3f0',
  grid:       '#d4a99e',
  text:       '#3a2520',
  text_muted: '#8c6e63',
  accent:     '#a0453a',
  border:     '#d4a99e',
  sigma_x:    '#a0453a',
  sigma_y:    '#3a5a8a',
  sigma_z:    '#c08a20',
  coherence:  '#3a2520',
  entropy:    '#3a2520',
};

/* ── jsfive loader ──────────────────────────────────────────── */
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

/* ── Manifest & state ───────────────────────────────────────── */
let manifest = [];
let activeCard = null;

async function init() {
  try {
    const resp = await fetch('data/manifest.json');
    manifest = await resp.json();
  } catch {
    /* fallback: default set */
    manifest = [
      { alpha: 0, label: 'Ground state',  nbar: 0,  path: 'data/alpha_0/detuning_scan.h5' },
      { alpha: 1, label: '⟨n⟩ = 1',       nbar: 1,  path: 'data/alpha_1/detuning_scan.h5' },
      { alpha: 3, label: '⟨n⟩ = 9',       nbar: 9,  path: 'data/alpha_3/detuning_scan.h5' },
      { alpha: 5, label: '⟨n⟩ = 25',      nbar: 25, path: 'data/alpha_5/detuning_scan.h5' },
    ];
  }
  renderGrid();
  await loadJsfive();
}

function renderGrid() {
  const grid = document.getElementById('dataset-grid');
  grid.innerHTML = '';
  manifest.forEach((ds, i) => {
    const card = document.createElement('div');
    card.className = 'dataset-card';
    card.innerHTML = `
      <div class="dc-alpha">α = ${ds.alpha}</div>
      <div class="dc-label">${ds.label}</div>
    `;
    card.addEventListener('click', () => selectDataset(i, card));
    grid.appendChild(card);
  });
}

/* ── Dataset selection ──────────────────────────────────────── */
async function selectDataset(idx, card) {
  if (activeCard) activeCard.classList.remove('active');
  card.classList.add('active');
  activeCard = card;

  const ds = manifest[idx];
  setStatus('sigma',   'Loading ' + ds.path + ' …');
  setStatus('entropy', '');

  try {
    const buf = await fetchHDF5(ds.path);
    const data = parseHDF5(buf);
    plotData(data, ds);
    showMeta(data.attrs, ds);
    showDownload(ds.path);
  } catch (e) {
    setStatus('sigma', 'Error: ' + e.message);
    console.error(e);
  }
}

function setStatus(panel, msg) {
  const el = document.getElementById('status-' + panel);
  if (el) el.textContent = msg;
}

/* ── Fetch HDF5 ─────────────────────────────────────────────── */
async function fetchHDF5(path) {
  const resp = await fetch(path);
  if (!resp.ok) throw new Error(`HTTP ${resp.status} fetching ${path}`);
  return await resp.arrayBuffer();
}

/* ── Parse HDF5 with jsfive ─────────────────────────────────── */
function parseHDF5(buf) {
  if (!jsfiveReady) throw new Error('HDF5 library not loaded');
  const f = new jsfive.File(buf);

  function read(name) {
    const ds = f.get(name);
    if (!ds) return null;
    return ds.value;  /* Float64Array or similar */
  }

  /* Try root-level datasets first, then scan/ group */
  const detuning  = read('detuning')  || read('scan/detuning');
  const sigma_x   = read('sigma_x')   || read('scan/sigma_x');
  const sigma_y   = read('sigma_y')   || read('scan/sigma_y');
  const sigma_z   = read('sigma_z')   || read('scan/sigma_z');
  const entropy   = read('entropy')   || read('scan/entropy');
  let   coherence = read('coherence')  || read('scan/coherence');

  if (!detuning || !sigma_x) throw new Error('Required datasets not found in HDF5');

  /* Compute coherence if missing */
  if (!coherence && sigma_x && sigma_y && sigma_z) {
    coherence = new Float64Array(detuning.length);
    for (let i = 0; i < detuning.length; i++) {
      coherence[i] = Math.sqrt(
        sigma_x[i]**2 + sigma_y[i]**2 + sigma_z[i]**2
      );
    }
  }

  /* Read attributes */
  const attrs = {};
  if (f.attrs) {
    for (const [k, v] of Object.entries(f.attrs)) {
      attrs[k] = v;
    }
  }

  return { detuning, sigma_x, sigma_y, sigma_z, entropy, coherence, attrs };
}

/* ── Plotly rendering ───────────────────────────────────────── */
const PLOTLY_LAYOUT_BASE = {
  paper_bgcolor: PALETTE.bg_figure,
  plot_bgcolor:  PALETTE.bg_axes,
  font: { family: 'Source Serif 4, Georgia, serif', color: PALETTE.text, size: 13 },
  margin: { l: 56, r: 20, t: 8, b: 4 },
  xaxis: {
    gridcolor: PALETTE.grid, gridwidth: 0.6,
    linecolor: PALETTE.border, linewidth: 0.7,
    tickfont: { size: 11, color: PALETTE.text_muted },
    zeroline: false,
  },
  yaxis: {
    gridcolor: PALETTE.grid, gridwidth: 0.6,
    linecolor: PALETTE.border, linewidth: 0.7,
    tickfont: { size: 11, color: PALETTE.text_muted },
    zeroline: false,
  },
  showlegend: true,
  legend: {
    bgcolor: PALETTE.bg_axes, bordercolor: PALETTE.border, borderwidth: 1,
    font: { size: 11 },
    x: 1, xanchor: 'right', y: 1, yanchor: 'top',
  },
};

function traceStyle(color) {
  return {
    mode: 'lines+markers',
    line: { color, width: 1.2 },
    marker: { color, size: 3, line: { width: 0 } },
  };
}

function plotData(data, ds) {
  /* ── σ traces ────────────────────────────────────────────── */
  const xs = Array.from(data.detuning);

  function contrast(arr) {
    const mn = Math.min(...arr), mx = Math.max(...arr);
    return ((mx - mn) / 2).toFixed(2);
  }

  const traces = [
    { x: xs, y: Array.from(data.sigma_x),  name: `σₓ  C=${contrast(data.sigma_x)}`, ...traceStyle(PALETTE.sigma_x) },
    { x: xs, y: Array.from(data.sigma_y),  name: `σᵧ  C=${contrast(data.sigma_y)}`, ...traceStyle(PALETTE.sigma_y) },
    { x: xs, y: Array.from(data.sigma_z),  name: `σ_z  C=${contrast(data.sigma_z)}`, ...traceStyle(PALETTE.sigma_z) },
  ];
  if (data.coherence) {
    traces.push({
      x: xs, y: Array.from(data.coherence), name: 'Coherence', ...traceStyle(PALETTE.coherence),
      line: { ...traceStyle(PALETTE.coherence).line, dash: 'dot' },
    });
  }

  const layoutSigma = {
    ...PLOTLY_LAYOUT_BASE,
    yaxis: {
      ...PLOTLY_LAYOUT_BASE.yaxis,
      title: { text: '⟨σᵢ⟩', font: { size: 13 } },
      range: [-1.08, 1.08],
    },
    xaxis: { ...PLOTLY_LAYOUT_BASE.xaxis, title: '' },
    height: 320,
  };

  const plotDiv = document.getElementById('plot-sigma');
  plotDiv.innerHTML = '';
  Plotly.newPlot(plotDiv, traces, layoutSigma, { responsive: true, displayModeBar: false });

  /* ── Entropy ─────────────────────────────────────────────── */
  if (data.entropy) {
    const tracesE = [{
      x: xs, y: Array.from(data.entropy), name: 'Entropy',
      ...traceStyle(PALETTE.entropy),
    }];
    const layoutE = {
      ...PLOTLY_LAYOUT_BASE,
      yaxis: {
        ...PLOTLY_LAYOUT_BASE.yaxis,
        title: { text: 'Entropy', font: { size: 13 } },
        rangemode: 'tozero',
      },
      xaxis: {
        ...PLOTLY_LAYOUT_BASE.xaxis,
        title: { text: 'Detuning  (2π ω_LF)', font: { size: 13 } },
      },
      height: 180,
      showlegend: false,
      margin: { l: 56, r: 20, t: 4, b: 40 },
    };

    const entropyDiv = document.getElementById('plot-entropy');
    entropyDiv.innerHTML = '';
    Plotly.newPlot(entropyDiv, tracesE, layoutE, { responsive: true, displayModeBar: false });
  }
}

/* ── Metadata readout ───────────────────────────────────────── */
function showMeta(attrs, ds) {
  const div = document.getElementById('meta-readout');
  const items = [
    ['α', ds.alpha],
    ['⟨n⟩', ds.nbar],
  ];
  if (attrs.eta)         items.push(['η', attrs.eta]);
  if (attrs.omega_rabi)  items.push(['Ω/(2π)', attrs.omega_rabi + ' MHz']);
  if (attrs.contrast_z !== undefined) items.push(['C(σ_z)', attrs.contrast_z]);

  div.innerHTML = items.map(
    ([k, v]) => `<span class="meta-item"><span class="meta-key">${k}:</span> ${v}</span>`
  ).join('');
  div.style.display = 'flex';
}

/* ── Download link ──────────────────────────────────────────── */
function showDownload(path) {
  const area = document.getElementById('download-area');
  const link = document.getElementById('download-link');
  link.href = path;
  link.download = path.split('/').pop();
  area.style.display = 'block';
}

/* ── Boot ────────────────────────────────────────────────────── */
init();
