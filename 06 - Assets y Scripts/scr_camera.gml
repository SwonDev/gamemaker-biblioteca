// ============================================================================
// scr_camera.gml
// Cámara 2D con seguimiento, deadzone, look-ahead, límites de sala y shake.
//
// Funciones nativas usadas (todas verificadas con gm-cli manual read):
//   camera_create, camera_destroy, camera_set_view_pos, camera_set_view_size,
//   camera_get_view_x, camera_get_view_y, camera_get_view_width,
//   camera_get_view_height, camera_set_view_target, view_camera,
//   window_get_width, window_get_height, clamp, lerp, approach
//
// Dependencias: scr_math_util (usa approach y lerp_dt)
//
// USO RAPIDO
//   // En el Create de obj_camera:
//   cam = camera_create();
//   cam_init(cam, 640, 360);              // tamaño de la vista
//   cam_set_target(cam, obj_player);
//   cam_set_deadzone(cam, 80, 50);        // píxeles de margen
//   cam_set_smooth(cam, 0.15);            // 0 = rigida, 1 = instantanea
//   cam_set_lookahead(cam, 48, 24);       // anticipa hacia donde miras
//   cam_set_bounds(cam, 0, 0, room_width, room_height);
//   view_camera[0] = cam;
//
//   // En el Step de obj_camera (después de que el jugador se haya movido):
//   cam_update(cam);
//
//   // Cuando el jugador recibe un golpe:
//   cam_shake(cam, 8, 0.4);
// ============================================================================


/// @function cam_init(_cam, _ancho_vista, _alto_vista)
/// @desc    Inicializa una cámara y la asocia a structs de configuración.
///          Guarda el estado en global.__cam_data, indexado por la cámara.
/// @param   {Id.Camera} _cam            Cámara creada con `camera_create()`.
/// @param   {Real}      _ancho_vista    Ancho de la vista en píxeles de room.
/// @param   {Real}      _alto_vista     Alto de la vista en píxeles de room.
/// @returns {Struct}                    El struct de datos de la cámara.
function cam_init(_cam, _ancho_vista, _alto_vista) {
    camera_set_view_size(_cam, _ancho_vista, _alto_vista);

    var _datos = {
        cam         : _cam,
        objetivo    : noone,
        // Deadzone: rectangulo centrado en el objetivo dentro del cuál la
        // cámara NO se mueve. Evita el temblor constante al moverte un pixel.
        dz_ancho    : 0,
        dz_alto     : 0,
        // Suavizado: 0 = la cámara sigue con deadzone pura,
        //            >0 = interpolación exponencial corregida por delta time.
        suavizado   : 0,
        // Look-ahead: cuánto se adelanta la cámara en la dirección de movimiento.
        la_x        : 0,
        la_y        : 0,
        la_actual_x : 0,
        la_actual_y : 0,
        // Limites de la sala. -1 = sin límite en ese borde.
        lim_izq     : 0,
        lim_arr     : 0,
        lim_der     : -1,
        lim_aba     : -1,
        // Estado del shake.
        shake_mag   : 0,
        shake_dur   : 0,
        shake_t     : 0,
        shake_x     : 0,
        shake_y     : 0,
        // Posición logica (sin shake), en píxeles de room.
        x           : 0,
        y           : 0
    };

    if (!variable_global_exists("__cam_data")) {
        global.__cam_data = {};
    }
    global.__cam_data[$ string(_cam)] = _datos;
    return _datos;
}


/// @function cam_get_data(_cam)
/// @desc    Devuelve el struct de configuración de una cámara ya inicializada.
/// @param   {Id.Camera} _cam  Cámara.
/// @returns {Struct}          Datos, o `undefined` si no se inicializo.
function cam_get_data(_cam) {
    if (!variable_global_exists("__cam_data")) { return undefined; }
    return global.__cam_data[$ string(_cam)];
}


