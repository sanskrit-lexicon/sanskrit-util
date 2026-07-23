// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "KeySwapCore",
    platforms: [
        .iOS(.v16),
        .macOS(.v13),
    ],
    products: [
        .library(name: "KeySwapCore", targets: ["KeySwapCore"]),
    ],
    targets: [
        .target(
            name: "KeySwapCore",
            path: "Sources/KeySwapCore"
        ),
        .testTarget(
            name: "KeySwapCoreTests",
            dependencies: ["KeySwapCore"],
            path: "Tests/KeySwapCoreTests",
            resources: [
                .copy("Fixtures"),
            ]
        ),
    ]
)
