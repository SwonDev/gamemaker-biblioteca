# 12 · Utilidades e integraciones para GameMaker

> Todo lo que **rodea** al motor y te hace ir más rápido: editores alternativos, formateadores,
> analizadores, frameworks de test, importadores de mapas, sincronizadores de Aseprite,
> extensiones nativas, integraciones con Steam/Discord/Twitch, multijugador y tiendas de assets.
>
> Investigado y verificado el **1 de septiembre de 2026**. Cuando existe el repositorio, está
> **descargado** en [`11 - Código descargado`](../11%20-%20C%C3%B3digo%20descargado/_CATALOGO.md).

---

## Los documentos de esta carpeta

| # | Documento | Qué cubre |
|---|---|---|
| 01 | [Herramientas del flujo de trabajo](./01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md) | Editores, formateadores, analizadores, CLI, tests, documentación, temas del IDE |
| 02 | [Extensiones nativas y del sistema](./02%20-%20Extensiones%20nativas%20y%20del%20sistema.md) | Ventana, ratón, ficheros fuera del sandbox, cámara, MIDI, Lua, WebAssembly |
| 03 | [Integraciones con servicios](./03%20-%20Integraciones%20con%20servicios.md) | Steam, Discord, Twitch, GOG, Epic, Firebase, anuncios, compras, GitHub |
| 04 | [Multijugador y red](./04%20-%20Multijugador%20y%20red.md) | Photon, Colyseus, Warp, rollback, HTTP, WebSockets |
| 05 | [Pipeline de arte, audio y niveles](./05%20-%20Pipeline%20de%20arte%2C%20audio%20y%20niveles.md) | Aseprite, Tiled, LDtk, Blender, FMOD, Spine, texture packing |
| 06 | [itch.io — assets, herramientas y jams](./06%20-%20itch.io%20-%20assets%2C%20herramientas%20y%20jams.md) | Qué hay realmente en itch.io para GameMaker, con precios |
| 07 | [Dónde buscar: hubs, foros y documentación](./07%20-%20D%C3%B3nde%20buscar%20-%20hubs%20y%20documentaci%C3%B3n.md) | awesome-gamemaker, GameMaker Kitchen, Marketplace, foros, gm(48) |
| 08 | [Tooling externo: CLI, parsers e ingeniería inversa](./08%20-%20Tooling%20externo%20-%20CLI%2C%20parsers%20e%20ingenier%C3%ADa%20inversa.md) | Ecosistema npm/PyPI: Stitch (@bscotch), @bscotch/yy, gml-parser, TS→GML, gml-linter, MCP, UndertaleModTool para estudiar juegos compilados |

---

## Regla de oro antes de instalar nada

**Comprueba si el motor ya lo hace.** GameMaker LTS 2026 incorporó cosas que antes requerían
extensión: buses y efectos de audio, sistema de partículas nuevo, UI Layers y Flexpanels,
Package Manager, filtros y efectos de capa. Antes de añadir una dependencia:

```sh
python3 "_indice/buscar.py" --listar audio_bus
python3 "_indice/buscar.py" --listar flexpanel_
python3 "_indice/buscar.py" --listar layer_
```

Y lee [`02 - Novedades 2026`](../02%20-%20Novedades%202026/). Media docena de extensiones
populares de 2022 hoy sobran.

---

## Las cinco que instalarías primero

Si tuvieras que elegir solo cinco, en este orden:

| # | Qué | Por qué | Coste |
|---|---|---|---|
| 1 | **[Input](https://codeberg.org/offalynne/Input)** (librería) | Teclado, ratón, gamepad, remapeo, multijugador local y buffers. Resuelto de una vez. ⚠️ Vive en **Codeberg**: el repo de GitHub está archivado | gratis (MIT) |
| 2 | **[Scribble](https://github.com/JujuAdams/Scribble)** (librería) | Texto con formato, efectos y ajuste de línea | gratis (MIT) |
| 3 | **[Gobo](https://github.com/Pizzaandy/Gobo)** o **[duck](https://github.com/imlazyeye/duck)** | Formateador y analizador de GML: código consistente sin discutir estilo | gratis |
| 4 | **[GMEdit](https://github.com/YellowAfterlife/GMEdit)** | Editor de código externo con autocompletado y navegación muy superiores | gratis (MIT) |
| 5 | **[GMLive](https://yellowafterlife.itch.io/gamemaker-live)** | Recarga de código **sin recompilar**. Es la mayor ganancia de productividad que existe | 💸 $29,95 |

Las cuatro primeras están descargadas en [`11 - Código descargado`](../11%20-%20C%C3%B3digo%20descargado/_CATALOGO.md).

---

## Cómo se ha verificado

- **GitHub:** metadatos reales por API (`gh api repos/<slug>`) — estrellas, licencia, fecha
  del último *push*, si está archivado. Nada se ha copiado de una lista sin comprobar.
- **itch.io:** listados extraídos y parseados de las páginas de etiquetas
  (`itch.io/tools/tag-gamemaker`, `itch.io/game-assets/tag-extension/tag-gamemaker`), con
  autor y precio reales.
- **Webs:** petición HTTP directa; `sitemap.xml` cuando existía, para datar la última
  actualización real.
- Lo que no se ha podido verificar aparece marcado con ⚠️.