/// @function cam_set_target(_cam, _objetivo)
/// @desc    Instancia u objeto al que sigue la cámara.
/// @param   {Id.Camera} _cam        Cámara.
/// @param   {Id.Instance} _objetivo Instancia (o `noone` para liberarla).
function cam_set_target(_cam, _objetivo) {
    var _d = cam_get_data(_cam);
    if (!is_struct(_d)) { return; }
    _d.objetivo = _objetivo;
}


/// @function cam_set_deadzone(_cam, _ancho, _alto)
/// @desc    Define el rectangulo de inercia. Con 0 la cámara sigue al objetivo
///          de forma estricta (puede temblar con movimientos pequenos).
/// @param   {Id.Camera} _cam    Cámara.
/// @param   {Real}      _ancho  Ancho del deadzone en píxeles (total, no mitad).
/// @param   {Real}      _alto   Alto del deadzone en píxeles (total, no mitad).
function cam_set_deadzone(_cam, _ancho, _alto) {
    var _d = cam_get_data(_cam);
    if (!is_struct(_d)) { return; }
    _d.dz_ancho = _ancho;
    _d.dz_alto  = _alto;
}


/// @function cam_set_smooth(_cam, _factor)
/// @desc    Suavizado exponencial corregido por delta time.
/// @param   {Id.Camera} _cam     Cámara.
/// @param   {Real}      _factor  0 = sin suavizar, 0.1 = suave, 1 = instantaneo.
function cam_set_smooth(_cam, _factor) {
    var _d = cam_get_data(_cam);
    if (!is_struct(_d)) { return; }
    _d.suavizado = clamp(_factor, 0, 1);
}


/// @function cam_set_lookahead(_cam, _x, _y)
/// @desc    Cuantos píxeles se adelanta la cámara en la dirección en la que
///          se mueve el objetivo. Hace que veas antes lo que viene.
/// @param   {Id.Camera} _cam  Cámara.
/// @param   {Real}      _x    Pixeles maximos de anticipacion horizontal.
/// @param   {Real}      _y    Pixeles maximos de anticipacion vertical.
function cam_set_lookahead(_cam, _x, _y) {
    var _d = cam_get_data(_cam);
    if (!is_struct(_d)) { return; }
    _d.la_x = _x;
    _d.la_y = _y;
}


/// @function cam_set_bounds(_cam, _izq, _arr, _der, _aba)
/// @desc    Limites de la sala. Si la vista es más grande que los límites, la
///          cámara se centra en ese eje en lugar de salirse.
/// @param   {Id.Camera} _cam  Cámara.
/// @param   {Real}      _izq  Limite izquierdo (o -1 para ninguno).
/// @param   {Real}      _arr  Limite superior (o -1 para ninguno).
/// @param   {Real}      _der  Limite derecho (o -1 para ninguno).
/// @param   {Real}      _aba  Limite inferior (o -1 para ninguno).
function cam_set_bounds(_cam, _izq, _arr, _der, _aba) {
    var _d = cam_get_data(_cam);
    if (!is_struct(_d)) { return; }
    _d.lim_izq = _izq;
    _d.lim_arr = _arr;
    _d.lim_der = _der;
    _d.lim_aba = _aba;
}


/// @function cam_shake(_cam, _magnitud, _duracion)
/// @desc    Dispara un screen shake. Si ya habia uno activo, se queda el más
///          fuerte de los dos (evita que golpes seguidos se cancelen).
/// @param   {Id.Camera} _cam        Cámara.
/// @param   {Real}      _magnitud   Pixeles maximos de desplazamiento.
/// @param   {Real}      _duracion   Duración en SEGUNDOS.
function cam_shake(_cam, _magnitud, _duracion) {
    var _d = cam_get_data(_cam);
    if (!is_struct(_d)) { return; }

    // Si el shake nuevo es más fuerte, machaca al anterior.
    if (_magnitud >= _d.shake_mag || _d.shake_t >= _d.shake_dur) {
        _d.shake_mag = _magnitud;
        _d.shake_dur = max(_duracion, 0.001);
        _d.shake_t   = 0;
    }
}


