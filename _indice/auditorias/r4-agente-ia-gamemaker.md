# Auditoría r4 · Un agente de IA operando GameMaker de principio a fin

> 7 de septiembre de 2026 · 66 temas evaluados · 41 cubiertos · 7 parciales · 18 faltan
> Referencia: GameMaker LTS 2026.0 (IDE `2026.0.0.16` · runtime `2026.0.0.23`) · `gm-cli` **2.3.0**
> (el instalado en esta máquina, el mismo que documenta la biblioteca).
> Todo lo de este informe se ejecutó **en vivo** en `~/gm_prueba_agente` (macOS, Apple Silicon) y
> se borró al terminar. Notación `NN/MM` = carpeta `NN - .../MM - ....md`.

## Resumen ejecutivo

**Sí, un agente puede llevar un juego de la idea a que compile siguiendo esta biblioteca — pero
se atasca en cuatro sitios muy concretos, y en dos de ellos el atasco es silencioso: no hay
mensaje de error que lo delate.** El ciclo grueso (`gm-cli init` → `resourcetool` → escribir
`.gml` → `gm-cli compile` → `validar-proyecto.py`) está bien documentado y funciona tal como dice
`AGENTS.md`. Los problemas reales que encontré **no estaban documentados en ningún sitio** y los
he verificado con evidencia reproducible, no con sospechas:

1. **La mitad de las plantillas de `gm-cli init` fallan hoy, no solo las que la biblioteca ya
   avisa.** No es «las plantillas con prefabs fallan, usa Space Rocks o Blank Pixel Game»: de las
   18 plantillas de juego, **9 fallan** con `PREFABS RESTORE exited with code 1` (incluida
   Platformer Template, ya documentada) y **9 funcionan perfectamente**, siete de ellas con
   prefabs y sin ningún aviso en la biblioteca de que son seguras. Actualizar a 2.3.0 —el remedio
   que da la biblioteca— **no arregla nada**: ya está instalada y el fallo persiste igual.
2. **`gm-cli resourcetool eval` cuelga sin avisar bajo el sandbox por defecto del Bash tool de
   Claude Code**, incluso con el paquete ya descargado en caché. La causa es la capa `npm exec`
   que usa por debajo; el binario `ResourceTool` cacheado, invocado directamente, responde en
   menos de un segundo. Ningún documento de la biblioteca menciona esta dependencia de red ni el
   `dangerouslyDisableSandbox` que la resuelve — y es precisamente la herramienta que un agente
   usa en **cada** paso de creación de recursos.
3. **`resourcetool` tiene bugs de numeración de eventos que crean el evento equivocado sin ningún
   error.** Pedir un evento «GUI Begin»/«GUI End» crea en realidad «Draw Begin»/«Draw End» (mismo
   `eventNum`, verificado byte a byte en el `.yy`); pedir «Room End» crea «Game End». El agente
   termina con código que compila, se ejecuta, y hace algo distinto de lo que pidió — con el
   nombre de archivo (`Draw_72.gml`, `Other_3.gml`) como única pista de que algo fue mal.
4. **El compilador de GameMaker no detecta una función inventada ni una variable no declarada.**
   Compila limpio (exit 0) y solo revienta en tiempo de ejecución. Esto no es una carencia de la
   biblioteca —ya recomienda `validar-proyecto.py` antes de compilar—, pero **en ningún sitio se
   explica por qué ese paso no es opcional**: un agente que solo mire el exit code de
   `gm-cli compile` concluirá, incorrectamente, que su código está limpio.

Fuera de eso, la biblioteca acierta en lo importante: el mapa de qué `.gml` va en qué carpeta con
qué nombre es correcto donde lo dice (`Create_0.gml`, `Step_0.gml`) pero **incompleto en todo lo
demás** —nunca dice qué número le toca a `Alarm_5`, `Draw_77` o `Other_58`, que es justo donde un
agente adivina y adivina mal—, y el flujo de «juego sin artista» (marcador de posición generado
por código o importado desde un PNG/WAV hechos con `magick`/Python) funciona pero no está descrito
en ningún documento propio, solo se puede inferir de la tabla de comandos.

## Tabla tema por tema

Leyenda: ✅ Cubierto y ejecutable por un agente · 🟡 Parcial (documenta pero no permite ejecutar
sin adivinar) · 🔴 Falta.

