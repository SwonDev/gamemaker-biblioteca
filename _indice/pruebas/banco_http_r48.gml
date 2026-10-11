function prueba_http_comprobar(_nombre, _bien, _detalle = "")
{
    if (_bien) { global.http_ok++; show_debug_message("OK · " + _nombre); }
    else { global.http_ko++; show_debug_message("FALLA · " + _nombre + " · " + _detalle); }
}

function prueba_http_mapa(_estado, _codigo = undefined, _id = 7)
{
    var _mapa = ds_map_create();
    _mapa[? "id"] = _id;
    _mapa[? "status"] = _estado;
    if (!is_undefined(_codigo)) _mapa[? "http_status"] = _codigo;
    return _mapa;
}

function prueba_http_unidad()
{
    var _vectores = [[0, 0], [0.4, 0], [1, 1], [0.3, 0.4]];
    var _esperados = [[0, 0], [0.4, 0], [0.7071067811865476, 0.7071067811865476], [0.3, 0.4]];
    for (var _v = 0; _v < array_length(_vectores); _v++)
    {
        global.http_eje_x = _vectores[_v][0]; global.http_eje_y = _vectores[_v][1];
        var _vector = prueba_http_vector();
        prueba_http_comprobar("input preserva magnitud " + string(_v),
            abs(_vector[0] - _esperados[_v][0]) <= 0.0001 && abs(_vector[1] - _esperados[_v][1]) <= 0.0001,
            json_stringify(_vector) + " frente a " + json_stringify(_esperados[_v]));
    }
    var _m = prueba_http_mapa(1, 200);
    var _r = clasificar_respuesta_http(_m, 7);
    prueba_http_comprobar("progreso conserva intento", _r.coincide && !_r.terminal && !_r.exito_http);
    ds_map_destroy(_m);
    _m = prueba_http_mapa(-1, 200);
    _r = clasificar_respuesta_http(_m, 7);
    prueba_http_comprobar("transporte fallido aunque figure 200", _r.terminal && !_r.exito_http && _r.clase == "transporte");
    ds_map_destroy(_m);
    _m = prueba_http_mapa(0);
    _r = clasificar_respuesta_http(_m, 7);
    prueba_http_comprobar("código ausente no acredita éxito", _r.terminal && !_r.exito_http && _r.clase == "sin_codigo");
    ds_map_destroy(_m);
    var _codigos = [199, 200, 204, 299, 300, 304, 400, 429, 500, 599, 600, 200.5, "200"];
    var _exitos = [false, true, true, true, false, false, false, false, false, false, false, false, false];
    for (var _i = 0; _i < array_length(_codigos); _i++)
    {
        _m = prueba_http_mapa(0, _codigos[_i]);
        _r = clasificar_respuesta_http(_m, 7);
        prueba_http_comprobar("categoría HTTP " + string(_codigos[_i]), _r.terminal && _r.exito_http == _exitos[_i]);
        ds_map_destroy(_m);
    }
    _m = prueba_http_mapa(0, 200, 8);
    _r = clasificar_respuesta_http(_m, 7);
    prueba_http_comprobar("ID ajeno no cambia intento", !_r.coincide && !_r.terminal && !_r.exito_http);
    ds_map_destroy(_m);
    _m = prueba_http_mapa(0, 200);
    _r = clasificar_respuesta_http(_m, -1);
    prueba_http_comprobar("intento invalidado descarta respuesta tardía", !_r.coincide && !_r.terminal);
    ds_map_destroy(_m);
    _m = prueba_http_mapa(2, 200);
    _r = clasificar_respuesta_http(_m, 7);
    prueba_http_comprobar("estado desconocido no se acepta", !_r.terminal && !_r.exito_http);
    ds_map_destroy(_m);
    _m = ds_map_create();
    _r = clasificar_respuesta_http(_m, 7);
    prueba_http_comprobar("map sin campos no se acepta", !_r.coincide && !_r.terminal);
    ds_map_destroy(_m);
}

// Entradas inyectadas en la frontera del fragmento de Step, sin simular hardware.
function input_mover_x() { return global.http_eje_x; }
function input_mover_y() { return global.http_eje_y; }

// Frontera de prueba del dominio liveops: únicamente validar JSON y contar aplicación.
// No simula ni acredita el esquema, balance o caché completa del sistema de liveops.
function __liveops_aplicar_json(_texto)
{
    try
    {
        var _datos = json_parse(_texto);
        if (!is_struct(_datos) || !variable_struct_exists(_datos, "marca")) return false;
        global.http_aplicaciones++;
        return true;
    }
    catch (_error) { return false; }
}

function prueba_http_escribir(_texto)
{
    var _f = file_text_open_write(game_save_id + TELEMETRIA_ARCHIVO);
    file_text_write_string(_f, _texto);
    file_text_close(_f);
}

function prueba_http_empezar()
{
    global.http_ok = 0; global.http_ko = 0;
    global.http_aplicaciones = 0;
    global.liveops_peticion_id = -1;
    global.telemetria_envio_id = -1;
    global.telemetria_envio_cuerpo = undefined;
    global.http_stage = 0;
    global.http_recibido = false;
    global.http_inicio = get_timer();
    prueba_http_unidad();
    prueba_http_lanzar();
}

function prueba_http_lanzar()
{
    global.http_recibido = false;
    var _rutas = ["/config200", "/config500", "/config204", "/configbad",
                  "/post500", "/post200", "/post204", "/postnuevo"];
    var _headers = ds_map_create();
    var _id_peticion = http_request(HTTP_TEST_BASE + _rutas[global.http_stage],
        global.http_stage < 4 ? "GET" : "POST", _headers, global.http_stage < 4 ? "" : "lote inicial");
    ds_map_destroy(_headers);
    prueba_http_comprobar("solicitud local iniciada " + string(global.http_stage), _id_peticion != -1);
    global.http_id = _id_peticion;
    if (global.http_stage < 4) global.liveops_peticion_id = _id_peticion;
    else
    {
        global.telemetria_envio_id = _id_peticion;
        global.telemetria_envio_cuerpo = "lote inicial";
        prueba_http_escribir(global.http_stage == 7 ? "lote nuevo" : "lote inicial");
    }
}

function prueba_http_avanzar()
{
    if (get_timer() - global.http_inicio > 20000000)
    {
        prueba_http_comprobar("respuesta dentro del tope de prueba", false);
        show_debug_message("HTTP_R48: " + string(global.http_ok) + " correctas, " + string(global.http_ko) + " fallidas");
        game_end();
        return;
    }
    if (!global.http_recibido) return;
    var _s = global.http_stage;
    if (_s < 4)
    {
        prueba_http_comprobar("config termina intento " + string(_s), global.liveops_peticion_id == -1);
        prueba_http_comprobar("config solo aplica 200 válido " + string(_s), global.http_aplicaciones == 1);
    }
    else
    {
        prueba_http_comprobar("POST termina intento " + string(_s), global.telemetria_envio_id == -1);
        var _debe_conservar = _s == 4 || _s == 7;
        prueba_http_comprobar("persistencia tras POST " + string(_s),
            file_exists(game_save_id + TELEMETRIA_ARCHIVO) == _debe_conservar);
        if (_s == 7) prueba_http_comprobar("confirmación anterior conserva volcado nuevo", telemetria_leer_pendiente() == "lote nuevo");
    }
    global.http_stage++;
    if (global.http_stage < 8) { prueba_http_lanzar(); return; }
    show_debug_message("HTTP_R48: " + string(global.http_ok) + " correctas, " + string(global.http_ko) + " fallidas");
    game_end();
}
