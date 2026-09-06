# GMRT — El nuevo runtime de GameMaker (codename Cronus)

> Estado en agosto de 2026: **Beta pública**. Última versión publicada: **GMRT 0.21.0** (julio 2026).
> Se instala desde el **Package Manager** y se actualiza por ahí también, no con la IDE.

---

## 1. Qué es GMRT

GMRT (**GameMaker Runtime**, nombre en clave **"Cronus"**) es un **toolchain y librería de runtime completamente nuevos**, construidos desde cero. Convive con —y eventualmente sustituirá a— los runtimes actuales **VM** y **YYC**, que ahora se denominan **GMS2 VM** y **GMS2 YYC**.

Objetivos declarados por YoYo Games:

1. **Desacoplar la arquitectura monolítica** del runtime actual en módulos.
2. Aprovechar **CMake + LLVM + Clang** para mejorar el rendimiento general.
3. Permitir **mejor soporte de librerías de terceros**.
4. Hacer que ampliar el runtime sea fácil, tanto para el equipo de GameMaker como para los usuarios.

### Contexto estratégico (lo que de verdad importa)

> **LTS 2026 marca el runtime GMS2 como *feature complete*. Todas las peticiones de funcionalidad nuevas y pendientes solo se considerarán para GMRT.**

El runtime GMS2 seguirá con soporte hasta **al menos Q1 2028**, pero **solo con actualizaciones de SDK y correcciones de bugs críticos**. Es decir: **el futuro de GameMaker es GMRT**, y cuanto antes lo conozcas, mejor.

---

## 2. Arquitectura

### 2.1 De monolito a modular

- **Antes**: una única librería monolítica enlazada en tiempo de compilación que proporcionaba *todo* (funcionalidad GML, ejecución de scripts, ventanas…).
- **Ahora**: GMRT rompe esa estructura. Puedes incluir **solo las librerías que tu proyecto necesita**, lo que potencialmente reduce mucho el tamaño del ejecutable… a costa de más tiempo de enlazado si enlazas todas.

> ⚠️ Esto **todavía no tiene soporte en la IDE**: se consigue instalando solo los paquetes de librería que quieras. Está documentado como experimento.

### 2.2 Toolchain

- La generación de **WAD** se ha movido al **runtime**. Implicación gorda: **un compilador de assets puede ser él mismo un proyecto GML**, y de hecho el *asset compiler* empaquetado lo es.
- Consecuencia actual: hay **poco cacheo** de assets generados, así que **cada vez que ejecutas el proyecto se regeneran assets**. Lo van a arreglar.

### 2.3 Renderizado, ventanas e IO

Reescritos por completo sobre:

- **Dawn** (el proyecto de Google, la capa de abstracción de WebGPU) — trabajan con Google.
- **SDL2**.

Objetivo: una solución de renderizado rápida y extensible que permita atacar APIs gráficas nuevas mucho más rápido que antes.

### 2.4 Funcionalidades planeadas (del repo oficial)

- Desarrollo más fácil de herramientas propias (de GM o del usuario) sobre el toolchain.
- Desarrollo más fácil de librerías para ampliar el runtime.
- **Más rendimiento** vía análisis estático y LLVM.
- Herramientas para convertir una librería nativa en extensión con **un solo fichero IDL**.
- **Pipeline de renderizado nuevo y personalizable**.
- Permitir **crear WAD en runtime** y soporte de **múltiples WAD**.
- Más herramientas: incluido un **servidor LSP** para escribir código desde cualquier IDE compatible.
  - Ya desde ahora, al compilar se genera un **proyecto de Visual Studio** que sirve para depuración básica.

---

## 3. Diferencias con GMS2 VM / YYC

| Aspecto | GMS2 VM / YYC | GMRT |
|---|---|---|
| Compilador | el de siempre | **compilador GML nuevo desde cero** |
| Arquitectura | monolítica | **modular por paquetes** |
| Backend | propio | **LLVM / Clang** (rendimiento) |
| Gráficos | pipeline propio | **Dawn (Google) + SDL2** |
| Depuración en IDE | completa | **básica**: puntos de ruptura y algo de "step" |
| Idiomas | GML | **GML + JavaScript (Q2 2026) + TypeScript (Q3) + C# (Q4 preview)** |
| Código fuente | solo Enterprise | **Desktop / Mobile / Web: abierto a TODOS los usuarios** |
| Estado | estable, feature complete | **Beta, incompleto** |
| Tiempos de build | rápidos | **mucho más lentos** |

