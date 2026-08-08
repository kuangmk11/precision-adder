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

[`docs/v3-panel.svg`](docs/v3-panel.svg) is drawn 1:1 (1 SVG unit = 1 mm, 20 x 128.499 mm).
The grey rings are hardware footprints — 8 mm Thonkiconn nut, 7.5 mm toggle nut — shown
for clearance checking, not artwork.

Panel drawing conventions — lettering, marks, label placement, mounting — are in
[`PANEL_STYLE_v1.00.md`](PANEL_STYLE_v1.00.md).

**The 16 hole positions are v2.2's, unchanged.** The built panel already has 8 rows x 2
columns, which is exactly what v3 needs, so the outline, the mounting holes and every
hole *position* carry over; only the diameter at each position is reassigned between
6 mm jack and 5 mm toggle. Eight of the eighteen holes change size, ten do not.

| Row | Y (mm) | Left — X 4.699 | Right — X 15.299 |
|---:|---:|---|---|
| 1 | 113.149 | `IN 1` — Ø6 | `IN 2` — Ø6 |
| 2 | 100.749 | `IN 3` — Ø6 | `SUM` (`PT`) — Ø6 |
| 3 | 84.749 | `OCT` +/o/− — Ø5 (ON-OFF-ON) | `2` / `1` — Ø5 (ON-ON) |
| 4 | 72.349 | `3rd` +/o/− — Ø5 (ON-OFF-ON) | `4` / `M3` / `m3` — Ø5 (ON-ON-ON) |
| 5 | 56.449 | `OUT 1` — Ø6 | `OUT 2` — Ø6 |
| 6 | 44.049 | `3rd` +/o/− — Ø5 (ON-OFF-ON) | `4` / `M3` / `m3` — Ø5 (ON-ON-ON) |
| 7 | 27.849 | `EXT` +/o/− — Ø5 (ON-OFF-ON) | `5` / `M3` / `m3` — Ø5 (ON-ON-ON) |
| 8 | 15.449 | `OUT 3` — Ø6 | `OUT 4` — Ø6 |

Mounting holes Ø3.2 at X 7.499, Y 3.000 and 125.500. Origin bottom-left, as the gerbers
have it; the SVG flips Y (`y_svg = 128.499 − y_gerber`).

Reading it: **row 5 carries the outputs of the two switch rows above it, row 8 the two
above it.** The left column is always polarity (`+` above the toggle, `−` below, centre
detent off) and the right column is always the selector, so there is one rule for the
whole panel. `PT` is silkscreened `SUM`, which is what it is once three inputs are
summed at the front.

The layout is constrained by where text can physically go. A 6 mm jack in a 10.6 mm
column pitch leaves 0.7 mm to the panel edge, so no silkscreen fits outboard of either
column — every label lives in the centre channel or in the vertical gaps. That is why
input names sit below their jacks, output names above theirs (the gap below `OUT1`/`OUT2`
is needed by the next stage's label), and stage names sit slightly right of centre,
clear of the polarity marks.

**One thing the drawing cannot settle:** rows 3-4 and 6-7 put two toggles 12.4 mm apart
vertically. v2.2 has no two toggles stacked, so this spacing is unproven on this
hardware. Print the SVG at 100%, check it measures 20 x 128.5 mm, and check finger
clearance on those pairs before ordering anything.

### Stages

| Stage | Control | Selects | Values | Volts |
|---|---|---|---|---|
| 1 | `OCT` on-off-on + `1/2` on-on | 1 / 2 oct | ±12, ±24 st | 1.000000 / 2.000000 |
| 2 | `3rd` on-off-on + quality on-on-on | 4th / M3 / m3 | ±5, ±4, ±3 st | 0.416667 / 0.333333 / 0.250000 |
| 3 | `3rd` on-off-on + quality on-on-on | 4th / M3 / m3 | ±5, ±4, ±3 st | 0.416667 / 0.333333 / 0.250000 |
| 4 | `EXT` on-off-on + quality on-on-on | **5th** / M3 / m3 | ±7, ±4, ±3 st | 0.583333 / 0.333333 / 0.250000 |

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
