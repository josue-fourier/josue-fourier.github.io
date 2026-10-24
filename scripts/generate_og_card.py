#!/usr/bin/env python3
"""Generate the 1200x630 social share card (og-card.png) with headless Chrome.

Usage (from the repo root):
    python scripts/generate_og_card.py
    python scripts/generate_og_card.py --photo path/to/new_photo.jpg
    python scripts/generate_og_card.py --photo me.png --focus "50% 20%" --grayscale 0

Options:
    --photo      Portrait to use (default: static/portfolio/images/profile.jpg)
    --output     Output PNG (default: static/portfolio/images/og-card.png)
    --focus      CSS object-position for cropping the square portrait (default "center")
    --grayscale  0.0 (full colour) .. 1.0 (black & white); default 0.85
    --name / --subtitle / --tagline / --badge   Override texts
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
body{width:1200px;height:630px;background:#050506;color:#fff;font-family:'Space Grotesk';position:relative;overflow:hidden}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:60px 60px}
.glow{position:absolute;right:-120px;top:-140px;width:620px;height:620px;background:radial-gradient(circle,rgba(16,185,129,.38),transparent 65%)}
.glow2{position:absolute;left:-200px;bottom:-260px;width:620px;height:620px;background:radial-gradient(circle,rgba(6,182,212,.2),transparent 65%)}
.frame{position:absolute;inset:36px;border:1px solid rgba(255,255,255,.14)}
.mono{font-family:'JetBrains Mono';letter-spacing:.18em;text-transform:uppercase}
.tag{position:absolute;left:84px;top:78px;font-size:17px;color:#a1a1aa;display:flex;gap:14px;align-items:center}
.dot{width:10px;height:10px;background:#10B981;box-shadow:0 0 14px #10B981}
h1{position:absolute;left:80px;top:122px;font-size:120px;line-height:.9;letter-spacing:-.045em;text-transform:uppercase;font-weight:700}
h1 span{color:#10B981}
.sub{position:absolute;left:84px;top:364px;width:600px;font-size:23px;font-weight:300;font-family:Inter;color:#d4d4d8;line-height:1.35}
.open{position:absolute;left:84px;top:470px;width:600px;border-left:2px solid #10B981;padding-left:14px;font-size:17px;font-family:Inter;color:#d4d4d8;line-height:1.4}
.open b{color:#fff;font-weight:600}
svg.ecc{position:absolute;left:0;top:0;width:760px;height:630px}
.foot{position:absolute;left:84px;bottom:64px;font-size:16px;color:#71717a;display:flex;gap:18px}
.foot em{font-style:normal;color:#10B981}
.ph{position:absolute;right:92px;top:128px;width:360px;height:360px;border:1px solid rgba(255,255,255,.25)}
.ph img{width:100%;height:100%;object-fit:cover;object-position:__FOCUS__;filter:grayscale(__GRAY__) contrast(1.1)}
.ph::before,.ph::after{content:"";position:absolute;width:22px;height:22px;border:2px solid #10B981;z-index:2}
.ph::before{top:-8px;left:-8px;border-right:0;border-bottom:0}.ph::after{bottom:-8px;right:-8px;border-left:0;border-top:0}
.badge{position:absolute;right:92px;top:500px;width:360px;font-size:16px;color:#10B981;text-align:right}
</style></head><body><div class="grid"></div><div class="glow"></div><div class="glow2"></div><div class="frame"></div>
<div class="tag mono"><span class="dot"></span>__LOCATION__</div>
<h1>__NAME__<span>.</span></h1>
__ECC__
<div class="sub">__SUBTITLE__</div>
<div class="open">__OPEN__</div>
<div class="foot mono"><em>__HANDLE__</em><span>//</span><span>__TAGLINE__</span></div>
<div class="ph"><img src="__PHOTO__"></div>
<div class="badge mono">__BADGE__</div>
</body></html>
"""


def mesh_svg():
    """Static version of the home hero mesh (same layout as hero-network.js): nodes, links, one packet chain."""
    N = [(.1, .86), (.44, .7), (.8, .8), (.08, .5), (.3, .42), (.6, .5), (.9, .55), (.2, .15),
         (.5, .2), (.75, .12), (.95, .3), (.36, .92), (.62, .94)]
    E = {(0, 1), (1, 2)}
    for i, n in enumerate(N):
        for j in sorted(range(len(N)), key=lambda j: (n[0] - N[j][0]) ** 2 + (n[1] - N[j][1]) ** 2)[1:3]:
            E.add((min(i, j), max(i, j)))
    xy = lambda n: (40 + n[0] * 680, 40 + n[1] * 550)
    line = lambda a, b, col, w: '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"/>' % (*xy(N[a]), *xy(N[b]), col, w)
    links = "".join(line(a, b, "rgba(255,255,255,.07)", 1) for a, b in sorted(E))
    chain = line(0, 1, "rgba(16,185,129,.5)", 1.5) + line(1, 2, "rgba(16,185,129,.5)", 1.5)
    dots = "".join('<circle cx="%.1f" cy="%.1f" r="%d" fill="rgba(255,255,255,.22)"/>' % (*xy(n), 3 if k < 3 else 2) for k, n in enumerate(N))
    rings = "".join('<circle cx="%.1f" cy="%.1f" r="6" fill="none" stroke="rgba(16,185,129,.5)"/>' % xy(N[k]) for k in (0, 2))
    return '<svg class="ecc" viewBox="0 0 760 630">%s%s%s%s</svg>' % (links, chain, dots, rings)


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
    ap.add_argument("--grayscale", type=float, default=0.85)
    ap.add_argument("--name", default="Josué<br>Leiva")
    ap.add_argument("--open", default="<b>Open to:</b> a 320-hour industrial internship, Dec 2026 to Mar 2027, in telecom, data centers or IoT. Open to working abroad.")
    ap.add_argument("--location", default="Santiago, Chile // UTFSM")
    ap.add_argument("--handle", default="F0UR13R")
    ap.add_argument("--tagline", default="Backend and systems engineering")
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
