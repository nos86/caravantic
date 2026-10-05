# Caravantic Board rev. 2 — Functional Requirements

Status: **Draft**
Last updated: 2026-10-05

## 1. Contesto e scopo

Scheda singola installata nel camper (Ducato X244 2005, 2.3 JTD), alimentata dalla batteria servizi LFP 12 V, integrata in Home Assistant via Wi-Fi (ESPHome su Waveshare ESP32-S3-Tiny). Raccoglie: assetto e posizione, stato serbatoio acque chiare e attuazione degli scarichi, misure energetiche (2 shunt, meter AC SDM120), stato cellula/cabina, stato/comando inverter. È master di un bus RS485 su cui possono aggiungersi slave futuri.

**A monte:** batteria servizi 12 V, linea +12 V cabina, sensori serbatoio, shunt, inverter Renogy R-INVT-PUH1-201235-IT e suo comando remoto, SDM120.
**A valle:** Home Assistant; comando remoto in cabina.

**Fuori scopo:** rete multi-nodo CANopen della rev. 1; interfaccia diagnostica motore (delegata a uno slave futuro sul bus RS485, vedi REQ-IF-006); certificazioni CE/E-mark; gestione batteria/ricarica.

## 2. Requisiti

Stato: Confirmed = dichiarato dall'utente · Assumed = ipotesi da confermare · Open = non risolto.

### 2.1 Elettrici

**REQ-EL-001** (Must, Assumed) — Alimentazione da batteria servizi LFP: operativo 10–14,6 V continuo, sopravvivenza a inversione di polarità e a 16 V continui.
*Rationale:* ripreso da rev. 1 e FRD positioning board. *Acceptance:* funzionamento a 10,0 V e 14,6 V; −16 V per 5 min senza danno.

**REQ-EL-002** (Must, Assumed) — Catena di ingresso con rating ≥ 40 V e clamp TVS con V_C < rating del regolatore, impedenza serie conteggiata.
*Rationale:* bus condiviso con inverter 2000 W e caricabatterie. Riuso diretto di `old/hardware/schematics/01-power-supply.md` §1.

**REQ-EL-003** (Must, Open) — Pilotaggio valvola motorizzata scarico acque chiare (12 V) con misura di corrente. Corrente nominale/stallo e numero di fili da confermare (OPEN-04).

**REQ-EL-004** (Must, Open) — Pilotaggio bidirezionale del pistone elettrico (attuatore lineare 12 V) per scarico grigie. Corrente di stallo e presenza di finecorsa interni da confermare (OPEN-04). Implica ponte H.

**REQ-EL-005** (Must, Confirmed/Open) — Uscita a relè per alimentazione telecamera scarico grigie. Corrente della telecamera da confermare; se ≤ 2 A riuso dello stadio relè rev. 1 (IM06 + BSS138).

**REQ-EL-006** (Must, Confirmed) — 2 ingressi digitali 12 V (stato cellula, stato cabina). Soglie assunte da rev. 1: attivo ≥ 8 V, inattivo ≤ 2 V. *Acceptance:* lettura corretta 10–16 V; 24 V di fault senza danno.

**REQ-EL-007** (Should, Open) — Consumo a riposo: da definire. La board resta alimentata a camper fermo? (OPEN-08)

### 2.2 Interfaccia / protocollo

**REQ-IF-001** (Must, Confirmed) — IMU accelerometro + magnetometro su I²C. Precisione angolare richiesta per i cunei da definire (OPEN-10).

**REQ-IF-002** (Must, Confirmed) — Ricevitore GPS su UART.

**REQ-IF-003** (Must, Confirmed) — Livello serbatoio acque chiare da sender resistivo a galleggiante tipo automotive, **0–190 Ω**, verso massa.
*Rationale:* scelta utente. *Acceptance:* lettura monotona su tutta la corsa; errore ≤ ±5 % fondo scala dopo taratura a 3 punti (vuoto, metà, pieno) — soglia Assumed.
Note: verso della caratteristica (0 Ω = vuoto o pieno) da verificare sul pezzo; eccitazione sezionabile e fondo scala ADC ≤ 2,45 V (riuso rev. 1).

**REQ-IF-004** (Must, Confirmed) — Sensore di temperatura montato sul serbatoio. Tipo e range da confermare (OPEN-05).

**REQ-IF-005** (Must, Confirmed) — 2 ingressi per shunt 200 A / 75 mV montati **sul negativo** (low-side), corrente **bidirezionale ±200 A** su entrambi: ±75 mV differenziali (0,375 mV/A).
*Massa:* la massa della board è collegata alla massa veicolo/batteria, cioè al **lato batteria** degli shunt (Confirmed). Il capo lato carichi oscilla quindi fra −75 mV e +75 mV rispetto alla massa della board.
*Prescrizioni:* misura differenziale con collegamento Kelvin (due fili dedicati per shunt, non la massa di alimentazione come riferimento); ingresso bipolare con modo comune ≈ 0 V, tollerando un offset di massa di ±0,5 V (Assumed) dovuto ai cavi del negativo.
*Acceptance:* errore ≤ 1 % della lettura sopra 10 A, risoluzione ≤ 0,1 A (Assumed, da confermare — OPEN-06).

