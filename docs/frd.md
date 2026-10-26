# Caravantic Board rev. 2 — Functional Requirements (comune)

Status: **Draft**
Last updated: 2026-10-26

## 1. Contesto e scopo

Scheda singola installata nel camper (Ducato X244 2005, 2.3 JTD), alimentata dalla batteria servizi LFP 12 V, integrata in Home Assistant via Wi-Fi (ESPHome su Waveshare ESP32-S3-Tiny). Raccoglie: assetto e posizione, stato serbatoio acque chiare e attuazione degli scarichi, misure energetiche (2 shunt, meter AC SDM120), stato cellula/cabina, stato/comando inverter. È master di un bus RS485 su cui possono aggiungersi slave futuri.

**A monte:** batteria servizi 12 V, linea +12 V cabina, sensori serbatoio, shunt, inverter Renogy R-INVT-PUH1-201235-IT e suo comando remoto, SDM120.
**A valle:** Home Assistant; comando remoto in cabina.

**Fuori scopo:** rete multi-nodo CANopen della rev. 1; interfaccia diagnostica motore (delegata a uno slave futuro sul bus RS485, vedi REQ-IF-006); certificazioni CE/E-mark; gestione batteria/ricarica.

## 1.1 Divisione in due PCB (decisione utente, 2026-10-26)

Il progetto è diviso in **due schede** (Confirmed). Specifiche e dettagli di implementazione sono nelle cartelle di scheda; qui restano contesto, requisiti trasversali, punti aperti comuni, riuso da `old/` e storico.

| Scheda | Cartella | Perimetro | REQ assegnati (Assumed) |
|---|---|---|---|
| Idraulica | [`idraulica/`](../idraulica/frd.md) | acque chiare, acque grigie, pompa, motori | EL-003, EL-004, EL-005, IF-003, IF-004, IF-009, IF-011 |
| Elettrica | [`elettrica/`](../elettrica/frd.md) | shunt, inverter, relè globale | IF-005, IF-007, IF-008 |

**Non ancora assegnati (restano qui, da decidere insieme):** EL-001/EL-002 (alimentazione: probabilmente replicata su entrambe), EL-006/008/009 (ingressi opto IN-CAB/IN-CEL/AUX), EL-007, IF-001 (IMU/magnetometro), IF-002 (GPS), IF-010 (bus RS485), IF-012 (Ethernet), SW-001/002, ENV-001. Aperto: quale scheda ospita l'MCU, e come comunicano le due schede (OPEN-17). Mappa pin (a8), ingressi (a1) e IMU (a7) in `hardware/schematic/` sono **da rifare** dopo questa decisione.

## 2. Requisiti

Stato: Confirmed = dichiarato dall'utente · Assumed = ipotesi da confermare · Open = non risolto.

### 2.1 Elettrici

