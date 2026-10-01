/**
 * SNEAKERS SQUAD - OFFICIAL PWA SERVICE WORKER (sw.js)
 * Caches core app assets, delivers lightning-fast loading,
 * and provides offline fallback experience.
 */

const CACHE_NAME = 'sneaker-squad-pwa-v1.0';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/men.html',
  '/women.html',
  '/accessories.html',
  '/contact.html',
  '/static/css/style.css',
  '/static/css/product.css',
  '/static/css/auth.css',
  '/static/css/dashboard.css',
  '/static/js/products-data.js',
  '/static/js/script.js',
  '/static/js/cart.js',
  '/static/js/auth-drawer.js',
  '/static/img/pwa-icon-192.png',
  '/static/img/pwa-icon-512.png',
  '/static/manifest.json'
];

// Install Event: Cache Core Static Shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SneakerSquad PWA] Pre-caching static app shell');
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[SneakerSquad PWA] Partial cache error (ignoring non-critical):', err);
      });
    }).then(() => self.skipWaiting())
  );
});

// Activate Event: Clean Old Caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(
        keyList.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[SneakerSquad PWA] Removing outdated cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event: Network First for Dynamic/API, Stale-While-Revalidate for Static Assets
self.addEventListener('fetch', (event) => {
  const requestUrl = new URL(event.request.url);

  // Skip non-GET requests or admin / backend API endpoints to keep them always live
  if (
    event.request.method !== 'GET' ||
    requestUrl.pathname.startsWith('/admin') ||
    requestUrl.pathname.startsWith('/api') ||
    requestUrl.pathname.startsWith('/accounts/api') ||
    requestUrl.pathname.startsWith('/order')
  ) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // Fetch from network in background or when not cached
      const fetchPromise = fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          // If network fails and no cache exists, return offline fallback HTML if requesting a page
          if (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html')) {
            return caches.match('/index.html') || new Response(
              `<!DOCTYPE html>
              <html>
              <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Offline | SNEAKERS SQUAD</title>
                <style>
                  body { background: #0b0d13; color: #fff; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; padding: 20px; }
                  .box { background: #141722; border: 1px solid #ff5a1f; padding: 36px 24px; border-radius: 20px; max-width: 400px; }
                  h2 { color: #ff5a1f; margin-bottom: 8px; }
                  p { color: #94a3b8; font-size: 0.95rem; }
                  button { background: #ff5a1f; color: #fff; border: none; padding: 12px 24px; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 16px; }
                </style>
              </head>
              <body>
                <div class="box">
                  <h2>👟 SNEAKERS SQUAD</h2>
                  <h3>You're Currently Offline</h3>
                  <p>Check your internet connection or mobile data to browse the latest authentic sneaker drops.</p>
                  <button onclick="window.location.reload()">Retry Connection</button>
                </div>
              </body>
              </html>`,
              { headers: { 'Content-Type': 'text/html' } }
            );
          }
        });

      return cachedResponse || fetchPromise;
    })
  );
});
