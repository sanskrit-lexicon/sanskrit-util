import Foundation

/// KeySwap 2.0 smart double-letter / digraph expansion (parity with ``smart_input.py``).
public struct SmartTables: Sendable {
    public let pairs: [(String, String)]

    public static let `default`: SmartTables = {
        let raw: [(String, String)] = [
            ("aa", "ā"), ("ii", "ī"), ("uu", "ū"), ("rr", "ṛ"), ("ll", "ḷ"),
            ("mm", "ṃ"), ("hh", "ḥ"), ("AA", "Ā"), ("II", "Ī"), ("UU", "Ū"),
            ("RR", "Ṛ"), ("LL", "Ḷ"), ("MM", "Ṃ"), ("HH", "Ḥ"),
            ("sh", "ś"), ("Sh", "Ś"), ("SH", "Ś"),
            ("ss", "ṣ"), ("Ss", "Ṣ"), ("SS", "Ṣ"),
            ("ng", "ṅ"), ("Ng", "Ṅ"), ("NG", "Ṅ"),
            ("ny", "ñ"), ("Ny", "Ñ"), ("NY", "Ñ"),
            ("nn", "ṇ"), ("Nn", "Ṇ"), ("NN", "Ṇ"),
            ("tt", "ṭ"), ("Tt", "Ṭ"), ("TT", "Ṭ"),
            ("dd", "ḍ"), ("Dd", "Ḍ"), ("DD", "Ḍ"),
        ]
        let sorted = raw.sorted { $0.0.count > $1.0.count }
        return SmartTables(pairs: sorted)
    }()

    public init(pairs: [(String, String)]) {
        self.pairs = pairs
    }

    public func apply(to textBeforeCaret: String) -> (text: String, changed: Bool) {
        let t = textBeforeCaret.precomposedStringWithCanonicalMapping
        for (src, dst) in pairs {
            if t.hasSuffix(src) {
                let prefix = String(t.dropLast(src.count))
                return (prefix + dst.precomposedStringWithCanonicalMapping, true)
            }
        }
        return (t, false)
    }
}

public extension CycleEngine {
    /// Forms for long-press menu (base first).
    func longPressMenu(for base: String) -> [String] {
        let b = base.precomposedStringWithCanonicalMapping
        for chain in chains where chain.first == b {
            return chain
        }
        return [b]
    }
}

public enum KeySwapVersion {
    public static let current = "2.2.0"
}
