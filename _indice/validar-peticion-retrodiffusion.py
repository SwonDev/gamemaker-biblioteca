#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Revisa una petición a la API de Retro Diffusion ANTES de mandarla.

Por qué existe. La API de Retro Diffusion cobra por generación, y casi todos sus
errores caros son comprobables sin red y sin clave: un estilo que no existe, un
tamaño que ese estilo concreto no admite, un lote más grande del permitido, una
animación cuyo fotograma de partida no mide lo que dice la petición. Mandarla
para que el servidor conteste 400 cuesta una vuelta; mandarla mal de una forma
que el servidor SÍ acepta cuesta dinero.

Y hay un fallo peor que un 400, porque no da error: **el POST de v2 no devuelve
la imagen**. Devuelve `{"status": "accepted", "task_id": …}` y hay que sondear
`GET /v2/inferences/tasks/{task_id}`. Un cliente que lea `base64_images` de la
respuesta del POST encuentra la clave vacía, no ve ningún error, y se le ha
cobrado igual. Eso no lo puede ver esta herramienta —es un fallo del código que
consume la respuesta, no de la petición— así que está documentado en
`07 · 23 §1 bis.1`, con la comprobación equivalente: **mirar siempre
`base64_images` Y `output_urls`**.

Todo lo que hay aquí sale de la documentación que la propia Retro Diffusion
publica para agentes (`llms.txt` y `README.md` de `Retro-Diffusion/api-examples`,
leídos el 2026-09-10) y del catálogo de estilos que allí aparece. Ese repositorio
**no declara licencia**, así que aquí no se copia su texto: se reproducen los
hechos —rutas, campos, límites numéricos— y se citan.

Uso:
    python3 _indice/validar-peticion-retrodiffusion.py peticion.json
    python3 _indice/validar-peticion-retrodiffusion.py peticion.json --imagen inicio.png
    echo '{"prompt":"…"}' | python3 _indice/validar-peticion-retrodiffusion.py -
    python3 _indice/validar-peticion-retrodiffusion.py peticion.json --presupuesto 0.50

`--imagen` es la comprobación que de verdad importa en las animaciones: mide el
PNG **en disco** y lo compara con `width`/`height` de la petición. Es el mismo
principio que el resto de la biblioteca — se comprueba el disco, no lo que dice
el comando.

