/// Funciones compartidas de «Enjambre».
/// Cada símbolo del runtime usado aquí se verificó con buscar.py ANTES de escribirlo.

#macro ENJ_VERSION_GUARDADO 1
#macro ENJ_ARCHIVO_GUARDADO "enjambre.sav"

/// @desc Textos en dos idiomas. Ni una cadena suelta en un draw_text: el auditor
///       lo comprueba y, sobre todo, así el juego se traduce sin tocar el código.
function txt(_clave) {
    var _es = global.idioma == "es";
    switch (_clave) {
        case "titulo":      return "ENJAMBRE";
        case "sub":         return _es ? "el último dron de escolta" : "the last escort drone";
        case "jugar":       return _es ? "Jugar" : "Play";
        case "opciones":    return _es ? "Opciones" : "Options";
        case "creditos":    return _es ? "Créditos" : "Credits";
        case "salir":       return _es ? "Salir" : "Quit";
        case "volver":      return _es ? "Volver" : "Back";
        case "idioma":      return _es ? "Idioma" : "Language";
        case "musica":      return _es ? "Música" : "Music";
        case "efectos":     return _es ? "Efectos" : "Sound";
        case "pantalla":    return _es ? "Pantalla completa" : "Fullscreen";
        case "sacudida":    return _es ? "Sacudida de cámara" : "Screen shake";
        case "si":          return _es ? "Sí" : "Yes";
        case "no":          return "No";
        case "pausa":       return _es ? "PAUSA" : "PAUSED";
        case "continuar":   return _es ? "Continuar" : "Resume";
        case "reiniciar":   return _es ? "Reiniciar" : "Restart";
        case "al_menu":     return _es ? "Ir al menú" : "Main menu";
        case "oleada":      return _es ? "Oleada" : "Wave";
        case "puntos":      return _es ? "Puntos" : "Score";
        case "record":      return _es ? "Récord" : "Best";
        case "vidas":       return _es ? "Vidas" : "Lives";
        case "energia":     return _es ? "Energía" : "Energy";
        case "fin":         return _es ? "COLMENA PERDIDA" : "HIVE LOST";
        case "nuevo_record": return _es ? "¡NUEVO RÉCORD!" : "NEW BEST!";
        case "reintentar":  return _es ? "Reintentar" : "Try again";
        case "pulsa":       return _es ? "Pulsa ENTER o A del mando" : "Press ENTER or gamepad A";
        case "ayuda_mov":   return _es ? "WASD mover · ratón apuntar · clic disparar"
                                       : "WASD move · mouse aim · click to shoot";
        case "ayuda_mando": return _es ? "Mando: palancas para mover y apuntar, RT dispara"
                                       : "Gamepad: sticks to move and aim, RT to shoot";
        case "creditos_txt": return _es
            ? "Código, arte y sonido generados para demostrar\nla biblioteca «gamemaker-biblioteca».\n\nArte: pixel art dibujado por código con Pillow.\nSonido: sintetizado con la librería wave de Python.\nSin assets de terceros."
            : "Code, art and sound generated to demonstrate\nthe «gamemaker-biblioteca» library.\n\nArt: pixel art drawn in code with Pillow.\nSound: synthesised with Python's wave module.\nNo third-party assets.";
        default:            return _clave;
    }
}

/// @desc Sacudida de cámara. Un impacto sin sacudida se siente de plástico (04 · 15).
function sacudir(_fuerza) {
    if (!global.op_sacudida) return;
    global.sacudida = max(global.sacudida, _fuerza);
}

/// @desc Detiene el mundo unos fotogramas. El *hit-stop* es lo que hace que un golpe
///       pese: sin él, el enemigo muere y no ha pasado nada.
function congelar(_fotogramas) {
    global.congelado = max(global.congelado, _fotogramas);
}

/// @desc Reproduce con la ganancia de efectos configurada.
function sonar(_snd, _tono) {
    if (global.op_efectos <= 0) return noone;
    var _t = is_undefined(_tono) ? 1 : _tono;
    var _v = audio_play_sound(_snd, 5, false, global.op_efectos, 0, _t);
    return _v;
}

/// @desc Guardado con VERSIÓN de esquema y suma de comprobación. Sin la versión, la
///       primera actualización del juego rompe las partidas de todo el mundo (01 · 14).
function guardar_datos() {
    var _datos = {
        version : ENJ_VERSION_GUARDADO,
        record  : global.record,
        idioma  : global.idioma,
        musica  : global.op_musica,
        efectos : global.op_efectos,
        sacudida: global.op_sacudida,
    };
    var _json = json_stringify(_datos);
    var _suma = 0;
    for (var i = 0; i < string_length(_json); i++) {
        _suma = (_suma + ord(string_char_at(_json, i + 1)) * (i + 1)) mod 1000000007;
    }
    var _sobre = json_stringify({ suma : _suma, cuerpo : _json });
    var _b = buffer_create(string_byte_length(_sobre) + 1, buffer_grow, 1);
    buffer_write(_b, buffer_string, _sobre);
    buffer_save(_b, ENJ_ARCHIVO_GUARDADO);
    buffer_delete(_b);          // se libera aquí mismo: no se fía de nadie más
}

