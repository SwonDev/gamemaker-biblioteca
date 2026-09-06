// ============================================================================
// scr_audio.gml
// Gestor de audio completo: buses y emisores por categoría, mezcla con
// ducking, banco de tomas con round robin, cupo de voces con fundido, anillo
// de emisores posicionales y crossfade de música/ambiente.
//
// POR QUÉ ESTE FICHERO
//   Sin él, cada proyecto reinventa lo mismo mal: sonidos que suenan siempre
//   igual de fuerte (§5.1), el mismo disparo repetido cincuenta veces sin
//   variación, un "cambiar de música" que corta en seco, y un límite de
//   canales (128 por defecto) que protege el motor pero no tu mezcla. Este
//   script junta la solución a los cinco problemas en una sola API.
//
// CÓMO SE MONTAN LOS BUSES DE VERDAD (la razón de todo lo que sigue)
//   El audio 2D (`audio_play_sound`) y el 3D directo (`audio_play_sound_at`)
//   acaban SIEMPRE en el bus principal: solo lo que pasa por un EMISOR
//   asignado a un bus recibe su ganancia y sus efectos. Por eso cada
//   categoría (música, sfx, ui, voz, ambiente) tiene su propio emisor, y por
//   eso el sonido posicional usa un anillo de emisores reutilizables en vez
//   de `audio_play_sound_at()`. — Manual, "Audio Effects".
//
// ARQUITECTURA
//   global.audio = {
//       bus      : { musica, sfx, ui, voz, ambiente }   structs AudioBus
//       em       : { musica, sfx, ui, voz, ambiente }   un emisor por bus,
//                                                        sin atenuación (no
//                                                        son posicionales)
//       anillo   : [ ... ]     emisores POSICIONALES, todos al bus "sfx"
//       anillo_i : índice del próximo emisor del anillo
//       voces    : { "nombre_del_sonido": [ids...] }    cupo por sonido
//       apagando : [ { voz, restante } ]                fundidos en curso
//       volumen  : { musica, sfx, ui, voz, ambiente }   sliders 0..1
//       musica_snd, musica_voz, ambiente_snd, ambiente_voz, voz_voz, duck
//   }
//
// USO RÁPIDO (todo desde un controlador persistente, p. ej. obj_audio)
//   // Create
//   audio_init();
//
//   // Step (o Begin Step)
//   audio_step();
//
//   // Clean Up
//   audio_destruir();
//
//   // Desde cualquier sitio del juego:
//   sfx(snd_disparo);                                  // efecto suelto
//   sonar_en(snd_explosion, other.x, other.y, 0.9);     // efecto EN el mundo
//   sonar_limitado(snd_impacto, 4, db_to_lin(-8));      // como mucho 4 a la vez
//   sfx_ui(snd_click, 1, 1);                            // sonido de interfaz
//   musica_poner(snd_boss_theme);                       // crossfade de música
//   ambiente_poner(snd_bosque_bed);                     // crossfade de ambiente
//   voz_decir(snd_linea_01);                             // corta la anterior
//
//   // Create de obj_ambiente_bosque
//   banco_aves = banco_crear([snd_ave_1, snd_ave_2, snd_ave_3, snd_ave_4]);
//   sonar_en(banco_siguiente(banco_aves), x, y, db_to_lin(-14));
//
//   // El jugador mueve un slider en Opciones
//   global.audio.volumen.musica = 0.4;
//   mezcla_aplicar();
//
// Funciones nativas usadas (verificadas con gm-cli manual read / buscar.py):
//   audio_bus_create, audio_emitter_create, audio_emitter_bus,
//   audio_emitter_falloff, audio_emitter_position, audio_emitter_free,
//   audio_play_sound_ext, audio_sound_gain, audio_stop_sound,
//   audio_is_playing, audio_system_is_available, audio_falloff_set_model,
//   audio_falloff_inverse_distance_clamped, audio_listener_position,
//   audio_get_name, db_to_lin, camera_get_active, camera_get_view_x/y,
//   camera_get_view_width/height, power, irandom, random_range, lerp, clamp,
//   struct_get, struct_set, struct_get_names, struct_exists, array_push,
//   array_delete, array_length, is_undefined, variable_global_exists,
//   delta_time
//
// Dependencias: ninguna.
//
// LO QUE ESTE SCRIPT NO CUBRE (y dónde está)
//   - Oclusión por paredes y zonas de reverberación: no forma parte del cupo
//     mínimo reutilizable, tienen coste propio por proyecto (filtros, rayos).
//     Ver "13 - Diseño y producción de videojuegos/09" §5.3.
//   - Voz, subtítulos y localización de audio: fuera de alcance de un script
//     genérico. Ver la misma carpeta, documento "14".
// ============================================================================


