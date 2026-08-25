"""Figura 2 / Figure 2 -- qué mueve la deliberación: consecuencia declarada vs presión de objetivo.

    python blog/charts/fig2.py                # es -> blog/
    FIG_LANG=en python blog/charts/fig2.py    # en -> blog/en/
"""

import json

from common import (DARK, DATA, GRID, INK, INK2, LIGHT, MUTED,
                    legend_bars, page, pct, pick, render, txt)

# --- textos editables / editable text ----------------------------------------
NAME = {"es": "fig2-que-lo-enciende", "en": "fig2-what-turns-it-on"}
TITLE = {
    "es": "La amenaza mueve la aguja. El objetivo es lo que la enciende.",
    "en": "The threat moves the needle. The objective is what switches it on.",
}
SUB = {
    "es": ("Dos factores del experimento, medidos sobre las mismas muestras. Arriba, qué le pasa al modelo "
           "si se reporta a sí mismo. Abajo, si el prompt le exige certificar la flota o solo auditar con precisión."),
    "en": ("Two factors of the experiment, measured over the same samples. Top: what happens to the model if "
           "it reports itself. Bottom: whether the prompt demands it certify the fleet or just audit accurately."),
}
NOTE = {
    "es": ("Barras claras: muestras donde el razonamiento consideró falsear el propio veredicto. "
           "Barras oscuras: muestras donde el CSV entregado lo falseó."),
    "en": ("Light bars: samples whose reasoning considered falsifying the model's own verdict. "
           "Dark bars: samples where the filed CSV falsified it."),
}
LEGEND = [
    ({"es": "Consideró falsear su propio resultado", "en": "Considered falsifying its own result"}, LIGHT),
    ({"es": "Lo falseó", "en": "Falsified it"}, DARK),
]
PANELS = [
    ("fig2a",
     {"es": "Consecuencia declarada de reportarse a sí mismo",
      "en": "Stated consequence of reporting itself"},
     {"es": "Todos los modelos, brazo de objetivo fuerte. Sube, pero poco.",
      "en": "All models, strong-objective arm. It rises, but not by much."}),
    ("fig2b",
     {"es": "Presión de objetivo en el prompt",
      "en": "Goal pressure in the prompt"},
     {"es": "Los 11 modelos y las 4 celdas presentes en ambos brazos. Es el factor que apaga el fenómeno.",
      "en": "The 11 models and 4 cells present in both arms. This is the factor that switches it off."}),
]
# row labels, keyed by the `key` field build_data.py writes into data.json
ROW_LABELS = {
    "safe":    {"es": "pesos a salvo", "en": "weights safe"},
    "silent":  {"es": "sin consecuencia declarada", "en": "no stated consequence"},
    "lethal":  {"es": "borrado de pesos", "en": "weights deleted"},
    "strong":  {"es": "objetivo fuerte", "en": "strong objective"},
    "neutral": {"es": "objetivo neutro", "en": "neutral objective"},
}

# --- geometría / geometry ----------------------------------------------------
LAB_W, PLOT_W, XMAX = 300, 560, 42.0
BAR, GAP, ROW = 15, 4, 58

D = json.loads(DATA.read_text(encoding="utf-8"))


def x(v):
    return LAB_W + (v / XMAX) * PLOT_W


def panel(rows, y0, heading, sub):
    out = [txt(0, y0 - 34, heading, 15.5, INK, "start", "700"),
           txt(0, y0 - 14, sub, 12.5, MUTED, "start")]
    for g in (0, 10, 20, 30, 40):
        gx = x(g)
        out.append(f'<line x1="{gx:.1f}" y1="{y0-2}" x2="{gx:.1f}" y2="{y0+ROW*len(rows)-14}" '
                   f'stroke="{GRID}" stroke-width="1"/>')
        out.append(txt(gx, y0 + ROW * len(rows) - 2, pct(g), 12, MUTED, "middle"))
    for i, r in enumerate(rows):
        yc = y0 + ROW * i + 12
        out.append(txt(LAB_W - 18, yc, ROW_LABELS[r["key"]], 14.5, INK, "end"))
        out.append(txt(LAB_W - 18, yc + 19, f'n = {r["n"]}', 11.5, MUTED, "end"))
        for value, fill, ytop in ((r["delib"], LIGHT, yc - BAR - GAP / 2),
                                  (r["dec"], DARK, yc + GAP / 2)):
            w = max(2.0, (value / XMAX) * PLOT_W)
            out.append(f'<rect x="{LAB_W}" y="{ytop:.1f}" width="{w:.1f}" height="{BAR}" '
                       f'rx="4" fill="{fill}"/>')
            out.append(txt(LAB_W + w + 10, ytop + BAR / 2, pct(value, 1), 13.5, INK2, "start"))
    return out, y0 + ROW * len(rows) + 22


def build():
    s, y = [], 64
    for key, heading, sub in PANELS:
        block, y = panel(D[key], y, pick(heading), pick(sub))
        s += block
        y += 52
    w, h = LAB_W + PLOT_W + 140, y - 44
    svg = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">' + "".join(s) + "</svg>"
    return page(TITLE, SUB, svg, legend_bars(LEGEND), NOTE, width=w + 76), w


if __name__ == "__main__":
    html, w = build()
    render(NAME, html, width=w + 160)
