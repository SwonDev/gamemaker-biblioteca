// ============================================================================
// scr_pool.gml
// Object pooling: reutiliza instancias en vez de crearlas y destruirlas.
//
// POR QUE LO NECESITAS
//   `instance_create_layer()` + `instance_destroy()` continuos (balas,
//   particulas, enemigos de una oleada) provocan tirones de framerate: cada
//   creación reserva memoria y cada destrucción la libera. Con un pool,
//   creas todo de una vez y solo activas/desactivas.
//
// COMO FUNCIONA
//   Las instancias inactivas se DESACTIVAN con
//   `instance_deactivate_object()`. Una instancia desactivada:
//     - no ejecuta eventos (ni Step ni Draw),
//     - no colisiona,
//     - sigue existiendo en memoria.
//   Al activarla recuperas una instancia limpia y lista.
//
//   ⚠️ Segun el manual, la desactivacion NO es instantanea: no surte efecto
//   hasta el final del evento en que se llama. Por eso el pool activa y ya
//   puede escribir variables en la misma llamada, pero si compruebas
//   `instance_exists()` en el mismo evento todavia dira true.
//
// Funciones nativas usadas (verificadas con gm-cli manual read):
//   instance_create_layer, instance_destroy, instance_exists,
//   instance_deactivate_object, instance_activate_object,
//   array_push, array_pop, array_length, array_delete, layer_get_id
//
// Dependencias: ninguna.
//
// USO RAPIDO
//   // En el Create de obj_game:
//   pool_balas = new Pool(obj_bullet, 100, "Instances");
//
//   // Para sacar una bala:
//   var _b = pool_balas.get_at(x, y);
//   if (_b != noone) {
//       _b.vel_x = lengthdir_x(10, image_angle);
//       _b.vel_y = lengthdir_y(10, image_angle);
//   }
//
//   // Cuando la bala muera (desde la propia bala):
//   obj_game.pool_balas.release(id);
//
//   // En el Clean Up de obj_game:
//   pool_balas.destroy();
// ============================================================================


