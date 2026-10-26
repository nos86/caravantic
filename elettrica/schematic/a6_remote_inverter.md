# Schematico A6 — Interfaccia remote inverter Renogy (specifica di disegno)

Requisito: REQ-IF-007 (Must, Confirmed). Punto aperto: OPEN-02. **Nessun part number scelto**: il dimensionamento dipende da misure non ancora fatte. Stato di tutto ciò che segue: **Proposto / Assumed**.

## Architettura attuale sul foglio (2026-10-18, descrizione utente; vale al posto delle sezioni "Topologia", "Analisi", "Revisione" e "Decisione utente" sotto, tutte SUPERATE per relè e pilotaggio)

Due soli relè **Omron G6K-2F-Y-TR DC12** (non tre, non IM06), ciascuno pilotato da un BSS138 low-side:

| Relè | Net di comando | Funzione | A riposo (diseccitato, NC) | Eccitato (board accesa) |
|---|---|---|---|---|
| **K2** (Q4) | `CMD_INVERTER_CTRL` | **chi controlla l'inverter** | **remote** (RJ2) collegato direttamente all'inverter (RJ1): IF-007 d | **board** (presa in carico): il remote è staccato dai segnali di comando |
| **K3** (Q8) | `CMD_INVERTER_STATE` | **stato dell'inverter comandato dalla board** | inverter **spento** (nessun +12 V forzato su VIN) | inverter **acceso** (+12 V su VIN) |

- **K2 e K3 lavorano solo sul contatto VIN / +12 V** (pin 3 e 5): i LED (pin 4 e 7) non passano dai relè, sono gestiti dalla logica a parte (celle TLP293 U15/U16 + specchio Q9/Q10, nodi GREEN/RED bidirezionali, vedi "Rettifica 2026-10-18 (sera)").
- K3 ha effetto solo con K2 eccitato. Con K2 diseccitato il remote comanda comunque, qualunque sia K3.
- Sequenza firmware: prima K3 = stato attuale del remote (letto da `SIG_INVERTER_REQ`, U17), poi K2; HA può poi forzare K3. In reset e a board spenta entrambi i relè sono diseccitati (sole reti passive, SW-002) ⇒ remote diretto.
- Punto chiuso 2026-10-18 (utente): i relè commutano solo VIN/+12 V; i drain di Q9/Q10 (R57/R58) vanno ai pin 4/7 di RJ2 senza relè, per scelta di progetto. Resta solo da rileggere sul foglio a quale nodo va il polo NO di K3 (+12 V con R serie, come in "Rischi" sotto).
- Pilotaggio: GPIO → R50/R60 1 kΩ → gate; R49/R59 47 kΩ gate–GND. Dettagli e designatori nella sezione "Designatori sul foglio EasyEDA" in fondo.

## Piedinatura (Renogy Support, CASE2025080300065, 9 ago — Assumed)

RJ45 T568B, vista dal disegno del costruttore:

| Pin | Segnale | Lato inverter | Note |
|---|---|---|---|
| 1 | NC | — | |
| 2 | GND | massa | |
| 3 | +12 V | uscita inverter | tensione e portata ignote |
| 4 | VERDE | uscita LED POWER | livello ignoto (forum: 2,7–3,8 V) |
| 5 | VIN | ingresso inverter | contatto del remote fra 3 e 5 |
| 6 | NC | — | |
| 7 | ROSSO | uscita LED FAULT | livello ignoto |
| 8 | NC | — | |

Discrepanza col forum (verde pin 2, rosso 4, massa 7): contatto 3–5 coincide, i pin LED no. Vale il costruttore, da verificare con il multimetro. Lettura del disegno (NC su 1, 6, 8) confermata dall'utente il 2026-10-17; la verifica sul pezzo resta da fare.

## Topologia proposta (a monte delle misure)

Due connettori RJ45: **J_INV** (verso inverter) e **J_REM** (verso remote). Pin 2, 3, 4, 7 passanti diretti da J_INV a J_REM. Solo il pin 5 (VIN) passa da un relè.

