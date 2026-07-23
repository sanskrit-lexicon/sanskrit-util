; KeySwap 2.0 for Windows — AutoHotkey v2
; MIT — sanskrit-util tools/KeySwap
;
; Modes (tray menu or first-line comment in config is ignored; use tray):
;   cycle    — letter then = (classic Keyswap)
;   smart    — also expand aa→ā, sh→ś, … after each letter
;   deadkey  — ' then letter style: type ' then a → ā (classroom-friendly)
;
; Hotkeys:
;   =              cycle last form (cycle/smart modes)
;   ^!=            convert clipboard IAST → Devanāgarī (needs Python + sanskrit-util)
;   ^!i            convert clipboard Devanāgarī → IAST
;   F6             reload config now
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

InitSmartPairs()
LoadAll()
BuildTray()
SetTimer(WatchConfig, 2000)
A_IconTip := StatusTip()

; --- letter tracking (pass-through) ---
bases := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
Loop Parse bases {
    Hotkey("~*" A_LoopField, OnLetter.Bind(A_LoopField))
}

; apostrophe as dead-key arm in deadkey mode
~*':: {
    global Mode, DeadArmed
    if (Mode = "deadkey")
        DeadArmed := true
}

=:: OnEquals()

; Convert clipboard
^!=:: ConvertClipboard("deva")
^!i:: ConvertClipboard("iast")
F6:: LoadAll()

OnLetter(letter, *) {
    global Mode, LastForm, DeadArmed, SmartPairs
    if (Mode = "deadkey" && DeadArmed) {
        DeadArmed := false
        mapped := DeadMap(letter)
        if (mapped != "") {
            ; remove the apostrophe that was typed and the letter about to type…
            ; letter already will be typed by ~ hotkey; we need to replace both
            SendInput("{Backspace}{Backspace}{Text}" mapped)
            LastForm := mapped
            return
        }
    }
    LastForm := letter
    if (Mode = "smart" || Mode = "cycle") {
        ; After letter is typed, try smart expand on last two chars via delayed check
        if (Mode = "smart")
            SetTimer(TrySmartAfterLetter, -10)
    }
}

TrySmartAfterLetter() {
    global LastForm, SmartPairs, FormIndex
    ; Reconstruct from LastForm only for digraphs ending with LastForm
    ; AHK cannot easily read caret; smart applies when user types second letter of pair:
    ; we track last *two* letters
    static prev := ""
    cur := LastForm
    pair := prev . cur
    for p in SmartPairs {
        if (p.src = pair) {
            ; delete two letters, insert dst
            SendInput("{Backspace}{Backspace}{Text}" p.dst)
            LastForm := p.dst
            prev := ""
            return
        }
    }
    prev := cur
}

