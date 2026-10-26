# Schematico A3 — Ingresso sonda serbatoio acque grigie (specifica di disegno)

Requisito: REQ-IF-011 (Open). Punto aperto: OPEN-14. **Tutto il dimensionamento poggia su ipotesi Assumed**: nessuna misura sulla sonda reale, nessun dato CBE (il manuale descrive solo una "sonda a viti SS/P", morsetto 13 del DS300).

## Ipotesi (tutte Assumed, da chiudere con OPEN-14)

| # | Ipotesi | Se falsa |
|---|---|---|
| H1 | Sonda = **due elettrodi (viti) isolati dalla massa**, conducono attraverso l'acqua; nessuna elettronica attiva nella sonda | Se la sonda è un contatto secco/galleggiante: il circuito funziona lo stesso (R_w = 0 chiuso, ∞ aperto) |
| H2 | Sonda **spostata** sulla board (DS300 scollegato dal morsetto 13); nessun parallelo con il DS300 | Con il DS300 in parallelo il suo livello di eccitazione si somma: da misurare |
| H3 | R_w (sonda "bagnata") ≲ 26 kΩ; sonda "asciutta" ≫ 100 kΩ | Soglia tarabile in firmware (vedi sotto) |
| H4 | Cavo nell'abitacolo/lato batteria servizi, non sul +15 lato alternatore: nessun load dump ISO | Se no: R_p in 0805 non regge (stesso rischio di EL-008) |
| H5 | Eccitazione **impulsata in DC** (10 ms ogni 5 s, duty 0,2 %): corrosione/elettrolisi trascurabile | Se la sonda si sporca/ossida: valutare inversione di polarità (due GPIO) |

## Riscontri dai forum (2026-10-15, tutte fonti deboli, nessuna misura elettrica)

