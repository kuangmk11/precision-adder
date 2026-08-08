#!/usr/bin/env python3
"""Generate the Precision Adder v3 front panel: KiCad board + 1:1 SVG preview.

Both outputs come from the one LAYOUT table below, so a change is a number edit
and the two can never disagree. Run with no arguments:

    python3 tools/gen_panel.py

writes docs/v3-panel.kicad_pcb and docs/v3-panel.svg, then prints a clearance
report. Nothing is written if the clearance check fails.

Conventions follow PANEL_STYLE (see the repo root):

  * a name goes below the thing it names, always;
  * a mark that means a position goes where that position is - "+" and "-"
    straddle a toggle, selector values sit at the throws they select;
  * text is emitted one item per character on a fixed pitch, uppercase;
  * mounting is regenerated to the <= 6 HP rule - one slot top-right, one
    bottom-left, so the module cannot pivot on a single screw per rail.

Coordinates are millimetres, Y down, origin at the panel's top-left corner.
KiCad output is shifted by ORIGIN so the board lands on the drawing sheet.
"""

import math
import os
import sys
import uuid

# --------------------------------------------------------------------------
# style tokens
# --------------------------------------------------------------------------

LINE_W = 0.25          # boxes, wordmark frame
RULE_W = 0.20          # section divider
EDGE_MARGIN = 0.6      # no silkscreen closer than this to the cut

TITLE_SIZE, PITCH_TITLE = 3.2, 3.4
LABEL_SIZE, PITCH_LABEL = 1.6, 1.7
LOGO_SIZE,  PITCH_LOGO = 1.3, 1.45
DETENT_SIZE, PITCH_DETENT = 1.0, 1.1   # the one mark that will not fit at 1.6

# --------------------------------------------------------------------------
# panel geometry
# --------------------------------------------------------------------------

PANEL_W, PANEL_H = 20.0, 128.5         # 4 HP
COL_L, COL_R = 4.6, 15.4               # control columns, 10.8 mm pitch

JACK_D, JACK_NUT = 6.0, 8.0            # Thonkiconn
TOGGLE_D, TOGGLE_NUT = 5.0, 7.5        # subminiature toggle

# labels sit this far below whatever is drawn around the hole
NAME_GAP = 2.15                        # baseline below the nut edge
MARK_UP = 4.25                         # "+" / upper value baseline above a toggle
MARK_DOWN = 5.85                       # "-" / lower value baseline below a toggle

MOUNT_L, MOUNT_H = 6.4, 3.2            # obround slot, horizontal
MOUNTS = [(PANEL_W - 7.5, 3.0), (7.5, PANEL_H - 3.0)]   # top-right, bottom-left

TITLE_Y = 8.5
SUBTITLE_Y = 11.6
ROW_IN = [16.6, 28.6]                  # IN1/IN2, IN3/SUM

# SUM is an output, so it takes the ring. The ring has to clear the 8 mm nut to
# be visible at all, which at this column leaves it 0.6 mm from the cut on the
# outboard side - so it is drawn as an arc with a gap there rather than a full
# circle. A 20 mm panel carrying two 8 mm nuts has 4 mm of slack in total; a
# ring bigger than a nut does not fit in it.
RING_R = 4.4

BOX_X = {"L": (0.6, 9.6), "R": (10.4, 19.4)}
BOX_R = 1.0
BOX_TOP = [36.8, 80.0]                 # top edge of each group row

SW1_DY = 8.0                           # polarity toggle below the box top edge
SW2_DY = 21.0                          # selector toggle below the box top edge
OUT_DY = 32.0                          # output jack below the box top edge
BOX_H = 39.15                          # box top edge to bottom edge

LOGO_Y = 121.5                         # wordmark centre, = height - 7.0

# --------------------------------------------------------------------------
# what is on the panel
# --------------------------------------------------------------------------

INPUTS = [("IN1", "L", 0, False), ("IN2", "R", 0, False),
          ("IN3", "L", 1, False), ("SUM", "R", 1, True)]   # last field: ringed

