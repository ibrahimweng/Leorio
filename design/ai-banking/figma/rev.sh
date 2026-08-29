#!/bin/sh
# The built screens carry {{accent}} where the accent colour goes, because the
# review canvas swaps it per theme. Figma needs a real colour, so this writes a
# copy of every screen with the placeholder resolved.
#
#   sh rev.sh /path/to/work
#
# Reads ../*.dc.html, writes <work>/rev/<Name>.html.
set -e
OUT="${1:?usage: sh rev.sh <work-dir>}/rev"
SRC="$(dirname "$0")/.."
ACCENT="#213ACA"
mkdir -p "$OUT"
for f in "$SRC"/*.dc.html; do
  name=$(basename "$f" .dc.html)
  sed "s/{{accent}}/$ACCENT/g" "$f" > "$OUT/$name.html"
done
echo "wrote $(ls "$OUT" | wc -l) screens to $OUT"
