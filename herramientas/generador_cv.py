"""
=============================================================================
ITe Jardín América — Generador Automático de Tarjetas de CV para el Tablero
=============================================================================
Este script procesa datos de un perfil (vía JSON o diccionario) y genera:
1. Flyer gráfico 1024x1024 en WebP y JPEG (mobile-first, alta definición).
2. Recorte circular automático antialiased de la foto de perfil.
3. Snippet de código HTML listo para insertar en `tablero.html`.
"""

import os
import sys
import json
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Soporte UTF-8 en consola de Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# ── Paleta institucional ITe ────────────────────────────────────────────────
COLOR_BG_START = (243, 236, 255)       # Violeta claro superior
COLOR_BG_END = (216, 198, 254)         # Violeta suave inferior
COLOR_CARD_BG = (255, 255, 255)        # Blanco puro tarjeta
COLOR_CARD_BORDER = (226, 218, 247)    # Borde sutil tarjeta
COLOR_PURPLE = (109, 40, 217)          # Violeta principal (#6d28d9)
COLOR_PURPLE_LIGHT = (243, 232, 255)   # Violeta fondos píldoras (#f3e8ff)
COLOR_PURPLE_RING = (124, 58, 237)     # Anillo foto (#7c3aed)
COLOR_TEXT_MAIN = (15, 23, 42)         # Texto oscuro (#0f172a)
COLOR_TEXT_MUTED = (100, 116, 139)     # Texto secundario (#64748b)
COLOR_TEXT_BODY = (51, 65, 85)         # Texto cuerpo (#334155)
COLOR_TEXT_SUB = (79, 70, 229)         # Subtítulo cargo (#4f46e5)
COLOR_DIVIDER = (241, 245, 249)        # Líneas divisorias (#f1f5f9)

def obtener_fuentes():
    """Carga fuentes del sistema con fallback seguro."""
    rutas_bold = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ]
    rutas_norm = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    f_bold = next((r for r in rutas_bold if os.path.exists(r)), None)
    f_norm = next((r for r in rutas_norm if os.path.exists(r)), None)

    if not f_bold or not f_norm:
        raise FileNotFoundError("No se encontraron fuentes TTF compatibles en el sistema.")

    return {
        "title": ImageFont.truetype(f_bold, 44),
        "role": ImageFont.truetype(f_bold, 20),
        "sub": ImageFont.truetype(f_norm, 16),
        "sec": ImageFont.truetype(f_bold, 21),
        "h3": ImageFont.truetype(f_bold, 18),
        "body_b": ImageFont.truetype(f_bold, 16),
        "body": ImageFont.truetype(f_norm, 15),
        "small": ImageFont.truetype(f_norm, 14),
        "contact": ImageFont.truetype(f_bold, 16)
    }

def recortar_foto_circular(foto_path, target_size=176):
    """Recorta la foto en un círculo perfecto suavizado (antialiased)."""
    if not os.path.exists(foto_path):
        # Genera un avatar neutro si no hay foto
        avatar = Image.new("RGBA", (target_size, target_size), COLOR_PURPLE_LIGHT)
        d = ImageDraw.Draw(avatar)
        d.ellipse([10, 10, target_size - 10, target_size - 10], fill=COLOR_PURPLE)
        return avatar

    im = Image.open(foto_path).convert("RGBA")
    w, h = im.size
    min_dim = min(w, h)
    
    # Encuentra el centro o área de interés
    cx, cy = w // 2, h // 2
    box = (cx - min_dim // 2, cy - min_dim // 2, cx + min_dim // 2, cy + min_dim // 2)
    cropped = im.crop(box)
    resized = cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)

    # Máscara circular con supersampling 4x para bordes ultra suaves
    mask = Image.new("L", (target_size * 4, target_size * 4), 0)
    m_draw = ImageDraw.Draw(mask)
    m_draw.ellipse([0, 0, target_size * 4, target_size * 4], fill=255)
    mask = mask.resize((target_size, target_size), Image.Resampling.LANCZOS)

    return resized, mask

