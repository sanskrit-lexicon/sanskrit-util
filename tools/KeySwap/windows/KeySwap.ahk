; KeySwap.ahk — open Windows reimplementation of the IAST diacritic cycler
; Requires AutoHotkey v2: https://www.autohotkey.com/
; MIT license (sanskrit-util tools/KeySwap)
;
; Type a base letter, press = to cycle through diacritic forms.
; Tracks the last form typed or cycled (same model as classic Keyswap).

#Requires AutoHotkey v2.0
#SingleInstance Force
Persistent

configPath := A_Args.Length >= 1 ? A_Args[1] : A_ScriptDir "\..\config.txt"
global Chains := LoadChains(configPath)
global FormIndex := Map()
global LastForm := ""
BuildIndex()

A_IconTip := "KeySwap (AHK) — press = after a letter | " ConfigLabel(configPath)
A_TrayMenu.Delete()
A_TrayMenu.Add("Reload config", (*) => Reload())
A_TrayMenu.Add("Open configs folder", (*) => Run('explorer.exe "' A_ScriptDir '\..\configs"'))
A_TrayMenu.Add()
A_TrayMenu.Add("Exit", (*) => ExitApp())

; Pass-through letter tracking (Latin letters used as bases)
bases := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
Loop Parse bases {
    Hotkey("~*" A_LoopField, MarkLetter.Bind(A_LoopField))
}

; Trigger: =
=:: CycleLast()

MarkLetter(letter, *) {
    global LastForm
    LastForm := letter
}

CycleLast(*) {
    global LastForm, FormIndex, Chains
    if (LastForm = "" || !FormIndex.Has(LastForm)) {
        ; Still send = if nothing to cycle (user wanted a literal equals)
        SendInput("=")
        return
    }
    info := FormIndex[LastForm]
    chain := Chains[info.chain]
    ni := Mod(info.idx, chain.Length) + 1
    next := chain[ni]
    ; Replace previous form: delete as many UTF-16 units as LastForm, insert next
    delCount := StrLen(LastForm)
    Loop delCount
        SendInput("{Backspace}")
    SendInput("{Text}" next)
    LastForm := next
}

LoadChains(path) {
    if !FileExist(path) {
        MsgBox("Config not found:`n" path, "KeySwap", "Iconx")
        ExitApp(1)
    }
    raw := FileRead(path, "UTF-8")
    chains := []
    for line in StrSplit(raw, "`n", "`r") {
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
        if parts.Length >= 2
            chains.Push(parts)
    }
    if chains.Length = 0 {
        MsgBox("No chains in config:`n" path, "KeySwap", "Iconx")
        ExitApp(1)
    }
    return chains
}

BuildIndex() {
    global Chains, FormIndex
    FormIndex := Map()
    for ci, chain in Chains {
        for fi, form in chain {
            if !FormIndex.Has(form)
                FormIndex[form] := {chain: ci, idx: fi}
        }
    }
}

ConfigLabel(path) {
    SplitPath(path, &name)
    return name
}
