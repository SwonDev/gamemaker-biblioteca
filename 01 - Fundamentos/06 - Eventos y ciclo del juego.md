# 06 · Eventos y ciclo del juego

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Event_Order.htm>
> - <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Object_Events.htm>
> - <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Draw_Events.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Time_Sources/Time_Sources.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Cameras_And_Display/display_set_timing_method.htm> (§7 bis)
> - `gm-cli manual read "delta_time"` y `gm-cli manual read "room_speed"`

---

## 1. Qué es un evento (y qué es un step)

GameMaker divide el tiempo en **steps** (también llamados **frames**). La velocidad de juego define cuántos steps debería haber por segundo.

Un **step** es básicamente **el bucle que se ejecuta constantemente**: en cada paso se comprueban y disparan todos los eventos que corresponda.

Un **evento** es un momento discreto de ese bucle donde ocurren las cosas que has programado.

```
┌────────────────────────────────────────────────┐
│  STEP 1                                        │
│   Begin Step → Timelines → Time Sources →      │
│   Alarms → Step → Movimiento → Colisiones →    │
│   End Step → Draw...                           │
└────────────────────────────────────────────────┘
┌────────────────────────────────────────────────┐
│  STEP 2  (ídem)                                │
└────────────────────────────────────────────────┘
```

---

## 2. ⚠️ La advertencia importante sobre el orden

El manual lo dice claramente:

> **«the exact order that ALL the events are going to occur in each step cannot be clearly stated»,** porque depende del funcionamiento interno de GameMaker y puede cambiar según la plataforma.

**Pero hay eventos que SIEMPRE ocurren en el mismo orden.** Esos son los que debes usar.

> ⚠️ **Y hay otra regla crítica:** puedes confiar en el orden de los **eventos**, pero **NO en el orden de las instancias dentro de un evento**.
>
> Puedes confiar en que *Begin Step* ocurre antes que *Step*. **No** puedes confiar en que `obj_enemigo` ejecute su Step antes que `obj_jugador`.
>
> Si necesitas ese orden, usa eventos distintos (por ejemplo, pon el código del segundo objeto en *End Step*).

---

## 3. Al entrar en una room

Este es el orden **garantizado** al entrar en una room:

```
1. Se crean TODAS las instancias, una tras otra,
   según el Instance Creation Order de la room.
   Por cada instancia:
      a) Se inicializan sus OBJECT VARIABLES (Pre-creation Code)
      b) Se ejecuta su CREATE EVENT
      c) Se ejecuta su INSTANCE CREATION CODE (si tiene)

2. GAME START event
   → Solo en la PRIMERA room del juego, para todas las instancias
     colocadas desde el Room Editor
   → ⚠️ game_restart() lo vuelve a disparar

3. ROOM CREATION CODE
   → El código único escrito en el Room Editor

4. ROOM START event de TODAS las instancias
   → Incluye las persistentes
```

### ⚠️ La trampa del Create event

Las instancias se crean de una en una, y su Create se ejecuta **en el momento de crearse**. Por tanto:

```gml
// obj_A va ANTES que obj_B en el orden de creación

// Create de obj_A
miValor = obj_B.miValor;   // ❌ CRASH

// Create de obj_B
miValor = 10;
```

Error resultante:
```
Variable obj_B.miValor(100003, -2147483648) not set before reading it.
```

**obj_B todavía no existe**, así que su Create no ha corrido.

> ⚠️ **Esto incluye cualquier código dentro de bloques `with()` en el Create.** Ten cuidado al leer variables de otras instancias ahí.

**Soluciones:**
- Mueve la lectura al evento **Room Start** (todas las instancias ya existen).
- Usa un objeto controlador que se cree el primero y orqueste.
- Comprueba con `instance_exists()` / `variable_instance_exists()` antes de leer.

---

## 4. El orden EXACTO de cada step

Esta es la tabla que debes memorizar:

