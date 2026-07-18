import Link from "next/link";
import type { Metadata } from "next";
import { LINES, EMERGENT_TRIGRAMS, TRIGRAMS, kingWenByPair, hexagram, mdBoldHtml } from "@/lib/iching";

/* The Structure — the I Ching's core message, rendered: change is composed.
   Two primordial lines → eight trigrams → sixty-four hexagrams, from the
   builder's Emergent Structure grammar (compositional axis; traditional
   characters; the builder's own Brief Translations). Server-rendered, pure
   links — the play is in the walking, not in widgets. */

export const metadata: Metadata = {
  title: "The Structure · Recursive I Ching",
  description: "Change is composed: two lines become eight trigrams become sixty-four hexagrams. The I Ching's own emergence, walkable.",
};

const TRIGRAM_ID_BY_GLYPH: Record<string, string> = {
  "☰": "trigram-heaven", "☱": "trigram-lake", "☲": "trigram-fire", "☳": "trigram-thunder",
  "☴": "trigram-wind", "☵": "trigram-water", "☶": "trigram-mountain", "☷": "trigram-earth",
};

export default function StructurePage() {
  const trigramById = new Map(EMERGENT_TRIGRAMS.map((t) => [t.id, t]));

  return (
    <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <h1 className="text-center text-3xl font-semibold">
        The <span className="text-amber-700">Structure</span>
      </h1>
      <p className="mx-auto mt-2 max-w-2xl text-center text-sm italic text-gray-500">
        The I Ching&apos;s deepest message is its own shape: everything is made of change, and change
        is made of two moves. One yin, one yang — eight trigrams — sixty-four hexagrams. Walk it.
      </p>

      {/* Tier 1 — the two lines */}
      <h2 className="mb-3 mt-10 text-lg font-semibold">Two lines <span className="text-sm font-normal text-gray-400">兩儀 — the whole alphabet</span></h2>
      <div className="grid gap-4 sm:grid-cols-2">
        {LINES.map((l) => (
          <div key={l.id} className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="mb-2 flex items-center gap-3">
              <span className="text-3xl leading-none">{l.id === "yang-line" ? "⚊" : "⚋"}</span>
              <h3 className="text-lg font-semibold">{l.name}</h3>
            </div>
            {l.sections["Nature"] && (
              <p className="whitespace-pre-wrap text-sm leading-relaxed"
                dangerouslySetInnerHTML={{ __html: mdBoldHtml(l.sections["Nature"]) }} />
            )}
            {l.sections["Brief Translation"] && (
              <p className="mt-2 text-sm italic text-gray-500">{l.sections["Brief Translation"]}</p>
            )}
          </div>
        ))}
      </div>

      {/* Tier 2 — the eight trigrams */}
      <h2 className="mb-3 mt-10 text-lg font-semibold">Eight trigrams <span className="text-sm font-normal text-gray-400">八卦 — three lines each</span></h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {EMERGENT_TRIGRAMS.map((t) => (
          <div key={t.id} id={t.id} className="rounded-xl border border-gray-200 bg-white p-4">
            <div className="mb-1 flex items-center gap-2">
              <span className="text-3xl leading-none">{t.symbol}</span>
              <h3 className="text-base font-semibold">{t.name}</h3>
            </div>
            {t.sections["Nature"] && (
              <p className="text-xs leading-relaxed text-gray-600">{t.sections["Nature"].split("\n")[0]}</p>
            )}
            {t.sections["Brief Translation"] && (
              <p className="mt-2 text-xs italic text-gray-500 line-clamp-3">{t.sections["Brief Translation"]}</p>
            )}
          </div>
        ))}
      </div>

      {/* Tier 3 — the sixty-four */}
      <h2 className="mb-1 mt-10 text-lg font-semibold">Sixty-four hexagrams <span className="text-sm font-normal text-gray-400">六十四卦 — every pair of trigrams</span></h2>
      <p className="mb-3 text-sm text-gray-500">Rows: lower trigram · columns: upper. Every cell opens the hexagram read across the centuries.</p>
      <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white p-3">
        <div className="grid min-w-[560px] grid-cols-9 gap-1">
          <span className="flex items-center justify-center text-[10px] text-gray-400">下↓ 上→</span>
          {TRIGRAMS.map(([, glyph]) => {
            const t = trigramById.get(TRIGRAM_ID_BY_GLYPH[glyph]);
            return <span key={glyph} title={t?.name} className="flex items-center justify-center text-base text-gray-500">{glyph}</span>;
          })}
          {TRIGRAMS.map(([lowerName, lowerGlyph]) => (
            <Row key={lowerName} lowerName={lowerName} lowerGlyph={lowerGlyph} />
          ))}
        </div>
      </div>

      <p className="mt-6 text-center text-sm text-gray-500">
        Cast a path through this space in <Link href="/cast" className="underline">the Caster</Link>,
        or start reading at <Link href="/hexagram/1" className="underline">hexagram 1</Link>.
      </p>
    </main>
  );
}

function Row({ lowerName, lowerGlyph }: { lowerName: string; lowerGlyph: string }) {
  return (
    <>
      <span className="flex items-center justify-center text-base text-gray-500">{lowerGlyph}</span>
      {TRIGRAMS.map(([upperName]) => {
        const kw = kingWenByPair(lowerName, upperName)!;
        const it = hexagram(kw);
        return (
          <Link key={upperName} href={`/hexagram/${kw}`} title={it.name}
            className="flex flex-col items-center rounded-md py-1 leading-none transition-colors hover:bg-amber-50">
            <span className="text-xl">{it.metadata.unicode}</span>
            <span className="text-[9px] text-gray-400">{kw}</span>
          </Link>
        );
      })}
    </>
  );
}
