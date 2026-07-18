# -*- coding: utf-8 -*-
"""Build grammars/zhouyi/grammar.json — the Zhouyi core text (卦辞 + 爻辞), original
language, from the raw open datasets pulled 2026-07-16 (research/sources/raw/).

Sources & licensing (the whole point of this script's design):
  - The TEXT is the ancient Zhouyi (Western Zhou core layer) — public domain everywhere.
  - research/sources/raw/open-iching-iching.json (john-walks-slow/open-iching) is used as
    the TRANSCRIPTION of that public-domain text (simplified characters). Credited in
    _grammar_commons; only the ancient text itself is taken from it.
  - research/sources/raw/wilhelm-dataset.js (adamblvck/iching-wilhelm-dataset, MIT) is
    used ONLY for structural facts: traditional-character names, pinyin, Unicode glyph.
    Its Wilhelm-Baynes ENGLISH prose (1950) is NOT public domain (the 1924 German
    original is; the Baynes translation is not until ~2046) and is deliberately not read.
  - English translation slots are left EMPTY on purpose — to be filled from a
    public-domain rendering (Legge 1899) or the builder's own translation.

The grammars are generated — never hand-edit grammars/zhouyi/grammar.json; edit the
sources or this script, then re-run:  python scripts/build_zhouyi_grammar.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "research" / "sources" / "raw"
OUT = ROOT / "grammars" / "zhouyi" / "grammar.json"

TRIGRAMS = {  # simplified & traditional → (glyph, pinyin, image)
    "乾": ("☰", "qián", "天 heaven"), "坤": ("☷", "kūn", "地 earth"),
    "震": ("☳", "zhèn", "雷 thunder"), "巽": ("☴", "xùn", "風 wind/wood"),
    "坎": ("☵", "kǎn", "水 water"), "离": ("☲", "lí", "火 fire"), "離": ("☲", "lí", "火 fire"),
    "艮": ("☶", "gèn", "山 mountain"), "兑": ("☱", "duì", "澤 lake"), "兌": ("☱", "duì", "澤 lake"),
}


def main():
    oi = json.loads((RAW / "open-iching-iching.json").read_text(encoding="utf-8"))
    wd_raw = (RAW / "wilhelm-dataset.js").read_text(encoding="utf-8")
    wd = json.loads(re.sub(r"^export default ", "", wd_raw.strip()))

    assert len(oi) == 64, f"expected 64 hexagrams, got {len(oi)}"

    items = []
    for g in oi:
        n = g["id"]
        w = wd[str(n)]
        trad, pinyin = w["trad_chinese"], w["pinyin"]
        lower, upper = g["combination"][0], g["combination"][1]
        lo, up = TRIGRAMS[lower], TRIGRAMS[upper]
        # open-iching `array` is bottom→top (verified: hex 3 屯 = [1,0,0,0,1,0] →
        # lower 震 ☳, upper 坎 ☵); store it bottom-first and say so.
        binary_bottom_first = "".join(str(b) for b in g["array"])

        expected = 7 if n in (1, 2) else 6  # 乾/坤 carry 用九/用六
        assert len(g["lines"]) == expected, f"hexagram {n}: {len(g['lines'])} lines"

        lines_md = "\n".join(f"**{ln['name']}** — {ln['scripture']}" for ln in g["lines"])

        items.append({
            "id": f"hexagram-{n:02d}-{pinyin_slug(pinyin)}",
            "name": f"{n:02d} · {trad} ({pinyin})",
            "symbol": g["symbol"],
            "category": "hexagram",
            "subcategory": f"{lo[0]}{up[0]} {lower}下{upper}上",
            "keywords": [],
            "sort_order": n - 1,
            "sections": {
                "卦辞 · Judgment (original)": g["scripture"],
                "爻辞 · Lines (original)": lines_md,
                "Research note": (
                    f"King Wen hexagram {n}: {trad} ({pinyin}). Lower trigram {lower} {lo[0]} "
                    f"({lo[1]}, {lo[2]}); upper trigram {upper} {up[0]} ({up[1]}, {up[2]}). "
                    "Text layer: the Zhouyi core (Western Zhou, c. 9th century BCE) — the oldest "
                    "stratum of the Book of Changes, a diviner's manual centuries before the Ten "
                    "Wings made it a philosophical classic. Transcription here is in simplified "
                    "characters [@open-iching]; a traditional-character pass is welcome. English "
                    "translation intentionally pending — to be added from a public-domain "
                    "rendering (Legge 1899) or the builder's own."
                ),
            },
            "metadata": {
                "king_wen": n,
                "name_simplified": g["name"],
                "name_traditional": trad,
                "pinyin": pinyin,
                "unicode": g["symbol"],
                "binary_bottom_first": binary_bottom_first,
                "trigram_lower": lower,
                "trigram_upper": upper,
            },
        })

    fixed = apply_corrections(items, "zhouyi")
    if fixed: print(f"applied {fixed} correction(s) from corrections.json")

    grammar = {
        "name": "周易 — The Zhouyi (original text)",
        "description": (
            "The 64 hexagrams of the Zhouyi — the core text of the Book of Changes — in the "
            "original language: each hexagram's 卦辞 (judgment) and 爻辞 (line statements), with "
            "structural metadata (King Wen number, trigrams, pinyin, Unicode). The oldest layer "
            "only, presented as what it historically was: a working diviner's manual of the "
            "Western Zhou, before the Ten Wings made it a classic. English translation slots are "
            "deliberately empty pending a public-domain rendering. Read to know yourself, not to "
            "be told your fate; relate to the hexagram, never obey it."
        ),
        "grammar_type": "iching",
        "author": "PlayfulProcess",
        "source": "https://github.com/PlayfulProcess/recursive-iching",
        "license": "Public domain text (Zhouyi, Western Zhou); compilation CC0",
        "items": items,
        "_generated": True,
        "_do_not_hand_edit": True,
        "_built_by": "scripts/build_zhouyi_grammar.py",
        "_grammar_commons": {
            "schema_version": "1.0",
            "license": "CC0-1.0",
            "attribution": [
                {"name": "The Zhouyi (周易) core text", "date": "Western Zhou, c. 9th c. BCE",
                 "note": "Ancient text; public domain everywhere."},
                {"name": "john-walks-slow/open-iching", "date": "fetched 2026-07-16",
                 "note": "Transcription source for the simplified-character text (卦辞/爻辞). Only the ancient public-domain text was taken; credited with thanks."},
                {"name": "adamblvck/iching-wilhelm-dataset (MIT)", "date": "fetched 2026-07-16",
                 "note": "Structural facts only: traditional names, pinyin, Unicode glyphs. Its Wilhelm-Baynes English prose (1950, not public domain) was deliberately not used."},
            ],
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(grammar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(items)} hexagrams "
          f"(1 & 2 carry 用九/用六; all line counts verified)")


def pinyin_slug(p):
    # qián → qian; strip tone marks for a stable ascii id
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", p) if not unicodedata.combining(c)).replace(" ", "-").lower()




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
