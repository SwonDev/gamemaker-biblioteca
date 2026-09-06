# 21 · Constantes que el manual abrevia

> Hay **47 símbolos que existen en el runtime 2026.0.0.23 y no aparecen escritos en ninguna
> parte del manual**, ni en español ni en inglés. No es que estén poco documentados: es que
> el texto que los describe usa puntos suspensivos —`ev_outside_view0...7`, «hasta
> `argument15`»— y los miembros intermedios no llegan a escribirse nunca.
>
> **Por qué importa:** cualquier búsqueda exacta de `ev_outside_view4` en el manual devuelve
> cero resultados. Un LLM concluye que no existe. Esta página los escribe uno a uno para que
> sí se encuentren.
>
> Complementa a [20 · Lo que el manual no documenta](./20%20-%20Lo%20que%20el%20manual%20no%20documenta.md),
> que cuenta cuántos hay; esta explica **estos**.

Comprobado el 2 de septiembre de 2026 contra `GmlSpec.xml` del runtime y contra el espejo
completo del manual (3142 páginas en español, 3119 en inglés).

---

## 1 · `pi`

Sí: **la constante `pi` no está escrita en ninguna página del manual.**

```gml
show_debug_message(pi);          // 3.14159265358979
var _grados = _radianes * 180 / pi;
```

| | |
|---|---|
| Tipo | constante `Real` |
| Valor | 3,14159265358979 |
| Alternativa | `degtorad()` y `radtodeg()` hacen la conversión sin escribir la fórmula |

> 💡 En la práctica casi nunca la necesitas: GML trabaja en **grados**, no en radianes.
> `image_angle`, `direction`, `lengthdir_x` y `draw_sprite_ext` esperan grados. `pi` solo
> aparece cuando escribes matemáticas propias o pasas ángulos a un shader (GLSL sí usa
> radianes).

---

## 2 · Argumentos numerados: `argument0` … `argument15`

El manual dice literalmente «`argument0`, `argument1`, `argument2`, etc... hasta
`argument15`». Los que faltan por escribir son **`argument5` a `argument13`**.

Los dieciséis existen: `argument0`, `argument1`, `argument2`, `argument3`, `argument4`,
`argument5`, `argument6`, `argument7`, `argument8`, `argument9`, `argument10`, `argument11`,
`argument12`, `argument13`, `argument14`, `argument15`.

```gml
/// forma antigua — evítala en código nuevo
function suma_vieja() {
    return argument0 + argument1;
}

/// forma actual
function suma(_a, _b) {
    return _a + _b;
}
```

> ⚠️ **El límite real es 16 argumentos**, y no es una recomendación: `argument16` no existe.
>
> 🔺 **Trampa documentada del compilador:** si usas `argument0..N` debes referenciar **todos**
> los índices de 0 a n al menos una vez. Si dejas de usar `argument0`, hay que renumerar todos
> los demás. Es una de las razones por las que los parámetros con nombre son mejores.

---

## 3 · Eventos por vista: `ev_outside_view0…7` y `ev_boundary_view0…7`

El manual los describe como un rango en una tabla de `event_perform`. Escritos uno a uno:

**Fuera de la vista** — la instancia está fuera del área que muestra esa vista:

`ev_outside_view0`, `ev_outside_view1`, `ev_outside_view2`, `ev_outside_view3`, `ev_outside_view4`, `ev_outside_view5`, `ev_outside_view6`, `ev_outside_view7`

**Cruce de borde** — la instancia toca el borde de esa vista:

`ev_boundary_view0`, `ev_boundary_view1`, `ev_boundary_view2`, `ev_boundary_view3`, `ev_boundary_view4`, `ev_boundary_view5`, `ev_boundary_view6`, `ev_boundary_view7`

```gml
/// destruir una bala cuando sale de la vista 0
event_perform(ev_other, ev_outside_view0);
```

En el editor de objetos son **Other → Outside View 0..7** e **Intersect Boundary View 0..7**.

📘 [`event_perform`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Objects/Object_Events/event_perform.md)

> 💡 **Ocho vistas, numeradas de 0 a 7.** Es el mismo límite que en `view_camera[0..7]`. Ver
> [10 · Rooms, capas, cámaras y viewports](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md).

**También sin escribir:** `ev_draw_normal` (el sub-evento Draw normal, frente a `ev_draw_begin`
y `ev_draw_end`) y `ev_async_audio_playback_ended`, el evento asíncrono que salta cuando un
sonido termina —cuya **página sí existe** ahora en español, traducida por esta biblioteca.

---

## 4 · Botones extra de mando: `gp_extra1` … `gp_extra6`

**Estos no aparecen en el manual en ningún idioma**, ni siquiera abreviados. Existen los seis:
`gp_extra1`, `gp_extra2`, `gp_extra3`, `gp_extra4`, `gp_extra5`, `gp_extra6`.

