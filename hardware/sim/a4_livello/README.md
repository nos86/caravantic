# A4 — Generatore di corrente per il sender di livello: confronto topologie e dimensionamento

Requisito: REQ-IF-003 (`docs/frd.md`). Simulatore: ngspice (stesso setup di A1). Eseguire da questa cartella: `python sim_a4.py S 68`, `python sim_a4.py M <Re1> <Re2> <Rref>`, `python explore_m.py`, `python final_m.py`, `python faults_m.py`.

**Limite dei modelli (leggere prima).** `models.lib` contiene un 1N4148WS generico (tarato per la sim A1) e un PNP **2N3906 con parametri SPICE generici, da memoria, non letti da un modello del costruttore**. I valori assoluti di corrente sono quindi indicativi; hanno valore i **confronti fra topologie** e gli ordini di grandezza. VOL del GPIO = 0,2 V: il datasheet ESP32-S3 v2.2 dà V_OL max 0,1·VDD (≈ 0,33 V) e I_OL 28 mA a 0,495 V (pad più forte): l'ipotesi è prudente. Il modello SPICE della coppia **non è** quello del costruttore (DMMT3906W): vedi `a4_serbatoio_chiare.md`.

## Risultati (Rs 0…190 Ω, VCC 3,2/3,3/3,4 V, −10/25/60 °C, taratura a 25 °C e 3,3 V)

| Topologia | Deriva con T (−10 / +60 °C) | Sensibilità al rail (±3 %) | Giudizio |
|---|---|---|---|
| **S**: PNP + 2 diodi di base + Re 68 Ω (proposta del 2026-10-17) | **+15 % / −15 %** (≈ −0,4 %/K) | ±1 % | **Scartata**: 2·V_D − V_EB ha tempco −2 mV/K su 0,55 V |
| **M**: specchio PNP, Re1 = Re2 = 47 Ω, Rref 243 Ω | −2,4 % / +2,4 % | ±4,2 % | Ok, ma il GPIO sinka 8 mA |
| **M-ratio**: Re1 390 Ω, Re2 47 Ω, Rref 1,65 kΩ | −2,1 % / +1,9 % | ±4,6 % | **Scelta**: il GPIO sinka solo 1,2 mA |

La sensibilità al rail dell'ordine di 1,4× la variazione relativa (4,2 % per ±3 %) è intrinseca: la corrente di riferimento è `(Vcc − V_EB − V_OL)/(Rref + Re1)`. La parte statica è assorbita dalla taratura; conta la deriva del rail, non la tolleranza.

## Candidato M-ratio (provvisorio): Re1 = 390 Ω, Re2 = 47 Ω, Rref = 1,65 kΩ

- I_out = 8,0 mA a 25 °C / 3,3 V / 95 Ω; 7,5…8,5 mA sul campo.
- Regolazione sul carico: a −10 °C e 3,2 V, da 0 a 209 Ω (sender +10 %) la corrente cala dello 0,7 %. Compliance ampia con D_f = 1N4148WS.
- Sender aperto: V(N) = 2,7 V (freddo, rail basso) … 3,1–3,2 V (caldo, rail alto): chiaramente fuori dal range utile (≤ 1,52 V).
- Guasto N a 24 V (EN acceso o spento): corrente nel sender e in D_f ≈ 0, la corrente non ritorna al transistor. N a massa: 8,7 mA, nessun danno.
- Reset con pull-down interno debole da 45 kΩ (ipotesi): 118 µA nel sender (22 mV a 190 Ω): innocuo.
- Dissipazione: Re2 3 mW, Rref 2,4 mW, Q2 < 16 mW.

## Alternativa valutata: INA219 (misura ratiometrica V_bus / I_shunt) — `ina219_error.py`

Datasheet TI SBOS448G (Rev. G, dic. 2015) letto direttamente (`pdftotext`). Configurazione: GPIO → 1N4148WS → R_exc → Rsh 3,3 Ω → nodo N (IN−) → sender → GND; `Rs = V_bus · Rsh / V_shunt`, indipendente dall'eccitazione. Errore su Rs in % del fondo scala (190 Ω), dai soli limiti di datasheet (offset del bus escluso: valore non leggibile dal grafico):

| Grado | Condizione | p95 | Caso peggiore |
|---|---|---|---|
| A | 25 °C | 1,4 % | 2,2 % |
| A | −25…85 °C | 1,9 % | 3,2 % |
| B | 25 °C | 1,1 % | 1,7 % |
| B | −25…85 °C | 1,5 % | 2,4 % |

Valori senza taratura; la taratura a 3 punti elimina la parte statica. Le correnti di bias degli ingressi (20 µA + V/320 kΩ su IN−) pesano circa 0,2 % e sono correggibili. Confronto con lo specchio: deriva ±2,4 % della sola sorgente, più l'errore dell'ADC ESP32-S3 non caratterizzato.
