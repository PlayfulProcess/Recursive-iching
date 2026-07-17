/**
 * lib/iching.ts — the one module that owns the I Ching data and the math.
 *
 * Data: static imports of the book-grammars (grammars/<slug>/grammar.json — the
 * repo's canon, same files recursive.eco reads raw). Bundled at build time; no
 * runtime fetch. The alignment contract (docs/TIME-AND-SPACE.md): every book
 * uses the same item ids, so cross-book reading = group by id.
 *
 * Math: King Wen ↔ binary ↔ trigram-pair indexes, the six one-line-change
 * neighbors, and the cast distributions (three-coin and true yarrow) with the
 * 本卦 → 之卦 path arithmetic. Verified against the static reference viewers
 * (public/viewers/*, the original spec) before porting.
 */
import zhouyiGrammar from "@/grammars/zhouyi/grammar.json";
import tenWingsGrammar from "@/grammars/ten-wings/grammar.json";

export interface HexagramItem {
  id: string;
  name: string;
  symbol: string;
  category: string;
  subcategory?: string;
  sort_order: number;
  sections: Record<string, string>;
  metadata: {
    king_wen: number;
    name_traditional: string;
    pinyin: string;
    unicode: string;
    binary_bottom_first?: string;
    trigram_lower?: string;
    trigram_upper?: string;
    name_simplified?: string;
    book?: string;
    book_period?: string;
  };
}

export interface Book {
  slug: string;
  label: string;
  era: string;
  items: HexagramItem[];
}

/** The time axis, oldest → newest. Future books append here (one line each). */
export const BOOKS: Book[] = [
  {
    slug: "zhouyi",
    label: "周易 Zhouyi",
    era: "Western Zhou, c. 9th c. BCE",
    items: (zhouyiGrammar as { items: HexagramItem[] }).items,
  },
  {
    slug: "ten-wings",
    label: "十翼 Ten Wings",
    era: "Warring States–Han",
    items: (tenWingsGrammar as { items: HexagramItem[] }).items,
  },
];

export const DEFAULT_BOOK_SLUGS = BOOKS.map((b) => b.slug);

/** Fuxi arrangement of the eight trigrams — the matrix axes. */
export const TRIGRAMS: ReadonlyArray<readonly [string, string]> = [
  ["乾", "☰"], ["兑", "☱"], ["离", "☲"], ["震", "☳"],
  ["巽", "☴"], ["坎", "☵"], ["艮", "☶"], ["坤", "☷"],
];

const normTrigram = (t: string) => (({ "離": "离", "兌": "兑" } as Record<string, string>)[t] ?? t);

// ---- indexes, built once at module scope from the base book (zhouyi) ----
const base = BOOKS[0].items;
const byKwMap = new Map<number, HexagramItem>();
const byBinMap = new Map<string, number>();
const byPairMap = new Map<string, number>();
for (const it of base) {
  byKwMap.set(it.metadata.king_wen, it);
  if (it.metadata.binary_bottom_first) byBinMap.set(it.metadata.binary_bottom_first, it.metadata.king_wen);
  if (it.metadata.trigram_lower && it.metadata.trigram_upper) {
    byPairMap.set(normTrigram(it.metadata.trigram_lower) + "|" + normTrigram(it.metadata.trigram_upper), it.metadata.king_wen);
  }
}

export function hexagram(kw: number): HexagramItem {
  const it = byKwMap.get(kw);
  if (!it) throw new Error(`no hexagram ${kw}`);
  return it;
}

export const kingWenByBinary = (binaryBottomFirst: string) => byBinMap.get(binaryBottomFirst);
export const kingWenByPair = (lower: string, upper: string) =>
  byPairMap.get(normTrigram(lower) + "|" + normTrigram(upper));

export function bookItem(slug: string, kw: number): HexagramItem | undefined {
  const book = BOOKS.find((b) => b.slug === slug);
  return book?.items.find((i) => i.metadata.king_wen === kw);
}

/** The six hexagrams one changed line away, bottom line first. */
export function neighbors(kw: number): { line: number; kw: number }[] {
  const bin = hexagram(kw).metadata.binary_bottom_first!;
  const out: { line: number; kw: number }[] = [];
  for (let i = 0; i < 6; i++) {
    const flipped = bin.slice(0, i) + (bin[i] === "1" ? "0" : "1") + bin.slice(i + 1);
    const nkw = byBinMap.get(flipped);
    if (nkw) out.push({ line: i + 1, kw: nkw });
  }
  return out;
}

// ---- casting ----
export type CastMethod = "coins" | "yarrow";

/** One line: 6 old yin · 7 young yang · 8 young yin · 9 old yang.
 *  Coins: 1/8 · 3/8 · 3/8 · 1/8.  Yarrow: 1/16 · 5/16 · 7/16 · 3/16. */
export function castLine(method: CastMethod, rand: () => number = Math.random): 6 | 7 | 8 | 9 {
  if (method === "coins") {
    let s = 0;
    for (let i = 0; i < 3; i++) s += rand() < 0.5 ? 2 : 3;
    return s as 6 | 7 | 8 | 9;
  }
  const r = Math.floor(rand() * 16);
  return r < 1 ? 6 : r < 6 ? 7 : r < 13 ? 8 : 9;
}

export interface Cast {
  casts: number[];        // six values 6–9, bottom line first
  moving: number[];       // 1-based positions of moving lines
  primaryKw: number;      // 本卦
  resultKw: number;       // 之卦 (equals primaryKw when nothing moves)
}

export function performCast(method: CastMethod, rand: () => number = Math.random): Cast {
  const casts = Array.from({ length: 6 }, () => castLine(method, rand));
  const primaryBin = casts.map((c) => (c % 2 === 1 ? "1" : "0")).join("");
  const resultBin = casts.map((c) => (c === 6 ? "1" : c === 9 ? "0" : c % 2 === 1 ? "1" : "0")).join("");
  const moving = casts.flatMap((c, i) => (c === 6 || c === 9 ? [i + 1] : []));
  return {
    casts,
    moving,
    primaryKw: byBinMap.get(primaryBin)!,
    resultKw: byBinMap.get(resultBin)!,
  };
}

/** Pick individual rows out of a per-line markdown section (one 爻 per row, bottom first). */
export function pickLines(sectionText: string | undefined, wanted: number[]): string[] {
  if (!sectionText) return [];
  const rows = sectionText.split("\n");
  return wanted.map((k) => rows[k - 1]).filter(Boolean);
}

/** Minimal renderer for the grammars' markdown-bold: escape, then **x** → <b>x</b>. */
export function mdBoldHtml(text: string): string {
  const esc = text.replace(/[&<>]/g, (c) => (({ "&": "&amp;", "<": "&lt;", ">": "&gt;" } as Record<string, string>)[c]!));
  return esc.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
}
