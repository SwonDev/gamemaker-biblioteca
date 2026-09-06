# 43 · Cámaras y resolución III — avanzado (objetivos dinámicos, sacudida, zoom, pantalla completa)

> **Serie:** GameMaker — Cameras & Resolution 2026 (PixelatedPope)
> **Vídeo:** 3 de 4 · Nivel **avanzado**

| | |
|---|---|
| **Canal** | PixelatedPope |
| **URL** | <https://www.youtube.com/watch?v=a0RJyz9Cr6s> |
| **Duración** | 23 min 37 s |
| **Publicado** | 27 de diciembre de 2025 |
| **Nivel** | Avanzado |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | macros, métodos, structs, constructores, `instance_exists`, `is_struct`, `camera_set_view_target`, `camera_get_view_*`, `window_set_fullscreen`, `window_set_size`, `window_center`, `surface_resize`, `mod`, `max`, `clamp` |

## Índice de contenido

1. Qué significa «avanzado» en este vídeo
2. Una advertencia honesta sobre el estilo
3. Limpieza previa: el script de macros de view
4. Llevar `base_width` y `base_height` a las macros
5. Que la cámara no tenga que recorrer la room al empezar: `snap_to_target`
6. Objetivos dinámicos: seguir algo que no sea el jugador
7. Un objetivo puede ser un struct: no hace falta una instancia
8. `target_is_valid`: la comprobación que se usa en dos sitios
9. Probarlo: la barra espaciadora enfoca un punto aleatorio
10. Organización: dividir el Create en métodos con nombre descriptivo
11. Scripts `__obj_camera_window` y `__obj_camera_view`
12. Sacudida de pantalla: la clase `Shake`
13. Los cuatro argumentos de `shake.start()`
14. Dónde aplicar la sacudida (y su efecto secundario)
15. Zoom: el struct con seis propiedades y tres funciones
16. El truco del zoom: conservar el punto central
17. La distorsión de píxel al hacer zoom
18. Cuando la room es más pequeña que el view
19. Pantalla completa con F4 y por qué hay que desactivar Alt + Enter
20. Redimensionar la superficie de aplicación al cambiar de modo
21. El error del escalado máximo en pantalla completa
22. Ciclar el tamaño de ventana con F3

---

## 1. Qué significa «avanzado» en este vídeo

El autor lo aclara desde el primer segundo:

> «Puede que hayas notado que el título y/o la miniatura sugieren que este es el vídeo
> *avanzado*. ¿Pero qué quiero decir con eso? **Sobre todo significa que voy a ir muy
> rápido.**»

Concretamente:

- No va a explicar cada línea ni cada función.
- No va a ejecutar el juego sabiendo que no funciona… **bueno, puede que un par de veces**.
- Para aprovecharlo deberías manejarte con **macros, funciones, métodos, structs y
  constructores**.

