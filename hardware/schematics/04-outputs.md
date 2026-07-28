# 04 — Uscite di potenza

Requisiti implementativi per i 4 canali di uscita configurabili per depopolazione.

**Traceability:** REQ-IF-008, IF-009, SAFE-001, SAFE-002, SAFE-003, EL-004, EL-009, MECH-003, LIFE-001.

---

## 1. Principio

**Quattro canali**, configurabili per depopolazione in tre varianti sullo stesso footprint:

| Variante | Realizzazione | Carico |
|---|---|---|
| **(I)** | MOSFET **high-side** con PWM | Fino a 5 A continui, dimming LED |
| **(II)** | Relè indipendente | 10 A |
| **(III)** | Ibrida: 2 relè indipendenti + 2 relè in interlock | Inversione motori DC |

> **I carichi hanno alimentazione propria esterna.** La board fornisce **solo il contatto di commutazione**: la corrente di carico non è prelevata dai rail della scheda e il ritorno non transita per la sua massa. Questo scarica i budget di REQ-EL-005 ed EL-007, ma **non** i requisiti su dimensionamento di piste e connettori.

---

## 2. Variante (I) — MOSFET high-side

### 2.1 Topologia

**MOSFET P-channel discreto** con **level-shifter** dal GPIO 3,3 V verso il riferimento battery+.

```
Battery+ ──┬── S ─[P-MOSFET]─ D ──→ Carico ──→ massa telaio (esterna alla board)
           │      │G
           ├──[Rgs pull-up]──┤
           │                 ├──[Zener clamp]── S
           │                 │
           └──[R divisore]───┴──[Rgate]── Q level-shifter ── GPIO
```

### 2.2 Perché high-side

Su un veicolo la carrozzeria è riferita a massa batteria. Con switching high-side un **corto accidentale del cavo di uscita verso massa o telaio non attiva il carico**, perché questo resta scollegato dal positivo finché il MOSFET non conduce. Con low-side lo stesso corto attiverebbe il carico aggirando il comando — evento plausibile su cablaggi lunghi ed esposti.

### 2.3 Perché discreto e non switch integrato

Alternative scartate, con il motivo:

- **Switch integrato "smart" automotive** (PROFET, TPS1HB16-Q1): offre diagnostica di sovracorrente, sovratemperatura e open-load, ma i tempi di commutazione tipici (~300–550 µs) danno un massimo di ~1–2 kHz, **senza margine** rispetto al target di 1,5–2 kHz. Costa inoltre circa un ordine di grandezza in più per canale, su 4 canali.
- **N-channel con driver high-side**: RDS(on) migliore a parità di costo, ma il duty cycle prossimo al 100% richiede un charge pump dedicato, complessità non giustificata a questa frequenza.

**Contro accettato del P-channel:** die più grande e scelta più ristretta dell'N-channel equivalente. Esistono opzioni automotive AEC-Q101 a bassa RDS(on) compatibili con il rating ≥ 40 V.

### 2.4 Gate drive — vincoli inderogabili

**Pull-up gate-source** verso battery+: garantisce lo stato OFF con GPIO flottante. È la rete che realizza lo stato sicuro passivo di §5.

> **Zener di clamp gate-source: non opzionale.** Con il partitore che tira il gate verso massa e la batteria a 16 V la V_GS è già prossima al limite tipico di ±20 V; durante un transitorio clampato — fino a ~38 V — lo supererebbe, distruggendo il gate.

**Resistore di gate:** scelto per **rallentare i fronti**. A 1,5–2 kHz le perdite di commutazione sono trascurabili, quindi conviene privilegiare il contenimento del dV/dt e delle emissioni rispetto alla velocità di commutazione.

**Level-shifter:** transistor o piccolo MOSFET che tira il gate verso massa attraverso il partitore, comandato dal GPIO a 3,3 V.

### 2.5 Dimensionamento

- **V_DS ≥ 40 V**, coerente con la catena di ingresso.
- **RDS(on)** tale da contenere la dissipazione a 5 A continui entro i limiti termici del package a 40 °C ambiente.
- **Clamp** sull'uscita per i transitori residui su cavi e connettori lunghi.

### 2.6 PWM

**Frequenza nominale 1,5–2 kHz**, configurabile per canale a firmware.

**Motivazione.** Sopra la soglia di rischio flicker di ~1250 Hz per modulazione a profondità piena, senza spingersi in banda ultrasonica che richiederebbe MOSFET e gate-drive più veloci.

> **Rischio accettato.** La banda 1,5–2 kHz è udibile: è possibile un fischio a basso livello dalle induttanze parassite di cavi e driver LED economici, percepibile nel silenzio dell'abitacolo. La configurabilità per canale consente di spostare il punto di lavoro entro il limite dell'hardware.

### 2.7 Rinuncia dichiarata

Senza switch integrato **non c'è diagnostica per canale** di open-load e sovratemperatura. Non è perdita di protezione — la sovracorrente dei carichi è comunque demandata al quadro del camper — ma solo di segnalazione. Se in futuro servisse, si aggiunge con shunt e amplificatore.

