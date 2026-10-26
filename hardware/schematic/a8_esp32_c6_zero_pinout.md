# A8 — ESP32-C6-Zero: pin disponibili (comune alle due schede)

Requisiti: REQ-SW-001 (un ESP32-C6-Zero per scheda), REQ-SW-002. Stato: **Proposto / Assumed**, rev. 2026-10-26 (strapping e stato al reset chiusi sul datasheet). Sostituisce, per il modulo, la sezione 1 della vecchia [`a8_mappa_pin.md`](a8_mappa_pin.md) (ESP32-S3-Tiny, superata).

## 1. Fonti e cosa è verificato

| Dato | Fonte | Peso |
|---|---|---|
| Pinout delle 22 GPIO: immagine [ESP32-C6-Zero_Pin.png](https://www.waveshare.com/w/upload/2/2e/ESP32-C6-Zero_Pin.png), letta il 2026-10-26 | Waveshare | primaria |
| Strapping, stato dei pin al reset, R_PU, mappa SDIO, UART, ADC: **datasheet ESP32-C6 Series v1.5** (`documentation.espressif.com/esp32-c6_datasheet_en.pdf`), testo estratto con `pdftotext`: §3 Boot Configurations (Tab. 3-1…3-7), §2.2 Pin Overview (Tab. 2-1/2-2 e note 4–6), §2.3.4/2.3.5 restrizioni dei GPIO, tab. DC (R_PU) | costruttore (Espressif) |
| GPIO12/13 usati dall'USB-JTAG; GPIO24…30 flash SPI | [ESP-IDF, GPIO & RTC GPIO](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/api-reference/peripherals/gpio.html) e datasheet §2.3.4 | primaria |

**Limiti di lettura:** le tabelle dei pin del datasheet si estraggono con le colonne "At Reset / After Reset" spostate; ho usato l'estrazione `-table` (righe coerenti fra QFN32 e QFN40) e il testo delle note. Le righe di GPIO0/GPIO1 e GPIO14 sono incomplete nell'estrazione (valore dato per **non pull** al reset, non verificato su immagine della pagina). **Schema Waveshare letto il 2026-10-26** ([ESP32-C6-Zero-Sch.pdf](https://files.waveshare.com/wiki/ESP32-C6-Zero/ESP32-C6-Zero-Sch.pdf), copia locale, testo e netlist estratti con `pdftotext`; il disegno non è stato visto come immagine): vedi §1.1. Il datasheet non dà R_PU min/max: solo tipico **45 kΩ**.

**Flash:** lo schema Waveshare e la wiki indicano ESP32-C6**FH4** (4 MB); la pagina prodotto dice FH8 (8 MB). Vale lo schema: **FH4, 4 MB** (la pagina prodotto è quindi in contrasto con lo schema; resta da confermare sul pezzo). Verificare anche che il link Amazon sia la **Zero** (5 V) e non la **Zero-B** (la pagina prodotto cita per la Zero-B un ingresso 5–36 V; lo schema letto ha l'LDO ME6217C33M5G alimentato da VBUS/5 V).

### 1.1 Cosa aggiunge la scheda ai pin (dalla netlist dello schema Waveshare)

| Pin | Componenti sulla scheda (oltre al modulo e al pad) |
|---|---|
| GP0…GP7, GP14, GP15, GP18…GP23 | **nessuno**: la rete contiene solo il pad e il pin del chip. Le conclusioni del §4 (pin "sicuri" e weak pull-up) non sono alterate dalla scheda |
| GP8 | LED WS2812B (DIN) e **R1 10 kΩ** (pull-up, dal valore letto; il collegamento a 3V3 non è stato visto) |
| GP9 | tasto BOOT e **R5 10 kΩ a 3V3** (pull-up) |
| GP12/GP13 | connettore USB-C (D−/D+) |
| GP16 (TX) | **R7 499 Ω in serie** fra il pin U0TXD del chip e il pad TX |
| GP17 (RX) | pad RX diretto |
| RESET | R6 10 kΩ a 3V3, tasto RESET, C16 |

Il nome del part number sul chip nello schema è ESP32-C6FH4. Lettura da netlist testuale: l'ordine dei pin nelle reti è stato interpretato (nome della rete dopo i suoi pin), non verificato a occhio sul disegno.

## 2. Pinout (letto dall'immagine)

| Lato | Pad (dall'alto) |
|---|---|
| Alimentazione | 5V, GND, 3V3(OUT) |
| Sinistro | GP0, GP1, GP2, GP3, GP4, GP5 (ADC su GP0…GP5) |
| Destro | TX (UART0, GP16), RX (UART0, GP17), GP14, GP15, GP18, GP19, GP20, GP21, GP22 |
| Retro (castellati) | GP13, GP12, GP23, GP9 (BOOT), GP8 (LED WS2812, DIN), GP7, GP6 (ADC) |

**Riservati:** GP8 (LED RGB e strapping ROM-print/boot), GP9 (tasto BOOT, strapping boot mode), GP12/GP13 (USB-C, USB-Serial-JTAG).

## 3. Strapping GP4 / GP5 / GP15: esito (datasheet v1.5, §3)

| Pin | Funzione di strapping | Default al reset | Conclusione |
|---|---|---|---|
| GP4 (MTMS), GP5 (MTDI) | solo **fronte di campionamento/pilotaggio SDIO** (Tab. 3-4); "MTMS e MTDI sono floating di default" | floating (nessun pull); abilitato solo l'ingresso | **Nessun effetto** senza SDIO (che non usiamo): liberi come I/O normali, **anche uscite** |
| GP15 | **sorgente JTAG** (Tab. 3-7), "non ha pull interni" | floating | Con le eFuse a valore di fabbrica (EFUSE_JTAG_SEL_ENABLE = 0, EFUSE_DIS_PAD_JTAG = EFUSE_DIS_USB_JTAG = 0) il valore è **ignorato**: libero. Se JTAG_SEL_ENABLE fosse bruciato a 1, GP15 dovrebbe essere pilotato da un circuito esterno mai in alta impedenza (un'uscita opto con pull-up va bene) |
| GP8 | ROM-print su UART0 (Tab. 3-5) + boot mode (Tab. 3-3) | floating | non usato |
| GP9 | boot mode: 1 = boot da SPI (default), 0 con GP8 = 1 = download | **weak pull-up** | non usato (tasto BOOT) |

Decisione: la regola "nessuna uscita sugli strapping" **vale solo per GP8 e GP9**; GP4, GP5 e GP15 sono usati come I/O generici. **Verifica sul pezzo:** leggere le eFuse (`espefuse summary`) per confermare i valori di fabbrica; MTMS/MTDI/MTCK/MTDO (GP4…GP7) sono anche i pin JTAG ma, di default, il JTAG è sull'USB-Serial-JTAG (Tab. 3-7, prima riga).

## 4. Stato dei pin al reset: nuova regola (cambia la mappa)

Dal datasheet (Tab. 2-1/2-2, note 4–6) e R_PU:

| GPIO | Stato al reset / dopo il reset | Uso come uscita di sicurezza |
|---|---|---|
| **0, 1, 2, 3, 4, 5, 7, 14, 15** | solo ingresso abilitato (IE) o alta impedenza; **nessun pull** | **sì (9 pin "sicuri")** |
| 6 (MTCK) | dopo il reset IE + **weak pull-up** (di default; con EFUSE_DIS_PAD_JTAG = 1 solo IE) | no |
| 9 (BOOT) | **weak pull-up** | non usato |
| 16 (U0TXD) | dopo il reset **uscita abilitata** + weak pull-up (idle alto; la ROM stampa i log di boot su UART0) | no |
| 17 (U0RXD) | IE + **weak pull-up** | no |
| **18…23** (pin SDIO) | **weak pull-up già durante il reset**; poi solo IE | no |

R_PU tipico **45 kΩ** (nessun min/max nel datasheet). Conseguenza progettuale: un gate con pull-down da 47 kΩ su uno di questi pin (come R49/R59 degli stadi relè dell'inverter) sale a ≈ 3,3 × 47/(45 + 47) ≈ **1,7 V** e può accendere un BSS138 (soglia dell'ordine di 1 V, dato non verificato qui) durante il reset e tutto il boot. **Le uscite che devono restare spente al reset stanno solo sui 9 pin sicuri.** Sugli altri pin vanno solo: ingressi, bus con pull-up esterno (I²C, 1-Wire), UART, segnali attivi bassi con pull-up (opto, specchio LED) e uscite di eccitazione non critiche (con pull-down ≤ 4,7 kΩ: ≈ 0,3 V con R_PU = 45 kΩ, sotto la soglia).

Verifica stadio per stadio (a2, a3, a4, a6, pistone, relè): [`a8_verifica_stato_reset.md`](a8_verifica_stato_reset.md).

## 5. Altre regole (Assumed)

1. **Mai usare GP8, GP9, GP12, GP13**: LED, BOOT e USB. L'USB serve per il primo flash e il debug; l'OTA via Wi-Fi viene dopo.
2. **Logger su USB-Serial-JTAG**, così GP16/GP17 (UART0) restano utilizzabili come UART dati. Il supporto ESPHome del logger su USB-Serial-JTAG per il C6 è **da verificare**. Nota: all'avvio la ROM stampa su UART0 (GP16): chi sta sull'altra parte della UART vede qualche riga di testo a 115200 baud.
3. **UART: due** (UART0, UART1) più una LP UART (datasheet §1): una per scheda (GPS sull'idraulica, RS485 sull'elettrica), con ampio margine.
4. **ADC:** SAR ADC a 12 bit, fino a 7 canali (datasheet §1; dal pinout Waveshare GP0…GP6). Nessun ingresso analogico sui GPIO nativi: restano ADS1115/INA219 su I²C.
5. **Deep sleep:** gli RTC GPIO sono GP0…GP7 (ESP-IDF, LP_GPIO0…7). Un nodo Zigbee end device alimentato dalla batteria di bordo non lo richiede; legato a OPEN-08.

## 6. Rischi comuni

- **Alimentazione:** 3V3 dall'LDO di bordo (ME6217C33M5G, 800 mA max: part number letto sullo schema Waveshare, corrente dalla pagina prodotto). Con il Wi-Fi in trasmissione il modulo assorbe una parte rilevante di quegli 800 mA: budget del 3V3 da fare (IMU, magnetometro, INA219, ADS1115, DS18B20, specchio LED); in caso di eccedenza serve un regolatore 3V3 sulla PCB. Il 5 V per il pin 5V viene da un convertitore dalla linea 12–14,6 V (non ancora scelto; tema di OPEN-08).
- **Antenna ceramica a bordo:** portata Zigbee in un vano metallico da provare (REQ-SW-001, rischio a).
- **Schema Waveshare letto:** nessun componente aggiuntivo sui pin usati dalla mappa (vedi §1.1). Un controllo con multimetro sul modulo reale resta consigliato.
