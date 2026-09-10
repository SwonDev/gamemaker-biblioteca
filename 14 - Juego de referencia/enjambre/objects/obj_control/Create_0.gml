/// Estado global del juego. Persistente: sobrevive al cambio de sala.
/// Un único sitio donde vive el estado es lo que evita que cada pantalla
/// invente el suyo y se contradigan (13 · 06).
persistent = true;

global.idioma      = "es";
global.record      = 0;
global.op_musica   = 0.5;
global.op_efectos  = 0.8;
global.op_sacudida = true;

global.transicion = false;   // guarda: nadie acepta entrada mientras se cambia de sala
global.sacudida  = 0;      // intensidad actual de la sacudida de cámara
global.congelado = 0;      // fotogramas de hit-stop pendientes
global.puntos    = 0;
global.oleada    = 1;
global.vidas     = 3;

cargar_datos();            // si no hay partida, se queda con los valores de arriba

// La música se lanza UNA vez y se guarda su identificador, para poder pararla y
// volver a lanzarla con otra ganancia sin que se solapen dos copias.
musica_id = -1;
if (global.op_musica > 0) {
    musica_id = audio_play_sound(snd_musica, 1, true, global.op_musica);
}

window_set_caption("Enjambre");

/// --- La fuente, y por qué NO es la de por defecto ----------------------------
/// `draw_set_font(-1)` compila limpio y dibuja «Crditos» en vez de «Créditos»: la
/// fuente integrada del motor no tiene glifos para á é í ó ú ñ ¿ ¡ y **los omite en
/// silencio** (12 · 09 §0 Trampa 12). Se vio en la primera captura de este mismo juego.
/// La salida es una fuente de sprite propia: sin `.ttf` que licenciar, sin *Included
/// File* y sin abrir el IDE.
global.fnt = font_add_sprite_ext(spr_glifos, " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?-+()áéíóúüñÁÉÍÓÚÜÑ¿¡", true, 1);
draw_set_font(global.fnt);

/// --- Modo captura -----------------------------------------------------------
/// Solo se activa si existe un archivo marcador que ningún jugador va a tener. Sirve
/// para que la prueba visual sea REPRODUCIBLE: recorre las pantallas **pulsando teclas
/// de verdad** (`keyboard_key_press`), no tocando variables por detrás, así que lo que
/// se fotografía es el mismo camino que recorre una persona.
global.captura = file_exists("modo_captura.txt");
global.captura_destino = "01_portada";
global.captura_mover_x = 0;
global.captura_mover_y = 0;
global.captura_disparar = false;
if (global.captura) {
    var _f = file_text_open_read("modo_captura.txt");
    if (_f != -1) {
        var _linea = string_trim(file_text_read_string(_f));
        file_text_close(_f);
        if (_linea != "") global.captura_destino = _linea;
    }
}
// Cada ejecución escribe con SU propio prefijo. `gm-cli run` arranca el juego más de
// una vez (compilación + ejecución), y sin prefijo las dos tandas se pisaban los
// archivos: salían capturas con nombre de una pantalla y contenido de otra. Un fallo
// de la prueba, no del juego, pero que invalidaba la prueba entera.
global.sello = string(date_get_hour(date_current_datetime())) + "_" +
               string(date_get_minute(date_current_datetime())) + "_" +
               string(date_get_second(date_current_datetime()));
paso_captura = 0;
reloj_captura = 0;
