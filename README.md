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
- **Casos de éxito**: se usan los 12 trabajos del portafolio actual (`assets/img/work/`, mockups de 1200×800). Faltan resultados/métricas aprobadas por cliente. VOLCALI está solo en el muro del hero (su enlace en el sitio actual apunta por error a ASOCLICPER). "Ver portafolio" enlaza al portafolio del sitio actual hasta que se diseñe esa página.
- **Cifras**: se usan datos reales del sitio actual (15+ años, 9 soluciones, 4 plataformas de pauta, 30 min de consultoría). Si hay métricas aprobadas (clientes, proyectos, ROI), se pueden sumar.
- **Textos de "¿Cómo lo hacemos?"**: el sitio actual tiene lorem ipsum en esta sección; los textos de los 3 pasos son propuesta nuestra.
- **Enlaces internos**: las páginas de cada solución, portafolio, blog y legales apuntan a anclas/`#` hasta que se diseñen.
- **Formulario de contacto**: falta diseñar la sección con formulario (hoy el CTA lleva al ancla `#contacto`).
