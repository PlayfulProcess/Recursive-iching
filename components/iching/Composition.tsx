import Link from "next/link";
import { structureOf } from "@/lib/iching";

/** "How it is built" — the compositional axis on a hexagram page: the two
 *  trigrams (below/above) with the builder's Brief Translations, linking to
 *  the full emergence at /structure. Bridged on King Wen; renders nothing if
 *  the structural grammar has no entry. */
export function Composition({ kw }: { kw: number }) {
  const s = structureOf(kw);
  if (!s) return null;
  const pair = [
    { role: "above · 上", t: s.upper },
    { role: "below · 下", t: s.lower },
  ];
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4">
      <h3 className="mb-2 text-sm font-semibold text-gray-700">
        How it is built <span className="font-normal text-gray-400">— {s.hexagram.name}</span>
      </h3>
      <div className="space-y-3">
        {pair.map(({ role, t }) => t && (
          <Link key={t.id} href={`/structure#${t.id}`} className="block rounded-lg border border-gray-100 p-3 transition-colors hover:border-amber-600">
            <div className="flex items-center gap-3">
              <span className="text-2xl leading-none">{t.symbol}</span>
              <div>
                <div className="text-sm font-medium">{t.name} <span className="text-xs text-gray-400">{role}</span></div>
                {t.sections["Nature"] && (
                  <div className="text-xs text-gray-500">{t.sections["Nature"].split("\n")[0]}</div>
                )}
              </div>
            </div>
          </Link>
        ))}
      </div>
      <p className="mt-2 text-xs text-gray-400">
        Change is composed: two lines → eight trigrams → this. <Link href="/structure" className="underline">Walk the whole structure →</Link>
      </p>
    </div>
  );
}
