#!/usr/bin/env python3
"""
SÁM digital · generador del sitio estático.

Lee el contenido de src/ (datos extraídos de samdigital.com.co + plantillas) y escribe todas las páginas:
Home, Nosotros, Soluciones, 9 servicios, Portafolio, Contacto, Blog (+ artículos) y páginas legales.

Uso:  python build.py
"""
import hashlib
import html as H
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://samdigital.com.co'    # dominio de producción: canonical, og:url, og:image y sitemap
WA = 'https://wa.link/j7n585'          # enlace de WhatsApp que usa el sitio actual en todos sus CTA
WA_NUMBER = '573167335485'
EMAIL = 'info@samdigital.com.co'


def read(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return f.read()


def write(p, s):
    full = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)


def esc(t):
    return H.escape(t, quote=False)


def qa(t):
    return H.escape(t, quote=True)


def local_img(path):
    """Nombre local (webp) de una imagen de uploads: quita el sufijo -WxH y pasa a minúsculas."""
    base = re.sub(r'-\d+x\d+(?=\.\w+$)', '', os.path.basename(path))
    return os.path.splitext(base)[0].lower() + '.webp'


def J(p):
    return json.loads(read(p))


def ver(p):
    """Huella del archivo para ?v= : el navegador no sirve un CSS/JS viejo tras publicar cambios."""
    with open(os.path.join(ROOT, p), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


SV = J('src/data/services.json')
ABOUT = J('src/data/about.json')
LEGAL = J('src/data/legal.json')
POSTS = J('src/data/posts.json')
SEO = J('src/data/seo.json')          # título y descripción de cada página (clave = ruta: '', 'services/', ...)
HOME = read('src/pages/home.html')
CHROME = read('src/partials/chrome.html')
FAB = read('src/partials/fab.html')

# ───────────────────────── Catálogo de servicios ─────────────────────────
# (slug, título corto del menú, frase corta, ícono)
SHORT = {
    'generacion-de-leads': ('Generación de leads', 'Clientes ideales, más ventas', 'leads'),
    'marketing-estrategico': ('Marketing estratégico', 'Estrategias que cumplen metas', 'consultoria'),
    'social-media-manager': ('Social media marketing', 'Conecta, impacta y convierte', 'redessociales'),
    'diseno-de-paginas-web': ('Diseño de páginas web', 'Sitios, tiendas y landing pages', 'paginasweb'),
    'optimizacion-seo': ('Optimización SEO', 'Más visibilidad en Google', 'seoicon'),
    'publicidad-paga': ('Publicidad paga', 'Google, Meta, TikTok y LinkedIn', 'pautagoogle'),
    'email-marketing': ('Email marketing / SMS', 'Campañas que fidelizan', 'emailmarketing'),
    'diseno-grafico': ('Diseño gráfico', 'Piezas que comunican', 'diseno'),
    'branding': ('Branding', 'Una identidad poderosa', 'marca2'),
}
ORDER = list(SHORT.keys())
CARD = {c['slug']: c for c in SV['cards']}
for c in SV['cards']:
    c['title'] = c['title'].replace('Estrátegico', 'Estratégico')

LEGAL_LINKS = [
    ('Política de privacidad', 'politica-de-privacidad'),
    ('Declaración de accesibilidad', 'declaracion-de-accesibilidad'),
    ('Aviso legal', 'aviso-legal'),
    ('Política de cookies', 'politica-de-cookies'),
]

ARROW = '<svg width="{s}" height="{s}"><use href="#i-arrow"/></svg>'
ARROW_UR = '<svg width="{s}" height="{s}"><use href="#i-arrow-ur"/></svg>'
CHECK = '<svg width="16" height="16"><use href="#i-check"/></svg>'


def btn(label, href, cls='btn--primary', ico='', ext=False, size='', reveal=False):
    t = ' target="_blank" rel="noopener"' if ext else ''
    r = ' data-reveal' if reveal else ''
    return (f'<a class="btn {cls} {size}" href="{href}"{t}{r} data-magnetic>'
            f'<span class="btn__txt"><span>{esc(label)}</span><span aria-hidden="true">{esc(label)}</span></span>'
            f'<span class="btn__ico {ico}">{ARROW.format(s=18)}</span></a>')


# ───────────────────────── Piezas compartidas ─────────────────────────
def header(root, is_home):
    home = '#inicio' if is_home else root
    links = [
        ('01', 'Inicio', home, 'inicio'),
        ('02', 'Nosotros', root + 'sobre-nosotros/', 'nosotros'),
        ('03', 'Soluciones', root + 'services/', 'soluciones'),
        ('04', 'Portafolio', root + 'portafolio/', 'portafolio'),
        ('05', 'Blog', root + 'blog/', 'blog'),
        ('06', 'Contacto', root + 'contacto/', 'contacto'),
    ]
    link_html = '\n'.join(
        f'        <li><a href="{h}" data-nav="{k}"><span class="mm__n">{n}</span><span class="mm__t"><span>{t}</span></span></a></li>'
        for n, t, h, k in links)
    cards = '\n'.join(
        f'          <li><a class="mm__card" href="{root}{slug}/"><span class="mm__ico"><img src="{root}assets/img/services/{ico}.png" alt="" width="46" height="41"></span>'
        f'<span class="mm__ctx"><b>{esc(t)}</b><small>{esc(d)}</small></span><i class="mm__go">{ARROW_UR.format(s=16)}</i></a></li>'
        for slug, (t, d, ico) in SHORT.items())
    return f'''<!-- ───────── Header ───────── -->
<header class="header" id="header">
  <div class="container">
    <div class="header__bar">
      <a class="header__logo" href="{home}" aria-label="SÁM digital, inicio">
        <img src="{root}assets/img/brand/logo-sam-blanco.png" alt="SÁM digital" width="300" height="116">
      </a>
      <button class="burger" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="mega-menu">
        <span class="burger__txt"><span>Menú</span><span aria-hidden="true">Cerrar</span></span>
        <span class="burger__ico" aria-hidden="true"><i></i><i></i></span>
      </button>
    </div>
  </div>
</header>

<!-- ───────── Mega menú ───────── -->
<div class="mm" id="mega-menu" role="dialog" aria-modal="true" aria-label="Menú principal" aria-hidden="true" tabindex="-1" data-lenis-prevent>
  <div class="mm__bg" aria-hidden="true"></div>
  <div class="mm__inner container">
    <nav class="mm__nav" aria-label="Navegación">
      <p class="mm__label">Navegación</p>
      <ol class="mm__links">
{link_html}
      </ol>
    </nav>
    <section class="mm__sol" aria-label="Soluciones">
      <p class="mm__label">Soluciones <small>9 servicios que trabajan juntos</small></p>
      <ul class="mm__grid">
{cards}
      </ul>
    </section>
    <aside class="mm__cta" aria-label="Contacto">
      <div class="mm__ctabox">
        <span class="mm__badge"><i></i>Consultoría gratis</span>
        <h3>Convierte tu presencia digital en un <em>sistema de clientes</em></h3>
        <p>Cuéntanos tu idea y resuelve todas tus dudas en 30 minutos con un especialista.</p>
        <a class="btn btn--dark btn--xl mm__btn" href="{root}contacto/">
          <span class="btn__txt"><span>Hablemos de tu proyecto</span><span aria-hidden="true">Hablemos de tu proyecto</span></span>
          <span class="btn__ico btn__ico--orange">{ARROW.format(s=22)}</span>
        </a>
        <ul class="mm__proof">
          <li><b>15+</b><span>años de experiencia</span></li>
          <li><b>9</b><span>soluciones integradas</span></li>
          <li><b>30</b><span>min para tus dudas</span></li>
        </ul>
      </div>
    </aside>
  </div>
  <div class="mm__foot container">
    <div class="social">{social()}</div>
    <p>Más que marketing, creamos sistemas que generan ventas.</p>
  </div>
</div>
'''


def social():
    return ('<a href="https://www.facebook.com/profile.php?id=61582248838081" aria-label="Facebook" target="_blank" rel="noopener"><svg width="20" height="20"><use href="#i-fb"/></svg></a>'
            '<a href="https://www.instagram.com/samdigital_mkt/" aria-label="Instagram" target="_blank" rel="noopener"><svg width="20" height="20"><use href="#i-ig"/></svg></a>'
            '<a href="https://www.linkedin.com/company/s%C3%A1m-digital/" aria-label="LinkedIn" target="_blank" rel="noopener"><svg width="20" height="20"><use href="#i-in"/></svg></a>')


def footer(root, is_home):
    home = '#inicio' if is_home else root
    arrow = '<svg width="14" height="14" aria-hidden="true"><use href="#i-arrow-ur"/></svg>'
    groups = [
        ('Atraer clientes', ['generacion-de-leads', 'publicidad-paga', 'optimizacion-seo']),
        ('Convertir y fidelizar', ['diseno-de-paginas-web', 'email-marketing', 'marketing-estrategico']),
        ('Marca y contenido', ['branding', 'diseno-grafico', 'social-media-manager']),
    ]
    sol = '\n'.join(
        f'''          <div class="footer__col">
            <a class="footer__cat" href="{root}services/">{t} {arrow}</a>
            <ul>
''' + '\n'.join(f'              <li><a href="{root}{s}/">{esc(SHORT[s][0])}</a></li>' for s in sl) + '''
            </ul>
          </div>''' for t, sl in groups)
    nav = [
        ('Principal', [('Inicio', home), ('Nosotros', root + 'sobre-nosotros/'), ('Soluciones', root + 'services/'),
                       ('Portafolio', root + 'portafolio/'), ('Contacto', root + 'contacto/')]),
        ('Recursos', [('Blog', root + 'blog/'), ('Casos de éxito', root + 'portafolio/')]),
    ]
    nav_html = '\n'.join(
        f'''          <div class="footer__col">
            <p class="footer__cat">{t}</p>
            <ul>
''' + '\n'.join(f'              <li><a href="{h}">{esc(x)}</a></li>' for x, h in items) + '''
            </ul>
          </div>''' for t, items in nav)
    legal = ''.join(f'<a href="{root}{s}/">{t}</a>' for t, s in LEGAL_LINKS)
    return f'''<footer class="footer" id="footer">
  <div class="footer__photo" aria-hidden="true"><img src="{root}assets/img/footer/equipo.webp" alt="" width="2200" height="1467" loading="lazy"></div>
  <div class="footer__shade" aria-hidden="true"></div>

  <div class="container footer__hero">
    <h2 class="footer__title" data-split>Más que marketing, creamos <em>sistemas</em> que generan ventas.</h2>
    <a class="btn btn--primary btn--xl" href="{root}contacto/" data-magnetic>
      <span class="btn__txt"><span>Hablemos de tu proyecto</span><span aria-hidden="true">Hablemos de tu proyecto</span></span>
      <span class="btn__ico">{ARROW.format(s=20)}</span>
    </a>
  </div>

  <div class="container footer__links">
    <section class="footer__block footer__block--sol" aria-label="Soluciones" data-reveal>
      <h3 class="footer__h">Soluciones</h3>
      <div class="footer__cols footer__cols--3">
{sol}
      </div>
    </section>
    <nav class="footer__block footer__block--nav" aria-label="Navegación" data-reveal>
      <h3 class="footer__h">Navegación</h3>
      <div class="footer__cols footer__cols--2">
{nav_html}
      </div>
    </nav>
  </div>

  <div class="container footer__bar">
    <div class="footer__brand">
      <img src="{root}assets/img/brand/logo-sam-blanco.png" alt="SÁM digital" width="300" height="116" loading="lazy">
      <p>© <span data-year>2026</span> SÁM digital. Todos los derechos reservados.</p>
    </div>
    <p class="footer__legal">{legal}</p>
    <div class="social">{social()}</div>
  </div>
</footer>'''


def shell(*, title, desc, main, root='', page='inner', nav='', og_image='', extra_js='', base='', robots=''):
    is_home = page == 'home'
    css = f'<link rel="stylesheet" href="{root}assets/css/styles.css?v={ver("assets/css/styles.css")}">'
    if not is_home:
        css += f'\n  <link rel="stylesheet" href="{root}assets/css/pages.css?v={ver("assets/css/pages.css")}">'
    scripts = (f'<script src="{root}assets/vendor/gsap.min.js"></script>\n'
               f'<script src="{root}assets/vendor/ScrollTrigger.min.js"></script>\n'
               f'<script src="{root}assets/vendor/lenis.min.js"></script>\n')
    if not is_home:
        scripts += f'<script src="{root}assets/js/pages.js?v={ver("assets/js/pages.js")}"></script>\n'
    scripts += f'<script src="{root}assets/js/main.js?v={ver("assets/js/main.js")}"></script>'
    fab = FAB.replace('src="assets/', f'src="{root}assets/')
    og = f'\n  <meta property="og:image" content="{qa(og_image)}">' if og_image else ''
    base_tag = f'\n  <base href="{base}">' if base else ''
    robots_tag = f'\n  <meta name="robots" content="{robots}">' if robots else ''
    return f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">{base_tag}
  <title>{esc(title)}</title>
  <meta name="description" content="{qa(desc)}">{robots_tag}
  <meta name="theme-color" content="#06304C">
  <meta property="og:title" content="{qa(title)}">
  <meta property="og:description" content="{qa(desc)}">
  <meta property="og:type" content="website">{og}
  <link rel="icon" href="{root}assets/img/brand/favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:ital,wght@0,400;0,500;0,700;0,800;0,900;1,700;1,800;1,900&family=Quicksand:wght@400;500;600;700&family=Poppins:wght@600;700&display=swap" rel="stylesheet">
  {css}
</head>
<body data-page="{page}" data-nav="{nav}">

{CHROME}

{header(root, is_home)}
{main}

{footer(root, is_home)}

{fab}

{scripts}
</body>
</html>
'''


# ───────────────────────── Bloques de página reutilizables ─────────────────────────
def crumbs(items):
    out = []
    for i, (label, href) in enumerate(items):
        if href and i < len(items) - 1:
            out.append(f'<a href="{href}">{esc(label)}</a>')
        else:
            out.append(f'<span aria-current="page">{esc(label)}</span>')
    return '<nav class="crumbs" data-hero-in aria-label="Ruta de navegación">' + '<i>/</i>'.join(out) + '</nav>'


def hero(*, crumb, title_html, lead='', ctas='', visual='', cls='', scroll_to='#contenido'):
    lead_html = f'\n        <p class="hero__lead" data-hero-in>{lead}</p>' if lead else ''
    cta_html = f'\n        <div class="hero__cta" data-hero-in>{ctas}</div>' if ctas else ''
    return f'''<section class="hero hero--page {cls}">
  <div class="hero__bg" data-hero-bg aria-hidden="true"></div>
  <span class="hero__glow" aria-hidden="true"></span>
  <div class="hero__grid" aria-hidden="true"></div>
  <span class="aurora aurora--a" aria-hidden="true"></span>
  <span class="aurora aurora--b" aria-hidden="true"></span>
  {visual}
  <div class="hero__shade" aria-hidden="true"></div>
  <div class="container hero__inner">
    <div class="hero__copy" data-hero-copy>
      {crumb}
      <h1 class="hero__title" data-split>{title_html}</h1>{lead_html}{cta_html}
    </div>
  </div>
  <a class="hero__scroll" href="{scroll_to}" aria-label="Desliza para ver más"><span class="hero__mouse"><i></i></span><span>Desliza</span></a>
  <span class="hero__dim" aria-hidden="true"></span>
</section>'''


def rings():
    return '<i class="hv__rings" aria-hidden="true"></i>'


def cta_section(root='../'):
    """Bloque 'Hablemos de tu proyecto' del Home (mismo diseño), apuntando al WhatsApp del sitio actual."""
    m = re.search(r'<section class="cta section" id="contacto">.*?</section>', HOME, re.S)
    block = m.group(0)
    # en páginas internas es la sección de cierre
    return block.replace('id="contacto"', 'id="hablemos"').replace('src="assets/', f'src="{root}assets/')


def related(current):
    others = [s for s in ORDER if s != current]
    i = ORDER.index(current)
    pick = [ORDER[(i + k) % len(ORDER)] for k in (1, 2, 3)]
    cards = '\n'.join(scard(s, small=True) for s in pick)
    return f'''<section class="section section--light psec s-related">
  <span class="aurora aurora--o aurora--o2" aria-hidden="true"></span>
  <div class="container">
    <div class="s-related__head">
      <div>
        <p class="eyebrow"><span></span>Más soluciones</p>
        <h2 class="h2" data-split>Otras <em>soluciones</em> que trabajan contigo</h2>
      </div>
      {btn('Ver todas las soluciones', '../services/', 'btn--dark', 'btn__ico--orange', reveal=True)}
    </div>
    <div class="sgrid sgrid--3">
{cards}
    </div>
  </div>
</section>'''


def scard(slug, small=False):
    c = CARD[slug]
    ico = SHORT[slug][2]
    root = '../'
    return f'''      <a class="scard" href="{root}{slug}/" data-reveal data-cursor="view" data-cursor-label="Ver">
        <span class="scard__ico"><img src="{root}assets/img/services/{ico}.png" alt="" width="194" height="174" loading="lazy"></span>
        <b class="scard__t">{esc(c['title'])}</b>
        <span class="scard__d">{esc(c['desc'])}</span>
        <i class="scard__go">{ARROW_UR.format(s=18)}</i>
      </a>'''


# ───────────────────────── Páginas de servicio ─────────────────────────
def blocks_html(blocks):
    out, first = [], True
    for b in blocks:
        if 'p' in b:
            cls = ' class="lead-p"' if first else ''
            out.append(f'<p{cls} data-reveal>{esc(b["p"])}</p>')
            first = False
        elif 'ul' in b:
            out.append('<ul class="checks" data-reveal>' + ''.join(f'<li>{CHECK}<span>{esc(i)}</span></li>' for i in b['ul']) + '</ul>')
    return '\n      '.join(out)


def service_page(slug):
    sv = SV['pages'][slug]
    root = '../'
    img1 = f'{root}assets/img/servicios/{slug}-1.webp'
    img2 = f'{root}assets/img/servicios/{slug}-2.webp'
    short = SHORT[slug][0]
    # título del hero: H1 (+ acento si hay H2 y párrafo)
    if sv['sub_h2'] and sv['sub_p']:
        title = f'{esc(sv["h1"])} <em>{esc(sv["sub_h2"])}</em>'
        lead = esc(sv['sub_p'])
    else:
        title = esc(sv['h1'])
        lead = esc(sv['sub_p'] or sv['sub_h2'])
    ico = SHORT[slug][2]
    visual = f'''<div class="hero__visual" data-hero-visual>
    <span class="hv__disc" aria-hidden="true"></span>{rings()}
    <img class="hv__img hv__img--main" data-depth="26" src="{img1}" alt="Ilustración de {qa(short.lower())}" width="800" height="732" fetchpriority="high">
    <span class="hv__chip" data-depth="-34"><img src="{root}assets/img/services/{ico}.png" alt="" width="64" height="58"><b>{esc(short)}</b></span>
  </div>'''
    ctas = (btn(sv['cta'], WA, 'btn--primary btn--lg', ext=True) +
            f'<a class="btn btn--ghost btn--lg" href="{root}services/" data-magnetic><span class="btn__txt"><span>Ver soluciones</span><span aria-hidden="true">Ver soluciones</span></span><span class="btn__ico btn__ico--ghost">{ARROW.format(s=18)}</span></a>')
    h = hero(crumb=crumbs([('Inicio', root), ('Soluciones', root + 'services/'), (sv['h1'], None)]),
             title_html=title, lead=lead, ctas=ctas, visual=visual, cls='hero--service')

    # 1 · intro
    intro = f'''<section class="section section--light psec sheet s-intro" id="contenido">
  <span class="aurora aurora--o aurora--o1" aria-hidden="true"></span>
  <div class="container s-intro__grid">
    <div class="s-intro__copy">
      <p class="eyebrow"><span></span>{esc(short)}</p>
      <h2 class="h2 h2--lg" data-split>{esc(sv['intro']['h2'])}</h2>
      {blocks_html(sv['intro']['blocks'])}
      {btn(sv['cta'], WA, 'btn--dark', 'btn__ico--orange', ext=True, reveal=True)}
    </div>
    <div class="s-intro__media" data-reveal>
      <div class="stage">
        <i class="stage__rings" aria-hidden="true"></i>
        <img src="{img2}" alt="Ilustración complementaria de {qa(short.lower())}" width="800" height="732" loading="lazy">
      </div>
    </div>
  </div>
</section>'''

    # 2 · por qué
    wb = sv['why']['blocks']
    statement = wb[0]['p'] if wb and 'p' in wb[0] and len(wb) > 1 else ''
    ul = next((b['ul'] for b in wb if 'ul' in b), [])
    closing = wb[-1]['p'] if len(wb) > 1 and 'p' in wb[-1] and 'ul' in wb[-2:-1][0] else ''
    if not statement and wb and 'p' in wb[0] and 'ul' not in wb[0]:
        statement = wb[0]['p']
    items = ''.join(f'<li class="why-item" data-reveal><b>{i + 1:02d}</b><span>{esc(t)}</span></li>' for i, t in enumerate(ul))
    st_html = f'<p class="lead-p" data-reveal>{esc(statement)}</p>' if statement else ''
    cl_html = f'<p class="callout" data-reveal>{esc(closing)}</p>' if closing else ''
    why = f'''<section class="section section--dark psec s-why">
  <span class="aurora aurora--c" aria-hidden="true"></span>
  <div class="container s-why__grid">
    <div class="s-why__head">
      <p class="eyebrow eyebrow--dark"><span></span>{esc(short)}</p>
      <h2 class="h2" data-split>{esc(sv['why']['h2'])}</h2>
      {btn(sv['cta'], WA, 'btn--primary', ext=True, reveal=True)}
    </div>
    <div class="s-why__body">
      {st_html}
      <ul class="why-list">{items}</ul>
      {cl_html}
    </div>
  </div>
</section>'''

    # 3 · pasos (tarjetas apiladas con sticky)
    n = len(sv['steps']['items'])
    cards = '\n'.join(
        f'''      <li class="step-card step-card--{(i % 5) + 1}" style="--i:{i}">
        <span class="step-card__n">{i + 1:02d}</span>
        <div class="step-card__txt"><h3>{esc(it['t'])}</h3><p>{esc(it['d'])}</p></div>
        <i class="step-card__rings" aria-hidden="true"></i>
      </li>''' for i, it in enumerate(sv['steps']['items']))
    steps = f'''<section class="section section--light psec-tall s-steps" data-steps="{n}">
  <span class="aurora aurora--o aurora--o3" aria-hidden="true"></span>
  <div class="container s-steps__grid">
    <div class="s-steps__head">
      <p class="eyebrow"><span></span>{esc(short)}</p>
      <h2 class="h2" data-split>{esc(sv['steps']['h2'])}</h2>
      <p class="s-steps__count" aria-hidden="true"><b data-steps-cur>01</b> / {n:02d}</p>
      <div class="s-steps__bar" aria-hidden="true"><i data-steps-bar></i></div>
    </div>
    <ol class="s-steps__list">
{cards}
    </ol>
  </div>
</section>'''

    # 4 · beneficios
    ben_items = '\n'.join(
        f'''      <article class="ben ben--{i + 1}" data-reveal>
        <b class="ben__n">{i + 1:02d}</b>
        <h3>{esc(it['t'])}</h3>
        <p>{esc(it['d'])}</p>
      </article>''' for i, it in enumerate(sv['benefits']['items']))
    ben = f'''<section class="section section--dark stats-bg psec s-ben">
  <span class="aurora aurora--d" aria-hidden="true"></span>
  <div class="container">
    <div class="s-ben__head">
      <div>
        <p class="eyebrow eyebrow--dark"><span></span>{esc(short)}</p>
        <h2 class="h2" data-split>{esc(sv['benefits']['h2'])}</h2>
      </div>
      {btn(sv['cta'], WA, 'btn--primary', ext=True, reveal=True)}
    </div>
    <div class="s-ben__grid">
{ben_items}
    </div>
  </div>
</section>'''

    main = f'<main id="main">\n{h}\n{intro}\n{why}\n{steps}\n{ben}\n{related(slug)}\n{cta_section()}\n</main>'
    return shell(title=f'{sv["h1"]} · SÁM digital', desc=(sv['sub_p'] or sv['sub_h2']) + ' ' + short + ' · SÁM digital.',
                 main=main, root=root, nav='soluciones', og_image='')


# ───────────────────────── Índice de soluciones ─────────────────────────
def services_page():
    root = '../'
    orbit = ''.join(
        f'<span class="orb orb--{i + 1}" data-depth="{(-1) ** i * (14 + i * 4)}"><img src="{root}assets/img/services/{SHORT[s][2]}.png" alt="" width="194" height="174"></span>'
        for i, s in enumerate(ORDER))
    visual = f'<div class="hero__visual hero__visual--orbit" data-hero-visual><span class="hv__disc" aria-hidden="true"></span>{rings()}{orbit}</div>'
    h = hero(crumb=crumbs([('Inicio', root), ('Soluciones', None)]),
             title_html='Nuestras <em>soluciones</em>',
             lead='Nueve soluciones que trabajan juntas: de atraer al cliente ideal a convertirlo y fidelizarlo.',
             ctas=btn('Hablemos de tu proyecto', root + 'contacto/', 'btn--primary btn--lg'),
             visual=visual, cls='hero--index')
    cards = '\n'.join(scard(s) for s in ORDER)
    grid = f'''<section class="section section--light psec sheet s-grid" id="contenido">
  <span class="aurora aurora--o aurora--o1" aria-hidden="true"></span>
  <span class="aurora aurora--o aurora--o2" aria-hidden="true"></span>
  <div class="container">
    <div class="sgrid">
{cards}
    </div>
  </div>
</section>'''
    main = f'<main id="main">\n{h}\n{grid}\n{cta_section()}\n</main>'
    return shell(title='Nuestras soluciones · SÁM digital',
                 desc='Generación de leads, marketing estratégico, social media, diseño web, SEO, publicidad paga, email marketing, diseño gráfico y branding.',
                 main=main, root=root, nav='soluciones')


# ───────────────────────── Nosotros ─────────────────────────
def about_page():
    root = '../'
    a = ABOUT
    h1 = ' '.join(a['h1'].split()).capitalize()  # "SOBRE NOSOTROS" -> "Sobre nosotros"
    photos = [('a-team', 'Equipo creativo trabajando junto', 'hp--1', 22), ('d-laptop', 'Mujer trabajando con un laptop', 'hp--2', -28), ('e-social', 'Celular con redes sociales', 'hp--3', 36)]
    ph = ''.join(f'<figure class="hp {c}" data-depth="{d}"><img src="{root}assets/img/about/{f}.webp" alt="{qa(al)}" width="900" height="600"></figure>' for f, al, c, d in photos)
    visual = f'''<div class="hero__visual hero__visual--photos" data-hero-visual>
    <span class="hv__disc" aria-hidden="true"></span>{rings()}{ph}
    <div class="hp hp--stat" data-depth="-30"><b>15+</b><span>años de experiencia</span></div>
  </div>'''
    h = hero(crumb=crumbs([('Inicio', root), ('Nosotros', None)]), title_html=esc(h1),
             lead=esc(a['h2']), ctas=btn('Hablemos de tu proyecto', root + 'contacto/', 'btn--primary btn--lg'),
             visual=visual, cls='hero--about')
    mosaic = re.search(r'<div class="mosaic" data-mosaic>.*?\n      </div>', HOME, re.S).group(0).replace('assets/', root + 'assets/')
    stmt = f'''<section class="section section--light psec sheet s-about" id="contenido">
  <span class="aurora aurora--o aurora--o1" aria-hidden="true"></span>
  <span class="aurora aurora--o aurora--o2" aria-hidden="true"></span>
  <div class="container">
    <p class="eyebrow"><span></span>Sobre nosotros</p>
    <h2 class="about__big" data-scrub>{esc(a['h2'])}</h2>
    <div class="s-about__grid">
      <p class="lead-p s-about__p" data-reveal>{esc(a['intro'])}</p>
      {mosaic}
    </div>
  </div>
</section>'''
    mv = f'''<section class="section section--dark psec s-mv">
  <span class="aurora aurora--c" aria-hidden="true"></span>
  <div class="container">
    <div class="mv__grid">
      <article class="mv mv--1" data-reveal>
        <i class="mv__rings" aria-hidden="true"></i>
        <span class="mv__n">01</span>
        <h3>{esc(a['mision']['t'])}</h3>
        <p>{esc(a['mision']['d'])}</p>
      </article>
      <article class="mv mv--2" data-reveal>
        <i class="mv__rings" aria-hidden="true"></i>
        <span class="mv__n">02</span>
        <h3>{esc(a['vision']['t'])}</h3>
        <p>{esc(a['vision']['d'])}</p>
      </article>
    </div>
  </div>
</section>'''
    stats = re.search(r'<section class="stats section section--dark".*?</section>', HOME, re.S).group(0)
    ally = f'''<section class="section section--light psec s-ally">
  <span class="aurora aurora--o aurora--o3" aria-hidden="true"></span>
  <div class="container s-ally__inner">
    <p class="eyebrow"><span></span>SÁM digital</p>
    <p class="s-ally__big" data-scrub>{esc(a['aliado'])}</p>
    {btn('Hablemos de tu proyecto', root + 'contacto/', 'btn--dark', 'btn__ico--orange', reveal=True)}
  </div>
</section>'''
    main = f'<main id="main">\n{h}\n{stmt}\n{mv}\n{stats}\n{ally}\n{cta_section()}\n</main>'
    return shell(title='Nosotros · SÁM digital', desc=a['h2'] + '. ' + a['intro'][:120], main=main, root=root, nav='nosotros')


# ───────────────────────── Portafolio ─────────────────────────
PORT_WEB = [
    ('OCTOPUS CONTENEDOR', 'Tienda virtual de artículos para dropshipping', 'octopus', 'https://octopuscontenedor.com/'),
    ('TAPETES Y PISOS DEL PACÍFICO', 'Especialistas en productos para decoración de interiores', 'tapetes', 'https://tapetesypisos.com.co/'),
    ('ASOCLICPER', 'Asociación Colombiana de Clínicas de Cirugía Plástica Estética y Reconstructiva', 'asoclicper', 'https://asoclicper.com/'),
    ('VOLCALI', 'Servicio profesional especializado en automóviles marca VOLVO', 'volcali', 'https://asoclicper.com/'),
    ('EC&R', 'Especialistas en color y Recubrimientos', 'ecyr', 'https://especialistascyr.com/'),
    ('INNOVA SYSTEMS', 'Especialistas en Gestión Documental Empresarial', 'innova', 'https://innova.com.co/wp/'),
    ('CLÍNICA PICASSO', 'Clínica de cirugía plástica y estética en Cali', 'picasso', 'https://clinicapicassocali.com/'),
    ('MAÑANITAS NATURALMENTE', 'Lotes campestres ubicados en el eje cafetero', 'mananitas', 'https://lasmananitasnaturalmente.com/'),
    ('DOCUNET WEB', 'Software de Gestión de Documentos y Procesos', 'docunet', 'https://docunetweb.com.co/'),
]
PORT_BRAND = [
    ('DIPA', 'brand-dipa', '../assets/pdf/brandboard-dipa.pdf'),
    ('CALA IMPACT', 'brand-cala', '../assets/pdf/manual-de-marca-cala-impact.pdf'),
    ('OCTOPUS CONTENEDOR', 'octopus', '../assets/pdf/manual-de-marca-octopus.pdf'),
    ('TRONOX', 'brand-tronox', '../assets/pdf/brandboard-tronox.pdf'),
]


NICE = {'OCTOPUS CONTENEDOR': 'Octopus Contenedor', 'TAPETES Y PISOS DEL PACÍFICO': 'Tapetes y Pisos del Pacífico', 'ASOCLICPER': 'Asoclicper',
        'VOLCALI': 'Volcali', 'EC&R': 'EC&R', 'INNOVA SYSTEMS': 'Innova Systems', 'CLÍNICA PICASSO': 'Clínica Picasso',
        'MAÑANITAS NATURALMENTE': 'Mañanitas Naturalmente', 'DOCUNET WEB': 'Docunet Web', 'DIPA': 'Dipa', 'CALA IMPACT': 'Cala Impact', 'TRONOX': 'Tronox'}


def pf_alt(cat, name, desc):
    kind = 'Diseño web' if cat == 'web' else 'Identidad de marca'
    return f'{kind} de {NICE.get(name, name)}' + (f'. {desc}' if desc else '')


def pf_card(cat, name, desc, img, href, label):
    d = f'<span class="pf__d">{esc(desc)}</span>' if desc else ''
    return f'''        <a class="pf" data-cat="{cat}" href="{href}" target="_blank" rel="noopener" data-cursor="view" data-cursor-label="{qa(label)}">
          <span class="pf__img"><img src="../assets/img/work/{img}.webp" alt="{qa(pf_alt(cat, name, desc))}" width="1200" height="800" loading="lazy"></span>
          <span class="pf__meta"><b class="pf__t">{esc(name)}</b>{d}</span>
          <span class="pf__cta">{esc(label)}<i>{ARROW_UR.format(s=16)}</i></span>
        </a>'''


def portfolio_page():
    root = '../'
    wall = re.search(r'<div class="wall" data-wall aria-hidden="true">.*?\n  </div>\n  <div class="hero__shade"', HOME, re.S).group(0)
    wall = wall[:wall.rindex('  <div class="hero__shade"')].replace('assets/', root + 'assets/')
    h = hero(crumb=crumbs([('Inicio', root), ('Portafolio', None)]), title_html='Nuestro <em>Portafolio</em>',
             ctas=btn('Hablemos de tu proyecto', root + 'contacto/', 'btn--primary btn--lg'), visual=wall, cls='hero--portfolio')
    tabs = [('web', 'Diseño web'), ('branding', 'Branding'), ('grafico', 'Diseño gráfico'), ('video', 'Edición de video')]
    tab_html = ''.join(f'<button class="ptab{" is-on" if i == 0 else ""}" type="button" role="tab" aria-selected="{"true" if i == 0 else "false"}" data-tab="{k}">{esc(t)}</button>' for i, (k, t) in enumerate(tabs))
    cards = '\n'.join(pf_card('web', n, d, i, u, 'Ver sitio web') for n, d, i, u in PORT_WEB)
    cards += '\n' + '\n'.join(pf_card('branding', n, '', i, u, 'Ver más') for n, i, u in PORT_BRAND)
    grid = f'''<section class="section section--light psec sheet s-port" id="contenido">
  <span class="aurora aurora--o aurora--o1" aria-hidden="true"></span>
  <span class="aurora aurora--o aurora--o2" aria-hidden="true"></span>
  <div class="container">
    <div class="ptabs" role="tablist" aria-label="Categorías del portafolio" data-reveal>{tab_html}<i class="ptabs__bar" aria-hidden="true"></i></div>
    <div class="pgrid" data-pgrid>
{cards}
    </div>
    <p class="pempty" data-pempty hidden>Pronto publicaremos nuevos proyectos en esta categoría.</p>
  </div>
</section>'''
    main = f'<main id="main">\n{h}\n{grid}\n{cta_section()}\n</main>'
    return shell(title='Nuestro Portafolio · SÁM digital',
                 desc='Proyectos de diseño web y branding de SÁM digital: Octopus Contenedor, Tapetes y Pisos del Pacífico, Asoclicper, Clínica Picasso y más.',
                 main=main, root=root, nav='portafolio')


# ───────────────────────── Contacto ─────────────────────────
def contact_page():
    root = '../'
    visual = f'''<div class="hero__visual hero__visual--contact" data-hero-visual>
    <span class="hv__disc" aria-hidden="true"></span>{rings()}
    <div class="cc cc--1" data-depth="26"><span class="cc__ico"><svg width="22" height="22"><use href="#i-wa"/></svg></span><b>WhatsApp</b><small>Respuesta directa</small></div>
    <div class="cc cc--2" data-depth="-24"><span class="cc__ico cc__ico--o"><svg width="22" height="22"><use href="#i-support"/></svg></span><b>Escríbenos</b><small>{EMAIL}</small></div>
    <div class="cc cc--3" data-depth="40"><span class="cc__ico cc__ico--b"><svg width="22" height="22"><use href="#i-spark"/></svg></span><b>Consultoría gratis</b><small>30 minutos</small></div>
  </div>'''
    h = hero(crumb=crumbs([('Inicio', root), ('Contacto', None)]), title_html='Contáctanos',
             ctas=btn('Contáctanos por whatsapp', WA, 'btn--primary btn--lg', ext=True), visual=visual, cls='hero--contact')
    form = f'''<section class="section section--light psec sheet s-contact" id="contenido">
  <span class="aurora aurora--o aurora--o1" aria-hidden="true"></span>
  <span class="aurora aurora--o aurora--o2" aria-hidden="true"></span>
  <div class="container s-contact__grid">
    <div class="s-contact__side">
      <p class="eyebrow"><span></span>Contacto</p>
      <h2 class="h2 h2--lg" data-split>Escríbenos</h2>
      <ul class="cinfo" data-reveal>
        <li><span class="cinfo__ico"><svg width="20" height="20"><use href="#i-wa"/></svg></span><span><small>WhatsApp</small><a href="{WA}" target="_blank" rel="noopener">Contáctanos por whatsapp</a></span></li>
        <li><span class="cinfo__ico cinfo__ico--o"><svg width="20" height="20"><use href="#i-arrow-ur"/></svg></span><span><small>Correo</small><a href="mailto:{EMAIL}">{EMAIL}</a></span></li>
      </ul>
      <div class="social social--dark" data-reveal>{social()}</div>
    </div>
    <form class="cform" data-form novalidate data-reveal>
      <div class="cform__row">
        <label class="fld"><input type="text" name="nombre" placeholder=" " autocomplete="name"><span>Nombre Completo</span></label>
        <label class="fld"><input type="email" name="email" placeholder=" " autocomplete="email" required><span>Correo Electrónico</span></label>
      </div>
      <div class="cform__row">
        <label class="fld"><input type="tel" name="telefono" placeholder=" " autocomplete="tel" required><span>Teléfono</span></label>
        <label class="fld"><input type="text" name="empresa" placeholder=" " autocomplete="organization"><span>Nombre de empresa (opcional)</span></label>
      </div>
      <label class="fld fld--area"><textarea name="mensaje" rows="5" placeholder=" "></textarea><span>Mensaje</span></label>
      <label class="chk"><input type="checkbox" name="acepto" required><i aria-hidden="true">{CHECK}</i><span>Acepto el <a href="{root}aviso-legal/">Aviso Legal</a> y la <a href="{root}politica-de-privacidad/">Política de Privacidad</a>.</span></label>
      <p class="cform__err" data-form-err role="alert" hidden></p>
      <button class="btn btn--primary btn--xl cform__btn" type="submit" data-magnetic><span class="btn__txt"><span>Enviar</span><span aria-hidden="true">Enviar</span></span><span class="btn__ico">{ARROW.format(s=20)}</span></button>
      <div class="cform__ok" data-form-ok hidden>
        <b>¡Gracias por escribirnos!</b>
        <p>Abrimos WhatsApp con tu mensaje listo para enviar. Si no se abrió, <a href="{WA}" target="_blank" rel="noopener">contáctanos por whatsapp</a>.</p>
      </div>
    </form>
  </div>
</section>'''
    main = f'<main id="main">\n{h}\n{form}\n</main>'
    return shell(title='Contacto · SÁM digital', desc='Contáctanos: escríbenos o habla con un especialista de SÁM digital por WhatsApp.', main=main, root=root, nav='contacto')


# ───────────────────────── Blog ─────────────────────────
def post_card(p, root='../', big=False):
    return f'''      <a class="bcard{' bcard--big' if big else ''}" href="{root}{p['slug']}/" data-reveal data-cursor="view" data-cursor-label="Leer">
        <span class="bcard__img"><img src="{root}assets/img/blog/{local_img(p['image'])}" alt="" width="1200" height="800" loading="lazy"></span>
        <small class="bcard__tag">{esc(p['cat'])}</small>
        <b class="bcard__t">{esc(p['title'])}</b>
        <time class="bcard__d" datetime="{p['iso']}">{esc(p['date'])}</time>
      </a>'''


def blog_page():
    root = '../'
    posts = sorted(POSTS, key=lambda p: p['iso'], reverse=True)
    covers = ''.join(f'<figure class="hp hp--p{i + 1}" data-depth="{d}"><img src="{root}assets/img/blog/{local_img(p["image"])}" alt="" width="1200" height="800"><figcaption>{esc(p["cat"])}</figcaption></figure>'
                     for i, (p, d) in enumerate(zip(posts, (26, -30, 38))))
    visual = f'<div class="hero__visual hero__visual--photos hero__visual--blog" data-hero-visual><span class="hv__disc" aria-hidden="true"></span>{rings()}{covers}</div>'
    h = hero(crumb=crumbs([('Inicio', root), ('Blog', None)]), title_html='Blog', lead='Últimas noticias',
             ctas=btn('Hablemos de tu proyecto', root + 'contacto/', 'btn--primary btn--lg'), visual=visual, cls='hero--blog')
    cards = '\n'.join(post_card(p, root, big=(i == 0)) for i, p in enumerate(posts))
    grid = f'''<section class="section section--light psec sheet s-blog" id="contenido">
  <span class="aurora aurora--o aurora--o1" aria-hidden="true"></span>
  <span class="aurora aurora--o aurora--o3" aria-hidden="true"></span>
  <div class="container">
    <div class="bgrid">
{cards}
    </div>
  </div>
</section>'''
    main = f'<main id="main">\n{h}\n{grid}\n{cta_section()}\n</main>'
    return shell(title='Blog · SÁM digital', desc='Últimas noticias de marketing digital: tendencias, estrategia y consejos de SÁM digital.', main=main, root=root, nav='blog')


# Limpieza del HTML de los artículos: solo etiquetas de contenido, sin estilos ni clases de Elementor/WordPress
ALLOWED = {'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'b', 'i', 'a', 'img', 'blockquote', 'br', 'figure', 'figcaption', 'hr'}


def slugify(t):
    t = t.lower()
    for a, b in zip('áéíóúüñ', 'aeiouun'):
        t = t.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:50] or 'seccion'


def clean_article(raw, root):
    from lxml import html as LH
    wrap = LH.fragment_fromstring(raw, create_parent='div')
    for el in list(wrap.iter()):
        if not isinstance(el.tag, str):
            continue
        if el.tag not in ALLOWED and el is not wrap:
            el.drop_tag()
    toc, used = [], set()
    for el in wrap.iter():
        if not isinstance(el.tag, str):
            continue
        keep = {}
        if el.tag == 'a' and el.get('href'):
            keep = {'href': el.get('href'), 'target': '_blank', 'rel': 'noopener'}
        elif el.tag == 'img':
            src = el.get('src') or ''
            keep = {'src': src, 'alt': el.get('alt') or '', 'loading': 'lazy'}
            if '/uploads/' in src:
                keep['src'] = root + 'assets/img/blog/' + local_img(src)
        for k in list(el.attrib):
            del el.attrib[k]
        el.attrib.update(keep)
        if el.tag == 'h2':
            txt = ' '.join(el.text_content().split())
            sid = slugify(txt)
            while sid in used:
                sid += '-2'
            used.add(sid)
            el.set('id', sid)
            toc.append((sid, txt))
    for p in wrap.xpath('.//p'):
        if not p.text_content().strip() and not p.xpath('.//img'):
            p.getparent().remove(p)
    body = LH.tostring(wrap, encoding='unicode')
    body = re.sub(r'^<div>|</div>$', '', body.strip())
    return body, toc


def post_page(p):
    root = '../'
    body, toc = clean_article(p['content'], root)
    toc_html = ''.join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)
    h = f'''<section class="hero hero--page hero--post">
  <div class="hero__bg hero__bg--photo" aria-hidden="true"><img src="{root}assets/img/blog/{local_img(p['image'])}" alt="" width="1200" height="800"></div>
  <span class="hero__glow" aria-hidden="true"></span>
  <div class="hero__grid" aria-hidden="true"></div>
  <div class="hero__shade hero__shade--post" aria-hidden="true"></div>
  <div class="container hero__inner">
    <div class="hero__copy hero__copy--wide" data-hero-copy>
      {crumbs([('Inicio', root), ('Blog', root + 'blog/'), ('Artículo', None)])}
      <p class="post-meta" data-hero-in><span class="chip"><i></i>{esc(p['cat'])}</span><time datetime="{p['iso']}">{esc(p['date'])}</time></p>
      <h1 class="hero__title hero__title--post" data-split>{esc(p['title'])}</h1>
    </div>
  </div>
  <span class="hero__dim" aria-hidden="true"></span>
</section>'''
    others = [x for x in sorted(POSTS, key=lambda q: q['iso'], reverse=True) if x['slug'] != p['slug']][:2]
    rel = '\n'.join(post_card(x, root) for x in others)
    art = f'''<section class="section section--light psec-tall sheet s-article" id="contenido">
  <span class="aurora aurora--o aurora--o1" aria-hidden="true"></span>
  <div class="container doc">
    <aside class="doc__toc" aria-label="En este artículo">
      <p class="doc__toc-t">En este artículo</p>
      <ol>{toc_html}</ol>
    </aside>
    <article class="prose">
{body}
    </article>
  </div>
</section>
<section class="section section--light psec s-related s-related--posts">
  <div class="container">
    <div class="s-related__head">
      <div>
        <p class="eyebrow"><span></span>Blog</p>
        <h2 class="h2" data-split>Más <em>publicaciones</em></h2>
      </div>
      {btn('Ver el blog', root + 'blog/', 'btn--dark', 'btn__ico--orange', reveal=True)}
    </div>
    <div class="bgrid bgrid--2">
{rel}
    </div>
  </div>
</section>'''
    main = f'<main id="main">\n{h}\n{art}\n{cta_section()}\n</main>'
    return shell(title=f'{p["title"]} · SÁM digital', desc=re.sub(r'<[^>]+>', '', body)[:155].strip(), main=main, root=root, nav='blog')


# ───────────────────────── Legales ─────────────────────────
def legal_page(slug):
    root = '../'
    lg = LEGAL[slug]
    parts_html, toc, used = [], [], set()
    for part in lg['parts']:
        if 'h' in part:
            sid = slugify(part['h'])
            while sid in used:
                sid += '-2'
            used.add(sid)
            toc.append((sid, part['h']))
            parts_html.append(f'<h2 id="{sid}">{esc(part["h"])}</h2>')
        elif 'p' in part:
            txt = esc(part['p']).replace('\n', '<br>')
            txt = re.sub(rf'({re.escape(EMAIL)})', rf'<a href="mailto:\1">\1</a>', txt)
            parts_html.append(f'<p>{txt}</p>')
        elif 'ul' in part:
            parts_html.append('<ul>' + ''.join(f'<li>{esc(i)}</li>' for i in part['ul']) + '</ul>')
    toc_html = ''.join(f'<li><a href="#{i}">{esc(re.sub(r"^\d+\.\s*", "", t)).capitalize()}</a></li>' for i, t in toc)
    h = hero(crumb=crumbs([('Inicio', root), (lg['title'], None)]), title_html=esc(lg['title']), cls='hero--compact', scroll_to='#contenido')
    other = ''.join(f'<a href="{root}{s}/">{t}</a>' for t, s in LEGAL_LINKS if s != slug)
    doc = f'''<section class="section section--light psec-tall sheet s-legal" id="contenido">
  <span class="aurora aurora--o aurora--o1" aria-hidden="true"></span>
  <div class="container doc">
    <aside class="doc__toc" aria-label="Contenido">
      <p class="doc__toc-t">Contenido</p>
      <ol>{toc_html}</ol>
      <p class="doc__toc-t doc__toc-t--sp">Otros documentos</p>
      <div class="doc__links">{other}</div>
    </aside>
    <article class="prose">
{chr(10).join(parts_html)}
    </article>
  </div>
</section>'''
    main = f'<main id="main">\n{h}\n{doc}\n</main>'
    return shell(title=f'{lg["title"]} · SÁM digital', desc=f'{lg["title"]} de SÁM digital.', main=main, root=root, nav='')


# ───────────────────────── SEO, 404 y sitemap ─────────────────────────
POST_BY_SLUG = {p['slug']: p for p in POSTS}
ORG_ID = SITE + '/#organization'
WEB_ID = SITE + '/#website'
LOGO = SITE + '/assets/img/brand/favicon.png'
SOCIAL = ['https://www.facebook.com/profile.php?id=61582248838081', 'https://www.instagram.com/samdigital_mkt/',
          'https://www.linkedin.com/company/s%C3%A1m-digital/']
PAGE_TYPE = {'services/': 'CollectionPage', 'portafolio/': 'CollectionPage', 'blog/': 'CollectionPage',
             'sobre-nosotros/': 'AboutPage', 'contacto/': 'ContactPage'}
CRUMB_NAME = {'services/': 'Soluciones', 'sobre-nosotros/': 'Nosotros', 'portafolio/': 'Portafolio', 'contacto/': 'Contacto', 'blog/': 'Blog'}


def apply_meta(rel, html):
    # Título y descripción de src/data/seo.json (límites para Google: título ≤ 60, descripción 110–160)
    m = SEO[rel]                      # si falta una página, el build falla
    t, d = m['title'], m['description']
    assert len(t) <= 60 and 110 <= len(d) <= 160, (rel, len(t), len(d))
    for pat, new in ((r'<title>.*?</title>', f'<title>{esc(t)}</title>'),
                     (r'<meta name="description" content=".*?">', f'<meta name="description" content="{qa(d)}">'),
                     (r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{qa(t)}">'),
                     (r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{qa(d)}">')):
        html, n = re.subn(pat, lambda _: new, html, count=1, flags=re.S)
        assert n == 1, (rel, pat)
    return html


def org_min():
    return {'@type': 'Organization', '@id': ORG_ID, 'name': 'SÁM digital', 'url': SITE + '/',
            'logo': {'@type': 'ImageObject', 'url': LOGO}}


def org_full():
    o = org_min()
    o['logo'].update(width=512, height=512)
    o.update({
        'alternateName': 'SAM Digital',
        'image': SITE + '/assets/img/og/default.jpg',
        'description': 'Agencia creativa de marketing digital: generación de leads, SEO, publicidad paga, diseño web, branding y más.',
        'slogan': 'Más que marketing, creamos sistemas que generan ventas.',
        'email': EMAIL,
        'contactPoint': [{'@type': 'ContactPoint', 'contactType': 'customer service', 'telephone': '+' + WA_NUMBER,
                          'email': EMAIL, 'availableLanguage': 'Spanish'}],
        'sameAs': SOCIAL,
    })
    return o


def crumb_items(rel):
    slug, url = rel.strip('/'), SITE + '/' + rel
    home = ('Inicio', SITE + '/')
    if slug in SV['pages']:
        return [home, ('Soluciones', SITE + '/services/'), (SV['pages'][slug]['h1'], url)]
    if slug in POST_BY_SLUG:
        return [home, ('Blog', SITE + '/blog/'), (POST_BY_SLUG[slug]['title'], url)]
    if rel in CRUMB_NAME:
        return [home, (CRUMB_NAME[rel], url)]
    return [home, (LEGAL[slug]['title'], url)]


def schema_graph(rel):
    # JSON-LD de la página: Organization + WebSite en el Home; migas de pan, tipo de página y entidad propia en las internas
    meta, url, slug = SEO[rel], SITE + '/' + rel, rel.strip('/')
    website = {'@type': 'WebSite', '@id': WEB_ID, 'url': SITE + '/', 'name': 'SÁM digital', 'inLanguage': 'es'}
    page = {'@type': PAGE_TYPE.get(rel, 'WebPage'), '@id': url + '#webpage', 'url': url, 'name': meta['title'],
            'description': meta['description'], 'inLanguage': 'es'}
    if not rel:
        website['publisher'] = {'@id': ORG_ID}
        page['isPartOf'] = {'@id': WEB_ID}
        page['about'] = {'@id': ORG_ID}
        return [org_full(), website, page]
    page['isPartOf'] = website
    page['breadcrumb'] = {'@id': url + '#breadcrumb'}
    crumbs_ld = {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb',
                 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u}
                                     for i, (n, u) in enumerate(crumb_items(rel))]}
    graph = [page, crumbs_ld]
    if slug in SV['pages']:
        sv = SV['pages'][slug]
        page['mainEntity'] = {'@id': url + '#service'}
        graph.append({'@type': 'Service', '@id': url + '#service', 'name': sv['h1'], 'serviceType': SHORT[slug][0],
                      'description': meta['description'], 'url': url, 'provider': org_min()})
    elif slug in POST_BY_SLUG:
        post = POST_BY_SLUG[slug]
        page['mainEntity'] = {'@id': url + '#article'}
        graph.append({'@type': 'BlogPosting', '@id': url + '#article', 'headline': post['title'], 'description': meta['description'],
                      'image': [f'{SITE}/assets/img/og/{slug}.jpg'], 'datePublished': post['iso'], 'dateModified': post['iso'],
                      'author': {'@type': 'Organization', 'name': 'SÁM digital', 'url': SITE + '/'}, 'publisher': org_min(),
                      'mainEntityOfPage': {'@id': url + '#webpage'}, 'articleSection': post['cat'], 'inLanguage': 'es', 'url': url})
    elif rel == 'services/':
        page['mainEntity'] = {'@type': 'ItemList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': SHORT[x][0], 'url': f'{SITE}/{x}/'} for i, x in enumerate(ORDER)]}
    elif rel == 'portafolio/':
        items = [(n, d, i, u) for n, d, i, u in PORT_WEB] + [(n, '', i, '') for n, i, _ in PORT_BRAND]
        els = []
        for k, (n, d, i, u) in enumerate(items):
            w = {'@type': 'CreativeWork', 'name': NICE.get(n, n), 'image': f'{SITE}/assets/img/work/{i}.webp', 'creator': {'@id': ORG_ID}}
            if d: w['description'] = d
            if u: w['url'] = u
            els.append({'@type': 'ListItem', 'position': k + 1, 'item': w})
        page['mainEntity'] = {'@type': 'ItemList', 'itemListElement': els}
    elif rel == 'blog/':
        posts = sorted(POSTS, key=lambda q: q['iso'], reverse=True)
        page['mainEntity'] = {'@type': 'Blog', '@id': url + '#blog', 'name': 'Blog de SÁM digital', 'url': url, 'inLanguage': 'es',
                              'publisher': org_min(),
                              'blogPost': [{'@type': 'BlogPosting', 'headline': q['title'], 'url': f'{SITE}/{q["slug"]}/',
                                            'datePublished': q['iso'], 'image': f'{SITE}/assets/img/og/{q["slug"]}.jpg'} for q in posts]}
    return graph


def ld_script(rel):
    data = json.dumps({'@context': 'https://schema.org', '@graph': schema_graph(rel)}, ensure_ascii=False, separators=(',', ':'))
    return '  <script type="application/ld+json">' + data.replace('</', '<\\/') + '</script>\n'


def seo_tags(key, html):
    """Inserta canonical, og:url/site_name/locale/image y tarjeta de Twitter (antes del favicon).
    `key` es la ruta del archivo generado: 'index.html', 'services/index.html', ..."""
    rel = '' if key == 'index.html' else key[:-len('index.html')]
    html = apply_meta(rel, html)
    slug = rel.strip('/')
    post = POST_BY_SLUG.get(slug)
    url = f'{SITE}/{rel}'
    img = f'{SITE}/assets/img/og/{slug if post else "default"}.jpg'
    alt = post['title'] if post else 'SÁM digital · Agencia de marketing digital'
    tags = [
        f'<link rel="canonical" href="{url}">',
        f'<meta property="og:url" content="{url}">',
        '<meta property="og:site_name" content="SÁM digital">',
        '<meta property="og:locale" content="es_CO">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{qa(alt)}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if post:
        html = html.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="article">', 1)
        tags += [f'<meta property="article:published_time" content="{post["iso"]}">',
                 f'<meta property="article:section" content="{qa(post["cat"])}">']
    marker = '  <link rel="icon"'
    assert marker in html, key
    html = html.replace(marker, '\n'.join('  ' + t for t in tags) + '\n' + marker, 1)
    assert '</head>' in html, key
    return html.replace('</head>', ld_script(rel) + '</head>', 1)


def sitemap_xml(keys):
    rows = []
    for key in keys:
        rel = '' if key == 'index.html' else key[:-len('index.html')]
        post = POST_BY_SLUG.get(rel.strip('/'))
        lastmod = f'<lastmod>{post["iso"]}</lastmod>' if post else ''
        rows.append(f'  <url><loc>{SITE}/{rel}</loc>{lastmod}</url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(rows) + '\n</urlset>\n')


def not_found_page():
    """404.html: el servidor la sirve en cualquier ruta inexistente, por eso usa <base href="/"> (rutas desde la raíz)."""
    visual = ('<div class="hero__visual hero__visual--404" data-hero-visual><span class="hv__disc" aria-hidden="true"></span>'
              f'{rings()}<b class="n404" aria-hidden="true">404</b></div>')
    ctas = (btn('Volver al inicio', './', 'btn--primary btn--lg') +
            '<a class="btn btn--ghost btn--lg" href="services/" data-magnetic><span class="btn__txt"><span>Ver soluciones</span>'
            f'<span aria-hidden="true">Ver soluciones</span></span><span class="btn__ico btn__ico--ghost">{ARROW.format(s=18)}</span></a>')
    h = hero(crumb='<p class="eyebrow" data-hero-in><span></span>Error 404</p>',
             title_html='Esta página no <em>existe</em>',
             lead='Es posible que el enlace haya cambiado o que la dirección esté mal escrita. Te llevamos de vuelta al camino.',
             ctas=ctas, visual=visual, cls='hero--404', scroll_to='#main')
    main = f'<main id="main" tabindex="-1">\n{h}\n</main>'
    html = shell(title='Página no encontrada · SÁM digital',
                 desc='La página que buscas no existe o cambió de dirección.', main=main, root='', page='notfound',
                 base='/', robots='noindex')
    # con <base href="/"> el ancla "#main" saldría de la página: el salto al contenido se resuelve con foco
    return html.replace('<a class="skip" href="#main">', '<a class="skip" href="#main" onclick="event.preventDefault();document.getElementById(\'main\').focus()">', 1)


# ───────────────────────── Home ─────────────────────────
def home_page():
    return shell(title='SÁM digital · Agencia de marketing digital',
                 desc='Más que marketing, creamos sistemas que generan ventas. Agencia creativa de marketing digital: leads, SEO, pauta, diseño web, branding y más.',
                 main=HOME, root='', page='home', nav='inicio')


def main():
    pages = {'index.html': home_page(), 'sobre-nosotros/index.html': about_page(), 'services/index.html': services_page(),
             'portafolio/index.html': portfolio_page(), 'contacto/index.html': contact_page(), 'blog/index.html': blog_page()}
    for s in ORDER:
        pages[f'{s}/index.html'] = service_page(s)
    for p in POSTS:
        pages[f'{p["slug"]}/index.html'] = post_page(p)
    for _, s in LEGAL_LINKS:
        pages[f'{s}/index.html'] = legal_page(s)
    sitemap = sitemap_xml(pages.keys())
    for path, content in pages.items():
        write(path, seo_tags(path, content))
    write('404.html', not_found_page())
    write('sitemap.xml', sitemap)
    print(f'{len(pages)} páginas generadas + 404.html + sitemap.xml')


if __name__ == '__main__':
    main()
