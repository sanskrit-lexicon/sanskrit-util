import UIKit
import KeySwapCore

/// Custom keyboard: QWERTY-ish Latin row + dedicated cycle key (=).
/// Enable in Settings → General → Keyboard → Keyboards → Add New Keyboard → KeySwap.
open class KeyboardViewController: UIInputViewController {
    private var engine: CycleEngine = {
        // Fallback minimal chain if bundle resource missing
        (try? CycleEngine.parse(text: """
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
        """))!
    }()

    private var shiftOn = false
    private let rows: [[String]] = [
        ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
        ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
        ["⇧", "z", "x", "c", "v", "b", "n", "m", "⌫"],
        ["123", "🌐", "space", "=", "return"],
    ]

    private var stack: UIStackView!

    public override func viewDidLoad() {
        super.viewDidLoad()
        loadPreferredProfile()
        buildKeyboard()
    }

    private func loadPreferredProfile() {
        let name = UserDefaults(suiteName: "group.keyswap")?.string(forKey: "profile")
            ?? KeySwapProfile.iastClassic.rawValue
        if let url = Bundle.main.url(forResource: name, withExtension: "txt"),
           let eng = try? CycleEngine.load(url: url) {
            engine = eng
        }
    }

    private func buildKeyboard() {
        view.backgroundColor = UIColor.secondarySystemBackground
        stack = UIStackView()
        stack.axis = .vertical
        stack.spacing = 6
        stack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 4),
            stack.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -4),
            stack.topAnchor.constraint(equalTo: view.topAnchor, constant: 6),
            stack.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -6),
        ])
        rebuildRows()
    }

    private func rebuildRows() {
        stack.arrangedSubviews.forEach { $0.removeFromSuperview() }
        for row in rows {
            let rowStack = UIStackView()
            rowStack.axis = .horizontal
            rowStack.spacing = 4
            rowStack.distribution = .fillEqually
            for key in row {
                rowStack.addArrangedSubview(makeKey(key))
            }
            stack.addArrangedSubview(rowStack)
        }
    }

    private func makeKey(_ label: String) -> UIButton {
        let b = UIButton(type: .system)
        var title = label
        if label.count == 1, label != "⇧", label != "=", label != "⌫" {
            title = shiftOn ? label.uppercased() : label
        }
        if label == "=" {
            title = "= cycle"
        }
        b.setTitle(title, for: .normal)
        b.titleLabel?.font = .systemFont(ofSize: label == "space" || label == "= cycle" || label == "=" ? 14 : 18, weight: .medium)
        b.backgroundColor = keyColor(label)
        b.setTitleColor(.label, for: .normal)
        b.layer.cornerRadius = 6
        b.heightAnchor.constraint(greaterThanOrEqualToConstant: 42).isActive = true
        b.addAction(UIAction { [weak self] _ in self?.handle(label) }, for: .touchUpInside)
        return b
    }

    private func keyColor(_ label: String) -> UIColor {
        switch label {
        case "=", "return", "⇧", "123", "🌐", "⌫":
            return UIColor.tertiarySystemBackground
        case "space":
            return UIColor.systemBackground
        default:
            return UIColor.systemBackground
        }
    }

    private func handle(_ label: String) {
        let proxy = textDocumentProxy
        switch label {
        case "⌫":
            proxy.deleteBackward()
        case "return":
            proxy.insertText("\n")
        case "space":
            proxy.insertText(" ")
        case "⇧":
            shiftOn.toggle()
            rebuildRows()
        case "🌐":
            advanceToNextInputMode()
        case "123":
            // Numbers not expanded in v1 — insert digits row later
            break
        case "=", "= cycle":
            applyCycle()
        default:
            let ch = shiftOn ? label.uppercased() : label
            proxy.insertText(ch)
            if shiftOn { shiftOn = false; rebuildRows() }
        }
    }

    /// Cycle the last form before the caret using document context.
    private func applyCycle() {
        let proxy = textDocumentProxy
        let before = proxy.documentContextBeforeInput ?? ""
        let (newBefore, changed) = engine.applyTrigger(to: before)
        guard changed else {
            // No known form — insert literal =
            proxy.insertText("=")
            return
        }
        // Delete the suffix that changed, insert new form
        let oldSuffixLen = before.precomposedStringWithCanonicalMapping.count
        let newN = newBefore.count
        // Safer: compute deleted suffix length from common prefix
        let oldNFC = before.precomposedStringWithCanonicalMapping
        let newNFC = newBefore
        var common = 0
        let oldChars = Array(oldNFC)
        let newChars = Array(newNFC)
        while common < oldChars.count, common < newChars.count, oldChars[common] == newChars[common] {
            common += 1
        }
        let deleteCount = oldChars.count - common
        for _ in 0..<deleteCount {
            proxy.deleteBackward()
        }
        let insert = String(newChars.suffix(newChars.count - common))
        proxy.insertText(insert)
        _ = oldSuffixLen
        _ = newN
    }
}
