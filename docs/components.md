# Registro componenti — comuni (schede: [idraulica](../idraulica/components.md), [elettrica](../elettrica/components.md))

> Le sezioni A1 (ingressi opto) e AUX sono ora in [`elettrica/components.md`](../elettrica/components.md). Le sezioni di verifica qui sotto (2026-10-15) mescolano pistone e ingressi A1 e restano nel comune.

## Verifica estesa dello schematico (2026-10-15)

Sei `datasheet-verifier` sui componenti dello stadio pistone e dell'ingresso A1. **Limite comune:** gli agenti non hanno una shell e non hanno potuto leggere i PDF. Tutti i dati sotto vengono da pagine LCSC/JLCPCB o da riassunti (**fonti deboli**) e nessun valore è promosso a Confirmed. Unico datasheet letto direttamente: Toshiba TLP293 (`pdftotext`). Il PDF luJing BSS138 ha glifi codificati: cifre non leggibili.

### Codici LCSC e disponibilità (istantanea 2026-10-15)

| Rif. | Pezzo | LCSC | Stock | Note |
|---|---|---|---|---|
| R7 | RALEC LR2512-22R005F4 (5 mΩ ±1 %, 2 W, ±25 ppm/°C) | **C108931** | 26.510 | MOQ 5. C154671 (±5 %) resta scartato; alternativa 3 W: C154688 |
| Q2 | VBsemi `IPD50N06S4L12ATMA2-VB` | **C45662394** | **10** | Il P/N `IPD50N06S4L-12-VB` non esiste su LCSC. Rischio approvvigionamento alto |
| U3 | LX INA180A2IDBVR(LX) | C48533471 | 41.230 | MOQ 5 |
| D6 | R+O BZT52C12S (SOD-323) | C19077447 | 1,02 M | MOQ 50 |
| D7 | R+O: esiste BZT52C3V3S (SOD-323, C19077437) e BZT52C3V3 (SOD-123, C19077396, 350 mW) | C19077396 | 714 k | Verificare quale è nello schematico |
| D5 | SMAJ33A: nessun luJing trovato; R+O C41376399 | C41376399 | 6.940 | Verificare produttore/codice nel BOM |
| D8 | SS56: nessun R+O in SMA; R+O ha SS56F in SMAF (C41411775, 5 A, 850 mV a 5 A, Tj 125 °C) | – | 15.940 | **Punto più critico**: verificare codice reale |
| K1 | TE RTE24012 | C1524518 | 2.747 | Pagina TE: "Active" ma "not currently available" |
| Q1 | luJing BSS138 | C53058666 | 1.400 | MOQ 20 |
| R | UNI-ROYAL 1 kΩ / 47 kΩ / 100 Ω | C17513 / C17713 / C17408 | ampio | MOQ 100 |
| R | FOJAN FRC0805F1202TS 12 kΩ | C2907225 | 836 k | FRC0805J822 TS (8,2 kΩ) **non trovato** in 0805 (solo 0603 C2907205); Sekorm attribuisce la serie a FOSAN |
| C | Yageo 10 nF / 100 nF | C83170 / C49678 | ampio | Per C49678 copie in cache segnano "discontinued": ricontrollare |
| D2/D4 | Hangyu BZT52C3V3 | C54930248 | 1.750 | MOQ 50, 350 mW |
| D1/D3 | DOWO 1N4148WS | C22374708 | 22.550 | MOQ 50 |
| P1/P2 | JILN JL500-50802G01 | C709041 | 4.940 | MOQ 5 |
| CN1 | MAX MX128-5.0-04P | C5290369 | 3.175 | MOQ 5 |

### Esiti per gruppo

