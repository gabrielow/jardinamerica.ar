# Reglas e Instrucciones del Proyecto (jardinamerica.ar)

## Alojamiento y Dominio
- Esta página está alojada en **GitHub Pages**.
- Utiliza un dominio personalizado (`jardinamerica.ar`), configurado mediante el archivo `CNAME` en la raíz del repositorio.
- Al ser un sitio estático (HTML, CSS, JavaScript vainilla), no requiere servidores backend dinámicos ni dependencias complejas.

## Estructura y Reglas para el Tablero (`tablero.html`)
1. **Agregar Nuevas Tarjetas / Flyers**:
   - Copiar/guardar la imagen promocional en la carpeta `assets/` utilizando nombres descriptivos en minúsculas con guiones bajos (`snake_case`, ej: `assets/maderas_del_norte.jpeg`).
   - Agregar el bloque `<div class="tarjeta-card">` siguiendo el orden numérico correlativo en los comentarios (ej: `<!-- Tarjeta 16: Maderas del Norte (Empresa) -->`).
   - Asignar la categoría correspondiente en `data-category` (`profesionales`, `emprendimientos`, `empresas`, `cvs`).
   - Incluir un atributo `data-keywords` amplio, en minúsculas y sin acentos, para el correcto funcionamiento del buscador local.
   - Configurar el visor de imagen lightbox con `onclick="openLightbox('assets/...')"` y la etiqueta `<img>` con `loading="lazy"`.
   - Formatear el botón de contacto de WhatsApp llamando a `irAContactar('549...', 'Mensaje inicial...')`.

## Generación Estandarizada de Tarjetas de CV
- Para tarjetas de postulantes (`data-category="cvs"`), utilizar la herramienta modular en `herramientas/generador_cv.py`.
- Genera automáticamente los activos gráficos en WebP y JPEG (1024x1024 px, mobile-first, paleta ITe) y el bloque HTML listo para insertar en `tablero.html`.
- Ver documentación y plantilla en `herramientas/README.md` y `herramientas/cv_plantilla.json`.
