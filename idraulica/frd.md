# Caravantic — scheda idraulica: requisiti

Status: **Draft** · Derivato da [`../docs/frd.md`](../docs/frd.md) (divisione in due PCB, 2026-10-26). Contesto, requisiti comuni, riuso da `old/` e storico revisioni restano nel FRD comune. Scheda sorella: [`../elettrica/frd.md`](../elettrica/frd.md).

**Perimetro (Confirmed, utente 2026-10-26):** acque chiare, acque grigie, pompa, motori (valvola e pistone di scarico). La **pompa** non era nel FRD precedente: requisiti da scrivere (vedi §3, NEW-1). L'assegnazione dei singoli REQ a questa scheda è **Assumed** (da rivedere insieme).

Stato: Confirmed = dichiarato dall'utente · Assumed = ipotesi da confermare · Open = non risolto.

## 1. Requisiti

### 1.1 Elettrici

**REQ-EL-003** (Must, Open) — Pilotaggio valvola motorizzata scarico acque chiare (12 V) con **misura di corrente (Confirmed, utente 2026-10-14)**. Modello indicato dall'utente: U.S. Solid 1/2" a sfera in ottone, 9–24 V AC/DC, 3 fili, ritorno automatico, normalmente chiusa (Amazon B07CWMRZXK — fonte debole, rivenditore). Verifica 2026-10-14: nessuna corrente dichiarata a 12 V (costruttore: "max 2 W"; rivenditore, debole: ≤ 500 mA a tensione non specificata); il titolo Amazon "3 fili + ritorno automatico + NC" è contraddittorio col catalogo U.S. Solid (il 3 fili mantiene la posizione, l'auto-return è un 2 fili con condensatore). Identità del modello e cablaggio da verificare sull'unità reale (OPEN-04).
*Caso peggiore di progetto (Assumed, 2026-10-14, da sostituire con la misura):* I_run = 0,5 A, I_picco/stallo = 2 A a 10–14,6 V; il driver deve reggere 2 A per tutto il tempo di manovra (≤ 10 s) senza intervento. **Cablaggio (schema della scheda prodotto Amazon fornito dall'utente il 2026-10-14, fonte debole, da verificare con multimetro):** nero = − (massa), rosso a + = apre, blu a + = chiude (un filo alla volta, mai entrambi). Quindi il pilotaggio è di **2 interruttori high-side** (uno per senso) con **interblocco hardware** (mai rosso e blu insieme) e nero a massa; la misura di corrente può stare sul ritorno nero (shunt low-side, come REQ-IF-005 e rev. 1). Il 3 fili mantiene la posizione senza alimentazione: nessun fail-safe di chiusura (da decidere, OPEN-04). Il cablaggio contraddice la lettura di un rivenditore (rosso +, nero −, verde comando): vale lo schema dell'utente finché non si verifica l'unità.
*Acceptance:* misura di corrente con risoluzione ≤ 20 mA e fondo scala ≥ 2,5 A.

**REQ-EL-004** (Must, Open) — Pilotaggio bidirezionale del pistone elettrico (attuatore lineare 12 V) per scarico grigie, con **misura di corrente (Confirmed, utente 2026-10-14)**. Modello indicato dall'utente: VEVOR 12 V, corsa 152 mm, 1000 N, 14 mm/s, IP54 (Amazon, fonte debole; ASIN letto B0D31KPC4K ≠ B0D2ZLWWQV del link: variante da verificare). Verifica 2026-10-14: unico dato "assorbimento 5 A" (pagina VEVOR, ambiguo: non dichiarato se nominale o stallo), duty 25 %, nessuna protezione interna dichiarata, finecorsa e fili non documentati; manuale OK648 trovato è di un allestimento con corsa 4". Corrente di stallo e finecorsa da misurare (OPEN-04). Non implica più un ponte H a semiconduttori: l'utente ha scelto il relè STEIPU ST8N-2C-12S (2026-10-14); la topologia (due relè 1C a bobine separate, con frenata dinamica, + interruttore low-side) è **Assumed**, vedi `docs/components.md`. Rating del contatto NC non dato dal datasheet: da provare al banco.
*Caso peggiore di progetto (Assumed, 2026-10-14, da sostituire con la misura):* I_run = 5 A (dato di pagina), I_stallo = 10 A (2× il dato di pagina; il FAQ del venditore consiglia un alimentatore da 8 A, quindi lo stallo non è documentato), nessuna protezione interna. **Finecorsa interni: l'utente acquisterà un attuatore che li ha (Confirmed, 2026-10-14)**; il VEVOR non è più vincolante e il modello definitivo sarà scelto con questo criterio (da registrare); resta da verificare che i finecorsa interrompano il motore nei due sensi e se espongano un segnale. Ponte H e linee di potenza dimensionati per ≥ 10 A di picco; protezione a carico della board: limite di corrente, timeout di manovra e fusibile a monte.
*Acceptance:* misura di corrente con fondo scala ≥ 12 A e risoluzione ≤ 100 mA; rilevazione di stallo/fine corsa dalla corrente.
**Soglia di lavoro massima: 7 A (Confirmed, utente 2026-10-15).** Il firmware spegne ENA se la corrente misurata supera 7 A (dopo il blanking dello spunto) entro 200 ms; il relè K1 (limite continuo 8 A) e la catena di potenza non devono mai portare più di 7 A in regime. Lo stallo assunto a 10 A (Assumed) resta un caso di guasto da interrompere, non di funzionamento. *Se gli I/O passano su expander I²C (REQ-IF-012):* lo spegnimento resta firmware, senza percorso indipendente dal bus; il doppio guasto "bus bloccato + finecorsa difettoso" è accettato (Confirmed, utente 2026-10-22).

**REQ-EL-005** (Must, Confirmed/Open) — **4 uscite a relè generiche, contatto N.O.** (Confirmed, utente 2026-10-14), non più dedicate alla sola telecamera scarico grigie (primo carico previsto). Portata contatti e tipo di carichi per canale da definire (OPEN-13); se ≤ 2 A riuso dello stadio relè rev. 1 (IM06 + BSS138), replicato ×4.

### 1.2 Interfaccia / protocollo

**REQ-IF-003** (Must, Confirmed) — Livello serbatoio acque chiare da sender resistivo a galleggiante tipo automotive, **0–190 Ω**, verso massa.
*Rationale:* scelta utente. *Acceptance:* lettura monotona su tutta la corsa; errore ≤ ±5 % fondo scala dopo taratura a 3 punti (vuoto, metà, pieno) — soglia Assumed.
Note: verso della caratteristica (0 Ω = vuoto o pieno) da verificare sul pezzo (OPEN-15); eccitazione sezionabile e fondo scala ADC ≤ 2,45 V (riuso rev. 1).
*Interfaccia (Confirmed, utente 2026-10-15):* connettore JST XH. *Circuito provvisorio (Assumed, rev. 2026-10-17):* misura ratiometrica con INA219 (V_bus / I_shunt, eccitazione impulsata da GPIO, ≈ 4–10 mA; errore atteso 1,5 % FS p95 dai limiti del datasheet) con protezione a valle del nodo di lettura e offset opzionale (Rb, non popolata), in [`schematic/a4_serbatoio_chiare.md`](schematic/a4_serbatoio_chiare.md). INA219 verificato sul datasheet TI Rev. G. **Nessuna rete di clamp sul nodo del livello: scostamento dalla convenzione accettato (Confirmed, utente 2026-10-17); tenuta a 24 V per il rating dell'INA219 (26 V).**

**REQ-IF-004** (Must, Confirmed) — Sensore di temperatura montato sul serbatoio acque chiare: **Maxim/ADI DS18B20, 1-Wire (Confirmed, utente 2026-10-15)**, connettore JST XH. Cablaggio a 3 fili (VDD, DQ, GND) (Assumed: il modo parassita è escluso). **VDD collegato direttamente al 3V3, senza protezione da guasto: rischio accettato (Confirmed, utente 2026-10-15)**; un guasto > 3,6 V sul filo VDD retroalimenta il 3V3. Scopo e range operativo ancora da definire (OPEN-05). Circuito in `a4_serbatoio_chiare.md` (Assumed).
*Acceptance:* [B] il sensore è rilevato dal firmware e legge la temperatura ambiente entro ±1 °C di un riferimento; [B] 24 V continui per 5 min su DQ senza danno (VDD escluso, vedi a4); [B] lettura stabile con il cavo reale.

**REQ-IF-009** (Must, Open) — Interfaccia verso comando remoto in cabina per lo scarico serbatoi (lato remoto: ESP8266/RP2040). Proposta in OPEN-07.

**REQ-IF-011** (Must, Open) — Ingresso dedicato per la sonda di pieno del serbatoio acque grigie, oggi collegata al morsetto 13 ("WASTE WATER TANK", 2 poli) del CBE DS300. Funzione: rilevare in HA il serbatoio grigie pieno. Tipo di sonda e livelli elettrici **non noti**: il manuale CBE PC100/PC200/DS300 la descrive solo come "tank probe with screws SS/P" (sonda a viti, segnalazione di pieno), senza tensione di eccitazione, polarità, soglia né corrente ([manuale](https://camperforum.nl/handleidingen/cbe/CBE_PC100_PC200_DS300_EN.pdf), copia di terzi del manuale CBE; un forum di camperisti ([camperonline](https://www.camperonline.it/forum/tecnica/cellula-abitativa/sensore-acque-grigie-dubbio-collegamento/233577), fonte debole) conferma 2 fili con faston, rilevazione per continuità attraverso l'acqua). Si assume sonda **conduttiva a due elettrodi** (Assumed). Se la sonda resta anche sul DS300 (parallelo) o viene spostata: da decidere (OPEN-14).
*Circuito provvisorio (Assumed, 2026-10-15):* eccitazione impulsata da GPIO (10 ms/5 s), partitore + lettura ADC1, protezione di campo (Rp + clamp), stato sicuro per pull-down; schema e ipotesi H1–H5 in [`schematic/a3_sonda_grigie.md`](schematic/a3_sonda_grigie.md). Soglia "pieno" proposta R_w ≈ 26 kΩ (V = 2,0 V), non misurata.
*Acceptance:* [B] stato "pieno" con sonda immersa nell'acqua del serbatoio e "vuoto" con sonda asciutta; [B] 24 V e −16 V continui sull'ingresso per 5 min senza danno; [B] corrente di eccitazione ≤ 0,2 mA. Soglie da confermare dopo OPEN-14.

## 2. Punti aperti

| ID | Domanda | Requisiti |
|---|---|---|
| OPEN-04 | Nessun datasheet con correnti trovato (verifica 2026-10-14). **Da misurare sulle unità reali a 10 V e 12 V:** corrente a vuoto/carico/stallo e comportamento ai finecorsa di valvola e pistone; cablaggio valvola (schema utente: nero −, rosso apre, blu chiude, da verificare con multimetro; il motore si ferma a fine corsa?; fail-safe); modello definitivo del pistone (con finecorsa interni, Confirmed 2026-10-14; il VEVOR è solo un candidato) e sua corrente di stallo | EL-003, EL-004 |
| OPEN-05 | Sensore temperatura serbatoio: tipo chiuso 2026-10-15 (DS18B20). Resta: scopo (solo monitoraggio / avviso antigelo / azione automatica?), lunghezza del cavo (~~VDD protetto da 24 V~~: deciso, nessuna protezione) | IF-004 |
| OPEN-07 | Interfaccia comando cabina — vedi §4 | IF-009 |
| OPEN-13 | 4 relè generici: carichi previsti per canale, corrente/tensione contatti, solo 12 V DC o anche 230 V AC, assorbimento bobine | EL-005 |
| OPEN-14 | Sonda grigie (morsetto 13 DS300): da misurare con multimetro sul DS300 reale — tensione a vuoto fra i due poli (DC/AC, polarità), corrente di corto, resistenza della sonda in aria e immersa/sporca; sonda spostata sulla board o in parallelo al DS300? | IF-011 |
| OPEN-15 | Sender livello chiare: da misurare con multimetro sul pezzo reale — resistenza a vuoto e a pieno (verso: 0 Ω = vuoto o pieno?), 2 fili o corpo a massa, corrente massima tollerata, lunghezza cavo | IF-003 |
| NEW-1 | **Pompa**: tipo (12 V DC?), corrente di spunto/regime, comando (on/off o PWM?), protezione a secco, misura di corrente? Nessun requisito scritto: usare la skill `hardware-requirements-engineer` | — |

## 3. Registro assunzioni

- Correnti di valvola (0,5 A run / 2 A picco) e pistone (5 A run / 10 A stallo): ipotesi di caso peggiore, non da datasheet (EL-003, EL-004, OPEN-04). Il rapporto fra i due fondo scala (2,5 A vs 12 A) suggerisce due canali di misura separati: **deciso dall'utente il 2026-10-14 (Confirmed)**, f.s. 2,5 A (valvola) e 12 A (pistone). Catena in `docs/components.md` sez. A2 (Proposto).

## 4. Proposta OPEN-07 — interfaccia comando cabina

| Opzione | Cavo | Pro | Contro |
|---|---|---|---|
| **A. RS485 condiviso con SDM120** (remote = slave Modbus) | 4 fili: +12 V, GND, A, B | Nessun transceiver aggiuntivo sulla board; differenziale, robusto su cavi lunghi | Guasto sul cavo cabina blocca anche la lettura SDM120; latenza legata al polling |
| B. RS485 dedicato | 4 fili | Isola i due bus | Secondo transceiver e UART (UART già contesi, OPEN-09) |
| C. Solo Wi-Fi (ESP8266 → HA) | 2 fili (alimentazione) | Cablaggio minimo | Comando di scarico dipende da Wi-Fi e HA |
| D. Discreti 12 V (pulsanti + LED, nessun MCU nel remote) | ~6 fili | Massima semplicità, nessun firmware remoto | Più fili, ingressi/uscite in più sulla board |

Raccomandazione: **A** — coerente con REQ-IF-010 (bus estendibile): il comando cabina è uno slave come gli altri.