**REQ-EL-001** (Must, Assumed) — Alimentazione da batteria servizi LFP: operativo **12–14,6 V** continuo (minimo alzato da 10 V il 2026-10-18: sotto 12 V la LFP è scarica, scelta dell'utente), sopravvivenza a inversione di polarità e a 16 V continui.
*Rationale:* ripreso da rev. 1 e FRD positioning board. *Acceptance:* funzionamento a 10,0 V e 14,6 V; −16 V per 5 min senza danno.

**REQ-EL-002** (Must, Assumed) — Catena di ingresso con rating ≥ 40 V e clamp TVS con V_C < rating del regolatore, impedenza serie conteggiata.
*Rationale:* bus condiviso con inverter 2000 W e caricabatterie. Riuso diretto di `old/hardware/schematics/01-power-supply.md` §1.




**REQ-EL-006** (Must, Confirmed) — 2 ingressi digitali 12 V **opto-isolati**:
- **IN-CAB** (stato cabina): +15 sotto chiave del Ducato (Confirmed), **derivato dalla radio con un cavo da 0,5 mm²** (Confirmed, utente 2026-10-08). Campo nominale **11,5–13,8 V** (Confirmed). Assorbimento non vincolante.
- **IN-CEL** (stato cellula): uscita della centralina cellula (Confirmed). Si assume high-side: **+V_batt LFP a cellula accesa**, flottante o 0 V a cellula spenta (Assumed, OPEN-12). Campo nominale **12,8–14,4 V** (Confirmed). Assorbimento a cellula attiva: **circa 1 mA accettato** (Confirmed, utente 2026-10-08); nessuno strobe.
- Optoaccoppiatore: **Toshiba TLP293, rango GB** (Confirmed, scelta utente 2026-10-08; sostituisce il PC817 scelto il 2026-10-05).
- Ritorno del LED dell'opto sulla **massa della board**, senza morsetto di ritorno dedicato (Confirmed). L'opto non protegge quindi da offset di massa fra sorgente e board: ne serve solo la robustezza ai fault.

Prescrizioni:
- Isolamento galvanico con optoaccoppiatore *shall* (Confirmed, scelta utente).
- Soglie: attivo ≥ 8 V, inattivo ≤ 2 V (Assumed, valori ereditati da rev. 1).
- Tempo di risposta ≤ 100 ms (Confirmed). Il filtro può essere dimensionato fino a questo limite.
- Corrente assorbita da IN-CEL a cellula attiva: circa 1 mA (Confirmed, 2026-10-08; sostituisce il limite Assumed di 0,1 mA). In progetto 1,0 mA a 12,8 V e 1,2–1,25 mA a 14,4 V (simulato). IN-CAB: nessun limite.
- Immunità ai transitori: REQ-EL-008.

*Acceptance:* [B] lettura corretta fra 10 e 16 V in ingresso e 0 V letto come inattivo, su entrambi i canali; [B] 24 V continui per 5 min senza danno; [B] −16 V continui per 5 min senza danno; [B] il fronte in ingresso compare sul GPIO entro 100 ms; [B] corrente di IN-CEL a 14,4 V ≤ 1,5 mA (Assumed).

**REQ-EL-009** (Must, Confirmed) — 2 ingressi digitali generici di riserva **IN-AUX1, IN-AUX2**, opto-isolati, **configurabili per canale con jumper a saldare** (Confirmed, utente 2026-10-15):
- **Modo H, attivo a 12 V:** come REQ-EL-006. Attivo con ingresso ≥ 8 V; inattivo con ingresso ≤ 2 V o aperto.
- **Modo L, attivo a massa:** la catena del LED è alimentata dal **+12 V batteria protetto della board** (Confirmed) e l'ingresso la chiude verso massa (contatto pulito o open-collector). Attivo con ingresso ≤ 2 V verso massa; inattivo con ingresso aperto o ≥ V_board − 2 V (Assumed).
- I jumper escono dalla fabbrica **aperti**: il canale non funziona finché non viene configurato (Confirmed). Una configurazione errata *shall* non danneggiare nulla.
- Stessa rete e stesso optoaccoppiatore di REQ-EL-006 (TLP293 GB, ritorno su massa della board), tempo di risposta ≤ 100 ms.
- Corrente assorbita a ingresso attivo ≤ 1,5 mA per canale, in entrambi i modi (Confirmed). Nel modo L è prelevata dalla batteria servizi.
- Immunità ai transitori: REQ-EL-008, applicato in entrambi i modi (uso generico, quindi caso peggiore lato alternatore).

*Rationale:* ingressi di riserva per segnali non ancora noti, che possono arrivare da sorgenti high-side o da contatti verso massa.
*Acceptance:* [B] per ogni modo e su entrambi i canali, lettura corretta con la board alimentata a 10,0 V e a 14,6 V; [B] modo L: lettura "attivo" con un contatto da 1 kΩ verso massa; [B] modo H: 24 V e −16 V continui per 5 min senza danno; modo L: ingresso a +24 V e a −16 V per 5 min senza danno; [B] configurazioni errate (entrambi i jumper verso IN, oppure verso +12 V e GND) per 5 min senza danno; [B] corrente a ingresso attivo ≤ 1,5 mA con la board a 14,6 V.

**REQ-EL-008** (Must, Assumed) — Gli ingressi IN-CAB, IN-CEL (e IN-AUX1/2, vedi REQ-EL-009) *shall* sopravvivere senza danno, con ripristino automatico della lettura, ai transitori dell'impianto 12 V del veicolo:
- **load dump ISO 16750-2 Test A (non soppresso)**, sistema 12 V: U_s 79–101 V, R_i 0,5–4 Ω, t_d 40–400 ms;
- **ISO 7637-2 impulso 1**: U_s fino a −150 V, R_i 10 Ω, t_d 2 ms;
- **ISO 7637-2 impulso 2a**: U_s fino a +112 V, R_i 2 Ω, t_d 0,05 ms;
- **ISO 7637-2 impulsi 3a/3b** (burst ns): R_i 50 Ω, livelli da verificare.

*Rationale:* IN-CAB è sul +15 lato alternatore. Non è noto se l'X244 abbia una soppressione centralizzata del load dump: si assume il caso non soppresso (Test A). Su un ingresso di segnale ad alta impedenza costa poco.
*Fonti:* il testo delle norme non è stato consultato. Valori da application note dei costruttori, fonti secondarie: [MCC AN0005](https://solutions.mccsemi.com/news/application-note-quick-guide-on-automotive-load-dump-protection-iso-16750-2) e [TI SNOAAA1](https://ti.com/document-viewer/lit/html/SNOAAA1) (load dump); [TI SNOAA13](https://ti.com/lit/pdf/snoaa13) tab. 1, 2, 4 (R_i e t_d degli impulsi 1, 2a, 3a); [TI e2e, ISO 7637-2](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/iso_5F00_7637_5F00_2.pdf) (range di U_s).
*Acceptance:* [D] analisi per impulso: corrente e energia su ogni componente del percorso d'ingresso entro i limiti del datasheet (impulsivi per resistori e diodi). Nessun generatore ISO disponibile al banco.
*Rischio accettato (utente, 2026-10-08):* il resistore serie R1 è un **0805**. Nel load dump Test A (101 V, 400 ms) dissipa circa 1,1 W (174 mJ), 9 volte la potenza nominale standard di un CRCW0805 (0,125 W; il datasheet Vishay prova il sovraccarico a 2,5× per 5 s). La tenuta al load dump **non è dimostrabile** con un 0805; se si rompe il canale legge "inattivo". Gli altri impulsi (1, 2a, 3a/3b) vanno ancora verificati sulle curve di impulso del resistore (non lette). Il load dump potrebbe non arrivare al nodo se l'alternatore dell'X244 ha una soppressione integrata (non verificato).

**REQ-EL-007** (Should, Open) — Consumo a riposo: da definire. La board resta alimentata a camper fermo? (OPEN-08)

### 2.2 Interfaccia / protocollo

**REQ-IF-001** (Must, Confirmed) — IMU accelerometro + magnetometro su I²C, con driver **ESPHome nativo** (vincolo, Confirmed 2026-10-22). Precisione richiesta (Confirmed, utente 2026-10-22): **assetto (roll/pitch) ≤ 1°; heading del camper ≤ 5°**.
*Rationale:* assetto per il livellamento con i cunei; heading del camper dal magnetometro. Il magnetometro resta (decisione utente).
*Note (Assumed):* ±5° di heading in un veicolo con scocca in acciaio, batteria e carichi induttivi richiede calibrazione hard-iron/soft-iron a camper montato, compensazione dell'inclinazione con l'accelerometro e un magnetometro lontano da relè, motori e cavi di corrente (eventuale scheda satellite su I²C). Il componente ESPHome fornisce solo campo grezzo e heading semplice: calibrazione e compensazione sono a carico del firmware. MPU-6050 e HMC5883L esclusi per ciclo di vita (NRND / dismesso 2016; fonti deboli, distributori e forum).
*Posizione (Confirmed, utente 2026-10-22):* magnetometro **sulla scheda principale, in un angolo lontano dai relè**; vincoli di layout (distanze Assumed) nel foglio a7.
*Componenti (Congelati, utente 2026-10-22):* ST LSM6DSOX (IMU, U23; sostituisce l'LSM6DSO) e MEMSIC MMC5983MA (magnetometro); circuito Proposto in [`hardware/schematic/a7_imu_magnetometro.md`](../hardware/schematic/a7_imu_magnetometro.md).
*Acceptance:* [B] roll e pitch entro ±1° rispetto a un riferimento (livella digitale) su camper fermo; [B] heading entro ±5° rispetto a una bussola di riferimento dopo calibrazione, con carichi spenti e accesi.

**REQ-IF-002** (Must, Confirmed) — Ricevitore GPS su UART. Unità **esterna** su connettore a 4 poli passo 2,5 mm: 2 alimentazione + TX/RX (Confirmed, utente 2026-10-22). Da definire: serie del connettore, modello, tensione di alimentazione e livelli logici, baud rate e protocollo.




**REQ-IF-006** (Won't, Confirmed) — Interfaccia diagnostica motore **non sulla board**: delegata a uno slave futuro sul bus RS485 (REQ-IF-010). Nota per lo slave: sul 2.3 JTD 2005 la diagnosi risulta K-line KWP2000, non CAN ([Klavkarr](https://www.klavkarr.com/compatible/fiat-ducatoii-243/244/245/247-17000121), fonte commerciale; [fiatforum](https://www.fiatforum.com/threads/problems-with-obd2-data-on-x244.511426), forum).



**REQ-IF-010** (Must, Confirmed) — Il bus RS485 della board è **multi-drop ed estendibile** a slave futuri (es. slave diagnosi motore). Connettore con +12 V, GND, A, B per alimentare gli slave. Terminazione inseribile. Corrente massima erogabile agli slave da definire (OPEN-11).



**REQ-IF-012** (Should, Assumed) — Collegamento Ethernet 10/100 Base-T verso uno **switch già presente a bordo** (Confirmed, utente 2026-10-22), per l'integrazione con Home Assistant via ESPHome.
*Rationale (Confirmed, utente 2026-10-22):* eliminare i problemi di mancata connessione e le disconnessioni del Wi-Fi.
*Vincoli (Assumed):* nessun PoE (la board resta alimentata a 12–14,6 V, REQ-EL-001); un solo controller SPI esterno, perché l'ESP32-S3 non ha MAC Ethernet interno (da verificare sul datasheet); linee verso l'esterno con protezione ESD/surge e isolamento fornito dalla magnetica; il numero di GPIO assorbiti non deve costringere a togliere funzioni Must (conteggio pin da fare); assorbimento aggiunto compatibile con il budget del 3V3 e con OPEN-08.
*Strategia pin (Confirmed, utente 2026-10-22):* l'ESP32-S3-Tiny resta; i GPIO per il controller Ethernet si liberano spostando su **expander I²C** gli I/O digitali lenti (ingressi opto, relè, pilotaggio valvola/pistone, eccitazioni, LED/relè del remote inverter). Restano su GPIO nativi i segnali che un expander non può portare: SPI del controller Ethernet, UART (GPS, RS485), 1-Wire, SDA/SCL (*Assumed:* elenco da confermare con la mappa pin).
*Vincoli aggiunti dalla strategia (Assumed):* (a) all'avvio e al reset dell'ESP le uscite degli expander *shall* tornare a uno stato sicuro (valvola, pistone, relè fermi), con RESET degli expander collegato al reset dell'ESP o a un supervisore e pull-down passivi sui gate (REQ-SW-002); (b) **nessuna protezione hardware indipendente dal bus** sullo spegnimento del pistone (REQ-EL-004, 7 A / 200 ms) e della valvola: valvola e pistone hanno finecorsa/arresti meccanici e la soglia di 7 A protegge i componenti in un caso limite; il caso "bus I²C bloccato + finecorsa difettoso" è un doppio guasto, **rischio accettato (Confirmed, utente 2026-10-22)**. Protezione firmware: **RESET degli expander comandato da un GPIO nativo dell'ESP** (Assumed, vedi sotto);
*RESET degli expander (Assumed):* linea attiva bassa, **tenuta a livello di reset da un pull-down passivo** e rilasciata dal firmware a fine inizializzazione, così che durante reset/boot/watchdog dell'ESP gli expander siano fermi (uscite ad alta impedenza + pull-down sui gate, REQ-SW-002) e il firmware possa impulsare il reset come arresto d'emergenza o per sbloccare il bus. GPIO non di strappo. Da verificare sul datasheet dell'expander scelto: presenza del pin RESET, ripristino della macchina a stati I²C, larghezza minima dell'impulso e tempo di recupero, soglie V_IL/V_IH rispetto al GPIO dell'S3; (c) ~~expander su un bus I²C separato da quello dei sensori~~ **superato (utente 2026-10-23): bus I²C unico** per expander e sensori (IMU, magnetometro, INA219, 2× ADS1115), indirizzi senza conflitti, pull-up e velocità da dimensionare sulla capacità (a8 §2.4), blocco del bus gestito dal firmware con `EXP_RESET`; (d) tempo di risposta degli ingressi ≤ 100 ms (REQ-EL-006) con polling o interrupt.
*Da decidere (OPEN-16):* Wi-Fi mantenuto come fallback o disattivato; distanza e percorso del cavo verso lo switch; connettore RJ45 con magnetica integrata o discreta.
*Acceptance:* [B] il nodo si registra in HA via cavo con Wi-Fi disattivato e mantiene la sessione per 24 h senza disconnessioni; [B] stacco e riattacco del cavo: il nodo ricompare in HA entro 30 s senza reset (soglia Assumed); [B] consumo aggiunto a 12 V misurato e annotato; [D] i pin usati non entrano in conflitto con gli ingressi/uscite Must e con gli strapping dell'ESP32-S3.

### 2.3 Ambientali

**REQ-ENV-001** (Should, Assumed) — −10…+60 °C, vibrazione veicolare, condensa possibile (da FRD positioning board).

### 2.4 Software / firmware

**REQ-SW-001** (Must, Confirmed) — Integrazione con Home Assistant via ESPHome su **Waveshare ESP32-S3-Tiny** (stesso modulo della rev. 1). UART necessarie: GPS, RS485, eventuale inverter (se seriale) — rientrano nelle 3 UART dell'ESP32-S3.

**REQ-SW-002** (Must, Assumed) — Stato sicuro: al reset/brown-out valvola e pistone fermi, relè diseccitato, per sole reti passive (pull-down). Riuso del principio rev. 1.

## 3. Punti aperti

| ID | Domanda | Requisiti |
|---|---|---|
| ~~OPEN-01~~ | Chiuso 2026-10-05: diagnosi motore delegata a slave RS485 | IF-006 |
| ~~OPEN-03~~ | Chiuso: sender resistivo 0–190 Ω | IF-003 |
| OPEN-08 | Board sempre alimentata o con wake da 12 V cabina? Budget a riposo | EL-007 |
| ~~OPEN-09~~ | Chiuso: ESP32-S3-Tiny | SW-001 |
| ~~OPEN-10~~ | Chiuso 2026-10-22: assetto ≤ 1°, heading ≤ 5° | IF-001 |
| OPEN-11 | Corrente da erogare agli slave RS485 su +12 V | IF-010 |
| OPEN-12 | Uscita "stato cellula" della centralina: modello della centralina, tipo di uscita (high-side 12 V / open-collector / contatto), livelli a cellula ON e OFF | EL-006 |
| OPEN-16 | Ethernet: Wi-Fi mantenuto come fallback o disattivato? Distanza/percorso del cavo verso lo switch; RJ45 con magnetica integrata o discreta; mappa pin nativi/expander: **proposta in [`hardware/schematic/a8_mappa_pin.md`](../hardware/schematic/a8_mappa_pin.md)** (19 pin nativi su 19 dell'header, margine zero; 12 pad di scorta da verificare fisicamente; IO33–37 da leggere sul datasheet Espressif); famiglia e indirizzi degli expander (stato al reset, RESET, corrente per pin da datasheet); supporto ESPHome del controller scelto su ESP32-S3 (da verificare) | IF-012 |

| OPEN-17 | **[Nuovo 2026-10-26]** Con due PCB: quale scheda ospita l'ESP32-S3 e i bus I²C/RS485? Un MCU per scheda o uno solo con cavo fra le schede (I²C/RS485/CAN)? Dove vanno IMU, GPS, Ethernet, ingressi cabina/cellula, alimentazione (una catena o due)? Massa e alimentazione fra le schede | IF-012, EL-001 |

_I punti aperti specifici di scheda sono in `idraulica/frd.md` e `elettrica/frd.md`._

## 4. Registro assunzioni


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


## 7. Storico revisioni

| Data | Modifica | Motivo |
|---|---|---|
| 2026-10-05 | Prima bozza rev. 2; rev. 1 archiviata in `old/` | Ridefinizione obiettivi |
| 2026-10-05 | Inverter: segnali discreti (fonti forum), relè trasparente a riposo; shunt ±200 A, massa lato batteria | Risposte utente + ricerca |
| 2026-10-05 | Motore delegato a slave RS485; inverter, sender 0–190 Ω, shunt low-side, ESP32-S3-Tiny | Risposte utente |
| 2026-10-05 | EL-006 dettagliato (sorgenti, opto obbligatorio, ≤ 100 ms); nuovo EL-008 sui transitori degli ingressi; OPEN-12 | Avvio schematico, sezione ingressi digitali |
| 2026-10-08 | EL-006: opto PC817 → TLP293 GB; circuito ingressi semplificato (senza generatore di corrente), simulata anche la variante non GB | Richiesta utente |
| 2026-10-08 | EL-006: rimosso lo strobe; assorbimento IN-CEL a cellula attiva ≈ 1 mA accettato (era ≤ 0,1 mA Assumed) | Decisione utente |
| 2026-10-08 | EL-006: IN-CAB dalla radio, cavo 0,5 mm². EL-008: R1 in 0805, rischio load dump accettato. Topologia senza D1 in serie | Decisione utente |
| 2026-10-14 | EL-003/004: modelli valvola e pistone indicati, misura di corrente Confirmed. EL-005: 4 relè generici N.O.; nuovo OPEN-13 | Decisione utente |
| 2026-10-14 | OPEN-04 riformulato: nessun dato di corrente verificabile da fonti; serve misura sulle unità reali | Verifica datasheet-verifier |
| 2026-10-15 | Nuovo IF-011 (ingresso sonda grigie) e OPEN-14: nessuna specifica elettrica pubblicata da CBE, serve misura | Richiesta utente |
| 2026-10-15 | EL-004: soglia di lavoro massima 7 A (spegnimento firmware, 200 ms); interlock relè/MOSFET solo software; fusibile esterno | Decisione utente |
| 2026-10-15 | Nuovo EL-009: 2 ingressi opto di riserva IN-AUX1/2 configurabili con jumper a saldare (attivo a 12 V / attivo a massa); EL-008 esteso | Richiesta utente |
| 2026-10-15 | EL-009: schema IN-AUX1/2 disegnato sul foglio (designatori R29/R30, U6/U7, H1–H4); documentazione allineata, modo L non simulato | Richiesta utente |
| 2026-10-15 | IF-003/IF-004: interfaccia serbatoio chiare (a4); sensore temperatura = DS18B20 (OPEN-05 ridotto a scopo/cavo/VDD); nuovo OPEN-15 | Richiesta utente |
| 2026-10-15 | IF-004: VDD del DS18B20 diretto al 3V3, rischio di retroalimentazione accettato | Decisione utente |
| 2026-10-17 | IF-003: eccitazione del livello da partitore a generatore di corrente + offset Rb opzionale (a4 sez. A) | Decisione utente |
| 2026-10-17 | IF-003: dal generatore a diodi di base allo specchio PNP (deriva ±15 % → ±2 % simulata, `idraulica/sim/a4_livello`) | Esito della simulazione; approvato dall'utente |
| 2026-10-17 | IF-003: coppia PNP DMMT3906W e GPIO ESP32-S3 verificati su datasheet letti direttamente (a4, components.md) | Verifica componenti |
| 2026-10-17 | IF-003: dallo specchio PNP alla misura ratiometrica con INA219 (R_exc 300 Ω, Rsh 3,9 Ω); ADC1 libero; rete di clamp eliminata (scostamento da confermare) | Decisione utente |
| 2026-10-17 | IF-003: accettata l'assenza della rete di clamp sul nodo del livello (tenuta a 24 V per il rating INA219) | Decisione utente |
| 2026-10-18 | IF-007: LED del remote proxati dalla board (relè K_LED + opto), comando +12 V/VIN invariato; spec in a6 | Decisione utente |
| 2026-10-17 | IF-007: piedinatura RJ45 dal costruttore Renogy (3 = +12 V, 5 = VIN, 4 = verde, 7 = rosso, 2 = GND); OPEN-02 riaperto con le sole misure residue; spec in a6 | Dato del costruttore (Assumed) |
| 2026-10-18 | IF-007: lettura di +12 V, LED e interruttore remote con TLP293; LED del remote alimentati dalla 3V3 della board con presa in carico a relè (3 IM06) | Decisione utente |
| 2026-10-18 | EL-001: minimo operativo 10 V → 12 V (resta Assumed). Verificare le sezioni che usano 10 V (opto EL-006, regolatori, valvola/pistone OPEN-04, caratteristiche del regolatore) | Decisione utente |
| 2026-10-22 | IF-001: schema U22 (MMC5983MA, C16/C17/C20) letto sull'immagine: conforme alla specifica a7; C16 100 nF invece di 1 µF accettato | Revisione schema |
| 2026-10-22 | IF-001: IMU LSM6DSO → LSM6DSOX (U23), stessi dati sul datasheet DS12814; nello schema SA0 (pin 1) risulta scollegato, da collegare a GND; LCSC e `datasheet-verifier` da fare | Decisione utente |
| 2026-10-22 | IF-001: magnetometro sulla scheda principale in un angolo lontano dai relè; vincoli di layout nel foglio a7 (distanze Assumed) | Decisione utente |
| 2026-10-22 | IF-001: congelati LSM6DSO (IMU) e MMC5983MA (magnetometro), datasheet letti sui PDF; foglio a7 scritto come specifica (EasyEDA non raggiungibile); aperti: posizione del magnetometro, rampa 3V3, pull-up e capacità del bus | Decisione utente; verifica componenti |
| 2026-10-22 | IF-001: precisione assetto ≤ 1° e heading ≤ 5°, driver ESPHome nativo obbligatorio, magnetometro mantenuto; OPEN-10 chiuso. IF-002: GPS esterno su connettore 4 poli 2,5 mm | Decisione utente |
| 2026-10-22 | Nuovo IF-012 (Ethernet verso switch a bordo, Should, Assumed) e OPEN-16; motivo: evitare disconnessioni Wi-Fi. Nessun componente scelto | Richiesta utente |
| 2026-10-22 | Mappa pin nativi/expander (a8): 19 nativi + 21 linee su expander (2×16 bit); LED di bordo del Tiny su IO38 (non IO14) secondo lo schematico Waveshare | Richiesta utente; pinout dal costruttore |
| 2026-10-22 | IF-012: rilassato il vincolo di arresto motori indipendente dal bus (doppio guasto accettato, finecorsa/arresti meccanici); RESET expander con pull-down e rilascio da firmware come protezione | Decisione utente |
| 2026-10-22 | IF-012: pin liberati spostando gli I/O digitali lenti su expander I²C (S3-Tiny resta); aggiunti vincoli di stato sicuro al reset, ENA pistone indipendente dal bus, bus I²C separato | Decisione utente |
| 2026-10-23 | a8: ingressi analogici `IN_VALVE_SENSE`, `IN_PISTON_SENSE`, `GRY_SNS` su secondo ADS1115 (0x49) sul bus sensori; liberati IO1, IO2, IO4. Rischio accettato: blocco del bus sensori = nessuna misura di corrente su valvola/pistone (EL-003, EL-004) | Decisione utente |
| 2026-10-23 | IF-012 (c): bus I²C unico per expander e sensori, rischio accettato; verifica in a8 §2.4: pull-up 2,2 kΩ (non 4,7 kΩ), 100 kHz iniziali, arresto/recupero via `EXP_RESET` | Decisione utente |
| 2026-10-26 | Progetto diviso in due PCB: idraulica (chiare, grigie, pompa, motori) ed elettrica (shunt, inverter, relè globale). Requisiti, componenti, schemi e simulazioni spostati in `idraulica/` ed `elettrica/`; il comune resta in `docs/` e `hardware/`. Nuovi: pompa (NEW-1), relè globale (NEW-2), OPEN-17 | Decisione utente |
