# A8 — Mappa pin, scheda elettrica (ESP32-C6-Zero)

Requisiti: REQ-SW-001, REQ-SW-002, REQ-EL-006, REQ-EL-009 (IN-AUX1), REQ-IF-005, REQ-IF-007, REQ-IF-008, REQ-IF-010, NEW-2 (relè globale). Pin del modulo, regole e fonti: [`../../hardware/schematic/a8_esp32_c6_zero_pinout.md`](../../hardware/schematic/a8_esp32_c6_zero_pinout.md). Stato di tutto: **Proposto / Assumed**.

## 1. Nessun expander I²C

Come per l'idraulica (vedi `idraulica/schematic/a8_mappa_pin.md` §1): 14 segnali più 2 riservati al relè globale (16) stanno su 15 pin puliti più GP4 (solo ingresso). Gli MCP23017 non servono. Le linee bidirezionali `SIG_INVERTER_GREEN/RED` (open-drain per specchiare i LED, ingresso per rilasciare) si fanno **direttamente sul GPIO** (modo open-drain + lettura), senza il problema del glitch di IODIR dell'expander. Da provare al banco.

## 2. Segnali

| Net | N. | Direzione | Requisito |
|---|---|---|---|
| SDA, SCL (bus I²C: ADS1115 U_SH 0x48 per i 2 shunt) | 2 | bus | IF-005 |
| RS485 TX, RX, DE/RE (pull-down passivo) | 3 | UART | IF-008, IF-010 |
| `SIG_CAB` (IN-CAB), `SIG_CEL` (IN-CEL), `SIG_AUX1` | 3 | ingresso (opto, attivo basso) | EL-006, EL-009 |
| `SIG_INVERTER_12V`, `SIG_INVERTER_REQ` | 2 | ingresso (opto) | IF-007 |
| `SIG_INVERTER_GREEN`, `SIG_INVERTER_RED` | 2 | **bidirezionale** (opto + specchio LED) | IF-007 |
| `CMD_INVERTER_CTRL`, `CMD_INVERTER_STATE` | 2 | uscita | IF-007 |
| Relè globale: comando | 1 | uscita | NEW-2 (**riservato**, funzione non definita) |
| Relè globale: stato/riscontro | 1 | ingresso | NEW-2 (**riservato**) |

Nomi dalla netlist EasyEDA del 2026-10-23 (vecchia a8 §2.5).

## 3. Assegnazione proposta (rev. 2026-10-26, dopo la lettura del datasheet)

Regola (vedi [pinout §4](../../hardware/schematic/a8_esp32_c6_zero_pinout.md)): le uscite attive alte e il DE/RE stanno sui **9 pin sicuri** (GP0, 1, 2, 3, 4, 5, 7, 14, 15: nessun pull al reset). Su GP6, GP16…GP23 (weak pull-up ≈ 45 kΩ) restano ingressi, bus, UART e segnali attivi bassi con pull-up (specchio LED: a riposo alto, quindi il pull-up è innocuo).

| GPIO | Lato | Funzione | Note |
|---|---|---|---|
| GP0 | sinistro | `SIG_CAB` (IN-CAB) | sicuro; RTC GPIO, candidato wake |
| GP1 | sinistro | `SIG_CEL` (IN-CEL) | sicuro; RTC GPIO, candidato wake |
| GP2 | sinistro | `SIG_AUX1` | sicuro |
| GP3 | sinistro | `SIG_INVERTER_12V` | sicuro |
| GP4 | sinistro | `CMD_INVERTER_CTRL` | **uscita**, sicuro (MTMS: strapping solo SDIO); pull-down passivo sul gate |
| GP5 | sinistro | `CMD_INVERTER_STATE` | **uscita**, sicuro (MTDI); pull-down passivo |
| GP7 | retro | comando relè globale (**riservato**, NEW-2) | **uscita**, sicuro; pull-down passivo; il relè non toglie l'alimentazione all'MCU |
| GP14 | destro | riscontro relè globale (**riservato**, NEW-2) | ingresso, sicuro |
| GP15 | destro | RS485 DE/RE | **uscita**, sicuro; pull-down passivo (ricezione a riposo); strapping JTAG ignorato con eFuse di fabbrica |
| GP6 | retro | `SIG_INVERTER_GREEN` | bidirezionale, open-drain; weak pull-up innocuo (a riposo alto) |
| GP16 (TX) | destro | RS485 TX | idle alto dopo il reset; la ROM stampa i log di boot qui (DE a riposo basso: il bus non è pilotato) |
| GP17 (RX) | destro | RS485 RX | |
| GP18 | destro | SDA | pull-up esterno 2,2 kΩ, 100 kHz iniziali |
| GP19 | destro | SCL | |
| GP20 | destro | `SIG_INVERTER_RED` | bidirezionale, open-drain |
| GP21 | destro | `SIG_INVERTER_REQ` | ingresso opto |
| GP22, GP23 | destro / retro | **liberi** | weak pull-up |
| GP8, GP9, GP12, GP13 | — | non usati | LED, BOOT, USB |

**Bilancio:** 16 segnali su 18 pin disponibili. **Tutte le 4 uscite** (`CMD_INVERTER_CTRL`, `CMD_INVERTER_STATE`, comando relè globale, DE/RE) sono **su pin sicuri**: nessuna porta il rischio del weak pull-up. Margine: GP22 e GP23 (solo ingressi o bus); nessun pin sicuro di scorta.

## 4. Aperti

- NEW-2: senza funzione, tipo di bobina e corrente del relè globale i due pin riservati sono un'ipotesi; il comando richiede un pilota (corrente di bobina).
- Verifica delle eFuse di fabbrica (`espefuse summary`): GP15 libero solo se EFUSE_JTAG_SEL_ENABLE = 0.
- Eventuale pull-up/pull-down sulla scheda Waveshare sui pin esposti: schema non letto, misurare sul modulo reale.
- Le linee `SIG_INVERTER_GREEN/RED` open-drain su GPIO nativo: da provare al banco (con il weak pull-up interno di GP6 attivo).
- IN-CAB/IN-CEL come wake da deep sleep: legato a OPEN-08, non deciso.
- U_SH (ADS1115, 0x48): unico dispositivo I²C sulla scheda.
