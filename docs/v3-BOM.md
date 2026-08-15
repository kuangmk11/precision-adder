# v3 bill of materials

Built for **hand assembly**: 1206 everywhere an SMD part is used, and through-hole kept for
anything that was already through-hole. 1206 is the largest size these values are commonly
stocked in, and the OPA4196's SOIC-14 is the largest package it comes in.

101 components. Values verified against the ladder maths in `v2.2-topology.md` — every
interval tap lands **exact to 0.000 cents** with these parts.

## Resistors

All 1206, `Resistor_SMD:R_1206_3216Metric`.

### 0.1 % — 32 parts

These set pitch directly. The per-stage trimmer corrects the chain's overall scale but
**not the ratios between taps**, so tolerance here is not recoverable.

| Qty | Value | Designators | Role |
|---:|---|---|---|
| 20 | 10.0k | R5–R7, R9, R15–R18, R25–R28, R35–R38, R45–R48 | input summing, per-stage summing and ×2 gain pairs |
| 5 | 1.00k | R21, R22, R31, R32, R41 | ladder segments |
| 4 | 3.00k | R20, R30, R40, R42 | ladder bottom segments |
| 2 | 12.0k | R11, R12 | `OCT` ladder — **match these two to each other** above all |
| 1 | 20.0k | R8 | input summer gain, ratio with R9 |

**3.00k and 12.0k are E24, not E96, and that is deliberate.** E96 has no exact 3:1 pair —
its nearest is 3.01k against 1.00k, which is a 0.33 % ratio error and puts the 4th out by
0.66 cents. Worse, that error cannot be selected away: a 0.1 % 3.01k never measures 3.000k.
E24 values are stocked in 0.1 % thin film, so use them.

`OCT` only needs its two segments **equal to each other** — the absolute value is free,
because the trimmer sets the scale and the second tap is twice the first by construction.
A matched pair matters more than the marked value.

### 1 % is fine — 17 parts

| Qty | Value | Designators | Why tolerance does not matter |
|---:|---|---|---|
| 5 | 1.00k | R10, R19, R29, R39, R49 | output series protection |
| 4 | 49.9k | R1–R4 | reference dividers — trimmed by VR5/VR6 |
| 4 | 619R | R14, R24, R34, R44 | buffer output snubbers |
| 2 | 24.3k | R23, R33 | ladder top, absorbed by trim |
| 1 | 22.6k | R43 | ladder top, absorbed by trim |
| 1 | 5.49k | R13 | ladder top, absorbed by trim |

## Capacitors

| Qty | Value | Type | Designators | Footprint |
|---:|---|---|---|---|
| 7 | 0.1uF | X7R | C8, C11–C16 | `Capacitor_SMD:C_1206_3216Metric` |
| 4 | 330pF | C0G | C17–C20 | `Capacitor_SMD:C_1206_3216Metric` |
| 2 | 10uF | electrolytic, **ESR ≥1 Ω, mount lying flat** | C9, C10 | `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm` |
| 2 | 10uF | electrolytic, any height, mounts upright | C1, C3 | `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm` |
| 2 | 0.33uF | X7R | C5, C7 | `Capacitor_SMD:C_1206_3216Metric` |
| 2 | 100pF | C0G | C2, C4 | `Capacitor_SMD:C_1206_3216Metric` |
| 1 | 0.01uF | X7R | C6 | `Capacitor_SMD:C_1206_3216Metric` |

C0G on the snubbers and the HF supply caps; X7R elsewhere is fine.

**C9 and C10 must be low-profile cans; C1 and C3 need not be.** The two boards
are stacked, and the only parts inside the gap are the ones on the control
board's rear face — which is where C9 and C10 live. C1 and C3 sit on the trimmer
board's rear, facing the back of the case, where nothing constrains them.

The gap is set by the interconnect: an 8.50 mm socket body plus the 2.54 mm
plastic of the mating header puts the two boards **11.04 mm** apart. That is the
whole budget for anything on the control board's rear, and the parts already
there use:

