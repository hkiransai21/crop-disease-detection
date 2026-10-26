/* Explicit opt-in audio downloads. Never runtime-cache a playback response. */
const LANGUAGES = ['en', 'hi', 'ta', 'te', 'kn'];
const PREFIX = 'agrishield-audio-v2-';
importScripts('/precache.js');
const APP_CACHE = 'leaf-app-' + self.APP_VERSION;
const FONT_CACHE = 'leaf-fonts-v2';
self.addEventListener('install', event => event.waitUntil((async () => {
 const cache=await caches.open(APP_CACHE);
 await cache.addAll(self.APP_FILES);
 await self.skipWaiting();
})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 for(const key of await caches.keys()) if(key.startsWith('leaf-app-') && key!==APP_CACHE) await caches.delete(key);
 await self.clients.claim();
})()));
self.addEventListener('fetch', event=>{
 const url=new URL(event.request.url);
 if(url.pathname.startsWith('/api/') && !url.pathname.startsWith('/api/v1/audio/'))return;
 if(url.origin!==self.location.origin || event.request.method!=='GET')return;
 if(url.pathname.startsWith('/fonts/') && url.pathname.endsWith('.woff2')) {
  event.respondWith((async()=>{const cache=await caches.open(FONT_CACHE);const hit=await cache.match(event.request);if(hit)return hit;const response=await fetch(event.request);if(response.ok)await cache.put(event.request,response.clone());return response;})());return;
 }
 if(event.request.mode==='navigate') {
  event.respondWith((async()=>{try{return await fetch(event.request);}catch{const cache=await caches.open(APP_CACHE);return (await cache.match('/index.html')) || Response.error();}})());return;
 }
 if(self.APP_FILES.includes(url.pathname))event.respondWith(caches.open(APP_CACHE).then(async cache=>(await cache.match(url.pathname)) || fetch(event.request)));
 if(url.pathname.startsWith('/voice/'))event.respondWith(caches.match(url.pathname).then(hit=>hit || fetch(event.request)));
});
self.addEventListener('message', event => {
  if (event.data?.type !== 'DOWNLOAD_AUDIO' || !LANGUAGES.includes(event.data.lang)) return;
  event.waitUntil((async () => {
    const lang = event.data.lang;
    const name = PREFIX + lang + '-' + Date.now();
    try {
      const manifest = await fetch(`/api/v1/audio/manifest/${lang}`, { cache: 'no-store' });
      if (!manifest.ok) throw new Error('Manifest unavailable');
      const { files } = await manifest.json();
      const cache = await caches.open(name);
      for (const url of files) {
        if (!url.startsWith(`/api/v1/audio/files/${lang}/`) || !url.endsWith('.mp3') || url.includes('..')) throw new Error('Invalid audio manifest');
        const response = await fetch(url, { cache: 'no-store' });
        if (!response.ok || !response.headers.get('content-type')?.startsWith('audio/mpeg')) throw new Error(`Audio unavailable: ${url}`);
        const bytes = await response.arrayBuffer();
        if (bytes.byteLength <= 5120) throw new Error(`Invalid audio: ${url}`);
        await cache.put(url, new Response(bytes, { headers: { 'Content-Type': 'audio/mpeg' } }));
      }
      for (const suffix of ['', '-low', '-medium', '-high']) {
        const promptUrl=suffix ? `/voice/risk-${lang}${suffix}.mp3` : `/voice/${lang}.mp3`;
        const prompt=await fetch(promptUrl);
        if(!prompt.ok || !prompt.headers.get('content-type')?.startsWith('audio/')) throw new Error('Prompt unavailable');
        await cache.put(promptUrl,prompt);
      }
      const catalogUrl = `/api/v1/audio/catalog/${lang}`;
      const catalog = await fetch(catalogUrl, { cache: 'no-store' });
      if (!catalog.ok) throw new Error('Narration text unavailable');
      await cache.put(catalogUrl, catalog);
      // Keep the last complete download if a refresh fails midway.
      for (const key of await caches.keys()) if (key.startsWith(PREFIX + lang + '-') && key !== name) await caches.delete(key);
      event.ports[0]?.postMessage({ ok: true });
    } catch (error) {
      await caches.delete(name);
      event.ports[0]?.postMessage({ ok: false, error: String(error) });
    }
  })());
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin || event.request.method !== 'GET' || !/^\/api\/v1\/audio\/(files|catalog)\//.test(url.pathname)) return;
  event.respondWith((async () => {
    const cached = await caches.match(url.pathname);
    if (!cached) return fetch(event.request);
    const range = event.request.headers.get('Range');
    if (!range) return cached;
    const bytes = await cached.arrayBuffer();
    const match = /^bytes=(\d*)-(\d*)$/.exec(range);
    if (!match) return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${bytes.byteLength}` } });
    const start = match[1] ? Number(match[1]) : Math.max(0, bytes.byteLength - Number(match[2]));
    const end = match[1] && match[2] ? Math.min(Number(match[2]), bytes.byteLength - 1) : bytes.byteLength - 1;
    if (start > end || start >= bytes.byteLength) return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${bytes.byteLength}` } });
    return new Response(bytes.slice(start, end + 1), { status: 206, headers: { 'Content-Type': 'audio/mpeg', 'Accept-Ranges': 'bytes', 'Content-Length': String(end - start + 1), 'Content-Range': `bytes ${start}-${end}/${bytes.byteLength}` } });
  })());
});