### Acceso al código fuente

YoYo Games ha decidido que el código fuente de GMRT para **Desktop, Mobile y Web** estará disponible para **todos** los usuarios: podrás acceder, modificar y compilar desde él. Los usuarios **Enterprise** tendrán además acceso a las versiones de **consola** de las plataformas para las que estén verificados.

> La distribución comercial de juegos **sigue requiriendo licencia activa**. Detalles en el *GameMaker Source Code License Agreement*.

---

## 4. Instalación paso a paso

### 4.1 Requisitos

| Requisito | Detalle |
|---|---|
| GameMaker | La versión estándar vale (**ya no hace falta la Beta**). Windows y macOS soportadas. |
| **dotnet 8.0** | **Obligatorio**. Instalar el *runtime* de .NET 8. |
| **EMSDK 5.0.4** | Solo si vas a compilar para **WebAssembly (wasm32)**. GMRT no lo incluye. |
| Licencia | Debes estar **logueado** en GameMaker para ver los targets GMRT. En instalaciones previas puede que necesites pulsar **"Update Licence"** en el panel de cuenta. |

```bash
# EMSDK (solo para wasm)
emsdk.bat install 5.0.4
```

### 4.2 Instalación por Package Manager

1. Abre GameMaker y **abre cualquier proyecto**. El Package Manager solo aparece con un proyecto abierto, porque su salida va a la ventana *Output*.
2. Ve a **`Tools > Package Manager`** (en Betas recientes también se cita el menú *Windows*).
3. Busca el **metapaquete `GMRT - <Plataforma>`** correspondiente a tu sistema y pulsa **Install**.
   - Es un **metapaquete**: está vacío y su única misión es arrastrar como dependencias todas las herramientas de terceros y las librerías de runtime de esa plataforma.
   - Tras instalarlo verás que se instalan otros paquetes a la vez.
4. En el panel derecho puedes elegir versión; para la instalación inicial deja la **última** (viene seleccionada por defecto).
5. Mientras instala verás la salida de GMPM en la consola y un icono girando en el Package Manager.

### 4.3 Paquetes adicionales para otros targets

Después del metapaquete tendrás instalado también **`GMRT Runtime - <Target>`** para tu plataforma. Para compilar a **otro** target necesitas su runtime específico:

- `GMRT Runtime - wasm32-emscripten` → WebAssembly
- `GMRT Runtime - aarch64-linux-android` → Android (junto con `Gmir2llvm-17.0.3`)

### 4.4 Preferencias

Aparecen dos secciones nuevas en Preferences:

- **Package Manager**: ruta de instalación (por defecto no hay que tocarla) y URL del source. Si cambias la ruta, **cambia también "Path to GMRT"** en las preferencias de GMRT o no encontrará los paquetes.
- **GMRT**: opciones por defecto; úsalas si quieres generar **soluciones de Visual Studio** para depurar/compilar fuera de GameMaker.

### 4.5 Compilar

Igual que con VM/YYC, pero con builds **mucho más lentos**:

- `Target: Windows > GMRT VM` → ejecuta tus scripts en el intérprete de GMRT.
- `Target: Windows > GMRT` → **compilación nativa**: compila tus scripts (más rápido en runtime, más lento en build).

---

## 5. "Changes to GML" — cambios de lenguaje en GMRT

GMRT trae un compilador GML nuevo. Algunos cambios son **deliberados** (simplificar el lenguaje) y otros son **limitaciones temporales** del compilador en desarrollo.

> **Regla general:** cualquier función marcada como *deprecated* en GMS2 **no existe** en GMRT, ni siquiera en las librerías de compatibilidad.

### 5.1 `typeof(self)` dentro de una instancia

Comportamiento contradictorio que GMRT corrige:

```gml
// Comportamiento actual (contradictorio)
_self_type  = typeof(self);    // "struct"
_is_struct  = is_struct(self); // false   ← se contradice
```

GMRT plantea que `is_struct(self)` devuelva `true` y añadir una función complementaria `is_instance(self)`.

### 5.2 Ambigüedad de `self` en struct literals

Hay una asimetría heredada:

