# Caravantic — scheda elettrica: requisiti

Status: **Draft** · Derivato da [`../docs/frd.md`](../docs/frd.md) (divisione in due PCB, 2026-10-26). Contesto, requisiti comuni, riuso da `old/` e storico revisioni restano nel FRD comune. Scheda sorella: [`../idraulica/frd.md`](../idraulica/frd.md).

**Perimetro (Confirmed, utente 2026-10-26):** shunt, inverter, relè globale. Il **relè globale** non era nel FRD precedente: requisiti da scrivere (vedi §3, NEW-2). L'assegnazione dei singoli REQ a questa scheda è **Assumed** (da rivedere insieme).

Stato: Confirmed = dichiarato dall'utente · Assumed = ipotesi da confermare · Open = non risolto.

## 1. Requisiti

### 1.1 Elettrici

**REQ-EL-006** (Must, Confirmed) — **Scheda elettrica (Confirmed, utente 2026-10-26).** 2 ingressi digitali 12 V **opto-isolati**:
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

**REQ-EL-009** (Must, Confirmed) — **IN-AUX1 sulla scheda elettrica, IN-AUX2 sulla scheda idraulica (utente 2026-10-26: «uno per scheda», proposta accettata); stesso circuito replicato, stessi requisiti.** 2 ingressi digitali generici di riserva **IN-AUX1, IN-AUX2**, opto-isolati, **configurabili per canale con jumper a saldare** (Confirmed, utente 2026-10-15):
- **Modo H, attivo a 12 V:** come REQ-EL-006. Attivo con ingresso ≥ 8 V; inattivo con ingresso ≤ 2 V o aperto.
- **Modo L, attivo a massa:** la catena del LED è alimentata dal **+12 V batteria protetto della board** (Confirmed) e l'ingresso la chiude verso massa (contatto pulito o open-collector). Attivo con ingresso ≤ 2 V verso massa; inattivo con ingresso aperto o ≥ V_board − 2 V (Assumed).
- I jumper escono dalla fabbrica **aperti**: il canale non funziona finché non viene configurato (Confirmed). Una configurazione errata *shall* non danneggiare nulla.
- Stessa rete e stesso optoaccoppiatore di REQ-EL-006 (TLP293 GB, ritorno su massa della board), tempo di risposta ≤ 100 ms.
- Corrente assorbita a ingresso attivo ≤ 1,5 mA per canale, in entrambi i modi (Confirmed). Nel modo L è prelevata dalla batteria servizi.
- Immunità ai transitori: REQ-EL-008, applicato in entrambi i modi (uso generico, quindi caso peggiore lato alternatore).

*Rationale:* ingressi di riserva per segnali non ancora noti, che possono arrivare da sorgenti high-side o da contatti verso massa.
*Acceptance:* [B] per ogni modo e su entrambi i canali, lettura corretta con la board alimentata a 10,0 V e a 14,6 V; [B] modo L: lettura "attivo" con un contatto da 1 kΩ verso massa; [B] modo H: 24 V e −16 V continui per 5 min senza danno; modo L: ingresso a +24 V e a −16 V per 5 min senza danno; [B] configurazioni errate (entrambi i jumper verso IN, oppure verso +12 V e GND) per 5 min senza danno; [B] corrente a ingresso attivo ≤ 1,5 mA con la board a 14,6 V.

**REQ-EL-008** (Must, Assumed) — **Vale per gli ingressi di entrambe le schede (IN-CAB, IN-CEL, IN-AUX1 sull'elettrica; IN-AUX2 sull'idraulica).** Gli ingressi IN-CAB, IN-CEL (e IN-AUX1/2, vedi REQ-EL-009) *shall* sopravvivere senza danno, con ripristino automatico della lettura, ai transitori dell'impianto 12 V del veicolo:
- **load dump ISO 16750-2 Test A (non soppresso)**, sistema 12 V: U_s 79–101 V, R_i 0,5–4 Ω, t_d 40–400 ms;
- **ISO 7637-2 impulso 1**: U_s fino a −150 V, R_i 10 Ω, t_d 2 ms;
- **ISO 7637-2 impulso 2a**: U_s fino a +112 V, R_i 2 Ω, t_d 0,05 ms;
- **ISO 7637-2 impulsi 3a/3b** (burst ns): R_i 50 Ω, livelli da verificare.