> «O, como mínimo, estar dispuesto a **pausar el vídeo e ir a investigar** cuando haga algo
> que no entiendas.```

---

## 2. Una advertencia honesta sobre el estilo

Una de las reflexiones más valiosas de toda la serie:

> «Voy a hacer varias cosas **específicamente a mi manera**. Igual que los artistas, los
> programadores a menudo tienen un estilo propio, y ese estilo **puede cambiar con los
> años**. Que esto sea como lo hago yo ahora no significa que lo haga exactamente así
> dentro de unos años. Y **cuanto más viejo sea este vídeo, más probable es que odie** la
> forma en que hago las cosas aquí.»

Y la conclusión, que es el verdadero objetivo del capítulo:

> «Idealmente, has llegado a este vídeo no para copiar y pegar todo lo que hago tal cual
> lo hago —que también vale, supongo— sino para **aprender algunos conceptos** y estar
> dispuesto a implementarlos de una forma con la que **tú** estés cómodo.»

> «Ser un usuario avanzado de GameMaker es ser capaz de **entender conceptos y procesos
> generales** y luego aplicarlos para que encajen con tus necesidades.**

---

## 3. Limpieza previa: el script de macros de view

Antes de añadir funciones, toca limpiar.

> «Si lo estuviera programando de verdad para mí en mi propio proyecto, no lo habría
> programado así, específicamente porque **habría traído mi script de macros de view antes
> de escribir una sola línea de código**.»

El script está en su repositorio *helpful scripts* de GitHub. Es, básicamente:

> «Un montón de atajos a las funciones comunes de view y cámara. Usar estas macros en
> lugar de las funciones hace que mi código sea **mucho más fácil de leer** y de trabajar.»

Ejemplo del tipo de macros que define:

```gml
// ══════════════════════════════════════════════════════════════
// Macros de view — atajos para las funciones más usadas
// ══════════════════════════════════════════════════════════════
#macro VIEW             view_camera[0]          // la cámara del viewport 0
#macro VIEW_WIDTH       camera_get_view_width(VIEW)
#macro VIEW_HEIGHT      camera_get_view_height(VIEW)
#macro VIEW_X           camera_get_view_x(VIEW)
#macro VIEW_Y           camera_get_view_y(VIEW)
#macro VIEW_SET_SIZE    camera_set_view_size(VIEW,
#macro VIEW_SET_POS     camera_set_view_pos(VIEW,
```

> **Nota:** la sintaxis exacta de las macros del autor depende de su repositorio; el
> objetivo es ilustrar la idea, no reproducir el archivo línea por línea. Si las usas,
> **descarga el script original** y léelo antes.

---

## 4. Llevar `base_width` y `base_height` a las macros

El autor mueve los dos valores de resolución base al archivo de macros y hace un
**buscar y reemplazar** en el proyecto.

```gml
// En el script de macros
#macro BASE_WIDTH   320
#macro BASE_HEIGHT  180
```

De este modo, `obj_camera` deja de declarar variables locales para algo que es
**configuración global del juego**.

---

## 5. Que la cámara no tenga que recorrer la room al empezar: `snap_to_target`

Primer problema real del sistema del capítulo anterior:

> «Lo primero que me molesta es que **la cámara tiene que recorrer toda la room hasta el
> jugador justo al empezar**. Así que, a menos que el jugador empiece todas las rooms en la
> esquina superior izquierda, **esto no sirve**.»

La solución es un método que coloque la cámara ya centrada en su objetivo:

```gml
// Método de obj_camera
/// @desc Coloca la cámara instantáneamente sobre su objetivo, sin suavizado.
function snap_to_target()
{
    if (!target_is_valid()) exit;

    var _target_x = current_target.x - (camera_get_view_width(view_camera[0])  / 2);
    var _target_y = current_target.y - (camera_get_view_height(view_camera[0]) / 2);

    _target_x = clamp(_target_x, 0, max(0, room_width  - camera_get_view_width(view_camera[0])));
    _target_y = clamp(_target_y, 0, max(0, room_height - camera_get_view_height(view_camera[0])));

    camera_set_view_pos(view_camera[0], _target_x, _target_y);
}
```

Se llama en el **Room Start**, justo después de inicializar el view.

> «Perfecto. Mejoraremos esto un poco cuando soportemos objetivos dinámicos, que haremos a
> continuación.```

---

## 6. Objetivos dinámicos: seguir algo que no sea el jugador

> «No necesariamente quieres que tu cámara siga siempre a `obj_player`. Puede que quieras
> seguir **otros objetos**, o puede que incluso quieras mirar **una posición concreta de
> la room**.```

Para eso se añade una variable y un método:

```gml
// Create event de obj_camera
current_target = obj_player;

