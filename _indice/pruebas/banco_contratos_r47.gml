// Ejecutado por probar-contratos-r47.py contra funciones extraídas de los documentos.
// Las expectativas de plural son ejemplos cardinales de CLDR 48 para enteros.
function contratos_comprobar(_nombre, _condicion, _detalle = "")
{
    if (_condicion) { global.contratos_ok++; show_debug_message("OK · " + _nombre); }
    else { global.contratos_ko++; show_debug_message("FALLA · " + _nombre + " · " + string(_detalle)); }
}

function contratos_plural_casos(_idioma, _cantidades, _esperadas)
{
    for (var _i = 0; _i < array_length(_cantidades); _i++)
    {
        var _actual = categoria_plural_entero(_idioma, _cantidades[_i]);
        contratos_comprobar("plural " + _idioma + " " + string(_cantidades[_i]),
                            _actual == _esperadas[_i], _actual);
    }
}

function contratos_probar_plural()
{
    var _idiomas = ["en", "de"];
    for (var _i = 0; _i < array_length(_idiomas); _i++)
        contratos_plural_casos(_idiomas[_i], [0, 1, 2, -1, 1000000],
                              ["other", "one", "other", "one", "other"]);

    _idiomas = ["es", "it", "pt-PT"];
    for (var _i = 0; _i < array_length(_idiomas); _i++)
        contratos_plural_casos(_idiomas[_i], [0, 1, 2, 999999, 1000000, 1000001, -1000000, 1000000000],
                              ["other", "one", "other", "other", "many", "other", "many", "many"]);

    _idiomas = ["fr", "pt", "pt-BR"];
    for (var _i = 0; _i < array_length(_idiomas); _i++)
        contratos_plural_casos(_idiomas[_i], [0, 1, 2, 1000000, 1000001],
                              ["one", "one", "other", "many", "other"]);

    contratos_plural_casos("ru", [0, 1, 2, 4, 5, 10, 11, 12, 14, 20, 21, 22, 24, 25, 111, 112, 114, 121, -22],
                          ["many", "one", "few", "few", "many", "many", "many", "many", "many", "many",
                           "one", "few", "few", "many", "many", "many", "many", "one", "few"]);
    contratos_plural_casos("ar", [0, 1, 2, 3, 10, 11, 99, 100, 101, 102, 103, 111, 199, 200, -3],
                          ["zero", "one", "two", "few", "few", "many", "many", "other", "other", "other",
                           "few", "many", "many", "other", "few"]);

    _idiomas = ["ja", "ko", "zh"];
    for (var _i = 0; _i < array_length(_idiomas); _i++)
        contratos_plural_casos(_idiomas[_i], [0, 1, 2, 1000000], ["other", "other", "other", "other"]);

    var _invalidos = [1.5, -1.5, 1000000001, -1000000001, "1", undefined, {}, []];
    for (var _i = 0; _i < array_length(_invalidos); _i++)
        contratos_comprobar("plural rechaza cantidad fuera del contrato " + string(_i),
                            is_undefined(categoria_plural_entero("es", _invalidos[_i])));
    contratos_comprobar("plural rechaza idioma no implementado", is_undefined(categoria_plural_entero("pl", 1)));

    global.idioma = "es";
    global.textos = { monedas_one: "{n} moneda", monedas_other: "{n} monedas",
                      monedas_many: "{n} monedas", saludo: "Hola, {nombre}: {zona}." };
    contratos_comprobar("txt_n singular", txt_n("monedas", 1) == "1 moneda");
    contratos_comprobar("txt_n plural", txt_n("monedas", 2) == "2 monedas");
    contratos_comprobar("txt_n categoría many", txt_n("monedas", 1000000) == "1000000 monedas");
    contratos_comprobar("txt_n cantidad inválida visible", txt_n("monedas", 1.5) == "[[monedas:plural_no_admitido]]");
    contratos_comprobar("clave ausente visible", txt("falta") == "[[falta]]");
    contratos_comprobar("interpolación de dos variables", txt("saludo", { nombre: "Ana", zona: "Bosque" }) == "Hola, Ana: Bosque.");
    global.idioma = "ar";
    contratos_comprobar("categoría ausente visible", txt_n("monedas", 2) == "[[monedas_two]]");
    global.idioma = "pl";
    contratos_comprobar("idioma no admitido visible", txt_n("monedas", 1) == "[[monedas:plural_no_admitido]]");
}