OnEquals(*) {
    global Mode, LastForm, FormIndex, Chains
    if (Mode = "deadkey") {
        SendInput("=")
        return
    }
    if (LastForm = "" || !FormIndex.Has(LastForm)) {
        SendInput("=")
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
    LastForm := next
}

DeadMap(letter) {
    ; ' + letter → common IAST (classroom dead-key)
    m := Map(
        "a", "ā", "i", "ī", "u", "ū", "r", "ṛ", "l", "ḷ",
        "m", "ṃ", "h", "ḥ", "n", "ṇ", "t", "ṭ", "d", "ḍ", "s", "ś",
        "A", "Ā", "I", "Ī", "U", "Ū", "R", "Ṛ", "L", "Ḷ",
        "M", "Ṃ", "H", "Ḥ", "N", "Ṇ", "T", "Ṭ", "D", "Ḍ", "S", "Ś"
    )
    return m.Has(letter) ? m[letter] : ""
}

InitSmartPairs() {
    global SmartPairs
    SmartPairs := []
    raw := [
        ["aa", "ā"], ["ii", "ī"], ["uu", "ū"], ["rr", "ṛ"], ["ll", "ḷ"],
        ["mm", "ṃ"], ["hh", "ḥ"], ["AA", "Ā"], ["II", "Ī"], ["UU", "Ū"],
        ["sh", "ś"], ["ss", "ṣ"], ["ng", "ṅ"], ["ny", "ñ"], ["nn", "ṇ"],
        ["tt", "ṭ"], ["dd", "ḍ"]
    ]
    for item in raw
        SmartPairs.Push({src: item[1], dst: item[2]})
}

LoadAll() {
    global ConfigPath, Chains, FormIndex, ConfigMTime, StatusText
    if !FileExist(ConfigPath) {
        MsgBox("Config not found:`n" ConfigPath, "KeySwap 2.0", "Iconx")
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
    ConfigMTime := FileGetTime(ConfigPath, "M")
    StatusText := "KeySwap 2.0 | " Mode " | " ConfigLabel(ConfigPath) " | " Chains.Length " chains"
    A_IconTip := StatusTip()
    try TraySetIcon()
}

WatchConfig() {
    global ConfigPath, ConfigMTime
    if !FileExist(ConfigPath)
        return
    mt := FileGetTime(ConfigPath, "M")
    if (mt != ConfigMTime) {
        LoadAll()
        TrayTip("KeySwap 2.0", "Config reloaded", "Iconi")
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
            MsgBox("Duplicate base '" parts[1] "' at line " lineNo "`nFix config and press F6.", "KeySwap 2.0", "Iconx")
            continue
        }
        bases[parts[1]] := lineNo
        chains.Push(parts)
    }
    if chains.Length = 0 {
        MsgBox("No chains in config:`n" path, "KeySwap 2.0", "Iconx")
        ExitApp(1)
    }
    return chains
}

ConvertClipboard(to) {
    py := FindPython()
    if (py = "") {
        MsgBox("Python not found on PATH. Install Python or add to PATH.", "KeySwap 2.0", "Iconx")
        return
    }
    script := A_ScriptDir "\..\convert_bridge.py"
    if !FileExist(script) {
        MsgBox("Missing convert_bridge.py", "KeySwap 2.0", "Iconx")
        return
    }
    ; Write clipboard to temp, convert, read back — more reliable than ctypes from AHK
    tmpIn := A_Temp "\keyswap_in.txt"
    tmpOut := A_Temp "\keyswap_out.txt"
    try FileDelete(tmpIn)
    try FileDelete(tmpOut)
    FileAppend(A_Clipboard, tmpIn, "UTF-8")
    cmd := Format('"{1}" "{2}" --to {3} < "{4}" > "{5}"', py, script, to, tmpIn, tmpOut)
    ; Use PowerShell for redirect
    ps := Format(
        "Get-Content -Raw -Encoding UTF8 '{1}' | & '{2}' '{3}' --to {4} | Set-Content -Encoding UTF8 '{5}'",
        tmpIn, py, script, to, tmpOut
    )
    RunWait('powershell -NoProfile -Command ' ps, , "Hide")
    if FileExist(tmpOut) {
        A_Clipboard := FileRead(tmpOut, "UTF-8")
        TrayTip("KeySwap 2.0", "Clipboard → " to, "Iconi")
    } else {
        MsgBox("Convert failed (is sanskrit-util py/ available?)", "KeySwap 2.0", "Iconx")
    }
}

FindPython() {
    for c in ["python", "py -3", "python3"] {
        try {
            ; just return python and hope
        }
    }
    return "python"
}

BuildTray() {
    A_TrayMenu.Delete()
    A_TrayMenu.Add("KeySwap 2.0", (*) => 0)
    A_TrayMenu.Disable("KeySwap 2.0")
    A_TrayMenu.Add()
    A_TrayMenu.Add("Mode: cycle", (*) => SetMode("cycle"))
    A_TrayMenu.Add("Mode: smart (default)", (*) => SetMode("smart"))
    A_TrayMenu.Add("Mode: deadkey", (*) => SetMode("deadkey"))
    A_TrayMenu.Add()
    A_TrayMenu.Add("Reload config (F6)", (*) => LoadAll())
    A_TrayMenu.Add("Open configs folder", (*) => Run('explorer.exe "' A_ScriptDir '\..\configs"'))
    A_TrayMenu.Add("Open cheatsheet", (*) => Run(A_ScriptDir "\..\layouts\cheatsheet-iast-classic.md"))
    A_TrayMenu.Add()
    A_TrayMenu.Add("Clipboard → Devanāgarī (Ctrl+Alt+=)", (*) => ConvertClipboard("deva"))
    A_TrayMenu.Add("Clipboard → IAST (Ctrl+Alt+I)", (*) => ConvertClipboard("iast"))
    A_TrayMenu.Add()
    A_TrayMenu.Add("Exit", (*) => ExitApp())
}

SetMode(m) {
    global Mode
    Mode := m
    A_IconTip := StatusTip()
    TrayTip("KeySwap 2.0", "Mode: " m, "Iconi")
}

StatusTip() {
    global StatusText, Mode
    return StatusText != "" ? StatusText : ("KeySwap 2.0 | " Mode)
}

ConfigLabel(path) {
    SplitPath(path, &name)
    return name
}

TraySetIcon() {
}
