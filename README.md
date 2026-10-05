# Caravantic Board — rev. 2

Scheda singola di bordo per il camper (Fiat Ducato X244, 2005, 2.3 JTD — Marlin 65G), integrata in Home Assistant.

> Il progetto rev. 1 (IO-board multi-nodo CANopen) è archiviato in [`old/`](old/). Le parti riutilizzabili sono mappate in [`docs/frd.md`](docs/frd.md) §5.

## Funzioni richieste

1. Assetto camper — accelerometro + magnetometro
2. Posizione GPS
3. Livello serbatoio acqua chiara
4. Valvola motorizzata scarico acque chiare, con misura di corrente
5. 2 ingressi misura corrente da shunt 200 A / 75 mV
6. 2 ingressi 12 V aux — stato cellula e cabina
7. ~~Interfaccia motore Ducato~~ — delegata a slave futuro sul bus RS485
8. Interfaccia con il comando remoto dell'inverter Renogy 2000 W (in serie fra inverter e comando)
9. Sensore di temperatura sul serbatoio
10. Pistone elettrico per scarico acque grigie
11. Relè accensione telecamera scarico grigie
12. Interfaccia verso comando remoto in cabina per scarico serbatoi
13. Modbus RS485 verso meter SDM120 — bus estendibile a slave futuri

## Struttura

| Cartella | Contenuto |
|---|---|
| `docs/` | Specifica funzionale (`frd.md`) e documenti di progetto |
| `hardware/` | Schematico e PCB rev. 2 |
| `firmware/` | Firmware rev. 2 |
| `old/` | Progetto rev. 1 archiviato — solo consultazione |

## Stato

Specifica in bozza: 13 funzioni confermate, punti aperti in `docs/frd.md` §3. Nessuna scelta di componente congelata.
