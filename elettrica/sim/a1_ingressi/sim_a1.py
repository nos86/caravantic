"""A1 — ingressi digitali IN-CAB / IN-CEL: verifica SPICE (ngspice) contro REQ-EL-006 / REQ-EL-008.

Circuito (per canale, identico per i due ingressi), opto Toshiba TLP293, LED in conduzione continua:
  IN -- R_S -- DZ (BZT52C3V3, catodo verso IN) -- LED TLP293 -- GND
  D1 (1N4148WS) antiparallelo al LED (protezione inversa: con ingresso negativo conducono D1 e DZ in diretta)
  Varianti con A1_TOPO: series (D1 BAV21W in serie), shunt (D1 verso massa + D antiparallelo), shunt_noD2, noD1 (default)
  uscita: fototransistore -> R_PU a 3,3 V -> GPIO in

Uso:  python sim_a1.py [GB|NONGB] [R_S_kohm R_PU_kohm]
      (default: valori di DEFAULTS per la variante; scrive out/results_<tag>.json e i grafici)
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from spice import run

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ---- Dimensionamento -------------------------------------------------------
P = dict(R_S=8.2e3, R_PU=12e3, VDD=3.3, topo="noD1")
DEFAULTS = {"GB": (8.2e3, 12e3), "NONGB": (8.2e3, 22e3)}              # (R_S, R_PU) per variante
VIL, VIH = 0.25 * 3.3, 0.75 * 3.3          # ESP32-S3 datasheet v2.2, tab. 5-4

# ---- Opto: varianti ---------------------------------------------------------
# CTR lineare (IF = 0,5 mA, VCE = 5 V): GB 100..600 %, non ranked 50..600 %.
# CTR saturo (IF = 1 mA, VCE = 0,4 V): GB min 30 % (typ 60 %); NON ranked: min NON dato -> assunto
# proporzionale al CTR lineare minimo (metà del GB, 15 %) — ASSUNZIONE.
# RCS (resistore di saturazione del modello) tarato con fit_opto.py: GB 0,95k -> 31,5 %, tipico 0,45k -> 62 %,
# non-GB 2,0k -> 16 %.
# Derating a caldo + invecchiamento: x0,84 x0,5 = x0,42 sul CTR (lineare e saturo), valore GENERICO ripreso dal
# progetto precedente (curve TLP293 Fig. 11.12/11.13 non lette): RCS diviso per 0,42.
# ATTENZIONE: con LED in continuo la corrente scende sotto 0,5 mA (punto di CTR garantito) vicino a 8 V:
# li' il CTR e' quello della curva, NON garantito. Il modello usa il CTR lineare costante.
DER = 0.84 * 0.5
VARIANTS = {
    "GB":    dict(ctr_min=1.0, ctr_typ=3.0, ctr_max=6.0, rcs_min=0.95e3, rcs_typ=0.45e3),
    "NONGB": dict(ctr_min=0.5, ctr_typ=2.0, ctr_max=6.0, rcs_min=2.0e3,  rcs_typ=0.45e3),
}


def corners(var):
    v = VARIANTS[var]
    return {
        # ON_worst: -10 °C, ZD alto, CTR e saturazione minimi derated, opto lento
        "ON_worst":  dict(T=-10, BV=3.3, CTR=v["ctr_min"] * DER, RCS=v["rcs_min"] / DER, CJC="30p", TF="9n"),
        "tipico":    dict(T=25,  BV=3.1, CTR=v["ctr_typ"], RCS=v["rcs_typ"], CJC="12p", TF="3n"),
        # OFF_worst / stress: ZD basso, CTR massimo (massima corrente e massima sensibilita' alle perdite)
        "OFF_worst": dict(T=60,  BV=2.9, CTR=v["ctr_max"], RCS=v["rcs_typ"], CJC="12p", TF="3n"),
    }


def netlist(c, vin_src, ri=0.5, p=P):
    """p['topo']: 'series' (D1 in serie, D2 antiparallelo) | 'shunt' (D1 verso massa, D2 antiparallelo)
    | 'shunt_noD2' (D1 verso massa, nessun antiparallelo). Con 'shunt' D1 (catodo sul nodo, anodo a GND) clampa
    gli ingressi negativi a -0,7 V: non serve un diodo da 250 V."""
    topo = p.get("topo", "series")
    if topo == "series":
        front = "D1 n1 n2 DBAV21\n"
    elif topo == "noD1":                      # nessun D1: la protezione inversa e' D2 + ZD in diretta
        front = "VJ n1 n2 0\n"
    else:
        front = f"VJ n1 n2 0\nD1 0 n1 {p.get('d1model', 'D4148')}\n"
    d2 = "" if topo == "shunt_noD2" else "D2 0 n3b D4148\n"
    return f"""
