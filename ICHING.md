# The Recursive I Ching

A historical, editorial account of the Book of Changes — how a Western Zhou diviner's
manual acquired a philosophy, a canon, and a world readership — built as open grammar
data on the recursive.eco pattern, sibling to
[recursive-tarot](https://github.com/PlayfulProcess/recursive-tarot) and
[Recursive-astrology](https://github.com/PlayfulProcess/Recursive-astrology).

The shared intention of the family holds here too: **read to know yourself, not to be
told your fate; relate to the hexagram, never obey it.**

## What's here now

- **`grammars/zhouyi/`** — the 64 hexagrams of the Zhouyi core text in the original
  language: each hexagram's 卦辞 (judgment) and 爻辞 (line statements), with King Wen
  number, trigram pair, pinyin, and Unicode glyph — and James Legge's public-domain
  English beside each one in `sections_i18n.en`. Generated — never hand-edit; run
  `python scripts/build_zhouyi_grammar.py`.
- **`grammars/ten-wings/`** — the per-hexagram commentary layer (Warring States–Han):
  彖传 on each judgment, 大象/小象 (the images, whole and per line), 文言 on hexagrams 1–2,
  and 序卦 (the sequence) — with Legge's English beside each one in `sections_i18n.en`.
  Generated; run `python scripts/build_ten_wings_grammar.py`.
- **`research/sources/raw/`** — the raw open datasets the build reads, pulled 2026-07-16
  (Legge's Zhouyi English 2026-07-27, his Ten Wings 2026-07-30), with the licensing
  decisions documented below.
- **`scripts/fetch_legge_english.py`** — pulls and verifies the Zhouyi English;
  `--crosscheck` re-runs the comparison against an independent transcription.
- **`scripts/fetch_legge_wings.py`** — the same for the Ten Wings: Legge's Appendixes I,
  II, IV and VI, with the same two structural checks and a `--crosscheck` against the
  Internet Archive's scan of the 1882 first edition.
- **`check.py`** — the family's grammar gate. Run before every commit:
  `python check.py` must end "all checks passed".

## Licensing stance (read before adding any text)

Same rule as the tarot repo: **public domain in, public domain out** — and honest about
what actually is public domain:

- The **Zhouyi text itself** (Western Zhou core layer) is ancient and public domain
  everywhere. Our transcription source is
  [john-walks-slow/open-iching](https://github.com/john-walks-slow/open-iching)
  (simplified characters; credited in the grammar's `_grammar_commons`).
- Structural facts (traditional names, pinyin, Unicode) come from
  [adamblvck/iching-wilhelm-dataset](https://github.com/adamblvck/iching-wilhelm-dataset)
  (MIT). Its **Wilhelm–Baynes English prose was deliberately not used**: the 1950
  English translation is *not* public domain (the claim that it entered PD in 2020
  confuses it with Wilhelm's 1924 German original) and stays out of this repo until 2046.
- **Images follow the same rule as text: public domain only, and *verified*.** Every
  picture in this repo has had its Wikimedia Commons file page opened and its licence tag
  read; each one is registered in [`docs/IMAGES.md`](docs/IMAGES.md) with creator, date,
  file page and PD basis, and carried inside its grammar as `_image_provenance`
  (shape: [`GRAMMAR_FORMAT.md`](GRAMMAR_FORMAT.md#image-provenance--a-recursive-i-ching-extension)).
  CC-BY and CC-BY-SA are not public domain and stay out — several near-perfect candidates
  were rejected on exactly that ground, and are listed so nobody re-proposes them. One apt
  image per grammar: `python check.py` fails if two grammars share a cover, because a
  library where three books wear the same stock photograph is telling you nothing.
- **The Ten Wings text** (Warring States–Han) is equally ancient and public domain; its
  transcription source is the same [open-iching](https://github.com/john-walks-slow/open-iching)
  dataset, 文言 included.
- **English, where there is any, is James Legge's** — *The Yî King*, Sacred Books of the
  East vol. XVI (1882; 2nd ed. 1899). Genuinely public domain: the translator died in 1897
  and the book was printed long before 1930. It sits *beside* the Chinese as
  `sections_i18n.en`, never over it (the convention:
  [`GRAMMAR_FORMAT.md`](GRAMMAR_FORMAT.md#languages--a-recursive-i-ching-extension)), and
  the viewers open in 中文 unless the reader asks otherwise. That default is the editorial
  point: this is what the book was before anyone translated, systematized, or believed
  things about it — and Legge's English is itself a Victorian Scot's reading, not a
  neutral window onto the Bronze Age.
  - **Where it is, exactly — the Zhouyi:** complete. All 64 judgments (卦辞) and all 386
    line statements (爻辞), including the 用九/用六 paragraphs of hexagrams 1 and 2.
  - **Where it is, exactly — the Ten Wings (added 2026-07-30):** every Wing this book
    carries. All 64 彖传 (Legge's Appendix I, 179 paragraphs); all 64 大象 and all 386 小象
    (Appendix II); the 文言 of hexagrams 1 and 2 (Appendix IV, 36 + 10 paragraphs, and the
    Wing covers no other hexagram); and the 序卦 of the 60 hexagrams whose Chinese sequence
    text this book carries (Appendix VI). Hexagrams 1, 2, 12 and 32 have no Chinese 序卦 in
    the transcription this book is built from, so they have no English one either — the
    language block mirrors the canonical keys, gaps included.
    - One thing about the 序卦 has to be said rather than smoothed over: Legge prints
      Appendix VI as running paragraphs, each walking a **run** of hexagrams, while the
      Chinese here is cut per hexagram. So a hexagram's English sequence text is the whole
      paragraph its sentence falls inside, labelled with the run it covers. The fit is
      honest; it is not one-to-one, and cutting Legge's sentences to fake one would be
      inventing a shape the printed book does not have.
  - **Where it is not, yet:** the **whole-treatise Wings** — Legge's Appendix III (繫辞
    Xi Ci, the Great Treatise), Appendix V (说卦 Shuogua) and Appendix VII (杂卦 Zagua).
    They are equally public domain; what stops them is not the translation but the shape.
    They speak about the *book*, not about any one hexagram, and `ten-wings` is a
    per-hexagram grammar: there is no canonical Chinese slot for them to sit beside. Giving
    them items of their own — a treatise grammar, or non-hexagram items in this one — is a
    structure decision for the builder, and it is the next pass here. Also unfilled:
    `emergent-structure` and `leibniz-binary-tree`, which carry the builder's own English
    already and were never bilingual in this sense.
  - **How the Zhouyi was checked:** every hexagram was matched to its King Wen number by
    the six-bit figure printed on the source page, and 210 passages across hexagrams 1–31
    were compared word for word against English Wikisource's independently proofread
    transcription of the 1882 first edition — no divergence. Run it yourself:
    `python scripts/fetch_legge_english.py --crosscheck`.
  - **How the Ten Wings was checked:** Appendixes I and II were required to arrive as an
    unbroken run of Roman numerals I–LXIV, each hexagram yielding a Tuan, a Great Image and
    exactly six Small Images (seven for hexagrams 1 and 2); Appendix VI to cover 1–64 with
    no hexagram outside a paragraph's range; Appendix IV to reach the 36 and 10 paragraphs
    the printing has. Then all **688 harvested passages** were cross-checked against the
    Internet Archive's independent scan-and-OCR of the 1882 first edition
    ([wg916](https://archive.org/details/wg916)) — nothing flagged; the widest gap, 12.5%,
    is one romanised hexagram name the OCR mangled. Wikisource has transcribed only the
    hexagram pages of this volume, no appendixes, which is why the reference is the scan.
    Run it yourself: `python scripts/fetch_legge_wings.py --crosscheck`.
    - Two defects in the etext were repaired against the printing and are recorded in the
      raw file as `_etext_defects_repaired`: on hexagram 42 the source runs Legge's own
      footnote into the body of the Tuan (his commentary is not harvested here, so the
      paragraph is cut back to where the book ends it), and hexagram 8's second Small Image
      is missing its closing full stop. Three mis-set paragraph numbers were normalised and
      are listed as `_source_typos_normalised`.
  - Wilhelm–Baynes (1950) is still **not** public domain and still stays out.

## Time and space

The architecture for rendering the different books across time — hexagram as the
spatial coordinate, book as the temporal one, aligned by shared item ids — is
[`docs/TIME-AND-SPACE.md`](docs/TIME-AND-SPACE.md).

## Viewers

The app routes are the canonical viewers: **/hexagram/[kw]** (64 static pages) and **/cast**. The static pages below are what the GitHub Pages site actually serves, and remain the reference spec — they work on any static host.

> **Known gap (2026-07-27):** the language switch is in the static viewers only. The app
> routes still render the canonical Chinese, because this machine has no `node_modules`
> and a Next build could not be run to verify a change to them. Porting it is small — the
> data is already there; it needs `sections_i18n` read in `app/hexagram/[kw]/page.tsx` and
> `app/cast/page.tsx`, with `?lang=` alongside the existing `?books=`.

- **[public/viewers/books.html](public/viewers/books.html)** — time×space reader: 8×8 trigram matrix, book rail, one-line neighbors, deep-linkable (`?hexagram=3&books=zhouyi,ten-wings&lang=both`).
- **[public/viewers/caster.html](public/viewers/caster.html)** — the cast as a path: three-coin or yarrow distribution, 本卦 → 之卦 via the moving lines, whose 爻辞 and 小象 are the texts read. Preview locally: `cd public && python3 -m http.server`.
- **[public/viewers/language.js](public/viewers/language.js)** — the 中文 / EN / 中文 + EN switch both readers share. Default 中文; the choice is remembered (localStorage) and carried in `?lang=`, so a shared link arrives in the language it was read in. The Binary Ladder has no switch because it renders no `sections` — only structure. Since 2026-07-30 both books the readers show — Zhouyi and Ten Wings — carry Legge, so nothing in them falls back any more; the fallback note stays in the code for the books still to come, and says so on the page rather than letting the original stand in for a translation.
- **[public/viewers/binary-ladder.html](public/viewers/binary-ladder.html)** — the dimensional ladder: one bit (yin/yang) → three bits (the 8 trigrams, 2×4) → six bits (the 64 hexagrams, 8×8, Fu Xi/binary order visible as the grid position itself). Selecting a line or trigram highlights the smaller world it's the *trace* of in the larger one. Level 4 bends the same 64 onto a circle: the **Human Design mandala** (SVG, no dependencies), each hexagram a "gate" of 5°37′30″ of the zodiac, clicking either the matrix or the wheel highlighting the other, with the gate 180° opposite always the exact binary complement. A three-way toggle — King Wen ↔ Fu Xi ↔ mandala slot — shows the three orderings as permutations of one set. Includes a sourced Leibniz/Bouvet history panel, with the two primary documents themselves as captioned public-domain figures: the 1701 woodcut Bouvet sent (the Fu Xi arrangement the grid re-draws) and Leibniz's own 1703 binary table. Human Design is credited as Ra Uru Hu's 1987 synthesis and described, not endorsed; the Hoffman "trace" framing — including the "I Ching as a trace of Human Design" reading and its honest inversion (the ladder ascends, the history descends) — stays clearly labeled as a modern teaching analogy, not doctrine. The research behind Level 4, and what was deliberately left unclaimed, is [`docs/HUMAN-DESIGN-TRACE.md`](docs/HUMAN-DESIGN-TRACE.md).

## The plan

The full historical spine (oracle bones → Zhouyi → Ten Wings → Wang Bi/Zhu Xi →
Legge/Wilhelm/Jung → the modern book), the two wings (people-of-iching,
books-of-iching), and the specialist video watchlists are laid out in the family plan:
[`docs/plan/ASTRO-ICHING-CONTENT-2026-07.md`](https://github.com/PlayfulProcess/recursive-tarot/blob/main/docs/plan/ASTRO-ICHING-CONTENT-2026-07.md)
in the tarot repo (this repo's own docs will grow as the stages land).

## License

Ancient texts: public domain. This repo's compilation, scripts, and prose: CC0-1.0 /
public domain dedication, matching the family's commons-first stance.
