#!/usr/bin/env bash
# SessionStart: riassume i punti aperti dei FRD (comune, idraulica, elettrica) nel contesto della sessione.
root="${CLAUDE_PROJECT_DIR:-.}"
files=""
for f in docs/frd.md idraulica/frd.md elettrica/frd.md; do [ -f "$root/$f" ] && files="$files $root/$f"; done
[ -n "$files" ] || exit 0
echo "Caravantic — punti aperti nei FRD docs/, idraulica/, elettrica/ (gli ID barrati sono chiusi):"
grep -hE '^\| (OPEN|NEW)-[0-9]+' $files | awk -F'|' '{gsub(/^ +| +$/,"",$2); gsub(/^ +| +$/,"",$3); gsub(/^ +| +$/,"",$4); printf "- %s [%s]: %s\n", $2, $4, substr($3,1,160)}'
n=$(cat $files | grep -c '^\*\*REQ-')
a=$(cat $files | grep '^\*\*REQ-' | grep -c 'Assumed')
o=$(cat $files | grep '^\*\*REQ-' | grep -c ', Open)')
echo "Requisiti: $n totali, $a Assumed, $o Open."
exit 0
