"""A4 livello serbatoio chiare — confronto fra generatori di corrente (REQ-IF-003).

Topologie:
  S  : PNP + stack di 2 diodi sulla base, Re sull'emettitore  (schema proposto il 2026-10-17)
  M  : specchio PNP con resistori di emettitore, riferimento verso GPIO basso
Uscita: corrente nel sender Rs (0..190 ohm) attraverso D_f, a vari VCC, T, Rs.
Modelli generici (models.lib): solo confronto fra topologie.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spice  # noqa: E402

VOL = 0.20  # tensione del GPIO a livello basso con ~2..8 mA (ipotesi, da verificare su datasheet ESP32-S3)


def net_S(vcc, rs, re, rpu=10e3, rben=1e3, df="D4148"):
    return f"""
Vcc vcc 0 {vcc}
Re vcc e {re}
Q1 c b e QP3906
Db1 vcc d1 D4148
Db2 d1 b D4148
Rpu vcc b {rpu}
Rben b g {rben}
Vg g 0 {VOL}
Df c n {df}
Vm n n2 0
Rs n2 0 {rs}
Vdum x 0 0
"""


def net_M(vcc, rs, re1, re2, rref, df="D4148"):
    return f"""
Vcc vcc 0 {vcc}
Re1 vcc e1 {re1}
Re2 vcc e2 {re2}
Q1 bm bm e1 QP3906
Q2 c bm e2 QP3906
Rref bm g {rref}
Vg g 0 {VOL}
Df c n {df}
Vm n n2 0
Rs n2 0 {rs}
Vdum x 0 0
"""


def point(net, temp):
    r = spice.run(net, "dc Vdum 0 0 1", ["i(vm)", "v(n)"], temp=temp)
    return float(np.atleast_1d(r["i(vm)"])[0]), float(np.atleast_1d(r["v(n)"])[0])


def table(build, label, temps=(-10, 25, 60), vccs=(3.2, 3.3, 3.4), rss=(0, 95, 190, 1e6)):
    print(f"\n=== {label} ===")
    base = {}
    for rs in rss:
        for t in temps:
            for v in vccs:
                i, vn = point(build(v, rs), t)
                base[(rs, t, v)] = (i, vn)
    ref = base[(95, 25, 3.3)][0]
    print(f"I(Rs=95, 25C, 3.3V) = {ref*1e3:.3f} mA")
    print("Rs   T    VCC   I[mA]   dI/Iref[%]  V(N)[V]")
    for rs in rss:
        for t in temps:
            for v in vccs:
                i, vn = base[(rs, t, v)]
                print(f"{rs:>7.0f} {t:>4} {v:>4.1f} {i*1e3:7.3f} {100*(i-ref)/ref:9.2f} {vn:8.3f}")
    return base


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "S"
    if which == "S":
        re = float(sys.argv[2]) if len(sys.argv) > 2 else 68
        table(lambda v, rs: net_S(v, rs, re), f"S Re={re}")
    else:
        re1, re2, rref = (float(x) for x in sys.argv[2:5])
        table(lambda v, rs: net_M(v, rs, re1, re2, rref), f"M Re1={re1} Re2={re2} Rref={rref}")
