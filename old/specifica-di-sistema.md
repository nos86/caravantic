# Caravantic IO-Board — Specifica di Sistema e Requisiti Funzionali

Status: Draft — rev. A
Ultimo aggiornamento: 2026-07-28

## 1. Contesto e scopo

La Caravantic IO-Board è una scheda di interfaccia tra la domotica governata da Home Assistant e l'impianto elettrico tradizionale di un camper di metà anni 2000 (batteria servizi 12 V, utenze a relè, sensori analogici/digitali).

Il sistema è una **rete multi-nodo di schede identiche** collegate via CAN-Bus a 125 kbit/s; un nodo assume il ruolo di **bridge** verso Home Assistant via WiFi. Ogni scheda espone 5 ingressi configurabili per depopolazione, 4 uscite configurabili per depopolazione, una sezione motori (1 stepper + 2 servo) e un connettore di espansione I²C.

**Fuori scopo** in questa revisione:

- Certificazioni formali (CE/E-mark), gestione della batteria e della ricarica, integrazione con bus proprietari del camper (CBE/CI-BUS).
- Progetto di dettaglio del contenitore, di cui questo documento fissa la sola interfaccia meccanica e il materiale (REQ-MECH-001).
- Protocollo di dettaglio dell'aggiornamento firmware e contenuto funzionale dell'HMI web, rimandati a una **specifica firmware/HMI separata** da redigere dopo la realizzazione dell'hardware (REQ-DIAG-002, REQ-SW-002).
- Layout e routing del PCB, oggetto dei documenti implementativi in `hardware/schematics/`.

## 2. Architettura di sistema

```
                    ┌─ Buck 3.3V always-on ─── MCU (ESP32-S3-Tiny) + transceiver CAN
Batteria servizi ──┤
  12V (9–16V)      ├─ Load-switch ─── rail periferiche (opto ingressi, sense, eccitazione NTC)
      │            └─ Load-switch ─── Buck 5V motori (stepper + 2 servo)
      │
   [PTC] [Prot. inversione P-MOSFET] [Clamp TVS] [Filtro EMI, footprint depopolati]
      │
   [Power-latch] ←── WAKEUP (opto-isolato)      power-hold ──→ GPIO MCU

CAN-H/L ──[Transceiver standby + bus wake-up]── MCU        I²C ──┬── I/O expander (LED, EN load-switch)
                                                                  └── Connettore di espansione
```

**Stati di alimentazione.** *OFF*: power-latch aperto, nessun rail attivo, assorbono solo i componenti di protezione di ingresso. *Deep-sleep*: MCU e transceiver alimentati, tutto il resto sezionato dai load-switch, risveglio da WAKEUP o da attività sul bus CAN. *Running*: rail abilitati secondo necessità.

**Carichi esterni.** Le 4 uscite commutano carichi con **alimentazione propria**: la board fornisce solo il contatto, il ritorno non transita per la sua massa.

## 3. Requisiti

Formato: **REQ-[CAT]-[NNN]** — Categoria, Priorità MoSCoW, Status (Confirmed = deciso; Assumed = ipotesi tracciata in §6).

**Convenzione BOM resistori:** **0805** di default per tutte le resistenze (pull-up, serie, partitori, limitazione LED). **1206** ammesso solo dove il dimensionamento di potenza lo richiede, previa verifica P=I²R contro il rating del package. Eccezione candidata: lo shunt di sense corrente motori (REQ-IF-011), che al picco di 2,5 A su 33 mΩ dissipa ~0,21 W, oltre il rating tipico di un 0805 generico (~0,1–0,125 W).

**Convenzione di verifica (decisione utente):** il progetto non è certificato né safety-critical (§1) e non dispone di laboratorio di qualifica, quindi **nessuna acceptance richiede prove di qualifica di laboratorio** — camere climatiche, endurance a decine di migliaia di cicli, generatori di transitori normalizzati, banchi ESD. Ogni acceptance è marcata con il proprio livello di verifica:

- **[B] Verificato in banco** — misurabile con alimentatore, multimetro, oscilloscopio, analizzatore logico o CAN, carico elettronico o resistivo. È l'unico livello che comporta una prova fisica.
- **[D] Derivato da datasheet** — soddisfacimento dimostrato per selezione del componente, confrontando il rating dichiarato dal costruttore con la sollecitazione attesa e annotando il margine in BOM. Nessuna prova fisica.

Dove la verifica fisica non è realisticamente possibile il requisito shall essere marcato [D], spostando la responsabilità sulla selezione del componente: un'acceptance non eseguibile dà una falsa sensazione di copertura.

### 3.0 Indice dei requisiti

Sintesi di una riga per requisito, per individuare rapidamente quello di interesse.

| REQ | Pri. / Status | Sintesi |
|---|---|---|
| **EL-001** | Must / Confirmed | Alimentazione da batteria servizi 12 V, range 9–16 VDC; supporto obbligatorio di entrambe le chimiche, LiFePO4 4S e piombo-acido, senza BOM alternative. |
| **EL-002** | Must / Confirmed | Protezione da inversione di polarità (−16 V continui) sul solo ingresso di alimentazione della board, non sui carichi esterni. |
| **EL-003** | Must / Confirmed | Immunità ai transitori veicolari brevi ISO 7637-2 (pulse 1, 2a, 3a/3b); il load dump pulse 5 è escluso dal design basis. |
| **EL-004** | Must / Confirmed | Load-switch hardware sulle sezioni energivore non governabili da GPIO; i LED sono esclusi perché si spengono dal pin che li pilota. |
| **EL-005** | Must / Confirmed | In OFF assorbono solo i componenti di protezione di ingresso, da minimizzare; in deep-sleep, con MCU e transceiver alimentati, ≤ 1 mA. |
| **EL-006** | Must / Confirmed | WAKEUP accende la scheda e ne richiede lo spegnimento totale, eseguito dal micro a fine sequenza; dallo stato OFF non c'è wake via CAN. |
| **EL-007** | Must / Confirmed | Rail 5 V motori indipendente e sezionabile, ≥ 2,5 A di picco, dimensionato assumendo che i due servo non si muovano mai simultaneamente. |
| **EL-009** | Must / Confirmed | Separazione massa potenza/segnale con star ground e distribuzione dedicata del positivo commutato verso i MOSFET high-side. |
| **EL-010** | Must / Confirmed | Immunità ai transitori locali da BMS LFP e inverter sulla bus-bar condivisa: catena di ingresso ≥ 40 V, clamp classe 20–24 V più impedenza serie. |
| **IF-001** | Must / Confirmed | CAN 2.0 a 125 kbit/s in rete multi-nodo di schede identiche, con terminazione 120 Ω inseribile. |
| **IF-002** | Must / Confirmed | Transceiver CAN con standby a basso assorbimento e wake-up da attività bus, interfacciabile a logica 3,3 V. |
| **IF-003** | Should / Confirmed | Il nodo bridge espone WiFi verso Home Assistant, mentre gli altri nodi tengono la radio spenta. |
| **IF-004** | Must / Confirmed | 5 ingressi per depopolazione: contatto secco 3,3 V, opto-isolato 12 V con soglie 8/2 V, analogico in tensione, o resistivo con eccitazione a bordo per NTC. |
| **IF-005** | Must / Confirmed | Filtro anti-rimbalzo su ogni ingresso: RC hardware da 1 ms più debounce firmware configurabile tra 10 e 100 ms. |
| **IF-006** | Must / Confirmed | Protezione da sovratensione uniforme su tutte e tre le varianti di ingresso: sopravvivenza a 24 V continui di fault e a ISO 7637-2 pulse 3. |
| **IF-007** | Must / Confirmed | Ingresso WAKEUP opto-isolato, attivo a livello batteria 12 V, integrato nella logica di power management. |
| **IF-008** | Must / Confirmed | 4 uscite per depopolazione: MOSFET high-side **2 A** con PWM a 1,5–2 kHz (riserva di incremento condizionata al piano di rame, vedi §3.2) oppure relè **2 A**; carichi alimentati esternamente. Correnti superiori o motori DC: **relè esterno** comandato da un'uscita della scheda. |
| **IF-009** | Must / Confirmed | L'inversione di motori DC è demandata a **relè esterni** con cablaggio di inversione dei contatti (requisito di installazione). Per comandi mutuamente esclusivi non di inversione: cascata NC1→COM2, con limiti dichiarati. |
| **IF-010** | Must / Confirmed | Pilotaggio di 1 stepper (28BYJ-48 modificato bipolare o NEMA17) e 2 servo RC con un unico driver TMC2209. |
| **IF-011** | Must / Confirmed | Limit-switch virtuali: StallGuard4 sullo stepper e un unico INA180 con shunt sul rail 5 V motori, instradato su ADC1. |
| **IF-012** | Must / Confirmed | Bus I²C 3,3 V su JST PH 2,0 mm a 4 pin con ordine Qwiic-like (GND, VCC, SDA, SCL), pull-up disinseribili e protezione ESD. |
| **IF-013** | Must / Confirmed | Due LED di stato CANopen conformi a CiA 303-3 (RUN verde, ERR rosso), pilotati tramite l'I/O expander di REQ-IF-015. |
| **IF-014** | Must / Confirmed | Linee CAN protette a ±8 kV ESD e ±58 V di guasto per selezione del transceiver; choke e array esterni solo come footprint depopolati. |
| **IF-015** | Must / Confirmed | I/O expander I²C a 8 bit push-pull per LED ed enable dei load-switch, necessario per far quadrare il bilancio dei GPIO. |
| **IF-016** | Must / Confirmed | Footprint depopolati per filtro EMI di ingresso (LC/pi e choke di modo comune), da popolare solo se la misura sul veicolo lo richiede. |
| **TIM-001** | Should / Confirmed | Round-trip di comando misurato sul bus CAN (comando → attuazione → conferma) ≤ 250 ms; evento ingresso → frame pubblicato ≤ debounce + 50 ms. |
| **MECH-001** | Must / Confirmed | PCB entro 100 × 100 mm, quattro fori M3 agli angoli e angoli smussati, montato su contenitore custom stampato in 3D in PETG. |
| **MECH-002** | Must / Confirmed | Keep-out di antenna del modulo ESP32-S3-Tiny sulla scheda portante, con modulo posizionato a filo del bordo. |
| **MECH-003** | Must / Confirmed | Morsettiere a vite sui bordi (5,08 mm per alimentazione e uscite, 2,54 mm per CAN e ingressi) e JST XH in parallelo sugli ingressi. |
| **ENV-001** | Must / Confirmed | Funzionamento tra 0 e +40 °C, umidità fino all'85% senza condensa; range di sopravvivenza non fissato, discende dai componenti e va documentato in BOM. |
| **SAFE-001** | Must / Confirmed | Fusibile resettabile PTC sulla sola alimentazione board; protezione dei carichi esterni demandata al quadro fusibili del camper. |
| **SAFE-002** | Must / Confirmed | Esclusione reciproca delle coppie di inversione garantita in hardware dal cablaggio dei contatti dei relè esterni, non dal solo firmware. |
| **SAFE-003** | Must / Confirmed | Tutte le uscite disattivate al power-on, in brown-out e dopo reset da watchdog, garantito passivamente da reti di polarizzazione esterne. |
| **SW-001** | Must / Confirmed | Gestione low-power in running, sequenza ordinata di shut-down ed esclusione mutua nel movimento dei due servo, con accodamento delle richieste. |
| **SW-002** | Should / Confirmed | Interfaccia macchina documentata su rete o USB per configurazione e telemetria; il frontend Vue può essere ospitato dalla board o esternamente. |
| **SW-003** | Must / Confirmed | Protocollo applicativo CANopen (CiA 301) tramite libreria CANopenNode: gestione NMT, Heartbeat, PDO e SDO. |
| **SW-004** | Must / Confirmed | Node-ID assegnato dinamicamente via LSS (CiA 305) usando il MAC di fabbrica; nessun DIP-switch né jumper. |
| **SW-005** | Must / Confirmed | Watchdog hardware con uscite in stato sicuro al reset, e configurazione del nodo persistente in memoria non volatile. |
| **LIFE-001** | Must / Confirmed | Lotto di massimo 20 pezzi, assemblaggio in-house con posizionamento manuale e reflow, popolamento on-demand; costo come criterio vincolante di selezione. |
| **DIAG-001** | Should / Confirmed | LED di stato, test point sui rail e telemetria CAN di correnti motori, stato degli I/O e causa dell'ultimo reset o wake. |
| **DIAG-002** | Must / Confirmed | Aggiornamento firmware su tre canali: USB cablato, OTA su CANopen verso qualsiasi nodo e OTA su WiFi sul solo bridge. |

**Ricerca per argomento**

- *Alimentazione, transitori, protezioni di ingresso* → EL-001, EL-002, EL-003, EL-010, SAFE-001
- *Consumi, sleep, accensione e spegnimento* → EL-004, EL-005, EL-006, IF-002, IF-007, SW-001
- *Ingressi da campo* → IF-004, IF-005, IF-006, DIAG-001 (nota ADC)
- *Alimentazione dei rail e I/O expander* → EL-004, IF-012, IF-015
- *Uscite di potenza e dimming LED* → IF-008, IF-009, EL-009, SAFE-001, SAFE-002, SAFE-003
- *Motori, servo e finecorsa virtuali* → EL-007, IF-010, IF-011
- *Rete CAN e protocollo* → IF-001, IF-002, IF-013, IF-014, SW-003, SW-004
- *Firmware, configurazione e HMI* → SW-001, SW-002, SW-005, DIAG-002
- *Meccanica, connettori e ambiente* → MECH-001, MECH-002, MECH-003, ENV-001, IF-012
- *Diagnostica e telemetria* → DIAG-001, DIAG-002, IF-011, IF-013, IF-015

### 3.1 Elettrica / Power Supply

**REQ-EL-001** (Electrical, Must, Confirmed)

- **Statement:** la scheda shall essere alimentata dalla batteria servizi 12 V, con range operativo continuo **10–16 VDC**. Entrambe le chimiche sono **nel perimetro obbligatorio**, senza BOM alternative: **LiFePO4 12 V** (4S, range 10,0–14,6 V, nominale 12,8 V) e **piombo-acido** (~11,8 V scarica, ~14,4 V in carica).
- **Revisione del limite inferiore (decisione utente, 2026-08-01):** il precedente estremo di 9 V, dettato dal piombo profondamente scarico, è stato rialzato a **10 V**: a 9 V la batteria servizi è da considerarsi esausta e la funzionalità del camper è già compromessa, quindi garantire la piena operatività lì non ha valore d'uso. Il nuovo limite coincide con il floor LFP (10,0 V) dell'impianto di riferimento. Tra 9 e 10 V non è richiesta la funzionalità ma la sola **assenza di danno e il ripristino autonomo** al rientro nel range. Questa revisione rimuove il punto critico di pick-up delle bobine relè sotto i 10 V.
- **Rationale:** decisione utente: l'impianto di riferimento è LFP e il retrofit LFP è ormai lo standard sui camper, quindi il supporto non può essere un'opzione BOM. Il range 9–16 V è l'inviluppo delle due chimiche e non cambia: il limite inferiore resta dettato dal piombo scarico, quello superiore dalla carica/equalizzazione al piombo, entrambi più larghi delle soglie LFP. Il supporto LFP non costa quindi nulla in termini di range, ma **rende obbligatorio** REQ-EL-010, che tratta lo sgancio del BMS: su un impianto al piombo quel transitorio non esisterebbe.
- **Acceptance:** piena funzionalità a 10,0 V e 16,0 V; tra 9,0 e 10,0 V nessun danno e ripristino autonomo al rientro nel range; nessun danno a 18 V per 60 s. La stessa scheda, senza modifiche di BOM, opera sia a 10,0–14,6 V (LFP) sia a 11,8–14,4 V (piombo).

**REQ-EL-002** (Electrical, Must, Confirmed)

- **Statement:** l'ingresso di alimentazione **della board** (rail logico MCU/CAN/driver, non i circuiti di carico esterni) shall sopravvivere all'inversione di polarità (−16 V continuativi) senza danni.
- **Rationale:** errore di cablaggio plausibile in un impianto camper fai-da-te.
- **Acceptance:** applicazione di −16 V per 5 min; al ripristino la scheda è pienamente funzionante.
- **Implementazione proposta:** P-MOSFET in configurazione ideal-diode sul ramo positivo (per correnti > 2 A raccomandato rispetto al diodo Schottky, §7).
- **Ambito:** la protezione copre solo l'alimentazione della board. Le alimentazioni esterne dei carichi pilotati (REQ-IF-008) non transitano per questo stadio e restano fuori dal perimetro di protezione della scheda.

