// Banco de pruebas de los scripts reutilizables que hasta ahora solo estaban
// COMPILADOS. Compilar demuestra que la sintaxis es válida y que los símbolos
// existen; nada más. Lo que sigue comprueba que además hacen lo que dicen.
//
// Cubre: scr_math_util · scr_state_machine · scr_grid_pathfinding · scr_tiempo ·
//        scr_save_load · scr_ui_confirmar

function banco_math()
{
    comprobar("approach no se pasa del objetivo", approach(0, 10, 3) == 3, approach(0, 10, 3));
    comprobar("approach clava el objetivo en el ultimo paso", approach(9, 10, 3) == 10, approach(9, 10, 3));
    comprobar("approach funciona hacia abajo", approach(10, 0, 3) == 7, approach(10, 0, 3));
    comprobar("approach con paso 0 no se mueve", approach(5, 10, 0) == 5, approach(5, 10, 0));

    comprobar("remap traslada el rango", remap(5, 0, 10, 0, 100) == 50, remap(5, 0, 10, 0, 100));
    comprobar("remap_clamped no se sale por arriba",
              remap_clamped(20, 0, 10, 0, 100) == 100, remap_clamped(20, 0, 10, 0, 100));
    comprobar("remap_clamped no se sale por abajo",
              remap_clamped(-5, 0, 10, 0, 100) == 0, remap_clamped(-5, 0, 10, 0, 100));

    comprobar("snap redondea a la rejilla", snap(17, 16) == 16, snap(17, 16));
    // Ojo con el ORDEN: smoothstep(_borde0, _borde1, _x), no (_x, ...).
    comprobar("smoothstep en los extremos",
              smoothstep(0, 10, 0) == 0 && smoothstep(0, 10, 10) == 1,
              string(smoothstep(0, 10, 0)) + " / " + string(smoothstep(0, 10, 10)));
    comprobar("smoothstep en el centro vale 0.5",
              abs(smoothstep(0, 10, 5) - 0.5) < 0.001, smoothstep(0, 10, 5));

    // Las 16 funciones de easing tienen que valer 0 en 0 y 1 en 1. Es la
    // propiedad que las hace intercambiables, y la que se rompe al copiar mal
    // una constante — sin que el compilador diga nada.
    var _fallan = "";
    var _nombres = ["linear","in_sine","out_sine","in_out_sine","in_quad","out_quad",
                    "in_out_quad","in_cubic","out_cubic","in_out_cubic","out_expo"];
    var _fns = [ease_linear, ease_in_sine, ease_out_sine, ease_in_out_sine, ease_in_quad,
                ease_out_quad, ease_in_out_quad, ease_in_cubic, ease_out_cubic,
                ease_in_out_cubic, ease_out_expo];
    for (var _i = 0; _i < array_length(_fns); _i++)
    {
        var _f = _fns[_i];
        if (abs(_f(0) - 0) > 0.001 || abs(_f(1) - 1) > 0.001) _fallan += _nombres[_i] + " ";
    }
    comprobar("las 11 curvas de easing valen 0 en 0 y 1 en 1", _fallan == "", _fallan);

    // Las de rebote y elástico solo tienen que clavar el 1 al final.
    comprobar("ease_out_bounce y ease_out_elastic terminan en 1",
              abs(ease_out_bounce(1) - 1) < 0.001 && abs(ease_out_elastic(1) - 1) < 0.001,
              string(ease_out_bounce(1)) + " / " + string(ease_out_elastic(1)));
}


