# 09 · Manual del agente de IA — operar GameMaker con `gm-cli`

> Este es el documento que usa un agente de IA cada vez que toca GameMaker de punta a punta:
> crear el proyecto, crear recursos, escribir GML, compilar, depurar y publicar sin abrir el
> IDE. No repite lo que ya explican [`07 · 13`](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md)
> (referencia completa del CLI) y [`07 · 14`](../07%20-%20Ecosistema/14%20-%20IA%20y%20GameMaker.md)
> (qué es el andamiaje `--ai` y cómo se prepara un proyecto para un agente): este documento
> añade **lo que ninguno de los dos cubre** — los cuatro sitios donde un agente se atasca hoy,
> el nombre exacto de archivo que le toca a cada evento, el inventario real de las 80
> herramientas del MCP, la frontera entre lo que un agente puede comprobar solo y lo que debe
> pedir al humano, y los errores que un LLM comete por reflejo al tratar GML como si fuera C#
> de Unity o GDScript de Godot.
>
> Todo lo verificado aquí se ejecutó **en vivo el 7 de septiembre de 2026**, en un proyecto de
> prueba bajo `~` (nunca dentro de esta biblioteca), borrado al terminar cada verificación,
> sobre GameMaker LTS 2026.0 (IDE `2026.0.0.16` · runtime `2026.0.0.23`) con `gm-cli` **2.3.0**
> — la misma versión que documenta el resto de la biblioteca. Reproduce la auditoría completa,
> con más temas y más detalle de investigación, en
> [`_indice/auditorias/r4-agente-ia-gamemaker.md`](../_indice/auditorias/r4-agente-ia-gamemaker.md).

---

## 0 · Las cuatro trampas que hacen fracasar a un agente hoy

Léelas antes de escribir un solo comando. Son silenciosas: no lanzan una excepción que las
delate, así que un agente que no las conozca de antemano pierde el tiempo, o peor, da por
buena una tarea que no lo está.

### Trampa 1 · 9 de las 18 plantillas de `gm-cli init` fallan hoy en macOS

`gm-cli init` con una plantilla que trae *prefabs* falla con `PREFABS RESTORE exited with code
1`. **No es solo Platformer Template** (la única que ya avisaba `07 · 06`): de las 18
plantillas de juego, **9 fallan y 9 funcionan**, siete de las que funcionan con *prefabs* y sin
ningún aviso previo en la biblioteca. **Actualizar a `gm-cli` 2.3.0 no arregla nada**: ya es la
versión instalada y el fallo persiste idéntico.

| Plantilla | Resultado | Verificado |
|---|---|---|
| Space Rocks | ✅ funciona | En esta sesión (`gm-cli init … -t "Space Rocks"`, proyecto creado con `.yyp`) |
| Blank Pixel Game | ✅ funciona | En esta sesión |
| Tower Defense Template | ✅ funciona | En esta sesión |
| RPG Starter Pack | ✅ funciona | En esta sesión |
| Scrolling Shooter Game Template | ✅ funciona | Auditoría r4 (07-09-2026, misma máquina y versión) |
| Survivor Game Template | ✅ funciona | Auditoría r4 |
| Brick Breaker Template | ✅ funciona | Auditoría r4 |
| Puzzle Slider Template | ✅ funciona | Auditoría r4 |
| Fire Jump Template | ✅ funciona | Auditoría r4 |
| Platformer Template | 🔴 `PREFABS RESTORE exited with code 1` | Auditoría r4 (ya documentada por `07 · 06`) |
| Arcade Action Game Template | 🔴 igual | Auditoría r4 |
| Endless Runner Template | 🔴 igual | En esta sesión |
| Idle Game Template | 🔴 igual | En esta sesión |
| Twin Stick Shooter Template | 🔴 igual | En esta sesión |
| Match 3 Template | 🔴 igual | Auditoría r4 |
| Card Game Template | 🔴 igual | Auditoría r4 |
| Cover Assault | 🔴 igual | Auditoría r4 |
| Hero's Trail Base - GML Visual | ⚠️ `Template not found` (ni nombre completo ni parcial) | Auditoría r4 — puede haberse retirado del catálogo |

**Qué hacer**: usa cualquiera de las 9 que funcionan. Si necesitas específicamente una de las 9
que fallan (por ejemplo, Platformer Template), créala desde el IDE — el mismo `ProjectTool` que
usa `gm-cli`, pero con la versión empaquetada en la instalación, sí resuelve los *prefabs*.

```bash
# Bien — cualquiera de estas 9 crea el proyecto sin fallos, verificado hoy mismo:
gm-cli init --no-interactive -n mi-juego -t "Space Rocks" --ai --toolchain GMS2@2026.0.0.23
```

