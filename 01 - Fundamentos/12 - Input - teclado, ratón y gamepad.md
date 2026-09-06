# 12 · Input — teclado, ratón y gamepad

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/Game_Input.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/Keyboard_Input/Keyboard_Input.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/Mouse_Input/Mouse_Input.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/GamePad_Input/Gamepad_Input.htm>
> - <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Object_Events.htm>
> - Josh Sutphin, *Doing Thumbstick Dead Zones Right*, Third Helix, 12-04-2013 — consultada el
>   06-09-2026 vía una copia de 2014 en Wayback Machine (`web.archive.org/web/20141025070920/`);
>   el dominio original hoy redirige a contenido sin relación, así que cita siempre el archivo.

> ⚠️ **Corrección importante sobre la librería «Input»:** en la petición original se describía como «la librería oficial Input de YoYoGames en GitHub». **No es exacto.** Es una librería de la comunidad creada por **Juju Adams y Alynne Keith**, y desde 2025 **se ha movido de GitHub a Codeberg**. El personal de YoYo Games la recomienda públicamente en el bug tracker oficial. Detalles en la sección 7.

---

## 1. Dos niveles de input

GameMaker te da **dos formas** de capturar la entrada:

| Nivel | Cómo | Cuándo usarlo |
|---|---|---|
| **Eventos** | Keyboard / Mouse / Gesture events en el objeto | Prototipos, menús simples, cosas de un solo objeto |
| **Funciones** | `keyboard_check()`, `mouse_check_button()`, `gamepad_button_check()`… | Control real del jugador, múltiples dispositivos, input rebindeable |

> 💡 **Cuando necesites control real** (varios dispositivos, gamepad, rebindeo), usa **funciones en el Step**, no eventos.

### ⚠️ Cuándo los eventos NO se disparan

> **GameMaker NO ejecuta eventos de teclado ni ratón cuando el Debug Overlay está abierto y ha tomado el control del input.** Tampoco al *simular pulsaciones*.

Las **funciones** (`keyboard_check()`, `mouse_check_button()`…) **sí siguen funcionando**.

Para detectarlo:

```gml
if (!is_keyboard_used_debug_overlay() && keyboard_check(vk_up))
{
    // ejecutar solo si el overlay no está "usando" el teclado
}

if (!is_mouse_over_debug_overlay() && mouse_check_button(mb_left))
{
    // ...
}
```

También puedes forzar el código de un evento con `event_perform()`.

---

## 2. Teclado

### `ord()` y las constantes `vk_*`

Cada carácter se define por su **código UTF-8**. Se obtiene con `ord()`:

```gml
if (keyboard_check(ord("A")))
{
    hspeed = -5;
}
```

> ⚠️ **`ord()` con `keyboard_check*()` solo detecta `0-9` y `A-Z`** (en mayúsculas). El string debe tener **un solo carácter**.

Para todo lo demás (flechas, Shift, F1…), están las constantes `vk_*` (*virtual key*):

| Constante | Tecla | | Constante | Tecla |
|---|---|---|---|---|
| `vk_nokey` | ninguna | | `vk_insert` | Insert |
| `vk_anykey` | cualquiera | | `vk_delete` | Supr |
| `vk_left` / `vk_right` | ← / → | | `vk_pageup` / `vk_pagedown` | RePág / AvPág |
| `vk_up` / `vk_down` | ↑ / ↓ | | `vk_pause` | Pausa |
| `vk_enter` | Enter | | `vk_printscreen` | ImprPant ⚠️ |
| `vk_escape` | Esc | | `vk_f1` … `vk_f12` | F1–F12 |
| `vk_space` | Espacio | | `vk_numpad0` … `vk_numpad9` | teclado numérico |
| `vk_shift` / `vk_control` / `vk_alt` | cualquiera de los dos | | `vk_multiply` / `vk_divide` / `vk_add` / `vk_subtract` / `vk_decimal` | numérico |
| `vk_backspace` | Retroceso | | `vk_lshift` / `vk_rshift` | izq / der |
| `vk_tab` | Tabulador | | `vk_lcontrol` / `vk_rcontrol` | izq / der |
| `vk_home` / `vk_end` | Inicio / Fin | | `vk_lalt` / `vk_ralt` | izq / der |

> ⚠️ **`vk_printscreen` no se recomienda**: en Windows 11 suele estar ligado a la herramienta de recorte, y no se generarán eventos.

