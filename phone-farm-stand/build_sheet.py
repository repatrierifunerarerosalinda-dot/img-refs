#!/usr/bin/env python3
"""Construieste fisa tehnica (HTML -> PDF) din _params.json."""
import json, os, math
OUT = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(OUT, "_params.json")))
g = lambda k: P[k]
L,D,HI,T = g("L"),g("D"),g("HI"),g("T")

INK="#1b1f24"; CUT="#d62828"; DIM="#1d4ed8"; FILL="#dbeafe"

# ---------- cote ----------
def dim_h(x1,x2,y,txt,s,off=0):
    """cota orizontala intre x1..x2 (coord. desen), linia la y"""
    a=[]
    a.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{DIM}" stroke-width="0.8" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    a.append(f'<text x="{(x1+x2)/2}" y="{y-3}" font-size="10" fill="{DIM}" text-anchor="middle">{txt}</text>')
    return "".join(a)
def dim_v(y1,y2,x,txt):
    return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{DIM}" stroke-width="0.8" marker-start="url(#ar)" marker-end="url(#ar)"/>'
            f'<text x="{x-4}" y="{(y1+y2)/2}" font-size="10" fill="{DIM}" text-anchor="middle" transform="rotate(-90 {x-4} {(y1+y2)/2})">{txt}</text>')
