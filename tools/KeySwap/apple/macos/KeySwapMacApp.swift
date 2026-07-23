import AppKit
import ApplicationServices
import Carbon.HIToolbox
import KeySwapCore
import SwiftUI

/// Menu-bar Mac app: system-wide `=` cycle via CGEvent tap (Accessibility permission).
@main
struct KeySwapMacApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        Settings {
            SettingsView()
                .environmentObject(appDelegate.model)
        }
    }
}

@MainActor
final class AppModel: ObservableObject {
    @Published var profile: KeySwapProfile = .iastClassic
    @Published var status: String = "Starting…"
    @Published var trusted: Bool = false

    private(set) var engine: CycleEngine
    var lastForm: String = ""

    init() {
        engine = (try? CycleEngine.parse(text: Self.embeddedClassic))!
    }

    func reloadEngine() {
        if let url = Bundle.main.url(forResource: profile.rawValue, withExtension: "txt"),
           let eng = try? CycleEngine.load(url: url) {
            engine = eng
            status = "Profile: \(profile.displayName)"
            return
        }
        // Fall back to sibling Resources/configs in repo when running from source tree
        let repo = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent() // macos
            .deletingLastPathComponent() // apple
            .appendingPathComponent("configs", isDirectory: true)
            .appendingPathComponent("\(profile.rawValue).txt")
        if let eng = try? CycleEngine.load(url: repo) {
            engine = eng
            status = "Profile: \(profile.displayName) (repo configs/)"
        } else {
            engine = (try? CycleEngine.parse(text: Self.embeddedClassic))!
            status = "Profile: embedded classic"
        }
    }

