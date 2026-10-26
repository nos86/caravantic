# A8 — Verifica dell'impatto dei weak pull-up al reset sulle uscite (a2, a3, a4, a6, pistone, relè)

Requisito: REQ-SW-002 (stato sicuro per sole reti passive). Stato: **Proposto**, 2026-10-26. Base: datasheet ESP32-C6 v1.5 (vedi [`a8_esp32_c6_zero_pinout.md`](a8_esp32_c6_zero_pinout.md) §4): GPIO18…23 hanno il weak pull-up **già durante il reset**, GP6/GP9/GP17 e GP16 (uscita alta) dopo il reset; **R_PU tipico 45 kΩ, nessun min/max**. GPIO0…5, 7, 14, 15: nessun pull. Circuiti letti dai fogli a2, a3, a4, a6 (valori da documento, non riletti su EasyEDA, non connesso).

## 1. Metodo

Un GPIO con weak pull-up e una rete verso massa formano un partitore a partire da 3,3 V: V = 3,3 V × R_giù / (R_PU + R_serie + R_giù). Sensibilità: R_PU tipico 45 kΩ; il datasheet non dà gli estremi, quindi ho calcolato anche 30 kΩ e 70 kΩ come ipotesi.

## 2. Esito per stadio

| Stadio (net) | Rete verso massa | V al gate/nodo con weak pull-up (R_PU 45 kΩ; 30 / 70 kΩ) | Conseguenza se su pin con pull-up | Su quale pin è ora |
|---|---|---|---|---|
| Valvola `OUT_VALVE_OPEN/CLOSE` (a2): R15/R26 1 kΩ + R14/R25 47 kΩ → BSS138 Q3/Q6 | 47 kΩ | **1,67 V** (1,99 / 1,30 V) | **supera la soglia del BSS138 (0,8 / 1,3 / 1,5 V a 1 mA, onsemi, letto in a6): Q3/Q6 conduce → Q5/Q7 → la valvola si muove al reset/boot** | GP4 / GP5: **nessun pull, OK** |
| Inverter `CMD_INVERTER_CTRL/STATE` (a6): R50/R60 1 kΩ + R49/R59 47 kΩ → BSS138 Q4/Q8 | 47 kΩ | **1,67 V** (idem) | **K2 e K3 si eccitano al boot: remote scollegato dall'inverter e +12 V su VIN, inverter acceso** (viola IF-007 d) | GP4 / GP5: **OK** |
| Relè generici `DO1…4` (EL-005): BSS138 + pull-down di gate (valore ancora da disegnare; rev. 1: 100 kΩ) | 100 kΩ (se come rev. 1) | 2,28 V | **I relè si eccitano al boot** | GP0…GP3: **OK** |
| Pistone `OUT_LINEAR_MOTOR_DIR/ENA` (R6/R5, R9/R10…): rete simile | 47 kΩ ecc. | ≈ 1,7 V | bobina K1 / abilitazione Q2: **comando indesiderato al boot** | GP7 / GP14: **OK** |
| RS485 DE/RE | pull-down passivo | dipende dal valore | driver RS485 abilitato al boot (collisione sul bus) | GP15: **OK** |
| Relè globale (NEW-2) | pull-down passivo | idem | stacco/attacco indesiderato dei servizi | GP7 (elettrica): **OK** |
| `SIG_INVERTER_GREEN/RED` (a6): nodo con pull-up 12 kΩ (R55/R56), gate di Q9/Q10 (PMOS) | verso 3V3 | resta alto | **nessuno**: alto = specchio LED spento | GP6 / GP20 (weak pull-up): **OK** |
| Eccitazione sonda grigie `WASTE_TANK_CMD` (a3): GPIO → Rs 10 kΩ, Rpd R34 100 kΩ | 100 kΩ | **2,28 V** (2,54 / 1,94 V) sul nodo GRY_DRV | sonda alimentata a DC da ≈ 2,28 V attraverso Rs: corrente ≤ circa 0,13 mA per la durata di reset + avvio (da misurare, ordine di 1 s). Mai pericolosa; contraria al principio a3 "a riposo la sonda non ha tensione" e alla ipotesi H5 (elettrolisi in DC) | **spostata su GP15 (sicuro)**, vedi §3 |
| Eccitazione livello `CLEAN_TANK_CMD` (a4): D20 1N4148WS + R38 300 Ω + R40 3,9 Ω + sender 0–190 Ω, Rpd R39 (100 kΩ al foglio) | 100 kΩ | **2,28 V** sul nodo LVL_EN → ≈ 5,5 mA nel sender a 0 Ω … ≈ 3,5 mA a 190 Ω (V_F di D20 ≈ 0,6 V) | corrente continua nel sender per tutto il reset/boot: **dentro H2 (≤ 9,5 mA)**, ma OPEN-15 (corrente massima tollerata dal sender) non è chiuso | GP21 (weak pull-up): **accettabile**, vedi §3 |
| Ingressi opto (`SIG_CAB`, `SIG_CEL`, `SIG_AUX1/2`, `SIG_INVERTER_12V/REQ`): pull-up 12 kΩ a 3V3 | verso 3V3 | resta alto | **nessuno**; il weak pull-up in parallelo aumenta il carico del collettore dell'opto da 0,28 a 0,35 mA a nodo basso (+27 %) | vedi §4 |
| I²C (SDA/SCL, pull-up 2,2 kΩ), 1-Wire (4,7 kΩ), UART (GP16/17) | verso 3V3 | resta alto | **nessuno** | GP16…GP22 |

