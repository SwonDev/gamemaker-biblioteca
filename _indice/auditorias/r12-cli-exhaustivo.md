# r12 · Auditoría exhaustiva del CLI de GameMaker

> **Qué es esto.** Un barrido sistemático de `gm-cli` 2.3.0 y de `ResourceTool@2026.0.17` —
> todos los comandos, todos los subcomandos, todos los tipos de recurso y sus propiedades una a
> una— ejecutado en vivo el **8 de septiembre de 2026** sobre GameMaker LTS 2026.0
> (IDE `2026.0.0.16`, runtime GMS2 `2026.0.0.23`), macOS 26 / Apple Silicon.
>
> **Dónde se ejecutó.** En proyectos de prueba propios bajo `~/auditoria_cli_r12/`, creados con
> `gm-cli init` y borrados al terminar. Nunca dentro de esta biblioteca.
>
> **La regla que gobierna este informe.** Para afirmar que algo **funciona** basta ejecutarlo una
> vez y pegar la salida. Para afirmar que algo **no funciona** hacen falta al menos **tres
> variantes sintácticas distintas**, y aquí están las tres. Donde solo se probó una vía, el texto
> dice «no lo conseguí con la sintaxis X», no «no se puede».
>
> **Lo que este informe NO repite**: la referencia de comandos de
> [`07 · 13`](../../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md)
> ni las trece trampas de
> [`12 · 09`](../../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md).
> Se construye encima de las dos: da por buenos los 18 miembros de `project`, los 17 tipos de
> `RESOURCE TYPES`, el modo por lotes `script` y el catálogo de 30 familias de `resourcetool`.

---

## 1 · Resumen ejecutivo — lo nuevo

Once hallazgos que la biblioteca no dice hoy, ordenados por cuánto cambian lo que un agente
puede entregar.

| # | Hallazgo | Impacto |
|---|---|---|
| 1 | **La causa raíz de las 9 plantillas que fallan es `PackageTool@2024.14.29` contra un `gmpm.dll` más nuevo** (`Parameter count mismatch`), y **hay dos rodeos verificados** que las arreglan del todo, sin IDE en el segundo caso. `gm-cli init -t "Platformer"` **crea y compila** el proyecto tras aplicarlos. | Corrige la Trampa 1, que hoy dice «no hay ninguna solución por CLI» |
| 2 | **`RESOURCE CREATE TYPE=shape` deja el proyecto irrecuperable** por CLI. Es uno de los 17 tipos que anuncia `RESOURCE TYPES`, falla siempre, y a partir de ahí ningún comando —ni `compile`— vuelve a cargar el proyecto | Peligro real; hay receta de reparación |
| 3 | **Todo el árbol de la sala se escribe**: tamaño, `persistent`, 8 viewports/cámaras completos, gravedad y escala de físicas, profundidad y visibilidad de cada capa, color y sprite del fondo | Cámaras, viewports y físicas de sala por CLI: nunca documentado |
| 4 | **`--toolchain-options` tiene un esquema JSON completo** en `.gmcache/schemas/gm-options-schema-2.json`: firma Android (keystore, alias, contraseñas), SDK de Visual Studio y Emscripten para YYC, y `packageType` por plataforma (`dmg`, `nsis`, `appimage`, `apk`, `aab`, `wallpaper`, `gamestrip`) | Firmar Android y empaquetar DMG/instalador desde la CLI |
| 5 | **`ProjectTool` es una segunda herramienta completa**, presente en el `.gmcache` de todo proyecto y sin documentar: `IMPORT YY` (copiar recursos entre proyectos), `EXPORT` (generar `.yymps`/ZIP con firma de Marketplace), `LINKS *`, `JSON FORMAT` (normalizar un `.yy` tocado a mano), `FILE CHANGEVERSION`, `SHOWVERSIONEDTYPES` | Empaquetado y trasvase de assets sin IDE |
| 6 | **Los recursos se renombran por CLI** con `resource set expr=X.name value=Y`, y **todas las referencias se actualizan** (sprite de un objeto, sprite de un asset de sala) | La biblioteca solo documenta `RENAME` para tileset/audiogroup/texturegroup/config |
| 7 | **Las opciones de plataforma sí se sobrescriben por configuración** con `--config`: `display_name` vale `Pixel Game` en `Default` y `JuegoDemo` en `Demo`, a la vez | Amplía la Trampa 10: las 5 propiedades escribibles lo son *por config* |
| 8 | **La velocidad de animación de un sprite se fija** con `spr_X.sequence.playbackSpeed` (y su `playbackSpeedType`) | Animación por CLI: nunca documentado |
| 9 | **Indexar una lista por nombre exige comilla simple** (`rm_test.layers['Background']`); la propia ayuda del comando anuncia comilla doble, que **falla** | Bug de la ayuda de la herramienta |
| 10 | **Un `=` dentro de un valor rompe el parser de `RESOURCE SET`** en las tres vías (`eval`, `script`, `repl`): el código de creación de una instancia no se puede escribir por CLI | Límite real nuevo, con 9 variantes probadas |
| 11 | **`gm-cli cache clean --project <yyp>` borra también la caché compartida** (los runtimes descargados), no solo la del proyecto. Solo `--cache-dir` la respeta | Trampa destructiva |

Y una corrección menor pero molesta: `12 · 09` §9 bis afirma que `projectpath=` dentro del comando
«sí funciona para `CHECK` … pero no para `RESOURCE INFO`/`RESOURCE SET` en general». **Es falso**:
`PROJECTPATH` figura en la sección *Global Arguments* de `HELP` y funciona en cualquier comando
(§7.1).

---

## 2 · Comandos de `gm-cli`: estado probado

`gm-cli --help` lista 9 comandos. Todos recorridos, y también el `--help` de cada subcomando.

> ⚠️ **`gm-cli <grupo> <sub> --help` sí funciona.** Si te devuelve
> `No command registered for 'manual read'`, el problema es tu shell: **zsh no divide en palabras
> una variable sin comillas**, así que `for c in "manual read"; do gm-cli $c --help; done` pasa
> `manual read` como **un solo argumento**. Es un error de quien llama, no del CLI.

| Comando | Qué hace | Flags reales | Probado en vivo |
|---|---|---|---|
| `init` | Crea proyecto | `--interactive/--no-interactive`, `-n/--name`, `-t/--template`, `--ai/--no-ai`, `--actions/--no-actions`, `--toolchain`, `--cache-dir` | ✅ Sí. Exige **directorio inexistente**: con la carpeta ya creada da `Directory "X" already exists`. `--cache-dir` reubica la caché **local** de herramientas (`gmpm`, `package-tool`, `project-tool`, `prefabs`, `schemas`), no solo la compartida — es la clave del rodeo de §6.1 |
| `run` | Ejecuta | `--target`, `--toolchain`, `--runtime vm\|native`, `--verbose`, `--errors-only`, `--license`, `--cache-dir`, `--config`, `--toolchain-options` | ❌ No ejecutado (fuera del encargo) |
| `compile` | Compila | idem `run` | ✅ Sí, decenas de veces |
| `package` | Empaqueta | idem + `-o/--output` | ✅ Sí (`--target mac` con `packageType=dmg`, §5.10) |
| `manual read` | Manual offline | `--language [en\|ru\|br\|it\|fr\|pl\|es\|ko\|de\|ja\|zh]` | ✅ Sí, **incluido `--language es`**: devuelve el texto traducido al español |
| `manual open` | Abre el manual web | `--language` | ❌ No ejecutado (abriría un navegador) |
| `resourcetool eval` | Un comando y sale | `--cache-dir`, `--config`, `[project]` | ✅ Sí, centenares de veces |
| `resourcetool script` | Lote desde archivo | `--cache-dir`, `--config`, `[project]` | ✅ Sí |
| `resourcetool repl` | Sesión interactiva | `--cache-dir`, `--config`, `[project]` | ✅ Sí, por *stdin* (`printf '...\nEXIT\n' \| gm-cli resourcetool repl`) |
| `resourcetool mcp` | Servidor MCP | — | ❌ No ejecutado (ya inventariado en `12 · 09` §3) |
| `login` | Licencia | `--print/--no-print`, `--cache-dir` | ❌ No ejecutado (licencia ya activa; no se tocan credenciales) |
| `gxgames link\|upload\|meta\|publish` | Publicar en GX.games | `link`: `--studioid`, `--gameid`; `upload`: `--file`, `--version`; `meta`: `--title`, `--age-rating`, `--description`, `--platforms`, `--cover`, `--graphic`; `publish`: ninguno | ⚠️ Solo `--help` (publicar es una operación externa e irreversible). Todos aceptan `[project]` posicional |
| `cache info` | Estado de la caché | `--project`, `--cache-dir`. **Tiene alias: `gm-cli cache` a secas es `cache info`** | ✅ Sí |
| `cache clean` | Limpia la caché | `--project`, `--cache-dir` | ✅ Sí — **y ahí está la trampa de §6.4** |

### 2.1 `--toolchain-options`: el esquema completo

No es un JSON libre: se valida contra
`<proyecto>/.gmcache/schemas/gm-options-schema-2.json`, y **el JSON que se pasa por la línea de
comandos es el sub-objeto del toolchain, no el archivo entero**:

