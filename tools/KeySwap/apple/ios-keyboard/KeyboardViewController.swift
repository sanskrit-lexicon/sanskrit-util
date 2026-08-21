import UIKit
import KeySwapCore

/// KeySwap 2.0 custom keyboard: cycle, smart vowels, long-press menus.
/// Settings → General → Keyboard → Keyboards → Add → KeySwap.
open class KeyboardViewController: UIInputViewController {
    private var engine: CycleEngine = {
        (try? CycleEngine.parse(text: Self.embeddedClassic))!
    }()

    private var smart = SmartTables.default
    private var shiftOn = false
    private var smartOn = false
    private var longPressBase: String?
    private var longPressTimer: Timer?
    private var menuView: UIStackView?

    private let rows: [[String]] = [
        ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
        ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
        ["⇧", "z", "x", "c", "v", "b", "n", "m", "⌫"],
        ["smart", "🌐", "space", "=", "return"],
    ]

    private var stack: UIStackView!

    private static let embeddedClassic = """
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

    public override func viewDidLoad() {
        super.viewDidLoad()
        loadPreferredProfile()
        buildKeyboard()
    }

    private func loadPreferredProfile() {
        let name = UserDefaults(suiteName: "group.keyswap")?.string(forKey: "profile")
            ?? KeySwapProfile.iastClassic.rawValue
        // Digraph substitution must match the cycle profile below, or Writer users get classic "aa"→ā instead of "-a"→ā.
        smart = SmartTables.forProfile(name)
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
        if label.count == 1, label != "=" {
            title = shiftOn ? label.uppercased() : label
        }
        switch label {
        case "=": title = "= ⟳"
        case "smart": title = smartOn ? "smart✓" : "smart"
        case "space": title = "space"
        default: break
        }
        b.setTitle(title, for: .normal)
        b.titleLabel?.font = .systemFont(ofSize: 16, weight: .medium)
        b.backgroundColor = keyColor(label)
        b.setTitleColor(.label, for: .normal)
        b.layer.cornerRadius = 6
        b.heightAnchor.constraint(greaterThanOrEqualToConstant: 42).isActive = true

        if label.count == 1, label != "=" {
            let long = UILongPressGestureRecognizer(target: self, action: #selector(longPressKey(_:)))
            long.minimumPressDuration = 0.35
            b.addGestureRecognizer(long)
            b.accessibilityIdentifier = shiftOn ? label.uppercased() : label
        }

        b.addAction(UIAction { [weak self] _ in self?.handle(label) }, for: .touchUpInside)
        return b
    }

    private func keyColor(_ label: String) -> UIColor {
        switch label {
        case "=", "return", "⇧", "smart", "🌐", "⌫":
            return UIColor.tertiarySystemBackground
        case "space":
            return UIColor.systemBackground
        default:
            return UIColor.systemBackground
        }
    }

    @objc private func longPressKey(_ gr: UILongPressGestureRecognizer) {
        guard gr.state == .began,
              let b = gr.view as? UIButton,
              let id = b.accessibilityIdentifier else { return }
        let base = id
        let forms = engine.longPressMenu(for: base)
        showMenu(forms: forms, from: b)
    }

    private func showMenu(forms: [String], from anchor: UIView) {
        menuView?.removeFromSuperview()
        let box = UIStackView()
        box.axis = .horizontal
        box.spacing = 4
        box.backgroundColor = UIColor.secondarySystemBackground
        box.layer.cornerRadius = 8
        box.layoutMargins = UIEdgeInsets(top: 4, left: 4, bottom: 4, right: 4)
        box.isLayoutMarginsRelativeArrangement = true
        for f in forms {
            let btn = UIButton(type: .system)
            btn.setTitle(f, for: .normal)
            btn.titleLabel?.font = .systemFont(ofSize: 20, weight: .semibold)
            btn.contentEdgeInsets = UIEdgeInsets(top: 8, left: 10, bottom: 8, right: 10)
            btn.backgroundColor = .systemBackground
            btn.layer.cornerRadius = 6
            btn.addAction(UIAction { [weak self] _ in
                self?.textDocumentProxy.insertText(f)
                self?.menuView?.removeFromSuperview()
                self?.menuView = nil
            }, for: .touchUpInside)
            box.addArrangedSubview(btn)
        }
        box.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(box)
        NSLayoutConstraint.activate([
            box.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            box.bottomAnchor.constraint(equalTo: stack.topAnchor, constant: -4),
        ])
        menuView = box
    }

    private func handle(_ label: String) {
        menuView?.removeFromSuperview()
        menuView = nil
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
        case "smart":
            smartOn.toggle()
            rebuildRows()
        case "=":
            applyCycle()
        default:
            let ch = shiftOn ? label.uppercased() : label
            proxy.insertText(ch)
            if smartOn { applySmart() }
            if shiftOn { shiftOn = false; rebuildRows() }
        }
    }

    private func applySmart() {
        let proxy = textDocumentProxy
        let before = proxy.documentContextBeforeInput ?? ""
        let (newBefore, changed) = smart.apply(to: before)
        guard changed else { return }
        replaceSuffix(old: before, new: newBefore)
    }

    private func applyCycle() {
        let proxy = textDocumentProxy
        let before = proxy.documentContextBeforeInput ?? ""
        let (newBefore, changed) = engine.applyTrigger(to: before)
        guard changed else {
            proxy.insertText("=")
            return
        }
        replaceSuffix(old: before, new: newBefore)
    }

    private func replaceSuffix(old: String, new: String) {
        let proxy = textDocumentProxy
        let oldNFC = old.precomposedStringWithCanonicalMapping
        let newNFC = new.precomposedStringWithCanonicalMapping
        let oldChars = Array(oldNFC)
        let newChars = Array(newNFC)
        var common = 0
        while common < oldChars.count, common < newChars.count, oldChars[common] == newChars[common] {
            common += 1
        }
        for _ in 0..<(oldChars.count - common) {
            proxy.deleteBackward()
        }
        proxy.insertText(String(newChars.suffix(newChars.count - common)))
    }
}
