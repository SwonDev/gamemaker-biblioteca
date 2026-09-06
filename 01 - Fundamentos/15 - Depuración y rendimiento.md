# 15 · Depuración y rendimiento

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Debugging/Debugging.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Debugging/The_Debug_Overlay.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Garbage_Collection/Garbage_Collection.htm>
> - <https://manual.gamemaker.io/lts/en/Introduction/The_Output_Window.htm>
> - <https://manual.gamemaker.io/lts/en/Introduction/Compiling.htm>

---

## 1. Las tres capas de depuración

GameMaker te da herramientas en tres niveles:

| Nivel | Herramienta | Para qué |
|---|---|---|
| **Estático (al escribir)** | **Feather** + ventana *Syntax Errors* | Errores antes de compilar |
| **En el IDE (al ejecutar)** | **El Debugger** + *Compile Errors* + Output | Inspeccionar variables, breakpoints, callstack |
| **En el juego (runtime)** | **Debug Overlay** + `show_debug_message()` | FPS, memoria, texturas, GC, audio |

---

## 2. Nivel 1: Feather y errores de sintaxis

**Feather** es el analizador estático. Se configura en *Feather Preferences*.

- Muestra errores, avisos y sugerencias en la ventana **Feather Messages**.
- Doble clic en cualquier entrada para ir al código.
- Analiza también las expresiones dentro de los **template strings** `$"...{ }"`.
- Tiene función de **Quick Fixes**, cuyos resultados salen en *Search Results*.

### Códigos útiles que verás

| Código | Significado |
|---|---|
| **GM2017** | Reglas de nomenclatura de assets |
| **GM2043** | Acceso a una variable `static` antes de su línea de inicialización |
| **GM1028** | Accessor aplicado al tipo equivocado (por ejemplo `\|` sobre un array) |

### Los dos avisos que no impiden compilar (pero revisa)

- Variable **declarada y nunca usada**.
- Variable **usada sin declarar**.

Normalmente es un *typo*. Otras veces es intencional (declaras para uso futuro).

### La ventana Syntax Errors

Se actualiza **con retardo** mientras escribes, para no reportar código a medio terminar. Formato:

```
[objeto] - [evento] - [línea] - [posición]: [error]
[script] - [línea] - [posición]: [error]
```

---

## 3. Nivel 2: el Debugger

Se lanza con el botón **Debug** (🐛) en lugar de Play. Abre la ventana de depuración, donde puedes:

- **Inspeccionar variables** en tiempo real.
- Ver la **pila de llamadas** (*callstack*).
- Recorrer el código paso a paso.
- Ver todas las instancias activas.

### Breakpoints

- Se ponen con **F9** en la línea deseada.
- Aparecen en la pestaña **Breakpoints** del Output.
- Se pueden **desactivar** (checkbox) sin borrarlos.
- Clic derecho → eliminar o abrir la ventana de código correspondiente.

### Macros de depuración integrados

| Macro | Contenido |
|---|---|
| `__GMLINE__` | El número de línea tal como se muestra en el editor |
| `__GMFILE__` | El nombre del archivo de código actual |
| `__GMFUNCTION__` | El nombre de la función más interna donde se usa |

```gml
show_debug_message(__GMFILE__);
show_debug_message(__GMLINE__);
show_debug_message(__GMFUNCTION__);
```

Ejemplos de valores:

| Contexto | `__GMFILE__` |
|---|---|
| Script asset | `gml_GlobalScript_Script1` |
| Evento de objeto | `gml_Object_Objeto1_Create_0` |
| Room Creation Code | `gml_Room_Room1_Create` |
| Función anónima | `gml_Script_anon@12@gml_Object_Objeto1_Create_0` |

> 💡 `__GMFUNCTION__` tiene el mismo valor que `__GMFILE__` si se usa **fuera** de cualquier definición de función.
> ⚠️ `__GMLINE__` requiere activar los números de línea en las preferencias del editor de texto.

### Funciones de depuración

```
debug_mode                   ¿Estoy en modo debug? (VARIABLE, no función: sin paréntesis)
debug_event(mensaje)         Añade una entrada al log del debugger
debug_get_callstack([max])   Devuelve el callstack como array
exception_unhandled_handler(metodo)   Captura excepciones no manejadas

get_integer(cadena, defecto)   Pide un número al usuario
get_string(cadena, defecto)    Pide un texto al usuario
show_error(cadena, abortar)    Muestra un error
show_message(cadena)           Ventana de mensaje
show_question(cadena)          Sí / No

show_debug_message(cadena)     Mensaje al log
show_debug_message_ext(...)    Con formato
show_debug_overlay(activar)    Abre/cierra el overlay
show_debug_log(activar)        Abre/cierra el overlay con el Log

code_is_compiled()             ¿Está el código compilado (YYC)?
fps                            FPS lógicos
fps_real                       FPS reales
```

