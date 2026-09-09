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
// ARQUITECTURA (globals planos — ver nota de unificación más abajo)
//   global.bus         = { musica, sfx, ui, voz, ambiente }   structs AudioBus
//   global.em          = { musica, sfx, ui, voz, ambiente }   un emisor por bus,
//                                                              sin atenuación (no
//                                                              son posicionales)
//   global.emisores    = [ ... ]     emisores POSICIONALES (el anillo), por
//                                    defecto todos al bus "sfx"
//   global.emisor_i    = índice del próximo emisor del anillo
//   global.voces       = { "nombre_del_sonido": [ids...] }    cupo por sonido
//   global.apagando    = [ { voz, restante } ]                fundidos en curso
//   global.volumen_musica / _sfx / _ui / _voz / _ambiente     sliders 0..1
//   global.musica_snd, global.musica_voz
//   global.ambiente_snd, global.ambiente_voz
//   global.voz_voz, global.duck
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
//   sonar_limitado(snd_impacto, 4, db_to_lin(-8));      // como mucho 4 a la vez,
//                                                        // por el bus principal
//                                                        // (barato; ver nota bajo
//                                                        // sonar_limitado() para
//                                                        // el caso contrario)
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
//   global.volumen_musica = 0.4;
//   mezcla_aplicar();
//
// Funciones nativas usadas (verificadas con gm-cli manual read / buscar.py):
//   audio_bus_create, audio_emitter_create, audio_emitter_bus,
//   audio_emitter_falloff, audio_emitter_position, audio_emitter_free,
//   audio_play_sound_ext, audio_sound_gain, audio_stop_sound,
//   audio_is_playing, audio_system_is_available, audio_falloff_set_model,
//   audio_falloff_inverse_distance_clamped, audio_listener_position,
//   audio_get_name, db_to_lin, camera_get_active, camera_get_view_x/y,
//   camera_get_view_width/height, power, irandom, random_range, lerp,
//   struct_get, struct_set, struct_get_names, struct_exists,
//   variable_global_get, variable_global_set, variable_global_exists,
//   array_push, array_delete, array_length, is_undefined, delta_time
//
// Dependencias: ninguna.
//
// LO QUE ESTE SCRIPT NO CUBRE (y dónde está)
//   - Oclusión por paredes y zonas de reverberación: no forma parte del cupo
//     mínimo reutilizable, tienen coste propio por proyecto (filtros, rayos).
//     Ver "13 - Diseño y producción de videojuegos/09" §5.3.
//   - Compresor-techo del bus principal, EQ para hacer sitio a la voz, y
//     estados de mezcla completos (bajo el agua, pausa…): ver 13 · 09 §4.3.
//   - Voz, subtítulos y localización de audio: fuera de alcance de un script
//     genérico. Ver la misma carpeta, documento "14" y "24".
//
// ✅ UNIFICADO con "13 - Diseño y producción de videojuegos/09" (Diseño de
//   sonido y mezcla): hasta esta ronda existían dos sistemas de audio
//   completos e independientes con ~10 nombres de función coincidentes pero
//   globals distintos (`global.audio.bus.*` aquí frente a `global.bus.*` en
//   13 · 09). Se han reconciliado en UNO: este script es ahora la única
//   implementación real, con los nombres de global que ya usaban 13 · 09 y
//   las recetas construidas encima de él (04 · 26, 04 · 42, 04 · 45, 13 · 10,
//   13 · 24…). 13 · 09 explica la TEORÍA (por qué esas cifras de headroom,
//   por qué esa curva de ducking, el mapa de bandas de EQ, LUFS…) y remite
//   aquí para el CÓDIGO; no dupliques sus bloques de nuevo en un proyecto que
//   ya use este script. La única diferencia de comportamiento real que
//   sobrevivió a la unificación está documentada en `sonar_limitado()` más
//   abajo — no es un descuido, es una decisión de coste explícita.
// ============================================================================


// ─────────────────────────── Configuración ──────────────────────────────
// Headroom en dB de cada categoría: deja hueco para que el ducking y los
// picos de SFX no saturen el bus principal. Ajusta estas cifras a tu mezcla,
// no el código que las usa. (Mismos valores que documenta 13 · 09 §4.1/§4.2.)
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

