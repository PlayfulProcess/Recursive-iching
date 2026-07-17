import Link from "next/link";
import { TRIGRAMS, kingWenByPair, hexagram } from "@/lib/iching";

/** The 8×8 trigram matrix — the space's native coordinates. Pure links; no client JS.
 *  Rows: lower trigram · Columns: upper trigram. */
export function HexagramMatrix({ currentKw, booksQuery }: { currentKw: number; booksQuery: string }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-3">
      <div className="grid grid-cols-9 gap-0.5">
        <span className="flex items-center justify-center text-[10px] text-gray-400">下↓ 上→</span>
        {TRIGRAMS.map(([, glyph]) => (
          <span key={glyph} className="flex items-center justify-center text-sm text-gray-500">{glyph}</span>
        ))}
        {TRIGRAMS.map(([lowerName, lowerGlyph]) => (
          <Row key={lowerName} lowerName={lowerName} lowerGlyph={lowerGlyph} currentKw={currentKw} booksQuery={booksQuery} />
        ))}
      </div>
      <p className="mt-2 text-[11px] text-gray-400">Rows: lower trigram · columns: upper — pick a place in the space.</p>
    </div>
  );
}

function Row({ lowerName, lowerGlyph, currentKw, booksQuery }: {
  lowerName: string; lowerGlyph: string; currentKw: number; booksQuery: string;
}) {
  return (
    <>
      <span className="flex items-center justify-center text-sm text-gray-500">{lowerGlyph}</span>
      {TRIGRAMS.map(([upperName]) => {
        const kw = kingWenByPair(lowerName, upperName)!;
        const it = hexagram(kw);
        const active = kw === currentKw;
        return (
          <Link
            key={upperName}
            href={`/hexagram/${kw}${booksQuery}`}
            title={it.name}
            className={`flex items-center justify-center rounded-md py-1 text-xl leading-none transition-colors ${
              active ? "bg-amber-600 text-white" : "hover:bg-amber-50 hover:text-amber-800"
            }`}
          >
            {it.metadata.unicode}
          </Link>
        );
      })}
    </>
  );
}
