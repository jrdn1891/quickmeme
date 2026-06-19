import pytest

from quickmeme.catalog import get, load_all, search


def test_catalog_loads_full_set():
    templates = load_all()
    assert len(templates) > 200
    for t in templates:
        assert t.box_count >= 1
        assert t.name
        assert t.image.exists()


def test_search_ranks_exact_id_first():
    hits = search("drake")
    assert hits
    assert hits[0].id == "drake"


def test_search_matches_keywords():
    assert any(t.id == "drake" for t in search("drakeposting"))


def test_get_unknown_raises():
    with pytest.raises(KeyError):
        get("definitely-not-a-template")
