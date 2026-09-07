# 12 · Input — teclado, ratón y gamepad

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/Game_Input.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/Keyboard_Input/Keyboard_Input.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/Mouse_Input/Mouse_Input.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/GamePad_Input/Gamepad_Input.htm>
> - <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Object_Events.htm>
> - <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Game_Input/Virtual_Keys_And_Keyboards/Virtual_Keys_And_Keyboards.htm>
>   (IME en Windows vía `keyboard_virtual_show`/`_hide`, §2 «IME y entrada de texto no ASCII»)
> - <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Cameras_And_Display/display_reset.htm>
>   (vsync, §4 «Vsync y latencia de input»)
> - <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Game_Input/GamePad_Input/gamepad_get_mapping.htm> ·
>   <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Game_Input/GamePad_Input/gamepad_test_mapping.htm>
> - Josh Sutphin, *Doing Thumbstick Dead Zones Right*, Third Helix, 12-04-2013 — consultada el
>   06-09-2026 vía una copia de 2014 en Wayback Machine (`web.archive.org/web/20141025070920/`);
>   el dominio original hoy redirige a contenido sin relación, así que cita siempre el archivo.
> - Wikipedia, *Screen tearing* — consultada 2026-09-06, solo para la relación general
>   vsync↔latencia de entrada (§4 «Vsync y latencia de input»); GameMaker no la documenta.

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
keyboard_unset_map()                          // ⚠️ SIN argumentos: borra TODOS los mapeos

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

### Remapeo físico del teclado: `keyboard_set_map` frente al rebinding lógico

`keyboard_set_map(key1, key2)` no es rebinding: es un remapeo a nivel del propio runtime.
Redirige la tecla física `key1` para que **se interprete como** `key2` en todas las funciones
`keyboard_check*()` — y `key1` deja de poder detectarse como ella misma mientras el mapeo esté
activo, tal como advierte el propio manual:

```gml
keyboard_set_map(ord("W"), vk_up);   // pulsar "W" se interpreta como vk_up
// A partir de aquí, keyboard_check(ord("W")) YA NO detecta la "W" físicamente pulsada:
// solo detecta vk_up. Si tu juego también usaba "W" para otra cosa, se ha roto.

keyboard_unset_map();   // ⚠️ sin argumentos: borra TODOS los mapeos a la vez, no solo este
```

