# Schematico A2 — Stadio valvola motorizzata (pagina 3 del foglio EasyEDA)

Requisiti: REQ-EL-003 (pilotaggio valvola con misura di corrente, Confirmed), REQ-SW-002 (stato sicuro per sole reti passive). Registro componenti: [`../components.md`](../components.md), sezione "Stadio valvola (EL-003)" e verifiche della pagina 3. Rev. 2026-10-15: **designatori allineati allo schematico reale; verificato circuitalmente** (terza rilettura live, nessun errore residuo). Codici, MPN e disponibilità non sono oggetto di questa verifica.

Scelte dell'utente: due interruttori high-side discreti (P-MOSFET + BSS138); P-MOSFET HXY `DMP4065S-7-HXY` (dati solo da listino); op-amp di misura separato da quello del pistone; alimentazione dalla linea `Vmot` (la stessa del pistone: P2.1 e contatti di K1).

## Valvola e cablaggio (ipotesi da verificare col multimetro, OPEN-04)
U.S. Solid 1/2", 9–24 V, 3 fili con finecorsa interni: **nero = −, rosso = apre, blu = chiude**. Corrente a 12 V non dichiarata: marcia 0,5 A, picco/stallo 2 A (**Assumed**). Se il lato spento può salire verso Vmot attraverso il motore o i finecorsa, serve un N-MOSFET di pull-down per filo (mezzo ponte).

**Connettore CN2 (3 poli, 5,08 mm):** pin 1 = **blu** (chiude, Q7), pin 2 = **rosso** (apre, Q5), pin 3 = **nero** (ritorno, shunt R16). Riportare l'ordine in serigrafia.

## Net verso il resto della board

| Net | Direzione | Note |
|---|---|---|
| `Vmot` | alimentazione | linea attuatore, dopo il fusibile esterno; condivisa col pistone (9 A sommati: 7 A soglia + 2 A picco valvola): fusibile e P2 da dimensionare |
| `OUT_VALVE_OPEN` | MCU → foglio | GPIO, attivo alto: apre (rosso). **C6-Zero: GP4 (pin senza pull al reset)**; su un pin con weak pull-up il gate di Q3 salirebbe a ≈ 1,67 V e la valvola si muoverebbe al boot ([verifica](../../hardware/schematic/a8_verifica_stato_reset.md)) |
| `OUT_VALVE_CLOSE` | MCU → foglio | GPIO, attivo alto: chiude (blu). **C6-Zero: GP5**, stesso vincolo |
| `IN_VALVE_SENSE` | foglio → MCU | ADC, 0,9 V/A (18 mΩ × G 50), 2,25 V a 2,5 A |
| `+5V`, `GND` | alimentazione | `+5V` per U5 |

Interblocco rosso/blu e sequenza **solo software**: mai accesi insieme; pausa tra due comandi opposti. Fine corsa rilevata dal calo di corrente, con timeout.

## Distinta (designatori dello schematico)

| Rif. | Valore | Funzione |
|---|---|---|
| Q5 | P-MOSFET HXY DMP4065S-7-HXY | high-side filo **rosso** (apre) |
| Q7 | idem | high-side filo **blu** (chiude) |
| Q3 | BSS138 | pilota il gate di Q5 |
| Q6 | BSS138 | pilota il gate di Q7 |
| R15 / R26 | 1 kΩ | serie GPIO → gate Q3 / Q6 |
| R14 / R25 | 47 kΩ | pull-down gate Q3 / Q6 (stato sicuro) |
| R24 / R28 | 2,2 kΩ | drain Q3 / Q6 → gate Q5 / Q7 |
| R23 / R27 | 10 kΩ | gate–source Q5 / Q7 (spento di default), sul `Vmot` |
| D10 / D13 | Zener 12 V BZT52C12S, **catodo su Vmot, anodo sul gate** | clamp V_GS di Q5 / Q7 |
| D9 / D12 | Schottky SS56, **anodo a GND, catodo sull'uscita** | ricircolo del filo rosso / blu |
| R16 | shunt 18 mΩ | misura corrente (ritorno nero → GND) |
| R21 / R22 | 100 Ω | filtro ingresso U5: IN+ (lato nero) / IN− (lato GND) |
| C4 | 10 nF | filtro differenziale fra IN+ e IN− |
| U5 | INA180A2 (clone LX) | amplificatore, G = 50 |
| C6 | 100 nF | disaccoppiamento VS (+5V) |
| R20 | 1 kΩ | serie uscita verso ADC |
| C5 | 100 nF | filtro uscita |
| D11 | Zener 3,3 V BZT52C3V3, catodo sul nodo, anodo a GND | clamp ADC |
| CN2 | 3 poli 5,08 mm | valvola: 1 blu, 2 rosso, 3 nero |

