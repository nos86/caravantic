# Registro componenti

Sezione A1 — ingressi digitali IN-CAB / IN-CEL. Circuito, dimensionamento e verifica SPICE: [`hardware/sim/a1_ingressi/README.md`](../hardware/sim/a1_ingressi/README.md).

Riepilogo valori (per canale, 5 componenti): R1 8,2 kΩ 0805 · D2 BZT52C3V3 · D1 1N4148WS (antiparallelo al LED) · U1 TLP293 rango GB · R2 12 kΩ. LED dell'opto in conduzione continua, **senza strobe** (assorbimento a cellula attiva ≈ 1 mA accettato dall'utente il 2026-10-08). Rev. 2026-10-08: opto da PC817C a TLP293 GB (scelta utente); rimossi generatore di corrente, strobe, BAV21W in serie, C_S e R_IN. Corrispondenza coi designatori del foglio EasyEDA: R_S = R1, ZD = D2, D2 (antiparallelo) = D1, R_PU = R2.

## U-IN1, U-IN2 (opto) — Toshiba TLP293(GB-TPL,E) (SO4, 11-3C1)
- Requisiti: REQ-EL-006, REQ-EL-008
- Stato: **Proposto** — scelta dell'utente (2026-10-08) del TLP293 rango GB al posto del PC817C. Dati numerici letti direttamente dal datasheet Toshiba; seconda fonte indipendente solo debole (listing LCSC/Digikey, coerente sul CTR minimo del GB). Non promuovere a Congelato senza conferma.
- Topologia d'uso: LED in serie a R1 (8,2 kΩ) e D2 (Zener), con D1 antiparallelo, in conduzione continua (0,50 mA a 8 V, 1,06 mA a 12,8 V, 1,25 mA a 14,4 V, caso peggiore simulato); fototransistore con pull-up R2 da 12 kΩ verso 3,3 V.
  - ⚠️ **Sotto 0,5 mA il CTR non è garantito dal datasheet.** Con questo dimensionamento il LED supera 0,5 mA da circa 8 V in su (simulato nel corner ON_worst: 0,50 mA a 8 V, 0,73 mA a 10 V). La simulazione dà "attivo" da 7,84 V, ma fra 7,84 e 8 V la lettura si appoggia alla curva tipica (Fig. 11.12, non letta), non a un valore garantito: il requisito "attivo ≥ 8 V" (Assumed) non è quindi garantito dal solo datasheet. I campi nominali Confirmed (11,5–13,8 V e 12,8–14,4 V) cadono tutti nella zona garantita.