```gml
// CREATE EVENT
__a__ = 12;
__b__ = 22;

result = { context: self, a: self.__a__ };
//       ^^^ primer self: apunta al PROPIO struct literal
//                          ^^^ segundo self (expresión compleja): apunta al
//                              ámbito EXTERIOR al struct literal
```

La regla general es que en los pares `[clave : valor]` de un struct literal, **los valores siempre se refieren al ámbito exterior**. La excepción es `self` como expresión simple.

Truco si necesitas el `self` exterior de forma explícita: usa una función "passthrough".

```gml
// Ámbito global
function passthrough(_val) { return _val; }

// CREATE EVENT
result = { context: passthrough(self) };   // contexto exterior, garantizado
```

```gml
// Recordatorio: todos los valores apuntan hacia fuera
var _t = "Hola";
result = { __a__: __a__, __b__: __b__, _t: _t };
```

### 5.3 `id` vs `self`

Aunque normalmente son intercambiables:

```gml
with (id)              == with (self)
id.speed               == self.speed
instance_destroy(self) == instance_destroy(id)
```

…sus `typeof()` difieren según el runtime:

```gml
// Runtime actual
typeof(id)    // "ref"
typeof(self)  // "struct"

// GMRT
typeof(id)    // "struct"
typeof(self)  // "struct"
```

### 5.4 Constructor function tags

Desde 07/07/2024, el asset compiler inyecta tags en las funciones constructor:

```gml
function A() constructor {}

tags = asset_get_tags(A, asset_script);
show_debug_message(tags);   // ["@@constructor"]

function B() : A() constructor {}

tags = asset_get_tags(B, asset_script);
show_debug_message(tags);   // ["@@constructor", "@@parent=A"]
```

### 5.5 Propiedades indexadas requieren índice

En GML actual puedes acceder a una propiedad indexada sin índice. **En GMRT no**:

```gml
var _c = view_camera;     // ✗ en GMRT no es válido
var _c = view_camera[0];  // ✓ obligatorio el índice
```

### 5.6 IDs de asset como valores numéricos

Es el mismo cambio que trae LTS 2026.0 con los **Handles**, llevado al extremo:

```gml
var _x = MiObjeto + 1;   // ✗ en GMRT lanza una excepción en runtime
```

GMRT ha adoptado referencias, igual que el runtime de GMS2 está migrando a referencias.

---

## 6. Estado actual: GMRT 0.20.0 (junio 2026)

### Novedades

- **Funciones GM3D** (incompletas, pidiendo feedback):
  - *Matemáticas 3D*: vectores, matrices, cuaterniones.
  - *Carga de modelos*: mallas, mallas con skinning, animaciones, animación esquelética y materiales. **Solo glTF**.
  - *Gestión de escena*: cámaras, iluminación y ajustes de entorno.
  - Lista completa de funciones, atributos y structs en el fichero `GM3D_API.md` del proyecto de ejemplo: https://github.com/YoYoGames/GM3D-Samples
  - ⚠️ **No hay ayuda de sintaxis en la IDE**: no aparecen en autocompletado ni tienen ayuda de parámetros ni resaltado.
- **Target Android** (solo `aarch64` por ahora):
  - Android SDK **35** (Android 15)
  - Android NDK **28.2.13676358**
  - Gradle **8.14.2**
  - Paquetes: `GMRT Runtime - aarch64-linux-android` + `Gmir2llvm-17.0.3`
  - Problemas conocidos: barras de navegación/estado siempre visibles; resolución incorrecta al arrancar en vertical/horizontal; multitáctil sin detectar; salir del juego puede causar crash de audio.
- **Target Switch**
- **Funciones de colisión que devuelven arrays** (también sin ayuda de sintaxis en la IDE)

### Compatibilidad con GMS2 añadida

- **UI Layers**
- Reproducción de vídeo (**solo Windows**)
- `layer_get_flexpanel_node()` y `layer_get_type()`
- `particle_add` / `particle_delete`
- Imprimir instancias a string ahora muestra la `ref` correcta
- **MRT** (multiple render targets) gestionado correctamente
- `os_type`, `os_version`, `os_device` y `os_get_info()` implementados
- Manejo de ficheros mejorado para reducir problemas por plataforma
- Los proyectos que usan las librerías **Scribble** e **Input** deberían compilar y funcionar
- Más funciones imGUI: `dbg_color`/`dbg_colour`, `dbg_drop_down`, `dbg_slider`, `dbg_slider_int`, `dbg_text`, `dbg_text_input`, `dbg_text_separator`, `dbg_watch`