- **K1, scambio a riposo trasparente** (SPST-CO sul solo VIN): comune = VIN lato inverter, NC = VIN del remote, NO = nodo `VIN_BRD`. Board spenta o in reset ⇒ K1 diseccitato ⇒ remote collegato direttamente (IF-007 d).
- **Comando dalla board** (K1 eccitato): `VIN_BRD` = +12 V (pin 3) tramite un secondo contatto K2 ⇒ ON; aperto ⇒ OFF. Tre stati: passante / forzato ON / forzato OFF, per questo servono due uscite GPIO (`INV_TAKE`, `INV_ON`). Interblocco solo software; entrambe a riposo con pull-down (SW-002).
- **Lettura dell'interruttore del remote** (`REM_SW`): nodo pin 5 lato remote, con pull-down ≥ 100 kΩ e resistore serie + clamp verso 3,3 V e massa (convenzione di progetto). Con K1 eccitato il pin 5 del remote è isolato dall'inverter, quindi la lettura resta valida anche mentre la board comanda.
- **Lettura LED** (`INV_LED_G`, `INV_LED_R`): derivati dai pin 4 e 7 lato inverter, a monte del remote, ad alta impedenza (≥ 100 kΩ, Assumed). Il verso del LED nel remote (anodo al pin o a +12 V) decide il tipo di ingresso: **da misurare**. Se i livelli sono ~2,7 V la soglia logica dell'ESP32-S3 è al limite: valutare ADC1 (≤ 2,45 V, partitore) invece di GPIO digitale.

Alternativa a K2 + K1: un solo relè bistabile; scartata per ora perché in reset non garantisce lo stato passante.

## Rischi e assunzioni fragili

1. **Natura di VIN ignota**: se VIN richiede corrente apprezzabile o ha soglia che dipende dal valore di +12 V, un contatto relè (signal) basta ma va dimensionato; se +12 V (pin 3) è la batteria non regolata, il relè e i fili vedono fino a 14,6 V (o 16 V di sopravvivenza).
2. **Pin 3 è alimentazione del remote** (cicalino sui RJ45): K2 non deve mai metterlo in corto con GND; limitare con resistore serie sul nodo `VIN_BRD`.
3. **Cavo remote lungo** (camper): disturbi e ESD sui pin 4/5/7; serve protezione di campo su tutte le linee lette.
4. Selettore 0/I/II dell'inverter: in posizione diversa da II il remote è ignorato — HA non può accendere. Da gestire in diagnostica, non in hardware.
5. Piedinatura non ancora verificata sul pezzo reale.

## Misure da fare sull'inverter (chiudono OPEN-02)

Con remote **scollegato**, multimetro su RJ45 inverter, inverter in posizione II, poi con remote collegato:
1. Tensione a vuoto pin 3–2 (acceso e spento).
2. Tensione pin 5–2 a contatto aperto; corrente pin 3→5 in corto (amperometro) — dà portata richiesta ai relè.
3. Tensione pin 4–2 e pin 7–2 in stati: spento, acceso, fault (se riproducibile); poi corrente di corto verso GND (portata dei pin LED).
4. Ripetere con remote collegato per vedere l'effetto del LED/cicalino.
5. Ohmetro nel remote: verso dei LED, continuità del contatto, presenza del cicalino.

## Analisi del 2026-10-18 — riuso dei componenti esistenti (SUPERATA per relè, LED via A/B e conteggio componenti)

### 1) Relè: ~~TE Axicom IM06~~ → **Omron G6K-2F-Y-TR DC12** miniaturizzato (2026-10-18, vedi components.md; IM06 = riserva), bobina 12 V

- Due relè: **K_TAKE** (polo 1 = scambio su VIN: C = VIN inverter, NC = VIN remote, NO = `VIN_BRD`) e **K_LVL** (polo 1: C = +12 V pin 3 tramite R serie, NO = `VIN_BRD`). Il secondo polo di ciascuno resta libero (regola rev. 1: mai in parallelo al primo).
- Pilotaggio identico a EL-005: BSS138 low-side + 1N4148WS di ricircolo + pull-down di gate 100 kΩ. A riposo: entrambi diseccitati ⇒ remote diretto (IF-007 d, SW-002) con sole reti passive.
- Bobina: 1029 Ω ⇒ 11,7 mA a 12 V, 15,5 mA a 16 V; due relè ≈ 23–31 mA, trascurabile.
- Perché IM06: relè da segnale, contatti adatti a bassa corrente; dati rev. 1 già letti a datasheet (finestra 10–16 V). **Da riverificare per rev. 2** (carico minimo, pick-up a 10 V alta temperatura, disponibilità LCSC): verifica del 2026-10-18 in `elettrica/components.md`: **pick-up 9,0 V a 25 °C, probabilmente ~10,6–11,2 V a 70–85 °C ⇒ a 10 V di batteria può non chiudere**. Opzioni: relè con bobina 5 V alimentata dal rail +5V (stesso IM06 in variante 5 V, da verificare), o relè con soglia più bassa. Da decidere.
- Scartati: ST8N-2C-12S (pistone, contatti di potenza, bobina più grande: inutile per milliampere); stato solido: perde l'isolamento fra il dominio inverter e la board.
- Rischio: **commutazione di K_TAKE break-before-make**: per qualche ms VIN è fluttuante. Sequenza firmware: prima K_LVL = stato attuale del remote (letto da `REM_SW`), poi K_TAKE. Se l'inverter reagisce ai fronti di VIN (non si sa) il glitch lo spegne: da provare al banco.

