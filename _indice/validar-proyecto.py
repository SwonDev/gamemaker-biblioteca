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
  · desconocida    → no lleva prefijo de familia; suele ser un nombre propio que falta
                     por definir o un método; se lista solo con --todo

Sale con 0 si no hay inventadas; con 1 si hay alguna.
"""
import os, re, sys, json, difflib, importlib.util

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
    d = json.load(open(os.path.join(IND, "simbolos.json"), encoding="utf-8"))
    return d["simbolos"], d.get("meta", {})


# La misma carpeta que consultan buscar.py y construir-indices.py (gm-cli guarda ahí
# los runtimes). buscar.py no se puede importar sin ejecutar su CLI, así que se repite
# la constante: si cambia allí, cambia aquí.
RUNTIMES = os.path.expanduser("~/Library/Caches/GameMakerCLI/runtimes-gms2")


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
    for fp in archivos:
        try:
            txt = open(fp, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        cod = vcg.limpiar(txt)
        codigos.append((fp, cod))
        for pat in (vcg.DEFINE, vcg.METODO, vcg.METODO_STRUCT):
            for m in pat.finditer(cod):
                definidas.add(m.group(1))

    inventadas, obsoletas, desconocidas = {}, {}, {}
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
            "desconocidas": {n: sorted(a) for n, a in desconocidas.items()},
        }, ensure_ascii=False, indent=1))
        return 1 if inventadas else 0

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
    if desconocidas and todo:
        print(f"\n· {len(desconocidas)} nombres que el proyecto no define ni el runtime declara "
              f"(métodos de struct, funciones que faltan o extensiones sin instalar):")
        for nom, donde in sorted(desconocidas.items()):
            print(f"  {nom}()  en {', '.join(sorted(donde)[:3])}")
    elif desconocidas:
        print(f"\n· {len(desconocidas)} nombres que el proyecto no define ni el runtime declara "
              f"(--todo para verlos): métodos de struct, funciones que faltan o extensiones sin instalar.")
    return 1 if inventadas else 0


if __name__ == "__main__":
    sys.exit(main())
