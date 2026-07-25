; KeySwap 2.9 for Windows — AutoHotkey v2
; MIT — sanskrit-util tools/KeySwap
;
; Modes: cycle | smart (default) | deadkey | writer (Writer-scheme digraphs)
; Script mode: iast | deva (Ctrl+Alt+D toggles; Ctrl+Alt+V converts clipboard)
; Guards: Keyman process warn; optional allowlist.txt; teaching HUD tooltips
; Trigger presets (2.8): equals | bracket | slash | backtick  (trigger.ini / tray)
;
; Hotkeys:
;   <trigger>         cycle last form (default =)
;   Shift+<trigger>   literal trigger char (escape cycle)
;   ^!=               clipboard → Devanāgarī
;   ^!i               clipboard → IAST
;   ^!h               clipboard HK/ITRANS/auto → IAST
;   ^!d               toggle script mode (IAST ⇄ Devanāgarī)
;   ^!v               clipboard → current script mode
;   ^!+d              selection → Devanāgarī, pasted in place (opt-in; select text first)
;   ^!c               open Cologne Simple Search for clipboard (auto scheme)
;   ^!s               light headword check (Cologne API → HUD)
;   ^!g               open Cologne webtc full entry / gloss for clipboard
;   ^!k               copy SLP1 + normkey of clipboard (no browser)
;   F6                reload config + allowlist + trigger
;   F7                toggle teaching HUD
;
; Args: KeySwap.ahk [configPath] [mode]

#Requires AutoHotkey v2.0
#SingleInstance Force
Persistent

global ConfigPath := A_Args.Length >= 1 ? A_Args[1] : A_ScriptDir "\..\config.txt"
global Mode := A_Args.Length >= 2 ? StrLower(A_Args[2]) : "smart"
global Chains := []
global FormIndex := Map()
global LastForm := ""
global SmartPairs := []
global DeadArmed := false
global ConfigMTime := ""
global StatusText := ""
global AllowList := []
global HudOn := true
global KeymanWarned := false
global ScriptMode := "iast"  ; iast | deva — target for Ctrl+Alt+V
; 2.8 trigger preset
global TriggerId := "equals"
global TriggerChar := "="
global TriggerHotkey := "="
global LiteralHotkey := "+="
global TriggerHotkeysBound := false

InitSmartPairs(Mode)
LoadAll()
RegisterTriggerHotkeys()
BuildTray()
CheckKeyman()
SetTimer(WatchConfig, 2000)
SetTimer(CheckKeyman, 30000)
A_IconTip := StatusTip()

bases := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
Loop Parse bases {
    Hotkey("~*" A_LoopField, OnLetter.Bind(A_LoopField))
}
; Writer-scheme punctuation prefixes (- ~ . ') participate in smart digraphs
Loop Parse "-~.'" {
    Hotkey("~*" A_LoopField, OnMark.Bind(A_LoopField))
}

~*':: {
    global Mode, DeadArmed, LastForm
    if (Mode = "deadkey" && AppAllowed())
        DeadArmed := true
    else if ((Mode = "smart" || Mode = "writer") && AppAllowed())
        LastForm := "'"
}

^!=:: ConvertClipboard("deva", "auto")
^!i:: ConvertClipboard("iast", "auto")
^!h:: ConvertClipboard("iast", "auto")  ; scheme auto → IAST
^!d:: ToggleScriptMode()
^!v:: ConvertToScriptMode()
^!+d:: ConvertSelectionInPlace("deva", "auto")
^!c:: OpenCologneSearch()
^!s:: CheckClipboardHeadword()
^!g:: OpenCologneGloss()
^!k:: CopySlp1Normkey()
F6:: {
    LoadAll()
    RegisterTriggerHotkeys()
    BuildTray()
}
F7:: ToggleHud()

; --- 2.8 trigger presets -------------------------------------------------

