# 01 — Alimentazione e protezioni

Requisiti implementativi per lo schematico della sezione di ingresso, delle protezioni, della logica di accensione e dei rail di alimentazione.

**Traceability:** REQ-EL-001, EL-002, EL-003, EL-004, EL-005, EL-006, EL-007, EL-009, EL-010, SAFE-001, IF-016, ENV-001, LIFE-001.

---

## 1. Catena di ingresso

L'ordine dei blocchi dal morsetto di alimentazione verso i regolatori è vincolante, perché ciascuno protegge quelli a valle.

```
Morsetto 5,08 mm ──[PTC]──[P-MOSFET ideal-diode]──[Clamp TVS]──[Filtro EMI]──┬──→ Buck 3,3V
   (2 poli)                                                                   └──→ Load-switch → Buck 5V
```

### 1.1 Fusibile resettabile (PTC)

**Topologia.** PTC in serie al ramo positivo, immediatamente a valle del morsetto di ingresso.

**Dimensionamento.**
- Corrente di **hold** shall essere superiore al consumo di picco della board con tutti i relè eccitati, con margine. **(da congelare)** dopo il consolidamento del consumo a schematico completo.
- Il derating della corrente di hold con la temperatura shall essere valutato fino a **+40 °C** (REQ-ENV-001).
- La **resistenza serie** del PTC va annotata: la sua caduta si sottrae al margine di tensione a 9 V, che è l'estremo inferiore operativo.

**Nota di sistema.** La resistenza serie del PTC è un contributo *utile* all'impedenza di ingresso richiesta al §1.3: va conteggiata lì e non trattata come parassita da minimizzare.

**Selezione.** Il leakage del PTC concorre al consumo nello stato OFF (§3.2) e shall essere fra i parametri di scelta.

> **Non prevedere** fusibili o PTC sui circuiti di carico commutati dalle uscite: la loro protezione è demandata al quadro fusibili del camper (REQ-SAFE-001).

### 1.2 Protezione da inversione di polarità

**Topologia.** **P-MOSFET in configurazione ideal-diode** sul ramo positivo: source verso l'ingresso, drain verso valle, gate riferito a massa attraverso un resistore, con Zener di clamp gate-source.

**Perché non un Schottky.** Sopra i 2 A la caduta diretta di un diodo produce dissipazione e caduta di tensione non accettabili sul margine a 9 V.

**Dimensionamento.**
- V_DS shall essere ≥ 40 V (§1.3).
- Il partitore di gate shall mantenere V_GS entro il rating anche con l'ingresso al valore di clamp del TVS, non solo a 16 V nominali. Lo **Zener di clamp gate-source non è opzionale**.
- RDS(on) scelta per contenere la caduta alla corrente massima della board.

**Acceptance [B].** −16 V continui applicati per 5 min: nessun danno, ripristino della piena funzionalità (REQ-EL-002).

### 1.3 Clamp TVS e rating della catena

Questo è il punto più delicato dello schema di ingresso: **clamp e regolatore sono accoppiati** e vanno scelti insieme.

**Vincolo doppio.**
- Il TVS **non deve condurre** a 16 V continui né sullo spike da apertura del BMS documentato a ~17,2 V → V_RWM sopra quei valori.
- La sua tensione di clamp **V_C alla corrente di picco attesa** deve restare **sotto il rating assoluto del buck** → V_C < 40 V.

**Classe indicativa: V_RWM 20–24 V (da congelare).** Il criterio di verifica è V_C, non V_RWM: su famiglia SMBJ 600 W un V_RWM di 24 V dà V_C = 38,9 V a 15,5 A sulla forma d'onda 10/1000 µs, mentre un V_RWM di 40 V darebbe 64,5 V, incompatibile.

**Rating ≥ 40 V su tutta la catena.** MOSFET di inversione, TVS, buck 3,3 V e buck 5 V motori.

