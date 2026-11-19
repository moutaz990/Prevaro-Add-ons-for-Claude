#!/usr/bin/env python3
"""Render the repository's images: banner, social preview and add-on icons.

Everything is drawn here from simple shapes and text; no third-party artwork and no vendor logo is used.
Output (PNG): assets/banner.png, assets/social-preview.png, assets/icon-gemini-media.png,
              assets/icon-content-studio.png, assets/icon-meeting-assistant.png
The icons are also copied to where the packages read them:
              gemini-media/source/icon.png, content-studio/plugin/.claude-plugin/icon.png,
              meeting-assistant/plugin/.claude-plugin/icon.png

Needs a local Chrome, Chromium or Edge, and the Tajawal font installed (Bold and Regular).
Usage: python3 tools/build_assets.py [--browser PATH]
"""
import argparse, os, shutil, struct, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
INK, INDIGO, VIOLET, MINT, AMBER, PAPER, SLATE = "#0F172A", "#4338CA", "#7C3AED", "#2DD4BF", "#F59E0B", "#F8FAFC", "#94A3B8"

ICON_GEMINI = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<defs><linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{INDIGO}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient></defs>
<rect width="512" height="512" rx="112" fill="url(#a)"/>
<rect x="92" y="112" width="276" height="220" rx="30" fill="none" stroke="{PAPER}" stroke-width="22"/>
<circle cx="164" cy="182" r="24" fill="{AMBER}"/>
<path d="M126 304 L198 236 L250 284 L286 256 L334 304 Z" fill="{PAPER}"/>
<circle cx="356" cy="350" r="92" fill="#5B3FD9"/>
<circle cx="356" cy="350" r="76" fill="{MINT}"/>
<path d="M332 308 L332 392 L402 350 Z" fill="{INK}"/>
</svg>"""

ICON_STUDIO = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0F766E"/><stop offset="1" stop-color="#14B8A6"/></linearGradient></defs>
<rect width="512" height="512" rx="112" fill="url(#b)"/>
<rect x="108" y="96" width="272" height="312" rx="34" fill="{PAPER}"/>
<rect x="136" y="124" width="216" height="124" rx="18" fill="#99F6E4"/>
<circle cx="184" cy="170" r="18" fill="{AMBER}"/>
<path d="M148 236 L214 182 L256 216 L288 194 L340 236 Z" fill="#0F766E"/>
<rect x="136" y="274" width="188" height="26" rx="13" fill="{INK}"/>
<rect x="136" y="318" width="132" height="20" rx="10" fill="{SLATE}"/>
<circle cx="372" cy="388" r="76" fill="#0F766E"/>
<circle cx="372" cy="388" r="60" fill="{AMBER}"/>
<path d="M344 388 L364 408 L402 366" fill="none" stroke="{PAPER}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

ICON_MEETING = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<defs><linearGradient id="c" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#075985"/><stop offset="1" stop-color="#0EA5E9"/></linearGradient></defs>
<rect width="512" height="512" rx="112" fill="url(#c)"/>
<rect x="100" y="124" width="312" height="284" rx="36" fill="{PAPER}"/>
<path d="M100 196 L100 160 Q100 124 136 124 L376 124 Q412 124 412 160 L412 196 Z" fill="{INK}"/>
<rect x="164" y="92" width="26" height="72" rx="13" fill="{AMBER}"/>
<rect x="322" y="92" width="26" height="72" rx="13" fill="{AMBER}"/>
<path d="M144 258 L162 276 L194 240" fill="none" stroke="#0EA5E9" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="222" y="246" width="150" height="22" rx="11" fill="{INK}"/>
<path d="M144 334 L162 352 L194 316" fill="none" stroke="#0EA5E9" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="222" y="322" width="112" height="22" rx="11" fill="{SLATE}"/>
</svg>"""

ICON_SKILLS = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="112" fill="#1E293B"/>
<path d="M256 112 L408 192 L256 272 L104 192 Z" fill="{MINT}"/>
<path d="M104 256 L256 336 L408 256" fill="none" stroke="{PAPER}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M104 320 L256 400 L408 320" fill="none" stroke="{SLATE}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