LoadTriggerPreset() {
    global TriggerId, TriggerChar, TriggerHotkey, LiteralHotkey
    ; Env KEYSWAP_TRIGGER wins (process / user env)
    envId := EnvGet("KEYSWAP_TRIGGER")
    id := ""
    if (envId != "") {
        id := NormalizeTriggerId(envId)
    } else {
        path := A_ScriptDir "\trigger.ini"
        if !FileExist(path) {
            ex := A_ScriptDir "\trigger.example.ini"
            if FileExist(ex)
                FileCopy(ex, path)
        }
        if FileExist(path) {
            for line in StrSplit(FileRead(path, "UTF-8"), "`n", "`r") {
                s := Trim(line)
                if (s = "" || SubStr(s, 1, 1) = "#" || SubStr(s, 1, 1) = ";")
                    continue
                if RegExMatch(s, "i)^preset\s*=\s*(\S+)", &m) {
                    id := NormalizeTriggerId(m[1])
                    break
                }
            }
        }
    }
    if (id = "")
        id := "equals"
    ApplyTriggerPreset(id, false)
}

NormalizeTriggerId(raw) {
    s := StrLower(Trim(raw))
    switch s {
        case "=", "equal", "equals", "plus":
            return "equals"
        case "]", "bracket", "rbrack", "right-bracket":
            return "bracket"
        case "/", "slash", "solidus":
            return "slash"
        case "``", "backtick", "grave", "tick":
            return "backtick"
        default:
            return s
    }
}

ApplyTriggerPreset(id, persist := true) {
    global TriggerId, TriggerChar, TriggerHotkey, LiteralHotkey
    id := NormalizeTriggerId(id)
    switch id {
        case "bracket":
            TriggerId := "bracket"
            TriggerChar := "]"
            TriggerHotkey := "]"
            LiteralHotkey := "+]"
        case "slash":
            TriggerId := "slash"
            TriggerChar := "/"
            TriggerHotkey := "/"
            LiteralHotkey := "+/"
        case "backtick":
            TriggerId := "backtick"
            TriggerChar := "``"
            TriggerHotkey := "``"
            LiteralHotkey := "+``"
        default:
            TriggerId := "equals"
            TriggerChar := "="
            TriggerHotkey := "="
            LiteralHotkey := "+="
    }
    if persist {
        path := A_ScriptDir "\trigger.ini"
        body := "# KeySwap 2.8 trigger preset (auto-written from tray)`r`n"
            . "preset=" TriggerId "`r`n"
        try FileDelete(path)
        FileAppend(body, path, "UTF-8")
    }
}

RegisterTriggerHotkeys() {
    global TriggerHotkey, LiteralHotkey, TriggerHotkeysBound
    static prevTrig := "", prevLit := ""
    if TriggerHotkeysBound {
        try Hotkey(prevTrig, "Off")
        try Hotkey(prevLit, "Off")
    }
    LoadTriggerPreset()
    global TriggerHotkey, LiteralHotkey
    Hotkey(TriggerHotkey, OnTrigger)
    Hotkey(LiteralHotkey, SendLiteralTrigger)
    prevTrig := TriggerHotkey
    prevLit := LiteralHotkey
    TriggerHotkeysBound := true
}

SetTriggerPreset(id) {
    ApplyTriggerPreset(id, true)
    RegisterTriggerHotkeys()
    BuildTray()
    A_IconTip := StatusTip()
    global TriggerId, TriggerChar
    TrayTip("KeySwap 2.8", "Trigger: " TriggerId " (" TriggerChar ")", "Iconi")
    ShowHud("trigger " TriggerId " → " TriggerChar)
}

SendLiteralTrigger(*) {
    global TriggerChar
    if !AppAllowed() {
        SendInput("{Text}" TriggerChar)
        return
    }
    SendInput("{Text}" TriggerChar)
    ShowHud("literal " TriggerChar)
}

OnMark(mark, *) {
    global LastForm, Mode
    if !AppAllowed()
        return
    if (Mode = "smart" || Mode = "writer") {
        LastForm := mark
        SetTimer(TrySmartAfterLetter, -10)
    }
}