// Regla deliberadamente pequeña: un punto por tick; A suma dos, B suma cinco.
// Contadores y orden permiten observar causalmente los ticks vacíos y simultáneos.
function contratos_estado_inicial(_azar)
{
    global.contratos_inicios++;
    return { puntuacion: 0 };
}

function contratos_simular_frame(_estado, _acciones, _azar)
{
    global.contratos_ticks++;
    _estado.puntuacion++;
    for (var _i = 0; _i < array_length(_acciones); _i++)
    {
        global.contratos_acciones++;
        global.contratos_orden += _acciones[_i];
        if (_acciones[_i] == "A") _estado.puntuacion += 2;
        if (_acciones[_i] == "B") _estado.puntuacion += 5;
    }
    return _estado;
}

function contratos_paquete(_replay)
{
    var _json = json_stringify(_replay);
    return { datos_json: _json, hash: sha1_string_utf8(_json) };
}

function contratos_replay_base()
{
    return { semilla: 42, version_simulacion: "r47", frame: 2,
             eventos: [{ frame: 0, accion: "A" }, { frame: 1, accion: "B" }], puntuacion: 9 };
}

function contratos_contexto()
{
    return { semilla: 42, version_simulacion: "r47", max_bytes: 4096,
             max_frames: 601, max_eventos: 10 };
}

function contratos_verificar(_nombre, _paquete, _esperado, _ticks, _acciones = 0, _orden = "", _contexto = undefined)
{
    if (is_undefined(_contexto)) _contexto = contratos_contexto();
    global.contratos_inicios = 0;
    global.contratos_ticks = 0;
    global.contratos_acciones = 0;
    global.contratos_orden = "";
    var _resultado = undefined;
    var _excepcion = "";
    try { _resultado = replay_verificar(_paquete, contratos_estado_inicial, contratos_simular_frame, _contexto); }
    catch (_error) { _excepcion = string(_error); }
    contratos_comprobar(_nombre,
        _excepcion == "" && _resultado == _esperado && global.contratos_ticks == _ticks
        && global.contratos_acciones == _acciones && global.contratos_orden == _orden,
        "resultado=" + string(_resultado) + ", ticks=" + string(global.contratos_ticks)
        + ", acciones=" + string(global.contratos_acciones) + ", orden=" + global.contratos_orden
        + ", excepción=" + _excepcion);
    if (_ticks == 0 && !_esperado)
        contratos_comprobar(_nombre + " no inicia simulación", global.contratos_inicios == 0);
}

