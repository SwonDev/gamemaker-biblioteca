#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validar-enlaces-externos.py — comprueba que los enlaces externos siguen vivos.

`verificar-enlaces.py` valida las rutas INTERNAS. Este valida las EXTERNAS: cada
repo de GitHub, cada página de itch.io o del foro que la biblioteca cita y que
puede haberse archivado, movido o borrado. Un enlace muerto es un hueco.

    python3 _indice/validar-enlaces-externos.py [--dominio itch.io] [--muestra N] [--todos]

Por defecto valida los dominios frágiles (itch.io, foro, marketplace, gms…) enteros
y una muestra de GitHub. Escribe el informe en _indice/enlaces-externos-muertos.txt.
"""
import os, re, sys, subprocess, concurrent.futures, random, collections

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IND = os.path.join(RAIZ, "_indice")

URL = re.compile(r"https?://[A-Za-z0-9._~:/?#@!$&'()*+,;=%-]+")
# dominios que NO se validan: el manual está espejado en disco; badges/imágenes no son recursos
IGNORA = ("manual-lts-2026", "img.shields.io", "user-images.githubusercontent",
          "camo.githubusercontent", "badge")
# URLs que son EJEMPLOS o PLACEHOLDERS, no enlaces reales que validar:
PLACEHOLDER = re.compile(
    r"example\.com|localhost|127\.0\.0\.1|YOUR_|url-to-picture|miservidor|"
    r"\*\*|firebaseapp|tu-servidor|tu-backend|servidor\.com|midominio|"
    r"https?://https?://|<[^>]+>|\{[^}]+\}|angusgames\.com|macsweeneygames\.com")
# quitar bloques de código ``` ``` y `inline`: una URL de ejemplo dentro de código
# no es un enlace de navegación (el manual usa http_get("http://ejemplo…") así)
COD = re.compile(r"```.*?```|`[^`\n]*`", re.S)
FRAGILES = ("itch.io", "forum.gamemaker.io", "marketplace.yoyogames.com",
            "marketplace.gamemaker.io", "gms.yoyogames.com", "releases.gamemaker.io",
            "gm48.net", "glebtsereteli.github.io", "help.yoyogames.com")


def recolectar():
    urls = collections.Counter()
    for raiz, dirs, files in os.walk(RAIZ):
        # Por defecto solo se valida el contenido PROPIO. Los enlaces en los
        # READMEs de repos de terceros no son nuestros para arreglar (editarlos
        # los desincronizaría de su upstream). --con-terceros los incluye.
        excl = {".git", "09 - Manual oficial"}
        if "--con-terceros" not in sys.argv:
            excl.add("11 - Código descargado")
        dirs[:] = [d for d in dirs if d not in excl and not d.startswith(".")]
        for f in files:
            if not f.endswith(".md"):
                continue
            try:
                txt = open(os.path.join(raiz, f), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            txt = COD.sub(" ", txt)          # fuera las URLs de ejemplo en código
            for m in URL.finditer(txt):
                u = m.group(0).rstrip(".,);]'\"")
                if any(x in u for x in IGNORA) or PLACEHOLDER.search(u):
                    continue
                urls[u] += 1
    return urls


def comprobar(u):
    """HEAD (y GET de respaldo). Devuelve (url, estado)."""
    for metodo in ("-I", "-r0-0"):
        try:
            r = subprocess.run(
                ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
                 "-L", "--max-time", "15", "-A",
                 "Mozilla/5.0 (validador-biblioteca-gamemaker)", metodo, u],
                capture_output=True, text=True, timeout=20)
            code = r.stdout.strip()[-3:]
            if code and code[0] in "23":
                return u, code
            if code == "429":         # rate limit: no es un enlace muerto
                return u, "429"
        except (subprocess.TimeoutExpired, OSError):
            continue
    return u, code if 'code' in dir() and code else "ERR"


def main():
    args = sys.argv[1:]
    dom = None
    muestra_gh = 60
    todos = "--todos" in args
    if "--dominio" in args:
        dom = args[args.index("--dominio") + 1]
    if "--muestra" in args:
        muestra_gh = int(args[args.index("--muestra") + 1])

    urls = recolectar()
    print(f"{len(urls)} URLs externas únicas en la biblioteca")

    if dom:
        objetivo = [u for u in urls if dom in u]
    else:
        fragiles = [u for u in urls if any(d in u for d in FRAGILES)]
        github = [u for u in urls if "github.com" in u or "githubusercontent" in u]
        otros = [u for u in urls if u not in fragiles and u not in github]
        random.seed(42)
        gh_m = github if todos else random.sample(github, min(muestra_gh, len(github)))
        objetivo = sorted(set(fragiles + otros + gh_m))
        print(f"  validando: {len(fragiles)} frágiles + {len(otros)} otros + "
              f"{len(gh_m)} de {len(github)} de GitHub")

    print(f"comprobando {len(objetivo)} enlaces…\n")
    muertos = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        for i, (u, code) in enumerate(ex.map(comprobar, objetivo), 1):
            if code[0] not in "234":           # 2xx ok, 3xx redirige, 429 rate-limit
                muertos.append((code, u, urls[u]))
            if i % 50 == 0:
                print(f"  … {i}/{len(objetivo)}")

    # 999 = anti-bot (LinkedIn, etc.), no es un enlace muerto
    muertos = [(c, u, n) for c, u, n in muertos if c != "999"]
    muertos.sort()
    rep = os.path.join(IND, "enlaces-externos-muertos.txt")
    with open(rep, "w", encoding="utf-8") as f:
        for code, u, n in muertos:
            f.write(f"{code}  {u}  (citado {n}×)\n")

    print(f"\n{len(muertos)} enlaces muertos de {len(objetivo)} comprobados")
    for code, u, n in muertos[:40]:
        print(f"  {code}  {u}")
    if muertos:
        print(f"\ninforme completo: _indice/enlaces-externos-muertos.txt")
    return 1 if muertos else 0


if __name__ == "__main__":
    sys.exit(main())
