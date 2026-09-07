#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validar-enlaces-externos.py — comprueba que los enlaces externos siguen vivos.

`verificar-enlaces.py` valida las rutas INTERNAS. Este valida las EXTERNAS: cada
repo de GitHub, cada página de itch.io o del foro que la biblioteca cita y que
puede haberse archivado, movido o borrado. Un enlace muerto es un hueco.

    python3 _indice/validar-enlaces-externos.py [--dominio itch.io] [--muestra N]
                                                  [--todos] [--con-terceros]
                                                  [--hilos N] [--reintentos N]

Por defecto valida los dominios frágiles (itch.io, foro, marketplace, gms…)
enteros y una muestra de GitHub. Escribe el informe en
`_indice/enlaces-externos-muertos.txt`.

## Por qué el script tiene esta forma (auditoría r4-frescura, 07-09-2026)

Una ejecución anterior de este script, dentro de un entorno en sandbox sin red
funcional, marcó el 100 % de ~2 782 URLs como "muertas" (código "000" — ni
siquiera se pudo conectar). Nadie se dio cuenta porque el script no
distinguía "no hay red" de "el enlace está muerto", y el informe se quedó
escrito en `enlaces-externos-muertos.txt` como si fuera un hallazgo real.
Comprobado a mano: 3 de esas URLs elegidas al azar, las 3 vivas (200). Ver
`_indice/auditorias/r4-frescura.md` para el detalle completo de la
investigación que destapó esto.

Una segunda ejecución en vivo (esta vez con red de verdad) todavía daba 589
"000" de 5 055 URLs comprobadas — muchas de ellas en dominios evidentemente
vivos como youtube.com, w3schools.com o fmod.com. Un reintento con más margen
dejó 391 aún en "000". Y al comprobar una MUESTRA de 20 de esas 391 una a
una, SIN concurrencia, con 20 s de margen: **19 de 20 resolvieron con 200**
(los otros dos: bloqueo anti-bot esperado, no un enlace muerto). La causa no
era el contenido de la biblioteca, era la propia herramienta:
`ThreadPoolExecutor(max_workers=12)` saturaba la resolución DNS y las
conexiones salientes de este entorno. A más hilos concurrentes, más falsos
"muerto"; con 3 hilos el falso positivo bajaba mucho; con 1 (comprobación
manual) prácticamente desaparecía.

De ahí las reglas que sigue este script y que **nadie debería relajar sin
releer `_indice/auditorias/r4-frescura.md` primero**:

1. **Comprobar la red ANTES que nada** (`hay_red()`). Si no responde ninguno
   de los tres dominios ancla (google.com, cloudflare.com, github.com), el
   script ABORTA con `sys.exit(2)` y un mensaje explícito, en vez de
   comprobar miles de URLs sin red y escribir un informe envenenado. Este es
   el fallo que originó toda esta reescritura — el más grave y el más fácil
   de evitar con una sola comprobación previa.
2. **Concurrencia baja por defecto (3 hilos, `--hilos N` para cambiarla).**
   12 saturaba DNS en este entorno; no subas el valor por defecto sin
   evidencia de que tu entorno lo aguanta — y si lo subes, vuelve a pasar la
   prueba de la muestra manual (comprobar 20 "muertos" uno a uno, sin
   concurrencia) antes de confiar en el resultado.
3. **Reintentos con espera creciente SOLO para lo que puede ser transitorio**
   (código vacío "000", timeout, fallo de DNS/conexión, error 5xx del
   servidor). Un 404/410 es una respuesta HTTP determinista: no hace falta
   reintentarlo para creerlo, pero aun así se confirma una segunda vez con
   GET (tras una pausa corta) antes de declararlo "muerto de verdad", por si
   el primer HEAD dio un falso negativo.