# Each group is one stage: polarity toggle, selector toggle, output jack.
# Reading order is across then down, so the cascade zig-zags and OUT1-OUT4
# read like a book.
#
# "detent" is the selector's centre position. It carries the stage's odd
# interval - the fourth or the fifth - because the centre mark is the only one
# with nowhere to go but the channel between the columns, where a single
# character fits and two do not. The two throws are then the two thirds, which
# is also the pair you reach for most.
GROUPS = [
    dict(name="OCT", col="L", row=0, out="OUT1", up="2",   detent=None, down="1"),
    dict(name="3RD", col="R", row=0, out="OUT2", up="MAJ", detent="4",  down="MIN"),
    dict(name="3RD", col="L", row=1, out="OUT3", up="MAJ", detent="4",  down="MIN"),
    dict(name="5TH", col="R", row=1, out="OUT4", up="MAJ", detent="5",  down="MIN"),
]

# --------------------------------------------------------------------------
# collected drawing primitives
# --------------------------------------------------------------------------

silk_lines = []    # (x0, y0, x1, y1, width)
silk_arcs = []     # (cx, cy, r, start_angle, end_angle, width) degrees, Y down
cuts_circles = []  # (cx, cy, r)
cuts_lines = []    # (x0, y0, x1, y1)
cuts_arcs = []     # (cx, cy, r, start_angle, end_angle)
chars = []         # (glyph, cell_cx, baseline_y, size)
boxes = []         # bookkeeping only: (label, x0, ytop, x1, ybaseline) for the check


def text(s, cx, baseline, size, pitch):
    """Emit one item per character, each centred in its own cell."""
    span = len(s) * pitch
    x0 = cx - span / 2
    for i, ch in enumerate(s):
        if ch != " ":
            chars.append((ch, x0 + pitch * (i + 0.5), baseline, size))
    boxes.append((s, x0, baseline - size, x0 + span, baseline))
    return x0, x0 + span


def rounded_box(x0, y0, x1, y1, r, gaps=()):
    """Rounded rectangle. `gaps` are (side, lo, hi) cut out of a straight run."""
    def run(side, a, b, horizontal, fixed):
        cuts = sorted((lo, hi) for s, lo, hi in gaps if s == side)
        pos = a
        for lo, hi in cuts:
            if lo > pos:
                emit(pos, min(lo, b), horizontal, fixed)
            pos = max(pos, hi)
        if pos < b:
            emit(pos, b, horizontal, fixed)

    def emit(a, b, horizontal, fixed):
        if horizontal:
            silk_lines.append((a, fixed, b, fixed, LINE_W))
        else:
            silk_lines.append((fixed, a, fixed, b, LINE_W))

    run("top", x0 + r, x1 - r, True, y0)
    run("bottom", x0 + r, x1 - r, True, y1)
    run("left", y0 + r, y1 - r, False, x0)
    run("right", y0 + r, y1 - r, False, x1)

    silk_arcs.append((x0 + r, y0 + r, r, 180, 270, LINE_W))
    silk_arcs.append((x1 - r, y0 + r, r, 270, 360, LINE_W))
    silk_arcs.append((x1 - r, y1 - r, r, 0, 90, LINE_W))
    silk_arcs.append((x0 + r, y1 - r, r, 90, 180, LINE_W))


