// ============================================================================
// scr_math_util.gml
// Utilidades matemáticas y funciones de easing para GameMaker LTS 2026.
//
// IMPORTANTE - NO REIMPLEMENTES LO QUE YA ES NATIVO.
// Verificado contra el manual con `gm-cli manual read "<función>"`:
//   YA EXISTEN (no están aquí): lerp, clamp, angle_difference, dsin, dcos,
//   sin, cos, abs, sign, min, max, floor, ceil, round, frac, sqrt, power,
//   point_distance, point_direction, lengthdir_x, lengthdir_y, dot_product.
//
//   NO EXISTEN como nativas (por eso están aquí): approach, wave, remap,
//   lerp_dt, ease_* (easing), smoothstep, snap.
//
// Dependencias: ninguna.
// Verificado: GameMaker LTS 2026.0 (IDE 16 / GMS2 Runtime 23) - agosto 2026
// ============================================================================


/// @function approach(_actual, _objetivo, _paso)
/// @desc    Acerca `_actual` a `_objetivo` como mucho `_paso` unidades, sin
///          pasarse. Es la forma correcta de acelerar/frenar sin oscilar.
/// @param   {Real} _actual    Valor actual.
/// @param   {Real} _objetivo  Valor al que queremos llegar.
/// @param   {Real} _paso      Incremento máximo por llamada (siempre positivo).
/// @returns {Real}            Nuevo valor, como mucho en `_objetivo`.
function approach(_actual, _objetivo, _paso) {
    if (_actual < _objetivo) {
        return min(_actual + _paso, _objetivo);
    }
    return max(_actual - _paso, _objetivo);
}


/// @function wave(_desde, _hasta, _duracion, _offset)
/// @desc    Oscila entre `_desde` y `_hasta` con una onda sinusoidal suave.
///          Ideal para flotar, pulsar, brillar o cualquier movimiento ciclico.
/// @param   {Real} _desde     Valor mínimo.
/// @param   {Real} _hasta     Valor máximo.
/// @param   {Real} _duracion  Milisegundos que dura un ciclo completo.
/// @param   {Real} _offset    Desfase en milisegundos (para desincronizar
///                            varios objetos que usan la misma onda).
/// @returns {Real}            Valor interpolado en el instante actual.
function wave(_desde, _hasta, _duracion, _offset = 0) {
    // current_time son los milisegundos desde que arranco el juego.
    var _t = ((current_time + _offset) % _duracion) / _duracion;
    // -dcos va de -1 a 1 pasando por el mínimo en t=0: arranca en `_desde`.
    var _s = (-dcos(_t * 360) + 1) / 2;
    return lerp(_desde, _hasta, _s);
}


/// @function remap(_valor, _in_min, _in_max, _out_min, _out_max)
/// @desc    Reescala un valor de un rango a otro. Equivale a `map_range` de
///          otros motores.
/// @param   {Real} _valor     Valor de entrada.
/// @param   {Real} _in_min    Mínimo del rango de entrada.
/// @param   {Real} _in_max    Máximo del rango de entrada.
/// @param   {Real} _out_min   Mínimo del rango de salida.
/// @param   {Real} _out_max   Máximo del rango de salida.
/// @returns {Real}            Valor reescalado (puede salirse del rango).
function remap(_valor, _in_min, _in_max, _out_min, _out_max) {
    // Guarda contra division por cero si el rango de entrada está degenerado.
    if (_in_max == _in_min) { return _out_min; }
    return _out_min + ((_valor - _in_min) / (_in_max - _in_min)) * (_out_max - _out_min);
}


/// @function remap_clamped(_valor, _in_min, _in_max, _out_min, _out_max)
/// @desc    Igual que `remap()` pero garantizando que la salida quede dentro
///          de [_out_min, _out_max].
/// @param   {Real} _valor     Valor de entrada.
/// @param   {Real} _in_min    Mínimo del rango de entrada.
/// @param   {Real} _in_max    Máximo del rango de entrada.
/// @param   {Real} _out_min   Mínimo del rango de salida.
/// @param   {Real} _out_max   Máximo del rango de salida.
/// @returns {Real}            Valor reescalado y limitado.
function remap_clamped(_valor, _in_min, _in_max, _out_min, _out_max) {
    return clamp(remap(_valor, _in_min, _in_max, _out_min, _out_max), _out_min, _out_max);
}