// ─────────────────────────── Configuración ──────────────────────────────
// Headroom en dB de cada categoría: deja hueco para que el ducking y los
// picos de SFX no saturen el bus principal. Ajusta estas cifras a tu mezcla,
// no el código que las usa.
#macro AUDIO_HEADROOM_MUSICA    -10
#macro AUDIO_HEADROOM_SFX        -6
#macro AUDIO_HEADROOM_UI         -9
#macro AUDIO_HEADROOM_AMBIENTE  -20
// La voz es la referencia: 0 dB, no se le resta nada en mezcla_aplicar().

// Ducking: cuánto baja la música mientras hay diálogo y a qué velocidad.
// Bajar rápido y subir despacio; si sube tan rápido como baja, se oye
// "bombear" en cada pausa del diálogo.
#macro AUDIO_DUCK_OBJETIVO_DB   -9
#macro AUDIO_DUCK_VEL_BAJAR    0.30
#macro AUDIO_DUCK_VEL_SUBIR    0.04

// Anillo de emisores posicionales: referencia, máxima y factor de atenuación
// (ver §5.1 de la biblioteca). Media pantalla / pantalla y media es un buen
// punto de partida; ajústalo a tu resolución de mundo.
#macro AUDIO_ANILLO_FALLOFF_REF   240
#macro AUDIO_ANILLO_FALLOFF_MAX   720


// ══════════════════════ Inicialización y ciclo de vida ═════════════════════

/// @function audio_init([_emisores_anillo])
/// @desc    Crea los buses, los emisores de categoría y el anillo de
///          emisores posicionales. Llámala UNA sola vez, desde el Create de
///          un objeto persistente (p. ej. obj_audio) creado en la sala de
///          arranque.
/// @param   {Real} [_emisores_anillo]  Tamaño del anillo posicional (por
///                                     defecto 24: sobra para casi cualquier
///                                     juego 2D con SFX cortos).
function audio_init(_emisores_anillo = 24)
{
    if (variable_global_exists("audio")) { return; }   // no reinicializar dos veces

    // El modelo por defecto es "audio_falloff_none": con él la ganancia vale
    // siempre 1, aunque el emisor esté a dos pantallas. Es EL bug de audio
    // más frecuente en GameMaker. Se fija una sola vez, para todo el juego.
    audio_falloff_set_model(audio_falloff_inverse_distance_clamped);

    global.audio = {
        bus      : {},
        em       : {},
        anillo   : [],
        anillo_i : 0,
        voces    : {},      // "nombre_del_sonido" -> array de ids en curso
        apagando : [],      // { voz, restante } con fundido de salida activo
        volumen  : { musica: 0.7, sfx: 1.0, ui: 0.8, voz: 1.0, ambiente: 0.6 },
        musica_snd   : undefined, musica_voz   : -1,
        ambiente_snd : undefined, ambiente_voz : -1,
        voz_voz  : -1,
        duck     : 1        // 1 = sin agachar · baja hacia AUDIO_DUCK_OBJETIVO_DB al hablar
    };

    // Un bus y un emisor por categoría: es la ÚNICA vía de entrada al bus.
    // Con factor 0 la atenuación no existe en NINGÚN modelo (no son sonidos
    // posicionales, son categorías globales de mezcla).
    var _categorias = ["musica", "sfx", "ui", "voz", "ambiente"];
    for (var _i = 0; _i < array_length(_categorias); _i += 1)
    {
        var _cat = _categorias[_i];
        var _bus = audio_bus_create();
        var _em  = audio_emitter_create();
        audio_emitter_bus(_em, _bus);
        audio_emitter_falloff(_em, 1, 2, 0);
        struct_set(global.audio.bus, _cat, _bus);
        struct_set(global.audio.em,  _cat, _em);
    }

    // El anillo de emisores POSICIONALES comparte el bus "sfx" con la
    // categoría de arriba: unos suenan "en el mundo" (sonar_en) y otros "en
    // ninguna parte" (sfx, sonar_limitado), pero pasan por el mismo control
    // de volumen y por el mismo ducking.
    repeat (_emisores_anillo)
    {
        var _em_pos = audio_emitter_create();
        audio_emitter_bus(_em_pos, global.audio.bus.sfx);
        audio_emitter_falloff(_em_pos, AUDIO_ANILLO_FALLOFF_REF, AUDIO_ANILLO_FALLOFF_MAX, 1);
        array_push(global.audio.anillo, _em_pos);
    }

    mezcla_aplicar();
}