> ⚠️ Las funciones `get_integer()`, `get_string()`, `show_message()` y `show_question()` **ponen el juego en un bucle cerrado** hasta que se resuelven. Por eso **se ignoran al compilar para targets que no sean Windows** (salvo en modo debug).
>
> ⚠️ **Nunca las uses en el juego final. Son solo para depurar.**

### Grabación y reproducción de input

```
debug_input_record()   debug_input_save()   debug_input_playback()
```

Permiten grabar la entrada del jugador y reproducirla para reproducir bugs.

> ⚠️ **Solo para depuración. No en el juego final.**

### Capturar excepciones no manejadas

```gml
// Create de un objeto controlador
exception_unhandled_handler(function(_excepcion)
{
    var _mensaje = $"ERROR: {_excepcion.message}\n";
    _mensaje    += $"En: {_excepcion.script} línea {_excepcion.line}\n";
    _mensaje    += $"Callstack:\n";

    var _pila = debug_get_callstack(20);
    for (var i = 0; i < array_length(_pila); i++)
    {
        _mensaje += $"  {_pila[i]}\n";
    }

    show_debug_message(_mensaje);

    // Opcional: guardar a archivo para tener un log del jugador
    var _f = file_text_open_append("crash.log");
    file_text_write_string(_f, _mensaje);
    file_text_writeln(_f);
    file_text_close(_f);
});
```

> 💡 Esto es invaluable para diagnosticar fallos en builds que envías a testers.

---

## 4. Nivel 3: el Debug Overlay

El overlay es una capa **dentro del juego** que muestra información en tiempo real.

```gml
show_debug_overlay(true);   // abre con la ventana FPS
show_debug_log(true);       // abre con la ventana Log
```

> ⚠️ **No está soportado en HTML5.**
> Se puede manejar con teclado, ratón y gamepad (usa el primer gamepad que encuentre).

### Ventanas integradas

| Ventana | Contenido |
|---|---|
| **FPS** | Abierta por defecto. Gráfico de frame time + contadores |
| **Log** | El Output Log del IDE, con consola de comandos |
| **Audio** | Buffer de salida y lista de fuentes |
| **Memory** | Memoria asignada/libre + estado del GC |
| **Texture Groups** | Grupos de texturas, carga/descarga |
| **Texture** | Visor de texture pages |
| **FlexPanel** | Previsualización de Flex Panels |
| **DebugView** | Visibilidad de tus vistas personalizadas |

### La ventana FPS: cómo leerla

La barra de título muestra:
- **Texture swaps** (cambios de textura)
- **Vertex batches** (lotes de vértices)
- **FPS real**
- Una barra con los tiempos apilados

> ⚠️ **Los dos primeros nunca serán cero.** Incluso con una room vacía verás 2 o 3, porque GameMaker siempre tiene que dibujar y agrupar algo.

**FrameTime** es lo que tardó cada frame, en segundos. Con el juego a 60 FPS, cada frame tiene **1/60 = 0.01666… s**. Si tarda más, GameMaker sigue procesando el frame actual cuando ya debería estar en el siguiente, y los FPS caen.

Con la opción **Stacked** activada verás el desglose:

| Categoría | Qué mide |
|---|---|
| **Garbage Collector** | Tiempo del recolector de basura |
| **IO&YoYo** | Teclado, ratón, gamepads, red y algo de procesamiento del SO |
| **Update** | El bucle de actualización (eventos Step, etc.) |
| **Draw** | El dibujado (eventos Draw) |
| **Text** | El texto de las Sequences |
| **Scroll** | Los fondos con scroll de las rooms y el vídeo |

Puedes hacer clic en cada valor para mostrarlo/ocultarlo. El control **History** ajusta el rango horizontal del gráfico (1-30 segundos).

### La ventana Log: una consola en vivo

Permite escribir comandos:
- Un **nombre de variable global** → imprime su valor.
- Un **nombre de función global** → la ejecuta, con argumentos separados por espacios.
- **Flechas arriba/abajo** → historial.
- **Tab** → autocompletado (aparece con más de 2 caracteres).

