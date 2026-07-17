"use client";

import { useState } from "react";
import Link from "next/link";
import {
  performCast, hexagram, bookItem, pickLines, mdBoldHtml,
  type Cast, type CastMethod,
} from "@/lib/iching";
import { LineDiagram } from "@/components/iching/LineDiagram";

/* The Caster — a cast is a path: six lines build the primary hexagram (本卦),
   and its moving lines carry it into the resulting one (之卦). The moving
   lines' 爻辞 (and their 小象) are exactly the texts read. Client component;
   all math lives in lib/iching (verified against the static reference). */

const METHOD_NOTE: Record<CastMethod, string> = {
  coins: "Three coins per line: 6 old yin ⅛ · 7 young yang ⅜ · 8 young yin ⅜ · 9 old yang ⅛.",
  yarrow: "Yarrow distribution per line: 6 old yin 1/16 · 7 young yang 5/16 · 8 young yin 7/16 · 9 old yang 3/16 — the stalks are biased toward change in yang.",
};

export default function CastPage() {
  const [method, setMethod] = useState<CastMethod>("coins");
  const [cast, setCast] = useState<Cast | null>(null);

  const A = cast ? hexagram(cast.primaryKw) : null;
  const B = cast ? hexagram(cast.resultKw) : null;

  return (
    <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <h1 className="text-center text-3xl font-semibold">
        The <span className="text-amber-700">Caster</span>
      </h1>
      <p className="mx-auto mt-2 max-w-xl text-center text-sm italic text-gray-500">
        A cast is a path: six lines build the primary hexagram, and its moving lines carry it into
        another. Read to know yourself, not to be told your fate — relate to the hexagram, never obey it.
      </p>

      <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
        <div className="inline-flex overflow-hidden rounded-full border border-gray-200 bg-white">
          {(["coins", "yarrow"] as const).map((m) => (
            <button key={m} onClick={() => setMethod(m)}
              className={`px-4 py-2 text-sm ${method === m ? "bg-amber-600 text-white" : "text-gray-700 hover:bg-gray-50"}`}>
              {m === "coins" ? "Three coins" : "Yarrow distribution"}
            </button>
          ))}
        </div>
        <button onClick={() => setCast(performCast(method))}
          className="rounded-full bg-amber-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-amber-700">
          Cast six lines
        </button>
      </div>
      <p className="mt-2 text-center text-xs italic text-gray-400">{METHOD_NOTE[method]}</p>

      {cast && A && B && (
        <>
          <div className="mt-8 grid items-start gap-4 sm:grid-cols-[1fr_auto_1fr]">
            <HexCard item={A} role="本卦 · primary" moving={cast.moving} />
            <div className="self-center text-center text-2xl text-gray-400">
              {cast.moving.length ? "→" : "·"}
              <span className="block text-xs">
                {cast.moving.length
                  ? `${cast.moving.length} moving line${cast.moving.length > 1 ? "s" : ""}`
                  : "no movement"}
              </span>
            </div>
            <div className={cast.moving.length ? "" : "opacity-40"}>
              <HexCard item={B} role="之卦 · becomes" moving={[]} />
            </div>
          </div>

          <Reading cast={cast} />
        </>
      )}
    </main>
  );
}

function HexCard({ item, role, moving }: {
  item: NonNullable<ReturnType<typeof hexagram>>; role: string; moving: number[];
}) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 text-center">
      <div className="text-xs uppercase tracking-widest text-gray-400">{role}</div>
      <div className="text-5xl leading-tight">{item.metadata.unicode}</div>
      <div className="my-3"><LineDiagram binary={item.metadata.binary_bottom_first!} moving={moving} /></div>
      <h2 className="text-lg font-semibold">
        <Link href={`/hexagram/${item.metadata.king_wen}`} className="hover:text-amber-700">{item.name}</Link>
      </h2>
      <div className="text-xs text-gray-400">{item.subcategory}</div>
    </div>
  );
}

function Reading({ cast }: { cast: Cast }) {
  const A = hexagram(cast.primaryKw);
  const B = hexagram(cast.resultKw);
  const allSixSpecial = cast.moving.length === 6 && (cast.primaryKw === 1 || cast.primaryKw === 2);
  const movingTexts = pickLines(A.sections["爻辞 · Lines (original)"], cast.moving);
  const tw = bookItem("ten-wings", cast.primaryKw);
  const smallImages = tw ? pickLines(tw.sections["小象 · Small Images (per line)"], cast.moving) : [];
  const seventh = A.sections["爻辞 · Lines (original)"]?.split("\n")[6];

  return (
    <div className="mt-8">
      <Block title={`${A.name} — the judgment`} sub="卦辞 (original)" html={mdBoldHtml(A.sections["卦辞 · Judgment (original)"] ?? "")} />

      {cast.moving.length === 0 ? (
        <p className="text-sm italic text-gray-500">
          No moving lines: the reading rests in the primary hexagram.{" "}
          <Link href={`/hexagram/${cast.primaryKw}`} className="underline">Read it across the centuries →</Link>
        </p>
      ) : allSixSpecial ? (
        <>
          <Block title="The path — all six lines move" sub="the seventh text (用九 / 用六)" html={mdBoldHtml(seventh ?? "")}
            note="Hexagrams 1 and 2 alone carry a text for exactly this cast." />
          <Arrival B={B} />
        </>
      ) : (
        <>
          <Block title="The path — the moving lines speak"
            sub={`爻辞 of the moving line${cast.moving.length > 1 ? "s" : ""} (original)`}
            html={movingTexts.map(mdBoldHtml).join("<br/><br/>")} />
          {smallImages.length > 0 && (
            <Block title="" sub="小象 on those lines (Ten Wings)" html={smallImages.map(mdBoldHtml).join("<br/><br/>")} />
          )}
          <Arrival B={B} />
        </>
      )}
    </div>
  );
}

function Arrival({ B }: { B: ReturnType<typeof hexagram> }) {
  return (
    <Block title={`${B.name} — where it arrives`} sub="卦辞 (original)"
      html={mdBoldHtml(B.sections["卦辞 · Judgment (original)"] ?? "")}
      note={`Read it across the centuries in `} noteLinkKw={B.metadata.king_wen} />
  );
}

function Block({ title, sub, html, note, noteLinkKw }: {
  title: string; sub: string; html: string; note?: string; noteLinkKw?: number;
}) {
  return (
    <div className="mb-4">
      {title && <h3 className="mb-1 text-lg font-semibold">{title}</h3>}
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <h4 className="mb-1 text-sm font-medium tracking-wide text-amber-700">{sub}</h4>
        <p className="whitespace-pre-wrap leading-relaxed" dangerouslySetInnerHTML={{ __html: html }} />
        {note && (
          <p className="mt-2 text-xs italic text-gray-400">
            {note}
            {noteLinkKw && <Link href={`/hexagram/${noteLinkKw}`} className="underline">the Books →</Link>}
          </p>
        )}
      </div>
    </div>
  );
}
