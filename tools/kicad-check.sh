#!/usr/bin/env bash
# Run KiCad's own ERC and DRC over the generated schematic and panel, and plot
# both for a look. Everything lands in .kicadcheck/, which is gitignored.
#
# Set KICAD_CLI if kicad-cli is not on PATH. Under WSL, point it at the Windows
# binary and this still works:
#
#   KICAD_CLI="/mnt/g/Program Files/KiCad/10.0/bin/kicad-cli.exe" tools/kicad-check.sh
#
# Needs KiCad 8 or newer: `sch erc` does not exist in 7.

set -uo pipefail
cd "$(dirname "$0")/.."

CLI="${KICAD_CLI:-kicad-cli}"
command -v "$CLI" >/dev/null 2>&1 || [ -x "$CLI" ] || {
    echo "kicad-cli not found. Set KICAD_CLI to its path." >&2; exit 127; }

OUT=.kicadcheck
mkdir -p "$OUT"

# kicad-cli is a Windows binary under WSL, so paths have to be translated
path() { if command -v wslpath >/dev/null 2>&1 && [[ "$CLI" == *.exe ]]
         then wslpath -w "$1"; else echo "$1"; fi; }

echo "== ERC: docs/v3-adder.kicad_sch"
"$CLI" sch erc --output "$(path $OUT/erc.rpt)" --severity-all \
    "$(path docs/v3-adder.kicad_sch)" 2>&1 | tail -2

echo "== DRC: docs/v3-panel.kicad_pcb"
"$CLI" pcb drc --output "$(path $OUT/drc.rpt)" --severity-all \
    "$(path docs/v3-panel.kicad_pcb)" 2>&1 | tail -3

echo "== plots"
"$CLI" sch export svg --output "$(path $OUT)" --no-background-color \
    "$(path docs/v3-adder.kicad_sch)" >/dev/null 2>&1
"$CLI" pcb export svg --output "$(path $OUT/panel.svg)" \
    --layers "Edge.Cuts,F.Silkscreen" --page-size-mode 2 \
    --exclude-drawing-sheet "$(path docs/v3-panel.kicad_pcb)" >/dev/null 2>&1
echo "   $OUT/v3-adder.svg, $OUT/panel.svg"

echo
echo "== ERC violations by type"
grep -oE '^\[[a-z_]+\]' "$OUT/erc.rpt" 2>/dev/null | sort | uniq -c | sort -rn
# grep -c prints 0 and exits 1 when nothing matches, so no || fallback here
echo "   errors: $(grep -c '; error' "$OUT/erc.rpt" 2>/dev/null)" \
     "warnings: $(grep -c '; warning' "$OUT/erc.rpt" 2>/dev/null)"
