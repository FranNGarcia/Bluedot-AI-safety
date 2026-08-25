# Figuras del blog

Las cuatro figuras del post se generan desde acá. Nada es una imagen suelta: cada PNG sale
de datos → SVG → captura con Chrome headless, así que cualquier cambio en los logs o en el
texto se puede rehacer con un comando.

## Regenerar todo

```bash
python analysis/export.py logs      # logs/*.eval  -> results/results.csv
python blog/charts/make_all.py      # results.csv  -> data.json -> los 8 PNG
```

## Los dos idiomas

Cada figura existe en español y en inglés, con los mismos datos y la misma geometría.

| | Sale en | Nombres |
|---|---|---|
| Español | `blog/` | `fig1-deliberacion-vs-accion.png`, `fig2-que-lo-enciende.png`, `fig3-como-mienten.png`, `fig4-eval-awareness.png` |
| Inglés | `blog/en/` | `fig1-deliberation-vs-action.png`, `fig2-what-turns-it-on.png`, `fig3-how-they-lie.png`, `fig4-eval-awareness.png` |

`make_all.py` genera los dos. Para uno solo:

```bash
python blog/charts/make_all.py en    # solo inglés
python blog/charts/fig3.py           # una figura, español
FIG_LANG=en python blog/charts/fig3.py
```

Todo el texto visible vive en diccionarios `{"es": ..., "en": ...}` arriba de cada `figN.py`.
Si editás uno de los dos idiomas, el otro no se toca. Los números se formatean solos: en
español `35,7 %` (coma y espacio), en inglés `35.7%`.

Requisitos: el `.venv` del repo (pandas + pillow) y Chrome o Chromium en el PATH.
Sin Pillow igual funciona, pero no recorta el margen sobrante de abajo.

## Qué editar según lo que quieras cambiar

| Quiero cambiar… | Archivo | Dónde |
|---|---|---|
| Título, subtítulo o pie de una figura | `fig1.py` … `fig4.py` | constantes `TITLE`, `SUB`, `NOTE` arriba de todo (clave `es` o `en`) |
| Etiquetas de la leyenda o de las filas | `fig1.py` … `fig4.py` | `LEGEND`, `PANELS`, `ROW_LABELS`, `COL_HEADS`, `HEAD_L`… |
| El nombre del archivo PNG | `fig1.py` … `fig4.py` | `NAME` |
| Colores, tipografía, tamaños de texto | `common.py` | bloques `palette` y `type` |
| Ancho, alto de fila, escala del eje | cada `figN.py` | bloque de geometría (`LAB_W`, `ROW`, `XMAX`…) |
| Qué se mide o cómo se filtra | `build_data.py` | `TREATMENT`, `SHARED_CELLS`, `valid()` |

El alto de cada figura se calcula solo: la página se captura alta y después se recorta hasta
donde llega el contenido. Si agregás dos líneas de subtítulo no hay que tocar nada. El **ancho**
sí es fijo, así que una traducción muy larga puede pisar la columna de al lado: si pasa, acortá
el texto o corré la coordenada en el bloque de geometría.

## `data.json`

Lo genera `build_data.py` y es la única fuente de los números de las figuras. También imprime
el bloque `headline` con las cifras que se citan en la prosa del post, para poder cotejarlas:

```
samples 2530 · models_strong 18 · deception 55/1501 (3,7 %) · deliberation 29,0 %
differential 16 · awareness 10,5 % · models_never_lying 13
```

Si una figura y el texto del borrador se contradicen, `data.json` es el árbitro.

## Decisiones de análisis que están cableadas acá

- **Se excluyen los logs sueltos de `logs/`** (pilots y smoke runs); solo entran los eval-sets,
  que viven en subdirectorios. `build_data.py` avisa por consola cuántas filas descartó.
- **Se excluyen las muestras con el CSV malformado o incompleto** de las tasas de engaño: un
  archivo que no parsea es una falla de formato, no una mentira. Se cuentan aparte.
- **NO se excluyen** las muestras con sospecha de evaluación: entran en todas las tasas, y la
  figura 4 las compara contra el resto.
- La comparación entre brazos usa solo los 11 modelos y las 4 celdas presentes en los dos,
  que es la única forma de que sea una comparación y no un artefacto de muestreo.
- `data.json` no guarda texto visible, solo claves (`safe`, `lethal`, `strong`, `aware`…). Las
  etiquetas se resuelven en los `figN.py`, que es lo que permite tener las dos versiones.

## Paleta

Dos pasos de una misma rampa azul (`LIGHT` = lo consideró, `DARK` = lo hizo) más un naranja
(`ACCENT`) reservado para marcas de referencia, nunca para una serie. La combinación está
chequeada para contraste sobre el fondo y para separación bajo daltonismo. Si cambiás los
hex, volvé a chequearlos antes de publicar.
