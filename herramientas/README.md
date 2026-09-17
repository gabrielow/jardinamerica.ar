# Manual de Procedimiento: Generación y Publicación de Tarjetas de CV

Este documento detalla el procedimiento estandarizado para la digitalización, diseño y publicación de currículums vitae en la cartelera digital de **ITe Jardín América** (`tablero.html`).

---

## 1. Filosofía y Principios de Diseño

1. **Fidelidad Estricta al Contenido (Sin Invenciones)**:
   - Toda la información volcada en la tarjeta y el flyer gráfico proviene exclusivamente del documento entregado por el postulante.
   - Está prohibido alterar cargos, inventar habilidades o exagerar responsabilidades.
   - Se sintetiza con criterio profesional para maximizar el impacto sin desvirtuar la realidad.

2. **Diseño Mobile-First**:
   - Más del 85% del tráfico en cartelera local proviene de dispositivos móviles (WhatsApp / smartphones).
   - El flyer se diseña en proporción **1:1 cuadrada (1024x1024 px)**, asegurando que se visualice completo en la pantalla del celular sin desbordar verticalmente.
   - Tipografía grande y de alto contraste (Segoe UI / Arial) con jerarquía visual nítida.
   - Se evitan fuentes de emojis del sistema que puedan romperse; en su lugar, se utilizan insignias vectoriales nativas para garantizar compatibilidad multiplataforma.

3. **Optimización de Rendimiento Web**:
   - Formato principal en **WebP** (`method=6`, `quality=92`) para carga instantánea y consumo mínimo de datos móviles.
   - Fallback en formato **JPEG** para retrocompatibilidad.
   - Atributos `loading="lazy"` en `tablero.html`.

4. **Conversión y Contacto Directo**:
   - Enlace directo de WhatsApp formateado con código de país (`+54 9 ...`), sin obligar al usuario a agendar manualmente el número.
   - Normalización inteligente de números argentinos (eliminación automática del prefijo local `15` en URLs de WhatsApp).
   - Mensaje inicial predeterminado respetuoso y contextualizado con el nombre del postulante.

---

## 2. Estructura de la Carpeta `herramientas/`

```
herramientas/
├── README.md               # Este manual operativo
├── extractor_cv.py         # Extractor y normalizador (Interactivo / Texto / Clipboard)
├── generador_cv.py         # Generador de flyers (1024x1024 WebP/JPEG) y snippet HTML
├── cv_plantilla.json       # Plantilla base para nuevos postulantes
└── cv_veronica_luque.json  # Caso de referencia implementado (Verónica Luque)
```

---

## 3. Procedimiento Paso a Paso

### Flujo A: Asistido con IA (Recomendado en el IDE con Antigravity)
1. El usuario adjunta la fotografía o escaneo del CV y la foto de perfil en el chat.
2. El asistente extrae fielmente el contenido mediante visión multimodal y genera el archivo `herramientas/cv_<slug>.json`.
3. El usuario aprueba los datos sintetizados.
4. El asistente ejecuta la compilación y la inserción en `tablero.html`.

---

### Flujo B: Extracción y Generación Autónoma por Consola

#### Paso 1: Extracción Automática de Datos (`extractor_cv.py`)

Tenés 3 opciones para crear el JSON del postulante:

- **Modo Interactivo Asistido (Paso a paso en consola)**:
  ```bash
  python herramientas/extractor_cv.py --interactivo
  ```
  El script guía al operador realizando preguntas concisas, normaliza el teléfono argentino automáticamente, valida los campos y pregunta si se desea generar e insertar la tarjeta al finalizar.

- **Modo Extracción desde Texto (Word, PDF o mensaje de WhatsApp)**:
  ```bash
  python herramientas/extractor_cv.py --texto ruta/a/cv_texto.txt
  ```
  Detecta automáticamente nombre, cargo, teléfono argentino, email, secciones de experiencia, habilidades y educación, y exporta `herramientas/cv_<slug>.json`.

- **Modo Pegado Rápido por Consola**:
  ```bash
  python herramientas/extractor_cv.py --pegar
  ```

---

#### Paso 2: Generación del Flyer y Publicación (`generador_cv.py`)

Una vez obtenido el JSON del postulante:

- **Opción 1: Generación y Publicación Automática (Recomendada)**
  ```bash
  python herramientas/generador_cv.py --json herramientas/cv_<slug>.json --insertar
  ```
  - Crea `assets/cv_<slug>.webp` y `assets/cv_<slug>.jpeg`.
  - Calcula automáticamente el próximo número correlativo de tarjeta (ej: `Tarjeta 20`).
  - Inserta el bloque de tarjeta directamente en `tablero.html` antes de `<!-- Mensaje de no resultados -->`.

- **Opción 2: Solo Generación Gráfica (Sin tocar `tablero.html`)**
  ```bash
  python herramientas/generador_cv.py --json herramientas/cv_<slug>.json
  ```
  - Crea las imágenes y muestra el snippet HTML en la consola para revisión manual.

---

### Paso 3: Control de Calidad y Validación
- [ ] **Sintaxis HTML**: Verificar que no hayan etiquetas abiertas (`tablero.html`).
- [ ] **Conteo de tarjetas**: Comprobar que el contador dinámico en la cabecera refleje el nuevo total.
- [ ] **Filtro de categoría**: Seleccionar el botón *"CVs Personales"* y verificar que la tarjeta se muestre correctamente.
- [ ] **Buscador en tiempo real**: Probar escribiendo el nombre, el cargo o palabras del rubro en el campo de búsqueda.
- [ ] **Lightbox**: Hacer clic en la tarjeta y comprobar que se amplíe nítidamente en la ventana emergente modal.
- [ ] **Botón WhatsApp**: Probar el enlace para verificar que abra la aplicación con el número internacional y el mensaje de cortesía prellenado.

---

## 4. Próxima Etapa (Etapa 2)

- **Formulario Web de Autocarga (`sumar-cv.html`)**:
  Página responsive en la web para que postulantes puedan cargar su currículum y foto directamente desde su smartphone, generando solicitudes listas para aprobación del administrador.
