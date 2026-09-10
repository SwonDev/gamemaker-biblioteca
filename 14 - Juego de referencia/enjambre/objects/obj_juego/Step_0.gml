tiempo += 1;
var _e = entrada_leer();

// --- pausa ------------------------------------------------------------------
if (estado == "jugando" && _e.pausa) {
    estado = "pausa"; opcion = 0; sonar(snd_clic, 0.9);
} else if (estado == "pausa") {
    // La pausa congela el mundo de verdad: los objetos consultan este estado antes
    // de moverse. Un menú de pausa sobre un juego que sigue corriendo debajo es de
    // los errores más comunes y de los más feos (04 · 41 §4).
    if (_e.abajo)  { opcion = (opcion + 1) mod array_length(opciones_pausa); sonar(snd_clic, 1); }
    if (_e.arriba) { opcion = (opcion - 1 + array_length(opciones_pausa)) mod array_length(opciones_pausa); sonar(snd_clic, 1); }
    if (_e.aceptar) {
        sonar(snd_clic, 1.2);
        switch (opciones_pausa[opcion]) {
            case "continuar": estado = "jugando"; break;
            case "reiniciar":
                global.puntos = 0; global.oleada = 1; global.vidas = 3;
                room_restart();
                break;
            case "al_menu": room_goto(rm_titulo); break;
        }
    }
    if (_e.atras) { estado = "jugando"; sonar(snd_clic, 0.9); }
    exit;
}

if (estado == "derrota") {
    if (_e.aceptar) {
        global.puntos = 0; global.oleada = 1; global.vidas = 3;
        room_restart();
    }
    if (_e.atras) room_goto(rm_titulo);
    exit;
}

if (global.congelado > 0) exit;

// --- oleadas ----------------------------------------------------------------
if (aviso_oleada > 0) aviso_oleada -= 1;
temporizador -= 1;
if (temporizador <= 0 && array_length(pendientes) > 0) {
    temporizador = max(12, 42 - global.oleada * 2);
    var _tipo = pendientes[0];
    array_delete(pendientes, 0, 1);
    // Aparecen por los bordes, nunca encima del jugador: que te maten por aparición
    // es la forma más rápida de que alguien cierre el juego.
    var _lado = irandom(3);
    var _x = 0, _y = 0;
    switch (_lado) {
        case 0: _x = irandom(room_width); _y = -24; break;
        case 1: _x = irandom(room_width); _y = room_height + 24; break;
        case 2: _x = -24; _y = irandom(room_height); break;
        case 3: _x = room_width + 24; _y = irandom(room_height); break;
    }
    instance_create_layer(_x, _y, "Instances", obj_enemigo, { tipo : _tipo, generacion : 0 });
}

if (array_length(pendientes) == 0 && !instance_exists(obj_enemigo)) {
    global.oleada += 1;
    global.puntos += 50 * global.oleada;
    pendientes = componer_oleada(global.oleada);
    aviso_oleada = 110;
    temporizador = 70;
    sonar(snd_oleada, 1);
}

// --- derrota ----------------------------------------------------------------
if (global.vidas <= 0 && estado == "jugando") {
    estado = "derrota";
    record_nuevo = (global.puntos > global.record);
    if (record_nuevo) { global.record = global.puntos; }
    guardar_datos();
    sacudir(20);
}
