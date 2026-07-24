import Foundation

/// Shared KeySwap cycle semantics (parity with ``tools/KeySwap/cycle_engine.py``).
public struct CycleEngine: Sendable {
    public let chains: [[String]]

    private let byForm: [String: (chain: Int, index: Int)]
    private let maxFormUTF16: Int

    public enum ConfigError: Error, CustomStringConvertible, Sendable {
        case empty
        case emptyForm(line: Int)
        case shortChain(line: Int)
        case duplicateBase(String, line: Int, firstLine: Int)

        public var description: String {
            switch self {
            case .empty: return "no chains found"
            case .emptyForm(let line): return "line \(line): empty form"
            case .shortChain(let line): return "line \(line): need base + ≥1 form"
            case .duplicateBase(let b, let line, let first):
                return "line \(line): duplicate base \(b) (first at \(first))"
            }
        }
    }

    public init(chains: [[String]]) throws {
        guard !chains.isEmpty else { throw ConfigError.empty }
        let normalized = chains.map { $0.map { $0.precomposedStringWithCanonicalMapping } }
        self.chains = normalized
        var map: [String: (Int, Int)] = [:]
        var maxLen = 1
        for (ci, chain) in normalized.enumerated() {
            for (fi, form) in chain.enumerated() {
                if map[form] == nil {
                    map[form] = (ci, fi)
                }
                maxLen = max(maxLen, form.utf16.count)
            }
        }
        self.byForm = map
        self.maxFormUTF16 = maxLen
    }

    public static func parse(text: String) throws -> CycleEngine {
        var chains: [[String]] = []
        var seenBases: [String: Int] = [:]
        for (idx, rawLine) in text.split(separator: "\n", omittingEmptySubsequences: false).enumerated() {
            let lineno = idx + 1
            var line = rawLine.trimmingCharacters(in: .whitespacesAndNewlines)
            if line.isEmpty || line.hasPrefix("#") { continue }
            if let r = line.range(of: " #") {
                line = String(line[..<r.lowerBound]).trimmingCharacters(in: .whitespaces)
            }
            let parts = line.split(separator: ">", omittingEmptySubsequences: false)
                .map { $0.trimmingCharacters(in: .whitespaces) }
            if parts.contains(where: \.isEmpty) {
                throw ConfigError.emptyForm(line: lineno)
            }
            guard parts.count >= 2 else { throw ConfigError.shortChain(line: lineno) }
            let forms = parts.map { $0.precomposedStringWithCanonicalMapping }
            let base = forms[0]
            if let first = seenBases[base] {
                throw ConfigError.duplicateBase(base, line: lineno, firstLine: first)
            }
            seenBases[base] = lineno
            chains.append(forms)
        }
        return try CycleEngine(chains: chains)
    }

    public static func load(url: URL) throws -> CycleEngine {
        let data = try Data(contentsOf: url)
        // Strip UTF-8 BOM if present
        var bytes = [UInt8](data)
        if bytes.starts(with: [0xEF, 0xBB, 0xBF]) {
            bytes.removeFirst(3)
        }
        let text = String(decoding: bytes, as: UTF8.self)
        return try parse(text: text)
    }

    public func nextForm(of current: String) -> String? {
        let cur = current.precomposedStringWithCanonicalMapping
        guard let hit = byForm[cur] else { return nil }
        let chain = chains[hit.chain]
        return chain[(hit.index + 1) % chain.count]
    }

    /// Replace the longest known form that is a suffix of ``textBeforeCaret``.
    public func applyTrigger(to textBeforeCaret: String) -> (text: String, changed: Bool) {
        let t = textBeforeCaret.precomposedStringWithCanonicalMapping
        guard let hit = findSuffixHit(in: t) else { return (t, false) }
        let chain = chains[hit.chain]
        let next = chain[(hit.formIndex + 1) % chain.count]
        let start = t.index(t.startIndex, offsetBy: hit.startScalarOffset)
        let newText = String(t[..<start]) + next
        return (newText, newText != t)
    }

    private struct Hit {
        let startScalarOffset: Int
        let chain: Int
        let formIndex: Int
    }

    private func findSuffixHit(in text: String) -> Hit? {
        let scalars = Array(text.unicodeScalars)
        let n = scalars.count
        guard n > 0 else { return nil }
        let maxLen = min(n, maxFormUTF16 + 4) // combining marks may add scalars
        for length in stride(from: maxLen, through: 1, by: -1) {
            let suffixScalars = scalars.suffix(length)
            let suffix = String(String.UnicodeScalarView(suffixScalars))
                .precomposedStringWithCanonicalMapping
            if let hit = byForm[suffix] {
                return Hit(startScalarOffset: n - length, chain: hit.chain, formIndex: hit.index)
            }
        }
        return nil
    }
}

/// Bundled profile names used by the Apple apps.
public enum KeySwapProfile: String, CaseIterable, Sendable, Identifiable {
    case iastClassic = "iast-classic"
    case writerScheme = "writer-scheme"
    case iso15919 = "iso15919"
    case vedicDraft = "vedic-draft"
    case vedicSvara = "vedic-svara"
    case personalLegacy = "personal-legacy"

    public var id: String { rawValue }

    public var displayName: String {
        switch self {
        case .iastClassic: return "IAST classic"
        case .writerScheme: return "Writer-scheme (SW-style)"
        case .iso15919: return "ISO 15919"
        case .vedicDraft: return "Vedic draft"
        case .vedicSvara: return "Vedic svara"
        case .personalLegacy: return "Personal legacy"
        }
    }
}
