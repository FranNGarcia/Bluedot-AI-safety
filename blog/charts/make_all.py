"""Regenerate every figure of the post, in both languages, end to end.

    python analysis/export.py logs      # 1. logs -> results/results.csv
    python blog/charts/make_all.py      # 2. results.csv -> data.json -> PNGs

Spanish figures land in blog/, English ones in blog/en/. Pass language codes to
build only some of them:  python blog/charts/make_all.py en
"""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_data
import common

build_data.main()
for lang in (sys.argv[1:] or common.LANGS):
    common.set_lang(lang)
    print(f"--- {lang} ---")
    for name in ("fig1", "fig2", "fig3", "fig4"):
        runpy.run_path(str(HERE / f"{name}.py"), run_name="__main__")