/// @function audio_destruir()
/// @desc    Libera TODOS los emisores (son recursos dinámicos: sin esto hay
///          fuga de memoria) y para lo que estuviera sonando. Llámala desde
///          el Clean Up del mismo objeto que llamó a audio_init().
///          Los buses NO se liberan: los recoge el recolector de basura en
///          cuanto nadie los referencia.
function audio_destruir()
{
    if (!variable_global_exists("audio")) { return; }

    var _nombres = struct_get_names(global.audio.em);
    for (var _i = 0; _i < array_length(_nombres); _i += 1)
    {
        audio_emitter_free(struct_get(global.audio.em, _nombres[_i]));
    }

    for (var _i = 0; _i < array_length(global.audio.anillo); _i += 1)
    {
        audio_emitter_free(global.audio.anillo[_i]);
    }
    global.audio.anillo = [];

    if (global.audio.musica_voz != -1)   { audio_stop_sound(global.audio.musica_voz);   global.audio.musica_voz   = -1; }
    if (global.audio.ambiente_voz != -1) { audio_stop_sound(global.audio.ambiente_voz); global.audio.ambiente_voz = -1; }
    if (global.audio.voz_voz != -1)      { audio_stop_sound(global.audio.voz_voz);      global.audio.voz_voz      = -1; }
}

/// @function audio_step()
/// @desc    Mantenimiento de cada frame: avanza los fundidos de salida en
///          curso, mueve el oyente con la cámara activa y aplica el ducking
///          de la música. Llámala UNA vez por frame, desde el Step (o Begin
///          Step) del mismo objeto que llamó a audio_init().
function audio_step()
{
    if (!variable_global_exists("audio")) { return; }

    voces_paso();

    // El oyente va con la CÁMARA, no con el jugador: si va con el jugador y
    // la cámara se adelanta, se oyen cosas que no se ven todavía.
    var _cam = camera_get_active();
    if (_cam != -1)
    {
        audio_listener_position(
            camera_get_view_x(_cam) + camera_get_view_width(_cam)  * 0.5,
            camera_get_view_y(_cam) + camera_get_view_height(_cam) * 0.5,
            0);
    }

    // Ducking: la música se agacha mientras suena una línea de diálogo.
    // mezcla_aplicar() deja la ganancia "plana"; aquí se vuelve a escribir
    // cada frame multiplicada por el duck, así que no hace falta llamar a
    // mezcla_aplicar() para que el duck surta efecto.
    var _hablando  = (global.audio.voz_voz != -1 && audio_is_playing(global.audio.voz_voz));
    var _objetivo  = _hablando ? db_to_lin(AUDIO_DUCK_OBJETIVO_DB) : 1;
    var _velocidad = _hablando ? AUDIO_DUCK_VEL_BAJAR : AUDIO_DUCK_VEL_SUBIR;
    global.audio.duck = lerp(global.audio.duck, _objetivo, _velocidad);
    global.audio.bus.musica.gain = global.audio.volumen.musica
                                  * db_to_lin(AUDIO_HEADROOM_MUSICA)
                                  * global.audio.duck;
}


// ══════════════════════════════ La mezcla ══════════════════════════════════

/// @function mezcla_aplicar()
/// @desc    Traduce los sliders de volumen (0..1) a la ganancia de cada bus.
///          Llámala al arrancar (audio_init() ya lo hace) y cada vez que el
///          jugador mueva un slider en Opciones.
function mezcla_aplicar()
{
    global.audio.bus.musica.gain   = global.audio.volumen.musica   * db_to_lin(AUDIO_HEADROOM_MUSICA);
    global.audio.bus.sfx.gain      = global.audio.volumen.sfx      * db_to_lin(AUDIO_HEADROOM_SFX);
    global.audio.bus.ui.gain       = global.audio.volumen.ui       * db_to_lin(AUDIO_HEADROOM_UI);
    global.audio.bus.voz.gain      = global.audio.volumen.voz;                                       // referencia: 0 dB
    global.audio.bus.ambiente.gain = global.audio.volumen.ambiente * db_to_lin(AUDIO_HEADROOM_AMBIENTE);
}