/// @function voces_iniciar()
/// @desc    Prepara SOLO el cupo de voces (`global.voces`, `global.apagando`),
///          sin tocar buses ni emisores. `audio_init()` ya la llama; existe
///          suelta para poder probar `sonar_limitado()`/`voces_paso()` en una
///          prueba de integración mínima sin montar todo el sistema de audio
///          (así lo hace la prueba de "13 · 09" §10 / "13 · 10" §2).
function voces_iniciar()
{
    global.voces    = {};   // "nombre_del_sonido" -> array de ids en curso
    global.apagando = [];   // { voz, restante } con fundido de salida activo
}

/// @function emisores_iniciar(_cantidad, _bus)
/// @desc    Crea el anillo de emisores POSICIONALES y lo engancha a `_bus`.
///          `audio_init()` ya la llama con el bus "sfx"; existe suelta por si
///          necesitas un segundo anillo colgado de otro bus.
/// @param   {Real}          _cantidad  Tamaño del anillo.
/// @param   {Id.AudioBus}   _bus       Bus al que se engancha cada emisor.
function emisores_iniciar(_cantidad, _bus)
{
    global.emisores = [];
    global.emisor_i = 0;
    repeat (_cantidad)
    {
        var _em = audio_emitter_create();
        audio_emitter_bus(_em, _bus);
        audio_emitter_falloff(_em, AUDIO_ANILLO_FALLOFF_REF, AUDIO_ANILLO_FALLOFF_MAX, 1);
        array_push(global.emisores, _em);
    }
}

/// @function emisores_liberar()
/// @desc    Libera todos los emisores del anillo (son recursos dinámicos).
///          `audio_destruir()` ya la llama.
function emisores_liberar()
{
    if (!variable_global_exists("emisores")) { return; }
    for (var _i = 0; _i < array_length(global.emisores); _i += 1)
    {
        audio_emitter_free(global.emisores[_i]);
    }
    global.emisores = [];
}

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
    // No reinicializar dos veces: perdería los volúmenes que el jugador acaba de
    // elegir en Opciones. Se comprueba que además SEA un struct, porque
    // `audio_destruir()` lo deja en `undefined` — sin esa segunda condición,
    // destruir y volver a inicializar dejaba el audio muerto en silencio.
    if (variable_global_exists("bus") && is_struct(global.bus)) { return; }

    // El modelo por defecto es "audio_falloff_none": con él la ganancia vale
    // siempre 1, aunque el emisor esté a dos pantallas. Es EL bug de audio
    // más frecuente en GameMaker. Se fija una sola vez, para todo el juego.
    audio_falloff_set_model(audio_falloff_inverse_distance_clamped);

    voces_iniciar();

    global.bus = {};
    global.em  = {};
    global.volumen_musica   = 0.7;
    global.volumen_sfx      = 1.0;
    global.volumen_ui       = 0.8;
    global.volumen_voz      = 1.0;
    global.volumen_ambiente = 0.6;
    global.musica_snd   = undefined; global.musica_voz   = -1;
    global.ambiente_snd = undefined; global.ambiente_voz = -1;
    global.voz_voz = -1;
    global.duck    = 1;        // 1 = sin agachar · baja hacia AUDIO_DUCK_OBJETIVO_DB al hablar

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
        struct_set(global.bus, _cat, _bus);
        struct_set(global.em,  _cat, _em);
    }

    // El anillo de emisores POSICIONALES comparte el bus "sfx" con la
    // categoría de arriba: unos suenan "en el mundo" (sonar_en) y otros "en
    // ninguna parte" (sfx, sonar_limitado con emisor explícito), pero pasan
    // por el mismo control de volumen y por el mismo ducking.
    emisores_iniciar(_emisores_anillo, global.bus.sfx);

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
    if (!variable_global_exists("bus")) { return; }

    var _nombres = struct_get_names(global.em);
    for (var _i = 0; _i < array_length(_nombres); _i += 1)
    {
        audio_emitter_free(struct_get(global.em, _nombres[_i]));
    }

    emisores_liberar();

    if (global.musica_voz != -1)   { audio_stop_sound(global.musica_voz);   global.musica_voz   = -1; }
    if (global.ambiente_voz != -1) { audio_stop_sound(global.ambiente_voz); global.ambiente_voz = -1; }
    if (global.voz_voz != -1)      { audio_stop_sound(global.voz_voz);      global.voz_voz      = -1; }

    // Y BORRAR LA MARCA. Sin esto, `audio_init()` posterior veía que
    // `global.bus` existía, se creía ya inicializado y volvía sin hacer nada —
    // dejando `global.em.sfx` apuntando a emisores YA LIBERADOS. El juego seguía
    // llamando a `sfx()` y no sonaba nada, sin un solo error.
    //
    // Pasa de verdad en cuanto el controlador de audio no es persistente: se
    // destruye al cambiar de sala (Clean Up → `audio_destruir`), se recrea en la
    // siguiente (Create → `audio_init`), y a partir de ahí el juego es mudo.
    // Lo cazó el banco de `_indice/validar-ejecucion.sh`; compilaba perfectamente.
    global.bus = undefined;
    global.em  = undefined;
}

