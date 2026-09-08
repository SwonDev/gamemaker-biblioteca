# 09 · Manual del agente de IA — operar GameMaker con `gm-cli`

> Este es el documento que usa un agente de IA cada vez que toca GameMaker de punta a punta:
> crear el proyecto, crear recursos, escribir GML, compilar, depurar y publicar sin abrir el
> IDE. No repite lo que ya explican [`07 · 13`](../07%20-%20Ecosistema/13%20-%20GM%20CLI%20-%20la%20l%C3%ADnea%20de%20comandos.md)
> (referencia completa del CLI) y [`07 · 14`](../07%20-%20Ecosistema/14%20-%20IA%20y%20GameMaker.md)
> (qué es el andamiaje `--ai` y cómo se prepara un proyecto para un agente): este documento
> añade **lo que ninguno de los dos cubre** — los seis sitios donde un agente se atasca hoy,
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

## 0 · Las seis trampas que hacen fracasar a un agente hoy

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

**Cómo se detecta**: no por el compilador ni por `validar-proyecto.py` — ninguno de los dos mira
dentro de un recurso de fuente. Solo capturando la pantalla de verdad y mirándola
([§4.1](#41-lo-que-un-agente-sí-puede-observar-por-sí-solo), `screen_save()`), o inspeccionando
el propio `.yy`:

```bash
gm-cli resourcetool eval "font glyphlist name=fnt_titulo"
# {} vacío -> la fuente no tiene ni un solo glifo rasterizado, por más ranges/size que tenga
```

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
- [`_indice/auditorias/r5-prueba-e2e.md`](../_indice/auditorias/r5-prueba-e2e.md) — la prueba end-to-end (juego completo desde cero) que descubrió las Trampas 5 y 6 de este documento.
- [`06 - Assets y Scripts/scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml) — `save_ensure_dir()` trae ya el parche de la Trampa 6, con el porqué documentado en el propio script.

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
