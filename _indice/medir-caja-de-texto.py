#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mide si el texto de cada idioma CABE, antes de que se salga en pantalla.

El desbordamiento de texto es el fallo silencioso clásico de un juego traducido:
no da error, no rompe la compilación, no aparece en las pruebas del idioma en que
se escribió. Aparece en una captura de pantalla, cuando ya está publicado.

Tres cosas que esta herramienta convierte en comprobación, y las tres salen de
medidas, no de reglas de oro:

  1. **«Diseña con el idioma más largo» no se puede aplicar en bloque.** Medido
     sobre una tabla real de 79 claves: el español era un 9,1 % más largo *en
     total*, y aun así **en 23 de las 79 cadenas ganaba el inglés**, hasta 26 px.
     Una cadena que cabe de media puede desbordar igual. Hay que medir CADA una.
  2. **Un carácter que no está en el mapa de la fuente mide cero.** No da error:
     la palabra sale mutilada y la cuenta de anchura miente a tu favor. Por eso
     aquí se listan aparte los caracteres ausentes.
  3. **El espacio es el caso peor.** Si la hoja no trae celda para el espacio,
     `font_add_sprite_ext` usa «la anchura del carácter más ancho» (`08 · 03`),
     no la del espacio. Una frase de ocho palabras se ensancha 40 px de golpe y
     toda la aritmética de la caja se cae.

Cómo mide. Reproduce lo que hace `font_add_sprite_ext(spr, mapa, prop, sep)`: la
hoja se parte en celdas iguales, cada celda es un glifo en el orden del mapa, y
con `prop = true` el avance es **la anchura pintada + `sep`**. Con `prop = false`
es la celda entera + `sep`. No aplica kerning, porque esa función tampoco.

