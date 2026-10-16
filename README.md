# SÁM digital · Rediseño del sitio (Home v1)

Propuesta de rediseño del Home de [samdigital.com.co](https://samdigital.com.co/): más impacto visual y de movimiento, manteniendo el branding de la marca.
Sitio estático (HTML + CSS + JS vanilla), sin build.

```
index.html              ← Home
assets/css/styles.css   ← sistema de diseño + estilos de todas las secciones
assets/js/main.js       ← animaciones, cursor, scrollytelling
assets/vendor/          ← GSAP 3.12.5, ScrollTrigger 3.12.5, Lenis 1.1.20 (copias locales)
assets/img/             ← logos, iconos de servicios, portafolio (work/) y blog (tomados del sitio actual)
```

## Probar en local

```bash
npx http-server . -p 5190 -c-1
```

## Marca (extraída del sitio actual)

| Token | Valor | Uso |
|---|---|---|
| `--navy-900` | `#06304C` | azul marino de marca, fondos oscuros y titulares |
| `--orange` | `#FEA027` → `#E67A1F` | CTA y acentos (degradé del botón original) |
| `--cyan` | `#25A8B3` | turquesa de marca (botón de cabecera, números) |
| `--ice` | `#F1FEFF` | fondo de secciones claras |

Tipografías: **Red Hat Display** (títulos, 900), **Quicksand** (texto) y **Poppins** (números), las mismas del sitio actual.
El acento en cursiva (estilo Superside/Markethink) usa Red Hat Display *italic* en lugar de una serif para no salirse de la marca.

## Contenedor

Medido en superside.com a 1920 px: contenido de **1608 px** máximo, centrado, con gutter de 32 px (`--maxw: 1672px` = 1608 + 2×32; `--gutter: clamp(16px, 2.5vw, 32px)`). Por debajo de 1672 px ocupa el ancho completo menos el gutter. Ver `.container` en `styles.css`.

## Técnicas aplicadas

| Técnica | Referente | Dónde |
|---|---|---|
| Scroll suave (Lenis) + progreso en la parte superior | Markethink | global |
| Cabecera flotante tipo píldora, oculta al bajar y visible al subir, con mega-menú de soluciones | Markethink | header |
| Titulares revelados palabra por palabra con máscara | Superside | todos los `h1/h2` |
| Acento en cursiva con degradé | Superside / Markethink | `em` en titulares |
| Hero sin foto: **muro de trabajos** (portafolio real de SÁM) en dos columnas inclinadas que suben y bajan, reactivas al scroll y al mouse; aurora y grilla | Superside / Markethink | hero |
| Bandas cruzadas (marquee) que aceleran con la velocidad del scroll | — | tras el hero |
| Párrafo que se ilumina palabra a palabra con el scroll | Superside | "Sobre nosotros" |
| Dígitos que ruedan | Superside | "15+" y cifras |
| Lista de soluciones con vista previa que sigue al cursor | Superside | "Soluciones" |
| **Scrollytelling** con pin: dashboard 3D que se endereza y 3 pasos (datos → análisis → estrategia) | Markethink | "¿Cómo lo hacemos?" |
| **Scroll horizontal** con pin y tarjetas altas (imagen + barra de título teñida con el color de cada proyecto) | Superside | "Casos de éxito" |
| Cursor personalizado (punto + aro, estados de enlace y "Ver"), botones magnéticos | — | global (solo punteros finos) |
| Secciones apiladas con borde redondeado | Superside | transición entre secciones |

Accesibilidad: respeta `prefers-reduced-motion` (sin Lenis, sin pines ni animaciones; el contenido queda visible y apilado). El cursor personalizado solo se activa con mouse.

## Pendientes por validar con el cliente

- **WhatsApp**: el botón flotante existe en el sitio actual; falta el número oficial (hoy enlaza a `#contacto`).
- **Logos de clientes**: la sección "Ellos confiaron en nosotros" del sitio actual no se pudo extraer; hay que pedir los logos.
- **Casos de éxito**: se usan los 12 trabajos del portafolio actual (`assets/img/work/`, mockups de 1200×800). Faltan resultados/métricas aprobadas por cliente. VOLCALI está solo en el muro del hero (su enlace en el sitio actual apunta por error a ASOCLICPER). "Ver portafolio" enlaza al portafolio del sitio actual hasta que se diseñe esa página.
- **Cifras**: se usan datos reales del sitio actual (15+ años, 9 soluciones, 4 plataformas de pauta, 30 min de consultoría). Si hay métricas aprobadas (clientes, proyectos, ROI), se pueden sumar.
- **Textos de "¿Cómo lo hacemos?"**: el sitio actual tiene lorem ipsum en esta sección; los textos de los 3 pasos son propuesta nuestra.
- **Enlaces internos**: las páginas de cada solución, portafolio, blog y legales apuntan a anclas/`#` hasta que se diseñen.
- **Formulario de contacto**: falta diseñar la sección con formulario (hoy el CTA lleva al ancla `#contacto`).
