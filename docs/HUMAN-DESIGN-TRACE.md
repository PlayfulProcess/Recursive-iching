# The I Ching and Human Design: what the correspondence actually is, and what "trace" can honestly mean

*Prepared 2026-07-27, in the same method as the Leibniz/Hoffman brief this repo's Binary
Ladder rests on. Claims marked **(fetched)** come from a page or file I retrieved and read
directly this session. Claims marked **(computed)** are arithmetic I ran here against this
repo's own `grammars/zhouyi/grammar.json` and the gate order below — reproducible, not
authority. Nothing in this document is cited to a source I did not actually open.*

---

## 0. The short version

Human Design takes the 64 hexagrams, keeps the King Wen numbers, and lays them around the
ecliptic in a specific order — 5°37′30″ each — then hangs a great deal of further machinery
on them (planets, a nine-node body graph, 36 channels, types). If you strip away everything
that is *not* the hexagram — the degrees, the planets, the graph — what is left is exactly
the bare 64-element binary lattice the *I Ching* already had.

That stripping-away is a real, well-defined projection, and it is the honest core of the
builder's "trace" idea. What it is **not** is evidence that the *I Ching* is a shadow of a
larger prior structure. Historically the arrow runs the other way: Human Design is a 1987
synthesis built **out of** the *I Ching*, so the "bigger matrix" is the younger object. See
§5, which is the part that keeps this honest.

---

## 1. Human Design, described as what it is

Human Design was originated by **Alan Robert Krakower**, who took the name **Ra Uru Hu** and
published *The Human Design System* in **1992**, following an experience in **January 1987**
on Ibiza which he described as an eight-day encounter with a "Voice." Wikipedia, which
categorises the system as pseudoscience and as a New Age practice, puts it plainly:
"Krakower developed the Human Design system following an alleged mystical experience in
1987," and describes it as combining "astrology, the Chinese I Ching, Judaic Kabbalah, Vedic
philosophy, and modern physics" (fetched — en.wikipedia.org/wiki/Human_Design).

Practitioners describe the same origin in their own register. Jovian Archive, the system's
official home, calls the 64 gates "derived from the 64 Hexagrams of the I'Ching" (fetched).
A practitioner site states it without hedging: "Human Design is a modern system, created in
1987. It incorporates the I Ching as one of four foundational pillars, but it is not a
traditional Chinese practice" (fetched — thalira.com). Note also that HD teachers commonly
insist the 1987 experience was a *revelation* rather than a *channelling* — a distinction
they consider important; it appears in search summaries of practitioner sites (via search
summary, not independently fetched).

For this repo's purposes the honest description is: **a modern, single-author synthesis,
modern-esoteric in provenance, presented faithfully as what it is.** It is not ancient
Chinese doctrine and does not claim to be. The repo's rule holds — present the system
accurately, credit its author, do not launder its age, and do not adopt its truth claims.

---

## 2. Gate → hexagram: it is the King Wen numbering

The correspondence is the identity map on King Wen numbers: **Gate *n* is hexagram *n*.**
"The mapping from hexagram to gate is numerically direct: Hexagram 1 is Gate 1, Hexagram 2
is Gate 2, all the way through Hexagram 64 as Gate 64" (fetched — thalira.com).

That is a low-authority source for a load-bearing claim, so it was checked from the inside
instead. Two independent consequences fall out only if the numbering really is King Wen's
(computed, see §3 and §4):

1. Taking the published gate→degree tables and reading each gate number as its **King Wen**
   hexagram, every pair of gates 180° apart on the wheel turns out to be an exact **binary
   complement** — all six lines inverted — for all 32 pairs, with no exceptions.
2. Under the same reading, half the wheel is the Fu Xi binary sequence 0→31 in exact order.