```console
$ gm-cli compile --toolchain-options '{"gms2":{"mac":{"packageType":"dmg"}}}' --errors-only
Command failed:
Invalid --toolchain-options for GMS2:
  - Unrecognized key: "gms2"

$ gm-cli compile --toolchain-options '{"mac":{"packageType":"dmg"}}' --errors-only
        ← sin salida: aceptado

$ gm-cli compile --toolchain-options '{"mac":{"packageType":"iso"}}' --errors-only
Command failed:
Invalid --toolchain-options for GMS2:
  - mac.packageType: Invalid option: expected one of "zip"|"dmg"

$ gm-cli compile --toolchain-options 'noesjson' --errors-only
Command failed:
--toolchain-options is not valid JSON: noesjson
```

El mismo esquema gobierna el `gm-options.json` que `init` deja en la raíz del proyecto — ahí sí
va el archivo completo, con la clave `gms2`/`gmrt` por fuera:

```json
{ "toolchain": "GMS2@2026.0.0.23", "$schema": ".gmcache/schemas/gm-options-schema-2.json" }
```

Árbol de claves aceptadas, extraído del propio esquema:

| Clave | Tipo | Para qué |
|---|---|---|
| `toolchain` | string | `GMS2`, `GMS2@2024.14.4`, `GMRT@0.18` |
| `gms2.operagx.packageType` | `zip` \| `wallpaper` \| `gamestrip` | Formato de salida de GX.games |
| `gms2.operagx.emscriptenSdk` | ruta | SDK de Emscripten para YYC |
| `gms2.windows.packageType` | `zip` \| `nsis` | ZIP o **instalador NSIS** |
| `gms2.windows.visualStudioSdk` | ruta a `VsDevCmd.bat` | YYC en Windows |
| `gms2.mac.packageType` | `zip` \| `dmg` | ZIP o **DMG** |
| `gms2.linux.packageType` | `zip` \| `appimage` | ZIP o **AppImage** |
| `gms2.android.packageType` | `apk` \| `aab` | APK o **Android App Bundle** |
| `gms2.android.sdkPath` / `ndkPath` / `jdkPath` | rutas | Cadena de herramientas Android |
| `gms2.android.keystoreFile` / `keystorePassword` / `keystoreAlias` / `keystoreAliasPassword` | strings | **Firma de Android entera por CLI** |
| `gmrt.buildGraph.{mac,windows,linux}` | ruta `.xml` | Grafo de build de GMRT |
| `gmrt.jobRun` / `jobCompile` / `jobPackage` `.{mac,windows,linux,operagx}.{vm,native}` | string | Sustituir el *job* de GMRT por comando |
| `gmrt.scriptBuildType` | string | Tipo de build del GML compilado |
| `externalTools` | objeto | Metadatos arbitrarios de herramientas externas |

> ⚠️ **Nunca pongas la contraseña del keystore en `gm-options.json` versionado.** Pásala por
> `--toolchain-options` desde un secreto de CI.

### 2.2 `--config`

- `gm-cli compile --config Demo` compila con esa configuración. ✅
- `gm-cli compile --config NoExiste` **no da un error limpio**: revienta con
  `KeyNotFoundException: The given key 'NoExiste' was not present in the dictionary`.
- `gm-cli resourcetool eval --config Demo "<comando>"` funciona con el flag **antes** del comando.
  Es lo que activa los *overrides* por configuración de §5.11.

---

## 3 · Familias de `resourcetool`

`gm-cli resourcetool eval "help"` devuelve 640 líneas y **30 familias**, exactamente las que ya
inventaría `07 · 13`. No apareció ninguna familia nueva. Lo que sí faltaba en la biblioteca:

### 3.1 Los *Global Arguments* — disponibles en **todos** los comandos

```
Global Arguments - Arguments available on all commands
──────────────────────────────────────────────────────
	PREFABSFOLDER = <Path to prefab library packages folder> (Optional)
	PROJECTTOOL   = <Path to ProjectTool> (Optional)
	PACKAGETOOL   = <Path to PackageTool> (Optional)
	GMPM_DLL      = <Path to GMPM DLL> (Optional)
	PROJECTPATH   = <Path to project YYP> (Optional)
	FILEWATCHER   = <How often to tick the FileWatcher in milliseconds> (Optional, default = 10000)
	CONFIG        = <Config to set as active on load> (Optional, default = Default)
```

Los cuatro primeros permiten **sustituir las herramientas que `resourcetool` invoca por dentro** —
es lo que abre el rodeo de §6.1.

### 3.2 Estado probado, familia a familia

| Familia | Subcomandos | Probado | Notas nuevas |
|---|---|---|---|
| `RESOURCE` | `SET INFO CREATE DELETE LIST TYPES` | ✅ todos | `CREATE TYPE=shape` rompe el proyecto (§6.2); `PARENT=` no sirve ni para carpetas ni para objetos |
| `PROJECT` | `CREATE RENAME` | ⚠️ solo `RENAME` (ya documentado) | — |
| `OBJECT EVENT` | `FINDORCREATE DELETE CHANGE LIST TYPES SETGMLFILE` | ✅ todos | `SETGMLFILE` **copia** el contenido del `.gml`; `CHANGE` **deja huérfano** el archivo (§5.4) |
| `ROOM INSTANCE` | `CREATE` | ✅ | Crea la capa con **el nombre que le des** |
| `ROOM ASSET` | `CREATE` | ✅ | **Ignora `LAYER=` si la capa no existe** y la llama `layerN` (§5.3) |
| `ROOM ITEM` | `LIST DELETE` | ✅ | `ALL` es un *flag*, no un valor |
| `ROOM LAYER` | `CREATE DELETE LIST` | ✅ | `DEPTH="INDEX 2"` **necesita comillas**; `PARENT=` se ignora en silencio (§6.5) |
| `ROOM LAYER TILES` | `GET SET LIST RESIZE INFO` | ✅ todos | Flujo completo verificado (§5.5). `TILES INFO` **no imprime nada** |
| `ROOM` | `LIST` | ✅ | — |
| `GML` | `SETGMLFILE` | ✅ | Copia el archivo dentro del proyecto |
| `SPRITE` | `ADDFRAME DELETEFRAME` | ✅ | `ADDFRAME` fija `width`/`height` desde el PNG |
| `SOUND` | `SETFILE` | ✅ | **Sí copia** el `.wav` a `sounds/<nombre>/` |
| `TILESET` | `CREATE DELETE RENAME SETSPRITE` | ✅ | `CREATE` **no calcula** `tile_count` ni `out_columns` (§5.5) |
| `CONFIG` | `LIST USAGES CREATE DELETE RENAME GETACTIVE SETACTIVE` | ✅ todos | `USAGES` no reporta los *overrides* de `OPTIONS` que sí existen (§5.11) |
| `AUDIOGROUP` | `CREATE DELETE RENAME LIST USAGES SET` | ✅ todos | `USAGES` sí muestra la asignación |
| `TEXTUREGROUP` | `CREATE DELETE RENAME LIST USAGES SET` | ✅ todos | — |
| `PREFAB` | `LIST INFO ADDREFERENCE REMOVEREFERENCE CUSTOMISE` | ⚠️ `LIST` e `INFO` | `INFO` sobre una colección no descargada devuelve **una tabla vacía sin error** |
| `SHADER` | `SETFILEPATH` | ✅ | `TYPE=VERTEX\|FRAGMENT` |
| `NOTE` | `SETFILEPATH` | ✅ | — |
| `PATH` | `ADDPOINT INFO DELETEPOINT` | ✅ `ADDPOINT`/`INFO` | `POINTS=(0,0),(100,0),(100,100)` |
| `FONT` | `RANGELIST ADDRANGE REMOVERANGE KERNINGLIST ADDKERNING REMOVEKERNING GLYPHLIST SETFILE` | ✅ | `SETFILE` **no copia** el `.ttf` ni actualiza `fontName` (§5.6) |
| `FOLDER` | `LIST CREATE` | ✅ | `LIST RESOURCES` dibuja el árbol del Asset Browser |
| `OPTIONS` | `LIST GET INFO SET` | ✅ | `SET` **por configuración** con `--config` (§5.11) |
| `CHECK` `STATUS` `VERSION` `HELP` `HELPTABLE` `DEFAULTS` `SCRIPT` `CLI` `MCP` `EXIT` | — | ✅ salvo `CLI`/`MCP` | — |

---

## 4 · El árbol de expresiones, tipo por tipo

Metodología: se creó **un recurso de cada uno de los 17 tipos** de `RESOURCE TYPES`, se listaron
sus campos con `RESOURCE INFO EXPR=<nombre> KEYS`, y **cada propiedad se intentó escribir de
verdad** con `RESOURCE SET`. «Escribe = ✅» significa que devolvió `Saved successfully`, no que se
haya inferido.

### 4.0 Las tres reglas generales que se derivan de la prueba

1. **Todo campo escalar de un recurso es escribible.** No hubo ni una sola excepción entre las ~200
   propiedades escalares probadas.
2. **Ningún campo de tipo lista o diccionario se puede escribir entero.** Siempre da
   ``Invalid cast from 'System.String' to '…ResourceList`1[…]'``. Se escriben **elemento a elemento**
   (`X.lista[0].campo`), y la lista solo **crece** con su comando dedicado
   (`SPRITE ADDFRAME`, `PATH ADDPOINT`, `FONT ADDRANGE`, `ROOM LAYER CREATE`,
   `OBJECT EVENT FINDORCREATE`…).
3. **Dos campos son de solo lectura declarada**: `FullName` en todos los tipos
   (`'X.FullName' can be read but set access is not yet permitted for this member`) y
   `includedfile.fullFilePath` (`Property set method not found`).

