# Schematico A7 — Sensoristica di bordo: IMU (assetto) e magnetometro (heading)

Requisiti: REQ-IF-001 (assetto ≤ 1°, heading ≤ 5°, driver ESPHome nativo; Confirmed 2026-10-22). Componenti **congelati il 2026-10-22** su conferma utente: **STMicroelectronics LSM6DSOX** (U23) e **MEMSIC MMC5983MA** (U22), voci in [`docs/components.md`](../../docs/components.md). Il circuito qui sotto è **Proposto** (Assumed): ricavato dagli schemi applicativi dei datasheet, non simulato né provato. Designatori: **non ancora assegnati**, si prendono nell'editor (nomi provvisori `U23`, `U22`, `C_*`, `R_SDA`, `R_SCL`). Pin GPIO: non assegnati. Il GPS (REQ-IF-002) non è in questo foglio. L'MCP `easyeda-pro` non era raggiungibile: il foglio **non è stato disegnato in EasyEDA**, questa è la specifica da riportare.

## Ipotesi (tutte Assumed)

| # | Ipotesi | Se falsa |
|---|---|---|
| H1 | Entrambi i chip stanno sulla scheda principale, sul bus I²C comune già usato dall'INA219 (A4) | Se il magnetometro va su una scheda satellite (H3), servono connettore I²C e cavo corto con pull-up valutati sulla capacità del cavo |
| H2 | Alimentazione dei due chip dalla 3V3 della scheda (VDD = VDDIO = 3,3 V) | Nessun regolatore dedicato: se la 3V3 sale in più di 5 ms il MMC5983MA non è garantito (vedi rischio 3) |
| H3 | **Decisione utente 2026-10-22:** il magnetometro sta sulla scheda principale, in un angolo lontano dai relè (vincoli in "Vincoli di layout") | Se i vincoli non si rispettano a layout: scheda satellite sul bus I²C |
| H4 | I pull-up del bus I²C sono su questo foglio (A4, punto 5, li rimanda qui) | Il bus resterebbe senza pull-up |
| H5 | I²C a 400 kHz con 3 slave e tracce corte (capacità totale ≲ 70 pF) | Se la capacità è maggiore: 100 kHz o pull-up più bassi |

## Bus I²C e indirizzi

| Dispositivo | Indirizzo 7 bit | Fonte |
|---|---|---|
| U23 LSM6DSOX, SA0 → GND | **0x6A** | datasheet ST DS12814 (LSM6DSOX) Rev 3, gennaio 2019, sezione I²C (SAD = 110101x; D4h/D5h con SA0 = 0, D6h/D7h con SA0 = 1 secondo la tabella degli indirizzi) |
| U22 MMC5983MA | **0x30** | datasheet MEMSIC Rev A, p. 17 |
| U_LVL INA219 (A4) | 0x40 | già registrato in `idraulica/components.md` |

Nessun conflitto. Il default del driver ESPHome `lsm6ds` è 0x6A.

## Schema

```
        3V3
         │
    ┌────┴─────┬───────────────────────────┐
    │          │                           │
   R_SDA      R_SCL                        │            (pull-up unica coppia del bus)
   4,7 kΩ     4,7 kΩ                       │
    │          │                           │
 SDA┴──────────┼──── SDA   U23  LSM6DSOX  │   U22  MMC5983MA
 SCL───────────┴──── SCL   (LGA-14L)       │   (LGA-16)
                                           │
 U23 (LGA-14L)                      U22 (LGA-16)
  1 SDO/SA0 ── GND (0x6A)              1 SCL ── SCL           16 SDA ── SDA
  2 SDx ────── GND                     2 VDD ── 3V3 + C 1 µF  15 INT ── non collegato
  3 SCx ────── GND                     4 SPI_CS ─ VDDIO       10 CAP ── C 10 µF verso GND
  4 INT1 ───── non collegato           9, 11 GND              13 VDDIO ─ 3V3 + C 100 nF
  5 VDDIO ──── 3V3 + C 100 nF          3, 5-8, 12, 14 NC (lasciare scollegati)
  6, 7 GND
  8 VDD ────── 3V3 + C 100 nF
  9 INT2 ───── non collegato
 10 OCS_Aux ── non collegato (saldato)
 11 SDO_Aux ── 3V3 o non collegato
 12 CS ─────── 3V3 (abilita I²C)
 13 SCL ────── SCL     14 SDA ── SDA
```

