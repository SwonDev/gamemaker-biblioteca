// ============================================================================
// scr_debug.gml
// Utilidades de depuración: panel de variables en vivo, log en pantalla,
// gráfica de FPS y medición de tiempos.
//
// Todo se dibuja en evento DRAW GUI, así que las coordenadas son de PANTALLA
// (no de room) y la cámara no afecta.
//
// Funciones nativas usadas (verificadas con gm-cli manual read):
//   show_debug_message, show_debug_overlay, get_timer, fps, fps_real,
//   draw_text, draw_rectangle, draw_line, draw_set_color, draw_set_alpha,
//   draw_set_halign, draw_set_valign, draw_set_font, draw_get_color,
//   draw_get_alpha, draw_get_halign, draw_get_valign, draw_get_font,
//   display_get_gui_width, display_get_gui_height, string_format,
//   keyboard_check_pressed, array_push, array_length, array_delete,
//   is_method, method
//
// Dependencias: ninguna.
//
// USO RAPIDO
//   // En el Create de un controlador de depuración:
//   debug_init();
//   debug_watch("vida",   function() { return obj_player.hp; });
//   debug_watch("estado", function() { return obj_player.fsm.get(); });
//
//   // En su Step:
//   debug_update();                       // para el toggle de teclado
//   debug_log("el jugador ha muerto");    // escribe en el log
//
//   // En su Draw GUI:
//   debug_draw();
//
//   // Para medir cuánto tarda un bloque de código:
//   debug_time_start("pathfinding");
//   var _ruta = grid.find_path(x, y, tx, ty);
//   debug_time_end("pathfinding");        // lo muestra en el panel
//
// ATALAJOS
//   F3   -> muestra/oculta el panel
//   F4   -> activa el Debug Overlay propio de GameMaker
// ============================================================================

#macro DEBUG_LINEAS_MAX 12     // líneas de log que se recuerdan
#macro DEBUG_FPS_MUESTRAS 120  // frames que guarda la gráfica de FPS


/// @function debug_init()
/// @desc    Inicializa el sistema de depuración. Llamalo una vez, en el Create
///          de un objeto persistente.
function debug_init() {
    if (variable_global_exists("__debug")) { return; }

    global.__debug = {
        visible    : true,
        overlay_nativo : false,
        relojes    : {},   // variables vigiladas: nombre -> método
        log        : [],   // ultimas líneas de texto
        fps_historia : [], // últimos valores de fps_real, para la gráfica
        tiempos    : {},   // mediciones de debug_time_start/end
        tiempos_parciales : {},
        x          : 8,
        y          : 8,
        fuente     : -1    // -1 = usar la fuente por defecto
    };

    array_resize(global.__debug.fps_historia, 0);
}


/// @function __debug()
/// @desc    Acceso interno al estado global. Se inicializa si hiciera falta.
/// @returns {Struct}
function __debug() {
    if (!variable_global_exists("__debug")) { debug_init(); }
    return global.__debug;
}


/// @function debug_set_position(_x, _y)
/// @desc    Mueve el panel de depuración.
/// @param   {Real} _x  Posición X en pantalla.
/// @param   {Real} _y  Posición Y en pantalla.
function debug_set_position(_x, _y) {
    var _d = __debug();
    _d.x = _x;
    _d.y = _y;
}


/// @function debug_set_font(_fuente)
/// @desc    Fuente del panel. Por defecto, la del juego.
/// @param   {Asset.GMFont} _fuente  Recurso de fuente, o -1 para la default.
function debug_set_font(_fuente) {
    var _d = __debug();
    _d.fuente = _fuente;
}


/// @function debug_watch(_etiqueta, _getter)
/// @desc    Anade una variable al panel. El getter es una FUNCION, no un
///          valor: se llama en cada frame, así que siempre ves el valor real.
/// @param   {String}   _etiqueta  Nombre a mostrar.
/// @param   {Function} _getter    Función que devuelve el valor.
function debug_watch(_etiqueta, _getter) {
    if (!is_method(_getter)) {
        show_debug_message("debug_watch: el getter de \"" + string(_etiqueta) + "\" no es una función.");
        return;
    }
    var _d = __debug();
    _d.relojes[$ _etiqueta] = _getter;
}


/// @function debug_unwatch(_etiqueta)
/// @desc    Quita una variable del panel.
/// @param   {String} _etiqueta  Nombre que le diste en `debug_watch()`.
function debug_unwatch(_etiqueta) {
    var _d = __debug();
    if (struct_exists(_d.relojes, _etiqueta)) {
        variable_struct_remove(_d.relojes, _etiqueta);
    }
}


