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
| 2 | 10uF | electrolytic, **≤7 mm tall** | C9, C10 | `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm` |
| 2 | 10uF | electrolytic, any height | C1, C3 | `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm` |
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

A 5 mm-diameter 10 µF is commonly sold as a **5 × 11 mm** can, which lands
exactly on 11.04 mm with no clearance at all — it will foul the trimmer board.
The 5 mm part the 3D model shows leaves 6 mm. Anything up to 7 mm is safe;
past that the margin is not worth having.

Worth noting that C9 and C10 are the same two flagged above as wanting tantalum
for their ESR, since they hang off the reference buffer outputs. An SMD tantalum
in EIA-3528 is about 2.1 mm tall and settles both problems at once.

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

Keep the **shrouded, keyed** power header — it is the only thing that stops the ribbon
going on backwards, and D1/D2 are the last line of defence after it.

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
