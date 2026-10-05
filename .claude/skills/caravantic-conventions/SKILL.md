---
name: caravantic-conventions
description: Convenzioni elettriche, di documentazione e di verifica del progetto Caravantic board. Da applicare a ogni lavoro su specifica, schematico, componenti o firmware di questo repository.
user-invocable: false
---

# Convenzioni Caravantic

## Documentazione

- Requisiti in `docs/frd.md`, formato `**REQ-CAT-NNN** (Priorità, Stato)`. Categorie: EL, IF, TIM, MECH, ENV, SAFE, SW, LIFE, DIAG.
- Priorità MoSCoW (Must/Should/Could/Won't). Stato Confirmed/Assumed/Open.
- Non rinumerare: un requisito rimosso resta come `[RIMOSSO — sostituito da ...]` o `Won't`.
- Criteri di accettazione marcati `[B]` (verificabile al banco con strumentazione ordinaria) o `[D]` (dimostrato per selezione e confronto a datasheet). Nessuna certificazione formale.
- Prescrizioni: *shall* = vincolante, *dovrebbe* = raccomandazione. Valori non decisi: **(da congelare)**.
- Ogni chiusura di un punto aperto: barrare l'ID nella tabella §3 e aggiungere una riga allo storico revisioni.

## Regole elettriche già decise (rev. 1, riconfermate dal riuso)

- Alimentazione LFP 12 V: operativo 10–14,6 V, sopravvivenza a 16 V continui e a inversione di polarità.
- Catena di ingresso: PTC → P-MOSFET ideal-diode con Zener di clamp G-S → TVS (V_C alla corrente di picco < rating del regolatore) → filtro EMI depopolato con ponticelli 0 Ω. Rating ≥ 40 V su tutta la catena; impedenza serie conteggiata.
- ESP32-S3: ingressi analogici **solo su ADC1** (ADC2 inaffidabile con Wi-Fi attivo); fondo scala ADC **≤ 2,45 V** (attenuazione 11 dB); nessuna uscita di potenza né LED su pin di strapping (GPIO0, GPIO3, GPIO45, GPIO46); GPIO14 impegnato dal LED RGB del modulo Waveshare ESP32-S3-Tiny.
- Pin esposti al campo: resistore serie + clamp verso 3,3 V e massa, tenuta a 24 V di fault.
- Ingressi 12 V da impianto: opto-isolati, attivo ≥ 8 V, inattivo ≤ 2 V.
- Stato sicuro per sole reti passive: pull-down sui gate e sugli enable, attuatori fermi e relè diseccitati con MCU in reset.
- Shunt: misura differenziale con collegamento Kelvin, mai riferita alla massa di alimentazione.

## Produzione

- Assemblaggio manuale + reflow: nessun BGA, passivi ≥ 0603, default 0805, 1206 dove la potenza lo richiede.
- Preferire componenti disponibili su LCSC/JLCPCB con footprint nella libreria EasyEDA.

## Verifica

- Dati numerici che reggono una decisione: datasheet del costruttore citato con sezione/tabella. Dati critici: seconda fonte indipendente o agente `datasheet-verifier`.
- Fonti deboli (forum, blog, rivenditori) dichiarate come tali nel testo.
