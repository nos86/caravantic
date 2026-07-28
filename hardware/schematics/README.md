# Requisiti implementativi — schematico

Documenti di traduzione dei requisiti di sistema ([`specifica-di-sistema.md`](../../specifica-di-sistema.md)) in prescrizioni per la stesura dello **schema elettrico**.

## Perimetro

**Dentro:** topologie circuitali, criteri di selezione dei componenti, valori e dimensionamenti, reti di polarizzazione, connessioni e pinout logici, note di sicurezza funzionale.

**Fuori:** layout, piazzamento, routing, stackup, integrità di segnale, disegno meccanico del PCB. Dove una scelta di schema vincola il layout la nota è presente, ma la sua attuazione appartiene a una fase successiva.

## Documenti

| File | Sezione |
|---|---|
| [`01-power-supply.md`](01-power-supply.md) | Ingresso, protezioni, power-latch, regolatori, load-switch |
| [`02-mcu.md`](02-mcu.md) | Modulo ESP32-S3-Tiny, allocazione dei pin, boot e reset |
| [`03-inputs.md`](03-inputs.md) | 5 ingressi configurabili per depopolazione, protezione, debounce |
| [`04-outputs.md`](04-outputs.md) | 4 uscite high-side e a relè, interlock, stato sicuro |
| [`05-motors.md`](05-motors.md) | Driver stepper, servo, misura di corrente e finecorsa virtuali |
| [`06-interfaces.md`](06-interfaces.md) | CAN, I²C, I/O expander, LED, test point, connettori |

## Come leggerli

Ogni documento è organizzato per **blocco funzionale**. Ogni blocco riporta:

- **Topologia** — cosa disegnare
- **Dimensionamento** — valori, con il calcolo o il criterio che li giustifica
- **Selezione** — vincoli sul componente, da verificare a datasheet
- **Traceability** — i requisiti di sistema da cui discende

Le prescrizioni usano *shall* dove sono vincolanti e *dovrebbe* dove sono raccomandazioni con margine di scelta. I valori marcati **(da congelare)** richiedono una decisione o una misura prima del rilascio dello schema.

## Copertura dei requisiti di sistema

I 41 requisiti della specifica sono coperti da questi documenti con **tre eccezioni volute**, che non hanno effetto sullo schema elettrico:

| Requisito | Perché non è qui |
|---|---|
| **REQ-MECH-001** — form factor, fori M3, contenitore PETG | Vincola il PCB e il meccanico, non lo schema. Appartiene alla fase di layout |
| **REQ-SW-002** — HMI web e interfaccia macchina | Puramente firmware. I due trasporti che usa, WiFi e USB, esistono già e sono coperti da [`02-mcu.md`](02-mcu.md) |
| **REQ-TIM-001** — round-trip ≤ 250 ms | Vincolo di progetto firmware: a 125 kbit/s il tempo di bus è ~1 ms e non è il collo di bottiglia |

Ogni altro requisito compare nella riga **Traceability** di almeno un documento.

## Prima di iniziare

Cinque verifiche sono propedeutiche e sono elencate in §5 della specifica di sistema. Due condizionano lo schema in modo diretto e vanno chiuse per prime:

1. **Tabella di allocazione dei pin** completa (vedi [`02-mcu.md`](02-mcu.md)) — senza di essa il rischio è scoprire a schema avanzato che i GPIO non bastano.
2. **Consumo a riposo del modulo MCU** in deep-sleep, contro il budget di 1 mA — condiziona la necessità di dissaldare il LED RGB del modulo.

Le altre tre — misura di stallo dei servo, range di immagazzinamento dei componenti, supporto CiA 302-3 in CANopenNode — possono procedere in parallelo alla stesura.