def ext(x1,y1,x2,y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{DIM}" stroke-width="0.4" stroke-dasharray="2 2"/>'
DEFS=f'<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="{DIM}"/></marker></defs>'

def f(v): return f"{v:g}"

def part_svg(part, maxw, extra_dims):
    w,h = part["w"], part["h"]
    s = min(maxw/w, 1.2)
    pad_l, pad_t, pad_r, pad_b = 40, 40, 20, 34
    W, H = w*s+pad_l+pad_r, h*s+pad_t+pad_b
    X=lambda v: pad_l+v*s; Y=lambda v: pad_t+v*s
    o=[f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" xmlns="http://www.w3.org/2000/svg">',DEFS]
    pts=" ".join(f"{X(x):.2f},{Y(y):.2f}" for x,y in part["outline"])
    o.append(f'<polygon points="{pts}" fill="{FILL}" stroke="{INK}" stroke-width="1.2"/>')
    if part["code"]!="E":
        for cx,cy,cw,ch in part["cuts"]:
            o.append(f'<rect x="{X(cx):.2f}" y="{Y(cy):.2f}" width="{cw*s:.2f}" height="{ch*s:.2f}" fill="#fff" stroke="{CUT}" stroke-width="1"/>')
    # cote generale
    o.append(dim_h(X(0),X(w),Y(h)+22,f"{f(w)}",s))
    o.append(ext(X(0),Y(h),X(0),Y(h)+26)); o.append(ext(X(w),Y(h),X(w),Y(h)+26))
    o.append(dim_v(Y(0),Y(h),X(0)-22,f"{f(h)}"))
    o.append(ext(X(0),Y(0),X(0)-26,Y(0))); o.append(ext(X(0),Y(h),X(0)-26,Y(h)))
    for d in extra_dims: o.append(d(X,Y,s))
    o.append('</svg>')
    return "".join(o)

parts={p["code"]:p for p in P["parts"]}

# cote speciale
def deck_dims(X,Y,s):
    c=parts["B"]["cuts"]; a=c[0]; b=c[1]
    o=[]
    o.append(dim_h(X(0),X(a[0]),Y(0)-18,f"{f(a[0])}",s)); o.append(ext(X(a[0]),Y(a[1]),X(a[0]),Y(0)-22))
    o.append(dim_h(X(a[0]+a[2]/2),X(b[0]+b[2]/2),Y(0)-6,f"pas {f(P['PITCH'])}",s))
    o.append(f'<text x="{X(P["L"])}" y="{Y(P["D"])+12}" font-size="11" fill="{CUT}" text-anchor="end">fante {f(a[2])} × {f(a[3])} mm — 20 buc, centrate pe adâncime</text>')
    last=c[-1]
    o.append(dim_v(Y(0),Y(a[1]),X(last[0]+last[2])+30,""))
    o.append(dim_v(Y(a[1]),Y(a[1]+a[3]),X(last[0]+last[2])+30,f"{f(a[3])}"))
    o.append(f'<text x="{X(last[0]+last[2])+40}" y="{Y(a[1]/2)+4}" font-size="10" fill="{DIM}">{f(a[1])}</text>')
    return "".join(o)
def front_dims(X,Y,s):
    cx,cy,cw,ch=parts["C"]["cuts"][0]
    return (f'<text x="{X(cx+cw/2)}" y="{Y(cy+ch/2)+4}" font-size="10" fill="{CUT}" text-anchor="middle">fereastră {f(cw)} × {f(ch)}, la {f(P["WIN_Y0"])} mm de marginea de jos</text>'
            + dim_h(X(0),X(cx),Y(cy)-4,f"{f(cx)}",s))
def back_dims(X,Y,s):
    return f'<text x="{X(P["L"]/2)}" y="{Y(18)}" font-size="10" fill="{CUT}" text-anchor="middle">24 fante aerisire 30 × 6 (2 rânduri × 12), margini 30 mm — poziția nu e critică</text>'
def sideL_dims(X,Y,s):
    x0=P['SIDE_L']/2-11; top=P['HI']-28
    return (dim_h(X(x0),X(x0+22),Y(top)-6,"22",s)+dim_v(Y(top),Y(P['HI']),X(x0+22)+14,"28")
            + f'<text x="{X(P["SIDE_L"]/2)}" y="{Y(18)}" font-size="10" fill="{CUT}" text-anchor="middle">degajare cablu alimentare hub (centrată)</text>')
def sideR_dims(X,Y,s):
    return f'<text x="{X(P["SIDE_L"]/2)}" y="{Y(18)}" font-size="10" fill="{CUT}" text-anchor="middle">6 fante aerisire 6 × 30</text>'

# ---------- vedere izometrica ----------
def iso():
    c,sn=math.cos(math.radians(30)),math.sin(math.radians(30))
    k=0.78
    def pr(x,y,z):  # oblic: x lungime, y adancime (spre spate-dreapta), z sus
        return (25 + k*(x + y*0.55), 300 + k*(-z - y*0.38))
    def poly(pts,fill,stroke=INK,sw=0.8,op=1):
        return f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a,b in (pr(*p) for p in pts))}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'
    def box(x0,y0,z0,x1,y1,z1,fill,op=1):
        # fata (y0), sus (z1), dreapta (x1)
        return (poly([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],fill,op=op)
               +poly([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],fill,op=op)
               +poly([(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)],fill,op=op))
    H=HI+2*T
    acr="#1f2937"; glass="#3b82f6"
    o=[f'<svg viewBox="0 0 560 330" width="560" height="330" xmlns="http://www.w3.org/2000/svg">']
    # spate, baza, laterale
    o.append(box(0,D-T,T,L,D,T+HI,acr,0.85))
    o.append(box(0,0,0,L,D,T,acr,0.95))
    o.append(box(0,T,T,T,D-T,T+HI,acr,0.9))
    # hub (interior, vizibil prin fereastra)
    o.append(box(60,60,T,L-60,130,T+35,"#6b7280",1))
    o.append(box(L-T,T,T,L,D-T,T+HI,acr,0.9))
    # fata cu fereastra
    wx=(L-470)/2; wz0=T+P['WIN_Y0']; wz1=wz0+P['WIN_H']
    o.append(poly([(0,0,T),(L,0,T),(L,0,wz0),(0,0,wz0)],acr))
    o.append(poly([(0,0,wz1),(L,0,wz1),(L,0,T+HI),(0,0,T+HI)],acr))
    o.append(poly([(0,0,wz0),(wx,0,wz0),(wx,0,wz1),(0,0,wz1)],acr))
    o.append(poly([(L-wx,0,wz0),(L,0,wz0),(L,0,wz1),(L-wx,0,wz1)],acr))
    o.append(poly([(L,0,0),(L,T,0),(L,T,T+HI),(L,0,T+HI)],acr))
    # capac
    z=T+HI
    o.append(box(0,0,z,L,D,z+T,"#111827",0.95))
    y0=(D-P['SLOT_L'])/2
    for i in range(P['N']):
        xc=P['FIRST_X']+i*P['PITCH']
        o.append(poly([(xc-7,y0,z+T),(xc+7,y0,z+T),(xc+7,y0+P['SLOT_L'],z+T),(xc-7,y0+P['SLOT_L'],z+T)],"#000",stroke="#ef4444",sw=0.5))
    # telefoane
    for i in range(P['N']):
        xc=P['FIRST_X']+i*P['PITCH']
        o.append(box(xc-4.5,y0+5,z+T,xc+4.5,y0+P['SLOT_L']-5,z+T+50,"#0f172a",1))
        o.append(poly([(xc-4.5,y0+5,z+T+3),(xc-4.5,y0+P['SLOT_L']-5,z+T+3),(xc-4.5,y0+P['SLOT_L']-5,z+T+47),(xc-4.5,y0+5,z+T+47)],glass,op=0.35))
        # cablu
        ax,ay=pr(xc,y0+5,z+T+25); bx,by=pr(xc,0,T+P['WIN_Y0']+20)
        o.append(f'<path d="M{ax:.1f},{ay:.1f} C{ax-6:.1f},{ay+5:.1f} {bx-14:.1f},{by-30:.1f} {bx:.1f},{by:.1f}" fill="none" stroke="#9ca3af" stroke-width="1.1"/>')
    # etichete
    def lab(x,y,zz,t,dx=0,dy=0):
        a,b=pr(x,y,zz); return f'<text x="{a+dx:.0f}" y="{b+dy:.0f}" font-size="11" fill="{INK}">{t}</text>'
    o.append(lab(L,0,T+HI/2,"C – față (fereastră cabluri)",-130,52))
    o.append(lab(0,D,z+T+60,"B – capac cu 20 fante",10,-6))
    o.append('</svg>')
    return "".join(o)

