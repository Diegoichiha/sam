/* ==========================================================================
   SÁM digital · lógica de las páginas internas
   main.js llama a window.SAM_PAGE(ctx) antes de crear lo que vive debajo de los pines.
   ========================================================================== */
window.SAM_PAGE = function (ctx) {
  'use strict';
  const { $, $$, clamp, split, gsap, ScrollTrigger, reduce } = ctx;
  const WA_NUMBER = '573167335485';

  /* ───────── Texto que se ilumina palabra a palabra con el scroll ───────── */
  if (!reduce) {
    $$('[data-scrub]').forEach((el) => {
      const words = split(el, false);
      gsap.fromTo(words, { opacity: 0.14 }, {
        opacity: 1, ease: 'none', stagger: 0.1,
        scrollTrigger: { trigger: el, start: 'top 82%', end: 'bottom 46%', scrub: 0.4 },
      });
    });
  }

  /* ───────── Mosaico (Nosotros): cada pieza entra desde una dirección distinta ───────── */
  const tiles = $$('.mosaic .tile');
  if (tiles.length && !reduce) {
    const dirs = [[-70, 0], [0, 70], [70, 0], [-70, 0], [0, 70], [70, 0]];
    tiles.forEach((t, i) => gsap.set(t, { autoAlpha: 0, x: dirs[i % dirs.length][0], y: dirs[i % dirs.length][1], scale: 0.92 }));
    ScrollTrigger.create({
      trigger: '.mosaic', start: 'top 85%', once: true,
      onEnter: () => gsap.to(tiles, { autoAlpha: 1, x: 0, y: 0, scale: 1, duration: 1.3, stagger: 0.12, ease: 'expo.out' }),
    });
  }

  /* ───────── Proceso: tarjetas que se apilan (sticky) y se alejan al llegar la siguiente ───────── */
  $$('.s-steps').forEach((sec) => {
    const cards = $$('.step-card', sec);
    const cur = $('[data-steps-cur]', sec);
    const bar = $('[data-steps-bar]', sec);
    const n = cards.length;
    const setCur = (i) => {
      if (cur) cur.textContent = String(i).padStart(2, '0');
      if (bar) bar.style.transform = `scaleX(${i / n})`;
    };
    setCur(1);
    if (reduce) return;
    cards.forEach((card, i) => {
      if (i < n - 1) {
        // Se oscurece en vez de volverse translúcida: así no deja ver las tarjetas de atrás
        gsap.fromTo(card, { scale: 1, filter: 'brightness(1)' }, {
          scale: 0.94, filter: 'brightness(0.66)', ease: 'none',
          scrollTrigger: { trigger: cards[i + 1], start: 'top 82%', end: 'top 24%', scrub: true },
        });
      }
      ScrollTrigger.create({
        trigger: card, start: 'top 62%',
        onEnter: () => setCur(i + 1),
        onLeaveBack: () => setCur(Math.max(1, i)),
      });
    });
  });

  /* ───────── Portafolio: pestañas con filtro animado ───────── */
  const pgrid = $('[data-pgrid]');
  if (pgrid) {
    const tabs = $$('.ptab');
    const cards = $$('.pf', pgrid);
    const empty = $('[data-pempty]');
    const apply = (cat) => {
      let keep = 0;
      cards.forEach((c) => { const on = c.dataset.cat === cat; c.hidden = !on; if (on) keep++; });
      if (empty) empty.hidden = keep > 0;
      return cards.filter((c) => !c.hidden);
    };
    apply('web');
    if (!reduce) {
      gsap.from(cards.filter((c) => !c.hidden), {
        autoAlpha: 0, y: 50, scale: 0.96, duration: 1, stagger: 0.08, ease: 'expo.out',
        scrollTrigger: { trigger: pgrid, start: 'top 88%', once: true },
      });
    }
    tabs.forEach((tab) => tab.addEventListener('click', () => {
      if (tab.classList.contains('is-on')) return;
      tabs.forEach((t) => { const on = t === tab; t.classList.toggle('is-on', on); t.setAttribute('aria-selected', String(on)); });
      const cat = tab.dataset.tab;
      if (reduce) { apply(cat); return; }
      const visible = cards.filter((c) => !c.hidden);
      gsap.to(visible, {
        autoAlpha: 0, y: 24, scale: 0.97, duration: 0.3, stagger: 0.02, overwrite: true,
        onComplete: () => {
          const next = apply(cat);
          gsap.fromTo(next, { autoAlpha: 0, y: 44, scale: 0.96 }, { autoAlpha: 1, y: 0, scale: 1, duration: 0.8, stagger: 0.07, ease: 'expo.out', overwrite: true, clearProps: 'transform' });
          ScrollTrigger.refresh();
        },
      });
    }));
  }

  /* ───────── Índice lateral (artículos y documentos): resalta la sección visible ───────── */
  const tocLinks = $$('.doc__toc ol a');
  if (tocLinks.length) {
    const heads = $$('.prose h2');
    const mark = (id) => tocLinks.forEach((a) => a.classList.toggle('is-on', a.getAttribute('href') === '#' + id));
    heads.forEach((h) => {
      h.dataset.scrollOffset = '-100';
      ScrollTrigger.create({ trigger: h, start: 'top 45%', end: 'bottom 45%', onToggle: (self) => { if (self.isActive) mark(h.id); } });
    });
    if (heads[0]) mark(heads[0].id);
  }

  /* ───────── Formulario de contacto ───────── */
  const form = $('[data-form]');
  if (form) {
    const err = $('[data-form-err]', form);
    const ok = $('[data-form-ok]', form);
    const field = (name) => form.elements[name];
    const flag = (el, bad) => { const box = el.closest('.fld, .chk'); if (box) box.classList.toggle('is-bad', bad); };
    form.addEventListener('input', (e) => { const box = e.target.closest('.fld, .chk'); if (box) box.classList.remove('is-bad'); err.hidden = true; });
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = field('email'), tel = field('telefono'), chk = field('acepto');
      const badEmail = !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.value.trim());
      const badTel = tel.value.replace(/\D/g, '').length < 7;
      const badChk = !chk.checked;
      flag(email, badEmail); flag(tel, badTel); flag(chk, badChk);
      if (badEmail || badTel || badChk) {
        err.textContent = 'Revisa los campos obligatorios: un correo válido, tu teléfono y la aceptación del Aviso Legal y la Política de Privacidad.';
        err.hidden = false;
        return;
      }
      err.hidden = true;
      // Sin backend: el mensaje se abre en WhatsApp ya redactado (se reemplaza por el envío real del formulario al migrar)
      const v = (n) => (field(n).value || '').trim();
      const lines = [
        `Hola, soy ${v('nombre') || 'una persona interesada'}${v('empresa') ? ' de ' + v('empresa') : ''}.`,
        `Correo: ${v('email')}`, `Teléfono: ${v('telefono')}`,
        v('mensaje') ? `Mensaje: ${v('mensaje')}` : '',
      ].filter(Boolean);
      window.open(`https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(lines.join('\n'))}`, '_blank', 'noopener');
      ok.hidden = false;
      if (!reduce) gsap.fromTo(ok, { autoAlpha: 0, y: 16 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: 'expo.out' });
    });
  }
};