/// @function cam_update(_cam)
/// @desc    Actualiza la cámara: look-ahead, deadzone, suavizado, límites y
///          shake. LLAMALA EN EL STEP (Begin Step si tu jugador se mueve en
///          Step y quieres que la cámara no vaya un frame por detras).
/// @param   {Id.Camera} _cam  Cámara.
function cam_update(_cam) {
    var _d = cam_get_data(_cam);
    if (!is_struct(_d)) { return; }

    var _vw = camera_get_view_width(_cam);
    var _vh = camera_get_view_height(_cam);

    // Posición logica actual (sin shake).
    var _cx = _d.x + _vw / 2;
    var _cy = _d.y + _vh / 2;

    if (instance_exists(_d.objetivo)) {
        var _tx = _d.objetivo.x;
        var _ty = _d.objetivo.y;

        // --- Look-ahead -----------------------------------------------------
        // Derivamos la velocidad comparando con la posición del frame anterior.
        var _vx = 0;
        var _vy = 0;
        if (struct_exists(_d, "obj_x_prev")) {
            _vx = _tx - _d.obj_x_prev;
            _vy = _ty - _d.obj_y_prev;
        }
        _d.obj_x_prev = _tx;
        _d.obj_y_prev = _ty;

        // Normalizamos la velocidad a [-1, 1] con un tope para que un
        // teletransporte no dispare la cámara al otro lado de la sala.
        var _la_obj_x = clamp(_vx * 2, -1, 1) * _d.la_x;
        var _la_obj_y = clamp(_vy * 2, -1, 1) * _d.la_y;

        // El look-ahead se suaviza: si se aplicara de golpe, la cámara daria
        // un tiron cada vez que inviertes la dirección.
        _d.la_actual_x = lerp(_d.la_actual_x, _la_obj_x, 0.15);
        _d.la_actual_y = lerp(_d.la_actual_y, _la_obj_y, 0.15);

        _tx += _d.la_actual_x;
        _ty += _d.la_actual_y;

        // --- Deadzone -------------------------------------------------------
        // Solo empujamos la cámara si el objetivo sale de la caja de inercia.
        var _dz_izq = _cx - _d.dz_ancho / 2;
        var _dz_der = _cx + _d.dz_ancho / 2;
        var _dz_arr = _cy - _d.dz_alto  / 2;
        var _dz_aba = _cy + _d.dz_alto  / 2;

        if (_tx < _dz_izq) { _cx -= (_dz_izq - _tx); }
        if (_tx > _dz_der) { _cx += (_tx - _dz_der); }
        if (_ty < _dz_arr) { _cy -= (_dz_arr - _ty); }
        if (_ty > _dz_aba) { _cy += (_ty - _dz_aba); }

        // --- Suavizado (opcional) -------------------------------------------
        // Con suavizado > 0 ignoramos la deadzone y seguimos al objetivo con
        // interpolación corregida por delta time. Son dos estilos distintos:
        // elige uno u otro según el juego, no los mezcles con valores raros.
        if (_d.suavizado > 0) {
            var _dt = delta_time / 1000000;
            _cx = lerp_dt(_cx, _tx, _d.suavizado, _dt);
            _cy = lerp_dt(_cy, _ty, _d.suavizado, _dt);
        }
    }

    // --- Limites de la sala -------------------------------------------------
    var _x_final = _cx - _vw / 2;
    var _y_final = _cy - _vh / 2;

    if (_d.lim_der >= 0) {
        if (_d.lim_der - _d.lim_izq < _vw) {
            // La sala es más estrecha que la vista: centramos en horizontal.
            _x_final = _d.lim_izq + ((_d.lim_der - _d.lim_izq) - _vw) / 2;
        } else {
            _x_final = clamp(_x_final, _d.lim_izq, _d.lim_der - _vw);
        }
    }
    if (_d.lim_aba >= 0) {
        if (_d.lim_aba - _d.lim_arr < _vh) {
            _y_final = _d.lim_arr + ((_d.lim_aba - _d.lim_arr) - _vh) / 2;
        } else {
            _y_final = clamp(_y_final, _d.lim_arr, _d.lim_aba - _vh);
        }
    }

    _d.x = _x_final;
    _d.y = _y_final;

    // --- Shake --------------------------------------------------------------
    _d.shake_x = 0;
    _d.shake_y = 0;
    if (_d.shake_dur > 0 && _d.shake_t < _d.shake_dur) {
        _d.shake_t += delta_time / 1000000;

        // La magnitud decae linealmente hasta 0 al final de la duración.
        var _progreso = clamp(_d.shake_t / _d.shake_dur, 0, 1);
        var _mag = _d.shake_mag * (1 - _progreso);

        // Aleatorio en circulo en vez de en cuadrado: el movimiento es más
        // organico y no aparecen los picos en las diagonales.
        var _ang = random(360);
        _d.shake_x = lengthdir_x(_mag, _ang);
        _d.shake_y = lengthdir_y(_mag, _ang);
    } else if (_d.shake_dur > 0) {
        // Shake terminado: reseteamos para que el siguiente empiece limpio.
        _d.shake_mag = 0;
        _d.shake_dur = 0;
        _d.shake_t   = 0;
    }

    // --- Aplicamos a la cámara real -----------------------------------------
    // Redondeamos: una cámara en posiciones con decimales provoca que los
    // sprites pixel art se vean borrosos al dibujarse entre píxeles.
    camera_set_view_pos(_cam, round(_x_final + _d.shake_x), round(_y_final + _d.shake_y));
}