ICON_CODE = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="112" fill="#1E293B"/>
<path d="M196 168 L108 256 L196 344" fill="none" stroke="{PAPER}" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M316 168 L404 256 L316 344" fill="none" stroke="{PAPER}" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M284 136 L228 376" fill="none" stroke="{AMBER}" stroke-width="30" stroke-linecap="round"/>
</svg>"""

FONT = ("@font-face{font-family:T;src:local('Tajawal Bold'),local('Tajawal-Bold');font-weight:700}"
        "@font-face{font-family:T;src:local('Tajawal Regular'),local('Tajawal-Regular'),local('Tajawal');font-weight:400}")
CHECK = ("<script>document.fonts.ready.then(()=>{const f=[...document.fonts];Promise.allSettled(f.map(x=>x.load())).then(()=>{"
         "document.documentElement.dataset.font=f.length&&f.every(x=>x.status==='loaded')?'ok':'missing'})})</script>")


def icon_page(svg):
    return f"<!doctype html><meta charset=utf-8><style>*{{margin:0}}html,body{{background:transparent}}svg{{display:block;width:512px;height:512px}}</style>{svg}"


def wide_page(width, height, big):
    """Banner (README) and social preview (repository settings) share one layout."""
    tiles = "".join(f'<div class="tile">{svg}<span>{label}</span></div>' for svg, label in (
        (ICON_GEMINI, "Images &amp; Video"), (ICON_STUDIO, "Content Studio"), (ICON_MEETING, "Meetings"), (ICON_SKILLS, "Chat skills"), (ICON_CODE, "Code pack")))
    u = height / 100
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONT}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{width}px;height:{height}px;overflow:hidden}}
body{{font-family:T,sans-serif;color:{PAPER};background:radial-gradient(ellipse at 18% 20%,#1E1B4B 0%,{INK} 58%,#020617 100%);
  display:flex;flex-direction:column;justify-content:center;padding:0 {7 * u}px;gap:{(7 if big else 6) * u}px}}
.top{{display:flex;align-items:center;gap:{3.2 * u}px}}
.mono{{width:{15 * u}px;height:{15 * u}px;border-radius:{3.6 * u}px;background:linear-gradient(135deg,{INDIGO},{VIOLET});
  display:flex;align-items:center;justify-content:center;font-weight:700;font-size:{10.5 * u}px;line-height:1;padding-top:{1.2 * u}px}}
h1{{font-weight:700;font-size:{(11.5 if big else 13) * u}px;line-height:1.05;letter-spacing:-{0.1 * u}px}}
h1 b{{color:{MINT};font-weight:700}}
p{{font-weight:400;font-size:{(4.6 if big else 5.2) * u}px;color:#CBD5E1;margin-top:{1.4 * u}px}}
.tiles{{display:flex;flex-wrap:{"wrap" if big else "nowrap"};gap:{(2.4 if big else 3) * u}px}}
.tile{{flex:{"0 0 auto" if big else "1"};display:flex;align-items:center;gap:{1.8 * u}px;background:rgba(148,163,184,.12);border:1px solid rgba(148,163,184,.25);
  border-radius:{3 * u}px;padding:{1.8 * u}px {2.8 * u}px {1.8 * u}px {1.8 * u}px}}
.tile svg{{width:{(9 if big else 11) * u}px;height:{(9 if big else 11) * u}px;display:block;flex:none}}
.tile span{{font-weight:700;font-size:{(4.2 if big else 4.8) * u}px;white-space:nowrap}}
.ar{{direction:rtl;text-align:right;font-size:{(4.6 if big else 5.2) * u}px;color:#CBD5E1;font-weight:400}}
</style></head><body>
<div class="top"><div class="mono">P</div><div><h1>Prevaro <b>Add-ons</b> for Claude</h1>
<p>Free, reviewed add-ons you install in minutes</p></div></div>
<div class="tiles">{tiles}</div>
<div class="ar">إضافات مجانية ومراجَعة أمنياً، بالعربية والإنجليزية</div>
{CHECK}</body></html>"""


def find_browser(explicit):
    cands = [explicit, os.environ.get("CHROME_PATH")]
    cands += [shutil.which(n) for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge", "microsoft-edge")]
    cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    return next((c for c in cands if c and Path(c).exists()), None)


def render(browser, html, png, width, height, scale=1, transparent=False, need_font=False):
    flags = ["--headless=new", "--disable-gpu", "--hide-scrollbars"]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        flags.append("--no-sandbox")  # Chromium refuses to start as root with its sandbox on
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(html, encoding="utf-8")
        if need_font:
            dom = subprocess.run([browser, *flags, "--virtual-time-budget=4000", f"--window-size={width},{height}", "--dump-dom",
                                  page.as_uri()], check=True, capture_output=True).stdout.decode("utf-8", "replace")
            if 'data-font="ok"' not in dom:
                raise SystemExit("ERROR: the Tajawal font (Regular and Bold) is not installed; the images would use a fallback font.")
        subprocess.run([browser, *flags, "--run-all-compositor-stages-before-draw", "--virtual-time-budget=4000",
                        f"--force-device-scale-factor={scale}", f"--window-size={width},{height}",
                        *(["--default-background-color=00000000"] if transparent else []),
                        f"--screenshot={png}", page.as_uri()], check=True, capture_output=True)
    with open(png, "rb") as f:
        head = f.read(24)
    got = struct.unpack(">II", head[16:24])
    if got != (width * scale, height * scale):
        raise SystemExit(f"ERROR: {png.name} is {got}, expected {(width * scale, height * scale)}")
    print(f"{png.relative_to(ROOT)}  {got[0]}x{got[1]}  {png.stat().st_size // 1024} KB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--browser", help="Chrome/Chromium/Edge path (else auto-detect or CHROME_PATH)")
    a = ap.parse_args()
    browser = find_browser(a.browser)
    if not browser:
        raise SystemExit("ERROR: no Chrome/Chromium/Edge found; pass --browser.")
    OUT.mkdir(exist_ok=True)
    render(browser, icon_page(ICON_GEMINI), OUT / "icon-gemini-media.png", 512, 512, transparent=True)
    render(browser, icon_page(ICON_STUDIO), OUT / "icon-content-studio.png", 512, 512, transparent=True)
    render(browser, icon_page(ICON_MEETING), OUT / "icon-meeting-assistant.png", 512, 512, transparent=True)
    render(browser, wide_page(1100, 360, big=False), OUT / "banner.png", 1100, 360, scale=2, need_font=True)
    render(browser, wide_page(1280, 640, big=True), OUT / "social-preview.png", 1280, 640, need_font=True)
    shutil.copyfile(OUT / "icon-gemini-media.png", ROOT / "gemini-media" / "source" / "icon.png")
    shutil.copyfile(OUT / "icon-content-studio.png", ROOT / "content-studio" / "plugin" / ".claude-plugin" / "icon.png")
    shutil.copyfile(OUT / "icon-meeting-assistant.png", ROOT / "meeting-assistant" / "plugin" / ".claude-plugin" / "icon.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