def arrow(pts, head=0.9):
    """Polyline with a chevron head at the last point. 0/90/45 segments only."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        silk_lines.append((x0, y0, x1, y1, LINE_W))
    (px, py), (tx, ty) = pts[-2], pts[-1]
    a = math.atan2(ty - py, tx - px)
    for barb in (math.radians(150), math.radians(-150)):
        silk_lines.append((tx, ty,
                           tx + head * math.cos(a + barb),
                           ty + head * math.sin(a + barb), LINE_W))


def obround(cx, cy, length, height):
    """Stadium slot on Edge.Cuts: two semicircles joined by two straights."""
    r = height / 2
    dx = length / 2 - r
    cuts_lines.append((cx - dx, cy - r, cx + dx, cy - r))
    cuts_lines.append((cx - dx, cy + r, cx + dx, cy + r))
    # Both caps bulge outward. The right one has to be swept as -90 -> +90 so
    # its midpoint lands at 0 degrees (the outboard point); 270 -> 90 puts the
    # midpoint at 180 and turns the cap inside out.
    cuts_arcs.append((cx + dx, cy, r, -90, 90))
    cuts_arcs.append((cx - dx, cy, r, 90, 270))


# --------------------------------------------------------------------------
# build the panel
# --------------------------------------------------------------------------

def build():
    # board outline
    cuts_lines.extend([
        (0, 0, PANEL_W, 0),
        (PANEL_W, 0, PANEL_W, PANEL_H),
        (PANEL_W, PANEL_H, 0, PANEL_H),
        (0, PANEL_H, 0, 0),
    ])
    for cx, cy in MOUNTS:
        obround(cx, cy, MOUNT_L, MOUNT_H)

    # title block
    text("ADDER", PANEL_W / 2, TITLE_Y, TITLE_SIZE, PITCH_TITLE)
    text("V3", PANEL_W / 2, SUBTITLE_Y, LABEL_SIZE, PITCH_LABEL)

    # inputs and SUM. A name is measured from whatever is drawn around the hole,
    # so a ringed jack pushes its whole row's baseline down - both labels move,
    # not just the ringed one.
    for row, y in enumerate(ROW_IN):
        ringed = [i for i in INPUTS if i[2] == row and i[3]]
        stand = RING_R if ringed else JACK_NUT / 2
        for name, col, r, ring in [i for i in INPUTS if i[2] == row]:
            x = COL_L if col == "L" else COL_R
            cuts_circles.append((x, y, JACK_D / 2))
            if ring:
                # gap the arc where a full circle would breach EDGE_MARGIN
                reach = PANEL_W - EDGE_MARGIN - x
                half = math.degrees(math.acos(min(1.0, reach / RING_R))) + 1.5
                silk_arcs.append((x, y, RING_R, half, 360 - half, LINE_W))
            text(name, x, y + stand + NAME_GAP, LABEL_SIZE, PITCH_LABEL)

    # stage groups
    for g in GROUPS:
        x = COL_L if g["col"] == "L" else COL_R
        x0, x1 = BOX_X[g["col"]]
        top = BOX_TOP[g["row"]]
        t1, t2, jy = top + SW1_DY, top + SW2_DY, top + OUT_DY

        cuts_circles.append((x, t1, TOGGLE_D / 2))
        cuts_circles.append((x, t2, TOGGLE_D / 2))
        cuts_circles.append((x, jy, JACK_D / 2))

        # polarity: + above, - below. Centre detent is off and unmarked.
        text("+", x, t1 - MARK_UP, LABEL_SIZE, PITCH_LABEL)
        text("−", x, t1 + MARK_DOWN, LABEL_SIZE, PITCH_LABEL)

        # selector: value at each throw
        text(g["up"], x, t2 - MARK_UP, LABEL_SIZE, PITCH_LABEL)
        text(g["down"], x, t2 + MARK_DOWN, LABEL_SIZE, PITCH_LABEL)

        text(g["out"], x, jy + JACK_NUT / 2 + NAME_GAP, LABEL_SIZE, PITCH_LABEL)

        # group name in a gap in the box's top edge
        half = len(g["name"]) * PITCH_LABEL / 2
        gaps = [("top", x - half - 0.3, x + half + 0.3)]

        # the cascade arrows cross these edges; break them rather than draw over
        ay = out_arrow_y(g["row"])
        gaps.append(("right" if g["col"] == "L" else "left", ay - 0.7, ay + 0.7))
        if g["row"] == 0 and g["col"] == "R":
            gaps.append(("bottom", x - 0.7, x + 0.7))

        # The centre detent's value goes between the toggle nut and the box's
        # inboard edge - the only clear width left at that height, and about
        # 1.2 mm of it. It stays *inside* the box: straddling the edge put the
        # two columns' marks 1.6 mm apart across the centre line, where "4" and
        # "5" read as the number 45 and neither belongs to a group.
        if g["detent"]:
            if g["col"] == "L":
                lo, hi = x + TOGGLE_NUT / 2, x1 - LINE_W / 2
            else:
                lo, hi = x0 + LINE_W / 2, x - TOGGLE_NUT / 2
            text(g["detent"], (lo + hi) / 2, t2 + DETENT_SIZE / 2,
                 DETENT_SIZE, PITCH_DETENT)

        rounded_box(x0, top, x1, top + BOX_H, BOX_R, gaps)
        text(g["name"], x, top + LABEL_SIZE / 2, LABEL_SIZE, PITCH_LABEL)

    cascade_arrows()
    wordmark()


def out_label_y(row):
    return BOX_TOP[row] + OUT_DY + JACK_NUT / 2 + NAME_GAP


def out_arrow_y(row):
    """Arrows run at the OUT labels' mid-cap height, so they read as one line."""
    return out_label_y(row) - LABEL_SIZE / 2