---

## 7. Estado actual: GMRT 0.21.0 (julio 2026)

### Novedades

- **Suite ImGUI basada en ImGM**, una mejora enorme de la implementación de Dear IMGui:
  - Ventanas **dockables**
  - Árboles
  - Pestañas
  - Tablas
  - Tooltips
  - Popups
  - Funciones de estilo
  - **Unas 200 funciones nuevas**
  - Proyecto de ejemplo y documentación: https://github.com/YoYoGames/ImGUI-Sample
  - ⚠️ Sin ayuda de sintaxis en la IDE (sin autocompletado ni ayuda de parámetros)

### Incompatibilidades conocidas con GMS2 (lista de 0.21.0)

- **Prefabs**
- Reproducción de vídeo (en plataformas que no sean Windows)
- Assets **SVG**
- `flexpanel_node_get_measure()` / `flexpanel_node_set_measure()`
- `vertex_buffer_exists()` / `vertex_format_exists()`
- `application_surface_is_draw_enabled()`

*(En 0.20.0 la lista incluía además "montones de spam de errores de SDL" — issue #4980 — que ya no aparece en 0.21.0.)*

### Bugs corregidos (selección de 0.20.0, da idea de por dónde van los tiros)

- Alpha-testing desactivado por defecto para coincidir con GMS2
- `array_sort` más rápido con arrays grandes
- `camera_get_proj_mat()` devuelve el valor correcto
- `direction` ya no se resetea cuando `speed` es 0
- `ds_grid_copy` ya no espeja los datos
- Filtro "Parallax background" ya renderiza
- GMRT ya no lanza excepción al llamar una función GML con argumentos opcionales omitiendo uno o pasando `undefined`
- Crecer un buffer más allá de 2 GB ya no crashea
- `gpu_pop_state()` afecta a uniforms de shader y textura
- `gpu_set_cullmode()` implementado
- Corregido el manejo de texturas Spine con alfa premultiplicado
- `instance_id` devuelve lo mismo que en GMS2
- El comportamiento heredado de `other` ya no es el defecto
- `matrix_set()` actualiza todas las matrices
- Fugas de memoria en structs de secuencia
- `room_get_info()` devuelve información de elementos de capa ParticleSystem
- `room_next()` ya no crashea con una sola room
- Los sprites Spine solo usan malla de colisión si se seleccionó en el editor
- `surface_get_depth_disable()` devuelve el valor correcto
- Los **template strings con llaves escapadas** ya no causan error de formato
- La profundidad del tilemap ya responde a `gpu_set_depth`
- El target **WASM** vuelve a compilar y ejecutarse
- `window_mouse_set()` mueve de verdad el ratón
- Las máquinas **Windows ARM64** ya pueden usar GMRT

---

## 8. Problemas conocidos generales (del repo oficial)

- La integración con el **depurador de la IDE no es funcional del todo**: solo puntos de ruptura básicos y algo de "step".
- El pipeline de renderizado **no está optimizado**: latencia extra por draw calls innecesarias y copias de buffers.
- Se ha portado aproximadamente el **99,5 %** de las funciones, propiedades y constantes de GML (excluyendo algunas específicas de plataforma y features recientes de GMS2), apoyándose en **tests automáticos y QA limitada**. Por tanto: **se espera que muchos juegos fallen** por funcionalidad ausente o rota en la capa de compatibilidad.
- **"Clean" no está implementado**: borra a mano la carpeta `Build` del proyecto y la caché de assets (`Documents/GameMaker/Cache/<nombre del juego>`).
- Al resolver problemas de build: **borra la carpeta "Build"** antes de reintentar. Los datos cacheados pueden seguir provocando el fallo aunque ya lo hayas arreglado.

### Dónde piden feedback prioritario

- Funciones GML rotas o con comportamiento raro
- Problemas de **orden de eventos** (la invocación ha cambiado; los proyectos que dependían de órdenes no documentados se romperán)
- Problemas de renderizado
- Problemas de audio
- Rendimiento, tanto de build como en juego
- Problemas del compilador / lenguaje GML
- Problemas del asset compiler
- Problemas al ejecutar las herramientas del toolchain
- Problemas con el depurador de la IDE

### Cómo reportar

Activa la salida verbose de GMRT: **`File > Preferences > GMRT` → "Compiler with verbose output"**, reproduce el fallo y adjunta el log.

Usa el bug reporter de la IDE (`Help`) con categoría **"In-Game (GMRT)"** o **"Project Fails to Build (GMRT)"**.

---

## 9. Troubleshooting

| Síntoma | Causa / solución |
|---|---|
| El Package Manager no abre al pulsar `Tools > Package Manager` | Está ligado a tu cuenta. Cierra y reabre la IDE y vuelve a loguearte. |
| Los paquetes tardan mucho o fallan | Problemas de red. Mira la ventana *Output*; GMPM va escribiendo el progreso. |
| Errores de "duplicate symbol" al enlazar | Librerías viejas que GMPM no limpió. Borra la carpeta de instalación de `gmpm` y reinstala la última versión. |
| Un paquete falla al instalar | Revisa el log (antivirus/permisos). Si se repite: cierra GameMaker, borra la carpeta `gmpm` y reinstala. |
| Tu proyecto no compila | **Primero compila un proyecto vacío** con una sola room. Si el vacío sí y el tuyo no, es un bug: repórtalo. |
| Quieres usar las herramientas que ya tienes instaladas | En `Preferences > GMRT`: *Path to Clang* → `clang-cl` (o `clang`); *Path to CMake* → `cmake`; *CMake Generator* → `Visual Studio 17` si tienes VS2022 (genera solución depurable). |

---

## 10. Recomendación: cuándo usar GMRT y cuándo NO

### ✅ Usa GMRT cuando

- Estás **aprendiendo / experimentando** y quieres familiarizarte con el futuro de GameMaker antes de que te pille el cambio.
- Vas a necesitar **JavaScript / TypeScript / C#** en tu proyecto (Q2–Q4 2026).
- Quieres explotar las **funciones GM3D** (glTF, scene graph, animación esquelética, matemáticas 3D).
- Vas a usar la nueva **suite ImGUI** para herramientas de depuración internas.
- Es un **proyecto pequeño, un prototipo o un jam**.
- Tu objetivo es **medir rendimiento** y comparar con GMS2 para decidir a medio plazo.

### ❌ NO uses GMRT cuando

- Es un **proyecto en producción** o con fecha de lanzamiento.
- Dependes de **Prefabs**, assets **SVG**, reproducción de vídeo (no Windows), o de `flexpanel_node_get_measure()`, `vertex_buffer_exists()`, `vertex_format_exists()` o `application_surface_is_draw_enabled()`.
- Necesitas el **depurador completo** de la IDE.
- Necesitas **builds rápidos** para iterar (GMRT es mucho más lento compilando).
- Vas a publicar en una plataforma que todavía no tiene runtime estable.

### Estrategia recomendada

1. **Ahora**: mantén tus proyectos serios en **GMS2 VM / YYC** sobre LTS 2026.0.
2. **En paralelo**: monta un proyecto de pruebas en GMRT y ve portando sistemas sueltos. Mantén el Package Manager al día.
3. **Cuando GMRT salga de Beta en desktop** (previsto "en los próximos meses" desde el update de primavera) y según se vayan añadiendo móvil y consola "a lo largo del año", replantea la migración.
4. Ve **leyendo los release notes de cada GMRT** antes de cada build: son cortos y las listas de incompatibilidades son la parte crítica.

---

## Fuentes

- Setup e instrucciones oficiales de GMRT (GitHub) — https://github.com/YoYoGames/GMRT-Beta/blob/main/docs/introduction/GMRT-intro-and-setup-instructions.md
- Manual: GMRT (GameMaker Runtime) — https://manual.gamemaker.io/lts/en/Settings/Runner_Details/GMRT_(GameMaker_Runtime).htm
- Release notes GMRT 0.20.0 — https://releases.gamemaker.io/release-notes/2026/GMRT_MS_20.html
- Release notes GMRT 0.21.0 — https://releases.gamemaker.io/release-notes/2026/GMRT_MS_21
- Índice de versiones ( GMRT y Betas) — https://releases.gamemaker.io/
- Ejemplo GM3D — https://github.com/YoYoGames/GM3D-Samples
- Ejemplo ImGUI — https://github.com/YoYoGames/ImGUI-Sample
- GameMaker Source Code License Agreement — https://gamemaker.io/en/legal/sourcecode
- Update primavera 2026 (roadmap) — https://gamemaker.io/en/blog/update-spring-2026
