#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verificar-espejo.py — compara el espejo español del manual con el inglés, página a página.

El espejo español (`09 - Manual oficial/manual-lts-2026-es`) es una traducción de
`manual-lts-2026-en`. Al traducirse en un momento dado, cuando YoYo Games actualiza
la versión inglesa (añade una sección, un tipo de evento, una plataforma nueva…) el
espejo español se queda desactualizado en silencio: la página existe, tiene buena
pinta, pero le faltan trozos. `Async_Events/System.md` es el caso que destapó esto:
66 líneas en español frente a 109 en inglés, con secciones enteras ausentes
(DeviceMotion, insets seguros, `permission_request_result`, `receipt_validation`).
Nadie había comprobado si pasaba en más sitios. Este script lo comprueba en las
~3100 páginas de la referencia.

Detecta tres defectos, DE MÁS A MENOS GRAVE (así se ordena también el informe):

  1. LITERALES TRADUCIDOS — el más peligroso, porque no se nota a simple vista.
     Dentro de un bloque de código (```) o de una línea con acento de código
     (`texto`), una cadena entre comillas casi siempre es un identificador o una
     constante de la API (`"hidden"`, `"event_type"`) que el motor compara tal
     cual: traducirla (`"oculto"`) no cambia la prosa, rompe el código de quien
     copie el ejemplo. Dentro de un bloque ``` se extrae cualquier cadena entre
     comillas dobles (es código de verdad, todo cuenta). Fuera de un bloque
     —en prosa— NO basta con que la línea tenga un acento de código en
     cualquier parte: una frase perfectamente normal («la capa "superior"…»)
     puede compartir línea con un enlace a otra función sin relación alguna.
     Solo cuenta cuando la comilla ENVUELVE directamente al acento —el patrón
     real de este manual, `"`event_type`"` o `` `"onResume"` ``— porque ahí sí
     es la API citándose a sí misma (y de paso cubre las tablas de claves, que
     siempre escriben la clave así). Los tokens de cada página se comparan
     entre inglés y español: uno que existe en el inglés y no aparece en
     ningún sitio del español es la señal del defecto. Se excluyen las líneas
     que llaman a funciones pensadas para mostrar texto al jugador
     (`show_message`, `draw_text`, `room_caption`…): esas SÍ pueden traducirse
     legítimamente y no son parte de un protocolo.

  2. PÁGINAS INCOMPLETAS — no se cuentan líneas en bruto: el español es más
     largo por naturaleza (frases más largas, tildes, „¿"/„¡"…) y esa métrica
     penaliza al idioma, no al contenido. En su lugar se comparan cuatro
     recuentos ESTRUCTURALES que no dependen de la prosa y deben coincidir casi
     exactamente entre idiomas:
       - encabezados (líneas que empiezan por `#`, fuera de bloques de código)
       - bloques de código (```…```)
       - filas de tabla (líneas que empiezan por `|`, sin contar la fila
         separadora de guiones)
       - enlaces (`[texto](destino)`)
     Si cualquiera de los cuatro cae por debajo del 90 % del valor inglés, la
     página está incompleta: le faltan secciones enteras, no solo palabras.

  3. PÁGINAS AUSENTES — la ruta existe en inglés y no tiene archivo español.

No se compara nunca por igualdad de longitud de línea ni por igualdad de texto:
todas las comparaciones son estructurales o de tokens de código, precisamente
para que la naturalidad de la traducción española no dispare falsos positivos.

Fuera de alcance a propósito: hay ~23 páginas que existen SOLO en español (de
una versión del manual anterior a la actual: UWP/Xbox Live, Opera GX antiguo,
`font_replace`, funciones GXC de grabación de vídeo…). Este script no las
señala porque no hay página inglesa con la que compararlas — son candidatas a
revisión aparte (¿siguen vigentes o hay que retirarlas?), no un defecto de
traducción.

Uso:
    python3 _indice/verificar-espejo.py              → informe completo
    python3 _indice/verificar-espejo.py --resumen    → solo el recuento final

Código de salida: 1 si hay algo grave (ausentes, incompletas o con literales
traducidos), 0 si el espejo está al día.

Rendimiento: recorre ~3100 páginas por idioma en unos segundos (solo lectura de
texto y expresiones regulares, sin llamadas externas), así que forma parte del
paso 11 de `actualizar.py`.
"""
import os
import re
import sys

# Windows: en cuanto la salida no es una consola interactiva (pipes, «> archivo», o el
# propio actualizar.py capturando la salida de este script vía subprocess), sys.stdout
# usa la página de códigos ANSI del sistema en vez de UTF-8 — y los símbolos ✗/⚠/→/…
# de este código no caben ahí: UnicodeEncodeError a mitad de ejecución. No verificado
# en Windows de verdad; aplica la solución estándar de Python 3.7+ (PEP 528 cubre la
# consola interactiva sola, no pipes ni redirecciones).
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RAIZ, "09 - Manual oficial")
EN = os.path.join(BASE, "manual-lts-2026-en")
ES = os.path.join(BASE, "manual-lts-2026-es")

UMBRAL = 0.90  # por debajo de esto, la página está incompleta

RE_HEADER = re.compile(r"^#{1,6}\s+\S")
RE_SEP_TABLA = re.compile(r"^\|[\s:\-|]+\|?$")
RE_ENLACE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
RE_COMILLAS = re.compile(r'"([^"\n]{1,50})"')
# Fuera de bloques ``` una comilla NO basta para marcar código: una frase de
# prosa perfectamente normal («la capa "superior"…») puede compartir línea con
# un enlace `a_otra_función()` sin relación. Solo cuenta como literal de
# protocolo cuando la comilla ENVUELVE directamente un acento de código —el
# patrón real del manual, "`event_type`" o `"onResume"`— porque ahí sí es la
# API citándose a sí misma, no una palabra resaltada por énfasis.
RE_COMILLAS_CODIGO_A = re.compile(r'"`([^`\n]{1,50})`"')   # "`token`"
RE_COMILLAS_CODIGO_B = re.compile(r'`"([^"\n]{1,50})"`')   # `"token"`
RE_LETRA = re.compile(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]")

# Funciones que muestran texto al jugador: sus cadenas SÍ pueden traducirse
# legítimamente (son diálogo, no protocolo), así que se excluyen del cotejo
# de literales para no llenar el informe de falsos positivos.
RE_TEXTO_LOCALIZABLE = re.compile(
    r"\b(show_message\w*|show_question\w*|show_error|draw_text\w*|room_caption|"
    r"dialog_message|get_string\w*|get_login_async|highscore_add|clickable_add)\b"
)


def leer(ruta):
    try:
        with open(ruta, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def token_valido(t):
    """Filtra ruido: solo interesan tokens cortos con al menos una letra —
    los identificadores y constantes de protocolo—, no frases largas de prosa
    que coincidan por casualidad con el patrón de comillas.

    Un token con espacio al principio o al final SIEMPRE es ruido: pasa cuando
    dos términos consecutivos entre comillas van unidos por un conector
    («"`rm_A`" and "`rm_B`"») y el patrón de adyacencia comilla+acento atrapa
    el hueco de en medio (" and "), no un literal real — ningún literal
    auténtico del manual lleva espacios sobrantes en los bordes."""
    if not t or t != t.strip():
        return False
    if len(t) > 50:
        return False
    if not RE_LETRA.search(t):
        return False
    if len(t.split()) > 6:
        return False
    return True


def analizar(texto):
    """Recuentos estructurales + literales de código de una página."""
    headers = 0
    bloques = 0
    filas_tabla = 0
    en_bloque = False
    literales = set()
    lineas_prosa = []
    for linea in texto.split("\n"):
        rec = linea.strip()
        if rec.startswith("```"):
            bloques += 0 if en_bloque else 1
            en_bloque = not en_bloque
            continue
        if en_bloque:
            if not RE_TEXTO_LOCALIZABLE.search(linea):
                literales.update(RE_COMILLAS.findall(linea))
            continue
        lineas_prosa.append(linea)
        if RE_HEADER.match(rec):
            headers += 1
        if rec.startswith("|") and not RE_SEP_TABLA.match(rec):
            filas_tabla += 1
        if "`" in linea and not RE_TEXTO_LOCALIZABLE.search(linea):
            literales.update(RE_COMILLAS_CODIGO_A.findall(linea))
            literales.update(RE_COMILLAS_CODIGO_B.findall(linea))
    texto_prosa = "\n".join(lineas_prosa)
    enlaces = len(RE_ENLACE.findall(texto_prosa))
    literales = {t for t in literales if token_valido(t)}
    return {
        "headers": headers,
        "bloques_codigo": bloques,
        "filas_tabla": filas_tabla,
        "enlaces": enlaces,
        "literales": literales,
    }


NOMBRES_METRICA = {
    "headers": "encabezados",
    "bloques_codigo": "bloques de código",
    "filas_tabla": "filas de tabla",
    "enlaces": "enlaces",
}

# Peso de cada métrica al ordenar por gravedad: un encabezado o un bloque de
# código que falta es una SECCIÓN entera perdida; un enlace que falta suele
# ser una única referencia cruzada reformulada en línea. Ordenar solo por el
# ratio más bajo hace que una página con un único enlace ausente (0/1 = 0 %)
# tape a una que ha perdido 22 de 24 encabezados (8 %, pero un desastre real);
# por eso se pondera por la cantidad ABSOLUTA de contenido perdido, no por el
# porcentaje desnudo.
PESO_METRICA = {"headers": 3, "bloques_codigo": 3, "filas_tabla": 2, "enlaces": 1}


def comparar():
    ausentes = []
    incompletas = []   # (gravedad, rel, [(metrica, en, es, ratio), ...])
    con_literales = []  # (n_defectos, rel, faltan, nuevas)

    rutas_en = []
    for raiz, _dirs, files in os.walk(EN):
        for f in files:
            if f.endswith(".md"):
                rutas_en.append(os.path.relpath(os.path.join(raiz, f), EN))
    rutas_en.sort()

    comparadas = 0
    for rel in rutas_en:
        ruta_en = os.path.join(EN, rel)
        ruta_es = os.path.join(ES, rel)
        if not os.path.isfile(ruta_es):
            ausentes.append(rel)
            continue
        comparadas += 1
        m_en = analizar(leer(ruta_en))
        m_es = analizar(leer(ruta_es))

        detalle = []
        gravedad = 0
        for clave in ("headers", "bloques_codigo", "filas_tabla", "enlaces"):
            v_en = m_en[clave]
            if v_en == 0:
                continue
            v_es = m_es[clave]
            ratio = v_es / v_en
            if ratio < UMBRAL:
                detalle.append((clave, v_en, v_es, ratio))
                gravedad += PESO_METRICA[clave] * (v_en - v_es)
        if detalle:
            incompletas.append((gravedad, rel, detalle))

        faltan = sorted(t for t in m_en["literales"] if t not in m_es["literales"])
        nuevas = sorted(t for t in m_es["literales"] if t not in m_en["literales"])
        if faltan:
            con_literales.append((len(faltan), rel, faltan, nuevas))

    incompletas.sort(key=lambda x: -x[0])             # más contenido perdido primero
    con_literales.sort(key=lambda x: -x[0])           # más literales perdidos primero

    return comparadas, ausentes, incompletas, con_literales


def informe(resumen_solo=False):
    comparadas, ausentes, incompletas, con_literales = comparar()

    # Cero páginas comparadas NO es «todo bien»: es «no he mirado nada». Pasa en un
    # clon recién sacado de GitHub, donde «09 - Manual oficial» no viaja (se
    # reconstruye con `reconstruir.sh`). Decir «0 ausentes» en esa situación es un
    # falso verde de manual: el espejo podría estar entero, medio o vacío y la
    # respuesta sería la misma. Sale con 2 —«no se ha podido comprobar»—, que es
    # distinto de 0 y de 1, y explica cuál de los dos casos es.
    if comparadas == 0 and not ausentes:
        hay_en = os.path.isdir(EN)
        hay_es = os.path.isdir(ES)
        print("· No se ha comparado ni una página.")
        if not hay_en and not hay_es:
            print("  El manual no está en este clon: «09 - Manual oficial» no se publica en")
            print("  GitHub, se reconstruye con `./reconstruir.sh`. No es un fallo del espejo,")
            print("  pero tampoco es una comprobación: no se ha mirado nada.")
        elif not hay_es:
            print(f"  Está el manual en inglés pero NO el espejo español ({ES}).")
        elif not hay_en:
            print(f"  Está el espejo español pero NO el manual en inglés ({EN}).")
        else:
            print("  Las dos carpetas existen pero no hay ni un .md que comparar: revisa")
            print("  si el volcado del manual quedó a medias.")
        return 2

    print(f"{comparadas} páginas comparadas · {len(ausentes)} ausentes · "
          f"{len(incompletas)} incompletas · {len(con_literales)} con literales traducidos\n")

    if resumen_solo:
        return 1 if (ausentes or incompletas or con_literales) else 0

    if con_literales:
        print("\033[1m1. LITERALES TRADUCIDOS (el más peligroso)\033[0m")
        for n, rel, faltan, nuevas in con_literales:
            print(f"  ✗ {rel}")
            print(f"      faltan en ES: {', '.join(repr(t) for t in faltan[:8])}"
                  + (" …" if len(faltan) > 8 else ""))
            if nuevas:
                print(f"      solo en ES (posible traducción): "
                      f"{', '.join(repr(t) for t in nuevas[:8])}"
                      + (" …" if len(nuevas) > 8 else ""))
        print()

    if incompletas:
        print("\033[1m2. PÁGINAS INCOMPLETAS (por debajo del 90 % del inglés)\033[0m")
        for _gravedad, rel, detalle in incompletas:
            resumen = ", ".join(
                f"{NOMBRES_METRICA[c]} {es}/{en} ({int(r * 100)} %)"
                for c, en, es, r in detalle
            )
            print(f"  ✗ {rel}\n      {resumen}")
        print()

    if ausentes:
        print("\033[1m3. PÁGINAS AUSENTES EN ESPAÑOL\033[0m")
        for rel in ausentes:
            print(f"  ✗ {rel}")
        print()

    return 1 if (ausentes or incompletas or con_literales) else 0


def autoprueba():
    """Las tres salidas posibles, cada una provocada de verdad.

    El caso que motiva esta autoprueba es el tercero: durante mucho tiempo, un
    árbol sin manual devolvía «0 páginas comparadas · 0 ausentes» y **exit 0**.
    Leído deprisa, eso dice «el espejo está perfecto». Decía «no he mirado nada».
    """
    global EN, ES
    import shutil
    import tempfile

    guardar = (EN, ES)
    fallos = []

    def revisar(nombre, ok, detalle=""):
        if ok:
            print("  \u2713 " + nombre)
        else:
            fallos.append(nombre)
            print("  \u2717 %s  ->  %s" % (nombre, detalle))

    def escribir(ruta, texto):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)

    # Una página con la misma estructura en los dos idiomas: encabezados, un
    # bloque de código y una tabla. Los literales de código NO se traducen.
    PAG_EN = ("# Title\n\n## Section\n\n```gml\nvar _x = draw_sprite(spr_a, 0, 0, 0);\n```\n\n"
              "| A | B |\n|---|---|\n| 1 | 2 |\n\nSee [link](https://ejemplo.com).\n")
    PAG_ES = ("# Título\n\n## Sección\n\n```gml\nvar _x = draw_sprite(spr_a, 0, 0, 0);\n```\n\n"
              "| A | B |\n|---|---|\n| 1 | 2 |\n\nVer [enlace](https://ejemplo.com).\n")

    try:
        with tempfile.TemporaryDirectory() as tmp:
            # a · Ni una carpeta: «no se ha podido comprobar», nunca «todo bien».
            EN = os.path.join(tmp, "no-existe-en")
            ES = os.path.join(tmp, "no-existe-es")
            revisar("sin manual devuelve 2, no 0", informe(resumen_solo=True) == 2)

            # b · Espejo completo: 0.
            EN = os.path.join(tmp, "en")
            ES = os.path.join(tmp, "es")
            escribir(os.path.join(EN, "a.md"), PAG_EN)
            escribir(os.path.join(ES, "a.md"), PAG_ES)
            revisar("un espejo completo devuelve 0", informe(resumen_solo=True) == 0)

            # c · Falta una página en español: 1.
            escribir(os.path.join(EN, "b.md"), PAG_EN)
            revisar("una página ausente devuelve 1", informe(resumen_solo=True) == 1)

            # d · Existe pero recortada a la mitad: también 1.
            shutil.rmtree(ES)
            escribir(os.path.join(ES, "a.md"), PAG_ES)
            escribir(os.path.join(ES, "b.md"), "# Título\n")
            revisar("una página incompleta devuelve 1", informe(resumen_solo=True) == 1)

            # e · Las dos carpetas existen pero están vacías: sigue siendo 2, y con
            #     un motivo distinto al de (a). Un árbol a medio volcar no es un
            #     espejo perfecto.
            shutil.rmtree(EN); shutil.rmtree(ES)
            os.makedirs(EN); os.makedirs(ES)
            revisar("dos carpetas vacías devuelven 2", informe(resumen_solo=True) == 2)
    finally:
        EN, ES = guardar

    if fallos:
        print("\n\u2717 %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n\u2713 Las 5 comprobaciones de la autoprueba pasan.")
    return 0


import os as _os_arg, sys as _sys_arg
_sys_arg.path.insert(0, _os_arg.path.dirname(_os_arg.path.abspath(__file__)))
from argumentos import exigir_sin_rutas  # noqa: E402

if __name__ == "__main__":
    _sobra = exigir_sin_rutas('Compara el manual de esta biblioteca. Para el detalle, sin `--resumen`.',
                             ("--resumen", "--autoprueba"))
    if _sobra:
        sys.exit(_sobra)
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(informe(resumen_solo="--resumen" in sys.argv))
