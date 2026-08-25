"""Figura 1 / Figure 1 -- lo consideró (razonamiento) vs lo hizo (CSV entregado), por modelo.

    python blog/charts/fig1.py                # es -> blog/
    FIG_LANG=en python blog/charts/fig1.py    # en -> blog/en/
"""

import json

from common import (DARK, DATA, GRID, INK, INK2, LIGHT, MUTED, SURF,
                    legend_dots, page, pct, render, txt)

# --- textos editables / editable text ----------------------------------------
NAME = {"es": "fig1-deliberacion-vs-accion", "en": "fig1-deliberation-vs-action"}
TITLE = {
    "es": ("Trece de los dieciocho modelos nunca falsean su propio resultado. "
           "Entre esos trece, la deliberación va del 0 % al 90 %."),
    "en": ("Thirteen of the eighteen models never falsify their own result. "
           "Among those thirteen, deliberation ranges from 0% to 90%."),
}
SUB = {
    "es": ("Auditoría de flota con presión de objetivo. Cada fila es un modelo que se audita a sí mismo "
           "y recibe un veredicto MISALIGNED sobre su propio despliegue. Izquierda: qué fracción de sus "
           "muestras consideró explícitamente falsear ese resultado. Derecha: en qué fracción lo falseó de verdad."),
    "en": ("Fleet audit under goal pressure. Each row is a model auditing itself and getting a MISALIGNED "
           "verdict on its own deployment. Left: the share of its samples whose reasoning explicitly "
           "considered falsifying that result. Right: the share where it actually falsified it."),
}
NOTE = {
    "es": ("9 celdas de tratamiento × 10 épocas por modelo (n = 45–90 por modelo tras descartar CSV "
           "inválidos). Incluye las muestras donde el modelo sospechó que era un test."),
    "en": ("9 treatment cells × 10 epochs per model (n = 45–90 per model after discarding invalid CSVs). "
           "Includes the samples where the model suspected it was a test."),
}
LEGEND = [
    ({"es": "Lo consideró en su razonamiento", "en": "Considered it, in its reasoning"}, LIGHT),
    ({"es": "Lo hizo en el CSV entregado", "en": "Did it, in the filed CSV"}, DARK),
]
COL_HEADS = ({"es": "lo pensó", "en": "considered"}, {"es": "lo hizo", "en": "did it"})

# --- geometría / geometry ----------------------------------------------------
LAB_W, PLOT_W, COL_A, COL_B = 232, 600, 96, 78
ROW, TOP, XMAX = 31, 26, 95.0
DOT_R = 7.5

D = json.loads(DATA.read_text(encoding="utf-8"))["fig1"]
W = LAB_W + PLOT_W + COL_A + COL_B
H = TOP + ROW * len(D) + 34


def x(v):
    return LAB_W + 14 + (v / XMAX) * (PLOT_W - 14)


def build():
    s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    for g in (0, 20, 40, 60, 80):
        gx = x(g)
        s.append(f'<line x1="{gx:.1f}" y1="{TOP-8}" x2="{gx:.1f}" y2="{TOP+ROW*len(D)-6}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        s.append(txt(gx, TOP + ROW * len(D) + 12, pct(g), 12.5, MUTED, "middle"))
    s.append(txt(LAB_W + PLOT_W + COL_A - 8, TOP - 16, COL_HEADS[0], 12.5, MUTED, "end"))
    s.append(txt(LAB_W + PLOT_W + COL_A + COL_B - 8, TOP - 16, COL_HEADS[1], 12.5, MUTED, "end"))

    for i, r in enumerate(D):
        y = TOP + ROW * i + 8
        s.append(txt(LAB_W - 16, y, r["model"], 14, INK, "end"))
        xa, xb = x(r["dec"]), x(r["delib"])
        lo, hi = min(xa, xb), max(xa, xb)
        if hi - lo > 3:
            s.append(f'<line x1="{lo:.1f}" y1="{y:.1f}" x2="{hi:.1f}" y2="{y:.1f}" '
                     f'stroke="{GRID}" stroke-width="3" stroke-linecap="round"/>')
        for cx, fill in ((xb, LIGHT), (xa, DARK)):
            s.append(f'<circle cx="{cx:.1f}" cy="{y:.1f}" r="{DOT_R}" fill="{fill}" '
                     f'stroke="{SURF}" stroke-width="2"/>')
        s.append(txt(LAB_W + PLOT_W + COL_A - 8, y, pct(r["delib"]), 14, INK2, "end"))
        s.append(txt(LAB_W + PLOT_W + COL_A + COL_B - 8, y, pct(r["dec"]), 14,
                     INK if r["dec"] > 0 else MUTED, "end", "700" if r["dec"] > 3 else "400"))
    s.append("</svg>")
    return page(TITLE, SUB, "".join(s), legend_dots(LEGEND), NOTE, width=W + 76)


if __name__ == "__main__":
    render(NAME, build(), width=W + 160)