- **TLP293(GB) – datasheet Toshiba letto:** CTR ≥100 % a I_F = 0,5 mA e a 5 mA (25 °C, V_CE = 5 V); a 2 mA plausibile ma la curva non è letta. CTR saturo ≥30 % (I_F = 1 mA, V_CE = 0,4 V). V_CE(sat) ≤0,3 V a I_C = 0,2 mA / I_F = 1 mA. Tempi solo con R_L = 100 Ω (t_r 2 µs) e 1,9 kΩ. Nessun dato a 60 °C nel testo (solo figure). **Carica gate Q2 (70 nC):** I_F ≈ 2 mA → ≥35 µs nel caso migliore contro obiettivo 40 µs: **margine nullo, non confermabile** (a 60 °C/fine vita probabilmente perso). Open: misura o simulazione col CTR di caso peggiore.
- **BSS138 luJing (Q1):** R_DS(on) a 3,3 V non documentata. Margine richiesto per bobina K1 a 10 V (≥9,6 V): R_DS ≤ ~13,5 Ω a −10 °C, ~17 Ω a 60 °C. Dato più vicino (ON/Fairchild, non luJing): 6 Ω max a 4,5 V. **Non verificabile**: serve curva dal PDF o misura su campione. Si somma al margine nullo di pull-in già aperto.
- **Stadio pistone, diodi (R+O):** nessun datasheet letto. D8: il 5 A in SMA non è verificato per R+O (SS56F ha Tj 125 °C); I_R a caldo e dissipazione a 10 A non calcolabili con dati verificati. D5: V_F a bassa corrente di un TVS non caratterizzato nei listini. D6: P_D 200 mW, a 60 °C ≈144 mW (calcolo con R_θJA di terzi); picchi 12 mA×400 ms al limite. D7: I_R a 1,75–3 V non trovata; resta da misurare.
- **R7:** codice trovato (C108931); potenza a 70 °C, derating, sovraccarico e land pattern Kelvin non letti dal PDF RALEC. Il nome EasyEDA del MPN va ancora corretto in `LR2512-22R005F4`.
- **K1 pin-out:** 12 = NC, 14 = NO, 22 = NC, 24 = NO **non verificati** (disegno wiring TE in immagine). Se scambiati, il verso a riposo del pistone si inverte. Da controllare a mano sul PDF TE RT2 contro il footprint.
- **Connettori:** P1/P2 sezione max catalogo 2 mm² (cavo previsto fino a 2,5 mm² non entra); 15 A senza condizioni. Footprint `JL500-50002G01` nel nome = codice del pezzo da 5,00 mm, pezzo scelto 5,08 mm: verificare le quote dei pad. CN1 sezione min catalogo 1 mm² (cavo 0,5 mm²: serve puntale o 1 mm²); 10 A senza condizioni. Foratura e pin 1 non verificati.
- **Passivi:** potenza 0805 1/8 W a 70 °C (riassunti). **R1/R3 8,2 kΩ:** il load dump (101 V, 400 ms) dà 1,13–1,22 W; i 2,7 W del registro (riga 39) sono l'impulso ISO 1 da 2 ms, non il load dump (nessuna discrepanza, correzione 2026-10-15). Resta 9–22× la potenza nominale e non esiste curva d'impulso per la serie: il rischio accettato (REQ-EL-008) resta tale. Perdita DC bias e invecchiamento X7R di C1–C3 non verificati.
- **Diodi A1:** Hangyu BZT52C3V3 (350 mW, 5 µA a 1 V, V_F e I_FSM non trovati) e DOWO 1N4148WS (V_F ≈1,0 V a 50 mA, I_FSM 2 A, Tj discordante 150/175 °C): solo listini. Uso ben sotto i limiti nominali, ma dati senza seconda fonte.

### Azioni aperte per l'utente
1. Controllare nel BOM EasyEDA i codici reali di D5, D7, D8, Q2, R1/R3 (vedi tabella).
2. Aprire a mano i PDF (R+O C19077447/C19077396/C41376399/C41411775, RALEC C108931, TE RT2, luJing C53058666) o fornirli per la lettura con `pdftotext`.
3. Verificare pin-out K1 e quote pad P1/P2.
4. Decidere su cavo P1/P2 (≤2 mm²) e CN1 (puntale).

## Validazione del dimensionamento sui valori nominali (2026-10-15)

**Base:** netlist e valori dell'ultima lettura live (R7 5 mΩ, C2/C3 corretti, D8 corretto), più l'ispezione del backup `caravantic_2026-10-15-00-35.epro2` (precedente alle ultime correzioni). **EasyEDA non era connesso**: non è stato possibile rileggere lo schematico live. Dati dei componenti da datasheet già letti o da fonti deboli dichiarate sopra. Condizioni: V_linea 10–14,4 V (nominale 12 V), −10…+60 °C, soglia di lavoro 7,0 A (Confirmed), stallo 10 A solo come guasto (Assumed).