// ═══════════════════ Variación, y banco de tomas (round robin) ═════════════

/// @function variacion_tono([_semitonos])
/// @desc    Multiplicador de pitch aleatorio, pensado en SEMITONOS (no en
///          porcentaje): ±1,5 semitonos ≈ 0,91-1,09, el "±10 %" de siempre,
///          y no desafina nada.
/// @param   {Real} [_semitonos]  Rango de variación en semitonos (1.5 por defecto).
/// @returns {Real}               Multiplicador para `pitch`.
function variacion_tono(_semitonos = 1.5)
{
    return power(2, random_range(-_semitonos, _semitonos) / 12);
}

/// @function variacion_ganancia([_db])
/// @desc    Multiplicador de ganancia aleatorio, solo hacia ABAJO: nunca
///          subes del nivel que fijaste en la mezcla.
/// @param   {Real} [_db]  Cuántos dB puede bajar como máximo (2 por defecto).
/// @returns {Real}        Multiplicador para `gain`.
function variacion_ganancia(_db = 2)
{
    return db_to_lin(random_range(-_db, 0));
}

/// @function banco_crear(_tomas)
/// @desc    Agrupa varias tomas de un mismo sonido (pasos, impactos…) para
///          servirlas sin repetir la anterior. Con azar puro, tres tomas
///          repiten seguida la misma el 33 % de las veces; con esto, nunca.
/// @param   {Array<Asset.GMSound>} _tomas  Las variantes del sonido.
/// @returns {Struct}                       El banco: pásalo a `banco_siguiente()`.
function banco_crear(_tomas)
{
    // `ultima` arranca en una toma al azar: si arrancase en -1, la toma 0
    // nunca podría sonar la primera vez, porque el salto de abajo la
    // descartaría siempre.
    return { tomas: _tomas, ultima: irandom(array_length(_tomas) - 1) };
}

/// @function banco_siguiente(_banco)
/// @desc    Devuelve la siguiente toma del banco, sin repetir la anterior.
/// @param   {Struct} _banco  Un banco creado con `banco_crear()`.
/// @returns {Asset.GMSound}
function banco_siguiente(_banco)
{
    var _n = array_length(_banco.tomas);
    if (_n <= 1) { return _banco.tomas[0]; }

    var _i = irandom(_n - 2);              // elegimos entre n-1 candidatas...
    if (_i >= _banco.ultima) { _i += 1; }  // ...saltándonos la que sonó la última vez
    _banco.ultima = _i;
    return _banco.tomas[_i];
}


// ═════════════════════ Cupo de voces, con fundido de salida ════════════════

/// @function apagar_con_fundido(_voz, [_ms])
/// @desc    Para un sonido con un fundido corto en vez de en seco: cortar a
///          mitad de onda produce un CLICK audible. Con 30-60 ms desaparece
///          sin que se note. Requiere que `audio_step()` se llame cada frame
///          (es quien completa el corte al terminar el fundido).
/// @param   {Id.Sound} _voz  El sonido en marcha a apagar.
/// @param   {Real}     [_ms] Duración del fundido en milisegundos (40 por defecto).
function apagar_con_fundido(_voz, _ms = 40)
{
    if (_voz == -1 || !audio_is_playing(_voz)) { return; }
    audio_sound_gain(_voz, 0, _ms);
    array_push(global.audio.apagando, { voz: _voz, restante: _ms / 1000 });
}

/// @function voces_paso()
/// @desc    Avanza los fundidos de salida en curso y para de verdad los que
///          ya han llegado a silencio. Uso interno: `audio_step()` ya la
///          llama; no hace falta llamarla a mano.
function voces_paso()
{
    var _dt = delta_time / 1000000;   // delta_time viene en MICROsegundos
    for (var _i = array_length(global.audio.apagando) - 1; _i >= 0; _i -= 1)
    {
        var _e = global.audio.apagando[_i];
        _e.restante -= _dt;
        if (_e.restante <= 0)
        {
            audio_stop_sound(_e.voz);
            array_delete(global.audio.apagando, _i, 1);
        }
    }
}

