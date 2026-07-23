import XCTest
@testable import KeySwapCore

final class CycleEngineTests: XCTestCase {
    func testNextFormWrap() throws {
        let eng = try CycleEngine.parse(text: "n > ṇ > ṅ > ñ\na > ā\n")
        XCTAssertEqual(eng.nextForm(of: "n"), "ṇ")
        XCTAssertEqual(eng.nextForm(of: "ñ"), "n")
        XCTAssertEqual(eng.nextForm(of: "a"), "ā")
        XCTAssertEqual(eng.nextForm(of: "ā"), "a")
    }

    func testApplyTrigger() throws {
        let eng = try CycleEngine.parse(text: "a > ā\nn > ṇ > ṅ\n")
        let (t1, c1) = eng.applyTrigger(to: "rama")
        XCTAssertTrue(c1)
        XCTAssertEqual(t1, "ramā")
        let (t2, c2) = eng.applyTrigger(to: "gaṇ")
        XCTAssertTrue(c2)
        XCTAssertEqual(t2, "gaṅ")
    }

    func testDuplicateBaseThrows() {
        XCTAssertThrowsError(try CycleEngine.parse(text: "a > ā\na > á\n"))
    }

    func testUnknownNoChange() throws {
        let eng = try CycleEngine.parse(text: "a > ā\n")
        let (t, c) = eng.applyTrigger(to: "xyz")
        XCTAssertFalse(c)
        XCTAssertEqual(t, "xyz")
    }

    func testSmartDigraphs() {
        let (t, ok) = SmartTables.default.apply(to: "ramaa")
        XCTAssertTrue(ok)
        XCTAssertTrue(t.hasSuffix("ā"))
        let (t2, ok2) = SmartTables.default.apply(to: "ash")
        XCTAssertTrue(ok2)
        XCTAssertTrue(t2.hasSuffix("ś"))
    }

    func testLongPressMenu() throws {
        let eng = try CycleEngine.parse(text: "n > ṇ > ṅ > ñ\n")
        XCTAssertEqual(eng.longPressMenu(for: "n"), ["n", "ṇ", "ṅ", "ñ"])
    }

    func testVersion() {
        XCTAssertEqual(KeySwapVersion.current, "2.3.0")
    }
}