function contratos_probar_replay()
{
    replay_iniciar(42, "r47");
    replay_anotar("A");
    replay_anotar("B");
    replay_avanzar_frame();
    var _paquete = replay_cerrar(8);
    contratos_comprobar("el grabador conserva dos acciones simultáneas y un tick",
        global.replay.frame == 1 && array_length(global.replay.eventos) == 2
        && global.replay.eventos[0].frame == 0 && global.replay.eventos[1].frame == 0);
    contratos_verificar("replay grabado reproduce ambas acciones en orden", _paquete, true, 1, 2, "AB");

    var _replay = { semilla: 42, version_simulacion: "r47", frame: 601,
                    eventos: [{ frame: 0, accion: "A" }, { frame: 600, accion: "B" }], puntuacion: 608 };
    contratos_verificar("acciones 0 y 600 conservan 601 ticks", contratos_paquete(_replay), true, 601, 2, "AB");
    _replay = { semilla: 42, version_simulacion: "r47", frame: 10, eventos: [], puntuacion: 10 };
    contratos_verificar("diez ticks vacíos avanzan", contratos_paquete(_replay), true, 10);
    _replay.frame = 0; _replay.puntuacion = 0;
    contratos_verificar("duración cero sin eventos", contratos_paquete(_replay), true, 0);

    _paquete = contratos_paquete(contratos_replay_base());
    var _ctx = contratos_contexto();
    _ctx.max_bytes = string_byte_length(_paquete.datos_json);
    _ctx.max_frames = 2; _ctx.max_eventos = 2;
    contratos_verificar("límites exactos de bytes, duración y eventos", _paquete, true, 2, 2, "AB", _ctx);
    _ctx.max_bytes--;
    contratos_verificar("un byte sobre presupuesto", _paquete, false, 0, 0, "", _ctx);
    _ctx = contratos_contexto(); _ctx.max_frames = 1;
    contratos_verificar("duración sobre presupuesto", _paquete, false, 0, 0, "", _ctx);
    _ctx = contratos_contexto(); _ctx.max_eventos = 1;
    contratos_verificar("eventos sobre presupuesto", _paquete, false, 0, 0, "", _ctx);

    contratos_verificar("paquete no struct", [], false, 0);
    contratos_verificar("paquete sin campos", {}, false, 0);
    contratos_verificar("datos no string", { datos_json: 123, hash: "x" }, false, 0);
    contratos_verificar("hash no string", { datos_json: "{}", hash: 123 }, false, 0);
    contratos_verificar("checksum discordante", { datos_json: _paquete.datos_json, hash: "x" }, false, 0);
    contratos_verificar("JSON malformado con checksum correcto", { datos_json: "{", hash: sha1_string_utf8("{") }, false, 0);
    contratos_verificar("JSON válido pero no struct", contratos_paquete([]), false, 0);

    var _campos = ["semilla", "version_simulacion", "frame", "eventos", "puntuacion"];
    for (var _i = 0; _i < array_length(_campos); _i++)
    {
        _replay = contratos_replay_base();
        variable_struct_remove(_replay, _campos[_i]);
        contratos_verificar("replay sin " + _campos[_i], contratos_paquete(_replay), false, 0);
    }
    _replay = contratos_replay_base(); _replay.semilla = 43;
    contratos_verificar("semilla ajena a la sesión", contratos_paquete(_replay), false, 0);
    _replay = contratos_replay_base(); _replay.version_simulacion = "otra";
    contratos_verificar("versión ajena a la sesión", contratos_paquete(_replay), false, 0);
    _replay = contratos_replay_base(); _replay.puntuacion = "9";
    contratos_verificar("puntuación no numérica", contratos_paquete(_replay), false, 0);
    _replay = contratos_replay_base(); _replay.eventos = {};
    contratos_verificar("eventos no array", contratos_paquete(_replay), false, 0);
    var _frames = [-1, 1.5, "2"];
    for (var _i = 0; _i < array_length(_frames); _i++)
    {
        _replay = contratos_replay_base(); _replay.frame = _frames[_i];
        contratos_verificar("duración inválida " + string(_i), contratos_paquete(_replay), false, 0);
    }

    var _eventos_invalidos = [false, {}, { frame: 0 }, { accion: "A" },
        { frame: "0", accion: "A" }, { frame: 0, accion: 1 },
        { frame: -1, accion: "A" }, { frame: 0.5, accion: "A" }, { frame: 2, accion: "A" }];
    for (var _i = 0; _i < array_length(_eventos_invalidos); _i++)
    {
        _replay = contratos_replay_base(); _replay.eventos = [_eventos_invalidos[_i]];
        contratos_verificar("evento inválido " + string(_i), contratos_paquete(_replay), false, 0);
    }
    _replay = contratos_replay_base(); _replay.eventos = [{ frame: 1, accion: "A" }, { frame: 0, accion: "B" }];
    contratos_verificar("eventos fuera de orden", contratos_paquete(_replay), false, 0);

    _replay = contratos_replay_base(); _replay.puntuacion = 10;
    contratos_verificar("checksum recalculado no valida puntuación falsa", contratos_paquete(_replay), false, 2, 2, "AB");
    _replay = contratos_replay_base(); _replay.eventos[0].accion = "B"; _replay.puntuacion = 12;
    contratos_verificar("checksum público admite otro replay consistente", contratos_paquete(_replay), true, 2, 2, "BB");
    var _json_reordenado = "{\"puntuacion\":9,\"eventos\":[{\"accion\":\"A\",\"frame\":0},{\"accion\":\"B\",\"frame\":1}],\"frame\":2,\"version_simulacion\":\"r47\",\"semilla\":42}";
    contratos_verificar("bytes JSON transportados con otro orden de propiedades",
        { datos_json: _json_reordenado, hash: sha1_string_utf8(_json_reordenado) }, true, 2, 2, "AB");
}