*Rationale:* IN-CAB è sul +15 lato alternatore. Non è noto se l'X244 abbia una soppressione centralizzata del load dump: si assume il caso non soppresso (Test A). Su un ingresso di segnale ad alta impedenza costa poco.
*Fonti:* il testo delle norme non è stato consultato. Valori da application note dei costruttori, fonti secondarie: [MCC AN0005](https://solutions.mccsemi.com/news/application-note-quick-guide-on-automotive-load-dump-protection-iso-16750-2) e [TI SNOAAA1](https://ti.com/document-viewer/lit/html/SNOAAA1) (load dump); [TI SNOAA13](https://ti.com/lit/pdf/snoaa13) tab. 1, 2, 4 (R_i e t_d degli impulsi 1, 2a, 3a); [TI e2e, ISO 7637-2](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/iso_5F00_7637_5F00_2.pdf) (range di U_s).
*Acceptance:* [D] analisi per impulso: corrente e energia su ogni componente del percorso d'ingresso entro i limiti del datasheet (impulsivi per resistori e diodi). Nessun generatore ISO disponibile al banco.
*Rischio accettato (utente, 2026-10-08):* il resistore serie R1 è un **0805**. Nel load dump Test A (101 V, 400 ms) dissipa circa 1,1 W (174 mJ), 9 volte la potenza nominale standard di un CRCW0805 (0,125 W; il datasheet Vishay prova il sovraccarico a 2,5× per 5 s). La tenuta al load dump **non è dimostrabile** con un 0805; se si rompe il canale legge "inattivo". Gli altri impulsi (1, 2a, 3a/3b) vanno ancora verificati sulle curve di impulso del resistore (non lette). Il load dump potrebbe non arrivare al nodo se l'alternatore dell'X244 ha una soppressione integrata (non verificato).

### 1.2 Interfaccia / protocollo

**REQ-IF-005** (Must, Confirmed) — 2 ingressi per shunt 200 A / 75 mV montati **sul negativo** (low-side), corrente **bidirezionale ±200 A** su entrambi: ±75 mV differenziali (0,375 mV/A).
*Massa:* la massa della board è collegata alla massa veicolo/batteria, cioè al **lato batteria** degli shunt (Confirmed). Il capo lato carichi oscilla quindi fra −75 mV e +75 mV rispetto alla massa della board.
*Prescrizioni:* misura differenziale con collegamento Kelvin (due fili dedicati per shunt, non la massa di alimentazione come riferimento); ingresso bipolare con modo comune ≈ 0 V. **Offset di massa (Confirmed, utente 2026-10-17):** la tolleranza di ±0,5 V (Assumed) è abbandonata. Vale invece una prescrizione di cablaggio: la massa della board si collega al **lato batteria dello shunt in un solo punto** (stella), con conduttore dedicato e non attraversato da correnti di carico, così che l'offset fra massa board e capo batteria dello shunt sia trascurabile (obiettivo ≤ ±50 mV, da misurare). *Ipotesi da confermare:* i capi lato batteria dei due shunt stanno sullo stesso nodo di negativo batteria (stessa barra), altrimenti il secondo canale vede un offset proprio. Motivo: l'ADC scelto (ADS1115, vedi `docs/components.md`) garantisce solo ingressi ≥ GND.
*Acceptance:* errore ≤ 1 % della lettura sopra 10 A, risoluzione ≤ 0,1 A (Assumed, da confermare — OPEN-06).

**REQ-IF-007** (Must, Confirmed) — Interfaccia in serie fra inverter **Renogy R-INVT-PUH1-201235-IT** e il suo comando remoto (interruttore on/off + LED verde + LED rosso, nessun display — Confirmed dall'utente).
Funzioni: (a) lettura stato LED verde (POWER) e rosso (FAULT); (b) comando on/off dalla board; (c) remote originale funzionante; (d) **board non alimentata o in reset ⇒ remote collegato direttamente all'inverter**, comportamento identico all'impianto senza board.
*Acceptance:* con board spenta, l'interruttore del remote accende/spegne l'inverter; con board attiva, HA comanda on/off e legge i due LED; nessuna variazione visibile della luminosità dei LED del remote.

*Evidenza sull'interfaccia* — solo fonti forum ([diysolarforum, thread 15308](https://diysolarforum.com/threads/renogy-remote-switch-wiring-diagram.15308/), più utenti concordi, modelli Renogy diversi):
- Segnali **discreti, nessun protocollo seriale**: l'interruttore è un contatto pulito fra due poli, uno dei quali porta la tensione di batteria; ogni LED ha un pin pilotato dall'inverter; uno o due pin di massa.
- Livelli misurati sui pin LED: ~2,7 V (utente *shinikveech*) e 3,8 V verde / poco meno rosso (utente *Timmerich*).
- **Connettore variabile per modello:** RJ12 6P6C o RJ11 6P4C sui modelli più vecchi; **RJ45 8 poli** sui più recenti, con cicalino nel remote. Su un RJ45 1000 W: contatto su pin 3–5, LED verde pin 2, rosso pin 4, massa pin 7 (*Timmerich*). Un altro utente con RJ45 non è riuscito ad accendere cortocircuitando coppie di fili: la piedinatura RJ45 **non è univoca**.
- Schema di un remote **RJ11** a 6 poli fornito dall'utente (2026-10-18, origine e modello ignoti, fonte debole): LED con R 1 kΩ in serie a GND, contatto etichettato "SW-PB" (pulsante?) fra due pin; da confermare se il remote Renogy è a levetta o a pulsante.
- Inverter con selettore 0 / I / II: in II lo stato è governato dal remote (*Dr.HD*).
*Dal costruttore (Renogy Support, caso CASE2025080300065, email del 9 ago, immagine "RJ45 T568B", lettura del disegno **confermata dall'utente 2026-10-17**; la piedinatura resta **Assumed** finché non verificata sul pezzo):* connettore **RJ45 8 poli**. Pin 1 NC · **2 GND** · **3 +12 V** · **4 VERDE** · **5 VIN** · 6 NC · **7 ROSSO** · 8 NC. Il contatto dell'interruttore è quindi fra **+12 V (3) e VIN (5)**, coerente con "contatto su pin 3–5" del forum; i pin LED del forum (verde 2, rosso 4, massa 7) **non coincidono**: vale il costruttore, da verificare.
*Non fornito dal costruttore:* livelli e capacità di pilotaggio dei pin LED, tensione e impedenza di VIN, tensione sul pin +12 V (regolata o batteria?). Da misurare (OPEN-02).

*Topologia di requisito proposta:* relè di scambio a riposo trasparente — contatto NC = remote → inverter; eccitato = contatto della board → inverter, con stato dell'interruttore del remote letto come ingresso. Linee LED **proxate** dalla board (decisione utente 2026-10-18): lette dall'inverter con celle opto isolate e ripresentate al remote, passanti a riposo (board spenta ⇒ remote diretto, LED compresi).

**REQ-IF-008** (Must, Confirmed) — Modbus RTU su RS485 verso meter SDM120 (board = master).

**REQ-IF-010** (Must, Confirmed) — Il bus RS485 della board è **multi-drop ed estendibile** a slave futuri (es. slave diagnosi motore). Connettore con +12 V, GND, A, B per alimentare gli slave. Terminazione inseribile. Corrente massima erogabile agli slave da definire (OPEN-11).
*Scheda (Assumed, 2026-10-26):* RS485 sulla scheda elettrica (SDM120, IF-008). Con un MCU per scheda e nessun link diretto, il bus **non è più condiviso** col comando cabina (vedi OPEN-07 in `idraulica/frd.md`).

## 2. Punti aperti

| ID | Domanda | Requisiti |
|---|---|---|
| OPEN-02 | **[Riaperto 2026-10-17]** Connettore RJ45 e piedinatura forniti da Renogy (IF-007). Restano: verifica piedinatura sul pezzo (lettura del disegno confermata 2026-10-17); selettore 0/I/II presente?; misure sul pezzo per pin in OFF/ON/FAULT (+12 V a vuoto, VIN a contatto aperto e chiuso con corrente, livello e corrente dei pin LED, verso del LED nel remote) | IF-007 |
| OPEN-12 | Uscita "stato cellula" della centralina: modello della centralina, tipo di uscita (high-side 12 V / open-collector / contatto), livelli a cellula ON e OFF | EL-006 |
| OPEN-06 | Shunt: confermare precisione (1 %) e risoluzione (0,1 A); lunghezza cavi Kelvin | IF-005 |
| NEW-2 | **Relè globale**: funzione (stacco generale servizi? su quale linea?), corrente/tensione contatti, comando e stato (NA/NC, fail-safe), protezione e misura. **Vincolo (Confirmed, utente 2026-10-26): il relè globale non deve togliere l'alimentazione all'MCU.** Nessun requisito scritto: usare la skill `hardware-requirements-engineer` | — |

