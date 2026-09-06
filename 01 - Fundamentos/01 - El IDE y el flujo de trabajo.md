# 01 · El IDE y el flujo de trabajo

> **Fuente principal:** Manual oficial de GameMaker (LTS 2026)
> - <https://manual.gamemaker.io/lts/en/Introduction/The_Asset_Browser.htm>
> - <https://manual.gamemaker.io/lts/en/Introduction/Compiling.htm>
> - <https://manual.gamemaker.io/lts/en/Introduction/The_Output_Window.htm>
> - <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Object_Events.htm>
> - Formato de proyecto: `gm-cli manual read "Export Project YYZ"` → *Project Format*

---

## 1. El mapa mental: qué es un proyecto de GameMaker

Un proyecto de GameMaker **no es un archivo**, es una **carpeta** con una estructura concreta. Entenderla te ahorra muchos dolores de cabeza con Git:

| Archivo / carpeta | Qué es |
|---|---|
| `*.yyp` | El **proyecto**. Describe los recursos del proyecto y sus metadatos. Es la raíz. |
| `*.resource_order` | El orden de grupos y assets del Asset Browser cuando el filtro está en *Custom Order*. |
| `*.yy` | Archivos de **recurso**. Guardan los datos de cada asset (objetos, sprites, rooms…) en un formato parecido a JSON. |
| `.gitignore` / `.gitattributes` | GameMaker los añade solos a proyectos nuevos/importados si activas *Add skeleton .git defaults* en **Source Control (Git)** dentro de las Plugin Preferences. |

> ⚠️ **Regla de oro:** **nunca edites `.yy` ni `.yyp` a mano.** Su formato es frágil y se corrompe con facilidad. Para crear o modificar recursos usa el IDE, el MCP `gamemaker-resource-tool` o `gm-cli resourcetool eval "<comando>"`. El código GML (`.gml`) sí se edita con el editor de texto normal.

Si GameMaker detecta un `.yy` al que le falta un archivo asociado (por ejemplo el PNG de un sprite), te lo reporta en la ventana **Project Health** al abrir el proyecto.

---

## 2. El Asset Browser

Es el corazón de la organización. Por defecto está a la derecha del IDE y contiene **todo** lo que tu juego necesita para funcionar: rooms, sprites, objetos, scripts, sonidos, paths, shaders, tilesets, secuencias, fuentes, notas, extensiones, animation curves, timelines y particle systems.

### Partes del Asset Browser

1. **Search Bar** — Filtra la lista escribiendo texto. Borra el texto para volver a la vista completa.
2. **Add Asset** — Crea recursos nuevos. Puedes elegir vista de lista o de rejilla, y también **importar** un asset ya existente desde otro proyecto. Si pones un número antes de pulsar *Create*, crea esa cantidad de assets de golpe.
3. **Filter** — Ordena A→Z o Z→A, agrupa primero por carpetas o todo junto, filtra por tipo de asset y por **tags**. Si hay un filtro activo que no sea *Any Type*, el botón cambia de color.
4. **Extras** — Acceso rápido a Room Manager, Config Editor, Game Options e Included Files.
5. **Quick Access** — *Recent* (últimos usados, máx. 10 por defecto), *Favourites*, *Room Order*, *Saved Searches*, *Tags*, *Game Options* y *Prefabs*.
6. **Asset List** — El árbol de assets. Clic derecho → *Create Group* para crear carpetas.
7. **Information** — Cuántos assets hay y cuántos hay seleccionados, más los tags activos (clic para quitarlos).
8. **Zoom Controls** — Del 50 % al 250 % del DPI del IDE. Doble clic en el porcentaje para volver al 100 %.

### Room Order (importante)

Todo proyecto necesita **al menos una room** para poder ejecutarse. La room que está arriba del todo es la **home room**: la primera que se carga al arrancar el juego (lleva un icono de casa). Arrastra para reordenar.

### Colores y tags

