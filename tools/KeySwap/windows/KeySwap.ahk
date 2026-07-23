; KeySwap 2.1 for Windows — AutoHotkey v2
; MIT — sanskrit-util tools/KeySwap
;
; Modes: cycle | smart (default) | deadkey
; Guards: Keyman process warn; optional allowlist.txt; teaching HUD tooltips
;
; Hotkeys:
;   =                 cycle last form
;   ^!=               clipboard → Devanāgarī
;   ^!i               clipboard → IAST
;   ^!h               clipboard HK/ITRANS/auto → IAST
;   F6                reload config + allowlist
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

InitSmartPairs()
LoadAll()
BuildTray()
CheckKeyman()
SetTimer(WatchConfig, 2000)
SetTimer(CheckKeyman, 30000)
A_IconTip := StatusTip()

bases := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
Loop Parse bases {
    Hotkey("~*" A_LoopField, OnLetter.Bind(A_LoopField))
}

~*':: {
    global Mode, DeadArmed
    if (Mode = "deadkey" && AppAllowed())
        DeadArmed := true
}

=:: OnEquals()
^!=:: ConvertClipboard("deva", "auto")
^!i:: ConvertClipboard("iast", "auto")
^!h:: ConvertClipboard("iast", "auto")  ; scheme auto → IAST
F6:: LoadAll()
F7:: ToggleHud()

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
    if (Mode = "smart")
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

OnEquals(*) {
    global Mode, LastForm, FormIndex, Chains
    if !AppAllowed() {
        SendInput("=")
        return
    }
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
    StatusText := "KeySwap 2.1 | " Mode " | " ConfigLabel(ConfigPath) " | " Chains.Length " chains | " al
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

ToggleHud() {
    global HudOn
    HudOn := !HudOn
    TrayTip("KeySwap 2.1", "Teaching HUD: " (HudOn ? "ON" : "OFF"), "Iconi")
}

BuildTray() {
    A_TrayMenu.Delete()
    A_TrayMenu.Add("KeySwap 2.1", (*) => 0)
    A_TrayMenu.Disable("KeySwap 2.1")
    A_TrayMenu.Add()
    A_TrayMenu.Add("Mode: cycle", (*) => SetMode("cycle"))
    A_TrayMenu.Add("Mode: smart (default)", (*) => SetMode("smart"))
    A_TrayMenu.Add("Mode: deadkey", (*) => SetMode("deadkey"))
    A_TrayMenu.Add()
    A_TrayMenu.Add("Reload config (F6)", (*) => LoadAll())
    A_TrayMenu.Add("Toggle teaching HUD (F7)", (*) => ToggleHud())
    A_TrayMenu.Add("Open configs folder", (*) => Run('explorer.exe "' A_ScriptDir '\..\configs"'))
    A_TrayMenu.Add("Edit allowlist", (*) => EditAllowList())
    A_TrayMenu.Add()
    A_TrayMenu.Add("Clipboard → Devanāgarī", (*) => ConvertClipboard("deva", "auto"))
    A_TrayMenu.Add("Clipboard → IAST (auto scheme)", (*) => ConvertClipboard("iast", "auto"))
    A_TrayMenu.Add()
    A_TrayMenu.Add("Exit", (*) => ExitApp())
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
    A_IconTip := StatusTip()
    TrayTip("KeySwap 2.1", "Mode: " m, "Iconi")
}

StatusTip() {
    global StatusText, Mode
    return StatusText != "" ? StatusText : ("KeySwap 2.1 | " Mode)
}

ConfigLabel(path) {
    SplitPath(path, &name)
    return name
}
