#!/usr/bin/env bash
# PreToolUse: blocca scritture in old/ (archivio rev. 1) e sui file binari EasyEDA.
input=$(cat)
f=$(printf '%s' "$input" | grep -o '"\(file_path\|notebook_path\)"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/^[^:]*:[[:space:]]*"//; s/"$//')
[ -z "$f" ] && exit 0
if printf '%s' "$f" | grep -Eq '(^|[\\/])old[\\/]'; then
  echo "Bloccato: old/ è l'archivio della rev. 1, in sola lettura. Copia ciò che serve in docs/ o hardware/." >&2
  exit 2
fi
if printf '%s' "$f" | grep -Eqi '\.eprj2?$'; then
  echo "Bloccato: i progetti EasyEDA sono binari. Modifica lo schematico tramite il server MCP easyeda-pro, non via file." >&2
  exit 2
fi
exit 0
