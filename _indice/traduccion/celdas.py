#!/usr/bin/env python3
"""Traduce, solo dentro del espejo español del manual, las celdas de las tablas de
argumentos que YoYo Games dejó en inglés.

No toca la prosa: la traducción oficial se respeta tal cual. Sustituye únicamente la
última columna de las filas de tabla cuyo texto siga en inglés, usando la memoria
`celdas_es.json` (inglés → español). Una celda sin traducción en la memoria se deja
intacta, así que nunca queda una tabla a medias por culpa de esta herramienta.

    python3 celdas.py estado     · cuántas celdas quedan y cuáles
    python3 celdas.py extraer    · vuelca a celdas_faltan.json las que no están en memoria
    python3 celdas.py aplicar    · reescribe las páginas con las celdas ya traducidas
"""
import os, re, json, sys, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
ES = os.path.join(RAIZ, "09 - Manual oficial", "manual-lts-2026-es")
MEM = os.path.join(AQUI, "celdas_es.json")
FALTAN = os.path.join(AQUI, "celdas_faltan.json")

EN_W = re.compile(r"\b(The|This|Whether|Sets|Returns|A |An |If |to be|of the|for the|"
                  r"that|which|will|should|used|value|number)\b")
ES_W = re.compile(r"\b(El|La|Los|Las|Un|Una|Si|que|de la|del|para|valor|número|se|"
                  r"Devuelve|Indica)\b")
FILA = re.compile(r"^(\|(?:[^|\n]*\|){2,}\s*)([^|\n]{12,}?)(\s*\|)\s*$", re.M)


def en_ingles(celda: str) -> bool:
    limpio = re.sub(r"\[[^\]]*\]\([^)]*\)|`[^`]*`", "", celda)
    if len(limpio.strip()) < 8:
        return False
    return len(EN_W.findall(limpio)) > len(ES_W.findall(limpio))


def paginas():
    for root, _, files in os.walk(ES):
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            p = os.path.join(root, f)
            txt = open(p, encoding="utf-8").read()
            if "traducido-por-la-biblioteca" in txt:
                continue          # esas ya están traducidas enteras
            yield p, txt


def memoria():
    return json.load(open(MEM, encoding="utf-8")) if os.path.exists(MEM) else {}


def recuento():
    cont = collections.Counter()
    for _, txt in paginas():
        for _, celda, _ in FILA.findall(txt):
            celda = celda.strip()
            if en_ingles(celda):
                cont[celda] += 1
    return cont


def cmd_estado():
    memo, cont = memoria(), recuento()
    faltan = {c: n for c, n in cont.items() if c not in memo}
    print(f"memoria: {len(memo)} celdas")
    print(f"celdas distintas en inglés: {len(cont)} · apariciones: {sum(cont.values())}")
    print(f"por traducir: {len(faltan)} · apariciones: {sum(faltan.values())}")


def cmd_extraer():
    memo, cont = memoria(), recuento()
    faltan = sorted(((n, c) for c, n in cont.items() if c not in memo), reverse=True)
    json.dump([c for _, c in faltan], open(FALTAN, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"{len(faltan)} celdas escritas en {os.path.basename(FALTAN)}")


def cmd_aplicar():
    memo = memoria()
    tocadas = celdas = 0
    for p, txt in paginas():
        def sub(m):
            nonlocal celdas
            pre, celda, post = m.group(1), m.group(2).strip(), m.group(3)
            if celda in memo and en_ingles(celda):
                celdas += 1
                return pre + memo[celda] + post
            return m.group(0)
        nuevo = FILA.sub(sub, txt)
        if nuevo != txt:
            open(p, "w", encoding="utf-8").write(nuevo)
            tocadas += 1
    print(f"{celdas} celdas traducidas en {tocadas} páginas")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "estado"
    {"estado": cmd_estado, "extraer": cmd_extraer, "aplicar": cmd_aplicar}[cmd]()