/// @function debug_log(_texto)
/// @desc    Escribe una línea en el log. Se muestra en pantalla Y en la
///          consola del IDE (Output).
/// @param   {String} _texto  Texto a registrar.
function debug_log(_texto) {
    var _d = __debug();

    var _linea = "[" + string_format(fps, 3, 0) + "] " + string(_texto);
    array_push(_d.log, _linea);

    // Mantenemos el log acotado: borramos las más viejas.
    while (array_length(_d.log) > DEBUG_LINEAS_MAX) {
        array_delete(_d.log, 0, 1);
    }

    show_debug_message(string(_texto));
}


/// @function debug_clear_log()
/// @desc    Vacia el log en pantalla.
function debug_clear_log() {
    var _d = __debug();
    _d.log = [];
}


/// @function debug_time_start(_etiqueta)
/// @desc    Empieza a medir un bloque de código. Usa `get_timer()`, que tiene
///          precisión de microsegundos.
/// @param   {String} _etiqueta  Nombre de la medición.
function debug_time_start(_etiqueta) {
    var _d = __debug();
    _d.tiempos_parciales[$ _etiqueta] = get_timer();
}


/// @function debug_time_end(_etiqueta)
/// @desc    Termina la medición y guarda el resultado para mostrarlo.
/// @param   {String} _etiqueta  Nombre que le diste en `debug_time_start()`.
/// @returns {Real}              Milisegundos transcurridos, o -1 si no habia
///                              una medición abierta con ese nombre.
function debug_time_end(_etiqueta) {
    var _d = __debug();

    if (!struct_exists(_d.tiempos_parciales, _etiqueta)) { return -1; }

    // get_timer() devuelve MICROsegundos: dividimos entre 1000 para ms.
    var _ms = (get_timer() - _d.tiempos_parciales[$ _etiqueta]) / 1000;
    _d.tiempos[$ _etiqueta] = _ms;
    variable_struct_remove(_d.tiempos_parciales, _etiqueta);

    return _ms;
}


/// @function debug_time_get(_etiqueta)
/// @desc    Ultima medición registrada de un bloque.
/// @param   {String} _etiqueta
/// @returns {Real}  Milisegundos, o -1 si no hay medición.
function debug_time_get(_etiqueta) {
    var _d = __debug();
    return struct_exists(_d.tiempos, _etiqueta) ? _d.tiempos[$ _etiqueta] : -1;
}


/// @function debug_update()
/// @desc    Gestiona los atajos de teclado y alimenta la gráfica de FPS.
///          LLAMALA EN EL STEP (o en Begin Step) de tu controlador.
function debug_update() {
    var _d = __debug();

    // F3 -> panel, F4 -> overlay nativo de GameMaker.
    if (keyboard_check_pressed(vk_f3)) {
        _d.visible = !_d.visible;
    }
    if (keyboard_check_pressed(vk_f4)) {
        show_debug_overlay(!_d.overlay_nativo);
        _d.overlay_nativo = !_d.overlay_nativo;
    }

    // Alimentamos la gráfica.
    array_push(_d.fps_historia, fps_real);
    while (array_length(_d.fps_historia) > DEBUG_FPS_MUESTRAS) {
        array_delete(_d.fps_historia, 0, 1);
    }
}


/// @function debug_toggle()
/// @desc    Muestra u oculta el panel.
function debug_toggle() {
    var _d = __debug();
    _d.visible = !_d.visible;
}


/// @function __debug_save_draw_state()
/// @desc    Guarda el estado de dibujado para poder restaurarlo. Uso interno.
/// @returns {Struct}
function __debug_save_draw_state() {
    return {
        color  : draw_get_color(),
        alpha  : draw_get_alpha(),
        halign : draw_get_halign(),
        valign : draw_get_valign(),
        font   : draw_get_font()
    };
}


/// @function __debug_restore_draw_state(_estado)
/// @desc    Restaura el estado de dibujado. Uso interno.
/// @param   {Struct} _estado  Struct devuelto por la función anterior.
function __debug_restore_draw_state(_estado) {
    draw_set_color(_estado.color);
    draw_set_alpha(_estado.alpha);
    draw_set_halign(_estado.halign);
    draw_set_valign(_estado.valign);
    draw_set_font(_estado.font);
}


