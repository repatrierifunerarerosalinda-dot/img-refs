#!/usr/bin/env python3
"""Genereaza fisierele de taiere pentru suportul de 20 telefoane (acrilic 5 mm).
Toate dimensiunile in mm. Modifica parametrii de mai jos si ruleaza din nou."""
import math, os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------- PARAMETRI ----------------
T       = 5      # grosime acrilic
N       = 20     # numar telefoane
PITCH   = 25     # distanta intre fante (centru-centru)
SLOT_W  = 14     # latime fanta (telefon + husa <= ~12 mm)
SLOT_L  = 175    # lungime fanta (telefon culcat pe latura lunga, cu husa <= ~170 mm)
L       = 540    # lungime totala
D       = 210    # adancime totala
HI      = 85     # inaltime interioara (intre baza si capac)
INSERT  = 20     # cat coboara telefonul sub capac (pana pe sinele de sprijin)
RAIL_W  = 25     # latime sine de sprijin
WIN_H   = 40     # inaltime fereastra cabluri (panou fata)
WIN_Y0  = 8      # fereastra incepe la ... mm de la baza panoului

SIDE_L  = D - 2*T          # panourile laterale stau intre fata si spate
RAIL_L  = L - 2*T          # sinele stau intre laterale
RAIL_TOP = HI - INSERT     # inaltimea fetei superioare a sinei, de la baza panoului
FIRST_X = (L - (N-1)*PITCH) / 2

# ---------------- GEOMETRIE PIESE ----------------
# fiecare piesa: (nume, cod, latime, inaltime, lista contururi interioare [(x,y,w,h)], buc)
def deck_cuts():
    y0 = (D - SLOT_L)/2
    return [(FIRST_X + i*PITCH - SLOT_W/2, y0, SLOT_W, SLOT_L) for i in range(N)]

def front_cuts():
    return [((L-470)/2, HI - WIN_Y0 - WIN_H, 470, WIN_H)]   # y masurat de sus in SVG

def back_cuts():   # fante de aerisire
    n, w, h = 12, 30, 6
    gap = (L - 60 - n*w) / (n-1)
    out = []
    for row in (HI-35, HI-20):
        for i in range(n):
            out.append((30 + i*(w+gap), row, w, h))
    return out

def side_left_cuts():  # degajare pt cablul de alimentare al hub-ului (deschisa jos)
    return [(SIDE_L/2 - 11, HI - 28, 22, 28)]

def side_right_cuts():
    return [(40 + i*(SIDE_L-80-6)/5, HI-45, 6, 30) for i in range(6)]

PARTS = [
    ("Baza (jos)",                  "A", L, D,       [],                1),
    ("Capac cu 20 fante (sus)",     "B", L, D,       deck_cuts(),       1),
    ("Panou fata (fereastra cabluri)","C", L, HI,    front_cuts(),      1),
    ("Panou spate (aerisire)",      "D", L, HI,      back_cuts(),       1),
    ("Lateral stanga (alimentare)", "E", SIDE_L, HI, side_left_cuts(),  1),
    ("Lateral dreapta (aerisire)",  "F", SIDE_L, HI, side_right_cuts(), 1),
    ("Sina sprijin",                "G", RAIL_L, RAIL_W, [],            2),
]

def outline_of(code, w, h):
    """Conturul exterior. Lateralul stanga are degajarea deschisa spre baza,
    deci conturul trece prin ea."""
    if code == "E":
        x0, x1, top = SIDE_L/2 - 11, SIDE_L/2 + 11, HI - 28
        return [(0,0),(w,0),(w,h),(x1,h),(x1,top),(x0,top),(x0,h),(0,h)]
    return [(0,0),(w,0),(w,h),(0,h)]

# ---------------- ASEZARE PE PLACA ----------------
GAP = 10
layout = []   # (code, x, y, rotated)
y = GAP
for code in "ABCD":
    p = next(p for p in PARTS if p[1]==code)
    layout.append((code, GAP, y, False)); y += p[3] + GAP
