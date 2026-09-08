# Auditoría r5 · Prueba end-to-end: construir un juego completo desde cero

> Fecha: 08-09-2026 · Metodología: soy un agente de IA al que se le pidió «hazme un juego con
> GameMaker», con la skill `gamemaker-biblioteca` como única fuente. Construí de verdad, en
> `~/gm_prueba_e2e/salto_nova` (nunca dentro de esta biblioteca), sobre GameMaker LTS 2026.0
> (IDE `2026.0.0.16` · runtime `2026.0.0.23`) y `gm-cli` **2.3.0**. Este documento es el
> entregable real: dónde se atasca un agente, no una demo de que «todo funciona».

## Resumen ejecutivo

**Sí, se puede llegar a un juego completo, jugable, con menús, opciones reales, pausa,
guardado, sonido y persistencia — siguiendo la skill casi al pie de la letra. El código GML
compiló limpio (`exit 0`) a la primera, en las 3.700 líneas repartidas en 17 objetos y 17
scripts.** Ese es el éxito real de la biblioteca: `buscar.py` antes de cada símbolo y el catálogo
reutilizable de `06 - Assets y Scripts` funcionan exactamente como prometen, y las cuatro trampas
de `12/09` (plantillas rotas, sandbox de red, numeración de eventos, compilador ciego) las evité
todas porque estaban documentadas y las leí antes de escribir el primer comando.

**Pero «compila limpio» no fue ni de lejos «funciona», y las dos veces que no funcionó fueron
exactamente del tipo que la propia biblioteca advierte que existe — solo que para un subsistema
que no cubre.** Encontré dos fallos silenciosos, no documentados en ningún sitio, que un agente
sin la costumbre de desconfiar del "exit 0" habría entregado como terminados:

1. **Los recursos de fuente (`font`) creados por `resourcetool` compilan limpio y **no
   muestran ni una sola letra en pantalla**.** `resourcetool`/`gml compile` nunca rasterizan los
   glifos (ese paso vive solo en la IDE); el `.yy` se queda con `"glyphs":{}` y el compilador
   empaqueta eso tal cual — un *chunk* `FONT` de 200 bytes en vez de los ~15 KB que hacen falta
   para un texto legible. Ningún documento de la biblioteca lo menciona. Tuve que
   reconstruir el formato a mano a partir de un `.yy` de un proyecto descargado, hornear los
   glifos yo mismo con PIL, y en el intento sobrevivió un hallazgo aún peor: un `.yy` mal
   formado (una coma que faltaba, error mío) **tumbó todo el toolchain** (`resourcetool` y
   `compile` por igual) con un `System.AccessViolationException` nativo — no un error de JSON
   limpio, un *crash* que bloqueó el proyecto entero hasta que reparé el archivo a mano.
2. **`directory_exists()` y `directory_create()` devuelven `false` siempre**, bajo
   `gm-cli run --target mac`, incluso sobre la propia carpeta de guardado (`game_save_id`) que
   ya existe y tiene archivos dentro — mientras que escribir un archivo ahí con
   `file_text_open_write()` funciona perfectamente. Esto rompe en silencio el *gate*
   `save_ensure_dir()` de `scr_save_load.gml`, el script marcado **⭐ Esencial** y
   «✅ Compilación verificada» en el propio catálogo de la biblioteca: cada partida que
   `save_game()` intentaba guardar fallaba con «no se pudo crear la carpeta de guardado», y la
   única pista era una línea de log que hay que estar mirando activamente para notar.

Los dos hallazgos comparten la misma forma: **código que compila limpio, que la biblioteca
recomienda o incluso da por verificado, y que en tiempo de ejecución hace exactamente lo
contrario de lo que promete, sin ningún error visible salvo que se mire el log con lupa o se
capture la pantalla.** Es la Trampa 4 (`12/09 §7.5`) — pero para dos subsistemas que ese
documento no cubre.

---

## Qué construí

**Salto Nova** — arcade de un botón (`04/11`), variante horizontal: nave de doble salto,
obstáculos y estrellas recogibles entrando por la derecha, puntuación con combo y multiplicador
decayendo por tiempo, dificultad creciente en raíz cuadrada. Cumple los ocho requisitos mínimos
del encargo:

