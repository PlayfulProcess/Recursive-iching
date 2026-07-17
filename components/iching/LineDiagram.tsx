/** Six lines of a hexagram, bottom line first; moving lines marked gold with ✶. */
export function LineDiagram({ binary, moving = [] }: { binary: string; moving?: number[] }) {
  return (
    <div className="mx-auto flex w-28 flex-col-reverse gap-1.5" aria-hidden>
      {binary.split("").map((b, i) => {
        const isMoving = moving.includes(i + 1);
        const bar = isMoving ? "bg-amber-600" : "bg-gray-800";
        return (
          <div key={i} className="relative flex h-2.5 justify-center gap-2">
            {b === "1" ? (
              <span className={`h-full flex-1 rounded-sm ${bar}`} />
            ) : (
              <>
                <span className={`h-full flex-1 rounded-sm ${bar}`} />
                <span className="h-full w-4" />
                <span className={`h-full flex-1 rounded-sm ${bar}`} />
              </>
            )}
            {isMoving && <span className="absolute -right-5 -top-1 text-xs text-amber-600">✶</span>}
          </div>
        );
      })}
    </div>
  );
}
