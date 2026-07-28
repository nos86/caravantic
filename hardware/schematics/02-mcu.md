# 02 — Microcontrollore

Requisiti implementativi per l'integrazione del modulo MCU, l'allocazione dei pin e i circuiti di boot e reset.

**Traceability:** §4 della specifica di sistema, REQ-IF-003, IF-011, MECH-002, SAFE-003, SW-004, SW-005, DIAG-002, EL-005, EL-006.

---

## 1. Modulo

**Componente: Waveshare ESP32-S3-Tiny**, montato sulla scheda portante anziché saldare un WROOM-1.

| Caratteristica | Valore |
|---|---|
| SoC | ESP32-S3FH4R2, dual-core LX7 240 MHz |
| Memoria | 4 MB Flash + 2 MB PSRAM in package, 512 KB SRAM, 16 KB RTC SRAM |
| GPIO portati | 34 |
| Ingombro | ~23,5 × 18 mm |
| USB e pulsanti | Su **scheda adattatrice separata**, collegata via FPC 8 pin |

**Motivazione.** Il modulo porta a bordo alimentazione, oscillatore, antenna e circuito di boot già validati: riduce i componenti da posizionare a mano e toglie dal progetto le sezioni critiche di layout RF.

### 1.1 Alimentazione del modulo

Alimentato dal **rail 3,3 V always-on** a valle del power-latch. In OFF il latch lo disalimenta completamente, quindi i suoi circuiti parassiti non pesano sul consumo di rimessaggio.

> **Verifica propedeutica.** In **deep-sleep** il modulo è alimentato: il suo regolatore di bordo e il **LED RGB indirizzabile su GPIO 14** concorrono al budget di 1 mA. Il produttore non dichiara il valore. Da misurare sul modulo reale; se eccessivo, il LED si dissalda.

### 1.2 Vincoli di integrazione

- **Keep-out di antenna** sulla scheda portante: nessun rame, piano o traccia sotto e attorno all'area di antenna del modulo, che va posizionato **a filo del bordo**.
- Il **connettore FPC** shall restare fisicamente accessibile a scheda montata: è la via di programmazione e di monitor seriale.
- Il range di temperatura del SoC non è critico con l'operativo 0…+40 °C, ma il modulo rientra fra i componenti per cui va **verificato e annotato anche il range di immagazzinamento**.

---

## 2. Allocazione dei pin

> **Da produrre prima di procedere con lo schema.** È l'attività a costo nullo che elimina il rischio di scoprire a schema avanzato che i GPIO non bastano.

### 2.1 Bilancio

| Funzione | GPIO | Destinazione |
|---|---|---|
| 5 ingressi configurabili | 5 | MCU diretto |
| 4 uscite di potenza (PWM) | 4 | MCU diretto |
| TMC2209: STEP, DIR, EN, UART, DIAG | 5–6 | MCU diretto |
| 2 PWM servo | 2 | MCU diretto |
| Sense corrente motori | 1 | MCU diretto, **ADC1** |
| CAN: TX, RX, STB | 3 | MCU diretto |
| I²C: SDA, SCL | 2 | MCU diretto |
| Power-hold | 1 | MCU diretto |
| WAKEUP | 1 | MCU diretto, **dominio RTC** |
| 2 LED CANopen + LED di stato | — | **I/O expander** |
| Enable dei load-switch | — | **I/O expander** |
| **Totale su MCU** | **24–25** | |

Dai 34 pin del modulo vanno sottratti due impegnati dall'USB nativo, uno dal LED RGB di bordo e tre o quattro pin di strapping non utilizzabili per le funzioni vincolate: il margine residuo è di **5–6 pin**.

**Senza I/O expander il bilancio non chiude.** È la ragione per cui l'expander è un requisito e non un'opzione.

### 2.2 Vincoli di assegnazione

Vincoli **inderogabili**, da rispettare nella tabella di allocazione:

1. **ADC1 obbligatorio** per il sense di corrente motori e per ogni ingresso analogico. I canali ADC2 non sono utilizzabili in modo affidabile con WiFi attivo, e poiché la board è identica su tutti i nodi qualsiasi nodo può diventare bridge.
2. **Nessuna uscita di potenza e nessun LED sui pin di strapping**: al boot assumono livelli imposti dal bootloader, incompatibili con lo stato sicuro richiesto.
3. **WAKEUP su pin del dominio RTC**, altrimenti non può risvegliare l'MCU dal deep-sleep.
4. **GPIO 14 impegnato** dal LED RGB del modulo: non riassegnare, salvo rimozione del LED.
5. I pin dell'**USB nativo** sono impegnati dalla scheda adattatrice.

### 2.3 Criteri di preferenza

- Raggruppare le funzioni di uno stesso blocco su pin contigui, per leggibilità dello schema.
- Assegnare a PWM i pin serviti da timer indipendenti, così che le 4 uscite e i 2 servo possano avere frequenze diverse.
- Lasciare liberi i pin superstiti e portarli su test point o pad: è la riserva per gli imprevisti.

---

## 3. Boot, reset e programmazione

**Prescrizione.** La scheda portante **non** shall prevedere convertitore USB-seriale proprio: programmazione e monitor seriale passano dalla scheda adattatrice del modulo.

**Circuito di boot.** Il modulo integra il circuito di download automatico. Sulla portante non replicare la logica DTR/RTS.

**Accessibilità.** Connettore FPC e pulsanti BOOT/RESET dell'adattatore accessibili a scheda montata (REQ-MECH-002).

### 3.1 Canali di aggiornamento firmware

| Canale | Copertura | Note di schema |
|---|---|---|
| **USB cablato** | Qualsiasi nodo, con accesso fisico | Nessun componente sulla portante |
| **OTA su CANopen** | Qualsiasi nodo, da remoto | Nessun componente aggiuntivo: usa il transceiver esistente |
| **OTA su WiFi** | Solo nodo bridge | Nessun componente aggiuntivo |

**Nessuno dei tre canali richiede hardware dedicato sulla portante.** L'unico vincolo che ne discende è il budget di Flash.

> **Vincolo di Flash.** L'OTA richiede **due partizioni applicative**, che impegnano la maggior parte dei 4 MB. Restano compatibili con l'HMI **solo se il frontend Vue è ospitato esternamente**; servirlo dalla board renderebbe verosimilmente insufficienti i 4 MB.

---

## 4. Watchdog e memoria non volatile

Entrambi integrati nell'MCU: **nessun componente esterno**.

- **Watchdog** abilitato, con reset che porta le uscite nello stato sicuro passivo.
- **Memoria non volatile** per Node-ID assegnato via LSS, parametri di debounce, limiti di corrente motori e calibrazioni.

**Identificativo di nodo.** Il Node-ID CANopen è assegnato dinamicamente via LSS usando come serial-number il **Base MAC address** dell'ESP32-S3, letto da eFuse.

> **Non prevedere DIP-switch né jumper** per il Node-ID. Nessun selettore fisico, nessun ingombro, nessuna configurazione manuale in produzione.

**Conseguenza da documentare.** Il Node-ID non è leggibile a vista sulla scheda: serve un tool di diagnostica per associare scheda fisica e Node-ID. Mitigazione a firmware, esponendolo in telemetria.

---

## 5. Checklist di rilascio

- [ ] Tabella di allocazione dei pin completa e verificata contro i cinque vincoli inderogabili
- [ ] Sense di corrente e ingressi analogici su ADC1
- [ ] Nessuna uscita di potenza né LED su pin di strapping
- [ ] WAKEUP su pin RTC
- [ ] Keep-out di antenna rispettata, modulo a filo del bordo
- [ ] Connettore FPC accessibile a scheda montata
- [ ] Consumo del modulo in deep-sleep misurato contro il budget di 1 mA
- [ ] Pin liberi portati su test point