/// @function debug_draw()
/// @desc    Dibuja el panel completo: FPS, variables vigiladas, mediciones y
///          log. LLAMALA EN UN EVENTO DRAW GUI.
function debug_draw() {
    var _d = __debug();
    if (!_d.visible) { return; }

    var _estado = __debug_save_draw_state();

    if (_d.fuente != -1) { draw_set_font(_d.fuente); }
    draw_set_alpha(1);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);

    var _x = _d.x;
    var _y = _d.y;
    var _alto_linea = 16;

    // --- Fondo --------------------------------------------------------------
    draw_set_alpha(0.7);
    draw_set_color(c_black);
    draw_rectangle(_x - 4, _y - 4, _x + 260, _y + 8 + _alto_linea * 3, false);
    draw_set_alpha(1);

    // --- Cabecera: FPS ------------------------------------------------------
    // fps es la media suavizada; fps_real es la medición del frame actual.
    // Si difieren mucho, hay picos de rendimiento que la media esconde.
    var _color_fps = c_lime;
    if (fps_real < 30)      { _color_fps = c_red; }
    else if (fps_real < 55) { _color_fps = c_yellow; }

    draw_set_color(_color_fps);
    draw_text(_x, _y, "FPS " + string_format(fps, 3, 0) +
                      "  (real " + string_format(fps_real, 4, 0) + ")");
    _y += _alto_linea;

    draw_set_color(c_gray);
    draw_text(_x, _y, "instancias: " + string(instance_count) +
                      "  F3 panel / F4 overlay");
    _y += _alto_linea;

    // --- Variables vigiladas ------------------------------------------------
    var _nombres = struct_get_names(_d.relojes);
    if (array_length(_nombres) > 0) {
        draw_set_color(c_white);
        draw_text(_x, _y, "-- variables --");
        _y += _alto_linea;

        var _i;
        for (_i = 0; _i < array_length(_nombres); _i++) {
            var _nombre = _nombres[_i];
            var _getter = _d.relojes[$ _nombre];

            var _valor = "(error)";
            // Envolvemos en try: si la instancia vigilada murio, el getter
            // revienta y se llevaria el juego por delante.
            try {
                _valor = _getter();
            } catch (_e) {
                _valor = "n/d";
            }

            draw_set_color(c_aqua);
            draw_text(_x, _y, "  " + _nombre + ": ");
            draw_set_color(c_white);
            draw_text(_x + 110, _y, string(_valor));
            _y += _alto_linea;
        }
    }

    // --- Mediciones de tiempo -----------------------------------------------
    var _nombres_t = struct_get_names(_d.tiempos);
    if (array_length(_nombres_t) > 0) {
        draw_set_color(c_white);
        draw_text(_x, _y, "-- tiempos (ms) --");
        _y += _alto_linea;

        var _j;
        for (_j = 0; _j < array_length(_nombres_t); _j++) {
            var _nom = _nombres_t[_j];
            var _ms  = _d.tiempos[$ _nom];

            // Mas de 4 ms en un frame de 16.6 ms es mucho: lo pintamos rojo.
            draw_set_color((_ms > 4) ? c_red : c_lime);
            draw_text(_x, _y, "  " + _nom + ": " + string_format(_ms, 0, 3));
            _y += _alto_linea;
        }
    }

    // --- Log ----------------------------------------------------------------
    if (array_length(_d.log) > 0) {
        draw_set_color(c_white);
        draw_text(_x, _y, "-- log --");
        _y += _alto_linea;

        var _k;
        for (_k = 0; _k < array_length(_d.log); _k++) {
            // Las más recientes más apagadas: el ojo va a lo último.
            var _a = 0.35 + 0.65 * (_k / max(1, array_length(_d.log) - 1));
            draw_set_alpha(_a);
            draw_set_color(c_yellow);
            draw_text(_x, _y, "  " + _d.log[_k]);
            _y += _alto_linea;
        }
        draw_set_alpha(1);
    }

    __debug_restore_draw_state(_estado);

    // --- Grafica de FPS -----------------------------------------------------
    debug_draw_fps_graph(8, display_get_gui_height() - 60, 220, 48);
}