> **Impedenza serie obbligatoria.** Con rating a 40 V il margine fra V_C e il buck è di pochi volt sulla forma d'onda 10/1000 µs e **negativo** su una 8/20 µs. Il requisito è soddisfacibile **solo** con impedenza serie fra clamp e buck: RDS(on) del MOSFET di inversione, resistenza del PTC e induttore o ferrite di ingresso. Va prevista fin dallo schema e conteggiata esplicitamente — senza, la selezione a 40 V non chiude.

**Fuori dal design basis:** load dump ISO 7637-2 pulse 5 (REQ-EL-003), guasto hard della sorgente di carica e sgancio del BMS in alta corrente (REQ-EL-010). Non dimensionare il TVS su questi scenari.

### 1.4 Filtro EMI

**Topologia.** Footprint per rete **LC o pi** e per **choke di modo comune**, in serie all'ingresso, **non popolati di default**.

**Prescrizione.** I footprint shall prevedere **ponticelli di corto o resistori da 0 Ω** che garantiscano la continuità del ramo quando il filtro non è popolato: la configurazione di default deve essere funzionante senza strap improvvisati.

**Nota.** Se popolato, l'induttore serie contribuisce all'impedenza richiesta al §1.3.

---

## 2. Logica di accensione

### 2.1 Ingresso WAKEUP

**Topologia.** Optoisolatore con LED lato campo alimentato a livello batteria, resistore di limitazione dimensionato su 9–16 V; uscita del foto-transistor verso la logica di latch e verso un GPIO dell'MCU nel dominio RTC.

**Funzione doppia.** Un fronte accende la board dallo stato OFF; l'asserzione della richiesta di spegnimento avvia la sequenza firmware (REQ-EL-006).

### 2.2 Power-latch

**Topologia.** Latch che abilita il regolatore always-on, comandato da WAKEUP in set e dal rilascio del **power-hold** dell'MCU in reset.

**Sequenza vincolante.**
1. WAKEUP → il latch abilita il buck 3,3 V.
2. L'MCU al boot **asserisce il power-hold**, che mantiene il latch anche se WAKEUP viene rimosso.
3. Su richiesta di spegnimento l'MCU completa la propria sequenza — parcheggio motori, flush dello stato, notifica CAN — e **solo dopo** rilascia il power-hold, aprendo il latch.

**Prescrizione.** Il taglio dell'alimentazione shall essere subordinato al rilascio del power-hold: nessun percorso hardware deve poter togliere alimentazione direttamente da WAKEUP.

**Comportamento all'accensione.** Il ritardo fra abilitazione del regolatore e asserzione del power-hold deve essere coperto: se l'MCU impiega più tempo a bootare di quanto WAKEUP resti asserito, la board si spegne. **(da verificare)** con il tempo di boot reale.

**Limitazione da documentare.** Dallo stato OFF **non è possibile il risveglio via CAN**, perché il transceiver non è alimentato. Solo WAKEUP riaccende un nodo spento.

---

## 3. Rail e stati di alimentazione

### 3.1 Struttura

| Rail | Sorgente | Alimenta | Sezionabile |
|---|---|---|---|
| **3,3 V always-on** | Buck a valle del latch | MCU, transceiver CAN, I/O expander | No (solo dal latch) |
| **Periferiche** | Load-switch da 3,3 V o dall'ingresso | Opto degli ingressi, sense di corrente, eccitazione NTC | Sì |
| **5 V motori** | Buck dedicato dietro load-switch | Stepper, 2 servo | Sì |

**Prescrizione (REQ-EL-004).** Il load-switch serve alle sezioni il cui assorbimento **non è governabile da un GPIO**. I LED ne sono esclusi: si spengono dal pin che li pilota.

### 3.2 Stato OFF

**Vincolo.** Con il latch aperto, le uniche correnti assorbite shall essere quelle dei **componenti di protezione a monte del regolatore**: leakage di TVS, MOSFET di inversione e PTC, più il quiescente del latch.

