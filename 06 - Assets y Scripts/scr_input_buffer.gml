// ============================================================================
// scr_input_buffer.gml
// Input buffering y coyote time para juegos de plataformas.
//
// LOS DOS PROBLEMAS QUE RESUELVE
//
//   COYOTE TIME
//     El jugador sale corriendo de un borde y pulsa salto 3 frames después.
//     Sin coyote time, no salta: ya no está en el suelo. Se siente injusto,
//     aunque "tecnicamente" el jugador llego tarde.
//     Solucion: durante unos frames tras dejar el suelo, seguimos permitiendo
//     el salto.
//
//   INPUT BUFFERING
//     El jugador pulsa salto 3 frames ANTES de aterrizar. El juego ignora la
//     pulsación porque está en el aire, y al aterrizar no salta.
//     Solucion: recordamos la pulsación durante unos frames y la consumimos
//     en cuánto sea legal ejecutarla.
//
//   Los dos juntos son la diferencia entre un plataformas que se siente
//   "duro" y uno que se siente "justo".
//
// IMPORTANTE SOBRE LAS UNIDADES
//   Estos buffers se miden en FRAMES, no en segundos, porque la ventana es muy
//   corta (4-8 frames) y es lo que usan los juegos de referencia. Si tu juego
//   corre a velocidad variable, convierte: segundos * room_speed.
//
// Funciones nativas usadas (verificadas con gm-cli manual read):
//   keyboard_check, keyboard_check_pressed, keyboard_check_released,
//   gamepad_button_check_pressed, max, min, instance_exists
//
// Dependencias: ninguna (usa solo input nativo; si quieres remapeo, usa Input).
//
// USO RAPIDO
//   // En el Create de obj_player:
//   buffer_jump = new InputBuffer(6);   // 6 frames de gracia
//   coyote      = new CoyoteTime(6);    // 6 frames tras salir del suelo
//
//   // En el Step de obj_player:
//   var _en_suelo = place_meeting(x, y + 1, obj_wall);
//   coyote.update(_en_suelo);
//   buffer_jump.update(keyboard_check_pressed(vk_space));
//
//   // Para saltar: consume el buffer si el coyote lo permite
//   if (buffer_jump.consume() && (coyote.disponible() || _en_suelo)) {
//       vel_y = -JUMP_SPEED;
//       coyote.consume();        // gastamos el coyote: no doble salto gratis
//       buffer_jump.consume();
//   }
//
//   // SALTO VARIABLE: suelta el botón y subes menos
//   if (keyboard_check_released(vk_space) && vel_y < 0) {
//       vel_y *= 0.5;
//   }
// ============================================================================


/// @function InputBuffer(_frames)
/// @desc    Constructor. Guarda una pulsación durante N frames para que no se
///          pierda si se pulsa un poco antes de tiempo.
/// @param   {Real} _frames  Frames que sobrevive la pulsación (4-8 es lo tipico).
function InputBuffer(_frames) constructor {
    frames_max = max(_frames, 1);
    contador   = 0;

    /// @desc Llamalo UNA VEZ POR FRAME con el resultado de la comprobacion de
    ///       pulsación. Si la tecla se acaba de pulsar, resetea el contador.
    /// @param {Bool} _pulsado  Resultado de `keyboard_check_pressed()`.
    static update = function(_pulsado) {
        if (_pulsado) {
            contador = frames_max;
        } else if (contador > 0) {
            contador--;
        }
    };

    /// @desc Mismo que `update` pero aceptando varias fuentes de input a la
    ///       vez (teclado + gamepad + tactil) con un OR.
    /// @param {Bool} _pulsado1  Primera fuente.
    /// @param {Bool} _pulsado2  Segunda fuente (opcional).
    /// @param {Bool} _pulsado3  Tercera fuente (opcional).
    static update_multi = function(_pulsado1, _pulsado2 = false, _pulsado3 = false) {
        update(_pulsado1 || _pulsado2 || _pulsado3);
    };

    /// @desc ¿Hay una pulsación pendiente sin consumir?
    /// @returns {Bool}
    static disponible = function() {
        return (contador > 0);
    };

    /// @desc Devuelve true y CONSUME el buffer (lo pone a 0) si hay pulsación.
    ///       Usa esto para que la misma pulsación no dispare dos acciones.
    /// @returns {Bool}
    static consume = function() {
        if (contador > 0) {
            contador = 0;
            return true;
        }
        return false;
    };

    /// @desc Borra el buffer sin consumirlo. Util al pausar, al cambiar de
    ///       room o al morir: evita que una pulsación vieja se dispare al
    ///       volver a tomar el control.
    static reset = function() {
        contador = 0;
    };

    /// @desc Cuantos frames quedan. Para depurar.
    /// @returns {Real}
    static restante = function() {
        return contador;
    };
}