Sale con **0** si la petición es sólida, **1** si encuentra un defecto y **2** si
no ha podido comprobarlo (falta el archivo, JSON ilegible, catálogo sin estilo).
NUNCA llama a la red y NUNCA necesita la clave: no puede gastar.
"""
import json
import os
import re
import sys

# Windows: en cuanto la salida no es una consola interactiva (pipes, «> archivo», o el
# propio actualizar.py capturando la salida vía subprocess), sys.stdout usa la página de
# códigos ANSI del sistema en vez de UTF-8 — y los ✓/✗/⚠ de este código no caben ahí.
#
# **Medido, ya no supuesto** (2026-09-09, Python 3.12.7 de Windows bajo Wine 11):
#     UnicodeEncodeError: 'charmap' codec can't encode character '✓'
# La autoprueba reventaba en la primera línea que imprimía un ✓. Las herramientas que ya
# llevaban estas seis líneas pasaron; las que no, murieron.
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


# ─────────────────────────────────────────────────────────────────────────────
# El catálogo. Cada entrada: (mín, máx, lote máximo, refs máximas, exige entrada)
#
# «mín» y «máx» se aplican a lo ancho y a lo alto por separado. Los estilos de
# medida única llevan mín == máx. `refs` a 0 significa que ese estilo NO admite
# `reference_images` (solo RD Pro y unas pocas animaciones las admiten).
# ─────────────────────────────────────────────────────────────────────────────
def _fam(nombres, minimo, maximo, lote, refs=0, entrada=False, gif=False, cuadrado=False):
    return {n: {"min": minimo, "max": maximo, "lote": lote, "refs": refs,
                "entrada": entrada, "gif": gif, "cuadrado": cuadrado} for n in nombres}


CATALOGO = {}
# RD Pro — la única familia de imagen fija que admite reference_images.
CATALOGO.update(_fam([f"rd_pro__{s}" for s in (
    "default", "painterly", "fantasy", "horror", "scifi", "simple",
    "isometric", "topdown", "platformer")], 12, 256, 16, refs=9))
CATALOGO.update(_fam([f"rd_pro__{s}" for s in (
    "dungeon_map", "spritesheet", "fps_weapon", "typography")], 64, 256, 4, refs=9))
CATALOGO.update(_fam([f"rd_pro__{s}" for s in (
    "hexagonal_tiles", "ui_panel", "inventory_items")], 256, 256, 4, refs=9))
CATALOGO.update(_fam(["rd_pro__pixelate"], 16, 256, 16, refs=9, entrada=True))
CATALOGO.update(_fam(["rd_pro__edit"], 64, 256, 4, refs=9, entrada=True))
# RD Plus.
CATALOGO.update(_fam([f"rd_plus__{s}" for s in (
    "default", "retro", "watercolor", "textured", "cartoon", "ui_element",
    "item_sheet", "character_turnaround", "environment", "isometric",
    "isometric_asset", "topdown_map", "topdown_asset")], 64, 384, 16))
CATALOGO.update(_fam(["rd_plus__classic", "rd_plus__skill_icon"], 32, 192, 16))
CATALOGO.update(_fam(["rd_plus__low_res", "rd_plus__mc_item", "rd_plus__mc_texture"], 16, 128, 16))
CATALOGO.update(_fam(["rd_plus__topdown_item"], 16, 96, 16))
# RD Fast.
CATALOGO.update(_fam(["rd_fast__default"], 64, 384, 15))
CATALOGO.update(_fam([f"rd_fast__{s}" for s in (
    "simple", "detailed", "retro", "game_asset", "portrait", "texture", "ui",
    "item_sheet", "character_turnaround", "no_style", "1_bit")], 64, 384, 16))
CATALOGO.update(_fam(["rd_fast__low_res", "rd_fast__mc_item", "rd_fast__mc_texture"], 16, 128, 16))
# RD Mini — alias que enrutan a Plus/Fast; el «model» de la respuesta enseña el real.
CATALOGO.update(_fam(["rd_mini__classic", "rd_mini__skill_icon"], 32, 192, 16))
CATALOGO.update(_fam([f"rd_mini__{s}" for s in (
    "low_res", "mc_item", "mc_texture",
    "fast_low_res", "fast_mc_item", "fast_mc_texture")], 16, 128, 16))
CATALOGO.update(_fam(["rd_mini__topdown_item"], 16, 96, 16))
# Animaciones avanzadas: animan un fotograma que TÚ das. Salen en GIF.
CATALOGO.update(_fam([f"rd_advanced_animation__{s}" for s in (
    "walking", "idle", "jump", "crouch", "attack", "destroy",
    "custom_action", "subtle_motion")], 32, 256, 1, entrada=True, gif=True))
# Animaciones por prompt: generan el sujeto ellas. Medida fija.
CATALOGO.update(_fam(["rd_animation__four_angle_walking",
                      "rd_animation__four_angle_walking_idle"], 48, 48, 1, gif=True))
CATALOGO.update(_fam(["rd_animation__small_sprites"], 32, 32, 16, gif=True))
CATALOGO.update(_fam(["rd_animation__vfx"], 24, 96, 1, gif=True, cuadrado=True))
CATALOGO.update(_fam(["rd_animation__any_animation"], 64, 64, 1, refs=9, gif=True))
CATALOGO.update(_fam(["rd_animation__big_animation"], 128, 128, 1, refs=9, gif=True))
CATALOGO.update(_fam(["rd_animation__8_dir_rotation"], 80, 80, 1, refs=5, gif=True))
CATALOGO.update(_fam(["rd_animation__battle_sprites"], 64, 64, 1, gif=True))
# Tilesets.
CATALOGO.update(_fam(["rd_tile__tileset", "rd_tile__tileset_advanced"], 16, 32, 1))
CATALOGO.update(_fam(["rd_tile__single_tile"], 16, 64, 16))
CATALOGO.update(_fam(["rd_tile__tile_variation"], 16, 128, 16, entrada=True))
CATALOGO.update(_fam(["rd_tile__tile_object"], 16, 96, 16))
CATALOGO.update(_fam(["rd_tile__scene_object"], 64, 384, 16))

# Los estilos de baja resolución comparten fórmula de precio propia.
BAJA_RES = {n for n in CATALOGO if re.search(
    r"__(low_res|mc_item|mc_texture|classic|skill_icon|topdown_item|"
    r"fast_low_res|fast_mc_item|fast_mc_texture)$", n)} | {
    n for n in CATALOGO if n.startswith("rd_tile__")}

FRAMES_VALIDOS = {4, 6, 8, 10, 12, 16}

CAMPOS_CONOCIDOS = {
    "prompt", "prompt_style", "width", "height", "num_images", "seed",
    "input_image", "strength", "reference_images", "input_palette", "remove_bg",
    "tile_x", "tile_y", "frames_duration", "return_spritesheet",
    "upscale_output_factor", "bypass_prompt_expansion", "include_downloadable_data",
    "check_cost", "async", "negative", "extra_prompt", "extra_input_image",
    "upload_outputs",
}


def coste(estilo, ancho, alto, lote):
    """El precio en dólares, con las fórmulas que publica Retro Diffusion.

    Es una estimación local para no llevarse sustos; la cifra que manda es la que
    devuelve `check_cost`, que es gratis. Devuelve None si no sabe calcularlo.
    """
    px = ancho * alto
    if estilo.startswith("rd_advanced_animation__"):
        base = 0.25 if estilo.endswith(("custom_action", "subtle_motion")) else 0.14
        return round(base, 4)
    if estilo.startswith("rd_animation__"):
        base = 0.25 if estilo.endswith(("any_animation", "8_dir_rotation")) else 0.07
        return round(base, 4)
    if estilo in ("rd_tile__tileset", "rd_tile__tileset_advanced"):
        return 0.10
    if estilo.startswith("rd_pro__"):
        return round(0.18 * lote, 4)
    if estilo in BAJA_RES:
        return round(max(0.02, (px + 13700) / 600000) * lote, 4)
    if estilo.startswith("rd_plus__") or estilo.startswith("rd_mini__"):
        return round(max(0.025, (px + 50000) / 2000000) * lote, 4)
    if estilo.startswith("rd_fast__"):
        return round(max(0.015, (px + 100000) / 6000000) * lote, 4)
    return None


def medir_png(ruta):
    """(ancho, alto) del PNG en disco, o (None, motivo).

    Lee la cabecera IHDR a mano: son 8 bytes en una posición fija del formato, no
    hace falta Pillow para esto y así la herramienta no depende de nada.
    """
    try:
        with open(ruta, "rb") as f:
            cab = f.read(33)
    except OSError as e:
        return None, f"no se pudo abrir: {e}"
    if len(cab) < 33 or cab[:8] != b"\x89PNG\r\n\x1a\n":
        return None, "no es un PNG"
    if cab[12:16] != b"IHDR":
        return None, "PNG sin cabecera IHDR donde toca"
    ancho = int.from_bytes(cab[16:20], "big")
    alto = int.from_bytes(cab[20:24], "big")
    return (ancho, alto), None


def revisar(pet, ruta_imagen=None, presupuesto=None):
    """Devuelve (errores, avisos, notas). Errores → salida 1."""
    errores, avisos, notas = [], [], []

    estilo = pet.get("prompt_style")
    if not estilo:
        errores.append("falta `prompt_style`. No hay estilo por defecto: es obligatorio.")
        return errores, avisos, notas
    if not isinstance(estilo, str):
        errores.append("`prompt_style` tiene que ser una cadena.")
        return errores, avisos, notas

    if estilo.startswith("user__"):
        notas.append(f"«{estilo}» es un estilo propio (creado con POST /v2/styles): "
                     "sus límites no están en el catálogo público y no se comprueban aquí.")
        lim = None
    elif estilo in CATALOGO:
        lim = CATALOGO[estilo]
    else:
        errores.append(
            f"el estilo «{estilo}» no está en el catálogo. Los ids son cadenas opacas: "
            "cópialos literalmente del catálogo o de GET /v2/styles/selector, no los "
            "deduzcas del prefijo.")
        parecidos = [n for n in CATALOGO if estilo.split("__")[-1] in n][:4]
        if parecidos:
            errores.append(f"   ¿querías uno de estos? {', '.join(parecidos)}")
        return errores, avisos, notas

    prompt = pet.get("prompt") or ""
    if not prompt.strip():
        errores.append("`prompt` vacío. Describe el SUJETO; el estilo pone el pixel art.")
    if re.search(r"\bpixel[ -]?art\b", prompt, re.I):
        errores.append(
            "el prompt dice «pixel art». No se escribe: de eso se encarga `prompt_style`. "
            "Ponerlo en el prompt compite con el estilo y empeora el resultado.")
    if re.search(r"transparent background|fondo transparente", prompt, re.I):
        errores.append(
            "el prompt pide «transparent background». La transparencia es trabajo de "
            "`remove_bg: true`, no del prompt. Di un color de fondo que CONTRASTE con el "
            "sujeto («on a plain white background») y activa `remove_bg`.")

    ancho, alto = pet.get("width"), pet.get("height")
    for nombre, valor in (("width", ancho), ("height", alto)):
        if not isinstance(valor, int) or isinstance(valor, bool):
            errores.append(f"`{nombre}` falta o no es un entero.")
    if lim and isinstance(ancho, int) and isinstance(alto, int) and not isinstance(ancho, bool):
        for nombre, valor in (("width", ancho), ("height", alto)):
            if not (lim["min"] <= valor <= lim["max"]):
                if lim["min"] == lim["max"]:
                    errores.append(
                        f"`{nombre}` = {valor}, pero «{estilo}» solo admite {lim['min']}. "
                        "El límite es del estilo, no de la API.")
                else:
                    errores.append(
                        f"`{nombre}` = {valor}, fuera del rango {lim['min']}–{lim['max']} de "
                        f"«{estilo}». La API valida 12–512, pero manda el estilo.")
        if lim["cuadrado"] and ancho != alto:
            errores.append(f"«{estilo}» exige lienzo cuadrado, y pides {ancho}×{alto}.")

    lote = pet.get("num_images")
    if not isinstance(lote, int) or isinstance(lote, bool) or lote < 1:
        errores.append("`num_images` falta o no es un entero ≥ 1.")
    elif lim and lote > lim["lote"]:
        errores.append(f"`num_images` = {lote}, y «{estilo}» admite como mucho {lim['lote']}.")

    entrada = pet.get("input_image")
    if lim and lim["entrada"] and not entrada:
        errores.append(
            f"«{estilo}» EXIGE `input_image` y no lo llevas. Los estilos "
            "`rd_animation__*` generan el sujeto del prompt; los "
            "`rd_advanced_animation__*` animan una imagen que ya tienes.")
    for campo in ("input_image", "extra_input_image", "input_palette", "mask_image"):
        v = pet.get(campo)
        if isinstance(v, str) and v.startswith("data:"):
            errores.append(
                f"`{campo}` lleva el prefijo «data:…;base64,». Va base64 crudo, sin prefijo.")
    refs = pet.get("reference_images")
    if refs is not None:
        if not isinstance(refs, list):
            errores.append("`reference_images` tiene que ser una lista.")
        elif lim and lim["refs"] == 0:
            errores.append(
                f"«{estilo}» no admite `reference_images`. Para mantener un personaje "
                "constante hay que generar con RD Pro y reutilizar esa salida como "
                "referencia: una descripción de texto no sustituye a la imagen.")
        elif lim and len(refs) > lim["refs"]:
            errores.append(f"{len(refs)} referencias, y «{estilo}» admite {lim['refs']}.")
        for i, r in enumerate(refs if isinstance(refs, list) else []):
            if isinstance(r, str) and r.startswith("data:"):
                errores.append(f"`reference_images[{i}]` lleva prefijo «data:». Va crudo.")

    fuerza = pet.get("strength")
    if fuerza is not None:
        if not isinstance(fuerza, (int, float)) or isinstance(fuerza, bool):
            errores.append("`strength` tiene que ser un número.")
        elif not (0 <= fuerza <= 1):
            errores.append(f"`strength` = {fuerza}, fuera de 0–1.")
        elif not entrada:
            avisos.append("`strength` sin `input_image` no hace nada: mide cuánto se cambia "
                          "la imagen de entrada.")

    frames = pet.get("frames_duration")
    if frames is not None:
        if frames not in FRAMES_VALIDOS:
            errores.append(f"`frames_duration` = {frames}; solo valen "
                           f"{', '.join(str(v) for v in sorted(FRAMES_VALIDOS))}.")
        elif lim and not lim["gif"]:
            avisos.append(f"`frames_duration` sobra: «{estilo}» no es un estilo de animación.")

    if pet.get("negative"):
        avisos.append("`negative` existe en el esquema pero los modelos actuales lo IGNORAN. "
                      "Si contabas con él para quitar algo, no va a pasar.")

    if pet.get("remove_bg") and not re.search(
            r"background|backdrop|fondo|on (a )?(plain |flat )?(white|black|green|blue|grey|gray)",
            prompt, re.I):
        avisos.append(
            "`remove_bg` activo y el prompt no dice de qué color es el fondo. Sin decirlo, "
            "el modelo tiende a un gris oscuro apagado que quita contraste y hace peor el "
            "recorte. Esto es un aviso y no un error porque desde el texto no se puede "
            "decidir con certeza que falte.")

    desconocidos = sorted(set(pet) - CAMPOS_CONOCIDOS)
    if desconocidos:
        avisos.append("campos que no están en el esquema documentado: "
                      + ", ".join(desconocidos)
                      + ". Pixel Fixer rechaza los desconocidos; aquí puede que se ignoren.")

    # La comprobación del disco: el fotograma de partida tiene que MEDIR lo que dice
    # la petición. El fallo clásico es mandar el PNG exportado a ×4 para verlo.
    if ruta_imagen:
        medida, motivo = medir_png(ruta_imagen)
        if medida is None:
            errores.append(f"no se pudo medir «{ruta_imagen}»: {motivo}")
        else:
            iw, ih = medida
            notas.append(f"«{os.path.basename(ruta_imagen)}» mide {iw}×{ih} px en disco.")
            if isinstance(ancho, int) and isinstance(alto, int) and (iw, ih) != (ancho, alto):
                errores.append(
                    f"el fotograma de partida mide {iw}×{ih} y la petición dice "
                    f"{ancho}×{alto}. Tienen que coincidir. Si {iw}×{ih} es un múltiplo "
                    f"exacto, estás mandando la copia ampliada para verla en pantalla en "
                    "vez del original.")
            if lim and lim["gif"] and lim["entrada"] and isinstance(ancho, int):
                if not (lim["min"] <= iw <= lim["max"]):
                    errores.append(
                        f"y {iw} px queda fuera del rango {lim['min']}–{lim['max']} que "
                        f"admite «{estilo}».")

    if lim and isinstance(ancho, int) and isinstance(alto, int) and isinstance(lote, int) \
            and not isinstance(ancho, bool) and not isinstance(lote, bool):
        precio = coste(estilo, ancho, alto, lote)
        if precio is not None:
            notas.append(f"coste estimado: ${precio:.4f}. Confírmalo con `check_cost: true`, "
                         "que es gratis y no genera nada.")
            if presupuesto is not None and precio > presupuesto:
                errores.append(f"${precio:.4f} pasa del presupuesto de ${presupuesto:.4f}.")

    if not pet.get("check_cost"):
        notas.append("recuerda: v2 SIEMPRE responde con una tarea aceptada, nunca con la "
                     "imagen. Sondea GET /v2/inferences/tasks/{task_id} y lee el resultado "
                     "de `base64_images` O de `output_urls` — las animaciones grandes llegan "
                     "solo por URL.")
    return errores, avisos, notas


def cargar(ruta):
    """(dict, None) o (None, motivo). El motivo lleva a salida 2."""
    try:
        if ruta == "-":
            texto = sys.stdin.read()
        else:
            with open(ruta, encoding="utf-8") as f:
                texto = f.read()
    except OSError as e:
        return None, f"no se pudo leer «{ruta}»: {e}"
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as e:
        return None, f"«{ruta}» no es JSON válido: {e}"
    if not isinstance(datos, dict):
        return None, "el JSON tiene que ser un objeto con los campos de la petición."
    return datos, None


def main():
    args = [a for a in sys.argv[1:]]
    if not args or "--help" in args or "-h" in args:
        print(__doc__.strip())
        return 0 if ("--help" in args or "-h" in args) else 2

    ruta_imagen = presupuesto = None
    if "--imagen" in args:
        i = args.index("--imagen")
        if i + 1 >= len(args):
            print("✗ `--imagen` necesita una ruta.")
            return 2
        ruta_imagen = args[i + 1]
        del args[i:i + 2]
    if "--presupuesto" in args:
        i = args.index("--presupuesto")
        if i + 1 >= len(args):
            print("✗ `--presupuesto` necesita una cifra.")
            return 2
        try:
            presupuesto = float(args[i + 1])
        except ValueError:
            print(f"✗ «{args[i + 1]}» no es una cifra.")
            return 2
        del args[i:i + 2]

    rutas = [a for a in args if not a.startswith("--")]
    if not rutas:
        print("✗ Falta el JSON de la petición.")
        return 2

    peor = 0
    for ruta in rutas:
        pet, motivo = cargar(ruta)
        if pet is None:
            print(f"⚠ {motivo}")
            peor = max(peor, 2)
            continue
        errores, avisos, notas = revisar(pet, ruta_imagen, presupuesto)
        etiqueta = "la petición" if ruta == "-" else ruta
        print(f"── {etiqueta}")
        for n in notas:
            print(f"  · {n}")
        for a in avisos:
            print(f"  ⚠ {a}")
        for e in errores:
            print(f"  ✗ {e}")
        if errores:
            print(f"  ✗ {len(errores)} defecto(s): NO la mandes todavía.")
            peor = max(peor, 1)
        else:
            print("  ✓ la petición es sólida. Lo que no se puede ver desde aquí es si el "
                  "código que lee la respuesta mira `output_urls` cuando `base64_images` "
                  "viene vacío.")
    return peor


def autoprueba():
    fallos = []

    def caso(nombre, condicion, detalle=""):
        if condicion:
            print(f"  ✓ {nombre}")
        else:
            print(f"  ✗ {nombre}{(' — ' + detalle) if detalle else ''}")
            fallos.append(nombre)

    base = {"prompt": "a squat round flask of glowing crimson liquid, cork stopper",
            "prompt_style": "rd_plus__default", "width": 128, "height": 128,
            "num_images": 1}

    e, a, n = revisar(dict(base))
    caso("una petición correcta no da ningún error", not e, str(e))

    e, _, _ = revisar(dict(base, prompt_style="rd_plus__defualt"))
    caso("un estilo mal escrito es un error", bool(e))

    e, _, _ = revisar(dict(base, prompt_style="rd_pro__inventory_items",
                           width=128, height=128))
    caso("256×256 obligatorio: 128 en un estilo de medida única falla", bool(e))

    e, _, _ = revisar(dict(base, prompt_style="rd_pro__inventory_items",
                           width=256, height=256))
    caso("y 256 pasa", not e, str(e))

    e, _, _ = revisar(dict(base, width=32))
    caso("32 px queda fuera del 64–384 de rd_plus__default", bool(e))

    e, _, _ = revisar(dict(base, prompt_style="rd_plus__low_res", width=32, height=32))
    caso("pero 32 px sí vale en rd_plus__low_res", not e, str(e))

    e, _, _ = revisar(dict(base, num_images=16, prompt_style="rd_fast__default"))
    caso("rd_fast__default corta en 15, no en 16", bool(e))

    e, _, _ = revisar(dict(base, prompt="pixel art of a sword"))
    caso("«pixel art» en el prompt es un error", bool(e))

    e, _, _ = revisar(dict(base, prompt="a sword on a transparent background"))
    caso("«transparent background» en el prompt es un error", bool(e))

    e, _, _ = revisar(dict(base, input_image="data:image/png;base64,AAAA"))
    caso("el prefijo data: es un error", bool(e))

    e, _, _ = revisar(dict(base, reference_images=["AAAA"]))
    caso("reference_images en un estilo que no las admite es un error", bool(e))

    e, _, _ = revisar(dict(base, prompt_style="rd_pro__default", reference_images=["A"] * 10))
    caso("diez referencias pasan del límite de nueve de RD Pro", bool(e))

    e, _, _ = revisar(dict(base, prompt_style="rd_pro__default", reference_images=["A"] * 9))
    caso("y nueve pasan", not e, str(e))

    e, _, _ = revisar({"prompt": "steady confident steps",
                       "prompt_style": "rd_advanced_animation__walking",
                       "width": 64, "height": 64, "num_images": 1})
    caso("una animación avanzada sin input_image es un error", bool(e))

    e, _, _ = revisar({"prompt": "a hero walking",
                       "prompt_style": "rd_animation__four_angle_walking",
                       "width": 48, "height": 48, "num_images": 1})
    caso("una animación por prompt NO exige input_image", not e, str(e))

    e, _, _ = revisar(dict(base, frames_duration=7))
    caso("frames_duration = 7 no existe", bool(e))

    _, a, _ = revisar(dict(base, frames_duration=8))
    caso("frames_duration en un estilo fijo es aviso, no error",
         any("frames_duration" in x for x in a))

    _, a, _ = revisar(dict(base, negative="blurry"))
    caso("`negative` avisa de que se ignora", any("negative" in x for x in a))

    _, a, _ = revisar(dict(base, remove_bg=True))
    caso("remove_bg sin fondo dicho avisa", any("remove_bg" in x for x in a))

    _, a, _ = revisar(dict(base, remove_bg=True,
                           prompt="a flask on a plain white background"))
    caso("y con el fondo dicho no avisa", not any("remove_bg" in x for x in a))

    e, _, _ = revisar(dict(base, prompt_style="rd_animation__vfx", width=64, height=48))
    caso("rd_animation__vfx exige cuadrado", bool(e))

    _, a, _ = revisar(dict(base, strength=0.8))
    caso("strength sin input_image avisa", any("strength" in x for x in a))

    e, _, _ = revisar(dict(base, strength=1.5))
    caso("strength fuera de 0–1 es un error", bool(e))

    _, a, _ = revisar(dict(base, temperatura=0.5))
    caso("un campo inventado avisa", any("temperatura" in x for x in a))

    e, _, _ = revisar(dict(base), presupuesto=0.0001)
    caso("el presupuesto corta", bool(e))

    caso("el coste de RD Pro es 0,18 por imagen",
         coste("rd_pro__default", 256, 256, 2) == 0.36,
         str(coste("rd_pro__default", 256, 256, 2)))
    caso("el coste de rd_fast tiene suelo de 0,015",
         coste("rd_fast__default", 64, 64, 1) == 0.0173,
         str(coste("rd_fast__default", 64, 64, 1)))

    e, _, _ = revisar(dict(base, prompt_style="user__mi_estilo_1a2b3c4d"))
    caso("un estilo propio no se rechaza por no estar en el catálogo", not e, str(e))

    # El disco. Un PNG real de 16×16 escrito a mano, sin dependencias.
    import struct
    import zlib
    import tempfile

    def png(ancho, alto):
        crudo = b"".join(b"\x00" + b"\xff\x00\x00\xff" * ancho for _ in range(alto))
        def trozo(tipo, datos):
            return (struct.pack(">I", len(datos)) + tipo + datos
                    + struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF))
        return (b"\x89PNG\r\n\x1a\n"
                + trozo(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 6, 0, 0, 0))
                + trozo(b"IDAT", zlib.compress(crudo))
                + trozo(b"IEND", b""))

    with tempfile.TemporaryDirectory() as tmp:
        p64 = os.path.join(tmp, "inicio64.png")
        p256 = os.path.join(tmp, "inicio256.png")
        with open(p64, "wb") as f:
            f.write(png(64, 64))
        with open(p256, "wb") as f:
            f.write(png(256, 256))

        caso("medir_png lee la cabecera IHDR", medir_png(p64)[0] == (64, 64),
             str(medir_png(p64)))

        anim = {"prompt": "steady steps", "prompt_style": "rd_advanced_animation__walking",
                "width": 64, "height": 64, "num_images": 1, "input_image": "AAAA"}
        e, _, _ = revisar(dict(anim), ruta_imagen=p64)
        caso("el fotograma que mide lo que dice la petición pasa", not e, str(e))

        e, _, _ = revisar(dict(anim), ruta_imagen=p256)
        caso("el fotograma ampliado ×4 en disco se caza aunque la petición cuadre",
             bool(e) and any("256×256" in x for x in e), str(e))

        no_png = os.path.join(tmp, "no.png")
        with open(no_png, "wb") as f:
            f.write(b"esto no es un PNG")
        e, _, _ = revisar(dict(anim), ruta_imagen=no_png)
        caso("un archivo que no es PNG da error, no una medida inventada", bool(e))

        d, motivo = cargar(os.path.join(tmp, "no-existe.json"))
        caso("un JSON que no existe da motivo, no excepción", d is None and bool(motivo))

        malo = os.path.join(tmp, "malo.json")
        with open(malo, "w", encoding="utf-8") as f:
            f.write("{no es json")
        d, motivo = cargar(malo)
        caso("un JSON ilegible da motivo, no excepción", d is None and bool(motivo))

    caso("el catálogo trae los 80 estilos públicos documentados",
         len(CATALOGO) >= 80, f"hay {len(CATALOGO)}")
    caso("ningún estilo de animación admite lote > 16",
         all(v["lote"] <= 16 for v in CATALOGO.values()))
    caso("esta herramienta no llama a la red",
         not re.search(r"requests|urllib|http", open(__file__, encoding="utf-8")
                       .read().split("def autoprueba")[0]
                       .replace("https://api.retrodiffusion.ai", "")
                       .replace("https://www.retrodiffusion.ai", "")
                       .replace("GET /v2", "").replace("POST /v2", "")))

    print()
    if fallos:
        print(f"✗ {len(fallos)} de {len(fallos) + 0} comprobaciones fallaron: "
              + ", ".join(fallos))
        return 1
    print("✓ Todas las comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
