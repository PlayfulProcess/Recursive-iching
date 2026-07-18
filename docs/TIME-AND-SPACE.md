# Time and space — the architecture of the Recursive I Ching

The builder's brief (Jul 16 2026): *every I Ching visualization should let you render the
different books across time — navigate through time and space.*

Here is what that means concretely, and the data decision (already implemented) that
makes it work.

## The model: hexagram = space, book = time

A hexagram is a **place**: one of 64 coordinates in a small, highly structured space.
A book is a **moment**: one textual layer laid over all 64 places at some point in the
last three thousand years. Every view in this repo is a way of moving along one axis
while holding the other still:

- **Hold the book still, move through space** → a normal reader (browse hexagrams
  within one text).
- **Hold the hexagram still, move through time** → the new thing: watch hexagram 3
  accrete meaning as the centuries pass — the terse Western Zhou omen text, then the
  moralizing Ten Wings, then (as layers land) Wang Bi's metaphysics, the Song
  systematizers, Legge's Victorian English, Wilhelm's German.

This is the family's "same card across decks" move (tarot's all-decks-many-lenses meta
grammar) transposed: there the constant is the card and the variable is the deck; here
the constant is the hexagram and the variable is the century.

## The one enabling convention (implemented)

**Every book-grammar uses the same item ids** — `hexagram-03-zhun` is hexagram 3 in
`grammars/zhouyi/`, in `grammars/ten-wings/`, and in every book that comes later. A
viewer aligns books by doing nothing: fetch N grammars, group items by id, sort books
by their `metadata.book_period`. No mapping tables, no cross-reference files. This is
the repo's equivalent of tarot's one-cross-link-pattern rule: do not invent a second
alignment mechanism.

Each book-grammar also carries, on every item, `metadata.book` (slug) and
`metadata.book_period` (the time-axis label), and the grammar's own top level carries
the provenance and licensing in `_grammar_commons`.

## Space: how the 64 places connect

The hexagram picker should offer the space's own structures, not an arbitrary grid:

- **8×8 trigram matrix** — lower trigram × upper trigram, the native coordinate system
  (`metadata.trigram_lower/upper` are already on every zhouyi item).
- **King Wen sequence** — the received order (`metadata.king_wen`), which is itself a
  historical artifact worth seeing; the 序卦 section narrates why each follows the last.
- **Binary/Fuxi order** — from `metadata.binary_bottom_first`, the ordering Leibniz saw.
- **One-line neighbors** — each hexagram touches six others by changing a single line;
  this is how a *reading* moves through the space (changing lines), so the viewer should
  eventually move that way too.

## Time: the book rail (roadmap)

| Book (grammar slug) | Period | Language | Status |
|---|---|---|---|
| `zhouyi` | Western Zhou, c. 9th c. BCE | Classical Chinese | ✅ built (64/64) |
| `ten-wings` | Warring States–Han | Classical Chinese | ✅ built (64/64; source lacks hexagram 32's 彖 — flagged) |
| `wang-bi` | 226–249 CE | Classical Chinese | planned — needs a PD transcription source |
| `zhu-xi` (周易本義) | 12th c. | Classical Chinese | planned — same |
| `legge-1899` | 1882/1899 | English (PD) | planned — needs a clean digital source (network-blocked this session) |
| `wilhelm-1924` | 1924 | German (PD in US since 2020) | planned — the German original only; the 1950 Baynes English stays out until ~2046 |
| `builder` | 2026– | English/Portuguese | the builder's own translation, hexagram by hexagram |

Rules for adding a book: public-domain text only, transcription source credited in
`_grammar_commons`, same item ids, `book_period` set, gate (`check.py`) green.

## The viewer (first build shipped Jul 16 2026: public/viewers/books.html + caster.html)

One static page on the channels.html pattern (no build step): fetch all
`grammars/*/grammar.json`, group by item id. Layout: **hexagram picker** (the 8×8
matrix, glyphs from `metadata.unicode`) on one side; a **time rail** of books on the
other; the reading pane renders the chosen hexagram's sections from each selected book,
stacked oldest-first. Arrow keys move through space (adjacent hexagrams); the rail
toggles books through time. Deep-linkable: `?hexagram=03&books=zhouyi,ten-wings`.

The same grammar data serves the recursive.eco app unchanged — book-grammars are
ordinary grammars there, and the channel (`/library/channels/iching`) simply lists them.

## The epistemic frame (added Jul 18 2026, from the builder's books)

The book rail is not a progress bar. No book on it is "the true one" — not the terse
Western Zhou omen text, not the moralizing Ten Wings, not Wilhelm, not whatever science
says about randomness. Each book is a **grammar**: a finite, coherent set of elements
generating an infinite range of appropriate responses, judged not by "is it true?" but
by the builder's three-filter test — *is it useful, does it fit the data, is it
compassionate.* Falsifiable claims (does casting predict events? — no one has shown it)
and relational claims (does sustained practice within this grammar produce coherence,
meaning, relationship? — observably, for three thousand years) are different kinds of
claim, not a ranking. The viewer's unranked co-presence of the books — oldest first,
none privileged — is this frame, rendered. Relate to the hexagram; never obey it.

**Pending (Phase A):** the builder corrected errors in the app-side copies of the two
book-grammars (recursive.eco library). Those corrections must be exported back into
grammars/ (the two-way-sync move: get_grammar → diff → repo, then re-run the gate and
sync_public) so the repo stays canon. Do this before adding any new book.
