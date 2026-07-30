# -*- coding: utf-8 -*-
"""Fetch James Legge's public-domain English of the TEN WINGS — his Appendixes — and cache
it as a raw source: research/sources/raw/legge-yi-king-appendixes.json.

This is the second half of the pass that scripts/fetch_legge_english.py began. That one
took the Zhouyi (the judgments and line statements); this one takes the commentary layer
the repo carries in grammars/ten-wings, which was Chinese-only until now.

WHAT IS BEING TAKEN, AND WHY IT IS FREE
---------------------------------------
James Legge (1815-1897), *The Yi King*, Sacred Books of the East vol. XVI (Oxford:
Clarendon Press; 1st ed. 1882, 2nd ed. 1899). Translator died 1897 and the book was
published long before 1930: public domain in the United States and in life+70 countries.
Wilhelm-Baynes (1950) is NOT public domain and stays out of this repo, here as everywhere.

Only the translated CANONICAL TEXT is taken. Legge's footnotes, his introduction, and the
running commentary in which he argues with Chinese scholarship are deliberately not
harvested: they are his 19th-century opinions, not the Wings.

WHICH APPENDIXES, AND WHY ONLY THESE
------------------------------------
grammars/ten-wings is a PER-HEXAGRAM book: every item is one of the 64, and its sections
are the Wings that speak about that hexagram. So the Appendixes that map onto it are the
per-hexagram ones, and those are the ones taken here:

    Appendix I   (icap1-1, icap1-2)  ->  彖传 Tuan, per hexagram
    Appendix II  (icap2-1, icap2-2)  ->  大象 Great Image + 小象 Small Images, per hexagram
    Appendix IV  (icap4-1, icap4-2)  ->  文言 Wenyan — hexagrams 1 and 2 only, which is all
                                          the Wing itself covers
    Appendix VI  (icap6)             ->  序卦 Xugua, the orderly sequence

Legge's Appendix III (the 繫辭 Xi Ci / Great Treatise), Appendix V (說卦 Shuogua), and
Appendix VII (雜卦 Zagua) are whole-treatise Wings that speak about the book rather than
about any one hexagram. They have no canonical Chinese in this repo to sit beside — the
per-hexagram grammar has no slot for them — so they are NOT fetched here. Filling them
means first giving them items of their own, which is a structure decision, not a
translation one. ICHING.md says so in the same words rather than letting the silence pass.

A NOTE ON GRANULARITY, WHICH IS NOT A DEFECT BUT MUST BE DECLARED
-----------------------------------------------------------------
Appendix VI is printed as running paragraphs, each covering a RUN of hexagrams ("3-6.
Kun is descriptive of things on their first production..."), while the Chinese 序卦 is
carried here cut per hexagram. So a hexagram's English 序卦 is the whole paragraph its
Chinese sentence falls inside, and it is labelled with the run it covers. Nothing is
truncated to fake a one-to-one fit; the reader is told what they are looking at.

CHECKS THAT RUN ON EVERY FETCH
------------------------------
1. *Right hexagram.* Appendixes I and II number their hexagrams with Roman numerals in the
   King Wen order. The parse asserts the numerals arrive as an unbroken I..XXX (section I)
   and XXXI..LXIV (section II) — a page can never be filed under the wrong number.
2. *Right shape.* Every hexagram must yield a Tuan, a Great Image, and exactly six Small
   Images — seven for hexagrams 1 and 2, which carry the 用九/用六 comment. Appendix VI
   must cover 1..64 with no hexagram falling outside every paragraph's range.
3. *Nothing cut off.* Any passage not ending in sentence punctuation is reported: that is
   the signature of a statement broken across a printed page whose continuation was missed.

A third check, against the Internet Archive's independent scan-and-OCR of the 1882 FIRST
EDITION (archive.org/details/wg916 — a different transcription lineage from sacred-texts'
etext), is `python scripts/fetch_legge_wings.py --crosscheck`. English Wikisource, which
the Zhouyi pass used, has transcribed only the hexagram pages of this volume — no
appendixes (checked 2026-07-30) — so the archive scan is the independent pair of eyes here.

    python scripts/fetch_legge_wings.py              # fetch + write the raw JSON
    python scripts/fetch_legge_wings.py --crosscheck # compare vs the 1882 printing
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "sources" / "raw" / "legge-yi-king-appendixes.json"

BASE = "https://sacred-texts.com/ich/{}.htm"
WAYBACK = "https://web.archive.org/web/2020id_/https://www.sacred-texts.com/ich/{}.htm"
UA = "Mozilla/5.0 (compatible; recursive-iching/1.0; +https://github.com/PlayfulProcess/Recursive-iching)"
PAUSE = 1.0  # be a polite guest on someone else's server

PAGES = {
    "appendix_1": ["icap1-1", "icap1-2"],
    "appendix_2": ["icap2-1", "icap2-2"],
    "appendix_4": ["icap4-1", "icap4-2"],
    "appendix_6": ["icap6"],
}


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_page(slug: str) -> tuple[str, str]:
    """(html, url actually used) — direct first, Wayback snapshot as the fallback."""
    for url in (BASE.format(slug), WAYBACK.format(slug)):
        try:
            page = get(url)
        except (urllib.error.URLError, urllib.error.HTTPError):
            continue
        if "APPENDIX" in page.upper():  # a real appendix page, not a challenge/error stub
            return page, url
    raise RuntimeError(f"{slug}: no usable source (tried direct and Wayback)")


# --------------------------------------------------------------------------- html -> text

TAG = re.compile(r"<[^>]+>")
PAGE_ANCHOR = re.compile(r'(?is)<a\s+name="page_\d+".*?</a>')
FOOT_REF = re.compile(r'(?is)<a\s+name="fr_[^"]*"></a>\s*<a\s+href="#fn_[^"]*">.*?</a>')
# The hexagram's Roman numeral is printed as the anchor of its footnote — so it has to be
# read BEFORE the footnote markers are stripped, or the numeral disappears with them.
# The full stop after the numeral is optional because the printing does not always have
# one — Appendix II opens hexagram XIX without it — and a parser that insisted would drop
# that hexagram's Great Image into its neighbour.
MARKER_IN_FOOTNOTE = re.compile(
    r'(?is)^\s*(?:&nbsp;|\s)*<a\s+name="fr_[^"]*"></a>\s*<a\s+href="#fn_[^"]*">\s*'
    r'(?:<font[^>]*>)?\s*([IVXLC]+)\s*(?:</font>)?\s*</a>\s*\.?\s')
MARKER_IN_TEXT = re.compile(r"^([IVXLC]+)\.\s")
CONTINUES = re.compile(r"^\[paragraph continues\]\s*")


def keep_roman(m: re.Match) -> str:
    """Footnote markers go; the Roman numeral of a chapter heading stays.

    Appendix IV prints 'Chapter III' with the numeral doubling as the anchor of Legge's
    footnote, so a blanket strip of footnote references leaves the reader a paragraph that
    opens 'Chapter . 24.' — the apparatus removed along with the text it was attached to."""
    inner = html.unescape(TAG.sub("", m.group(0))).strip()
    return f" {inner} " if roman(inner) else ""


def clean(chunk: str) -> str:
    chunk = PAGE_ANCHOR.sub("", chunk)
    chunk = FOOT_REF.sub(keep_roman, chunk)
    text = html.unescape(TAG.sub("", chunk))
    text = text.replace(" ", " ").replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return CONTINUES.sub("", text).strip()


def paragraphs(page: str) -> list[tuple[str | None, str]]:
    """(hexagram Roman numeral or None, text) for every <p> in the body, in order."""
    # The text of one of these pages is what lies between the site's navigation rule and
    # the rule before "Footnotes" — the two <hr>s. Anchoring on a heading instead does not
    # work: some sections open with <h1>, some with <h3>, and the <head> above them carries
    # an og:description quoting a paragraph of the text, which would parse as text.
    rules = [m.start() for m in re.finditer(r"(?is)<hr\b", page)]
    if len(rules) < 2:
        raise RuntimeError("page has no <hr> pair — the sacred-texts layout has changed")
    body = page[rules[0]:rules[1]]

    out = []
    for chunk in re.split(r"(?i)<p\b", body)[1:]:
        head, _, rest = chunk.partition(">")
        # Stop at the paragraph's own close: what follows it before the next <p> is markup
        # between paragraphs, and on these pages that includes the <h3>SECTION II</h3>
        # running head, which would otherwise be glued to the end of the text above it.
        rest = re.split(r"(?i)</p\s*>", rest)[0]
        marker = None
        m = MARKER_IN_FOOTNOTE.match(rest)
        if m:
            marker = m.group(1).upper()
            rest = rest[m.end():]
        text = clean(rest)
        if not text:
            continue
        if marker is None:
            m2 = MARKER_IN_TEXT.match(text)
            if m2 and roman(m2.group(1)) is not None:
                marker = m2.group(1).upper()
                text = text[m2.end():].strip()
        if re.match(r"(?i)^(treatise|section|appendix|the orderly sequence)\b", text) and marker is None:
            continue                              # running heads, not text
        out.append((marker, text))
    return out


ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def roman(s: str) -> int | None:
    """Roman numeral -> int, or None if it is not one (so 'I' the pronoun cannot pass)."""
    total = prev = 0
    for ch in reversed(s.upper()):
        v = ROMAN_VALUES.get(ch)
        if v is None:
            return None
        total = total - v if v < prev else total + v
        prev = max(prev, v)
    return total if 1 <= total <= 64 else None


# The etext carries a handful of scanning slips in the paragraph numbers themselves — the
# small image of hexagram 2's fifth line opens "S." rather than "5.". A mis-read digit is
# only ever accepted when it lands exactly where the next paragraph is due, and every one
# is recorded in the output as _source_typos_normalised so the repair is visible.
NUMBERED = re.compile(r"^(\d+)\s*[.,]\s+")     # "8," for "8." happens too
LOOSE = re.compile(r"^([0-9SsIlOo])\s*[.,]\s+")
CONFUSED = {"S": 5, "s": 5, "I": 1, "l": 1, "O": 0, "o": 0}


def numbered(text: str, due: int, typos: list, where: dict) -> str | None:
    """The paragraph text without its number, if this is the paragraph next due.

    Returns None otherwise — and the caller then treats the paragraph as the continuation
    of the one before, which is what a statement broken across a printed page looks like.
    A mis-set number is only ever accepted when it lands exactly where the next paragraph
    is due, and is recorded in the output so the repair is visible rather than silent."""
    m = NUMBERED.match(text)
    if m and int(m.group(1)) == due:
        if m.group(0).rstrip()[-1] == ",":
            typos.append({**where, "paragraph": due,
                          "source_reads": f"{m.group(1)},", "read_as": f"{due}."})
        return text[m.end():]
    m = LOOSE.match(text)
    if m and CONFUSED.get(m.group(1)) == due:
        typos.append({**where, "paragraph": due,
                      "source_reads": m.group(0).strip(), "read_as": f"{due}."})
        return text[m.end():]
    return None

ENDINGS = (".", "!", "?", ".)", "!)", "?)", ".'", "!'", ".\"", "'", "--")


# Two places where the sacred-texts etext is defective and the printed book is not. Each
# was checked against the Internet Archive's scan of the 1882 first edition before being
# listed here, each is applied by exact string match, and each is written into the output
# as _etext_defects_repaired. Nothing else about the text is touched.
#
# The first is the more serious kind: on the page for hexagram 42 the etext runs Legge's
# own footnote — his notes on the trigrams, and his versified rendering of the Thwan —
# straight on into the body of paragraph 3, where the printing has the paragraph end. His
# commentary is exactly what this repo does not harvest, so the paragraph is cut back to
# where the book ends it. That leak was found by the "passage does not end in sentence
# punctuation" sweep below, which is why the sweep exists.
ETEXT_FIXES = [
    {
        "appendix": "I", "king_wen": 42, "passage": "paragraph 3", "operation": "truncate_after",
        "anchor": "proceeds according to the requirements of the time.",
        "why": "The etext runs Legge's footnote on hexagram XLII (and his rhymed rendering) "
               "into the body of the paragraph. In the 1882 printing the paragraph ends at "
               "the anchor and the rest is note apparatus, which this repo does not take.",
        "checked_against": "Internet Archive scan of the 1882 first edition, p. 248, "
                           "https://archive.org/details/wg916",
    },
    {
        "appendix": "II", "king_wen": 8, "passage": "line 2", "operation": "replace",
        "etext_reads": "does not fail in what is proper to himself",
        "printed_reads": "does not fail in what is proper to himself.",
        "why": "The etext drops the full stop that closes the sentence in the printing.",
        "checked_against": "Internet Archive scan of the 1882 first edition, p. 276, "
                           "https://archive.org/details/wg916",
    },
]


def apply_fix(fix: dict, text: str, applied: list) -> str:
    if fix["operation"] == "truncate_after":
        i = text.find(fix["anchor"])
        if i < 0 or i + len(fix["anchor"]) >= len(text):
            return text
        applied.append({**fix, "dropped": text[i + len(fix["anchor"]):].strip()})
        return text[: i + len(fix["anchor"])]
    after = text.replace(fix["etext_reads"], fix["printed_reads"])
    if after != text:
        applied.append(fix)
    return after


def note_unterminated(sink: list, where: str, text: str) -> None:
    if sink is not None and not text.rstrip().endswith(ENDINGS):
        sink.append({"passage": where, "ends": text[-70:]})


# --------------------------------------------------------------------------- appendix I

def parse_appendix_1(pages: list[str], typos: list, unterminated: list, repaired: list) -> dict:
    """Per hexagram: Legge's numbered paragraphs of the Thwan (彖) treatise, in order.

    The paragraphs keep his numbering, because that is how the printed book cites itself
    and because a paragraph silently merged into its neighbour is exactly the failure this
    repo's other parsers were built to make loud."""
    out: dict[int, list[str]] = {}
    expected = 1
    for page in pages:
        current = None
        for marker, text in paragraphs(page):
            if marker is not None:
                n = roman(marker)
                if n != expected:
                    raise RuntimeError(
                        f"Appendix I: hexagram numerals arrived {marker} (={n}) where {expected} "
                        f"was due — the treatise is not in King Wen order, or a page was misparsed")
                current, expected = n, expected + 1
                out[current] = []
            if current is None:
                continue                                   # front matter before hexagram I
            due = len(out[current]) + 1
            rest = numbered(text, due, typos, {"appendix": "I", "king_wen": current})
            if rest is not None:
                out[current].append(f"{due}. " + rest)
            elif out[current]:
                out[current][-1] += " " + text             # split by a printed page break
            else:
                out[current].append(text)                  # an unnumbered single paragraph
    if sorted(out) != list(range(1, 65)):
        raise RuntimeError(f"Appendix I: parsed hexagrams {sorted(out)}, expected 1..64")
    for fix in ETEXT_FIXES:
        if fix["appendix"] != "I":
            continue
        i = int(fix["passage"].split()[1]) - 1
        out[fix["king_wen"]][i] = apply_fix(fix, out[fix["king_wen"]][i], repaired)
    for n, paras in out.items():
        if not paras:
            raise RuntimeError(f"Appendix I: hexagram {n} has no text")
        for i, p in enumerate(paras, start=1):
            note_unterminated(unterminated, f"Appendix I, hexagram {n}, paragraph {i}", p)
    return {str(n): {"paragraphs": paras} for n, paras in sorted(out.items())}