### 2) Stadio di lettura

| Segnale | Soluzione proposta | Riuso | Dipende da |
|---|---|---|---|
| `REM_SW` (pin 5 lato remote, con contatto chiuso = +12 V) | cella 12 V di EL-006: R 8,2 kΩ + BZT52C3V3 + 1N4148WS + TLP293-GB + pull-up 12 kΩ a 3V3. LED dell'opto fra pin 5 e **pin 2 (GND inverter)**: dominio isolato dalla board | tutta la cella (stesso BOM) | tensione pin 3 ≥ 8 V a contatto chiuso |
| Presenza +12 V inverter (pin 3), opzionale diagnostica | seconda cella identica fra pin 3 e pin 2 | idem | serve? (punto 3 della richiesta?) |
| `INV_LED_G`, `INV_LED_R` (pin 4, 7 lato inverter) | **non risolto**: due vie, scelta dopo le misure (sotto) | — | corrente e livello dei pin LED, massa comune |

Perché l'opto sul remote switch: il contatto del remote regge ~1 mA senza problemi, e la cella ha già simulazione e soglie (attivo ≥ 8 V, inattivo ≤ 2 V). Carico aggiunto su VIN: ~1 mA a 12 V; se VIN è un ingresso ad alta impedenza va bene, **da misurare**.

**LED, via A — opto TLP293 (stesso dominio isolato).** Corrente minima utile 0,5 mA (CTR garantito); con livello 2,7 V: R ≈ (2,7 − 1,2)/0,5 mA ≈ 3 kΩ. Confligge con "≥ 100 kΩ, nessuna variazione visibile": accettabile solo se la corrente di pilotaggio del LED nel remote è molto maggiore (≳ 5 mA) e il pin tiene 2,7 V sotto carico.
**LED, via B — alta impedenza riferita alla massa board:** 100 kΩ serie + clamp BAT54S verso 3V3/GND come A3, ingresso GPIO digitale o ADC1. Richiede **pin 2 collegato a GND board**: crea un secondo percorso di massa (cavo sottile) in parallelo al percorso inverter→shunt→batteria, in tensione con la regola "massa board in un solo punto sul lato batteria dello shunt" (a5). Se il negativo dell'inverter è sul lato carichi, con 100+ A cade fino a ~75 mV + cavo e i livelli ~2,7 V restano leggibili, ma il collegamento va deciso consapevolmente. A livelli 2,7 V la soglia VIH del GPIO (≈ 0,75·3,3 = 2,5 V) lascia solo ~0,2 V: meglio ADC1 con soglia in firmware.
**ADS1115 (a5): non utilizzabile**, tutti e quattro gli ingressi sono già impegnati dai due shunt.

Raccomandazione provvisoria (da confermare con le misure): `REM_SW` via opto (via certa), LED via **B su ADC1** se le misure mostrano corrente LED < ~2 mA o massa comune; via A solo se la corrente LED è ≳ 5 mA.

### Misure aggiuntive che decidono la via LED
- Corrente di corto del pin 4/7 verso pin 2 (mA) e tensione a vuoto (già in elenco).
- Il negativo dell'inverter è sul lato carichi o sul lato batteria dello shunt? Tensione fra pin 2 dell'RJ45 inverter e GND board con inverter in carico.

## Revisione 2026-10-18 — LED proxati dalla board (decisione utente; sostituisce "LED via A/B" sopra)

Il comando +12 V / VIN resta come concordato (K_TAKE, K_LVL, passante a riposo). I due LED non sono più letti in alta impedenza: la board **li legge dall'inverter e li ripropone al remote** (proxy).

