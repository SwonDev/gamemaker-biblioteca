// ============================================================================
// scr_tween.gml
// Sistema de tweens (interpolaciones animadas) con structs, dirigido por
// delta_time. Sin objetos, sin assets, sin alarmas.
//
// Por que dirigido por `delta_time` y no por frames:
//   Un tween de 0.5 segundos dura 0.5 segundos tanto a 30 fps como a 144 fps.
//   Con un contador de frames duraria distinto en cada máquina.
//
// Alternativa nativa: `time_source_create()` + `time_source_start()` es válido
// para temporizadores DISCRETOS ("llama a esto dentro de 2 segundos"), pero no
// para interpolar un valor frame a frame. Para eso, este sistema.
//
// Funciones nativas usadas (verificadas con gm-cli manual read):
//   struct_get_names, struct_get, struct_set, is_struct, is_method,
//   instance_exists, variable_instance_get, variable_instance_set,
//   array_length, array_push, array_delete, clamp, delta_time, method
//
// Dependencias: scr_math_util (para las funciones de easing)
//
// USO RAPIDO
//   // En el Create de un controlador persistente (obj_game):
//   //   (nada que inicializar: el sistema se auto-crea)
//   // En su Step:
//   tween_update();
//
//   // Desde cualquier sitio:
//   tween_to(obj_player, { x: 400, y: 200 }, 0.5, ease_out_quad);
//
//   // Con callback al terminar (se ejecuta en el ambito del objetivo):
//   tween_to(obj_menu, { image_alpha: 0 }, 0.3, ease_in_quad, function() {
//       instance_destroy();
//   });
//
//   // Parar:
//   var _t = tween_to(id, { x: 100 }, 1, ease_linear);
//   tween_stop(_t);
// ============================================================================


/// @function __tween_init()
/// @desc    Crea el array global de tweens si no existe. Uso interno.
function __tween_init() {
    if (!variable_global_exists("__tweens")) {
        global.__tweens = [];
    }
}


/// @function tween_to(_objetivo, _props, _duracion, _easing, _on_complete, _retraso)
/// @desc    Interpola una o varias propiedades de una instancia o de un struct.
/// @param   {Id.Instance|Struct} _objetivo   Quien se anima.
/// @param   {Struct}  _props                 Struct { propiedad: valor_final }.
/// @param   {Real}    _duracion              Duración en SEGUNDOS.
/// @param   {Function} _easing               Función de easing (de scr_math_util).
/// @param   {Function} _on_complete          Opcional. Se ejecuta al terminar,
///                                           en el ambito de `_objetivo`.
/// @param   {Real}    _retraso               Opcional. Segundos antes de empezar.
/// @returns {Struct}                         El tween, para poder pararlo.
function tween_to(_objetivo, _props, _duracion, _easing = ease_linear, _on_complete = undefined, _retraso = 0) {
    __tween_init();

    var _es_instancia = false;
    if (is_numeric(_objetivo)) {
        // Los ids de instancia son numericos en tiempo de ejecucion.
        _es_instancia = instance_exists(_objetivo);
    }

    // Guardamos los valores de partida YA, no al empezar: si creas el tween con
    // retraso, el valor inicial debe ser el de AHORA, no el de dentro de 2 s.
    var _nombres = struct_get_names(_props);
    var _iniciales = {};
    var _i;
    for (_i = 0; _i < array_length(_nombres); _i++) {
        var _nombre = _nombres[_i];
        if (_es_instancia) {
            _iniciales[$ _nombre] = variable_instance_get(_objetivo, _nombre);
        } else {
            _iniciales[$ _nombre] = struct_get(_objetivo, _nombre);
        }
    }

    var _tween = {
        objetivo     : _objetivo,
        es_instancia : _es_instancia,
        props        : _props,
        nombres      : _nombres,
        iniciales    : _iniciales,
        duracion     : max(_duracion, 0.0001),
        easing       : is_method(_easing) ? _easing : ease_linear,
        on_complete  : _on_complete,
        retraso      : max(_retraso, 0),
        transcurrido : 0,
        terminado    : false
    };

    array_push(global.__tweens, _tween);
    return _tween;
}


