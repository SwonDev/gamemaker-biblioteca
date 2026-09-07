# 25 · Menú de opciones y ajustes

> La pantalla de Opciones: volumen con sliders, pantalla completa con un toggle, idioma y
> resolución con dropdowns, reasignar controles, y un botón «Aplicar». La navegación de listas
> ya la resuelve [18 · Menús con scroll](./18%20-%20Menús%20con%20scroll%20y%20navegación.md);
> aquí montamos los **widgets** y su persistencia.
>
> **Cobertura parcial detectada:** el volumen, el guardado en INI, la resolución y el rebinding
> estaban en documentos distintos. Este los une en una pantalla.

---

## Los ajustes son datos (otra vez)

Como el menú, la pantalla de opciones es una lista de widgets descritos por datos. Cada uno
sabe leerse, cambiarse y dibujarse.

```gml
/// obj_opciones · Create
ajustes = [
    { tipo: "slider",   clave: "volumen_musica", etiqueta: txt("op_musica"), val: 0.8, min: 0, max: 1 },
    { tipo: "slider",   clave: "volumen_sfx",    etiqueta: txt("op_sfx"),    val: 1.0, min: 0, max: 1 },
    { tipo: "toggle",   clave: "pantalla_completa", etiqueta: txt("op_fullscreen"), val: false },
    { tipo: "dropdown", clave: "idioma", etiqueta: txt("op_idioma"),
      val: 0, opciones: ["Español", "English", "Français"], codigos: ["es", "en", "fr"] },
    { tipo: "boton",    clave: "controles", etiqueta: txt("op_controles"), accion: abrir_rebinding },
];
seleccion = 0;
```

---

## 1 · Los widgets: leer y cambiar

```gml
/// obj_opciones · Step — izquierda/derecha cambian el valor del widget marcado
var _w = ajustes[seleccion];
var _izq = keyboard_check_pressed(vk_left)  || gamepad_button_check_pressed(0, gp_padl);
var _der = keyboard_check_pressed(vk_right) || gamepad_button_check_pressed(0, gp_padr);

switch (_w.tipo) {
    case "slider":
        if (_izq) _w.val = clamp(_w.val - 0.1, _w.min, _w.max);
        if (_der) _w.val = clamp(_w.val + 0.1, _w.min, _w.max);
        aplicar_ajuste(_w);            // en vivo: oyes el volumen mientras lo mueves
        break;
    case "toggle":
        if (_izq || _der) { _w.val = !_w.val; aplicar_ajuste(_w); }
        break;
    case "dropdown":
        var _n = array_length(_w.opciones);
        if (_izq) _w.val = (_w.val - 1 + _n) mod _n;
        if (_der) _w.val = (_w.val + 1) mod _n;
        if (_izq || _der) aplicar_ajuste(_w);
        break;
    case "boton":
        if (keyboard_check_pressed(vk_enter)) _w.accion();
        break;
}
```

---

## 2 · Aplicar de verdad cada ajuste

```gml
function aplicar_ajuste(_w) {
    switch (_w.clave) {
        case "volumen_musica":
            audio_group_set_gain(agrupo_musica, _w.val, 0);  break;
        case "volumen_sfx":
            audio_group_set_gain(agrupo_sfx, _w.val, 0);     break;
        case "pantalla_completa":
            window_set_fullscreen(_w.val);                   break;
        case "idioma":
            cambiar_idioma(_w.codigos[_w.val]);              break;   // ver receta 21
    }
}
```

> 💡 **Aplica en vivo, no al salir.** Que el jugador oiga el volumen mientras mueve el slider y
> vea la pantalla completa al instante. Un menú de opciones que solo aplica al pulsar «Guardar»
> se siente roto.
>
> 🔺 **`audio_group_set_gain(grupo, ganancia, tiempo)`** ajusta el volumen de un grupo de audio
> entero (música, efectos) — mejor que `audio_master_gain`, que afecta a todo por igual. Ver
> [13 · Audio](../01%20-%20Fundamentos/13%20-%20Audio.md).

---

## 3 · Dibujar los widgets

```gml
/// obj_opciones · Draw GUI
var _x = 200, _y = 120, _paso = 48;
for (var _i = 0; _i < array_length(ajustes); _i++) {
    var _w = ajustes[_i];
    var _wy = _y + _i * _paso;
    var _col = (_i == seleccion) ? c_yellow : c_white;

    draw_text_color(_x, _wy, _w.etiqueta, _col, _col, _col, _col, 1);

    switch (_w.tipo) {
        case "slider":
            // barra de fondo + relleno proporcional
            draw_rectangle_color(_x+220, _wy+8, _x+420, _wy+20, c_dkgray,c_dkgray,c_dkgray,c_dkgray, false);
            draw_rectangle_color(_x+220, _wy+8, _x+220 + 200*_w.val, _wy+20, _col,_col,_col,_col, false);
            break;
        case "toggle":
            draw_text_color(_x+220, _wy, _w.val ? txt("op_si") : txt("op_no"), _col,_col,_col,_col, 1);
            break;
        case "dropdown":
            draw_text_color(_x+220, _wy, "< " + _w.opciones[_w.val] + " >", _col,_col,_col,_col, 1);
            break;
    }
}
```

---

## 4 · Guardar y cargar los ajustes

```gml
/// al salir de Opciones — persistir todo en un INI
function guardar_ajustes() {
    ini_open("ajustes.ini");
    for (var _i = 0; _i < array_length(ajustes); _i++) {
        var _w = ajustes[_i];
        if (_w.tipo == "boton") continue;
        ini_write_real("opciones", _w.clave, is_bool(_w.val) ? (_w.val ? 1 : 0) : _w.val);
    }
    ini_close();
}

/// al arrancar el juego — leerlos y aplicarlos
function cargar_ajustes() {
    ini_open("ajustes.ini");
    for (var _i = 0; _i < array_length(ajustes); _i++) {
        var _w = ajustes[_i];
        if (_w.tipo == "boton") continue;
        _w.val = ini_read_real("opciones", _w.clave, _w.val);   // por defecto, lo que ya tenía
        aplicar_ajuste(_w);
    }
    ini_close();
}
```

