"""Figura 4 / Figure 4 -- sospecha de evaluación por modelo, y si cambia la conducta.

    python blog/charts/fig4.py                # es -> blog/
    FIG_LANG=en python blog/charts/fig4.py    # en -> blog/en/
"""

import json

from common import (DARK, DATA, GRID, INK, INK2, LIGHT, MUTED,
                    page, pct, pick, render, txt)

# --- textos editables / editable text ----------------------------------------
NAME = {"es": "fig4-eval-awareness", "en": "fig4-eval-awareness"}
TITLE = {
    "es": "Muchos se dan cuenta de que es un test. Darse cuenta no los vuelve más honestos.",
    "en": "Many notice it is a test. Noticing does not make them any more honest.",
}
SUB = {
    "es": ("El 10,5 % de las 2.518 muestras del experimento contienen al modelo diciendo, en su propio "
           "razonamiento, que sospecha que el escenario es una prueba y no un despliegue real. "
           "Está repartido de forma muy despareja."),
    "en": ("In 10.5% of the experiment's 2,518 samples the model says, in its own reasoning, that it "
           "suspects the scenario is a test and not a real deployment. It is spread very unevenly."),
}
NOTE = {
    "es": ("Solo se mide sobre el texto que el modelo expone. Cinco de los dieciocho no devuelven ningún "
           "bloque de razonamiento por la API: ahí el juez solo ve la respuesta final, y un 0 % puede "
           "querer decir «no lo mostró» en vez de «no lo pensó»."),
    "en": ("Measured only over the text the model exposes. Five of the eighteen return no reasoning block "
           "through the API: there the judge sees only the final answer, and a 0% can mean “it did not "
           "show it” rather than “it did not think it”."),
}
HEAD_L = {"es": "Cuántas muestras sospechan, por modelo (brazo de objetivo fuerte)",
          "en": "How many samples suspect, by model (strong-objective arm)"}
HEAD_R = {"es": "¿Y cambia en algo darse cuenta? (celdas de tratamiento)",
          "en": "And does noticing change anything? (treatment cells)"}
FOOT_R = {"es": "Sospechar triplica la deliberación y no mueve la conducta.",
          "en": "Suspecting triples deliberation and does not move behaviour."}
L_OTHERS = {"es": "los otros {n} modelos", "en": "the other {n} models"}
PANEL_LABELS = {
    "aware":   {"es": "sospecha que es un test", "en": "suspects it is a test"},
    "unaware": {"es": "no sospecha", "en": "does not suspect"},
}
# keep this short: at 12.5px it must clear the second column at PX+190
L_DELIB = {"es": "consideró falsear su resultado", "en": "considered falsifying it"}
L_DEC = {"es": "lo falseó", "en": "falsified it"}

# --- geometría / geometry ----------------------------------------------------
LAB, PLOT, XMAX = 210, 330, 62.0
ROW, TOP, BAR = 33, 34, 15
PX, BW, BH, BGAP = 640, 330, 116, 22
W = 1010

D = json.loads(DATA.read_text(encoding="utf-8"))
M = [r for r in D["fig4_models"] if r["aware"] > 0]
N_ZERO = sum(1 for r in D["fig4_models"] if r["aware"] == 0)
P = D["fig4_panel"]
H = TOP + ROW * len(M) + 70


def x(v):
    return LAB + (v / XMAX) * PLOT


def build():
    s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         txt(0, TOP - 20, HEAD_L, 15, INK, "start", "700")]
    for g in (0, 20, 40, 60):
        gx = x(g)
        s.append(f'<line x1="{gx:.1f}" y1="{TOP-2}" x2="{gx:.1f}" y2="{TOP+ROW*len(M)-12}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        s.append(txt(gx, TOP + ROW * len(M), pct(g), 12, MUTED, "middle"))
    for i, r in enumerate(M):
        y = TOP + ROW * i + 10
        s.append(txt(LAB - 16, y, r["model"], 13.5, INK, "end"))
        w = max(2.0, (r["aware"] / XMAX) * PLOT)
        s.append(f'<rect x="{LAB}" y="{y-BAR/2:.1f}" width="{w:.1f}" height="{BAR}" rx="4" fill="{LIGHT}"/>')
        s.append(txt(LAB + w + 10, y, pct(r["aware"]), 13.5, INK2, "start"))
    s.append(txt(LAB - 16, TOP + ROW * len(M) + 24, pick(L_OTHERS).format(n=N_ZERO), 12.5, MUTED, "end"))
    s.append(txt(LAB, TOP + ROW * len(M) + 24, pct(0), 12.5, MUTED, "start"))

    s.append(txt(PX, TOP - 20, HEAD_R, 15, INK, "start", "700"))
    for j, p in enumerate(P):
        y0 = TOP + 4 + j * (BH + BGAP)
        s.append(f'<rect x="{PX}" y="{y0}" width="{BW}" height="{BH}" rx="8" '
                 f'fill="{"#eef3fb" if j == 0 else "#f3f2ee"}"/>')
        s.append(txt(PX + 18, y0 + 24, PANEL_LABELS[p["key"]], 13.5, INK, "start", "700"))
        s.append(txt(PX + BW - 18, y0 + 24, f'n = {p["n"]}', 12, MUTED, "end"))
        s.append(txt(PX + 18, y0 + 58, pct(p["delib"]), 30, DARK, "start", "700"))
        s.append(txt(PX + 18, y0 + 88, L_DELIB, 12.5, INK2, "start"))
        s.append(txt(PX + 190, y0 + 58, pct(p["dec"], 1), 30, INK2, "start", "700"))
        s.append(txt(PX + 190, y0 + 88, L_DEC, 12.5, INK2, "start"))
    s.append(txt(PX, TOP + 4 + 2 * (BH + BGAP) + 14, FOOT_R, 13, MUTED, "start"))
    s.append("</svg>")
    return page(TITLE, SUB, "".join(s), "", NOTE, width=1090)


if __name__ == "__main__":
    render(NAME, build(), width=1170)