> 💡 **Truco para descubrir los valores de un enum sin salir del CLI**:
> `RESOURCE INFO EXPR=<recurso>.<campo> LIST` imprime la tabla nombre→entero.
> ```console
> $ gm-cli resourcetool eval "resource info expr=spr_test.type LIST"
> Type: eGMSpriteType
> spr_test.type = Bitmap
>  name     integer value
>  Bitmap   0
>  SWF      1
>  Spine    2
>  Vector   3
> ```

> 💡 **Indexar por nombre exige comilla SIMPLE.** `RESOURCE INFO EXPR=rm.layers LIST` anuncia
> `eg: rm_test.layers["<name>"]` — con comillas dobles, y **así falla**:
> ```console
> $ gm-cli resourcetool eval "resource info expr=rm_test.layers[\"Background\"]"
> Unrecognized syntax at rm_test.layers
> $ gm-cli resourcetool eval "resource info expr=rm_test.layers['Background']"
> Type: backgroundlayer            ← comilla simple: funciona
> ```

### 4.1 `object` — 26 campos

| Propiedad | Lee | Escribe | Comprobado con |
|---|---|---|---|
| `spriteId` | ✅ | ✅ | `resource set expr=obj_test.spriteId value=spr_test` |
| `spriteMaskId` | ✅ | ✅ | idem — **la máscara de colisión se asigna por CLI** |
| `parentObjectId` | ✅ | ✅ | `value=obj_padre` — **herencia de objetos por CLI** |
| `persistent` | ✅ | ✅ | `value=true` |
| `visible` `solid` `managed` | ✅ | ✅ | `value=false` / `true` |
| `physicsObject` `physicsSensor` `physicsKinematic` `physicsStartAwake` | ✅ | ✅ | booleanos |
| `physicsDensity` `physicsFriction` `physicsRestitution` `physicsLinearDamping` `physicsAngularDamping` | ✅ | ✅ | floats |
| `physicsGroup` `physicsShape` | ✅ | ✅ | enteros |
| `eventList` | ✅ | ❌ entera / ✅ por índice | `obj.eventList[0].eventNum` (receta de `12 · 09` §9 ter) |
| `properties` (Variable Definitions) | ✅ (lista vacía) | ❌ **ver §6.3** | 3 variantes |
| `overriddenProperties` `physicsShapePoints` | ✅ | ❌ enteras | cast inválido |
| `tags` | ✅ | ❌ | `Invalid cast from 'System.String' to List<String>` |
| `name` | ✅ | ✅ | **renombra el recurso y su carpeta** (§5.8) |
| `FullName` | ✅ | ❌ | *set access is not yet permitted* |
| `parent` | ✅ | ❌ en la práctica | §6.6 |

### 4.2 `sprite` — 32 campos

| Propiedad | Lee | Escribe | Comprobado con |
|---|---|---|---|
| `width` `height` | ✅ | ✅ | `value=64` — **pero `SPRITE ADDFRAME` los recalcula desde el PNG** |
| `bbox_left` `bbox_right` `bbox_top` `bbox_bottom` | ✅ | ✅ | enteros |
| `bboxMode` `collisionKind` `collisionTolerance` | ✅ | ✅ | **la máscara de colisión completa se define por CLI** |
| `origin` | ✅ | ✅ | `value=4` (centro) |
| `textureGroupId` | ✅ | ✅ | `value=tg_test` |
| `For3D` `HTile` `VTile` `preMultiplyAlpha` `DynamicTexturePage` `edgeFiltering` | ✅ | ✅ | booleanos |
| `gridX` `gridY` `swfPrecision` | ✅ | ✅ | — |
| `type` | ✅ | ⚠️ ✅ **pero peligroso** | `value=1` (SWF) hace que el compilador busque `frame0.swf` y **falle con exit 1** |
| `frames` | ✅ | ❌ entera / ✅ por índice | `SPRITE ADDFRAME` para crecer |
| `frames[i].subRegionOfResource/MinX/MaxX/MinY/MaxY` | ✅ | ✅ | ver §5.2 |
| `sequence.*` | ✅ | ✅ | `spr.sequence.playbackSpeed`, `playbackSpeedType`, `length`, `volume`, `autoRecord` |
| `layers` | ✅ (tabla propia) | ❌ entera | — |
| `nineSlice` | ✅ (`is null`) | ❌ | §6.7 |
| `swatchColours` `sourceResourceFiles` | ✅ | ❌ | `swatchColours cannot be indexed by an integer` |

### 4.3 `room` — 20 campos, y todo el sub-árbol

**Todo lo siguiente devolvió `Saved successfully`:**

| Expresión | Para qué |
|---|---|
| `rm.roomSettings.Width` / `.Height` | **Tamaño de la sala** |
| `rm.roomSettings.persistent` | Sala persistente |
| `rm.roomSettings.inheritRoomSettings` | Herencia |
| `rm.viewSettings.enableViews` / `.clearViewBackground` / `.clearDisplayBuffer` | Activar viewports |
| `rm.views[0..7].visible` `.xview` `.yview` `.wview` `.hview` `.xport` `.yport` `.wport` `.hport` `.hborder` `.vborder` `.hspeed` `.vspeed` `.objectId` `.inherit` | **Los 8 viewports/cámaras enteros, incluido el objeto que sigue la cámara** |
| `rm.physicsSettings.PhysicsWorld` `.PhysicsWorldGravityX` `.PhysicsWorldGravityY` `.PhysicsWorldPixToMetres` | **Mundo de físicas de la sala** |
| `rm.volume` `rm.parentRoom` `rm.inheritLayers` `rm.inheritCode` `rm.inheritCreationOrder` `rm.creationCodeFile` | — |
| `rm.layers[i]` o `rm.layers['Nombre']` → `.depth` `.visible` `.gridX` `.gridY` `.effectEnabled` `.inherit*` `.userdefinedDepth` `.hierarchyFrozen` | Cualquier capa |
| `rm.layers['Background'].colour` `.htiled` `.vtiled` `.hspeed` `.vspeed` `.stretch` `.animationFPS` `.userdefinedAnimFPS` `.x` `.y` | **Fondo de la sala** |
| `rm.layers['CapaTiles'].tilesetId` | **Asignar el tileset a una capa de tiles** |

Solo lectura o inalcanzable: `layers`, `views`, `instanceCreationOrder` como listas enteras;
`rm.scriptSource` acepta escritura pero con el límite del `=` (§6.8).

⚠️ **`rm.layers['X'].spriteId` (sprite del fondo) falló** con
`Cannot set … Exception has been thrown by the target of an invocation` sobre un sprite **sin
fotogramas**. No se reintentó con un sprite ya poblado, así que el veredicto honesto es
«no lo conseguí con un sprite vacío», no «no se puede».

⚠️ **`effectType` de una capa es escribible y es una bomba.** `value=_filter_tintfilter` se
acepta, y a partir de ahí el proyecto **exige descargar un paquete de prefabs**; con el
`gmpm.dll` roto de fábrica eso hace ilegible el proyecto entero (§6.1).

### 4.4 `instance` (elemento de `rm.layers[i].instances`)

Raíz de expresión propia: el nombre de la instancia (`inst_jugador`).

| Propiedad | Lee | Escribe |
|---|---|---|
| `x` `y` `scaleX` `scaleY` `rotation` `colour` `imageIndex` `imageSpeed` | ✅ | ✅ |
| `frozen` `ignore` `hasCreationCode` `inheritCode` `isDnd` `inheritItemSettings` | ✅ | ✅ |
| `previewSprite` `objectId` | ✅ | ✅ |
| `scriptSource` (código de creación) | ✅ | ⚠️ **solo si no contiene `=` ni `"`** → §6.8 |
| `flexProperties` | ✅ (`null`) | no probado |
| `properties` | ✅ (vacía) | no creable |

### 4.5 Resto de tipos

| Tipo | Campos | Escribibles verificados | Solo lectura / no alcanzable |
|---|---|---|---|
| `animcurve` | 6 | `function` (enum `Linear`/`CentripetalCatmullRom`/`Bezier2D`), `name`, `channels[0].name` (**auto-crea**, §6.9) | `channels` entera, `FullName` |
| `audiogroup` | 6 | `exportDir`, `targets`, `name` | `FullName` |
| `font` | 33 | `size` `bold` `italic` `fontName` `styleName` `includeTTF` `usesSDF` `sdfSpread` `AntiAlias` `textureGroupId` `first` `last` `lineHeight` `ascender` `ascenderOffset` `charset` `hinting` `interpreter` `applyKerning` `sampleText` `regenerateBitmap` `canGenerateBitmap` `glyphOperations` `maintainGms1Font` `pointRounding` `TTFName` | `glyphs` `ranges` `kerningPairs` (listas), `FullName` |
| `includedfile` | 7 | `filePath` `CopyToMask` `name` | `fullFilePath` (*Property set method not found*), `FullName` |
| `notes` | 6 | `shouldOpenOnLoad` `openedOnFirstLoad` `name` | `FullName` |
| `particlesystem` | 16 | `drawOrder` `xorigin` `yorigin` `showBackdrop` `showBackdropImage` `backdropWidth/Height` `backdropImagePath` `backdropImageOpacity` `backdropXOffset/YOffset`, `emitters[0].*` | `emitters` entera; `emitters[1]` no existe (ya documentado) |
| `path` | 8 | `closed` `precision` `kind`, `points[i].x/y/speed` | `points` entera |
| `script` | 8 | `isCompatibility` `isDnD` `scriptLanguageType` `name` | `FullName`; `scriptSource` con el límite del `=` |
| `shader` | 5 | `type` (enum), `name` | `FullName` |
| `shape` | — | **NO SE PUEDE NI CREAR — rompe el proyecto (§6.2)** | — |
| `sound` | 16 | `volume` `preload` `compression` `compressionQuality` `conversionMode` `bitDepth` `channelFormat` `sampleRate` `audioGroupId` `duration` `soundFile` `exportDir` | `FullName` |
| `texturegroup` | 14 | `autocrop` `border` `isScaled` `mipsToGenerate` `loadType` `compressFormat` `directory` `groupParent` `targets` `customOptions` | `FullName` |
| `tileset` | 21 | `tileWidth` `tileHeight` `tile_count` `out_columns` `out_tilehborder` `out_tilevborder` `tilehsep` `tilevsep` `tilexoff` `tileyoff` `tileAnimationSpeed` `spriteId` `spriteNoExport` `textureGroupId` | `autoTileSets` `macroPageTiles` `tileAnimationFrames` (listas), `FullName` |
| `timeline` | 5 | `name` | `momentList` — **no auto-crea**, §6.9 |

