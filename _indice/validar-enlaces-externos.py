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
import shutil
import subprocess
import sys
import time

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
IND = os.path.join(RAIZ, "_indice")

URL = re.compile(r"https?://[A-Za-z0-9._~:/?#@!$&'()*+,;=%-]+")
# dominios que NO se validan: el manual está espejado en disco; badges/imágenes no son recursos
IGNORA = ("manual-lts-2026", "img.shields.io", "user-images.githubusercontent",
          "camo.githubusercontent", "badge",
          # Servidores de sellado de tiempo para firmar binarios: NO son páginas
          # web. Responden 404 a un GET y funcionan perfectamente para lo suyo
          # (`signtool /tr`). Marcarlos como muertos es un falso positivo, y de
          # los caros: alguien podría "arreglar" una URL de firma que estaba bien.
          "timestamp.digicert.com", "timestamp.sectigo.com",
          "timestamp.comodoca.com", "timestamp.apple.com")
# URLs que son EJEMPLOS o PLACEHOLDERS, no enlaces reales que validar:
PLACEHOLDER = re.compile(
    r"example\.com|localhost|127\.0\.0\.1|YOUR_|url-to-picture|miservidor|"
    r"\*\*|firebaseapp|tu-servidor|tu-backend|servidor\.com|midominio|"
    r"https?://https?://|<[^>]+>|\{[^}]+\}|angusgames\.com|macsweeneygames\.com")
# quitar bloques de código ``` ``` y `inline`: una URL de ejemplo dentro de código
# no es un enlace de navegación (el manual usa http_get("http://ejemplo…") así)
COD = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def recortar_puntuacion(u):
    """Quita la puntuación que arrastra una URL al final de una frase.

    Ojo con el paréntesis, que es donde estaba el fallo: un `.rstrip(")")` a
    secas partía `…/wiki/Hades_(video_game)` en `…/wiki/Hades_(video_game`, y el
    informe daba por MUERTOS doce enlaces de Wikipedia que están perfectamente
    vivos. Doce falsos positivos de setenta hacen que nadie se crea la lista, que
    es peor que no tenerla.

    La regla correcta: un `)` final solo sobra si NO cierra un `(` abierto dentro
    de la propia URL.
    """
    # 1 · Cortar en el primer `)` que cierra un paréntesis que la URL no abrió.
    #     Es el de `[texto](https://tabelf.link/)'s ...` en Markdown: el regex se
    #     traga el cierre del enlace Y lo que venga detrás. Estrictamente al final
    #     no sirve, porque ahí la basura va DESPUÉS del paréntesis sobrante.
    abiertos = 0
    for i, ch in enumerate(u):
        if ch == "(":
            abiertos += 1
        elif ch == ")":
            if abiertos == 0:
                u = u[:i]
                break
            abiertos -= 1

    # 2 · Y quitar la puntuación que arrastra el final de una frase.
    u = u.rstrip(".,;:!]'\"")
    while u.endswith(")") and u.count(")") > u.count("("):
        u = u[:-1].rstrip(".,;:!]'\"")
    return u
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

# Repositorios CERRADOS, que no muertos. GitHub responde 404 a quien no está
# dentro de un repositorio privado — el mismo 404, byte por byte, que devuelve
# uno que jamás existió. Desde fuera no hay forma de distinguirlos, así que el
# comprobador solo puede hacer dos cosas: gritar cada semana por algo que nadie
# puede arreglar, o reclasificarlo. Gritar es peor: un aviso que salta cuando no
# toca se aprende a ignorar, y con él se ignoran los que sí importan.
#
# La excepción NO es un permiso permanente: se apoya en un CENTINELA, una URL
# pública que solo sigue viva mientras el motivo siga siendo cierto. Si la
# organización que aloja esos repositorios desaparece, el centinela cae y sus
# 404 vuelven a contar como muertos. Una excepción que no puede caducar es una
# mentira con fecha de entrega.
CERRADOS_ESPERADOS = (
    ("github.com/GameMakerEnterprise/",
     "https://github.com/GameMakerEnterprise",
     "repositorio privado de GameMaker Enterprise: la wiki del runner de consola "
     "solo se ve con la aprobación del fabricante (NDA)"),
)


def motivo_cerrado(u):
    """(centinela, motivo) si esta URL es un 404 esperado; None si no lo es."""
    for patron, centinela, motivo in CERRADOS_ESPERADOS:
        if patron in u:
            return centinela, motivo
    return None