```gml
show_debug_message "¡Hola Mundo!"
```

> ⚠️ **Sin paréntesis.** Si los pones, verás `ERROR : unknown command`.
>
> ⚠️ **Mientras escribes, el juego sigue recibiendo el input** y disparando eventos de teclado.
> 💡 Los scripts se ejecutan en el ámbito del struct `global`.

Reglas de conversión de argumentos:
1. Intenta interpretarlo como valor global.
2. Si es nombre de asset, pasa la referencia.
3. `true` / `false` → booleanos.
4. Si es número → real.
5. Texto entre comillas dobles → string.
6. Cualquier otra cosa → string.

### La ventana Audio

Muestra el **buffer de salida más reciente** del hilo de audio (la señal final tras mezclar y procesar).

La lista de fuentes se colorea por estado:

| Color | Estado |
|---|---|
| Blanco | Suena ahora |
| Rojo | Ha terminado |
| Amarillo | En pausa |
| Magenta | Preparándose (transitorio) |
| Cian | Deteniéndose (transitorio) |

Columnas: `source`, `buffer`, `syncSource`, `numQueued`, `gain` (16 bits, 0-65535), `name`, `pos` (frames, en hex).

También se abre con `audio_debug()`.

### La ventana Memory

- **Allocated memory** (asignada por el SO) y **Free memory** (libre), con gráfico en el tiempo.
- Sección del **Garbage Collector** con dos botones: **Force Collection** y **Toggle GC**, más una gráfica de objetos tocados y recogidos.

### La ventana Texture

Muestra **todas las texture pages** del juego, incluidas tus surfaces y la application surface.

Información por textura:
- `width`, `height`
- `group` (nombre del texture group; `<unknown>` si no pertenece a ninguno)
- `index in group` (una textura puede ocupar varias páginas)
- `num mips` (niveles de mipmap)

> ⚠️ Acceder a **Dynamic Textures** descargadas en este visor las carga a memoria y VRAM para poder mostrarlas.

### ⚠️ El overlay bloquea los eventos de teclado y ratón

Cuando el ratón está sobre cualquier menú o ventana del overlay, o el overlay espera input de teclado, **GameMaker no dispara eventos de teclado ni ratón**. Las funciones sí siguen funcionando.

```gml
if (!is_keyboard_used_debug_overlay() && keyboard_check(vk_up))
{
    // no se ejecuta si el overlay está usando el teclado
}
```

### Vistas de depuración personalizadas (muy potente)

Puedes crear tus propias ventanas de depuración con controles en vivo:

```gml
// Create de un objeto de debug
custom_dbgview = dbg_view("Mi Debug View", true);
custom_section = dbg_section("Jugador");

// Referencia a una variable (debe estar en un struct o instancia:
// las locales NO funcionan, porque la vista se declara una sola vez)
ref_vida   = ref_create(obj_jugador, "vida");
ref_puntos = ref_create(self, "puntos");

dbg_slider_int(ref_vida, 0, 100, "Vida", 1);
dbg_watch(ref_puntos, "Puntos");
dbg_checkbox(ref_create(obj_jugador, "invencible"), "Invencible");

boton_curarse = function()
{
    with (obj_jugador) { vida = vida_max; }
}
dbg_button("Curar", ref_create(self, "boton_curarse"));
```

> ⚠️ **El orden de los argumentos engaña:** en `dbg_watch`, `dbg_checkbox`, `dbg_slider` y
> `dbg_slider_int` la **referencia va primero y la etiqueta después** (`dbg_watch(ref, "Etiqueta")`).
> La única que lleva la etiqueta delante es `dbg_button("Etiqueta", ref)`. Comprobado en
> `GmlSpec.xml`: `python3 "_indice/buscar.py" dbg_watch`.

**Controles disponibles:**

```
dbg_view(nombre, visible, [x], [y], [w], [h])
dbg_section(name, [open])
dbg_set_view(vista)   dbg_set_section(seccion)

dbg_button          dbg_checkbox      dbg_colour
dbg_drop_down       dbg_same_line     dbg_slider
dbg_slider_int      dbg_sprite        dbg_sprite_button
dbg_text            dbg_text_input    dbg_text_separator
dbg_watch

dbg_view_exists / dbg_view_delete
dbg_section_exists / dbg_section_delete
dbg_control_exists / dbg_control_delete

dbg_add_font_glyphs     dbg_get_gamepad_input
is_mouse_over_debug_overlay / is_keyboard_used_debug_overlay
```

