# 15 · Depuración y rendimiento

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Debugging/Debugging.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Debugging/The_Debug_Overlay.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Garbage_Collection/Garbage_Collection.htm>
> - <https://manual.gamemaker.io/lts/en/Introduction/The_Output_Window.htm>
> - <https://manual.gamemaker.io/lts/en/Introduction/Compiling.htm>
> - <https://manual.gamemaker.io/lts/en/IDE_Tools/The_Debugger/The_Profiler.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/OS_And_Compiler/os_get_info.htm> (API gráfica real por plataforma, §11)
> - <https://renderdoc.org/> y <https://renderdoc.org/docs/getting_started/faq.html> (RenderDoc: plataformas y APIs soportadas, consultado 2026-09-07)
> - <https://github.com/odditica/renderdoc-gms2-kit> (kit de la comunidad para capturar builds de GMS2, consultado 2026-09-07)
> - <https://gamemaker.io/en/help/articles/android-troubleshooting> (adb oficial de GameMaker, consultado 2026-09-07 vía curl con User-Agent — 403 sin él)
> - <https://developer.android.com/studio/profile/android-profiler> (Android Profiler, requisitos de versión)

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

### El Profiler

La ventana del Debugger tiene una segunda pestaña, **Profile**, con su propio botón de
activar/desactivar. Mientras está activo, registra cuánto tarda cada evento, script y función en
cada *step*, en microsegundos — es el bisturí que usas después de que el Debug Overlay del §4 te
haya dicho *en qué categoría* (Update, Draw, GC…) está el problema, para encontrar la línea exacta.

- **Pantalla de la hora**: alterna entre **total** (tiempo/llamadas acumulados durante toda la
  sesión de perfilado) y **medio** (por step).
- **Ver Modo**: `Top Down` sigue la jerarquía de la pila de llamadas (evento → script → función);
  `Bottom Up` lista cada función individual y expande hacia arriba quién la llamó — mejor para
  responder «¿desde cuántos sitios distintos se llama a esto?».
- **Ver objetivo**: `GML` (tus eventos, scripts y funciones), `Motor` (llamadas internas del
  runtime) o `Ambos`.
- Doble clic en cualquier fila abre ese código en la ventana **Fuente**.
- Las cuatro columnas (**Nombre**, **Tiempo**, **Llamadas**, **Paso %**) se ordenan haciendo clic
  en su cabecera.

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

