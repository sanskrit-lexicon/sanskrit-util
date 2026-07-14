# -*- coding: utf-8 -*-
"""csl_pyutil — generic (non-Sanskrit-specific) Python helpers shared across the
sanskrit-lexicon / CDSL repos, distinct from the Sanskrit-linguistics-specific
``sanskrit_util`` package this repo also ships.

Public API
----------
render_review_sheet(items, ...)   self-contained HTML review/voting sheet (H925)

Extracted from the ad-hoc HTML the `/review-sheet` Claude Code skill previously
hand-wrote from scratch on every invocation — one emitter, called the same way
every time, instead of an LLM re-deriving the same markup/JS per sheet.
"""
import html
import json

__version__ = "0.1.0"

__all__ = ["render_review_sheet"]

_STRINGS = {
    "ru": {
        "approve": "✅ Принять",
        "reject": "❌ Отклонить",
        "defer": "⏸ Отложить",
        "note_placeholder": "Заметка (необязательно)…",
        "items_label": "пунктов",
        "approved": "Принято",
        "rejected": "Отклонено",
        "deferred": "Отложено",
        "undecided": "Не решено",
        "download": "Скачать {filename}",
        "save_to_folder": "💾 Сохранять в папку…",
        "saved": "Сохранено ✓",
        "legend_title": "Легенда",
        "legend_approve": "<b>Принять</b> — согласиться с предложенным изменением как показано на карточке (отдельного варианта «принять как есть» нет — принятие означает согласие внести правку именно в этом виде).",
        "legend_reject": "<b>Отклонить</b> — оставить текущую запись без изменений.",
        "legend_defer": "<b>Отложить</b> — пока не уверены, решить позже.",
        "legend_note": "Поле заметки — для запроса частичной правки вместо полного отклонения.",
        "no_items": "Нет пунктов для оценки.",
    },
    "en": {
        "approve": "✅ Approve",
        "reject": "❌ Reject",
        "defer": "⏸ Defer",
        "note_placeholder": "Note (optional)…",
        "items_label": "items",
        "approved": "Approved",
        "rejected": "Rejected",
        "deferred": "Deferred",
        "undecided": "Undecided",
        "download": "Download {filename}",
        "save_to_folder": "💾 Save to folder…",
        "saved": "Saved ✓",
        "legend_title": "Legend",
        "legend_approve": "<b>Approve</b> — accept the proposed change shown on the card (there is no separate “approve as-is” — approving means agreeing the change should be made as written).",
        "legend_reject": "<b>Reject</b> — keep the current entry unchanged.",
        "legend_defer": "<b>Defer</b> — not sure yet, decide later.",
        "legend_note": "The free-text note field is for requesting a partial tweak instead of an outright reject.",
        "no_items": "No items to review.",
    },
}


def render_review_sheet(items, *, sheet_id, title, description="", source=None,
                         language="ru", decisions_filename=None):
    """Build a self-contained HTML review/voting sheet.

    items: list of dicts, each ``{"id": str, "title": str, "context": str,
        "links": [str, ...] (optional), "default": "approve"|"reject"|"defer"|None
        (optional)}``. IDs must be stable across regeneration (decisions are
        keyed by them, not array position).
    sheet_id: stable identifier for this sheet — used as the localStorage key
        and (unless overridden) the decisions filename stem. Should already
        follow the org naming convention (``<repo-slug>-<topic>_<scope>``).
    title: sheet heading.
    description: one-line source/context description shown under the title.
    source: optional dict of extra provenance shown in the header (e.g.
        ``{"repo": "...", "generated": "..."}``); rendered as-is, escaped.
    language: "ru" (default, per the org's Russian-default rule) or "en".
    decisions_filename: override the exported JSON's filename; defaults to
        ``f"{sheet_id}_decisions.json"``.

    Returns the full HTML document as a string — write it to disk yourself
    (the caller owns naming/placement per the org's review-sheet convention).
    """
    if language not in _STRINGS:
        raise ValueError("language must be one of %r, got %r" % (sorted(_STRINGS), language))
    t = _STRINGS[language]
    decisions_filename = decisions_filename or ("%s_decisions.json" % sheet_id)

    items = list(items)
    for it in items:
        if "id" not in it or "title" not in it:
            raise ValueError("every item needs at least 'id' and 'title': %r" % (it,))

    items_payload = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    source_html = ""
    if source:
        parts = ["<b>%s</b>: %s" % (html.escape(str(k)), html.escape(str(v)))
                 for k, v in source.items()]
        source_html = "<p class='src'>" + " &middot; ".join(parts) + "</p>"

    return _TEMPLATE.format(
        title=html.escape(title),
        description=html.escape(description),
        source_html=source_html,
        n=len(items),
        items_label=t["items_label"],
        sheet_id=html.escape(sheet_id, quote=True),
        decisions_filename=html.escape(decisions_filename, quote=True),
        items_json=items_payload,
        strings_json=json.dumps(t, ensure_ascii=False),
        no_items=t["no_items"],
        legend_title=t["legend_title"],
        legend_approve=t["legend_approve"],
        legend_reject=t["legend_reject"],
        legend_defer=t["legend_defer"],
        legend_note=t["legend_note"],
    )


