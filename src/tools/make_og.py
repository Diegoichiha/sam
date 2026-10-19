#!/usr/bin/env python3
"""
Genera las imágenes para compartir en redes (og:image, 1200x630) en assets/img/og/.

  default.jpg      → todas las páginas (foto del equipo + logo)
  <slug>.jpg       → una por artículo del blog (su foto + logo)

Uso:  python src/tools/make_og.py     (requiere Pillow)
Se ejecuta a mano cuando cambian las fotos; las imágenes generadas se versionan en el repo.
"""
import json
import os

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
W, H = 1200, 630
NAVY = (6, 48, 76)


def p(*a):
    return os.path.join(ROOT, *a)


def cover(im, w=W, h=H):
    """Escala para cubrir w×h y recorta al centro."""
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def shade(im, horizontal):
    """Degradado azul marino: de izquierda a derecha (portada) o de abajo hacia arriba (artículos)."""
    ov = Image.new('RGBA', (W, H))
    px = ov.load()
    for y in range(H):
        for x in range(W):
            if horizontal:   # opaco hasta el 30 % del ancho y se desvanece hasta el 85 %
                a = 0.95 * min(1.0, max(0.0, 1 - (x / W - 0.30) / 0.55))
            else:
                t = y / H
                a = 0.9 * max(0.0, (t - 0.38) / 0.62) ** 1.2
            px[x, y] = (*NAVY, round(255 * min(a, 1)))
    return Image.alpha_composite(im.convert('RGBA'), ov)


def logo(w):
    lg = Image.open(p('assets', 'img', 'brand', 'logo-sam-blanco.png')).convert('RGBA')
    return lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)


def accent(im, x, y, w=220, h=8):
    """Barra con el degradado naranja de la marca."""
    bar = Image.new('RGBA', (w, h))
    px = bar.load()
    c0, c1 = (255, 185, 77), (230, 122, 31)
    for i in range(w):
        t = i / (w - 1)
        for j in range(h):
            px[i, j] = tuple(round(c0[k] + (c1[k] - c0[k]) * t) for k in range(3)) + (255,)
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=255)
    im.paste(bar, (x, y), mask)


def save(im, name):
    out = p('assets', 'img', 'og')
    os.makedirs(out, exist_ok=True)
    im.convert('RGB').save(os.path.join(out, name), 'JPEG', quality=84, optimize=True, progressive=True)
    print('og/' + name, os.path.getsize(os.path.join(out, name)) // 1024, 'KB')


def main():
    # Portada: foto del equipo, degradado desde la izquierda, logo grande y barra naranja
    im = shade(cover(Image.open(p('assets', 'img', 'footer', 'equipo.webp')).convert('RGB')), horizontal=True)
    lg = logo(380)
    y = (H - lg.height) // 2 - 14
    im.paste(lg, (84, y), lg)
    accent(im, 84, y + lg.height + 30)
    save(im, 'default.jpg')

    # Artículos: su foto, degradado desde abajo y logo pequeño
    for post in json.load(open(p('src', 'data', 'posts.json'), encoding='utf-8')):
        base = os.path.basename(post['image'])
        import re
        base = re.sub(r'-\d+x\d+(?=\.\w+$)', '', base)
        name = os.path.splitext(base)[0].lower() + '.webp'
        src = Image.open(p('assets', 'img', 'blog', name)).convert('RGB')
        im = shade(cover(src), horizontal=False)
        lg = logo(210)
        im.paste(lg, (56, H - lg.height - 48), lg)
        accent(im, W - 56 - 140, H - 48 - 8, 140, 8)
        save(im, post['slug'] + '.jpg')


if __name__ == '__main__':
    main()