AppAllowed() {
    global AllowList
    if AllowList.Length = 0
        return true
    try {
        p := WinGetProcessName("A")
    } catch {
        return true
    }
    for name in AllowList {
        if (StrLower(name) = StrLower(p))
            return true
    }
    return false
}

ShowHud(msg) {
    global HudOn
    if !HudOn
        return
    ToolTip(msg)
    SetTimer(() => ToolTip(), -1200)
}

OnLetter(letter, *) {
    global Mode, LastForm, DeadArmed
    if !AppAllowed()
        return
    if (Mode = "deadkey" && DeadArmed) {
        DeadArmed := false
        mapped := DeadMap(letter)
        if (mapped != "") {
            SendInput("{Backspace}{Backspace}{Text}" mapped)
            LastForm := mapped
            ShowHud(letter " → " mapped)
            return
        }
    }
    LastForm := letter
    if (Mode = "smart" || Mode = "writer")
        SetTimer(TrySmartAfterLetter, -10)
}

TrySmartAfterLetter() {
    global LastForm, SmartPairs
    if !AppAllowed()
        return
    static prev := ""
    cur := LastForm
    pair := prev . cur
    for p in SmartPairs {
        if (p.src = pair) {
            SendInput("{Backspace}{Backspace}{Text}" p.dst)
            LastForm := p.dst
            ShowHud(pair " → " p.dst)
            prev := ""
            return
        }
    }
    prev := cur
}

OnTrigger(*) {
    global Mode, LastForm, FormIndex, Chains, TriggerChar
    if !AppAllowed() {
        SendInput("{Text}" TriggerChar)
        return
    }
    if (Mode = "deadkey") {
        SendInput("{Text}" TriggerChar)
        return
    }
    if (LastForm = "" || !FormIndex.Has(LastForm)) {
        SendInput("{Text}" TriggerChar)
        return
    }
    info := FormIndex[LastForm]
    chain := Chains[info.chain]
    ni := Mod(info.idx, chain.Length) + 1
    next := chain[ni]
    delCount := StrLen(LastForm)
    Loop delCount
        SendInput("{Backspace}")
    SendInput("{Text}" next)
    ShowHud(LastForm " → " next)
    LastForm := next
}

DeadMap(letter) {
    m := Map(
        "a", "ā", "i", "ī", "u", "ū", "r", "ṛ", "l", "ḷ",
        "m", "ṃ", "h", "ḥ", "n", "ṇ", "t", "ṭ", "d", "ḍ", "s", "ś",
        "A", "Ā", "I", "Ī", "U", "Ū", "R", "Ṛ", "L", "Ḷ",
        "M", "Ṃ", "H", "Ḥ", "N", "Ṇ", "T", "Ṭ", "D", "Ḍ", "S", "Ś"
    )
    return m.Has(letter) ? m[letter] : ""
}

