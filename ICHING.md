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
  number, trigram pair, pinyin, and Unicode glyph. Generated — never hand-edit; run
  `python scripts/build_zhouyi_grammar.py`.
- **`research/sources/raw/`** — the raw open datasets the build reads, pulled 2026-07-16,
  with the licensing decisions documented below.
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
- **English translation slots are intentionally empty.** The plan: James Legge's 1899
  rendering (Sacred Books of the East vol. XVI — genuinely public domain) once a clean
  digital source is processed, and/or the builder's own translation. Interim readers get
  the original text — which is itself the editorial point: this is what the book actually
  was before anyone translated, systematized, or believed things about it.

## Time and space

The architecture for rendering the different books across time — hexagram as the
spatial coordinate, book as the temporal one, aligned by shared item ids — is
[`docs/TIME-AND-SPACE.md`](docs/TIME-AND-SPACE.md).

## Viewers

The app routes are now the canonical viewers: **/hexagram/[kw]** (64 static pages) and **/cast**. The static pages below remain as the reference spec and work on any static host:

- **[public/viewers/books.html](public/viewers/books.html)** — time×space reader: 8×8 trigram matrix, book rail, one-line neighbors, deep-linkable (`?hexagram=3&books=zhouyi,ten-wings`).
- **[public/viewers/caster.html](public/viewers/caster.html)** — the cast as a path: three-coin or yarrow distribution, 本卦 → 之卦 via the moving lines, whose 爻辞 and 小象 are the texts read. Preview locally: `cd public && python3 -m http.server`.

## The plan

The full historical spine (oracle bones → Zhouyi → Ten Wings → Wang Bi/Zhu Xi →
Legge/Wilhelm/Jung → the modern book), the two wings (people-of-iching,
books-of-iching), and the specialist video watchlists are laid out in the family plan:
[`docs/plan/ASTRO-ICHING-CONTENT-2026-07.md`](https://github.com/PlayfulProcess/recursive-tarot/blob/main/docs/plan/ASTRO-ICHING-CONTENT-2026-07.md)
in the tarot repo (this repo's own docs will grow as the stages land).

## License

Ancient texts: public domain. This repo's compilation, scripts, and prose: CC0-1.0 /
public domain dedication, matching the family's commons-first stance.