/// @function lerp_dt(_actual, _objetivo, _factor, _dt)
/// @desc    Interpolación exponencial CORREGIDA por delta time.
///          `lerp(a, b, 0.1)` a 60 fps NO es lo mismo que a 144 fps: con está
///          función el resultado es identico en ambos. Usala siempre que
///          interpoles por frame (camaras, suavizados, seguimiento de UI).
/// @param   {Real} _actual    Valor actual.
/// @param   {Real} _objetivo  Valor al que nos acercamos.
/// @param   {Real} _factor    Factor de suavizado por segundo (0.1 = suave).
/// @param   {Real} _dt        Delta time en SEGUNDOS (delta_time / 1000000).
/// @returns {Real}            Valor interpolado, independiente del framerate.
function lerp_dt(_actual, _objetivo, _factor, _dt) {
    return lerp(_actual, _objetivo, 1 - power(1 - _factor, _dt * 60));
}


/// @function smoothstep(_borde0, _borde1, _x)
/// @desc    Interpolación suave con aceleración y frenado en los extremos.
///          Devuelve 0 si x <= borde0, 1 si x >= borde1, y una curva suave
///          (3t^2 - 2t^3) en medio. Muy usada para fundidos y transiciones.
/// @param   {Real} _borde0    Inicio del rango.
/// @param   {Real} _borde1    Final del rango.
/// @param   {Real} _x         Valor de entrada.
/// @returns {Real}            0..1
function smoothstep(_borde0, _borde1, _x) {
    if (_borde0 == _borde1) { return (_x < _borde0) ? 0 : 1; }
    var _t = clamp((_x - _borde0) / (_borde1 - _borde0), 0, 1);
    return _t * _t * (3 - 2 * _t);
}


/// @function snap(_valor, _incremento)
/// @desc    Redondea `_valor` al multiplo más cercano de `_incremento`.
///          Util para grids, pixel-perfect y alineacion de UI.
/// @param   {Real} _valor       Valor a ajustar.
/// @param   {Real} _incremento  Paso al que ajustar (p. ej. 16, 32, 1).
/// @returns {Real}              Valor ajustado.
function snap(_valor, _incremento) {
    if (_incremento == 0) { return _valor; }
    return round(_valor / _incremento) * _incremento;
}


// ---------------------------------------------------------------------------
// FUNCIONES DE EASING
// ---------------------------------------------------------------------------
// Todas reciben `_t` en el rango 0..1 y devuelven un valor que normalmente
// está en 0..1 (los *back* y *elastic* se salen un poco: es intencionado,
// es lo que produce el rebote).
//
// NOTA: GameMaker tiene `animcurve_*`, pero exige CREAR UN ASSET de curva de
// animación en el IDE. Estas funciones no necesitan ningun asset: son código
// puro y funcionan en cualquier proyecto.
//
// No existe ninguna función de easing nativa en GML (verificado con
// `gm-cli manual read "easing"` -> sin resultados).
// ---------------------------------------------------------------------------

/// @function ease_linear(_t)
/// @desc    Sin easing: progresion constante.
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_linear(_t) {
    return _t;
}

/// @function ease_in_sine(_t)
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_in_sine(_t) {
    return 1 - dcos(_t * 90);
}

/// @function ease_out_sine(_t)
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_out_sine(_t) {
    return dsin(_t * 90);
}

/// @function ease_in_out_sine(_t)
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_in_out_sine(_t) {
    return -(dcos(_t * 180) - 1) / 2;
}

/// @function ease_in_quad(_t)
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_in_quad(_t) {
    return _t * _t;
}

/// @function ease_out_quad(_t)
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_out_quad(_t) {
    return 1 - (1 - _t) * (1 - _t);
}

