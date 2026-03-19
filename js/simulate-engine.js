/**
 * simulate-engine.js  v0.8
 * Stroboscopic detuning-scan simulation engine.
 * Includes: squeeze operator, thermal state sampling, complex displacement,
 *           tunable spin state, quantum trajectories, GPU acceleration.
 */
"use strict";

const PAL = {
  bg: '#fcfcfb', bg_axes: '#fafaf8', grid: '#e0e0de', text: '#333',
  text_muted: '#999', border: '#ddd',
  sigma_x: '#c0453a', sigma_y: '#3a6a9a', sigma_z: '#c09020',
  coherence: '#444', entropy: '#666',
};
const VER = '0.8.0';
const REPO = 'https://github.com/threehouse-plus-ec/open-research-platform';
let lastResult = null, lastHash = null;

// ═══════════════════════════════════════════════════════════
// GPU
// ═══════════════════════════════════════════════════════════
let gpuDevice = null, gpuAvailable = false, gpuPipeline = null, gpuBGL = null;

async function initGPU() {
  try {
    if (!navigator.gpu) return;
    const a = await navigator.gpu.requestAdapter();
    if (!a) return;
    gpuDevice = await a.requestDevice();
    gpuAvailable = true;
    document.getElementById('gpu-badge').textContent = 'WebGPU';
    document.getElementById('gpu-badge').className = 'gpu-badge on';
  } catch (e) { /* no GPU */ }
}
initGPU();

const WGSL = `
struct P{n:u32}
@group(0)@binding(0) var<uniform> p:P;
@group(0)@binding(1) var<storage,read> A:array<f32>;
@group(0)@binding(2) var<storage,read> B:array<f32>;
@group(0)@binding(3) var<storage,read_write> C:array<f32>;
@compute @workgroup_size(8,8) fn main(@builtin(global_invocation_id) g:vec3u){
  let i=g.x;let j=g.y;let n=p.n;if(i>=n||j>=n){return;}
  var re:f32=0.0;var im:f32=0.0;
  for(var k:u32=0;k<n;k=k+1){let ai=2u*(i*n+k);let bi=2u*(k*n+j);
    re+=A[ai]*B[bi]-A[ai+1u]*B[bi+1u];im+=A[ai]*B[bi+1u]+A[ai+1u]*B[bi];}
  let ci=2u*(i*n+j);C[ci]=re;C[ci+1u]=im;}`;

async function initPipeline() {
  if (!gpuDevice || gpuPipeline) return;
  const mod = gpuDevice.createShaderModule({ code: WGSL });
  gpuBGL = gpuDevice.createBindGroupLayout({ entries: [
    { binding: 0, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'uniform' } },
    { binding: 1, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'read-only-storage' } },
    { binding: 2, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'read-only-storage' } },
    { binding: 3, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
  ] });
  gpuPipeline = gpuDevice.createComputePipeline({
    layout: gpuDevice.createPipelineLayout({ bindGroupLayouts: [gpuBGL] }),
    compute: { module: mod, entryPoint: 'main' },
  });
}

