#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saca las funciones GML de un documento y las deja en un .gml compilable.

Existe para que el código de una receta se pueda EJECUTAR sin copiarlo a otro
sitio. Copiarlo tendría el fallo de siempre: las dos copias se separan y la
prueba acaba comprobando una versión que ya nadie lee. Aquí el código bajo
prueba **es** el del documento, extraído en cada ejecución.

Solo se llevan los bloques ```gml que declaran `function`: el resto de bloques
de una receta son fragmentos de evento (`obj_x · Step`) que no compilan sueltos.

    python3 _indice/pruebas/extraer_funciones.py <documento.md> <salida.gml>
"""
import io
import os
import re
import sys

BLOQUE = re.compile(r"```gml\n(.*?)```", re.S)


def main():
    if len(sys.argv) < 3:
        print(__doc__.strip())
        return 2
    doc, salida = sys.argv[1], sys.argv[2]
    if not os.path.isfile(doc):
        print("✗ No existe el documento: %s" % doc)
        return 2

    texto = io.open(doc, encoding="utf-8").read()
    trozos = [b for b in BLOQUE.findall(texto) if re.search(r"^\s*function\s+\w+", b, re.M)]
    if not trozos:
        # Cero bloques no es «está todo bien»: es que no se ha extraído nada, y
        # una prueba montada sobre un archivo vacío pasa siempre.
        print("✗ %s no tiene ni un bloque ```gml con `function`." % os.path.basename(doc))
        return 2

    with io.open(salida, "w", encoding="utf-8") as f:
        f.write("// GENERADO por extraer_funciones.py desde:\n//   %s\n"
                "// No lo edites: se regenera en cada `validar-ejecucion.sh`.\n\n"
                % os.path.relpath(doc, os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__))))))
        for t in trozos:
            f.write(t.rstrip() + "\n\n")

    n = sum(len(re.findall(r"^\s*function\s+(\w+)", t, re.M)) for t in trozos)
    print("%d función(es) de %d bloque(s) → %s"
          % (n, len(trozos), os.path.basename(salida)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