InitSmartPairs(mode := "smart") {
    global SmartPairs
    SmartPairs := []
    classic := [
        ["aa", "ā"], ["ii", "ī"], ["uu", "ū"], ["rr", "ṛ"], ["ll", "ḷ"],
        ["mm", "ṃ"], ["hh", "ḥ"], ["AA", "Ā"], ["II", "Ī"], ["UU", "Ū"],
        ["sh", "ś"], ["ss", "ṣ"], ["ng", "ṅ"], ["ny", "ñ"], ["nn", "ṇ"],
        ["tt", "ṭ"], ["dd", "ḍ"]
    ]
    ; Sanskrit Writer–style top→bottom digraphs (mark then letter)
    writer := [
        ["-a", "ā"], ["-i", "ī"], ["-u", "ū"], ["-A", "Ā"], ["-I", "Ī"], ["-U", "Ū"],
        ["~n", "ñ"], ["~N", "Ñ"], ["~m", "ṃ"], ["~M", "Ṃ"],
        ["'s", "ś"], ["'S", "Ś"],
        ["h.", "ḥ"], ["H.", "Ḥ"], ["r.", "ṛ"], ["R.", "Ṛ"], ["l.", "ḷ"], ["L.", "Ḷ"],
        ["m.", "ṃ"], ["M.", "Ṃ"], ["n.", "ṇ"], ["N.", "Ṇ"], ["t.", "ṭ"], ["T.", "Ṭ"],
        ["d.", "ḍ"], ["D.", "Ḍ"], ["s.", "ṣ"], ["S.", "Ṣ"],
        [".h", "ḥ"], [".H", "Ḥ"], [".r", "ṛ"], [".R", "Ṛ"], [".l", "ḷ"], [".L", "Ḷ"],
        [".m", "ṃ"], [".M", "Ṃ"], [".n", "ṇ"], [".N", "Ṇ"], [".t", "ṭ"], [".T", "Ṭ"],
        [".d", "ḍ"], [".D", "Ḍ"], [".s", "ṣ"], [".S", "Ṣ"]
    ]
    raw := classic
    if (mode = "writer") {
        raw := []
        for item in writer
            raw.Push(item)
        for item in classic
            raw.Push(item)
    }
    for item in raw
        SmartPairs.Push({src: item[1], dst: item[2]})
}

ToggleScriptMode() {
    global ScriptMode
    ScriptMode := (ScriptMode = "iast") ? "deva" : "iast"
    label := (ScriptMode = "deva") ? "Devanāgarī" : "IAST"
    ShowHud("Script mode: " label)
    TrayTip("KeySwap", "Script mode: " label " — Ctrl+Alt+V converts clipboard", "Iconi")
    A_IconTip := StatusTip()
}

ConvertToScriptMode() {
    global ScriptMode
    ConvertClipboard(ScriptMode, "auto")
}

LoadAllowList() {
    global AllowList
    AllowList := []
    path := A_ScriptDir "\allowlist.txt"
    if !FileExist(path)
        return
    for line in StrSplit(FileRead(path, "UTF-8"), "`n", "`r") {
        t := Trim(line)
        if (t = "" || SubStr(t, 1, 1) = "#")
            continue
        AllowList.Push(t)
    }
}

CheckKeyman() {
    global KeymanWarned
    ; Known Keyman process names
    names := ["keyman.exe", "kmshell.exe", "KeymanDesktop.exe", "keymanx64.exe"]
    found := false
    for n in names {
        if ProcessExist(n) {
            found := true
            break
        }
    }
    if found && !KeymanWarned {
        KeymanWarned := true
        TrayTip(
            "KeySwap 2.1",
            "Keyman appears to be running. Dual hooks often conflict — pause one of them.",
            "Icon!"
        )
    }
    if !found
        KeymanWarned := false
}

LoadAll() {
    global ConfigPath, Chains, FormIndex, ConfigMTime, StatusText, Mode, AllowList
    if !FileExist(ConfigPath) {
        MsgBox("Config not found:`n" ConfigPath, "KeySwap 2.1", "Iconx")
        ExitApp(1)
    }
    Chains := LoadChains(ConfigPath)
    FormIndex := Map()
    for ci, chain in Chains {
        for fi, form in chain {
            if !FormIndex.Has(form)
                FormIndex[form] := {chain: ci, idx: fi}
        }
    }
    LoadAllowList()
    ConfigMTime := FileGetTime(ConfigPath, "M")
    al := AllowList.Length ? (AllowList.Length " apps") : "all apps"
    StatusText := "KeySwap 2.9 | " Mode " | " ConfigLabel(ConfigPath) " | " Chains.Length " chains | " al
    A_IconTip := StatusTip()
    ShowHud("Reloaded · " al)
}

WatchConfig() {
    global ConfigPath, ConfigMTime
    if !FileExist(ConfigPath)
        return
    mt := FileGetTime(ConfigPath, "M")
    if (mt != ConfigMTime) {
        LoadAll()
        TrayTip("KeySwap 2.1", "Config reloaded", "Iconi")
    }
}