/// @function CoyoteTime(_frames)
/// @desc    Constructor. Mantiene viva la posibilidad de saltar durante N
///          frames después de abandonar el suelo.
/// @param   {Real} _frames  Frames de gracia (4-8 es lo tipico).
function CoyoteTime(_frames) constructor {
    frames_max = max(_frames, 1);
    contador   = 0;
    en_suelo_antes = false;

    /// @desc Llamalo UNA VEZ POR FRAME, ANTES de decidir si saltas.
    /// @param {Bool} _en_suelo  ¿Esta el personaje pisando suelo ahora mismo?
    static update = function(_en_suelo) {
        if (_en_suelo) {
            // En el suelo: la ventana se rellena por completo.
            contador = frames_max;
        } else if (contador > 0) {
            // En el aire: la ventana se vacía.
            contador--;
        }
        en_suelo_antes = _en_suelo;
    };

    /// @desc ¿Todavia puede saltar (porque está en el suelo O porque acaba de
    ///       dejarlo)?
    /// @returns {Bool}
    static disponible = function() {
        return (contador > 0);
    };

    /// @desc Gasta la ventana. LLAMALO JUSTO DESPUES DE SALTAR: si no, el
    ///       jugador podria volver a saltar en el aire aprovechando el
    ///       coyote restante (un doble salto involuntario).
    static consume = function() {
        contador = 0;
    };

    /// @desc Pone la ventana a cero. Util al caer por un precipicio o al
    ///       empujar al personaje: no debería poder saltar en el aire.
    static reset = function() {
        contador = 0;
    };

    /// @desc Cuantos frames quedan. Para depurar.
    /// @returns {Real}
    static restante = function() {
        return contador;
    };

    /// @desc ¿Acaba de dejar el suelo en este mismo frame? Util para
    ///       disparar polvo, sonido o la animación de caida.
    /// @returns {Bool}
    static acaba_de_salir = function() {
        return (!en_suelo_antes && contador > 0);
    };
}


/// @function JumpHelper(_buffer_frames, _coyote_frames)
/// @desc    Los dos juntos en un solo objeto, con la logica de salto ya
///          resuelta. Es la forma más rapida de tener un salto que se sienta
///          bien sin escribir tu propia máquina de estados.
/// @param   {Real} _buffer_frames  Frames de input buffering.
/// @param   {Real} _coyote_frames  Frames de coyote time.
function JumpHelper(_buffer_frames, _coyote_frames) constructor {
    buffer = new InputBuffer(_buffer_frames);
    coyote = new CoyoteTime(_coyote_frames);

    en_suelo = false;
    saltando = false;

    /// @desc Llamalo UNA VEZ POR FRAME, al principio del Step.
    /// @param {Bool} _en_suelo  ¿Esta pisando suelo?
    /// @param {Bool} _pulso     ¿Se ha pulsado el botón de salto?
    static update = function(_en_suelo, _pulso) {
        en_suelo = _en_suelo;
        coyote.update(_en_suelo);
        buffer.update(_pulso);
    };

    /// @desc True si se dan las condiciones para saltar. NO consume nada:
    ///       llámalo para decidir, y luego a `consume_salto()`.
    /// @returns {Bool}
    static puede_saltar = function() {
        return (buffer.disponible() && coyote.disponible());
    };

    /// @desc Devuelve true exactamente UNA VEZ por salto: consume el buffer y
    ///       el coyote a la vez. Usa el resultado para aplicar la velocidad.
    /// @returns {Bool}
    static consumir_salto = function() {
        if (!puede_saltar()) { return false; }
        buffer.consume();
        coyote.consume();
        return true;
    };

    /// @desc Corta el salto si se suelta el botón. LLAMALO CUANDO SUELTEN el
    ///       botón: multiplica la velocidad vertical y produce el clasico
    ///       "salto variable" (poco = salto corto, mucho = salto alto).
    /// @param {Real} _vel_y    Velocidad vertical actual (negativa = subiendo).
    /// @param {Real} _corte    Factor de corte (0.45-0.6 es lo habitual).
    /// @returns {Real}         Nueva velocidad vertical.
    static cortar_salto = function(_vel_y, _corte = 0.5) {
        // Solo cortamos si estamos SUBIENDO (vel_y < 0 en GameMaker, donde el
        // eje Y crece hacia abajo). Si ya caemos, no tocamos nada.
        if (_vel_y < 0) {
            return _vel_y * _corte;
        }
        return _vel_y;
    };

    /// @desc Resetea todo. Llamalo al morir, al pausar o al cambiar de room.
    static reset = function() {
        buffer.reset();
        coyote.reset();
        saltando = false;
    };
}


/// @function input_debug_draw(_helper, _x, _y)
/// @desc    Pinta el estado del buffer y del coyote. LLAMALO EN DRAW GUI.
///          Imprescindible para AJUSTAR los valores: si ves que el buffer
///          nunca llega a cero cuando juegas, es demasiado largo.
/// @param   {Struct} _helper  Un `JumpHelper`.
/// @param   {Real}   _x       Posición X en pantalla.
/// @param   {Real}   _y       Posición Y en pantalla.
function input_debug_draw(_helper, _x, _y) {
    if (!is_struct(_helper)) { return; }

    var _c_previo = draw_get_color();
    var _a_previo = draw_get_alpha();
    var _h_previo = draw_get_halign();

    draw_set_halign(fa_left);
    draw_set_alpha(1);

    draw_set_color(_helper.en_suelo ? c_lime : c_gray);
    draw_text(_x, _y, "suelo: " + (_helper.en_suelo ? "SI" : "no"));

    draw_set_color(_helper.buffer.disponible() ? c_yellow : c_gray);
    draw_text(_x, _y + 16, "buffer: " + string(_helper.buffer.restante()));

    draw_set_color(_helper.coyote.disponible() ? c_aqua : c_gray);
    draw_text(_x, _y + 32, "coyote: " + string(_helper.coyote.restante()));

    draw_set_color(_c_previo);
    draw_set_alpha(_a_previo);
    draw_set_halign(_h_previo);
}