> ⚠️ **Carga y aplica los ajustes al ARRANCAR, en `rm_init`, no al abrir Opciones.** Si el
> jugador puso el volumen al 30 %, el juego debe arrancar al 30 %, aunque nunca abra Opciones
> esa sesión. Ver el orden de sistemas globales en
> [00 · Anatomía de un juego completo](./00%20-%20Anatomía%20de%20un%20juego%20completo.md).

---

## 5 · Reasignar controles (rebinding)

El remapeo de controles es pauta **Basic** de las Game Accessibility Guidelines —*«Allow
controls to be remapped / reconfigured»*, ya citada por
[04 · 40](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md#fuentes)— y
requisito de certificación en las tres consolas de sobremesa: un esbozo de doce líneas no basta.
Esta sección monta el mecanismo completo: capturar tecla, botón de mando y eje; detectar y
resolver conflictos entre acciones; perfiles de teclado y de mando; restablecer con
confirmación; y guardarlo todo en `ajustes.ini`. Al final se sigue recomendando la librería
**Input**, pero ya con el problema entendido, no como atajo para no entenderlo.

### 5.1 Una sola forma de datos, la que ya usa el tutorial

**No hay una estructura de rebinding y otra de prompts: es la misma**, y eso no es casualidad —
es lo único que permite que un *prompt* («pulsa E para abrir») dibuje la tecla que el jugador
asignó de verdad y no la de fábrica. [04 · 40 §2.4](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md#24-el-widget-de-prompts-la-asignación-real-no-la-de-fábrica)
y [§3.5](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md#35-scr_controles--la-asignación-real-de-cada-acción)
ya definen esa estructura y sus funciones de acceso — **no se repiten aquí**, se usan:

```gml
// Definida en 04/40 §3.5 — scr_controles.gml. Un vistazo, no una copia:
global.controles = {
    saltar:      { teclado: vk_space,   mando: gp_face1 },
    dash:        { teclado: vk_shift,   mando: gp_shoulderr },
    atacar:      { teclado: ord("F"),   mando: gp_face3 },
    interactuar: { teclado: ord("E"),   mando: gp_face2 },
    abrir_ayuda: { teclado: vk_f1,      mando: gp_select },
};
// controles_iniciar()        — valores de fábrica
// control_asignar_teclado()  — escribe .teclado con la comprobación defensiva de struct_exists
// control_asignar_mando()    — escribe .mando
// control_tecla() / control_boton_mando() — lectura segura (vk_nokey / -1 si la acción no existe)
```

Esta sección **añade** tres piezas que 04/40 no necesitaba para su ejemplo (ninguna de sus
acciones — saltar, dash, atacar, interactuar, abrir ayuda — es analógica): un campo `eje`
opcional por acción, la captura en sí, y el guardado. Lo hace **sin tocar** la forma existente:
`eje`/`eje_signo` se añaden de forma perezosa, igual que `control_asignar_mando()` ya añade
`.mando` a una entrada que solo tenía `.teclado` — así que ningún código que ya lea
`.teclado`/`.mando` (empezando por `prompt_boton()` de 04/40 §3.6) se entera del cambio.

```gml
// ============================================================================
// Ampliación de scr_controles.gml — SOLO lo que 04/40 §3.5 no cubre: el eje.
// Verificado: struct_exists
// ============================================================================

/// @func control_asignar_eje(_accion, _eje, _signo)
/// @desc _eje es un índice de eje de mando (0..gamepad_axis_count()-1, incluye las
///       constantes gp_axislh/lv/rh/rv); _signo es +1 o -1 — la MITAD del eje que
///       dispara la acción (empujar el stick arriba no es lo mismo que abajo).
function control_asignar_eje(_accion, _eje, _signo) {
    if (!struct_exists(global.controles, _accion)) global.controles[$ _accion] = { teclado: vk_nokey, mando: -1 };
    global.controles[$ _accion].eje       = _eje;
    global.controles[$ _accion].eje_signo = _signo;
}

/// @func control_eje(_accion)
/// @returns {Real} -1 si la acción no existe o no tiene eje asignado.
function control_eje(_accion) {
    return struct_exists(global.controles, _accion) ? (global.controles[$ _accion][$ "eje"] ?? -1) : -1;
}

/// @func control_eje_signo(_accion)
/// @returns {Real} +1 por defecto (no revienta si la acción aún no tiene eje).
function control_eje_signo(_accion) {
    return struct_exists(global.controles, _accion) ? (global.controles[$ _accion][$ "eje_signo"] ?? 1) : 1;
}
```

> 🔺 **`[$ "eje"] ?? -1` es el mismo patrón que ya usa `enemigo_crear()` en
> [13 · 06 §3.8](<../13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md#38-datos-dirigidos-definir-el-juego-en-json>)
> con `_def[$ "sueltas"] ?? []`**: leer un campo que puede no existir sin que
> `struct_exists()` lo obligue a comprobarse dos veces.

### 5.2 El modo «esperando entrada»: tecla, botón de mando y eje

El esbozo original leía `keyboard_lastkey` sin más. Aquí se generaliza a un **estado**, porque
teclado, botón y eje se capturan de formas distintas y las tres necesitan poder cancelarse y
detectar conflicto antes de escribir nada:

```gml
// ============================================================================
// El modo "esperando entrada" — un solo global.rebind, tres formas de leerlo.
// Verificado: keyboard_lastkey, keyboard_check_pressed, vk_nokey, vk_escape,
//             gamepad_button_check_pressed, gamepad_axis_count, gamepad_axis_value,
//             abs, sign, delta_time, is_undefined, struct_get_names, array_length
// ============================================================================

#macro REBIND_TIMEOUT_SEG 6     // se cancela solo si nadie pulsa nada (mando sin teclado)
#macro REBIND_UMBRAL_EJE  0.6   // más alto que cualquier deriva del stick en reposo

/// @func rebind_iniciar(_accion, _campo)
/// @desc Entra en el modo de captura. Llamar desde el botón "Cambiar" de una fila.
/// @param {String} _accion  Clave de global.controles.
/// @param {String} _campo   "teclado" | "mando" | "eje"
function rebind_iniciar(_accion, _campo) {
    global.rebind = {
        accion: _accion, campo: _campo, tiempo: 0,
        conflicto: "", valor_pendiente: undefined, foco_confirmacion: 0,
    };
    keyboard_lastkey = vk_nokey;   // descarta la tecla que abrió el propio menú de rebinding
}

/// obj_opciones · pantalla == "controles" · Step — SOLO si hay una captura en curso
function rebind_actualizar() {
    if (is_undefined(global.rebind)) return;
    var _r = global.rebind;

    // Hay un conflicto esperando "¿reasignar? Sí/No": no sigas leyendo entrada nueva (§5.3)
    if (_r.conflicto != "") { __rebind_resolver_confirmacion(_r); return; }

    _r.tiempo += delta_time / 1000000;
    if (keyboard_check_pressed(vk_escape) || _r.tiempo > REBIND_TIMEOUT_SEG) {
        global.rebind = undefined;   // cancelado: nada se escribe
        return;
    }

    switch (_r.campo) {
        case "teclado": __rebind_capturar_teclado(_r); break;
        case "mando":   __rebind_capturar_mando(_r);   break;
        case "eje":     __rebind_capturar_eje(_r);     break;
    }
}

/// __rebind_capturar_teclado(_r) — uso interno
function __rebind_capturar_teclado(_r) {
    var _tecla = keyboard_lastkey;
    if (_tecla == vk_nokey || _tecla == vk_escape) return;   // Esc ya cancela arriba
    if (!keyboard_check_pressed(_tecla)) return;
    keyboard_lastkey = vk_nokey;                              // consumida: no la veas dos veces

    var _choque = control_buscar_conflicto(_r.accion, "teclado", _tecla);
    if (_choque != "") { _r.conflicto = _choque; _r.valor_pendiente = _tecla; return; }

    control_asignar_teclado(_r.accion, _tecla);   // 04/40 §3.5 — no se reescribe, se usa
    global.rebind = undefined;
}

/// __rebind_capturar_mando(_r) — uso interno
function __rebind_capturar_mando(_r) {
    // La misma lista de botones digitales que 13/05 §2.3 usa en __ui_mando_activo()
    static BOTONES = [gp_face1, gp_face2, gp_face3, gp_face4, gp_padu, gp_padd, gp_padl,
                      gp_padr, gp_shoulderl, gp_shoulderr, gp_shoulderlb, gp_shoulderrb,
                      gp_start, gp_select, gp_stickl, gp_stickr];

    for (var _i = 0; _i < array_length(BOTONES); _i++) {
        if (!gamepad_button_check_pressed(global.mando_slot, BOTONES[_i])) continue;

        var _boton  = BOTONES[_i];
        var _choque = control_buscar_conflicto(_r.accion, "mando", _boton);
        if (_choque != "") { _r.conflicto = _choque; _r.valor_pendiente = _boton; }
        else { control_asignar_mando(_r.accion, _boton); global.rebind = undefined; }
        return;   // un botón por fotograma basta
    }
}

/// __rebind_capturar_eje(_r) — uso interno
function __rebind_capturar_eje(_r) {
    var _n = gamepad_axis_count(global.mando_slot);
    for (var _a = 0; _a < _n; _a++) {
        var _valor = gamepad_axis_value(global.mando_slot, _a);
        if (abs(_valor) < REBIND_UMBRAL_EJE) continue;

        var _signo  = sign(_valor);
        var _choque = control_buscar_conflicto(_r.accion, "eje", [_a, _signo]);
        if (_choque != "") { _r.conflicto = _choque; _r.valor_pendiente = [_a, _signo]; }
        else { control_asignar_eje(_r.accion, _a, _signo); global.rebind = undefined; }
        return;
    }
}
```

```gml
/// obj_opciones · Draw GUI — overlay de captura, por encima de la lista de opciones
if (!is_undefined(global.rebind)) {
    var _r  = global.rebind;
    var _gw = display_get_gui_width(), _gh = display_get_gui_height();

    draw_set_alpha(0.75); draw_set_colour(c_black);
    draw_rectangle(0, 0, _gw, _gh, false);
    draw_set_alpha(1); draw_set_colour(c_white);
    draw_set_halign(fa_center);

    if (_r.conflicto != "") {
        draw_text(_gw/2, _gh/2 - 20, string_replace(txt("rebind_conflicto"),
                   "{accion}", txt($"accion_{_r.conflicto}")));
        draw_text_color(_gw/2 - 60, _gh/2 + 20, txt("comun_no"),
                   _r.foco_confirmacion == 0 ? c_white : c_gray,
                   _r.foco_confirmacion == 0 ? c_white : c_gray,
                   _r.foco_confirmacion == 0 ? c_white : c_gray,
                   _r.foco_confirmacion == 0 ? c_white : c_gray, 1);
        draw_text_color(_gw/2 + 60, _gh/2 + 20, txt("comun_si"),
                   _r.foco_confirmacion == 1 ? c_white : c_gray,
                   _r.foco_confirmacion == 1 ? c_white : c_gray,
                   _r.foco_confirmacion == 1 ? c_white : c_gray,
                   _r.foco_confirmacion == 1 ? c_white : c_gray, 1);
    } else {
        // GML no encadena ternarios sin paréntesis (ver 01/If_Else_and_Conditional_Operators
        // §Operadores ternarios): el segundo `?:` va envuelto en su propio paréntesis.
        var _msg = (_r.campo == "teclado") ? txt("rebind_pulsa_tecla")
                 : ((_r.campo == "mando")  ? txt("rebind_pulsa_boton")
                                           : txt("rebind_mueve_eje"));
        draw_text(_gw/2, _gh/2 - 10, _msg);
        draw_text(_gw/2, _gh/2 + 20, txt("rebind_cancelar_esc"));
    }
    draw_set_halign(fa_left);
}
```

> ⚠️ **`keyboard_lastkey` no es de solo lectura** — el propio manual lo dice y ya lo aprovechaba
> el esbozo original: se pone a `vk_nokey` justo después de leerla para que el siguiente
> fotograma no la vuelva a ver. `rebind_iniciar()` hace lo mismo al ENTRAR en el modo, por la
> misma razón: la tecla que el jugador pulsó para abrir "Cambiar" no debe colarse como la nueva
> tecla asignada.
>
> 💡 **El tiempo de espera (`REBIND_TIMEOUT_SEG`) no es solo comodidad**: es la única salida para
> quien está remapeando solo con mando y no tiene Esc a mano si algo se queda colgado. Sin él,
> una captura fallida deja el menú inservible hasta reiniciar.

### 5.3 Detección y resolución de conflictos

Ninguna de las GAG lo pide explícitamente, pero es la mitad del trabajo real del rebinding: sin
esto, asignar "atacar" a la misma tecla que "saltar" dispara las dos acciones a la vez y el
jugador cree que el juego falla.

```gml
/// @func control_buscar_conflicto(_accion, _campo, _valor)
/// @desc ¿Ya usa OTRA acción este mismo valor en el mismo campo? _accion se excluye
///       de la búsqueda a propósito: reasignar una tecla a la acción que YA la tiene
///       no es un conflicto, es un no-op.
/// @param {String} _accion
/// @param {String} _campo   "teclado" | "mando" | "eje"
/// @param          _valor   vk_* / gp_* si _campo es teclado o mando; [eje, signo] si es eje
/// @returns {String} el nombre de la acción en conflicto, o "" si no hay ninguna
function control_buscar_conflicto(_accion, _campo, _valor) {
    var _nombres = struct_get_names(global.controles);
    for (var _i = 0; _i < array_length(_nombres); _i++) {
        var _n = _nombres[_i];
        if (_n == _accion) continue;
        var _c = global.controles[$ _n];

        switch (_campo) {
            case "teclado":
                if (_c.teclado == _valor) return _n;
                break;
            case "mando":
                if (_c.mando == _valor) return _n;
                break;
            case "eje":
                if ((_c[$ "eje"] ?? -1) == _valor[0] && (_c[$ "eje_signo"] ?? 1) == _valor[1]) return _n;
                break;
        }
    }
    return "";
}

/// __rebind_resolver_confirmacion(_r) — uso interno, llamado por rebind_actualizar()
/// mientras _r.conflicto != "". Mismo patrón de "No por defecto" que la confirmación
/// de salir de 04/41 §3.4.4, con los widgets de entrada propios de esta pantalla (§1).
function __rebind_resolver_confirmacion(_r) {
    var _izq = keyboard_check_pressed(vk_left)  || gamepad_button_check_pressed(global.mando_slot, gp_padl);
    var _der = keyboard_check_pressed(vk_right) || gamepad_button_check_pressed(global.mando_slot, gp_padr);
    if (_izq || _der) _r.foco_confirmacion = 1 - _r.foco_confirmacion;

    var _ok = keyboard_check_pressed(vk_enter) || gamepad_button_check_pressed(global.mando_slot, gp_face1);
    if (keyboard_check_pressed(vk_escape)) { global.rebind = undefined; return; }   // cancelar también aquí
    if (!_ok) return;

    if (_r.foco_confirmacion == 1) {   // "Sí": se lo quitas a quien lo tenía y se lo das al nuevo
        switch (_r.campo) {
            case "teclado":
                control_asignar_teclado(_r.conflicto, vk_nokey);
                control_asignar_teclado(_r.accion, _r.valor_pendiente);
                break;
            case "mando":
                control_asignar_mando(_r.conflicto, -1);
                control_asignar_mando(_r.accion, _r.valor_pendiente);
                break;
            case "eje":
                control_asignar_eje(_r.conflicto, -1, 1);
                control_asignar_eje(_r.accion, _r.valor_pendiente[0], _r.valor_pendiente[1]);
                break;
        }
    }
    // "No": no se toca nada — la captura se descarta y la acción conserva lo que ya tenía
    global.rebind = undefined;
}
```

> ⚠️ **Dejar una acción sin tecla ni botón (`vk_nokey` / `-1`) es un estado válido**, no un bug:
> es justo lo que le pasa a la acción perdedora de un "Sí" en el conflicto. `control_tecla()` y
> `control_boton_mando()` (04/40 §3.5) ya devuelven ese valor de forma segura; lo único que hay
> que decidir es cómo se dibuja — `control_nombre_teclado()` (04/40 §3.6) no tiene una entrada
> para `vk_nokey`, así que cae a su rango A-Z/0-9 o a `"?"`: dale una entrada propia
> (`txt("rebind_sin_asignar")`) si te importa distinguir "sin asignar" de "tecla rara".

### 5.4 Perfiles: teclado / mando 1 / mando 2

`global.controles` guarda **una** asignación de mando por acción, no tres — el mismo modelo de
un solo dispositivo activo que ya usa `global.ui_dispositivo` en
[13 · 05 §2.3](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#23-ratón-táctil-y-mando-a-la-vez-manda-el-último-dispositivo-usado>).
Lo que cambia con el perfil no es una copia distinta del mapa de botones: es **de qué ranura
física** (`device`, el primer argumento de toda función `gamepad_*`) lee la captura y la
partida en curso.

```gml
/// @func mando_slot_fijar(_slot)
/// @desc Cambia qué ranura de mando alimenta .mando/.eje. "Mando 1" = ranura 0,
///       "Mando 2" = ranura 1 — útil cuando hay dos mandos conectados y el jugador
///       quiere usar el que tiene cargado, no necesariamente el primero detectado.
function mando_slot_fijar(_slot) {
    global.mando_slot = clamp(_slot, 0, max(0, gamepad_get_device_count() - 1));
}
```

```gml
/// obj_opciones · Create (al entrar en la pantalla de controles)
global.mando_slot ??= 0;          // por si esta pantalla se abre antes que dispositivo_iniciar()
perfil_activo          = "teclado";   // "teclado" | "mando1" | "mando2"
seleccion_control       = 0;
confirmando_restablecer = false;
foco_confirmacion_reset = 0;

/// obj_opciones · pantalla == "controles" · Step — cambiar de pestaña
var _tab_izq = keyboard_check_pressed(ord("Q")) || gamepad_button_check_pressed(global.mando_slot, gp_shoulderl);
var _tab_der = keyboard_check_pressed(ord("E")) || gamepad_button_check_pressed(global.mando_slot, gp_shoulderr);

if (_tab_izq || _tab_der) {
    static PERFILES = ["teclado", "mando1", "mando2"];
    var _idx = 0;
    for (var _i = 0; _i < array_length(PERFILES); _i++) {
        if (PERFILES[_i] == perfil_activo) { _idx = _i; break; }
    }
    _idx = _tab_der ? (_idx + 1) mod array_length(PERFILES) : (_idx - 1 + array_length(PERFILES)) mod array_length(PERFILES);
    perfil_activo = PERFILES[_idx];
    if (perfil_activo != "teclado") mando_slot_fijar(perfil_activo == "mando2" ? 1 : 0);
}

/// al pulsar "Cambiar" en la fila de una acción — qué campo se captura según la pestaña
var _campo = (perfil_activo == "teclado") ? "teclado" : "mando";
rebind_iniciar(nombre_accion_seleccionada, _campo);
// y un botón aparte, "Cambiar eje", solo en las filas de las acciones que lo admitan
// (típicamente movimiento o cámara — decídelo tú, 04/40 no trae ninguna analógica de ejemplo):
// rebind_iniciar(nombre_accion_seleccionada, "eje");
```

> ⚠️ **Esto NO es multijugador local independiente.** "Mando 1" y "Mando 2" seleccionan de qué
> ranura física lee la partida — siguen escribiendo en el mismo `global.controles`, porque el
> modelo entero de esta receta (y el de 04/40) es de **un** jugador con **un** dispositivo activo
> a la vez. Un splitscreen de verdad, con esquemas independientes por jugador, necesita un
> `global.controles` por jugador (un array o un struct indexado por número de jugador) — fuera
> del alcance de esta sección; el punto de partida está en
> [04 · 14 § Antes de empezar, en serio](./14%20-%20Multijugador.md#antes-de-empezar-en-serio)
> y en el ejemplo de `objPlayer2` de
> [04 · 02 §8, punto «Local co-op»](./02%20-%20Top-Down%20_%20Twin-Stick.md#8-cómo-escalarlo).
>
> 💡 **Por qué Q/E y hombros, no flechas**: las flechas ya navegan la lista de acciones (§1). Un
> segundo par de entradas para las pestañas evita que cambiar de fila y cambiar de perfil
> compartan el mismo gesto.

### 5.5 Restablecer valores de fábrica, con confirmación

`controles_iniciar()` (04/40 §3.5) ya vuelve a los valores de fábrica — lo que faltaba es el
guardarraíl: es una acción destructiva y la regla ya está fijada en
[13 · 05 §2.1, punto 3](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#21--el-mapa-de-pantallas-se-dibuja-antes-de-programar-nada>)
(«restablecer controles» es justo el ejemplo que cita esa regla): **toda acción destructiva
confirma, y el botón por defecto es "No"**. Mismo mecanismo que la confirmación de salir de
[04 · 41 §3.4.4](./41%20-%20Transiciones,%20carga%20y%20pausa.md#344-seguro-que-quieres-salir--con-no-por-defecto-sin-show_question),
adaptado a los propios widgets de esta pantalla (nada de `show_question()`: bloquea el juego y
se ignora fuera de Windows fuera de modo debug, como ya advierte
[01 · 15](../01%20-%20Fundamentos/15%20-%20Depuración%20y%20rendimiento.md)):

```gml
/// obj_opciones · pantalla == "controles" · Step — botón "Restablecer todo" de la fila
if (boton_restablecer_pulsado()) confirmando_restablecer = true;   // tu propia comprobación de Enter

/// obj_opciones · pantalla == "controles" · Step — mientras confirmando_restablecer == true
if (confirmando_restablecer) {
    var _izq = keyboard_check_pressed(vk_left)  || gamepad_button_check_pressed(global.mando_slot, gp_padl);
    var _der = keyboard_check_pressed(vk_right) || gamepad_button_check_pressed(global.mando_slot, gp_padr);
    if (_izq || _der) foco_confirmacion_reset = 1 - foco_confirmacion_reset;

    if (keyboard_check_pressed(vk_enter) || gamepad_button_check_pressed(global.mando_slot, gp_face1)) {
        if (foco_confirmacion_reset == 1) {   // "Sí"
            controles_iniciar();               // 04/40 §3.5 — vuelve a los valores de fábrica
            controles_guardar();               // y se persiste YA (§5.6): no esperes a salir de Opciones
        }
        confirmando_restablecer = false;
        foco_confirmacion_reset = 0;           // otra vez "No" para la próxima
    } else if (keyboard_check_pressed(vk_escape)) {
        confirmando_restablecer = false;
        foco_confirmacion_reset = 0;
    }
}
```

```gml
/// @func dibujar_confirmacion_restablecer(_gw, _gh)
/// @desc Mismo patrón visual que dibujar_confirmacion_salir() de 04/41 §3.4.4.
function dibujar_confirmacion_restablecer(_gw, _gh) {
    var _pw = 420, _ph = 160;
    var _px = (_gw - _pw) / 2, _py = (_gh - _ph) / 2;

    draw_set_colour(c_black);
    draw_rectangle(_px, _py, _px + _pw, _py + _ph, false);
    draw_set_halign(fa_center);
    draw_text(_gw / 2, _py + 32, txt("opciones_confirmar_restablecer"));

    draw_text_color(_gw/2 - 80, _py + _ph - 40, txt("comun_no"),
                     foco_confirmacion_reset == 0 ? c_white : c_gray,
                     foco_confirmacion_reset == 0 ? c_white : c_gray,
                     foco_confirmacion_reset == 0 ? c_white : c_gray,
                     foco_confirmacion_reset == 0 ? c_white : c_gray, 1);
    draw_text_color(_gw/2 + 80, _py + _ph - 40, txt("comun_si"),
                     foco_confirmacion_reset == 1 ? c_white : c_gray,
                     foco_confirmacion_reset == 1 ? c_white : c_gray,
                     foco_confirmacion_reset == 1 ? c_white : c_gray,
                     foco_confirmacion_reset == 1 ? c_white : c_gray, 1);
    draw_set_halign(fa_left);
}
```

> 💡 **Ofrece también "restablecer solo esta acción"**, fila por fila, sin confirmación (el coste
> de un error es una tecla, no doce): `control_asignar_teclado(_accion, _tecla_de_fabrica)`
> leyendo de una copia congelada de los valores que puso `controles_iniciar()` al arrancar, antes
> de que el jugador tocara nada.

### 5.6 Guardar y cargar: en `ajustes.ini`, según la clase de dato de 13/06 §3.10

La tabla de
[13 · 06 §3.10](<../13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md#310-estado-global-guardado-y-migraciones>)
clasifica el rebinding sin ambigüedad: es **Configuración** («preferencias del jugador, no del
personaje»), en el mismo fichero que el volumen y el idioma, escrito al cambiarlo — nunca en el
guardado de partida (`partida_N.json`), donde se perdería al borrar un *slot* y donde no tiene
ningún sentido que dependa de él. Esta receta ya usa `ajustes.ini` desde §4 para el resto de
ajustes: el rebinding va al mismo fichero, en su propia sección.

```gml
// ============================================================================
// Persistencia del rebinding — misma clase de dato que §4, otra sección del INI.
// Verificado: ini_open, ini_close, ini_write_string, ini_write_real, ini_read_string,
//             ini_read_real, ini_key_exists, struct_get_names, array_length, json_stringify,
//             json_parse
// ============================================================================

/// @func controles_guardar()
/// @desc Llamar junto a guardar_ajustes() (§4): al pulsar "Aplicar"/"Guardar" en Opciones,
///       y también nada más confirmar un "Restablecer todo" (§5.5), para que no se pierda
///       si el jugador cierra el juego sin volver a pasar por Opciones.
function controles_guardar() {
    ini_open("ajustes.ini");
    var _nombres = struct_get_names(global.controles);
    for (var _i = 0; _i < array_length(_nombres); _i++) {
        var _n = _nombres[_i];
        // Un JSON por acción: menos claves de INI que un campo por acción y por tipo,
        // y admite añadir "eje"/"eje_signo" sin migrar el formato de nuevo.
        ini_write_string("controles", _n, json_stringify(global.controles[$ _n]));
    }
    ini_write_real("controles", "__slot_mando", global.mando_slot);
    ini_close();
}

/// @func controles_cargar()
/// @desc Llamar DESPUÉS de controles_iniciar() (04/40 §3.5), nunca antes: así toda acción
///       que el INI no tenga —una acción nueva en una versión posterior del juego— se
///       queda con su valor de fábrica en vez de romper. Es la misma idea de compatibilidad
///       hacia atrás que 13/06 §3.10 resuelve con migraciones completas; aquí basta con
///       esto porque la FORMA de global.controles no ha cambiado entre versiones, solo
///       su contenido.
function controles_cargar() {
    ini_open("ajustes.ini");
    var _nombres = struct_get_names(global.controles);   // los valores de fábrica ya están puestos
    for (var _i = 0; _i < array_length(_nombres); _i++) {
        var _n = _nombres[_i];
        if (!ini_key_exists("controles", _n)) continue;         // acción nueva: se queda de fábrica
        var _txt = ini_read_string("controles", _n, "");
        if (_txt != "") global.controles[$ _n] = json_parse(_txt);
    }
    global.mando_slot = ini_read_real("controles", "__slot_mando", 0);
    ini_close();
}
```

> ⚠️ **El orden de arranque importa tanto como en §4**: `controles_iniciar()` →
> `controles_cargar()` → (más adelante) `tutorial_iniciar()`, en `rm_init`, nunca al abrir la
> pantalla de Opciones — el orden completo, con estas dos funciones añadidas, está en
> [04 · 40 §3.9](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md#39-orden-de-arranque-quién-llama-a-quién).
> Si `controles_cargar()` corriera antes de `controles_iniciar()`, cada `struct_get_names()`
> devolvería un array vacío y el rebinding guardado no se aplicaría nunca.

### 5.7 El enganche con los iconos y con accesibilidad

Con `global.controles` ya completo (teclado + mando + eje) no queda nada que enseñar aquí de
los iconos: **ya está resuelto**, y repetirlo sería justo lo que la regla 7 del brief de esta
biblioteca prohíbe. `icono_boton()` de
[13 · 05 §2.3](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#23-ratón-táctil-y-mando-a-la-vez-manda-el-último-dispositivo-usado>)
elige la hoja según la marca del mando conectado, y `prompt_boton()`/`prompt_dibujar()` de
[04 · 40 §3.6](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md#36-scr_ui_prompt--el-widget-que-lee-dispositivo--asignación)
combinan esa hoja con la asignación real de esta sección — cayendo a una etiqueta de texto,
nunca a un icono al azar, si la tecla o el botón concretos no tienen icono en la hoja. Lo único
propio de la pantalla de rebinding es que necesita ver **las dos columnas a la vez** (qué tecla
Y qué botón tiene cada acción), no la del dispositivo activo en ese instante:

```gml
/// @func prompt_boton_forzado(_accion, _dispositivo)
/// @desc Envoltorio de prompt_boton() (04/40 §3.6) para dibujar la columna que TOQUE en
///       esta pantalla, no la del último dispositivo tocado — aquí se configuran las dos
///       a la vez, así que hace falta verlas sin esperar a que el jugador use una u otra.
/// @param {String} _accion
/// @param {String} _dispositivo  "teclado" | "mando"
function prompt_boton_forzado(_accion, _dispositivo) {
    var _anterior = global.ui_dispositivo;
    global.ui_dispositivo = (_dispositivo == "mando") ? "mando" : "teclado";
    var _p = prompt_boton(_accion);        // 04/40 §3.6 — se envuelve, no se reescribe
    global.ui_dispositivo = _anterior;     // esto NO es un cambio de dispositivo real: se restaura
    return _p;
}

/// @func control_nombre_eje(_eje, _signo)
/// @desc Etiqueta de un eje de mando — 04/40 §3.6 no lo cubre (ninguna de sus acciones
///       de ejemplo es analógica), así que es la única tabla nueva de esta sección.
/// Verificado: string, struct_exists, is_undefined
function control_nombre_eje(_eje, _signo) {
    if (_eje == -1) return txt("rebind_sin_asignar");
    static NOMBRES = undefined;
    if (is_undefined(NOMBRES)) {
        NOMBRES = {};
        NOMBRES[$ string(gp_axislh)] = txt("eje_stick_izq_h");
        NOMBRES[$ string(gp_axislv)] = txt("eje_stick_izq_v");
        NOMBRES[$ string(gp_axisrh)] = txt("eje_stick_der_h");
        NOMBRES[$ string(gp_axisrv)] = txt("eje_stick_der_v");
    }
    var _c = string(_eje);
    var _nombre = struct_exists(NOMBRES, _c) ? NOMBRES[$ _c] : $"eje {_eje}";
    return _nombre + (_signo > 0 ? " +" : " -");
}
```

Por el lado de accesibilidad, [04 · 27 §4](./27%20-%20Accesibilidad.md#4--accesibilidad-motriz)
ya señala el rebinding completo de esta sección como *«imprescindible para mandos adaptados»* y
[§6](./27%20-%20Accesibilidad.md#6--recordatorio-de-controles-y-de-objetivo) reutiliza
`control_tecla()`/`control_boton_mando()` para que el panel de ayuda en partida muestre la
asignación real — otra vez la misma estructura de datos, en un tercer sitio, sin una tercera
copia.

> 💡 **Recomendación final, ahora sí con el mecanismo entendido**: si tu proyecto no quiere
> mantener a mano la captura, los conflictos y los perfiles de arriba, la librería
> **[Input](../07%20-%20Ecosistema/02%20-%20Librerías%20esenciales%20de%20la%20comunidad.md)** de
> JujuAdams resuelve lo mismo — teclado, mando, varios perfiles, detección de conflictos y
> guardado — con menos código propio y una base de datos de mandos por marca ya mantenida (la
> alternativa a la heurística de `marca_de_mando()`, ver el ⚠️ de 13/05 §2.3). Esta sección
> existe para el caso contrario: cuando prefieres no añadir una dependencia, o cuando necesitas
> entender el mecanismo para poder depurarlo. Ver también
> [12 · Input](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md).

### 5.8 Perfiles de input por jugador: local co-op

Todo el §5 hasta aquí asume **un jugador, un `global.controles`**: la pestaña "Mando 1"/"Mando
2" de §5.4 cambia de qué ranura física se lee, pero sigue escribiendo en el **mismo** mapa de
verbos — como ya avisa esa sección, **no es splitscreen**. Un splitscreen de verdad necesita
que cada jugador tenga su propio mapa, independiente del de los demás: si el Jugador 2 remapea
"saltar" a otro botón, el Jugador 1 no debe enterarse.

La reestructuración es mínima porque la forma de datos de §5.1 ya está verificada: en vez de
**un** `global.controles`, un **array de structs idénticos**, uno por jugador.

```gml
// ============================================================================
// global.controles_jugador — un global.controles (§5.1) por cada jugador.
// Verificado: array_create, array_length, struct_exists
// ============================================================================

/// @func controles_jugador_iniciar(_num_jugadores)
/// @desc Llamar UNA vez, en vez de controles_iniciar() (04/40 §3.5), cuando el juego
///       soporta co-op local. Cada jugador arranca con sus valores de fábrica en un
///       STRUCT PROPIO: reasignar el del Jugador 2 no toca el del 1.
function controles_jugador_iniciar(_num_jugadores) {
    global.controles_jugador = array_create(_num_jugadores);
    for (var _j = 0; _j < _num_jugadores; _j++) {
        // Mismos verbos que controles_iniciar() (04/40 §3.5); el teclado solo se ofrece
        // al Jugador 0 por convención — el resto entra siempre con mando. No es una
        // limitación de GameMaker: si tu juego SÍ reparte el teclado entre dos jugadores,
        // dale a cada acción un vk_* distinto por jugador en vez de vk_nokey.
        global.controles_jugador[_j] = {
            saltar:      { teclado: (_j == 0) ? vk_space : vk_nokey, mando: gp_face1 },
            dash:        { teclado: (_j == 0) ? vk_shift : vk_nokey, mando: gp_shoulderr },
            atacar:      { teclado: (_j == 0) ? ord("F") : vk_nokey, mando: gp_face3 },
            interactuar: { teclado: (_j == 0) ? ord("E") : vk_nokey, mando: gp_face2 },
        };
    }
}

/// @func control_tecla_jugador(_jugador, _accion)
/// @desc Misma lectura defensiva que control_tecla() (04/40 §3.5), indexada por jugador.
function control_tecla_jugador(_jugador, _accion) {
    var _c = global.controles_jugador[_jugador];
    return struct_exists(_c, _accion) ? _c[$ _accion].teclado : vk_nokey;
}

/// @func control_boton_mando_jugador(_jugador, _accion)
function control_boton_mando_jugador(_jugador, _accion) {
    var _c = global.controles_jugador[_jugador];
    return struct_exists(_c, _accion) ? _c[$ _accion].mando : -1;
}
```

El segundo cambio es de dónde sale la **ranura física** de cada jugador: no de
`global.mando_slot` (singular, §5.4), sino del array `mandos_por_jugador` que ya resuelve
[01 · 12 §4 — "Varios mandos, uno por jugador (co-op local)"](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md) —
esa sección asigna qué `pad_index` físico le toca a cada número de jugador; esta añade **qué
significa cada botón** para ese mismo jugador. Las dos piezas encajan sin que ninguna repita a
la otra:

```gml
/// @func input_mover_x_jugador(_jugador)
/// @desc Eje horizontal del JUGADOR indicado: su teclado (solo Jugador 0, ver arriba) y
///       su propio slot de mando, leído de mandos_por_jugador (01 · 12 §4). Nombre distinto
///       a propósito de input_mover_x() (01 · 12 §8, sin parámetro): son dos scripts para
///       dos escenarios —un jugador frente a varios—, y coexistir con el mismo nombre
///       reescribiría la función de uno de los dos en cuanto se importaran los dos scripts
///       al mismo proyecto.
function input_mover_x_jugador(_jugador) {
    if (_jugador == 0) {
        var _teclado = keyboard_check(ord("D")) - keyboard_check(ord("A"));
        if (_teclado != 0) return _teclado;
    }

    var _slot = obj_input_manager.mandos_por_jugador[_jugador];   // 01 · 12 §4
    if (_slot == -1) return 0;                                    // este jugador aún sin mando

    var _eje = gamepad_axis_value(_slot, gp_axislh);
    return (abs(_eje) > 0.25) ? _eje : 0;                         // zona muerta axial (01 · 12 §4)
}

/// @func input_saltar_pulsado_jugador(_jugador)
function input_saltar_pulsado_jugador(_jugador) {
    var _slot         = obj_input_manager.mandos_por_jugador[_jugador];
    var _boton_mando  = control_boton_mando_jugador(_jugador, "saltar");
    var _mando        = (_slot != -1) && gamepad_button_check_pressed(_slot, _boton_mando);
    var _tecla        = (_jugador == 0)
                      && keyboard_check_pressed(control_tecla_jugador(0, "saltar"));

    return _mando || _tecla;
}
```

```gml
// ═══════════ obj_jugador · Create ═══════════
numero_jugador = 0;   // 0 o 1; lo fija el creador de instancia al colocar al Jugador 2

// ═══════════ obj_jugador · Step ═══════════
var _dx = input_mover_x_jugador(numero_jugador);
if (input_saltar_pulsado_jugador(numero_jugador) && en_suelo) { vel_y = vel_salto; }
```

> ⚠️ **Esto NO trae rebinding completo de fábrica.** §5.2-§5.3 (captura, conflictos) siguen
> siendo válidos por jugador, pero cada pantalla de rebinding tiene que operar sobre
> `global.controles_jugador[_jugador]` en vez de sobre `global.controles` — la misma mecánica,
> indexada una vez más. Fuera del alcance de este ejemplo mínimo: monta primero el rebinding
> completo con un solo jugador (§5.2-§5.6) y solo entonces multiplica la forma de datos.
>
> 💡 **Persistencia**: `controles_guardar()`/`controles_cargar()` (§5.6) se adaptan igual — una
> sección de INI por jugador (`$"controles_j{jugador}"`), o un array entero serializado a JSON
> en una sola clave. No hace falta ningún símbolo nuevo, solo un bucle exterior más.

Símbolos verificados: `array_create`, `array_length`, `struct_exists`, `keyboard_check`,
`keyboard_check_pressed`, `gamepad_axis_value`, `gamepad_button_check_pressed`, `abs`.

---

## Las trampas

| Trampa | Consecuencia |
|---|---|
| Aplicar solo al pulsar «Guardar» | El menú se siente muerto; aplica en vivo |
| Cargar los ajustes al abrir Opciones | El juego arranca con valores por defecto |
| `audio_master_gain` para todo | No puedes separar música de efectos; usa grupos |
| Rebinding a mano sin conflictos ni perfiles | El §5 completo lo resuelve; hazlo a mano solo si no quieres la dependencia de Input |
| No dar valores por defecto al leer el INI | La primera vez (sin archivo) el juego revienta |
| Guardar el rebinding en el guardado de partida, no en `ajustes.ini` | Se pierde al borrar el *slot*; es Configuración, no progreso (13/06 §3.10, §5.6) |
| No excluir `vk_escape` al capturar una tecla | El jugador pierde el atajo universal de cancelar/pausar en toda pantalla del juego (§5.2) |
| Asignar el mismo botón a dos acciones sin avisar | El jugador cree que falló al pulsar; en realidad las ejecuta las dos a la vez (§5.3) |
| Restablecer sin confirmar | Una pulsación de más borra un remapeo cuidadoso; pide confirmación con «No» por defecto (§5.5) |

---

## Ver también

- [18 · Menús con scroll](./18%20-%20Menús%20con%20scroll%20y%20navegación.md) — la navegación de la lista
- [21 · Localización](./21%20-%20Localización%20e%20idiomas%20%28con%20traducción%20por%20IA%29.md) — el dropdown de idioma
- [13 · Audio](../01%20-%20Fundamentos/13%20-%20Audio.md) — grupos de audio y volumen
- [00 · Anatomía de un juego completo](./00%20-%20Anatomía%20de%20un%20juego%20completo.md) — dónde encaja Opciones en el arco
- [40 · Tutorial, onboarding y prompts en pantalla](./40%20-%20Tutorial,%20onboarding%20y%20prompts%20en%20pantalla.md#35-scr_controles--la-asignación-real-de-cada-acción) — la forma de datos de `global.controles` que el §5 completa, y los *prompts* que la leen
- [13 · 05 §2.3](<../13 - Diseño y producción de videojuegos/05 - UI y UX de juego.md#23-ratón-táctil-y-mando-a-la-vez-manda-el-último-dispositivo-usado>) — `icono_boton()` y la marca de mando que dibuja el icono correcto tras el rebinding
- [13 · 06 §3.10](<../13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md#310-estado-global-guardado-y-migraciones>) — por qué el rebinding va a `ajustes.ini` y no al guardado de partida
- [27 · Accesibilidad](./27%20-%20Accesibilidad.md#4--accesibilidad-motriz) — por qué el rebinding completo es imprescindible para mandos adaptados
- [01 · 12 §4](../01%20-%20Fundamentos/12%20-%20Input%20-%20teclado,%20ratón%20y%20gamepad.md) — asignación de ranura física por jugador (`mandos_por_jugador`) que §5.8 usa para el local co-op, y la sección de vsync y latencia de input
- [02 · Top-Down / Twin-Stick §8](./02%20-%20Top-Down%20_%20Twin-Stick.md#8-cómo-escalarlo) y [14 · Multijugador § Antes de empezar, en serio](./14%20-%20Multijugador.md#antes-de-empezar-en-serio) — dónde encaja el local co-op de §5.8 en el arco de un proyecto
