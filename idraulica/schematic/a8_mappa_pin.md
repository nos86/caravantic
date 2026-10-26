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

## 3. Assegnazione proposta (rev. 2026-10-26, dopo la lettura del datasheet)

Regola (vedi [pinout §4](../../hardware/schematic/a8_esp32_c6_zero_pinout.md)): le uscite che devono restare spente al reset stanno sui **9 pin sicuri** (GP0, 1, 2, 3, 4, 5, 7, 14, 15: nessun pull al reset). GP6, GP16…GP23 hanno un weak pull-up (≈ 45 kΩ tipico), GP18…GP23 già durante il reset.

| GPIO | Lato | Funzione | Note |
|---|---|---|---|
| GP0 | sinistro | `DO1` | sicuro |
| GP1 | sinistro | `DO2` | sicuro |
| GP2 | sinistro | `DO3` | sicuro |
| GP3 | sinistro | `DO4` | sicuro |
| GP4 | sinistro | `OUT_VALVE_OPEN` | sicuro (MTMS: strapping solo SDIO, nessun effetto); interblocco hardware con CLOSE (EL-003) |
| GP5 | sinistro | `OUT_VALVE_CLOSE` | sicuro (MTDI, idem) |
| GP7 | retro | `OUT_LINEAR_MOTOR_DIR` | sicuro; pull-down passivo sul gate |
| GP14 | destro | `OUT_LINEAR_MOTOR_ENA` | sicuro; pull-down passivo sul gate |
| GP15 | destro | **libero, pin sicuro di scorta** | strapping JTAG ignorato con eFuse di fabbrica |
| GP6 | retro | libero (weak pull-up) | MTCK |
| GP16 (TX) | destro | GPS TX | uscita alta dopo il reset (idle UART); la ROM stampa i log di boot qui |
| GP17 (RX) | destro | GPS RX | |
| GP18 | destro | SDA | pull-up 2,2 kΩ esterno (vedi vecchia a8 §2.4), 100 kHz iniziali |
| GP19 | destro | SCL | |
| GP20 | destro | `OW` (1-Wire) | pull-up esterno |
| GP21 | destro | `CLEAN_TANK_CMD` (= `LVL_EN`) | **su pin con weak pull-up**: durante il boot l'eccitazione del livello può essere accesa; accettabile (misura, 4–10 mA, poche centinaia di ms) oppure pull-down ≤ 4,7 kΩ; da verificare sul foglio a4 la polarità del pilota |
| GP22 | destro | `WASTE_TANK_CMD` (= `GRY_DRV`) | idem, foglio a3 (eccitazione continua della sonda per qualche centinaio di ms al boot: corrosione trascurabile, da confermare) |
| GP23 | retro | `SIG_AUX2` | ingresso opto con pull-up a 3V3: il weak pull-up è innocuo |
| GP8, GP9, GP12, GP13 | — | non usati | LED, BOOT, USB |

**Bilancio:** 16 segnali su 18 pin disponibili. **10 uscite**: 9 sui pin sicuri più 2 (`CLEAN_TANK_CMD`, `WASTE_TANK_CMD`) sui pin con weak pull-up, scelte perché un'accensione al boot è innocua; **valvola, pistone e i 4 relè sono tutti su pin sicuri**. Margine: **GP15** (sicuro) e **GP6**.

## 4. Aperti

- Polarità e rete di pull-down dei piloti `CLEAN_TANK_CMD` e `WASTE_TANK_CMD` (fogli a4 e a3): accettare l'accensione al boot o aggiungere pull-down ≤ 4,7 kΩ.
- Eventuale pull-up/pull-down sulla scheda Waveshare sui pin esposti: schema non letto, misurare sul modulo reale.
- Verifica delle eFuse di fabbrica (`espefuse summary`): GP15 libero solo se EFUSE_JTAG_SEL_ENABLE = 0.
- I²C: bus unico con 4 dispositivi (LSM6DSOX 0x6A, MMC5983MA 0x30, INA219 0x40, ADS1115 0x49), indirizzi liberi dopo lo spostamento di U_SH (0x48) sull'elettrica.
- Il magnetometro e il suo cavo vanno lontano dai relè `DO1…4` e dal motore: vincoli di layout in a7.
- Il LED WS2812 su GP8 resta inutilizzato.
- Uscite al reset: i pull-down passivi sui gate sono comunque obbligatori (REQ-SW-002).
