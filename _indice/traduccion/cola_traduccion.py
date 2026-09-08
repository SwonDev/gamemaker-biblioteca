#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gestiona la cola de páginas del manual que siguen en inglés.

  cola_traduccion.py estado          -> cuántas quedan
  cola_traduccion.py siguiente N     -> vuelca el contenido de las N siguientes
  cola_traduccion.py hecho <ruta>    -> marca una como traducida
"""
import os, re, sys, json

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


# La raíz se deriva de la ubicación de este archivo, no se escribe a fuego: el script
# viaja en el repositorio y una ruta absoluta solo vale en la máquina del autor.
import os as _os
_RAIZ = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
P = _os.path.join(_RAIZ, "09 - Manual oficial")
ES = os.path.join(P, "manual-lts-2026-es")
EN = os.path.join(P, "manual-lts-2026-en")
SC = os.path.dirname(os.path.abspath(__file__))
COLA = os.path.join(SC, "cola_traduccion.json")

ESW = set("que para con los las una del por como pero este esta cuando siguiente ejemplo "
          "funcion función puede debe también más así sobre desde hacer valor código "
          "argumento devuelve sintaxis nota siguiente atrás".split())
ENW = set("the and that with for this from will your they which have been when should "
          "used argument returns syntax note back next above below".split())


def es_ingles(texto):
    t = texto.lower()
    w = re.findall(r"[a-záéíóúñü]+", t)
    if len(w) < 40:
        return False
    a = sum(1 for x in w if x in ESW)
    b = sum(1 for x in w if x in ENW)
    return b >= a


def construir():
    pend = []
    for r, d, fs in os.walk(ES):
        for f in fs:
            if not f.endswith(".md"):
                continue
            fp = os.path.join(r, f)
            try:
                txt = open(fp, encoding="utf-8").read()
            except OSError:
                continue
            if "<!-- traducido-por-la-biblioteca -->" in txt:
                continue
            if es_ingles(txt):
                pend.append(os.path.relpath(fp, ES))
    pend.sort(key=lambda x: (0 if "GML_Reference" in x else 1, x))
    return pend


def cargar():
    if os.path.exists(COLA):
        return json.load(open(COLA, encoding="utf-8"))
    d = {"pendientes": construir(), "hechas": []}
    json.dump(d, open(COLA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return d


def guardar(d):
    json.dump(d, open(COLA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "estado"
    d = cargar()
    if cmd == "estado":
        print(f"pendientes: {len(d['pendientes'])} · traducidas: {len(d['hechas'])}")
        import collections
        c = collections.Counter("/".join(p.split(os.sep)[:5]) for p in d["pendientes"])
        for k, v in c.most_common(12):
            print(f"  {v:4}  {k}")
    elif cmd == "reconstruir":
        d = {"pendientes": construir(), "hechas": d.get("hechas", [])}
        guardar(d)
        print("pendientes:", len(d["pendientes"]))
    elif cmd == "siguiente":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        filtro = sys.argv[3] if len(sys.argv) > 3 else ""
        cand = [x for x in d["pendientes"] if filtro in x]
        for rel in cand[:n]:
            # se traduce a partir de la versión EN, que está más al día
            fuente = os.path.join(EN, rel)
            if not os.path.exists(fuente):
                fuente = os.path.join(ES, rel)
            txt = open(fuente, encoding="utf-8").read()
            if "--compacto" in sys.argv:
                # quita pie de fuente, separadores y el div sobrante
                txt = re.sub(r"\n---\n\nFuente oficial:.*$", "", txt, flags=re.S)
                txt = txt.replace('<div class="body-scroll" style="top: 150px;">', "")
                txt = re.sub(r"\n\s*</div>\s*KEYWORDS.*$", "", txt, flags=re.S)
                txt = re.sub(r"\n\*\*Palabras clave:\*\*.*$", "", txt, flags=re.S)
                txt = re.sub(r"\n{3,}", "\n\n", txt).strip()
            print(f"\n<<<<< {rel}")
            print(txt)
    elif cmd == "listar":
        filtro = sys.argv[2] if len(sys.argv) > 2 else ""
        for x in d["pendientes"]:
            if filtro in x:
                print(x)
    elif cmd == "hecho":
        for rel in sys.argv[2:]:
            if rel in d["pendientes"]:
                d["pendientes"].remove(rel)
            if rel not in d["hechas"]:
                d["hechas"].append(rel)
        guardar(d)
        print(f"pendientes: {len(d['pendientes'])}")
