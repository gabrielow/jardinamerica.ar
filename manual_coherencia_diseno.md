# Manual de Coherencia de Diseño — ITe Jardín América

Este manual establece las pautas visuales y técnicas de frontend para mantener la coherencia del diseño en las páginas `index.html` y `tablero.html` durante futuras modificaciones o integraciones en **jardinamerica.ar**.

---

## 1. Sistema de Colores (Design Tokens)

El sitio utiliza una paleta centrada en un **violeta vibrante** (Violeta Roxo) como tono de identidad corporativa y **verde WhatsApp** para acciones de contacto. Todos los colores están mapeados en `:root`.

| Nombre Variable | Color Base | Uso Primario |
| :--- | :--- | :--- |
| `--purple` | `#7c3aed` | Identidad, marcas principales, hover activo. |
| `--purple-dark` | `#5b21b6` | Fondos oscuros de CTA, textos sobre fondos claros muy suaves. |
| `--purple-light` | `#ede9fe` | Fondos de badges, secciones destacadas muy claras. |
| `--purple-mid` | `#8b5cf6` | Botón primario de carteleras. |
| `--green-wa` | `#25d366` | Acciones directas de WhatsApp y botones "Pedir Turno". |
| `--green-wa-dk` | `#128c4a` | Hover del botón de WhatsApp. |
| `--blue-ar` | `#0055A4` | Enlaces o marcas institucionales de alcance nacional (Argentina). |
| `--text` | `#1f2937` | Texto base (gris oscuro, evita negro puro para mejor lectura). |
| `--muted` | `#6b7280` | Subtítulos y textos de soporte/descripción de tarjetas. |
| `--border` | `#e5e7eb` | Líneas de división de cards, navbar y footer. |
| `--bg-alt` | `#f9fafb` | Color de fondo de secciones alternadas (gris ultra claro). |

> [!IMPORTANT]
> **Accesibilidad WCAG:** Al agregar textos encima de fondos de color, siempre asegúrate de usar combinaciones que superen la relación de contraste **4.5:1** (WCAG 2.1 AA). 
> - *Texto blanco:* Solo sobre fondos `--purple`, `--purple-dark` o `--green-wa-dk`.
> - *Texto oscuro:* Sobre fondo blanco, `--purple-light` o `--bg-alt`.

---

## 2. Pautas de Tipografía y Espaciado

- **Tipografía:** Se utiliza la fuente del sistema por defecto (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto...`) garantizando tiempos de carga óptimos de 0ms y adaptabilidad nativa en iOS/Android.
- **Jerarquía:** 
  - `h1`: Reservado para el encabezado principal de cada página (uno por página, `font-weight: 800`).
  - `h2`: Títulos de secciones.
  - `h3`: Títulos de tarjetas o subsecciones.
- **Espaciados standard:**
  - Padding de secciones principales: `padding: 4.5rem 0` en escritorio, `padding: 3rem 0` en mobile.

---

## 3. Botones y Micro-interacciones

### Clases de Botón Standard
- **`.btn-primary`:** Botón principal verde WhatsApp (`background: var(--green-wa)`).
- **`.btn-secondary`:** Botón translúcido (`background: rgba(255,255,255,0.15)`) con borde claro, diseñado para fondos oscuros.
- **`.btn-wa-contact`:** Usado específicamente en las tarjetas del tablero para inicializar llamadas y chats por WhatsApp.

### Badge de Sugerencia del Tablero (`.cta-suggestion`)
Para promocionar el tablero digital ("Encontrá la solución acá ↓"), se utiliza un badge flotante con animación.

**Regla Técnica Crítica de Alineación:**
Para evitar desajustes verticales y baselines descuadradas de `2px` en layouts flex, **no se deben utilizar divs contenedores wrapper**. El elemento `.cta-suggestion` debe insertarse directamente dentro del enlace `<a>` que tenga `position: relative`:

```html
<a class="btn-primary" href="tablero.html" style="position: relative; background: var(--purple-mid);">
  <span class="cta-suggestion">
    Encontrá la solución acá <span class="cta-arrow">↓</span>
  </span>
  🖼️ Ver Tablero de Tarjetas
</a>
```

### Animaciones Registradas:
- **`floatBadge` (2s ease-in-out infinite):** Flotamiento suave arriba/abajo del badge sugeridor.
- **`bounceArrow` (1s infinite alternate):** Rebote vertical de la flecha indicadora (`↓`).
- **Zoom de imágenes (`.tarjeta-img`):** Escala a `1.03` con transición de `.3s` al pasar el cursor sobre las tarjetas.

---

## 4. Tarjetas de la Cartelera (`tablero.html`)

Para mantener el tablero en orden, cada tarjeta agregada debe seguir el siguiente código rígido:

```html
<!-- Tarjeta [Número]: [Nombre] ([Categoría]) -->
<div class="tarjeta-card" data-category="[CATEGORÍA]" data-keywords="[PALABRAS CLAVE]">
  <div class="tarjeta-img-container" onclick="openLightbox('assets/[NOMBRE_ARCHIVO].jpeg')">
    <img class="tarjeta-img" src="assets/[NOMBRE_ARCHIVO].jpeg" alt="[NOMBRE_NEGOCIO]" loading="lazy">
    <div class="tarjeta-zoom-overlay">🔍 Ampliar</div>
  </div>
  <div class="tarjeta-info">
    <span class="tarjeta-cat-badge">[TEXTO_CATEGORÍA]</span>
    <h3 class="tarjeta-title">[NOMBRE_NEGOCIO]</h3>
    <p class="tarjeta-desc">
      [DESCRIPCIÓN DE SERVICIOS]
    </p>
    <a class="btn-wa-contact" href="#" onclick="irAContactar('[TELEFONO_INTERNACIONAL]', '[MENSAJE_WHATSAPP_CODIFICADO]'); return false;">
      📲 Enviar WhatsApp
    </a>
  </div>
</div>
```

- **Categorías (`data-category`):** Debe ser estrictamente `profesionales`, `emprendimientos` o `empresas`.
- **Palabras Clave (`data-keywords`):** Cadena en minúsculas, sin comas ni tildes, que contenga sinónimos útiles para el buscador (ej: `odontologo dentista muelas ortodoncia salud`).

---

## 5. SEO y Estructura Semántica

Cada modificación de página debe respetar estas reglas:
- **Un único `<h1>`:** Asegura la indexación SEO adecuada en Google.
- **Etiquetas de HTML5:** Usa `<nav>`, `<header>`, `<main>`, `<section>`, `<footer>` en lugar de divs anidados sin valor semántico.
- **IDs únicos:** Los elementos interactivos (buscadores, botones, FAQs) deben tener IDs descriptivos.
- **Imágenes:** Todo elemento `<img>` debe contar con un atributo `alt` coherente e inteligible y carga diferida (`loading="lazy"`) para las tarjetas.
