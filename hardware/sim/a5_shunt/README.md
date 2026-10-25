# A5 — Simulazione della rete di ingresso ADS1115 per gli shunt energetici

Requisito: REQ-IF-005 (`docs/frd.md`). Specifica e commento dei risultati: [`../../schematic/a5_shunt_energia.md`](../../schematic/a5_shunt_energia.md).

Esecuzione, da questa cartella: `py -3 sim_a5.py` (ngspice in `C:\Program Files (x86)\Spice64`, numpy e matplotlib). Non usare `-I`: `packaging` sta nel site-packages utente. Produce `out/results.json`, `out/01_dc.png`, `out/02_montecarlo.png`, `out/03_ac.png`. Durata circa 20 s.

**Limiti dei modelli.** `models.lib` contiene un diodo generico tipo 1N4148 usato sia per i due diodi del BAV199 sia per i diodi ESD interni dell'ADS1115. La perdita inversa è iniettata con sorgenti di corrente (0–5 nA, limite garantito a 75 V / 25 °C). L'ADC è modellato solo come carico: 710 kΩ differenziale (tipico, ±20 % nel Monte Carlo), 100 MΩ di modo comune. Offset, guadagno, rumore e temperatura dell'ADS1115 non sono modellati; il rail 3,3 V è ideale.

Variante: `A5_VARIANT=10k py -3 sim_a5.py` (PowerShell: `$env:A5_VARIANT='10k'`) scrive in `out_10k/`. Il valore del Monte Carlo dipende dal rapporto R_S/R_B, non dai valori assoluti.

Varianti: `base` (3,3k/47k, cartella `out/`), `10k` (10k/143k, `out_10k/`), `10k150` (10k/150k, **adottata**, `out_10k150/`).