> ⚠️ **Las variables deben existir en un struct o una instancia.** Las **locales no se pueden mostrar**, porque la vista se declara una sola vez.
> 💡 Un control creado antes de cualquier sección va a una sección llamada «Default».
> 💡 Las vistas personalizadas solo se muestran si **DebugView** está activado en el menú Debug.

---

## 5. El Garbage Collector (recolector de basura)

### Por qué existe

Los métodos, structs y arrays pueden quedar sin referencias. Sin limpieza, eso sería un memory leak. El GC corre en segundo plano recogiendo lo que se ha desreferenciado.

> *«When we talk about something being de-referenced, we generally refer to any struct or function which isn't connected (directly or through a chain of other variables) to a **global** variable or an **object instance variable**.»*

### ⚠️ Lo que el GC NO recoge

> **Las surfaces, estructuras de datos, buffers y otros recursos dinámicos NO los recoge el GC.** Tienen sus propias funciones de destrucción.

**Regla general: si lo que creas tiene una función `*_destroy()`, `*_free()` o `*_delete()`, límpialo tú.**

> ⚠️ **Excepción:** las sequences, animation curves e instancias **sí** requieren el GC, **pero aun así hay que llamar a su función de destrucción**.

### Cómo funciona: generacional + incremental

- Los objetos nacen en la **generación 0** y envejecen hacia generaciones superiores.
- Las generaciones antiguas se comprueban con menos frecuencia (los objetos que llevan tiempo no necesitan revisarse constantemente).
- La limpieza es **incremental**: en vez de limpiar miles de objetos en un solo frame (pico de CPU), se reparte entre varios frames.

### Funciones

```gml
gc_enable(true);             // activar/desactivar
gc_is_enabled();
gc_collect();                // forzar una recogida
gc_target_frame_time(ms);    // cuánto tiempo dedicar por frame
gc_get_target_frame_time();
gc_get_stats();              // estadísticas
```

```gml
// Ajustar el presupuesto del GC: más tiempo = recogidas más agresivas
gc_target_frame_time(2);   // 2 ms por frame

// Forzar una recogida en un momento seguro (por ejemplo, al cambiar de room)
gc_collect();
```

> ⚠️ **En HTML5 la recogida la hace el motor de JavaScript**, así que ninguna de estas funciones afecta a su funcionamiento y `gc_get_stats()` devuelve `0` en todos los campos.

### Referencias débiles

Una **weak reference** no protege al objeto de la recogida. Sirve para comprobar si un struct sigue «vivo».

```gml
ref_debil = weak_ref_create(mi_struct);

// ...más tarde...
if (weak_ref_alive(ref_debil))
{
    // el struct sigue existiendo
}

// ¿Alguna de varias sigue viva?
if (weak_ref_any_alive(ref1, ref2, ref3)) { ... }
```

```gml
// Ejemplo: un sistema de "objetivos" que no impide que los enemigos se liberen
objetivo_debil = weak_ref_create(enemigo);

// Step
if (!weak_ref_alive(objetivo_debil))
{
    objetivo_debil = undefined;   // el enemigo ya no existe: buscamos otro
}
```

---

## 6. Rendimiento: dónde está el cuello de botella

### Paso 1: mide antes de optimizar

Abre el **Debug Overlay** y mira la ventana **FPS** con **Stacked** activado. Te dirá si tu problema está en:

| Si domina… | El problema está en… | Mira… |
|---|---|---|
| **Update** | La lógica (Step) | Bucles pesados, instancias activas, `with()` sobre objeto |
| **Draw** | El dibujado | Texture swaps, vertex batches, surfaces |
| **Garbage Collector** | Asignaciones excesivas | Crear structs/arrays en el Step |
| **IO&YoYo** | Input / red | Sondeos constantes, operaciones de red |
| **Text** | Sequences | Texto en secuencias |
| **Scroll** | Fondos con scroll | Fondos grandes con scroll |

### Paso 2: los sospechosos habituales

#### Demasiadas instancias activas

```gml
// Desactiva lo que esté fuera de cámara (en una ALARMA, no en el Step)
instance_deactivate_all(colspace.room);
instance_activate_region(_vx - 128, _vy - 128, _vw + 256, _vh + 256, true);
```