- **K_LED** (terzo IM06, stesso pilotaggio BSS138 + 1N4148WS + pull-down): pin 4 e 7 passano dai due scambi. A riposo (NC) inverter→remote diretto (IF-007 d invariato, LED compresi); eccitato, il remote è staccato dall'inverter e i LED sono pilotati dalla board. K_LED è necessario: senza, l'uscita dell'inverter e quella della board pilotano lo stesso filo. Si eccita insieme a K_TAKE (un solo GPIO può pilotare entrambe le bobine, ~23 mA).
- **Lettura dall'inverter:** due celle TLP293-GB, LED opto fra pin 4 (o 7) e pin 2 (GND inverter), R serie ≈ 2,2 kΩ (da ricalcolare con le misure). Dominio isolato, nessun legame fra GND inverter e GND board, e il carico sul pin non è più un vincolo perché il remote non è più su quella linea. Resta da misurare che il pin regga ≥ 0,5 mA a 2,7 V.
- **Pilotaggio del remote** *(SUPERATO il 2026-10-18 dalla decisione utente "LED del remote dalla 3V3 della board", sezione seguente; i 2 TLP293 di drive escono dalla distinta)*: il ritorno dei LED nel remote è il pin 2 (GND inverter, passante). Il drive deve quindi stare nel dominio inverter: due TLP293 con fototransistore **collettore a pin 3 (+12 V inverter) tramite R serie, emettitore sul pin 4 (o 7)**. R = (12 − 0,3 − V_F LED)/I_LED: con 2 mA circa 4,7 kΩ. Corrente limitata dal CTR saturo (GB min 30 %): I_F ≈ 7 mA per 2 mA di LED. Alternativa scartata: GPIO della board direttamente sui pin, che riporterebbe la massa della board sul cavo.
- **Da misurare sul remote** (ohmmetro/prova diodo): se i LED hanno una resistenza interna; corrente dei LED con l'inverter originale; cicalino sulla linea o sul +12 V. Se il remote ha già una R interna tarata su ~3 V, R serie e corrente cambiano.
- **Totale componenti per l'interfaccia:** 3 IM06 (o 2 + un TLP293 al posto di K_LVL se VIN ≲ 1 mA), 5 TLP293-GB (REM_SW, 2 lettura LED, 2 drive LED), una cella 12 V in più per la presenza pin 3 se serve.
- **Rischi nuovi:** commutazione di K_LED = LED spenti per qualche ms; tre bobine in più sul rail; il verso reale delle uscite LED (high-side vs open-collector) non è noto: se sono open-collector il pin a riposo sta a +V del remote e lo schema di lettura cambia.

## Schema del remote RJ11 (fornito dall'utente 2026-10-18, fonte e modello ignoti: **debole**)

RJ11 6 poli: 1 GND · 2 LED-R · 3 e 4 = contatto **SW-PB** · 5 LED-G · 6 GND. Ogni LED: anodo al pin tramite **R 1 kΩ**, catodo a GND; nessun pin +12 V.
Conseguenze (se il remote RJ45 è simile, da verificare sul pezzo):
- **LED pilotati dall'inverter a livello logico**: corrente LED ≈ (V_pin − V_F)/1 kΩ ≈ 0,5–1,8 mA a 2,7–3,8 V. Una lettura via opto (≥ 0,5 mA) ruberebbe metà o più della corrente del LED, quindi **via A scartata**; resta la **via B** (alta impedenza, ADC1) con pin 2 = GND board da decidere (vedi sopra).
- Il simbolo è un **pulsante (SW-PB)**: se il remote è un pulsante momentaneo e l'inverter commuta sul fronte, il comando va dato con un **impulso**, non con un livello; K_LVL/K_TAKE cambiano ruolo. Da chiarire col remote reale: interruttore a levetta (mantenuto) o pulsante?
- Il contatto è un contatto secco fra due pin: sul RJ45 sono i pin 3 (+12 V) e 5 (VIN), coerente.

## Decisione utente 2026-10-18 — lettura con TLP293, LED del remote alimentati dalla 3V3 (SUPERATA per relè (ora K2/K3) e per il drive LED via GPIO push-pull; restano valide le celle TLP293)

**Sostituisce** le vie A/B, la raccomandazione provvisoria e il pilotaggio dei LED remote via TLP293 della revisione precedente. K_LED di quella revisione = K_TAKE_B di questa (stesso numero di relè: tre IM06). Il ritorno della corrente dei LED passa dal pin 2 e chiude sul negativo batteria; il collegamento di massa è quello fisico dell'impianto, non un legame aggiunto sul cavo (da verificare con la misura della tensione pin 2–GND board).

