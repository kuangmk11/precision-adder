# Kassutronics front panel style

**Version 1.00.**

All eleven panels are generated, not drawn. Each one is a `<stem>.layout.json`
saying what its controls are and how they relate; every mark on the finished
board comes from `tools/panel_style.py`. Change a number there and all eleven
panels change with it.

```sh
tools/build_styled_panels.sh            # every finished layout
tools/build_styled_panels.sh Slope      # just the ones whose path matches
```

Outputs land beside each source as `<stem>.styled.{panel.json,kicad_pcb,svg}`,
leaving the PDF-derived conversions untouched.

The look is borrowed from RYO's *Altered States* (`reference.jpg`) and is
deliberately PCB-native: single-weight plotter lettering, connections routed the
way a trace is routed, and dots where a silkscreen would have vias. Printed as
white silkscreen on black soldermask.

## The one rule that is not negotiable

**Control hole positions are inherited, never computed.** They were fitted from
the production Illustrator artwork, and a panel whose holes move stops fitting
its main board. `panel_compose.py` copies them through untouched and refuses to
write if the set has changed. It also errors if a layout fails to account for
every hole, so a jack cannot silently vanish.

Mounting holes are the exception: they meet the rails, not the module's own
board, so they are regenerated (below).

## Tokens

Every value lives in `STYLE` in `tools/panel_style.py`.

| | value | |
|---|---|---|
| `LINE_W` / `RULE_W` | 0.25 / 0.20 mm | wires, brackets, rings / centre divider |
| `LABEL_SIZE` / `PITCH_LABEL` | 2.0 / 2.2 mm | control labels |
| `SMALL_SIZE` / `PITCH_SMALL` | 1.6 / 1.7 mm | crowded rows, notes, bracket labels |
| `TITLE_SIZE` / `PITCH_TITLE` | 3.2 / 3.4 mm | module name |
| `LOGO_SIZE` / `PITCH_LOGO` | 1.3 / 1.45 mm | wordmark |
| `TRAVEL_DOT_D` / `TRAVEL_END_D` | 0.9 / 1.4 mm | knob travel marks |
| `DOT_D` | 0.6 mm | star-field, when used at all |
| `RING_GAP` | 1.2 mm | output ring stands off the hole edge |
| `EDGE_MARGIN` | 0.6 mm | no silkscreen closer than this to the cut |

**Tracking.** KiCad has no letter-spacing setting and Newstroke is proportional,
but the reference's lettering is monospaced and widely tracked. So text is
emitted **one `PCB_TEXT` per character** on a fixed pitch, each centred in its
own cell. Everything is uppercase.

## Marks and what they mean

**Knob travel — a dotted arc.** Eleven dots every 30°, at every position except
+90°; the gap at the bottom is where the label goes and the two dots either side
of it, at +120° and +60°, are the ends of travel and are drawn heavier. These
positions are not invented: they are measured off the starbursts on the ASR,
both Attenumix panels and the Avalanche VCO, which all draw the same 300° pot.
The radius sits inside the band that artwork occupies — 3.75 to 8.06 mm on a
7.5 mm pot — so the marks stay visible with a knob fitted.

```
        ·  ·  ·               11 dots, r = hole_r + 3.45
      ·         ·
    ·     (O)     ·           hole
      ·         ·
     ●           ●            heavy: ends of travel, +120 / +60
          FOLD                the 30 deg gap at +90
```

- `"knob": "small"` pulls the radius in for tightly spaced rows (Slope's
  Shape/Sustain sit on 13.3 mm centres).
- `"knob": "big"` draws **two** concentric rings, for the oversized main knob
  whose starburst on the old panels runs out to 18.5 mm rather than 8.5 —
  the 3340 and KS-20 Frequency, the Ladder Filter, the Wavefolder's Fold.
- `"polarity": "bipolar"` adds a heavier dot at 12 o'clock for the centre
  detent, and sets `-` / `+` outside the travel ends.
- `"ends": ["LP", "HP"]` does the same with words, for the KS-20's Mode.

**A ring means signal leaves here.** Every jack carries `"dir": "in"` or
`"out"`, and `out` draws the ring. Keeping it the only closed circle on a panel
is what lets direction read at a glance — which is also why nothing else may be
a closed circle.

**A bracket groups one direction only.** It says *these belong together*, so
enclosing an input and an output in one misstates the signal flow.
`emit_brackets` raises `LayoutError` if a bracket mixes directions. Labels sit in
gaps in the bracket's own top edge. An output row inside a bracket does not also
get rings — the bracket already says it.

**An outline groups by function, not direction.** A plain rounded box at the
lighter rule weight, drawn round everything belonging to one section — the
Quantizer's two channels, each of which necessarily has both an input and an
output, so the bracket's one-direction rule does not apply. Where a bracket
labels a row in its own top edge and must not mix directions, an outline just
says *this lot is one thing*.

**A span is one shared label** over a bar covering the controls it names, with a
tick turning down at each end — the 3340's two V/Oct inputs get one word, not
the same word twice.

**A wire is a connection**, routed with one knee using only 0°, 90° and 45°
segments, stopping short of what it joins and breaking around any label it
passes under. The router does **not** avoid obstacles: check that a wire does
not cross a control, or drop it.

## Layout

Labels go **above** jacks and LEDs, **below** pots and switches, measured from
whatever is drawn around the hole — a pot's travel ring, an output's ring — not
from the hole itself.

