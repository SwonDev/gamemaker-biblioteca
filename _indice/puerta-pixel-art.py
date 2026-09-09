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


if __name__ == "__main__":
    sys.exit(main())