```
┌─ BEGIN STEP ────────────────────────────────────┐
│  Todos los Begin Step de todas las instancias   │
├─ TIMELINES ─────────────────────────────────────┤
├─ TIME SOURCES ──────────────────────────────────┤
│   · "Ticks" (actualizaciones)                   │
│   · Callbacks:                                  │
│       1. Hijos de time_source_global            │
│       2. Time sources de call_later()           │
│       3. Hijos de time_source_game              │
├─ ALARMS ────────────────────────────────────────┤
├─ STEP ──────────────────────────────────────────┤
│  Todos los Step de todas las instancias         │
├─ MOVIMIENTO ────────────────────────────────────┤
│  Todas las instancias se mueven a su nueva      │
│  posición (según hspeed/vspeed, o siguiendo     │
│  un path)                                       │
├─ COLISIONES ────────────────────────────────────┤
│  Se comprueban las colisiones                   │
│  Si hay colisión y una de las instancias es     │
│  SOLID: ambas vuelven a la posición del frame   │
│  anterior y se llaman sus collision events      │
│  (Si no son solid, se quedan en la nueva        │
│   posición)                                     │
├─ END STEP ──────────────────────────────────────┤
│  Todos los End Step de todas las instancias     │
└─────────────────────────────────────────────────┘
```

> ⚠️ **Nota sobre Collision Compatibility Mode:** en ese modo las instancias se devuelven a su posición anterior **antes y después** de los eventos de colisión, en vez de solo antes. Es un modo de compatibilidad para proyectos anteriores a 2022.1.

### ¿Para qué sirven Begin Step y End Step?

Los tres eventos de step se comprueban **todos los steps**, y su orden **nunca variará**, aunque futuras actualizaciones cambien otros eventos.

> Es **el único método fiable** de garantizar que algo ocurre antes que otra cosa.

**Uso típico:**
- **Begin Step:** leer input, calcular intenciones.
- **Step:** lógica principal.
- **End Step:** reaccionar al resultado (por ejemplo, la cámara sigue al jugador *después* de que el jugador se haya movido).

```gml
// Begin Step del jugador: capturamos la intención
var _izq = keyboard_check(ord("A"));
var _der = keyboard_check(ord("D"));
intencion_x = _der - _izq;

// Step: aplicamos movimiento
x += intencion_x * velocidad;

// End Step de la cámara: seguimos al jugador YA movido
x = obj_jugador.x;
y = obj_jugador.y;
```

---

## 5. El orden de los eventos de DIBUJADO

Después de todos los eventos de step, GameMaker ejecuta los **Draw events** en el mismo step.

```
┌─ PRE-DRAW ─────────────────────────────────────┐
│  Dibuja DIRECTAMENTE al display buffer         │
│  ⚠️ La application surface se crea aquí        │
│     (si no existía) y se fija como render      │
│     target                                     │
├─ DRAW BEGIN ───────────────────────────────────┤
├─ DRAW ─────────────────────────────────────────┤
├─ DRAW END ─────────────────────────────────────┤
│  ⚠️ El render target se resetea aquí           │
├─ POST-DRAW ────────────────────────────────────┤
│  ⚠️ La application surface se dibuja al display│
│     buffer aquí (por defecto)                  │
├─ DRAW GUI BEGIN ───────────────────────────────┤
├─ DRAW GUI ─────────────────────────────────────┤
├─ DRAW GUI END ─────────────────────────────────┤
└────────────────────────────────────────────────┘
```

> **Regla de oro:** **todo lo que dibujes en Draw GUI se dibuja ENCIMA de todo lo dibujado en los Draw normales, sin importar la capa.**
>
> Es decir: una instancia en la capa más baja con evento Draw GUI **tapará** a una instancia en la capa más alta con Draw normal. Si **ambas** tienen Draw GUI, entonces sí se respeta el orden de capas.

### Orden de instancias DENTRO de un evento de dibujado

A diferencia de los eventos de step, **aquí sí importa el orden**, y depende de **`depth`**:

- La capa con el **depth más ALTO** dibuja **primero** (queda debajo).
- La capa con el **depth más BAJO** dibuja al final (queda «más cerca» del espectador, encima).

> En el Room Editor: la capa con depth más alto aparece **abajo** de la lista; la de depth más bajo, **arriba**.

Cada evento de dibujado dibuja todas las instancias en ese orden y luego pasa al siguiente evento, repitiendo el mismo orden de instancias.