---

## 5 · Las tareas que un agente necesita para entregar un juego

Cada una con veredicto y el comando exacto que la resuelve.

### 5.1 Asignar un sprite a un objeto · marcarlo persistente · definir herencia — ✅

```bash
gm-cli resourcetool eval "resource set expr=obj_jugador.spriteId value=spr_jugador"
gm-cli resourcetool eval "resource set expr=obj_jugador.persistent value=true"
gm-cli resourcetool eval "resource set expr=obj_slime.parentObjectId value=obj_enemigo"
```

Máscara de colisión, completa:

```bash
gm-cli resourcetool eval "resource set expr=obj_jugador.spriteMaskId value=spr_mascara"
gm-cli resourcetool eval "resource set expr=spr_jugador.bboxMode value=1"          # Manual
gm-cli resourcetool eval "resource set expr=spr_jugador.collisionKind value=1"     # Rectangle…
gm-cli resourcetool eval "resource set expr=spr_jugador.bbox_left value=2"
```

### 5.2 Importar una imagen a un sprite y sus fotogramas — ✅

```console
$ gm-cli resourcetool script lote.txt
$> RESOURCE CREATE TYPE=sprite NAME=spr_anim
$> SPRITE ADDFRAME NAME=spr_anim PATH=/tmp/gm_img/f0.png
Saved successfully
$> SPRITE ADDFRAME NAME=spr_anim PATH=/tmp/gm_img/f1.png
$> SPRITE ADDFRAME NAME=spr_anim PATH=/tmp/gm_img/f2.png
$> RESOURCE INFO EXPR=spr_anim.width
spr_anim.width = 32
$> RESOURCE INFO EXPR=spr_anim.frames LIST
List has 3 items of type spriteframe
```

**Velocidad de la animación** — nunca documentado:

```bash
gm-cli resourcetool eval "resource set expr=spr_anim.sequence.playbackSpeed value=12"
gm-cli resourcetool eval "resource set expr=spr_anim.sequence.playbackSpeedType value=1"
```

**Sobre trocear una tira (`_stripN`)**: `12 · 09` §9 quater.3 concluye —y se confirma— que
`ADDFRAME` no trocea. Lo **nuevo** es que cada fotograma expone
`subRegionOfResource` + `subRegionMinX/MaxX/MinY/MaxY`, y **los cinco aceptan escritura y
persisten en el `.yy`**:

```bash
gm-cli resourcetool eval "resource set expr=spr_strip.frames[0].subRegionOfResource value=true"
gm-cli resourcetool eval "resource set expr=spr_strip.frames[0].subRegionMaxX value=32"
```

⚠️ **Honestidad**: se verificó que los campos se escriben y quedan en el `.yy`; **no** se pudo
verificar visualmente que el empaquetador recorte de verdad (no se ejecutan juegos en esta
auditoría). Hasta que alguien lo mire en pantalla, **usa el rodeo ya documentado** (trocear con
`magick` y añadir cada trozo).

### 5.3 Crear y poblar una sala — ✅ con dos avisos

```bash
# tamaño y persistencia
gm-cli resourcetool eval "resource set expr=rm_nivel1.roomSettings.Width value=640"
gm-cli resourcetool eval "resource set expr=rm_nivel1.roomSettings.Height value=360"

# capas (el tipo va en MAYÚSCULAS; DEPTH necesita comillas si es INDEX n)
gm-cli resourcetool eval "room layer create room=rm_nivel1 name=Suelo type=TILE"
gm-cli resourcetool eval 'room layer create room=rm_nivel1 name=Frente type=INSTANCE depth="INDEX 2"'

# instancias
gm-cli resourcetool eval "room instance create room=rm_nivel1 object=obj_jugador name=inst_p1 layer=Instances x=100 y=200"
gm-cli resourcetool eval "resource set expr=inst_p1.scaleX value=2"
gm-cli resourcetool eval "resource set expr=inst_p1.rotation value=45"

# fondo
gm-cli resourcetool eval "resource set expr=rm_nivel1.layers['Background'].colour value=4283782485"
```

> ⚠️ **`ROOM ASSET CREATE` ignora `LAYER=` cuando la capa no existe.** Verificado con **tres
> variantes**: con `layer=CapaDeco` inexistente creó `layer3`; con `layer=OtraCapa` inexistente
> creó `layer6`; con la capa `CapaDeco2` **creada antes** con `ROOM LAYER CREATE … TYPE=ASSET`,
> colocó el asset donde tocaba. `ROOM INSTANCE CREATE`, en cambio, **sí** respeta el nombre.
> **Crea siempre la capa ASSET antes.**

### 5.4 Eventos y su GML — ✅ con una trampa nueva

```bash
gm-cli resourcetool eval "object event findorcreate name=obj_jugador type=create"
gm-cli resourcetool eval "object event setgmlfile name=obj_jugador type=create path=/ruta/create.gml"
```

`SETGMLFILE` **copia el contenido** del archivo dentro del evento. Verificado leyendo
`objects/obj_test/Create_0.gml` después.

> 🔴 **Trampa nueva — `OBJECT EVENT CHANGE` deja el `.gml` huérfano.** Es la misma familia que las
> Trampas 3 y 9 de `12 · 09`, pero con otro comando:
> ```console
> $ ... OBJECT EVENT CHANGE NAME=obj_test TYPE=step SUBTYPE=step_normal NEWTYPE=step NEWSUBTYPE=step_end
> Saved successfully
> $ ... OBJECT EVENT LIST NAME=obj_test
> │ step   │ Event_StepEnd │        ← el .yy ya dice eventNum:2, eventType:3
> $ ls objects/obj_test/
> Create_0.gml  obj_test.yy  Step_0.gml     ← el archivo SIGUE llamándose Step_0
> ```
> `gm-cli compile` termina limpio y **no avisa**. El código deja de ejecutarse en silencio.
> Renombra tú el archivo a `Step_2.gml` después de cualquier `OBJECT EVENT CHANGE`.

### 5.5 Tileset desde un sprite y pintar el tilemap — ✅

```console
$> SPRITE ADDFRAME NAME=spr_tiles PATH=/tmp/gm_img/tiles.png
$> TILESET CREATE NAME=ts_mundo SPRITE=spr_tiles TILEWIDTH=32 TILEHEIGHT=32
Created resource named 'ts_mundo' of type 'GMTileSet'
$> RESOURCE INFO EXPR=ts_mundo.tile_count
ts_mundo.tile_count = 0        ← ¡OJO! TILESET CREATE no calcula la rejilla
```

⚠️ **`TILESET CREATE` deja `tile_count` y `out_columns` a 0** aunque le des sprite, ancho y alto.
Hay que fijarlos a mano (los dos son escribibles).

Asignar el tileset a la capa y pintar:

```console
$ gm-cli resourcetool eval "resource set expr=rm_test.layers['CapaSuelo'].tilesetId value=ts_mundo"
OK
$> ROOM LAYER TILES RESIZE ROOM=rm_test LAYER=CapaSuelo WIDTH=10 HEIGHT=6
$> ROOM LAYER TILES SET ROOM=rm_test LAYER=CapaSuelo LEFT=0 TOP=0 WIDTH=3 HEIGHT=2 DATA=1,2,3,4,5,6
$> ROOM LAYER TILES SET ROOM=rm_test LAYER=CapaSuelo FILE=/tmp/mapa.csv LEFT=5 TOP=3
$> ROOM LAYER TILES GET ROOM=rm_test LAYER=CapaSuelo
# Bit fields: [ 31..19:Zeroes | 18..0:Tile index ]
1,2,3,0,0,0,0,0,0,0
4,5,6,0,0,0,0,0,0,0
0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,1,1,1,0,0
0,0,0,0,0,2,2,2,0,0
0,0,0,0,0,0,0,0,0,0
```

**`FILE=` acepta un CSV**: es la vía natural para importar un mapa de Tiled o generado por script.
`ROOM LAYER TILES INFO` **no imprime nada** (debería mostrar el desglose de bits; el desglose sí
aparece como cabecera de `TILES GET`).

### 5.6 Fuente desde una fuente del sistema — ⚠️ con la Trampa 5 intacta

