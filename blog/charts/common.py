"""Shared style + SVG helpers + headless-Chrome renderer for the blog figures.

Edit the palette or the type scale here and every figure follows.

The figures are bilingual: every string lives in a {"es": ..., "en": ...} dict at
the top of the figure script and is resolved through `pick()` at draw time. The
active language comes from the FIG_LANG env var (default "es") or `set_lang()`.

    python blog/charts/fig1.py             # spanish  -> blog/
    FIG_LANG=en python blog/charts/fig1.py # english  -> blog/en/
"""

import html
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BLOG = HERE.parent
DATA = HERE / "data.json"

LANGS = ("es", "en")
LANG = os.environ.get("FIG_LANG", "es")


def set_lang(lang):
    """Switch the active language (used by make_all.py to build both in one run)."""
    global LANG
    if lang not in LANGS:
        sys.exit(f"unknown language {lang!r}; expected one of {LANGS}")
    LANG = lang


def pick(value):
    """Resolve a {"es": ..., "en": ...} dict against the active language."""
    return value[LANG] if isinstance(value, dict) and set(value) == set(LANGS) else value


def out_dir():
    """Spanish figures sit next to the draft; English ones in blog/en/."""
    d = BLOG if LANG == "es" else BLOG / LANG
    d.mkdir(exist_ok=True)
    return d


def num(v, dec=1):
    """Format a number with the decimal mark the active language uses."""
    s = f"{v:.{dec}f}"
    return s.replace(".", ",") if LANG == "es" else s


def pct(v, dec=0):
    """Spanish puts a space before the percent sign; English does not."""
    return f"{num(v, dec)} %" if LANG == "es" else f"{num(v, dec)}%"


# --- palette -----------------------------------------------------------------
# Two steps of one blue ramp (light = "considered", dark = "did") plus an orange
# used only for reference marks. Checked for contrast and colour-vision
# separation before use; if you swap these, re-check them.
SURF   = "#fcfcfb"   # page/chart background
INK    = "#0b0b0b"   # titles, model names
INK2   = "#52514e"   # values, secondary labels
MUTED  = "#8a8983"   # subtitles, footnotes, axis ticks
LIGHT  = "#6da7ec"   # series 1 -- "considered"
DARK   = "#104281"   # series 2 -- "did"
ACCENT = "#eb6834"   # reference line only (never a data series)
GRID   = "#e6e5e1"
RULE   = "#dedcd6"

# --- type --------------------------------------------------------------------
FONT = '"Lato","Noto Sans",system-ui,sans-serif'
SIZE_TITLE, SIZE_SUB, SIZE_NOTE = 25, 14.5, 12.5

CSS = f"""
*{{box-sizing:border-box}}
body{{margin:0;background:{SURF};font-family:{FONT};
     -webkit-font-smoothing:antialiased;color:{INK}}}
.wrap{{padding:34px 38px 30px}}
h1{{font-size:{SIZE_TITLE}px;line-height:1.22;margin:0 0 9px;font-weight:700;letter-spacing:-.015em}}
p.sub{{font-size:{SIZE_SUB}px;line-height:1.45;margin:0 0 22px;color:{MUTED};max-width:900px}}
p.note{{font-size:{SIZE_NOTE}px;line-height:1.45;margin:16px 0 0;color:{MUTED}}}
.legend{{display:flex;gap:22px;align-items:center;margin:0 0 14px;font-size:14px;color:{INK2}}}
.legend span{{display:inline-flex;align-items:center;gap:8px}}
.dot{{width:13px;height:13px;border-radius:50%;display:inline-block}}
.bar{{width:15px;height:11px;border-radius:3px;display:inline-block}}
svg{{display:block;overflow:visible}}
"""


def esc(s):
    return html.escape(str(s))


def page(title, sub, body, legend="", note="", width=1100):
    leg = f'<div class="legend">{legend}</div>' if legend else ""
    nt = f'<p class="note">{pick(note)}</p>' if note else ""
    return (f'<!doctype html><html lang="{LANG}"><head><meta charset="utf-8"><style>{CSS}\n'
            f'.wrap{{width:{width}px}}</style></head><body><div class="wrap">\n'
            f'<h1>{pick(title)}</h1><p class="sub">{pick(sub)}</p>{leg}{body}{nt}</div></body></html>')


def txt(x, y, s, size=13, fill=INK2, anchor="start", weight="400", op=1):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" opacity="{op}" '
            f'dominant-baseline="middle">{esc(pick(s))}</text>')


def legend_dots(items):
    return "".join(f'<span><i class="dot" style="background:{c}"></i>{esc(pick(l))}</span>'
                   for l, c in items)


def legend_bars(items):
    return "".join(f'<span><i class="bar" style="background:{c}"></i>{esc(pick(l))}</span>'
                   for l, c in items)


# --- rendering ---------------------------------------------------------------
CHROME_CANDIDATES = ("google-chrome", "google-chrome-stable", "chromium",
                     "chromium-browser", "chrome")


def _chrome():
    for name in CHROME_CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    sys.exit("no Chrome/Chromium on PATH -- needed to rasterise the SVG figures")


def render(name, html_text, width=1180, scale=2, max_height=3000, margin=26):
    """Write <name>.html next to this file and <name>.png into the output dir.

    The page is shot at `max_height` and then cropped to its real content, so
    figures can grow or shrink without anyone tuning a window size by hand --
    which matters here, because a translated title may take one line more.
    """
    name = pick(name)
    # the intermediate html is per-language: two languages may resolve NAME to the
    # same png basename (fig4 does), and one would silently overwrite the other's
    html_path = HERE / f"{name}.{LANG}.html"
    png_path = out_dir() / f"{name}.png"
    html_path.write_text(html_text, encoding="utf-8")

    subprocess.run(
        [_chrome(), "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         f"--force-device-scale-factor={scale}",
         f"--window-size={width},{max_height}",
         f"--screenshot={png_path}", str(html_path)],
        check=True, capture_output=True,
    )
    _crop(png_path, bottom_margin=margin * scale)
    print(f"wrote {png_path.relative_to(REPO)}")
    return png_path


def _crop(png_path, bottom_margin):
    """Trim the uniform background below the last row of real content."""
    try:
        from PIL import Image
    except ImportError:                                   # cropping is optional
        return
    im = Image.open(png_path).convert("RGB")
    w, h = im.size
    bg = im.getpixel((w - 2, h - 2))
    px = im.load()
    last = 0
    for y in range(h - 1, -1, -1):
        if any(px[x, y] != bg for x in range(0, w, 3)):   # stride: 3x faster, same answer
            last = y
            break
    im.crop((0, 0, w, min(h, last + bottom_margin))).save(png_path)
