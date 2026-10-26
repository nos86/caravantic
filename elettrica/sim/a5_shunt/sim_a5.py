"""Simulazione A5: rete di ingresso ADS1115 per due shunt 200 A / 75 mV low-side (REQ-IF-005).

Esecuzione (da questa cartella):  py -3 sim_a5.py
Produce out/results.json e tre PNG. Tutti i dati dei componenti sono quelli del registro
(docs/components.md); i modelli SPICE sono generici (models.lib), non dei costruttori.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from spice import run

VARIANT = os.environ.get("A5_VARIANT", "base")   # base = 3,3k/47k ; 10k = 10k/143k con filtro riscalato
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out" if VARIANT == "base" else f"out_{VARIANT}")
os.makedirs(OUT, exist_ok=True)

K = 0.375e-3            # V/A (shunt 75 mV / 200 A)
LSB = 0.256 / 2**15     # ADS1115 a FSR +-0,256 V
NOM = dict(rs1=3.3e3, rs2=3.3e3, rb1=47e3, rb2=47e3, cd=100e-9, cc1=10e-9, cc2=10e-9,
           rk1=0.05, rk2=0.05, zd=710e3, il1=0.0, il2=0.0)
if VARIANT == "10k":
    NOM.update(rs1=10e3, rs2=10e3, rb1=143e3, rb2=143e3, cd=33e-9, cc1=3.3e-9, cc2=3.3e-9)
elif VARIANT == "10k150":   # variante adottata 2026-10-18: 143k non e' in stock su LCSC, si usa 150k (E24)
    NOM.update(rs1=10e3, rs2=10e3, rb1=150e3, rb2=150e3, cd=33e-9, cc1=3.3e-9, cc2=3.3e-9)
RS0 = NOM["rs1"]


def netlist(p, vg="0", vs="0", ac_vs=False, ac_vg=False):
    v2 = f"V2 nl nb DC {vs}" + (" AC 1" if ac_vs else "")
    v1 = f"Vg nb 0 DC {vg}" + (" AC 1" if ac_vg else "")
    return f"""Vdd vdd 0 3.3
{v1}
{v2}
Rk1 nb nbk {p['rk1']}
Rk2 nl nlk {p['rk2']}
RS1 nbk ainn {p['rs1']}
RS2 nlk ainp {p['rs2']}
RB1 ainn vdd {p['rb1']}
RB2 ainp vdd {p['rb2']}
CD ainp ainn {p['cd']}
CC1 ainn 0 {p['cc1']}
CC2 ainp 0 {p['cc2']}
DL1 0 ainn DGEN
DH1 ainn vdd DGEN
DL2 0 ainp DGEN
DH2 ainp vdd DGEN
Il1 vdd ainn DC {p['il1']}
Il2 vdd ainp DC {p['il2']}
RDIF ainp ainn {p['zd']}
RCM1 ainn 0 100Meg
RCM2 ainp 0 100Meg
"""


def dc_grid(p, v2_step, vg_vals):
    """Ritorna (v2, vg, vainp, vainn) con vg esterno, v2 interno."""
    vg0, vg1, vgs = vg_vals
    r = run(netlist(p), f"dc V2 -0.075 0.075 {v2_step} Vg {vg0} {vg1} {vgs}", ["v(ainp)", "v(ainn)"])
    n = int(round(0.15 / v2_step)) + 1
    ap, an = r["v(ainp)"].reshape(-1, n), r["v(ainn)"].reshape(-1, n)
    v2 = r[list(r)[0]][:n]
    return v2, np.arange(ap.shape[0]), ap, an


def calibrated_error(vd, v2, ivg0, cal_hi=0.0375):
    """vd[vg, v2]: taratura (zero e guadagno) a vg=0, errore in A a tutte le righe."""
    i0 = int(np.argmin(abs(v2)))
    ih = int(np.argmin(abs(v2 - cal_hi)))
    off = vd[ivg0, i0]
    gain = (vd[ivg0, ih] - off) / (v2[ih] / K)       # V per A, al punto di griglia piu' vicino
    est = (vd - off) / gain
    return est - (v2 / K)[None, :]


# ---------------------------------------------------------------- 1. nominale
v2, _, ap, an = dc_grid(NOM, 0.005, (-0.15, 0.15, 0.05))
vgs = np.arange(-0.15, 0.1500001, 0.05)
vd = ap - an
iz = int(np.argmin(abs(vgs)))
err = calibrated_error(vd, v2, iz)
res = {"nominale": {
    "gain_rete": float((vd[iz, -1] - vd[iz, 0]) / (0.15)),
    "min_nodo_V_vg0": float(min(ap[iz].min(), an[iz].min())),
    "min_nodo_V_per_vg": {f"{g:+.2f}": float(min(ap[i].min(), an[i].min())) for i, g in enumerate(vgs)},
    "risoluzione_A_per_LSB": float(LSB / ((vd[iz, -1] - vd[iz, 0]) / (0.15 / K))),
    "fs_ADC_a_200A_mV": float(vd[iz, -1] * 1e3),
    "errore_A_vs_offset_massa_a_0A_10A_200A": {
        f"{g:+.2f}": [float(err[i, int(np.argmin(abs(v2 - x * K)))]) for x in (0, 10, 200)] for i, g in enumerate(vgs)},
}}

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(v2 / K, ap[iz], label="AINP"); ax[0].plot(v2 / K, an[iz], label="AINN")
ax[0].axhline(0, color="k", lw=0.5); ax[0].set_xlabel("corrente shunt [A]"); ax[0].set_ylabel("tensione ingresso ADC [V]")
ax[0].set_title("Tensioni agli ingressi (offset di massa 0)"); ax[0].legend(); ax[0].grid(alpha=.3)
for i, g in enumerate(vgs):
    ax[1].plot(v2 / K, err[i], label=f"{g*1e3:+.0f} mV")
ax[1].set_xlabel("corrente shunt [A]"); ax[1].set_ylabel("errore dopo taratura a offset 0 [A]")
ax[1].set_title("Errore vs offset di massa (rete nominale)"); ax[1].legend(fontsize=7); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "01_dc.png"), dpi=110); plt.close()

# ---------------------------------------------------------------- 2. Monte Carlo
rng = np.random.default_rng(1)
N = 300
errs = []   # [vg=-50mV, +50mV] x [10 A, -10 A, 200 A]
lowest = []
for n in range(N):
    q = dict(NOM)
    for k in ("rs1", "rs2", "rb1", "rb2"):
        q[k] = NOM[k] * (1 + rng.uniform(-1e-3, 1e-3))
    q["cc1"] = NOM["cc1"] * (1 + rng.uniform(-0.01, 0.01))
    q["cc2"] = NOM["cc2"] * (1 + rng.uniform(-0.01, 0.01))
    q["cd"] = NOM["cd"] * (1 + rng.uniform(-0.1, 0.1))
    q["rk1"] = rng.uniform(0.03, 0.07); q["rk2"] = rng.uniform(0.03, 0.07)
    q["zd"] = NOM["zd"] * (1 + rng.uniform(-0.2, 0.2))
    q["il1"] = rng.uniform(0, 5e-9); q["il2"] = rng.uniform(0, 5e-9)
    v2m, _, a_p, a_n = dc_grid(q, 0.00375, (-0.05, 0.05, 0.05))
    d = a_p - a_n
    e = calibrated_error(d, v2m, 1)
    pick = lambda x: int(np.argmin(abs(v2m - x * K)))
    errs.append([e[0, pick(10)], e[0, pick(-10)], e[0, pick(200)], e[2, pick(10)], e[2, pick(-10)], e[2, pick(200)]])
    lowest.append(min(a_p[1].min(), a_n[1].min()))
errs = np.array(errs)
labels = ["vg=-50mV,10A", "vg=-50mV,-10A", "vg=-50mV,200A", "vg=+50mV,10A", "vg=+50mV,-10A", "vg=+50mV,200A"]
res["monte_carlo_300"] = {
    "ipotesi": "R 0,1 % uniforme; C_CM +-1 %; C_DIFF +-10 %; fili Kelvin 0,03-0,07 ohm; Z diff ADC 710k +-20 %; perdite clamp 0-5 nA; taratura zero e guadagno a offset 0",
    "errore_A_max_assoluto": {l: float(np.abs(errs[:, i]).max()) for i, l in enumerate(labels)},
    "errore_A_p95": {l: float(np.percentile(np.abs(errs[:, i]), 95)) for i, l in enumerate(labels)},
    "min_nodo_V_vg0": float(min(lowest)),
}
plt.figure(figsize=(6, 4))
plt.hist(errs[:, [0, 1, 3, 4]].ravel(), bins=40)
plt.xlabel("errore a +-10 A con offset di massa +-50 mV [A]"); plt.ylabel("campioni"); plt.title("Monte Carlo (300)")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "02_montecarlo.png"), dpi=110); plt.close()

# ---------------------------------------------------------------- 3. AC
freqs = None
ac = {}
for name, kw, pp in (("diff", dict(ac_vs=True), NOM),
                     ("cm_to_diff", dict(ac_vg=True), dict(NOM, cc1=NOM["cc1"] * 1.01, cc2=NOM["cc2"] * 0.99, rs1=RS0 * 1.001, rs2=RS0 * 0.999))):
    r = run(netlist(pp, **kw), "ac dec 20 1 1meg\nlet vdm = mag(v(ainp)-v(ainn))", ["vdm"])
    f = r[list(r)[0]]
    ac[name] = (f, r["vdm"])
fd, gd = ac["diff"]
fc, gc = ac["cm_to_diff"]
pick = lambda f, x: int(np.argmin(abs(np.log10(f / x))))
res["ac"] = {
    "guadagno_diff_dc": float(gd[0]),
    "f_3dB_diff_Hz": float(fd[int(np.argmax(gd < gd[0] / np.sqrt(2)))]),
    "cm_to_diff_dB": {f"{x} Hz": float(20 * np.log10(gc[pick(fc, x)])) for x in (1, 50, 100, 1000, 10000, 100000)},
    "diff_attenuazione_dB": {f"{x} Hz": float(20 * np.log10(gd[pick(fd, x)] / gd[0])) for x in (50, 1000, 10000, 100000)},
    "ipotesi_cm": "C_CM +-1 % in senso opposto, R_S +-0,1 % in senso opposto",
}
rdiff = 2 * (NOM["rs1"] * NOM["rb1"] / (NOM["rs1"] + NOM["rb1"]))
f3 = res["ac"]["f_3dB_diff_Hz"]
kT4 = 4 * 1.380649e-23
res["rumore_termico"] = {
    "R_diff_ohm": rdiff,
    "uVrms_a_25C": float(np.sqrt(kT4 * 298 * rdiff * f3 * np.pi / 2) * 1e6),
    "uVrms_a_60C": float(np.sqrt(kT4 * 333 * rdiff * f3 * np.pi / 2) * 1e6),
    "LSB_ADS1115_uV": LSB * 1e6,
    "nota": "solo rumore Johnson delle resistenze di sorgente, banda equivalente pi/2*f3dB; il rumore dell'ADC (1 LSB rms a 8/64 SPS) e' a parte",
}
plt.figure(figsize=(6, 4))
plt.semilogx(fd, 20 * np.log10(gd), label="differenziale")
plt.semilogx(fc, 20 * np.log10(gc), label="modo comune -> differenziale")
plt.xlabel("Hz"); plt.ylabel("dB (rispetto a 1 V)"); plt.grid(alpha=.3, which="both"); plt.legend(); plt.title("Risposta in frequenza")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "03_ac.png"), dpi=110); plt.close()

# ---------------------------------------------------------------- 4. guasti +-24 V
fault = {}
for vf in (24.0, -24.0):
    body = netlist(NOM).replace("Rk2 nl nlk 0.05\n", "").replace("V2 nl nb DC 0\n", "") + \
        f"Vf nlk0 0 DC {vf}\nRfs nlk0 nlk 0.01\n" + \
        "DE1 0 ainn DGEN\nDE2 0 ainp DGEN\n"
    r = run(body, "dc Vf %g %g 1" % (vf, vf), ["v(ainp)", "v(ainn)", "@rs2[i]", "i(vdd)"])
    fault[f"{vf:+.0f} V sul capo lato carichi (RS2)"] = {
        "i_RS2_mA": float(r["@rs2[i]"][0] * 1e3),
        "i_assorbita_dal_rail_3V3_mA (negativa = il rail eroga)": float(r["i(vdd)"][0] * 1e3),
        "V_ainp": float(r["v(ainp)"][0]),
    }
res["guasti"] = fault

with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
