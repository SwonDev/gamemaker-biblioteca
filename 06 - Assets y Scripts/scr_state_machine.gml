// ============================================================================
// scr_state_machine.gml
// Máquina de estados finitos (FSM) implementada con structs, SIN objetos.
//
// Por que structs y no objetos:
//   - No ocupa una instancia en la room.
//   - No ejecuta eventos: tu decides CUANDO se actualiza.
//   - Se puede guardar el estado actual con json_stringify (solo el nombre).
//
// Funciones nativas usadas (verificadas con gm-cli manual read):
//   is_struct, struct_exists, is_method, method, struct_get_names, string
//
// Dependencias: ninguna.
//
// USO RAPIDO
//   // En el Create de obj_player:
//   fsm = new StateMachine(id, {
//       idle: {
//           enter : function() { sprite_index = spr_player_idle; },
//           update: function() { if (abs(vel_x) > 0) { fsm.set("correr"); } },
//           exit  : function() { show_debug_message("dejo de estar quieto"); }
//       },
//       correr: {
//           enter : function() { sprite_index = spr_player_run; },
//           update: function() { if (abs(vel_x) == 0) { fsm.set("idle"); } }
//       }
//   }, "idle");
//
//   // En el Step de obj_player:
//   fsm.update();
//
// NOTA SOBRE `self`: las funciones de estado se ejecutan en el ambito del
// dueno (gracias a `method()`), así que dentro de ellas `vel_x` es
// `obj_player.vel_x` y `fsm` es `obj_player.fsm`. No hace falta `other`.
// ============================================================================


/// @function StateMachine(_dueno, _estados, _inicial)
/// @desc    Constructor de la máquina de estados.
/// @param   {Id.Instance} _dueno    Instancia dueña (normalmente `id`).
/// @param   {Struct}      _estados  Struct con un sub-struct por estado. Cada
///                                  estado acepta las claves `enter`,
///                                  `update` y `exit`, todas opcionales.
/// @param   {String}      _inicial  Nombre del estado de arranque.
function StateMachine(_dueno, _estados, _inicial) constructor {
    dueno   = _dueno;
    estados = is_struct(_estados) ? _estados : {};

    estado_actual = "";
    estado_anterior = "";
    tiempo_en_estado = 0;   // en llamadas a update(), no en segundos

    /// @desc Cambia de estado llamando a `exit` del viejo y `enter` del nuevo.
    /// @param {String} _nombre  Nombre del estado destino.
    /// @returns {Bool}          True si el cambio se hizo.
    static set = function(_nombre) {
        if (!struct_exists(estados, _nombre)) {
            show_debug_message("StateMachine.set: el estado \"" + string(_nombre) + "\" no existe.");
            return false;
        }
        if (_nombre == estado_actual) { return false; }

        // Salimos del estado anterior.
        if (estado_actual != "" && struct_exists(estados, estado_actual)) {
            var _viejo = estados[$ estado_actual];
            if (is_struct(_viejo) && struct_exists(_viejo, "exit") && is_method(_viejo.exit)) {
                _viejo.exit();
            }
        }

        estado_anterior = estado_actual;
        estado_actual   = _nombre;
        tiempo_en_estado = 0;

        // Entramos en el nuevo.
        var _nuevo = estados[$ _nombre];
        if (is_struct(_nuevo) && struct_exists(_nuevo, "enter") && is_method(_nuevo.enter)) {
            _nuevo.enter();
        }
        return true;
    };

    /// @desc Ejecuta la función `update` del estado actual. Llamala una vez
    ///       por frame desde el Step de la instancia dueña.
    static update = function() {
        if (estado_actual == "") { return; }

        tiempo_en_estado++;

        var _est = estados[$ estado_actual];
        if (is_struct(_est) && struct_exists(_est, "update") && is_method(_est.update)) {
            _est.update();
        }
    };

    /// @desc Nombre del estado actual.
    /// @returns {String}
    static get = function() {
        return estado_actual;
    };

    /// @desc Comprueba si estamos en un estado concreto.
    /// @param {String} _nombre
    /// @returns {Bool}
    static is = function(_nombre) {
        return (estado_actual == _nombre);
    };

    /// @desc Cuantas llamadas a update() llevamos en el estado actual.
    ///       Para comparar tiempos, hazlo en frames o conviertelo con
    ///       `fsm.tiempo_en_estado / room_speed` para tener segundos.
    /// @returns {Real}
    static get_time = function() {
        return tiempo_en_estado;
    };

    /// @desc Anade o reemplaza un estado en caliente.
    /// @param {String} _nombre
    /// @param {Struct} _estado  Struct con claves enter/update/exit opcionales.
    static add = function(_nombre, _estado) {
        estados[$ _nombre] = _estado;
    };

    /// @desc Lista de nombres de estados definidos (útil para depurar).
    /// @returns {Array<String>}
    static list = function() {
        return struct_get_names(estados);
    };

    /// @desc Vuelve al estado anterior. Si no hay anterior, no hace nada.
    /// @returns {Bool}
    static back = function() {
        if (estado_anterior == "") { return false; }
        return set(estado_anterior);
    };

    // Arrancamos en el estado inicial. Se hace AL FINAL del constructor para
    // que todos los métodos static ya existan cuando se llame a `enter`.
    if (_inicial != "" && struct_exists(estados, _inicial)) {
        estado_actual   = _inicial;
        tiempo_en_estado = 0;
        var _ini = estados[$ _inicial];
        if (is_struct(_ini) && struct_exists(_ini, "enter") && is_method(_ini.enter)) {
            _ini.enter();
        }
    }
}


