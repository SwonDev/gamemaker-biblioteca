// Banco de pruebas sobre INSTANCIAS DESACTIVADAS.
//
// Nace de r15 §2.4: un agente escribió `if (instance_exists(global.nivel))` en una
// acción del menú de pausa —donde `instance_deactivate_all()` ya se había llamado— y
// la acción no hizo nada, sin error. Aquí se mide qué contesta de verdad
// `instance_exists()` sobre una instancia desactivada, en el mismo evento y un frame
// después, porque la desactivación no surte efecto hasta el final del evento.
//
// Y de paso se comprueba la consecuencia que eso tiene sobre `scr_pool.gml`, que
// guarda sus instancias libres DESACTIVADAS y las recorre con `instance_exists()`.

function banco_desactivadas_preparar()
{
    global.sonda = instance_create_layer(0, 0, "Instances", obj_bala);
    instance_deactivate_object(global.sonda);

    show_debug_message("MEDIDO · mismo evento, instance_exists(desactivada) = "
        + string(instance_exists(global.sonda)));
    show_debug_message("MEDIDO · mismo evento, instance_number(obj_bala) = "
        + string(instance_number(obj_bala)));

    // El pool también se crea aquí: su constructor desactiva las cinco instancias.
    global.pool = new Pool(obj_bala, 5, "Instances");
    show_debug_message("MEDIDO · mismo evento, pool.count_free() = "
        + string(global.pool.count_free()));
}

function banco_desactivadas_comprobar()
{
    var _existe = instance_exists(global.sonda);
    show_debug_message("MEDIDO · frames despues, instance_exists(desactivada) = " + string(_existe));
    show_debug_message("MEDIDO · frames despues, instance_number(obj_bala) = "
        + string(instance_number(obj_bala)));

    // Lo que sí debe seguir funcionando pase lo que pase:
    instance_activate_object(global.sonda);
    comprobar("tras reactivar, la instancia existe otra vez", instance_exists(global.sonda));
    // Se destruye aquí: la sonda también es un obj_bala y falsearía el recuento
    // final de instancias que deja `destroy()` del pool.
    instance_destroy(global.sonda);

    // --- El pool, un frame despues de que su constructor desactivara todo -------
    var _p = global.pool;
    comprobar("el pool pre-creo 5 libres", _p.count_free() == 5, _p.count_free());

    var _b = _p.get_at(10, 20);
    comprobar("get_at() devuelve una instancia", _b != noone);
    comprobar("y baja las libres a 4", _p.count_free() == 4, _p.count_free());

    _p.release(_b);
    comprobar("release() la devuelve al pool", _p.count_free() == 5, _p.count_free());

    // EL PUNTO: `pool_cleanup_orphans()` recorre `libres`, que son instancias
    // DESACTIVADAS, y borra las que `instance_exists()` diga que no existen.
    var _limpiadas = pool_cleanup_orphans(_p);
    comprobar("cleanup_orphans NO se lleva por delante las libres",
              _p.count_free() == 5,
              "libres=" + string(_p.count_free()) + " limpiadas=" + string(_limpiadas));

    // Y `destroy()` recorre `libres` con la misma guarda. Para saber si de verdad
    // las destruyó hay que ACTIVARLO todo antes de contar: `instance_number()`
    // tampoco ve las desactivadas, así que sin esto el recuento saldría 0 tanto si
    // se destruyeron como si quedaron ahí para siempre. Es la misma trampa que se
    // está midiendo, una vez más.
    _p.destroy();
    instance_activate_object(obj_bala);
    comprobar("destroy() no deja instancias desactivadas en la sala",
              instance_number(obj_bala) == 0,
              "quedan " + string(instance_number(obj_bala)));
}
