#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La puerta que va DELANTE de reparar un PNG de pixel art.

`12 · 09 §5.2` peldaño 2 bis decía, en negrita: «nada que salga de un generador
entra en el juego sin pasar por aquí». Un sprite dibujado con Pillow sale de un
generador, así que la regla, obedecida al pie de la letra, lo pasa por
`pixel-art-fixer` — y lo destruye. Medido sobre arte real de 16×20 px dibujado a
1:1: `detect()` lo declaró una imagen de 6×7 ampliada ×2,5, y `pixeldetector` lo
redujo a 4×10. Las dos herramientas hacen bien su trabajo (buscar la rejilla
oculta de una imagen ampliada); lo que faltaba era distinguir los dos casos.
Caso completo en `_indice/auditorias/r15-prueba-puzles.md` §2.1.

Esta puerta decide, sin heurística blanda:

  1. **Escala real.** El mayor `k` tal que reducir por `k` y volver a ampliar
     reproduce la imagen EXACTA. `k == 1` significa que ya es pixel art de
     verdad: no hay rejilla que reconstruir.
  2. **Paleta.** Un PNG salido de un modelo trae cientos de colores; uno dibujado
     con paleta fija, decenas.
  3. **Halo.** Proporción de píxeles con alfa intermedio (0 < a < 255). Un
     generador deja un borde emborronado; un pincel de pixel art, no.

Y exige la **conjunción**, no la disyunción, porque cada síntoma por separado
tiene causas legítimas: una sombra es alfa parcial a propósito (81 % medido), y
una puerta de bloques grandes puede ser por casualidad un aumento exacto ×2. Con
la disyunción, esos dos ficheros reales se habrían triturado.

Uso:
    python3 _indice/puerta-pixel-art.py <carpeta o PNG> [más rutas…]