### Draw Begin / Draw / Draw End

- Los tres son eventos de dibujado «estándar».
- **Solo el evento Draw tiene «default draw»:** si no pones código ni acciones, GameMaker dibuja el sprite asignado automáticamente (o nada, si no hay sprite).
- **Draw Begin y Draw End no dibujan nada por defecto** si no los añades explícitamente.
- Si pones código en el Draw, **anulas por completo el dibujado por defecto**. Para dibujar el sprite además de tu código, llama a `draw_self()`.

```gml
// Draw event
draw_self();                                  // el sprite como siempre
draw_text(x, y - 40, $"Vida: {vida}");        // más texto encima
```

> ⚠️ **Si pones `visible = false`, TODOS los eventos de dibujado se saltan** (excepto el evento *Resize*). No pongas lógica esencial en eventos de dibujado de objetos invisibles.

> ⚠️ **El Draw event es intensivo.** No hagas cálculos pesados ahí: solo dibuja. Deja la lógica para Step, alarmas u otros eventos.

### Draw GUI

Diseñado para interfaces que **no** se ven afectadas por la escala ni la rotación de la cámara.

- Las coordenadas **no cambian** aunque haya vistas activas.
- `(0,0)` es siempre la esquina superior izquierda de la **application surface** (o del display).
- Por defecto el tamaño es 1:1 con la application surface.

```gml
// Draw GUI event del objeto HUD
draw_healthbar(16, 16, 216, 40, obj_jugador.vida / obj_jugador.vida_max,
               c_black, c_red, c_lime, 0, true, true);

draw_text(16, 56, $"Puntuación: {global.puntuacion}");
```

Funciones para controlarlo:
```gml
display_set_gui_size(ancho, alto);       // fija un tamaño lógico y lo escala solo
display_set_gui_maximise(true);          // que ocupe toda la pantalla (incluidas barras negras)
```

### Pre-Draw y Post-Draw

Ambos dibujan **directamente al display buffer** (el tamaño de la ventana o del espacio combinado de todos los viewports).

**Pre-Draw** ocurre antes que cualquier otro evento de dibujado:
- Puedes fijar valores y propiedades sin preocuparte por los viewports.
- ⚠️ Ocurre **antes** de que se limpie el display buffer: si no desactivas el *clearing* de la vista en el Room Editor, **nada de lo que dibujes se verá**.
- Si lo desactivas, verás artefactos/estelas del frame anterior. Límpialo tú con `draw_clear_alpha()`.

**Post-Draw** va después de los Draw normales pero **antes** de los Draw GUI:
- Ideal para **post-procesado a pantalla completa** sin afectar al HUD.

```gml
// Post-Draw: aplicar un shader de post-procesado a TODO lo dibujado
shader_set(sh_vinheta);
draw_surface(application_surface, 0, 0);
shader_reset();
```

### Window Resize (solo HTML5)

Se dispara cada vez que se redimensiona el canvas.

> ⚠️ **No puedes dibujar en este evento.** Solo sirve para reaccionar al cambio (reajustar la vista, reposicionar el HUD).

---

## 6. Catálogo de eventos

### Create
Lo primero que ocurre en una instancia al crearse. Ideal para inicializar variables, arrancar Timelines, fijar Paths…

> Las **Object Variables** y **Instance Variables** se inicializan **antes** del Create.
> El **Instance Creation Code** del Room Editor se ejecuta **justo después** del Create, y sirve para crear variables de instancia o sobrescribir valores.

### Destroy
Cuando la instancia se destruye. Útil para explosiones, partículas, respawns, sumar puntos.

### Clean Up
Se llama después de **cualquier** evento que elimine la instancia:
- la instancia se destruye
- la room termina
- el juego termina

Diseñado para limpiar **recursos dinámicos** (surfaces, estructuras de datos, buffers, time sources).