### Stadio pistone — verifica nominale

| Blocco | Calcolo nominale | Limite | Utilizzo | Esito |
|---|---|---|---|---|
| Bobina K1 (360 Ω) | 12 V → 33 mA, 0,40 W; 10 V → 27,8 mA | BSS138 I_D 220 mA | 15 % | OK. **Margine di pull-in a 10 V/60 °C nullo (già aperto)**, R_DS(on) di Q1 a 3,3 V non documentata (ammessi 13–17 Ω) |
| Ricircolo bobina D5 | conduzione diretta, circa 0,8 V sopra +12 V; lato drain Q1 nel transitorio: 12 V + V_BR 36,7–40,6 V ≈ 49–53 V | V_DS Q1 50 V | **~100 %** | Solo nei transitori sul rail (load dump a monte): margine nullo, da gestire con la protezione d'ingresso del rail |
| LED U4 (R9 1 kΩ) | I_F = (3,3 − 1,25)/1 kΩ = 2,05 mA, P(R9) 4 mW | GPIO ESP32-S3 | <10 % | OK |
| Gate Q2 a V_linea = 12 V | V_G ≈ 11,5 V (R8 47 kΩ, V_CE(sat) ≈ 0,2 V) | V_GS max ±16 V (Infineon) | 72 % | OK |
| Gate Q2 a V_linea = 14,4 V | Zener D6 limita a 11,4–12,7 V; corrente nello Zener limitata da R10 a (14,4 − 12 − V_CE)/1 kΩ ≈ 2 mA → 25 mW | P_D 144 mW a 60 °C | 17 % | OK (R10 protegge D6 anche con CTR 600 %) |
| Gate Q2 a V_linea = 10 V | V_G ≈ 9,5 V | R_DS(on) specificata a 10 V; a 4,5 V circa 17 mΩ | – | OK |
| Carica gate (70 nC) | I_C = CTR × I_F: CTR min 100 % → 2 mA → 35 µs; CTR tipico 200–300 % → 12–17 µs | nessun requisito di tempo imposto dal carico (perdita di commutazione a 7 A < 2 mJ) | – | OK. **Il vincolo "40 µs" usato prima non è un requisito**: va tolto; 35 µs al caso peggiore sono accettabili |
| Q2 conduzione | R_DS(on) max 12 mΩ a 25 °C, ×1,5 a ~100 °C = 18 mΩ: 7 A → 0,88 W; 10 A (≤200 ms) → 1,8 W | T_j 175 °C; R_θJA TO-252 su rame minimo assunta 50–60 K/W (**Assumed**, non letta) | T_j ≈ 105–115 °C a 60 °C ambiente | OK con il rame del PCB; verificare R_θJA sul datasheet VBsemi |
| Q2 sovratensione | picco di spegnimento clampato da D8 a ≈ 12 V + V_F(D8) ≈ 13–15 V | V_DS 60 V | 25 % | OK |
| Shunt R7 5 mΩ | 7 A → 35 mV, 0,245 W; 10 A → 50 mV, 0,50 W | 2 W a 70 °C | 12 % / 25 % | OK (derating RALEC non letto) |
| U3 INA180A2 (G = 50) | 7 A → 1,75 V; 10 A → 2,5 V; 0 A → ≤5 mV | V_S 5 V; ADC lineare fino a ~2,45 V | 7 A: 71 % del fondo scala ADC | OK. A 10 A (guasto) l'uscita satura l'ADC: la soglia 7 A deve scattare prima |
| Filtro R12/R13 + C1 | f(−3 dB) differenziale 1/(2π·200 Ω·10 nF) ≈ 80 kHz; bias −6 µA × 100 Ω = 0,6 mV in modo comune | – | – | OK |
| R11 1 kΩ + C2 100 nF + D7 | f(−3 dB) ≈ 1,6 kHz; sovratensione: (5 − 3,3 V)/1 kΩ = 1,7 mA → 5,6 mW nello Zener | P_D D7 350 mW | 2 % | OK. Perdita di D7 vicino a 2,4 V da misurare (errore: 20 µA × 1 kΩ = 20 mV ≈ 0,08 A al caso peggiore) |
| Contatti K1 | 7 A continui | 8 A (carico motore, RT2) | 88 % | OK. Contatti non devono mai commutare sotto carico (sequenza SW ENA off → 20 ms → DIR → 20 ms → ENA on) |
| Morsetti P1/P2 | 7 A / 10 A guasto | 15 A (catalogo, senza condizioni) | 47 % / 67 % | OK numericamente; sezione cavo max 2 mm² |
| Fusibile esterno | stallo 10 A ≤200 ms, regime 7 A, contatti K1 8 A | – | – | **Open:** valore non definito. Un fusibile da 10 A non protegge i contatti K1 (8 A) da uno stallo prolungato; indicazione: 7,5–8 A ritardato (da confermare con inrush misurato) |