/// @desc Carga verificando la suma. Un archivo manipulado o truncado se descarta
///       entero en vez de meter datos raros en el juego.
function cargar_datos() {
    if (!file_exists(ENJ_ARCHIVO_GUARDADO)) return false;
    var _b = buffer_load(ENJ_ARCHIVO_GUARDADO);
    if (_b < 0) return false;
    var _texto = buffer_read(_b, buffer_string);
    buffer_delete(_b);
    var _sobre = undefined;
    try { _sobre = json_parse(_texto); } catch (_e) { return false; }
    if (!is_struct(_sobre) || !struct_exists(_sobre, "suma") || !struct_exists(_sobre, "cuerpo")) {
        return false;
    }
    var _json = _sobre.cuerpo;
    var _suma = 0;
    for (var i = 0; i < string_length(_json); i++) {
        _suma = (_suma + ord(string_char_at(_json, i + 1)) * (i + 1)) mod 1000000007;
    }
    if (_suma != _sobre.suma) return false;
    var _d = undefined;
    try { _d = json_parse(_json); } catch (_e) { return false; }
    if (!is_struct(_d) || !struct_exists(_d, "version")) return false;
    if (_d.version > ENJ_VERSION_GUARDADO) return false;   // partida de un juego más nuevo
    global.record      = struct_exists(_d, "record")   ? _d.record   : 0;
    global.idioma      = struct_exists(_d, "idioma")   ? _d.idioma   : "es";
    global.op_musica   = struct_exists(_d, "musica")   ? _d.musica   : 0.5;
    global.op_efectos  = struct_exists(_d, "efectos")  ? _d.efectos  : 0.8;
    global.op_sacudida = struct_exists(_d, "sacudida") ? _d.sacudida : true;
    return true;
}

/// @desc Entrada unificada: teclado Y mando, en un solo sitio. Consultar el mando
///       disperso por diez objetos es como se acaba con un juego que solo responde
///       al teclado en la mitad de las pantallas.
function entrada_leer() {
    var _m = 0;   // primer mando conectado, si lo hay
    var _hay_mando = gamepad_is_connected(0);
    var _e = {
        mover_x : 0, mover_y : 0, apuntar_x : 0, apuntar_y : 0,
        disparar : false, aceptar : false, atras : false, pausa : false,
        arriba : false, abajo : false, izquierda : false, derecha : false,
        usa_mando : _hay_mando,
    };
    _e.mover_x = keyboard_check(ord("D")) - keyboard_check(ord("A"));
    _e.mover_y = keyboard_check(ord("S")) - keyboard_check(ord("W"));
    _e.disparar = mouse_check_button(mb_left);
    _e.aceptar  = keyboard_check_pressed(vk_enter) || keyboard_check_pressed(vk_space);
    _e.atras    = keyboard_check_pressed(vk_escape);
    _e.pausa    = keyboard_check_pressed(vk_escape) || keyboard_check_pressed(ord("P"));
    _e.arriba   = keyboard_check_pressed(vk_up) || keyboard_check_pressed(ord("W"));
    _e.abajo    = keyboard_check_pressed(vk_down) || keyboard_check_pressed(ord("S"));
    _e.izquierda = keyboard_check_pressed(vk_left) || keyboard_check_pressed(ord("A"));
    _e.derecha  = keyboard_check_pressed(vk_right) || keyboard_check_pressed(ord("D"));
    if (_hay_mando) {
        var _lx = gamepad_axis_value(_m, gp_axislh);
        var _ly = gamepad_axis_value(_m, gp_axislv);
        if (abs(_lx) > 0.25) _e.mover_x = _lx;
        if (abs(_ly) > 0.25) _e.mover_y = _ly;
        _e.apuntar_x = gamepad_axis_value(_m, gp_axisrh);
        _e.apuntar_y = gamepad_axis_value(_m, gp_axisrv);
        if (gamepad_button_check(_m, gp_shoulderrb) ||
            gamepad_axis_value(_m, gp_axisrh) != 0 ||
            gamepad_axis_value(_m, gp_axisrv) != 0) {
            if (point_distance(0, 0, _e.apuntar_x, _e.apuntar_y) > 0.4) _e.disparar = true;
        }
        if (gamepad_button_check(_m, gp_shoulderrb)) _e.disparar = true;
        _e.aceptar  = _e.aceptar || gamepad_button_check_pressed(_m, gp_face1);
        _e.atras    = _e.atras   || gamepad_button_check_pressed(_m, gp_face2);
        _e.pausa    = _e.pausa   || gamepad_button_check_pressed(_m, gp_start);
        _e.arriba   = _e.arriba  || gamepad_button_check_pressed(_m, gp_padu);
        _e.abajo    = _e.abajo   || gamepad_button_check_pressed(_m, gp_padd);
        _e.izquierda = _e.izquierda || gamepad_button_check_pressed(_m, gp_padl);
        _e.derecha  = _e.derecha || gamepad_button_check_pressed(_m, gp_padr);
    }
    // Entrada simulada del modo captura. Va DENTRO de `entrada_leer` a propósito: así
    // la prueba recorre el mismo camino que una persona —el jugador de verdad dispara
    // por aquí— en vez de llamar a las funciones internas por detrás, que probaría
    // otra cosa. Solo se activa con el archivo marcador, que ningún jugador tiene.
    if (variable_global_exists("captura") && global.captura) {
        if (global.captura_mover_x != 0) _e.mover_x = global.captura_mover_x;
        if (global.captura_mover_y != 0) _e.mover_y = global.captura_mover_y;
        if (global.captura_disparar) _e.disparar = true;
    }
    return _e;
}
