# 09 · Manual del agente de IA — operar GameMaker con `gm-cli`

> Este es el documento que usa un agente de IA cada vez que toca GameMaker de punta a punta:
> crear el proyecto, crear recursos, escribir GML, compilar, depurar y publicar sin abrir el
> IDE. No repite lo que ya explican [`07 · 13`](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md)
> (referencia completa del CLI) y [`07 · 14`](../07%20-%20Ecosistema/14%20-%20IA%20y%20GameMaker.md)
> (qué es el andamiaje `--ai` y cómo se prepara un proyecto para un agente): este documento
> añade **lo que ninguno de los dos cubre** — los trece sitios donde un agente se atasca hoy,
> el nombre exacto de archivo que le toca a cada evento, el inventario real de las 80
> herramientas del MCP, la frontera entre lo que un agente puede comprobar solo y lo que debe
> pedir al humano, los errores que un LLM comete por reflejo al tratar GML como si fuera C#
> de Unity o GDScript de Godot, y la raíz de expresión `project` — 18 miembros que abren
> configuraciones de build, grupos de audio/textura, archivos incluidos y metadatos del
> proyecto sin tocar el IDE.
>
> Todo lo verificado aquí se ejecutó **en vivo el 7 de septiembre de 2026**, en un proyecto de
> prueba bajo `~` (nunca dentro de esta biblioteca), borrado al terminar cada verificación,
> sobre GameMaker LTS 2026.0 (IDE `2026.0.0.16` · runtime `2026.0.0.23`) con `gm-cli` **2.3.0**
> — la misma versión que documenta el resto de la biblioteca. Reproduce la auditoría completa,
> con más temas y más detalle de investigación, en
> [`_indice/auditorias/r4-agente-ia-gamemaker.md`](../_indice/auditorias/r4-agente-ia-gamemaker.md).
>
> **Corrección del 8 de septiembre de 2026**: la sección 9 de este documento afirmaba que no
> existe ningún comando para el orden de las salas. Era falso — la raíz de expresión `project`
> (nunca antes documentada) lo resuelve directamente. Detalle completo en §9 y §9 bis.
>
> **Segunda corrección del 8 de septiembre de 2026**: este documento recomendaba
> `gm-cli compile --errors-only` para el ciclo normal del agente sin advertir de que ese mismo
> flag esconde por completo un fallo real — un *included file* creado por `resourcetool` cuyo
> archivo nunca llega al paquete compilado, y por separado, un *crash* del `AssetCompiler` que
> impide escribir el paquete. Nueva Trampa 8 en §0, nota en §1, §7.7 y checklist ampliado en §8.
>
> **Tercera corrección del 8 de septiembre de 2026**: una auditoría anti-alucinación encontró
> que este documento afirmaba, en tres sitios distintos, que crear un GUI Begin/End real, un
> evento Async (HTTP, Save/Load, Steam, Cloud, redes…) o `user1`-`user15` **no era posible por
> CLI ni MCP**. Era falso: `OBJECT EVENT FINDORCREATE` tiene la whitelist cerrada, pero el
> `eventNum` crudo del evento ya creado se puede forzar con `RESOURCE SET` — la misma raíz de
> expresión genérica que destapó la corrección de §9. Nueva Trampa 9 en §0, receta completa en
> §9 ter. La única afirmación de imposibilidad que se reverificó y se confirmó cierta fue la del
> asset **Extensión**, que sigue sin poder crearse por CLI/MCP.
>
> **Cuarta corrección del 8 de septiembre de 2026**: esa misma auditoría dejó 4 afirmaciones de
> imposibilidad sin verificar por depender, en apariencia, de un editor visual del IDE (presets
> de partículas, capas de UI del editor de rooms, troceado de sprites, GMRT). Esta sesión las
> cerró las 4: **dos se abren con un rodeo verificado** (un preset se puede replicar campo a
> campo leyendo el `.yy` que trae el propio toolchain instalado, y una tira de sprite se puede
> trocear con una herramienta de imagen externa y añadir fotograma a fotograma), **una se acota
> con precisión** (un Particle System solo admite un emitter completo por CLI, no varios), y
> **una resultó ser una limitación de máquina, no de herramienta** (el toolchain `GMRT@versión`
> ya es seleccionable desde `gm-cli compile`/`run` sin el IDE; lo que faltó en esta sesión fue
> el requisito de sistema **.NET 8**). Solo una limitación nueva se confirmó real y sin rodeo:
> las capas de UI del editor de rooms no tienen ninguna raíz de expresión que las alcance. De
> paso apareció una quinta: `OPTIONS SET` tiene una lista cerrada real de solo 5 propiedades
> escribibles por plataforma (de ~30), y esta vez no hay campo crudo que la esquive porque las
> opciones de plataforma no cuelgan del árbol de `RESOURCE`/`project`. Detalle completo, con
> comandos y salidas reales, en la nueva Trampa 10 de §0 y en §9 quater.
>
> **Quinta corrección del 8 de septiembre de 2026**: una prueba de regresión — construir un juego
> completo (*Empuja y Gana*, sokoban de tres niveles) volviendo a pisar cada arreglo de las
> correcciones anteriores — confirmó que los cinco aguantan el uso real sin excepción, pero dejó
> **cinco hallazgos nuevos**, documentados en
> [`_indice/auditorias/r6-regresion.md`](../_indice/auditorias/r6-regresion.md): (1) la receta de
> horneado de fuentes de la Trampa 5 necesitaba fijar también `%Name` y `parent: null`, no solo
> copiar el `.yy` de referencia — sin eso falla de tres formas distintas, ahora documentadas todas
> en la propia Trampa 5; (2) `resourcetool script` (el modo por lotes de §10) reporta éxito en
> cada línea pero **no persiste** un `RESOURCE SET` sobre `project.RoomOrderNodes` — reordenar
> salas exige `eval`, uno por índice, nunca lotes; nueva nota en §9.3 y excepción explícita en
> §10.4; (3) la auditoría observó una vez que `RESOURCE DELETE` de una sala **reinicia TODO**
> `project.RoomOrderNodes` al orden de creación — esta sesión intentó reproducirlo 6 veces más
> (permutación completa, borrando tanto `Room1` como salas propias, en distintas posiciones) y
> **no volvió a pasar ninguna vez**: parece intermitente, probablemente ligada a la misma
> condición de carrera del hallazgo (4), no un comportamiento garantizado — la regla práctica se
> mantiene igual de todos modos: reordena siempre después de borrar, nunca antes, y verifica el
> `.yyp` tras cualquier borrado — detalle y las dos tandas de evidencia en §9.3 bis; (4)
> `ResourceTool@2026.0.17` tiene un `AccessViolationException` nativo
> **no determinista**, incluso sobre un proyecto sano (2 de 5 llamadas idénticas fallaron) —
> promovido a la nueva **Trampa 11** de §0, con la mitigación (reintentar) también en el checklist
> de §8; (5) una
> instancia **sin `sprite_index` asignado no tiene máscara de colisión**, así que
> `instance_position()`/`place_meeting()` nunca la encuentran — no es un fallo de esta biblioteca
> sino de GML, documentado con detalle en
> [`01 · 08` §9](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md#9-errores-típicos),
> con una nota de aviso cruzada en el §5.2 de este documento.
>
> **Sexta corrección del 8 de septiembre de 2026**: una prueba de un juego para móvil
> (`_indice/auditorias/r7-prueba-movil.md`) confirmó en vivo, con captura de pantalla y
> hexdump de los bytes UTF-8 antes y después de compilar, un hallazgo serio para una biblioteca
> escrita entera en español: **la fuente por defecto de GameMaker (`draw_set_font(-1)`, o no
> fijar ninguna) no tiene glifos de `á é í ó ú ñ Ñ ¿ ¡` y los omite en silencio**, sin caja de
> «glifo no encontrado» ni aviso de ningún tipo — «¡Añádeme más peón!» se dibuja «Ademe ms
> pen!». No es un problema de codificación: los bytes UTF-8 llegan intactos hasta el juego
> compilado. Compila limpio y `validar-proyecto.py` no lo detecta — solo se ve mirando la
> pantalla. Nueva **Trampa 12** en §0, con la solución verificada de punta a punta (combina
> `font_add()` con la receta de *Included Files* de la Trampa 8): cross-referencias en
> [`08 · 03`](../08%20-%20Referencia%20GML%20completa/03%20-%20Texto%20y%20fuentes.md) y en el
> documento de dibujo de
> [`01 · 11`](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md#la-fuente-por-defecto-no-tiene-acentos-españoles).
>
> **Séptima corrección del 8 de septiembre de 2026**: una prueba de un juego de gestión
> (`_indice/auditorias/r7-prueba-gestion.md`) confirmó en vivo, comparando contra una captura
> de pantalla real de macOS (`screencapture`) tomada mientras el mismo fotograma se veía en la
> ventana del runner, que **`screen_save()` invierte la imagen verticalmente en el runner de
> Mac** — la ventana real se ve perfectamente, derecha; el PNG que produce `screen_save()` sale
> boca abajo y con el orden vertical invertido. Es relevante para cualquier agente que use
> `screen_save()` como canal de verificación (§4.1 de este documento, y el Procedimiento 1 de
> [`13 · 10` §8.6](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#86-compilar-limpio-no-es-lo-mismo-que-funcionar-el-fallo-silencioso-de-tiempo-de-ejecución)):
> **la captura automática puede mentir sobre la orientación mientras el juego real se ve bien**.
> Nueva **Trampa 13** en §0, con la mitigación (contrastar al menos una vez con
> `screencapture`) y la nota correspondiente en el guion de humo de `13 · 10` §8.7.

---

## 0 · Las quince trampas que hacen fracasar a un agente hoy

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

**Qué hacer, si te vale cualquier plantilla**: usa una de las 9 que funcionan.

```bash
# Bien — cualquiera de estas 9 crea el proyecto sin fallos:
gm-cli init --no-interactive -n mi-juego -t "Space Rocks" --ai --toolchain GMS2@2026.0.0.23
```

#### ❌ Corrección — «no hay ninguna solución por CLI» era falso

**Esta misma sección afirmaba que las 9 plantillas rotas no tenían arreglo fuera del IDE: «no es
un flag que falte, ni una versión que instalar».** Lo era. La causa raíz se aisló el 08-09-2026 y
hay **dos rodeos verificados de punta a punta**, uno de ellos sin IDE.

**La causa raíz no está en las plantillas.** Compilando con `--verbose` aparece la traza completa:

```
│  EXEC PACKAGE TOOL: find package="io.gamemaker.gm_filter_tintfilter" registry="http://gmpm.gamemaker.io"
│  PackageTool@2024.14.29
│  PackageTool failed because of an internal program error:
│  Parameter count mismatch.
│     at PackageTool.GmpmBindings.GetAvailablePackages(String registryUrl, …)
```

`PackageTool@2024.14.29` —la única versión publicada— **no puede consultar el registro de
paquetes en absoluto**: hay un desfase de firma entre él y el `gmpm.dll` que `gm-cli` descarga,
que es más nuevo (79 872 bytes frente a los 64 512 del que trae el IDE). Reproducido invocando el
binario directamente, fuera de `gm-cli`. Por eso falla **cualquier cosa que resuelva un paquete
del registro**: las 9 plantillas, los comandos `PREFAB`, y —efecto colateral— poner un filtro de
capa (`effectType`) en una sala.

**Rodeo A — sustituir el `gmpm.dll` por el del IDE.** Verificado de punta a punta el
09-09-2026, ejecutando cada paso. Son **cuatro**, y los dos últimos no estaban en la primera
versión de esta receta: sin ellos parece que el rodeo no funciona.

```bash
CACHE=~/.gmcli-cache
IDEDLL="$HOME/Library/Application Support/Steam/steamapps/common/GameMaker Studio 2/GameMaker.app/Contents/MacOS/arm64/gmpm/gmpm.dll"

# 1. Consigue una caché de herramientas poblada. Lo más rápido es COPIARLA de cualquier
#    proyecto que ya exista — la caché de herramientas es POR PROYECTO, vive en su .gmcache,
#    y así te ahorras la descarga entera (~167 MB):
cp -R <un-proyecto-cualquiera>/.gmcache "$CACHE"
#    (si no tienes ninguno: un `gm-cli init … --cache-dir "$CACHE"` que FALLE también la puebla)

# 2. Pisa el gmpm.dll roto (79 872 bytes) con el del IDE (64 512 bytes)
cp "$IDEDLL" "$(find "$CACHE" -name gmpm.dll | head -1)"

# 3. Crea el proyecto APUNTANDO A ESA CACHÉ
gm-cli init --no-interactive -n MiJuego -t "Platformer" --cache-dir "$CACHE"

# 4. Parchea también el .gmcache PROPIO que el proyecto acaba de crearse
cp "$IDEDLL" "$(find MiJuego/.gmcache -name gmpm.dll | head -1)"
```

Salida real del paso 3: `Project created at …/MiJuego`, con su `.yyp`. Y el proyecto **compila**
(`Igor complete` · `Compilation finished` · `exit 0`), con la lista real de objetos de la
plantilla (`obj_block_brick`, `obj_bridge`…).

> 🔴 **El paso 4 es el que falta en todas partes, y sin él parece que el rodeo no sirve.** El
> proyecto recién creado se hace **su propia** `.gmcache` con el `gmpm.dll` roto, así que
> cualquier comando posterior que no lleve `--cache-dir` vuelve a fallar:
>
> ```console
> $ gm-cli resourcetool eval "resource list type=object"      # sin el flag
> Failed to restore project. "ProjectTool PREFABS RESTORE" exited with code 1
>
> $ gm-cli resourcetool eval --cache-dir "$CACHE" "resource list type=object"   # con él
>  obj_block_brick …                                          # funciona
> ```
>
> Tienes dos salidas: **arrastrar `--cache-dir` en todos los comandos** del proyecto, o
> —mejor— **parchear una vez el `.gmcache` propio** (paso 4) y olvidarte del flag. Comprobado:
> tras el paso 4, `resourcetool` sin ningún flag lista los objetos sin problema.

**Rodeo B — llevarse la carpeta `.gmcache/prefabs` ya resuelta. Sin IDE, pensado para CI.** Una
vez que un proyecto resolvió sus prefabs, copiar esa carpeta a otro clon hace que cargue aunque
el `gmpm.dll` siga roto. Los *workflows* que genera `gm-cli init` ya cachean `.gmcache` con
`actions/cache@v5`, así que en CI basta con poblar la caché una vez desde una máquina sana.

**Y sin `init` en absoluto**: la API de plantillas da la URL de descarga de **las 31**, y el
`.yymps` es un ZIP normal con el `.yyp` dentro.

```bash
curl -s https://api.gamemaker.io/api/gamemaker/project-templates \
  | python3 -c "import json,sys;[print(t['attributes']['info_title'],'|',t['attributes']['gml_code_download_url']) for t in json.load(sys.stdin)['data']]"
curl -sL "https://api.yoyogames.com/api/2/download?package_id=com.yoyogames.windywoods&version=1.2.2" -o plataformer.yymps
unzip -q plataformer.yymps -d MiPlat
```

> ⚠️ **Lo que NO funciona**, para que nadie repita el camino: apuntar `prefabsfolder=` a la
> carpeta `packages/` del IDE, a `gm-ide-prefabs` o a un prefab concreto; copiar el `.yymps` a
> mano a `.gmcache/prefabs` o a `<proyecto>/prefabs`; y apuntar `projecttool=` al `ProjectTool`
> del IDE, solo o combinado con `prefabsfolder=`. Seis variantes, las seis
> `PREFABS RESTORE exited with code 1`.
>
> Y ese mensaje **es genérico**: significa «no se pudo cargar el proyecto», no necesariamente que
> falten prefabs. El diagnóstico real lo da `gm-cli compile --verbose`.

Contexto y matriz completa de plantillas en [`07 · 13` §12](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md#12-bug-conocido-las-plantillas-con-prefabs-fallan-al-crear-el-proyecto).

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


> 🔴 **Cuarto caso de la misma familia: `OBJECT EVENT CHANGE` deja el `.gml` huérfano.**
> Verificado el 08-09-2026. Cambiar un evento de Step normal a Step End actualiza el `.yy`
> (`eventNum:2`) y responde `Saved successfully`, pero **el archivo sigue llamándose
> `Step_0.gml`**:
>
> ```console
> $> OBJECT EVENT CHANGE NAME=obj_test TYPE=step SUBTYPE=step_normal NEWTYPE=step NEWSUBTYPE=step_end
> Saved successfully
> $ ls objects/obj_test/
> Create_0.gml  obj_test.yy  Step_0.gml      ← debería ser Step_2.gml
> ```
>
> `gm-cli compile` termina limpio y no avisa. **El código deja de ejecutarse, en silencio.**
> Renombra tú el archivo al número nuevo después de cualquier `OBJECT EVENT CHANGE` — es la misma
> disciplina que ya exige la Trampa 9 tras parchear un `eventNum`.

> 🔴 **Y el quinto caso: `OBJECT EVENT DELETE` deja el `.gml` en el disco.** Verificado el
> 09-09-2026:
>
> ```console
> $ ls objects/obj_t/
> obj_t.yy  Step_0.gml
> $> OBJECT EVENT DELETE NAME=obj_t TYPE=step SUBTYPE=step_normal
> Saved successfully
> $ grep -c eventNum objects/obj_t/obj_t.yy
> 0                       ← el evento SÍ desapareció del .yy
> $ ls objects/obj_t/
> obj_t.yy  Step_0.gml    ← el archivo sigue ahí
> ```
>
> Aquí el riesgo es el contrario al de `CHANGE`: no es que el código deje de ejecutarse, es que
> **queda un archivo huérfano que parece código vivo**. Quien lo lea después —tú mismo dentro de
> una hora, o el siguiente agente— creerá que ese Step existe. Bórralo a mano.
>
> **La regla que unifica los cinco casos de esta familia**: `resourcetool` mantiene el `.yy` y
> **nunca** los archivos `.gml`. Cada vez que un comando cambie qué eventos tiene un objeto,
> mira la carpeta con `ls` y cuadra los archivos con lo que dice `object event list`.

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

> ⚠️ **Variante nueva, misma familia: una `global.*` propia sin inicializar en el camino de
> ejecución de una sala concreta es invisible tanto al compilador como a `validar-proyecto.py`.**
> Verificado el 8 de septiembre de 2026 construyendo un *bullet heaven*
> (`_indice/auditorias/r8-prueba-masivo.md` §5.1): `validar-proyecto.py --todo` pasó limpio y aun
> así el juego reventó en tiempo de ejecución la primera vez que se cargó una sala distinta de la
> habitual —
> ```
> ERROR in action number 1
> global variable name 'pool_proyectiles' index (100246) not set before reading it.
> ```
> Causa: un objeto persistente leía `global.pool_proyectiles` sin condición, correcto en la sala
> donde otro objeto la crea, pero esa sala secundaria (un banco de pruebas propio) nunca la
> inicializaba. **Ni el compilador ni `validar-proyecto.py` lo cazan**: para el primero,
> `global.pool_proyectiles` es sintácticamente válido (esta misma Trampa 4); para el segundo,
> **solo verifica que los símbolos del runtime existan** ([§7](#7--interpretar-los-errores-del-compilador--lo-que-detecta-y-lo-que-no)) —
> nunca que una `global.*` propia esté garantizada en el camino de ejecución de cada sala, porque
> eso no es una llamada a función, es una variable. La corrección no es un mejor `is_undefined()`
> (evalúa el argumento antes de poder responder, y sobre una global nunca asignada también lanza
> «not set before reading it» — ver el hallazgo gemelo de `r8-prueba-3d.md` §6): es **gatear el
> acceso tras una condición que sí distinga la sala** (`instance_exists(obj_director_de_turno)`,
> o inicializar la global en un objeto persistente que se cree garantizado antes que cualquier
> otra cosa, en vez de dejarla a cargo del primer objeto que la necesite).

### Trampa 5 · Las fuentes creadas por `resourcetool` compilan limpio y no dibujan ni una letra

**El síntoma**: `resource create type=font`, `font addrange name=X lower=32 upper=255`,
`resource set expr=X.size value=N` — todo responde `Success`. `gm-cli compile --errors-only`
sale con `exit 0`. El juego arranca, `screen_save()` ([§4.1](#41-lo-que-un-agente-sí-puede-observar-por-sí-solo))
produce una captura perfecta... salvo que no hay ni una sola letra en pantalla. Todo lo demás se
dibuja con normalidad — solo el texto falta, porque solo el texto depende de una fuente.

**La causa**: rasterizar los glifos — generar el atlas PNG con cada carácter dibujado y las
coordenadas que lo localizan en él — es trabajo del **editor de GameMaker**, no del compilador
ni de ningún comando de `resourcetool`. El `.yy` de una fuente creada por `resourcetool` se
queda con `"glyphs":{}` (diccionario vacío) pase lo que pase con `ranges`, `size`, o incluso con
`font setfile` apuntando a un `.ttf` real del sistema: el comando responde «marked for
re-generation», pero **ningún comando de `resourcetool` ni de `ProjectTool` ejecuta esa
regeneración** (comprobado su `--help` completo: `PROJECT`, `IMPORT YY`, `EXPORT`, `SIGNING`...
nada de rasterizado). El compilador empaqueta el diccionario vacío tal cual: el *chunk* `FONT`
del juego compilado pasa de los ~15 KB que hacen falta para un alfabeto legible a **200 bytes**.

> **Tres datos más sobre `FONT SETFILE`, medidos el 08-09-2026**, que hacen la trampa aún más
> silenciosa de lo que parecía:
>
> - **No copia el `.ttf` al proyecto.** Después de `font setfile … path=…/Andale Mono.ttf`, la
>   carpeta `fonts/fnt_sys/` sigue conteniendo únicamente el `.yy`. La fuente apunta a un archivo
>   que en otra máquina no existe.
> - **No actualiza `fontName`.** Sigue valiendo `Arial` aunque le hayas dado otro `.ttf`.
> - **Compilar no rasteriza.** Se volvió a pedir `FONT GLYPHLIST` después de un `compile` con
>   `exit 0`: el diccionario seguía vacío. Poner `includeTTF` a `true` tampoco genera glifos.
>
> 💡 **Rutas con espacios**: `path="…/Andale Mono.ttf"` con **comilla doble** funciona en `eval` y
> en modo `script`; con comilla simple falla, y sin comillas el parser corta en el espacio
> (`Cannot find Source .TTF file file at path '…/Supplemental/Andale'`). Es la regla contraria a
> la de indexar listas por nombre, que exige comilla **simple** ([§3 bis.1](#3-bis1-las-tres-reglas-del-árbol-de-expresiones)).

**Cómo se detecta**: no por el compilador ni por `validar-proyecto.py` — ninguno de los dos mira
dentro de un recurso de fuente. Solo capturando la pantalla de verdad y mirándola
([§4.1](#41-lo-que-un-agente-sí-puede-observar-por-sí-solo), `screen_save()`), o inspeccionando
el propio `.yy`:

```bash
gm-cli resourcetool eval "font glyphlist name=fnt_titulo"
# {} vacío -> la fuente no tiene ni un solo glifo rasterizado, por más ranges/size que tenga
```

> ⚠️ **No esquives esta trampa apoyándote en `draw_set_font(-1)` (la fuente por defecto) si el
> juego tiene texto en español.** Es la vía «segura» de verdad para no tocar `resourcetool`,
> pero abre una trampa distinta: la fuente por defecto tampoco tiene glifos de
> `á é í ó ú ñ Ñ ¿ ¡`, y los omite en silencio — «Créditos» se dibuja «Crditos». Detalle completo
> y la solución (`font_add()` real, no la fuente por defecto) en la
> [Trampa 12](#trampa-12--la-fuente-por-defecto-de-gamemaker-no-dibuja-acentos-españoles--ni-un-aviso-los-omite-en-silencio)
> de este mismo §0.

**La alternativa más simple, si te vale**: si tu juego solo necesita un puñado de caracteres
fijos (dígitos para un marcador, un logotipo de tres letras), una **fuente de sprite** — dibujar
cada carácter como un frame de un `sprite` normal y componer el texto con `draw_sprite_ext()`
letra a letra — evita el problema de raíz: nunca pasa por el pipeline de fuentes de GameMaker.
Es más trabajo por carácter, así que solo compensa con un alfabeto muy reducido. Si tu juego
necesita texto libre (menús, diálogos, HUD con nombres de jugador), esa alternativa no escala:
la solución real es una de estas dos:

1. **Abre el proyecto en el IDE una vez** y guarda cada fuente creada por `resourcetool` — el
   editor rasteriza los glifos al guardar, y desde ese momento el `.yy` queda con `"glyphs"`
   poblado para siempre, sin que haga falta repetir el paso. Es la vía más simple si tienes el
   IDE a mano; un agente que solo opera por terminal no la tiene.
2. **Hornea el `.yy` tú mismo con Pillow**, si no puedes abrir el IDE. Verificado de punta a
   punta en `_indice/auditorias/r5-prueba-e2e.md`:
   - Parte de un `.yy` de fuente **real**, con glifos ya poblados, de un proyecto descargado en
     `11 - Código descargado/` (cualquier carpeta `fonts/*/*.yy` con `"glyphs"` no vacío) — no
     escribas el formato desde cero, cópialo y edítalo.
   - Con Pillow (`PIL.ImageFont`, `PIL.ImageDraw`), rasteriza cada carácter del rango que
     necesitas con la fuente `.ttf` del sistema, empácalos en un atlas PNG, y calcula para cada
     uno `{character, h, offset, shift, w, x, y}` con las coordenadas reales dentro del atlas.
   - Reescribe el bloque `"glyphs"` del `.yy` de referencia con esas entradas y coloca el PNG del
     atlas junto al `.yy`, con el mismo nombre base que espera GameMaker.
   - Verifica el resultado por el tamaño del *chunk* `FONT` tras compilar (200 bytes = sigue
     vacío; miles de bytes = tiene glifos de verdad) **y** por captura de pantalla real — el
     tamaño del chunk demuestra que hay datos, no que el texto se lea bien.

> 🔴 **Un `.yy` mal formado en este proceso no falla limpio: tumba el toolchain entero.** Una
> coma que falte entre dos entradas del diccionario `"glyphs"` no da un error de parseo JSON
> legible — hace que **`resourcetool` y `gm-cli compile` por igual** revienten con un
> `System.AccessViolationException` nativo (memoria protegida corrupta), y ambas herramientas
> quedan inutilizables sobre ese proyecto hasta que reparas el JSON a mano. Es la prueba en vivo
> de por qué la regla «nunca edites un `.yy` a mano» (`AGENTS.md` §4) también protege un `.yy`
> que generas tú por script: valida el JSON (`python3 -m json.tool archivo.yy > /dev/null`)
> **antes** de dejar que `resourcetool` o `compile` lo toquen.

> ⚠️ **Ampliación del 8 de septiembre de 2026, verificada en
> [`_indice/auditorias/r6-regresion.md` §5.2](../_indice/auditorias/r6-regresion.md#52-el-horneado-con-pillow--la-receta-necesita-dos-campos-que-hoy-no-documenta):
> partir de un `.yy` de referencia (remedio 2 de arriba) no basta con copiar la estructura y
> sobreescribir `name`.** Faltan dos campos más, y si no se corrigen, el fallo **no es limpio —
> tiene tres caras distintas**, observadas en la misma sesión con el mismo `.yy` de fondo, según
> qué parte toca primero el parser concurrente de `ResourceTool`:
>
> - **`%Name`** (con el símbolo de porcentaje — la clave que GameMaker usa de verdad como
>   identidad del recurso, distinta de `name`) se queda con el valor de la plantilla de origen si
>   no se sobreescribe también ella. El recurso queda desincronizado de su propia carpeta/archivo.
> - **`"parent"`** del `.yy` de referencia suele apuntar a una carpeta del Asset Browser (por
>   ejemplo `{"name":"Fonts","path":"folders/Fonts.yy"}`) que existe en el proyecto de origen pero
>   no en el tuyo. Debe quedar en `"parent": null`.
>
> **Los tres síntomas de la misma causa, para reconocerla la próxima vez** — no asumas cuál te va
> a tocar:
>
> 1. **`resourcetool` «repara» mal el recurso** en vez de fallar — a veces reconcilia `%Name` con
>    el de la plantilla original, dejando un recurso con un nombre que no es el tuyo, sin ningún
>    aviso.
> 2. **Crash nativo** — el mismo `System.AccessViolationException` del recuadro de arriba
>    (`GMWindowsOptions.set_option_windows_display_name(String)` en la traza), aunque el JSON sea
>    perfectamente válido y `json.load()` de Python lo acepte sin rechistar. El problema no es la
>    sintaxis JSON, es la identidad del recurso.
> 3. **Error de *linking* legible** — `Cannot find folder path 'folders/Fonts.yy'` o `Field
>    "includeTTF": expected`, según qué campo falte al cargar el proyecto.
>
> **La corrección**: al hornear un `.yy` de fuente a partir de una plantilla real, sobreescribe
> SIEMPRE `%Name` (no solo `name`) y pon `"parent": null` en vez de copiar el de la plantilla —
> el resto de la estructura sí es seguro copiarlo tal cual.

> ⚠️ **Aviso, no confundir con lo de arriba**: `ResourceTool@2026.0.17` tiene, además, un
> `AccessViolationException` **no determinista** que puede saltar incluso sobre un proyecto sano,
> sin relación con las fuentes ni con ningún JSON mal formado — es un problema aparte, de la
> herramienta en general, no de este remedio en particular. Documentado con la mitigación
> (reintentar) en la nueva
> [Trampa 11](#trampa-11--resourcetool2026017-puede-fallar-con-accessviolationexception-de-forma-no-determinista-incluso-sobre-un-proyecto-sano)
> de este mismo §0.

**Severidad**: la más alta de las seis — un agente que no capture y mire una pantalla de verdad
entrega un juego enteramente mudo, sin ningún mensaje de error que lo delate. Detalle completo,
con el diagnóstico paso a paso y el proyecto de referencia, en
[`_indice/auditorias/r5-prueba-e2e.md` §1](../_indice/auditorias/r5-prueba-e2e.md#1--los-recursos-font-creados-por-resourcetool-compilan-limpio-y-no-muestran-texto--nunca-documentado).

### Trampa 6 · `directory_exists()`/`directory_create()` devuelven `false` siempre bajo `gm-cli run --target mac`

**El síntoma**: `save_ensure_dir()` de `06 - Assets y Scripts/scr_save_load.gml` — el script
marcado ⭐ Esencial y «✅ Compilación verificada» del catálogo — falla siempre, incluso sobre la
propia carpeta de guardado (`game_save_id`) que ya existe y tiene archivos dentro. `save_game()`
nunca escribe a disco, y la única pista es una línea de log («no se pudo crear la carpeta de
guardado») que hay que estar mirando activamente para notar: no hay ningún error en pantalla, ni
en el compilador, ni en `validar-proyecto.py`.

**Verificado en vivo** (`_indice/auditorias/r5-prueba-e2e.md` §2), con una tecla de depuración
temporal siguiendo el patrón de [`13 · 10` §7.4](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#74-el-modo-qa-teclas-ocultas-que-no-llegan-al-jugador):

```
directory_exists(game_save_id) = 0     ← la carpeta EXISTE y tiene archivos dentro
directory_create(game_save_id) = 0     ← falla al "crear" lo que ya existe
directory_exists('.')          = 0
directory_exists('')           = 0     ← ninguna llamada a directory_exists() devuelve true
file_text_open_write directo   = 1     ← pero ESCRIBIR un archivo ahí funciona perfecto
file_exists tras escribir      = 1
```

`directory_exists()` devuelve `false` para **cualquier** argumento probado bajo `gm-cli run
--target mac`, mientras que escribir un archivo directamente con `file_text_open_write()` en esa
misma carpeta funciona sin ningún problema. Rompe exactamente el *gate* que ambas funciones
protegen:

```gml
function save_ensure_dir() {
    if (directory_exists(game_save_id)) { return true; }
    return directory_create(game_save_id);   // ambas ramas fallan -> save_game() nunca escribe
}
```

**Alcance honesto**: no está aislado si es un bug del *runtime* 2026.0.0.23 en macOS en general,
o específico del *runner* de pruebas sin firma que lanza `gm-cli run` (`YoYo Runner.app`
genérico, no un `.app` firmado o exportado de verdad) — [§4.2](#42-lo-que-un-agente-no-puede-comprobar-por-sí-solo--pídeselo-al-humano)
de este mismo documento ya avisa de que el *runner* de escritorio "no reproduce" ciertas
condiciones del hardware o del target real. Aun así, **es exactamente el flujo que este
documento recomienda para que un agente pruebe su propio juego** (`gm-cli run`, paso 8 de
[§1](#1--el-ciclo-completo-del-agente)), así que el hallazgo se sostiene tal cual para ese flujo.

**El parche, ya aplicado en `06 - Assets y Scripts/scr_save_load.gml`**: no confiar en el
resultado de `directory_exists()`/`directory_create()` y dejar que el intento real de escritura
decida — documentado con el porqué en el propio script y en
[`01 · 14` §11](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#11-directorios).
Verificado de extremo a extremo: partida → derrota → puntuación guardada → **cerrar el proceso
del juego por completo → volver a lanzarlo → el récord de la sesión anterior aparece cargado en
el menú.** Ese ciclo completo — no solo `save_game() == true` en el mismo *run* — es la única
prueba que no se puede engañar con este bug; procedimiento paso a paso en
[`13 · 10` §8.6](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#86-compilar-limpio-no-es-lo-mismo-que-funcionar-el-fallo-silencioso-de-tiempo-de-ejecución).

**Severidad**: alta, y silenciosa de la misma forma que la Trampa 5 — sin instrumentar una
comprobación deliberada, «probé a guardar y no salió ningún error visible» es la conclusión de
un agente que no mira el log a propósito. Detalle completo en
[`_indice/auditorias/r5-prueba-e2e.md` §2](../_indice/auditorias/r5-prueba-e2e.md#2--directory_existsdirectory_create-devuelven-false-siempre-bajo-gm-cli-run---target-mac--rompe-en-silencio-el-script-de-guardado--esencial-de-la-propia-biblioteca).

### Trampa 7 · Antes de dar un comando por imposible, prueba `resource info expr=project` y `help <COMANDO>`

**El síntoma**: una versión anterior de este mismo documento (§9) afirmaba, con aparente
rigor — «se leyó el `HELP` completo... buscando la palabra "order"» —, que no existía ningún
comando de `resourcetool`/`gm-cli` para leer o escribir el orden de las salas. **Era falso.**

**La causa raíz, verificada en vivo el 8 de septiembre de 2026**: la investigación anterior
probó `resource info expr=RoomOrderNodes` (sin prefijo), recibió `'RoomOrderNodes' not found at
root` y concluyó que `RoomOrderNodes` «no es una raíz de expresión válida». Cierto a medias — no
es una raíz *por sí misma*, pero es un **miembro** de una raíz que nadie había probado:

```bash
$ gm-cli resourcetool eval "resource info expr=project"
Type: project
project members:
┌───────────────────────────────┬────────────────────────────────┬──────────────────────────┐
│ Field                         │ Type                            │ Value                     │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ AudioGroups                   │ list of audiogroup             │ …                        │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ configs                       │ ProjectConfig                  │ …                        │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ defaultScriptType             │ eDefaultScriptType             │ GML                      │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ Folders                       │ list of folder                 │ …                        │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ ForcedPrefabProjectReferences │ list of resource               │ …                        │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ FullName                      │ string                         │ InvestigacionProjectRoot │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ IncludedFiles                 │ list of includedfile           │ …                        │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ isDnDProject                  │ bool                           │ False                    │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ isEcma                        │ bool                           │ False                    │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ LibraryEmitters               │ list of emitter                │ …                        │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ MetaData                      │ dictionary of string -> string │ …                        │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ name                          │ string                         │ InvestigacionProjectRoot │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ parent                        │ resource                       │ null                     │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ resources                     │ list of resource               │ …                        │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ RoomOrderNodes                │ list of RoomOrderNode          │ …                        │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ tags                          │ list of string                 │ …                        │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ templateType                  │ string                         │ null                     │
├───────────────────────────────┼────────────────────────────────┼──────────────────────────┤
│ TextureGroups                 │ list of texturegroup           │ …                        │
└───────────────────────────────┴────────────────────────────────┴──────────────────────────┘
```

`project` **es una raíz de expresión válida** — al mismo nivel que un nombre de recurso
(`spr_ufo`, `obj_ship`) — con 18 miembros propios, entre ellos `RoomOrderNodes`. Salida real,
capturada tal cual en un proyecto de prueba llamado `InvestigacionProjectRoot`. Detalle completo
de los 18 en [§9 bis](#9-bis--la-raíz-project-18-miembros-probados-uno-a-uno).

**Por qué pasó**: el texto de ayuda de `resourcetool` (`HELP`, `HELPTABLE`) documenta
exhaustivamente los **comandos** (`RESOURCE`, `ROOM`, `CONFIG`…) pero **nunca lista las raíces
de expresión disponibles** para `RESOURCE INFO`/`RESOURCE SET` — ni en el texto de ayuda general
ni en `HELP RESOURCE INFO`. Los únicos ejemplos que da son nombres de recursos (`spr_ufo`,
`obj_ship`, `inst_1A5B7D9E`, `room_welcome`). Leer el `HELP` entero, por exhaustivo que sea, **no
basta** cuando lo que falta no es un comando sino una raíz de expresión — y esas solo se
descubren probándolas, no leyéndolas.

**La regla que deja esta trampa**: antes de escribir en esta biblioteca (o en el código de un
agente) «esto no se puede hacer por `resourcetool`/CLI/MCP», prueba explícitamente:

1. `gm-cli resourcetool eval "resource info expr=project"` — la otra raíz de expresión, aparte
   de los recursos con nombre, y la que más a menudo esconde lo que parece imposible
   (configuraciones de build, grupos de audio/textura, archivos incluidos, metadatos…).
2. `gm-cli resourcetool eval "help <COMANDO>"` sobre cada grupo de comandos que pueda rozar el
   tema — la ayuda de subcomandos a veces expone un campo (`filePath`, `CopyToMask`…) que no
   aparece en la tabla resumen.
3. Si de verdad no hay ni raíz ni comando, dilo con la certeza de haber probado esto primero —
   no de haber leído el `HELP` una vez y no haber visto la palabra que buscabas.

Un agente que se cree un «no se puede» sin haber probado esto **no vuelve a intentarlo** — y ese
es el daño real: no es el tiempo perdido en la sesión que lo escribió, es cada sesión futura que
hereda la afirmación y ni se molesta en comprobarla.

### Trampa 8 · `RESOURCE CREATE TYPE=includedfile` deja `filePath` fuera de `datafiles/`, y `--errors-only` no lo detecta

**El síntoma**: `gm-cli resourcetool eval "resource create type=includedfile name=datos.json"`
responde `Success` igual que cualquier otro recurso. `gm-cli compile --errors-only` — el comando
que la tabla de [§1](#1--el-ciclo-completo-del-agente) recomienda para el paso «Compilar» — sale
con `exit 0` y **ni una sola línea**. Todo parece en orden. El archivo de datos, sin embargo,
nunca llega al juego compilado: cualquier `json_parse(file_text_read_all(...))` que dependa de
él falla en tiempo de ejecución, o peor, si el propio código ya defiende contra
`file_exists() == false`, no falla nada — el juego arranca «bien» y sencillamente no tiene los
datos que se supone que debía cargar.

**La causa, reproducida en esta sesión** en un proyecto de prueba bajo `~`
(`gm-cli init -t "Blank Pixel Game"`, borrado al terminar): crear el recurso **no copia ningún
byte** y deja `filePath` como una cadena vacía — la raíz del proyecto, no `datafiles/`, que es
donde el motor espera encontrar el archivo físico.

```bash
$ gm-cli resourcetool eval "resource create type=includedfile name=datos.json"
Created resource named 'datos.json' of type 'GMIncludedFile'
Created resource 'datos.json' of type 'includedfile'
ResourceTool Successful
$ grep -A2 IncludedFiles gm_prueba_includedfiles.yyp
"IncludedFiles":[
    {"$GMIncludedFile":"","%Name":"datos.json","CopyToMask":-1,"filePath":"","name":"datos.json",
     "resourceType":"GMIncludedFile","resourceVersion":"2.0",},
],
$ ls datafiles
ls: datafiles: No such file or directory
```

`filePath:""`, y **la carpeta `datafiles/` ni siquiera existe** — comparado con el `.yyp` de un
proyecto real descargado con Included Files de verdad
(`11 - Código descargado/extensiones_oficiales/GMEXT-GameCenter/source/GameCenter_gml/GameCenter.yyp`),
que trae `"filePath":"datafiles"`. El comando registra el recurso en el proyecto, pero lo deja
apuntando a la nada.

**La reproducción completa, con las dos compilaciones — salida real, sin recortar**:

```bash
$ gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only
$ echo $?
0
```

Sin ninguna línea: parece una compilación limpia. Solo compilando **sin** `--errors-only`
aparece la prueba real, con la ruta exacta que buscó y no encontró:

```
│  WARNING :: datafile /Users/…/gm_prueba_includedfiles/datos.json was NOT copied skipped - reason File does not exist
```

(nótese la ruta: la raíz del proyecto, exactamente lo que dice `filePath:""` — no
`datafiles/datos.json`, que es donde debería buscarlo). Y abriendo el `.zip` compilado, sin
ejecutar el juego:

```bash
$ unzip -l .gmcache/build-gms2-mac-VM/output/game.zip | grep -i json
(sin resultado — datos.json no está en el paquete)
```

**La corrección exacta**: dos pasos, ninguno de los dos automático.

1. Crea `datafiles/` a mano y coloca ahí el archivo físico, con el mismo nombre que el recurso:
   ```bash
   mkdir -p datafiles && cp /ruta/a/datos.json datafiles/datos.json
   ```
2. Fija `filePath` al valor literal `datafiles`. **No lo hagas con el nombre del recurso como
   raíz de expresión si ese nombre lleva un punto** — `resource set expr=datos.json.filePath
   value=datafiles` falla con `'datos' not found at root`, porque `resourcetool` lee el punto
   como acceso a miembro, no como parte del nombre. Usa el índice dentro de
   `project.IncludedFiles` ([§9 bis](#9-bis--la-raíz-project-18-miembros-probados-uno-a-uno)):
   ```bash
   gm-cli resourcetool eval "resource set expr=project.IncludedFiles[0].filePath value=datafiles"
   ```

Recompilando después de los dos pasos, el `WARNING` desaparece y el archivo aparece en el
paquete — verificado en la misma sesión:

```bash
$ gm-cli compile --toolchain GMS2@2026.0.0.23
… (sin ningún WARNING) …
◆  Compilation finished
$ unzip -l .gmcache/build-gms2-mac-VM/output/game.zip | grep json
       43  …   assets/datos.json
```

**Cómo detectarlo antes de que lo note un jugador**: después de crear cualquier `includedfile`
con `resourcetool`, comprueba su `filePath` (`resource info expr=project.IncludedFiles LIST` o
leyendo el `.yyp` directamente) y **compila al menos una vez sin `--errors-only`** antes de dar
la tarea por terminada — es el único de los dos modos que muestra el `WARNING`. Ver también la
corrección de la tabla de [§1](#1--el-ciclo-completo-del-agente) y el checklist de
[§8](#8--checklist-final-antes-de-dar-una-tarea-por-terminada).

**Severidad**: alta, y de la misma familia silenciosa que las Trampas 5 y 6 — un fallo que
compila «limpio» según el propio criterio que esta biblioteca enseña a usar, con el agravante de
que **ni siquiera hace falta ejecutar el juego** para detectarlo: basta con compilar sin el flag
y leer la salida completa, algo que ningún paso de esta biblioteca pedía hacer hasta esta
corrección. Detalle completo, con la construcción en vivo de un juego narrativo completo que lo
descubrió de forma independiente, en
[`_indice/auditorias/r6-prueba-narrativa.md` §6.1](../_indice/auditorias/r6-prueba-narrativa.md#61--el-fallo-real-resource-create-typeincludedfile-no-deja-el-archivo-donde-la-skill-dice-que-vive).


> 🔴 **Y una vez dentro del paquete, el nombre cambia: los *included files* se escriben en
> MINÚSCULAS.** Verificado con `unzip -l` sobre el `game.zip` de un juego real:
>
> ```
>      4414  assets/licencia_fuentes.txt      ← el recurso se llamaba LICENCIA_FUENTES.txt
> ```
>
> La Trampa 8 explica cómo hacer que el archivo llegue al paquete y no decía nada de esto. Si
> nombras el recurso `Fuente_UI.ttf` y luego pides `font_add("Fuente_UI.ttf", …)`, **falla en
> silencio**: `font_add` devuelve `-1`, el juego cae a la fuente por defecto, y esa se come las
> tildes — la Trampa 12 entrando por la puerta de atrás, con el agravante de que el síntoma
> aparece lejos de la causa.
>
> **Nombra el recurso en minúsculas y úsalo así desde GML.** Y ponle la red que sí delata el
> fallo sin mirar la pantalla:
>
> ```gml
> global.fnt_ui = font_add("fuente_ui.ttf", 16, false, false, 32, 255);
> if (global.fnt_ui == -1) show_debug_message("FALLO: no se cargó fuente_ui.ttf del paquete");
> ```

### Trampa 9 · Un `subtype`/argumento rechazado por un subcomando no significa que la propiedad cruda sea inalcanzable

**El síntoma**: `OBJECT EVENT FINDORCREATE` tiene una whitelist cerrada de nombres para `draw` y
`other` (§2.3-§2.4). Pedir `gui_begin` crea de verdad `draw_begin` (Trampa 3), y forzar el
número real como `subtype` falla: `type=draw subtype=74` → `Invalid subtype '74' for event type
'draw'`. De ahí, varias versiones de este documento (y la auditoría `r4-agente-ia-gamemaker.md`
que lo originó) saltaron a «por CLI/MCP no hay manera de crear un GUI Begin/End real» y «los
eventos Async no se pueden crear por CLI ni MCP» — **la misma clase de error que corrigió la
Trampa 7**: confundir «este comando concreto lo rechaza» con «esta biblioteca entera no puede
hacerlo».

**La causa raíz**: `OBJECT EVENT FINDORCREATE` valida el `subtype` contra su propia whitelist de
nombres — eso es negocio de ese comando, no una limitación del formato del recurso. El evento ya
creado expone su número real como un campo crudo (`eventNum`) alcanzable con la raíz de
expresión genérica de `RESOURCE SET`/`RESOURCE INFO` (la misma familia que la Trampa 7 destapó
para `project`), y **ese campo no pasa por la whitelist de `FINDORCREATE`**.

**Verificado en vivo el 8 de septiembre de 2026**, en un proyecto de prueba bajo `~`
(`~/verif_audit_tmp`, `gm-cli init -t "Blank Pixel Game"`, borrado al terminar), `gm-cli` 2.3.0 /
`ResourceTool@2026.0.17`:

```bash
# 1. Crea el evento con CUALQUIER nombre de la whitelist de la misma familia (draw u other)
$ gm-cli resourcetool eval "object event findorcreate name=obj_x type=draw subtype=gui_begin"
New GML file: .../obj_x/Draw_72.gml          # el bug de la Trampa 3: crea draw_begin, no gui_begin

# 2. Localiza el índice del evento en la lista cruda
$ gm-cli resourcetool eval "resource info expr=obj_x.eventList[0]"
eventNum: 72   eventType: 8   ← el 8 es ev_draw; el número es lo que hay que corregir

# 3. Fuerza el número real — esto NO pasa por la whitelist de FINDORCREATE
$ gm-cli resourcetool eval "resource set expr=obj_x.eventList[0].eventNum value=74"
obj_x.eventList[0].eventNum: 74
Saved successfully

# 4. resourcetool ya lo reconoce como el evento real
$ gm-cli resourcetool eval "object event list name=obj_x"
draw │ Event_Draw_DrawGUIBegin        ← antes decía Event_Draw_DrawBegin

# 5. Renombra/escribe el .gml con el nombre que corresponde al número real
#    (FINDORCREATE dejó Draw_72.gml; el evento real necesita Draw_74.gml)
$ mv obj_x/Draw_72.gml obj_x/Draw_74.gml

# 6. Compila
$ gm-cli compile
◆  Compilation finished
```

Reproducido igual con un evento **Async - HTTP** real (`type=other`, se crea con cualquier
nombre whitelisted como `outside`, se parchea `eventNum` a `62`, se renombra a `Other_62.gml`) —
`resourcetool` lo lista después como `Event_Async_HTTP` y compila sin error. Y con **`user1`**
(se crea `user0`, `eventNum` 10 → 11) — se lista como `Event_Other_UserN` detalle `1`. Los tres,
con `gm-cli compile` terminando en `Compilation finished`.

**El paso que de verdad importa y que un agente puede saltarse**: `FINDORCREATE` deja el `.gml`
con el nombre del número **equivocado** (el de la Trampa 3). Parchear solo `eventNum` sin
renombrar el archivo **no da ningún error al compilar** — compila igual de "limpio" que el caso
de la Trampa 8 — pero el código real vive en el archivo con el nombre correcto, no en el que
dejó `FINDORCREATE`. Verifica siempre con `object event list` (§2.5) y, si vas a escribir código
de verdad en el evento, asegúrate de que el `.gml` que editas tiene el nombre `<Prefijo>_<número
real>.gml`.

**Qué eventos concretos desbloquea esto**: cualquier evento cuyo *nombre* esté en la whitelist de
`FINDORCREATE` pero apunte al número equivocado (`gui_begin`/`gui_end`, `room_end` — Trampa 3), y
cualquier evento cuyo número real **no tenga nombre en la whitelist en absoluto**: todos los
`ev_async_*` (HTTP, Save/Load, Steam, Cloud, Networking, System, Social, Push, Audio
Recording/Playback/Playback Ended, Dialog, Web Image Load, Web IAP) y `user1`-`user15`. Sigue sin
haber forma de crear el asset **Extensión** por CLI/MCP (`resource create type=extension` →
`Resource type 'extension' is not creatable` — verificado de nuevo el 8 de septiembre de 2026,
esa sí es una limitación real: el tipo de recurso mismo no admite creación, no hay un `eventNum`
equivalente que parchear).

**La regla que deja esta trampa, además de la que ya dejó la Trampa 7**: cuando un *subcomando*
específico (`OBJECT EVENT FINDORCREATE`, o cualquier otro con una lista cerrada de valores
válidos) rechace algo, prueba si la propiedad cruda es alcanzable por la vía genérica
(`RESOURCE INFO`/`RESOURCE SET` sobre el recurso ya creado) antes de escribir «no se puede por
CLI/MCP». La whitelist es del comando, no siempre del formato del recurso.

> ⚠️ **No teclees `type=async` directamente** — no es un `TYPE` válido de
> `OBJECT EVENT FINDORCREATE` (los Async son `subtype=` numéricos dentro de `type=other`, como
> arriba), y pedirlo no da un mensaje de error limpio: **revienta el propio `resourcetool` con
> una excepción interna sin capturar** (`KeyNotFoundException: The given key 'ev_async' was not
> present in the dictionary`, `exit 2`). Verificado en vivo el 8 de septiembre de 2026. Es fácil
> que un agente lo intente por reflejo — el propio IDE tiene una pestaña «Async» en el diálogo de
> creación de eventos — y un *crash* con traza de pila se lee como «esto está roto» en vez
> de «pedí el `TYPE` equivocado». Usa siempre `type=other subtype=<número>` para esta familia.

### Trampa 10 · `OPTIONS SET` tiene una lista cerrada real — y esta vez no hay campo crudo que la esquive

**El síntoma**: `HELP OPTIONS SET` dice `PROPERTY = <Property name: interpolation, fullscreen,
display_name, image, icon>`. Ni `interpolation` ni `fullscreen` son nombres de propiedad
reales — `resourcetool` los rechaza. Y de una decena de propiedades que sí existen y se leen sin
problema con `OPTIONS GET`/`OPTIONS INFO` (`executable_name`, `company_info`, `version`,
`resize_window`…), **ninguna se puede escribir por CLI/MCP**, y a diferencia de las Trampas 7 y
9, **no hay ninguna raíz de expresión que las alcance por el camino genérico**.

**Verificado en vivo el 8 de septiembre de 2026**, en un proyecto de prueba bajo `~`
(`gm-cli init -t "Blank Pixel Game"`, borrado al terminar), `gm-cli` 2.3.0 /
`ResourceTool@2026.0.17`:

1. **El propio texto de ayuda tiene nombres equivocados.** `OPTIONS GET PLATFORM=windows`
   (sin `PROPERTY=`, para listar todo) y `OPTIONS INFO PLATFORM=windows` devuelven la tabla
   completa y real de propiedades — 30 en Windows —, entre ellas `interpolate_pixels` y
   `start_fullscreen`. `interpolation` y `fullscreen` (los nombres que da `HELP`) **no existen**:
   ```bash
   $ gm-cli resourcetool eval "options set platform=windows property=interpolation value=1"
   Property 'interpolation' is not available for platform 'windows'. Valid properties:
   allow_fullscreen_switching, borderless, company_info, copy_exe_to_dest, copyright_info,
   d3dswapeffectdiscard, description_info, disable_sandbox, display_cursor, display_name,
   executable_name, icon, installer_finished, installer_header, interpolate_pixels, license,
   nsis_file, product_info, resize_window, save_location, scale, sleep_margin, splash_screen,
   start_fullscreen, steam_use_alternative_launcher, texture_page, use_raw_mouse, use_splash,
   version, vsync
   ```
   El nombre correcto es `interpolate_pixels`; el de «fullscreen» es `start_fullscreen`. Con los
   nombres reales, **solo cinco de las 30 propiedades se pueden escribir**:
   `interpolate_pixels`, `start_fullscreen`, `display_name`, `icon` y `splash_screen` (las dos
   últimas piden una ruta a un PNG real, no un valor arbitrario). Las 25 restantes —incluidas
   `executable_name`, `company_info`, `copyright_info`, `description_info`, `product_info`,
   `version`, `resize_window`, `borderless`, `vsync`, `scale`, `save_location`, `sleep_margin`,
   `texture_page`, `use_raw_mouse`, `display_cursor`, `disable_sandbox`,
   `allow_fullscreen_switching`, `copy_exe_to_dest`, `d3dswapeffectdiscard`,
   `steam_use_alternative_launcher`, `license`, `nsis_file`, `installer_finished`,
   `installer_header` — dan siempre el mismo error, aunque el nombre sea correcto y el valor
   válido:
   ```bash
   $ gm-cli resourcetool eval "options set platform=windows property=executable_name value=MiJuego"
   Property 'executable_name' cannot be set on 'windows' because it is read-only.
   ```
2. **Por qué esta vez no sirve el truco de la Trampa 7/9**: las opciones de plataforma
   (`GMWindowsOptions`, `GMMacOptions`…) viven en `options/<plataforma>/options_<plataforma>.yy`
   como un recurso `.yy` normal y corriente, con `resourceType` y `%Name` como cualquier otro —
   pero **no están entre los 17 tipos que devuelve `RESOURCE TYPES`**, y su nombre (`Windows`,
   `Mac`…) **no es una raíz de expresión válida**:
   ```bash
   $ gm-cli resourcetool eval "resource info expr=Windows"
   'Windows' not found at root
   ```
   Tampoco aparecen como miembro de `project` (los 18 miembros de
   [§9 bis](#9-bis--la-raíz-project-18-miembros-probados-uno-a-uno) no incluyen ninguno de
   opciones). `RESOURCE INFO`/`RESOURCE SET` sencillamente no llegan hasta aquí — es un
   subsistema aparte, gestionado en exclusiva por la familia `OPTIONS`, y esa familia decide por
   diseño qué se puede escribir desde fuera del IDE.
3. **Confirmado que es una limitación real, no una whitelist perezosa**: si fuera solo que
   `OPTIONS SET` no reconoce el nombre, el error sería «not available, valid properties: …»
   (el que da `interpolation`). En cambio, para las 25 propiedades read-only el propio mensaje
   lo dice explícito: *«cannot be set... because it is read-only»* — es una decisión consciente
   del comando, no un hueco de cobertura.

**Qué significa para un agente que prepara un lanzamiento**: nombre de compañía, copyright,
descripción, versión del ejecutable, si la ventana es redimensionable/sin bordes, VSync, el
modo de escalado, la ruta de guardado, el lanzador alternativo de Steam, la licencia y el script
NSIS del instalador — **todo eso hay que pedírselo al humano, que lo ponga desde la ventana
Game Options del IDE.** Solo el nombre visible, el icono, la imagen de splash, si arranca a
pantalla completa y si interpola píxeles se pueden fijar por CLI/MCP hoy.

> 🔴 **Y de las cinco que sí se escriben, una te miente: `OPTIONS SET` trunca el valor en el
> primer espacio y responde «éxito».** Verificado el 08-09-2026:
>
> ```console
> $ gm-cli resourcetool eval "options set platform=windows property=display_name value=La Ultima Chispa"
> Set windows.display_name = La
> Saved successfully
> ResourceTool Successful          ← ni un aviso
> $ gm-cli resourcetool eval "options get platform=windows property=display_name"
> display_name = La
> ```
>
> El juego habría salido llamándose **«La»** en el Finder y en el conmutador de aplicaciones, y
> no hay forma de enterarse salvo releyéndolo. **Entrecomilla siempre el valor** — funciona
> incluso con tildes:
>
> ```console
> $ gm-cli resourcetool eval 'options set platform=windows property=display_name value="La Última Chispa"'
> Set windows.display_name = La Última Chispa
> ```
>
> Encontrado por un agente que construyó un juego entero usando solo esta biblioteca
> ([`r12-prueba-plataformas.md` §1.2](../_indice/auditorias/r12-prueba-plataformas.md)).

> ⚠️ **La columna se titula «Option» y el argumento se llama `PROPERTY=`.** `OPTIONS INFO`
> imprime la tabla con la cabecera `Option`, así que el reflejo es escribir
> `options set … option=version`, que no existe. El argumento correcto es **`PROPERTY=`**, y el
> error de un nombre equivocado **vuelca la ayuda entera** en vez de decir cuál era.
>
> **Y `name=` es peor que un nombre equivocado, porque cada verbo falla de una manera distinta.**
> Cuatro variantes verificadas el 09-09-2026 leyendo el `.yy` de vuelta:
>
> | Lo que escribes | Qué pasa |
> |---|---|
> | `options set … property=display_name value="Con espacios"` | ✅ escribe `Con espacios` |
> | `options set … property=display_name value=Con espacios` | escribe `Con` — trunca y dice «éxito» |
> | `options set … property=display_name value='Con espacios'` | escribe `'Con` — **peor**: se queda la comilla |
> | `options set … property=display_name value=Con\ espacios` | escribe `Con\` |
> | `options set … name=display_name value=X` | `Command failed: npm exec failed with code 1`, sin decir por qué |
> | `options get … name=display_name` | **vuelca las ~30 propiedades** (13 KB) y termina en `Successful`: ignora el argumento sin avisar |
> | `options get … property=display_name` | ✅ `display_name = Con espacios` |
>
> La fila del `GET` con `name=` es la que muerde: no falla, **contesta otra cosa**. Un agente que
> busque su propiedad en esa avalancha creerá que la ha leído.
> ([`r15` §2.7](../_indice/auditorias/r15-prueba-puzles.md))

> 💡 **`options info` no cabe en la salida de un agente.** `options info platform=mac` devuelve
> **82 KB** de tabla con bordes Unicode, que desborda la salida del Bash de Claude Code y de
> cualquier herramienta con tope. Pide solo los nombres:
>
> ```bash
> gm-cli resourcetool eval "options info platform=mac" | grep -oE "^│ [a-z_0-9]+ +│" | tr -d '│ '
> ```
>
> Y `icon_png` **exige exactamente 1024×1024**: con otro tamaño responde
> `Image … dimensions (512 x 512) do not match the expected dimensions (1024 x 1024)` y no
> escribe nada. Genera el tamaño exacto antes (`sips -z 1024 1024 …`).

> ⚠️ **Los nombres de las propiedades NO son los mismos en todas las plataformas.** La tabla de
> arriba es la de Windows, y en Mac dos de las cinco escribibles se llaman de otra forma:
>
> | Escribible | Windows | macOS |
> |---|---|---|
> | Nombre visible | `display_name` | `display_name` |
> | Interpolar píxeles | `interpolate_pixels` | `interpolate_pixels` |
> | Arrancar a pantalla completa | `start_fullscreen` | `start_fullscreen` |
> | Icono | `icon` (un `.ico`) | **`icon_png`** (PNG 1024×1024) |
> | Splash | `splash_screen` | **`splash_png`** |
>
> Pedir `icon` en Mac da `is not available for platform 'mac'`, no un valor por defecto.
> **Lista siempre las propiedades reales de tu plataforma antes de escribir**, con
> `options info platform=<la tuya>` — y si no imprime nada, con el truco del nombre inventado.
> La tabla por plataforma para los iconos está en
> [`07 · 24 §2.2`](../07%20-%20Ecosistema/24%20-%20Logotipo%2C%20icono%20del%20ejecutable%20y%20capsule%20de%20tienda.md#22-la-vía-nativa-de-gamemaker-resourcetool-options-set-hallazgo-verificado).

**Pero esas cinco sí se fijan POR CONFIGURACIÓN, y eso cambia bastante.** Es exactamente como se
prepara una build de demo o de prensa con otro nombre y otro icono, y no estaba documentado
(verificado el 08-09-2026):

```console
$ gm-cli resourcetool eval "config create name=Demo parent=Default"
Config 'Demo' created successfully based on parent 'Default'.
$ gm-cli resourcetool eval --config Demo "options set platform=windows property=display_name value=JuegoDemo"
Set windows.display_name = JuegoDemo
$ gm-cli resourcetool eval --config Demo    "options get platform=windows property=display_name"
display_name = JuegoDemo
$ gm-cli resourcetool eval --config Default "options get platform=windows property=display_name"
display_name = Pixel Game        ← las dos conviven
```

El flag va **antes** del comando. Dos avisos:

- **`CONFIG USAGES` no reporta estos *overrides*** (sigue diciendo «no hay filas»): no lo uses
  como verificación. Lee el valor con `OPTIONS GET --config <nombre>`.
- **Un `RESOURCE SET` bajo `--config` NO crea un *override***: escribe el valor base. Comprobado
  leyendo el mismo campo bajo las dos configuraciones — idéntico. El mecanismo de configuración
  solo alcanza a las opciones de plataforma, no al árbol de recursos.

**Y la plataforma `main` es peor: figura en la lista y no funciona en absoluto.**
`OPTIONS LIST` la anuncia junto a `windows`, `mac` y las demás — es la pestaña *Main* de Game
Options, donde viven la velocidad del juego, el color de fondo y el comportamiento ante errores,
justo lo que a un agente le interesaría fijar. Pero en `ResourceTool@2026.0.17` está rota de las
tres formas posibles a la vez (verificado el 08-09-2026):

```bash
$ gm-cli resourcetool eval "options info platform=main"
# (no imprime NADA: ni tabla ni error)

$ gm-cli resourcetool eval "options get platform=main"
There are no table rows to show
ResourceTool Successful          # ← «éxito» con cero filas

$ gm-cli resourcetool eval "options set platform=main property=speed value=60"
Property 'speed' is not available for platform 'main'. Valid properties: instance_change,
error_behaviour, , compatibility, on_write_enabled, colour, speed, , json_parsing, …
```

Lee esa última salida despacio: **`speed` aparece en la lista de propiedades válidas del propio
mensaje que la rechaza**. Y la lista viene con huecos vacíos (`, ,`) y `colour` repetido — es una
tabla de descriptores mal formada, no una lista real. Probado también con `app_id`, `description`
y `colour`, todos nombres que el mensaje declara válidos: los tres dan el mismo
`not available for platform`.

> 💡 **El truco que sí sirve de aquí**: cuando `OPTIONS INFO` no imprima nada, **manda a propósito
> un nombre de propiedad inventado**. El mensaje de error enumera las propiedades que el comando
> considera válidas para esa plataforma, y es la única forma de verlas cuando `INFO` calla. Que
> luego las acepte es otra cuestión.

**La regla que deja esta trampa**: el patrón de la Trampa 7/9 («si un subcomando rechaza algo,
prueba la raíz de expresión genérica») **no es universal** — solo funciona para recursos que
viven bajo el árbol de `RESOURCE`/`project`. Antes de aplicarlo a ciegas, comprueba con
`resource types` y `resource info expr=project` si el dato que buscas está siquiera ahí. Si no
lo está (como las opciones de plataforma), no hay campo crudo que parchear: la limitación es
real y hay que decírselo al humano con esa certeza, no con la esperanza de que exista un rodeo.

### Trampa 11 · `ResourceTool@2026.0.17` puede fallar con `AccessViolationException` de forma no determinista, incluso sobre un proyecto sano

**El síntoma**: la misma llamada de `resourcetool`, sobre el mismo proyecto sin ningún archivo mal
formado, responde bien unas veces y revienta otras con un `System.AccessViolationException`
nativo — el mismo tipo de excepción que la Trampa 5 documenta para un `.yy` corrupto, pero aquí
**sin ninguna causa en los datos**: nada cambia en el proyecto ni en el comando entre un intento y
el siguiente. No lo confundas con el `.yy` mal formado de la Trampa 5 ni con el `%Name`/`parent`
mal fijado al hornear una fuente (ambos también terminan en `AccessViolationException`, pero ahí
sí hay una causa real que corregir en los datos): esta trampa es del propio `ResourceTool`, no de
lo que le pases.

**Verificado en vivo el 8 de septiembre de 2026**
([`_indice/auditorias/r6-regresion.md` §5.4](../_indice/auditorias/r6-regresion.md#54-hallazgo-nuevo-separado--resourcetool2026017-tiene-un-accessviolationexception-no-determinista-incluso-sano)):
cinco llamadas idénticas y seguidas (`resourcetool status`) sobre el mismo proyecto de prueba, de
solo 3 recursos, ya sano:

```
intento 1: Core Resources : Info - +++ GMSC serialisation: SUCCESSFUL LOAD AND LINK TIME: 92.305ms
intento 2: Fatal error. System.AccessViolationException...
intento 3: Fatal error. System.AccessViolationException...
intento 4: Core Resources : Info - +++ GMSC serialisation: SUCCESSFUL LOAD AND LINK TIME: 95.799ms
intento 5: Core Resources : Info - +++ GMSC serialisation: SUCCESSFUL LOAD AND LINK TIME: 94.876ms
```

2 de 5 fallaron con exactamente el mismo crash nativo, 3 no. La traza apunta a
`ConcurrentFileSetLoader`: parece una condición de carrera real dentro del propio cargador
concurrente de `ResourceTool`, no un síntoma de contenido corrupto — no está ligado a ningún
comando concreto ni al tamaño del proyecto (apareció con solo 3 recursos en el `.yyp`).

**La mitigación, verificada de punta a punta**: reintenta la misma llamada de `resourcetool`
(hasta 10-12 veces si hace falta) antes de asumir que el proyecto está corrupto — en la sesión que
lo descubrió, reintentar siempre terminó por pasar. **No hay forma de predecir cuándo hace falta
reintentar**, así que trátalo como un hábito, no como un diagnóstico previo: si una llamada de
`resourcetool` revienta con `AccessViolationException` sobre un proyecto que ya sabes sano, el
primer paso es repetir la misma llamada, no investigar qué se rompió. Añadido al checklist de
[§8](#8--checklist-final-antes-de-dar-una-tarea-por-terminada).

### Trampa 12 · La fuente por defecto de GameMaker no dibuja acentos españoles — ni un aviso, los omite en silencio

**El síntoma**: `draw_set_font(-1)` (o no fijar ninguna fuente) es la vía «segura» que esta
misma biblioteca sugiere para esquivar la Trampa 5 — no crear ninguna fuente por `resourcetool`,
depender de la fuente por defecto del motor. `gm-cli compile` sale con `exit 0`, sin ningún
`WARNING`. El juego arranca, `screen_save()` produce una captura perfecta... salvo que
**cualquier `á é í ó ú ñ Ñ ¿ ¡` desaparece del texto, sin dejar hueco ni caja de «glifo no
encontrado»**. `draw_text(x, y, "¡Añádeme más peón!")` se dibuja «Ademe ms pen!»: el motor
recorre la cadena carácter a carácter y **salta en silencio** cualquiera que no tenga glifo en el
atlas integrado, como si nunca hubiera estado ahí — ni el hueco ni el orden del resto del texto
delatan que falta algo.

**Verificado en esta sesión** (proyecto de prueba bajo `~`, borrado al terminar): un objeto con
`draw_set_font(-1); draw_text(16, 16, "¡Añádeme más peón!");` en Draw GUI, compilado y ejecutado
con `gm-cli run --target mac`, capturado con `screen_save()` y leído el PNG resultante. Antes de
mirar la pantalla se comprobó que **no es un problema de codificación de origen**: los bytes
UTF-8 de cada tilde y eñe están intactos y son idénticos tanto en el `.gml` fuente como dentro
del `game.ios` ya compilado (mismo `xxd`/hexdump en los dos). El fallo es exclusivamente de
**renderizado**, en el juego de glifos que trae la fuente integrada del motor — no en cómo el
texto llegó hasta ahí.

**La causa**: la fuente que usa el motor cuando no cargas ninguna propia solo trae rasterizado un
subconjunto de caracteres (en la práctica, ASCII básico); no incluye los caracteres por encima de
ese rango, y GameMaker no avisa cuando pide dibujar uno que no tiene — simplemente lo descarta.
Es la misma familia de fallo silencioso que las Trampas 5, 6 y 8: **compila limpio y no se
detecta ni por el compilador ni por `validar-proyecto.py`**, porque ninguno de los dos mira un
solo píxel de la pantalla. Para una biblioteca escrita entera en español, y cuya regla número uno
es que todo el texto del juego lleve ortografía completa, es el hueco más grave de los tres que
esta sesión encontró: contradice de hecho la recomendación implícita de
[`08 · 03`](../08%20-%20Referencia%20GML%20completa/03%20-%20Texto%20y%20fuentes.md) de usar
`draw_set_font(-1)` como alternativa «segura» frente al horneado roto de la Trampa 5 — es segura
para **compilar**, no para **mostrar texto en español**.

**Cómo se detecta**: igual que la Trampa 5, solo capturando la pantalla de verdad y leyendo el
PNG ([§4.1](#41-lo-que-un-agente-sí-puede-observar-por-sí-solo)); ninguna herramienta de texto
(`validar-proyecto.py`, el compilador, un `grep` sobre el `.gml`) lo detecta, porque el propio
código fuente es correcto — el fallo está en qué elige rasterizar la fuente del motor, no en lo
que el agente escribió.

**La solución, verificada de punta a punta en esta misma sesión**: no es una fuente nueva de la
nada — es **conectar dos piezas de esta biblioteca que hasta ahora no estaban enlazadas entre
sí**: `font_add()` ([`08 · 03` — Gestión de fuentes](../08%20-%20Referencia%20GML%20completa/03%20-%20Texto%20y%20fuentes.md#gestión-de-fuentes))
cargando un `.ttf` real, empaquetado como *Included File* siguiendo al pie de la letra la receta
de la [Trampa 8](#trampa-8--resource-create-typeincludedfile-deja-filepath-fuera-de-datafiles-y---errors-only-no-lo-detecta)
de este mismo §0 (crear el recurso, copiar el archivo físico a `datafiles/`, y fijar `filePath`
con `resource set expr=project.IncludedFiles[0].filePath value=datafiles`):

```gml
/// Create — carga una fuente real con acentos, en vez de depender de la fuente por defecto
/// Verificado: font_add
fnt_ui = font_add("fuente_ui.ttf", 24, false, false, 32, 255);
// first=32, last=255: cubre ASCII completo + Latin-1 (á, é, í, ó, ú, ñ, Ñ, ¿, ¡)
```

```gml
/// Draw GUI
draw_set_font(fnt_ui);           // NUNCA draw_set_font(-1) si el texto lleva español
draw_text(16, 16, "¡Añádeme más peón!");
```

Reproducido con `SFNSMono.ttf` del propio sistema (válido solo para verificar localmente —
**nunca para distribuir**: hace falta una fuente con licencia redistribuible para publicar de
verdad): compiló sin ningún `WARNING`, el `.ttf` entró en el paquete compilado
(`unzip -l … | grep ttf` → `assets/fuente_ui.ttf`), y el texto en pantalla pasó de
«¡Añádeme más peón!» dibujado «Ademe ms pen!» a las tildes y la eñe completas — capturas de
antes y después comparadas píxel a píxel en la misma sesión que verificó esta trampa.

#### La tercera salida, y para un agente suele ser la mejor: `font_add_sprite_ext()`

Las dos vías anteriores tienen peaje: la fuente del proyecto arrastra la **Trampa 5** (los glifos
no se rasterizan por CLI) y el `.ttf` por *Included File* arrastra la **Trampa 8** *y* te obliga a
conseguir una tipografía con licencia redistribuible, que esta biblioteca no te da. Hay una
tercera que evita las dos cosas y que ningún documento presentaba como respuesta a esta trampa:

```gml
/// Create — la hoja de glifos es un sprite normal, así que no hay Trampa 5 ni Trampa 8
/// Verificado: font_add_sprite_ext(spr, string_map, prop, sep)
global.fnt_ui = font_add_sprite_ext(
    spr_glifos,
    " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~áéíóúüñÁÉÍÓÚÜÑ¿¡",
    true,   // prop: ancho proporcional; false = todos los glifos igual de anchos
    1       // sep: píxeles de separación entre caracteres
);
```

`string_map` es **la cadena que dice, en orden, qué carácter es cada sub-imagen del sprite**. Por
eso `font_add_sprite_ext` es mejor que `font_add_sprite(spr, first, prop, sep)` para español:
aquel exige que los caracteres sean **consecutivos** desde un código, y las tildes y la eñe no lo
son — están dispersas por Latin-1. Con `_ext` los pones donde quieras.

**Por qué encaja tan bien con un agente**: la hoja de glifos la puedes **dibujar tú** con Pillow,
igual que el resto de los *placeholders* de [§5.2](#52-gráfico-la-escalera-de-prioridad-sin-el-rectángulo-plano)
— un carácter por sub-imagen, mismo alto, y ya tienes tipografía propia con tildes, sin licencia
ajena, sin `.ttf`, sin *Included File* y sin abrir el IDE. Un agente que construyó un RPG con
esta biblioteca acabó ahí después de más de una hora peleando con las otras dos vías, y anotó que
nadie se lo había dicho ([`r13-prueba-rpg.md`](../_indice/auditorias/r13-prueba-rpg.md)).

> ⚠️ **Ojo con las comillas dentro del `string_map`.** La cadena lleva `"` y `\`, y los dos hay
> que escaparlos. Es exactamente el literal que rompe el análisis si se te escapa uno —
> [§3 bis del nivel como mapa de texto](../04%20-%20Recetas%20por%20género/58%20-%20El%20nivel%20como%20mapa%20de%20texto%20-%20construir%20sin%20abrir%20el%20editor%20de%20salas.md).
> Si te resulta más cómodo, deja fuera del mapa la comilla y la barra.

##### La receta completa, verificada ejecutándola

Lo de arriba explica **por qué** `font_add_sprite_ext`; esto es el **cómo**, de punta a punta.
Un agente lo resolvió entero por su cuenta porque no estaba escrito
([`r15` §2.8](../_indice/auditorias/r15-prueba-puzles.md)); ahora está, y además lo comprueba
`bash _indice/validar-ejecucion.sh` en cada pasada, dentro de un juego real.

**1 · Dibuja un PNG POR CARÁCTER, no una tira.** `SPRITE ADDFRAME` añade **un fotograma por
archivo**: la hoja de glifos de una fuente de sprite no es una imagen larga, son N imágenes del
mismo tamaño. El generador completo, listo para copiar, está en
`_indice/pruebas/generar_glifos.py` — rasteriza una `.ttf` del sistema con **umbral duro** (sin
antialias: así no hay halo de alfa parcial y la puerta del peldaño 2 bis lo deja en paz).

**2 · El espacio necesita una barra sólida.** El manual lo dice de pasada —«puede definir el
espacio como cualquier carácter que desee, por ejemplo una sola línea»— y la imagen elegida
nunca se dibuja. Lo que no dice es la consecuencia: **si la sub-imagen del espacio va vacía, el
ancho del espacio lo decide el motor y no tú.** Medido con una barra de 4 px y `sep = 1`:

```console
MEDIDO · string_width(" ") con barra solida = 5
```

**3 · Impórtalos EN LOTE.** Uno a uno con `resourcetool eval` son minutos; en lote, un segundo:

```bash
# un `sprite addframe` por línea, y una sola llamada
for g in glifos/g_*.png; do
  echo "sprite addframe name=spr_glifos path=$g" >> lote.txt
done
gm-cli resourcetool eval "resource create type=sprite name=spr_glifos" <proyecto.yyp>
gm-cli resourcetool script lote.txt <proyecto.yyp>
```

Medido aquí: **89 fotogramas en 1,46 s**. Y como siempre, `Saved successfully` no vale — se lee
de vuelta contando los fotogramas del `.yy`:

```bash
grep -o '"\$GMSpriteFrame"' sprites/spr_glifos/spr_glifos.yy | wc -l   # → 89
```

**4 · Deja fuera del mapa la comilla y la barra invertida.** No es una limitación seria: son dos
caracteres que casi ningún juego dibuja, y evitarlos elimina de raíz el literal mal escapado.

**5 · El mapa del `.gml` y la hoja tienen que coincidir CARÁCTER A CARÁCTER.** Si divergen, el
juego dibuja letras cambiadas y compila igual de limpio. Se comprueba en una línea, dentro del
juego:

```gml
// El número de sub-imágenes tiene que ser el número de caracteres del mapa.
if (sprite_get_number(spr_glifos) != string_length(GLIFOS_MAPA)) {
    show_debug_message("HOJA Y MAPA DESCUADRADOS: " + string(sprite_get_number(spr_glifos))
        + " sub-imágenes para " + string(string_length(GLIFOS_MAPA)) + " caracteres");
}
```

> 🔴 **Y el hallazgo que cambia cómo se detecta esta trampa entera: NO hace falta una captura.**
> Hasta ahora este documento decía que la fuente muda solo se detecta capturando la pantalla y
> mirando el PNG. Es verdad a medias. **Un carácter que la fuente no tiene mide cero.** Medido
> dentro del juego contra la fuente por defecto del motor:
>
> ```console
> MEDIDO · fuente por defecto: a=9  á=0  ñ=0  ¿=0
> ```
>
> Así que la Trampa 12 se cierra con una condición en el arranque, sin ojos y sin capturas.
> Está hecha en [`06 · scr_debug.gml`](../06%20-%20Assets%20y%20Scripts/scr_debug.gml):
>
> ```gml
> // En el arranque, con la fuente que vas a usar de verdad:
> debug_exigir_fuente_con_acentos(global.fnt_ui);   // avisa y devuelve false si falta alguno
> var _faltan = debug_fuente_sin_glifos(global.fnt_ui, "áéíóúüñÁÉÍÓÚÜÑ¿¡");
> ```
>
> **Lo que prueba y lo que no**: ancho 0 prueba que el glifo **no está**, y eso es concluyente.
> Ancho > 0 prueba que hay algo dibujado en ese hueco, **no** que sea el glifo correcto — una
> hoja con el mapa desordenado dibuja letras cambiadas y mide perfectamente. Para eso sigue
> haciendo falta mirar ([`13 · 10 §8.6`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md)).
> Es una red barata que caza el fallo más común de los dos, no un sustituto de mirar.

**Severidad**: alta, y de la familia silenciosa de las Trampas 5, 6 y 8 — con el agravante de que
la vía que parece más segura (no tocar `resourcetool`, fiarse de la fuente por defecto) es
precisamente la que lo dispara. Cross-referencias con la explicación completa y el aviso para
cualquier documento que enseñe a dibujar texto en
[`01 · 11` § La fuente por defecto no tiene acentos españoles](../01%20-%20Fundamentos/11%20-%20Dibujo%20y%20renderizado.md#la-fuente-por-defecto-no-tiene-acentos-españoles)
y en [`13 · 05` §3.6](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#36-tipografía-bitmap-ttf-y-sdf).
Detalle completo, con el hexdump de verificación y las capturas de antes y después, en
[`_indice/auditorias/r7-prueba-movil.md` §2.5-1](../_indice/auditorias/r7-prueba-movil.md#25--sirvieron-las-once-trampas-o-tropecé-con-alguna-nueva).

### Trampa 13 · `screen_save()` invierte la imagen verticalmente en el runner de Mac — la ventana real no

**El síntoma**: al comprobar una captura tomada con `screen_save()` (§7.3 de
[`13 · 10`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md))
para verificar visualmente un horneado de fuente o un elemento de UI, el PNG resultante muestra
el contenido **boca abajo y con el orden vertical invertido**: un título dibujado en `y=20`
aparece al fondo de la imagen, no arriba; un sprite anclado al borde superior de la GUI aparece
pegado al borde inferior. El juego, jugado en directo, **se ve correcto** — el volteo es
exclusivo del archivo que produce `screen_save()`.

**Verificado en esta sesión** (`~/gm_prueba_gestion`, proyecto de prueba, borrado al terminar;
`gm-cli` 2.3.0, runtime `2026.0.0.23`, `--target mac`): un horneado de fuente y un sprite de
prueba se capturaron con `screen_save()` y salieron invertidos verticalmente. Antes de asumir
que el horneado estaba mal, se comparó contra una captura de pantalla real del sistema operativo
(`screencapture`) tomada mientras el mismo fotograma se veía en la ventana del runner: **la
ventana se ve perfectamente, derecha, en el orden correcto** — confirma que el volteo es de
`screen_save()` en esta combinación concreta, no del juego ni del código del agente.

**La causa**: no confirmada contra el manual oficial (que no documenta ninguna diferencia de
orientación entre lo que se ve en pantalla y lo que escribe `screen_save()`) — consistente con
una diferencia de convención de ejes Y entre el *buffer* que lee `screen_save()` en el *runner*
de Mac y el que compone la ventana, específica de esta combinación de `gm-cli`/runtime/target.
No se investigó más a fondo por no ser el objetivo de la sesión que la encontró; el hecho
verificado es el síntoma, con su contraste contra `screencapture`, no la causa interna del
motor.

**Cómo se detecta**: comparando, al menos una vez por sesión de verificación visual, una captura
de `screen_save()` contra una captura de pantalla real del sistema operativo (`screencapture` en
Mac) tomada mientras se ve el mismo fotograma en la ventana del runner. Si las dos coinciden en
todo menos en el eje vertical, es esta trampa, no un bug del juego.

**La mitigación**: si tu procedimiento de verificación (`§4.1` de este documento,
[`13 · 10` §8.6 Procedimiento 1](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#86-compilar-limpio-no-es-lo-mismo-que-funcionar-el-fallo-silencioso-de-tiempo-de-ejecución)
o el guion de humo de
[`13 · 10` §8.7](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#87--el-guion-de-humo-arrancar-capturar-sola-y-verificar-el-guardado-sin-manos))
depende de `screen_save()` para diagnosticar POSICIÓN vertical (un elemento arriba/abajo,
solapamiento con el borde superior o inferior), voltea la imagen mentalmente —o con cualquier
herramienta de imagen— antes de concluir nada sobre el eje Y, o contrasta con
`screencapture` esa captura en concreto. Para diagnósticos que no dependen de arriba/abajo
(¿aparece el texto?, ¿está el color correcto?, ¿existe el sprite?) esta trampa no afecta a la
conclusión.

**Severidad**: media — no bloquea nada por sí sola, pero **puede llevar a un diagnóstico
equivocado de un bug de renderizado que no existe** (o a no ver uno real que sí existe, si el
agente da por buena una posición vertical que en realidad está invertida). Es la misma familia
de fallo que las Trampas 5 y 12: la herramienta de verificación automática no es sincera sobre lo
que muestra, y solo se ve contrastando con otra fuente. Detalle completo, con el hallazgo en
contexto, en
[`_indice/auditorias/r7-prueba-gestion.md` §9](../_indice/auditorias/r7-prueba-gestion.md#9--las-once-trampas--cuáles-se-usaron-de-verdad-y-una-nueva).

**Discrepancia registrada el 8 de septiembre de 2026, no resuelta**: una prueba de un juego de
ritmo (mismo `gm-cli`, mismo `--target mac`, mismo runtime `2026.0.0.23` que documenta esta
trampa) tomó **seis capturas con `screen_save()`** en la misma sesión (menú, juego, opciones,
pausa, victoria, créditos) y **ninguna salió invertida**: las seis se vieron en la orientación
esperada, arriba lo de arriba. No se vuelve a reproducir la trampa a voluntad — puede depender de
algo del contexto que ninguna de las dos sesiones aisló todavía (pantalla completa frente a
ventana, la resolución concreta del proyecto, una diferencia fina de versión no capturada por
`2026.0.0.23`, u otra variable no identificada). **No se retira la trampa**: se verificó en vivo
una vez, con contraste directo contra `screencapture`, así que sigue siendo real en al menos esa
combinación — pero tampoco es fiable darla por segura siempre. Trátala como **intermitente**: si
tu captura de `screen_save()` se ve invertida, es esta trampa; si se ve bien, no des por hecho que
nunca te va a pasar — sigue siendo buena práctica contrastar con `screencapture` al menos una vez
por sesión de verificación visual, tal y como dice la mitigación de arriba, en vez de asumir
ninguno de los dos resultados por defecto. Detalle de la sesión que no la reprodujo en
[`_indice/auditorias/r8-prueba-ritmo.md` §6.2](../_indice/auditorias/r8-prueba-ritmo.md#62--la-trampa-13-screen_save-invertido-no-se-reprodujo--posible-desfase).

### Trampa 14 · 🔴 `RESOURCE CREATE TYPE=shape` deja el proyecto irrecuperable

**Que un tipo aparezca en `RESOURCE TYPES` no significa que se pueda crear.** `shape` es uno de
los 17 que anuncia, y crearlo **rompe el proyecto para siempre** por CLI. Verificado el
08-09-2026, reproducido tres veces sobre un proyecto recién creado: es determinista, no es la
Trampa 11.

```console
$> RESOURCE CREATE TYPE=shape NAME=shp_test
Created resource named 'shp_test' of type 'GMShape'
System.UnauthorizedAccessException: Access to the path '/Users/…/audit12' is denied.
    IExecutableCommand: Write binary file /Users/…/audit12
Project save failed
```

Intenta escribir un archivo binario **sobre la ruta del directorio del proyecto**, sin nombre de
archivo. Pero antes de fallar **ya ha registrado el recurso** en el `.yyp` y en el
`.resource_order`, con la ruta vacía. A partir de ahí no carga nada — ni `resourcetool`, ni
`compile`, ni `status` — y **no hay comando que lo deshaga**: `resource delete` con tres
variantes distintas devuelve siempre el mismo error de carga, porque para borrarlo tendría que
poder abrir el proyecto.

**La única reparación es a mano**, y es justo lo que `AGENTS.md §4` prohíbe salvo emergencia.
Esto es una emergencia:

```bash
sed -i '' '/"name":"shp_test"/d' MiJuego.yyp MiJuego.resource_order
# y normaliza el JSON con la herramienta oficial, para no dejar el formato a medias:
.gmcache/project-tool/*/ProjectTool json format input=MiJuego.yyp commas=GAMEMAKER
```

> 🔑 **Y el hallazgo que vale para cualquier proyecto que no cargue**: el mensaje
> `Failed to restore project. "ProjectTool PREFABS RESTORE" exited with code 1` **es genérico** —
> significa «no pude cargar el proyecto», no que falten prefabs. `resourcetool` no sabe decirte
> más. **Compila** (sin `--errors-only`) y te da archivo, línea y el enlace que no resuelve:
>
> ```
> │  Cannot load project because linking failed with the following errors:
> │  /Users/…/ImpTest.yyp(31,49): Cannot resolve link 'ImpTest.yyp : shp_1' in user's project.
> ```

### Trampa 15 · 🔴 `cache clean --project` borra también la caché COMPARTIDA

El flag dice `--project`. Suena acotado al proyecto. **No lo está**: se lleva por delante
`~/Library/Caches/GameMakerCLI`, donde viven los *runtimes* descargados, y el siguiente `compile`
tiene que bajarse `runtimes-gms2` entero otra vez.

```console
$ gm-cli cache clean --project "…/MiJuego.yyp"
Shared cache
/Users/…/Library/Caches/GameMakerCLI
Cleaned                       ← los runtimes, borrados

Local cache
/Users/…/MiJuego/.gmcache
Cleaned
```

Comprobado después: la carpeta había desaparecido de verdad. La única forma de limpiar **solo** lo
local es `--cache-dir` apuntando a la caché del proyecto, que sí respeta la compartida
(`Shared cache … Skipped`).

**Para un agente**: no ejecutes `cache clean` para «arreglar» un problema de compilación sin
avisar al usuario de que le vas a costar una descarga larga. Y si lo haces, usa `--cache-dir`.

---

## 0 bis · Qué vía usar para cada cosa: CLI → MCP → computer use → humano

**Antes del ciclo de trabajo, la decisión de arquitectura.** Un agente tiene cuatro vías para
tocar un proyecto de GameMaker, y elegir mal cuesta horas. El orden no es negociable, y el
motivo de cada peldaño importa más que el peldaño.

### 1º · El CLI oficial, siempre que llegue

`gm-cli` y su `resourcetool` son la vía por defecto: oficial, determinista, guionizable, sin
proceso aparte, y **es lo que esta biblioteca tiene verificado comando a comando**
([§3 bis](#3-bis--construir-el-juego-entero-por-cli-qué-se-escribe-de-verdad)). Con él se
construye un juego entero: recursos, eventos, salas, capas, cámaras, viewports, físicas de sala,
tilesets, tilemaps desde CSV, orígenes de sprite, renombrados, compilación y empaquetado.

### 2º · El MCP oficial — que NO es un escalón por encima, es el mismo motor

> 🔑 **El error de arquitectura más común: creer que el MCP puede más que el CLI.** El MCP
> `gamemaker-resource-tool` **es el mismo ResourceTool**, expuesto como herramientas en vez de
> como línea de comandos. No desbloquea nada nuevo — y de hecho tiene **menos**: le faltan cinco
> operaciones que `eval` sí tiene ([§3.1](#31-lo-que-el-mcp-no-tiene-y-resourcetool-eval-sí)).
>
> Se usa por **comodidad**, no por capacidad: llamadas tipadas en vez de construir cadenas. Si
> algo no se puede por CLI, tampoco se puede por el MCP oficial. Buscar ahí la solución es
> perder el tiempo.

Los MCP de **terceros** sí hacen más que el CLI, pero al precio de escribir directamente sobre
los `.yy` en vez de pasar por el ResourceTool — con lo que eso implica
([`07 · 14`](../07%20-%20Ecosistema/14%20-%20IA%20y%20GameMaker.md)).

### 3º · Computer use, para lo que es exclusivo del IDE

Aquí está el cambio de fondo: **hay una lista corta y concreta de operaciones que el CLI no hace
y que hasta ahora terminaban en «pídeselo al humano».** No son un misterio ni una limitación
difusa — están medidas, una por una, en este mismo documento:

| Operación | Por qué el CLI no llega | Dónde está medido |
|---|---|---|
| **Rasterizar los glifos de una fuente** | Es trabajo del editor; el `.yy` se queda con `"glyphs":{}` pase lo que pase | Trampa 5 |
| **Versión del ejecutable, nombre de producto, copyright, NSIS…** | 25 de las 30 propiedades de plataforma son de solo lectura | Trampa 10 |
| **Variable Definitions de un objeto** | 3 variantes probadas, ninguna | [§3 bis.6](#3-bis6-los-límites-reales-para-que-no-pierdas-el-tiempo) |
| **`nineSlice` de un sprite** | 3 variantes | §3 bis.6 |
| **Mover un recurso a otra carpeta del Asset Browser** | 8 variantes, y `ProjectTool IMPORT YY` tampoco | §3 bis.6 · §3 ter.1 |
| **Anidar una capa de sala dentro de otra** | `PARENT=` dice «Saved successfully» y la deja en la raíz | §3 bis.6 |
| **Código de creación de una instancia** | Un `=` dentro de `value=` rompe el parser | §3 bis.6 |
| **Crear un asset de Extensión** | `Resource type 'extension' is not creatable` | Prohibiciones de la skill |
| **Flex Panels / UI Layers complejos** | Es un editor visual | §10 de este documento |

**Todas esas son operaciones de interfaz gráfica.** Un agente con control del escritorio —en este
equipo, *Codex Computer Use*— puede abrir el IDE y hacerlas: son clics en diálogos, no juicios
humanos. Eso convierte «pídeselo al humano» en «hazlo tú, con más cuidado».

> ⚠️ **Y con más cuidado de verdad.** Computer use no tiene las garantías del CLI: no hay código
> de salida que leer, la interfaz cambia entre versiones, y un clic mal puesto en el IDE toca el
> proyecto sin dejar rastro. Antes de usarlo: **haz copia del proyecto**, y después **verifica el
> resultado por CLI** —`options get`, `resource info`, `font glyphlist`— en vez de fiarte de lo
> que se vio en pantalla. La regla de leer siempre de vuelta vale aquí el doble.

> 🔎 **Estado de esta afirmación, dicho con la misma vara que el resto del documento.** Lo de
> arriba es **razonado, no medido**: la lista de nueve operaciones sí está verificada una a una
> con sus variantes, y *Codex Computer Use* está instalado en este equipo (comprobado el
> 09-09-2026 en `~/.codex/computer-use/`), pero **nadie de este proyecto ha ejecutado ninguna de
> las nueve conduciendo el IDE**. Que sean diálogos y no juicios humanos hace el argumento
> sólido; no lo convierte en una prueba.
>
> **Lo que lo convertiría en prueba**, y es el orden en que conviene intentarlo —de menos a más
> riesgo—: hornear los glifos de una fuente (Trampa 5) sobre un proyecto de usar y tirar, y
> comprobar el resultado con `font glyphlist`, que devuelve el diccionario vacío o lleno sin
> ambigüedad. Si eso funciona, el resto de la lista es la misma mecánica. Hasta entonces, trátalo
> como una vía **plausible y sin rodar**, no como una garantía.

### 4º · El humano, solo para lo que depende de sus sentidos o de su cuenta

Lo que queda tras los tres peldaños anteriores es corto y no lo resuelve ninguna herramienta:
**si se ve bien, si se oye bien, si se siente bien**, el rendimiento en hardware real, y todo lo
que exija una cuenta o una firma suya (tiendas, certificación, claves). La tabla está en
[§4.2](#42-lo-que-un-agente-no-puede-comprobar-por-sí-solo--pídeselo-al-humano) — y conviene
releerla sabiendo que ahora es **más corta de lo que era**: lo que es «abrir un diálogo y
rellenar un campo» ya no pertenece a esa lista.

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
| 5 | **Compilar** | `gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only` (solo para iterar rápido — ver la nota debajo de la tabla) | Sintaxis válida — **NO** que las funciones existan (Trampa 4) | `exit 0` **y** sin salida en `--errors-only` |
| 6 | **Validar antes de confiar en el paso 5** | `python3 "_indice/validar-proyecto.py" <ruta> --todo` | Funciones inventadas (con prefijo de familia del runtime) **y** nombres desconocidos sin definir | `✓ Ninguna llamada a una función del runtime que no exista` **y** la lista de «desconocidas» revisada a mano (ver matiz en [§7](#7--interpretar-los-errores-del-compilador--lo-que-detecta-y-lo-que-no)) |
| 7 | **Corregir** | Vuelve al paso 4 con el error exacto: `gml_Object_<obj>_<Evento>(<línea>) : <mensaje>` | — | Repite 5-6 hasta limpio |
| 8 | **Ejecutar** | `gm-cli run --toolchain GMS2@2026.0.0.23 --target mac` (o el target de tu plataforma) | Comportamiento real — ver [§4](#4--depurar-sin-ver-la-pantalla) para qué puedes leer de la salida | El juego llega al punto que estás probando sin errores no controlados en el log |
| 9 | **Limpiar** | Mata el proceso del *runner* por nombre tras cada `run` de depuración (§4) | Que no queden procesos huérfanos | `ps -ef \| grep -i runner` no devuelve nada tuyo |
| 10 | **Iterar** | Vuelve al paso 3 o 4 según qué falte | — | El sistema de la receta del paso 1 está completo |
| 11 | **¿Es un juego?** | `python3 "_indice/auditar-juego-completo.py" <ruta>` | Qué piezas del envoltorio NO aparecen: menú, opciones, pausa, guardado, créditos, fin de partida, sonido, mando, arranque por portada, y objetos sin sprite que pintan rectángulos | `exit 0`, o cada ✗ justificado por escrito |

**Nunca dos pasos a la vez.** El error más caro de un agente en este ciclo es escribir GML para
tres sistemas y compilar una sola vez al final: el primer error de sintaxis oculta los otros
dos, y el mensaje `gml_Object_<obj>_<Evento>(<línea>)` solo apunta al primero que encuentra el
compilador, no a todos los que hay.

> ⚠️ **`--errors-only` sirve para iterar rápido en el paso 5 — no para la última compilación
> antes de dar la tarea por terminada.** Silencia los `WARNING`, y al menos uno de ellos es un
> fallo real y no cosmético: un *included file* creado por `resourcetool` cuyo archivo nunca
> llegó al paquete compilado (Trampa 8 de [§0](#0--las-quince-trampas-que-hacen-fracasar-a-un-agente-hoy)).
> **Antes de cerrar una tarea, compila al menos una vez sin el flag** y lee la salida completa —
> ver el checklist de [§8](#8--checklist-final-antes-de-dar-una-tarea-por-terminada).

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

> ❌ **Afirmación anterior, falsa — corregida el 8 de septiembre de 2026 (Trampa 9):** esta
> misma sección decía que «no existe forma de forzar el número real (74, 75) por `resourcetool`»
> y que «hoy no hay manera de crear un GUI Begin/End real por CLI o MCP». La whitelist de
> `subtype=` en `OBJECT EVENT FINDORCREATE` es cerrada, en efecto — pero **no es la única vía**.
> El campo crudo `eventNum` del evento ya creado **sí se puede escribir** con `RESOURCE SET`
> (la misma raíz de expresión genérica de la Trampa 7, aplicada a un evento en vez de a
> `project`). Receta verificada de punta a punta (creación, parcheo y `gm-cli compile` con
> salida `Compilation finished`) en [§9 ter](#9-ter--forzar-un-eventnum-real-cuando-la-whitelist-de-subtype-es-cerrada).

### 2.4 Other: tabla completa, con los dos bugs marcados

Verificado igual que Draw, con los 14 subtipos que acepta la whitelist de `resourcetool` (los
eventos Async — HTTP, Save/Load, Steam, Cloud, redes — no están en esta lista, y ni por nombre
ni forzando el número real como `subtype` los acepta `OBJECT EVENT FINDORCREATE`: `type=other
subtype=62` da `Invalid subtype`).

> ❌ **Esto NO significa que los eventos Async no se puedan crear por CLI ni MCP** — una
> afirmación repetida en varias versiones de este documento y **falsa**, corregida el 8 de
> septiembre de 2026: `FINDORCREATE` tiene la whitelist cerrada, pero el `eventNum` crudo del
> evento sí se puede forzar con `RESOURCE SET` una vez creado. Ver [§9 ter](#9-ter--forzar-un-eventnum-real-cuando-la-whitelist-de-subtype-es-cerrada)
> para la receta completa — incluye un evento **Async - HTTP** (62) real, reconocido después
> como `Event_Async_HTTP` por el propio `resourcetool`, y compilado sin error.

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

> `user1` a `user15` **existen en GameMaker real** y `OBJECT EVENT FINDORCREATE` los rechaza: la
> whitelist de `other` se cierra en `user0`. ❌ **Una versión anterior de esta nota decía que por
> eso «necesitas crearlos desde el IDE» — falso, corregido el 8 de septiembre de 2026.** Crea
> `user0` (`eventNum=10`) por CLI/MCP como siempre y fuerza `eventNum=11` (`user1`), `12`
> (`user2`)… con `RESOURCE SET` — verificado con `user1`: `resourcetool` vuelve a listarlo como
> `Event_Other_UserN` (detalle `1`). Receta en [§9 ter](#9-ter--forzar-un-eventnum-real-cuando-la-whitelist-de-subtype-es-cerrada).

### 2.5 La regla de oro para no caer en las dos trampas anteriores

**Después de cualquier `object event findorcreate` en `draw` u `other`, verifica**:

```bash
gm-cli resourcetool eval "object event list name=<objeto>"
```

Si el resultado no muestra el subtipo exacto que pediste (por ejemplo, pediste `gui_begin` y la
tabla solo lista `Event_Draw_DrawBegin`), el evento se coló en el archivo equivocado. Dos
salidas, no una sola: bórralo y edítalo desde el IDE si te vale con eso, **o fuerza el número
real con `RESOURCE SET` sobre `eventNum`** ([§9 ter](#9-ter--forzar-un-eventnum-real-cuando-la-whitelist-de-subtype-es-cerrada))
si necesitas el evento real sin salir del CLI/MCP — no des el segundo camino por cerrado sin
haberlo probado (Trampa 9).

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

## 3 bis · Construir el juego entero por CLI: qué se escribe de verdad

La Trampa 7 dice «antes de dar un comando por imposible, prueba `resource info expr=project`».
Esta sección es el resultado de aplicar esa regla **a todo el árbol**, propiedad por propiedad,
el 08-09-2026 (`gm-cli` 2.3.0 / `ResourceTool@2026.0.17`). Lo de abajo **devolvió
`Saved successfully` de verdad**; el informe completo, con los tipos que no caben aquí, está en
[`_indice/auditorias/r12-cli-exhaustivo.md`](../_indice/auditorias/r12-cli-exhaustivo.md).

### 3 bis.1 Las tres reglas del árbol de expresiones

1. **Una lista se indexa por número con corchete normal, y por nombre con COMILLA SIMPLE.**
   `rm_test.layers['Background']` funciona; `rm_test.layers["Background"]` **falla**, aunque la
   propia ayuda del comando anuncie la comilla doble. Es un bug de la ayuda, no tuyo.
2. **Las listas enteras son de solo lectura.** `rm.layers`, `rm.views`, `obj.eventList`,
   `path.points` no se asignan de golpe: se escribe **elemento a elemento**.
3. **`FullName` nunca se escribe.** Para renombrar, `name` (ver §3 bis.5).

### 3 bis.2 La sala entera: tamaño, cámaras, físicas y capas

Nada de esto estaba documentado, y es justo lo que hace falta para montar un nivel sin abrir el
IDE.

```bash
R='gm-cli resourcetool eval'

# Tamaño y persistencia
$R "resource set expr=rm_nivel1.roomSettings.Width value=640"
$R "resource set expr=rm_nivel1.roomSettings.Height value=360"
$R "resource set expr=rm_nivel1.roomSettings.persistent value=true"

# Viewports y cámaras: los OCHO, enteros
$R "resource set expr=rm_nivel1.viewSettings.enableViews value=true"
$R "resource set expr=rm_nivel1.views[0].visible value=true"
$R "resource set expr=rm_nivel1.views[0].wview value=320"
$R "resource set expr=rm_nivel1.views[0].hview value=180"
$R "resource set expr=rm_nivel1.views[0].wport value=1280"
$R "resource set expr=rm_nivel1.views[0].hport value=720"
$R "resource set expr=rm_nivel1.views[0].hborder value=96"    # zona muerta horizontal
$R "resource set expr=rm_nivel1.views[0].objectId value=obj_jugador"   # a quién sigue

# Mundo de físicas de la sala
$R "resource set expr=rm_nivel1.physicsSettings.PhysicsWorld value=true"
$R "resource set expr=rm_nivel1.physicsSettings.PhysicsWorldGravityY value=10"
$R "resource set expr=rm_nivel1.physicsSettings.PhysicsWorldPixToMetres value=0.1"

# Capas — el TIPO va en MAYÚSCULAS
$R "room layer create room=rm_nivel1 name=Suelo type=TILE"
$R 'room layer create room=rm_nivel1 name=Frente type=INSTANCE depth="INDEX 2"'
$R "resource set expr=rm_nivel1.layers['Frente'].visible value=true"

# El fondo, por nombre de capa (¡comilla simple!)
$R "resource set expr=rm_nivel1.layers['Background'].colour value=4283782485"
$R "resource set expr=rm_nivel1.layers['Background'].htiled value=true"

# Instancias, y sus transformaciones
$R "room instance create room=rm_nivel1 object=obj_jugador name=inst_p1 layer=Instances x=100 y=200"
$R "resource set expr=inst_p1.scaleX value=2"
$R "resource set expr=inst_p1.rotation value=45"
```

> 💡 **Qué es `INDEX n`, que el `HELP` no explica.** El argumento acepta `FRONT`, `BACK` o
> `INDEX n`, y ese `n` **no es el `depth` de GameMaker: es la posición en la lista de capas**.
> GameMaker asigna el `depth` él solo después, en saltos de 100 siguiendo ese orden. Verificado
> creando tres capas con `INDEX 0`, `1` y `2` sobre una sala nueva y leyendo el `.yy`:
>
> ```
> Capa0 → depth 0     Capa1 → depth 100    Capa2 → depth 200
> Instances → 300     Background → 400
> ```
>
> Es decir: **las capas nuevas se colocan delante** (menos `depth` = se dibuja encima), y las que
> traía la plantilla se van hacia atrás. Para una capa detrás de todo, `BACK`.

> ⚠️ **`ROOM ASSET CREATE` ignora `LAYER=` si la capa no existe** — y no avisa: se inventa una
> (`layer3`, `layer6`…). Verificado con tres variantes. `ROOM INSTANCE CREATE` sí respeta el
> nombre. **Crea antes la capa de tipo `ASSET`.**
>
> ⚠️ **`effectType` de una capa es escribible y es una bomba.** Poner `_filter_tintfilter` hace
> que el proyecto exija resolver un paquete del registro, y con el `gmpm.dll` de fábrica eso lo
> deja ilegible entero (Trampa 1). No lo toques salvo que hayas aplicado el rodeo.

### 3 bis.3 Tilesets y tilemaps — incluido importar un CSV

```bash
$R "sprite addframe name=spr_tiles path=/ruta/tiles.png"
$R "tileset create name=ts_mundo sprite=spr_tiles tilewidth=32 tileheight=32"
```

> ⚠️ **`TILESET CREATE` deja `tile_count` y `out_columns` a 0** aunque le des sprite y medidas.
> Hay que fijarlos a mano — los dos son escribibles — o el tileset no sirve para nada.

```bash
$R "resource set expr=ts_mundo.tile_count value=48"
$R "resource set expr=ts_mundo.out_columns value=8"
$R "resource set expr=rm_nivel1.layers['Suelo'].tilesetId value=ts_mundo"

$R "room layer tiles resize room=rm_nivel1 layer=Suelo width=20 height=12"
$R "room layer tiles set room=rm_nivel1 layer=Suelo left=0 top=0 width=3 height=2 data=1,2,3,4,5,6"
$R "room layer tiles set room=rm_nivel1 layer=Suelo file=/ruta/mapa.csv left=0 top=0"
$R "room layer tiles get room=rm_nivel1 layer=Suelo"
```

**`FILE=` acepta un CSV**, que es la vía natural para meter un mapa hecho en Tiled o generado por
un script. (`ROOM LAYER TILES INFO` no imprime nada; el desglose de bits sale como cabecera de
`TILES GET`.)

### 3 bis.4 Origen y animación de un sprite

```bash
# Animación
$R "resource set expr=spr_jugador.sequence.playbackSpeed value=12"
$R "resource set expr=spr_jugador.sequence.playbackSpeedType value=FramesPerSecond"

# Origen — en PÍXELES, no el desplegable
$R "resource set expr=spr_jugador.sequence.xorigin value=16"
$R "resource set expr=spr_jugador.sequence.yorigin value=47"
$R "resource set expr=spr_jugador.origin value=9"      # 9 = «Custom» en el IDE, cosmético
```

> 🔴 **`origin` NO mueve el origen: es el desplegable del IDE, y escribirlo solo no hace nada.**
> Verificado el 09-09-2026 sobre un sprite de 32×48 recién creado:
>
> ```console
> $ resource set expr=spr_i.origin value=4     # 4 = «Middle Centre»
> Saved successfully
> $ grep origin sprites/spr_i/spr_i.yy
> "origin":4  "xorigin":0  "yorigin":0         ← el centro sería 16,24
> ```
>
> El preset se guarda y **las coordenadas reales se quedan donde estaban**: solo el IDE las
> recalcula al elegir en el desplegable. Lo que lee el runtime es `sequence.xorigin` /
> `sequence.yorigin`, en píxeles. Escribe **esos dos**, y deja `origin` en `9` («Custom») para
> que el IDE no te lo pise si alguien abre el proyecto.
>
> **No es un detalle cosmético.** En un cenital, el origen a los pies es el sistema de
> profundidad entero (`depth = -y`); en un plataformas, decide dónde aterriza el personaje y
> dónde cae su sombra. Un origen en `0,0` con «Saved successfully» de por medio es de los fallos
> que más tardan en atribuirse a su causa. Otro caso de la regla:
> **léelo de vuelta del `.yy`.**

### 3 bis.5 Renombrar un recurso — y sí, actualiza las referencias

```bash
$R "resource set expr=obj_viejo.name value=obj_nuevo"
```

Verificado: cambia también quien lo referenciaba (el sprite de un objeto, el objeto de una
instancia de sala). La biblioteca solo documentaba `RENAME` para tileset, grupo de audio, grupo de
textura y configuración; para todo lo demás, esta es la vía.

### 3 bis.6 Los límites reales, para que no pierdas el tiempo

Cada uno probado con varias variantes antes de darlo por imposible:

| Lo que querrías | Estado | Rodeo |
|---|---|---|
| Un `=` dentro de un `value=` | 🔴 **rompe el parser** en `eval`, `script` y `repl` (9 variantes). Guarda solo hasta el `=`, y el único aviso son unas líneas `Ignoring Argument:` fáciles de pasar por alto: `value=vida = 100;` deja `scriptSource = vida` | El código de creación de una instancia **no se escribe por CLI**. Ponlo en el evento Create del objeto |
| Mover un recurso ya creado a otra carpeta | 🔴 8 variantes, ninguna | **Ninguno.** `ProjectTool IMPORT YY` tampoco: dice que sí y no registra nada ([§3 ter.1](#3-ter1--import-yy-dice-que-funciona-copia-archivos-y-no-registra-nada)). Decide la carpeta **al crear** el recurso |
| Anidar una capa dentro de otra | 🔴 `PARENT=` responde «Saved successfully» y la deja en la raíz | — |
| *Variable Definitions* de un objeto | 🔴 3 variantes | Declara las variables en el evento Create |
| El `nineSlice` de un sprite | 🔴 3 variantes | El IDE |
| Crear un recurso `shape` | 🔴 **rompe el proyecto** | Trampa 14. No lo hagas |

> 💡 **Y una corrección**: `12 · 09` §9 bis decía que `projectpath=` «no funciona para
> `RESOURCE INFO`/`RESOURCE SET` en general». **Es falso.** `PROJECTPATH` figura en la sección
> *Global Arguments* de `HELP` y funciona en **cualquier** comando — útil para operar sobre un
> proyecto sin `cd` a su carpeta.
>
> Y el auto-relleno de `[0]` **no es exclusivo de `emitters`**: `animcurve.channels[0].name`
> también crea el elemento al escribirlo. `timeline.momentList`, en cambio, no.

---

## 3 ter · `ProjectTool`: la segunda herramienta que nadie documenta

En el `.gmcache` de **todo** proyecto, junto al `ResourceTool` que usa esta biblioteca, vive un
binario aparte con capacidades propias que ningún documento —oficial ni de aquí— menciona:

```bash
PT="$(find .gmcache/project-tool -name ProjectTool -type f | head -1)"
"$PT"                                    # sin argumentos: imprime la ayuda completa
"$PT" JSON FORMAT "INPUT=MiJuego.yyp" "COMMAS=GAMEMAKER"
```

**Se invoca con los argumentos directos**, como el `ResourceTool` cacheado de la Trampa 2 — no
con un subcomando `cli`: `"$PT" cli "<comando>"` abre una sesión **interactiva** y se queda
colgado esperando por *stdin*. Para varios comandos seguidos, `"$PT" SCRIPT "PATH=<archivo>"`.

Versión comprobada: **`ProjectTool - Version 2026.0.174`** (distinta de la del `ResourceTool`,
que es `2026.0.17`).

| Familia | Qué hace | Estado comprobado el 09-09-2026 |
|---|---|---|
| `JSON FORMAT` | Normaliza un `.yy`/`.yyp` al formato exacto de GameMaker (`COMMAS=GAMEMAKER`, el valor por defecto, o `STANDARD` para JSON normal) | ✅ útil para reparar un archivo tocado a mano |
| `PROJECT NEW/OPEN/CLOSE/SAVE` | Crear, abrir, cerrar y guardar un proyecto en memoria | — |
| `EXPORT` | Genera `.yymps` de Marketplace, prefab, proyecto o ZIP. Con `INCLUDEFOLDERS`/`EXCLUDERESOURCES`, icono, y firma con certificado | — |
| `SIGNING CREATE/PACKAGE/VERIFY/VALIDATE` | Firmar y validar un paquete de Marketplace con certificado | — |
| `LINKS GET/APPLY/CHANGE/LIST/LIBS/FREQUENCY/NULL` | **Enlaces de *prefabs*** (no de recursos en general): listarlos, cambiar de versión, anular los rotos | — |
| `PREFABS RESTORE` | Resolver los prefabs del proyecto — es lo que falla con el `gmpm.dll` desparejado de la Trampa 1 | 🔴 roto de fábrica |
| `FILE CHANGEVERSION` | Cambiar la versión de un `.yy`/`.yyp` en formato *versioned* | — |
| `SHOWVERSIONEDTYPES` | Volcar la lista de clases de recurso y versión que conoce esta build | — |
| **`IMPORT YY`** | Copiar recursos de un proyecto a otro | 🔴 **NO FUNCIONA — ver abajo** |

> ⚠️ **`READONLY=TRUE` es el valor por defecto.** Si esperas que guarde y no guarda, empieza por
> ahí: hay que pasar `READONLY=FALSE` explícitamente.

### 3 ter.1 🔴 `IMPORT YY` dice que funciona, copia archivos y no registra nada

> ❌ **Corrección del 09-09-2026.** La versión anterior de esta sección presentaba `IMPORT YY`
> como «copiar recursos entre proyectos ✅ (verificado, el destino compila)» y lo ofrecía como
> el rodeo para mover un recurso de carpeta. **Ninguna de las dos cosas es cierta.** La
> afirmación venía de una auditoría que lo dio por bueno porque el proyecto destino compilaba —
> y compilaba precisamente **porque no se había importado nada**. Es el error que esta misma
> biblioteca documenta en la Trampa 4, aplicado a sí misma: *compilar limpio no prueba que algo
> haya pasado; a veces prueba justo lo contrario*.

Lo que hace de verdad, probado con **tres variantes** el 09-09-2026 sobre proyectos recién
creados:

```console
$ "$PT" IMPORT YY "SOURCES=…/verif3bis/scripts/scr_util/scr_util.yy" \
        "DESTINATION=…/destino/destino.yyp" "READONLY=FALSE"
Found Project - …/verif3bis/verif3bis.yyp - for resource - …/scr_util/scr_util.yy
..Success
Core Resources : Debug Info - Adding resource: scr_util to destino
ProjectTool Successful                      ← dice que sí

$ grep -c scr_util destino/destino.yyp
0                                           ← no está en el .yyp

$ gm-cli resourcetool eval "resource list type=script"
 script
ResourceTool Successful                     ← la lista, vacía

$ ls destino/scripts/
scr_util                                    ← pero la carpeta SÍ está en disco
```

**Lo peor no es que falle: es que deja basura silenciosa.** La carpeta del recurso queda en el
disco del proyecto destino y GameMaker la ignora por completo, porque lo que manda es el `.yyp`.
Nadie te avisa, y en un proyecto grande esas carpetas huérfanas se acumulan.

Las tres variantes probadas, todas con el mismo resultado (`0` en el `.yyp`):

1. `IMPORT YY` con `DESTINATION=`, invocación directa.
2. `IMPORT YY` con `DESTINATION=` seguido de `PROJECT SAVE DESTINATION=…` en un `SCRIPT`.
3. `PROJECT OPEN` → `IMPORT YY` sin `DESTINATION` → `PROJECT SAVE`, en un `SCRIPT`.

Y si el recurso que importas **referencia otro que no existe en el destino** —un objeto con su
sprite, el caso normal— no es que no registre: **revienta** con
`Fatal error. System.AccessViolationException: Attempted to read or write protected memory`
dentro del cargador de archivos. Reintentado tres veces; no es la Trampa 11.

**Qué hacer entonces.** Para llevar recursos de un proyecto a otro, hoy: el IDE
(*Local Package* → importar), o copiar la carpeta a mano **y** registrar el recurso con
`resource create` + `resource set` en el destino, que es lo que `IMPORT YY` debería hacer y no
hace. Para **mover un recurso a otra carpeta del Asset Browser** no hay ninguna vía por CLI:
lo que decía esta sección era falso, y el límite de
[§3 bis.6](#3-bis6-los-límites-reales-para-que-no-pierdas-el-tiempo) es real y sin rodeo.

> 🔑 **La lección que deja, y que vale para cualquier comando de esta familia**: `Successful`,
> `Saved successfully` y un `exit 0` **no son verificación**. Ya lo eran `OPTIONS SET`
> truncando un nombre en el primer espacio (Trampa 10) y el *included file* que nunca llegaba al
> paquete (Trampa 8). **Lee siempre el `.yyp` o el `.yy` después de escribir**, o pídeselo de
> vuelta a `resource info` / `resource list`. Esta sección existe porque no se hizo.

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

> ❌ **Esta tabla tenía una fila más** («Un evento Async que no se puede crear por CLI/MCP,
> pídeselo al humano») **quitada el 8 de septiembre de 2026: era falsa** y además no encajaba
> aquí — crear un evento no depende de un sentido humano, y sí se puede hacer sin salir del
> CLI/MCP. Ver [§9 ter](#9-ter--forzar-un-eventnum-real-cuando-la-whitelist-de-subtype-es-cerrada)
> (Trampa 9).

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

> ⚠️ **Con más de una sesión de agente activa en el mismo Mac, `pkill -f Mac_Runner` es
> demasiado ancho: mata TODOS los runners, no solo el tuyo.** Verificado en
> [`_indice/auditorias/r7-prueba-movil.md` §7](../_indice/auditorias/r7-prueba-movil.md#7--limpieza):
> dos sesiones distintas pueden tener cada una su propio `Mac_Runner` corriendo a la vez, ambos
> con el mismo título de ventana literal `${project_name}` y, por defecto, la misma posición en
> pantalla — indistinguibles a simple vista, así que una captura o un clic pensados para tu
> juego pueden aterrizar en la ventana del otro. Aísla tu propio proceso por el argumento
> `-game <ruta-a-tu-proyecto>` de `ps aux`, y mata solo ese PID, no el nombre del runner entero:
> ```bash
> ps aux | grep -- "-game .*/mi-juego/" | grep -v grep   # localiza SOLO tu proceso
> kill <PID>                                              # nunca pkill -f Mac_Runner a ciegas
> ```

---

## 5 · Assets sin artista

### 5.1 Audio

Ya resuelto, con la escalera de prioridad completa (síntesis en runtime → generador externo →
`PLACEHOLDERS.md`) y el catálogo mínimo de sonidos sintetizables, en
[`13 · 09` §8 bis](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/09%20-%20Dise%C3%B1o%20de%20sonido%20y%20mezcla.md#8-bis--un-agente-sin-archivo-de-audio-la-escalera-de-prioridad).
No se repite aquí.

### 5.2 Gráfico: la escalera de prioridad, sin el rectángulo plano

La pregunta es la misma que en audio (§5.1): «necesito un sprite AHORA MISMO, sin artista —
¿qué hago sin salir de la biblioteca?». La respuesta comparte el patrón de `PLACEHOLDERS.md`
descrito en
[`13 · 11` §5](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/11%20-%20Producci%C3%B3n%2C%20alcance%20y%20lanzamiento.md#5--assets-y-pipeline),
pero **la versión anterior de esta sección recomendaba un cuadrado de un solo color
(`magick -size 64x64 xc:"#ff3366"`) como si fuera un peldaño intermedio digno.** No lo es: es
exactamente la «basura en SVG o lo que sea» que un agente debe evitar, solo que en PNG. Se
sustituye por una escalera real, verificada en vivo en esta sesión en
`~/gm_prueba_assets` (creado y borrado al terminar).

> 🔴 **La regla que gobierna las tres alternativas de abajo: en ningún caso se entrega un
> rectángulo o un cuadrado de color plano como sprite final de un personaje, un enemigo o
> cualquier objeto con el que el jugador interactúa.** Un óvalo con dos tonos y un contorno de
> 1 px cuesta exactamente el mismo número de líneas que un rectángulo liso, y se lee mil veces
> mejor — ver la comparación en la tabla de «calidad mínima exigible» más abajo.

#### Peldaño 0 — Sin sprite, solo para volúmenes de lógica pura

Para una zona de disparo, un trigger o una caja de depuración que **nunca representa un
personaje ni un enemigo**, seguir dibujando con `draw_rectangle`/`draw_circle` directamente en
el evento Draw sigue siendo válido y es el patrón habitual de varias recetas de `13/02`: cero
archivos, cero sprite. En cuanto el objeto tiene identidad visual propia (jugador, enemigo,
objeto, proyectil), pasa al peldaño 1.

> ⚠️ **Si el objeto va a usar colisión estándar (`place_meeting()`, `instance_place()`,
> `instance_position()`…), no se queda en el peldaño 0** — verificado en
> [`_indice/auditorias/r6-regresion.md` §7](../_indice/auditorias/r6-regresion.md#7--hallazgo-nuevo-propio-no-de-la-biblioteca-pero-instructivo--colisión-sin-sprite):
> una instancia sin `sprite_index` asignado no tiene máscara de colisión, así que esas funciones
> **nunca la encuentran**, aunque esté dibujando algo y esté exactamente donde se la busca. Es un
> comportamiento de GML, no de esta biblioteca — detalle completo, verificado contra el manual
> oficial, en
> [`01 · 08` §9](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md#9-errores-típicos).
> El peldaño 1 de abajo sí genera un sprite real (`sprite_create_from_surface()`), así que no
> tiene este problema — la trampa solo alcanza a quien se queda dibujando a mano en el peldaño 0
> y luego reutiliza colisión estándar sobre ese objeto.

#### Peldaño 1 — Dibujo por código con criterio

El objetivo no es «un PNG», es una **silueta reconocible**: cabeza, cuerpo y extremidades
diferenciados, con la paleta de dos tonos + contorno que ya exige `13 · 03 §2` para el resto
del arte del juego, y el origen marcado en el punto real (pies de un personaje, centro de un
proyectil). Dos formas de conseguirlo, ambas verificadas en esta sesión — usa la que encaje con
si el objeto necesita máscara de colisión ahora mismo o solo un archivo de partida:

**(a) En tiempo de ejecución, sin salir de GameMaker** — para cuando el propio juego debe
generarse su placeholder al arrancar. Símbolos verificados con `buscar.py`:
`surface_create`, `surface_set_target`, `surface_reset_target`, `surface_free`,
`draw_clear_alpha`, `draw_circle_color`, `draw_ellipse_color`, `draw_rectangle`,
`draw_set_color`, `sprite_create_from_surface`, `make_color_rgb`.

```gml
/// @function generar_placeholder_silueta(_ancho, _alto, _col_claro, _col_oscuro)
/// @description Genera un sprite real (con mascara de colision) de una figura biped simple
///              -cabeza + torso + piernas-, con paleta de dos tonos y contorno, y el origen
///              en los pies. Devuelve el sprite (handle), listo para sprite_index.
function generar_placeholder_silueta(_ancho, _alto, _col_claro, _col_oscuro)
{
    var _surf = surface_create(_ancho, _alto);
    surface_set_target(_surf);
    draw_clear_alpha(c_black, 0);

    var _cx        = _ancho * 0.5;
    var _r_cabeza   = _ancho * 0.28;
    var _y_cabeza   = _r_cabeza + 1;
    var _y_torso0   = _y_cabeza + _r_cabeza * 0.75;
    var _y_torso1   = _alto * 0.72;

    // cabeza: relleno + contorno de 1 px
    draw_circle_color(_cx, _y_cabeza, _r_cabeza, _col_claro, _col_claro, false);
    draw_circle_color(_cx, _y_cabeza, _r_cabeza, c_black, c_black, true);

    // torso: ovalo relleno + contorno
    draw_ellipse_color(_cx - _ancho * 0.35, _y_torso0, _cx + _ancho * 0.35, _y_torso1, _col_oscuro, _col_oscuro, false);
    draw_ellipse_color(_cx - _ancho * 0.35, _y_torso0, _cx + _ancho * 0.35, _y_torso1, c_black, c_black, true);

    // piernas: dos rectangulos solidos
    draw_set_color(_col_oscuro);
    draw_rectangle(_cx - _ancho * 0.28, _y_torso1 - 2, _cx - _ancho * 0.05, _alto - 1, false);
    draw_rectangle(_cx + _ancho * 0.05, _y_torso1 - 2, _cx + _ancho * 0.28, _alto - 1, false);
    draw_set_color(c_white);

    surface_reset_target();

    // origen en el centro-x, a la altura de los pies (ultima fila)
    var _spr = sprite_create_from_surface(_surf, 0, 0, _ancho, _alto, false, false, _cx, _alto - 1);
    surface_free(_surf);
    return _spr;
}
```

Verificado de punta a punta en esta sesión: un objeto de prueba lo llama en su Create
(`sprite_index = generar_placeholder_silueta(32, 48, make_color_rgb(109,156,214),
make_color_rgb(58,92,138));`), `gm-cli compile --errors-only` da `exit 0`, y `gm-cli run` +
`screen_save()` produjo una captura real con la figura biped completa y el marcador de origen
exactamente en los pies — no una hipótesis, una comprobación con la imagen delante.

**(b) Por CLI, cuando el asset debe existir como archivo** — con Pillow (más control por forma)
o ImageMagick (una sola línea). Verificado generando y **abriendo el PNG resultante** en esta
sesión, ampliado ×8 sobre fondo gris para juzgarlo a conciencia:

```python
# Pillow — silueta biped completa, dos tonos + contorno + resalte de volumen
from PIL import Image, ImageDraw

W, H = 32, 48
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

col_claro    = (109, 156, 214, 255)
col_oscuro   = (58, 92, 138, 255)
col_contorno = (23, 34, 51, 255)

d.ellipse([10, 2, 21, 13], fill=col_claro, outline=col_contorno, width=1)                 # cabeza
d.polygon([(8, 14), (23, 14), (25, 34), (6, 34)], fill=col_oscuro, outline=col_contorno)  # torso
d.rectangle([9, 34, 14, 45], fill=col_oscuro, outline=col_contorno)                       # pierna izq
d.rectangle([17, 34, 22, 45], fill=col_oscuro, outline=col_contorno)                      # pierna der
d.line([(11, 15), (11, 33)], fill=col_claro, width=1)                                     # resalte, un solo lado

img.save("spr_jugador_idle_0.png")
```

```bash
# ImageMagick — silueta de enemigo (categoria = paleta distinta), relleno + contorno reales
magick -size 24x24 xc:none \
  -fill "#c23b3b" -stroke "#4a1414" -strokewidth 1 -draw "roundRectangle 4,10 19,21 3,3" \
  -fill "#e0685a" -stroke "#4a1414" -strokewidth 1 -draw "ellipse 12,7 6,6 0,360" \
  spr_enemigo_idle_0.png
```

Importa e **importa el origen real**, no solo el frame — el gap que tenía la receta anterior.
`resource set` sobre `origin` y `sequence.xorigin`/`sequence.yorigin` está verificado en esta
sesión (crea el sprite, cambia su origen a `Custom` y coloca el punto donde tú digas):

```bash
gm-cli resourcetool eval "resource create type=sprite name=spr_jugador_idle"
gm-cli resourcetool eval "sprite addframe name=spr_jugador_idle path=spr_jugador_idle_0.png"
gm-cli resourcetool eval "resource set expr=spr_jugador_idle.origin value=Custom"
gm-cli resourcetool eval "resource set expr=spr_jugador_idle.sequence.xorigin value=16"
gm-cli resourcetool eval "resource set expr=spr_jugador_idle.sequence.yorigin value=47"
```

**Anímalo con un segundo fotograma cuando el movimiento lo pida** (§«Calidad mínima exigible»
más abajo) — repite la misma función o el mismo script con una pequeña variación (un `bob` de
1 px, brazos en otra posición) y un segundo `sprite addframe`; no hace falta más para un idle
creíble mientras llega el arte definitivo.

Nombra el archivo con el **nombre definitivo del asset** desde el principio (`spr_jugador_idle`,
no `spr_temp1`): sustituir el contenido más adelante no toca ni una línea de código, el mismo
principio que fija `13 · 11 §5` para todos los placeholders.

#### Peldaño 2 — Assets libres reales

Antes de dibujar nada tuyo, mira si ya existe: [`07 · 09` — Asset packs y recursos
gráficos](../07%20-%20Ecosistema/09%20-%20Asset%20packs%20y%20recursos%20gr%C3%A1ficos.md)
cataloga Kenney (CC0), los *Asset Bundles* oficiales (Apache 2.0), OpenGameArt e itch.io, con la
licencia de cada uno comprobada. Enlaces reverificados en vivo en esta sesión (2026-09-08):
Kenney, itch.io/game-assets/tag-gamemaker y OpenGameArt responden y sirven contenido real. No se
repite el catálogo aquí — sí el criterio: **un pack CC0 de Kenney bien elegido siempre gana a un
placeholder propio**, y cubre §4 de coherencia entre packs si mezclas más de uno.

#### Peldaño 2 bis — REPARAR lo generado, antes de meterlo en el juego

**Este peldaño no crea nada: arregla.** Y hace falta siempre que la imagen venga de un
generador, de un upscaler o de un JPEG — que es el caso del peldaño 3 de abajo.

El problema es concreto: lo que sale de un modelo *parece* pixel art y no lo es. Los píxeles
quedan **fuera de rejilla**, los bordes emborronados, la escala no es entera y el archivo pesa
diez veces su resolución real. Metido así en un sprite, el juego se ve sucio y no sabrás por qué.

```bash
# pixel-art-fixer — convierte pixel art FALSO en real. Sin modelo, sin clave, sin cuenta:
#   «Image processing only, no model required» (su propio README)
# En 11 - Código descargado/herramientas/pixel-art-ia/pixel-art-fixer/

# pixeldetector — repara arte dañado por reescalado o compresión y lo devuelve a su
# resolución verdadera. Solo pide Pillow, Numpy y Scipy.
python3 pixeldetector.py <entrada.png>
```

| Si tienes… | Usa |
|---|---|
| Una imagen generada que «parece» pixel art | `pixel-art-fixer` |
| Pixel art que alguien reescaló o guardó en JPEG | `pixeldetector` |
| Que reducir de escala sin destrozar los bordes | `K-Centroid-Aseprite` (k-medias) |
| Que aplicar tramado con tu paleta, desde Python | `hitherdither` (trabaja en PIL, encaja con §5.2 peldaño 1) |
| Partir una hoja de sprites sin rejilla fija | `spritesplitter` |
| Un mapa normal para la iluminación de `04 · 24 §3` | `Material-Map-Generator` |

Las siete son **MIT o Apache-2.0 y se ejecutan en local**. Catálogo y contexto en
[`07 · 23 §1 bis`](../07%20-%20Ecosistema/23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md).

> 🔑 **Regla: nada que salga de un generador entra en el juego sin pasar por aquí.** Es un
> comando, no cuesta nada, y es la diferencia entre un sprite que se ve nítido a tamaño real y
> uno que se ve emborronado sin causa aparente.

> 🔴 **PERO ANTES PASA LA PUERTA, o esta regla te destruye el arte.** La regla de arriba,
> obedecida al pie de la letra, se come también los sprites que dibujaste tú con Pillow en el
> peldaño 1(b) — porque Pillow también es «un generador». Medido sobre arte real de 16×20 px
> dibujado a 1:1: `pixel-art-fixer` lo declaró una imagen de **6×7 ampliada ×2,5**, y
> `pixeldetector` lo redujo a **4×10**. Un personaje con capucha, cara, cinturón y botas quedó
> en una mancha. Las dos herramientas hacen bien lo que anuncian —buscar la rejilla oculta de
> una imagen ampliada—; lo que faltaba era distinguir los dos casos.
> Caso completo: [`r15-prueba-puzles.md` §2.1](../_indice/auditorias/r15-prueba-puzles.md).
>
> ```bash
> python3 "$BIB/_indice/puerta-pixel-art.py" <carpeta de PNG>
> ```
>
> Sale con **0 si no hay nada que reparar** y con **1 listando qué PNG lo piden y por qué**.
> Decide con tres medidas y exigiendo las tres **a la vez**, no una cualquiera:
>
> | Medida | Qué distingue |
> |---|---|
> | **Escala real** — el mayor `k` tal que reducir por `k` y volver a ampliar reproduce la imagen EXACTA | `k == 1` ya es pixel art de verdad: no hay rejilla que reconstruir |
> | **Paleta** — número de colores distintos | Un PNG de un modelo trae cientos; uno con paleta fija, decenas |
> | **Halo** — % de píxeles con alfa intermedio (0 < a < 255) | Un generador deja el borde emborronado; un pincel, no |
>
> **La conjunción no es un detalle, es lo que evita el destrozo**: cada síntoma por separado
> tiene causas legítimas. Una sombra es alfa parcial *a propósito* (81 % medido en un caso real)
> y una puerta de bloques grandes puede ser, por casualidad, un aumento exacto ×2. Con la
> disyunción, esos dos archivos reales se habrían triturado.
>
> Verificada en las dos direcciones: sobre 76 PNG de arte real dibujado a 1:1 dice
> «0 piden reparación», y sobre un pixel art ampliado ×4 con interpolación suave lo señala
> (3 753 colores, 62 % de alfa intermedio) sin tocar el que se amplió con vecino más próximo.

> ⚠️ **`pixel-art-fixer` no arranca por la orden que anuncia su propio README.**
> `python -m pixelfixer.cli entrada.png` termina en `ModuleNotFoundError: No module named
> 'detector'`: el paquete se renombró a `pixelfixer` y `cli.py` sigue importando del nombre viejo
> en sus tres sitios. **La API sí funciona** — `from pixelfixer import detect` y
> `from pixelfixer.reconstruct import reconstruct`. Verificado en `r15` §2.2.

#### Peldaño 3 — Generación por IA

`codex exec` con el modelo `gpt-image-2` está disponible y verificado en esta máquina —
**probado en esta sesión**, generando un icono de personaje real (no un boceto): la política
global del entorno del usuario lo delega así porque `imagegen` es una *skill* de sistema propia
de Codex, sin equivalente directo en Claude Code.

```bash
codex exec -C <dir_proyecto> --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check \
  -o <scratch>/codex_last.txt \
  "Usa tu herramienta de generación de imágenes (gpt-image-2) para crear <descripción del
   personaje/objeto: silueta, paleta, estilo>. Fondo neutro o transparente, sin texto ni marcas
   de agua. Guarda el PNG 1024x1024 en <ruta>. Genera 2-3 variantes. Al terminar lista las rutas."
```

El resultado de esta sesión: un icono de zorro azul en pixel art limpio, 1024×1024, coherente en
paleta y con silueta legible — muy por encima de lo que exige un placeholder, y una referencia de
diseño real si luego se redibuja a mano. **Para dónde encaja esto en el pipeline sin arriesgar
propiedad intelectual ni incumplir la política de una tienda**, la tabla ya está resuelta en
[`07 · 23` §5](../07%20-%20Ecosistema/23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md#5--dónde-encaja-en-un-pipeline-real--recomendación-práctica):
sí para referencia, moodboard y concept; sí, declarándolo, para un icono o pieza de UI puntual
sin animar; **no** para el sprite final animado y jugable (§2-§3 de ese mismo documento explican
por qué es estructural, no una cuestión de calidad del modelo). Sigue el checklist de
[`07 · 23` §6](../07%20-%20Ecosistema/23%20-%20Arte%20generado%20por%20IA%20%28pixel%20art%20y%20assets%202D%29.md#6--checklist-antes-de-usar-ia-generativa-en-tu-arte)
antes de dar por bueno cualquier resultado.

Lístalo en `PLACEHOLDERS.md` si va a convivir con el proyecto más de una sesión, igual que
cualquier otro asset provisional de §5.1 y de este mismo peldaño 1.

#### Calidad mínima exigible de un marcador de posición

Extiende las tres reglas de
[`13 · 03 §7.3`](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resoluci%C3%B3n.md#73-placeholders-cajas-grises-con-disciplina)
(tamaño definitivo, un color por categoría, origen y dirección marcados) con lo que un color
plano nunca puede darte: silueta y, cuando el objeto se mueve, una segunda pose. Comprobable
punto por punto, no una impresión subjetiva:

| Criterio | Qué comprobar | Cómo se falla |
|---|---|---|
| **Tamaño coherente** | Igual al tamaño definitivo del sprite en la resolución base del juego (`13 · 03 §1`), nunca «ya lo escalo luego» | Placeholder a 64×64 en un juego de tiles de 16 px: la colisión y la cámara quedan mal calibradas desde el primer día |
| **Paleta limitada compartida** | Los mismos 2-4 tonos + contorno en **todos** los placeholders del proyecto, un juego de tonos por categoría (jugador, enemigo, objeto, peligro) | Cada placeholder con un color elegido al azar: no hay forma de distinguir categorías de un vistazo |
| **Silueta legible a tamaño real** | Se reconoce **sin ampliar** qué es (cabeza, cuerpo, extremidades o su equivalente para un objeto) — la prueba de `13 · 03 §8.1`: en escala de grises se sigue leyendo | Un óvalo sin cabeza ni piernas diferenciadas sigue siendo mejor que un cuadrado, pero si ni así se distingue de otro placeholder, no pasa el filtro |
| **Origen correcto** | Marcado y verificado — pies para un personaje, centro para un proyectil u objeto — con `resource set … origin=Custom` + `xorigin`/`yorigin`, o el `xorig`/`yorig` de `sprite_create_from_surface()` | El sprite «flota» o se hunde en el suelo en cuanto se coloca en una room real |
| **Animación mínima** | **Al menos 2 fotogramas** cuando el objeto tiene idle, andar o cualquier movimiento visible — un `bob` de 1 px o un cambio de pose ya rompe la sensación de sprite muerto | Un solo frame estático en un personaje que se mueve todo el rato del juego |

Un placeholder que cumple esta tabla **se ve reconociblemente mejor que un rectángulo de color
plano** con el mismo coste de tiempo — es la comprobación hecha en esta sesión con las dos
siluetas del peldaño 1: un vistazo basta para distinguir «jugador» de «enemigo» y ver hacia dónde
mira cada uno, algo que ningún cuadrado monocolor consigue.

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
- **`FOLDER CREATE` no comparte argumentos con `RESOURCE CREATE`**, aunque lo parezca: acepta un
  único `folder=<ruta>` (la ruta a crear), no `name=`/`type=` como los comandos de creación de
  recursos. Pedirlo por analogía (`folder create name=Objetos type=object`) no da error: cada
  argumento sobrante se ignora en silencio (`Ignoring Argument: NAME` / `Ignoring Argument:
  TYPE`) y la carpeta se crea en la **ruta vacía** (`''`) en vez de donde pretendías. Tabla
  completa de argumentos en [`07 · 13`](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md#inventario-completo-de-comandos-resourcetool-2026017).

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

### 7.6 El punto ciego de `validar-proyecto.py`: no distingue «conectado a un recurso» de «está en la carpeta»

`validar-proyecto.py` analiza cualquier `.gml` que encuentre dentro de la carpeta del proyecto,
**sin cruzarlo contra el `.yyp`** para comprobar si ese archivo está de verdad enlazado a un
recurso compilable. Si dejas una copia de trabajo — un `.gml` que editaste fuera del flujo de
`resourcetool` antes de importarlo, o material de referencia — dentro de la carpeta del proyecto
(por ejemplo, en una subcarpeta propia como `_borrador/` o `_assets_gen/`), el validador la
cuenta como «definida en el proyecto» aunque el compilador nunca la vea.

**Consecuencia real, verificada en `_indice/auditorias/r5-prueba-e2e.md` §7**: una función nueva
añadida a una copia de trabajo sin re-sincronizarla con el recurso real (`gml setgmlfile`) queda
invisible para `validar-proyecto.py` — no aparece como `desconocida` ni como `INVENTADA`, porque
el validador la encuentra definida en esa copia y da el símbolo por resuelto — y solo sale a la
luz al ejecutar el juego de verdad (`Variable obj_x.funcion_nueva(...) not set before reading
it`, el mismo mensaje de la Trampa 4, pero por una causa distinta: la función existe en disco,
solo que no donde el compilador la busca).

**La defensa**: nunca dejes archivos de trabajo (borradores, copias antes de importar, material
de referencia) dentro de la carpeta del proyecto — usa el scratchpad de la sesión o cualquier
ruta fuera del `.yyp`. Si tienes dudas de si algo se coló, compara cuántos archivos analiza el
validador contra `find <ruta-del-proyecto> -name "*.gml" | wc -l`: una diferencia entre lo que
reporta uno y otro señala una carpeta suelta que el `.yyp` no referencia.

### 7.7 Un segundo hallazgo de esta sesión: `--errors-only` también esconde por completo un `NullReferenceException` real del `AssetCompiler`

`06 - Assets y Scripts/README.md` ya dejaba constancia de que un `sprite` creado por
`resourcetool` sin ninguna imagen real (un *stub* sin frames, como los que deja
`resource create type=sprite name=X` sin un `sprite addframe` después) hace que el
`AssetCompiler` lance una `NullReferenceException` de .NET al compilar — pero sin decir qué pasa
con `--errors-only`, ni si el paquete llega a escribirse. Reproducido aquí, en un proyecto
mínimo con un único `spr_vacio` sin frames y nada más:

```bash
$ gm-cli compile --toolchain GMS2@2026.0.0.23 --errors-only
$ echo $?
0
```

**Cero líneas, exit 0** — indistinguible de una compilación realmente limpia. Solo compilando
**sin** el flag aparece lo que de verdad ocurrió:

```
│  Core Resources : Info - Sprite - spr_vacio - has missing layers; resetting to default Sprite.
│  ...
│  Unhandled exception.
│  System.Reflection.TargetInvocationException: Exception has been thrown by the target of an invocation.
│   ---> System.NullReferenceException: Object reference not set to an instance of an object.
│     at GMAssetCompiler.GMSprite.SetFromResource(GMAssets _assets, GMSprite _sprite)
│     at GMAssetCompiler.GMSprite..ctor(GMAssets _assets, ResourceBase _id)
│     ...
◆  Compilation finished
```

`gm-cli` imprime «◆ Compilation finished» y **el proceso sale con `exit 0`** pese al *crash* — es
un crash real del `AssetCompiler` (`System.NullReferenceException` sin capturar, con su *stack
trace* completo de .NET), no un aviso cosmético. Y la consecuencia práctica es peor que un
`WARNING`: el `AssetCompiler` revienta **antes** de llegar a la fase de «Saving IFF file», así
que `game.zip` **no se reescribe en absoluto** — si ya existía un build anterior en
`.gmcache/.../output/game.zip`, ese archivo queda ahí, intacto y desactualizado, y nada en la
salida de `gm-cli compile` (ni siquiera sin `--errors-only`, que solo muestra la traza pero no
dice «no se generó el paquete») lo señala como obsoleto.

**La defensa** es la misma que ya da [§5.2](#52-gráfico-la-escalera-de-prioridad-sin-el-rectángulo-plano):
nunca dejes un `sprite` creado por `resourcetool` sin al menos un frame real antes de compilar —
la escalera de esa sección (dibujo por código, assets libres, IA) evita este estado por completo.
Si sospechas que un build no se actualizó, compara la fecha de `game.zip` contra la hora actual
después de cada `compile`, no solo el `exit 0`.

> ⚠️ **Y hay un tercer silencio, el más difícil de leer: `--errors-only` no distingue «compiló
> bien» de «no miró nada».** Sobre un proyecto con 2 000 líneas de GML nuevo, la primera
> compilación devolvió esto:
>
> ```console
> $ gm-cli compile --errors-only ; echo "EXIT=$?"
> EXIT=0
> ```
>
> Ni una línea, siete segundos. Es la salida correcta —y es exactamente la misma que daría una
> herramienta que no hubiera abierto un solo archivo—. **La forma de saberlo es rompiendo el
> código a propósito una vez**, al empezar, y comprobando que se queja:
>
> ```console
> $ printf 'function prueba() { var _x = ; }\n' >> scripts/scr_ui/scr_ui.gml
> $ gm-cli compile --errors-only
> Command failed:
> gml_GlobalScript_scr_ui(279) : unexpected symbol ";" in expression
> GMAssetCompiler.dll exited with non-zero status (1)
> ```
>
> Confirmado: el compilador sí ve tu código, y el silencio anterior era silencio de éxito. Cuesta
> veinte segundos y convierte un `exit 0` mudo en una prueba. Es la misma disciplina que
> `verificar-enlaces.py` aprendió a la fuerza —**un cero puede significar «nada mal» o «nada
> mirado», y hay que poder distinguirlo**— y la que `buscar.py` aplica cuando no encuentra
> `grep`. ([`r15` §2.11](../_indice/auditorias/r15-prueba-puzles.md))

---

## 8 · Checklist final antes de dar una tarea por terminada

- [ ] Cada símbolo de GML que escribiste está verificado con `buscar.py` (no «creo que existe»).
- [ ] Cada evento que creaste con `resourcetool` se comprobó con `object event list name=<obj>`
      — no te fiaste del nombre del subtipo a ciegas (§2.5).
- [ ] `gm-cli compile --errors-only` da `exit 0` y **sin salida** — y al menos una vez en la
      sesión rompiste el código a propósito para comprobar que ese silencio es de éxito y no de
      «no he mirado nada» (§7.7).
- [ ] **Compilaste también sin `--errors-only` al menos una vez** y leíste la salida completa
      buscando `WARNING` — no solo el `exit 0` del paso anterior. Es el único modo que muestra un
      *included file* que no llegó al paquete (Trampa 8 de [§0](#0--las-quince-trampas-que-hacen-fracasar-a-un-agente-hoy)).
- [ ] Si el proyecto tiene algún `includedfile`, comprobaste su `filePath`
      (`resource info expr=project.IncludedFiles LIST` o el `.yyp`) y que el archivo físico
      existe de verdad dentro de `datafiles/` — no confiaste en que `resourcetool` lo copiara.
- [ ] `validar-proyecto.py <ruta> --todo` da `✓ Ninguna función INVENTADA` **y** revisaste a mano
      la lista de `desconocida` (§7.5) — no solo miraste el exit code.
- [ ] Si el proyecto usa `constructor` con herencia, ningún padre queda sin definir (§7.3).
- [ ] Ejecutaste el juego (`gm-cli run`) al menos hasta el punto que estás probando, y no quedó
      ningún proceso de *runner* huérfano (§4.3).
- [ ] Si algo depende de vista, oído, hardware real o certificación de plataforma, lo dijiste
      explícitamente en vez de darlo por bueno (§4.2).
- [ ] **Si la tarea era «hazme un juego» y no «arréglame esto»**: ejecutaste
      `python3 "_indice/auditar-juego-completo.py" <ruta>` y, o sale con `exit 0`, o justificaste
      **por escrito** cada pieza que marca como ausente. Un bucle de juego que compila no es un
      juego: sin menú, sin pausa, sin guardado y sin cierre, lo que entregas es una demo técnica,
      y el usuario que pidió un juego no lo va a llamar así. El detector no juzga la calidad —
      solo impide que la ausencia pase inadvertida.
- [ ] Ningún objeto con el que el jugador interactúa se quedó **sin sprite, pintando un
      rectángulo** en su evento Draw. El auditor del punto anterior los lista por nombre; la
      escalera para salir de ahí está en [§5.2](#52-gráfico-la-escalera-de-prioridad-sin-el-rectángulo-plano).
- [ ] Si reordenaste `project.RoomOrderNodes`, lo hiciste con `resourcetool eval`, una llamada
      por índice — **nunca** con `resourcetool script` (el modo por lotes reporta éxito en cada
      línea pero no persiste el cambio, §9.3 y §10.4) — y, si borraste alguna sala de por medio,
      reordenaste **después** del borrado, nunca antes, y lo confirmaste leyendo el `.yyp` (§9.3
      bis: `RESOURCE DELETE` puede reiniciar el array entero, de forma intermitente).
- [ ] Si una llamada de `resourcetool` falló con `System.AccessViolationException` sobre un
      proyecto que ya sabes sano, la reintentaste antes de asumir que el proyecto está corrupto —
      el propio `ResourceTool@2026.0.17` puede fallar así de forma no determinista
      (Trampa 11 de [§0](#0--las-quince-trampas-que-hacen-fracasar-a-un-agente-hoy)).
- [ ] Si el juego dibuja texto en español, comprobaste **mirando la captura**, no el código,
      que las tildes y la eñe se ven — nunca dependiendo de `draw_set_font(-1)`/la fuente por
      defecto para texto en español (Trampa 12 de
      [§0](#0--las-quince-trampas-que-hacen-fracasar-a-un-agente-hoy)).

---

## 9 · El orden de las salas: `project.RoomOrderNodes` lo resuelve directamente

> ⚠️ **Corrección del 8 de septiembre de 2026**: la versión anterior de esta sección afirmaba
> que no existía ningún comando para el orden de las salas, y documentaba editar el `.yyp` a
> mano como único recurso. **Era falso** — la causa exacta está en la
> [Trampa 7 de §0](#trampa-7--antes-de-dar-un-comando-por-imposible-prueba-resource-info-exprproject-y-help-comando):
> nadie había probado la raíz de expresión `project`, que no aparece en ningún ejemplo del
> `HELP`. Esta sección queda reescrita con la vía real; el resto de la raíz `project` (18
> miembros, de los que `RoomOrderNodes` es solo uno) está en
> [§9 bis](#9-bis--la-raíz-project-18-miembros-probados-uno-a-uno).

**Pregunta que responde esta sección**: creaste tus salas con `resourcetool` — ¿cómo le dices a
GameMaker cuál arranca primero, y cómo reordenas salas que ya tienen contenido? Verificado en
vivo el **8 de septiembre de 2026**, `gm-cli` 2.3.0 / `ResourceTool@2026.0.17`, en un proyecto de
prueba bajo `~` (creado con `gm-cli init -t "Blank Pixel Game"`, borrado al terminar).

### 9.1 El comando real

`RoomOrderNodes` es un **miembro de la raíz `project`** (§9 bis), no una raíz en sí misma. Por
eso `resource info expr=RoomOrderNodes` (sin el prefijo `project.`) falla con `'RoomOrderNodes'
not found at root` — y por eso la investigación anterior concluyó, incorrectamente, que no había
ningún mecanismo. Con el prefijo correcto, `RoomOrderNodes` se lee y se escribe igual que
cualquier otro campo:

```bash
$ gm-cli resourcetool eval "resource set expr=project.RoomOrderNodes[0].roomId value=rm_juego"
project.RoomOrderNodes[0].roomId: YoYoStudio.Resources.GMRoom
Saved successfully
ResourceTool Successful
```

Y para leer el orden completo:

```bash
$ gm-cli resourcetool eval "resource info expr=project.RoomOrderNodes LIST"
Type: list of RoomOrderNode
List has 4 items of type RoomOrderNode
Index with: eg: project.RoomOrderNodes[0]
```

Cada elemento es un `RoomOrderNode` con un único campo, `roomId` (una referencia a una sala
completa) — `resource info expr=project.RoomOrderNodes[i].roomId` devuelve esa sala entera
(capas, instancias, ajustes de vista…) en la posición `i`.

### 9.2 Las salas se añaden en el orden en que las creas — sigue siendo cierto y sigue siendo útil

`RESOURCE CREATE TYPE=room` **añade la sala nueva al final de `RoomOrderNodes`**, verificado de
nuevo en esta sesión creando tres salas seguidas y leyendo el `.yyp`:

```
"RoomOrderNodes":[
    {"roomId":{"name":"Room1", …}},        ← la de la plantilla, ya estaba primera
    {"roomId":{"name":"rm_splash", …}},    ← 1ª creada por resourcetool → 2ª posición
    {"roomId":{"name":"rm_menu", …}},      ← 2ª creada → 3ª posición
    {"roomId":{"name":"rm_juego", …}},     ← 3ª creada → 4ª posición
  ],
```

Y borrar la sala de la plantilla (que la mayoría de plantillas dejan primera, con el nombre
`Room1` o similar) **promueve automáticamente a primera la siguiente en el array**, sin tocar
`RoomOrderNodes` explícitamente:

```bash
gm-cli resourcetool eval "resource delete name=Room1 type=room"
# RoomOrderNodes queda: rm_splash (ahora primera), rm_menu, rm_juego
```

Esto sigue siendo la vía más simple si decides el orden **antes** de construir el contenido de
cada sala: crea las salas en el orden final que quieres y, si sobra la sala de la plantilla,
bórrala.

⚠️ **Esto solo es seguro para salas vacías o para la sala de plantilla que vas a descartar.**
`RESOURCE DELETE` de una sala se lleva todo su contenido (capas, instancias, *tiles*), y
`RESOURCE CREATE` de una sala con el mismo nombre no lo recupera, la crea vacía — verificado de
nuevo en esta sesión: se colocó una instancia (`ROOM INSTANCE CREATE`), se borró la sala y se
volvió a crear con el mismo nombre, y la instancia **desapareció**. No la uses para reordenar una
sala que ya tiene contenido — para eso está §9.3.

⚠️ **`RESOURCE DELETE` de una sala puede reiniciar el orden entero, no solo el hueco que borra**
— se ha observado que, tras reordenar `RoomOrderNodes` con la receta de §9.3, borrar cualquier
sala (aunque esté vacía y en la última posición) hace que el reordenamiento se pierda por
completo, no solo la posición de la sala borrada. Parece intermitente, no garantizado — detalle
completo, con la doble tanda de evidencia (a favor y en contra) y la regla práctica que se deriva
de esto, en
[§9.3 bis](#93-bis--dos-matices-nuevos-encontrados-construyendo-un-juego-real-de-punta-a-punta).

### 9.3 Reordenar salas que ya tienen contenido — sin borrar nada

**Esto es lo que corrige la sección**: como `RoomOrderNodes[i].roomId` se puede **reasignar
directamente**, reordenar no requiere borrar ni recrear ninguna sala — la operación solo cambia
qué sala ocupa cada posición del array, sin tocar las capas, instancias ni ajustes de la sala en
sí. Es igual de segura con salas vacías que con salas llenas de contenido.

**Verificado en vivo con una permutación completa**, en un proyecto de prueba con 4 salas
(`Room1`, `rm_splash`, `rm_menu`, `rm_juego`, en ese orden de creación):

```bash
$ gm-cli resourcetool eval "resource set expr=project.RoomOrderNodes[0].roomId value=rm_juego"
$ gm-cli resourcetool eval "resource set expr=project.RoomOrderNodes[1].roomId value=rm_menu"
$ gm-cli resourcetool eval "resource set expr=project.RoomOrderNodes[2].roomId value=Room1"
$ gm-cli resourcetool eval "resource set expr=project.RoomOrderNodes[3].roomId value=rm_splash"
```

`.yyp` resultante, leído después de las cuatro llamadas:

```
"RoomOrderNodes":[
    {"roomId":{"name":"rm_juego", …}},
    {"roomId":{"name":"rm_menu", …}},
    {"roomId":{"name":"Room1", …}},
    {"roomId":{"name":"rm_splash", …}},
  ],
```

Los cuatro índices quedaron en una permutación completamente distinta de la de creación —
ninguna sala de las cuatro conserva su posición original. `gm-cli resourcetool eval "check"` y
`gm-cli compile --errors-only` (`exit 0`) confirmaron después que el proyecto seguía siendo
válido. **No se tocó ninguna sala** — solo el array de orden.

**La receta general**:

1. Lee el orden actual con `resource info expr=project.RoomOrderNodes LIST` (o índice a índice,
   `expr=project.RoomOrderNodes[i].roomId`, si necesitas ver qué sala hay en cada posición).
2. Reasigna cada posición que quieras cambiar con `resource set
   expr=project.RoomOrderNodes[i].roomId value=<nombre_de_sala>` — cualquier sala que ya exista
   en el proyecto, tenga o no contenido. **Hazlo con `resourcetool eval`, una llamada por
   índice — nunca con `resourcetool script`** (ver §9.3 bis, más abajo: el modo por lotes no
   persiste esta operación aunque reporte éxito).
3. No hace falta tocar el tamaño del array: siempre tiene tantos elementos como salas existan en
   el proyecto, y `resource set` sobre un índice solo cambia **qué sala apunta ahí**, nunca
   cuántas posiciones hay.

### 9.3 bis · Dos matices nuevos, encontrados construyendo un juego real de punta a punta

> Verificados el 8 de septiembre de 2026 en
> [`_indice/auditorias/r6-regresion.md` §3](../_indice/auditorias/r6-regresion.md#3--el-orden-de-las-salas--funcionó-projectroomordernodes-tal-como-documenta-1209),
> reordenando 7 salas reales de un sokoban de tres niveles, y reverificados de nuevo en un
> proyecto de prueba independiente al escribir esta sección — con un resultado distinto para el
> punto 2, detallado ahí mismo. §9.1-§9.3 arriba se verificaron de nuevo tal cual y siguen siendo
> correctos — estos dos matices se suman, no los sustituyen.

**1 · El modo por lotes (§10) reporta éxito pero NO persiste un `RESOURCE SET` sobre
`RoomOrderNodes`.** Un archivo de lote con las 7 líneas de `resource set
expr=project.RoomOrderNodes[i].roomId value=…`, ejecutado con `gm-cli resourcetool script
lote.txt proyecto.yyp`, respondió `Saved successfully` en cada línea y `ResourceTool Successful`
al final — pero el `.yyp` en disco, leído justo después, **seguía con el orden de creación
original**, como si el lote nunca se hubiera ejecutado. Las mismas 7 operaciones, repetidas una
por una con `resourcetool eval` sin cambiar ni una letra del comando, sí persistieron — confirmado
leyendo el archivo. No se investigó la causa interna (podría ser el `ProjectFileWatcher` que se ve
parar y reanudar en cada guardado, compitiendo con el guardado incremental del lote); el hecho
reproducible es que **el modo por lotes no escribe este cambio a disco**, aunque diga que sí.

⚠️ Esto **matiza la recomendación de §10.4** («varias salas en el orden que quieres — §9.2»): esa
fila sigue siendo cierta para crear salas en el orden de **creación** (§9.2), pero **no** se
extiende a *reordenar* salas que ya existen (§9.3) — para `RESOURCE SET` sobre
`project.RoomOrderNodes`, usa siempre `eval`, nunca `script`, por rápido que parezca el lote. Nota
gemela en [§10.4](#104-cuándo-usar-script-en-vez-de-eval).

**2 · `RESOURCE DELETE` de una sala puede reiniciar TODO `RoomOrderNodes` — observado una vez,
NO reproducido en 6 intentos posteriores; trátalo como riesgo intermitente, no como ley fija.**
Tras confirmar un reordenamiento correcto con la receta de arriba, `r6-regresion.md` borró una
sala completamente distinta — `Room1`, la sala vacía de la plantilla, que ya estaba en la última
posición del array — con `resource delete name=Room1 type=room`, y el `.yyp` resultante
**volvió al orden de creación original de las demás salas**, perdiendo el reordenamiento explícito
ya aplicado. `Room1` sí desapareció correctamente; lo que se perdió fue el orden de las otras seis.

⚠️ **Verificación de esta corrección, 8 de septiembre de 2026**: se repitió el experimento 6 veces
más, en un proyecto de prueba distinto bajo `~` — permutación completa de `RoomOrderNodes` por
`eval`, seguida de un `RESOURCE DELETE` sobre la sala que quedó en la última posición (incluida
`Room1` en un intento, salas creadas por el propio agente en los otros cinco) — y **ninguna de las
6 veces se reinició el array**: en todas, `RESOURCE DELETE` se limitó a quitar el hueco de la sala
borrada, conservando intacto el resto de la permutación. No es que la observación original fuera
falsa — ocurrió, con evidencia real, en una sesión que ya documentó por separado una condición de
carrera genuina de `ResourceTool` (el hallazgo 4 de esta misma Trampa). Lo más probable es que sea
la **misma familia de fallo no determinista**, no un comportamiento garantizado de `RESOURCE
DELETE` — pero con una sola observación a favor y seis en contra, no hay base para escribirlo como
ley fija, así que queda documentado como riesgo posible, no como certeza.

**La regla práctica se mantiene igual pase lo que pase con el determinismo del bug: reordena
SIEMPRE después de borrar cualquier sala, nunca antes, y confírmalo leyendo el `.yyp` (o con
`resource info expr=project.RoomOrderNodes LIST`) en vez de fiarte del mensaje de éxito.** Cuesta
lo mismo hacerlo así siempre que investigar, cada vez, si esta ejecución en concreto fue de las
que reinician o no.

### 9.3 ter · Un `RESOURCE SET` de un solo índice, sin recolocar la sala desplazada, deja `RoomOrderNodes` duplicado y tumba el compilador entero

> Verificado el 8 de septiembre de 2026, primero en
> [`_indice/auditorias/r8-prueba-coop.md` §8.2](../_indice/auditorias/r8-prueba-coop.md), y
> reproducido de nuevo aquí en un proyecto de prueba independiente bajo `~` para esta corrección
> (dos salas, `gm-cli` 2.3.0 / `ResourceTool@2026.0.17`).

La receta de **§9.3** (arriba) es segura **solo si el array queda como una permutación
completa**: cada sala del proyecto aparece exactamente una vez, en algún índice. `RESOURCE SET`
no comprueba esa condición — deja escribir un `roomId` que ya está en otro índice sin avisar de
nada, y el resultado es una sala duplicada (aparece en dos posiciones) y otra que desaparece del
array por completo:

```bash
$ gm-cli resourcetool eval "resource set expr=project.RoomOrderNodes[0].roomId value=rm_dos"
Saved successfully
```

Con dos salas (`Room1`, `rm_dos`) y `Room1` en el índice 0 antes del comando, el `.yyp` queda:

```
"RoomOrderNodes":[
    {"roomId":{"name":"rm_dos", …}},
    {"roomId":{"name":"rm_dos", …}},
  ],
```

`Room1` desapareció del array (sigue existiendo como recurso, solo salió del orden) y `rm_dos`
quedó duplicado. `resourcetool` no avisa — dice `Saved successfully` igual que con un valor
correcto. La siguiente compilación **no da un error de GameMaker**: tumba el `AssetCompiler`
entero con una excepción de .NET sin manejar, reproducida al carácter:

```
Unhandled exception.
System.Reflection.TargetInvocationException: Exception has been thrown by the target of an invocation.
 ---> System.ArgumentOutOfRangeException: Index was out of range. Must be non-negative and less than the size of the collection. (Parameter 'index')
   at System.Collections.Generic.List`1.get_Item(Int32 index)
   at GMAssetCompiler.GMProjectSymbols.GatherResources()
   ...
◆  Game exited
```

**La forma correcta de la escritura**: si vas a mover una sala a un índice, tienes que mover
también la sala que ya ocupaba ese índice a otro sitio válido, para que el array siga siendo una
permutación sin huecos ni repetidos — exactamente la receta de §9.3 (reasignar **todos** los
índices afectados, no solo uno) o la permutación completa de su ejemplo verificado. Confirmado
aquí: devolver `Room1` al índice 0 (`resource set expr=project.RoomOrderNodes[0].roomId
value=Room1`) restaura una permutación válida (`Room1` en 0, `rm_dos` en 1, sin duplicados) y el
mismo proyecto vuelve a compilar limpio (`exit 0`, sin `WARNING`). **La regla práctica**: después
de cualquier `RESOURCE SET` sobre `project.RoomOrderNodes`, lee el array completo
(`resource info expr=project.RoomOrderNodes LIST`, o índice a índice) y confirma que tiene
tantas entradas como salas y ninguna se repite, **antes** de compilar — el mensaje de éxito de
`resourcetool` no lo garantiza, y el error que sale si te equivocas es un *stack trace* de .NET
en bruto, no algo que oriente a un agente sobre qué se rompió.

### 9.4 El IDE sigue siendo una alternativa válida — ya no la única

GameMaker tiene un panel «Room Order» con arrastrar-y-soltar en el IDE. Sigue siendo perfectamente
válido si un humano está reordenando salas a mano, pero **ya no es necesario para un agente**: la
receta de §9.3 hace exactamente lo mismo sin abrir el IDE y sin el riesgo de una edición manual
del `.yyp`.

**Nota histórica**: la versión anterior de esta sección documentaba, como último recurso, editar
`RoomOrderNodes` directamente en el `.yyp` a mano — con el aviso de que el archivo usa comas
finales (`trailing commas`, un `json.load()` estricto de Python falla contra él) y de que un JSON
mal formado puede tirar `resourcetool`/`compile` con un `System.AccessViolationException` nativo
(Trampa 5 de §0). Esa técnica **ya no hace falta para el orden de las salas** — §9.3 la sustituye
por completo —, pero el aviso sobre el formato del `.yyp` y la utilidad de `CHECK` para verificar
una edición manual siguen siendo válidos para cualquier otro campo que de verdad resulte
inalcanzable por `resourcetool` — solo que primero comprueba la Trampa 7 de §0 antes de asumir
que lo es.

**Resumen de la sección**: `project.RoomOrderNodes[i].roomId` lee y escribe el orden de las
salas directamente, con o sin contenido. §9.2 sigue siendo la vía más simple para fijar el orden
antes de construir contenido; §9.3 es la vía para reordenar después. Ninguna de las dos necesita
el IDE ni tocar el `.yyp` a mano.

---

## 9 bis · La raíz `project`: 18 miembros, probados uno a uno

**El hallazgo grande de esta corrección**: `project` es una segunda raíz de expresión válida
para `RESOURCE INFO`/`RESOURCE SET` — al mismo nivel que un nombre de recurso — que ningún
documento de la biblioteca había probado hasta ahora. Se descubre con `gm-cli resourcetool eval
"resource info expr=project"` (salida real completa en la [Trampa 7 de
§0](#trampa-7--antes-de-dar-un-comando-por-imposible-prueba-resource-info-exprproject-y-help-comando)):
18 campos — `AudioGroups`, `configs`, `defaultScriptType`, `Folders`,
`ForcedPrefabProjectReferences`, `FullName`, `IncludedFiles`, `isDnDProject`, `isEcma`,
`LibraryEmitters`, `MetaData`, `name`, `parent`, `resources`, `RoomOrderNodes`, `tags`,
`templateType`, `TextureGroups`.

Verificado en un proyecto de prueba bajo `~` (`gm-cli init -t "Blank Pixel Game"`, borrado al
terminar), `gm-cli` 2.3.0 / `ResourceTool@2026.0.17`, el 8 de septiembre de 2026. Los 18
miembros, probados uno a uno con `resource info`/`resource set` (lectura y escritura reales, no
inferidas):

| Campo | Tipo | Lectura | Escritura | Para qué le sirve a un agente |
|---|---|---|---|---|
| `AudioGroups` | lista de `audiogroup` | ✅ | ✅ vía `AUDIOGROUP CREATE/DELETE/RENAME` (comando dedicado, ya en el inventario de `07 · 13`) — reflejado aquí al instante | Ver y auditar los grupos de audio del proyecto (streaming/descarga bajo demanda) sin abrir el IDE |
| `configs` | árbol `ProjectConfig` (`name` + `children` anidados) | ✅ | ✅ vía `CONFIG CREATE/DELETE/RENAME/SETACTIVE` — reflejado aquí, anidación incluida | Configuraciones de build (dev/prod, variantes por plataforma) — leerlas o crearlas sin el IDE |
| `defaultScriptType` | enum `None`\|`GML`\|`GMLVisual` | ✅ | ✅ **directa**: `resource set expr=project.defaultScriptType value=GML` | Fijar si los scripts nuevos del proyecto se crean en GML o en GML Visual por defecto |
| `Folders` | lista de `folder` | ✅ | ✅ vía `FOLDER CREATE` — reflejado aquí | Carpetas del Asset Browser — organizar el árbol de recursos sin pasar `folder=` en cada `resource create` |
| `ForcedPrefabProjectReferences` | lista de `resource` | ✅ (vacía sin Prefab Collections) | No se localizó un comando dedicado — `PREFAB ADDREFERENCE` gestiona referencias normales, no se encontró el equivalente «forzada» | Solo relevante si el proyecto depende de Prefab Collections de terceros; no verificable sin una Collection real instalada |
| `FullName` | string | ✅ | ❌ **confirmado de solo lectura**: `'project.FullName' can be read but set access is not yet permitted for this member` | Nombre completo del proyecto (coincide con `name` en el caso normal) |
| `IncludedFiles` | lista de `includedfile` | ✅ | ✅ para crear el recurso — `includedfile` ya está entre los 17 tipos de `resource create`, solo que nunca se había conectado con `project.IncludedFiles`; ⚠️ para el contenido real ver el aviso de abajo | Registrar archivos de datos (JSON, configuración, DLC) en el proyecto, con la salvedad de cómo se adjunta el archivo físico |
| `isDnDProject` | bool | ✅ | ✅ (`true`/`false`; es un flag crudo — no convierte código GML real en acciones Drag & Drop) | Detectar o forzar si el proyecto se trata como 100 % Drag & Drop |
| `isEcma` | bool | ✅ | ✅ | Flag de compatibilidad ECMAScript del proyecto |
| `LibraryEmitters` | lista de `emitter` | ✅ (vacía en un proyecto normal) | No se localizó un comando dedicado | Ligado a proyectos tipo «Librería» que generan código hacia otros proyectos (paquetes de extensión); no es el caso normal de un juego |
| `MetaData` | diccionario `string → string` | ✅ — `project.MetaData['Clave']` (**comillas simples**; con dobles falla: `Unrecognized syntax`) | ❌ **confirmado de solo lectura**: `cannot determine member type` | Leer `IDEVersion`, `PackageID`, `PackageName`, `PackagePublisher`, `PackageType`, `PackageVersion` — útil para que un script sepa la versión/identidad del proyecto; no editable por esta vía hoy |
| `name` | string | ✅ | ⚠️ técnicamente sí, **pero no la uses** — ver aviso abajo | Nombre interno del proyecto |
| `parent` | `resource`, siempre `null` en la raíz | ✅ | Rechaza cualquier valor que no sea el nombre de un recurso existente | Campo heredado de la clase base de recursos; sin uso real en la raíz del proyecto |
| `resources` | lista de `resource` (todo el proyecto) | ✅ | ❌ **confirmado de solo lectura**: `'project.resources[0]' can be read but set access is not yet permitted for this member` | Vista plana de todos los recursos del proyecto — la gestión real sigue siendo `RESOURCE CREATE`/`RESOURCE DELETE` |
| `RoomOrderNodes` | lista de `RoomOrderNode` | ✅ | ✅ — ver [§9](#9--el-orden-de-las-salas-projectroomordernodes-lo-resuelve-directamente) | El orden de las salas |
| `tags` | lista de string | ✅ (vacía por defecto) | ❌ sin comando dedicado localizado: `resource set` sobre un índice de una lista vacía falla (`out of range`), y sobre la lista completa falla por tipo (`Invalid cast from String to List`) | Solo lectura práctica hoy — no se encontró forma de añadir etiquetas de proyecto por CLI |
| `templateType` | string, `null` salvo plantillas | ✅ | ✅ acepta cualquier string, **pero no es la vía real de «guardar como plantilla»** — es un flag crudo sin la lógica de plantilla detrás | Indica si el proyecto se guardó como plantilla; tocarlo a mano no convierte el proyecto en una plantilla funcional |
| `TextureGroups` | lista de `texturegroup` | ✅ | ✅ vía `TEXTUREGROUP CREATE/DELETE/RENAME` — reflejado aquí | Grupos de texturas (empaquetado, *streaming*) sin el IDE |

### Cómo llegar hasta aquí desde el MCP, no solo desde `eval`

El MCP `gamemaker-resource-tool` expone `resource_info`/`resource_set` como herramientas
genéricas (§3) — **no hace falta caer a `resourcetool eval` para tocar `project.*`**: el mismo
`expr=project.RoomOrderNodes[0].roomId` que funciona en `eval` funciona igual en la llamada
tipada del MCP.

### `configs`: configuraciones de build, no solo lectura

```bash
$ gm-cli resourcetool eval "config create name=Demo parent=Default"
Config 'Demo' created successfully based on parent 'Default'.
$ gm-cli resourcetool eval "resource info expr=project.configs.children[0]"
project.configs.children[0] members:
  children: list of ProjectConfig
  name: Demo
```

El árbol anida correctamente (`children` de `children`), así que un agente puede construir
jerarquías de configuración (`Default` → `Demo` → `Demo-Android`…) igual que en el panel de
configuraciones del IDE, sin abrirlo.

### `AudioGroups` / `TextureGroups`: ya eran gestionables, ahora también visibles desde `project`

`AUDIOGROUP CREATE`/`TEXTUREGROUP CREATE` ya estaban en el inventario de comandos de `07 · 13` —
lo que faltaba era saber que el resultado se puede **auditar de un vistazo** vía
`project.AudioGroups`/`project.TextureGroups`, en vez de fiarte solo del mensaje de éxito del
comando:

```bash
$ gm-cli resourcetool eval "audiogroup create name=audiogroup_musica"
$ gm-cli resourcetool eval "texturegroup create name=texgroup_ui"
$ gm-cli resourcetool eval "resource info expr=project.AudioGroups LIST"
project.AudioGroups table:
  audiogroup_default
  audiogroup_musica
```

### `IncludedFiles`: se crea, pero adjuntar el archivo real no funciona como `SOUND SETFILE`

`includedfile` ya figuraba entre los 17 tipos de `resource create` en `07 · 13` — el hueco real
es que **no hay un comando `INCLUDEDFILE SETFILE`** equivalente a `SOUND SETFILE`/`SPRITE
ADDFRAME` que copie el archivo dentro del proyecto. Lo único que acepta el recurso es el campo
`filePath`, y no copia bytes — **guarda la ruta tal cual, literal**, verificado:

```bash
$ gm-cli resourcetool eval "resource create type=includedfile name=archivo_prueba"
$ gm-cli resourcetool eval "resource set expr=archivo_prueba.filePath value=/tmp/datos_prueba.txt"
$ grep IncludedFiles -A2 mi-juego.yyp
"IncludedFiles":[
    {"$GMIncludedFile":"","%Name":"archivo_prueba","CopyToMask":-1,
     "filePath":"/tmp/datos_prueba.txt", …},
],
```

La ruta quedó tal cual en el `.yyp`, apuntando fuera del proyecto.

> ⚠️ **Actualización del 8 de septiembre de 2026 — ya no es un hallazgo parcial, es la
> [Trampa 8 de §0](#trampa-8--resource-create-typeincludedfile-deja-filepath-fuera-de-datafiles-y---errors-only-no-lo-detecta),
> confirmada con `gm-cli compile`.** Si dejas `filePath` vacío (el valor por defecto tras
> `RESOURCE CREATE`, sin tocarlo) o apuntando fuera del proyecto como en el ejemplo de arriba,
> **`gm-cli compile` no resuelve esa ruta**: el archivo no se copia al paquete, y el único rastro
> es un `WARNING :: datafile ... was NOT copied` que `--errors-only` silencia por completo (exit
> 0, sin salida). El valor correcto de `filePath` es el string literal `datafiles` — no una ruta
> absoluta ni relativa — con el archivo físico colocado a mano en `datafiles/<nombre-del-recurso>`
> dentro de la carpeta del proyecto; comparar contra un `.yyp` real con Included Files
> (`filePath:"datafiles"`) lo confirma. Detalle completo, con las dos compilaciones y la
> inspección del `.zip`, en la Trampa 8 de §0.

### `MetaData`: se lee, no se escribe — y las comillas importan

```bash
$ gm-cli resourcetool eval "resource info expr=project.MetaData KEYS"
['IDEVersion', 'PackageID', 'PackageName', 'PackagePublisher', 'PackageType', 'PackageVersion']
$ gm-cli resourcetool eval "resource info expr=project.MetaData['PackageName']"
project.MetaData['PackageName'] = Blank Pixel Project
$ gm-cli resourcetool eval "resource set expr=project.MetaData['PackageName'] value=Prueba"
project.MetaData['PackageName']: cannot determine member type
ResourceTool Failed
```

Dos hallazgos en uno: (a) para indexar un diccionario, `resourcetool` exige **comillas simples**
dentro de los corchetes — `project.MetaData["Clave"]` con dobles falla con `Unrecognized syntax`,
mientras que `project.MetaData['Clave']` funciona —; y (b) **la escritura de un valor de
diccionario está bloqueada** hoy, aunque la lectura funcione perfectamente. Si necesitas cambiar
`PackageName`/`PackageVersion` antes de publicar al Marketplace, edítalos desde el IDE.

### `Folders`: organizar el Asset Browser sin `folder=` repetido

```bash
$ gm-cli resourcetool eval "folder create folder=Enemigos/Robots"
Created Asset Browser folder path 'Enemigos/Robots'
$ gm-cli resourcetool eval "resource info expr=project.Folders LIST"
List has 2 items of type folder
```

Crea la jerarquía de carpetas de una vez con `FOLDER CREATE` y luego usa `folder=` en cada
`RESOURCE CREATE` para colocar ahí cada recurso — más ordenado que crear la carpeta de forma
implícita la primera vez que se usa.

### ⚠️ Trampa nueva: no renombres el proyecto con `resource set expr=project.name`

`project.name` **sí acepta escritura** — a diferencia de `FullName`, que la rechaza. Pero
hacerlo directamente deja el proyecto en un estado peor que `PROJECT RENAME`, verificado en vivo:

```bash
$ gm-cli resourcetool eval "resource set expr=project.name value=OtroNombre"
project.name: OtroNombre
Saved successfully
$ ls *.yyp
InvestigacionProjectRoot.yyp   OtroNombre.yyp      ← ¡las DOS quedan en disco!
```

`resource set expr=project.name` **crea un `.yyp`/`.resource_order` nuevo con el nombre nuevo,
pero no borra ni renombra el antiguo** — quedan dos `.yyp` en la misma carpeta, y cualquier
comando posterior que dependa de la autodetección (sin pasar la ruta explícita) puede resolver
el proyecto equivocado o fallar de forma confusa. `PROJECT RENAME`, en cambio, renombra limpio:

```bash
$ gm-cli resourcetool eval "project rename name=NombreFinal"
$ ls *.yyp
NombreFinal.yyp    ← un único archivo, correctamente renombrado
```

**Usa siempre `PROJECT RENAME name=<nuevo>`** para renombrar un proyecto — nunca `resource set
expr=project.name`. Si ya lo hiciste por la vía mala, borra a mano el `.yyp`/`.resource_order`
viejo antes de seguir.

### Nota sobre apuntar a un `.yyp` explícito

Hay **dos** formas, y las dos funcionan.

`gm-cli resourcetool eval "<comando>" <ruta-al-yyp>` acepta la ruta como **segundo argumento
posicional puro** (`gm-cli resourcetool eval --help` lo confirma: `[project] Path to the project
.yyp file`). Si hay más de un `.yyp` en la carpeta —por ejemplo, tras la trampa de arriba—
pásalo explícito y sin prefijo:

```bash
gm-cli resourcetool eval "resource info expr=project.name" "$(pwd)/NombreFinal.yyp"
```

> ❌ **Corrección del 08-09-2026.** Esta sección decía que `projectpath=` dentro del comando «sí
> funciona para `CHECK` … pero no para `RESOURCE INFO`/`RESOURCE SET` en general». **Es falso.**
> `PROJECTPATH` figura en la sección ***Global Arguments*** de `HELP` —junto a `PROJECTTOOL`,
> `PREFABSFOLDER` y `CONFIG`— y por tanto lo acepta **cualquier** comando, no solo `CHECK`:
>
> ```bash
> gm-cli resourcetool eval "resource info expr=project.name projectpath=$(pwd)/MiJuego.yyp"
> ```
>
> Es útil precisamente cuando no quieres hacer `cd` a la carpeta del proyecto — por ejemplo, al
> operar sobre varios proyectos desde un mismo script.

---

## 9 ter · Forzar un `eventNum` real cuando la whitelist de `subtype` es cerrada

Receta completa de la Trampa 9. Sirve para cualquier evento cuyo número real no tenga nombre
aceptado por `OBJECT EVENT FINDORCREATE` — todos los `ev_async_*` (HTTP, Save/Load, Steam,
Cloud, Networking, System, Social, Push, Audio Recording/Playback/Playback Ended, Dialog, Web
Image Load, Web IAP), `user1`-`user15`, y el GUI Begin/End real (que la whitelist mapea al
número equivocado, Trampa 3). Verificado de punta a punta el 8 de septiembre de 2026 en
`~/verif_audit_tmp` (`gm-cli init -t "Blank Pixel Game"`, borrado al terminar), `gm-cli` 2.3.0 /
`ResourceTool@2026.0.17`.

### Paso a paso

1. **Crea el objeto** (si no existe) y **un evento de la misma familia** (`draw` o `other`) con
   cualquier nombre que la whitelist acepte — el nombre exacto no importa, solo la familia:
   ```bash
   gm-cli resourcetool eval "resource create type=object name=obj_x"
   gm-cli resourcetool eval "object event findorcreate name=obj_x type=other subtype=outside"
   ```
2. **Localiza el índice** del evento recién creado en la lista cruda:
   ```bash
   gm-cli resourcetool eval "resource info expr=obj_x.eventList list"
   ```
   (el orden es el de creación; si es el único evento `other`, es el último índice de la lista).
3. **Confirma el número que trae y fuerza el real** — este paso no pasa por la whitelist de
   `FINDORCREATE`:
   ```bash
   gm-cli resourcetool eval "resource info expr=obj_x.eventList[N]"
   gm-cli resourcetool eval "resource set expr=obj_x.eventList[N].eventNum value=<número real>"
   ```
4. **Verifica con `object event list`** que `resourcetool` ya reconoce el evento real:
   ```bash
   gm-cli resourcetool eval "object event list name=obj_x"
   ```
5. **Renombra (o crea) el `.gml`** con el nombre que corresponde al número real —
   `Draw_<N>.gml` u `Other_<N>.gml` (tabla completa en [§2](#2--dónde-va-cada-gml-el-nombre-exacto-de-archivo)).
   El archivo que dejó `FINDORCREATE` lleva el nombre del número **equivocado** (Trampa 3); si no
   lo renombras, `gm-cli compile` **no avisa**, pero el código no vive donde el evento real lo
   busca:
   ```bash
   mv objects/obj_x/Other_0.gml objects/obj_x/Other_62.gml   # ejemplo: Async - HTTP
   ```
6. **Escribe el código real en el archivo renombrado** y compila:
   ```bash
   gm-cli compile
   ```

### Números reales verificados en esta sesión

| Evento | `eventType` | `eventNum` real | Nombre en `object event list` tras el parche |
|---|---|---|---|
| GUI Begin | 8 (`ev_draw`) | 74 | `Event_Draw_DrawGUIBegin` |
| GUI End | 8 (`ev_draw`) | 75 | (no verificado directamente esta sesión; simétrico a GUI Begin — verifícalo con `object event list` antes de confiar en él a ciegas) |
| Async - HTTP | 7 (`ev_other`) | 62 | `Event_Async_HTTP` |
| Async - Dialog | 7 (`ev_other`) | 63 | `Event_Async_Dialog` |
| Async - System | 7 (`ev_other`) | 75 | `Event_Async_SystemEvent` |
| User Event 1 | 7 (`ev_other`) | 11 | `Event_Other_UserN` (detalle `1`) |

Para el resto de `ev_async_*` (Save/Load, Steam, Cloud, Networking, Social, Push, Audio
Recording/Playback/Playback Ended, Web Image Load, Web IAP) y `user2`-`user15`, la técnica es la
misma pero el número exacto no se verificó uno a uno en esta sesión — confírmalo con
`object event list` después del parche, igual que aquí, antes de dar el número por bueno; los
números de los `ev_async_*` están en el manual oficial
(`The_Asset_Editors/Object_Properties/Async_Events/`) y en
[`08 · 21` §10](../08%20-%20Referencia%20GML%20completa/21%20-%20Constantes%20que%20el%20manual%20abrevia.md#10--las-173-constantes-de-evento-ev_-para-event_perform).

> ⚠️ **Un informe de prueba (`r8-prueba-coop.md` §8.1) afirmó que el evento Async - System
> «no se puede crear por ningún nombre» y que era una excepción sin rodeo a esta misma receta —
> verificado de nuevo el 8 de septiembre de 2026 y **no se sostiene**. `object event findorcreate
> … subtype=async_system` sí se rechaza (reproducido igual: la whitelist de `other` no incluye
> ningún `async_*`), pero el rodeo de esta sección **funciona igual que para HTTP/Dialog**: creado
> con `eventNum=75` a mano, `object event list` lo reconoce como `Event_Async_SystemEvent`,
> compila limpio, y — la comprobación que faltaba, no solo «compila» — **se disparó de verdad en
> tiempo de ejecución**, comprobado dos veces: con `event_perform_async(ev_async_system_event,
> ds_map_create())` simulándolo a mano, y con el disparo real que hace el propio motor al iniciar
> el subsistema de audio (el manual del evento Sistema lo documenta: fuera de HTML5, se dispara
> una vez al arrancar el juego). Las dos vías ejecutaron el código de `Other_75.gml`. La única
> forma de que pareciera no funcionar es llamar a `game_end()` en el mismo paso que
> `event_perform_async()`: el evento se encola para procesarse ese mismo cuadro, y terminar el
> juego antes de que le toque lo corta — un error de la prueba, no de la técnica.**

### Qué sigue sin tener solución por esta vía

El asset **Extensión** no se puede crear por CLI/MCP de ninguna forma — a diferencia de un
evento, no hay un recurso ya creado cuyo campo crudo parchear: `resource create type=extension`
falla antes de llegar a existir (`Resource type 'extension' is not creatable`, verificado de
nuevo el 8 de septiembre de 2026). Sigue siendo cierto que hace falta el IDE para ese asset
concreto — ver [`07 · 22`](../07%20-%20Ecosistema/22%20-%20Crear%20una%20extensión%20nativa%20%28guía%20en%20español%29.md).

---

## 9 quater · Cuatro cosas que se daban por «solo IDE visual» — dos se abren, una se acota y una se confirma

Una auditoría anterior (`git log` del 8 de septiembre de 2026, «Los validadores comprueban la
aridad, y tres "no se puede" más eran falsos») examinó 30 afirmaciones de imposibilidad de esta
biblioteca y dejó 4 sin verificar por parecer atadas a un editor visual del IDE (presets de
partículas, capas del editor de rooms, troceado de sprites, GMRT). No hay ningún informe aparte
en `_indice/auditorias/` para esas 4 — la única traza es el mensaje de ese commit —, así que esta
sesión las verificó desde cero, en vivo, el 8 de septiembre de 2026, en un proyecto de prueba
bajo `~` (`gm-cli init -t "Blank Pixel Game"`, borrado al terminar), `gm-cli` 2.3.0 /
`ResourceTool@2026.0.17`.

### 1 · Presets de partículas — se puede configurar un emitter completo por CLI, pero no enlazarlo a un preset real, y solo cabe uno por sistema

El asset **Particle System** no tiene ningún comando dedicado en absoluto (no hay `PARTICLE` ni
`EMITTER` entre los 30 comandos de `resourcetool` — [§0 Trampa 7](#trampa-7--antes-de-dar-un-comando-por-imposible-prueba-resource-info-exprproject-y-help-comando)
enseña a comprobarlo con `resource types`, que no lo lista). Todo pasa por la raíz de expresión
genérica:

```bash
$ gm-cli resourcetool eval "resource create type=particlesystem name=part_test"
$ gm-cli resourcetool eval "resource info expr=part_test.emitters"
List has 0 items of type emitter          # ← el conteo miente, ver más abajo
$ gm-cli resourcetool eval "resource set expr=part_test.emitters[0].name value=preset_fuego"
part_test.emitters[0].name: preset_fuego
Saved successfully
```

Indexar `[0]` sobre una lista de emitters que el propio `resource info` acababa de reportar como
vacía **crea de verdad el primer emitter**, con los ~50 campos completos que trae un emitter real
(`shape`, `distribution`, `speedMin/Max`, `startColour`/`midColour`/`endColour`, `spriteId`,
`regionW/H`, `GMPresetName`…) — todos escribibles uno a uno con `resource set` y confirmados en
el `.yy` final. `gm-cli compile` termina limpio. **Pero esto no generaliza**: probar
`part_test.emitters[1]` con la lista en 1 elemento da `is out of range (0..0)` — a diferencia de
`project.RoomOrderNodes`, la lista de emitters **no crece más allá del primero** por esta vía;
un Particle System con varios emitters (la forma normal de construir un efecto real: uno para el
núcleo, otro para chispas, otro para humo) **no se puede montar completo por CLI/MCP** — hace
falta el editor visual para el segundo emitter en adelante. Y el mismo auto-relleno **no es
general**: se probó también sobre `project.LibraryEmitters[0]` (lista vacía) y sobre
`obj_x.eventList[0]` de un objeto recién creado sin eventos, y ambos fallan con
`is out of range (list is empty)` — el comportamiento es específico del campo `emitters` de un
`particlesystem`, no una regla del motor de `resourcetool`.

El campo `GMPresetName` **se puede escribir** (`resource set
expr=part_test.emitters[0].GMPresetName value=Fire` responde `Saved successfully` y compila
limpio), pero es **cosmético**: no copia ni un solo valor real del preset «Fire» al emitter — se
comprobó guardando el campo y releyéndolo, sin que ningún otro campo (`shape`, colores,
velocidad…) cambiara. Enlazar de verdad un emitter a un preset, con todos sus valores aplicados,
es una operación del editor visual
([`02 · 05 §2.3`](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20part%C3%ADculas%20nuevo.md#23-presets-propios-compartidos-entre-assets))
que no tiene equivalente por CLI.

**El rodeo real para replicar un preset sin abrir el IDE**: los 10 presets incorporados
(`Electricity`, `Embers`, `Embers 2`, `Fire`, `Flame Intensity`, `Rain`, `Smoke`, `Smoke 2`,
`Sparks`, `Warp Centre`, `Warp Lines` — [`02 · 05` §2.2](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20part%C3%ADculas%20nuevo.md#22-efectos-predefinidos-library))
**están en disco, dentro del propio toolchain instalado**, no solo dentro de la memoria del IDE:

```
GameMaker.app/Contents/MacOS/arm64/packages/gm-ide-prefabs/gm-particle-presets/
  io.gamemaker.gmparticlepresets-1.0.0.yymps      ← ZIP normal (unzip lo abre)
    particlelib/GM_Fire/GM_Fire.yy                ← el emitter "Fire" completo, en JSON
    particlelib/GM_Smoke/GM_Smoke.yy
    ... (los 10 presets, cada uno con su .yy)
    sprites/spr_Fire/spr_Fire.png                 ← sprites que usan los presets con textura
```

Cada `.yy` trae los valores exactos (`shape`, `distribution`, `directionMin/Max`,
`lifetimeMin/Max`, `startColour`/`midColour`/`endColour`, `sizeMin/Max`, `speedMin/Max`,
`spriteId`…) que el editor visual aplicaría al pulsar «Select Particles → Fire». Un agente puede
leer ese `.yy`, y reproducir el efecto campo a campo con una secuencia de `resource set
expr=<sistema>.emitters[0].<campo> value=<valor>` sobre su propio emitter — funcionalmente
idéntico al preset, aunque `GMPresetName` no quede enlazado. Ruta verificada en esta sesión
(la del `.app` descrito arriba puede variar de instalación a instalación; confírmala con
`find "<ruta de GameMaker.app>" -iname "*particle-presets*"`).

### 2 · Capas de UI del editor de rooms — limitación real, confirmada, sin campo crudo que la esquive

`ROOM LAYER CREATE TYPE=` solo admite `INSTANCE | ASSET | BACKGROUND | PATH | TILE | EFFECTS`
([§2](#2--dónde-va-cada-gml-el-nombre-exacto-de-archivo) documenta los 6). Pedir `TYPE=UI` —la
capa nueva de LTS 2026 que contiene Flex Panels, la forma recomendada de montar HUDs y menús
([`09 - Manual oficial/.../UI_Layers.md`](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Room_Properties/UI_Layers.md)) — se rechaza limpio:

```bash
$ gm-cli resourcetool eval "room layer create room=Room1 name=capa_ui type=UI"
Invalid value 'UI' for 'TYPE' argument.  Expected format: INSTANCE | ASSET | BACKGROUND | PATH | TILE | EFFECTS
```

A diferencia de la Trampa 9, **aquí no hay campo crudo que rescate el caso**: las capas de UI son
**globales al proyecto, no por room** (el manual lo dice explícito: «viven en la "UI Folder"
global… compartida por todas las rooms»), y ni `project` (sus 18 miembros de
[§9 bis](#9-bis--la-raíz-project-18-miembros-probados-uno-a-uno) no incluyen nada de UI/Flexpanel)
ni ninguna room concreta exponen una raíz de expresión para ellas. Se contrastó además contra
`11 - Código descargado/` — ningún `.yy` de room de los proyectos reales descargados usa un
`resourceType` de capa fuera de los 6 conocidos (`GMRAssetLayer`, `GMRBackgroundLayer`,
`GMRInstanceLayer`, `GMRLayer`, `GMRPathLayer`, `GMRTileLayer`) — no hay un séptimo tipo
serializado que copiar. `resourcetool` no tiene tampoco ningún comando `FLEXPANEL`/`UI`.

**Conclusión, la única de las 4 que se confirma como limitación real sin rodeo**: montar una capa
de UI y sus Flex Panels *como recurso de diseño* (lo que vería el editor de rooms) requiere el
IDE visual — pídeselo al humano, o dile con precisión qué estructura de Flex Panels necesitas
para que la monte. **Hay un camino distinto, no equivalente pero funcional, que no pasa por el
editor de rooms en absoluto**: construir la interfaz en tiempo de ejecución con las
[funciones de Flex Panel](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Flex_Panels/Flex_Panels.md)
(`flexpanel_create_node` y familia) desde GML — el propio manual lo cubre en
[UI_Layers_At_Runtime.md](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Room_Properties/UI_Layers_At_Runtime.md).
Es código, no un recurso `.yy`, así que sí es alcanzable para un agente sin el IDE, pero no
sustituye a «crear la capa de UI que pide la tarea» si lo que hace falta es justo el recurso de
diseño.

### 3 · Troceado de sprites — `SPRITE ADDFRAME` no trocea, pero trocear antes y añadir cada trozo sí funciona

El editor de sprites del IDE detecta el sufijo `_stripN` en el nombre de archivo y divide la
imagen en `N` fotogramas automáticamente al importarla
([`09 - Manual oficial/.../Sprite_Strips.md`](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sprite_Properties/Sprite_Strips.md)).
`SPRITE ADDFRAME` **no reproduce esa convención**: se probó con una tira de 3 fotogramas de
16×16 (48×16 en total), primero con un nombre de archivo cualquiera y después con el sufijo
`_strip3` exacto que pide el manual — en los dos casos el sprite resultante quedó con
**1 solo fotograma de 48×16** (la imagen completa, sin trocear):

```bash
$ gm-cli resourcetool eval "sprite addframe name=spr_x path=prueba_strip3.png"     # sin _stripN
$ gm-cli resourcetool eval "resource info expr=spr_x.width"    # 48
$ gm-cli resourcetool eval "sprite addframe name=spr_y path=..._strip3.png"        # con _stripN
$ gm-cli resourcetool eval "resource info expr=spr_y.width"    # 48 — igual, no trocea
```

`ADDFRAME` es una operación literal: «copia este PNG tal cual como un fotograma nuevo», sin
inspeccionar el nombre del archivo ni su contenido para decidir dividirlo.

**El rodeo, verificado de punta a punta**: trocear la imagen **antes** de dársela a
`resourcetool`, con cualquier herramienta de imagen (`ImageMagick` en esta sesión), y llamar a
`SPRITE ADDFRAME` una vez por trozo, en orden:

```bash
$ magick tira.png -crop 16x16+0+0 +repage tile_0.png
$ magick tira.png -crop 16x16+16+0 +repage tile_1.png
$ magick tira.png -crop 16x16+32+0 +repage tile_2.png
$ gm-cli resourcetool eval "sprite addframe name=spr_z path=tile_0.png frame=LAST"
$ gm-cli resourcetool eval "sprite addframe name=spr_z path=tile_1.png frame=LAST"
$ gm-cli resourcetool eval "sprite addframe name=spr_z path=tile_2.png frame=LAST"
$ gm-cli resourcetool eval "resource info expr=spr_z.width"    # 16
$ gm-cli resourcetool eval "resource info expr=spr_z.frames"   # List has 3 items
```

Resultado: sprite de 16×16 con 3 fotogramas — **funcionalmente idéntico** al que produciría
arrastrar la tira al IDE, verificado con `gm-cli compile` limpio. Un agente sin acceso al editor
de sprites puede trocear cualquier hoja de sprites con una herramienta de imagen normal y montar
la animación fotograma a fotograma; el troceado en sí no es una operación de `resourcetool`,
pero el resultado sí se consigue enteramente por CLI/MCP.

### 4 · GMRT — sí es accesible desde `gm-cli`, sin el IDE; lo que falló en esta sesión fue un requisito de máquina, no una limitación de la herramienta

GMRT (el nuevo runtime, [`02 · 03`](../02%20-%20Novedades%202026/03%20-%20GMRT%20-%20El%20nuevo%20runtime.md))
tiene su propia sección de **Preferences** en el IDE (`Path to GMRT`, generador de CMake, tipo de
build…) que sí es exclusiva del IDE — son ajustes globales del programa, guardados fuera de
cualquier proyecto (`~/Library/Application Support/GameMakerStudio2-LTS2026/<usuario>/local_settings.json`
en macOS), y `resourcetool` no toca nunca ese archivo porque opera sobre `.yyp`/`.yy`, no sobre
preferencias de la IDE. Hasta ahí, la afirmación «GMRT es solo IDE» sería cierta.

Pero **compilar o ejecutar con GMRT como toolchain no pasa por esas preferencias en absoluto**:
`gm-cli compile --help` y `gm-cli run --help` documentan `--toolchain` con el ejemplo literal
`GMRT@0.18`, exactamente igual que `GMS2@2024.14.4`:

```bash
$ gm-cli compile --toolchain "GMRT@0.21.0" --errors-only
Command failed:
You must install .NET to run this application.
App: .../gmpm/lib/node_modules/@gm-tools/gmpm-mac-arm64/.../gmpm
Failed to resolve libhostfxr.dylib [not found]
```

`gm-cli` **intentó por su cuenta resolver/instalar GMRT** invocando su propio gestor de paquetes
(`gmpm`, el mismo Package Manager que usa el IDE, pero disparado aquí desde la CLI sin abrir
ninguna ventana) — el fallo fue que esta máquina no tiene **.NET 8** instalado, un requisito que
el propio [`02 · 03` §4.1](../02%20-%20Novedades%202026/03%20-%20GMRT%20-%20El%20nuevo%20runtime.md)
ya documenta como obligatorio para GMRT, con o sin IDE (`which dotnet` → no encontrado en esta
sesión). No es un límite de `resourcetool`/`gm-cli`: es una dependencia de sistema que falta en
esta máquina concreta.

**Conclusión**: elegir GMRT como toolchain de compilación/ejecución **es una operación de
`gm-cli`, alcanzable sin el IDE visual**, igual que elegir una versión de GMS2. Lo que sigue
siendo exclusivo del IDE son las *preferencias* de GMRT (rutas de herramientas de terceros,
generador de CMake…), que un agente normal no necesita tocar salvo que el proyecto exija una
toolchain de compilación personalizada.

### 5 · «Página de Textura Separada» de un sprite — no hay campo booleano, pero un grupo de textura dedicado consigue el mismo efecto

Verificado en vivo el 8 de septiembre de 2026, construyendo un juego 3D
(`_indice/auditorias/r8-prueba-3d.md`). `04 · 29 §3` exige que un sprite que se dibuja con
`gpu_set_texrepeat(true)` esté marcado como **Separate Texture Page** en el editor de sprites —
si no, la repetición de UV puede pintar trozos de los sprites vecinos de la misma página. Esa
casilla **no tiene ningún campo directo** alcanzable por `resourcetool`:

```bash
$ gm-cli resourcetool eval "resource info expr=spr_piso KEYS"
# 33 campos listados, incluidos DynamicTexturePage y textureGroupId —
# ningún SeparateTexturePage entre ellos
```

`DynamicTexturePage` es un concepto distinto (grupos de texturas *dinámicos*, cargados en tiempo
de ejecución — [`Settings/Texture_Information/Dynamic_Textures.md`](../09%20-%20Manual%20oficial/manual-lts-2026-es/Settings/Texture_Information/Dynamic_Textures.md)),
no la casilla de aislamiento de página que pide `gpu_set_texrepeat`.

**El rodeo real, con el mismo efecto práctico**: crear un grupo de textura dedicado y asignarle
el sprite. Un grupo de texturas se empaqueta en sus propias páginas, así que un sprite que vive
solo en su grupo no comparte página con nada del grupo `Default`:

```bash
gm-cli resourcetool eval "texturegroup create name=tg_piso"
gm-cli resourcetool eval "texturegroup set group=tg_piso resources=spr_piso"
```

Ambos subcomandos existen de verdad (`resourcetool eval "help texturegroup"` los lista, junto a
`DELETE`/`RENAME`/`LIST`/`USAGES`) y compilan limpio. No enlazan con el campo `SeparateTexturePage`
del `.yy` de un modo verificable desde fuera (no hay forma de leer «¿esta página es exclusiva?»
por `resourcetool`), pero consiguen el resultado que pide `04 · 29 §3`: el sprite deja de
compartir página con sus vecinos, que es justo lo que evita el bug de repetición.

---

## 10 · El modo por lotes (`resourcetool script`): mucho más rápido que encadenar `eval`

**No estaba documentado ni en `SKILL.md` ni en la tabla de comandos de `07 · 13`** — lo señaló
`r5-revalidacion.md` como un hallazgo propio del agente, descubierto leyendo `resourcetool
--help`. Verificado en esta sesión, con tiempos reales, el **8 de septiembre de 2026**.

### 10.1 Qué es

`gm-cli resourcetool script <archivo> [proyecto.yyp]` ejecuta una **lista de comandos**, uno por
línea, en un único proceso — la misma sintaxis que usarías dentro de `resourcetool eval "<…>"`,
sin las comillas exteriores:

```bash
$ gm-cli resourcetool script --help
USAGE
  gm-cli resourcetool script <file>
  gm-cli resourcetool script --help

ARGUMENTS
   file      Path to the script file
  [project]  Path to the project .yyp file
```

> 💡 **Los comentarios del archivo de lote empiezan por `#`, no por `//`.** No es obvio —el
> resto de la herramienta habla en GML, donde el comentario es `//`— y un lote de cuatrocientas
> líneas es justo donde quieres explicar qué hace cada bloque. Verificado el 08-09-2026:
>
> ```
> $> # esto es un comentario
> $> RESOURCE LIST TYPE=room        ← se ejecuta
> $> // y esto otro
> Unknown Command: // y esto otro
> ResourceTool Failed
> ```
>
> Las líneas en blanco sí se ignoran.

Ejemplo real, un archivo de texto con seis comandos:

```
RESOURCE CREATE TYPE=object NAME=obj_lote_1
RESOURCE CREATE TYPE=object NAME=obj_lote_2
RESOURCE CREATE TYPE=object NAME=obj_lote_3
OBJECT EVENT FINDORCREATE NAME=obj_lote_1 TYPE=create
OBJECT EVENT FINDORCREATE NAME=obj_lote_1 TYPE=step SUBTYPE=step_normal
OBJECT EVENT FINDORCREATE NAME=obj_lote_1 TYPE=draw SUBTYPE=draw_normal
```

```bash
gm-cli resourcetool script lote.txt mi-juego.yyp
```

La salida repite cada línea (`$> RESOURCE CREATE …`) seguida de su resultado — se lee igual que
una sesión de `repl`, pero sin interacción.

### 10.2 Cuánto compensa — medido en esta sesión, no una estimación

Los mismos seis comandos de arriba, por las dos vías, sobre el mismo proyecto de prueba:

| Vía | Comando | Tiempo real |
|---|---|---|
| 6 llamadas `eval` separadas (una por proceso) | `gm-cli resourcetool eval "…"` × 6, encadenadas con `&&` | **8,8 s** |
| 1 llamada `script` (un solo proceso) | `gm-cli resourcetool script lote.txt mi-juego.yyp` | **1,4 s** |

**≈6× más rápido** con solo seis comandos. La causa es la misma que documenta la Trampa 2 (§0):
cada invocación de `resourcetool` paga el coste de arranque de `npx` (verificación de versión
contra el registro) una vez; `script` paga ese coste **una sola vez** para todo el lote, en vez
de una vez por comando. Con los 23 recursos + 39 eventos que construyó `r5-revalidacion.md` para
un juego real, la diferencia se cuenta en decenas de segundos ahorrados, no en menos de uno.

### 10.3 Qué pasa si un comando del lote falla — se para, no sigue

Verificado a propósito con un lote de tres líneas donde la segunda pide un tipo de recurso que no
existe:

```
RESOURCE CREATE TYPE=object NAME=obj_lote_error_a
RESOURCE CREATE TYPE=tipo_que_no_existe NAME=x
RESOURCE CREATE TYPE=object NAME=obj_lote_error_b
```

Resultado: `obj_lote_error_a` se creó, la segunda línea falló (`Unknown resource type
'tipo_que_no_existe'`) y **la tercera línea nunca se ejecutó** — el proceso completo salió con
`exit 1`. `script` no es transaccional (lo ya ejecutado antes del fallo se queda hecho) ni
tolerante a fallos (no sigue con las líneas siguientes): es secuencial y se detiene en el primer
error real, igual que el ciclo de `gm-cli compile` de §1.

### 10.4 Cuándo usar `script` en vez de `eval`

| Situación | Usa |
|---|---|
| Crear un lote de recursos/eventos que ya sabes de antemano (varios objetos, sus eventos, varias salas en el orden que quieres — §9.2) | `script` — más rápido, y el archivo del lote queda como documentación de lo que se creó |
| Necesitas leer el resultado de un comando (`RESOURCE INFO`, `ROOM ITEM LIST`…) para decidir el siguiente | `eval`, uno a uno — `script` no te deja inspeccionar la salida de una línea antes de que corra la siguiente |
| Vas a verificar cada evento con `object event list` según se crea (§2.5, para evitar las Trampas 3/4 de numeración) | `eval` intercalado con la verificación, o `script` para el lote y **una sola** verificación con `object event list` al final sobre todos los objetos |
| Trabajas por MCP (`gamemaker-resource-tool`) en una sesión interactiva | El MCP ya es rápido por llamada tipada — `script` es una ventaja de la vía `eval`/CLI, no del MCP |
| **Reordenar `project.RoomOrderNodes`** (`RESOURCE SET` sobre salas que ya existen — §9.3) | **`eval`, siempre — nunca `script`.** Ver el aviso justo debajo: es la única excepción confirmada a la regla práctica de esta sección. |

⚠️ **Excepción verificada el 8 de septiembre de 2026**
([`_indice/auditorias/r6-regresion.md` §3.2](../_indice/auditorias/r6-regresion.md#32-hallazgo-nuevo--resourcetool-script-no-persiste-resource-set-sobre-roomordernodes)):
un lote de `resourcetool script` con siete líneas de `RESOURCE SET
expr=project.RoomOrderNodes[i].roomId` respondió `Saved successfully` en cada línea y
`ResourceTool Successful` al final — pero el `.yyp` en disco, leído justo después, conservaba el
orden anterior al lote **por completo**, como si nunca se hubiera ejecutado. Las mismas siete
operaciones, una a una con `eval`, sí persistieron. La regla práctica de abajo («más de dos o tres
comandos seguidos → usa `script`») **no vale para esta operación concreta**: reordenar salas
siempre por `eval`, aunque sean muchas llamadas y el ahorro de tiempo del lote sea tentador.
Detalle completo, con la regla de «reordena después de borrar, nunca antes», en
[§9.3 bis](#93-bis--dos-matices-nuevos-encontrados-construyendo-un-juego-real-de-punta-a-punta).

**Regla práctica**: si vas a lanzar más de dos o tres comandos de `resourcetool` seguidos que no
dependen del resultado de los anteriores, escribe un archivo de lote y usa `script` — el ahorro
de tiempo (~6× en esta medición) se nota en cualquier proyecto real, donde crear el andamiaje
inicial de objetos y eventos son fácilmente decenas de comandos. La única excepción confirmada
hasta hoy es reordenar `project.RoomOrderNodes` (recuadro de arriba).

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
- [`_indice/auditorias/r5-prueba-e2e.md`](../_indice/auditorias/r5-prueba-e2e.md) — la prueba end-to-end (juego completo desde cero) que descubrió las Trampas 5 y 6 de este documento.
- [`_indice/auditorias/r5-revalidacion.md`](../_indice/auditorias/r5-revalidacion.md) — la revalidación que señaló los tres huecos de §9 y §10 (orden de salas, el aviso de `instance_deactivate_all` que solo vivía en `04/41`, y el modo por lotes de `resourcetool`); su §5.1 documenta el rodeo manual que la corrección del 8 de septiembre de 2026 dejó innecesario — ver la nota en ese mismo punto.
- [`_indice/auditorias/r6-prueba-narrativa.md`](../_indice/auditorias/r6-prueba-narrativa.md) — la prueba narrativa que descubrió la Trampa 8 (`filePath` vacío en los Included Files creados por `resourcetool`) construyendo un juego con diálogos y finales ramificados de principio a fin.
- [`06 - Assets y Scripts/scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml) — `save_ensure_dir()` trae ya el parche de la Trampa 6, con el porqué documentado en el propio script.
- [`06 - Assets y Scripts/README.md` §«Pruebas realizadas»](../06%20-%20Assets%20y%20Scripts/README.md) — primera constancia de la `NullReferenceException` de sprites vacíos que amplía [§7.7](#77-un-segundo-hallazgo-de-esta-sesión---errors-only-también-esconde-por-completo-un-nullreferenceexception-real-del-assetcompiler).
- [`02 · 05 — Sistema de partículas nuevo`](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20part%C3%ADculas%20nuevo.md) — qué es el Particle System Editor, los 10 presets incorporados y cómo funcionan los presets propios por proyecto.
- [`02 · 03 — GMRT, el nuevo runtime`](../02%20-%20Novedades%202026/03%20-%20GMRT%20-%20El%20nuevo%20runtime.md) — arquitectura, instalación y requisitos (.NET 8) de GMRT.
- [`09 - Manual oficial/.../UI_Layers.md`](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Room_Properties/UI_Layers.md) — capas de UI y Flex Panels en el editor de rooms.
- [`09 - Manual oficial/.../Sprite_Strips.md`](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sprite_Properties/Sprite_Strips.md) — la convención `_stripN` que el editor de sprites detecta y `resourcetool` no.

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
- [`_indice/auditorias/r5-prueba-e2e.md`](../_indice/auditorias/r5-prueba-e2e.md) (8 de
  septiembre de 2026) — construcción en vivo de un juego completo (`~/gm_prueba_e2e/salto_nova`)
  con esta biblioteca como única fuente; origen de las Trampas 5 y 6 y de §7.6.
- [`_indice/auditorias/r5-revalidacion.md`](../_indice/auditorias/r5-revalidacion.md) (8 de
  septiembre de 2026) — señaló los tres huecos que cierran §9 y §10 de este documento.
- Ejecución en vivo en un segundo proyecto de prueba bajo `~` (`~/gm_investigacion_r6`, creado
  con `gm-cli init -t "Blank Pixel Game"` y borrado al terminar), `gm-cli` 2.3.0 /
  `ResourceTool@2026.0.17` — 8 de septiembre de 2026. Fuente directa de §9 (lectura completa del
  `HELP` de `resourcetool` buscando un comando de orden de salas; `RESOURCE INFO
  expr=RoomOrderNodes` → `'RoomOrderNodes' not found at root`; creación de tres salas y borrado
  de la sala de plantilla para confirmar que `RoomOrderNodes` crece por orden de creación;
  `ROOM INSTANCE CREATE` + borrar y recrear una sala para confirmar que se pierde su contenido;
  edición manual de `RoomOrderNodes` seguida de `CHECK` y `gm-cli compile --errors-only` para
  confirmar que el orden manual sobrevive y el proyecto sigue siendo válido) y de §10 (`gm-cli
  resourcetool script --help`; comparación cronometrada de 6 comandos por `eval` encadenado
  frente a los mismos 6 en un archivo de `script`; lote de 3 líneas con un tipo de recurso
  inválido en medio para confirmar que `script` se detiene en el primer error).
- **Corrección del 8 de septiembre de 2026** (§0 Trampa 7, §9, §9 bis): ejecución en vivo en un
  proyecto de prueba bajo `~` (`gm-cli init -t "Blank Pixel Game"`, borrado al terminar), `gm-cli`
  2.3.0 / `ResourceTool@2026.0.17`. Fuente directa de: `resource info expr=project` (descubrimiento
  de la raíz y sus 18 miembros); `resource set expr=project.RoomOrderNodes[i].roomId` reasignado
  en las cuatro posiciones de un proyecto con 4 salas hasta lograr una permutación completa,
  verificada leyendo el `.yyp` y confirmada con `check` + `gm-cli compile --errors-only` (`exit
  0`); lectura y escritura probadas en los 18 miembros de `project` uno a uno (`AudioGroups`,
  `configs`, `defaultScriptType`, `Folders`, `ForcedPrefabProjectReferences`, `FullName`,
  `IncludedFiles`, `isDnDProject`, `isEcma`, `LibraryEmitters`, `MetaData`, `name`, `parent`,
  `resources`, `RoomOrderNodes`, `tags`, `templateType`, `TextureGroups`); creación real de un
  `audiogroup`, un `texturegroup`, una `folder` anidada, un `config` hijo y un `includedfile`,
  confirmados después en `project.*`; reproducción de que `resource set expr=project.name` deja
  un `.yyp` huérfano mientras que `PROJECT RENAME` no; y reverificación en vivo, con los números
  reales del manual (`Async_Events.md`), de que `OBJECT EVENT FINDORCREATE` sigue rechazando un
  `subtype` numérico (62, 68 y 72 probados, todos rechazados con `Invalid subtype`) y de que el
  asset Extensión sigue sin poder crearse (`resource create type=extension` → `Resource type
  'extension' is not creatable`) — la de la Extensión se confirmó cierta, no se corrigió.
- ❌ **Corrección del 8 de septiembre de 2026 (Trampa 9) — la entrada anterior sobre eventos
  Async estaba incompleta y llevó a una conclusión falsa.** Esa reverificación probó un único
  camino (`FINDORCREATE` con `subtype` numérico) y, al ver que lo rechazaba, dio por buena la
  afirmación previa de que «los eventos Async siguen sin poder crearse por `resourcetool`» — el
  mismo patrón que la propia Trampa 7 advierte: un comando cerrado no prueba que la propiedad
  cruda sea inalcanzable. Reproducido en un tercer proyecto de prueba bajo `~`
  (`~/verif_audit_tmp`, `gm-cli init -t "Blank Pixel Game"`, borrado al terminar), `gm-cli`
  2.3.0 / `ResourceTool@2026.0.17` — 8 de septiembre de 2026: `OBJECT EVENT FINDORCREATE` con un
  nombre de la whitelist (`gui_begin`, o `outside`/`user0` para Other) crea el evento con el
  número **equivocado** (bug ya documentado en la Trampa 3), pero `RESOURCE SET
  expr=<objeto>.eventList[i].eventNum value=<número real>` **sí lo corrige** — el evento pasa a
  listarse como `Event_Draw_DrawGUIBegin`, `Event_Async_HTTP` (62) o `Event_Other_UserN` detalle
  `1` (`user1`, `eventNum=11`) según el caso, y `gm-cli compile` termina con `Compilation
  finished` en los tres. Requiere además renombrar/escribir el `.gml` con el nombre de archivo
  que corresponde al número real (`Draw_74.gml`, `Other_62.gml`…): el archivo que dejó
  `FINDORCREATE` sigue llevando el nombre del número equivocado, y aunque `gm-cli compile` no
  avisa si no se renombra, el código real solo se ejecuta desde el archivo correcto. Receta
  completa en [§9 ter](#9-ter--forzar-un-eventnum-real-cuando-la-whitelist-de-subtype-es-cerrada).
- [`_indice/auditorias/r6-prueba-narrativa.md`](../_indice/auditorias/r6-prueba-narrativa.md) (8
  de septiembre de 2026) — construcción en vivo de un juego narrativo completo (`~/gm_prueba_narrativa`)
  que descubrió la Trampa 8; su §6.1 trae la primera reproducción del bug de `filePath`.
- **Corrección del 8 de septiembre de 2026** (§0 Trampa 8, §1, §7.7, §8): reproducción
  independiente en dos proyectos de prueba bajo `~` (`~/gm_prueba_includedfiles` y
  `~/gm_prueba_sprite_vacio`, ambos creados con `gm-cli init -t "Blank Pixel Game"` y borrados al
  terminar), `gm-cli` 2.3.0 / `ResourceTool@2026.0.17`. Fuente directa de: la confirmación de que
  `resource create type=includedfile` deja `"filePath":""` sin crear `datafiles/` ni copiar
  ningún byte; la comparación con el `filePath:"datafiles"` real de
  `11 - Código descargado/extensiones_oficiales/GMEXT-GameCenter/source/GameCenter_gml/GameCenter.yyp`;
  las dos compilaciones completas (con y sin `--errors-only`) antes y después de la corrección,
  con el `WARNING :: datafile ... was NOT copied` real solo visible sin el flag; la apertura
  directa de `game.zip` (`unzip -l`) confirmando la ausencia y luego la presencia del archivo; el
  hallazgo de que `resource set expr=<nombre>.filePath` falla si el nombre del recurso lleva un
  punto, resuelto indexando `project.IncludedFiles[N]`; y, por separado, la reproducción de que
  un `sprite` creado por `resourcetool` sin frames hace que el `AssetCompiler` lance una
  `NullReferenceException` no capturada que `gm-cli compile --errors-only` esconde por completo
  (exit 0, cero líneas) y que impide escribir `game.zip` sin que ninguna salida lo señale.
- **Cuarta corrección del 8 de septiembre de 2026** (§0 Trampa 10, §9 quater): ejecución en vivo
  en un proyecto de prueba bajo `~` (`~/gm_audit_r7`, `gm-cli init -t "Blank Pixel Game"`, borrado
  al terminar), `gm-cli` 2.3.0 / `ResourceTool@2026.0.17`. Fuente directa de: `helptable` completo
  (30 comandos) recorrido buscando argumentos con lista cerrada; `resource create
  type=particlesystem` + `resource set expr=<sistema>.emitters[0].<campo> value=<valor>` sobre
  ~15 campos distintos, confirmados en el `.yy` final y con `gm-cli compile` limpio, y la prueba
  de que `emitters[1]` sí falla (`out of range (0..0)`) mientras `emitters[0]` sobre lista vacía
  no; la comparación con `project.LibraryEmitters[0]` y con `eventList[0]` de un objeto sin
  eventos (ambos fallan igual, `list is empty`) para descartar que fuera un comportamiento
  general; extracción con `unzip` del `.yymps` bundlado en
  `GameMaker.app/Contents/MacOS/arm64/packages/gm-ide-prefabs/gm-particle-presets/` y lectura de
  los 10 `.yy` de presets reales; `room layer create type=UI` rechazado, contrastado contra los
  18 miembros de `project` y contra un grep de `resourceType` de capa en todos los `.yy` de
  `11 - Código descargado/`; una tira de prueba de 3×16×16 generada con `ImageMagick`, probada sin
  y con el sufijo `_stripN`, y trocéada y reensamblada fotograma a fotograma con
  `SPRITE ADDFRAME` verificando `width`/`height`/`frames` antes y después; `gm-cli compile
  --toolchain GMRT@0.21.0` fallando por falta de **.NET 8** (`which dotnet` sin resultado) tras
  confirmar en el propio `--help` de `compile`/`run` que `GMRT@<versión>` es un valor documentado
  de `--toolchain`; `object event findorcreate type=async` reproducido como excepción interna sin
  capturar (`KeyNotFoundException`, `exit 2`); y el barrido completo de `OPTIONS GET/INFO/SET
  PLATFORM=windows` que destapó que `HELP OPTIONS SET` da nombres de propiedad equivocados
  (`interpolation`/`fullscreen` en vez de `interpolate_pixels`/`start_fullscreen`) y que, de 30
  propiedades reales, solo 5 son escribibles por CLI — las 25 restantes fallan con «is read-only»
  incluso con el nombre correcto y sin que ninguna raíz de expresión (`resource info
  expr=Windows`, los 17 tipos de `resource types`, los 18 miembros de `project`) las alcance por
  la vía genérica.
