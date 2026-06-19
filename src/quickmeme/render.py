from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

from quickmeme.catalog import Template, get

FONT_DIR = Path(__file__).parent / "assets" / "fonts"
FALLBACK_FONT = FONT_DIR / "Anton-Regular.ttf"

FONT_CANDIDATES = {
    "thick": ["/System/Library/Fonts/Supplemental/Impact.ttf"],
    "thin": [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
    "comic": ["/System/Library/Fonts/Supplemental/Comic Sans MS.ttf"],
}

MIN_FONT = 8


def _font_path(name: str | None) -> str:
    for candidate in FONT_CANDIDATES.get(name or "thick", FONT_CANDIDATES["thick"]):
        if Path(candidate).exists():
            return candidate
    return str(FALLBACK_FONT)


@lru_cache(maxsize=256)
def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _styled(text: str, style: str | None) -> str:
    if style == "upper":
        return text.upper()
    if style == "mock":
        return "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
    return text


def _stroke(size: int) -> int:
    return max(1, round(size / 12))


def _contrast(fill: tuple[int, int, int]) -> tuple[int, int, int]:
    luminance = 0.299 * fill[0] + 0.587 * fill[1] + 0.114 * fill[2]
    return (0, 0, 0) if luminance > 140 else (255, 255, 255)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: float, stroke: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines, current = [], words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        box = draw.textbbox((0, 0), trial, font=font, stroke_width=stroke)
        if box[2] - box[0] <= max_w:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _fit(draw, text, box_w, box_h, font_path, align):
    lo, hi = MIN_FONT, max(MIN_FONT, int(box_h))
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        font = _font(font_path, mid)
        stroke = _stroke(mid)
        lines = _wrap(draw, text, font, box_w, stroke)
        block = "\n".join(lines)
        spacing = max(2, mid // 10)
        box = draw.multiline_textbbox(
            (0, 0), block, font=font, stroke_width=stroke, align=align, spacing=spacing
        )
        if box[2] - box[0] <= box_w and box[3] - box[1] <= box_h:
            best = (font, lines, stroke, spacing)
            lo = mid + 1
        else:
            hi = mid - 1
    if best is None:
        font = _font(font_path, MIN_FONT)
        stroke = _stroke(MIN_FONT)
        best = (font, _wrap(draw, text, font, box_w, stroke), stroke, max(2, MIN_FONT // 10))
    return best


def _draw_box(base: Image.Image, box: dict, text: str) -> None:
    text = _styled(text, box.get("style"))
    if not text.strip():
        return

    width, height = base.size
    box_x, box_y = box.get("anchor_x", 0.0) * width, box.get("anchor_y", 0.0) * height
    box_w, box_h = box.get("scale_x", 1.0) * width, box.get("scale_y", 0.2) * height
    align = "left" if box.get("align") == "left" else "center"
    fill = ImageColor.getrgb(box.get("color") or "white")
    stroke_fill = _contrast(fill)
    angle = float(box.get("angle") or 0.0)

    draw = ImageDraw.Draw(base)
    font, lines, stroke, spacing = _fit(draw, text, box_w, box_h, _font_path(box.get("font")), align)
    block = "\n".join(lines)
    bbox = draw.multiline_textbbox(
        (0, 0), block, font=font, stroke_width=stroke, align=align, spacing=spacing
    )
    block_w, block_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    text_kwargs = dict(
        font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, align=align, spacing=spacing
    )

    if angle == 0.0:
        x = box_x + (box_w - block_w) / 2 if align == "center" else box_x
        y = box_y + (box_h - block_h) / 2
        draw.multiline_text((x - bbox[0], y - bbox[1]), block, **text_kwargs)
        return

    pad = stroke + 2
    layer = Image.new("RGBA", (int(block_w) + 2 * pad, int(block_h) + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(layer).multiline_text((pad - bbox[0], pad - bbox[1]), block, **text_kwargs)
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    center_x, center_y = box_x + box_w / 2, box_y + box_h / 2
    base.alpha_composite(layer, (int(center_x - layer.width / 2), int(center_y - layer.height / 2)))


def _base_image(template: Template) -> Image.Image:
    image = Image.open(template.image)
    image.seek(0)
    return image.convert("RGBA")


def render(template_id: str, texts: list[str], out_path: Path) -> Path:
    template = get(template_id)
    base = _base_image(template)
    for box, text in zip(template.boxes, texts):
        _draw_box(base, box, text)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out_path)
    return out_path
