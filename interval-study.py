#!/usr/bin/env python3
"""Precision Adder interval study.

Each stage contributes +v, -v, or 0, so N stages give 3^N configurations.
On v2.2 the zero state costs a patch cable (PT -> IN of the next stage)
because the switches are ON-ON; on the v3 proposal it is the center detent
of an ON-OFF-ON.  The arithmetic is the same either way.  Values are in
semitones; 1 semitone = 1/12 V in the 1V/octave standard.
"""
from itertools import product, combinations
from fractions import Fraction

NAMES = {0:"unison",1:"min 2nd",2:"maj 2nd",3:"min 3rd",4:"maj 3rd",5:"4th",
         6:"tritone",7:"5th",8:"min 6th",9:"maj 6th",10:"min 7th",11:"maj 7th",
         12:"octave"}

def reach(vals, extra=(0,)):
    """Set of reachable offsets. `extra` = states of a multi-value stage."""
    return {e + sum(c*v for c, v in zip(k, vals))
            for e in extra for k in product([1,0,-1], repeat=len(vals))}

def contig(S):
    """Widest symmetric run around 0 with every semitone present."""
    n = 0
    while (n+1) in S and -(n+1) in S: n += 1
    return n

def pcs(S):     return len({s % 12 for s in S})
def combos(v, extra=(0,)): return len(extra) * 3**len(v)

BASE = [24, 12, 7, 5]           # v2.2
OCT2 = [0, 12, -12, 24, -24]    # collapsed 1V/2V octave stage
OCT3 = [0, 12, -12, 36, -36]    # collapsed 1V/3V octave stage

def row(v, extra=(0,)):
    S = reach(v, extra)
    return len(S), combos(v, extra), contig(S), pcs(S)

print("### v2.2 baseline")
d,t,c,p = row(BASE)
print(f"  {{24,12,7,5}}  {d} distinct / {t} combos, chromatic +/-{c}, {p}/12 pitch classes\n")

print("### chart 1 - one stage added to v2.2, by interval")
for x in range(1, 13):
    d,t,c,p = row(BASE+[x])
    print(f"  +{x:2d} st {NAMES[x]:<9} {d:3d} distinct  chromatic +/-{c:2d}  {p:2d}/12 pc")

print("\n### chart 2 - best 4-value sets, unconstrained (search 1..27)")
r = sorted(((contig(reach(list(k))), len(reach(list(k))), k)
            for k in combinations(range(1,28), 4)), reverse=True)[:8]
for c,d,k in r: print(f"  {str(k):<14} {d:2d}/81 distinct  chromatic +/-{c:2d} ({c/12:.2f} oct)")

print("\n### chart 3 - constrained: must keep both octave stages (12 and 24)")
r = sorted(((contig(reach([24,12,a,b])), len(reach([24,12,a,b])), (a,b))
            for a,b in combinations(range(1,12), 2)), reverse=True)[:5]
for c,d,k in r: print(f"  {{24,12,{k[0]},{k[1]}}}  {d:2d}/81 distinct  chromatic +/-{c:2d}")

print("\n### chart 4 - constrained: must keep one octave stage (12)")
r = sorted(((contig(reach([12]+list(k))), len(reach([12]+list(k))), k)
            for k in combinations([x for x in range(1,28) if x!=12], 3)), reverse=True)[:4]
for c,d,k in r: print(f"  {{12,{k[0]},{k[1]},{k[2]}}}  {d:2d}/81 distinct  chromatic +/-{c:2d}")

print("\n### chart 5 - collapsed octave stage, best 3-value fill")
for lbl, O in (("1V/2V", OCT2), ("1V/3V", OCT3)):
    r = sorted(((contig(reach(list(k), O)), len(reach(list(k), O)), k)
                for k in combinations(range(1,20), 3)), reverse=True)[:3]
    print(f"  {lbl}:")
    for c,d,k in r:
        print(f"    {str(k):<11} {d:3d} distinct /135  chromatic +/-{c:2d} ({c/12:.2f} oct)")

print("\n### chart 6 - four stages added to v2.2 (8 total, 6561 combos)")
r = sorted(((contig(reach(BASE+list(k))), len(reach(BASE+list(k))), k)
            for k in combinations(range(1,13), 4)), reverse=True)[:4]
for c,d,k in r: print(f"  add {str(k):<15} {d:3d} distinct  chromatic +/-{c:2d} ({c/12:.2f} oct)")

print("\n### chart 7 - summary")
for lbl, v, e in (("v2.2 {24,12,7,5}", BASE, (0,)),
                  ("ternary {1,3,9,27}", [1,3,9,27], (0,)),
                  ("collapsed 1V/2V + {1,3,9}", [1,3,9], OCT2),
                  ("collapsed 1V/2V + {4,9,19}", [4,9,19], OCT2),
                  ("collapsed 1V/3V + {1,3,9}", [1,3,9], OCT3)):
    d,t,c,p = row(v, e)
    print(f"  {lbl:<28} {d:3d} distinct /{t:4d}  chromatic +/-{c:2d} ({c/12:.2f} oct)  {p:2d}/12 pc")

