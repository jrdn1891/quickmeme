from PIL import Image, ImageChops

from quickmeme.catalog import get
from quickmeme.render import render


def test_render_matches_template_size_and_draws_text(tmp_path):
    out = render("drake", ["left on unread", "left on read"], tmp_path / "drake.png")
    assert out.exists()

    rendered = Image.open(out).convert("RGB")
    base = Image.open(get("drake").image).convert("RGB")
    assert rendered.size == base.size

    diff = ImageChops.difference(rendered, base)
    assert diff.getbbox() is not None


def test_render_rotated_template(tmp_path):
    out = render("cmm", ["tabs beat spaces"], tmp_path / "cmm.png")
    rendered = Image.open(out).convert("RGB")
    base = Image.open(get("cmm").image).convert("RGB")
    assert rendered.size == base.size
    assert ImageChops.difference(rendered, base).getbbox() is not None


def test_render_ignores_empty_boxes(tmp_path):
    out = render("drake", ["", ""], tmp_path / "blank.png")
    rendered = Image.open(out).convert("RGB")
    base = Image.open(get("drake").image).convert("RGB")
    assert ImageChops.difference(rendered, base).getbbox() is None