# ---------- plan de taiere ----------
def layout_svg():
    s=0.75; W=P['SHEET_W']*s; H=P['SHEET_H']*s
    o=[f'<svg viewBox="-2 -2 {W+4:.0f} {H+20:.0f}" width="{W+4:.0f}" height="{H+20:.0f}" xmlns="http://www.w3.org/2000/svg">',
       f'<rect x="0" y="0" width="{W}" height="{H}" fill="#f8fafc" stroke="#94a3b8" stroke-dasharray="4 3"/>']
    for poly in P['polys']:
        o.append(f'<polygon points="{" ".join(f"{x*s:.1f},{y*s:.1f}" for x,y in poly)}" fill="none" stroke="{CUT}" stroke-width="0.7"/>')
    for code,x,y,rot in P['layout']:
        pt=parts[code]; w,h=(pt['h'],pt['w']) if rot else (pt['w'],pt['h'])
        o.append(f'<text x="{(x+w/2)*s:.0f}" y="{(y+h/2)*s+5:.0f}" font-size="14" font-weight="700" fill="{DIM}" text-anchor="middle">{code}</text>')
    o.append(f'<text x="{W/2:.0f}" y="{H+15:.0f}" font-size="11" text-anchor="middle" fill="{INK}">placă minimă {P["SHEET_W"]:.0f} × {P["SHEET_H"]:.0f} mm (acrilic negru/fumuriu 5 mm)</text>')
    o.append('</svg>'); return "".join(o)

def card(code, maxw, dims=()):
    p=parts[code]
    return (f'<div class="part"><h3><span class="tag">{code}</span>{p["name"]} <small>— {p["qty"]} buc · {f(p["w"])}×{f(p["h"])}×{T} mm</small></h3>'
            + part_svg(p,maxw,list(dims)) + '</div>')

rows="".join(f'<tr><td><b>{p["code"]}</b></td><td>{p["name"]}</td><td>{f(p["w"])} × {f(p["h"])}</td><td>{p["qty"]}</td></tr>' for p in P["parts"])