/// @function cam_destroy(_cam)
/// @desc    Libera la cámara y su struct de datos. LLAMALA EN CLEAN UP.
/// @param   {Id.Camera} _cam  Cámara.
function cam_destroy(_cam) {
    if (variable_global_exists("__cam_data")) {
        variable_struct_remove(global.__cam_data, string(_cam));
    }
    camera_destroy(_cam);
}


/// @function cam_center_on(_cam, _x, _y)
/// @desc    Centra la cámara al instante en un punto (sin suavizado ni shake).
///          Util al cambiar de room o al hacer un respawn.
/// @param   {Id.Camera} _cam  Cámara.
/// @param   {Real}      _x    Coordenada X de la room.
/// @param   {Real}      _y    Coordenada Y de la room.
function cam_center_on(_cam, _x, _y) {
    var _d = cam_get_data(_cam);
    if (!is_struct(_d)) { return; }

    var _vw = camera_get_view_width(_cam);
    var _vh = camera_get_view_height(_cam);

    _d.x = _x - _vw / 2;
    _d.y = _y - _vh / 2;
    _d.shake_mag = 0;
    _d.shake_dur = 0;
    _d.shake_t   = 0;
    _d.la_actual_x = 0;
    _d.la_actual_y = 0;

    camera_set_view_pos(_cam, round(_d.x), round(_d.y));
}


/// @function cam_fit_window(_cam, _ancho_base, _alto_base)
/// @desc    Ajusta el tamaño del VIEWPORT al de la ventana manteniendo la
///          proporción de la vista. Llamala en el evento Window Resize o
///          tras cambiar a pantalla completa: sin esto, la imagen se estira.
/// @param   {Id.Camera} _cam         Cámara.
/// @param   {Real}      _ancho_base  Ancho de la vista en píxeles de room.
/// @param   {Real}      _alto_base   Alto de la vista en píxeles de room.
function cam_fit_window(_cam, _ancho_base, _alto_base) {
    var _ww = window_get_width();
    var _wh = window_get_height();

    var _escala = min(_ww / _ancho_base, _wh / _alto_base);
    var _vp_w = floor(_ancho_base * _escala);
    var _vp_h = floor(_alto_base  * _escala);

    view_wport[0] = _vp_w;
    view_hport[0] = _vp_h;
    view_xport[0] = floor((_ww - _vp_w) / 2);
    view_yport[0] = floor((_wh - _vp_h) / 2);

    camera_set_view_size(_cam, _ancho_base, _alto_base);
}