function banco_fsm()
{
    var _traza = { visitados: [], salidas: [] };
    var _estados = {
        quieto: {
            enter:  method(_traza, function() { array_push(visitados, "quieto"); }),
            exit:   method(_traza, function() { array_push(salidas,  "quieto"); }),
        },
        andando: {
            enter:  method(_traza, function() { array_push(visitados, "andando"); }),
            exit:   method(_traza, function() { array_push(salidas,  "andando"); }),
        }
    };

    var _fsm = new StateMachine(id, _estados, "quieto");
    comprobar("la FSM arranca en el estado inicial", _fsm.get() == "quieto", _fsm.get());
    comprobar("y llamo a su enter", array_length(_traza.visitados) == 1, _traza.visitados);

    comprobar("cambiar de estado devuelve true", _fsm.set("andando"));
    comprobar("ahora esta en el nuevo", _fsm.is("andando"), _fsm.get());
    comprobar("salio del anterior", array_length(_traza.salidas) == 1 && _traza.salidas[0] == "quieto",
              _traza.salidas);

    comprobar("cambiar al estado en el que YA esta devuelve false", !_fsm.set("andando"));
    comprobar("un estado que no existe devuelve false", !_fsm.set("volando"));
    comprobar("y no cambia el estado actual", _fsm.get() == "andando", _fsm.get());

    comprobar("back() vuelve al anterior", _fsm.back() && _fsm.get() == "quieto", _fsm.get());

    _fsm.update();
    _fsm.update();
    comprobar("get_time cuenta las llamadas a update", _fsm.get_time() == 2, _fsm.get_time());
    _fsm.set("andando");
    comprobar("y se reinicia al cambiar de estado", _fsm.get_time() == 0, _fsm.get_time());

    comprobar("list() devuelve los dos estados", array_length(_fsm.list()) == 2, _fsm.list());
}


function banco_grid()
{
    // Un pasillo con un muro que obliga a rodear:
    //   . . . . .
    //   . . # . .
    //   . . # . .
    //   . . . . .      celda de 16 px
    // OJO: ancho y alto van en PÍXELES, no en celdas. Pasar 5 y 4 aquí deja una
    // rejilla de 1x1 que nunca encuentra ruta — el script ahora lo avisa.
    var _g = new GridPonderado(16, 5 * 16, 4 * 16, 0, 0);
    comprobar("la rejilla tiene el tamano pedido en CELDAS",
              _g.columnas == 5 && _g.filas == 4,
              string(_g.columnas) + "x" + string(_g.filas));
    _g.bloquear(2, 1);
    _g.bloquear(2, 2);

    var _ruta = _g.buscar(0, 1, 4, 1, false);
    comprobar("hay ruta rodeando el muro", array_length(_ruta) > 0, array_length(_ruta));
    comprobar("la ruta empieza donde se pidio",
              array_length(_ruta) > 0 && _ruta[0].x == 0 * 16 + 8 && _ruta[0].y == 1 * 16 + 8,
              array_length(_ruta) > 0 ? string(_ruta[0].x) + "," + string(_ruta[0].y) : "vacía");
    comprobar("y termina en el destino",
              array_length(_ruta) > 0
              && _ruta[array_length(_ruta) - 1].x == 4 * 16 + 8
              && _ruta[array_length(_ruta) - 1].y == 1 * 16 + 8);

    // Ninguna casilla de la ruta puede caer sobre el muro. Es la comprobación
    // que de verdad importa y la que un `array_length > 0` no hace.
    var _pisa_muro = false;
    for (var _i = 0; _i < array_length(_ruta); _i++)
    {
        var _c = floor(_ruta[_i].x / 16);
        var _f = floor(_ruta[_i].y / 16);
        if (_c == 2 && (_f == 1 || _f == 2)) _pisa_muro = true;
    }
    comprobar("la ruta NO atraviesa el muro", !_pisa_muro);

    // Encerrar el destino: no debe haber ruta, y no debe devolver una a medias.
    var _g2 = new GridPonderado(16, 5 * 16, 4 * 16, 0, 0);
    _g2.bloquear(3, 0); _g2.bloquear(3, 1); _g2.bloquear(3, 2); _g2.bloquear(3, 3);
    comprobar("sin ruta posible devuelve un array vacio",
              array_length(_g2.buscar(0, 1, 4, 1, false)) == 0,
              array_length(_g2.buscar(0, 1, 4, 1, false)));

    comprobar("un destino fuera del mapa devuelve vacio",
              array_length(_g2.buscar(0, 1, 99, 99, false)) == 0);
}


function banco_tiempo()
{
    var _cd = new Cooldown(2);          // 2 segundos
    comprobar("un Cooldown nace listo", _cd.listo());
    comprobar("usarlo devuelve true la primera vez", _cd.usar());
    comprobar("y ya no esta listo", !_cd.listo());
    comprobar("usarlo otra vez devuelve false", !_cd.usar());

    _cd.actualizar(1);
    comprobar("a mitad de recarga, fraccion ~0.5", abs(_cd.fraccion() - 0.5) < 0.01, _cd.fraccion());
    _cd.actualizar(1.5);                // se pasa a propósito
    comprobar("tras pasarse del tiempo vuelve a estar listo", _cd.listo());
    comprobar("y la fraccion no se va por debajo de 0", _cd.fraccion() >= 0, _cd.fraccion());

    var _t = new Temporizador(3);
    comprobar("un Temporizador nuevo no ha terminado", !_t.terminado());
    _t.pausar();
    _t.actualizar(5);
    comprobar("pausado, el tiempo NO corre", !_t.terminado(), _t.restante_segundos());
    _t.reanudar();
    _t.actualizar(5);
    comprobar("reanudado, termina", _t.terminado());
    _t.reiniciar();
    comprobar("reiniciar lo vuelve a poner en marcha", !_t.terminado(), _t.restante_segundos());
}


