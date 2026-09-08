// ============================================================================
// scr_ui_confirmar.gml
// Diálogo de confirmación genérico (Sí/No), con «No» siempre por defecto.
//
// Generaliza el patrón que documenta 04 · 41 §3.4.4 (la confirmación de "¿Seguro
// que quieres salir?" del menú de pausa), que la propia receta señalaba como
// "todavía sin generalizar" — este script cierra ese hueco. Reutilízalo para
// CUALQUIER acción destructiva: salir, sobrescribir una ranura de guardado
// (13 · 05, componente n), borrar una partida, restablecer los ajustes de
// fábrica (04 · 25)... Solo puede haber un diálogo abierto a la vez, que es
// justo lo que necesita una confirmación: bloquea el resto de la UI hasta que
// el jugador responde, a propósito.
//
// POR QUÉ NO USA show_question(): bloquea el juego en un bucle cerrado y se
// ignora al compilar para cualquier plataforma que no sea Windows salvo en
// modo debug (01 · 15 §12, ya lo advierte). Un diálogo de confirmación de
// verdad es un estado más de tu propia máquina, no una llamada bloqueante.
//
// Funciones nativas usadas (verificadas con gm-cli manual read / buscar.py):
//   keyboard_check_pressed, gamepad_is_connected, gamepad_button_check_pressed,
//   is_callable, display_get_gui_width, display_get_gui_height, draw_rectangle,
//   draw_rectangle_color, draw_text, draw_text_color, draw_set_halign,
//   draw_set_valign, draw_set_colour, draw_set_alpha
//
// LOCALIZACIÓN: este script NO llama a `txt()` directamente (una función que tu
// proyecto podría no definir haría que esto ni compilase). En su lugar, fija
// los rótulos UNA vez al arrancar con `confirmar_configurar_textos()`, igual
// que el resto de sistemas globales de 04 · 00 §1:
//   confirmar_configurar_textos(txt("comun_si"), txt("comun_no"));
// Las mismas claves "comun_si"/"comun_no" que ya usa el ejemplo de 04 · 41
// §3.4.4, para no traducir el mismo par de botones con dos claves distintas.
//
// USO RÁPIDO
//   // rm_init, una vez (04 · 00 §1):
//   confirmar_configurar_textos(txt("comun_si"), txt("comun_no"));
//
//   // Donde haga falta confirmar algo:
//   confirmar_abrir(txt("guardado_sobrescribir_pregunta"),
//       function() { save_game("slot1", global.partida_actual); },   // "Sí"
//       undefined);                                                  // "No": no hace falta acción
//
//   // Desde un objeto persistente (obj_pausa, obj_ui_gestor…), UNA vez por frame:
//   //   Step:     confirmar_step();
//   //   Draw GUI: confirmar_dibujar();     // por encima de todo lo demás
// ============================================================================

global.confirmar = {
    activo     : false,
    texto      : "",
    texto_si   : "Sí",         // sobrescribe con confirmar_configurar_textos() al arrancar
    texto_no   : "No",
    foco       : 0,             // 0 = "No", 1 = "Sí" — "No" empieza SIEMPRE con el foco
    accion_si  : undefined,
    accion_no  : undefined,
};

/// @function confirmar_configurar_textos(_texto_si, _texto_no)
/// @desc    Fija los rótulos de los dos botones para TODOS los diálogos de confirmación
///          que se abran a partir de ahora. Llámala una vez al arrancar el juego, junto al
///          resto de sistemas globales (04 · 00 §1) — después de inicializar la localización,
///          para poder pasarle ya el texto traducido de `txt()`.
/// @param   {String} _texto_si
/// @param   {String} _texto_no
/// @returns {Undefined}
function confirmar_configurar_textos(_texto_si, _texto_no) {
    global.confirmar.texto_si = _texto_si;
    global.confirmar.texto_no = _texto_no;
}

