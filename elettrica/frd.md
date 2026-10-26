# Caravantic — scheda elettrica: requisiti

Status: **Draft** · Derivato da [`../docs/frd.md`](../docs/frd.md) (divisione in due PCB, 2026-10-26). Contesto, requisiti comuni, riuso da `old/` e storico revisioni restano nel FRD comune. Scheda sorella: [`../idraulica/frd.md`](../idraulica/frd.md).

**Perimetro (Confirmed, utente 2026-10-26):** shunt, inverter, relè globale. Il **relè globale** non era nel FRD precedente: requisiti da scrivere (vedi §3, NEW-2). L'assegnazione dei singoli REQ a questa scheda è **Assumed** (da rivedere insieme).

Stato: Confirmed = dichiarato dall'utente · Assumed = ipotesi da confermare · Open = non risolto.

## 1. Requisiti

### 1.1 Interfaccia / protocollo

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

## 2. Punti aperti

| ID | Domanda | Requisiti |
|---|---|---|
| OPEN-02 | **[Riaperto 2026-10-17]** Connettore RJ45 e piedinatura forniti da Renogy (IF-007). Restano: verifica piedinatura sul pezzo (lettura del disegno confermata 2026-10-17); selettore 0/I/II presente?; misure sul pezzo per pin in OFF/ON/FAULT (+12 V a vuoto, VIN a contatto aperto e chiuso con corrente, livello e corrente dei pin LED, verso del LED nel remote) | IF-007 |
| OPEN-06 | Shunt: confermare precisione (1 %) e risoluzione (0,1 A); lunghezza cavi Kelvin | IF-005 |
| NEW-2 | **Relè globale**: funzione (stacco generale servizi? su quale linea?), corrente/tensione contatti, comando e stato (NA/NC, fail-safe), protezione e misura. Nessun requisito scritto: usare la skill `hardware-requirements-engineer` | — |

