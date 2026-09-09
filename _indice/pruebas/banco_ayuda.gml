// Ayudas del banco de pruebas. VAN EN UN SCRIPT, no en el evento: una función
// declarada dentro de un evento pertenece a la instancia, y dentro de un `with`
// deja de existir.
function comprobar(_nombre, _condicion, _detalle = "")
{
    if (_condicion) { global.ok++; show_debug_message("OK    · " + _nombre); }
    else            { global.ko++; show_debug_message("FALLA · " + _nombre + "  ->  " + string(_detalle)); }
}