/// @function confirmar_abrir(_texto, _accion_si, _accion_no)
/// @desc    Abre el diálogo de confirmación. Solo puede haber uno activo a la vez: si ya
///          había otro abierto, este lo reemplaza.
/// @param   {String}   _texto      La pregunta, ya traducida (pásale el resultado de `txt()`).
/// @param   {Function} _accion_si  Se llama si el jugador confirma. Puede ser `undefined`.
/// @param   {Function} _accion_no  OPCIONAL. Se llama si el jugador cancela (con "No" o Esc/B).
///                                 Si no la das, cancelar simplemente cierra el diálogo.
/// @returns {Undefined}
function confirmar_abrir(_texto, _accion_si, _accion_no = undefined) {
    global.confirmar.activo    = true;
    global.confirmar.texto     = _texto;
    global.confirmar.foco      = 0;          // "No" por defecto — 13/05 §2.1, regla 3
    global.confirmar.accion_si = _accion_si;
    global.confirmar.accion_no = _accion_no;
}

/// @function confirmar_activo()
/// @desc    Comprueba si hay un diálogo de confirmación abierto ahora mismo. Úsalo para que
///          la pantalla de debajo ignore su propio input mientras el diálogo está encima
///          (el mismo criterio que ya usa la pausa con sus propios sub-estados, 04/41 §3.4.1).
/// @returns {Bool}
function confirmar_activo() {
    return global.confirmar.activo;
}

/// @function confirmar_step()
/// @desc    Llamar UNA vez por frame, desde un objeto persistente, ANTES de que cualquier
///          otro input de la pantalla de debajo consuma la tecla de aceptar/cancelar. No
///          hace nada si no hay ningún diálogo abierto.
/// @returns {Undefined}
function confirmar_step() {
    if (!global.confirmar.activo) { return; }

    var _hay_mando = gamepad_is_connected(0);

    var _izquierda = keyboard_check_pressed(vk_left)
                   || (_hay_mando && gamepad_button_check_pressed(0, gp_padl));
    var _derecha   = keyboard_check_pressed(vk_right)
                   || (_hay_mando && gamepad_button_check_pressed(0, gp_padr));
    var _aceptar   = keyboard_check_pressed(vk_enter)
                   || (_hay_mando && gamepad_button_check_pressed(0, gp_face1));
    var _cancelar  = keyboard_check_pressed(vk_escape)
                   || (_hay_mando && gamepad_button_check_pressed(0, gp_face2));

    if (_izquierda || _derecha) {
        global.confirmar.foco = 1 - global.confirmar.foco;
    }

    if (_aceptar) {
        var _elegido_si = (global.confirmar.foco == 1);
        var _si = global.confirmar.accion_si;
        var _no = global.confirmar.accion_no;
        global.confirmar.activo = false;    // cerrar ANTES de llamar: la acción puede abrir otro
        if (_elegido_si) { if (is_callable(_si)) { _si(); } }
        else              { if (is_callable(_no)) { _no(); } }
        return;
    }

    if (_cancelar) {
        var _no2 = global.confirmar.accion_no;
        global.confirmar.activo = false;
        if (is_callable(_no2)) { _no2(); }
    }
}

/// @function confirmar_dibujar()
/// @desc    Llamar desde el evento Draw GUI, por encima de cualquier otro dibujo de la
///          pantalla. No hace nada si no hay ningún diálogo abierto.
/// @returns {Undefined}
function confirmar_dibujar() {
    if (!global.confirmar.activo) { return; }

    var _gw = display_get_gui_width();
    var _gh = display_get_gui_height();
    var _pw = 420, _ph = 160;
    var _px = (_gw - _pw) / 2, _py = (_gh - _ph) / 2;

    // velo semitransparente: deja claro que el resto de la pantalla está bloqueada
    draw_set_alpha(0.6);
    draw_rectangle_color(0, 0, _gw, _gh, c_black, c_black, c_black, c_black, false);
    draw_set_alpha(1);

    draw_set_colour(c_black);
    draw_rectangle(_px, _py, _px + _pw, _py + _ph, false);

    draw_set_halign(fa_center);
    draw_set_valign(fa_top);
    draw_text(_gw / 2, _py + 32, global.confirmar.texto);

    var _col_no = (global.confirmar.foco == 0) ? c_white : c_gray;
    var _col_si = (global.confirmar.foco == 1) ? c_white : c_gray;

    draw_text_color(_gw / 2 - 80, _py + _ph - 40, global.confirmar.texto_no,
                     _col_no, _col_no, _col_no, _col_no, 1);
    draw_text_color(_gw / 2 + 80, _py + _ph - 40, global.confirmar.texto_si,
                     _col_si, _col_si, _col_si, _col_si, 1);

    draw_set_halign(fa_left);
    draw_set_valign(fa_top);
}