> 💡 **¿Cuál es «un momento seguro» de verdad?** La pantalla de carga real de
> [04 · 41 §3.3](../04%20-%20Recetas%20por%20g%C3%A9nero/41%20-%20Transiciones%2C%20carga%20y%20pausa.md#33-la-pantalla-de-carga-real):
> el jugador ya espera ahí, no hay animación crítica en curso, y es el sitio natural para
> colgar un `gc_collect()` explícito justo antes de entrar en la room nueva, en vez de dejar
> que el GC decida disparar en mitad de una escena de acción.

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

#### Crear `function()` dentro del Step

Una función anónima (o un `method()`) creada dentro de un bucle o del Step es, para el GC, la
misma asignación que un struct o un array: cada `function() {...}` reserva memoria nueva que
alguien tendrá que recoger más tarde. El principio de arriba («no crees structs/arrays en el
Step») se aplica igual a los *closures*: el que se ve raro es justo el que más se repite —
pasar un callback a `array_foreach()`, a un Time Source o a un sistema de eventos escribiendo
la función en el sitio en vez de guardarla antes.

```gml
// ❌ Crea una función nueva cada frame, solo para usarla una vez
// Step
array_foreach(enemigos_cerca, function(_enemigo) {
    _enemigo.alerta = true;
});

// ✅ La función se crea UNA VEZ (en el Create) y se reutiliza
// Create
_marcar_alerta = function(_enemigo) {
    _enemigo.alerta = true;
};
// Step
array_foreach(enemigos_cerca, _marcar_alerta);
```

> 💡 Si el callback necesita datos de la instancia que lo llama (`self`), créalo una vez con
> `method(id, function() {...})` en el Create y guárdalo en una variable — no lo re-envuelvas
> con `method()` en cada Step: eso también asigna un método nuevo cada vez.

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

#### Overdraw

**Overdraw** es que el mismo píxel de pantalla se rellene más de una vez en el mismo
fotograma. No es exclusivo de 2D, pero un juego 2D lo dispara con facilidad porque casi todo
lo que hace bonito a un juego —parallax, VFX aditivo, niebla, paneles de UI semitransparentes,
luces por superficie ([04 · 24](../04%20-%20Recetas%20por%20g%C3%A9nero/24%20-%20Iluminación%202D.md))—
son capas que se dibujan unas encima de otras cubriendo la misma zona de pantalla.

**Qué lo dispara, en orden de frecuencia real:**

- **Capas de parallax muy grandes que se solapan** entre sí en vez de recortarse a lo visible.
- **Partículas aditivas apiladas** sin límite — ya avisado en
  [04 · 39 §1.4 y §3.12](../04%20-%20Recetas%20por%20g%C3%A9nero/39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md#312-presupuesto-medido-y-culling-de-emisores):
  el propio manual de partículas señala el overdraw como «la causa principal de tirones en
  móvil».
- **Sprites con mucho margen transparente**: un sprite de 128×128 cuya silueta real ocupa
  32×32 sigue costando el rectángulo completo salvo que se recorte el lienzo o se filtre por
  alfa (ver más abajo).
- **Paneles de UI semitransparentes apilados** (fondo del HUD + panel de diálogo + tooltip,
  todos con alfa, todos ocupando la pantalla entera).

**Cómo medirlo — GameMaker no tiene un contador nativo de overdraw**, así que se infiere de
tres formas, de la más rápida a la más precisa:

1. **Debug Overlay, ventana FPS en modo Stacked** (§4, más arriba en este documento): si
   **Draw** domina el tiempo de fotograma y ya has descartado texture swaps (Paso 3) y exceso
   de instancias, el sospechoso siguiente es overdraw.
2. **Prueba A/B directa**: desactiva la capa sospechosa (una luz, una capa de parallax, un
   emisor) y compara el FPS del overlay con y sin ella. Es el método más fiable porque no
   necesita instrumentación — simplemente aísla la variable.
3. **Visualización de overdraw «casera»**: sustituye temporalmente todo lo que se dibuja por
   un color plano muy tenue en modo aditivo. Las zonas con más capas superpuestas acumulan
   más brillo, así que se ven literalmente más claras cuantas más veces se han redibujado.

   ```gml
   /// obj_control_debug · Draw GUI — activar con una tecla, nunca en build de release
   if (ver_overdraw)
   {
       gpu_set_blendmode(bm_add);
       with (obj_dibujable)              // el padre de todo lo que se dibuja en el juego
       {
           draw_sprite_ext(sprite_index, image_index, x, y,
                            image_xscale, image_yscale, image_angle,
                            c_white, 0.05);           // alfa muy bajo: se acumula por capa
       }
       gpu_set_blendmode(bm_normal);
   }
   ```

**Mitigación:**

- **Menos capas aditivas solapadas** en el mismo punto de pantalla — el mismo consejo que ya
  da [04 · 39 §1.4](../04%20-%20Recetas%20por%20g%C3%A9nero/39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md#14-silueta-y-lectura-a-distancia-aditivo-frente-a-normal):
  aditivo solo en lo que emite luz de verdad.
- **`gpu_set_alphatestenable(true)` + `gpu_set_alphatestref(valor)`**: descarta los píxeles
  con alfa por debajo del umbral **antes** de escribir en el framebuffer, así que las zonas
  totalmente transparentes de un sprite con mucho margen no llegan a mezclarse.

  ```gml
  /// Draw — recortar el coste de un sprite con mucho margen transparente
  gpu_set_alphatestenable(true);
  gpu_set_alphatestref(1);       // descarta cualquier píxel casi invisible (0-1 de 255)
  draw_self();
  gpu_set_alphatestenable(false);
  ```

  > ⚠️ Esto no reduce el coste del *fragment shader* en sí —se sigue evaluando cada píxel—,
  > pero sí evita el coste de mezclar y escribir los que de todas formas no se verían.
- **Recorta el lienzo del sprite al contenido real** en el editor de imagen, en vez de dejar
  un margen grande «por si acaso» — menos overdraw y menos memoria de textura a la vez.
- **Desactiva capas fuera de cámara** con el mismo patrón que ya usan las partículas
  (`part_emitter_enable(false)` en [04 · 39 §3.12](../04%20-%20Recetas%20por%20g%C3%A9nero/39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md#312-presupuesto-medido-y-culling-de-emisores))
  y las instancias (`instance_deactivate_all` / `instance_activate_region`, arriba en este
  mismo apartado): una luz o una capa que no se ve no debería seguir dibujándose.

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

## 10. Depurar un guardado en producción

Un bug de guardado casi nunca lo ves tú: te llega como un mensaje de un jugador ("se me borró
la partida", "cargué y no era mi progreso"), sin tu IDE delante y sin poder poner un breakpoint.
Esta sección cubre las tres piezas que hacen ese caso resoluble: **mirar** el save sin salir
del juego, **editarlo** a mano para reproducir el escenario, y **pedirle al jugador el fichero
correcto** sin pedirle de paso datos que no necesitas.

### 10.1 Inspector de guardado con el Debug Overlay

`dbg_text()` muestra el contenido de una variable como texto; combinado con las funciones de
[`06 · Assets y Scripts/scr_save_load.gml`](../06%20-%20Assets%20y%20Scripts/scr_save_load.gml)
(§4 arriba tiene el resto de controles `dbg_*`), esto es un inspector completo en menos de 30
líneas, sin salir del juego ni escribir una pantalla propia:

```gml
// ═══ obj_debug · Create (solo en builds de desarrollo, junto al resto de dbg_view) ═══
inspector_slot = "slot1";
inspector_json = "(pulsa Inspeccionar)";

if (debug_mode)
{
    dbg_view("Inspector de guardado", false);
    dbg_section("Guardado");
    dbg_text_input(ref_create(self, "inspector_slot"), "Slot");
    dbg_button("Inspeccionar", ref_create(self, "inspector_refrescar"));
    dbg_button("Copiar JSON", ref_create(self, "inspector_copiar"));
    dbg_text_separator("Contenido (solo lectura)");
    dbg_text(ref_create(self, "inspector_json"));
}

inspector_refrescar = function()
{
    // load_game_raw() ya desenvuelve el checksum y migra el formato interno:
    // aquí solo se lee para MIRAR, nunca se llama a save_game() por accidente.
    var _sobre = load_game_raw(inspector_slot);
    inspector_json = is_struct(_sobre)
        ? json_stringify(_sobre.datos, true)              // con indentación: legible
        : $"(no hay guardado válido en el slot '{inspector_slot}')";
}

inspector_copiar = function()
{
    clipboard_set_text(inspector_json);   // para pegarlo en un issue o en un chat
}
```

> ⚠️ **Es de solo lectura a propósito.** `dbg_text_input` permite editar texto en pantalla, pero
> reconstruir un struct arbitrario desde un textbox editado a mano es frágil y easy de dejar en
> un estado a medias. Para forzar un valor concreto, la vía segura es la §10.2 de abajo: editar
> el struct **en memoria** con las mismas herramientas de §4 (`dbg_slider`, `dbg_checkbox`… sobre
> `obj_jugador`) y dejar que `save_game()` lo persista con el checksum recalculado solo.
>
> 💡 `dbg_view(..., false)` lo crea **oculto**: ábrelo desde el menú *Debug* del propio overlay
> cuando lo necesites, no en cada partida.

### 10.2 Editar un save a mano para forzar un escenario de prueba

El fichero es JSON en texto plano — `game_save_id + "save_slot1.json"` (rutas por plataforma en
§1 de [`01 · 14`](./14%20-%20Persistencia%20y%20archivos.md#dónde-está-el-save-area-en-cada-plataforma))
— así que en principio basta abrirlo con cualquier editor de texto, cambiar un valor y guardar.
En la práctica hay un matiz desde que existe el checksum de
[`01 · 14 §12 bis`](./14%20-%20Persistencia%20y%20archivos.md#12-bis-checksum-como-verificación-real-calcular-guardar-aparte-comparar-y-rechazar):

- El campo `"datos"` del fichero es el **JSON de tus datos ya escapado** dentro del JSON
  exterior (comillas como `\"`), no un objeto anidado legible a simple vista. Sigue siendo
  editable a mano — busca la clave que te interese entre las comillas escapadas, por ejemplo
  cambia `\"vida\":100` por `\"vida\":1` — pero es más incómodo que un JSON plano.
- Si lo editas así, el `checksum` que va al lado **ya no coincide**, y `load_game()` lo
  rechazará. La forma honesta de forzar el escenario sin pelearte con el hash: **borra por
  completo la clave `"checksum"`** del sobre exterior. Sin esa clave, la verificación se salta
  igual que con un guardado de antes de que existiera — es el mismo camino de compatibilidad que
  usan los saves viejos, y no rompe nada más.
- La alternativa más cómoda, casi siempre mejor: usa el inspector de §10.1 para ver el valor
  actual, cambia el dato **en memoria** (con una `dbg_slider`/`dbg_checkbox` como en §4, o
  directamente en el Debugger) y llama a `save_game()` de nuevo. El checksum sale recalculado
  solo y el fichero queda íntegro.

### 10.3 Pedirle a un jugador el fichero que hace falta, sin que te mande datos personales

Cuando el reporte llega de fuera (Discord, un ticket, una reseña), pedir "mándame tu carpeta de
guardado entera" es pedir de más: esa carpeta puede tener saves de otros slots, capturas de
pantalla (§4·10.6 de otros documentos) y, en Windows, la propia **ruta ya contiene el nombre de
usuario del sistema** (`C:\Users\<Usuario>\AppData\Local\...`, tabla completa en
[`01 · 14 §1`](./14%20-%20Persistencia%20y%20archivos.md#dónde-está-el-save-area-en-cada-plataforma)).
Ninguna de las dos cosas hace falta para depurar un guardado roto.

**Lo que sí hace falta, y nada más:**

1. **El fichero de guardado concreto del slot afectado** (`save_slot1.json`, no la carpeta
   entera) — es JSON con tus propios campos de partida; si tu juego no mete en el save nada de
   identidad real (nombre del sistema, email, ubicación — la misma regla de "no PII" de
   [`13 · 11 §7`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/11%20-%20Producción,%20alcance%20y%20lanzamiento.md#7--post-lanzamiento)
   punto 2), el fichero no trae nada personal que proteger.
2. **`partida.log`**, si tienes el registro con niveles de
   [`13 · 10 §7.2`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/10%20-%20Testing%20y%20QA.md#72-un-log-con-niveles-que-sobrevive-al-cierre)
   conectado (`scr_save_load.gml` ya lo hace si defines `global.save_logger`, ver su cabecera):
   trae la secuencia de qué falló y cuándo, sin que el jugador tenga que describirlo de memoria.

**Cómo pedirlo sin que tenga que navegar rutas de sistema**: dale un botón, no una ruta.

```gml
// ═══ obj_menu_opciones · botón "Copiar informe de guardado" ═══
function generar_informe_soporte(_slot)
{
    var _sobre = load_game_raw(_slot);   // ya sin checksum, ya migrado

    var _informe = {
        slot          : _slot,
        gm_version    : GM_version,
        plataforma    : os_type,
        guardado      : is_struct(_sobre) ? _sobre.datos  : "(no se pudo cargar)",
        version_save  : is_struct(_sobre) ? _sobre.version : -1
    };

    clipboard_set_text(json_stringify(_informe, true));
}
```

El jugador pega el resultado en el ticket/Discord con un solo "copiar y pegar" — sin abrir un
explorador de archivos, sin que la ruta con su nombre de usuario aparezca en ningún sitio, y sin
mandar la carpeta entera. `GM_version` (`08 · 19`) y `os_type` dan el contexto técnico que de
verdad hace falta para reproducir el bug, no una identidad.

> ⚠️ **Pide esto solo cuando el jugador está reportando un problema, nunca lo envíes tú solo
> desde el juego.** Automatizar este envío sin que el jugador lo pida convertiría un dato de
> depuración puntual en telemetría no consentida — la misma línea que traza
> [`13 · 11 §7`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/11%20-%20Producción,%20alcance%20y%20lanzamiento.md#7--post-lanzamiento)
> punto 1 ("pregunta antes de enviar nada").

---

## 11. Herramientas externas de perfilado

Todo lo anterior en este documento (Debugger, Profiler, Debug Overlay) ocurre **dentro** de
GameMaker. Hay una pregunta distinta que ningún documento de esta biblioteca respondía hasta
ahora: ¿qué se puede ver **desde fuera**, con las herramientas de la plataforma — RenderDoc,
Instruments, Android Profiler — cuando el Profiler del §3 no basta porque el problema está en
la GPU misma, en el sistema operativo, o hace falta un frame-by-frame de verdad?

**Respuesta corta y honesta primero:** las tres funcionan, con matices y ninguna está integrada
oficialmente por YoYo Games. Ninguna de las tres «habla GML» — todas ven el proceso nativo que
GameMaker produce (ejecutable Windows, app Xcode, APK/AAB), nunca tu código fuente `.gml`. Sirven
para confirmar o descartar un sospechoso que ya localizaste con el Debug Overlay/Profiler, no
para sustituirlos como primera parada — sigue siendo el §1 "mide antes de optimizar".

### 11.1 RenderDoc (captura de frame en Windows)

**Qué API gráfica hay detrás importa antes que nada.** GameMaker no lo publica como un dato
suelto en ningún sitio, pero el propio runtime lo revela a través de
[`os_get_info()`](../08%20-%20Referencia%20GML%20completa/19%20-%20Sistema%2C%20compilador%20y%20entorno.md#os_get_info--información-detallada-del-sistema):
en **Windows Desktop y UWP** el mapa devuelto trae claves `video_d3d11_device`,
`video_d3d11_context` y `video_d3d11_swapchain`. **GameMaker exporta Windows sobre Direct3D 11**,
no OpenGL (Xbox Series X/S usa D3D12, pero eso no es un target que compiles ni pruebes en un PC
de escritorio).

RenderDoc soporta oficialmente D3D11 (hasta 11.4), D3D12, Vulkan y OpenGL/OpenGL ES — Windows,
Linux y Android «out of the box» — según su propia FAQ. Eso pone a un build de Windows dentro de
lo que RenderDoc sabe capturar sin trucos. En la práctica hay un obstáculo conocido y ya
resuelto por la comunidad, no por YoYo Games: **los builds de desarrollo de GMS2 se ejecutan
desde puntos de montaje temporales**, lo que hace que «File → Launch Application» apuntando al
ejecutable que lanza el IDE no encuentre nada estable que capturar. La herramienta
[`renderdoc-gms2-kit`](https://github.com/odditica/renderdoc-gms2-kit) (script de PowerShell,
código abierto) resuelve justo eso: localiza el build temporal más reciente y genera un archivo
de ajustes `.cap` con rutas absolutas que RenderDoc sí puede cargar («Launch Application → Load
Settings»); funciona con builds VM y YYC.

**La vía más simple, y la que recomienda esta biblioteca:** no captures el build temporal del
IDE. Exporta el juego a una carpeta real (`gm-cli package` o *Build → Create Executable* en el
IDE) y apunta RenderDoc directamente al `.exe` exportado con «File → Launch Application». Sin
puntos de montaje temporales de por medio, no hace falta ningún script externo.

```
RenderDoc → File → Launch Application
  Executable Path: C:\ruta\a\tu_build_exportado\tu_juego.exe
  Working Directory: (la misma carpeta)
  → Launch
```

Con el juego capturado bajo RenderDoc puedes inspeccionar, frame a frame: cada *draw call*, sus
texturas de entrada, el estado de blend/depth/stencil, el pipeline completo y el contenido de
cada render target — exactamente el nivel de detalle que ni el Debug Overlay ni el Profiler dan,
porque ambos miden **tiempo**, no **estado de la GPU**.

> ⚠️ **RenderDoc no tiene versión de macOS.** Su propia documentación lista Windows, Linux,
> Android y Nintendo Switch (bajo NDA) como plataformas soportadas; el soporte de macOS es
> "pretty early [...] not usable for debugging yet and is not officially supported" según los
> propios mantenedores. Esto significa que **el export de macOS no se puede capturar con
> RenderDoc en absoluto** — ni siquiera intentándolo desde otra máquina, porque RenderDoc como
> aplicación host no corre ahí. Si necesitas depurar gráficos en macOS, la única vía de esta
> biblioteca es Instruments (§11.2).
>
> ⚠️ **Linux/Ubuntu** exporta sobre OpenGL (mismo `os_get_info()`, sección macOS/Ubuntu, que
> reporta `gl_vendor_string`/`gl_renderer_string`). RenderDoc soporta OpenGL 3.2+ en Linux, así
> que en teoría un build de Ubuntu debería poder capturarse en una máquina Linux — pero esta
> biblioteca no ha podido verificarlo en vivo (no hay una máquina Linux disponible en esta
> sesión) y no hay ningún reporte de la comunidad de GameMaker específico para Linux + RenderDoc,
> a diferencia del kit de Windows. Trátalo como plausible, no confirmado.
>
> ⚠️ **Android** usa OpenGL ES (`GL_VERSION`/`GL_RENDERER` en `os_get_info()`), y RenderDoc sí
> tiene un flujo de captura para Android (GLES y Vulkan) con `adb` de por medio. No hay ningún
> reporte encontrado de alguien haciéndolo específicamente con un APK de GameMaker: el
> procedimiento genérico de RenderDoc para Android debería aplicar igual que a cualquier app,
> pero márcalo como sin verificar para este motor en concreto.

### 11.2 Instruments (macOS e iOS)

Esto no hace falta inventarlo: **al compilar para macOS o iOS, GameMaker invoca a Xcode para
construir la app** — ya documentado en
[`05 · 05 §6.1`](../05%20-%20Referencia/05%20-%20Entregar%20el%20juego%20-%20firmar%2C%20notarizar%20y%20subir%20a%20las%20tiendas.md#61-del-xarchive-de-gamemaker-a-xcode)
para la firma y notarización — no se repite aquí. Lo relevante para perfilado es la
consecuencia directa: el resultado **es un proyecto/app de Xcode como cualquier otro**, así que
se perfila exactamente igual — sin ningún paso especial de GameMaker:

```
Xcode → abre el .xcodeproj que GameMaker generó (o el .app ya compilado)
  → Product → Profile  (⌘I)
  → elige la plantilla: Time Profiler, Allocations, Leaks, Energy Log...
```

También funciona por línea de comandos, útil para automatizar una captura sin abrir Xcode:

```sh
xcrun xctrace record --template 'Time Profiler' --time-limit 30s \
  --output /tmp/juego.trace --launch -- /ruta/a/tu_juego.app
```

**Lo que SÍ da Instruments, sin matices:** CPU total y por hilo, uso de memoria nativa
(Allocations/Leaks — útil para fugas de recursos que el GC de GML nunca ve, §8 de este
documento), energía/batería en iOS, y actividad de disco/red del proceso. Todo esto es
información a nivel de **proceso del sistema operativo**, así que es tan válida para un build de
GameMaker como para cualquier app nativa — no depende de que Instruments entienda GML.

> ⚠️ **La limitación real: el código GML no aparece en el stack como tal.** GameMaker no expone
> tu `.gml` a Xcode de ningún modo — no hay un mapa de "esta línea GML = esta línea del stack".
> Lo que Instruments SÍ ve depende de cómo se ejecuta tu juego:
>
> - **VM (intérprete):** tu GML nunca se compila a código nativo. El stack de Time Profiler
>   muestra el bucle del intérprete del runtime de GameMaker (funciones C++ internas,
>   repetidas miles de veces), no tus funciones. Sirve para saber "el intérprete está ocupado",
>   no en qué evento.
> - **YYC (nativo):** aquí sí hay algo más útil, porque el **YYC traduce tu GML a C++ y lo
>   compila** ([`01 · 01 §6`](./01%20-%20El%20IDE%20y%20el%20flujo%20de%20trabajo.md#6-ejecutar-y-compilar-vm-vs-yyc)) —
>   esto genera un `.cpp` real por cada evento (confirmado mirando el árbol de un proyecto YYC
>   exportado: aparece un archivo por evento, con nombres como
>   `gml_Object_obj_bench_Create_0.gml.cpp`). El símbolo que ves en el stack de Instruments es
>   ese nombre generado — reconocible (dice de qué objeto y qué evento viene), pero **no es tu
>   código línea a línea**: no puedes poner un breakpoint fuente en tu `.gml` desde Xcode, solo
>   saber qué evento consume el tiempo. Combínalo con el nombre para localizar el objeto y
>   contrasta con el Profiler del §3 (que sí ve línea a línea, pero solo mide, no perfila la GPU
>   ni memoria nativa) para bajar al detalle exacto.
>
> ⚠️ **GPU-específico (Metal System Trace, GPU Frame Capture) no está verificado para este
> motor.** El manual de GameMaker no confirma en ningún sitio si el runtime de iOS/tvOS emite
> llamadas Metal nativas o pasa por una capa de compatibilidad OpenGL ES — la única referencia
> primaria encontrada (`os_get_info()`, sección iOS/tvOS) solo menciona "claves adicionales que
> contienen información gráfica de OpenGL", sin aclarar el backend real de 2026. No se afirma
> aquí si los instrumentos de GPU de Xcode (pensados para Metal) muestran algo útil sobre un
> build de GameMaker: pruébalo tú mismo si lo necesitas, y no asumas ninguna de las dos cosas.

### 11.3 Android Profiler / `adb` (Android)

Igual que en macOS/iOS: no hay una integración especial de GameMaker con Android Studio. Lo que
hay es la vía oficial de GameMaker para **conectar y depurar el dispositivo**, documentada en su
propia ayuda oficial
(<https://gamemaker.io/en/help/articles/android-troubleshooting>, consultada el 2026-09-07 —
`gamemaker.io` sigue devolviendo 403 a peticiones sin cabecera `User-Agent`, igual que ya
documentaba `00-auditoria-externa-inicial.md`; con `curl -A "Mozilla/5.0..."` responde 200):
configurar `adb` en el PATH, comprobar el dispositivo con `adb devices` y ver el log en vivo con
`adb logcat`. Eso es *debugging* básico (conexión, mensajes de error), no *profiling*.

Para perfilar de verdad (CPU, memoria, batería, red por proceso) se usa el **Android Profiler**
de Android Studio — herramienta 100% de Google, no de GameMaker, y por eso funciona exactamente
igual con un APK/AAB exportado desde GameMaker que con cualquier otro:

```
Android Studio → Profile → selecciona el proceso del juego en el dispositivo conectado
  (compatible con Android 5.0 / API 21 en adelante, según la documentación oficial de Android)
```

Alternativa sin abrir Android Studio, directamente desde `adb`:

```sh
adb devices                              # confirma que el dispositivo aparece
adb shell dumpsys meminfo <package_name> # foto de memoria del proceso
adb shell top -m 10                      # CPU en vivo, los 10 procesos que más consumen
adb logcat | grep -i "tu_juego\|fatal"   # log filtrado, útil para crashes nativos
```

**Qué se ve y qué no:** igual que Instruments, esto es perfilado **a nivel de proceso del
sistema operativo** — memoria total, CPU, batería, tráfico de red — no perfilado de GML línea a
línea. GameMaker exporta Android sobre OpenGL ES (`os_get_info()`, sección Android:
`GL_VERSION`/`GL_RENDERER`/`GL_VENDOR`), así que si además necesitas ver *draw calls* concretos,
la ruta es RenderDoc para Android (§11.1, sin verificar para este motor) o el propio Debug
Overlay del §4 conectado al dispositivo — no el Android Profiler, que no distingue *draw calls*
individuales.

> ⚠️ No se ha encontrado ningún reporte de la comunidad de GameMaker usando el Android Profiler
> con un build propio — el procedimiento de arriba es el genérico de Android (válido para
> cualquier APK) aplicado a este caso, no una receta verificada específicamente con GameMaker.

### 11.4 Cuándo compensa salir de GameMaker

| Síntoma | Empieza en… | Sal a herramienta externa si… |
|---|---|---|
| FPS bajo, no sabes si es CPU o GPU | Debug Overlay §4 (Stacked) | El overlay ya dice "Draw" y necesitas saber **qué** *draw call* concreto pesa — RenderDoc |
| Un evento/script concreto es lento | Profiler §3 | Ya sabes la línea y necesitas contexto de sistema (memoria nativa, energía) — Instruments/Android Profiler |
| El juego se cierra solo en móvil | `adb logcat` / Instruments Crash Reporter | El log de GameMaker no explica nada: es un crash nativo del runtime, no una excepción GML capturable |
| Sospechas de una fuga de memoria nativa (no del GC de GML) | §8 de este documento (checklist) | El `gc_get_stats()` no cuadra con lo que reporta el sistema operativo — Allocations/Leaks (Instruments) o `dumpsys meminfo` (Android) |
| Quieres inspeccionar texturas/estado de la GPU frame a frame | — no hay equivalente dentro de GameMaker — | Directamente RenderDoc (Windows) |

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
13. **Un `dbg_view` con `dbg_text()` es un inspector de guardado gratis.** Pide al jugador solo el fichero del slot y el log, nunca la carpeta entera — la ruta de Windows ya lleva su nombre de usuario.
14. **Fuera de GameMaker: RenderDoc (Windows, D3D11) para frame GPU, Instruments (macOS/iOS, vía el proyecto Xcode que ya genera GameMaker) y Android Profiler/`adb` (Android) para CPU/memoria/energía a nivel de proceso.** Ninguna «habla GML»: úsalas después del Profiler del §3, no en vez de él. ⚠️ RenderDoc no tiene versión de macOS.
