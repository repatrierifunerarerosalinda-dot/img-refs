# Suport fermă telefoane – 20 locuri (acrilic 5 mm)

| Fișier | Pentru ce |
|---|---|
| `fisa_tehnica.pdf` | Desenul cu cote, lista de piese, asamblarea – de dat atelierului |
| `taiere_laser_acrilic_5mm.dxf` | Fișierul de tăiere laser (mm, 1:1, layer TAIERE) |
| `taiere_laser_acrilic_5mm.svg` | Același fișier în format SVG |
| `generate.py`, `build_sheet.py` | Regenerează fișierele dacă schimbați dimensiunile |

Gabarit: 540 × 210 × 95 mm. Fante 14 × 175 mm, pas 25 mm. Spațiu pentru hub în interior: max 520 × 190 × 55 mm.

Regenerare: `python3 generate.py && python3 build_sheet.py`, apoi tipăriți `fisa_tehnica.html` în PDF.
