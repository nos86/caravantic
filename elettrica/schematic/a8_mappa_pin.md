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

## 3. Assegnazione proposta

| GPIO | Lato | Funzione | Note |
|---|---|---|---|
| GP0 | sinistro | `SIG_CAB` | RTC GPIO: candidato wake |
| GP1 | sinistro | `SIG_CEL` | RTC GPIO: candidato wake |
| GP2 | sinistro | `SIG_AUX1` | |
| GP3 | sinistro | `SIG_INVERTER_12V` | |
| GP4 | sinistro | riscontro relè globale (**riservato**) | **solo ingresso**, strapping |
| GP5 | sinistro | libero, solo ingresso | strapping |
| GP6 | retro | `SIG_INVERTER_REQ` | |
| GP7 | retro | `SIG_INVERTER_GREEN` | bidirezionale, open-drain |
| GP14 | destro | RS485 DE/RE | pull-down passivo (stato sicuro) |
| GP15 | destro | libero, solo ingresso | strapping |
| GP16 (TX) | destro | RS485 TX | logger su USB-Serial-JTAG |
| GP17 (RX) | destro | RS485 RX | |
| GP18 | destro | `CMD_INVERTER_CTRL` | |
| GP19 | destro | `CMD_INVERTER_STATE` | |
| GP20 | destro | `SIG_INVERTER_RED` | bidirezionale, open-drain |
| GP21 | destro | comando relè globale (**riservato**) | pull-down passivo; il relè globale non toglie l'alimentazione all'MCU |
| GP22 | destro | SDA | pull-up 2,2 kΩ, 100 kHz iniziali |
| GP23 | retro | SCL | |
| GP8, GP9, GP12, GP13 | — | non usati | LED, BOOT, USB |

**Bilancio:** 16 usati su 18 (15 puliti + GP4, compresi 2 riservati al relè globale): **margine 2** (GP5, GP15, solo ingresso; sul pin del riscontro GP4 solo se non serve). Il livello logico dei GP4/GP15 va verificato (livelli di strapping).

## 4. Aperti

- NEW-2: senza funzione, tipo di bobina e corrente del relè globale i due pin riservati sono un'ipotesi.
- Un'uscita per il comando del relè globale richiede un pilota (corrente di bobina); non è un'uscita diretta.
- Livelli di default di GP4/5/15 al boot (datasheet non letto).
- IN-CAB/IN-CEL come wake da deep sleep: legato a OPEN-08 (consumo a riposo), non deciso.
- Conferma dell'ADS1115 U_SH a 0x48: unico dispositivo I²C sulla scheda.