def cascade_arrows():
    """The signal path through the four stages: across, down, across.

    OUT1 -> OUT2 -> down into the 3RD group -> across to 5TH. The middle leg
    cannot be a straight diagonal: 4 mm of clear band between the two box rows
    against 10.8 mm of column pitch would need a 15-degree line, and the house
    routing is 0, 90 and 45 only. So it drops, takes a 45-degree knee, runs the
    band, and turns down into the group it feeds.
    """
    inset = len("OUT1") * PITCH_LABEL / 2 + 0.4      # clear of the OUT labels

    for row in (0, 1):
        y = out_arrow_y(row)
        arrow([(COL_L + inset, y), (COL_R - inset, y)])

    tip = BOX_TOP[1] - LABEL_SIZE / 2 - 0.5           # just above the 3RD name
    band = tip - 1.5                                  # 0.8 of knee, 0.7 of run-in
    assert band > BOX_TOP[0] + BOX_H + 0.5, "no clear band between the box rows"
    arrow([(COL_R, out_label_y(0) + 0.5),
           (COL_R, band - 0.8),
           (COL_R - 0.8, band),
           (COL_L + 0.8, band),
           (COL_L, band + 0.8),
           (COL_L, tip)])


def wordmark():
    """508 letterspaced inside a plain two-lead component frame."""
    span = 3 * PITCH_LOGO
    w, h = span + 1.6, 2.4
    x0, x1 = PANEL_W / 2 - w / 2, PANEL_W / 2 + w / 2
    y0, y1 = LOGO_Y - h / 2, LOGO_Y + h / 2
    silk_lines.extend([
        (x0, y0, x1, y0, LINE_W), (x1, y0, x1, y1, LINE_W),
        (x1, y1, x0, y1, LINE_W), (x0, y1, x0, y0, LINE_W),
        (x0 - 1.8, LOGO_Y, x0, LOGO_Y, LINE_W),
        (x1, LOGO_Y, x1 + 1.8, LOGO_Y, LINE_W),
    ])
    text("508", PANEL_W / 2, LOGO_Y + LOGO_SIZE / 2, LOGO_SIZE, PITCH_LOGO)


# --------------------------------------------------------------------------
# clearance check
# --------------------------------------------------------------------------

def char_box(ch, cx, baseline, size):
    """Conservative ink box: a stroke glyph fills about 0.62 em of its cell."""
    half = size * 0.62 / 2
    return (cx - half, baseline - size, cx + half, baseline)


