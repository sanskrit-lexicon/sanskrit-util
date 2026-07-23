/* KeySwap 2.0 PWA — cycle + smart + long-press (parity with cycle_engine / smart_input) */
(function () {
  "use strict";

  const EMBEDDED_CLASSIC = `
a > ā
i > ī
u > ū
r > ṛ > ṝ
l > ḷ > ḹ
m > ṃ > ṁ
h > ḥ
n > ṇ > ṅ > ñ
t > ṭ
d > ḍ
s > ṣ > ś
A > Ā
I > Ī
U > Ū
R > Ṛ > Ṝ
L > Ḷ > Ḹ
M > Ṃ > Ṁ
H > Ḥ
N > Ṇ > Ṅ > Ñ
T > Ṭ
D > Ḍ
S > Ṣ > Ś
`.trim();

  const SMART = [
    ["aa", "ā"], ["ii", "ī"], ["uu", "ū"], ["rr", "ṛ"], ["ll", "ḷ"],
    ["mm", "ṃ"], ["hh", "ḥ"], ["AA", "Ā"], ["II", "Ī"], ["UU", "Ū"],
    ["sh", "ś"], ["ss", "ṣ"], ["ng", "ṅ"], ["ny", "ñ"], ["nn", "ṇ"],
    ["tt", "ṭ"], ["dd", "ḍ"], ["Sh", "Ś"], ["Ss", "Ṣ"],
  ].sort((a, b) => b[0].length - a[0].length);

  function nfc(s) {
    return s.normalize("NFC");
  }

  function parseChains(text) {
    const chains = [];
    const seen = new Map();
    let lineNo = 0;
    for (const raw of text.split(/\r?\n/)) {
      lineNo++;
      let line = raw.trim();
      if (!line || line.startsWith("#")) continue;
      const hash = line.indexOf(" #");
      if (hash >= 0) line = line.slice(0, hash).trim();
      const parts = line.split(">").map((p) => nfc(p.trim())).filter(Boolean);
      if (parts.length < 2) continue;
      if (seen.has(parts[0])) throw new Error("duplicate base " + parts[0] + " line " + lineNo);
      seen.set(parts[0], lineNo);
      chains.push(parts);
    }
    return chains;
  }

  function buildEngine(chains) {
    const byForm = new Map();
    let maxLen = 1;
    chains.forEach((chain, ci) => {
      chain.forEach((form, fi) => {
        if (!byForm.has(form)) byForm.set(form, [ci, fi]);
        maxLen = Math.max(maxLen, [...form].length);
      });
    });
    return {
      chains,
      applyTrigger(text) {
        const t = nfc(text);
        const cps = [...t];
        for (let len = Math.min(cps.length, maxLen); len >= 1; len--) {
          const suffix = cps.slice(-len).join("");
          const hit = byForm.get(suffix);
          if (hit) {
            const [ci, fi] = hit;
            const chain = chains[ci];
            const next = chain[(fi + 1) % chain.length];
            return cps.slice(0, -len).join("") + next;
          }
        }
        return null;
      },
      longPress(base) {
        for (const c of chains) if (c[0] === base) return c;
        return [base];
      },
    };
  }

  function applySmart(text) {
    const t = nfc(text);
    for (const [src, dst] of SMART) {
      if (t.endsWith(src)) return t.slice(0, -src.length) + nfc(dst);
    }
    return null;
  }

  const ta = document.getElementById("t");
  const profileSel = document.getElementById("profile");
  const smartCb = document.getElementById("smart");
  const menu = document.getElementById("menu");
  let engine = buildEngine(parseChains(EMBEDDED_CLASSIC));
  const profiles = {
    "iast-classic": EMBEDDED_CLASSIC,
  };

  async function tryLoadProfiles() {
    const names = ["iast-classic", "iso15919", "vedic-draft", "vedic-svara", "personal-legacy"];
    for (const name of names) {
      try {
        const r = await fetch("../configs/" + name + ".txt");
        if (r.ok) {
          profiles[name] = await r.text();
        }
      } catch (_) { /* file:// or missing */ }
    }
    profileSel.innerHTML = "";
    for (const name of Object.keys(profiles)) {
      const o = document.createElement("option");
      o.value = name;
      o.textContent = name;
      profileSel.appendChild(o);
    }
    setProfile(profileSel.value || "iast-classic");
  }

  function setProfile(name) {
    const text = profiles[name] || EMBEDDED_CLASSIC;
    engine = buildEngine(parseChains(text));
  }

  profileSel.addEventListener("change", () => setProfile(profileSel.value));

  function insert(str) {
    const start = ta.selectionStart;
    const end = ta.selectionEnd;
    const v = ta.value;
    ta.value = v.slice(0, start) + str + v.slice(end);
    const pos = start + str.length;
    ta.setSelectionRange(pos, pos);
    ta.focus();
    maybeSmart();
  }

  function maybeSmart() {
    if (!smartCb.checked) return;
    const pos = ta.selectionStart;
    const before = ta.value.slice(0, pos);
    const next = applySmart(before);
    if (next == null) return;
    ta.value = next + ta.value.slice(pos);
    ta.setSelectionRange(next.length, next.length);
  }

  function doCycle() {
    const pos = ta.selectionStart;
    const before = ta.value.slice(0, pos);
    const after = ta.value.slice(pos);
    const cycled = engine.applyTrigger(before);
    if (cycled == null) {
      insert("=");
      return;
    }
    ta.value = cycled + after;
    ta.setSelectionRange(cycled.length, cycled.length);
    ta.focus();
  }

  ta.addEventListener("keydown", (e) => {
    if (e.key === "=" && !e.ctrlKey && !e.metaKey && !e.altKey) {
      e.preventDefault();
      doCycle();
    }
  });

  document.getElementById("cycle").onclick = doCycle;
  document.getElementById("copy").onclick = async () => {
    await navigator.clipboard.writeText(ta.value);
  };
  document.getElementById("clear").onclick = () => {
    ta.value = "";
    ta.focus();
  };

  const rows = [
    "qwertyuiop".split(""),
    "asdfghjkl".split(""),
    "zxcvbnm".split(""),
  ];
  const keysEl = document.getElementById("keys");
  let pressTimer = null;
  let pressBase = null;

  function hideMenu() {
    menu.style.display = "none";
  }

  function showMenu(base, x, y) {
    const forms = engine.longPress(base);
    menu.innerHTML = "";
    for (const f of forms) {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = f;
      b.onclick = () => {
        insert(f);
        hideMenu();
      };
      menu.appendChild(b);
    }
    menu.style.left = Math.min(x, window.innerWidth - 120) + "px";
    menu.style.top = Math.min(y, window.innerHeight - 80) + "px";
    menu.style.display = "block";
  }

  for (const row of rows) {
    for (const ch of row) {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = ch;
      b.addEventListener("pointerdown", (ev) => {
        pressBase = ch;
        pressTimer = setTimeout(() => {
          showMenu(ch, ev.clientX, ev.clientY);
          pressTimer = null;
          pressBase = null;
        }, 400);
      });
      b.addEventListener("pointerup", () => {
        if (pressTimer) {
          clearTimeout(pressTimer);
          pressTimer = null;
          if (pressBase) insert(pressBase);
          pressBase = null;
        }
      });
      b.addEventListener("pointerleave", () => {
        if (pressTimer) clearTimeout(pressTimer);
        pressTimer = null;
      });
      keysEl.appendChild(b);
    }
  }
  const eq = document.createElement("button");
  eq.type = "button";
  eq.textContent = "=";
  eq.className = "wide";
  eq.onclick = doCycle;
  keysEl.appendChild(eq);

  document.addEventListener("pointerdown", (e) => {
    if (!menu.contains(e.target) && e.target !== menu) hideMenu();
  });

  tryLoadProfiles();
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  }
})();
