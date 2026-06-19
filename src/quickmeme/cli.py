from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quickmeme import share
from quickmeme.catalog import Template, get, load_all, search
from quickmeme.render import render


def _as_dict(template: Template) -> dict:
    return {
        "id": template.id,
        "name": template.name,
        "box_count": template.box_count,
        "keywords": list(template.keywords),
        "example": list(template.example),
    }


def _boxes_label(template: Template) -> str:
    return f"{template.box_count} box" + ("es" if template.box_count != 1 else "")


def _print_table(templates: list[Template]) -> None:
    if not templates:
        print("No matching templates.")
        return
    width = max(len(t.id) for t in templates)
    for t in templates:
        example = "  ".join(f'"{e}"' for e in t.example)
        line = f"{t.id:<{width}}  {_boxes_label(t):<8}  {t.name}"
        print(line + (f"   e.g. {example}" if example else ""))


def _deliver(template_id: str, texts: list[str], out: Path, *, copy: bool, open_: bool) -> None:
    render(template_id, texts, out)
    print(out)
    if copy:
        if share.copy_to_clipboard(out):
            print("Copied to clipboard.")
        else:
            print("(clipboard unavailable — install xclip or wl-copy)", file=sys.stderr)
    if open_:
        share.open_file(out)


def _cmd_list(args) -> int:
    templates = list(load_all())
    if args.json:
        print(json.dumps([_as_dict(t) for t in templates], indent=2))
    else:
        _print_table(templates)
        print(f"\n{len(templates)} templates.")
    return 0


def _cmd_search(args) -> int:
    templates = search(args.query)
    if args.json:
        print(json.dumps([_as_dict(t) for t in templates], indent=2))
    else:
        _print_table(templates)
    return 0


def _cmd_make(args) -> int:
    try:
        template = get(args.template)
    except KeyError:
        hits = search(args.template)
        print(f"Unknown template '{args.template}'.", file=sys.stderr)
        if hits:
            print("Did you mean: " + ", ".join(t.id for t in hits[:5]), file=sys.stderr)
        return 1

    if len(args.text) != template.box_count:
        print(
            f"Note: '{template.id}' has {template.box_count} text box(es), "
            f"you gave {len(args.text)}.",
            file=sys.stderr,
        )

    out = Path(args.out) if args.out else share.output_path(template.id)
    _deliver(template.id, args.text, out, copy=not args.no_copy, open_=not args.no_open)
    return 0


def _interactive() -> int:
    query = input("Search templates (or press Enter to list popular ones): ").strip()
    results = (search(query) if query else list(load_all()))[:20]
    if not results:
        print("No matching templates.")
        return 1
    for i, t in enumerate(results, 1):
        example = "  ".join(f'"{e}"' for e in t.example)
        print(f"{i:>2}) {t.id}  ({_boxes_label(t)})  {t.name}" + (f"   e.g. {example}" if example else ""))

    choice = input("\nPick a number: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(results)):
        print("Invalid choice.", file=sys.stderr)
        return 1
    template = results[int(choice) - 1]

    texts = []
    for i in range(template.box_count):
        hint = f' (e.g. "{template.example[i]}")' if i < len(template.example) else ""
        texts.append(input(f"Box {i + 1} text{hint}: "))

    _deliver(template.id, texts, share.output_path(template.id), copy=True, open_=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="quickmeme", description="Render meme templates locally.")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="list all templates")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=_cmd_list)

    p_search = sub.add_parser("search", help="search templates by name/keyword")
    p_search.add_argument("query")
    p_search.add_argument("--json", action="store_true")
    p_search.set_defaults(func=_cmd_search)

    p_make = sub.add_parser("make", help="render a meme")
    p_make.add_argument("template", help="template id (see `quickmeme search`)")
    p_make.add_argument("text", nargs="*", help="text per box, in order")
    p_make.add_argument("--out", help="output path (default: ~/.quickmeme/out/)")
    p_make.add_argument("--no-copy", action="store_true", help="don't copy to clipboard")
    p_make.add_argument("--no-open", action="store_true", help="don't open the rendered meme")
    p_make.set_defaults(func=_cmd_make)

    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        return _interactive()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