.param VZ={c['BV']}
{vin_src}
RSRC src in {ri}
RS in n1 {p['R_S']}
{front}DZ n3 n2 DZ33
RZL n2 n3 200k
VLED n3 n3b 0
{d2}XU n3b 0 out 0 TLP293 params: CTR={c['CTR']} CJCPT={c['CJC']} TFPT={c['TF']} RCS={c['RCS']}
RPU vdd out {p['R_PU']}
VDD vdd 0 {p['VDD']}
"""


def dc_sweep(c, p=P):
    d = run(netlist(c, "VSRC src 0 DC 0", p=p), "dc VSRC -20 30 0.02",
            ["v(out)", "i(VLED)", "i(VSRC)"], temp=c["T"])
    v = d["v-sweep"]
    vout, iled, iin = d["v(out)"], d["i(vled)"], -d["i(vsrc)"]
    pos = v > 0
    inact = v[pos][vout[pos] > VIH]
    bad = np.where(vout[pos] >= VIL)[0]            # punti in cui l'uscita NON e' ancora "attivo"
    if len(bad) == 0:
        v_act = float(v[pos][0])
    elif bad.max() + 1 >= len(v[pos]):
        v_act = float("nan")                       # mai attivo garantito fino a 30 V
    else:
        v_act = float(v[pos][bad.max() + 1])       # primo Vin da cui l'uscita resta sempre sotto VIL
    v_inact = float(inact.max()) if len(inact) else float("nan")
    return v, vout, iled, iin, v_act, v_inact


if __name__ == "__main__":
    var = (sys.argv[1] if len(sys.argv) > 1 else "GB").upper()
    CORNERS = corners(var)
    P["R_S"], P["R_PU"] = DEFAULTS[var]
    tag = var
    if len(sys.argv) > 3:
        P["R_S"], P["R_PU"] = float(sys.argv[2]) * 1e3, float(sys.argv[3]) * 1e3
        tag = f"{var}_{sys.argv[2]}k_{sys.argv[3]}k"
    P["topo"] = os.environ.get("A1_TOPO", "noD1")
    if P["topo"] != "noD1":
        tag += "_" + P["topo"]
    res = {}

    # ---- 1. Caratteristica statica ------------------------------------------
    fig, ax = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
    for name, c in CORNERS.items():
        v, vout, iled, iin, v_act, v_inact = dc_sweep(c)
        res[f"dc_{name}"] = dict(
            Vin_attivo_garantito=round(v_act, 2),
            Vin_max_inattivo=round(v_inact, 2),
            I_in_mA_at={k: round(float(np.interp(k, v, iin)) * 1e3, 3) for k in (-16, 0, 2, 8, 10, 11.5, 12.8, 14.4, 16, 24, 30)},
        )
        ax[0].plot(v, vout, label=name)
        ax[1].plot(v, iled * 1e3, label=name)
        ax[2].plot(v, iin * 1e3, label=name)
    ax[0].axhline(VIL, ls="--", c="gray"); ax[0].axhline(VIH, ls="--", c="gray")
    ax[0].set_ylabel("V(out) [V]"); ax[1].set_ylabel("I LED [mA]"); ax[2].set_ylabel("I ingresso [mA]")
    ax[2].set_xlabel("V ingresso [V]")
    for a in ax:
        a.axvspan(2, 8, color="orange", alpha=0.1); a.grid(True); a.legend(fontsize=8)
    ax[0].set_title(f"A1 / TLP293 {var} — caratteristica statica (fascia arancio: 2–8 V non specificata)")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, f"01_dc_{tag}.png"), dpi=110); plt.close(fig)

    # ---- 2. Risposta a gradino: accensione e spegnimento ---------------------
    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    for name, c in CORNERS.items():
        for vin in (8, 11.5, 14.4):
            src = f"VSRC src 0 PWL(0 0 1m 0 1.001m {vin} 21m {vin} 21.001m 0 41m 0)"
            d = run(netlist(c, src), "tran 2u 41m", ["v(out)"], temp=c["T"])
            t, vo = d["time"], d["v(out)"]
            on = (t > 1e-3) & (t < 21e-3) & (vo < VIL)
            off = (t > 21e-3) & (vo > VIH)
            res.setdefault(f"gradino_{name}", {})[f"Vin={vin}"] = dict(
                t_attivo_us=None if not on.any() else round((t[on][0] - 1e-3) * 1e6, 1),
                t_inattivo_us=None if not off.any() else round((t[off][0] - 21e-3) * 1e6, 1),
                Vout_a_regime=round(float(np.interp(20.9e-3, t, vo)), 3))
            if vin == 8:
                ax.plot(t * 1e3, vo, label=f"{name} 8 V")
    ax.axhline(VIL, ls="--", c="gray"); ax.axhline(VIH, ls="--", c="gray")
    ax.set_xlabel("t [ms]"); ax.set_ylabel("V(out) [V]"); ax.grid(True); ax.legend(fontsize=8)
    ax.set_title(f"TLP293 {var} — gradino 0 → 8 V → 0")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, f"02_gradino_{tag}.png"), dpi=110); plt.close(fig)

    # ---- 3. Transitori ISO: sollecitazione dei componenti ---------------------
    def stress(tg, src, ri, tstop, step, c):
        d = run(netlist(c, src, ri=ri), f"tran {step} {tstop}",
                ["v(in)", "v(n1,n2)", "v(n3b)", "i(VLED)", "v(in,n1)", "v(n1)"], temp=c["T"])
        t = d["time"]
        p_rs = d["v(in,n1)"] ** 2 / P["R_S"]
        res[f"iso_{tg}"] = dict(
            Vin_picco=round(float(np.abs(d["v(in)"]).max()), 1),
            Vr_D1_max=round(float(-d["v(n1,n2)"].min()), 1),
            V_nodo_min_max=(round(float(d["v(n1)"].min()), 2), round(float(d["v(n1)"].max()), 2)),
            V_LED_inversa_max=round(float(-d["v(n3b)"].min()), 2),
            I_LED_max_mA=round(float(d["i(vled)"].max()) * 1e3, 2),
            P_RS_picco_W=round(float(p_rs.max()), 3),
            E_RS_mJ=round(float(np.trapezoid(p_rs, t)) * 1e3, 3),
        )

    cw = CORNERS["OFF_worst"]
    # Load dump ISO 16750-2 Test A: Us 101 V, Ri 0,5 ohm, td 400 ms, tr 10 ms (su 13,5 V)
    stress("loaddump", "VSRC src 0 PWL(0 13.5 10m 13.5 20m 101 420m 13.5 600m 13.5)", 0.5, "600m", "20u", cw)
    pulses = {
        "pulse1": ("VSRC src 0 PWL(0 0 10u 0 11u -150 2.011m 0 3m 0)", 10, "3m", "0.2u"),
        "pulse2a": ("VSRC src 0 PWL(0 13.5 10u 13.5 11u 125.5 61u 13.5 200u 13.5)", 2, "200u", "0.05u"),
        # 3a/3b: livelli NON verificati (assunti -220 / +150 V), Ri 50 ohm, td 150 ns
        "pulse3a": ("VSRC src 0 PWL(0 13.5 10u 13.5 10.005u -206.5 10.155u 13.5 12u 13.5)", 50, "12u", "0.5n"),
        "pulse3b": ("VSRC src 0 PWL(0 13.5 10u 13.5 10.005u 163.5 10.155u 13.5 12u 13.5)", 50, "12u", "0.5n"),
    }
    for ptag, (src, ri, tstop, step) in pulses.items():
        stress(ptag, src, ri, tstop, step, cw)
    for ftag, v in (("fault_+24V", 24), ("fault_-16V", -16)):
        stress(ftag, f"VSRC src 0 DC {v}", 0.5, "60m", "10u", cw)

    with open(os.path.join(OUT, f"results_{tag}.json"), "w") as f:
        json.dump(dict(variant=tag, params=P, corners=CORNERS, results=res), f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
