# 06 — Interfacce aggiuntive

Requisiti implementativi per bus CAN, bus I²C, I/O expander, LED di stato, test point e connettori.

**Traceability:** REQ-IF-001, IF-002, IF-012, IF-013, IF-014, IF-015, MECH-003, DIAG-001, EL-004, SAFE-003, SW-003, SW-004.

---

## 1. Bus CAN

### 1.1 Transceiver

**Componente candidato: NXP TJA1042T/3.**

| Requisito | Valore a datasheet |
|---|---|
| Standby con wake-up da attività bus | Sì |
| VIO per logica 3,3 V | 3–5 V |
| ESD sui pin di bus | **±8 kV** IEC 61000-4-2 |
| Tensione ammessa sui pin di bus | **−58…+58 V** |
| Immunità ISO 7637-2 sui pin di bus | pulse 1, 2a, 3a |

> **La protezione delle linee CAN si ottiene per selezione del transceiver, non aggiungendo componenti.** Un array di protezione esterno sarebbe ridondante rispetto ai valori sopra, e in contrasto con il criterio di costo del progetto.

**Clausola di validità.** Se si adottasse un transceiver alternativo che **non** dichiara ESD ≥ ±8 kV, tensione di guasto ≥ ±40 V e immunità ai pulse ISO pertinenti, l'array esterno diventa obbligatorio e i footprint predisposti vanno popolati.

**Margine.** I ±58 V coprono con ampio margine un corto accidentale verso il positivo batteria a 12 V, che è lo scenario di guasto plausibile.

### 1.2 Segnali verso l'MCU

TX, RX e **STB** (standby), tutti su GPIO diretti.

Lo standby è ciò che permette il risveglio del nodo da attività sul bus in deep-sleep: non è opzionale.

### 1.3 Terminazione

**120 Ω inseribile** via jumper o solder-bridge. La scheda è identica su tutti i nodi, ma solo i due estremi della linea vanno terminati.

### 1.4 Filtro di modo comune

**Footprint per choke di modo comune, depopolato.** Risponde al **rumore condotto** dell'inverter sulla stessa struttura, non all'ESD — che è già coperto dal transceiver.

Stesso criterio del filtro EMI di ingresso: predisposto e non popolato, si valorizza solo se la misura sul veicolo lo richiede. Prevedere i **ponticelli di continuità**.

### 1.5 Connettore

**Morsettiera a vite 2,54 mm** sul bordo della scheda. Le correnti sono trascurabili: il vincolo è di segnale, non di potenza.

### 1.6 Bit-rate e conseguenze

**125 kbit/s.** Bit-rate basso scelto per tollerare cablaggi lunghi e poco schermati.

Due conseguenze già verificate, da non rimettere in discussione:

- **Latenza:** un frame standard con 8 byte occupa ~1 ms, quindi il tempo di bus è trascurabile nel budget di round-trip di 250 ms.
- **Aggiornamento firmware via CANopen:** ~5–6 kB/s effettivi, cioè **circa 5 minuti** per un'immagine da 1,5 MB. Lungo ma praticabile.

---

## 2. Bus I²C

### 2.1 Struttura

Un solo bus a 3,3 V, condiviso fra:

- **I/O expander a bordo** (§3)
- **Connettore di espansione** verso l'esterno

### 2.2 Pull-up

**Pull-up on-board disinseribili.** Se un modulo esterno porta i propri, i pull-up si sommano abbassando la resistenza equivalente: la possibilità di disinserirli evita di doverli dissaldare.

### 2.3 Protezione

Protezione ESD sulle linee del connettore di espansione, che è accessibile all'utente.

**Acceptance [B].** Scheda funzionante con connettore aperto o in corto verso GND.

### 2.4 Connettore di espansione

**JST PH 2,0 mm, 4 pin**, ordine dei segnali **Qwiic-like**:

| Pin | Segnale |
|---|---|
| 1 | GND |
| 2 | VCC (3,3 V) |
| 3 | SDA |
| 4 | SCL |

**La numerazione del pin 1 shall essere serigrafata.**

**Conseguenza dichiarata.** Si rinuncia alla compatibilità fisica diretta con l'ecosistema Qwiic/STEMMA-QT, che usa JST-SH 1,0 mm. Ma con l'ordine dei segnali identico **l'adattatore è un semplice cambio di connettore pin-a-pin**, senza incroci di fili e senza rischio di invertire alimentazione e segnali.

**Nessun segnale di interrupt o reset.** Se un futuro expander esterno dovesse generare eventi senza polling, servirà un GPIO su un connettore diverso o un re-spin: vincolo accettato in cambio di un connettore più piccolo.

**Acceptance [B].** Comunicazione a 100 kHz con dispositivo esterno su cavo di 30 cm.

---

## 3. I/O expander

### 3.1 Necessità

> **Non è un'opzione.** Il bilancio dei GPIO non chiude con margine sui 34 pin del modulo: spostando 6 funzioni lente sull'expander il fabbisogno diretto scende a 24–25 GPIO, con 5–6 pin di riserva. Il costo è **un solo integrato e nessun GPIO aggiuntivo**, perché il bus I²C è già richiesto per l'espansione.

### 3.2 Componente

**Expander I²C a 8 bit con uscite push-pull.**

**Perché push-pull e non quasi-bidirezionale** (tipo PCF8574): serve a pilotare i LED con corrente adeguata senza resistenze di pull-up aggiuntive.