/// @function ease_in_out_quad(_t)
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_in_out_quad(_t) {
    return (_t < 0.5) ? (2 * _t * _t) : (1 - power(-2 * _t + 2, 2) / 2);
}

/// @function ease_in_cubic(_t)
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_in_cubic(_t) {
    return _t * _t * _t;
}

/// @function ease_out_cubic(_t)
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_out_cubic(_t) {
    return 1 - power(1 - _t, 3);
}

/// @function ease_in_out_cubic(_t)
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_in_out_cubic(_t) {
    return (_t < 0.5) ? (4 * _t * _t * _t) : (1 - power(-2 * _t + 2, 3) / 2);
}

/// @function ease_out_back(_t)
/// @desc    Sale rápido, se pasa y vuelve. Ideal para pop-ins de UI.
/// @param   {Real} _t  0..1
/// @returns {Real}     Puede superar 1 momentaneamente (el rebote).
function ease_out_back(_t) {
    var _c1 = 1.70158;
    var _c3 = _c1 + 1;
    return 1 + _c3 * power(_t - 1, 3) + _c1 * power(_t - 1, 2);
}

/// @function ease_in_back(_t)
/// @param   {Real} _t  0..1
/// @returns {Real}     Puede bajar de 0 momentaneamente.
function ease_in_back(_t) {
    var _c1 = 1.70158;
    var _c3 = _c1 + 1;
    return _c3 * _t * _t * _t - _c1 * _t * _t;
}

/// @function ease_out_elastic(_t)
/// @desc    Rebote elastico al final. Muy vistoso para recompensas o golpes.
/// @param   {Real} _t  0..1
/// @returns {Real}     Puede salirse de 0..1 durante el rebote.
function ease_out_elastic(_t) {
    if (_t <= 0) { return 0; }
    if (_t >= 1) { return 1; }
    // (2*pi/3) radianos == 120 grados: la constante estandar de está curva.
    var _c4 = 120;
    return power(2, -10 * _t) * dsin((_t * 10 - 0.75) * _c4) + 1;
}

/// @function ease_out_bounce(_t)
/// @desc    Rebote tipo pelota que pierde altura en cada salto.
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_out_bounce(_t) {
    var _n1 = 7.5625;
    var _d1 = 2.75;
    if (_t < 1 / _d1) {
        return _n1 * _t * _t;
    } else if (_t < 2 / _d1) {
        var _t2 = _t - 1.5 / _d1;
        return _n1 * _t2 * _t2 + 0.75;
    } else if (_t < 2.5 / _d1) {
        var _t3 = _t - 2.25 / _d1;
        return _n1 * _t3 * _t3 + 0.9375;
    }
    var _t4 = _t - 2.625 / _d1;
    return _n1 * _t4 * _t4 + 0.984375;
}

/// @function ease_out_expo(_t)
/// @desc    Caida explosiva al principio y frenado largo. Buena para aparecer.
/// @param   {Real} _t  0..1
/// @returns {Real}     0..1
function ease_out_expo(_t) {
    return (_t >= 1) ? 1 : (1 - power(2, -10 * _t));
}

/// Tabla de easings por nombre, para poder elegirlos desde datos.
/// Uso: var _fn = EASINGS[$ "out_back"];  var _v = _fn(0.5);
/// @desc Diccionario nombre -> función de easing.
global.EASINGS = {
    linear      : ease_linear,
    in_sine     : ease_in_sine,
    out_sine    : ease_out_sine,
    in_out_sine : ease_in_out_sine,
    in_quad     : ease_in_quad,
    out_quad    : ease_out_quad,
    in_out_quad : ease_in_out_quad,
    in_cubic    : ease_in_cubic,
    out_cubic   : ease_out_cubic,
    in_out_cubic: ease_in_out_cubic,
    in_back     : ease_in_back,
    out_back    : ease_out_back,
    out_elastic : ease_out_elastic,
    out_bounce  : ease_out_bounce,
    out_expo    : ease_out_expo
};
