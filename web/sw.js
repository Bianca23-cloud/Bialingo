/* Bialingo — service worker : fonctionnement hors ligne et mises à jour.
   Ne traite que les requêtes GET vers la même origine ; aucune donnée n'est envoyée nulle part. */
'use strict';
const VERSION = 'bialingo-__BUILD__';
const SHELL = [
  './', './index.html', './app.css', './app.js', './glyphs.js', './manifest.webmanifest',
  './telecharger.html', './dl.js', './confidentialite.html', './mentions-legales.html',
  './icons/icon-192.png', './icons/icon-512.png', './icons/maskable-512.png', './icons/apple-touch-icon.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith('bialingo-') && k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function putInCache(request, response) {
  if (response && response.ok && response.type === 'basic') {
    const copy = response.clone();
    caches.open(VERSION).then((c) => c.put(request, copy));
  }
  return response;
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // jamais de mise en cache de contenus tiers

  if (url.pathname.indexOf('/audio/') !== -1 && !url.pathname.endsWith('index.json')) {
    // Voix natives enregistrées : cache dédié, conservé lors des mises à jour (l'empreinte change si la phrase change).
    event.respondWith(caches.open('audio-bialingo').then((c) => c.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res && res.ok && res.type === 'basic') c.put(req, res.clone());
      return res;
    }))));
    return;
  }

  if (req.mode === 'navigate') {
    // Pages : réseau d'abord (pour recevoir les mises à jour), cache si hors ligne.
    event.respondWith(
      fetch(req).then((res) => putInCache(req, res))
        .catch(() => caches.match(req, { ignoreSearch: true }).then((hit) => hit || caches.match('./index.html')))
    );
    return;
  }
  // Fichiers statiques : cache d'abord, puis réseau.
  event.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => putInCache(req, res))));
});