```console
$ gm-cli resourcetool eval 'font setfile name=fnt_sys path="/System/Library/Fonts/Supplemental/Andale Mono.ttf"'
fnt_sys has been marked for re-generation.
Saved successfully
$> FONT ADDRANGE NAME=fnt_sys LOWER=32 UPPER=255
$> FONT GLYPHLIST NAME=fnt_sys
fnt_sys.glyphs dictionary:
There are no table rows to show          ← sigue vacío
$> RESOURCE INFO EXPR=fnt_sys.fontName
fnt_sys.fontName = Arial                 ← SETFILE NO actualiza fontName
$ ls fonts/fnt_sys/
fnt_sys.yy                               ← el .ttf NO se copió al proyecto
```

Tres datos nuevos que la Trampa 5 no dice: **`FONT SETFILE` no copia el `.ttf`**, **no actualiza
`fontName`**, y **compilar no rasteriza** (se comprobó volviendo a pedir `FONT GLYPHLIST` después
de un `gm-cli compile` con exit 0). `includeTTF` se puede poner a `true`, pero eso no genera
glifos. La solución sigue siendo la de la Trampa 5 (hornear con Pillow) o la de la Trampa 12
(`font_add()` con el `.ttf` como *Included File*).

> 💡 **Rutas con espacios**: `path="…/Andale Mono.ttf"` con **comilla doble** funciona en `eval` y
> en modo `script`. Con comilla simple falla. Sin comillas, el parser corta en el espacio:
> `Cannot find Source .TTF file file at path '/System/Library/Fonts/Supplemental/Andale'`.

### 5.7 Included file, audio, grupos de textura y de audio — ✅

```bash
# Included file: la receta de la Trampa 8, reconfirmada
mkdir -p datafiles && cp datos.json datafiles/datos.json
gm-cli resourcetool eval "resource create type=includedfile name=datos.json"
gm-cli resourcetool eval "resource set expr=project.IncludedFiles[0].filePath value=datafiles"
# compilación final: exit 0 y ningún "WARNING :: datafile ... was NOT copied"

# Sonido: SOUND SETFILE sí copia el archivo dentro del proyecto
gm-cli resourcetool eval "sound setfile name=snd_salto path=/ruta/beep.wav"
gm-cli resourcetool eval "audiogroup create name=ag_musica"
gm-cli resourcetool eval "audiogroup set group=ag_musica resources=snd_salto"

# Grupos de textura
gm-cli resourcetool eval "texturegroup create name=tg_ui"
gm-cli resourcetool eval "texturegroup set group=tg_ui resources=spr_boton,spr_marco"
gm-cli resourcetool eval "resource set expr=tg_ui.border value=4"
```

> 🔴 **Un `sound` sin archivo tumba la compilación** — y a diferencia del sprite vacío, **con
> exit 1**: `FileNotFoundException: Could not find file '…/Audio/snd_test.wav'`. Crea el recurso y
> asígnale el `.wav` en el mismo lote, nunca lo dejes vacío.

### 5.8 Renombrar recursos — ✅ y actualiza referencias

```console
$ gm-cli resourcetool eval "resource set expr=spr_anim.name value=spr_animacion"
spr_anim.name: spr_animacion
Saved successfully
$ grep -o '"spriteId":{[^}]*}' objects/obj_test/obj_test.yy
"spriteId":{"name":"spr_animacion","path":"sprites/spr_animacion/spr_animacion.yy",}
$ grep -o '"spriteId":{[^}]*}' rooms/rm_test/rm_test.yy | head -1
"spriteId":{"name":"spr_animacion","path":"sprites/spr_animacion/spr_animacion.yy",}
$ gm-cli compile --toolchain GMS2@2026.0.0.23 ; echo $?
◆  Compilation finished
0
```

La carpeta en disco también se renombra. **Es limpio** — al contrario que
`resource set expr=project.name`, que deja dos `.yyp` (aviso ya documentado).

### 5.9 Ordenar recursos en carpetas — ⚠️ solo al crearlos

```bash
gm-cli resourcetool eval "folder create folder=Enemigos/Robots"
gm-cli resourcetool eval "resource create type=object name=obj_slime folder=Enemigos/Robots"
gm-cli resourcetool eval "folder list resources"
```

```
audit12
 ├─ [Enemigos]
 │   └─ [Robots]
 │       └─ obj_en_carpeta
 ├─ [Personajes]
```

**Mover uno ya existente no se consigue** — ocho variantes en §6.6.

### 5.10 Empaquetar en formatos nativos — ✅ (llega hasta la firma)

```console
$ gm-cli package --target mac --toolchain GMS2@2026.0.0.23 \
    --toolchain-options '{"mac":{"packageType":"dmg"}}' -o /tmp/audit_mac.dmg
│  Debug Igor: Package as dmg and SSH back to windows.
│  Error : Could not find matching certificate for Developer ID Application:, please check your
│          'Signing Identifier' in your macOS Options
■  Failed
```

**La ruta del DMG es real y se ejecuta**: Igor entra en el camino de empaquetado de DMG y se
detiene solo porque esta máquina no tiene certificado *Developer ID*. Lo mismo aplica a
`{"windows":{"packageType":"nsis"}}`, `{"linux":{"packageType":"appimage"}}` y
`{"android":{"packageType":"aab"}}` — validados por el esquema, no ejecutados hasta el final por
falta de la plataforma o del certificado.

### 5.11 Configuraciones de build y *overrides* por configuración — ✅ (hallazgo nuevo)

```console
$ gm-cli resourcetool eval "config create name=Demo parent=Default"
Config 'Demo' created successfully based on parent 'Default'.
$ gm-cli resourcetool eval --config Demo "options set platform=windows property=display_name value=JuegoDemo"
Set windows.display_name = JuegoDemo
$ gm-cli resourcetool eval --config Demo    "options get platform=windows property=display_name"
display_name = JuegoDemo
$ gm-cli resourcetool eval --config Default "options get platform=windows property=display_name"
display_name = Pixel Game
```

**Las dos conviven.** La Trampa 10 dice —y es cierto— que solo cinco propiedades por plataforma
son escribibles (`interpolate_pixels`, `start_fullscreen`, `display_name`, `icon`,
`splash_screen`); lo que faltaba saber es que **esas cinco se pueden fijar por configuración**, que
es exactamente como se prepara una build de demo o de prensa con otro nombre e icono.

⚠️ `CONFIG USAGES` **no reporta** estos *overrides* (sigue diciendo
`There are no table rows to show`), así que no lo uses como verificación: lee el valor con
`OPTIONS GET --config <nombre>`.

⚠️ Un `RESOURCE SET` bajo `--config Demo` **no** crea un *override*: escribe el valor base. Probado
leyendo el mismo campo bajo `Default` y bajo `Demo` — idéntico en los dos.

---

## 6 · Los límites reales — cada uno con sus variantes

### 6.1 Las 9 plantillas que fallan: causa raíz y **dos rodeos que funcionan**

**Lo que dice hoy la biblioteca** (`12 · 09` Trampa 1, `07 · 13` §12): 9 de 18 plantillas fallan
con `PREFABS RESTORE exited with code 1` y *«No hay ninguna solución por CLI … créala desde el
IDE»*.

**La causa raíz, aislada en esta sesión.** El fallo no está en las plantillas. Compilando con
`--verbose` un proyecto que necesitaba un paquete de prefabs apareció la traza entera:

```
│  EXEC PACKAGE TOOL: find package="io.gamemaker.gm_filter_tintfilter" registry="http://gmpm.gamemaker.io" …
│  PackageTool@2024.14.29
│  gmpm: Initialised GMPM with NPM Backend
│  PackageTool failed because of an internal program error:
│  Parameter count mismatch.
│     at System.Reflection.MethodBaseInvoker.ThrowTargetParameterCountException()
│     at PackageTool.GmpmBindings.GetAvailablePackages(String registryUrl, String registryPackagesUrlPath, String username, String password)
│     at PackageTool.Commands.FindCommand.Execute()
│  Still Missing Prefabs
│  io.gamemaker.gm_filter_tintfilter
```

Reproducido **fuera de `gm-cli`**, invocando el binario directamente:

```console
$ .gmcache/package-tool/.../PackageTool find package="io.gamemaker.gm_filter_tintfilter" \
    registry="https://gmpm.gamemaker.io" gmpm_dll=".gmcache/gmpm/.../gmpm.dll"
PackageTool failed because of an internal program error:
Parameter count mismatch.
   at PackageTool.GmpmBindings.GetAvailablePackages(...)
```

**`PackageTool@2024.14.29` no puede consultar el registro de paquetes en absoluto.** Es un desfase
de firma entre PackageTool (versión **2024**.14.29, la única publicada: `npm view
@gm-tools/package-tool-osx-arm64 versions` → `2024.14.29`) y el `gmpm.dll` que `gm-cli` descarga,
que es más nuevo (79 872 bytes frente a los 64 512 del que trae el IDE). No es un problema de las
plantillas: **cualquier cosa que necesite resolver un paquete del registro falla igual**, incluidas
las 9 plantillas, los comandos `PREFAB` y —hallazgo colateral— poner un filtro de capa
(`effectType`) en una sala.

#### Rodeo A — sustituir el `gmpm.dll` (necesita el IDE instalado). **Verificado de punta a punta.**

