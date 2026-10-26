# Caravantic Board rev. 2 — istruzioni di progetto

Scheda singola per camper Fiat Ducato X244 (2005, 2.3 JTD), Marlin 65G. ESPHome su Waveshare ESP32-S3-Tiny, integrata in Home Assistant. Lingua di lavoro: italiano.

## Dove sono le cose

- **Due PCB (decisione 2026-10-26):** `idraulica/` (acque chiare/grigie, pompa, motori) ed `elettrica/` (shunt, inverter, relè globale). Ognuna contiene `frd.md` (requisiti), `components.md` (registro componenti), `schematic/` (specifiche dei fogli) e `sim/`. Un requisito/componente/foglio di una scheda va nella sua cartella.
- `docs/frd.md` — specifica funzionale **comune** (contesto, requisiti trasversali non ancora assegnati, punti aperti comuni, riuso, storico). **Riferimento normativo** insieme ai due `frd.md` di scheda: ogni scelta hardware deve tracciare a un `REQ-*`.
- `docs/components.md` — registro componenti **comuni** (creato dalla skill `component-selection`; i componenti di scheda vanno nel `components.md` della scheda).
- `hardware/` — parti comuni dello schematico (a1 ingressi, a7 IMU, a8 mappa pin), datasheet e progetto EasyEDA rev. 2 (accessibile via MCP `easyeda-pro`).
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

- Hook `SessionStart`: riassume i punti aperti dei tre FRD.
- Hook `PreToolUse`: blocca modifiche a `old/` e ai file binari EasyEDA (`*.eprj2`).
- Hook `PostToolUse`: dopo ogni modifica a `*.md` in `docs/`, `idraulica/`, `elettrica/` verifica la coerenza dei tre FRD (`docs/`, `idraulica/`, `elettrica/`) (ID duplicati, stato/priorità mancanti, riferimenti OPEN/REQ orfani).
- Skill: `hardware-requirements-engineer`, `caravantic-conventions`, `component-selection`, `/schematic-review`.
- Agente: `datasheet-verifier` — verifica indipendente dei dati di componente.
