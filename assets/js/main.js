/* ==========================================================================
   SÁM digital · Home v1
   Lenis (scroll suave) + GSAP/ScrollTrigger (animación y scrollytelling)
   ========================================================================== */
(() => {
  'use strict';

  const $  = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  const yearEl = $('[data-year]');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  if (!window.gsap || !window.ScrollTrigger) return;
  gsap.registerPlugin(ScrollTrigger);

  if (reduce) root.classList.add('reduce');

  /* ───────── Utilidades ───────── */

  // Divide un texto en palabras (conserva <em> y otros elementos). mask: cada palabra con máscara de recorte.
  function split(el, mask = true) {
    const words = [];
    const walk = (node) => {
      const frag = document.createDocumentFragment();
      node.childNodes.forEach((child) => {
        if (child.nodeType === 3) {
          child.textContent.split(/(\s+)/).forEach((tok) => {
            if (!tok) return;
            if (/^\s+$/.test(tok)) { frag.appendChild(document.createTextNode(' ')); return; }
            const outer = document.createElement('span');
            outer.className = mask ? 'w' : 'sw';
            const inner = document.createElement('span');
            inner.className = 'wi';
            inner.textContent = tok;
            outer.appendChild(inner);
            frag.appendChild(outer);
            words.push(inner);
          });
        } else if (child.nodeType === 1) {
          const clone = child.cloneNode(false);
          clone.appendChild(walk(child));
          frag.appendChild(clone);
        }
      });
      return frag;
    };
    const frag = walk(el);
    el.textContent = '';
    el.appendChild(frag);
    return words;
  }

  // Dígitos que ruedan (como Superside). Devuelve las columnas para animarlas.
  function buildRoll(el) {
    const val = String(el.dataset.roll);
    const suffix = el.dataset.suffix || '';
    el.textContent = '';
    const cols = [];
    [...val].forEach((ch) => {
      const d = document.createElement('span');
      d.className = 'digit';
      d.setAttribute('aria-hidden', 'true');
      const col = document.createElement('span');
      col.className = 'digit__col';
      for (let n = 0; n < 20; n++) {
        const i = document.createElement('i');
        i.textContent = n % 10;
        col.appendChild(i);
      }
      d.dataset.to = ch;
      d.appendChild(col);
      el.appendChild(d);
      cols.push({ col, to: Number(ch) });
    });
    let sfx = null;
    if (suffix) {
      sfx = document.createElement('span');
      sfx.className = 'suffix';
      sfx.setAttribute('aria-hidden', 'true');
      sfx.textContent = suffix;
      el.appendChild(sfx);
    }
    return { cols, sfx };
  }

  // Cada columna toma el ancho real del dígito final (evita huecos entre cifras como el "1")
  const fitDigits = () => $$('.digit').forEach((d) => {
    const m = document.createElement('span');
    m.style.cssText = 'position:absolute;visibility:hidden;white-space:pre';
    m.textContent = d.dataset.to;
    d.parentElement.appendChild(m);
    d.style.width = m.offsetWidth + 1 + 'px'; // offsetWidth no se ve afectado por escalas (.years entra con scale 0)
    m.remove();
  });

  /* ───────── Scroll suave ───────── */
  let lenis = null;
  if (!reduce && window.Lenis) {
    lenis = new Lenis({ lerp: 0.09, wheelMultiplier: 0.95, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  const scrollToTarget = (target) => {
    if (lenis) lenis.scrollTo(target, { duration: 1.6, easing: (t) => 1 - Math.pow(1 - t, 4) });
    else target.scrollIntoView({ behavior: 'smooth' });
  };

  /* ───────── Cabecera + menú móvil ───────── */
  const header = $('#header');
  const burger = $('.burger');
  const mmenu = $('#mobile-menu');
  let menuOpen = false;
  let headerHidden = false;

  const showHeader = (show) => {
    const hide = !show;
    if (hide === headerHidden) return;
    headerHidden = hide;
    gsap.to(header, { yPercent: hide ? -140 : 0, duration: 0.8, ease: 'expo.out', overwrite: 'auto' });
  };

  const setMenu = (open) => {
    menuOpen = open;
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    mmenu.classList.toggle('is-open', open);
    mmenu.setAttribute('aria-hidden', String(!open));
    if (lenis) open ? lenis.stop() : lenis.start();
    if (open) showHeader(true);
  };
  burger.addEventListener('click', () => setMenu(!menuOpen));
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && menuOpen) setMenu(false); });

  ScrollTrigger.create({
    start: 0, end: 'max',
    onUpdate: (self) => {
      const y = self.scroll();
      header.classList.toggle('is-solid', y > 60);
      if (menuOpen) return;
      if (self.direction === 1 && y > 320) showHeader(false);
      else if (self.direction === -1) showHeader(true);
    },
  });

  // Anclas con scroll suave
  $$('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (!id || id.length < 2) return;
      const target = $(id);
      if (!target) return;
      e.preventDefault();
      if (menuOpen) setMenu(false);
      scrollToTarget(target);
    });
  });

  // Barra de progreso
  gsap.to('.progress', { scaleX: 1, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: 0.2 } });

  /* ───────── Triggers que viven DEBAJO de los pines ─────────
     ScrollTrigger calcula mal la posición de lo que se crea antes que un pin que queda más arriba en la página,
     así que estas funciones se llaman al final, cuando ya existen el pin del proceso y el scroll horizontal. */

  // Enlace activo del menú
  const initNav = () => {
    const navLinks = $$('.nav__link');
    // Qué sección resalta cada bloque de la página (el proceso cuenta como "Soluciones", las cifras como "Nosotros")
    const map = [
      ['inicio', '#inicio'], ['nosotros', '#nosotros'], ['soluciones', '#soluciones'], ['soluciones', '#como'],
      ['soluciones', '.story'], ['nosotros', '.stats'], ['portafolio', '#portafolio'], ['contacto', '#contacto'],
    ];
    // Se lee la posición real en cada scroll (los pines cambian el layout, no conviene fiarse de rangos precalculados)
    const update = () => {
      const line = innerHeight * 0.55;
      let id = null;
      map.forEach(([nid, sel]) => {
        const el = $(sel);
        if (!el) return;
        const r = el.getBoundingClientRect();
        if (r.top <= line && r.bottom > line) id = nid;
      });
      navLinks.forEach((l) => l.classList.toggle('is-current', !!id && l.getAttribute('href') === '#' + id));
    };
    ScrollTrigger.create({ start: 0, end: 'max', onUpdate: update });
    ScrollTrigger.addEventListener('refresh', update);
    update();
  };

  // Dígitos que ruedan (también con movimiento reducido)
  const initRolls = () => {
    $$('[data-roll]').forEach((el) => {
      const { cols, sfx } = buildRoll(el);
      const finalY = (c) => -(10 + c.to) * 5;
      if (reduce) { cols.forEach((c) => gsap.set(c.col, { yPercent: finalY(c) })); return; }
      if (sfx) gsap.set(sfx, { autoAlpha: 0, x: -10 });
      cols.forEach((c) => gsap.set(c.col, { yPercent: 0 }));
      ScrollTrigger.create({
        trigger: el, start: 'top 88%', once: true,
        onEnter: () => {
          cols.forEach((c, i) => gsap.to(c.col, { yPercent: finalY(c), duration: 2.2 + i * 0.35, ease: 'expo.out' }));
          if (sfx) gsap.to(sfx, { autoAlpha: 1, x: 0, duration: 1, delay: 1.2, ease: 'power3.out' });
        },
      });
    });
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(fitDigits);
    addEventListener('resize', fitDigits);
  };

  // Titulares con máscara (todas las secciones salvo el hero) y aparición genérica
  const initReveals = (skip) => {
    $$('[data-split]').forEach((el) => {
      if (el === skip) return;
      const words = split(el);
      gsap.set(words, { yPercent: 118 });
      ScrollTrigger.create({
        trigger: el, start: 'top 86%', once: true,
        onEnter: () => gsap.to(words, { yPercent: 0, duration: 1.3, stagger: 0.06, ease: 'expo.out' }),
      });
    });
    gsap.set('[data-reveal]', { autoAlpha: 0, y: 44 });
    ScrollTrigger.batch('[data-reveal]', {
      start: 'top 90%', once: true,
      onEnter: (els) => gsap.to(els, { autoAlpha: 1, y: 0, duration: 1.1, stagger: 0.12, ease: 'expo.out' }),
    });
  };

  /* ───────── Cursor personalizado (punto pegado al puntero + aro con suavizado corto) ───────── */
  if (fine && !reduce) {
    root.classList.add('has-cursor');
    const cur = $('.cursor');
    const ring = $('.cursor__ring');
    const dot = $('.cursor__dot');
    const label = $('.cursor__label');
    // Sin GSAP en el cursor: el punto se coloca en el mismo evento del mouse y el aro lo sigue con un suavizado
    // calculado por tiempo (45 ms, independiente de los fps). Solo transform; el bucle se apaga cuando el aro alcanza al punto.
    let tx = 0, ty = 0, rx = 0, ry = 0, live = false, running = false, last = 0, mx = -1, my = -1, raf = 0;
    const place = (el, x, y) => { el.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) translate(-50%,-50%)'; };
    const tick = (now) => {
      const dt = Math.max(1, Math.min(50, now - last));
      last = now;
      const k = 1 - Math.exp(-dt / 45);
      rx += (tx - rx) * k; ry += (ty - ry) * k;
      if (Math.abs(tx - rx) < 0.15 && Math.abs(ty - ry) < 0.15) { rx = tx; ry = ty; running = false; }
      place(ring, rx, ry);
      if (running) requestAnimationFrame(tick);
    };
    const setState = (target) => {
      if (!target || !target.closest) return;
      const view = target.closest('[data-cursor="view"]');
      const link = target.closest('a, button, [role="button"]');
      cur.classList.toggle('is-view', !!view);
      cur.classList.toggle('is-link', !view && !!link);
      if (view) label.textContent = view.dataset.cursorLabel || 'Ver';
    };

    addEventListener('mousemove', (e) => {
      tx = mx = e.clientX; ty = my = e.clientY;
      place(dot, tx, ty);
      if (!live) { live = true; rx = tx; ry = ty; place(ring, rx, ry); cur.classList.add('is-on'); }
      if (!running) { running = true; last = performance.now(); requestAnimationFrame(tick); }
    }, { passive: true });
    root.addEventListener('mouseleave', () => { live = false; cur.classList.remove('is-on'); });
    addEventListener('mousedown', () => cur.classList.add('is-down'));
    addEventListener('mouseup', () => cur.classList.remove('is-down'));
    document.addEventListener('mouseover', (e) => setState(e.target));
    // Con scroll suave el contenido se mueve bajo el cursor sin eventos de mouse: se revalida el estado
    addEventListener('scroll', () => {
      if (raf || mx < 0) return;
      raf = requestAnimationFrame(() => { raf = 0; setState(document.elementFromPoint(mx, my)); });
    }, { passive: true });
  }

  /* ───────── Botones: magnéticos + foco de luz que sigue al cursor ───────── */
  if (fine && !reduce) {
    const magnetic = new Set($$('[data-magnetic], .btn, .cta__bubble, .social a, .footer__big, .fab-popup-cta, .burger'));
    magnetic.forEach((el) => {
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        el.style.setProperty('--mx', e.clientX - r.left + 'px');
        el.style.setProperty('--my', e.clientY - r.top + 'px');
        gsap.to(el, { x: (e.clientX - r.left - r.width / 2) * 0.35, y: (e.clientY - r.top - r.height / 2) * 0.5, duration: 0.4, ease: 'power3.out', overwrite: 'auto' });
      });
      el.addEventListener('mouseleave', () => gsap.to(el, { x: 0, y: 0, duration: 0.8, ease: 'elastic.out(1,.4)', overwrite: 'auto' }));
    });
    // Tarjetas y filas de soluciones: la luz sigue al cursor
    $$('.ccard, .svc a').forEach((el) => {
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        el.style.setProperty('--mx', e.clientX - r.left + 'px');
        el.style.setProperty('--my', e.clientY - r.top + 'px');
      }, { passive: true });
    });
  }

  /* ───────── WhatsApp: círculo que se expande y abre una tarjeta de contacto ───────── */
  const fab = $('#fab');
  const fabPopup = $('#fabPopup');
  const fabClose = $('#fabPopupClose');
  if (fab && fabPopup && fabClose) {
    const parts = $$('[data-fab-part]', fabPopup);
    let fabOpen = false;
    const openFab = () => {
      fabOpen = true;
      fab.setAttribute('aria-expanded', 'true');
      fab.classList.add('is-hidden');
      fabPopup.classList.add('is-open');
      if (reduce) { fabPopup.style.opacity = 1; return; }
      gsap.killTweensOf([fabPopup, ...parts]);
      gsap.timeline()
        .fromTo(fabPopup, { opacity: 0, scale: 0.85, y: 16 }, { opacity: 1, scale: 1, y: 0, duration: 0.45, ease: 'back.out(1.6)' })
        .fromTo(parts, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.35, ease: 'power3.out', stagger: 0.08 }, '-=0.25');
    };
    const closeFab = () => {
      fabOpen = false;
      fab.setAttribute('aria-expanded', 'false');
      fab.classList.remove('is-hidden');
      if (reduce) { fabPopup.style.opacity = 0; fabPopup.classList.remove('is-open'); return; }
      gsap.killTweensOf([fabPopup, ...parts]);
      gsap.to(fabPopup, { opacity: 0, scale: 0.9, y: 10, duration: 0.25, ease: 'power2.in', onComplete: () => fabPopup.classList.remove('is-open') });
    };
    fab.addEventListener('click', () => (fabOpen ? closeFab() : openFab()));
    fabClose.addEventListener('click', closeFab);
    document.addEventListener('click', (e) => {
      if (!fabOpen || fabPopup.contains(e.target) || fab.contains(e.target)) return;
      closeFab();
    });
    addEventListener('keydown', (e) => { if (fabOpen && e.key === 'Escape') closeFab(); });
    // Aparece al bajar medio viewport
    const fabVisibility = () => fab.classList.toggle('is-visible', scrollY > innerHeight * 0.5);
    addEventListener('scroll', fabVisibility, { passive: true });
    fabVisibility();
  }

  if (reduce) { initRolls(); finishReduced(); return; }

  /* ───────── Hero ───────── */
  const heroTitle = $('.hero__title');
  const heroWords = split(heroTitle);
  gsap.set(heroWords, { yPercent: 118 });
  gsap.set('[data-hero-in]', { autoAlpha: 0, y: 34 });
  gsap.set('.wall', { autoAlpha: 0, x: 90, scale: 0.94 });
  gsap.set('.hero__scroll', { autoAlpha: 0 });
  gsap.set(header, { yPercent: -140 });

  const intro = () => {
    gsap.timeline({ defaults: { ease: 'expo.out' }, delay: 0.15 })
      .to('.wall', { autoAlpha: 1, x: 0, scale: 1, duration: 2, ease: 'power4.out' }, 0.1)
      .to(header, { yPercent: 0, duration: 1.3 }, 0.35)
      .to(heroWords, { yPercent: 0, duration: 1.5, stagger: 0.07 }, 0.3)
      .to('[data-hero-in]', { autoAlpha: 1, y: 0, duration: 1.2, stagger: 0.13 }, 0.5)
      .to('.hero__scroll', { autoAlpha: 1, duration: 1 }, 1.4);
  };
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(intro);

  // Parallax al hacer scroll
  gsap.timeline({ scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } })
    .to('.hero__bg', { yPercent: 10, ease: 'none' }, 0)
    .to('.wall__rot', { yPercent: -10, ease: 'none' }, 0)
    .to('[data-hero-copy]', { yPercent: -14, opacity: 0.15, ease: 'none' }, 0);

  // Parallax con el mouse
  if (fine) {
    const heroEl = $('.hero');
    const wallEl = $('.wall');
    const bgx = gsap.quickTo(wallEl, 'x', { duration: 1.4, ease: 'power3' });
    const bgy = gsap.quickTo(wallEl, 'y', { duration: 1.4, ease: 'power3' });
    // Luz de color que sigue al cursor sobre el hero (como en Asoclicper)
    const glow = $('.hero__glow');
    gsap.set(glow, { xPercent: -50, yPercent: -50 });
    const glowX = gsap.quickTo(glow, 'x', { duration: 0.75, ease: 'power3.out' });
    const glowY = gsap.quickTo(glow, 'y', { duration: 0.75, ease: 'power3.out' });
    let glowOn = false;
    heroEl.addEventListener('mousemove', (e) => {
      const nx = e.clientX / innerWidth - 0.5;
      const ny = e.clientY / innerHeight - 0.5;
      bgx(nx * -34); bgy(ny * -22);
      const r = heroEl.getBoundingClientRect();
      glowX(e.clientX - r.left); glowY(e.clientY - r.top);
      if (!glowOn) { glowOn = true; gsap.to(glow, { opacity: 1, duration: 0.45, overwrite: 'auto' }); }
    });
    heroEl.addEventListener('mouseleave', () => { glowOn = false; gsap.to(glow, { opacity: 0, duration: 0.7, overwrite: 'auto' }); });
  }

  /* ───────── Muro de trabajos del hero (reactivo a la velocidad del scroll) ───────── */
  const bandTweens = [];
  // Muro de trabajos del hero: columnas en sentidos opuestos, también reactivas a la velocidad del scroll
  $$('.wall__col').forEach((col, i) => {
    const track = $('.wall__track', col);
    const base = track.innerHTML;
    const target = $('.wall__rot').offsetHeight * 1.1;
    let html = base;
    track.innerHTML = html;
    let guard = 0;
    while (track.scrollHeight < target && guard++ < 4) { html += base; track.innerHTML = html; }
    track.innerHTML = html + html;
    const up = i % 2 === 0;
    bandTweens.push(gsap.fromTo(track, { yPercent: up ? 0 : -50 }, { yPercent: up ? -50 : 0, duration: 60 + i * 14, ease: 'none', repeat: -1 }));
  });
  let lastY = scrollY, boost = 0;
  gsap.ticker.add(() => {
    const dy = Math.abs(scrollY - lastY);
    lastY = scrollY;
    boost += (Math.min(dy, 70) / 7 - boost) * 0.08;
    bandTweens.forEach((t) => t.timeScale(1 + boost));
  });

  /* ───────── Sobre nosotros ───────── */
  const bigWords = split($('.about__big'), false);
  gsap.fromTo(bigWords, { opacity: 0.14 }, {
    opacity: 1, ease: 'none', stagger: 0.1,
    scrollTrigger: { trigger: '.about__big', start: 'top 82%', end: 'bottom 46%', scrub: 0.4 },
  });
  const aboutImg = $('.about__media > img');
  gsap.fromTo(aboutImg, { scale: 0.88, rotate: -3, yPercent: 6 }, {
    scale: 1, rotate: 0, yPercent: -4, ease: 'none',
    scrollTrigger: { trigger: '.about__media', start: 'top bottom', end: 'bottom 30%', scrub: 0.6 },
  });
  gsap.from('.years', {
    scale: 0, autoAlpha: 0, duration: 1.2, ease: 'back.out(1.7)',
    scrollTrigger: { trigger: '.about__media', start: 'top 65%', once: true },
  });

  /* ───────── Soluciones: vista previa que sigue al cursor ───────── */
  const list = $('.svc-list');
  const preview = $('.svc-preview');
  if (list && preview && fine) {
    const pimg = $('img', preview);
    gsap.set(preview, { autoAlpha: 0, scale: 0.7 });
    const px = gsap.quickTo(preview, 'x', { duration: 0.55, ease: 'power3' });
    const py = gsap.quickTo(preview, 'y', { duration: 0.55, ease: 'power3' });
    const pr = gsap.quickTo(preview, 'rotation', { duration: 0.7, ease: 'power3' });
    let lastX = 0;
    // La tarjeta viaja pegada al borde derecho de la lista (sin tapar los títulos) y sigue al cursor en vertical
    let lastY = 0;
    list.addEventListener('mousemove', (e) => {
      const r = list.getBoundingClientRect();
      const w = preview.offsetWidth;
      const nx = (e.clientX - (r.left + r.width / 2)) / r.width;
      px(r.right - w - 96 + nx * 40);
      py(e.clientY - preview.offsetHeight / 2);
      pr(clamp((e.clientY - lastY) * 0.5 + (e.clientX - lastX) * 0.2, -14, 14));
      lastX = e.clientX;
      lastY = e.clientY;
    });
    $$('.svc', list).forEach((row) => {
      row.addEventListener('mouseenter', () => {
        pimg.src = row.dataset.img;
        gsap.to(preview, { autoAlpha: 1, scale: 1, duration: 0.6, ease: 'back.out(1.6)', overwrite: 'auto' });
      });
    });
    list.addEventListener('mouseleave', () => gsap.to(preview, { autoAlpha: 0, scale: 0.7, duration: 0.35, overwrite: 'auto' }));
  }

  /* ───────── Cómo lo hacemos · Scrollytelling ───────── */
  const story = $('.story');
  if (story) {
    const pin = $('.story__pin', story);
    const dash = $('[data-dash]', story);
    const panels = $$('.panel', story);
    const layers = $$('.viz__layer', story);
    const tabs = $$('.dash__tab', story);
    const fills = $$('.story__progress i', story);
    const countEl = $('.story__count b', story);
    let cur = -1;

    // Centra nodos y hub con transformaciones de GSAP
    gsap.set($$('.node, .hub', story), { xPercent: -50, yPercent: -50 });

    // Líneas entre el hub y cada nodo (calculadas en px para que coincidan siempre)
    const layoutLinks = () => {
      const l = layers[0];
      const W = l.offsetWidth, H = l.offsetHeight;
      if (!W) return;
      $$('.link', l).forEach((n) => n.remove());
      $$('.node', l).forEach((node) => {
        const nx = (parseFloat(node.style.getPropertyValue('--x')) / 100) * W;
        const ny = (parseFloat(node.style.getPropertyValue('--y')) / 100) * H;
        const dx = nx - W / 2, dy = ny - H / 2;
        const link = document.createElement('i');
        link.className = 'link';
        link.style.cssText = `left:${W / 2}px;top:${H / 2}px;width:${Math.hypot(dx, dy)}px`;
        l.insertBefore(link, l.firstChild);
        gsap.set(link, { rotation: (Math.atan2(dy, dx) * 180) / Math.PI, transformOrigin: '0 50%', scaleX: cur === 0 ? 1 : 0 });
      });
    };
    layoutLinks();
    addEventListener('resize', layoutLinks);

    const enter = [
      // 1 · Datos: las fuentes se conectan al sistema
      () => {
        const l = layers[0];
        layoutLinks();
        const links = $$('.link', l), nodes = $$('.node', l), hub = $('.hub', l);
        gsap.fromTo(hub, { scale: 0.3, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.9, ease: 'back.out(1.7)', overwrite: true });
        gsap.fromTo(links, { scaleX: 0 }, { scaleX: 1, duration: 0.9, stagger: 0.09, ease: 'power3.out', delay: 0.2, overwrite: true });
        gsap.fromTo(nodes, { scale: 0.4, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.8, stagger: 0.09, ease: 'back.out(1.8)', delay: 0.35, overwrite: true });
      },
      // 2 · Análisis: barras, curva e insights
      () => {
        const l = layers[1];
        gsap.fromTo($$('.bar', l), { scaleY: 0 }, { scaleY: 1, duration: 1.1, stagger: 0.07, ease: 'power3.out', overwrite: true });
        gsap.fromTo($('.chart__line path', l), { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.8, ease: 'power2.inOut', delay: 0.4, overwrite: true });
        gsap.fromTo($$('.insight', l), { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: 0.8, stagger: 0.28, ease: 'expo.out', delay: 0.8, overwrite: true });
      },
      // 3 · Estrategia: embudo hasta la venta
      () => {
        const l = layers[2];
        gsap.fromTo($$('.band-f', l), { scaleX: 0, autoAlpha: 0 }, { scaleX: 1, autoAlpha: 1, duration: 0.9, stagger: 0.16, ease: 'power3.out', overwrite: true });
        gsap.fromTo($('.plan', l), { autoAlpha: 0, y: -12 }, { autoAlpha: 1, y: 0, duration: 0.8, delay: 0.3, overwrite: true });
        gsap.fromTo($('.sale', l), { scale: 0, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.9, delay: 1, ease: 'back.out(2.2)', overwrite: true });
      },
    ];

    const setStep = (i) => {
      if (i === cur) return;
      const prev = cur;
      cur = i;
      panels.forEach((p, k) => {
        if (k === i) {
          p.classList.add('is-active');
          gsap.set(p, { autoAlpha: 1 });
          const kids = [$('.panel__title', p), $('.panel__text', p), ...$$('.panel__list li', p)];
          gsap.fromTo(kids, { autoAlpha: 0, y: 36 }, { autoAlpha: 1, y: 0, duration: 0.95, stagger: 0.09, ease: 'expo.out', delay: 0.12, overwrite: true });
        } else if (k === prev) {
          p.classList.remove('is-active');
          gsap.to(p, { autoAlpha: 0, duration: 0.25, overwrite: true });
        }
      });
      if (prev >= 0) gsap.to(layers[prev], { autoAlpha: 0, duration: 0.35, overwrite: true });
      gsap.set(layers[i], { autoAlpha: 1 });
      enter[i]();
      tabs.forEach((t, k) => t.classList.toggle('is-on', k === i));
      if (countEl) countEl.textContent = '0' + (i + 1);
    };

    // El panel entra inclinado en 3D y se endereza mientras llega a la sección
    gsap.fromTo(dash,
      { rotationY: -22, rotationX: 11, scale: 0.86, y: 70, transformPerspective: 1600 },
      { rotationY: 0, rotationX: 0, scale: 1, y: 0, ease: 'none',
        scrollTrigger: { trigger: story, start: 'top 100%', end: 'top 18%', scrub: 0.6 } });

    ScrollTrigger.create({
      trigger: story, start: 'top 72%',
      onEnter: () => { if (cur < 0) setStep(0); },
    });

    ScrollTrigger.create({
      trigger: pin, start: 'top top', end: () => '+=' + innerHeight * 2.5,
      pin: true, anticipatePin: 1, invalidateOnRefresh: true,
      onUpdate: (self) => {
        const p = self.progress;
        setStep(Math.min(2, Math.floor(p * 3)));
        fills.forEach((f, k) => gsap.set(f, { scaleX: clamp(p * 3 - k, 0, 1) }));
      },
    });
  }

  /* ───────── Portafolio · scroll horizontal ───────── */
  const work = $('.work');
  if (work) {
    const track = $('.work__track', work);
    const wpin = $('.work__pin', work);
    const dist = () => Math.max(0, track.scrollWidth - innerWidth);
    gsap.to(track, {
      x: () => -dist(), ease: 'none',
      scrollTrigger: { trigger: work, start: 'top top', end: () => '+=' + dist(), pin: wpin, scrub: 0.8, anticipatePin: 1, invalidateOnRefresh: true },
    });
  }

  /* ───────── Lo que queda debajo de los pines ───────── */
  initNav();
  initRolls();
  initReveals(heroTitle);

  gsap.from('.cta__bubble', {
    scale: 0.3, autoAlpha: 0, rotate: -40, duration: 1.4, ease: 'back.out(1.6)',
    scrollTrigger: { trigger: '.cta__title', start: 'top 70%', once: true },
  });

  addEventListener('load', () => ScrollTrigger.refresh());
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => ScrollTrigger.refresh());

  /* Con movimiento reducido: sin pin ni animaciones, contenido visible */
  function finishReduced() {
    gsap.set($$('.node, .hub'), { xPercent: -50, yPercent: -50 });
    const l = $('.viz__layer[data-layer="0"]');
    if (l) {
      const W = l.offsetWidth, H = l.offsetHeight;
      $$('.node', l).forEach((node) => {
        const nx = (parseFloat(node.style.getPropertyValue('--x')) / 100) * W;
        const ny = (parseFloat(node.style.getPropertyValue('--y')) / 100) * H;
        const dx = nx - W / 2, dy = ny - H / 2;
        const link = document.createElement('i');
        link.className = 'link';
        link.style.cssText = `left:${W / 2}px;top:${H / 2}px;width:${Math.hypot(dx, dy)}px;transform-origin:0 50%;transform:rotate(${(Math.atan2(dy, dx) * 180) / Math.PI}deg)`;
        l.insertBefore(link, l.firstChild);
      });
    }
    $$('.chart__line path').forEach((p) => { p.style.strokeDashoffset = 0; });
  }
})();
