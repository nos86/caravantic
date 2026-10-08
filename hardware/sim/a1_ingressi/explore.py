"""Esplorazione di R_S e R_PU (LED in continuo) per le due varianti GB / non GB."""
import itertools
import numpy as np
from sim_a1 import corners, dc_sweep, P

for var in ("GB", "NONGB"):
    C = corners(var)
    for rs, rpu in itertools.product((8.2e3, 10e3), (10e3, 12e3, 15e3, 22e3, 33e3, 47e3)):
        p = dict(P, R_S=rs, R_PU=rpu, topo="noD1")
        _, _, _, _, v_act, _ = dc_sweep(C["ON_worst"], p)
        v, vout, il, iin, _, v_inact = dc_sweep(C["OFF_worst"], p)
        print(f"{var:5s} R_S={rs/1e3:4.1f}k R_PU={rpu/1e3:3.0f}k attivo da {v_act:5.2f} V  inattivo fino a {v_inact:5.2f} V  "
              f"I_in(14.4V,hot)={np.interp(14.4, v, iin)*1e3:.2f} mA  I_in(12.8V)={np.interp(12.8, v, iin)*1e3:.2f}", flush=True)