Neither pattern survives a wrong numbering; a scrambled gate→hexagram map would destroy
both. Independently, the Gene Keys documentation (which shares Human Design's wheel) gives
"Programming Partners" as pairs opposite on the wheel, states that "if one hexagram
comprises three yin lines followed by three yang lines, its partner will have the reverse,"
and names the **7 / 13** and **1 / 2** pairs (fetched — genekeys.com). Both pairs are exact
binary complements under King Wen numbering and sit exactly 32 slots apart in the wheel
order below (computed).

**Conclusion: gate number = King Wen hexagram number, verified three ways.** What Human
Design does *not* keep is the King Wen *sequence* — see next.

---

## 3. The mandala order — verified, with sources

Each gate occupies **5°37′30″** of the ecliptic (= 360/64 = 5.625°). Jovian Archive states
this exactly: "the I'Ching wheel is mapped onto a 360-degree circle, with each hexagram
occupying exactly 5 degrees, 37 minutes, and 30 seconds of arc" (fetched).

The order is **not** the King Wen sequence. It begins with **Gate 41 at 2°00′ Aquarius** and
runs forward through the zodiac:

```
41 19 13 49 30 | 55 37 63 22 36 25 | 17 21 51 42 3 | 27 24 2 23 8 | 20 16 35 45 12 15 |
52 39 53 62 56 | 31 33 7 4 29 | 59 40 64 47 6 46 | 18 48 57 32 50 | 28 44 1 43 14 |
34 9 5 26 11 10 | 58 38 54 61 60
```

(gate 41 starts at 2°00′ Aquarius; each subsequent gate starts 5°37′30″ later; the groups
above are only a reading aid, roughly sign by sign.)

**Three independent sources agree on this exact cyclic order** (fetched):

- bonniesorsby.com/human-design-gates-by-degree/ — a full 64-row gate/sign/degree table.
- barneyandflow.com/gate-zodiac-degrees — a second full table, same order, same degrees.
- **github.com/CReizner/SharpAstrology.HumanDesign** — an open-source chart-calculation
  library (read via the GitHub API). This one is worth more than the other two, because it
  is *executable*: `Enums/Gates.cs` lists the gates as enum values 0–63 and
  `Utility/HumanDesignUtility.cs` computes `Gate = floor((longitude − 3.875°) / 5.625°)`.
  The offset 3.875° = 3°52′30″ Aries is where its slot 0 (Gate 17) begins; rotating its list
  by 11 reproduces the sequence above exactly (computed).

Two small conflicts worth naming rather than hiding: both degree tables contain one obvious
typo each around Gate 45 (22°27′ where the arithmetic requires 22°37′30″), and both round
5°37′30″ to minutes in places. The library's arithmetic is the arbiter; the tables agree
with it everywhere else.

The widely repeated claim that the gates "are arranged according to the Fuxi sequence"
(seen in several practitioner posts and in search-engine summaries) is **half true, and
worth stating precisely** — §4.

---

## 4. What the mandala order actually is, mathematically (computed)

Read each hexagram's six lines bottom-to-top as a binary numeral with the **bottom line as
the most significant digit** — this repo's existing Fu Xi/Shao Yong convention, the one the
Binary Ladder's Level 3 already uses. Write *v(h)* for that value, 0–63.

Then, walking the wheel forward through the zodiac from **Gate 2 (v = 0, all yin, beginning
13°15′ Taurus)**:

- the next **32 gates have v = 0, 1, 2, … 31** — the Fu Xi binary count, in exact order;
- then the wheel jumps to **Gate 1 (v = 63, all yang, beginning 13°15′ Scorpio)** and counts
  **down: 63, 62, … 32**, arriving back at Gate 2.

Equivalently, and more elegantly:

> **The gate diametrically opposite any gate is its binary complement** — all six lines
> inverted. True for all 32 antipodal pairs, no exceptions (computed).

Equivalently again: the first half of the wheel is every hexagram whose **bottom line is
yin**, in Fu Xi order; the second half is their complements, in mirror order. 乾 (all yang)
and 坤 (all yin) sit exactly opposite each other, at 13°15′ Scorpio and 13°15′ Taurus.

So: the mandala is neither King Wen order nor plain Fu Xi order. It is Fu Xi order *folded
in half* so that antipodes are opposites. Three orderings, three permutations of the same 64
objects — King Wen ↔ Fu Xi ↔ mandala — which is exactly the lesson the Binary Ladder was
already teaching, now with a third instance.

Two more computed facts, both of which matter for §5:

- **What the folding preserves.** Complementation is an involution on the 64 hexagrams with
  no fixed points, so it partitions them into 32 pairs — precisely the shape that embeds
  naturally on a circle. The mandala order is not an arbitrary shuffle: it is an embedding
  of the hexagram set into a circle that *respects a symmetry the lattice already had.*
- **What the folding does not explain.** The 36 channels — the gate pairs that wire the nine
  centres of the body graph — show **no** consistent binary relation. Only 3 of the 36 pairs
  are complements, 1 is a line-order reversal, and the rest are unrelated; their Hamming
  distances scatter across 1–6, and their arc-distances on the wheel scatter across 1–32
  slots (computed, using the channel list from the same open-source library). **The body
  graph is genuinely added structure. It is not hiding inside the hexagrams.**

For completeness, the finer subdivisions a chart uses, as implemented in that library
(fetched): gate 5.625° → line 0.9375° → colour 0.15625° → tone → base, i.e.
64 × 6 × 6 × 6 × 5 = **69,120** slices of the ecliptic, each about 18.75 arc-seconds. A
chart reads **13 bodies** (Sun, Earth, both lunar nodes, Moon, and the eight planets) at
**two** moments — birth, and the moment 88° of solar arc earlier — giving 26 activations.

---

## 5. The "trace" reading — and where it breaks

### 5a. The precise sense in which it works

Hoffman's *trace* (see the Leibniz/Hoffman brief; the 2024 "Traces of Consciousness" paper
is still a preprint and its physics claims are explicitly conjectural) is: take a large
Markov chain, restrict it to the states one observer can actually reach, and there is a
unique smaller chain describing the dynamics *as seen from inside* that restriction.

