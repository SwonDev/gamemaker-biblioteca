# 05 · Pipeline de arte, audio y niveles

> Cómo conectar GameMaker con las herramientas donde de verdad haces el arte, el audio y los
> mapas: **Aseprite, Tiled, LDtk, Blender, FMOD, Spine**. El objetivo es no volver a importar
> sprites a mano.
>
> Verificado el 1 de septiembre de 2026.

---

## 1. Aseprite → GameMaker (sprites)

**Aseprite** es el editor de pixel art estándar. El problema clásico: cada cambio obliga a
reexportar y reimportar a mano. Estas herramientas lo automatizan.

| Herramienta | Qué hace | Dónde |
|---|---|---|
| **AseSync** | Sincroniza ficheros `.aseprite` con GameMaker automáticamente | YellowAfterlife |
| **AseSync GUI** | Interfaz gráfica para el CLI de AseSync | [GameMaker Kitchen](https://www.gamemakerkitchen.com/tools) · Sohom Sahaun |
| [**conveyorbelt**](https://github.com/imissmyfriends/conveyorbelt) ★7 | Exporta ficheros de Aseprite e importa como sprites automáticamente | 📁 `librerias/sprites-y-animacion/conveyorbelt` |
| **GM Link** | Sincroniza sprites de Aseprite a GameMaker con un clic, sin programas extra | itch.io |
| [**GM-Sprite-Importer**](https://www.gamemakerkitchen.com/tools) | Importación automatizada de colecciones grandes de imágenes (Python) | GameMaker Kitchen · emperor2020 |

> 💡 **Flujo recomendado:** guarda los `.aseprite` **fuera** de la carpeta del proyecto, en un
> `arte/` propio, y deja que la herramienta exporte a `datafiles/` o directamente al asset.
> Así el `.yyp` no se llena de rutas absolutas y Git no se atraganta.

### Herramientas de sprites dentro de GameMaker

| Librería | ★ | Qué hace | Ruta |
|---|---:|---|---|
| [**AESnips**](https://github.com/angelwire/AESnips) | 9 | Sistema de reproducción de sprites (recortes, secuencias) | `librerias/sprites-y-animacion/AESnips` |
| [**Collage**](https://github.com/tabularelf/Collage) | 29 | Atlas de texturas y sprites generados en tiempo de ejecución | `librerias/sprites-y-animacion/Collage` |
| [**Texer**](https://www.gamemakerkitchen.com/libraries) | — | Empaquetado de texturas en tiempo de ejecución | GameMaker Kitchen |
| [**GM-Animate**](https://github.com/KormexGit/GM-Animate) | 10 | Sistema de animación | `librerias/sprites-y-animacion/GM-Animate` |
| [**Chameleon**](https://github.com/Lojemiru/Chameleon) | 16 | **Intercambio de paletas** rápido y libre | `librerias/sprites-y-animacion/Chameleon` |
| [**Sprite Sheet Functions**](https://ghostwolf-games.itch.io/sprite-sheet-functions) 💸 $4,99 | — | Manipulación de hojas de sprites | itch.io |

---

## 2. Editores de mapas → GameMaker (niveles)

GameMaker trae su propio editor de rooms con tile sets y autotiles
([`08 - Referencia GML/09`](../08%20-%20Referencia%20GML%20completa/09%20-%20Dibujo%20de%20tiles%20y%20tilemaps.md)),
pero si vienes de otra herramienta o quieres un flujo por datos:

### LDtk (el más recomendable hoy)

| Herramienta | ★ | Qué hace |
|---|---:|---|
| [**LDtkParser**](https://github.com/evolutionleo/LDtkParser) | 63 | Importador avanzado de niveles `.ldtk`. MIT, último *push* 2025-08-14 |
| [**LDtk to GMS**](https://shynif.itch.io/ldtk-to-gms) | — | Importador alternativo (itch.io) |

📁 `librerias/niveles-y-mapas/LDtkParser`

**Qué resuelve.** [LDtk](https://ldtk.io) (deepnight, ★4 174 en GitHub, sin cambios desde
2026-07-12: **vivo**, verificado en vivo el 07-09-2026) es un editor de niveles gratuito y
multiplataforma, pensado como sustituto moderno de Tiled: capas por tipo (IntGrid, Tiles,
Entidades), autotiling por reglas, campos personalizados tipados en las entidades y un formato
`.ldtk` en JSON legible. GameMaker no lo lee de forma nativa —a diferencia de Tiled, que sí tiene
exportador oficial ([`07 · 09` §4](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gráficos.md#4-tilemaps-tiled-y-cómo-exportar-a-gamemaker))—;
**LDtkParser** es el puente: un `.yymps` que se importa como Local Package y da un objeto `oLDtk`
capaz de cargar un nivel `.ldtk` entero —capas, entidades con sus campos, enums— con una sola
llamada, en vez de escribir tu propio parser de JSON.

**Cómo se conecta a un proyecto GameMaker**, según su propio README (verificado el 07-09-2026):

1. **Instalar**: descargar el `.yymps` de la
   [última *release*](https://github.com/evolutionleo/LDtkParser/releases/latest) e importarlo
   con *Tools → Import Local Package* (mismo mecanismo que cualquier Local Package, ver
   [`13 · 06` §3.15](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/06%20-%20Arquitectura%20de%20un%20proyecto%20GameMaker.md#315-escalar-módulos-y-local-packages)
   — **no** se edita el `.yyp` a mano, el propio flujo de Local Packages es lo que evita eso).
2. **Configurar**: colocar una instancia de `oLDtk` en la room que cargue el nivel (o en el
   controlador persistente) y llamar a `LDtkConfig()` con los ajustes propios —o editar los
   valores por defecto directamente en `oLDtk`— para mapear los nombres de capas/entidades/campos
   del `.ldtk` a sus equivalentes en el proyecto, cuando no coinciden literalmente.
3. **Entidades con campos tipados**: si algún objeto usa *Field Definitions* de LDtk, hay que
   activar la opción `escape_fields` de la configuración y llamar a `LDtkReloadFields()` en el
   Create Event de esos objetos, para que los valores lleguen ya convertidos al tipo de GML que
   corresponde (no como texto suelto).
4. **Cargar el nivel**: una única llamada de función (propia de la librería, documentada en el
   README del `.yymps`) trae la room entera —tiles, autotiles, entidades posicionadas y sus
   campos— sin escribir un `json_parse` manual.

**Recarga en vivo (*live updating*), la pieza que el catálogo no explicaba**: LDtkParser puede
recargar el nivel **mientras el juego está corriendo**, cada vez que guardas en el propio editor
de LDtk — útil para iterar un nivel sin reiniciar el juego una y otra vez. Tres pasos, literales
del README:

1. Marca **«Disable file system sandbox»** en las Game Options de la plataforma de escritorio
   (la misma opción que abre el `working_directory` a lectura fuera del bundle — ver
   [`01 · 14` §1](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#1-el-sandbox-lo-primero-que-debes-entender)).
2. Activa el macro `LDTK_LIVE` de la librería.
3. Apunta la ruta de la configuración de recarga en vivo al `.ldtk` **dentro de la carpeta del
   proyecto** (no a una copia importada), para que los cambios en LDtk se reflejen en el
   siguiente fotograma.

⚠️ **Solo tiene sentido en desarrollo, nunca en la build que se publica**: el sandbox
desactivado y una ruta absoluta al proyecto fuente no deben viajar en el ejecutable final —
el mismo criterio de «apaga esto en Release» que ya usan el modo QA y la consola de comandos
([`13 · 10` §7.4 y §7.5](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#75-una-consola-de-comandos-en-runtime)).

⚠️ **Sin cambios desde agosto de 2025** (más de un año a fecha de esta verificación): sigue sin
estar archivado y el enlace de Discord del propio README sigue activo, así que no hay señal de
abandono, pero comprueba issues abiertos antes de depender de él en un proyecto nuevo.

### Tiled

**GMTiled** convierte mapas de **Tiled** a rooms de GMS2.
⚠️ No se ha encontrado un repositorio mantenido en 2026; verifica su estado antes de adoptarlo.
Tiled sigue muy vivo (<https://github.com/mapeditor/tiled>, ★12 860, 2026-08-27), pero la
integración con GameMaker está menos cuidada que la de LDtk.

### Ogmo Editor: no compensa frente a Tiled y LDtk

**Ogmo Editor 3** (Community Edition, <https://github.com/Ogmo-Editor-3/OgmoEditor3-CE>, MIT,
escrito en Haxe; el repositorio no recibe commits desde mediados de 2024 pero sigue siendo la
versión de referencia y se descarga y usa sin problema) es un editor de niveles genérico y
ligero: exporta cada nivel a JSON con capas de tiles, decoraciones y **entidades** con campos
tipados — el mismo espíritu que Tiled y LDtk, sin atarse a ningún motor concreto.

⚠️ **No se ha encontrado ningún importador mantenido para GameMaker en 2026**, ni siquiera al
nivel de "abandonado pero existe" como `GMTiled` arriba. Una búsqueda de código y de repositorios
en GitHub por proyectos que combinen Ogmo con GML no devuelve nada: los parsers de niveles Ogmo
que sí existen son para LÖVE2D, MonoGame, Rust, Kotlin y Haxe — ninguno para GameMaker. El propio
repositorio de Ogmo Editor 3 tampoco menciona GameMaker entre los motores con soporte. El formato
es JSON plano y está bien documentado, así que escribir un importador propio es viable — pero hoy
es trabajo desde cero, no una integración que instalar.

**Para un proyecto GameMaker en 2026, usa LDtk.** Tiene un importador con licencia MIT activo
(arriba) y un editor más completo que Ogmo: auto-tiling, capas IntGrid, reglas de generación. Ogmo
solo compensa si ya tienes niveles Ogmo de otro proyecto que migrar, o si su modelo de "entidades
con campos tipados" encaja mejor con tu flujo que las capas de entidades de LDtk — y en ese caso,
cuenta con escribir el importador tú mismo.

### Dentro del propio motor

| Librería | ★ | Qué hace | Ruta |
|---|---:|---|---|
| [**GMRoomLoader**](https://github.com/GlebTsereteli/GMRoomLoader) | 128 | **Carga rooms como prefabs en tiempo de ejecución**, en cualquier posición. La base para generación procedural con piezas dibujadas a mano | `librerias/niveles-y-mapas/GMRoomLoader` |
| [**Hotglue**](https://github.com/JujuAdams/Hotglue) | 8 | Editor de niveles **dentro del propio juego** | `librerias/niveles-y-mapas/Hotglue` |
| [**GM-RoomInspector**](https://github.com/heygleeson/GM-RoomInspector) | 10 | Vuelca los datos de una room a JSON | `librerias/niveles-y-mapas/GM-RoomInspector` |

### Generación procedural

| Recurso | ★ | Qué hace | Ruta |
|---|---:|---|---|
| [**random-level-gen-gms2**](https://github.com/GameMakerDiscord/random-level-gen-gms2) | 57 | Generación tipo **Nuclear Throne** | `librerias/niveles-y-mapas/random-level-gen-gms2` |
| [**Random Dungeon Generator**](https://github.com/BlaXun/Random-Dungeon-Generator-GMS-2.3) | 10 | Combina cámaras definidas por el usuario para formar mazmorras | `librerias/niveles-y-mapas/Random-Dungeon-Generator-GMS-2.3` |
| [**destructible-terrain**](https://github.com/niksudan/gms2-destructible-terrain) | 31 | Terreno **destructible** con superficies y rejillas | `librerias/niveles-y-mapas/gms2-destructible-terrain` |
| [Wave Function Collapse](https://quadolorgames.itch.io/wfc-gml-demo) | — | Demo de WFC (⚠️ no listo para producción, según el autor) |
| [Cellular Automata Caves](https://alessiogamedev.itch.io/gms-cellular-automata-algorithm) | — | Cuevas enormes en pocos cientos de milisegundos |

📖 Marco conceptual en [`04 - Recetas por género/05 · Roguelike y generación procedural`](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md).

---

## 3. Blender y 3D

| Herramienta | ★ | Qué hace | Ruta |
|---|---:|---|---|
| [**BBMOD**](https://github.com/blueburncz/BBMOD) | 119 | **El motor 3D de referencia**: modelos, animación esqueletal, materiales PBR, terreno, niebla y sombras | `librerias/3d/BBMOD` |
| [**BBMOD-Blender**](https://github.com/blueburncz/BBMOD-Blender) | 2 | Complemento de Blender para exportar al formato de BBMOD | `librerias/3d/BBMOD-Blender` |
| [**DmrVBM-blender-to-gms2**](https://github.com/Sandman13sq/DmrVBM-blender-to-gms2) | 43 | **Vertex buffers desde Blender** a GameMaker | `librerias/3d/DmrVBM-blender-to-gms2` |
| [**dotobj**](https://github.com/JujuAdams/dotobj) | 47 | Cargador de `.obj`/`.mtl` escrito en GML puro | `librerias/3d/dotobj` |
| [**Cardboard**](https://github.com/JujuAdams/Cardboard) | 3 | Geometría 3D sencilla sobre el pipeline 2D | `librerias/3d/Cardboard` |
| [**GM3D-Samples**](https://github.com/YoYoGames/GM3D-Samples) (oficial) | 13 | Ejemplos 3D oficiales | `plantillas_y_ejemplos/GM3D-Samples` |
| [**3D-2D**](https://github.com/YoYoGames/3D-2D) (oficial) | 48 | Mezcla de 3D y 2D | `plantillas_y_ejemplos/3D-2D` |

📖 Fundamento en [`08 - Referencia GML/07 · Vertex buffers y formatos`](../08%20-%20Referencia%20GML%20completa/07%20-%20Vertex%20buffers%20y%20formatos.md)
y [`11 · Vectores, matrices y ángulos`](../08%20-%20Referencia%20GML%20completa/11%20-%20Vectores%2C%20matrices%20y%20%C3%A1ngulos.md).

---

## 4. Animación esqueletal (Spine)

GameMaker tiene **soporte nativo para Spine**: 48 funciones `skeleton_*` en el runtime.

```sh
python3 "_indice/buscar.py" --listar skeleton_
```

No necesitas extensión: exportas desde Spine e importas el sprite esqueletal directamente.

---

## 5. Audio

### Lo que ya trae el motor (2026)

LTS 2026 incorporó **buses y efectos de audio** nativos: *bitcrusher*, *delay*, ganancia,
filtros, reverberación… Antes esto exigía FMOD o una extensión.

```sh
python3 "_indice/buscar.py" --listar audio_bus
python3 "_indice/buscar.py" --listar audio_effect
```

📖 [`02 - Novedades 2026/07 · Audio — buses y efectos`](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md)

### Cuándo salir del motor

| Opción | ★ | Cuándo |
|---|---:|---|
| [**GMEXT-FMOD**](https://github.com/YoYoGames/GMEXT-FMOD) (oficial) | 74 | Audio adaptativo serio, con **FMOD Studio** como herramienta de autoría. Es lo que usan los estudios |
| [**fml**](https://github.com/Nikkilae/fml) | 7 | *Bindings* alternativos a la API de FMOD Studio |
| [**Vinyl**](https://github.com/JujuAdams/Vinyl) | 61 | Mezclas, buses, *ducking* y variaciones **declarativas** desde un fichero de configuración. La opción intermedia |
| [**bard-audio**](https://github.com/gl326/bard-audio) | 40 | Mezcla dinámica y música adaptativa |
| [**Phonix**](https://github.com/Andre-404/Phonix) | 6 | Sistema de audio compacto |
| [**audioExt**](https://github.com/tabularelf/audioExt) | 6 | Gestor de audio externo (cargar ficheros de disco) |
| [**ExternalAudio**](https://github.com/katsaii/ExternalAudio) | 1 | Cargar audio externo, en GML puro |
| [**wavload**](https://github.com/nkrapivin/wavload) | 7 | Ejemplo de carga externa de `.wav` |
| [**AssParser**](https://github.com/DecadeDecaf/AssParser) | 0 | **Subtítulos** para reproducción de vídeo |
| **Wwise** (Audiokinetic) | — | ⚠️ **Sin integración mantenida.** `CaKlassen/gmwwise` (★26, sin *commits* desde 2022-10) y `Fatdazz/lib-GMWwise` (★2, sin *commits* desde 2021) están abandonados — verificado con la API de GitHub el 6 de septiembre de 2026. Usa buses nativos + Vinyl, o GMEXT-FMOD si de verdad hace falta middleware |

📁 Todas en `librerias/audio/` salvo `AssParser` (`librerias/extras/`) y la oficial
(`extensiones_oficiales/GMEXT-FMOD/`).

> **Recomendación:** empieza con las funciones nativas + **Vinyl** si necesitas organización.
> Salta a FMOD solo si tienes un diseñador de sonido que ya trabaja con FMOD Studio.

---

## 6. Shaders y postprocesado

| Herramienta | ★ | Qué hace | Ruta |
|---|---:|---|---|
| [**Xpanda**](https://github.com/GameMakerDiscord/Xpanda) | 16 | `#include` en shaders: reutilizar GLSL entre ficheros | `librerias/shaders/Xpanda` |
| [**Shadertoy2GM**](https://github.com/jfkn1ght/Shadertoy2GM) | 12 | Convierte GLSL de **Shadertoy** a shaders de GameMaker | `librerias/shaders/Shadertoy2GM` |
| **Shady** | — | Preprocesador GLSL con *imports* y variantes de shader | [GameMaker Kitchen](https://www.gamemakerkitchen.com/tools) |
| [**Bokeh**](https://github.com/XorDev/Bokeh) · [**Dual-Kawase**](https://github.com/XorDev/Dual-Kawase) · [**1PassBlur**](https://github.com/XorDev/1PassBlur) | 19/11/15 | Desenfoques de calidad (XorDev es la referencia en shaders para GameMaker) | `librerias/shaders/` |
| [**Post-Processing FX**](https://foxyofjungle.itch.io/post-processing-fx) 💸 $34,30 | — | Suite de efectos visuales de alto rendimiento | itch.io |
| [**RenderStack**](https://github.com/FoxyOfJungle/RenderStack) | 7 | Gestión del renderizado en capas virtuales ordenadas | `librerias/utilidades/RenderStack` |

📖 Base en [`08 - Referencia GML/06 · Shaders`](../08%20-%20Referencia%20GML%20completa/06%20-%20Shaders.md).

> 🆕 LTS 2026 trae además **filtros y efectos de capa (FX)** nativos, que cubren muchos casos
> sin escribir un shader. Ver [`08 - Referencia GML completa`](../08%20-%20Referencia%20GML%20completa/)
> y `python3 "_indice/buscar.py" --listar fx_`.

---

## 6 bis. Atlas de texturas (TexturePacker)

GameMaker **ya empaqueta tus sprites en atlas él solo**: son los *texture groups*. TexturePacker
solo tiene sentido en un caso concreto, así que antes de comprar nada, comprueba si es el tuyo.

### Primero, mira si tienes un problema real

GameMaker trae dos herramientas para esto, y con ellas basta para saber si tienes un problema:

```gml
/// obj_control · Create — solo en depuración
if (debug_mode) {
    texture_debug_messages(true);   // avisa por consola de cada cambio de página
    show_debug_overlay(true);       // superposición con fps y draw calls
}
```

- **`texture_debug_messages(true)`** escupe un mensaje **cada vez que se cambia de página de
  textura**. Si ves decenas por fotograma, tus sprites están mal repartidos.
- **`show_debug_overlay(true)`** te da fps reales y número de *draw calls* en pantalla.

📘 [Páginas de textura](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Texture_Information/Texture_Pages.md) ·
📘 [Grupos de textura](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Texture_Groups.md)

**Síntomas de que el atlas es tu cuello de botella:**

| Síntoma | Causa probable |
|---|---|
| Tirones al entrar en una sala nueva | Páginas cargándose en caliente |
| Consumo de VRAM muy alto en móvil | Páginas medio vacías por mal reparto |
| Muchas *draw calls* por fotograma | Sprites que se dibujan juntos están en páginas distintas |

### La solución que casi siempre basta: texture groups

Antes de meter una herramienta externa, **agrupa por sala, no por tipo**. El objetivo es que
todo lo que se dibuja en la misma pantalla viva en la misma página.

En el Inspector de cada sprite: **Texture Group → tg_nivel_1** (o el que corresponda).
Y en **Tools → Texture Groups** creas los grupos y decides cuáles se cargan al arrancar.

```gml
/// cargar y liberar grupos al cambiar de nivel
texturegroup_load("tg_nivel_2", true);      // true = bloquea hasta terminar
texturegroup_unload("tg_nivel_1");
```

> 🔺 **`texturegroup_*` no existe en HTML5.** En web, todo se carga de golpe. Ver
> [17 · Interoperabilidad con la web](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md).

### Cuándo sí compensa TexturePacker

**[TexturePacker](https://www.codeandweb.com/texturepacker)** (CodeAndWeb, comercial, prueba
gratuita) empaqueta mejor que GameMaker en un caso: **cuando tus sprites tienen mucho hueco
transparente** — árboles, efectos, siluetas irregulares. Su empaquetado con polígonos recorta
la silueta real en vez de reservar el rectángulo completo.

| | Texture groups de GameMaker | TexturePacker |
|---|---|---|
| Coste | Incluido | De pago |
| Recorte | Rectangular | Rectangular **o poligonal** |
| Integración | Nativa, sin pasos extra | Exportas y reimportas a mano |
| ¿Sobrevive a un cambio de arte? | Sí, automático | Hay que reexportar |

> ⚠️ **El coste real no es la licencia, es el paso manual.** Cada vez que tu artista toque un
> sprite hay que reexportar el atlas. Si no tienes ese paso automatizado en un script, el
> equipo acabará trabajando con un atlas desfasado. **No lo metas hasta haber medido que los
> texture groups no te llegan.**

---

## 7. Color

| Librería | ★ | Qué hace | Ruta |
|---|---:|---|---|
| [**OKColor.gml**](https://github.com/KeeVeeGames/OKColor.gml) | 56 | Gestión de color con **OKLab/OKLCH**: interpolaciones y paletas que se ven bien de verdad | `librerias/datos-y-estructuras/OKColor.gml` |
| [Sushi! Color Picker](https://makorie.itch.io/sushi-color-picker) | — | Selector de color para pixel art (herramienta externa, gratis) | itch.io |

📖 [`08 - Referencia GML/04 · Color y blending`](../08%20-%20Referencia%20GML%20completa/04%20-%20Color%20y%20blending.md).

---

## 8. Localización

Si vas a traducir tu juego —y esta biblioteca existe justamente porque la traducción importa—:

| Librería | ★ | Qué hace | Ruta |
|---|---:|---|---|
| [**lexicon**](https://github.com/tabularelf/lexicon) | 52 | Ficheros de idioma con sustitución de variables | `librerias/localizacion/lexicon` |
| [**polyglot**](https://github.com/daikon-games/polyglot) | 35 | Localización sencilla | `librerias/localizacion/polyglot` |
| [**Localize**](https://github.com/Kruger0/Localize) | 20 | Multi-idioma con sincronización | `librerias/localizacion/Localize` |
| [**gm-i18n**](https://github.com/CreativeHandOficial/gm-i18n) | 21 | i18n para GMS 2.3+ | `librerias/localizacion/gm-i18n` |
| [**GMLocalize2**](https://github.com/DragoniteSpam/GMLocalize2) | 5 | Con interfaz visual | `librerias/localizacion/GMLocalize2` |
| [**small_pp_localization_tool**](https://github.com/AntonBergaker/small_pp_localization_tool) | 11 | Exportación a hoja de cálculo para traductores | `librerias/localizacion/small_pp_localization_tool` |
| **Cultured** | — | Localización dentro de GameMaker | [GameMaker Kitchen](https://www.gamemakerkitchen.com/tools) |
| [**Unic**](https://github.com/TabularElf/Unic) | 8 | **Soporte Unicode real**: normalización y mayúsculas correctas | `librerias/datos-y-estructuras/Unic` |
| [**AsciiTransliterate**](https://github.com/JujuAdams/AsciiTransliterate) | 1 | Transliteración a ASCII para búsquedas sin acentos | `librerias/datos-y-estructuras/AsciiTransliterate` |

> ⚠️ Si tu juego va a estar en español, **Unic no es opcional**: sin él, `string_upper("ñ")`
> y el orden alfabético te van a dar sorpresas.

### Texto quemado en un sprite: la trampa que no avisa

Un botón «JUGAR», un logo con texto o un cartel dibujado a mano dentro de un `.png` **no pasa
por `txt()`** ([`04 · 21`](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md)):
es un dibujo. Traduces los 800 textos del juego, publicas, y ese botón sigue en español para
todo el mundo — nadie lo detecta hasta que un jugador lo reporta, porque no hay ningún error
que lanzar.

Dos salidas, según cuánto pese el texto en el diseño del sprite:

- **Rehacerlo como texto real sobre gráfico neutro.** El sprite lleva solo el fondo/marco; el
  texto se dibuja encima con `txt()` y una fuente, igual que cualquier otro texto del juego. Es
  la solución por defecto: cero sprites nuevos por idioma.
- **Una variante de sprite por idioma**, cuando el texto es parte del arte (un logo, una
  ilustración con rótulo integrado) y no se puede separar limpiamente. Incluida como parte de
  los datos de localización: se produce, no se improvisa.

```gml
/// mismo patrón que voz_localizada_obtener() de 13 · 24 §3.2, aplicado a sprites
/// @func grafico_localizado_obtener(_nombre)
/// @desc Handle del sprite "spr_<nombre>_<idioma>", o -1 si no existe esa variante.
function grafico_localizado_obtener(_nombre) {
    return asset_get_index("spr_" + _nombre + "_" + global.idioma);
}
```

```gml
/// uso: spr_boton_jugar_es, spr_boton_jugar_en, spr_boton_jugar_ja…
var _spr = grafico_localizado_obtener("boton_jugar");
if (_spr != -1) draw_sprite(_spr, 0, x, y);
```

> 🔺 **Un sprite nuevo por idioma es un asset de producción, no un `if` suelto.** Añádelo a la
> lista de encargos de arte de cada idioma nuevo, con el mismo peso que una línea de voz o una
> hoja de traducción — si se te olvida, no hay ningún `[[clave]]` que lo delate.

---

## Fuentes

- awesome-gamemaker: <https://github.com/bytecauldron/awesome-gamemaker>
- GameMaker Kitchen · Tools y Libraries: <https://www.gamemakerkitchen.com/>
- itch.io · assets GameMaker: <https://itch.io/game-assets/tag-gamemaker>
- Metadatos de repositorios: API de GitHub, 1 de septiembre de 2026
- Ogmo Editor 3, repositorio oficial (Community Edition): <https://github.com/Ogmo-Editor-3/OgmoEditor3-CE> — MIT, escrito en Haxe, sin commits desde 2024-06-19; búsqueda de repositorios y de código en GitHub (`ogmo gamemaker`, `ogmo gml`) el 7 de septiembre de 2026, sin ningún resultado de un importador o parser en GML — 6 de septiembre de 2026.
