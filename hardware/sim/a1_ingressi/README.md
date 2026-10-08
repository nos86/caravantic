# A1 — Ingressi digitali IN-CAB / IN-CEL: dimensionamento e verifica SPICE

Requisiti: REQ-EL-006, REQ-EL-008 (`docs/frd.md`). Simulatore: ngspice-47. Rigenerare con `python sim_a1.py GB` o `python sim_a1.py NONGB [R_S_k R_PU_k]` (scrive `out/results_<tag>.json`, `out/01_dc_<tag>.png`, `out/02_gradino_<tag>.png`). La variabile d'ambiente `A1_TOPO` seleziona la topologia: `noD1` (default), `series`, `shunt`, `shunt_noD2`. `explore.py` ripete la scelta di R_S e R_PU; `fit_opto.py` tara velocità e saturazione del modello dell'opto.

## Circuito (per canale; i due canali sono identici; LED in continuo, nessuno strobe)

```
IN ─R1─┤◄D2├──┬──── U1.1 (anodo LED)
              │      U1.2 (catodo LED) ── GND
            D1 ▲ (catodo sul nodo, anodo a GND)
              GND
U1 lato uscita: collettore ── R2 ── 3V3 ; collettore → GPIO_IN ; emettitore → GND
```

| Rif. | Valore | Funzione |
|---|---|---|
| R1 (R_S) | 8,2 kΩ, **0805** (rischio load dump accettato) | Fissa la corrente del LED: I_F ≈ (V_in − V_Z − V_F)/R1 |
| D2 | BZT52C3V3, catodo verso l'ingresso | Soglia: sotto circa 3,3 V + V_F non c'è corrente nel LED. Con ingresso negativo conduce in diretta |
| D1 | 1N4148WS, catodo sul nodo | Antiparallelo al LED: con ingresso negativo la corrente passa da D1 e D2 e il LED vede al massimo 0,7 V in inversa (limite 5 V) |
| U1 | TLP293 rango GB | Opto, CTR ≥ 100 % garantito a I_F = 0,5 mA e 5 mA |
| R2 (R_PU) | 12 kΩ | Pull-up dell'uscita. La finestra "attivo sotto 8 V / inattivo sopra 2 V" è praticamente un solo valore |

Decisione dell'utente (2026-10-08): LED in continuo, assorbimento di circa 1 mA a cellula attiva accettato; R1 in 0805 con rischio load dump accettato. Firmware: ingressi semplici con filtro anti-rimbalzo.

Topologie confrontate: `series` (D1 BAV21W in serie, versione precedente: attivo da 7,1 V, inattivo fino a 2,16 V con R_PU 18 kΩ); `shunt` (D1 verso massa con diodo antiparallelo); `noD1` (adottata: senza diodo in derivazione). `shunt` e `noD1` danno risultati identici sul lato positivo; `shunt_noD2` (senza antiparallelo) porta la tensione inversa sul LED a 3,05 V nel burst 3a, quindi l'antiparallelo si tiene.

## Dati dell'opto usati (datasheet Toshiba TLP293, Rev. 7.0, 2026-08-05; letto direttamente dal PDF)

| Parametro | GB | Non ranked | Condizioni |
|---|---|---|---|
| CTR lineare | **100–600 %** | 50–600 % | I_F = 0,5 mA **e** 5 mA, V_CE = 5 V, 25 °C |
| CTR saturo | **≥ 30 %** (typ 60 %) | non dato per il minimo (typ 60 %) | I_F = 1 mA, V_CE = 0,4 V |
| V_CE(sat) | ≤ 0,3 V | ≤ 0,2 V | I_C = 0,2 mA, I_F = 1 mA |
| V_F | 1,1 / 1,25 / 1,4 V | idem | I_F = 10 mA |
| I_F max / V_R max / V_CEO | 50 mA / 5 V / 80 V | idem | — |
| I_C(off) | ≤ 10 µA | idem | V_F = 0,7 V, V_CE = 48 V, 25 °C |

## Corner di simulazione

| Corner | T | V_Z (5 mA) | CTR lineare | CTR saturo (1 mA, 0,4 V) |
|---|---|---|---|---|
| ON_worst | −10 °C | 3,5 V (max) | GB 100 % × 0,42 = 42 %; non GB 21 % | GB circa 13 %; non GB circa 6 % |
| tipico | 25 °C | 3,3 V | 300 % (GB) / 200 % (non GB) | circa 62 % |
| OFF_worst / stress | 60 °C | 3,1 V (min) | 600 % (max) | circa 62 % |

Il fattore 0,42 = 0,84 (+60 °C) × 0,5 (invecchiamento) è **generico**, ripreso dal progetto precedente: le curve TLP293 (Fig. 11.12/11.13) non sono state lette. **Sotto I_F = 0,5 mA il modello tiene il CTR costante**: è un'approssimazione ottimistica, perché il datasheet non garantisce nulla in quella zona.

## Risultati: GB, R1 = 8,2 kΩ, R2 = 12 kΩ

