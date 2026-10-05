#!/usr/bin/env bash
# SessionStart: riassume i punti aperti di docs/frd.md nel contesto della sessione.
frd="${CLAUDE_PROJECT_DIR:-.}/docs/frd.md"
[ -f "$frd" ] || exit 0
echo "Caravantic — punti aperti in docs/frd.md (gli ID barrati sono chiusi):"
grep -E '^\| OPEN-[0-9]+' "$frd" | awk -F'|' '{gsub(/^ +| +$/,"",$2); gsub(/^ +| +$/,"",$3); gsub(/^ +| +$/,"",$4); printf "- %s [%s]: %s\n", $2, $4, substr($3,1,160)}'
n=$(grep -c '^\*\*REQ-' "$frd")
a=$(grep '^\*\*REQ-' "$frd" | grep -c 'Assumed')
o=$(grep '^\*\*REQ-' "$frd" | grep -c ', Open)')
echo "Requisiti: $n totali, $a Assumed, $o Open."
exit 0