col2 = GAP + L + GAP
layout.append(("E", col2, GAP, True))
layout.append(("F", col2 + HI + GAP, GAP, True))
layout.append(("G", col2, GAP + SIDE_L + GAP, True))
layout.append(("G", col2 + RAIL_W + GAP, GAP + SIDE_L + GAP, True))
SHEET_W = col2 + 2*HI + 2*GAP
SHEET_H = max(y, GAP + SIDE_L + GAP + RAIL_L + GAP)

def transformed(code, x0, y0, rot):
    p = next(p for p in PARTS if p[1]==code)
    _, _, w, h, cuts, _ = p
    def tr(px, py):
        return (x0 + h - py, y0 + px) if rot else (x0 + px, y0 + py)
    polys = [[tr(*pt) for pt in outline_of(code, w, h)]]
    for (cx, cy, cw, ch) in cuts:
        if code == "E":   # deja inclusa in contur
            continue
        polys.append([tr(cx,cy), tr(cx+cw,cy), tr(cx+cw,cy+ch), tr(cx,cy+ch)])
    return polys

all_polys = []
for code, x0, y0, rot in layout:
    all_polys += transformed(code, x0, y0, rot)

# ---------------- SVG (1:1 mm) ----------------
def write_svg(path):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SHEET_W}mm" height="{SHEET_H}mm" '
         f'viewBox="0 0 {SHEET_W} {SHEET_H}">',
         '<g id="TAIERE" fill="none" stroke="#ff0000" stroke-width="0.1">']
    for poly in all_polys:
        s.append('<polygon points="' + " ".join(f"{x:.3f},{y:.3f}" for x,y in poly) + '"/>')
    s.append('</g></svg>')
    open(path, "w").write("\n".join(s))

# ---------------- DXF (R12, mm) ----------------
def write_dxf(path):
    o = ["0","SECTION","2","HEADER","9","$INSUNITS","70","4","0","ENDSEC",
         "0","SECTION","2","ENTITIES"]
    for poly in all_polys:
        for i in range(len(poly)):
            (x1,y1),(x2,y2) = poly[i], poly[(i+1)%len(poly)]
            # DXF are axa Y in sus
            o += ["0","LINE","8","TAIERE","62","1",
                  "10",f"{x1:.3f}","20",f"{SHEET_H-y1:.3f}","30","0",
                  "11",f"{x2:.3f}","21",f"{SHEET_H-y2:.3f}","31","0"]
    o += ["0","ENDSEC","0","EOF"]
    open(path, "w").write("\n".join(o))

write_svg(os.path.join(OUT, "taiere_laser_acrilic_5mm.svg"))
write_dxf(os.path.join(OUT, "taiere_laser_acrilic_5mm.dxf"))
print(f"Placa necesara: {SHEET_W:.0f} x {SHEET_H:.0f} mm")
print(f"Prima fanta la {FIRST_X} mm de margine; sina sus la {RAIL_TOP} mm")

# export parametri pt fisa tehnica
import json
json.dump(dict(T=T,N=N,PITCH=PITCH,SLOT_W=SLOT_W,SLOT_L=SLOT_L,L=L,D=D,HI=HI,INSERT=INSERT,
               RAIL_W=RAIL_W,WIN_H=WIN_H,WIN_Y0=WIN_Y0,SIDE_L=SIDE_L,RAIL_L=RAIL_L,
               RAIL_TOP=RAIL_TOP,FIRST_X=FIRST_X,SHEET_W=SHEET_W,SHEET_H=SHEET_H,
               polys=all_polys, layout=layout,
               parts=[dict(name=p[0],code=p[1],w=p[2],h=p[3],cuts=p[4],qty=p[5],
                           outline=outline_of(p[1],p[2],p[3])) for p in PARTS]),
          open(os.path.join(OUT, "_params.json"), "w"))