The structurally analogous move here is a **projection**, and it is exact:

| Human Design carries | the *I Ching* keeps |
|---|---|
| position on the ecliptic (69,120 slices) | which of 64 arcs — i.e. the hexagram |
| which of 13 bodies, in which of 2 charts | — |
| the nine centres and 36 channels | — |
| type, authority, profile, definition | — |

Forget every coordinate except "which of the 64 arcs" and you land back on exactly the 64
hexagrams, with their binary structure intact. That is a genuine forgetful map from a finer
labelled space onto a coarser one — the same *shape* of move as taking a trace, done with
ordinary projections instead of Markov kernels. In that precise and limited sense:
**the 64 hexagrams are what is left of the Human Design mandala when the only thing you can
observe is which arc you are in.**

The Binary Ladder already teaches this move twice — a trigram is the 64-hexagram world seen
through three lines; a single line is the trigram world seen through one. The mandala is a
third rung in the same direction: a larger labelled space whose forgetting returns the
smaller one.

### 5b. Where the analogy breaks — four ways, none of them small

1. **The history is backwards.** Hoffman's trace has the big chain as the prior, more
   fundamental object. Here the "bigger matrix" is a 1987 construction assembled *out of*
   the smaller one. The *Yijing*'s core layer is Western Zhou; the mandala is younger than
   television. The ladder in the viewer ascends 1 → 3 → 6 bits → mandala; the history
   descends. Anyone who reads the ascent as a claim of priority has it exactly inverted.
2. **It is a projection, not a dynamics.** A trace is defined on a Markov chain: transition
   probabilities. The mandala is a static labelling of a circle. The one dynamics it
   naturally carries — a planet walking the 64 arcs — is a deterministic cycle, and its
   "trace" onto anything coarser is trivial. If you want a genuine stochastic chain over
   the 64 hexagrams, this repo already has one and it is the *I Ching*'s own: the casting
   distribution in [the Caster](../public/viewers/caster.html). That is the honest place for
   Markov language in this project.