Three things adjust themselves and should not be fought:

- a row whose labels would collide, or would need shoving back inside the board,
  drops to the small size **as a whole row**;
- every label in a row is snapped to one baseline, so a ringed output does not
  sit 1.2 mm below its plain neighbours;
- the title shrinks to fit the clear span between the mounting slots.

Escape hatches, in the order you should reach for them: `"size": "small"`,
`"label_gap"`, `"label_at"` as a direction, `"label_at"` as an explicit `[x, y]`.
`"title_y"` and `"title_size"` exist for panels where a control near the top
leaves only ~2 mm of clear band.

## Mounting

Regenerated to one rule, as 6.4 × 3.2 mm obround slots milled on Edge.Cuts —
horizontal, so a module can slide ±1.6 mm to meet its neighbours.

| | |
|---|---|
| vertical | centre 3.0 mm from the top and bottom edges |
| horizontal | centre 7.5 mm in from the edge; the opposite column steps out by N × 5.08 mm |
| **> 6 HP** | both columns, 4 slots — 8 HP at 7.5 / 32.9, 10 HP at 7.5 / 43.06 |
| **≤ 6 HP** | one slot top and bottom on **opposite corners**, top right and bottom left. One screw per rail is enough at that width, and diagonal placement stops the module pivoting. |

The 7.5 mm inset is the datum and the grid steps out from it, so the far margin
lands at 7.26–7.44 rather than exactly 7.5. That is the way round that matters:
the grid is what the rail is drilled to.

## Glyphs and the keyboard (Quantizer only)

The Quantizer's shift layer is iconographic, and those icons are what its user
manual teaches, so they are redrawn rather than replaced with words. `GLYPHS` in
`panel_style.py` holds twelve, each built in a local box running -1..1 from the
same strokes and arcs as everything else and scaled on placement:

| button | glyph | function |
|---|---|---|
| 0 | `gate_length` | gate length — a crotchet and a minim, a short note and a long one |
| 1 | `rotate` | rotate menu |
| 2 / 3 | `transpose_both` / `transpose_one` | transpose |
| 4 / 5 | `offset_both` / `offset_one` | offset |
| 6 | `keyboard` | keyboard mode |
| 7 | `legato` | legato — two crotchets under a slur |
| 8 | `gear` | settings |
| 9 | `tau` | gate length |
| 10 / 11 | `cv_a` / `cv_b` | CV A / CV B menus |

The "both channels" glyphs carry two marks where the "one channel" ones carry
one — the distinction the original draws, and the one the manual describes.
`tau` is drawn rather than set, so it cannot depend on the stroke font carrying
Greek.

**The keyboard ring inverts.** The original fills the five *black* keys as
wedges on a white panel. Straight onto black soldermask that reading breaks, so
the seven **white** keys are filled instead and the black keys are left as bare
panel — same keyboard, same contrast, opposite ink. Adjacent white keys (E–F,
B–C) merge into one shape, as on a real keyboard. Each wedge subtracts its own
scale button's hole with clearance rather than printing over it.

The numbers moved outside the keyboard ring to make room, and **3 and 9 are
omitted** — they sit dead on the panel edges, exactly as on the original.

## Screw holes

3.4 mm holes fix the board behind the panel. They are drilled and then ignored:
`SILENT_KINDS` covers them along with mounting slots, so they need no layout
entry, take no label and get no marks.

## The star-field

Off. The reference's scatter reads as texture because it covers a whole panel
edge to edge; here, once the keepouts around holes, wires, brackets and type have
taken their share, there is nothing left but orphans — measured, 15 of 17
survivors on Slope had no near neighbour, and the ASR had none at all. An orphan
dot reads as fab dirt. The travel rings already carry the polar-dot language.

`starfield()` remains in the library and `"starfield": true` opts a panel back
in, should one turn out to have real open space to fill.

## The wordmark

`KASSUTRONICS` letterspaced inside a plain two-lead component frame — the same
schematic-fragment idea as RYO's, a different part. It drops to `KT` on 4 HP,
where the bottom margin has only ~7 mm of clear width. It sits at
`height − 7.0`, above the mounting line, because a 6.4 mm slot leaves only
17.8 mm between the bottom pair and the full wordmark needs 19.0.

## Adding a panel

```sh
python3 tools/panel_compose.py --stub documentation/Foo/Foo.panel.json
```

writes a starter layout with every hole classified by diameter and
`"label": "TODO"`. Fill it in; the build skips any layout still containing
`TODO`. Then check, in this order:

1. the composer exits 0 — no unmatched control, no unaccounted hole;
2. `holes` in the styled output is identical to the source's control holes;
3. `kicad-cli pcb drc` reports **zero** violations. Not "warnings only" — the
   keepouts are under our control now, so anything that survives is a real
   collision;
4. rasterise the SVG and look at it.

## Versioning

**Any change to this document increments the version by one hundredth** — v1.00 →
v1.01 → v1.02, and so on. There is no distinction between a typo and a new rule;
every edit is a bump.

Two things move together, and a change that touches only one of them is incomplete:

1. the version line at the top of this file;
2. the filename — `PANEL_STYLE_v1.00.md` → `PANEL_STYLE_v1.01.md`. Rename with
   `git mv` so the history follows the file.

Then update anything pointing at the old filename (`README.md`).
