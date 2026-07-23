#!/usr/bin/env python3
"""Render the seminar HTML to a crisp, furniture-free multi-page PDF.

Why not one giant page: a single ~292-inch page is ~45 Mpx at fit-width, which
exceeds the per-page raster cap of PDF.js-based viewers (VS Code, browsers, ~16.7
Mpx) — so the viewer downsamples the whole page and the text looks blurry, even
though it is really vector text.

Fix: paginate onto a continuous-feeling page — the SAME 9.375-in content width, so
the layout and tables are byte-for-byte the layout that was verified, and a page
HEIGHT small enough to stay well under the raster cap even on a retina display
(2400 px fit-width). No page numbers, no headers/footers — it still reads as one
continuous document, but every page renders sharp.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "reports" / "GEOMIND-R-checkpoint-3.html"
PDF = ROOT / "reports" / "GEOMIND-R-checkpoint-3.pdf"

CHROME = (shutil.which("google-chrome") or shutil.which("chromium")
          or shutil.which("chromium-browser"))
if not CHROME:
    sys.exit("no chrome/chromium found")

# 9.375 in = 900 CSS px : identical width to the verified layout (tables unchanged).
PAGE_W_IN = 9.375
# 22 in tall: at a 2400 px retina fit-width that is 2400 x 5632 = 13.5 Mpx per page,
# safely under the ~16.7 Mpx cap, so pages stay crisp at any normal zoom.
PAGE_H_IN = 22.0
MARGIN_TB_IN = 0.32  # small top/bottom breathing room between page breaks

with tempfile.TemporaryDirectory() as td:
    tdp = Path(td)
    html_txt = HTML.read_text(encoding="utf-8")
    inject = (
        f"<style>@page{{size:{PAGE_W_IN}in {PAGE_H_IN}in;"
        f"margin:{MARGIN_TB_IN}in 0}}html,body{{margin:0}}</style>"
    )
    html_txt = html_txt.replace("</head>", inject + "</head>")
    tmp = tdp / "print.html"
    tmp.write_text(html_txt, encoding="utf-8")

    subprocess.run(
        [
            CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", f"--user-data-dir={tdp/'prof'}",
            "--no-pdf-header-footer", "--window-size=1200,1200",
            f"--print-to-pdf={PDF}", tmp.as_uri(),
        ],
        check=True, capture_output=True,
    )

doc = fitz.open(PDF)
p0 = doc[0]
w_px = 2400
mpx = w_px * (w_px * p0.rect.height / p0.rect.width) / 1e6
print(f"wrote {PDF}: {len(doc)} pages, "
      f"{p0.rect.width/72:.2f} x {p0.rect.height/72:.1f} in "
      f"({mpx:.1f} Mpx at retina fit-width; cap ~16.7 -> crisp)", file=sys.stderr)
doc.close()
