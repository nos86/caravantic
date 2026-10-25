"""Helper minimale: scrive un netlist, lancia ngspice in batch, legge l'output wrdata."""
import os
import subprocess
import tempfile

import numpy as np

NGSPICE = r"C:\Program Files (x86)\Spice64\bin\ngspice_con.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models.lib").replace("\\", "/")


def run(netlist_body, analysis, vectors, temp=25):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "out.txt").replace("\\", "/")
        cir = os.path.join(td, "c.cir")
        text = f"""* auto
.include "{MODELS}"
.options temp={temp} tnom=25 reltol=1e-6 abstol=1e-15 vntol=1e-9 itl1=500 itl4=200 method=gear
{netlist_body}
.control
set wr_singlescale
set wr_vecnames
{analysis}
wrdata {out} {' '.join(vectors)}
.endc
.end
"""
        with open(cir, "w") as f:
            f.write(text)
        p = subprocess.run([NGSPICE, "-b", cir], capture_output=True, text=True, timeout=300)
        if not os.path.exists(out):
            raise RuntimeError(p.stdout[-3000:] + p.stderr[-3000:])
        data = np.atleast_2d(np.loadtxt(out, skiprows=1))
        names = open(out).readline().split()
        return {n.lower(): data[:, i] for i, n in enumerate(names)}
