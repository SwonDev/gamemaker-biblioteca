// La sacudida se apaga sola. Si no decae, la cámara nunca se queda quieta.
global.sacudida = max(0, global.sacudida - 0.55);
if (global.congelado > 0) global.congelado -= 1;

// La ganancia de la música se sigue en caliente: cambiarla en Opciones se oye al
// instante, sin reiniciar el juego.
if (global.op_musica > 0) {
    if (!audio_is_playing(musica_id)) {
        musica_id = audio_play_sound(snd_musica, 1, true, global.op_musica);
    } else {
        audio_sound_gain(musica_id, global.op_musica, 0);
    }
} else if (audio_is_playing(musica_id)) {
    audio_stop_sound(musica_id);
}

if (!global.captura) exit;

// --- visita guiada, UNA pantalla por ejecución -------------------------------
// La primera versión recorría las siete pantallas en una sola ejecución y guardaba
// las siete capturas seguidas. El resultado: archivos con el nombre de una pantalla
// y el contenido de otra. `screen_save()` no escribe necesariamente el fotograma en
// el que se llama, así que encadenar capturas y cambios de pantalla en la misma
// ejecución no es fiable — y una prueba visual que no se puede creer no vale nada.
//
// Ahora cada ejecución hace UNA cosa: navegar hasta su pantalla, esperar a que esté
// quieta, capturar, esperar de nuevo, y cerrarse. Es más lenta y es incontestable.
// La tecla se suelta al PRINCIPIO del fotograma SIGUIENTE, nunca en el mismo en que
// se pulsa. Soltarla en el mismo Step hacía que los objetos cuyo Step corre después
// de este no llegaran a ver el `keyboard_check_pressed`: el menú se comía una de cada
// dos pulsaciones y la visita guiada se quedaba parada en el menú. El síntoma era una
// captura con nombre «juego» y contenido «menú», que parece un fallo del capturador y
// era de orden de eventos.
if (variable_instance_exists(id, "tecla_pendiente") && tecla_pendiente >= 0) {
    keyboard_key_release(tecla_pendiente);
    tecla_pendiente = -1;
}

reloj_captura += 1;
var _destino = global.captura_destino;
var _teclas = [];
switch (_destino) {
    case "01_portada":  _teclas = []; break;
    case "02_menu":     _teclas = [vk_enter]; break;
    case "03_opciones": _teclas = [vk_enter, vk_down, vk_enter]; break;
    case "04_creditos": _teclas = [vk_enter, vk_down, vk_down, vk_enter]; break;
    case "05_juego":    _teclas = [vk_enter, vk_enter]; break;
    case "06_pausa":    _teclas = [vk_enter, vk_enter]; break;
    case "07_derrota":  _teclas = [vk_enter, vk_enter]; break;
}

// La tecla i se pulsa en el fotograma (i+1)*cadencia. La primera versión calculaba
// el índice con `floor(reloj / cadencia)` y, como el reloj ya venía incrementado, en
// el fotograma 22 daba índice 1: **la tecla 0 no se pulsaba nunca**. El síntoma era
// una captura de menú con nombre de juego, y parecía un fallo del capturador.
var _cadencia = 22;
var _n = array_length(_teclas);
for (var i = 0; i < _n; i++) {
    if (reloj_captura == (i + 1) * _cadencia) {
        keyboard_key_press(_teclas[i]);
        tecla_pendiente = _teclas[i];
    }
}
if (reloj_captura <= _n * _cadencia) exit;

// Ya estamos donde tocaba. Cada pantalla necesita su propio reposo antes de la foto.
var _espera = _n * _cadencia;
switch (_destino) {
    case "05_juego":   _espera += 760; break;   // en plena oleada 3, no en el cambio   // que aparezcan enemigos y se dispare
    case "06_pausa":   _espera += 240; break;
    case "07_derrota": _espera += 240; break;
    default:           _espera += 70;  break;
}

// Mientras se espera en las pantallas de acción, el dron se mueve y dispara: una
// captura del juego con la nave quieta y sin una bala en pantalla no enseña el juego,
// enseña el fondo.
if (_destino == "05_juego" || _destino == "06_pausa" || _destino == "07_derrota") {
    global.captura_disparar = true;
    // Se acerca al enemigo más cercano sin pegarse a él: mantiene la distancia de
    // combate para que en la foto haya balas EN VUELO, no impactos ya consumidos.
    global.captura_mover_x = sin(reloj_captura / 34) * 0.7;
    global.captura_mover_y = cos(reloj_captura / 41) * 0.7;
    with (obj_nave) {
        var _o = instance_nearest(x, y, obj_enemigo);
        if (_o != noone && instance_exists(_o)) {
            var _d = point_distance(x, y, _o.x, _o.y);
            if (_d > 150) {
                global.captura_mover_x = lengthdir_x(1, point_direction(x, y, _o.x, _o.y));
                global.captura_mover_y = lengthdir_y(1, point_direction(x, y, _o.x, _o.y));
            }
        }
    }
}

// Se pulsa **P**, no ESC. ESC significa a la vez «pausa» y «atrás», así que el
// borde de pulsación llegaba dos veces —una abría la pausa y otra la cerraba— y la
// captura salía con el juego corriendo. No es un fallo del juego (ESC dentro de la
// pausa DEBE volver al juego): es que la prueba tenía que elegir una tecla sin doble
// significado.
// Se pulsa **P** y NO se suelta. Medido en esta sesión: `keyboard_key_release()`
// genera un SEGUNDO borde de `keyboard_check_pressed` en el runner de Mac, así que
// pulsar-y-soltar equivale a pulsar dos veces: la primera abría la pausa y la segunda
// la cerraba, y la captura salía con el juego corriendo. Como el juego se cierra solo
// treinta fotogramas después de la foto, dejar la tecla pulsada no tiene consecuencia.
if (_destino == "06_pausa" && reloj_captura == _espera - 60) {
    keyboard_key_press(ord("P"));
}
if (_destino == "07_derrota" && reloj_captura == _espera - 60) {
    global.vidas = 0;                          // provocar la derrota a propósito
}

if (reloj_captura == _espera) {
    // Desde el **Step**, no desde Post-Draw. Se probó a moverlo a Post-Draw porque
    // ahí `application_surface` está viva… y las capturas salieron NEGRAS las dos,
    // incluida la de `screen_save()` que llevaba toda la sesión funcionando. Medido y
    // revertido: `screen_save()` desde el Step captura el fotograma anterior, que es
    // exactamente lo que hace falta.
    screen_save(global.sello + "_" + _destino + ".png");
    show_debug_message("###CAPTURA### " + global.sello + "_" + _destino);
}
// 30 fotogramas de margen tras la captura: tiempo de sobra para que el archivo se
// escriba entero antes de cerrar el juego.
if (reloj_captura > _espera + 30) {
    show_debug_message("###CAPTURA_FIN###");
    game_end(0);
}