_TEMPLATE = """<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
 :root{{--bg:#fbfaf7;--fg:#1c1a17;--muted:#6b6660;--line:#e6e1d8;--card:#fff;--accent:#7a4f2b;--chip:#f2ede3;--good:#3a7d44;--bad:#b5462f;--warn:#a3781f}}
 @media(prefers-color-scheme:dark){{:root{{--bg:#17150f;--fg:#ece7dd;--muted:#9c948a;--line:#2e2a22;--card:#1f1c15;--accent:#d9a066;--chip:#2a251c;--good:#7fbf87;--bad:#e08a70;--warn:#e0c070}}}}
 *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
 .wrap{{max-width:900px;margin:0 auto;padding:1.2rem 1.1rem 4rem}}
 h1{{font-size:1.4rem;margin:.2rem 0 .2rem}} .sub{{color:var(--muted);font-size:.9rem;margin:0 0 .3rem}}
 .src{{color:var(--muted);font-size:.82rem;margin:0 0 1rem}}
 .bar{{position:sticky;top:0;background:var(--bg);z-index:5;display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;padding:.6rem 0;border-bottom:1px solid var(--line);margin-bottom:1rem;font-size:.85rem}}
 .tally b{{font-variant-numeric:tabular-nums}}
 button{{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:.4rem;padding:.4rem .7rem;cursor:pointer}}
 button.primary{{background:var(--accent);color:var(--bg);border-color:var(--accent)}}
 .save-status{{color:var(--good);font-size:.8rem}}
 .card{{background:var(--card);border:1px solid var(--line);border-radius:.6rem;padding:1rem 1.1rem;margin-bottom:.9rem}}
 .card.decided{{opacity:.7}}
 .card h3{{margin:0 0 .4rem;font-size:1.02rem}}
 .ctx{{white-space:pre-wrap;font-size:.92rem;color:var(--fg);background:var(--chip);border-radius:.4rem;padding:.6rem .7rem;margin:.4rem 0}}
 .links{{font-size:.8rem;margin:.3rem 0}} .links a{{color:var(--accent);margin-right:.6rem}}
 .votebar{{display:flex;gap:.5rem;align-items:center;margin-top:.6rem;flex-wrap:wrap}}
 .votebar button[data-v]{{}} .votebar button.active[data-v="approve"]{{border-color:var(--good);background:color-mix(in srgb, var(--good) 18%, var(--card))}}
 .votebar button.active[data-v="reject"]{{border-color:var(--bad);background:color-mix(in srgb, var(--bad) 18%, var(--card))}}
 .votebar button.active[data-v="defer"]{{border-color:var(--warn);background:color-mix(in srgb, var(--warn) 18%, var(--card))}}
 .note{{flex:1 1 12rem;min-width:10rem;font:inherit;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:.4rem;padding:.35rem .5rem}}
 .legend{{margin-top:1.6rem;padding-top:.8rem;border-top:1px solid var(--line);font-size:.82rem;color:var(--muted)}}
 .legend h4{{margin:.2rem 0 .4rem;color:var(--fg);font-size:.85rem}}
 .legend div{{margin:.15rem 0}}
 .empty{{color:var(--muted);padding:2rem 0;text-align:center}}
 kbd{{border:1px solid var(--line);border-radius:.25rem;padding:0 .3rem;font-size:.75em}}
</style></head><body><div class="wrap">
 <h1>{title}</h1>
 <p class="sub">{description}</p>
 {source_html}
 <div class="bar">
  <span class="tally" id="tally"><b>{n}</b> {items_label}</span>
  <button id="dl">⬇</button>
  <button id="save" style="display:none"></button>
  <span class="save-status" id="saveStatus"></span>
 </div>
 <div id="items"></div>
 <div class="legend">
  <h4>{legend_title}</h4>
  <div>{legend_approve}</div>
  <div>{legend_reject}</div>
  <div>{legend_defer}</div>
  <div>{legend_note}</div>
  <div><kbd>a</kbd>/<kbd>r</kbd>/<kbd>d</kbd> = approve/reject/defer the focused card &middot; <kbd>&darr;</kbd>/<kbd>&uarr;</kbd> move focus</div>
 </div>
</div>
<script>
const SHEET_ID = "{sheet_id}";
const DECISIONS_FILENAME = "{decisions_filename}";
const ITEMS = {items_json};
const STR = {strings_json};
const STORE_KEY = "review-sheet:" + SHEET_ID;
let decisions = {{}};
try {{ decisions = JSON.parse(localStorage.getItem(STORE_KEY) || "{{}}"); }} catch (e) {{ decisions = {{}}; }}
let saveHandle = null;
let saveTimer = null;

function persist() {{
  try {{ localStorage.setItem(STORE_KEY, JSON.stringify(decisions)); }} catch (e) {{}}
  updateTally();
  scheduleAutosave();
}}

function updateTally() {{
  let a = 0, r = 0, d = 0;
  for (const id in decisions) {{
    const v = decisions[id].decision;
    if (v === "approve") a++; else if (v === "reject") r++; else if (v === "defer") d++;
  }}
  const u = ITEMS.length - a - r - d;
  document.getElementById("tally").innerHTML =
    "<b>" + ITEMS.length + "</b> " + STR.items_label +
    " &middot; " + STR.approved + " <b>" + a + "</b>" +
    " &middot; " + STR.rejected + " <b>" + r + "</b>" +
    " &middot; " + STR.deferred + " <b>" + d + "</b>" +
    " &middot; " + STR.undecided + " <b>" + u + "</b>";
}}

function exportPayload() {{
  const items = ITEMS.map(it => ({{
    id: it.id,
    decision: (decisions[it.id] && decisions[it.id].decision) || null,
    note: (decisions[it.id] && decisions[it.id].note) || "",
  }}));
  const decided = items.filter(x => x.decision).length;
  return JSON.stringify({{
    sheet_id: SHEET_ID, generated: new Date().toISOString(), decided, items,
  }}, null, 1);
}}

function downloadNow() {{
  const blob = new Blob([exportPayload()], {{type: "application/json"}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = DECISIONS_FILENAME;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}}

function scheduleAutosave() {{
  if (!saveHandle) return;
  clearTimeout(saveTimer);
  saveTimer = setTimeout(async () => {{
    try {{
      const w = await saveHandle.createWritable();
      await w.write(exportPayload());
      await w.close();
      const s = document.getElementById("saveStatus");
      s.textContent = STR.saved;
      setTimeout(() => {{ s.textContent = ""; }}, 1500);
    }} catch (e) {{ /* handle revoked or write failed — fall back silently to manual download */ }}
  }}, 1000);
}}

function renderItems() {{
  const root = document.getElementById("items");
  if (!ITEMS.length) {{ root.innerHTML = "<p class='empty'>" + STR.no_items + "</p>"; return; }}
  root.innerHTML = ITEMS.map((it, i) => {{
    const cur = decisions[it.id] || {{}};
    const links = (it.links || []).map(u => "<a href=\\"" + u + "\\" target=\\"_blank\\" rel=\\"noopener\\">" + u + "</a>").join("");
    return "<div class='card" + (cur.decision ? " decided" : "") + "' data-id='" + it.id + "' tabindex='0'>" +
      "<h3>" + (it.title || "") + "</h3>" +
      (it.context ? "<div class='ctx'>" + it.context + "</div>" : "") +
      (links ? "<div class='links'>" + links + "</div>" : "") +
      "<div class='votebar'>" +
      "<button data-v='approve' class='" + (cur.decision === "approve" ? "active" : "") + "'>" + STR.approve + "</button>" +
      "<button data-v='reject' class='" + (cur.decision === "reject" ? "active" : "") + "'>" + STR.reject + "</button>" +
      "<button data-v='defer' class='" + (cur.decision === "defer" ? "active" : "") + "'>" + STR.defer + "</button>" +
      "<input class='note' placeholder='" + STR.note_placeholder + "' value='" + (cur.note ? cur.note.replace(/'/g, "&#39;") : "") + "'>" +
      "</div></div>";
  }}).join("");

  root.querySelectorAll(".card").forEach(card => {{
    const id = card.dataset.id;
    card.querySelectorAll("button[data-v]").forEach(btn => {{
      btn.addEventListener("click", () => {{
        const v = btn.dataset.v;
        decisions[id] = decisions[id] || {{}};
        decisions[id].decision = (decisions[id].decision === v) ? null : v;
        renderItems(); persist();
      }});
    }});
    card.querySelector(".note").addEventListener("input", (e) => {{
      decisions[id] = decisions[id] || {{}};
      decisions[id].note = e.target.value;
      persist();
    }});
  }});
}}

document.getElementById("dl").textContent = STR.download.replace("{{filename}}", DECISIONS_FILENAME);
document.getElementById("dl").addEventListener("click", downloadNow);

if (window.showSaveFilePicker) {{
  const saveBtn = document.getElementById("save");
  saveBtn.style.display = "";
  saveBtn.textContent = STR.save_to_folder;
  saveBtn.addEventListener("click", async () => {{
    try {{
      saveHandle = await window.showSaveFilePicker({{suggestedName: DECISIONS_FILENAME}});
      scheduleAutosave();
    }} catch (e) {{ /* user cancelled the picker */ }}
  }});
}}

document.addEventListener("keydown", (e) => {{
  const active = document.activeElement;
  const cards = Array.from(document.querySelectorAll(".card"));
  if (!cards.length) return;
  let idx = cards.indexOf(active);
  if (e.key === "ArrowDown") {{ e.preventDefault(); cards[Math.min(cards.length - 1, idx + 1)].focus(); return; }}
  if (e.key === "ArrowUp") {{ e.preventDefault(); cards[Math.max(0, idx - 1)].focus(); return; }}
  if (idx < 0) return;
  const map = {{a: "approve", r: "reject", d: "defer"}};
  if (map[e.key]) {{ cards[idx].querySelector("button[data-v='" + map[e.key] + "']").click(); }}
}});

renderItems();
updateTally();
</script>
</body></html>
"""
