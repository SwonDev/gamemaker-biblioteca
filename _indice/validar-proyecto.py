#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validar-proyecto.py — ¿el GML de UN PROYECTO real llama a funciones que no existen?

Es el mismo control anti-alucinación que `validar-codigo-gml.py` aplica a la biblioteca,
pero apuntado a cualquier proyecto de GameMaker del disco. Pensado para que un agente
lo ejecute sobre su propio código ANTES de `gm-cli compile`: el compilador también lo
cazaría, pero este informe dice el nombre exacto, dónde está y qué símbolo parecido sí
existe.

    python3 "_indice/validar-proyecto.py" <ruta-del-proyecto> [--todo] [--json]

Recorre todos los `.gml` del proyecto (scripts y eventos de objetos) y clasifica cada
llamada `nombre(`:

  · runtime        → existe en GmlSpec.xml/fnames del runtime instalado (correcto)
  · propia         → la define el propio proyecto con `function nombre(` (correcto)
  · extensión      → la declara una extensión del propio proyecto (su .yy) (correcto)
  · obsoleta       → existe pero está marcada como obsoleta en el runtime (aviso)
  · INVENTADA      → lleva prefijo de familia del runtime y no existe (ERROR)
  · ARIDAD         → existe, pero se llama con un número de argumentos que su firma no
                     admite (ERROR) — el fallo de «existe, pero los argumentos están mal»
  · desconocida    → no lleva prefijo de familia; suele ser un nombre propio que falta
                     por definir o un método; se lista solo con --todo

