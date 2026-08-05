# Design log — v3, 2026-08-03

How the v3 proposal in the README was arrived at, including the options that were
rejected and why. The charts and numbers live in the README appendix; this file is
the reasoning and the dead ends, which the appendix does not record.

Raw session transcript: `docs/session-2026-08-03-v3-design.jsonl` (gitignored, local only).
Everything numeric here is reproducible with `interval-study.py`.

---

## 1. The v2.2 defect

Started by enumerating what v2.2 can actually produce. With ON-ON switches and
bypass-by-patching, four stages of `{24, 12, 7, 5}` semitones give 81 configurations
but only **39 distinct voltages**, and the reachable pitch classes are just
`{0, 2, 5, 7, 10}` — the suspended pentatonic.

Cause: **a fifth plus a fourth is exactly an octave** (7 + 5 = 12). Two of the four
stages are redundant with the octave stages. No thirds, no sixths, no tritone, no
semitones, ever.

## 2. Interval set search

Searched all 4-value sets 1..27. The mathematical optimum is **balanced ternary
`{1, 3, 9, 27}`** — each stage 3x the previous, 81 configurations producing 81
distinct voltages, every semitone from -40 to +40, zero redundancy. Provably
unbeatable: 81 states cannot cover more than 81 notes.

**Rejected on usability.** In balanced ternary, 2 octaves is `27 - 3` and a fourth
is `9 - 3 - 1`. Every setting is arithmetic in a base nobody thinks in, and the
panel cannot be read as intervals. The objection that killed it: *most people cannot
calculate semitones past an octave.*

This reframed the whole problem. Chromatic range is not the objective function —
**cost per interval you actually use** is. All complete designs average ~1.83 switch
flips across the twelve intervals; what separates them is *which* intervals get the
cheap settings. Balanced ternary spends its one-flip settings on the minor 2nd,
minor 3rd and major 6th. Named-interval sets spend them on the octave, fifth and
fourth.

## 3. Rejected mechanical options

**5-position rotary for the octave stage** (`-2 -1 0 +1 +2`). Elegant on paper: one
legible control, one hole. Killed by the side photo — the build is a two-board
sandwich with the front PCB about 10-11 mm behind the panel (set by the Thonkiconn
bushing). A panel-mount rotary is 20-25 mm deep and would crash through the front
board. Correct answer to "which control is most legible", wrong answer to "what fits".

**Keeping both octave stages.** Searched: spending two of four stages on octaves
caps the chromatic range at ±4 semitones regardless of what the other two are. The
octave stages were the problem, not the fifth and fourth.

**Adding four more stages to v2.2** (8 total, 6561 configurations). Only 167 distinct
voltages, because output range is bounded by the *sum* of stage values, which grows
linearly while configurations grow as 3^N. Past about four well-chosen stages, extra
stages buy range, not resolution.

## 4. The switch — taken from Doepfer

The A-185-2 uses **ON-OFF-ON** toggles, so a stage's off position is a center detent
rather than a patch cable. v2.2 uses ON-ON. Same footprint, essentially the same
price. This is a BOM choice, not a design constraint, and it invalidated a chunk of
earlier reasoning that had been working around the cost of patch-bypassing.

Also from the comparison: the A-185-2 is a *summer* first, with octave offsets falling
out of its +1 V input normalling. Its only non-octave path is a log pot, so **it
cannot produce an exact fifth** — which is precisely the gap this module fills.
Conversely it has an inverting output and an input attenuator, which this module
does not and cannot fake.

## 5. The normalling discovery

The README's original description — "each input cascades to the one below it if
there's no input below" — reads as input-to-input normalling. It is actually
**output-to-input**: `OUT1` normals to `IN2`, so with nothing patched `PT2` = `OUT1`,
`PT3` = `OUT2`, `PT4` = `OUT3`.

Consequence: **`PT2`-`PT4` are duplicates of the output above them**, and `IN2`-`IN4`
exist only to break the cascade — which the center-off switch now does better. Six
jacks doing the work of two. This was confirmed by the author mid-session and the
opening line of the README was corrected.

An earlier hypothesis in this session — that the passthrus were needed as buffered
mults to feed a parallel "same root to every stage" harmony mode — was wrong. That
mode does not exist by default.

## 6. The reframe: it is a chord generator

Given the cascade is the default and each `OUT` is a *running sum*, the four outputs
are **stacked intervals**. Stacking thirds is how chords are built. Three stages of
maj-or-min third produce every standard tetrad, on the outputs, simultaneously.

That is what the module is uniquely good at, and it is what the old `{octave, 5th,
4th, maj 3rd}` set could not do — fifths and fourths do not stack into chords.

Final refinement: stage 4 takes a **5th** where stages 2 and 3 take a 4th. Placement
is free for transposition (a sum does not care about order), so it was chosen on
chord grounds — stages 2-3 finish the triad, stage 4 becomes an extension selector
(m3 → 7th, M3 → maj7, 5th → add9). It also buys back the one-flip fifth.

## 7. Where it landed

Three summed inputs, four cascaded stages, 8 jacks + 8 switches = 16 panel positions,
identical to v2.2. 1715 configurations, 83 distinct voltages, fully chromatic across
±41 semitones, all 12 pitch classes, 12 chord voicings. Every v2.2 resistor divider
is reused; only the two third values are new.

## 8. Open questions

- **Headroom.** Three summed inputs plus up to ±3.42 octaves of offset can rail a
  ±12 V supply. The worst case for the intended sources has not been worked.
- **Input summing resistor matching.** This is where 1V/oct accuracy is spent once
  there are three inputs. Doepfer specs 0.1% for the same reason. Not yet specified here.
- ~~**Panel layout.**~~ **Resolved** — drawn in [`v3-panel.svg`](v3-panel.svg), 1:1.
  The v2.2 panel is already 8 rows x 2 columns = 16 positions, so v3 reuses the outline,
  the mounting holes and every hole *position* from
  `Gerber_precision-adder-new-better-panel`; only the diameter at each position is
  reassigned between 6 mm jack and 5 mm toggle (8 of 18 change, 10 do not). Layout and
  hole table are in the README's Panel section.

  Two things fell out of drawing it. First, the silkscreen is the binding constraint,
  not the holes: a 6 mm jack in a 10.6 mm column pitch leaves 0.7 mm to the panel edge,
  so nothing can be labelled outboard of either column and every mark has to live in the
  3.1 mm centre channel or in the vertical gaps. Second, the grouping is forced — three
  summed inputs have to sit together, which means some rows carry two toggles, which
  means the stage's `OUT` cannot share its row. Outputs therefore land in pairs, row 5
  serving the two switch rows above it and row 8 the two above it.

  **Still to check:** rows 3-4 and 6-7 place two toggles 12.4 mm apart vertically. v2.2
  never stacked toggles, so that spacing is unproven here — 1:1 print and a finger test
  before any fab order.
- **`ON-ON-ON` variant.** Type 1 vs Type 2 differ in which pole combinations the
  three positions produce. Not yet pinned down for the quality switches.