/// @function audio_step()
/// @desc    Mantenimiento de cada frame: avanza los fundidos de salida en
///          curso, mueve el oyente con la cámara activa y aplica el ducking
///          de la música. Llámala UNA vez por frame, desde el Step (o Begin
///          Step) del mismo objeto que llamó a audio_init().
function audio_step()
{
    if (!variable_global_exists("bus")) { return; }

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
    var _hablando  = (global.voz_voz != -1 && audio_is_playing(global.voz_voz));
    var _objetivo  = _hablando ? db_to_lin(AUDIO_DUCK_OBJETIVO_DB) : 1;
    var _velocidad = _hablando ? AUDIO_DUCK_VEL_BAJAR : AUDIO_DUCK_VEL_SUBIR;
    global.duck = lerp(global.duck, _objetivo, _velocidad);
    global.bus.musica.gain = global.volumen_musica
                            * db_to_lin(AUDIO_HEADROOM_MUSICA)
                            * global.duck;
}


// ══════════════════════════════ La mezcla ══════════════════════════════════

/// @function mezcla_aplicar()
/// @desc    Traduce los sliders de volumen (0..1) a la ganancia de cada bus.
///          Llámala al arrancar (audio_init() ya lo hace) y cada vez que el
///          jugador mueva un slider en Opciones.
function mezcla_aplicar()
{
    global.bus.musica.gain   = global.volumen_musica   * db_to_lin(AUDIO_HEADROOM_MUSICA);
    global.bus.sfx.gain      = global.volumen_sfx      * db_to_lin(AUDIO_HEADROOM_SFX);
    global.bus.ui.gain       = global.volumen_ui       * db_to_lin(AUDIO_HEADROOM_UI);
    global.bus.voz.gain      = global.volumen_voz;                                       // referencia: 0 dB
    global.bus.ambiente.gain = global.volumen_ambiente * db_to_lin(AUDIO_HEADROOM_AMBIENTE);
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
    array_push(global.apagando, { voz: _voz, restante: _ms / 1000 });
}

/// @function voces_paso()
/// @desc    Avanza los fundidos de salida en curso y para de verdad los que
///          ya han llegado a silencio. Uso interno: `audio_step()` ya la
///          llama; no hace falta llamarla a mano.
function voces_paso()
{
    var _dt = delta_time / 1000000;   // delta_time viene en MICROsegundos
    for (var _i = array_length(global.apagando) - 1; _i >= 0; _i -= 1)
    {
        var _e = global.apagando[_i];
        _e.restante -= _dt;
        if (_e.restante <= 0)
        {
            audio_stop_sound(_e.voz);
            array_delete(global.apagando, _i, 1);
        }
    }
}