Architettura: con la board **accesa** i relè sono sempre eccitati (presa in carico); l'inverter vede solo gli opto, e i LED del remote sono pilotati dalla board da 3V3. Con la board **spenta o in reset** tutti i relè sono diseccitati e il remote è collegato direttamente (IF-007 d).

| Funzione | Realizzazione | Riuso |
|---|---|---|
| Stato +12 V (pin 3 → pin 2) | cella 12 V EL-006 invariata: R 8,2 kΩ + BZT52C3V3 + 1N4148WS + TLP293-GB + pull-up 12 kΩ a 3V3 | identica |
| `REM_SW` (pin 5 lato remote → pin 2) | stessa cella | identica |
| LED verde/rosso inverter (pin 4, 7 lato inverter → pin 2) | TLP293-GB con **R ≈ 1,8 kΩ** al posto di R1 8,2 kΩ; **senza Zener** (la soglia a 3,3 V + V_F bloccherebbe segnali da 2,7–3,8 V); 1N4148WS antiparallelo; stesso pull-up 12 kΩ | opto, diodo e pull-up |
| LED del remote (pin 4, 7 lato remote) | GPIO 3V3 → R serie + clamp verso 3V3/GND → pin; il LED del remote ha già 1 kΩ in serie, ~1,3 mA | clamp come A3 |

Dimensionamento R LED (Proposto, **livelli dei pin LED non misurati**): con R = 1,8 kΩ, I_F opto = (V_pin − 1,25 V)/1,8 kΩ ≈ 0,8 mA a 2,7 V e 1,4 mA a 3,8 V. Il carico per l'inverter è simile a quello del LED del remote (1 kΩ + V_F ≈ 2 V), quindi i livelli dei pin non cambiano molto. Sopra 0,5 mA il CTR è garantito (GB), margine ridotto solo se il pin scende sotto ~2,2 V.

Relè: la presa in carico commuta **tre linee** (VIN, pin 4, pin 7) ⇒ **K_TAKE_A** (VIN + pin 4) e **K_TAKE_B** (pin 7, secondo polo libero), bobine pilotate insieme da un solo BSS138, più **K_LVL** (livello +12 V su VIN): in tutto **tre IM06**, due GPIO di comando. ~~Il pin 2 (GND) resta passante e non è collegato alla massa board.~~ **Superato il 2026-10-18 dalla "Decisione utente 2026-10-18 (sera) — pin 2 RJ2 a GND board" in fondo.**
GPIO totali: 4 ingressi (+12 V, `REM_SW`, LED G, LED R) + 4 uscite (2 relè, 2 LED remote) = 8, da assegnare (non strapping).

Sequenza: all'avvio K_LVL = `REM_SW` letto, poi K_TAKE; HA può forzare ON/OFF e il remote resta specchiato. Se il firmware si blocca con i relè eccitati, i LED del remote restano congelati: serve watchdog.

Rischi: (1) glitch su VIN al trasferimento; (2) i LED del remote dipendono dal firmware con la board accesa; (3) tensione del pin 3 non misurata (se < 8 V la cella 12 V non basta); (4) pulsante/levetta ancora da chiarire.

## Rettifica 2026-10-18 (sera) — segnali GREEN/RED bidirezionali, come nello schematico dell'utente (Proposto)

