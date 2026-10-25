"""Esegue una netlist ngspice in batch e produce log, .raw e grafico PNG in sim/out/.

Uso:  py sim/run.py sim/<caso>.cir [vettore ...]
      senza vettori traccia tutte le tensioni di nodo.
La netlist non deve contenere un blocco .control: il .raw lo scrive questo script.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from spicelib import RawRead

SIM = Path(__file__).resolve().parent
OUT = SIM / "out"
FALLBACK = Path(r"C:\Program Files (x86)\Spice64\bin\ngspice_con.exe")


def ngspice() -> str:
    exe = shutil.which("ngspice_con")
    if exe:
        return exe
    if FALLBACK.exists():
        return str(FALLBACK)
    sys.exit("ngspice_con non trovato: aggiungere ...\\Spice64\\bin al PATH")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cir = Path(sys.argv[1]).resolve()
    OUT.mkdir(exist_ok=True)
    raw, log, png = (OUT / f"{cir.stem}{ext}" for ext in (".raw", ".log", ".png"))

    # Con -r ngspice non valuta le .meas: si aggiunge un blocco .control
    # che esegue l'analisi e scrive il .raw.
    lines = cir.read_text().splitlines()
    while lines and lines[-1].strip().lower() in ("", ".end"):
        lines.pop()
    run_cir = OUT / f"{cir.stem}.run.cir"
    run_cir.write_text("\n".join(lines + [
        ".control", "run", f"write out/{raw.name}", ".endc", ".end", "",
    ]))
    raw.unlink(missing_ok=True)

    # cwd = sim/ così le .include relative (models/...) funzionano
    res = subprocess.run(
        [ngspice(), "-b", str(run_cir)], cwd=SIM, capture_output=True, text=True,
    )
    log.write_text(res.stdout + res.stderr)
    for s in dict.fromkeys(l.strip() for l in (res.stdout + res.stderr).splitlines()):
        if s.lower().startswith(("error", "warning")) or (
            "=" in s and not s.startswith(("Doing", "Total", "Note", "Circuit"))
            and "DRAM" not in s and "program size" not in s
        ):
            print(s)
    if res.returncode != 0 or not raw.exists():
        sys.exit(f"ngspice terminato con codice {res.returncode}, vedi {log}")

    data = RawRead(str(raw), verbose=False)
    names = sys.argv[2:] or [n for n in data.get_trace_names() if n.lower().startswith("v(")]
    x = data.get_axis()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for n in names:
        ax.plot(x, data.get_trace(n).get_wave(), label=n)
    ax.set_xlabel(data.get_trace_names()[0])
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_title(cir.stem)
    fig.tight_layout()
    fig.savefig(png, dpi=120)
    print(f"-> {png.relative_to(SIM.parent)}")


if __name__ == "__main__":
    main()