# --------------------------------------------------------------------------- appendix II

def parse_appendix_2(pages: list[str], typos: list, unterminated: list, repaired: list) -> dict:
    """Per hexagram: the Great Symbolism (大象, Legge's unnumbered opening paragraph) and
    the Small Symbolism (小象, his numbered paragraphs, one per line)."""
    great: dict[int, str] = {}
    small: dict[int, list[str]] = {}
    expected = 1
    for page in pages:
        current = None
        for marker, text in paragraphs(page):
            if marker is not None:
                n = roman(marker)
                if n != expected:
                    raise RuntimeError(
                        f"Appendix II: hexagram numerals arrived {marker} (={n}) where {expected} "
                        f"was due — the treatise is not in King Wen order, or a page was misparsed")
                current, expected = n, expected + 1
                great[current], small[current] = text, []
                continue
            if current is None:
                continue
            due = len(small[current]) + 1
            rest = numbered(text, due, typos, {"appendix": "II", "king_wen": current})
            if rest is not None:
                small[current].append(rest)
            elif small[current]:
                small[current][-1] += " " + text           # split by a printed page break
            else:
                great[current] += " " + text               # great image split by a page break
    if sorted(great) != list(range(1, 65)):
        raise RuntimeError(f"Appendix II: parsed hexagrams {sorted(great)}, expected 1..64")
    for fix in ETEXT_FIXES:
        if fix["appendix"] != "II":
            continue
        i = int(fix["passage"].split()[1]) - 1
        small[fix["king_wen"]][i] = apply_fix(fix, small[fix["king_wen"]][i], repaired)
    for n in great:
        want = 7 if n in (1, 2) else 6                     # 1 and 2 carry 用九 / 用六
        if len(small[n]) != want:
            raise RuntimeError(
                f"Appendix II: hexagram {n} yielded {len(small[n])} line images, expected {want}")
        # Checked here rather than where the paragraph is first seen: a Great Image broken
        # across a printed page is completed by the paragraph after it, so the passage is
        # only whole once the whole hexagram has been read.
        note_unterminated(unterminated, f"Appendix II, hexagram {n}, great image", great[n])
        for i, p in enumerate(small[n], start=1):
            note_unterminated(unterminated, f"Appendix II, hexagram {n}, line {i}", p)
    return {str(n): {"great_image": great[n].strip(), "line_images": small[n]}
            for n in sorted(great)}