**Indirizzo I²C selezionabile via strap e documentato**, per non collidere con dispositivi collegati al connettore di espansione.

**Corrente di riposo** compatibile con il budget di deep-sleep: l'expander sta sul rail always-on.

### 3.3 Funzioni assegnate

| Funzione | Numero |
|---|---|
| LED CANopen RUN ed ERR | 2 |
| LED di stato generici | 1 |
| Enable dei load-switch | 3 |
| Riserva | 2 |

**Criterio.** Sull'expander vanno **solo funzioni lente e non critiche nei tempi**. Restano su GPIO diretti dell'MCU tutte quelle con vincoli temporali — PWM delle uscite e dei servo, STEP/DIR, CAN — e quelle di sicurezza — power-hold, WAKEUP.

### 3.4 Stato sicuro

> Al reset le uscite dell'expander vanno in **alta impedenza**. Le reti di polarizzazione passive sono quindi necessarie anche su queste linee: **pull-down sugli enable dei load-switch**, così che un expander non inizializzato lasci le sezioni di potenza disalimentate.

### 3.5 Limitazione dichiarata

Le funzioni pilotate dall'expander dipendono dal bus I²C. Un blocco del bus impedisce di comandare LED e load-switch, ma **non** compromette uscite di potenza né motori, che restano su GPIO diretti.

---

## 4. LED di stato

### 4.1 LED CANopen

**Due LED conformi a CiA 303-3**, pilotati dall'expander:

- **Verde "RUN"** — stato NMT: flicker ~10 Hz = LSS configuration; blink = Pre-operational; singolo flash = Stopped; triplo flash = download firmware; fisso = Operational.
- **Rosso "ERR"** — stato errori: spento = nessun errore; flicker = Node-ID non configurato; blink = errore di configurazione; singolo flash = warning CAN; doppio flash = errore Heartbeat; triplo flash = timeout SYNC; quadruplo flash = timeout PDO; fisso = bus-off.

La logica è implementata nativamente da CANopenNode: **l'onere hardware si riduce ai 2 LED**.

**Scelta di schema.** LED bicolore a footprint singolo contro due LED distinti: lo standard ammette entrambe le soluzioni. Il bicolore riduce ingombro e BOM ma non consente di leggere RUN ed ERR simultaneamente. **(da congelare)**

### 4.2 Spegnimento passivo

> **Nessun load-switch sui LED.** Si spengono dal pin che li pilota: un load-switch dedicato sarebbe un componente e un GPIO in più a parità di risultato.

**Ma:** lo spegnimento in deep-sleep e in OFF shall essere garantito **dalla polarità di pilotaggio**, senza intervento firmware attivo. Un LED acceso per errore assorbe qualche mA e da solo sfonderebbe il budget di 1 mA.

**Vincolo di assegnazione.** I LED non possono stare su pin di strapping dell'MCU — vincolo che non si applica se pilotati dall'expander, ma va verificato per eventuali LED su GPIO diretti.

---

## 5. Test point

**Prescrizione.** Test point su rail e segnali chiave: **3V3, 5V motori, CAN-H, CAN-L, WAKEUP**.

Motivo: una scheda installata in un vano camper dev'essere diagnosticabile senza smontaggio, e in bring-up sono l'unico punto di misura non distruttivo.

**Raccomandazione.** Portare su pad anche i GPIO liberi rimasti: sono la riserva per gli imprevisti e costano solo area.

---

## 6. Riepilogo dei connettori

| Connettore | Tipo | Posizione | Sezione |
|---|---|---|---|
| Alimentazione board | Morsettiera a vite **5,08 mm**, 2 poli | Bordo | [`01`](01-power-supply.md) |
| 4 uscite di potenza | Morsettiera a vite **5,08 mm** | Bordo | [`04`](04-outputs.md) |
| Bus CAN | Morsettiera a vite **2,54 mm** | Bordo | §1.5 |
| 5 ingressi | Morsettiera a vite **2,54 mm** | Bordo | [`03`](03-inputs.md) |
| 5 ingressi (parallelo) | **JST XH 2,5 mm** | Anche interno | [`03`](03-inputs.md) |
| Bus I²C | **JST PH 2,0 mm**, 4 poli | Anche interno | §2.4 |
| Stepper | 4 poli | Anche interno | [`05`](05-motors.md) |
| 2 servo | 3 poli standard servo | Anche interno | [`05`](05-motors.md) |

**Regola di posizionamento.** Tutte le **morsettiere a vite sui bordi**, accessibili con il cacciavite a contenitore aperto. I connettori a innesto possono stare internamente all'area del PCB.

---

## 7. Checklist di rilascio

- [ ] Transceiver CAN verificato per ESD ≥ ±8 kV, guasto ≥ ±40 V e immunità ISO 7637-2
- [ ] STB del transceiver collegato a GPIO, non fissato
- [ ] Terminazione 120 Ω inseribile via jumper o solder-bridge
- [ ] Ponticelli di continuità sui footprint del choke CAN
- [ ] Pull-up I²C disinseribili
- [ ] Indirizzo dell'expander selezionabile via strap e documentato
- [ ] Pull-down sugli enable dei load-switch comandati dall'expander
- [ ] LED spenti con pin a riposo, per sola polarità di pilotaggio
- [ ] Pin 1 del connettore I²C serigrafato
- [ ] Test point su 3V3, 5V motori, CAN-H/L, WAKEUP
- [ ] Morsettiere a vite tutte sul bordo