| Requisito | Cómo |
|---|---|
| Menú principal (jugar/opciones/salir) + pausa | `obj_menu` (Jugar/Opciones/Créditos/Salir) + `obj_pausa` (Reanudar/Opciones/Salir, con confirmación «No» por defecto) |
| Opciones reales | Volumen de música y efectos (`scr_audio.gml`, buses reales) + pantalla completa (`window_set_fullscreen`), aplicados EN VIVO y persistidos en `ajustes.ini` |
| Bucle jugable con victoria y derrota | Ganas al llegar a 400 puntos (`rm_victoria`); pierdes al primer choque (`rm_derrota`), arcade clásico |
| Guardado y carga | Mejor puntuación y nº de partidas, vía `scr_save_load.gml` (JSON con checksum, escritura seguro por temporal) — **verificado round-trip real: cerrar el proceso y volver a abrirlo carga el récord guardado** |
| Transiciones + créditos | Fundido a negro entre salas (`obj_fundido`, patrón de `04/00 §2`) + créditos con scroll saltable |
| Sonido | 100% sintetizado en tiempo real con `audio_create_buffer_sound()` (`08/24 §3`): salto, doble salto, impacto, dos tonos de recogida, confirmaciones de UI — cero archivos de audio |
| Efecto visual | Screen shake (`scr_camera.gml`), squash & stretch con tweens (`scr_tween.gml`), texto flotante de puntos, flash de pantalla al morir, campo de estrellas parpadeante dibujado por código |

**Reutilizado tal cual del catálogo `06 - Assets y Scripts`** (no reescrito): `scr_math_util`,
`scr_camera`, `scr_tween`, `scr_save_load`, `scr_audio`, `scr_tiempo` — los seis compilaron
juntos sin tocar una línea salvo el parche de `save_ensure_dir()` descrito abajo. Esto es
exactamente el flujo que `06/README.md` promete y funcionó.

### La compilación — salida real

```
$ gm-cli compile --toolchain GMS2@2026.0.0.23
...
│  Stats : GMA : Elapsed=218.395
│  Stats : GMA : sp=3,au=0,bk=0,pt=0,sc=193,sh=0,fo=3,tl=0,ob=17,ro=7,da=0,ex=0,ma=6,fm=0x1000929C6DE62C30
◆  Compilation finished
$ echo $?
0
```

`sp=3` sprites, `fo=3` fuentes, `ob=17` objetos, `ro=7` salas, `sc=193` (bloques de script
compilados) — sobre 17 objetos y 17 scripts de proyecto, 3.725 líneas de `.gml`. Limpio a la
**primera** compilación tras terminar de escribir todo el GML (una sola ronda de correcciones
fue necesaria después, no por errores de sintaxis sino por los dos bugs de runtime de más
abajo).

`validar-proyecto.py --todo`, sobre el proyecto ya limpio de archivos sueltos:

```
63 archivos .gml · 1181 llamadas analizadas · runtime del índice 2026.0.0.23
✓ Ninguna llamada a una función del runtime que no exista.
· 1 nombres que el proyecto no define ni el runtime declara (...):
  callback()  en scripts/scr_tiempo/scr_tiempo.gml
```

Ese único aviso es un falso positivo esperado: `callback` es una variable local que guarda una
`method`, no una llamada a una función global — el propio patrón de `Temporizador` de
`scr_tiempo.gml`, código verbatim de la biblioteca.

