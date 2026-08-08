#!/usr/bin/env python3
"""Generate the Precision Adder v3 schematic as a KiCad .kicad_sch.

    python3 tools/gen_schematic.py

writes docs/v3-adder.kicad_sch and prints a netlist report. Nothing is written
if the design check fails.

This is a *scaffold*, not a finished drawing. Connectivity is complete and is
the point; placement is a plain grid and every connection is made with a net
label on a short pin stub rather than by routing wires. That is deliberate -
label-based connectivity cannot be got subtly wrong the way routed wires can,
and rearranging symbols in KiCad afterwards does not break anything.

Topology follows docs/v2.2-topology.md, which is the built v2.2 design read off
its schematic. What changes for v3 is described there too.
"""

import math
import os
import sys
import uuid

SHEET_UUID = "8f1c0b1e-0000-4000-8000-000000000001"
PROJECT = "v3-adder"
PAPER = "A2"
LIB = "adder"      # library prefix; lib_symbols entries must carry it too

# --------------------------------------------------------------------------
# symbol definitions -- deliberately plain bodies; pins are what matter
# --------------------------------------------------------------------------
# Pins are (number, name, x, y, angle, etype) in symbol space, where Y is up
# and (x, y) is the electrical connection point. `angle` points from that
# connection point *into* the body.

# "art" is a list of (kind, *args) in symbol space:
#   ("rect", x0, y0, x1, y1) / ("poly", [(x, y), ...]) / ("circle", cx, cy, r)
# A pin's (x, y) is its connection point and `angle` points into the body, so a
# pin of length 2.54 at (-3.81, 0, 0) has its body end at (-1.27, 0).

def _dot(x, y):
    return ("circle", x, y, 0.508)


SYMS = {
    "R": dict(ref="R", hide_names=True,
              art=[("rect", -1.016, -2.54, 1.016, 2.54)],
              pins=[("1", "~", 0, 3.81, 270, "passive"),
                    ("2", "~", 0, -3.81, 90, "passive")]),
    "C": dict(ref="C", hide_names=True,
              art=[("poly", [(-2.54, 0.762), (2.54, 0.762)]),
                   ("poly", [(-2.54, -0.762), (2.54, -0.762)])],
              pins=[("1", "~", 0, 3.81, 270, "passive"),
                    ("2", "~", 0, -3.81, 90, "passive")]),
    "POT": dict(ref="VR",
                art=[("rect", -1.016, -2.54, 1.016, 2.54),
                     ("poly", [(1.27, 0), (2.54, 0.762), (2.54, -0.762),
                               (1.27, 0)])],
                pins=[("1", "~", 0, 3.81, 270, "passive"),
                      ("2", "W", 3.81, 0, 180, "passive"),
                      ("3", "~", 0, -3.81, 90, "passive")]),
    # cathode bar on the left, so pin 1 (K) is the barred end
    "D": dict(ref="D", hide_names=True,
              art=[("poly", [(1.27, 1.27), (1.27, -1.27), (-1.27, 0),
                             (1.27, 1.27)]),
                   ("poly", [(-1.27, 1.27), (-1.27, -1.27)])],
              pins=[("1", "K", -3.81, 0, 0, "passive"),
                    ("2", "A", 3.81, 0, 180, "passive")]),
    "FB": dict(ref="FB", hide_names=True,
               art=[("rect", -2.54, -1.27, 2.54, 1.27),
                    ("poly", [(-2.54, 0), (2.54, 0)])],
               pins=[("1", "~", -5.08, 0, 0, "passive"),
                     ("2", "~", 5.08, 0, 180, "passive")]),
    "REG": dict(ref="U",
                art=[("rect", -5.08, -5.08, 5.08, 5.08)],
                pins=[("1", "IN", -7.62, 2.54, 0, "power_in"),
                      ("2", "GND", 0, -7.62, 90, "power_in"),
                      ("3", "OUT", 7.62, 2.54, 180, "power_out")]),
    # a jack: sleeve bar down the left, tip contact springing off it
    "JACK": dict(ref="J",
                 art=[("poly", [(-2.54, 3.81), (-2.54, -3.81)]),
                      ("poly", [(-2.54, 2.54), (0, 2.54), (1.27, 3.302)]),
                      ("poly", [(-2.54, -2.54), (1.27, -2.54)]),
                      ("poly", [(1.27, -1.778), (2.54, -2.54),
                                (1.27, -3.302)])],
                 pins=[("1", "T", -5.08, 2.54, 0, "passive"),
                       ("2", "S", -5.08, -2.54, 0, "passive")]),
    # Thonkiconn with its normalling contact. The switch shorts tip to pin 3
    # when no plug is in, so wiring pin 3 to GND holds an unused input at a
    # hard 0 V - which the passive summing network requires. A pulldown will
    # not do: 100k in series with the 10k summing resistor re-weights the
    # average and the gain goes wrong as soon as an input is left unpatched.
    "JACK_SW": dict(ref="J",
                    art=[("poly", [(-2.54, 3.81), (-2.54, -3.81)]),
                         ("poly", [(-2.54, 2.54), (0, 2.54), (1.27, 3.302)]),
                         ("poly", [(-2.54, -2.54), (1.27, -2.54)]),
                         ("poly", [(1.27, -1.778), (2.54, -2.54),
                                   (1.27, -3.302)]),
                         ("poly", [(-2.54, 0), (0.5, 0.9)]),
                         _dot(-2.54, 0)],
                    pins=[("1", "T", -5.08, 2.54, 0, "passive"),
                          ("2", "S", -5.08, -2.54, 0, "passive"),
                          ("3", "N", -5.08, 0, 0, "passive")]),
    # lever drawn resting on throw A; the centre position is open
    "SW_ONON": dict(ref="SW",
                       art=[_dot(-2.54, 2.54), _dot(-2.54, -2.54),
                            _dot(2.54, 0),
                            ("poly", [(2.54, 0), (-2.032, 2.032)])],
                       pins=[("1", "A", -5.08, 2.54, 0, "passive"),
                             ("2", "COM", 5.08, 0, 180, "passive"),
                             ("3", "B", -5.08, -2.54, 0, "passive")]),
    # Taiway series 200 DPDT: pins 1-2-3 are pole A with 2 common, 4-5-6 are
    # pole B with 5 common. Cascading the poles is what turns a DPDT ON-ON-ON
    # into a 1-of-3 selector without ever shorting two ladder taps together.
    "SW_DPDT": dict(ref="SW",
                    art=[("rect", -2.54, -7.62, 2.54, 7.62),
                         _dot(-2.54, 6.35), _dot(-2.54, 3.81), _dot(-2.54, 1.27),
                         _dot(-2.54, -1.27), _dot(-2.54, -3.81), _dot(-2.54, -6.35),
                         ("poly", [(-2.032, 3.81), (1.27, 5.588)]),
                         ("poly", [(-2.032, -3.81), (1.27, -2.032)])],
                    pins=[("1", "1", -5.08, 6.35, 0, "passive"),
                          ("2", "2com", -5.08, 3.81, 0, "passive"),
                          ("3", "3", -5.08, 1.27, 0, "passive"),
                          ("4", "4", -5.08, -1.27, 0, "passive"),
                          ("5", "5com", -5.08, -3.81, 0, "passive"),
                          ("6", "6", -5.08, -6.35, 0, "passive")]),
    # a bare power-output pin, so KiCad sees +12V / -12V / GND as driven
    "PWR_FLAG": dict(ref="#FLG", hide_names=True,
                     art=[("poly", [(0, 0), (0, 1.27)]),
                          ("poly", [(0, 1.27), (-1.016, 2.032),
                                    (0, 2.794), (1.016, 2.032), (0, 1.27)])],
                     pins=[("1", "pwr", 0, 0, 90, "power_out")]),
    # laid out as the physical 2x5: odd pins down the left, even down the right
    "HDR2x5": dict(ref="P",
                   art=[("rect", -2.54, -6.35, 2.54, 6.35)],
                   pins=[(str(2 * r + 1), f"P{2*r+1}", -5.08, 5.08 - 2.54 * r,
                          0, "passive") for r in range(5)]
                        + [(str(2 * r + 2), f"P{2*r+2}", 5.08, 5.08 - 2.54 * r,
                            180, "passive") for r in range(5)]),
}

