# quickmeme

Render popular meme templates locally from the terminal. No browser, no editor,
no screenshot — pick a template, fill the text, and the PNG lands on your
clipboard ready to paste.

Built for an agent to drive: `search` to discover templates and their text
boxes, `make` to render.

## Install

```sh
uv tool install .        # global `quickmeme` command
# or, in-repo during development:
uv run quickmeme ...
```

## Usage

```sh
quickmeme search drake          # find templates by name/keyword
quickmeme list                  # all 209 templates
quickmeme make drake "writing comments" "letting the code speak"
```

`make` renders to `~/.quickmeme/out/`, copies the PNG to the clipboard, and
opens it in Preview. Text is given per box, in order — `search` shows each
template's box count and an example.

Flags: `--out PATH`, `--no-copy`, `--no-open`. `search`/`list` take `--json`
for machine-readable output.

## How it works

- **Templates** (`src/quickmeme/templates/`) are vendored from
  [memegen](https://github.com/jacebrowning/memegen) (MIT) — each is an image
  plus a `config.yml` defining normalized text boxes (position, font, color,
  alignment, rotation). This is the single source of truth; re-vendor with
  `scripts/vendor.py`.
- **Rendering** (`render.py`) uses Pillow: text is case-styled, word-wrapped,
  auto-fit to its box, stroked, and rotated to match the template.
- **Fonts**: system Impact / Comic Sans on macOS, with bundled
  [Anton](https://fonts.google.com/specimen/Anton) (OFL) as the offline fallback.

## Roadmap

- Fill boxes with images (faces/logos) via the template `overlay` geometry.
- `quickmeme sync` to refresh the catalog from upstream memegen.