Collegamenti ricavati da: LSM6DSOX Tab. 1 (pin) e §7.1 (modo 1, I²C: SDx/SCx a VDDIO o GND, CS a VDDIO, OCS_Aux scollegato, 100 nF su VDD e VDDIO); MMC5983MA schemi "I²C Dual Supply Connection" e descrizione pin (SPI_CS a VDDIO per l'I²C, CAP ≥ 10 µF a bassa ESR vicino al pin).

## Componenti passivi (valori Assumed)

| Rif. provv. | Funzione | Valore | Note |
|---|---|---|---|
| R_SDA, R_SCL | Pull-up bus I²C | 4,7 kΩ, 0805 | Il datasheet ST mostra 10 kΩ; con 400 kHz e ~50–70 pF il tempo di salita (≈ 0,85·R·C, ~0,2–0,3 µs per R = 4,7 kΩ) resta entro il limite di 300 ns dello standard I²C Fast-mode (valore **da memoria**, UM10204 non letta). 10 kΩ darebbe ~0,6 µs a 70 pF: ammesso solo a 100 kHz |
| C19 (VDD), C18 (VDDIO) | Disaccoppiamento LSM6DSOX | 100 nF, 0603 | Raccomandati da ST (§7.1), vicino ai pin 5 e 8 |
| C16 | Disaccoppiamento VDD MMC5983MA | 100 nF (disegnato; la specifica diceva 1 µF) | Lo schema MEMSIC mostra 1 µF su VDD. Qui VDD e CAP stanno sullo stesso nodo 3V3 (sono cortocircuitati nel chip) e C20 da 10 µF fa da riserva, quindi 100 nF per le alte frequenze è accettato (Assumed) |
| C17 | Disaccoppiamento VDDIO MMC5983MA | 100 nF, 0603 | Ipotesi mia, non riportata nello schema MEMSIC letto |
| C20 | Bobina SET/RESET (pin CAP, collegato al nodo 3V3 nello schema disegnato) | **10 µF, X5R/X7R ≥ 10 V, 0805 o 1206**, bassa ESR | MEMSIC: "minimum 10 µF low ESR". La capacità effettiva a 3,3 V scende con la polarizzazione DC (ceramiche): verificare sulla curva del costruttore scelto che resti ≥ 10 µF |

Condensatori e resistori sono stati scelti nel rispetto del package ≥ 0603 delle convenzioni. Nessun ferrite bead né induttore vicino al magnetometro (materiale ferromagnetico).

## Risorse MCU

| Segnale | Tipo | Vincolo |
|---|---|---|
| SDA / SCL | I²C comune (U23, U22, U_LVL) | Non su pin di strappo (GPIO0, 3, 45, 46); non GPIO14 (LED RGB del modulo). Pin da assegnare nell'editor |
| INT1, INT2 (IMU), INT (MAG) | Non collegati | Il polling di ESPHome basta; nessun GPIO consumato |

## Rischi e punti aperti

1. **Posizione del magnetometro (H3): decisa dall'utente il 2026-10-22, sulla scheda principale in un angolo lontano dai relè.** Vedi "Vincoli di layout". Rischio residuo: la distanza non basta contro le correnti del pistone (stima sotto), quindi il firmware deve escludere le letture durante i carichi forti. Il MMC5983MA ha un campo di disturbo di 10 G oltre il quale serve un SET/RESET di ripristino (datasheet, nota 6).
2. **Budget dell'heading.** Errore di allineamento degli assi del chip: 1° tip. / 3° max (MEMSIC, tabella Specifications). I ±5° restano raggiungibili solo con calibrazione hard-iron/soft-iron sul camper montato. Il driver ESPHome `mmc5983` fa solo RESET a ogni lettura e non calcola l'heading: heading, calibrazione e compensazione dell'inclinazione vanno scritti nel firmware (vedi sotto).
3. **Rampa dell'alimentazione.** Il datasheet MEMSIC indica un tempo di salita dell'alimentazione ≤ 5 ms. Non so quanto sale la 3V3 della scheda (Waveshare ESP32-S3-Tiny): **da misurare** o da leggere sul datasheet del regolatore. Con C_MAG_CAP da 10 µF la rampa dipende anche dal carico.
4. **Offset dell'accelerometro.** ±20 mg tip. (1,15°) per LSM6DSOX: serve taratura dello zero a camper livellato; non si può omettere se vale il requisito ≤ 1°.
5. **Orientamento relativo degli assi.** IMU e magnetometro vanno montati con gli assi allineati (stesso orientamento) per la compensazione dell'inclinazione: gli assi di ciascun package vanno letti sui disegni dei datasheet (non ancora annotati qui) e riportati sulla serigrafia. L'asse X dell'IMU va orientato rispetto alla marcia del camper.
6. **Package LGA a pad nascosti** (LSM6DSOX 14 pad 2,5×3 mm, MMC5983MA 16 pad 3×3 mm): reflow con stencil, non saldabile a mano. Scostamento dalla convenzione "assemblaggio manuale + reflow": da confermare.
7. **Footprint EasyEDA**: non verificato per entrambi i chip; codice LCSC dell'LSM6DSOXTR **da trovare** (C2655100 è dell'LSM6DSOTR), C404329 per il MMC5983MA con stock non confermato.
8. **Capacità del bus (H5)**: non calcolata. Da stimare a layout (INA219 + due chip + tracce + eventuale connettore).
9. **Schema U23 come disegnato dall'utente (2026-10-22): SDO/SA0 (pin 1) è scollegato (marcatore X).** L'ultimo bit dell'indirizzo I²C resta indefinito (il pin è un ingresso senza pull-up): **va collegato a GND** per 0x6A, come previsto in questa specifica. Il resto dello schema (SDx/SCx a GND, CS a 3V3, 100 nF su VDD e VDDIO, INT1/INT2/SDO_Aux/OSC_Aux non collegati) è conforme. Verificare in EasyEDA che l'incrocio del filo di VDDIO sul pin 5 con la linea di GND non abbia un punto di giunzione. I pull-up non erano visibili nel ritaglio.
10. **Schema U22 come disegnato dall'utente (2026-10-22): conforme.** SCL/SDA ai pin 1 e 16, VDD a 3V3 con C16, SPI_CS a 3V3, VDDIO a 3V3 con C17, CAP al nodo 3V3 con C20 10 µF verso GND (ammesso per deduzione dalla nota MEMSIC "VDD and CAP pins are shorted together inside the device"; **non verificato sulla figura** dello schema applicativo, non leggibile dal testo estratto del PDF: il datasheet raccomanda solo i 10 µF sul pin CAP e non dice se collegare CAP al 3V3), GND ai pin 9 e 11, pin NC e INT con la X. Da controllare in EasyEDA: la linea SDA orizzontale incrocia la verticale di SCL verso U23 senza punto di giunzione (SCL e SDA non devono toccarsi); il tipo di C20 (X5R/X7R ≥ 10 V, capacità effettiva a 3,3 V).