---

## 3. Varianti (II) e (III) — relè

### 3.1 Driver di bobina

**Topologia.** Transistor o MOSFET low-side che pilota la bobina, con **diodo di ricircolo** in antiparallelo.

**Prescrizione.** Ingresso del driver con **pull-down**, così che al reset dell'MCU o dell'I/O expander la bobina resti diseccitata (§5).

**Alimentazione della bobina** dietro load-switch, per poterla disalimentare in deep-sleep.

### 3.2 Isolamento

Le varianti a relè sono le uniche che offrono **isolamento galvanico vero**: il carico può non condividere mai la massa della board.

Nella variante (I) il source del MOSFET e la massa scheda condividono il riferimento batteria−: **non è isolamento galvanico**, anche se il ritorno del carico non transita per la board.

### 3.3 Interlock (variante III)

**Funzione.** Esclusione reciproca di due relè per l'inversione di motori DC — gradino, antenna: **mai entrambi attivi**, perché l'attivazione simultanea equivale a un cortocircuito sul motore o sull'alimentazione.

> **L'esclusione shall essere garantita in hardware**, non dal solo firmware: cablaggio dei contatti in configurazione di inversione, oppure interblocco elettrico delle bobine. Un bug firmware o un glitch al boot non deve poter attivare entrambi i relè.

**Acceptance [B].** Forzando via software l'attivazione simultanea, il carico non è mai alimentato in configurazione di corto; l'ispezione dello schema conferma l'impossibilità topologica.

---

## 4. Protezione da sovracorrente

**Prescrizione: nessuna protezione a bordo sui circuiti di carico.**

I carichi hanno alimentazione esterna e il quadro del camper ha già i propri fusibili di ramo: replicarli significherebbe quattro portafusibili, spazio e costo per una protezione ridondante.

> **Rischio residuo da documentare.** Un guasto su un circuito di carico non è limitato dalla board. Se il quadro del camper non ha un fusibile sul ramo che alimenta quel carico, **piste e morsettiera di uscita sono esposte alla corrente di guasto**. L'onere ricade sull'installatore e va scritto nella documentazione di montaggio.

Il PTC di ingresso protegge **solo** l'alimentazione della board.

---

## 5. Stato sicuro

**Prescrizione.** Al power-on, in brown-out e dopo reset da watchdog, **tutte le uscite shall trovarsi o portarsi nello stato disattivato**.

> **Garantito passivamente, senza dipendere dal firmware.** I GPIO dell'MCU sono in alta impedenza durante reset e boot, quindi ogni stadio di uscita richiede una rete di polarizzazione esterna che imponga il livello di OFF con il pin flottante.

| Stadio | Rete richiesta |
|---|---|
| P-MOSFET high-side | **Pull-up** di gate verso il source |
| Driver di bobina relè | **Pull-down** sull'ingresso del driver |
| Enable dei load-switch (via expander) | **Pull-down**, così che un expander non inizializzato lasci le sezioni disalimentate |

**Vincolo di assegnazione pin.** Le uscite di potenza **non** possono stare su pin di strapping dell'MCU, che al boot assumono livelli imposti dal bootloader.

**Acceptance [B].** Almeno 20 cicli di power-on e altrettanti di brown-out indotto con alimentatore da banco, senza attivazioni spurie su oscilloscopio; ispezione dello schema che conferma le reti di polarizzazione su ogni stadio.

---

## 6. Masse e distribuzione

Con topologia high-side il ritorno del carico **non transita per la massa della board**, il che riduce il ground-bounce rispetto al low-side. Resta però un percorso di rumore residuo: il **dI/dt del PWM si manifesta sul ramo positivo**, condiviso con l'ingresso di potenza.

**Prescrizioni.**
- Distribuzione del positivo commutato verso i source dei MOSFET su **traccia o piano dedicato**, disaccoppiato dal rail dei regolatori.
- Le bobine dei relè, pilotate low-side, restituiscono la propria corrente sulla **massa di potenza**, separata da quella di segnale e ricongiunta in star ground.

---

## 7. Connettori

**Morsettiera a vite 5,08 mm** per tutte e 4 le uscite, **sul bordo** della scheda.

Rating tipico 10 A (UL) / 15 A (IEC): copre sia la variante MOSFET a 5 A continui sia quella a relè da 10 A.

---

## 8. Checklist di rilascio

- [ ] Zener di clamp gate-source su ogni P-MOSFET
- [ ] Pull-up di gate presente su ogni canale MOSFET
- [ ] Pull-down su ogni ingresso di driver di bobina
- [ ] Diodo di ricircolo su ogni bobina
- [ ] Interlock realizzato in hardware, verificato per ispezione topologica
- [ ] Nessuna uscita assegnata a pin di strapping
- [ ] Resistore di gate dimensionato per fronti lenti, non veloci
- [ ] V_DS ≥ 40 V e dissipazione a 5 A/40 °C verificate a datasheet
- [ ] Positivo commutato su traccia dedicata, separato dal rail dei regolatori
- [ ] Requisito di installazione sui fusibili di ramo riportato nella documentazione
