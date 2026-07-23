import SwiftUI

/// Minimal host app required to install the KeySwap keyboard extension on iPhone/iPad.
@main
struct KeySwapHostApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    var body: some View {
        NavigationStack {
            List {
                Section("Enable the keyboard") {
                    Text("Settings → General → Keyboard → Keyboards → Add New Keyboard… → KeySwap")
                    Text("Optional: allow Full Access only if a future version needs it (current build does not).")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
                Section("How to type") {
                    Text("1. Switch to the KeySwap keyboard (🌐).")
                    Text("2. Type a Latin letter (e.g. n).")
                    Text("3. Tap “= cycle” to walk ṇ → ṅ → ñ → n.")
                    Text("4. Use ⇧ for uppercase chains (Ṇ Ṅ Ñ).")
                }
                Section("Profiles") {
                    Text("Profiles ship as configs/iast-classic, iso15919, vedic-draft. Bundle them into the keyboard target and pick via App Group defaults (group.keyswap / profile).")
                        .font(.footnote)
                }
            }
            .navigationTitle("KeySwap")
        }
    }
}