## Vincoli di layout del magnetometro (decisione utente 2026-10-22; distanze Assumed)

Stima dell'ordine di grandezza (mia, non misurata): un filo rettilineo con corrente I a distanza r produce B = μ₀·I / (2π·r). Con la componente orizzontale del campo terrestre assunta ≈ 22 µT (valore **da memoria** per l'Italia, da verificare con un modello come WMM), un errore di heading di 5° corrisponde a un disturbo di circa 2 µT nel piano orizzontale. Per I = 10 A servirebbero r ≈ 1 m; a 3 cm il disturbo sarebbe ~67 µT, più del campo terrestre. Conseguenza: **la distanza sulla scheda attenua i relè e i segnali, non le correnti del pistone**; quelle si gestiscono nel firmware (punto 8).

*Shall (vincolanti):*
1. U22 nell'angolo della scheda **più lontano da tutti i relè** (K-PH, K2/K3, i 4 relè generici) e dal ponte H/MOSFET del pistone. Distanza minima dai relè: **≥ 30 mm dal corpo del relè più vicino (Assumed, da validare con la misura al banco)**.
2. **Nessuna pista di potenza** (pistone, valvola, ingresso batteria, 12 V di carico) a meno di **10 mm** dal chip, né sotto di esso su nessun layer. Le piste di corrente che non si possono allontanare si fanno **in coppia andata/ritorno affiancate**, per ridurre il campo esterno.
3. **Nessun materiale ferromagnetico entro 15 mm (Assumed):** niente ferrite bead, induttori con nucleo, schermi in acciaio, connettori con corpo in acciaio, viti/distanziali in acciaio, magneti (buzzer, altoparlanti, relè reed). Scegliere pastiglie e distanziali in ottone, alluminio o plastica.
4. **Piano di massa sotto il chip senza correnti di ritorno forti**: tagliare la corrente di ritorno dei carichi altrove (massa a stella già prevista per gli shunt, A5).
5. **Condensatore CAP da 10 µF** vicinissimo al pin 10, ma con tracce corte: i picchi di corrente di SET/RESET (500 ns) non devono percorrere anelli grandi.

