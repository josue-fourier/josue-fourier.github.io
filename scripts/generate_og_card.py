#!/usr/bin/env python3
"""Generate the 1200x630 social share card (og-card.png) with headless Chrome, in the site's light theme.

Usage (from the repo root):
    python scripts/generate_og_card.py
    python scripts/generate_og_card.py --photo path/to/new_photo.jpg
    python scripts/generate_og_card.py --photo me.png --focus "50% 20%" --grayscale 0

Options:
    --photo      Portrait to use (default: static/portfolio/images/profile.jpg)
    --output     Output PNG (default: static/portfolio/images/og-card.png)
    --focus      CSS object-position for cropping the square portrait (default "center")
    --grayscale  0.0 (full colour, default) .. 1.0 (black & white)
    --name / --subtitle / --bio / --open / --fact / --tagline / --badge   Override texts
    --keep-html  Also keep the intermediate HTML next to the output (for tweaking)

Requires Google Chrome / Chromium. Set CHROME_BIN to point at a custom binary.
After regenerating, run `python djangoPortfolio/manage.py collectstatic --noinput`.
"""
import argparse
import html
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "djangoPortfolio" / "static" / "portfolio"

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
@import url("__FONTS__");
*{margin:0;box-sizing:border-box}
/* Tokens mirror the site's light (lofi) theme in custom.css */
:root{--bg:#F8F9FA;--surface:#fff;--ink:#0F172A;--ink2:#334155;--muted:#475569;--line:rgba(0,0,0,.12);--accent:#059669}
body{width:1200px;height:630px;background:var(--bg);color:var(--ink);font-family:'Space Grotesk';position:relative;overflow:hidden;display:grid;grid-template-columns:720px 1fr}
.mono{font-family:'JetBrains Mono';text-transform:uppercase}
svg.ecc{position:absolute;left:0;top:0;width:720px;height:630px}
.left{position:relative;padding:56px 56px 44px;display:flex;flex-direction:column;gap:24px}
.tag{font-size:14px;letter-spacing:.1em;color:var(--muted);display:flex;gap:10px;align-items:center}
.tag i{width:7px;height:7px;background:var(--accent)}
h1{font-size:112px;line-height:.9;letter-spacing:-.04em;text-transform:uppercase;font-weight:700}
.sub{font-family:Inter;font-weight:300;font-size:23px;line-height:1.3;color:var(--ink2);width:600px}
.open{font-family:Inter;font-size:16px;line-height:1.45;color:var(--ink2);width:600px;padding:12px 16px 12px 20px;background:#E7F3EE;position:relative;border-left:2px solid var(--accent)}
.open b{color:var(--ink);font-weight:600}
.foot{margin-top:auto;font-size:14px;letter-spacing:.14em;color:var(--muted);display:flex;gap:14px}
.foot em{font-style:normal;color:var(--accent);font-weight:700}
.right{position:relative;background:var(--surface);border-left:1px solid var(--line);padding:56px 48px 44px;display:flex;flex-direction:column;gap:28px}
.who{display:flex;gap:20px;align-items:center}
.ph{position:relative;flex:none;width:150px;height:150px;border:1px solid var(--line);background:var(--surface)}
.ph img{width:100%;height:100%;object-fit:cover;object-position:__FOCUS__;filter:grayscale(__GRAY__)}
.ph::before,.ph::after{content:"";position:absolute;width:20px;height:20px;border:2px solid var(--accent);z-index:2}
.ph::before{top:-7px;left:-7px;border-right:0;border-bottom:0}.ph::after{bottom:-7px;right:-7px;border-left:0;border-top:0}
.who p{font-family:'JetBrains Mono';font-size:13px;line-height:1.55;color:var(--ink2)}
dl{font-family:'JetBrains Mono';font-size:14px;border-top:1px solid var(--line)}
dl div{display:grid;grid-template-columns:110px 1fr;gap:12px;padding:12px 0;border-bottom:1px solid var(--line)}
dt{text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-size:12px;padding-top:1px}
dd{color:var(--ink)}
.badge{margin-top:auto;font-size:14px;letter-spacing:.14em;color:var(--accent);text-align:right;font-weight:700}
</style></head><body>
<div class="left">__ECC__
<div class="tag mono"><i></i>__LOCATION__</div>
<h1>__NAME__<span style="color:var(--accent)">.</span></h1>
<div class="sub">__SUBTITLE__</div>
<div class="open">__OPEN__</div>
<div class="foot mono"><em>__HANDLE__</em><span>//</span><span>__TAGLINE__</span></div>
</div>
<div class="right">
<div class="who"><div class="ph"><img src="__PHOTO__"></div><p>__BIO__</p></div>
<dl>__FACTS__</dl>
<div class="badge mono">__BADGE__</div>
</div>
</body></html>
"""

DEFAULT_FACTS = ["Now|Research assistant, LabOPT (UTFSM)", "Graduation|Expected December 2029",
                 "Awards|Academic Merit Recognition, 2025 and 2026", "Languages|Spanish (native), English C1",
                 "HackerRank|C++ 5★"]


def mesh_svg():
    """Static version of the home hero mesh (same layout as hero-network.js): nodes, links, one packet chain."""
    N = [(.1, .86), (.44, .7), (.8, .8), (.08, .5), (.3, .42), (.6, .5), (.9, .55), (.2, .15),
         (.5, .2), (.75, .12), (.95, .3), (.36, .92), (.62, .94)]
    E = {(0, 1), (1, 2)}
    for i, n in enumerate(N):
        for j in sorted(range(len(N)), key=lambda j: (n[0] - N[j][0]) ** 2 + (n[1] - N[j][1]) ** 2)[1:3]:
            E.add((min(i, j), max(i, j)))
    xy = lambda n: (40 + n[0] * 640, 40 + n[1] * 550)
    line = lambda a, b, col, w: '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"/>' % (*xy(N[a]), *xy(N[b]), col, w)
    links = "".join(line(a, b, "rgba(15,23,42,.10)", 1) for a, b in sorted(E))
    chain = line(0, 1, "rgba(5,150,105,.6)", 1.5) + line(1, 2, "rgba(5,150,105,.6)", 1.5)
    dots = "".join('<circle cx="%.1f" cy="%.1f" r="%d" fill="rgba(15,23,42,.22)"/>' % (*xy(n), 3 if k < 3 else 2) for k, n in enumerate(N))
    rings = "".join('<circle cx="%.1f" cy="%.1f" r="6" fill="none" stroke="rgba(5,150,105,.6)"/>' % xy(N[k]) for k in (0, 2))
    return '<svg class="ecc" viewBox="0 0 720 630">%s%s%s%s</svg>' % (links, chain, dots, rings)


def find_chrome():
    env = os.environ.get("CHROME_BIN")
    if env:
        return env
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        path = shutil.which(name)
        if path:
            return path
    sys.exit("Chrome/Chromium not found. Install it or set CHROME_BIN.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--photo", default=str(STATIC / "images" / "profile.jpg"))
    ap.add_argument("--output", default=str(STATIC / "images" / "og-card.png"))
    ap.add_argument("--focus", default="center")
    ap.add_argument("--grayscale", type=float, default=0.0)
    ap.add_argument("--name", default="Josué<br>Leiva")
    ap.add_argument("--open", default="<b>Open to:</b> a 320-hour industrial internship, December 2026 to March 2027, in software development, telecom, data centers or IoT. Open to working abroad.")
    ap.add_argument("--location", default="Santiago, Chile // UTFSM")
    ap.add_argument("--handle", default="F0UR13R")
    ap.add_argument("--tagline", default="Backend and systems engineering")
    ap.add_argument("--bio", default="3rd-year Civil Telematics Engineering student at Universidad Técnica Federico Santa María.")
    ap.add_argument("--fact", action="append", metavar="LABEL|VALUE", help="Right-panel row, repeatable (replaces the defaults)")
    ap.add_argument("--badge", default="[ Portfolio ]")
    ap.add_argument("--subtitle",
                    default="Telematics Engineering student. I build edge runtimes for IoT gateways, and the networks and servers they run on.",
                    help="HTML allowed (use <b> for emphasis)")
    ap.add_argument("--keep-html", action="store_true")
    a = ap.parse_args()

    photo = Path(a.photo).expanduser().resolve()
    if not photo.is_file():
        sys.exit(f"Photo not found: {photo}")

    page = (TEMPLATE
            .replace("__FONTS__", (STATIC / "css" / "fonts.css").as_uri())
            .replace("__FOCUS__", html.escape(a.focus))
            .replace("__GRAY__", str(max(0.0, min(1.0, a.grayscale))))
            .replace("__LOCATION__", html.escape(a.location))
            .replace("__NAME__", a.name)
            .replace("__BIO__", html.escape(a.bio))
            .replace("__FACTS__", "".join("<div><dt>%s</dt><dd>%s</dd></div>" % tuple(map(html.escape, f.split("|", 1)))
                                          for f in (a.fact or DEFAULT_FACTS)))
            .replace("__SUBTITLE__", a.subtitle)
            .replace("__OPEN__", a.open)
            .replace("__ECC__", mesh_svg())
            .replace("__HANDLE__", html.escape(a.handle))
            .replace("__TAGLINE__", html.escape(a.tagline))
            .replace("__PHOTO__", photo.as_uri())
            .replace("__BADGE__", html.escape(a.badge)))

    out = Path(a.output).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "og.html"
        src.write_text(page, encoding="utf-8")
        if a.keep_html:
            shutil.copy(src, out.with_suffix(".html"))
        cmd = [find_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
               "--allow-file-access-from-files", "--virtual-time-budget=4000", "--window-size=1200,630",
               f"--screenshot={out}", src.as_uri()]
        res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not out.exists():
        sys.exit(f"Chrome failed:\n{res.stderr}")
    print(f"Wrote {out} ({out.stat().st_size // 1024} KB)")
    print("Next: python djangoPortfolio/manage.py collectstatic --noinput")


if __name__ == "__main__":
    main()
