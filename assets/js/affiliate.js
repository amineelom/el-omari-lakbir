(function(){
  function isExternal(url){
    try { const u = new URL(url, location.href); return u.hostname !== location.hostname; }
    catch(e){ return false; }
  }
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href]').forEach(a => {
      const href = a.getAttribute('href');
      // Mark likely affiliate links (contains ?ref= or ?aff= or known networks)
      const looksAffiliate = /(\baff\b|\bref\b|utm_|shareasale|impact|partner|r=\d+)/i.test(href || '');
      if (isExternal(href) && looksAffiliate) {
        a.setAttribute('rel','nofollow sponsored noopener');
      }
      // Track outbound clicks (minimal, GA friendly)
      a.addEventListener('click', () => {
        if (window.gtag && isExternal(href)) {
          gtag('event','click', { 'event_category':'outbound', 'event_label': href });
        }
      });
    });
  });
})();