function banco_guardado()
{
    var _slot = "banco_prueba";
    if (save_exists(_slot)) delete_save(_slot);

    var _datos = {
        nombre: "Ángela",              // con tilde: el guardado va en UTF-8 o no vale
        vida: 87,
        inventario: ["poción", "llave"],
        posicion: { x: 120, y: 340 }
    };

    var _ok = save_game(_slot, _datos);
    comprobar("save_game devuelve true", _ok);
    comprobar("y el archivo existe de verdad", save_exists(_slot));

    var _leido = load_game(_slot);
    comprobar("load_game devuelve un struct", is_struct(_leido), typeof(_leido));
    if (is_struct(_leido))
    {
        comprobar("el texto con tilde sobrevive al viaje", _leido.nombre == "Ángela", _leido.nombre);
        comprobar("los numeros sobreviven", _leido.vida == 87, _leido.vida);
        comprobar("los arrays sobreviven",
                  is_array(_leido.inventario) && array_length(_leido.inventario) == 2
                  && _leido.inventario[1] == "llave", _leido.inventario);
        comprobar("los structs anidados sobreviven",
                  is_struct(_leido.posicion) && _leido.posicion.x == 120, _leido.posicion);
    }

    // Exportar/importar como cadena: el camino de «pásale tu partida a un amigo».
    var _cadena = save_export_string(_datos);
    comprobar("save_export_string devuelve texto", is_string(_cadena) && string_length(_cadena) > 0);
    var _vuelta = save_import_string(_cadena);
    comprobar("save_import_string lo recupera",
              is_struct(_vuelta) && _vuelta.nombre == "Ángela",
              is_struct(_vuelta) ? _vuelta.nombre : typeof(_vuelta));

    // Una cadena corrupta NO debe devolver un struct a medias.
    var _basura = save_import_string("esto no es una partida");
    comprobar("una cadena corrupta no se cuela", !is_struct(_basura) || _basura == undefined,
              typeof(_basura));

    comprobar("delete_save borra de verdad", delete_save(_slot) && !save_exists(_slot));
}


// El diálogo de confirmación se prueba A LO LARGO DE VARIOS FRAMES, y no es un
// capricho: `keyboard_key_press()` marca la tecla, pero `keyboard_check_pressed()`
// no la ve hasta el paso siguiente. Una prueba que pulsara y comprobara en la
// misma llamada diría que el diálogo no responde — y sería la prueba la que está
// mal, no el diálogo.
function confirmar_prueba_abrir()
{
    confirmar_configurar_textos("Sí", "No");
    global.res_confirmar = { si: 0, no: 0 };
    confirmar_abrir("¿Seguro?",
        method(global.res_confirmar, function() { si++; }),
        method(global.res_confirmar, function() { no++; }));
    comprobar("el dialogo se abre", confirmar_activo());
    keyboard_key_press(vk_escape);
}

function confirmar_prueba_cancelar()
{
    confirmar_step();
    keyboard_key_release(vk_escape);
    comprobar("cancelar llama a la accion de No",
              global.res_confirmar.no == 1 && global.res_confirmar.si == 0,
              "si=" + string(global.res_confirmar.si) + " no=" + string(global.res_confirmar.no));
    // Al cerrarse sigue "activo" un frame a propósito, para que la pantalla de
    // debajo no lea la misma tecla que acaba de cerrar el diálogo.
    comprobar("un frame despues sigue 'activo' a proposito", confirmar_activo());
}

function confirmar_prueba_no_se_reabre()
{
    // EL BUG QUE ESTO EXISTE PARA CAZAR: si ese estado de "recién cerrado" no se
    // limpia solo, el diálogo se reabre y el jugador no puede salir nunca.
    confirmar_step();
    comprobar("y al siguiente ya NO esta activo: no se reabre", !confirmar_activo());

    confirmar_abrir("¿Seguro?",
        method(global.res_confirmar, function() { si++; }),
        method(global.res_confirmar, function() { no++; }));
    keyboard_key_press(vk_right);      // mover el foco de "No" a "Sí"
}

