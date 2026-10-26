"""Corrente nel LED del remote pilotato da BSS84 high-side a 3V3 (IF-007, a6).
Modello a legge quadratica, beta da g_fs min 0,05 S @ I_D 0,1 A (onsemi BSS84);
Vth max 2,0 V (onsemi), a -20 C stima 2,14 V (3 mV/C, segno dedotto). LED: Vf ipotizzata
1,9-2,1 V (non misurata), R interna del remote 1 kOhm. Non e' un modello SPICE del costruttore."""
from scipy.optimize import brentq
BETA = 0.05**2 / (2 * 0.1)

def i_led(vs, vg, vth, rtot, vf):
    vov = (vs - vg) - vth
    if vov <= 0:
        return 0.0
    def f(i):
        vsd = vs - vf - i * rtot
        if vsd <= 0:
            return i
        idm = BETA / 2 * vov**2 if vsd >= vov else BETA * (vov * vsd - vsd**2 / 2)
        return i - idm
    return brentq(f, 0, 0.01)

for vth in (1.7, 2.0, 2.14):
    for vf in (1.9, 2.1):
        for rser in (0, 220, 470):
            print(vth, vf, rser, [round(i_led(3.135, vg, vth, 1000 + rser, vf) * 1e3, 2) for vg in (0.1, 0.3, 0.5)])
