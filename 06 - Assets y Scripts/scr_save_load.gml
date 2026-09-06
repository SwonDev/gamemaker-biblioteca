// ============================================================================
// scr_save_load.gml
// Guardado y carga de partidas con structs + JSON, escritura segura y
// control de versión de esquema.
//
// TRES REGLAS QUE ESTE SCRIPT RESPETA
//   1. ESCRITURA SEGURA: nunca se escribe directamente sobre la partida
//      buena. Se escribe en un temporal, se válida y solo entonces se
//      reemplaza. Si el juego se cierra a medias, la partida sigue intacta.
//   2. NADA DE DATOS BASURA: `json_stringify` guarda los assets por NOMBRE,
//      no por contenido. Si renombras un sprite, una partida vieja puede
//      romper. Por eso hay versión de esquema y validación.
//   3. CARPETA CORRECTA: se usa `game_save_id`, que es la carpeta de guardado
//      válida en TODAS las plataformas. NO uses `working_directory`.
//
// Funciones nativas usadas (verificadas con gm-cli manual read):
//   json_stringify, json_parse, file_text_open_write, file_text_open_read,
//   file_text_write_string, file_text_read_string, file_text_readln,
//   file_text_eof, file_text_close, file_exists, file_delete, file_rename,
//   directory_exists, directory_create, is_struct, struct_exists,
//   date_current_datetime, date_datetime_string, game_save_id
//
// Dependencias: ninguna.
//
// USO RAPIDO
//   // Guardar
//   var _datos = {
//       nivel      : room_get_name(room),
//       vida       : obj_player.hp,
//       inventario : obj_player.inventario,   // array de structs: funciona
//       pos        : { x: obj_player.x, y: obj_player.y }
//   };
//   if (!save_game("slot1", _datos)) {
//       show_debug_message("No se pudo guardar.");
//   }
//
//   // Comprobar y cargar
//   if (save_exists("slot1")) {
//       var _d = load_game("slot1");
//       if (is_struct(_d)) {
//           obj_player.hp = _d.vida;
//       }
//   }
//
//   // Borrar
//   delete_save("slot1");
// ============================================================================

#macro SAVE_VERSION 1          // Subelo cada vez que cambies la forma de los datos
#macro SAVE_EXTENSION ".json"
#macro SAVE_TEMP_SUFFIX ".tmp"


/// @function save_get_path(_slot)
/// @desc    Ruta completa del fichero de un slot.
/// @param   {String} _slot  Nombre del slot ("slot1", "auto", ...).
/// @returns {String}        Ruta absoluta dentro de `game_save_id`.
function save_get_path(_slot) {
    return game_save_id + "save_" + string(_slot) + SAVE_EXTENSION;
}


/// @function __save_get_temp_path(_slot)
/// @desc    Ruta del fichero temporal de un slot. Uso interno.
/// @param   {String} _slot
/// @returns {String}
function __save_get_temp_path(_slot) {
    return game_save_id + "save_" + string(_slot) + SAVE_TEMP_SUFFIX;
}


/// @function save_ensure_dir()
/// @desc    Crea la carpeta de guardado si no existe. `game_save_id` suele
///          existir ya, pero en algunos targets puede no estar creada.
/// @returns {Bool}  True si la carpeta existe o se pudo crear.
function save_ensure_dir() {
    if (directory_exists(game_save_id)) { return true; }
    return directory_create(game_save_id);
}


/// @function save_exists(_slot)
/// @desc    Comprueba si hay una partida guardada en ese slot.
/// @param   {String} _slot
/// @returns {Bool}
function save_exists(_slot) {
    return file_exists(save_get_path(_slot));
}