/// @function sonar_limitado(_sonido, _max_voces, [_gain], [_prioridad], [_emisor])
/// @desc    Reproduce un sonido respetando un cupo MÁXIMO de voces
///          simultáneas del MISMO sonido: al llenarse, roba la más antigua
///          con fundido. El límite nativo (128 voces) protege el motor, no
///          la mezcla: veinte impactos idénticos en un frame caben de sobra y
///          suenan como un cañonazo de ruido con el volumen sumado. Un cupo
///          de 3-5 arregla el 90 % de las mezclas sucias.
///
///          ⚠️ **Por defecto NO pasa `emitter`**: el sonido va al bus
///          principal, sin coste de cálculo de emisor y sin que le afecten
///          el volumen de "Efectos" ni ningún efecto colgado de un bus
///          propio (reverberación de zona, compresor…). Es la decisión
///          correcta para un sonido que se dispara muchas veces por segundo
///          (pasos: ver "04 · 42" §1.2/§3.1, que documenta el porqué). Si
///          este sonido SÍ necesita pasar por un bus — normalmente
///          `global.em.sfx`, para que el slider de Efectos y la
///          reverberación de zona le afecten — pásalo explícitamente en
///          `_emisor`.
/// @param   {Asset.GMSound}    _sonido      El sonido a reproducir.
/// @param   {Real}             _max_voces   Cuántas copias como mucho a la vez.
/// @param   {Real}             [_gain]      Multiplicador de ganancia (1 por defecto).
/// @param   {Real}             [_prioridad] Prioridad del canal (10 por defecto).
/// @param   {Id.SoundEmitter}  [_emisor]    Emisor por el que enrutarlo (ninguno por defecto).
/// @returns {Id.Sound}
function sonar_limitado(_sonido, _max_voces, _gain = 1, _prioridad = 10, _emisor = -1)
{
    if (!audio_system_is_available()) { return -1; }

    var _clave = audio_get_name(_sonido);
    if (!struct_exists(global.voces, _clave)) { struct_set(global.voces, _clave, []); }
    var _lista = struct_get(global.voces, _clave);

    for (var _i = array_length(_lista) - 1; _i >= 0; _i -= 1)   // podar las que ya acabaron
    {
        if (!audio_is_playing(_lista[_i])) { array_delete(_lista, _i, 1); }
    }
    while (array_length(_lista) >= _max_voces)
    {
        apagar_con_fundido(_lista[0], 30);
        array_delete(_lista, 0, 1);
    }

    var _params = {
        sound   : _sonido,
        priority: _prioridad,
        gain    : _gain * variacion_ganancia(1.5),
        pitch   : variacion_tono(1.5)
    };
    if (_emisor != -1) { _params.emitter = _emisor; }

    var _voz = audio_play_sound_ext(_params);
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

    var _n = array_length(global.emisores);
    if (_n == 0) { return -1; }

    var _em = global.emisores[global.emisor_i];
    global.emisor_i = (global.emisor_i + 1) mod _n;
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
        emitter : global.em.sfx,
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
        emitter : global.em.ui,
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

    if (global.voz_voz != -1) { apagar_con_fundido(global.voz_voz, 60); }
    global.voz_voz = audio_play_sound_ext({
        sound   : _sonido,
        priority: 100,
        emitter : global.em.voz
    });
    return global.voz_voz;
}

/// @function __audio_categoria_poner(_categoria, _campo_snd, _campo_voz, _sonido, _ms)
/// @desc    Crossfade genérico para un bucle largo de categoría (música o
///          ambiente): los dos bucles suenan a la vez durante la transición,
///          uno bajando y otro subiendo. Uso interno: usa `musica_poner()` o
///          `ambiente_poner()`, no llames a esta directamente.
/// @param   {String} _categoria  Nombre de la categoría ("musica"/"ambiente").
/// @param   {String} _campo_snd  Nombre del global con el sonido actual (p. ej. "musica_snd").
/// @param   {String} _campo_voz  Nombre del global con la voz actual (p. ej. "musica_voz").
/// @param   {Asset.GMSound} _sonido  El nuevo bucle.
/// @param   {Real}   _ms         Duración del cruce en milisegundos.
function __audio_categoria_poner(_categoria, _campo_snd, _campo_voz, _sonido, _ms)
{
    var _actual = variable_global_get(_campo_snd);
    if (!is_undefined(_actual) && _actual == _sonido) { return; }   // ya suena

    apagar_con_fundido(variable_global_get(_campo_voz), _ms);
    variable_global_set(_campo_snd, _sonido);

    var _voz_nueva = audio_play_sound_ext({
        sound   : _sonido,
        loop    : true,
        gain    : 0,                                  // entra desde el silencio
        priority: 90,                                  // alta: que no lo descarte el límite de canales
        emitter : struct_get(global.em, _categoria)
    });
    variable_global_set(_campo_voz, _voz_nueva);
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