LoadChains(path) {
    raw := FileRead(path, "UTF-8")
    chains := []
    bases := Map()
    lineNo := 0
    for line in StrSplit(raw, "`n", "`r") {
        lineNo++
        t := Trim(line)
        if (t = "" || SubStr(t, 1, 1) = "#")
            continue
        if InStr(t, " #")
            t := Trim(StrSplit(t, " #")[1])
        parts := []
        for p in StrSplit(t, ">") {
            p := Trim(p)
            if p != ""
                parts.Push(p)
        }
        if parts.Length < 2
            continue
        if bases.Has(parts[1]) {
            MsgBox("Duplicate base '" parts[1] "' at line " lineNo "`nFix config and press F6.", "KeySwap 2.1", "Iconx")
            continue
        }
        bases[parts[1]] := lineNo
        chains.Push(parts)
    }
    if chains.Length = 0 {
        MsgBox("No chains in config:`n" path, "KeySwap 2.1", "Iconx")
        ExitApp(1)
    }
    return chains
}

ConvertClipboard(to, frm) {
    py := "python"
    script := A_ScriptDir "\..\convert_bridge.py"
    if !FileExist(script) {
        MsgBox("Missing convert_bridge.py", "KeySwap 2.1", "Iconx")
        return
    }
    tmpIn := A_Temp "\keyswap_in.txt"
    tmpOut := A_Temp "\keyswap_out.txt"
    try FileDelete(tmpIn)
    try FileDelete(tmpOut)
    FileAppend(A_Clipboard, tmpIn, "UTF-8")
    ps := Format(
        "$in = Get-Content -Raw -Encoding UTF8 '{1}'; $in | & {2} '{3}' --from {4} --to {5} | Set-Content -Encoding UTF8 -NoNewline '{6}'",
        tmpIn, py, script, frm, to, tmpOut
    )
    RunWait('powershell -NoProfile -Command ' ps, , "Hide")
    if FileExist(tmpOut) {
        A_Clipboard := FileRead(tmpOut, "UTF-8")
        ShowHud("clipboard → " to)
        TrayTip("KeySwap 2.1", "Clipboard → " to, "Iconi")
    } else {
        MsgBox("Convert failed (Python + sanskrit-util py/ required).", "KeySwap 2.1", "Iconx")
    }
}

; Live, in-place conversion of the current text selection — no manual
; copy → convert → switch-app → paste round trip. Off by default: nothing
; happens unless the user selects text and presses the hotkey/tray item.
ConvertSelectionInPlace(to, frm) {
    if !AppAllowed()
        return
    saved := ClipboardAll()
    A_Clipboard := ""
    SendInput("^c")
    if !ClipWait(0.5) {
        A_Clipboard := saved
        ShowHud("nothing selected")
        return
    }
    src := A_Clipboard
    out := ConvertTextViaBridge(src, to, frm)
    if (out = "") {
        A_Clipboard := saved
        ShowHud("live convert failed (Python + sanskrit-util py/ required)")
        return
    }
    A_Clipboard := out
    SendInput("^v")
    Sleep(80)
    A_Clipboard := saved
    ShowHud("selection → " to)
}

; Same bridge as ConvertClipboard, but on explicit text — never touches A_Clipboard.
ConvertTextViaBridge(text, to, frm) {
    py := "python"
    script := A_ScriptDir "\..\convert_bridge.py"
    if !FileExist(script)
        return ""
    tmpIn := A_Temp "\keyswap_live_in.txt"
    tmpOut := A_Temp "\keyswap_live_out.txt"
    try FileDelete(tmpIn)
    try FileDelete(tmpOut)
    FileAppend(text, tmpIn, "UTF-8")
    ps := Format(
        "$in = Get-Content -Raw -Encoding UTF8 '{1}'; $in | & {2} '{3}' --from {4} --to {5} | Set-Content -Encoding UTF8 -NoNewline '{6}'",
        tmpIn, py, script, frm, to, tmpOut
    )
    RunWait('powershell -NoProfile -Command ' ps, , "Hide")
    if FileExist(tmpOut)
        return FileRead(tmpOut, "UTF-8")
    return ""
}