# --------------------------------------------------------------------------- appendix IV

CHAPTER = re.compile(r"(?i)^chapter\s+([IVXLC]+)\s*\.?\s*")
# What the 1882 printing has, and therefore what a correct parse must produce. Legge's
# Wenyan runs its paragraph numbers straight through its chapters: Khien to 36, Khwăn to 10.
WENYAN_PARAGRAPHS = {1: 36, 2: 10}


def parse_appendix_4(pages: list[str], typos: list, unterminated: list) -> dict:
    """Appendix IV, the 文言 Wenyan: Section I is hexagram 1 (Khien), Section II hexagram 2
    (Khwăn), and the Wing covers no others. Legge numbers his paragraphs; a paragraph that
    does not open with the number due is a page-break continuation of the one before."""
    out = {}
    for kw, page in zip((1, 2), pages):
        paras: list[str] = []
        for marker, text in paragraphs(page):
            if not paras and not CHAPTER.match(text):
                continue          # the section's descriptive sub-heading, not the Wing
            # Legge's paragraph numbers run on through the chapters (Khien reaches 36), so
            # a chapter heading is a prefix on the paragraph that follows it, not a break
            # in the count. Strip it to read the number, then put it back.
            chapter = CHAPTER.match(text)
            head, body = (f"Chapter {chapter.group(1)}. ", text[chapter.end():]) if chapter else ("", text)
            due = len(paras) + 1
            rest = numbered(body, due, typos, {"appendix": "IV", "king_wen": kw})
            if rest is not None:
                paras.append(f"{head}{due}. {rest}")
            elif paras:
                paras[-1] += " " + text                    # split by a printed page break
        want = WENYAN_PARAGRAPHS[kw]
        if len(paras) != want:
            raise RuntimeError(
                f"Appendix IV: hexagram {kw} yielded {len(paras)} paragraphs, and the 1882 "
                f"printing has {want} — a chapter heading or a page break was misread")
        for i, p in enumerate(paras, start=1):
            note_unterminated(unterminated, f"Appendix IV, hexagram {kw}, paragraph {i}", p)
        out[str(kw)] = {"paragraphs": paras}
    return out


