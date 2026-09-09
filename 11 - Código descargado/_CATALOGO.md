# Catálogo del código descargado

> Espejo local del código fuente del ecosistema de GameMaker.
> **632 repositorios** clonados con `git clone --depth 1` (base del **1 de septiembre de 2026**;
> ampliado el **2 de septiembre** con la organización completa de tutoriales de DragoniteSpam y una
> auditoría de novedades 2025-2026, incluida la suite de YellowAfterlife y el barrido completo de GameMakerDiscord y las 44 extensiones oficiales GMEXT-*).
> **El recuento exacto y siempre al día es [`_RUTAS.json`](./_RUTAS.json)** (632 claves); la tabla
> de abajo es el desglose orientativo por categoría.

## Qué es esto y qué no es

De cada repositorio se ha copiado **solo el texto**: `.gml`, `.md`, `.yyp`, shaders, configuración y código nativo fuente. **No** hay sprites, sonidos, binarios ni `.yy` de recursos individuales. El objetivo es tener un corpus **greppable** de GML real, no una copia ejecutable de los proyectos.

> ⚠️ **Cada repositorio conserva su propia licencia** (está en su carpeta). Esto es material de consulta y aprendizaje. Antes de copiar código a un proyecto tuyo, **lee la licencia**. Los juegos comerciales extraídos (Pizza Tower, Deltarune, AM2R, Hotline Miami, Kirby) están aquí como **referencia de lectura**: su código no es libre y no debes reutilizarlo.

## Cómo buscar aquí

```sh
# ¿Dónde se usa de verdad una función? (además de su ficha)
python3 "_indice/buscar.py" audio_play_sound

# ¿Cómo resuelve la gente un problema concreto?
python3 "_indice/buscar.py" --codigo "coyote"
python3 "_indice/buscar.py" --codigo "screen_shake"

# Ruta exacta de un repositorio por su nombre
python3 -c 'import json;print(json.load(open("11 - Código descargado/_RUTAS.json"))["Scribble"])'
```

El fichero [`_RUTAS.json`](./_RUTAS.json) mapea **nombre de repositorio → ruta**.

## Resumen

