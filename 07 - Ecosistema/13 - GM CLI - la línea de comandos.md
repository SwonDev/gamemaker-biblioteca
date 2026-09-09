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
| `--errors-only` | Silencia todo salvo errores de sintaxis GML. Ideal para iterar rápido o en CI — **no para la última compilación antes de publicar** (ver el aviso debajo). |
| `--toolchain-options` | JSON con opciones específicas del toolchain. **No es JSON libre**: ver abajo. |

### `--toolchain-options`: el esquema completo, y lo que desbloquea

Ningún documento lo decía, pero este flag es la puerta a **DMG, instalador NSIS, AppImage, AAB y
la firma de Android entera desde la línea de comandos**. Se valida contra
`<proyecto>/.gmcache/schemas/gm-options-schema-2.json`, y la trampa está en el nivel: **lo que se
pasa por la CLI es el sub-objeto del toolchain, sin la clave `gms2` por fuera.**

```console
$ gm-cli compile --toolchain-options '{"gms2":{"mac":{"packageType":"dmg"}}}'
Invalid --toolchain-options for GMS2:  - Unrecognized key: "gms2"    ← el error típico

$ gm-cli compile --toolchain-options '{"mac":{"packageType":"dmg"}}'
        ← aceptado
```

En el `gm-options.json` que `init` deja en la raíz sí va el archivo completo, con `gms2`/`gmrt`
por fuera. Claves aceptadas, sacadas del propio esquema (verificado el 08-09-2026):

| Clave | Valores | Para qué |
|---|---|---|
| `windows.packageType` | `zip` · `nsis` | ZIP o **instalador NSIS** |
| `mac.packageType` | `zip` · `dmg` | ZIP o **DMG** |
| `linux.packageType` | `zip` · `appimage` | ZIP o **AppImage** |
| `android.packageType` | `apk` · `aab` | APK o **Android App Bundle** (el que pide Play) |
| `operagx.packageType` | `zip` · `wallpaper` · `gamestrip` | Formatos de GX.games |
| `android.keystoreFile` · `keystorePassword` · `keystoreAlias` · `keystoreAliasPassword` | strings | **Firma de Android completa por CLI** |
| `android.sdkPath` · `ndkPath` · `jdkPath` | rutas | Cadena de herramientas Android |
| `windows.visualStudioSdk` | ruta a `VsDevCmd.bat` | YYC en Windows |
| `operagx.emscriptenSdk` | ruta | YYC en Opera GX |
| `gmrt.buildGraph.{mac,windows,linux}` | ruta `.xml` | Grafo de build de GMRT |
| `gmrt.jobRun` · `jobCompile` · `jobPackage` | string, por `<plataforma>.<vm\|native>` | Sustituir un *job* de GMRT por un comando propio |
| `gmrt.scriptBuildType` | `Release` · `Debug` | Tipo de build del GML compilado en GMRT |

Las 46 claves salen de leer el propio `.gmcache/schemas/gm-options-schema-2.json` del proyecto,
y las cuatro respuestas del comando están comprobadas en vivo (09-09-2026). Un valor fuera de la lista da un error claro
(`mac.packageType: Invalid option: expected one of "zip"|"dmg"`), y un JSON mal formado también
(`--toolchain-options is not valid JSON`). Es de los pocos sitios del CLI donde los mensajes
ayudan.

> 🔐 **Nunca metas la contraseña del keystore en un `gm-options.json` versionado.** Pásala por
> `--toolchain-options` desde un secreto de CI. Es una clave de firma: quien la tenga puede
> publicar actualizaciones de tu juego en Play.

> ⚠️ **`--config` con un nombre que no existe no da un error limpio**: revienta con
> `KeyNotFoundException: The given key 'NoExiste' was not present in the dictionary`. Comprueba el
> nombre antes. Y en `resourcetool`, el flag va **antes** del comando:
> `gm-cli resourcetool eval --config Demo "<comando>"`.

### Fijar el runtime LTS 2026

```bash
gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only
```

Compilación verificada sobre el proyecto de prueba: **sin salida y código de salida 0**.

Cuando hay un **error de sintaxis GML**, sí se imprime. Prueba real rompiendo a propósito
`objects/obj_player/Step_0.gml` con `var _horizontal = ;`:

```
Command failed:
gml_Object_obj_player_Step_0(0) : unexpected symbol ";" in expression
/Users/adrianpereradelgado/Library/Caches/GameMakerCLI/runtimes-gms2/runtime-2026.0.0.23/bin/assetcompiler/osx/arm64/GMAssetCompiler.dll exited with non-zero status (1)
```

> ⚠️ **`--errors-only` no muestra los `WARNING` ni algunos *crashes* reales del `AssetCompiler`
> — solo errores de sintaxis GML con código de salida distinto de 0.** Verificado en vivo: un
> *included file* creado por `resourcetool` sin su archivo físico en `datafiles/` produce
> `WARNING :: datafile ... was NOT copied` compilando sin el flag, y **exit 0 sin ninguna línea**
> con `--errors-only` — indistinguible de una compilación realmente limpia. Úsalo para iterar
> rápido; **antes de dar un juego por terminado, compila al menos una vez sin el flag** y lee la
> salida completa. Detalle con las dos compilaciones reales en
> [`12 · 09` §0 Trampa 8](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-8--resource-create-typeincludedfile-deja-filepath-fuera-de-datafiles-y---errors-only-no-lo-detecta).

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

> ⚠️ **Si un agente de IA ejecuta esto y se cuelga sin salida durante 20-30 segundos**: no es
> `resourcetool`, es `npx` verificando el paquete contra el registro bajo un sandbox de red
> restringido (el modo por defecto del Bash tool de Claude Code). Receta de emergencia (dos
> niveles, con el comando exacto para invocar el binario ya cacheado sin pasar por `npx`) en
> [`12 · 09` §0, Trampa
> 2](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-2--resourcetool-eval-y-compile-pueden-colgarse-bajo-el-sandbox-del-bash-tool).

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

> ⚠️ **`FOLDER CREATE` no comparte argumentos con `RESOURCE CREATE`**, aunque la tabla los ponga
> uno junto al otro y sea tentador adivinar por analogía. `RESOURCE CREATE` se coloca con
> `TYPE / NAME† / PARENT† / FOLDER†`; `FOLDER CREATE` solo acepta `FOLDER†` — la ruta de la
> carpeta a crear, no un destino junto a un `NAME`/`TYPE`. Verificado en
> `_indice/auditorias/r5-prueba-e2e.md` §5: pedir `folder create name=Objetos type=object` no da
> ningún error — cada argumento sobrante se ignora en silencio (`Ignoring Argument: NAME` /
> `Ignoring Argument: TYPE`) y la carpeta se crea en la **ruta vacía** (`''`) en vez de donde se
> pretendía. La forma correcta: `folder create folder=<ruta>` (por ejemplo, `folder create
> folder=Objetos/Enemigos`).

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

### La raíz de expresión `project`: lo que `RESOURCE INFO`/`RESOURCE SET` no anuncian

Los ejemplos de `HELP RESOURCE INFO`/`HELP RESOURCE SET` solo muestran nombres de recursos como
raíz (`spr_ufo`, `obj_ship`, `room_welcome`…), pero **`project` es otra raíz de expresión
válida**, con 18 miembros propios — configuraciones de build, grupos de audio y textura, archivos
incluidos, metadatos del paquete, el orden de las salas y más — que el `HELP` no lista en
ninguna parte. Se descubre con `gm-cli resourcetool eval "resource info expr=project"`: 18
campos — `AudioGroups`, `configs`, `defaultScriptType`, `Folders`,
`ForcedPrefabProjectReferences`, `FullName`, `IncludedFiles`, `isDnDProject`, `isEcma`,
`LibraryEmitters`, `MetaData`, `name`, `parent`, `resources`, `RoomOrderNodes`, `tags`,
`templateType`, `TextureGroups`.

