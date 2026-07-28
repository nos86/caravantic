# 05 — Motori e monitoraggio

Requisiti implementativi per la sezione motori: driver stepper, servo RC, misura di corrente e finecorsa virtuali.

**Traceability:** REQ-IF-010, IF-011, EL-007, EL-004, SW-001, LIFE-001, DIAG-001.

---

## 1. Perimetro

| Attuatore | Quantità | Driver |
|---|---|---|
| Stepper | 1 | TMC2209 |
| Servo RC | 2 | PWM diretto da GPIO |

Tutti alimentati dal **rail 5 V motori** dedicato, dietro load-switch (vedi [`01-power-supply.md`](01-power-supply.md) §3.5).

> **Vincolo di sistema che pervade questa sezione.** Il firmware garantisce che **un solo servo si muova alla volta**, con accodamento delle richieste concorrenti. Non è un'ottimizzazione: è il presupposto sia del dimensionamento del rail sia dell'attribuzione della battuta con sense singolo. Se un giorno cadesse, decadrebbero entrambi.

---

## 2. Driver stepper

### 2.1 Componente

**TMC2209** — 2 A RMS, 2,8 A di picco, interfaccia step/dir con configurazione via UART.

**Perché non un ULN2003.** È richiesta la compatibilità sia con stepper unipolari classe 28BYJ-48 sia con NEMA17 bipolari: l'ULN2003 non può pilotare un bipolare, quindi non copre il requisito.

**Package.** Disponibile in QFN, **compatibile con il processo di assemblaggio** a posizionamento manuale e reflow: il reflow gestisce nativamente i package leadless.

### 2.2 Interfaccia

| Segnale | Direzione | Note |
|---|---|---|
| STEP | MCU → driver | GPIO diretto, vincolo di temporizzazione |
| DIR | MCU → driver | GPIO diretto |
| EN | MCU → driver | GPIO diretto, attivo per abilitare |
| UART | bidirezionale | Configurazione corrente e lettura StallGuard4 |
| DIAG | driver → MCU | Uscita di allarme stallo |

**Prescrizione.** Tutti su **GPIO diretti dell'MCU**, mai sull'I/O expander: hanno vincoli di temporizzazione.

**MS1/MS2**, che selezionano l'indirizzo UART, possono essere fissati a livelli statici senza consumare GPIO.

### 2.3 Compatibilità con i due motori

Lo **stesso driver** serve entrambi i motori cambiando **un solo parametro firmware** — il registro `IHOLD_IRUN` — senza BOM alternativa:

| Motore | Corrente per fase |
|---|---|
| 28BYJ-48 modificato bipolare | **~100 mA** |
| NEMA17 | fino a 1,2 A |

> **Vincolo critico sul 28BYJ-48: ~100 mA/fase.** Oltre questa soglia il motore si scalda e può fondere gli avvolgimenti. Il limite si imposta via UART e va verificato prima del primo movimento.

**Modifica bipolare del 28BYJ-48 (versione 5 V).** Apertura del coperchio, taglio della pista centrale sul PCB interno, rimozione del filo rosso comune; risultato: 2 avvolgimenti pilotabili come bipolare a 4 fili. **La modifica è manuale e va eseguita su ogni motore prima del montaggio.**

### 2.4 Connettore

Connettore a 4 poli per lo stepper. Ammesso **interno all'area del PCB**, essendo a innesto e non richiedendo accesso con utensile.

---

## 3. Servo RC

**Segnale.** 50 Hz, impulso 1–2 ms, generato da GPIO con timer indipendente.

**Alimentazione.** Rail 5 V motori.

**Connettori.** Due connettori a 3 poli nello standard servo (segnale, +5 V, massa). Ammessi interni all'area del PCB.

**Acceptance [B].** Due servo comandati senza jitter percepibile sull'impulso (> ±10 µs).

### 3.1 Modelli candidati

**SG90** (stallo ~500–700 mA) e **MG90S** (fino a ~1,5 A) sono meccanicamente ed elettricamente intercambiabili — stesso footprint, stesso pinout, stesso range 4,8–6 V — quindi **non richiedono BOM diversa**: si dimensiona sul caso peggiore MG90S.

> **Dato non verificato.** Le correnti provengono da fonti divulgative su cloni generici, non da datasheet ufficiali. Il valore è congelato per decisione di progetto, ma **una misura sui pezzi acquistati resta consigliata prima dell'ordine dei componenti di potenza**.

---

