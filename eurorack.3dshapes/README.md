# eurorack.3dshapes

3D models for the footprints in `../eurorack.pretty`. Found the same way the
footprints are — `fp-lib-table` points at `${KIPRJMOD}/../eurorack.pretty`, so
the models sit beside it and resolve as `${KIPRJMOD}/../eurorack.3dshapes/…`
from any project one directory down. They were previously written as
`${KIPRJMOD}/3d/…`, which resolved to `docs/3d` and tied a shared library to a
single project.

Everything else on the adder resolves from KiCad's own `${KICAD10_3DMODEL_DIR}`
and needs nothing here.

## Files this library expects

These are vendor STEP files. They are not in the repo and cannot be generated —
drop them in this directory under exactly these names.

| File | Used by | Source |
|---|---|---|
| `PJ301M-12 Thonkiconn v0.2.stp` | `Thonkiconn_PJ301M` (J1–J8) | Thonk's PJ301M-12 product page, or the community "Thonkiconn" STEP |
| `200MDPxT2B1M2xE.stp` | `SW_Taiway_200_DPDT`, `SW_200_MDP3_DPDT` (SW6–SW8) | Taiway, series 200 DPDT |
| `200MSPxT2B1M2xE.stp` | `SW_Taiway_200_SPDT` (SW1–SW5) | Taiway, series 200 SPDT |

**The SPDT filename is a guess.** `SW_Taiway_200_SPDT` had no model reference at
all; the name above follows Taiway's own scheme by analogy with the DPDT file.
If the vendor ships it under a different name, rename the file or edit the
`(model …)` line in `../eurorack.pretty/SW_Taiway_200_SPDT.kicad_mod` and the
cached copies in `../docs/v3-adder.kicad_pcb` — the board carries its own copy of
every model path, so both have to change together.

## Orientation

All three are declared with zero offset and zero rotation, which assumes the
model's origin sits at the PCB surface with the body extending up in +Z. That
has not been checked against the actual files, because the actual files are not
here. Once they are, open the board in the 3D viewer and confirm the jacks and
switches stand off the front face rather than sinking through it. The panel-side
parts are all on F.Cu, so anything pointing the wrong way will be obvious.
