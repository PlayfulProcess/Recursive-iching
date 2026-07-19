import Link from "next/link";
import type { Metadata } from "next";
import { BOOKS, DEFAULT_BOOK_SLUGS, hexagram, bookItem, neighbors, mdBoldHtml } from "@/lib/iching";
import { HexagramMatrix } from "@/components/iching/HexagramMatrix";
import { LineDiagram } from "@/components/iching/LineDiagram";
import { Composition } from "@/components/iching/Composition";

/* The time×space reader as 64 real pages (docs/TIME-AND-SPACE.md):
   the matrix moves you through space; the book rail toggles the centuries.
   Fully server-rendered — every hexagram is a shareable, indexable URL. */

export function generateStaticParams() {
  return Array.from({ length: 64 }, (_, i) => ({ kw: String(i + 1) }));
}

type Params = { kw: string };
type Search = { books?: string };

function parseBooks(search: Search): string[] {
  const asked = (search.books ?? "").split(",").filter(Boolean);
  const valid = asked.filter((s) => BOOKS.some((b) => b.slug === s));
  return valid.length ? valid : DEFAULT_BOOK_SLUGS;
}

const booksQuery = (slugs: string[]) =>
  slugs.length === DEFAULT_BOOK_SLUGS.length ? "" : `?books=${slugs.join(",")}`;

// The July 2026 canonical-format alignment (commit 17016a3) added English-labeled
// section aliases (Judgment / Image / Line 1-6) so the grammars render in
// recursive.eco's card viewer. The time-rail reading pane shows the curated
// bilingual-labeled originals (卦辞·/彖传·/…) instead, so these aliases are hidden
// here to avoid showing every text twice.
const HIDDEN_SECTIONS = new Set([
  "Research note", "Judgment", "Image",
  "Line 1", "Line 2", "Line 3", "Line 4", "Line 5", "Line 6",
]);

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const kw = Number((await params).kw);
  const it = hexagram(kw);
  return {
    title: `${it.name} · Recursive I Ching`,
    description: `Hexagram ${kw} (${it.metadata.name_traditional}, ${it.metadata.pinyin}) read across the books of the I Ching tradition — the Zhouyi core, the Ten Wings, and the layers to come.`,
  };
}

export default async function HexagramPage({ params, searchParams }: {
  params: Promise<Params>;
  searchParams: Promise<Search>;
}) {
  const kw = Math.min(64, Math.max(1, Number((await params).kw) || 1));
  const active = parseBooks(await searchParams);
  const it = hexagram(kw);
  const q = booksQuery(active);
  const nbs = neighbors(kw);

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <p className="mb-6 text-center text-sm italic text-gray-500">
        One hexagram, many centuries. Read to know yourself, not to be told your fate —
        relate to the hexagram, never obey it.
      </p>

      <div className="grid gap-6 md:grid-cols-[minmax(280px,340px)_1fr]">
        <aside className="space-y-4">
          <HexagramMatrix currentKw={kw} booksQuery={q} />
          <div className="rounded-xl border border-gray-200 bg-white p-4">
            <h3 className="mb-2 text-sm font-semibold text-gray-700">One line changes — six neighbors</h3>
            <div className="flex flex-wrap gap-1.5">
              {nbs.map(({ line, kw: nkw }) => (
                <Link key={line} href={`/hexagram/${nkw}${q}`}
                  className="inline-flex items-center gap-1 rounded-full border border-gray-200 px-2.5 py-0.5 text-sm hover:border-amber-600">
                  <span>{hexagram(nkw).metadata.unicode}</span>
                  <span>{nkw}</span>
                  <span className="text-xs text-gray-400">line {line}</span>
                </Link>
              ))}
            </div>
            <p className="mt-2 text-xs text-gray-400">
              A moving line in a cast walks exactly one of these steps — <Link href="/cast" className="underline">cast a path</Link>.
            </p>
          </div>
          <Composition kw={kw} />
        </aside>

        <section>
          {/* the time rail */}
          <div className="mb-4 flex flex-wrap gap-2">
            {BOOKS.map((b) => {
              const on = active.includes(b.slug);
              const next = on ? active.filter((s) => s !== b.slug) : [...active, b.slug].sort(
                (x, y) => BOOKS.findIndex((k) => k.slug === x) - BOOKS.findIndex((k) => k.slug === y));
              const target = next.length ? next : [BOOKS[0].slug];
              return (
                <Link key={b.slug} href={`/hexagram/${kw}?books=${target.join(",")}`}
                  className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
                    on ? "border-amber-600 bg-amber-600 text-white" : "border-gray-200 bg-white text-gray-700 hover:border-amber-600"
                  }`}>
                  {b.label}
                  <span className="block text-[11px] opacity-75">{b.era}</span>
                </Link>
              );
            })}
          </div>

          <div className="mb-4 flex items-center gap-4">
            <span className="text-5xl leading-none">{it.metadata.unicode}</span>
            <div>
              <h1 className="text-2xl font-semibold">{it.name}</h1>
              <p className="text-sm text-gray-500">{it.subcategory} · King Wen {kw}</p>
            </div>
            <div className="ml-auto hidden sm:block">
              <LineDiagram binary={it.metadata.binary_bottom_first!} />
            </div>
          </div>

          {BOOKS.filter((b) => active.includes(b.slug)).map((b) => {
            const bi = bookItem(b.slug, kw);
            return (
              <article key={b.slug} className="mb-4 rounded-xl border border-gray-200 bg-white p-5">
                <h2 className="text-lg font-semibold">{b.label}</h2>
                <p className="mb-3 text-xs text-gray-400">{b.era}</p>
                {!bi ? (
                  <p className="italic text-gray-400">This book has no text for this hexagram.</p>
                ) : (
                  Object.entries(bi.sections)
                    .filter(([sec]) => !HIDDEN_SECTIONS.has(sec))
                    .map(([sec, text]) => (
                      <div key={sec} className="mb-3">
                        <h3 className="mb-1 text-sm font-medium tracking-wide text-amber-700">{sec}</h3>
                        <p className="whitespace-pre-wrap leading-relaxed"
                          dangerouslySetInnerHTML={{ __html: mdBoldHtml(text) }} />
                      </div>
                    ))
                )}
              </article>
            );
          })}

          <p className="text-xs text-gray-400">
            Texts are public domain; provenance lives in each grammar&apos;s <code>_grammar_commons</code>{" "}
            (<a className="underline" href="https://github.com/PlayfulProcess/Recursive-iching">source</a>).
            English translation slots are deliberately empty for now.
          </p>
        </section>
      </div>
    </main>
  );
}