No hay ninguna solución por CLI para las 9 que fallan: no es un flag que falte, ni una versión
que instalar. Detalle de diagnóstico y contexto en [`07 · 13` §12](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md#12-bug-conocido-las-plantillas-con-prefabs-fallan-al-crear-el-proyecto).

### Trampa 2 · `resourcetool eval` y `compile` pueden colgarse bajo el sandbox del Bash tool

**El síntoma**: el mismo comando (`gm-cli resourcetool eval "resource types"`), sobre el mismo
proyecto, responde en menos de un segundo unas veces y se queda colgado indefinidamente otras
— no determinista. `gm-cli compile` puede fallar con `Failed to download Igor: fetch failed`
en vez de colgarse. **Reconócelo así**: llevas más de 20-30 segundos sin salida en un comando
de `resourcetool` o `compile` que en un `run` anterior fue instantáneo.

**La causa, aislada leyendo el propio bundle de `gm-cli`** (`dist/chunk-WDR26R2W.js`, función de
descarga de herramientas): cada llamada a `resourcetool` **no invoca un binario instalado**,
invoca `npx --yes --registry https://gmpm.gamemaker.io @gm-tools/resource-tool-<plataforma>@latest
<comando>`. Aunque el paquete ya esté en caché, `npx` sigue **verificando la versión contra el
registro** antes de ejecutar. Bajo un sandbox de red restringido (el modo por defecto del Bash
tool de Claude Code), esa verificación de red es la que cuelga o falla — nunca el binario en sí.

**La solución que ya está verificada, en dos niveles**:

1. **Desactiva el sandbox para estas llamadas concretas** (`dangerouslyDisableSandbox: true` en
   el Bash tool). Es la vía recomendada: sigues usando `gm-cli` tal cual, sin más cambios.
2. **Si aun así se cuelga o no puedes tocar el sandbox**, invoca el binario `ResourceTool` ya
   cacheado directamente, saltándote la capa `npx`:

   ```bash
   # 1. Localiza el binario cacheado (una vez ejecutado gm-cli resourcetool, ya existe)
   find ~/.npm/_npx -iname "ResourceTool" 2>/dev/null
   # → .../node_modules/@gm-tools/resource-tool-osx-arm64/Contents/MacOS/ResourceTool

   # 2. Invócalo directo: el comando va PRIMERO, luego projectpath= (mismo formato key=value
   #    que usa resourcetool por dentro — verificado leyendo el propio bundle de gm-cli)
   RT="$(find ~/.npm/_npx -iname ResourceTool 2>/dev/null | head -1)"
   "$RT" resource types "projectpath=$(pwd)/mi-juego.yyp"
   ```

   Verificado en esta sesión: la llamada por `npx` puede tardar segundos o colgarse; la llamada
   directa al binario cacheado respondió en **0,3 s**, siempre, en más de 15 invocaciones.

> El MCP `gamemaker-resource-tool` usa la misma capa de descarga por debajo (`gm-cli resourcetool
> mcp` también pasa por `npx`), así que el mismo cuelgue puede darse al arrancar el servidor MCP,
> no solo con `eval`. Si el MCP no arranca en unos segundos bajo sandbox, sospecha de esto antes
> que de la configuración del `.mcp.json`.

### Trampa 3 · `resourcetool` crea el evento equivocado sin avisar (dos bugs de numeración)

Pedir un evento por nombre no siempre crea el archivo que ese nombre promete. Verificado byte a
byte en el `.yy` resultante, en esta sesión:

| Pides (`subtype=`) | Debería crear | Crea de verdad | Colisiona con |
|---|---|---|---|
| `gui_begin` | `Draw_74.gml` | 🔴 `Draw_72.gml` | `draw_begin` |
| `gui_end` | `Draw_75.gml` | 🔴 `Draw_73.gml` | `draw_end` |
| `room_end` (evento `other`) | `Other_5.gml` | 🔴 `Other_3.gml` | `game_end` |

**Consecuencia real**: si un agente pide `draw_begin` y luego `gui_begin` en el mismo objeto, el
segundo `findorcreate` **encuentra el archivo del primero** (`Existing GML file`, no `New GML
file`) — dos eventos semánticamente distintos (dibujar en coordenadas de mundo frente a
coordenadas de pantalla) acaban compartiendo el mismo código, y GameMaker no lo señala como
error porque, desde su punto de vista, no lo es: el archivo existe y es válido.

**La única defensa fiable**: después de cualquier `object event findorcreate`, comprueba el
número real, nunca te fíes del nombre a ciegas:

```bash
gm-cli resourcetool eval "object event list name=<objeto>"
```

Tabla completa de números (Alarm, Step, Draw, Other) verificada, con el detalle de qué archivo
te toca en cada caso, en la [§2](#2--dónde-va-cada-gml-el-nombre-exacto-de-archivo).

### Trampa 4 · El compilador NO detecta una función inventada ni una variable sin declarar

`gm-cli compile` compila **limpio, con exit 0**, código que llama a una función que no existe.
El error solo aparece **en tiempo de ejecución**, y el mensaje ni siquiera nombra el problema
real:

```gml
// Create_0.gml de un objeto — esto COMPILA sin ningún aviso
funcion_que_no_existe_de_verdad(5, "hola");
```

```bash
gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only
echo $?
# 0 — nada en pantalla, "compilación limpia"
```

Y al ejecutar el objeto que la llama (verificado con `gm-cli run`, log real):

```
Variable obj_test_invento.funcion_que_no_existe_de_verdad(100003, -2147483648) not set before reading it.
 at gml_Object_obj_test_invento_Create_0 (line 2) - funcion_que_no_existe_de_verdad(5, "hola");
```

El mensaje dice **«variable»**, no «función inexistente» — GML resuelve los identificadores en
tiempo de ejecución y una llamada a algo que no existe se comporta, a efectos del compilador,
como leer una variable global no inicializada. Un agente que solo mire el `exit code` de
`compile` da por bueno código que no lo está. Por eso `validar-proyecto.py` **no es opcional**:
detalle completo, y una precisión importante sobre sus límites, en [§7](#7--interpretar-los-errores-del-compilador--lo-que-detecta-y-lo-que-no).

---

## 1 · El ciclo completo del agente

`AGENTS.md §5` ya documenta la secuencia y es correcta; esta tabla añade, para cada paso, **qué
comando exacto, qué comprobar y cómo saber que puedes pasar al siguiente** — que es donde un
agente sin experiencia se detiene sin saber si puede seguir.

| # | Paso | Comando | Qué comprueba | Criterio para avanzar |
|---|---|---|---|---|
| 1 | **Idea → receta** | Lee `04 - Recetas por género/` del género que toca | Qué sistemas construir y en qué orden | Tienes una lista de sistemas, no una vaga idea |
| 2 | **Crear el proyecto** | `gm-cli init --no-interactive -n <nombre> -t "<plantilla de la tabla de la Trampa 1>" --ai --toolchain GMS2@2026.0.0.23` | Que exista `<nombre>.yyp` | `ls <nombre>/*.yyp` no está vacío |
| 3 | **Crear recursos** | MCP `gamemaker-resource-tool` o `gm-cli resourcetool eval "<comando>"` — ver [§3](#3--el-mcp-gamemaker-resource-tool-inventario-real) | El recurso aparece en `resource list` y, si es un evento, el `.gml` en la ruta de [§2](#2--dónde-va-cada-gml-el-nombre-exacto-de-archivo) | `object event list name=<obj>` muestra el evento con el número que pediste (por la Trampa 3) |
| 4 | **Escribir GML** | Editor de archivos normal sobre el `.gml` ya creado | Cada símbolo que uses existe: `python3 "_indice/buscar.py" <símbolo>` | Ningún símbolo sin verificar en el código que acabas de escribir |
| 5 | **Compilar** | `gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only` | Sintaxis válida — **NO** que las funciones existan (Trampa 4) | `exit 0` **y** sin salida en `--errors-only` |
| 6 | **Validar antes de confiar en el paso 5** | `python3 "_indice/validar-proyecto.py" <ruta> --todo` | Funciones inventadas (con prefijo de familia del runtime) **y** nombres desconocidos sin definir | `✓ Ninguna llamada a una función del runtime que no exista` **y** la lista de «desconocidas» revisada a mano (ver matiz en [§7](#7--interpretar-los-errores-del-compilador--lo-que-detecta-y-lo-que-no)) |
| 7 | **Corregir** | Vuelve al paso 4 con el error exacto: `gml_Object_<obj>_<Evento>(<línea>) : <mensaje>` | — | Repite 5-6 hasta limpio |
| 8 | **Ejecutar** | `gm-cli run --toolchain GMS2@2026.0.0.23 --target mac` (o el target de tu plataforma) | Comportamiento real — ver [§4](#4--depurar-sin-ver-la-pantalla) para qué puedes leer de la salida | El juego llega al punto que estás probando sin errores no controlados en el log |
| 9 | **Limpiar** | Mata el proceso del *runner* por nombre tras cada `run` de depuración (§4) | Que no queden procesos huérfanos | `ps -ef \| grep -i runner` no devuelve nada tuyo |
| 10 | **Iterar** | Vuelve al paso 3 o 4 según qué falte | — | El sistema de la receta del paso 1 está completo |

**Nunca dos pasos a la vez.** El error más caro de un agente en este ciclo es escribir GML para
tres sistemas y compilar una sola vez al final: el primer error de sintaxis oculta los otros
dos, y el mensaje `gml_Object_<obj>_<Evento>(<línea>)` solo apunta al primero que encuentra el
compilador, no a todos los que hay.

---

## 2 · Dónde va cada `.gml`: el nombre exacto de archivo

La ruta general (`objects/<Nombre>/<Evento>_<N>.gml`, `scripts/<Nombre>/<Nombre>.gml`) ya está
en [`07 · 13` §6](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md#6-gm-cli-resourcetool--editar-el-proyecto-sin-ide).
Lo que falta — y es donde un agente adivina y adivina mal — es **el número exacto** para cada
evento. Todo lo de aquí está verificado en esta sesión creando los eventos de verdad y leyendo
el `.yy` resultante.

### 2.1 Los triviales (sin trampa)

| Evento | Archivo | Nota |
|---|---|---|
| Create / Destroy / CleanUp | `Create_0.gml` / `Destroy_0.gml` / `CleanUp_0.gml` | Siempre sufijo `_0` |
| Alarm 0-11 | `Alarm_0.gml` … `Alarm_11.gml` | El número que pides es el número del archivo, directo |
| Collision con `<objeto>` | `Collision_<objeto>.gml` | El nombre del archivo lleva el **nombre del objeto colisionado**, no un número — verificado: `object event findorcreate name=obj_a type=collision collisionobject=obj_b` → `Collision_obj_b.gml` |
| Keyboard / KeyPress / KeyRelease | `Keyboard_<código>.gml` / `KeyPress_<código>.gml` / `KeyRelease_<código>.gml` | El sufijo es el código de tecla (`vk_space` = 32, verificado: `subtype=32` → `Keyboard_32.gml`) |

### 2.2 Step: normal, begin, end

| Pides (`subtype=`) | Archivo |
|---|---|
| `step_normal` | `Step_0.gml` |
| `step_begin` | `Step_1.gml` |
| `step_end` | `Step_2.gml` |

### 2.3 Draw: tabla completa, con los dos bugs marcados

Verificado creando los nueve subtipos aceptados por `resourcetool` en un objeto de prueba y
leyendo `object event findorcreate` para cada uno. Contrastado además con el `.yy` real de
`testobj` en `OpenGM/OpenGM/Test Gamemaker Projects/EventOrder/` (`11 - Código descargado`) y con
`RoomController.yy` de `gml-raptor`, ambos con los mismos números.

| Pides (`subtype=`) | Archivo real | Número real de GameMaker | ¿Coincide? |
|---|---|---|---|
| `draw_normal` | `Draw_0.gml` | 0 | ✅ |
| `gui` | `Draw_64.gml` | 64 | ✅ |
| `draw_resize` | `Draw_65.gml` | 65 | ✅ |
| `draw_begin` | `Draw_72.gml` | 72 | ✅ |
| `draw_end` | `Draw_73.gml` | 73 | ✅ |
| `gui_begin` | `Draw_72.gml` | debería ser 74 | 🔴 **BUG**: crea el archivo de `draw_begin` |
| `gui_end` | `Draw_73.gml` | debería ser 75 | 🔴 **BUG**: crea el archivo de `draw_end` |
| `draw_pre` | `Draw_76.gml` | 76 | ✅ |
| `draw_post` | `Draw_77.gml` | 77 | ✅ |

> No existe forma de forzar el número real (74, 75) por `resourcetool`: la whitelist de
> subtipos de `draw` es cerrada y `gui_begin`/`gui_end` son los únicos nombres que apuntan a
> esos eventos, así que hoy **no hay manera de crear un GUI Begin/End real por CLI o MCP**. Si
> tu juego necesita distinguir de verdad `draw_begin` de `gui_begin`, créalos desde el IDE.

### 2.4 Other: tabla completa, con los dos bugs marcados

Verificado igual que Draw, con los 14 subtipos que acepta la whitelist de `resourcetool` (los
eventos Async — HTTP, Save/Load, Steam, Cloud, redes — **no están en esta lista y no se pueden
crear por CLI ni MCP**, ni por nombre ni forzando el número real como `subtype`: `type=other
subtype=62` da `Invalid subtype`).

| Pides (`subtype=`) | Archivo real | Número real | ¿Coincide? |
|---|---|---|---|
| `outside` | `Other_0.gml` | 0 | ✅ |
| `boundary` | `Other_1.gml` | 1 | ✅ |
| `game_start` | `Other_2.gml` | 2 | ✅ |
| `game_end` | `Other_3.gml` | 3 | ✅ |
| `room_start` | `Other_4.gml` | 4 | ✅ |
| `room_end` | `Other_3.gml` | debería ser 5 | 🔴 **BUG**: crea el archivo de `game_end` |
| `animation_end` | `Other_7.gml` | 7 | ✅ |
| `end_of_path` | `Other_8.gml` | 8 | ✅ |
| `user0` | `Other_10.gml` | 10 | ✅ |
| `broadcast_message` | `Other_1.gml` | ⚠️ no confirmado cuál es el real | 🟡 colisiona con `boundary`, sin resolver — evento poco documentado incluso fuera de esta biblioteca |
| `outside_view0` | `Other_40.gml` | 40 | ✅ |
| `boundary_view0` | `Other_50.gml` | 50 | ✅ |
| `animation_update` | `Other_58.gml` | 58 | ✅ |
| `animation_event` | `Other_59.gml` | 59 | ✅ |

> `user1` a `user15` **existen en GameMaker real** pero `resourcetool` los rechaza: la
> whitelist de `other` se cierra en `user0`. Para usar `user1`-`user15` necesitas crearlos desde
> el IDE, o reutilizar un `Other_11.gml`…`Other_25.gml` que ya venga en una plantilla.

### 2.5 La regla de oro para no caer en las dos trampas anteriores

**Después de cualquier `object event findorcreate` en `draw` u `other`, verifica**:

```bash
gm-cli resourcetool eval "object event list name=<objeto>"
```

Si el resultado no muestra el subtipo exacto que pediste (por ejemplo, pediste `gui_begin` y la
tabla solo lista `Event_Draw_DrawBegin`), el evento se coló en el archivo equivocado — bórralo y
edita el `.gml` que corresponde de verdad, o edítalo desde el IDE si necesitas el evento real.

---

## 3 · El MCP `gamemaker-resource-tool`: inventario real

`07 · 14` explica **qué es** el andamiaje `--ai` y cómo se prepara un proyecto; esto es **lo que
expone de verdad el servidor**, obtenido por introspección directa del protocolo (`initialize` +
`tools/list` por stdio, JSON delimitado por salto de línea — no el *framing* `Content-Length` de
LSP) sobre un proyecto de prueba en esta sesión: **80 herramientas exactas.**

```
status, help, helptable, global_arguments, resource_set, resource_info, resource_create,
resource_delete, resource_list, resource_types, project_rename, object_event_findorcreate,
object_event_delete, object_event_change, object_event_list, object_event_types,
room_instance_create, room_asset_create, room_item_list, room_item_delete, room_layer_create,
room_layer_delete, room_layer_list, room_layer_tiles_get, room_layer_tiles_set,
room_layer_tiles_list, room_layer_tiles_resize, room_layer_tiles_info, room_list,
gml_getgmlfilepath, sprite_addframe, sprite_deleteframe, sound_setfile, tileset_create,
tileset_delete, tileset_rename, tileset_setsprite, config_list, config_usages, config_create,
config_delete, config_rename, config_getactive, config_setactive, audiogroup_create,
audiogroup_delete, audiogroup_rename, audiogroup_list, audiogroup_usages, audiogroup_set,
texturegroup_create, texturegroup_delete, texturegroup_rename, texturegroup_list,
texturegroup_usages, texturegroup_set, prefab_list, prefab_info, prefab_addreference,
prefab_removereference, prefab_customise, shader_getfilepath, note_getfilepath, path_addpoint,
path_info, path_deletepoint, font_rangelist, font_addrange, font_removerange, font_kerninglist,
font_addkerning, font_removekerning, font_glyphlist, font_setfile, folder_list, folder_create,
options_list, options_get, options_info, options_set
```

### 3.1 Lo que el MCP NO tiene (y `resourcetool eval` sí)

Cinco operaciones existen en `eval` (comandos `DEFAULTS GET/SET`, `GML SETGMLFILE`, `OBJECT
EVENT SETGMLFILE`, `SHADER SETFILEPATH`, `NOTE SETFILEPATH` del inventario de `07 · 13` §6) y
**no tienen tool equivalente en el MCP**:

| Falta en el MCP | Para qué sirve | Alternativa con MCP conectado |
|---|---|---|
| `defaults_get` / `defaults_set` | Fijar valores por defecto para no repetir argumentos | Pasa siempre el argumento completo |
| `gml_setgmlfile` | Cambiar la ruta del `.gml` que respalda un **script** | Cae a `resourcetool eval "gml setgmlfile ..."` |
| `object_event_setgmlfile` | Cambiar la ruta del `.gml` de un **evento** | Cae a `resourcetool eval "object event setgmlfile ..."` |
| `shader_setfilepath` | Fijar el fichero fuente de un shader (solo hay `shader_getfilepath`, de lectura) | Cae a `resourcetool eval "shader setfilepath ..."` |
| `note_setfilepath` | Fijar el fichero de una nota (solo hay `note_getfilepath`) | Cae a `resourcetool eval "note setfilepath ..."` |

Para estas cinco, un agente con el MCP conectado **debe** caer igualmente a `resourcetool eval`.
Todo lo demás está disponible por las dos vías.

### 3.2 Cuándo conviene cada vía

| Situación | Usa |
|---|---|
| Sesión interactiva de Claude Code con `.mcp.json` del proyecto cargado | El MCP — llamadas tipadas, sin parsear texto |
| Script, CI, o cualquiera de las cinco operaciones de §3.1 | `resourcetool eval "<comando>"` |
| El MCP no arranca o la sesión no lo tiene disponible | `resourcetool eval` — es funcionalmente equivalente salvo §3.1 |
| Sospechas del cuelgue de la Trampa 2 | El binario `ResourceTool` cacheado, directo, sin `npx` ni MCP |

### 3.3 Si el MCP no está en la sesión

El MCP es **por proyecto**: `gm-cli resourcetool mcp` exige un `.yyp` y se cierra si no lo
encuentra. Un proyecto creado con `gm-cli init` ya trae su `.mcp.json`; uno existente necesita
`gm-mcp-setup .` desde su raíz. Si aun así no aparece en la sesión (por ejemplo, el agente no
arrancó dentro de la carpeta del proyecto, o el servidor se colgó por la Trampa 2), usa
`gm-cli resourcetool eval "<comando>"` para todo: es el mismo `ResourceTool` por debajo, solo
cambia el transporte.

---

## 4 · Depurar sin ver la pantalla

### 4.1 Lo que un agente SÍ puede observar por sí solo

| Señal | Cómo se captura | Verificado |
|---|---|---|
| `show_debug_message(...)` | Aparece literal en el `stdout` de `gm-cli run`, prefijado con `│` | `13 · 10` §7.2 (ya documentado) |
| Fin de partida controlado | El marcador `###game_end###N` en el `stdout` | `13 · 10` §3.4 (ya documentado) |
| Errores de compilación | Formato `gml_Object_<obj>_<Evento>(<línea>) : <mensaje>` en `stdout`/`stderr` | Ver [§7](#7--interpretar-los-errores-del-compilador--lo-que-detecta-y-lo-que-no) |
| Errores de compilación, en JSON | Bloque `{"errors":[{"source":"AssetCompiler","message":"..."}]}` al final de un `compile` fallido — parseable, mejor que hacer *grep* del texto con bordes `│` | Verificado en esta sesión, ver §7 |
| Errores de ejecución no controlados | `Variable X.Y(...) not set before reading it` y similares, en el `stdout` de `run` | Verificado en esta sesión (Trampa 4) |
| Capturas de pantalla del propio juego | `screen_save(nombre)` desde GML, disparado en el momento que interesa | `13 · 10` §7.3 (ya documentado) |
| Rendimiento agregado | `get_timer()`, `gc_get_stats()` (no en HTML5) | `13 · 10` §6 |
| Una tanda de pruebas propia | Mini-framework de un solo script (`scr_pruebas`), interruptor por `config` o variable de entorno | `13 · 10` §2-3 (ya documentado extensamente) |

### 4.2 Lo que un agente NO puede comprobar por sí solo — pídeselo al humano

| No puedes verificar tú solo | Por qué | Pídele al humano que |
|---|---|---|
| Que el juego **se vea** como se pretende | No hay salida visual que el agente pueda inspeccionar directamente sin capturas manuales | Mire una captura (`screen_save`) o juegue una build |
| **Sonido**: mezcla, volumen relativo, si algo se oye mal | No hay forma de «escuchar» el audio generado desde el log | Escuche una build con auriculares |
| **Input táctil o de mando físico** | `gm-cli run` no simula gestos ni un gamepad real conectado | Pruebe en el dispositivo o mando real |
| **Rendimiento en el dispositivo real** (móvil, consola) | El *runner* de escritorio no reproduce la CPU/GPU del objetivo | Ejecute un *profiling* en el hardware real |
| **Certificación de plataforma** (Steam, consolas, tiendas) | Requiere procesos y revisiones fuera de GameMaker | Gestione el envío y la revisión |
| **Sensación / *game feel* subjetiva** | Es una valoración humana, no un dato del log | Juegue y dé su impresión |
| Un evento **Async** (HTTP, Save/Load, Steam, redes) que no se puede crear por CLI/MCP | Whitelist cerrada de `resourcetool` (§2.4) | Cree el evento desde el IDE, o reutilice uno ya presente en una plantilla |

**Regla práctica**: si la comprobación depende de un sentido humano (vista, oído) o de hardware
que el `runner` de escritorio no reproduce, no está a tu alcance como agente — dilo con
claridad en vez de asumir que «compila y no truena en el log» equivale a «funciona bien».

### 4.3 `gm-cli run` no propaga el estado del juego — y deja procesos huérfanos si crashea

Ya está documentado que `gm-cli run` sale con `0` aunque el juego llame a `game_end(1)` (`13 ·
10` §3.4). Lo que no estaba escrito: **si el juego crashea con un error no controlado, el
proceso de `gm-cli run` tampoco termina por sí solo.** Hay que envolver la llamada con un
timeout y matar el proceso hijo explícitamente por nombre, o los procesos se acumulan:

```bash
gm-cli run --toolchain GMS2@2026.0.0.23 --target mac > salida.log 2>&1 &
PID_RUN=$!
sleep 15                       # tiempo suficiente para que el juego llegue al punto que pruebas
kill $PID_RUN 2>/dev/null
pkill -f Mac_Runner 2>/dev/null   # en macOS; el nombre del runner cambia por plataforma
```

Un agente que solo ponga un `timeout` al comando padre y no mate el proceso hijo del *runner*
por nombre acumula juegos zombis en cada iteración de depuración automatizada.

---

## 5 · Assets sin artista

### 5.1 Audio

Ya resuelto, con la escalera de prioridad completa (síntesis en runtime → generador externo →
`PLACEHOLDERS.md`) y el catálogo mínimo de sonidos sintetizables, en
[`13 · 09` §8 bis](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md#8-bis--un-agente-sin-archivo-de-audio-la-escalera-de-prioridad).
No se repite aquí.

### 5.2 Gráfico: la misma idea, para sprites

La escalera es la misma que para audio, y comparte el patrón de `PLACEHOLDERS.md` ya descrito en
[`13 · 11` §5](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#5--assets-y-pipeline).

1. **Dibuja con GML puro, sin ningún sprite** — `draw_rectangle`, `draw_circle` u otras
   primitivas de dibujo directamente en el evento Draw. Cero archivos, cero pasos fuera de
   GameMaker. Es el placeholder más barato que existe y patrón habitual en varias recetas de
   `13/02`.
2. **Genera un PNG plano por código y impórtalo**, cuando el objeto sí necesita ser un `sprite`
   de verdad (por ejemplo, para tener máscara de colisión o entrar en un sistema de animación).
   Verificado en esta sesión, sin errores, sin dependencias de red:

   ```bash
   # Con ImageMagick (ya instalado en este Mac)
   magick -size 64x64 xc:"#ff3366" spr_placeholder.png
   ```

   ```python
   # O con Python + Pillow, si no hay ImageMagick disponible
   from PIL import Image
   Image.new("RGB", (64, 64), (255, 51, 102)).save("spr_placeholder.png")
   ```

   ```bash
   gm-cli resourcetool eval "resource create type=sprite name=spr_placeholder"
   gm-cli resourcetool eval "sprite addframe name=spr_placeholder path=spr_placeholder.png"
   ```

   El sprite resultante toma el tamaño del PNG. Nombra el archivo con el **nombre definitivo
   del asset** desde el principio (`spr_jugador_idle`, no `spr_temp1`): así sustituir el
   contenido más adelante no toca ni una línea de código, siguiendo el mismo principio que ya
   fija `13 · 11` §5 para placeholders de arte.
3. **Lístalo en `PLACEHOLDERS.md`** si el placeholder va a convivir con el proyecto más de una
   sesión, para que no se cuele sin querer en una build o captura final.

> No hay generador de arte por IA configurado en esta biblioteca por defecto: si necesitas algo
> más elaborado que un color plano, la política del proyecto (fuera de esta biblioteca, en la
> skill hermana `gamedev-self-generated-assets`) es generarlo tú por código o pedirlo al
> humano — nunca depender de una API de terceros sin configurar.

---

## 6 · Errores típicos de un LLM con GameMaker

### 6.1 Lo que un LLM se inventa

| Se inventa | Por qué | Cómo evitarlo |
|---|---|---|
| Firmas de función «razonables» que no existen | El nombre suena plausible por analogía con otra función real | `python3 "_indice/buscar.py" <símbolo>` **antes** de escribir la llamada, siempre |
| Que `resource create type=object ... parent=X` fija la herencia | La tabla de `resourcetool` sugiere que `parent=` es genérico | `parent=` en `RESOURCE CREATE` es la carpeta del Asset Browser (igual que `folder=`), **no** la herencia. El padre real se fija con `resource set expr=<hijo>.parentObjectId value=<padre>` **después** de crear ambos objetos — verificado: `resource create type=object name=X parent=obj_padre` falla con `Failed to add resource '...' to project` |
| Aritmética directa sobre IDs de asset (`sprite_index + 1`) | Costumbre de motores donde los IDs son enteros | En 2026 son *handles*, no enteros — [`01 · 03`](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) |
| Que el `exit code 0` de `gm-cli compile` certifica que el código es correcto | Es lo que significa en casi cualquier otro compilador | No en GML: ver la Trampa 4 y [§7](#7--interpretar-los-errores-del-compilador--lo-que-detecta-y-lo-que-no) |

### 6.2 Lo que un LLM confunde

- **Los dos bugs de numeración de eventos** (§2.3-2.4): pedir `gui_begin` y creer que se creó de
  verdad porque no hubo error.
- **`Collision_<objeto>.gml` usa el nombre del objeto, no un número** — a diferencia de casi
  todos los demás eventos, que sí lo hacen. Es fácil intentar `Collision_1.gml` por analogía con
  `Alarm_1.gml` y equivocarse.
- **`Other_<N>.gml` con `broadcast_message`** colisiona con `boundary` (§2.4): un agente que
  cree ambos eventos en el mismo objeto acaba con un solo archivo compartido, sin aviso.
- **El mensaje de la Trampa 4** dice «variable», y un agente que busque la palabra «función» en
  el log de error no la encontrará — hay que reconocer el patrón `not set before reading it`
  como «esto probablemente es una función que no existe», no solo como una variable olvidada.

### 6.3 Patrones de otro motor que no aplican en GML

| En Unity / Godot / Unreal | El reflejo equivocado en GML | Lo que hay que hacer en GameMaker |
|---|---|---|
| `Update()` / `_process()` cada frame | Buscar una función `Update` que sobrescribir | El Step Event (`Step_0.gml`) ya se ejecuta cada frame — no hay que definir ni llamar a nada |
| `Awake()`/`Start()` / `_ready()` al instanciar | Buscar un evento de «inicialización tardía» | El Create Event (`Create_0.gml`) ya cubre ambos casos; si necesitas separar «antes de que existan los demás» de «cuando ya existen todos», usa Room Start (`other/room_start` → `Other_4.gml`), no busques un segundo Create |
| `this.propiedad` dentro de un método de instancia | Escribir `this.` en GML | GML usa `self` implícito (casi nunca hace falta escribirlo) o `id` para referirte a la instancia propia; `this` no es la sintaxis del lenguaje |
| Prefabs de escena que se instancian con `Instantiate()` | Buscar un `Instantiate()` genérico | `instance_create_layer(x, y, layer_id, obj, [var_struct])` crea una instancia de un **objeto** (el equivalente a la clase, no al prefab-escena) directamente en una capa |
| `OnCollisionEnter`/`OnTriggerEnter` como un único callback genérico | Un solo evento de colisión para «cualquier cosa» | Cada combinación objeto-contra-objeto es **su propio archivo** (`Collision_<objeto>.gml`, §2.1); si un objeto puede chocar con cinco tipos distintos, son cinco eventos de colisión distintos, uno por cada objeto contra el que puede chocar |
| *Singletons* con `DontDestroyOnLoad` / *autoload* | Buscar un decorador o flag de «no destruir» | Un objeto **persistente** (`persistent = true`, o la propiedad del objeto en el editor/`resourcetool`) sobrevive al cambio de room; combínalo con una sola instancia creada una vez, no con una clase estática |
| Corutinas (`yield return`, `await`) para esperar frames | Buscar `await` o `yield` en GML | GML no tiene corutinas: usa Alarms para esperas con temporizador, o una máquina de estados con variables de instancia y el Step Event — ver [`01 · 09`](../01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md) |
| Delta time multiplicando el movimiento (`* Time.deltaTime`) | Multiplicar la velocidad por un delta time manual por reflejo | El Step Event de GameMaker corre a un *framerate* fijo por defecto (`game_get_speed()` te da el real); antes de replicar el patrón de *delta time* de otro motor, confirma si tu juego lo necesita — no es automático ni obligatorio en GML |

---

## 7 · Interpretar los errores del compilador — lo que detecta y lo que no

### 7.1 El formato de un error de sintaxis normal

```
gml_Object_obj_player_Step_0(0) : unexpected symbol ";" in expression
```

`gml_Object_<objeto>_<Evento>(<línea>) : <mensaje>` — verificado en esta sesión rompiendo a
propósito un `Create_0.gml` con `var _horizontal = ;`. Autoexplicativo una vez visto, pero
ningún documento lo daba como formato general hasta ahora.

### 7.2 La salida JSON al final de un `compile` fallido

Además del log en texto con bordes `│`, `gm-cli compile` imprime al final un bloque JSON
parseable — mejor que hacer *grep* del texto bonito:

```json
{"errors":[{"source":"AssetCompiler","message":"gml_Object_obj_test_invento_Create_0(0) : unexpected symbol \";\" in expression"},{"source":"AssetCompiler","message":".../GMAssetCompiler.dll exited with non-zero status (1)"}]}
```

### 7.3 🔴 El crash silencioso: un `constructor` con padre no definido tira abajo el `AssetCompiler` entero

Este hallazgo llevaba viviendo solo en un documento de seguimiento interno de auditorías
(`_indice/PENDIENTE-r3.md`) que un agente no visita en su flujo normal. Se promueve aquí y a
[`13 · 10`](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#85-interpretar-los-errores-lo-que-el-compilador-sí-detecta-y-lo-que-no).

```gml
// scripts/scr_test_crash/scr_test_crash.gml — NO HAGAS ESTO: PadreQueNoExiste no está definido
function Hijo() : PadreQueNoExiste() constructor {
    valor = 1;
}
```

Reproducido en esta sesión: el `AssetCompiler` se cae **tres veces seguidas**, sin línea, sin
mensaje que mencione `constructor` ni herencia:

```
Command failed:
/…/runtime-2026.0.0.23/bin/assetcompiler/osx/arm64/GMAssetCompiler.dll exited with non-zero status (1)
```

Y el bloque JSON, para este caso concreto, **no trae ningún mensaje útil añadido** — solo repite
el «exited with non-zero status (1)» genérico, a diferencia del error de sintaxis normal de
§7.2, que sí trae el mensaje real además del genérico:

```json
{"errors":[{"source":"AssetCompiler","message":".../GMAssetCompiler.dll exited with non-zero status (1)"}]}
```

**Cómo reconocerlo**: si un `compile` falla sin ninguna línea ni mensaje de GML, y el proyecto
usa herencia con `constructor` (`function Hijo() : Padre() constructor {}`), sospecha primero de
un padre mal escrito o no definido antes que de cualquier otra cosa — es la causa más difícil de
encontrar por descarte porque el compilador no señala ni el archivo ni la línea.

### 7.4 Otras trampas del motor descubiertas al compilar 3 501 bloques de la biblioteca

También vivían solo en `PENDIENTE-r3.md`. Encontradas por `validar-compilacion-docs.py`
compilando el GML de la propia biblioteca contra el runtime real — no son errores de esta
biblioteca, son comportamientos reales del compilador que conviene conocer antes de escribir:

| Trampa | Por qué falla |
|---|---|
| **GML no admite notación científica**: `1e10` | Se trocea en el literal `1` seguido del identificador `e10` — no es un error de sintaxis claro, es un *token* inesperado más adelante en la línea |
| **El ternario anidado necesita paréntesis** | `a ? x : b ? y : z` falla; escribe `a ? x : (b ? y : z)` |
| **`const` no existe en GML** | Usa `#macro NOMBRE valor` para una constante |
| **`skeleton_animation_set(animname, [loop])`** no tiene argumento de *track* | Buscar una firma con más argumentos por analogía con otros motores de animación por *skeleton* falla |
| **`skeleton_animation_get_position`** devuelve 0-1 normalizado | No son segundos — un error habitual es tratarlo como un tiempo absoluto |
| **`keyboard_unset_map()`** no acepta argumentos | Llamarla con un argumento es un error de sintaxis, no de lógica |

### 7.5 Por qué `validar-proyecto.py` no es opcional — y un matiz importante sobre lo que detecta de verdad

La razón de fondo, en una frase: **GML resuelve los nombres de función en tiempo de ejecución,
así que llamar a una que no existe no es un error de compilación — es solo de ejecución**, con
un mensaje que dice «variable», no «función» (Trampa 4). `gm-cli compile` con exit 0 **no**
certifica que el código esté libre de funciones inventadas.

**El matiz, verificado en esta sesión y no explícito en ningún sitio hasta ahora**:
`validar-proyecto.py` clasifica cada llamada en cuatro categorías, y solo una hace fallar el
comando (exit 1):

```
python3 "_indice/validar-proyecto.py" <ruta-del-proyecto> [--todo] [--json]
```

| Categoría | Cuándo se marca | ¿Falla el comando (`exit 1`)? |
|---|---|---|
| `INVENTADA` | El nombre lleva un **prefijo de familia del runtime** (`draw_`, `audio_`, `string_`…) y no existe | ✅ Sí — es lo que se ve sin ningún flag |
| `obsoleta` | La función existe pero está marcada como obsoleta | ⚠️ Aviso, no falla |
| **`desconocida`** | El nombre **no** lleva prefijo de familia y no está definido en el proyecto ni en el runtime | ❌ **No hace fallar el comando**, y **solo se lista con `--todo`** |
| `runtime`/`propia`/`extensión` | Existe de verdad | Correcto |

Verificado con el mismo ejemplo de la Trampa 4: `funcion_que_no_existe_de_verdad()` **no** lleva
prefijo de familia, así que `validar-proyecto.py` sin `--todo` responde `✓ Ninguna llamada a una
función del runtime que no exista` con **exit 0** — silencio total sobre el problema real. Solo
con `--todo` aparece, y como aviso informativo, no como error:

```
· 1 nombres que el proyecto no define ni el runtime declara (--todo para verlos):
  funcion_que_no_existe_de_verdad()  en objects/obj_test_invento/Create_0.gml
```

Con un nombre que sí lleva prefijo de familia (`draw_super_mega_sprite()`), el mismo comando
**sin** `--todo` ya falla con exit 1 y la etiqueta `INVENTADA`.

**Consecuencia práctica para un agente**: la mayoría de funciones propias que va a escribir un
LLM (nombres de dominio en español, sin prefijo de familia, tal y como pide `BRIEF-redactor.md`
regla 2) caen en la categoría `desconocida` si tienen una errata o si se llaman antes de
definirse. **Ejecuta siempre `validar-proyecto.py` con `--todo`** y revisa a mano la lista de
`desconocida` — el exit code por sí solo no es suficiente para ese caso, solo para el de una
función con pinta de pertenecer al runtime.

```bash
# La forma correcta de usarlo antes de dar una tarea por terminada
python3 "_indice/validar-proyecto.py" <ruta-del-proyecto> --todo
```

---

## 8 · Checklist final antes de dar una tarea por terminada

- [ ] Cada símbolo de GML que escribiste está verificado con `buscar.py` (no «creo que existe»).
- [ ] Cada evento que creaste con `resourcetool` se comprobó con `object event list name=<obj>`
      — no te fiaste del nombre del subtipo a ciegas (§2.5).
- [ ] `gm-cli compile --errors-only` da `exit 0` y **sin salida**.
- [ ] `validar-proyecto.py <ruta> --todo` da `✓ Ninguna función INVENTADA` **y** revisaste a mano
      la lista de `desconocida` (§7.5) — no solo miraste el exit code.
- [ ] Si el proyecto usa `constructor` con herencia, ningún padre queda sin definir (§7.3).
- [ ] Ejecutaste el juego (`gm-cli run`) al menos hasta el punto que estás probando, y no quedó
      ningún proceso de *runner* huérfano (§4.3).
- [ ] Si algo depende de vista, oído, hardware real o certificación de plataforma, lo dijiste
      explícitamente en vez de darlo por bueno (§4.2).

---

## Ver también

- [`07 · 13 — GM CLI, la línea de comandos`](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md) — referencia completa del CLI, inventario de comandos de `resourcetool eval`.
- [`07 · 14 — IA y GameMaker`](../07%20-%20Ecosistema/14%20-%20IA%20y%20GameMaker.md) — qué genera `gm-cli init --ai`, reglas para el agente, MCP por proyecto.
- [`07 · 06 — Plantillas y starters`](../07%20-%20Ecosistema/06%20-%20Plantillas%20y%20starters.md) — catálogo completo de las 31 plantillas.
- [`13 · 10 — Testing y QA`](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/10%20-%20Testing%20y%20QA.md) — mini-framework de pruebas, `show_debug_message`, `###game_end###`, capturas automáticas, interpretar errores del compilador.
- [`13 · 09 §8 bis — Un agente sin archivo de audio`](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md#8-bis--un-agente-sin-archivo-de-audio-la-escalera-de-prioridad) — escalera de prioridad de audio sin artista.
- [`13 · 11 §5 — Assets y pipeline`](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#5--assets-y-pipeline) — patrón `PLACEHOLDERS.md`.
- [`01 · 03 — Handles`](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) — por qué no se puede hacer aritmética con IDs de asset.
- [`01 · 09 — Instancias, objetos y herencia`](../01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md) — `self`, `id`, máquinas de estado sin corutinas.
- [`AGENTS.md`](../AGENTS.md) — la regla que lo gobierna todo y el flujo recomendado de la biblioteca.
- [`_indice/auditorias/r4-agente-ia-gamemaker.md`](../_indice/auditorias/r4-agente-ia-gamemaker.md) — la auditoría completa de la que sale este documento, con más temas y más detalle de investigación.

## Fuentes

- Ejecución en vivo en un proyecto de prueba bajo `~` (creado y borrado en esta sesión, nunca
  dentro de la biblioteca ni en `/private/tmp`), sobre GameMaker LTS 2026.0 (IDE `2026.0.0.16`,
  runtime `2026.0.0.23`) y `gm-cli` 2.3.0 — 7 de septiembre de 2026.
- Introspección directa del protocolo MCP (`initialize` + `tools/list` por stdio) sobre
  `gm-cli resourcetool mcp` — 7 de septiembre de 2026.
- Lectura del propio bundle de `gm-cli` (`dist/chunk-WDR26R2W.js`, `dist/chunk-MM37US67.js`) para
  aislar la causa exacta del cuelgue bajo sandbox (llamada `npx --yes --registry
  https://gmpm.gamemaker.io ...`) y el formato de argumentos del binario `ResourceTool`
  (`<comando> projectpath=<ruta> [projecttool=] [prefabsfolder=] [config=]`) — 7 de septiembre de
  2026.
- `11 - Código descargado/juegos_y_motores/OpenGM/OpenGM/Test Gamemaker Projects/EventOrder/objects/testobj/testobj.yy`
  y `11 - Código descargado/librerias/utilidades/gml-raptor/game/objects/RoomController/RoomController.yy`
  — código real con los números de evento Draw/Other verificados de forma independiente.
- [`_indice/auditorias/r4-agente-ia-gamemaker.md`](../_indice/auditorias/r4-agente-ia-gamemaker.md)
  (7 de septiembre de 2026) — auditoría origen de este documento; fuente de la matriz completa de
  las 18 plantillas para las que no se repitió la prueba en esta sesión.
- `_indice/PENDIENTE-r3.md` — hallazgos del crash del `AssetCompiler` y las trampas de compilación
  de §7.4, promovidos aquí desde ese documento de seguimiento interno.
