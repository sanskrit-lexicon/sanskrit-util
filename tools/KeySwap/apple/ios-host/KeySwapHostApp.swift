import SwiftUI
import KeySwapCore

/// KeySwap 2.0 host app — required to install the keyboard extension on iPhone/iPad.
@main
struct KeySwapHostApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @AppStorage("profile", store: UserDefaults(suiteName: "group.keyswap"))
    private var profile: String = "iast-classic"

    var body: some View {
        NavigationStack {
            List {
                Section("KeySwap \(KeySwapVersion.current)") {
                    Text("Type IAST with cycle (=), smart double-letters (aa→ā), and long-press alternates.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                Section("Enable the keyboard") {
                    Text("Settings → General → Keyboard → Keyboards → Add New Keyboard… → KeySwap")
                    Text("Full Access is not required for v2.0 core typing.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
                Section("How to type") {
                    Label("Letter then = cycle (ṇ → ṅ → ñ)", systemImage: "arrow.triangle.2.circlepath")
                    Label("Long-press a key for the full chain", systemImage: "hand.tap")
                    Label("Smart: aa ii uu rr → ā ī ū ṛ (toggle smart✓)", systemImage: "textformat.abc")
                }
                Section("Profile") {
                    Picker("Config profile", selection: $profile) {
                        ForEach(KeySwapProfile.allCases) { p in
                            Text(p.displayName).tag(p.rawValue)
                        }
                    }
                    Text("Bundle the matching configs/*.txt into the keyboard target. Restart the keyboard after changing profile.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
                Section("Desktop / web") {
                    Text("Windows AHK, Mac menu bar, and offline PWA share the same configs — see tools/KeySwap/README.md")
                        .font(.footnote)
                }
            }
            .navigationTitle("KeySwap 2.0")
        }
    }
}
