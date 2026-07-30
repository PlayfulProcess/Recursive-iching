# -*- coding: utf-8 -*-
"""Build grammars/ten-wings/grammar.json — the per-hexagram Ten Wings commentary layer
(彖传 Tuan, 象传 Xiang big & small, 文言 Wenyan on hexagrams 1–2, 序卦 Xu), original
language, from the raw open datasets in research/sources/raw/ (see build_zhouyi_grammar.py
for the sourcing and licensing rationale — same PD-only rules apply; this text layer is
Warring States–Han).

Since 2026-07-30 the same items also carry James Legge's public-domain English beside the
Chinese as `sections_i18n.en` — his Appendixes I, II, IV and VI, harvested and verified by
scripts/fetch_legge_wings.py. The convention is GRAMMAR_FORMAT.md, "Languages": the
Chinese stays canonical in `sections`, the English mirrors its key set exactly, and
check.py fails the build if a language block has a hole in it. Wilhelm-Baynes (1950) is
still not public domain and still stays out.

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

# Public-domain cover, verified 2026-07-26 against its Wikimedia Commons file page.
# The Wings are the layer traditionally (and, scholars agree, wrongly) ascribed to
# Confucius — so the apt picture is the ascription itself, in its oldest surviving
# pictorial form. Full provenance below in _image_provenance; registry: docs/IMAGES.md.
COVER_URL = (
    "https://commons.wikimedia.org/wiki/Special:FilePath/"
    "Confucius_Tang_Dynasty.jpg?width=350"
)


def pinyin_slug(p):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", p) if not unicodedata.combining(c)).replace(" ", "-").lower()


# Canonical English trigram names — the exact strings recursive.eco's converter
# (iching-conversion.ts TRIGRAM_LOOKUP) resolves. Same map as build_zhouyi_grammar.py.
FLOW_TRIGRAM = {
    "乾": "heaven", "坤": "earth", "震": "thunder", "巽": "wind",
    "坎": "water", "离": "fire", "離": "fire", "艮": "mountain",
    "兑": "lake", "兌": "lake",
}


def add_canonical_sections(items):
    """Jul 18 2026 — canonical-format alignment with recursive.eco (the flow app).

    The app's converter reads ONLY canonical keys: sections `Judgment`/`Image`/
    `Line 1`..`Line 6`. Our scholarly section names (彖传/大象/小象) are the
    book's identity and STAY; this adds canonical duplicates so the same grammar
    renders fully in the app. Runs AFTER apply_corrections so corrected text
    flows into the canonical copies. setdefault: never clobbers."""
    for it in items:
        s = it["sections"]
        if "彖传 · Tuan (on the judgment)" in s:
            s.setdefault("Judgment", s["彖传 · Tuan (on the judgment)"])
        if "大象 · Great Image" in s:
            s.setdefault("Image", s["大象 · Great Image"])
        blob = s.get("小象 · Small Images (per line)", "")
        line_entries = [ln for ln in blob.split("\n") if ln.strip()]
        for i, ln in enumerate(line_entries[:6], start=1):
            s.setdefault(f"Line {i}", ln)


# Legge's own words for the seventh paragraph hexagrams 1 and 2 carry — the 用九/用六
# comment, on the cast in which every line moves. Same map as build_zhouyi_grammar.py.
SEVENTH = {1: "The use of the number nine", 2: "The use of the number six"}

# The canonical section keys, in the order the items carry them, and where each one's
# English comes from. Written out rather than inferred so that adding a section to this
# book without deciding where its English comes from is a build error, not a silent hole.
WENYAN_KEY = "文言 · Wenyan (words on the text)"


def english_sections(kw: int, wings: dict) -> dict:
    """James Legge's English for one hexagram, keyed by the canonical section it mirrors.

    Appendix I is his Thwan treatise (彖传), Appendix II his Symbolism — the opening
    paragraph is the Great Image (大象) and the numbered ones the Small Images (小象) —
    Appendix IV the Wenyan on hexagrams 1 and 2, Appendix VI the orderly sequence (序卦).

    On the sequence, one thing has to be said plainly rather than smoothed over: Legge's
    Appendix VI is printed as running paragraphs, each walking a RUN of hexagrams, while
    the Chinese 序卦 here is cut per hexagram. So a hexagram's English is the whole
    paragraph its Chinese sentence falls inside, and it says which run that is. The fit is
    honest; it is not one-to-one, and pretending otherwise would mean cutting Legge's
    sentences to a shape the printed book does not have."""
    a1 = wings["appendix_1"][str(kw)]["paragraphs"]
    a2 = wings["appendix_2"][str(kw)]
    labels = [f"Line {i}" for i in range(1, 7)]
    if len(a2["line_images"]) == 7:
        labels.append(SEVENTH[kw])
    lines = [f"**{lab}** — {txt}" for lab, txt in zip(labels, a2["line_images"])]

    out = {
        "彖传 · Tuan (on the judgment)": "\n".join(a1),
        "大象 · Great Image": a2["great_image"],
        "小象 · Small Images (per line)": "\n".join(lines),
        "_lines": lines,                                   # for the canonical Line N aliases
    }
    if str(kw) in wings["appendix_4"]:
        out[WENYAN_KEY] = "\n".join(wings["appendix_4"][str(kw)]["paragraphs"])
    block = wings["appendix_6"]["blocks"][wings["appendix_6"]["by_hexagram"][str(kw)]]
    out["序卦 · Sequence"] = (
        f"**Appendix VI, the paragraph on hexagrams {block['label']}** — {block['text']}")
    return out


def add_english(items, wings):
    """Attach Legge's English as `sections_i18n.en` on every hexagram.

    THE CONVENTION (GRAMMAR_FORMAT.md, "Languages"): `sections` stays the canonical text —
    here the Chinese — and the language block mirrors its key set exactly, so a viewer can
    swap languages section for section without knowing anything about this book, and a
    missing key is a build failure rather than a hole the reader discovers. That is why the
    English block repeats the 彖传/大象/小象 key names: the key is the *slot*, not the label.

    Runs last, after apply_corrections and add_canonical_sections, so it mirrors whatever
    key set the item actually ended up with."""
    for it in items:
        kw = it["metadata"]["king_wen"]
        src = english_sections(kw, wings)
        lines = src.pop("_lines")
        en = {}
        for key in it["sections"]:                         # canonical order, mirrored
            if key in src:
                en[key] = src[key]
            elif key == "Research note":
                en[key] = it["sections"][key]              # already English
            elif key == "Judgment":
                en[key] = src["彖传 · Tuan (on the judgment)"]
            elif key == "Image":
                en[key] = src["大象 · Great Image"]
            elif key.startswith("Line "):
                en[key] = lines[int(key.split()[1]) - 1]
            else:
                raise SystemExit(
                    f"hexagram {kw}: section '{key}' has no English counterpart — decide "
                    f"where it comes from here rather than shipping a block with a hole in it")
        it["sections_i18n"] = {"en": en}


def i18n_block(wings):
    """Root-level provenance for every language in `sections_i18n` — who translated it,
    when, from where, on what basis it is free, and exactly how much of the book it
    reaches. check.py requires all of it."""
    return {
        "canonical_language": "zh-Hans",
        "canonical_note": (
            "Each item's `sections` is the canonical text: the Ten Wings in simplified "
            "Chinese. `sections_i18n` holds translations beside it, never over it — a "
            "language block mirrors the canonical key set exactly. There is no 'zh' block "
            "because Chinese is what `sections` already is."
        ),
        "languages": [
            {
                "lang": "en",
                "name": "English",
                "translator": "James Legge (1815–1897)",
                "year": "1882 (2nd ed. 1899)",
                "work": "The Yî King, Sacred Books of the East vol. XVI (Oxford: Clarendon Press)",
                "source": wings["_transcription_source"],
                "source_url": wings["_transcription_source_url"],
                "pd_basis": wings["_pd_basis"],
                "retrieved_on": wings["_fetched_on"],
                "coverage": (
                    "Complete for the Wings this book carries: all 64 彖传 (Legge's Appendix I, "
                    "179 paragraphs), all 64 大象 and all 386 小象 (Appendix II), the 文言 of "
                    "hexagrams 1 and 2 (Appendix IV, 36 + 10 paragraphs), and the 序卦 of the 60 "
                    "hexagrams whose Chinese sequence text this book carries (Appendix VI)."
                ),
                "coverage_note": (
                    "Appendix VI is printed as running paragraphs covering runs of hexagrams "
                    "while the Chinese 序卦 is cut per hexagram, so a hexagram's English "
                    "sequence text is the whole paragraph its sentence falls inside, labelled "
                    "with the run. Hexagrams 1, 2, 12 and 32 have no Chinese 序卦 in the "
                    "transcription this book is built from, and so have no English one either — "
                    "the language block mirrors the canonical keys, gaps included."
                ),
                "not_included": (
                    "Legge's Appendix III (繫辭 Xi Ci), Appendix V (說卦 Shuogua) and Appendix VII "
                    "(雜卦 Zagua): whole-treatise Wings that speak about the book rather than "
                    "about any one hexagram, so this per-hexagram grammar has no canonical "
                    "Chinese slot for them to sit beside. Also not included: Legge's own "
                    "footnotes and commentary — his 19th-century reading, not the Wings."
                ),
                "verified": (
                    "Appendixes I and II were required to arrive as an unbroken run of Roman "
                    "numerals I–LXIV, each hexagram yielding a Tuan, a Great Image and exactly "
                    "six Small Images (seven for hexagrams 1 and 2); Appendix VI to cover 1–64 "
                    "with no hexagram outside a paragraph's range; Appendix IV to reach the 36 "
                    "and 10 paragraphs the printing has. All 649 harvested passages were then "
                    "cross-checked against the Internet Archive's independent scan of the 1882 "
                    "first edition (archive.org/details/wg916), with nothing flagged. "
                    "See scripts/fetch_legge_wings.py."
                ),
                "built_by": "scripts/fetch_legge_wings.py → scripts/build_ten_wings_grammar.py",
            },
        ],
    }


def main():
    oi = json.loads((RAW / "open-iching-iching.json").read_text(encoding="utf-8"))
    wd = json.loads(re.sub(r"^export default ", "",
                           (RAW / "wilhelm-dataset.js").read_text(encoding="utf-8").strip()))
    tuan = json.loads((RAW / "open-iching-tuan.json").read_text(encoding="utf-8"))
    xiang = json.loads((RAW / "open-iching-xiang.json").read_text(encoding="utf-8"))
    xu = json.loads((RAW / "open-iching-xu.json").read_text(encoding="utf-8"))
    wen = json.loads((RAW / "open-iching-wen.json").read_text(encoding="utf-8"))
    wings = json.loads((RAW / "legge-yi-king-appendixes.json").read_text(encoding="utf-8"))

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
        if wen.get(key):                      # 文言 exists for hexagrams 1 and 2 only
            sections[WENYAN_KEY] = wen[key]
        if xu.get(key):
            sections["序卦 · Sequence"] = xu[key]
        sections["Research note"] = (
            f"Ten Wings commentary on King Wen hexagram {n} ({trad}, {pinyin}). Text layer: "
            "the canonical commentaries (Warring States to Han, c. 4th–2nd century BCE) — the "
            "stratum that turned a diviner's manual into a philosophical classic, traditionally "
            "attributed to Confucius, an attribution modern scholarship treats as legend. "
            "Transcription in simplified characters [@open-iching]. English is James Legge's "
            "(Sacred Books of the East vol. XVI, 1882/1899 — public domain): his Appendix I for "
            "the 彖传, Appendix II for the 大象 and 小象, Appendix IV for the 文言, Appendix VI "
            "for the 序卦, carried beside the Chinese as sections_i18n.en, not over it."
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
                # Canonical keys the recursive.eco converter reads (Jul 18 2026
                # alignment — see add_canonical_sections). open-iching `array` is
                # bottom-line-first, same as the app's convention: verbatim copy.
                "number": n,
                "binary": "".join(str(b) for b in g["array"]),
                "chinese_name": trad,
                "trigram_below": FLOW_TRIGRAM[g["combination"][0]],
                "trigram_above": FLOW_TRIGRAM[g["combination"][1]],
            },
        })

    fixed = apply_corrections(items, "ten-wings")
    if fixed: print(f"applied {fixed} correction(s) from corrections.json")
    add_canonical_sections(items)
    # English last: the language block mirrors whatever key set the canonical sections
    # ended up with, corrections and canonical aliases included.
    add_english(items, wings)

    # what still lacks a 彖 after the corrections overlay (source gaps that remain open)
    missing_tuan = [it["metadata"]["king_wen"] for it in items
                    if "彖传 · Tuan (on the judgment)" not in it["sections"]]
    grammar = {
        "name": "十翼 — The Ten Wings (per-hexagram commentary)",
        "description": (
            "The per-hexagram layers of the canonical commentaries in the original language: "
            "彖传 (on each judgment), 大象/小象 (the images, whole and per line), 文言 (on "
            "hexagrams 1 and 2), and 序卦 (the sequence). This is the stratum — Warring States "
            "to Han — that turned the Zhouyi diviner's manual into a philosophical classic. "
            "Item ids align one-to-one with the zhouyi grammar so the two books can be read "
            "side by side, or paged through time. James Legge's public-domain English "
            "(Appendixes I, II, IV and VI; 1882/1899) travels beside the Chinese rather than "
            "replacing it. The whole-treatise Wings — 繫辭, 說卦, 雜卦 — speak about the book "
            "rather than about any one hexagram, and are not in this per-hexagram grammar in "
            "either language."
        ),
        "grammar_type": "iching",
        "cover_image_url": COVER_URL,
        "thumbnail_url": COVER_URL,
        "author": "PlayfulProcess",
        "source": "https://github.com/PlayfulProcess/Recursive-iching",
        "license": "Public domain text (Ten Wings, Warring States–Han); compilation CC0",
        "_image_provenance": [
            {
                "used_as": ["cover_image_url", "thumbnail_url"],
                "url": COVER_URL,
                "title": "The teaching Confucius",
                "creator": "Attributed to Wu Daozi 吳道子 (c. 685–758), Tang dynasty",
                "date": "8th century (Commons dates the work c. 750)",
                "file_page": "https://commons.wikimedia.org/wiki/File:Confucius_Tang_Dynasty.jpg",
                "pd_basis": "PD-old — the artist died in the 8th century, so the work is public domain worldwide (life + 100 years and then some), and it was published long before 1 Jan 1930 (PD-US). Commons licence tag on the file page: Public domain.",
                "verified_on": "2026-07-26",
                "why_this_image": "The Ten Wings are the commentarial stratum traditionally ascribed to Confucius — an ascription modern scholarship rejects but which is exactly what this layer of the book meant to its readers for two thousand years. The portrait illustrates the claim, not a fact.",
            },
        ],
        "_i18n": i18n_block(wings),
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
                {"name": "john-walks-slow/open-iching", "date": "fetched 2026-07-16 (文言 2026-07-30)",
                 "note": "Transcription source (simplified characters); only the ancient public-domain text taken; credited with thanks."},
                {"name": "James Legge, The Yî King (Sacred Books of the East vol. XVI)", "date": "1882; 2nd ed. 1899",
                 "note": "The English in sections_i18n.en — his Appendixes I, II, IV and VI. Translator d. 1897 and published well before 1930: public domain. Transcription from sacred-texts.com/ich/, cross-checked against the Internet Archive's scan of the 1882 first edition. Legge's footnotes and commentary were not taken."},
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
