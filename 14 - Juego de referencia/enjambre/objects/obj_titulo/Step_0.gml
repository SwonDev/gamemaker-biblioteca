tiempo += 1;

// Guarda de transición (04 · 41 §4). Sin ella, durante el fundido de salida hacia el
// juego el menú sigue aceptando ENTER y puede lanzar una segunda transición sobre la
// primera. El auditor de la biblioteca lo señaló en este mismo proyecto.
if (global.transicion) exit;

var _e = entrada_leer();

switch (estado) {
    case "portada":
        // La portada SIEMPRE se puede saltar. Una intro que no se salta es lo primero
        // que odia quien vuelve a abrir el juego (04 · 00).
        if (_e.aceptar || _e.atras || tiempo > 60 * 6) {
            estado = "menu"; sonar(snd_clic, 1);
        }
        break;

    case "menu":
        if (_e.abajo)  { opcion = (opcion + 1) mod array_length(opciones_menu); sonar(snd_clic, 1); }
        if (_e.arriba) { opcion = (opcion - 1 + array_length(opciones_menu)) mod array_length(opciones_menu); sonar(snd_clic, 1); }
        if (_e.aceptar) {
            sonar(snd_clic, 1.2);
            switch (opciones_menu[opcion]) {
                case "jugar":
                    global.puntos = 0; global.oleada = 1; global.vidas = 3;
                    global.transicion = true;
                    room_goto(rm_juego);
                    break;
                case "opciones":  estado = "opciones"; opcion = 0; break;
                case "creditos":  estado = "creditos"; break;
                case "salir":     game_end(0); break;
            }
        }
        break;

    case "opciones":
        if (_e.abajo)  { opcion = (opcion + 1) mod array_length(opciones_ajustes); sonar(snd_clic, 1); }
        if (_e.arriba) { opcion = (opcion - 1 + array_length(opciones_ajustes)) mod array_length(opciones_ajustes); sonar(snd_clic, 1); }
        var _paso = (_e.derecha ? 1 : 0) - (_e.izquierda ? 1 : 0);
        var _ajuste = opciones_ajustes[opcion];
        if (_paso != 0 || (_e.aceptar && _ajuste != "volver")) {
            sonar(snd_clic, 1);
            switch (_ajuste) {
                case "idioma":   global.idioma = (global.idioma == "es") ? "en" : "es"; break;
                case "musica":   global.op_musica = clamp(global.op_musica + _paso * 0.1, 0, 1); break;
                case "efectos":  global.op_efectos = clamp(global.op_efectos + _paso * 0.1, 0, 1); break;
                case "sacudida": global.op_sacudida = !global.op_sacudida; break;
                case "pantalla": window_set_fullscreen(!window_get_fullscreen()); break;
            }
            guardar_datos();
        }
        if ((_e.aceptar && _ajuste == "volver") || _e.atras) {
            estado = "menu"; opcion = 0; sonar(snd_clic, 0.9);
            guardar_datos();
        }
        break;

    case "creditos":
        if (_e.aceptar || _e.atras) { estado = "menu"; sonar(snd_clic, 0.9); }
        break;
}
