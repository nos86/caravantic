"""Taratura della velocita' e della saturazione del modello TLP293 sui dati del datasheet Toshiba Rev.7.0."""
from spice import run


def tr_tf(RL, IC, cjc, tf, ctr=2.0):
    vcc = 2.0 + IC * RL
    body = f"""
IF1 0 a PULSE(0 {IC/ctr} 10u 100n 100n 400u 1m)
XU a 0 c 0 TLP293 params: CTR={ctr} CJCPT={cjc} TFPT={tf} RCS=0.1
RL vcc c {RL}
VCC vcc 0 {vcc}
"""
    d = run(body, "tran 20n 900u", ["v(c)"])
    t, v = d["time"], d["v(c)"]
    hi, lo = vcc, v[(t > 380e-6) & (t < 400e-6)].mean()
    a10, a90 = lo + 0.1 * (hi - lo), lo + 0.9 * (hi - lo)
    on = t > 10e-6; off = t > 410.1e-6
    t90 = t[on & (v < a90)][0]; t10 = t[on & (v < a10)][0]
    u10 = t[off & (v > a10)][0]; u90 = t[off & (v > a90)][0]
    return round((t10 - t90) * 1e6, 1), round((u90 - u10) * 1e6, 1)


def sat_ctr(ctr, rcs, i_f=1e-3, vce=0.4):
    body = f"""
IF1 0 a DC {i_f}
XU a 0 c 0 TLP293 params: CTR={ctr} RCS={rcs}
VC c 0 DC {vce}
"""
    d = run(body, "op", ["i(VC)"])
    return round(float(-d["i(vc)"][0]) / i_f * 100, 1)


if __name__ == "__main__":
    for cjc in (6e-12, 8e-12, 10e-12):
        for tf in (1e-9, 2e-9):
            print(f"CJC={cjc*1e12:3.0f}p TF={tf*1e9:3.0f}n  tr/tf RL100 {tr_tf(100, 2e-3, cjc, tf)}")
    for ctr, rcs in ((1.0, 1.2e3), (1.0, 2.0e3), (2.0, 0.5e3), (3.0, 0.5e3)):
        print(f"CTR_lin={ctr} RCS={rcs:.0f}: CTR_sat(1 mA, 0.4 V) = {sat_ctr(ctr, rcs)} %")