- **Colores:** clic derecho sobre un asset o carpeta → franja de colores abajo. Colorear una carpeta colorea también su contenido. Con Shift o Ctrl/Cmd + clic puedes colorear varios a la vez.
- **Tags:** clic derecho → *Edit Tags*. Separa con comas o Enter. Los tags **no** se heredan de la carpeta a los assets de dentro (aunque asignar un tag a una carpeta sí la etiqueta a ella).
- ⚠️ **Trampa clásica:** si tienes un filtro por tag activo y creas un asset nuevo, **ese asset nace con ese tag**.
- Los tags no son solo decoración: se pueden usar **en código** con `asset_get_tags()` y `tag_get_asset_ids()`. Ejemplo mental: etiquetas cosas con `"MuereAlTocar"` y tu código genérico reacciona a cualquier asset que lleve ese tag, sin need de enumerar objetos.

---

## 3. Tipos de asset (resumen)

| Icono | Asset | Para qué sirve |
|---|---|---|
| 🏠 | **Rooms** | El espacio donde ocurre el juego. Al menos una es obligatoria. Pueden tener rooms **hijas** que heredan propiedades, capas y contenido. |
| 🧩 | **Objects** | Los "planos" con eventos. No se colocan directamente: se colocan **instancias** suyas. |
| 🖼️ | **Sprites** | Imagen estática, *strip* animado, SVG/SWF vectorial o Spine (JSON + atlas). Son la representación visual de los objetos. |
| 🟦 | **Tile Sets** | Sprites partidos en celdas para construir tilemaps. Siempre **cuadrados**. Ideales para terreno estático (sin el overhead de los objetos). |
| 📜 | **Scripts** | Contenedores de una o más **funciones**. |
| 🎞️ | **Sequences** | Animaciones dinámicas con *tracks* y *keyframes*. Reemplazan a los Timelines. |
| ⏱️ | **Timelines** | **Legacy.** Reemplazados por Sequences; solo existen por compatibilidad. |
| ✨ | **Shaders** | Programas de GPU (vertex + fragment). |
| 🔊 | **Sounds** | WAV, MP3 y OGG. |
| 🔤 | **Fonts** | Fuentes para dibujar texto. |
| 🛤️ | **Paths** | Rutas que una instancia puede seguir. |
| 🧬 | **Animation Curves** | Curvas de valores normalizados (−1..1 vertical, 0..1 horizontal). |
| ⚙️ | **Extensions** | Código nativo (C++, C# o JS) que amplía GameMaker. |
| ✨ | **Particle Systems** | Sistemas de partículas (sistema → emisores → tipos). |
| 📝 | **Notes** | Editor de texto libre: snippets, TODOs, comunicación de equipo. |

> **Sobre los sonidos:** WAV para efectos cortos (se reproducen al instante, no necesitan decodificación). MP3/OGG para música y efectos largos: ocupan mucho menos pero tienen coste de CPU al decodificar.

> **Sobre los shaders**, el lenguaje depende de la plataforma:
> | Lenguaje | Plataforma |
> |---|---|
> | **GLSL ES** | Todas |
> | **GLSL** | Mac y Ubuntu (Linux) |
> | **HLSL11** | Windows, XboxOne |
> | **PSSL** | PlayStation 4 |
>
> Se cambia con clic derecho → *Shader Type*.

---

## 4. Convenciones de nombres

### Lo que impone GameMaker (reglas duras)

Los nombres de assets solo pueden ser **alfanuméricos**, **no pueden empezar por un número** y solo admiten el guion bajo `_` como carácter adicional. Lo mismo aplica a las variables.

Hay además **nombres reservados** que no puedes usar para tus variables:
`player_avatar_sprite`, `player_avatar_url`, `player_id`, `player_local`, `player_name`, `player_type`, `player_user_id`, `player_prefs`, `managed`.

Tampoco puedes usar el nombre de un asset como nombre de variable salvo que indiques explícitamente el ámbito (`self.MiVariable`, `global.MiVariable`), porque eso define el scope y desambigua.

### Lo que se recomienda (convención de la comunidad y del IDE)

Si activas la regla **GM2017** en *Feather Preferences* (con Feather o Code Editor 2 activados), el IDE **aplica automáticamente** unas reglas de nomenclatura a los assets nuevos que crees.

| Prefijo | Tipo | Ejemplo |
|---|---|---|
| `spr_` | Sprite | `spr_player_idle` |
| `obj_` | Object | `obj_enemy_slime` |
| `rm_` | Room | `rm_level_01` |
| `scr_` | Script | `scr_inventario` |
| `snd_` | Sound | `snd_jump` |
| `fnt_` | Font | `fnt_ui_bold` |
| `ts_` | Tile Set | `ts_dungeon` |
| `shd_` | Shader | `shd_water` |
| `path_` | Path | `path_patrol_a` |
| `seq_` | Sequence | `seq_intro` |
| `anim_` | Animation Curve | `anim_fade` |

**¿Por qué molestarse?** Porque en GML el nombre del asset *es* el identificador que usas en código (`instance_create_layer(x, y, "Instances", obj_enemy)`). Un prefijo te dice de un vistazo qué estás pasando a una función y evita colisiones: `snd_explosion` y `obj_explosion` pueden convivir sin ambigüedad.

Además, en el **código** la convención es distinta y conviene respetarla:

```gml
// Variables locales: prefijo _ (guion bajo). Es la convención GML más extendida.
var _velocidad = 4;
var _dir = point_direction(x, y, mouse_x, mouse_y);

// Variables de instancia: snake_case, sin prefijo.
velocidad = 4;

// Globales: prefijo global. explícito.
global.puntuacion = 0;

// Constantes (#macro / enum): MAYÚSCULAS con guion bajo.
#macro MAX_VIDAS 3
enum EstadoEnemigo { PATRULLA, ALERTA, ATAQUE }
```

---

## 5. El Inspector, el Output y los Workspaces

### El Inspector

Es el panel de propiedades del asset seleccionado. En el **Object Editor** verás: sprite asignado, si usa físicas, objeto **padre**, y las **Object Variables** (variables por defecto que se asignan a las instancias *antes* de que corra el evento Create).

> ⚠️ Diferencia clave que confunde a mucha gente: las **Object Variables** NO son variables estáticas. No pertenecen al objeto: son **valores por defecto** que se copian a cada instancia creada desde ese objeto, antes del Create.

### La ventana Output

Docking en la parte inferior con pestañas. Puedes arrastrar las pestañas a otros docks, sacarlas a ventana independiente, o arrastrar un output sobre otro para tener **vista dividida**. Si la lías: *Reset Layout* desde el menú Layouts.

| Pestaña | Contenido |
|---|---|
| **Output** | Salida del compilador **y** todos tus `show_debug_message()`. |
| **Search Results** | Resultados de buscar y reemplazar (`Ctrl/Cmd + Shift + F`). Formato `[objeto] - [evento] - [línea]: [texto]`. Doble clic para saltar. |
| **Source Control** | Salida del plugin de SCM. |
| **Breakpoints** | Puntos de parada. Se ponen con **F9**. Se pueden desactivar sin borrar. |
| **Syntax Errors** | Errores de sintaxis en vivo mientras escribes. |
| **Compile Errors** | Errores de compilación, listados aparte para que no se pierdan en el Output general. |
| **Feather Messages** | Errores, avisos y sugerencias de **Feather** (el analizador estático). Doble clic para navegar al código. |

> Los *Syntax Errors* se actualizan con un pequeño retardo mientras tecleas (para no reportar código a medio escribir). Dos casos **no** impiden compilar pero conviene revisar: variable declarada y nunca usada, y variable usada sin declarar. Normalmente es un *typo*.

---

## 6. Ejecutar y compilar: VM vs YYC

Tres botones en la parte superior:

| Botón | Qué hace |
|---|---|
| ▶️ **Play** | Compila y lanza el juego con el target seleccionado. |
| 🐛 **Debug** | Igual, pero abre la ventana de depuración. |
| 📦 **Create Executable** | Genera el paquete ejecutable final (también en el menú *Build*). |

### Los formatos de salida (*Output*)

| Salida | Qué es | Cuándo usarla |
|---|---|---|
| **GMS2 VM** | Un *runner* genérico por plataforma que **interpreta** tu código. | Desarrollo. Builds rapidísimos. También válido para juegos pequeños donde el rendimiento no va a ser problema. |
| **GMS2 YYC** | El **YoYo Compiler** traduce tu GML a **C++** y lo compila a código nativo con el compilador de la plataforma. Elimina funciones que no usas y aplica optimizaciones. | Builds finales y proyectos grandes o intensivos en CPU. Puede multiplicar el rendimiento **×2 o ×3**, sobre todo en juegos con mucha lógica. |
| **JavaScript** | Solo para targets como HTML5. Emite **ECMAScript 2015 (ES6)**. | Web. |
| **GMRT / GMRT VM** | El nuevo *GameMaker Runtime*, actualmente en desarrollo. | Experimental, según plataforma. |

> **Nota:** "GMS2" en los nombres se refiere a que el runner actual viene de la era GameMaker Studio 2, frente al nuevo GMRT.

### Checklist antes de compilar el build definitivo

1. **Limpia la caché del Asset Compiler** (icono de escoba 🧹 arriba en el IDE). GameMaker cachea muchos archivos para acelerar la compilación y a veces se corrompen.
2. **Debes estar logueado** (menú de cuenta) o no podrás crear el ejecutable.
3. Ten instalados los **SDKs y build tools** de la plataforma y rellenadas sus *Platform Preferences*.
4. El tamaño máximo del paquete final es **4 GB** (sin contar sonidos en streaming, texturas dinámicas e *Included Files*).
5. Si usas **YYC**, los tiempos de compilación son más largos; es normal.

### Formatos por plataforma

| Plataforma | Qué genera |
|---|---|
| **GX.games** | Subida directa o ZIP local. Opciones *Game* / *Live Wallpaper* / *Game Strip*. |
| **Windows** | *Installer* o *Zip*, para x64 (y opción separada para Arm64). **Solo compila ejecutables de 64 bits.** |
| **Ubuntu (Linux)** | `.AppImage` (distribución general) o `.zip` (exclusivo para Steam, usa el Steam Runtime; **no** es un zip normal). |
| **HTML5** | Un `index.html` + carpeta con los archivos del juego. Hay que subir **ambos** al servidor. |
| **Android** | `.apk` (otras tiendas) o `.aab` (obligatorio para Google Play). |
| **iOS** | Un `.xarchive` que luego se usa en Xcode. **Requiere un Mac** y los certificados. |
| **macOS** | *DMG* (instalador) o *Zip* (`.app` o `.pkg`, según si vas al Mac App Store). **Requiere un Mac**. |
| **Reddit** | No permite debug mode ni ejecutable; se compila con el botón Run (F5). |

Sobre optimizaciones que hace el compilador: ver *Compiler Optimisations*. Por defecto, **los assets que no se referencian directamente en el código se eliminan** del ejecutable. Puedes desactivarlo en las Game Options o preservar tags concretos con:

```gml
gml_pragma("MarkTagAsUsed", "mis_assets_importantes");
```

---

## 7. Importar / exportar proyectos (YYZ)

GameMaker permite **exportar** el proyecto a un único archivo `.yyz` (y **importarlo** de vuelta) desde el menú *File* → *Export Project* / *Import Project*. Un `.yyz` es básicamente un ZIP de la carpeta del proyecto con su `.yyp`.

**Cuándo usarlo:**
- Para hacer una copia de seguridad completa antes de un cambio gordo.
- Para mover el proyecto entre máquinas sin Git.
- Para compartirlo con alguien.

**Cuándo NO usarlo:** para el trabajo diario. Un `.yyz` es una foto estática: no tiene historial, no hace merge, no te dice qué cambió. Para eso está el control de versiones.

---

## 8. Control de versiones (Git)

GameMaker tiene soporte integrado de **Source Control** que se activa en las **Game Options**.

### Qué hace GameMaker por ti

Si activas *Add skeleton .git defaults to new/imported projects* en las Plugin Preferences, añade a los proyectos nuevos e importados:
- Un **`.gitignore`** con patrones útiles (archivos que Windows y macOS meten en carpetas, tipos temporales, etc.). Por ejemplo, añade `*.resource_order` al `.gitignore` por defecto, ya que ese archivo solo guarda el orden visual del Asset Browser y suele generar conflictos tontos en equipos.
- Un **`.gitattributes`**.

### Recomendaciones prácticas

```gitignore
# Ejemplo de .gitignore para un proyecto GameMaker
*.resource_order
.DS_Store
Thumbs.db
*.yy.bak
```

**Reglas de trabajo:**
- Commits **atómicos y frecuentes**. Un proyecto de GameMaker genera muchos archivos pequeños; un commit por feature, no por día.
- **Nunca** edites `.yy`/`.yyp` a mano para resolver un conflicto de merge: usa el IDE o `gm-cli resourcetool`.
- Si trabajas en equipo, coordina quién toca rooms y objetos: son los archivos que más conflictos generan.
- El `.yyz` **no** sustituye a Git: úsalo como backup puntual, no como historial.

---

## 9. Atajos que merece la pena memorizar

| Atajo | Acción |
|---|---|
| **F5** | Run / Play |
| **F6** | Debug |
| **F9** | Poner/quitar breakpoint en la línea actual |
| **F1** o clic con botón central sobre un nombre de función | Abre el script que contiene esa función |
| **Ctrl/Cmd + Shift + F** | Buscar y reemplazar en todo el proyecto |
| **Ctrl/Cmd + X / C / V** | Cortar / copiar / pegar eventos |
| **Shift + clic izq.** en la lista de eventos | Selección múltiple de eventos (para borrarlos juntos) |
| **Doble clic lento** sobre un asset | Renombrarlo |
| **Doble clic** en el porcentaje de zoom | Resetear zoom al 100 % |

---

## 10. Cómo se organiza un proyecto (opinión con fundamento)

Dos estrategias, según el tamaño:

**A. Por tipo de asset** (proyectos pequeños / prototipos)
```
Sprites/
Objects/
Scripts/
Rooms/
Sounds/
```

**B. Por funcionalidad o nivel** (proyectos medianos/grandes)
```
01_Core/          → obj_game, scr_estado_global, macros
02_Entidades/     → jugador, enemigos, proyectiles
03_UI/            → HUD, menús
04_Levels/
   Level_01/
   Level_02/
```

La B escala mucho mejor: cuando un nivel deja de interesarte, borras una carpeta y se va todo. Además se lleva de maravilla con los **tags** (`Level_01`) y con los **colores** del Asset Browser.

Sea cual sea, **crea un script de inicialización global** y úsalo para centralizar constantes:

```gml
/// @description Constantes globales del juego (Script: scr_config)
///              Se ejecuta ANTES de arrancar el juego, en scope global.

// --- Macros: valores simples o expresiones ---
#macro GRAVEDAD        0.5
#macro VEL_MAXIMA      8
#macro COLOR_ACENTO    make_colour_hsv(210, 180, 255)

// --- Enums: listas de enteros con nombre ---
enum EstadoJuego
{
    MENU,
    JUGANDO,
    PAUSA,
    GAME_OVER
}

enum TipoDano
{
    FISICO,
    FUEGO,
    HIELO,
    VENENO
}

// --- Variables globales (con prefijo explícito) ---
global.estado       = EstadoJuego.MENU;
global.puntuacion   = 0;
global.vidas        = 3;
```

> **¿Por qué en un Script y no en el Create de un objeto?** Porque los scripts se parsean a nivel global y se compilan **al inicio del todo**, antes de que cargue la primera room. Así tienes las constantes listas desde el primer frame, sin depender del orden de creación de instancias.

---

## Resumen

- El proyecto es una **carpeta** con `.yyp` + archivos `.yy` por recurso. No los edites a mano.
- El **Asset Browser** lo organiza todo: grupos, colores y **tags** (que además son usables en código).
- Necesitas **al menos una room**; la primera de la lista es la *home room*.
- **VM** para desarrollar, **YYC** para el build final (×2–×3 de rendimiento en lógica pesada).
- Limpia la caché del compilador antes de cada release.
- `.yyz` para backups puntuales, **Git** para el trabajo diario.
- Prefijos `spr_`, `obj_`, `rm_`, `scr_`, `snd_`… y activa la regla **GM2017** en Feather para que el IDE te los aplique solo.