/// @function fsm_bind(_dueno, _estados, _inicial)
/// @desc    Crea una StateMachine y vincula TODAS sus funciones de estado al
///          ambito del dueno con `method()`. Esto es lo que permite escribir
///          `vel_x` en vez de `dueno.vel_x` dentro de un estado.
///
///          Usala en lugar de `new StateMachine(...)` si quieres ese azucar.
/// @param   {Id.Instance} _dueno    Instancia dueña.
/// @param   {Struct}      _estados  Struct de estados.
/// @param   {String}      _inicial  Estado inicial.
/// @returns {Struct}                La StateMachine ya vinculada.
function fsm_bind(_dueno, _estados, _inicial) {
    if (!is_struct(_estados)) { return new StateMachine(_dueno, {}, _inicial); }

    var _nombres = struct_get_names(_estados);
    var _nuevos = {};

    for (var _i = 0; _i < array_length(_nombres); _i++) {
        var _nombre = _nombres[_i];
        var _estado = _estados[$ _nombre];

        if (!is_struct(_estado)) { continue; }

        var _claves = struct_get_names(_estado);
        var _estado_nuevo = {};

        for (var _j = 0; _j < array_length(_claves); _j++) {
            var _clave = _claves[_j];
            var _fn = _estado[$ _clave];

            // Solo reenlazamos si es una función.
            if (is_method(_fn)) {
                _estado_nuevo[$ _clave] = method(_dueno, _fn);
            } else {
                _estado_nuevo[$ _clave] = _fn;
            }
        }
        _nuevos[$ _nombre] = _estado_nuevo;
    }

    return new StateMachine(_dueno, _nuevos, _inicial);
}


/// @function fsm_debug_draw(_fsm, _x, _y)
/// @desc    Dibuja el estado actual y el tiempo en el mismo. Para depuración.
///          LLAMALA EN UN EVENTO DRAW GUI.
/// @param   {Struct} _fsm  La StateMachine.
/// @param   {Real}   _x    Posición X en pantalla.
/// @param   {Real}   _y    Posición Y en pantalla.
function fsm_debug_draw(_fsm, _x, _y) {
    if (!is_struct(_fsm)) { return; }

    var _c_prev  = draw_get_color();
    var _a_prev  = draw_get_alpha();
    var _h_prev  = draw_get_halign();

    draw_set_halign(fa_left);
    draw_set_alpha(1);
    draw_set_color(c_yellow);
    draw_text(_x, _y, "FSM: " + string(_fsm.get()));
    draw_set_color(c_white);
    draw_text(_x, _y + 16, "  t: " + string(_fsm.get_time()) + "  ant: " + string(_fsm.estado_anterior));

    draw_set_color(_c_prev);
    draw_set_alpha(_a_prev);
    draw_set_halign(_h_prev);
}
