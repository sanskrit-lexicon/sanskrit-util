# -*- coding: utf-8 -*-
import json
import re

import pytest

from csl_pyutil import render_review_sheet


def _items():
    return [
        {"id": "L1", "title": "पश्यति → पश्यति (no change)", "context": "old: X\nnew: Y",
         "links": ["https://example.org/a"]},
        {"id": "L2", "title": "second item", "context": "context text"},
    ]


def test_basic_shape():
    html = render_review_sheet(_items(), sheet_id="testrepo-topic_scope",
                                title="Test Sheet", description="a test sheet")
    assert html.startswith("<!doctype html>")
    assert "Test Sheet" in html
    assert "a test sheet" in html
    assert "testrepo-topic_scope_decisions.json" in html
    assert html.count("<script>") == html.count("</script>")


def test_default_filename_from_sheet_id():
    html = render_review_sheet(_items(), sheet_id="repo-x_y", title="T")
    assert "repo-x_y_decisions.json" in html


def test_custom_decisions_filename():
    html = render_review_sheet(_items(), sheet_id="repo-x_y", title="T",
                                decisions_filename="custom_name.json")
    assert "custom_name.json" in html
    assert "repo-x_y_decisions.json" not in html


def test_items_embedded_as_valid_json_roundtrip():
    items = _items()
    html = render_review_sheet(items, sheet_id="s1", title="T")
    m = re.search(r"const ITEMS = (\[.*?\]);\n", html, re.S)
    assert m, "ITEMS payload not found in emitted HTML"
    parsed = json.loads(m.group(1))
    assert [p["id"] for p in parsed] == [it["id"] for it in items]
    assert parsed[0]["title"] == items[0]["title"]  # unicode survives, not mangled


def test_requires_id_and_title():
    with pytest.raises(ValueError):
        render_review_sheet([{"title": "no id"}], sheet_id="s", title="T")
    with pytest.raises(ValueError):
        render_review_sheet([{"id": "x"}], sheet_id="s", title="T")


def test_unknown_language_rejected():
    with pytest.raises(ValueError):
        render_review_sheet(_items(), sheet_id="s", title="T", language="de")


def test_english_strings():
    html = render_review_sheet(_items(), sheet_id="s", title="T", language="en")
    assert "Approve" in html
    assert "Reject" in html
    assert "Defer" in html


def test_russian_is_default():
    html = render_review_sheet(_items(), sheet_id="s", title="T")
    assert "Принять" in html
    assert "Отклонить" in html
    assert "Отложить" in html


def test_title_and_description_are_escaped():
    html = render_review_sheet(_items(), sheet_id="s",
                                title="<script>alert(1)</script>",
                                description="<img src=x onerror=alert(2)>")
    # the literal tags must not survive unescaped — html.escape() neutralizes
    # them to inert text (the substring "onerror=..." staying as plain text
    # is fine; it is no longer inside a real "<img ...>" tag)
    assert "<script>alert(1)</script>" not in html
    assert "<img src=x" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;img src=x onerror=alert(2)&gt;" in html


def test_no_premature_script_close_from_item_content():
    items = [{"id": "L1", "title": "boundary", "context": "</script><script>evil()</script>"}]
    html = render_review_sheet(items, sheet_id="s", title="T")
    # the only genuine "</script>" in the document must be the emitter's own
    # closing tag — every occurrence coming from item content must have been
    # neutralized (an unescaped literal "<script>" OPEN tag inside a script
    # block's text content is inert to the HTML tokenizer; only an unescaped
    # "</script>" can prematurely end the block, so that's the real check)
    assert html.count("</script>") == 1


def test_empty_items_renders_no_items_message():
    html_ru = render_review_sheet([], sheet_id="s", title="T")
    assert "Нет пунктов" in html_ru
    html_en = render_review_sheet([], sheet_id="s", title="T", language="en")
    assert "No items to review" in html_en


def test_source_dict_rendered_and_escaped():
    html = render_review_sheet(_items(), sheet_id="s", title="T",
                                source={"repo": "<x>", "generated": "2026-07-14"})
    assert "&lt;x&gt;" in html
    assert "2026-07-14" in html