html=f"""<!doctype html><html lang="ro"><head><meta charset="utf-8"><title>Suport 20 telefoane – fișă tehnică</title>
<style>
@page {{ size: A4 landscape; margin: 11mm; }}
body {{ font-family: 'DejaVu Sans', Arial, sans-serif; color:{INK}; font-size:11px; margin:0; }}
.page {{ page-break-after: always; }}
h1 {{ font-size:20px; margin:0 0 2px; }} h2 {{ font-size:14px; margin:12px 0 6px; border-bottom:1px solid #cbd5e1; padding-bottom:3px; }}
h3 {{ font-size:12px; margin:4px 0; }} small {{ color:#64748b; font-weight:400; }}
.tag {{ display:inline-block; background:{DIM}; color:#fff; border-radius:3px; padding:0 6px; margin-right:6px; }}
.row {{ display:flex; gap:18px; align-items:flex-start; }}
table {{ border-collapse:collapse; }} td,th {{ border:1px solid #cbd5e1; padding:3px 7px; text-align:left; }}
th {{ background:#f1f5f9; }} ul,ol {{ margin:4px 0; padding-left:18px; }} li {{ margin:2px 0; }}
.note {{ background:#fef9c3; border:1px solid #facc15; padding:6px 9px; border-radius:4px; }}
.part {{ border:1px solid #e2e8f0; border-radius:5px; padding:4px 8px; margin-bottom:8px; }}
.leg span {{ margin-right:14px; }}
</style></head><body>

<div class="page">
<h1>Suport fermă telefoane — 20 locuri, acrilic 5 mm</h1>
<div style="color:#64748b">Toate cotele în mm · toleranță ±0,5 · fișierele de tăiere: <b>taiere_laser_acrilic_5mm.dxf</b> / <b>.svg</b> (scară 1:1)</div>
<div class="row">
<div>{iso()}</div>
<div style="flex:1">
<h2>Dimensiuni de gabarit</h2>
<b>{L} × {D} × {HI+2*T} mm</b> (L × A × Î) · telefoane culcate pe latura lungă, la pas de {P['PITCH']} mm
<h2>Listă piese</h2>
<table><tr><th>Cod</th><th>Piesă</th><th>L × l (mm)</th><th>Buc</th></tr>{rows}</table>
<h2>Material</h2>
<ul><li>Plexiglas/acrilic turnat (GS) 5 mm, negru lucios sau fumuriu — placă ~{P['SHEET_W']:.0f}×{P['SHEET_H']:.0f} mm</li>
<li>Adeziv acrilic (Acrifix 1R0192 / 1S0116) sau diclormetan</li>
<li>4 picioare cauciuc autoadezive · opțional bandă LED 12/5 V pentru efect</li></ul>
</div></div>
<div class="note"><b>Verificați înainte de tăiere:</b> fanta are {P['SLOT_W']} × {P['SLOT_L']} mm — încape un telefon cu husă de max. ~12 mm grosime și ~170 mm lungime.
În interior, sub sine, rămâne loc pentru hub: max. <b>{L-2*T-10} × {D-2*T-10} × {P['RAIL_TOP']-T-5} mm</b> (L × A × Î). Dacă hubul vostru e mai înalt, măriți înălțimea panourilor C, D, E, F.</div>
</div>

<div class="page">
<h2>Desene piese</h2>
{card("B", 900, [deck_dims])}
<div class="row"><div>{card("A", 430)}</div><div>{card("C", 430, [front_dims])}</div></div>
</div>

<div class="page">
<div class="row"><div>{card("D", 430, [back_dims])}</div><div>{card("G", 430)}</div></div>
<div class="row"><div>{card("E", 260, [sideL_dims])}</div><div>{card("F", 260, [sideR_dims])}</div>
<div style="flex:1"><h2 style="margin-top:4px">Asamblare</h2>
<ol>
<li>Lipiți <b>C</b> (față) și <b>D</b> (spate) pe <b>A</b> (bază), pe marginile lungi, la exterior.</li>
<li>Lipiți <b>E</b> (stânga) și <b>F</b> (dreapta) între C și D — degajarea din E stă jos, la bază.</li>
<li>Lipiți cele 2 <b>sine G</b> pe fața interioară a lui C și D, cu fața de sus la <b>{P['RAIL_TOP']} mm</b> de la baza panoului
({P['INSERT']} mm sub capac). Pe ele se sprijină telefoanele.</li>
<li>Puneți hubul înăuntru, cu porturile spre fereastra din C; cablul de alimentare iese prin E.</li>
<li><b>B</b> (capacul) se pune deasupra — recomandat doar <b>prins cu 4 puncte de silicon</b> sau bandă dublu-adezivă, ca să se poată scoate hubul.</li>
<li>Telefoanele intră în fante cu portul spre față; cablurile coboară prin fereastra din C în hub.</li>
</ol></div></div>
</div><div class="page"><h2>Plan de tăiere (A–G pe o singură placă)</h2>
<div class="row"><div>{layout_svg()}</div>
<div style="flex:1"><ul>
<li>Linie roșie = tăiere (layer <b>TAIERE</b>). Nu există gravuri.</li>
<li>Fișierele sunt la cota nominală; compensarea razei laserului (kerf) o aplică atelierul.</li>
<li>Toate decupajele sunt interioare; se taie întâi interioarele, apoi conturul.</li>
<li>Parametrii se pot modifica în <b>generate.py</b> (grosime, pas, fante, număr de telefoane).</li>
</ul></div></div>
</div>
</body></html>"""
open(os.path.join(OUT,"fisa_tehnica.html"),"w").write(html)
print("ok")