def generar_flyer_cv(datos, output_webp, output_jpeg=None):
    """
    Genera el flyer gráfico 1024x1024 a partir de un diccionario de datos.
    """
    W, H = 1024, 1024
    img = Image.new("RGBA", (W, H), (248, 247, 255, 255))
    draw = ImageDraw.Draw(img)

    # 1. Fondo degradado
    for y in range(H):
        ratio = y / H
        r = int(COLOR_BG_START[0] * (1 - ratio) + COLOR_BG_END[0] * ratio)
        g = int(COLOR_BG_START[1] * (1 - ratio) + COLOR_BG_END[1] * ratio)
        b = int(COLOR_BG_START[2] * (1 - ratio) + COLOR_BG_END[2] * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Círculos sutiles decorativos
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.ellipse([(-80, -80), (320, 320)], fill=(255, 255, 255, 70))
    ov_draw.ellipse([(W - 260, H - 260), (W + 140, H + 140)], fill=(124, 58, 237, 30))
    ov_draw.ellipse([(W - 160, 40), (W + 80, 280)], fill=(255, 255, 255, 55))
    img = Image.alpha_composite(img, overlay)

    # 2. Tarjeta blanca central con sombra difuminada
    card_m_x, card_m_y = 42, 32
    card_w = W - 2 * card_m_x
    card_h = H - 2 * card_m_y
    card_box = [card_m_x, card_m_y, card_m_x + card_w, card_m_y + card_h]

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rounded_rectangle(
        [card_m_x + 4, card_m_y + 8, card_m_x + card_w + 4, card_m_y + card_h + 8],
        radius=28, fill=(76, 29, 149, 35)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # Dibujo de tarjeta blanca
    draw.rounded_rectangle(card_box, radius=28, fill=COLOR_CARD_BG, outline=COLOR_CARD_BORDER, width=2)

    fonts = obtener_fuentes()

    # 3. Foto de perfil
    p_size = 176
    photo_resized, mask = recortar_foto_circular(datos.get("foto_path", ""), target_size=p_size)

    photo_x = (W - p_size) // 2
    photo_y = card_m_y + 32

    ring_pad = 5
    draw.ellipse(
        [photo_x - ring_pad, photo_y - ring_pad, photo_x + p_size + ring_pad, photo_y + p_size + ring_pad],
        fill=(245, 240, 255), outline=COLOR_PURPLE_RING, width=3
    )

    img.paste(photo_resized, (photo_x, photo_y), mask)
    draw = ImageDraw.Draw(img)

    # 4. Encabezado: Nombre y Cargo
    nombre = datos.get("nombre", "Nombre y Apellido")
    n_box = draw.textbbox((0, 0), nombre, font=fonts["title"])
    n_w = n_box[2] - n_box[0]
    name_y = photo_y + p_size + 14
    draw.text(((W - n_w) // 2, name_y), nombre, fill=COLOR_TEXT_MAIN, font=fonts["title"])

    # Píldora de Cargo
    cargo = datos.get("cargo", "POSTULANTE").upper()
    r_box = draw.textbbox((0, 0), cargo, font=fonts["role"])
    r_w = r_box[2] - r_box[0]
    pill_w = r_w + 36
    pill_h = 32
    pill_x = (W - pill_w) // 2
    pill_y = name_y + 54
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=16, fill=COLOR_PURPLE_LIGHT, outline=(221, 214, 254), width=1)
    draw.text((pill_x + 18, pill_y + 4), cargo, fill=COLOR_PURPLE, font=fonts["role"])

    # Subtítulo / Etiquetas
    sub = datos.get("subtitulo", "")
    if sub:
        s_box = draw.textbbox((0, 0), sub, font=fonts["sub"])
        s_w = s_box[2] - s_box[0]
        draw.text(((W - s_w) // 2, pill_y + 40), sub, fill=COLOR_TEXT_MUTED, font=fonts["sub"])

    # Divisor principal
    div_y = pill_y + 68
    draw.line([(card_m_x + 36, div_y), (W - card_m_x - 36, div_y)], fill=COLOR_DIVIDER, width=2)

    # 5. Columnas de Contenido
    col_split = 475
    left_x = card_m_x + 36
    right_x = col_split + 26
    top_c_y = div_y + 18

    draw.line([(col_split, top_c_y), (col_split, card_m_y + card_h - 96)], fill=COLOR_DIVIDER, width=2)

    def draw_badge(x, y, text):
        draw.rounded_rectangle([x, y, x + 28, y + 28], radius=7, fill=COLOR_PURPLE_LIGHT)
        draw.ellipse([x + 9, y + 9, x + 19, y + 19], fill=COLOR_PURPLE_RING)
        draw.text((x + 38, y + 2), text, fill=COLOR_PURPLE, font=fonts["sec"])

    def draw_bullet(x, y):
        draw.ellipse([x, y + 5, x + 8, y + 13], fill=COLOR_PURPLE_RING)

    # ── Columna Izquierda: Perfil & Habilidades ──
    draw_badge(left_x, top_c_y, "PERFIL PROFESIONAL")
    cur_y = top_c_y + 38
    for line in datos.get("perfil_lineas", []):
        draw.text((left_x, cur_y), line, fill=COLOR_TEXT_BODY, font=fonts["body"])
        cur_y += 22

    cur_y += 20
    draw_badge(left_x, cur_y, "HABILIDADES")
    cur_y += 38

    for hab in datos.get("habilidades", []):
        draw_bullet(left_x, cur_y)
        draw.text((left_x + 16, cur_y), hab, fill=COLOR_TEXT_MAIN, font=fonts["body_b"])
        cur_y += 28

    # ── Columna Derecha: Experiencia & Formación ──
    draw_badge(right_x, top_c_y, "EXPERIENCIA LABORAL")
    r_y = top_c_y + 38

    for exp in datos.get("experiencias", []):
        empresa = exp.get("empresa", "")
        fechas = exp.get("fechas", "")
        rol = exp.get("rol", "")
        desc = exp.get("desc", "")

        draw.text((right_x, r_y), empresa, fill=COLOR_TEXT_MAIN, font=fonts["h3"])
        if fechas:
            d_w = draw.textbbox((0, 0), fechas, font=fonts["small"])[2] - draw.textbbox((0, 0), fechas, font=fonts["small"])[0]
            draw.text((W - card_m_x - 36 - d_w, r_y + 2), fechas, fill=COLOR_PURPLE, font=fonts["small"])
        r_y += 22
        if rol:
            draw.text((right_x, r_y), rol, fill=COLOR_TEXT_SUB, font=fonts["body_b"])
            r_y += 20
        if desc:
            draw.text((right_x, r_y), desc, fill=COLOR_TEXT_BODY, font=fonts["small"])
            r_y += 26
        else:
            r_y += 8

    # Educación
    draw_badge(right_x, r_y, "EDUCACIÓN Y FORMACIÓN")
    r_y += 34

    for edu in datos.get("educacion", []):
        draw_bullet(right_x, r_y)
        draw.text((right_x + 16, r_y), edu, fill=COLOR_TEXT_MAIN, font=fonts["small"])
        r_y += 22

    # 6. Tira Inferior de Contacto
    banner_y = card_m_y + card_h - 76
    banner_box = [card_m_x + 18, banner_y, card_m_x + card_w - 18, card_m_y + card_h - 18]
    draw.rounded_rectangle(banner_box, radius=14, fill=(248, 250, 252), outline=(226, 232, 240), width=1)

    c_y = banner_y + 18
    c1_x = card_m_x + 40
    c2_x = card_m_x + 355
    c3_x = card_m_x + 685

    tel = datos.get("telefono_display", "")
    email = datos.get("email", "")
    direccion = datos.get("direccion", "")

    draw.text((c1_x, c_y), "WhatsApp:", fill=COLOR_PURPLE_RING, font=fonts["contact"])
    draw.text((c1_x + 88, c_y), tel, fill=COLOR_TEXT_MAIN, font=fonts["contact"])

    draw.text((c2_x, c_y), "Email:", fill=COLOR_PURPLE_RING, font=fonts["contact"])
    draw.text((c2_x + 55, c_y), email, fill=COLOR_TEXT_MAIN, font=fonts["contact"])

    draw.text((c3_x, c_y), "Dirección:", fill=COLOR_PURPLE_RING, font=fonts["contact"])
    draw.text((c3_x + 82, c_y), direccion, fill=COLOR_TEXT_MAIN, font=fonts["contact"])

    # Guardar
    os.makedirs(os.path.dirname(os.path.abspath(output_webp)), exist_ok=True)
    img_rgb = img.convert("RGB")
    img_rgb.save(output_webp, format="WEBP", quality=92, method=6)
    print(f"[OK] Flyer guardado en WebP: {output_webp}")

    if output_jpeg:
        img_rgb.save(output_jpeg, format="JPEG", quality=92)
        print(f"[OK] Fallback JPEG guardado: {output_jpeg}")

def generar_snippet_html(datos, numero_tarjeta=19):
    """Genera el bloque HTML listo para insertar en tablero.html."""
    nombre = datos.get("nombre", "Nombre y Apellido")
    foto_webp = datos.get("asset_webp_name", f"cv_{nombre.lower().replace(' ', '_')}.webp")
    keywords = datos.get("keywords", "")
    descripcion = datos.get("descripcion_tarjeta", "")
    wa_num = datos.get("telefono_wa", "")
    primer_nombre = nombre.split()[0]
    wa_msg = f"Hola {primer_nombre}! Vi tu CV en ITe y quería consultarte por una búsqueda de empleo."

    snippet = f"""      <!-- Tarjeta {numero_tarjeta}: {nombre} (CV / Postulante) -->
      <div class="tarjeta-card" data-category="cvs"
        data-keywords="{keywords}">
        <div class="tarjeta-img-container" onclick="openLightbox('assets/{foto_webp}')">
          <img class="tarjeta-img" src="assets/{foto_webp}" width="1024" height="1024" alt="CV {nombre}" loading="lazy">
          <div class="tarjeta-zoom-overlay">🔍 Ampliar</div>
        </div>
        <div class="tarjeta-info">
          <span class="tarjeta-cat-badge">CV / Postulante</span>
          <h3 class="tarjeta-title">{nombre}</h3>
          <p class="tarjeta-desc">
            {descripcion}
          </p>
          <a class="btn-wa-contact" href="https://wa.me/{wa_num}?text={wa_msg.replace(' ', '%20')}"
            onclick="irAContactar('{wa_num}', '{wa_msg}'); return false;">
            📲 Enviar WhatsApp
          </a>
        </div>
      </div>"""
    return snippet

def calcular_proximo_numero_tarjeta(tablero_path=r"d:\jardinamerica.ar\tablero.html"):
    """Calcula el próximo número correlativo analizando los comentarios en tablero.html."""
    import re
    if not os.path.exists(tablero_path):
        return 1
    with open(tablero_path, "r", encoding="utf-8") as f:
        content = f.read()
    nums = [int(m) for m in re.findall(r'<!--\s*Tarjeta\s*(\d+):', content)]
    return (max(nums) + 1) if nums else 1

def insertar_tarjeta_en_tablero(datos, numero_tarjeta=None, tablero_path=r"d:\jardinamerica.ar\tablero.html"):
    """Inserta el bloque de tarjeta al final del grid en tablero.html."""
    if not os.path.exists(tablero_path):
        print(f"[ERROR] No se encontró el archivo: {tablero_path}")
        return False
    
    if numero_tarjeta is None:
        numero_tarjeta = calcular_proximo_numero_tarjeta(tablero_path)
        
    snippet = generar_snippet_html(datos, numero_tarjeta)
    
    with open(tablero_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    marcador = "<!-- Mensaje de no resultados -->"
    if marcador not in html:
        print(f"[ERROR] No se encontró el marcador '{marcador}' en {tablero_path}")
        return False
        
    nuevo_bloque = f"{snippet}\n\n      {marcador}"
    nuevo_html = html.replace(f"      {marcador}", nuevo_bloque, 1)
    if nuevo_html == html:
        nuevo_html = html.replace(marcador, f"{snippet}\n\n      {marcador}", 1)
        
    with open(tablero_path, "w", encoding="utf-8") as f:
        f.write(nuevo_html)
        
    print(f"[OK] Tarjeta {numero_tarjeta} insertada con éxito en: {tablero_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de tarjetas y flyers de CV para tablero.html")
    parser.add_argument("--json", help="Ruta al archivo JSON de perfil", default=None)
    parser.add_argument("--out-dir", help="Directorio destino de assets", default=r"d:\jardinamerica.ar\assets")
    parser.add_argument("--tarjeta-num", type=int, help="Número correlativo de tarjeta (por defecto autocalculado)", default=None)
    parser.add_argument("--insertar", action="store_true", help="Inserta automáticamente la tarjeta generada en tablero.html")
    parser.add_argument("--tablero", help="Ruta al archivo tablero.html", default=r"d:\jardinamerica.ar\tablero.html")
    args = parser.parse_args()

    if args.json and os.path.exists(args.json):
        with open(args.json, "r", encoding="utf-8") as f:
            datos_cv = json.load(f)
    else:
        print("Usando configuración de ejemplo o no se especificó --json.")
        sys.exit(0)

    nombre_slug = datos_cv.get("slug", "postulante")
    out_webp = os.path.join(args.out_dir, f"cv_{nombre_slug}.webp")
    out_jpeg = os.path.join(args.out_dir, f"cv_{nombre_slug}.jpeg")
    datos_cv["asset_webp_name"] = f"cv_{nombre_slug}.webp"

    generar_flyer_cv(datos_cv, out_webp, out_jpeg)

    num_tarjeta = args.tarjeta_num if args.tarjeta_num is not None else calcular_proximo_numero_tarjeta(args.tablero)

    print("\n--- SNIPPET HTML GENERADO ---")
    print(generar_snippet_html(datos_cv, num_tarjeta))

    if args.insertar:
        insertar_tarjeta_en_tablero(datos_cv, num_tarjeta, args.tablero)
