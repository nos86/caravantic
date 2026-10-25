"""Candidati dello specchio: deriva, rail, compliance, guasti. Salva out/final_m.json."""
import json
import sim_a4 as S

def I(n, t=25): return S.point(n, t)[0]

def solve(re1, re2, target=8e-3):
    lo, hi = 20.0, 6000.0
    for _ in range(16):
        mid = (lo + hi) / 2
        (lo, hi) = (mid, hi) if I(S.net_M(3.3, 95, re1, re2, mid)) > target else (lo, mid)
    return (lo + hi) / 2

res = {}
for tag, re1, re2 in (("EQ47", 47, 47), ("RATIO", 376, 47)):
    rref = solve(re1, re2)
    n = lambda v, rs: S.net_M(v, rs, re1, re2, rref)
    i0 = I(n(3.3, 95))
    d = lambda i: round(100 * (i - i0) / i0, 2)
    r = dict(re1=re1, re2=re2, rref=round(rref, 1), i0_mA=round(i0 * 1e3, 3))
    r["dT_-10"] = d(I(n(3.3, 95), -10)); r["dT_60"] = d(I(n(3.3, 95), 60))
    r["dV_-3%"] = d(I(n(3.2, 95))); r["dV_+3%"] = d(I(n(3.4, 95)))
    # compliance: caso peggiore freddo, rail basso, sender 190 e 209 (+10 %)
    for rs in (0, 190, 209):
        r[f"I_Rs{rs}_cold_low"] = round(I(n(3.2, rs), -10) * 1e3, 3)
    r["I_Rs190_hot_hi"] = round(I(n(3.4, 190), 60) * 1e3, 3)
    # sender aperto
    r["Vopen_cold_low"] = round(S.point(n(3.2, 1e7), -10)[1], 3)
    r["Vopen_hot_hi"] = round(S.point(n(3.4, 1e7), 60)[1], 3)
    # corrente di riferimento (GPIO)
    iref = S.spice.run(n(3.3, 95), "dc Vdum 0 0 1", ["i(vg)"], temp=25)["i(vg)"]
    r["I_gpio_mA"] = round(abs(float(iref[0])) * 1e3, 3)
    res[tag] = r
    print(tag, json.dumps(r))
json.dump(res, open("out/final_m.json", "w"), indent=1)
