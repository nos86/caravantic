# Schematico A1 — Ingressi digitali IN-CAB / IN-CEL (specifica di disegno)

Requisiti: REQ-EL-006, REQ-EL-008. Dimensionamento e verifica: [`../sim/a1_ingressi/README.md`](../sim/a1_ingressi/README.md). Registro componenti: [`../../docs/components.md`](../../docs/components.md).

Rev. 2026-10-08 (3): opto **Toshiba TLP293 rango GB**, LED in conduzione continua (assorbimento di circa 1 mA a cellula attiva accettato dall'utente), **senza D1 in serie**: la protezione inversa è fatta dal diodo antiparallelo al LED e dallo Zener in diretta. **5 componenti per canale.** Allineata al foglio EasyEDA "Optoisolated inputs" (designatori del canale IN-CAB).

Foglio EasyEDA: **Optoisolated inputs**. Il canale IN-CAB usa R1, D1, D2, U1, R2; i designatori del canale IN-CEL sono da assegnare nel foglio.

## Net verso il resto della board (net label / porte)

| Net | Direzione | Note |
|---|---|---|
| `IN_CAB` | dal connettore di campo | +15 sotto chiave, derivato dalla radio (vedi sotto) |
| `IN_CEL` | dal connettore di campo | uscita della centralina cellula |
| `SIG_CAB` | foglio → MCU | attivo basso, GPIO di solo ingresso (nella specifica precedente: `IN_CAB_N`; **nome da decidere**) |
| `SIG_CEL` | foglio → MCU | idem per IN-CEL |
| `+3V3`, `GND` | alimentazione | GND = massa della board = massa veicolo |

Il connettore di campo non fa parte di questo foglio: è un punto aperto da decidere nella sezione connettori.

## Schema (per canale)

```
IN ─R1 8,2k─┤◄D2├──┬──── U1.1 (anodo LED)
 (0805)  BZT52C3V3 │      U1.2 (catodo LED) ── GND
                 D1 ▲ 1N4148WS (catodo sul nodo, anodo a GND)
                   │
                  GND
U1 lato uscita: pin 4 (collettore) ── R2 12k ── +3V3 ; pin 4 → SIG_xxx ; pin 3 (emettitore) → GND
```

## Distinta (per canale IN-CAB)

| Designatore | Valore / P/N | Package | Stato componente |
|---|---|---|---|
| R1 | 8,2 kΩ 1 % | 0805 | Proposto. **Rischio accettato**: la tenuta al load dump non è dimostrabile (vedi REQ-EL-008) |
| D2 | BZT52C3V3 (Diodes, C151564), **catodo verso l'ingresso** | SOD-123 | Proposto |
| D1 | 1N4148WS, **catodo sul nodo, anodo a GND** | SOD-323 | Proposto |
| U1 | **TLP293(GB-TPL,E)** (Toshiba, LCSC C77656) | SO4 (11-3C1) | Proposto (scelta utente, 2026-10-08). ⚠️ Il foglio mostra `TLP293(TPL,E)` (non ranked): da correggere |
| R2 | 12 kΩ 1 % | 0805 | — |

Rimossi rispetto alle versioni precedenti: D1 BAV21W in serie (250 V), Q1 MMBTA42, R_E, R_B, R_BE, C_S, R_IN e il net `STROBE_IN`.

## Netlist del canale 1 (il canale 2 è identico)

| Net | Pin collegati |
|---|---|
| `IN_CAB` | R1.1 |
| `N1` | R1.2 — D2.K |
| `N2` | D2.A — D1.K — U1.1 (anodo LED) |
| `GND` | D1.A — U1.2 (catodo LED) — U1.3 (emettitore) |
| `SIG_CAB` | U1.4 (collettore) — R2.1 |
| `+3V3` | R2.2 |

Piedinature da controllare sul simbolo EasyEDA scelto:
- **TLP293 (SO4):** 1 anodo, 2 catodo, 3 emettitore, 4 collettore (datasheet Toshiba Rev. 7.0, §4).
- **Diodi:** controllare la marcatura A/K del simbolo LCSC. D2 deve avere il simbolo dello Zener, D1 quello di un diodo normale.

## Alimentazione di IN_CAB dal veicolo
Il +15 sotto chiave è derivato dalla **radio** con un cavo da 0,5 mm² (Confirmed, utente 2026-10-08). Il cavo si trova sulla rete del veicolo, lato alternatore: i transitori ISO 7637-2 dell'X244 arrivano qui, non sul cavo da 35 mm² della batteria servizi. Raccomandazioni (*dovrebbe*, non ancora decise):
- fusibile in linea, a pochi centimetri dalla derivazione, dimensionato per il cavo da 0,5 mm² (il fusibile della radio a monte è per un cavo e un carico diversi);
- la massa del segnale è la massa della board: un offset fra la massa carrozzeria vicino alla radio e la massa della board sposta le soglie. Il margine su "inattivo" è di 0,10 V (vedi simulazione).

## Firmware
Nessuno strobe: i due GPIO sono ingressi semplici (senza pull interni). Lettura periodica con filtro anti-rimbalzo di almeno 3 campioni concordi; tempo di risposta totale ≤ 100 ms (il circuito risponde in meno di 0,2 ms).

## Note di layout (da riprendere nella fase PCB)
- Il nodo `N1`/`N2` arriva a 101 V nel load dump (R1 ne assorbe la maggior parte) e a circa 160 V nei burst: servono distanze ≥ 0,5 mm verso `+3V3`/GPIO e nessuna traccia lato MCU sotto il corpo dell'opto.
- La distanza di isolamento fra i lati del TLP293 è quella del package (creepage 5,0 mm min. dichiarata da Toshiba). Il ritorno è comunque `GND` comune.
- R1 vicino al connettore di campo.