| | height above board |
|---|---|
| U4, U5 — TO-92 | 7.30 mm |
| C9, C10 — as modelled | 5.00 mm |
| U1–U3 — SOIC-14 | 1.75 mm |
| 1206 SMD | ~0.95 mm |

A 5 mm-diameter 10 µF is sold as a **5 × 11 mm** can, and 11 mm against 11.04 mm
is no clearance at all — stood upright it will foul the trimmer board. There is
no shorter part to buy; every stocked 5 mm 10 µF is 11 mm or longer.

**So C9 and C10 are laid flat**, leads bent 90° at the board, the can resting on
the control board's rear face. On its side the same part is 5.00 mm tall — the
figure in the table above — which leaves 6 mm of clearance. Anything up to 7 mm
is safe; past that the margin is not worth having.

### C9 and C10 need ESR, and "low ESR" is the wrong part

They hang directly off U3's reference buffer outputs, wired as unity-gain
followers — the worst case for capacitive load. **The OPA4196 is rated to drive
1 nF bare. These are 10 µF, ten thousand times that.** The capacitor's own ESR is
what keeps that loop stable, so it is a specified parameter here, not a defect to
be minimised.

TI's Table 3 (SBOS869) gives the series resistance needed for a given phase
margin, and stops characterising at 1 µF:

| C load | 100 pF | 1 nF | 10 nF | 100 nF | 1 µF |
|---|---|---|---|---|---|
| R for 45° | 280 Ω | 113 Ω | 68 Ω | 17.8 Ω | 3.6 Ω |
| R for 60° | — | 432 Ω | 210 Ω | 53.6 Ω | 10 Ω |

Extrapolating one decade puts 10 µF at roughly **0.8 Ω for 45° and 2.2 Ω for
60°**. Against what each capacitor type actually offers:

| Type, 10 µF | ESR | |
|---|---|---|
| ceramic X7R 1210 | 2–10 mΩ | ~200× too low |
| polymer tantalum, polymer aluminium | 20–100 mΩ | still far too low |
| **MnO2 tantalum, EIA-3528** | 0.5–3 Ω | in range |
| **aluminium electrolytic, 5 mm** | 1–3 Ω | in range |

So **do not substitute a ceramic, a polymer tantalum, or a "low ESR" aluminium
part here.** All three are marketed as upgrades and all three remove the damping.
An ordinary aluminium electrolytic — the last row of that table, and what the
board's through-hole footprint expects — sits squarely in range. Height is dealt
with by laying the can flat, as above, not by picking a different chemistry.

The ESR must be in the capacitor rather than a discrete resistor, even though TI
recommends the resistor. An isolation resistor sits between the amplifier output
and *everything*, so the ladder current flows through it: worst case is four
30 kΩ ladders selecting the positive reference, 333 µA. At the 10 Ω TI lists for
1 µF that is 3.3 mV of reference shift, moving the `OCT_2V` tap by 3.2 cents —
and the shift tracks how many switches point up, so it is not a fixed offset and
cannot be trimmed out. The capacitor's ESR carries no DC load current at all,
because the ladders connect to the amplifier output directly.

## Semiconductors