### Ingressi A1 (R1–R4, D1–D4, U1–U2) — verifica nominale
- IN_CAB a 15 V: I_LED = (15 − 3,3 V_Z − 1,2 V_F)/8,2 kΩ ≈ 1,3 mA; a 12 V ≈ 0,9 mA. P(R1) 14 mW (11 %), P(D2) 4 mW. Coerente con la simulazione (`elettrica/sim/a1_ingressi/`) e con l'assorbimento di circa 1 mA accettato.
- Uscita: R2 12 kΩ a 3,3 V → 0,275 mA; CTR saturo GB ≥30 % a I_F = 1 mA → 0,3 mA a 15 V (margine ~9 %), a 12 V (0,9 mA) 0,27 mA: opto al limite della saturazione ma V_OL resta sotto la soglia bassa ESP32 (0,8 V): OK sul nominale, margine ridotto.
- Sollecitazioni di impulso: vedi riga 39 (load dump 1,13 W, ISO 1 2,7 W) — rischio accettato REQ-EL-008, nessun dato d'impulso del costruttore.

### Esito della validazione
- **Dimensionamento nominale: valido** per tutti i blocchi di potenza e di misura dello stadio pistone a 7 A (utilizzi massimi: Q2 e K1 sul 7 A, ADC 71 %).
- **Tolto un vincolo errato** (carica gate in 40 µs): non è un requisito.
- **Punti non chiusi (non nominali):** pull-in K1 a 10 V/60 °C, R_DS(on) Q1 a 3,3 V, picco di D5 vs V_DS Q1 nei transitori, fusibile, R_θJA Q2, derating R7.
- **Schematico:** riletto live il 2026-10-15 (vedi sotto, 34 elementi, nessuna incoerenza di collegamento). Residuo da fare nell'editor (R7 è già corretto): MPN di R7 → `LR2512-22R005F4` (LCSC C108931); Q2 `IPD50N06S4L-12-VB` non esiste su LCSC con quel nome (reale: `IPD50N06S4L12ATMA2-VB`, C45662394, 10 pz); D5 nel backup ha codice C53058808, non verificato (l'agente ha trovato R+O C41376399); K1 pin-out 12/14/22/24 non verificato.

### Rilettura live dello schematico (2026-10-15)

Letto da `easyeda_schematic_snapshot` (34 elementi, un foglio, confidenza "partial": le net sono ricostruite dalla geometria dei fili, i pin risultano tutti toccati da un filo). **Nessuna incoerenza di collegamento.**

| Net | Pin |
|---|---|
| Rail +12 V (bobina) | D5.K, K1.A1 |
| Linea attuatore +12 V | P2.1, K1.14 (NO1), K1.22 (NC2), D8.K, U4.C (collettore) |
| GND_SW | Q2.D, D8.A, K1.12 (NC1), K1.24 (NO2) |
| Pistone | K1.11 → P1.1, K1.21 → P1.2 |
| Bobina | K1.A2, Q1.D, D5.A |
| Gate Q1 | Q1.G, R6.2, R5.2 (R6.1 = `OUT_LINEAR_MOTOR_DIR`; R5.1 e Q1.S a GND) |
| Gate Q2 | Q2.G, R10.2, R8.2, D6.K (U4.E → R10.1; R9.2 → U4.A, R9.1 = `OUT_LINEAR_MOTOR_ENA`, U4.K a GND) |
| Source Q2 | Q2.S, R7.2, R8.1, D6.A, R12.1 |
| Massa shunt | R7.1, R13.1, U3.GND, C2.1, D7.A, GND |
| Misura | R12.2, C1.2 → U3.IN+; R13.2, C1.1 → U3.IN−; U3.OUT → R11 → `IN_LINEAR_MOTOR_SENSE` con C2 e D7.K; U3.VS e C3 su +5V |