```gml
if (gamepad_button_check_pressed(0, gp_extra1)) { /* … */ }
```

> ⚠️ **A qué botón físico corresponden depende del mando y de la plataforma.** No asumas
> nada: en un mando de Xbox pueden no existir; en mandos con paletas traseras o botones
> adicionales, sí. **Compruébalo con el mando real** antes de asignarles nada importante, y
> no los uses como controles obligatorios.
>
> 💡 Para saber cuáles responde de verdad tu mando:
> ```gml
> for (var _b = gp_extra1; _b <= gp_extra6; _b++) {
>     if (gamepad_button_check_pressed(0, _b)) show_debug_message($"extra pulsado: {_b}");
> }
> ```

---

## 5 · Constantes de red

Tres familias, con miembros que el manual no escribe:

**Tipo de mensaje recibido** (`async_load[? "type"]` en el evento Networking):

| Constante | Significado | ¿Escrita en el manual? |
|---|---|---|
| `network_type_connect` | Alguien se ha conectado | ✅ |
| `network_type_disconnect` | Alguien se ha desconectado | ✅ |
| `network_type_data` | Han llegado datos | ✅ |
| `network_type_non_blocking_connect` | Conexión no bloqueante establecida | ✅ |
| **`network_type_up`** | La interfaz de red **ha subido** | ❌ |
| **`network_type_down`** | La interfaz de red **se ha caído** | ❌ |
| **`network_type_up_failed`** | La interfaz **no ha podido subir** | ❌ |

**Modo de conexión del socket:**

`network_connect_none`, `network_connect_blocking`, `network_connect_nonblocking`,
`network_connect_active`, `network_connect_passive`, `network_connect_async`,
`network_connect_raw`, `network_connect_raw_async` — de las ocho, las **tres primeras** no
están escritas en el manual.

**Configuración** (`network_set_config`): entre las nueve constantes,
**`network_config_enable_multicast`** y **`network_config_disable_multicast`** no aparecen.

> 💡 Las tres de `network_type_up/down/up_failed` son útiles de verdad: permiten detectar que
> el jugador ha perdido el wifi **sin esperar a que caduque un temporizador**.

---

## 6 · Códigos de error de búfer

`buffer_error_general`, `buffer_error_invalid_type`, `buffer_error_out_of_space`. **Ninguno
está escrito en el manual**, aunque son lo que devuelve el sistema cuando una operación con
búferes falla.

```gml
/// comprobar por qué falló una escritura
try {
    buffer_write(_buf, buffer_u8, 300);   // 300 no cabe en un u8
} catch (_e) {
    show_debug_message($"error de búfer: {_e.message}");
}
```

---

## 7 · Tipos de elemento de capa

De los diez `layerelementtype_*`, dos no están escritos:

- **`layerelementtype_undefined`** — lo devuelve `layer_get_element_type()` cuando el ID que
  le pasas no corresponde a ningún elemento. **Es el valor que debes comprobar** antes de
  fiarte del resultado.
- **`layerelementtype_oldtilemap`** — el formato de tiles anterior a GameMaker Studio 2.
  No lo vas a producir; puede aparecer al importar un proyecto muy antiguo.

```gml
var _tipo = layer_get_element_type(_id);
if (_tipo == layerelementtype_undefined) {
    show_debug_message("ese ID no es un elemento de capa");
    exit;
}
```

---

## 8 · Interpolación de secuencias y sistemas operativos

- **`seqinterpolation_assign`** — el valor salta de un fotograma clave al siguiente, sin
  transición (útil para conmutar sprites o visibilidad).
- **`seqinterpolation_lerp`** — interpolación lineal entre fotogramas clave. Es el
  comportamiento habitual.

Y dos constantes de plataforma sin escribir en el manual: **`os_gdk`** (Microsoft Game
Development Kit, la vía moderna de publicar en Xbox y en PC de Microsoft Store) y
**`os_switch2`** (la segunda generación de Nintendo Switch).

```gml
switch (os_type) {
    case os_windows:  break;
    case os_gdk:      break;    // Xbox / Microsoft Store
    case os_switch:   break;
    case os_switch2:  break;
}
```

> 🔺 **`os_operagx` tampoco está en el manual**, aunque sí se menciona en alguna página; ver
> [20 · Lo que el manual no documenta](./20%20-%20Lo%20que%20el%20manual%20no%20documenta.md).

---

## 9 · Macros del compilador: `_GMFILE_`, `_GMLINE_`, `_GMFUNCTION_`

Tres constantes que el compilador sustituye **en tiempo de compilación**, no de ejecución.
No están escritas en el manual y son inmediatamente útiles para depurar:

