---
name: schematic-review
description: Revisione dello schematico EasyEDA Pro della Caravantic board contro docs/frd.md e le convenzioni di progetto, tramite il server MCP easyeda-pro.
disable-model-invocation: true
argument-hint: "[blocco o foglio da rivedere, vuoto = tutto]"
---

# Revisione schematico

Ambito: $ARGUMENTS (vuoto = intero schematico)

## Preparazione

1. Verifica la connessione al server MCP `easyeda-pro` (strumenti di stato/diagnosi, es. `easyeda_live_status`, `easyeda_doctor`). Se non è raggiungibile, fermati e chiedi all'utente di aprire il progetto in EasyEDA Pro.
2. Leggi `docs/frd.md` e, se esiste, `docs/components.md`.

## Raccolta

- Elenca componenti e reti (`easyeda_list_schematic_components`, `easyeda_export_netlist`).
- Cerca pin non connessi (`easyeda_find_unconnected_pins`).
- Per i blocchi in ambito traccia le reti critiche (`easyeda_trace_net`, `easyeda_trace_component`).
- Leggi la descrizione di ogni strumento prima di usarlo: i nomi possono cambiare.

## Controlli minimi

| Controllo | Riferimento |
|---|---|
| Ingressi analogici su ADC1, fondo scala ≤ 2,45 V | caravantic-conventions |
| Nessuna uscita/LED su GPIO0, 3, 45, 46; GPIO14 libero | caravantic-conventions |
| Pull-down su gate/enable degli attuatori e del relè | REQ-SW-002 |
| Catena di ingresso: ordine PTC → ideal-diode → TVS → filtro; rating ≥ 40 V; Zener G-S presente | REQ-EL-001/002 |
| Pin esposti al campo con R serie + clamp | caravantic-conventions |
| Shunt: reti Kelvin dedicate fino al convertitore | REQ-IF-005 |
| Inverter: relè a riposo trasparente (NC = remote → inverter) | REQ-IF-007 |
| RS485: terminazione inseribile, +12 V protetto verso gli slave | REQ-IF-010 |
| Ogni componente attivo tracciato a un REQ e, se congelato, a `docs/components.md` | component-selection |

## Output

Tabella dei rilievi, dal più grave: severità (Bloccante/Maggiore/Minore) | componente/rete | problema | requisito violato | correzione proposta.

**Non modificare lo schematico.** Le correzioni vanno proposte; un'azione di modifica via MCP richiede conferma esplicita dell'utente, una per volta.