> ⚠️ No lo hagas cada step: puede empeorar el rendimiento. Cada 10-15 steps suele bastar.

#### Código en el Draw

El Draw debe **solo dibujar**. Mueve los cálculos al Step.

#### Cambios de textura (texture swaps)

Ordena los dibujados por textura. Ver **tema 11**.

#### Crear structs/arrays en el Step

Cada `{}` o `[]` dentro del Step es una asignación que el GC tendrá que recoger.

```gml
// ❌ Crea un struct nuevo cada frame
// Step
var _pos = { x: x, y: y };
procesar(_pos);

// ✅ Reutiliza un struct creado una vez
// Create
_pos = { x: 0, y: 0 };
// Step
_pos.x = x;
_pos.y = y;
procesar(_pos);
```

#### `with()` sobre objetos con muchas instancias

```gml
with (obj_enemigo)   // si hay 5000 enemigos, esto recorre los 5000
{
    // ...
}
```

Considera mantener tu propia lista de instancias relevantes.

#### Cadenas de texto construidas cada frame

```gml
// ❌ Concatena strings cada frame
draw_text(10, 10, "Vida: " + string(vida));

// ✅ Solo actualiza cuando cambia
if (vida != vida_anterior)
{
    texto_vida = "Vida: " + string(vida);
    vida_anterior = vida;
}
draw_text(10, 10, texto_vida);
```

### Paso 3: la ventana Texture

Mira cuántas **texture pages** tienes. Si tus sprites se reparten por muchas páginas, cada dibujo que salte de una a otra rompe el batch.

**Solución:** asigna a un mismo **Texture Group** los sprites que se dibujan juntos.

### Paso 4: VM vs YYC

Si tu juego es intensivo en **lógica**, el **YYC** puede multiplicar el rendimiento **×2 o ×3**.

> ⚠️ YYC no hace milagros con el **dibujado** (que está en la GPU). Si tu cuello está en *Draw*, YYC no te va a salvar.

### Paso 5: optimizaciones del compilador

Por defecto, **los assets que no se referencian directamente en el código se eliminan** del ejecutable. Para preservarlos:

```gml
gml_pragma("MarkTagAsUsed", "mis_assets_importantes");
```

### Paso 6: cuánto cuestan las colisiones

Las colisiones no han salido hasta ahora en este documento, y son una de las formas más
silenciosas de perder rendimiento: el código «funciona», solo que cada vez menos rápido a
medida que crece el número de instancias.

**La forma de la máscara no es gratis.** `Rectangle` es la más barata (un test de rectángulos
alineados a ejes); `Rectangle With Rotation`, `Ellipse` y `Diamond` cuestan más al añadir
geometría; `Precise` y sobre todo `Precise per frame` son las más caras porque siguen el
contorno de píxeles del sprite en vez de una forma simple. Tabla completa de las seis formas,
sus constantes `bboxkind_*` y `sprite_collision_mask()` en
[01 · 08 §4 «Elegir la forma de la máscara»](./08%20-%20Movimiento%20y%20colisiones.md).

> ⚠️ **Por qué `all` sale caro.** Cuando pasas `all` a `place_meeting()`, `instance_place()`,
> `move_and_collide()` o cualquier `collision_*()`, el motor no tiene un grupo reducido de
> candidatos por tipo de objeto: tiene que considerar cualquier instancia activa de la room. Con
> un **objeto padre** (`obj_solido`, `obj_enemigo`…) o un **tipo concreto** en vez de `all`, la
> comprobación se limita a las instancias de ese tipo (y sus hijos). Esto es razonamiento sobre
> cómo se organiza la comprobación, no una cifra medida: confírmalo en tu proyecto con el
> fragmento de más abajo antes de asumirlo.

**Cuándo el problema es el NÚMERO de instancias, no la forma de la máscara.** Si cientos de
instancias comprueban colisión contra cientos de instancias cada Step, el coste no crece
linealmente: crece con el **cuadrado** del número de instancias (cada una contra todas las
demás). Dos salidas, de más simple a más trabajo:

1. **Reducir cuántas están activas de verdad.** `instance_deactivate_region()` /
   `instance_activate_region()` — ya visto en el **Paso 2** de este mismo documento — saca de
   la simulación lo que está lejos de la cámara. Es la primera palanca, y la más barata de
   implementar.
