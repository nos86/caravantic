# 03 — Ingressi

Requisiti implementativi per i 5 canali di ingresso configurabili per depopolazione.

**Traceability:** REQ-IF-004, IF-005, IF-006, IF-007, MECH-003, EL-004, EL-005, DIAG-001.

---

## 1. Principio

**Cinque canali identici**, ciascuno configurabile in una di tre varianti popolando componenti diversi sullo **stesso footprint**. Non esistono BOM alternative di scheda: la variante si sceglie in assemblaggio, canale per canale.

| Variante | Dominio | Uso previsto |
|---|---|---|
| **(I)** Contatto secco | Logico 3,3 V | Reed, microswitch, finecorsa locali alla board |
| **(II)** Opto-isolato | 12 V batteria (9–16 V) | Segnali dall'impianto camper |
| **(III-a)** Analogico in tensione | 0–16 V lato campo | Sensori che consegnano già una tensione |
| **(III-b)** Analogico resistivo | Eccitazione a bordo | **NTC**, sonde di livello, potenziometri |

**Il popolamento è on-demand:** si assembla la parte comune e si popola la variante quando serve.

---

## 2. Protezione del pin MCU/ADC — comune alle varianti esposte a fault di campo

> **Regola generale: nessuna eccezione per i canali non isolati.** La protezione si applica alle varianti (I) e (III), comprese le loro configurazioni interne (III-a, III-b e il caso di sensore resistivo riferito a 12 V, vedi §5). L'ipotesi di lasciare il pin non protetto in questi casi è stata scartata: il vincolo d'uso "contatti locali" non elimina il rischio di errore di cablaggio, e una restrizione d'uso senza riscontro visivo sulla scheda non è imponibile all'installatore.

> **Eccezione motivata — Variante (II), opto-isolata.** Il nodo lato MCU di questa variante (collettore del foto-transistor) non è raggiungibile da un fault sul terminale di ingresso: l'isolamento galvanico dell'opto lo esclude strutturalmente, e l'unica sorgente elettrica di quel nodo è il pull-up verso il rail 3,3 V, già protetto a monte (PTC, MOSFET ideal-diode, TVS — vedi [`01-power-supply.md`](01-power-supply.md) §1). Resistore serie e clamp **non sono popolati** in questa variante. Il rischio residuo — guasto hard dell'opto (cortocircuito o breakdown collettore-emettitore) — è escluso dal design basis, coerentemente con l'esclusione dei guasti hard di sorgente già adottata in [`01-power-supply.md`](01-power-supply.md) §1.3.

**Topologia (dove si applica la regola generale).** Resistore serie + clamp verso rail 3,3 V e massa, su ogni canale configurato come (I) o (III), mantenendo la topologia diretta della variante (I) — nessun opto, nessun ADC dedicato.

**Dimensionamento.**
- Resistore serie **1–4,7 kΩ (da congelare)**. Il valore interagisce con altri due parametri e non può essere scelto isolatamente: vedi §3.1 e §5.3. Per il modo (III-b) va preferito il valore più basso compatibile con la protezione, per minimizzare la distorsione del partitore.
- Clamp dimensionato per **24 V continui** e per i transitori ISO 7637-2 pulse 3.

**Perché.** Un pin GPIO dell'ESP32-S3 ha rating assoluto −0,3…3,6 V: senza rete di protezione un fault verso i 12 V lo distrugge. Vale per (I) e (III); non vale per (II) per il motivo esposto sopra.

> **I 24 V sono un livello di fault da errore di cablaggio, non un'alimentazione supportata.** Il progetto è a sola alimentazione 12 V.

**Acceptance [B].** 24 V DC applicati per 5 min su un canale campione configurato come (I) e su uno come (III): nessun danno, tensione al pin sempre < 3,6 V. Per la Variante (II), il test equivalente è applicare il fault sul terminale di ingresso e verificare che LED e foto-transistor dell'opto restino entro i limiti di datasheet — non è un test sul pin MCU, che resta strutturalmente fuori dal percorso di fault.

**Costo.** Circa 2 componenti passivi per canale sui canali configurati come (I) o (III); nessuno sui canali configurati come (II).

---

## 3. Variante (I) — contatto secco

**Topologia.** Ingresso verso massa attraverso il contatto; **pull-up esterno** verso 3,3 V; resistore serie e clamp di §2; rete RC di debounce.

### 3.1 Pull-up

**Prescrizione.** Pull-up **esterno definito**, non il pull-up interno dell'MCU.

**Motivo.** Il pull-up interno dell'ESP32-S3 (~45 kΩ) ha tolleranza larga: un pull-up debole e impreciso allunga il tempo di risposta e lo rende poco ripetibile, penalizzante quando il contatto è un finecorsa che deve fermare un motore in tempo utile.

**Valore indicativo 10 kΩ (da congelare).** Dipende da: costante RC richiesta (§4), resistore serie di protezione (§2), corrente di riposo tollerabile sul contatto chiuso.

### 3.2 Uso previsto

Contatti locali alla board, con cablaggio corto non esposto alle linee 12 V del camper: contatti magnetici, microswitch, finecorsa legati alla logica di attuazione.

---

## 4. Debounce hardware

**Topologia.** Rete RC su ogni ingresso, a valle del resistore serie di protezione.

**Costante di tempo: 1 ms.**

**Dimensionamento.** La costante RC va calcolata sulla **combinazione** di pull-up esterno, resistore serie di protezione e condensatore, non sul solo condensatore. Con pull-up interno il calcolo non è ripetibile.