```gml
if (keyboard_check_pressed(vk_tab))
{
    instance_create_layer(x, y, "Controllers", obj_menu);
}
```

### Para caracteres fuera de 0-9 / A-Z

Usa las variables de estado del teclado:

```gml
if (keyboard_lastchar == "ç")
{
    show_debug_message("Se pulsó la ç");
    keyboard_lastchar = "";   // ← resetea para no repetir
}
```

### Funciones

```
io_clear()
keyboard_check(tecla)            // ¿está pulsada?
keyboard_check_pressed(tecla)    // ¿se acaba de pulsar?
keyboard_check_released(tecla)   // ¿se acaba de soltar?
keyboard_check_direct(tecla)     // física, ignora el mapeo
keyboard_clear(tecla)

keyboard_set_map(tecla_real, tecla_mapeada)   // remapear
keyboard_get_map(tecla)
keyboard_unset_map(tecla)

keyboard_set_numlock(activado) / keyboard_get_numlock()
```

### Variables de estado

| Variable | Qué contiene |
|---|---|
| `keyboard_key` | La última tecla pulsada (código) |
| `keyboard_lastkey` | Última tecla pulsada (código) |
| `keyboard_lastchar` | Último carácter como string |
| `keyboard_string` | Todo lo tecleado como string |

> ⚠️ Con el **teclado virtual** (móvil) solo funciona `keyboard_string`.

### Simular pulsaciones

```gml
keyboard_key_press(tecla);
keyboard_key_release(tecla);
```

> ⚠️ **Simular pulsaciones NO ejecuta los eventos de teclado.** Solo afecta a las funciones `keyboard_check*()`.

---

## 3. Ratón

### Constantes de botón

| Constante | Botón |
|---|---|
| `mb_left` | Izquierdo |
| `mb_middle` | Central (no válido en todas las plataformas) |
| `mb_right` | Derecho |
| `mb_side1` / `mb_side2` | Botones laterales ⚠️ (solo Windows, macOS, Ubuntu y HTML5) |
| `mb_any` | Cualquiera |
| `mb_none` | Ninguno |

### Funciones

```
mouse_button                       // qué botón está pulsado
mouse_check_button(boton)
mouse_check_button_pressed(boton)
mouse_check_button_released(boton)
mouse_clear(boton)
mouse_lastbutton
mouse_wheel_up() / mouse_wheel_down()
mouse_x / mouse_y                  // coordenadas en la ROOM
```

### Funciones de ventana (escritorio)

```
window_mouse_get_x / window_mouse_get_y
window_mouse_set(x, y)
window_view_mouse_get_x(id_vista) / window_view_mouse_get_y(id_vista)
window_views_mouse_get_x() / window_views_mouse_get_y()
```

### ⚠️ Coordenadas del ratón: el matiz que sorprende

Las coordenadas se actualizan **cada frame**, pero algunas plataformas (por ejemplo **macOS**) usan un *event handler* para capturar la posición.

> **Significa que puede haber frames en los que el ratón se movió pero su posición no cambió**, simplemente porque no hubo evento de ratón entre el frame anterior y el actual.

```gml
// ⚠️ No asumas que mouse_x cambia siempre que el ratón se mueve
```

### En dispositivos táctiles

- El botón **izquierdo** equivale a un toque.
- El botón **derecho** se dispara con un **doble toque** (puedes cambiarlo por código).

> Para **multi-touch** necesitas las funciones `device_mouse_*` (*Device Input*), no las del ratón.

---

## 4. Gamepad

### Detección: usa el Async System event

Cuando se conecta o desconecta un gamepad se dispara un evento asíncrono **System** con tipo `"gamepad discovered"` o `"gamepad lost"`. El slot se devuelve en la clave `"pad_index"` del mapa `async_load`.

> ⚠️ **Este evento NO se disparará salvo que tengas al menos una función `gamepad_*` en tu código.** El runner solo inicializa el subsistema de gamepads cuando se usan.

> ⚠️ **No asumas que un gamepad está en el slot 0.** El slot depende del SO.

### Slots por plataforma

| Plataforma | Slots |
|---|---|
| **Windows** | 0-3 → **XInput** (mandos de Xbox y compatibles). 4-11 → **DirectInput** |
| **Otras** | Cualquier slot que asigne el SO (puede ser el 3, el 20 o más alto) |
| **Android** | Reserva un slot por cada dispositivo Bluetooth emparejado, **esté o no conectado** |

