# Schematico A1 — Ingressi digitali IN-CAB / IN-CEL (specifica di disegno)

Requisiti: REQ-EL-006, REQ-EL-008, REQ-EL-009. Dimensionamento e verifica: [`../sim/a1_ingressi/README.md`](../sim/a1_ingressi/README.md). Registro componenti: [`../../docs/components.md`](../../docs/components.md).

Rev. 2026-10-08 (3): opto **Toshiba TLP293 rango GB**, LED in conduzione continua (assorbimento di circa 1 mA a cellula attiva accettato dall'utente), **senza D1 in serie**: la protezione inversa è fatta dal diodo antiparallelo al LED e dallo Zener in diretta. **5 componenti per canale.** Allineata al foglio EasyEDA "Optoisolated inputs" (designatori del canale IN-CAB).

Foglio EasyEDA: **Optoisolated inputs**. Il canale IN-CAB usa R1, D1, D2, U1, R2; il canale IN-CEL usa R3, D3, D4, U2 (letti dal foglio il 2026-10-15). I designatori dei canali AUX sono nella sezione REQ-EL-009.

Connettore di campo sul foglio (**CN1**, 4 poli, "Digital Inputs", 2026-10-15): pin 4 = `IN_T15` (IN-CAB), pin 3 = `IN_CEL`, pin 2 = `IN3` (IN-AUX1), pin 1 = `IN4` (IN-AUX2). Il foglio chiama `IN_T15` quello che questa specifica chiama `IN_CAB`: **nome da uniformare**.

## Net verso il resto della board (net label / porte)

| Net | Direzione | Note |
|---|---|---|
| `IN_CAB` | dal connettore di campo | +15 sotto chiave, derivato dalla radio (vedi sotto) |
| `IN_CEL` | dal connettore di campo | uscita della centralina cellula |
| `SIG_CAB` | foglio → MCU | attivo basso, GPIO di solo ingresso (nella specifica precedente: `IN_CAB_N`; **nome da decidere**) |
| `SIG_CEL` | foglio → MCU | idem per IN-CEL |
| `+3V3`, `GND` | alimentazione | GND = massa della board = massa veicolo |

Il connettore di campo non fa parte di questo foglio: è un punto aperto da decidere nella sezione connettori.

## Schema (per canale)

```
IN ─R1 8,2k─┤◄D2├──┬──── U1.1 (anodo LED)
 (0805)  BZT52C3V3 │      U1.2 (catodo LED) ── GND
                 D1 ▲ 1N4148WS (catodo sul nodo, anodo a GND)
                   │
                  GND
U1 lato uscita: pin 4 (collettore) ── R2 12k ── +3V3 ; pin 4 → SIG_xxx ; pin 3 (emettitore) → GND
```

## Distinta (per canale IN-CAB)

| Designatore | Valore / P/N | Package | Stato componente |
|---|---|---|---|
| R1 | 8,2 kΩ 1 % | 0805 | Proposto. **Rischio accettato**: la tenuta al load dump non è dimostrabile (vedi REQ-EL-008) |
| D2 | BZT52C3V3 (Diodes, C151564), **catodo verso l'ingresso** | SOD-123 | Proposto |
| D1 | 1N4148WS, **catodo sul nodo, anodo a GND** | SOD-323 | Proposto |
| U1 | **TLP293(GB-TPL,E)** (Toshiba, LCSC C77656) | SO4 (11-3C1) | Proposto (scelta utente, 2026-10-08). ⚠️ Il foglio mostra `TLP293(TPL,E)` (non ranked): da correggere |
| R2 | 12 kΩ 1 % | 0805 | — |

Rimossi rispetto alle versioni precedenti: D1 BAV21W in serie (250 V), Q1 MMBTA42, R_E, R_B, R_BE, C_S, R_IN e il net `STROBE_IN`.

## Netlist del canale 1 (il canale 2 è identico)

| Net | Pin collegati |
|---|---|
| `IN_CAB` | R1.1 |
| `N1` | R1.2 — D2.K |
| `N2` | D2.A — D1.K — U1.1 (anodo LED) |
| `GND` | D1.A — U1.2 (catodo LED) — U1.3 (emettitore) |
| `SIG_CAB` | U1.4 (collettore) — R2.1 |
| `+3V3` | R2.2 |

Piedinature da controllare sul simbolo EasyEDA scelto:
- **TLP293 (SO4):** 1 anodo, 2 catodo, 3 emettitore, 4 collettore (datasheet Toshiba Rev. 7.0, §4).
- **Diodi:** controllare la marcatura A/K del simbolo LCSC. D2 deve avere il simbolo dello Zener, D1 quello di un diodo normale.

## Alimentazione di IN_CAB dal veicolo
Il +15 sotto chiave è derivato dalla **radio** con un cavo da 0,5 mm² (Confirmed, utente 2026-10-08). Il cavo si trova sulla rete del veicolo, lato alternatore: i transitori ISO 7637-2 dell'X244 arrivano qui, non sul cavo da 35 mm² della batteria servizi. Raccomandazioni (*dovrebbe*, non ancora decise):
- fusibile in linea, a pochi centimetri dalla derivazione, dimensionato per il cavo da 0,5 mm² (il fusibile della radio a monte è per un cavo e un carico diversi);
- la massa del segnale è la massa della board: un offset fra la massa carrozzeria vicino alla radio e la massa della board sposta le soglie. Il margine su "inattivo" è di 0,10 V (vedi simulazione).

## Firmware
Nessuno strobe: i due GPIO sono ingressi semplici (senza pull interni). Lettura periodica con filtro anti-rimbalzo di almeno 3 campioni concordi; tempo di risposta totale ≤ 100 ms (il circuito risponde in meno di 0,2 ms).

## Note di layout (da riprendere nella fase PCB)
- Il nodo `N1`/`N2` arriva a 101 V nel load dump (R1 ne assorbe la maggior parte) e a circa 160 V nei burst: servono distanze ≥ 0,5 mm verso `+3V3`/GPIO e nessuna traccia lato MCU sotto il corpo dell'opto.
- La distanza di isolamento fra i lati del TLP293 è quella del package (creepage 5,0 mm min. dichiarata da Toshiba). Il ritorno è comunque `GND` comune.
- R1 vicino al connettore di campo.

---

# Canali configurabili IN-AUX1 / IN-AUX2 (REQ-EL-009)

Stessa rete dei canali IN-CAB/IN-CEL (R1 8,2 kΩ 0805, Zener BZT52C3V3, TLP293 GB, 1N4148WS antiparallelo, pull-up 12 kΩ). Due jumper a saldare a 3 pad per canale scelgono a cosa collegare i due capi della catena del LED. I jumper escono dalla fabbrica **aperti**.

```
              JP_A (3 pad)                                   JP_B (3 pad)
 IN_AUXx ──[1]                                          [1]── GND
            [2]── TOP ─R1─┤◄Zener├─┬─ LED U.1→U.2 ─┬─ BOT ──[2]
 +12V_BAT ──[3]                     └──── D1 ◄──────┘        [3]── IN_AUXx
                                (D1: catodo su U.1, anodo su BOT)
 lato uscita: U.4 ── R_PU 12k ── +3V3 ; U.4 → SIG_AUXx ; U.3 → GND
```

| Modo | JP_A | JP_B | Comportamento |
|---|---|---|---|
| **H, attivo a 12 V** | 1-2 (TOP = IN) | 2-1 (BOT = GND) | Identico a IN-CAB/IN-CEL |
| **L, attivo a massa** | 3-2 (TOP = +12V_BAT) | 2-3 (BOT = IN) | La catena è alimentata dalla board; IN verso massa accende il LED |
| Errato: entrambi su IN | 1-2 | 2-3 | LED cortocircuitato: canale sempre "inattivo", nessun danno |
| Errato: +12 V e GND | 3-2 | 2-1 | LED sempre acceso (circa 1 mA): canale sempre "attivo", nessun danno |
| Aperti (default) | — | — | Canale sempre "inattivo" |

**Nota sul D1.** Nei canali IN-CAB/IN-CEL l'anodo del D1 va a GND perché il catodo del LED è a GND. Qui deve andare su **BOT**, cioè sul catodo del LED, non su GND: altrimenti nel modo L il D1 cortocircuita l'ingresso verso massa senza passare dal LED.

## Verifica del modo L per equivalenza
La corrente del LED dipende solo da V_TOP − V_BOT. Il modo L equivale quindi al modo H simulato in [`../sim/a1_ingressi/README.md`](../sim/a1_ingressi/README.md) con una tensione d'ingresso equivalente V_eq = V_board − V_IN:

| Condizione | V_eq | Esito (dai risultati del modo H) |
|---|---|---|
| Board a 10,0 V, IN a 0 V | 10,0 V | attivo (soglia simulata 7,84 V) |
| Board a 10,0 V, IN a 2 V (contatto resistivo o caduta sul cavo) | 8,0 V | attivo, margine 0,16 V come nel modo H |
| Board a 14,6 V, IN a 0 V | 14,6 V | attivo; I_LED circa 1,25 mA ≤ 1,5 mA |
| IN aperto | — | nessuna corrente: inattivo |
| IN a ≥ V_board − 2 V | ≤ 2 V | inattivo (soglia simulata 2,10 V) |
| IN a +24 V | −10…−14 V | inversa: conducono D1 e lo Zener in diretta, circa 1,2 mA; LED a circa 0,6 V in inversa |
| IN a −16 V | 26–30,6 V | I_LED circa 3,2 mA; R1 circa 85 mW (0805: 125 mW) |
| Impulso 1 (−150 V) su IN | circa 160 V | I_LED circa 19 mA per 2 ms (< 50 mA, OK). R1 dissipa circa 3 W per 2 ms (circa 6 mJ): **più severo che nel modo H** (1,8 mJ). Da verificare sulla curva degli impulsi del resistore (punto già aperto) |
| Load dump (+101 V) su IN | circa −89 V | circa 11 mA in inversa attraverso D1 e Zener **verso il rail +12V_BAT** (il rail deve assorbirli, trascurabile) |

Nessuna nuova simulazione: l'equivalenza è esatta per il circuito e per i modelli usati. Restano gli stessi rischi del modo H (R1 0805 nel load dump, CTR sotto 0,5 mA).

## Designatori sul foglio EasyEDA (letti dall'immagine del foglio, 2026-10-15)

| Funzione (nella specifica) | AUX1 (net `IN3`, CN1.2) | AUX2 (net `IN4`, CN1.1) |
|---|---|---|
| R1 (serie, 8,2 kΩ) | R29 | R30 |
| Zener BZT52C3V3 | D15 | D17 |
| D1 (1N4148WS antiparallelo) | D14 | D16 |
| Opto TLP293(GB-TPL,E) | U6 | U7 |
| JP_A (3 pad: 1 = IN, 2 = TOP, 3 = +12 V) | H1 | H3 |
| JP_B (3 pad: 1 = GND, 2 = BOT, 3 = IN) | H2 | H4 |

Il foglio mostra GB su U2, U6 e U7. Il simbolo non ranked segnalato per U1 va riverificato.
Pull-up e `SIG_AUXx` non erano nell'immagine: designatori da leggere dal foglio. Il rail di alimentazione dei jumper è etichettato `+12V` sul foglio (la specifica lo chiama `+12V_BAT`): deve essere il rail protetto dopo l'ideal-diode, da confermare nella sezione alimentazione.

Lo schema del foglio coincide con la topologia sopra (D14/D16 con anodo su BOT, jumper H2/H4 sul catodo del LED). La rete è stata riletta a mano dall'immagine: **nessuna simulazione del modo L**, vale l'equivalenza della sezione precedente.

## Note emerse dalla rilettura del foglio (2026-10-15)
- **Orientamento dello Zener:** il catodo va verso R29/R30 (come D4), perché in entrambi i modi la soglia è la tensione di breakdown. Non verificabile dall'immagine; da controllare sul simbolo LCSC.
- **Rischio ponte su tre pad:** un ponte di stagno su tutti e tre i pad di H1/H3 porta +12 V sul morsetto IN; su H2/H4 porta IN a GND. Footprint a tre pad **senza traccia di default** fra i pad, serigrafia chiara, pad ben distanziati.
- **Modo L, sovratensione su IN:** a +101 V, R29/R30 (0805) dissipano circa 0,9 W e il riflusso nel +12 V è di circa 10 mA: stessa classe di rischio accettato per R1 (REQ-EL-008). A +24 V il riflusso è circa 1,4 mA; a −16 V il LED conduce e preleva circa 3 mA dal +12 V. Nessun danno atteso, ma il rail deve essere la linea protetta, non quella verso la batteria.
- **Corrente del LED in modo L:** circa 0,7 mA con la board a 10 V e circa 1,2 mA a 14,6 V (stima su Vz 3,3 V, V_F circa 1,1 V). A 10 V il TLP293 lavora sotto 1 mA: da confermare con la simulazione A1 (V_OL sotto 0,8 V).

## Netlist del canale AUX1 (AUX2 identico)

| Net | Pin collegati |
|---|---|
| `IN_AUX1` | JP_A1.1 — JP_B1.3 |
| `+12V_BAT` | JP_A1.3 (rail protetto della board: **nome e sorgente da definire** nella sezione alimentazione, REQ-EL-002) |
| `GND` | JP_B1.1 — U.3 (emettitore) |
| `TOP1` | JP_A1.2 — R1.1 |
| `N1` | R1.2 — Zener.K |
| `N2` | Zener.A — U.1 (anodo LED) — D1.K |
| `BOT1` | JP_B1.2 — U.2 (catodo LED) — D1.A |
| `SIG_AUX1` | U.4 (collettore) — R_PU.1 |
| `+3V3` | R_PU.2 |

Componenti per canale: 5 come IN-CAB, più 2 jumper a 3 pad (footprint SolderJumper a 3 pad, nessun componente in BOM).

## Note
- **Due GPIO di ingresso in più** (SIG_AUX1, SIG_AUX2) da prevedere nell'assegnazione dei pin dell'MCU.
- **Layout:** TOP, N1, N2 e BOT e i jumper portano fino a 101 V nel load dump. Valgono le stesse distanze dei nodi N1/N2 degli altri canali; i pad dei jumper vanno tenuti lontani dalle tracce lato MCU.
- **Serigrafia:** accanto ai jumper una tabellina "H: A1-2 B1-2 / L: A2-3 B2-3", per non doversi ricordare la configurazione.