| Qty | Part | Designators | Footprint |
|---:|---|---|---|
| 3 | OPA4196 (SOIC-14) | U1, U2, U3 | `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm` |
| 1 | L78L05 | U4 | `Package_TO_SOT_THT:TO-92_Inline` |
| 1 | L79L05 | U5 | `Package_TO_SOT_THT:TO-92_Inline` |
| 2 | 1N5819 | D1, D2 | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` |

**The two regulators do not share a pinout.** L78L05 TO-92 is `1 = VOUT, 2 = GND, 3 = VIN`;
L79L05 is `1 = GND, 2 = VIN, 3 = VOUT`. Both datasheet figures are *bottom* views — check
the footprint's pad 1 against the datasheet with the part oriented as you will fit it.

## Electromechanical

| Qty | Part | Designators | Footprint |
|---:|---|---|---|
| 8 | Thonkiconn PJ398SM | J1–J8 | `eurorack:Thonkiconn_PJ301M` |
| 4 | Taiway `200-MSP3-T1B1M2QE` SPDT ON-OFF-ON | SW1–SW4 | `eurorack:SW_Taiway_200_SPDT` |
| 3 | Taiway `200-MDP6-T1B1M2QE` DPDT ON-ON-ON | SW6, SW7, SW8 | `eurorack:SW_Taiway_200_DPDT` |
| 1 | Taiway `200-MSP1-T1B1M2QE` SPDT ON-ON | SW5 | `eurorack:SW_Taiway_200_SPDT` |
| 4 | 1k multiturn trimmer | VR1–VR4 | `Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical` |
| 2 | 50k multiturn trimmer | VR5, VR6 | `Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical` |
| 2 | Ferrite bead, axial | FB1, FB2 | `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal` |
| 1 | Eurorack 2×5 shrouded header | P1 | `Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical` |
| 4 | 1×6 pin header, 2.54 mm | P2–P5 | `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical` |
| 4 | 1×6 socket, 2.54 mm | P6–P9 | `Connector_PinSocket_2.54mm:PinSocket_1x06_P2.54mm_Vertical` |

Keep the **shrouded, keyed** power header — it is the only thing that stops the ribbon
going on backwards, and D1/D2 are the last line of defence after it.

### Board-to-board interconnect

P2–P9 join the two cards. Pins go on the **control board's rear**, sockets on the
**trimmer board's front**, and the cards stack by a plain 20.2 mm translation with
no flip. Mating pairs:

| Pins (control board) | Socket (trimmer board) | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| P2 | P6 | GND | REFP_TOP | — | — | — | +12V |
| P3 | P7 | GND | LAD1_TOP | LAD2_TOP | S2_4th | LAD1_TRIM | −12V |
| P4 | P8 | +12V | REFP_W | — | REFN_TOP | LAD3_TOP | GND |
| P5 | P9 | S4_5th | S3_4th | LAD4_TOP | REFN_W | — | GND |

Nineteen signals across twenty-four pins; the five dashes are spares, carried in the
schematic as no-connects so they stay available. The socket body is what sets the
11.04 mm board spacing the capacitor heights are budgeted against, so substituting a
taller or shorter socket changes that budget.

### Footprint libraries

Everything resolves against stock KiCad libraries plus `eurorack.pretty` at the repo root,
wired up by `docs/fp-lib-table` as `${KIPRJMOD}/../eurorack.pretty`. **ERC reports 0 errors
and 0 warnings.**

Two footprints were added to `eurorack.pretty` for this build:

| Footprint | Notes |
|---|---|
| `SW_Taiway_200_SPDT` | 3 pads in a line on 2.54, **pad 2 is the common** |
| `SW_Taiway_200_DPDT` | 6 pads, 2.54 × 5.08, **pads 2 and 5 are the commons** |

**Both use Taiway's own pin numbering.** The library already contained
`SW_200_MDP3_DPDT`, which is the same physical part with the commons deliberately remapped
to pads 1 and 4 to suit a differently-numbered symbol. The two are *not* interchangeable —
pick the one matching your symbol and confirm the common lands on a centre terminal. Both
descriptions say so.

The Thonkiconn footprint names its pads `T` / `TN` / `S` rather than 1/2/3, so the jack
symbols use those as their pin numbers. KiCad allows any string there, and matching the
footprint is what keeps the pads connected.

Panel holes for the toggles are Ø5.0, against Taiway's recommended Ø4.95 for the 10‑48
bushing — fine. The optional 4.55 mm anti-rotation flat is not cut, so nut torque alone
holds them.

### Switch designators

`SW1`–`SW4` are the four polarity toggles, one per stage. `SW5` is the `OCT` magnitude
switch. `SW6`–`SW8` are the three quality selectors on stages 2–4.

Earlier drafts called these `SW1A`/`SW1B` and so on. That reads well but KiCad rejects it:
a trailing letter is how it writes the *unit* of a multi-unit symbol, so a reference ending
in one never counts as annotated. It does not appear in ERC — only in the annotation dialog
and as a warning on netlist export.

## Trimmer set points

Each chain totals **30k** when correctly trimmed. Nominal wiper settings, all comfortably
mid-travel on a 1k part:

| Trimmer | Stage | Fixed top | Trim to |
|---|---|---:|---:|
| VR1 | `OCT` | 5.49k | ~510 Ω |
| VR2, VR3 | `3RD` | 24.3k | ~700 Ω |
| VR4 | `5TH` | 22.6k | ~400 Ω |

The trim only has to absorb resistor tolerance — about ±60 Ω on a 30k chain at 0.1 % — so a
1k part is roughly eight times the range needed. VR5/VR6 set the ±2.5 V references and are
the first thing to adjust; everything else is a ratio of them.

## Changes from what is currently in the schematic

Apply with **Tools → Edit Symbol Fields** in Eeschema — it bulk-edits Value and Footprint by
group.

| Was | Now | Parts |
|---|---|---|
| 0805 | 1206 | every SMD R and C |
| 3k | 3.00k | R20, R30, R40, R42 |
| 12k | 12.0k | R11, R12 |
| 5.5k | 5.49k | R13 |
| 24.5k | 24.3k | R23, R33 |
| 22.5k | 22.6k | R43 |
| 50k | 49.9k | R1–R4 |

Only the first is a real change of part; the rest are non-stock values being pinned to
stocked ones. None of them alters a tap voltage — the trimmer takes up the difference.

**This table is history, and its first two rows now read backwards.** The Value fields were
later shortened for the silkscreen, so the schematic and board say `3k` and `12k` again. The
parts did not change back: they are still the E24 3.00 k and 12.0 k 0.1 % resistors chosen
above, and the reasoning for picking E24 over E96 stands. Only the label is shorter. Trailing
zeros are dropped wherever they carry no information — `10.0k` is written `10k`, while `49.9k`,
`24.3k`, `22.6k` and `5.49k` keep every digit. Tolerance lives in this document, not on the
silk, which has no room for it at 4 HP.

## Sourcing

[`BOM_v3_DigiKey.csv`](BOM_v3_DigiKey.csv) is an upload-ready DigiKey list covering 93 of the
parts. Create a list at [digikey.com/en/mylists](https://www.digikey.com/en/mylists) and choose
the spreadsheet upload option. Every line was checked as Active and in stock on 2026-08-14
except where noted below; stock moves, so verify before ordering.

**Reconciled against the board** on 2026-08-15. `v3-adder.kicad_pcb` places 109 footprints. The
CSV's 93 pieces plus the 13 parts listed under *Not on the DigiKey list* below account for 106 of
them; the remaining 3 are P2–P5, which the board draws as four separate 1×6 headers and the CSV
buys as a single 1×40 breakaway strip. Every value and quantity in the tables above matches the
board exactly.

### Resistors

**The E24 gamble paid off.** Panasonic's ERA-8 series carries 0.1 % thin film in 1206 across
both E24 values this design depends on — `ERA-8AEB302V` for the 3.00k and `ERA-8AEB123V` for
the 12.0k — with 18.5k and healthy stock respectively. The argument above for choosing E24
over E96 therefore costs nothing in availability, which was the one thing that could have
undermined it. All five 0.1 % values come from the same series, so they share a tolerance
grade, a tempco (±25 ppm/°C) and a supplier.

The 1 % parts are Yageo RC1206 except the 49.9k. Yageo's `RC1206FR-0749K9L` is out of stock
with a restock date of 2026-08-17, and Panasonic's `ERJ-8ENF4992V` — the obvious substitute —
is marked **Not For New Designs**, which is the wrong flag for a board that has not been built
yet. The list uses Vishay `CRCW120649K9FKEA` instead: active, in stock, same price.

The 1.00k appears twice, five at 0.1 % (ladder segments) and five at 1 % (output protection).
That split is deliberate and follows the tolerance reasoning above. If you would rather buy one
part than two, ordering all ten as `ERA-8AEB102V` is never wrong — it costs about $0.85 extra.

### C9 and C10 — resolved: electrolytic, laid flat

Earlier revisions of this section argued for an MnO2 tantalum in EIA-3528, which conflicts with
the footprint. `v3-adder.kicad_pcb` places all four 10 µF positions — C1, C3, C9 and C10 — on the
same `CP_Radial_D5.0mm_P2.00mm` through-hole footprint, so the board wants a can, not a chip.
**All four are ordinary aluminium electrolytics: Panasonic `ECA-1VM100`, 10 µF 35 V, 5 mm
diameter on 2 mm pitch.** No board edit, and one line on the order instead of two.

This satisfies the stability requirement on its own terms. The table above puts a 5 mm aluminium
electrolytic at 1–3 Ω of ESR, which is the range the phase-margin analysis calls for — the same
row that made the tantalum acceptable. Nothing about the damping argument changes.

**Height is handled by mounting, not by part selection.** A 5 mm 10 µF can is 5 × 11 mm, and
11 mm against an 11.04 mm board gap is no clearance at all. So **lay C9 and C10 over** — bend the
leads 90° at the board and let the cans lie against the control board's rear face. A 5 mm-diameter
can on its side stands 5.00 mm, which is exactly the figure the height table above already
budgets for C9/C10, so the design's own numbers assume this. Allow about 12 mm of clear board
length next to each one for the body to lie in, and orient them away from U4/U5.

C1 and C3 mount normally. They sit on the trimmer board's rear, facing the back of the case,
where nothing constrains height.

There is no shorter part to buy instead: DigiKey's stocked 5 mm-diameter 10 µF through-hole parts
start at 5 × 11 mm and run to 5 × 13 mm. Dropping the voltage rating does not shrink the can at
this capacitance either.

### OPA4196 packaging

`OPA4196IDR` (tape) is out of stock until 2026-09-08. The list uses `OPA4196ID` (tube) at
$5.36 against the reel part's $4.55. Three of them either way, so the packaging premium is
about $2.40 — cheaper than waiting, and the tube is easier to handle for hand assembly anyway.

### Not on the DigiKey list

| Qty | Part | Why | Where |
|---:|---|---|---|
| 8 | Thonkiconn PJ398SM | Not a DigiKey line | Thonk, Modular Addict |
| 3 | Taiway `200-MDP6-T1B1M2QE` DPDT ON-ON-ON | See below | Tayda, Love My Switches, Small Bear |
| 2 | Ferrite bead, axial leaded | See below | Mouser, or substitute |

**The ON-ON-ON DPDT has no DigiKey equivalent.** The three quality selectors are the one switch
function DigiKey cannot supply in this form factor: its only stocked ON-ON-ON DPDT is a full-size
part with a 15/32-32 bushing and a right-angle body, and it is not kept in stock either. The
sub-miniature 10-48 part has to come from a synth DIY shop. The other five switches are fine —
E-Switch `200MSP3T2B1M2QE` (ON-OFF-ON) and `200MSP1T1B1M2QEH` (ON-ON) are both stocked, in the
same 10-48 sub-miniature family, and drop onto the Taiway footprints.

Note the suffix: Taiway's part is `T1B1M2QE`, the stocked E-Switch ON-OFF-ON is `T2B1M2QE`.
The digit is the actuator variant, not the function or the bushing. Check the actuator length
suits your panel before committing to four of them.

**Axial ferrite beads are effectively not a DigiKey category.** They stock SMD beads and cable
cores, not the resistor-shaped leaded part the `R_Axial_DIN0207` footprint expects. Mouser
carries Würth's leaded range. Failing that, the footprint takes any 1/4 W axial body, so a wire
link or a small-value resistor will complete the board — you lose the HF filtering on the supply
rails and nothing else.

### Cost

The 0.1 % resistors and the three OPA4196 dominate: roughly $9 of precision resistors and $16 of
op amps, against about $4 for every 1 % resistor and ceramic on the board. The six trimmers add
another $14. That distribution is the design working as intended — the money is in the parts that
set pitch and in the amplifier driving them.
