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
- **`research/sources/raw/`** — the raw open datasets the build reads, pulled 2026-07-16
  (Legge's English 2026-07-27), with the licensing decisions documented below.
- **`scripts/fetch_legge_english.py`** — pulls and verifies that English; `--crosscheck`
  re-runs the comparison against an independent transcription.
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
- **English, where there is any, is James Legge's** — *The Yî King*, Sacred Books of the
  East vol. XVI (1882; 2nd ed. 1899). Genuinely public domain: the translator died in 1897
  and the book was printed long before 1930. It sits *beside* the Chinese as
  `sections_i18n.en`, never over it (the convention:
  [`GRAMMAR_FORMAT.md`](GRAMMAR_FORMAT.md#languages--a-recursive-i-ching-extension)), and
  the viewers open in 中文 unless the reader asks otherwise. That default is the editorial
  point: this is what the book was before anyone translated, systematized, or believed
  things about it — and Legge's English is itself a Victorian Scot's reading, not a
  neutral window onto the Bronze Age.
  - **Where it is, exactly:** the Zhouyi, complete — all 64 judgments (卦辞) and all 386
    line statements (爻辞), including the 用九/用六 paragraphs of hexagrams 1 and 2.
  - **Where it is not, yet:** the **Ten Wings**. Legge's Appendixes I–VI are equally public
    domain and are the obvious next pass; until then the viewers fall back to the original
    and say so on the page rather than let it pass for a translation. Also unfilled:
    `emergent-structure` and `leibniz-binary-tree`, which carry the builder's own English
    already and were never bilingual in this sense.
  - **How it was checked:** every hexagram was matched to its King Wen number by the
    six-bit figure printed on the source page, and 210 passages across hexagrams 1–31 were
    compared word for word against English Wikisource's independently proofread
    transcription of the 1882 first edition — no divergence. Run it yourself:
    `python scripts/fetch_legge_english.py --crosscheck`.
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
- **[public/viewers/language.js](public/viewers/language.js)** — the 中文 / EN / 中文 + EN switch both readers share. Default 中文; the choice is remembered (localStorage) and carried in `?lang=`, so a shared link arrives in the language it was read in. The Binary Ladder has no switch because it renders no `sections` — only structure. A book with no English says so on the page rather than letting the original stand in for a translation.
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