// El lector inyectable, que es lo que permite cumplir «toda la entrada por UNA
// función». Sin estas comprobaciones, el gancho compilaba y nadie sabía si de
// verdad se usaba: `confirmar_step()` podía seguir leyendo el teclado por su
// cuenta y las pruebas de arriba habrían pasado igual, porque simulan teclas.
//
// Corren al FINAL, después de `confirmar_prueba_cerrar()`, y dejan el diálogo
// cerrado. La primera versión se metió en medio de la secuencia y dejó uno
// abierto: reventó una prueba ajena que llevaba meses en verde. Una prueba que
// no devuelve el estado como lo encontró rompe a la siguiente, no a sí misma.
function confirmar_prueba_lector_inyectado()
{
    global.res_lector = { veces: 0, mover: false };
    confirmar_configurar_entrada(method(global.res_lector, function() {
        veces++;
        return { izquierda: false, derecha: mover, aceptar: !mover, cancelar: false };
    }));

    global.res_confirmar = { si: 0, no: 0 };
    confirmar_abrir("¿Seguro?",
        method(global.res_confirmar, function() { si++; }),
        method(global.res_confirmar, function() { no++; }));
    confirmar_step();

    comprobar("el lector inyectado SE LLAMA", global.res_lector.veces == 1,
              global.res_lector.veces);
    // El foco arranca en «No» a PROPÓSITO: aceptar sin moverlo tiene que ejecutar
    // la acción segura. No es un fallo del lector — es la salvaguarda del script,
    // y esta prueba existe para que nadie la quite sin enterarse.
    comprobar("aceptar sin mover el foco ejecuta 'No' (la salvaguarda)",
              global.res_confirmar.no == 1 && global.res_confirmar.si == 0,
              "si=" + string(global.res_confirmar.si) + " no=" + string(global.res_confirmar.no));
}

function confirmar_prueba_lector_elige_si()
{
    confirmar_step();                       // limpia el «recién cerrado»
    global.res_confirmar = { si: 0, no: 0 };
    confirmar_abrir("¿Seguro?",
        method(global.res_confirmar, function() { si++; }),
        method(global.res_confirmar, function() { no++; }));

    global.res_lector.mover = true;         // el lector pide «derecha»
    confirmar_step();
    global.res_lector.mover = false;        // y ahora «aceptar»
    confirmar_step();

    comprobar("moviendo el foco por el lector inyectado, 'Sí' SÍ se elige",
              global.res_confirmar.si == 1 && global.res_confirmar.no == 0,
              "si=" + string(global.res_confirmar.si) + " no=" + string(global.res_confirmar.no));
}

function confirmar_prueba_lector_por_defecto()
{
    confirmar_step();                       // limpia el «recién cerrado»
    confirmar_configurar_entrada(undefined);

    var _e = confirmar_entrada_por_defecto();
    comprobar("el lector por defecto devuelve las cuatro marcas",
              is_struct(_e) && variable_struct_exists(_e, "izquierda")
              && variable_struct_exists(_e, "derecha")
              && variable_struct_exists(_e, "aceptar")
              && variable_struct_exists(_e, "cancelar"));
    comprobar("y sin ninguna tecla pulsada, las cuatro son falsas",
              !_e.izquierda && !_e.derecha && !_e.aceptar && !_e.cancelar);

    global.res_lector.veces = 0;
    global.res_confirmar = { si: 0, no: 0 };
    confirmar_abrir("¿Seguro?",
        method(global.res_confirmar, function() { si++; }),
        method(global.res_confirmar, function() { no++; }));
    confirmar_step();
    comprobar("tras quitar la inyeccion, el lector viejo YA NO se llama",
              global.res_lector.veces == 0, global.res_lector.veces);
    comprobar("y sin teclas no pasa nada",
              global.res_confirmar.si == 0 && global.res_confirmar.no == 0);

    // Se devuelve el estado como estaba: cancelar cierra el diálogo.
    keyboard_key_press(vk_escape);
}

function confirmar_prueba_lector_limpiar()
{
    confirmar_step();
    keyboard_key_release(vk_escape);
    confirmar_step();
    comprobar("el banco del lector deja el dialogo CERRADO", !confirmar_activo());
}