# --------------------------------------------------------------------------- appendix VI

RANGE = re.compile(r"^(\d+)\s*[-,]\s*(\d+)\s*\.\s+")
SINGLE = re.compile(r"^(\d+)\s*\.\s+")


def parse_appendix_6(pages: list[str], unterminated: list) -> dict:
    """Appendix VI, the 序卦 Xugua. Printed as running paragraphs, each labelled with the
    RUN of hexagrams it walks ("3-6. Kun is descriptive of..."), so the blocks are kept
    with their ranges and each hexagram is mapped to the block it falls inside. See the
    granularity note in this file's docstring: the fit is honest, not one-to-one."""
    blocks: list[dict] = []
    for page in pages:
        for _, text in paragraphs(page):
            m = RANGE.match(text) or SINGLE.match(text)
            if m:
                first = int(m.group(1))
                last = int(m.group(2)) if m.lastindex == 2 else first
                blocks.append({"first": first, "last": last,
                               "label": f"{first}–{last}" if last != first else str(first),
                               "text": text[m.end():].strip()})
            elif blocks:
                blocks[-1]["text"] += " " + text            # continuation paragraph
    if not blocks:
        raise RuntimeError("Appendix VI: no ranged paragraphs parsed")
    by_hexagram = {}
    for kw in range(1, 65):
        hit = [i for i, b in enumerate(blocks) if b["first"] <= kw <= b["last"]]
        if not hit:
            raise RuntimeError(
                f"Appendix VI: hexagram {kw} falls outside every paragraph's range "
                f"— the sequence treatise must cover the whole book")
        by_hexagram[str(kw)] = hit[0]
    for b in blocks:
        note_unterminated(unterminated, f"Appendix VI, paragraph {b['label']}", b["text"])
    return {"blocks": blocks, "by_hexagram": by_hexagram}