print("\n### ternary voltages")
for st in (1,3,9,27):
    print(f"  {st:2d} st = {str(Fraction(st,12)):>4} V = {st/12:.6f} V")

OCT2 = [0, 12, -12, 24, -24]
SUP  = [7, 5, 4]                # superseded proposal: 5th, 4th, maj 3rd

def flips(t, v, extra=(0,)):
    """Fewest switch flips from all-bypassed to reach t. Unreachable -> None."""
    best = None
    for e in extra:
        for k in product([1,0,-1], repeat=len(v)):
            if e + sum(c*x for c, x in zip(k, v)) == t:
                n = (1 if e else 0) + sum(1 for c in k if c)
                best = n if best is None else min(best, n)
    return best

def max_fill(v, extra=(0,)):
    """Largest magnitude ever needed on the non-octave stages."""
    w = 0
    for t in reach(v, extra):
        w = max(w, min(abs(t-e) for e in extra
                       if t-e in reach(v)))
    return w

print("\n### chart 8 - usability")
DESIGNS = (("v2.2 {24,12,7,5}", BASE, (0,), "interval names"),
           ("ternary {1,3,9,27}", [1,3,9,27], (0,), "balanced ternary"),
           ("1V/3V oct + {1,3,9}", [1,3,9], OCT3, "balanced ternary"),
           ("1V/2V oct + {4,2,1}", [4,2,1], OCT2, "binary 0-7"),
           ("1V/2V oct + {7,5,4}", SUP, OCT2, "interval names"))
for lbl, v, e, model in DESIGNS:
    S = reach(v, e)
    got = [flips(t, v, e) for t in range(1, 13)]
    got = [g for g in got if g is not None]
    avg = sum(got)/len(got) if got else 0
    print(f"  {lbl:<22} chromatic +/-{contig(S):<3} max fill {max_fill(v,e):>2}  "
          f"{len(got):>2}/12 intervals  avg {avg:.2f} flips  ({model})")

print("\n  cost per interval, cheapest setting")
print("  " + "interval".ljust(10) + "".join(l[:18].rjust(20) for l,_,_,_ in DESIGNS))
for t in (1,4,5,6,7,9,12,19,24):
    nm = NAMES.get(t) or (f"{t//12} oct + {NAMES[t%12]}" if t % 12 else f"{t//12} octaves")
    r = "  " + nm.ljust(10)
    for lbl, v, e, _ in DESIGNS:
        f = flips(t, v, e)
        r += ("-" if f is None else f"{f} flip" + ("s" if f != 1 else "")).rjust(20)
    print(r)

print("\n### superseded: settings chart for 1V/2V octave + {7,5,4}")
best = {}
for e in OCT2:
    for k in product([1,0,-1], repeat=3):
        t = e + sum(c*x for c, x in zip(k, SUP))
        cost = (1 if e else 0) + sum(1 for c in k if c)
        sett = ({0:"o",12:"+1",-12:"-1",24:"+2",-24:"-2"}[e],
                *({1:"+",0:"o",-1:"-"}[c] for c in k))
        if t not in best or cost < best[t][0]:
            best[t] = (cost, sett)
S = reach(SUP, OCT2)
print(f"  {len(S)} distinct / 135 combos, fully chromatic +/-{contig(S)} st\n")
print("  st   volts  interval              OCT 5th 4th M3  flips")
for t in range(0, 34):
    if t not in best: continue
    c, s = best[t]
    nm = NAMES.get(t) or (f"{t//12} oct + {NAMES[t%12]}" if t % 12 else f"{t//12} octaves")
    print(f"  {t:>2} {t/12:>7.4f}  {nm:<20} {s[0]:>3} {s[1]:>3} {s[2]:>3} {s[3]:>3} {c:>5}")

# --- v3 proposal: octave stage + 4th/M3/m3 x2 + 5th/M3/m3 -------------------
print("\n### v3 proposal - oct{1,2} + {5,4,3} + {5,4,3} + {7,4,3}")
def multi(vals): return [0] + [s*x for x in vals for s in (1, -1)]
V3 = [multi([12,24]), multi([5,4,3]), multi([5,4,3]), multi([7,4,3])]  # current
S = {sum(p) for p in product(*V3)}
n = 0
while (n+1) in S and -(n+1) in S: n += 1
print(f"  {len(S)} distinct / {len(list(product(*V3)))} configs, "
      f"chromatic +/-{n} st ({n/12:.2f} oct), {len({x%12 for x in S})}/12 pitch classes")

print("\n  chord matrix - stages 2,3 set the triad; stage 4 the extension")
TRIAD = {(4,3):"major", (3,4):"minor", (3,3):"diminished", (4,4):"augmented"}
PCN = {0:"1",1:"b9",2:"9",3:"m3",4:"M3",5:"11",6:"b5",7:"5",8:"#5",9:"13",10:"m7",11:"M7"}
for (a,b), name in TRIAD.items():
    row = f"  {name:<11}"
    for c in (3, 4, 7):
        v = [0, a, a+b, a+b+c]
        row += "  " + " ".join(PCN[x % 12] for x in v).ljust(16)
    print(row)
print("  " + " "*11 + "  " + "st4=m3".ljust(18) + "st4=M3".ljust(18) + "st4=5th")