**REQ-EL-003** (Electrical, Must, Confirmed)

- **Statement:** l'ingresso di alimentazione shall tollerare i transitori **a breve durata** tipici del bus 12 V veicolare — ISO 7637-2 **pulse 1, 2a, 3a e 3b**, tutti di durata compresa fra le decine di nanosecondi e pochi millisecondi — mediante clamp TVS e filtro di ingresso.
- **Rationale:** la scheda è connessa direttamente alla batteria servizi; con alternatore e caricabatterie i transitori esistono, anche se meno severi che sul bus motore. Fonti: app note Littelfuse e Analog Devices (§7).
- **Acceptance [D]:** il clamp selezionato per REQ-EL-010 shall risultare capace dell'energia dei pulse 1, 2a, 3a e 3b, verificata confrontando ampiezza, durata e resistenza interna di generatore previste dallo standard per ciascun pulse con la curva di potenza di picco del datasheet del TVS, e annotando il margine in BOM. La generazione fisica dei pulse richiederebbe un generatore normalizzato ISO 7637-2, fuori dal perimetro di verifica del progetto.
- **Esclusione dal design basis — load dump, ISO 7637-2 pulse 5a/5b (decisione utente):** il load dump, di durata pari a centinaia di millisecondi, **non** rientra in questo requisito. Motivazione: la board è alimentata dalla batteria **servizi**, non dal bus alternatore, e una batteria permanentemente connessa agisce già da clamp di primo livello sull'evento. Lo standard consente esplicitamente l'omissione dei pulse non pertinenti alla connessione del dispositivo — *"some pulses may be omitted if a device, depending on its function or its connection, is not influenced by comparable transients in the vehicle"* (ISO 7637-2:2004, §4.1, §7). Lo scenario di sovratensione effettivamente osservato sull'impianto reale, cioè lo sgancio del BMS, resta coperto da REQ-EL-010.
- **Rischio residuo dichiarato:** un evento di load dump che si propaghi dal bus motore al bus servizi attraverso il DC-DC di ricarica da alternatore non è coperto. La mitigazione è delegata alle caratteristiche di uscita di quel convertitore, da verificare sul suo datasheet in fase di installazione; la board non la garantisce.
- **Nota:** il vincolo dominante sul dimensionamento del clamp resta REQ-EL-010 (V_RWM 20–24 V, V_C sotto il rating di 40 V della catena di ingresso), con cui questo requisito va congelato contestualmente.

**REQ-EL-004** (Electrical, Must, Confirmed)

- **Statement:** tutte le sezioni energivore il cui assorbimento **non è governabile da un GPIO** (rail motori 5 V, bobine relè, opto di ingresso lato scheda, sensori di corrente) shall essere disalimentabili in hardware tramite load-switch comandati dal micro.
- **Rationale:** requisito utente — il risparmio energetico non deve dipendere solo dal firmware per i carichi che consumano indipendentemente dallo stato dei pin. I **LED sono esclusi** da questo requisito (decisione utente): essendo pilotati direttamente da GPIO attraverso la propria resistenza di limitazione, si spengono azzerando il pin e non richiedono un load-switch dedicato — che sarebbe un componente e un GPIO di comando in più a parità di risultato.
- **Acceptance:** con tutti i load-switch aperti e MCU in deep-sleep, l'assorbimento totale a 12,8 V rispetta REQ-EL-005.
- **Nota sui LED:** i LED sono pilotati dall'I/O expander di REQ-IF-015. Il loro spegnimento in deep-sleep e in OFF **shall** essere garantito passivamente dalla polarità di pilotaggio, senza intervento firmware attivo: un LED acceso per errore assorbe qualche mA e da solo sfonderebbe il budget di REQ-EL-005.

**REQ-EL-005** (Electrical, Must, Confirmed)

- **Statement:** la scheda shall prevedere due stati a basso consumo distinti, misurati a 12,8 V:
  - **OFF (spegnimento totale)**, power-latch aperto, nessun rail alimentato. In questo stato le uniche correnti assorbite **shall essere quelle dei soli componenti di protezione a monte del regolatore** — leakage del clamp TVS, del MOSFET di protezione da inversione e del PTC, più il quiescente del latch — e **shall essere minimizzate come criterio di selezione** di quei componenti. Nessun altro circuito shall restare connesso al positivo di batteria. Non è fissato un valore di soglia: il consumo in OFF è la somma dei leakage dichiarati a datasheet dei componenti scelti, e come tale va calcolato e annotato in BOM. È lo stato in cui la board entra su richiesta di shut-down da WAKEUP (REQ-EL-006).
  - **Deep-sleep**, MCU e transceiver CAN alimentati sul rail always-on, tutti i load-switch aperti: assorbimento **≤ 1 mA**.
- **Rationale (deep-sleep):** budget di 1 mA per nodo fissato dall'utente sulla base di un impianto da **300 Ah** e di una rete fino a **10 nodi**. Verifica del bilancio: 10 nodi × 1 mA = 10 mA, cioè ~0,24 Ah/giorno e **~7,2 Ah/mese**, pari al **2,4% al mese** di una batteria da 300 Ah. È lo stesso ordine di grandezza delle perdite proprie della batteria — autoscarica chimica LFP 1–3%/mese e quiescente del BMS tipicamente di alcuni mA (§7) — quindi la rete di nodi non diventa il contributo dominante al drain di rimessaggio. Su quattro mesi di sosta invernale senza carica il contributo delle board è di ~29 Ah, circa il 10% della capacità. **Rationale (OFF):** in questo stato i regolatori sono disabilitati e non esiste un carico attivo, quindi non ha senso fissare una soglia arbitraria: il consumo è interamente determinato dai leakage dei componenti di protezione, e il requisito utile è che siano gli **unici** presenti e che la loro somma sia minimizzata in fase di selezione. È lo stato che pesa sul rimessaggio lungo.
- **Acceptance:** **[B]** misura con amperometro in serie a 12,8 V nei due stati — (a) board in OFF dopo sequenza di shut-down completata, con il valore misurato coerente con la somma dei leakage attesi; (b) board in deep-sleep con MCU e transceiver alimentati e tutti i load-switch aperti, entro 1 mA. **[D]** somma dei leakage dichiarati dei componenti di protezione di ingresso calcolata e annotata in BOM; ispezione dello schematico che conferma l'assenza di altri rami permanentemente connessi al positivo.
- **Conseguenza dichiarata:** con un budget di 1 mA la scelta del regolatore always-on non è più vincolata a Iq < 100 µA, il che apre la selezione a famiglie molto più ampie ed economiche. Il vincolo di consumo cessa anche di essere un argomento discriminante nella scelta dell'MCU (vedi §4.1).
- **Circuiti parassiti del modulo MCU (decisione utente):** nello stato **OFF** il power-latch toglie alimentazione anche al modulo, quindi il suo regolatore di bordo e il LED RGB su GPIO 14 non contribuiscono al consumo di rimessaggio — è il caso che conta sul bilancio a lungo termine, ed è coperto per architettura. Resta da verificare il solo stato di **deep-sleep**, in cui il modulo è alimentato: un LED RGB indirizzabile assorbe corrente anche a colore spento e da solo può impegnare una quota rilevante del budget di 1 mA. Se la misura lo confermasse, la mitigazione è dissaldare il LED dal modulo, senza altre conseguenze di progetto.

**REQ-EL-006** (Electrical, Must, Confirmed)

- **Statement:** il segnale WAKEUP (opto-isolato, REQ-IF-007) shall (a) accendere la scheda dallo stato OFF e (b) richiedere lo **spegnimento totale** della board, non un semplice ritorno in deep-sleep. Lo shut-off effettivo shall essere eseguito dal micro al termine della propria sequenza di spegnimento (parcheggio motori, flush dello stato, notifica CAN), rilasciando il power-hold e aprendo il power-latch.
- **Rationale:** decisione utente: WAKEUP governa l'alimentazione della board, non un livello di sleep intermedio. Uno spegnimento hardware brutale lascerebbe gli attuatori in stato indefinito, quindi il taglio dell'alimentazione resta subordinato al completamento della sequenza firmware.
- **Architettura di alimentazione (Confirmed):** i due meccanismi coesistono e non sono alternativi.
  - **Power-latch hardware** comandato da WAKEUP, con GPIO di *power-hold* asserito dal micro al boot: definisce la transizione OFF ↔ acceso, e in OFF nessun rail è alimentato.
  - **Rail always-on a valle del latch** che alimenta **MCU e transceiver CAN**: consente il deep-sleep con wake da GPIO RTC e da attività sul bus CAN (REQ-IF-002), mentre tutto il resto resta sezionato dai load-switch di REQ-EL-004.
- **Acceptance:** (a) fronte su WAKEUP con scheda in OFF → scheda operativa; (b) richiesta di shut-down → il micro completa la sequenza e solo dopo rilascia il power-latch, portando la board in OFF secondo il budget di REQ-EL-005; la rimozione della richiesta durante la sequenza è gestita senza stati inconsistenti; (c) in deep-sleep un frame CAN risveglia il nodo senza intervento di WAKEUP.
- **Limitazione dichiarata:** dallo stato **OFF il risveglio via CAN non è possibile**, perché il transceiver non è alimentato. Un nodo spento può essere riacceso solo dal segnale WAKEUP hardware. Questo va tenuto presente nella progettazione della rete: lo spegnimento totale di un nodo lo rende irraggiungibile da Home Assistant fino a un comando WAKEUP cablato.

**REQ-EL-007** (Electrical, Must, Confirmed)

- **Statement:** la sezione motori shall avere alimentazione indipendente — rail 5 V dedicato da buck separato, sezionabile in hardware (REQ-EL-004), dimensionato per **≥ 2,5 A di picco**. Il dimensionamento presuppone il **vincolo di non contemporaneità** dei due servo (REQ-SW-001): mai più di un servo in movimento alla volta.
- **Rationale:** decisione utente: rinunciando al movimento simultaneo dei due servo, il caso peggiore si dimezza e il buck può essere sensibilmente più piccolo ed economico, coerentemente con REQ-LIFE-001. I picchi dei servo non devono comunque causare brown-out di MCU e transceiver CAN.
- **Budget di picco (worst case con vincolo di esclusività):** 1× MG90S in stallo (~1,5 A) + 1× servo fermo in tenuta di posizione (≤ 300 mA, Assumed) + 28BYJ-48 modificato (~200 mA, cioè 2 fasi a 100 mA limitate via TMC2209) ⇒ ~2,0 A, più margine ⇒ **≥ 2,5 A**. I servo candidati SG90 (stallo ~500–700 mA) e MG90S (fino a ~1,5 A) sono meccanicamente ed elettricamente intercambiabili (stesso footprint, stesso pinout, stesso range 4,8–6 V), quindi si dimensiona sul caso peggiore MG90S senza BOM alternative. I dati di corrente provengono da fonti divulgative su cloni generici, non da datasheet ufficiali: il valore è congelato per decisione utente, ma una misura di verifica sui pezzi acquistati resta consigliata prima dell'ordine dei componenti di potenza.
- **Acceptance:** transitorio di stallo di un singolo servo simulato con carico elettronico, con il secondo servo in tenuta e lo stepper in movimento — nessun reset MCU, ripple sul rail 3,3 V < 100 mV.
- **Nota di progetto:** il picco di stallo è breve e va assorbito prevalentemente dal **condensatore di bulk** sul rail 5 V, non erogato in continuo dal buck. Dimensionare la capacità di bulk permette di restare su un regolatore da 2,5 A anziché sovradimensionarlo sul transitorio — è la voce che rende il budget realistico a basso costo.

**REQ-EL-009** (Electrical, Must, Confirmed)

- **Statement:** la massa di potenza (ritorno delle bobine relè e, residualmente, delle uscite MOSFET) shall essere separata fisicamente dalla massa di segnale (logica MCU, CAN, ADC) e ricongiunta in un unico punto (star ground) in prossimità dell'ingresso di alimentazione. Analogamente, la distribuzione del **positivo commutato** verso i MOSFET high-side shall essere su traccia o piano dedicato e disaccoppiata dal rail 3,3 V logico.
- **Rationale:** con i MOSFET **high-side** (REQ-IF-008) il ritorno del carico non transita più per la massa della board, il che riduce il ground-bounce rispetto alla soluzione low-side. Resta però un percorso di rumore residuo: il dI/dt del PWM si manifesta ora sul **ramo positivo**, condiviso con l'ingresso di potenza della board, e senza disaccoppiamento adeguato può iniettare ripple sul bus dei regolatori. Le bobine dei relè, pilotate low-side, restituiscono comunque la propria corrente (decine-centinaia di mA) sulla massa scheda, quindi la separazione star-ground resta necessaria. Pratica di layout consolidata su schede miste potenza/segnale (app note TI, §7).
- **Acceptance:** con tutte le uscite MOSFET commutate a pieno carico in PWM, il rumore su rail 3,3 V, riferimento ADC e livelli CAN resta entro le tolleranze dei componenti scelti (soglia numerica da congelare in schematico); verifica analoga sulla massa di segnale con le bobine relè commutate.
- **Nota:** il beneficio di rumore atteso dal passaggio a high-side è teorico e va confermato in fase di layout e misura. Il connettore (REQ-MECH-001) deve prevedere terminali distinti per massa di potenza e massa di segnale.

**REQ-EL-010** (Electrical, Must, Confirmed)

