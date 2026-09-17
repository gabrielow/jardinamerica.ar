"""
=============================================================================
ITe Jardín América — Extractor y Normalizador de Datos de CV
=============================================================================
Herramienta de extracción y estructuración de currículums para el tablero.
Soporta:
1. Ingesta desde texto plano / portapapeles / archivo TXT con detección heurística.
2. Modo interactivo asistido paso a paso por consola.
3. Normalización automática de teléfonos argentinos para WhatsApp.
4. Generación automática de archivo JSON compatible con `generador_cv.py`.
"""

import os
import sys
import re
import json
import unicodedata
import argparse

# Soporte UTF-8 en consola de Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def normalizar_texto_sin_acentos(texto):
    """Elimina acentos y normaliza a minúsculas para keywords."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize('NFKD', texto)
    sin_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', sin_acento).lower()

def normalizar_telefono_argentina(raw_tel):
    """
    Normaliza números telefónicos argentinos de cualquier formato:
    ej: '1173673799', '011 15 7367-3799', '03743-15-454291', '+54 9 3743 454291'
    Retorna: (telefono_display, telefono_wa)
    """
    if not raw_tel:
        return ("", "")
    
    # Extrae solo dígitos
    nums = re.sub(r'\D', '', raw_tel)
    
    # Remueve ceros iniciales de prefijo (011 -> 11, 03743 -> 3743)
    if nums.startswith('0'):
        nums = nums[1:]
    
    # Remueve código de país inicial si ya lo trae
    if nums.startswith('549'):
        nums = nums[3:]
    elif nums.startswith('54'):
        nums = nums[2:]
    
    # Remueve '15' de celular local si tiene 12 dígitos (2, 3 o 4 de área + 15 + número)
    # ej: 11 15 73673799 (11 + 15 + 8 digitos) -> 1173673799
    # ej: 376 15 4123456 (376 + 15 + 7 digitos) -> 3764123456
    # ej: 3743 15 454291 (3743 + 15 + 6 digitos) -> 3743454291
    if len(nums) == 12:
        if nums[2:4] == '15':
            nums = nums[:2] + nums[4:]
        elif nums[3:5] == '15':
            nums = nums[:3] + nums[5:]
        elif nums[4:6] == '15':
            nums = nums[:4] + nums[6:]
    elif len(nums) == 11 and nums.startswith('15'):
        nums = nums[2:]

    # Construye formato WhatsApp internacional (+54 9 ...)
    wa_num = f"549{nums}"

    # Formateo amigable de visualización
    if nums.startswith('11') and len(nums) == 10:
        display = f"+54 9 11 {nums[2:6]}-{nums[6:]}"
    elif len(nums) == 10:
        # Áreas de 3 dígitos (ej: 376) o 4 dígitos (ej: 3743)
        if nums.startswith(('376', '341', '351', '381', '221', '223')):
            display = f"+54 9 {nums[:3]} {nums[3:6]}-{nums[6:]}"
        else:
            display = f"+54 9 {nums[:4]} {nums[4:6]}-{nums[6:]}"
    else:
        display = f"+54 9 {nums}"

    return display, wa_num

def extraer_email(texto):
    """Extrae el primer correo electrónico válido."""
    m = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', texto)
    return m.group(0).strip() if m else ""

def extraer_telefono(texto):
    """Detecta números de teléfono en el texto."""
    # Busca patrones telefónicos comunes
    patrones = [
        r'(?:\+?54\s*9?\s*)?(?:0?[1-9]\d{1,4})[\s.-]?(?:15[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}',
        r'\b\d{10}\b',
        r'\b\d{2,4}[\s.-]\d{6,8}\b'
    ]
    for pat in patrones:
        m = re.search(pat, texto)
        if m:
            candidato = m.group(0).strip()
            # Validar que tenga al menos 8 dígitos
            if len(re.sub(r'\D', '', candidato)) >= 8:
                return candidato
    return ""

def generar_slug(nombre):
    """Genera un slug limpio en minúsculas con guiones bajos."""
    s = normalizar_texto_sin_acentos(nombre)
    s = re.sub(r'\s+', '_', s.strip())
    return s or "postulante"

def generar_keywords_base(nombre, cargo, habilidades, experiencias):
    """Genera palabras clave completas para el buscador de tablero.html."""
    terminos = [nombre, cargo, "cv", "curriculum", "vitae", "postulante", "empleo", "jardin america", "misiones"]
    terminos.extend(habilidades)
    for exp in experiencias:
        if isinstance(exp, dict):
            terminos.append(exp.get("empresa", ""))
            terminos.append(exp.get("rol", ""))
        elif isinstance(exp, str):
            terminos.append(exp)
            
    texto_bruto = " ".join(terminos)
    limpio = normalizar_texto_sin_acentos(texto_bruto)
    palabras = [p for p in limpio.split() if len(p) > 2]
    # Eliminar duplicados manteniendo orden
    vistas = set()
    unicas = []
    for p in palabras:
        if p not in vistas:
            vistas.add(p)
            unicas.append(p)
    return " ".join(unicas)

def parsear_texto_cv(texto_crudo):
    """
    Analiza un texto plano de CV y lo estructura en un diccionario de datos.
    """
    lineas = [l.strip() for l in texto_crudo.splitlines() if l.strip()]
    if not lineas:
        return {}

    # Email y teléfono
    email = extraer_email(texto_crudo)
    tel_raw = extraer_telefono(texto_crudo)
    tel_display, tel_wa = normalizar_telefono_argentina(tel_raw)

    # Heurística para Nombre y Cargo (usualmente primeras líneas)
    idx = 0
    nombre = lineas[0] if len(lineas) > 0 else "Postulante"
    # Si la primera línea es un título genérico de CV, saltar a la siguiente
    if any(k in nombre.lower() for k in ["curriculum", "vitae", "cv", "resumen", "hoja de vida"]):
        idx = 1
        nombre = lineas[1] if len(lineas) > 1 else "Postulante"

    cargo = "Postulante"
    cargo_idx = idx + 1
    if len(lineas) > cargo_idx and lineas[cargo_idx] != nombre and "@" not in lineas[cargo_idx] and not any(c.isdigit() for c in lineas[cargo_idx][:5]):
        if not any(k in lineas[cargo_idx].lower() for k in ["tel", "email", "contacto", "perfil", "direccion", "barrio"]):
            cargo = lineas[cargo_idx]
            idx = cargo_idx

    # Detección de secciones
    secciones = {
        "perfil": [],
        "habilidades": [],
        "experiencias": [],
        "educacion": [],
        "contacto": []
    }

    sec_actual = "perfil"
    patrones_sec = {
        "perfil": ["perfil", "sobre mi", "resumen", "acerca de"],
        "habilidades": ["habilidades", "aptitudes", "competencias", "conocimientos"],
        "experiencias": ["experiencia", "historial laboral", "antecedentes", "empleos"],
        "educacion": ["educacion", "formacion", "estudios", "cursos", "capacitaciones"],
        "contacto": ["contacto", "datos personales", "datos de contacto"]
    }

    for l in lineas[2:]:
        l_norm = normalizar_texto_sin_acentos(l)
        cambio_sec = False
        for sec_name, palabras_clave in patrones_sec.items():
            if any(l_norm == k or l_norm.startswith(k + ":") or l_norm.startswith(k + " ") for k in palabras_clave):
                sec_actual = sec_name
                cambio_sec = True
                break
        if cambio_sec:
            continue

        if sec_actual == "habilidades":
            item = l.lstrip("•-*•1234567890. ")
            if item:
                secciones["habilidades"].append(item)
        elif sec_actual == "educacion":
            item = l.lstrip("•-*• ")
            if item:
                secciones["educacion"].append(item)
        elif sec_actual == "experiencias":
            secciones["experiencias"].append(l)
        elif sec_actual == "perfil":
            if "@" not in l and not re.search(r'\d{8,}', l):
                secciones["perfil"].append(l)

    # Estructura de experiencias agrupadas
    exp_estructuradas = []
    for exp_line in secciones["experiencias"]:
        exp_estructuradas.append({
            "empresa": exp_line,
            "fechas": "",
            "rol": "",
            "desc": ""
        })

    slug = generar_slug(nombre)
    keywords = generar_keywords_base(nombre, cargo, secciones["habilidades"], exp_estructuradas)

    descripcion_tarjeta = (
        f"{cargo} con experiencia y sólida formación. "
        f"Perfil proactivo, organizado y con alto compromiso laboral en Jardín América."
    )

    perfil_resumen = secciones["perfil"][:4] if secciones["perfil"] else [
        "Persona responsable, motivada y orientada a resultados,",
        "con capacidad de aprendizaje y compromiso profesional."
    ]

    return {
        "slug": slug,
        "nombre": nombre,
        "cargo": cargo,
        "subtitulo": f"{cargo} · Jardín América",
        "foto_path": "",
        "perfil_lineas": perfil_resumen,
        "habilidades": secciones["habilidades"][:7] if secciones["habilidades"] else ["Responsabilidad y Compromiso", "Puntualidad", "Atención al Público"],
        "experiencias": exp_estructuradas[:5],
        "educacion": secciones["educacion"][:4] if secciones["educacion"] else ["Secundario Completo"],
        "telefono_display": tel_display,
        "telefono_wa": tel_wa,
        "email": email,
        "direccion": "Jardín América, Misiones",
        "descripcion_tarjeta": descripcion_tarjeta,
        "keywords": keywords
    }

def modo_interactivo():
    """Asistente paso a paso en consola para cargar un nuevo CV."""
    print("\n" + "=" * 65)
    print("  ITe Jardín América — Asistente Interactivo de Carga de CV")
    print("=" * 65 + "\n")

    nombre = input("• Nombre y Apellido completo: ").strip()
    if not nombre:
        nombre = "Postulante"

    cargo = input("• Puesto / Profesión principal (ej: Supervisora, Administrativo): ").strip()
    if not cargo:
        cargo = "Postulante"

    subtitulo = input(f"• Especialidades o subtítulo (Enter para '{cargo}'): ").strip()
    if not subtitulo:
        subtitulo = cargo

    raw_tel = input("• Teléfono de contacto (ej: 11 7367-3799 o 3743 454291): ").strip()
    tel_display, tel_wa = normalizar_telefono_argentina(raw_tel)
    print(f"  -> Visualización: {tel_display}")
    print(f"  -> WhatsApp URL:  https://wa.me/{tel_wa}")

    email = input("• Correo electrónico (opcional): ").strip()
    direccion = input("• Domicilio / Barrio / Localidad (ej: Jardín América): ").strip()
    if not direccion:
        direccion = "Jardín América, Misiones"

    foto_path = input("• Ruta a la foto de perfil (dejar vacío si no tiene foto aún): ").strip()

    print("\n• Perfil profesional (ingrese 2 a 4 líneas de resumen, línea vacía para terminar):")
    perfil_lineas = []
    while True:
        linea = input("  > ").strip()
        if not linea:
            break
        perfil_lineas.append(linea)

    if not perfil_lineas:
        perfil_lineas = [
            "Persona responsable y proactiva con sólida vocación de servicio,",
            "orientada a mantener altos estándares de calidad y compromiso."
        ]

    print("\n• Habilidades y aptitudes (separadas por coma):")
    hab_raw = input("  > ").strip()
    if hab_raw:
        habilidades = [h.strip() for h in hab_raw.split(",") if h.strip()]
    else:
        habilidades = ["Responsabilidad y Compromiso", "Organización", "Atención al Público"]

    print("\n• Experiencia laboral (ingrese empresa o rol, fechas y responsabilidades):")
    experiencias = []
    while True:
        emp = input("  - Empresa / Empleo (Enter para finalizar): ").strip()
        if not emp:
            break
        fechas = input("    Fechas (ej: 2020 - 2023 o Actualidad): ").strip()
        rol = input("    Puesto / Rol desempeñado: ").strip()
        desc = input("    Tareas resumidas: ").strip()
        experiencias.append({
            "empresa": emp,
            "fechas": fechas,
            "rol": rol,
            "desc": desc
        })

    print("\n• Educación y Cursos (separados por coma o uno por línea, Enter para terminar):")
    educacion = []
    while True:
        ed = input("  - Título / Curso e Institución: ").strip()
        if not ed:
            break
        educacion.append(ed)

    desc_tarjeta = input(f"\n• Descripción resumida para la tarjeta web (Enter para generar automática):\n  > ").strip()
    if not desc_tarjeta:
        desc_tarjeta = f"{cargo} con experiencia comprobable en el rubro. Perfil con alto compromiso, responsabilidad, organización y capacidad de trabajo en equipo."

    slug = generar_slug(nombre)
    keywords = generar_keywords_base(nombre, cargo, habilidades, experiencias)

    datos = {
        "slug": slug,
        "nombre": nombre,
        "cargo": cargo,
        "subtitulo": subtitulo,
        "foto_path": foto_path,
        "perfil_lineas": perfil_lineas,
        "habilidades": habilidades,
        "experiencias": experiencias,
        "educacion": educacion,
        "telefono_display": tel_display,
        "telefono_wa": tel_wa,
        "email": email,
        "direccion": direccion,
        "descripcion_tarjeta": desc_tarjeta,
        "keywords": keywords
    }

    out_file = os.path.join(os.path.dirname(__file__), f"cv_{slug}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Perfil guardado exitosamente en: {out_file}")
    
    preg_generar = input("\n¿Desea generar el flyer y código HTML ahora mismo? (s/n): ").strip().lower()
    if preg_generar.startswith("s"):
        import generador_cv
        out_webp = os.path.join(r"d:\jardinamerica.ar\assets", f"cv_{slug}.webp")
        out_jpeg = os.path.join(r"d:\jardinamerica.ar\assets", f"cv_{slug}.jpeg")
        datos["asset_webp_name"] = f"cv_{slug}.webp"
        generador_cv.generar_flyer_cv(datos, out_webp, out_jpeg)
        
        tarjeta_num = generador_cv.calcular_proximo_numero_tarjeta()
        print("\n--- SNIPPET HTML GENERADO ---")
        print(generador_cv.generar_snippet_html(datos, tarjeta_num))

        preg_insertar = input(f"\n¿Desea insertar automáticamente la Tarjeta {tarjeta_num} en tablero.html? (s/n): ").strip().lower()
        if preg_insertar.startswith("s"):
            generador_cv.insertar_tarjeta_en_tablero(datos, tarjeta_num)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extractor y estructurador de datos para CVs de ITe")
    parser.add_argument("--interactivo", "-i", action="store_true", help="Iniciar asistente interactivo en consola")
    parser.add_argument("--texto", "-t", help="Ruta a un archivo de texto con el contenido del CV")
    parser.add_argument("--pegar", "-p", action="store_true", help="Pegar texto crudo desde consola")
    parser.add_argument("--out-json", "-o", help="Ruta de destino del archivo JSON generado")
    args = parser.parse_args()

    if args.interactivo:
        modo_interactivo()
    elif args.texto and os.path.exists(args.texto):
        with open(args.texto, "r", encoding="utf-8") as f:
            contenido = f.read()
        res = parsear_texto_cv(contenido)
        out = args.out_json or os.path.join(os.path.dirname(__file__), f"cv_{res.get('slug', 'nuevo')}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f"[OK] CV estructurado y guardado en: {out}")
    elif args.pegar:
        print("Pegue el texto del CV y presione Ctrl+Z (en Windows) o Ctrl+D (en Linux/Mac) seguido de Enter:")
        contenido = sys.stdin.read()
        res = parsear_texto_cv(contenido)
        out = args.out_json or os.path.join(os.path.dirname(__file__), f"cv_{res.get('slug', 'nuevo')}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] CV estructurado y guardado en: {out}")
    else:
        parser.print_help()
