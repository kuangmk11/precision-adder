# Precision Adder v2.2
This is a precision CV source and adder. It has four stages, each with an input, an output and a passthru. Each stage's **output** normals down to the next stage's input, so with a single cable into `IN1` the stages cascade and their offsets sum; patching into any `IN` breaks the normal above it. The passthru is a buffered copy of that stage's input, so with nothing patched `PT2` = `OUT1`, `PT3` = `OUT2`, and so on.

Each section provides a different voltage to be added to the input: +/- 2v, +/- 1v, +/- .5833333v (a fifth), +/- .4166666v (a fourth)

<img src="adder-front.JPG" width=210>
<img src="adder-side.JPG" width=210>

## Available intervals

The switches are SPDT ON-ON, so a stage in the chain always contributes either its positive or its negative offset — there's no center-off. Using the switches alone gives 4 stages x 2 states = **16 combinations** and 13 distinct voltages.

A stage can also be bypassed by patching its `PT` (passthru) into the `IN` of the next stage, feeding that stage's input forward instead of its output. That makes each stage a 3-state element (**+**, **-**, or **bypassed**), for **81 configurations** and **39 distinct voltages**.

The full set is symmetric, so the table below lists magnitudes only — for the negative of any row, flip every `+`/`-` (bypasses stay bypassed). `o` = stage bypassed.

| Semitones | Volts | Interval | Settings (2oct · 1oct · 5th · 4th) |
|---:|---:|---|---|
| 48 | 4.0000 | 4 oct | `+ + + +` |
| 43 | 3.5833 | 3 oct + 5th | `+ + + o` |
| 41 | 3.4167 | 3 oct + 4th | `+ + o +` |
| 38 | 3.1667 | 3 oct + M2 | `+ + + -` |
| 36 | 3.0000 | 3 oct | `+ + o o` · `+ o + +` |
| 34 | 2.8333 | 2 oct + m7 | `+ + - +` |
| 31 | 2.5833 | 2 oct + 5th | `+ + o -` · `+ o + o` |
| 29 | 2.4167 | 2 oct + 4th | `+ + - o` · `+ o o +` |
| 26 | 2.1667 | 2 oct + M2 | `+ o + -` |
| 24 | 2.0000 | 2 oct | `+ + - -` · `+ o o o` · `+ - + +` · `o + + +` |
| 22 | 1.8333 | 1 oct + m7 | `+ o - +` |
| 19 | 1.5833 | 1 oct + 5th | `+ o o -` · `+ - + o` · `o + + o` |
| 17 | 1.4167 | 1 oct + 4th | `+ o - o` · `+ - o +` · `o + o +` |
| 14 | 1.1667 | 1 oct + M2 | `+ - + -` · `o + + -` |
| 12 | 1.0000 | 1 oct | `+ o - -` · `+ - o o` · `o + o o` · `o o + +` |
| 10 | 0.8333 | m7 | `+ - - +` · `o + - +` |
| 7 | 0.5833 | 5th | `+ - o -` · `o + o -` · `o o + o` |
| 5 | 0.4167 | 4th | `+ - - o` · `o + - o` · `o o o +` |
| 2 | 0.1667 | M2 | `o o + -` |
| 0 | 0.0000 | unison | `o o o o` · `+ - - -` · `o + - -` · `o - + +` · `- + + +` |

### The pattern

Every reachable offset is **0, ±2, or ±5 semitones (mod 12)** — unison, M2, 4th, 5th, m7, and their octaves. Within ±48 semitones every such value is reachable *except* ±46. Thirds, tritones, sixths, and single semitones are not available, because a fifth and a fourth can only ever combine to an octave (7+5) or a whole step (7-5).

The usable pitch-class set is therefore the suspended pentatonic `{0, 2, 5, 7, 10}`, spread across a full ±4 octaves in 1/12 V steps.

### Patching notes

- **Leading bypasses are free** — plug your CV into `IN2` / `IN3` / `IN4` instead of `IN1`.
- **Trailing bypasses are free** — take your output from the last active stage's `OUT` instead of `OUT4`.
- **Only interior bypasses cost a cable**: one patch, `PTn` -> `IN(n+1)`, per skipped stage.
- Where a row lists multiple settings, prefer the one with bypasses at the edges — same voltage, fewer cables. For example 2 oct + 4th is `+ + - o` with no cables, versus `+ o o +` with two.

## v3 proposal (unbuilt)

v2.2 is a serial interval adder with a redundant interval set. v3 keeps the cascade, fixes the set, and reorganises the panel around what the cascade is actually good at — stacking intervals into chords.