# 4-channel op-amp: units 1-4 are amplifiers, unit 5 carries the supply pins.
OPAMP_UNITS = {
    1: [("3", "+", -7.62, 2.54, 0), ("2", "-", -7.62, -2.54, 0),
        ("1", "~", 7.62, 0, 180)],
    2: [("5", "+", -7.62, 2.54, 0), ("6", "-", -7.62, -2.54, 0),
        ("7", "~", 7.62, 0, 180)],
    3: [("10", "+", -7.62, 2.54, 0), ("9", "-", -7.62, -2.54, 0),
        ("8", "~", 7.62, 0, 180)],
    4: [("12", "+", -7.62, 2.54, 0), ("13", "-", -7.62, -2.54, 0),
        ("14", "~", 7.62, 0, 180)],
    5: [("4", "V+", 0, 7.62, 270), ("11", "V-", 0, -7.62, 90)],
}

# --------------------------------------------------------------------------
# the circuit
# --------------------------------------------------------------------------

parts = []          # (ref, sym, value, unit, x, y, {pin: net}, footprint)
_seq = {}

# Placement is on a 25.4 mm lattice, one part per cell. That is wide enough for
# the largest symbol plus its label stubs, which is the point: hand-placed
# coordinates let two parts' stubs overlap, and overlapping stubs are a short.
# 25.4 is also 20 x 1.27, so every pin lands on KiCad's connection grid.
CELL = 25.4
ORIGIN = (38.1, 38.1)
ROWS = 13
_cur = dict(col=0, row=0)

# Stock KiCad footprints where they exist, so the links resolve on any install.
# The custom ones (Thonkiconn, trimmer, Eurorack header) are left as bare names
# on purpose - they are yours to supply, and a name that does not resolve is a
# more honest placeholder than a wrong one that does.
FOOTPRINTS = {"R": "Resistor_SMD:R_0805_2012Metric",
              "C": "Capacitor_SMD:C_0805_2012Metric"}


def new_block():
    """Start the next block in a fresh column."""
    if _cur["row"]:
        _cur["col"] += 1
        _cur["row"] = 0


def next_pos():
    x = ORIGIN[0] + _cur["col"] * CELL
    y = ORIGIN[1] + _cur["row"] * CELL
    _cur["row"] += 1
    if _cur["row"] >= ROWS:
        _cur["row"] = 0
        _cur["col"] += 1
    return x, y


def ref_for(prefix):
    _seq[prefix] = _seq.get(prefix, 0) + 1
    return f"{prefix}{_seq[prefix]}"


def add(sym, value, conns, ref=None, unit=1, fp=None):
    r = ref or ref_for(SYMS[sym]["ref"] if sym in SYMS else "U")
    x, y = next_pos()
    parts.append(dict(ref=r, sym=sym, value=value, unit=unit, x=x, y=y,
                      conns=conns, fp=fp if fp is not None
                      else FOOTPRINTS.get(sym, "")))
    return r


