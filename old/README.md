# Caravantic IO-Board

Scheda di interfaccia tra la domotica governata da **Home Assistant** e l'impianto elettrico tradizionale di un camper di metà anni 2000: batteria servizi 12 V, utenze a relè, sensori analogici e digitali.

Il sistema è una **rete multi-nodo di schede identiche** collegate via CAN-Bus a 125 kbit/s, con protocollo applicativo **CANopen**. Un nodo qualsiasi può assumere il ruolo di **bridge** verso Home Assistant via WiFi; gli altri tengono la radio spenta.

## Cosa fa una scheda

| Sezione | Contenuto |
|---|---|
| **Ingressi** | 5 canali configurabili per depopolazione: contatto secco 3,3 V, opto-isolato 12 V, analogico in tensione, o resistivo con eccitazione a bordo per NTC |
| **Uscite** | 4 canali configurabili per depopolazione: MOSFET high-side 2 A con PWM per dimming LED, relè 10 A, o variante ibrida con interlock |
| **Motori** | 1 stepper (28BYJ-48 modificato bipolare o NEMA17) via TMC2209 e 2 servo RC, con finecorsa virtuali basati sull'assorbimento |
| **Rete** | CAN 2.0 a 125 kbit/s, CANopen con Node-ID assegnato dinamicamente via LSS |
| **Espansione** | Bus I²C su connettore, più I/O expander a bordo |

I carichi commutati hanno **alimentazione propria esterna**: la board fornisce solo il contatto.

## Stato del progetto

**Specifica di sistema congelata** (rev. A) — 41 requisiti, nessun punto aperto. Prossimo passo: schematico.

Le scelte principali già decise:

- Microcontrollore **ESP32-S3** come modulo preassemblato Waveshare ESP32-S3-Tiny
- Alimentazione **12 V**, compatibile sia con piombo-acido sia con LiFePO4 4S; catena di ingresso con rating ≥ 40 V
- Uscite **high-side** con P-MOSFET discreto e level-shifter, PWM a 1,5–2 kHz
- Due stati a basso consumo: **OFF** con power-latch e **deep-sleep** con risveglio da bus CAN
- PCB entro **100 × 100 mm**, contenitore custom stampato in 3D in PETG
- Lotto di **20 pezzi**, assemblaggio in-house con posizionamento manuale e reflow

## Documenti

| Documento | Contenuto |
|---|---|
| [`specifica-di-sistema.md`](specifica-di-sistema.md) | Requisiti di sistema e funzionali, registro delle assunzioni, fonti. È il riferimento normativo del progetto |
| [`hardware/schematics/`](hardware/schematics/) | Requisiti tecnici e implementativi per la stesura dello schematico, divisi per sezione funzionale |

La specifica di sistema dice **cosa** deve fare la scheda e perché; i documenti in `hardware/schematics/` dicono **come** realizzarlo a livello di schema elettrico. Ogni requisito implementativo è tracciato al requisito di sistema che lo origina.

### Convenzioni

- **Livelli di verifica.** Ogni criterio di accettazione è marcato `[B]` se verificabile in banco con strumentazione ordinaria, `[D]` se dimostrato per selezione del componente e confronto a datasheet. Il progetto non è certificato e non dispone di laboratorio di qualifica, quindi non esistono requisiti che richiedano prove normalizzate.
- **Stato dei requisiti.** `Confirmed` = deciso; `Assumed` = ipotesi tracciata nel registro delle assunzioni.
- **BOM.** Package resistori 0805 di default, 1206 dove il dimensionamento di potenza lo richiede. Nessun BGA, nessun passivo sotto 0603: l'assemblaggio è a posizionamento manuale.

## Fuori scopo

Certificazioni formali (CE/E-mark), gestione della batteria e della ricarica, integrazione con bus proprietari del camper (CBE/CI-BUS). Il contenuto funzionale dell'HMI web e il protocollo di dettaglio dell'aggiornamento firmware sono rimandati a una specifica firmware/HMI separata, da redigere dopo la realizzazione dell'hardware.
