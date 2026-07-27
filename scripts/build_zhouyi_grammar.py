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
  - research/sources/raw/legge-yi-king-text.json (built by scripts/fetch_legge_english.py)
    carries James Legge's English of the same ancient text — Sacred Books of the East vol.
    XVI, translator d. 1897, published 1882/1899: public domain, and the rendering this
    repo has always named as the one that could honestly fill the English slots. It goes
    in as `sections_i18n.en` beside the canonical Chinese, never over it.
    Still excluded: Wilhelm-Baynes (1950), which is not public domain.

The grammars are generated — never hand-edit grammars/zhouyi/grammar.json; edit the
sources or this script, then re-run:  python scripts/build_zhouyi_grammar.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "research" / "sources" / "raw"
OUT = ROOT / "grammars" / "zhouyi" / "grammar.json"

# Public-domain cover, verified 2026-07-26 against its Wikimedia Commons file page.
# Full provenance travels inside the grammar as _image_provenance (below) and is
# registered once, repo-wide, in docs/IMAGES.md. PD ONLY — never add an image whose
# file page you have not opened and read.
COVER_URL = (
    "https://commons.wikimedia.org/wiki/Special:FilePath/"
    "I_Ching_Song_Dynasty_print.jpg?width=800"
)

TRIGRAMS = {  # simplified & traditional → (glyph, pinyin, image)
    "乾": ("☰", "qián", "天 heaven"), "坤": ("☷", "kūn", "地 earth"),
    "震": ("☳", "zhèn", "雷 thunder"), "巽": ("☴", "xùn", "風 wind/wood"),
    "坎": ("☵", "kǎn", "水 water"), "离": ("☲", "lí", "火 fire"), "離": ("☲", "lí", "火 fire"),
    "艮": ("☶", "gèn", "山 mountain"), "兑": ("☱", "duì", "澤 lake"), "兌": ("☱", "duì", "澤 lake"),
}

# Canonical English trigram names — the exact strings recursive.eco's converter
# (iching-conversion.ts TRIGRAM_LOOKUP) resolves. Jul 18 2026: the app reads
# metadata.trigram_above/below by these names; the scholarly chars stay in
# trigram_lower/upper alongside.
FLOW_TRIGRAM = {
    "乾": "heaven", "坤": "earth", "震": "thunder", "巽": "wind",
    "坎": "water", "离": "fire", "離": "fire", "艮": "mountain",
    "兑": "lake", "兌": "lake",
}


def add_canonical_sections(items):
    """Jul 18 2026 — canonical-format alignment with recursive.eco (the flow app).

    The app's converter reads ONLY canonical keys: sections `Judgment` /
    `Line 1`..`Line 6`, metadata `number`/`binary`/`chinese_name`/
    `trigram_above`/`trigram_below`. Our scholarly section names (卦辞/爻辞)
    are the book's identity and STAY; this adds canonical duplicates so the
    same grammar renders fully in the app. Runs AFTER apply_corrections so
    corrected text flows into the canonical copies too. setdefault: a
    correction that already wrote a canonical key is never clobbered."""
    for it in items:
        s = it["sections"]
        if "卦辞 · Judgment (original)" in s:
            s.setdefault("Judgment", s["卦辞 · Judgment (original)"])
        blob = s.get("爻辞 · Lines (original)", "")
        line_entries = [ln for ln in blob.split("\n") if ln.strip()]
        for i, ln in enumerate(line_entries[:6], start=1):
            s.setdefault(f"Line {i}", ln)


# The 7th paragraph of hexagrams 1 and 2 is not a line — it is 用九 / 用六, the text for a
# cast in which every line moves. Legge's own words for what it reads off.
SEVENTH = {1: "The use of the number nine", 2: "The use of the number six"}


def add_english(items, legge):
    """Attach James Legge's English as `sections_i18n.en` on every hexagram.

    THE CONVENTION (GRAMMAR_FORMAT.md, "Languages"): an item's `sections` stays the
    canonical text — here the Chinese — and every block under `sections_i18n` mirrors its
    key set exactly, same keys in the same order. A viewer can therefore swap languages
    section for section without knowing anything about this particular book, and a missing
    key is a bug the gate catches rather than a hole a reader discovers.

    That is why the English block repeats the 卦辞/爻辞 key names rather than inventing
    English ones: the key is the *slot*, not the label."""
    by_kw = {h["king_wen"]: h for h in legge["hexagrams"]}
    for it in items:
        kw = it["metadata"]["king_wen"]
        h = by_kw[kw]
        labels = [f"Line {i}" for i in range(1, 7)]
        if len(h["lines"]) == 7:
            labels.append(SEVENTH[kw])
        lines_md = "\n".join(f"**{lab}** — {txt}" for lab, txt in zip(labels, h["lines"]))

        en = {}
        for key in it["sections"]:                      # canonical order, mirrored
            if key == "卦辞 · Judgment (original)":
                en[key] = h["judgment"]
            elif key == "爻辞 · Lines (original)":
                en[key] = lines_md
            elif key == "Research note":
                en[key] = it["sections"][key]           # already English
            elif key == "Judgment":
                en[key] = h["judgment"]
            elif key.startswith("Line "):
                en[key] = f"**{key}** — {h['lines'][int(key.split()[1]) - 1]}"
            else:
                raise SystemExit(
                    f"hexagram {kw}: section '{key}' has no English counterpart — "
                    f"add one here rather than shipping a language block with a hole in it"
                )
        it["sections_i18n"] = {"en": en}