Lo schematico reale (screenshot utente) rende **superata** la sezione precedente ("GPIO push-pull + R serie + clamp") e il drive via GPIO dedicato. Designatori: U14 `SIG_INVERTER_12V`, U17 `SIG_INVERTER_REQ`, U15 `SIG_INVERTER_GREEN`, U16 `SIG_INVERTER_RED` (TLP293-GB, uscita con pull-up 12 kΩ a 3V3: R52, R62, R55, R56). **Q9 e Q10 = BSS84K (P-MOSFET)**, source a 3V3, **gate = nodo GREEN / RED** (cioè il collettore dell'opto), drain → R57 / R58 **220 Ω** → pin LED del remote.

- **Funzione:** specchio hardware senza firmware. LED dell'inverter acceso ⇒ opto conduce ⇒ nodo basso ⇒ Q9 conduce ⇒ 3V3 attraverso 220 Ω al LED del remote. Il 12 kΩ è proprio il pull-up di gate: il riuso è corretto (risposta precedente sbagliata: avevo letto il 12 kΩ come pull-up del LED).
- **Bidirezionale:** il GPIO sul nodo in **open-drain** (in uscita e in ingresso insieme, `GPIO_MODE_INPUT_OUTPUT_OD` in ESP-IDF; non riletto su TRM) lo tira basso ⇒ Q9 conduce ⇒ LED acceso. Rilascio ⇒ il 12 kΩ lo riporta alto ⇒ LED spento. Wired-OR: LED acceso se acceso dall'inverter **o** forzato dall'ESP. Nessun GPIO di pilotaggio in più: 4 ingressi/ingressi-uscite (12 V, REQ, GREEN, RED) + relè.
- **Corrente LED:** (3,3 − V_F ≈ 2)/(220 Ω + 1 kΩ + R_DS(on)) ≈ **1,05 mA** (ipotesi: LED + 1 kΩ del remote RJ11, V_F 2 V), pari a quanto assorbiva con l'inverter. BSS84K (HJC, C54795811): datasheet letto e corrente LED simulata 0,72–0,98 mA (peggiore 0,54 mA), vedi `elettrica/components.md` e la revisione dello schema più sotto.
- **Stato sicuro:** GPIO in reset in alta Z ⇒ nodo alto ⇒ Q9/Q10 spenti; relè diseccitati ⇒ il drain non è collegato al remote.
- **Lampeggio verde:** l'ESP tira basso a 1 Hz quando ha il controllo e l'inverter non è acceso. Durante la fase di rilascio il nodo riflette lo stato dell'inverter (campionare a fine fase; τ ≈ 12 kΩ × poche decine di pF, trascurabile); durante la fase bassa lo stato dell'inverter non è leggibile.
- **Rischi aperti:** (1) corto del pin 4/7 al pin 3 (+12 V adiacente): il corpo-diodo di Q9 porta (12 − 3,3 − 0,7)/220 Ω ≈ 36 mA nel rail 3V3 (55 mA a 16 V, 0,66 W in R57 da 0805): oltre il rating e il rail 3V3 non sink-a; già censito (Schottky serie al drain, vedi revisione schema più sotto); (2) se il LED dell'inverter lampeggia per un guasto, la fase di forzatura ESP maschera il lampeggio solo se in corso; (3) specchio con tolleranza di V_F del LED non misurata.

## Open-drain per i LED del remote? Verifica 2026-10-18 (SUPERATA: vale lo specchio Q9/Q10 con nodo GREEN/RED bidirezionale; la conclusione «push-pull + BAT54S» non è nel foglio)

Idea utente: pin ESP32-S3 in open-drain per pilotare il LED del remote, con lampeggio del verde quando la board ha il controllo e non comanda l'inverter acceso.
Il modo open-drain esiste (ESP-IDF `GPIO_MODE_OUTPUT_OD`); non l'ho riletto sul datasheet/TRM in questa sessione, quindi nessun numero di I_OL/V_OL è usato qui.

- **Funziona solo con pull-up esterno a 3V3** (non a 12 V: il pin non è 5 V-tollerante), logica invertita: GPIO basso = LED spento, alta Z = acceso.
- Con R_pu verso 3V3 e il LED del remote (1 kΩ + V_F ≈ 2 V, ipotesi): acceso I = (3,3 − 2)/(R_pu + 1 kΩ); **spento** il pin tira a massa 3,3 V/R_pu sprecati. R_pu = 1 kΩ: 0,65 mA acceso, 3,3 mA spento; R_pu = 470 Ω: 0,9 mA acceso, 7 mA spento. Il push-pull dà 0,65 mA acceso con R serie 1 kΩ e **0 mA spento**.
- **Nessun vantaggio di protezione**: il rischio reale è un corto del pin 4 (verde) al pin 3 (+12 V, adiacente) su connettore o cavo. Serve R serie + clamp in entrambi i casi; con 0805 e 16 V la R serie dovrebbe essere ≥ ~1,5 kΩ per restare entro 125 mW ((16 − 3,6)²/R), il che abbassa la luminosità (a 1,5 kΩ + 1 kΩ: 0,5 mA).
- A reset/boot il pin è comunque scollegato dal remote (relè diseccitati): l'open-drain non aggiunge sicurezza di stato.

Esito: **fattibile, non conveniente**. Proposta: **GPIO push-pull**, R serie ~1 kΩ + clamp BAT54S, GPIO alto = LED acceso. Il LED del remote sarà più scuro di quello pilotato dall'inverter (≈ 0,65 mA contro ~1 mA, ipotesi): da valutare sul pezzo, R serie tarabile.

**Lampeggio (firmware):** presa in carico attiva + inverter non comandato acceso ⇒ verde a 1 Hz; inverter acceso ⇒ verde fisso (specchio); rosso sempre specchiato dall'inverter. Lo specchio va campionato ≥ 20 Hz perché eventuali pattern di lampeggio dei guasti dell'inverter restano riconoscibili. Il lampeggio non è un indicatore di salute del firmware: se si blocca, il LED resta fisso.

## Prossimo passo

Richiesta prima della scelta dei relè (REQ-IF-007 + risultati di queste misure): `datasheet-verifier` sul solo candidato proposto, non a tappeto.

## Specchio LED in hardware (discussione 2026-10-18; SUPERATA sul part number: Q9/Q10 = BSS84K HJC C54795811, vedi ultima revisione)

P-MOSFET high-side per LED: ~~BSS84-7-F (C85202)~~, source a 3V3, gate direttamente su `SIG_INVERTER_GREEN/RED`, drain → R serie + clamp → pin 4/7 lato remote (relè K_TAKE eccitato). Il firmware legge gli stessi nodi per HA. Esito della verifica e rischi (margine di pilotaggio, body diode su cavo esposto, pinout) in `elettrica/components.md`. Da fare: simulare/misurare a −20 °C; leggere il PDF Diodes; decidere R serie e clamp.

## Revisione schema 2026-10-18 (foglio EasyEDA, Q9/Q10 = BSS84K)

- **Decisione utente:** nessun 1N4148WS antiparallelo sui LED degli opto (U14–U16).
- **Errore trovato (stato sul foglio attuale non riverificato da questa sessione): Q9 e Q10 sono montati invertiti.** Nel simbolo il terminale in basso è il **source** (qui il gate-protection e la freccia del body sono collegati lì) e quello in alto il **drain**; nello schema il +3V3 è sul terminale alto e R57/R58 su quello basso. Con il drain a 3V3 il body diode (anodo drain, catodo source) alimenta comunque il LED dal rail tramite ~0,7 V: i LED del remote restano accesi qualunque sia il gate. **Correzione:** source (basso) a +3V3, drain (alto) verso R57/R58. Verificare anche il pinout del footprint SOT-23 del BSS84K (convenzione 1 = G, 2 = S, 3 = D, non letta sul datasheet Nexperia).
- Il riquadro con la croce al gate è la protezione ESD gate-source integrata del BSS84K, non un pin non collegato (ritirata la mia osservazione precedente).
- Resta da fare: relè K_TAKE sui pin 4/7/VIN (non disegnati), diodo Schottky serie al drain per il body diode verso il 3V3, verifica del BSS84K sul datasheet Nexperia.

- **Q9/Q10 = LCSC C54795811** (HJC BSS84K, scelta utente 2026-10-18): datasheet letto, V_th max −2,2 V, pinout 1 = G, 2 = S, 3 = D, ESD 2 kV HBM. Corrente simulata nel LED 0,72–0,98 mA (caso peggiore 0,54 mA). Dettagli in `elettrica/components.md`.


## Designatori sul foglio EasyEDA (letti dallo screenshot, 2026-10-18; connettività dedotta, MCP non connesso)

| Funzione | Designatore | Valore / part number |
|---|---|---|
| Relè presa in carico del solo VIN (NC = remote, eccitato = board) | K2 | Omron G6K-2F-Y-TR DC12 |
| Relè stato inverter da board, solo +12 V su VIN (NC = spento, eccitato = acceso) | K3 | Omron G6K-2F-Y-TR DC12 |
| MOSFET pilota bobina K2 / K3 | Q4 / Q8 | BSS138 (costruttore non indicato sul foglio) |
| R serie gate (GPIO → gate) | R50 / R60 | 1 kΩ |
| Pull-down di gate | R49 / R59 | 47 kΩ |
| TVS sulla bobina | D19 (K2) / D22 (K3) | SMAJ33A (non 1N4148WS: in verifica, sessione inv-coil-tvs) |
| Net di comando | `CMD_INVERTER_CTRL` (Q4) / `CMD_INVERTER_STATE` (Q8) | GPIO da assegnare |
| Cella +12 V inverter (pin 3) → `SIG_INVERTER_12V` | R51 8,2 kΩ, D21 BZT52C3V3, U14, pull-up R52 12 kΩ | TLP293-GB |
| Cella richiesta/remote (pin 5) → `SIG_INVERTER_REQ` | R61 8,2 kΩ, D23 BZT52C3V3, U17, pull-up R62 12 kΩ | TLP293-GB |
| Cella LED verde → `SIG_INVERTER_GREEN` | R53 1,8 kΩ, U15, pull-up R55 12 kΩ | TLP293-GB, senza Zener né antiparallelo |
| Cella LED rosso → `SIG_INVERTER_RED` | R54 1,8 kΩ, U16, pull-up R56 12 kΩ | TLP293-GB, senza Zener né antiparallelo |
| Specchio LED (gate = GREEN / RED) | Q9 / Q10, drain → R57 / R58 220 Ω → pin 4 / 7 RJ2 | BSS84K HJC C54795811 |
| Connettori | RJ1 (inverter), RJ2 (remote) | R-RJ45R08P-A004 |

D20 non è visibile nello screenshot (range D19–D23): da cercare sul foglio.

**Pilotaggio bobine (Proposto; BSS138 onsemi Rev. 7, apr. 2024, letto sul PDF):** V_GS(th) 0,8 / 1,3 / 1,5 V a 1 mA (−2 mV/°C); I_GSS ±100 nA ⇒ 4,7 mV su 47 kΩ; R_DS(on) ≤ 6 Ω a 4,5 V (nessun valore a 3,3 V, irrilevante con bobina G6K 1315 Ω, 9,1 mA a 12 V); τ di gate ≈ 30 ns contro 3 ms del relè. Con 3V3 assente il gate è a 0 V per sola rete passiva (SW-002). **Rischio:** un pin ESP32-S3 con pull-up interno di default in reset (≈ 45 kΩ, GPIO0 certo; 3/45/46 da verificare sul datasheet, **non riletto**) porta il gate a ≈ 1,7 V, sopra il V_th max: assegnare a `CMD_INVERTER_*` pin senza pull di default, oppure R49/R59 ≈ 10 kΩ. Non salire a 100 kΩ.

**Altre differenze dal testo storico:** nessun 1N4148WS su U14–U17 (decisione utente per U14–U16; U17 da confermare: il LED del TLP293 regge pochi V inversi, valore da verificare); a riposo U14/U17 non hanno Zener inverso.

## Decisione utente 2026-10-18 (sera) — pin 2 RJ2 a GND board (opzione B, Proposto, da confermare alla revisione del foglio)

Verifica dello screenshot (solo immagine, MCP non connesso): **RJ2 pin 2 è già a GND board**; RJ1 pin 2 (GND inverter) va solo ai catodi di U14–U17; fra RJ1 pin 2 e RJ2 pin 2 non c'è filo. Pin 8 RJ1→RJ2 passante, NC, nessun GND. L'utente sceglie di **mantenere così** e di aggiornare la documentazione. Sostituisce "pin 2 passante, non collegato a GND board" (sezioni precedenti).

Conseguenze da tenere presenti:
- **Ritorno dei LED del remote = GND board** (3V3 → Q9/Q10 → 220 Ω → LED+1 kΩ → RJ2 pin 2 → GND board): coerente con il pilotaggio da 3V3, nessuna corrente LED sul cavo verso l'inverter.
- **Dominio inverter isolato:** GND inverter (RJ1 pin 2) solo su catodi opto; nessun legame di massa via cavo, quindi nessun secondo percorso di massa (a5) e REQ-IF-005 (stella a punto singolo) non toccato.
- **Pin 2 non è più passante.** Con la board spenta e i relè a riposo il remote **non** vede il GND dell'inverter: i LED del remote, che con l'inverter collegato direttamente sono pilotati dai pin 4/7 verso il ritorno su pin 2, non funzionano finché la board non è alimentata, o il remote perde il ritorno. **IF-007 (d) (passante a riposo) non è soddisfatto per il ritorno dei LED**; il comando VIN (pin 3–5) resta passante e funziona. Da accettare consapevolmente o da risolvere con un polo di relè su pin 2 (commutazione GND inverter ↔ GND board): **Open**, da decidere.
- Da verificare al banco: che il remote non usi il pin 2 per altro (cicalino, contatto) e la tensione fra GND inverter e GND board con inverter in carico (solo diagnostica, nessun legame fisico).
- Foglio EasyEDA: nessuna modifica necessaria per B; solo i numeri pin di RJ2 pin 2 da confermare con zoom/net highlight.