/// @function sonar_limitado(_sonido, _max_voces, [_gain], [_prioridad])
/// @desc    Reproduce un sonido no posicional respetando un cupo MÁXIMO de
///          voces simultáneas del MISMO sonido: al llenarse, roba la más
///          antigua con fundido. El límite nativo (128 voces) protege el
///          motor, no la mezcla: veinte impactos idénticos en un frame caben
///          de sobra y suenan como un cañonazo de ruido con el volumen
///          sumado. Un cupo de 3-5 arregla el 90 % de las mezclas sucias.
/// @param   {Asset.GMSound} _sonido      El sonido a reproducir.
/// @param   {Real}          _max_voces   Cuántas copias como mucho a la vez.
/// @param   {Real}          [_gain]      Multiplicador de ganancia (1 por defecto).
/// @param   {Real}          [_prioridad] Prioridad del canal (10 por defecto).
/// @returns {Id.Sound}
function sonar_limitado(_sonido, _max_voces, _gain = 1, _prioridad = 10)
{
    if (!audio_system_is_available()) { return -1; }

    var _clave = audio_get_name(_sonido);
    if (!struct_exists(global.audio.voces, _clave)) { struct_set(global.audio.voces, _clave, []); }
    var _lista = struct_get(global.audio.voces, _clave);

    for (var _i = array_length(_lista) - 1; _i >= 0; _i -= 1)   // podar las que ya acabaron
    {
        if (!audio_is_playing(_lista[_i])) { array_delete(_lista, _i, 1); }
    }
    while (array_length(_lista) >= _max_voces)
    {
        apagar_con_fundido(_lista[0], 30);
        array_delete(_lista, 0, 1);
    }

    var _voz = audio_play_sound_ext({
        sound   : _sonido,
        priority: _prioridad,
        emitter : global.audio.em.sfx,
        gain    : _gain * variacion_ganancia(1.5),
        pitch   : variacion_tono(1.5)
    });
    if (_voz != -1) { array_push(_lista, _voz); }
    return _voz;
}


// ═════════════════════ Anillo de emisores posicionales ═════════════════════

/// @function sonar_en(_sonido, _px, _py, [_gain], [_prioridad])
/// @desc    Reproduce un sonido EN una posición del mundo, pasando por el
///          bus "sfx". `audio_play_sound_at()` no sirve para esto: el audio
///          3D directo va al bus principal y se salta toda la mezcla. La
///          solución es un anillo de emisores reutilizables.
///          ⚠️ Reutilizar un emisor MUEVE los sonidos que sigan sonando en
///          él: con SFX cortos (< 500 ms) y 16-32 emisores no se nota; para
///          un bucle largo (fuego, cascada) usa un emisor dedicado aparte.
/// @param   {Asset.GMSound} _sonido      El sonido a reproducir.
/// @param   {Real}          _px          Posición X en el mundo.
/// @param   {Real}          _py          Posición Y en el mundo.
/// @param   {Real}          [_gain]      Multiplicador de ganancia (1 por defecto).
/// @param   {Real}          [_prioridad] Prioridad del canal (10 por defecto).
/// @returns {Id.Sound}
function sonar_en(_sonido, _px, _py, _gain = 1, _prioridad = 10)
{
    if (!audio_system_is_available()) { return -1; }

    var _n = array_length(global.audio.anillo);
    if (_n == 0) { return -1; }

    var _em = global.audio.anillo[global.audio.anillo_i];
    global.audio.anillo_i = (global.audio.anillo_i + 1) mod _n;
    audio_emitter_position(_em, _px, _py, 0);

    return audio_play_sound_ext({
        sound   : _sonido,
        priority: _prioridad,
        emitter : _em,
        gain    : _gain * variacion_ganancia(1.5),
        pitch   : variacion_tono(1.5)
    });
}

/// @function sfx(_sonido, [_gain], [_pitch])
/// @desc    Reproduce un efecto NO posicional (menús, recolectables, HUD de
///          gameplay) por el bus "sfx", con una pequeña variación de tono
///          para evitar el "efecto ametralladora" al repetirlo mucho.
/// @param   {Asset.GMSound} _sonido  El sonido a reproducir.
/// @param   {Real}          [_gain]  Multiplicador de ganancia (1 por defecto).
/// @param   {Real}          [_pitch] Multiplicador de tono (1 por defecto).
/// @returns {Id.Sound}
function sfx(_sonido, _gain = 1, _pitch = 1)
{
    if (!audio_system_is_available()) { return -1; }

    return audio_play_sound_ext({
        sound   : _sonido,
        priority: 10,
        emitter : global.audio.em.sfx,
        gain    : _gain,
        pitch   : _pitch * variacion_tono(1.5)
    });
}

