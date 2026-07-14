# csl_pyutil

_Created: 14-07-2026 · Last updated: 14-07-2026_

Generic (non-Sanskrit-specific) Python helpers shared across the CDSL /
Sanskrit-Lexicon repos — a sibling of [`sanskrit_util`](../py/) in this same
repo, kept as a **separate package** because its scope isn't Sanskrit
linguistics: `sanskrit_util` is string/transcoding helpers only, this package
is generic tooling. See [`../README.md`](../README.md) for why both packages
live in one repo.

## Install

```sh
pip install "csl-pyutil @ git+https://github.com/sanskrit-lexicon/sanskrit-util@main#subdirectory=csl_pyutil"
```

## `render_review_sheet()`

Builds the self-contained interactive HTML review/voting sheet the org's
`/review-sheet` Claude Code skill produces — approve/reject/defer per item,
running tally, `localStorage` persistence, a download button, and (on
Chromium) live auto-save via the File System Access API. One emitter, called
the same way every time, instead of an LLM hand-writing the same markup/JS
from scratch on every invocation (H925).

```python
from csl_pyutil import render_review_sheet

html = render_review_sheet(
    items=[
        {"id": "L142", "title": "पश्यति → पश्यति", "context": "old: X\nnew: Y",
         "links": ["https://github.com/.../blob/....md#L142"]},
        ...
    ],
    sheet_id="commentarystrategies-sundarakanda_35-37",   # org naming convention
    title="Sundarakāṇḍa commentary xref — sarga 35-37",
    description="43 candidate cross-references needing a decision",
    source={"repo": "CommentaryStrategies", "generated": "2026-07-14"},
    language="ru",  # default per the org's Russian-default rule; "en" also supported
)
open("review/commentarystrategies-sundarakanda_35-37_review.html", "w",
     encoding="utf-8").write(html)
```

Exported decisions JSON shape (unchanged from the skill's prior contract, so
[`Uprava/tools/review_decisions_watcher.py`](https://github.com/gasyoun/Uprava/blob/main/tools/review_decisions_watcher.py)
needs no changes):

```json
{"sheet_id": "...", "generated": "2026-07-14T12:00:00.000Z", "decided": 12,
 "items": [{"id": "L142", "decision": "approve", "note": ""}, ...]}
```

Item schema: `{"id": str, "title": str, "context": str (optional),
"links": [str, ...] (optional)}`. IDs must be stable across regeneration —
decisions are keyed by them, not array position.

The sheet's naming, placement (gitignored `review/`), GTD `@DO` line, and
`Uprava/REVIEW_SHEETS_INDEX.md` registration are still the caller's job — this
function only produces the HTML string. See
[`~/.claude/commands/review-sheet.md`](https://github.com/gasyoun/claude-config/blob/main/commands/review-sheet.md)
for the full process.

## Tests

```sh
pip install -e . pytest
pytest tests -q
```