> ⚠️ **Recomendación oficial:** usa el evento **Async System** en lugar de comprobar índices con `gamepad_is_connected()`.

### Constantes de botón

| Constante | Equivalencia |
|---|---|
| `gp_face1` | **A** (Xbox) / **cruz** (PS) |
| `gp_face2` | **B** (Xbox) / **círculo** (PS) |
| `gp_face3` | **X** (Xbox) / **cuadrado** (PS) |
| `gp_face4` | **Y** (Xbox) / **triángulo** (PS) |
| `gp_shoulderl` / `gp_shoulderlb` | Gatillo/bumper izquierdo |
| `gp_shoulderr` / `gp_shoulderrb` | Gatillo/bumper derecho |
| `gp_select` | Select (en PS, pulsar el touchpad) |
| `gp_start` | Start (en PS, «options») |
| `gp_stickl` / `gp_stickr` | Stick pulsado como botón |
| `gp_padu` / `gp_padd` / `gp_padl` / `gp_padr` | D-pad |
| `gp_home` | Botón home (Switch) / logo (PS, Xbox) |
| `gp_touchpadbutton` | Botón del touchpad de PS |
| `gp_paddler` / `gp_paddlel` / `gp_paddlerb` / `gp_paddlelb` | Palancas traseras (Xbox Elite) |
| `gp_extra1` … `gp_extra6` | Botones adicionales |

### Constantes de eje

```
gp_axislh   stick izquierdo, horizontal
gp_axislv   stick izquierdo, vertical
gp_axisrh   stick derecho, horizontal
gp_axisrv   stick derecho, vertical
```

**Solo DualSense en PS4/PS5:**
```
gp_axis_acceleration_x/y/z
gp_axis_angular_velocity_x/y/z
gp_axis_orientation_x/y/z/w      ← cuaternión (por eso 4 valores)
```

> ⚠️ En otras plataformas estas devuelven **0**, incluso con un DualSense.

### ⚠️ Los mandos no estándar no mapean igual

> *«the constants given above **may not match exactly the buttons that you expect when they are pressed**, due to the fragmented and non-standardised way that the API is implemented by controller manufacturers.»*

**Consecuencia:** pon una pantalla de configuración donde el jugador pueda **redefinir** los botones.

