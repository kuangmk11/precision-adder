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
| 4 | 10uF | electrolytic | C1, C3, C9, C10 | `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm` |
| 2 | 0.33uF | X7R | C5, C7 | `Capacitor_SMD:C_1206_3216Metric` |
| 2 | 100pF | C0G | C2, C4 | `Capacitor_SMD:C_1206_3216Metric` |
| 1 | 0.01uF | X7R | C6 | `Capacitor_SMD:C_1206_3216Metric` |

C0G on the snubbers and the HF supply caps; X7R elsewhere is fine.

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
| 8 | Thonkiconn PJ398SM | J1–J8 | `THONKICONN-TIGHT` *(custom)* |
| 4 | Taiway `200-MSP3-T1B1M2QE` SPDT ON-OFF-ON | SW1A–SW4A | `TAIWAY_200_SP_M2` *(custom)* |
| 3 | Taiway `200-MDP6-T1B1M2QE` DPDT ON-ON-ON | SW2B, SW3B, SW4B | `TAIWAY_200_DP_M2` *(custom)* |
| 1 | Taiway `200-MSP1-T1B1M2QE` SPDT ON-ON | SW1B | `TAIWAY_200_SP_M2` *(custom)* |
| 4 | 1k multiturn trimmer | VR1–VR4 | `Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical` |
| 2 | 50k multiturn trimmer | VR5, VR6 | `Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical` |
| 2 | Ferrite bead, axial | FB1, FB2 | `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal` |
| 1 | Eurorack 2×5 shrouded header | P1 | `EURO_PWR_HEADER_LOCK` *(custom)* |

Keep the **shrouded, keyed** power header — it is the only thing that stops the ribbon
going on backwards, and D1/D2 are the last line of defence after it.

### Custom footprints still to draw

| Footprint | Geometry |
|---|---|
| `TAIWAY_200_SP_M2` | 3 pins in a row, **2.54 mm** pitch |
| `TAIWAY_200_DP_M2` | 6 pins, 2 columns × 3 rows, **5.08 × 2.54 mm**; numbered 6‑5‑4 down one column, 3‑2‑1 down the other |
| `THONKICONN-TIGHT` | carries over from v2.2 |
| `EURO_PWR_HEADER_LOCK` | carries over from v2.2 |

Panel holes for the toggles are Ø5.0, against Taiway's recommended Ø4.95 for the 10‑48
bushing — fine. The optional 4.55 mm anti-rotation flat is not cut, so nut torque alone
holds them.

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