def i18n_block(legge):
    """Root-level provenance for every language in `sections_i18n` — who translated it,
    when, from where, and on what basis it is free. check.py requires all of it."""
    return {
        "canonical_language": "zh-Hans",
        "canonical_note": (
            "Each item's `sections` is the canonical text: the Zhouyi in simplified Chinese. "
            "`sections_i18n` holds translations beside it, never over it — a language block "
            "mirrors the canonical key set exactly. There is no 'zh' block because Chinese "
            "is what `sections` already is."
        ),
        "languages": [
            {
                "lang": "en",
                "name": "English",
                "translator": "James Legge (1815–1897)",
                "year": "1882 (2nd ed. 1899)",
                "work": "The Yî King, Sacred Books of the East vol. XVI (Oxford: Clarendon Press)",
                "source": legge["_transcription_source"],
                "source_url": legge["_transcription_source_url"],
                "pd_basis": legge["_pd_basis"],
                "retrieved_on": legge["_fetched_on"],
                "coverage": (
                    "Complete for this book: all 64 judgments (卦辞) and all 386 line statements "
                    "(爻辞), including the 用九/用六 paragraph of hexagrams 1 and 2."
                ),
                "not_included": legge["_not_taken"],
                "verified": (
                    "Every hexagram matched to its King Wen number by the six-bit figure on the "
                    "source page; 210 passages across hexagrams 1–31 cross-checked word for word "
                    "against English Wikisource's independently proofread transcription of the "
                    "1882 first edition, with no divergence. "
                    "See scripts/fetch_legge_english.py."
                ),
                "built_by": "scripts/fetch_legge_english.py → scripts/build_zhouyi_grammar.py",
            },
        ],
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
                    "is James Legge's (Sacred Books of the East vol. XVI, 1882/1899 — public "
                    "domain), carried beside the Chinese as sections_i18n.en, not over it; it is "
                    "a Victorian Scot's reading of a Bronze Age manual, and reads like one."
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
                # Canonical keys the recursive.eco converter reads (Jul 18 2026
                # alignment — see add_canonical_sections). The app's binary is
                # bottom-line-first too (index 0 = line 1), so it's a verbatim copy.
                "number": n,
                "binary": binary_bottom_first,
                "chinese_name": trad,
                "trigram_below": FLOW_TRIGRAM[lower],
                "trigram_above": FLOW_TRIGRAM[upper],
            },
        })

    fixed = apply_corrections(items, "zhouyi")
    if fixed: print(f"applied {fixed} correction(s) from corrections.json")
    add_canonical_sections(items)

    # English last: sections_i18n mirrors whatever key set the canonical sections ended up
    # with, so it has to be built after corrections and after the canonical aliases.
    legge = json.loads((RAW / "legge-yi-king-text.json").read_text(encoding="utf-8"))
    add_english(items, legge)

    grammar = {
        "name": "周易 — The Zhouyi (original text)",
        "description": (
            "The 64 hexagrams of the Zhouyi — the core text of the Book of Changes — in the "
            "original language: each hexagram's 卦辞 (judgment) and 爻辞 (line statements), with "
            "structural metadata (King Wen number, trigrams, pinyin, Unicode). The oldest layer "
            "only, presented as what it historically was: a working diviner's manual of the "
            "Western Zhou, before the Ten Wings made it a classic. James Legge's public-domain "
            "English (1882/1899) travels beside the Chinese rather than replacing it. Read to "
            "know yourself, not to be told your fate; relate to the hexagram, never obey it."
        ),
        "grammar_type": "iching",
        # Cover: a page of the book itself, not a mood photograph. See
        # docs/IMAGES.md for the repo's public-domain-only image policy and the
        # _image_provenance shape (GRAMMAR_FORMAT.md, "Image provenance").
        "cover_image_url": COVER_URL,
        "thumbnail_url": COVER_URL,
        "author": "PlayfulProcess",
        "source": "https://github.com/PlayfulProcess/recursive-iching",
        "license": "Public domain text (Zhouyi, Western Zhou); compilation CC0",
        "_image_provenance": [
            {
                "used_as": ["cover_image_url", "thumbnail_url"],
                "url": COVER_URL,
                "title": "A page from a Song Dynasty printed edition of the Yijing",
                "creator": "Unknown Song-era print artist",
                "date": "Song dynasty, 960–1279",
                "file_page": "https://commons.wikimedia.org/wiki/File:I_Ching_Song_Dynasty_print.jpg",
                "pd_basis": "PD-old — anonymous woodblock print from the Song dynasty; far beyond any copyright term, and published long before 1 Jan 1930 (PD-US). Commons licence tag on the file page: Public domain.",
                "verified_on": "2026-07-26",
                "why_this_image": "The Zhouyi grammar is the core text; the apt picture is the text as an actual printed book of its own tradition — the oldest surviving print layer, not a modern photograph of an unrelated volume.",
            },
        ],
        "_i18n": i18n_block(legge),
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
                {"name": "James Legge, The Yî King (Sacred Books of the East vol. XVI)", "date": "1882; 2nd ed. 1899",
                 "note": "The English in sections_i18n.en. Translator d. 1897 and published well before 1930: public domain. Transcription from sacred-texts.com/ich/, cross-checked against English Wikisource's proofread transcription of the 1882 edition. Legge's footnotes and commentary were not taken."},
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
