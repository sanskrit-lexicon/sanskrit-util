import Foundation

/// KeySwap smart digraph expansion (parity with ``smart_input.py``).
public struct SmartTables: Sendable {
    public let pairs: [(String, String)]

    public static let `default`: SmartTables = {
        SmartTables(pairs: classicPairs.sorted { $0.0.count > $1.0.count })
    }()

    /// Sanskrit Writer–style top→bottom digraphs + classic doubles.
    public static let writer: SmartTables = {
        var seen = Set<String>()
        var raw: [(String, String)] = []
        for p in writerPairs + classicPairs {
            if seen.contains(p.0) { continue }
            seen.insert(p.0)
            raw.append(p)
        }
        return SmartTables(pairs: raw.sorted { $0.0.count > $1.0.count })
    }()

    private static let classicPairs: [(String, String)] = [
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

    private static let writerPairs: [(String, String)] = [
        ("-a", "ā"), ("-i", "ī"), ("-u", "ū"), ("-A", "Ā"), ("-I", "Ī"), ("-U", "Ū"),
        ("~n", "ñ"), ("~N", "Ñ"), ("~m", "ṃ"), ("~M", "Ṃ"),
        ("'s", "ś"), ("'S", "Ś"),
        ("h.", "ḥ"), ("H.", "Ḥ"), ("r.", "ṛ"), ("R.", "Ṛ"),
        ("l.", "ḷ"), ("L.", "Ḷ"), ("m.", "ṃ"), ("M.", "Ṃ"),
        ("n.", "ṇ"), ("N.", "Ṇ"), ("t.", "ṭ"), ("T.", "Ṭ"),
        ("d.", "ḍ"), ("D.", "Ḍ"), ("s.", "ṣ"), ("S.", "Ṣ"),
        (".h", "ḥ"), (".H", "Ḥ"), (".r", "ṛ"), (".R", "Ṛ"),
        (".l", "ḷ"), (".L", "Ḷ"), (".m", "ṃ"), (".M", "Ṃ"),
        (".n", "ṇ"), (".N", "Ṇ"), (".t", "ṭ"), (".T", "Ṭ"),
        (".d", "ḍ"), (".D", "Ḍ"), (".s", "ṣ"), (".S", "Ṣ"),
    ]

    public init(pairs: [(String, String)]) {
        self.pairs = pairs
    }

    public static func forProfile(_ name: String) -> SmartTables {
        name.lowercased().contains("writer") ? .writer : .default
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
    public static let current = "2.6.0"
}
