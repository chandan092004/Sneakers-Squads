/**
 * SNEAKERS SQUAD - OFFICIAL PWA SERVICE WORKER (sw.js)
 * Caches core app assets, delivers lightning-fast loading,
 * and preserves live dynamic user authentication state on mobile.
 */

const CACHE_NAME = 'sneaker-squad-pwa-v4.0';
const STATIC_ASSETS = [
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

// Install Event: Cache Core Static Assets Only (Never dynamic pages)
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SneakerSquad PWA] Pre-caching static assets');
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[SneakerSquad PWA] Partial cache error (ignoring non-critical):', err);
      });
    })
  );
});

// Activate Event: Clean Old Caches immediately to ensure fresh session state
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

// Fetch Event: Network-first with dynamic bypass for auth and pages
self.addEventListener('fetch', (event) => {
  const requestUrl = new URL(event.request.url);

  // Skip non-GET requests, all auth/account endpoints, admin, API, and dashboard
  // to ensure authentication cookies and tokens are ALWAYS live and never cached
  if (
    event.request.method !== 'GET' ||
    requestUrl.pathname.startsWith('/admin') ||
    requestUrl.pathname.startsWith('/api') ||
    requestUrl.pathname.startsWith('/accounts') ||
    requestUrl.pathname.startsWith('/dashboard') ||
    requestUrl.pathname.startsWith('/order')
  ) {
    return;
  }

  const isNavigation = event.request.mode === 'navigate' || 
                       (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html'));

  // Navigation requests (HTML pages): Always Network First, NEVER cache user-specific pages
  if (isNavigation) {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          return new Response(
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
        })
    );
    return;
  }

  // Static Assets: Network first with Cache fallback
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && requestUrl.pathname.startsWith('/static/')) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        return caches.match(event.request);
      })
  );
});
