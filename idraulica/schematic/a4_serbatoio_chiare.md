# Schematico A4 — Interfaccia serbatoio acque chiare (livello 0–190 Ω + DS18B20)

Requisiti: REQ-IF-003 (livello, Confirmed), REQ-IF-004 (temperatura, Confirmed; tipo DS18B20 indicato dall'utente il 2026-10-15). Punti aperti: OPEN-05 (scopo), OPEN-15 (misure sul serbatoio reale). Designatori: **non ancora assegnati**, si prendono nell'editor (nomi provvisori `_LVL`, `_TMP`). Pin GPIO: non assegnati (vedi "Risorse MCU").

Due canali indipendenti, due connettori **non scambiabili** (2 poli e 3 poli): un 3 poli non entra nel 2 poli.

## Ipotesi (tutte Assumed)

| # | Ipotesi | Se falsa |
|---|---|---|
| H1 | Sender = resistenza variabile 0–190 Ω fra due fili (segnale, ritorno) | Se ha un solo terminale e il corpo a massa: J_LVL.2 resta non collegato e il ritorno passa per il telaio (vedi rischio 5) |
| H2 | Il sender tollera fino a 9,5 mA impulsati (≈ 7 mW sul resistore, duty 0,3 %) | Alzare R_exc: cala la corrente, e con essa V_shunt (peggiora l'errore, vedi sez. A; OPEN-15) |
| H3 | Verso della caratteristica ignoto: 0 Ω = vuoto **oppure** pieno | Si risolve con la taratura a 3 punti (OPEN-15) |
| H4 | Cavi nel volume abitativo, niente load dump ISO sui fili (stessa H4 di A3) | Altrimenti l'INA219 (26 V assoluti) e gli 0805/BAT54 del 1-Wire non reggono |
| H5 | DS18B20 a **3 fili** (VDD, DQ, GND), cavo ≤ 10 m. Il modo parassita a 2 fili è escluso: la conversione richiede un pull-up forte a MOSFET che ESPHome non gestisce e che con 4,7 kΩ non regge | Cavo più lungo: rivedere pull-up (vedi app note Maxim, in verifica) |
| H6 | Scopo della temperatura = monitoraggio / avviso antigelo; nessun comando automatico (OPEN-05) | Se serve un'azione automatica, aggiungere requisito di sicurezza |
| H7 | JST XH: il pitch vero è 2,50 mm; "XH2.54" in catalogo indica cloni a 2,54 mm. Si sceglie un solo footprint e lo si usa anche per il controconnettore | Mismatch di passo: il crimpato non entra |

## A. Livello 0–190 Ω (rev. 2026-10-17, v. 4: misura ratiometrica con INA219)

**Storico di progetto.**
1. v. 1 — GPIO + diodo + Rref 330 Ω (partitore): **sostituita**, la lettura dipendeva da Vexc (±0,1 V = ±5 % FS a 190 Ω).
2. v. 2 — generatore PNP con due diodi di base: **scartata**, ±15 % di corrente fra −10 e +60 °C.
3. v. 3 — specchio PNP DMMT3906W (±2,4 % di deriva simulata): **sostituita** dalla v. 4 per scelta dell'utente.
4. v. 4 (questa, **approvata dall'utente il 2026-10-17**): l'eccitazione non deve essere stabile; si misurano **tensione sul sender e corrente** con un INA219 e si calcola `Rs = V_bus · Rsh / V_shunt`. Stato: **Proposto**; l'errore è calcolato dai limiti del datasheet TI SBOS448G Rev. G (letto direttamente), non misurato.

### Principio
`LVL_EN` (GPIO) alimenta, attraverso il diodo D_drv e R_exc, la serie Rsh + sender. L'INA219 misura la caduta su Rsh (corrente) tra IN+ e IN−, e la tensione di IN− verso massa (bus), cioè la tensione sul sender. Il rapporto fra le due misure non dipende da Vexc né dalla tensione di rail.

```
            R_exc         Rsh
LVL_EN ─ D_drv ─/\/\──┬──/\/\──┬────── J_LVL.1 ── sender 0–190 Ω ── J_LVL.2 ── GND
(GPIO)  1N4148WS 300 Ω│  3,9 Ω │
   │                  │        │         INA219 (SOIC-8)
  Rpd 100 kΩ         IN+      IN−   ◄──  VS ─ 3V3 (+ 100 nF)    GND ─ GND
   │                                     A0, A1 ─ GND (0x40)
  GND                                    SDA, SCL ─ bus I²C comune (IMU)
```

IN+ e IN− sono ai capi di Rsh. IN− è anche il punto di misura di V_bus verso GND.

### Designatori nel foglio EasyEDA (2026-10-17, da screenshot dell'utente)
Net `CLEAN_TANK_CMD` (= `LVL_EN`). Corrispondenze: D_drv = **D20** (1N4148WS, anodo verso il GPIO, polarità verificata sull'ingrandimento), R_exc = **R38** 300 Ω, Rsh = **R40** 3,9 Ω, Rpd = **R39**, INA219 = **U8** (INA219BIDCNT, SOT-23-8), connettore = **P4** (pin 1 = nodo N, pin 2 = GND). Letta a mano la rete: IN+ (pin 1) sul nodo fra R38 e R40, IN− (pin 2) sul nodo fra R40 e P4.1, GND (3) a massa, VS (4) a +3V3, SCL (5) e SDA (6) su porta, A0 (7) e A1 (8) a GND, cioè indirizzo **0x40**; piedinatura coerente con il pacchetto DCN del datasheet. **Scostamenti dal progetto:**
1. **Manca il condensatore di bypass su VS** (100 nF vicino ai pin 3 e 4; il datasheet raccomanda 0,1–1 µF).
2. **R39 vale 10 kΩ** (progetto: 100 kΩ): funziona (0,25 mA a 2,5 V quando `LVL_EN` è alto) ma carica il GPIO più del necessario. Da decidere.
3. **P4 ha ancora l'etichetta "Waste Water Tank"**: dovrebbe essere "Clean Water Tank".
4. R40: il valore sul foglio non indica la tolleranza; deve essere **0,1 %** (vedi distinta).
5. Pull-up di SDA e SCL non presenti in questo foglio: devono stare sul bus comune (IMU), da controllare altrove.

**Rilettura dal vivo con il tool EasyEDA (2026-10-17, dopo le modifiche dell'utente).** Il foglio ora ha 152 componenti (109 al primo controllo). Dalle proprietà dei componenti: **R39 = 100 kΩ** (FOJAN FRC0805F1003TS: corretto rispetto al valore 10 kΩ visto nello screenshot); **C8 = 100 nF** (YAGEO CC0805KRX7R9BB104, nuovo, posizione vicina a U8: probabile bypass di VS, **collegamento non confermabile dal tool**); **P4** con commento "Clean Water Tank"; R38 = FOJAN FRC0805F3000TS 300 Ω 1 %. **Corretto il 2026-10-17: R40 ora è Yageo RT0805BRD073R9L (±0,1 %, ±25 ppm/°C, C136923), riletto dal foglio EasyEDA. Prima era** FOJAN FRC0805F3R90TS, 3,9 Ω ±1 %, ±200 ppm/°C (LCSC C2933436)**, non 0,1 % come da distinta: ±200 ppm/°C su ±35 K sono ±0,7 % di deriva di Rsh, che entra 1:1 nell'errore su Rs (la tolleranza statica ±1 % è assorbita dalla taratura). **P4 è un morsetto a vite da 5,08 mm** (JILN JL500-50802G01, LCSC C709041), non un JST XH: da confermare se voluto. **Limite del tool:** lo snapshot vede solo 49 pin e 17 fili su 152 componenti e segnala *tutti* i pin come non collegati (anche R38/R39): la connettività **non è verificabile via MCP** su questo foglio; resta valida la lettura a mano dallo screenshot (U8: IN+, IN−, A0/A1, VS).

**Connettore corretto (rilettura del 2026-10-17).** Il morsetto P4 non c'è più: ora è **CN3 = JST B2B-XH-A(LF)(SN)**, 2 poli, passo **2,50 mm** (LCSC C158012), nome "Clean Water Tank". Nota: il JST XH vero è a 2,50 mm; se il controconnettore sul cavo è un clone "XH2.54" l'accoppiamento funziona in pratica ma il passo non coincide (H7). **Il connettore a 3 poli per il DS18B20 e il suo circuito non risultano ancora disegnati** (la ricerca "XH" trova solo CN3).

### Dimensionamento (R_exc = 300 Ω, Rsh = 3,9 Ω)
Eccitazione efficace Vexc = 3,3 V − caduta del GPIO − V_F di D_drv: **2,2…2,9 V, nominale 2,5 V** (ipotesi, non misurata). Vincolo principale: V_shunt ≤ 40 mV (PGA /1, fondo scala ±40 mV, **datasheet Tab. 7.5**), con Rs = 0 e Vexc massima.

| Vexc | R_sender | I | V_shunt | V_bus (sender) | P sender |
|---|---|---|---|---|---|
| 2,9 V (max) | 0 Ω | 9,5 mA | **37,2 mV** (< 40 mV) | 0 V | 0 |
| 2,5 V | 0 Ω | 8,2 mA | 32,1 mV | 0 V | 0 |
| 2,5 V | 95 Ω | 6,3 mA | 24,4 mV | 0,60 V | 3,7 mW |
| 2,5 V | 190 Ω | 5,1 mA | 19,7 mV | 0,96 V | 4,9 mW |
| 2,2 V (min) | 190 Ω | 4,5 mA | 17,4 mV | 0,85 V | 3,8 mW |
| 2,9 V (max) | 190 Ω | 5,9 mA | 22,9 mV | 1,12 V | 6,6 mW |
| qualsiasi | aperto | 0 | 0 | = Vexc (2,2…2,9 V) | — |

- **Sender aperto** = V_shunt ≈ 0 e V_bus ≈ Vexc: distinguibile da qualsiasi Rs valida (I ≥ 4,5 mA). Corto verso GND = 0 Ω (non distinguibile da una sonda a 0 Ω, come prima).
- Dissipazione: R_exc 27 mW (0805 ✓), Rsh 0,36 mW, sender ≤ 6,6 mW.
- **Risoluzione:** V_bus ha LSB 4 mV (≈ 0,6 Ω a 6 mA, 0,3 % FS); V_shunt ha LSB 10 µV (0,06 % del segnale a 17 mV).
- Rsh: 3,9 Ω 0,1 %, 0805. R_exc: 300 Ω 1 %, 0805 (la sua tolleranza non conta: il rapporto non dipende da Vexc).

### Impostazioni INA219 (da verificare in firmware)
- Indirizzo **0x40** (A0 = A1 = GND; Tab. 1 del datasheet: 16 indirizzi 0x40…0x4F). **Verifica del 2026-10-17 con IMU MPU-6050 e magnetometro HMC5883L (indicati dall'utente): nessun conflitto.** Indirizzi sul bus: INA219 0x40, HMC5883L 0x1E (datasheet Honeywell, copia di terzi), MPU-6050 0x68 con AD0 a livello basso o 0x69 con AD0 alto (InvenSense PS-MPU-6000A-00 Rev. 3.2, copia di terzi, letto direttamente). Tutti distinti. Riserve se servisse spostarlo: 0x41 (A0 = VS+), 0x44 (A1 = VS+), 0x45 (A0 = A1 = VS+). PGA /1 (±40 mV), BRNG = 0 (16 V di fondo scala di V_bus).
- Modo "shunt e bus, triggered", 12 bit con 8 campioni: **4,26 ms per canale** (Tab. 5 del datasheet), cioè ≈ 8,6 ms in tutto; impulso di eccitazione ≈ 15 ms ogni 5 s. Fra le misure `Power-down` (6 µA tip., 15 µA max; ritorno in 40 µs).
- **Pad `LVL_EN`:** ESPHome (solo framework esp-idf) espone `drive_strength` sui GPIO ESP32 con valori 5 / 10 / 20 / 40 mA, **default 20 mA** (documentazione ESPHome, pagina Pin Schema, letta via WebFetch). ESP-IDF non dà mA per i livelli (weak, stronger, medium = default, strongest) e avverte di non fidarsi del valore di reset. Il datasheet ESP32-S3 v2.2 specifica solo I_OH = 40 mA a V_OH ≥ 2,64 V con il pad più forte. La corrente richiesta è ≤ 9,5 mA: il default basta se la corrispondenza 20 mA = medium è corretta; se V_shunt a 190 Ω scendesse troppo, impostare `drive_strength: 40mA`. Da confermare al banco (leggere V_shunt a Rs = 0 e 190 Ω).
- Calcolo: `I_sender = V_shunt/Rsh − I_bias(IN−) − V_bus/320 kΩ`, con `I_bias(IN−) ≈ 20 µA` tipico (valore massimo non riportato nella tabella letta); `Rs = V_bus / I_sender`. Poi mappa Rs → % con la taratura a 3 punti.

### Errore atteso (dai limiti del datasheet, `idraulica/sim/a4_livello/ina219_error.py`)
Su Rs, in % del fondo scala (190 Ω), senza taratura:

| Grado | 25 °C, p95 / peggiore | −25…85 °C, p95 / peggiore |
|---|---|---|
| A | 1,4 % / 2,2 % | 1,9 % / 3,2 % |
| **B (consigliato)** | **1,1 % / 1,7 %** | **1,5 % / 2,4 %** |

Con taratura a 3 punti resta la sola deriva termica. **Non incluso:** l'offset dell'ADC del bus (Fig. 5 del datasheet, valore non leggibile dal testo estratto): si cancella con il punto "0 Ω" della taratura, rimane solo la sua deriva.

### Guasti
- **24 V su J_LVL.1:** IN+ e IN− vanno a 24 V, entro il massimo assoluto di 26 V (−0,3…26 V, Tab. 7.1) con **2 V di margine**; D_drv (V_R 75 V) blocca il ritorno verso il GPIO. Il datasheet dice che la tensione di bus può essere presente a INA219 spento. **Non c'è più la rete Rp + clamp** della convenzione elettrica: è uno **scostamento da `caravantic-conventions`, accettato dall'utente il 2026-10-17 (Confirmed)**. La tenuta a 24 V poggia solo sul rating dell'INA219; rischio residuo: tensioni > 26 V o negative sul filo del sender.
- **N a massa:** 9,5 mA massimi, V_shunt 37 mV, nessun clipping.
- **Reset/MCU spento:** `LVL_EN` in alta impedenza (i GPIO generici non hanno pull al reset) e Rpd a massa: nessuna corrente nel sender. **Valido per l'S3 e per i pin senza pull del C6-Zero (GP0…5, 7, 14, 15). Sul C6-Zero `LVL_EN` è su GP21, che ha un weak pull-up ≈ 45 kΩ al reset:** con Rpd 100 kΩ il nodo sale a ≈ 2,28 V e il sender riceve ≈ 3,5…5,5 mA per tutto il boot (entro H2, ≤ 9,5 mA; OPEN-15 non chiuso). Con Rpd ≤ 4,7 kΩ ≈ 0,3 V, nessuna corrente. Dettagli: [`a8_verifica_stato_reset.md`](../../hardware/schematic/a8_verifica_stato_reset.md). INA219 acceso o spento non cambia nulla.
- **Bus I²C bloccato:** la lettura del livello manca ma nulla di pericoloso; firmware con timeout.

## B. Temperatura DS18B20 (1-Wire, 3 fili)

```
3V3 ──┬── J_TMP.1 (VDD)           3V3
      └─ C 100 nF ─ GND           │
                                 Rpu 4,7 kΩ
J_TMP.2 (DQ) ──────────┬──────────┘
                       └─ Rf 1 kΩ (2512) ─┬─ OW ── GPIO (I/O, open-drain)
                                          └─ D_clamp BAT54S (3V3 / GND)
J_TMP.3 (GND) ── GND
```

- **Pull-up lato cavo, resistore serie lato MCU.** Quando il master porta la linea a zero, la linea vista dallo slave vale `3,3 · Rf / (Rf + Rpu)` = **0,58 V** con 1 kΩ / 4,7 kΩ: sotto il V_IL del DS18B20 (**0,8 V da memoria, in verifica**), con margine di 0,2 V. Rf non può salire (a 2,2 kΩ la linea va a 1,05 V: fuori soglia) né scendere senza costare potenza in guasto.
- **Fault a 24 V su DQ:** 20 mA nel clamp, **0,42 W su Rf** → Rf in **2512** (≥ 0,5 W). Con 1206 si resterebbe entro 16 V (≈ 0,15 W). Il pull-up dissipa 91 mW (0805 ✓).
- **VDD dal 3V3 in modo diretto.** Un diodo serie (BAT54, ≈ 0,3 V) porterebbe VDD sotto il minimo del DS18B20 (3,0 V, **da memoria, in verifica**); una resistenza serie non regge i 24 V. **Decisione utente 2026-10-15 (Confirmed): VDD diretto dal 3V3, rischio accettato.** Si accetta che un guasto > 3,6 V sul filo VDD retroalimenti il 3V3 (cavo a 3 fili dedicato, nessun 12 V nello stesso cavo); l'alternativa (interruttore di potenza/LDO dedicato) è scartata. Il DS18B20 ha −0,5…+6 V assoluti su VDD: un guasto a 12 V lo distrugge.
- Il bypass 100 nF va sul connettore, lato scheda.
- Corrente del sensore ≈ 1,5 mA max (**in verifica**), trascurabile sul 3V3.

## Connettori
| Rif. | Poli | Piedinatura |
|---|---|---|
| J_LVL | JST XH 2 poli | 1 = segnale sender, 2 = ritorno (GND) |
| J_TMP | JST XH 3 poli | 1 = VDD (3V3), 2 = DQ, 3 = GND |

Footprint, orientamento (verticale/90°) e codici LCSC: da decidere nell'editor (H7).

## Risorse MCU (da assegnare)
| Segnale | Tipo | Vincoli |
|---|---|---|
| LVL_EN | uscita digitale, **attiva alta** (eccitazione) | non su pin di strappo (GPIO0, 3, 45, 46); non GPIO14 |
| SDA / SCL | I²C comune (IMU, INA219) | **nessun ADC1 occupato** dal livello |
| OW | I/O digitale (1-Wire) | non su pin di strappo; non GPIO14 |

## Distinta (tutto **Proposto**)
| Funzione | Valore | Package | Stato verifica |
|---|---|---|---|
| U_LVL | TI **INA219BIDR** (grado B; riserva INA219AIDR) | SOIC-8 | datasheet SBOS448G Rev. G letto direttamente; LCSC C2155799 (B, ~100 pz, fonte debole) / C138706 (A); ciclo di vita contraddittorio fra fonti, da confermare sul sito TI |
| D_drv | 1N4148WS | SOD-323 | già nel registro (verificato 2026-10-05, V_R 75 V) |
| R_exc | 300 Ω 1 % | 0805 | calcolo (27 mW) |
| Rsh (R40) | **Yageo RT0805BRD073R9L**, 3,9 Ω ±0,1 %, ±25 ppm/°C, film sottile (LCSC **C136923**) | 0805 | scelto dall'utente il 2026-10-17; dati dalla pagina LCSC e dal foglio EasyEDA (non dal datasheet): 11.490 pz, 0,054 USD da 10 pz; calcolo 0,36 mW |
| Rpd | 100 kΩ | 0805 | stato sicuro su LVL_EN |
| C VS | 100 nF | 0603/0805 | consigliato dal datasheet |
| Rpu 1-Wire | 4,7 kΩ | 0805 | datasheet DS18B20 in verifica |
| Rf 1-Wire | 1 kΩ | **2512** | calcolo (0,42 W a 24 V) |
| D_clamp 1-Wire | BAT54S | SOT-23 | datasheet: V_R 30 V (limitato da Rf) |
| C bypass DS18B20 | 100 nF | 0603/0805 | — |
| U sensore | Maxim/ADI DS18B20 (esterno, a cavo) | — | in verifica |
| J_LVL / J_TMP | JST XH 2 e 3 poli | — | da decidere |

Eliminati rispetto alla v. 3: DMMT3906W, Re1, Re2, Rref, Rb, Rp (livello), clamp BAT54S e C del nodo ADC.

## Limiti noti (rischi)
1. **Accuratezza del livello**: 1,5 % FS (p95) e 2,4 % nel caso peggiore con grado B su −25…85 °C, dai limiti del datasheet e senza taratura; offset del bus non valutato.
2. **Nessuna rete di clamp** sul nodo di campo: scostamento dalla convenzione, tenuta a 24 V solo per il rating dell'INA219 (26 V, margine 2 V; −0,3 V minimi). **Accettato dall'utente il 2026-10-17.**
3. **Verso e curva del sender** non noti; la curva Rs → volume dipende dalla forma del serbatoio (taratura a punti).
4. **VDD del DS18B20 non protetto** da 24 V: rischio accettato dall'utente il 2026-10-15.
5. **Ritorno del sender**: se il corpo del sender va a massa telaio e non sul filo 2, la differenza di potenziale fra telaio e massa scheda entra nella misura (pochi mV; verificare il collegamento).
6. **Cavo 1-Wire**: oltre i 10 m il pull-up da 4,7 kΩ può non bastare (app note Maxim in verifica).
7. **Clamp 1-Wire** scaricano sul 3V3: in guasto prolungato si presuppone un carico del rail > 25 mA.
8. **INA219:** un dispositivo I²C in più sul bus dell'IMU (0x40 senza conflitti con MPU-6050 e HMC5883L; capacità del bus da verificare), consumo a riposo 0,7 mA tip. / 1 mA max se non si usa il power-down (OPEN-08), ciclo di vita e stock da confermare.

## Esito della verifica datasheet (datasheet-verifier, 2026-10-15)

**Limite:** i PDF ufficiali non erano leggibili; i dati DS18B20 vengono da una copia di terzi della Rev 4 (fonte debole-media), i VF del BAT54 da una copia MCC. Nessun dato ha una seconda fonte solida: **aprire a mano i PDF ufficiali prima di congelare**.

| Dato | Esito |
|---|---|
| DS18B20 VDD | 3,0–5,5 V: 3,3 V dentro, margine 0,3 V sul minimo (debole) |
| DS18B20 accuratezza | ±0,5 °C da −10 a +85 °C (debole); −10 °C è il limite del range ambiente |
| DS18B20 DQ | V_IL ≤ 0,8 V ✓ (la mia linea a 0,58 V ha margine 0,22 V); V_IH ≥ 2,2 V; sink 4 mA a 0,4 V |
| DS18B20 IDD | 1,5 mA max, ma specificata a 5 V, non a 3,3 V |
| DS18B20 assoluti | −0,5…+6,0 V su ogni pin: **VDD non tollera 12 V** (conferma il rischio 4) |
| DS18B20 conversione | 750 ms a 12 bit: il polling firmware ne tiene conto |
| Pull-up / cavo | 4,7 kΩ nominale; AN148 non letta e non copre il caso 3,3 V: il limite a 10 m **non è dimostrato** |
| BAT54(S) V_R | 30 V, **nessun margine** a 24 V di fault (V(BR) min 30 V); I_R 2 µA a 25 V e 25 °C, **nessun dato a +60 °C** |
| BAT54(S) V_F | max 320 mV a 1 mA, 400 mV a 10 mA (25 °C); tipico e deriva termica **non trovati**: la stima −1…−2 mV/K resta ipotesi |
| BAT54(S) I_F | 200 mA continui; LCSC C47546 (Nexperia BAT54S,215) in stock, ciclo di vita non verificato |

Conseguenza (aggiornata il 2026-10-17): con il generatore, il diodo che vede i 24 V è D_f; i clamp BAT54S sono limitati da Rp e non sono critici. Per D_f serve V_R ≥ 40 V (candidato 1N4148WS, 75 V), da confermare su datasheet nel passo di verifica.

## Esito della verifica coppia PNP e GPIO (2026-10-17) — **la parte PNP è superata dalla v. 4; restano validi i dati sul GPIO**

Il verificatore non riusciva a decodificare i PDF; li ho estratti io con `pdftotext` dalle copie scaricate dal costruttore e **letto direttamente**: Diodes DS30312 **Rev. 13-2 (feb. 2018)** per il DMMT3906W, Espressif **ESP32-S3 Datasheet v2.2**, tabella 5-4 e Pin Overview 2-1. La disposizione delle tabelle estratte è in parte confusa: i valori sotto sono quelli leggibili senza ambiguità.

**DMMT3906W (Diodes, SOT-363)**
| Dato | Valore letto |
|---|---|
| Tipo | "40V matched pair PNP", coppia intrinsecamente accoppiata (dadi adiacenti dello stesso wafer) |
| V_CEO / V_CBO / V_EBO / I_C | −40 V / −40 V / −5 V / −200 mA |
| Matching dichiarato | **2 % su hFE e 2 mV su V_BE, a I_C = −2 mA, V_CE = −5 V** (rapporto 1:1) |
| hFE (V_CE = −1 V) | min 60 a 0,1 mA; **min 80 a 1 mA; min 100 a 10 mA** |
| V_CE(sat) | max 250 mV a I_C 10 mA / I_B 1 mA |
| V_BE(sat) | 0,65…0,85 V a 10 mA / 1 mA (V_BE(on) a 1 e 10 mA non riportata) |
| P_D / R_θJA | 200 mW **totale del dispositivo** / 625 °C/W |
| T di esercizio | −65…+150 °C |
| Varianti | DMMT3906W-7-F (AEC-Q101) e DMMT3906WQ-7-F (Automotive): "elettricamente e termicamente uguali" |

Conseguenze per il progetto:
1. **Il matching non copre il nostro punto di lavoro.** È dichiarato a 2 mA, 1:1; noi lavoriamo a 1,2 mA e 8 mA (rapporto ≈ 7). Lo scarto statico (fino a 2 mV su 47 Ω ≈ 0,5 % di corrente, più la parte dovuta alla densità di corrente) è assorbito dalla taratura; la deriva termica del rapporto è quella simulata (±2 %), **con un modello generico**.
2. **Autoriscaldamento:** nel caso peggiore (Rs = 0, V_CE ≈ 2 V) Q2 dissipa ≈ 17 mW, cioè ≈ 10 K sul package (625 °C/W) in regime. Con impulsi da 10 ms ogni 5 s è trascurabile; **in continuo sposterebbe la corrente di qualche punto percentuale** (firmware: mai acceso in continuo).
3. **Alternative scartate:** BC857BS e BCV62 non risultano accoppiati e non hanno dati di matching nelle fonti viste (fonti deboli, PDF Nexperia non accessibili); il BCV62A risulta esaurito su LCSC (C549618). Il BCM857BS (LCSC C105887, 1.335 pz) e il BCM62B sono varianti "matched" **non verificate** e restano una riserva.
4. **Disponibilità (fonte debole, LCSC, 2026-10-17):** DMMT3906WQ-7-F C526574, circa 525 pz. Per il DMMT3906W-7-F senza Q non risulta un codice LCSC/JLCPCB. Ciclo di vita non dichiarato come attivo dal costruttore nelle fonti viste.
5. **Modello SPICE:** la simulazione usa un 2N3906 con parametri generici, **non** il modello Diodes. Il file "SPICE model" del costruttore trovato è la Rev. 4 del 2003 (solo il datasheet, senza modello in testo). Valori assoluti da confermare al banco.

**GPIO ESP32-S3 (datasheet v2.2, tabella 5-4, 3,3 V, 25 °C)**
| Dato | Valore |
|---|---|
| V_OL max | 0,1 · VDD (≈ 0,33 V), misurata a carico ad alta impedenza |
| I_OL | 28 mA con V_OL = 0,495 V, PAD_DRIVER = 3 (il più forte); la forza di default non è in mA nel datasheet |
| I_OH | 40 mA a V_OH ≥ 2,64 V, PAD_DRIVER = 3 |
| Pull interni | R_PU 45 kΩ, R_PD 45 kΩ |
| Stato al reset (Pin Overview 2-1) | GPIO generici (es. GPIO1, 2, 4): solo ingresso abilitato o alta impedenza, **senza pull**; WPU/WPD solo su pin con funzioni speciali (strapping, VDD3P3, ecc.) |

Conseguenze: il ramo di riferimento (1,2 mA) è ben dentro i limiti; la V_OL ipotizzata di 0,2 V è prudente (con il pad più forte V_OL ≈ 17 Ω · 1,2 mA ≈ 20 mV). In reset, su un GPIO generico senza pull, lo specchio resta spento: **la regola resta di evitare i pin di strapping** (GPIO0, 3, 45, 46), che hanno pull al reset.