async function gpuMM(A64, B64, n) {
  const sz = 2 * n * n, bl = sz * 4;
  const Af = new Float32Array(sz), Bf = new Float32Array(sz);
  for (let i = 0; i < sz; i++) { Af[i] = A64[i]; Bf[i] = B64[i]; }
  const pb = gpuDevice.createBuffer({ size: 4, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
  gpuDevice.queue.writeBuffer(pb, 0, new Uint32Array([n]));
  const ab = gpuDevice.createBuffer({ size: bl, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST });
  const bb = gpuDevice.createBuffer({ size: bl, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST });
  const cb = gpuDevice.createBuffer({ size: bl, usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC });
  const rb = gpuDevice.createBuffer({ size: bl, usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST });
  gpuDevice.queue.writeBuffer(ab, 0, Af);
  gpuDevice.queue.writeBuffer(bb, 0, Bf);
  const bg = gpuDevice.createBindGroup({ layout: gpuBGL, entries: [
    { binding: 0, resource: { buffer: pb } }, { binding: 1, resource: { buffer: ab } },
    { binding: 2, resource: { buffer: bb } }, { binding: 3, resource: { buffer: cb } },
  ] });
  const enc = gpuDevice.createCommandEncoder();
  const pass = enc.beginComputePass();
  pass.setPipeline(gpuPipeline);
  pass.setBindGroup(0, bg);
  pass.dispatchWorkgroups(Math.ceil(n / 8), Math.ceil(n / 8));
  pass.end();
  enc.copyBufferToBuffer(cb, 0, rb, 0, bl);
  gpuDevice.queue.submit([enc.finish()]);
  await rb.mapAsync(GPUMapMode.READ);
  const r32 = new Float32Array(rb.getMappedRange().slice(0));
  rb.unmap();
  pb.destroy(); ab.destroy(); bb.destroy(); cb.destroy(); rb.destroy();
  const C64 = new Float64Array(sz);
  for (let i = 0; i < sz; i++) C64[i] = r32[i];
  return C64;
}

async function mm(A, B, n) {
  if (gpuAvailable && gpuPipeline && n >= 20) {
    try { return await gpuMM(A, B, n); } catch (e) { /* fall through */ }
  }
  return cmmul(A, B, n);
}

// ═══════════════════════════════════════════════════════════
// SLIDERS
// ═══════════════════════════════════════════════════════════
function wire(id, vid, fmt, cb) {
  const s = document.getElementById(id), v = document.getElementById(vid);
  if (!s || !v) return;
  const up = () => { v.textContent = fmt(s.value); if (cb) cb(s.value); };
  s.addEventListener('input', up);
  up();
}

function etaSq() { return Math.pow(parseFloat(document.getElementById('p-eta').value), 2); }
function dwF() { return Math.exp(-etaSq() / 2); }

wire('p-alpha', 'v-alpha', x => parseFloat(x).toFixed(1), x => {
  document.getElementById('h-nbar').textContent = Math.round(parseFloat(x) * parseFloat(x));
});
wire('p-alpha-phase', 'v-alpha-phase', x => x + '°');
wire('p-eta', 'v-eta', x => parseFloat(x).toFixed(3), () => {
  document.getElementById('h-dw').textContent = dwF().toFixed(3);
  document.getElementById('h-eff').textContent =
    (parseFloat(document.getElementById('p-omega-r').value) * dwF()).toFixed(3);
  updateTiming();
});
wire('p-omega-m', 'v-omega-m', x => parseFloat(x).toFixed(3), () => updateTiming());
wire('p-omega-r', 'v-omega-r', x => parseFloat(x).toFixed(3), () => {
  document.getElementById('h-eff').textContent =
    (parseFloat(document.getElementById('p-omega-r').value) * dwF()).toFixed(3);
  updateTiming();
});
wire('p-nth', 'v-nth', x => parseFloat(x).toFixed(1));
wire('p-nth-traj', 'v-nth-traj', x => x);
wire('p-nmax', 'v-nmax', x => x);
wire('p-squeeze-r', 'v-squeeze-r', x => parseFloat(x).toFixed(2));
wire('p-squeeze-phi', 'v-squeeze-phi', x => x + '°');
wire('p-theta', 'v-theta', x => x + '°');
wire('p-phi', 'v-phi', x => x + '°');
wire('p-T1', 'v-T1', x => parseFloat(x) === 0 ? '∞' : x);
wire('p-T2', 'v-T2', x => parseFloat(x) === 0 ? '∞' : x);
wire('p-heat', 'v-heat', x => x);
wire('p-ntraj', 'v-ntraj', x => x);
wire('p-nrep', 'v-nrep', x => parseInt(x) === 0 ? '∞' : x);

// Pulse separation slider
wire('p-tsep', 'v-tsep', x => {
  const v = parseFloat(x);
  if (Math.abs(v - 1.0) < 0.001) return '1.000 (strobo)';
  return v.toFixed(3);
}, () => updateTiming());

const npEl = document.getElementById('p-npulses');
if (npEl) { npEl.addEventListener('input', updateTiming); npEl.addEventListener('change', updateTiming); }

function updateTiming() {
  const eta = parseFloat(document.getElementById('p-eta').value);
  const or = parseFloat(document.getElementById('p-omega-r').value);
  const om = parseFloat(document.getElementById('p-omega-m').value);
  const np = parseInt(document.getElementById('p-npulses').value) || 22;
  const tsep_el = document.getElementById('p-tsep');
  const tsf = tsep_el ? parseFloat(tsep_el.value) || 1.0 : 1.0;
  const oeff = or * Math.exp(-(eta * eta) / 2);
  const dt_us = 1 / (4 * np * oeff);
  const Tm_us = 1 / om;
  const Tsep_us = Tm_us * tsf;
  const duty = dt_us / Tsep_us;
  const total = np * Tsep_us;
  const el = document.getElementById('h-timing');
  if (el) el.textContent =
    'θ/pulse=' + (90 / np).toFixed(1) + '°  δt=' + (dt_us * 1e3).toFixed(1) +
    'ns  T_sep=' + (Tsep_us * 1e3).toFixed(0) + 'ns  duty=' + (duty * 100).toFixed(1) +
    '%  T_seq=' + total.toFixed(1) + 'μs';
  const wn = document.getElementById('duty-warn');
  if (wn) {
    if (duty > 1) { wn.textContent = '⚠ Duty > 100%: pulse exceeds inter-pulse spacing.'; wn.style.display = 'block'; wn.style.color = '#a03030'; }
    else if (Math.abs(tsf - 1.0) > 0.01) { wn.textContent = '⚡ Non-stroboscopic: T_sep ≠ T_m. Free evolution ≠ identity.'; wn.style.display = 'block'; wn.style.color = '#a08000'; }
    else { wn.style.display = 'none'; }
  }
  drawPulseSVG(np, dt_us, Tsep_us);
}
updateTiming();

// ── Pulse train SVG ──────────────────────────────────────
function drawPulseSVG(np, dt_us, Tm_us) {
  const el = document.getElementById('pulse-svg');
  if (!el) return;
  const showN = Math.min(np, 8); // show up to 8 pulses
  const w = 700, h = 80, pad = 30;
  const totalT = showN * Tm_us;
  const sx = (w - 2 * pad) / totalT; // pixels per μs
  const pulseW = Math.max(2, dt_us * sx);
  const pulseH = 36;
  const baseY = h - 18;
  let svg = `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;">`;
  // axis
  svg += `<line x1="${pad}" y1="${baseY}" x2="${w - pad}" y2="${baseY}" stroke="#bbb" stroke-width="1"/>`;
  // pulses
  for (let i = 0; i < showN; i++) {
    const x = pad + i * Tm_us * sx;
    svg += `<rect x="${x}" y="${baseY - pulseH}" width="${pulseW}" height="${pulseH}" fill="#8b4a3a" opacity="0.7" rx="1"/>`;
    // Tm bracket
    if (i < showN - 1) {
      const mid = x + pulseW / 2 + Tm_us * sx / 2;
      svg += `<line x1="${x + pulseW}" y1="${baseY + 5}" x2="${x + Tm_us * sx}" y2="${baseY + 5}" stroke="#888" stroke-width="0.5"/>`;
    }
  }
  if (np > showN) {
    svg += `<text x="${w - pad - 5}" y="${baseY - pulseH / 2}" font-size="11" fill="#888" text-anchor="end">… ${np} total</text>`;
  }
  // labels
  svg += `<text x="${pad}" y="${12}" font-size="10" font-family="JetBrains Mono,monospace" fill="#888">`;
  svg += `N_p=${np}  δt=${(dt_us * 1e3).toFixed(0)}ns  T_m=${(Tm_us * 1e3).toFixed(0)}ns`;
  svg += `</text>`;
  svg += `<text x="${pad}" y="${baseY + 14}" font-size="9" fill="#aaa">t →</text>`;
  svg += `</svg>`;
  el.innerHTML = svg;
}

// Observable toggles
document.querySelectorAll('.ot').forEach(el => {
  el.addEventListener('click', () => {
    el.classList.toggle('ac');
    el.querySelector('input').checked = el.classList.contains('ac');
    if (lastResult) doPlot(lastResult);
  });
});
function obsAct() {
  const o = {};
  document.querySelectorAll('.ot').forEach(el => { o[el.dataset.k] = el.classList.contains('ac'); });
  return o;
}

function readP() {
  return {
    alpha: parseFloat(document.getElementById('p-alpha').value),
    alpha_phase_deg: parseFloat(document.getElementById('p-alpha-phase').value),
    eta: parseFloat(document.getElementById('p-eta').value),
    omega_m: parseFloat(document.getElementById('p-omega-m').value),
    omega_r: parseFloat(document.getElementById('p-omega-r').value),
    n_thermal: parseFloat(document.getElementById('p-nth').value),
    n_thermal_traj: parseInt(document.getElementById('p-nth-traj').value),
    nmax: parseInt(document.getElementById('p-nmax').value),
    squeeze_r: parseFloat(document.getElementById('p-squeeze-r').value),
    squeeze_phi_deg: parseFloat(document.getElementById('p-squeeze-phi').value),
    theta_deg: parseFloat(document.getElementById('p-theta').value),
    phi_deg: parseFloat(document.getElementById('p-phi').value),
    det_min: parseFloat(document.getElementById('p-dmin').value),
    det_max: parseFloat(document.getElementById('p-dmax').value),
    npts: parseInt(document.getElementById('p-npts').value),
    n_pulses: parseInt(document.getElementById('p-npulses').value),
    t_sep_factor: parseFloat(document.getElementById('p-tsep').value),
    T1: parseFloat(document.getElementById('p-T1').value),
    T2: parseFloat(document.getElementById('p-T2').value),
    heating: parseFloat(document.getElementById('p-heat').value),
    n_traj: parseInt(document.getElementById('p-ntraj').value),
    n_rep: parseInt(document.getElementById('p-nrep').value),
  };
}

function hasDeco(p) { return p.T1 > 0 || p.T2 > 0 || p.heating > 0; }

// ═══════════════════════════════════════════════════════════
// COMPLEX LINEAR ALGEBRA
// ═══════════════════════════════════════════════════════════
function ix(n, i, j) { return 2 * (i * n + j); }
function czeros(n) { return new Float64Array(2 * n * n); }
function ceye(n) { const m = czeros(n); for (let i = 0; i < n; i++) m[ix(n, i, i)] = 1; return m; }

function cmmul(A, B, n) {
  const C = czeros(n);
  for (let i = 0; i < n; i++)
    for (let k = 0; k < n; k++) {
      const ar = A[ix(n, i, k)], ai = A[ix(n, i, k) + 1];
      if (ar === 0 && ai === 0) continue;
      for (let j = 0; j < n; j++) {
        const p = ix(n, i, j), q = ix(n, k, j);
        C[p] += ar * B[q] - ai * B[q + 1];
        C[p + 1] += ar * B[q + 1] + ai * B[q];
      }
    }
  return C;
}

function cmv(A, x, n) {
  const y = new Float64Array(2 * n);
  for (let i = 0; i < n; i++) {
    let r = 0, m = 0;
    for (let j = 0; j < n; j++) {
      const p = ix(n, i, j), q = 2 * j;
      r += A[p] * x[q] - A[p + 1] * x[q + 1];
      m += A[p] * x[q + 1] + A[p + 1] * x[q];
    }
    y[2 * i] = r; y[2 * i + 1] = m;
  }
  return y;
}

function cdag(A, n) {
  const B = czeros(n);
  for (let i = 0; i < n; i++)
    for (let j = 0; j < n; j++) {
      B[ix(n, i, j)] = A[ix(n, j, i)];
      B[ix(n, i, j) + 1] = -A[ix(n, j, i) + 1];
    }
  return B;
}

function cadd(A, B) {
  const C = new Float64Array(A.length);
  for (let k = 0; k < C.length; k++) C[k] = A[k] + B[k];
  return C;
}

function cscl(A, sr, si) {
  const B = new Float64Array(A.length);
  for (let k = 0; k < A.length; k += 2) {
    B[k] = sr * A[k] - si * A[k + 1];
    B[k + 1] = sr * A[k + 1] + si * A[k];
  }
  return B;
}

function fac(n) { let f = 1; for (let i = 2; i <= n; i++) f *= i; return f; }

function cexpm(M, n) {
  let nr = 0;
  for (let k = 0; k < M.length; k++) nr += M[k] * M[k];
  nr = Math.sqrt(nr);
  let s = Math.max(0, Math.ceil(Math.log2(nr + 1e-16)));
  const Ms = cscl(M, Math.pow(2, -s), 0);
  let R = ceye(n), Mk = ceye(n);
  for (let k = 1; k <= 12; k++) { Mk = cmmul(Mk, Ms, n); R = cadd(R, cscl(Mk, 1 / fac(k), 0)); }
  for (let i = 0; i < s; i++) R = cmmul(R, R, n);
  return R;
}

async function cexpmG(M, n) {
  let nr = 0;
  for (let k = 0; k < M.length; k++) nr += M[k] * M[k];
  nr = Math.sqrt(nr);
  let s = Math.max(0, Math.ceil(Math.log2(nr + 1e-16)));
  const Ms = cscl(M, Math.pow(2, -s), 0);
  let R = ceye(n), Mk = ceye(n);
  for (let k = 1; k <= 12; k++) { Mk = await mm(Mk, Ms, n); R = cadd(R, cscl(Mk, 1 / fac(k), 0)); }
  for (let i = 0; i < s; i++) R = await mm(R, R, n);
  return R;
}

function vnorm(v) { let s = 0; for (let k = 0; k < v.length; k++) s += v[k] * v[k]; return Math.sqrt(s); }
function vnormalize(v) { const n = vnorm(v); if (n > 0) for (let k = 0; k < v.length; k++) v[k] /= n; return v; }

// ═══════════════════════════════════════════════════════════
// PHYSICS: Operators & State Preparation
// ═══════════════════════════════════════════════════════════

// Position quadrature X = a + a†
function buildX(nm) {
  const x = czeros(nm);
  for (let n = 0; n < nm - 1; n++) {
    const v = Math.sqrt(n + 1);
    x[ix(nm, n, n + 1)] += v;
    x[ix(nm, n + 1, n)] += v;
  }
  return x;
}

// exp(iη(a+a†))
async function buildC(eta, nm) {
  return await cexpmG(cscl(buildX(nm), 0, eta), nm);
}

// Fock state |n⟩
function fockState(n, nm) {
  const psi = new Float64Array(2 * nm);
  if (n < nm) psi[2 * n] = 1;
  return psi;
}

// Coherent state D(α)|0⟩ with complex α = |α|e^{iθ}
function coherentSt(absAlpha, thetaDeg, nm) {
  const theta = thetaDeg * Math.PI / 180;
  const alpha_re = absAlpha * Math.cos(theta);
  const alpha_im = absAlpha * Math.sin(theta);
  const psi = new Float64Array(2 * nm);
  const a2 = absAlpha * absAlpha;
  const ef = Math.exp(-a2 / 2);
  // ⟨n|α⟩ = e^{-|α|²/2} α^n / √(n!)
  // α^n computed iteratively: α^0=1, α^{k+1} = α^k * α
  let pow_re = 1, pow_im = 0; // α^0
  for (let n = 0; n < nm; n++) {
    const norm = ef / Math.sqrt(fac(n) > 1e300 ? 1e300 : fac(n));
    // For large n, use log: log(|⟨n|α⟩|) = -|α|²/2 + n*log|α| - log(n!)/2
    // But fac overflows. Use iterative approach:
    if (n === 0) {
      psi[0] = ef;
      psi[1] = 0;
    } else {
      // ⟨n|α⟩ = ⟨n-1|α⟩ * α / √n
      const prev_re = psi[2 * (n - 1)], prev_im = psi[2 * (n - 1) + 1];
      const sqn = Math.sqrt(n);
      psi[2 * n] = (prev_re * alpha_re - prev_im * alpha_im) / sqn;
      psi[2 * n + 1] = (prev_re * alpha_im + prev_im * alpha_re) / sqn;
    }
  }
  return psi;
}

// Squeeze operator: S(r,φ) = exp[(r/2)(e^{-2iφ}a² - e^{2iφ}a†²)]
// Build the exponent matrix and use cexpm
function buildSqueezeExponent(r, phiDeg, nm) {
  const phi = phiDeg * Math.PI / 180;
  const e2phi_re = Math.cos(2 * phi), e2phi_im = Math.sin(2 * phi);
  // a² matrix: ⟨n-2|a²|n⟩ = √(n(n-1))
  const M = czeros(nm);
  for (let n = 2; n < nm; n++) {
    const v = Math.sqrt(n * (n - 1));
    // (r/2) e^{-2iφ} a²: element (n-2, n)
    const p1 = ix(nm, n - 2, n);
    M[p1] += (r / 2) * e2phi_re;     // real part of (r/2)e^{-2iφ}
    M[p1 + 1] += -(r / 2) * e2phi_im; // imag part

    // -(r/2) e^{2iφ} (a†)²: element (n, n-2)
    const p2 = ix(nm, n, n - 2);
    M[p2] += -(r / 2) * e2phi_re;
    M[p2 + 1] += -(r / 2) * e2phi_im;
  }
  return M;
}

// Prepare motional state: S(r,φ_s) D(|α|,θ_α) |n_thermal⟩
// For thermal: sample Fock state from Bose-Einstein distribution
function sampleThermalN(nbar, nmax) {
  if (nbar <= 0) return 0;
  // Geometric distribution: P(n) = (nbar/(1+nbar))^n / (1+nbar)
  const p = 1 / (1 + nbar); // success probability
  // Sample: n = floor(log(U) / log(1-p))
  let n = Math.floor(Math.log(Math.random()) / Math.log(1 - p));
  return Math.min(n, nmax - 1);
}

async function prepareMotional(P) {
  const { alpha, alpha_phase_deg, n_thermal, squeeze_r, squeeze_phi_deg, nmax } = P;

  // Start from Fock state |n⟩ (n=0 for ground, sampled for thermal)
  const n0 = n_thermal > 0 ? sampleThermalN(n_thermal, nmax) : 0;
  let psi_m;

  if (alpha > 0) {
    // Apply displacement to |n0⟩: D(α)|n⟩
    // For n0=0, use coherentSt directly. For n0>0, apply D as matrix.
    if (n0 === 0) {
      psi_m = coherentSt(alpha, alpha_phase_deg, nmax);
    } else {
      // D(α) = exp(α a† - α* a) — build as matrix expm
      const theta_a = alpha_phase_deg * Math.PI / 180;
      const ar = alpha * Math.cos(theta_a), ai = alpha * Math.sin(theta_a);
      // α a† - α* a: element (n+1,n) = α√(n+1), element (n,n+1) = -α*√(n+1)
      const Dexp = czeros(nmax);
      for (let n = 0; n < nmax - 1; n++) {
        const sq = Math.sqrt(n + 1);
        // α a†: (n+1, n)
        Dexp[ix(nmax, n + 1, n)] += ar * sq;
        Dexp[ix(nmax, n + 1, n) + 1] += ai * sq;
        // -α* a: (n, n+1) = -conj(α)√(n+1)
        Dexp[ix(nmax, n, n + 1)] += -ar * sq;
        Dexp[ix(nmax, n, n + 1) + 1] += ai * sq; // -conj means +im
      }
      const Dmat = cexpm(Dexp, nmax);
      psi_m = cmv(Dmat, fockState(n0, nmax), nmax);
    }
  } else {
    psi_m = fockState(n0, nmax);
  }

  // Apply squeeze if r > 0
  if (squeeze_r > 0) {
    const Sexp = buildSqueezeExponent(squeeze_r, squeeze_phi_deg, nmax);
    const Smat = cexpm(Sexp, nmax);
    psi_m = cmv(Smat, psi_m, nmax);
  }

  return psi_m;
}

// Full initial state: |ψ_spin⟩ ⊗ |ψ_mot⟩
function tensorSpinMotion(theta_deg, phi_deg, psi_m, nmax) {
  const theta = theta_deg * Math.PI / 180;
  const phi = phi_deg * Math.PI / 180;
  const cd_re = Math.cos(theta / 2);
  const cu_re = Math.sin(theta / 2) * Math.cos(phi);
  const cu_im = Math.sin(theta / 2) * Math.sin(phi);

  const dim = 2 * nmax;
  const psi0 = new Float64Array(2 * dim);
  for (let n = 0; n < nmax; n++) {
    const mr = psi_m[2 * n], mi = psi_m[2 * n + 1];
    psi0[2 * n] = cd_re * mr;
    psi0[2 * n + 1] = cd_re * mi;
    psi0[2 * (nmax + n)] = cu_re * mr - cu_im * mi;
    psi0[2 * (nmax + n) + 1] = cu_re * mi + cu_im * mr;
  }
  return psi0;
}

// Hamiltonian
async function buildH(eta, or, delta, nm, C, Cd) {
  const d = 2 * nm, H = czeros(d);
  for (let n = 0; n < nm; n++) { H[ix(d, n, n)] = -delta / 2; H[ix(d, nm + n, nm + n)] = delta / 2; }
  for (let i = 0; i < nm; i++)
    for (let j = 0; j < nm; j++) {
      const pc = ix(nm, i, j);
      H[ix(d, i, nm + j)] += (or / 2) * C[pc];
      H[ix(d, i, nm + j) + 1] += (or / 2) * C[pc + 1];
      H[ix(d, nm + i, j)] += (or / 2) * Cd[pc];
      H[ix(d, nm + i, j) + 1] += (or / 2) * Cd[pc + 1];
    }
  return H;
}

function compObs(psi, nm) {
  let dd = 0, uu = 0, dur = 0, dui = 0;
  for (let n = 0; n < nm; n++) {
    const dr = psi[2 * n], di = psi[2 * n + 1];
    const ur = psi[2 * (nm + n)], ui = psi[2 * (nm + n) + 1];
    dd += dr * dr + di * di; uu += ur * ur + ui * ui;
    dur += dr * ur + di * ui; dui += di * ur - dr * ui;
  }
  const sx = 2 * dur, sy = -2 * dui, sz = uu - dd;
  const coh = Math.sqrt(sx * sx + sy * sy + sz * sz);
  const r = Math.sqrt(4 * (dur * dur + dui * dui) + (uu - dd) * (uu - dd));
  const lp = (1 + r) / 2, lm = (1 - r) / 2;
  let ent = 0;
  if (lp > 1e-15) ent -= lp * Math.log2(lp);
  if (lm > 1e-15) ent -= lm * Math.log2(lm);

  // ⟨n⟩ = Σ_n n·(|⟨↓,n|ψ⟩|² + |⟨↑,n|ψ⟩|²)
  let nbar = 0;
  for (let n = 0; n < nm; n++) {
    nbar += n * (psi[2 * n] * psi[2 * n] + psi[2 * n + 1] * psi[2 * n + 1]);
    nbar += n * (psi[2 * (nm + n)] * psi[2 * (nm + n)] + psi[2 * (nm + n) + 1] * psi[2 * (nm + n) + 1]);
  }

  // Motional purity: Tr(ρ_m²)
  // ρ_m(i,j) = Σ_s ψ*(s,i) ψ(s,j) where s ∈ {↓,↑}
  // Tr(ρ_m²) = Σ_{i,j} |ρ_m(i,j)|²
  // This is O(nm²) — compute the reduced density matrix elements on the fly
  let purity = 0;
  for (let i = 0; i < nm; i++) {
    for (let j = 0; j < nm; j++) {
      // ρ_m(i,j) = ψ*(↓,i)ψ(↓,j) + ψ*(↑,i)ψ(↑,j)
      const di_r = psi[2 * i], di_i = psi[2 * i + 1];
      const dj_r = psi[2 * j], dj_i = psi[2 * j + 1];
      const ui_r = psi[2 * (nm + i)], ui_i = psi[2 * (nm + i) + 1];
      const uj_r = psi[2 * (nm + j)], uj_i = psi[2 * (nm + j) + 1];
      // conj(d_i)*d_j + conj(u_i)*u_j
      const rho_re = (di_r * dj_r + di_i * dj_i) + (ui_r * uj_r + ui_i * uj_i);
      const rho_im = (di_r * dj_i - di_i * dj_r) + (ui_r * uj_i - ui_i * uj_r);
      purity += rho_re * rho_re + rho_im * rho_im;
    }
  }

  return { sigma_x: sx, sigma_y: sy, sigma_z: sz, coherence: coh, entropy: ent,
           nbar: nbar, motional_purity: purity };
}

// Fidelity of final motional state with initial: F = ⟨ψ_m,init|ρ_m,final|ψ_m,init⟩
// = Σ_{i,j} ψ*_init(i) ρ_m(i,j) ψ_init(j)
function motionalFidelity(psi, psi_m_init, nm) {
  // ρ_m(i,j) = Σ_s ψ*(s,i)ψ(s,j)
  // F = Σ_{i,j} ψ*_init(i) [Σ_s ψ*(s,i)ψ(s,j)] ψ_init(j)
  //   = Σ_s |Σ_i ψ*_init(i) ψ(s,i)|²  (rewritten as sum of overlaps)
  let F = 0;
  // s = ↓ (indices 0..nm-1)
  let ov_re = 0, ov_im = 0;
  for (let i = 0; i < nm; i++) {
    const ir = psi_m_init[2 * i], ii = psi_m_init[2 * i + 1];
    // conj(init) * psi(↓,i)
    ov_re += ir * psi[2 * i] + ii * psi[2 * i + 1];
    ov_im += ir * psi[2 * i + 1] - ii * psi[2 * i];
  }
  F += ov_re * ov_re + ov_im * ov_im;
  // s = ↑ (indices nm..2nm-1)
  ov_re = 0; ov_im = 0;
  for (let i = 0; i < nm; i++) {
    const ir = psi_m_init[2 * i], ii = psi_m_init[2 * i + 1];
    ov_re += ir * psi[2 * (nm + i)] + ii * psi[2 * (nm + i) + 1];
    ov_im += ir * psi[2 * (nm + i) + 1] - ii * psi[2 * (nm + i)];
  }
  F += ov_re * ov_re + ov_im * ov_im;
  return F;
}

function fockLeak(psi, nm) {
  let l = 0;
  for (let n = Math.max(0, nm - 3); n < nm; n++) {
    l += psi[2 * n] ** 2 + psi[2 * n + 1] ** 2;
    l += psi[2 * (nm + n)] ** 2 + psi[2 * (nm + n) + 1] ** 2;
  }
  return l;
}

function collapse(psi, nm, Tm, g1, gp, gh) {
  const d = 2 * nm;
  let pu = 0;
  for (let n = 0; n < nm; n++) pu += psi[2 * (nm + n)] ** 2 + psi[2 * (nm + n) + 1] ** 2;
  const dp1 = g1 * Tm * pu;
  const dp2 = (gp / 2) * Tm;
  let np1 = 0;
  for (let n = 0; n < nm; n++) {
    np1 += (n + 1) * (psi[2 * n] ** 2 + psi[2 * n + 1] ** 2);
    np1 += (n + 1) * (psi[2 * (nm + n)] ** 2 + psi[2 * (nm + n) + 1] ** 2);
  }
  const dp3 = gh * Tm * np1;
  const r = Math.random();
  if (r < dp1 && dp1 > 0) {
    const o = new Float64Array(2 * d);
    for (let n = 0; n < nm; n++) { o[2 * n] = psi[2 * (nm + n)]; o[2 * n + 1] = psi[2 * (nm + n) + 1]; }
    return vnormalize(o);
  }
  if (r < dp1 + dp2 && dp2 > 0) {
    const o = new Float64Array(psi);
    for (let n = 0; n < nm; n++) { o[2 * n] = -psi[2 * n]; o[2 * n + 1] = -psi[2 * n + 1]; }
    return vnormalize(o);
  }
  if (r < dp1 + dp2 + dp3 && dp3 > 0) {
    const o = new Float64Array(2 * d);
    for (let n = 0; n < nm - 1; n++) {
      const sq = Math.sqrt(n + 1);
      o[2 * (n + 1)] += sq * psi[2 * n]; o[2 * (n + 1) + 1] += sq * psi[2 * n + 1];
      o[2 * (nm + n + 1)] += sq * psi[2 * (nm + n)]; o[2 * (nm + n + 1) + 1] += sq * psi[2 * (nm + n) + 1];
    }
    return vnormalize(o);
  }
  // No jump
  const o = new Float64Array(psi);
  for (let n = 0; n < nm; n++) {
    const s1 = g1 * Tm / 2;
    o[2 * (nm + n)] -= s1 * psi[2 * (nm + n)]; o[2 * (nm + n) + 1] -= s1 * psi[2 * (nm + n) + 1];
    const s2 = (gp / 2) * Tm / 2;
    o[2 * n] -= s2 * psi[2 * n]; o[2 * n + 1] -= s2 * psi[2 * n + 1];
    o[2 * (nm + n)] -= s2 * psi[2 * (nm + n)]; o[2 * (nm + n) + 1] -= s2 * psi[2 * (nm + n) + 1];
    const s3 = gh * (n + 1) * Tm / 2;
    o[2 * n] -= s3 * psi[2 * n]; o[2 * n + 1] -= s3 * psi[2 * n + 1];
    o[2 * (nm + n)] -= s3 * psi[2 * (nm + n)]; o[2 * (nm + n) + 1] -= s3 * psi[2 * (nm + n) + 1];
  }
  return vnormalize(o);
}

function qpn(ideal, nr) {
  if (nr <= 0) return { noisy: ideal, err: 0 };
  const p = Math.max(1e-10, Math.min(1 - 1e-10, (1 + ideal) / 2));
  let s = 0; for (let i = 0; i < nr; i++) if (Math.random() < p) s++;
  return { noisy: 2 * (s / nr) - 1, err: 2 * Math.sqrt(p * (1 - p) / nr) };
}

// ═══════════════════════════════════════════════════════════
// MAIN SIMULATION
// ═══════════════════════════════════════════════════════════
document.getElementById('rbtn').addEventListener('click', runSim);

async function runSim() {
  const btn = document.getElementById('rbtn'), st = document.getElementById('rstat');
  const pw = document.getElementById('pw'), pb = document.getElementById('pb');
  const cbb = document.getElementById('cb');
  btn.disabled = true; st.textContent = 'Initialising…';
  pw.classList.add('vis'); pb.style.width = '0%'; cbb.style.display = 'none';
  if (gpuAvailable) await initPipeline();

  const P = readP();
  const useDeco = hasDeco(P);
  const useThermal = P.n_thermal > 0;
  const nThermTraj = useThermal ? P.n_thermal_traj : 1;
  const nDecoTraj = useDeco ? P.n_traj : 1;
  const totalTraj = nThermTraj * nDecoTraj;

  const dets = [];
  for (let i = 0; i < P.npts; i++)
    dets.push(P.det_min + (P.det_max - P.det_min) * i / (P.npts - 1));

  const oeff = P.omega_r * Math.exp(-(P.eta * P.eta) / 2);
  const dt = (Math.PI / 2) / (P.n_pulses * oeff);
  const Tm = 2 * Math.PI / P.omega_m;  // motional period
  const Tsep = Tm * P.t_sep_factor;     // actual inter-pulse spacing
  const g1 = P.T1 > 0 ? 1 / P.T1 : 0;
  const gpR = P.T2 > 0 ? 1 / P.T2 : 0;
  const gp = Math.max(0, gpR - g1 / 2);
  const gh = P.heating > 0 ? P.heating / 1000 : 0;

  st.textContent = 'Building operators…';
  await new Promise(r => setTimeout(r, 0));
  const Cm = await buildC(P.eta, P.nmax);
  const Cdm = cdag(Cm, P.nmax);
  const dim = 2 * P.nmax;

  // Free-evolution operator between pulses:
  // U_free = exp(-i ωm a†a Tsep) = diag(exp(-i 2π n Tsep/Tm))
  // When t_sep_factor = 1: U_free = I (stroboscopic condition)
  // When t_sep_factor ≠ 1: nontrivial phase rotation
  const needFreeEvol = Math.abs(P.t_sep_factor - 1.0) > 1e-6;
  let Ufree = null;
  if (needFreeEvol) {
    // Build as dim×dim diagonal matrix in spin⊗motion space
    Ufree = czeros(dim);
    const phase_per_n = 2 * Math.PI * P.t_sep_factor; // ωm Tsep = 2π × (Tsep/Tm)
    for (let n = 0; n < P.nmax; n++) {
      const phi = -n * phase_per_n;
      const cr = Math.cos(phi), ci = Math.sin(phi);
      // ↓ block
      Ufree[ix(dim, n, n)] = cr;
      Ufree[ix(dim, n, n) + 1] = ci;
      // ↑ block
      Ufree[ix(dim, P.nmax + n, P.nmax + n)] = cr;
      Ufree[ix(dim, P.nmax + n, P.nmax + n) + 1] = ci;
    }
  }

  const R = {
    detuning: new Float64Array(P.npts),
    sigma_x: new Float64Array(P.npts), sigma_y: new Float64Array(P.npts), sigma_z: new Float64Array(P.npts),
    coherence: new Float64Array(P.npts), entropy: new Float64Array(P.npts),
    nbar: new Float64Array(P.npts), mot_purity: new Float64Array(P.npts), mot_fidelity: new Float64Array(P.npts),
    noisy_sigma_x: new Float64Array(P.npts), noisy_sigma_y: new Float64Array(P.npts), noisy_sigma_z: new Float64Array(P.npts),
    err_sigma_x: new Float64Array(P.npts), err_sigma_y: new Float64Array(P.npts), err_sigma_z: new Float64Array(P.npts),
    max_leakage: 0,
  };

  const t0 = performance.now();
  let maxLk = 0;
  const tw = P.npts * totalTraj;
  let wd = 0;

  for (let i = 0; i < P.npts; i++) {
    const delta = dets[i] * P.omega_m;
    const H = await buildH(P.eta, P.omega_r, delta, P.nmax, Cm, Cdm);
    const U = await cexpmG(cscl(H, 0, -dt), dim);

    let ax = 0, ay = 0, az = 0, ac = 0, ae = 0;
    let a_nbar = 0, a_pur = 0, a_fid = 0;

    for (let tt = 0; tt < nThermTraj; tt++) {
      const psi_m = await prepareMotional(P);
      const psi0 = tensorSpinMotion(P.theta_deg, P.phi_deg, psi_m, P.nmax);

      for (let td = 0; td < nDecoTraj; td++) {
        let psi = new Float64Array(psi0);
        for (let p = 0; p < P.n_pulses; p++) {
          psi = cmv(U, psi, dim);
          if (p < P.n_pulses - 1) {
            // Free evolution between pulses
            if (needFreeEvol) psi = cmv(Ufree, psi, dim);
            // Decoherence collapse
            if (useDeco) psi = collapse(psi, P.nmax, Tsep, g1, gp, gh);
          }
        }
        const ob = compObs(psi, P.nmax);
        ax += ob.sigma_x; ay += ob.sigma_y; az += ob.sigma_z;
        ac += ob.coherence; ae += ob.entropy;
        a_nbar += ob.nbar; a_pur += ob.motional_purity;
        a_fid += motionalFidelity(psi, psi_m, P.nmax);
        const lk = fockLeak(psi, P.nmax);
        if (lk > maxLk) maxLk = lk;
        wd++;
      }
    }

    const nt = totalTraj;
    R.detuning[i] = dets[i];
    R.sigma_x[i] = ax / nt; R.sigma_y[i] = ay / nt; R.sigma_z[i] = az / nt;
    R.coherence[i] = ac / nt; R.entropy[i] = ae / nt;
    R.nbar[i] = a_nbar / nt; R.mot_purity[i] = a_pur / nt; R.mot_fidelity[i] = a_fid / nt;

    if (P.n_rep > 0) {
      const nx = qpn(R.sigma_x[i], P.n_rep);
      const ny = qpn(R.sigma_y[i], P.n_rep);
      const nz = qpn(R.sigma_z[i], P.n_rep);
      R.noisy_sigma_x[i] = nx.noisy; R.err_sigma_x[i] = nx.err;
      R.noisy_sigma_y[i] = ny.noisy; R.err_sigma_y[i] = ny.err;
      R.noisy_sigma_z[i] = nz.noisy; R.err_sigma_z[i] = nz.err;
    }

    if (wd % Math.max(1, Math.floor(tw / 50)) < totalTraj) {
      pb.style.width = (wd / tw * 100).toFixed(0) + '%';
      st.textContent = `Pt ${i + 1}/${P.npts}` +
        (totalTraj > 1 ? ` (${totalTraj} traj)` : '') +
        (gpuAvailable ? ' [GPU]' : '') + '…';
      await new Promise(r => setTimeout(r, 0));
    }
  }

  R.max_leakage = maxLk;
  const el = ((performance.now() - t0) / 1000).toFixed(1);
  pb.style.width = '100%';
  st.textContent = `Done in ${el}s. ${P.npts}pts, dim=${dim}` +
    (totalTraj > 1 ? `, ${totalTraj}traj` : '') +
    (P.n_rep > 0 ? `, N_rep=${P.n_rep}` : '') + '.';

  showConv(maxLk, P.alpha, P.nmax);
  lastResult = { params: P, data: R, elapsed: el, timestamp: new Date().toISOString() };
  doPlot(lastResult);
  await compHash(lastResult);
  document.getElementById('dlsec').style.display = 'block';
  document.getElementById('nodl').style.display = 'none';
  showMeta(P, maxLk);
  btn.disabled = false;
}

function showConv(lk, alpha, nmax) {
  const cb = document.getElementById('cb');
  const pct = (lk * 100).toFixed(3);
  const rec = Math.ceil(alpha * alpha + 5 * Math.sqrt(alpha * alpha) + 10);
  if (lk < 1e-4) { cb.className = 'cb ok'; cb.innerHTML = '✓ Converged — boundary: ' + pct + '%'; }
  else if (lk < 0.01) { cb.className = 'cb wn'; cb.innerHTML = '⚠ Marginal — boundary: ' + pct + '%. Try N<sub>max</sub> ≥ ' + rec + '.'; }
  else { cb.className = 'cb fl'; cb.innerHTML = '✗ Not converged — boundary: ' + pct + '%. Need N<sub>max</sub> ≥ ' + rec + '.'; }
  cb.style.display = 'block';
}

// ═══════════════════════════════════════════════════════════
// PLOTTING
// ═══════════════════════════════════════════════════════════
const LB = {
  paper_bgcolor: PAL.bg, plot_bgcolor: PAL.bg_axes,
  font: { family: 'Source Serif 4,Georgia,serif', color: PAL.text, size: 13 },
  margin: { l: 56, r: 20, t: 8, b: 44 },
  xaxis: { gridcolor: PAL.grid, gridwidth: 0.5, linecolor: PAL.border, linewidth: 0.6,
    tickfont: { size: 11, color: PAL.text_muted }, zeroline: false },
  yaxis: { gridcolor: PAL.grid, gridwidth: 0.5, linecolor: PAL.border, linewidth: 0.6,
    tickfont: { size: 11, color: PAL.text_muted }, zeroline: false },
  showlegend: true,
  legend: { bgcolor: PAL.bg_axes, bordercolor: PAL.border, borderwidth: 1,
    font: { size: 10 }, x: 1, xanchor: 'right', y: 1, yanchor: 'top' },
};

function doPlot(res) {
  const D = res.data, P = res.params, obs = obsAct();
  const xs = Array.from(D.detuning), hn = P.n_rep > 0;
  function C(a) { const v = Array.from(a); return ((Math.max(...v) - Math.min(...v)) / 2).toFixed(3); }
  const tr = [];
  for (const [k, c, l] of [['sigma_x', PAL.sigma_x, '⟨σₓ⟩'], ['sigma_y', PAL.sigma_y, '⟨σᵧ⟩'], ['sigma_z', PAL.sigma_z, '⟨σ_z⟩']]) {
    if (!obs[k]) continue;
    tr.push({ x: xs, y: Array.from(D[k]), name: `${l} C=${C(D[k])}${hn ? ' (ideal)' : ''}`,
      mode: 'lines', line: { color: c, width: hn ? 1 : 1.4, dash: hn ? 'dot' : 'solid' } });
    if (hn) tr.push({ x: xs, y: Array.from(D['noisy_' + k]),
      error_y: { type: 'data', array: Array.from(D['err_' + k]), visible: true, color: c, thickness: 0.8, width: 2 },
      name: `${l} (N=${P.n_rep})`, mode: 'markers', marker: { color: c, size: 3, opacity: 0.7 } });
  }
  if (obs.coherence) tr.push({ x: xs, y: Array.from(D.coherence), name: 'Coherence',
    mode: 'lines', line: { color: PAL.coherence, width: 1.1, dash: 'dot' } });

  const pd = document.getElementById('pl-s'); pd.innerHTML = '';
  if (tr.length > 0) Plotly.newPlot(pd, tr, { ...LB,
    yaxis: { ...LB.yaxis, title: { text: '⟨σᵢ⟩', font: { size: 13 } }, range: [-1.08, 1.08] },
    xaxis: { ...LB.xaxis, title: { text: 'Detuning  δ₀ / ωₘ', font: { size: 12 } } },
    height: hn ? 380 : 340 },
    { responsive: true, displayModeBar: true, modeBarButtonsToRemove: ['lasso2d', 'select2d'] });

  const ed = document.getElementById('pl-e'); ed.innerHTML = '';
  if (obs.entropy) Plotly.newPlot(ed,
    [{ x: xs, y: Array.from(D.entropy), name: 'S', mode: 'lines', line: { color: PAL.entropy, width: 1.1 } }],
    { ...LB, yaxis: { ...LB.yaxis, title: { text: 'S (bits)', font: { size: 12 } }, rangemode: 'tozero' },
      xaxis: { ...LB.xaxis, title: { text: 'Detuning  δ₀ / ωₘ', font: { size: 12 } } },
      height: 170, showlegend: false, margin: { l: 56, r: 20, t: 4, b: 40 } },
    { responsive: true, displayModeBar: false });

  // Third panel: motional observables
  const md = document.getElementById('pl-m'); if (md) { md.innerHTML = '';
  const mtr = [];
  if (obs.nbar) mtr.push({ x: xs, y: Array.from(D.nbar), name: '⟨n⟩',
    mode: 'lines', line: { color: '#3a7a3a', width: 1.3 }, yaxis: 'y' });
  if (obs.mot_purity) mtr.push({ x: xs, y: Array.from(D.mot_purity), name: 'Tr(ρ_m²)',
    mode: 'lines', line: { color: '#8a5a3a', width: 1.1, dash: 'dash' }, yaxis: 'y2' });
  if (obs.mot_fidelity) mtr.push({ x: xs, y: Array.from(D.mot_fidelity), name: 'F(ρ_m,ψ₀)',
    mode: 'lines', line: { color: '#3a5a8a', width: 1.1, dash: 'dot' }, yaxis: 'y2' });
  if (mtr.length > 0) Plotly.newPlot(md, mtr, { ...LB,
    yaxis: { ...LB.yaxis, title: { text: '⟨n⟩', font: { size: 12 } }, rangemode: 'tozero', side: 'left' },
    yaxis2: { overlaying: 'y', side: 'right', title: { text: 'Purity / Fidelity', font: { size: 11 } },
      range: [0, 1.05], gridcolor: 'transparent', tickfont: { size: 10, color: PAL.text_muted } },
    xaxis: { ...LB.xaxis, title: { text: 'Detuning  δ₀ / ωₘ', font: { size: 12 } } },
    height: 200, margin: { l: 56, r: 56, t: 4, b: 40 },
    legend: { ...LB.legend, y: 0.95 } },
    { responsive: true, displayModeBar: false });
  }
}

function showMeta(P, lk) {
  const d = document.getElementById('meta');
  const it = [['α', P.alpha], ['θ_α', P.alpha_phase_deg + '°'],
    ['η', P.eta], ['ωₘ/(2π)', P.omega_m + ' MHz'], ['Ω/(2π)', P.omega_r + ' MHz'],
    ['N_max', P.nmax], ['N_p', P.n_pulses],
    ['T_sep/T_m', P.t_sep_factor.toFixed(3)],
    ['Leak', (lk * 100).toFixed(4) + '%']];
  if (P.squeeze_r > 0) it.push(['r_sq', P.squeeze_r]);
  if (P.n_thermal > 0) it.push(['n̄_th', P.n_thermal]);
  if (P.theta_deg !== 0) it.push(['θ_spin', P.theta_deg + '°']);
  if (P.T1 > 0) it.push(['T₁', P.T1 + 'μs']);
  if (P.T2 > 0) it.push(['T₂', P.T2 + 'μs']);
  if (P.heating > 0) it.push(['dn/dt', P.heating]);
  if (P.n_rep > 0) it.push(['N_rep', P.n_rep]);
  if (gpuAvailable) it.push(['GPU', '✓']);
  d.innerHTML = it.map(([k, v]) => `<span class="mi"><span class="mk">${k}:</span> ${v}</span>`).join('');
  d.style.display = 'flex';
}

// ═══════════════════════════════════════════════════════════
// SHA-256
// ═══════════════════════════════════════════════════════════
async function compHash(res) {
  const p = {
    code_version: VER, repo: REPO, params: res.params, timestamp: res.timestamp,
    data_fingerprint: {
      sigma_x_sum: Array.from(res.data.sigma_x).reduce((a, b) => a + b, 0),
      sigma_y_sum: Array.from(res.data.sigma_y).reduce((a, b) => a + b, 0),
      sigma_z_sum: Array.from(res.data.sigma_z).reduce((a, b) => a + b, 0),
      entropy_sum: Array.from(res.data.entropy).reduce((a, b) => a + b, 0),
      coherence_sum: Array.from(res.data.coherence).reduce((a, b) => a + b, 0),
      n_points: res.data.detuning.length, max_leakage: res.data.max_leakage,
    }
  };
  const d = new TextEncoder().encode(JSON.stringify(p));
  const b = await crypto.subtle.digest('SHA-256', d);
  lastHash = Array.from(new Uint8Array(b)).map(x => x.toString(16).padStart(2, '0')).join('');
  document.getElementById('hashd').textContent = lastHash;
}

// ═══════════════════════════════════════════════════════════
// DOWNLOADS
// ═══════════════════════════════════════════════════════════
function bm() {
  const p = lastResult.params;
  return {
    schema_version: '1.2', code_version: VER, repository: REPO,
    source_paper: { journal: 'Phys. Rev. A 109, 053105 (2024)', doi: '10.1103/PhysRevA.109.053105', arxiv: '2309.15580' },
    endorsement_marker: 'Local candidate framework',
    parameters: p,
    derived: {
      omega_eff: p.omega_r * Math.exp(-(p.eta * p.eta) / 2),
      debye_waller: Math.exp(-(p.eta * p.eta) / 2),
      n_mean: p.alpha * p.alpha, hilbert_dim: 2 * p.nmax,
    },
    convergence: { max_fock_leakage: lastResult.data.max_leakage, converged: lastResult.data.max_leakage < 0.01 },
    execution: { timestamp: lastResult.timestamp, elapsed_s: parseFloat(lastResult.elapsed),
      engine: gpuAvailable ? 'browser-webgpu' : 'browser-js' },
    provenance_hash: lastHash, n_points: lastResult.data.detuning.length,
  };
}

function dlF(fn, ct, mt) {
  const b = new Blob([ct], { type: mt }), u = URL.createObjectURL(b);
  const a = document.createElement('a'); a.href = u; a.download = fn;
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(u);
}

document.getElementById('dl-json').addEventListener('click', () => {
  if (!lastResult) return;
  const d = lastResult.data;
  const o = { manifest: bm(), data: {
    detuning: Array.from(d.detuning), sigma_x: Array.from(d.sigma_x),
    sigma_y: Array.from(d.sigma_y), sigma_z: Array.from(d.sigma_z),
    coherence: Array.from(d.coherence), entropy: Array.from(d.entropy),
  } };
  if (lastResult.params.n_rep > 0) {
    o.data.noisy_sigma_x = Array.from(d.noisy_sigma_x); o.data.noisy_sigma_y = Array.from(d.noisy_sigma_y);
    o.data.noisy_sigma_z = Array.from(d.noisy_sigma_z); o.data.err_sigma_x = Array.from(d.err_sigma_x);
    o.data.err_sigma_y = Array.from(d.err_sigma_y); o.data.err_sigma_z = Array.from(d.err_sigma_z);
  }
  dlF('simulation_results.json', JSON.stringify(o, null, 2), 'application/json');
});

document.getElementById('dl-csv').addEventListener('click', () => {
  if (!lastResult) return;
  const d = lastResult.data;
  let c = `# Hash: ${lastHash}\n# ${REPO} v${VER}\n`;
  c += 'detuning,sigma_x,sigma_y,sigma_z,coherence,entropy\n';
  for (let i = 0; i < d.detuning.length; i++)
    c += `${d.detuning[i].toFixed(6)},${d.sigma_x[i].toFixed(8)},${d.sigma_y[i].toFixed(8)},${d.sigma_z[i].toFixed(8)},${d.coherence[i].toFixed(8)},${d.entropy[i].toFixed(8)}\n`;
  dlF('simulation_results.csv', c, 'text/csv');
});

document.getElementById('dl-py').addEventListener('click', () => {
  if (!lastResult) return;
  const p = lastResult.params;
  dlF('stroboscopic_scan.py', `#!/usr/bin/env python3
"""Stroboscopic Detuning Scan — PRA 109, 053105 (2024)
Repo: ${REPO}  v${VER}  Browser hash: ${lastHash}
pip install qutip numpy"""
import numpy as np, json, hashlib, qutip as qt
from datetime import datetime, timezone

ALPHA=${p.alpha}; ALPHA_PHASE=${p.alpha_phase_deg}; ETA=${p.eta}
OMEGA_M=${p.omega_m}; OMEGA_R=${p.omega_r}; NMAX=${p.nmax}
DET_MIN=${p.det_min}; DET_MAX=${p.det_max}; NPTS=${p.npts}
N_PULSES=${p.n_pulses}; N_THERMAL=${p.n_thermal}
SQUEEZE_R=${p.squeeze_r}; SQUEEZE_PHI=${p.squeeze_phi_deg}
THETA_SPIN=${p.theta_deg}; PHI_SPIN=${p.phi_deg}
T1=${p.T1}; T2=${p.T2}; HEATING=${p.heating}; N_TRAJ=${p.n_traj}; N_REP=${p.n_rep}

# ... (QuTiP implementation — see code.html for full documentation)
print("Parameters exported. See code.html for the full QuTiP implementation.")
`, 'text/x-python');
});

document.getElementById('dl-man').addEventListener('click', () => {
  if (!lastResult) return;
  dlF('manifest.json', JSON.stringify(bm(), null, 2), 'application/json');
});

// ═══════════════════════════════════════════════════════════
// BLOCH SPHERE (live SVG)
// ═══════════════════════════════════════════════════════════
function drawBloch() {
  const el = document.getElementById('bloch-svg');
  if (!el) return;
  const theta = parseFloat(document.getElementById('p-theta').value) * Math.PI / 180;
  const phi = parseFloat(document.getElementById('p-phi').value) * Math.PI / 180;

  // Bloch vector components
  const bx = Math.sin(theta) * Math.cos(phi);
  const by = Math.sin(theta) * Math.sin(phi);
  const bz = Math.cos(theta);

  // Simple orthographic projection with slight tilt
  const tilt = 0.3; // viewing angle from z-axis
  const w = 180, h = 180, cx = w / 2, cy = h / 2, R = 65;

  // Project 3D → 2D (tilted view: x→right, y→into screen, z→up, slight y-tilt)
  const px = cx + R * (bx * 0.95 + by * 0.15);
  const py = cy - R * (bz * 0.9 - by * tilt);

  let svg = `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" style="max-width:180px;">`;
  // Sphere outline
  svg += `<ellipse cx="${cx}" cy="${cy}" rx="${R}" ry="${R}" fill="none" stroke="#ccc" stroke-width="0.8"/>`;
  // Equator ellipse (tilted)
  svg += `<ellipse cx="${cx}" cy="${cy + R * tilt * 0.4}" rx="${R}" ry="${R * 0.35}" fill="none" stroke="#ddd" stroke-width="0.5" stroke-dasharray="3,3"/>`;
  // Axes
  svg += `<line x1="${cx}" y1="${cy + R + 5}" x2="${cx}" y2="${cy - R - 5}" stroke="#ccc" stroke-width="0.5"/>`;
  svg += `<line x1="${cx - R - 5}" y1="${cy + R * tilt * 0.4}" x2="${cx + R + 5}" y2="${cy + R * tilt * 0.4}" stroke="#ccc" stroke-width="0.5"/>`;
  // Labels
  svg += `<text x="${cx}" y="${cy - R - 8}" font-size="9" fill="#888" text-anchor="middle">|↑⟩</text>`;
  svg += `<text x="${cx}" y="${cy + R + 14}" font-size="9" fill="#888" text-anchor="middle">|↓⟩</text>`;
  // Bloch vector (arrow from origin to tip)
  svg += `<line x1="${cx}" y1="${cy}" x2="${px}" y2="${py}" stroke="#8b4a3a" stroke-width="2" stroke-linecap="round"/>`;
  // Tip dot
  svg += `<circle cx="${px}" cy="${py}" r="4" fill="#8b4a3a"/>`;
  // Shadow on equator
  const sx = cx + R * (bx * 0.95 + by * 0.15);
  const sy = cy + R * tilt * 0.4;
  svg += `<line x1="${cx}" y1="${cy + R * tilt * 0.4}" x2="${sx}" y2="${sy}" stroke="#ddd" stroke-width="1" stroke-dasharray="2,2"/>`;
  svg += `<circle cx="${sx}" cy="${sy}" r="2" fill="#ccc"/>`;
  // Info text
  const tdeg = (theta * 180 / Math.PI).toFixed(0);
  const pdeg = (phi * 180 / Math.PI).toFixed(0);
  svg += `<text x="${w - 4}" y="${h - 4}" font-size="8" font-family="JetBrains Mono,monospace" fill="#aaa" text-anchor="end">θ=${tdeg}° φ=${pdeg}°</text>`;
  svg += `</svg>`;
  el.innerHTML = svg;
}

// Wire Bloch sphere to spin sliders
['p-theta', 'p-phi'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', drawBloch);
});
drawBloch();

// ═══════════════════════════════════════════════════════════
// WIGNER FUNCTION (analytic, live Plotly heatmap)
//
// For a displaced squeezed thermal state:
//   W(x,p) = (1/π) * 1/√det(V) * exp(-½ ξᵀ V⁻¹ ξ)
// where ξ = (x - x₀, p - p₀)ᵀ, V is the covariance matrix:
//   V = S(r,φ) · diag(n̄+½, n̄+½) · S(r,φ)ᵀ
//   S(r,φ) = [[cosh(r)+cos(2φ)sinh(r), sin(2φ)sinh(r)],
//             [sin(2φ)sinh(r), cosh(r)-cos(2φ)sinh(r)]]
// x₀ = √2 Re(α), p₀ = √2 Im(α)
// ═══════════════════════════════════════════════════════════
function drawWigner() {
  const el = document.getElementById('wigner-plot');
  if (!el) return;

  const alpha = parseFloat(document.getElementById('p-alpha').value);
  const alpha_phase = parseFloat(document.getElementById('p-alpha-phase').value) * Math.PI / 180;
  const nth = parseFloat(document.getElementById('p-nth').value);
  const r = parseFloat(document.getElementById('p-squeeze-r').value);
  const sphi = parseFloat(document.getElementById('p-squeeze-phi').value) * Math.PI / 180;

  // Displacement in phase space
  const x0 = Math.SQRT2 * alpha * Math.cos(alpha_phase);
  const p0 = Math.SQRT2 * alpha * Math.sin(alpha_phase);

  // Covariance matrix of squeezed thermal state
  const nbar = nth + 0.5; // total variance per quadrature for thermal
  const ch = Math.cosh(r), sh = Math.sinh(r);
  const c2p = Math.cos(2 * sphi), s2p = Math.sin(2 * sphi);
  // V = nbar * S·Sᵀ where S is the symplectic squeeze matrix
  const V11 = nbar * (ch * ch + sh * sh + 2 * ch * sh * c2p); // = nbar * (cosh(2r) + sinh(2r)cos(2φ))
  const V22 = nbar * (ch * ch + sh * sh - 2 * ch * sh * c2p); // = nbar * (cosh(2r) - sinh(2r)cos(2φ))
  const V12 = nbar * (2 * ch * sh * s2p); // = nbar * sinh(2r) * sin(2φ)

  const detV = V11 * V22 - V12 * V12;
  const invV11 = V22 / detV, invV22 = V11 / detV, invV12 = -V12 / detV;

  // Grid
  const extent = Math.max(3, alpha * 1.5 + 2 * Math.exp(r) + 2);
  const N = 80;
  const dx = 2 * extent / (N - 1);
  const xs = [], ps = [];
  for (let i = 0; i < N; i++) {
    xs.push(-extent + i * dx);
    ps.push(-extent + i * dx);
  }

  const W = [];
  for (let j = 0; j < N; j++) {
    const row = [];
    for (let i = 0; i < N; i++) {
      const xi = xs[i] - x0, pi = ps[j] - p0;
      const exponent = -0.5 * (invV11 * xi * xi + 2 * invV12 * xi * pi + invV22 * pi * pi);
      row.push((1 / Math.PI) * (1 / Math.sqrt(detV)) * Math.exp(exponent));
    }
    W.push(row);
  }

  const trace = {
    z: W, x: xs, y: ps, type: 'heatmap',
    colorscale: [
      [0, '#1a237e'], [0.15, '#283593'], [0.3, '#5c6bc0'],
      [0.45, '#e8eaf6'], [0.5, '#fff'], [0.55, '#fce4ec'],
      [0.7, '#ef5350'], [0.85, '#c62828'], [1, '#b71c1c']
    ],
    showscale: false, hoverinfo: 'skip',
  };

  const layout = {
    paper_bgcolor: 'transparent', plot_bgcolor: '#fafaf8',
    font: { family: 'JetBrains Mono, monospace', size: 10, color: '#888' },
    margin: { l: 40, r: 10, t: 22, b: 36 },
    xaxis: { title: 'x', gridcolor: '#e8e8e6', zeroline: true, zerolinecolor: '#ccc' },
    yaxis: { title: 'p', gridcolor: '#e8e8e6', zeroline: true, zerolinecolor: '#ccc', scaleanchor: 'x' },
    title: { text: 'W(x, p) — initial motional state', font: { size: 11, color: '#888' } },
    width: null, height: 270,
  };

  Plotly.react(el, [trace], layout, { responsive: true, displayModeBar: false });
}

// Wire Wigner to motional state sliders
['p-alpha', 'p-alpha-phase', 'p-nth', 'p-squeeze-r', 'p-squeeze-phi'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', drawWigner);
});

// Debounced initial draw (wait for Plotly to be ready)
setTimeout(drawWigner, 300);
setTimeout(drawBloch, 100);