| Constante | Tipo | Contiene |
|---|---|---|
| `_GMFILE_` | `String` | El archivo donde aparece |
| `_GMLINE_` | `Real` | La línea donde aparece |
| `_GMFUNCTION_` | `String` | La función donde aparece |

```gml
/// un log que se sitúa solo
function log(_texto) {
    show_debug_message($"[{_GMFILE_}:{_GMLINE_}] {_texto}");
}

/// una aserción que dice dónde ha saltado
function afirmar(_cond, _mensaje = "aserción fallida") {
    if (!_cond) {
        show_debug_message($"✗ {_mensaje} — {_GMFUNCTION_}() en {_GMFILE_}:{_GMLINE_}");
    }
}
```

> ⚠️ **Se sustituyen donde están escritas, no donde se llama la función.** Si metes `_GMLINE_`
> dentro de `log()`, siempre dará la línea de `log()`, no la de quien la llamó. Para que sea
> útil, pásalo como argumento desde el sitio de la llamada:
>
> ```gml
> log($"vida = {hp}", _GMLINE_);
> ```

---

## 10 · Las 173 constantes de evento (`ev_*`) para `event_perform`

`event_perform(tipo, número)` ejecuta un evento de un objeto por código. El `tipo` y el
`número` son constantes `ev_*`, y hay **173**. El manual las agrupa por familias, así que muchas
no se escriben una a una. Estas son las familias, con cuántas constantes tiene cada una:

| Familia | Nº | Para qué |
|---|---|---|
| `ev_joystick*` | 24 | Eventos de joystick (heredados) |
| `ev_global*` | 22 | Ratón/teclado **global** (`ev_global_left_button`…) — se disparan pases lo que pases por encima |
| `ev_user0` … `ev_user15` | 16 | **Eventos de usuario**: los defines tú, los lanzas con `event_perform(ev_other, ev_user0)` |
| `ev_gesture*` | 14 | Gestos táctiles (ver [12 · Input §8 bis](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md)) |
| `ev_async*` | 14 | Eventos asíncronos (HTTP, guardado, imagen cargada, audio…) |
| `ev_outside_view0..7` / `ev_boundary_view0..7` | 9+9 | Salir/tocar el borde de cada vista (ver §3) |
| `ev_web*` | 7 | Específicos de HTML5 |
| `ev_draw*` | 6 | `ev_draw`, `ev_draw_begin`, `ev_draw_end`, `ev_gui`… |
| `ev_mouse*` | 5 | Ratón sobre la instancia |
| `ev_step*` | 4 | `ev_step`, `ev_step_begin`, `ev_step_end`, `ev_step_normal` |

```gml
/// disparar un evento de usuario por código (patrón muy útil)
event_perform(ev_other, ev_user0);      // ejecuta el "User Event 0" de esta instancia

/// forzar el Step de otro objeto
with (obj_enemigo) event_perform(ev_step, ev_step_normal);
```

> 💡 **Los eventos de usuario (`ev_user0..15`) son tu herramienta para organizar lógica.** En
> vez de una función enorme en Step, pones trozos en User Events y los llamas cuando toca. Es
> como tener «métodos» en un objeto sin escribir un struct.
>
> 🔺 **La lista completa**, con el número exacto de cada constante:
> `python3 _indice/buscar.py --listar ev_`. No las escribas de memoria: `ev_close_button`,
> `ev_room_start`, `ev_game_start` y compañía tienen nombres que se confunden.

📘 [`event_perform`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Objects/Object_Events/event_perform.md)

---

## Cómo se detectaron

No se buscaron a mano. El procedimiento fue:

1. Extraer los 3486 símbolos del `GmlSpec.xml` del runtime instalado.
2. Descartar los obsoletos.
3. Descartar los que tienen página propia en el manual español.
4. Descartar los que se **mencionan** en el texto de alguna de las 3142 páginas.
5. Descartar los que ya explica algún documento de esta biblioteca.
6. Lo que queda son los invisibles: **eran 87**, bajaron a **47** al completar la traducción
   del manual, y esos 47 son los que documenta esta página.

`_indice/actualizar.py` repite ese cálculo en cada ejecución, así que si un runtime nuevo
añade símbolos, aparecerán aquí como pendientes en vez de pasar desapercibidos.

---

## Ver también

- [20 · Lo que el manual no documenta](./20%20-%20Lo%20que%20el%20manual%20no%20documenta.md) — el recuento completo y la metodología
- [12 · Input — teclado, ratón y gamepad](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md) — los botones de mando que sí están documentados
- [14 · Multijugador](../04%20-%20Recetas%20por%20género/14%20-%20Multijugador.md) — dónde se usan las constantes de red
- [15 · Depuración y rendimiento](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md)