/// @function tween_update()
/// @desc    Avanza todos los tweens activos. LLAMALA UNA VEZ POR FRAME desde
///          el Step de un objeto controlador persistente.
function tween_update() {
    __tween_init();

    var _dt = delta_time / 1000000;
    var _i;

    // Recorremos hacia atras para poder borrar sin descolocar los índices.
    for (_i = array_length(global.__tweens) - 1; _i >= 0; _i--) {
        var _t = global.__tweens[_i];

        // ¿Sigue vivo el objetivo? Si no, el tween sobra.
        if (_t.es_instancia && !instance_exists(_t.objetivo)) {
            array_delete(global.__tweens, _i, 1);
            continue;
        }

        // Retraso inicial.
        if (_t.retraso > 0) {
            _t.retraso -= _dt;
            continue;
        }

        _t.transcurrido += _dt;

        var _progreso = clamp(_t.transcurrido / _t.duracion, 0, 1);
        var _v = _t.easing(_progreso);

        // Aplicamos el valor interpolado a cada propiedad.
        var _j;
        for (_j = 0; _j < array_length(_t.nombres); _j++) {
            var _nombre = _t.nombres[_j];
            var _desde  = _t.iniciales[$ _nombre];
            var _hasta  = _t.props[$ _nombre];
            var _valor  = lerp(_desde, _hasta, _v);

            if (_t.es_instancia) {
                variable_instance_set(_t.objetivo, _nombre, _valor);
            } else {
                struct_set(_t.objetivo, _nombre, _valor);
            }
        }

        // ¿Termino?
        if (_progreso >= 1) {
            _t.terminado = true;

            // Garantizamos el valor final EXACTO: `lerp` con _v = 1 debería
            // darlo, pero los redondeos de coma flotante a veces dejan 99.999.
            for (_j = 0; _j < array_length(_t.nombres); _j++) {
                var _n = _t.nombres[_j];
                if (_t.es_instancia) {
                    variable_instance_set(_t.objetivo, _n, _t.props[$ _n]);
                } else {
                    struct_set(_t.objetivo, _n, _t.props[$ _n]);
                }
            }

            if (is_method(_t.on_complete)) {
                // Reenlazamos al objetivo para que `self` dentro del callback
                // sea la instancia que se anima, no quién llamo al tween.
                if (_t.es_instancia) {
                    var _cb = method(_t.objetivo, _t.on_complete);
                    _cb();
                } else {
                    _t.on_complete();
                }
            }

            array_delete(global.__tweens, _i, 1);
        }
    }
}


/// @function tween_stop(_tween)
/// @desc    Detiene un tween concreto sin ejecutar su callback.
/// @param   {Struct} _tween  El struct devuelto por `tween_to()`.
/// @returns {Bool}           True si estaba activo y se ha detenido.
function tween_stop(_tween) {
    __tween_init();

    var _i;
    for (_i = array_length(global.__tweens) - 1; _i >= 0; _i--) {
        if (global.__tweens[_i] == _tween) {
            array_delete(global.__tweens, _i, 1);
            return true;
        }
    }
    return false;
}


/// @function tween_stop_all(_objetivo)
/// @desc    Detiene todos los tweens de un objetivo. Util antes de destruir
///          una instancia o al reiniciar una room.
/// @param   {Id.Instance|Struct} _objetivo  Objetivo cuyos tweens parar.
/// @returns {Real}                          Cuantos se han detenido.
function tween_stop_all(_objetivo) {
    __tween_init();

    var _contador = 0;
    var _i;
    for (_i = array_length(global.__tweens) - 1; _i >= 0; _i--) {
        if (global.__tweens[_i].objetivo == _objetivo) {
            array_delete(global.__tweens, _i, 1);
            _contador++;
        }
    }
    return _contador;
}


/// @function tween_count()
/// @desc    Cuantos tweens hay activos ahora mismo. Para depurar fugas: si
///          este número crece sin parar, se te está escapando alguno.
/// @returns {Real}
function tween_count() {
    __tween_init();
    return array_length(global.__tweens);
}


/// @function tween_clear_all()
/// @desc    Vacia la lista de tweens. Llamala al cambiar de room si tus tweens
///          no sobreviven al cambio (los de instancias no lo hacen).
function tween_clear_all() {
    global.__tweens = [];
}


/// @function tween_delay(_segundos, _callback, _dueno)
/// @desc    Atajo para "haz esto dentro de X segundos", sin crear un alarm.
///          Equivalente a `call_later()` pero integrable con tu propio
///          bucle de tweens.
/// @param   {Real}     _segundos  Segundos de espera.
/// @param   {Function} _callback  Que ejecutar.
/// @param   {Any}      _dueno     Opcional. Ambito del callback (`id`).
/// @returns {Struct}              El tween, por si quieres cancelarlo.
function tween_delay(_segundos, _callback, _dueno = undefined) {
    // Truco: interpolamos una propiedad inventada de un struct desechable.
    // El objetivo no necesita existir de verdad, solo ser un struct válido.
    var _falso = { __t: 0 };

    var _cb = is_undefined(_dueno) ? _callback : method(_dueno, _callback);

    return tween_to(_falso, { __t: 1 }, max(_segundos, 0.0001), ease_linear, _cb);
}
