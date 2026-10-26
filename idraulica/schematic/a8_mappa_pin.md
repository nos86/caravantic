# A8 — Mappa pin, scheda idraulica (ESP32-C6-Zero)

Requisiti: REQ-SW-001, REQ-SW-002, REQ-EL-003, REQ-EL-004, REQ-EL-005, REQ-EL-009 (IN-AUX2), REQ-IF-001, REQ-IF-002, REQ-IF-003, REQ-IF-004, REQ-IF-011. Pin del modulo, regole e fonti: [`../../hardware/schematic/a8_esp32_c6_zero_pinout.md`](../../hardware/schematic/a8_esp32_c6_zero_pinout.md). Stato di tutto: **Proposto / Assumed**.

## 1. Scelta strutturale: nessun expander I²C

Con due schede ogni scheda ha **meno segnali** di quella unica: la ripartizione sotto richiede 16 pin e il C6-Zero ne offre 15 "puliti" più 3 solo-ingresso. Gli MCP23017 (U_EX1/U_EX2) **non servono più**. Conseguenze, tutte a favore:

- scompaiono `EXP_RESET`, `INT_EXT1/2`, il bus-clear e il rischio "bus bloccato = uscite senza controllo";
- lo spegnimento del pistone (7 A / 200 ms, REQ-EL-004) non dipende più da un expander, ma resta firmware e dipende ancora dall'ADS1115 sul bus I²C per la misura di corrente: il blocco del bus resta un guasto accettato (doppio guasto con finecorsa difettoso, utente 2026-10-22);
- più semplice e meno componenti (decisione **Proposta**, da confermare).

## 2. Segnali (16)

| Net | N. | Direzione | Requisito |
|---|---|---|---|
| SDA, SCL (bus I²C unico: LSM6DSOX, MMC5983MA, INA219, ADS1115 #2 per valvola/pistone/grigie) | 2 | bus | IF-001, IF-003, EL-003/004, IF-011 |
| GPS TX, RX | 2 | UART | IF-002 |
| `OW` (DS18B20) | 1 | 1-Wire | IF-004 |
| `OUT_VALVE_OPEN`, `OUT_VALVE_CLOSE` | 2 | uscita | EL-003 |
| `OUT_LINEAR_MOTOR_DIR`, `OUT_LINEAR_MOTOR_ENA` | 2 | uscita | EL-004 (topologia Assumed) |
| `DO1`…`DO4` (relè generici) | 4 | uscita | EL-005 |
| `CLEAN_TANK_CMD` (= `LVL_EN`) | 1 | uscita | IF-003 |
| `WASTE_TANK_CMD` (= `GRY_DRV`) | 1 | uscita | IF-011 |
| `SIG_AUX2` (uscita opto, attivo basso, pull-up a 3V3) | 1 | ingresso | EL-009 |

Nomi dalla netlist EasyEDA del 2026-10-23 (vedi la vecchia a8 §2.5).

## 3. Assegnazione proposta

| GPIO | Lato | Funzione | Note |
|---|---|---|---|
| GP0 | sinistro | `DO1` | |
| GP1 | sinistro | `DO2` | |
| GP2 | sinistro | `DO3` | |
| GP3 | sinistro | `DO4` | |
| GP4, GP5 | sinistro | **liberi, solo ingresso** | strapping |
| GP6 | retro | `OUT_LINEAR_MOTOR_ENA` | pull-down passivo sul gate |
| GP7 | retro | `OUT_LINEAR_MOTOR_DIR` | pull-down passivo |
| GP14 | destro | `OW` | |
| GP15 | destro | `SIG_AUX2` | **strapping: provvisorio.** Da verificare il livello di default sul datasheet; alternativa GP4 o GP5 |
| GP16 (TX) | destro | GPS TX | logger su USB-Serial-JTAG |
| GP17 (RX) | destro | GPS RX | |
| GP18 | destro | `CLEAN_TANK_CMD` | |
| GP19 | destro | `WASTE_TANK_CMD` | |
| GP20 | destro | `OUT_VALVE_OPEN` | interblocco hardware con CLOSE (EL-003) |
| GP21 | destro | `OUT_VALVE_CLOSE` | |
| GP22 | destro | SDA | pull-up 2,2 kΩ (vedi vecchia a8 §2.4), 100 kHz iniziali |
| GP23 | retro | SCL | |
| GP8, GP9, GP12, GP13 | — | non usati | LED, BOOT, USB |

**Bilancio:** 16 usati su 18 (15 puliti + 3 solo-ingresso): 15 puliti tutti occupati, `SIG_AUX2` su un pin di strappo. **Margine: GP4 e GP5 (solo ingresso).** Nessun margine sulle uscite: ogni segnale in più richiede di unire due relè su un pilota, o un expander I²C reintrodotto solo per le uscite.

## 4. Aperti

- Livelli di default di GP4/GP5/GP15 al boot (datasheet Espressif, non letto) e se un pull-up opto su GP15 è compatibile.
- I²C: il bus è unico ma con meno slave (4 dispositivi: LSM6DSOX 0x6A, MMC5983MA 0x30, INA219 0x40, ADS1115 0x49): verificare che gli indirizzi restino liberi dopo aver tolto U_SH (che passa all'elettrica con il suo 0x48).
- Il magnetometro e il suo cavo vanno lontano dai relè `DO1…4` e dal motore: vincoli di layout in a7.
- Il LED di bordo WS2812 su GP8 resta inutilizzato (o indicatore di stato, a scelta).
- Uscite al reset: il C6 porta i GPIO in ingresso a alta impedenza; i pull-down passivi sui gate sono obbligatori (REQ-SW-002).
