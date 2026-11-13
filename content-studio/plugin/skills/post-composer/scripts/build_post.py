#!/usr/bin/env python3
"""Compose a ready-to-post image: picture + headline + your official logo, in your brand colours and font.

The picture (an AI-generated image or a real photo) never contains text or a logo. This script adds them
from the brand profile (brand.json): the logo file as it is, the brand font, the brand colours, and the
platform sizes as exact pixels.

Example:
  python build_post.py --brand content-studio/brand.json --headline "Where does the first camera go?" \
      --sub "Three things to check on site" --image picture.jpg --layout photo --sizes square,story --out deliver

The run stops (non-zero exit, nothing delivered) when: the brand font did not really load, a character is not
drawn by that font, the text does not fit at the smallest allowed size, a banned word is in the text, the
colours do not give readable contrast, or an output has the wrong size.
Deps: none beyond Python 3, plus a local Chrome, Chromium or Edge.
"""
import argparse
import datetime
import html as htmlmod
import json
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

SIZES = {  # name -> (width, height, safe top, safe bottom) in pixels
    "square": (1080, 1080, 0, 0),
    "portrait": (1080, 1350, 0, 0),
    "story": (1080, 1920, 250, 340),
    "landscape": (1920, 1080, 0, 0),
}
LAYOUTS = ("photo", "split", "card")
RTL_LANGS = ("ar", "fa", "ur", "he")
MIN_LOGO_PX = 240
IMAGE_MAGIC = ((b"\xff\xd8\xff", "jpeg"), (b"\x89PNG\r\n\x1a\n", "png"))
PLACEHOLDERS = ("[يُتحقق", "[TODO", "[TBC", "[verify")
TAG_TEXT = {"ar": "صورة توضيحية", "en": "Illustrative image"}


# ---------- colours ----------
def rgb(value, where):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        raise SystemExit(f"ERROR: {where} must be a colour like #12355B, got {value!r}")
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def hexc(c):
    return "#%02X%02X%02X" % c


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rgba(c, alpha):
    return f"rgba({c[0]},{c[1]},{c[2]},{alpha})"


def contrast(a, b):
    """WCAG contrast ratio between two colours."""
    def lum(c):
        ch = [(v / 255) for v in c]
        ch = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in ch]
        return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# ---------- files ----------
def image_kind(path):
    with open(path, "rb") as f:
        head = f.read(256)
    kind = next((k for magic, k in IMAGE_MAGIC if head.startswith(magic)), None)
    if not kind and head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        kind = "webp"
    if not kind and re.match(rb"\s*(<\?xml[^>]*>\s*)?(<!--.*?-->\s*)*<svg[\s>]", head, re.S):
        kind = "svg"
    return kind


def check_image(path, what="image", allow_svg=False):
    p = Path(path)
    if not p.is_file():
        raise SystemExit(f"ERROR: {what} not found: {p}")
    kind = image_kind(p)
    if not kind or (kind == "svg" and not allow_svg):
        raise SystemExit(f"ERROR: {p.name} is not a JPEG, PNG or WebP image" + (" or an SVG" if allow_svg else ""))
    return p.resolve()


def find_brand(explicit):
    cands = [explicit] if explicit else ["content-studio/brand.json", "brand.json"]
    for c in cands:
        if c and Path(c).is_file():
            return Path(c).resolve()
    raise SystemExit("ERROR: brand profile not found (" + ", ".join(str(c) for c in cands) + "). "
                     "Create it with the brand-setup skill, or pass --brand.")


