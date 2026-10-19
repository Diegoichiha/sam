/* ==========================================================================
   SÁM digital · eventos propios para el Google tag (GA4 y Google Ads)
   El Google tag (GT-K4CXQSWC) se carga en el <head> de cada página (build.py) y solo envía datos
   desde samdigital.com.co. Aquí se definen los eventos que antes enviaba WordPress:
     · clic a WhatsApp  → gtag "click to chat"  +  dataLayer "Click to Chat"   (mismos nombres que el plugin anterior)
     · formulario enviado → gtag "generate_lead" +  dataLayer "form_submit"
   ========================================================================== */
(() => {
  'use strict';

  const WA_NUMBER = '573167335485';
  const layer = (window.dataLayer = window.dataLayer || []);

  // Envía un evento al Google tag (si no cargó, por ejemplo con un bloqueador, no pasa nada) y, opcional, al dataLayer
  window.samTrack = (name, params, layerEvent) => {
    try {
      if (typeof window.gtag === 'function') window.gtag('event', name, params || {});
      if (layerEvent) layer.push(layerEvent);
    } catch (_) { /* la analítica nunca debe romper la página */ }
  };

  // Cualquier enlace a WhatsApp: botones, tarjeta del botón flotante y respaldo del formulario
  document.addEventListener('click', (e) => {
    const a = e.target.closest && e.target.closest('a[href*="wa.link/"], a[href*="wa.me/"], a[href*="api.whatsapp.com"]');
    if (!a) return;
    const data = { number: WA_NUMBER, title: document.title, url: location.href };
    window.samTrack('click to chat', data, { event: 'Click to Chat', type: 'chat', ...data, ref: 'dataLayer push' });
  }, true);
})();