/// @function save_game(_slot, _datos)
/// @desc    Guarda un struct (o un array) como partida. Escritura segura.
/// @param   {String}        _slot   Nombre del slot.
/// @param   {Struct|Array}  _datos  Tus datos. Deben ser serializables a JSON.
/// @returns {Bool}                  True si se guardo correctamente.
function save_game(_slot, _datos) {
    if (!is_struct(_datos) && !is_array(_datos)) {
        show_debug_message("save_game: los datos deben ser un struct o un array.");
        return false;
    }

    if (!save_ensure_dir()) {
        show_debug_message("save_game: no se pudo crear la carpeta de guardado.");
        return false;
    }

    // Envolvemos los datos con metadatos. La versión es lo que nos permitirá
    // migrar partidas viejas cuando cambiemos la estructura.
    var _sobre = {
        version  : SAVE_VERSION,
        fecha    : date_datetime_string(date_current_datetime()),
        datos    : _datos
    };

    var _ruta_final = save_get_path(_slot);
    var _ruta_temp  = __save_get_temp_path(_slot);

    // --- PASO 1: escribir en el temporal ------------------------------------
    var _f = file_text_open_write(_ruta_temp);
    if (_f == -1) {
        show_debug_message("save_game: no se pudo abrir " + _ruta_temp);
        return false;
    }

    // Sin prettify: una sola línea, más rapida de escribir y de leer.
    file_text_write_string(_f, json_stringify(_sobre));
    file_text_close(_f);

    // --- PASO 2: validar lo escrito -----------------------------------------
    // Leemos el temporal y lo parseamos. Si algo fue mal (disco lleno, corte
    // de luz), aquí lo detectamos ANTES de tocar la partida buena.
    var _leido = __save_read_raw(_ruta_temp);
    if (!is_struct(_leido) || !struct_exists(_leido, "version") || !struct_exists(_leido, "datos")) {
        show_debug_message("save_game: el temporal no es válido. Se descarta.");
        if (file_exists(_ruta_temp)) { file_delete(_ruta_temp); }
        return false;
    }

    // --- PASO 3: reemplazar -------------------------------------------------
    // Borramos el destino y renombramos el temporal. `file_rename` sobre un
    // fichero existente falla en algunos targets, de ahi el delete previo.
    if (file_exists(_ruta_final)) { file_delete(_ruta_final); }

    if (!file_rename(_ruta_temp, _ruta_final)) {
        show_debug_message("save_game: fallo el reemplazo final.");
        return false;
    }

    return true;
}


/// @function __save_read_raw(_ruta)
/// @desc    Lee un fichero de texto completo y lo parsea como JSON.
///          Devuelve `undefined` si algo falla. Uso interno.
/// @param   {String} _ruta  Ruta del fichero.
/// @returns {Struct|Array|Undefined}
function __save_read_raw(_ruta) {
    if (!file_exists(_ruta)) { return undefined; }

    var _f = file_text_open_read(_ruta);
    if (_f == -1) { return undefined; }

    var _contenido = "";
    while (!file_text_eof(_f)) {
        _contenido += file_text_read_string(_f);
        file_text_readln(_f);
    }
    file_text_close(_f);

    if (_contenido == "") { return undefined; }

    // json_parse puede lanzar un error fatal si el JSON está corrupto.
    // Por eso comprobamos antes y envolvemos el parseo.
    var _parseado = undefined;
    try {
        _parseado = json_parse(_contenido);
    } catch (_e) {
        show_debug_message("__save_read_raw: JSON corrupto en " + _ruta);
        return undefined;
    }

    return _parseado;
}


/// @function load_game_raw(_slot)
/// @desc    Carga el sobre completo (versión + fecha + datos).
/// @param   {String} _slot
/// @returns {Struct|Undefined}  El sobre, o `undefined` si no hay nada válido.
function load_game_raw(_slot) {
    var _sobre = __save_read_raw(save_get_path(_slot));

    if (!is_struct(_sobre)) { return undefined; }
    if (!struct_exists(_sobre, "version")) { return undefined; }
    if (!struct_exists(_sobre, "datos")) { return undefined; }

    return _sobre;
}


/// @function load_game(_slot)
/// @desc    Carga solo los datos de la partida, aplicando la migración de
///          versión si hiciera falta. Es la función que usarás el 95 % de las
///          veces.
/// @param   {String} _slot
/// @returns {Struct|Array|Undefined}  Tus datos, o `undefined` si fallo.
function load_game(_slot) {
    var _sobre = load_game_raw(_slot);
    if (!is_struct(_sobre)) { return undefined; }

    var _datos = _sobre.datos;
    var _version_guardada = _sobre.version;

    // --- Migracion de esquema -----------------------------------------------
    // Si la versión guardada es más antigua que la actual, intentamos migrar.
    // Define `global.save_migrar` en tu juego con una función:
    //   global.save_migrar = function(_datos, _version_vieja) { ... return _datos; }
    if (_version_guardada < SAVE_VERSION) {
        show_debug_message("load_game: partida v" + string(_version_guardada) +
                           " -> migrando a v" + string(SAVE_VERSION));

        if (variable_global_exists("save_migrar") && is_method(global.save_migrar)) {
            _datos = global.save_migrar(_datos, _version_guardada);
        } else {
            show_debug_message("load_game: no hay función de migración definida. " +
                               "Se cargaran los datos sin convertir.");
        }
    } else if (_version_guardada > SAVE_VERSION) {
        // La partida es de una versión MAS NUEVA del juego. Cargarla puede
        // romper cosas: avisamos y seguimos, pero es una situacion a vigilar.
        show_debug_message("AVISO: la partida es de una versión posterior (v" +
                           string(_version_guardada) + "). Puede fallar.");
    }

    return _datos;
}