**Verificación en vivo, no solo estática**: ejecuté el juego de verdad con `gm-cli run` en
once ocasiones distintas a lo largo de la sesión (depurando los dos bugs de abajo), y en la
versión final confirmé por captura de pantalla real (`screen_save()`, ver hallazgo #6) que el
menú principal, el bucle de juego, y la pantalla de derrota con «¡NUEVO RÉCORD!» se ven y dicen
lo que el código dice que deberían decir — incluyendo un ciclo completo de **cerrar el proceso,
volver a abrirlo, y ver el récord guardado en la sesión anterior ya cargado en el menú.**

---

## Los tropiezos, de más a menos grave

### 1 · Los recursos `font` creados por `resourcetool` compilan limpio y no muestran texto — nunca documentado

**Qué necesitaba**: tres fuentes (título, texto normal, texto pequeño) para un juego que es,
literalmente, casi todo texto (menús, HUD, resultados).

**Qué hice, siguiendo la skill al pie de la letra**: `resource create type=font`, `font addrange
name=X lower=32 upper=255` (para cubrir tildes, eñes, ¿¡), `resource set expr=X.size value=N`.
Todo respondió "Success". Compilé limpio. Ejecuté el juego, capturé el menú con
`screen_save()` (ver hallazgo #6) — **la pantalla se veía perfecta salvo por un detalle: no
había ni una sola letra.** Solo el campo de estrellas de fondo, dibujado con `draw_circle` (eso
sí funcionaba, porque no depende de ninguna fuente).

**Lo que encontré al investigar** (nada de esto está en `12/09`, que documenta 80 herramientas
de `resourcetool` con gran detalle pero no menciona esto):

- El `.yy` de una fuente creada por `resourcetool` se queda con `"glyphs":{}` — un diccionario
  vacío — pase lo que pase con `ranges`, `size`, o incluso apuntar `font setfile` a un `.ttf`
  real del sistema (`/System/Library/Fonts/Supplemental/Arial.ttf`): el comando responde
  «marked for re-generation», pero ni `gm-cli compile` ni ningún otro comando de `resourcetool`
  o de `ProjectTool` (comprobé su `--help` completo: `PROJECT`, `IMPORT YY`, `EXPORT`,
  `SIGNING`... nada de rasterizado) ejecutan esa regeneración.
- Un proyecto real (`11 - Código descargado/.../fonts/fnt_game/fnt_game.yy`) confirma el
  formato que hace falta: cada fuente lleva **su propio PNG** con los glifos ya rasterizados
  junto al `.yy`, y `"glyphs"` tiene una entrada por carácter con `{character, h, offset,
  shift, w, x, y}` apuntando a ese PNG. Ese PNG y esas coordenadas los genera la IDE al crear o
  editar la fuente — es trabajo de editor, no de compilador ni de `resourcetool`.
- El *chunk* `FONT` del juego compilado lo confirma sin ambigüedad: **200 bytes** con mis
  fuentes vacías, **15.064 bytes** después de hornearlas — un salto de 75×.

**Cómo lo resolví** (fuera de lo que la biblioteca ofrece): un script Python con Pillow que
rasteriza Arial/Arial Bold del sistema, empaqueta los glifos en un atlas, y **reescribe el
`.yy` con el bloque `"glyphs"` correcto** — la única vía que encontré, porque ningún comando de
CLI lo hace. A la primera versión del script le faltaba una coma entre entradas del
diccionario; el `.yy` resultante, mal formado, **no dio un error de parseo limpio: tumbó
`ResourceTool` y `gm-cli compile` con un `System.AccessViolationException` nativo** (memoria
protegida corrupta), y ambas herramientas quedaron inutilizables sobre el proyecto hasta que
reparé el JSON a mano insertando las comas que faltaban. Esto es la prueba en vivo, más
dramática de lo que esperaba, de por qué la regla «nunca edites `.yy` a mano» existe: no falla
limpio, falla catastróficamente.

**Severidad**: la más alta de la sesión. Un agente que no dude de un `exit 0` (Trampa 4 avisa
de esto para *funciones inventadas*, no para *fuentes vacías*) entregaría un juego enteramente
mudo visualmente — cada menú, cada botón, cada puntuación — sin ningún mensaje de error que lo
delate, ni en el compilador ni en el log de ejecución.

**Qué le falta a la skill**: o (a) documentar clarísimamente que las fuentes creadas por
`resourcetool` necesitan abrirse una vez en la IDE real antes de servir para nada, o (b) mejor
aún, **enviar 2-3 fuentes ya horneadas y listas para copiar** dentro de la propia biblioteca —
el mismo patrón que ya funciona de maravilla con `06 - Assets y Scripts` para código GML, pero
para este recurso concreto que ningún comando de CLI puede generar.

### 2 · `directory_exists()`/`directory_create()` devuelven `false` siempre bajo `gm-cli run --target mac` — rompe en silencio el script de guardado ⭐ Esencial de la propia biblioteca

**Qué pasó**: la primera vez que un jugador perdía, el HUD de resultados decía «¡NUEVO
RÉCORD!» (correcto, en memoria) pero el log mostraba `save_game: no se pudo crear la carpeta de
guardado.` — el guardado a disco fallaba siempre.

**Diagnóstico en vivo** (añadí una tecla de depuración temporal, F8, con el patrón de
`13/10 §7.4`):

```
QA-F8: game_save_id = [/Users/.../Library/Application Support/com.yoyogames.macyoyorunner/]
QA-F8: directory_exists(game_save_id) = 0     ← la carpeta EXISTE y tiene archivos dentro
QA-F8: directory_create(game_save_id) = 0     ← falla al "crear" lo que ya existe
QA-F8: directory_exists('.') = 0
QA-F8: directory_exists('') = 0               ← ninguna llamada a directory_exists() devuelve true
QA-F8: file_text_open_write directo = 1       ← pero ESCRIBIR un archivo ahí funciona perfecto
QA-F8: file_exists tras escribir = 1
```

`directory_exists()` devuelve `false` para **cualquier** argumento probado, incluida la propia
carpeta de guardado con archivos dentro, mientras que la escritura directa de archivos
(`file_text_open_write`) en esa misma carpeta funciona sin ningún problema. Esto rompe
exactamente el *gate* de `save_ensure_dir()` en `06 - Assets y Scripts/scr_save_load.gml`:

```gml
function save_ensure_dir() {
    if (directory_exists(game_save_id)) { return true; }
    return directory_create(game_save_id);   // ambas ramas fallan → save_game() nunca escribe
}
```

Ese script está marcado **⭐ Esencial** y **«✅ Compilación verificada (2026-09-06)»** en el
`README.md` del catálogo — la verificación fue de compilación, no de ejecución, y aquí es
exactamente donde se nota la diferencia.

**Lo apliqué**: parcheé `save_ensure_dir()` para no confiar en el resultado de
`directory_exists`/`directory_create` (documentado en el propio archivo, con el porqué) y
dejar que el intento real de escritura decida. Verificado con el mismo F8: `save_ensure_dir() =
1`, `save_game(qa_test) = 1`, archivo real en disco con el checksum correcto. Después,
verificación de extremo a extremo real: partida → derrota → puntuación 18 guardada → **cerrar
el proceso del juego por completo → volver a lanzarlo → el menú principal muestra «RÉCORD:
18.78»**, cargado de la sesión anterior.

**Severidad**: alta, y silenciosa de la misma manera que el hallazgo #1 — sin capturar el log o
instrumentar una comprobación deliberada, «probé a guardar y no salió ningún error visible en
pantalla» habría sido la conclusión de un agente que no mira la consola de depuración a
propósito.

**Nota de alcance honesta**: no pude aislar si esto es un bug del *runtime* 2026.0.0.23 en
macOS en general, o específico del **runner de pruebas sin firma** que `gm-cli run` lanza
(`YoYo Runner.app` genérico, no un `.app` firmado/exportado de verdad) — el propio `12/09 §4`
ya avisa de que el *runner* de escritorio "no reproduce" ciertas condiciones del hardware/target
real. No tuve forma de probar un build exportado y firmado de verdad en esta sesión. Aun así,
dado que **es exactamente el flujo que la biblioteca recomienda para que un agente pruebe su
propio juego** (`gm-cli run`, `12/09 §1` paso 8), el hallazgo se sostiene tal cual para ese
flujo.

**Qué le falta a la skill**: una nota en `01/14` (Persistencia) o en `12/09` avisando de que
`directory_exists`/`directory_create` pueden no ser fiables bajo `gm-cli run`, y que
`scr_save_load.gml` debería (como ya lo dejé) no bloquear el guardado en ese *gate* sino
intentar la escritura igualmente.

### 3 · El MCP `gamemaker-resource-tool` nunca estuvo disponible en esta sesión

Exactamente como predice `12/09 §3.3`: el MCP es por proyecto y esta sesión no arrancó dentro
de la carpeta del proyecto (no existía todavía cuando la sesión empezó). Usé
`gm-cli resourcetool eval` para **absolutamente todo** — más de 90 llamadas a lo largo de la
sesión. Funcionó, tal y como la biblioteca dice que funcionaría como alternativa equivalente,
pero confirma en la práctica que la vía "rápida" (MCP tipado) es la excepción, no la norma, para
un agente que arranca sin un proyecto ya creado.

### 4 · `gm-cli init` con el sandbox por defecto no cuelga: falla directamente

La Trampa 2 de `12/09` describe el síntoma como "se queda colgado" bajo el sandbox del Bash
tool. En esta sesión, la primera llamada a `gm-cli init` bajo sandbox no colgó: **falló con
`Failed to fetch templates:`** (mensaje vacío) en unos 2 segundos. Incidental respecto al
diagnóstico ya documentado (misma causa raíz, la verificación de red de `npx` contra el
registro de GameMaker), pero el síntoma exacto puede ser un fallo limpio y rápido en vez de un
cuelgue indefinido — vale la pena que el documento lo mencione como las dos formas posibles,
para que un agente no descarte la Trampa 2 solo porque no "se quedó colgado" literalmente.
`dangerouslyDisableSandbox: true` lo resolvió al instante, como promete la biblioteca.

### 5 · `FOLDER CREATE` usa un argumento distinto al patrón de `RESOURCE CREATE` — sin aviso

Adiviné, por analogía con `resource create type=X name=Y folder=Z`, que `folder create
name=Objetos type=object` crearía una carpeta del Asset Browser. Respuesta: `Ignoring
Argument: NAME` / `Ignoring Argument: TYPE`, y creó una carpeta en la **ruta vacía** (`''`). El
comando correcto, que solo descubrí con `resourcetool eval "help folder"`, es `folder create
folder=<ruta>` — un único argumento con el mismo nombre (`folder=`) que el campo de
*colocación* de `resource create`, pero con un significado distinto (aquí es la ruta a crear,
no el destino de otra cosa). Sin consecuencias graves (las carpetas vacías no rompieron nada,
las descarté sin más), pero es exactamente el tipo de "adivina y adivina mal" que `12/09` ya
identifica como el problema central de un agente sin esta tabla. `07/13` debería incluir esta
firma en su inventario de comandos.

### 6 · Verificación visual: nada de la biblioteca la cubre, pero se puede improvisar (con matices)

`12/09 §4.2` es honesto: "que el juego se vea como se pretende" está fuera del alcance de un
agente porque no hay salida visual que pueda inspeccionar sin capturas manuales — y solo cita
`screen_save()` disparado por el propio GML como vía (`§4.1`), sin decir *cuándo* dispararlo si
el jugador (que soy yo, sin manos) nunca llega a esa pantalla.

Lo que hice, no documentado en ningún sitio de la biblioteca: monté un modo QA con teclas
ocultas (patrón exacto de `13/10 §7.4`, `F2` captura / `F3` salta a la partida / `F6` fuerza
victoria / `F7` fuerza derrota), lancé el juego con `gm-cli run`, y **envié las pulsaciones de
teclado de verdad a la ventana del runner con `osascript`/System Events** (`key code 120` = F2,
etc., tras poner el proceso en primer plano por su PID). Funcionó: conseguí capturas reales del
menú principal y de la pantalla de derrota, y confirmé visualmente que el texto se veía
correctamente alineado (tras el hallazgo #1) y que la lógica de "nuevo récord" se refleja bien
en pantalla.

**Con matices importantes que vale la pena documentar**:
- Las pulsaciones sintéticas de `System Events` no siempre llegan una sola vez: en más de una
  ocasión, una sola pulsación de tecla se tradujo en varias transiciones de pantalla
  encadenadas (menú → partida → derrota) o en una salida completa del juego
  (`obj_menu` → "SALIR" → `game_end()`) sin que yo hubiera pedido esa secuencia — sugiere que
  el *runner* de pruebas o el propio System Events puede encolar/repetir eventos de teclado de
  forma no determinista.
- **Un proceso de GameMaker completamente ajeno, ejecutándose en la misma máquina en paralelo**
  (la suite de pruebas automatizada de otro proyecto del usuario, "Lumbre"), robó el foco de
  ventana de forma agresiva y bloqueó esta técnica durante varios minutos — nada que ver con la
  biblioteca, pero un recordatorio de que esta vía es fràgil en una máquina compartida.

Ninguna de las dos cosas es un fallo de la biblioteca (la técnica entera es una improvisación
mía, fuera de lo documentado), pero si `12/09` fuera a ampliar su §4 con esta vía como opción
para un agente con acceso a `osascript`/automatización de UI, debería avisar de ambos matices.

### 7 · Mi propio error de proceso reveló un punto ciego de `validar-proyecto.py`

Guardé mis copias de trabajo de los `.gml` (antes de importarlos con `resourcetool`) dentro de
una carpeta `_assets_gen/` **dentro del propio directorio del proyecto**, por comodidad. En un
momento edité `scr_sonidos.gml` para añadir dos funciones nuevas (`sonar_evento`, `sonar_ui`)
**después** de haberlo importado ya al proyecto, y me olvidé de re-sincronizarlo con
`gml setgmlfile`. El proyecto real se quedó sin esas dos funciones — y sin embargo,
`python3 validar-proyecto.py --todo` **no las marcó como `desconocida`**, porque escaneaba
también mi carpeta de trabajo (que sí las tenía) y las contó como "definidas en el proyecto"
aunque no estuvieran conectadas a ningún recurso real. El bug solo salió a la luz al ejecutar
el juego de verdad (`Variable obj_menu.sonar_ui(...) not set before reading it`). Moví toda mi
carpeta de trabajo fuera del proyecto (al scratchpad de la sesión) y, con el proyecto limpio de
archivos sueltos, `validar-proyecto.py` pasó de analizar 78 a 63 archivos — confirmando que sí
estaba escaneando lo que no debía. Esto es en gran parte un error mío (debí usar el scratchpad
desde el principio, como manda la propia guía general de esta sesión), pero **revela un punto
ciego real**: el validador no cruza contra el `.yyp` para saber qué `.gml` está de verdad
conectado a un recurso compilable — cualquier archivo suelto en la carpeta del proyecto cuenta
como una "fuente de definición" válida, aunque el compilador nunca lo vea.

### 8 · Piezas conscientemente recortadas de scope (no fallos de la biblioteca)

- **`04/41` (transiciones/pausa completas)** documenta un motor con wipe/iris/disolución por
  shader y congelado de física/partículas/Sequences. Implementé solo el fundido a negro y un
  congelado reducido a lo que el proyecto usa de verdad (instancias + audio) — la receta
  completa existe y es excelente, pero exige criterio editorial para recortarla a lo que un
  proyecto pequeño necesita; la biblioteca no ofrece una versión "mínima viable" junto a la
  completa.
- **Música**: cero, a propósito. `13/09 §8bis` es honesto sobre esto — "instrumentación con
  melodía o música completa" está en su propia tabla de "no razonable por síntesis". No añadí
  música porque la biblioteca correctamente me dice que no debo fingir que la síntesis en
  tiempo de ejecución la resuelve. Esto **no** es un hallazgo negativo: es la biblioteca
  fijando expectativas con precisión.
- **Sprites**: nave (triángulo con cabina y llama), asteroide (polígono irregular con
  cráteres), estrella recogible — generados con Python/Pillow siguiendo `12/09 §5.2` punto 2
  ("genera un PNG por código e impórtalo"), pero **el propio ejemplo que da ese punto es un
  cuadrado de color liso**. Tuve que decidir yo mismo ir un poco más allá con primitivas de
  dibujo (polígonos, elipses) para que no fueran, literalmente, "un rectángulo de color" — que
  es justo lo que el encargo pedía anotar como fallo si pasaba. No pasó, pero fue **por
  iniciativa propia, no porque la biblioteca ofreciera nada entre "rectángulo plano" y "arte
  de verdad"**. Sí cuenta como hueco: dos o tres ejemplos más elaborados (una nave, un
  personaje redondo, una moneda) en el propio `12/09 §5.2` bajarían mucho el listón de lo que
  un agente sin more criterio entrega por defecto.

---

## Lo que NO pude verificar (honestidad de cobertura, `12/09 §4.2`)

- **Sonido de verdad** (mezcla, si algo satura, si el volumen se nota bien): no hay forma de
  "escuchar" desde este entorno. Generé los tonos siguiendo las fórmulas verificadas de
  `08/24 §3` y confié en que compilaran y jugaran sin abortar, pero ni una sola vez comprobé
  que sonaran bien.
- **Sensación de juego** (si el salto se siente "justo", si la dificultad escala bien): es una
  valoración humana. Jugué exactamente cero veces con mis propias manos — todo lo que se ve en
  las capturas es la IA jugando sola (sin saltar nunca) o disparando los atajos de F3/F6/F7.
- **Pantalla de Opciones, pausa superpuesta y créditos**: escritas y compiladas, pero no las
  vi renderizadas en pantalla — la técnica de inyección de teclas del hallazgo #6 no llegó a
  esos flujos concretos (requieren varias pulsaciones encadenadas de forma fiable, y la
  inestabilidad ya descrita hizo que me diera por satisfecho con la cobertura ya conseguida en
  vez de perseguir cada pantalla).
- **Pantalla completa de verdad, mando/gamepad**: código escrito (`window_set_fullscreen`, sin
  gamepad en absoluto — decisión de alcance, no probada por no tener mando conectado a esta
  máquina).

---

## El veredicto honesto

**¿Podría un agente sin mi criterio haber llegado hasta aquí solo con la biblioteca?** Hasta
"compila limpio, exit 0" — sí, con bastante confianza. La lista de trampas de `12/09`, el
catálogo de `06`, y las recetas de `04` son, de verdad, suficientes para que un agente
disciplinado (que verifique cada símbolo con `buscar.py`, que lea el manual del agente antes de
tocar `resourcetool`) escriba miles de líneas de GML correctas a la primera. Eso no es poco.

**¿Dónde se habría rendido, o habría entregado basura sin saberlo?** En los dos hallazgos
principales — y ahí es donde un agente "normal" se separa de esta sesión: **ninguno de los dos
falla en el compilador, ninguno de los dos aparece en `validar-proyecto.py`, y ninguno de los
dos se nota si no se mira específicamente**. Un agente que siguiera el checklist de `12/09 §8`
tal cual está escrito hoy marcaría las siete casillas, incluida "ejecutaste el juego al menos
hasta el punto que pruebas" — y aun así entregaría un juego mudo (sin texto) que además no
guarda nunca la partida, con el checklist en verde. La checklist actual no tiene ninguna
casilla que diga "capturaste una pantalla y la miraste" ni "confirmaste que el guardado
persiste tras cerrar el proceso" — las dos comprobaciones que, en esta sesión, fueron las que
realmente delataron los dos bugs graves.

**Lo que hizo la diferencia no fue conocimiento de GameMaker que la biblioteca no diera: fue no
confiar en el silencio.** Cada vez que algo "no dio ningún error", lo traté como sospechoso en
vez de como aprobado — exactamente la lección que `12/09` ya enseña para las funciones
inventadas, pero que un agente tiene que generalizar por su cuenta a fuentes vacías y a
guardados que fallan callados, porque el documento no lo dice para esos dos casos todavía.

## Qué le falta a la skill, en una lista

1. **Fuentes horneadas ya listas para copiar** (2-3, como los scripts de `06`), o al menos un
   aviso imposible de no ver de que `resourcetool`/`gm-cli compile` no rasterizan glifos.
2. **Una nota sobre `directory_exists`/`directory_create` bajo `gm-cli run`**, y que
   `scr_save_load.gml` no debería bloquear el guardado en ese *gate* — patch ya escrito y
   verificado en esta sesión, trasladable tal cual.
3. **Dos casillas nuevas en el checklist de `12/09 §8`**: "capturaste al menos una pantalla con
   `screen_save()` y la miraste" y "el guardado sobrevive a cerrar y reabrir el proceso, no
   solo a `save_game() == true` en el mismo run".
4. **La firma exacta de `FOLDER CREATE`** (`folder=<ruta>`, no `name=`/`type=`) en el
   inventario de comandos de `07/13`.
5. **Un aviso de no dejar archivos `.gml` sueltos dentro de la carpeta del proyecto** antes de
   correr `validar-proyecto.py`, porque el validador no distingue "conectado a un recurso" de
   "está en la carpeta".
6. **Dos o tres ejemplos de sprite procedural más elaborados que un cuadrado plano** en
   `12/09 §5.2`, para que "genera un PNG por código" no colapse por defecto en exactamente el
   resultado que el encargo de esta prueba pedía vigilar.

---

## El proyecto

`~/gm_prueba_e2e/salto_nova` — **lo conservo como ejemplo**, fuera de esta biblioteca. Compila
limpio, corre, guarda partida de verdad, y las fuentes horneadas a mano (`fonts/*/*.png` +
`.yy` con `glyphs` poblado) son en sí mismas un ejemplo reproducible de la solución al hallazgo
#1 — útil como referencia si esta auditoría motiva a arreglarlo en la biblioteca. El script de
horneado (`generar_fuente.py`) y el resto de material de trabajo quedaron en el scratchpad de
la sesión, no en el proyecto ni en la biblioteca.
