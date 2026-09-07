# 13 · GM CLI — la línea de comandos de GameMaker

> **Estado de la documentación**: todo lo que aparece aquí se ha ejecutado de verdad en este Mac
> (31 de agosto de 2026). Las salidas son copias literales de la terminal, no recreaciones.
>
> **Entorno verificado**
> - `gm-cli` **2.3.0** instalado global en `/opt/homebrew/bin/gm-cli` — es también la última publicada en npm (reverificado el **2 de septiembre de 2026**)
> - GameMaker **LTS 2026.0** — IDE 2026.0.0.16 / GMS2 Runtime 2026.0.0.23
> - Licencia Professional activa vía variable de entorno `GAMEMAKER_CLI_LICENSE`
> - macOS 26 (Darwin 25.5), Apple Silicon

---

## 1. Qué es y por qué importa

`gm-cli` es la interfaz de línea de comandos oficial de GameMaker, publicada por YoYo Games como
paquete npm `@gamemaker/gm-cli`. Es **código abierto con licencia Apache-2.0**.

| Dato | Valor verificado |
|---|---|
| Paquete npm | [`@gamemaker/gm-cli`](https://www.npmjs.com/package/@gamemaker/gm-cli) |
| Repositorio | <https://github.com/YoYoGames/gm-cli> |
| Licencia | `Apache-2.0` (campo `license` del `package.json`) |
| Binario | `gm-cli` (entrada `dist/cli.js`) |
| Node requerido | `>=24` (campo `engines`) |
| Versión publicada más reciente | `2.3.0` |
| Historial de versiones npm | `1.2.1, 1.3.0, 1.4.0, 1.4.1, 2.0.0, 2.1.0, 2.2.0, 2.3.0` |
| Repo creado / último push | 2026-03-25 / 2026-08-17 |

### Por qué es importante

1. **Integración continua (CI/CD)**. Es la primera forma oficial de compilar y empaquetar un juego
   de GameMaker **sin abrir el IDE**. `gm-cli init` genera además dos workflows de GitHub Actions
   listos para usar (`compile.yml` y `package.yml`).
2. **Automatización headless**. Granjas de build, pipelines, tests nocturnos: el CLI descarga él
   mismo el runtime y las herramientas que necesita.
3. **Edición de proyectos sin IDE** mediante `resourcetool`, que es la única vía soportada para
   tocar recursos sin corromper el proyecto.
4. **Es la puerta de entrada de los agentes de IA**: `resourcetool mcp` expone el proyecto como
   servidor MCP (Model Context Protocol).

### El MCP es POR PROYECTO, no global

`gm-cli resourcetool mcp` **exige un `.yyp`**. Fuera de un proyecto GameMaker el servidor se cierra
al arrancar. Por eso el andamiaje de `gm-cli init` escribe un `.mcp.json` **dentro del proyecto**:

```json
{
  "mcpServers": {
    "gamemaker-resource-tool": {
      "type": "stdio",
      "command": "npx",
      "args": ["@gamemaker/gm-cli@latest", "resourcetool", "mcp"],
      "env": {}
    }
  }
}
```

Consecuencia práctica: **cada proyecto necesita su propio `.mcp.json`**, y el agente debe arrancar
con el directorio de trabajo puesto en la carpeta del `.yyp`. Para un proyecto creado a mano:

```bash
# Genera el .mcp.json de un proyecto existente (lo hace gm-cli init al crear el proyecto)
gm-cli init
```

---

## 2. Ayuda raíz (salida real)

```bash
gm-cli --help
```

```
USAGE
  gm-cli init
  gm-cli run
  gm-cli compile
  gm-cli package
  gm-cli manual read|open ...
  gm-cli resourcetool mcp|eval|repl|script ...
  gm-cli login <access-key>
  gm-cli gxgames link|upload|meta|publish ...
  gm-cli cache info|clean ...
  gm-cli --help
  gm-cli --version

The GameMaker command-line interface GM-CLI is a helpful tool to edit, compile, package, and run your GameMaker projects.

FLAGS
  -h --help     Print help information and exit
  -v --version  Print version information and exit

COMMANDS
  init          Initialize a new project
  run           Run the project
  compile       Compile the project
  package       Package the project
  manual        Use the GameMaker manual
  resourcetool  Programmatically read and manipulate project resources
  login         Sign-in using an access key
  gxgames       GX.Games commands
  cache         Manage the cache
```

`gm-cli --version` imprime la versión y, **si hay una más nueva**, un aviso. Con la 2.3.0
instalada (la última publicada) ya no aparece ese aviso; así se veía cuando sí lo había:

```
Latest available version is 2.3.0 (currently running 2.2.0), upgrade with "npm install -g @gamemaker/gm-cli"
2.2.0
```

> Ese aviso se imprime en **todos** los comandos mientras haya versión nueva.

---

## 3. `gm-cli init` — crear un proyecto

```bash
gm-cli init --help
```

```
USAGE
  gm-cli init
  gm-cli init --help

Initialize a new project

FLAGS
     [--interactive/--no-interactive]  Run interactive wizard                                           [default = true]
  -n [--name]                          Project name (required if --no-interactive)
  -t [--template]                      Template ID or partial name match (required if --no-interactive)
     [--ai/--no-ai]                    Set up AI scaffolding (MCP, CLAUDE.md, etc.)                     [default = true]
     [--actions/--no-actions]          Set up GitHub Actions workflows                                  [default = true]
     [--toolchain]                     Toolchain to use, e.g. GMS2, GMS2@2024.14.4, or GMRT@0.18
     [--cache-dir]                     Cache directory
  -h  --help                           Print help information and exit
```

### Ejemplo ejecutado de verdad

```bash
mkdir -p /tmp/gmtest && cd /tmp/gmtest
gm-cli init -n PruebaCLI -t "Blank Pixel Game" --no-interactive
```

```
Creating project...
◇  Project created at /private/tmp/gmtest/PruebaCLI
```

### Lo que genera

```
PruebaCLI/
├── PruebaCLI.yyp            # proyecto
├── PruebaCLI.resource_order # orden del Asset Browser (nuevo en 2026.0, pensado para git)
├── gm-options.json          # toolchain por defecto: { "toolchain": "GMS2" }
├── options/                 # Game Options por plataforma
│   ├── android/ html5/ ios/ linux/ mac/ main/ operagx/
│   └── ps4/ ps5/ switch/ tvos/ windows/ xboxseriesxs/
├── rooms/
├── .gmcache/                # caché local (herramientas descargadas)
├── .gitignore  .gitattributes
├── .github/workflows/compile.yml
├── .github/workflows/package.yml
├── .claude/settings.local.json
├── .mcp.json
├── AGENTS.md
└── CLAUDE.md                # idéntico a AGENTS.md (diff vacío)
```

### Las 31 plantillas disponibles

El CLI consulta `https://api.gamemaker.io/api/gamemaker/project-templates`. Listado real,
ordenado por la posición que devuelve la API:

| # | Tipo | Plantilla |
|---|------|-----------|
| 1 | game | Blank Pixel Game |
| 2 | game | Cover Assault |
| 3 | game | RPG Starter Pack |
| 4 | game | Arcade Action Game Template |
| 5 | game | Hero's Trail Base - GML Visual |
| 6 | game | Scrolling Shooter Game Template |
| 7 | game | Idle Game Template |
| 8 | game | Card Game Template |
| 9 | game | Endless Runner Template |
| 10 | game | Twin Stick Shooter Template |
| 11 | game | Survivor Game Template |
| 12 | game | Puzzle Slider Template |
| 13 | game | Match 3 Template |
| 14 | game | Brick Breaker Template |
| 15 | game | Tower Defense Template |
| 16 | game | Platformer Template |
| 17 | game | Fire Jump Template |
| 18 | game_strip | Idle Clicker Game Strip Template |
| 19 | live_wallpaper | Fairy Flocking Live Wallpaper Template |
| 20 | live_wallpaper | Shader Live Wallpaper Template |
| 21 | live_wallpaper | Rain Live Wallpaper Template |
| 22 | live_wallpaper | Fire Live Wallpaper Template |
| 23 | game | Space Rocks |
| 24 | live_wallpaper | Opera Glitch Live Wallpaper Template |
| 25 | live_wallpaper | Opera Colours Live Wallpaper Template |
| 26 | live_wallpaper | Fractal Sky Live Wallpaper Template |
| 27 | live_wallpaper | Colour Splash Live Wallpaper Template |
| 28 | live_wallpaper | Wizardly Workshop Live Wallpaper Template |
| 29 | live_wallpaper | Enchanted Forest Live Wallpaper Template |
| 30 | live_wallpaper | Ocean Waves Live Wallpaper Template |
| 30 | live_wallpaper | Weather Station Live Wallpaper Template |

> `-t` admite el **ID UUID** o una **coincidencia parcial por nombre**. `gm-cli init -t "Empty"`
> falla: `Command failed: Template "Empty" not found`.

### Andamiaje de IA y de CI

- `--ai/--no-ai` (activo por defecto): escribe `CLAUDE.md`, `AGENTS.md`, `.mcp.json` y
  `.claude/settings.local.json`.
- `--actions/--no-actions` (activo por defecto): escribe los dos workflows de GitHub Actions.

---

## 4. `run`, `compile` y `package`

Los tres comparten casi todos los flags. Salida real de `gm-cli compile --help`:

```
USAGE
  gm-cli compile
  gm-cli compile --help

Compile the project

FLAGS
     [--target]                        The platform the game will run on ('windows', 'mac', 'linux', 'operagx', etc.)
     [--toolchain]                     Toolchain to use, e.g. GMS2, GMS2@2024.14.4, or GMRT@0.18
     [--runtime]                       Virtual machine (VM) or ahead-of-time native compilation.                      [vm|native, default = vm]
     [--verbose/--no-verbose]          Verbose output
     [--errors-only/--no-errors-only]  Suppress all output except errors
     [--license]                       License .plist file (can also set env GAMEMAKER_CLI_LICENSE)
     [--cache-dir]                     Cache directory
     [--config]                        GameMaker project config to build with (default: 'Default')
     [--toolchain-options]             JSON string of toolchain-specific options
  -h  --help                           Print help information and exit

ARGUMENTS
  [project]  Path to the project .yyp file
```

`package` añade únicamente:

```
  -o [--output]                        Output file path
```

### Flags importantes

| Flag | Significado |
|---|---|
| `--target` | Plataforma de destino. Ver la tabla de targets soportados más abajo. |
| `--toolchain` | Fija el runtime: `GMS2`, `GMS2@2026.0.0.23`, `GMRT@0.18`. |
| `--runtime vm\|native` | `vm` = GMS2 VM (por defecto); `native` = YYC (compilación anticipada). |
| `--config` | Configuración del proyecto (por defecto `Default`). |
| `--license` | Fichero `.plist` de licencia; alternativa: variable de entorno `GAMEMAKER_CLI_LICENSE`. |
| `--errors-only` | Silencia todo salvo errores. Ideal para CI. |
| `--toolchain-options` | JSON con opciones específicas del toolchain. |

### Fijar el runtime LTS 2026

```bash
gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only
```

Compilación verificada sobre el proyecto de prueba: **sin salida y código de salida 0**.

Cuando hay un error, sí se imprime. Prueba real rompiendo a propósito
`objects/obj_player/Step_0.gml` con `var _horizontal = ;`:

```
Command failed:
gml_Object_obj_player_Step_0(0) : unexpected symbol ";" in expression
/Users/adrianpereradelgado/Library/Caches/GameMakerCLI/runtimes-gms2/runtime-2026.0.0.23/bin/assetcompiler/osx/arm64/GMAssetCompiler.dll exited with non-zero status (1)
```

### Empaquetar

```bash
gm-cli package --target operagx --toolchain GMS2@2026.0.0.23 --output /tmp/pruebacli-operagx.zip
```

Salida real (cola):

```
│  Copying .../runtimes-gms2/runtime-2026.0.0.23/operagx/runner.js to .../output/runner/runner.js...
│  Copying .../runtimes-gms2/runtime-2026.0.0.23/operagx/runner.wasm to .../output/runner/runner.wasm...
│  Copying .../runtimes-gms2/runtime-2026.0.0.23/operagx/index.html to .../output/runner/index.html...
│  Igor complete.
◆  Package created: /tmp/pruebacli-operagx.zip
```

Resultado: **ZIP de 2.105.101 bytes** con el juego en HTML5 + WASM listo para GX.games.

### Targets realmente soportados por el CLI

Verificado leyendo el código del propio binario, no la documentación:

| Versión | Targets aceptados por `run` / `compile` / `package` |
|---|---|
| **2.2.0** | `mac`, `windows`, `linux`, `operagx` |
| **2.3.0** (instalada y última, verificado 07-09-2026) | `mac`, `windows`, `linux`, `operagx`, **`android`** |

Cualquier otro valor lanza un error antes de compilar:

```bash
gm-cli compile --target reddit
```

```
Command failed:
Support for target 'reddit' is coming soon to GameMaker CLI.
```

> **Importante**: Reddit/Devvit **sí** existe como target en el IDE 2026.0, pero **todavía no** en
> el CLI. Consolas, iOS, tvOS, HTML5 y el resto: tampoco. En el CLI 2.3.0 (la instalada) puedes
> compilar para escritorio (Windows/macOS/Linux), GX.games y Android; en la 2.2.0, sin Android.

---

## 5. `gm-cli manual` — el manual oficial offline

```bash
gm-cli manual read <consulta>     # imprime el contenido en la terminal
gm-cli manual open <consulta>     # abre la página en el navegador
```

Flag común: `--language` con `en|ru|br|it|fr|pl|es|ko|de|ja|zh`.

Es una búsqueda **semántica** sobre el manual. Funciona de verdad:

```bash
gm-cli manual read "instance_create_layer"
```

```
instance_create_layer

With this function you can create a new instance of the specified object at any
given point within the room and on the layer specified. ...

Syntax:

     instance_create_layer(x, y, layer_id, obj, [var_struct]);

┌────────────┬─────────────────┬──────────────────────────────────────────┐
│ Argument   │ Type            │ Description                              │
├────────────┼─────────────────┼──────────────────────────────────────────┤
│ x          │ Real            │ The x position the object will be created at │
...
Returns:

     Object Instance
```

Cada respuesta termina con la URL de origen, por ejemplo:
`Article source: https://manual.gamemaker.io/monthly/en/Quick_Start_Guide/Rooms.htm`

> Es la forma más rápida de resolver dudas de GML sin salir de la terminal y **sin adivinar**
> firmas de funciones. Úsalo antes de escribir código.

---

## 6. `gm-cli resourcetool` — editar el proyecto sin IDE

```
USAGE
  gm-cli resourcetool mcp
  gm-cli resourcetool eval <command>
  gm-cli resourcetool repl
  gm-cli resourcetool script <file>

Programmatically read and manipulate project resources
```

| Subcomando | Uso |
|---|---|
| `mcp` | Arranca como servidor MCP (stdio). Lo consume el agente de IA. |
| `eval "<comando>"` | Ejecuta **un** comando y sale. Perfecto para scripts y CI. |
| `repl` | Sesión interactiva. |
| `script <fichero>` | Ejecuta un fichero con una lista de comandos. |

Todos aceptan `[--cache-dir]`, `[--config]` y el argumento `[project]` (ruta al `.yyp`).

**La regla de oro**: nunca edites `.yy` ni `.yyp` a mano. Son archivos generados, con campos
cuyo orden y contenido gestiona GameMaker; un error manual deja el proyecto corrupto. Para la
lógica sí puedes (y debes) editar los `.gml` con tu editor normal.

### Ayuda interna

```bash
gm-cli resourcetool eval "help"        # ayuda completa
gm-cli resourcetool eval "helptable show descriptions"   # tabla resumen
```

La versión que corre por debajo es **`ResourceTool@2026.0.17`**.

### Inventario completo de comandos (ResourceTool 2026.0.17)

| Comando | Área | Argumentos († = opcional) |
|---|---|---|
| `CHECK` | — | `PROJECTPATH` |
| `CLI` | — | — |
| `EXIT` | — | — |
| `HELP` | — | `COMMAND†` |
| `HELPTABLE` | — | `SHOW†` |
| `MCP` | — | `LOGFILE† / TOOLLESS†` |
| `SCRIPT` | — | `PATH` |
| `STATUS` | — | — |
| `VERSION` | — | — |
| `ROOM ASSET CREATE` | Asset | `ROOM / SPRITE† / SEQUENCE† / PARTICLESYSTEM† / FONT† / NAME† / LAYER† / X† / Y†` |
| `AUDIOGROUP CREATE` | Audiogroup | `NAME` |
| `AUDIOGROUP DELETE` | Audiogroup | `NAME` |
| `AUDIOGROUP LIST` | Audiogroup | — |
| `AUDIOGROUP RENAME` | Audiogroup | `NAME / NEWNAME` |
| `AUDIOGROUP SET` | Audiogroup | `GROUP / RESOURCES` |
| `AUDIOGROUP USAGES` | Audiogroup | `GROUP†` |
| `CONFIG CREATE` | Config | `NAME / PARENT†` |
| `CONFIG DELETE` | Config | `NAME` |
| `CONFIG GETACTIVE` | Config | — |
| `CONFIG LIST` | Config | — |
| `CONFIG RENAME` | Config | `NAME / NEWNAME` |
| `CONFIG SETACTIVE` | Config | `NAME` |
| `CONFIG USAGES` | Config | `TYPE† / NAME† / CONFIG† / PROPERTY†` |
| `DEFAULTS GET` | Defaults | — |
| `DEFAULTS SET` | Defaults | — |
| `OBJECT EVENT CHANGE` | Event | `NAME / TYPE / SUBTYPE† / COLLISIONOBJECT† / NEWTYPE / NEWSUBTYPE† / NEWCOLLISIONOBJECT†` |
| `OBJECT EVENT DELETE` | Event | `NAME / TYPE / SUBTYPE† / COLLISIONOBJECT†` |
| `OBJECT EVENT FINDORCREATE` | Event | `NAME / TYPE / SUBTYPE† / COLLISIONOBJECT†` |
| `OBJECT EVENT LIST` | Event | `NAME / TYPE†` |
| `OBJECT EVENT SETGMLFILE` | Event | `NAME / TYPE / SUBTYPE† / COLLISIONOBJECT† / PATH†` |
| `OBJECT EVENT TYPES` | Event | — |
| `FOLDER CREATE` | Folder | `FOLDER†` |
| `FOLDER LIST` | Folder | `TYPE† / RESOURCES` |
| `FONT ADDKERNING` | Font | `NAME / FIRST / SECOND / AMOUNT` |
| `FONT ADDRANGE` | Font | `NAME / LOWER / UPPER` |
| `FONT GLYPHLIST` | Font | `NAME` |
| `FONT KERNINGLIST` | Font | `NAME` |
| `FONT RANGELIST` | Font | `NAME` |
| `FONT REMOVEKERNING` | Font | `NAME / FIRST / SECOND` |
| `FONT REMOVERANGE` | Font | `NAME / LOWER / UPPER` |
| `FONT SETFILE` | Font | `NAME / PATH` |
| `GML SETGMLFILE` | Gml | `NAME / PATH` |
| `ROOM INSTANCE CREATE` | Instance | `ROOM / OBJECT / NAME† / LAYER† / X† / Y†` |
| `ROOM ITEM DELETE` | Item | `ROOM / ITEM` |
| `ROOM ITEM LIST` | Item | `ROOM† / LAYER† / LAYERTYPE† / ITEM† / ITEMTYPE† / ALL` |
| `ROOM LAYER CREATE` | Layer | `ROOM / NAME / TYPE† / PARENT† / DEPTH†` |
| `ROOM LAYER DELETE` | Layer | `ROOM / LAYER` |
| `ROOM LAYER LIST` | Layer | `ROOM / LAYERTYPE†` |
| `ROOM LAYER TILES GET` | Layer Tiles | `ROOM / LAYER† / LEFT† / TOP† / WIDTH† / HEIGHT† / OUTFILE†` |
| `ROOM LAYER TILES INFO` | Layer Tiles | — |
| `ROOM LAYER TILES LIST` | Layer Tiles | `ROOM†` |
| `ROOM LAYER TILES RESIZE` | Layer Tiles | `ROOM / LAYER / WIDTH† / HEIGHT† / PADLEFT† / TRIMLEFT† / PADRIGHT† / TRIMRIGHT† / PADTOP† / TRIMTOP† / PADBOTTOM† / TRIMBOTTOM†` |
| `ROOM LAYER TILES SET` | Layer Tiles | `ROOM / LAYER / LEFT† / TOP† / WIDTH† / HEIGHT† / DATA† / FILE† / REPEATX† / REPEATY† / TRANSPARENT†` |
| `NOTE SETFILEPATH` | Note | `NAME / PATH` |
| `OPTIONS GET` | Options | `PLATFORM / PROPERTY†` |
| `OPTIONS INFO` | Options | `PLATFORM` |
| `OPTIONS LIST` | Options | — |
| `OPTIONS SET` | Options | `PLATFORM / PROPERTY / VALUE` |
| `PATH ADDPOINT` | Path | `NAME / POINTS / INDEX†` |
| `PATH DELETEPOINT` | Path | `NAME / INDEX† / COUNT†` |
| `PATH INFO` | Path | `NAME` |
| `PREFAB ADDREFERENCE` | Prefab | `COLLECTIONS` |
| `PREFAB CUSTOMISE` | Prefab | `COLLECTION / PREFAB / NAME†` |
| `PREFAB INFO` | Prefab | `COLLECTIONS` |
| `PREFAB LIST` | Prefab | `DOWNLOADED \| REFERENCED \| FORCED` |
| `PREFAB REMOVEREFERENCE` | Prefab | `COLLECTIONS` |
| `PROJECT CREATE` | Project | `NAME / PATH† / SAVE†` |
| `PROJECT RENAME` | Project | `NAME` |
| `RESOURCE CREATE` | Resource | `TYPE / NAME† / PARENT† / FOLDER†` |
| `RESOURCE DELETE` | Resource | `NAME / TYPE† / PARENT† / PARENTTYPE†` |
| `RESOURCE INFO` | Resource | `EXPR / KEYS \| LIST` |
| `RESOURCE LIST` | Resource | `TYPE†` |
| `RESOURCE SET` | Resource | `EXPR / VALUE` |
| `RESOURCE TYPES` | Resource | — |
| `ROOM LIST` | Room | — |
| `SHADER SETFILEPATH` | Shader | `NAME / PATH / TYPE` |
| `SOUND SETFILE` | Sound | `NAME / PATH` |
| `SPRITE ADDFRAME` | Sprite | `NAME / PATH / FRAME†` |
| `SPRITE DELETEFRAME` | Sprite | `NAME / INDEX` |
| `TEXTUREGROUP CREATE` | Texturegroup | `NAME` |
| `TEXTUREGROUP DELETE` | Texturegroup | `NAME` |
| `TEXTUREGROUP LIST` | Texturegroup | — |
| `TEXTUREGROUP RENAME` | Texturegroup | `NAME / NEWNAME` |
| `TEXTUREGROUP SET` | Texturegroup | `GROUP / RESOURCES` |
| `TEXTUREGROUP USAGES` | Texturegroup | `TYPE† / GROUP†` |
| `TILESET CREATE` | Tileset | `NAME† / PARENT† / SPRITE† / TILEWIDTH† / TILEHEIGHT† / TILEXOFFSET† / TILEYOFFSET† / TILEHSEP† / TILEVSEP† / TILEHBORDER† / TILEVBORDER†` |
| `TILESET DELETE` | Tileset | `NAME` |
| `TILESET RENAME` | Tileset | `NAME / NEWNAME` |
| `TILESET SETSPRITE` | Tileset | `NAME / SPRITE` |

### Los 17 tipos de recurso

```bash
gm-cli resourcetool eval "resource types"
```

```
There are 17 resource types:
animcurve
audiogroup
font
includedfile
notes
object
particlesystem
path
room
script
shader
shape
sound
sprite
texturegroup
tileset
timeline
```

### Receta completa ejecutada de verdad

Todo lo siguiente se ejecutó en el proyecto `PruebaCLI` y funcionó.

**1. Ver qué hay en el proyecto**

```bash
gm-cli resourcetool eval "resource list"
```

```
PruebaCLI resources:
────────────────────
┌────────────────────┬──────────────┐
│ Resource name      │ Type         │
╞════════════════════╪══════════════╡
│ audiogroup_default │ audiogroup   │
├────────────────────┼──────────────┤
│ Default            │ texturegroup │
├────────────────────┼──────────────┤
│ Room1              │ room         │
└────────────────────┴──────────────┘
```

**2. Crear un objeto y un script**

```bash
gm-cli resourcetool eval "resource create type=object name=obj_player"
gm-cli resourcetool eval "resource create type=script name=scr_mover"
```

```
Created resource named 'obj_player' of type 'GMObject'
Saved successfully
Created resource 'obj_player' of type 'object'
```

```
Created resource named 'scr_mover' of type 'GMScript'
Saved successfully
Created resource 'scr_mover' of type 'script'
GML file path for script 'scr_mover' is /private/tmp/gmtest/PruebaCLI/scripts/scr_mover/scr_mover.gml
```

**3. Crear eventos en el objeto**

```bash
gm-cli resourcetool eval "object event findorcreate name=obj_player type=create"
gm-cli resourcetool eval "object event findorcreate name=obj_player type=step subtype=step_normal"
```

```
New GML file: /private/tmp/gmtest/PruebaCLI/objects/obj_player/Create_0.gml
New GML file: /private/tmp/gmtest/PruebaCLI/objects/obj_player/Step_0.gml
```

Tipos de evento disponibles (`object event types`): `create`, `destroy`, `alarm` (0-11),
`step` (`step_normal` \| `step_begin` \| `step_end`), `collision`, `keyboard` (código de tecla),
`mouse` (`left_button`, `right_button`, `middle_button`, `no_button`, `left_press`,
`right_press`, `middle_press`, `left_release`, `right_release`, `middle_release`,
`mouse_enter`, `mouse_leave`) y más.

**4. Escribir la lógica (esto sí se hace con el editor, son `.gml`)**

```gml
// Create_0.gml — variables de instancia
velocidad = 4;
salud = 100;
```

```gml
// Step_0.gml — movimiento; las locales llevan el prefijo _
var _horizontal = keyboard_check(vk_right) - keyboard_check(vk_left);
var _vertical   = keyboard_check(vk_down)  - keyboard_check(vk_up);

x += _horizontal * velocidad;
y += _vertical   * velocidad;
```

**5. Capas e instancias en la room**

```bash
# Ver capas existentes
gm-cli resourcetool eval "room layer list room=Room1"
```

```
┌────────────┬─────────────────┬────────────┐
│ LAYER      │ Layer tree path │ LAYERTYPE  │
╞════════════╪═════════════════╪════════════╡
│ Instances  │ Instances       │ INSTANCE   │
├────────────┼─────────────────┼────────────┤
│ Background │ Background      │ BACKGROUND │
└────────────┴─────────────────┴────────────┘
```

```bash
# Crear una capa: el tipo va en MAYÚSCULAS
gm-cli resourcetool eval "room layer create room=Room1 name=CapacEffects type=EFFECTS"
# Tipos válidos: INSTANCE | ASSET | BACKGROUND | PATH | TILE | EFFECTS

# Colocar una instancia del objeto en la capa
gm-cli resourcetool eval "room instance create room=Room1 object=obj_player layer=Instances x=100 y=200"
```

```
New instance 'inst_39CC2A5B'
Saved successfully
```

> **Cuidado con el tipo de capa.** `type=instances` (minúsculas) falla:
> `Invalid value 'instances' for 'TYPE' argument. Expected format: INSTANCE | ASSET | BACKGROUND | PATH | TILE | EFFECTS`

**6. Verificar**

```bash
gm-cli resourcetool eval "room item list room=Room1"
```

```
┌────────────┬─────────────────┬───────────┬───────────────┬──────────┐
│ LAYER      │ Layer tree path │ LAYERTYPE │ ITEM          │ ITEMTYPE │
╞════════════╪═════════════════╪═══════════╪═══════════════╪══════════╡
│ Instances  │ Instances       │ INSTANCE  │ inst_39CC2A5B │ instance │
├────────────┼─────────────────┼───────────┼───────────────┼──────────┤
│ Background │ Background      │ BACKGROUND│ (no items)    │ (n/a)    │
└────────────┴─────────────────┴───────────┴───────────────┴──────────┘
```

**7. Game Options y configuraciones**

```bash
gm-cli resourcetool eval "options list"   # plataformas con opciones
gm-cli resourcetool eval "config list"    # configuraciones del proyecto
```

`options list` devuelve 13 plataformas:
`main`, `android`, `html5`, `ios`, `linux`, `mac`, `operagx`, `ps4`, `ps5`, `switch`, `tvos`,
`windows`, `xboxseriesxs`.

`config list` sobre el proyecto nuevo:

```
┌─────────────┬────────────┐
│ Config name │ Is active? │
╞═════════════╪════════════╡
│ Default     │ (active)   │
└─────────────┴────────────┘
```

### Modo script

Puedes guardar una lista de comandos en un fichero y ejecutarla de una vez:

```bash
gm-cli resourcetool script ./mi_script.txt
```

Y con `DEFAULTS SET` puedes fijar valores por defecto para no repetir argumentos:

```bash
gm-cli resourcetool eval "DEFAULTS SET <Comando> <SubComando> <Argumento>=<Valor>"
gm-cli resourcetool eval "DEFAULTS GET <Comando> <SubComando> <Argumento>"
```

---

## 7. `gm-cli login` — licencia

```
USAGE
  gm-cli login <access-key>

Sign-in using an access key.

You can issue an access key at: https://gamemaker.io/en/account/access-keys

FLAGS
     [--print/--no-print]  Print the license to stdout instead of saving to a file
     [--cache-dir]         Cache directory
```

```bash
# Guarda la licencia en la caché del CLI
gm-cli login "MI-ACCESS-KEY"

# O la imprime por pantalla para guardarla tú donde quieras
gm-cli login "MI-ACCESS-KEY" --print
```

**No hace falta iniciar sesión**: el CLI concede una licencia *guest* automática. Con licencia
Professional activa por `GAMEMAKER_CLI_LICENSE` tampoco hace falta login. `--license` permite
pasar un `.plist` concreto por comando.

---

## 8. `gm-cli gxgames` — publicar en GX.games

```
USAGE
  gm-cli gxgames link
  gm-cli gxgames upload (--file value)
  gm-cli gxgames meta
  gm-cli gxgames publish
```

Flujo completo de publicación en la plataforma web de GameMaker:

```bash
# 1. Vincular el proyecto con un estudio y un juego de GX.games
gm-cli gxgames link --studioid <ID> --gameid <ID>

# 2. Generar el bundle (el upload espera un ZIP de operagx)
gm-cli package --target operagx --output ./package.zip

# 3. Subirlo (pregunta el número de versión si no se lo das)
gm-cli gxgames upload --file ./package.zip --version 1.0.0.0

# 4. Rellenar los metadatos obligatorios
gm-cli gxgames meta \
  --title "Mi Juego" \
  --age-rating EVERYONE \
  --description "Un juego hecho con GameMaker" \
  --platforms DESKTOP,MOBILE \
  --cover ./cover.png \
  --graphic ./screenshot.png

# 5. Publicar
gm-cli gxgames publish
```

Detalles verificados en la ayuda real:

- `upload` acepta `--version` con formato `X.Y.Z.B` (por ejemplo `1.0.0.0`); si no se indica,
  lo pregunta de forma interactiva.
- `meta`: cada flag sobrescribe su campo; los que se omiten **conservan** el valor actual en el
  servidor.
- Valores de `--age-rating`: `NOT_SET | EVERYONE | CHILDREN | EARLY_TEENS | TEENS | ADULTS | MATURE`.
- `--platforms`: `DESKTOP,MOBILE`.
- `--cover` y `--graphic`: imágenes **16:9 exacto** (por ejemplo 1920×1080 PNG/JPG).
- `publish` exige tener bundle subido, portada, captura, descripción, clasificación por edad y
  plataformas. Al terminar abre la página del juego en el navegador.

---

## 9. `gm-cli cache` — la caché

```
USAGE
  gm-cli cache info
  gm-cli cache clean
```

```bash
gm-cli cache info                      # caché compartida (sin proyecto)
gm-cli cache info --project ./MiJuego.yyp   # añade la caché local del proyecto
```

Salida real sin proyecto:

```
Shared cache
/Users/adrianpereradelgado/Library/Caches/GameMakerCLI
Contents: version-check

Local cache
Not used. Specify a --project
```

Salida real con proyecto:

```
Shared cache
/Users/adrianpereradelgado/Library/Caches/GameMakerCLI
Contents: runtimes-gms2, version-check

Local cache
/private/tmp/gmtest/PruebaCLI/.gmcache
Contents: build-gms2-mac-VM, build-gms2-operagx-VM, gmpm, igor, package-tool, prefabs, project-tool, schemas
```

> `--project` espera la ruta al **`.yyp`**, no al directorio. Pasar un directorio da error:
> `Expected a file with the .yyp extension.`

### Qué se guarda dónde

| Ruta | Contenido |
|---|---|
| `~/Library/Caches/GameMakerCLI/` | Caché compartida: `runtimes-gms2/` (runtimes descargados), `version-check` |
| `<proyecto>/.gmcache/` | Caché local: builds por target, `gmpm` (package manager), `igor`, `package-tool`, `project-tool`, `prefabs`, `schemas` |

En CI conviene cachear `.gmcache` (es exactamente lo que hacen los workflows generados):

```yaml
- uses: actions/cache@v5
  with:
    path: .gmcache
    key: ${{ runner.os }}-gmcache
```

---

## 10. Actualizar a la 2.3.0

> ✅ **Ya hecho en este Mac** (verificado 07-09-2026): `gm-cli --version` devuelve `2.3.0`. Esta
> sección queda como guía para cuando exista una versión más nueva o para otra máquina.

El propio CLI lo sugiere con npm:

```bash
npm install -g @gamemaker/gm-cli@latest
```

Con npm, que es el gestor con el que quedó instalado en este Mac:

```bash
npm install -g @gamemaker/gm-cli@latest
```

> **Nota sobre el gestor:** pnpm es el gestor por defecto en este entorno, pero
> `@gamemaker/gm-cli` ya estaba instalado **con npm**. Actualizarlo con pnpm dejaría
> dos copias globales del binario, así que en este caso concreto se usa npm.

Para fijar exactamente la 2.3.0:

```bash
npm install -g @gamemaker/gm-cli@2.3.0
```

> **Recomendación práctica**: `gm-cli` ya está instalado en este Mac con **npm**
> (`/opt/homebrew/lib/node_modules/@gamemaker/gm-cli`). Mezclar gestores en un paquete global
> suele acabar en dos copias y en un binario que apunta a la vieja. Actualízalo con **npm** para
> mantener la coherencia, o desinstálalo con npm y vuelve a instalarlo con pnpm si prefieres
> unificar. No se ha ejecutado la actualización al redactar este documento: era documentación,
> no mantenimiento.

### Qué cambia de 2.2.0 a 2.3.0 (verificado)

| Cambio | Detalle |
|---|---|
| **Target `android`** | La lista de targets aceptados pasa de `["mac","windows","linux","operagx"]` a `["mac","windows","linux","operagx","android"]` |
| README | **Idéntico** en ambas versiones (diff vacío), así que no hay changelog oficial en el paquete |
| Repo GitHub | `YoYoGames/gm-cli` tiene **0 releases** publicados: no hay notas de versión oficiales |

Comprobación literal del binario 2.3.0:

```
if(!["mac","windows","linux","operagx","android"].includes(s)) throw new l(`Support for target '${s}' is coming soon to GameMaker CLI.`);
```

---

## 11. Los workflows de GitHub Actions que genera `init`

### `compile.yml` — en cada PR y push a `main`

```yaml
env:
  GM_COMMAND: "@gamemaker/gm-cli@latest"   # fija una versión si quieres, p. ej. @gamemaker/gm-cli@2.3.0

jobs:
  compile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/cache@v5              # cachea .gmcache entre ejecuciones
        with:
          path: .gmcache
          key: ${{ runner.os }}-gmcache
      # ffmpeg es obligatorio en Linux: https://github.com/YoYoGames/GameMaker-Bugs/issues/4977
      - name: Install FFmpeg if not cached
        run: |
          VERSION=6.0.1
          RELEASE_NAME=ffmpeg-${VERSION}-amd64-static
          mkdir -p ~/.local/share/ffmpeg-bin
          wget --timeout=8 --tries=10 https://www.johnvansickle.com/ffmpeg/old-releases/${RELEASE_NAME}.tar.xz
          tar -xf ${RELEASE_NAME}.tar.xz
          mv ${RELEASE_NAME}/ffmpeg ${RELEASE_NAME}/ffprobe ~/.local/share/ffmpeg-bin/
      - run: npx "$GM_COMMAND" login "$GAMEMAKER_PAT"   # opcional, sólo si define el secret
      - run: npx "$GM_COMMAND" compile                  # "test compile": no genera bundle
        env:
          NO_COLOR: 1
```

### `package.yml` — disparo manual (`workflow_dispatch`)

Matriz por defecto (lo demás viene comentado):

```yaml
strategy:
  matrix:
    include:
      - runner: ubuntu-latest
        target: operagx
      # - runner: ubuntu-latest
      #   target: linux
      # - runner: ubuntu-latest
      #   target: windows
      # - runner: macos-latest
      #   target: mac
```

Y el paso clave:

```yaml
- run: npx "$GM_COMMAND" package --target ${{ matrix.target }} --output ./package.zip
- uses: actions/upload-artifact@v7
  with:
    name: ${{ env.ARTIFACT_NAME }}     # nombre-target-commit.zip
    path: ./package.zip
```

> **Nota para el usuario**: el `package.yml` generado sólo tiene activo `operagx`. Descomenta los
> targets que necesites. Recuerda que en la 2.2.0 el CLI sólo acepta `mac`, `windows`, `linux` y
> `operagx` (más `android` a partir de la 2.3.0).

---

## 12. Recetas útiles

```bash
# Compilar mostrando sólo errores, con el runtime LTS 2026 fijado
gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only

# Compilación YYC (nativa) en vez de VM
gm-cli compile --runtime native --target windows

# Ejecutar el juego en local
gm-cli run

# Empaquetar para GX.games y subirlo
gm-cli package --target operagx --output ./package.zip
gm-cli gxgames upload --file ./package.zip --version 1.0.0.0

# Consultar una función sin salir de la terminal
gm-cli manual read "instance_create_layer"

# Ver el estado del proyecto
gm-cli resourcetool eval "STATUS"

# Verificar que el proyecto carga bien
gm-cli resourcetool eval "CHECK PROJECTPATH=./MiJuego.yyp"

# Limpiar la caché si algo se ha corrompido
gm-cli cache clean
```

---

## 12. Bug conocido: las plantillas con prefabs fallan al crear el proyecto

> **Verificado el 31 de agosto de 2026** y **reverificado el 2 de septiembre de 2026** en
> este Mac (macOS, Apple Silicon) con `gm-cli` **2.2.0** y **2.3.0**. No es un problema de
> versión ni de configuración: **sigue fallando en la 2.3.0**, la última publicada.

### Síntoma

```console
$ gm-cli init --no-interactive -n MiJuego -t "Platformer"
Creating project...
◒  Extracting template...  ◇  Failed
Command failed:
Failed to restore project. "ProjectTool PREFABS RESTORE" exited with code 1
```

El directorio del proyecto se crea **pero queda vacío de `.yyp`**: no hay proyecto usable.

### Alcance real (matriz de pruebas ejecutada)

| Plantilla | Resultado | ¿Genera `.yyp`? |
|---|---|---|
| `Space Rocks` | ✅ Correcto | Sí |
| `Blank Pixel Game` | ✅ Correcto | Sí |
| `Platformer` | ❌ `PREFABS RESTORE exited with code 1` | **No** |

Probado también **sin** `--toolchain` y con `--toolchain GMS2@2026.0.0.23`: el resultado es
idéntico, así que el runtime fijado no influye. Actualizar de la 2.2.0 a la 2.3.0 **no lo
arregla**.

La causa es el paso `PREFABS RESTORE` de `ProjectTool`, la utilidad que GameMaker usa al
abrir, importar y convertir proyectos. Las plantillas que incluyen **prefabs** dependen de él;
las que no, no lo ejecutan y por eso funcionan.

### Soluciones, de mejor a peor

1. **Usa una plantilla sin prefabs** y añade los prefabs después desde el IDE
   (`Package Manager` → `Prefab Library`). Es lo que recomiendo: el proyecto se crea
   correctamente y pierdes un minuto.

   ```bash
   gm-cli init --no-interactive -n MiJuego -t "Space Rocks" --ai --actions
   ```

2. **Crea el proyecto desde la interfaz de GameMaker.** El IDE usa el mismo `ProjectTool`
   pero con la versión empaquetada en su instalación, que sí resuelve los prefabs.

3. **Actualiza `ProjectTool` por el Package Manager** del IDE si hay una versión nueva
   disponible, y vuelve a probar por terminal.

### Cómo diagnosticarlo tú mismo

```bash
# 1. ¿El proyecto se creó de verdad?
ls MiJuego/*.yyp

# 2. Si no hay .yyp, reproduce y mira el paso exacto que falla
gm-cli init --no-interactive -n Prueba -t "Platformer" 2>&1 | tr '\r' '\n' | grep -iE "failed|prefab|projecttool"
```

> ⚠️ **No edites a mano los `.yy` ni el `.yyp`** para intentar arreglarlo: su formato es
> frágil y se corrompe. Si el proyecto no se crea, créalo por otra vía.

---

## 13. Fuentes

- Paquete npm: <https://www.npmjs.com/package/@gamemaker/gm-cli>
- Repositorio oficial (Apache-2.0): <https://github.com/YoYoGames/gm-cli>
- Plantillas de proyecto (API usada por `init`): <https://api.gamemaker.io/api/gamemaker/project-templates>
- Manual oficial: <https://manual.gamemaker.io/>
- Notas de versión: <https://releases.gamemaker.io/>
- Notas de la LTS 2026.0: <https://releases.gamemaker.io/release-notes/2026/0>
- Claves de acceso para `login`: <https://gamemaker.io/en/account/access-keys>
- Wiki de SDKs y guías de plataforma: <https://github.com/YoYoGames/GameMaker-Bugs/wiki>
- GameMaker Package Manager (gmpm): <https://gmpm.gamemaker.io>
- Blog "GameMaker Update Spring 2026" (GM-CLI, GMRT, roadmap): <https://gamemaker.io/en/blog/update-spring-2026>
- CLI en el blog de lanzamiento de GX.games / GMRT (nota de prensa de Opera): <https://press.opera.com/2026/04/30/gamemaker-gmrt>