// Construye entradas de prueba del formato publicado; el parser bajo prueba se extrae
// íntegro. Estos buffers son del fixture y se borran aquí, no buffers de Async Networking.
function contratos_snapshot_buffer(_tick, _registros, _ack)
{
    var _b = buffer_create(64, buffer_grow, 1);
    buffer_write(_b, buffer_u32, _tick);
    buffer_write(_b, buffer_u16, array_length(_registros));
    for (var _i = 0; _i < array_length(_registros); _i++)
    {
        var _r = _registros[_i];
        buffer_write(_b, buffer_u32, _r.net_id);
        buffer_write(_b, buffer_u32, _r.propietario);
        buffer_write(_b, buffer_u8, 1);
        buffer_write(_b, buffer_s16, _r.x);
        buffer_write(_b, buffer_s16, _r.y);
        buffer_write(_b, buffer_s16, 125);
        buffer_write(_b, buffer_s16, -250);
        buffer_write(_b, buffer_u8, 90);
        buffer_write(_b, buffer_u8, _r.equipo);
    }
    buffer_write(_b, buffer_u32, _ack);
    return { buffer: _b, limite: buffer_tell(_b) };
}

function contratos_snapshot_leer(_nombre, _paquete, _esperado)
{
    var _nm = objNetManager;
    var _anterior = _nm.snapshot_reciente;
    var _ack = _nm.ultima_sec_confirmada;
    var _historial = array_length(_nm.historial_prediccion);
    var _entidades = array_length(variable_struct_get_names(_nm.entidades));
    buffer_seek(_paquete.buffer, buffer_seek_start, 0);
    var _resultado = undefined;
    var _excepcion = "";
    try { _resultado = recibir_snapshot(_paquete.buffer, _paquete.limite); }
    catch (_error) { _excepcion = string(_error); }
    contratos_comprobar(_nombre, _excepcion == "" && _resultado == _esperado, _excepcion);
    if (!_esperado)
        contratos_comprobar(_nombre + " conserva estado",
            _nm.snapshot_reciente == _anterior && _nm.ultima_sec_confirmada == _ack
            && array_length(_nm.historial_prediccion) == _historial
            && array_length(variable_struct_get_names(_nm.entidades)) == _entidades);
    buffer_delete(_paquete.buffer);
}

function contratos_callback_pendiente(_cliente, _intencion)
{
    global.contratos_callback_ids += string(_cliente) + ":" + string(_intencion.sec) + ";";
    return false;
}

function contratos_callback_aplicado(_cliente, _intencion)
{
    global.contratos_callback_ids += string(_cliente) + ":" + string(_intencion.sec) + ";";
    return true;
}

