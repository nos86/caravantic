"""Guasti sul filo del sender con il candidato RATIO (Re1=390, Re2=47, Rref=1,6k)."""
import sim_a4 as S

RE1, RE2, RREF = 390, 47, 1600
def base(vcc=3.3):
    return S.net_M(vcc, 95, RE1, RE2, RREF)

def with_src(vsrc, gpio):
    n = base().replace("Rs n2 0 95", f"Vf n2 0 {vsrc}").replace(f"Vg g 0 {S.VOL}", f"Vg g 0 {gpio}")
    return n

print("caso                         I_sender[mA]  V(c)[V]  I_gpio[mA]  I_Df_rev[uA]")
for name, v, g in (("EN on, nominale 95 ohm", None, S.VOL), ("EN on, N a 24 V", 24, S.VOL), ("EN off(GPIO=3,3), N a 24 V", 24, 3.3),
                   ("EN on, N a 0 V (corto)", 0, S.VOL), ("EN off(GPIO=3,3), N a 12 V", 12, 3.3)):
    n = base() if v is None else with_src(v, g)
    r = S.spice.run(n, "dc Vdum 0 0 1", ["i(vm)", "v(c)", "i(vg)"], temp=60)
    print(f"{name:<30} {float(r['i(vm)'][0])*1e3:10.4f} {float(r['v(c)'][0]):8.3f} {abs(float(r['i(vg)'][0]))*1e3:10.3f} {abs(float(r['i(vm)'][0]))*1e6:10.1f}")
# stato GPIO flottante (input con pull-down 45k debole al reset)
n = base().replace(f"Vg g 0 {S.VOL}", "Rg g 0 45k")
r = S.spice.run(n, "dc Vdum 0 0 1", ["i(vm)"], temp=25)
print("reset con pull-down 45 kohm: I_sender =", float(r['i(vm)'][0]) * 1e6, "uA")