def check():
    """Report the tightest clearances. Returns a list of failures."""
    fails, report = [], []
    items = [(ch, char_box(ch, cx, y, s)) for ch, cx, y, s in chars]

    # text against the hardware that sits on each hole
    worst_nut = (99, None)
    for label, (bx0, by0, bx1, by1) in items:
        for cx, cy, r in cuts_circles:
            nut = (JACK_NUT if r > 2.6 else TOGGLE_NUT) / 2
            nx = min(max(cx, bx0), bx1)
            ny = min(max(cy, by0), by1)
            d = math.hypot(cx - nx, cy - ny) - nut
            if d < worst_nut[0]:
                worst_nut = (d, f"{label!r} vs nut at ({cx}, {cy})")
            if d < 0:
                fails.append(f"text {label!r} under the nut at ({cx}, {cy}): {d:.2f} mm")
    report.append(f"text to nut          {worst_nut[0]:6.2f} mm   {worst_nut[1]}")

    # text against text
    worst_tt = (99, None)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i][1], items[j][1]
            dx = max(a[0] - b[2], b[0] - a[2])
            dy = max(a[1] - b[3], b[1] - a[3])
            d = max(dx, dy) if (dx >= 0 or dy >= 0) else -min(-dx, -dy)
            if d < worst_tt[0]:
                worst_tt = (d, f"{items[i][0]!r} vs {items[j][0]!r}")
            if d < 0:
                fails.append(f"text {items[i][0]!r} overlaps {items[j][0]!r}: {d:.2f} mm")
    report.append(f"text to text         {worst_tt[0]:6.2f} mm   {worst_tt[1]}")

    # text against the silkscreen it sits among. A label placed in a gap in a
    # box edge has to actually clear that edge - the gap being too short is the
    # easiest way to get this drawing wrong.
    worst_ts = (99, None)
    for label, (bx0, by0, bx1, by1) in items:
        for x0, y0, x1, y1, w in silk_lines:
            lx0, lx1 = min(x0, x1) - w / 2, max(x0, x1) + w / 2
            ly0, ly1 = min(y0, y1) - w / 2, max(y0, y1) + w / 2
            dx = max(bx0 - lx1, lx0 - bx1)
            dy = max(by0 - ly1, ly0 - by1)
            d = max(dx, dy) if (dx >= 0 or dy >= 0) else -min(-dx, -dy)
            if d < worst_ts[0]:
                worst_ts = (d, f"{label!r} vs line ({x0}, {y0})-({x1}, {y1})")
            if d < 0:
                fails.append(f"text {label!r} crosses a silk line "
                             f"({x0}, {y0})-({x1}, {y1}): {d:.2f} mm")
    report.append(f"text to silk line    {worst_ts[0]:6.2f} mm   {worst_ts[1]}")

    # silkscreen to the board edge
    worst_edge = (99, None)
    for label, (bx0, by0, bx1, by1) in items:
        m = min(bx0, PANEL_W - bx1, by0, PANEL_H - by1)
        if m < worst_edge[0]:
            worst_edge = (m, repr(label))
    for x0, y0, x1, y1, _ in silk_lines:
        m = min(x0, x1, PANEL_W - x0, PANEL_W - x1, y0, y1, PANEL_H - y0, PANEL_H - y1)
        if m < worst_edge[0]:
            worst_edge = (m, "silk line")
    report.append(f"silk to board edge   {worst_edge[0]:6.2f} mm   {worst_edge[1]}")
    if worst_edge[0] < EDGE_MARGIN - 1e-9:
        fails.append(f"silkscreen {worst_edge[1]} is {worst_edge[0]:.2f} mm from the cut "
                     f"(EDGE_MARGIN {EDGE_MARGIN})")

    # holes to the board edge, and hole to hole
    worst_hole = (99, None)
    for cx, cy, r in cuts_circles:
        m = min(cx - r, PANEL_W - cx - r, cy - r, PANEL_H - cy - r)
        if m < worst_hole[0]:
            worst_hole = (m, f"hole at ({cx}, {cy})")
    for mx, my in MOUNTS:
        m = min(mx - MOUNT_L / 2, PANEL_W - mx - MOUNT_L / 2,
                my - MOUNT_H / 2, PANEL_H - my - MOUNT_H / 2)
        if m < worst_hole[0]:
            worst_hole = (m, f"mounting slot at ({mx}, {my})")
    report.append(f"hole to board edge   {worst_hole[0]:6.2f} mm   {worst_hole[1]}")
    if worst_hole[0] < 1.0:
        fails.append(f"{worst_hole[1]} leaves only {worst_hole[0]:.2f} mm of material")

    # nut to nut, the thing a print has to confirm
    worst_nn = (99, None)
    pts = [(cx, cy, (JACK_NUT if r > 2.6 else TOGGLE_NUT) / 2) for cx, cy, r in cuts_circles]
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            ax, ay, ar = pts[i]
            bx, by, br = pts[j]
            d = math.hypot(ax - bx, ay - by) - ar - br
            if d < worst_nn[0]:
                worst_nn = (d, f"({ax}, {ay}) to ({bx}, {by})")
    report.append(f"nut to nut           {worst_nn[0]:6.2f} mm   {worst_nn[1]}")
    if worst_nn[0] < 0:
        fails.append(f"nuts overlap: {worst_nn[1]}")

    return report, fails


# --------------------------------------------------------------------------
# KiCad output
# --------------------------------------------------------------------------

ORIGIN = (60.0, 40.0)      # where the panel's top-left corner lands on the sheet


def arc_points(cx, cy, r, a0, a1):
    """Start / mid / end for a KiCad arc. Angles in degrees, Y down."""
    def p(a):
        t = math.radians(a)
        return (cx + r * math.cos(t), cy + r * math.sin(t))
    return p(a0), p((a0 + a1) / 2), p(a1)