> ⚠️ **Dos trampas:**
> 1. Se llama **inmediatamente** después del evento que lo dispara, pero la instancia **no se elimina hasta el final del evento actual**. Si llamas a `instance_destroy()` en el Step, se ejecutan Destroy → Clean Up → **y luego el resto del Step**. Si has limpiado algo que el código posterior necesita, tendrás errores.
> 2. Los eventos que llames desde Clean Up (salvo el heredado) **solo se ejecutan si el disparador fue la destrucción de la instancia**, no si fue el fin de room o de juego.

```gml
// Clean Up event
if (surface_exists(surf))  { surface_free(surf);  surf = -1; }
if (mi_lista != -1)        { ds_list_destroy(mi_lista); mi_lista = -1; }
if (time_source_exists(ts)) { time_source_destroy(ts); ts = -1; }
delete mi_struct;
```

### Alarm
12 alarmas por instancia. No hacen nada hasta que las activas; entonces cuentan atrás hasta 0.

- Al llegar a 0 ejecuta el código y **sigue bajando a -1**, donde se queda.
- Puedes comprobar si está activa con `alarm[0] > -1`.
- ⚠️ **Poner un alarm a 0 NO ejecuta su código** (el evento se dispara, pero la alarma se pone a -1 inmediatamente y el código se salta). Si quieres que corra en el siguiente step, ponlo a **1**.
- ⚠️ **Un alarm sin código no cuenta atrás.** Con solo un comentario dentro, sí.

```gml
// Create
alarm[0] = game_get_speed(gamespeed_fps) * 3;   // 3 segundos

// Alarm 0
direction = irandom(360);
alarm[0] = game_get_speed(gamespeed_fps) * 3;   // se reprograma a sí mismo
```

También existen `alarm_get(ind)` y `alarm_set(ind, valor)`.

### Step
Begin Step / Step / End Step (visto en la sección 4).

### Collision
Se coloca en un objeto y se especifica contra qué otro objeto comprueba.

- Sin física: se calcula con la **máscara** de los sprites. ⚠️ Si alguna instancia no tiene máscara asignada, **no se detecta colisión**, aunque esté dibujando algo.
- Con física: se basa en las **fixtures**. ⚠️ El evento **necesita al menos un comentario** para que se detecten las colisiones.
- ⚠️ **Las colisiones se calculan una vez por step, antes de disparar el evento.** Si creas una instancia dentro del evento de colisión y compruebas colisión con ella, **no se detectará hasta el siguiente step**.
- ⚠️ Las comprobaciones están limitadas al **collision space** de la instancia: una instancia en una capa *Display UI* no puede colisionar con las de una capa de room ni de una capa *Viewport UI*.

### Keyboard / Keyboard Press / Keyboard Release
- **Keyboard:** se dispara continuamente mientras la tecla está pulsada.
- **Keyboard Press:** una sola vez al pulsar.
- **Keyboard Release:** una sola vez al soltar.

Se disparan en **todas** las instancias activas de la room; solo responden las que tienen ese evento definido.

> ⚠️ **GameMaker NO ejecuta eventos de teclado ni ratón cuando el Debug Overlay está abierto** y ha tomado el control del input. Tampoco al *simular pulsaciones*. Las funciones (`keyboard_check()`…) sí siguen funcionando.
> Puedes detectarlo con `is_keyboard_used_debug_overlay()` y `is_mouse_over_debug_overlay()`.

Sub-eventos especiales: **No Key** y **Any Key**.
> Las teclas del teclado numérico solo generan eventos si **Block Num** está activado.

### Mouse
Los eventos de botón (izquierdo, derecho, central) funcionan **contra la máscara de la instancia**: si el ratón está sobre su bounding box, se dispara. Necesitas sprite con máscara válida o un mask sprite asignado.

- **No Mouse Input:** ratón sobre la máscara pero sin pulsar botones.
- **Mouse Enter / Leave:** cuando el ratón entra o sale de la instancia. Ideales para botones con hover.
- **Mouse Wheel Up / Down:** no dependen de la máscara; se disparan siempre.
- **Global Mouse:** se disparan en todas las instancias, sin importar la posición del ratón.

> En móvil: el botón izquierdo equivale a un toque; el derecho a un doble toque.

### Gestures
Tap, drag, flick, pinch y rotate. Versiones normales (sobre la bounding box) y **globales** (en cualquier parte de la pantalla).