function contratos_probar_snapshot()
{
    var _nm = instance_create_depth(0, 0, 0, objNetManager);
    _nm.mi_id = 42;
    _nm.secuencia_input = 4;
    _nm.historial_prediccion = [{ sec: 1 }, { sec: 2 }, { sec: 3 }, { sec: 4 }];
    var _propia = instance_create_depth(0, 0, 0, objNetEntity);
    var _remota = instance_create_depth(0, 0, 0, objNetEntity);
    _nm.entidades[$ "10"] = _propia;
    _nm.entidades[$ "11"] = _remota;
    var _registros = [{ net_id: 10, propietario: 42, x: 20, y: 0, equipo: 7 },
                      { net_id: 11, propietario: 43, x: 40, y: 0, equipo: 7 }];
    var _paquete = contratos_snapshot_buffer(1, _registros, 2);
    contratos_comprobar("snapshot dos registros: 6 + 2*19 + 4 bytes", _paquete.limite == 48);
    contratos_snapshot_leer("snapshot válido", _paquete, true);
    contratos_comprobar("ACK retira solo historial confirmado",
        _nm.ultima_sec_confirmada == 2 && array_length(_nm.historial_prediccion) == 2
        && _nm.historial_prediccion[0].sec == 3 && _nm.historial_prediccion[1].sec == 4);
    contratos_comprobar("propietario local usa reconciliación, no equipo",
        _propia.propietario == 42 && _propia.equipo == 7 && _propia.x_servidor == 20
        && _propia.x == 5 && _propia.x_objetivo == 0);
    contratos_comprobar("mismo equipo y distinto propietario usa destino remoto",
        _remota.propietario == 43 && _remota.equipo == 7 && _remota.x == 0
        && _remota.x_objetivo == 40 && _remota.x_servidor == 0);
    contratos_comprobar("velocidades escaladas y vida", _remota.vel_x == 1.25 && _remota.vel_y == -2.5 && _remota.hp == 90);
    contratos_comprobar("primer snapshot inicializa anterior", _nm.snapshot_anterior == _nm.snapshot_reciente);

    contratos_snapshot_leer("tick repetido", contratos_snapshot_buffer(1, [], 2), false);
    contratos_snapshot_leer("tick anterior", contratos_snapshot_buffer(0, [], 2), false);
    contratos_snapshot_leer("ACK mayor que input enviado", contratos_snapshot_buffer(2, [], 5), false);
    contratos_snapshot_leer("ACK regresivo", contratos_snapshot_buffer(2, [], 1), false);
    _paquete = contratos_snapshot_buffer(2, _registros, 3);
    _paquete.limite = 5;
    contratos_snapshot_leer("cabecera truncada", _paquete, false);
    _paquete = contratos_snapshot_buffer(2, _registros, 3);
    _paquete.limite--;
    contratos_snapshot_leer("ACK truncado", _paquete, false);
    _paquete = contratos_snapshot_buffer(2, _registros, 3);
    _paquete.limite = 25;
    contratos_snapshot_leer("contador superior a registros presentes", _paquete, false);
    // El paquete está completo: solo el límite, nunca truncamiento, lo rechaza.
    _paquete = contratos_snapshot_buffer(2, array_create(NET_MAX_ENTIDADES + 1, _registros[1]), 3);
    contratos_snapshot_leer("contador sobre máximo de entidades", _paquete, false);

    contratos_snapshot_leer("snapshot vacío válido confirma el resto", contratos_snapshot_buffer(2, [], 4), true);
    contratos_comprobar("ACK vacía historial pendiente y rota snapshot",
        _nm.ultima_sec_confirmada == 4 && array_length(_nm.historial_prediccion) == 0
        && _nm.snapshot_anterior.tick == 1 && _nm.snapshot_reciente.tick == 2);

    _nm.clientes = {
        primer_socket: { id: 42, ultimo_input_aplicado: 2, intencion: { sec: 3 } },
        segundo_socket: { id: 43, ultimo_input_aplicado: 5, intencion: { sec: 6 } },
        sin_input: { id: 44, ultimo_input_aplicado: 0, intencion: undefined }
    };
    servidor_consumir_inputs(undefined);
    contratos_comprobar("sin callback no confirma input", _nm.clientes.primer_socket.ultimo_input_aplicado == 2);
    global.contratos_callback_ids = "";
    servidor_consumir_inputs(contratos_callback_pendiente);
    contratos_comprobar("callback pendiente conserva ACK individuales",
        _nm.clientes.primer_socket.ultimo_input_aplicado == 2 && _nm.clientes.segundo_socket.ultimo_input_aplicado == 5);
    global.contratos_callback_ids = "";
    servidor_consumir_inputs(contratos_callback_aplicado);
    contratos_comprobar("callback aplicado confirma secuencia por destinatario",
        _nm.clientes.primer_socket.ultimo_input_aplicado == 3 && _nm.clientes.segundo_socket.ultimo_input_aplicado == 6);
    contratos_comprobar("callback recibe identidad asignada; omite cliente sin input",
        string_pos("42:3;", global.contratos_callback_ids) > 0
        && string_pos("43:6;", global.contratos_callback_ids) > 0
        && string_pos("44:", global.contratos_callback_ids) == 0);
    instance_destroy(_propia);
    instance_destroy(_remota);
    instance_destroy(_nm);
}

function banco_contratos_r47()
{
    global.contratos_ok = 0;
    global.contratos_ko = 0;
    contratos_probar_plural();
    contratos_probar_replay();
    contratos_probar_snapshot();
    show_debug_message("CONTRATOS_R47: " + string(global.contratos_ok) + " correctas, " + string(global.contratos_ko) + " fallidas");
}
