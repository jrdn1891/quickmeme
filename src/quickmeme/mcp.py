from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Image as MCPImage

from quickmeme import share
from quickmeme.catalog import load_all, search as _search
from quickmeme.render import render

mcp = FastMCP("quickmeme")


@mcp.tool()
def search(query: str = "") -> list[dict]:
    """Find meme templates by name or keyword.

    Returns up to 25 matches, each with `id`, `name`, `box_count`, and an
    `example` showing the text each box expects. Pass an empty query to list
    popular templates.
    """
    results = _search(query) if query else list(load_all())
    return [
        {"id": t.id, "name": t.name, "box_count": t.box_count, "example": list(t.example)}
        for t in results[:25]
    ]


@mcp.tool()
def make(template_id: str, texts: list[str]) -> MCPImage:
    """Render a meme and copy it to the clipboard.

    `texts` maps to the template's boxes in order (see `search` for box_count).
    Returns the rendered PNG.
    """
    out = share.output_path(template_id)
    render(template_id, texts, out)
    try:
        share.copy_to_clipboard(out)
    except Exception:
        pass
    return MCPImage(path=str(out))


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
