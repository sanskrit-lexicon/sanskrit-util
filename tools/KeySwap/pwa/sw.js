/* Minimal offline cache for KeySwap 2.0 PWA */
const CACHE = "keyswap-2.1.0";
const ASSETS = ["./", "./index.html", "./keyswap-pwa.js", "./manifest.webmanifest"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request).catch(() => caches.match("./index.html")))
  );
});
