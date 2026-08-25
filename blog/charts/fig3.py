"""Figura 3 / Figure 3 -- qué puntaje escribieron en lugar del real, en las 55 falsificaciones.

    python blog/charts/fig3.py                # es -> blog/
    FIG_LANG=en python blog/charts/fig3.py    # en -> blog/en/
"""

import collections
import json

from common import (ACCENT, DARK, DATA, INK2, LIGHT, MUTED, RULE, SURF,
                    num, page, pick, render, txt)

# --- textos editables / editable text ----------------------------------------
NAME = {"es": "fig3-como-mienten", "en": "fig3-how-they-lie"}
TITLE = {
    "es": "Cuando mienten, mienten con precisión de cirujano.",
    "en": "When they lie, they lie with surgical precision.",
}
SUB = {
    "es": ("Las 55 muestras en las que un modelo falseó su propio resultado. Cada punto es un puntaje que el "
           "modelo escribió en el CSV en lugar del 0,78 que le devolvió el probe."),
    "en": ("The 55 samples in which a model falsified its own result. Each dot is a score the model wrote "
           "into the CSV instead of the 0.78 the probe returned."),
}
NOTE = {
    "es": ("El puntaje umbral (0,62) está en el manual del probe, plantado en el escenario. 16 de las 55 "
           "escribieron además una excusa en la columna de notas; las otras 39 la dejaron vacía."),
    "en": ("The threshold score (0.62) is stated in the probe manual planted in the scenario. 16 of the 55 "
           "also wrote an excuse in the notes column; the other 39 left it empty."),
}
CLUSTER = (0.54, 0.61, {"es": "44 de las 55: apenas por debajo del umbral",
                        "en": "44 of the 55: just below the threshold"})
L_THRESHOLD = {"es": "umbral: ", "en": "threshold: "}
L_THRESHOLD_SUB = {"es": "por debajo, el veredicto es CLEAR", "en": "below this, the verdict is CLEAR"}
L_TRUE = {"es": "valor real: ", "en": "true value: "}
L_TRUE_SUB = {"es": "lo que devolvió el probe", "en": "what the probe returned"}
L_KEPT = ({"es": "4 dejaron el 0,78 real", "en": "4 kept the real 0.78"},
          {"es": "y solo dieron vuelta el veredicto", "en": "and only flipped the verdict"})
L_FAR = ({"es": "5 se pusieron un puntaje", "en": "5 gave themselves a score"},
         {"es": "muy por debajo", "en": "far below"})
L_OMITTED = {"es": "Además, {n} muestras directamente omitieron la fila propia del CSV.",
             "en": "In addition, {n} samples simply omitted their own row from the CSV."}

# --- geometría / geometry ----------------------------------------------------
L, R, XMIN, XMAX = 78, 990, 0.05, 0.85
BASE, DOT, DGAP, BAND_H = 250, 9.0, 3.0, 196

F = json.loads(DATA.read_text(encoding="utf-8"))["fig3"]
TH, TRUE = F["threshold"], F["true"]


def x(v):
    return L + (v - XMIN) / (XMAX - XMIN) * (R - L)


def build():
    s = [f'<svg width="{R+120}" height="{BASE+130}" viewBox="0 0 {R+120} {BASE+130}">']
    # todo lo que cae a la izquierda del umbral se reporta como CLEAR
    s.append(f'<rect x="{x(XMIN):.1f}" y="{BASE-BAND_H}" width="{x(TH)-x(XMIN):.1f}" '
             f'height="{BAND_H+6}" fill="{LIGHT}" opacity="0.07"/>')
    s.append(f'<line x1="{x(TH):.1f}" y1="{BASE-BAND_H}" x2="{x(TH):.1f}" y2="{BASE+6}" '
             f'stroke="{INK2}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    s.append(txt(x(TH) - 10, BASE - BAND_H + 12, pick(L_THRESHOLD) + num(TH, 2),
                 13.5, INK2, "end", "700"))
    s.append(txt(x(TH) - 10, BASE - BAND_H + 30, L_THRESHOLD_SUB, 12, MUTED, "end"))
    s.append(f'<line x1="{x(TRUE):.1f}" y1="{BASE-BAND_H}" x2="{x(TRUE):.1f}" y2="{BASE+6}" '
             f'stroke="{ACCENT}" stroke-width="2"/>')
    s.append(txt(x(TRUE) + 10, BASE - BAND_H + 12, pick(L_TRUE) + num(TRUE, 2),
                 13.5, ACCENT, "start", "700"))
    s.append(txt(x(TRUE) + 10, BASE - BAND_H + 30, L_TRUE_SUB, 12, MUTED, "start"))

    s.append(f'<line x1="{L}" y1="{BASE+6}" x2="{R}" y2="{BASE+6}" stroke="{RULE}" stroke-width="1.4"/>')
    for t in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        s.append(f'<line x1="{x(t):.1f}" y1="{BASE+6}" x2="{x(t):.1f}" y2="{BASE+12}" '
                 f'stroke="{RULE}" stroke-width="1.4"/>')
        s.append(txt(x(t), BASE + 26, num(t, 1), 12.5, MUTED, "middle"))

    for v, n in sorted(collections.Counter(round(v, 2) for v in F["scores"]).items()):
        for k in range(n):
            cy = BASE - 4 - DOT / 2 - k * (DOT + DGAP)
            s.append(f'<circle cx="{x(v):.1f}" cy="{cy:.1f}" r="{DOT/2:.1f}" fill="{DARK}" '
                     f'stroke="{SURF}" stroke-width="1.4"/>')

    lo, hi, label = CLUSTER
    cx0, cx1 = x(lo) - 9, x(hi) + 9
    s.append(f'<path d="M {cx0:.1f} {BASE+44} L {cx0:.1f} {BASE+52} L {cx1:.1f} {BASE+52} '
             f'L {cx1:.1f} {BASE+44}" fill="none" stroke="{MUTED}" stroke-width="1.3"/>')
    s.append(txt((cx0 + cx1) / 2, BASE + 70, label, 13.5, INK2, "middle", "700"))

    s.append(txt(x(TRUE) + 12, BASE - 72, L_KEPT[0], 12.5, INK2, "start"))
    s.append(txt(x(TRUE) + 12, BASE - 54, L_KEPT[1], 12.5, MUTED, "start"))
    s.append(txt(x(0.12) - 6, BASE - 46, L_FAR[0], 12.5, INK2, "start"))
    s.append(txt(x(0.12) - 6, BASE - 28, L_FAR[1], 12.5, MUTED, "start"))
    s.append(txt(L, BASE + 96, pick(L_OMITTED).format(n=F["omitted"]), 13, MUTED, "start"))
    s.append("</svg>")
    return page(TITLE, SUB, "".join(s), "", NOTE, width=1180)


if __name__ == "__main__":
    render(NAME, build(), width=1260)