/// @desc Cambia el objetivo que sigue la cámara.
/// @param {Id.Instance|Struct} _target Instancia o struct con x e y.
function set_target(_target)
{
    current_target = _target;
}
```

---

## 7. Un objetivo puede ser un struct: no hace falta una instancia

Aquí está la parte interesante:

> «Lo divertido es que el objetivo **no necesita ser una instancia**. Podemos soportar
> igual de fácil que se le pase **un struct que tenga propiedades `x` e `y`**.»

Eso abre la puerta a enfocar un punto arbitrario de la room sin crear ningún objeto:

```gml
// Enfocar un punto concreto de la room, sin instancia de por medio.
set_target({ x: 1000, y: 400 });
```

---

## 8. `target_is_valid`: la comprobación que se usa en dos sitios

Como la validación hace falta tanto en `snap_to_target` como en el End Step, se extrae a
un método:

```gml
/// @desc Comprueba que el objetivo actual se puede usar.
function target_is_valid()
{
    // Si no es un struct, tiene que ser una instancia existente.
    if (!is_struct(current_target))
    {
        return instance_exists(current_target);
    }

    // Si es un struct, damos por hecho que es válido.
    return true;
}
```

Y sustituimos **todas** las referencias a `obj_player` por `current_target`.

---

## 9. Probarlo: la barra espaciadora enfoca un punto aleatorio

La prueba que monta el autor en el objeto jugador:

```gml
// Step event de obj_player
if (keyboard_check_pressed(vk_space))
{
    // Enfocamos un punto aleatorio de la room.
    obj_camera.set_target({
        x: random(room_width),
        y: random(room_height)
    });
}

if (keyboard_check_released(vk_space))
{
    // Volvemos a enfocar al jugador, y de paso encuadramos de golpe.
    obj_camera.set_target(id);
    obj_camera.snap_to_target();
}
```

El resultado: al pulsar espacio, la cámara enfoca un punto aleatorio; al soltarlo,
**vuelve al jugador de forma instantánea**.

> «Esto es algo bastante común que ocurre en los juegos, como cuando **accionas un
> interruptor que abre una puerta**.```

---

## 10. Organización: dividir el Create en métodos con nombre descriptivo

> «El Create de nuestra cámara se está desmadrando y solo va a ir a peor. Así que creo
> que es hora de hacer un poco de limpieza.»

El proceso que propone es sistemático:

> «Voy a aplicar esta misma lógica a **cada evento**. Me preguntaré: *¿qué está haciendo
> este bloque de código?* Y entonces escribiré un método **con un nombre que describa esa
> acción**, cortaré y pegaré el código dentro del método, y llamaré al método en el
> evento.»

El resultado, en sus palabras:

> «Puede que esto parezca excesivo, pero hay algo muy reconfortante en poder ir a mi evento
> Room Start y leer **en español** lo que está pasando: estoy inicializando el view y
> luego me ajusto al objetivo. Puedo ver tan claramente qué está haciendo este objeto en
> cada evento, y eso se siente bien.»

---

## 11. Scripts `__obj_camera_window` y `__obj_camera_view`

El autor crea **dos assets de script** separados:

- `__obj_camera_window` → métodos relacionados con la ventana.
- `__obj_camera_view` → métodos relacionados con el view.

Los nombra con **doble guion bajo más el nombre del objeto** por dos razones: mantener
organizado el árbol de recursos y **evitar llamarlos por error desde otros objetos**.

```gml
// Script: __obj_camera_window
function __obj_camera_window()
{
    calculate_max_window_scale = function(_fullscreen = false) { /* … */ };
    init_window                = function() { /* … */ };
    set_window_size            = function(_scale) { /* … */ };
}

// Script: __obj_camera_view
function __obj_camera_view()
{
    init_view       = function() { /* … */ };
    snap_to_target  = function() { /* … */ };
    target_is_valid = function() { /* … */ };
    set_target      = function(_target) { current_target = _target; };
}
```

Y se llaman **una sola vez**, al principio del Create:

```gml
// Create event de obj_camera
__obj_camera_window();
__obj_camera_view();
```

Un efecto secundario que le gusta especialmente:

> «Si pulso **Ctrl + T** y escribo *obj_camera*, se crea una **especie de estructura de
> árbol** en la lista. Es bastante chulo, sobre todo en objetos más complicados que tienen
> un montón de estos scripts.»

---

## 12. Sacudida de pantalla: la clase `Shake`

> «Para esto vamos a usar **mi clase `Shake`** que está en mi GitHub de *helpful scripts*.
> Es **mi método de referencia** para sacudir la cámara. Creo que es **simple de
> implementar, fácil de controlar, y queda muy bien**.»

La clase `Shake` tiene:

| Miembro | Tipo | Qué hace |
|---|---|---|
| `start()` | función | Inicia la sacudida |
| `update()` | función | Avanza la sacudida cada step |
| `offset_x` | propiedad | Desplazamiento horizontal actual |
| `offset_y` | propiedad | Desplazamiento vertical actual |

Tiene dos dependencias: **`approach`** y **`sin_oscillate`**, que también hay que
importar.

```gml
// Create event de obj_camera
shake = new Shake();

// Step event de obj_camera
shake.update();
```

---

## 13. Los cuatro argumentos de `shake.start()`

```gml
// Ejemplo: sacudida hacia abajo al aterrizar
shake.start(270,   // dirección del temblor, en grados
            10,    // amplitud, en píxeles
            0.25,  // caída: cuánto se reduce la amplitud cada step
            0.1);  // frecuencia, en segundos
```

1. **Dirección.** El ángulo al que tiembla la pantalla.

   > «Empezaremos con **abajo, 270**. Esto sería genial para algo como un **golpe contra el
   > suelo** o una roca que cae.»

2. **Amplitud.** Tamaño de la sacudida en píxeles.

   > «Cuanto más grande sea el número, **más extrema** es la sacudida.»

3. **Caída** (*falloff*). Cuánto se reduce la amplitud cada step.

   > «0,25 significa que **perderemos un píxel completo de amplitud cada cuatro frames**.
   > Eso significa que tardará **40 frames**, poco más de medio segundo, en desaparecer.»

4. **Frecuencia.** Cómo de rápido o violento es el temblor.

   > «Es un poco raro, porque **se basa en segundos reales y no en steps**. Si lo pones a
   > 1, tardará un segundo completo en hacer una sacudida entera: de arriba abajo y otra vez
   > arriba. **El valor por defecto son 0,1 segundos.**»

---

## 14. Dónde aplicar la sacudida (y su efecto secundario)

La regla es importante:

> «Siempre queremos aplicar la sacudida **después** de que la cámara se haya posicionado.
> Así que el mejor sitio es en `camera_set_view_pos` **antes** de fijar la posición del
> view: simplemente sumamos la X y la Y de la sacudida a nuestro objetivo.»

```gml
// Dentro del método que fija la posición del view
camera_set_view_pos(view_camera[0],
                    _final_x + shake.offset_x,
                    _final_y + shake.offset_y);
```

> **Efecto secundario:** como aplicamos la sacudida **después** del `clamp` que encierra la
> cámara en la room, **la sacudida puede mostrar la zona de fuera de la room**.

Si te molesta, la solución es añadir un **margen** al `clamp` para que no encaje justo al
borde, sino que deje unos píxeles para poder temblar.

> «En la mayoría de los casos **no va a ser un gran problema**.»

---

## 15. Zoom: el struct con seis propiedades y tres funciones

> «El zoom es bastante inusual en juegos de pixel art, pero ocurre, y es **súper común** en
> juegos HD y dibujados a mano.»

### Por qué no usar un único valor de zoom

La forma obvia es guardar un valor de zoom y redimensionar el view dividiendo el tamaño
base por ese nivel. El autor la descarta:

> «Pero esto hace que sea **difícil saltar a una anchura o altura concreta** para tu zoom.
> Por ejemplo, si quisieras alejarte para mostrar **el ancho entero de la room actual**,
> tendrías que hacer cálculos para averiguar entre qué dividir tu anchura base para
> obtener la anchura de la room. Se puede, claro, pero es más engorroso.»

En su lugar, el sistema guarda **una anchura objetivo**: se aumenta para alejar y se reduce
para acercar.

```gml
// Create event de obj_camera
zoom = {
    width:     BASE_WIDTH,    // anchura objetivo actual del view
    height:    BASE_HEIGHT,   // altura objetivo, derivada de la relación de aspecto
    speed:     0.2,           // velocidad de interpolación hacia el objetivo
    inc:       32,            // cuánto cambia el zoom con cada paso de rueda
    min_width: 160,           // zoom máximo hacia dentro
    max_width: 1280,          // zoom máximo hacia fuera
};
```

Y las funciones se meten **directamente en el struct**:

```gml
zoom.set = function(_width) { /* … */ };
zoom.change = function(_direction) { /* … */ };
zoom.apply = function() { /* … */ };
```

### `zoom.set()`

```gml
zoom.set = function(_width)
{
    // Fijamos la anchura objetivo y derivamos la altura a partir de
    // la relación de aspecto del juego.
    width  = clamp(_width, min_width, max_width);
    height = width / (BASE_WIDTH / BASE_HEIGHT);
};
```

> «Tengo macros de relación de aspecto para todos nuestros elementos de renderizado: base,
> view, app surface, gui… pero **siempre deberían ser todas iguales**, así que no importa
> mucho cuál usemos aquí.»

---

## 16. El truco del zoom: conservar el punto central

Aquí está **el detalle que hace tropezar a casi todo el mundo** la primera vez que
implementa un zoom:

> «Cuando haces zoom con una cámara en la vida real, esperamos que **lo que está en el
> centro de la cámara se quede en el centro**. Pero desafortunadamente, **no es así como
> funcionan las cámaras de GameMaker**.»

Cuando reduces el tamaño del view, **lo que estaba en el centro se desplaza hacia abajo y a
la derecha**. La solución es un proceso de tres pasos:

1. Capturar la posición de la room que es **el centro actual**.
2. Redimensionar el view.
3. Volver a colocar la cámara para que **el punto central no se mueva**.

```gml
zoom.apply = function()
{
    // ──────────────────────────────────────────────────────────
    // PASO 1 — Capturamos el punto central ANTES de redimensionar.
    // ──────────────────────────────────────────────────────────
    var _center_x = camera_get_view_x(view_camera[0])
                  + camera_get_view_width(view_camera[0])  / 2;
    var _center_y = camera_get_view_y(view_camera[0])
                  + camera_get_view_height(view_camera[0]) / 2;

    // ──────────────────────────────────────────────────────────
    // PASO 2 — Redimensionamos el view interpolando hacia el objetivo.
    // ──────────────────────────────────────────────────────────
    var _new_width  = lerp(camera_get_view_width(view_camera[0]),  width,  speed);
    var _new_height = lerp(camera_get_view_height(view_camera[0]), height, speed);

    camera_set_view_size(view_camera[0], _new_width, _new_height);

    // ──────────────────────────────────────────────────────────
    // PASO 3 — Devolvemos el centro a donde estaba.
    // ¡COMENTA ESTA LÍNEA PARA VER QUÉ PASA SIN ELLA!
    // ──────────────────────────────────────────────────────────
    camera_set_view_pos(view_camera[0],
                        _center_x - _new_width  / 2,
                        _center_y - _new_height / 2);
};
```

> «Prueba a **comentar esa última línea** y mira qué pasa. Es **súper importante** que
> hagamos esto.»

Las llamadas quedan repartidas entre dos eventos: `zoom.change()` en el **Step** y
`zoom.apply()` en el **End Step**.

---

## 17. La distorsión de píxel al hacer zoom

> «Según nos acercamos y alejamos, vigila la esquina superior izquierda, concretamente el
> **multiplicador del view 0**. Si tu juego es pixel art y ese valor **no es un número
> entero** en algún momento, **has introducido distorsión de píxel**.»

La recomendación es clara:

- **Pixel art:** no dejes el juego quieto mucho tiempo en un nivel de zoom con
  multiplicador decimal. Puede quedar bien según tu estilo, pero **la distorsión está ahí**
  y no hay mucho que puedas hacer fácilmente si se ve mal.
- **Arte HD o dibujado a mano:** debería verse bien a prácticamente cualquier nivel de zoom.

---

## 18. Cuando la room es más pequeña que el view

Al probar los límites de zoom aparece un fallo, y el autor hace una distinción importante:

> «Pero esto en realidad **no es un problema de nuestro código de zoom**. Es un problema de
> **nuestro código de clamp a la room**.»

El caso práctico no es tan raro como parece:

> «Lo que es **mucho** más probable es que metas al jugador en una room que resulta ser
> **más pequeña que el view**. Esto pasa constantemente en los RPG: entras en una cabaña
> que es una única room pequeña. La cámara no se mueve para seguir al jugador y hay **un
> borde negro alrededor de toda la zona**.»