ToggleHud() {
    global HudOn
    HudOn := !HudOn
    TrayTip("KeySwap 2.1", "Teaching HUD: " (HudOn ? "ON" : "OFF"), "Iconi")
}

OpenCologneSearch() {
    py := "python"
    script := A_ScriptDir "\..\cologne_search.py"
    if !FileExist(script) {
        MsgBox("Missing cologne_search.py", "KeySwap", "Iconx")
        return
    }
    tmpIn := A_Temp "\keyswap_cologne.txt"
    try FileDelete(tmpIn)
    FileAppend(A_Clipboard, tmpIn, "UTF-8")
    ; --open builds URL and opens browser; print keys via tray
    ps := Format(
        "Get-Content -Raw -Encoding UTF8 '{1}' | & {2} '{3}' --from auto --dict mw --open --print-keys",
        tmpIn, py, script
    )
    RunWait('powershell -NoProfile -Command ' ps, , "Hide")
    ShowHud("Cologne Simple Search")
    TrayTip("KeySwap", "Opened Cologne Simple Search for clipboard", "Iconi")
}

; Typing-tool: last clipboard token → Cologne API, then local wordlist if offline
CheckClipboardHeadword() {
    py := "python"
    script := A_ScriptDir "\..\typing_check.py"
    if !FileExist(script) {
        MsgBox("Missing typing_check.py", "KeySwap", "Iconx")
        return
    }
    tmpIn := A_Temp "\keyswap_check_in.txt"
    tmpOut := A_Temp "\keyswap_check_out.txt"
    try FileDelete(tmpIn)
    try FileDelete(tmpOut)
    FileAppend(A_Clipboard, tmpIn, "UTF-8")
    ps := Format(
        "Get-Content -Raw -Encoding UTF8 '{1}' | & {2} '{3}' --from auto --dict mw --hud --timeout 12 | Set-Content -Encoding UTF8 -NoNewline '{4}'",
        tmpIn, py, script, tmpOut
    )
    ShowHud("checking Cologne…")
    RunWait('powershell -NoProfile -Command ' ps, , "Hide")
    if FileExist(tmpOut) {
        msg := FileRead(tmpOut, "UTF-8")
        ShowHud(msg)
        TrayTip("KeySwap headword", msg, "Iconi")
    } else {
        ShowHud("check failed (Python / network?)")
    }
}

; Open Cologne webtc full entry (gloss) for clipboard headword
OpenCologneGloss() {
    py := "python"
    script := A_ScriptDir "\..\typing_check.py"
    if !FileExist(script) {
        MsgBox("Missing typing_check.py", "KeySwap", "Iconx")
        return
    }
    tmpIn := A_Temp "\keyswap_gloss_in.txt"
    try FileDelete(tmpIn)
    FileAppend(A_Clipboard, tmpIn, "UTF-8")
    ps := Format(
        "Get-Content -Raw -Encoding UTF8 '{1}' | & {2} '{3}' --from auto --dict mw --no-verify --open-gloss --hud",
        tmpIn, py, script
    )
    ShowHud("opening gloss…")
    RunWait('powershell -NoProfile -Command ' ps, , "Hide")
    TrayTip("KeySwap", "Opened Cologne webtc entry (gloss)", "Iconi")
}

UseWriterProfile() {
    global ConfigPath, Mode
    ConfigPath := A_ScriptDir "\..\configs\writer-scheme.txt"
    Mode := "writer"
    InitSmartPairs("writer")
    LoadAll()
    TrayTip("KeySwap", "Writer-scheme profile + digraphs (-a, ~n, 's, h.)", "Iconi")
}

UseClassicProfile() {
    global ConfigPath, Mode
    ConfigPath := A_ScriptDir "\..\configs\iast-classic.txt"
    Mode := "smart"
    InitSmartPairs("smart")
    LoadAll()
    TrayTip("KeySwap", "IAST classic + smart digraphs", "Iconi")
}