    static let embeddedClassic = """
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
    """
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    let model = AppModel()
    private var statusItem: NSStatusItem?
    private var tap: CFMachPort?
    private var source: CFRunLoopSource?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        model.reloadEngine()
        setupStatusItem()
        startTapIfPossible()
    }

    private func setupStatusItem() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let button = statusItem?.button {
            button.title = "ā="
            button.toolTip = "KeySwap — press = after a letter to cycle IAST"
        }
        let menu = NSMenu()
        menu.addItem(withTitle: "Status…", action: #selector(showStatus), keyEquivalent: "")
        menu.addItem(NSMenuItem.separator())
        for p in KeySwapProfile.allCases {
            let item = NSMenuItem(title: p.displayName, action: #selector(selectProfile(_:)), keyEquivalent: "")
            item.representedObject = p.rawValue
            menu.addItem(item)
        }
        menu.addItem(NSMenuItem.separator())
        menu.addItem(withTitle: "Open Accessibility Settings", action: #selector(openAccessibility), keyEquivalent: "")
        menu.addItem(withTitle: "Quit KeySwap", action: #selector(quit), keyEquivalent: "q")
        statusItem?.menu = menu
    }

    @objc private func showStatus() {
        let alert = NSAlert()
        alert.messageText = "KeySwap for Mac"
        alert.informativeText = model.status + "\nAccessibility trusted: \(model.trusted)\n\nType a Latin letter, then press = to cycle diacritics."
        alert.runModal()
    }

    @objc private func selectProfile(_ sender: NSMenuItem) {
        guard let raw = sender.representedObject as? String,
              let p = KeySwapProfile(rawValue: raw) else { return }
        model.profile = p
        model.reloadEngine()
    }

    @objc private func openAccessibility() {
        if let url = URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility") {
            NSWorkspace.shared.open(url)
        }
    }

    @objc private func quit() {
        NSApp.terminate(nil)
    }

    private func startTapIfPossible() {
        let trusted = AXIsProcessTrustedWithOptions(
            [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true] as CFDictionary
        )
        model.trusted = trusted
        if !trusted {
            model.status = "Grant Accessibility, then relaunch KeySwap"
            return
        }
        // Listen for keyDown
        let mask = (1 << CGEventType.keyDown.rawValue)
        let refcon = Unmanaged.passUnretained(self).toOpaque()
        guard let tap = CGEvent.tapCreate(
            tap: .cgSessionEventTap,
            place: .headInsertEventTap,
            options: .defaultTap,
            eventsOfInterest: CGEventMask(mask),
            callback: { _, type, event, refcon in
                guard let refcon else { return Unmanaged.passUnretained(event) }
                let del = Unmanaged<AppDelegate>.fromOpaque(refcon).takeUnretainedValue()
                return del.handle(event: event, type: type)
            },
            userInfo: refcon
        ) else {
            model.status = "Failed to create event tap"
            return
        }
        self.tap = tap
        source = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
        CFRunLoopAddSource(CFRunLoopGetMain(), source, .commonModes)
        CGEvent.tapEnable(tap: tap, enable: true)
        model.status = "Listening — profile \(model.profile.displayName)"
    }

    private func handle(event: CGEvent, type: CGEventType) -> Unmanaged<CGEvent>? {
        if type == .tapDisabledByTimeout || type == .tapDisabledByUserInput {
            if let tap { CGEvent.tapEnable(tap: tap, enable: true) }
            return Unmanaged.passUnretained(event)
        }
        guard type == .keyDown else {
            return Unmanaged.passUnretained(event)
        }
        let keycode = event.getIntegerValueField(.keyboardEventKeycode)
        let flags = event.flags
        // Ignore with Command/Control
        if flags.contains(.maskCommand) || flags.contains(.maskControl) {
            return Unmanaged.passUnretained(event)
        }

        // kVK_ANSI_Equal = 0x18
        if keycode == 0x18 {
            return handleTrigger(event: event)
        }

        // Track ANSI letter keys → update lastForm
        if let letter = Self.letter(forKeycode: keycode, shift: flags.contains(.maskShift)) {
            model.lastForm = letter
        }
        return Unmanaged.passUnretained(event)
    }

    private func handleTrigger(event: CGEvent) -> Unmanaged<CGEvent>? {
        let last = model.lastForm
        guard !last.isEmpty, let next = model.engine.nextForm(of: last) else {
            // Pass through literal =
            return Unmanaged.passUnretained(event)
        }
        // Swallow =, send backspaces + next form
        let del = last.utf16.count
        DispatchQueue.main.async { [weak self] in
            self?.typeReplacement(deleteUTF16: del, insert: next)
            self?.model.lastForm = next
        }
        return nil // swallow equals
    }

    private func typeReplacement(deleteUTF16: Int, insert: String) {
        let src = CGEventSource(stateID: .hidSystemState)
        for _ in 0..<deleteUTF16 {
            if let down = CGEvent(keyboardEventSource: src, virtualKey: 0x33, keyDown: true) { // delete
                down.post(tap: .cghidEventTap)
            }
            if let up = CGEvent(keyboardEventSource: src, virtualKey: 0x33, keyDown: false) {
                up.post(tap: .cghidEventTap)
            }
        }
        // Insert unicode string
        let utf16 = Array(insert.utf16)
        var chars = utf16
        if let down = CGEvent(keyboardEventSource: src, virtualKey: 0, keyDown: true) {
            chars.withUnsafeBufferPointer { buf in
                down.keyboardSetUnicodeString(stringLength: buf.count, unicodeString: buf.baseAddress)
            }
            down.post(tap: .cghidEventTap)
        }
        if let up = CGEvent(keyboardEventSource: src, virtualKey: 0, keyDown: false) {
            up.post(tap: .cghidEventTap)
        }
    }

    private static func letter(forKeycode keycode: Int64, shift: Bool) -> String? {
        // ANSI keycodes → letter
        let map: [Int64: String] = [
            0x00: "a", 0x0B: "b", 0x08: "c", 0x02: "d", 0x0E: "e", 0x03: "f",
            0x05: "g", 0x04: "h", 0x22: "i", 0x26: "j", 0x28: "k", 0x25: "l",
            0x2E: "m", 0x2D: "n", 0x1F: "o", 0x23: "p", 0x0C: "q", 0x0F: "r",
            0x01: "s", 0x11: "t", 0x20: "u", 0x09: "v", 0x0D: "w", 0x07: "x",
            0x10: "y", 0x06: "z",
        ]
        guard let base = map[keycode] else { return nil }
        return shift ? base.uppercased() : base
    }
}

struct SettingsView: View {
    @EnvironmentObject var model: AppModel

    var body: some View {
        Form {
            Text(model.status)
            Picker("Profile", selection: $model.profile) {
                ForEach(KeySwapProfile.allCases) { p in
                    Text(p.displayName).tag(p)
                }
            }
            .onChange(of: model.profile) { _, _ in model.reloadEngine() }
            Text("Grant Accessibility under Privacy & Security, then relaunch.")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding()
        .frame(width: 360, height: 160)
    }
}