function confirmar_prueba_mover_foco()
{
    confirmar_step();
    keyboard_key_release(vk_right);
    keyboard_key_press(vk_enter);
}

function confirmar_prueba_aceptar()
{
    confirmar_step();
    keyboard_key_release(vk_enter);
    comprobar("aceptar llama a la accion de Si", global.res_confirmar.si == 1,
              "si=" + string(global.res_confirmar.si) + " no=" + string(global.res_confirmar.no));
}

function confirmar_prueba_cerrar()
{
    confirmar_step();
    comprobar("y tampoco se reabre por este camino", !confirmar_activo());
}


// --- scr_input_buffer: puro, no necesita teclado ----------------------------
// Sus tres constructores reciben booleanos, así que se pueden ejercitar frame a
// frame sin simular una sola tecla. Es justo lo que los hace probables.
function banco_input()
{
    var _b = new InputBuffer(4);
    comprobar("un buffer recien creado no tiene nada", !_b.disponible());

    _b.update(true);
    comprobar("tras pulsar, esta disponible", _b.disponible());
    comprobar("y le quedan 4 frames", _b.restante() == 4, _b.restante());

    _b.update(false);
    _b.update(false);
    comprobar("sigue vivo a los 2 frames", _b.disponible(), _b.restante());

    comprobar("consume() lo gasta y devuelve true", _b.consume());
    comprobar("y ya no esta disponible", !_b.disponible());
    comprobar("consume() otra vez devuelve false", !_b.consume());

    // Y que caduca de verdad: sin esto, el buffer sería una bandera permanente.
    var _b2 = new InputBuffer(3);
    _b2.update(true);
    _b2.update(false); _b2.update(false); _b2.update(false);
    comprobar("el buffer CADUCA a los N frames", !_b2.disponible(), _b2.restante());

    var _c = new CoyoteTime(5);
    _c.update(true);
    comprobar("en el suelo, el coyote esta disponible", _c.disponible());
    _c.update(false);
    comprobar("recien salido del suelo, sigue disponible", _c.disponible(), _c.restante());
    comprobar("y sabe que acaba de salir", _c.acaba_de_salir());
    _c.update(false); _c.update(false); _c.update(false); _c.update(false);
    comprobar("el coyote CADUCA", !_c.disponible(), _c.restante());

    // El caso que hace útil el coyote time: pulsar salto UN frame después de
    // caerse del borde. Con las dos piezas sueltas hay que acordarse de las dos;
    // JumpHelper lo resuelve de una vez.
    var _j = new JumpHelper(4, 4);
    _j.update(true, false);      // en el suelo, sin pulsar
    _j.update(false, true);      // ya en el aire, y AHORA pulsa
    comprobar("JumpHelper deja saltar justo tras salir del borde", _j.puede_saltar());
}


// --- scr_tween: necesita frames, porque avanza con delta_time ---------------
function tween_prueba_lanzar()
{
    tween_clear_all();
    global.res_tween = { hecho: 0 };
    global.obj_tween = { valor: 0, otro: 100 };

    tween_to(global.obj_tween, { valor: 50, otro: 0 }, 0.1, ease_linear,
             method(global.res_tween, function() { hecho++; }));

    comprobar("hay un tween en marcha", tween_count() == 1, tween_count());
    comprobar("y todavia no ha movido nada", global.obj_tween.valor == 0, global.obj_tween.valor);
}

function tween_prueba_comprobar()
{
    comprobar("el tween llego al valor final", global.obj_tween.valor == 50, global.obj_tween.valor);
    comprobar("y movio TODAS las propiedades, no solo la primera",
              global.obj_tween.otro == 0, global.obj_tween.otro);
    comprobar("el callback se llamo UNA vez", global.res_tween.hecho == 1, global.res_tween.hecho);
    comprobar("y el tween se retiro solo de la lista", tween_count() == 0, tween_count());

    // tween_stop: parar a medias no debe llamar al callback.
    var _o = { v: 0 };
    var _r = { hecho: 0 };
    var _t = tween_to(_o, { v: 10 }, 5, ease_linear, method(_r, function() { hecho++; }));
    comprobar("tween_stop lo retira", tween_stop(_t) && tween_count() == 0, tween_count());
    comprobar("y NO dispara el callback al pararlo", _r.hecho == 0, _r.hecho);

    tween_clear_all();
    comprobar("tween_clear_all deja la lista vacia", tween_count() == 0, tween_count());
}