/// @function Pool(_obj, _tamano, _layer, _crecer_auto)
/// @desc    Constructor del pool.
/// @param   {Asset.GMObject} _obj          Objeto del que crear instancias.
/// @param   {Real}           _tamano       Cuantas instancias pre-crear.
/// @param   {String}         _layer        Nombre de la capa donde crearlas
///                                         (por defecto "Instances").
/// @param   {Bool}           _crecer_auto  Si al quedarse sin instancias debe
///                                         crear más en vez de devolver noone.
function Pool(_obj, _tamano, _layer = "Instances", _crecer_auto = true) constructor {
    obj         = _obj;
    layer_nombre = _layer;
    crecer_auto = _crecer_auto;

    libres  = [];   // instancias desactivadas, listas para usar
    activos = [];   // instancias en uso

    // Variables que se reinician al reciclar una instancia. Se rellenan con
    // `set_reset_vars()` y se aplican con `variable_instance_set()`.
    reset_vars = {};

    /// @desc Pre-crea N instancias y las desactiva.
    /// @param {Real} _n  Cuantas anadir.
    static grow = function(_n) {
        var _capa = layer_get_id(layer_nombre);
        if (_capa == -1) {
            show_debug_message("Pool.grow: la capa \"" + string(layer_nombre) + "\" no existe.");
            return 0;
        }

        var _creadas = 0;
        var _i;
        for (_i = 0; _i < _n; _i++) {
            var _inst = instance_create_layer(0, 0, _capa, obj);
            if (!instance_exists(_inst)) { continue; }

            // Importante: desactivar INMEDIATAMENTE para que no ejecute ni un
            // solo Step ni un solo Draw antes de que la usemos.
            instance_deactivate_object(_inst);
            array_push(libres, _inst);
            _creadas++;
        }
        return _creadas;
    };

    /// @desc Saca una instancia del pool y la activa.
    /// @returns {Id.Instance|Constant.Noone}  La instancia, o `noone` si no
    ///          quedan libres y no se permite crecer.
    static get = function() {
        // ¿Nos hemos quedado sin instancias?
        if (array_length(libres) == 0) {
            if (crecer_auto) {
                grow(max(1, floor(array_length(activos) / 2) + 1));
            }
            if (array_length(libres) == 0) {
                return noone;
            }
        }

        var _inst = array_pop(libres);

        // La reactivamos. La instancia conserva su posición anterior: es
        // responsabilidad de quién la pide colocarla (ver `get_at`).
        instance_activate_object(_inst);

        __resetear(_inst);

        array_push(activos, _inst);
        return _inst;
    };

    /// @desc Saca una instancia, la coloca y la activa. Atajo del caso comun.
    /// @param {Real} _x  Posición X.
    /// @param {Real} _y  Posición Y.
    /// @returns {Id.Instance|Constant.Noone}
    static get_at = function(_x, _y) {
        var _inst = get();
        if (_inst == noone) { return noone; }
        _inst.x = _x;
        _inst.y = _y;
        return _inst;
    };

    /// @desc Devuelve una instancia al pool (la desactiva).
    ///       IMPORTANTE: llama a esto en vez de a `instance_destroy()`.
    /// @param {Id.Instance} _inst  Instancia a reciclar.
    /// @returns {Bool}             True si estaba en la lista de activos.
    static release = function(_inst) {
        if (!instance_exists(_inst)) { return false; }

        var _i;
        for (_i = 0; _i < array_length(activos); _i++) {
            if (activos[_i] == _inst) {
                array_delete(activos, _i, 1);
                instance_deactivate_object(_inst);
                array_push(libres, _inst);
                return true;
            }
        }

        // No estaba registrada como activa: la desactivamos igual para evitar
        // que se quede suelta ejecutando eventos.
        instance_deactivate_object(_inst);
        array_push(libres, _inst);
        return false;
    };

    /// @desc Devuelve TODAS las instancias activas al pool. Llamalo al
    ///       reiniciar una room o al empezar una oleada nueva.
    static release_all = function() {
        // Copiamos el array porque `release` lo modifica mientras iteramos.
        var _copia = [];
        var _i;
        for (_i = 0; _i < array_length(activos); _i++) {
            array_push(_copia, activos[_i]);
        }
        for (_i = 0; _i < array_length(_copia); _i++) {
            release(_copia[_i]);
        }
    };

    /// @desc Aplica las variables de reinicio a una instancia reciclada.
    ///       Uso interno.
    /// @param {Id.Instance} _inst
    static __resetear = function(_inst) {
        var _nombres = struct_get_names(reset_vars);
        var _i;
        for (_i = 0; _i < array_length(_nombres); _i++) {
            var _nombre = _nombres[_i];
            variable_instance_set(_inst, _nombre, reset_vars[$ _nombre]);
        }
    };

    /// @desc Define variables que se reinician al reciclar cada instancia.
    ///       Ahorra el tipico "se me olvido resetear image_alpha y la bala
    ///       reaparecio transparente".
    /// @param {Struct} _vars  Struct { nombre_variable: valor_por_defecto }.
    static set_reset_vars = function(_vars) {
        if (is_struct(_vars)) { reset_vars = _vars; }
    };

    /// @desc Ejecuta una función sobre cada instancia ACTIVA del pool.
    ///       Equivale a un `with()` pero solo sobre tus instancias.
    /// @param {Function} _fn  Función a ejecutar; recibe la instancia.
    static for_each_active = function(_fn) {
        if (!is_method(_fn)) { return; }

        var _i;
        for (_i = 0; _i < array_length(activos); _i++) {
            var _inst = activos[_i];
            if (instance_exists(_inst)) { _fn(_inst); }
        }
    };

    /// @desc Cuantas instancias hay en uso ahora mismo.
    /// @returns {Real}
    static count_active = function() {
        return array_length(activos);
    };

    /// @desc Cuantas instancias quedan disponibles.
    /// @returns {Real}
    static count_free = function() {
        return array_length(libres);
    };

    /// @desc Destruye el pool y TODAS sus instancias (activas e inactivas).
    ///       LLAMALO EN EL CLEAN UP del objeto dueño.
    static destroy = function() {
        var _i;

        // Hay que ACTIVAR antes de destruir: una instancia desactivada no se
        // puede destruir con fiabilidad en todos los targets.
        for (_i = 0; _i < array_length(libres); _i++) {
            var _l = libres[_i];
            if (instance_exists(_l)) {
                instance_activate_object(_l);
                instance_destroy(_l);
            }
        }
        for (_i = 0; _i < array_length(activos); _i++) {
            var _a = activos[_i];
            if (instance_exists(_a)) { instance_destroy(_a); }
        }

        libres  = [];
        activos = [];
    };

    // Pre-creamos el tamaño inicial. Va al final del constructor para que
    // todos los métodos static ya existan cuando se llame.
    if (_tamano > 0) { grow(_tamano); }
}


/// @function pool_cleanup_orphans(_pool)
/// @desc    Limpia del array de activos las instancias que hayan sido
///          destruidas por otra via (un `instance_destroy()` perdido, un
///          cambio de room...). Llamalo de vez en cuando si tu juego destruye
///          instancias del pool por su cuenta.
/// @param   {Struct} _pool  El pool.
/// @returns {Real}          Cuantas referencias muertas se han eliminado.
function pool_cleanup_orphans(_pool) {
    if (!is_struct(_pool)) { return 0; }

    var _limpiadas = 0;

    var _i;
    for (_i = array_length(_pool.activos) - 1; _i >= 0; _i--) {
        if (!instance_exists(_pool.activos[_i])) {
            array_delete(_pool.activos, _i, 1);
            _limpiadas++;
        }
    }
    for (_i = array_length(_pool.libres) - 1; _i >= 0; _i--) {
        if (!instance_exists(_pool.libres[_i])) {
            array_delete(_pool.libres, _i, 1);
            _limpiadas++;
        }
    }

    return _limpiadas;
}
