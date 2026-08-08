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
    # lever drawn resting on throw A; the centre position is open
    "SW_ONOFFON": dict(ref="SW",
                       art=[_dot(-2.54, 2.54), _dot(-2.54, -2.54),
                            _dot(2.54, 0),
                            ("poly", [(2.54, 0), (-2.032, 2.032)])],
                       pins=[("1", "A", -5.08, 2.54, 0, "passive"),
                             ("2", "COM", 5.08, 0, 180, "passive"),
                             ("3", "B", -5.08, -2.54, 0, "passive")]),
    "SW_1P3T": dict(ref="SW",
                    art=[_dot(-2.54, 3.81), _dot(-2.54, 0), _dot(-2.54, -3.81),
                         _dot(2.54, 0),
                         ("poly", [(2.54, 0), (-2.032, 3.048)])],
                    pins=[("1", "A", -5.08, 3.81, 0, "passive"),
                          ("2", "B", -5.08, 0, 0, "passive"),
                          ("3", "C", -5.08, -3.81, 0, "passive"),
                          ("4", "COM", 5.08, 0, 180, "passive")]),
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
    opamp("U3", 2, "GND", "U3B_OUT", "U3B_OUT")     # spare, tied off

    # ---------------- input summer -----------------------------------------
    # Three inputs at unity: equal resistors average them onto the + input,
    # then a gain of 3 undoes the averaging. Same trick as v2.2's adder, which
    # averages two and takes a gain of 2.
    new_block()
    for n in (1, 2, 3):
        add("JACK", "Thonkiconn", {"1": f"IN{n}", "2": "GND"},
            ref=f"J{n}", fp="THONKICONN-TIGHT")
        res("100k", f"IN{n}", "GND")               # unpatched input = 0 V
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
         sel=["OCT_1V", "OCT_2V"],
         want={"OCT_1V": 1.0, "OCT_2V": 2.0}),
    dict(n=2, name="3RD", amp=("U1", 4), out=("U2", 1), src="OUT1",
         segs=[(3, "S2_MIN3"), (1, "S2_MAJ3"), (1, "S2_4th"), (25, None)],
         sel=["S2_MIN3", "S2_MAJ3", "S2_4th"],
         want={"S2_MIN3": 0.25, "S2_MAJ3": 1 / 3, "S2_4th": 5 / 12}),
    dict(n=3, name="3RD", amp=("U2", 2), out=("U2", 3), src="OUT2",
         segs=[(3, "S3_MIN3"), (1, "S3_MAJ3"), (1, "S3_4th"), (25, None)],
         sel=["S3_MIN3", "S3_MAJ3", "S3_4th"],
         want={"S3_MIN3": 0.25, "S3_MAJ3": 1 / 3, "S3_4th": 5 / 12}),
    dict(n=4, name="5TH", amp=("U2", 4), out=("U3", 1), src="OUT3",
         segs=[(3, "S4_MIN3"), (1, "S4_MAJ3"), (3, "S4_5th"), (23, None)],
         sel=["S4_MIN3", "S4_MAJ3", "S4_5th"],
         want={"S4_MIN3": 0.25, "S4_MAJ3": 1 / 3, "S4_5th": 7 / 12}),
]


def stage(st):
    n = st["n"]
    new_block()

    # polarity: +2.5 V ref, open, -2.5 V ref. Open leaves the ladder pulled to
    # GND through its own bottom segment, so the stage contributes exactly 0.
    add("SW_ONOFFON", "SUBMINI ON-OFF-ON",
        {"1": "VREF_P", "3": "VREF_N", "2": f"LAD{n}_TOP"},
        ref=f"SW{n}A", fp="SUBMINI_TOGGLE")
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
    taps = st["sel"]
    if len(taps) == 2:
        add("SW_ONOFFON", "SUBMINI ON-ON",
            {"1": taps[0], "3": taps[1], "2": f"BIAS{n}_SEL"},
            ref=f"SW{n}B", fp="SUBMINI_TOGGLE")
    else:
        add("SW_1P3T", "SUBMINI ON-ON-ON",
            {"1": taps[2], "2": taps[1], "3": taps[0], "4": f"BIAS{n}_SEL"},
            ref=f"SW{n}B", fp="SUBMINI_TOGGLE")

    # bias buffer, with v2.2's compensation cap and output snubber
    amp_ref, amp_unit = st["amp"]
    opamp(amp_ref, amp_unit, f"BIAS{n}_SEL", f"BIAS{n}", f"BIAS{n}")
    cap("22pF", f"BIAS{n}", f"BIAS{n}_SEL")
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

def uid():
    return str(uuid.uuid4())


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
    fails += tap_fails + check_designators()

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