def load_brand(path, lang):
    """Reads and validates brand.json. File paths in it are relative to its own folder."""
    try:
        b = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"ERROR: {path.name} is not valid JSON: {e}")
    base = path.parent
    name = b.get("name")
    if not isinstance(name, str) or not name.strip() or name.strip().startswith("["):
        raise SystemExit(f"ERROR: {path.name}: 'name' is missing or still a placeholder")
    col = b.get("colors") or {}
    bg = rgb(col.get("background"), "colors.background")
    text = rgb(col.get("text"), "colors.text")
    accent = rgb(col.get("accent"), "colors.accent")
    dark = rgb(col["background_dark"], "colors.background_dark") if col.get("background_dark") else mix(bg, (0, 0, 0), 0.28)
    light = rgb(col["background_light"], "colors.background_light") if col.get("background_light") else mix(bg, (255, 255, 255), 0.12)
    muted = rgb(col["muted"], "colors.muted") if col.get("muted") else mix(text, bg, 0.18)
    if contrast(text, bg) < 4.5:
        raise SystemExit(f"ERROR: colors.text on colors.background has a contrast of {contrast(text, bg):.1f}; "
                         "the headline would be hard to read (4.5 or more is needed)")
    if contrast(accent, bg) < 3:
        raise SystemExit(f"ERROR: colors.accent on colors.background has a contrast of {contrast(accent, bg):.1f}; "
                         "3 or more is needed")

    logo = b.get("logo") or {}
    logo_file = logo.get(lang) or logo.get("default")
    if not logo_file:
        raise SystemExit(f"ERROR: {path.name}: logo.default is missing (the logo version that reads well on your background colour)")
    logo_path = check_image(base / logo_file, "logo", allow_svg=True)
    mark_path = check_image(base / logo["mark"], "logo mark", allow_svg=True) if logo.get("mark") else None

    font = b.get("font") or {}
    family = font.get("family")
    if not isinstance(family, str) or not re.fullmatch(r"[A-Za-z0-9 _-]{1,60}", family):
        raise SystemExit(f"ERROR: {path.name}: font.family must be a font name (letters, digits, spaces)")
    files = {}
    for weight, rel in (font.get("files") or {}).items():
        if weight not in ("400", "500", "700"):
            raise SystemExit(f"ERROR: {path.name}: font.files keys must be 400, 500 or 700")
        fp = base / rel
        if not fp.is_file():
            raise SystemExit(f"ERROR: font file not found: {fp}")
        files[weight] = fp.resolve()
    if files and not {"400", "700"} <= set(files):
        raise SystemExit(f"ERROR: {path.name}: font.files needs at least 400 and 700")

    banned = b.get("banned_words") or []
    if not all(isinstance(w, str) for w in banned):
        raise SystemExit(f"ERROR: {path.name}: banned_words must be a list of words")
    tag = (b.get("illustrative_tag") or {}).get(lang) or TAG_TEXT.get(lang) or TAG_TEXT["en"]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:24] or "brand"
    return dict(name=name.strip(), slug=slug, bg=bg, text=text, accent=accent, dark=dark, light=light, muted=muted,
                logo=logo_path, mark=mark_path, family=family, font_files=files, banned=[w for w in banned if w.strip()],
                tag=tag)


def font_css(brand):
    if brand["font_files"]:
        files = dict(brand["font_files"])
        files.setdefault("500", files["400"])
        return "".join(f'@font-face{{font-family:BrandFont;src:url("{files[w].as_uri()}");font-weight:{w}}}'
                       for w in ("400", "500", "700"))
    # local() matches one face by its full or PostScript name, not a family: local('Tajawal') is the regular
    # face only, and declaring it as weight 700 would draw the headline in regular with no warning.
    fam, ps = brand["family"], brand["family"].replace(" ", "")
    faces = ((400, f"local('{fam} Regular'),local('{ps}-Regular'),local('{fam}')"),
             (500, f"local('{fam} Medium'),local('{ps}-Medium')"),
             (700, f"local('{fam} Bold'),local('{ps}-Bold')"))
    return "".join(f"@font-face{{font-family:BrandFont;src:{src};font-weight:{w}}}" for w, src in faces)


# ---------- browser ----------
def find_browser(explicit=None):
    cands = [explicit, os.environ.get("CHROME_PATH")]
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
                 "chrome", "msedge", "microsoft-edge"):
        cands.append(shutil.which(name))
    system = platform.system()
    if system == "Darwin":
        cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Chromium.app/Contents/MacOS/Chromium",
                  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    elif system == "Windows":
        for base in (os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"),
                     os.environ.get("LOCALAPPDATA")):
            if base:
                cands += [str(Path(base) / "Google/Chrome/Application/chrome.exe"),
                          str(Path(base) / "Microsoft/Edge/Application/msedge.exe")]
    for c in cands:
        if c and Path(c).exists():
            return c
    return None


def base_flags():
    """Chromium refuses to start as root with its sandbox on (containers, CI). Only then is it turned off."""
    root = hasattr(os, "geteuid") and os.geteuid() == 0
    return ["--headless=new", "--disable-gpu", "--hide-scrollbars"] + (["--no-sandbox"] if root else [])


def chrome_png(browser, html_path, png_path, width, height):
    subprocess.run([browser, *base_flags(),
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=4000",
                    "--force-device-scale-factor=1", f"--window-size={width},{height}",
                    f"--screenshot={Path(png_path).resolve()}", Path(html_path).resolve().as_uri()],
                   check=True, capture_output=True)