def recolectar(con_terceros):
    urls = collections.Counter()
    for raiz, dirs, files in os.walk(RAIZ):
        # Por defecto solo se valida el contenido PROPIO. Los enlaces en los
        # READMEs de repos de terceros no son nuestros para arreglar (editarlos
        # los desincronizaría de su upstream). --con-terceros los incluye.
        # `GameMaker_Fuentes` (almacén crudo de clones ajenos, 14 GB) y `Lumbre`
        # (el juego personal del autor) NO se tocan, no se citan y no se publican
        # — lo dice el .gitignore y AGENTS.md. Faltaban aquí, y el informe venía
        # arrastrando enlaces muertos de documentación de terceros que además NO
        # es nuestra para arreglar: un `polyfill.io` de los docs de Pixel-Composer
        # aparecía como si fuera una cita de esta biblioteca.
        # `auditorias` queda fuera por el mismo motivo que en `verificar-enlaces.py`:
        # son informes con fecha, y un enlace que murió después es un hecho
        # histórico del informe, no algo que corregir.
        excl = {".git", "09 - Manual oficial", "GameMaker_Fuentes", "Lumbre", "auditorias"}
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
                # Un autolink `<https://…Inc.>` ya viene delimitado por el `>`:
                # ahí el punto final ES parte de la URL y recortarlo la rompe.
                # Pasaba con el caso Tetris (`…_v._Xio_Interactive,_Inc.`), que
                # salía como muerto siendo un enlace perfecto.
                delimitada = (m.end() < len(txt) and txt[m.end()] == ">"
                              and m.start() > 0 and txt[m.start() - 1] == "<")
                u = m.group(0) if delimitada else recortar_puntuacion(m.group(0))
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

    if not shutil.which("curl"):
        print("✗ No encuentro el comando «curl» en el PATH. Este validador lo necesita para")
        print("  comprobar enlaces externos (viene de serie en macOS, Linux y Windows 10")
        print("  1803+). Instálalo y vuelve a intentarlo. Esto NO es 'sin red': es la propia")
        print("  herramienta la que falta.")
        return 2

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

    resultados = {"vivo": [], "muerto": [], "bloqueado": [], "no_comprobado": [],
                  "otro": [], "cerrado": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.hilos) as ex:
        futuros = [ex.submit(comprobar, u, args.reintentos, 2.0, args.timeout) for u in objetivo]
        for i, fut in enumerate(concurrent.futures.as_completed(futuros), 1):
            u, code, clase = fut.result()
            resultados[clase].append((code, u, urls[u]))
            if i % 100 == 0 or i == len(objetivo):
                print(f"  … {i}/{len(objetivo)}")

    # Reclasificar los 404 esperados — pero solo si su centinela responde. El
    # centinela se comprueba AQUÍ y no antes para no gastar una petición cuando
    # ninguno de sus repositorios ha salido muerto.
    cerrados_motivo = {}
    if any(motivo_cerrado(u) for _c, u, _n in resultados["muerto"]):
        centinelas = {}
        for code, u, n in list(resultados["muerto"]):
            m = motivo_cerrado(u)
            if not m:
                continue
            centinela, motivo = m
            if centinela not in centinelas:
                print(f"  comprobando el centinela {centinela} …")
                centinelas[centinela] = comprobar(centinela, 1, 2.0, args.timeout)[2]
            if centinelas[centinela] == "vivo":
                resultados["muerto"].remove((code, u, n))
                resultados["cerrado"].append((code, u, n))
                cerrados_motivo[u] = motivo
            else:
                # El centinela no responde: no hay evidencia para la excepción,
                # así que el enlace se queda donde estaba. Callar sin pruebas
                # sería justo el fallo que esta tabla intenta evitar.
                print(f"  ⚠ el centinela {centinela} no está vivo "
                      f"({centinelas[centinela]}): {u} sigue contando como muerto")

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

        if resultados["cerrado"]:
            f.write(f"\n## CERRADOS, NO MUERTOS ({len(resultados['cerrado'])}) — "
                    f"404 esperado: el recurso existe pero es privado.\n"
                    f"## Su centinela público respondió 2xx en esta misma pasada, que es "
                    f"la única\n## prueba que se puede tener desde fuera. NO los borres.\n")
            for code, u, n in resultados["cerrado"]:
                f.write(f"{code}  {u}  (citado {n}×)\n")
                f.write(f"       └─ {cerrados_motivo.get(u, '')}\n")

        if resultados["otro"]:
            f.write(f"\n## OTROS CÓDIGOS ({len(resultados['otro'])}) — "
                    f"no encajan en ninguna categoría anterior, revisar a mano.\n")
            for code, u, n in resultados["otro"]:
                f.write(f"{code}  {u}  (citado {n}×)\n")

    print(f"\n— vivo: {len(resultados['vivo'])}")
    print(f"— muerto de verdad: {len(resultados['muerto'])}")
    print(f"— bloqueado (existe, rechaza al robot): {len(resultados['bloqueado'])}")
    if resultados["cerrado"]:
        print(f"— cerrado, no muerto (privado, centinela vivo): {len(resultados['cerrado'])}")
    print(f"— no se pudo comprobar (red/timeout/5xx): {len(resultados['no_comprobado'])}")
    if resultados["otro"]:
        print(f"— otros códigos: {len(resultados['otro'])}")

    if resultados["muerto"]:
        print("\nmuertos de verdad:")
        for code, u, n in resultados["muerto"][:40]:
            print(f"  {code}  {u}")

    print(f"\ninforme completo: _indice/enlaces-externos-muertos.txt")
    return 1 if resultados["muerto"] else 0