Verifiche: polarità di D5 (flyback), D6 (Zener gate-source, catodo sul gate), D7 (clamp positivo a GND), D8 (anodo GND_SW, catodo sulla linea +12 V) corrette; IN+ sul lato source dello shunt e IN− sul lato massa (segno corretto per corrente Q2→GND); C2 e C3 distinti e collegati; il rail della bobina e la linea attuatore sono due net separate (come da progetto: bobina dal rail di scheda, linea attuatore dal fusibile esterno).

MPN riletti: **R7 = `LR2512-22R005F4`** (corretto); K1 `RTE24012`; Q2 `IPD50N06S4L-12-VB` (non esiste su LCSC con questo nome: usare `IPD50N06S4L12ATMA2-VB`); D5 luJing `SMAJ33A` (nessun luJing trovato su LCSC, solo R+O C41376399: scegliere il codice nell'editor); D7 R+O `BZT52C3V3` (SOD-123, coerente con C19077396); D8 R+O `SS56` in SMA (nessun R+O SS56 in SMA trovato, esiste SS56F in SMAF); footprint P1/P2 nominato `...50002G01` (5,00 mm) per un pezzo da 5,08 mm.

Non verificabile da schematico: pin-out fisico di K1 (12 = NC, 14 = NO) e quote dei pad dei footprint.

## U_EX1, U_EX2 (expander I/O, A8) — Microchip MCP23017 (SSOP-28 `-E/SS` o SOIC-28 `-E/SO`)
- Requisiti: REQ-IF-012 (Assumed: RESET con pull-down passivo e rilascio da firmware, uscite sicure al reset), REQ-SW-002 (stato sicuro), REQ-EL-006 (ingressi ≤ 100 ms, polling). 21 linee → 2 esemplari da 16 bit (32 linee, 11 di scorta). Stato: **Congelato** (2026-10-23, conferma utente; package scelto: **SOIC-28 `MCP23017-E/SO`, LCSC C47023**). Famiglia scelta da me (non da un confronto a tappeto): le alternative comuni PCA9535/TCA9535/TCA9555 non hanno il pin RESET; riserva: NXP PCAL6416A (non verificata).
- Verifica `datasheet-verifier` del 2026-10-23 su **DS20001952C (luglio 2016)**, letto tramite una conversione automatica del PDF (r.jina.ai), non dal PDF diretto: **da ricontrollare a vista prima di congelare**; **mono-fonte** (seconde fonti solo forum).
- Parametri decisivi (DS20001952C, Tab. 1-1, 1-2, 1-3, Tab. 2-1, sez. 3.0):
  - VDD 1,8–5,5 V; 400 kHz specificati per 2,7–5,5 V (ok a 3,3 V: TLOW ≥ 1,3 µs, tR/tF ≤ 300 ns, CB ≤ 400 pF); 1,7 MHz solo 4,5–5,5 V. Il datasheet è incoerente sul campo di temperatura (+125 °C solo a 4,5–5,5 V): per il progetto vale −40…+85 °C.
  - Indirizzi 0x20–0x27 da A2:A0 (**non lasciare flottanti**): nessun conflitto con 0x30, 0x40, 0x48, 0x49, 0x6A.
  - **RESET** (attivo basso, Schmitt): VIL max 0,2·VDD (0,66 V a 3,3 V), VIH min 0,8·VDD (2,64 V), impulso minimo TRSTL 1 µs, **uscite in alta impedenza entro 1 µs** (TIOZ); "deve essere polarizzato esternamente" (non flottante). Default dopo POR: IODIR = 0xFF (tutti ingressi), GPPU = 0 (pull-up interni spenti).
  - SDA/SCL: VIL max 0,66 V e VIH min 2,64 V a 3,3 V (soglie 0,2/0,8·VDD, più strette dello standard 0,3/0,7); VOL SDA max 0,6 V a 3 mA (VDD 1,8 V), 0,8 V a 4,5 V; punto a 3,3 V non dato.
  - GPIO: ingressi VIH/VIL come sopra; perdita ±1 µA; 25 mA per pin è un assoluto massimo, non una corrente garantita; VOL/VOH a 3,3 V **non specificati** (solo a 4,5 V: VOL 0,6 V a 8 mA).
- **Non documentato dal datasheet (impatti):**
  - Cosa azzera il pin RESET e se ripristina la macchina a stati I²C; tempo di recupero a 3,3 V (THLD = 0 ns tipico solo a 5 V). Il datasheet garantisce però le uscite in alta impedenza durante RESET: è ciò che serve per lo stato sicuro (gate con pull-down). Conseguenza di progetto: dopo ogni reset il firmware **riscrive tutti i registri** e attende qualche µs; il recupero del bus non si affida al pin RESET ma al bus-clear (9 impulsi SCL).
  - CIN dei pin SDA/SCL (solo CB ≤ 400 pF e CIO ≤ 50 pF per i GPIO), timeout di bus, clock stretching: capacità del bus da stimare con prudenza.
  - Passaggio IODIR ingresso → uscita con OLAT = 0 senza glitch (inferenza, non garanzia): per `SIG_INVERTER_GREEN/RED` da provare al banco. Leggere GPIO restituisce il pin, non il latch: niente read-modify-write su GPIO/OLAT (usare OLAT).
- ESPHome: componente `mcp23017` (famiglia `mcp230xx`), I²C, 16 pin, indirizzo 0x20 di default, modo INPUT/OUTPUT per pin con `pullup`, `inverted`, `interrupt` (esphome.io/components/mcp230xx; non dice nulla sul RESET). Il passaggio dinamico input/output per le linee bidirezionali è da provare.
- **Verifica LCSC/produzione (2026-10-23, pagine lette direttamente nel browser):** pagina LCSC C47023 = MCP23017-E/SO, SOIC-28-300mil, **Extended**, stock **1.184**, 1,77 USD (1 pz) / 1,50 (10 pz), −40…+85 °C, 1,8–5,5 V, funzione di reset, nessun avviso NRND sulla pagina. Pagina prodotto Microchip (microchip.com/en-us/product/MCP23017): **Status: In Production**; esiste un "MCP23017 Rev. A Silicon Errata" **non letto**. Footprint EasyEDA ancora da verificare. Il datasheet attuale è sul sito Microchip (DS20001952): la rev. C del 2016 usata per i dati potrebbe non essere l'ultima.
- ⚠️ La scheda LCSC riporta nelle feature "Pins GPA7, GPB7 are output only for MCP23017" (testo del datasheet, **non verificato sul PDF**): **GPA7 e GPB7 non vanno usati come ingressi** né per le linee bidirezionali `SIG_INVERTER_GREEN/RED`; solo uscite (con 32 linee e 21 usate non costa nulla). Da leggere nell'errata.
- LCSC/JLCPCB (fonte debole, istantanea del verificatore 2026-10-23, superata per il SOIC dalla verifica sopra): `-E/SS` **C506653**, SSOP-28 (5,3 mm, passo 0,65 mm da JLCPCB), Extended, stock circa 90, uno snippet lo segna "not recommended for new designs" (non confermato); `-E/SO` **C47023**, SOIC-28 largo, Extended, stock circa 3.200. Stato produzione sul sito Microchip: **non verificato** (403). Footprint EasyEDA verificato: **no**.
- Alternative scartate: PCA9535/TCA9535/TCA9555 (nessun pin RESET); TCA6416A, PCAL6416A (non analizzati, solo 2 indirizzi).
- Rischi: stock di C506653 (SSOP scartato: si usa il SOIC C47023); datasheet del 2016 con incoerenze interne; RESET non descritto compiutamente; due esemplari Extended (costo di setup in più); fonte unica convertita.
