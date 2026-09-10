/// Director de la partida: oleadas, pausa, derrota y HUD.

/// Cámara a escala 2. La sala mide 683×384 y la ventana 1366×768: cada píxel del
/// mundo ocupa cuatro en pantalla. Es la diferencia entre «se ve un juego» y «se ven
/// motas de color»: con la sala al tamaño de la ventana, una nave de 24 px se pierde.
/// El HUD NO se escala porque vive en Draw GUI, que va en coordenadas de pantalla.
var _cam = camera_create_view(0, 0, room_width, room_height, 0, noone, -1, -1, 0, 0);
view_set_camera(0, _cam);
view_set_visible(0, true);
view_enabled = true;
estado = "jugando";       // jugando · pausa · derrota
opcion = 0;
opciones_pausa = ["continuar", "reiniciar", "al_menu"];
temporizador = 60;
enemigos_pendientes = 0;
aviso_oleada = 90;
tiempo = 0;
record_nuevo = false;

// Fondo: tres capas de estrellas. Se crean aquí, no en la sala, para que el número
// se ajuste al tamaño real de la ventana.
for (var c = 0; c < 3; c++) {
    repeat (26 - c * 6) {
        instance_create_layer(irandom(room_width), irandom(room_height),
            "Instances", obj_estrella, { capa : c });
    }
}
instance_create_layer(room_width / 2, room_height / 2, "Instances", obj_nave, {});

function componer_oleada(_n) {
    // La oleada 1 solo tiene rastreadores; el veloz entra en la 3 y el divisor en
    // la 5. Enseñar una pieza cada vez es lo que hace que se entienda (13 · 02).
    var _lista = [];
    var _base = 3 + floor(_n * 1.6);
    repeat (_base) array_push(_lista, 0);
    if (_n >= 3) repeat (1 + floor(_n / 2)) array_push(_lista, 1);
    if (_n >= 5) repeat (1 + floor(_n / 4)) array_push(_lista, 2);
    return _lista;
}
pendientes = componer_oleada(global.oleada);