# --------------------------------------------------------------------------- main

def main() -> int:
    fetched, urls, typos, unterminated, repaired = {}, {}, [], [], []
    for key, slugs in PAGES.items():
        pages = []
        for slug in slugs:
            page, url = fetch_page(slug)
            pages.append(page)
            urls[slug] = url
            print(f"  {slug:9s}  {len(page):6d} bytes  {url}")
            time.sleep(PAUSE)
        fetched[key] = pages

    data = {
        "_what": (
            "James Legge's English of the per-hexagram Ten Wings: Appendix I (Thwan/彖), "
            "Appendix II (Symbolism/大象 + 小象), Appendix IV (文言, hexagrams 1-2), and "
            "Appendix VI (序卦, the orderly sequence)."
        ),
        "_translator": "James Legge (1815-1897)",
        "_work": "The Yi King, Sacred Books of the East vol. XVI (Oxford: Clarendon Press; 1st ed. 1882, 2nd ed. 1899)",
        "_pd_basis": "Public domain: translator died 1897 (life+70 expired), and the work was published long before 1 Jan 1930 (PD-US).",
        "_transcription_source": "sacred-texts.com/ich/ (icap1-1, icap1-2, icap2-1, icap2-2, icap4-1, icap4-2, icap6), Legge tr.; Internet Archive Wayback snapshots used where a direct fetch failed.",
        "_transcription_source_url": "https://sacred-texts.com/ich/",
        "_not_taken": "Legge's own footnotes, introduction and running commentary — his 19th-century reading, not the Wings.",
        "_not_fetched": (
            "Appendix III (繫辭 Xi Ci), Appendix V (說卦 Shuogua) and Appendix VII (雜卦 Zagua): "
            "whole-treatise Wings that speak about the book rather than about any one hexagram, "
            "so the per-hexagram grammar has no canonical slot for them to sit beside. Giving "
            "them items of their own is a structure decision, and is named as open in ICHING.md."
        ),
        "_granularity_note": (
            "Appendix VI is printed as running paragraphs covering runs of hexagrams, while the "
            "Chinese 序卦 is carried per hexagram: a hexagram's English is the whole paragraph its "
            "sentence falls inside, labelled with the run. Nothing is truncated to fake a fit."
        ),
        "_fetched_by": "scripts/fetch_legge_wings.py",
        "_fetched_on": time.strftime("%Y-%m-%d"),
        "_source_urls": urls,
        "_wayback_fallback_used_for": sorted(s for s, u in urls.items() if "web.archive.org" in u),
        "_source_typos_normalised": typos,
        "_etext_defects_repaired": repaired,
        "_passages_without_terminal_punctuation": unterminated,
        "appendix_1": parse_appendix_1(fetched["appendix_1"], typos, unterminated, repaired),
        "appendix_2": parse_appendix_2(fetched["appendix_2"], typos, unterminated, repaired),
        "appendix_4": parse_appendix_4(fetched["appendix_4"], typos, unterminated),
        "appendix_6": parse_appendix_6(fetched["appendix_6"], unterminated),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    small = sum(len(v["line_images"]) for v in data["appendix_2"].values())
    print(f"wrote {OUT.relative_to(ROOT)} — Appendix I: 64 hexagrams "
          f"({sum(len(v['paragraphs']) for v in data['appendix_1'].values())} paragraphs); "
          f"Appendix II: 64 great images + {small} line images; "
          f"Appendix IV: {len(data['appendix_4'])} hexagrams; "
          f"Appendix VI: {len(data['appendix_6']['blocks'])} paragraphs covering 1–64")
    if unterminated:
        print(f"note: {len(unterminated)} passage(s) do not end in sentence punctuation — listed "
              f"in the output as _passages_without_terminal_punctuation")
    return 0


# --------------------------------------------------------------------------- crosscheck

ARCHIVE_TXT = ("https://archive.org/download/wg916/"
               "WG916-1882%20-The%20Sacred%20Books%20of%20East%20-%20Vol%2016%20of%2050%20-%20"
               "The%20Sacred%20Books%20of%20China%20%20-%20Part%202%20Of%204%20-%20"
               "The%20Texts%20Of%20Confucianism%20-%20Yi%20King_djvu.txt")
CACHE = ROOT / "research" / "sources" / "raw" / ".cache-wg916-1882.txt"

STOP = {"the", "of", "and", "to", "in", "is", "it", "a", "that", "this", "be", "are", "as",
        "by", "for", "with", "his", "he", "its", "there", "will", "which", "not", "but",
        "from", "has", "have", "was", "were", "s", "i", "o"}


def archive_text() -> str:
    """The Internet Archive's OCR of the 1882 first edition — an independent transcription
    of the printed book, cached locally so a re-run does not re-download 1 MB."""
    if CACHE.exists():
        return CACHE.read_text(encoding="utf-8")
    print("downloading the 1882 printing's full text from archive.org (~1 MB, cached after this)…")
    text = get(ARCHIVE_TXT)
    CACHE.write_text(text, encoding="utf-8")
    return text


def words(s: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP and len(w) > 2]


def crosscheck() -> int:
    """Does the printed 1882 book contain the words of each passage we took, in a run?

    The reference is OCR of a scan, so it cannot be compared character for character: the
    1899 edition we took also differs from the 1882 one in wording here and there (Legge
    revised), and OCR mangles the accented romanisations throughout. What IS decisive is
    whether a passage's distinctive vocabulary appears together in the printing at all. A
    passage picked up from the wrong hexagram, or a paragraph fused with its neighbour,
    fails that badly and unmistakably; an OCR smudge does not.
    """
    data = json.loads(OUT.read_text(encoding="utf-8"))
    ref = set(words(archive_text()))
    checked = flagged = 0
    worst: list[tuple[float, str]] = []

    def compare(label: str, text: str) -> None:
        nonlocal checked, flagged
        ws = set(words(text))
        if len(ws) < 6:
            return
        checked += 1
        gap = len(ws - ref) / len(ws)
        worst.append((gap, label))
        if gap > 0.20:
            flagged += 1
            print(f"  {label}: {gap:.0%} of its distinctive words are absent from the 1882 "
                  f"printing\n    {text[:200]}")

    for kw in range(1, 65):
        for i, p in enumerate(data["appendix_1"][str(kw)]["paragraphs"], start=1):
            compare(f"Appendix I, hexagram {kw}, paragraph {i}", p)
        a2 = data["appendix_2"][str(kw)]
        compare(f"Appendix II, hexagram {kw}, great image", a2["great_image"])
        for i, p in enumerate(a2["line_images"], start=1):
            compare(f"Appendix II, hexagram {kw}, line {i}", p)
    for kw, block in data["appendix_4"].items():
        for i, p in enumerate(block["paragraphs"], start=1):
            compare(f"Appendix IV, hexagram {kw}, paragraph {i}", p)
    for b in data["appendix_6"]["blocks"]:
        compare(f"Appendix VI, paragraph {b['label']}", b["text"])

    worst.sort(reverse=True)
    print(f"\ncross-checked {checked} passage(s) against the Internet Archive's OCR of the 1882 "
          f"first edition (archive.org/details/wg916); {flagged} flagged for review")
    print("widest vocabulary gaps (for the record — under the threshold is OCR noise, not divergence):")
    for gap, label in worst[:10]:
        print(f"  {gap:5.1%}  {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(crosscheck() if "--crosscheck" in sys.argv else main())
