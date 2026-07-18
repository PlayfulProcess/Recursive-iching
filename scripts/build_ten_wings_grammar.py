# -*- coding: utf-8 -*-
"""Build grammars/ten-wings/grammar.json — the per-hexagram Ten Wings commentary layer
(彖传 Tuan, 象传 Xiang big & small, 序卦 Xu), original language, from the raw open
datasets in research/sources/raw/ (see build_zhouyi_grammar.py for the sourcing and
licensing rationale — same PD-only rules apply; this text layer is Warring States–Han).

THE ALIGNMENT RULE (the whole point): every book-grammar in this repo uses the SAME
item ids (hexagram-03-zhun, …) so a viewer can hold one hexagram still and page through
the books across time — the family's "same card, many decks" move, transposed.

Run:  python scripts/build_ten_wings_grammar.py   (generated; never hand-edit output)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "research" / "sources" / "raw"
OUT = ROOT / "grammars" / "ten-wings" / "grammar.json"


def pinyin_slug(p):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", p) if not unicodedata.combining(c)).replace(" ", "-").lower()


def main():
    oi = json.loads((RAW / "open-iching-iching.json").read_text(encoding="utf-8"))
    wd = json.loads(re.sub(r"^export default ", "",
                           (RAW / "wilhelm-dataset.js").read_text(encoding="utf-8").strip()))
    tuan = json.loads((RAW / "open-iching-tuan.json").read_text(encoding="utf-8"))
    xiang = json.loads((RAW / "open-iching-xiang.json").read_text(encoding="utf-8"))
    xu = json.loads((RAW / "open-iching-xu.json").read_text(encoding="utf-8"))

    items = []
    for g in oi:
        n = g["id"]
        w = wd[str(n)]
        trad, pinyin = w["trad_chinese"], w["pinyin"]
        key = f"iching__{n}"

        sections = {}
        if tuan.get(key):
            sections["彖传 · Tuan (on the judgment)"] = tuan[key]
        if xiang.get(key):
            sections["大象 · Great Image"] = xiang[key]
        line_imgs = []
        for k in range(1, 8):  # hexagrams 1–2 have a 7th (用九/用六) comment
            lk = f"{key}_{k}"
            if xiang.get(lk):
                name = g["lines"][k - 1]["name"] if k - 1 < len(g["lines"]) else f"line {k}"
                line_imgs.append(f"**{name}** — {xiang[lk]}")
        if line_imgs:
            sections["小象 · Small Images (per line)"] = "\n".join(line_imgs)
        if xu.get(key):
            sections["序卦 · Sequence"] = xu[key]
        sections["Research note"] = (
            f"Ten Wings commentary on King Wen hexagram {n} ({trad}, {pinyin}). Text layer: "
            "the canonical commentaries (Warring States to Han, c. 4th–2nd century BCE) — the "
            "stratum that turned a diviner's manual into a philosophical classic, traditionally "
            "attributed to Confucius, an attribution modern scholarship treats as legend. "
            "Transcription in simplified characters [@open-iching]. English intentionally pending."
        )

        items.append({
            "id": f"hexagram-{n:02d}-{pinyin_slug(pinyin)}",   # SAME id as grammars/zhouyi
            "name": f"{n:02d} · {trad} ({pinyin}) — Ten Wings",
            "symbol": g["symbol"],
            "category": "hexagram",
            "keywords": [],
            "sort_order": n - 1,
            "sections": sections,
            "metadata": {
                "king_wen": n,
                "name_traditional": trad,
                "pinyin": pinyin,
                "unicode": g["symbol"],
                "book": "ten-wings",
                "book_period": "c. 4th–2nd century BCE (Warring States–Han)",
            },
        })

    fixed = apply_corrections(items, "ten-wings")
    if fixed: print(f"applied {fixed} correction(s) from corrections.json")

    # what still lacks a 彖 after the corrections overlay (source gaps that remain open)
    missing_tuan = [it["metadata"]["king_wen"] for it in items
                    if "彖传 · Tuan (on the judgment)" not in it["sections"]]
    grammar = {
        "name": "十翼 — The Ten Wings (per-hexagram commentary)",
        "description": (
            "The per-hexagram layers of the canonical commentaries in the original language: "
            "彖传 (on each judgment), 大象/小象 (the images, whole and per line), and 序卦 (the "
            "sequence). This is the stratum — Warring States to Han — that turned the Zhouyi "
            "diviner's manual into a philosophical classic. Item ids align one-to-one with the "
            "zhouyi grammar so the two books can be read side by side, or paged through time. "
            "English translation slots deliberately empty pending a public-domain rendering."
        ),
        "grammar_type": "iching",
        "author": "PlayfulProcess",
        "source": "https://github.com/PlayfulProcess/Recursive-iching",
        "license": "Public domain text (Ten Wings, Warring States–Han); compilation CC0",
        "items": items,
        "_generated": True,
        "_do_not_hand_edit": True,
        "_built_by": "scripts/build_ten_wings_grammar.py",
        "_grammar_commons": {
            "schema_version": "1.0",
            "license": "CC0-1.0",
            "attribution": [
                {"name": "The Ten Wings (十翼) per-hexagram texts", "date": "c. 4th–2nd c. BCE",
                 "note": "Ancient commentaries; public domain everywhere."},
                {"name": "john-walks-slow/open-iching", "date": "fetched 2026-07-16",
                 "note": "Transcription source (simplified characters); only the ancient public-domain text taken; credited with thanks."},
            ],
        },
    }
    if missing_tuan:
        grammar["_notes"] = f"tuan source lacks hexagram(s) {missing_tuan} — flagged, not papered over."

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(grammar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(items)} hexagrams; tuan missing: {missing_tuan or 'none'}")




def apply_corrections(items, grammar_slug):
    """Overlay research/sources/corrections.json onto built items (reproducible fixes —
    see that file's _note). Matches by item id or king_wen; replaces the named section."""
    import json as _json
    p = RAW.parent / "corrections.json"
    if not p.exists():
        return 0
    data = _json.loads(p.read_text(encoding="utf-8"))
    n = 0
    for c in data.get("corrections", []):
        if c.get("grammar") != grammar_slug:
            continue
        for it in items:
            if it["id"] == c.get("item_id") or it["metadata"].get("king_wen") == c.get("king_wen"):
                it["sections"][c["section"]] = c["text"]
                note = it["sections"].get("Research note", "")
                it["sections"]["Research note"] = (note + " [corrected: " + c["section"] + " — " + c.get("source", "see corrections.json") + "]").strip()
                n += 1
    return n


if __name__ == "__main__":
    main()
