/**
 * PathFinder — Service Worker pour mode hors-ligne
 * Cache les pages visitées et ressources statiques pour consultation offline
 */

const CACHE_NAME = 'pathfinder-v1';
const OFFLINE_URL = '/offline/';

// Ressources à pré-cacher au premier chargement
const PRECACHE_URLS = [
    '/',
    '/offline/',
    '/static/css/shared.css',
    '/static/js/shared.js',
    '/static/manifest.json',
];

// Installation : pré-cacher les ressources essentielles
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(PRECACHE_URLS);
        }).then(() => self.skipWaiting())
    );
});

// Activation : nettoyer les anciens caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
            );
        }).then(() => self.clients.claim())
    );
});

// Stratégie : Network-first avec fallback cache
self.addEventListener('fetch', event => {
    // Ignorer les requêtes non-GET
    if (event.request.method !== 'GET') return;

    // Ignorer les requêtes admin et API
    const url = new URL(event.request.url);
    if (url.pathname.startsWith('/admin/')) return;

    // Pour les ressources statiques : Cache-first
    if (url.pathname.startsWith('/static/') || url.pathname.startsWith('/media/')) {
        event.respondWith(
            caches.match(event.request).then(cached => {
                if (cached) return cached;
                return fetch(event.request).then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    }
                    return response;
                });
            })
        );
        return;
    }

    // Pour les pages HTML : Network-first avec cache fallback
    if (event.request.headers.get('accept')?.includes('text/html')) {
        event.respondWith(
            fetch(event.request).then(response => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                }
                return response;
            }).catch(() => {
                return caches.match(event.request).then(cached => {
                    return cached || caches.match(OFFLINE_URL);
                });
            })
        );
        return;
    }

    // Autres requêtes : Network avec cache fallback
    event.respondWith(
        fetch(event.request).then(response => {
            if (response.ok) {
                const clone = response.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
            }
            return response;
        }).catch(() => caches.match(event.request))
    );
});