GameMaker incluye mapeos de la base de datos **[SDL Gamepad Controller DB](https://github.com/gabomdq/SDL_GameControllerDB)**. Puedes añadir los tuyos con un `gamecontrollerdb.txt` en los **Included Files**.

### Funciones

```
// Generales
gamepad_is_supported()            gamepad_is_connected(slot)
gamepad_get_device_count()        gamepad_enumerate()

// Info y configuración
gamepad_get_guid(slot)            gamepad_get_description(slot)
gamepad_get_button_threshold(slot)   gamepad_set_button_threshold(slot, v)
gamepad_get_axis_deadzone(slot)      gamepad_set_axis_deadzone(slot, v)
gamepad_get_option / set_option
gamepad_set_vibration(slot, izq, der)
gamepad_set_colour(slot, color)
gamepad_axis_count(slot) / button_count(slot) / hat_count(slot)

// Comprobar entrada
gamepad_button_check(slot, boton)
gamepad_button_check_pressed(slot, boton)
gamepad_button_check_released(slot, boton)
gamepad_button_value(slot, boton)     // analógico (gatillos)
gamepad_axis_value(slot, eje)         // -1 .. 1
gamepad_hat_value(slot, hat)          // raro: mandos no estándar

// Mapeos personalizados (solo Windows DirectInput, Ubuntu, macOS, Android)
gamepad_get_mapping(slot)
gamepad_test_mapping(slot, cadena_mapeado)
gamepad_remove_mapping(slot)
```

### Zona muerta bien hecha

Un stick analógico casi nunca reposa exactamente en `(0, 0)`: el desgaste mecánico (*stick
drift*) hace que devuelva valores pequeños en reposo. Sin zona muerta, el personaje camina solo
o la cámara tiembla. Con una zona muerta mal hecha, el input se siente raro sin que sepas por
qué. Hay varias formas de aplicarla, y no todas valen para todo.

**1. Axial (por eje) — la más simple, y la que usa el ejemplo de §8.**

```gml
var _eje_h = gamepad_axis_value(slot, gp_axislh);
if (abs(_eje_h) < 0.25) { _eje_h = 0; }   // ← zona muerta en forma de cruz/cuadrado
```

Zera cada eje **por separado**. Funciona bien para movimiento en 4 direcciones (tipo
Bomberman): el stick queda "enganchado" a las cuatro cardinales, que es justo lo que quieres.
Para cualquier cosa que necesite precisión analógica (apuntar, un twin-stick) se siente mal: al
barrer el stick en un giro amplio —un gesto habitual al apuntar en un shooter— notas cómo se
«engancha» (*snap*) a cada cardinal al cruzarla, en vez de girar liso.

**2. Radial — arregla el enganche, pero tiene "el problema de la precisión".**

```gml
var _eje_h = gamepad_axis_value(slot, gp_axislh);
var _eje_v = gamepad_axis_value(slot, gp_axislv);
var _magnitud = point_distance(0, 0, _eje_h, _eje_v);

if (_magnitud < 0.25)
{
    _eje_h = 0; _eje_v = 0;
}
```

Prueba la magnitud del vector **completo**, no cada eje. Ya no hay enganche a las cardinales: la
zona muerta es un círculo limpio en el centro. Pero al recortar el vector por debajo del umbral
se pierde toda la precisión que había **dentro** de la zona muerta: el input salta de `0` a
`0.25` de golpe justo al cruzar el borde, en vez de arrancar en `0` y crecer. Para mover un
personaje no se nota mucho; para apuntar con precisión (un rifle de francotirador, un
twin-stick de puntería fina) se siente como un tirón brusco justo al empezar a mover el stick.

**3. Radial escalada — la que resuelve el salto.**

La solución es **reescalar** el rango `[zona_muerta, 1]` a `[0, 1]`, para que el input empiece
en `0` justo al salir de la zona muerta y crezca suave hasta `1` en la extensión máxima:

```gml
function input_leer_eje_radial(_slot, _eje_h, _eje_v, _zona_muerta)
{
    var _bruto_h  = gamepad_axis_value(_slot, _eje_h);
    var _bruto_v  = gamepad_axis_value(_slot, _eje_v);
    var _magnitud = point_distance(0, 0, _bruto_h, _bruto_v);

    if (_magnitud < _zona_muerta) { return [0, 0]; }

    // Reescala [zona_muerta, 1] → [0, 1]: sin el salto de la versión radial simple
    var _escalada = clamp((_magnitud - _zona_muerta) / (1 - _zona_muerta), 0, 1);

    // Dirección normalizada × magnitud reescalada
    return [
        (_bruto_h / _magnitud) * _escalada,
        (_bruto_v / _magnitud) * _escalada
    ];
}
```

> 💡 **Cuál usar según el juego** (así lo plantea la fuente de esta sección): axial va bien en
> movimiento por rejilla/4 direcciones; la radial simple basta cuando **solo importa la
> dirección** (el stick de puntería de un twin-stick que no gradúa velocidad de giro); en cuanto
> la **magnitud** importa de verdad —velocidad de movimiento variable, puntería fina en un
> shooter— hace falta la radial escalada.

**4. ⚠️ Curva de respuesta cuadrática (no verificado contra una fuente primaria).** Con una
respuesta lineal, un micro-movimiento cerca del centro ya mueve la mira o el personaje una
fracción notable de la velocidad máxima — dificulta la puntería fina. Es práctica común (no
descrita en la fuente citada abajo) elevar la magnitud **ya reescalada** a una potencia antes de
aplicarla, para dar más control cerca del centro sin perder el máximo en el borde:

```gml
var _leido    = input_leer_eje_radial(slot, gp_axisrh, gp_axisrv, 0.2);
var _magnitud = point_distance(0, 0, _leido[0], _leido[1]);

if (_magnitud > 0)
{
    var _factor = power(_magnitud, 2) / _magnitud;   // respuesta cuadrática (usa 3 para más suave aún)
    _leido[0] *= _factor;
    _leido[1] *= _factor;
}
```

**5. ⚠️ Zona muerta exterior (no verificado contra una fuente primaria).** Por el mismo desgaste
mecánico, muchos sticks no llegan físicamente a `1.0` en su extensión máxima: se quedan en
`0.92` o `0.95`. Si el jugador nunca puede alcanzar la velocidad o precisión tope, se siente mal
sin que sepa por qué. La solución habitual es saturar cerca del borde:

```gml
#macro ZONA_MUERTA_EXTERIOR 0.9

if (_magnitud > ZONA_MUERTA_EXTERIOR) { _escalada = 1; }   // dentro del cálculo de input_leer_eje_radial
```

### Por qué `gamepad_set_axis_deadzone()` del motor no basta para un twin-stick

La función nativa **ya hace bien una cosa**: no tiene el salto del punto 2. El propio manual lo
confirma con su ejemplo: con zona muerta `0.2`, un valor bruto de `0.5` devuelve `0.375`
—exactamente `(0.5 - 0.2) / (1 - 0.2)`, la misma fórmula de la radial escalada—. Pero se queda
corta en dos sitios muy concretos de un twin-stick:

- **Es axial, no radial.** El manual lo dice tal cual: actúa sobre **"el eje del joystick"**,
  uno cada vez. El enganche a las cardinales del punto 1 sigue ahí; no hay forma de pedirle una
  zona muerta circular.
- **Es global al dispositivo, no por stick.** `gamepad_set_axis_deadzone(device, deadzone)`
  «es un ajuste global que afectará a **todos** los ejes de todos los joysticks conectados a la
  ranura indicada» (cita literal del manual). No puedes darle al stick de movimiento una zona
  muerta distinta a la del stick de puntería — y en un twin-stick casi nunca quieres la misma.

Para un twin-stick con curva de respuesta y zona muerta exterior, **no la actives**: calcula tú
la zona muerta a partir de `gamepad_axis_value()` en bruto, como en los puntos 3-5. Resérvala
para juegos de un solo stick donde el eje por eje ya basta.

### Compatibilidad por plataforma

| Plataforma | Soporte | Remapeo |
|---|---|---|
| **Windows** | Hasta 12 dispositivos (0-3 XInput, 4-11 DirectInput) | ✅ |
| **macOS** | Hasta 4. ⚠️ **«Build for Mac App Store» debe estar OFF** | ✅ |
| **Ubuntu** | Sí, requiere `sudo apt-get install jstest-gtk joystick` | ❌ |
| **HTML5** | La mayoría de navegadores **excepto Safari**. Solo detecta mandos tras pulsar un botón o mover un eje | ❌ |
| **iOS** | iCade (digital, no analógico) | ❌ |
| **Android** | NYKO y Bluetooth genéricos (activar iCade/Bluetooth en Game Options) | ✅ |
| **PlayStation** | El touchpad va por `device_mouse_*` | ❌ |
| **Xbox One / Switch** | Completo | ❌ |

### ⚠️ Pérdida de foco

- Los mandos **DirectInput** funcionan en modo cooperativo: solo tienes acceso cuando tu juego está en primer plano. Si pierde el foco, se «pierden» y se «recuperan».
- **No se detecta entrada mientras el juego no tiene el foco**, y un botón mantenido al perder el foco **seguirá pareciendo pulsado** hasta que el juego lo recupere.

```gml
// Pausa el juego si pierde el foco
if (!window_has_focus() || os_is_paused())
{
    global.pausa = true;
}
```

---

## 5. Device Input (multi-touch)

Para multi-touch en móvil, las funciones del ratón no bastan. Usa **Device Input**:

```
device_mouse_x(dispositivo) / device_mouse_y(dispositivo)
device_mouse_check_button(dispositivo, boton)
device_mouse_check_button_pressed(dispositivo, boton)
device_mouse_check_button_released(dispositivo, boton)
device_mouse_x_to_gui(dispositivo) / device_mouse_y_to_gui(dispositivo)
```

```gml
// Recorrer hasta 5 dedos simultáneos
for (var i = 0; i < 5; i++)
{
    if (device_mouse_check_button(i, mb_left))
    {
        var _tx = device_mouse_x_to_gui(i);
        var _ty = device_mouse_y_to_gui(i);
        draw_circle(_tx, _ty, 24, false);
    }
}
```

> En PlayStation, el **touch pad** se lee con estas mismas funciones.

---

## 6. Gestos

Eventos de gestos (tap, drag, flick, pinch, rotate) disponibles en el objeto. Todos rellenan el mapa **`event_data`**.

También por código, en **Gesture Input**.

---

## 7. La librería Input (recomendada para proyectos serios)

### Qué es

> **Input** es «una librería de input robusta y llena de funciones que unifica teclado, ratón y gamepad bajo un mismo techo».

- **Autores:** Juju Adams y Alynne Keith (y colaboradores).
- **Versión actual (agosto 2026):** **10.4.3**, etiquetada explícitamente para **GameMaker LTS 2026**.
- **Licencia:** gratuita, con Patreon/Ko-fi para apoyar el desarrollo.

### ⚠️ Dónde está (importante, porque se movió)

| | Ubicación |
|---|---|
| Repositorio **antiguo** (espejo) | <https://github.com/offalynne/Input> — pone *«Moved to Codeberg»* |
| **Repositorio actual** | <https://codeberg.org/offalynne/Input> |
| Documentación | <https://offalynne.grebedoc.dev/Input/> |
| Descarga | Un archivo `.yymps` (local package de GameMaker) |

> ⚠️ **No está en la organización `YoYoGames` de GitHub.** Es una librería de la comunidad. Sin embargo, el propio **Russell Kay (rwkay), de YoYo Games, la recomienda en el bug tracker oficial** en conversaciones sobre gamepads problemáticos, diciendo cosas como:
> *«Please try using the Input library that I linked above with these controllers - this may be situations that alynne has already encountered and implemented a solution for.»*

### Por qué usarla

| Problema del input nativo | Cómo lo resuelve Input |
|---|---|
| Los mandos DirectInput devuelven valores inconsistentes | Capa de normalización probada en muchos dispositivos |
| No sabes en qué slot está el mando | Gestión automática mediante el evento Async |
| Rebindeo: tienes que escribirlo tú | Sistema de rebindeo integrado |
| Teclado, ratón y mando son APIs distintas | **API unificada** con «verbos» abstractos |
| Detección de dispositivos conectados/desconectados | Gestión automática |
| Zona muerta de sticks analógicos | Configurable y consistente |

### Instalación

1. Descarga el `.yymps` desde Codeberg o la documentación.
2. En GameMaker: **Tools → Import Local Package** (o arrastra el `.yymps` al IDE).
3. Importa todos los recursos.

### Filosofía de uso (conceptual)

La librería trabaja con **perfiles de jugador** y **verbos abstractos** en lugar de teclas concretas:

```
Verbo "mover_izquierda"  →  A / ← / stick izquierdo hacia la izquierda
Verbo "saltar"           →  Espacio / W / gp_face1
Verbo "pausa"            →  Escape / gp_start
```

Ventaja: tu código de juego pregunta por **«¿saltar?»**, no por «¿Espacio?» ni por «¿gp_face1?». Añadir soporte para un dispositivo nuevo no cambia ni una línea de la lógica del juego.

> 📖 **Para la API exacta** consulta siempre <https://offalynne.grebedoc.dev/Input/>, porque las firmas cambian entre versiones mayores de la librería.

### Cuándo NO usarla

- Prototipos de una tarde.
- Juegos de un solo botón.
- Cuando el tamaño del paquete es crítico.

### Cuándo SÍ

- Cualquier juego que vayas a publicar.
- Si vas a soportar gamepad.
- Si quieres que el jugador pueda reconfigurar los controles.
- Si vas a varias plataformas (consolas, móvil, web).

---

## 8. Ejemplo completo: controlador de input unificado (nativo)

Si no quieres añadir la librería, este es el patrón a seguir con las funciones nativas:

```gml
// ═══════════ Script: scr_input ═══════════

/// @description Verbos de input abstractos.
///              Devuelven true/false o un valor -1..1.

function input_mover_x()
{
    var _teclado = keyboard_check(ord("D")) - keyboard_check(ord("A"));
    if (_teclado != 0) { return _teclado; }

    if (global.gamepad_slot != noone)
    {
        var _eje = gamepad_axis_value(global.gamepad_slot, gp_axislh);
        if (abs(_eje) > 0.25) { return _eje; }   // zona muerta
    }

    return 0;
}

function input_mover_y()
{
    var _teclado = keyboard_check(ord("S")) - keyboard_check(ord("W"));
    if (_teclado != 0) { return _teclado; }

    if (global.gamepad_slot != noone)
    {
        var _eje = gamepad_axis_value(global.gamepad_slot, gp_axislv);
        if (abs(_eje) > 0.25) { return _eje; }
    }

    return 0;
}

function input_saltar_pulsado()
{
    var _teclado = keyboard_check_pressed(vk_space);
    var _mando   = (global.gamepad_slot != noone)
                   && gamepad_button_check_pressed(global.gamepad_slot, gp_face1);

    return _teclado || _mando;
}

function input_pausa()
{
    var _teclado = keyboard_check_pressed(vk_escape);
    var _mando   = (global.gamepad_slot != noone)
                   && gamepad_button_check_pressed(global.gamepad_slot, gp_start);

    return _teclado || _mando;
}
```

```gml
// ═══════════ obj_game (Create) ═══════════
global.gamepad_slot = noone;

// ═══════════ obj_game (Async - System) ═══════════
// Detectamos gamepads conectados/desconectados
var _tipo = async_load[? "event_type"];

if (_tipo == "gamepad discovered")
{
    var _slot = async_load[? "pad_index"];
    global.gamepad_slot = _slot;
    show_debug_message($"Gamepad conectado en slot {_slot}");
}
else if (_tipo == "gamepad lost")
{
    var _slot = async_load[? "pad_index"];
    if (global.gamepad_slot == _slot)
    {
        global.gamepad_slot = noone;
    }
    show_debug_message($"Gamepad desconectado del slot {_slot}");
}
```

```gml
// ═══════════ obj_jugador (Step) ═══════════
// La lógica del juego pregunta por VERBOS, no por teclas
var _dx = input_mover_x();
var _dy = input_mover_y();

// Normalizar el vector diagonal
if (_dx != 0 || _dy != 0)
{
    var _longitud = point_distance(0, 0, _dx, _dy);
    _dx /= _longitud;
    _dy /= _longitud;
}

move_and_collide(_dx * velocidad, _dy * velocidad, [obj_pared, tilemap_suelo]);

if (input_saltar_pulsado() && en_suelo)
{
    vel_y = vel_salto;
}
```

```gml
// ═══════════ obj_controlador (Step) ═══════════
// Pausa: centralizada, no repartida por objetos
if (input_pausa())
{
    global.pausa = !global.pausa;
}

// Pausa automática al perder el foco
if (!window_has_focus() || os_is_paused())
{
    global.pausa = true;
}
```

**Por qué está bien:**
- El código del jugador **no sabe** si usas teclado o mando.
- El manejo del gamepad vive en **un solo sitio** (el evento Async).
- La **zona muerta** evita el drift de los sticks.
- Se **normaliza el vector diagonal**.
- Funciona igual aunque el Debug Overlay esté abierto (usa funciones, no eventos).

---

## 8 bis. Input táctil móvil: gestos y teclado virtual

Si publicas en móvil, el jugador no tiene teclado ni mando: tiene un dedo. GameMaker trae dos
sistemas para eso —**gestos** y **teclado virtual**— que casi ningún tutorial en español cubre.

### Gestos táctiles (tap, drag, flick, pinch)

En vez de leer coordenadas de toque a mano, GameMaker reconoce **gestos** y los entrega como
**eventos de objeto**. En el editor de objetos → Add Event → **Gesture**:

| Evento | Gesto | Uso típico |
|---|---|---|
| **Tap** | toque simple | pulsar un botón |
| **Double Tap** | doble toque | acción rápida (recargar, saltar) |
| **Drag Start / Dragging / Drag End** | arrastrar | mover una pieza, un joystick |
| **Flick** | deslizar rápido y soltar | lanzar algo, pasar de página |
| **Pinch In / Out / End** | pellizcar con dos dedos | **zoom** de cámara |

```gml
/// obj_camara · Gesture - Pinch In / Pinch Out — zoom con dos dedos
var _dist = gesture_get_pinch_distance();   // separación actual de los dedos
zoom = clamp(zoom_previo * (_dist / dist_inicial), 0.5, 2.0);
```

**La sensibilidad se ajusta**, y esto importa mucho en móvil (una pantalla de 5" no es una de
10"):

```gml
/// Create — afinar qué cuenta como cada gesto
gesture_drag_distance(16);        // píxeles antes de considerar que arrastras
gesture_flick_speed(300);         // velocidad mínima para un flick
gesture_double_tap_time(300);     // ms máximos entre los dos toques
gesture_tap_count(true);          // permitir detectar toques múltiples
```

> 🔺 **Los gestos también funcionan con ratón en escritorio**, así que puedes desarrollar y
> probar en el PC. Pero **prueba en un móvil real** antes de publicar: las distancias y tiempos
> que se sienten bien con ratón no son los mismos con el dedo.
>
> 💡 Para input táctil «a mano» (sin gestos), están `device_mouse_x/y(dispositivo)` y
> `device_mouse_check_button` — un móvil admite varios toques a la vez (multi-touch), cada uno
> un «dispositivo». Los gestos son la capa cómoda encima de eso.

### Teclado virtual (introducir texto en móvil)

Para que el jugador escriba (nombre en un ranking, chat), se muestra el teclado del sistema:

```gml
/// mostrar el teclado para escribir un nombre
keyboard_virtual_show(kbv_type_default,      // tipo: default, ascii, url, email, numbers, phone
                      kbv_returnkey_done,     // qué pone la tecla de retorno
                      kbv_autocapitalize_words,
                      true);                  // texto predictivo

/// cuando termina, ocultarlo
if (keyboard_virtual_status()) {              // ¿está visible?
    // leer keyboard_string, y al terminar:
    keyboard_virtual_hide();
}
```

> ⚠️ **El teclado virtual tapa parte de la pantalla.** `keyboard_virtual_height()` te dice
> cuántos píxeles ocupa, para subir el campo de texto y que no quede oculto tras el teclado.
> `keyboard_virtual_set_position` coloca dónde aparece.
>
> 🔺 **Solo existe en móvil.** En escritorio, `keyboard_virtual_show` no hace nada (usas
> `keyboard_string` directamente). Protege con `if (os_type == os_android || os_type == os_ios)`.

### Ver también móvil

- [16 · Exportar y publicar](./16%20-%20Exportar%20y%20publicar.md) — exportar a Android/iOS
- [Servicios de plataforma](../04%20-%20Recetas%20por%20género/20%20-%20Servicios%20de%20plataforma%20%28logros,%20anuncios,%20compras%29.md) — IAP y anuncios, que en móvil van de la mano del táctil
- [25 · Menú de opciones](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md) — controles táctiles en pantalla

---

## 9. Errores típicos

### ❌ Usar `ord()` con minúsculas o caracteres especiales

```gml
keyboard_check(ord("a"));   // ❌ solo detecta A-Z en MAYÚSCULAS
keyboard_check(ord("ñ"));   // ❌ no funciona

// ✅ Para caracteres especiales, usa keyboard_lastchar
if (keyboard_lastchar == "ñ") { ... }
```

### ❌ Suponer que el gamepad está en el slot 0

```gml
gamepad_button_check(0, gp_face1);   // ❌ puede no estar ahí

// ✅ Usa el slot detectado en el evento Async
gamepad_button_check(global.gamepad_slot, gp_face1);
```

### ❌ Esperar que el evento Async se dispare sin funciones `gamepad_*`

El subsistema no se inicializa hasta que usas alguna función `gamepad_*`.

### ❌ No aplicar zona muerta a los sticks

```gml
var _eje = gamepad_axis_value(slot, gp_axislh);
if (_eje != 0) { mover(_eje); }   // ❌ el stick nunca vale exactamente 0

// ✅
if (abs(_eje) > 0.25) { mover(_eje); }
```

### ❌ Poner input en el evento Draw

Va en **Step** (o Begin Step). El Draw es para dibujar.

### ❌ Consultar `mouse_x` en Draw GUI creyendo que son coordenadas GUI

`mouse_x`/`mouse_y` son coordenadas de **room**. Para GUI usa `device_mouse_x_to_gui(0)` / `device_mouse_y_to_gui(0)`.

---

## Resumen

1. **Eventos** para prototipos; **funciones en el Step** para control real.
2. ⚠️ El **Debug Overlay bloquea los eventos** de teclado y ratón, pero **no** las funciones.
3. `ord()` solo sirve para `0-9` y `A-Z`. Para el resto, `vk_*` o `keyboard_lastchar`.
4. `mouse_x`/`mouse_y` son coordenadas de **room**. Puede haber frames sin actualización (macOS).
5. **Gamepad:** detecta con el **Async System event**, nunca asumas el slot 0, y aplica **zona muerta**.
6. Los mandos **no estándar mapean distinto**: ofrece rebindeo.
7. ⭐ **La librería Input** (Juju Adams + Alynne Keith, v10.4.3 para LTS 2026, ahora en **Codeberg**) unifica teclado, ratón y mando y es lo recomendado para proyectos serios. **No es de la organización YoYoGames**, aunque el personal de YoYo la recomienda en su bug tracker.
8. Independientemente de la librería: **abstrae tus controles en «verbos»** (`input_saltar()`), no en teclas.
