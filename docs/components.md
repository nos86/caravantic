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