```bash
CACHE=~/.gmcli-cache
IDEDLL="$HOME/Library/Application Support/Steam/steamapps/common/GameMaker Studio 2/GameMaker.app/Contents/MacOS/arm64/gmpm/gmpm.dll"

# 1. Una vez: deja que gm-cli descargue sus herramientas a una caché tuya. Este init FALLA.
gm-cli init --no-interactive -n Tmp -t "Platformer" --cache-dir "$CACHE"

# 2. Sustituye el gmpm.dll roto por el que trae el IDE instalado
cp "$IDEDLL" "$(find "$CACHE" -name gmpm.dll | head -1)"

# 3. A partir de aquí, cualquiera de las 9 plantillas funciona
gm-cli init --no-interactive -n MiJuego -t "Platformer" --cache-dir "$CACHE"
```

Salida real del paso 3:

```console
Creating project...
$ ls P4/*.yyp
P4/P4.yyp
```

Y el proyecto **compila**:

```console
$ gm-cli compile --toolchain GMS2@2026.0.0.23 ; echo $?
│  Compile Timelines...finished.
│  Compile UI Layers...finished.
│  Final Compile finished.
◆  Compilation finished
0
```

> El paso 1 es obligatorio porque `gm-cli init` **exige que el directorio destino no exista**
> (`Directory "X" already exists`), así que no se puede pre-sembrar el `.gmcache` local; lo que sí
> se puede es reubicarlo con `--cache-dir` y parchearlo allí una sola vez para todos los proyectos.

#### Rodeo B — llevarse la caché de prefabs ya resuelta (**sin IDE**, pensado para CI)

Una vez que un proyecto resolvió sus prefabs, la carpeta `.gmcache/prefabs` los contiene:

```console
$ ls plat3/MiPlat3/.gmcache/prefabs
io.gamemaker.gm_effect_windblown_particles-1.0.0
io.gamemaker.gm_filter_pixelate-1.0.0
io.gamemaker.gm_filter_tintfilter-1.0.0
io.gamemaker.gm_filter_underwater-1.0.0
io.gamemaker.sdfshaders-1.0.0
```

Copiándola a otro clon del mismo proyecto **con el `gmpm.dll` roto**, el proyecto carga:

```console
$ cp -R plat3/MiPlat3/.gmcache/prefabs plat6/.gmcache/prefabs
$ cd plat6 && gm-cli resourcetool eval "status"
Project 'Windy Woods - GML Code' loaded from '…/plat6/Windy Woods - GML Code.yyp'
```

Los workflows que genera `gm-cli init` ya cachean `.gmcache` con `actions/cache@v5`, así que en CI
basta con que la caché se haya poblado una vez desde una máquina con el `dll` bueno.

#### Vía adicional: bajarse cualquier plantilla sin `init`

La API de plantillas expone la URL de descarga de cada una, y el `.yymps` es **un ZIP normal con
el `.yyp` dentro**:

```bash
curl -s https://api.gamemaker.io/api/gamemaker/project-templates \
  | python3 -c "import json,sys;[print(t['attributes']['info_title'],'|',t['attributes']['gml_code_download_url']) for t in json.load(sys.stdin)['data']]"
# Platformer Template | https://api.yoyogames.com/api/2/download?package_id=com.yoyogames.windywoods&version=1.2.2
curl -sL "https://api.yoyogames.com/api/2/download?package_id=com.yoyogames.windywoods&version=1.2.2" -o plataformer.yymps
unzip -q plataformer.yymps -d MiPlat   # → MiPlat/Windy Woods - GML Code.yyp
```

Sigue haciendo falta uno de los dos rodeos para que los prefabs se resuelvan, pero esto da acceso
a **las 31 plantillas** sin depender de `gm-cli init`.

**Lo que NO funcionó** (documentado para que nadie repita el camino): apuntar `prefabsfolder=` a la
carpeta `packages/` del IDE, a su subcarpeta `gm-ide-prefabs`, o a la carpeta de un prefab
concreto (3 variantes, las tres `PREFABS RESTORE exited with code 1`); copiar el `.yymps` a mano a
`.gmcache/prefabs` y a `<proyecto>/prefabs` (4.ª variante, igual); y apuntar `projecttool=` al
`ProjectTool` que trae el IDE, solo y combinado con `prefabsfolder=` (variantes 5 y 6, igual).

### 6.2 🔴 `RESOURCE CREATE TYPE=shape` deja el proyecto irrecuperable

`shape` es **uno de los 17 tipos que anuncia `RESOURCE TYPES`**. Crear uno falla siempre:

```console
$> RESOURCE CREATE TYPE=shape NAME=shp_test
Created resource named 'shp_test' of type 'GMShape'
System.UnauthorizedAccessException: Access to the path '/Users/…/audit12' is denied.
 ---> System.IO.IOException: Permission denied
   at System.IO.File.WriteAllBytes(String path, Byte[] bytes)
    IExecutableCommand: Write binary file /Users/…/audit12
Project save failed: One or more errors occurred.
ResourceTool Failed
```

Intenta **escribir un archivo binario sobre la ruta del directorio del proyecto** (sin nombre de
archivo). Pero antes de fallar **ya ha registrado el recurso**:

```console
$ grep -n shp_test audit12.yyp
30:    {"id":{"name":"shp_test","path":"audit12.yyp",},},
$ cat audit12.resource_order
    {"name":"shp_test","order":10,"path":"",},
```

A partir de ahí, **todo** falla — `resourcetool`, `compile`, cualquier comando:

```console
$ gm-cli resourcetool eval "status"
Command failed:
Failed to restore project. "ProjectTool PREFABS RESTORE" exited with code 1
```

**Reproducido tres veces sobre un proyecto recién creado** (`gm-cli init -t "Blank Pixel Game"`):
el primer intento da la excepción, el segundo y el tercero ya dan el error genérico de carga.
Es determinista, no la Trampa 11.

**No hay comando para deshacerlo.** Tres variantes probadas, las tres con el mismo error:

```console
$ gm-cli resourcetool eval "resource delete name=shp_test type=shape"     → PREFABS RESTORE exited with code 1
$ gm-cli resourcetool eval "resource delete name=shp_test"                → PREFABS RESTORE exited with code 1
$ gm-cli resourcetool eval "resource delete name=shp_test" "$(pwd)/audit12.yyp"  → idem
```

**El diagnóstico real lo da `gm-cli compile`, no `resourcetool`** — y esto vale para cualquier
proyecto que no cargue:

```console
$ gm-cli compile --toolchain GMS2@2026.0.0.23
│  Core Resources : Info - Cannot load project because linking failed with the following errors:
│  /Users/…/ImpTest.yyp(31,49): Cannot resolve link 'ImpTest.yyp : shp_1' in user's project.
```

> 🔑 **`PREFABS RESTORE exited with code 1` es un mensaje genérico de «no pude cargar el
> proyecto»**, no necesariamente algo de prefabs. Cuando lo veas, compila (sin `--errors-only`)
> para saber la causa de verdad: te da archivo, línea y el enlace que no resuelve.

**Reparación** (la única, y es exactamente lo que `AGENTS.md` prohíbe salvo emergencia):

```bash
sed -i '' '/"name":"shp_test"/d' MiJuego.yyp MiJuego.resource_order
# y normaliza el JSON con la herramienta oficial, para no dejar el formato a medias:
.gmcache/project-tool/.../ProjectTool json format input=MiJuego.yyp commas=GAMEMAKER
```

```console
$ gm-cli resourcetool eval "status"
Project 'ImpTest' loaded from '…/ImpTest.yyp'
```

**Regla práctica: no crees nunca un recurso de tipo `shape` por CLI.** Que aparezca en
`RESOURCE TYPES` no significa que sea creable.

### 6.3 Las Variable Definitions de un objeto no se pueden crear — 3 variantes

```console
$ gm-cli resourcetool eval "resource set expr=obj_test.properties[0].name value=velocidad"
obj_test.properties[0].name: obj_test.properties[0] is out of range (list is empty)

$ gm-cli resourcetool eval "resource create type=objectproperty name=velocidad parent=obj_test"
ResourceTool Failed

$ gm-cli resourcetool eval "resource set expr=obj_test.properties value=velocidad"
ResourceTool Failed
```

**Rodeo**: usa un evento *Create* con `OBJECT EVENT SETGMLFILE` (§5.4). Las Variable Definitions
son azúcar del editor sobre lo mismo.

### 6.4 🔴 `cache clean --project` borra **también** la caché compartida

```console
$ gm-cli cache clean --cache-dir /tmp/gmcachetest
Shared cache
Skipped                       ← con --cache-dir sí respeta la compartida

Local cache
/tmp/gmcachetest
Cleaned

$ gm-cli cache clean --project "$HOME/…/plat6/Windy Woods - GML Code.yyp"
Shared cache
/Users/…/Library/Caches/GameMakerCLI
Cleaned                       ← ¡los runtimes descargados, borrados!

Local cache
/Users/…/plat6/.gmcache
Cleaned
```

El nombre del flag (`--project`) sugiere que la operación está acotada al proyecto. **No lo está.**
Se comprobó después: `~/Library/Caches/GameMakerCLI` había desaparecido, y el siguiente
`gm-cli compile` tuvo que volver a descargar `runtimes-gms2` entero. **Si solo quieres limpiar un
proyecto, usa `--cache-dir` apuntando a su caché local, no `--project`.**

### 6.5 Las capas de sala no se anidan — 4 variantes

`ROOM LAYER CREATE` acepta `PARENT=`, responde `Saved successfully`, y **la capa queda en la
raíz**: en `ROOM LAYER LIST` su *Layer tree path* es su propio nombre, no `Padre/Hija`.

