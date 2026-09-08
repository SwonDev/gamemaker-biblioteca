#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Memoria de traducción para el manual de GameMaker.

Segmenta cada página en unidades traducibles (párrafos, celdas de tabla, listas,
encabezados), busca cada unidad en la memoria (`tm_es.json`) y reconstruye la página
en español. El código, los enlaces y los nombres de función se conservan intactos.

  tm.py faltan <filtro> [n]   -> unidades sin traducir, por frecuencia
  tm.py aplicar <filtro>      -> traduce todas las páginas cuyas unidades estén completas
  tm.py estado                -> resumen
"""
import os, re, sys, json, collections

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


SC = os.path.dirname(os.path.abspath(__file__))
# La raíz se deriva de la ubicación de este archivo, no se escribe a fuego: el script
# viaja en el repositorio y una ruta absoluta solo vale en la máquina del autor.
import os as _os
_RAIZ = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
P = _os.path.join(_RAIZ, "09 - Manual oficial")
EN = os.path.join(P, "manual-lts-2026-en")
ES = os.path.join(P, "manual-lts-2026-es")
TM_FILE = os.path.join(SC, "tm_es.json")
COLA = os.path.join(SC, "cola_traduccion.json")

# --- unidades que NO se traducen nunca ---
NO_TRADUCIR = re.compile(
    r"^(N/A|Real|String|Boolean|Array|Struct|Undefined|Any|Pointer|Method|Function|Int32|Int64|"
    r"true|false|undefined|-?\d[\d.,]*|`[^`]+`|\[[^\]]+\]\([^)]+\)|[\w.]+\(\)|"
    # identificadores de GML: nombres de función, argumentos, constantes
    r"[a-z][a-z0-9_]*|[A-Z][A-Za-z0-9]*\.[A-Za-z0-9_]+|"
    # tipos entre corchetes con enlace, opcionalmente con sufijo
    r"\[[^\]]+\]\([^)]+\)( or \[[^\]]+\]\([^)]+\))*|"
    r"\[?[a-z_]+\]?|"
    r"Fuente oficial: <.*>|"
    r"\*\*Palabras clave:\*\*.*|\*\*Etiquetas:\*\*.*)$"
)
CODIGO = re.compile(r"^```")


def cargar_tm():
    if os.path.exists(TM_FILE):
        return json.load(open(TM_FILE, encoding="utf-8"))
    return {}


def guardar_tm(tm):
    json.dump(tm, open(TM_FILE, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1, sort_keys=True)


def segmentar(texto):
    """Devuelve [(tipo, contenido)] donde tipo es 'trad' (traducible) o 'fijo'."""
    salida = []
    lineas = texto.split("\n")
    i = 0
    en_codigo = False
    buf = []

    def volcar():
        nonlocal buf
        if buf:
            p = "\n".join(buf).strip()
            if p:
                salida.append(("trad", p) if not NO_TRADUCIR.match(p) else ("fijo", p))
            buf = []

    while i < len(lineas):
        l = lineas[i]
        if CODIGO.match(l.strip()):
            volcar()
            bloque = [l]
            i += 1
            while i < len(lineas):
                bloque.append(lineas[i])
                if CODIGO.match(lineas[i].strip()):
                    i += 1
                    break
                i += 1
            salida.append(("fijo", "\n".join(bloque)))
            continue
        s = l.strip()
        if not s:
            volcar()
            salida.append(("fijo", ""))
            i += 1
            continue
        if s.startswith("|"):
            volcar()
            if re.match(r"^\|[\s:|-]+\|$", s):
                salida.append(("fijo", l))
            else:
                celdas = s.strip("|").split("|")
                salida.append(("fila", [c.strip() for c in celdas]))
            i += 1
            continue
        if s.startswith("#"):
            volcar()
            m = re.match(r"^(#+)\s*(.*)$", s)
            salida.append(("enc", (m.group(1), m.group(2))))
            i += 1
            continue
        if re.match(r"^([-*]|\d+\.)\s", s):
            volcar()
            m = re.match(r"^(\s*(?:[-*]|\d+\.)\s+)(.*)$", l)
            salida.append(("lista", (m.group(1), m.group(2))))
            i += 1
            continue
        if s == "---":
            volcar()
            salida.append(("fijo", "---"))
            i += 1
            continue
        buf.append(l)
        i += 1
    volcar()
    return salida


def unidades(seg):
    """Todas las cadenas traducibles de un segmentado."""
    u = []
    for tipo, cont in seg:
        if tipo == "trad":
            u.append(cont)
        elif tipo == "fila":
            for c in cont:
                if c and not NO_TRADUCIR.match(c):
                    u.append(c)
        elif tipo == "enc":
            if cont[1] and not NO_TRADUCIR.match(cont[1]):
                u.append(cont[1])
        elif tipo == "lista":
            if cont[1] and not NO_TRADUCIR.match(cont[1]):
                u.append(cont[1])
    return u


def reconstruir(seg, tm):
    out = []
    for tipo, cont in seg:
        if tipo == "fijo":
            out.append(cont)
        elif tipo == "trad":
            out.append(tm.get(cont, cont))
        elif tipo == "fila":
            out.append("| " + " | ".join(tm.get(c, c) if c and not NO_TRADUCIR.match(c) else c
                                         for c in cont) + " |")
        elif tipo == "enc":
            h, t = cont
            out.append(f"{h} {tm.get(t, t) if t and not NO_TRADUCIR.match(t) else t}")
        elif tipo == "lista":
            pre, t = cont
            out.append(pre + (tm.get(t, t) if t and not NO_TRADUCIR.match(t) else t))
    return "\n".join(out)


# Etiquetas de enlace de tipo que sí se traducen (el destino no se toca)
ETIQUETAS = {
    "Text Element ID": "ID de elemento de texto",
    "Text Horizontal Alignment Constant": "Constante de alineación horizontal de texto",
    "Text Vertical Alignment Constant": "Constante de alineación vertical de texto",
    "Text Frame Origin Constant": "Constante de origen de marco de texto",
    "Text Wrap Mode Constant": "Constante de modo de ajuste de línea",
    "Font Asset": "Asset de fuente",
    "Object Asset": "Asset de objeto",
    "Sprite Asset": "Asset de sprite",
    "Sound Asset": "Asset de sonido",
    "Room Asset": "Asset de room",
    "Path Asset": "Asset de path",
    "Tile Set Asset": "Asset de tile set",
    "Shader Asset": "Asset de shader",
    "Sequence Asset": "Asset de secuencia",
    "Particle System Asset": "Asset de sistema de partículas",
    "Animation Curve Asset": "Asset de curva de animación",
    "Object Instance": "Instancia de objeto",
    "Colour": "Color",
    "Layer": "Capa",
    "Layer ID": "ID de capa",
    "Particle System Element ID": "ID de elemento de sistema de partículas",
    "Particle System Instance": "Instancia de sistema de partículas",
    "Sprite Element ID": "ID de elemento de sprite",
    "Background Element ID": "ID de elemento de fondo",
    "Sequence Element ID": "ID de elemento de secuencia",
    "Tile Map Element ID": "ID de elemento de tile map",
    "Instance Element ID": "ID de elemento de instancia",
    "Flex Panel Node": "Nodo de Flex Panel",
    "Asset Type Constant": "Constante de tipo de asset",
    "Audio Emitter": "Emisor de audio",
    "Sound Instance": "Instancia de sonido",
    "Buffer": "Búfer",
    "Time Source": "Fuente de tiempo",
    "Camera ID": "ID de cámara",
    "Surface": "Superficie",
    "Texture Group": "Grupo de texturas",
    "Vertex Buffer": "Búfer de vértices",
    "Vertex Format": "Formato de vértices",
}


def traducir_etiquetas(md):
    def rep(m):
        et = m.group(1)
        return f"[{ETIQUETAS.get(et, et)}]({m.group(2)})"
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", rep, md)


def paginas(filtro):
    d = json.load(open(COLA, encoding="utf-8"))
    return [p for p in d["pendientes"] if filtro in p]


def leer(rel):
    f = os.path.join(EN, rel)
    if not os.path.exists(f):
        f = os.path.join(ES, rel)
    return open(f, encoding="utf-8").read()


if __name__ == "__main__":
    cmd = sys.argv[1]
    tm = cargar_tm()
    if cmd == "faltan":
        filtro = sys.argv[2] if len(sys.argv) > 2 else ""
        lim = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        c = collections.Counter()
        for rel in paginas(filtro):
            for u in unidades(segmentar(leer(rel))):
                if u not in tm:
                    c[u] += 1
        print(f"# {len(c)} unidades sin traducir en {len(paginas(filtro))} páginas")
        for u, n in c.most_common(lim):
            print(f"\n[{n}] {u}")
    elif cmd == "aplicar":
        filtro = sys.argv[2] if len(sys.argv) > 2 else ""
        listas, incompletas = [], []
        for rel in paginas(filtro):
            seg = segmentar(leer(rel))
            falt = [u for u in unidades(seg) if u not in tm]
            (incompletas if falt else listas).append((rel, seg, falt))
        print(f"completas: {len(listas)} · incompletas: {len(incompletas)}")
        import subprocess
        hechas = []
        for rel, seg, _ in listas:
            md = traducir_etiquetas(reconstruir(seg, tm))
            md = re.sub(r"\n---\n\nFuente oficial: <(.*?)>", "", md).strip()
            url = re.search(r"Fuente oficial: <(.*?)>", leer(rel))
            md = ("<!-- traducido-por-la-biblioteca -->\n" + md +
                  "\n\n---\n\n> 🌐 Traducción propia de esta biblioteca. "
                  "La traducción oficial al español no cubre esta página.\n\n"
                  f"Fuente oficial: <{url.group(1) if url else ''}>\n")
            dst = os.path.join(ES, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, "w", encoding="utf-8").write(md)
            hechas.append(rel)
        if hechas:
            subprocess.run([sys.executable, os.path.join(SC, "cola_traduccion.py"),
                            "hecho"] + hechas)
        for rel, _, falt in incompletas[:10]:
            print(f"  incompleta: {rel}  ({len(falt)} unidades)")
    elif cmd == "estado":
        d = json.load(open(COLA, encoding="utf-8"))
        print(f"memoria: {len(tm)} unidades · pendientes: {len(d['pendientes'])}")