// --- scr_camera: con una cámara de verdad, no con aritmética a mano ---------
// `cam_init` recibe un id de cámara real. Se crea una con `camera_create_view()`
// sin asignarla a ningún viewport: para lo que se comprueba aquí —encuadre,
// límites de sala y decaimiento del temblor— no hace falta que se dibuje.
function banco_camara_preparar()
{
    global.cam_prueba = camera_create_view(0, 0, 320, 180);
    cam_init(global.cam_prueba, 320, 180);

    global.cam_objetivo = instance_create_layer(500, 400, "Instances", obj_bala);
    cam_set_target(global.cam_prueba, global.cam_objetivo);
    cam_set_deadzone(global.cam_prueba, 0, 0);     // sin zona muerta: sigue exacto
    cam_set_smooth(global.cam_prueba, 0);          // sin suavizado: determinista
    cam_set_bounds(global.cam_prueba, 0, 0, 1000, 800);

    cam_center_on(global.cam_prueba, 500, 400);
    comprobar("cam_center_on deja la vista centrada en el punto",
              camera_get_view_x(global.cam_prueba) == 500 - 160
              && camera_get_view_y(global.cam_prueba) == 400 - 90,
              string(camera_get_view_x(global.cam_prueba)) + ","
              + string(camera_get_view_y(global.cam_prueba)));
}

function banco_camara_comprobar()
{
    var _cam = global.cam_prueba;

    // El objetivo se va a la esquina superior izquierda, fuera de los límites:
    // la cámara tiene que PARARSE en el borde, no salirse de la sala.
    global.cam_objetivo.x = 10;
    global.cam_objetivo.y = 10;
    repeat (30) cam_update(_cam);
    comprobar("la camara no se sale por la esquina superior izquierda",
              camera_get_view_x(_cam) >= 0 && camera_get_view_y(_cam) >= 0,
              string(camera_get_view_x(_cam)) + "," + string(camera_get_view_y(_cam)));

    // Y a la inferior derecha: el borde derecho de la vista no puede pasar de 1000.
    global.cam_objetivo.x = 990;
    global.cam_objetivo.y = 790;
    repeat (30) cam_update(_cam);
    comprobar("ni por la esquina inferior derecha",
              camera_get_view_x(_cam) + 320 <= 1000 && camera_get_view_y(_cam) + 180 <= 800,
              string(camera_get_view_x(_cam) + 320) + "," + string(camera_get_view_y(_cam) + 180));

    // El temblor tiene que volver SOLO a cero. Un shake que no decae deja la
    // cámara temblando para siempre y no da ningún error.
    cam_shake(_cam, 8, 0.1);
    var _d = cam_get_data(_cam);
    comprobar("cam_shake arranca el temblor", _d.shake_mag > 0, _d.shake_mag);
    repeat (60) cam_update(_cam);
    comprobar("y el temblor se apaga solo", _d.shake_dur <= 0 && _d.shake_x == 0 && _d.shake_y == 0,
              "dur=" + string(_d.shake_dur) + " x=" + string(_d.shake_x));

    instance_destroy(global.cam_objetivo);
    cam_update(_cam);   // el objetivo ya no existe: no debe reventar
    comprobar("sobrevive a que el objetivo desaparezca", true);

    cam_destroy(_cam);
    comprobar("cam_destroy limpia sus datos", !is_struct(cam_get_data(_cam)));
}