/// @function sfx_ui(_sonido, [_gain], [_pitch])
/// @desc    Reproduce un sonido de INTERFAZ (clic, confirmar, error). Nunca
///          posicional, y con prioridad alta para que no lo descarte el
///          límite de canales en un frame cargado.
/// @param   {Asset.GMSound} _sonido  El sonido a reproducir.
/// @param   {Real}          [_gain]  Multiplicador de ganancia (1 por defecto).
/// @param   {Real}          [_pitch] Multiplicador de tono (1 por defecto, sin variación:
///                                   la interfaz debe sonar IGUAL siempre).
/// @returns {Id.Sound}
function sfx_ui(_sonido, _gain = 1, _pitch = 1)
{
    if (!audio_system_is_available()) { return -1; }

    return audio_play_sound_ext({
        sound   : _sonido,
        priority: 80,
        emitter : global.audio.em.ui,
        gain    : _gain,
        pitch   : _pitch
    });
}


// ═══════════════════════ Voz, música y ambiente (crossfade) ════════════════

/// @function voz_decir(_sonido)
/// @desc    Reproduce una línea de diálogo, cortando la anterior con
///          fundido: dos voces solapadas no se entienden. Activa el ducking
///          de la música mientras suena (lo aplica `audio_step()`).
/// @param   {Asset.GMSound} _sonido  La línea a reproducir.
/// @returns {Id.Sound}
function voz_decir(_sonido)
{
    if (!audio_system_is_available()) { return -1; }

    if (global.audio.voz_voz != -1) { apagar_con_fundido(global.audio.voz_voz, 60); }
    global.audio.voz_voz = audio_play_sound_ext({
        sound   : _sonido,
        priority: 100,
        emitter : global.audio.em.voz
    });
    return global.audio.voz_voz;
}

/// @function __audio_categoria_poner(_categoria, _campo_snd, _campo_voz, _sonido, _ms)
/// @desc    Crossfade genérico para un bucle largo de categoría (música o
///          ambiente): los dos bucles suenan a la vez durante la transición,
///          uno bajando y otro subiendo. Uso interno: usa `musica_poner()` o
///          `ambiente_poner()`, no llames a esta directamente.
/// @param   {String} _categoria  Nombre de la categoría ("musica"/"ambiente").
/// @param   {String} _campo_snd  Campo de `global.audio` con el sonido actual.
/// @param   {String} _campo_voz  Campo de `global.audio` con la voz actual.
/// @param   {Asset.GMSound} _sonido  El nuevo bucle.
/// @param   {Real}   _ms         Duración del cruce en milisegundos.
function __audio_categoria_poner(_categoria, _campo_snd, _campo_voz, _sonido, _ms)
{
    var _actual = struct_get(global.audio, _campo_snd);
    if (!is_undefined(_actual) && _actual == _sonido) { return; }   // ya suena

    apagar_con_fundido(struct_get(global.audio, _campo_voz), _ms);
    struct_set(global.audio, _campo_snd, _sonido);

    var _voz_nueva = audio_play_sound_ext({
        sound   : _sonido,
        loop    : true,
        gain    : 0,                                  // entra desde el silencio
        priority: 90,                                  // alta: que no lo descarte el límite de canales
        emitter : struct_get(global.audio.em, _categoria)
    });
    struct_set(global.audio, _campo_voz, _voz_nueva);
    audio_sound_gain(_voz_nueva, 1, _ms);              // el bus ya aplica el volumen de la categoría
}

/// @function musica_poner(_sonido, [_ms])
/// @desc    Cambia la música con fundido cruzado. Si ya es la que suena, no
///          hace nada.
/// @param   {Asset.GMSound} _sonido  La nueva música.
/// @param   {Real}          [_ms]    Duración del cruce (1500 ms por defecto).
function musica_poner(_sonido, _ms = 1500)
{
    __audio_categoria_poner("musica", "musica_snd", "musica_voz", _sonido, _ms);
}

/// @function ambiente_poner(_sonido, [_ms])
/// @desc    Cambia el "bed" de ambiente de la zona con fundido cruzado.
///          2000-4000 ms hacen que el cambio de zona no se note como un
///          corte.
/// @param   {Asset.GMSound} _sonido  El nuevo bed de ambiente.
/// @param   {Real}          [_ms]    Duración del cruce (2500 ms por defecto).
function ambiente_poner(_sonido, _ms = 2500)
{
    __audio_categoria_poner("ambiente", "ambiente_snd", "ambiente_voz", _sonido, _ms);
}