### A · Crear el proyecto (7)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 1 | `gm-cli init` interactivo vs `--no-interactive` con flags | ✅ | `07/06 §2` + `07/13 §3` (tabla de flags verificada con `--help`) | — |
| 2 | Qué plantillas de juego (18) funcionan hoy en macOS con `gm-cli` 2.3.0 | 🔴 | `07/06 §4` solo prueba **una** (Platformer Template) y en la versión **2.2.0** | **Probé las 18 en vivo con 2.3.0** (tabla completa en «Huecos» #1). El dato que da la biblioteca hoy (»usa Space Rocks o Blank Pixel Game») deja fuera 7 plantillas que sí funcionan |
| 3 | Qué genera `--ai` (`.mcp.json`, `AGENTS.md`, `CLAUDE.md`, `.claude/settings.local.json`) | ✅ | `07/13 §3` y `07/14 §3` (contenido literal, verificado en vivo) | — |
| 4 | Qué genera `--actions` (workflows CI) | ✅ | `07/13 §3` y `§11` | — |
| 5 | `--toolchain` para fijar el runtime | ✅ | `07/13 §4` | — |
| 6 | `gm-mcp-setup` para un proyecto existente sin `.mcp.json` | ✅ | Script instalado, leído en esta auditoría: engancha `.mcp.json` y `opencode.json` por proyecto; `AGENTS.md` §0 lo referencia | — |
| 7 | El MCP es por proyecto: fuera de un `.yyp` se cierra al arrancar | ✅ | `gm-mcp-setup` (comentario propio del script) + `AGENTS.md` intro | — |

### B · Crear y editar recursos sin tocar `.yy`/`.yyp` (17)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 8 | Sintaxis general `resource create type=X name=Y` | ✅ | `07/13 §6` (receta completa ejecutada) | — |
| 9 | Crear objeto / script / sprite / sonido | ✅ | `07/13 §6` (`resource create`, `sprite addframe`, `sound setfile`) — reejecutado y confirmado | — |
| 10 | **Asignar un sprite a un objeto** | 🔴 | `07/13` solo cita `RESOURCE SET \| EXPR / VALUE` en la tabla, sin ejemplo | **Verificado en vivo**: `resource set expr=obj_player.spriteId value=spr_player`. El campo se llama `spriteId` (confirmado con `resource info expr=obj_player keys`), no `sprite_index` ni `sprite` |
| 11 | Asignar la máscara de colisión de un objeto | 🟡 | Mismo mecanismo que #10, no probado literalmente | Por analogía directa con `spriteId` (mismo tipo de campo `sprite`): `resource set expr=<obj>.spriteMaskId value=<spr>`. Sin verificar en vivo — marcar como inferido si se documenta |
| 12 | **Asignar el padre de herencia de un objeto (`parentObjectId`)** | 🔴 | Ninguno. La tabla de `07/13` sugiere que se hace con `resource create ... parent=X` | **Falso y peligroso, verificado en vivo**: `resource create type=object name=X parent=obj_padre` **falla** (`Failed to add resource '...' to project`, exit 1) — `parent=` en `RESOURCE CREATE` es para la **carpeta del Asset Browser** (`folder=` hace lo mismo), no para la jerarquía de objetos. El padre real se fija **después de crear ambos objetos** con `resource set expr=obj_hijo.parentObjectId value=obj_padre` (verificado, `.yy` resultante correcto) |
| 13 | Mover/crear instancias en una room | ✅ | `07/13 §6` (`room instance create room=Room1 object=obj_player layer=Instances x=100 y=200`) | — |
| 14 | Capas de room y sus tipos (mayúsculas) | ✅ | `07/13 §6` (`room layer create`, aviso de que `type=instances` en minúscula falla) | — |
| 15 | Tipos de recurso que **no** se pueden crear (Extension) | ✅ | `AGENTS.md §4` + `07/22` (verificado 2026-09-06, no reabrir) | — |
| 16 | `resource delete` | ✅ | Verificado en vivo: borra el recurso y su carpeta, mensaje `deleted resource folder: ... :True` | — |
| 17 | **Fiabilidad de `gm-cli resourcetool eval` bajo el sandbox del Bash tool** | 🔴 | Ninguna mención en la biblioteca | Ver «Huecos» #2. El mismo comando, repetido en el mismo proyecto, cuelga indefinidamente o responde en 15 s de forma no determinista, siempre por la capa `npm exec` interna — nunca por `ResourceTool` en sí |
| 18 | Cómo saltarse el cuelgue: invocar el binario `ResourceTool`/`ProjectTool` cacheado directamente | 🔴 | Ninguna | Receta verificada en «Encargo» #2 |
| 19 | **Colisión de números de evento `draw gui_begin`/`gui_end`** | 🔴 | Ninguna | Bug de `ResourceTool@2026.0.17` verificado byte a byte (ver «Huecos» #3) |
| 20 | **Colisión `other room_end` ↔ `game_end`** | 🔴 | Ninguna | Verificado en vivo; el número correcto (5) existe en código real descargado (`gml-raptor/RoomController.yy`) pero `resourcetool` asigna 3, el mismo que `game_end` |
| 21 | Colisión `other broadcast_message` ↔ `boundary` | 🟡 | Ninguna | Verificada la colisión (ambos → `Other_1.gml`); no verificado cuál es el número «correcto» real por ser un evento poco documentado — marcar como hallazgo sin resolver |
| 22 | `object event types`: listado autoritativo completo | ✅ (nuevo, propio) | Capturado en vivo, íntegro (14 tipos, ~90 subtipos con nombre) | Ningún documento propio lo reproduce; solo aparece un fragmento (create/step/draw/mouse) en `07/13 §6` |
| 23 | **Eventos Async (HTTP, Save/Load, Steam, Cloud, Networking…) no se pueden crear con `resourcetool`** | 🔴 | Ninguna | Verificado: `object event types` no lista ningún tipo `async`; forzar `type=other subtype=<número real>` (probado con 62) es **rechazado** (`Invalid subtype`, whitelist cerrada). Un agente **no puede** crear estos eventos por CLI/MCP: debe pedir al humano que los cree desde el IDE, o editar el `.gml` de uno que ya exista en la plantilla |
| 24 | Tipos válidos de `room layer create` (`INSTANCE\|ASSET\|BACKGROUND\|PATH\|TILE\|EFFECTS`) | ✅ | `07/13 §6` | — |

### C · El MCP `gamemaker-resource-tool` (5)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 25 | **Inventario exacto de las herramientas que expone el MCP** | 🔴 | `07/13 §6` da el inventario de comandos de `eval`, no de MCP; `07/14` describe el MCP en general sin listar herramientas | **Verificado en vivo con introspección directa del protocolo** (`initialize` + `tools/list` por stdio): **80 herramientas**, listado completo en «Encargo» #4 |
| 26 | Diferencias MCP vs `resourcetool eval` | 🔴 | `07/14 línea 484` dice solo «crear y editar recursos» sin detalle | **Verificado**: el MCP **no expone** `defaults_get`/`defaults_set`, ni forma de fijar la ruta de un `.gml` de script o evento (`gml_setgmlfile`, `object_event_setgmlfile` no existen como tools — solo hay `gml_getgmlfilepath`, de solo lectura), ni `shader_setfilepath`/`note_setfilepath` (solo sus versiones `_getfilepath`). Para esas cuatro operaciones un agente con MCP **debe** caer a `resourcetool eval` |
| 27 | Qué pasa si el MCP no está en la sesión | ✅ | `AGENTS.md §2` + skill: cae a `resourcetool eval`, funcionalmente equivalente salvo #26 | — |
| 28 | `.claude/settings.local.json` generado (permisos) | ✅ | `07/14 §3.3` (contenido literal) | — |
| 29 | Formato del protocolo (Content-Length vs JSON por línea) | ✅ (nuevo, propio) | Verificado en vivo: el servidor usa **JSON delimitado por salto de línea**, no el framing `Content-Length` de LSP | No documentado en ningún sitio, pero es un detalle de implementación de MCP genérico, no específico de GameMaker — solo importa si alguien reimplementa un cliente a mano |

### D · Escribir el GML: dónde y con qué nombre exacto (13)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 30 | Ruta de un script (`scripts/<nombre>/<nombre>.gml`) | ✅ | `07/13 §6` | — |
| 31 | Ruta de un evento (`objects/<nombre>/<Evento>_<N>.gml`) | ✅ | `07/13 §6` (Create_0.gml, Step_0.gml) | — |
| 32 | Create/Destroy/CleanUp → sufijo `_0` | ✅ | Verificado en vivo, coincide con lo poco que dice `07/13` | — |
| 33 | Alarm 0-11 → `Alarm_N.gml` directo | ✅ | Verificado en vivo (`Alarm_0.gml`…`Alarm_5.gml`); trivial y sin trampa | — |
| 34 | Step: normal=0, begin=1, end=2 | ✅ (nuevo) | Verificado en vivo | No estaba en ningún documento, solo el ejemplo de `step_normal` |
| 35 | **Draw: tabla completa de números** | 🔴 | Solo `Draw_0` (normal) aparece, de pasada, en `07/18` | **Verificado en vivo y contrastado con código real** (`OpenGM` test project + `gml-raptor`): `draw_normal=0, gui=64, draw_resize=65, draw_begin=72, draw_end=73, gui_begin=74*, gui_end=75*, draw_pre=76, draw_post=77` (*= el número real; `resourcetool` da 72/73 por el bug #19) |
| 36 | **Other: tabla completa de números** | 🔴 | Ninguna | Verificado en vivo: `outside=0, boundary=1, game_start=2, game_end=3, room_start=4, room_end=5*, animation_end=7, end_of_path=8, user0=10, outside_view0=40, boundary_view0=50, animation_update=58, animation_event=59` (*=real; `resourcetool` da 3 por el bug #20). `user1`-`user15` **no aceptados** por `resourcetool` pese a existir en GameMaker real (whitelist cerrada a `user0`) |
| 37 | Keyboard/KeyPress/KeyRelease: sufijo = código de tecla | ✅ | `07/13 §6` (menciona «código de tecla» genéricamente) | El código exacto (`vk_space`=32, verificado) no está tabulado, pero el patrón general sí está explicado y es suficiente |
| 38 | Mouse: sufijo por acción | ✅ | `07/13 §6` (tabla completa de subtipos con nombre, ya verificada por r3) | — |
| 39 | Collision: nombre de archivo incluye el objeto colisionado | ✅ | Deducible del propio `object event types` (`collisionobject=` como argumento obligatorio) | — |
| 40 | **Cómo saber el número correcto sin adivinar** | 🔴 | Ninguna receta explícita | Encargo: usar SIEMPRE `object event list name=<obj>` tras crear el evento, o leer el `.yy` directamente, en vez de memorizar/adivinar el número — es la única forma fiable dado el bug #19/#20 |
| 41 | Gesture: subtipos completos (tap, pinch, rotate, flick…) | ✅ | `object event types` los lista todos; `01/12 §8bis` ya cubre gestos táctiles a nivel de concepto | — |
| 42 | Trigger event | 🟡 | Aparece en `object event types` pero no en ningún documento propio con explicación de uso | Menor: es GML Visual/legacy, poco relevante para código a mano |

### E · Compilar y leer los errores (9)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 43 | `gm-cli compile` / `--errors-only` / exit codes | ✅ | `13/10` líneas 1226-1249 + `07/13 §4` (ya verificado por r3, reconfirmado en esta auditoría) | — |
| 44 | Formato de un error de sintaxis real | ✅ (nuevo, propio) | Verificado en vivo: `gml_Object_<obj>_<Evento>(<línea>) : <mensaje>` (p. ej. `got '{' expected ')'`) | No documentado como formato general en ningún sitio, aunque es autoexplicativo una vez visto |
| 45 | **Salida JSON `{"errors":[...]}` al final de un `compile` fallido** | 🔴 | Ninguna | Verificado en vivo: además del log en texto, `gm-cli compile` imprime un bloque `{"errors":[{"source":"AssetCompiler","message":"..."}]}` — parseable programáticamente, mejor que hacer *grep* del texto bonito con bordes `│` |
| 46 | **El compilador NO detecta una función inventada ni una variable no declarada** | 🔴 | Ninguna explicación de *por qué* `validar-proyecto.py` es necesario y no redundante con `compile` | **Verificado en vivo, contraste directo**: `funcion_que_no_existe()` compila con exit 0 y solo falla en tiempo de ejecución (`Variable ....funcion_que_no_existe(...) not set before reading it`); el mismo código, pasado por `validar-proyecto.py`, se detecta al instante (`✗ 1 funciones INVENTADAS`) |
| 47 | **Un `constructor` con padre no definido (`: Padre() constructor`) crashea el `AssetCompiler` entero sin ningún mensaje útil** | 🟡 | **Ya vive en `_indice/PENDIENTE-r3.md`**, un documento interno de seguimiento de auditorías que un agente normal **no lee nunca** | **Reproducido en vivo**: el error se reduce a `AssetCompiler exited with non-zero status (1)` repetido tres veces, sin línea ni mensaje. Encargo: promover este hallazgo de `PENDIENTE-r3.md` a `13/10` (interpretación de errores), que sí está en el camino de lectura normal |
| 48 | Recursos no usados: listados y eliminados del build (no del proyecto) | ✅ (nuevo, propio) | Verificado: `NOTE: N Unused Assets found (and will be removed)` — no borra nada del proyecto fuente, solo del `.win` compilado | No documentado, pero es información tranquilizadora más que un problema |
| 49 | `gm-cli run` no propaga el exit code del juego (salida normal) | ✅ | `13/10 §3.4-3.5` + `07/13 §4` (ya verificado por r3; reconfirmado con `game_end(7)` → exit 0 del propio proceso) | — |
| 50 | **`gm-cli run` tampoco propaga nada cuando el juego CRASHEA, y deja un proceso huérfano** | 🔴 | Ninguna | Verificado en vivo: un error no controlado no termina el proceso de `gm-cli run` (hay que matarlo con timeout), y dos ejecuciones sucesivas dejaron **dos procesos `Mac_Runner` huérfanos** corriendo tras matar el `gm-cli run` padre. Un agente que no limpie explícitamente por nombre de proceso acumula juegos zombis |
| 51 | El validador de compilación de docs (`validar-compilacion-docs.py`) como fuente de trampas del motor | ✅ | `_indice/PENDIENTE-r3.md` («Trampas del motor descubiertas al compilar»: notación científica, ternario anidado, `const` inexistente…) | Mismo problema que #47: vive en un documento que el flujo normal de un agente no visita |

### F · Ejecutar y depurar sin ver la pantalla (7)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 52 | `show_debug_message` se captura en el stdout de `gm-cli run` | ✅ | `13/06 §3.14` + `13/10 §7.2` (ya documentado; reconfirmado en vivo, aparece literal en el log prefijado con `│`) | — |
| 53 | Marcador `###game_end###N` como fin de partida controlado | ✅ | `13/10 §3.4` (ya documentado por r3; reconfirmado) | — |
| 54 | Qué NO puede comprobar un agente por sí solo (debe pedírselo al humano) | 🟡 | Disperso: `05/02 §6` habla de vacíos de info de consolas; nada reúne la lista completa | Encargo: reunir en una lista explícita — renderizado visual real, sonido, input táctil/gamepad físico, rendimiento en dispositivo real, certificación de plataforma, sensación/*feel* subjetiva |
| 55 | Capturas de pantalla automatizadas desde dentro del juego | ✅ | `13/11 §4.7` + `13/10 §7.3` (ya verificado por r3) | — |
| 56 | Grabación de vídeo desde el juego | ✅ (como «no genérico») | `r3-herramientas-pipeline.md #66` ya lo marcó: solo existe para Opera GX/GXC | — |
| 57 | Pruebas automatizadas: mini-framework GML | ✅ | `13/10 §3` (ya documentado extensamente por r3/ingenieria) | — |
| 58 | Depuración remota / en dispositivo real | 🟡 | `r3-herramientas-pipeline.md #16` ya lo marcó parcial | No reabrir; ya evaluado |

### G · Assets sin artista (4)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 59 | **Generar un PNG plano por código e importarlo** | 🔴 | Ninguna receta propia | Verificado en vivo: `magick -size 64x64 xc:"#ff3366" spr.png` (o Python+PIL) → `resource create type=sprite name=spr_x` → `sprite addframe name=spr_x path=spr.png`. Funciona sin errores, tamaño del sprite toma el del PNG |
| 60 | **Generar un WAV por código e importarlo** | 🔴 | Ninguna receta propia | Verificado en vivo: módulo `wave` de Python (tono senoidal, sin dependencias) → `resource create type=sound name=snd_x` → `sound setfile name=snd_x path=snd.wav`. Funciona sin errores |
| 61 | Marcadores de posición dibujados por GML puro (sin sprite) | ✅ | `13/02` y varias recetas usan `draw_rectangle`/`draw_circle` como placeholder habitual | — |
| 62 | Política de «genera tú los recursos, no dependas de terceros» | ✅ | Cubierto por la skill hermana `gamedev-self-generated-assets` (fuera de esta biblioteca pero coherente con ella) y por `07/09` (Asset packs libres) | — |

### H · El ciclo completo y errores típicos de un LLM (4)

| # | Tema | Veredicto | Evidencia | Qué falta |
|---|---|---|---|---|
| 63 | El ciclo idea→proyecto→recursos→código→compilar→corregir→ejecutar→iterar, documentado de punta a punta | ✅ | `AGENTS.md §5` + SKILL.md «Flujo para un desarrollo real» | Los cuatro atascos de este informe (huecos 1-4) ocurren dentro de este ciclo ya documentado, no fuera de él |
| 64 | Aritmética con IDs de asset (`sprite_index + 1`) | ✅ | `AGENTS.md §4` (ya cubierto, no reabrir) | — |
| 65 | Nombres reservados (`x`, `y`, `speed`, `id`…) | ✅ | `AGENTS.md §5` + `05/04` (ya cubierto) | — |
| 66 | Patrones de otro motor que no aplican en GML (Unity `Update()`, Godot `_ready()`, `this.`) | 🟡 | Cubierto de forma dispersa en varios documentos de fundamentos, sin una lista dedicada a «falsos amigos entre motores» | Menor: no bloquea a un agente que ya sigue `01 - Fundamentos/` |

## Huecos por prioridad

### 🔴 Graves

1. **9 de las 18 plantillas de `gm-cli init` fallan hoy en macOS con `gm-cli` 2.3.0** (#2), y la
   biblioteca no lo dice con esa precisión. Tabla completa, verificada en vivo hoy:

   | Plantilla | Resultado |
   |---|---|
   | Space Rocks | ✅ funciona |
   | Blank Pixel Game | ✅ funciona |
   | Scrolling Shooter Game Template | ✅ funciona |
   | Tower Defense Template | ✅ funciona |
   | Survivor Game Template | ✅ funciona |
   | Brick Breaker Template | ✅ funciona |
   | Puzzle Slider Template | ✅ funciona |
   | Fire Jump Template | ✅ funciona |
   | RPG Starter Pack | ✅ funciona |
   | Platformer Template | 🔴 `PREFABS RESTORE exited with code 1` |
   | Arcade Action Game Template | 🔴 igual |
   | Twin Stick Shooter Template | 🔴 igual |
   | Endless Runner Template | 🔴 igual |
   | Idle Game Template | 🔴 igual |
   | Match 3 Template | 🔴 igual |
   | Card Game Template | 🔴 igual |
   | Cover Assault | 🔴 igual |
   | Hero's Trail Base - GML Visual | ⚠️ `Template not found` — ni con el nombre completo ni con «Hero» como coincidencia parcial; puede haberse retirado del catálogo de YoYo desde que se documentó |

2. **`gm-cli resourcetool eval` (y por extensión el MCP, que usa la misma capa) cuelga sin avisar
   bajo el sandbox por defecto del Bash tool de Claude Code** (#17). Reproducido de forma
   controlada: el mismo comando (`resource types`) sobre el mismo proyecto, repetido tres veces
   seguidas, dio *hang* (>20 s, subiendo a >100 s sin resolver), éxito en 15 s, y *hang* otra vez.
   La causa raíz, aislada con `ps -ef` mientras colgaba: el proceso real es
   `npm exec @gm-tools/resource-tool-osx-arm64@latest ...`, y **el binario `ResourceTool` que ese
   `npm exec` acaba lanzando responde en 0,3 s si se invoca directamente**, con el paquete ya
   cacheado en `~/.npm/_npx/`. Con `dangerouslyDisableSandbox: true` en el Bash tool, el mismo
   comando no ha vuelto a colgarse ni una vez en decenas de invocaciones. `gm-cli compile` tiene
   el mismo problema con la descarga de Igor (`Failed to download Igor: fetch failed` bajo
   sandbox; funciona a la primera sin él). Esto no es una carencia de GameMaker: es información
   operativa que un agente de Claude Code **necesita antes de tocar el CLI**, y hoy no está en
   ningún sitio de la biblioteca.

3. **Bugs de numeración de eventos en `ResourceTool@2026.0.17` que crean el evento equivocado sin
   error** (#19, #20). Verificado con evidencia doble (el `.yy` resultante y código real
   descargado que usa los números correctos):
   - `object event findorcreate type=draw subtype=gui_begin` crea `eventNum:72,eventType:8`
     — el mismo número que `draw_begin`. El número real de GUI Begin es 74 (confirmado en
     `OpenGM/.../testobj.yy`, que enumera los ocho eventos de dibujo con sus ocho números reales).
   - `subtype=gui_end` → mismo problema con 73 en vez de 75.
   - `type=other subtype=room_end` → crea `Other_3.gml`, el mismo archivo que `game_end`. El
     número real (5) existe en un objeto de producción real (`gml-raptor/RoomController.yy`).
   - Consecuencia práctica: si un agente pide «Draw Begin» y luego «GUI Begin» en el mismo objeto,
     el segundo `findorcreate` **encuentra el archivo del primero** («Existing GML file») en vez
     de crear uno nuevo — los dos eventos, semánticamente distintos (coordenadas de mundo vs.
     coordenadas de pantalla), acaban compartiendo el mismo código sin ningún aviso.

4. **El compilador no detecta funciones inventadas ni variables no declaradas — solo
   `validar-proyecto.py` lo hace, y en ningún sitio se explica por qué ese paso no es
   opcional** (#46). Un agente que interprete «`gm-cli compile` salió con exit 0» como «mi GML es
   correcto» está equivocado: `funcion_que_no_existe(5, "hola")` compila limpio y solo revienta en
   tiempo de ejecución con `Variable ...funcion_que_no_existe(...) not set before reading it` — un
   mensaje que ni siquiera nombra el problema real (dice «variable», no «función inexistente»).

### 🟠 Medios

- **Un `constructor` con padre no definido crashea el `AssetCompiler` entero sin mensaje útil**
  (#47): ya está descubierto y descrito con precisión, pero solo en `_indice/PENDIENTE-r3.md`, un
  documento de seguimiento interno de auditorías que ningún agente lee en su flujo de trabajo
  normal. Es del calibre de un hallazgo que debería vivir en `13/10`.
- **Asignar el padre de herencia de un objeto por `resourcetool` no es lo que la tabla de
  comandos sugiere** (#12): `resource create ... parent=X` falla para objetos (ese `parent=` es
  para la carpeta del Asset Browser); el mecanismo real es `resource set
  expr=<hijo>.parentObjectId value=<padre>` después de crear ambos objetos por separado.
- **`gm-cli run` deja procesos `Mac_Runner` huérfanos cuando el juego crashea** (#50): un agente
  que solo pone un timeout al comando y no mata el proceso hijo por nombre acumula juegos zombis
  en cada iteración de depuración.
- **El inventario de las 80 herramientas del MCP no existe en ningún documento** (#25, #26): la
  biblioteca describe el MCP en general pero nunca lista sus *tools*, ni explica que hay
  operaciones (fijar el `.gml` que respalda un evento o script, fijar la ruta de un shader/nota,
  `defaults`) que solo están disponibles por `eval`, no por MCP.
- **Los eventos Async no se pueden crear con `resourcetool`** (#23): ni por nombre ni forzando el
  número real como `subtype`. Un agente que necesite un evento Async - HTTP/Save-Load/Steam debe
  saber que tiene que pedírselo al humano (o reutilizar uno ya presente en la plantilla).

### 🟡 Menores

- Tabla de eventos Draw/Other/Step por número (#34-#36): ahora está en este informe, pendiente de
  trasladar a la biblioteca — ver Encargo #3.
- `broadcast_message` colisiona con `boundary` pero no se ha podido confirmar el número «correcto»
  real (#21): evento poco documentado incluso fuera de esta biblioteca.
- Máscara de colisión de objeto (#11): inferido por analogía con `spriteId`, no verificado
  literalmente — cerrar en la próxima ronda con una comprobación de 30 segundos.
- La plantilla «Hero's Trail Base - GML Visual» no se encuentra ni por nombre completo ni por
  coincidencia parcial: puede haberse retirado del catálogo de 31 plantillas desde que `07/06` lo
  documentó (31-ago-2026); revisar contra la API oficial en la próxima ronda.
- Falta un documento único que reúna «qué NO puede comprobar un agente solo y debe preguntar al
  humano» (#54): hoy la información existe dispersa.
- Formato JSON `{"errors":[...]}` de `gm-cli compile` (#45): útil de documentar pero no bloquea a
  nadie — la salida en texto ya es suficiente para un agente que hace *grep*.

## Encargo para el redactor

1. **Corregir `07/06 §4`** («Incidencia encontrada al probar») con la tabla completa de las 18
   plantillas verificadas hoy en `gm-cli` 2.3.0 (sección «Huecos» #1 de este informe, cita y
   pega la tabla). Sustituir la recomendación «usa Space Rocks o Blank Pixel Game» por «usa
   cualquiera de estas 9: Space Rocks, Blank Pixel Game, Scrolling Shooter Game Template, Tower
   Defense Template, Survivor Game Template, Brick Breaker Template, Puzzle Slider Template, Fire
   Jump Template, RPG Starter Pack». Aclarar que actualizar a 2.3.0 **no** arregla el fallo de
   `PREFABS RESTORE` (ya está instalada esa versión y el fallo persiste) — quitar esa frase como
   solución. Sin símbolos GML: es tooling del CLI.

2. **Nueva nota en `07/13` (junto a §6, antes de la receta) y en `AGENTS.md §2.bis`, sobre la
   fiabilidad de `resourcetool eval`/`compile`/`run` bajo sandbox de red**: explicar que estos
   comandos descargan/verifican paquetes npm (`@gm-tools/resource-tool-osx-arm64`,
   `@gm-tools/project-tool-osx-arm64`, Igor) incluso con caché local, y que bajo un sandbox de red
   restringido (como el Bash tool de Claude Code en modo por defecto) pueden colgarse
   indefinidamente o fallar con `fetch failed`/`Failed to download Igor`. Dar la receta de
   emergencia verificada: localizar el binario ya cacheado
   (`find ~/.npm/_npx -path "*/resource-tool-<plataforma>/Contents/MacOS/ResourceTool"`) e
   invocarlo directamente con `projectpath=`, `projecttool=` y `prefabsfolder=` como argumentos
   (mismo formato `key=value` que usa `resourcetool` internamente) para saltarse la capa `npm
   exec` cuando haga falta velocidad o fiabilidad. Sin símbolos GML: es infraestructura del CLI.

3. **Ampliar `07/13 §6`** con la tabla completa de números de evento verificados en esta auditoría
   (Alarm, Step, Draw, Other), y con un aviso explícito y destacado sobre los bugs de colisión:
   `gui_begin`/`gui_end` (dan 72/73 en vez de 74/75, colisionando con `draw_begin`/`draw_end`) y
   `other subtype=room_end` (da 3, el mismo que `game_end`, en vez de 5). Recomendar como práctica
   obligatoria: tras cualquier `object event findorcreate`, comprobar con
   `object event list name=<obj>` o leyendo el `.yy` que el evento creado es el que se pidió,
   nunca fiarse del nombre del subtipo a ciegas. Documentar también que los eventos Async no se
   pueden crear por `resourcetool` (ni por nombre ni por número), con la whitelist exacta
   verificada de `other`: `outside, boundary, outside_view0, boundary_view0, game_start, game_end,
   room_start, room_end, animation_end, animation_update, animation_event, end_of_path, user0,
   broadcast_message` — nada más se acepta, ni siquiera `user1`-`user15`.

4. **Nueva sección en `07/14`** (o ampliar §5) con el inventario completo de las 80 herramientas
   MCP de `gamemaker-resource-tool` (verificado por introspección directa del protocolo,
   `initialize`+`tools/list`): `status, help, helptable, global_arguments, resource_set,
   resource_info, resource_create, resource_delete, resource_list, resource_types,
   project_rename, object_event_findorcreate, object_event_delete, object_event_change,
   object_event_list, object_event_types, room_instance_create, room_asset_create,
   room_item_list, room_item_delete, room_layer_create, room_layer_delete, room_layer_list,
   room_layer_tiles_get, room_layer_tiles_set, room_layer_tiles_list, room_layer_tiles_resize,
   room_layer_tiles_info, room_list, gml_getgmlfilepath, sprite_addframe, sprite_deleteframe,
   sound_setfile, tileset_create, tileset_delete, tileset_rename, tileset_setsprite,
   config_list, config_usages, config_create, config_delete, config_rename, config_getactive,
   config_setactive, audiogroup_create, audiogroup_delete, audiogroup_rename, audiogroup_list,
   audiogroup_usages, audiogroup_set, texturegroup_create, texturegroup_delete,
   texturegroup_rename, texturegroup_list, texturegroup_usages, texturegroup_set, prefab_list,
   prefab_info, prefab_addreference, prefab_removereference, prefab_customise,
   shader_getfilepath, note_getfilepath, path_addpoint, path_info, path_deletepoint,
   font_rangelist, font_addrange, font_removerange, font_kerninglist, font_addkerning,
   font_removekerning, font_glyphlist, font_setfile, folder_list, folder_create, options_list,
   options_get, options_info, options_set`. Añadir el aviso de que **no** existen (a diferencia de
   `resourcetool eval`) `defaults_get`/`defaults_set`, `gml_setgmlfile`,
   `object_event_setgmlfile`, `shader_setfilepath` ni `note_setfilepath`: para esas cinco
   operaciones un agente con el MCP conectado debe caer a `resourcetool eval` igualmente.

5. **Promover el hallazgo de `_indice/PENDIENTE-r3.md`** («un constructor con padre no definido
   crashea el AssetCompiler entero») a `13/10` (interpretación de errores del compilador), con el
   ejemplo mínimo reproducible (`function Hijo() : PadreQueNoExiste() constructor {}`) y la salida
   exacta que da (`AssetCompiler exited with non-zero status (1)` repetido, sin línea ni mensaje).
   Añadir junto a él el resto de «Trampas del motor descubiertas al compilar» que ya vive en ese
   mismo `PENDIENTE-r3.md` (notación científica trocea el identificador, ternario anidado necesita
   paréntesis, `const` no existe) — todo ya verificado, solo falta moverlo al documento que un
   agente sí lee. En la misma sección, añadir el ejemplo del error de sintaxis normal
   (`gml_Object_<obj>_<Evento>(<línea>) : <mensaje>`) y mencionar que `gm-cli compile` también
   imprime un bloque `{"errors":[{"source":"AssetCompiler","message":"..."}]}` parseable al final
   de una compilación fallida.

6. **Nueva sección corta en `13/10`** (junto a lo ya escrito sobre `gm-cli run` y el exit code):
   un párrafo sobre que un juego que crashea con un error no controlado **no** hace que
   `gm-cli run` termine por sí solo — el proceso queda abierto (en macOS, un `Mac_Runner`
   huérfano) y hay que envolver la llamada con un timeout y matar el proceso hijo explícitamente
   por nombre tras cada ejecución de depuración automatizada, o los procesos se acumulan.

7. **Explicar por qué `validar-proyecto.py` no es opcional**, en la propia entrada de
   `AGENTS.md §5.4` o en `13/10`: una frase que diga que GML resuelve nombres de función de forma
   dinámica y que llamar a una función que no existe **no es un error de compilación**, solo de
   ejecución (`Variable X.funcion(...) not set before reading it`), con el ejemplo mínimo ya
   verificado en esta auditoría. Sin este matiz, un agente que solo mira el exit code de
   `gm-cli compile` da por buena una función inventada.

8. **Sección nueva o ampliación en `12 - Utilidades e integraciones/05 - Pipeline de arte, audio y
   niveles.md`: «Placeholders sin artista, generados por CLI»**: receta verificada de PNG
   (`magick -size 64x64 xc:"#ff3366" spr.png`, o Python + PIL, sin dependencias de red) y WAV
   (módulo `wave` de Python, tono senoidal, sin dependencias) seguida de la importación real con
   `resourcetool` (`resource create type=sprite name=spr_x` → `sprite addframe name=spr_x
   path=spr.png`; `resource create type=sound name=snd_x` → `sound setfile name=snd_x
   path=snd.wav`), ambas verificadas en vivo sin errores.

9. **Corregir `07/13 §6`** (tabla `RESOURCE CREATE`) con un aviso: `parent=` en `resource create`
   sirve para la carpeta del Asset Browser (equivalente a `folder=`), **no** para la herencia de
   objetos — verificado que `resource create type=object name=X parent=obj_padre` falla con
   `Failed to add resource '...' to project`. El padre de herencia real se fija después, con
   `resource set expr=<hijo>.parentObjectId value=<padre>`.

## Lo que comprobé y NO hacía falta

- **El ciclo documentado en `AGENTS.md §5` y en la skill `gamemaker-biblioteca`** (proyecto →
  recursos → GML → compilar → corregir → ejecutar): es correcto en su secuencia y en el orden de
  autoridad de las fuentes. No hace falta reescribirlo, solo rellenar los huecos de detalle que
  lista este informe dentro de cada paso.
- **`resource create`, `sprite addframe`, `sound setfile`, `room instance create`, `room layer
  create` para los casos ya documentados en `07/13 §6`**: reejecutados literalmente y funcionan
  exactamente como dice el documento. No reabrir esa parte.
- **`gm-cli run` no propaga el exit code del juego en una salida limpia** (`13/10 §3.4-3.5`,
  `r3-herramientas-pipeline.md #22`): reconfirmado con un `game_end(7)` explícito — el proceso de
  `gm-cli run` sale con 0 pase lo que pase dentro del juego. No es un hallazgo nuevo, solo una
  reconfirmación con un caso más concreto que el ya documentado.
- **El asset Extensión no se puede crear con `resourcetool`** (`AGENTS.md §4`, verificado
  2026-09-06): no reabierto, sigue siendo cierto y no tenía por qué volver a probarlo.
- **El andamiaje de `gm-cli init --ai`** (`.mcp.json`, `AGENTS.md`, `CLAUDE.md`,
  `.claude/settings.local.json`): reproducido en vivo, coincide byte a byte con lo que documenta
  `07/13 §3` y `07/14 §3`.
- **La captura de `show_debug_message` y del marcador `###game_end###N` en el stdout de
  `gm-cli run`**: ya documentada por r3/ingenieria, reconfirmada sin sorpresas.
- **Mouse, Keyboard, KeyPress, KeyRelease y Gesture como categorías de evento**: el `object event
  types` capturado en vivo coincide exactamente con lo que ya resume `07/13 §6`; el hueco real
  estaba en Draw y Other, no en estas.

## Lo que encontré desactualizado

- **`AGENTS.md §5.3` y `07/06`: «Las plantillas con prefabs fallan en `gm-cli` 2.3.0 en macOS.
  Usa Space Rocks o Blank Pixel Game»** — verificado el 2026-09-07 con `gm-cli` 2.3.0 instalado en
  este Mac (la misma versión que documenta la biblioteca): la afirmación es **cierta pero
  incompleta**, no desactualizada de raíz. De las 18 plantillas de juego, 9 fallan (incluida
  Platformer Template, la única que la biblioteca había probado) y 9 funcionan, siete de ellas con
  prefabs. La recomendación práctica («usa Space Rocks o Blank Pixel Game») deja fuera 7 opciones
  válidas sin necesidad. Fuente de la corrección: pruebas en vivo de las 18 plantillas,
  2026-09-07, en esta misma máquina.
- **`07/06 §4`: «Solución: actualiza a 2.3.0»** como remedio al error `PREFABS RESTORE exited with
  code 1` — verificado el 2026-09-07 que **no es una solución**: `gm-cli` 2.3.0 (la versión que la
  propia biblioteca recomienda instalar) reproduce el mismo error exacto en Platformer Template y
  en 7 plantillas más. La única salida real que sigue siendo válida es la otra mitad de la frase
  original: «si sigue fallando, crea el proyecto desde el IDE» o usar una de las 9 plantillas que
  sí funcionan.