def autoprueba():
    """Los casos de recorte que ya han dado falsos positivos.

    Un informe de enlaces muertos con doce falsos positivos de setenta no se lee:
    se ignora entero. Por eso el recorte de puntuación tiene prueba propia.
    """
    casos = [
        ("https://en.wikipedia.org/wiki/Hades_(video_game)",
         "https://en.wikipedia.org/wiki/Hades_(video_game)",
         "un paréntesis que SÍ cierra uno abierto se conserva"),
        ("https://es.wikipedia.org/wiki/A_(letra)):",
         "https://es.wikipedia.org/wiki/A_(letra)",
         "y el de más, con dos puntos detrás, se quita"),
        ("https://ejemplo.com/pagina).", "https://ejemplo.com/pagina",
         "un paréntesis suelto de la frase se quita"),
        ("https://jqlang.github.io/jq/):", "https://jqlang.github.io/jq/",
         "«):» al final de una cita se quita"),
        ("https://ejemplo.com/x,", "https://ejemplo.com/x",
         "una coma final se quita"),
        ("https://ejemplo.com/normal", "https://ejemplo.com/normal",
         "una URL limpia no se toca"),
        ("https://tabelf.link/)'s", "https://tabelf.link/",
         "un `)` EN MEDIO corta ahí, no solo al final"),
        ("https://mashmerlow.github.io/)._", "https://mashmerlow.github.io/",
         "y lo que venga detrás se va con él"),
        ("https://bottosson.github.io/posts/oklab/)/", "https://bottosson.github.io/posts/oklab/",
         "aunque detrás siga habiendo barra"),
    ]

    fallos = 0
    for entrada, esperado, nombre in casos:
        obtenido = recortar_puntuacion(entrada)
        if obtenido == esperado:
            print("  \u2713 " + nombre)
        else:
            fallos += 1
            print("  \u2717 %s  ->  %s" % (nombre, obtenido))
    # El autolink va aparte: NO pasa por `recortar_puntuacion`, y ese es el punto.
    # Un `<https://…Inc.>` viene delimitado por el `>`, así que el punto final es
    # parte de la URL. Recortarlo daba por muerto el caso Tetris, que está vivo.
    def _extraer(texto):
        for _m in URL.finditer(texto):
            delimitada = (_m.end() < len(texto) and texto[_m.end()] == ">"
                          and _m.start() > 0 and texto[_m.start() - 1] == "<")
            return _m.group(0) if delimitada else recortar_puntuacion(_m.group(0))
        return None

    for texto, esperado, nombre in [
        ("ver <https://en.wikipedia.org/wiki/A,_Inc.> y punto",
         "https://en.wikipedia.org/wiki/A,_Inc.",
         "en un autolink <…> el punto final NO se recorta"),
        ("ver [x](https://ejemplo.com/y). Y sigue",
         "https://ejemplo.com/y",
         "y fuera de un autolink sí se recorta"),
    ]:
        obtenido = _extraer(texto)
        if obtenido == esperado:
            print("  \u2713 " + nombre)
        else:
            fallos += 1
            print("  \u2717 %s  ->  %s" % (nombre, obtenido))

    # La lista de 404 esperados es la que más fácil se le va a la mano a alguien:
    # un patrón demasiado ancho silencia repositorios que sí están rotos. Por eso
    # se prueba sobre todo lo que NO debe entrar.
    for url, debe_entrar, nombre in [
        ("https://github.com/GameMakerEnterprise/GMS2-Runner-PS4/wiki/", True,
         "la wiki privada del runner de PS4 entra en la excepción"),
        ("https://github.com/GameMakerEnterprise/GMS2-Runner-Switch2/wiki", True,
         "y la de Switch 2 también"),
        ("https://github.com/GameMakerEnterprise", False,
         "pero el centinela NO se excepciona a sí mismo: si él cae, hay que verlo"),
        ("https://github.com/YoYoGames/GMEXT-Steamworks", False,
         "un repositorio público de YoYo no entra"),
        ("https://github.com/GameMakerEnterpriseFalso/x", False,
         "ni un nombre de organización parecido"),
        ("https://gamemaker.io/es", False,
         "ni nada fuera de GitHub"),
    ]:
        entra = motivo_cerrado(url) is not None
        if entra == debe_entrar:
            print("  \u2713 " + nombre)
        else:
            fallos += 1
            print("  \u2717 %s  ->  entra=%s" % (nombre, entra))

    if fallos:
        print("\n\u2717 %d comprobación(es) de la autoprueba fallan." % fallos)
        return 1
    print("\n\u2713 Las %d comprobaciones de la autoprueba pasan." % (len(casos) + 8))
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