**Cuándo usarlo en vez del rebinding lógico de
[04 · 25 §5](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md#5--reasignar-controles-rebinding):**
casi nunca, para juegos propios. El rebinding de verbos (`global.controles`, esa misma
sección) es lo correcto cuando quieres que el jugador reconfigure **sus acciones**, porque no
toca las teclas de nadie más y admite conflictos, perfiles y persistencia.
`keyboard_set_map()` sirve para el caso contrario y mucho más raro: cuando necesitas que
**todo el runtime**, sin tocar tu código de lectura de input, vea una tecla física como si
fuera otra distinta — por ejemplo, redirigir un layout de teclado no estándar sin reescribir
cada `keyboard_check(ord("W"))` del proyecto. Es compatibilidad de bajo nivel, no un sustituto
del menú de Opciones.

Símbolos verificados: `keyboard_set_map`, `keyboard_unset_map`, `keyboard_get_map`.

### IME y entrada de texto no ASCII (CJK)

> 🔴 **Hueco cerrado aquí.** La biblioteca documentaba cómo *mostrar* texto chino, japonés o
> coreano (fuentes con los glifos correctos, en
> [21 · Localización §4](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md#4--fuentes-y-glifos--la-trampa-de-los-alfabetos-no-latinos)),
> nunca cómo **escribirlo**. Esto responde con lo que el manual documenta de verdad — ni más,
> ni menos.

**Qué es un IME y por qué `ord()`/`vk_*` no valen aquí.** Un IME (*Input Method Editor*) es la
capa del sistema operativo que traduce una secuencia de teclas latinas (pinyin, romaji…) en
una ventana de **composición** donde el jugador elige el carácter final entre varias opciones
antes de confirmarlo. Mientras compone, eso no es una pulsación de tecla normal: no tiene un
único `vk_*` ni un `ord()` de un solo carácter — el mismo motivo por el que arriba `ord()` con
`keyboard_check*()` solo detecta `0-9`/`A-Z`.

**Lo que dice el manual — y lo que NO dice.** Comprobado íntegro sobre `09 - Manual oficial/`
(es y en): **ninguna página menciona «IME» ni «composición»**, salvo una excepción concreta
(siguiente punto). Las páginas de `keyboard_string` y `keyboard_lastchar` solo dicen que
recogen «los caracteres imprimibles escritos» — ni una palabra sobre qué pasa mientras un IME
está componiendo.

**La excepción, y es la respuesta real:** la página de **Teclas y teclados virtuales** dice,
sobre `keyboard_virtual_show`/`_hide`/`_status`/`_height`/`_set_position`:

> *«Estas funciones sólo son válidas para las plataformas de destino **Xbox (GDK)**, **Android**
> (incluido AndroidTV) e **iOS** (incluido tvOS). En **Windows**, se pueden utilizar para
> activar o desactivar el uso de IME.»*

Es la única mención a IME en todo el manual, y es la pieza que faltaba: **el teclado virtual de
GameMaker no es solo para móvil.** En Windows, llamar a `keyboard_virtual_show()` no dibuja
nada en pantalla — **activa el IME del sistema**, y el resultado (ya confirmado, con los
caracteres CJK elegidos) llega por `keyboard_string`, igual que en móvil: *«no activarán los
eventos regulares del teclado, sino que actualizarán la variable `keyboard_string`»* (misma
página).

```gml
// obj_campo_nombre — al entrar en un campo que puede necesitar CJK (nombre, chat)
// Verificado: keyboard_virtual_show, keyboard_virtual_hide, keyboard_string

function campo_texto_ime_activar()
{
    keyboard_string = "";
    // En Windows esto NO dibuja un teclado: activa el IME del sistema operativo.
    // En Android/iOS/Xbox abre el teclado nativo, que ya trae su propio IME integrado.
    keyboard_virtual_show(kbv_type_default, kbv_returnkey_done, kbv_autocapitalize_none, false);
}

function campo_texto_ime_leer()
{
    // NO leas keyboard_check*/keyboard_lastkey mientras esto está activo: el manual dice que
    // esos eventos normales no se disparan. Lee SIEMPRE keyboard_string.
    return keyboard_string;
}

function campo_texto_ime_desactivar()
{
    keyboard_virtual_hide();
}
```

> ⚠️ **Esto no es una solución nativa completa, y hay que decirlo con esas palabras.** La nota
> del manual cubre Xbox, Android, iOS y Windows (solo para IME). **No menciona macOS, Ubuntu,
> HTML5 ni GX.games en absoluto** — a diferencia de las teclas virtuales (la otra mitad de esa
> misma página), que sí listan HTML5 y GX.games como compatibles. No hay fuente primaria que
> confirme qué ocurre en macOS o Linux al llamar a `keyboard_virtual_show()` con un IME del
> sistema activo. **Pruébalo en la plataforma real antes de prometerle japonés al jugador en
> Mac o Linux**, no asumas que funciona solo porque funciona en Windows.

**En la práctica, para un campo que deba admitir japonés/chino/coreano:**

1. Llama a `keyboard_virtual_show()` al entrar en el campo **en todas las plataformas de
   escritorio y móvil por igual** — no lo reserves para `os_android`/`os_ios` como hace el
   teclado virtual "normal" de [§8bis](#8-bis-input-táctil-móvil-gestos-y-teclado-virtual): en
   Windows es la única forma documentada de activar el IME.
2. Lee siempre `keyboard_string`, nunca `keyboard_check*()` ni `keyboard_lastchar` mientras el
   campo esté activo.
3. Al confirmar o cancelar, `keyboard_virtual_hide()`.
4. La fuente de dibujo necesita los glifos CJK — ya resuelto en
   [21 · Localización §4](../04%20-%20Recetas%20por%20género/21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md#4--fuentes-y-glifos--la-trampa-de-los-alfabetos-no-latinos):
   una fuente con Noto Sans CJK y cacheado por glifo, no el rango de `font_add()`.
5. Si tu juego no puede permitirse esa incertidumbre en macOS/Linux (un ranking competitivo
   donde todo el mundo necesita poder escribir su nombre), la alternativa honesta es un
   **selector de caracteres en pantalla** — una rejilla navegable con `foco_rejilla()` de
   [13 · 05 §2.2](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#22-navegación-con-mando-y-teclado-foco-orden-envolvente-y-repetición) —
   más lento de usar, pero no depende de un IME del sistema sin documentar en esa plataforma.

Símbolos verificados: `keyboard_virtual_show`, `keyboard_virtual_hide`, `keyboard_string`. No
existe `keyboard_ime_*` ni `os_ime_*`: comprobado con `--listar keyboard_` (21 símbolos,
ninguno con «ime») y `--texto "IME"` sobre toda la biblioteca antes de escribir esta sección.

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

> ⚠️ **No hay giroscopio nativo distinto del acelerómetro/tilt.** GameMaker no expone un sensor
> de rotación en bruto aparte: solo `device_get_tilt_x()`, `device_get_tilt_y()` y
> `device_get_tilt_z()` (verificado con `--listar device_get`: son los tres únicos símbolos de
> esa familia). No existe `device_get_gyro_*` ni equivalente, ni una constante `gp_axis_gyro_*`
> entre las de arriba. Receta de inclinación, calibración y zona muerta con lo que sí hay:
> [04 · 28 §8.1](../04%20-%20Recetas%20por%20género/28%20-%20Juegos%20para%20móvil%20%28táctil%29.md#81-inclinación-acelerómetro).

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

### Mapeos SDL personalizados: cuando `gamecontrollerdb.txt` no basta

Antes de tocar estas tres funciones, la mayoría de mandos exóticos ya se resuelven con un
`gamecontrollerdb.txt` actualizado en los **Included Files** (arriba). Son el siguiente nivel:
**escribir tú mismo** el mapeo SDL de un mando que ni siquiera esa base de datos reconoce.

```gml
// gamepad_get_mapping(slot) — ¿ya tiene mapeo este mando?
var _mapa = gamepad_get_mapping(slot);

if (_mapa == "no mapping" || _mapa == "")
{
    // Mismo formato que gamecontrollerdb.txt: GUID,nombre,botón:código,...,platform:X
    var _mapa_manual = "030000005e0400008e02000010010000,Mando genérico," +
                       "a:b0,b:b1,x:b2,y:b3,leftx:a0,lefty:a1,rightx:a2,righty:a3," +
                       "leftshoulder:b4,rightshoulder:b5,start:b7,back:b6,platform:Windows";
    gamepad_test_mapping(slot, _mapa_manual);   // lo aplica para PROBARLO, sin persistirlo
}
```

`gamepad_test_mapping(index, value)` aplica el mapeo dado para esa sesión, sin guardarlo.
`gamepad_remove_mapping(index)` lo retira y el mando vuelve a reportar botones sin traducir.
`gamepad_get_mapping(index)` devuelve el string SDL activo, `"no mapping"` si el slot no tiene
ninguno, o `"device index out of range"` si el slot ni siquiera es válido.

> 💡 **Cuándo se llega hasta aquí de verdad**: casi nunca. Es la última instancia cuando un
> mando muy concreto (un stick arcade artesanal, una marca pequeña) llega a un jugador y
> `gamecontrollerdb.txt` no lo cubre — necesitas que el propio jugador te mande el nombre que
> reporta `gamepad_get_description(slot)` y el mapeo botón por botón antes de poder escribir el
> string de arriba a mano.

Símbolos verificados: `gamepad_get_mapping`, `gamepad_test_mapping`, `gamepad_remove_mapping`.

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

### Varios mandos, uno por jugador (co-op local)

Para 2-4 jugadores en el mismo sofá, cada uno necesita un **slot de jugador fijo**: el primer
mando que se conecta no es necesariamente el del "jugador 1" si alguien desconecta el suyo y lo
vuelve a enchufar a mitad de partida. El patrón es acumular los `pad_index` que llegan por el
evento **Async System** de "Detección" (arriba) y asignarles un número de jugador **en el orden
en que aparecen** — nunca fijar el slot a mano, por lo dicho en «no asumas que un gamepad está
en el slot 0».

```gml
// ═══════════ obj_input_manager — Create (persistente, uno por partida) ═══════════
mandos_por_jugador = [];      // índice = número de jugador (0-3); valor = pad_index, o -1

/// @func mando_asignar(_pad_index)
/// @desc Le da al mando el primer hueco de jugador libre, o le devuelve el que ya tenía si
///       es una reconexión. Llamarlo desde "gamepad discovered" (evento Async System).
/// @returns {Real} El número de jugador (0-3) al que se asignó el mando.
function mando_asignar(_pad_index)
{
    var _n = array_length(mandos_por_jugador);

    // ¿Ya estaba asignado? (reconexión del mismo mando) no lo dupliques.
    for (var _i = 0; _i < _n; _i++)
    {
        if (mandos_por_jugador[_i] == _pad_index) return _i;
    }

    // Primer hueco libre (quedó a -1 tras una desconexión)
    for (var _i = 0; _i < _n; _i++)
    {
        if (mandos_por_jugador[_i] == -1) { mandos_por_jugador[_i] = _pad_index; return _i; }
    }

    array_push(mandos_por_jugador, _pad_index);
    return array_length(mandos_por_jugador) - 1;
}

/// @func mando_liberar(_pad_index)
/// @desc Llamarlo desde "gamepad lost". Deja el hueco en -1 en vez de encoger el array, para
///       que los demás jugadores NO cambien de número de jugador a mitad de partida.
function mando_liberar(_pad_index)
{
    var _n = array_length(mandos_por_jugador);
    for (var _i = 0; _i < _n; _i++)
    {
        if (mandos_por_jugador[_i] == _pad_index) { mandos_por_jugador[_i] = -1; return; }
    }
}
```

```gml
// ═══════════ obj_input_manager — Async System ═══════════
switch (async_load[? "event_type"])
{
    case "gamepad discovered":
        var _jugador = mando_asignar(async_load[? "pad_index"]);
        show_debug_message("Mando conectado → jugador " + string(_jugador));
        break;

    case "gamepad lost":
        mando_liberar(async_load[? "pad_index"]);
        break;
}
```

Cada `obj_jugador` lee su propio mando con `obj_input_manager.mandos_por_jugador[numero_jugador]`
en vez de asumir un slot fijo. Si el valor es `-1`, ese jugador todavía no tiene mando —
enséñale una pantalla de "conecta un mando" en vez de leer input de un slot que no existe.

> 💡 **Para arrancar con los mandos que ya estaban conectados** (no solo los que se detectan
> DESPUÉS): recorre `gamepad_get_device_count()` slots al empezar la partida y llama a
> `mando_asignar()` para cada uno que `gamepad_is_connected()` confirme. El evento *Async
> System* solo dispara ante **cambios** de conexión, no te da el estado inicial.

Símbolos verificados: `gamepad_get_device_count`, `gamepad_is_connected`, `array_length`,
`array_push`.

### Vsync y latencia de input

`display_reset(aa, vsync)` es la única función del runtime que toca la sincronización vertical
en marcha. El manual advierte, literalmente, que activarla *«puede dar una experiencia de
juego más suave, pero también necesitará más potencia de procesamiento, por lo que su impacto
debe ser considerado cuidadosamente antes de su uso»*. Desde 2026.0, **vsync viene activada por
defecto** en todos los targets compatibles (ver
[05 · 02 §4.1](../05%20-%20Referencia/02%20-%20Publicar%20y%20exportar.md#41-cambios-de-20260-que-afectan-a-tu-publicación)),
así que si no tocas nada, tu juego ya la lleva encendida.

```gml
// Alternar vsync en caliente, típicamente desde Opciones (04 · 25)
display_reset(0, _vsync_activado);   // 0 = sin antialiasing; conserva el AA que ya tuvieras
```

**La disyuntiva que el manual no explica:**

| | **Vsync activada** | **Vsync desactivada** |
|---|---|---|
| *Tearing* (el frame se corta a media pantalla) | No aparece | Puede aparecer si el juego renderiza más rápido que la tasa de refresco |
| Latencia de entrada | El frame terminado espera al siguiente refresco de pantalla antes de mostrarse: añade retraso entre pulsar y ver el resultado | El frame se muestra en cuanto está listo: la latencia es la mínima que puede dar el motor |
| Coste de GPU | Limita el juego a la tasa de refresco del monitor | El juego renderiza tan rápido como la GPU dé, gastando ciclos que no llegan a verse |

> ⚠️ La relación general entre vsync y latencia de entrada (el frame se retiene hasta el
> intervalo de blanqueo vertical antes de mostrarse) es conocimiento de gráficos por
> computador establecido en el oficio, **no algo que documente el manual de GameMaker**: el
> manual solo habla del coste de «potencia de procesamiento», nunca de la latencia. Confirmado
> como relación real —sin cifra concreta de GameMaker— en Wikipedia, *Screen tearing*:
> *«vertical synchronization causes input lag»* (consultado 2026-09-06).

**Cuándo compensa cada cual:**

- **Vsync activada** por defecto: para casi todo el catálogo (RPG, aventura, puzzle, la
  mayoría de plataformas) el tearing se nota más que un poco de retraso, y es lo que trae
  GameMaker de fábrica desde 2026.0.
- **Vsync desactivada, o al menos opcional**: en cualquier juego donde la latencia se juega —
  shmups, lucha, plataformas de precisión estricta, shooters twin-stick competitivos. El coyote
  time y el buffer de
  [06 · scr_input_buffer.gml](../06%20-%20Assets%20y%20Scripts/scr_input_buffer.gml) compensan
  unos fotogramas de cuándo se **lee** la pulsación, no de cuándo se **muestra** el resultado en
  pantalla: son dos retrasos distintos, y este es el segundo.

**La recomendación práctica: no decidas tú, dale la opción al jugador.** Un toggle más en
[04 · 25 §1](../04%20-%20Recetas%20por%20género/25%20-%20Menú%20de%20opciones%20y%20ajustes.md#1--los-widgets-leer-y-cambiar),
aplicado en vivo con el mismo patrón que «pantalla_completa»:

```gml
// aplicar_ajuste() de 04 · 25 §2 — un case más, mismo patrón que "pantalla_completa"
case "vsync":
    display_reset(0, _w.val);
    break;
```

Símbolo verificado: `display_reset`.

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
9. **IME/CJK**: no hay solución nativa documentada para macOS/Linux. En Windows, Android, iOS y
   Xbox, `keyboard_virtual_show()` + leer `keyboard_string` sí es la vía oficial — también en
   escritorio, no solo en móvil.
10. **Vsync no es solo un ajuste visual**: añade latencia de entrada. Ofrécelo como opción, no
    lo fijes tú por el jugador.