Uso:
    python3 _indice/medir-caja-de-texto.py idiomas/*.json \\
        --hoja fuente.png --celda 8x16 --mapa-archivo mapa.txt --caja 356

    …  --sep 1 --sin-proporcional        (prop = false)
    …  --escala 1.5                      (la caja útil al 150 % de accesibilidad)
    …  --mapa "ABCDEFG…"                 (el mapa en línea, si es corto)
    …  --espacio 4                        (responde a «¿y si añadimos la celda del espacio?»)

Sale con **0** si todo cabe, **1** si algo desborda o faltan caracteres, y **2**
si no ha podido medir. No escribe nada.
"""
import json
import os
import re
import struct
import sys
import zlib

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


# ───────────────────── PNG a mano: sin depender de Pillow ─────────────────────
def leer_png(ruta):
    """(ancho, alto, filas RGBA) o (None, motivo, None).

    Se decodifica aquí en vez de pedir Pillow porque esta herramienta tiene que
    poder correr en un clon recién hecho, sin instalar nada. Cubre 8 bits en
    color 0 (gris), 2 (RGB), 3 (paleta), 4 (gris+alfa) y 6 (RGBA), que es todo lo
    que exporta un editor de pixel art.
    """
    try:
        with open(ruta, "rb") as f:
            datos = f.read()
    except OSError as e:
        return None, f"no se pudo abrir: {e}", None
    if datos[:8] != b"\x89PNG\r\n\x1a\n":
        return None, "no es un PNG", None

    pos, comprimido, paleta, trans = 8, b"", None, None
    ancho = alto = prof = tipo = entrelazado = None
    while pos + 8 <= len(datos):
        largo = int.from_bytes(datos[pos:pos + 4], "big")
        tag = datos[pos + 4:pos + 8]
        cuerpo = datos[pos + 8:pos + 8 + largo]
        pos += 12 + largo
        if tag == b"IHDR":
            ancho, alto, prof, tipo, _, _, entrelazado = struct.unpack(">IIBBBBB", cuerpo)
        elif tag == b"PLTE":
            paleta = cuerpo
        elif tag == b"tRNS":
            trans = cuerpo
        elif tag == b"IDAT":
            comprimido += cuerpo
        elif tag == b"IEND":
            break
    if ancho is None:
        return None, "PNG sin cabecera IHDR", None
    if prof != 8:
        return None, f"profundidad {prof} bits: solo se leen 8", None
    if entrelazado:
        return None, "PNG entrelazado (Adam7): vuelve a exportarlo sin entrelazar", None
    canales = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(tipo)
    if canales is None:
        return None, f"tipo de color {tipo} no contemplado", None

    try:
        crudo = zlib.decompress(comprimido)
    except zlib.error as e:
        return None, f"los datos del PNG no se dejan descomprimir: {e}", None

    ancho_linea = ancho * canales
    filas, previa, i = [], bytearray(ancho_linea), 0
    for _ in range(alto):
        if i >= len(crudo):
            return None, "el PNG se corta antes de tiempo", None
        filtro = crudo[i]
        i += 1
        linea = bytearray(crudo[i:i + ancho_linea])
        if len(linea) < ancho_linea:
            return None, "el PNG se corta antes de tiempo", None
        i += ancho_linea
        for x in range(ancho_linea):
            a = linea[x - canales] if x >= canales else 0
            b = previa[x]
            c = previa[x - canales] if x >= canales else 0
            v = linea[x]
            if filtro == 1:
                v += a
            elif filtro == 2:
                v += b
            elif filtro == 3:
                v += (a + b) >> 1
            elif filtro == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                v += a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
            elif filtro != 0:
                return None, f"filtro PNG desconocido: {filtro}", None
            linea[x] = v & 0xFF
        previa = linea
        filas.append(_a_rgba(linea, ancho, tipo, paleta, trans))
    return ancho, alto, filas


def _a_rgba(linea, ancho, tipo, paleta, trans):
    """Solo interesa el alfa, pero se normaliza entero para no volver a pensarlo."""
    salida = bytearray(ancho * 4)
    for x in range(ancho):
        if tipo == 6:
            salida[x * 4:x * 4 + 4] = linea[x * 4:x * 4 + 4]
        elif tipo == 2:
            salida[x * 4:x * 4 + 3] = linea[x * 3:x * 3 + 3]
            salida[x * 4 + 3] = 255
        elif tipo == 0:
            g = linea[x]
            salida[x * 4:x * 4 + 4] = bytes((g, g, g, 255))
        elif tipo == 4:
            g, a = linea[x * 2], linea[x * 2 + 1]
            salida[x * 4:x * 4 + 4] = bytes((g, g, g, a))
        elif tipo == 3:
            idx = linea[x]
            if paleta and idx * 3 + 3 <= len(paleta):
                salida[x * 4:x * 4 + 3] = paleta[idx * 3:idx * 3 + 3]
            a = 255
            if trans and idx < len(trans):
                a = trans[idx]
            salida[x * 4 + 3] = a
    return bytes(salida)


# ───────────────────────────── métricas de la hoja ────────────────────────────
def anchuras(ruta_hoja, celda_w, celda_h, mapa, sep, proporcional):
    """{carácter: avance en px}, o (None, motivo).

    Reproduce `font_add_sprite_ext`: la hoja se parte en celdas iguales de
    izquierda a derecha y de arriba abajo, y cada una es el glifo del carácter que
    ocupa esa posición en el mapa.
    """
    ancho, alto, filas = leer_png(ruta_hoja)
    if ancho is None:
        return None, alto
    columnas = ancho // celda_w
    if columnas < 1:
        return None, (f"la hoja mide {ancho} px de ancho y la celda {celda_w}: "
                      "no cabe ni un glifo")
    capacidad = columnas * (alto // celda_h)
    if capacidad < len(mapa):
        return None, (f"el mapa tiene {len(mapa)} caracteres y la hoja solo da para "
                      f"{capacidad} celdas de {celda_w}×{celda_h}. Uno de los dos miente, "
                      "y el resultado sería una fuente descuadrada glifo a glifo.")

    tabla = {}
    for i, ch in enumerate(mapa):
        cx, cy = (i % columnas) * celda_w, (i // columnas) * celda_h
        if not proporcional:
            tabla[ch] = celda_w + sep
            continue
        izq, der = None, None
        for y in range(cy, min(cy + celda_h, alto)):
            fila = filas[y]
            for x in range(cx, min(cx + celda_w, ancho)):
                if fila[x * 4 + 3] > 0:
                    if izq is None or x < izq:
                        izq = x
                    if der is None or x > der:
                        der = x
        pintado = 0 if izq is None else (der - izq + 1)
        tabla[ch] = pintado + sep
    return tabla, None


def medir(cadena, tabla, ancho_espacio_sin_glifo):
    """(px, caracteres ausentes). Un ausente suma 0 — que es justo el problema."""
    total, faltan = 0, []
    for ch in cadena:
        if ch in tabla:
            total += tabla[ch]
        elif ch == " ":
            total += ancho_espacio_sin_glifo
        else:
            faltan.append(ch)
    return total, faltan


def palabra_mas_ancha(cadena, tabla, ancho_espacio):
    peor, cual = 0, ""
    for p in cadena.split(" "):
        w, _ = medir(p, tabla, ancho_espacio)
        if w > peor:
            peor, cual = w, p
    return peor, cual


def main():
    args = sys.argv[1:]
    if not args or "--help" in args or "-h" in args:
        print(__doc__.strip())
        return 0 if ("--help" in args or "-h" in args) else 2

    def sacar(bandera, por_defecto=None):
        if bandera in args:
            i = args.index(bandera)
            if i + 1 >= len(args):
                print(f"✗ `{bandera}` necesita un valor.")
                sys.exit(2)
            v = args[i + 1]
            del args[i:i + 2]
            return v
        return por_defecto

    hoja = sacar("--hoja")
    celda = sacar("--celda")
    mapa_txt = sacar("--mapa")
    mapa_arch = sacar("--mapa-archivo")
    caja = sacar("--caja")
    sep = sacar("--sep", "1")
    escala = sacar("--escala", "1")
    espacio_forzado = sacar("--espacio")
    proporcional = "--sin-proporcional" not in args
    if not proporcional:
        args.remove("--sin-proporcional")

    if not (hoja and celda and caja and (mapa_txt or mapa_arch)):
        print("✗ Faltan `--hoja`, `--celda`, `--caja` y el mapa (`--mapa` o `--mapa-archivo`).")
        return 2
    m = re.fullmatch(r"(\d+)x(\d+)", celda.strip())
    if not m:
        print(f"✗ `--celda` se escribe como 8x16, no «{celda}».")
        return 2
    celda_w, celda_h = int(m.group(1)), int(m.group(2))
    try:
        caja_px = float(caja) / float(escala)
        sep_n = int(sep)
    except ValueError:
        print("✗ `--caja`, `--escala` y `--sep` tienen que ser números.")
        return 2

    if mapa_arch:
        try:
            with open(mapa_arch, encoding="utf-8") as f:
                mapa = f.read().replace("\n", "")
        except OSError as e:
            print(f"⚠ no se pudo leer el mapa: {e}")
            return 2
    else:
        mapa = mapa_txt

    tabla, motivo = anchuras(hoja, celda_w, celda_h, mapa, sep_n, proporcional)
    if tabla is None:
        print(f"⚠ {motivo}")
        return 2

    if espacio_forzado is not None:
        try:
            espacio = int(espacio_forzado)
        except ValueError:
            print(f"✗ `--espacio` tiene que ser un entero, no «{espacio_forzado}».")
            return 2
        nota_espacio = (f"el espacio se ha FORZADO a {espacio} px. Esto responde a «¿y si "
                        "añadimos su celda?»; no es lo que hará GameMaker hoy.")
    elif " " in tabla:
        espacio = tabla[" "]
        nota_espacio = f"el espacio tiene su celda y mide {espacio} px"
    else:
        espacio = max(tabla.values()) if tabla else 0
        nota_espacio = (f"⚠ el mapa NO trae el espacio, así que GameMaker usará la anchura "
                        f"del carácter más ancho: {espacio} px, no la del espacio. "
                        "Añade su celda a la hoja o toda esta cuenta va a quedarse corta.")

    ficheros = [a for a in args if not a.startswith("--")]
    if not ficheros:
        print("✗ Falta al menos un JSON de idioma.")
        return 2

    idiomas, problemas = {}, 0
    for ruta in ficheros:
        try:
            with open(ruta, encoding="utf-8") as f:
                datos = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"⚠ «{ruta}»: {e}")
            return 2
        if not isinstance(datos, dict):
            print(f"⚠ «{ruta}» no es un objeto de clave → texto.")
            return 2
        idiomas[os.path.splitext(os.path.basename(ruta))[0]] = datos

    print(f"── caja útil: {caja_px:.0f} px" + (f" (de {caja} al {float(escala):g}×)"
                                               if float(escala) != 1 else ""))
    print(f"── {nota_espacio}")
    print(f"── {len(tabla)} glifos en el mapa · sep = {sep_n} · "
          f"{'proporcional' if proporcional else 'monoespaciado'}\n")

    todas = sorted(set().union(*(set(d) for d in idiomas.values())) if idiomas else [])
    ausentes_global, desbordes, ganadores = {}, [], {}
    for clave in todas:
        anchos = {}
        for idi, datos in idiomas.items():
            if clave not in datos:
                print(f"  ✗ «{clave}» falta en «{idi}». Una clave sin traducir se dibuja "
                      "como la clave: visible y fea, que es lo correcto — pero no se publica así.")
                problemas += 1
                continue
            px, faltan = medir(str(datos[clave]), tabla, espacio)
            anchos[idi] = px
            for ch in faltan:
                ausentes_global.setdefault(ch, []).append(f"{idi}:{clave}")
            if px > caja_px:
                desbordes.append((clave, idi, px))
            ancha, palabra = palabra_mas_ancha(str(datos[clave]), tabla, espacio)
            if ancha > caja_px:
                print(f"  ✗ «{clave}» [{idi}]: la palabra «{palabra}» mide {ancha:.0f} px "
                      f"ella sola y la caja son {caja_px:.0f}. Partir la línea no lo arregla.")
                problemas += 1
        if len(anchos) > 1:
            ganadores[clave] = max(anchos, key=anchos.get)

    if desbordes:
        print(f"\n  ✗ {len(desbordes)} cadena(s) NO caben en una línea:")
        for clave, idi, px in sorted(desbordes, key=lambda t: -t[2])[:25]:
            print(f"      {clave} [{idi}]: {px:.0f} px > {caja_px:.0f}")
        if len(desbordes) > 25:
            print(f"      … y {len(desbordes) - 25} más")
        problemas += len(desbordes)

    if ausentes_global:
        print(f"\n  ✗ {len(ausentes_global)} carácter(es) que NO están en el mapa de la "
              "fuente. Cada uno mide CERO: la palabra sale mutilada y esta cuenta se queda "
              "corta, sin que salte ningún error.")
        for ch, donde in sorted(ausentes_global.items()):
            print(f"      «{ch}» (U+{ord(ch):04X}) en {len(donde)} cadena(s), "
                  f"p. ej. {donde[0]}")
        problemas += len(ausentes_global)

    if len(idiomas) > 1 and ganadores:
        cuenta = {}
        for idi in ganadores.values():
            cuenta[idi] = cuenta.get(idi, 0) + 1
        reparto = " · ".join(f"{k}: {v}" for k, v in sorted(cuenta.items(),
                                                            key=lambda t: -t[1]))
        print(f"\n── qué idioma es el más largo, CADENA A CADENA: {reparto}")
        if len(cuenta) > 1:
            print("   No hay un «idioma más largo» que valga para todas. Diseñar la caja "
                  "con el que gana de media deja fuera a las demás: la regla se aplica "
                  "cadena a cadena, y por eso esta herramienta existe.")

    print()
    if problemas:
        print(f"✗ {problemas} problema(s). Nada de esto da error en tiempo de ejecución: "
              "sale en pantalla.")
        return 1
    print("✓ Todo cabe. Lo que esto NO comprueba: si se entiende, si el salto de línea cae "
          "donde debe, y que `font_add_sprite_ext` no aplica kerning — tampoco aquí.")
    return 0


# ─────────────────────────────── autoprueba ───────────────────────────────────
def _png(ancho, alto, pintar, tipo=6):
    """Un PNG de verdad, escrito a mano. `pintar(x, y)` dice si ese píxel es opaco."""
    if tipo == 6:
        crudo = b"".join(
            b"\x00" + b"".join((b"\xff\x00\x00\xff" if pintar(x, y) else b"\x00\x00\x00\x00")
                               for x in range(ancho))
            for y in range(alto))
        extra = b""
    else:                                     # tipo 3: paleta, con tRNS
        crudo = b"".join(b"\x00" + bytes(1 if pintar(x, y) else 0 for x in range(ancho))
                         for y in range(alto))
        extra = None

    def trozo(tag, datos):
        return (struct.pack(">I", len(datos)) + tag + datos
                + struct.pack(">I", zlib.crc32(tag + datos) & 0xFFFFFFFF))

    salida = b"\x89PNG\r\n\x1a\n" + trozo(
        b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, tipo, 0, 0, 0))
    if tipo == 3:
        salida += trozo(b"PLTE", b"\x00\x00\x00\xff\x00\x00")
        salida += trozo(b"tRNS", b"\x00\xff")
    return salida + trozo(b"IDAT", zlib.compress(crudo)) + trozo(b"IEND", b"")


def autoprueba():
    import subprocess
    import tempfile
    fallos = []

    def caso(nombre, condicion, detalle=""):
        if condicion:
            print(f"  ✓ {nombre}")
        else:
            print(f"  ✗ {nombre}{(' — ' + detalle) if detalle else ''}")
            fallos.append(nombre)

    with tempfile.TemporaryDirectory() as tmp:
        # Hoja de 4 celdas de 8×8. El glifo i-ésimo pinta (i+1) px de ancho,
        # empezando en la columna 2 de su celda: así la anchura PINTADA es
        # distinta de la celda y se ve si el proporcional funciona.
        def pintar(x, y):
            celda, dentro = x // 8, x % 8
            return celda < 4 and 2 <= dentro < 2 + (celda + 1) and 1 <= y < 7
        hoja = os.path.join(tmp, "hoja.png")
        with open(hoja, "wb") as f:
            f.write(_png(32, 8, pintar))

        a, al, filas = leer_png(hoja)
        caso("el descodificador de PNG lee las dimensiones", (a, al) == (32, 8), f"{a}×{al}")
        caso("y lee el canal alfa donde toca",
             filas[3][(2) * 4 + 3] == 255 and filas[3][0 * 4 + 3] == 0)

        pal = os.path.join(tmp, "paleta.png")
        with open(pal, "wb") as f:
            f.write(_png(32, 8, pintar, tipo=3))
        a2, _, filas2 = leer_png(pal)
        caso("un PNG con paleta y tRNS también se lee",
             a2 == 32 and filas2[3][2 * 4 + 3] == 255, str(a2))

        with open(os.path.join(tmp, "roto.png"), "wb") as f:
            f.write(b"no soy un png")
        r, motivo, _ = leer_png(os.path.join(tmp, "roto.png"))
        caso("un archivo que no es PNG da motivo, no excepción", r is None and bool(motivo))

        t, motivo = anchuras(hoja, 8, 8, "abcd", 1, True)
        caso("proporcional: avance = pintado + sep",
             t == {"a": 2, "b": 3, "c": 4, "d": 5}, str(t))

        t2, _ = anchuras(hoja, 8, 8, "abcd", 1, False)
        caso("monoespaciado: avance = celda + sep",
             all(v == 9 for v in t2.values()), str(t2))

        t3, motivo3 = anchuras(hoja, 8, 8, "abcdefghij", 1, True)
        caso("un mapa más largo que la hoja no se inventa glifos: da motivo",
             t3 is None and "mapa tiene 10" in motivo3, str(motivo3))

        px, faltan = medir("ab", t, 99)
        caso("medir suma los avances", px == 5, str(px))
        px, faltan = medir("añ", t, 99)
        caso("y devuelve aparte los caracteres que NO están en el mapa",
             faltan == ["ñ"] and px == 2, f"{px} {faltan}")

        px, _ = medir("a b", t, 99)
        caso("sin glifo de espacio, el espacio cuesta lo que se le pase",
             px == 2 + 99 + 3, str(px))

        t4, _ = anchuras(hoja, 8, 8, "ab d", 1, True)   # el 3.º es el espacio
        caso("si el mapa trae el espacio, tiene su propia anchura",
             " " in t4 and t4[" "] == 4, str(t4.get(" ")))

        ancha, palabra = palabra_mas_ancha("a bbbb", t, 1)
        caso("palabra_mas_ancha encuentra la peor", palabra == "bbbb" and ancha == 12,
             f"{palabra} {ancha}")

        # Extremo a extremo, que es donde de verdad se ve si el contrato se cumple.
        mapa = os.path.join(tmp, "mapa.txt")
        with open(mapa, "w", encoding="utf-8") as f:
            f.write("abcd")
        es = os.path.join(tmp, "es.json")
        en = os.path.join(tmp, "en.json")
        with open(es, "w", encoding="utf-8") as f:
            json.dump({"k1": "aa", "k2": "dddd"}, f)
        with open(en, "w", encoding="utf-8") as f:
            json.dump({"k1": "dddd", "k2": "aa"}, f)

        def correr(*extra):
            return subprocess.run(
                [sys.executable, __file__, es, en, "--hoja", hoja, "--celda", "8x8",
                 "--mapa-archivo", mapa, *extra],
                capture_output=True, text=True)

        r = correr("--caja", "100")
        caso("con caja de sobra, sale 0", r.returncode == 0, r.stdout[-200:])
        caso("y dice que ningún idioma gana siempre",
             "cadena a cadena" in r.stdout and "es: 1" in r.stdout and "en: 1" in r.stdout,
             r.stdout[-300:])

        r = correr("--caja", "10")
        caso("con caja estrecha, sale 1", r.returncode == 1, str(r.returncode))
        caso("y nombra la cadena que no cabe", "k2 [es]" in r.stdout or "k1 [en]" in r.stdout,
             r.stdout[-300:])

        r = correr("--caja", "100", "--escala", "10")
        caso("la escala de accesibilidad estrecha la caja de verdad",
             r.returncode == 1, r.stdout[-200:])

        with open(os.path.join(tmp, "falta.json"), "w", encoding="utf-8") as f:
            json.dump({"k1": "aa"}, f)
        r = subprocess.run([sys.executable, __file__, es, os.path.join(tmp, "falta.json"),
                            "--hoja", hoja, "--celda", "8x8", "--mapa-archivo", mapa,
                            "--caja", "100"], capture_output=True, text=True)
        caso("una clave que falta en un idioma es un problema",
             r.returncode == 1 and "falta en" in r.stdout, r.stdout[-200:])

        with open(os.path.join(tmp, "no.json"), "w", encoding="utf-8") as f:
            f.write("{esto no")
        r = subprocess.run([sys.executable, __file__, os.path.join(tmp, "no.json"),
                            "--hoja", hoja, "--celda", "8x8", "--mapa-archivo", mapa,
                            "--caja", "100"], capture_output=True, text=True)
        caso("un JSON ilegible sale con 2, no con 1", r.returncode == 2, str(r.returncode))

        r = subprocess.run([sys.executable, __file__, es, "--hoja", hoja,
                            "--celda", "ocho", "--mapa-archivo", mapa, "--caja", "100"],
                           capture_output=True, text=True)
        caso("una celda mal escrita sale con 2", r.returncode == 2, str(r.returncode))

        # Los DOS idiomas, o `k2` se queda huérfana en «en» y el 1 que sale es por eso.
        for archivo in (es, en):
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump({"k1": "a a a a a a"}, f)
        # 6 «a» (2 px) + 5 espacios. Sin celda de espacio valen 5 px cada uno → 37 px;
        # con --espacio 1 → 17 px. La caja de 30 es lo único que separa los dos casos.
        ancho = correr("--caja", "30")
        estrecho = correr("--caja", "30", "--espacio", "1")
        caso("--espacio cambia el resultado: sin él desborda, con él cabe",
             ancho.returncode == 1 and estrecho.returncode == 0,
             f"{ancho.returncode}/{estrecho.returncode}")
        caso("y dice claramente que la anchura está forzada",
             "se ha FORZADO" in estrecho.stdout, estrecho.stdout[:200])

        r = correr("--caja", "30", "--espacio", "tres")
        caso("un --espacio que no es un número sale con 2", r.returncode == 2)

        # El aviso del espacio: el caso que hunde toda la aritmética en silencio.
        with open(es, "w", encoding="utf-8") as f:
            json.dump({"k1": "a a"}, f)
        r = subprocess.run([sys.executable, __file__, es, "--hoja", hoja, "--celda", "8x8",
                            "--mapa-archivo", mapa, "--caja", "100"],
                           capture_output=True, text=True)
        caso("avisa de que el mapa no trae el espacio",
             "NO trae el espacio" in r.stdout, r.stdout[:300])
        caso("y dice qué anchura va a usar GameMaker en su lugar",
             "carácter más ancho" in r.stdout, r.stdout[:300])

    print()
    if fallos:
        print(f"✗ Fallan {len(fallos)}: " + ", ".join(fallos))
        return 1
    print("✓ Todas las comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