- Parametri decisivi (fonte: [datasheet Toshiba TLP293, Rev. 7.0, 2026-08-05](https://toshiba.semicon-storage.com/info/docget.jsp?did=14419&prodName=TLP293), tab. 6, 7, 8, 8.1):
  - CTR rango GB **100–600 % sia a I_F = 0,5 mA sia a 5 mA** (V_CE = 5 V, 25 °C); non ranked 50–600 %.
  - CTR saturo (I_F = 1 mA, V_CE = 0,4 V): GB **min 30 %**, tipico 60 %. Per il non ranked il minimo non è dato.
  - V_CE(sat): ≤ 0,3 V (GB) a I_C = 0,2 mA, I_F = 1 mA; ≤ 0,2 V per il non ranked.
  - V_F 1,1 / 1,25 / 1,4 V a 10 mA; I_F max 50 mA (−1,11 mA/°C sopra 90 °C); I_FP 1 A (≤ 0,1 ms, 100 Hz); V_R max 5 V; P_D LED 100 mW.
  - V_CEO min 80 V; I_C max 50 mA; I_C(off) ≤ 10 µA (V_F = 0,7 V, V_CE = 48 V, 25 °C); I_DARK ≤ 0,08 µA (48 V, 25 °C).
  - Tempi (tipici): t_r 2 µs, t_f 3 µs a R_L = 100 Ω; le righe con R_L = 1,9 kΩ e 4,7 kΩ danno storage e t_off fino a circa 47 µs (colonne ambigue nel testo estratto: non usate per il dimensionamento).
  - T_opr −55…+125 °C; isolamento 3750 Vrms; creepage/clearance min 5,0 mm; piedinatura 1 anodo, 2 catodo, 3 emettitore, 4 collettore.
- Alternative:
  - **TLP293 non ranked** (CTR 50–600 % a 0,5 mA): simulato il 2026-10-08, vedi `hardware/sim/a1_ingressi/README.md`. **Non utilizzabile in continuo**: non esiste un R_PU che dia insieme "attivo" a 8 V e "inattivo" a 2 V (con 22 kΩ attivo da 8,1 V e inattivo fino a 1,7 V; con 12 kΩ non scende mai sotto V_IL). Con lo strobe funzionava, ma solo ricalibrando e con margini di 0,08–0,12 V. Sconsigliato.
  - HXY PC817C (C5451663): scelto in precedenza, scartato per scelta dell'utente il 2026-10-08. Richiedeva generatore di corrente e circa 8 mA di strobe.
- LCSC: **C77656** (TLP293(GB-TPL,E), nastro da 2500 pezzi), SOP-4 1,27 mm, circa 40,9 k pezzi a stock il 2026-10-08, circa 0,17 $ per 5 pezzi e 0,09 $ per 2500 (listino, fonte debole). Digikey: attivo, nessun avviso NRND/EOL trovato. Footprint EasyEDA: non verificato.
- Rischi / note:
  - **Deriva termica e invecchiamento del CTR non verificati:** le curve del datasheet (Fig. 11.12, 11.13) non sono state lette; la simulazione usa il fattore generico 0,42 (stesso del progetto precedente).
  - Il CTR saturo GB (min 30 %) pesa molto: con la derating a 0,42 resta circa 13 %, e il margine su V_IL a 8 V è di soli 0,22 V. Controllare il CTR saturo su campioni del lotto (criterio [B]).
  - Il rango GB è marcato sul corpo (marcatura "GB"): verificare sui pezzi ricevuti. L'ordine "(GB-TPL,E)" è la versione a nastro, stesso rango.
  - Componente commerciale, non qualificato AEC-Q101 (RS Online: "Automotive Standard: No", fonte debole); le approvazioni sono UL 1577, VDE, CQC. Il datasheet contiene le precauzioni generali Toshiba sulle applicazioni ad alta affidabilità.
  - Corrente LED nei transitori (simulata, caso peggiore): 11,8 mA nel load dump (400 ms), 14,7 mA nell'impulso 2a, 19 mA nel burst 3b (livello non verificato). Tutte sotto I_F max 50 mA.
  - ⚠️ Il simbolo nel foglio EasyEDA è `TLP293(TPL,E)` (non ranked): va sostituito con `TLP293(GB-TPL,E)`.

## Q-IN1, Q-IN2 (MMBTA42) — **RIMOSSI il 2026-10-08**
- Servivano come generatore di corrente / interruttore dello strobe. Eliminati con la decisione di alimentare il LED in continuo (assorbimento ≈ 1 mA accettato). Con essi sono usciti R_E, R_B, R_BE, C_S e il net `STROBE_IN`. Le verifiche del 2026-10-05 restano nello storico di git.

## R1 (resistore serie) — 8,2 kΩ 1 %, **0805**
- Requisiti: REQ-EL-006, REQ-EL-008
- Stato: **Proposto, P/N da scegliere.** Fissa la corrente del LED (circa 1 mA a 12,8 V) e assorbe l'energia dei transitori.
- ⚠️ **Rischio accettato dall'utente (2026-10-08):** l'0805 non regge in modo dimostrabile il load dump. Fonte: [Vishay D/CRCW e3](https://www.vishay.com/docs/20035/dcrcwe3.pdf) (datasheet del costruttore): CRCW0805 P70 0,125 W standard / 0,25 W esteso, U_max 150 V; sovraccarico di breve durata provato a 2,5 × P70 per 5 s, cioè circa 0,31 W. Le curve degli impulsi singoli sono nel PDF solo come grafico e non le ho lette.
- Sollecitazioni simulate (GB, caso peggiore): 50 mW continui a +24 V (ok); **load dump 101 V / 400 ms: 1,13 W di picco, 174 mJ**; impulso 1 2,7 W per 2 ms; impulso 2a 1,8 W per 50 µs; burst 3a/3b 3–5 W per 150 ns, con 205 V ai capi in 3a (livelli non verificati).
- Se si rompe: circuito aperto, il canale legge "inattivo". Alternativa se si cambia idea: 2512 da 1 W (U_max 500 V), che regge 1,13 W entro il sovraccarico 2,5×.

## D-IN1, D-IN2 (BAV21W in serie) — **RIMOSSI il 2026-10-08**
- Servivano a bloccare l'inversione di polarità e l'impulso 1 con ingresso fino a −150/−220 V. Con la topologia attuale la corrente inversa passa dal diodo antiparallelo al LED e dallo Zener in diretta: nessun diodo da 250 V. Il problema del V_RRM dipendente dal costruttore e il margine 1,22× sull'impulso 3a spariscono. Le verifiche del 2026-10-05 restano nello storico di git.

## ZD-IN1, ZD-IN2 (Zener di soglia) — BZT52C3V3 (SOD-123)
- Requisiti: REQ-EL-006 (soglia inattivo ≤ 2 V), REQ-EL-008 (conduzione in diretta con ingresso negativo)
- Stato: Proposto. ⚠️ Nel circuito attuale conduce **in diretta** con ingresso negativo (1,8 mA a −16 V; 18 mA per 2 ms nell'impulso 1; fino a circa 27 mA per 150 ns nel burst 3a): un limite di corrente diretta impulsiva non è nel registro (solo V_F 0,9 V a 10 mA, P_D 370 mW) e va verificato. Verifica `datasheet-verifier` del 2026-10-05 superata sul datasheet Diodes. La seconda fonte è debole: solo il listino LCSC del JSCJ.
- Parametri decisivi ([Diodes DS18004 Rev. 38](https://www.diodes.com/assets/Datasheets/ds18004.pdf)):
  - V_Z 3,1–3,5 V a 5 mA;
  - Z_ZT ≤ 95 Ω; Z_ZK ≤ 600 Ω a 1 mA;
  - I_R ≤ 5 µA a 1 V (solo a 25 °C);
  - coefficiente di temperatura −3,5…0 mV/K;
  - P_D 370 mW a T_A 25 °C (500 mW riferiti ai terminali a 75 °C). In uso dissipa ≤ 30 mW.
- Attenzione: la sigla non è uniforme fra costruttori. Il BZT52C3V3 MDD (C173413) ha Z_ZT 130 Ω e I_R 20 µA: da non usare senza rifare la simulazione.
- LCSC: **C151564**, Diodes BZT52C3V3-7-F, circa 17 k pezzi; è il costruttore verificato, quindi preferito. In alternativa C2112 (JSCJ, valori del listino coincidenti).
- Alternativa scartata: SMAJ33A (TVS con V_BR 36,7–40,6 V): porterebbe la soglia a circa 42 V.

## D1 (foglio EasyEDA; antiparallelo al LED e protezione inversa) — 1N4148WS (SOD-323)
- Requisiti: REQ-EL-006 (−16 V), REQ-EL-008. Protegge il LED (V_R max 5 V per il TLP293) e, con lo Zener in diretta, sostituisce il BAV21W in serie: con ingresso negativo conduce 1,8 mA a −16 V e circa 18 mA nell'impulso 1. Senza D1 la tensione inversa sul LED salirebbe a 3,05 V nel burst 3a (simulato).
- Stato: Proposto. Verifica `datasheet-verifier` del 2026-10-05 superata ([Diodes DS30097 Rev. 29](https://www.diodes.com/assets/Datasheets/ds30097.pdf), [onsemi 1N4148WS/D Rev. 4](https://www.onsemi.com/download/data-sheet/pdf/1n4148ws-d.pdf)).
- Parametri: V_RRM 75 V; I_O 150 mA; V_F ≤ 1,0 V a 50 mA; I_R ≤ 25 nA a 20 V. In uso lavora a circa 1,2 V in inversa: parametri non critici.
- LCSC: C2128, JSCJ, oltre 5 milioni di pezzi (il listino dà V_R 100 V). Il pezzo Diodes C60580 è esaurito.

---

Sezione A2 — stadio di uscita: misura di corrente di valvola (EL-003) e pistone (EL-004). Due canali separati, scelta dell'utente del 2026-10-14 (fondo scala valvola 2,5 A, pistone 12 A). Il driver (interruttori high-side valvola, ponte H pistone) è **non ancora scelto**: questa sezione copre solo la catena di misura.

Dimensionamento (calcolo mio, Proposto; il guadagno è G = 50 per entrambi i canali, quindi una sola riga di BOM per gli amplificatori):

| Canale | Shunt | Uscita a fondo scala | Dissipazione a f.s. | Errore da offset (150 µV) | Risoluzione richiesta |
|---|---|---|---|---|---|
| Valvola, f.s. 2,5 A | 18 mΩ, 1206 | 2,25 V | 0,11 W | circa 8 mA | ≤ 20 mA |
| Pistone, f.s. 12 A | 3 mΩ, 2512 | 1,80 V | 0,43 W | circa 50 mA | ≤ 100 mA |

Il pistone arriva a 16 A prima di toccare 2,4 V: lascia margine per vedere lo stallo oltre i 12 A. Con il pistone in stallo assunto a 10 A (EL-004, Assumed) l'uscita è 1,5 V.

## U-SNS1, U-SNS2 (amplificatore di shunt) — Texas Instruments INA180A2 (SOT-23-5)
- Requisiti: REQ-EL-003, REQ-EL-004 (misura di corrente, Confirmed); REQ-IF-005 per la convenzione shunt low-side Kelvin.
- Stato: **Proposto.** Verifica `datasheet-verifier` del 2026-10-14 su TI SBOS741H (luglio 2022), letta dalla versione HTML perché il PDF non era leggibile; **mono-fonte (TI)**. Vedi sotto cosa non è verificato.
- Parametri decisivi (fonte: [TI INA180, §7.3 e §7.5](https://ti.com/document-viewer/INA180/datasheet/GUID-A44FE6A5-2E5D-42DE-A145-98FDD4C4E98B)):
  - Alimentazione 2,7–5,5 V; modo comune −0,2…+26 V; gli ingressi reggono 26 V anche non alimentati (§9.3).
  - Guadagno A2 = 50 V/V; errore di guadagno typ ±0,1 %, max ±1 %; linearità garantita per uscita da 0,5 V a VS − 0,5 V.
  - Offset a V_IN+ = 0 V: typ ±25 µV, max ±150 µV (VS = 5 V); deriva max 1 µV/°C. Stima mia a +60 °C: circa 185 µV.
  - Banda A2 210 kHz (typ); I_Q max 300 µA.
  - Stato: ACTIVE (pagina TI). LCSC **C116203** (INA180A2IDBVT, SOT-23-5); footprint EasyEDA non verificato.
- Alternative: INA180A3 con shunt 2 mΩ per il pistone: scartato, offset 75 mA contro risoluzione richiesta di 100 mA, margine inferiore. INA181 (bidirezionale): non serve, la misura è unidirezionale sul ritorno di massa.
- Rischi / note:
  - ⚠️ **Valori garantiti a V_S = 5 V, non a 3,3 V** (alimentazione dal rail 3,3 V dell'ESP32-S3). Offset, guadagno e swing a 3,3 V sono **Assumed**: da verificare al banco.
  - ⚠️ **Sotto 0,5 V di uscita l'errore di guadagno non è garantito.** Valvola: 0,5 V corrispondono a circa 0,55 A; pistone: a circa 3,3 A. Sotto queste correnti vale solo l'offset: serve calibrazione dello zero in firmware.
  - Limiti dell'ADC dell'ESP32-S3 (non linearità agli estremi, rumore) non considerati qui: la risoluzione calcolata è del chip di misura, non dell'intera catena.
  - Errore complessivo a fondo scala, solo da amplificatore (1 %) e shunt (1 % se 1 %): circa 2 %. Valvola ±50 mA, pistone ±240 mA.
  - ⚠️ **Pinout A/B (suffisso B = pinout alternativo):** ordinare INA180A2IDBVT e controllare il pin-out sul PDF (§6) prima del layout.
  - Assoluti massimi (GND − 0,3 V sul modo comune) non letti dalla tabella ma da un estratto di aggregatore (fonte debole). Il ritorno di massa del camper ha picchi induttivi: serve R serie + clamp sugli ingressi (da progettare).
  - Tempo di assestamento non verificato: il filtro in uscita non deve mangiarsi i 200 ms di rilevazione battuta (da congelare).
  - Alimentare dietro il load-switch dei periferici, come in rev. 1.

## R-SH1 (shunt valvola) — 18 mΩ, 1206
- Requisiti: REQ-EL-003. Stato: **Proposto, P/N da scegliere.** Dissipa 0,11 W a 2,5 A. Collegamento Kelvin a 4 terminali o piste di sense separate; tolleranza 1 % o migliore.

## R-SH2 (shunt pistone) — 3 mΩ, 2512
- Requisiti: REQ-EL-004. Stato: **Proposto, P/N da scegliere.** Dissipa 0,43 W a 12 A, 0,30 W a 10 A: verificare potenza nominale e derating a +60 °C sul datasheet del P/N scelto (non fatto). Kelvin obbligatorio: a 12 A la caduta in massa è 36 mV.

## U-PH1 (ponte H pistone) — candidati con sense integrato, **nessuna scelta**
- Requisiti: REQ-EL-004 (ponte H, misura di corrente Confirmed), REQ-SW-002 (stato sicuro), REQ-EL-001/002 (alimentazione e catena d'ingresso). Il caso peggiore 5 A di marcia / 10 A di stallo è **Assumed** (EL-004).
- Stato: **Proposto: ST VNH7100BAS (VNH7100BASTR); riserva: TI DRV8873HPWPR(Q1)** — scelta mia del 2026-10-14 su mandato dell'utente (criteri: termica, costo, disponibilità). VNH5019A scartato dall'utente (costo).
- **Decisione utente 2026-10-14:** la misura del pistone resta sullo shunt 3 mΩ + INA180 (12 A f.s., sez. A2). Il sense integrato è **ridondanza**, non misura primaria.
- Motivazione della scelta (fonti: Tab. 4, 6, 9 del VNH, TI SLVSET1 per il DRV; prezzi e stock da aggregatori/listini, **deboli**):
  - Termica: RDS(on) a caldo più basso sul VNH (HS 120 + LS 80 mΩ max a 150 °C contro 250 mΩ tipico del DRV) e dissipazione ripartita su due die; il DRV ha il PowerPAD (R_θJA 27,8 contro 40,7/55,4 °C/W) ma dissipa di più. Il vantaggio non è dimostrato: mancano le curve termiche impulsive. **Da confermare al banco.**
  - Costo: solo su LCSC il VNH costa meno (1,92 $ contro 4,35 $), ma è esaurito; fuori LCSC il listino è simile (VNH circa 3,4 $ Mouser da aggregatore, DRV circa 3,2–3,4 $ Digi-Key).
  - Disponibilità: **incerta e contraddittoria**. VNH: Digi-Key a 0 pezzi con 26 settimane di lead time, Mouser con scorte forti da un aggregatore (da verificare sul sito). DRV: Digi-Key a 0 pezzi con 6 settimane, LCSC 78 pezzi del solo Q1. Assemblaggio manuale: si può comprare fuori LCSC, ma **verificare lo stock su mouser.com prima di congelare**.
  - Se il VNH non è acquistabile, passare al DRV8873H: stessa classe, e la misura primaria non cambia.
- Sense integrato come ridondanza (da decidere, Assumed): R_SENSE circa 390 Ω dal CS verso GND (6,5 A → circa 2,3 V), clamp e R serie verso l'ADC perché in guasto il CS arriva a 5–7 V (Tab. 10); SEL0 comandato in base al senso. **Costa un pin ADC1**, risorsa contesa: se manca, il CS resta non collegato e SEL0 non serve.
- Esito principale: **nessuno dei due sense integrati arriva a 12 A f.s. / 100 mA di risoluzione** (valori scelti da me in A2, Assumed). Il VNH7100BAS satura intorno a 6,5 A; il DRV8873H regola a circa 6,5 A fissi. Entrambi misurano solo l'high-side in conduzione. Per tenere i 12 A resta lo shunt da 3 mΩ con INA180 (sez. A2).

| Parametro | DRV8873H (TI, HTSSOP-24 PowerPAD) | VNH7100BAS (ST, SO-16N) |
|---|---|---|
| Fonte | TI SLVSET1 / SLVSDY7B via verificatore (conversione testuale, mono-fonte, celle (*) da ricontrollare) | **PDF ST DocID029596 Rev 2, mar. 2017, letto direttamente (fornito dall'utente)**; mono-fonte, non ancora passato dal verificatore |
| Alimentazione | 4,5–38 V operativa, 40 V assoluta max | 4–28 V operativa, 38 V assoluta max, 40 V transitorio (ISO 16750-2 test B) **solo con soppressore esterno a 40 V** (Tab. 4, 6, nota 3 di Tab. 14) |
| RDS(on) | HS+LS 150 mΩ a 25 °C, 250 mΩ a 150 °C (tipici) | HS 60 mΩ, LS 40 mΩ tipici a 25 °C; **max a 150 °C: HS 120 mΩ, LS 80 mΩ** (Tab. 6) |
| Limite di corrente | Variante H: fisso 6,5 A (5,5–7,5 A), regolazione disattivabile; OCP latch min 10 A | HS ILIM 12/18/24 A (min/typ/max); LS shutdown 14/22/30 A (Tab. 9): **a 10 A di stallo non limita** |
| Sense: rapporto | k = 1100 A/A tip. | K = 1120 tip.; a 2,5 A min–max 1015–1229, a 4 A 1040–1200 (Tab. 10); **a 4–12 A non specificato** |
| Sense: accuratezza | ±50 mA sotto 1 A, ±5 % da 1 A (min/max) | K a 4 A ±7 % da pezzo a pezzo; deriva termica ±4 % a 4 A, ±5 % a 2,5 A, **±21 % a 0,2 A, ±25 % a 0,05 A** |
| Sense: fondo scala | circa 6,5 A (limite di regolazione), pin IPROPI max 5,5 V | **Saturazione: I_SENSE ≥ 5,8 mA min, I_OUT_SAT ≥ 7 A (Tab. 10) → circa 6,5 A**; R_SENSE ≤ 420 Ω per stare sotto 2,45 V |
| Sense nei due sensi | Sì, ma solo HS (nessun ricircolo low-side) | Sì, **SEL0 deve seguire il senso**: INA=1 → SEL0=1; INB=1 → SEL0=0, altrimenti Hi-Z (Tab. 11) |
| Pin di sense in guasto | n/d | **CS sale a 5–7 V** (R_SENSE 1 kΩ) con 10–30 mA (Tab. 10 VSENSEH, ISENSEH): protezione dell'ADC obbligatoria |
| Termico | R_θJA 27,8 °C/W (PowerPAD) | R_θJA 40,7 (HS) / 55,4 (LS) °C/W su 4 strati; dissipatori separati per die, **no exposed pad** |
| Batteria invertita | assente nel chip | assente: regge −15 A sui diodi di body; protezione a monte o diodo/MOSFET (§3.2). **Coperta dalla catena d'ingresso EL-001/002** |
| Logica 3,3 V | VIH min 1,6 V | VIH max 2,1 V (Tab. 7): ok a 3,3 V; pull-down interni sugli ingressi **non dichiarati** nel testo letto |
| LCSC | **C2150479** (solo Q1), 78 pezzi, 4,35 $ | **C503078**, SO-16, **esaurito**, 1,92 $ (1) / 1,25 $ (100): fonte debole, listino |

- Rischi comuni: 5 A continui a 60 °C non reggono (DRV: budget ≈ 3,2 W contro ≈ 5 W; VNH: HS a 150 °C dissipa fino a 3 W con 40,7 °C/W). Il VEVOR ha duty dichiarato 25 % e ≈ 11 s per corsa: va quantificato con le curve di impedenza termica (Fig. 25/26 VNH, Fig. 2 DRV), che non ho potuto leggere. TVS con V_C < 40 V non lascia margine su nessuno dei due (VNH: 38 V assoluta max).
- Note VNH7100BAS: BAS e AS differiscono (BAS 38 V, AEC-Q100; AS 41 V da fonte debole); ordinare VNH7100BASTR, lo stock a zero va risolto prima. Alimentazione dalla standby: toggle INA/INB prima di PWM, con ritardo ≥ 20 µs (Tab. 6 nota 1).

## K-PH1, K-PH2 (ponte H pistone a relè) — Hongfa HF3FF-M/012-1ZS (LCSC C190459): **non adatto così com'è**
- Requisiti: REQ-EL-004. Stato: **Scartato come configurato (2 relè SPDT con NC a massa)**; scelta del relè through-hole saldato a mano, dell'utente (2026-10-14).
- Fonte: datasheet Hongfa HF3FF-M, "2024 Rev. 1.01", **letto direttamente dalla copia locale** (pagine Characteristics, Contact data, Coil data); mono-fonte; il verificatore aveva letto un estratto confuso e le sue letture sul NC erano incomplete.
- Parametri decisivi (Hongfa HF3FF-M, tabelle Contact data e Coil data):
  - Contatti per **carico resistivo a 13,5 VDC**, durata 1×10⁵ OPS: **NO 15 A, NC 5 A** (colonne 1C), AgSnO₂, max 10 A continui, 30 VDC. **Nessun rating DC induttivo**; la nota 1 rimanda a Hongfa per 24 VDC o condizioni diverse.
  - Relè automotive per chiusura centralizzata / antifurto (applicazioni tipiche del datasheet), plastic sealed (suffisso S).
  - Bobina 12 V: 320 Ω ±10 %, 0,45 W, pull-in max **9,0 V** (23 °C), drop-out min 1,2 V, **sovratensione ammessa 15,6 V a 23 °C e 14,4 V a 85 °C** (senza carico). Operate 5 ms tip. / 10 ms max, release 3 / 10 ms. Ambiente −40…+85 °C. Ingombro 15,2 × 19 mm, 4 pin, foro 1,3 mm.
- Perché non va:
  - Con COM sulle uscite del motore, NO a +12 V e NC a massa, **il contatto NC porta la corrente del motore: 5 A di rating resistivo contro 5 A di marcia e 10 A di stallo assunto (EL-004, Assumed)**. Nessun margine, e per un carico induttivo.
  - Nessun dato su L/R o corrente di spunto: la vita elettrica per questo carico non è dimostrabile.
  - Bobina: i 16 V continui di REQ-EL-001 superano i 15,6 V ammessi; a 60 °C il limite sale a circa 15 V per interpolazione (mia stima), e il pull-in con LFP a 10 V ha margine ridotto a caldo (la resistenza di bobina cresce con la temperatura: stima mia). Pilotare la bobina con tensione regolata o con un limitatore.
  - Stock LCSC: la pagina mostrava "Not available now" (fonte debole); il prezzo 0,47–0,81 $ è un listino non verificato.
- Alternative da valutare (non scelte):
  - **4 relè SPST NO (HF3FF-M/012-1HS) come ponte a 4 interruttori**: tutta la corrente sui contatti NO (15 A resistivi), ma 4 relè, interblocco hardware e nessun dato induttivo.
  - Relè 1C con **NC ≥ 10 A documentato in DC induttivo** (famiglie automotive tipo 30/20 A): da cercare e verificare sul datasheet; ingombro maggiore.
  - Ponte discreto MOSFET SMD, oppure il VNH7100BAS (sez. U-PH1).

## K-PH1, K-PH2 (ponte H pistone a relè, seconda proposta) — STEIPU ST8N-2A-12 (dual Form A, through-hole)
- Requisiti: REQ-EL-004; REQ-SW-002 (stato sicuro). Stato: **Proposto**, scelta dell'utente del PDF (2026-10-14) con la topologia sotto. Nessuna conferma di stock/codice LCSC.
- Fonte: datasheet STEIPU ST8N, "V1.1-24" (PDF fornito dall'utente, stampato da PowerPoint, con avvertenza "solo di riferimento"), **letto direttamente**; mono-fonte, produttore piccolo, nessun datasheet con firma di revisione ufficiale. La ricerca web ha dato V1.2-24: confrontare.
- Parametri decisivi (datasheet ST8N, pagine Contact data, Coil data, Contact load):
  - Configurazioni 1A, 1C, 2A, 2C (2 relè in un solo corpo), larghezza 7,2 mm, peso circa 4 g (S) / 8 g (doppio).
  - Contatti: **25 A a 16 VDC**, corrente di commutazione max 30 A, potenza max 480 W, **tensione di commutazione max 16 VDC**, resistenza di contatto max 100 mΩ (1 A, 5 VDC), carico minimo 1 A 6 VDC, lega di Ag.
  - **Carico motore a 13,5 VDC, NO, 1×10⁵ operazioni:** inserzione (spunto) 25 A, apertura 25 A (on/off 0,5 s / 9,5 s). Prova "alzacristalli simulato": spunto 25 A, regime 10 A, apertura 25 A. È un rating DC su motore, che l'HF3FF-M non aveva. Il carico dell'attuatore (5 A di marcia, 10 A di stallo assunto, EL-004 Assumed) sta sotto.
  - **Colonna NC: "--"**: il rating NC non è dato, anche se la nota dice che la durata è provata "con il contatto NO o NC" (testo ambiguo). **Non usare l'NC per la corrente del motore** finché il produttore non lo conferma.
  - Bobina 12 V standard: 180 Ω (±10 %), 0,8 W, operate max 6,5 V, release min 1,2 V; versione "L" sensibile: 225 Ω, 0,64 W, operate 7,2 V. **Tensione continua max 170 % della nominale (circa 20 V)**: i 16 V di REQ-EL-001 sono coperti. Operate 10 ms / release 5 ms, temperatura −40…+105 °C, endurance meccanica 1×10⁷.
- Topologia proposta con soli contatti NO: **2 relè 2A (4 contatti NO)**. K1 chiude +12 V → OUTA e GND (shunt) → OUTB; K2 chiude +12 V → OUTB e GND → OUTA. A bobine diseccitate le due uscite sono flottanti (nessuna frenata dinamica, compatibile con REQ-SW-002; il pistone è autobloccante, i finecorsa interni fermano la corsa).
- Rischi / note:
  - ⚠️ **K1 e K2 eccitati insieme mettono +12 V e GND in cortocircuito attraverso i contatti** (OUTA: +12 V da K1, GND da K2). Serve interblocco hardware (non solo firmware) e un tempo morto fra inversioni di marcia.
  - ⚠️ **Tensione di commutazione max 16 VDC = limite di REQ-EL-001 a 16 V continui:** nessun margine. Il picco induttivo all'apertura va assorbito con un clamp bidirezionale (TVS o varistore) sui morsetti del motore: dimensionamento da fare.
  - Il datasheet non dà corrente di picco oltre la tabella, né declassamento in temperatura: a +60 °C la portata non è dimostrata.
  - Dimensioni, passo e foratura sono solo nei disegni (non estratti): serve il disegno per il footprint. Through-hole saldato a mano dopo il reflow (scelta dell'utente).
  - Se il produttore conferma l'NC per carico motore si potrebbe usare un 2C (DPDT) come inversore, con un solo relè; da chiedere a STEIPU.
  - Costo e codice LCSC non verificati (la ricerca non ha trovato ST8N su LCSC).

## K-PH1 (inversione di marcia pistone) — STEIPU ST8N-2C-12S (LCSC C41432833), **sostituisce la proposta ST8N-2A a due relè**
- Requisiti: REQ-EL-004; REQ-SW-002. Stato: **Proposto** (scelta del codice dell'utente, 2026-10-14; topologia mia, da confermare).
- Fonte: pagina LCSC C41432833 (listino, fonte debole) e datasheet STEIPU ST8N V1.1-24 letto direttamente (vedi voce precedente). Dati LCSC: **2 Form C (DPDT)**, bobina 12 V 180 Ω 0,8 W, through-hole 14 × 7,2 mm, altezza 13,5 mm, 25 A a 16 VDC, **1,37 $ (1 pz), 0,86 $ (100 pz), 12 pezzi a stock**, tubo da 25. **Correzione del 2026-10-14 (schema della pagina LCSC fornito dall'utente):** il corpo contiene **due relè 1C indipendenti, ciascuno con la propria bobina** (non una bobina sola come avevo scritto). Per la topologia sotto vanno quindi **pilotate insieme le due bobine** (circa 2 × 67 mA a 12 V, 2 × 81 mA a 14,6 V, mia stima da 180 Ω), da un solo interruttore: un'alternativa è pilotarle separatamente, ma con NC e NO assegnati come sotto l'NC porterebbe corrente in entrambi i sensi (vedi note).
- **Topologia proposta: un solo relè DPDT per invertire la polarità, più un interruttore low-side per marcia/stop.**
  - COM1 → OUTA, COM2 → OUTB. NO1 e NC2 → +12 V; NC1 e NO2 → GND_SW (nodo di ritorno commutato).
  - Bobina eccitata: OUTA = +12 V, OUTB = GND_SW (un senso). Diseccitata: polarità opposta (altro senso).
  - GND_SW → MOSFET N low-side → shunt 3 mΩ (R-SH2) → massa. Marcia = MOSFET acceso; stop = spento; la polarità si cambia **a MOSFET spento**.
- Vantaggi:
  - **Nessun cortocircuito possibile** fra +12 V e massa attraverso i contatti (ogni uscita è sempre l'opposto dell'altra): sparisce il problema dell'interblocco della proposta a due relè.
  - I contatti **non commutano sotto carico** nel funzionamento normale: il carico lo apre e lo chiude il MOSFET. Il rating NC "--" del datasheet pesa molto meno (resta da provare come tenuta di corrente, non come apertura/chiusura).
  - Un solo componente relè da 1,4 $ (due relè in un corpo, bobine unite), più un MOSFET e un diodo; PWM e partenza morbida possibili.
  - Con le bobine **separate** (pilotaggio indipendente) si avrebbe frenata dinamica (entrambe diseccitate = uscite a GND_SW), ma ogni senso passerebbe da un NC (senso avanti: NC del relè B; indietro: NC del relè A): **peggio** per il rating NC non dato. Per questo si propone di unire le bobine.
  - Stato sicuro (REQ-SW-002): pull-down sul gate del MOSFET, motore spento; la posizione del relè a riposo è indifferente.
- Rischi / note:
  - ⚠️ **L'NC porta la corrente del motore in uno dei due sensi** (rating NC non dato): assegnare alla posizione di riposo il senso meno gravoso, e chiedere a STEIPU conferma per carico motore.
  - ⚠️ **Sequenza obbligatoria: MOSFET spento → inversione relè → MOSFET acceso**, con tempo morto ≥ release/operate (10 ms) e rimbalzo. Se il firmware sbaglia, l'inversione sotto carico apre contatti a 5–10 A induttivi (rating non dimostrato). Valutare un ritardo hardware sul gate che impedisca l'accensione finché la bobina commuta.
  - **Spegnimento induttivo:** all'apertura del MOSFET il nodo GND_SW sale. Serve un clamp (Schottky o TVS) da GND_SW verso +12 V, dimensionato per 10 A di picco. Lo scarico si ritrova sul +12 V a valle della catena d'ingresso (che ha un P-MOSFET ideal-diode, quindi la corrente non rientra nella batteria): serve un condensatore di bulk o una TVS adeguati. Da dimensionare.
  - La tensione di commutazione massima del relè è 16 VDC, pari al limite di REQ-EL-001 (nessun margine).
  - Stock 12 pezzi: fonte debole, può non bastare per più schede.
  - Il MOSFET low-side, il diodo di clamp e lo shunt/INA180 sono **da scegliere** (sez. A2 resta valida per la misura).

### K-PH1 — variante a **bobine separate con frenata dinamica** (richiesta dell'utente, 2026-10-14): gestione del rating NC
Stato: **Proposto**, sostituisce la scelta "bobine unite" della voce precedente. Il datasheet ST8N non dà il rating NC (colonna "--"): non si può eliminare, si può solo **ridurne l'esposizione** e **verificarlo al banco**.

- **Cablaggio (W1):** per entrambi i relè COM → uscita motore, **NO → +12 V**, **NC → GND_SW**; GND_SW → MOSFET N low-side → shunt 3 mΩ → massa. Clamp Schottky/TVS da GND_SW a +12 V.
- **Stati (A, B = bobina eccitata):**

| A | B | Uscita A | Uscita B | Effetto | Contatti che portano corrente |
|---|---|---|---|---|---|
| 0 | 0 | GND_SW | GND_SW | **frenata** (motore in corto fra i due NC) | solo la corrente di forza controelettromotrice, piccola |
| 1 | 0 | +12 V | GND_SW | avanti (MOSFET acceso) | NO di A, **NC di B** |
| 0 | 1 | GND_SW | +12 V | indietro (MOSFET acceso) | NO di B, **NC di A** |
| 1 | 1 | +12 V | +12 V | frenata a +12 V, da non usare | nessuna |

  - Con bobine diseccitate il motore è in frenata (compatibile con REQ-SW-002). Nessun cortocircuito +12 V/massa possibile: ogni relè commuta fra +12 V e GND_SW (break-before-make).
  - **Perché W1 e non l'inverso (NO → GND_SW, NC → +12 V):** se una bobina cade mentre il motore gira, il contatto che si apre sotto carico è il **NO**, che ha il rating di 25 A con carico motore a 13,5 VDC; l'NC si chiude solo verso GND_SW dove la corrente è già quella di frenata. Con il cablaggio inverso si aprirebbe un NO verso massa e si chiuderebbe un NC verso +12 V.
- **Come si riduce l'esposizione dell'NC:**
  1. **Nessuna apertura/chiusura sotto carico in marcia normale:** la corrente la accende e la spegne il MOSFET; sequenza obbligatoria MOSFET off → relè → attesa ≥ 20 ms (operate 10 ms + rimbalzo, ipotesi mia) → MOSFET on.
  2. **Interblocco hardware sul gate del MOSFET** (ritardo a RC o abilitazione dalle bobine) in modo che un errore del firmware non accenda il MOSFET durante la commutazione.
  3. **Limite di corrente dal firmware sullo shunt** (canale 12 A f.s.): stallo a metà corsa → MOSFET off in < 200 ms; a fine corsa i finecorsa interni aprono il circuito (Confirmed, EL-004).
  4. **Limite di tempo di marcia** (circa 11 s per 152 mm a 14 mm/s dal VEVOR; duty 25 % dichiarato), per limitare il riscaldamento dei contatti.
  5. **Rating del carico:** il carico previsto (5 A di marcia, 10 A di stallo, Assumed) sta sotto i valori NO provati (regime 10 A, spunto 25 A); l'NC non è dimostrato.
- **Riscaldamento dei contatti:** la resistenza di contatto iniziale max è 100 mΩ (1 A, 5 VDC): al valore massimo ammesso sarebbero 2,5 W per contatto a 5 A (5 W con due contatti in serie) in un relè da 4 g. Il valore tipico non è dato. **Da misurare.**
- **Prova al banco prima di congelare [B], su 3 esemplari:** caduta di tensione ai capi di NC e NO a 5 A e 10 A, temperatura del corpo dopo una corsa completa, 1000 cicli avanti/indietro con MOSFET a bordo; criterio da definire (caduta NC non peggiore del doppio di quella NO, temperatura corpo < 85 °C a 25 °C ambiente).
- **Domande a STEIPU:** (1) rating NC per carico motore a 13,5 VDC (corrente, cicli); (2) corrente di tenuta continua di NC e NO a +60 °C; (3) resistenza di contatto tipica a 5 e 10 A; (4) conferma del datasheet V1.2-24 contro V1.1-24 fornita.
- **Piano B se la prova fallisce o STEIPU non conferma:** ponte a **4 relè SPST NO** (due corpi ST8N-2C, usando solo COM e NO; costo circa 2,7 $), con **interblocco hardware** obbligatorio perché +12 V e GND_SW si possono mettere in corto; oppure il VNH7100BAS (sez. U-PH1).

### K-PH1 — cablaggio **W3** (idea dell'utente: DPDT per il verso + MOSFET per l'alimentazione), con bobine separate: **sostituisce W1**
Stato: **Proposto** (2026-10-14). Il corpo ST8N-2C contiene due relè 1C a bobine indipendenti; cablati come un DPDT di inversione, ma con le bobine pilotabili una per una, danno anche la frenata.

- **Cablaggio:** relè A: COM → OUTA, **NO → +12 V**, **NC → GND_SW**. Relè B: COM → OUTB, **NO → GND_SW**, **NC → +12 V**. GND_SW → MOSFET N low-side → shunt 3 mΩ → massa. Clamp da GND_SW a +12 V (come in W1).

| A | B | Uscita A | Uscita B | Effetto | Contatti con corrente |
|---|---|---|---|---|---|
| 1 | 1 | +12 V (NO) | GND_SW (NO) | **avanti** | **solo NO** (25 A con carico motore, provato) |
| 0 | 0 | GND_SW (NC) | +12 V (NC) | **indietro** | **solo NC** (rating non dato) |
| 1 | 0 | +12 V (NO) | +12 V (NC) | frenata (motore in corto) | solo corrente di frenata |
| 0 | 1 | GND_SW (NC) | GND_SW (NO) | frenata (motore in corto) | solo corrente di frenata |

- Con il DPDT unito (bobine in parallelo) si hanno solo i primi due stati; con le bobine separate gli stati misti danno la **frenata dinamica** senza altri componenti. Nessun cortocircuito +12 V/massa possibile.
- **Rispetto a W1 l'NC porta la corrente in un solo senso** (indietro), non in entrambi: dimezza l'esposizione. Assegnare all'"indietro" il senso con il carico meno gravoso, che l'utente deve indicare (estensione o ritrazione del pistone: dato non ancora in possesso, aggiungere a OPEN-04).
- **Bobine diseccitate = senso "indietro", con MOSFET spento:** il motore è flottante, non frenato (stato sicuro REQ-SW-002 rispettato: nessuna corrente, pull-down sul gate). Per frenare dopo uno stop: MOSFET spento, poi si porta un solo relè nello stato misto.
- **Sequenze:** avanti ↔ indietro: MOSFET off → frenata (stato misto, per esempio 1,0) → attesa → stato finale → attesa ≥ 20 ms (ipotesi mia) → MOSFET on. Le mitigazioni di W1 (interblocco sul gate, limite di corrente dallo shunt, tempo di marcia, prova al banco su NC, domande a STEIPU, piano B a 4 relè SPST NO) valgono anche qui.
- **Consumo bobine:** in "avanti" sono eccitate entrambe (circa 133 mA a 12 V, mia stima da 180 Ω ciascuna); "indietro" a bobine spente: 0 mA.

### K-PH1 — nota del 2026-10-14: **niente frenata dinamica** (precisazione dell'utente)
L'idea dell'utente è un **DPDT a relè unico (una sola bobina) + MOSFET**: con una bobina sola esistono solo gli stati "avanti" (bobina eccitata, solo contatti NO) e "indietro" (bobina diseccitata, solo contatti NC), quindi **la frenata dinamica non è prevista**. Resta valido il cablaggio W3 (primi due stati della tabella), con gli stessi rischi e mitigazioni sull'NC (un solo senso). Il motore si ferma lasciandolo flottante (MOSFET spento); il pistone è autobloccante e i finecorsa interni fermano la corsa.
- **Conseguenza sul componente:** l'ST8N-2C-12S (C41432833) contiene **due relè con due bobine**: si può usare come DPDT unendo le bobine (consumo circa 133 mA a 12 V, circa 1,6 W a 14,6 V, mia stima da 180 Ω ciascuna, solo in "avanti"), oppure tenere separati i due pin bobina per riavere la frenata in futuro. Non ho verificato un DPDT a bobina unica con rating NO/NC per carico motore: se si vuole risparmiare corrente di bobina va cercato e verificato sul datasheet.

### K-PH1 — seconda fonte per l'ST8N-2C: American Zettler **AZ9891J-2C-12DE** (datasheet 3/4/20, letto direttamente dalla copia locale scaricata dal verificatore)
- Stato: **informazione**, non una nuova scelta. I valori coincidono con quelli del datasheet STEIPU ST8N (stessa famiglia o clone: non dichiarato, è una mia inferenza), quindi danno una **seconda fonte per i dati di contatto e bobina**, con un costruttore noto.
- Dati (datasheet AZ9891J, pagine Contacts / General data / Coil / Ordering): carico resistivo max 480 W, 30 A, 16 VDC; **carico nominale 25 A a 16 VDC con rotore bloccato** (locked motor); **vita elettrica 1×10⁵ operazioni a 25 A, 14 VDC, rotore bloccato**; meccanica 1×10⁶; contatti AgSnO, resistenza iniziale < 50 mΩ (6 V, 1 A); operate/release 10 ms tip.; rilascio a > 8,3 % della tensione nominale; ambiente −40…+85 °C (versione "T" 105 °C); peso 4,1 g.
- **Il rating non distingue NO e NC**: vale per il relè (carico motore a rotore bloccato). Il rischio sul NC resta, ma il carico di stallo previsto (10 A assunto) sta ben sotto i 25 A provati a rotore bloccato.
- Bobina "2 Form C **twin coil**": **due bobine** da 180 Ω ±10 %, must operate 7,2 V, **max continua 16,0 V**, 0,8 W ciascuna. Quindi anche l'AZ9891J-2C **non è un DPDT a bobina unica**. Sul datasheet ST8N il limite continuo era dato come 170 % della nominale; l'AZ dà 16,0 V.
- Dimensioni: 14,3 × 15,7 mm di impronta (twin), altezza 13,8 mm max; piedini 1,2 × 0,3 mm e 0,5 × 0,3 mm; pin-out e passo nel disegno (non estratto).
- Prezzo/stock: DigiKey 3,15 $ (1 pz), 2,22 $ da 1036 pz, 1901 pezzi, lead time 9 settimane (fonte debole, da verificatore); nessun codice LCSC trovato. Future Electronics lo classifica DPST con 225 Ω: quasi certamente errato.

### K-PH1 — alternativa documentata: CIT **A102CS12VDC** (serie A10, 2C = due SPDT, datasheet CIT "A10 Rev C 03/2024", letto direttamente dalla copia locale)
- Stato: **candidato**, non scelto. **Anche questo è un doppio relè a due bobine** (2C = "(2) SPDT"), non un DPDT a bobina unica.
- Dati (datasheet CIT A10, pagine 1–2):
  - **Rating NO e NC separati a 14 VDC:** 2C: **NO 25 A (30 A max); NC 20 A (25 A max)**. Corrente continua limite NO/NC: **30/25 A a 23 °C, 25/20 A a 85 °C**. Commutazione max 40 A in inserzione, 30 A in apertura (3 s, rapporto make/break 1:10). Tensione di commutazione max 28 VDC, potenza max 420 W.
  - **Nessun rating per carico motore o induttivo**, nessuna prova a rotore bloccato: vita elettrica "100K cicli, media a carico nominale".
  - Contatti AgSnO₂, resistenza iniziale < 30 mΩ. Operate 4 ms, release 1,5 ms.
  - **Bobina 12 V: 254 Ω, 0,55 W, pull-in max 7,0 V (58 %), release min 1,2 V, tensione massima 14,4 V (120 % della nominale).** I 14,6 V di carica LFP e i 16 V continui di REQ-EL-001 **superano il massimo di bobina**: serve un limitatore o un riduttore di tensione in serie alle bobine.
  - Esercizio −40…+105 °C. Corpo 12,0 (23,8 per il doppio) × 12,9 × 9,9 mm, peso 4 g (8 g doppio). I disegni dei piedini sono nel PDF (passo non estratto in modo affidabile).
- Prezzo/stock (fonte debole, DigiKey, dal verificatore): 3,26 $ (1), 2,59 $ (100), 2.938 pezzi, lead time 15 settimane. Nessun codice LCSC trovato.
- **Confronto con ST8N-2C e AZ9891J-2C:** il CIT ha l'unico rating NC separato (20 A a 14 VDC) ma non ha il dato a rotore bloccato; ha l'ingombro più piccolo e la bobina meno robusta (max 14,4 V contro 16 V). ST8N e AZ9891J hanno 25 A a rotore bloccato provati, senza distinzione NO/NC e con bobina fino a 16 V.

### Hongfa HF115F/012-2ZS4AF (LCSC C882372) — **non adatto per il rating**
- L'LCSC e Master Electronics danno **8 A a 250 VAC** per la versione 2Z; i "16 A" del titolo di serie non valgono per il 2Z (fonte debole, da distributori). Il PDF Hongfa è stato scaricato ma ha i caratteri non estraibili: **rating DC e induttivo non letti**. Contatti AgSnO₂ (suffisso AF) o AgCdO (senza AF) secondo LCSC/JLCPCB.
- Bobina 12 V a bobina singola 360 Ω, 400 mW, ingombro 29 × 12,7 × 15,7 mm, LCSC 3,71 $ (1) fino a 2,50 $ (1000), 1.964 pezzi (fonte debole). Segnali contrastanti sul ciclo di vita della versione (257).

### American Zettler **AZ934-2C-12DET** — scartato (datasheet AZ934 del 7/17/19, letto direttamente)
- Anche questo è un **doppio relè**: il datasheet dice "Two separate relays in DPDT (dual) version", quindi due bobine, non un DPDT a bobina unica. Il PDF ufficiale riporta la filigrana **"Discontinued"** (dato dal verificatore, filigrana letta dal contenuto del PDF).
- Dati: 20 A / 25 A (make/break, "make" riferito a lampada) a 14 VDC resistivi, vita 2×10⁵ operazioni a 20 A, 14 VDC resistivi; 280 W, 100 VDC max; AgSnO₂, < 100 mΩ (1 A, 5 VDC); bobina 255 Ω, must operate 7,2 V, **max continua 24 V**; peso 10 g; −40…+100 °C. **Nessun rating motore/induttivo né NO/NC separati.** Nessun codice LCSC trovato.
- Motivo dello scarto: prodotto discontinuato, nessun dato su carico motore, nessun vantaggio rispetto all'AZ9891J-2C o all'ST8N-2C.

### TE Connectivity **RTE24012** (LCSC C1524518) — DPDT a bobina unica, **scartato per il carico DC** (datasheet TE "RT2 DC and AC", letto direttamente dalla copia locale)
- Bobina unica (2 Form C): **360 Ω ±10 %, 400 mW, operate max 8,4 V, release min 1,2 V** (23 °C, senza pre-eccitazione). Ambiente −40…+85 °C. Corrente limite continua 8 A (UL 10 A), corrente di inserzione limite 15 A per max 4 s con duty 10 %, AgNi 90/10, operate/release 8/6 ms max.
- Rating dei contatti: tutti **AC** (8 A, 250 VAC, cos φ = 1, 10×10³ cicli; 10 A uso generale UL 20×10³). In DC l'unico dato in tabella è **DC13, 24 VDC, 2 A** (EN 60947-5-1, categoria induttiva) e DC13 250 VDC 0,2 A. La curva "Max. DC load breaking capacity" è un grafico, non letto. **Nessun rating per carico motore né per NO/NC separati.**
- Perché non va: a 14 V con un motore da 5 A di marcia e 10 A di stallo (EL-004, Assumed) l'unico rating induttivo DC documentato è 2 A, e il limite continuo (8 A) è sotto lo stallo. Pull-in a 8,4 V ha poco margine con LFP a 10 V (rapporto 1,19, mia stima); il limite di tensione continua di bobina non è stato letto.
- LCSC: 2,29 $ (1), 1,65 $ (100), 2.747 pezzi (fonte debole); DigiKey 21.566 pezzi, lead time 19 settimane (dal verificatore).

### Esito della ricerca "DPDT a bobina unica con rating motore" (2026-10-14)
- **Nessun DPDT a bobina unica trovato con rating motore documentato.** Il TE RTE24012 e l'Hongfa HF115F-2Z sono da 8 A in AC; il TE ha un solo dato DC induttivo (24 VDC 2 A). Tutti i relè con 25 A su motore provati o con NC separato (ST8N-2C, AZ9891J-2C, CIT A10-2C, AZ934-2C) sono **doppi relè a due bobine**.
- **Scelta consigliata:** relè a due bobine con bobine unite, con priorità a **ST8N-2C-12S (C41432833, LCSC)** e come seconda fonte **AZ9891J-2C-12DE** (stessi valori da datasheet American Zettler). Rating motore: 25 A a 16 VDC a rotore bloccato, vita 1×10⁵ operazioni a 25 A, 14 VDC; bobina fino a 16 V continui; rating NC non distinto (rischio residuo da provare al banco).

### K-PH1 — **decisione dell'utente 2026-10-14: si usa il TE RTE24012 (LCSC C1524518)**, DPDT a bobina unica
- Stato: **Proposto** (scelta dell'utente, contro il consiglio del verificatore: il rating DC non è dimostrato). Topologia: W3 a due soli stati (vedi sopra), bobina unica 12 V / 360 Ω; **frenata non prevista**.
- **Condizioni di progetto che ne derivano (tutte Assumed, da provare al banco):**
  - **Corrente di tenuta dei contatti ≤ 8 A** (limite continuo del datasheet): il firmware spegne il MOSFET a circa 7 A misurati sullo shunt; lo stallo assunto a 10 A **non** va mai sostenuto sul relè.
  - **I contatti non devono mai aprirsi né chiudersi sotto carico**: l'unico dato DC induttivo del datasheet è 24 VDC a 2 A (DC13). Sequenza obbligatoria MOSFET off → attesa → relè → attesa ≥ 20 ms (operate 8 ms max, bounce 4/10 ms) → MOSFET on, con interblocco hardware sul gate.
  - **Bobina:** operate max 8,4 V (23 °C) contro il minimo LFP di 10 V: margine di 1,6 V, da verificare a −10 °C; la tensione continua massima di bobina non è nel datasheet letto: **verificare** prima di alimentarla a 14,6–16 V (dissipazione 0,57–0,71 W a 14,6–16 V). Soluzione da valutare: limitatore o resistenza in serie, dopo la verifica del pull-in a freddo.
  - **Prova al banco su 3 esemplari** (caduta ai capi di NO e NC a 5 A, temperatura del corpo, 1000 cicli) e domanda a TE sul rating DC induttivo, come per il piano di W3.

### R-SH2 (shunt pistone) — verifica del 2026-10-14: **RALEC LR2512-22R003F4 (LCSC C154669)** proposto
- Stato: **Proposto** (sostituisce la voce "3 mΩ, 2512, P/N da scegliere" della sez. A2). Fonti: datasheet RALEC IE-SP-060 (2023/12/07) letto dal verificatore via estrazione di testo (tabelle confuse, curve di declassamento non lette); TI SBOS741H per l'INA180. Mono-fonte, nessuna seconda fonte indipendente.
- Dati: 3 mΩ ±1 %, 2 W a 70 °C, **TCR ±25 ppm/°C** (il valore ±50 del mio brief era sbagliato per 3 mΩ), −55…+170 °C, sovraccarico 5×P per 5 s, 2 terminali (nessuna variante a 4 terminali trovata), lega FeCrAl. LCSC: **2.280 pezzi**, 0,109 $ (5 pz), 0,087 $ (100 pz). La versione 3 W (C154686) è identica ma risultava esaurita.
- Dissipazione: 0,43 W a 12 A (21,5 % di 2 W, 3 W per C154686), 0,075 W a 5 A. Il declassamento è riferito al terminale, non letto: verificare sul PDF.
- **Lettura Kelvin su 2 terminali:** tracce di sense prese sul bordo interno di ciascun pad; il rame dei terminali entra comunque nella misura. Controllare i disegni di pad sul PDF originale.
- **Errore e risoluzione (calcolo del verificatore, caso peggiore, ΔT 65 K assunto):** senza calibrazione circa 330 mA a 12 A (tolleranza shunt 120, guadagno INA 120, offset 50–73, TCR 19,5 mA); **con calibrazione a zero e fondo scala circa 40 mA**. Quindi il criterio di risoluzione 100 mA (EL-004) è raggiungibile **solo con calibrazione in firmware**.
- **INA180A2:** tutte le specifiche (offset ±150 µV, guadagno ±1 %) sono a V_S = 5 V; a 3,3 V l'offset non è garantito (PSRR 40 µV/V max aggiunge fino a circa 68 µV): **valutare l'alimentazione a 5 V** o accettare la calibrazione. L'uscita minima (5 mV max) rende inaffidabile la lettura sotto 30–50 mA.
- Alternative: Bourns CSS2H-2512K-3L00F (4 W, REV. 01/26, AEC-Q200, < 5 nH, ma non LCSC e lead time 19 settimane); RESI/C&B ECSR2512FR003K9 (±100 ppm/°C, esaurito) e Milliohm LRS2512-3WR003F (documentazione debole): scartati.

## Q_PWR (MOSFET low-side pistone) — verifica del 2026-10-14: **Diodes DMTH6005LK3-13** proposto, riserva **Infineon IPD50N06S4L-12**
- Requisiti: REQ-EL-004 (5 A di marcia, 10 A di stallo assunti, firmware spegne a circa 7 A), REQ-SW-002 (stato sicuro con pull-down sul gate), REQ-EL-002 (picchi sul rail +12 V fino a circa 36–38 V). Stato: **Proposto**, scelta mia su verifica `datasheet-verifier`; **non congelato**.
- Posizione: drain su GND_SW, source su R-SH2 (3 mΩ). Pilotaggio del gate: **10–12 V da traslatore** (ipotesi b). **Il pilotaggio diretto a 3,3 V (ipotesi a) non è verificabile: nessuna parte ha R_DS(on) garantito a V_GS = 3,3 V** (V_GS(th) max 3 V su Diodes e Vishay).
- Fonti: datasheet dei costruttori letti dal verificatore (Diodes DS38211 Rev 3-2 giu. 2022; Infineon Rev 1.0 mar. 2009; Vishay Rev F 2013; DOINGTER V1.0). Valori a caldo e T_J derivati da grafici e R_θJA (±10 %, calcoli del verificatore, **non** dati di datasheet); il rame da 1 cm² non è documentato (i datasheet usano 6–6,45 cm²).
- Confronto sintetico: V_DS 60 V per tutti.

| | Diodes DMTH6005LK3 | Infineon IPD50N06S4L-12 | Vishay SUD50N06-09L | DOINGTER (C49237811) |
|---|---|---|---|---|
| R_DS(on) max 10 V / 4,5 V, 25 °C | 5,6 / 10 mΩ | 12 / 21,6 mΩ | 9,3 / 12,2 mΩ | 15 / 20 mΩ |
| R_θJA | 38 K/W (1 in², 2 oz) | 62 (minimo) / 40 K/W (6 cm²) | 40–50 K/W (1 in²) | non dato |
| T_J a 60 °C, 7 A, 10 V | circa 76 °C | circa 95–115 °C | circa 99 °C | circa 119 °C (assunto) |
| Stallo 10 A per 11 s | circa 93 °C | circa 132–172 °C | circa 140 °C | circa 180 °C (assunto) |
| V_GS max | ±20 V | ±16 V | ±20 V | ±20 V |
| LCSC | solo variante Q (C211367), stock 1 | solo clone TECH PUBLIC (C51939570, 2.690 pz) | C468004, stock 0, obsoleto | 165 pz, **marchio terzo** |
| Prezzo (1 / 100) | 1,97 $ / 0,84 $ (DigiKey) | 1,64 $ / 0,69 $ (DigiKey) | n/d | 0,13 $ a 5+ |
| Ciclo di vita | Attivo, lead time 40 settimane | Attivo, lead time 12 settimane | Obsoleto (fonte debole) | non dichiarato |

- Perché il Diodes: la dissipazione più bassa (0,43 W a 7 A, 0,87 W a 10 A), V_GS max ±20 V, SOA fino a 1 s, E_AS 98 mJ. Da acquistare **fuori LCSC** (DigiKey/Mouser), che con assemblaggio manuale è possibile.
- **Il DOINGTER non è equivalente al Vishay** (R_DS(on) 15 contro 9,3 mΩ, R_θJC 2 contro 1,1 K/W, I_D a 100 °C 33 contro 50 A): utilizzabile a 10–12 V e 5–7 A, ma senza dati termici e con rischio di lotti diversi; scartato come prima scelta.
- Rischi / note:
  - ⚠️ **Il rame da 1 cm² non è documentato:** con meno di 6 cm² le T_J salgono; prevedere rame e via termici sul PCB.
  - ⚠️ **Lo stallo di 11 s a 10 A è un caso termico non coperto dalla SOA:** nessun datasheet dà la corrente ammissibile per 1–11 s. Il firmware spegne a circa 7 A entro 200 ms; il relè in serie ha comunque limite continuo di 8 A.
  - **Se si usa l'Infineon:** V_GS max ±16 V; con il traslatore alimentato dal rail +12 V (picchi fino a 36–38 V) serve una Zener (circa 12–15 V) sul gate. Consigliata comunque anche sul Diodes.
  - Il clamp Schottky D_CL tiene il drain sotto circa 15 V, quindi l'avalanche è poco rilevante; D_CL va dimensionato per 10 A di picco, ≥ 60 V inversa.
  - Prova in ingresso se si usa un clone: R_DS(on) a 10 V e a 4,5 V, soglia.

### Q_PWR — **decisione dell'utente 2026-10-14: Infineon IPD50N06S4L-12 (PG-TO252-3-11)**
- Stato: **Proposto**, scelta dell'utente (la mia raccomandazione era il Diodes DMTH6005LK3-13). Dati dal datasheet Infineon Rev 1.0 (2009-03-23), letti dal verificatore: V_DS 60 V; R_DS(on) max 12 mΩ a 10 V (50 A) e 21,6 mΩ a 4,5 V (25 A); V_GS(th) 1,2 / 1,7 / 2,2 V (a 20 µA); **V_GS max ±16 V**; Q_g 30 typ / 40 max nC; C_iss 2220 typ pF; R_θJA 62 K/W (rame minimo) e 40 K/W (6 cm² Cu 70 µm); R_θJC 3 K/W; E_AS 33 mJ; DPAK passo 2,29 mm; attivo, lead time 12 settimane, 1,64 $ (1) / 0,69 $ (100) su DigiKey.
- **Conseguenze di progetto (Assumed, da verificare al banco):**
  - **Gate a 10–12 V, non a 3,3 V**: R_DS(on) è garantito solo a 4,5 V e 10 V.
  - **V_GS max ±16 V:** il gate non deve vedere il rail +12 V (16 V continui, picchi fino a 36–38 V). Zener di gate da circa 12 V (da scegliere) tra gate e source, più resistenza serie; tensione di gate di progetto 10–12 V.
  - **Termica più critica del Diodes:** 7 A a 60 °C ambiente: circa 95 °C con 6 cm² di rame (40 K/W), circa 115 °C con rame minimo (62 K/W); stallo 10 A per 11 s: circa 132 °C (40 K/W) e circa 172 °C (62 K/W), vicino al limite di 175 °C. **Prevedere almeno 6 cm² di rame con via termici sotto il drain** e lo spegnimento a circa 7 A entro 200 ms (firmware).
  - Acquisto **fuori LCSC** (DigiKey/Mouser, codice IPD50N06S4L12ATMA2); su LCSC esiste solo il clone TECH PUBLIC `IPD50N06S4L12-TP` (C51939570), che non sostituisce l'originale senza prova in ingresso.
- Proposta per il traslatore di gate, con **stato di default spento per sola rete passiva** (REQ-SW-002): GPIO → R (circa 4,7 kΩ) → NPN di piccolo segnale (es. SOT-23) → R (circa 2,2 kΩ) → base di un PNP di piccolo segnale con emettitore sul rail +12 V; collettore del PNP → R di gate (circa 22–47 Ω) → gate di Q_PWR. Resistenza gate-source circa 47–100 kΩ, Zener circa 12 V gate-source. Con GPIO flottante o in reset i due transistori sono spenti e il gate è a massa. Valori e P/N sono **da dimensionare e verificare**.

## U-DRV1 (driver di gate di Q_PWR) — TI UCC27517DBVR (LCSC C99395, SOT-23-5): **Proposto, verificato**
- Requisiti: REQ-EL-004; REQ-SW-002 (uscita bassa per sola rete passiva). Stato: **Proposto**; soluzione 2 scelta dall'utente (2026-10-14) fra le alternative al traslatore NPN+PNP. Verifica `datasheet-verifier` del 2026-10-14 sulla **versione HTML ufficiale TI** (SLUSAY4D mar. 2012–dic. 2014 per il non-A, SLUSBQ0C ago. 2013–ago. 2015 per l'A); mono-fonte, tabelle min/typ/max ambigue in alcune righe (V_IN_H, V_IN_L, ROH/ROL, tR/tF): ricontrollare sul PDF prima di congelare.
- Parametri decisivi (datasheet TI, sezioni Specifications e Pin configuration):
  - Pinout DBV: 1 VDD, 2 GND, **3 IN+**, 4 IN−, 5 OUT. Non invertente: IN+ = ingresso, **IN− a GND**. Con ingresso flottante o non polarizzato **OUT è tenuto basso** (resistori interni, valore non dichiarato).
  - VDD operativa 4,5–18 V (12 V nominali), **assoluta max 20 V**; UVLO on 3,91/4,20/4,5 V, off 3,45/3,9/4,35 V, isteresi 0,2/0,3/0,5 V; sotto UVLO OUT è basso. A 10 V non c'è UVLO.
  - Soglie ingresso fisse (indipendenti da VDD): V_IN_H circa 2,2–2,4 V, V_IN_L circa 1,0–1,2 V: compatibile con 3,3 V CMOS (margine circa 0,9 V). Ingressi −0,3…20 V (non-A) / −6…20 V (A).
  - Picco ±4 A a VDD = 12 V (C_LOAD 0,22 µF); ROH 5,0/7,5 Ω, ROL 0,5/1,0 Ω a 12 V; tR 8/12 ns, tF 7/11 ns con carico 1,8 nF; ritardo 13 ns. **Nessun dato a VDD = 10 V** (interpolato). OUT regge 500 mA di corrente di ritorno.
  - R_θJA 217,6 °C/W; a 1 kHz con Q_g 30 nC l'energia di gate è 0,36 mW: trascurabile.
- LCSC: **C99395**, TI, circa 0,25–0,32 $ (5–50 pezzi), stock 1.290–47.385 pezzi (dati discordanti fra le pagine: ricontrollare). **Controllare che C99395 sia il TI**: su DigiKey esiste un "UCC27517DBVR" di UMW con soglie diverse (V_IL/V_IH 0,8/2,7 V). Alternativa pin-compatibile UCC27517A (stessi parametri rilevanti).
- Circuito (da dimensionare): VDD da rail "VGATE" = +12 V → R circa 470 Ω → Zener 12 V (≥ 1 W consigliato) con condensatore vicino al pin 1 (≥ 1 µF, i dati sono con 1 µF); IN+ dall'uscita dell'interblocco (74LVC1G08) con pull-down 100 kΩ; IN− a GND; uscita → R di gate 10–22 Ω → gate; pull-down gate-source circa 47 kΩ.
- Rischi / note:
  - ⚠️ **VDD max 20 V:** se lo Zener va aperto con picchi a 36–38 V il driver si rompe; se va in corto VDD cade e il driver va in UVLO con uscita bassa (stato sicuro). Verificare la potenza di picco dello Zener sul suo datasheet (con 470 Ω: circa 0,66 W per 400 ms a 38 V).
  - ⚠️ **Sotto circa 7–8 V di VDD il MOSFET è mal pilotato ma l'UVLO (circa 4,2 V) non interviene:** il V_GS reale con VGATE a 9,8 V (batteria a 10 V) non è stato verificato.
  - Il V_OH del 74LVC1G08 sotto carico e alla temperatura minima va controllato sul suo datasheet.

### A2 — pistone: decisioni dell'utente del 2026-10-14/15 e revisione dello schematico (netlist letta da EasyEDA)
- **Decisioni (Confirmed, utente):** interblocco **solo software** (nessun interblocco hardware: sequenza ENA off → attesa ≥ 20 ms → DIR → attesa ≥ 20 ms → ENA on); **fusibile esterno** alla linea P2.1; collettore di U4 alimentato **direttamente dalla linea +12 V** (rete di P2.1, K1.14 e K1.22). Schema scelto per il gate: TLP293 (soluzione 1), non l'UCC27517.
- **Collegamenti letti dalla netlist EasyEDA:** linea +12 V (P2.1, K1.14 = NO1, K1.22 = NC2, collettore U4) e GND_SW (drain Q2, K1.12 = NC1, K1.24 = NO2, catodo D8) come da cablaggio W3; K1.11 → P1.1, K1.21 → P1.2; bobina K1.A1 su +12V, K1.A2 sul drain di Q1 con D5 (anodo su A2, catodo su +12V: **ricircolo corretto**); R7 tra source e GND; IN+ di U3 su source via R12, IN− su GND via R13, C1 10 nF fra i due; uscita U3 → R11 1 kΩ → rete `IN_LINEAR_MOTOR_SENSE` con D7 (3,3 V) a GND.
- **Errore trovato: D8 (SS56) è collegato in antiparallelo a Q2 (anodo sul source, catodo sul drain),** cioè duplica il diodo di body e **non** offre il ricircolo del motore. Va collegato con **anodo su GND_SW (drain) e catodo sulla linea +12 V** (P2.1).
- **Altri punti:** K1 è ancora l'RTE24012 (8 A, non regge 10 A; decisione dell'utente sull'ST8N-2C-12S in sospeso); Q2 è il clone **VBsemi** `IPD50N06S4L-12-VB` (non l'Infineon scelto), U3 è il clone **LX** `INA180A2IDBVR(LX)` (non il TI): i dati di verifica sono del costruttore originale; D8/D6/D7 sono R+O, **SS56 in package SMA** (5 A in SMA da verificare sul datasheet), manca un condensatore sul pin ADC dopo R11; pin-out K1 (12 = NC, 14 = NO) da confermare sul datasheet TE.

### A2 pistone — rilettura dello schematico e validazione del dimensionamento (2026-10-15, K1 = RTE24012 mantenuto dall'utente)
- **Netlist riletta da EasyEDA dopo la correzione:** D8 ora ha **anodo su GND_SW (drain Q2, K1.12, K1.24) e catodo sulla linea +12 V (P2.1, K1.14, K1.22, collettore U4, D8.K)**: errore chiuso. Aggiunto C2 100 nF fra l'uscita dell'INA (dopo R11) e GND (fc circa 1,6 kHz con R11 1 kΩ). Cablaggio W3, shunt, filtro d'ingresso 2×100 Ω + 10 nF, clamp D7 3,3 V e D5 come ricircolo di bobina: coerenti con il progetto.
- **Validazione (calcolo mio su dati dei datasheet già registrati; nessun dato nuovo da datasheet):**
  - Bobina: 33 mA a 12 V, circa 45 mA a 14,6 V con resistenza −10 %, circa 49 mA a 16 V (BSS138, limite 0,22 A: ok). V_DS di Q1 al ricircolo circa 13–17 V (D5 come diodo, limite 50 V): ok.
  - **Pull-in della bobina: non validato.** Operate max 8,4 V a 23 °C; a +60 °C la resistenza di bobina sale di circa 13 % (stima mia), quindi il pull-in sale verso circa 9,5 V; con rail a 10 V e BSS138 con V_GS di 3,3 V (R_DS(on) non specificata) restano circa 9,6 V: **margine nullo a batteria scarica e caldo**.
  - Gate di Q2: V_GS circa 9,5 V a 10 V di linea (R10 e R8 in partizione, V_CE(sat) circa 0,3 V); a 14,6–16 V D6 limita a circa 12 V, con corrente di Zener fino a CTR × I_F (circa 2–12 mA, 0,03–0,15 W, il caso estremo sta al limite dei 200 mW a +60 °C del SOD-323). Carica del gate (30 nC) in circa 15 µs a 2 mA di I_C: ok.
  - Spegnimento di Q2: τ circa 100 µs (R8 · C_iss); con D8 attivo l'energia nel FET è circa 7,5 mJ per stop a 10 A (E_AS 33 mJ): ok. L'impedenza termica a 100 µs (Fig. 4 Infineon) non è stata letta.
  - Ricircolo in D8: circa 10 A che decade con L/R (qualche ms), circa 30–135 mJ per stop a seconda di L ignota; V_RRM 60 V contro 38 V di picco: ok sulla carta; **SS56 R+O in SMA non verificata sul suo datasheet**.
  - Shunt e misura: R7 0,3 W a 10 A (0,43 W a 12 A) su 2 W; uscita INA 0,15 V/A: 1,5 V a 10 A, 1,8 V a 12 A, 2,45 V a circa 16 A; ADC ≤ 2,45 V rispettato. Clamp D7 fino a 5 V di uscita: ok, ma il ginocchio dello Zener può spostare la lettura di decine di mV vicino a 2,4 V (da misurare).
- **Verdetto:** lo stadio è coerente e valido per una corrente **≤ 8 A sul relè**. A 10 A di stallo non è valido finché K1 è l'RTE24012 (limite continuo 8 A, nessun dato DC induttivo). Con K1 invariato: soglia firmware a circa 7 A, con blanking dello spunto (corrente di spunto del motore, non nota) e sequenza ENA off → attesa → DIR → attesa → ENA on in software.
- **Aperti:** pull-in a caldo; cloni **VBsemi** (Q2) e **LX** (U3) al posto dei componenti verificati; SS56 R+O in SMA; nome di rete `12V` (netflag a (290,615), altro foglio) contro `+12V`; pin-out di K1 (12 = NC, 14 = NO) da confermare sul datasheet TE.

### A2 pistone — clone VBsemi (Q2) e LX (U3): datasheet forniti dall'utente il 2026-10-15, letti direttamente; **soglia di lavoro 7 A (Confirmed)**
- **Q2 = VBsemi IPD50N06S4L-12-VB** (datasheet VBsemi, TO-252). Il documento riprende la struttura e i valori del Vishay SUD50N06-09L, non dell'Infineon: V_DS 60 V; V_GS **±20 V**; R_DS(on) 10 mΩ (10 V, 20 A), 13 mΩ (4,5 V, 15 A), **16 mΩ a 125 °C, 20 mΩ a 175 °C** (le colonne Typ/Max non sono distinguibili nel testo estratto); V_GS(th) 1/2/3 V (250 µA); I_D 58 A (limitata dal package), I_DM 100 A; E_AS 125 mJ (L = 0,1 mH); Q_g 47 typ / 70 max nC; C_iss 2650 pF; **R_θJA 40 typ / 50 max °C/W** (1"×1" FR4, regime), R_θJC 0,85 / 1,1 °C/W; T_J max 175 °C; V_SD 1,5 V max. Valori "for design aid, not subject to production testing" (nota a). **Valori identici al Vishay: non misurati dal produttore, prova in ingresso consigliata** (R_DS(on) a 10 V e a 4,5 V, soglia).
  - Validazione a 7 A e 60 °C ambiente (calcolo mio): P = 7² · 16 mΩ = 0,78 W, ΔT = 0,78 · 50 = 39 K, **T_J ≈ 99 °C**; a 5 A: 0,40 W, circa 80 °C; stallo a 10 A (solo guasto, 200 ms): 1,6 W, circa 140 °C a regime, con rame ≥ 6 cm². Carica del gate 70 nC max in 35 µs a 2 mA di I_C; spegnimento τ = R8 · C_iss = 47 kΩ · 2,65 nF ≈ 125 µs. Il limite V_GS ±20 V dà più margine del ±16 V dell'Infineon: lo Zener D6 da 12 V resta valido.
  - **Q2 clone accettabile** sulla base di questo datasheet; l'Infineon originale non è più necessario.
- **U3 = LX INA180A2IDBVR(LX)** (Shenzhen Lingxing, documento "835-11-B5", 2024-08-A1, testo in cinese in gran parte non estratto ma tabelle numeriche leggibili): V_S 2,7–5,5 V (5 V di progetto, **alimentato a 5 V: il caso di prova**); V_CM −0,2…30 V; **V_OS ±150 µV max a V_CM = 0 V** (±500 µV a 12 V), deriva 25/150 (unità non estratte); **errore di guadagno ±0,1 % tip., ±1 % max**, deriva 1,5 / 20 ppm; CMRR min 84 dB; BW A2 210 kHz; I_Q 175 tip., 260 max µA; V_OL = V_GND + 0,5 mV tip. / 5 mV max, V_OH = V_S − 0,02 V tip. / −0,03 V; pinout A: 1 OUT, 2 GND, 3 IN+, 4 IN−, 5 VS (come lo schematico). **Il datasheet LX coincide con quello TI sui parametri che contano**, quindi la validazione della catena di misura vale anche per il clone.
  - **Differenza da notare:** corrente di bias a V_IN+ = 0 V: **−6 µA tipica** (TI: circa 0,1 µA); con R12/R13 da 100 Ω produce circa 0,6 mV su entrambi gli ingressi (modo comune), mentre l'offset di corrente 0,05 µA tip. dà circa 5 µV differenziali (circa 1,7 mA equivalenti): trascurabile. Slew rate A2 4 V/µs (TI: 2 V/µs).
- **Soglia di lavoro 7 A (Confirmed, utente 2026-10-15):** il firmware spegne ENA oltre 7 A (dopo il blanking dello spunto) entro 200 ms. Effetti: K1 (limite 8 A) resta valido; R7 dissipa 0,15 W; uscita INA 1,05 V a 7 A (0,15 V/A); la risoluzione di 100 mA corrisponde a 15 mV. Senza calibrazione l'incertezza a 7 A è circa ±0,2–0,3 A (tolleranza shunt ±1 % + guadagno ±1 % + offset circa 50 mA + TCR): con calibrazione a zero e fondo scala scende sotto circa 0,1 A. **Soglia da impostare a 7,0 A calibrati, non a un valore nominale, per non scattare sullo spunto o lasciare passare più di 8 A.**
- **Opzionale (non fatto):** R7 da 5 mΩ (0,245 W a 7 A, 1,75 V di uscita a 7 A) migliora la risoluzione dell'offset a circa 30 mA, ma toglie margine di fondo scala ADC (circa 9,8 A a 2,45 V).

### A2 pistone — validazione del dimensionamento con **R7 = 5 mΩ**, soglia 7 A (2026-10-15)
- **Schematico riletto da EasyEDA:** connessioni invariate e corrette (linea +12 V = P2.1, K1.14, K1.22, collettore U4, catodo D8; GND_SW = drain Q2, K1.12, K1.24, anodo D8; R7 tra source e GND con IN+ sul source via R12 e IN− su GND via R13; rete `12V` rinominata `+12V`). **Due errori nuovi:** (1) R7 vale 5 mΩ ma il codice costruttore resta `LR2512-22R003F4` (3 mΩ): va `LR2512-22R005F4` (RALEC 5 mΩ ±1 %, 2 W, ±25 ppm/°C; stock solo da aggregatori, codice LCSC non trovato; C154671 è la versione ±5 % "J"); (2) **designatore C2 duplicato** (il filtro di uscita a (945,325) e un nuovo condensatore a (795,395)); il secondo non è collegato a nessun filo (probabile disaccoppiamento di U3 su +5 V).
- **Validazione di R7 = 5 mΩ (calcoli miei su dati già registrati):**
  - Tensione 35 mV a 7 A; P = 0,245 W (12 % di 2 W); a 10 A in guasto 0,5 W (25 %).
  - Uscita INA 0,25 V/A: 1,75 V a 7 A; il fondo scala ADC di 2,45 V cade a 9,8 A; oltre, l'uscita sale fino a 4,5 V (limite lineare, 18 A) e D7 la limita; la soglia di 7 A (1,75 V) resta lontana dal limite ADC.
  - Errore a 7 A senza calibrazione, somma lineare del caso peggiore: tolleranza shunt 70 mA, guadagno INA 70 mA, offset 150 µV / 5 mΩ = 30 mA, deriva offset 7 mA, TCR 11 mA, deriva guadagno 5 mA = **±0,19 A** (con 3 mΩ erano ±0,22 A). **Anche senza calibrazione la lettura massima possibile a soglia 7,0 A è 7,19 A, sotto gli 8 A di K1.** Con calibrazione a zero e a 7 A resta circa 23 mA più l'errore dell'ADC.
  - Risoluzione: 100 mA = 25 mV in uscita (ADC LSB circa 0,6 mV): ok con media/oversampling. Filtro di uscita R11 1 kΩ + C2 100 nF: fc circa 1,6 kHz, nessun impatto sui 200 ms di rilevazione.
  - D7 (3,3 V): a 1,75 V di uscita la perdita dello Zener, non datata per il pezzo R+O, può dare fino a circa 10 mV (circa 40 mA): da misurare; alternativa Schottky verso 3V3.
- **Tenuta del ramo di potenza a 7 A:** K1 8 A (margine 14 %); Q2 clone VBsemi T_J circa 99 °C a 60 °C ambiente (0,78 W); R7 0,245 W; D8 e K1 come da validazione precedente. Fusibile esterno (decisione dell'utente): dimensionato ≥ 10 A ritardato per non scattare sullo spunto, ≤ 15 A (piste e connettore); piste e connettori per 7 A continui e 10 A di guasto.
- **Verdetto:** ramo di potenza e catena di misura **validati per soglia 7 A**. **Aperti:** pull-in della bobina di K1 con batteria a 10 V e +60 °C (margine nullo, K1 invariato per scelta dell'utente), MPN di R7, designatore C2 duplicato, prova in ingresso dei cloni, spunto del motore (blanking).

## Verifica estesa dello schematico (2026-10-15)

Sei `datasheet-verifier` sui componenti dello stadio pistone e dell'ingresso A1. **Limite comune:** gli agenti non hanno una shell e non hanno potuto leggere i PDF. Tutti i dati sotto vengono da pagine LCSC/JLCPCB o da riassunti (**fonti deboli**) e nessun valore è promosso a Confirmed. Unico datasheet letto direttamente: Toshiba TLP293 (`pdftotext`). Il PDF luJing BSS138 ha glifi codificati: cifre non leggibili.

### Codici LCSC e disponibilità (istantanea 2026-10-15)

| Rif. | Pezzo | LCSC | Stock | Note |
|---|---|---|---|---|
| R7 | RALEC LR2512-22R005F4 (5 mΩ ±1 %, 2 W, ±25 ppm/°C) | **C108931** | 26.510 | MOQ 5. C154671 (±5 %) resta scartato; alternativa 3 W: C154688 |
| Q2 | VBsemi `IPD50N06S4L12ATMA2-VB` | **C45662394** | **10** | Il P/N `IPD50N06S4L-12-VB` non esiste su LCSC. Rischio approvvigionamento alto |
| U3 | LX INA180A2IDBVR(LX) | C48533471 | 41.230 | MOQ 5 |
| D6 | R+O BZT52C12S (SOD-323) | C19077447 | 1,02 M | MOQ 50 |
| D7 | R+O: esiste BZT52C3V3S (SOD-323, C19077437) e BZT52C3V3 (SOD-123, C19077396, 350 mW) | C19077396 | 714 k | Verificare quale è nello schematico |
| D5 | SMAJ33A: nessun luJing trovato; R+O C41376399 | C41376399 | 6.940 | Verificare produttore/codice nel BOM |
| D8 | SS56: nessun R+O in SMA; R+O ha SS56F in SMAF (C41411775, 5 A, 850 mV a 5 A, Tj 125 °C) | – | 15.940 | **Punto più critico**: verificare codice reale |
| K1 | TE RTE24012 | C1524518 | 2.747 | Pagina TE: "Active" ma "not currently available" |
| Q1 | luJing BSS138 | C53058666 | 1.400 | MOQ 20 |
| R | UNI-ROYAL 1 kΩ / 47 kΩ / 100 Ω | C17513 / C17713 / C17408 | ampio | MOQ 100 |
| R | FOJAN FRC0805F1202TS 12 kΩ | C2907225 | 836 k | FRC0805J822 TS (8,2 kΩ) **non trovato** in 0805 (solo 0603 C2907205); Sekorm attribuisce la serie a FOSAN |
| C | Yageo 10 nF / 100 nF | C83170 / C49678 | ampio | Per C49678 copie in cache segnano "discontinued": ricontrollare |
| D2/D4 | Hangyu BZT52C3V3 | C54930248 | 1.750 | MOQ 50, 350 mW |
| D1/D3 | DOWO 1N4148WS | C22374708 | 22.550 | MOQ 50 |
| P1/P2 | JILN JL500-50802G01 | C709041 | 4.940 | MOQ 5 |
| CN1 | MAX MX128-5.0-04P | C5290369 | 3.175 | MOQ 5 |

### Esiti per gruppo

- **TLP293(GB) – datasheet Toshiba letto:** CTR ≥100 % a I_F = 0,5 mA e a 5 mA (25 °C, V_CE = 5 V); a 2 mA plausibile ma la curva non è letta. CTR saturo ≥30 % (I_F = 1 mA, V_CE = 0,4 V). V_CE(sat) ≤0,3 V a I_C = 0,2 mA / I_F = 1 mA. Tempi solo con R_L = 100 Ω (t_r 2 µs) e 1,9 kΩ. Nessun dato a 60 °C nel testo (solo figure). **Carica gate Q2 (70 nC):** I_F ≈ 2 mA → ≥35 µs nel caso migliore contro obiettivo 40 µs: **margine nullo, non confermabile** (a 60 °C/fine vita probabilmente perso). Open: misura o simulazione col CTR di caso peggiore.
- **BSS138 luJing (Q1):** R_DS(on) a 3,3 V non documentata. Margine richiesto per bobina K1 a 10 V (≥9,6 V): R_DS ≤ ~13,5 Ω a −10 °C, ~17 Ω a 60 °C. Dato più vicino (ON/Fairchild, non luJing): 6 Ω max a 4,5 V. **Non verificabile**: serve curva dal PDF o misura su campione. Si somma al margine nullo di pull-in già aperto.
- **Stadio pistone, diodi (R+O):** nessun datasheet letto. D8: il 5 A in SMA non è verificato per R+O (SS56F ha Tj 125 °C); I_R a caldo e dissipazione a 10 A non calcolabili con dati verificati. D5: V_F a bassa corrente di un TVS non caratterizzato nei listini. D6: P_D 200 mW, a 60 °C ≈144 mW (calcolo con R_θJA di terzi); picchi 12 mA×400 ms al limite. D7: I_R a 1,75–3 V non trovata; resta da misurare.
- **R7:** codice trovato (C108931); potenza a 70 °C, derating, sovraccarico e land pattern Kelvin non letti dal PDF RALEC. Il nome EasyEDA del MPN va ancora corretto in `LR2512-22R005F4`.
- **K1 pin-out:** 12 = NC, 14 = NO, 22 = NC, 24 = NO **non verificati** (disegno wiring TE in immagine). Se scambiati, il verso a riposo del pistone si inverte. Da controllare a mano sul PDF TE RT2 contro il footprint.
- **Connettori:** P1/P2 sezione max catalogo 2 mm² (cavo previsto fino a 2,5 mm² non entra); 15 A senza condizioni. Footprint `JL500-50002G01` nel nome = codice del pezzo da 5,00 mm, pezzo scelto 5,08 mm: verificare le quote dei pad. CN1 sezione min catalogo 1 mm² (cavo 0,5 mm²: serve puntale o 1 mm²); 10 A senza condizioni. Foratura e pin 1 non verificati.
- **Passivi:** potenza 0805 1/8 W a 70 °C (riassunti). **R1/R3 8,2 kΩ:** il load dump (101 V, 400 ms) dà 1,13–1,22 W; i 2,7 W del registro (riga 39) sono l'impulso ISO 1 da 2 ms, non il load dump (nessuna discrepanza, correzione 2026-10-15). Resta 9–22× la potenza nominale e non esiste curva d'impulso per la serie: il rischio accettato (REQ-EL-008) resta tale. Perdita DC bias e invecchiamento X7R di C1–C3 non verificati.
- **Diodi A1:** Hangyu BZT52C3V3 (350 mW, 5 µA a 1 V, V_F e I_FSM non trovati) e DOWO 1N4148WS (V_F ≈1,0 V a 50 mA, I_FSM 2 A, Tj discordante 150/175 °C): solo listini. Uso ben sotto i limiti nominali, ma dati senza seconda fonte.

### Azioni aperte per l'utente
1. Controllare nel BOM EasyEDA i codici reali di D5, D7, D8, Q2, R1/R3 (vedi tabella).
2. Aprire a mano i PDF (R+O C19077447/C19077396/C41376399/C41411775, RALEC C108931, TE RT2, luJing C53058666) o fornirli per la lettura con `pdftotext`.
3. Verificare pin-out K1 e quote pad P1/P2.
4. Decidere su cavo P1/P2 (≤2 mm²) e CN1 (puntale).

## Validazione del dimensionamento sui valori nominali (2026-10-15)

**Base:** netlist e valori dell'ultima lettura live (R7 5 mΩ, C2/C3 corretti, D8 corretto), più l'ispezione del backup `caravantic_2026-10-15-00-35.epro2` (precedente alle ultime correzioni). **EasyEDA non era connesso**: non è stato possibile rileggere lo schematico live. Dati dei componenti da datasheet già letti o da fonti deboli dichiarate sopra. Condizioni: V_linea 10–14,4 V (nominale 12 V), −10…+60 °C, soglia di lavoro 7,0 A (Confirmed), stallo 10 A solo come guasto (Assumed).

### Stadio pistone — verifica nominale

| Blocco | Calcolo nominale | Limite | Utilizzo | Esito |
|---|---|---|---|---|
| Bobina K1 (360 Ω) | 12 V → 33 mA, 0,40 W; 10 V → 27,8 mA | BSS138 I_D 220 mA | 15 % | OK. **Margine di pull-in a 10 V/60 °C nullo (già aperto)**, R_DS(on) di Q1 a 3,3 V non documentata (ammessi 13–17 Ω) |
| Ricircolo bobina D5 | conduzione diretta, circa 0,8 V sopra +12 V; lato drain Q1 nel transitorio: 12 V + V_BR 36,7–40,6 V ≈ 49–53 V | V_DS Q1 50 V | **~100 %** | Solo nei transitori sul rail (load dump a monte): margine nullo, da gestire con la protezione d'ingresso del rail |
| LED U4 (R9 1 kΩ) | I_F = (3,3 − 1,25)/1 kΩ = 2,05 mA, P(R9) 4 mW | GPIO ESP32-S3 | <10 % | OK |
| Gate Q2 a V_linea = 12 V | V_G ≈ 11,5 V (R8 47 kΩ, V_CE(sat) ≈ 0,2 V) | V_GS max ±16 V (Infineon) | 72 % | OK |
| Gate Q2 a V_linea = 14,4 V | Zener D6 limita a 11,4–12,7 V; corrente nello Zener limitata da R10 a (14,4 − 12 − V_CE)/1 kΩ ≈ 2 mA → 25 mW | P_D 144 mW a 60 °C | 17 % | OK (R10 protegge D6 anche con CTR 600 %) |
| Gate Q2 a V_linea = 10 V | V_G ≈ 9,5 V | R_DS(on) specificata a 10 V; a 4,5 V circa 17 mΩ | – | OK |
| Carica gate (70 nC) | I_C = CTR × I_F: CTR min 100 % → 2 mA → 35 µs; CTR tipico 200–300 % → 12–17 µs | nessun requisito di tempo imposto dal carico (perdita di commutazione a 7 A < 2 mJ) | – | OK. **Il vincolo "40 µs" usato prima non è un requisito**: va tolto; 35 µs al caso peggiore sono accettabili |
| Q2 conduzione | R_DS(on) max 12 mΩ a 25 °C, ×1,5 a ~100 °C = 18 mΩ: 7 A → 0,88 W; 10 A (≤200 ms) → 1,8 W | T_j 175 °C; R_θJA TO-252 su rame minimo assunta 50–60 K/W (**Assumed**, non letta) | T_j ≈ 105–115 °C a 60 °C ambiente | OK con il rame del PCB; verificare R_θJA sul datasheet VBsemi |
| Q2 sovratensione | picco di spegnimento clampato da D8 a ≈ 12 V + V_F(D8) ≈ 13–15 V | V_DS 60 V | 25 % | OK |
| Shunt R7 5 mΩ | 7 A → 35 mV, 0,245 W; 10 A → 50 mV, 0,50 W | 2 W a 70 °C | 12 % / 25 % | OK (derating RALEC non letto) |
| U3 INA180A2 (G = 50) | 7 A → 1,75 V; 10 A → 2,5 V; 0 A → ≤5 mV | V_S 5 V; ADC lineare fino a ~2,45 V | 7 A: 71 % del fondo scala ADC | OK. A 10 A (guasto) l'uscita satura l'ADC: la soglia 7 A deve scattare prima |
| Filtro R12/R13 + C1 | f(−3 dB) differenziale 1/(2π·200 Ω·10 nF) ≈ 80 kHz; bias −6 µA × 100 Ω = 0,6 mV in modo comune | – | – | OK |
| R11 1 kΩ + C2 100 nF + D7 | f(−3 dB) ≈ 1,6 kHz; sovratensione: (5 − 3,3 V)/1 kΩ = 1,7 mA → 5,6 mW nello Zener | P_D D7 350 mW | 2 % | OK. Perdita di D7 vicino a 2,4 V da misurare (errore: 20 µA × 1 kΩ = 20 mV ≈ 0,08 A al caso peggiore) |
| Contatti K1 | 7 A continui | 8 A (carico motore, RT2) | 88 % | OK. Contatti non devono mai commutare sotto carico (sequenza SW ENA off → 20 ms → DIR → 20 ms → ENA on) |
| Morsetti P1/P2 | 7 A / 10 A guasto | 15 A (catalogo, senza condizioni) | 47 % / 67 % | OK numericamente; sezione cavo max 2 mm² |
| Fusibile esterno | stallo 10 A ≤200 ms, regime 7 A, contatti K1 8 A | – | – | **Open:** valore non definito. Un fusibile da 10 A non protegge i contatti K1 (8 A) da uno stallo prolungato; indicazione: 7,5–8 A ritardato (da confermare con inrush misurato) |

### Ingressi A1 (R1–R4, D1–D4, U1–U2) — verifica nominale
- IN_CAB a 15 V: I_LED = (15 − 3,3 V_Z − 1,2 V_F)/8,2 kΩ ≈ 1,3 mA; a 12 V ≈ 0,9 mA. P(R1) 14 mW (11 %), P(D2) 4 mW. Coerente con la simulazione (`hardware/sim/a1_ingressi/`) e con l'assorbimento di circa 1 mA accettato.
- Uscita: R2 12 kΩ a 3,3 V → 0,275 mA; CTR saturo GB ≥30 % a I_F = 1 mA → 0,3 mA a 15 V (margine ~9 %), a 12 V (0,9 mA) 0,27 mA: opto al limite della saturazione ma V_OL resta sotto la soglia bassa ESP32 (0,8 V): OK sul nominale, margine ridotto.
- Sollecitazioni di impulso: vedi riga 39 (load dump 1,13 W, ISO 1 2,7 W) — rischio accettato REQ-EL-008, nessun dato d'impulso del costruttore.

### Esito della validazione
- **Dimensionamento nominale: valido** per tutti i blocchi di potenza e di misura dello stadio pistone a 7 A (utilizzi massimi: Q2 e K1 sul 7 A, ADC 71 %).
- **Tolto un vincolo errato** (carica gate in 40 µs): non è un requisito.
- **Punti non chiusi (non nominali):** pull-in K1 a 10 V/60 °C, R_DS(on) Q1 a 3,3 V, picco di D5 vs V_DS Q1 nei transitori, fusibile, R_θJA Q2, derating R7.
- **Schematico:** riletto live il 2026-10-15 (vedi sotto, 34 elementi, nessuna incoerenza di collegamento). Residuo da fare nell'editor (R7 è già corretto): MPN di R7 → `LR2512-22R005F4` (LCSC C108931); Q2 `IPD50N06S4L-12-VB` non esiste su LCSC con quel nome (reale: `IPD50N06S4L12ATMA2-VB`, C45662394, 10 pz); D5 nel backup ha codice C53058808, non verificato (l'agente ha trovato R+O C41376399); K1 pin-out 12/14/22/24 non verificato.

### Rilettura live dello schematico (2026-10-15)

Letto da `easyeda_schematic_snapshot` (34 elementi, un foglio, confidenza "partial": le net sono ricostruite dalla geometria dei fili, i pin risultano tutti toccati da un filo). **Nessuna incoerenza di collegamento.**

| Net | Pin |
|---|---|
| Rail +12 V (bobina) | D5.K, K1.A1 |
| Linea attuatore +12 V | P2.1, K1.14 (NO1), K1.22 (NC2), D8.K, U4.C (collettore) |
| GND_SW | Q2.D, D8.A, K1.12 (NC1), K1.24 (NO2) |
| Pistone | K1.11 → P1.1, K1.21 → P1.2 |
| Bobina | K1.A2, Q1.D, D5.A |
| Gate Q1 | Q1.G, R6.2, R5.2 (R6.1 = `OUT_LINEAR_MOTOR_DIR`; R5.1 e Q1.S a GND) |
| Gate Q2 | Q2.G, R10.2, R8.2, D6.K (U4.E → R10.1; R9.2 → U4.A, R9.1 = `OUT_LINEAR_MOTOR_ENA`, U4.K a GND) |
| Source Q2 | Q2.S, R7.2, R8.1, D6.A, R12.1 |
| Massa shunt | R7.1, R13.1, U3.GND, C2.1, D7.A, GND |
| Misura | R12.2, C1.2 → U3.IN+; R13.2, C1.1 → U3.IN−; U3.OUT → R11 → `IN_LINEAR_MOTOR_SENSE` con C2 e D7.K; U3.VS e C3 su +5V |

Verifiche: polarità di D5 (flyback), D6 (Zener gate-source, catodo sul gate), D7 (clamp positivo a GND), D8 (anodo GND_SW, catodo sulla linea +12 V) corrette; IN+ sul lato source dello shunt e IN− sul lato massa (segno corretto per corrente Q2→GND); C2 e C3 distinti e collegati; il rail della bobina e la linea attuatore sono due net separate (come da progetto: bobina dal rail di scheda, linea attuatore dal fusibile esterno).

MPN riletti: **R7 = `LR2512-22R005F4`** (corretto); K1 `RTE24012`; Q2 `IPD50N06S4L-12-VB` (non esiste su LCSC con questo nome: usare `IPD50N06S4L12ATMA2-VB`); D5 luJing `SMAJ33A` (nessun luJing trovato su LCSC, solo R+O C41376399: scegliere il codice nell'editor); D7 R+O `BZT52C3V3` (SOD-123, coerente con C19077396); D8 R+O `SS56` in SMA (nessun R+O SS56 in SMA trovato, esiste SS56F in SMAF); footprint P1/P2 nominato `...50002G01` (5,00 mm) per un pezzo da 5,08 mm.

Non verificabile da schematico: pin-out fisico di K1 (12 = NC, 14 = NO) e quote dei pad dei footprint.

## Stadio valvola (EL-003): interruttori high-side discreti — **Proposto** (2026-10-15)

Requisiti: REQ-EL-003 (pilotaggio valvola con misura di corrente, Confirmed), REQ-SW-002 (stato sicuro per sole reti passive). Scelta utente 2026-10-15: due interruttori high-side discreti (P-MOSFET + BSS138); op-amp di misura separati dal pistone (l'INA2180 doppio non viene usato).

**Topologia (Proposta).** Valvola U.S. Solid a 3 fili (nero −, rosso apre, blu chiude; **cablaggio interno da verificare col multimetro, OPEN-04**). Un P-MOSFET per filo (rosso e blu) dal +12 V; il nero torna a massa attraverso R-SH1 (18 mΩ, 1206) → un solo canale di misura per entrambi i versi, catena INA180A2 già dimensionata (sez. A2: 2,5 A → 45 mV → 2,25 V). Un Schottky da massa verso ciascun nodo di uscita per il ricircolo dell'induttanza (la corrente di ricircolo attraversa ancora lo shunt). Interblocco rosso/blu solo software (nessun corto fra alimentazioni, il caso "entrambi accesi" non danneggia ma si evita).

**Pilotaggio per canale (da definire in schematico):** GPIO → R 1 kΩ → gate BSS138 (47 kΩ gate–massa); drain BSS138 → R_dn 2,2 kΩ → gate P-FET; R_up 10 kΩ gate–source P-FET; Zener 12 V (come D6, BZT52C12S) gate–source P-FET. Stato sicuro: GPIO a zero → BSS138 spento → P-FET spento.

### Q_VLV (P-MOSFET) — Diodes **DMP4065S-7** (SOT-23): **Proposto**
- Scelta mia (2026-10-15): originale Diodes, 40 V, 80 mΩ max a −10 V. Riserva: ElecSuper DMP4065S-7(ES) (LCSC C49108755, 2.210 pz) o Winsok WST4041 (C148357): **cloni/equivalenti non verificati**; i parametri dei listini LCSC differiscono (3–5 A, 65–110 mΩ). Il Diodes originale **non risulta tra i codici LCSC trovati**: acquisto da Mouser/Digi-Key per il montaggio manuale (lead time ~8 settimane da distributore, fonte debole).
- **Dati letti sul datasheet Diodes DS37646 Rev. 3-2 (agosto 2021, `pdftotext`):** V_DSS −40 V; V_GSS ±20 V; R_DS(on) tip. 64 mΩ / max 80 mΩ a V_GS = −10 V, I_D = −4,2 A; tip. 85 / max 100 mΩ a −4,5 V, I_D = −3,3 A; V_GS(th) min −1,0 V, max −3,0 V (250 µA); I_D −2,4 A (25 °C) / −1,9 A (70 °C) su rame minimo, −3,4 / −2,7 A con 1 in²; I_DM −20 A; P_D 0,72 W (171 °C/W, rame minimo) o 1,4 W (90 °C/W, 1 in²); T_j −55…+150 °C; V_SD −0,7 V tip. a −1 A. Valori di commutazione e curva R_DS(on)–T non leggibili nel testo estratto.
- **Dimensionamento (nominale, 10–14,4 V, 60 °C ambiente):**

| Verifica | Calcolo | Limite | Esito |
|---|---|---|---|
| V_GS a 12 V (divisore 10 kΩ/2,2 kΩ) | −12 × 10/12,2 = −9,8 V | V_GS(th) max −3 V; R_DS(on) garantita a −10 V | OK |
| V_GS a 10 V / 14,4 V | −8,2 V / −11,8 V | ±20 V | OK (tipico di R_DS(on) tra i valori −4,5 V e −10 V) |
| Transitorio rail a 40 V a valvola accesa | senza Zener V_GS ≈ −33 V; con Zener 12 V la corrente nel divisore è (40 − 12)/2,2 kΩ ≈ 13 mA → 150 mW per pochi ms | ±20 V; Zener 200 mW (144 mW a 60 °C) | OK solo con Zener gate–source e solo per impulso breve |
| Marcia 0,5 A | R_DS(on) a caldo ≈ 1,5 × 80 mΩ = 120 mΩ → 30 mW, ΔT ≈ 5 K | 0,72 W (rame minimo) | OK |
| Picco/stallo 2 A (**Assumed**) | 0,48 W → ΔT ≈ 82 K (171 °C/W) → T_j ≈ 142 °C a 60 °C ambiente | 150 °C | Solo per tempi brevi (soglia di corrente firmware); con rame 1 in² ΔT ≈ 43 K |
| Corrente continua | 2 A vs I_D 1,9 A a 70 °C (rame minimo) | – | Non ammesso in continuo a 2 A: ammesso perché è un guasto/picco |
| Commutazione | carico induttivo lento (ms), gate pilotato da BSS138 tramite 2,2 kΩ | – | Nessun requisito di tempo |
| Perdita in spento | I_DSS max −1 µA a 25 °C | – | Trascurabile; con R_up/R_dn il gate resta a V_GS = 0 |

- **Rischi:** (1) R_DS(on) del BSS138 luJing a 3,3 V non documentata (già aperto): qui è meno critica perché il divisore ha margine, ma l'R_DS(on) di Q5/Q6 si somma a 2,2 kΩ; (2) cablaggio interno della valvola: se il lato spento può flottare verso +12 V serve un N-MOSFET di pull-down (mezzo ponte per lato); (3) stallo a 2 A mai oltre i tempi del firmware; (4) disponibilità dell'originale Diodes; (5) Schottky di ricircolo: stessa classe di D8 (decisione D8 aperta), ≥ 40 V, ≥ 3 A; (6) la risposta del `datasheet-verifier` su DMP4065S-7 è in corso: riportare l'esito qui sotto.

### Esito del verificatore su DMP4065S-7 (2026-10-15)
Il verificatore non ha letto il PDF (compresso): fonti deboli (Digi-Key, Farnell, riassunti). Confronto con la mia lettura diretta del datasheet DS37646 Rev. 3-2:
- **Concordano:** V_DSS −40 V, V_GSS ±20 V, R_DS(on) 80 mΩ max a −10 V (tip. 64), I_D −2,4/−1,9 A (rame minimo) e −3,4/−2,7 A (1 in²), P_D 0,72/1,4 W, 171/90 °C/W, I_DM −20 A, T_j 150 °C.
- **Che il verificatore non trovava e ho letto io:** V_GS(th) min −1,0 V, max −3,0 V; V_SD tip. −0,7 V, max −1,2 V (−1 A). SOA, Z_θJA transitoria e curva R_DS(on)–T restano **non letti**; il coefficiente a caldo ×1,5 usato è un'ipotesi.
- **Stallo 2 A a 60 °C su rame minimo:** il verificatore stima T_j ≈ 139 °C (×1,45), io 142 °C (×1,5): margine ~10 K, nessun derating; vale solo per stalli brevi. Conferma il rischio: Zener gate–source obbligatorio (−33 V di V_GS a 40 V senza), V_DSS −40 V senza margine contro transitori a ~40 V (ricircolo con Schottky, non con il body diode), V_GS −8,3 V a 10 V di rail non coperta dalla condizione di prova ma accettabile (100 mΩ max a −4,5 V).
- **Disponibilità (fonti deboli, 2026-10-15): problema.** Originale Diodes LCSC **C182476**: fuori stock, MOQ 5, ~$0,22 a 50 pz (i parametri LCSC sono quelli della colonna 1 in² — non usarli). Digi-Key: 0 pz, 3.000 attesi il 2026-12-28, lead time 32 settimane. Future: MOQ 3.000, 40 settimane. Mouser non verificato.
- **Riserve:** ElecSuper C49108755 (2.170 pz): 65 mΩ a 10 V, V_th 1,6 V — non equivalente verificato, riporta probabilmente un tipico. Winsok WST4041 C148357: **non equivalente** (V_th 2,2 V, I_D 6 A), polarità non confermata.
- **Azioni aperte:** (1) leggere i PDF delle riserve prima di sceglierne una; (2) decidere tra attendere l'originale e un clone (scelta utente, come per Q2/U3); (3) SOA e Z_θJA dal PDF Diodes.

### Decisione utente 2026-10-15: P-MOSFET valvola = HXY MOSFET `DMP4065S-7-HXY` (LCSC **C6285747**)
Sostituisce il Diodes originale (non disponibile) come P/N di acquisto per Q_VLV. Il Diodes DS37646 resta il riferimento di confronto. Stato: **scelta utente (Confirmed)**; i dati sotto sono del solo listino LCSC (**fonte debole**), il PDF non è stato letto (la richiesta di fetch restituisce solo il titolo).
- **Listino LCSC (2026-10-15):** SOT-23, P-ch, −40 V, −5 A, R_DS(on) < 85 mΩ a −10 V e < 120 mΩ a −4,5 V (il listino riporta anche 73 mΩ a 10 V), P_D 1,4 W, Q_g 14 nC a 10 V, C_oss 90 pF, T −55…+150 °C. V_GS(th) e C_iss non indicati. Stock 2.380 pz, MOQ 10, 0,046 USD a 100 pz.
- **Confronto con il Diodes originale:** R_DS(on) max −10 V: 85 contro 80 mΩ; −4,5 V: 120 contro 100 mΩ → con lo stesso calcolo (V_GS −9,8 V a 12 V) stallo 2 A a caldo ≈ 0,51 W contro 0,48 W (T_j ≈ +5 K, circa 147 °C su rame minimo, 171 °C/W **del Diodes**: R_θJA di HXY non nota): margine sotto 5 K sui 150 °C, solo per stalli brevi o con rame ≥1 in². Marcia 0,5 A: ≈ 0,03 W, invariata.
- **Non verificato:** V_GSS (assunto ±20 V), V_GS(th) min/max (a −8,2 V di V_GS il margine è comunque ampio), R_θJA, SOA, polarità e pinout SOT-23 (D–G–S del Diodes: verificare sul simbolo EasyEDA), body diode, qualità del lotto (clone: collaudo in ingresso come per Q2/U3).
- **Azioni:** leggere il datasheet HXY (PDF LCSC C6285747) con `pdftotext` appena disponibile; confermare V_GSS ±20 V (la Zener gate–source da 12 V resta obbligatoria); misurare V_GS(th) e R_DS(on) su un campione.

### Verifica circuitale della pagina 3 (stadio valvola), 2026-10-15
Rilettura live (`easyeda_schematic_snapshot`, 69 elementi totali, pagina 3: Q3, Q5, Q6, Q7, U5, CN2, R14–R16, R20–R28, C4–C6, D10, D11, D13; confidenza "partial", net ricostruite dalla geometria dei fili). Codici, MPN e disponibilità ignorati su richiesta. Designatori diversi dalla specifica `hardware/schematic/a2_valvola.md` (Q3/Q6 = BSS138, Q5/Q7 = P-MOSFET, R16 = shunt, CN2 = 3 poli): la specifica va riallineata.

**Corretto:**
- Pilotaggio: GPIO → 1 kΩ (R15/R26) → gate BSS138 con 47 kΩ a massa (R14/R25), source a GND; drain → 2,2 kΩ (R24/R28) → gate P-FET con 10 kΩ verso Vmot (R23/R27). Stato sicuro (GPIO a zero → tutto spento) rispettato.
- Misura: nero (CN2.3) → shunt R16 18 mΩ → GND; IN+ di U5 su CN2.3 via R21 100 Ω, IN− su GND via R22 100 Ω, C4 10 nF tra i due; U5.VS su +5V con C6; uscita → R20 1 kΩ → `IN_VALVE_SENSE` con C5 100 nF e D11 (3,3 V, catodo sul nodo, anodo a GND). Segno e filtri come nel pistone.
- Rosso/blu: Q5 → CN2.2, Q7 → CN2.1; nero CN2.3 (ordine pin: 1 blu, 2 rosso, 3 nero: da riportare in serigrafia).

**Errori (da correggere nell'editor):**
1. **Q5 e Q7 hanno source e drain invertiti.** Il drain (pin 3) è sulla linea Vmot e il source (pin 2) sul carico/CN2: il diodo di body (anodo drain, catodo source) conduce da Vmot al carico, quindi **le uscite rosso e blu sono sempre alimentate a circa Vmot − 0,7 V, qualunque sia il comando**; inoltre il pull-up R23/R27 su Vmot è sul drain e non sul source. Correzione: source (pin 2) su Vmot e sul pull-up, drain (pin 3) sul carico e sul D10/D13. **Critico.**
2. **D10 e D13 sono Zener BZT52C12S con catodo sull'uscita e anodo a GND.** Con il P-FET acceso l'uscita è a 12–14,4 V, oltre la tensione di Zener (11,4–12,7 V): lo Zener conduce in continuo, abbassa la tensione alla valvola e brucia (200 mW). In diretta si comporta da ricircolo ma con V_F di un diodo piccolo. Servono due **Schottky** (60 V, ≥ 3 A, catodo sul nodo di uscita, anodo a GND) per il ricircolo. **Critico.**
3. **Mancano gli Zener gate–source** (12 V, catodo sul source/Vmot, anodo sul gate) su Q5 e Q7: in nominale il circuito funziona (V_GS ≈ −9,8 V a 12 V), ma un transitorio del rail a 40 V a canale acceso porta V_GS a circa −33 V (limite ±20 V, V_GSS HXY non letto). **Medio** (protezione).

**Da decidere (non sono errori di collegamento):**
- **Alimentazione:** la pagina 3 usa `Vmot`, la linea attuatore della pagina 1 (P2.1, contatti di K1, D8.K, collettore di U4) e non il rail +12V della specifica: valvola e pistone condividono il fusibile esterno e la stessa linea; correnti massime sommate 7 A (pistone, soglia) + 2 A (valvola, picco) = 9 A. Il fusibile e P2 vanno dimensionati su questo.
- Lo shunt R16 ha ancora l'MPN da 5 mΩ nello schematico (ignorato qui).
- Cablaggio interno della valvola (lato spento) da misurare.

### Seconda verifica della pagina 3 (dopo le correzioni dell'utente), 2026-10-15
Rilettura live, 71 elementi. **Corretti:** Q5/Q7 (source su Vmot, drain su CN2.2/CN2.1, pull-up R23/R27 sul source); D9/D12 = SS56 Schottky di ricircolo con anodo a GND e catodo sul nodo di uscita (corretto). Resto della pagina invariato e corretto (pilotaggio BSS138, misura su R16 con R21/R22/C4, U5, R20/C5/D11).

**Errore residuo (critico): D10 e D13 (BZT52C12S) sono collegati fra gate e drain/uscita, non fra gate e source.** D10: catodo sul gate di Q5 (con R23.1/R24.2), anodo sul nodo di uscita CN2.2; D13 analogamente su Q7/CN2.1. A canale spento il gate è tirato a Vmot da R23 e l'uscita è a circa 0 V (valvola verso massa): gate−uscita = Vmot = 12–14,4 V supera la V_Z (11,4–12,7 V), lo Zener va in rottura e trascina il gate verso circa V_Z sopra l'uscita, cioè V_GS ≈ −(Vmot − V_Z): 0 V a 12 V, fino a −3 V a 14,4 V. Con V_GS(th) fino a −3 V (Diodes; HXY non letto) il P-FET può **accendersi parzialmente a canale comandato spento**. Correzione: D10 e D13 con **catodo sul source (Vmot) e anodo sul gate**, come nella specifica (Zener gate–source).

### Terza verifica della pagina 3 (2026-10-15): nessun errore circuitale residuo
Rilettura live (71 elementi, net ricostruite dalla geometria): D10 e D13 ora hanno catodo su Vmot (source di Q5/Q7) e anodo sul gate; Q5/Q7 con source su Vmot e drain sulle uscite CN2.2/CN2.1; D9/D12 (SS56) con anodo a GND e catodo sulle uscite; pilotaggio BSS138, misura R16/R21/R22/C4/U5 e uscita R20/C5/D11 invariati e corretti. Il circuito soddisfa la specifica di stato sicuro e il dimensionamento nominale della sezione "Stadio valvola".
**Residui non circuitali:** la linea è `Vmot` (condivisa con il pistone, fusibile esterno e P2 da dimensionare per 9 A sommati); MPN dello shunt R16 da correggere (ignorato su richiesta); cablaggio interno della valvola da misurare; `hardware/schematic/a2_valvola.md` ha designatori diversi dallo schematico (da riallineare).

### Verifica della pagina 3 dopo l'aggiunta dei LED (2026-10-15)
Rilettura live (80 elementi). Invariati e corretti: pilotaggio BSS138, P-FET Q5/Q7 con source su Vmot, Zener D10/D13 gate–source, Schottky D9/D12, misura R16/R21/R22/C4/U5 e uscita R20/C5/D11. **Cambio di pinout (non errore):** CN2.1 ora è il filo rosso (Q5, D9, LED2) e CN2.2 il filo blu (Q7, D12, LED1); aggiornare `hardware/schematic/a2_valvola.md` (nel file CN2 pin 1 = blu, pin 2 = rosso).

**Errore introdotto: i due LED (LED1 sull'uscita blu, LED2 sull'uscita rossa) hanno i catodi uniti su un'unica resistenza R17 (4,7 kΩ) verso GND.** A uscita rossa accesa il nodo comune dei catodi sale a circa Vmot − V_F ≈ 10 V (2 mA × 4,7 kΩ ≈ 9,9 V a 12 V): il LED dell'uscita spenta ha l'anodo a circa 0 V (nodo di uscita verso massa tramite motore e Schottky) e vede ≈ 10 V in inversa, oltre il limite tipico di 5 V per un LED 0805 (datasheet YLED0805G non letto). Rischio: rottura del LED e corrente inversa che attraversa il motore e lo shunt (falsa misura, possibile movimento della valvola). Correzione: una resistenza per ogni LED (stesso valore 4,7 kΩ), catodo di ciascun LED sul proprio R verso GND, nessun nodo comune.

## Ingressi AUX (EL-009): R29/R30, D14–D17, U6/U7, H1–H4 — **Proposto** (foglio letto il 2026-10-15)

Stessi componenti dei canali IN-CAB/IN-CEL (R 8,2 kΩ 0805, BZT52C3V3, 1N4148WS, TLP293 GB), più 2 jumper a saldare a 3 pad per canale, senza BOM. Mappa dei designatori e note in [`hardware/schematic/a1_ingressi.md`](../hardware/schematic/a1_ingressi.md), sezione "Designatori sul foglio EasyEDA".

| Canale | R | Zener | Antiparallelo | Opto | Jumper |
|---|---|---|---|---|---|
| IN-AUX1 (`IN3`) | R29 | D15 | D14 | U6 | H1, H2 |
| IN-AUX2 (`IN4`) | R30 | D17 | D16 | U7 | H3, H4 |

Verifica: lettura a mano dello schema, topologia coerente con REQ-EL-009 nei due modi. Nessuna simulazione del modo L; nessun dato nuovo da datasheet. Aperti: orientamento dello Zener sul simbolo, rail `+12V` dei jumper (deve essere il protetto), footprint a tre pad senza traccia di default, comportamento del TLP293 sotto 1 mA con la board a 10 V.

## Q1/Q2 (specchio di corrente del livello acque chiare, A4) — Diodes DMMT3906W (SOT-363) — **SUPERATO il 2026-10-17 dalla misura con INA219 (sezione seguente)**
- Requisito: REQ-IF-003. Stato: **Proposto**, scelta approvata dall'utente come topologia (specchio PNP) il 2026-10-17; il part number è la proposta del verificatore e mia.
- Datasheet letto direttamente (Diodes DS30312 Rev. 13-2, feb. 2018): coppia PNP intrinsecamente accoppiata, V_CEO −40 V, I_C −200 mA, P_D 200 mW totale, R_θJA 625 °C/W, matching 2 % (hFE) e 2 mV (V_BE) a 2 mA 1:1, hFE min 80 a 1 mA e 100 a 10 mA (V_CE 1 V), V_CE(sat) max 250 mV a 10 mA. Dettagli e conseguenze in `hardware/schematic/a4_serbatoio_chiare.md` ("Esito della verifica coppia PNP e GPIO").
- LCSC: DMMT3906WQ-7-F = C526574 (circa 525 pz, fonte debole: distributore). Il DMMT3906W-7-F senza Q non ha un codice LCSC trovato. Stessa parte per il datasheet (nota 5).
- Punti aperti: matching non garantito a 1,2/8 mA; modello SPICE del costruttore non disponibile in testo; ciclo di vita da confermare.
- Scartati: Nexperia BC857BS e BCV62 (non accoppiati nelle fonti viste; BCV62A esaurito su LCSC).
- D_f del livello usa il 1N4148WS già registrato sopra (V_R 75 V).

## U_LVL (misura del livello acque chiare, A4 v. 4) — Texas Instruments INA219BIDR (SOIC-8)
- Requisito: REQ-IF-003. Stato: **Proposto**, topologia approvata dall'utente il 2026-10-17 (riserva: INA219AIDR, grado A).
- Datasheet letto direttamente (TI SBOS448G, Rev. G, dic. 2015): alimentazione 3–5,5 V (assorbimento 0,7 mA tip., 1 mA max; power-down 6 µA tip., 15 µA max); ingressi IN+/IN− −0,3…26 V assoluti, differenziale ±26 V; fondo scala shunt ±40 mV (PGA /1), LSB 10 µV; tensione di bus 0–16 V (BRNG = 0), LSB 4 mV; offset shunt PGA /1 ±100 µV (A) / ±50 µV (B); errore di misura della corrente ±0,5 % (A) / ±0,3 % (B) a 25 °C e ±1 % / ±0,5 % su −25…85 °C; errore della tensione di bus ±0,5 % a 25 °C e ±1 % su −25…85 °C; bias di IN+ 20 µA e IN− 20 µA ‖ 320 kΩ (tipici); conversione 12 bit 532 µs, con 8 campioni 4,26 ms; 16 indirizzi.
- Dimensionamento e errore: `hardware/schematic/a4_serbatoio_chiare.md` sez. A, `hardware/sim/a4_livello/ina219_error.py` (calcolo sui limiti, non SPICE).
- LCSC (fonte debole, istantanea 2026-10-17): INA219BIDR C2155799, circa 100 pz, 2,6 USD (1 pz); INA219AIDR C138706, 1.255–4.409 pz (due pagine LCSC discordanti), una pagina riporta "not recommended for new designs", mentre gli aggregatori lo danno attivo: **ciclo di vita non confermato, da verificare sulla pagina TI**.
- Punti aperti: offset del bus (Fig. 5, non leggibile); bias massimo di IN−; indirizzo I²C 0x40 verificato senza conflitti con MPU-6050 (0x68/0x69) e HMC5883L (0x1E); scostamento dalla rete di clamp di campo (convenzione): accettato dall'utente il 2026-10-17.
- D_drv: 1N4148WS già registrato.
- **Rsh (R40) del livello acque chiare: Yageo RT0805BRD073R9L (LCSC C136923)**, scelto dall'utente il 2026-10-17. Pagina LCSC: 3,9 Ω ±0,1 %, ±25 ppm/°C, film sottile, 125 mW, 0805, 11.490 pz, 0,054 USD da 10 pz (fonte debole: distributore); ±25 ppm/°C su ±35 K ≈ ±0,09 % di deriva di Rsh. Sostituisce il FOJAN FRC0805F3R90TS (±1 %, ±200 ppm/°C). Datasheet del costruttore non letto.

---

Sezione A5 — misura dei due shunt energetici (IF-005): batteria servizi e secondo shunt, 200 A / 75 mV low-side, bipolari.

## U_SH (ADC dei due shunt) — Texas Instruments ADS1115IDGSR (VSSOP-10)
- Requisito: REQ-IF-005 (Confirmed). Stato: **Proposto**, scelta approvata dall'utente il 2026-10-17 (ADC esterno ADS1115). Dimensionamento in [`hardware/schematic/a5_shunt_energia.md`](../hardware/schematic/a5_shunt_energia.md).
- Verifica `datasheet-verifier` del 2026-10-17 su TI SBAS444E (dic. 2024), letta dalla versione HTML (il PDF non era leggibile); **mono-fonte (TI)**, nessuna seconda fonte indipendente ottenuta.
- Parametri decisivi (fonte: SBAS444E §5.1, §5.5, §6.1):
  - 16 bit, FSR ±0,256 V → 1 LSB = 7,8125 µV; alimentazione 2,0–5,5 V; T −40…+125 °C; 8…860 SPS; I²C 0x48–0x4B da ADDR.
  - Ingressi: assoluto massimo GND−0,3 V … VDD+0,3 V; corrente continua ±10 mA per pin; diodi ESD verso VDD e GND.
  - Z differenziale 710 kΩ (typ) a ±0,256 V; Z di modo comune 100 MΩ.
  - Offset e guadagno **specificati solo a ±2,048 V**: offset ±3 LSB max (=±187,5 µV), guadagno 0,15 % max a 25 °C. A ±0,256 V c'è solo la deriva di guadagno 7 ppm/°C (typ). CMRR 105 dB (typ). Rumore 7,81 µVrms (1 LSB) a 8 e 64 SPS.
- ⚠️ **Il datasheet dice che gli ADS111x accettano tensioni positive rispetto a GND** (§9.2, esempio shunt con OPA333 e traslatore a VCM). Un ingresso a −75 mV è nell'assoluto massimo ma fuori dal funzionamento garantito: serve un offset positivo sugli ingressi (vedi A5).
- LCSC (fonte debole, istantanea 2026-10-17): **C37593**, VSSOP-10, circa 10.000 pz; footprint EasyEDA non verificato. Ciclo di vita: Active.
- Non verificato: testo di §7.3.2 / §9.2.2.3 / Tab. 5.3 (intervallo di modo comune in lineare), latenza dopo cambio di MUX (§7.3.6), trattamento di ALERT/RDY non usato. ESPHome `ads1115` supporta A0_A1 / A2_A3 e gain 0,256 (fonte secondaria).
- Alternative scartate: ADC interno ESP32-S3 (37,5 µV per 0,1 A, unipolare); INA226/INA219 (modo comune ≥ 0 V, qui un ingresso va sotto massa).

## D_CL (clamp degli ingressi shunt, A5) — Nexperia BAV199,215 (SOT-23, doppio diodo in serie)
- Requisiti: REQ-IF-005; convenzione "resistore serie + clamp verso 3,3 V e massa". Stato: **Proposto**, verifica `datasheet-verifier` del 2026-10-17.
- Fonte: **datasheet Nexperia non letto** (403); numeri da Diodes DS30232 Rev. 11-2 e onsemi BAV199L Rev. 13 (letti direttamente): I_R max 5 nA a 75 V / 25 °C, 80 nA a 150 °C; 60 °C solo tipico da grafico (≈ 1,1 nA); nessun matching fra i due diodi; capacità ≈ 2 pF a 0 V; pinout: 1 anodo D1, 2 catodo D2, 3 comune.
- LCSC (debole): C40919, circa 126.000 pz (altra fonte: 31.200); C549304 (bobina da 10.000) con stato discordante. Un BAV199 Diodes risulta discontinuato (da una ricerca, non verificato).
- Budget di perdita: vedi `hardware/schematic/a5_shunt_energia.md`. Rischio: perdita non garantita a 3 V / 60 °C.

## R_S, R_B, C_DIFF, C_CM (rete di ingresso, A5) — rev. 2026-10-18: R_S 10 kΩ / R_B 150 kΩ
- Requisiti: REQ-IF-005. Stato: **Proposto**; scelta dell'utente del 2026-10-17 (R_S 10 kΩ, R_B in proporzione, C_DIFF 33 nF, C_CM 3,3 nF); R_B = 150 kΩ perché il 143 kΩ non è in stock su LCSC. Sostituisce la prima versione (3,3 kΩ / 47 kΩ / 100 nF / 10 nF), confronto in `hardware/schematic/a5_shunt_energia.md`.
- R_S = Yageo RT0805BRD0710KL (10 kΩ ±0,1 % ±25 ppm/°C, 1/8 W, 150 V; LCSC **C110775**, circa 672.000 pz). R_B = Yageo RT0805BRD07150KL (150 kΩ, stessi parametri; LCSC **C136927**, circa 57.000 pz). Serie RT: datasheet Yageo RT V.17 letto direttamente dal verificatore (2026-10-17); stock LCSC dalla ricerca nel browser del 2026-10-18 (fonte debole).
- C_DIFF = Yageo CC0805JRX7R8BB333 (33 nF X7R 25 V ±5 %; LCSC **C520038**, circa 2.500 pz, poco stock). C_CM = Murata GRM2165C1H332JA01D (3,3 nF C0G 50 V ±5 %; LCSC **C77062**, circa 44.800 pz). Datasheet di entrambi non letti: solo dati dalle pagine LCSC. C_CM ±5 % (le ±1 % sono a stock 0) peggiora la reiezione di modo comune rispetto alla simulazione, vedi A5.
- Simulazione ngspice (modelli generici): `hardware/sim/a5_shunt/`.
## K_TAKE, K_LVL (remote inverter, IF-007) — TE Axicom IM06 (IM06GR SMD, LCSC C2153106) — **SUPERATA 2026-10-18** (sul foglio: G6K-2F-Y-TR, K2/K3; IM06 = riserva) — era Proposto con riserva (verifica `datasheet-verifier` del 2026-10-18)

- Requisito: REQ-IF-007. Uso: scambio su VIN e livello +12 V, mA a 12 V. Dettagli in [`hardware/schematic/a6_remote_inverter.md`](../hardware/schematic/a6_remote_inverter.md).
- **Verifica del 2026-10-18 (secondo giro, PDF letto):** datasheet TE "108-98001 Rev. M" (09-2017) letto da Mouser, ma ogni pagina è marcata SUPERSEDED: esiste una revisione più recente non letta. Confermati dal PDF: pick-up **9,00 V** e release 1,20 V a +23 °C; tempi 3 ms operate, 5 ms release con diodo, rimbalzo 5 ms; contatti 2 A, 100 µV minimi, PdRu+Au; isolamento 1800 Vrms bobina-contatti; monostabile (il bistabile è IM46); Active su TE; LCSC C2153106 4064 pz.
- **Non verificabili dal testo del PDF:** pick-up e U_max a temperatura (solo curva "Coil operating range"), comportamento a polarità inversa (pin + = 1, − = 8 dal disegno), carico a pochi mA a 12 V (nessuna tabella intermedia). Discrepanza fra due fonti TE: contatti aperti 1000 Vrms (F1) contro 750 Vrms (stampa 2021). Da leggere la curva sul PDF a mano prima di promuovere.
- Confermato (TE + Digi-Key): bobina 12 V, 1029 Ω, 140 mW, polarizzata monostabile; contatti 2 A, PdRu dorati (LCSC dice AgNi: scheda LCSC non affidabile); isolamento bobina-contatti 1800 Vrms; operate/release ≤ 3 ms (con diodo release fino a 5 ms), rimbalzo ≤ 5 ms.
- **Rischio principale:** must operate **9,0 V a 25 °C** (Digi-Key; Findchips dice 8,4 V). A 10 V (minimo di esercizio) il margine è ~11 % a 25 °C; a 70–85 °C la stima (mia, non da datasheet) porta il pick-up a ~10,6–11,2 V ⇒ **può non chiudere**. Contraddice quanto scritto in rev. 1 ("finestra 10–16 V chiude"). Anche la tensione continua massima di bobina (14,6 V = 148 %, 16 V = 178 %) è non verificata.
- Disponibilità: IM06GR 4064 pz su LCSC (2,96 $), TE "not currently available", lead time lunghi; IM06TS THT 5 pz su LCSC. Footprint EasyEDA non verificato.
- Alternative (dati non verificati): Omron G6K-2F-Y DC12 (C397192), G6K-2G-Y DC12 (C1525300): pick-up max 9,6 V da Arrow (fonte debole), non migliore dell'IM06. Quasi tutti i DPDT 12 V chiudono al 70–80 % di U_nom: il vincolo vero è il rail minimo a 10 V a caldo.
- Nota: la scelta a 3 relè (K_TAKE, K_LVL, K_LED) triplica l'esposizione a questo rischio.

## Q_LEDG, Q_LEDR (specchio LED al remote, IF-007) — Diodes BSS84-7-F (SOT-23, LCSC C85202) — **SUPERATA 2026-10-18** (Q9/Q10 = BSS84K HJC C54795811, vedi in fondo) — era Proposto con riserva (verifica `datasheet-verifier` del 2026-10-18)

- Requisito: REQ-IF-007. Uso: P-MOSFET high-side, source a +3V3, gate sul nodo `SIG_INVERTER_GREEN/RED` (pull-up 12 kΩ, basso = ON), drain → R serie → pin 4/7 del remote (LED con 1 kΩ interno, ~1,3 mA). Scartato il DMP4065S della valvola: V_GS(th) max −3 V ≈ il V_GS disponibile (−3,0…−3,2 V).
- **Limite della verifica:** letto solo il datasheet **onsemi** BSS84 (senza revisione); i PDF Diodes e Nexperia non erano leggibili. Il BOM deve riportare C85202 (Diodes) e il PDF Diodes va letto prima di fissare.
- Dati (onsemi, 25 °C): V_DSS −50 V, V_GSS ±20 V, I_D −0,13 A; **V_GS(th) 0,8 / 1,7 / 2,0 V (min/typ/max) a 1 mA**, ΔV_th 3 mV/°C (a −20 °C stima mia ≈ 2,14 V max); R_DS(on) max 10 Ω a −5 V, **nessun valore a −3 V**; I_DSS max 15 µA; I_GSS ±10 nA; diodo drain-source V_SD max 1,2 V.
- **Rischi:** (1) margine di pilotaggio < 1 V (V_GS ≈ −2,84 V a rail 3,135 V e livello basso 0,3 V; stima R_on ≈ 100–120 Ω ⇒ perdita ≈ 0,2 mA sul LED, **stima a legge quadratica**, Fig. 5 non letta): da simulare o misurare a −20 °C; (2) il body diode conduce se il drain supera il source di ~0,8 V: ESD/tensione sul cavo può retro-alimentare il 3V3 ⇒ serve R serie + clamp sul pin; (3) cloni con parametri diversi (HUASHUO 60 V/6 Ω a 10 V): BOM solo C85202 o Nexperia C493579; (4) pinout (convenzione 1 = G, 2 = S, 3 = D) non verificato; (5) stato del ciclo di vita Diodes non confermato.
- Alternative a soglia più bassa (DMG2305UX, DMP2305U, AO3401A): V_DS solo −20/−30 V e V_GS ±8 V per le prime due; non adatte con il cavo esposto senza protezione. Dati secondari, non verificati.

- **Simulazione del 2026-10-18** (`hardware/sim/a6_led/bss84_led.py`, modello a legge quadratica da g_fs min, **non SPICE del costruttore**; V_f LED 1,9–2,1 V ipotizzata): a rail 3,135 V, livello basso 0,1–0,5 V, V_th 1,7–2,14 V, corrente nel LED con R serie 0 Ω: 0,87–1,16 mA contro 1,03–1,24 mA ideali (senza MOSFET): perdita 0,05–0,15 mA. Con R serie 220/470 Ω: 0,74–0,96 / 0,63–0,81 mA. Con V_th = 2,3 V e gate a 0,5 V la corrente scende a 0,57–0,70 mA. Non include dispersione di β né caso freddo reale.

## K2, K3 (remote inverter, IF-007) — Omron **G6K-2F-Y-TR DC12** (SMD, LCSC/JLCPCB C397192) — **Proposto** (2026-10-18; **sostituisce l'IM06 come prima scelta**, IM06 resta riserva). Ex K_TAKE_A/K_TAKE_B/K_LVL: sul foglio i relè sono due

- Requisito: REQ-IF-007. Stesso part number per i due relè (un solo footprint e un solo stadio di pilotaggio: BSS138 Q4/Q8, GPIO → 1 kΩ → gate, pull-down 47 kΩ; la TVS di bobina sul foglio è SMAJ33A (D19/D22), non 1N4148WS, in verifica). **K2 (`CMD_INVERTER_CTRL`): chi controlla l'inverter, NC = remote, eccitato = board. K3 (`CMD_INVERTER_STATE`): stato comandato dalla board, NC = inverter spento, eccitato = acceso (effetto solo con K2 eccitato).** Entrambi commutano **solo VIN / +12 V**; i LED (pin 4/7) non passano dai relè (specchio Q9/Q10, chiuso con l'utente 2026-10-18). Resta da rileggere a quale nodo va il polo NO di K3. Sostituisce la ripartizione precedente a 3 relè (K_TAKE_A VIN + pin 4, K_TAKE_B pin 7, K_LVL +12 V). Spec in [`hardware/schematic/a6_remote_inverter.md`](../hardware/schematic/a6_remote_inverter.md).
- Scelto perché è miniaturizzato: **10 × 6,5 × 5,2 mm**, 0,7 g, DPDT, monostabile non polarizzato, versione "Highly insulated".
- Dati letti **direttamente** dal datasheet Omron G6K ([en-g6k.pdf](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf), testo estratto con pypdf; tabelle Coil/Characteristics/Contacts): bobina 12 V, **1315 Ω ±10 %, 9,1 mA, circa 100 mW (110 mW a 12 V)**; **must operate ≤ 80 % = 9,6 V; must release ≥ 10 % = 1,2 V** (a 23 °C di temperatura bobina); tensione massima 150 % (istantanea); operate/release ≤ 3 ms; contatti Ag con lega Au, bifilari, 1 A a 30 VDC (max 60 VDC, 1 A), carry 2 A; **P-level 10 µA a 10 mVDC** (adatto a segnali di pochi mA); isolamento bobina-contatti 1500 VAC, contatti adiacenti 1000 VAC, stessi contatti 750 VAC; temperatura −40…+70 °C. Coerente con Arrow/element14/JLCPCB (fonti deboli: 1,315 kΩ, 9,6 V, 1,2 V, 3 ms, Au).
- **Rischio principale: il pick-up peggiora in temperatura e a 12 V di bobina il margine dipende dalla tensione minima di esercizio (EL-001, ancora da fissare).** Margine (Vmin − pick-up)/pick-up, con pick-up a temperatura = 9,6 V × (1 + 0,0039·ΔT) (**stima mia** sulla resistenza del rame, non da datasheet):
  | Vmin | 23 °C | 50 °C | 70 °C |
  |---|---|---|---|
  | 11 V | +15 % | +4 % | −3 % |
  | 12 V | +25 % | +13 % | +5 % |
  Il pick-up in temperatura è peggiore dell'IM06 (9,0 V a 25 °C, verifica 2026-10-18). **Con Vmin = 12 V (EL-001, deciso il 2026-10-18) il margine minimo è +5 % a 70 °C, +13 % a 50 °C, +25 % a 23 °C**: accettato in assenza di condizioni peggiori; a 11 V il G6K non sarebbe garantito a 70 °C.
- Non letti: grafico "Ambient temperature vs maximum coil voltage" (solo immagine nel PDF), rimbalzo dei contatti, resistenza di contatto dopo vita; footprint EasyEDA non verificato. Libreria JLCPCB: **Extended** (costo di setup per parte); stock e prezzo non letti.
- Alternative: IM06GR (vedi voce sopra, pick-up 9,0 V, disponibilità incerta); bobina 4,5 V o 3 V del G6K da rail regolato (pick-up 3,6 V / 2,4 V, margine migliore ma bobina oltre il nominale: serve il grafico della tensione massima); latching G6KU scartato (a board spenta resterebbe in presa in carico, viola IF-007 d); reed relay SIP/SMD scartati (500 mA, ingombro, nessun vantaggio per milliampere).
- **Disponibilità e prezzi LCSC (letti il 2026-10-18, fonte rivenditore = debole):** C397192 G6K-2F-Y-TR DC12 — **20 230 pz**, bobina da 900; 1,13 $ (1 pz), 0,79 $ (100), 0,71 $ (900). Equivalente **C397194 G6K-2F-Y DC12** (senza -TR) — **28 810 pz**, 1,18 $ (1), 0,77 $ (100), 0,69 $ (900): stesso modello, pezzo marginalmente più economico a volume. La pagina C397194 dà −40…+85 °C e 1,4 ms, in disaccordo col datasheet Omron letto (70 °C, 3 ms): vale il datasheet. Non-Y G6K-2F DC12 (C397197): 42 pz a 7,72 $, da scartare. G6K-2G-Y (C1525300): altezza 5,4 mm, terminali diversi. Libreria JLCPCB di C397192: Extended. Nessun clone più economico pin-compatibile trovato su LCSC (la ricerca ha restituito solo Omron). Costo dei tre relè ≈ 3,4 $ a 1 scheda, ≈ 2,3 $ a 100.
- **Risparmio possibile (da valutare, non deciso):** sostituire K_LVL (solo forzatura del livello su VIN) con un TLP293-GB (già in distinta, ~0,09–0,17 $) se la misura di OPEN-02 mostra che VIN assorbe ≲ 1 mA: risparmia ~1 $ e un relè.


- **Verifica "BSS84K" del 2026-10-18: esito negativo, nessun dato numerico verificato.** Un "Nexperia BSS84K" **non risulta esistere** (la famiglia ESD di Nexperia è **BSS84AK**, 50 V, 180 mA, ESD fino a 1 kV: pagina prodotto, indiretto; i siti Nexperia davano 403, nessun datasheet letto). Su LCSC "BSS84K" è un altro componente a seconda del produttore: **MDD C53463905** (60 V, 200 mA, V_th 1,6 V, R_DS(on) 3,7 Ω a 10 V, ESD 2 kV, 113 k pz) e **MCC BSS84K-TP C2987028** (60 V, 130 mA, V_th 2,5 V, 7 Ω a 4,5 V, 780 pz): dati di distributore, incompatibili fra loro. Con V_th 2,5 V il pilotaggio a −3,1 V lascia ~0,6 V di overdrive: **non adatto senza datasheet**. Il mio riferimento al "BSS84K Nexperia con ESD" era un'assunzione sbagliata. Pinout, verso del body diode e struttura ESD restano non letti. Azione: scegliere il codice (BSS84AK Nexperia, oppure BSS84-7-F Diodes C85202 già verificato in parte) e leggere il PDF a mano.

- **LCSC C54795811 (scelto dall'utente il 2026-10-18, "BSS84K" R+O, SOT-23): non verificato.** Pagina LCSC (rivenditore, debole): P-ch, 60 V, ±20 V, 170 mA, 225 mW, V_th "1,6 V" (typ o max non indicato, senza condizioni), R_DS(on) 3,6 Ω a 10 V, 218 k pz, MOQ 20, 0,028 $ a 20 pz. Costruttore reale non identificato, ciclo di vita non dichiarato, datasheet PDF (lcsc.com/datasheet/C54795811.pdf) **illeggibile al verificatore**. Soglia max, R_DS(on) a bassa V_GS, struttura ESD, pinout e verso del body diode: **non verificati**. Stato: **Assumed**. Il suffisso "K" non garantisce protezione ESD (il BSS84P Infineon, con dati simili, non la ha).

- **C54795811 — datasheet letto il 2026-10-18** (`hardware/datasheets/C54795811.pdf`, scaricato da datasheet.lcsc.com, **Zhuhai Hongjiacheng (HJC, ichjc.com), BSS84K, Rev. 1.1**, 3 pagine; produttore identificato, dato di costruttore, nessuna seconda fonte): P-ch SOT-23, V_DS −60 V, V_GS ±20 V, I_D −0,17 A (−1,2 A impulsivo), P_D 0,225 W, T_J −55…+150 °C; **V_GS(th) −1,1 / −1,6 / −2,2 V (min/typ/max) a I_D = −250 µA, 25 °C**; R_DS(on) 3,6 / 4,7 Ω a −10 V, 0,15 A e **4,4 / 5,7 Ω a una V_GS indicata −2,5 V in tabella ma −4,5 V nelle Features: incoerenza interna, non usabile come garanzia a bassa V_GS**; I_DSS ≤ 1 µA (−60 V); I_GSS ≤ ±10 µA (±20 V); V_SD ≤ −1,2 V a −0,17 A; **ESD HBM fino a 2 kV** (struttura gate non descritta); **pinout: 1 = G, 2 = S, 3 = D** (diagramma funzionale). Non nel datasheet: coefficiente di temperatura di V_th, curve I_D–V_GS, ciclo di vita, qualifica AEC.
- Simulazione con questo V_th (max 2,2 V, a −20 °C stima 2,34 V; β 12,5–27 mA/V² da R_DS(on)): corrente nel LED con R serie 220 Ω e rail 3,135 V = 0,72–0,98 mA (V_f 1,9–2,1 V), con unico caso basso 0,54 mA a V_th 2,34 V, gate 0,5 V, β minimo. Il pezzo regge il pilotaggio a 3,3 V con ~0,5–0,9 V di overdrive; margine minore a freddo.
- Stato: **Proposto, datasheet letto**; resta da fare: V_th a freddo (misura su campione a −20 °C), pinout sul footprint EasyEDA (1 = G, 2 = S, 3 = D), cambio di costruttore sotto lo stesso codice LCSC.

## Q4, Q8 (pilota bobine K2/K3, IF-007) — BSS138 (costruttore non indicato sul foglio) — Proposto (2026-10-18)

- Requisiti: REQ-IF-007, REQ-SW-002. Pilotaggio: GPIO → R50/R60 1 kΩ → gate, R49/R59 47 kΩ gate–GND; drain sul lato − della bobina G6K (1315 Ω, 9,1 mA a 12 V, ≈ 12 mA a 16 V). Spec e designatori in [`hardware/schematic/a6_remote_inverter.md`](../hardware/schematic/a6_remote_inverter.md).
- Dati **onsemi BSS138 Rev. 7 (aprile 2024), letti sul PDF**: V_GS(th) 0,8 / 1,3 / 1,5 V a 1 mA, −2 mV/°C; I_GSS ±100 nA (unità nel testo estratto persa, nA per coerenza); I_DSS ≤ 0,5 µA a 50 V; R_DS(on) ≤ 6 Ω a 4,5 V (nessun valore a 3,3 V); C_iss 27 pF, C_rss 6 pF. Fonte unica e **non** luJing (C53058666, PDF illeggibile): il costruttore montato va confermato.
- Verifica 47 kΩ + 1 kΩ: leakage 4,7 mV (≪ 0,8 V); overdrive ≥ 1,7 V a 3,3 V (V_th max ≈ 1,6 V a −20 °C, stima mia); τ di gate ≈ 30 ns contro 3 ms del relè; stato sicuro per sola rete passiva, indipendente dal 3V3.
- **Riserva:** un pin ESP32-S3 con pull-up interno di default in reset (≈ 45 kΩ da memoria, **non riletto sul datasheet**; GPIO0 certo, 3/45/46 da verificare) porta il gate a ≈ 1,7 V > V_th max ⇒ relè possibile in reset. Assegnare pin senza pull di default o ridurre R49/R59 a ≈ 10 kΩ; non 100 kΩ.

## U23 (ex U_IMU; accelerometro/giroscopio, assetto) — STMicroelectronics **LSM6DSOX** (LSM6DSOXTR, LGA-14L) — **Congelato** (2026-10-22, conferma utente; **sostituisce l'LSM6DSO**)

- **Sostituzione (utente, 2026-10-22):** lo schema dell'utente usa l'LSM6DSOXTR (U23, C18, C19) e l'utente ha chiesto di aggiornare i documenti. Il datasheet LSM6DSOX (**ST DS12814 Rev 3, gennaio 2019**, fornito dall'utente) è stato letto sul PDF: stesse caratteristiche dell'LSM6DSO sui parametri che contano (offset zero-g ±20 mg tip., deriva ±0,1 mg/°C, sensibilità 0,061 mg/LSB a ±2 g, rumore, Vdd 1,71–3,6 V, Vdd_IO 1,62–3,6 V, −40…+85 °C, 0,55 mA, indirizzi 0x6A/0x6B, **WHO_AM_I = 0x6C**, LGA-14L 2,5 × 3 × 0,83 mm). Differenze: Machine Learning Core e macchina a stati in più (non usati). Il pinout non è stato confrontato riga per riga con l'LSM6DSO. I valori elencati sotto sono quelli letti sul datasheet LSM6DSO Rev 3 (2024) e confermati sul DSOX.
- **ESPHome:** il driver `lsm6ds` non elenca l'LSM6DSOX ma riconosce il chip dal WHO_AM_I (0x6C = costante `LSM6DSO` in `lsm6ds.h`), quindi lo accetta e lo segnala come "LSM6DSO" (letto sul sorgente, non provato su hardware).
- Da fare: `datasheet-verifier` sull'LSM6DSOX (non lanciato), stato di produzione e revisione più recente del datasheet (quello letto è del 2019), codice LCSC e stock (C2655100 è dell'LSM6DSOTR e non vale per il DSOX).
- Requisiti: REQ-IF-001 (assetto ≤ 1°, driver ESPHome nativo). Giroscopio non richiesto: si usa solo l'accelerometro.
- Parametri decisivi, **letti sul PDF ST DS12140 Rev 3 (giugno 2024)**, tabelle delle caratteristiche meccaniche, elettriche e I²C (condizioni: Vdd = 1,8 V, T = 25 °C salvo nota): offset zero-g **±20 mg** (LA_TyOff, 1,15° di inclinazione, valore tipico), deriva ±0,1 mg/°C (≈ 3,5 mg = 0,2° su −10…+60 °C), sensibilità 0,061 mg/LSB a ±2 g e tolleranza ±1 %, rumore 70 µg/√Hz a ±2 g; Vdd 1,71–3,6 V, Vdd_IO 1,62–3,6 V; I²C 400 kHz; indirizzo 0x6A (SA0 = GND) o 0x6B (SA0 = Vdd); WHO_AM_I = 0x6C; −40…+85 °C; corrente accel + giro in alte prestazioni 0,55 mA (a 1,8 V).
- **Esito sul requisito:** l'offset di 20 mg da solo (1,15°) supera il budget di 1°. Serve la taratura dello zero a camper livellato, o una misura capovolta; dopo la taratura restano deriva termica (0,2°) e tolleranza di sensibilità (trascurabile). Valori non verificati alle condizioni d'uso (3,3 V, −10…+60 °C): i dati ST sono a 1,8 V e 25 °C.
- Driver ESPHome: componente `lsm6ds` (categoria `motion`), supporta LSM6DS3 e LSM6DSO, `roll` tra le uscite, `accelerometer_range` 2–16 g ([doc ESPHome](https://esphome.io/components/motion/lsm6ds/)). Pitch non elencato nella pagina: da verificare, altrimenti si calcola dalle accelerazioni.
- Alternative scartate: LSM6DSO (stessi dati, sostituito dall'LSM6DSOX per scelta dell'utente), MPU-6050 (NRND, fonti deboli da distributori), BMI270 (richiede il caricamento di un blob di configurazione a ogni accensione; non analizzato oltre).
- LCSC: C2655100 è dell'**LSM6DSOTR** (mirror Flux, debole): codice dell'LSM6DSOXTR **da trovare** — LGA-14L 2,5 × 3 × 0,83 mm, classe extended — footprint EasyEDA verificato: **no**.
- Rischi / note: stato di produzione non verificato (le pagine prodotto ST sono andate in timeout; l'unico indizio è la Rev 3 del datasheet, giugno 2024, quindi ancora aggiornato). Package LGA a pad nascosti: richiede reflow con stencil, non saldabile a mano; da confermare con le convenzioni di produzione (esclusi i BGA). Il verificatore `datasheet-verifier` non ha potuto leggere il PDF: i valori sopra li ho letti io dal PDF locale scaricato dallo strumento (`tool-results`, non nel repo).

## U22 (magnetometro, heading) — MEMSIC MMC5983MA (LGA-16, 3 × 3 × 1 mm) — **Congelato** (2026-10-22, conferma utente)

- Requisiti: REQ-IF-001 (heading ≤ 5°, driver ESPHome nativo).
- Parametri decisivi, **letti sul PDF MEMSIC MMC5983MA Rev A (4/3/2019)**, tabella Specifications, pp. 2 e 18: VDD 2,8–3,0–3,6 V; VDDIO 2,8–3,6 V; indirizzo I²C 7 bit `0110000` = 0x30, 400 kHz; ±8 G, 18 bit, 16384 conteggi/G; rumore RMS 0,4 mG (BW=00); −40…+105 °C; **errore di allineamento assi 1° tip. / 3° max**; heading 1° tip. **solo con l'algoritmo proprietario MEMSIC** (nota 3); variazione del null field con SET/RESET 3 mG su −40…105 °C; campo di disturbo 10 G, campo massimo 10.000 G; MSL3, 260 °C, massimo 3 cicli di reflow; corrente 450 µA a 7 misure/s (BW=00), power-down 1 µA.
- **Esito sul requisito:** l'errore di allineamento (fino a 3°) consuma più della metà del budget di 5° prima di contare gli effetti del camper; il resto dipende da calibrazione hard-iron/soft-iron e dalla distanza da relè, motori e cavi di corrente.
- **Driver ESPHome `mmc5983`** ([sorgente](https://github.com/esphome/esphome/tree/dev/esphome/components/mmc5983)): espone solo field_strength X/Y/Z, nessun heading. Scrive 0b10000 nel registro Internal Control 0 a ogni lettura: sul datasheet (p. 14) il bit 4 è **Reset**, il bit 5 è Auto_SR_en, quindi il commento nel codice è sbagliato e il driver fa solo un RESET, senza il ciclo SET → misura → RESET → misura che il datasheet (p. 18) indica per eliminare l'offset. Impatto stimato piccolo (deriva dell'offset 3 mG con SET/RESET, contro un campo terrestre di circa 500 mG), ma da rivalutare con la calibrazione; un componente esterno con la sequenza completa è possibile.
- Alternative scartate: HMC5883L (dismesso 2016, cloni), QMC5883L, MLX90393 e MMC5603 (non analizzati; hanno driver ESPHome nativo).
- LCSC: C404329 (extended; stock con segnalazioni contrastanti, da controllare sul sito) — LGA-16 — footprint EasyEDA verificato: **no**.
- Rischi / note: stato di produzione "Active" solo da DigiKey (debole), datasheet unico del 2019; LGA a pad nascosti come sopra; CAP richiede un condensatore di almeno 10 µF a bassa ESR (raccomandazione MEMSIC nella descrizione dei pin; pagina non annotata); il driver ha un'unica frequenza fissa (100 Hz, modalità continua).

---
## U_EX1, U_EX2 (expander I/O, A8) — Microchip MCP23017 (SSOP-28 `-E/SS` o SOIC-28 `-E/SO`)
- Requisiti: REQ-IF-012 (Assumed: RESET con pull-down passivo e rilascio da firmware, uscite sicure al reset), REQ-SW-002 (stato sicuro), REQ-EL-006 (ingressi ≤ 100 ms, polling). 21 linee → 2 esemplari da 16 bit (32 linee, 11 di scorta). Stato: **Congelato** (2026-10-23, conferma utente; package scelto: **SOIC-28 `MCP23017-E/SO`, LCSC C47023**). Famiglia scelta da me (non da un confronto a tappeto): le alternative comuni PCA9535/TCA9535/TCA9555 non hanno il pin RESET; riserva: NXP PCAL6416A (non verificata).
- Verifica `datasheet-verifier` del 2026-10-23 su **DS20001952C (luglio 2016)**, letto tramite una conversione automatica del PDF (r.jina.ai), non dal PDF diretto: **da ricontrollare a vista prima di congelare**; **mono-fonte** (seconde fonti solo forum).
- Parametri decisivi (DS20001952C, Tab. 1-1, 1-2, 1-3, Tab. 2-1, sez. 3.0):
  - VDD 1,8–5,5 V; 400 kHz specificati per 2,7–5,5 V (ok a 3,3 V: TLOW ≥ 1,3 µs, tR/tF ≤ 300 ns, CB ≤ 400 pF); 1,7 MHz solo 4,5–5,5 V. Il datasheet è incoerente sul campo di temperatura (+125 °C solo a 4,5–5,5 V): per il progetto vale −40…+85 °C.
  - Indirizzi 0x20–0x27 da A2:A0 (**non lasciare flottanti**): nessun conflitto con 0x30, 0x40, 0x48, 0x49, 0x6A.
  - **RESET** (attivo basso, Schmitt): VIL max 0,2·VDD (0,66 V a 3,3 V), VIH min 0,8·VDD (2,64 V), impulso minimo TRSTL 1 µs, **uscite in alta impedenza entro 1 µs** (TIOZ); "deve essere polarizzato esternamente" (non flottante). Default dopo POR: IODIR = 0xFF (tutti ingressi), GPPU = 0 (pull-up interni spenti).
  - SDA/SCL: VIL max 0,66 V e VIH min 2,64 V a 3,3 V (soglie 0,2/0,8·VDD, più strette dello standard 0,3/0,7); VOL SDA max 0,6 V a 3 mA (VDD 1,8 V), 0,8 V a 4,5 V; punto a 3,3 V non dato.
  - GPIO: ingressi VIH/VIL come sopra; perdita ±1 µA; 25 mA per pin è un assoluto massimo, non una corrente garantita; VOL/VOH a 3,3 V **non specificati** (solo a 4,5 V: VOL 0,6 V a 8 mA).
- **Non documentato dal datasheet (impatti):**
  - Cosa azzera il pin RESET e se ripristina la macchina a stati I²C; tempo di recupero a 3,3 V (THLD = 0 ns tipico solo a 5 V). Il datasheet garantisce però le uscite in alta impedenza durante RESET: è ciò che serve per lo stato sicuro (gate con pull-down). Conseguenza di progetto: dopo ogni reset il firmware **riscrive tutti i registri** e attende qualche µs; il recupero del bus non si affida al pin RESET ma al bus-clear (9 impulsi SCL).
  - CIN dei pin SDA/SCL (solo CB ≤ 400 pF e CIO ≤ 50 pF per i GPIO), timeout di bus, clock stretching: capacità del bus da stimare con prudenza.
  - Passaggio IODIR ingresso → uscita con OLAT = 0 senza glitch (inferenza, non garanzia): per `SIG_INVERTER_GREEN/RED` da provare al banco. Leggere GPIO restituisce il pin, non il latch: niente read-modify-write su GPIO/OLAT (usare OLAT).
- ESPHome: componente `mcp23017` (famiglia `mcp230xx`), I²C, 16 pin, indirizzo 0x20 di default, modo INPUT/OUTPUT per pin con `pullup`, `inverted`, `interrupt` (esphome.io/components/mcp230xx; non dice nulla sul RESET). Il passaggio dinamico input/output per le linee bidirezionali è da provare.
- **Verifica LCSC/produzione (2026-10-23, pagine lette direttamente nel browser):** pagina LCSC C47023 = MCP23017-E/SO, SOIC-28-300mil, **Extended**, stock **1.184**, 1,77 USD (1 pz) / 1,50 (10 pz), −40…+85 °C, 1,8–5,5 V, funzione di reset, nessun avviso NRND sulla pagina. Pagina prodotto Microchip (microchip.com/en-us/product/MCP23017): **Status: In Production**; esiste un "MCP23017 Rev. A Silicon Errata" **non letto**. Footprint EasyEDA ancora da verificare. Il datasheet attuale è sul sito Microchip (DS20001952): la rev. C del 2016 usata per i dati potrebbe non essere l'ultima.
- ⚠️ La scheda LCSC riporta nelle feature "Pins GPA7, GPB7 are output only for MCP23017" (testo del datasheet, **non verificato sul PDF**): **GPA7 e GPB7 non vanno usati come ingressi** né per le linee bidirezionali `SIG_INVERTER_GREEN/RED`; solo uscite (con 32 linee e 21 usate non costa nulla). Da leggere nell'errata.
- LCSC/JLCPCB (fonte debole, istantanea del verificatore 2026-10-23, superata per il SOIC dalla verifica sopra): `-E/SS` **C506653**, SSOP-28 (5,3 mm, passo 0,65 mm da JLCPCB), Extended, stock circa 90, uno snippet lo segna "not recommended for new designs" (non confermato); `-E/SO` **C47023**, SOIC-28 largo, Extended, stock circa 3.200. Stato produzione sul sito Microchip: **non verificato** (403). Footprint EasyEDA verificato: **no**.
- Alternative scartate: PCA9535/TCA9535/TCA9555 (nessun pin RESET); TCA6416A, PCAL6416A (non analizzati, solo 2 indirizzi).
- Rischi: stock di C506653 (SSOP scartato: si usa il SOIC C47023); datasheet del 2016 con incoerenze interne; RESET non descritto compiutamente; due esemplari Extended (costo di setup in più); fonte unica convertita.
