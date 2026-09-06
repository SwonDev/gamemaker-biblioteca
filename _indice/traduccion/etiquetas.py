#!/usr/bin/env python3
"""Traduce en el espejo español las etiquetas de enlace y las cabeceras de tabla que
YoYo Games dejó en inglés (nombres de grupos de constantes, sobre todo).

No toca las rutas de los enlaces ni los identificadores de GML: solo el texto visible.

    python3 etiquetas.py estado    · cuántas quedan
    python3 etiquetas.py aplicar   · las sustituye
"""
import os, re, sys, collections

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
ES = os.path.join(RAIZ, "09 - Manual oficial", "manual-lts-2026-es")

# etiqueta inglesa → etiqueta española (solo el texto visible del enlace o de la celda)
ETIQUETAS = {
    "Mouse Button Constant": "Constante de botón de ratón",
    "Socket Type Constant": "Constante de tipo de socket",
    "Virtual Key Constant (vk_*)": "Constante de tecla virtual (vk_*)",
    "File Attribute Constant": "Constante de atributo de archivo",
    "OS Type Constant": "Constante de tipo de sistema operativo",
    "Device Type Constant": "Constante de tipo de dispositivo",
    "Permission State Constant": "Constante de estado de permiso",
    "Browser Type Constant": "Constante de tipo de navegador",
    "External Data Type Constant": "Constante de tipo de dato externo",
    "Exteriores Data Type Constantes": "Constantes de tipo de dato externo",
    "Buffer Data Type Constant": "Constante de tipo de dato de búfer",
    "Buffer Seek Constant": "Constante de búsqueda en búfer",
    "Buffer Type Constant": "Constante de tipo de búfer",
    "Mipmapping Filter Constant": "Constante de filtro de mipmapping",
    "Mipmapping Constant": "Constante de mipmapping",
    "Particle Emitter Shape Constant": "Constante de forma de emisor de partículas",
    "Particle Emitter Distribution Constant": "Constante de distribución de emisor de partículas",
    "Particle Shape Constant": "Constante de forma de partícula",
    "Blend Mode Factor Constant": "Constante de factor de modo de mezcla",
    "Blend Mode Constant": "Constante de modo de mezcla",
    "Culling Mode Constant": "Constante de modo de descarte de caras",
    "Comparison Function Constant": "Constante de función de comparación",
    "Primitive Type Constant": "Constante de tipo de primitiva",
    "Vertex Data Type Constant": "Constante de tipo de dato de vértice",
    "Vertex Usage Type Constant": "Constante de tipo de uso de vértice",
    "Video Status Constant": "Constante de estado de vídeo",
    "Video Format Constant": "Constante de formato de vídeo",
    "Light Type Constant": "Constante de tipo de luz",
    "Vertical Alignment Constant": "Constante de alineación vertical",
    "Horizontal Alignment Constant": "Constante de alineación horizontal",
    "DS Type Constant": "Constante de tipo de estructura DS",
    "Network Send Type Constant": "Constante de tipo de envío de red",
    "Matrix Type Constant": "Constante de tipo de matriz",
    "Time Zone Constant": "Constante de zona horaria",
    "UWP Privilege Constant": "Constante de privilegio UWP",
    "Xbox File Error Constant": "Constante de error de archivo de Xbox",
    "Xbox Age Group Constant": "Constante de grupo de edad de Xbox",
    "Xbox Match Visibility Constant": "Constante de visibilidad de partida de Xbox",
    "Xbox Live Achievement Filter Constant": "Constante de filtro de logros de Xbox Live",
    "Sprite Speed Constant": "Constante de velocidad de sprite",
    "Bounding Box Kind (Shape) Constant": "Constante de tipo (forma) de caja de colisión",
    "Tile Mode Constant": "Constante de modo de mosaico",
    "Gamepad Axis Constant": "Constante de eje de mando",
    "Gamepad Button Constant": "Constante de botón de mando",
    "Texture Group Status Constant": "Constante de estado de grupo de texturas",
    "Flex Panel Layout Direction Constant": "Constante de dirección de disposición de Flex Panel",
    "Particle Emitter Mode Constant": "Constante de modo de emisor de partículas",
    "Audio Falloff Model Constant": "Constante de modelo de atenuación de audio",
    "Cursor Constant": "Constante de cursor",
    "Path End Action Constant": "Constante de acción al final de la ruta",
    "Effect Type Constant": "Constante de tipo de efecto",
    "Event Constant": "Constante de evento",
    "Game Speed Constant": "Constante de velocidad del juego",
    "Timing Method Constant": "Constante de método de temporización",
}

# cabeceras de tabla completas (fila entera) → su versión española
CABECERAS = {
    "| Constant | Description |": "| Constante | Descripción |",
    "| Constant | Meaning |": "| Constante | Significado |",
    "| Argument | Type | Description |": "| Argumento | Tipo | Descripción |",
    "| Value | Description |": "| Valor | Descripción |",
    "| Name | Description |": "| Nombre | Descripción |",
    "| Property | Description |": "| Propiedad | Descripción |",
    "| Key | Description |": "| Clave | Descripción |",
    "| Function | Description |": "| Función | Descripción |",
    "| Returns: |": "| Devuelve: |",
}


def paginas():
    for root, _, files in os.walk(ES):
        for f in sorted(files):
            if f.endswith(".md"):
                p = os.path.join(root, f)
                yield p, open(p, encoding="utf-8").read()


def sustituir(txt: str) -> str:
    for en, es in CABECERAS.items():
        txt = txt.replace(en + "\n", es + "\n")
    for en, es in ETIQUETAS.items():
        # etiqueta de enlace: [Etiqueta](ruta)
        txt = txt.replace("[" + en + "](", "[" + es + "](")
        # celda de tabla suelta: | Etiqueta |
        txt = txt.replace("| " + en + " |", "| " + es + " |")
    return txt


def cmd_estado():
    n = collections.Counter()
    for _, txt in paginas():
        for en in CABECERAS:
            n[en] += txt.count(en + "\n")
        for en in ETIQUETAS:
            n[en] += txt.count("[" + en + "](") + txt.count("| " + en + " |")
    quedan = {k: v for k, v in n.items() if v}
    print(f"etiquetas y cabeceras en inglés pendientes: {len(quedan)} · apariciones: {sum(quedan.values())}")
    for k, v in sorted(quedan.items(), key=lambda x: -x[1])[:15]:
        print(f"  x{v:4d}  {k}")


def cmd_aplicar():
    tocadas = 0
    for p, txt in paginas():
        nuevo = sustituir(txt)
        if nuevo != txt:
            open(p, "w", encoding="utf-8").write(nuevo)
            tocadas += 1
    print(f"{tocadas} páginas actualizadas")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "estado"
    {"estado": cmd_estado, "aplicar": cmd_aplicar}[cmd]()