```console
$ ... room layer create room=rm_test name=Hija  type=INSTANCE parent=Padre depth="INDEX 2"  → Saved successfully
$ ... room layer create room=rm_test name=Hija4 parent=Padre                                → Saved successfully
$ ... room layer create room=rm_test name=Hija5 type=INSTANCE parent="Padre"                → Saved successfully
$ ... room layer list room=rm_test
│ Hija5      │ Hija5           │ INSTANCE   │
│ Hija4      │ Hija4           │ INSTANCE   │
│ Hija       │ Hija            │ INSTANCE   │
│ Padre      │ Padre           │ INSTANCE   │
```

Cuarta variante, por el árbol de expresiones:

```console
$ ... resource set expr="rm_test.layers['Padre'].layers[0].name" value=SubCapa
rm_test.layers['Padre'].layers[0] is out of range (list is empty)
```

### 6.6 Mover un recurso ya existente a una carpeta — 8 variantes, ninguna funciona

```console
$ ... resource set expr=obj_test.parent value=Personajes                  → 'Personajes' is not a valid resource name
$ ... resource set expr=obj_test.parent value=folders/Personajes.yy       → ídem
$ ... resource set expr=obj_padre.parent value=Enemigos/Robots            → ídem
$ ... resource set expr=obj_test.parent value=Robots                      → 'Robots' is not a valid resource name
$ ... resource set expr=obj_test.parent value=folders/Enemigos/Robots.yy  → 'folders/…' is not a valid resource name
$ ... resource set expr=obj_test.parent value=Enemigos/Robots             → ídem
$ ... resource create type=object name=obj_test folder=Personajes         → Failed to add resource 'obj_test' … (ya existe)
$ ... resource create type=object name=obj_p1  parent=Personajes          → Cannot find parent resource named 'Personajes'
```

Y sin embargo `obj_en_carpeta.parent` **lee** la carpeta perfectamente
(`folderPath = folders/Enemigos/Robots.yy`): la lectura funciona, la escritura no acepta ninguna
forma de nombrar una carpeta.

**Rodeo**: crea el recurso ya en su sitio (`RESOURCE CREATE … FOLDER=Enemigos/Robots`). Para uno
que ya existe, la única vía es sacarlo y volver a meterlo con `ProjectTool IMPORT YY` (§7.2).

### 6.7 No hay forma de crear el `nineSlice` de un sprite

```console
$ ... resource info expr=spr_test.nineSlice
Type: NineSliceData
spr_test.nineSlice is null
$ ... resource set expr=spr_test.nineSlice value=algo
Cannot set 'spr_test.nineSlice': Invalid cast from 'System.String' to 'YoYoStudio.Resources.GMNineSliceData'.
$ ... resource set expr=spr_test.nineSlice.left value=4
spr_test.nineSlice.left: spr_test.nineSlice cannot have member access
```

Tres variantes. El auto-relleno de índice `[0]` (§6.9) no aplica porque no es una lista.

### 6.8 🔴 Un `=` dentro de un valor rompe `RESOURCE SET` — 9 variantes

Consecuencia práctica: **el código de creación de una instancia no se puede escribir por CLI**,
porque cualquier asignación GML lleva `=`.

```console
# eval, comilla doble
$ ... 'resource set expr=inst_jugador.scriptSource value="velocidad = 8;"'   → vuelca la ayuda de VALUE, Command failed
# eval, sin espacios
$ ... "resource set expr=inst_jugador.scriptSource value=velocidad=8;"       → ídem
# eval, escapando el igual
$ ... 'resource set expr=…  value="velocidad \= 8;"'                          → ídem
# eval, comilla simple: NO falla, pero corta en el primer espacio
$ ... "resource set expr=… value='velocidad = 8;'"
inst_jugador.scriptSource: 'velocidad                                          ← truncado
# script (archivo de lote), comilla doble
$ printf 'RESOURCE SET EXPR=… VALUE="velocidad = 8;"\n' > cc.txt ; gm-cli resourcetool script cc.txt
	VALUE = <Value to set>
ResourceTool Failed
# script, comilla simple                                                       → truncado igual
# repl por stdin, comilla doble                                                → Command Failed
# valor SIN '=' → funciona, luego el problema es el signo igual, no la longitud ni el espacio:
$ ... 'resource set expr=inst_jugador.scriptSource value="show_debug_message(hola)"'
inst_jugador.scriptSource: show_debug_message(hola)
Saved successfully
# las comillas dobles internas tampoco sobreviven: value="…\"velocidad\"…" guarda \velocidad\
```

**No hay rodeo por archivo**: en LTS 2026 el código de creación de una instancia vive **inline** en
el `.yy` de la sala (campo `scriptSource`), no en un `InstanceCreationCode_*.gml`. Se escribió ese
archivo a mano y el compilador lo ignoró (`0 CC empty` en el log de `compile`).

**Rodeo real**: pon la lógica en el evento *Create* del objeto (`OBJECT EVENT SETGMLFILE`, §5.4) y
diferencia las instancias por su posición, por su capa o por un objeto hijo distinto. Es lo que un
proyecto mantenible debería hacer de todas formas.

Y el mismo límite afecta a **cualquier** propiedad de texto que necesite un `=`.

### 6.9 El auto-relleno de `[0]` **no es exclusivo de los emitters** — corrección a `12 · 09`

`12 · 09` §9 quater.1 dice que indexar `[0]` sobre una lista vacía crea el primer elemento y que
«el comportamiento es específico del campo `emitters` de un `particlesystem`, no una regla general».
**También pasa con `animcurve.channels`:**

```console
$ ... resource info expr=ac_test.channels LIST
List has 0 items of type animcurvechannel
$ ... resource set expr="ac_test.channels[0].name" value=canal1
Saved successfully
$ ... resource info expr=ac_test.channels LIST
List has 1 items of type animcurvechannel
```

Y **tampoco crece más allá de `[0]`**, igual que los emitters:

```console
$ ... resource set expr="ac_test.channels[1].name" value=canal2
ac_test.channels[1] is out of range (0..0)
$ ... resource set expr="ps_test.emitters[1].name" value=emisor2
ps_test.emitters[1] is out of range (0..0)
```

Donde **no** ocurre (3 comprobaciones): `timeline.momentList`, `object.properties`,
`layer.layers`. La regla honesta es: *algunos* campos de «recurso hijo» auto-crean el índice 0;
compruébalo con `RESOURCE INFO … LIST` después, nunca lo des por hecho.

---

## 7 · Correcciones a lo que la biblioteca dice hoy

| Dónde | Lo que dice | Lo que se comprobó |
|---|---|---|
| `12 · 09` Trampa 1 · `07 · 13` §12 | «No hay ninguna solución por CLI para las 9 que fallan: no es un flag que falte, ni una versión que instalar» | **Falso.** La causa es `PackageTool@2024.14.29` contra un `gmpm.dll` más nuevo, y hay **dos rodeos verificados** (§6.1). `gm-cli init -t "Platformer"` crea el proyecto y **compila con exit 0** |
| `12 · 09` §9 bis, «Nota sobre apuntar a un `.yyp` explícito» | `projectpath=<ruta>` dentro del comando «sí funciona para el subcomando `CHECK` … pero no para `RESOURCE INFO`/`RESOURCE SET` en general» | **Falso.** `PROJECTPATH` está en *Global Arguments* de `HELP` — disponible en **todos** los comandos. Verificado desde `/tmp`: ver §7.1 |
| `12 · 09` §9 quater.1 | «el comportamiento [de auto-crear `[0]`] es específico del campo `emitters` de un `particlesystem`, no una regla del motor» | **Impreciso.** También ocurre con `animcurve.channels` (§6.9) |
| `07 · 13` §6, tabla de comandos | Presenta `RESOURCE SET`/`INFO` con raíces de recurso y `project` | Falta la regla operativa: **escalares sí, listas nunca enteras**, y **comilla simple** para indexar por nombre (§4.0) |
| `07 · 13` §9, «Qué se guarda dónde» | Caché local: `build-*`, `gmpm`, `igor`, `package-tool`, `project-tool`, `prefabs`, `schemas` | Falta `gms2-local-settings`. Y falta el aviso de que **`cache clean --project` borra también la compartida** (§6.4) |
| `07 · 13` §4, tabla de flags | `--toolchain-options` = «JSON con opciones específicas del toolchain» | El esquema completo está en `.gmcache/schemas/gm-options-schema-2.json` y **el JSON que se pasa es el sub-objeto del toolchain** (§2.1) |
| `07 · 13` §3, «Lo que genera» | `gm-options.json` → «toolchain por defecto» | Es el archivo persistente del **mismo esquema**: firma Android, SDKs de YYC, `packageType`… (§2.1) |
| `12 · 09` Trampa 10 | «solo cinco de las 30 propiedades se pueden escribir» | Cierto, **y se amplía**: esas cinco se escriben **por configuración** con `--config` (§5.11) |
| `12 · 09` Trampa 5 | Las fuentes creadas por `resourcetool` no rasterizan | Confirmado, **y tres datos nuevos**: `FONT SETFILE` no copia el `.ttf`, no actualiza `fontName`, y compilar no rasteriza (comprobado releyendo `FONT GLYPHLIST` tras un `compile` con exit 0) |
| `12 · 09` §2 / Trampas 3 y 9 | Bugs de numeración en `FINDORCREATE` | Falta un cuarto caso: **`OBJECT EVENT CHANGE` deja el `.gml` con el nombre viejo** y el compilador no avisa (§5.4) |
| — | — | Falta por completo `ProjectTool` como herramienta con capacidades propias (§7.2) |

### 7.1 `projectpath=` funciona en cualquier comando