## Netlist (letta dallo schematico)

| Net | Pin collegati |
|---|---|
| `Vmot` | Q5.S, Q7.S, R23.2, R27.2, D10.K, D13.K |
| `GATE_Q5` | Q5.G, R23.1, R24.2, D10.A |
| `GATE_Q7` | Q7.G, R27.1, R28.2, D13.A |
| `DRN_Q3` | Q3.D, R24.1 |
| `DRN_Q6` | Q6.D, R28.1 |
| Rosso | Q5.D, CN2.2, D9.K |
| Blu | Q7.D, CN2.1, D12.K |
| Nero | CN2.3, R16.1, R21.2 |
| `GATE_Q3` | Q3.G, R14.2, R15.2 |
| `GATE_Q6` | Q6.G, R25.2, R26.2 |
| `OUT_VALVE_OPEN` | R15.1 |
| `OUT_VALVE_CLOSE` | R26.1 |
| `SENSE_P` | R21.1, C4.2, U5.3 (IN+) |
| `SENSE_N` | R22.1, C4.1, U5.4 (IN−) |
| `AMP_OUT` | U5.1, R20.1 |
| `IN_VALVE_SENSE` | R20.2, C5.2, D11.1 (K) |
| `+5V` | U5.5 (VS), C6.2 |
| `GND` | Q3.S, Q6.S, R14.1, R25.1, R16.2, R22.2, D9.A, D12.A, D11.A, C5.1, C6.1, U5.2 |

## Dimensionamento (valori nominali, dati di listino per Q5/Q7)
- V_GS(on) = −Vmot × 10 k/12,2 k: −9,8 V a 12 V, −8,2 V a 10 V, −11,8 V a 14,4 V; D10/D13 limitano a −12 V nei transitori. Corrente nel divisore ≈ 1 mA per canale acceso.
- Spento: R14/R25 tengono Q3/Q6 chiusi → R23/R27 portano il gate al source → Q5/Q7 spenti (REQ-SW-002).
- Marcia 0,5 A: Q5 ≈ 0,03 W. Stallo 2 A: ≈ 0,5 W, T_j ≈ 147 °C su rame minimo a 60 °C ambiente (R_θJA del Diodes): solo per stalli brevi o con rame ≥ 1 in² sotto Q5/Q7.
- Misura: 0,5 A → 0,45 V; 2,5 A → 2,25 V (< 2,45 V ADC); sotto 0,5 V di uscita il guadagno non è garantito (zero in firmware). R16: 0,11 W a 2,5 A; la corrente di ricircolo attraversa ancora lo shunt.

## Punti aperti
- Cablaggio interno della valvola e stato del lato spento.
- Fusibile e P2 su `Vmot` per 9 A sommati; protezione del rail Vmot dai transitori.
- Q5/Q7: V_GSS, R_θJA, SOA e pinout non letti dal PDF HXY; collaudo in ingresso.
- MPN dello shunt R16 nello schematico (da correggere); verifica di SS56 in SMA a 2 A.
- Layout: Kelvin R16 → U5; R16 vicino a CN2; rame sotto Q5/Q7.
