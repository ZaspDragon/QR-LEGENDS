
// QR Legends Service Worker
const CACHE_NAME = 'qr-legends-cache-v1';
const urlsToCache = [
  '/',
  '/static/main_dashboard.html',
  '/static/company_login.html',
  '/static/qr_legends_logo.png'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