/// @function debug_draw_fps_graph(_x, _y, _ancho, _alto)
/// @desc    Dibuja una gráfica de barras con los últimos FPS. Es la forma más
///          rapida de VER un tiron: la media no lo muestra, la gráfica si.
///          LLAMALA EN DRAW GUI.
/// @param   {Real} _x       Esquina superior izquierda X.
/// @param   {Real} _y       Esquina superior izquierda Y.
/// @param   {Real} _ancho   Ancho de la gráfica.
/// @param   {Real} _alto    Alto de la gráfica.
function debug_draw_fps_graph(_x, _y, _ancho, _alto) {
    var _d = __debug();

    var _estado = __debug_save_draw_state();
    draw_set_alpha(1);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);

    // Marco.
    draw_set_alpha(0.5);
    draw_set_color(c_black);
    draw_rectangle(_x, _y, _x + _ancho, _y + _alto, false);
    draw_set_alpha(1);

    // Linea de referencia en 60 fps.
    var _y60 = _y + _alto - (_alto * (60 / 120));
    draw_set_color(c_dkgray);
    draw_line(_x, _y60, _x + _ancho, _y60);

    // Linea de referencia en 30 fps.
    var _y30 = _y + _alto - (_alto * (30 / 120));
    draw_set_color(c_maroon);
    draw_line(_x, _y30, _x + _ancho, _y30);

    // Barras. El techo de la gráfica son 120 fps: por encima se saturaria.
    var _n = array_length(_d.fps_historia);
    var _ancho_barra = _ancho / DEBUG_FPS_MUESTRAS;

    var _i;
    for (_i = 0; _i < _n; _i++) {
        var _valor = _d.fps_historia[_i];
        var _h = clamp((_valor / 120) * _alto, 1, _alto);

        if (_valor < 30)      { draw_set_color(c_red); }
        else if (_valor < 55) { draw_set_color(c_yellow); }
        else                  { draw_set_color(c_lime); }

        draw_rectangle(
            _x + _i * _ancho_barra, _y + _alto - _h,
            _x + _i * _ancho_barra + _ancho_barra - 1, _y + _alto,
            false
        );
    }

    draw_set_color(c_white);
    draw_text(_x + 4, _y + 2, "fps (techo 120)");

    __debug_restore_draw_state(_estado);
}


/// @function debug_assert(_condicion, _mensaje)
/// @desc    Asercion: si la condicion es falsa, escribe el mensaje en el log
///          y en la consola. No detiene el juego (usa `show_error()` si
///          quieres que pare).
/// @param   {Bool}   _condicion
/// @param   {String} _mensaje
/// @returns {Bool}   La condicion, para poder encadenarla.
function debug_assert(_condicion, _mensaje) {
    if (!_condicion) {
        debug_log("!! ASSERT: " + string(_mensaje));
    }
    return _condicion;
}


// ============================================================================
// LA FUENTE MUDA, DETECTADA SIN MIRAR UN PÍXEL
//
// La Trampa 12 de `12 · 09 §0` dice que la fuente por defecto de GameMaker se come
// los acentos españoles en silencio, y que la única forma de detectarlo es capturar
// la pantalla y mirar el PNG. Es verdad a medias: hay una forma más barata, y sale
// de una medida hecha dentro del juego.
//
//   MEDIDO con `bash _indice/validar-ejecucion.sh`, fuente por defecto (`draw_set_font(-1)`):
//       string_width("a") = 9      ← la letra existe
//       string_width("á") = 0      ← la fuente no la tiene
//       string_width("ñ") = 0
//       string_width("¿") = 0
//
// Un carácter que la fuente no tiene mide CERO. Así que la fuente muda se puede
// detectar con una condición, en el arranque, sin capturas y sin ojos.
//
// ⚠️ Lo que esto demuestra y lo que no. Ancho 0 prueba que el glifo NO está: es
//    concluyente. Ancho > 0 prueba que hay algo dibujado en ese hueco, no que sea
//    el glifo correcto — una hoja de glifos con el mapa desordenado dibuja letras
//    cambiadas y mide perfectamente. Para eso sigue haciendo falta mirar
//    (`13 · 10 §8.6`). Es una red barata que caza el fallo más común, no un sustituto.
// ============================================================================

/// @function debug_fuente_sin_glifos(_fuente, _muestra)
/// @desc     Devuelve los caracteres de `_muestra` que la fuente NO tiene.
///           Array vacío = todos los caracteres miden algo.
/// @param    {Asset.GMFont|Real} _fuente   La fuente a examinar (-1 = la del motor).
/// @param    {String}            _muestra  Los caracteres que tu juego va a dibujar.
/// @returns  {Array<String>}
function debug_fuente_sin_glifos(_fuente = -1, _muestra = "áéíóúüñÁÉÍÓÚÜÑ¿¡") {
    var _antes = draw_get_font();
    draw_set_font(_fuente);

    var _faltan = [];
    for (var _i = 1; _i <= string_length(_muestra); _i++) {
        var _c = string_char_at(_muestra, _i);
        if (string_width(_c) <= 0) { array_push(_faltan, _c); }
    }

    draw_set_font(_antes);
    return _faltan;
}

