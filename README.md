# SÁM digital · Rediseño del sitio

Propuesta de rediseño de [samdigital.com.co](https://samdigital.com.co/): más impacto visual y de movimiento, manteniendo el branding de la marca y **exactamente los mismos textos** del sitio actual.
Sitio estático (HTML + CSS + JS vanilla) con las 22 páginas generadas desde datos por un script de Python.

```
index.html                       ← Home (generado)
<slug>/index.html                ← 21 páginas internas, con las mismas URL del sitio actual (generadas)
404.html, sitemap.xml            ← página de error y mapa del sitio (generados)
robots.txt, .htaccess            ← para buscadores y servidor (escritos a mano, ver "Producción")
build.py                         ← generador de todas las páginas
src/data/*.json                  ← contenido extraído del sitio actual (servicios, nosotros, legales, artículos)
src/pages/home.html              ← contenido del Home
src/partials/                    ← chrome (cursor, progreso) y botón flotante compartidos
assets/css/styles.css            ← sistema de diseño + estilos del Home
assets/css/pages.css             ← estilos de las páginas internas
assets/js/main.js                ← lo común: cabecera, mega menú, cursor, hero, revelados (+ secciones del Home)
assets/js/pages.js               ← lógica de las internas (pasos apilados, filtro, índice, formulario)
assets/vendor/                   ← GSAP 3.12.5, ScrollTrigger 3.12.5, Lenis 1.1.20 (copias locales)
assets/img/og/                   ← imágenes para compartir en redes (1200×630), generadas con src/tools/make_og.py
assets/img/                      ← logos, iconos, portafolio (work/), blog, servicios y fotos de stock
```

### Páginas

| Ruta | Contenido |
|---|---|
| `/` | Home |
| `/services/` | Nuestras soluciones: órbita con los 9 servicios + tarjetas |
| `/generacion-de-leads/` `/marketing-estrategico/` `/social-media-manager/` `/diseno-de-paginas-web/` `/optimizacion-seo/` `/publicidad-paga/` `/email-marketing/` `/diseno-grafico/` `/branding/` | Páginas de servicio: hero con ilustración, intro, "por qué", proceso (tarjetas apiladas), beneficios, otras soluciones y CTA |
| `/sobre-nosotros/` | Hero de fotos, mosaico, misión y visión, cifras, aliado estratégico |
| `/portafolio/` | Pestañas con filtro animado (Diseño web, Branding, Diseño gráfico, Edición de video) |
| `/contacto/` | Datos de contacto + formulario |
| `/blog/` y 3 artículos | Listado y lectura con índice lateral que resalta la sección visible |
| `/aviso-legal/` `/politica-de-privacidad/` `/politica-de-cookies/` `/declaracion-de-accesibilidad/` | Documentos legales con índice |

Elementos nuevos propuestos (no existen en el sitio actual): órbita de servicios, tarjetas de proceso apiladas con contador, filtro animado del portafolio, índice lateral de lectura, migas de pan y bloque "Otras soluciones".

## Probar en local

```bash
python build.py                      # regenera index.html y las carpetas de cada página
npx http-server . -p 5190 -c-1       # servidor local
```

Para cambiar un texto: editar el JSON de `src/data/` (o `src/pages/home.html` para el Home) y volver a ejecutar `python build.py`. Requiere Python 3 con `lxml`. **No editar a mano los `index.html` generados.**

## Producción (https://samdigital.com.co)

El sitio se publica con el Git de Hostinger (hPanel → Advanced → Git, rama `main`): **cada push a `main` actualiza el sitio real**, así que se publica solo lo que ya se probó en local. No hay build en el servidor: se sube lo que está commiteado, por eso los HTML generados van en el repo.

- **Canonical, `og:url` y `og:image`** (y tarjeta de Twitter): los agrega `build.py` a cada página con el dominio de la constante `SITE`. Si el dominio cambia, se cambia ahí y se regenera. Los artículos usan `og:type=article`.
- **Imágenes para compartir:** `python src/tools/make_og.py` (requiere Pillow) genera `assets/img/og/default.jpg` y una por artículo. Se ejecuta solo si cambian las fotos.
- **`sitemap.xml`:** se regenera con cada `python build.py`. **`robots.txt`** es estático y apunta a ese mapa.
- **`404.html`:** la sirve el servidor en cualquier ruta que no existe (`ErrorDocument` del `.htaccess`). Usa `<base href="/">` para que cargue bien en rutas profundas; por eso solo se ve correcta en el dominio raíz.
- **`.htaccess`:** una sola dirección (`https` y sin `www`), bloquea `build.py`, `README.md`, `src/` y `.git`, y declara la 404. Cada despliegue lo reemplaza: no editarlo en el servidor. Si el deploy falla por un `.htaccess` ya existente, borrar el del servidor y volver a desplegar.
- **Caché:** los CSS y JS llevan `?v=<huella>` (la calcula `build.py`), así un cambio publicado se ve de inmediato aunque el navegador tenga la versión anterior en caché.

## Marca (extraída del sitio actual)

| Token | Valor | Uso |
|---|---|---|
| `--navy-900` | `#06304C` | azul marino de marca, fondos oscuros y titulares |
| `--orange` | `#FEA027` → `#E67A1F` | CTA y acentos (degradé del botón original) |
| `--cyan` | `#25A8B3` | turquesa de marca (botón de cabecera, números) |
| `--ice` | `#F1FEFF` | fondo de secciones claras |

Tipografías: **Red Hat Display** (títulos, 900), **Quicksand** (texto) y **Poppins** (números), las mismas del sitio actual.
El acento en cursiva (estilo Superside/Markethink) usa Red Hat Display *italic* en lugar de una serif para no salirse de la marca.

## Degradados

- **Claros:** blanco que se funde a naranja suave (`--grad-warm`), con luces naranja (`.aurora--o`).
- **Oscuros:** azul marino con luz azul/turquesa y toques naranja (`--grad-dark-1`, `--grad-dark-2`), más profundidad en CTA y footer.
- **Botones:** naranja degradado (primario), azul marino degradado (oscuro) y degradé turquesa → naranja (cabecera y WhatsApp).

## Contenedor

Medido en superside.com a 1920 px: contenido de **1608 px** máximo, centrado, con gutter de 32 px (`--maxw: 1672px` = 1608 + 2×32; `--gutter: clamp(16px, 2.5vw, 32px)`). Por debajo de 1672 px ocupa el ancho completo menos el gutter. Ver `.container` en `styles.css`.

## Técnicas aplicadas

| Técnica | Referente | Dónde |
|---|---|---|
| Scroll suave (Lenis) + progreso en la parte superior | Markethink | global |
| Cabecera flotante tipo píldora, oculta al bajar y visible al subir; botón de menú (hamburguesa) que abre un **mega menú** de pantalla completa: se expande en círculo desde el botón, navegación grande, las 9 soluciones y un CTA naranja con botón con brillo y pulso | Markethink | header |
| Titulares revelados palabra por palabra con máscara | Superside | todos los `h1/h2` |
| Acento en cursiva con degradé | Superside / Markethink | `em` en titulares |
| Hero sin foto: **muro de trabajos** (portafolio real de SÁM) en dos columnas inclinadas que suben y bajan, reactivas al scroll y al mouse; aurora y grilla | Superside / Markethink | hero |
| Párrafo que se ilumina palabra a palabra con el scroll | Superside | "Sobre nosotros" |
| **Hero fijo (sticky)** a pantalla completa: "Sobre nosotros" sube y lo cubre; el hero se aleja y se oscurece mientras tanto | — | hero → sección 2 |
| **Mosaico** de cuadrados y rectángulos (5 fotos de stock + tile de experiencia con cifra que rueda) | Superside | "Sobre nosotros" |
| **Footer estilo Superside**: foto de stock a pantalla completa con degradado oscuro, titular + CTA centrados y columnas "Soluciones" / "Navegación" con líneas finas; la foto se desplaza con el scroll | Superside | footer |
| **Secciones a alto completo**: cada bloque mide al menos el alto de la pantalla (`min-height: 100svh`) y centra su contenido, así nunca asoma un pedazo de la siguiente | Superside | global |
| Dígitos que ruedan | Superside | "15+" del mosaico y cifras |
| Lista de soluciones con vista previa que sigue al cursor | Superside | "Soluciones" |
| **Scrollytelling en una sola escena fija**: la intro "¿Cómo lo hacemos?" se acerca al espectador y se desvanece mientras la primera tarjeta emerge desde el fondo (escala, desenfoque y dashboard inclinado en 3D); luego los 3 pasos (datos → análisis → estrategia) sobre el mismo fondo, con anillos que crecen para dar profundidad | Markethink | "¿Cómo lo hacemos?" |
| **Scroll horizontal** con pin y tarjetas altas (imagen + barra de título teñida con el color de cada proyecto) | Superside | "Casos de éxito" |
| Cursor personalizado (punto sólido + aro con halo blanco, estados de enlace y "Ver") y luz de color que sigue al cursor en el hero | Asoclicper | global (solo punteros finos) |
| Botones magnéticos con retorno elástico y foco de luz que sigue al cursor; tarjetas y filas con luz al pasar el mouse | Asoclicper | botones, tarjetas, soluciones |
| Botón flotante de servicio al cliente (ícono de audífonos): círculo que se expande al pasar el mouse y abre una tarjeta de contacto que lleva a WhatsApp (número de SÁM tomado de su sitio actual) | Asoclicper | esquina inferior derecha |

Accesibilidad: respeta `prefers-reduced-motion` (sin Lenis, sin pines ni animaciones; el contenido queda visible y apilado). El cursor personalizado solo se activa con mouse.

## Imágenes

- **Portafolio** (hero y casos de éxito): trabajos reales de samdigital.com.co.
- **Mosaico de "Sobre nosotros"** y **foto del footer**: fotos de stock de [Unsplash](https://unsplash.com) (licencia libre), **provisionales**; reemplazar por fotografía propia del equipo de SÁM cuando exista.
- Blog e íconos de servicios: del sitio actual.

## Pendientes por validar con el cliente

- **WhatsApp**: se usa el número que ya está configurado en el sitio actual (`573167335485`); confirmar que es el oficial.
- **Logos de clientes**: la sección "Ellos confiaron en nosotros" del sitio actual no se pudo extraer; hay que pedir los logos.
- **Casos de éxito**: se usan los 12 trabajos del portafolio actual (`assets/img/work/`, mockups de 1200×800). Faltan resultados/métricas aprobadas por cliente. VOLCALI está solo en el muro del hero (su enlace en el sitio actual apunta por error a ASOCLICPER). "Ver portafolio" enlaza a `/portafolio/`.
- **Cifras**: se usan datos reales del sitio actual (15+ años, 9 soluciones, 4 plataformas de pauta, 30 min de consultoría). Si hay métricas aprobadas (clientes, proyectos, ROI), se pueden sumar.
- **Textos de "¿Cómo lo hacemos?"**: el sitio actual tiene lorem ipsum en esta sección; los textos de los 3 pasos son propuesta nuestra.
- **Formulario de contacto**: no tiene backend. Al enviarlo valida los campos y abre WhatsApp con el mensaje ya redactado; al migrar se reemplaza por el envío real (correo / CRM).
- **Textos repetidos en el sitio actual** (se mantuvieron tal cual): el título "Beneficios de la generación de leads" aparece también en Social media manager, Publicidad paga, Diseño gráfico y Email marketing. Conviene corregirlos con el cliente.
- **Enlace de VOLCALI** en el portafolio: en el sitio actual apunta a asoclicper.com (se mantuvo); la tarjeta "Marketing Estrátegico" se corrigió a "Estratégico".
- **Portafolio**: las pestañas "Diseño gráfico" y "Edición de video" están vacías en el sitio actual; muestran "Pronto publicaremos nuevos proyectos en esta categoría.".
- **Fotos de los artículos y de Nosotros**: las de stock son provisionales.