The interval problem first: because a fifth plus a fourth is exactly an octave (7 + 5 = 12), two of v2.2's four stages collapse into a redundant third. 81 configurations produce only 39 distinct voltages, and the output can never leave the pitch classes `{0, 2, 5, 7, 10}` — no thirds, no sixths, no tritone, no single semitones.

### Four changes

**1. ON-OFF-ON switches.** v2.2 uses SPDT ON-ON, which is why bypassing a stage costs a patch cable. A subminiature ON-OFF-ON is the same footprint at essentially the same price, and the center detent gives each stage a native off position. Every configuration becomes reachable from the front panel with no patching. (Doepfer's A-185-2 has always done it this way — see the comparison below.)

**2. Drop `IN2`-`IN4` and `PT2`-`PT4`.** Outputs normal down to the next input, so with nothing patched `PT2` = `OUT1`, `PT3` = `OUT2`, `PT4` = `OUT3`. Those passthrus are duplicates of the output above them. The extra inputs existed to break the cascade, which the center-off switch now does better. Six jacks were doing the work of two.

**3. Sum three inputs at the front.** `IN1` + `IN2` + `IN3` at unity gain feed the head of the cascade. This is the multi-source summing the module is named for — keyboard plus sequencer plus offset — and it is what the freed panel space buys. `PT` becomes the buffered *sum* of the inputs: an untransposed root that stays put while the cascade transposes everything above it.

**4. Collapse the two octave stages into one, and make stages 2-4 thirds.** Stage 1 becomes a 5-state octave control (±1, ±2, off) from two toggles, freeing a stage. Stages 2 and 3 get a three-position quality switch selecting **4th / maj 3rd / min 3rd**, and stage 4 selects **5th / maj 3rd / min 3rd** — because stacked thirds are how chords are built, and the fifth on the last stage keeps the module's most-used interval one flip away.

### Panel

| | v2.2 | v3 |
|---|---:|---:|
| Jacks | 12 | 8 — `IN1` `IN2` `IN3` `PT` `OUT1`-`OUT4` |
| Switches | 4 | 8 — 2 per stage |
| **Positions** | **16** | **16** |

Same density as the board already built. No rotary, no new mechanical problem.

<img src="docs/v3-panel.svg" width=210>

**This is a new panel, not v2.2's reused.** Earlier v3 drafts kept every v2.2 hole
position and only reassigned diameters, which forced the four outputs into two shared
rows. Grouping each stage instead — its two switches and its own output, boxed together —
needs six evenly spaced rows below the inputs, so the positions are refitted. The v3 main
board is new anyway.

Panel and drawing are generated by [`tools/gen_panel.py`](tools/gen_panel.py) from one
layout table, so they cannot disagree:

```sh
python3 tools/gen_panel.py            # writes the .kicad_pcb and the .svg, with a clearance report
python3 tools/gen_panel.py --table    # the hole schedule below
```

- [`docs/v3-panel.kicad_pcb`](docs/v3-panel.kicad_pcb) — board outline, holes and mounting
  slots on `Edge.Cuts`, silkscreen on `F.SilkS`. Holes are `Edge.Cuts` circles, so the fab
  routes rather than drills them; swap to NPTH pads if your fab prefers.
- [`docs/v3-panel.svg`](docs/v3-panel.svg) — the same geometry at 1:1 (1 unit = 1 mm,
  20 × 128.5 mm), for printing and review. The grey rings are hardware footprints — 8 mm
  Thonkiconn nut, 7.5 mm toggle nut — shown for clearance checking, not artwork, and not
  in the KiCad output.

Conventions — lettering, marks, label placement, mounting — are in
[`PANEL_STYLE_v1.02.md`](PANEL_STYLE_v1.02.md).

#### How it reads

Four jacks at the top: three summed inputs and `SUM`, the buffered sum that `PT` becomes.
`SUM` is an output, so it carries the ring — the panel's only closed circle, which is what
lets direction read at a glance. The ring has to clear the 8 mm nut to be visible at all,
and a 20 mm panel carrying two 8 mm nuts has 4 mm of slack in total, so at r 4.4 it ends up
0.07 mm from the cut on the outboard side. Still on the board, but well inside the 0.6 mm
edge margin, and a fab may trim the outer edge of it. Taken deliberately: a broken ring
reads worse than a clipped one. Below them, **four boxed groups, one per stage — polarity
switch, selector switch, that stage's output.** Each stage now owns its output, which the
old shared-row layout could not manage.

**Arrows trace the cascade** across the top pair, down into the bottom-left group, and
across the bottom pair — the order the stages actually sum in. The middle leg cannot be a
straight diagonal: about 4 mm of clear band between the box rows against a 10.8 mm column
pitch would need a 15° line, and the house routing is 0°, 90° and 45° only. So it drops,
takes a 45° knee, runs the band and turns down into the group it feeds. Where an arrow
crosses a box outline the outline is broken, the same way a group name breaks it.

`OUT1`–`OUT4` do not repeat the ring. Each already sits inside a named box that says which
stage it belongs to, and the style guide's rule against a second closed circle is what
keeps `SUM`'s ring meaningful. If you would rather every output ring, it is one line in the
generator.

Within a group: `+` above the polarity toggle, `−` below it, and **`0` beside its centre
detent**. The selector's two throws are labelled above and below it the same way.

That `0` matters more than it looks. A selector displays a value at all times, so without
it the panel reads as though a stage adds its interval even when the stage is switched off
— and the polarity toggle's centre, not the selector's, is what turns a stage off. One rule
covers both toggles now: **a three-position toggle's centre value is marked in the strip
between its nut and the box edge.** `OCT`'s magnitude switch is two-position and has no
centre, so it carries no such mark.

It is also why a plain fifth is one flip. At rest every polarity toggle is centred and the
module passes through untouched, whatever the selectors show; move stage 4's polarity to
`+` and its selector is already sitting on the `5`.

**The selector's centre detent carries the stage's odd interval** — the 4th on the two
`3RD` stages, the 5th on `5TH` — and the two throws are the two thirds, `MAJ` and `MIN`.
That is partly ergonomic, since the thirds are the pair you reach for when building a
chord, and partly forced: the centre mark is the only one with nowhere to go but the
1.2 mm strip between the toggle nut and the box, where a single character fits and two do
not. It is set at 1.0 mm, below the house 1.6 mm minimum, and is the one deliberate
exception on the panel.

#### Hole schedule

Origin top-left, millimetres, Y down — the drawing's own frame, not the old gerbers'.

| Y (mm) | X (mm) | Ø | What |
|---:|---:|---:|---|
| 3.00 | 12.50 | 6.4×3.2 | mounting slot, obround |
| 16.60 | 4.60 | 6.0 | IN1 |
| 16.60 | 15.40 | 6.0 | IN2 |
| 28.60 | 4.60 | 6.0 | IN3 |
| 28.60 | 15.40 | 6.0 | SUM (output, ringed) |
| 44.80 | 4.60 | 5.0 | OCT polarity +/o/− |
| 44.80 | 15.40 | 5.0 | 3RD polarity +/o/− |
| 57.80 | 4.60 | 5.0 | OCT select 1/2 |
| 57.80 | 15.40 | 5.0 | 3RD select MAJ/MIN (detent 4) |
| 68.80 | 4.60 | 6.0 | OUT1 |
| 68.80 | 15.40 | 6.0 | OUT2 |
| 88.00 | 4.60 | 5.0 | 3RD polarity +/o/− |
| 88.00 | 15.40 | 5.0 | 5TH polarity +/o/− |
| 101.00 | 4.60 | 5.0 | 3RD select MAJ/MIN (detent 4) |
| 101.00 | 15.40 | 5.0 | 5TH select MAJ/MIN (detent 5) |
| 112.00 | 4.60 | 6.0 | OUT3 |
| 112.00 | 15.40 | 6.0 | OUT4 |
| 125.50 | 7.50 | 6.4×3.2 | mounting slot, obround |

Mounting follows the style guide's ≤ 6 HP rule: one 6.4 × 3.2 mm horizontal slot top-right
and one bottom-left, so the module can slide ±1.6 mm to meet its neighbours and cannot
pivot on a single screw per rail. v2.2's round Ø3.2 holes do not carry over.

#### What the generator checks, and what it cannot

`gen_panel.py` refuses to write if anything overlaps, and reports the tightest clearance in
each category. Currently: **0.25 mm** text-to-nut, **0.64 mm** text-to-text, **0.25 mm**
text-to-silk, **0.42 mm** text-to-ring, **0.60 mm** silk-to-edge, **1.40 mm** of material
at the worst hole, and **2.80 mm** between the closest two nuts. `SUM`'s ring is exempted
from the edge margin and reported separately, so the exception stays visible instead of
being absorbed into a looser rule.

Those come from a stroke-glyph model that assumes ink fills 0.62 em of each character
cell — conservative for the KiCad stroke font, but still a model. **KiCad's own DRC passes
with 0 violations and 0 unconnected items** (`tools/kicad-check.sh`), and the board plots
correctly from KiCad, mounting slots and all.

The two toggles in a group are 13.0 mm apart, leaving 5.5 mm between their nuts — up from
4.9 mm in the row-based draft, but still unproven on this hardware, since v2.2 stacks no
toggles at all. Print the SVG at 100%, check it measures 20 × 128.5 mm, and try the pairs
with real fingers.

### Schematic

[`docs/v3-adder.kicad_sch`](docs/v3-adder.kicad_sch), generated by
[`tools/gen_schematic.py`](tools/gen_schematic.py) from a netlist table:

```sh
python3 tools/gen_schematic.py             # writes the .kicad_sch, with a design report
python3 tools/gen_schematic.py --bom       # bill of materials
python3 tools/gen_schematic.py --netlist   # every net and what is on it
```

**It is a scaffold, not a finished drawing.** Connectivity is complete and correct;
placement is a plain grid, and every connection is made with a net label on a short pin stub
rather than by routing wires. That is deliberate — label-based connectivity cannot be got
subtly wrong the way routed wires can, and rearranging symbols in KiCad afterwards breaks
nothing. Expect to spend time on layout, not on wiring.

Topology follows [`docs/v2.2-topology.md`](docs/v2.2-topology.md). The reference block, the
power block and the summing topology are v2.2's, unchanged. 102 parts, 72 nets, 12 op-amp
channels across three OPA4196 — 11 used, one spare tied off as a follower.

**Only the lower ladder segments need to be precise.** A tap's voltage is set by the ratio
of the segments below it to the whole chain, and the trimmer sits in series at the top, so
the top segment's absolute value is absorbed by trimming — which is why the BOM shows
5.5k, 24.5k and 22.5k and why that does not matter. Use the nearest E96 part and let the
trimmer take up the difference. What does matter is the ratio between the small segments
(1k, 3k, 12k), and that is where hand-matched parts earn their keep.

Alongside the schematic the generator writes `adder.kicad_sym`, `v3-adder.kicad_pro` and a
`sym-lib-table`, so the project opens with its symbol library resolved rather than warning
once per symbol.

**KiCad's own ERC passes with 0 errors.** Run it yourself:

```sh
KICAD_CLI="/path/to/kicad-cli" tools/kicad-check.sh    # ERC, DRC and plots into .kicadcheck/
```

The 23 remaining ERC warnings are all `footprint_link_issues` on the custom parts — jacks,
toggles, trimmers, ferrites, the Eurorack header. Those footprints are yours to supply, and
a name that does not resolve is a more honest placeholder than a wrong one that does. Stock
KiCad footprints are used everywhere they exist, so the passives, op-amps, regulators and
diodes resolve on any install.

The generator additionally checks, before writing: every `lib_id` resolves as a full
`library:name` string and every instantiated unit has a matching body; every pin coordinate
read back out of the written file lands on a wire endpoint, so the label stubs really do
attach; no pin is unconnected; no net has fewer than two connections; no reference is used
twice and no pin appears on two nets; and every ladder tap computes to its interval voltage
exactly with the trimmer centred.

### Stages

Read the selector column as **up / _centre detent_ / down**, which is how the panel is
marked: the two throws are the thirds, the detent is the stage's odd interval.

| Stage | Panel group | Control | Selects — up / _detent_ / down | Values | Volts |
|---|---|---|---|---|---|
| 1 | `OCT` | on-off-on + `1/2` on-on | 1 oct / — / 2 oct | ±12, ±24 st | 1.000000 / 2.000000 |
| 2 | `3RD` | on-off-on + quality on-on-on | M3 / _4th_ / m3 | ±4, ±5, ±3 st | 0.333333 / 0.416667 / 0.250000 |
| 3 | `3RD` | on-off-on + quality on-on-on | M3 / _4th_ / m3 | ±4, ±5, ±3 st | 0.333333 / 0.416667 / 0.250000 |
| 4 | `5TH` | on-off-on + quality on-on-on | M3 / _**5th**_ / m3 | ±4, ±7, ±3 st | 0.333333 / 0.583333 / 0.250000 |

The values are unchanged from earlier drafts — only which throw carries which. Stage 1's
magnitude switch is a two-position ON-ON, so it has no detent.

Stage 4 takes a **5th** where stages 2 and 3 take a 4th. That buys back the one-switch fifth — the module's most-used interval — and on the chord side it turns stage 4 into an extension selector, since stages 2 and 3 have already built the triad by the time the signal reaches it.

**1715 configurations, 83 distinct voltages, fully chromatic across ±41 semitones (±3.42 octaves), all 12 pitch classes.**

### Chords

The cascade means each output is a running sum, so `OUT1`-`OUT4` are stacked intervals, with `PT` available as an untransposed root beneath them. **Stages 2 and 3 set the triad; stage 4 sets the extension.**

| Triad (st2 + st3) | st4 = m3 | st4 = M3 | st4 = 5th |
|---|---|---|---|
| M3 + m3 — **major** | dominant 7th | major 7th | add9 |
| m3 + M3 — **minor** | minor 7th | minor-major 7th | minor add9 |
| m3 + m3 — **diminished** | diminished 7th | half-diminished | dim add b9 |
| M3 + M3 — **augmented** | augmented maj7 | augmented (8ve) | augmented #9 |

Twelve voicings from three switches, and the triad is already correct on `OUT1`-`OUT3` before stage 4 is touched. The 4th position on stages 2 and 3 adds sus and quartal voicings on top of that.

The `OCT` stage transposes the whole chord while `PT` holds the original root — so a pedal tone stays put underneath a transposed voicing.

This is what the old `{octave, 5th, 4th, maj 3rd}` set could not do: fifths and fourths do not stack into chords.

### Transposition chart

Taking `OUT4` as a single transposed voice. `o` = switch centered. Within any octave the settings are identical, so the `OCT` stage handles everything above; negative intervals are the mirror image.

| Semitones | Volts | Interval | OCT | st2 | st3 | st4 | Flips |
|---:|---:|---|:---:|:---:|:---:|:---:|---:|
| 0 | 0.0000 | unison | `o` | `o` | `o` | `o` | 0 |
| 1 | 0.0833 | min 2nd | `o` | `o` | `+4th` | `-M3` | 2 |
| 2 | 0.1667 | maj 2nd | `o` | `o` | `+4th` | `-m3` | 2 |
| 3 | 0.2500 | min 3rd | `o` | `o` | `o` | `+m3` | 1 |
| 4 | 0.3333 | maj 3rd | `o` | `o` | `o` | `+M3` | 1 |
| 5 | 0.4167 | 4th | `o` | `o` | `+4th` | `o` | 1 |
| 6 | 0.5000 | tritone | `o` | `o` | `+m3` | `+m3` | 2 |
| 7 | 0.5833 | 5th | `o` | `o` | `o` | `+5th` | **1** |
| 8 | 0.6667 | min 6th | `o` | `o` | `+4th` | `+m3` | 2 |
| 9 | 0.7500 | maj 6th | `o` | `o` | `+4th` | `+M3` | 2 |
| 10 | 0.8333 | min 7th | `o` | `o` | `+m3` | `+5th` | 2 |
| 11 | 0.9167 | maj 7th | `o` | `o` | `+M3` | `+5th` | 2 |
| 12 | 1.0000 | octave | `+1` | `o` | `o` | `o` | 1 |

Every interval up to the octave is one or two switch positions, and the octave, 4th, 5th, maj 3rd and min 3rd are all single flips. The remaining rows read as stacks — a tritone is two minor thirds, a major 7th is a major third over a fifth.

### Build notes

- **BOM:** 4x `SUBMINI_SPDT ON-OFF-ON` (polarity, one per stage), 3x `ON-ON-ON` DPDT (quality, stages 2-4), 1x `ON-ON` (octave magnitude). 8 jacks instead of 12.
- Resistor values needed: 1.000000 and 2.000000 V (already on the v2.2 board), 0.583333 V (the existing 5th) and 0.416667 V (the existing 4th), plus 0.333333 V and 0.250000 V (new). Every v2.2 divider is reused; only the two third values are added.
- The three input summing resistors must be matched — this is where the "precision" in the name is spent. Doepfer specs 0.1% on the A-185-2 for the same reason.
- **Headroom:** three summed inputs plus up to ±3.25 octaves of offset can rail a ±12 V supply. Worth checking the worst case for the intended sources rather than assuming.
- No normalling on `IN2`/`IN3` — an unpatched input should contribute 0 V, not a fixed offset. (Doepfer normals its inputs to +1 V so they double as octave switches; here the octave stage already does that job.)
- All inputs stay at unity gain. An attenuator on one input would be useful for modulation depth, but it compromises the precision identity — that is the A-185-2's tradeoff, not this one's.

## Comparison: Doepfer A-185-2

The obvious commercial reference point, and the source of the ON-OFF-ON idea. (The A-185-2V is the Vintage Edition — beige panel, functionally identical.)

The A-185-2 is a **summer first and an offset generator second**. It has four CV inputs — one with a log attenuator, three without — each with a three-position add/off/subtract switch, and every input normalled to +1 V. Its intended job is combining keyboard + sequencer 1 + sequencer 2; the offset capability falls out of the normalling. Unpatched, you get three switches at ±1 octave plus the attenuated channel as a continuous 0...±1 V fine tune. Total range ±4 V, the same as v2.2, but the switched part is only `{0, ±12, ±24, ±36}` semitones — 7 distinct values out of 27 combinations, since all three sections are the same 1 V.

| | A-185-2 | v2.2 | v3 |
|---|---|---|---|
| Width | 6 HP | — | — |
| Summing inputs | 4 (1 attenuated) | 1 (+3 cascade breaks) | 3 |
| Interval stages | 4 | 4 | 4 |
| Switch type | ON-OFF-ON | ON-ON | ON-OFF-ON + ON-ON-ON |
| Bypass a stage | center detent | patch `PT`->`IN` | center detent |
| Offset values | 1 V x3 (octaves only) | 2, 1, 0.5833, 0.4167 V | 1/2 oct; 4th/M3/m3 x2; 5th/M3/m3 |
| Switched distinct values | 7 | 39 | 83 |
| Non-octave intervals | knob only, not exact | exact 4th/5th | exact 3rd/4th/5th |
| Fully chromatic | via knob, unrepeatable | no (5/12 pitch classes) | yes, ±41 st |
| Chord voices | 1 | 4 (cumulative) | 4 + root, 12 voicings |
| Inverting output | yes | no | no |
| Input attenuator | yes (log) | no | no |
| Outputs | 3x sum + 1x inverted | per-stage taps | per-stage taps + `PT` |
| A-100 bus CV | yes (JP5) | no | no |
| Accuracy | 0.1% matched | — | — |

**What the Doepfer cannot do:** produce an exact fifth. Its only non-octave path is a log potentiometer — you can get close by ear, but not to 0.583333 V repeatably, and not back to it after moving the knob. That gap is the reason this module exists.

**What this module cannot do:** invert or attenuate its input, or reach the A-100 bus. The ± switches negate each stage's own contribution, not the incoming CV; the A-185-2's inverting output negates the entire sum. That is a real feature absent here and not fakeable with the current topology.

They are complementary rather than competing — the Doepfer is the better general-purpose summer, this is the better interval and chord source. v3 narrows the gap on summing by taking three inputs at the front. The one thing worth taking wholesale is the switch: center-off is a BOM choice, not a design constraint, and v2.2 pays a patch cable per bypass for want of it.

Sources: [A-185-2 specification](https://doepfer.de/a185_2.htm), [Doepfer product page](https://www2.doepfer.eu/en/item/a185-2).

## Appendix: interval set study

Where the v3 numbers come from. All of it is reproducible with [`interval-study.py`](interval-study.py) (no dependencies, `python3 interval-study.py`).

### Method

Each stage contributes `+v`, `-v`, or `0`, so N stages give 3^N configurations. On v2.2 the zero state costs a patch cable (`PT` -> `IN` of the next stage) because the switches are ON-ON; on v3 it is the center detent of an ON-OFF-ON. The arithmetic is identical either way, so every chart below applies to both. Values are in semitones; 1 semitone = 1/12 V. Three metrics are reported:

- **distinct** — how many different output voltages the module can produce. Below the combination count means stages are redundant with each other.
- **chromatic ±N** — the widest symmetric range around 0 in which *every* semitone is reachable. This is the metric that matters; a set can have plenty of distinct values and still be useless for chromatic work.
- **pc** — how many of the 12 pitch classes are reachable at all.

Baseline for v2.2 `{24,12,7,5}`: **39 distinct / 81 combos, chromatic ±0, 5/12 pitch classes.**

### Chart 1 — one stage added to v2.2

| Added | Interval | Distinct | Chromatic | Pitch classes |
|---:|---|---:|---:|---:|
| +1 | min 2nd | 95 | ±44 | 12/12 |
| +2 | maj 2nd | 73 | ±0 | 9/12 |
| +3 | min 3rd | 89 | ±5 | 11/12 |
| **+4** | **maj 3rd** | **97** | **±45** | **12/12** |
| +5 | 4th | 57 | ±0 | 7/12 |
| +6 | tritone | 83 | ±2 | 10/12 |
| +7 | 5th | 57 | ±0 | 7/12 |
| +8 | min 6th | 99 | ±44 | 12/12 |
| +9 | maj 6th | 89 | ±5 | 11/12 |
| +10 | min 7th | 75 | ±0 | 9/12 |
| +11 | maj 7th | 99 | ±38 | 12/12 |
| +12 | octave | 49 | ±0 | 5/12 |

A major third is the best single addition — widest chromatic range, all 12 pitch classes, and musically it is what turns octave/fifth stacking into triads. Note the traps: the minor third and major sixth look appealing but top out at 11/12 pitch classes, and the one they cannot reach is the tritone. Adding another 4th, 5th, or octave is nearly worthless, because those are already in the span of the existing stages.

### Chart 2 — best 4-value sets, unconstrained (search 1..27)

| Set | Distinct | Chromatic |
|---|---:|---:|
| **(1, 3, 9, 27)** | **81/81** | **±40 (3.33 oct)** |
| (2, 3, 9, 27) | 81/81 | ±39 (3.25 oct) |
| (1, 3, 9, 26) | 79/81 | ±39 (3.25 oct) |
| (1, 3, 9, 25) | 77/81 | ±38 (3.17 oct) |
| (3, 4, 9, 27) | 81/81 | ±37 (3.08 oct) |
| (1, 6, 9, 27) | 81/81 | ±37 (3.08 oct) |
| (2, 3, 9, 25) | 77/81 | ±37 (3.08 oct) |
| (1, 3, 9, 24) | 75/81 | ±37 (3.08 oct) |

`{1, 3, 9, 27}` is balanced ternary — each stage 3x the one before, which is exactly the condition for no combination to duplicate another. 81 configurations produce 81 distinct voltages covering every semitone from -40 to +40, each by exactly one switch setting. No four values can beat this, because 81 states cannot cover more than 81 notes.

Voltages: 1 st = 1/12 = 0.083333 V, 3 st = 1/4 = 0.250000 V, 9 st = 3/4 = 0.750000 V, 27 st = 9/4 = 2.250000 V. Three of the four are exact quarter-volt multiples in a 1:3:9 ratio off a single reference, so it is also the cleanest of these to build.

**This is the theoretical maximum, and v3 does not use it.** No four values reach further or waste less. But the panel would be unplayable: 2 octaves is `27 - 3`, a fourth is `9 - 3 - 1`, and reading an interval off the switches means decoding balanced ternary. It is the right answer to "how many distinct voltages can four switches make" and the wrong answer to "what should the panel say." See Chart 8.

### Chart 3 — constrained: keep both octave stages (12 and 24)

| Set | Distinct | Chromatic |
|---|---:|---:|
| {24,12,9,11} | 63/81 | ±4 |
| {24,12,3,11} | 63/81 | ±4 |
| {24,12,1,9} | 63/81 | ±4 |
| {24,12,1,3} | 63/81 | ±4 |
| {24,12,9,10} | 63/81 | ±3 |

This is the case against keeping the v2.2 layout. Spending two of four stages on octaves leaves only two to fill twelve semitones, and nothing does better than ±4. The octave stages are the problem, not the fifth and fourth.

### Chart 4 — constrained: keep one octave stage (12)

| Set | Distinct | Chromatic |
|---|---:|---:|
| {12,1,9,27} | 81/81 | ±31 |
| {12,2,9,27} | 81/81 | ±30 |
| {12,4,11,25} | 79/81 | ±30 |
| {12,4,13,23} | 77/81 | ±29 |

Keeping one labeled octave switch is affordable — still 81/81 distinct, at a cost of about 20% of the chromatic range versus pure ternary.

### Chart 5 — collapsed octave stage, best 3-value fill

With stage 1 collapsed to a 5-state element (±big, ±small, bypassed), three stages remain free. 135 configurations.

| Magnitude switch | Fill | Distinct | Chromatic |
|---|---|---:|---:|
| 1V/2V | (4, 9, 19) | 93 | ±40 (3.33 oct) |
| 1V/2V | (1, 9, 15) | 87 | ±40 (3.33 oct) |
| 1V/2V | (2, 9, 15) | 87 | ±39 (3.25 oct) |
| **1V/3V** | **(1, 3, 9)** | **99** | **±49 (4.08 oct)** |
| 1V/3V | (2, 3, 9) | 99 | ±48 (4.00 oct) |
| 1V/3V | (1, 3, 8) | 97 | ±48 (4.00 oct) |

### Chart 6 — four stages added to v2.2 (8 total, 6561 combos)

| Added | Distinct | Chromatic |
|---|---:|---:|
| (8, 9, 11, 12) | 167 | ±81 (6.75 oct) |
| (8, 10, 11, 12) | 167 | ±79 (6.58 oct) |
| (8, 9, 10, 11) | 163 | ±79 (6.58 oct) |
| (4, 10, 11, 12) | 163 | ±78 (6.50 oct) |

Included for completeness — an expander rather than a revision. Note the diminishing returns: 6561 configurations yield only 167 distinct voltages. That is not mainly redundancy, it is arithmetic — output range is bounded by the *sum* of the stage values (here 88 semitones, so 177 integers maximum), which grows linearly while configurations grow as 3^N. Small values like these are close to saturating what is available. Beyond about four well-chosen stages, extra stages buy range, not resolution.

### Chart 7 — summary

| Design | Distinct | Combos | Chromatic | Pitch classes |
|---|---:|---:|---:|---:|
| v2.2 {24,12,7,5} | 39 | 81 | ±0 | 5/12 |
| ternary {1,3,9,27} | 81 | 81 | ±40 (3.33 oct) | 12/12 |
| collapsed 1V/2V + {1,3,9} | 75 | 135 | ±37 (3.08 oct) | 12/12 |
| collapsed 1V/2V + {4,9,19} | 93 | 135 | ±40 (3.33 oct) | 12/12 |
| collapsed 1V/3V + {1,3,9} | 99 | 135 | ±49 (4.08 oct) | 12/12 |
| collapsed 1V/2V + {4,2,1} | 63 | 135 | ±31 (2.58 oct) | 12/12 |
| collapsed 1V/2V + {7,5,4} | 73 | 135 | ±33 (2.75 oct) | 12/12 |
| **oct + {5,4,3},{5,4,3},{7,4,3}** (v3) | **83** | **1715** | **±41 (3.42 oct)** | **12/12** |

### Chart 8 — usability

Range is not the only axis, and on its own it picks the wrong design. Two ergonomic measures:

- **max fill** — the largest number you ever have to reach on the non-octave stages. At or below 12 you never count past an octave in your head.
- **flips** — switches moved from all-off to reach an interval. With ON-OFF-ON switches this is literal; on v2.2 hardware some of these "flips" are patch cables instead, which is a further argument for the center-off variant.

| Design | Chromatic | Max fill | Intervals reachable | Avg flips | Mental model |
|---|---:|---:|---:|---:|---|
| v2.2 {24,12,7,5} | ±0 | 48 | 5/12 | 1.60 | interval names |
| ternary {1,3,9,27} | ±40 | 40 | 12/12 | 2.00 | balanced ternary |
| collapsed 1V/3V + {1,3,9} | ±49 | 13 | 12/12 | 1.83 | balanced ternary |
| collapsed 1V/2V + {4,2,1} | ±31 | 7 | 12/12 | 1.83 | binary 0-7 |
| **collapsed 1V/2V + {7,5,4}** | **±33** | **16** | **12/12** | **1.83** | **interval names** |

Cost per interval, cheapest setting:

| Interval | v2.2 | 1V/2V + {7,5,4} | 1V/2V + {4,2,1} | 1V/3V + {1,3,9} |
|---|---|---|---|---|
| min 2nd | — | 2 | 1 | 1 |
| maj 3rd | — | **1** | 1 | 2 |
| 4th | 1 | **1** | 2 | 3 |
| tritone | — | 3 | 2 | 2 |
| 5th | 1 | **1** | 3 | 3 |
| maj 6th | — | 2 | 3 | 1 |
| octave | 1 | **1** | 1 | 1 |
| oct + 5th | 2 | **2** | 3 | 4 |
| 2 octaves | 1 | **1** | 1 | 3 |

All three complete designs average 1.83 flips, so the average is not the deciding number — the *distribution* is. `{7,5,4}` spends its one-flip settings on the octave, fifth, fourth, and major third; the ternary set spends them on the minor 2nd, minor 3rd, and major 6th. The binary fill `{4,2,1}` is the honest middle (plain addition to 7, labelable as M3 / tone / semitone) but makes the fifth a three-flip operation to buy chromatic coverage that `{7,5,4}` already provides.

Note that `{7,5,4}` has the worst "max fill" of these at 16, because the tritone and a few neighbours are cheapest via a fifth plus a fourth plus a third. In practice this never bites: the fill settings repeat identically in every octave, so the settings repeat identically in every octave.