def res(value, a, b):
    return add("R", value, {"1": a, "2": b})


def cap(value, a, b):
    return add("C", value, {"1": a, "2": b})


def cap_tht(value, a, b):
    """Bulk electrolytics are through-hole, not 0805."""
    return add("C", value, {"1": a, "2": b},
               fp="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")


def opamp(ref, unit, plus, minus, out):
    x, y = next_pos()
    parts.append(dict(ref=ref, sym="OPA4196", value="OPA4196", unit=unit,
                      x=x, y=y, fp="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
                      conns=dict(zip([p[0] for p in OPAMP_UNITS[unit]],
                                     [plus, minus, out]))))


def pwr_flag(net):
    """KiCad wants every power net driven by a power-output pin somewhere."""
    add("PWR_FLAG", "PWR_FLAG", {"1": net}, ref=ref_for("#FLG"), fp="")


def build():
    # ---------------- power input ------------------------------------------
    new_block()
    add("HDR2x5", "Eurorack 2x5",
        {"1": "N12_RAW", "2": "N12_RAW", "3": "GND", "4": "GND", "5": "GND",
         "6": "GND", "7": "GND", "8": "GND", "9": "P12_RAW", "10": "P12_RAW"},
        ref="P1", fp="EURO_PWR_HEADER_LOCK")
    add("FB", "Ferrite", {"1": "P12_RAW", "2": "P12_F"}, fp="7MM_RESISTOR")
    add("D", "1N5819", {"1": "+12V", "2": "P12_F"}, fp="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
    add("FB", "Ferrite", {"1": "N12_RAW", "2": "N12_F"}, fp="7MM_RESISTOR")
    add("D", "1N5819", {"1": "N12_F", "2": "-12V"}, fp="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal")
    cap_tht("10uF", "+12V", "GND")
    cap("100pF", "+12V", "GND")
    cap_tht("10uF", "-12V", "GND")
    cap("100pF", "-12V", "GND")
    for net in ("+12V", "-12V", "GND"):
        pwr_flag(net)

    # ---------------- +/-5 V ------------------------------------------------
    new_block()
    # U1-U3 are the op-amp packages, so the regulators take U4/U5 explicitly.
    add("REG", "L78L05", {"1": "+12V", "2": "GND", "3": "+5V"},
        ref="U4", fp="Package_TO_SOT_THT:TO-92_Inline")
    cap("0.33uF", "+12V", "GND")
    cap("0.01uF", "+5V", "GND")
    add("REG", "L79L05", {"1": "-12V", "2": "GND", "3": "-5V"},
        ref="U5", fp="Package_TO_SOT_THT:TO-92_Inline")
    cap("0.33uF", "-12V", "GND")
    cap("0.1uF", "-5V", "GND")

    # ---------------- +/-2.5 V references -----------------------------------
    # Only precision source on the board; every stage scales down from these.
    new_block()
    res("50k", "+5V", "REFP_TOP")
    add("POT", "50k", {"1": "REFP_TOP", "2": "REFP_W", "3": "REFP_BOT"},
        ref="VR5", fp="PV36W-MULTITURN-TRIMMER")   # VR1-VR4 are the stage trims
    res("50k", "REFP_BOT", "GND")
    opamp("U3", 3, "REFP_W", "VREF_P", "VREF_P")
    cap_tht("10uF", "VREF_P", "GND")

    res("50k", "-5V", "REFN_TOP")
    add("POT", "50k", {"1": "REFN_TOP", "2": "REFN_W", "3": "REFN_BOT"},
        ref="VR6", fp="PV36W-MULTITURN-TRIMMER")
    res("50k", "REFN_BOT", "GND")
    opamp("U3", 4, "REFN_W", "VREF_N", "VREF_N")
    cap_tht("10uF", "VREF_N", "GND")

    # op-amp supply pins (unit 5 of each package) and the spare channel
    new_block()
    for u in ("U1", "U2", "U3"):
        opamp_supply(u)
        # local decoupling at each package, as v2.2 has on every quad
        cap("0.1uF", "+12V", "GND")
        cap("0.1uF", "-12V", "GND")
    opamp("U3", 2, "GND", "U3B_OUT", "U3B_OUT")     # spare, tied off

    # ---------------- input summer -----------------------------------------
    # Three inputs at unity: equal resistors average them onto the + input,
    # then a gain of 3 undoes the averaging. Same trick as v2.2's adder, which
    # averages two and takes a gain of 2.
    new_block()
    for n in (1, 2, 3):
        # pin 3 to GND: the jack's own switch grounds the tip when unpatched,
        # which is what keeps the summing ratios right with 1 or 2 inputs in use
        add("JACK_SW", "Thonkiconn", {"1": f"IN{n}", "2": "GND", "3": "GND"},
            ref=f"J{n}", fp="THONKICONN-TIGHT")
        res("10k", f"IN{n}", "SUMNODE")
    opamp("U1", 1, "SUMNODE", "SUMFB", "SUM_BUS")
    res("20k", "SUM_BUS", "SUMFB")
    res("10k", "SUMFB", "GND")
    res("1k", "SUM_BUS", "SUM_JACK")
    add("JACK", "Thonkiconn", {"1": "SUM_JACK", "2": "GND"},
        ref="J4", fp="THONKICONN-TIGHT")

    # ---------------- the four stages ---------------------------------------
    for st in STAGES:
        stage(st)


def opamp_supply(ref):
    x, y = next_pos()
    parts.append(dict(ref=ref, sym="OPA4196", value="OPA4196", unit=5,
                      x=x, y=y, fp="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
                      conns={"4": "+12V", "11": "-12V"}))


# Ladder segments run GND -> top. Taps are the junctions between them, so a
# tap's voltage is (sum of segments below it) / (whole chain) x 2.5 V. The
# op-amp input draws nothing, so selecting one tap does not disturb the others
# and a single trimmer in series scales all of them together.
VREF = 2.5

STAGES = [
    dict(n=1, name="OCT", amp=("U1", 2), out=("U1", 3), src="SUM_BUS",
         segs=[(12, "OCT_1V"), (12, "OCT_2V"), (6, None)],
         up="OCT_1V", detent=None, down="OCT_2V",
         want={"OCT_1V": 1.0, "OCT_2V": 2.0}),
    dict(n=2, name="3RD", amp=("U1", 4), out=("U2", 1), src="OUT1",
         segs=[(3, "S2_MIN3"), (1, "S2_MAJ3"), (1, "S2_4th"), (25, None)],
         up="S2_MAJ3", detent="S2_4th", down="S2_MIN3",
         want={"S2_MIN3": 0.25, "S2_MAJ3": 1 / 3, "S2_4th": 5 / 12}),
    dict(n=3, name="3RD", amp=("U2", 2), out=("U2", 3), src="OUT2",
         segs=[(3, "S3_MIN3"), (1, "S3_MAJ3"), (1, "S3_4th"), (25, None)],
         up="S3_MAJ3", detent="S3_4th", down="S3_MIN3",
         want={"S3_MIN3": 0.25, "S3_MAJ3": 1 / 3, "S3_4th": 5 / 12}),
    dict(n=4, name="5TH", amp=("U2", 4), out=("U3", 1), src="OUT3",
         segs=[(3, "S4_MIN3"), (1, "S4_MAJ3"), (3, "S4_5th"), (23, None)],
         up="S4_MAJ3", detent="S4_5th", down="S4_MIN3",
         want={"S4_MIN3": 0.25, "S4_MAJ3": 1 / 3, "S4_5th": 7 / 12}),
]


# Which pole of the ON-ON-ON moves at which detent. Taiway's series 200 sheet
# documents MDP-1..MDP-5 only; MDP-6 (ON-ON-ON) is a custom code and its
# contact sequence is not published, and the two possibilities are:
#
#   variant 1   up: 2-3, 5-6    centre: 2-3, 5-4    down: 2-1, 5-4
#   variant 2   up: 2-3, 5-6    centre: 2-1, 5-6    down: 2-1, 5-4
#
# i.e. pole A moves at the upper detent in one and the lower detent in the
# other. MEASURE BEFORE ORDERING A BOARD - continuity from pin 2 to pins 1/3
# through the three positions settles it in under a minute. The two wirings
# differ only in which of pins 1/3 carries a tap and which links to pole B.
ONONON_VARIANT = 1


def selector_3(n, up, mid, dn):
    """1-of-3 tap selection from a DPDT ON-ON-ON, by cascading the poles.

    Pole A's common is the output. One of its throws is a tap outright; the
    other feeds pole B's common, and pole B picks between the remaining two.
    Nothing ever shorts two taps together, which a tied-commons arrangement
    would do in every position.
    """
    link = f"SW{n}B_POLE"
    if ONONON_VARIANT == 1:
        conns = {"2": f"BIAS{n}_SEL", "3": link, "5": link,
                 "6": up, "4": mid, "1": dn}
    else:
        conns = {"2": f"BIAS{n}_SEL", "1": link, "5": link,
                 "3": up, "6": mid, "4": dn}
    add("SW_DPDT", "200-MDP6 (DPDT ON-ON-ON)", conns,
        ref=f"SW{n}B", fp="TAIWAY_200_DP_M2")


def stage(st):
    n = st["n"]
    new_block()

    # polarity: +2.5 V ref, open, -2.5 V ref. Open leaves the ladder pulled to
    # GND through its own bottom segment, so the stage contributes exactly 0.
    add("SW_ONON", "200-MSP3 (SPDT ON-OFF-ON)",
        {"1": "VREF_P", "3": "VREF_N", "2": f"LAD{n}_TOP"},
        ref=f"SW{n}A", fp="TAIWAY_200_SP_M2")
    # Trimmer as a rheostat in series at the top of the chain. The top fixed
    # resistor is 0.5k light, so the chain is nominal with the wiper centred
    # and trims about +/-1.7% either way.
    add("POT", "1k", {"1": f"LAD{n}_TOP", "2": f"LAD{n}_TRIM",
                      "3": f"LAD{n}_TRIM"},
        ref=f"VR{n}", fp="PV36W-MULTITURN-TRIMMER")

    # Ladder, built GND upward. Each entry is (value, tap at the TOP of that
    # segment); the last has no tap and runs to the trimmer.
    node = "GND"
    for i, (value, tap) in enumerate(st["segs"]):
        top = i == len(st["segs"]) - 1
        upper = f"LAD{n}_TRIM" if top else tap
        res(f"{value - 0.5:g}k" if top else f"{value:g}k", node, upper)
        node = upper

    # selector: 2-position on the octave stage, 3-position on the others
    if st["detent"] is None:
        add("SW_ONON", "200-MSP1 (SPDT ON-ON)",
            {"1": st["up"], "3": st["down"], "2": f"BIAS{n}_SEL"},
            ref=f"SW{n}B", fp="TAIWAY_200_SP_M2")
    else:
        selector_3(n, st["up"], st["detent"], st["down"])

    # Bias buffer and v2.2's output snubber. v2.2 also has a 22pF across its
    # follower's feedback, but that feedback is a plain wire, so the cap sits
    # across a short and does nothing - not reproduced here.
    amp_ref, amp_unit = st["amp"]
    opamp(amp_ref, amp_unit, f"BIAS{n}_SEL", f"BIAS{n}", f"BIAS{n}")
    res("619R", f"BIAS{n}", f"BIAS{n}_SNUB")
    cap("330pF", f"BIAS{n}_SNUB", "GND")

    # summing node: stage input and bias averaged, then a gain of 2
    res("10k", st["src"], f"SUM{n}")
    res("10k", f"BIAS{n}", f"SUM{n}")
    out_ref, out_unit = st["out"]
    opamp(out_ref, out_unit, f"SUM{n}", f"FB{n}", f"OUT{n}")
    res("10k", f"OUT{n}", f"FB{n}")
    res("10k", f"FB{n}", "GND")

    res("1k", f"OUT{n}", f"OUT{n}_JACK")
    add("JACK", "Thonkiconn", {"1": f"OUT{n}_JACK", "2": "GND"},
        ref=f"J{4 + n}", fp="THONKICONN-TIGHT")


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_ladders():
    """Each tap must land on its interval voltage with the trimmer centred.

    This is the check that matters: a ladder can be wired wrongly and still
    leave every net with two connections, so the netlist check alone passes a
    chain that produces the wrong voltages.
    """
    out, fails = [], []
    for st in STAGES:
        total = sum(v for v, _ in st["segs"])
        acc = 0
        for value, tap in st["segs"]:
            acc += value
            if tap is None:
                continue
            got = VREF * acc / total
            want = st["want"][tap]
            err = abs(got - want)
            semitones = err * 12
            flag = "" if err < 1e-9 else f"  <-- off by {semitones * 100:.2f} cents"
            out.append(f"  {tap:<9} {acc:>2}k/{total}k  {got:.6f} V  "
                       f"want {want:.6f}{flag}")
            if err > 1e-9:
                fails.append(f"{tap} is {got:.6f} V, wants {want:.6f} V")
    return out, fails


def check_function():
    """Assert the things that make the circuit do its job.

    These are the properties a netlist check cannot see, because a wrong value
    still connects. Each one here is a bug that was actually present at some
    point: an unpatched input that did not sum to zero, a missing decoupling
    cap, a gain that no longer matched the divider in front of it.
    """
    fails = []
    on_net = {}
    for p in parts:
        for pin, n in p["conns"].items():
            on_net.setdefault(n, []).append((p, pin))

    def parts_on(net, sym="R"):
        return [p for p, _ in on_net.get(net, []) if p["sym"] == sym]

    # A stage adds input and bias through two equal resistors and then takes a
    # gain of 2, so the divide-by-two is undone exactly.
    for st in STAGES:
        n = st["n"]
        summing = [p["value"] for p in parts_on(f"SUM{n}")]
        if sorted(summing) != ["10k", "10k"]:
            fails.append(f"stage {n} summing node has {summing}, wants two 10k")
        fb = [p["value"] for p in parts_on(f"FB{n}")]
        if len(fb) != 2 or fb[0] != fb[1]:
            fails.append(f"stage {n} gain network is {fb}, wants two equal")

    # Three inputs averaged then multiplied by three.
    ins = sorted(p["value"] for p in parts_on("SUMNODE"))
    if ins != ["10k"] * 3:
        fails.append(f"input summer has {ins}, wants three 10k")
    gain = [p["value"] for p in parts_on("SUMFB")]
    if sorted(gain) != ["10k", "20k"]:
        fails.append(f"input summer gain network is {gain}, wants 10k and 20k")

    # An unpatched input must be a hard 0 V, not a pulldown, or the passive
    # averager re-weights itself and the gain goes wrong.
    for p in parts:
        if p["sym"] == "JACK_SW" and p["conns"].get("3") != "GND":
            fails.append(f"{p['ref']} switch pin is not grounded; an unpatched "
                         f"input will not sum to zero")

    # Local decoupling on every op-amp package.
    packages = {p["ref"] for p in parts if p["sym"] == "OPA4196"}
    for rail in ("+12V", "-12V"):
        near = [p for p in parts_on(rail, "C") if p["value"] == "0.1uF"]
        if len(near) < len(packages):
            fails.append(f"{len(near)} x 0.1uF on {rail} for {len(packages)} "
                         f"op-amp packages; wants one each")
    return fails


# Taiway's contact table for the ON-ON-ON, position by position. Variant 1 is
# the published MDP-6 sequence; variant 2 is the other way the centre detent
# can resolve, kept so the wiring can be switched if a different part is used.
CONTACTS = {
    1: [[(2, 3), (5, 6)], [(2, 3), (5, 4)], [(2, 1), (5, 4)]],
    2: [[(2, 3), (5, 6)], [(2, 1), (5, 6)], [(2, 1), (5, 4)]],
}


def check_rotation_symmetry():
    """Fitting the switch 180 degrees round must change nothing.

    The body is symmetric, so rotating it swaps diagonally opposite pads
    (6<->1, 5<->2, 4<->3) and reverses the lever. Those two cancel: the
    sequence read against the board's own pad numbers, from lever-up to
    lever-down, comes out the same. So the pin numbers are wrong on a rotated
    part and the behaviour is not, and neither the footprint nor the panel
    needs to care which way it goes in.
    """
    rot = {1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
    table = CONTACTS[ONONON_VARIANT]
    rotated = [{frozenset(rot[a] for a in pair) for pair in pos}
               for pos in reversed(table)]
    fails = []
    for i, (orig, rt) in enumerate(zip(table, rotated), 1):
        if {frozenset(p) for p in orig} != rt:
            fails.append(f"ON-ON-ON position {i} is not rotation-symmetric; "
                         f"orientation would matter after all")
    return fails


def check_selector():
    """Simulate each selector through its three positions from the contact
    table, and confirm the output lands on the intended tap - exactly one tap,
    never two shorted together.

    This is what makes the cascaded-pole trick trustworthy: the wiring is not
    obviously right by inspection, and getting it wrong shorts two points of a
    resistor ladder rather than failing loudly.
    """
    fails = []
    for st in STAGES:
        if st["detent"] is None:
            continue
        n = st["n"]
        sw = next((p for p in parts if p["ref"] == f"SW{n}B"), None)
        if sw is None:
            fails.append(f"stage {n} has no selector")
            continue
        pin_net = {int(k): v for k, v in sw["conns"].items()}
        taps = {st["up"], st["detent"], st["down"]}
        want = [st["up"], st["detent"], st["down"]]

        for pos, closed in enumerate(CONTACTS[ONONON_VARIANT]):
            group = {2}                       # pole A common is the output
            for _ in range(len(closed)):      # propagate through the cascade
                for a, b in closed:
                    na, nb = pin_net.get(a), pin_net.get(b)
                    if a in group or b in group or (na and na == pin_net.get(
                            next(iter(group)))):
                        group |= {a, b} if (a in group or b in group) else set()
                # a pin links to another pin sharing its net (the pole link)
                for p1 in list(group):
                    for p2, nn in pin_net.items():
                        if nn == pin_net.get(p1) and p2 not in group:
                            group.add(p2)

            reached = {pin_net[p] for p in group if pin_net.get(p) in taps}
            if len(reached) != 1:
                fails.append(f"stage {n} position {pos + 1} reaches "
                             f"{sorted(reached) or 'no tap'}; wants exactly one")
            elif reached != {want[pos]}:
                fails.append(f"stage {n} position {pos + 1} selects "
                             f"{reached.pop()}, wants {want[pos]}")
    return fails


def check_panel_agreement():
    """The silkscreen and the wiring must say the same thing.

    The panel is the reference: whatever is printed next to a throw is what
    that throw has to select. These drifted apart once already - the schematic
    had the 4th on the up throw while the panel printed MAJ there, which would
    have shipped a module whose front lied about its own switches.
    """
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location(
        "gen_panel", os.path.join(here, "gen_panel.py"))
    panel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(panel)

    suffix = {"MAJ": "MAJ3", "MIN": "MIN3", "4": "4th", "5": "5th",
              "1": "1V", "2": "2V"}
    fails = []
    if len(panel.GROUPS) != len(STAGES):
        return [f"panel has {len(panel.GROUPS)} groups, schematic has "
                f"{len(STAGES)} stages"]

    for g, st in zip(panel.GROUPS, STAGES):
        if g["out"] != f"OUT{st['n']}":
            fails.append(f"panel group {g['name']} drives {g['out']}, "
                         f"schematic stage {st['n']} drives OUT{st['n']}")
        for throw in ("up", "detent", "down"):
            printed, wired = g[throw], st[throw]
            if printed is None or wired is None:
                if (printed is None) != (wired is None):
                    fails.append(f"stage {st['n']} {throw}: panel says "
                                 f"{printed!r}, schematic says {wired!r}")
                continue
            want = suffix.get(printed)
            if want is None:
                fails.append(f"panel label {printed!r} has no known tap")
            elif not wired.endswith(want):
                fails.append(f"stage {st['n']} {throw}: panel prints "
                             f"{printed!r}, schematic wires {wired!r}")
    return fails


def check_designators():
    """No two symbols may share a reference, and no unit may be placed twice.

    Auto-assigned references collided with hand-named ones here: the regulators
    took U1/U2 from the op-amp packages and the reference trimmers took VR1/VR2
    from the stage trimmers. Every net still had two or more connections, so
    the netlist check passed it - the giveaway was one pin appearing on two
    different nets.
    """
    fails, kinds, seen = [], {}, {}
    for p in parts:
        kinds.setdefault(p["ref"], set()).add(p["sym"])
        key = (p["ref"], p["unit"])
        if key in seen:
            fails.append(f"{p['ref']} unit {p['unit']} placed more than once")
        seen[key] = True
    for ref, syms in sorted(kinds.items()):
        if len(syms) > 1:
            fails.append(f"reference {ref} used by {' and '.join(sorted(syms))}")

    pin_net = {}
    for p in parts:
        for pin, net in p["conns"].items():
            key = (p["ref"], pin)
            if key in pin_net and pin_net[key] != net:
                fails.append(f"{p['ref']} pin {pin} is on both "
                             f"{pin_net[key]!r} and {net!r}")
            pin_net[key] = net
    return fails


def check():
    nets, fails, report = {}, [], []
    for p in parts:
        pins = ([q[0] for q in OPAMP_UNITS[p["unit"]]] if p["sym"] == "OPA4196"
                else [q[0] for q in SYMS[p["sym"]]["pins"]])
        for pin in pins:
            net = p["conns"].get(pin)
            if net is None:
                fails.append(f"{p['ref']} unit {p['unit']} pin {pin} unconnected")
                continue
            nets.setdefault(net, []).append(f"{p['ref']}.{pin}")

    singles = {n: v for n, v in nets.items() if len(v) < 2}
    for n, v in sorted(singles.items()):
        fails.append(f"net {n!r} has only one connection: {v[0]}")

    report.append(f"parts           {len({p['ref'] for p in parts})}")
    report.append(f"symbol units    {len(parts)}")
    report.append(f"nets            {len(nets)}")
    report.append(f"widest net      {max(nets, key=lambda n: len(nets[n]))} "
                  f"({max(len(v) for v in nets.values())} pins)")
    opamps = sorted({(p['ref'], p['unit']) for p in parts
                     if p['sym'] == 'OPA4196' and p['unit'] != 5})
    report.append(f"op-amp channels {len(opamps)} used of "
                  f"{4 * len({r for r, _ in opamps})}")
    return nets, report, fails


# --------------------------------------------------------------------------
# .kicad_sch output
# --------------------------------------------------------------------------

_NS = uuid.UUID("6f1a2c30-0000-4000-8000-000000000000")
_uid_n = [0]


def uid():
    """Deterministic ids, so regenerating an unchanged design is a no-op diff.

    Random uuid4s meant every run rewrote every line of the file and `git diff`
    could not show what actually changed.
    """
    _uid_n[0] += 1
    return str(uuid.uuid5(_NS, f"{PROJECT}:{_uid_n[0]}"))


def eff(hide=False, size=1.27):
    return f'(effects (font (size {size} {size}))' + (' hide' if hide else '') + ')'


STROKE = "(stroke (width 0.254) (type default)) (fill (type none))"


def art_sexpr(item):
    kind = item[0]
    if kind == "rect":
        _, x0, y0, x1, y1 = item
        return f'        (rectangle (start {x0} {y0}) (end {x1} {y1}) {STROKE})'
    if kind == "circle":
        _, cx, cy, r = item
        return f'        (circle (center {cx} {cy}) (radius {r}) {STROKE})'
    pts = " ".join(f"(xy {x} {y})" for x, y in item[1])
    return f'        (polyline (pts {pts}) {STROKE})'


def sym_body(name):
    """lib_symbols entry.

    The entry is named with the FULL lib_id, "adder:R" and not "R" - KiCad keys
    lib_symbols on the whole LIBRARY:NAME string, and a bare name leaves every
    instance unresolved and drawn as a box with "??" in it.
    """
    d = SYMS[name]
    # two-pin passives hide both, as the stock KiCad symbols do
    plain = d.get("hide_names")
    names = " hide" if plain else ""
    numbers = "(pin_numbers hide) " if plain else ""
    o = [f'    (symbol "{LIB}:{name}" {numbers}(pin_names (offset 0.254){names}) '
         '(in_bom yes) (on_board yes)']
    o.append(f'      (property "Reference" "{d["ref"]}" (at 0 5.08 0) {eff()})')
    o.append(f'      (property "Value" "{name}" (at 0 -5.08 0) {eff()})')
    o.append(f'      (property "Footprint" "" (at 0 0 0) {eff(True)})')
    o.append(f'      (property "Datasheet" "~" (at 0 0 0) {eff(True)})')
    o.append(f'      (symbol "{name}_0_1"')
    for item in d["art"]:
        o.append(art_sexpr(item))
    o.append('      )')
    o.append(f'      (symbol "{name}_1_1"')
    for num, pname, px, py, ang, et in d["pins"]:
        o.append(f'        (pin {et} line (at {px} {py} {ang}) (length 2.54) '
                 f'(name "{pname}" {eff()}) (number "{num}" {eff()}))')
    o.append('      )')
    o.append('    )')
    return "\n".join(o)


def opamp_body():
    o = [f'    (symbol "{LIB}:OPA4196" (pin_names (offset 0.254)) '
         '(in_bom yes) (on_board yes)',
         f'      (property "Reference" "U" (at 0 7.62 0) {eff()})',
         f'      (property "Value" "OPA4196" (at 0 -7.62 0) {eff()})',
         f'      (property "Footprint" "" (at 0 0 0) {eff(True)})',
         f'      (property "Datasheet" "~" (at 0 0 0) {eff(True)})']
    for unit, pins in OPAMP_UNITS.items():
        if unit != 5:
            o.append(f'      (symbol "OPA4196_{unit}_1"')
            o.append('        (polyline (pts (xy -5.08 5.08) (xy -5.08 -5.08) '
                     '(xy 5.08 0) (xy -5.08 5.08)) '
                     '(stroke (width 0.254) (type default)) (fill (type none)))')
            for num, pname, px, py, ang in pins:
                et = "output" if pname == "~" else "input"
                o.append(f'        (pin {et} line (at {px} {py} {ang}) (length 2.54) '
                         f'(name "{pname}" {eff()}) (number "{num}" {eff()}))')
            o.append('      )')
        else:
            o.append('      (symbol "OPA4196_5_1"')
            for num, pname, px, py, ang in pins:
                o.append(f'        (pin power_in line (at {px} {py} {ang}) (length 2.54) '
                         f'(name "{pname}" {eff()}) (number "{num}" {eff()}))')
            o.append('      )')
    o.append('    )')
    return "\n".join(o)


def pin_points(p):
    """Absolute schematic coords of each pin, and the direction away from body."""
    pins = (OPAMP_UNITS[p["unit"]] if p["sym"] == "OPA4196"
            else [(q[0], q[1], q[2], q[3], q[4]) for q in SYMS[p["sym"]]["pins"]])
    out = {}
    for num, _, px, py, ang in [(q[0], q[1], q[2], q[3], q[4]) for q in pins]:
        cx, cy = p["x"] + px, p["y"] - py          # symbol Y is up, sheet Y down
        a = math.radians(ang + 180)
        out[num] = (cx, cy, round(math.cos(a)), -round(math.sin(a)))
    return out


def write(path):
    o = [f'(kicad_sch (version 20230121) (generator "gen_schematic.py")',
         f'  (uuid "{SHEET_UUID}")',
         f'  (paper "{PAPER}")',
         '  (lib_symbols']
    for name in SYMS:
        o.append(sym_body(name))
    o.append(opamp_body())
    o.append('  )')

    for p in parts:
        lib = f'{LIB}:{p["sym"]}'
        o.append(f'  (symbol (lib_id "{lib}") (at {p["x"]} {p["y"]} 0) '
                 f'(unit {p["unit"]}) (in_bom yes) (on_board yes) (dnp no)')
        o.append(f'    (uuid "{uid()}")')
        o.append(f'    (property "Reference" "{p["ref"]}" '
                 f'(at {p["x"] + 6} {p["y"] - 6} 0) {eff()})')
        o.append(f'    (property "Value" "{p["value"]}" '
                 f'(at {p["x"] + 6} {p["y"] - 3} 0) {eff()})')
        o.append(f'    (property "Footprint" "{p["fp"]}" '
                 f'(at {p["x"]} {p["y"]} 0) {eff(True)})')
        o.append(f'    (property "Datasheet" "~" (at {p["x"]} {p["y"]} 0) {eff(True)})')
        pins = (OPAMP_UNITS[p["unit"]] if p["sym"] == "OPA4196"
                else SYMS[p["sym"]]["pins"])
        for q in pins:
            o.append(f'    (pin "{q[0]}" (uuid "{uid()}"))')
        o.append('    (instances')
        o.append(f'      (project "{PROJECT}"')
        o.append(f'        (path "/{SHEET_UUID}" (reference "{p["ref"]}") '
                 f'(unit {p["unit"]}))')
        o.append('      )')
        o.append('    )')
        o.append('  )')

    # a stub off every pin, with the net name on its far end
    for p in parts:
        for num, (cx, cy, dx, dy) in pin_points(p).items():
            net = p["conns"].get(num)
            if not net:
                continue
            ex, ey = cx + dx * 3.81, cy + dy * 3.81
            o.append(f'  (wire (pts (xy {cx} {cy}) (xy {ex} {ey})) '
                     f'(stroke (width 0) (type default)) (uuid "{uid()}"))')
            rot = 0 if dx >= 0 else 180
            if dx == 0:
                rot = 90 if dy < 0 else 270
            o.append(f'  (label "{net}" (at {ex} {ey} {rot}) '
                     f'{eff(size=1.0)} (uuid "{uid()}"))')

    o.append('  (sheet_instances (path "/" (page "1")))')
    o.append(')')
    with open(path, "w") as f:
        f.write("\n".join(o) + "\n")


def write_library(path):
    """The same symbols as a standalone .kicad_sym, so the schematic's library
    resolves instead of warning once per symbol."""
    o = ['(kicad_symbol_lib (version 20231120) (generator "gen_schematic.py")']
    for name in SYMS:
        o.append(sym_body(name))
    o.append(opamp_body())
    o.append(')')
    with open(path, "w") as f:
        f.write("\n".join(o) + "\n")


def write_project(docs):
    """Minimal project plus a sym-lib-table pointing at the local library."""
    with open(os.path.join(docs, "sym-lib-table"), "w") as f:
        f.write('(sym_lib_table\n  (version 7)\n'
                f'  (lib (name "{LIB}")(type "KiCad")'
                f'(uri "${{KIPRJMOD}}/{LIB}.kicad_sym")(options "")(descr ""))\n)\n')
    with open(os.path.join(docs, f"{PROJECT}.kicad_pro"), "w") as f:
        f.write('{\n  "board": {},\n  "libraries": {\n'
                '    "pinned_footprint_libs": [],\n'
                '    "pinned_symbol_libs": []\n  },\n'
                '  "meta": { "filename": "%s.kicad_pro", "version": 1 },\n'
                '  "schematic": {},\n'
                '  "sheets": [ [ "%s", "Root" ] ],\n'
                '  "text_variables": {}\n}\n' % (PROJECT, SHEET_UUID))


def main():
    build()
    nets, report, fails = check()
    taps, tap_fails = check_ladders()
    fails += tap_fails + check_designators() + check_function() + check_panel_agreement() + check_selector() + check_rotation_symmetry()

    print("design")
    for line in report:
        print("  " + line)
    print("\nladder taps, trimmer centred")
    for line in taps:
        print(line)
    if fails:
        print("\nFAILED - nothing written:")
        for f in fails[:20]:
            print("  " + f)
        return 1

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs = os.path.join(here, "docs")
    write(os.path.join(docs, f"{PROJECT}.kicad_sch"))
    write_library(os.path.join(docs, f"{LIB}.kicad_sym"))
    write_project(docs)
    print(f"\nwrote docs/{PROJECT}.kicad_sch, {LIB}.kicad_sym, "
          f"{PROJECT}.kicad_pro, sym-lib-table")

    if "--bom" in sys.argv:
        print("\n| Value | Designators | Qty | Footprint |")
        print("|---|---|---:|---|")
        groups = {}
        for p in parts:
            if p["unit"] != 1:                 # one row per package, not per unit
                continue
            groups.setdefault((p["value"], p["fp"]), []).append(p["ref"])
        for (value, fp), refs in sorted(groups.items(),
                                        key=lambda kv: (-len(kv[1]), kv[0][0])):
            order = sorted(refs, key=lambda r: (r.rstrip("0123456789"),
                                                int(r.lstrip("A-Za-z") or 0)
                                                if r.lstrip("A-Za-z").isdigit() else 0))
            print(f"| {value} | {', '.join(order)} | {len(refs)} | {fp} |")

    if "--netlist" in sys.argv:
        print("\nnetlist")
        for n in sorted(nets):
            print(f"  {n:<14} {' '.join(sorted(nets[n]))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
