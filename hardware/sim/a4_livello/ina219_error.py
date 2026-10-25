"""Errore di misura di Rs con INA219 (misura ratiometrica V_bus / I_shunt), dai limiti del datasheet SBOS448G.

Modello (limiti dichiarati, NON include l'offset del bus, il cui valore non e' leggibile dal grafico di Fig. 5):
  - offset shunt PGA/1: +-100 uV (A), +-50 uV (B), uniforme;
  - errore di misura della corrente: +-0,5 % (A) / +-0,3 % (B) a 25 C; +-1 % / +-0,5 % su -25..85 C;
  - errore della tensione di bus: +-0,5 % a 25 C; +-1 % su -25..85 C;
  - tolleranza di Rsh 0,1 %;
  - corrente nei pin IN-: 20 uA + V/320 kohm, NON corretta nel caso peggiore (poi corretta in firmware).
Eccitazione: Vexc_eff = 2,5 V (GPIO - 1N4148WS), R_exc + Rsh = 310 ohm.
Risultato: errore su Rs in % del fondo scala (190 ohm), caso peggiore (somma) e Monte Carlo (percentili 95).
"""
import numpy as np

rng = np.random.default_rng(1)
VEXC, RSER, RSH = 2.5, 310.0, 3.3
FS = 190.0


def run(grade, over_temp, correct_bias, n=200000):
    off = {"A": 100e-6, "B": 50e-6}[grade]
    ei = {("A", 0): 0.005, ("A", 1): 0.01, ("B", 0): 0.003, ("B", 1): 0.005}[(grade, over_temp)]
    ev = 0.01 if over_temp else 0.005
    out = {}
    for rs in (10, 95, 190):
        i = VEXC / (RSER + rs)            # corrente nello shunt
        vb = i * rs                       # tensione sul sender (approssimata)
        # errori casuali
        o = rng.uniform(-off, off, n)
        gi = rng.uniform(-ei, ei, n)
        gv = rng.uniform(-ev, ev, n)
        rt = rng.uniform(-0.001, 0.001, n)
        ibias = 20e-6 + vb / 320e3
        ibias_res = ibias * (0.25 if correct_bias else 1.0)
        i_true_sender = i - ibias               # corrente reale nel sender
        vb_true = i_true_sender * rs
        vsh_meas = (i * RSH * (1 + rt) + o) * (1 + gi)
        i_est = vsh_meas / RSH - (ibias - ibias_res)   # il firmware sottrae la parte corretta
        rs_est = vb_true * (1 + gv) / i_est
        err = (rs_est - rs) / FS * 100
        # caso peggiore (somma lineare dei limiti)
        wc = (off / (i * RSH) + ei + ev + 0.001 + ibias_res / i) * rs / FS * 100
        out[rs] = (np.percentile(np.abs(err), 95), wc)
    return out


print("grado  T       bias   Rs   p95 [%FS]  caso peggiore [%FS]")
for g in "AB":
    for ot, tn in ((0, "25C"), (1, "-25..85C")):
        for cb in (False, True):
            r = run(g, ot, cb)
            for rs, (p95, wc) in r.items():
                print(f"{g}     {tn:<9} {'corr ' if cb else 'no   '}  {rs:>4}   {p95:7.2f}   {wc:7.2f}")