La solución es ampliar el `clamp` para que, si el view es más grande que la room, **centre
el view en el centro de la room**:

```gml
// Después de obtener la posición ya limitada...
if (camera_get_view_width(view_camera[0]) > room_width)
{
    // El view es más ancho que la room: lo centramos horizontalmente.
    _final_x = (room_width - camera_get_view_width(view_camera[0])) / 2;
}

if (camera_get_view_height(view_camera[0]) > room_height)
{
    // Lo mismo en vertical.
    _final_y = (room_height - camera_get_view_height(view_camera[0])) / 2;
}
```

> «Hay un pequeño **tirón** al cruzar ese límite, porque nuestra cámara cambia aquello
> sobre lo que se está centrando. De nuevo, lo que estamos haciendo aquí es **súper
> inusual**.»

Y la advertencia final:

> «Si quieres permitir que la cámara se aleje hasta mostrar la room entera, probablemente
> **no deberías estar haciendo clamp a la room en absoluto**. Prueba a comentar el código
> de clamp por completo.»

---

## 19. Pantalla completa con F4 y por qué hay que desactivar Alt + Enter

Primero hay que quitarle al jugador el atajo del sistema operativo:

> «El primer paso es **desactivar la posibilidad de que el jugador use el atajo de teclado
> por defecto del sistema operativo** para cambiar entre pantalla completa y modo
> ventana: **Alt + Enter** en Windows. Lo desactivamos porque **queremos que el juego use
> nuestro código**.»

Esto se hace en los ajustes de la plataforma Windows, en las opciones de pantalla
completa, desmarcando el atajo de teclado del sistema.

Después, en el **Step** de `obj_camera`:

```gml
// Step event de obj_camera
if (keyboard_check_pressed(vk_f4))
{
    toggle_fullscreen();
}
```

---

## 20. Redimensionar la superficie de aplicación al cambiar de modo

> «¿Ya está, no? Hemos terminado. **No del todo.**»

Como el proyecto usa **subpíxeles**, al agrandar la ventana queremos **aprovechar esa
resolución extra**. Y al volver a modo ventana, queremos **reducir** el tamaño de la
superficie de aplicación para no renderizar a más resolución de la necesaria.

```gml
/// @desc Alterna entre pantalla completa y modo ventana.
function toggle_fullscreen()
{
    window_set_fullscreen(!window_get_fullscreen());

    // ──────────────────────────────────────────────────────────
    // Según estemos en pantalla completa o no, usamos la escala
    // máxima posible o la escala de ventana elegida.
    // ──────────────────────────────────────────────────────────
    var _scale = window_get_fullscreen()
               ? calculate_max_window_scale(true)   // pantalla completa
               : window_scale;                      // modo ventana

    surface_resize(application_surface,
                   BASE_WIDTH  * _scale,
                   BASE_HEIGHT * _scale);
}
```

---

## 21. El error del escalado máximo en pantalla completa

Al probarlo, la pantalla completa funciona… pero algo no cuadra:

> «Pero espera, mira nuestro **valor de escala del view** en la esquina superior izquierda
> cuando cambiamos entre pantalla completa y modo ventana. **No cambia. Se queda en 5x.**
> Y mira las dimensiones de nuestra **app surface**: 1600 × 900, pero la pantalla dice
> 1920 × 1080. ¿Qué pasa?»

El culpable es `calculate_max_window_scale`:

> «El problema está en nuestro `calculate_max_window_scale`. Se escribió para calcular la
> escala máxima de ventana **en modo ventana**, que, como he dicho ya muchas veces,
> **necesita tener en cuenta la barra de título** o Windows nos aplastará. **Pero en
> pantalla completa no necesitamos preocuparnos de eso.**»

La solución es **añadir un argumento** a la función:

```gml
/// @desc Calcula la escala máxima de ventana que cabe en el monitor.
/// @param {Bool} _fullscreen Si es true, no se descuenta la barra de título.
function calculate_max_window_scale(_fullscreen = false)
{
    var _max_height_scale = display_get_height() / BASE_HEIGHT;
    var _max_width_scale  = display_get_width()  / BASE_WIDTH;

    // Solo en modo ventana hay que dejar sitio a la barra de título.
    if (!_fullscreen && frac(_max_height_scale) == 0)
    {
        _max_height_scale -= 1;
    }

    return floor(min(_max_width_scale, _max_height_scale));
}
```

Y al usarlo desde `toggle_fullscreen()` se pasa `true`:

> «Ahora, al ejecutar, obtenemos el **6x de escala completo** y una superficie de
> aplicación de **tamaño 1080p completo**.»

---

## 22. Ciclar el tamaño de ventana con F3

> «Es realmente molesto **obligar al jugador a usar el tamaño máximo de ventana todo el
> tiempo**, pero permitirle redimensionar la ventana sin restricciones significa que
> puede dejarla con un tamaño que se vea mal.»

El punto intermedio habitual: **dejar que el jugador elija la escala**.

- Una escala de **1** es la resolución base del juego.
- El jugador puede elegir cualquier multiplicador soportado **hasta el máximo**.
- **Si tu juego es pixel art, las opciones deberían restringirse a números enteros.**

```gml
// Step event de obj_camera
if (keyboard_check_pressed(vk_f3))
{
    // En pantalla completa no tiene sentido cambiar el tamaño de ventana.
    if (window_get_fullscreen()) exit;

    // ──────────────────────────────────────────────────────────
    // Sumamos 1 y lo envolvemos con mod() contra (máximo + 1).
    // Al envolver, el valor podría quedarse en 0, así que nos
    // aseguramos de que como mínimo sea 1.
    // ──────────────────────────────────────────────────────────
    window_scale = (window_scale + 1) mod (max_window_scale + 1);
    window_scale = max(window_scale, 1);

    set_window_size(window_scale);
    window_center();

    // Igual que al pasar a pantalla completa, redimensionamos la superficie.
    surface_resize(application_surface,
                   BASE_WIDTH  * window_scale,
                   BASE_HEIGHT * window_scale);
}
```

> «Ahora podemos pulsar **F3** para ciclar por los distintos tamaños de ventana
> perfectamente escalados. Y en cualquier momento, pulsar **F4** para saltar a pantalla
> completa y **F4** otra vez para volver.»

---

## Puntos clave

1. «Avanzado» aquí significa **ritmo rápido** y uso de macros, métodos, structs y
   constructores.
2. El estilo del autor **es suyo**: aprende los conceptos, no copies la forma.
3. Las macros de view hacen el código de cámara **mucho más legible**.
4. `snap_to_target()` evita que la cámara recorra la room al entrar en un nivel.
5. El objetivo de la cámara **puede ser un struct con `x` e `y`**, no solo una instancia.
6. Extrae la validación del objetivo a un método si la usas en varios sitios.
7. Divide el Create en **métodos con nombres que describen la acción**: el evento se lee
   como una lista de intenciones.
8. Los scripts `__nombre_objeto_*` agrupan métodos y evitan llamadas accidentales.
9. `Shake` tiene `start()` y `update()`, y expone `offset_x` / `offset_y`.
10. `shake.start(dirección, amplitud, caída, frecuencia)`: la **frecuencia va en
    segundos**, no en steps.
11. La sacudida se aplica **después** del posicionado, por lo que **puede mostrar fuera de
    la room**.
12. Guarda una **anchura objetivo** para el zoom en lugar de un factor: así puedes saltar
    a un tamaño concreto.
13. Al hacer zoom hay que **capturar el centro, redimensionar y restaurar el centro**, o
    la imagen se desplazará.
14. En pixel art, el multiplicador del view debe ser **entero** o hay distorsión.
15. Si la room es más pequeña que el view, **centra el view en el centro de la room**.
16. Desactiva el **Alt + Enter** del sistema para controlar tú la pantalla completa.
17. Al cambiar de modo hay que **redimensionar la superficie de aplicación**.
18. `calculate_max_window_scale()` necesita un argumento: en **pantalla completa no hay
    barra de título** que descontar.
19. Para ciclar el tamaño de ventana usa `mod` contra `máximo + 1` y **fuerza un mínimo
    de 1**.

