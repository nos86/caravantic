#!/usr/bin/env bash
# PostToolUse: dopo una modifica a docs/*.md verifica la coerenza di docs/frd.md.
input=$(cat)
f=$(printf '%s' "$input" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/^[^:]*:[[:space:]]*"//; s/"$//')
printf '%s' "$f" | grep -Eq 'docs[\\/]+[^\\/]*\.md$' || exit 0
frd="${CLAUDE_PROJECT_DIR:-.}/docs/frd.md"
[ -f "$frd" ] || exit 0
err=""
# 1. ID requisito duplicati
dup=$(grep -o '^\*\*REQ-[A-Z]*-[0-9]*\*\*' "$frd" | sort | uniq -d | tr -d '*')
[ -n "$dup" ] && err="$err\n- REQ duplicati: $(echo $dup)"
# 2. Requisiti senza (Priorità, Stato)
bad=$(grep '^\*\*REQ-' "$frd" | grep -Ev '\((Must|Should|Could|Won.t), (Confirmed|Assumed|Open)' | grep -o '^\*\*REQ-[A-Z]*-[0-9]*' | tr -d '*')
[ -n "$bad" ] && err="$err\n- REQ senza (Priorità, Stato) MoSCoW/Confirmed|Assumed|Open: $(echo $bad)"
# 3. OPEN citati ma assenti dalla tabella dei punti aperti
for id in $(grep -o 'OPEN-[0-9][0-9]*' "$frd" | sort -u); do
  grep -Eq "^\| (~~)?$id(~~)? \|" "$frd" || err="$err\n- $id citato ma non presente nella tabella §3"
done
# 4. REQ citati nella tabella OPEN ma non definiti
for id in $(grep -E '^\| (~~)?OPEN-' "$frd" | awk -F'|' '{print $(NF-1)}' | grep -o '[A-Z]\{2,5\}-[0-9]\{3\}' | sort -u); do
  grep -q "^\*\*REQ-$id\*\*" "$frd" || err="$err\n- REQ-$id citato nei punti aperti ma non definito"
done
# 5. Riferimenti a file di old/ inesistenti
for p in $(grep -o 'old/[A-Za-z0-9_./-]*\.md' "$frd" | sort -u); do
  [ -f "${CLAUDE_PROJECT_DIR:-.}/$p" ] || err="$err\n- Riferimento a file inesistente: $p"
done
if [ -n "$err" ]; then
  printf 'Controllo coerenza docs/frd.md fallito:%b\n' "$err" >&2
  exit 2
fi
exit 0
