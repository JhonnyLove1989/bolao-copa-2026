var GHPATH = '/bolao-copa-2026';
var APP_PREFIX = 'bolao_';
var VERSION = 'version_01';

var URLS = [
  `${GHPATH}/`,
  `${GHPATH}/index.html`,
  `${GHPATH}/games.json`,
  `${GHPATH}/groups.json`,
  `${GHPATH}/ranking.json`,
  `${GHPATH}/palpites.json`,
  `${GHPATH}/palpites_mm.json`,
  `${GHPATH}/claro.png`,
  `${GHPATH}/fifa.png`
];

self.addEventListener('install', function(e){
  e.waitUntil(
    caches.open(APP_PREFIX + VERSION).then(function(cache){
      return cache.addAll(URLS);
    })
  );
});

self.addEventListener('activate', function(e){
  e.waitUntil(
    caches.keys().then(function(keyList){
      return Promise.all(keyList.map(function(key){
        if(key !== APP_PREFIX + VERSION){
          return caches.delete(key);
        }
      }));
    })
  );
});

self.addEventListener('fetch', function(e){
  e.respondWith(
    caches.match(e.request).then(function(request){
      return request || fetch(e.request);
    })
  );
});