Todos incluyen un DS map llamado **`event_data`** con pares clave/valor sobre la posición y el movimiento.

### Other
Grupo de eventos especiales (Game Start, Game End, Room Start, Room End, Outside Room, Intersect Boundary, No More Lives, Animation End, Path Ended, User Events…).

### Draw
Visto en la sección 5.

### Asynchronous
Eventos **no disparados por defecto** por GameMaker, sino por la finalización de otra acción: carga de un archivo, respuesta de un servidor web, etc.

```gml
// Create: pedimos un archivo
buff = buffer_create(1, buffer_grow, 1);
load_id = buffer_load_async(buff, "datos.json", 0, -1);

// Async - Load/Save event
if (async_load[? "id"] == load_id)
{
    if (async_load[? "status"] == true)
    {
        var _json = buffer_read(buff, buffer_string);
        datos = json_parse(_json);
    }
    buffer_delete(buff);
    buff = -1;
}
```

### Cómo nombrar eventos

Pon esto en la **primera línea** del evento:

```gml
/// @description Aquí tu texto descriptivo
```

Así verás el texto junto al evento en la lista de eventos. En GML Visual hay que usar la acción *Execute Code* al principio.

---

## 7. Velocidad de juego, `delta_time` y game loop

### `room_speed` — ⚠️ DEPRECADO

> *«This variable is maintained for **Legacy Support only**, and should not be used as it no longer sets the speed for a single room, but for ALL rooms in the game.»*

```gml
alarm[0] = room_speed * 10;   // ❌ legacy
```

**Usa en su lugar:**

```gml
game_set_speed(60, gamespeed_fps);       // fijar
var _fps = game_get_speed(gamespeed_fps); // leer
```

| Constante | Unidad |
|---|---|
| `gamespeed_fps` | Frames por segundo |
| `gamespeed_microseconds` | Microsegundos por frame |

```gml
alarm[0] = game_get_speed(gamespeed_fps) * 10;   // ✅ 10 segundos
```

### `delta_time`

Devuelve el tiempo transcurrido entre el frame anterior y el actual, en **microsegundos** (1 µs = 1/1.000.000 s).

**¿Para qué sirve?** Para que el juego se mueva a la misma velocidad real aunque haya lag.

```gml
// Ejemplo 1: velocidad base en PÍXELES POR STEP
var _dt = delta_time / game_get_speed(gamespeed_microseconds);
speed = spd * _dt;

// Ejemplo 2: velocidad base en PÍXELES POR SEGUNDO
var _dt = delta_time / 1000000;
speed = spd * _dt;
```

> 💡 **Regla mental:** si tu `spd` está pensada para 60 FPS (píxeles por step), usa el ejemplo 1. Si la piensas en píxeles por segundo (más portable), usa el ejemplo 2.

### `fps` y `fps_real`

```gml
show_debug_message($"FPS lógico: {fps}");
show_debug_message($"FPS real:   {fps_real}");
```

`fps` es los frames de juego que GameMaker ha conseguido mantener; `fps_real` es el rendimiento real. Si `fps_real` baja de tu game speed, vas mal.

### 7 bis · Vsync y frame pacing

`fps_real` te dice **cuántos** frames por segundo estás sacando; no te dice si esos frames
llegan **espaciados de forma regular**. Un juego puede marcar 60 fps de media y aun así sentirse
a tirones si los frames llegan en ráfagas irregulares (16, 16, 33, 8, 16 ms…) en vez de cada
16,67 ms clavados — eso es *frame pacing*, y GameMaker expone el control exacto para
diagnosticarlo con dos funciones que hasta ahora no tenían una sola línea propia en esta
biblioteca.

```gml
display_set_timing_method(method);   // fija el método de sincronización
display_get_timing_method();         // consulta cuál está activo
```

Solo hay dos constantes documentadas por el manual oficial (verificado con
`python3 _indice/buscar.py display_set_timing_method`):

