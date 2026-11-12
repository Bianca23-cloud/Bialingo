/* Page de téléchargement : met en avant la plateforme détectée et masque les liens si le dépôt n'est pas encore configuré. */
(function () {
  'use strict';
  var ua = navigator.userAgent || '';
  var platform = /android/i.test(ua) ? 'android'
    : (/iphone|ipad|ipod/i.test(ua) || (/macintosh/i.test(ua) && navigator.maxTouchPoints > 1)) ? 'ios'
    : /windows/i.test(ua) ? 'windows' : '';
  if (platform) {
    var el = document.getElementById(platform);
    if (el && el.parentNode) {
      el.parentNode.insertBefore(el, el.parentNode.firstChild);
      var h = el.querySelector('h2');
      if (h) { h.textContent = h.textContent + ' (votre appareil)'; }
    }
  }
  if (document.getElementById('apk').getAttribute('href').indexOf('__REPO__') !== -1) {
    ['apk', 'exe', 'exep', 'appimage', 'deb', 'sums', 'src'].forEach(function (id) {
      var a = document.getElementById(id);
      if (a) { a.removeAttribute('href'); a.setAttribute('aria-disabled', 'true'); a.textContent = a.textContent + ' (disponible après la première publication)'; }
    });
  }
})();
