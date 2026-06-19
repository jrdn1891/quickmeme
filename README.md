<p align="center">
  <img src="docs/hero.png" alt="quickmeme" width="340">
</p>

<h1 align="center">quickmeme</h1>

<p align="center">
  React with a meme without leaving your terminal.<br>
  Your agent picks a template, fills in the text, and the PNG lands on your clipboard.
</p>

---

That meme up top was made with quickmeme:

```sh
quickmeme make drake "going to a web app, editing by hand, screenshot, save, share" "the quickmeme CLI, right from your agent"
```

## Install

**No terminal — just talk to Claude.** Download [`quickmeme.mcpb`](https://github.com/jrdn1891/quickmeme/releases/latest/download/quickmeme.mcpb)
and double-click to install it in Claude Desktop. Then ask in plain English:
*"make a drake meme about Mondays."* Claude picks the template and fills it in.

**Command line:**

```sh
# one-liner (installs uv if you don't have it)
curl -fsSL https://raw.githubusercontent.com/jrdn1891/quickmeme/main/install.sh | sh

# or, if you already use uv
uv tool install git+https://github.com/jrdn1891/quickmeme
```

## Use it

Run `quickmeme` on its own for a guided picker, or go straight to a command:

```sh
quickmeme                      # interactive: search, pick, type — done
quickmeme search drake         # find a template and see its text boxes
quickmeme make drake "left on unread" "left on read"
```

`make` renders the meme, copies the PNG to your clipboard, and opens it.
Text maps to the template's boxes in order — `search` tells you how many each one has.

It's built to be driven by an agent: `search` to discover, `make` to render.
No browser, no manual editing, no screenshot.

## How it works

- 209 templates (image + text-box geometry) vendored from [memegen](https://github.com/jacebrowning/memegen) (MIT).
- Rendering is fully local via Pillow: case styling, word-wrap, auto-fit, outline, and per-box rotation.
- Fonts: system Impact / Comic Sans, with bundled [Anton](https://fonts.google.com/specimen/Anton) (OFL) as the offline fallback.

Clipboard and open work on macOS, Linux (`xclip`/`wl-copy`), and Windows; rendering runs anywhere.
There's also an MCP server (`quickmeme-mcp`, the `[mcp]` extra) — that's what the Claude Desktop extension wraps.
