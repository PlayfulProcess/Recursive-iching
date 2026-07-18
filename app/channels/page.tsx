import type { Metadata } from "next";
import Link from "next/link";
import { BOOKS } from "@/lib/iching";
import emergentGrammar from "@/grammars/emergent-structure/grammar.json";
import leibnizGrammar from "@/grammars/leibniz-binary-tree/grammar.json";
import idsFile from "@/ids.json";

/* The Channels — this repo's grammars as channel cards, plus the family.
   The family pattern (tarot pages/channels.html is the canon); here it is a
   server component reading the same data the repo already carries. */

export const metadata: Metadata = {
  title: "Channels · Recursive I Ching",
  description: "Every grammar in the Recursive I Ching — the books across time, the compositional structures — and the rest of the recursive.eco family.",
};

const APP_CHANNEL = "https://flow.recursive.eco/library/channels/iching";

export default function ChannelsPage() {
  const ids = (idsFile as { ids: Record<string, string>; _public_now?: string[] }).ids;
  const publicNow = new Set((idsFile as { _public_now?: string[] })._public_now ?? []);

  const cards = [
    ...BOOKS.map((b) => ({
      slug: b.slug, name: b.label + " — " + b.era, axis: "historical axis · a book on the time rail",
      items: b.items.length, href: "/hexagram/1?books=" + b.slug,
    })),
    {
      slug: "emergent-structure",
      name: (emergentGrammar as unknown as { name: string }).name,
      axis: "compositional axis · lines → trigrams → hexagrams",
      items: (emergentGrammar as unknown as { items: unknown[] }).items.length,
      href: "/structure",
    },
    {
      slug: "leibniz-binary-tree",
      name: (leibnizGrammar as unknown as { name: string }).name,
      axis: "compositional axis · the 6-D binary hypercube Leibniz saw",
      items: (leibnizGrammar as unknown as { items: unknown[] }).items.length,
      href: "/structure",
    },
  ];

  return (
    <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <h1 className="text-center text-3xl font-semibold">
        The <span className="text-amber-700">Channels</span>
      </h1>
      <p className="mx-auto mt-2 max-w-xl text-center text-sm italic text-gray-500">
        Every grammar in this library — none of them &quot;the true one.&quot; Read to know yourself,
        not to be told your fate; relate to the hexagram, never obey it.
      </p>
      <div className="mt-4 text-center">
        <a href={APP_CHANNEL} target="_blank" rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-5 py-2 text-sm font-semibold text-violet-700 hover:border-violet-500">
          Open this channel in recursive.eco ↗
        </a>
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {cards.map((c) => (
          <div key={c.slug + c.name} className="flex flex-col rounded-xl border border-gray-200 bg-white p-5">
            <h2 className="text-base font-semibold leading-snug">{c.name}</h2>
            <p className="mt-1 text-xs text-gray-500">{c.axis}</p>
            <div className="mt-2 text-xs text-gray-400">{c.items} items</div>
            <div className="mt-auto flex items-center gap-3 pt-3 text-sm">
              <Link href={c.href} className="font-semibold text-gray-800 hover:text-amber-700">Read here →</Link>
              {ids[c.slug] && publicNow.has(c.slug) ? (
                <a className="ml-auto font-semibold text-violet-700 hover:text-violet-500"
                  href={`https://flow.recursive.eco/?deckId=${ids[c.slug]}`} target="_blank" rel="noopener noreferrer">
                  recursive.eco ↗
                </a>
              ) : (
                <span className="ml-auto text-xs italic text-gray-400">not yet published</span>
              )}
            </div>
          </div>
        ))}
      </div>

      <h2 className="mb-3 mt-10 text-lg font-semibold">The family</h2>
      <div className="grid gap-4 sm:grid-cols-3">
        <a href="https://tarot.recursive.eco" className="rounded-xl border border-gray-200 bg-white p-4 hover:border-amber-600">
          <div className="font-semibold">The Recursive Tarot</div>
          <p className="mt-1 text-xs text-gray-500">A public-domain genealogy of the cards — the museum wing. Card × deck.</p>
        </a>
        <a href="https://github.com/PlayfulProcess/Recursive-astrology" className="rounded-xl border border-gray-200 bg-white p-4 hover:border-amber-600">
          <div className="font-semibold">The Recursive Astrology</div>
          <p className="mt-1 text-xs text-gray-500">Grammars of the sky, none flattened into &quot;the true one.&quot; Sky-object × tradition.</p>
        </a>
        <a href="https://recursive.eco" className="rounded-xl border border-gray-200 bg-white p-4 hover:border-amber-600">
          <div className="font-semibold">recursive.eco</div>
          <p className="mt-1 text-xs text-gray-500">The living app — cast, fork, edit, and keep what you make.</p>
        </a>
      </div>
    </main>
  );
}