---

## Ejercicio propuesto

> **Objetivo:** añadir objetivos dinámicos, sacudida, zoom y control de pantalla completa
> al sistema del capítulo 42.

**Parte A — Limpieza**

1. Crea un script de macros con `BASE_WIDTH` y `BASE_HEIGHT`, y sustituye las variables del
   Create de `obj_camera`.
2. Añade macros de atajo para `camera_get_view_width`, `camera_get_view_height`,
   `camera_get_view_x`, `camera_get_view_y` y `camera_set_view_pos`. Reescribe el End Step
   usándolas y compara la legibilidad.

**Parte B — Objetivos dinámicos**

3. Añade `current_target` y el método `set_target()`. Sustituye todas las referencias a
   `obj_player` por `current_target`.
4. Escribe `target_is_valid()` con la lógica `is_struct()` / `instance_exists()`.
5. Añade `snap_to_target()` y llámalo en el Room Start. Comprueba que al entrar en un nivel
   **la cámara ya está encuadrada**.
6. Implementa la prueba de la barra espaciadora del apartado 9. Verifica que al soltarla la
   cámara **vuelve de golpe** al jugador.

**Parte C — Organización**

7. Crea los scripts `__obj_camera_window` y `__obj_camera_view`. Mueve los métodos y llama
   a ambos desde lo alto del Create.
8. Aplica el criterio del autor a cada evento: ¿qué hace este bloque? Escribe un método con
   ese nombre. Al terminar, **lee tus eventos en voz alta** y comprueba que se entienden
   sin mirar el código de dentro.

**Parte D — Sacudida**

9. Implementa (o importa) la clase `Shake` con sus dependencias `approach` y
   `sin_oscillate`. Crea la instancia en el Create y llama a `shake.update()` en el Step.
10. Aplica el desplazamiento **después** del posicionado. Dispara una sacudida
    `shake.start(270, 10, 0.25, 0.1)` al pulsar una tecla.
11. Comprueba el **efecto secundario**: muévete hasta el borde de la room y sacude.
    Describe qué ves fuera de la room. Después añade un margen al `clamp` y verifica la
    diferencia.
12. Calcula cuántos frames tarda en desaparecer una sacudida con amplitud 20 y caída 0,1.
    Compruébalo en el juego.

**Parte E — Zoom**

13. Crea el struct `zoom` con las seis propiedades y las funciones `set()`, `change()` y
    `apply()`. Llama a `change()` en el Step y a `apply()` en el End Step.
14. Implementa los tres pasos del apartado 16. **Comenta la última línea** de `apply()` y
    ejecuta: describe exactamente hacia dónde se desplaza la imagen al acercar.
15. Vigila el multiplicador del view de `display_write_all_specs`. Encuentra un nivel de
    zoom en el que **no** sea entero y explica qué distorsión introduces.
16. Crea una room **más pequeña que tu view** y entra en ella. Verifica el borde negro.
    Implementa el centrado del apartado 18 y comprueba el resultado.

**Parte F — Pantalla completa y tamaño de ventana**

17. Desactiva el atajo **Alt + Enter** en los ajustes de la plataforma Windows.
18. Implementa `toggle_fullscreen()` con F4, **primero sin** redimensionar la superficie de
    aplicación. Describe qué se ve mal y por qué.
19. Añade el redimensionado. Después, ejecuta **sin** pasar el argumento a
    `calculate_max_window_scale()` y comprueba que la superficie se queda en 1600 × 900 en
    lugar de 1920 × 1080.
20. Implementa el ciclado con F3. Comprueba el **fallo del 0**: qué ocurre si quitas el
    `max(window_scale, 1)`.

**Reto extra:** el autor explica por qué `Shake` es un **constructor** y `zoom` se queda
como **struct literal**: `Shake` es genérico (puedes sacudir una cámara, un objeto, un
botón de la interfaz), mientras que `zoom` solo sirve para una cámara y **solo puede haber
uno a la vez**. Piensa en otros dos sistemas de tu juego y decide cuál de los dos enfoques
encaja en cada caso, justificándolo con ese mismo criterio.
