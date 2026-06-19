from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

TEMPLATES_DIR = Path(__file__).parent / "templates"


@dataclass(frozen=True)
class Template:
    id: str
    name: str
    keywords: tuple[str, ...]
    boxes: tuple[dict, ...]
    example: tuple[str, ...]
    image: Path
    config: Path

    @property
    def box_count(self) -> int:
        return len(self.boxes)


def _base_image(directory: Path) -> Path | None:
    for ext in ("png", "jpg", "jpeg", "gif"):
        candidate = directory / f"default.{ext}"
        if candidate.exists():
            return candidate
    return None


def _load(directory: Path) -> Template | None:
    config = directory / "config.yml"
    image = _base_image(directory)
    if not config.exists() or image is None:
        return None
    data = yaml.safe_load(config.read_text()) or {}
    keywords = tuple(k for k in (data.get("keywords") or []) if k)
    return Template(
        id=directory.name,
        name=data.get("name") or directory.name,
        keywords=keywords,
        boxes=tuple(data.get("text") or []),
        example=tuple(data.get("example") or []),
        image=image,
        config=config,
    )


@lru_cache(maxsize=1)
def load_all() -> tuple[Template, ...]:
    templates = (
        _load(d)
        for d in sorted(TEMPLATES_DIR.iterdir())
        if d.is_dir() and not d.name.startswith("_")
    )
    return tuple(t for t in templates if t is not None)


def get(template_id: str) -> Template:
    for template in load_all():
        if template.id == template_id:
            return template
    raise KeyError(template_id)


def _score(template: Template, query: str) -> int:
    if template.id == query:
        return 100
    if template.id.startswith(query):
        return 60
    if query in template.id:
        return 40
    if query in template.name.lower():
        return 30
    if any(query in keyword.lower() for keyword in template.keywords):
        return 15
    return 0


def search(query: str) -> list[Template]:
    query = query.strip().lower()
    if not query:
        return list(load_all())
    scored = ((_score(t, query), t) for t in load_all())
    hits = sorted((s_t for s_t in scored if s_t[0]), key=lambda s_t: (-s_t[0], s_t[1].id))
    return [t for _, t in hits]
