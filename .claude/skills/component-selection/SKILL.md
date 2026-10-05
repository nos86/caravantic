---
name: component-selection
description: Procedura per scegliere e congelare un componente della Caravantic board, tracciandolo ai requisiti e verificandolo su datasheet. Usare quando si propone, confronta o sostituisce un part number.
argument-hint: "[funzione o REQ-ID]"
---

# Selezione componente

Argomento: $ARGUMENTS

## 1. Requisito

- Individua i `REQ-*` in `docs/frd.md` che il componente deve soddisfare. Se non esistono o sono `Open` nei parametri che decidono la scelta, **fermati** e usa la skill `hardware-requirements-engineer` prima di proporre part number.
- Elenca i parametri decisivi con il valore richiesto e il caso peggiore (tensione max 16 V continui / transitori, temperatura −10…+60 °C salvo diverso REQ-ENV).

## 2. Candidati

- Al massimo 3 candidati. Tabella: parametro | richiesto | candidato A | B | C | margine.
- Applica derating: tensione ≥ 1,25× il caso peggiore continuo salvo diversa prescrizione; corrente e dissipazione alla temperatura massima, non a 25 °C.
- Vincoli di produzione da `caravantic-conventions` (package, assemblaggio manuale, disponibilità LCSC).
- Preferisci componenti già in BOM o già usati in `old/` se soddisfano il requisito: una riga di BOM in meno.

## 3. Verifica

- Ogni numero nella tabella deve citare il datasheet del costruttore (link + tabella/figura). Niente valori a memoria.
- Per il candidato scelto lancia l'agente `datasheet-verifier` con l'elenco delle affermazioni da verificare. Non congelare finché non ha restituito esito.

## 4. Registrazione

Aggiungi una voce a `docs/components.md` (crealo se manca, con intestazione `# Registro componenti`):

```
## <Rif. funzionale> — <Produttore> <P/N>
- Requisiti: REQ-...
- Stato: Proposto | Congelato
- Parametri decisivi: ... (fonte: link, tabella)
- Alternative scartate: ... (motivo)
- LCSC: Cxxxx — package — footprint EasyEDA verificato sì/no
- Rischi / note: ...
```

Aggiorna la riga del requisito in `docs/frd.md` se la scelta chiude un `Assumed` o un `Open` (solo con conferma dell'utente).