/// @function debug_exigir_fuente_con_acentos(_fuente, _muestra)
/// @desc     Falla ruidosamente si la fuente no dibuja los caracteres que le pasas.
///           Llámalo UNA vez al arrancar, con la fuente que vas a usar para el texto
///           del juego. Cuesta microsegundos y cierra la Trampa 12 entera.
/// @param    {Asset.GMFont|Real} _fuente
/// @param    {String}            _muestra
/// @returns  {Bool}  true si están todos.
function debug_exigir_fuente_con_acentos(_fuente = -1, _muestra = "áéíóúüñÁÉÍÓÚÜÑ¿¡") {
    var _faltan = debug_fuente_sin_glifos(_fuente, _muestra);
    if (array_length(_faltan) == 0) { return true; }

    var _texto = "FUENTE SIN GLIFOS: la fuente elegida no dibuja "
               + string(array_length(_faltan)) + " carácter(es) de tu texto: "
               + string_join_ext("", _faltan)
               + "\nSe dibujarán como nada, sin error y sin aviso (12 · 09 Trampa 12).";
    show_debug_message(_texto);
    return false;
}


// ============================================================================
// EL SONIDO QUE NO SUENA, MEDIDO EN VEZ DE ESCUCHADO
//
// Conviene saber qué caza ya el compilador antes de añadir una guarda, así que se
// midió (09-09-2026):
//   · Un asset de sonido SIN archivo y que nadie referencia → compila limpio: el
//     compilador lo descarta por no usado.
//   · El mismo, referenciado desde GML → rompe el build con
//     `Failed to convert audio file … source file does not exist` (exit 1).
//
// O sea: el asset sin archivo YA lo caza el compilador. Lo que NO caza es un
// archivo que sí existe y no suena — silencio grabado, una conversión que salió
// vacía, un `.ogg` de 0 s. Para eso sirve esto.
//
//   MEDIDO con `bash _indice/validar-ejecucion.sh`, en cada pasada:
//       audio_sound_length(snd_con_archivo_de_medio_segundo) == 0.50
//
// ⚠️ Lo que prueba y lo que no. Duración 0 prueba que no hay audio: es
//    concluyente. Duración > 0 prueba que hay algo, no que sea el sonido
//    correcto ni que se oiga a un volumen razonable. Eso lo juzga una persona
//    (`13 · 09 §4`). Es una red barata, no un sustituto de escuchar.
// ============================================================================

/// @function debug_sonidos_vacios(_sonidos)
/// @desc     Devuelve los sonidos de la lista que duran 0 s — es decir, los que
///           existen como asset y no tienen archivo detrás.
/// @param    {Array} _sonidos  Array de índices de sonido.
/// @returns  {Array}           Los que están vacíos. Array vacío = todos bien.
function debug_sonidos_vacios(_sonidos) {
    var _vacios = [];
    if (!is_array(_sonidos)) { return _vacios; }

    for (var _i = 0; _i < array_length(_sonidos); _i++) {
        var _s = _sonidos[_i];
        if (!audio_exists(_s) || audio_sound_length(_s) <= 0) {
            array_push(_vacios, _s);
        }
    }
    return _vacios;
}

/// @function debug_exigir_sonidos(_sonidos)
/// @desc     Falla ruidosamente si alguno de los sonidos está vacío. Llámalo una
///           vez al arrancar con los que de verdad tienen que sonar.
/// @param    {Array} _sonidos
/// @returns  {Bool}  true si están todos.
function debug_exigir_sonidos(_sonidos) {
    var _vacios = debug_sonidos_vacios(_sonidos);
    if (array_length(_vacios) == 0) { return true; }

    show_debug_message("SONIDOS VACÍOS: " + string(array_length(_vacios))
        + " asset(s) de sonido duran 0 s: existen y no suenan. Si el archivo falta,"
        + " el compilador lo dice al referenciarlo; si está pero es silencio o dura"
        + " cero, esto es lo único que lo caza. Ver 13 · 09 §8 quater.");
    return false;
}