/// @function load_game_safe(_slot, _validador)
/// @desc    Carga la partida y la pasa por un validador antes de devolverla.
///          Si el validador dice que no, devuelve `undefined` SIN borrar el
///          fichero (así puedes decidir que hacer).
/// @param   {String}   _slot       Nombre del slot.
/// @param   {Function} _validador  Función que recibe los datos y devuelve Bool.
/// @returns {Struct|Array|Undefined}
function load_game_safe(_slot, _validador) {
    var _datos = load_game(_slot);

    if (is_undefined(_datos)) { return undefined; }

    if (is_method(_validador)) {
        if (!_validador(_datos)) {
            show_debug_message("load_game_safe: la partida no paso la validacion.");
            return undefined;
        }
    }

    return _datos;
}


/// @function save_get_meta(_slot)
/// @desc    Devuelve solo los metadatos (versión y fecha) sin cargar los datos.
///          Ideal para pintar la pantalla de "elige partida".
/// @param   {String} _slot
/// @returns {Struct|Undefined}  { versión, fecha } o `undefined`.
function save_get_meta(_slot) {
    var _sobre = load_game_raw(_slot);
    if (!is_struct(_sobre)) { return undefined; }

    return {
        version : _sobre.version,
        fecha   : struct_exists(_sobre, "fecha") ? _sobre.fecha : "desconocida"
    };
}


/// @function delete_save(_slot)
/// @desc    Borra una partida. También limpia los temporales huérfanos que
///          haya podido dejar un intento de guardado fallido.
/// @param   {String} _slot
/// @returns {Bool}  True si se borro algo.
function delete_save(_slot) {
    var _borrado = false;

    if (file_exists(save_get_path(_slot))) {
        file_delete(save_get_path(_slot));
        _borrado = true;
    }

    // Limpieza de temporales: si un guardado anterior se interrumpio, aquí
    // queda un .tmp ocupando espacio y confundiendo al siguiente guardado.
    var _temp = __save_get_temp_path(_slot);
    if (file_exists(_temp)) { file_delete(_temp); }

    return _borrado;
}


/// @function save_list(_slots)
/// @desc    Devuelve la información de varios slots de una vez, para pintar un
///          menu de seleccion de partida.
/// @param   {Array<String>} _slots  Nombres de slot a consultar.
/// @returns {Array<Struct>}         Array de { slot, existe, versión, fecha }.
function save_list(_slots) {
    var _resultado = [];

    if (!is_array(_slots)) { return _resultado; }

    var _i;
    for (_i = 0; _i < array_length(_slots); _i++) {
        var _slot = _slots[_i];
        var _meta = save_get_meta(_slot);

        array_push(_resultado, {
            slot    : _slot,
            existe  : save_exists(_slot),
            version : is_struct(_meta) ? _meta.version : -1,
            fecha   : is_struct(_meta) ? _meta.fecha   : ""
        });
    }

    return _resultado;
}


/// @function save_export_string(_datos)
/// @desc    Serializa unos datos a texto JSON. Util para depurar, para copiar
///          y pegar una partida, o para enviarla por red.
/// @param   {Struct|Array} _datos
/// @returns {String}
function save_export_string(_datos) {
    var _sobre = {
        version : SAVE_VERSION,
        fecha   : date_datetime_string(date_current_datetime()),
        datos   : _datos
    };
    return json_stringify(_sobre);
}


/// @function save_import_string(_texto)
/// @desc    Importa una partida desde texto JSON (lo contrario de la anterior).
/// @param   {String} _texto  Texto generado por `save_export_string()`.
/// @returns {Struct|Array|Undefined}
function save_import_string(_texto) {
    if (!is_string(_texto) || _texto == "") { return undefined; }

    var _sobre = undefined;
    try {
        _sobre = json_parse(_texto);
    } catch (_e) {
        show_debug_message("save_import_string: JSON invalido.");
        return undefined;
    }

    if (!is_struct(_sobre) || !struct_exists(_sobre, "datos")) { return undefined; }

    return _sobre.datos;
}
