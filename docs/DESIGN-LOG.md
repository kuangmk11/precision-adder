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
- ~~**Panel layout.**~~ **Resolved twice.** Layout and hole table are in the README's
  Panel section; both outputs come from [`../tools/gen_panel.py`](../tools/gen_panel.py).

  *First attempt — inherited holes.* The v2.2 panel is already 8 rows x 2 columns = 16
  positions, so v3 reused every hole *position* from
  `Gerber_precision-adder-new-better-panel` and only reassigned diameters between 6 mm
  jack and 5 mm toggle (8 of 18 changed). Two things fell out of drawing it. The
  silkscreen is the binding constraint, not the holes: a 6 mm jack in a 10.6 mm column
  pitch leaves 0.7 mm to the panel edge, so nothing can be labelled outboard of either
  column and every mark has to live in the centre channel or the vertical gaps. And the
  grouping was forced — three summed inputs sit together, so some rows carry two toggles,
  so a stage's `OUT` could not share its row. Outputs landed in pairs, row 5 serving the
  two switch rows above it and row 8 the two above it. Legible, but the panel could not
  say which output belonged to which stage.

  *Second — grouped, on new holes.* One box per stage: polarity switch, selector switch,
  that stage's own output. Six evenly spaced rows below the inputs, which the inherited
  pitches (12.4 / 15.9 / 16.2 / 12.4 mm) could not give, so the positions were refitted.
  The v3 main board is new anyway, and the style guide's inherit rule covers this case —
  positions are fitted once when the board is laid out, and inherited from then on. These
  are now that datum.

  What the grouping cost: a three-position selector needs a mark at its centre detent,
  and the only clear width at that height is the ~1.2 mm strip between the toggle nut and
  the box edge. One character fits there, two do not. So the detent carries the stage's
  odd interval — the 4th, or the 5th on stage 4 — and the two throws carry `MAJ` and
  `MIN`. It reads well, since the thirds are the pair you reach for, but it was a
  constraint before it was a preference. That mark is set at 1.0 mm against a house
  minimum of 1.6, and is the panel's one deliberate exception.

  Marks straddling the box edge were tried first and rejected: the two columns' detent
  marks ended up 1.6 mm apart across the centre line, where `4` and `5` read as the
  number 45 and neither belonged to a group. Inside its own box, each is unambiguous.

  The divider above the stages came out — four boxed groups already separate themselves
  from the input block, and the rule was doing the job twice.

  **`SUM`'s ring does not close.** It is an output, so it takes the ring, but a ring is
  only visible if it clears the 8 mm nut, and a 20 mm panel carrying two 8 mm nuts has
  4 mm of slack in total. At r 4.4 the ring reaches 0.6 mm from the cut on the outboard
  side, so it is drawn as a ~310° arc with the gap there. Moving the columns inboard to
  fit a full circle would shrink the detent strip below what a character needs, so the
  arc is the cheaper compromise. `OUT1`-`OUT4` get no ring at all: each is inside a named
  box, and a second closed circle would cost `SUM`'s ring its meaning.

  The cascade arrows run across the top pair, down into the bottom-left group, and across
  the bottom pair. The middle leg is a dogleg rather than a diagonal — 4 mm of band
  against 10.8 mm of column pitch is a 15° line, and house routing is 0/90/45.

  **Still to check:** the two toggles in a group are 13.0 mm apart, leaving 5.5 mm
  between nuts — better than the 4.9 mm of the row-based draft, still unproven here since
  v2.2 stacks no toggles. 1:1 print and a finger test before any fab order. And no DRC
  has been run: KiCad is not installed on the machine that generated the board.
- **`ON-ON-ON` variant.** Type 1 vs Type 2 differ in which pole combinations the
  three positions produce. Not yet pinned down for the quality switches.