2. **Dejar de comprobar todas contra todas.** Si el paso 1 no basta (mundos grandes, muchas
   instancias activas a la vez), hace falta particionar el espacio: una rejilla que solo
   compare cada instancia con sus vecinas de celda. Desarrollado a fondo, con código completo,
   en [13 · 08 §4 «Particionado espacial: colisiones cuando hay cientos de cosas»](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/08%20-%20F%C3%ADsicas%20a%20mano%20y%20fluidos.md)
   (spatial hash) — el mismo patrón sirve tanto para física a mano como para colisiones con
   `place_meeting()` / `move_and_collide()`.

**Mide, no adivines.** El mismo patrón de `get_timer()` que
[13 · 08 §14 «Rendimiento: medir antes de decidir»](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/08%20-%20F%C3%ADsicas%20a%20mano%20y%20fluidos.md)
usa para separar el coste de cada sistema en microsegundos funciona igual para colisiones:

```gml
/// obj_jugador · Step — cuánto cuesta la comprobación de colisión, en microsegundos
var _t0 = get_timer();
var _col = move_and_collide(vel_x, vel_y, [obj_solido, tilemap_suelo]);
coste_colision_us = get_timer() - _t0;
```

Compáralo contra el presupuesto de **16 666 µs por frame** a 60 fps: un sistema de colisiones
que se lleve una parte importante de eso ya merece atención, antes de tocar nada más.

---

## 7. Checklist de rendimiento

```
[ ] ¿He medido con el Debug Overlay antes de tocar nada?
[ ] ¿Sé si mi cuello de botella está en Update o en Draw?
[ ] ¿Cuántos texture swaps y vertex batches tengo?
[ ] ¿Desactivo las instancias fuera de cámara?
[ ] ¿Agrupo los dibujos por textura?
[ ] ¿Creo structs/arrays dentro del Step? (¿puedo reutilizarlos?)
[ ] ¿Tengo código de lógica dentro de eventos de dibujado?
[ ] ¿Libero surfaces, buffers, estructuras de datos y time sources?
[ ] ¿Destruyo las cámaras que creo?
[ ] ¿Están mis sprites agrupados en texture groups sensatos?
[ ] ¿He ajustado gc_target_frame_time() si el GC aparece mucho en la gráfica?
[ ] ¿He probado con YYC?
[ ] ¿He limpiado la caché del compilador antes del build final?
```

---

## 8. Checklist de limpieza de recursos dinámicos

Esta tabla es oro. **Todo lo que creas en runtime y tenga función de destrucción debe destruirse.**

| Recurso | Crear | Destruir | Resetear a |
|---|---|---|---|
| Surface | `surface_create()` | `surface_free()` | `-1` |
| Buffer | `buffer_create()` | `buffer_delete()` | `-1` |
| Vertex buffer | `vertex_create_buffer()` | `vertex_delete_buffer()` | `-1` |
| DS list / map / grid / stack / queue / priority | `ds_*_create()` | `ds_*_destroy()` | `-1` |
| Time Source | `time_source_create()` | `time_source_destroy()` | `-1` |
| Cámara | `camera_create()` | `camera_destroy()` | `-1` |
| Audio emitter | `audio_emitter_create()` | `audio_emitter_free()` | `-1` |
| Particle system / emitter / type | `part_*_create()` | `part_*_destroy()` | `-1` |
| Instancia | `instance_create_*()` | `instance_destroy()` | `noone` |
| Struct | `{}` / `new X()` | `delete` | — |
| Array | `[]` | `= undefined` | — |

```gml
// Clean Up event — el patrón completo
if (surface_exists(surf))          { surface_free(surf);          surf = -1; }
if (buffer_exists(buff))           { buffer_delete(buff);         buff = -1; }
if (vb != -1)                      { vertex_delete_buffer(vb);    vb   = -1; }
if (mi_lista != -1)                { ds_list_destroy(mi_lista);   mi_lista = -1; }
if (time_source_exists(ts))        { time_source_destroy(ts);     ts   = -1; }
if (cam != -1)                     { camera_destroy(cam);         cam  = -1; }
if (audio_emitter_exists(em))      { audio_emitter_free(em);      em   = -1; }

delete mi_struct;
```

> 💡 **¿Por qué en Clean Up y no en Destroy?** Porque **Clean Up** también se ejecuta al terminar la room y al terminar el juego, no solo al destruir la instancia.

---

## 9. Plantilla de objeto con depuración integrada