*Dovrebbe (raccomandazioni):*
6. U23 **vicino a U22** e con la stessa orientazione degli assi (per la compensazione dell'inclinazione), ma l'IMU non è sensibile ai campi: la sua posizione è libera dentro quella zona.
7. Zona del chip libera da componenti pesanti, vicino al bordo scheda, lontano dal connettore dei carichi; serigrafia con la freccia dell'asse X rivolta verso la marcia del camper e l'orientazione del chip.
8. **Firmware:** non aggiornare l'heading mentre pistone, valvola o altri carichi ≥ ~1 A sono attivi (stato noto dal firmware e dalla corrente degli shunt), oppure compensare con la corrente misurata; riportare l'ultimo heading valido. Eseguire la calibrazione con i relè in stato noto e ripeterla se cambia.

*Verifica a banco (aggiunta all'acceptance):* [B] con la scheda ferma e orientata, la variazione del campo magnetico misurato (modulo) fra carichi spenti e ciascun carico acceso resta **< 2 µT** (Assumed, deriva dal budget di 5° sopra); se no, riposizionare U22 o passare al satellite.

## Firmware ESPHome (sintesi, non provato)

- `i2c:` a 400 kHz sui pin assegnati.
- `lsm6ds` (categoria `motion`, indirizzo 0x6A), accelerometro a ±2 g o ±4 g; roll/pitch dalle accelerazioni. Il giroscopio non serve: spegnerlo/ignorarlo.
- `mmc5983` per il campo X/Y/Z (indirizzo 0x30). Heading: calcolato con un `template` sensor partendo da campo calibrato e inclinazione. Eventuale componente esterno per la sequenza SET/RESET completa.
- Calibrazione: offset dell'accelerometro (livellamento) e matrice/offset del magnetometro (rotazione del camper a 360°), salvati in configurazione.

## Verifica (acceptance di REQ-IF-001)

- [B] Roll e pitch entro ±1° rispetto a una livella digitale, camper fermo.
- [B] Heading entro ±5° rispetto a una bussola di riferimento dopo calibrazione, con carichi spenti e accesi (relè e pistone in azione).
- [B] Lettura stabile con INA219 sullo stesso bus a 400 kHz; forme d'onda SDA/SCL con tempo di salita misurato.