- **Statement:** l'ingresso di alimentazione shall tollerare, oltre ai transitori di REQ-EL-003, i transitori locali generati sulla bus-bar di potenza condivisa da batteria LFP 4S, inverter (fino a 2000 W) ed eventuali sorgenti di carica (MPPT/DC-DC), in particolare la sovratensione da apertura del BMS durante una sessione di carica attiva. Tutti i componenti della catena di ingresso — MOSFET di protezione da inversione, clamp TVS, buck 3,3 V e buck 5 V motori — shall avere **rating di tensione ≥ 40 V**; il buck shall avere inoltre range di regolazione qualificato per almeno 9–18 V. Il clamp di ingresso shall avere V_RWM sufficiente a non condurre a 16 V continui né sullo spike documentato (~17,2 V), e V_C alla corrente di picco attesa **inferiore** al rating assoluto del buck — classe indicativa V_RWM 20–24 V, da congelare in schematico.
- **Rationale:** caso reale documentato di spike ~17,2 V su impianto inverter + LFP all'apertura del BMS (fonte aneddotica da forum, §7), combinato con la topologia dichiarata dall'utente (batteria al centro della bus-bar, inverter a destra, board e altre utenze a sinistra) e con l'assenza di soppressione centralizzata. Con l'LFP obbligatorio (REQ-EL-001) lo sgancio del BMS è uno scenario del design basis nominale, non di una variante. La coppia clamp/buck è vincolata da entrambi i lati: verso il basso dal massimo operativo (16 V più lo spike), verso l'alto dal rating di 40 V, scelto per non gravare tutte le unità del costo, dell'ingombro e della RDS(on) peggiore di una catena a 60 V. Su una famiglia SMBJ 600 W un V_RWM di 24 V dà V_C = 38,9 V a 15,5 A sulla forma d'onda 10/1000 µs, appena dentro un buck da 40 V; un V_RWM di 40 V darebbe V_C = 64,5 V, incompatibile (§7).
- **Acceptance:** da verificare in schematico sul componente reale — la tensione di clamp effettiva (V_C) alla corrente di picco attesa, non il solo V_RWM (distinzione rilevante in selezione, fonte Diodes Inc. AN1142, §7), shall restare sotto il rating assoluto di ingresso del buck, verificato da datasheet.
- **Nota di dimensionamento (margine stretto):** con rating ≥ 40 V il margine tra V_C del clamp e rating del buck è di pochi volt sulla forma d'onda 10/1000 µs, e **negativo** su una 8/20 µs (SMBJ24A: V_C = 50,6 V a 77,5 A). Il requisito è quindi soddisfacibile solo con una **impedenza serie** tra clamp e buck — RDS(on) del MOSFET di inversione più induttore o ferrite di ingresso — che riduca la tensione residua al pin del regolatore. Questa impedenza va prevista fin dallo schematico e non è opzionale: senza, il rating a 40 V non regge la selezione. Questa impedenza si somma a quella del PTC di REQ-SAFE-001 e al filtro EMI predisposto da REQ-IF-016.
- **Assunzioni escluse dal design basis (decisione utente):**
  - **Guasto interno hard della sorgente di carica** (per esempio MOSFET di regolazione MPPT in corto, con passthrough della tensione di stringa PV non regolata): escluso per criterio a singolo guasto, coerente con l'ambito non safety-critical del progetto (§1).
  - **Sgancio del BMS in alta corrente** (spike induttivo L·di/dt dal loop batteria–busbar–inverter): trattato come caso limite che il dimensionamento di sistema (corrente dell'inverter, soglia di trip del BMS, eventuale precharge) shall evitare in condizioni operative normali. Dati di induttanza di loop e tempo di turn-off del BMS non disponibili in questa fase.
- **Nota:** il rumore condotto ad alta frequenza generato dallo switching dell'inverter non è coperto da questo requisito, che riguarda il clamp di tensione e non il filtro EMI — vedi REQ-IF-016.

### 3.2 Interfaccia / Protocollo

**REQ-IF-001** (Interface, Must, Confirmed)

- **Statement:** la scheda shall comunicare su CAN 2.0 a 125 kbit/s in rete multi-nodo con schede identiche; terminazione 120 Ω inseribile via jumper o solder-bridge.
- **Rationale:** il bit-rate basso consente cablaggi lunghi e poco schermati, tipici di un retrofit camper.
- **Acceptance:** frame loss < 0,1% su 24 h con ≥ 3 nodi e 10 m di bus.

**REQ-IF-002** (Interface, Must, Confirmed)

- **Statement:** il transceiver CAN shall disporre di modalità standby a basso assorbimento con wake-up da attività bus, interfacciabile a logica 3,3 V.
- **Rationale:** consente il risveglio remoto di un nodo via CAN oltre che dal segnale WAKEUP locale; contribuisce a REQ-EL-005.
- **Acceptance:** un nodo in deep-sleep si risveglia alla ricezione di un frame CAN dedicato.
- **Componente candidato:** NXP TJA1042T/3 (standby con bus wake-up, VIO 3–5 V, sistemi 12/24 V, §7).

**REQ-IF-003** (Interface, Should, Confirmed)

- **Statement:** il nodo in ruolo bridge shall esporre connettività WiFi (opzionalmente BT) verso Home Assistant; gli altri nodi shall poter tenere la radio spenta.
- **Rationale:** topologia scelta — schede identiche, una assume il ruolo di bridge.
- **Acceptance:** bridge raggiungibile da HA via WiFi; su nodo non-bridge la radio disabilitata non contribuisce all'assorbimento.
- **Nota:** questo requisito **vincola di fatto la scelta MCU alla famiglia ESP32** se si vuole una board identica per tutti i ruoli (vedi §4).

**REQ-IF-004** (Interface, Must, Confirmed)

- **Statement:** la scheda shall esporre 5 ingressi, ciascuno configurabile **per depopolazione** in una di tre varianti, con dominio di segnale distinto:
  - **(I) Diretto a pin del micro** — dominio logico 3,3 V: contatto secco verso massa, con pull-up esterno definito (non il solo pull-up interno del micro). **Non** è un ingresso a 12 V. Uso previsto: contatti magnetici (reed), microswitch e finecorsa locali alla board, con cablaggio corto non esposto alle linee 12 V del camper.
  - **(II) Opto-isolato** — dominio 12 V batteria servizi (9–16 V), logica "attivo" ≥ 8 V, "inattivo" ≤ 2 V (soglie confermate). Uso previsto: segnali provenienti dall'impianto camper a livello batteria.
  - **(III) Analogico verso ADC** — due modi d'uso alternativi sullo stesso footprint, selezionabili per depopolazione e per ponticello di saldatura:
    - **(III-a) Ingresso in tensione**, dominio 0–16 V lato campo. L'adattamento del livello verso l'ADC (0–3,3 V, target ≤ 2,45 V per linearità, vedi REQ-DIAG-001) è **a carico del dispositivo esterno collegato**, non della board. Uso previsto: sensori che consegnano già una tensione.
    - **(III-b) Ingresso resistivo con eccitazione a bordo**, per sensori passivi a due fili — **NTC di temperatura**, sonde di livello resistive, potenziometri. Il resistore superiore del partitore è commutato dal terminale di ingresso a un **rail di eccitazione**, e il sensore esterno costituisce il ramo verso massa.
- **Rationale:** requisito utente. La variante (I) non gestisce segnali a livello batteria ma contatti secchi locali, legati alla logica di attuazione della board. Nel modo (III-a) la board non progetta né garantisce un rapporto di partizione, per non ipotizzarne uno sbagliato su sensori non ancora noti e non dover mantenere BOM alternative; nel modo (III-b) l'eccitazione deve invece essere a bordo, perché un sensore passivo non può fornirla da sé.
- **Contro dichiarato del modo (III-a):** nessuna rete di sicurezza sulla qualità della misura — se il dispositivo esterno non scala il segnale, REQ-IF-006 evita il danno ma la lettura ADC sarà satura e inutilizzabile. L'onere di garantire Vmax ≤ 2,45 V ricade sull'installatore.
- **Acceptance:** (I) contatto chiuso letto correttamente entro il tempo di debounce (REQ-IF-005), con pull-up esterno a tolleranza nota; (II) lettura corretta a 9 V e 16 V, nessun danno a 24 V; (III-a) con un partitore di test noto popolato sul footprint, lettura ADC coerente entro le tolleranze di REQ-DIAG-001; (III-b) con una NTC nota collegata al terminale e l'eccitazione attiva, lettura coerente con la curva del sensore; a eccitazione disattivata, il canale non contribuisce al consumo di deep-sleep.
- **Provviste per il modo (III-b):** un partitore che attenua una tensione e uno che eccita un sensore resistivo **non hanno la stessa topologia**, quindi il footprint a due resistori da solo non basta. Ciascun canale analogico shall prevedere:
  - Un **ponticello di saldatura** che colleghi il capo alto del resistore superiore al terminale di ingresso (modo III-a) oppure al **rail di eccitazione** (modo III-b). Senza questa selezione la variante non è utilizzabile con una NTC.
  - Un rail di eccitazione **sezionabile**, derivato dal rail periferiche già commutato da load-switch (REQ-EL-004) o da un GPIO usato come sorgente: un partitore da 10 kΩ permanentemente collegato a 3,3 V assorbe ~165 µA per canale, e su più canali saturerebbe da solo il budget di deep-sleep di REQ-EL-005.
  - Il **resistore serie di protezione** di REQ-IF-006 (1–4,7 kΩ) entra nel partitore e falsa la lettura: va scelto il valore più basso compatibile con la protezione e incluso nel calcolo della caratteristica, oppure compensato in firmware.
- **Limiti del modo (III-b):** la lettura **non è ratiometrica**, perché l'ADC dell'ESP32-S3 usa un riferimento interno e non il rail di eccitazione, quindi la tolleranza del rail 3,3 V si trasferisce sulla misura — accettabile per una temperatura ambiente, non per misure di precisione. L'impedenza equivalente vista dall'ADC va inoltre mantenuta bassa, il che sconsiglia NTC ad altissima resistenza e va bilanciato con il consumo di eccitazione.
- **Nota di progetto:** footprint unico con BOM alternativa per variante — resistore serie e pull-up per (I), opto e resistenza per (II), pad del partitore per (III). Il dimensionamento dei pad (range kΩ–MΩ, package 0805) va definito in schematico garantendo lo spazio fisico per renderli popolabili, non congelando un valore.

**REQ-IF-005** (Interface, Must, Confirmed)

- **Statement:** ogni ingresso shall avere un filtro anti-rimbalzo: **RC hardware con costante di tempo 1 ms** più debounce firmware configurabile tra 10 e 100 ms.
- **Rationale:** contatti elettromeccanici e linee lunghe generano rimbalzi e spike.
- **Acceptance:** un treno di impulsi < 1 ms sovrapposto al segnale non genera falsi eventi; un cambio di stato reale è riportato entro il tempo di debounce configurato + 10 ms.
- **Nota (variante I):** la costante RC va dimensionata sul pull-up esterno definito (per esempio 10 kΩ), non sul pull-up interno del micro (~45 kΩ, con tolleranza non stretta, §7): un pull-up debole e impreciso allunga il tempo di risposta e lo rende meno ripetibile, penalizzante se il contatto è un finecorsa che deve fermare un motore in tempo utile.

**REQ-IF-006** (Interface, Must, Confirmed)

- **Statement:** ogni ingresso shall essere protetto da sovratensione con resistenza serie e clamp (TVS o zener) dimensionati per sopravvivere a **24 V continui** e ai transitori ISO 7637-2 pulse 3 senza danno al micro. La protezione si applica **senza eccezioni a tutte e tre le varianti**, compresa la **(I)**, per la quale si realizza come resistore serie (1–4,7 kΩ, da dimensionare) più clamp verso rail 3,3 V e massa, mantenendo la topologia "diretta" (nessun opto, nessun ADC dedicato).
- **Rationale:** decisione utente, che chiude l'ipotesi di lasciare la variante (I) senza protezione. Un pin GPIO ESP32-S3 ha rating assoluto −0,3…3,6 V (§7): senza resistore e clamp, un fault verso 12 V lo distrugge. Il vincolo d'uso "contatti locali" non elimina il rischio di errore di cablaggio, e la protezione uniforme evita di dover documentare e far rispettare all'installatore una restrizione d'uso che non ha riscontro visivo sulla scheda. Costo: circa 2 componenti passivi per canale su 5 canali.
- **Nota sui 24 V:** la soglia dei 24 V è un livello di **fault da errore di cablaggio**, non un'alimentazione supportata. Il progetto è a sola alimentazione 12 V (REQ-EL-001) e la variante 24 V è stata eliminata.
- **Acceptance:** (I) 24 V DC applicati per 5 min → nessun danno, tensione al pin sempre < 3,6 V; (II) e (III) 24 V DC per 5 min senza danno.

**REQ-IF-007** (Interface, Must, Confirmed)

- **Statement:** l'ingresso WAKEUP shall essere opto-isolato e attivo a livello batteria (12 V), integrato nella logica di power management (REQ-EL-006).
- **Rationale:** il segnale proviene dall'impianto veicolo (quadro acceso, comando da pannello), potenzialmente con massa non pulita.
- **Acceptance:** isolamento galvanico verificato; un fronte di 12 V sull'opto risveglia la scheda entro 500 ms.

**REQ-IF-008** (Interface, Must, Confirmed)

- **Statement:** la scheda shall esporre 4 uscite, configurabili **per depopolazione** in: (I) MOSFET **high-side** per carichi fino a **2 A continuativi** con PWM a **frequenza nominale 1,5–2 kHz**, configurabile per canale via firmware — uso primario dichiarato: **dimming di strisce LED**; (II) relè indipendente **2 A** (TE Axicom IM, contatto di scambio COM/NO/NC). In entrambe le varianti la corrente del carico **non è prelevata dal rail di alimentazione della board**: il carico ha alimentazione propria esterna e la board fornisce solo il contatto di commutazione. Questo scarica REQ-EL-005 e REQ-EL-007 dal budget di corrente dei carichi, ma non elimina i requisiti su dimensionamento di piste e connettori.
- **Carichi oltre 2 A e motori DC (decisione utente, 2026-08-01):** non sono commutati a bordo. Il canale della scheda (in variante I o II) comanda la **bobina di un relè esterno** — tipicamente automotive, decine–centinaia di mA — e il relè esterno commuta il carico. L'inversione dei motori DC è demandata al cablaggio dei relè esterni (REQ-IF-009). Conseguenze: (a) il precedente limite di 10 A della variante a relè **decade**; (b) la selezione, il fusibile e il cablaggio del relè esterno sono **requisiti di installazione**, fuori dal perimetro della scheda; (c) la bobina esterna è un carico induttivo in continua — il canale che la comanda shall avere il clamp di uscita popolato **oppure** (decisione utente 2026-08-02: clamp opzionale) il **diodo di ricircolo ai capi della bobina esterna come requisito di installazione obbligatorio**: senza né clamp né ricircolo, il transitorio di spegnimento supera il rating di 40 V del MOSFET high-side.
- **Rationale:** su un veicolo la carrozzeria è riferita a massa batteria. Con switching **high-side** un corto accidentale del cavo di uscita verso massa o telaio **non attiva il carico**, perché questo resta scollegato dal positivo finché il MOSFET non conduce; con **low-side** lo stesso corto attiverebbe il carico aggirando il comando. È la ragione per cui la prassi automotive usa prevalentemente high-side per carichi riferiti a massa veicolo (§7).
- **Implementazione (Confirmed):** **MOSFET P-channel discreto** con **level-shifter** dal GPIO 3,3 V verso il riferimento battery+. Scartate le alternative: lo *switch integrato "smart" automotive* offre diagnostica di sovracorrente, sovratemperatura e open-load, ma i tempi di commutazione tipici della famiglia (~300–550 µs) danno un massimo di ~1–2 kHz, **senza margine** rispetto al target di 1,5–2 kHz, e costa circa un ordine di grandezza in più per canale su 4 canali (REQ-LIFE-001); l'*N-channel con driver high-side* avrebbe RDS(on) migliore a parità di costo, ma il duty cycle prossimo al 100% richiede un charge pump dedicato (TI SLVA444, §7), complessità non giustificata a questa frequenza. Il P-channel ha die più grande e scelta più ristretta dell'N-channel equivalente, ma esistono opzioni automotive AEC-Q101 a bassa RDS(on) compatibili con il rating ≥ 40 V di REQ-EL-010.
- **Vincoli di progetto del gate drive:**
  - Il **resistore di pull-up gate-source** verso battery+ garantisce lo stato OFF con GPIO flottante, come richiesto da REQ-SAFE-003.
  - La tensione **V_GS shall essere limitata** entro il rating del MOSFET (tipicamente ±20 V): con il partitore che tira il gate verso massa a 16 V di batteria la V_GS è già prossima al limite, e durante un transitorio clampato (fino a ~38 V, REQ-EL-010) lo supererebbe. Serve quindi un **diodo Zener di clamp gate-source**, non opzionale.
  - La rete di gate **shall** essere dimensionata contro un tetto esplicito di perdite di commutazione, non genericamente «per rallentare i fronti». L'ipotesi che a 1,5–2 kHz le perdite di commutazione siano trascurabili **è stata verificata ed è falsa**: con un partitore di gate lento (fronti di ~15 µs) valgono ~1,3 W a 16 V e 5 A, cioè il triplo delle perdite di conduzione, e restano il termine dominante anche a 2 A. Il criterio è quindi t_on + t_off ≤ 2·P_sw,max / (V·I·f); con P_sw,max = 0,5 W nel caso peggiore ne discende un tempo di transizione ≤ 6 µs, che a 5 V/µs di dV/dt non compromette il contenimento delle emissioni di REQ-IF-016.
- **Rinuncia dichiarata:** senza switch integrato non c'è diagnostica per canale di open-load e sovratemperatura. Non è una perdita di protezione — la sovracorrente dei carichi è comunque demandata al quadro del camper (REQ-SAFE-001) — ma solo di segnalazione; se in futuro servisse, si aggiunge con shunt e amplificatore sullo stesso principio di REQ-IF-011.
- **Contro residuo della topologia high-side:** il ritorno del carico esce dalla board, il che cambia, senza eliminarle, le considerazioni di grounding (REQ-EL-009).
- **Limite di corrente della variante (I) — 2 A, con riserva di incremento (decisione utente):** il limite discende dal **budget termico**, non dal MOSFET, che è dimensionato molto oltre. Con la sola piazzola di montaggio la resistenza termica giunzione-ambiente stimata (~120 °C/W, **da confermare con misura [B]**) consente ~0,18 W per canale a 2 A, cioè una giunzione intorno ai 64 °C: margine ampio. A 5 A la dissipazione sale a ~0,9 W a caldo e la giunzione supererebbe i 150 °C, valore accettabile a datasheet ma fuori da un obiettivo di progetto ragionevole. Rialzare il limite richiede un **piano di rame di smaltimento sulla faccia opposta**, collegato alla tab da via termici: con una superficie confrontabile con l'in² di rame 2 oz del datasheet il limite tornerebbe intorno ai **5 A**.
  - **La riserva shall essere esercitata in fase di layout, non dopo.** Il rame non è depopolabile: se il piano non viene disegnato, aumentare la corrente richiede una nuova revisione di scheda. Il layout **shall** quindi tentare di ricavare il piano anche restando a 2 A di requisito, e riportare a verbale se non ci riesce.
  - **La rivalutazione shall basarsi su RθJA misurata [B]** sul prototipo, non su una stima o su un valore di letteratura.
  - **Il footprint del MOSFET shall restare quello a maggiore capacità termica** (DPAK o equivalente) anche se a 2 A risulta sovradimensionato: è il footprint, non il valore, a rendere possibile l'incremento futuro.
  - **Impatto funzionale contenuto:** i 2 A limitano solo la potenza *dimmerabile* (24 W per canale a 12 V). I carichi on/off oltre tale soglia sono demandati al relè esterno comandato dalla scheda; il limite di canale a bordo è 2 A in entrambe le varianti.
- **Acceptance:** (I) **[B]** 2 A continui a 40 °C ambiente con temperatura del MOSFET entro i limiti di datasheet e RθJA effettiva misurata e annotata in BOM; con comando OFF, un corto del cavo di uscita verso massa telaio non alimenta il carico; PWM a 1,5–2 kHz con fronti controllati e nessun flicker percepibile su striscia LED reale. (II) **[B]** commutazione di 2 A resistivi verificata funzionalmente; **[D]** l'endurance in numero di cicli è coperta dal rating dichiarato dal costruttore del relè; **[B]** comando affidabile della bobina di un relè automotive esterno reale, con ricircolo esterno cablato.
- **Frequenza PWM — motivazione e rischio accettato:** 1,5–2 kHz sta sopra la soglia di rischio flicker di ~1250 Hz per la modulazione a profondità piena, evitando la banda ultrasonica che richiederebbe MOSFET e gate-drive più veloci. **Rischio accettato:** la banda 1,5–2 kHz è udibile, quindi è possibile un fischio a basso livello dalle induttanze parassite di cavi e driver LED economici, percepibile nel silenzio dell'abitacolo; la configurabilità per canale consente di spostare il punto di lavoro entro il limite dell'hardware selezionato. *Fonte:* il testo di IEEE 1789 non è stato consultato direttamente, le soglie provengono da interpretazioni divulgative e commerciali (§7).
- **Nota:** ogni uscita MOSFET richiede un clamp per i transitori residui su cavi e connettori lunghi; i relè richiedono driver con diodo di ricircolo e spegnimento della bobina via load-switch (REQ-EL-004).
- **Nota sull'isolamento:** nella variante (I) il MOSFET commuta il **positivo** verso il carico e il ritorno va direttamente dal carico alla massa telaio o batteria, senza transitare per la massa della board. Non si tratta però di isolamento galvanico: il source del MOSFET e la massa scheda condividono lo stesso riferimento batteria−. Solo la variante (II) a relè offre isolamento galvanico vero.

**REQ-IF-009** (Interface, Must, Confirmed) — *rivisto 2026-08-01*

- **Statement:** l'inversione di motori DC (per esempio gradino o antenna) shall essere realizzata da **due relè esterni** comandati da due uscite della scheda, con i contatti esterni cablati in **configurazione di inversione** (COM di ciascun relè a un morsetto del motore, i due NO uniti sul positivo del carico, i due NC sul negativo): in tale rete il cortocircuito positivo→negativo è topologicamente impossibile, qualunque sia lo stato delle bobine.
- **Rationale:** decisione utente 2026-08-01 — la scheda non commuta motori a bordo (REQ-IF-008). La rete di inversione per cablaggio conserva la stessa garanzia topologica della precedente variante on-board: nessuna combinazione di comandi, inclusa l'attivazione simultanea spuria, produce un corto.
- **Acceptance:** vedi REQ-SAFE-002. Lo schema di cablaggio esterno, con il diodo di ricircolo su ciascuna bobina e il TVS bidirezionale ai capi del motore, shall essere parte della documentazione di installazione.
- **Conseguenze dichiarate:** la frenatura dinamica nei due stati di riposo è inerente alla rete di inversione (motore in corto sui contatti, marcia a ruota libera non ottenibile); il firmware shall inserire un tempo morto fra le due direzioni, da congelare sul tempo di rilascio misurato dei relè esterni scelti.
- **Secondo schema — esclusione in cascata per comandi mutuamente esclusivi (2026-08-02):** per due utenze indipendenti che non devono mai essere attive insieme (non un'inversione), l'esclusione shall poter essere realizzata in installazione con **NC del canale 1 → COM del canale 2** (alimentazione su COM1), on-board entro 2 A o sui relè esterni. Limiti dichiarati e accettati per questo solo caso d'uso: non robusta al contatto incollato di NC1; finestra transitoria di qualche ms su comandi quasi simultanei (l'esclusione primaria resta a firmware, la cascata è la rete di sicurezza); la corrente del ramo 2 transita per NC1 e ne consuma rating ed endurance. La cascata **non è ammessa** come sostituto della rete di inversione sui motori. Dettagli in [`04b`](hardware/schematics/04b-relay-output-stage.md) §3.6.1.

**REQ-IF-010** (Interface, Must, Confirmed)

- **Statement:** la sezione motori shall pilotare 1 motore stepper e 2 servo RC standard (segnale 50 Hz, impulso 1–2 ms, alimentazione 5 V), con compatibilità sia con stepper unipolari classe 28BYJ-48 sia con NEMA17 bipolari.
- **Acceptance:** rotazione controllata di un 28BYJ-48 (modificato bipolare) e di un NEMA17 (≤ 1,2 A/fase) con lo stesso driver; 2 servo comandati simultaneamente senza jitter percepibile (> ±10 µs sull'impulso).
- **Implementazione:** driver step/dir **TMC2209** (2 A RMS, 2,8 A di picco, §7) al posto dell'ULN2003: copre il NEMA17 nativamente e il 28BYJ-48 previa modifica bipolare. L'ULN2003 non può pilotare un bipolare, quindi la doppia compatibilità richiesta lo esclude come soluzione unica.
- **Modifica bipolare del 28BYJ-48 (versione 5 V):** apertura del coperchio, taglio della pista centrale sul PCB interno, rimozione del filo rosso (comune); il risultato sono 2 avvolgimenti (Arancio+Rosa e Giallo+Blu) pilotabili come bipolare a 4 fili (fonti hobbistiche concordanti, §7). **Vincolo critico:** corrente massima ~100 mA/fase, oltre la quale il motore si scalda e può fondere gli avvolgimenti. Il TMC2209 imposta il limite via UART (registro IHOLD_IRUN), quindi lo stesso driver serve sia il 28BYJ-48 modificato sia il NEMA17 cambiando un solo parametro firmware, senza BOM alternativa. **Rischio dichiarato:** la modifica è manuale e va eseguita su ogni singolo motore prima del montaggio, con rischio di danno se eseguita da terzi.

**REQ-IF-011** (Interface, Must, Confirmed)

- **Statement:** la sezione motori shall misurare gli assorbimenti per implementare limit-switch virtuali, cioè la rilevazione della battuta meccanica, tramite un **unico sistema di misura** sul rail 5 V motori.
- **Rationale:** evita l'installazione di finecorsa fisici su serrande e valvole. La soluzione a sense singolo è una decisione utente, resa possibile dal vincolo di non contemporaneità dei servo (REQ-EL-007, REQ-SW-001): con un solo servo in movimento alla volta, l'attribuzione della battuta è univoca anche senza sense per canale. Dimezza componenti, costo e canali ADC rispetto alla soluzione a due amplificatori, coerentemente con REQ-LIFE-001.
- **Acceptance:** battuta meccanica rilevata entro 200 ms e motore de-energizzato prima di danni meccanici, con il secondo servo in tenuta di posizione e lo stepper eventualmente in movimento.
- **Implementazione:**
  - **Stepper:** **StallGuard4 del TMC2209**, rilevazione di stallo sensorless integrata nel driver e letta via registro UART SG_RESULT o pin DIAG. Nessun sense di corrente esterno necessario.
  - **Servo:** **un solo INA180A1** (gain 20 V/V) con shunt unico sul rail 5 V motori. Dimensionamento indicativo: shunt **33 mΩ** ⇒ ~1,65 V di fondo scala a 2,5 A (REQ-EL-007), sotto la soglia di 2,45 V consigliata per la linearità dell'ADC; a corrente di riposo (~100 mA) l'uscita resta risolvibile (~66 mV, ampiamente sufficiente su ADC a 12 bit). Dissipazione ~0,21 W al picco: resta valida l'eccezione **1206** della convenzione BOM. Costo: 1 IC in SOT23-5 e 1 shunt.
- **Condizioni di validità dell'attribuzione:** poiché la misura è aggregata, la lettura è interpretabile solo se (a) **un solo servo è in movimento alla volta**, garantito dal firmware, e (b) il contributo dello stepper è trattato come **offset noto e limitato** (~200 mA, imposto dal registro IHOLD_IRUN del TMC2209 e quindi non variabile con il carico), da sottrarre o da includere nella soglia di battuta. Se una futura evoluzione richiedesse il movimento simultaneo dei due servo, questa soluzione **non** sarebbe più sufficiente e occorrerebbe tornare a un sense per canale.
- **Nota di instradamento ADC:** su ESP32-S3 i canali **ADC2 non sono utilizzabili in modo affidabile mentre il WiFi è attivo** (§7). Poiché la board è identica su tutti i nodi e qualsiasi nodo può assumere il ruolo di bridge (REQ-IF-003), il sense motori e ogni ingresso analogico critico (compresa la variante III di REQ-IF-004) **shall** essere instradati solo su pin **ADC1**, indipendentemente dal ruolo del nodo.

**REQ-IF-012** (Interface, Must, Confirmed)

- **Statement:** la scheda shall esporre su connettore un bus I²C a 3,3 V per espansione esterna (IO expander, sensori), con pull-up on-board disinseribili e protezione ESD sulle linee.
- **Rationale:** estende l'IO senza un re-spin della scheda.
- **Acceptance:** comunicazione a 100 kHz con dispositivo esterno su cavo di 30 cm; scheda funzionante con connettore aperto o in corto verso GND.
- **Connettore e pinout (Confirmed):** **JST PH, passo 2,0 mm, 4 pin**, con ordine dei segnali **Qwiic-like: pin 1 = GND, pin 2 = VCC (3,3 V), pin 3 = SDA, pin 4 = SCL**. La numerazione del pin 1 shall essere serigrafata sulla scheda. Conseguenza dichiarata: si rinuncia alla compatibilità fisica diretta con l'ecosistema Qwiic/STEMMA-QT, che usa JST-SH 1,0 mm, quindi servirà un cavo adattatore per interfacciarsi a moduli Qwiic esistenti — ma con l'ordine dei segnali identico l'adattatore è un semplice cambio di connettore pin-a-pin, senza incroci di fili e senza rischio di invertire alimentazione e segnali. Rating JST PH ~2 A/contatto con AWG24 (§7), ampiamente sufficiente per un bus di espansione.
- **Nota:** non sono previsti segnali di interrupt o reset sul connettore. Se un futuro IO expander dovesse generare eventi senza polling, servirà un GPIO aggiuntivo su un connettore diverso o un re-spin — vincolo accettato in cambio di un connettore più piccolo e di un cablaggio standard.

**REQ-IF-013** (Interface, Must, Confirmed)

- **Statement:** la scheda shall montare **due LED di segnalazione dello stato CANopen**, conformi a **CiA 303-3** (lo standard ammette in alternativa un solo LED bicolore):
  - **LED verde "RUN"** — stato NMT del nodo: flicker (~10 Hz) = LSS configuration attivo; blink = Pre-operational; singolo flash = Stopped; triplo flash = download firmware in corso; fisso = Operational.
  - **LED rosso "ERR"** — stato errori: spento = nessun errore; flicker = Node-ID LSS non configurato o CANopen non inizializzato; blink = errore di configurazione generale; singolo flash = soglia di warning CAN raggiunta; doppio flash = errore Heartbeat consumer su nodo remoto; triplo flash = timeout ricezione SYNC; quadruplo flash = timeout evento PDO; fisso = CAN bus-off.
- **Rationale:** conseguenza diretta della scelta CANopen (REQ-SW-003). Lo standard richiede l'indicazione visiva dello stato del nodo per una diagnosi rapida senza strumentazione; CANopenNode implementa nativamente questa logica nel modulo `CO_LEDs`, quindi l'onere hardware si riduce a 2 LED pilotabili.
- **Acceptance:** agli stati NMT Pre-operational, Operational e Stopped il LED RUN mostra rispettivamente blink, fisso e singolo flash; su bus-off simulato (disconnessione o corto del bus) il LED ERR resta fisso e si spegne al ripristino del traffico CAN valido.
- **Nota di progetto:** valutare in schematico un LED bicolore (footprint singolo, 3 pin) contro due LED distinti (2 footprint, ciascuno con la propria resistenza di limitazione): lo standard ammette entrambe le soluzioni, il bicolore riduce ingombro e BOM ma non consente di leggere RUN ed ERR simultaneamente. Questi LED sono indicatori obbligatori del protocollo, distinti dai LED di stato generici di REQ-DIAG-001; come quelli sono pilotati dall'I/O expander (REQ-IF-015), senza load-switch dedicato, e devono risultare spenti in deep-sleep e in OFF per la sola polarità di pilotaggio.

**REQ-IF-014** (Interface, Must, Confirmed)

- **Statement:** le linee CAN-H e CAN-L shall tollerare, ai morsetti, **ESD a contatto ±8 kV** secondo IEC 61000-4-2, **corto verso qualsiasi potenziale dell'impianto** entro ±58 V e i transitori ISO 7637-2 accoppiati sul cablaggio. La protezione shall essere ottenuta **per selezione del transceiver**; sulla scheda shall essere previsto in aggiunta il **footprint depopolato per un choke di modo comune** e per un array di protezione esterno, da popolare solo se necessario.
- **Rationale:** il bus attraversa il camper con cavo non schermato e morsettiera accessibile, quindi le linee vanno trattate come esposte. Il transceiver candidato di REQ-IF-002 copre però già tutti e tre gli scenari sui pin CANH/CANL: **±8 kV IEC 61000-4-2**, tensione ammessa **−58…+58 V** e immunità dichiarata ai pulse ISO 7637-2 1, 2a e 3a (datasheet NXP TJA1042 rev. 11, §7). Un array di protezione esterno sarebbe quindi **ridondante** e in contrasto con il criterio di costo di REQ-LIFE-001: il requisito si soddisfa scegliendo il componente giusto, non aggiungendone uno.
- **Acceptance [D]:** il transceiver selezionato shall dichiarare a datasheet ESD a contatto ≥ ±8 kV IEC 61000-4-2 sui pin di bus, tensione di guasto sui pin di bus ≥ ±40 V e immunità ai pulse ISO 7637-2 pertinenti, con i valori annotati in BOM. Se un transceiver alternativo non li dichiarasse, l'array esterno diventa obbligatorio e i footprint predisposti vanno popolati.
- **Nota:** il footprint per il choke di modo comune risponde a un'esigenza diversa — il **rumore condotto** dell'inverter sulla stessa struttura, non l'ESD — e segue lo stesso criterio di REQ-IF-016: predisposto e non popolato, si valorizza solo se la misura sul veicolo lo richiede.
- **Margine dichiarato:** i ±58 V del transceiver coprono con ampio margine un corto accidentale verso il positivo batteria a 12 V, che è lo scenario di guasto plausibile su questo impianto.

**REQ-IF-015** (Interface, Must, Confirmed)

- **Statement:** la scheda shall montare un **I/O expander I²C a 8 bit con uscite push-pull** sul bus di REQ-IF-012, per pilotare le funzioni lente e non critiche nei tempi: i **LED** (2 di stato CANopen, REQ-IF-013, più quelli generici di REQ-DIAG-001) e i segnali di **enable dei load-switch** (REQ-EL-004). L'indirizzo I²C shall essere selezionabile via strap e documentato, per non collidere con dispositivi collegati al connettore di espansione.
- **Rationale:** il bilancio dei GPIO (vedi §4.3) non chiude con margine sui 34 pin del modulo. Spostare 6 funzioni lente sull'expander libera altrettanti GPIO al costo di un solo IC, senza consumare pin aggiuntivi perché il bus I²C è già presente per REQ-IF-012. La scelta push-pull, anziché quasi-bidirezionale tipo PCF8574, serve a pilotare i LED con corrente adeguata senza resistenze di pull-up aggiuntive.
- **Acceptance:** **[B]** accensione e spegnimento indipendenti di ogni LED e commutazione di ogni load-switch via I²C; **[B]** al reset dell'MCU e dell'expander tutte le uscite risultano nello stato inattivo, verificato su oscilloscopio; **[D]** corrente di riposo dell'expander compatibile con il budget di deep-sleep di REQ-EL-005.
- **Coerenza con REQ-SAFE-003:** al reset le uscite dell'expander vanno in alta impedenza, quindi le reti di polarizzazione passive richieste da REQ-SAFE-003 shall essere presenti anche su queste linee: pull-down sugli enable dei load-switch, così che un expander non inizializzato lasci le sezioni di potenza disalimentate.
- **Limitazione dichiarata:** le funzioni pilotate dall'expander dipendono dalla disponibilità del bus I²C. Un blocco del bus impedisce di comandare LED e load-switch, ma **non** compromette le uscite di potenza né i motori, che restano su GPIO diretti dell'MCU. Non sono state spostate sull'expander funzioni con vincoli di temporizzazione (PWM, STEP/DIR) né di sicurezza.

**REQ-IF-016** (Interface, Must, Confirmed)

- **Statement:** l'ingresso di alimentazione shall prevedere i **footprint** per un **filtro EMI** — rete LC o pi e **choke di modo comune** — **non popolati di default**. La popolazione avviene solo se la misura del rumore condotto sulla bus-bar reale lo richiede.
- **Rationale:** decisione utente. Il rumore condotto ad alta frequenza generato dallo switching dell'inverter e delle sorgenti di carica sulla bus-bar condivisa non è coperto dal clamp di REQ-EL-010, che è un dispositivo di tensione e non di filtro. Dimensionare un filtro senza aver misurato il disturbo reale significa però scegliere valori a caso: prevedere i soli footprint costa lo spazio di layout e nulla in BOM, evita un re-spin se il filtro servirà, e non impone componenti se non servirà.
- **Acceptance:** **[B]** la scheda funziona a norma con i footprint non popolati e con i ponticelli di continuità chiusi; **[B]** se popolati, il rumore residuo sul rail 3,3 V rientra nelle tolleranze di REQ-EL-009.
- **Nota di progetto:** i footprint shall prevedere ponticelli di corto o resistori da 0 Ω che garantiscano la continuità del ramo quando il filtro non è popolato, così che la configurazione di default sia funzionante e non richieda strap improvvisati. L'induttore serie del filtro, se popolato, contribuisce anche all'impedenza di ingresso richiesta da REQ-EL-010.

### 3.3 Timing & Performance

**REQ-TIM-001** (Timing, Should — round-trip Confirmed, ripartizione interna Assumed)

- **Statement:** il **round-trip di comando** shall essere **≤ 250 ms**, misurato sul bus CAN: frame di comando ricevuto → uscita commutata → frame di conferma di stato pubblicato. Ripartizione interna del budget (indicativa, da verificare a firmware): ≤ 100 ms da comando ad attuazione, ≤ 100 ms da attuazione a pubblicazione della conferma, ~50 ms di margine. Per gli eventi generati localmente, la latenza fronte su ingresso → frame CAN pubblicato shall essere ≤ debounce + 50 ms.
- **Rationale:** decisione utente. Il round-trip è la grandezza che l'utente percepisce davvero — premo il comando e vedo lo stato aggiornato — e a differenza della sola latenza di andata è verificabile con un unico strumento collegato al bus. Il limite è ampiamente compatibile con l'infrastruttura scelta: a 125 kbit/s (REQ-IF-001) un frame CAN standard con 8 byte di dati occupa ~1 ms, quindi il tempo di bus è trascurabile e il budget è consumato dal ciclo di polling/PDO del firmware e dal tempo di attuazione (una bobina di relè impiega tipicamente 5–10 ms a chiudere). Il vincolo è quindi di progetto firmware, non di banda del bus.
- **Acceptance:** misura con analizzatore CAN su ≥ 100 cicli comando/conferma; nessun campione oltre 250 ms. La ripartizione interna si verifica in parallelo con analizzatore logico sul pin di uscita.
- **Perimetro dichiarato:** il limite si applica **da bus CAN a bus CAN**. La latenza percepita end-to-end in Home Assistant aggiunge la tratta WiFi e l'elaborazione del bridge e di HA, che non sono sotto il controllo della board e non rientrano in questo requisito.

### 3.4 Meccanica / Fisica

**REQ-MECH-001** (Mechanical, Must, Confirmed) — *Form factor e montaggio*

- **Statement:** il PCB shall rientrare in un ingombro massimo di **100 × 100 mm**, con **quattro fori di fissaggio M3 agli angoli** e **angoli smussati**. Il montaggio avviene su un **contenitore custom in stampa 3D realizzato in PETG**, il cui progetto di dettaglio resta fuori dal perimetro di questo documento (§1); questo requisito ne fissa la sola interfaccia meccanica e il materiale.
- **Rationale:** decisione utente. I 100 × 100 mm coincidono con il formato di prima fascia di prezzo della quasi totalità dei fornitori di PCB, quindi il vincolo dimensionale contribuisce direttamente al criterio di costo di REQ-LIFE-001. Gli angoli smussati facilitano l'inserimento in un contenitore stampato con raggi interni non nulli.
- **Acceptance [B]:** verifica dimensionale del PCB fabbricato contro il disegno meccanico; inserimento e fissaggio nel contenitore con quattro viti M3 senza forzature.
- **Vincoli per il floorplan:** i fori M3 e gli smussi vanno tenuti liberi da rame e componenti; l'area di keep-out di antenna di REQ-MECH-002 va conciliata con il posizionamento a bordo scheda del modulo.
- **Materiale (decisione utente):** **PETG**, con temperatura di transizione vetrosa **~80 °C** e stabilità dimensionale fino a ~70 °C (§7). Sostituisce il PLA, inizialmente ipotizzato, che con transizione vetrosa ~60 °C e servizio continuo 45–55 °C avrebbe coperto il range operativo ma non le temperature che un camper chiuso al sole raggiunge da fermo, con rischio di deformazione e allentamento del serraggio sui fori M3. Il PETG mantiene lo stesso processo di stampa e un costo di filamento comparabile. Il margine contro il caso estivo peggiore va confrontato con il range di sopravvivenza che emergerà dalla BOM (REQ-ENV-001).

**REQ-MECH-002** (Mechanical, Must, Confirmed)

- **Statement:** la **scheda portante** shall rispettare la keep-out di antenna prescritta per il modulo ESP32-S3-Tiny — nessun rame, nessun piano di massa e nessuna traccia sotto e attorno all'area dell'antenna del modulo — e il modulo shall essere posizionato a filo del bordo della scheda. Il connettore FPC del modulo shall restare accessibile a scheda montata, per la programmazione via scheda adattatrice USB (REQ-DIAG-002).
- **Rationale:** su un nodo bridge la portata WiFi determina la raggiungibilità da Home Assistant, e una violazione della keep-out è un errore di layout non correggibile senza re-spin. Costo nullo se previsto fin dall'inizio, costo di un re-spin se scoperto dopo.
- **Acceptance:** ispezione del layout contro il disegno di keep-out della documentazione del modulo; misura di RSSI dalla posizione di installazione tipica nel vano camper.

**REQ-MECH-003** (Mechanical, Must, Confirmed) — *Connettori e posizionamento*

- **Statement:** la scheda shall esporre i seguenti connettori:
  - **Alimentazione board** (REQ-EL-001/002): morsettiera a vite **5,08 mm, 2 poli**.
  - **4 uscite di potenza** (REQ-IF-008): morsettiera a vite **5,08 mm**.
  - **Bus CAN** (REQ-IF-001): morsettiera a vite **2,54 mm**.
  - **5 ingressi** (REQ-IF-004): morsettiera a vite **2,54 mm** *e*, **elettricamente in parallelo**, un connettore **JST XH a 2,5 mm** sugli stessi nodi.
  - **Bus I²C** (REQ-IF-012): JST PH 2,0 mm, 4 poli.
  - **Servo e stepper** (REQ-IF-010): connettori dedicati, tipo da congelare in schematico.
- **Posizionamento:** tutte le **morsettiere a vite shall stare sui bordi** della scheda, accessibili con il cacciavite a contenitore aperto. I connettori **JST e quelli dei motori possono essere interni** all'area del PCB, essendo a innesto e non richiedendo accesso frontale con utensile.
- **Rationale:** decisione utente. Il passaggio dell'alimentazione board da 2,54 a 5,08 mm risolve il dubbio sul wire gauge: il passo maggiore accetta senza incertezze cavi da 16 AWG e oltre, mentre il 2,54 mm era dato per 18–26 AWG da fonti deboli. Il doppio connettore sugli ingressi copre due modalità di cablaggio: morsettiera per cavi sfusi provenienti dall'impianto, JST per sensori preassemblati con codino e connettore crimpato — caso tipico delle NTC e delle sonde del modo (III-b) di REQ-IF-004. Rating morsettiera 5,08 mm tipicamente **10 A (UL) / 15 A (IEC)** (datasheet RS PRO, §7): con il limite di canale portato a 2 A in entrambe le varianti (REQ-IF-008, rev. 2026-08-01) è sovradimensionato, ma resta per robustezza meccanica del cablaggio da impianto e per non cambiare un footprint già congelato.
- **Acceptance:** **[B]** nessun surriscaldamento anomalo alla corrente nominale di ciascuna morsettiera a 40 °C ambiente; tutte le morsettiere azionabili con cacciavite senza rimuovere altri componenti; **[D]** portata di corrente, sezione di cavo ammessa ed endurance di inserzione coperte dal datasheet del part number scelto, con margine annotato in BOM.
- **Nota sul passo del connettore ingressi:** JST non produce una serie a 2,54 mm; la corrispondenza più vicina è la **serie XH a 2,5 mm**, qui adottata. Se l'intenzione fosse invece uno **strip di pin a 2,54 mm** — meno robusto e senza ritenzione — la scelta va corretta in schematico.
- **Nota di installazione:** morsettiera e JST di uno stesso ingresso sono sullo stesso nodo elettrico. Vanno usati in alternativa, mai entrambi contemporaneamente sullo stesso canale: il vincolo va riportato nella documentazione di montaggio.

### 3.5 Ambientale

**REQ-ENV-001** (Environmental, Must, Confirmed)

- **Statement:** la scheda shall **operare** tra **0 e +40 °C** con umidità fino all'85% senza condensa, in ambiente soggetto a vibrazioni veicolari (installazione in vano interno del camper, non nel vano motore). Fuori dal range operativo, a scheda spenta, non è richiesto il funzionamento ma **l'assenza di danno permanente**: il range di sopravvivenza effettivo **non è fissato a priori**, discende dai componenti scelti e shall essere documentato in BOM.
- **Rationale:** il range operativo corrisponde alle condizioni in cui l'impianto è effettivamente in uso, con camper occupato e riscaldamento attivo. Il range di sopravvivenza è invece determinato in rimessaggio, quando la board è spenta e il camper può stare al sole d'estate o sotto zero d'inverno: fissarne uno a priori significherebbe imporre un vincolo di selezione senza sapere se sia il collo di bottiglia, mentre il valore reale emerge dai componenti effettivamente disponibili.
- **Acceptance [D]:** ogni componente selezionato con range **operativo** che copre 0…+40 °C, verificato da datasheet. Per i componenti a **range di immagazzinamento tipicamente più stretto** — condensatori elettrolitici e polimerici, relè, connettori e morsettiere in plastica, modulo MCU — shall essere verificato e annotato in BOM anche il range di **storage**; il minimo comune fra questi valori costituisce il range di sopravvivenza dichiarato della scheda. Nessuna prova in camera climatica: non disponibile nel perimetro del progetto.

### 3.6 Sicurezza

**REQ-SAFE-001** (Safety, Must, Confirmed)

- **Statement:** (a) l'ingresso di alimentazione **della sola board** shall essere protetto da un **fusibile resettabile (PTC)** dimensionato sul consumo interno — MCU, transceiver, driver, bobine relè — non sui carichi pilotati; (b) la protezione da sovracorrente dei **circuiti di carico esterni** commutati da MOSFET o relè **non** è a bordo scheda: è demandata al quadro fusibili del camper a monte ed è un **requisito di installazione** da riportare nella documentazione di montaggio.
- **Rationale:** decisione utente. I carichi hanno alimentazione propria esterna (REQ-IF-008) e il quadro del camper ha già i propri fusibili di ramo, quindi replicarli a bordo significherebbe quattro portafusibili, spazio e costo per una protezione ridondante. Il PTC sul solo ingresso board è invece giustificato: si autoripristina senza intervento su una scheda installata in un vano poco accessibile, che è esattamente lo scenario d'uso.
- **Acceptance:** **[B]** corto sul rail di alimentazione board → il PTC interviene e la scheda si ripristina da sola alla rimozione del guasto, senza danni; **[D]** corrente di hold del PTC superiore con margine al consumo massimo della board, e corrente di trip compatibile con la sezione delle piste, verificate a datasheet.
- **Conseguenze del PTC da verificare in schematico:** un PTC ha **resistenza serie non trascurabile** (tipicamente da decimi a qualche ohm) e la sua caduta va sottratta al margine di tensione all'estremo inferiore del range operativo (10 V, REQ-EL-001); la corrente di hold va scelta sopra il consumo di picco della board con relè eccitati, tenendo conto che si **riduce con la temperatura ambiente** (REQ-ENV-001, fino a +40 °C). Effetto collaterale favorevole: quella stessa resistenza serie contribuisce all'**impedenza di ingresso** che REQ-EL-010 richiede fra clamp e buck.
- **Rischio residuo dichiarato:** un guasto su un circuito di carico non è limitato dalla board. Se il quadro del camper non ha un fusibile sul ramo che alimenta quel carico, piste e morsettiera di uscita sono esposte alla corrente di guasto — l'onere ricade sull'installatore e va scritto nella documentazione.

**REQ-SAFE-002** (Safety, Must, Confirmed) — *rivisto 2026-08-01*

- **Statement:** l'esclusione reciproca delle coppie di inversione shall essere garantita **in hardware** dal cablaggio dei contatti dei relè esterni in configurazione di inversione (REQ-IF-009), non dal solo firmware.
- **Rationale:** un bug firmware o un glitch al boot non deve poter produrre un corto. Con l'inversione demandata ai relè esterni la garanzia si sposta dallo schematico al **cablaggio di installazione**: resta hardware, ma la verifica cambia oggetto.
- **Acceptance:** forzando via software l'attivazione simultanea delle due uscite di comando, il carico non è mai alimentato in configurazione di corto; l'ispezione dello **schema di cablaggio esterno** (parte della documentazione di installazione) conferma l'impossibilità topologica.
- **Rischio residuo dichiarato:** la garanzia dipende dalla corretta esecuzione del cablaggio da parte dell'installatore; la scheda non può verificarla. Lo schema di inversione shall quindi essere documentato come disegno obbligatorio, non come nota.

**REQ-SAFE-003** (Safety, Must, Confirmed)

- **Statement:** al power-on, in brown-out e in caso di reset da watchdog, tutte le uscite shall trovarsi o portarsi nello stato disattivato.
- **Rationale:** fail-safe: un'utenza come pompa o boiler non deve mai attivarsi spontaneamente; sulle coppie che comandano l'inversione esterna (REQ-IF-009) l'attivazione spuria simultanea non produce un corto grazie al cablaggio di inversione, ma resta un'attuazione non richiesta da impedire.
- **Acceptance [B]:** almeno 20 cicli di power-on e altrettanti di brown-out indotto con alimentatore da banco, senza alcuna attivazione spuria osservata su oscilloscopio; ispezione dello schematico che conferma la presenza delle reti di polarizzazione passive su ogni stadio di uscita.
- **Conseguenza sullo schematico:** lo stato sicuro shall essere garantito **passivamente**, senza dipendere dal firmware. I GPIO dell'MCU sono in alta impedenza durante reset e boot, quindi ogni stadio di uscita richiede una rete di polarizzazione esterna che imponga il livello di OFF con il pin flottante: pull-up di gate verso il source per i P-MOSFET high-side (REQ-IF-008 variante I) e pull-down sugli ingressi dei driver di bobina per le varianti a relè. Vanno inoltre evitati per queste funzioni i pin di strapping dell'MCU, che al boot assumono livelli imposti dal bootloader — vincolo da riportare nella tabella di allocazione dei pin (§4.3).

### 3.7 Interfaccia Software / Firmware

**REQ-SW-001** (Software, Must, Confirmed)

- **Statement:** il firmware shall implementare: (a) la gestione low-power in running (clock gating, radio spenta sui nodi non-bridge, sleep tra gli eventi); (b) la sequenza ordinata di shut-down (REQ-EL-006); (c) l'**esclusione mutua nel movimento dei due servo** — mai più di un servo in movimento alla volta, con accodamento delle richieste concorrenti.
- **Rationale (c):** il vincolo di esclusività non è un'ottimizzazione ma il presupposto di due requisiti hardware: dimensiona il rail motori a 2,5 A anziché oltre 4 A (REQ-EL-007) e rende univoca l'attribuzione della battuta con un sense singolo (REQ-IF-011). Va quindi trattato come vincolo di sicurezza funzionale, non come politica di scheduling modificabile.
- **Acceptance:** assorbimento in running (nodo non-bridge, nessun carico attivo) misurato e documentato; sequenza di shut-down completa in meno di 5 s; una richiesta di movimento su un servo mentre l'altro è in moto viene accodata e non eseguita in parallelo, verificato su ≥ 100 tentativi.

**REQ-SW-002** (Software, Should, Confirmed — architettura e dettaglio funzionale differiti)

- **Statement:** configurazione, telemetria e diagnostica dei nodi shall essere accessibili, oltre che via CAN, attraverso una **interfaccia macchina documentata** esposta dalla board — API su rete e/o protocollo su porta seriale USB. Il **frontend Vue.js** che la consuma può essere **servito dalla board oppure ospitato altrove** (per esempio come pannello di Home Assistant o da un host di rete). La scelta dell'architettura e il dettaglio funzionale — schermate, modello dati, endpoint, autenticazione — shall essere definiti in una **specifica firmware/HMI separata, redatta dopo la realizzazione dell'hardware**.
- **Rationale:** il requisito che conta per la board è **esporre i dati in modo documentato**, non servire pagine. Disaccoppiare il frontend dal firmware permette di aggiornare l'interfaccia senza toccare la board — rilevante visto che l'OTA è fuori scopo (§1) — e lascia aperta la strada dell'integrazione diretta in Home Assistant. Il contenuto dell'HMI dipende inoltre da quali grandezze la board esporrà davvero, cosa che si stabilizza solo a hardware costruito.
- **Nessun vincolo hardware aggiuntivo:** entrambi i trasporti esistono già — **WiFi** sul nodo bridge (REQ-IF-003) e **USB** attraverso la scheda adattatrice del modulo (REQ-DIAG-002). Se il frontend è ospitato esternamente, la Flash della board non ne contiene gli asset e il budget di occupazione (§4.2) non è un vincolo dimensionante; se invece si sceglierà di servirlo dalla board, l'occupazione andrà verificata contro i 4 MB del modulo. **In nessuno dei due casi la decisione impatta il progetto hardware**, quindi può essere presa dopo.
- **Acceptance:** **[B]** i dati di configurazione e telemetria di tutti i nodi sono leggibili e scrivibili dall'esterno attraverso almeno uno dei due trasporti; la verifica di dettaglio è demandata alla specifica firmware/HMI.
- **Punti da risolvere nella specifica firmware/HMI:**
  - Se il frontend è ospitato su un'origine diversa (Home Assistant), il server della board deve gestire il **CORS**, altrimenti il browser blocca le chiamate.
  - L'accesso alla **porta seriale da una pagina web** richiede API browser disponibili solo su alcuni motori e in contesto sicuro: la via USB è praticabile senza riserve solo da un'applicazione locale, non necessariamente da un frontend nel browser.
  - Solo il **nodo bridge** ha WiFi; gli altri nodi restano raggiungibili unicamente attraverso di esso via CAN (REQ-IF-003).

**REQ-SW-003** (Software, Must, Confirmed)

- **Statement:** il protocollo applicativo su CAN shall essere **CANopen** (EN 50325-4, CiA 301), implementato tramite la libreria open source **CANopenNode**, e comprende: gestione NMT degli stati del nodo (Stopped, Pre-operational, Operational), Heartbeat e Node-Guarding per la supervisione, mappatura ID standard CANopen (11 bit, function code più Node-ID 1–127), PDO per lo scambio ciclico di I/O e SDO per configurazione e diagnostica.
- **Rationale:** CANopenNode è uno stack maturo con licenza permissiva, scritto in ANSI C, con porting già esistenti per ESP32 — riduce il rischio di dover scrivere e validare da zero un protocollo proprietario per una rete multi-nodo di schede identiche.
- **Pro:** protocollo standardizzato con tool di diagnostica esistenti (candump, PCAN-View); NMT e Heartbeat coprono nativamente la supervisione e il wake-up via bus richiesti da REQ-IF-002 e REQ-EL-006; il modulo **LSS (CiA 305)** permette l'assegnazione dinamica del Node-ID (vedi REQ-SW-004).
- **Contro:** overhead di RAM e flash superiore a un protocollo minimale custom; curva di apprendimento del framework (Object Dictionary, callback OD_); il bit-rate resta 125 kbit/s, compatibile con CANopen ma tra i più bassi standardizzati da CiA 301.
- **Acceptance:** il nodo raggiunge lo stato NMT Operational dopo il boot; Heartbeat periodico verificato su bus con analizzatore; comandi NMT Start/Stop/Reset applicati correttamente da un altro nodo della rete; almeno un PDO e un SDO scambiati correttamente con un tool CANopen standard.

**REQ-SW-004** (Software, Must, Confirmed)

- **Statement:** il Node-ID CANopen di ciascuna scheda shall essere assegnato **dinamicamente via bus tramite LSS (CiA 305)**; **nessun selettore fisico (DIP-switch o jumper)** per il Node-ID shall essere previsto sulla board. L'LSS address a 128 bit (Object 1018h: vendor-ID, product-code, revision-number, serial-number) shall usare come serial-number un identificativo hardware univoco già presente sul chip, senza necessità di programmazione dedicata in produzione.
- **Rationale:** elimina un componente meccanico e un passaggio di configurazione manuale in produzione e installazione, a favore di LSS Fastscan, già implementato in CANopenNode (`305/CO_LSSmaster.c`).
- **Implementazione proposta:** **Base MAC address** dell'ESP32-S3 (48 bit, programmato in fabbrica in eFuse BLK1, univoco per chip), letto via `esp_efuse_mac_get_default()`.
- **Pro:** zero hardware dedicato, nessun errore di configurazione da parte dell'installatore, Node-ID riassegnabile via bus in caso di sostituzione della scheda.
- **Contro dichiarati:** il Node-ID non è leggibile a vista sulla scheda, quindi serve un tool di diagnostica per sapere quale scheda fisica corrisponde a quale Node-ID — mitigabile esponendolo nella telemetria e nella HMI (REQ-DIAG-001, REQ-SW-002); richiede inoltre che il nodo bridge o un tool esterno implementi il ruolo di **LSS master** per lo scan e l'assegnazione iniziale.
- **Acceptance:** una scheda nuova, con LSS non configurato, collegata al bus viene rilevata dal master LSS tramite Fastscan e riceve un Node-ID valido senza intervento manuale; il Node-ID assegnato persiste al riavvio e resta leggibile via telemetria CAN.

**REQ-SW-005** (Software, Must, Confirmed)

- **Statement:** (a) il firmware shall abilitare un watchdog hardware che resetti l'MCU in caso di blocco, portando le uscite nello stato sicuro definito da REQ-SAFE-003; (b) la configurazione persistente del nodo (Node-ID assegnato via LSS, parametri di debounce, limiti di corrente dei motori, calibrazioni) shall essere salvata in memoria non volatile e sopravvivere a power-cycle e reset.
- **Rationale:** entrambi i meccanismi sono presupposti da REQ-SAFE-003 e dall'acceptance di REQ-SW-004. Su un nodo installato in un vano non accessibile, un blocco firmware senza watchdog richiede l'intervento fisico dell'utente, e una configurazione non persistente richiede una riassegnazione LSS a ogni power-cycle. Entrambi hanno costo hardware nullo, essendo watchdog e memoria non volatile integrati nell'MCU.
- **Acceptance:** un blocco software indotto artificialmente provoca il reset entro il timeout configurato, e le uscite restano disattivate durante il reset; dopo 10 power-cycle la configurazione persistente risulta invariata.

### 3.8 Ciclo di vita / Produzione

**REQ-LIFE-001** (Lifecycle, Must, Confirmed)

- **Statement:** il progetto shall essere dimensionato su un lotto di **massimo 20 esemplari**, con **assemblaggio in-house** e **popolamento on-demand** delle varianti. Il contenimento del costo unitario shall costituire un **criterio di selezione vincolante per ogni componente**, al pari di prestazioni e ingombro: a parità di soddisfacimento del requisito applicabile shall essere scelta l'opzione di costo inferiore, e ogni scelta di un componente più costoso dell'alternativa idonea shall essere accompagnata dalla motivazione tecnica che la rende necessaria. **Non è fissato un target numerico di costo**: il requisito è un criterio di scelta, non una soglia.
- **Rationale:** l'assemblaggio in-house elimina i costi di setup e di caricamento tipici della terziarizzazione, quindi il criterio di costo si concentra sul **prezzo dei componenti alle quantità effettivamente acquistate** — dove i tagli minimi di vendita possono rendere una parte "economica" più cara del previsto — e sul **numero di part number distinti** da approvvigionare e gestire a magazzino. Il popolamento on-demand valorizza pienamente la strategia di depopolazione già adottata su ingressi (REQ-IF-004) e uscite (REQ-IF-008): si assembla la parte comune e si popola la variante solo quando serve, senza mantenere varianti di BOM parallele né immobilizzare componenti.
- **Processo di assemblaggio (Confirmed):** stencil e pasta salda, **posizionamento manuale** dei componenti SMD, **saldatura a reflow**; i componenti through-hole (morsettiere di REQ-MECH-001, connettore JST PH di REQ-IF-012, eventuali header) vengono saldati a mano **dopo** il ciclo di reflow.
- **Vincoli di selezione che ne discendono:**
  - Il reflow gestisce nativamente i package **leadless (QFN/DFN)**, che non costituiscono quindi un ostacolo: il TMC2209 di REQ-IF-010 in QFN è compatibile con questo processo. Il vincolo riguarda i soli package **BGA**, da escludere perché non ispezionabili visivamente e non rilavorabili senza attrezzatura dedicata.
  - Il **posizionamento manuale** fissa invece un limite inferiore alle dimensioni: i passivi non dovrebbero scendere sotto 0603, e la convenzione **0805** di §3 è già coerente e va mantenuta anche dove un package più piccolo sarebbe elettricamente sufficiente.
  - Il layout dovrebbe concentrare i componenti SMD su **una sola faccia**, per evitare un secondo ciclo di reflow e il rischio di far cadere i componenti del primo lato.
- **Acceptance:** revisione della BOM prima del rilascio — ogni riga riporta l'alternativa più economica valutata e, se non selezionata, la motivazione tecnica; il conteggio dei part number distinti è documentato; nessun componente in package BGA e nessun passivo sotto 0603.
- **Applicazione del criterio:** ha già pesato su due scelte — MOSFET discreto anziché switch integrato "smart" sulle uscite (REQ-IF-008, circa un ordine di grandezza per canale su 4 canali) e sense di corrente unico anziché per canale (REQ-IF-011).
- **Rapporto con REQ-ENV-001:** con il range operativo ristretto a 0…+40 °C la scelta dei componenti si allarga sensibilmente a parità di costo. Resta però il vincolo sul range di **immagazzinamento** dei componenti più delicati, che REQ-ENV-001 impone di verificare e documentare: questo requisito non autorizza a ignorarlo per risparmiare.

### 3.9 Diagnostica & Osservabilità

**REQ-DIAG-001** (Diagnostics, Should, Confirmed)

- **Statement:** la scheda shall esporre: LED di stato pilotati dall'I/O expander (REQ-IF-015); test point su rail e segnali chiave (3V3, 5V motori, CAN-H/L, WAKEUP); telemetria via CAN delle correnti dei motori misurate da REQ-IF-011, dello stato di ingressi e uscite, e della causa dell'ultimo reset o wake.
- **Rationale:** una scheda installata in un vano camper dev'essere diagnosticabile da remoto, tramite Home Assistant, senza smontaggio.
- **Acceptance [B]:** tutti i valori di telemetria leggibili da HA con errore inferiore al 5%.
- **Nota ADC (criterio generale):** ogni segnale portato a un ingresso ADC dovrebbe restare **≤ 2,45 V** a fondo scala, non 3,3 V: sopra tale soglia l'ADC dell'ESP32-S3 con attenuazione 11 dB esce dal range ufficialmente caratterizzato per la calibrazione, con non-linearità residua maggiore (§7). Il criterio è già applicato al sense motori di REQ-IF-011 e vale come indicazione per il partitore esterno del modo (III-a) di REQ-IF-004.

**REQ-DIAG-002** (Diagnostics, Must, Confirmed)

- **Statement:** il firmware shall essere aggiornabile attraverso **tre canali**, di cui almeno uno remoto:
  - **(a) USB cablato** — tramite la **scheda adattatrice del modulo ESP32-S3-Tiny** collegata via cavo FPC; la scheda portante **non** shall prevedere convertitore USB-seriale proprio. È anche il canale del monitor seriale e del bring-up.
  - **(b) OTA su CANopen** — download del programma sul bus, che raggiunge **qualsiasi nodo**, compresi quelli senza WiFi.
  - **(c) OTA su WiFi** — disponibile sul **solo nodo bridge**.

  Il connettore FPC e i pulsanti BOOT/RESET dell'adattatore shall restare accessibili a scheda montata (REQ-MECH-002).
- **Rationale:** i nodi sono installati in vani poco accessibili, quindi un aggiornamento che richieda di raggiungere fisicamente la scheda è impraticabile su una rete di più unità. Il canale **(b)** è quello dirimente: solo il bridge ha WiFi, mentre gli altri nodi sarebbero altrimenti aggiornabili solo smontandoli. Il canale (a) resta necessario per il primo flash e per il recupero da un'immagine corrotta.
- **Conseguenza hardware — budget di Flash:** l'OTA richiede **due partizioni applicative** più le aree di sistema, quindi impegna la maggior parte dei **4 MB** del modulo (§4.2). È il vincolo dimensionante che l'OTA introduce, e va tenuto presente insieme alla scelta di REQ-SW-002: **se il frontend Vue venisse servito dalla board**, i suoi asset competerebbero per lo stesso spazio e i 4 MB diventerebbero verosimilmente insufficienti. Ospitare il frontend esternamente rende invece le due esigenze compatibili.
- **Acceptance:** **[B]** (a) flash completo e monitor seriale su scheda montata, senza modifiche hardware, con reset azionabile senza power-cycle; (b) aggiornamento completo di un nodo non-bridge attraverso il solo bus CAN, con ripristino automatico dell'immagine precedente se la nuova non si avvia; (c) aggiornamento del bridge via WiFi con la stessa garanzia di rollback.
- **Fattibilità di (b) — stima di durata:** su CAN a 125 kbit/s (REQ-IF-001) un frame standard con 8 byte di dati occupa ~1 ms, e un trasferimento a blocchi porta 7 byte utili per frame, cioè **~5–6 kB/s** al netto di riscontri e traffico concorrente. Un'immagine applicativa dell'ordine di 1,5 MB richiede quindi **circa 5 minuti**: lungo ma pienamente praticabile per un aggiornamento occasionale. Il bit-rate basso non pregiudica questa funzione.
- **Punti da risolvere nella specifica firmware:**
  - Meccanismo di download su CANopen: lo standard prevede oggetti dedicati al trasferimento del programma (CiA 302-3), coerenti con lo stato "download firmware in corso" già previsto dal LED RUN di REQ-IF-013. Da verificare il supporto nella versione di CANopenNode adottata.
  - Per il canale (c), se si intende l'OTA **nativa di ESPHome** occorre valutarne la convivenza con lo stack CANopen e con ESP-IDF; l'alternativa è l'OTA standard di ESP-IDF su WiFi, funzionalmente equivalente e senza vincoli di framework.
  - Politica di **rollback e watchdog di avvio**, che si appoggia al watchdog di REQ-SW-005.

## 4. Microcontrollore — scelta e motivazioni

**Decisione: ESP32-S3**, integrato come modulo preassemblato **Waveshare ESP32-S3-Tiny** montato sulla scheda portante, anziché come modulo WROOM-1 saldato direttamente.

### 4.1 Perché ESP32-S3 e non RP2040

| Criterio | RP2040 | ESP32-S3 |
|---|---|---|
| Controller CAN | Assente in hardware: serve un controller SPI esterno (MCP2515/MCP2518FD) oppure can2040 via PIO (software) | **TWAI integrato** (ISO 11898-1): serve solo il transceiver |
| WiFi/BT (ruolo bridge) | Assente: servirebbe un modulo esterno, la scheda non sarebbe più identica | Nativo |
| Deep-sleep (chip) | ~180 µA in dormant | ~7 µA |
| ADC | 4 canali, 12 bit, non-linearità note | Non-linearità note; entrambi richiedono calibrazione o ADC I²C esterno per precisione |
| Costo e reperibilità | Ottimi | Ottimi |

1. Il requisito di **rete di schede identiche con un nodo bridge WiFi** (REQ-IF-003) è dirimente: con RP2040 il WiFi richiederebbe un modulo radio esterno, annullando il vantaggio di semplicità.
2. **Semplificazione hardware CAN**: il TWAI integrato elimina controller esterno e bus SPI dedicato; can2040 su RP2040 funziona ma consuma PIO e CPU e non offre filtraggio hardware dei frame, rilevante su un bus multi-nodo.
3. I **consumi in sleep** non sono stati determinanti: con il budget portato a 1 mA (REQ-EL-005) anche l'RP2040 rientrerebbe. L'argomento è marginale rispetto ai due precedenti.

**Contro dichiarati della famiglia ESP32-S3:** assorbimento in *running* più alto dell'RP2040 (mitigabile con radio spenta sui nodi non-bridge e light-sleep tra gli eventi); ADC mediocre (mitigabile con partitori calibrati o ADC esterno su I²C); toolchain meno minimale.

### 4.2 Perché un modulo preassemblato e non il WROOM-1 saldato

**Motivazione:** semplificazione del PCB e dell'assemblaggio (REQ-LIFE-001). Il modulo porta a bordo alimentazione, oscillatore, antenna e circuito di boot già validati, riducendo il numero di componenti da posizionare a mano e le sezioni critiche di layout.

**Caratteristiche del modulo** (fonte: wiki ufficiale Waveshare, §7):

- SoC **ESP32-S3FH4R2**, dual-core LX7 a 240 MHz, **4 MB Flash e 2 MB PSRAM in package**, 512 KB SRAM, 16 KB RTC SRAM.
- **34 GPIO multifunzione** portati sui pin del modulo.
- Ingombro ~23,5 × 18 mm.
- **Design separato**: USB Type-C e pulsanti BOOT/RESET stanno su una **scheda adattatrice distinta**, collegata al modulo con un **cavo FPC a 8 pin**. Sul modulo non c'è quindi il connettore USB.

**Conseguenze sui requisiti**, tutte recepite nei rispettivi testi: il primo flash e il debug passano dalla scheda adattatrice USB del modulo (REQ-DIAG-002); la keep-out di antenna diventa un vincolo sulla scheda portante (REQ-MECH-002); i **4 MB di Flash** sono il vincolo da sorvegliare: l'OTA a doppia partizione richiesta da REQ-DIAG-002 ne impegna la maggior parte, quindi restano compatibili solo se il frontend Vue è ospitato esternamente (REQ-SW-002).

**Rischio residuo del modulo:** il regolatore di bordo e il LED RGB su GPIO 14 assorbono corrente a riposo, e il produttore non ne dichiara il valore. In **OFF** la questione non si pone, perché il power-latch disalimenta anche il modulo; in **deep-sleep** il LED RGB va misurato contro il budget di REQ-EL-005 e, se necessario, dissaldato. Il range di temperatura del SoC non è invece critico con il range operativo ristretto di REQ-ENV-001; il modulo rientra però fra i componenti per cui quel requisito impone di verificare e documentare anche il range di immagazzinamento.

### 4.3 Bilancio dei GPIO e necessità dell'I/O expander

Conteggio delle funzioni sui **34 GPIO** portati dal modulo:

| Funzione | Req. | GPIO |
|---|---|---|
| Ingressi configurabili | REQ-IF-004 | 5 |
| Uscite di potenza (PWM) | REQ-IF-008 | 4 |
| Driver stepper TMC2209 (STEP, DIR, EN, UART, DIAG) | REQ-IF-010 | 5–6 |
| PWM servo | REQ-IF-010 | 2 |
| Sense corrente motori (ADC1) | REQ-IF-011 | 1 |
| CAN (TX, RX, STB) | REQ-IF-001/002 | 3 |
| I²C (SDA, SCL) | REQ-IF-012 | 2 |
| LED CANopen RUN/ERR | REQ-IF-013 | 2 |
| LED di stato generici | REQ-DIAG-001 | 1 |
| Enable dei load-switch | REQ-EL-004 | 3 |
| Power-hold | REQ-EL-006 | 1 |
| Ingresso WAKEUP (RTC) | REQ-IF-007 | 1 |
| **Totale richiesto** | | **30–31** |

Dai 34 pin disponibili vanno però sottratti quelli **non liberamente assegnabili**: due impegnati dall'USB nativo verso la scheda adattatrice del modulo, uno dal LED RGB di bordo (GPIO 14), e tre o quattro **pin di strapping** che REQ-SAFE-003 esclude per uscite e LED. Il margine reale scende quindi **a zero o sotto zero**.

**Conclusione: l'I/O expander è necessario, non opzionale.** Spostando su di esso i 3 LED e i 3 enable dei load-switch — funzioni lente, senza vincoli di temporizzazione né di sicurezza attiva — il fabbisogno diretto sull'MCU scende a **24–25 GPIO**, con un margine di 5–6 pin per riserve e per gli imprevisti di layout. Il costo è un solo integrato e nessun GPIO aggiuntivo, perché il bus I²C è già richiesto da REQ-IF-012. Il requisito è formalizzato in **REQ-IF-015**.

Restano volutamente su GPIO diretti dell'MCU tutte le funzioni con vincoli temporali (PWM delle uscite e dei servo, STEP/DIR dello stepper, CAN) e quelle di sicurezza (power-hold, WAKEUP), che non devono dipendere dalla disponibilità del bus I²C.

## 5. Open Points

**Nessun punto aperto.** Tutte le domande emerse in fase di stesura sono state decise e le relative motivazioni sono assorbite nei requisiti; gli scarti rispetto alle ipotesi iniziali sono documentati come esclusioni o rinunce esplicite nei requisiti che li riguardano, e le assunzioni ancora non verificate sono raccolte in §6.

I punti che restano da chiudere non sono decisioni ma **verifiche**, tutte demandate alla fase di schematico o alla specifica firmware e già indicate nei rispettivi requisiti: il consumo a riposo del modulo MCU in deep-sleep (REQ-EL-005), la misura di stallo dei servo (REQ-EL-007), il range di immagazzinamento dei componenti più delicati (REQ-ENV-001), il supporto degli oggetti CiA 302-3 in CANopenNode (REQ-DIAG-002) e la tabella di allocazione dei pin (§4.3).

## 6. Registro delle assunzioni

| REQ | Assunzione | Perché |
|---|---|---|
| REQ-EL-010 | Rating ≥ 40 V su tutta la catena di ingresso | Fissato dall'utente per contenere costo, ingombro e RDS(on) rispetto a una catena a 60 V, dopo l'eliminazione della variante 24 V dal progetto |
| REQ-EL-003 | Applicabilità dei soli pulse brevi (1, 2a, 3a/3b), con esclusione del load dump pulse 5a/5b | Decisione utente: bus servizi separato dal bus motore e batteria permanentemente connessa che agisce da clamp; lo standard consente di omettere i pulse non pertinenti alla connessione del dispositivo. Rischio residuo dichiarato: propagazione del load dump attraverso il DC-DC di ricarica da alternatore |
| REQ-EL-005 | Deep-sleep ≤ 1 mA (Confirmed); OFF ≤ 100 µA (Assumed) | Il valore di deep-sleep è una decisione utente, verificata sul bilancio di 10 nodi su batteria 300 Ah (~2,4%/mese, stesso ordine di autoscarica e BMS); il budget OFF è una stima da congelare sul componente di latch |
| REQ-EL-007 | Picco servo: SG90 ~500–700 mA, MG90S fino a ~1,5 A; servo fermo in tenuta ≤ 300 mA; rail ≥ 2,5 A con non contemporaneità | Fonti divulgative su cloni generici, non datasheet ufficiali. Valore congelato per decisione utente assumendo un solo servo in movimento; misura di verifica sui pezzi acquistati ancora consigliata prima dell'ordine dei componenti di potenza |
| REQ-EL-009 | Beneficio di rumore atteso dalla topologia high-side | Il requisito di separazione delle masse è confermato; resta teorica la stima del guadagno rispetto alla soluzione low-side, da confermare a layout e misura |
| REQ-EL-010 | Guasto hard della sorgente di carica escluso dal design basis; sgancio BMS in alta corrente non caratterizzato sul TVS | Decisione esplicita dell'utente: criterio a singolo guasto per progetto non certificato; dati di induttanza di loop e turn-off del BMS non disponibili |
| REQ-IF-004 (I) | Variante (I) = contatto locale, mai esposto a 12 V esterni | Interpretazione dell'indicazione utente. Il rischio residuo è comunque coperto: l'utente ha deciso la protezione uniforme su tutte le varianti (REQ-IF-006), quindi il vincolo d'uso non è più l'unica barriera |
| REQ-IF-004 (III) | Partitore a carico del dispositivo esterno nel modo in tensione; eccitazione a bordo e sezionabile nel modo resistivo per NTC | La board non ipotizza rapporti per sensori in tensione non noti, ma deve fornire l'eccitazione ai sensori passivi. Consumo dell'eccitazione da contenere entro REQ-EL-005 e resistore di protezione di REQ-IF-006 da includere nel calcolo |
| REQ-IF-015 | I/O expander a 8 bit per LED ed enable dei load-switch | Necessario dal bilancio GPIO di §4.3, che senza expander non chiude con margine sui 34 pin del modulo |
| §4.2 | Modulo ESP32-S3-Tiny al posto del WROOM-1 saldato | Decisione utente per semplificare PCB e assemblaggio. Il consumo a riposo del modulo non è dichiarato dal produttore: irrilevante in OFF, dove il power-latch lo disalimenta, da verificare in deep-sleep per il solo LED RGB |
| REQ-MECH-001/003 | PCB 100 × 100 mm, fori M3, angoli smussati, contenitore stampato in PETG; morsettiere sui bordi e JST XH in parallelo sugli ingressi | Decisione utente. JST non produce una serie a 2,54 mm: adottata la XH a 2,5 mm, da correggere se l'intenzione era uno strip di pin |
| REQ-IF-005 | Pull-up esterno ~10 kΩ | Costante RC e debounce firmware sono confermati; resta da congelare il valore del pull-up, che dipende anche dal resistore serie di REQ-IF-006. Il pull-up interno ESP32-S3 (~45 kΩ) ha tolleranza larga e penalizza il tempo di risposta sui finecorsa |
| REQ-IF-008 | PWM 1,5–2 kHz confermato | Interpretazioni secondarie di IEEE 1789 (soglia ~1250 Hz), non il testo dello standard. Rischio di fischio in banda udibile esplicitamente accettato dall'utente; la frequenza resta configurabile per canale |
| REQ-IF-008 | Topologia high-side con P-MOSFET discreto e level-shifter | Decisione utente: beneficio di sicurezza sul corto a massa telaio, e discreto anziché switch integrato per margine PWM e costo. Il clamp Zener gate-source non è opzionale, dato che a 16 V la V_GS è già prossima al limite |
| REQ-IF-011 | Sense motori su ADC1, mai su ADC2; attribuzione della battuta da esclusività dei servo e offset noto dello stepper | ADC2 non affidabile con WiFi attivo su ESP32-S3, e la board è identica su tutti i nodi. Il sense singolo è una decisione utente: vale finché resta il vincolo di non contemporaneità di REQ-SW-001 |
| REQ-IF-012 | JST PH 2,0 mm a 4 pin, ordine Qwiic-like, senza compatibilità fisica Qwiic/STEMMA-QT | Passo e ordine dei segnali decisi dall'utente; l'ordine identico a Qwiic rende l'adattatore un semplice cambio di connettore pin-a-pin. Nessun segnale di interrupt previsto |
| REQ-IF-014 | Protezione delle linee CAN ottenuta per selezione del transceiver anziché con componenti dedicati | Verificato sul datasheet TJA1042: ±8 kV IEC 61000-4-2, ±58 V sui pin di bus e immunità ai pulse ISO 7637-2. Vale finché resta questo transceiver; con un alternativo i footprint predisposti vanno popolati |
| REQ-MECH-003 | Rating morsettiera 2,54 mm ~6 A, cavo 18–26 AWG, sufficiente per CAN e ingressi | *Fonte debole*: schede prodotto di rivenditori generici, nessun datasheet di produttore reperito; da verificare sul part number di BOM. Il ramo critico, l'alimentazione board, è stato portato a 5,08 mm e non dipende più da questo dato |
| REQ-ENV-001 | Operativo 0…+40 °C, vano interno e non vano motore; sopravvivenza non fissata a priori | Range operativo per decisione utente; la verifica è solo documentale. Il range di sopravvivenza si ricava dal minimo comune dei rating di storage dei componenti più delicati, annotato in BOM |
| REQ-SAFE-001 | PTC sulla sola board, protezione carichi a monte | Decisione utente. Rischio residuo: se il quadro del camper non ha un fusibile sul ramo del carico, piste e morsettiera di uscita restano esposte |
| REQ-DIAG-001 | Set di telemetria; criterio generale Vmax ≤ 2,45 V sugli ingressi ADC | Derivato dalla pratica HMI del progetto; la soglia mantiene l'ADC nel range caratterizzato dell'attenuazione 11 dB, senza costo aggiuntivo. Il sense di tensione batteria è escluso per decisione utente (curva LFP piatta, protezione delegata al BMS) |
| REQ-DIAG-002 | Tre canali di aggiornamento, con l'OTA su CANopen come unica via remota per i nodi senza WiFi | Decisione utente. La durata stimata del trasferimento su CAN a 125 kbit/s (~5 min per 1,5 MB) è calcolata, non misurata; il supporto degli oggetti CiA 302-3 nella versione di CANopenNode adottata è da verificare |

## 7. Fonti

**MCU e periferiche**

- ESP32-S3 (deep-sleep ~7 µA, TWAI ISO 11898-1, pull-up interno ~45 kΩ, rating GPIO −0,3…3,6 V): [ESP32-S3 Series Datasheet, Espressif](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf); consumi reali su devkit: [lucidar.me](https://lucidar.me/en/esp32/power-consumption-of-esp32-s3-devkitm-1/)
- RP2040, dormant ~180 µA (datasheet §5.7): [RP2040 Datasheet](http://academy.cba.mit.edu/classes/embedded_programming/RP2040/RP2040.pdf); [Raspberry Pi Forums](https://forums.raspberrypi.com/viewtopic.php?t=316458)
- can2040 (CAN 2.0B via PIO su RP2040, fino a 1 Mbit/s): [Hackster.io](https://www.hackster.io/news/kevin-o-connor-s-can2040-brings-a-pio-powered-can-bus-to-the-raspberry-pi-pico-other-rp2040-boards-2caf05c0808d)
- ADC ESP32-S3, canali ADC1/ADC2: [ESP-IDF, Analog to Digital Converter](https://docs.espressif.com/projects/esp-idf/en/v4.4/esp32s3/api-reference/peripherals/adc.html); non-linearità e calibrazione: [Espressif Developer Blog](https://developer.espressif.com/blog/2025/08/adc-performance/), [ESP-IDF ADC Calibration Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc_calibration.html); range consigliato per attenuazione 11 dB (150–2450 mV): [ESP32 Forum](https://www.esp32.com/viewtopic.php?t=23902); ADC2 non affidabile con WiFi attivo: [ESP32 Forum](https://esp32.com/viewtopic.php?t=44885), [arduino-esp32 Issue #440](https://github.com/espressif/arduino-esp32/issues/440)
- Base MAC address in eFuse BLK1, univoco di fabbrica: [ESP-IDF, Miscellaneous System APIs](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/misc_system_api.html)
- Proprietà termiche dei filamenti da stampa 3D (PETG: transizione vetrosa ~80 °C, stabile fino a ~70 °C; PLA, scartato: ~60 °C e servizio continuo 45–55 °C), riferimento per REQ-MECH-001: [3D Solved — Is PLA heat resistant?](https://3dsolved.com/is-pla-heat-resistant-abs-asa-petg-and-more/); [Sovol — PLA vs PETG vs ASA for outdoor printing](https://www.sovol3d.com/blogs/news/pla-vs-petg-vs-asa-for-outdoor-3d-printing-which-is-best) *(fonti divulgative e commerciali di settore, valori concordanti fra loro ma non da scheda tecnica di un singolo filamento)*
- Modulo Waveshare ESP32-S3-Tiny — SoC ESP32-S3FH4R2 con 4 MB Flash e 2 MB PSRAM in package, 34 GPIO, design separato con USB e pulsanti su scheda adattatrice via FPC 8 pin, LED RGB su GPIO 14: [Waveshare Wiki — ESP32-S3-Tiny](https://www.waveshare.com/wiki/ESP32-S3-Tiny) *(documentazione ufficiale del produttore del modulo; range di temperatura e assorbimento a riposo non dichiarati dal produttore)*

**CAN e CANopen**

- TJA1042 (standby con bus wake-up, VIO 3–5 V, sistemi 12/24 V; sui pin CANH/CANL: ESD ±8 kV IEC 61000-4-2, tensione ammessa −58…+58 V, immunità ai pulse ISO 7637-2 1/2a/3a): [Datasheet NXP Rev. 11](https://www.nxp.com/docs/en/data-sheet/TJA1042.pdf) *(datasheet ufficiale di produttore)*
- CANopenNode (stack ANSI C, EN 50325-4 / CiA 301): [GitHub](https://github.com/CANopenNode/CANopenNode); porting ESP32 esistenti: [CANopenNode_ESP32](https://github.com/sicrisembay/CANopenNode_ESP32), [CANopenESP32](https://github.com/Wizcat22/CANopenESP32)
- CiA 303-3, indicatori LED RUN/ERR e pattern di flash: [CiA 303 Part 3 v1.4.0](https://forum.opencyphal.org/uploads/short-url/uitNY0mIOaAZisD7dk05So1ntiy.pdf); implementazione di riferimento: [modulo CO_LEDs](https://canopennode.github.io/CANopenNode/group__CO__LEDs.html)
- CiA 305, Layer Setting Services e assegnazione dinamica del Node-ID: [CAN in Automation](https://www.can-cia.org/can-knowledge/cia-305-layer-setting-services-lss); [CO_LSSmaster.c](https://github.com/CANopenNode/CANopenNode/blob/master/305/CO_LSSmaster.c); [tutorial LSS](https://canopennode.github.io/md_tutorial_2LSS.html)

**Alimentazione e protezioni**

- Protezione da inversione di polarità (Schottky sotto 2 A, MOSFET oltre): [Diotec App Note](https://diotec.com/en/application/application-notes/application-note-about-automotive-load-dump-protection.html); [TI SLVAE57B, Basics of Ideal Diodes](https://www.ti.com/lit/an/slvae57b/slvae57b.pdf)
- Transitori ISO 7637-2, load dump e TVS asimmetriche: [Littelfuse](https://www.littelfuse.com/assetdocs/littelfuse-tvs-diode-meet-automotive-load-dump-standard-application-note?assetguid=a53ad6b0-87f7-4ca3-a783-55133fc020dc); [Analog Devices, Robust Automotive Supply Protection](https://www.analog.com/en/resources/technical-articles/low-quiescent-current-surge-stopper-robust-automotive-supply-protection.html)
- Livelli di load dump su bus 12 V (~101 V) senza soppressione centralizzata: [Microchip AN DS00006186](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ApplicationNotes/ApplicationNotes/Automotive-Cold-Crank-Load-Dump-Standards-DS00006186.pdf)
- ISO 7637-2:2004 — struttura dei pulse di immunità (5.6.1–5.6.4 pulse 1/2a/2b/3a/3b/4, 5.6.5 pulse 5a/5b di load dump), resistenza opzionale Rv 0,7–40 Ω per i soli pulse 5, e facoltà di omettere i pulse non pertinenti alla connessione del dispositivo (§4.1): [estratto ufficiale ISO 7637-2:2004](https://cdn.standards.iteh.ai/samples/28533/685012e1e8cd46859debd063adc725da/ISO-7637-2-2004.pdf) *(anteprima ufficiale ISO: contiene scopo, procedura e struttura delle prove; le tabelle numeriche dei singoli pulse non sono incluse nell'estratto e non sono state consultate direttamente)*
- Distinzione tra V_RWM e V_C nella selezione di un TVS: [Diodes Incorporated, AN1142](https://www.diodes.com/assets/App-Note-Files/TVS-in-Automotive-Applications.pdf)
- Valori V_RWM / V_C / I_PP della famiglia TVS SMBJ 600 W usati nel dimensionamento di REQ-EL-010 (SMBJ24A: V_C 38,9 V a 15,5 A su 10/1000 µs e 50,6 V a 77,5 A su 8/20 µs; SMBJ30A: 48,4 V; SMBJ40A: 64,5 V): [Bourns, SMBJ Transient Voltage Suppressor Diode Series](https://www.bourns.com/docs/product-datasheets/smbj.pdf) *(datasheet ufficiale di produttore)*
- Range di tensione LiFePO4 12 V (4S, 10,0–14,6 V) e curva di scarica piatta: [Renogy](https://www.renogy.com/blogs/general-solar/lifepo4-voltage-chart); [PowMr](https://powmr.com/blogs/news/lifepo4-voltage-chart-and-soc)
- Autoscarica LiFePO4 (~1–3%/mese) e quiescente del BMS come termine di confronto per il budget di deep-sleep di REQ-EL-005 (esempio citato: BMS da 3 mA ⇒ 2,16 Ah/mese, contributo pari o superiore all'autoscarica chimica): [Anern — LiFePO4 Battery Storage: Stop Parasitic Drain](https://www.anernstore.com/blogs/portable-solar-power/lifepo4-self-discharge-storage-myths); [Ufine — Li-ion Battery Self-Discharge](https://www.ufinebattery.com/blog/battery-self-discharge-li-ion-battery-self-discharge-rate/) *(fonti commerciali/divulgative di produttori: valori concordanti tra loro ma non da studio indipendente né da datasheet di cella)*
- Spike da apertura del BMS durante la carica (~17,2 V osservato su impianto Magnum Energy MS2000 con batterie LFP): [DIY Solar Power Forum](https://diysolarforum.com/threads/voltage-spike-caused-by-bms-disconnecting.12443/) *(fonte aneddotica da forum utenti, non uno studio né un datasheet)*

**Uscite di potenza e layout**

- High-side contro low-side, sicurezza sul corto a massa: [Next Electronics](https://www.next.gr/tutorials/transistors-and-fets/high-side-vs-low-side-switching-explained-tutorial) *(tutorial divulgativo)*; [Elektor Magazine](https://www.elektormagazine.com/articles/high-side-low-side-switching) *(rivista di settore)*
- Frequenza PWM massima degli switch integrati automotive, calcolata dai tempi di turn-on/turn-off: [Infineon Developer Community](https://community.infineon.com/t5/Smart-Power-Switches/What-is-the-maximum-PWM-frequency-that-can-be-used-with-any-specific-PROFET/td-p/445869) *(risposta di moderatore Infineon, non datasheet)*; famiglie candidate: [Infineon PROFET+2 12V](https://www.infineon.com/products/power/smart-power-switches/high-side-switches/12v/profet-plus-2-12v-automotive); [TI TPS1HB16-Q1](https://www.ti.com/product/TPS1HB16-Q1); [TI TPS1H100-Q1](https://www.ti.com/product/TPS1H100-Q1)
- Gate drive di N-MOSFET high-side a duty cycle prossimo al 100%: [TI SLVA444](https://www.ti.com/lit/an/slva444/slva444.pdf)
- Confronto P-channel contro N-channel (RDS(on) e costo): [Power Electronics News](https://www.powerelectronicsnews.com/comparing-n-channel-and-p-channel-mosfets-which-is-best-for-your-application/) *(divulgativa di settore)*; opzioni P-channel AEC-Q101: [Vishay](https://www.vishay.com/docs/49552/49552.pdf)
- Frequenza PWM e flicker LED (*interpretazioni secondarie di IEEE 1789; lo standard non è stato consultato direttamente*): [Tecolite](https://tecolite.com/pwm-frequency-led-flicker/) *(commerciale)*; [AZoM](https://www.azom.com/article.aspx?ArticleID=14729) *(divulgativa)*; [Waveform Lighting](https://www.waveformlighting.com/film-photography/an-introduction-to-flicker-free-led-strip-dimming) *(blog di produttore)*
- Separazione massa potenza/segnale su schede miste: [TI SLVA959B, Best Practices for Board Layout of Motor Drivers](https://www.ti.com/lit/an/slva959b/slva959b.pdf); [AllPCB, Effective Grounding Strategies](https://www.allpcb.com/allelectrohub/effective-grounding-strategies-a-beginners-guide-to-quieting-your-pcb-layout) *(divulgativa, corroborata dall'app note TI)*
- Relè di canale variante (II), TE Axicom IM06 — coil data, finestra di bobina, contatti 2 A/60 W, versione "D" 5 A: [TE, IM Series datasheet 108-98001 Rev. K](https://www.farnell.com/datasheets/477186.pdf) *(datasheet ufficiale)*; divieto di parallelo dei contatti per aumentare la portata: [Omron, FAQ relè](https://components.omron.com/us-en/faq/relays/FAQE10056) *(documentazione ufficiale di produttore)*; [NAVSEA SD-18, Relays](https://www.navsea.navy.mil/Portals/103/Documents/NSWC_Crane/SD-18/PDFs/Products/Archive/Relays/Relays.pdf) *(guida di affidabilità militare)*

**Motori e sensori**

- TMC2209 (2 A RMS / 2,8 A di picco, StallGuard4): [Datasheet Analog Devices/Trinamic rev. 1.09](https://www.analog.com/media/en/technical-documentation/data-sheets/tmc2209_datasheet_rev1.09.pdf)
- Modifica bipolare del 28BYJ-48: [Ardufocus](https://ardufocus.com/howto/28byj-48-bipolar-hw-mod/); [Coeleveld, PDF](https://coeleveld.com/wp-content/uploads/2016/10/Modifying-a-28BYJ-48-step-motor-from-unipolar-to-bipolar.pdf) *(misure dirette, limite ~100 mA/fase)*; [Jangeox](http://www.jangeox.be/2013/10/change-unipolar-28byj-48-to-bipolar.html) — *tutte fonti hobbistiche: procedura affidabile, dato di coppia da verificare sul motore reale*
- SG90 e MG90S (stallo, coppia, footprint): [Zbotic](https://zbotic.in/mg90s-vs-sg90-torque-accuracy-best-uses-compared/); [Kpower](https://www.kpower.com/insight_bldc/7870.html/); [Components101](https://components101.com/motors/mg90s-metal-gear-servo-motor) — *fonti divulgative e commerciali, dati di corrente non da datasheet ufficiale, con variabilità dichiarata*

**Connettori**

- JST PH 2,0 mm (~2 A/contatto con AWG24): [JST, PH connector](https://www.jst.com/products/crimp-style-connectors-wire-to-board-type/ph-connector/); [ePH-H datasheet](https://www.jst.com/wp-content/uploads/2021/01/ePH-H.pdf) *(documentazione ufficiale JST)*; confronto PH contro SH: [Keszoox](https://keszoox.com/blogs/news/jst-ph-vs-sh-connector-guide) *(commerciale)*
- Morsettiere a vite per PCB, passo minimo commerciale 2,54 mm: [SOS electronic / TE Connectivity](https://www.soselectronic.com/en-us/articles/te-connectivity/the-smallest-screw-terminals-for-the-most-common-solutions-2530) *(articolo di distributore, non datasheet)*; rating 5,08 mm, 10 A (UL) / 15 A (IEC): [RS PRO datasheet](https://docs.rs-online.com/20ee/A700000007927568.pdf); rating 2,54 mm ~6 A a 150 V per 18–26 AWG: dato ricorrente su schede prodotto di rivenditori generici *(**fonte debole**, da verificare sul part number di BOM)*

## 8. Storico revisioni

| Data | Modifica | Motivo |
|---|---|---|
| 2026-08-01 | **Rev. B — stadio uscite.** REQ-EL-001: range operativo rialzato a **10–16 V**, banda 9–10 V declassata a «nessun danno». REQ-IF-008: variante (II) a relè portata a **2 A** con TE Axicom IM06 (sostituisce l'HFKW da 10 A); carichi oltre 2 A e motori DC demandati a **relè esterni** comandati dalla scheda. REQ-IF-009/SAFE-002: variante (III) a interlock on-board eliminata, inversione realizzata dal cablaggio dei contatti dei relè esterni, con schema di installazione come documento obbligatorio. Economizzatore PWM di bobina eliminato (la finestra IM06 chiude per datasheet). Dettagli e razionali in [`04b-relay-output-stage.md`](hardware/schematics/04b-relay-output-stage.md) rev. B. | Decisioni utente: a 9 V la batteria servizi è esausta e la piena funzionalità non ha valore d'uso; il profilo reale dei carichi di canale è a bassa corrente e i carichi pesanti passano da relè esterni. |
| 2026-07-28 | **Rev. A — prima versione consolidata.** Assorbe in un unico documento l'intera cronologia decisionale precedente. Contenuti portanti: alimentazione 12 V con supporto obbligatorio di piombo e LiFePO4 (REQ-EL-001); catena di ingresso a 40 V con clamp e impedenza serie dimensionati sullo sgancio del BMS (REQ-EL-003/010); due stati a basso consumo, OFF e deep-sleep, con power-latch comandato da WAKEUP (REQ-EL-005/006); 5 ingressi e 4 uscite configurabili per depopolazione, con uscite MOSFET high-side in PWM a 1,5–2 kHz (REQ-IF-004/008); sezione motori con TMC2209, servo non contemporanei e sense di corrente unico (REQ-EL-007, REQ-IF-010/011); protocollo CANopen via CANopenNode, Node-ID assegnato via LSS e LED di stato CiA 303-3 (REQ-SW-003/004, REQ-IF-013); microcontrollore ESP32-S3 come modulo Waveshare ESP32-S3-Tiny, con I/O expander I²C reso necessario dal bilancio dei GPIO (§4, REQ-IF-015); PCB entro 100 × 100 mm su contenitore stampato in PETG, con morsettiere sui bordi e JST in parallelo sugli ingressi (REQ-MECH-001/003); aggiornamento firmware su USB, OTA CANopen e OTA WiFi (REQ-DIAG-002); lotto di 20 pezzi con assemblaggio in-house a posizionamento manuale e reflow, e contenimento del costo come criterio vincolante di selezione (REQ-LIFE-001). Introdotte la convenzione BOM sui package e la convenzione di verifica [B]/[D], che sostituisce le acceptance di qualifica di laboratorio non eseguibili nel perimetro del progetto. Le domande aperte residue sono state tutte decise e assorbite nei requisiti: alla chiusura della revisione **non restano punti aperti** (§5). | Consolidamento richiesto dall'utente, con revisione redazionale, verifica di over-engineering, completamento delle lacune di specifica e compressione dello storico in una voce unica. Le decisioni di dettaglio e le loro motivazioni sono nei singoli requisiti e nel registro delle assunzioni; gli scarti rispetto alle ipotesi iniziali — variante 24 V, sense di tensione batteria, load-switch sui LED, sense di corrente per canale — sono documentati come esclusioni esplicite nei requisiti che li riguardano. |