| Verifica | Richiesto | Simulato (caso peggiore) | Esito |
|---|---|---|---|
| Lettura "attivo" da | ≥ 8 V | 7,84 V (modello) | ⚠️ margine 0,16 V; il LED supera 0,5 mA (CTR garantito) solo da circa 8 V |
| Lettura "inattivo" fino a | ≤ 2 V | 2,10 V | ⚠️ margine 0,10 V |
| V_out con ingresso a 8 V, ON_worst | < 0,825 V (V_IL) | 0,73 V | ⚠️ margine 0,10 V |
| Campi nominali Confirmed (11,5–13,8 V; 12,8–14,4 V) | lettura "attivo" | I_LED 0,9–1,3 mA, V_out 0,59–0,60 V | ✅ |
| Assorbimento di IN-CEL | ≈ 1 mA (accettato dall'utente) | 1,06–1,13 mA a 12,8 V; 1,25–1,32 mA a 14,4 V (caldo, 19 mW); 2,4–2,5 mA a 24 V | ✅ |
| Tempo di risposta | ≤ 100 ms | accensione ≤ 60 µs, spegnimento ≤ 100 µs | ✅ |
| +24 V continui | nessun danno | I_LED 2,5 mA; R1 50 mW (0805 da 0,125 W) | ✅ |
| −16 V continui | nessun danno | 1,8 mA da R1, D1 e D2; LED a 0,54 V in inversa; R1 26 mW | ✅ |
| Load dump 101 V / 400 ms | nessun danno | I_LED 11,8 mA; **R1 1,13 W di picco, 174 mJ** (0805: 9× la potenza nominale standard) | ❌ **non dimostrabile con 0805: rischio accettato dall'utente** |
| Impulso 1, −150 V | nessun danno | 18 mA per 2 ms; LED a 0,66 V in inversa; R1 2,7 W per 2 ms (1,8 mJ) | ⚠️ tenuta di R1 da verificare sulla curva degli impulsi singoli (non letta) |
| Impulso 2a, +112 V | I_LED < 50 mA | 14,7 mA; R1 1,8 W per 50 µs | ⚠️ idem |
| Impulso 3a, −220 V **(livello non verificato)** | nessun danno | LED a 0,68 V in inversa; R1 5,2 W per 150 ns; 205 V ai capi di R1 (U_max 0805: 150 V) | ⚠️ tensione impulsiva da verificare |
| Impulso 3b, +150 V **(livello non verificato)** | I_LED < 50 mA | 19 mA; R1 3 W per 150 ns | ⚠️ |

## Risultati: variante NON GB

**Non utilizzabile in continuo.** Con R1 = 8,2 kΩ e la topologia adottata:

| R2 | "Attivo" garantito da | "Inattivo" garantito fino a |
|---|---|---|
| 10 kΩ, 12 kΩ, 15 kΩ | **mai** (l'uscita non scende sotto V_IL) | 2,20 / 2,10 / 1,96 V |
| 22 kΩ | 8,1 V ❌ | 1,70 V ❌ |
| 33 kΩ | 6,6 V | 1,42 V ❌ |
| 47 kΩ | 5,7 V | 1,20 V ❌ |

Non esiste un R2 che dia insieme "attivo" a 8 V e "inattivo" a 2 V. In più il datasheet non dà il CTR saturo minimo del non ranked (il valore usato è la metà del GB, un'assunzione). Il foglio EasyEDA riporta `TLP293(TPL,E)`: va corretto in `TLP293(GB-TPL,E)`.

## Limiti della verifica

- **Nessun modello SPICE del costruttore** per TLP293, BZT52 e 1N4148WS. I modelli in `models.lib` sono parametrici e tarati sui valori dei datasheet citati. L'opto è tarato sulla velocità (t_r/t_f 2/3 µs a R_L = 100 Ω; il modello dà 1,9/2,1 µs) e sulla saturazione (GB 31,5 % contro 30 % minimo). Le curve del datasheet non sono state lette.
- **CTR sotto 0,5 mA:** non garantito dal datasheet, modellato costante. È il punto più debole del dimensionamento a LED continuo; si chiude leggendo la Fig. 11.12 o misurando campioni.
- **Deriva termica e invecchiamento del CTR:** fattore generico 0,42, non da dati TLP293.
- **Margini sottili su entrambe le soglie** (0,16 V e 0,10 V): la finestra di R2 è praticamente un solo valore e dipende dal modello di perdita dello Zener (5 µA a 1 V, dato solo a 25 °C, tenuto costante).
- **Energia sul resistore serie** non confrontata con le curve di impulso Vishay (non lette). Il datasheet Vishay CRCW e3 dà per lo 0805 P70 = 0,125 W (standard) / 0,25 W (esteso), U_max 150 V e il sovraccarico di breve durata a 2,5 × P70 per 5 s.
- **Temperatura di giunzione non simulata.**
- **Livelli degli impulsi ISO 7637-2 3a/3b non verificati** sulla norma (vedi REQ-EL-008).
- **Corrente diretta impulsiva dello Zener** (18–27 mA) non verificata su un limite di datasheet: nel registro c'è solo V_F 0,9 V a 10 mA e P_D 370 mW.
