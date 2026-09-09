// Banco de pruebas de la receta `04 · 59 — Puertas, llaves y placas de presión`.
//
// El código bajo prueba NO está aquí: se extrae del propio documento en cada
// ejecución con `extraer_funciones.py`. Si copiara las funciones, las dos copias
// se separarían y esto acabaría comprobando una versión que ya nadie lee.
//
// La receta se escribió el 09-09-2026 y se compiló. Compilar no es ejecutar, así
// que aquí se ejecuta: es la misma vara con la que esta biblioteca mide todo lo
// demás, aplicada también a lo que escribe ella.

function banco_circuitos()
{
    circuitos_reiniciar();
    comprobar("circuitos_reiniciar deja el canal vacio",
              is_struct(global.circuitos) && array_length(struct_get_names(global.circuitos)) == 0);

    // EL CASO QUE LA RECETA SEÑALA EN ROJO: un canal sin emisores NO está abierto.
    // Si devolviera true, una puerta con el nombre mal escrito se abriría sola y
    // parecería que el puzle funciona.
    comprobar("un canal sin emisores NO esta abierto", !circuito_abierto("no_existe", "todos"));

    // Dos placas en el mismo canal, modo "todos".
    circuito_fijar("puerta_norte", 101, false);
    circuito_fijar("puerta_norte", 102, false);
    comprobar("con las dos sueltas, la puerta esta cerrada",
              !circuito_abierto("puerta_norte", "todos"));

    circuito_fijar("puerta_norte", 101, true);
    comprobar("con una sola pulsada, sigue cerrada",
              !circuito_abierto("puerta_norte", "todos"));
    comprobar("pero en modo «alguno» ya esta abierta",
              circuito_abierto("puerta_norte", "alguno"));

    circuito_fijar("puerta_norte", 102, true);
    comprobar("con las dos pulsadas, abierta", circuito_abierto("puerta_norte", "todos"));

    var _n = circuito_cuenta("puerta_norte");
    comprobar("circuito_cuenta devuelve [activos, totales]", _n[0] == 2 && _n[1] == 2, _n);

    // Y se vuelve a cerrar al soltar. Es lo que se pierde si abrir una puerta se
    // hiciera con `instance_destroy()`, como avisa la receta.
    circuito_fijar("puerta_norte", 101, false);
    comprobar("al soltar una placa, la puerta se cierra",
              !circuito_abierto("puerta_norte", "todos"));

    // Que la clave sea el emisor y no un contador: publicar dos veces «pulsada»
    // desde el mismo emisor no puede dejar el canal abierto para siempre.
    circuitos_reiniciar();
    circuito_fijar("p", 200, true);
    circuito_fijar("p", 200, true);
    circuito_fijar("p", 200, false);
    comprobar("publicar dos veces desde el mismo emisor no descuadra la cuenta",
              !circuito_abierto("p", "todos"), circuito_cuenta("p"));

    comprobar("modo «exactamente» distingue el numero",
              !circuito_abierto("p", "exactamente", 1), circuito_cuenta("p"));
    circuito_fijar("p", 201, true);
    comprobar("y acierta cuando coincide", circuito_abierto("p", "exactamente", 1),
              circuito_cuenta("p"));

    // --- Llaves ------------------------------------------------------------
    llaves_reiniciar();
    comprobar("sin llaves, llave_cuantas es 0", llave_cuantas() == 0, llave_cuantas());
    comprobar("y no tienes ninguna concreta", !llave_tienes("n1_x34_y12"));

    llave_coger("n1_x34_y12");
    comprobar("tras cogerla, la tienes", llave_tienes("n1_x34_y12"));
    comprobar("y cuenta 1", llave_cuantas() == 1, llave_cuantas());

    // Coger la misma dos veces no puede contar dos: es lo que pasaría con un
    // contador en vez de una clave estable, y abriría una puerta de más.
    llave_coger("n1_x34_y12");
    comprobar("coger la MISMA llave dos veces sigue contando 1", llave_cuantas() == 1,
              llave_cuantas());

    llave_coger("n1_x99_y99");
    comprobar("otra llave distinta sí suma", llave_cuantas() == 2, llave_cuantas());
}


// Lo que hace falta para poder EJECUTAR las dos funciones de la receta que
// tocan el mundo: `circuitos_validar()` y `nivel_reiniciar()`. Sin esto compilan
// y no se ejecutan nunca — pasarían por verdes sin haber corrido.
#macro CELDA 16

function mi_leyenda()
{
    return {
        "#" : { objeto: obj_muro,    solido: true },
        "@" : { objeto: noone,       papel:  "aparicion" },
        "!" : { objeto: obj_salida,  papel:  "salida" }
    };
}

function mi_mapa(_n)
{
    return ["#####",
            "#@..!",
            "#####"];
}

function banco_circuitos_mundo()
{
    // --- circuitos_validar() ------------------------------------------------
    circuitos_reiniciar();
    var _p = instance_create_layer(0, 0, "Instances", obj_puerta);   // canal "puerta_norte"

    // Una puerta que escucha un canal que nadie emite: es el error de dedo más
    // probable de todo el sistema, y la receta existe para cazarlo.
    var _problemas = circuitos_validar();
    comprobar("circuitos_validar caza una puerta sin emisores",
              array_length(_problemas) > 0, _problemas);

    // Ahora sí hay emisor: no debe quedar ningún problema.
    circuito_fijar("puerta_norte", 999, false);
    _problemas = circuitos_validar();
    comprobar("con emisor y receptor, ningun problema", array_length(_problemas) == 0, _problemas);

    // Y un canal que nadie escucha también se avisa.
    circuito_fijar("canal_huerfano", 998, false);
    _problemas = circuitos_validar();
    comprobar("y un canal que nadie escucha tambien se avisa",
              array_length(_problemas) > 0, _problemas);

    instance_destroy(_p);

    // --- nivel_reiniciar() --------------------------------------------------
    global.nivel_actual = 1;
    global.pasos = 99;
    global.deshacer = ["algo"];
    llaves_reiniciar();
    llave_coger("vieja");
    circuitos_reiniciar();
    circuito_fijar("puerta_norte", 1, true);

    nivel_reiniciar();

    comprobar("nivel_reiniciar limpia los circuitos del intento anterior",
              !circuito_abierto("puerta_norte", "todos"), circuito_cuenta("puerta_norte"));
    comprobar("y las llaves", llave_cuantas() == 0, llave_cuantas());
    comprobar("y los contadores de global", global.pasos == 0 && array_length(global.deshacer) == 0,
              string(global.pasos) + "/" + string(array_length(global.deshacer)));
    comprobar("y reconstruye el nivel: hay muros", instance_number(obj_muro) > 0,
              instance_number(obj_muro));
    comprobar("y crea al jugador en la aparicion", instance_number(obj_jugador) == 1,
              instance_number(obj_jugador));

    // --- celda_bloqueada() --------------------------------------------------
    comprobar("una celda con muro esta bloqueada", celda_bloqueada(0, 0));
    comprobar("y una vacia no", !celda_bloqueada(2, 1));

    with (obj_muro)     instance_destroy();
    with (obj_jugador)  instance_destroy();
    with (obj_salida)   instance_destroy();
}