**Prescrizione di schema.** Nessun altro ramo shall restare connesso al positivo di batteria. In particolare **non prevedere partitori di sense permanenti** — è la ragione per cui il sense di tensione batteria è stato escluso dal progetto.

**Acceptance [D].** Somma dei leakage dichiarati calcolata e annotata in BOM; ispezione dello schema che conferma l'assenza di rami permanenti. **[B]** misura coerente con il calcolo.

**Criterio di selezione.** A parità di prestazione, fra due componenti di protezione si sceglie quello a leakage minore.

### 3.3 Stato deep-sleep

MCU e transceiver alimentati, tutti i load-switch aperti, **≤ 1 mA a 12,8 V**.

**Contributi da conteggiare:** quiescente del buck 3,3 V, MCU in deep-sleep, transceiver in standby, quiescente dell'I/O expander, LED RGB del modulo MCU.

> **Verifica propedeutica.** Il LED RGB indirizzabile del modulo assorbe corrente anche a colore spento e può da solo impegnare una quota rilevante del budget. Da misurare; se necessario si dissalda, senza altre conseguenze di progetto.

**Sollievo di progetto.** Con 1 mA di budget il buck always-on **non** è più vincolato a Iq < 100 µA: la selezione è ampia ed economica.

### 3.4 Buck 3,3 V

- Rating assoluto di ingresso **≥ 40 V** verificato a datasheet.
- Range di regolazione qualificato per almeno **9–18 V**.
- Corrente sufficiente per MCU con radio attiva sul nodo bridge, transceiver, expander e le reti di polarizzazione.

### 3.5 Buck 5 V motori

- **≥ 2,5 A di picco** (REQ-EL-007).
- Rating di ingresso ≥ 40 V.
- A valle del load-switch: in deep-sleep e in OFF è completamente disalimentato.

**Condensatore di bulk.** Il picco di stallo servo è breve e shall essere assorbito **prevalentemente dal bulk**, non erogato in continuo dal regolatore. Dimensionarlo è ciò che permette di restare su un regolatore da 2,5 A: **(da congelare)** con la durata del transitorio di stallo misurata.

**Budget che giustifica i 2,5 A:** 1 servo in stallo (~1,5 A) + 1 servo in tenuta (≤ 300 mA) + stepper (~200 mA) + margine. Vale **solo** sotto il vincolo firmware di non contemporaneità dei due servo.

---

## 4. Masse

**Prescrizione (REQ-EL-009).** Massa di potenza — ritorno delle bobine relè e residuo delle uscite — separata dalla massa di segnale (MCU, CAN, ADC), ricongiunte in **un solo punto** presso l'ingresso di alimentazione.

**Distribuzione del positivo commutato.** Il ramo che alimenta i source dei MOSFET high-side shall essere disaccoppiato dal rail dei regolatori: con topologia high-side il dI/dt del PWM si manifesta sul **positivo**, non sul ritorno di massa.

**Connettori.** Terminali distinti per massa di potenza e massa di segnale.

**Acceptance [B].** Con tutte le uscite in PWM a pieno carico, il rumore su rail 3,3 V, riferimento ADC e livelli CAN resta entro le tolleranze dei componenti scelti **(soglia da congelare)**.

---

## 5. Checklist di rilascio

- [ ] V_C del TVS alla corrente di picco < rating assoluto del buck, con l'impedenza serie conteggiata
- [ ] Rating ≥ 40 V verificato su MOSFET di inversione, TVS ed entrambi i buck
- [ ] Zener di clamp gate-source presente sul MOSFET di inversione
- [ ] Nessun ramo permanentemente connesso al positivo oltre alle protezioni di ingresso
- [ ] Somma dei leakage in OFF calcolata e annotata
- [ ] Ponticelli di continuità sui footprint del filtro EMI
- [ ] Corrente di hold del PTC verificata contro il consumo di picco con relè eccitati, derating a +40 °C incluso
- [ ] Percorso di spegnimento subordinato al rilascio del power-hold, senza scorciatoie hardware