## 3. Scelte di mappa che ne derivano (applicate in `idraulica/schematic/a8_mappa_pin.md`)

- **Tutte le uscite attive alte su pin senza pull** (valvola, pistone, 4 relè, inverter, relè globale, DE/RE): già così.
- **`WASTE_TANK_CMD` passa su GP15** (pin sicuro di scorta dell'idraulica). `SIG_AUX2` resta su GP23 (ingresso, innocuo). GP22 diventa libero.
- **`CLEAN_TANK_CMD` resta su GP21 (weak pull-up)**: unica uscita "attiva" su pin con pull-up. Accettabile perché la corrente al boot (≈ 3,5…5,5 mA) è sotto il limite H2. **Per azzerare il problema:** R39 da 100 kΩ a ≤ 4,7 kΩ ⇒ nodo LVL_EN a ≈ 0,3 V, sotto la soglia di D20 (nessuna corrente); costo: 0,7 mA a GPIO alto. Decisione all'utente.

## 4. Mitigazioni firmware (Assumed)

1. **Disattivare il weak pull-up interno** sui pin che hanno già un pull-up esterno (GP6, GP20, GP23, I²C, 1-Wire): in ESPHome `pullup: false` (da verificare sul C6 con `INPUT_OUTPUT_OD`). Riduce il carico sul collettore degli opto e sul 3V3.
2. Imporre le uscite a livello basso appena possibile: `setup_priority` alta e `restore_mode: ALWAYS_OFF` sugli switch; non coprono la finestra di reset e bootloader (nessun codice utente in esecuzione), quindi **la protezione di REQ-SW-002 resta sulle reti passive**.
3. Durata della finestra pull-up + avvio: **non misurata**. Da misurare con un oscilloscopio su un GPIO di prova (reset e avvio a freddo).

## 5. Cose che questa verifica non copre

- **Schema Waveshare letto (2026-10-26, netlist testuale)**: nessun resistore sui pin GP0…7, 14, 15, 18…23. Chiusa l'incertezza sui pin "sicuri". Resta una lettura da testo, non dal disegno.
- Le reti di pull-down di `DO1…4` e dei gate del pistone sono ricavate da rev. 1 / dal registro componenti, non dalla netlist EasyEDA (non connessa in questa sessione).
- Il fronte di salita del 3V3 all'accensione e la sequenza in cui i pin passano da alta impedenza a weak pull-up non sono documentati nel datasheet letto.
- R_PU min/max: non dichiarati; i valori 30/70 kΩ sono ipotesi di sensibilità.