Sale con 0 si no hay nada que reparar, 1 si algún PNG pide reparación, y 2 si no
se pudo mirar (falta Pillow, no hay PNG en la ruta…). Solo diagnostica: no toca
ni un archivo.
"""
import os
import sys

# Windows: en cuanto la salida no es una consola interactiva (pipes, «> archivo», o el
# propio actualizar.py capturando la salida vía subprocess), sys.stdout usa la página de
# códigos ANSI del sistema en vez de UTF-8 — y los ✓/✗/⚠ de este código no caben ahí.
#
# **Medido, ya no supuesto** (2026-09-09, Python 3.12.7 de Windows bajo Wine 11):
#     UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
# La autoprueba reventaba en la primera línea que imprimía un ✓. Las herramientas que ya
# llevaban estas seis líneas pasaron; las que no, murieron.
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


UMBRAL_COLORES = 64      # por encima de esto ya no es una paleta, es un degradado
UMBRAL_ALFA_PCT = 12.0   # halo de alfa intermedio propio de un generador


def _pillow():
    try:
        from PIL import Image
        return Image
    except ImportError:
        print("✗ Falta Pillow, así que NO se ha mirado ningún PNG.")
        print("  Esto no significa que el arte esté bien: significa que no se ha comprobado.")
        print("  Instálalo con:  python3 -m pip install --user Pillow")
        return None


def escala_real(im, Image):
    """Mayor k >= 1 tal que la imagen es un aumento exacto ×k, por vecino más próximo."""
    w, h = im.size
    mejor = 1
    for k in range(2, min(w, h) + 1):
        if w % k or h % k:
            continue
        reducida = im.resize((w // k, h // k), Image.NEAREST)
        if reducida.resize((w, h), Image.NEAREST).tobytes() == im.tobytes():
            mejor = k
    return mejor


def diagnosticar(ruta, Image):
    im = Image.open(ruta).convert("RGBA")
    w, h = im.size
    # `tobytes()` en vez de `getdata()`: getdata está deprecado desde Pillow 12
    # y desaparece en la 14, y esto además es más rápido.
    crudo = im.tobytes()
    pixeles = [crudo[i:i + 4] for i in range(0, len(crudo), 4)]
    colores = len(set(pixeles))
    parcial = sum(1 for p in pixeles if 0 < p[3] < 255)
    return {
        "ruta": ruta,
        "ancho": w,
        "alto": h,
        "escala": escala_real(im, Image),
        "colores": colores,
        "alfa_pct": round(100.0 * parcial / max(1, len(pixeles)), 2),
    }


def motivos_para_reparar(d):
    """Los tres síntomas, exigiendo la firma COMPLETA de un PNG generado."""
    motivos = []
    paleta_rota = d["colores"] > UMBRAL_COLORES
    if d["escala"] > 1 and paleta_rota:
        motivos.append("ampliado ×%d con %d colores" % (d["escala"], d["colores"]))
    if paleta_rota and d["alfa_pct"] > UMBRAL_ALFA_PCT:
        motivos.append("%d colores y %.1f %% de alfa intermedio" % (d["colores"], d["alfa_pct"]))
    return motivos


def reunir_pngs(rutas):
    encontrados = []
    for r in rutas:
        if os.path.isdir(r):
            for raiz, _dirs, files in os.walk(r):
                for f in sorted(files):
                    if f.lower().endswith(".png"):
                        encontrados.append(os.path.join(raiz, f))
        elif r.lower().endswith(".png") and os.path.isfile(r):
            encontrados.append(r)
    return encontrados


def main():
    rutas = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not rutas or "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__.strip())
        return 0 if ("--help" in sys.argv or "-h" in sys.argv) else 2

    Image = _pillow()
    if Image is None:
        return 2

    pngs = reunir_pngs(rutas)
    if not pngs:
        print("✗ No hay ningún .png en: %s" % ", ".join(rutas))
        print("  No es «todo correcto»: es que no se ha mirado nada.")
        return 2

    sospechosos = []
    ampliados_limpios = []      # ×k exacto pero con la paleta intacta: informativo
    a_escala_1 = 0
    colores_max = 0
    alfa_max = 0.0
    for p in pngs:
        try:
            d = diagnosticar(p, Image)
        except Exception as e:                      # un PNG ilegible es un problema, no un cero
            print("✗ No se pudo leer %s: %s" % (p, e))
            return 2
        a_escala_1 += (d["escala"] == 1)
        colores_max = max(colores_max, d["colores"])
        alfa_max = max(alfa_max, d["alfa_pct"])
        motivos = motivos_para_reparar(d)
        if motivos:
            sospechosos.append((d, motivos))
        elif d["escala"] > 1:
            ampliados_limpios.append(d)

    print("Puerta del peldaño 2 bis · %d PNG analizados" % len(pngs))
    print("  a escala real 1:1 ............ %d / %d" % (a_escala_1, len(pngs)))
    print("  máximo de colores por PNG .... %d" % colores_max)
    print("  máximo de alfa intermedio .... %.2f %%" % alfa_max)
    print("  piden reparación ............. %d" % len(sospechosos))

    for d, motivos in sospechosos:
        print("   ! %-40s %s" % (os.path.basename(d["ruta"]), ", ".join(motivos)))

    if ampliados_limpios:
        # Ni se reparan ni se callan: son un aumento EXACTO con la paleta intacta,
        # así que reducirlos no perdería un solo píxel… pero cambiaría el tamaño del
        # sprite, y eso es una decisión de diseño, no de limpieza. Que se vea.
        print("\n  (informativo) %d PNG son un aumento exacto con la paleta intacta."
              % len(ampliados_limpios))
        print("  No se tocan: reducirlos es reversible, pero cambia el tamaño del sprite")
        print("  y eso lo decide quien hace el juego, no esta puerta.")
        for d in ampliados_limpios[:10]:
            print("   · %-40s ×%d, %d colores"
                  % (os.path.basename(d["ruta"]), d["escala"], d["colores"]))

    if sospechosos:
        print("\nA ESOS —y solo a esos— pásales `pixel-art-fixer` o `pixeldetector`.")
        print("Al resto NO: ya están a 1:1 y la reconstrucción de rejilla los destruiría.")
        return 1

    print("\nNada que reparar: el arte ya está a su resolución real y con paleta cerrada.")
    print("La reconstrucción de rejilla del peldaño 2 bis no tiene aquí trabajo que hacer.")
    return 0


def autoprueba():
    """Las dos direcciones, que es lo único que hace útil a una puerta.

    Una puerta que nunca deja pasar nada es tan inútil como una que deja pasar
    todo: la primera manda reparar arte que está bien —y `pixel-art-fixer` lo
    destruye—, la segunda deja entrar en el juego un PNG emborronado. Aquí se
    fabrican los dos casos y se comprueban los dos.
    """
    import tempfile, random
    Image = _pillow()
    if Image is None:
        return 2

    fallos = []

    def revisar(nombre, condicion, detalle=""):
        if condicion:
            print("  ✓ " + nombre)
        else:
            fallos.append(nombre)
            print("  ✗ %s  ->  %s" % (nombre, detalle))

    with tempfile.TemporaryDirectory() as tmp:
        random.seed(7)
        paleta = [(20, 20, 40, 255), (200, 60, 60, 255), (240, 220, 180, 255), (0, 0, 0, 0)]
        original = Image.new("RGBA", (16, 16))
        original.putdata([random.choice(paleta) for _ in range(256)])

        p_1a1 = os.path.join(tmp, "dibujado_1a1.png")
        original.save(p_1a1)
        p_nitido = os.path.join(tmp, "ampliado_nitido.png")
        original.resize((64, 64), Image.NEAREST).save(p_nitido)
        p_borroso = os.path.join(tmp, "ampliado_borroso.png")
        original.resize((64, 64), Image.BICUBIC).save(p_borroso)

        d1 = diagnosticar(p_1a1, Image)
        revisar("el arte dibujado a 1:1 mide escala 1", d1["escala"] == 1, d1["escala"])
        revisar("y no pide reparación", motivos_para_reparar(d1) == [], motivos_para_reparar(d1))

        d2 = diagnosticar(p_nitido, Image)
        revisar("un aumento exacto ×4 se detecta como escala 4", d2["escala"] == 4, d2["escala"])
        revisar("pero con la paleta intacta NO se repara (reducir cambia el tamaño del sprite)",
                motivos_para_reparar(d2) == [], motivos_para_reparar(d2))

        d3 = diagnosticar(p_borroso, Image)
        revisar("un aumento con interpolación suave rompe la paleta",
                d3["colores"] > UMBRAL_COLORES, d3["colores"])
        revisar("y SÍ pide reparación", motivos_para_reparar(d3) != [], motivos_para_reparar(d3))

        # Una sombra: alfa parcial a propósito, paleta pequeña. NO puede repararse:
        # con la disyunción en vez de la conjunción, este archivo real se destruía.
        sombra = Image.new("RGBA", (16, 16), (0, 0, 0, 90))
        p_sombra = os.path.join(tmp, "sombra.png")
        sombra.save(p_sombra)
        d4 = diagnosticar(p_sombra, Image)
        revisar("una sombra es 100 % alfa intermedio…", d4["alfa_pct"] > UMBRAL_ALFA_PCT,
                d4["alfa_pct"])
        revisar("…y aun así NO se repara, porque la paleta está sana",
                motivos_para_reparar(d4) == [], motivos_para_reparar(d4))

    if fallos:
        print("\n✗ %d comprobación(es) de la autoprueba fallan." % len(fallos))
        return 1
    print("\n✓ Las 8 comprobaciones de la autoprueba pasan.")
    return 0


if __name__ == "__main__":
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    sys.exit(main())