```gml
// ═══════════ obj_debug (persistente, solo en builds de desarrollo) ═══════════

// ─── Create ───
if (instance_number(obj_debug) > 1) { instance_destroy(); exit; }
persistent = true;

// Capturar excepciones
exception_unhandled_handler(function(_e)
{
    var _msg = $"[{date_datetime_string(date_current_datetime())}]\n";
    _msg += $"  Mensaje: {_e.message}\n";
    _msg += $"  En: {_e.script}:{_e.line}\n";
    _msg += "  Callstack: " + string(debug_get_callstack(10)) + "\n";

    show_debug_message(_msg);

    var _f = file_text_open_append("crash.log");
    file_text_write_string(_f, _msg);
    file_text_writeln(_f);
    file_text_close(_f);
});

// Vista de depuración propia
if (debug_mode)
{
    dbg_view("Depuración del juego", true);
    dbg_section("Rendimiento");
    dbg_watch(ref_create(self, "fps_mostrado"), "FPS real");
    dbg_watch(ref_create(self, "num_instancias"), "Instancias");
    dbg_watch(ref_create(self, "memoria_mostrada"), "Memoria");

    dbg_section("Jugador");
    if (instance_exists(obj_jugador))
    {
        dbg_slider_int(ref_create(obj_jugador, "vida"), 0, 100, "Vida", 1);
        dbg_checkbox(ref_create(obj_jugador, "invencible"), "Invencible");
    }

    dbg_section("Acciones");
    dbg_button("Forzar GC", ref_create(self, "accion_gc"));
    dbg_button("Recargar room", ref_create(self, "accion_recargar"));
}

fps_mostrado       = 0;
num_instancias     = 0;
memoria_mostrada   = "";
temporizador       = 0;

accion_gc = function()
{
    gc_collect();
    show_debug_message("Recogida de basura forzada");
}

accion_recargar = function()
{
    room_restart();
}

// ─── Step ───
// Actualizamos los contadores solo cada 15 frames (no hace falta más)
if (++temporizador >= 15)
{
    temporizador     = 0;
    fps_mostrado     = round(fps_real);
    num_instancias   = instance_count;

    var _stats = gc_get_stats();
    memoria_mostrada = $"{_stats}";
}

// ─── Draw GUI ───
// Un contador de FPS siempre visible durante el desarrollo
if (debug_mode || !code_is_compiled())
{
    draw_set_alpha(0.7);
    draw_set_colour(c_black);
    draw_rectangle(4, 4, 150, 52, false);
    draw_set_alpha(1);
    draw_set_colour(c_lime);
    draw_set_font(-1);
    draw_text(10, 10, $"FPS: {fps_real}");
    draw_text(10, 26, $"Instancias: {instance_count}");
    draw_set_colour(c_white);
}
```

> 💡 `debug_mode` es una **variable** integrada (⚠️ escribirla con paréntesis, `debug_mode()`, no compila: «unable to use builtin variable as a function call») y vale `true` cuando ejecutas con el botón Debug. `!code_is_compiled()` es `true` en VM. Úsalos para que el HUD de depuración **desaparezca solo** en el build final.

---

## Resumen

1. **Tres capas:** Feather (estático), Debugger (IDE), Debug Overlay (runtime).
2. **Feather** te avisa antes de compilar. Revisa los códigos GM####.
3. **Breakpoints con F9.** Los macros `__GMFILE__`, `__GMLINE__`, `__GMFUNCTION__` te ubican.
4. `exception_unhandled_handler()` te da un **log de errores** para builds de testers.
5. ⚠️ **El Debug Overlay bloquea los eventos** de teclado y ratón (no las funciones). Y **no existe en HTML5**.
6. **La ventana FPS con Stacked te dice DÓNDE está tu cuello de botella.** Mide antes de optimizar.
7. ⚠️ **Texture swaps y vertex batches nunca son 0.** Cuanto más bajos, mejor.
8. **El GC es generacional e incremental.** Ajusta su presupuesto con `gc_target_frame_time()`.
9. ⚠️ **El GC NO recoge surfaces, buffers, estructuras de datos ni time sources.** Destrúyelos en **Clean Up** y resetea a `-1` / `noone`.
10. **Ordena los dibujos por textura** y **desactiva instancias fuera de cámara** para las dos mayores ganancias.
11. **YYC multiplica ×2–×3 la lógica**, pero no el dibujado.
12. Usa `debug_mode` para que el HUD de depuración **se apague solo** en el build final.