4. **Cuatro categorías que NUNCA se mezclan en el informe ni en el resumen:**
   - `vivo`          — 2xx/3xx (con `-L`, ya siguiendo redirecciones).
   - `muerto`        — 404/410, confirmado dos veces. Es el ÚNICO grupo que
                        cuenta como "enlace muerto de verdad".
   - `bloqueado`     — 401/403/429/999: el recurso probablemente existe, pero
                        el sitio rechaza al robot (ya documentado:
                        `gamemaker.io` lo hace con varias rutas). NO es un
                        enlace muerto.
   - `no_comprobado` — la red falló (DNS, timeout, "000") incluso tras los
                        reintentos, o el servidor devolvió un 5xx
                        persistente. **Esto NO es "muerto"**: solo significa
                        que no se pudo concluir nada esta vez. Se reporta
                        aparte y nunca debe usarse como base para borrar un
                        enlace del contenido.
   - (`otro` — cajón de códigos HTTP inusuales, 400/405/451/etc., que no
     encajan en ninguna de las cuatro anteriores. Se reporta aparte, a mano,
     nunca como "muerto".)

Solo `muerto` debe interpretarse como "hay que arreglar este enlace".
`no_comprobado` es una lista de "vuelve a intentarlo", no de sospechosos.
"""
import argparse
import collections
import concurrent.futures
import os
import random
import re
import subprocess
import sys
import time

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

# Dominios ancla para la comprobación de red previa: estables, con TLS y sin
# bloqueo agresivo de robots. Basta con que UNO responda 2xx/3xx para dar la
# red por buena — no hace falta que los tres respondan.
ANCLAS_RED = ("https://www.google.com", "https://www.cloudflare.com", "https://github.com")

# UA de navegador real: varios dominios (gamemaker.io entre ellos, ya
# documentado) devuelven 403 a UAs que no parecen un navegador.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

CODIGOS_MUERTO = {"404", "410"}
CODIGOS_BLOQUEADO = {"401", "403", "429", "999"}
# "000" = curl no llegó a conectar (DNS/timeout/reset); ERR/TIMEOUT son los
# marcadores internos de este script para lo mismo cuando ni siquiera hay
# código HTTP que leer.
CODIGOS_SIN_RED = {"000", "ERR", "TIMEOUT"}


def recolectar(con_terceros):
    urls = collections.Counter()
    for raiz, dirs, files in os.walk(RAIZ):
        # Por defecto solo se valida el contenido PROPIO. Los enlaces en los
        # READMEs de repos de terceros no son nuestros para arreglar (editarlos
        # los desincronizaría de su upstream). --con-terceros los incluye.
        excl = {".git", "09 - Manual oficial"}
        if not con_terceros:
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


def hay_red(silencioso=False):
    """Comprueba conectividad real contra dominios muy estables ANTES de
    lanzar el barrido completo. Sin concurrencia, sin reintentos: si esto
    falla, el problema es la red del entorno, no los enlaces de la
    biblioteca. Basta con que UNO de los ANCLAS_RED responda 2xx/3xx."""
    for url in ANCLAS_RED:
        try:
            r = subprocess.run(
                ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
                 "-L", "--max-time", "10", "-A", USER_AGENT, "-I", url],
                capture_output=True, text=True, timeout=15)
            code = r.stdout.strip()[-3:]
            if code and code[0] in "23":
                if not silencioso:
                    print(f"  red OK ({url} → {code})")
                return True
        except (subprocess.TimeoutExpired, OSError):
            continue
    return False


def _curl(u, metodo, timeout):
    """Una sola petición curl. Devuelve el código HTTP como texto, o
    "TIMEOUT"/"ERR"/"000" si no hubo transacción HTTP completa."""
    try:
        r = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
             "-L", "--max-time", str(timeout), "-A", USER_AGENT, metodo, u],
            capture_output=True, text=True, timeout=timeout + 5)
        code = r.stdout.strip()[-3:]
        return code if code and code.isdigit() else "000"
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except OSError:
        return "ERR"


def _clasificar(code):
    if code and code[0] in "23":
        return "vivo"
    if code in CODIGOS_MUERTO:
        return "muerto"
    if code in CODIGOS_BLOQUEADO:
        return "bloqueado"
    if code in CODIGOS_SIN_RED or (code and len(code) == 3 and code[0] == "5"):
        return "no_comprobado"
    return "otro"


def comprobar(u, reintentos=3, espera_base=2.0, timeout=20):
    """Comprueba una URL con reintentos de espera creciente para lo que
    puede ser transitorio (red, timeout, 5xx). Un 404/410 se confirma una
    segunda vez con GET (tras una pausa corta) antes de declararse muerto de
    verdad, por si el HEAD inicial dio un falso negativo."""
    intento = 0
    ultimo_code = "000"
    while intento <= reintentos:
        if intento > 0:
            time.sleep(espera_base * (2 ** (intento - 1)))  # 2s, 4s, 8s…
        # jitter pequeño para no sincronizar todos los hilos en la misma
        # ventana de resolución DNS (parte del diagnóstico de saturación)
        time.sleep(random.uniform(0, 0.3))

        code = _curl(u, "-I", timeout)
        if code == "000":
            code = _curl(u, "-r0-0", timeout)  # algunos servidores no soportan HEAD

        clase = _clasificar(code)
        ultimo_code = code

        if clase in ("vivo", "bloqueado", "otro"):
            return u, code, clase

        if clase == "muerto":
            time.sleep(1.5)
            code2 = _curl(u, "-r0-0", timeout)  # confirmación con GET, no HEAD
            clase2 = _clasificar(code2)
            return u, code2, clase2 if clase2 != "muerto" else "muerto"

        # clase == "no_comprobado": puede ser transitorio, reintenta
        intento += 1

    return u, ultimo_code, "no_comprobado"


def main():
    ap = argparse.ArgumentParser(
        description="Comprueba que los enlaces externos de la biblioteca siguen vivos.")
    ap.add_argument("--dominio", help="valida solo URLs que contengan este texto")
    ap.add_argument("--muestra", type=int, default=60,
                     help="cuántas URLs de GitHub muestrear (por defecto 60)")
    ap.add_argument("--todos", action="store_true", help="valida TODAS las URLs de GitHub")
    ap.add_argument("--con-terceros", action="store_true",
                     help="incluye los READMEs de '11 - Código descargado'")
    ap.add_argument("--hilos", type=int, default=3,
                     help="concurrencia del comprobador (defecto 3 — ver cabecera del "
                          "script: 12 saturaba DNS en el entorno que motivó esta reescritura)")
    ap.add_argument("--reintentos", type=int, default=3,
                     help="reintentos con espera creciente ante fallo de red/5xx (defecto 3)")
    ap.add_argument("--timeout", type=int, default=20,
                     help="segundos de margen por intento de curl (defecto 20)")
    ap.add_argument("--sin-red-check", action="store_true",
                     help="salta la comprobación de red inicial (solo para depurar hay_red())")
    args = ap.parse_args()

    print("comprobando conectividad de red…")
    if not args.sin_red_check and not hay_red():
        print("\n✖ SIN RED: no se pudo conectar con ninguno de los dominios ancla "
              f"({', '.join(ANCLAS_RED)}).")
        print("  Esto NO significa que los enlaces de la biblioteca estén muertos: significa")
        print("  que este entorno no tiene red utilizable ahora mismo (ver la cabecera del")
        print("  script — así se generó el informe envenenado que motivó esta reescritura).")
        print("  Abortando SIN escribir ningún informe. Reinténtalo con red disponible.")
        return 2

    urls = recolectar(args.con_terceros)
    print(f"{len(urls)} URLs externas únicas en la biblioteca")

    if args.dominio:
        objetivo = [u for u in urls if args.dominio in u]
    else:
        fragiles = [u for u in urls if any(d in u for d in FRAGILES)]
        github = [u for u in urls if "github.com" in u or "githubusercontent" in u]
        otros = [u for u in urls if u not in fragiles and u not in github]
        random.seed(42)
        gh_m = github if args.todos else random.sample(github, min(args.muestra, len(github)))
        objetivo = sorted(set(fragiles + otros + gh_m))
        print(f"  validando: {len(fragiles)} frágiles + {len(otros)} otros + "
              f"{len(gh_m)} de {len(github)} de GitHub")

    print(f"comprobando {len(objetivo)} enlaces con {args.hilos} hilos "
          f"(hasta {args.reintentos} reintentos por fallo transitorio)…\n")

    resultados = {"vivo": [], "muerto": [], "bloqueado": [], "no_comprobado": [], "otro": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.hilos) as ex:
        futuros = [ex.submit(comprobar, u, args.reintentos, 2.0, args.timeout) for u in objetivo]
        for i, fut in enumerate(concurrent.futures.as_completed(futuros), 1):
            u, code, clase = fut.result()
            resultados[clase].append((code, u, urls[u]))
            if i % 100 == 0 or i == len(objetivo):
                print(f"  … {i}/{len(objetivo)}")

    for clave in resultados:
        resultados[clave].sort()

    # informe: SOLO 'muerto' se escribe como "enlaces muertos de verdad". El
    # resto se reporta en secciones aparte para que nadie los confunda ni los
    # use como base para borrar un enlace que en realidad está vivo o solo
    # bloqueado para robots.
    rep = os.path.join(IND, "enlaces-externos-muertos.txt")
    with open(rep, "w", encoding="utf-8") as f:
        f.write(f"# Generado {time.strftime('%Y-%m-%d %H:%M')} · {len(objetivo)} URLs "
                f"comprobadas · {args.hilos} hilos · {args.reintentos} reintentos\n")
        f.write("# Metodología completa: cabecera de _indice/validar-enlaces-externos.py\n")
        f.write("# y _indice/auditorias/r4-frescura.md.\n\n")

        f.write(f"## MUERTOS DE VERDAD ({len(resultados['muerto'])}) — "
                f"404/410 confirmados dos veces. Los únicos que hay que arreglar.\n")
        for code, u, n in resultados["muerto"]:
            f.write(f"{code}  {u}  (citado {n}×)\n")

        f.write(f"\n## BLOQUEADOS PERO EXISTENTES ({len(resultados['bloqueado'])}) — "
                f"401/403/429/999: el sitio rechaza al robot, el recurso probablemente\n"
                f"## sigue ahí. NO son enlaces muertos.\n")
        for code, u, n in resultados["bloqueado"]:
            f.write(f"{code}  {u}  (citado {n}×)\n")

        f.write(f"\n## NO SE PUDO COMPROBAR ({len(resultados['no_comprobado'])}) — "
                f"fallo de red/timeout/5xx persistente incluso tras reintentos.\n"
                f"## Esto NO es \"muerto\": solo significa que no se concluyó nada esta vez.\n")
        for code, u, n in resultados["no_comprobado"]:
            f.write(f"{code}  {u}  (citado {n}×)\n")

        if resultados["otro"]:
            f.write(f"\n## OTROS CÓDIGOS ({len(resultados['otro'])}) — "
                    f"no encajan en ninguna categoría anterior, revisar a mano.\n")
            for code, u, n in resultados["otro"]:
                f.write(f"{code}  {u}  (citado {n}×)\n")

    print(f"\n— vivo: {len(resultados['vivo'])}")
    print(f"— muerto de verdad: {len(resultados['muerto'])}")
    print(f"— bloqueado (existe, rechaza al robot): {len(resultados['bloqueado'])}")
    print(f"— no se pudo comprobar (red/timeout/5xx): {len(resultados['no_comprobado'])}")
    if resultados["otro"]:
        print(f"— otros códigos: {len(resultados['otro'])}")

    if resultados["muerto"]:
        print("\nmuertos de verdad:")
        for code, u, n in resultados["muerto"][:40]:
            print(f"  {code}  {u}")

    print(f"\ninforme completo: _indice/enlaces-externos-muertos.txt")
    return 1 if resultados["muerto"] else 0


if __name__ == "__main__":
    sys.exit(main())