Thread camperonline: [sensori grigie e chiare (191904)](https://www.camperonline.it/forum/tecnica/cellula-abitativa/sensori-serbatoio-acque-grigie-e-acqua-chiara/191904), [sensore grigie (92224)](https://www.camperonline.it/forum/tecnica/cellula-abitativa/sensore-grigie/92224), [led rosso grigie (174565)](https://www.camperonline.it/forum/tecnica/accessori/led-rosso-acque-grigie-sempre-acceso/174565).
- **Confermano H1 (qualitativamente):** sonda = due viti (una dice d'ottone) avvitate orizzontalmente nel serbatoio all'altezza del "troppo pieno", un filo per vite verso la centralina; il pieno è dato dall'acqua che chiude il circuito fra le viti.
- **Segnale a corrente "molto bassa"** (un utente, senza misura): coerente con l'eccitazione a bassa corrente; i contatti ossidati danno falsi stati.
- **Prova a vuoto:** staccando i fili dalle viti la spia si spegne ⇒ circuito aperto = "vuoto", come nel mio schema.
- **Guasto più comune: falso "pieno"** per patina di grasso/amido conduttiva sulle viti, anche a serbatoio vuoto; rimedi: aceto/acido citrico, viti più lunghe o più corte, sposta una vite più in alto. Conferma il rischio 3 sotto.
- **Non trovato:** tensione, corrente, soglia di resistenza, polarità. Un solo utente (su un Mobilvetta, non CBE) descrive "positivo alla spia, negativo di ritorno dalla vite": non misurato, e non dice se una vite sia a massa.
- Nel mio schema l'elettrodo B è a GND: resta compatibile anche se una vite fosse a massa carrozzeria.

## Principio

Misura resistiva a partitore **impulsata**: il GPIO `GRY_DRV` eccita il nodo per 10 ms, l'ADC1 legge `GRY_SNS` a regime, poi `GRY_DRV` torna basso. A riposo la sonda non ha tensione.

```
GRY_DRV ─ Rs 10k ─┬───────────┬── Rp 10k ── J.1 (elettrodo A)
(GPIO out)        │           │
   │            Rg 27k      D1 BAT54S (clamp a +3V3 e GND)
Rpd 100k          │           │
   │             GND         GRY_SNS ──┬── GPIO ADC1
  GND                                  └── C1 100 nF ── GND
                                   J.2 (elettrodo B) ── GND
```

`N` = nodo comune a Rs, Rg, Rp, D1, ADC (un solo nodo).

## Designatori nel foglio EasyEDA (2026-10-15, da screenshot dell'utente)

Net `WASTE_TANK_CMD` (= `GRY_DRV`), `WASTE_TANK_SENSE` (= `GRY_SNS`). Corrispondenze: Rs = **R33**, Rpd = **R34**, Rp = **R35**, Rg = **R36** (corretto da U8), C1 = **C7**, D1 = **D18** (BAT54S), connettore = **P3** "Waste Water Tank" (pin 1 = elettrodo A via R35, pin 2 = elettrodo B). Foglio rev. 2 (2026-10-15): aggiunta **R37 = 2,2 kΩ** in serie fra P3.2 e GND (protezione del ritorno: a 12 V sul filo 2 ⇒ 5,5 mA, 65 mW; a 24 V ⇒ 260 mW, oltre il limite di un 0805, quindi vale per guasti fino a ~16 V). Il simbolo di D18 sembra corretto (comune sul nodo N, diodo superiore verso +3V3, inferiore verso GND): da confermare sui pin del footprint.

**Effetto di R37 sui livelli** (ricalcolato): la resistenza vista dal nodo diventa Rp + R_w + R37. Asciutto invariato 2,41 V; elettrodi in corto 1,51 V (era 1,39); soglia 2,0 V a R_w ≈ 24 kΩ (era 26 kΩ). Guasto cavo < 0,5 V invariato.

## Distinta (tutto **Proposto**, nessun P/N verificato)

| Des. | Valore | Package | Funzione |
|---|---|---|---|
| Rs | 10 kΩ 1 % | 0805 | eccitazione + partitore |
| Rg | 27 kΩ 1 % | 0805 | porta il livello "asciutto" sotto 2,45 V (convenzione ADC) |
| Rp | 10 kΩ 1 % | 0805 | **protezione di campo**: limita la corrente di guasto verso il clamp (24 V ⇒ 2 mA, 57 mW) |
| D1 | doppio Schottky serie BAT54S (SOT-23) | SOT-23 | clamp N verso +3V3 e GND. **P/N non verificato su datasheet** |
| C1 | 100 nF | 0603/0805 | filtro ADC; τ = (Rs‖Rg‖…) × C1 ≈ 0,7 ms |
| Rpd | 100 kΩ | 0805 | `GRY_DRV` a massa in reset (stato sicuro, SW-002) |
| J | 2 poli | — | connettore di campo: **da decidere** nella sezione connettori |

## Livelli calcolati (ricalcolati, Vdd = 3,3 V)

Nodo N = 3,3 V · X/(Rs+X), con X = Rg ‖ (Rp+R_w):

| Condizione | R_w | V(GRY_SNS) |
|---|---|---|
| Asciutto / cavo aperto | ∞ | **2,41 V** (≤ 2,45 V ✓) |
| Bagnato | 1 kΩ | 1,45 V |
| | 10 kΩ | 1,76 V |
| | 26 kΩ | **2,00 V** (soglia proposta) |
| | 70 kΩ | 2,21 V |
| Elettrodi in corto | 0 | 1,39 V |
| **Guasto: N a massa (cavo in corto a GND)** | — | < 0,5 V (impossibile in uso normale: minimo 1,39 V) |

Corrente massima in eccitazione: 0,19 mA. Corrente in guasto 24 V sull'elettrodo: 2,0 mA (Rp), −16 V: 1,6 mA.

## Firmware (proposta)

- Ogni 5 s: `GRY_DRV` alto, attesa 5 ms (> 7 τ), lettura ADC1 (11 dB, media di 8 campioni), `GRY_DRV` basso.
- Stati: V < 0,5 V ⇒ **guasto cavo**; 0,5 ≤ V < 2,0 V ⇒ **pieno**; V ≥ 2,0 V ⇒ vuoto. Isteresi ±0,1 V, conferma su 3 letture. Soglie in `substitutions`, tarabili.
- Pubblicare anche il valore grezzo in HA per tarare la soglia sul pezzo reale.

## Limiti noti (rischi)

1. **Contrasto ridotto per R_w alta**: da 26 kΩ (2,00 V) a ∞ (2,41 V) ci sono solo 0,4 V; con isteresi ±0,1 V il margine sulla soglia è modesto. Colpa del vincolo ADC ≤ 2,45 V con eccitazione a 3,3 V. Se la sonda reale ha R_w alta, abbassare Rs o alzare la soglia dopo la misura.
2. **Cavo interrotto = "vuoto"**: lo stato "vuoto" non distingue sonda asciutta da filo staccato (non rilevabile con questo schema).
3. **Sonda sporca/ossidata** (biofilm, calcare) può dare R_w bassa a serbatoio vuoto ⇒ falso "pieno"; l'ossidazione delle viti dà l'errore opposto (testimoniato su forum, fonte debole).
4. R_w e il comportamento della sonda sono **ipotesi**: nessuna misura finora.
5. Pin GPIO: **`GRY_DRV` su GP15 del C6-Zero (pin senza pull al reset)**, assegnato il 2026-10-26 in `a8_mappa_pin.md`; la lettura `GRY_SNS` è sull'ADS1115 #2. Su un pin con weak pull-up (GP18…23) R34 100 kΩ darebbe ≈ 2,28 V sul nodo al reset e la sonda sarebbe eccitata in DC per tutto il boot: [verifica](../../hardware/schematic/a8_verifica_stato_reset.md).

## Rilettura dal vivo con il tool EasyEDA (2026-10-17)
Dalle proprietà dei componenti sul foglio (la connettività non è verificabile via MCP: lo snapshot vede solo 49 pin e 17 fili su 152 componenti):
| Des. | Valore e parte | Coerenza con la distinta |
|---|---|---|
| R33 (Rs) | 10 kΩ ±1 %, Uni-Royal 0805W8F1002T5E, 0805 | ✓ |
| R34 (Rpd) | 100 kΩ ±1 %, FOJAN FRC0805F1003TS, 0805 | ✓ |
| R35 (Rp) | 10 kΩ ±1 %, Uni-Royal 0805W8F1002T5E, 0805 | ✓ |
| R36 (Rg) | 27 kΩ ±1 %, FOJAN FRC0805F2702TS, 0805 | ✓ |
| R37 | 2,2 kΩ ±1 %, Uni-Royal 0805W8F2201T5E, 0805 | ✓ (65 mW a 12 V; oltre 16 V supera il limite dell'0805, già documentato) |
| C7 (C1) | 100 nF X7R, YAGEO CC0805KRX7R9BB104, 0805 | ✓ |
| D18 (D1) | BAT54S, **baocheng** (LCSC C51898308), SOT-23: V_R 30 V, I_F 200 mA, I_R 2 µA a 25 V (dalla scheda LCSC) | ✓ per valori; è un clone di marca poco nota, **non verificato sul datasheet del costruttore** |
| P3 | **JILN JL500-50802G01, morsetto a vite 5,08 mm** (LCSC C709041), commento "Waste Water Tank" | il connettore "da decidere" è stato scelto: morsetto a vite, non JST XH |
Punti ancora aperti: pin GPIO/ADC1 non assegnati; polarità del simbolo D18 da confermare sul footprint; connettività da confermare a mano (screenshot) perché il tool non la risolve.
