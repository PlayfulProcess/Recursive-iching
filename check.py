#!/usr/bin/env python3
"""Minimal grammar gate for a starter site — run before you commit.

Walks grammars/*/grammar.json (or pass paths as args), validates each
against the canonical shape in GRAMMAR_FORMAT.md, and fails loud on the three
mistakes that keep a grammar from loading. Zero dependencies.

It also enforces this repo's image policy (GRAMMAR_FORMAT.md "Image provenance",
registry in docs/IMAGES.md): every image URL a grammar carries must have a
matching `_image_provenance` entry naming its file page and public-domain basis,
and no two grammars may wear the same cover — a library where three books show
the same stock photograph is telling the reader nothing.

    python check.py            # check every grammar under grammars/
    python check.py path.json  # check one file
"""
import json
import sys
from pathlib import Path

VALID_TYPES = {
    "tarot", "iching", "astrology", "sequence",
    "course", "prompt", "birthchart", "altar", "music", "custom",
}

PROVENANCE_FIELDS = ("url", "title", "creator", "date", "file_page", "pd_basis")


def image_urls(g: dict) -> list[str]:
    """Every image URL a grammar points at, in declaration order, deduped."""
    urls = []
    for key in ("cover_image_url", "thumbnail_url"):
        if g.get(key):
            urls.append(g[key])
    for it in g.get("items") or []:
        if isinstance(it, dict) and it.get("image_url"):
            urls.append(it["image_url"])
    return list(dict.fromkeys(urls))


def check_images(path: Path, g: dict) -> list[str]:
    errs = []
    prov = g.get("_image_provenance") or []
    if not isinstance(prov, list):
        return [f"{path}: '_image_provenance' must be an array"]
    documented = {}
    for entry in prov:
        if not isinstance(entry, dict):
            errs.append(f"{path}: every _image_provenance entry must be an object")
            continue
        missing = [f for f in PROVENANCE_FIELDS if not entry.get(f)]
        if missing:
            errs.append(
                f"{path}: _image_provenance entry {entry.get('url') or '?'} is missing {missing} "
                f"— an unverified image is worse than no image"
            )
        if entry.get("url"):
            documented[entry["url"]] = entry
    for url in image_urls(g):
        if url not in documented:
            errs.append(
                f"{path}: image {url} has no _image_provenance entry "
                f"(record title, creator, date, file_page, pd_basis — see docs/IMAGES.md)"
            )
    for url in documented:
        if url not in image_urls(g):
            errs.append(f"{path}: _image_provenance documents {url}, which no image field uses")
    return errs


def check(path: Path) -> list[str]:
    errs = []
    try:
        g = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"{path}: not valid JSON — {e}"]

    for field in ("name", "description", "grammar_type"):
        if field not in g:
            errs.append(f"{path}: missing required top-level '{field}'")
    if g.get("grammar_type") not in VALID_TYPES:
        errs.append(f"{path}: grammar_type '{g.get('grammar_type')}' is not one of {sorted(VALID_TYPES)}")
    if "emergences" in g:
        errs.append(f"{path}: has a top-level 'emergences' array — move those items into items[] with composite_of")
    items = g.get("items")
    if not isinstance(items, list) or not items:
        errs.append(f"{path}: 'items' must be a non-empty array")
        return errs

    ids = {it.get("id") for it in items}
    for it in items:
        for field in ("id", "name", "sections"):
            if field not in it:
                errs.append(f"{path}: item {it.get('id') or it.get('name') or '?'} missing '{field}'")
        for child in it.get("composite_of", []):
            if child not in ids:
                errs.append(f"{path}: composite_of references missing id '{child}'")
        meta = it.get("metadata") or {}
        if "video_id" in meta:
            errs.append(f"{path}: item {it.get('id')} uses metadata.video_id — rename to youtube_video_id")
    errs += check_images(path, g)
    return errs


def main() -> int:
    args = sys.argv[1:]
    root = Path(__file__).parent
    paths = [Path(a) for a in args] if args else sorted(root.glob("grammars/*/grammar.json"))
    if not paths:
        print("No grammars found under grammars/*/grammar.json")
        return 1
    all_errs = []
    covers: dict[str, list[str]] = {}
    for p in paths:
        all_errs += check(p)
        try:
            g = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — already reported by check()
            continue
        if g.get("cover_image_url"):
            covers.setdefault(g["cover_image_url"], []).append(str(p))
    for url, users in covers.items():
        if len(users) > 1:
            all_errs.append(
                f"{len(users)} grammars share the cover {url} ({', '.join(users)}) — "
                f"one repeated picture across a library says nothing about any of the books"
            )
    if all_errs:
        print("\n".join(all_errs))
        print(f"\nFAILED: {len(all_errs)} problem(s) across {len(paths)} grammar(s)")
        return 1
    print(f"OK: all checks passed ({len(paths)} grammar{'s' if len(paths) != 1 else ''})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