**Complemento firmware.** Debounce configurabile 10–100 ms, sopra il filtro hardware.

**Acceptance [B].** Un treno di impulsi < 1 ms sovrapposto al segnale non genera falsi eventi; un cambio di stato reale è riportato entro il debounce configurato + 10 ms.

---

## 5. Variante (III) — analogica

### 5.1 Footprint del partitore

Due pad per resistore su ogni canale, più il **ponticello di saldatura** di §5.2. Dimensionati per accettare valori nel range kΩ–MΩ, package 0805: si tratta di garantire lo spazio fisico, non di congelare un valore.

### 5.2 Selezione del modo — ponticello di saldatura

> **Punto critico.** Un partitore che *attenua* una tensione in ingresso e uno che *eccita* un sensore resistivo **non hanno la stessa topologia**. Il solo footprint a due resistori non basta.

**Prescrizione.** Ogni canale analogico shall prevedere un ponticello che colleghi il capo alto del resistore superiore:

- al **terminale di ingresso** → modo (III-a), attenuazione di una tensione esterna;
- al **rail di eccitazione** → modo (III-b), sensore resistivo verso massa.

Senza questa selezione la variante non è utilizzabile con una NTC.

### 5.3 Rail di eccitazione

**Prescrizione: sezionabile.** Derivato dal rail periferiche già commutato da load-switch, oppure da un GPIO usato come sorgente.

**Motivo.** Un partitore da 10 kΩ permanentemente collegato a 3,3 V assorbe ~165 µA per canale: su più canali analogici saturerebbe da solo il budget di deep-sleep di 1 mA. L'eccitazione va attivata **solo durante la misura**.

**Interazione con la protezione.** Il resistore serie di §2 entra nel partitore e **falsa la lettura**. Per il modo (III-b) va scelto il valore più basso compatibile con la protezione e incluso nel calcolo della caratteristica, oppure compensato a firmware.

### 5.4 Limiti da documentare

- **Lettura non ratiometrica.** L'ADC dell'ESP32-S3 usa un riferimento interno, non il rail di eccitazione: la tolleranza del 3,3 V si trasferisce sulla misura. Accettabile per una temperatura ambiente, non per misure di precisione.
- **Impedenza vista dall'ADC** da mantenere bassa per non degradare il campionamento: sconsiglia NTC ad altissima resistenza, in tensione con il contenimento del consumo di eccitazione.
- **Modo (III-a):** la board non garantisce la qualità della misura. Se il dispositivo esterno non scala il segnale la protezione evita il danno ma la lettura è satura. L'onere di rispettare il fondo scala ricade sull'installatore.

### 5.5 Fondo scala

**≤ 2,45 V**, non 3,3 V: sopra tale soglia l'ADC con attenuazione 11 dB esce dal range caratterizzato per la calibrazione, con non-linearità residua maggiore. Criterio generale, valido per ogni ingresso analogico.

---

## 6. Variante (II) — opto-isolata

**Topologia.** LED dell'opto in serie a resistore di limitazione dal terminale di ingresso; foto-transistor con pull-up verso 3,3 V lato MCU.

**Soglie:** attivo **≥ 8 V**, inattivo **≤ 2 V**.

**Dimensionamento.** Il resistore di limitazione shall garantire corrente sufficiente al LED a 8 V e non superare la dissipazione ammessa a 16 V.

**Alimentazione.** Il lato MCU dell'opto sta sul **rail periferiche**, sezionabile da load-switch: in deep-sleep non assorbe.

---

## 7. Ingresso WAKEUP

Non è uno dei 5 canali configurabili: è un ingresso dedicato, sempre opto-isolato, trattato in [`01-power-supply.md`](01-power-supply.md) §2.1.

**Motivo dell'isolamento.** Il segnale proviene dall'impianto veicolo — quadro acceso, comando da pannello — potenzialmente con massa non pulita.

**Acceptance [B].** Isolamento galvanico verificato; un fronte di 12 V sull'opto risveglia la scheda entro 500 ms.

---

## 8. Connettori

Ogni ingresso è portato su **due connettori in parallelo**, sullo stesso nodo elettrico:

- **Morsettiera a vite 2,54 mm**, sul bordo della scheda — per cavi sfusi dall'impianto.
- **JST XH 2,5 mm**, ammesso anche interno all'area del PCB — per sensori preassemblati con codino crimpato, caso tipico delle NTC del modo (III-b).

> **Nota di installazione da documentare.** I due connettori di uno stesso canale sono sullo stesso nodo: vanno usati **in alternativa**, mai entrambi contemporaneamente.

**Nota sul passo.** JST non produce una serie a 2,54 mm. È adottata la **serie XH a 2,5 mm**; se l'intenzione fosse uno strip di pin a 2,54 mm — meno robusto e senza ritenzione — la scelta va corretta.

---

## 9. Checklist di rilascio

- [ ] Resistore serie e clamp presenti sui canali configurati come (I) o (III); non popolati sui canali configurati come (II) — isolamento galvanico e rail 3,3 V a monte verificati (§2)
- [ ] Ponticello di selezione modo III-a / III-b su ogni canale analogico
- [ ] Rail di eccitazione sezionabile, non permanente
- [ ] Resistore serie di protezione conteggiato nel calcolo del partitore di (III-b)
- [ ] Costante RC di debounce calcolata su pull-up esterno, non interno
- [ ] Ingressi analogici assegnati a pin ADC1
- [ ] Fondo scala ≤ 2,45 V su ogni ingresso analogico
- [ ] Doppio connettore in parallelo su ogni ingresso, morsettiere sul bordo