// --- scr_audio: con un sonido de verdad -------------------------------------
// Era el único script reutilizable que no se podía ejecutar, porque sus
// funciones reciben ids de sonido y un proyecto en blanco no tiene ninguno.
// `_indice/pruebas/generar_sonido.py` fabrica medio segundo de tono con la
// biblioteca estándar de Python, y `SOUND SETFILE` lo mete en el proyecto.
function banco_audio_preparar()
{
    audio_init();
    comprobar("audio_init crea los cinco buses",
              variable_global_exists("bus") && struct_exists(global.bus, "musica")
              && struct_exists(global.bus, "sfx") && struct_exists(global.bus, "ui")
              && struct_exists(global.bus, "voz") && struct_exists(global.bus, "ambiente"));
    comprobar("y sus cinco emisores",
              struct_exists(global.em, "musica") && struct_exists(global.em, "sfx"));

    // Llamarlo dos veces no debe rehacer nada: si lo hiciera, se perderían los
    // volúmenes que el jugador acaba de elegir en Opciones.
    global.volumen_sfx = 0.42;
    audio_init();
    comprobar("audio_init dos veces no pisa la mezcla", global.volumen_sfx == 0.42,
              global.volumen_sfx);

    // Round robin: con 3 tomas, nunca debe repetir la misma dos veces seguidas.
    // Es la propiedad que hace que un paso no suene a metralleta, y la que se
    // rompe con un `irandom` a secas sin que nadie lo note al leer el código.
    var _banco = banco_crear([snd_prueba, snd_prueba2, snd_prueba3]);
    var _anterior = -1;
    var _repetida = false;
    repeat (60)
    {
        var _t = banco_siguiente(_banco);
        if (_t == _anterior) _repetida = true;
        _anterior = _t;
    }
    comprobar("el banco NUNCA repite toma dos veces seguidas", !_repetida);

    // Con una sola toma sí tiene que devolver siempre la misma, sin dividir por cero.
    var _uno = banco_crear([snd_prueba]);
    comprobar("un banco de una sola toma devuelve esa",
              banco_siguiente(_uno) == snd_prueba && banco_siguiente(_uno) == snd_prueba);

    comprobar("variacion_tono se queda dentro del rango pedido",
              variacion_tono(0) == 1, variacion_tono(0));

    // Y sonar de verdad: `sfx()` devuelve el id de la voz.
    global.voz_sfx = sfx(snd_prueba, 0.05);
    comprobar("sfx() devuelve una voz que existe", audio_is_playing(global.voz_sfx),
              global.voz_sfx);

    // El cupo de voces: pedir 20 con un máximo de 3 no puede dejar 20 sonando.
    repeat (20) sonar_limitado(snd_prueba2, 3, 0.02);
    comprobar("sonar_limitado respeta el cupo",
              audio_sound_get_track_position(snd_prueba2) >= 0, "sin excepción");
}

function banco_audio_comprobar()
{
    // `audio_step()` mueve el ducking y limpia las voces terminadas. Tras unos
    // frames, la estructura de voces no puede haber crecido sin control.
    comprobar("audio_step no revienta ni deja el sistema inconsistente",
              variable_global_exists("bus") && is_struct(global.bus));

    audio_destruir();
    comprobar("audio_destruir borra la marca de inicializado",
              !is_struct(global.bus), typeof(global.bus));

    // Y LA PRUEBA QUE IMPORTA: destruir y volver a inicializar tiene que dejar el
    // audio FUNCIONANDO. Si no, un controlador de audio no persistente deja el
    // juego mudo a partir del primer cambio de sala, sin un solo error.
    audio_init();
    comprobar("tras destruir, audio_init vuelve a montar los buses",
              is_struct(global.bus) && struct_exists(global.bus, "sfx"), typeof(global.bus));
    comprobar("y los emisores son nuevos y utilizables",
              is_struct(global.em) && audio_emitter_exists(global.em.sfx),
              is_struct(global.em) ? "emisor " + string(global.em.sfx) : typeof(global.em));

    var _v = sfx(snd_prueba, 0.02);
    comprobar("y sonar despues de reiniciar funciona", audio_is_playing(_v), _v);

    // --- La duracion como medida, no como suposicion (13 · 09 §8 quater) -----
    // Un sonido SIN archivo lo caza el compilador en cuanto el GML lo referencia
    // (medido: `Failed to convert audio file`, exit 1). Lo que el compilador NO
    // caza es un archivo que SI existe y no suena. `audio_sound_length()` mide, y
    // esa medida es la que sirve de guarda en el arranque.
    show_debug_message("MEDIDO · audio_sound_length(snd_prueba) = "
        + string(audio_sound_length(snd_prueba)));
    comprobar("un sonido con archivo dura mas que cero",
              audio_sound_length(snd_prueba) > 0, audio_sound_length(snd_prueba));
    comprobar("debug_sonidos_vacios no señala los tres que si tienen archivo",
              array_length(debug_sonidos_vacios([snd_prueba, snd_prueba2, snd_prueba3])) == 0,
              debug_sonidos_vacios([snd_prueba, snd_prueba2, snd_prueba3]));
    comprobar("y debug_exigir_sonidos dice true con ellos",
              debug_exigir_sonidos([snd_prueba, snd_prueba2, snd_prueba3]));

}