def chrome_dom(browser, html_path, width, height):
    """Runs the page (fonts + fitting script) and returns the resulting DOM, to read the checks from it."""
    out = subprocess.run([browser, *base_flags(), "--virtual-time-budget=4000", f"--window-size={width},{height}", "--dump-dom",
                          Path(html_path).resolve().as_uri()], check=True, capture_output=True)
    return out.stdout.decode("utf-8", "replace")


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"ERROR: {path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def check_text(brand, *texts):
    joined = " ".join(t for t in texts if t)
    hits = [w for w in brand["banned"] if w.lower() in joined.lower()]
    if hits:
        raise SystemExit("ERROR: banned word or claim in the text (from brand.json): " + ", ".join(hits))
    left = [p for p in PLACEHOLDERS if p.lower() in joined.lower()]
    if left:
        raise SystemExit(f"ERROR: the text still contains a placeholder ({left[0]}...]); confirm it with the owner first.")


def page(spec):
    """Returns the HTML for one size. Everything dynamic is escaped; files are referenced by file URI."""
    W, H, top, bottom = spec["W"], spec["H"], spec["top"], spec["bottom"]
    b = spec["brand"]
    BG, DARK, LIGHT = hexc(b["bg"]), hexc(b["dark"]), hexc(b["light"])
    TEXT, ACCENT, MUTED = hexc(b["text"]), hexc(b["accent"]), hexc(b["muted"])
    u = min(W, H) / 100.0                      # layout unit: 1% of the short side
    rtl = spec["rtl"]
    layout = spec["layout"]
    wide = W > H * 1.2
    pad = round(6.2 * u)
    esc = htmlmod.escape
    img = f'<img class="pic" src="{esc(spec["image"].as_uri())}" alt="">' if spec["image"] else ""
    logo_w = max(MIN_LOGO_PX, round((30 if wide else 36) * u))
    logo_h = round(logo_w * 0.42)              # box for the logo; it is fitted inside, never stretched
    start = "right" if rtl else "left"
    end = "left" if rtl else "right"
    logo = (f'<img class="logoimg" src="{esc(b["logo"].as_uri())}" alt="" style="width:{logo_w}px;height:{logo_h}px;'
            f'object-fit:contain;object-position:{start} center;display:block">')
    label = f'<div class="label">{esc(spec["label"])}</div>' if spec["label"] else ""
    sub = f'<div class="sub">{esc(spec["sub"])}</div>' if spec["sub"] else ""
    tag = f'<div class="tag">{esc(b["tag"])}</div>' if spec["image"] and spec["illustrative"] else ""

    hmax = {"photo": 8.6, "split": 7.4, "card": 10.0}[layout] * u * (0.92 if wide else 1)
    hmin = 4.4 * u
    grad = f"{LIGHT} 0%,{BG} 60%,{DARK} 100%"
    # Geometry per layout. `panel` is the box the text must fit in.
    if layout == "card":
        geo = f".panel{{inset:{top + pad}px {pad}px {bottom + pad}px {pad}px;justify-content:center}}"
        bg = f"background:radial-gradient(ellipse at 30% 25%,{LIGHT} 0%,{BG} 55%,{DARK} 100%)"
    elif layout == "split":
        if wide:
            geo = (f".pic{{{end}:0;top:0;width:52%;height:100%}}"
                   f".panel{{{start}:0;top:0;width:48%;height:100%;padding:{pad}px;justify-content:center;"
                   f"background:linear-gradient(160deg,{grad})}}")
        else:
            ph = round(H * 0.50)
            geo = (f".pic{{left:0;top:0;width:100%;height:{ph}px}}"
                   f".panel{{left:0;top:{ph}px;width:100%;height:{H - ph}px;padding:{round(pad * .8)}px {pad}px "
                   f"{bottom + round(pad * .8)}px;justify-content:center;"
                   f"background:linear-gradient(170deg,{grad})}}")
        bg = f"background:{DARK}"
    else:  # photo: full-bleed picture, text over a scrim in the brand background colour
        d = b["dark"]
        if wide:
            geo = (".pic{inset:0;width:100%;height:100%}"
                   f".scrim{{inset:0;background:linear-gradient(to {start},"
                   f"{rgba(d, 0)} 30%,{rgba(d, .80)} 62%,{rgba(d, .94)} 100%)}}"
                   f".panel{{{start}:0;top:0;width:46%;height:100%;padding:{pad}px;justify-content:center}}")
        else:
            geo = (".pic{inset:0;width:100%;height:100%}"
                   f".scrim{{inset:0;background:linear-gradient(to bottom,{rgba(d, .55)} 0%,{rgba(d, 0)} 22%,"
                   f"{rgba(d, 0)} 38%,{rgba(d, .82)} 66%,{rgba(d, .95)} 100%)}}"
                   f".panel{{left:0;right:0;bottom:0;height:{round(H * 0.56)}px;padding:{pad}px {pad}px "
                   f"{bottom + pad}px;justify-content:flex-end}}")
        bg = f"background:{DARK}"

    # The logo sits inside the panel for split/card, and at the top start corner for photo.
    logo_css = (f".logo{{position:absolute;top:{top + pad}px;{start}:{pad}px}}" if layout == "photo"
                else f".logo{{margin-top:{round(5 * u)}px}}")
    orn = ""
    if layout == "card" and b["mark"]:
        orn = f'<img class="orn" src="{esc(b["mark"].as_uri())}" alt="">'
    tag_css = (f".tag{{position:absolute;{end}:{pad}px;"
               + (f"top:{top + pad}px" if layout != "split" or wide else f"top:{round(H * 0.50) - round(6.5 * u)}px")
               + f";font:500 {round(2.1 * u)}px/1 BrandFont;color:{TEXT};background:{rgba(b['dark'], .55)};"
               f"padding:{round(1.1 * u)}px {round(1.8 * u)}px;border-radius:{round(3 * u)}px}}")
    return f"""<!doctype html><html lang="{esc(spec['lang'])}" dir="{'rtl' if rtl else 'ltr'}"><head><meta charset="utf-8">
<style>{spec['fonts']}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;{bg}}}
body{{position:relative;font-family:BrandFont,sans-serif;color:{TEXT};text-align:{start}}}
.pic,.scrim,.panel,.orn{{position:absolute}}.pic{{object-fit:cover;display:block}}
.panel{{display:flex;flex-direction:column;overflow:hidden}}.inner{{flex:none;width:100%}}
.label{{font:500 {round(2.7 * u)}px/1.3 BrandFont;color:{ACCENT};margin-bottom:{round(1.6 * u)}px}}
.rule{{width:{round(9 * u)}px;height:{max(4, round(.55 * u))}px;background:{ACCENT};margin-bottom:{round(3 * u)}px;flex:none}}
.h{{font-weight:700;font-size:{hmax:.2f}px;line-height:1.32;text-wrap:balance}}
.sub{{font:400 {round(3.5 * u)}px/1.6 BrandFont;color:{MUTED};margin-top:{round(2.4 * u)}px;text-wrap:balance}}
.orn{{{end}:-{round(14 * u)}px;bottom:-{round(18 * u)}px;width:{round(78 * u)}px;height:auto;opacity:.045}}
{geo}{logo_css}{tag_css}
</style></head><body>
{img}{'<div class="scrim"></div>' if layout == 'photo' else ''}{orn}
<div class="panel" id="panel"><div class="inner" id="inner">{label}<div class="rule"></div><div class="h" id="h">{esc(spec['headline'])}</div>{sub}
{'' if layout == 'photo' else f'<div class="logo">{logo}</div>'}</div></div>
{f'<div class="logo">{logo}</div>' if layout == 'photo' else ''}{tag}
<script>
(async () => {{
  const root = document.documentElement, h = document.getElementById('h'), panel = document.getElementById('panel');
  const inner = document.getElementById('inner'), cs = getComputedStyle(panel);
  // Measured on the content block itself: with bottom-aligned text, overflow goes upward and scrollHeight misses it.
  const room = () => panel.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
  const faces = [...document.fonts];
  await Promise.allSettled(faces.map(f => f.load()));
  const loaded = w => faces.some(f => f.family.replace(/["']/g, '') === 'BrandFont' && String(f.weight) === String(w) && f.status === 'loaded');
  root.dataset.font = loaded(700) && loaded(400) ? 'ok' : 'missing';
  // A loaded font can still lack a glyph (an Arabic-only file and a Latin word): the browser then falls back
  // silently. Two tests per character:
  //  1. width: a character drawn by the brand font is equally wide whatever the fallback is; one that falls back is not.
  //  2. pixels: for characters whose fallback is the same font either way (emoji, symbols), drawing with
  //     "BrandFont, serif" gives the very same pixels as drawing with "serif" alone.
  // Test 2 is skipped for a script when the system's own serif fallback for it is the brand font itself.
  const cv = document.createElement('canvas'); cv.width = cv.height = 160;
  const ctx = cv.getContext('2d', {{ willReadFrequently: true }});
  const width = (ch, weight, fallback) => {{ ctx.font = weight + ' 100px BrandFont, ' + fallback; return ctx.measureText(ch).width; }};
  const draw = (ch, weight, family) => {{
    ctx.clearRect(0, 0, 160, 160); ctx.font = weight + ' 80px ' + family;
    // Alphabetic baseline: 'middle' is computed from the first family's metrics and would shift the same glyph.
    ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillText(ch, 80, 110);
    return ctx.getImageData(0, 0, 160, 160).data;
  }};
  const blank = a => {{ for (let i = 3; i < a.length; i += 4) if (a[i]) return false; return true; }};
  const same = (a, b) => {{ for (let i = 3; i < a.length; i += 4) if (a[i] !== b[i]) return false; return true; }};
  const fellBack = (ch, weight) => {{ const a = draw(ch, weight, 'BrandFont, serif'); return !blank(a) && same(a, draw(ch, weight, 'serif')); }};
  const arabic = /[\\u0600-\\u06FF\\u0750-\\u077F\\u08A0-\\u08FF\\uFB50-\\uFDFF\\uFE70-\\uFEFF]/;
  const missing = new Set();
  document.querySelectorAll('.label, .h, .sub, .tag').forEach(el => {{
    const weight = getComputedStyle(el).fontWeight;
    const arabicTestable = !fellBack('\\u0628', weight), latinTestable = !fellBack('a', weight);
    for (const ch of new Set(el.textContent)) {{
      if (!ch.trim()) continue;
      const testable = arabic.test(ch) ? arabicTestable : (/[A-Za-z0-9]/.test(ch) ? latinTestable : true);
      if (width(ch, weight, 'monospace') !== width(ch, weight, 'serif')) missing.add(ch);
      else if (testable && fellBack(ch, weight)) missing.add(ch);
    }}
  }});
  root.dataset.glyphs = missing.size ? [...missing].join(' ') : 'ok';
  let size = {hmax:.2f};
  const fits = () => inner.getBoundingClientRect().height <= room() + 1 && h.scrollWidth <= h.clientWidth + 1;
  while (!fits() && size > {hmin:.2f}) {{ size -= 1; h.style.fontSize = size + 'px'; }}
  root.dataset.fit = fits() ? 'ok' : 'overflow';
  root.dataset.hsize = String(Math.round(size));
  // Wait for the pictures: with an installed font nothing above takes time, and the check would run too early.
  const pics = [...document.querySelectorAll('.pic, .logoimg, .orn')];
  await Promise.all(pics.filter(i => !i.complete).map(i => new Promise(done => {{ i.onload = i.onerror = done; }})));
  const ok = i => i.complete && i.naturalWidth > 0;
  const pic = document.querySelector('.pic');
  root.dataset.pic = !pic ? 'none' : (ok(pic) ? 'ok' : 'broken');
  root.dataset.logo = pics.filter(i => !i.classList.contains('pic')).every(ok) ? 'ok' : 'broken';
}})();
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--headline", required=True, help="the headline, in the post's language")
    ap.add_argument("--sub", default="", help="optional second line")
    ap.add_argument("--label", default="", help="optional small line above the headline (e.g. the pillar name)")
    ap.add_argument("--image", help="picture without text or logo (JPEG/PNG/WebP). Omit for a brand card")
    ap.add_argument("--layout", choices=LAYOUTS, help="photo | split | card (default: photo with --image, else card)")
    ap.add_argument("--sizes", default="square", help="comma list of: " + ", ".join(SIZES) + " (default: square)")
    ap.add_argument("--lang", help="text language code, e.g. ar or en (default: 'language' in brand.json, else en). "
                                   "Right-to-left for: " + ", ".join(RTL_LANGS))
    ap.add_argument("--real-photo", action="store_true",
                    help="the picture is a real photo with confirmed rights: do not add the 'illustrative image' tag")
    ap.add_argument("--slug", default="post", help="short ASCII name used in the file names")
    ap.add_argument("--out", default="deliver", help="output folder (default ./deliver)")
    ap.add_argument("--brand", help="brand.json (default: content-studio/brand.json, then ./brand.json)")
    ap.add_argument("--browser", help="Chrome/Chromium/Edge path (else auto-detect or CHROME_PATH)")
    a = ap.parse_args()

    brand_path = find_brand(a.brand)
    lang = a.lang
    if not lang:
        try:
            lang = json.loads(brand_path.read_text(encoding="utf-8")).get("language") or "en"
        except json.JSONDecodeError:
            lang = "en"
    if not re.fullmatch(r"[a-z]{2,3}", lang):
        raise SystemExit("ERROR: --lang must be a language code such as ar or en")
    brand = load_brand(brand_path, lang)
    check_text(brand, a.headline, a.sub, a.label)
    image = check_image(a.image) if a.image else None
    layout = a.layout or ("photo" if image else "card")
    if layout in ("photo", "split") and not image:
        raise SystemExit(f"ERROR: layout {layout} needs --image")
    sizes = [s.strip() for s in a.sizes.split(",") if s.strip()]
    unknown = [s for s in sizes if s not in SIZES]
    if unknown or not sizes:
        raise SystemExit("ERROR: unknown size: " + ", ".join(unknown or ["(none)"]) + ". Use: " + ", ".join(SIZES))
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", a.slug):
        raise SystemExit("ERROR: --slug must be lowercase letters, digits and hyphens")
    browser = find_browser(a.browser)
    if not browser:
        raise SystemExit("ERROR: no Chrome/Chromium/Edge found; install one or pass --browser.")

    fonts = font_css(brand)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    results, problems = [], []
    for name in sizes:
        W, H, top, bottom = SIZES[name]
        spec = dict(W=W, H=H, top=top, bottom=bottom, lang=lang, rtl=lang in RTL_LANGS, layout=layout, image=image,
                    brand=brand, fonts=fonts, headline=a.headline.strip(), sub=a.sub.strip(), label=a.label.strip(),
                    illustrative=not a.real_photo)
        work = out / f"_{a.slug}_{name}.html"
        work.write_text(page(spec), encoding="utf-8")
        png = out / f"{brand['slug']}_post_{a.slug}_{name}_{stamp}.png"
        try:
            dom = chrome_dom(browser, work, W, H)
            checks = {k: (re.search(rf'data-{k}="([^"]*)"', dom) or [None, "unknown"])[1]
                      for k in ("font", "glyphs", "fit", "hsize", "pic", "logo")}
            if checks["font"] != "ok":
                problems.append(f"{name}: the font '{brand['family']}' did not load (install it, or set font.files in brand.json)")
            elif checks["glyphs"] != "ok":
                problems.append(f"{name}: the font '{brand['family']}' cannot draw: {htmlmod.unescape(checks['glyphs'])} "
                                "(use a font file that covers these characters, or remove them)")
            if checks["fit"] != "ok":
                problems.append(f"{name}: the text does not fit even at the smallest size; shorten the headline or the second line")
            if checks["pic"] == "broken":
                problems.append(f"{name}: the picture could not be loaded")
            if checks["logo"] != "ok":
                problems.append(f"{name}: the logo file could not be loaded")
            if not any(p.startswith(name + ":") for p in problems):
                chrome_png(browser, work, png, W, H)
                if png_size(png) != (W, H):
                    problems.append(f"{name}: output is {png_size(png)}, expected {(W, H)}")
                    png.unlink()
                else:
                    results.append({"size": name, "width": W, "height": H, "file": str(png), "headline_px": int(checks["hsize"])})
        finally:
            work.unlink(missing_ok=True)

    if problems:
        for r in results:  # deliver all sizes or none
            Path(r["file"]).unlink(missing_ok=True)
        raise SystemExit("ERROR: nothing delivered.\n- " + "\n- ".join(problems))
    manifest = {"brand": brand["name"], "headline": a.headline.strip(), "sub": a.sub.strip(), "label": a.label.strip(),
                "lang": lang, "layout": layout, "image": str(image) if image else None,
                "illustrative_tag": bool(image) and not a.real_photo,
                "font": f"{brand['family']} (verified loaded; every character drawn by it)",
                "logo": brand["logo"].name, "outputs": results, "status": "DRAFT - not published; needs the owner's approval"}
    (out / f"{brand['slug']}_post_{a.slug}_{stamp}.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in results:
        print(f"{r['size']:10} {r['width']}x{r['height']}  headline {r['headline_px']}px  {r['file']}")
    print("DRAFT: not published. Needs the owner's approval.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
