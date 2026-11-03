/*
 * heating-overview-card — card custom per Home Assistant (nessuna dipendenza).
 * Mostra: potenza termica (gauge), circuito mandata/ritorno con ΔT e portata,
 * energia 24 h e da inizio stagione, storico potenza 24 h.
 * Configurazione: vedi example-dashboard.yaml
 */
const HOC_KEYS = ['supply_temp', 'return_temp', 'flow', 'power', 'energy_24h', 'energy_season'];

const hocEsc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const hocNum = (st) => {
  if (!st) return NaN;
  const v = parseFloat(st.state);
  return Number.isFinite(v) ? v : NaN;
};
const hocUnit = (st) => (st && st.attributes && st.attributes.unit_of_measurement) || '';
const hocClamp = (v, a, b) => Math.min(b, Math.max(a, v));

class HeatingOverviewCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._hist = null;
    this._histErr = false;
    this._histAt = 0;
    this._sig = '';
    this.shadowRoot.addEventListener('click', (e) => {
      const t = e.target.closest('[data-e]');
      if (!t || !this._config) return;
      this.dispatchEvent(new CustomEvent('hass-more-info', {
        bubbles: true, composed: true, detail: { entityId: this._config[t.dataset.e] },
      }));
    });
  }

  static getStubConfig() {
    return {
      supply_temp: 'sensor.riscaldamento_mandata',
      return_temp: 'sensor.riscaldamento_ritorno',
      flow: 'sensor.riscaldamento_portata',
      power: 'sensor.riscaldamento_potenza',
      energy_24h: 'sensor.riscaldamento_energia_24h',
      energy_season: 'sensor.riscaldamento_energia_stagione',
    };
  }

  setConfig(config) {
    for (const k of HOC_KEYS) if (!config[k]) throw new Error(`Parametro obbligatorio mancante: ${k}`);
    this._config = {
      title: 'Riscaldamento',
      temp_min: 20,
      temp_max: 80,
      history: true,
      ...config,
    };
    this._sig = '';
    this._hist = null;
    this._histAt = 0;
    if (this._hass) this.hass = this._hass;
  }

  getCardSize() { return 6; }

  set hass(hass) {
    this._hass = hass;
    if (!this._config) return;
    const sig = HOC_KEYS.map((k) => {
      const s = hass.states[this._config[k]];
      return s ? `${s.state}|${hocUnit(s)}` : 'x';
    }).join(';');
    if (this._config.history !== false && Date.now() - this._histAt > 300000) this._loadHistory();
    if (sig === this._sig) return;
    this._sig = sig;
    this._render();
  }

  async _loadHistory() {
    this._histAt = Date.now();
    const id = this._config.power;
    try {
      const end = new Date();
      const start = new Date(end.getTime() - 24 * 3600e3);
      const res = await this._hass.callWS({
        type: 'history/history_during_period',
        start_time: start.toISOString(),
        end_time: end.toISOString(),
        entity_ids: [id],
        minimal_response: true,
        no_attributes: true,
        significant_changes_only: false,
      });
      const raw = (res && res[id]) || [];
      const pts = raw
        .map((p) => ({
          t: (p.lu !== undefined ? p.lu * 1000 : Date.parse(p.last_updated)),
          v: parseFloat(p.s !== undefined ? p.s : p.state),
        }))
        .filter((p) => Number.isFinite(p.t) && Number.isFinite(p.v))
        .sort((a, b) => a.t - b.t);
      const N = 96;
      const step = (end.getTime() - start.getTime()) / N;
      const out = [];
      let j = 0;
      let last = pts.length ? pts[0].v : 0;
      for (let i = 1; i <= N; i++) {
        const tEnd = start.getTime() + i * step;
        while (j < pts.length && pts[j].t <= tEnd) { last = pts[j].v; j++; }
        out.push({ t: tEnd, v: last });
      }
      this._hist = pts.length ? out : [];
      this._histErr = false;
    } catch (e) {
      this._hist = null;
      this._histErr = true;
    }
    this._render();
  }

  _tempColor(t) {
    if (!Number.isFinite(t)) return 'var(--hc-muted)';
    const { temp_min: a, temp_max: b } = this._config;
    const k = hocClamp((t - a) / (b - a), 0, 1);
    return `color-mix(in oklab, #e8590c ${(k * 100).toFixed(0)}%, #2f80d0)`;
  }

  _sparkline(loc) {
    const W = 320, H = 92, pl = 4, pr = 4, pt = 12, pb = 18;
    if (!this._hist || !this._hist.length) {
      const msg = this._histErr ? 'Storico non disponibile' : (this._hist ? 'Nessun dato nelle ultime 24 h' : 'Carico lo storico…');
      return `<div class="empty">${msg}</div>`;
    }
    const h = this._hist;
    const peak = Math.max(...h.map((p) => p.v), 0) || 1;
    const x = (i) => pl + (i / (h.length - 1)) * (W - pl - pr);
    const y = (v) => pt + (1 - v / peak) * (H - pt - pb);
    const line = h.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)} ${y(p.v).toFixed(1)}`).join('');
    const area = `${line}L${x(h.length - 1).toFixed(1)} ${y(0).toFixed(1)}L${x(0).toFixed(1)} ${y(0).toFixed(1)}Z`;
    const lastP = h[h.length - 1];
    const u = hocUnit(this._hass.states[this._config.power]);
    const d = peak < 10 ? 1 : 0;
    const f = (v) => v.toLocaleString(loc, { maximumFractionDigits: d });
    const grid = [0, 0.5, 1].map((k) => {
      const yy = y(peak * k).toFixed(1);
      return `<line x1="${pl}" x2="${W - pr}" y1="${yy}" y2="${yy}" class="grid"/>`;
    }).join('');
    return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Potenza ultime 24 ore">
      <defs><linearGradient id="hcArea" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="var(--hc-hot)" stop-opacity=".35"/><stop offset="1" stop-color="var(--hc-hot)" stop-opacity="0"/>
      </linearGradient></defs>
      ${grid}
      <path d="${area}" fill="url(#hcArea)"/>
      <path d="${line}" fill="none" stroke="var(--hc-hot)" stroke-width="1.8" stroke-linejoin="round"/>
      <circle cx="${x(h.length - 1).toFixed(1)}" cy="${y(lastP.v).toFixed(1)}" r="3.2" fill="var(--hc-hot)" stroke="var(--hc-card)" stroke-width="1.5"/>
      <text x="${pl}" y="${pt - 3}" class="ax">max ${f(peak)} ${hocEsc(u)}</text>
      <text x="${pl}" y="${H - 4}" class="ax">−24 h</text>
      <text x="${W / 2}" y="${H - 4}" class="ax" text-anchor="middle">−12 h</text>
      <text x="${W - pr}" y="${H - 4}" class="ax" text-anchor="end">ora</text>
    </svg>`;
  }

  _render() {
    const c = this._config, S = this._hass.states;
    const loc = (this._hass.locale && this._hass.locale.language) || 'it';
    const fmt = (v, d) => (Number.isFinite(v)
      ? v.toLocaleString(loc, { minimumFractionDigits: d, maximumFractionDigits: d }) : '—');

    const sup = hocNum(S[c.supply_temp]), ret = hocNum(S[c.return_temp]);
    const flow = hocNum(S[c.flow]), pw = hocNum(S[c.power]);
    const e24 = hocNum(S[c.energy_24h]), eS = hocNum(S[c.energy_season]);
    const uT = hocUnit(S[c.supply_temp]) || '°C';
    const uF = hocUnit(S[c.flow]), uP = hocUnit(S[c.power]);
    const uE24 = hocUnit(S[c.energy_24h]), uES = hocUnit(S[c.energy_season]);
    const dT = sup - ret;

    const kW = uP === 'kW';
    const pMax = c.power_max ?? (kW ? 3 : 3000);
    const thr = c.active_threshold ?? (kW ? 0.05 : 50);
    const active = Number.isFinite(pw) && pw > thr;

    let st = { label: 'Spento', cls: 'off' };
    if (!Number.isFinite(pw)) st = { label: 'Non disponibile', cls: 'na' };
    else if (active && Number.isFinite(dT) && dT < 0) st = { label: 'Anomalia ΔT', cls: 'warn' };
    else if (active) st = { label: 'In funzione', cls: 'on' };

    const pct = Number.isFinite(pw) ? hocClamp(pw / pMax, 0, 1) * 100 : 0;
    const gauge = `<svg viewBox="0 0 200 124" role="img" aria-label="Potenza termica">
      <path d="M20 100A80 80 0 0 1 180 100" pathLength="100" class="g-track"/>
      ${pct > 0.5 ? `<path d="M20 100A80 80 0 0 1 180 100" pathLength="100" class="g-val" stroke-dasharray="${pct.toFixed(2)} 100"/>` : ''}
      <text x="100" y="88" text-anchor="middle" class="g-num">${fmt(pw, kW ? 2 : 0)}</text>
      <text x="100" y="106" text-anchor="middle" class="g-unit">${hocEsc(uP)}</text>
      <text x="20" y="120" text-anchor="middle" class="ax">0</text>
      <text x="180" y="120" text-anchor="middle" class="ax">${fmt(pMax, kW ? 1 : 0)}</text>
    </svg>`;

    const cs = this._tempColor(sup), cr = this._tempColor(ret);
    const loop = `<svg viewBox="0 0 320 156" role="img" aria-label="Circuito di riscaldamento">
      <defs><linearGradient id="hcLoop" gradientUnits="userSpaceOnUse" x1="0" y1="38" x2="0" y2="118">
        <stop offset="0" stop-color="${cs}"/><stop offset="1" stop-color="${cr}"/>
      </linearGradient></defs>
      <rect x="40" y="38" width="240" height="80" rx="16" fill="none" stroke="url(#hcLoop)" stroke-width="7"/>
      ${active ? '<rect class="flowdash" x="40" y="38" width="240" height="80" rx="16" fill="none" pathLength="100" stroke-dasharray="1.2 2.8" stroke-width="2"/>' : ''}
      <g data-e="supply_temp" class="tap">
        <text x="160" y="16" text-anchor="middle" class="lbl">MANDATA</text>
        <text x="160" y="31" text-anchor="middle" class="tv" fill="${cs}">${fmt(sup, 1)} ${hocEsc(uT)}</text>
      </g>
      <g data-e="return_temp" class="tap">
        <text x="160" y="136" text-anchor="middle" class="lbl">RITORNO</text>
        <text x="160" y="152" text-anchor="middle" class="tv" fill="${cr}">${fmt(ret, 1)} ${hocEsc(uT)}</text>
      </g>
      <text x="160" y="72" text-anchor="middle" class="lbl">ΔT</text>
      <text x="160" y="92" text-anchor="middle" class="dt">${Number.isFinite(dT) ? fmt(dT, 1) : '—'} K</text>
      <g data-e="flow" class="tap">
        <text x="160" y="108" text-anchor="middle" class="fl">${fmt(flow, flow >= 100 ? 0 : 1)} ${hocEsc(uF)}</text>
      </g>
    </svg>`;

    const tile = (key, label, val, u, d) => `<div class="tile tap" data-e="${key}">
      <div class="lbl">${label}</div><div class="tn">${fmt(val, d)}<span>${hocEsc(u)}</span></div></div>`;

    this.shadowRoot.innerHTML = `
<style>
  :host { display: block; container-type: inline-size;
    --hc-fg: var(--primary-text-color, #1d2125);
    --hc-muted: var(--secondary-text-color, #6b7280);
    --hc-card: var(--card-background-color, #fff);
    --hc-tile: var(--secondary-background-color, #f1f3f5);
    --hc-line: var(--divider-color, #d6dae0);
    --hc-hot: #e8590c;
  }
  ha-card { padding: 16px; display: block; }
  .head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
  h2 { margin: 0; font-size: 1.1rem; font-weight: 500; color: var(--hc-fg); }
  .pill { display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 999px;
    font-size: .8rem; font-weight: 500; background: var(--hc-tile); color: var(--hc-muted); white-space: nowrap; }
  .pill::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: currentColor; }
  .pill.on { background: color-mix(in srgb, var(--hc-hot) 16%, transparent); color: var(--hc-hot); }
  .pill.warn { background: color-mix(in srgb, #d9a400 20%, transparent); color: #b88700; }
  .hero { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr); gap: 16px; align-items: center; }
  .sec { margin-top: 16px; }
  .sec > .lbl { margin-bottom: 4px; }
  .tiles { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }
  .tile { background: var(--hc-tile); border-radius: 12px; padding: 12px 14px; min-width: 0; }
  .tn { font-size: 1.6rem; font-weight: 500; color: var(--hc-fg); font-variant-numeric: tabular-nums; line-height: 1.3; }
  .tn span { font-size: .85rem; color: var(--hc-muted); margin-left: 4px; font-weight: 400; }
  svg { width: 100%; height: auto; display: block; overflow: visible; }
  .tap { cursor: pointer; }
  .lbl { font-size: 10.5px; letter-spacing: .08em; text-transform: uppercase; fill: var(--hc-muted); color: var(--hc-muted); }
  .tiles .lbl, .sec > .lbl { font-size: .7rem; }
  .ax { font-size: 9px; fill: var(--hc-muted); }
  .grid { stroke: var(--hc-line); stroke-width: .6; }
  .g-track { fill: none; stroke: var(--hc-line); stroke-width: 12; stroke-linecap: round; }
  .g-val { fill: none; stroke: var(--hc-hot); stroke-width: 12; stroke-linecap: round; }
  .g-num { font-size: 32px; font-weight: 500; fill: var(--hc-fg); font-variant-numeric: tabular-nums; }
  .g-unit { font-size: 12px; fill: var(--hc-muted); }
  .tv { font-size: 15px; font-weight: 500; font-variant-numeric: tabular-nums; }
  .dt { font-size: 20px; font-weight: 500; fill: var(--hc-fg); font-variant-numeric: tabular-nums; }
  .fl { font-size: 12px; fill: var(--hc-muted); font-variant-numeric: tabular-nums; }
  .flowdash { stroke: var(--hc-card); stroke-opacity: .8; animation: hcflow 2.4s linear infinite; }
  @keyframes hcflow { to { stroke-dashoffset: -4; } }
  .empty { padding: 20px 0; text-align: center; color: var(--hc-muted); font-size: .85rem; }
  @media (prefers-reduced-motion: reduce) { .flowdash { animation: none; } }
  @container (max-width: 460px) { .hero { grid-template-columns: 1fr; } .gwrap { max-width: 260px; margin: 0 auto; width: 100%; } }
</style>
<ha-card>
  <div class="head"><h2>${hocEsc(c.title)}</h2><span class="pill ${st.cls}">${st.label}</span></div>
  <div class="hero">
    <div class="gwrap tap" data-e="power"><div class="lbl" style="text-align:center">Potenza termica</div>${gauge}</div>
    <div>${loop}</div>
  </div>
  <div class="tiles">
    ${tile('energy_24h', 'Energia ultime 24 h', e24, uE24, e24 >= 100 ? 0 : 1)}
    ${tile('energy_season', 'Da inizio stagione', eS, uES, eS >= 100 ? 0 : 1)}
  </div>
  ${c.history !== false ? `<div class="sec"><div class="lbl">Potenza ultime 24 h</div>${this._sparkline(loc)}</div>` : ''}
</ha-card>`;
  }
}

customElements.define('heating-overview-card', HeatingOverviewCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'heating-overview-card',
  name: 'Heating overview',
  description: 'Overview del circuito di riscaldamento: potenza, mandata/ritorno, portata, energia.',
});
