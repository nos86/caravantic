"""Esplora Re/Rref dello specchio: porta I a 8 mA a 25 C / 3,3 V / 95 ohm e misura deriva, sensibilita' al rail, compliance."""
import sys
import sim_a4 as S

def I(net, t):
    return S.point(net, t)[0]

def solve_rref(re, target=8e-3):
    lo, hi = 50.0, 1500.0
    for _ in range(14):
        mid = (lo + hi) / 2
        i = I(S.net_M(3.3, 95, re, re, mid), 25)
        if i > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

print("Re    Rref    I25[mA] dT(-10) dT(60) dV(-3%) dV(+3%)  Isat(190,-10C) Iref[mA]")
for re in (27, 40, 56, 82, 120):
    rref = solve_rref(re)
    n = lambda v, rs: S.net_M(v, rs, re, re, rref)
    i0 = I(n(3.3, 95), 25)
    d = lambda i: 100 * (i - i0) / i0
    print(f"{re:>4} {rref:7.1f} {i0*1e3:7.3f} {d(I(n(3.3,95),-10)):7.2f} {d(I(n(3.3,95),60)):7.2f} "
          f"{d(I(n(3.2,95),25)):7.2f} {d(I(n(3.4,95),25)):7.2f} {d(I(n(3.3,190),-10)):9.2f}")