Sale con 0 si no hay inventadas ni problemas de aridad; con 1 si hay alguna.
"""
import os, re, sys, json, difflib, importlib.util, platform

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


IND = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(IND)

# Reutiliza las expresiones y listas del validador de la biblioteca: una sola fuente.
_spec = importlib.util.spec_from_file_location("vcg", os.path.join(IND, "validar-codigo-gml.py"))
vcg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vcg)

FAMILIAS = ("draw_", "audio_", "gpu_", "ds_", "camera_", "instance_", "sprite_", "room_",
    "layer_", "surface_", "shader_", "buffer_", "string_", "file_", "ini_", "json_",
    "physics_", "part_", "path_", "mp_", "tile_", "tilemap_", "window_", "display_",
    "os_", "game_", "font_", "texture_", "vertex_", "matrix_", "math_", "keyboard_",
    "mouse_", "gamepad_", "view_", "event_", "object_", "asset_", "struct_", "array_",
    "variable_", "script_", "time_", "date_", "point_", "lengthdir_", "collision_",
    "place_", "move_", "distance_", "angle_", "animcurve_", "sequence_", "network_",
    "http_", "device_", "gesture_", "skeleton_", "video_", "layer_", "tileset_",
    "rollback_", "flexpanel_", "steam_", "dbg_", "ref_", "weak_ref_", "extension_",
    "debug_", "show_", "get_", "is_", "random", "irandom", "choose", "lerp", "clamp")

# Familias de extensiones NATIVAS (C++/JS/Java): sus funciones no están en GmlSpec ni en
# ningún .gml, solo en el .yy de la extensión. Si el proyecto declara la extensión, cualquier
# llamada de esa familia que NO esté declarada es inventada; si no la declara, la llamada
# queda como desconocida (falta instalar la extensión o el nombre es falso).
PREF_EXT = ("steam_", "admob_", "gpb_", "appleiap_", "gamecenter_", "firebase_",
            "levelplay_", "facebook_", "discord_", "photon_", "colyseus_", "epic_",
            "iap_", "ads_", "push_", "gxc_", "gpg_")


def cargar_simbolos():
    ruta = os.path.join(IND, "simbolos.json")
    if not os.path.exists(ruta):
        print("✗ No existe _indice/simbolos.json todavía.")
        print("  Se genera (desde el GmlSpec.xml de tu runtime instalado) con:")
        print("      python3 _indice/actualizar.py")
        sys.exit(1)
    d = json.load(open(ruta, encoding="utf-8"))
    return d["simbolos"], d.get("meta", {})


# La misma carpeta que consultan buscar.py y construir-indices.py (gm-cli guarda ahí
# los runtimes). buscar.py no se puede importar sin ejecutar su CLI, así que se repite
# la constante: si cambia allí, cambia aquí.
def _ruta_cache_gamemakercli():
    """Réplica de la lógica de gm-cli (ver buscar.py, misma función, para el porqué
    exacto): macOS → ~/Library/Caches, Windows → %LOCALAPPDATA%\\GameMakerCLI\\cache,
    resto → XDG_CACHE_HOME. No verificado fuera de macOS."""
    home = os.path.expanduser("~")
    sistema = platform.system()
    if sistema == "Darwin":
        return os.path.join(home, "Library", "Caches", "GameMakerCLI")
    if sistema == "Windows":
        base = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
        return os.path.join(base, "GameMakerCLI", "cache")
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(home, ".cache")
    return os.path.join(base, "GameMakerCLI")


RUNTIMES = os.path.join(_ruta_cache_gamemakercli(), "runtimes-gms2")


def runtime_instalado():
    """Versión del runtime que hay en disco, para avisar si el índice caducó."""
    try:
        rts = sorted(d for d in os.listdir(RUNTIMES) if d.startswith("runtime-"))
    except OSError:
        return None
    return rts[-1].replace("runtime-", "") if rts else None


def gml_del_proyecto(ruta):
    for raiz, dirs, files in os.walk(ruta):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"node_modules"}]
        for f in files:
            if f.endswith(".gml"):
                yield os.path.join(raiz, f)


def extensiones_del_proyecto(ruta):
    """Funciones declaradas por las extensiones del propio proyecto (.yy de extensión)."""
    nombres = set()
    for raiz, dirs, files in os.walk(os.path.join(ruta, "extensions")):
        for f in files:
            if not f.endswith(".yy"):
                continue
            try:
                txt = open(os.path.join(raiz, f), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in re.finditer(r'"externalName"\s*:\s*"([A-Za-z_][A-Za-z0-9_]*)"', txt):
                nombres.add(m.group(1))
            for m in re.finditer(r'"name"\s*:\s*"([A-Za-z_][A-Za-z0-9_]*)"', txt):
                nombres.add(m.group(1))
    return nombres


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    todo = "--todo" in sys.argv
    como_json = "--json" in sys.argv
    if not args:
        print(__doc__)
        return 2
    proyecto = os.path.abspath(args[0])
    if not os.path.isdir(proyecto):
        print(f"No existe la carpeta: {proyecto}")
        return 2
    if not any(f.endswith(".yyp") for f in os.listdir(proyecto)):
        print(f"⚠ En {proyecto} no hay ningún .yyp: se analizan igualmente los .gml que haya.")

    simb, meta = cargar_simbolos()
    instalado = runtime_instalado()
    if instalado and instalado != meta.get("runtime"):
        print(f"⚠ ÍNDICE CADUCADO: simbolos.json es del runtime {meta.get('runtime')} y el "
              f"instalado es {instalado}. Regenera con: python3 _indice/actualizar.py")

    # Solo cuenta lo que el proyecto trae de verdad: sus .gml y sus extensiones. Las
    # librerías descargadas en la biblioteca NO valen aquí: muchas traen «shims» de
    # funciones retiradas (instance_create, draw_set_blend_mode…) que taparían un error real.
    externas = extensiones_del_proyecto(proyecto)
    familias_ext_declaradas = {p for p in PREF_EXT if any(n.startswith(p) for n in externas)}

    archivos = list(gml_del_proyecto(proyecto))
    definidas = set()
    codigos = []
    crudos = {}          # fuente SIN limpiar, para el contraste de §desconocidas
    literales_rotos = [] # (archivo, líneas) con una cadena que no cierra
    for fp in archivos:
        try:
            txt = open(fp, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        cod = vcg.limpiar(txt)
        codigos.append((fp, cod))
        crudos[fp] = txt
        _rotas = vcg.comillas_descuadradas(txt)
        if _rotas:
            literales_rotos.append((os.path.relpath(fp, proyecto), _rotas))
        for pat in (vcg.DEFINE, vcg.METODO, vcg.METODO_STRUCT):
            for m in pat.finditer(cod):
                definidas.add(m.group(1))

    # {nombre: (mínimo, máximo|None, variádica)} de cada función con firma conocida —
    # existir no basta: el número de argumentos con el que se llama tiene que caber
    # en su firma. Es el mismo control que aplica validar-codigo-gml.py a la biblioteca.
    aridad = vcg.aridades_funciones(simb)

    inventadas, obsoletas, desconocidas, problemas_aridad = {}, {}, {}, {}
    total = 0
    for fp, cod in codigos:
        rel = os.path.relpath(fp, proyecto)
        for m in vcg.LLAMADA.finditer(cod):
            nom = m.group(1)
            total += 1
            if nom in vcg.PALABRAS or nom in definidas or nom.startswith(vcg.PREF_ASSET) \
                    or nom.startswith("_"):
                continue
            if nom in simb:
                if simb[nom].get("obsoleta"):
                    obsoletas.setdefault(nom, set()).add(rel)
                if nom in aridad:
                    minimo, maximo, variadica = aridad[nom]
                    n_args = vcg.contar_argumentos(cod, m.end())
                    if n_args is not None:
                        if n_args < minimo:
                            rango = f"mínimo {minimo}" if variadica else f"entre {minimo} y {maximo}"
                            problemas_aridad.setdefault(nom, []).append(
                                (rel, f"{n_args} argumento(s) — la firma exige {rango}"))
                        elif maximo is not None and n_args > maximo:
                            problemas_aridad.setdefault(nom, []).append(
                                (rel, f"{n_args} argumento(s) — la firma admite entre {minimo} y {maximo}"))
                continue
            if nom in externas:
                continue
            if nom.startswith(PREF_EXT):
                if nom.startswith(tuple(familias_ext_declaradas)):
                    inventadas.setdefault(nom, set()).add(rel)   # la extensión está y no la declara
                else:
                    desconocidas.setdefault(nom, set()).add(rel) # extensión sin instalar, o falsa
                continue
            if nom.startswith(FAMILIAS):
                inventadas.setdefault(nom, set()).add(rel)
            else:
                desconocidas.setdefault(nom, set()).add(rel)

    def parecidos(nom):
        return difflib.get_close_matches(nom, simb.keys(), n=3, cutoff=0.75)

    if como_json:
        print(json.dumps({
            "proyecto": proyecto, "archivos_gml": len(archivos), "llamadas": total,
            "inventadas": {n: {"en": sorted(a), "parecidas": parecidos(n)} for n, a in inventadas.items()},
            "obsoletas": {n: sorted(a) for n, a in obsoletas.items()},
            "aridad_incorrecta": {n: [{"en": d, "problema": msg} for d, msg in casos]
                                   for n, casos in problemas_aridad.items()},
            "desconocidas": {n: sorted(a) for n, a in desconocidas.items()},
        }, ensure_ascii=False, indent=1))
        return 1 if (inventadas or problemas_aridad) else 0

    print(f"{len(archivos)} archivos .gml · {total} llamadas analizadas · runtime del índice "
          f"{meta.get('runtime')}")
    if inventadas:
        print(f"\n\033[1m✗ {len(inventadas)} funciones INVENTADAS (no existen en el runtime):\033[0m")
        for nom, donde in sorted(inventadas.items()):
            p = parecidos(nom)
            print(f"  {nom}()")
            for d in sorted(donde)[:4]:
                print(f"      en {d}")
            if p:
                print(f"      ¿quisiste decir? {', '.join(p)}")
            print(f"      ficha: python3 \"_indice/buscar.py\" {p[0] if p else nom}")
    else:
        print("\n✓ Ninguna llamada a una función del runtime que no exista.")
    if obsoletas:
        print(f"\n⚠ {len(obsoletas)} funciones OBSOLETAS (existen, pero el runtime las retira):")
        for nom, donde in sorted(obsoletas.items()):
            print(f"  {nom}()  →  python3 \"_indice/buscar.py\" {nom}   (te dice la alternativa)")
            for d in sorted(donde)[:3]:
                print(f"      en {d}")
    if problemas_aridad:
        n_llamadas = sum(len(v) for v in problemas_aridad.values())
        print(f"\n\033[1m✗ {n_llamadas} llamada(s) a {len(problemas_aridad)} función(es) con un número "
              f"de argumentos que no cuadra con su firma:\033[0m")
        print("  (existir no basta: la firma completa es la que manda — ver `buscar.py <función>`)")
        for nom, casos in sorted(problemas_aridad.items()):
            for d, msg in casos:
                print(f"  {nom}()  ·  {msg}  ·  en {d}")
    else:
        print("\n✓ Ninguna llamada a una función del runtime con un número de argumentos "
              "que no cuadre con su firma.")
    # Un literal sin cerrar descuadra el análisis del archivo entero: lo que sigue a la
    # comilla huérfana se lee como cadena, y las funciones definidas ahí «desaparecen».
    # Se avisa ANTES de la lista de desconocidas porque, sin este aviso, esa lista mezcla
    # nombres falsos con los de verdad y enseña a desconfiar de ella entera — que es
    # exactamente cómo se cuela el fallo que sí importa.
    if literales_rotos:
        print(f"\n⚠ {len(literales_rotos)} archivo(s) con una cadena que NO cierra. GameMaker no")
        print("  los compilará, y mientras tanto este análisis pierde lo que venga después:")
        for rel, lineas in literales_rotos[:10]:
            print(f"  {rel}  ·  línea(s) {', '.join(str(x) for x in lineas[:6])}")
        print("  Suele ser un generador que escribe un « \" » sin escapar dentro del literal.")
        print("  Arregla esto ANTES de leer la lista de nombres desconocidos de abajo.")

    # Contraste contra el fuente crudo: si el nombre SÍ aparece definido en el archivo,
    # el análisis se perdió (casi siempre por lo de arriba) y decirlo evita que alguien
    # persiga una función que existe.
    fantasmas = set()
    if desconocidas:
        crudo_todo = "\n".join(crudos.values())
        for nom in desconocidas:
            if re.search(r"function\s+" + re.escape(nom) + r"\s*\(", crudo_todo):
                fantasmas.add(nom)
    if fantasmas:
        print(f"\n⚠ {len(fantasmas)} de esos nombres SÍ están definidos en el proyecto y el")
        print("  analizador no los vio — no los persigas, arregla el archivo que los contiene:")
        print("      " + ", ".join(sorted(fantasmas)))

    if desconocidas and todo:
        reales = {n: d for n, d in desconocidas.items() if n not in fantasmas}
        print(f"\n· {len(reales)} nombres que el proyecto no define ni el runtime declara "
              f"(métodos de struct, funciones que faltan o extensiones sin instalar):")
        for nom, donde in sorted(reales.items()):
            print(f"  {nom}()  en {', '.join(sorted(donde)[:3])}")
    elif desconocidas:
        print(f"\n· {len(desconocidas)} nombres que el proyecto no define ni el runtime declara "
              f"(--todo para verlos): métodos de struct, funciones que faltan o extensiones sin instalar.")
    return 1 if (inventadas or problemas_aridad) else 0


def autoprueba():
    """Casos que ya han mordido, montados como proyectos de mentira.

    Este script es el que un agente corre sobre SU juego, así que sus dos formas
    de equivocarse son caras y opuestas: dejar pasar una función inventada (y el
    juego no arranca) o señalar una real (y se enseña a desconfiar de la lista
    entera, que es peor — pasó en r12).
    """
    import subprocess, tempfile
    yo = os.path.abspath(__file__)
    fallos = []

    def revisar(nombre, condicion, detalle=""):
        if condicion:
            print("  ✓ " + nombre)
        else:
            fallos.append(nombre)
            print("  ✗ %s  ->  %s" % (nombre, detalle))

    def proyecto(base, ficheros):
        os.makedirs(base, exist_ok=True)
        with open(os.path.join(base, "falso.yyp"), "w", encoding="utf-8") as f:
            f.write('{"resources":[]}')
        for nombre, codigo in ficheros.items():
            d = os.path.join(base, "scripts", nombre)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, nombre + ".gml"), "w", encoding="utf-8") as f:
                f.write(codigo)
        r = subprocess.run([sys.executable, yo, base, "--todo"], capture_output=True, text=True)
        return r.returncode, r.stdout

    with tempfile.TemporaryDirectory() as tmp:
        # 1 · Código correcto: no puede dar ni un falso positivo.
        c, o = proyecto(os.path.join(tmp, "bien"), {
            "scr_ok": "function mover() {\n  x += lengthdir_x(4, image_angle);\n"
                      "  draw_sprite_ext(spr, 0, x, y, 1, 1, 0, c_white, 1);\n}\n"})
        revisar("código correcto sale con 0", c == 0, "exit %d · %s" % (c, o.strip()[-120:]))

        # 2 · Una función del runtime que NO existe: tiene que cazarla.
        c, o = proyecto(os.path.join(tmp, "inventada"), {
            "scr_mal": "function pinta() {\n  sprite_set_interpolation(spr, false);\n}\n"})
        revisar("una función inventada del runtime se caza", c != 0, "exit %d" % c)
        revisar("y la nombra en la salida", "sprite_set_interpolation" in o, o.strip()[-120:])

        # 3 · El caso de r15 §2.3: `case "@":` no puede romper el análisis.
        c, o = proyecto(os.path.join(tmp, "arroba"), {
            "scr_mapa": 'function leer(_c) {\n  switch (_c) {\n    case "@": return 1;\n'
                        '    case "S": return 2;\n  }\n  return 0;\n}\n'})
        revisar("`case \"@\":` no dispara el aviso de cadena sin cerrar",
                "NO cierra" not in o and c == 0, o.strip()[-140:])

        # 4 · Una cadena de verdad sin cerrar SÍ tiene que avisar.
        c, o = proyecto(os.path.join(tmp, "rota"), {
            "scr_rota": 'function mal() {\n  var _t = "sin cerrar;\n  return _t;\n}\n'})
        revisar("una cadena sin cerrar de verdad SÍ se avisa", "NO cierra" in o, o.strip()[-140:])

        # 5 · Lo que el propio proyecto define no es «inventado».
        c, o = proyecto(os.path.join(tmp, "propia"), {
            "scr_mias": "function mi_helper() { return 1; }\n"
                        "function usa() { return mi_helper() + 1; }\n"})
        revisar("una función propia del proyecto no se marca como inventada", c == 0,
                "exit %d · %s" % (c, o.strip()[-120:]))

        # 6 · Sin argumentos: no puede salir con 0 fingiendo que todo está bien.
        r = subprocess.run([sys.executable, yo], capture_output=True, text=True)
        revisar("sin argumentos NO sale con 0", r.returncode != 0, "exit %d" % r.returncode)

        # 7 · Una carpeta que no existe tampoco.
        r = subprocess.run([sys.executable, yo, os.path.join(tmp, "no_existe")],
                           capture_output=True, text=True)
        revisar("una carpeta inexistente NO sale con 0", r.returncode != 0, "exit %d" % r.returncode)

    if fallos:
        print("\n✗ %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n✓ Las 8 comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