| Constante | Qué hace |
|---|---|
| `tm_countvsyncs` | Usa la señal de **vsync** de la plataforma como ancla para el tiempo de renderizado. Es el método **por defecto en todas las plataformas soportadas excepto PS4, Ubuntu y HTML5** — ahí solo está disponible el margen de sueño |
| `tm_sleep` | Ignora vsync: cada frame intenta durar exactamente lo que le toca (1/30, 1/60 s…) esperando o durmiendo el tiempo justo. Es el único método disponible en las plataformas donde vsync no está soportado |

```gml
// Comprobar el método activo y forzar tm_sleep si hiciera falta
if (display_get_timing_method() != tm_sleep)
{
    display_set_timing_method(tm_sleep);
    if (display_get_sleep_margin() != 20) display_set_sleep_margin(20);
}
```

El manual es explícito sobre cuál usar por defecto: *"la sincronización vsync por defecto dará
los resultados más suaves"*, y advierte de que **incluso usando vsync, el margen de sueño sigue
siendo relevante** — recomienda dejarlo en su valor por defecto salvo que sepas por qué lo tocas.
El margen de sueño en sí (`display_set_sleep_margin()`, 4 ms por defecto en móvil / 10 ms en
escritorio) ya está cubierto en
[`04 · 28 §6.3`](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#63-lo-demás-que-se-paga-caro) —
no se repite aquí; lo que faltaba era el propio `display_set_timing_method()`.

⚠️ **Dos constantes más existen en el runtime pero no están documentadas por el manual oficial**:
`tm_countvsyncs_winalt` y `tm_systemtiming` (verificadas con `buscar.py`: existen, se usan en
código de terceros, pero ninguna página del manual las explica). No se recomienda apoyarse en
ellas para un proyecto nuevo — usa `tm_sleep`/`tm_countvsyncs`, que sí tienen comportamiento
documentado por YoYo Games.

**Checklist de *hitching* (tirones), las tres causas que de verdad importan:**

| Causa | Dónde se diagnostica y se corrige |
|---|---|
| **Garbage Collector** disparando en mitad de una escena de acción | [`01 · 15 §5`](./15%20-%20Depuración%20y%20rendimiento.md#5-el-garbage-collector-recolector-de-basura) — `gc_target_frame_time()`, y `gc_collect()` forzado en un momento seguro |
| **Carga de texturas/assets** en el momento equivocado | [`04 · 41 §3.3`](../04%20-%20Recetas%20por%20género/41%20-%20Transiciones%2C%20carga%20y%20pausa.md#33-la-pantalla-de-carga-real) — pantalla de carga real con `texturegroup_get_status()` |
| **Vsync/margen de sueño** mal ajustado para la plataforma | Esta sección + [`04 · 28 §6.3`](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#63-lo-demás-que-se-paga-caro) |

Las tres vivían dispersas en tres documentos sin conectarse entre sí; si el juego «va a
tirones» sin más pista, repasa las tres en ese orden antes de sospechar de tu propio código de
Step.

---

## 8. Time Sources: la alternativa moderna a los alarm

Un **Time Source** (TS) es un temporizador personalizado que creas tú. Corre durante un periodo, expira, y al expirar llama a un **método callback**.

Puede repetirse N veces o para siempre. Cada repetición se llama **«rep»**.

### Crear y arrancar

```gml
time_source_create(padre, periodo, unidades, callback, [args, repeticiones, tipo_expiracion])
```

| Argumento | Qué es |
|---|---|
| `padre` | `time_source_global`, `time_source_game`, u otro Time Source propio |
| `periodo` | Cuánto dura. **Si usas frames, debe ser entero** (se redondea hacia abajo; valores < 1 suben a 1) |
| `unidades` | `time_source_units_seconds` o `time_source_units_frames` |
| `callback` | El método o script function a llamar al expirar |
| `args` (opcional) | Array con los argumentos. **Cada elemento se pasa como argumento separado** (no el array entero) |
| `repeticiones` (opcional) | Cuántas veces se repite. **1** = una sola vez (por defecto). **-1** = infinito |
| `tipo_expiracion` (opcional) | `time_source_expire_nearest` o `time_source_expire_after` |

> ⚠️ **Crear un Time Source NO lo arranca.** Debes llamar a `time_source_start()`.
> ⚠️ **Debes destruirlo** con `time_source_destroy()` cuando no lo necesites.

### Ejemplo 1: destruir la instancia en 300 frames

```gml
var _mi_metodo = function()
{
    instance_destroy();
}

time_source = time_source_create(
    time_source_game,
    300,
    time_source_units_frames,
    _mi_metodo
);

time_source_start(time_source);

// Clean Up / Room End
if (time_source_exists(time_source))
{
    time_source_destroy(time_source);
    time_source = -1;
}
```

### Ejemplo 2: un temporizador global que se repite cada segundo

```gml
// En la RAÍZ de un script (scope global)
var _mi_metodo = function()
{
    show_debug_message("¡Ha pasado un segundo!");
}

global.ts_por_segundo = time_source_create(
    time_source_game,
    1,
    time_source_units_seconds,
    _mi_metodo,
    [],
    -1,                          // infinito
    time_source_expire_after
);

time_source_start(global.ts_por_segundo);
```

### Ejemplo 3: pasar argumentos

```gml
var _callback = function(_x, _y, _objeto)
{
    instance_create_layer(_x, _y, "Instances", _objeto);
}

// ⚠️ Se pasa un ARRAY, pero el método recibe los elementos SUELTOS
var _ts = time_source_create(
    time_source_game,
    2,
    time_source_units_seconds,
    _callback,
    [30, 600, obj_enemigo]     // → _callback(30, 600, obj_enemigo)
);
time_source_start(_ts);
```

### Atajo: `call_later()` y `call_cancel()`

Para temporizadores de un solo uso:

```gml
var _id = call_later(60, time_source_units_frames, function()
{
    show_debug_message("Un segundo después");
});

// Cancelar
call_cancel(_id);
```

> ⚠️ **No puedes usar las funciones de Time Source con los IDs de `call_later()`.** Son incompatibles.

### Funciones disponibles

```
time_source_create / destroy / start / stop / pause / resume
time_source_reconfigure / reset / exists
time_source_get_children / parent / period
time_source_get_reps_completed / reps_remaining
time_source_get_state / time_remaining / units

// Conversión
time_seconds_to_bpm(bpm)  /  time_bpm_to_seconds(segundos)
```

> Cada función `get_*` devuelve `undefined` si el Time Source no existe.

### Cuándo usar alarm vs Time Source

| | Alarm | Time Source |
|---|---|---|
| Temporizador simple por instancia | ✅ | ➖ |
| Necesitas pausarlo / reanudarlo | ❌ | ✅ |
| Necesitas reconfigurarlo en caliente | ❌ | ✅ |
| Scope global (no ligado a instancia) | ❌ | ✅ |
| Quieres saber cuánto queda | ❌ | ✅ |
| Jerarquía de temporizadores (padre/hijo) | ❌ | ✅ |
| Ligado al tempo musical (BPM) | ❌ | ✅ |

> ⚠️ **Recuerda:** los Time Sources se actualizan («ticks») **entre Begin Step y Step**. Es el momento en que se ejecutan los callbacks.

---

## 8 bis. Pausar de verdad

`global.pausado = true;` no para nada por sí sola: es una etiqueta que tu propio código debe
leer, y cada sistema tiene una regla distinta. `instance_deactivate_all(true)` (la técnica de
[04 · 00 §5](../04%20-%20Recetas%20por%20género/00%20-%20Anatomía%20de%20un%20juego%20completo.md#5--el-bucle-de-juego-zonas-hud-pausa-guardado))
para de golpe Step, Alarm, Collision, Draw **y** la animación automática de sprite — el manual
dice que una instancia desactivada «no es procesada de ninguna manera» — pero **no toca nada
que viva fuera del sistema de instancias**:

- **Time Sources.** Corren en su propia fase del step (tabla del §4, arriba), ajenas por
  completo a qué instancias estén activas.
- **Sistemas de partículas** (`part_system_create`) y **Sequences en una capa**
  (`layer_sequence_create`) — ninguno de los dos es una instancia.
- **La física de Box2D**: el propio manual de `physics_pause_enable` avisa de que un cuerpo
  físico **sigue simulándose** aunque su instancia esté desactivada.

Y al revés: si usas el patrón de `global.time_scale = 0` de
[04 · 15 §5.0](../04%20-%20Recetas%20por%20género/15%20-%20Game%20feel%20y%20juice.md#50-sistema-de-tiempo-hit-stop-y-time-scale)
en vez de desactivar instancias (para que el mundo siga visible detrás del menú), las
**Alarmas siguen contando y disparándose** — el motor las decrementa en la fase `ALARMS` de la
tabla del §4, **antes** de que corra tu Step, así que un `if (time_delta() == 0) exit;` llega
tarde para pararlas.

La receta completa —qué función usar para cada sistema, el registro de partículas y
Sequences, la jerarquía de Time Sources que se pausan todas con una sola llamada, y la tabla
de cuándo conviene cada uno de los dos métodos— está en
[04 · 41 — Transiciones, carga y pausa §3.1](../04%20-%20Recetas%20por%20género/41%20-%20Transiciones,%20carga%20y%20pausa.md#31-pausar-de-verdad-el-cimiento-que-usan-las-otras-dos-piezas).

---

## 9. Eventos asíncronos

Se disparan por la finalización de una acción externa, no por el bucle de juego.

Tipos principales:
- **Async - Save/Load:** fin de carga/guardado de archivos.
- **Async - HTTP:** respuesta de un servidor.
- **Async - System:** cambios del sistema (conexión de gamepads, estado del audio en web…).
- **Async - Audio Playback Ended:** cuando un sonido termina.
- **Async - Audio Recording / Cloud / Steam / Image Loaded / Dialog / Push Notification…**

Todos rellenan el DS map global **`async_load`** con los datos del evento.

```gml
// Async - System: detectar gamepads
if (async_load[? "event_type"] == "gamepad discovered")
{
    var _slot = async_load[? "pad_index"];
    show_debug_message($"Gamepad conectado en slot {_slot}");
}
```

> ⚠️ Los datos de `async_load` solo son válidos **dentro del evento**. Si necesitas conservarlos, cópialos.

---

## 10. Resumen visual: el step completo

```
┌─────────────────────── UN STEP / FRAME ───────────────────────┐
│                                                               │
│  BEGIN STEP                                                   │
│      ↓                                                        │
│  TIMELINES                                                    │
│      ↓                                                        │
│  TIME SOURCES  (ticks + callbacks: global → call_later → game) │
│      ↓                                                        │
│  ALARMS                                                       │
│      ↓                                                        │
│  STEP                                                         │
│      ↓                                                        │
│  MOVIMIENTO  (hspeed / vspeed / paths)                        │
│      ↓                                                        │
│  COLISIONES  (si hay sólido → retroceden + collision events)  │
│      ↓                                                        │
│  END STEP                                                     │
│      ↓                                                        │
│  ┌────────────── DIBUJADO ──────────────┐                     │
│  │  PRE-DRAW      (display buffer)      │                     │
│  │  DRAW BEGIN                          │                     │
│  │  DRAW                                │  orden por depth:   │
│  │  DRAW END                            │  depth alto → debajo│
│  │  POST-DRAW     (display buffer)      │                     │
│  │  DRAW GUI BEGIN                      │                     │
│  │  DRAW GUI                            │  siempre encima     │
│  │  DRAW GUI END                        │                     │
│  └──────────────────────────────────────┘                     │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Reglas para no sufrir

1. **No confíes en el orden de las instancias**, solo en el orden de los eventos.
2. **No leas variables de otras instancias en el Create**: quizá no existan todavía.
3. **Limpia recursos dinámicos en Clean Up**, no en Destroy (Clean Up también cubre fin de room y fin de juego).
4. **Draw GUI siempre va encima**, sin importar la capa.
5. **No pongas lógica en eventos de Draw**; y recuerda que `visible = false` los desactiva todos.
6. **`room_speed` está deprecado**: usa `game_set_speed()` / `game_get_speed()`.
7. **Usa Time Sources** si necesitas pausar, reconfigurar o consultar el tiempo restante.
8. **Los eventos asíncronos no siguen el orden del step**: pueden dispararse en cualquier momento.
