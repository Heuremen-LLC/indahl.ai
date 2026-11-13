// Registers the app shell. Nothing is sent anywhere: the worker only keeps public pages on the visitor's own device.
if ('serviceWorker' in navigator) window.addEventListener('load', function () { navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {}); });