## 4. Monitoraggio della corrente

Due meccanismi distinti, uno per lo stepper e uno per i servo.

### 4.1 Stepper — StallGuard4

**Nessun sense di corrente esterno.** Il TMC2209 integra la rilevazione di stallo sensorless, letta via registro UART `SG_RESULT` o dal pin DIAG.

### 4.2 Servo — sense unico

**Topologia.** **Un solo INA180A1** (gain 20 V/V) con **shunt unico sul rail 5 V motori**, non uno per canale.

```
Buck 5V ──[Shunt 33 mΩ]──┬──→ Stepper
                          ├──→ Servo 1
       └──[INA180A1]──→ ADC1
```

**Dimensionamento.**

| Parametro | Valore | Verifica |
|---|---|---|
| Shunt | **33 mΩ** | |
| Fondo scala | ~1,65 V a 2,5 A | Sotto la soglia di 2,45 V per la linearità ADC |
| Risoluzione a riposo | ~66 mV a 100 mA | Ampiamente risolvibile su ADC a 12 bit |
| Dissipazione al picco | ~0,21 W | Oltre il rating di un 0805: **package 1206** |

**Instradamento: ADC1 obbligatorio.** I canali ADC2 non sono utilizzabili in modo affidabile con WiFi attivo, e qualsiasi nodo può diventare bridge.

**Alimentazione dell'INA180** sul rail periferiche, sezionabile: in deep-sleep non assorbe.

### 4.3 Condizioni di validità dell'attribuzione

> La misura è **aggregata**: la lettura è interpretabile solo sotto due condizioni.

1. **Un solo servo in movimento alla volta**, garantito dal firmware. Con entrambi in moto la corrente sommata non permette di distinguere quale sia in battuta.
2. Il contributo dello stepper è trattato come **offset noto e limitato** — ~200 mA, imposto dal registro `IHOLD_IRUN` e quindi non variabile con il carico — da sottrarre o includere nella soglia di battuta.

**Se una futura evoluzione richiedesse il movimento simultaneo dei due servo, questa soluzione non basta più** e occorre tornare a un sense per canale.

**Beneficio.** Rispetto a due amplificatori indipendenti: metà componenti, metà costo, un canale ADC1 in meno — risorsa contesa nel bilancio dei pin.

---

## 5. Finecorsa virtuali

**Funzione.** Rilevare la battuta meccanica dall'assorbimento, evitando finecorsa fisici su serrande e valvole.

**Acceptance [B].** Battuta rilevata entro **200 ms** e motore de-energizzato prima di danni meccanici, con il secondo servo in tenuta e lo stepper eventualmente in movimento.

**Implicazione di schema.** La banda del percorso shunt → INA180 → ADC deve permettere di campionare entro quel tempo con margine: il filtro sull'uscita dell'amplificatore **non deve** essere così lento da mangiarsi i 200 ms. **(da congelare)** in fase di dimensionamento del filtro.

---

## 6. Alimentazione della sezione

**Rail 5 V dedicato, ≥ 2,5 A di picco**, da buck separato dietro load-switch.

**Budget che lo giustifica:** 1 servo in stallo (~1,5 A) + 1 servo in tenuta (≤ 300 mA, assunto) + stepper (~200 mA) + margine.

**Condensatore di bulk.** Il picco di stallo è breve e va assorbito prevalentemente dal bulk, non erogato in continuo dal regolatore: è ciò che permette di restare su 2,5 A anziché sovradimensionare.

**Acceptance [B].** Transitorio di stallo di un singolo servo con carico elettronico, secondo servo in tenuta e stepper in movimento: **nessun reset MCU**, ripple sul rail 3,3 V < 100 mV.

---

## 7. Checklist di rilascio

- [ ] STEP, DIR, EN, UART, DIAG su GPIO diretti dell'MCU
- [ ] Sense motori su ADC1
- [ ] Shunt 33 mΩ in package 1206, dissipazione verificata
- [ ] Fondo scala dell'INA180 ≤ 2,45 V a 2,5 A
- [ ] Filtro sull'uscita dell'amplificatore compatibile con i 200 ms di rilevazione battuta
- [ ] INA180 e rail servo alimentati dietro load-switch
- [ ] Bulk sul rail 5 V dimensionato sul transitorio di stallo
- [ ] Vincolo di ~100 mA/fase per il 28BYJ-48 documentato per il firmware
- [ ] Misura di stallo sui servo reali eseguita prima dell'ordine dei componenti di potenza
