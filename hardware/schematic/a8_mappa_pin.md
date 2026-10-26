# A8 — Mappa pin: GPIO nativi ed expander I²C

> **SUPERATA il 2026-10-26** (REQ-SW-001: due schede con ESP32-C6-Zero, IF-012 Ethernet rimosso). Sostituita da [`a8_esp32_c6_zero_pinout.md`](a8_esp32_c6_zero_pinout.md) (modulo) e dalle mappe di scheda `idraulica/schematic/a8_mappa_pin.md` ed `elettrica/schematic/a8_mappa_pin.md` (senza expander). Conservata come riferimento: i nomi di rete e l'analisi del bus I²C (§2.4) restano utili.

Requisiti: REQ-IF-012 (Ethernet, strategia pin), REQ-SW-001, REQ-SW-002, OPEN-16. Stato di tutto ciò che segue: **Proposto / Assumed**. Nessun componente scelto (famiglia di expander da decidere).

## 1. Pin disponibili sul Waveshare ESP32-S3-Tiny

Fonte: schematico Waveshare `ESP32-S3-Tiny-Sch.pdf` (immagine della pagina 1 letta direttamente; fonte del costruttore). Il pinout fotografico della wiki non è leggibile come testo.

| Gruppo | GPIO | Note |
|---|---|---|
| Header P1 (23 poli) | IO1…IO18 (IO3 strapping), TX = IO43, RX = IO44 | 20 GPIO |
| Pad "Testpoint" P2…P15 | IO21, IO33…IO42, IO45, IO47, IO48 | 14 GPIO; **forma fisica e accessibilità dei pad da verificare** sul modulo |
| Scheda adattatrice FPC (non sull'header) | IO0 (BOOT), RESET, USB D−/D+ (IO19/IO20) | non disponibili |
| Interni al SoC | IO26…IO32 (flash/PSRAM in package) | non esposti |

Totale esposto: 34, coerente col dato "34 GPIO" della wiki Waveshare.

**Esclusi dall'assegnazione:**
- **IO3** (strapping) e **IO45** (strapping): vedi regola di progetto, nessuna uscita/LED su pin di strappo (IO0 e IO46 non sono esposti).
- **IO38**: nello schematico Waveshare il pin DI del LED WS2812B (LED1, con pull-up R1 10 kΩ) è su **IO38**, non su IO14. I documenti rev. 1 (`old/.../02-mcu.md`) e i fogli a4 e a7 dicono "non GPIO14" prendendo il dato dall'esempio Arduino della wiki, che a sua volta avverte che i pin vanno adattati: **IO14 è libero, IO38 no**. Da riconfermare sul modulo reale.

Disponibili: **17 sull'header** (IO1, 2, 4…18) + TX/RX + **12 sui pad** (IO21, 33…37, 39…42, 47, 48).

**Da verificare sul datasheet Espressif ESP32-S3 (non letto):** che IO33…IO37 siano liberi con la PSRAM quad in package della variante FH4R2 (la wiki li dice usati dalla PSRAM solo per la variante N8R8, quindi sul Tiny dovrebbero essere liberi); funzione di IO39…IO42 (JTAG, GPIO se non usato); IO47/IO48.

## 2. Segnali e destinazione

### 2.1 Restano su GPIO nativo (17, con le 2 linee INT degli expander; 16 con W5500 RST condiviso con RESET expander)

Rev. 2026-10-23 (richiesta utente): i tre ingressi analogici `IN_VALVE_SENSE`, `IN_PISTON_SENSE`, `GRY_SNS` passano a un **secondo ADS1115 (U_AD2, I²C 0x49, single-ended A0…A2)**, quindi escono dai GPIO nativi (−3 pin, vedi §2.3). Un expander digitale non porta segnali analogici: serve un ADC I²C.

| Segnale | N. | Motivo | Fonte |
|---|---|---|---|
| SDA/SCL bus I²C **unico** (IMU, magnetometro, INA219, 2× ADS1115, 2 expander) | 2 | periferica I²C; bus unico per decisione utente 2026-10-23, vedi §2.4 | a4, a5, a7, IF-012 |
| `INT_EXT1`, `INT_EXT2` (INT degli expander, wake-up da deep sleep) | 2 | ingressi RTC; vedi §2.6 | utente 2026-10-23 |
| `EXP_RESET` (+ RST W5500) | 1 | RESET degli expander, pull-down passivo, rilascio da firmware | IF-012 |
| W5500: SCLK, MOSI, MISO, CS, INT | 5 | SPI + interrupt | IF-012 |
| 1-Wire `OW` (DS18B20) | 1 | timing a microsecondi | a4 |
| UART GPS (TX, RX) | 2 | UART | IF-002 |
| UART RS485 (TX, RX, DE/RE) | 3 | UART, DE/RE con timing Modbus | IF-008 |

### 2.2 Vanno sull'expander (21)

**Ingressi (8)**

| Net | Foglio |
|---|---|
| `SIG_CAB`, `SIG_CEL`, `SIG_AUX1`, `SIG_AUX2` (uscite opto, attivo basso, pull-up a 3V3) | a1 |
| `SIG_INVERTER_12V`, `SIG_INVERTER_REQ` | a6 |
| `SIG_INVERTER_GREEN`, `SIG_INVERTER_RED` (**bidirezionali**: il firmware li tira bassi in open-drain per lo specchio dei LED; sull'expander = pin in ingresso per rilascio, in uscita a 0 per forzare) | a6 |

**Uscite (13)**

| Net | N. | Foglio |
|---|---|---|
| `OUT_VALVE_OPEN`, `OUT_VALVE_CLOSE` | 2 | a2 |
| Pistone: bobine K1, K2 + ENA (topologia **Assumed**, `idraulica/components.md`) | 3 | EL-004 |
| 4 relè generici | 4 | EL-005 (OPEN-13) |
| `CMD_INVERTER_CTRL`, `CMD_INVERTER_STATE` | 2 | a6 |
| `LVL_EN` | 1 | a4 |
| `GRY_DRV` | 1 | a3 |

### 2.3 Ingressi analogici su ADC I²C (Assumed)

| Net | Canale U_AD2 | Foglio | Note |
|---|---|---|---|
| `IN_LINEAR_MOTOR_SENSE` (= `IN_PISTON_SENSE`) | AIN0 | EL-004 | soglia 7 A = 1,75 V, fondo scala 2,45 V; R33 + C12 + D14 |
| `IN_VALVE_SENSE` | AIN1 | a2 | 0,9 V/A, 2,25 V a 2,5 A; R45 + C15 + D18 (3,3 V) |
| — | AIN2 | — | a GND (non usato) |
| `WASTE_TANK_SENSE` (= `GRY_SNS`) | AIN3 | a3 | misura impulsata (10 ms dopo `WASTE_TANK_CMD`); R12/R13/R15, D10, C2 |

Assegnazione **letta dalla netlist EasyEDA del 2026-10-23** (non dai documenti). U26: ADDR a 3V3 = 0x49, ALERT/RDY non collegato.

- U_SH (ADS1115 #1, shunt energetici) usa tutti e 4 gli ingressi in A0_A1 / A2_A3 differenziale: serve un **secondo dispositivo**, non un canale in più. Indirizzi: U_SH 0x48 (ADDR a GND), U_AD2 0x49 (ADDR a VDD); da controllare l'assenza di conflitti con IMU, magnetometro e INA219 sullo stesso bus.
- **Bus: unico (Confirmed, utente 2026-10-23).** U_AD2 sta sullo stesso bus di IMU, magnetometro, INA219, U_SH **e degli expander** (l'utente ha accettato il rischio del bus singolo; il punto (c) di IF-012 è superato). Rischio accettato dall'utente: un blocco del bus lascia valvola e pistone pilotati dagli expander ma senza misura di corrente, quindi senza la soglia 7 A / 200 ms (EL-004); è un guasto singolo, protetto solo da finecorsa/arresti meccanici. Mitigazione firmware da definire (non fatta): se la lettura di corrente manca o è scaduta, il firmware porta a riposo le uscite pistone/valvola e non le riattiva.
- Impatti da verificare, non fatti qui: (1) latenza: 860 SPS ≈ 1,2 ms per conversione, più il polling ESPHome, contro 200 ms del pistone; (2) `GRY_SNS`: la lettura va sincronizzata col finestra di 10 ms di `GRY_DRV` (firmware, `GRY_DRV` è su expander); (3) impedenza di sorgente del partitore a3 contro Z d'ingresso dell'ADS1115 al FSR scelto (datasheet SBAS444E, FSR ±4,096 V o ±2,048 V: 2,45 V richiede ±4,096 V); (4) il datasheet ADS1115 è stato verificato mono-fonte (`idraulica/components.md`, U_SH).

### 2.4 Verifica del bus unico (2026-10-23)

Dispositivi: 2 expander (famiglia da scegliere), LSM6DSOX 0x6A, MMC5983MA 0x30, INA219 0x40, ADS1115 0x48 e 0x49. Tutti a 3,3 V (INA219 con VS a 3V3, a4).

| Aspetto | Esito | Base |
|---|---|---|
| Indirizzi | Nessun conflitto. Gli expander non sono scelti: le famiglie comuni stanno a 0x20…0x27 (**da memoria**, da confermare sulla parte); l'indirizzo scelto deve evitare 0x30, 0x40, 0x48, 0x49, 0x6A | a7, U_SH; 0x49 con ADDR a VDD confermato su TI SBAS444E §7.5.1.1 |
| Livelli logici | OK a 3,3 V per tutti: VIH = 0,7·VDD (2,31 V), VIL = 0,3·VDD, VOL ≤ 0,4 V a 3 mA per ADS1115 e INA219 | TI SBAS444E §5.5, SBOS448G §7.5 (letti). LSM6DSOX: solo 0,7·VDD_IO da mirror (debole); MMC5983MA: **non verificato** |
| Velocità | 400 kHz ammessa da ADS1115, INA219 (letti), LSM6DSOX e MMC5983MA (solo snippet, debole) | |
| **Pull-up** | **I 4,7 kΩ di a7 non vanno bene a 400 kHz con 8 slave.** tr = 0,8473·R·C ≤ 300 ns → con 4,7 kΩ C ≤ 75 pF; il bus con 8 chip, 2 pin ESP e tracce è stimato 100–150 pF (**mia stima**, Ci ADS1115/LSM6DSOX/MMC5983MA non trovate; INA219 3 pF). Con 2,2 kΩ: C ≤ 160 pF, corrente di pozzo 1,5 mA (< 3 mA, ok). Limite inferiore ≈ 1 kΩ per i 3 mA | formula e 300 ns / 400 pF / 3 mA da fonti secondarie (UM10204 non letta) |
| Carico | Cb ≤ 400 pF (Fast-mode) con ampio margine | idem |
| Tempi di transazione | 1 lettura IMU/ADS/expander ≈ 0,3–0,5 ms a 400 kHz (≈ 1,3 ms a 100 kHz): trascurabili contro 200 ms (pistone) e 100 ms (ingressi, EL-006) | calcolo mio, non misurato |
| Blocco del bus | Vedi sotto | |

**Cosa serve per essere robusti (proposta, Assumed):**
1. Pull-up **2,2 kΩ** (non 4,7 kΩ) e, finché la capacità non è misurata, firmware a **100 kHz**; salire a 400 kHz solo dopo misura del fronte di salita sulla scheda (≤ 300 ns).
2. Il bus non ha un reset hardware per i sensori: ADS1115 e MMC5983 non hanno pin RESET; l'INA219 azzera l'interfaccia dopo 28 ms con linee basse (SBOS448G §7.5); per l'LSM6DSOX c'è la segnalazione di un forum ST di sensore che ignora il SW_RESET dopo traffico anomalo (debole). L'ADS1115 risponde al general call reset (0x00 0x06) ma solo a bus funzionante.
3. **Rilevamento e arresto indipendenti dal bus:** il firmware conta le transazioni fallite o scadute; superata la soglia, **impulsa `EXP_RESET`** (GPIO nativo, non dipende dal bus) per portare a riposo valvola, pistone e relè, poi esegue il recupero del bus (9 impulsi su SCL, STOP) e riprende. Così un blocco in marcia del pistone **ferma** il pistone, non lo lascia senza protezione. Expander: **MCP23017-E/SO ×2 (Congelato, utente 2026-10-23)**, `idraulica/components.md` U_EX1/U_EX2. Il datasheet garantisce le uscite in alta impedenza entro 1 µs dal RESET basso, ma non dice se il RESET riporta a default i registri né se ripristina la macchina a stati I²C: dopo ogni reset il firmware riscrive tutti i registri e il bus si recupera col bus-clear, non col pin RESET. Effetto collaterale già accettato: il reset resetta anche il W5500.
4. Non spegnere i sensori per ripristinarli (nessun power-cycle): un chip senza alimentazione potrebbe caricare SDA/SCL; per l'ADS1115 con VDD = 0 V il datasheet non dice nulla (non verificabile).
5. Layout: tracce SDA/SCL corte e lontane dai relè e dalle bobine; magnetometro con i vincoli di a7.

**Con l'MCP23017:** soglie SDA/SCL 0,2/0,8·VDD (VIL max 0,66 V, VIH min 2,64 V a 3,3 V), più strette dello standard; con 2,2 kΩ la corrente di pozzo è circa 1,3 mA e VOL (≤ 0,6 V a 3 mA) resta sotto 0,66 V, ma il margine è piccolo: un motivo in più per partire a 100 kHz e misurare livello basso e fronte di salita sulla scheda.

**Non verificato / aperto:** capacità d'ingresso di ADS1115, LSM6DSOX, MMC5983MA; VIH/VOL di MMC5983MA; datasheet di LSM6DSOX e MMC5983MA e UM10204 non letti dal verificatore (PDF illeggibili); implementazione del bus-clear in ESPHome da verificare; famiglia degli expander.

### 2.5 Assegnazione effettiva degli expander (netlist EasyEDA del 2026-10-23)

Nomi di rete dello schematico, con fra parentesi i nomi usati in questo documento quando differiscono. Pull-up bus: R76/R77 2,2 kΩ a +3V3. RESET: R78 modificato dall'utente a **pull-down 1 kΩ** (non riletto nella netlist: l'ultima esportazione non è stata salvata).

**U24 MCP23017 — 0x21** (A0 = 3V3, A1 = A2 = GND)

| Pin | Rete | Tipo | Pin | Rete | Tipo |
|---|---|---|---|---|---|
| GPA0 | `SIG_IN3` (= `SIG_AUX1`) | ingresso opto | GPB0 | `OUT_LINEAR_MOTOR_DIR` | uscita |
| GPA1 | `SIG_CEL` | ingresso opto | GPB1 | `OUT_LINEAR_MOTOR_ENA` | uscita |
| GPA2 | `SIG_T15` | ingresso opto | GPB2 | `OUT_VALVE_OPEN` | uscita |
| GPA3 | `SIG_IN4` (= `SIG_AUX2`) | ingresso opto | GPB3 | `OUT_VALVE_CLOSE` | uscita |
| GPA4 | `DO1` | uscita relè | GPB4 | `CLEAN_TANK_CMD` (= `LVL_EN`) | uscita |
| GPA5 | `DO2` | uscita relè | GPB5 | `WASTE_TANK_CMD` (= `GRY_DRV`) | uscita |
| GPA6 | `DO3` | uscita relè | GPB6 | libero | |
| GPA7 | `DO4` | uscita relè | GPB7 | libero | |

INTA = `INT_EXT1`, INTB non collegato.

**U25 MCP23017 — 0x20** (A0 = A1 = A2 = GND)

| Pin | Rete | Tipo |
|---|---|---|
| GPB0 | `CMD_INVERTER_CTRL` | uscita |
| GPB1 | `CMD_INVERTER_STATE` | uscita |
| GPB2 | `SIG_INVERTER_RED` | **bidirezionale** (ingresso opto + specchio LED con Q12; un solo pin, IODIR commutato) |
| GPB3 | `SIG_INVERTER_GREEN` | **bidirezionale** (opto + Q11) |
| GPB4 | `SIG_INVERTER_12V` | ingresso opto |
| GPB5 | `SIG_INVERTER_REQ` | ingresso opto |
| GPB6, GPB7 | liberi | |
| GPA0…GPA7 | liberi (8) | |

INTB = `INT_EXT2`, INTA non collegato.

**Conti:** 20 pin usati su 32 (6 ingressi opto, 12 uscite, 2 bidirezionali) e 12 liberi (U24: 2, U25: 10). Differenza rispetto a §2.2: il pistone usa 2 linee (`DIR`, `ENA`) invece di 3 (K1, K2, ENA). I pin liberi non vanno lasciati flottanti: o uscita a 0 da firmware, o pull-up interno (GPPU).

### 2.6 Wake-up del micro da deep sleep via INT (**Open**, utente 2026-10-23)

Tema lasciato aperto per decisione dell'utente: nulla di questa sezione è deciso, è solo un'istruttoria di partenza. Le reti `INT_EXT1`/`INT_EXT2` sono già sullo schematico (INTA di U24, INTB di U25); i GPIO ESP32 e la configurazione sotto sono **proposte non confermate**.

**Collegamenti proposti**

| Rete | Pin expander | GPIO ESP32-S3 | Note |
|---|---|---|---|
| `INT_EXT1` | U24.INTA (pin 20) | **IO12** | porta A di U24 = tutti gli ingressi opto di U24 |
| `INT_EXT2` | U25.INTB (pin 19) | **IO13** | porta B di U25 = ingressi e linee inverter |

Scelta dei pin: IO12 e IO13 sono liberi dopo l'unione dei bus e sono sull'header. Le funzioni RTC dell'S3 sono sui GPIO 0…21 (**da memoria**, da confermare sul datasheet Espressif, non letto): entrambi ricadono nell'intervallo, come IO14.

**Configurazione degli expander (da firmware; valori da memoria del datasheet MCP23017, da riverificare su DS20001952)**
- `IOCON.MIRROR = 1` su entrambi: INTA e INTB si comportano come una sola uscita, così il pin collegato segnala l'interrupt di qualsiasi porta (l'altro pin di ciascun chip è scollegato).
- Polarità **attiva alta** (`INTPOL = 1`) e push-pull (`ODR = 0`): permette EXT1 in modo "any high" (supportato su tutte le varianti ESP32); l'"any low" sull'S3 è da verificare. Nessun pull-up/pull-down sulle linee INT.
- `GPINTEN` solo sui pin che devono svegliare; `INTCON = 0` (interrupt sul cambio rispetto al valore precedente). L'interrupt resta attivo finché il firmware non legge `GPIO`/`INTCAP`: **leggere sempre dopo il risveglio**, altrimenti un nuovo sleep si risveglia subito.
- Quali ingressi devono svegliare (`SIG_T15`, `SIG_CEL`, `SIG_IN3/4`, linee inverter) è **da decidere** (legato a OPEN-08: scheda sempre alimentata o con wake da 12 V cabina).

**Vincoli di progetto per il deep sleep**
1. **Il RESET degli expander deve restare rilasciato (alto) in deep sleep.** Con il pull-down passivo, se `IO14` diventa flottante in sleep gli expander vengono resettati: niente interrupt e quindi niente risveglio. Serve il mantenimento del pin in deep sleep (gpio hold; supporto in ESPHome **da verificare**). Le uscite degli expander mantengono l'ultimo valore, quindi **prima di dormire il firmware spegne valvola, pistone, relè, `CLEAN_TANK_CMD` e `WASTE_TANK_CMD`**.
2. **Consumo del pull-down:** con IO14 alto e un pull-down da **1 kΩ** si dissipano 3,3 V / 1 kΩ = **3,3 mA** per tutto lo sleep, che annulla lo scopo del deep sleep. Il pull-down serve solo a tenere il reset con il pin flottante: 10 kΩ (0,33 mA) o più dovrebbe bastare se VIL del RESET (0,66 V max a 3,3 V, DS20001952C) è rispettato con le perdite dei pin; da dimensionare sul budget di OPEN-08 (la linea è condivisa con il RST del W5500, che ha le sue soglie).
3. Il W5500 condivide `EXP_RESET`: il suo stato in sleep dipende da quella linea; il consumo Ethernet in sleep non è trattato qui.
4. Al risveglio da deep sleep l'ESP riparte da reset e, senza hold, `EXP_RESET` torna flottante (pull-down) per qualche ms e **resetta gli expander**: l'evento che ha svegliato va ricostruito leggendo lo stato degli ingressi all'avvio, oppure il pin va tenuto con hold anche durante il boot.
5. ESPHome: componente `deep_sleep` con wake su pin; `esp32_ext1_wakeup` con più pin e `interrupt_pin` del componente `mcp23017` sono **da verificare** sulla documentazione.

**Non verificato:** funzioni RTC e modalità EXT1 dell'S3 sul datasheet Espressif; bit e comportamento di IOCON/INTCON/INTCAP sul DS20001952; stato dei pin INT durante il RESET basso; consumo reale in sleep.

## 3. Assegnazione proposta

| GPIO | Posizione | Funzione | Note |
|---|---|---|---|
| IO1, IO2, IO4 | header | **liberi (3)** | ex ingressi analogici, ora su U_AD2 (§2.3); IO3 resta strapping |
| IO5 | header | W5500 SCLK | |
| IO6 | header | W5500 MOSI | |
| IO7 | header | W5500 MISO | |
| IO8 | header | W5500 CS | |
| IO9 | header | W5500 INT | |
| IO10 | header | SDA bus I²C unico | |
| IO11 | header | SCL bus I²C unico | |
| IO12 | header | `INT_EXT1` (U24.INTA) | riservato per wake-up da deep sleep (§2.6, **Open**) |
| IO13 | header | `INT_EXT2` (U25.INTB) | riservato per wake-up da deep sleep (§2.6, **Open**) |
| IO14 | header | `EXP_RESET` (+ RST W5500) | pull-down passivo **1 kΩ** (R78, utente 2026-10-23); libero (il LED è su IO38); valore da rivedere se si usa il deep sleep (§2.6, Open) |
| IO15 | header | `OW` | |
| IO16 | header | RS485 TX | |
| IO17 | header | RS485 RX | |
| IO18 | header | RS485 DE/RE | pull-down passivo (stato sicuro) |
| IO43 (TX) | header | GPS TX | log su USB-Serial-JTAG (supporto ESPHome da verificare) |
| IO44 (RX) | header | GPS RX | |
| IO21, 33…37, 39…42, 47, 48 | pad | **liberi (12)** | riserva; usare solo se i pad sono saldabili |
| IO3, IO45 | header/pad | non usati | strapping |
| IO38 | pad | non usato | LED di bordo |

**Bilancio:** servono 16 pin (con RESET condiviso col W5500, INT incluse) e l'header ne offre 19 (17 + TX/RX): **margine 3 sull'header** (era zero prima di U_AD2 e dell'unione dei bus), 12 di scorta sui pad. Se i pad non sono accessibili, ogni segnale in più richiede una di queste mosse: unire i due bus I²C (−2 pin; contro: rischio 5 della discussione), DE/RE automatico sul transceiver RS485 (−1), ponte I²C→1-Wire tipo DS2482 (−1, nuovo componente).

## 4. Vincoli da rispettare nello schema

1. Nessun ingresso analogico sui GPIO nativi (rev. 2026-10-23): tutti su ADS1115. Se in futuro serve un ingresso analogico nativo, gli ADC1 sono solo IO1…IO10.
2. Nessuna uscita su pin di strappo; le uscite verso gate/relè stanno sull'expander, quindi il loro stato al reset dipende dal RESET degli expander (IF-012) e dai pull-down di gate.
3. `EXP_RESET` e `IO18` (DE/RE) con pull-down passivo; il valore va scelto contro V_IL del pin RESET dell'expander.
4. Il RESET del W5500 è sulla stessa linea di `EXP_RESET`: un reset degli expander resetta anche l'Ethernet (accettato come ipotesi, da confermare).
5. Verificare che il rischio già annotato in `a6` (pull-up interno di default su alcuni pin dell'S3) sia superato dalla scelta: le bobine non sono più su GPIO nativi, ma gli expander devono avere uscite in alta impedenza al reset.

## 5. Punti aperti

- Accessibilità fisica dei pad P2…P15 (ne dipende il margine).
- IO33…IO37 liberi con FH4R2: da leggere sul datasheet Espressif.
- Expander: MCP23017-E/SO ×2 congelato (2×16 bit; In Production, LCSC C47023 con 1.184 pz). **Assegnazione linee: GPA7 e GPB7 solo uscite** (output-only secondo la scheda LCSC, da verificare sull'errata). Aperti: RESET non descritto compiutamente, VOL/VOH a 3,3 V non dati, glitch di IODIR per le linee bidirezionali, footprint EasyEDA, errata Rev. A.
- Supporto ESPHome di W5500 su ESP32-S3 e del logger su USB-Serial-JTAG.
- Stadi pistone ed EL-005 non ancora disegnati: i conteggi per questi due blocchi si basano sui requisiti.