**REQ-IF-006** (Won't, Confirmed) — Interfaccia diagnostica motore **non sulla board**: delegata a uno slave futuro sul bus RS485 (REQ-IF-010). Nota per lo slave: sul 2.3 JTD 2005 la diagnosi risulta K-line KWP2000, non CAN ([Klavkarr](https://www.klavkarr.com/compatible/fiat-ducatoii-243/244/245/247-17000121), fonte commerciale; [fiatforum](https://www.fiatforum.com/threads/problems-with-obd2-data-on-x244.511426), forum).

**REQ-IF-007** (Must, Confirmed) — Interfaccia in serie fra inverter **Renogy R-INVT-PUH1-201235-IT** e il suo comando remoto (interruttore on/off + LED verde + LED rosso, nessun display — Confirmed dall'utente).
Funzioni: (a) lettura stato LED verde (POWER) e rosso (FAULT); (b) comando on/off dalla board; (c) remote originale funzionante; (d) **board non alimentata o in reset ⇒ remote collegato direttamente all'inverter**, comportamento identico all'impianto senza board.
*Acceptance:* con board spenta, l'interruttore del remote accende/spegne l'inverter; con board attiva, HA comanda on/off e legge i due LED; nessuna variazione visibile della luminosità dei LED del remote.

*Evidenza sull'interfaccia* — solo fonti forum ([diysolarforum, thread 15308](https://diysolarforum.com/threads/renogy-remote-switch-wiring-diagram.15308/), più utenti concordi, modelli Renogy diversi):
- Segnali **discreti, nessun protocollo seriale**: l'interruttore è un contatto pulito fra due poli, uno dei quali porta la tensione di batteria; ogni LED ha un pin pilotato dall'inverter; uno o due pin di massa.
- Livelli misurati sui pin LED: ~2,7 V (utente *shinikveech*) e 3,8 V verde / poco meno rosso (utente *Timmerich*).
- **Connettore variabile per modello:** RJ12 6P6C o RJ11 6P4C sui modelli più vecchi; **RJ45 8 poli** sui più recenti, con cicalino nel remote. Su un RJ45 1000 W: contatto su pin 3–5, LED verde pin 2, rosso pin 4, massa pin 7 (*Timmerich*). Un altro utente con RJ45 non è riuscito ad accendere cortocircuitando coppie di fili: la piedinatura RJ45 **non è univoca**.
- Inverter con selettore 0 / I / II: in II lo stato è governato dal remote (*Dr.HD*).
*Non confermato su questo modello:* tipo di connettore e piedinatura. Da misurare (OPEN-02).

*Topologia di requisito proposta:* relè di scambio a riposo trasparente — contatto NC = remote → inverter; eccitato = contatto della board → inverter, con stato dell'interruttore del remote letto come ingresso. Linee LED passanti, lette ad alta impedenza (≥ 100 kΩ, Assumed) per non alterarle.

**REQ-IF-008** (Must, Confirmed) — Modbus RTU su RS485 verso meter SDM120 (board = master).

**REQ-IF-010** (Must, Confirmed) — Il bus RS485 della board è **multi-drop ed estendibile** a slave futuri (es. slave diagnosi motore). Connettore con +12 V, GND, A, B per alimentare gli slave. Terminazione inseribile. Corrente massima erogabile agli slave da definire (OPEN-11).

**REQ-IF-009** (Must, Open) — Interfaccia verso comando remoto in cabina per lo scarico serbatoi (lato remoto: ESP8266/RP2040). Proposta in OPEN-07.

### 2.3 Ambientali

**REQ-ENV-001** (Should, Assumed) — −10…+60 °C, vibrazione veicolare, condensa possibile (da FRD positioning board).

### 2.4 Software / firmware

**REQ-SW-001** (Must, Confirmed) — Integrazione con Home Assistant via ESPHome su **Waveshare ESP32-S3-Tiny** (stesso modulo della rev. 1). UART necessarie: GPS, RS485, eventuale inverter (se seriale) — rientrano nelle 3 UART dell'ESP32-S3.

**REQ-SW-002** (Must, Assumed) — Stato sicuro: al reset/brown-out valvola e pistone fermi, relè diseccitato, per sole reti passive (pull-down). Riuso del principio rev. 1.

## 3. Punti aperti

| ID | Domanda | Requisiti |
|---|---|---|
| ~~OPEN-01~~ | Chiuso 2026-10-05: diagnosi motore delegata a slave RS485 | IF-006 |
| OPEN-02 | **[Sospeso 2026-10-05]** Remote inverter: RJ12 o RJ45? Selettore 0/I/II presente? Piedinatura: continuità interruttore, pin LED, masse; tensioni per pin in OFF/ON/FAULT | IF-007 |
| ~~OPEN-03~~ | Chiuso: sender resistivo 0–190 Ω | IF-003 |
| OPEN-04 | Valvola acque chiare (3 fili DN15?) e pistone grigie: modelli, corrente di stallo, finecorsa | EL-003, EL-004 |
| OPEN-05 | Sensore temperatura serbatoio: tipo (NTC, DS18B20…), scopo (antigelo?) | IF-004 |
| OPEN-06 | Shunt: confermare precisione (1 %) e risoluzione (0,1 A); lunghezza cavi Kelvin | IF-005 |
| OPEN-07 | Interfaccia comando cabina — vedi §6 | IF-009 |
| OPEN-08 | Board sempre alimentata o con wake da 12 V cabina? Budget a riposo | EL-007 |
| ~~OPEN-09~~ | Chiuso: ESP32-S3-Tiny | SW-001 |
| OPEN-10 | Risoluzione angolare richiesta per l'assetto | IF-001 |
| OPEN-11 | Corrente da erogare agli slave RS485 su +12 V | IF-010 |

## 4. Registro assunzioni

- Alimentazione, soglie ingressi 12 V, ambiente: ripresi da rev. 1 e da `frd-positioning-board.md`, non riconfermati per rev. 2.

## 5. Mappa di riuso da `old/`

| Parte rev. 1 | Riuso in rev. 2 | Note |
|---|---|---|
| Catena di ingresso (PTC, P-MOSFET ideal-diode + zener, TVS V_C < 40 V, filtro EMI depopolato) — `01-power-supply.md` §1 | **Sì, integrale** | |
| Power-latch / WAKEUP opto — `01` §2 | Valutare | Dipende da OPEN-08 |
| Ingresso opto 12 V (variante II) — `03-inputs.md` §6 | **Sì** → ingressi cellula/cabina | |
| Protezione pin ADC (R serie + clamp, fault 24 V), fondo scala ≤ 2,45 V, solo ADC1 — `03` §2, §5.5 | **Sì** → livello, temperatura | |
| Stadio relè IM06 + BSS138 + pull-down — `04b` | **Sì** → relè telecamera | Se I_cam ≤ 2 A |
| Sense INA180 + shunt — `05-motors.md` §4 | **Sì** → corrente valvola/pistone | Rivalutare shunt e gain sulle correnti reali |
| Vincoli MCU (ADC1, no strapping su uscite, stato sicuro) — `02-mcu.md` §2.2 | **Sì** | |
| IMU, GPS, livello — `frd-positioning-board.md` (Project) | **Sì** | HMC5883L: verificare disponibilità |
| CANopen multi-nodo, LSS, I/O expander, stepper, servo, 4 uscite configurabili | **No** | Fuori perimetro rev. 2 |
| `clean_water/clean_water.eprj2` (EasyEDA) | Da verificare | Contenuto non ancora esaminato |

## 6. Proposta OPEN-07 — interfaccia comando cabina

| Opzione | Cavo | Pro | Contro |
|---|---|---|---|
| **A. RS485 condiviso con SDM120** (remote = slave Modbus) | 4 fili: +12 V, GND, A, B | Nessun transceiver aggiuntivo sulla board; differenziale, robusto su cavi lunghi | Guasto sul cavo cabina blocca anche la lettura SDM120; latenza legata al polling |
| B. RS485 dedicato | 4 fili | Isola i due bus | Secondo transceiver e UART (UART già contesi, OPEN-09) |
| C. Solo Wi-Fi (ESP8266 → HA) | 2 fili (alimentazione) | Cablaggio minimo | Comando di scarico dipende da Wi-Fi e HA |
| D. Discreti 12 V (pulsanti + LED, nessun MCU nel remote) | ~6 fili | Massima semplicità, nessun firmware remoto | Più fili, ingressi/uscite in più sulla board |

Raccomandazione: **A** — coerente con REQ-IF-010 (bus estendibile): il comando cabina è uno slave come gli altri.

## 7. Storico revisioni

| Data | Modifica | Motivo |
|---|---|---|
| 2026-10-05 | Prima bozza rev. 2; rev. 1 archiviata in `old/` | Ridefinizione obiettivi |
| 2026-10-05 | Inverter: segnali discreti (fonti forum), relè trasparente a riposo; shunt ±200 A, massa lato batteria | Risposte utente + ricerca |
| 2026-10-05 | Motore delegato a slave RS485; inverter, sender 0–190 Ω, shunt low-side, ESP32-S3-Tiny | Risposte utente |