3. **The restriction is chosen, not discovered.** Hoffman's trace chain is *unique* given a
   subset of states. Here, "forget the degrees" is one projection among many; nothing makes
   it canonical except that it happens to land on the object we started from. The uniqueness
   that gives the theorem its force is absent.
4. **The extra layers are additions, not hidden depth.** §4 shows this concretely: the
   channel topology has no binary signature. Human Design's further structure is *appended*
   to the hexagrams (elegantly, in the case of the antipodal folding), not extracted from
   them. Calling the *I Ching* a trace of it risks implying the hexagrams secretly contained
   the body graph. They do not.

### 5c. So what should the viewer say?

The version that survives all four objections, and the one the page ships:

> The *I Ching* is what is left of the Human Design mandala when you forget the degrees, the
> planets and the body graph — a real projection, and a nice way to feel what "restricting a
> larger structure to what an observer can see" means. It is a teaching analogy, borrowed
> from a speculative research programme, not a claim that either system is true, and
> historically the bigger structure is the younger one: Human Design descends from the *I
> Ching*, not the other way round.

That is offered as a mirror, in the family's usual stance: relate to the hexagram, never
obey it — and the same goes for the gate.

---

## 6. What this document deliberately does not claim

- **Not claimed:** that the mandala order "is the Fu Xi sequence." It is a folded variant;
  the popular phrasing is imprecise and §4 gives the precise version.
- **Not claimed:** any of Human Design's own assertions — neutrino imprinting, the
  hexagram/codon identification, types, authority, or the reliability of any chart reading.
  The repo describes the system; it does not endorse it.
- **Not claimed:** that Ra Uru Hu's ordering has an ancient Chinese precedent. No source
  found this session traces the mandala order to any pre-modern text; the antipodal-
  complement structure is a mathematical property of the arrangement, checkable by anyone,
  not evidence of transmission.
- **Not claimed:** Hoffman's stronger positions (that this reproduces physics, that
  consciousness is the base layer). Those remain conjecture, as the Leibniz/Hoffman brief
  records.
- **Not settled:** the "revelation vs. channelling" distinction is reported here as a claim
  HD teachers make, from search summaries only — not independently fetched.

---

## Sources

**Fetched and read this session:**

- https://en.wikipedia.org/wiki/Human_Design — origin, components, pseudoscience classification
- https://jovianarchive.com/pages/gates-and-hexagrams-in-human-design — gates derived from hexagrams; mandala rings
- https://jovianarchive.com/blogs/human-design-basics/the-i-ching-the-genetic-code-and-the-architecture-of-human-design — the 5°37′30″ per hexagram figure
- https://thalira.com/blogs/quantum-codex/human-design-i-ching-connection — gate *n* = hexagram *n*; "not a traditional Chinese practice"; not King Wen order
- https://bonniesorsby.com/human-design-gates-by-degree/ — full gate/degree table
- https://www.barneyandflow.com/gate-zodiac-degrees — second full gate/degree table
- https://github.com/CReizner/SharpAstrology.HumanDesign — open-source chart library; `Enums/Gates.cs`, `Enums/Channels.cs`, `Enums/Centers.cs`, `Utility/HumanDesignUtility.cs`, `ExtensionMethods/HumanDesignPlanetPositionProviderExtensionMethods.cs`, `Definitions/HumanDesignDefaults.cs` (MIT-licensed project; read via the GitHub API, not vendored here)
- https://genekeys.com/docs/programming-partners/ — opposite-on-the-wheel pairs are line-opposites; 7/13 and 1/2

**Found via search only, not independently fetched** (named because they were the route to
the above, not as evidence): jovianarchive.com/pages/about-ra-uru-hu; humandesign.school;
ihdschool.com; freehumandesignchart.com; livingthespiral.com; ascendantgate.com.

**Prior brief this one builds on:** the Leibniz/Bouvet + Hoffman research brief (kept
outside this repo, in the builder's `_research/`), whose sources back the Binary Ladder's
existing history and "trace" panels.