| Categoría | Repositorios | Archivos `.gml` | Archivos totales |
|---|---:|---:|---:|
| [Librerías de la comunidad](#librerias) | 238 | 21506 | 25423 |
| [Extensiones oficiales de YoYo Games](#extensiones-oficiales) | 44 | 2959 | 4998 |
| [Juegos y motores de referencia](#juegos-y-motores) | 21 | 28723 | 37035 |
| [Plantillas, ejemplos y utilidades oficiales](#plantillas-y-ejemplos) | 18 | 1089 | 2257 |
| [Herramientas del ecosistema](#herramientas) | 3 | 146 | 247 |
| [Tutoriales de DragoniteSpam](#dragonitespam) | 189 | 3909 | 21812 |
| [Novedades 2025-2026 (auditoría)](#novedades-2026) | ~87 | ~2700 | ~12000 |
| **TOTAL** (desglose orientativo — el exacto es `_RUTAS.json`) | **~600** | **~61000** | **~103800** |

<a id="librerias"></a>

## Librerías de la comunidad

Código reutilizable, **organizado por tema**. Antes de escribir un sistema desde cero, mira si ya existe aquí. La mayoría es MIT.

### Temas

[3D y renderizado tridimensional](#3d) · [Asincronía, promesas y corrutinas](#asincronia) · [Audio y música](#audio) · [Cámaras, resolución y escalado](#camara) · [Datos, estructuras y serialización](#datos-y-estructuras) · [Depuración, pruebas y perfilado](#depuracion) · [Diálogos y narrativa](#dialogos-y-narrativa) · [Entrada: teclado, ratón, gamepad y táctil](#entrada) · [Extensiones nativas (DLL / C++)](#extensiones-nativas) · [Extras y misceláneos](#extras) · [Física y colisiones](#fisica) · [Herramientas externas de desarrollo](#herramientas-externas) · [Iluminación y sombras](#iluminacion) · [Integraciones con servicios y plataformas](#integraciones) · [Interfaz de usuario (UI/HUD)](#interfaz-de-usuario) · [Localización y traducción](#localizacion) · [Máquinas de estados](#maquinas-de-estados) · [Matemáticas, vectores y aleatoriedad](#matematicas) · [Niveles, mapas y generación procedural](#niveles-y-mapas) · [Partículas y efectos](#particulas) · [Pathfinding y navegación](#pathfinding) · [Red y multijugador](#red-y-multijugador) · [Secuencias y animación por línea de tiempo](#secuencias) · [Shaders y postprocesado](#shaders) · [Sprites y animación](#sprites-y-animacion) · [Texto y tipografía](#texto-y-tipografia) · [Tiempo, temporizadores y bucle de juego](#tiempo-y-temporizadores) · [Utilidades generales de GML](#utilidades)


<a id="3d"></a>

### 3D y renderizado tridimensional

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `BBMOD` [↗](https://github.com/blueburncz/BBMOD) | El motor 3D de referencia para GameMaker: modelos, animación esqueletal, materiales PBR, terreno, niebla y sombras. Incluye exportador para Blender. | 119 | MIT | 2026-08-04 | 453 |
| `dotobj` [↗](https://github.com/JujuAdams/dotobj) | Cargador de **.obj/.mtl** escrito en GML nativo. Sin extensión nativa. | 47 | MIT | 2025-10-12 | 86 |
| `DmrVBM-blender-to-gms2` [↗](https://github.com/Dreamer13sq/DmrVBM-blender-to-gms2) | Exporta **vertex buffers desde Blender** a GameMaker. | 43 | MIT | 2026-08-21 | 52 |
| `ThreeMiceInaTrenchcoat` [↗](https://github.com/XorDev/ThreeMiceInaTrenchcoat) | Experimento 3D de XorDev. | 10 | sin licencia | 2021-06-25 | 5078 |
| `GMFlux` [↗](https://github.com/Fanatrick/GMFlux) | Solucionador de **fluidos por campo de altura** en GPU, muy rápido y configurable. | 9 | MIT | 2022-11-08 | 5 |
| `Bronze-Box` [↗](https://github.com/cicadian/Bronze-Box) | Ejemplo de mundos 3D sencillos construidos desde una rejilla 2D, al estilo *Eye of the Beholder* o *Etrian Odyssey*. | 5 | MIT | 2022-07-23 | 16 |
| `Cardboard` [↗](https://github.com/JujuAdams/Cardboard) | Renderizado de geometría 3D sencilla sobre el pipeline 2D de GameMaker. | 3 | MIT | 2026-07-08 | 308 |
| `BBMOD-Blender` [↗](https://github.com/blueburncz/BBMOD-Blender) | Complemento de Blender para exportar al formato de BBMOD. | 2 | MIT | 2026-08-03 | 0 |
| `Stack3D` [↗](https://github.com/dev-dwarf/Stack3D) | El método más rápido de **sprite stacking** (falso 3D apilando sprites) en GameMaker. 🆕 | 18 | — | 2021-07-11 | 31 |

<a id="asincronia"></a>

### Asincronía, promesas y corrutinas

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Coroutines` [↗](https://github.com/JujuAdams/Coroutines) | **Corrutinas** para GameMaker: pausar y reanudar una función a lo largo de varios frames. Perfecto para secuencias de guion y cutscenes. | 83 | MIT | 2025-06-29 | 69 |
| `Promise.gml` [↗](https://github.com/YAL-GameMaker/Promise.gml) | Adaptación del *polyfill* de **Promise** de JavaScript. | 26 | sin licencia | 2023-07-21 | 10 |
| `SimThreads` [↗](https://github.com/tabularelf/SimThreads) | **Ejecución en paralelo** en GameMaker. | 15 | MIT | 2024-05-07 | 11 |
| `GML-Promise` [↗](https://github.com/tinkerer-red/GML-Promise) | Promesas al estilo JS más un buen número de funciones asíncronas que devuelven promesa. | 9 | sin licencia | 2025-11-27 | 18 |
| `MultiProcessing` [↗](https://github.com/tinkerer-red/MultiProcessing) | Ejemplo de multiproceso en GML, pensado para que se entienda. | 2 | MIT | 2023-11-06 | 18 |

<a id="audio"></a>

### Audio y música

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Vinyl` [↗](https://github.com/JujuAdams/Vinyl) | Sistema de audio declarativo: mezclas, buses, ducking, variaciones aleatorias y control de volumen por categoría desde un fichero de configuración. | 61 | MIT | 2026-07-08 | 192 |
| `bard-audio` [↗](https://github.com/gl326/bard-audio) | Motor de audio con mezcla dinámica y música adaptativa. | 40 | MIT | 2024-09-16 | 288 |
| `fml` [↗](https://github.com/Nikkilae/fml) | *Bindings* de GameMaker a la API de **FMOD Studio**. | 7 | MIT | 2025-03-08 | 102 |
| `wavload` [↗](https://github.com/nkrapivin/wavload) | Ejemplo de carga externa de ficheros **.wav**. | 7 | Unlicense | 2020-10-05 | 4 |
| `Phonix` [↗](https://github.com/Andre-404/Phonix) | Sistema de audio compacto. | 6 | MIT | 2022-06-18 | 14 |
| `audioExt` [↗](https://github.com/tabularelf/audioExt) | Gestor de **audio externo**: cargar ficheros de sonido desde disco en tiempo de ejecución. | 6 | MIT | 2024-12-07 | 33 |
| `LineAudio` [↗](https://github.com/WangleLine/LineAudio) | Utilidades de audio ligeras. | 5 | MIT | 2026-07-25 | 11 |
| `Sonus` [↗](https://github.com/tabularelf/Sonus) | Envoltorio de audio con reproducción por capas y transiciones. | 5 | MIT | 2024-05-26 | 47 |
| `ExternalAudio` [↗](https://github.com/NuxiiGit/ExternalAudio) | Extensión en GML puro para cargar **audio externo** en tiempo de ejecución. | 1 | sin licencia | 2019-02-27 | 15 |

<a id="camara"></a>

### Cámaras, resolución y escalado

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `STANNcam` [↗](https://github.com/stann-co/STANNcam) | Sistema de cámaras con soporte de resolución, zoom, sacudida y seguimiento suave. | 43 | MIT | 2026-08-21 | 64 |
| `pixel-perfect-smooth-camera` [↗](https://github.com/YAL-GameMaker/pixel-perfect-smooth-camera) | Ejemplo de cámara **pixel-perfect pero suave**: resuelve el conflicto clásico entre nitidez y movimiento fluido. | 38 | sin licencia | 2020-12-10 | 8 |
| `PictureFrame` [↗](https://github.com/JujuAdams/PictureFrame) | Resuelve de una vez el problema de cámaras, viewports, resolución y escalado *pixel perfect*. Compañero directo de los capítulos 41-44 del curso de PixelatedPope. | 10 | MIT | 2026-08-16 | 40 |

<a id="datos-y-estructuras"></a>

### Datos, estructuras y serialización

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `SNAP` [↗](https://github.com/JujuAdams/SNAP) | Conversión entre estructuras de GameMaker y formatos externos: JSON, CSV, XML, YAML, TOML, binario. La navaja suiza de la serialización. | 100 | MIT | 2026-07-08 | 96 |
| `OKColor.gml` [↗](https://github.com/KeeVeeGames/OKColor.gml) | Gestión de color con **OKLab/OKLCH**: genera, convierte, ajusta al gamut y mezcla colores con resultados visualmente correctos. También RGB, HSV, HSL, Lab y LCH. | 56 | MIT | 2026-01-18 | 3 |
| `Destructors` [↗](https://github.com/DatZach/Destructors) | **Destructores** para structs: ejecutar código cuando el recolector de basura libera un objeto. | 26 | MIT | 2022-10-24 | 5 |
| `foreach.gml` [↗](https://github.com/KeeVeeGames/foreach.gml) | Implementación de `foreach()` para arrays, `ds_list`, `ds_map`, `ds_stack`, `ds_queue`, `ds_priority` y structs. | 26 | MIT | 2020-10-13 | 2 |
| `Elephant` [↗](https://github.com/JujuAdams/Elephant) | Serialización profunda de structs, arrays e instancias, incluidas las referencias circulares. Base para sistemas de guardado complejos. | 24 | MIT | 2026-07-02 | 30 |
| `db` [↗](https://github.com/JujuAdams/db) | Base de datos en memoria con consultas sobre structs. Útil para inventarios, catálogos y tablas de datos del juego. | 22 | MIT | 2026-08-26 | 40 |
| `ArrayList.gml` [↗](https://github.com/KeeVeeGames/ArrayList.gml) | La clase de lista más completa para GameMaker: accesor `[ ]`, más de 50 funciones (añadir, quitar, insertar, buscar, ordenar, barajar, invertir) y compatible con el recolector de basura. | 19 | MIT | 2020-12-03 | 2 |
| `GML-Classes` [↗](https://github.com/Nikko-the-cat/GML-Classes) | Script de extensión que añade características de **POO** a GML. | 18 | sin licencia | 2024-05-08 | 4 |
| `Exception.gml` [↗](https://github.com/KeeVeeGames/Exception.gml) | Clase base para **excepciones** en GameMaker, con mejor salida de error y mejor soporte en YYC. | 17 | MIT | 2025-03-29 | 3 |
| `Cottonwool` [↗](https://github.com/JujuAdams/Cottonwool) | **Superficies seguras**: gestiona la pérdida de superficies (el fallo silencioso más común al cambiar de pantalla completa). *(📦 archivado)* | 14 | sin licencia | 2024-07-12 | 8 |
| `DeepCopy.gml` [↗](https://github.com/KeeVeeGames/DeepCopy.gml) | **Copia profunda** de structs construidos, structs anónimos y arrays anidados en cualquier orden. | 12 | MIT | 2023-03-18 | 6 |
| `Lock-And-Key` [↗](https://github.com/AlubJ/Lock-And-Key) | **Cifrado** de cadenas y ficheros. | 10 | MIT | 2020-09-07 | 3 |
| `lwo` [↗](https://github.com/tabularelf/lwo) | *Light Weight Objects*: objetos ligeros sin el coste de una instancia. *(📦 archivado)* | 9 | MIT | 2021-07-07 | 5 |
| `Unic` [↗](https://github.com/TabularElf/Unic) | Soporte Unicode real en GML: normalización, mayúsculas/minúsculas y datos CLDR. (Los datos CLDR se han retirado del espejo por tamaño; están en el repositorio original.) | 8 | MIT | 2026-03-29 | 73 |
| `gm-stream` [↗](https://github.com/daikon-games/gm-stream) | Implementación de **streams** al estilo Java: API fluida para manipular estructuras de datos encadenando operaciones. | 8 | propia | 2022-03-02 | 2 |
| `matrices` [↗](https://github.com/JujuAdams/matrices) | Colección de scripts para manejar matrices. | 7 | MIT | 2024-02-18 | 34 |
| `BSONGML` [↗](https://github.com/LAGameStudio/BSONGML) | Serialización binaria robusta y rápida de datos complejos de tipo mixto. Resuelve los problemas de `json_stringify` con estructuras grandes. | 6 | MIT | 2025-03-22 | 3 |
| `Binder` [↗](https://github.com/Homunculus84/Binder) | Búsqueda binaria avanzada. | 6 | MIT | 2025-06-19 | 19 |
| `Map.gml` [↗](https://github.com/GameMakerDiscord/Map.gml) | Tabla hash compatible con el recolector de basura. Alternativa moderna a `ds_map`. | 3 | sin licencia | 2020-06-14 | 8 |
| `Ngrams` [↗](https://github.com/tinkerer-red/Ngrams) | Implementación ligera de **búsqueda elástica y n-gramas predictivos**. Para buscadores dentro del juego. | 3 | sin licencia | 2025-12-10 | 14 |
| `Airkiver` [↗](https://github.com/AlubJ/Airkiver) | Herramienta de **archivado de ficheros del juego** en un solo paquete. | 1 | MIT | 2026-01-20 | 2 |
| `AsciiTransliterate` [↗](https://github.com/JujuAdams/AsciiTransliterate) | Transliteración de texto Unicode a ASCII (búsquedas y ordenación insensibles a acentos). | 1 | MIT | 2026-07-28 | 9 |

<a id="depuracion"></a>

### Depuración, pruebas y perfilado

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `rt-shell` [↗](https://github.com/daikon-games/rt-shell) | **Consola de trucos y depuración dentro del juego**: comandos propios, metadatos, sugerencias e historial. La herramienta de depuración más útil del ecosistema. | 96 | propia | 2023-07-11 | 16 |
| `crispy` [↗](https://github.com/bfrymire/crispy) | Framework de **pruebas unitarias** escrito en GML, específico para la rama LTS. | 40 | MIT | 2025-11-26 | 22 |
| `Snitch` [↗](https://github.com/JujuAdams/Snitch) | Captura y reporte de errores en producción: registra los crashes de tu juego publicado y te los envía. | 39 | MIT | 2026-07-29 | 55 |
| `GMBenchmark` [↗](https://github.com/DragoniteSpam/GMBenchmark) | Banco de pruebas para medir el coste real de funciones de GML. Úsalo antes de optimizar a ciegas. | 34 | MIT | 2026-08-18 | 129 |
| `Gobo` [↗](https://github.com/Pizzaandy/Gobo) | **Formateador de GML con opinión propia**, al estilo de Prettier. Se acabó discutir dónde va la llave. | 33 | MIT | 2025-11-21 | 0 |
| `gms2-test` [↗](https://github.com/pmarincak/gms2-test) | Framework de pruebas unitarias sencillo. | 28 | MIT | 2022-12-27 | 15 |
| `Lookout` [↗](https://github.com/GlebTsereteli/Lookout) | Observador de cambios de variables para depuración. | 21 | MIT | 2026-08-08 | 16 |
| `olympus` [↗](https://github.com/bscotch/olympus) | Framework de pruebas de Bscotch (los de *Crashlands*). | 21 | MIT | 2024-05-13 | 51 |
| `Inspectron` [↗](https://github.com/shdwcat/Inspectron) | API fluida para construir **vistas de depuración** con poco código. | 16 | MIT | 2024-06-19 | 2 |
| `duck` [↗](https://github.com/imlazyeye/duck) | **Analizador estático de GML** rápido y flexible: aplica estilo y detecta errores antes de compilar. | 14 | Apache-2.0 | 2025-06-05 | 0 |
| `ganary` [↗](https://github.com/bscotch/ganary) | Pruebas de **regresión** montadas sobre Olympus. | 10 | sin licencia | 2026-08-31 | 126 |
| `meta` [↗](https://github.com/nommiin/meta) | **Inspector de assets en tiempo de ejecución**. | 8 | MIT | 2020-08-15 | 1 |
| `gm-verrific` [↗](https://github.com/Alphish/gm-verrific) | Framework de **pruebas automatizadas**, el más ambicioso de la comunidad. | 5 | MIT | 2025-10-12 | 41 |
| `GoboCat` [↗](https://github.com/EttyKitty/GoboCat) | Fork de Gobo **determinista y más configurable**, con más opciones. | 0 | MIT | 2026-07-22 | 0 |
| `GM-EzConsole` [↗](https://github.com/DAndrewBox/GM-EzConsole) | **Consola de depuración** en pantalla para escribir comandos mientras el juego corre. 🆕 | 11 | MIT | 2025-09-01 | 21 |

<a id="dialogos-y-narrativa"></a>

### Diálogos y narrativa

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Chatterbox` [↗](https://github.com/JujuAdams/Chatterbox) | Intérprete de Yarn (el lenguaje de diálogo de *Night in the Woods*) para GameMaker. Diálogos ramificados, variables y condiciones sin escribir un parser. | 175 | MIT | 2026-08-13 | 260 |
| `Crochet` [↗](https://github.com/FaultyFunctions/Crochet) | Editor visual de diálogos ramificados con exportación a GameMaker. | 121 | MIT | 2026-05-28 | 0 |
| `gmdialogue` [↗](https://github.com/danielpancake/gmdialogue) | Sistema de diálogos ligero con etiquetas de formato. | 18 | sin licencia | 2024-06-10 | 22 |

<a id="entrada"></a>

### Entrada: teclado, ratón, gamepad y táctil

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Input` [↗](https://github.com/offalynne/Input) | **La** librería de entrada de GameMaker: teclado, ratón, gamepad, multijugador local, remapeo, buffers, chords y detección de dispositivo. Archivada por su autora pero sigue siendo el estándar de facto. *(📦 archivado)* | 311 | MIT | 2026-01-30 | 344 |
| `Input-Dog` [↗](https://github.com/messhof/Input-Dog) | Gestor de entrada ligero, alternativa mínima a Input. | 39 | MIT | 2016-05-19 | 34 |
| `good-vibes` [↗](https://github.com/mrdaneeyul/good-vibes) | **Vibración de mando** para GameMaker Studio 2. | 27 | MIT | 2022-11-24 | 8 |
| `InputCandy` [↗](https://github.com/LAGameStudio/InputCandy) | Soporte muy completo de **gamepads**, con base de datos de mandos. | 18 | MIT | 2025-03-14 | 25 |
| `InputTouch` [↗](https://github.com/AlubJ/InputTouch) | *Plug-in* de **entrada táctil** para la librería Input. | 9 | MIT | 2026-06-29 | 410 |
| `window_mouse_queue` [↗](https://github.com/YAL-GameMaker/window_mouse_queue) | Datos de movimiento del ratón de **alta precisión** en Windows. Para software de dibujo y juegos de puntería. | 6 | MIT | 2024-07-14 | 19 |
| `Input-Legacy` [↗](https://github.com/offalynne/Input-Legacy) | Versión anterior de Input, conservada para proyectos que no pueden migrar. *(📦 archivado)* | 1 | MIT | 2026-01-30 | 446 |

<a id="extensiones-nativas"></a>

### Extensiones nativas (DLL / C++)

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `GMSDLL` [↗](https://github.com/YAL-GameMaker/GMSDLL) | **Plantilla para escribir extensiones nativas en C++**. | 19 | sin licencia | 2024-06-15 | 16 |
| `wasm-bridge` [↗](https://github.com/Sidorakh/wasm-bridge) | Incluir extensiones de **JavaScript** en juegos de GX/WASM. | 16 | MIT | 2025-08-28 | 2 |
| `gameframe` [↗](https://github.com/YAL-GameMaker/gameframe) | **Marco de ventana personalizado** para juegos de GameMaker. | 15 | propia | 2024-09-15 | 12 |
| `gm-sysinfo` [↗](https://github.com/SpikeHD/gm-sysinfo) | Extensión multiplataforma para obtener **información del sistema** y uso de recursos. | 12 | MIT | 2023-12-12 | 1 |
| `GMSDLL.rs` [↗](https://github.com/YAL-GameMaker/GMSDLL.rs) | **Plantilla para escribir extensiones nativas en Rust**. | 7 | sin licencia | 2025-09-14 | 1 |
| `file_dragger` [↗](https://github.com/YAL-GameMaker/file_dragger) | Arrastrar ficheros **fuera** de la ventana del juego. | 5 | sin licencia | 2024-06-11 | 15 |
| `GMD3D11` [↗](https://github.com/JujuAdams/GMD3D11) | Acceso de bajo nivel a Direct3D 11 desde GameMaker en Windows. | 0 | CC0-1.0 | 2026-07-14 | 20 |

<a id="extras"></a>

### Extras y misceláneos

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `ThoughtsOnGameMaker` [↗](https://github.com/JujuAdams/ThoughtsOnGameMaker) | Reflexiones sobre el motor de **Juju Adams**, que mantiene media docena de las librerías clave del ecosistema. Lectura muy recomendable. | 53 | sin licencia | 2025-11-28 | 0 |
| `Clean-Shapes` [↗](https://github.com/JujuAdams/Clean-Shapes) | Librería de **primitivas con antialiasing**: círculos, líneas y polígonos suaves, que GameMaker no dibuja bien de serie. | 48 | MIT | 2026-05-26 | 52 |
| `gml_starfield_generator` [↗](https://github.com/PixelProphecy/gml_starfield_generator) | Script para generar **campos de estrellas**. | 33 | MIT | 2022-06-13 | 1 |
| `Gruvbox-GMTheme` [↗](https://github.com/heygleeson/Gruvbox-GMTheme) | Tema **Gruvbox** para el IDE. | 16 | sin licencia | 2022-08-12 | 0 |
| `DanmakuProject` [↗](https://github.com/OmegaX1000/DanmakuProject) | Motor eficiente de **bullet hell** (danmaku). | 14 | MIT | 2021-05-03 | 10 |
| `Tome` [↗](https://github.com/chesrowe/Tome) | Genera **sitios de documentación** automáticamente a partir del JSDoc de tu código GML. | 14 | MIT | 2026-05-12 | 19 |
| `gml-animated-flag` [↗](https://github.com/Grisgram/gml-animated-flag) | **Bandera animada** por vértices. | 13 | MIT | 2024-05-30 | 3 |
| `piano_example` [↗](https://github.com/gmclan-org/piano_example) | Piano en GameMaker usando control de tono (`pitch`). | 7 | MIT | 2023-02-17 | 2 |
| `pause_no_surface` [↗](https://github.com/gmclan-org/pause_no_surface) | Ejemplo de **pausa sin usar superficies**. | 5 | MIT | 2021-09-21 | 7 |
| `compatibility-scripts` [↗](https://github.com/gmclan-org/compatibility-scripts) | Scripts de compatibilidad de **GameMaker: Studio 1.4 a GameMaker 2022+**. Útiles al portar proyectos antiguos. | 2 | sin licencia | 2022-04-11 | 373 |
| `AssParser` [↗](https://github.com/DecadeDecaf/AssParser) | Soporte de **subtítulos** (formato .ass) para reproducción de vídeo. | 0 | sin licencia | 2025-12-01 | 4 |
| `Podium` [↗](https://github.com/JujuAdams/Podium) | Tablas de clasificación locales. | 0 | MIT | 2026-08-28 | 105 |
| `Sus` [↗](https://github.com/JujuAdams/Sus) | Comprobaciones de integridad y detección de manipulación de datos guardados. | 0 | MIT | 2026-08-28 | 233 |

<a id="fisica"></a>

### Física y colisiones

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Loj-Hadron-Collider` [↗](https://github.com/Lojemiru/Loj-Hadron-Collider) | **Motor de colisiones pixel-perfect** robusto. La alternativa cuando las máscaras nativas no bastan. | 42 | MIT | 2022-10-28 | 17 |
| `Bonk` [↗](https://github.com/JujuAdams/Bonk) | Detección de colisiones 3D y 2D con formas arbitrarias, fuera del sistema nativo de máscaras. | 15 | MIT | 2026-08-27 | 428 |
| `Fracture` [↗](https://github.com/GlebTsereteli/Fracture) | **Destrucción física** rápida y flexible: fractura procedural con Box2D. | 14 | MIT | 2026-07-25 | 121 |
| `GMVerlet-Integration` [↗](https://github.com/tabularelf/GMVerlet-Integration) | **Integración de Verlet**: cuerdas, telas y cadenas. Experimental. | 11 | sin licencia | 2021-06-10 | 6 |
| `Inverse-Kinematics-Extension-for-Gamemaker` [↗](https://github.com/tonystr/Inverse-Kinematics-Extension-for-Gamemaker) | **Cinemática inversa**: para brazos, patas y tentáculos que siguen un objetivo. | 4 | MIT | 2017-12-26 | 0 |

<a id="herramientas-externas"></a>

### Herramientas externas de desarrollo

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `stitch` [↗](https://github.com/bscotch/stitch) | Suite de herramientas de Bscotch: **CLI de pipeline** y **extensión de VSCode** para editar proyectos de GameMaker. | 158 | propia | 2026-06-15 | 47 |
| `Rubber` [↗](https://github.com/GameMakerDiscord/Rubber) | Compilación de proyectos desde línea de comandos, en JavaScript. ⚠️ Anterior al CLI oficial y sin cambios desde 2021; se conserva porque explica bien cómo funciona **Igor**. | 33 | MIT | 2021-02-20 | 0 |
| `GMLC` [↗](https://github.com/tinkerer-red/GMLC) | VM y compilador de GML escritos **en GML**, con la meta de compilar cualquier carpeta de proyecto. | 18 | sin licencia | 2026-06-11 | 572 |
| `vim-gml` [↗](https://github.com/JafarDakhan/vim-gml) | Resaltado de sintaxis de GML de calidad para **Vim** y Neovim. | 13 | MIT | 2022-10-04 | 6 |
| `GMLVM` [↗](https://github.com/erkan612/GMLVM) | Intérprete completo de GML para ejecutar código en tiempo de ejecución. | 5 | MIT | 2026-05-21 | 9 |
| `sfgml` [↗](https://github.com/YellowAfterlife/sfgml) | Compilador de **Haxe a GML**: escribe en Haxe y genera un proyecto de GameMaker. 🆕 | 32 | LGPL-3.0 | 2026-06-01 | 1 |
| `AseSync23` [↗](https://github.com/YAL-GameMaker-Tools/AseSync23) | Sincroniza automáticamente los sprites del proyecto cuando cambia el archivo de **Aseprite** en disco. 🆕 | 30 | — | 2026-07-22 | 0 |

<a id="iluminacion"></a>

### Iluminación y sombras

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Bulb` [↗](https://github.com/JujuAdams/Bulb) | Iluminación 2D dinámica con sombras proyectadas. Luces, oclusores y penumbras sobre superficies. | 107 | MIT | 2026-07-08 | 113 |
| `Gamemaker-Lighting-Engine` [↗](https://github.com/bilouw/Gamemaker-Lighting-Engine) | Motor de **iluminación** 2D. | 27 | MIT | 2019-02-15 | 15 |
| `GMShaders-Radiance-Cascades` [↗](https://github.com/Yaazarai/GMShaders-Radiance-Cascades) | **Cascadas de radiancia** en GameMaker: iluminación global 2D con rebote de color, el método de moda desde 2024. Es el código del artículo de GM Shaders. | 171 | Unlicense | 2025-02-05 | 31 |
| `RadianceCascades` [↗](https://github.com/Yaazarai/RadianceCascades) | Implementación 2D del paper original de Alexander Sannikov (Path of Exile). La versión anterior y más desnuda de la anterior. | 64 | Sin licencia | 2024-05-03 | 7 |
| `Global-Irradiance` [↗](https://github.com/Yaazarai/Global-Irradiance) | Irradiancia global 2D: el paso previo a las cascadas, con voxelización y propagación por rejilla. | 15 | Unlicense | 2023-10-27 | 8 |
| `Volumetric-HRC` [↗](https://github.com/Yaazarai/Volumetric-HRC) | Volumétricos por píxel en tiempo constante mediante extensión de rayos y cascadas holográficas. Lo más reciente del autor. | 121 | Unlicense | 2026-07-23 | 28 |
| `PathTraced-Volumetrics` [↗](https://github.com/Yaazarai/PathTraced-Volumetrics) | Volumétricos por trazado de caminos: la versión de referencia, lenta y correcta, con la que se contrasta la rápida. | 34 | Unlicense | 2026-02-17 | 7 |
| `2D-QuickRayTracing-GLSL` [↗](https://github.com/Yaazarai/2D-QuickRayTracing-GLSL) | Trazado de rayos 2D en dos pasadas con GLSL ES. Base de las técnicas de arriba. | 82 | LGPL-2.1 | 2026-05-08 | 0 |
| `prettylight` [↗](https://github.com/niksudan/prettylight) | Iluminación 2D sencilla y directa, sin sombras proyectadas. Útil como punto de partida mínimo. | 86 | MIT | 2018-10-08 | 19 |

<a id="pixel-art-ia"></a>

### Pixel art asistido por IA: generación, reparación y pipeline

> Casi todo **MIT y ejecutable en local**. La generación de Retro Diffusion es de pago por
> créditos, pero la mitad útil para un agente —**reparar** y **convertir a pixel art real**—
> es procesado de imagen puro: sin modelo, sin clave, sin cuenta. Ver `07 · 23 §1 bis`.

| Repositorio | Qué es | ★ | Licencia | Último cambio | archivos |
|---|---|---:|---|---|---:|
| `pixel-art-fixer` [↗](https://github.com/Retro-Diffusion/pixel-art-fixer) | **Convierte pixel art falso en pixel art real**: rejilla alineada, escala entera, colores recuperados. *Solo procesado de imagen, sin modelo* — local y gratis. | 383 | MIT | 2026-07-15 | 22 |
| `pixeldetector` [↗](https://github.com/Astropulse/pixeldetector) | **Repara pixel art dañado** por reescalado o compresión JPEG, y lo devuelve a su resolución real. Solo pide Pillow, Numpy y Scipy. | 357 | MIT | 2024-04-04 | 3 |
| `sd-palettize` [↗](https://github.com/Astropulse/sd-palettize) | Reduce a paleta las imágenes generadas. Extensión de Automatic1111. | 206 | Sin licencia | 2024-04-18 | 4 |
| `mixamotoopenpose` [↗](https://github.com/Astropulse/mixamotoopenpose) | Convierte animaciones de Mixamo en secuencias OpenPose: poses exactas para guiar la generación con ControlNet. | 114 | MIT | 2024-11-10 | 7 |
| `api-examples` [↗](https://github.com/Retro-Diffusion/api-examples) | Ejemplos de uso de la API de Retro Diffusion. | 147 | Sin licencia | 2026-09-02 | 23 |
| `pixel-bench` [↗](https://github.com/Retro-Diffusion/pixel-bench) | Banco de pruebas abierto para reconstrucción de pixel art: mide cuánto se parece un resultado al original. | 35 | MIT | 2026-07-16 | 37 |
| `retro-diffusion-mcp` [↗](https://github.com/Retro-Diffusion/retro-diffusion-mcp) | Servidor MCP para pedir sprites desde Claude, Cursor o cualquier cliente MCP. | 3 | MIT | 2026-09-02 | 13 |
| `stable-diffusion-aseprite` [↗](https://github.com/Astropulse/stable-diffusion-aseprite) | Stable Diffusion dentro de Aseprite. | 57 | Sin licencia | 2026-08-28 | 91 |
| `hexmap` [↗](https://github.com/Astropulse/hexmap) | Genera mapas de mundo con baldosas hexagonales. | 56 | MIT | 2026-01-07 | 3 |
| `K-Centroid-Aseprite` [↗](https://github.com/Astropulse/K-Centroid-Aseprite) | Algoritmo de reducción de escala por k-medias: conserva bordes duros donde un remuestreo normal los destroza. | 28 | MIT | 2023-04-25 | 6 |
| `tilesetbuilder` [↗](https://github.com/Astropulse/tilesetbuilder) | Construye tilesets a partir de dos texturas. | 22 | MIT | 2025-04-07 | 6 |
| `expression-generator` [↗](https://github.com/Astropulse/expression-generator) | Genera expresiones faciales de un personaje ya dibujado. | 20 | MIT | 2025-07-17 | 4 |
| `shadow-projector` [↗](https://github.com/Astropulse/shadow-projector) | Proyecta sombras desde sprites con fondo transparente. | 15 | MIT | 2025-08-14 | 3 |
| `spritesplitter` [↗](https://github.com/Astropulse/spritesplitter) | Parte una hoja de sprites en imágenes sueltas por relleno por difusión, sin rejilla fija. | 10 | MIT | 2026-01-21 | 3 |
| `hitherdither` [↗](https://github.com/Astropulse/hitherdither) | Algoritmos de tramado (*dithering*) para paletas arbitrarias, en PIL. Encaja directo con el generador de placeholders de 12/09 §5.2. | 4 | MIT | 2023-08-29 | 22 |
| `Material-Map-Generator` [↗](https://github.com/Astropulse/Material-Map-Generator) | Genera mapas normales y de desplazamiento a partir de una textura. Alimenta el normal map 2D de 04/24 §3. | 4 | Apache-2.0 | 2022-10-16 | 7 |

<a id="integraciones"></a>

### Integraciones con servicios y plataformas

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `steamworks.gml` [↗](https://github.com/YAL-GameMaker/steamworks.gml) | Ampliaciones del SDK de Steamworks. ⚠️ Su funcionalidad se fusionó en la extensión oficial. | 90 | sin licencia | 2023-07-31 | 71 |
| `GMTwitch` [↗](https://github.com/GameMakerDiscord/GMTwitch) | Interfaz ligera de **Twitch**, de código abierto. | 69 | MIT | 2022-01-03 | 15 |
| `GMHook` [↗](https://github.com/Kruger0/GMHook) | Implementación de **webhooks de Discord** para GameMaker. | 11 | MIT | 2026-07-04 | 7 |
| `GOG.gml` [↗](https://github.com/GameMakerDiscord/GOG.gml) | Extensión nativa para el SDK de **GOG.com**. | 11 | MIT | 2023-07-30 | 15 |
| `DHook` [↗](https://github.com/tabularelf/DHook) | Interacción con **webhooks de Discord**. | 6 | MIT | 2024-05-07 | 4 |
| `GitHub.gml` [↗](https://github.com/AlubJ/GitHub.gml) | Envoltorio de la **API REST de GitHub** desde GML. | 3 | MIT | 2026-01-20 | 33 |
| `Parworks` [↗](https://github.com/nkrapivin/Parworks) | Funcionalidad adicional para la extensión oficial de Steamworks. | 3 | sin licencia | 2022-06-30 | 132 |
| `Allchievements` [↗](https://github.com/JujuAdams/Allchievements) | Capa unificada de logros sobre Steam, Epic, GOG y demás back-ends. | 2 | MIT | 2026-07-03 | 45 |
| `GMS2_RPC` [↗](https://github.com/Mtax-Development/GMS2_RPC) | **Discord Rich Presence**: muestra en tu perfil de Discord a qué estás jugando. Incluye la aplicación *GameMaker Companion*. | 0 | sin licencia |  | 0 |

<a id="interfaz-de-usuario"></a>

### Interfaz de usuario (UI/HUD)

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `YUI` [↗](https://github.com/shdwcat/YUI) | Interfaz de usuario declarativa con un lenguaje de marcado propio, inspirado en HTML/CSS. | 65 | MIT | 2026-08-24 | 835 |
| `textboxy` [↗](https://github.com/glitchroy/textboxy) | **Cuadros de texto** sencillos, listos para diálogos. | 64 | MIT | 2023-03-05 | 45 |
| `Bento` [↗](https://github.com/JujuAdams/Bento) | Framework de interfaz de usuario con layout declarativo. Alternativa a montar el HUD a mano. | 53 | MIT | 2026-08-17 | 690 |
| `NotificationSystem` [↗](https://github.com/babaganosch/NotificationSystem) | Framework ligero de **señales** (patrón observador) para desacoplar sistemas. | 44 | MIT | 2023-12-28 | 14 |
| `Emu` [↗](https://github.com/DragoniteSpam/Emu) | Framework de interfaz pensado para **herramientas de edición** dentro del juego, no para el HUD del jugador. | 43 | MIT | 2026-02-18 | 94 |
| `LimeUI` [↗](https://github.com/Limekys/LimeUI) | Interfaz de usuario ligera y rápida de integrar. | 36 | MIT | 2026-08-29 | 61 |
| `GMUI` [↗](https://github.com/erkan612/GMUI) | Framework de interfaz de usuario por componentes. | 30 | MIT | 2026-08-10 | 46 |
| `GMUI-Framework` [↗](https://github.com/AlertStudios/GMUI-Framework) | Framework de interfaz para GameMaker. | 29 | MIT | 2021-07-20 | 861 |
| `Guido` [↗](https://github.com/JujuAdams/Guido) | Framework de GUI en **modo inmediato**, sencillo. *(📦 archivado)* | 24 | MIT | 2019-06-15 | 34 |
| `PXLUI` [↗](https://github.com/1pxlchibs/PXLUI) | Interfaz orientada a estética de píxel. | 19 | MIT | 2024-06-25 | 376 |
| `GMS2-UI-Library` [↗](https://github.com/nabilatsoulcade/GMS2-UI-Library) | Colección de scripts para implementar diseños de interfaz. | 17 | sin licencia | 2018-01-11 | 21 |
| `SimpleBook` [↗](https://github.com/Gizmo199/SimpleBook) | Framework de renderizado de **libros** dentro del juego. | 11 | sin licencia | 2026-05-07 | 22 |
| `MajorGUI_GML` [↗](https://github.com/erkan612/MajorGUI_GML) | Librería de GUI **jerárquica en modo retenido** basada en Canvas. | 9 | MIT | 2026-04-15 | 48 |
| `SimpleUI` [↗](https://github.com/evolutionleo/SimpleUI) | Interfaz mínima para prototipos y herramientas internas. | 9 | MIT | 2024-05-07 | 15 |
| `zitk` [↗](https://github.com/TandyRum1024/zitk) | Sucesor experimental de IMNOTGUI: interfaz en modo inmediato. | 6 | MIT | 2022-06-26 | 9 |
| `gooey` [↗](https://github.com/biyectivo/gooey) | Librería de **interfaz basada en sprites**: botones, paneles, listas y ventanas. 🆕 | 9 | MIT | 2025-12-16 | 165 |
| `Emu` [↗](https://github.com/DragoniteSpam/Emu) | Librería de **interfaz tipo Windows Forms**: la más completa para herramientas y editores internos. 🆕 | 43 | MIT | 2026-02-18 | 94 |

<a id="localizacion"></a>

### Localización y traducción

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `lexicon` [↗](https://github.com/tabularelf/lexicon) | Sistema de localización con ficheros de idioma y sustitución de variables. | 52 | MIT | 2026-07-11 | 219 |
| `polyglot` [↗](https://github.com/daikon-games/polyglot) | Carga de cadenas localizadas de forma muy simple. | 35 | propia | 2026-02-23 | 7 |
| `gm-i18n` [↗](https://github.com/CreativeHandOficial/gm-i18n) | Funciones de internacionalización para GMS 2.3+. | 21 | MIT | 2023-02-04 | 17 |
| `Localize` [↗](https://github.com/Kruger0/Localize) | Sistema de localización multi-idioma **sincronizado con Google Sheets**. Muy práctico si traduces con colaboradores. | 20 | MIT | 2026-08-12 | 60 |
| `small_pp_localization_tool` [↗](https://github.com/AntonBergaker/small_pp_localization_tool) | Herramienta de exportación a **hoja de cálculo** para pasar los textos a traductores. | 11 | MIT | 2026-01-23 | 3 |
| `GMLocalize2` [↗](https://github.com/DragoniteSpam/GMLocalize2) | Localización con **interfaz visual**. | 5 | sin licencia | 2022-07-05 | 0 |
| `gms2-mofile` [↗](https://github.com/pmarincak/gms2-mofile) | Cargador de ficheros **.mo** (gettext) para GameMaker. | 3 | propia | 2023-12-28 | 5 |

<a id="maquinas-de-estados"></a>

### Máquinas de estados

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `SnowState` [↗](https://github.com/sohomsahaun/SnowState) | **La máquina de estados finitos de referencia** en GameMaker (★178). Estados con eventos de entrada y salida, historial, herencia y transiciones. Si tu personaje tiene más de tres comportamientos, empieza aquí. | 178 | MIT | 2026-09-01 | 34 |
| `BehaviorTree` [↗](https://github.com/Gizmo199/BehaviorTree) | **Árbol de comportamiento** para IA de enemigos: más escalable que una máquina de estados cuando la IA se complica. | 14 | sin licencia | 2023-12-18 | 8 |
| `Pinocchio` [↗](https://github.com/JujuAdams/Pinocchio) | Sistema de **animación basado en estados**: liga la animación al estado sin duplicar lógica. | 10 | MIT | 2024-03-04 | 14 |
| `FastSM` [↗](https://github.com/JulianDicken/FastSM) | Máquina de estados minimalista y rápida. *(📦 archivado)* | 7 | MIT | 2024-02-16 | 3 |
| `FSM-AI-module` [↗](https://github.com/gmclan-org/FSM-AI-module) | Módulo de máquina de estados finitos orientado a IA. | 5 | MIT | 2021-09-21 | 14 |

<a id="matematicas"></a>

### Matemáticas, vectores y aleatoriedad

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `gmlinear2` [↗](https://github.com/dicksonlaw583/gmlinear2) | Álgebra lineal en GML: vectores, matrices y cuaterniones. | 17 | MIT | 2025-07-29 | 23 |
| `basic-quaternions` [↗](https://github.com/JujuAdams/basic-quaternions) | Cuaterniones para rotaciones 3D sin bloqueo de cardán. | 16 | MIT | 2026-07-08 | 48 |
| `gmlinear` [↗](https://github.com/dicksonlaw583/gmlinear) | Versión anterior de gmlinear (archivada). *(📦 archivado)* | 13 | MIT | 2019-04-21 | 1 |
| `PRNG-Functions` [↗](https://github.com/JujuAdams/PRNG-Functions) | Generadores pseudoaleatorios deterministas y reproducibles: imprescindible para roguelikes con semilla. | 6 | MIT | 2026-08-20 | 22 |
| `gmlinear-legacy` [↗](https://github.com/dicksonlaw583/gmlinear-legacy) | Versión heredada de gmlinear (archivada). *(📦 archivado)* | 6 | MIT | 2019-04-21 | 8 |
| `Macaw` [↗](https://github.com/DragoniteSpam/Macaw) | Generación de **ruido Perlin** para terreno, texturas y variación procedural. 🆕 | 2 | MIT | 2026-06-19 | 128 |

<a id="niveles-y-mapas"></a>

### Niveles, mapas y generación procedural

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `GMRoomLoader` [↗](https://github.com/GlebTsereteli/GMRoomLoader) | Carga rooms como si fueran prefabs, en tiempo de ejecución y en cualquier posición. Base para generación procedural con piezas dibujadas a mano. | 128 | MIT | 2026-08-17 | 74 |
| `LDtkParser` [↗](https://github.com/evolutionleo/LDtkParser) | Analizador de niveles **.ldtk** para GameMaker. LDtk es hoy el mejor editor de niveles externo para 2D. ⚠️ Más de un año sin *push* (reverificado 2026-09-07) — sigue siendo la mejor opción viva, pero revisa antes de depender de ella. | 63 | MIT | 2025-08-14 | 9 |
| `random-level-gen-gms2` [↗](https://github.com/GameMakerDiscord/random-level-gen-gms2) | Ejemplo de **generación aleatoria de niveles** al estilo *Nuclear Throne*. | 57 | MIT | 2018-03-03 | 12 |
| `gms2-destructible-terrain` [↗](https://github.com/niksudan/gms2-destructible-terrain) | **Terreno destructible** y con colisión, usando superficies y rejillas. | 31 | MIT | 2023-04-17 | 7 |
| `GM-RoomInspector` [↗](https://github.com/heygleeson/GM-RoomInspector) | Vuelca los datos de una room a **JSON** para leerlos fuera del IDE. | 10 | MIT | 2022-01-05 | 9 |
| `Random-Dungeon-Generator-GMS-2.3` [↗](https://github.com/BlaXun/Random-Dungeon-Generator-GMS-2.3) | Generador de mazmorras que combina cámaras definidas por el usuario. | 10 | sin licencia | 2020-06-30 | 24 |
| `Hotglue` [↗](https://github.com/JujuAdams/Hotglue) | Editor de niveles integrado en el propio juego, en tiempo de ejecución. | 8 | sin licencia | 2026-07-13 | 331 |
| `GMS2-Autotile-Converter` [↗](https://github.com/null-sharp/GMS2-Autotile-Converter) | Convierte tilesets externos al formato de **autotile** de GameMaker. 🆕 | 21 | MIT | 2020-07-05 | 0 |
| `PushEd` [↗](https://github.com/GameMakerDiscord/PushEd) | **Editor de niveles 2D/3D** externo para GameMaker, del Discord de la comunidad. 🆕 | 25 | MIT | 2025-12-28 | 521 |

<a id="particulas"></a>

### Partículas y efectos

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Dynamo` [↗](https://github.com/JujuAdams/Dynamo) | Sistema de partículas por código con una API más manejable que la nativa. | 36 | MIT | 2026-07-08 | 33 |
| `Pulse` [↗](https://github.com/Delfos1/Pulse) | Librería de **partículas** para GameMaker. | 23 | MIT | 2025-12-14 | 87 |
| `Burrn` [↗](https://github.com/FoxyOfJungle/Burrn) | Sistema de partículas que usa el **asset de partículas** integrado de GameMaker. *(📦 archivado)* | 17 | MIT | 2024-06-15 | 11 |
| `particles` [↗](https://github.com/GamemakerCasts/particles) | Sistema de partículas simple que **se limpia solo** (sin fugas de memoria). | 7 | MIT | 2022-08-21 | 7 |

<a id="pathfinding"></a>

### Pathfinding y navegación

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `A-Star-Pathing` [↗](https://github.com/helloalbertdang/A-Star-Pathing) | Librería de **A\*** escrita para integrarse sin configurar nada. | 9 | Apache-2.0 | 2021-02-06 | 6 |
| `dijkstra-graph` [↗](https://github.com/gmclan-org/dijkstra-graph) | Solución con el algoritmo de **Dijkstra** para el camino más corto en un grafo. | 6 | sin licencia | 2026-08-29 | 18 |
| `GMNav` [↗](https://github.com/erkan612/GMNav) | Framework de **pathfinding y navegación**. | 2 | MIT | 2026-08-31 | 47 |

<a id="red-y-multijugador"></a>

### Red y multijugador

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Warp` [↗](https://github.com/evolutionleo/Warp) | **Framework completo de multijugador** escrito en GameMaker y Node.js. La opción de la comunidad más completa y activa. | 149 | MIT | 2026-07-31 | 93 |
| `patchwire-gm` [↗](https://github.com/gm-core/patchwire-gm) | Red simplificada usando el servidor multijugador Patchwire. | 36 | MIT | 2020-09-13 | 10 |
| `MultiClient` [↗](https://github.com/tabularelf/MultiClient) | Lanza **varias instancias del juego a la vez** para probar red sin necesitar dos ordenadores. Imprescindible al desarrollar multijugador. | 31 | MIT | 2026-01-06 | 8 |
| `http.gml` [↗](https://github.com/Sidorakh/http.gml) | Envoltorio HTTP sencillo: recibir peticiones GET y subir ficheros desde GML. | 19 | MIT | 2026-08-29 | 15 |
| `GMNest` [↗](https://github.com/TimVN/GMNest) | Extensión de **Socket.IO** para juegos HTML5. | 2 | sin licencia | 2022-10-11 | 0 |
| `gm_boomers_networking` [↗](https://github.com/gmclan-org/gm_boomers_networking) | Red con los mismos nombres de función que el clásico **39dll**, pero con funciones nativas. Para portar código antiguo. | 2 | sin licencia | 2023-08-06 | 37 |
| `gm_networking` [↗](https://github.com/gmclan-org/gm_networking) | Ejemplo mínimo de red. Ideal para **entender** cómo funciona por debajo antes de usar un framework. | 2 | MIT | 2023-08-06 | 34 |

<a id="secuencias"></a>

### Secuencias y animación por línea de tiempo

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `DuplicateSequence.gml` [↗](https://github.com/KeeVeeGames/DuplicateSequence.gml) | **Copia profunda de una secuencia** para editarla en tiempo de ejecución. | 15 | MIT | 2024-09-06 | 3 |

<a id="shaders"></a>

### Shaders y postprocesado

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `gml-outline-shader-drawer` [↗](https://github.com/Grisgram/gml-outline-shader-drawer) | Dibujado de **contornos** (outline) con shader. | 26 | MIT | 2024-10-16 | 42 |
| `Bokeh` [↗](https://github.com/XorDev/Bokeh) | Shader de **bokeh** (desenfoque con forma de diafragma). | 19 | sin licencia | 2024-03-02 | 2 |
| `Chameleon` [↗](https://github.com/Lojemiru/Chameleon) | **Intercambio de paletas** rápido y fiable. Para variantes de color de un mismo sprite sin duplicar assets. | 16 | MIT | 2022-10-28 | 35 |
| `ColorMod` [↗](https://github.com/JujuAdams/ColorMod) | **Intercambio de paletas** del autor de Bulb, Scribble e Input. Más nuevo y más usado que Chameleon; misma licencia. | 27 | MIT | 2024-10-27 | 11 |
| `Xpanda` [↗](https://github.com/GameMakerDiscord/Xpanda) | Permite **`#include`** en shaders: reutilizar código GLSL entre ficheros. Imprescindible si escribes más de dos shaders. | 16 | MIT | 2026-05-05 | 42 |
| `1PassBlur` [↗](https://github.com/XorDev/1PassBlur) | Shader de **desenfoque en una sola pasada**. | 15 | sin licencia | 2026-01-15 | 5 |
| `GMS-Voronoi-Pixels` [↗](https://github.com/XorDev/GMS-Voronoi-Pixels) | Efecto de **píxeles de Voronoi**. | 14 | sin licencia | 2022-05-18 | 5 |
| `Fire-Fun` [↗](https://github.com/XorDev/Fire-Fun) | Bolas de fuego con shaders. | 12 | sin licencia | 2022-01-11 | 3 |
| `Shadertoy2GM` [↗](https://github.com/jfkn1ght/Shadertoy2GM) | Aplicación web que **convierte GLSL de Shadertoy** a GLSL ES de GameMaker, con el código de acompañamiento necesario. | 12 | sin licencia | 2026-03-12 | 0 |
| `Dual-Kawase` [↗](https://github.com/XorDev/Dual-Kawase) | Filtro de **desenfoque dual-kawase**: gaussiano de calidad a bajo coste. | 11 | sin licencia | 2024-02-20 | 9 |
| `Shady.gml` [↗](https://github.com/KeeVeeGames/Shady.gml) | **Preprocesador de shaders**: `#include` e inline para reutilizar código GLSL entre shaders. 🆕 | 28 | MIT | 2026-01-27 | 2 |
| `bktGlitchFilter` [↗](https://github.com/nkrapivin/bktGlitchFilter) | Shader de **glitch** configurable (desplazamiento RGB, ruido, bandas). 🆕 | 3 | — | 2021-11-03 | 0 |

<a id="sprites-y-animacion"></a>

### Sprites y animación

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Pixel-Art-Upscaling` [↗](https://github.com/JujuAdams/Pixel-Art-Upscaling) | Shader de **escalado de pixel art** para resoluciones incómodas (las que no son múltiplo exacto). | 36 | sin licencia | 2024-12-31 | 6 |
| `Collage` [↗](https://github.com/tabularelf/Collage) | Gestión de atlas de texturas y sprites generados en tiempo de ejecución. | 29 | MIT | 2026-07-26 | 123 |
| `GM-Animate` [↗](https://github.com/KormexGit/GM-Animate) | Sistema de animación de sprites. | 10 | MIT | 2026-08-18 | 25 |
| `AESnips` [↗](https://github.com/angelwire/AESnips) | Sistema de **reproducción de sprites**: recortes, secuencias y control de fotogramas. | 9 | MIT | 2025-08-04 | 0 |
| `conveyorbelt` [↗](https://github.com/imissmyfriends/conveyorbelt) | Exporta ficheros de **Aseprite** e importa los sprites en GameMaker automáticamente. | 7 | sin licencia | 2023-09-08 | 0 |
| `Splat` [↗](https://github.com/JujuAdams/Splat) | Utilidad de dibujo de manchas y decals. | 5 | MIT | 2026-07-28 | 13 |
| `phgen` [↗](https://github.com/squircledev/phgen) | Generador de **assets de marcador de posición** para prototipar sin arte. | 3 | sin licencia | 2021-11-16 | 3 |
| `gmParallax` [↗](https://github.com/TobySushi/gmParallax) | Fondos con desplazamiento por capas (parallax). | 2 | MIT | 2023-06-15 | 0 |

<a id="texto-y-tipografia"></a>

### Texto y tipografía

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Scribble` [↗](https://github.com/JujuAdams/Scribble) | El motor de texto de referencia en GameMaker: formato enriquecido, efectos por carácter, ajuste de línea, tipografías de mapa de bits y máquina de escribir. Si vas a dibujar algo más que `draw_text`, empieza aquí. | 415 | MIT | 2026-08-10 | 506 |
| `ScribbleJunior` [↗](https://github.com/JujuAdams/ScribbleJunior) | Versión reducida de Scribble para proyectos que solo necesitan texto con formato sin todo el peso de la librería grande. | 25 | MIT | 2026-07-16 | 61 |

<a id="tiempo-y-temporizadores"></a>

### Tiempo, temporizadores y bucle de juego

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `iota` [↗](https://github.com/JujuAdams/iota) | Bucle de lógica a paso fijo, independiente de los FPS reales. La solución correcta al problema de `delta_time`. | 48 | MIT | 2026-07-08 | 39 |
| `DoLater` [↗](https://github.com/JujuAdams/DoLater) | Ejecuta código diferido de forma segura: al final del step, tras N frames, o cuando se cumpla una condición. | 45 | MIT | 2026-06-07 | 16 |
| `GMMT` [↗](https://github.com/erkan612/GMMT) | *GameMaker Motion Toolkit*: framework de **tweens** fácil de usar. | 8 | MIT | 2026-08-09 | 35 |
| `GMTimeLine` [↗](https://github.com/TimVN/GMTimeLine) | Motor para implementar **oleadas de enemigos** con facilidad. | 7 | MIT | 2022-11-03 | 25 |
| `fuwafuwa` [↗](https://github.com/kemonologic/fuwafuwa) | Sistema de temporizadores completo y fácil de usar. | 6 | MIT | 2022-07-28 | 99 |
| `Agenda.gml` [↗](https://github.com/benal20/Agenda.gml) | Encadenado de *callbacks* al estilo promesa. | 4 | MIT | 2026-05-03 | 9 |
| `Stopwatch` [↗](https://github.com/Lojemiru/Stopwatch) | Sustituto de las **alarmas** de GameMaker, con más control. | 4 | MIT | 2022-10-28 | 4 |
| `STAGING` [↗](https://github.com/sdelaughter/STAGING) | Automatización de tareas secuenciadas para la **inicialización** del juego. | 3 | MIT | 2026-07-20 | 19 |
| `Timers` [↗](https://github.com/nommiin/Timers) | Implementación de `setTimeout` y `setInterval` de JavaScript. | 3 | MIT | 2020-04-24 | 4 |
| `FrogAlarms` [↗](https://github.com/colmeye/FrogAlarms) | Sistema de alarmas alternativo, sencillo. | 0 | sin licencia |  | 1 |

<a id="utilidades"></a>

### Utilidades generales de GML

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `catspeak-lang` [↗](https://github.com/katsaii/catspeak-lang) | **Lenguaje de modding multiplataforma** para juegos de GameMaker. La opción seria si quieres que tus jugadores escriban scripts. ⚠️ El desarrollo se ha movido a Codeberg. | 133 | propia | 2026-08-19 | 0 |
| `GameMakerLibraries` [↗](https://github.com/JujuAdams/GameMakerLibraries) | Índice mantenido por Juju Adams de librerías de la comunidad. Punto de partida para descubrir más. | 123 | sin licencia | 2022-08-04 | 0 |
| `scripts` [↗](https://github.com/gmlscripts/scripts) | El archivo histórico de gmlscripts.com: cientos de funciones de matemáticas, geometría, colisiones y dibujo, cada una con su demo. Mucho es de la era GMS 1.x, pero los algoritmos siguen valiendo. | 85 | propia | 2026-07-24 | 263 |
| `SSave` [↗](https://github.com/stoozey/SSave) | Sistema de **guardado** sencillo. | 44 | sin licencia | 2025-10-13 | 17 |
| `HelpfulGMLScripts` [↗](https://github.com/PixelatedPope/HelpfulGMLScripts) | Colección de scripts de PixelatedPope, el autor de la serie de cámaras y resolución. | 37 | sin licencia | 2026-07-24 | 159 |
| `DDDEditorGMS2` [↗](https://github.com/DragoniteSpam/DDDEditorGMS2) | **Editor de juego de propósito general hecho en GameMaker.** Demuestra hasta dónde llega el motor para construir herramientas. | 34 | MIT | 2026-08-31 | 570 |
| `GML-OOP` [↗](https://github.com/Mtax-Development/GML-OOP) | Capa de programación orientada a objetos sobre GML: envuelve las estructuras nativas en constructores. | 34 | propia | 2026-08-29 | 48 |
| `FAST` [↗](https://github.com/Hyomoto/FAST) | Librería suplementaria de GML de uso general. | 31 | MIT | 2026-02-23 | 57 |
| `gm-seedpod` [↗](https://github.com/daikon-games/gm-seedpod) | Colección de funciones útiles de Daikon Games. | 29 | CC0-1.0 | 2023-07-18 | 3 |
| `Figgy` [↗](https://github.com/GlebTsereteli/Figgy) | Sistema de configuración y ajustes con persistencia. | 27 | MIT | 2026-08-10 | 344 |
| `GMLodash` [↗](https://github.com/DatZach/GMLodash) | Port de la librería **Lodash** de JavaScript a GML. | 25 | propia | 2021-11-28 | 2 |
| `Canvas` [↗](https://github.com/tabularelf/Canvas) | **Solución no volátil para superficies**: las superficies de GameMaker se pierden sin avisar; Canvas guarda su contenido y lo restaura. | 22 | MIT | 2026-04-11 | 37 |
| `game-maker-scripts` [↗](https://github.com/adam-rumpf/game-maker-scripts) | Colección de funciones de utilidad y matemáticas. | 17 | MIT | 2023-06-12 | 55 |
| `Broadcast` [↗](https://github.com/JulianDicken/Broadcast) | Librería de **manejo de eventos** (bus de mensajes) escrita en GML: desacopla los sistemas del juego para que no se llamen entre sí directamente. *(📦 archivado)* | 16 | MIT | 2022-07-04 | 7 |
| `GMLiteSearch` [↗](https://github.com/erkan612/GMLiteSearch) | **Motor de búsqueda ligero** para dentro del juego. | 14 | MIT | 2026-08-31 | 26 |
| `GameMakerScaffolding` [↗](https://github.com/babaganosch/GameMakerScaffolding) | Plantilla de proyecto con estructura ya montada. | 13 | MIT | 2023-12-28 | 67 |
| `Gumshoe` [↗](https://github.com/JujuAdams/Gumshoe) | Función de **búsqueda profunda de ficheros**. | 12 | MIT | 2024-03-04 | 3 |
| `polarca` [↗](https://github.com/VitorEstevam/polarca) | Utilidades de coordenadas polares. | 12 | MIT | 2024-03-11 | 10 |
| `CoreExtension` [↗](https://github.com/blueburncz/CoreExtension) | Colección de librerías **CC0** (dominio público) para GameMaker. *(📦 archivado)* | 11 | CC0-1.0 | 2022-01-27 | 80 |
| `RunGML` [↗](https://github.com/sdelaughter/RunGML) | Lenguaje tipo Lisp embebido en GameMaker y programado en JSON. | 10 | MIT | 2026-07-03 | 43 |
| `Tweeny` [↗](https://github.com/Kruger0/Tweeny) | Motor de animación por **tweens**. | 8 | MIT | 2026-08-15 | 32 |
| `GMVex` [↗](https://github.com/erkan612/GMVex) | **Framework de vectores** para GameMaker. | 7 | MIT | 2026-07-30 | 25 |
| `RenderStack` [↗](https://github.com/FoxyOfJungle/RenderStack) | Gestiona el renderizado en **capas virtuales ordenadas y configurables**. | 7 | MIT | 2025-12-17 | 13 |
| `auto-framer` [↗](https://github.com/mstop4/auto-framer) | Framework que **redimensiona la vista del juego automáticamente** según la pantalla y la ventana. Resuelve el problema clásico de resolución en móvil. | 7 | sin licencia | 2021-05-02 | 13 |
| `gml-highscorer` [↗](https://github.com/Grisgram/gml-highscorer) | **Puntuaciones máximas y trofeos** para tu juego. | 7 | MIT | 2024-09-01 | 28 |
| `PNGEncoder` [↗](https://github.com/JujuAdams/PNGEncoder) | Escribe ficheros PNG desde GML sin extensiones nativas. | 4 | sin licencia | 2026-07-28 | 3 |
| `JITSpeak` [↗](https://github.com/BenjaminUrquhart/JITSpeak) | Compilador *just-in-time* de Catspeak a bytecode de la VM de GameMaker. | 3 | MIT | 2025-11-08 | 71 |
| `Ugg` [↗](https://github.com/JujuAdams/Ugg) | Utilidades varias de GML de uso frecuente. | 3 | MIT | 2025-11-13 | 85 |
| `OSAB` [↗](https://github.com/matty147/OSAB) | Colección amplia de sistemas de juego listos para usar. | 2 | MIT | 2026-03-30 | 226 |
| `GML-Assistant` [↗](https://github.com/RMDomingos20/GML-Assistant) | Utilidades de asistencia a la escritura de GML. | 1 | MIT | 2026-08-11 | 0 |
| `FreeGMScripts` [↗](https://github.com/vphoton/FreeGMScripts) | Colección libre de scripts de GML. | 0 | sin licencia |  | 0 |
| `Moniker` [↗](https://github.com/JujuAdams/Moniker) | Nombres generados proceduralmente. | 0 | MIT | 2026-08-16 | 22 |
| `handytools` [↗](https://github.com/JujuAdams/handytools) | Utilidades variadas de uso frecuente. | 0 | sin licencia |  | 778 |

<a id="extensiones-oficiales"></a>

## Extensiones oficiales de YoYo Games

Los repositorios `GMEXT-*`: integración con tiendas, servicios y SDK nativos. Contienen la **API de GML** que expone cada extensión y su documentación. Los binarios nativos no se han copiado.

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `GMEXT-Steamworks` [↗](https://github.com/YoYoGames/GMEXT-Steamworks) | Extensión oficial de **Steamworks**: logros, estadísticas, nube, UGC (Workshop), amigos y superposición de Steam. | 123 | propia | 2026-08-25 | 275 |
| `GMEXT-FMOD` [↗](https://github.com/YoYoGames/GMEXT-FMOD) | Extensión oficial de **FMOD Studio**: audio adaptativo profesional, el estándar de la industria para música interactiva. | 74 | Apache-2.0 | 2026-08-12 | 240 |
| `GMEXT-Twitch` [↗](https://github.com/YoYoGames/GMEXT-Twitch) | Extensión oficial de **Twitch**: integración con el chat y con la API del canal. | 21 | Apache-2.0 | 2025-12-29 | 283 |
| `GMEXT-Firebase` [↗](https://github.com/YoYoGames/GMEXT-Firebase) | Extensión oficial de **Firebase**: autenticación, Firestore, base de datos en tiempo real, Cloud Functions y analíticas. | 20 | propia | 2026-09-01 | 412 |
| `GMEXT-GDK` [↗](https://github.com/YoYoGames/GMEXT-GDK) | Extensión oficial del **GDK de Microsoft**: servicios de Xbox y de la Microsoft Store. | 20 | propia | 2026-08-14 | 144 |
| `GMEXT-EpicOnlineServices` [↗](https://github.com/YoYoGames/GMEXT-EpicOnlineServices) | Extensión oficial de **Epic Online Services**: cuentas, logros, amigos y servicios cruzados de Epic. | 16 | propia | 2026-08-25 | 215 |
| `GMEXT-AdMob` [↗](https://github.com/YoYoGames/GMEXT-AdMob) | Extensión oficial de **AdMob** (Google): anuncios en móvil. | 14 | propia | 2026-08-25 | 40 |
| `GMEXT-Discord` [↗](https://github.com/YoYoGames/GMEXT-Discord) | Extensión oficial de **Discord**, actualizada en junio de 2026 con el Discord Social SDK. | 13 | propia | 2026-08-25 | 58 |
| `GMEXT-MobileUtils` [↗](https://github.com/YoYoGames/GMEXT-MobileUtils) | Extensión oficial con utilidades varias de móvil (vibración, red, permisos, compartir). | 13 | propia | 2026-08-25 | 69 |
| `GMEXT-GooglePlayBilling` [↗](https://github.com/YoYoGames/GMEXT-GooglePlayBilling) | Extensión oficial de **compras integradas** en Google Play. | 12 | propia | 2026-08-28 | 26 |
| `GMEXT-mod.io` [↗](https://github.com/YoYoGames/GMEXT-mod.io) | Extensión oficial de **mod.io**: soporte de mods multiplataforma para tu juego. | 12 | propia | 2026-04-24 | 136 |
| `GMEXT-GOG` [↗](https://github.com/YoYoGames/GMEXT-GOG) | Extensión oficial de **GOG Galaxy**. | 10 | propia | 2026-04-24 | 70 |
| `GMEXT-GooglePlayServices` [↗](https://github.com/YoYoGames/GMEXT-GooglePlayServices) | Extensión oficial de **Google Play Services**: logros, tablas de clasificación y guardado en la nube. | 10 | propia | 2026-08-25 | 97 |
| `GMEXT-Bluetooth` [↗](https://github.com/YoYoGames/GMEXT-Bluetooth) | Extensión oficial de **Bluetooth** para móvil. | 8 | Apache-2.0 | 2026-08-31 | 87 |
| `GMEXT-GX.games` [↗](https://github.com/YoYoGames/GMEXT-GX.games) | Extensión oficial de **GX.games**, la plataforma de Opera. | 8 | propia | 2025-06-20 | 36 |
| `GMEXT-Photon` [↗](https://github.com/YoYoGames/GMEXT-Photon) | Extensión oficial de **Photon**: multijugador en tiempo real con salas, emparejamiento, chat de texto y **chat de voz**. Publicada en julio de 2026. | 8 | propia | 2026-08-25 | 72 |
| `GMEXT-Elements` [↗](https://github.com/YoYoGames/GMEXT-Elements) | Extensión oficial de componentes de plataforma. | 7 | propia | 2026-08-26 | 38 |
| `GMEXT-GameCenter` [↗](https://github.com/YoYoGames/GMEXT-GameCenter) | Extensión oficial de **Game Center**: logros y clasificaciones en iOS y macOS. | 7 | propia | 2026-08-25 | 65 |
| `GMEXT-GameJolt` [↗](https://github.com/YoYoGames/GMEXT-GameJolt) | Extensión oficial de la **API de Game Jolt**. | 7 | Apache-2.0 | 2025-11-20 | 120 |
| `GMEXT-MobileReview` [↗](https://github.com/YoYoGames/GMEXT-MobileReview) | Extensión oficial para pedir al jugador una **valoración en la tienda** sin sacarlo del juego. | 7 | propia | 2026-08-25 | 21 |
| `GMEXT-WebView` [↗](https://github.com/YoYoGames/GMEXT-WebView) | Extensión oficial para incrustar una **vista web** dentro del juego. | 7 | propia | 2026-08-04 | 12 |
| `GMEXT-AppleIAP` [↗](https://github.com/YoYoGames/GMEXT-AppleIAP) | Extensión oficial de **compras integradas de Apple** (StoreKit). | 5 | Apache-2.0 | 2026-08-25 | 44 |
| `GMEXT-GooglePlayLicensing` [↗](https://github.com/YoYoGames/GMEXT-GooglePlayLicensing) | Extensión oficial de verificación de licencia de Google Play. | 5 | propia | 2026-05-04 | 9 |
| `GMEXT-Interhaptics-Main` [↗](https://github.com/YoYoGames/GMEXT-Interhaptics-Main) | Extensión oficial de **Interhaptics**: retroalimentación háptica avanzada. | 5 | Apache-2.0 | 2026-04-24 | 34 |
| `GMEXT-GooglePlayPassLicensing` [↗](https://github.com/YoYoGames/GMEXT-GooglePlayPassLicensing) | Extensión oficial de licencias de **Google Play Pass**. | 4 | propia | 2026-04-24 | 9 |
| `GMEXT-AppTrackingTransparency` [↗](https://github.com/YoYoGames/GMEXT-AppTrackingTransparency) | Extensión oficial de **App Tracking Transparency** de Apple: pedir permiso de seguimiento. Obligatoria en iOS. | 3 | propia | 2026-06-18 | 9 |
| `GMEXT-GoogleSignIn` [↗](https://github.com/YoYoGames/GMEXT-GoogleSignIn) | Extensión oficial de **inicio de sesión con Google**. | 3 | propia | 2026-06-30 | 16 |
| `GMEXT-InAppUpdate` [↗](https://github.com/YoYoGames/GMEXT-InAppUpdate) | Extensión oficial de **actualización dentro de la app** en Android. | 3 | Apache-2.0 | 2026-07-31 | 13 |
| `GMEXT-AppleSignIn` [↗](https://github.com/YoYoGames/GMEXT-AppleSignIn) | Extensión oficial de **Iniciar sesión con Apple**. | 2 | propia | 2026-06-30 | 20 |
| `GMEXT-CrazyGames` [↗](https://github.com/YoYoGames/GMEXT-CrazyGames) | Extensión oficial del portal web **CrazyGames**. | 2 | propia | 2026-04-24 | 68 |
| `GMEXT-GooglePlayInstant` [↗](https://github.com/YoYoGames/GMEXT-GooglePlayInstant) | Extensión oficial de **Google Instant Games** (jugar sin instalar). | 2 | Apache-2.0 | 2025-10-01 | 9 |
| `GMEXT-H5GamesAds` [↗](https://github.com/YoYoGames/GMEXT-H5GamesAds) | Extensión oficial de **anuncios para juegos HTML5**. | 2 | propia | 2025-06-20 | 11 |
| `GMEXT-IronSource` [↗](https://github.com/YoYoGames/GMEXT-IronSource) | Extensión oficial de **ironSource**. ⚠️ Sustituida por LevelPlay. | 2 | propia | 2025-06-13 | 25 |
| `GMEXT-MLKit` [↗](https://github.com/YoYoGames/GMEXT-MLKit) | Extensión oficial de **aprendizaje automático en dispositivo** (visión y texto). Es la **única extensión oficial de IA** que existe. | 2 | Apache-2.0 | 2026-08-25 | 26 |
| `GMEXT-Adjust` [↗](https://github.com/YoYoGames/GMEXT-Adjust) | Extensión oficial de **Adjust**: atribución de instalaciones y analíticas de campaña. | 1 | Apache-2.0 | 2025-08-26 | 7 |
| `GMEXT-HuaweiPaidApps` [↗](https://github.com/YoYoGames/GMEXT-HuaweiPaidApps) | Extensión oficial de **Huawei AppGallery** para aplicaciones de pago. | 1 | Apache-2.0 | 2026-06-19 | 8 |
| `GMEXT-DeclaredAgeRange` [↗](https://github.com/YoYoGames/GMEXT-DeclaredAgeRange) | Extensión oficial de **declaración de rango de edad**. 🆕 Requisito nuevo de las tiendas. | 0 | propia | 2026-08-25 | 8 |
| `GMEXT-Facebook` [↗](https://github.com/YoYoGames/GMEXT-Facebook) | Extensión oficial de **Facebook**: inicio de sesión y compartir. | 0 | Apache-2.0 | 2026-08-27 | 40 |
| `GMEXT-GooglePlayIntegrity` [↗](https://github.com/YoYoGames/GMEXT-GooglePlayIntegrity) | Extensión oficial de **Play Integrity**: comprueba que la app y el dispositivo no están manipulados. | 0 | propia | 2026-08-25 | 9 |
| `GMEXT-LevelPlay` [↗](https://github.com/YoYoGames/GMEXT-LevelPlay) | Extensión oficial de **LevelPlay** (mediación de anuncios de Unity/ironSource). **Sustituye a la de ironSource**: si empiezas hoy, usa esta. | 0 | propia | 2026-08-26 | 13 |
| `GMEXT-Medal` [↗](https://github.com/YoYoGames/GMEXT-Medal) | Extensión oficial de **Medal.tv**: grabación y compartición de clips de partida. | 0 | propia | 2026-08-26 | 13 |
| `GMEXT-OperaAds` [↗](https://github.com/YoYoGames/GMEXT-OperaAds) | Extensión oficial de **Opera Ads**, para GX.games. | 0 | propia | 2026-08-25 | 25 |
| `GMEXT-PlayAgeSignals` [↗](https://github.com/YoYoGames/GMEXT-PlayAgeSignals) | Extensión oficial de **señales de edad de Google Play**. 🆕 Requisito nuevo. | 0 | propia | 2026-08-25 | 13 |
| `GMEXT-Reddit` [↗](https://github.com/YoYoGames/GMEXT-Reddit) | Extensión oficial de **Reddit (Devvit)**. Reddit es un target nuevo de 2026. | 0 | Apache-2.0 | 2026-08-14 | 14 |

<a id="juegos-y-motores"></a>

## Juegos y motores de referencia

Proyectos completos hechos con GameMaker, con su código fuente. Sirven para ver **cómo se estructura de verdad** un juego grande. Solo se ha copiado el código y la documentación, no los gráficos ni el audio.

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `Pixel-Composer` [↗](https://github.com/Ttanasart-pt/Pixel-Composer) | Editor nodal de gráficos procedurales hecho **en** GameMaker. La demostración más ambiciosa de que se pueden construir herramientas complejas con el motor. | 1354 | MIT | 2026-08-29 | 2096 |
| `NoteBlockStudio` [↗](https://github.com/OpenNBS/NoteBlockStudio) | Editor musical hecho con GameMaker. | 1011 | MIT | 2026-08-21 | 414 |
| `Mine-imator` [↗](https://github.com/stuffbydavid/Mine-imator) | Herramienta de animación 3D hecha con GameMaker. Referencia de 3D y de interfaz compleja. | 248 | sin licencia | 2026-09-01 | 2067 |
| `SpelunkyClassicHD` [↗](https://github.com/yancharkin/SpelunkyClassicHD) | Reimplementación del Spelunky clásico. Excelente referencia de generación procedural por salas. | 219 | propia | 2026-08-25 | 1353 |
| `UndertaleEngine` [↗](https://github.com/TML233/UndertaleEngine) | Recreación del motor de Undertale: diálogos, combate por turnos con esquiva en tiempo real. | 181 | MIT | 2026-08-07 | 532 |
| `FVM-Reborn` [↗](https://github.com/Spring-SG/FVM-Reborn) | Proyecto de gran tamaño hecho con GameMaker. | 177 | GPL-3.0 | 2026-08-30 | 1882 |
| `OrbinautFramework` [↗](https://github.com/TrianglyRU/OrbinautFramework) | Motor completo de plataformas al estilo Sonic clásico: física de pendientes, bucles y velocidad. La referencia si haces un plataformas rápido. | 126 | sin licencia | 2026-08-20 | 475 |
| `Gang-Garrison-2` [↗](https://github.com/Gang-Garrison-2/Gang-Garrison-2) | Shooter multijugador 2D estilo Team Fortress. Uno de los proyectos abiertos más veteranos hechos con GameMaker. | 119 | propia | 2026-07-26 | 330 |
| `DeltaruneChinese` [↗](https://github.com/gm3dr/DeltaruneChinese) | Traducción de Deltarune. Referencia de localización y de estructura de un juego comercial. | 95 | sin licencia | 2026-08-26 | 221 |
| `HotlineMiami.gmx` [↗](https://github.com/Pi0h1/HotlineMiami.gmx) | Proyecto estilo Hotline Miami en formato .gmx (GameMaker antiguo). Valor histórico y de referencia de IA de enemigos. | 82 | sin licencia | 2026-07-28 | 425 |
| `nt-recreated-public` [↗](https://github.com/toarch7/nt-recreated-public) | Recreación de Nuclear Throne. Referencia de *game feel*, cámara y combate twin-stick. | 82 | GPL-3.0 | 2026-08-19 | 2422 |
| `tldr-engine` [↗](https://github.com/tweenko/tldr-engine) | Motor de plataformas moderno y bien estructurado. | 82 | MIT | 2026-08-19 | 1039 |
| `Harmony-Framework` [↗](https://github.com/UltraRing/Harmony-Framework) | Framework de juego con arquitectura por sistemas. | 81 | MIT | 2026-08-29 | 371 |
| `ChapterMaster` [↗](https://github.com/Adeptus-Dominus/ChapterMaster) | Juego de estrategia y gestión de gran alcance. Referencia de sistemas complejos de datos y UI. | 72 | sin licencia | 2026-09-01 | 593 |
| `Kirby-Soft-and-Wet` [↗](https://github.com/MegaStrimp/Kirby-Soft-and-Wet) | Plataformas fan de Kirby, con sistemas de habilidades. | 65 | sin licencia | 2026-08-31 | 1040 |
| `MegamixEngine` [↗](https://github.com/MegamixEngine/MegamixEngine) | Motor de plataformas estilo Mega Man, muy completo y documentado. | 50 | sin licencia | 2026-07-30 | 490 |
| `renex2-engine` [↗](https://github.com/omicronrex/renex2-engine) | Motor de plataformas de acción. | 36 | propia | 2026-07-29 | 969 |
| `DyNode` [↗](https://github.com/NordLandeW/DyNode) | Juego de ritmo con editor de niveles. Referencia de sincronización con música y de herramientas internas. | 30 | MIT | 2026-08-22 | 435 |
| `Pizza-Tower-EXtracted` [↗](https://github.com/setupwitch/Pizza-Tower-EXtracted) | Código extraído de Pizza Tower. Referencia real de un juego comercial de éxito hecho con GameMaker. | 25 | sin licencia | 2026-07-28 | 10634 |
| `AM2R-Re-Splashed` [↗](https://github.com/AbyssalCreature/AM2R-Re-Splashed) | Trabajo sobre AM2R (metroidvania). Referencia de estructura de un metroidvania grande. | 22 | propia | 2026-07-22 | 135 |
| `Undertale-Engine-modded-by-Zhazha` [↗](https://github.com/onezhazha233/Undertale-Engine-modded-by-Zhazha) | Variante ampliada del motor de Undertale. | 21 | sin licencia | 2026-08-30 | 800 |

<a id="plantillas-y-ejemplos"></a>

## Plantillas, ejemplos y utilidades oficiales

Proyectos de ejemplo, prefabs oficiales, el framework de tests y las herramientas de YoYo Games.

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `GameMaker-HTML5` [↗](https://github.com/YoYoGames/GameMaker-HTML5) | **El runtime de HTML5**, en abierto. Útil para entender qué se puede y qué no en exportaciones web. | 325 | propia | 2026-09-01 | 0 |
| `3D-2D` [↗](https://github.com/YoYoGames/3D-2D) | Ejemplo oficial de cómo **mezclar 3D y 2D** en la misma escena. | 48 | propia | 2023-03-27 | 184 |
| `YourWorld` [↗](https://github.com/YoYoGames/YourWorld) | Mundo cenital de código abierto escrito con GameMaker: Studio. Ejemplo oficial antiguo pero completo. | 45 | sin licencia | 2017-05-04 | 133 |
| `gm-cli` [↗](https://github.com/YoYoGames/gm-cli) | **El CLI oficial de GameMaker.** Crear, ejecutar, compilar y empaquetar proyectos desde terminal, consultar el manual sin conexión y manipular recursos. Es la herramienta central de esta biblioteca. | 39 | Apache-2.0 | 2026-08-17 | 0 |
| `GameMakerStudio_ExtensionExample` [↗](https://github.com/YoYoGames/GameMakerStudio_ExtensionExample) | Ejemplo oficial mínimo de una extensión. | 34 | sin licencia | 2023-03-29 | 0 |
| `GMRT-Beta` [↗](https://github.com/YoYoGames/GMRT-Beta) | Repositorio de seguimiento de bugs del **runtime nuevo (GMRT)**. Aquí se ve qué funciona y qué no en la Beta 0.21. | 33 | sin licencia | 2026-05-01 | 54 |
| `GM-ExtensionGenerator` [↗](https://github.com/YoYoGames/GM-ExtensionGenerator) | Herramienta oficial que **genera el esqueleto de una extensión** nativa. | 26 | Apache-2.0 | 2026-08-27 | 1 |
| `GM-TestFramework` [↗](https://github.com/YoYoGames/GM-TestFramework) | **El framework de pruebas oficial de YoYo Games**, el que usa el propio equipo del motor. Es por donde deberías empezar si quieres tests. | 25 | propia | 2026-08-25 | 475 |
| `GM3D-Samples` [↗](https://github.com/YoYoGames/GM3D-Samples) | Proyectos de ejemplo **3D** oficiales. | 13 | MIT | 2026-08-20 | 27 |
| `GM-GPUTextureCompression` [↗](https://github.com/YoYoGames/GM-GPUTextureCompression) | Demo oficial de **compresión de texturas en GPU**. | 11 | Apache-2.0 | 2025-07-14 | 105 |
| `GM-RedditDemo` [↗](https://github.com/YoYoGames/GM-RedditDemo) | Demo oficial del target **Reddit (Devvit)**. | 4 | Apache-2.0 | 2026-02-09 | 14 |
| `pfb-UserInterface` [↗](https://github.com/YoYoGames/pfb-UserInterface) | **Prefab oficial**: componentes básicos de interfaz. | 3 | MIT | 2026-07-02 | 62 |
| `GameMakerRedditTemplate` [↗](https://github.com/YoYoGames/GameMakerRedditTemplate) | Plantilla oficial de proyecto WASM para **Reddit**. | 1 | propia | 2026-01-14 | 0 |
| `GM-OpenAPIGenerator` [↗](https://github.com/YoYoGames/GM-OpenAPIGenerator) | Herramienta oficial que **genera un cliente en GML** a partir de una especificación OpenAPI. Para hablar con tu backend REST sin escribir el envoltorio. | 0 | Apache-2.0 | 2026-08-26 | 0 |
| `Guides` [↗](https://github.com/YoYoGames/Guides) | Guías oficiales de YoYo Games. | 0 | sin licencia | 2024-08-20 | 0 |
| `ImGUI-Sample` [↗](https://github.com/YoYoGames/ImGUI-Sample) | Proyecto de ejemplo de **Dear ImGui** dentro de GameMaker: interfaces de herramientas internas. | 0 | MIT | 2026-07-30 | 3 |
| `pfb-Inventory` [↗](https://github.com/YoYoGames/pfb-Inventory) | **Prefab oficial**: sistema de inventario básico. Los prefabs son la novedad de 2026 para reutilizar piezas completas. | 0 | MIT | 2026-06-03 | 23 |
| `pfb-MiniMap` [↗](https://github.com/YoYoGames/pfb-MiniMap) | **Prefab oficial**: minimapa. | 0 | MIT | 2026-05-12 | 8 |

<a id="herramientas"></a>

## Herramientas del ecosistema

Programas que rodean a GameMaker sin ser librerías de GML.

| Repositorio | Qué es | ★ | Licencia | Último cambio | `.gml` |
|---|---|---:|---|---|---:|
| `GMEdit` [↗](https://github.com/YellowAfterlife/GMEdit) | Editor de código alternativo para GameMaker, con mejoras de autocompletado y navegación. No es una librería: es una herramienta externa. | 369 | MIT | 2026-07-22 | 146 |
| `YYToolkit` [↗](https://github.com/AurieFramework/YYToolkit) | Herramienta de instrumentación en tiempo de ejecución para juegos ya compilados de GameMaker. Contexto de ingeniería inversa/modding. | 133 | AGPL-3.0 | 2026-03-03 | 0 |
| `GameMaker-Bugs` [↗](https://github.com/YoYoGames/GameMaker-Bugs) | **El rastreador oficial de bugs.** Búscalo aquí antes de perder una tarde con un fallo que ya está reportado. Su wiki tiene los requisitos de SDK por plataforma. | 82 | sin licencia | 2026-08-27 | 0 |

## Repositorios catalogados pero no descargados

| Repositorio | Motivo |
|---|---|
| [aseprite/aseprite](https://github.com/aseprite/aseprite) | editor de pixel art en C++, no es GameMaker |
| [mapeditor/tiled](https://github.com/mapeditor/tiled) | editor de mapas en C++, no es GameMaker |
| [LibreSprite/LibreSprite](https://github.com/LibreSprite/LibreSprite) | fork de Aseprite en C++, no es GameMaker |
| [YoYoGames/GameMaker-Manual](https://github.com/YoYoGames/GameMaker-Manual) | ya cubierto por el espejo del manual (09) |
| [YoYoGames/GameMaker-Manual-ES](https://github.com/YoYoGames/GameMaker-Manual-ES) | ya cubierto por el espejo del manual en español (09) |
| [YoYoGames/GameMaker-Manual-DE](https://github.com/YoYoGames/GameMaker-Manual-DE) | traducción a otro idioma, fuera de alcance |
| [YoYoGames/GameMaker-Manual-FR](https://github.com/YoYoGames/GameMaker-Manual-FR) | traducción a otro idioma, fuera de alcance |
| [YoYoGames/GameMaker-Manual-IT](https://github.com/YoYoGames/GameMaker-Manual-IT) | traducción a otro idioma, fuera de alcance |
| [YoYoGames/GameMaker-Manual-JA](https://github.com/YoYoGames/GameMaker-Manual-JA) | traducción a otro idioma, fuera de alcance |
| [YoYoGames/GameMaker-Manual-KO](https://github.com/YoYoGames/GameMaker-Manual-KO) | traducción a otro idioma, fuera de alcance |
| [YoYoGames/GameMaker-Manual-PL](https://github.com/YoYoGames/GameMaker-Manual-PL) | traducción a otro idioma, fuera de alcance |
| [YoYoGames/GameMaker-Manual-PT-BR](https://github.com/YoYoGames/GameMaker-Manual-PT-BR) | traducción a otro idioma, fuera de alcance |
| [YoYoGames/GameMaker-Manual-RU](https://github.com/YoYoGames/GameMaker-Manual-RU) | traducción a otro idioma, fuera de alcance |
| [YoYoGames/GameMaker-Manual-ZH](https://github.com/YoYoGames/GameMaker-Manual-ZH) | traducción a otro idioma, fuera de alcance |
| [YoYoGames/dpdeploy](https://github.com/YoYoGames/dpdeploy) | abandonado en 2020, sin valor de referencia |
| [NuxiiGit/disarm](https://github.com/NuxiiGit/disarm) | El repositorio ya no existe (404 el 01-09-2026) |

<a id="novedades-2026"></a>

## Novedades 2025-2026 (auditoría del 2 de septiembre)

Repos recientes que faltaban, encontrados en una auditoría del ecosistema y **verificados en vivo**.
El detalle de las herramientas de IA está en [`07 · IA y GameMaker §6 bis.2`](../07%20-%20Ecosistema/14%20-%20IA%20y%20GameMaker.md).

**IA / MCP / agentes** (`librerias/ia-y-mcp/`):

| Repo | Qué es | Licencia |
|---|---|---|
| [`gamemaker-mcp`](https://github.com/yearningss/gamemaker-mcp) | Servidor MCP project-aware (~190 tools): análisis GML, refactor, builds | MIT |
| [`GameMaker-MCP-Server`](https://github.com/darkw3bb/GameMaker-MCP-Server) | Servidor MCP para Cursor | NOASSERTION |
| [`gm-forge-mcp`](https://github.com/nicklesimba/gm-forge-mcp) | Servidor MCP para crear/editar proyectos | MIT |
| [`gamemaker-skills`](https://github.com/leihaht/gamemaker-skills) | Skills de Claude Code para GMS2/GML | MIT |

**Tooling / editor / build** (`librerias/herramientas-externas/`):

| Repo | Qué es | Licencia |
|---|---|---|
| [`gamemaker-typescript`](https://github.com/OleksandrDemian/gamemaker-typescript) | Transpila TypeScript → GML | MIT |
| [`GML-formatter`](https://github.com/GanjaViruss/GML-formatter) | Formateador de GML offline | MIT |
| [`gml_lsp`](https://github.com/Okerew/gml_lsp) | Servidor LSP para GML *(archivado)* | MIT |
| [`GMEdit-Constructor`](https://github.com/thennothinghappened/GMEdit-Constructor) | Plugin de GMEdit que compila con Igor | MIT |
| [`GMSync`](https://github.com/Atennebris/GMSync) | Live-edit de GMS2 desde VS Code | NOASSERTION |
| [`gms2-ios-builder`](https://github.com/yearningss/gms2-ios-builder) | CLI GMS2 → Xcode → `.ipa` vía GitHub Actions | MIT |
| [`GameMakerCompanion`](https://github.com/Mtax-Development/GameMakerCompanion) | App companion + Discord Rich Presence | NOASSERTION |
| [`GM2Godot`](https://github.com/Infiland/GM2Godot) | Convierte proyectos GameMaker → Godot | Apache-2.0 |
| [`awesome-gamemaker`](https://github.com/bytecauldron/awesome-gamemaker) | Lista curada de referencia (501★) | CC0-1.0 |

**Frameworks y utilidades GML** (`librerias/utilidades/`):

| Repo | Qué es | Licencia |
|---|---|---|
| [`gml-raptor`](https://github.com/Grisgram/gml-raptor) | Framework integral de juego (61★) | NOASSERTION |
| [`gm-community-toolbox`](https://github.com/Alphish/gm-community-toolbox) | Utilidades comunitarias GML (60★) | MIT |
| [`GML-Extended`](https://github.com/DAndrewBox/GML-Extended) | Complementa las funciones nativas | MIT |
| [`MiniToolkit-GM`](https://github.com/mneet/MiniToolkit-GM) | Event System + Tween + UI Builder | MIT |

**Extensiones y librerías por categoría:**

| Repo | Ruta | Qué es | Licencia |
|---|---|---|---|
| [`GameMaker-Save`](https://github.com/NiZaMinius/GameMaker-Save) | `datos-y-estructuras/` | Guardado cifrado (Rust, XChaCha20-Poly1305) | Apache-2.0 |
| [`gms_enet`](https://github.com/alitoprak/gms_enet) | `red-y-multijugador/` | Red UDP fiable (ENet) | Unlicense |
| [`htgm`](https://github.com/meseta/htgm) | `red-y-multijugador/` | Servidor web en GML puro | MIT |
| [`gm-socketio`](https://github.com/ignoxx/gm-socketio) | `red-y-multijugador/` | Socket.io para GMS2 (HTML5) | MIT |
| [`IVideo`](https://github.com/mionumbra/IVideo) | `extras/` | Reproducción de vídeo (FFmpeg) | MIT |
| [`GML-Lua`](https://github.com/WushR00M/GML-Lua) | `extras/` | Lua 5.4 embebido (scripting/modding) | MIT |
| [`GLoader`](https://github.com/Kruger0/GLoader) | `3d/` | Cargador `.glb`/`.gltf` en GML | sin licencia |
| [`ImGM`](https://github.com/knno/ImGM) | `interfaz-de-usuario/` | Wrapper de Dear ImGui | MIT |
| [`GM-Testing-Library`](https://github.com/DAndrewBox/GM-Testing-Library) | `depuracion/` | Framework de testing para librerías | MIT |

**Runtimes / motores alternativos de código abierto** (`juegos_y_motores/`):

| Repo | Qué es | Licencia |
|---|---|---|
| [`Butterscotch`](https://github.com/ButterscotchRunner/Butterscotch) | Reimplementación open-source del runner de GM:Studio (351★) | AGPL-3.0 |
| [`OpenGM`](https://github.com/misternebula/OpenGM) | Runner de juegos GameMaker en .NET/OpenTK (44★) | MIT |
| [`Project-Sunshine-Native/cinnamon`](https://github.com/Project-Sunshine-Native/cinnamon) | *Fork* de Butterscotch: runner GML en C para **Nintendo 3DS y Wii U homebrew** (390★, *push* 2026-09-05, verificado 2026-09-07). El propio README avisa de que el desarrollo activo se mudó a `cinnamon-latest` (fila siguiente) | MPL-2.0 |
| [`Grayforz2468/cinnamon-latest`](https://github.com/Grayforz2468/cinnamon-latest) | Continuación activa de `cinnamon` — mismo runner para 3DS/Wii U (0★, *push* 2026-09-06, verificado 2026-09-07) | AGPL-3.0 |
| [`Ralcactus/GameMaker-Anywhere`](https://github.com/Ralcactus/GameMaker-Anywhere) | Port del runner GML a **varias consolas homebrew** vía devkitpro/C++ (convierte GML a C, no lo interpreta); 69★, *push* 2026-08-31, verificado 2026-09-07 | ⚠️ sin licencia declarada — revisa el repo antes de reutilizar código |

> 🕹️ Los tres de arriba son proyectos de **modding/porting**: ejecutan juegos GameMaker ya
> compilados en hardware homebrew no oficial (3DS, Wii U). No son herramientas de desarrollo
> para hacer un juego nuevo — misma distinción que ya aplica a Butterscotch/OpenGM frente al
> IDE oficial. **Para qué le sirve a alguien hoy**: casi para nada salvo curiosidad técnica o
> preservación — solo interesa si quieres ejecutar tus propios juegos GameMaker (u otros ya
> compilados) en una 3DS o Wii U con homebrew, un caso de uso muy de nicho. No aporta nada al
> desarrollo normal de un juego nuevo.

> ⚠️ Licencias `NOASSERTION` / `sin licencia`: revisa el `LICENSE` real del repo antes de
> redistribuir. `gml_lsp` está **archivado** (referencia, no producción). Muchos son de 2026 con
> pocas estrellas: valor por actualidad, no por popularidad.

### YellowAfterlife (YAL) y GameMakerDiscord — el filón que faltaba

**YellowAfterlife es el autor de herramientas de GameMaker más importante del ecosistema**, y sus
librerías open source y las de la comunidad `GameMakerDiscord` no estaban descargadas. Añadidas:

| Repo | Ruta | Qué es | ★ |
|---|---|---|---:|
| [`GMEdit`](https://github.com/YellowAfterlife/GMEdit) | `herramientas/GMEdit` | **Editor de código externo de referencia** para GameMaker (multi-versión, plugins). Estándar de facto. Ya estaba descargado y documentado en `12/01` | 369 |
| [`steamworks.gml`](https://github.com/YAL-GameMaker/steamworks.gml) | `integraciones/YAL-steamworks.gml` | Extensión Steamworks alternativa a la oficial | 90 |
| [`pixel-perfect-smooth-camera`](https://github.com/YAL-GameMaker/pixel-perfect-smooth-camera) | `camara/` | Cámara suave sin *jitter* de pixel *(ya estaba)* | 38 |
| [`Promise.gml`](https://github.com/YAL-GameMaker/Promise.gml) | `asincronia/` | Promesas/async *(ya estaba)* | 26 |
| [`Apollo`](https://github.com/YAL-GameMaker/Apollo) | `extras/Apollo` | Lua embebido en GameMaker (GML↔Lua) | 23 |
| [`GMSDLL`](https://github.com/YAL-GameMaker/GMSDLL) | `extensiones-nativas/GMSDLL` | Helper para escribir DLLs para GameMaker | 19 |
| [`room-shift`](https://github.com/YAL-GameMaker/room-shift) · [`gameframe`](https://github.com/YAL-GameMaker/gameframe) | `niveles-y-mapas/` · `extensiones-nativas/` *(ya estaba)* | Desplazamiento de rooms · marco de juego | 15 |
| [`window_frame`](https://github.com/YAL-GameMaker/window_frame) · [`winwin`](https://github.com/YAL-GameMaker/winwin) · [`window_shape`](https://github.com/YAL-GameMaker/window_shape) | `utilidades/` | Control avanzado de la ventana del juego (bordes, forma, embebido) | — |
| [`zip-writer`](https://github.com/YAL-GameMaker/zip-writer) | `datos-y-estructuras/` | Escribir archivos ZIP desde GML | — |
| [`random-level-gen-gms2`](https://github.com/GameMakerDiscord/random-level-gen-gms2) | `niveles-y-mapas/` | Generación procedural de niveles *(ya estaba)* | 57 |
| [`odin`](https://github.com/GameMakerDiscord/odin) | `utilidades/odin` | Utilidades varias de la comunidad | 36 |
| [`Rubber`](https://github.com/GameMakerDiscord/Rubber) | `herramientas-externas/` | CLI de compilación GMS2 *(ya estaba)* | 33 |
| [`PushEd`](https://github.com/GameMakerDiscord/PushEd) | `niveles-y-mapas/PushEd` *(ya estaba)* | Editor de rooms/niveles externo | 25 |
| [`gml-tools-langserver`](https://github.com/GameMakerDiscord/gml-tools-langserver) | `herramientas-externas/` | Servidor LSP para GML (autocompletado) | 19 |
| [`Discord.gml`](https://github.com/GameMakerDiscord/Discord.gml) | `integraciones/` | Discord Rich Presence | 19 |
| [`fix-your-timestep`](https://github.com/GameMakerDiscord/fix-your-timestep) | `tiempo-y-temporizadores/` | *Delta timing* correcto (semi-fixed timestep) | 17 |
| [`execute_string`](https://github.com/GameMakerDiscord/execute_string) | `utilidades/` | Ejecutar código GML desde un string | 16 |
| [`ArrayClass`](https://github.com/GameMakerDiscord/ArrayClass) | `datos-y-estructuras/` | Clase de array con métodos | 15 |
| [`PBR_shader_GMS2`](https://github.com/GameMakerDiscord/PBR_shader_GMS2) | `shaders/` | Shader PBR (physically-based rendering) | 14 |
| [`BigNum.gml`](https://github.com/GameMakerDiscord/BigNum.gml) | `matematicas/` | Números de precisión arbitraria | 8 |

**Herramientas de pago de YAL** (no descargables; referencia con enlace, en `12 - Utilidades`):
`GMLive.gml` (hot-reload, ya en `12/01`), **`cmnLoc`** (localización i18n con ICU/plurales/Crowdin),
`GMRoomPack` (rooms→JSON en runtime), `QRKoodi` (códigos QR en GML puro).

---

### GameMakerDiscord — resto de la organización (barrido completo)

Barrida entera la org [`GameMakerDiscord`](https://github.com/GameMakerDiscord) (65 repos): añadidos
los **42** que faltaban (código GML y herramientas), descartado el ruido (webs de la org, fangames,
un repo GMS 1.4 obsoleto y `FMODGMS`, retirado y reemplazado por el oficial `GMEXT-FMOD`). Además,
las **44 extensiones oficiales `GMEXT-*`** de YoYoGames ya estaban **todas** descargadas (0 faltaban).

| Repo | Ruta (`librerias/…` salvo indicado) | ★ |
|---|---|---:|
| [`blur-shaders`](https://github.com/GameMakerDiscord/blur-shaders) | `shaders/` | ★44 |
| [`z-tilting`](https://github.com/GameMakerDiscord/z-tilting) | `graficos-y-3d/` | ★17 |
| [`custom-sprite-framework`](https://github.com/GameMakerDiscord/custom-sprite-framework) | `graficos-y-3d/` | ★17 |
| [`microtester`](https://github.com/GameMakerDiscord/microtester) | `depuracion/` | ★13 |
| [`Lazy-Data-Scripts`](https://github.com/GameMakerDiscord/Lazy-Data-Scripts) | `datos-y-estructuras/` | ★12 |
| [`wind-shader`](https://github.com/GameMakerDiscord/wind-shader) | `shaders/` | ★11 |
| [`GML-Text`](https://github.com/GameMakerDiscord/GML-Text) | `texto-y-tipografia/` | ★10 |
| [`tic-net-toe`](https://github.com/GameMakerDiscord/tic-net-toe) | `red-y-multijugador/` | ★9 |
| [`astar-grid-pathfinding`](https://github.com/GameMakerDiscord/astar-grid-pathfinding) | `pathfinding/` | ★9 |
| [`depth-system`](https://github.com/GameMakerDiscord/depth-system) | `graficos-y-3d/` | ★9 |
| [`tex-pack`](https://github.com/GameMakerDiscord/tex-pack) | `utilidades/` | ★9 |
| [`GML-Tasks`](https://github.com/GameMakerDiscord/GML-Tasks) | `tiempo-y-temporizadores/` | ★8 |
| [`textbox-9slice`](https://github.com/GameMakerDiscord/textbox-9slice) | `shaders/` | ★7 |
| [`ExternalLibraryExample`](https://github.com/GameMakerDiscord/ExternalLibraryExample) | `ejemplos/` | ★7 |
| [`Outline-System`](https://github.com/GameMakerDiscord/Outline-System) | `shaders/` | ★7 |
| [`YY-YAML`](https://github.com/GameMakerDiscord/YY-YAML) | `datos-y-estructuras/` | ★7 |
| [`RegexGM`](https://github.com/GameMakerDiscord/RegexGM) | `utilidades/` | ★6 |
| [`Mario-like-Platformer-example`](https://github.com/GameMakerDiscord/Mario-like-Platformer-example) | `ejemplos/` | ★6 |
| [`snake-body-nodes`](https://github.com/GameMakerDiscord/snake-body-nodes) | `utilidades/` | ★5 |
| [`Top-Down-game-template`](https://github.com/GameMakerDiscord/Top-Down-game-template) | `ejemplos/` | ★5 |
| [`chess`](https://github.com/GameMakerDiscord/chess) | `ejemplos/` | ★5 |
| [`function-execute`](https://github.com/GameMakerDiscord/function-execute) | `utilidades/` | ★4 |
| [`YoYoProject`](https://github.com/GameMakerDiscord/YoYoProject) | `utilidades/` | ★4 |
| [`Timers-Made-Easy`](https://github.com/GameMakerDiscord/Timers-Made-Easy) | `tiempo-y-temporizadores/` | ★4 |
| [`GML-system-movement-release`](https://github.com/GameMakerDiscord/GML-system-movement-release) | `utilidades/` | ★4 |
| [`proximity_nodes`](https://github.com/GameMakerDiscord/proximity_nodes) | `fisica/` | ★4 |
| [`inverse-kinematics`](https://github.com/GameMakerDiscord/inverse-kinematics) | `graficos-y-3d/` | ★3 |
| [`gridcol-rounded-corners`](https://github.com/GameMakerDiscord/gridcol-rounded-corners) | `utilidades/` | ★3 |
| [`RubberSharp`](https://github.com/GameMakerDiscord/RubberSharp) | `utilidades/` | ★3 |
| [`rain_glass_effect`](https://github.com/GameMakerDiscord/rain_glass_effect) | `shaders/` | ★3 |
| [`instance_flags`](https://github.com/GameMakerDiscord/instance_flags) | `utilidades/` | ★3 |
| [`GML-system-depth-release`](https://github.com/GameMakerDiscord/GML-system-depth-release) | `graficos-y-3d/` | ★3 |
| [`hit-target-example`](https://github.com/GameMakerDiscord/hit-target-example) | `fisica/` | ★2 |
| [`low-poly-terrain`](https://github.com/GameMakerDiscord/low-poly-terrain) | `shaders/` | ★2 |
| [`json-save`](https://github.com/GameMakerDiscord/json-save) | `datos-y-estructuras/` | ★2 |
| [`Collision-List-Functions`](https://github.com/GameMakerDiscord/Collision-List-Functions) | `fisica/` | ★2 |
| [`instance_nearest_ext`](https://github.com/GameMakerDiscord/instance_nearest_ext) | `fisica/` | ★2 |
| [`YY-Reunion`](https://github.com/GameMakerDiscord/YY-Reunion) | `datos-y-estructuras/` | ★2 |
| [`yy-hider`](https://github.com/GameMakerDiscord/yy-hider) | `datos-y-estructuras/` | ★1 |
| [`StrayResourceFinder`](https://github.com/GameMakerDiscord/StrayResourceFinder) | `utilidades/` | ★1 |
| [`Sten`](https://github.com/GameMakerDiscord/Sten) | `utilidades/` | ★1 |
| [`Simple-Dynamic-Audio-Demo`](https://github.com/GameMakerDiscord/Simple-Dynamic-Audio-Demo) | `audio/` | ★1 |

<a id="dragonitespam"></a>

## Tutoriales de DragoniteSpam

La **organización completa** de [DragoniteSpam-GameMaker-Tutorials](https://github.com/DragoniteSpam-GameMaker-Tutorials)
(**193 proyectos**, todos **MIT**): el código real que acompaña a cada tutorial de un tutor veterano.
Los **189** de la carpeta `plantillas_y_ejemplos/dragonitespam/` (los otros 4 destacados están en sus
carpetas temáticas con prefijo `DS-`). En vez de re-listarlos aquí, el **desglose por tema** (serie 3D
1→94, shaders, structs/métodos 2.3+, diálogo, audio, guardado, vídeo…) está en la ficha detallada:

👉 [`07 - Ecosistema/04 - Proyectos de ejemplo para estudiar.md` §4 bis](../07%20-%20Ecosistema/04%20-%20Proyectos%20de%20ejemplo%20para%20estudiar.md)

Para localizar uno concreto: `python3 "_indice/buscar.py" --codigo "<tema>"`, o busca `DS-<Nombre>`
en [`_RUTAS.json`](./_RUTAS.json). Código GML real, moderno (muchos actualizados a 2.3+) y MIT
(conserva el aviso de copyright si copias archivos enteros).

## Cómo actualizar este espejo

Los clones completos viven **fuera** de la biblioteca, en `~/Documents/GameMaker_Fuentes/`, para no inflarla. Cada carpeta de ahí es un clon de git normal: `git -C <carpeta> pull` lo actualiza, y volviendo a ejecutar el extractor se regenera la copia de texto.

Fuentes de la selección: la sección [`07 - Ecosistema`](../07%20-%20Ecosistema/_INDICE-ECOSISTEMA.md) de esta biblioteca y [awesome-gamemaker](https://github.com/bytecauldron/awesome-gamemaker) (★501, 2026-08-23), del que se han incorporado los 167 repositorios que faltaban.

