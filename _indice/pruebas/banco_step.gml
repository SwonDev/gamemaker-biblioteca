// Evento Step del objeto de pruebas. Hace falta porque la desactivación de una
// instancia NO surte efecto hasta el final del evento en que se pide: para medir
// qué contesta `instance_exists()` sobre una desactivada hay que esperar un frame.
paso++;

if (paso == 1) banco_desactivadas_preparar();

if (paso == 4)
{
    banco_desactivadas_comprobar();

    show_debug_message("=========================================");
    show_debug_message("RESULTADO: " + string(global.ok) + " correctas, " + string(global.ko) + " fallidas");
    show_debug_message("=========================================");
    game_end();
}