UsePaliProfile() {
    global ConfigPath, Mode
    ConfigPath := A_ScriptDir "\..\configs\pali-lite.txt"
    Mode := "smart"
    InitSmartPairs("smart")
    LoadAll()
    TrayTip("KeySwap", "Pali-lite profile", "Iconi")
}

; Copy SLP1 + dalnorm key of clipboard (no browser)
CopySlp1Normkey() {
    py := "python"
    script := A_ScriptDir "\..\cologne_search.py"
    if !FileExist(script) {
        MsgBox("Missing cologne_search.py", "KeySwap", "Iconx")
        return
    }
    tmpIn := A_Temp "\keyswap_keys_in.txt"
    tmpOut := A_Temp "\keyswap_keys_out.txt"
    try FileDelete(tmpIn)
    try FileDelete(tmpOut)
    FileAppend(A_Clipboard, tmpIn, "UTF-8")
    ps := Format(
        "Get-Content -Raw -Encoding UTF8 '{1}' | & {2} '{3}' --from auto --print-keys | Set-Content -Encoding UTF8 '{4}'",
        tmpIn, py, script, tmpOut
    )
    RunWait('powershell -NoProfile -Command ' ps, , "Hide")
    if FileExist(tmpOut) {
        txt := FileRead(tmpOut, "UTF-8")
        A_Clipboard := txt
        ShowHud("SLP1+normkey → clipboard")
        TrayTip("KeySwap keys", txt, "Iconi")
    } else {
        ShowHud("keys failed (Python?)")
    }
}

OpenUrl(url) {
    Run(url)
}

