# Brief — verifica del foglio "Inverter interface" (EasyEDA, MCP `easyeda-pro`)

Da incollare come primo messaggio nella nuova sessione con l'MCP attivo. Obiettivo: leggere il foglio **Inverter interface** (schematico "Mainboard", board "Caravantic") e dire se è **in linea con i requisiti** e se lo **schematico è corretto**. Sola lettura: non modificare il foglio, non toccare `*.eprj2`, non promuovere stati.

## Fonti da leggere prima
- `docs/frd.md`: REQ-IF-007, REQ-SW-002, REQ-EL-006, REQ-EL-008, OPEN-02. Nota: EL-001 (10–14,6 V) è **Assumed** e l'utente ha detto che 10 V non è una tensione operativa per la LFP; il limite basso non è ancora fissato.
- `hardware/schematic/a6_remote_inverter.md`: **sezioni vecchie superate**; vale l'ultima: "Rettifica 2026-10-18 (sera)" + "Revisione schema 2026-10-18" + "Specchio LED in hardware". Le sezioni "via A/B", "GPIO push-pull" e "open-drain" sono superate.
- `docs/components.md`: IM06 (K_TAKE/K_LVL, riserva sul pick-up), BSS84K HJC C54795811 (Q9/Q10), TLP293-GB, celle EL-006.
- `hardware/schematic/a3_sonda_grigie.md` ("Rilettura dal vivo"): **limite noto del tool**: la connettività non è verificabile via MCP (snapshot parziale di pin e fili); se vale ancora, chiedere all'utente uno screenshot del foglio per le connessioni e usare l'MCP per proprietà, valori e part number.

## Design atteso (da confrontare col foglio)
Connettori: RJ45 lato inverter e RJ45 lato remote. Pinout Renogy (Assumed, lettura confermata dall'utente): 2 GND · 3 +12 V · 4 VERDE · 5 VIN · 7 ROSSO · 1,6,8 NC. Contatto del remote fra pin 3 e 5.
- **Relè:** 3 × TE IM06 (12 V), bobine con BSS138 low-side + 1N4148WS di ricircolo + pull-down di gate 100 kΩ. K_TAKE_A: VIN (comune = inverter, NC = remote, NO = nodo scheda) e pin 4; K_TAKE_B: pin 7; K_LVL: +12 V verso nodo VIN scheda (via R serie). **Tutti diseccitati ⇒ remote diretto sull'inverter** (IF-007 d).
- **Letture con TLP293-GB** (dominio inverter, riferite al pin 2, nessun legame di massa con la board): U14 `SIG_INVERTER_12V` (pin 3), U17 `SIG_INVERTER_REQ` (pin 5 lato remote), U15 `SIG_INVERTER_GREEN`, U16 `SIG_INVERTER_RED`. Celle 12 V: R 8,2 kΩ + BZT52C3V3 + (1N4148WS) + pull-up 12 kΩ a 3V3. Celle LED: R ≈ 1,8 kΩ **senza Zener**. Pull-up: R52, R62, R55, R56 (12 kΩ).
- **Specchio LED:** Q9/Q10 = BSS84K (P-MOSFET), **source a 3V3, gate = nodo GREEN/RED (collettore opto), drain → R57/R58 220 Ω → pin 4/7 lato remote** (tramite i contatti dei relè). L'ESP tira il nodo basso in open-drain per forzare il LED (wired-OR).
- Decisione utente: **nessun 1N4148WS antiparallelo** sui LED degli opto U14–U16.

## Cosa verificare
1. **Requisiti:**
   - IF-007 (a) leggere LED verde/rosso; (b) comando on/off; (c) remote funzionante; (d) board spenta/reset ⇒ remote diretto; nessuna variazione visibile della luminosità dei LED.
   - SW-002: stato sicuro con sole reti passive (pull-down, gate dei BSS138, nodi GREEN/RED alti a reset, relè diseccitati).
   - EL-006/EL-008 per le celle a 12 V (soglie 8 V/2 V, transitori).
2. **Correttezza del foglio:**
   - **Q9/Q10: orientamento** (source a 3V3, drain verso R57/R58; l'errore trovato prima era l'inversione) e pinout del footprint (1 = G, 2 = S, 3 = D per C54795811).
   - Relè: contatti sui pin giusti (3 linee: VIN, pin 4, pin 7), NC/NO scambiati? BSS138 + diodo di ricircolo (catodo a +12 V) + pull-down gate; polarità della bobina IM06 (relè polarizzato).
   - Pin 2 (GND remote/inverter) **non** collegato a GND board; TLP293 con LED a pin 2, uscite verso 3V3/GND board. Nessun nodo GND comune fra i due domini tranne dove previsto.
   - Rail: pull-up opto a 3V3, bobine a +12 V protetto; nessun net a +12 V diretto sul 3V3.
   - Valori e part number: R57/R58 220 Ω; R52/R62/R55/R56 12 kΩ; R celle LED ≈ 1,8 kΩ.
   - Corti 4/7 verso pin 3 (+12 V adiacente): body diode di Q9/Q10 e **diodo Schottky serie al drain** (da decidere/valutare, non ancora disegnato); R 0805 a 16 V.
   - Net/etichette duplicate o orfane, pin non collegati, designatori duplicati.
3. **Coerenza foglio ↔ documenti:** designatori e valori di a6 e components.md contro il foglio; dire cosa è nel foglio e non nella doc, e viceversa.

## Fuori scopo
GPIO e assegnazioni (da fare), firmware, layout PCB, selezione del relè (il pick-up IM06 a 10 V è un tema aperto legato a EL-001).

## Output richiesto
Tabella `Punto · Esito (OK / Errore / Non verificabile) · Evidenza (designatori/net/proprietà) · Azione`, poi elenco breve di errori in ordine di gravità. Dichiarare ciò che non si può verificare dall'MCP (connettività) e chiedere lo screenshot; non scrivere nei file di progetto senza richiesta. Lingua: italiano.