def kicad(path):
    ox, oy = ORIGIN
    def X(v): return round(v + ox, 4)
    def Y(v): return round(v + oy, 4)
    def tid(): return f'(tstamp {uuid.uuid4()})'

    out = ['(kicad_pcb (version 20221018) (generator "gen_panel.py")',
           '  (general (thickness 1.6))',
           '  (paper "A4")',
           '  (layers',
           '    (0 "F.Cu" signal)',
           '    (31 "B.Cu" signal)',
           '    (36 "B.SilkS" user "B.Silkscreen")',
           '    (37 "F.SilkS" user "F.Silkscreen")',
           '    (38 "B.Mask" user)',
           '    (39 "F.Mask" user)',
           '    (44 "Edge.Cuts" user)',
           '    (45 "Margin" user)',
           '  )',
           '  (setup (pad_to_mask_clearance 0))',
           '  (net 0 "")']

    for x0, y0, x1, y1 in cuts_lines:
        out.append(f'  (gr_line (start {X(x0)} {Y(y0)}) (end {X(x1)} {Y(y1)}) '
                   f'(stroke (width 0.05) (type solid)) (layer "Edge.Cuts") {tid()})')
    for cx, cy, r, a0, a1 in cuts_arcs:
        s, m, e = arc_points(cx, cy, r, a0, a1)
        out.append(f'  (gr_arc (start {X(s[0])} {Y(s[1])}) (mid {X(m[0])} {Y(m[1])}) '
                   f'(end {X(e[0])} {Y(e[1])}) (stroke (width 0.05) (type solid)) '
                   f'(layer "Edge.Cuts") {tid()})')
    for cx, cy, r in cuts_circles:
        out.append(f'  (gr_circle (center {X(cx)} {Y(cy)}) (end {X(cx + r)} {Y(cy)}) '
                   f'(stroke (width 0.05) (type solid)) (fill none) '
                   f'(layer "Edge.Cuts") {tid()})')

    for x0, y0, x1, y1, w in silk_lines:
        out.append(f'  (gr_line (start {X(x0)} {Y(y0)}) (end {X(x1)} {Y(y1)}) '
                   f'(stroke (width {w}) (type solid)) (layer "F.SilkS") {tid()})')
    for cx, cy, r, a0, a1, w in silk_arcs:
        s, m, e = arc_points(cx, cy, r, a0, a1)
        out.append(f'  (gr_arc (start {X(s[0])} {Y(s[1])}) (mid {X(m[0])} {Y(m[1])}) '
                   f'(end {X(e[0])} {Y(e[1])}) (stroke (width {w}) (type solid)) '
                   f'(layer "F.SilkS") {tid()})')
    for ch, cx, baseline, size in chars:
        thick = round(max(0.15, size * 0.15), 3)
        glyph = ch.replace("−", "-")
        out.append(f'  (gr_text "{glyph}" (at {X(cx)} {Y(baseline - size / 2)}) '
                   f'(layer "F.SilkS") {tid()}'
                   f' (effects (font (size {size} {size}) (thickness {thick}))))')

    out.append(')')
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


# --------------------------------------------------------------------------
# SVG output - the same geometry, for printing at 1:1 and for review
# --------------------------------------------------------------------------

