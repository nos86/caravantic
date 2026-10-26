# A8 — ESP32-C6-Zero: pin disponibili (comune alle due schede)

Requisiti: REQ-SW-001 (un ESP32-C6-Zero per scheda), REQ-SW-002. Stato: **Proposto / Assumed**. Sostituisce, per il modulo, la sezione 1 della vecchia [`a8_mappa_pin.md`](a8_mappa_pin.md) (ESP32-S3-Tiny, superata).

## 1. Fonti e cosa è verificato

| Dato | Fonte | Peso |
|---|---|---|
| Pinout delle 22 GPIO: immagine [ESP32-C6-Zero_Pin.png](https://www.waveshare.com/w/upload/2/2e/ESP32-C6-Zero_Pin.png), **letta direttamente il 2026-10-26** | costruttore (Waveshare) | primaria |
| GPIO12/13 usate dall'USB-JTAG; GPIO24…30 = flash SPI; GPIO0…7 = LP_GPIO0…7 | [ESP-IDF, GPIO & RTC GPIO, ESP32-C6](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/api-reference/peripherals/gpio.html) | primaria |
| GPIO4, 5, 8, 9 strapping (GPIO15 citato da un forum Arduino come ulteriore strapping) | stessa pagina ESP-IDF (4, 5, 8, 9); [forum Arduino](https://forum.arduino.cc/t/esp32-c6-usable-gpios/1350380) per il 15 | primaria / **debole** per GPIO15 |
| GPIO9 alto = boot da flash, GPIO9 basso + GPIO8 alto = download | [RIOT-OS](https://doc.riot-os.org/group__cpu__esp32__esp32c6.html) | secondaria |

**Non letti:** la tabella degli strapping del datasheet Espressif (livelli di default e significato di GPIO4/5/15), lo schema Waveshare `ESP32-C6-Zero-Sch.pdf` (scaricato, ma `pdftoppm` non è installato: non renderizzabile qui), il numero di UART e i canali ADC dal datasheet.

**Discrepanza da risolvere:** la wiki Waveshare dice ESP32-C6**FH4**, 4 MB di flash; la pagina prodotto dice ESP32-C6**FH8**, 8 MB. REQ-SW-001 riportava FH8/8 MB dalla pagina prodotto: **corretto in "FH4/FH8, da verificare sul pezzo"**. Verificare anche che il link Amazon dell'utente sia la variante **Zero** (5 V) e non la **Zero-B** (la pagina prodotto cita per la Zero-B un ingresso 5–36 V: prodotto diverso, non confondere).

## 2. Pinout (letto dall'immagine)

| Lato | Pad (dall'alto) |
|---|---|
| Alimentazione | 5V, GND, 3V3(OUT) |
| Sinistro | GP0, GP1, GP2, GP3, GP4, GP5 (ADC su GP0…GP5) |
| Destro | TX (UART0, GP16), RX (UART0, GP17), GP14, GP15, GP18, GP19, GP20, GP21, GP22 |
| Retro (castellati) | GP13, GP12, GP23, GP9 (BOOT), GP8 (LED WS2812, DIN), GP7, GP6 (ADC) |

Totale **22 GPIO**, coerente con la pagina prodotto. Riservati dalla scheda: **GP8** (LED RGB WS2812), **GP9** (tasto BOOT), **GP12/GP13** (USB-C, USB-Serial-JTAG).

## 3. Regole di assegnazione (Assumed)

1. **Mai usare GP8, GP9, GP12, GP13**: LED, BOOT e USB. Il USB serve per il primo flash e il debug; l'OTA via Wi-Fi viene dopo.
2. **Nessuna uscita su GP4, GP5, GP15** (strapping, regola di progetto): solo ingressi, e solo dopo aver letto i livelli di default sul datasheet. Un ingresso opto con pull-up a 3V3 su un pin di strappo può cambiare la configurazione di boot.
3. **Logger su USB-Serial-JTAG**, così GP16/GP17 (UART0 di default) restano utilizzabili come UART dati. Il supporto ESPHome del logger su USB-Serial-JTAG per il C6 è **da verificare**.
4. **Uscite verso gate/relè** su pin "puliti", con pull-down passivo sui gate (REQ-SW-002). Dopo il reset i GPIO del C6 sono ingressi: la tenuta dello stato sicuro resta alle reti passive.
5. **Pin puliti disponibili (15):** GP0, 1, 2, 3, 6, 7, 14, 16, 17, 18, 19, 20, 21, 22, 23. **Solo ingresso (3):** GP4, 5, 15.
6. Nessun ingresso analogico sui GPIO nativi: restano gli ADS1115/INA219 su I²C (invariato rispetto alla vecchia a8).
7. Risveglio da deep sleep: gli RTC GPIO sono GP0…GP7. Un nodo Zigbee end device alimentato dalla batteria di bordo non lo richiede; resta legato a OPEN-08.

## 4. Rischi comuni

- **Alimentazione:** 3V3 dall'LDO di bordo (ME6217C33M5G, 800 mA max, dalla pagina prodotto; **non** letto sullo schema). Con il Wi-Fi in trasmissione il modulo assorbe una parte rilevante di quegli 800 mA: il budget dei sensori sul 3V3 va fatto (IMU, magnetometro, INA219, ADS1115, DS18B20, LED di specchio sull'elettrica). In caso di eccedenza serve un regolatore 3V3 sulla PCB. Il 5 V per il pin 5V viene da un convertitore dalla linea 12–14,6 V (non ancora scelto; stesso tema di OPEN-08).
- **Antenna ceramica a bordo:** portata Zigbee in un vano metallico da provare (REQ-SW-001, rischio a).
- **Una sola UART dati per scheda** grazie alla ripartizione GPS/RS485: nessuna scheda ne usa due.
