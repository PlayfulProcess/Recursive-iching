# -*- coding: utf-8 -*-
"""Mirror grammars/*/grammar.json into public/grammars/ so the Next.js app (and any
static server pointed at public/) can serve them to the viewers. The root grammars/
folder stays the canon — recursive.eco reads it raw from GitHub; this mirror is only
for the site's own fetches. Run after any grammar rebuild (the build scripts call it).
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "grammars"
DST = ROOT / "public" / "grammars"


def main():
    n = 0
    for g in sorted(SRC.glob("*/grammar.json")):
        out = DST / g.parent.name / "grammar.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(g, out)
        n += 1
    print(f"synced {n} grammar(s) -> public/grammars/")


if __name__ == "__main__":
    main()