def svg(path):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PANEL_W}mm" '
         f'height="{PANEL_H}mm" viewBox="0 0 {PANEL_W} {PANEL_H}">',
         '  <title>Precision Adder v3 - panel, 4 HP, 1:1</title>',
         '  <desc>Generated by tools/gen_panel.py - do not edit by hand. To scale:',
         '  1 user unit = 1 mm. Grey rings are hardware footprints (8 mm Thonkiconn nut,',
         '  7.5 mm toggle nut) shown for clearance checking; they are not artwork and are',
         '  not in the KiCad output.</desc>',
         '  <g font-family="Helvetica, Arial, sans-serif" fill="#e8e8e8">',
         f'    <rect x="0" y="0" width="{PANEL_W}" height="{PANEL_H}" fill="#161616" '
         'stroke="#3c3c3c" stroke-width="0.12"/>']

    o.append('    <!-- hardware footprints, not artwork -->')
    o.append('    <g fill="#242424" stroke="#454545" stroke-width="0.1">')
    for cx, cy, r in cuts_circles:
        nut = (JACK_NUT if r > 2.6 else TOGGLE_NUT) / 2
        o.append(f'      <circle cx="{cx}" cy="{cy}" r="{nut}"/>')
    o.append('    </g>')

    o.append('    <!-- drilled holes and mounting slots -->')
    o.append('    <g fill="#000000">')
    for cx, cy, r in cuts_circles:
        o.append(f'      <circle cx="{cx}" cy="{cy}" r="{r}"/>')
    for cx, cy in MOUNTS:
        r = MOUNT_H / 2
        o.append(f'      <rect x="{cx - MOUNT_L / 2}" y="{cy - r}" width="{MOUNT_L}" '
                 f'height="{MOUNT_H}" rx="{r}"/>')
    o.append('    </g>')

    o.append('    <!-- silkscreen -->')
    o.append('    <g stroke="#e8e8e8" fill="none" stroke-linecap="round">')
    for x0, y0, x1, y1, w in silk_lines:
        o.append(f'      <line x1="{r4(x0)}" y1="{r4(y0)}" x2="{r4(x1)}" y2="{r4(y1)}" '
                 f'stroke-width="{w}"/>')
    for cx, cy, r, a0, a1, w in silk_arcs:
        s, _, e = arc_points(cx, cy, r, a0, a1)
        large = 1 if abs(a1 - a0) > 180 else 0     # SUM's ring is a 300+ deg sweep
        o.append(f'      <path d="M {r4(s[0])} {r4(s[1])} A {r} {r} 0 {large} 1 '
                 f'{r4(e[0])} {r4(e[1])}" stroke-width="{w}"/>')
    o.append('    </g>')

    o.append('    <g text-anchor="middle">')
    for ch, cx, baseline, size in chars:
        glyph = "&#8722;" if ch == "−" else ch
        o.append(f'      <text x="{r4(cx)}" y="{r4(baseline)}" font-size="{size}">'
                 f'{glyph}</text>')
    o.append('    </g>')

    o.append('  </g>')
    o.append('</svg>')
    with open(path, "w") as f:
        f.write("\n".join(o) + "\n")


def r4(v):
    return round(v, 4)


# --------------------------------------------------------------------------

def hole_table():
    """Markdown hole schedule, so the README cannot drift from the drawing."""
    rows = [("Y (mm)", "X (mm)", "Ø", "What")]
    named = []
    for name, col, row, ring in INPUTS:
        named.append((ROW_IN[row], COL_L if col == "L" else COL_R, JACK_D,
                      f"{name} (output, ringed)" if ring else name))
    for g in GROUPS:
        x = COL_L if g["col"] == "L" else COL_R
        top = BOX_TOP[g["row"]]
        named.append((top + SW1_DY, x, TOGGLE_D, f'{g["name"]} polarity  +/o/−'))
        det = f' (detent {g["detent"]})' if g["detent"] else ""
        named.append((top + SW2_DY, x, TOGGLE_D,
                      f'{g["name"]} select  {g["up"]}/{g["down"]}{det}'))
        named.append((top + OUT_DY, x, JACK_D, g["out"]))
    out = ["| Y (mm) | X (mm) | Ø | What |", "|---:|---:|---:|---|"]
    for y, x, d, what in sorted(named):
        out.append(f"| {y:.2f} | {x:.2f} | {d:.1f} | {what} |")
    for mx, my in sorted(MOUNTS, key=lambda m: m[1]):
        out.append(f"| {my:.2f} | {mx:.2f} | {MOUNT_L:.1f}×{MOUNT_H:.1f} "
                   f"| mounting slot, obround |")
    return "\n".join(out)


def main():
    build()
    if "--table" in sys.argv:
        print(hole_table())
        return 0
    report, fails = check()
    print("clearances")
    for line in report:
        print("  " + line)

    if fails:
        print("\nFAILED - nothing written:")
        for f in fails:
            print("  " + f)
        return 1

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs = os.path.join(here, "docs")
    kicad(os.path.join(docs, "v3-panel.kicad_pcb"))
    svg(os.path.join(docs, "v3-panel.svg"))
    print("\nwrote docs/v3-panel.kicad_pcb and docs/v3-panel.svg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