BuildTray() {
    global TriggerId
    A_TrayMenu.Delete()
    A_TrayMenu.Add("KeySwap 2.9", (*) => 0)
    A_TrayMenu.Disable("KeySwap 2.9")
    A_TrayMenu.Add()
    A_TrayMenu.Add("Mode: cycle", (*) => SetMode("cycle"))
    A_TrayMenu.Add("Mode: smart (default)", (*) => SetMode("smart"))
    A_TrayMenu.Add("Mode: writer (Sanskrit Writer-style)", (*) => SetMode("writer"))
    A_TrayMenu.Add("Mode: deadkey", (*) => SetMode("deadkey"))
    A_TrayMenu.Add()
    trig := Menu()
    trig.Add("Equals (=) — default US", (*) => SetTriggerPreset("equals"))
    trig.Add("Bracket (]) — non-US / Word", (*) => SetTriggerPreset("bracket"))
    trig.Add("Slash (/)", (*) => SetTriggerPreset("slash"))
    trig.Add("Backtick (`)", (*) => SetTriggerPreset("backtick"))
    A_TrayMenu.Add("Trigger: " TriggerId, trig)
    A_TrayMenu.Add()
    A_TrayMenu.Add("Profile: IAST classic", (*) => UseClassicProfile())
    A_TrayMenu.Add("Profile: Writer-scheme", (*) => UseWriterProfile())
    A_TrayMenu.Add("Profile: Pali-lite", (*) => UsePaliProfile())
    A_TrayMenu.Add()
    A_TrayMenu.Add("Toggle script mode IAST/Deva (Ctrl+Alt+D)", (*) => ToggleScriptMode())
    A_TrayMenu.Add("Clipboard → script mode (Ctrl+Alt+V)", (*) => ConvertToScriptMode())
    A_TrayMenu.Add("Copy SLP1+normkey (Ctrl+Alt+K)", (*) => CopySlp1Normkey())
    A_TrayMenu.Add("Reload config (F6)", (*) => {
        LoadAll()
        RegisterTriggerHotkeys()
        BuildTray()
    })
    A_TrayMenu.Add("Toggle teaching HUD (F7)", (*) => ToggleHud())
    A_TrayMenu.Add("Open configs folder", (*) => Run('explorer.exe "' A_ScriptDir '\..\configs"'))
    A_TrayMenu.Add("Edit allowlist", (*) => EditAllowList())
    A_TrayMenu.Add("Edit trigger.ini", (*) => EditTriggerIni())
    A_TrayMenu.Add()
    A_TrayMenu.Add("Clipboard → Devanagari", (*) => ConvertClipboard("deva", "auto"))
    A_TrayMenu.Add("Clipboard → IAST (auto scheme)", (*) => ConvertClipboard("iast", "auto"))
    A_TrayMenu.Add("Selection → Devanagari in place (Ctrl+Alt+Shift+D)", (*) => ConvertSelectionInPlace("deva", "auto"))
    A_TrayMenu.Add("Clipboard → Cologne Simple Search (Ctrl+Alt+C)", (*) => OpenCologneSearch())
    A_TrayMenu.Add("Clipboard headword check (Ctrl+Alt+S)", (*) => CheckClipboardHeadword())
    A_TrayMenu.Add("Clipboard → MW gloss page (Ctrl+Alt+G)", (*) => OpenCologneGloss())
    A_TrayMenu.Add()
    eco := Menu()
    eco.Add("Sanscript (learnsanskrit.org)", (*) => OpenUrl("https://www.learnsanskrit.org/tools/sanscript/"))
    eco.Add("Aksharamukha (scripts / Brahmi)", (*) => OpenUrl("https://www.aksharamukha.com/converter"))
    eco.Add("Lexilogos Sanskrit Latin", (*) => OpenUrl("https://www.lexilogos.com/keyboard/sanskrit_latin.htm"))
    eco.Add("Dunning ABC Extended (Windows layouts)", (*) => OpenUrl("https://github.com/adunning/Mac-Keyboard-Layouts-for-Windows"))
    eco.Add("EasyUnicode (Mac)", (*) => OpenUrl("https://www.yogicstudies.com/blog/how-to-type-transliterated-sanskrit-with-diacritics-in-mac-osx"))
    eco.Add("Keyman Heidelberg Input Solution", (*) => OpenUrl("https://keyman.com/keyboards/heidelberginputsolution"))
    eco.Add("Sanskrit Writer (Auroville)", (*) => OpenUrl("https://sri.auroville.org/projects/sanskrit-writer/"))
    eco.Add("UBC Sanskrit tools", (*) => OpenUrl("https://blogs.ubc.ca/ubcsanskrit/tools/"))
    eco.Add("Cologne Simple Search", (*) => OpenUrl("https://sanskrit-lexicon.uni-koeln.de/simple/"))
    A_TrayMenu.Add("Ecosystem (peers)", eco)
    A_TrayMenu.Add()
    A_TrayMenu.Add("Exit", (*) => ExitApp())
}

EditTriggerIni() {
    path := A_ScriptDir "\trigger.ini"
    if !FileExist(path) {
        ex := A_ScriptDir "\trigger.example.ini"
        if FileExist(ex)
            FileCopy(ex, path)
        else
            FileAppend("preset=equals`r`n", path, "UTF-8")
    }
    Run("notepad.exe " path)
}

EditAllowList() {
    path := A_ScriptDir "\allowlist.txt"
    if !FileExist(path)
        FileCopy(A_ScriptDir "\allowlist.example.txt", path)
    Run("notepad.exe " path)
}

SetMode(m) {
    global Mode
    Mode := m
    if (m = "writer" || m = "smart")
        InitSmartPairs(m)
    A_IconTip := StatusTip()
    TrayTip("KeySwap 2.8", "Mode: " m, "Iconi")
}

StatusTip() {
    global StatusText, Mode, ScriptMode, TriggerId, TriggerChar
    base := StatusText != "" ? StatusText : ("KeySwap 2.9 | " Mode)
    return base " | script=" ScriptMode " | trig=" TriggerId "(" TriggerChar ")"
}

ConfigLabel(path) {
    SplitPath(path, &name)
    return name
}