Tabla completa de los 18 (qué se lee, qué se escribe, para qué le sirve a un agente) y el orden
de las salas — que vive aquí, en `project.RoomOrderNodes` — en
[`12 · 09` §9 y §9 bis](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#9-bis--la-raíz-project-18-miembros-probados-uno-a-uno).
Verificado el 8 de septiembre de 2026.

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

## 11 bis. La puerta de estilo: un job que de verdad falla

Los dos *workflows* que genera `init` compilan y empaquetan. Eso rechaza el código que **no
compila** — que es mucho, pero deja pasar cualquier cosa que compile: llaves donde a cada uno le
apetezca, tabulaciones mezcladas con espacios, ternarios de tres pantallas. Si trabajas con
agentes de IA eso importa el doble, porque cada agente formatea a su gusto y el `diff` acaba
siendo ruido puro.

**La pieza que falta es un *check* de formato**, y para montarlo hay que saber un dato que ningún
README pone por delante: de las cuatro herramientas de estilo del ecosistema, **solo GoboCat
devuelve un código de salida distinto de 0** cuando encuentra algo mal. Las otras tres imprimen
el problema y terminan en éxito, así que un job construido sobre ellas **pasa siempre en verde**.
El detalle de por qué, con el código fuente de cada una, está en
[`12 · 01 §2`](../12%20-%20Utilidades%20e%20integraciones/01%20-%20Herramientas%20del%20flujo%20de%20trabajo.md#2-formatear-y-analizar-el-c%C3%B3digo).

### `estilo.yml` — formato comprobado en cada PR

```yaml
name: Estilo

on:
  pull_request:
  push:
    branches: [main]

env:
  # Fija la versión. El propio README de GoboCat avisa de que las opciones y el
  # comportamiento «change weekly»: con `latest`, un formateador que cambia de
  # opinión rompe PRs que no han tocado nada.
  GOBO_VERSION: v0.7.1

jobs:
  formato:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Instalar GoboCat
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          set -euo pipefail
          gh release download "$GOBO_VERSION" \
             --repo EttyKitty/GoboCat \
             --pattern 'gobo-linux-x64.zip' \
             --output gobo.zip
          unzip -q gobo.zip            # el zip contiene un único binario: `gobo`
          chmod +x gobo
          ./gobo --version

      # --check no toca los archivos y sale con 1 si alguno necesita formato.
      - name: Comprobar formato
        run: ./gobo --check ./scripts ./objects
```

Tres detalles que hacen que este job funcione y no es evidente que hagan falta:

- **`gh` viene instalado en los *runners* de GitHub** y `GH_TOKEN: ${{ github.token }}` le basta
  para descargar de un repositorio público. Así no hay que escribir a mano la URL del *asset*,
  que es justo lo que se rompe cuando el proyecto renombra sus binarios.
- **`set -euo pipefail`**: sin `-e`, un fallo en la descarga deja el paso en verde y el
  `--check` siguiente se ejecuta sobre un binario que no existe.
- **Apuntar a `./scripts` y `./objects`, no a `.`**. GoboCat ya ignora `node_modules`,
  `extensions`, `.git`, `.svn`, `prefabs`, `bin` y `obj`, pero no las carpetas de un proyecto de
  GameMaker; darle la raíz entera lo hace recorrer `datafiles` y los `.yy` sin necesidad.

> ⚠️ **Un formateador no es un analizador.** Esto comprueba **forma**, no corrección: pasa
> igual de verde con una variable sin inicializar o una función que no existe. Las tres puertas
> se complementan y ninguna sustituye a las otras: `gm-cli compile` (¿compila?), GoboCat
> (¿está formateado?) y Feather dentro del IDE (¿tiene sentido?). Si solo puedes tener una,
> quédate con la primera.

### El *hook* de pre-commit

El mismo binario, en local, antes de que el problema llegue al repositorio. En
`.git/hooks/pre-commit`, con permiso de ejecución (`chmod +x`):

```bash
#!/usr/bin/env bash
# Rechaza el commit si algún .gml en el índice está sin formatear.
set -euo pipefail

# Solo los archivos GML que se van a commitear, no el repositorio entero:
# un hook que tarda diez segundos se acaba desactivando.
mapfile -t ARCHIVOS < <(git diff --cached --name-only --diff-filter=ACM -- '*.gml')
[ ${#ARCHIVOS[@]} -eq 0 ] && exit 0

if ! command -v gobo >/dev/null 2>&1; then
    echo "⚠️  gobo no está en el PATH; me salto la comprobación de formato."
    exit 0          # avisar, no bloquear a quien aún no lo ha instalado
fi

if ! gobo --check "${ARCHIVOS[@]}"; then
    echo
    echo "✗ Hay GML sin formatear. Arréglalo con:"
    echo "    gobo ${ARCHIVOS[*]}"
    echo "  y vuelve a añadir los archivos (git add) antes de commitear."
    exit 1
fi
```

> 💡 **`--diff-filter=ACM` y no el repositorio entero.** Sin ese filtro el *hook* también
> examina archivos borrados (`gobo` falla porque no existen) y, al pasarle el proyecto completo,
> tarda lo suficiente como para que alguien acabe usando `--no-verify` por costumbre. Un *hook*
> que se salta la gente no es una puerta.
>
> ⚠️ **`.git/hooks/` no viaja en el repositorio.** Cada persona —y cada agente que clone— tiene
> que instalarlo. O bien lo guardas versionado en `.githooks/` y lo activas con
> `git config core.hooksPath .githooks`, que sí se puede documentar en el README y automatizar,
> o bien asumes que el *hook* es una comodidad local y **la puerta de verdad es el job de CI**.
> Las dos opciones son razonables; lo que no funciona es creer que tienes puerta porque un
> archivo existe en tu `.git`.

### Lo que NO se puede automatizar hoy, y por qué

| Quieres | Con qué | Estado real (08-09-2026) |
|---|---|---|
| Rechazar lo que no compila | `gm-cli compile` | ✅ `compile.yml`, §11 |
| Rechazar lo mal formateado | `gobo --check` (GoboCat) | ✅ arriba |
| Rechazar por reglas de estilo/nomenclatura | duck | ❌ sin *release* instalable; ver `12 · 01 §2` |
| Rechazar por reglas de un linter npm | `@turlututu-games/gml-linter` | ❌ termina en 0 aunque encuentre violaciones |
| Rechazar por avisos de Feather | — | ❌ Feather solo vive dentro del IDE; no tiene CLI |

**Ese último hueco es el que más duele** y conviene decirlo claro en vez de sugerir un apaño:
Feather es el mejor analizador de GML que existe y **no se puede ejecutar desde línea de
comandos**. No hay `gm-cli feather`, ni un modo *headless* del IDE que escupa sus avisos. Todo
lo que un agente puede automatizar hoy en materia de calidad de GML es: que compile, que esté
formateado, y las comprobaciones que tú mismo escribas.

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

**No es solo `Platformer`**: de las 18 plantillas de juego, **9 fallan y 9 funcionan**. La
tabla completa con las 18, verificada una a una, vive en un solo sitio para no duplicarla y
que se desactualice — [`12 · 09` §0, Trampa
1](../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md#trampa-1--9-de-las-18-plantillas-de-gm-cli-init-fallan-hoy-en-macos).
Como referencia rápida, las tres que se probaron primero en esta sesión:

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

> 🔴 **`Failed to fetch templates:` (sin nada detrás) suele ser límite de tasa, no un fallo tuyo.**
> `gm-cli init` descarga la plantilla de `api.gamemaker.io` **en cada invocación**, y esa API
> limita por tasa: tras varios `init` seguidos —lo normal en una sesión de verificación o en un
> CI— responde **429** y el CLI se queda con ese mensaje truncado. Comprobado el 09-09-2026,
> justo mientras se escribía esto:
>
> ```console
> $ curl -s -o /dev/null -w "%{http_code}" https://api.gamemaker.io/api/gamemaker/project-templates
> 429
> ```
>
> Se pasa solo en unos minutos. Y si tu herramienta crea un proyecto de prueba en cada pasada,
> **guárdate una copia del proyecto vacío la primera vez** y restáurala cuando el `init` falle:
> es lo que hace `_indice/validar-compilacion-docs.py` desde ese día, y con ello la validación
> de los 3448 bloques dejó de depender de la red.

### La causa raíz, y por qué sí tiene arreglo

> ❌ **Corrección del 08-09-2026.** Este documento decía que la única salida era el IDE. No lo es:
> la causa está aislada y hay dos rodeos verificados de punta a punta, uno de ellos sin IDE.

**No falla la plantilla: falla el resolutor de paquetes.** `gm-cli compile --verbose` enseña la
traza real — `PackageTool@2024.14.29` revienta con `Parameter count mismatch` dentro de
`GmpmBindings.GetAvailablePackages` antes de consultar nada. Es un desfase de firma entre
`PackageTool` (versión 2024, la única publicada) y el `gmpm.dll` que `gm-cli` se descarga, que es
más nuevo (79 872 bytes contra los 64 512 del IDE). Reproducido invocando el binario a pelo, fuera
de `gm-cli`. Falla, por tanto, **todo lo que resuelva un paquete del registro**: las 9 plantillas,
los comandos `PREFAB`, y también poner un filtro de capa (`effectType`) en una sala.

> ⚠️ Y `PREFABS RESTORE exited with code 1` **es un mensaje genérico**: quiere decir «no se pudo
> cargar el proyecto», no forzosamente que falten prefabs. No lo tomes como diagnóstico; el
> diagnóstico está en `compile --verbose`.

### Soluciones, de mejor a peor

1. **Parchea el `gmpm.dll` con el del IDE.** Ejecutado paso a paso el 09-09-2026: tras esto,
   `gm-cli init -t "Platformer"` crea el proyecto **y compila** con `exit 0`.

   ```bash
   CACHE=~/.gmcli-cache
   IDEDLL="$HOME/Library/Application Support/Steam/steamapps/common/GameMaker Studio 2/GameMaker.app/Contents/MacOS/arm64/gmpm/gmpm.dll"

   cp -R <un-proyecto-cualquiera>/.gmcache "$CACHE"        # la caché es POR PROYECTO: cópiala
   cp "$IDEDLL" "$(find "$CACHE" -name gmpm.dll | head -1)"
   gm-cli init --no-interactive -n MiJuego -t "Platformer" --cache-dir "$CACHE"
   cp "$IDEDLL" "$(find MiJuego/.gmcache -name gmpm.dll | head -1)"    # ← imprescindible
   ```

   La caché de herramientas vive en el `.gmcache` de cada proyecto, así que copiarla de uno que
   ya exista ahorra los ~167 MB de descarga. (Si no tienes ninguno, un `init` con `--cache-dir`
   que **falle** también la deja poblada.)

   > 🔴 **La última línea es la que falta en todas partes.** El proyecto recién creado se hace su
   > propia `.gmcache` con el `gmpm.dll` roto: sin parchearla, cualquier comando posterior sin
   > `--cache-dir` vuelve a dar `PREFABS RESTORE exited with code 1`, y parece que el rodeo no
   > sirvió. Con ella, `resourcetool` funciona sin ningún flag.

2. **Arrastra la carpeta `.gmcache/prefabs` ya resuelta** desde un proyecto sano. **No necesita
   IDE**, que es lo que la hace la vía buena en CI: los *workflows* que genera `init` ya cachean
   `.gmcache` con `actions/cache@v5`, así que basta con poblarla una vez desde una máquina buena.

3. **Usa una plantilla sin prefabs** y añade los prefabs después desde el IDE
   (`Package Manager` → `Prefab Library`).

   ```bash
   gm-cli init --no-interactive -n MiJuego -t "Space Rocks" --ai --actions
   ```

4. **Crea el proyecto desde la interfaz de GameMaker**, que usa el `ProjectTool` y el `gmpm.dll`
   de su propia instalación.

> 💡 **Y hay una vía que no pasa por `init`**: la API expone la URL de descarga de **las 31**
> plantillas, y el `.yymps` es un ZIP normal con el `.yyp` dentro.
>
> ```bash
> curl -s https://api.gamemaker.io/api/gamemaker/project-templates \
>   | python3 -c "import json,sys;[print(t['attributes']['info_title'],'|',t['attributes']['gml_code_download_url']) for t in json.load(sys.stdin)['data']]"
> curl -sL "https://api.yoyogames.com/api/2/download?package_id=com.yoyogames.windywoods&version=1.2.2" -o plataformer.yymps
> unzip -q plataformer.yymps -d MiPlat
> ```
>
> Sigue haciendo falta uno de los dos rodeos para que los prefabs se resuelvan, pero da acceso al
> catálogo entero sin depender de `gm-cli init`.

> ⚠️ **Lo que NO funciona**, probado y descartado: `prefabsfolder=` apuntando a `packages/` del
> IDE, a `gm-ide-prefabs` o a un prefab suelto; copiar el `.yymps` a mano a `.gmcache/prefabs` o a
> `<proyecto>/prefabs`; y `projecttool=` apuntando al `ProjectTool` del IDE, solo o combinado con
> `prefabsfolder=`. Seis variantes, las seis con el mismo error.

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