```console
$ cd /tmp
$ gm-cli resourcetool eval "resource info expr=project.name projectpath=$HOME/auditoria_cli_r12/audit12/audit12.yyp"
Type: string
project.name = audit12

$ gm-cli resourcetool eval "resource info expr=project.name"      # sin ruta, fuera del proyecto
No Project Loaded
```

La forma posicional (`gm-cli resourcetool eval "<comando>" <ruta.yyp>`) también funciona; son dos
vías equivalentes, no una válida y otra no.

### 7.2 `ProjectTool`: la segunda herramienta que nadie documenta

Vive en `<proyecto>/.gmcache/project-tool/lib/node_modules/@gm-tools/project-tool-osx-arm64/Contents/MacOS/ProjectTool`
(versión **2026.0.174**) y `resourcetool` lo invoca por dentro. Su `help` lista comandos que
`gm-cli` no expone:

| Comando | Para qué | Probado |
|---|---|---|
| `IMPORT YY SOURCES=… ` | **Importar un recurso `.yy` desde otro proyecto** | ✅ (§7.3) |
| `EXPORT … PACKAGETYPE=Project\|Package\|Prefab\|Zip` | **Generar un `.yymps` de Marketplace o un ZIP del proyecto**, con `INCLUDEFOLDERS`/`EXCLUDERESOURCES`/`PREFABASSETS`/`CERTIFICATEPATH` | ✅ `Package` y `Zip` |
| `JSON FORMAT INPUT=… COMMAS=GAMEMAKER\|STANDARD` | **Normalizar un `.yy`/`.yyp` tocado a mano** al estilo exacto de GameMaker | ✅ |
| `LINKS GET/APPLY/CHANGE/FREQUENCY/LIST/LIBS/NULL` | Auditar y reescribir los enlaces a prefabs; `LINKS NULL` pone a `null` los rotos | ⚠️ solo `LIST` |
| `FILE CHANGEVERSION` | Convertir un `.yy` entre formatos `LTS22\|JUN23\|AUG23\|NOV23\|VERSIONED` | ❌ |
| `PROJECT NEW/OPEN/SAVE/CLOSE` | Ciclo de vida del proyecto | ✅ |
| `SIGNING CREATE/PACKAGE/VERIFY/VALIDATE` | Firmar y validar paquetes de Marketplace | ❌ (requiere certificado) |
| `SHOWVERSIONEDTYPES DESTINATION=…` | Volcar las **140** clases de recurso y su versión | ✅ |
| `PREFABS RESTORE` | Lo que falla en §6.1; acepta `PACKAGETOOLREGISTRY`, `PACKAGETOOLVERBOSE`… | ✅ (fallando) |

Argumento global crítico: **`READONLY` vale `TRUE` por defecto**. Sin `READONLY=FALSE`, un
`PROJECT OPEN` seguido de `PROJECT SAVE` no persiste nada.

### 7.3 Importar un recurso de otro proyecto — ✅ (y es la vía para duplicar)

```console
$ cat pjt.txt
PROJECT OPEN SOURCE="…/ImpTest/ImpTest.yyp" READONLY=FALSE
IMPORT YY SOURCES="…/MiPlat3/sprites/spr_backtrees_1/spr_backtrees_1.yy"
PROJECT SAVE
EXIT

$ .gmcache/…/ProjectTool script path=pjt.txt readonly=false
Core Resources : Debug Info - Creating folder: folders/Sprites/Environment/Backgrounds
Core Resources : Debug Info - Adding resource: spr_backtrees_1 to Backgrounds
Saving To: …/ImpTest.yyp as VERSIONED
Saving...............Success

$ gm-cli resourcetool eval "resource list type=sprite"
 spr_backtrees_1
$ gm-cli compile --toolchain GMS2@2026.0.0.23 ; echo $?
◆  Compilation finished
0
```

Copia también los PNG y **recrea la jerarquía de carpetas de origen** (ignora el argumento
`FOLDER=` que se le pase). Es, de paso, la única forma de duplicar un recurso: copiar su carpeta,
renombrar el `.yy` y sus claves `name`/`%Name`, e importarlo.

> ⚠️ Sobre un proyecto muy manipulado, `PROJECT OPEN` disparó el `AccessViolationException` no
> determinista de la Trampa 11 (3 intentos seguidos fallaron). Sobre un proyecto recién creado
> funcionó a la primera. **Reintenta antes de dar por rota la técnica.**

### 7.4 Empaquetar como `.yymps` — ✅

```console
$ .gmcache/…/ProjectTool export source="…/ImpTest.yyp" destination=/tmp/imptest.yymps \
    packagetype=Package packageid=com.prueba.imptest packagename=ImpTest packageversion=1.0.0
ProjectTool Successful
$ unzip -l /tmp/imptest.yymps
      716  yymanifest.xml
     1809  ImpTest.yyp
      149  metadata.json
      297  ImpTest.resource_order
  1191733  sprites/spr_backtrees_1/…png
```

(El primer intento murió con el `AccessViolationException` de la Trampa 11; el segundo funcionó.)
`packagetype=Zip` produce un ZIP del proyecto entero, renombrando el `.yyp` al nombre del destino.

### 7.5 `JSON FORMAT`: la forma segura de cerrar una edición manual de un `.yy`

```console
$ cat /tmp/prueba.yy
{"$GMTest": "v1", "b": 2, "a": 1}

$ ProjectTool json format input=/tmp/prueba.yy output=/tmp/fmt.yy commas=GAMEMAKER
$ cat /tmp/fmt.yy
{
  "$GMTest":"v1",
  "a":1,
  "b":2,
}
```

Ordena las claves y aplica la coma final que usa GameMaker. `COMMAS` es **obligatorio en la
práctica**: omitirlo da `Unrecognised COMMAS argument value:` pese a que la ayuda lo marca opcional.
Cuando la reparación de emergencia de §6.2 te obligue a tocar un `.yyp` con `sed`, **pasa esto
después**.

---

## 8 · Checklist operativo que deja esta auditoría

1. **Nunca `resource create type=shape`.** Rompe el proyecto sin vuelta atrás por CLI (§6.2).
2. **Nunca `gm-cli cache clean --project`** si quieres conservar los runtimes: usa `--cache-dir` (§6.4).
3. Si ves `PREFABS RESTORE exited with code 1`, **compila sin `--errors-only`** para saber la causa
   real; puede no tener nada que ver con prefabs (§6.2).
4. **Parchea el `gmpm.dll` una vez, en una `--cache-dir` propia**, y las 31 plantillas funcionan (§6.1).
5. Después de `OBJECT EVENT CHANGE`, **renombra el `.gml`** a mano (§5.4).
6. Crea la capa `ASSET` **antes** de `ROOM ASSET CREATE` (§5.3).
7. Crea el recurso **ya en su carpeta** (`FOLDER=`): moverlo después no se puede (§6.6).
8. Asigna el `.wav` a un `sound` **en el mismo lote** en que lo creas (§5.7).
9. Fija `tile_count` y `out_columns` del tileset a mano: `TILESET CREATE` los deja a 0 (§5.5).
10. Indexa listas por nombre con **comilla simple**; pasa rutas con espacios con **comilla doble** (§4.0, §5.6).
11. Nada de `=` dentro de un `value=`: replantea la lógica al evento *Create* (§6.8).
12. Antes de escribir «esto no se puede», prueba `RESOURCE INFO EXPR=<recurso> KEYS`,
    `… LIST` sobre el campo, `help <COMANDO>`, los *Global Arguments*, y **el `help` de
    `ProjectTool` y `PackageTool`** — que es donde estaban escondidas la mitad de las respuestas de
    esta auditoría.

---

## 9 · Ver también

- [`07 · 13 — GM CLI, la línea de comandos`](../../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md)
- [`12 · 09 — Manual del agente de IA`](../../12%20-%20Utilidades%20e%20integraciones/09%20-%20Manual%20del%20agente%20de%20IA%20-%20operar%20GameMaker%20con%20gm-cli.md)
- [`_indice/auditorias/r4-agente-ia-gamemaker.md`](r4-agente-ia-gamemaker.md)
- [`_indice/auditorias/r6-regresion.md`](r6-regresion.md)

## 10 · Fuentes

- Ejecución en vivo el **8 de septiembre de 2026** en `~/auditoria_cli_r12/` (proyectos
  `audit12`, `MiPlat3`, `ImpTest`, `P4`, creados y borrados en la sesión), macOS 26 / Apple
  Silicon, `gm-cli` **2.3.0**, `ResourceTool@2026.0.17`, `ProjectTool@2026.0.174`,
  `PackageTool@2024.14.29`, GameMaker LTS 2026.0 (IDE `2026.0.0.16`, runtime `2026.0.0.23`).
- `gm-cli --help` y el `--help` de los 9 comandos y sus 12 subcomandos.
- `gm-cli resourcetool eval "help"` (640 líneas), `ProjectTool help` (260 líneas),
  `PackageTool help`.
- Esquema `<proyecto>/.gmcache/schemas/gm-options-schema-2.json`.
- API de plantillas <https://api.gamemaker.io/api/gamemaker/project-templates> y las URLs de
  descarga que devuelve (`https://api.yoyogames.com/api/2/download?package_id=…`).
- Instalación del IDE en
  `~/Library/Application Support/Steam/steamapps/common/GameMaker Studio 2/GameMaker.app`
  (`Contents/MacOS/arm64/gmpm/gmpm.dll` y `packages/gm-ide-prefabs/`).
