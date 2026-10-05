# Caravantic Board rev. 2 — istruzioni di progetto

Scheda singola per camper Fiat Ducato X244 (2005, 2.3 JTD), Marlin 65G. ESPHome su Waveshare ESP32-S3-Tiny, integrata in Home Assistant. Lingua di lavoro: italiano.

## Dove sono le cose

- `docs/frd.md` — specifica funzionale. **Riferimento normativo**: ogni scelta hardware deve tracciare a un `REQ-*`.
- `docs/components.md` — registro delle scelte di componente (creato dalla skill `component-selection`).
- `hardware/` — schematico e PCB rev. 2 (EasyEDA Pro, accessibile via MCP `easyeda-pro`).
- `firmware/` — firmware ESPHome rev. 2.
- `old/` — progetto rev. 1 archiviato. **Sola lettura** (un hook blocca le modifiche). Da consultare per il riuso: la mappa è in `docs/frd.md` §5.

## Regole di lavoro

1. **Un problema alla volta.** Resta sulla domanda posta; non anticipare problemi a valle se non richiesto.
2. **Requisito prima del componente.** Nessun part number senza `REQ-*` di riferimento; se manca, usa la skill `hardware-requirements-engineer`.
3. **Fonti.** Ogni dato numerico su cui poggia una decisione va confermato su datasheet del costruttore; per i dati critici serve una seconda fonte indipendente. Fonti deboli (forum, blog, rivenditori) vanno dichiarate come tali. Se non verificabile, dirlo.
4. **Stati:** `Confirmed` = deciso dall'utente; `Assumed` = ipotesi da confermare; `Open` = da risolvere. Non promuovere un `Assumed` a `Confirmed` senza conferma esplicita.
5. **Analisi critica:** evidenziare rischi, assunzioni fragili, problemi di implementazione.
6. Le convenzioni elettriche e di documentazione sono nella skill `caravantic-conventions`.

## Automazioni attive (`.claude/`)

- Hook `SessionStart`: riassume i punti aperti di `docs/frd.md`.
- Hook `PreToolUse`: blocca modifiche a `old/` e ai file binari EasyEDA (`*.eprj2`).
- Hook `PostToolUse`: dopo ogni modifica a `docs/*.md` verifica la coerenza di `docs/frd.md` (ID duplicati, stato/priorità mancanti, riferimenti OPEN/REQ orfani).
- Skill: `hardware-requirements-engineer`, `caravantic-conventions`, `component-selection`, `/schematic-review`.
- Agente: `datasheet-verifier` — verifica indipendente dei dati di componente.
