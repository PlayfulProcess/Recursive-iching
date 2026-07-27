# -*- coding: utf-8 -*-
"""Fetch James Legge's public-domain English of the Zhouyi text and cache it as a raw
source: research/sources/raw/legge-yi-king-text.json.

WHAT IS BEING TAKEN, AND WHY IT IS FREE
---------------------------------------
James Legge (1815-1897), *The Yi King*, Sacred Books of the East vol. XVI (Oxford:
Clarendon Press; 1st ed. 1882, 2nd ed. 1899). The translator died in 1897 and the book
was published well before 1930: public domain in the United States (pre-1930
publication) and in life+70 countries (author d. 1897). This is the rendering ICHING.md
has always named as the one that could honestly fill the English slots — as opposed to
Wilhelm-Baynes (1950), which is NOT public domain and stays out of this repo.

Only the TRANSLATED TEXT is taken: the 卦辞 (king Wăn's judgment) and the 爻辞 (the duke
of Kâu's line statements). Legge's own footnotes and commentary are deliberately not
harvested — they are his 19th-century opinions, not the book.

SOURCE OF THE TRANSCRIPTION
---------------------------
sacred-texts.com/ich/ (Evinity/John Bruno Hare's etext of Legge, one page per hexagram,
ic01.htm .. ic64.htm). The markup is theirs; the words are Legge's and are public domain.
If a direct fetch is blocked, the script falls back to the Internet Archive's Wayback
snapshot of the same page — an archive, not a workaround for any access control.

TWO INDEPENDENT CHECKS RUN ON EVERY FETCH
-----------------------------------------
1. *Right hexagram.* Each page embeds img/hex<six bits>.jpg, written top line first.
   Reversed it must equal the hexagram's binary_bottom_first in grammars/zhouyi — so a
   page can never be filed under the wrong King Wen number.
2. *Right shape.* Every hexagram must yield a non-empty judgment and exactly six line
   statements — seven for 1 and 2, which carry 用九/用六. A parse that drifts fails loud.

A third check, against the independently proofread English Wikisource transcription of
the 1882 first edition, is `python scripts/fetch_legge_english.py --crosscheck`.

    python scripts/fetch_legge_english.py              # fetch + write the raw JSON
    python scripts/fetch_legge_english.py --crosscheck # compare vs Wikisource 1-31
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
OUT = ROOT / "research" / "sources" / "raw" / "legge-yi-king-text.json"
ZHOUYI = ROOT / "grammars" / "zhouyi" / "grammar.json"

BASE = "https://sacred-texts.com/ich/ic{:02d}.htm"
WAYBACK = "https://web.archive.org/web/2020id_/https://www.sacred-texts.com/ich/ic{:02d}.htm"
UA = "Mozilla/5.0 (compatible; recursive-iching/1.0; +https://github.com/PlayfulProcess/Recursive-iching)"
PAUSE = 1.0  # be a polite guest on someone else's server


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_page(n: int) -> tuple[str, str]:
    """(html, url actually used) — direct first, Wayback snapshot as the fallback."""
    for url in (BASE.format(n), WAYBACK.format(n)):
        try:
            page = get(url)
        except (urllib.error.URLError, urllib.error.HTTPError):
            continue
        if "img/hex" in page:  # a real chapter page, not a challenge/error stub
            return page, url
    raise RuntimeError(f"hexagram {n}: no usable source (tried direct and Wayback)")


TAG = re.compile(r"<[^>]+>")
PAGE_ANCHOR = re.compile(r'(?is)<a\s+name="page_\d+".*?</a>')
FOOT_REF = re.compile(r'(?is)<a\s+name="fr_[^"]*"></a>\s*<a\s+href="#fn_[^"]*">.*?</a>')


def clean(chunk: str) -> str:
    chunk = PAGE_ANCHOR.sub("", chunk)
    chunk = FOOT_REF.sub("", chunk)
    text = html.unescape(TAG.sub("", chunk))
    text = text.replace(" ", " ").replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


NUMBERED = re.compile(r"^(\d+)\s*\.\s+")   # "2 ." for "2." happens too
# The etext carries a few scanning slips in the paragraph numbers themselves — hexagram 6
# opens its fifth line "S." rather than "5.". A mis-read digit is only ever accepted when
# it lands exactly where the next paragraph is due, and every one is recorded in the
# output as _source_typos_normalised so the repair is visible rather than silent.
LOOSE = re.compile(r"^([0-9SsIlOo])\s*\.\s+")
CONFUSED = {"S": 5, "s": 5, "I": 1, "l": 1, "O": 0, "o": 0}
# …and in a few places the number is missing altogether (hexagram 8's third line opens
# "In the third SIX, divided, …" with no "3."). Legge names the line's position in the
# first words of every such paragraph, so the ordinal itself identifies it — again only
# accepted when it is exactly the paragraph next due.
# The leading article is REQUIRED. Without it this rule also fires on the tail of a
# statement broken across a printed page — "second line). Through his firm correctness…"
# (hexagram 19) — swallowing the continuation and truncating the line above it. That bug
# was caught by the Wikisource cross-check below, which is why the cross-check exists.
ORDINAL = re.compile(
    r"^(?:In the|The)\s+(first|second|third|fourth|fifth|sixth|topmost)\s+"
    r"(?:\([^)]*\)\s+)?(?:line|six|nine)\b", re.I)
ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "topmost": 6}


# Two places where the etext itself is defective and the printed book is not. Each was
# checked against an independent transcription of the 1882 first edition before being
# listed here, each is applied by exact string replacement, and each is written into the
# output as _etext_defects_repaired. Nothing else about the text is touched.
#
# NOT in this table, deliberately: hexagram 29's judgment reads "through which the mind
# is. penetrating." Both transcriptions carry that stray full stop, so it is the printed
# book's own and stays.
ETEXT_FIXES = [
    {"king_wen": 17, "passage": "line 3",
     "etext_reads": "and lets go. the little boy", "printed_reads": "and lets go the little boy",
     "checked_against": "English Wikisource, proofread transcription of the 1882 first edition, "
                        "https://en.wikisource.org/wiki/Sacred_Books_of_the_East/Volume_16/Hexagram_17"},
    {"king_wen": 41, "passage": "line 2",
     "etext_reads": "without taking from himself", "printed_reads": "without taking from himself.",
     "checked_against": "Internet Archive scan of the 1882 first edition, page 147, "
                        "https://archive.org/details/wg916"},
]


def apply_etext_fixes(rec: dict, applied: list) -> None:
    for fix in ETEXT_FIXES:
        if fix["king_wen"] != rec["king_wen"]:
            continue
        i = int(fix["passage"].split()[1]) - 1
        before = rec["lines"][i]
        after = before.replace(fix["etext_reads"], fix["printed_reads"])
        if after != before:
            rec["lines"][i] = after
            applied.append(fix)


def parse(page: str, n: int, typos: list | None = None, unterminated: list | None = None) -> dict:
    """Judgment + line statements out of one sacred-texts chapter page."""
    m = re.search(r'img/hex([01]{6})\.jpg', page)
    if not m:
        raise RuntimeError(f"hexagram {n}: no hexagram image on the page")
    img_binary_top_first = m.group(1)

    body = page[m.end():]
    end = re.search(r"(?is)<hr\b", body)          # the rule before "Footnotes"
    if end:
        body = body[: end.start()]

    judgment_parts: list[str] = []
    lines: dict[int, str] = {}
    last = None
    for chunk in re.split(r"(?i)<p\b", body)[1:]:
        head, _, rest = chunk.partition(">")
        if re.search(r'(?i)align\s*=\s*"?center', head):
            continue                              # "Explanation of the entire figure by…"
        text = clean(rest)
        if not text or text.startswith("Explanation of the"):
            continue
        num = NUMBERED.match(text)
        loose = None if num else LOOSE.match(text)
        if loose and CONFUSED.get(loose.group(1)) == (last or 0) + 1:
            last = CONFUSED[loose.group(1)]
            lines[last] = LOOSE.sub("", text)
            if typos is not None:
                typos.append({"king_wen": n, "paragraph": last,
                              "source_reads": loose.group(1) + ".", "read_as": f"{last}."})
        elif num:
            last = int(num.group(1))
            lines[last] = NUMBERED.sub("", text)
        elif last is None and not judgment_parts:
            judgment_parts.append(text)           # king Wăn's judgment
        elif (ORDINAL.match(text)
              and ORDINALS[ORDINAL.match(text).group(1).lower()] == (last or 0) + 1):
            last = ORDINALS[ORDINAL.match(text).group(1).lower()]
            lines[last] = text
            if typos is not None:
                typos.append({"king_wen": n, "paragraph": last, "source_reads": "(no number)",
                              "read_as": f"{last}. — identified by the ordinal Legge names in it"})
        elif last is None:
            judgment_parts.append(text)           # judgment continued across a page break
        else:
            lines[last] += " " + text             # a line statement split by a page break

    judgment = " ".join(judgment_parts).strip()
    expected = 7 if n in (1, 2) else 6            # 1 and 2 carry 用九 / 用六
    if not judgment:
        raise RuntimeError(f"hexagram {n}: no judgment parsed")
    if sorted(lines) != list(range(1, expected + 1)):
        raise RuntimeError(f"hexagram {n}: parsed line numbers {sorted(lines)}, expected 1..{expected}")

    # A passage not ending in sentence punctuation is the signature of a statement cut off
    # at a printed page break whose continuation was missed. The Wikisource cross-check
    # only reaches hexagrams 1-31, so this sweep covers the other half of the book. It
    # reports rather than fails, because the one hit it produces (41.2) turned out on
    # inspection of the 1882 printing to be a full stop the etext dropped rather than a
    # lost clause — see ETEXT_FIXES. The report is what sent someone to look.
    ENDINGS = (".", "!", "?", ".)", "!)", "?)", ".'", "!'")
    if unterminated is not None:
        passages = [("judgment", judgment)] + [(f"line {i}", t) for i, t in sorted(lines.items())]
        for label, passage in passages:
            if not passage.rstrip().endswith(ENDINGS):
                unterminated.append({"king_wen": n, "passage": label, "ends": passage[-60:]})

    return {
        "king_wen": n,
        "img_binary_top_first": img_binary_top_first,
        "binary_bottom_first": img_binary_top_first[::-1],
        "judgment": judgment,
        "lines": [lines[i] for i in range(1, expected + 1)],
    }


def main() -> int:
    zhouyi = json.loads(ZHOUYI.read_text(encoding="utf-8"))
    by_kw = {it["metadata"]["king_wen"]: it for it in zhouyi["items"]}

    hexagrams, urls, typos, unterminated, repaired = [], [], [], [], []
    for n in range(1, 65):
        page, url = fetch_page(n)
        rec = parse(page, n, typos, unterminated)
        apply_etext_fixes(rec, repaired)
        ours = by_kw[n]["metadata"]["binary_bottom_first"]
        if rec["binary_bottom_first"] != ours:
            raise RuntimeError(
                f"hexagram {n}: source figure is {rec['binary_bottom_first']} bottom-first, "
                f"this repo has {ours} — the page does not match the hexagram it claims"
            )
        hexagrams.append(rec)
        urls.append(url)
        print(f"  {n:2d}/64  {len(rec['lines'])} lines  {url}")
        time.sleep(PAUSE)

    used_wayback = sorted(h["king_wen"] for h, u in zip(hexagrams, urls) if "web.archive.org" in u)
    data = {
        "_what": "James Legge's English of the Zhouyi text (judgment + line statements), 64 hexagrams.",
        "_translator": "James Legge (1815-1897)",
        "_work": "The Yi King, Sacred Books of the East vol. XVI (Oxford: Clarendon Press; 1st ed. 1882, 2nd ed. 1899)",
        "_pd_basis": "Public domain: translator died 1897 (life+70 expired), and the work was published long before 1 Jan 1930 (PD-US).",
        "_transcription_source": "sacred-texts.com/ich/ (ic01.htm .. ic64.htm), Legge tr.; Internet Archive Wayback snapshots used where a direct fetch failed.",
        "_transcription_source_url": "https://sacred-texts.com/ich/",
        "_not_taken": "Legge's own footnotes and commentary — his 19th-century reading, not the text.",
        "_fetched_by": "scripts/fetch_legge_english.py",
        "_fetched_on": time.strftime("%Y-%m-%d"),
        "_wayback_fallback_used_for": used_wayback,
        "_source_typos_normalised": typos,
        "_passages_without_terminal_punctuation": unterminated,
        "_etext_defects_repaired": repaired,
        "hexagrams": hexagrams,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — 64 hexagrams, "
          f"{sum(len(h['lines']) for h in hexagrams)} line statements")
    return 0


# --------------------------------------------------------------------------- crosscheck

WS_API = "https://en.wikisource.org/w/api.php"


def wikisource_hexagram(n: int) -> dict | None:
    """The same passage from English Wikisource's proofread transcription of the 1882
    first edition — an independent pair of eyes. Only hexagrams 1-31 are transcribed
    there (checked 2026-07-27), so this validates roughly half the book."""
    import urllib.parse
    q = urllib.parse.urlencode({
        "action": "parse", "prop": "text", "format": "json",
        "page": f"Sacred Books of the East/Volume 16/Hexagram {n}",
    })
    try:
        page = json.loads(get(f"{WS_API}?{q}"))["parse"]["text"]["*"]
    except Exception:  # noqa: BLE001 — a missing page is a finding, not a crash
        return None
    page = re.sub(r"(?is)<(style|sup)\b.*?</\1>", "", page)
    tuan = re.search(r'(?is)<span class="anchor" id="tuan"></span>(.*?)(?:<div|<link|<p)', page)
    body = page.split('id="tuan"', 1)[-1]
    body = re.split(r"(?is)<hr\b|wst-rule", body)[0]     # stop before Legge's notes
    # Key by the ordinal Legge names inside each paragraph, not by the order they were
    # found: Wikisource's anchors are not on every paragraph, and index-alignment silently
    # compares line 3 against line 4 and reports a difference that is not there.
    lines: dict[int, str] = {}
    for chunk in re.split(r"(?i)<p\b", body)[1:]:
        text = clean(chunk.partition(">")[2]).lstrip("​ ")
        text = NUMBERED.sub("", text)
        m = ORDINAL.match(text)
        if m:
            lines.setdefault(ORDINALS[m.group(1).lower()], text)
    return {"judgment": clean(tuan.group(1)) if tuan else "", "lines": lines}


EDITION = {"nine", "six", "line", "lines", "undivided", "divided"}


def words(s: str) -> set[str]:
    """Compare on lowercase word stems only, minus the handful of words the two editions
    systematically disagree about: 1899 writes 'the first NINE, undivided' where 1882
    wrote 'the first line, undivided'. Real divergence is what we want to see."""
    return set(re.findall(r"[a-z]+", s.lower())) - EDITION


def unmatched(ours: str, reference: str) -> float:
    """The fraction of OUR words the reference does not have. Asymmetric on purpose:
    Wikisource often runs two numbered statements into one paragraph, so its passage
    being longer than ours is normal and says nothing. Ours containing words the 1882
    printing does not is the thing that would mean we had picked up the wrong text."""
    a, b = words(ours), words(reference)
    return len(a - b) / max(1, len(a))


def crosscheck() -> int:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    by_kw = {h["king_wen"]: h for h in data["hexagrams"]}
    checked = compared = flagged = 0
    for n in range(1, 65):
        ws = wikisource_hexagram(n)
        time.sleep(0.4)
        if not ws or not ws["judgment"]:
            continue
        checked += 1
        ours = by_kw[n]
        compared += 1
        o = unmatched(ours["judgment"], ws["judgment"])
        if o > 0.12:
            flagged += 1
            print(f"  hexagram {n} judgment: {o:.0%} of our words are not in the 1882 text\n    1899: {ours['judgment'][:180]}\n    1882: {ws['judgment'][:180]}")
        for i, x in enumerate(ours["lines"][:6], start=1):
            y = ws["lines"].get(i)
            if not y:
                continue
            compared += 1
            o = unmatched(x, y)
            if o > 0.12:
                flagged += 1
                print(f"  hexagram {n} line {i}: {o:.0%} of our words are not in the 1882 text\n    1899: {x[:180]}\n    1882: {y[:180]}")
    print(f"cross-checked {checked} hexagram(s) / {compared} passage(s) against Wikisource's "
          f"proofread 1882 transcription; {flagged} flagged for review")
    return 0


if __name__ == "__main__":
    raise SystemExit(crosscheck() if "--crosscheck" in sys.argv else main())
