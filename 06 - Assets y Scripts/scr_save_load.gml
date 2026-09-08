// ============================================================================
// scr_save_load.gml
// Guardado y carga de partidas con structs + JSON, escritura segura y
// control de versión de esquema.
//
// CINCO REGLAS QUE ESTE SCRIPT RESPETA
//   1. ESCRITURA SEGURA: nunca se escribe directamente sobre la partida
//      buena. Se escribe en un temporal, se válida y solo entonces se
//      reemplaza. Si el juego se cierra a medias, la partida sigue intacta.
//   2. NADA DE DATOS BASURA: `json_stringify` guarda los assets por NOMBRE,
//      no por contenido. Si renombras un sprite, una partida vieja puede
//      romper. Por eso hay versión de esquema y validación.
//   3. CARPETA CORRECTA: se usa `game_save_id`, que es la carpeta de guardado
//      válida en TODAS las plataformas. NO uses `working_directory`.
//   4. INTEGRIDAD REAL: el guardado lleva un checksum que se COMPRUEBA al
//      cargar, no solo se calcula (ver 01 · 14 §12 bis). Un fichero
//      corrompido o editado a mano de forma que rompa los datos se
//      RECHAZA, en vez de devolver una partida a medias.
//   5. RED DE SEGURIDAD: cada guardado nuevo empuja el anterior a una
//      cadena de copias rotativas (`SAVE_BACKUP_COUNT`). Si el save
//      principal no pasa la validación, `load_game_recover()` prueba las
//      copias antes de rendirse.
//
// Funciones nativas usadas (verificadas con gm-cli manual read):
//   json_stringify, json_parse, file_text_open_write, file_text_open_read,
//   file_text_write_string, file_text_read_string, file_text_readln,
//   file_text_eof, file_text_close, file_exists, file_delete, file_rename,
//   directory_exists, directory_create, is_struct, is_string, struct_exists,
//   date_current_datetime, date_datetime_string, sha1_string_utf8, is_method,
//   variable_global_exists, game_save_id, screen_save_part, sprite_add,
//   sprite_exists, sprite_delete
//
// Dependencias: ninguna obligatoria. Opcional: si tu juego define
//   global.save_logger = function(_nivel, _texto) { registrar(_nivel, _texto); }
// (con `registrar()` de 13 · 10 §7.2, el log con niveles que sobrevive al
// cierre), los fallos de guardado/carga quedan también en `partida.log`, no
// solo en la consola de desarrollo. Sin ese hook, este script se comporta
// exactamente como antes: solo `show_debug_message()`.
//
// METADATOS DE RANURA (§ "UX de ranura de guardado" — hueco B4b de
// _indice/auditorias/r5-juego-completo.md, cerrado aquí). `save_game()` acepta
// un tercer argumento OPCIONAL, `_meta`: un struct plano (zona, tiempo jugado,
// porcentaje... lo que tu juego quiera mostrar en la pantalla de "elige
// partida") que viaja en el propio sobre, al lado de `version`/`fecha`, y que
// `save_get_meta()`/`save_list()` devuelven SIN cargar `datos` completo. La
// miniatura es aparte, como archivo PNG: `save_thumbnail_capture()` la toma
// con `screen_save_part()` en el momento de guardar, y `save_thumbnail_load()`
// la recupera como sprite para la ficha de la ranura — ver 13 · 05, componente
// n) Ranura de guardado (metadatos, miniatura y "guardando…").
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
//   // Cargar con red de seguridad: si "slot1" no pasa la validación,
//   // intenta las copias de seguridad antes de rendirse.
//   var _d = load_game_recover("slot1");
//
//   // Borrar
//   delete_save("slot1");
// ============================================================================

#macro SAVE_VERSION 1          // Subelo cada vez que cambies la forma de los datos
#macro SAVE_EXTENSION ".json"
#macro SAVE_TEMP_SUFFIX ".tmp"
#macro SAVE_BACKUP_COUNT 3     // copias de seguridad rotativas a conservar por slot. 0 = desactivado.
#macro SAVE_LOG_NIVEL_ERROR 3  // = NIVEL.ERROR si usas el enum de 13 · 10 §7.2 tal cual


/// @function __save_log(_nivel, _texto)
/// @desc    Registra un mensaje de este script. Siempre va a Output; si el juego
///          define `global.save_logger` (ver cabecera), también se le reenvía
///          para que quede en un log persistente. Uso interno.
/// @param   {Real}   _nivel  Nivel del mensaje. Usa SAVE_LOG_NIVEL_ERROR para fallos.
/// @param   {String} _texto
function __save_log(_nivel, _texto) {
    show_debug_message(_texto);

    if (variable_global_exists("save_logger") && is_method(global.save_logger)) {
        global.save_logger(_nivel, _texto);
    }
}


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


/// @function save_backup_path(_slot, _n)
/// @desc    Ruta de la copia de seguridad número `_n` de un slot (1 = la más
///          reciente, `SAVE_BACKUP_COUNT` = la más vieja que se conserva).
/// @param   {String} _slot
/// @param   {Real}   _n
/// @returns {String}
function save_backup_path(_slot, _n) {
    return game_save_id + "save_" + string(_slot) + ".bak" + string(_n) + SAVE_EXTENSION;
}


/// @function save_ensure_dir()
/// @desc    Crea la carpeta de guardado si no existe. `game_save_id` suele
///          existir ya, pero en algunos targets puede no estar creada.
///
///          ⚠️ NO SE FÍA del resultado de `directory_exists()`/`directory_create()`:
///          bajo `gm-cli run --target mac` (runtime GMS2 2026.0.0.23), ambas
///          funciones pueden devolver `false` SIEMPRE, incluso sobre una
///          carpeta que ya existe y tiene archivos dentro — mientras que
///          escribir un fichero ahí con `file_text_open_write()` funciona sin
///          ningún problema. Confiar en la rama `if` de arriba bloqueaba
///          `save_game()` para siempre, en silencio, sin ningún error visible
///          salvo una línea de log que hay que estar mirando a propósito.
///          Verificado en vivo construyendo un juego completo de punta a
///          punta: `_indice/auditorias/r5-prueba-e2e.md` §2, documentado como
///          Trampa 6 en
///          `12 - Utilidades e integraciones/09 - Manual del agente de IA...md`
///          y en `01 · 14` §11. La corrección: en vez de devolver lo que digan
///          esas dos funciones, se intenta escribir un fichero centinela de
///          verdad — si la escritura funciona, la carpeta es utilizable, sin
///          importar lo que hayan dicho `directory_exists()`/`directory_create()`.
/// @returns {Bool}  True si la carpeta existe o se pudo crear (o ya es
///                   utilizable aunque el sistema diga lo contrario).
function save_ensure_dir() {
    // Si el sistema SÍ confirma que existe, no hace falta nada más.
    if (directory_exists(game_save_id)) { return true; }

    // El sistema dice que no existe: puede ser cierto, o puede ser el bug de
    // arriba. Intentamos crearla de todas formas (no cuesta nada si ya existe)...
    directory_create(game_save_id);

    // ...y comprobamos con una ESCRITURA REAL, no con otra llamada a
    // directory_exists()/directory_create(): ambas pueden seguir devolviendo
    // false aunque la carpeta ya sea perfectamente utilizable.
    var _centinela = game_save_id + "__save_ensure_dir.tmp";
    var _f = file_text_open_write(_centinela);
    if (_f == -1) { return false; }   // esto sí es un fallo real: no se puede escribir ahí

    file_text_close(_f);
    file_delete(_centinela);
    return true;
}


/// @function save_exists(_slot)
/// @desc    Comprueba si hay una partida guardada en ese slot.
/// @param   {String} _slot
/// @returns {Bool}
function save_exists(_slot) {
    return file_exists(save_get_path(_slot));
}


/// @function save_backup(_slot, _n)
/// @desc    Rota `_n` copias de seguridad del slot ANTES de que se sobrescriba:
///          bak(_n-1) -> bak(_n), ..., bak1 -> bak2, y el save actual (si existe)
///          pasa a ser bak1. `save_game()` la llama sola en cada guardado; solo
///          hace falta llamarla a mano si quieres forzar una copia fuera de ese
///          flujo. Con `_n <= 0` no hace nada (backups desactivados).
/// @param   {String} _slot
/// @param   {Real}   _n     Cuántas copias conservar (normalmente SAVE_BACKUP_COUNT).
/// @returns {Bool}          True siempre que no haga falta nada más (incluida la
///                          rotación desactivada).
function save_backup(_slot, _n) {
    if (_n <= 0) { return true; }

    // De la más vieja a la más nueva, para no pisar una copia antes de moverla.
    var _i = _n;
    repeat (_n - 1) {
        var _origen  = save_backup_path(_slot, _i - 1);
        var _destino = save_backup_path(_slot, _i);
        if (file_exists(_origen)) {
            if (file_exists(_destino)) { file_delete(_destino); }
            file_rename(_origen, _destino);
        }
        _i--;
    }

    // El save que había hasta ahora (si lo había) pasa a ser la copia más reciente.
    var _actual = save_get_path(_slot);
    if (file_exists(_actual)) {
        var _bak1 = save_backup_path(_slot, 1);
        if (file_exists(_bak1)) { file_delete(_bak1); }
        file_rename(_actual, _bak1);
    }

    return true;
}


/// @function __save_envelope_checksum_ok(_sobre)
/// @desc    Comprueba la integridad de un sobre ya parseado, SIN reserializar
///          `datos`. Uso interno.
///
///          Por qué no se reserializa: `json_stringify` no garantiza el orden
///          de las claves de un struct (01 · 14 §8), así que comparar el hash
///          de un struct vuelto a convertir a texto podría rechazar un
///          guardado perfectamente válido solo porque las claves salieron en
///          otro orden. Por eso, desde que existe el checksum, `datos` se
///          guarda como el TEXTO JSON exacto que se hasheó al escribir (un
///          string sobrevive el parseo byte a byte, a diferencia de un
///          struct) — ver `save_game()` más abajo y 01 · 14 §12 bis.
///
///          Un guardado del formato anterior (sin checksum, `datos` ya como
///          struct/array) se acepta tal cual: no hay nada que comprobar.
/// @param   {Struct} _sobre  El sobre ya parseado (con `.datos` sin desenvolver).
/// @returns {Bool}
function __save_envelope_checksum_ok(_sobre) {
    if (!is_struct(_sobre) || !struct_exists(_sobre, "datos")) { return false; }
    if (!is_string(_sobre.datos)) { return true; }                   // formato antiguo
    if (!struct_exists(_sobre, "checksum")) { return true; }         // nada que comprobar

    return (sha1_string_utf8(_sobre.datos) == _sobre.checksum);
}


/// @function save_game(_slot, _datos, _meta)
/// @desc    Guarda un struct (o un array) como partida. Escritura segura, con
///          checksum de integridad y copia de seguridad rotativa del save
///          anterior antes de reemplazarlo.
/// @param   {String}        _slot   Nombre del slot.
/// @param   {Struct|Array}  _datos  Tus datos. Deben ser serializables a JSON.
/// @param   {Struct}        _meta   OPCIONAL. Metadatos ligeros para pintar la
///                                  ficha de la ranura sin cargar `_datos`
///                                  entero: zona, tiempo jugado, porcentaje...
///                                  lo que tu juego quiera mostrar. Se guarda
///                                  tal cual, sin forma fija.
/// @returns {Bool}                  True si se guardo correctamente.
function save_game(_slot, _datos, _meta = undefined) {
    if (!is_struct(_datos) && !is_array(_datos)) {
        __save_log(SAVE_LOG_NIVEL_ERROR, "save_game: los datos deben ser un struct o un array.");
        return false;
    }

    if (!save_ensure_dir()) {
        __save_log(SAVE_LOG_NIVEL_ERROR, "save_game: no se pudo crear la carpeta de guardado.");
        return false;
    }

    // Envolvemos los datos con metadatos. La versión es lo que nos permitirá
    // migrar partidas viejas cuando cambiemos la estructura. `datos` se guarda
    // como TEXTO JSON (no como struct anidado) para que el checksum se pueda
    // comprobar sin reserializar nada — ver __save_envelope_checksum_ok().
    var _datos_json = json_stringify(_datos);
    var _sobre = {
        version  : SAVE_VERSION,
        fecha    : date_datetime_string(date_current_datetime()),
        checksum : sha1_string_utf8(_datos_json),
        datos    : _datos_json
    };
    // `meta` viaja SIN envolver (no es texto JSON como `datos`): es pequeño y
    // no necesita checksum propio — si el sobre entero pasa el checksum de
    // `datos`, `meta` llegó en el mismo archivo íntegro.
    if (is_struct(_meta)) { _sobre.meta = _meta; }

    var _ruta_final = save_get_path(_slot);
    var _ruta_temp  = __save_get_temp_path(_slot);

    // --- PASO 1: escribir en el temporal ------------------------------------
    var _f = file_text_open_write(_ruta_temp);
    if (_f == -1) {
        __save_log(SAVE_LOG_NIVEL_ERROR, "save_game: no se pudo abrir " + _ruta_temp);
        return false;
    }

    // Sin prettify: una sola línea, más rapida de escribir y de leer.
    file_text_write_string(_f, json_stringify(_sobre));
    file_text_close(_f);

    // --- PASO 2: validar lo escrito -----------------------------------------
    // Leemos el temporal y lo parseamos. Si algo fue mal (disco lleno, corte
    // de luz), aquí lo detectamos ANTES de tocar la partida buena. Además de
    // la forma (version/datos), comprobamos que el checksum recién escrito
    // coincide: si el disco corrompió algo al escribir, se descubre aquí y
    // no al cargar la partida días después.
    var _leido = __save_read_raw(_ruta_temp);
    if (!is_struct(_leido) || !struct_exists(_leido, "version") || !struct_exists(_leido, "datos")) {
        __save_log(SAVE_LOG_NIVEL_ERROR, "save_game: el temporal no es válido. Se descarta.");
        if (file_exists(_ruta_temp)) { file_delete(_ruta_temp); }
        return false;
    }
    if (!__save_envelope_checksum_ok(_leido)) {
        __save_log(SAVE_LOG_NIVEL_ERROR, "save_game: el checksum del temporal no coincide. Se descarta.");
        if (file_exists(_ruta_temp)) { file_delete(_ruta_temp); }
        return false;
    }

    // --- PASO 3: copia de seguridad y reemplazo ------------------------------
    // El save que había hasta ahora (si lo había) pasa a ser la copia de
    // seguridad más reciente ANTES de escribir la nueva partida encima. Si
    // el juego se apaga justo aquí: el `.tmp` de este guardado sigue en
    // disco (recuperable a mano) y el save anterior sigue accesible como
    // bak1 aunque el archivo principal haya "desaparecido" un instante —
    // `load_game_recover()` lo encuentra igual.
    save_backup(_slot, SAVE_BACKUP_COUNT);

    // Por si los backups están desactivados o algo no se movió: `file_rename`
    // sobre un destino existente falla en algunos targets, de ahí el borrado
    // previo como red de seguridad.
    if (file_exists(_ruta_final)) { file_delete(_ruta_final); }

    if (!file_rename(_ruta_temp, _ruta_final)) {
        __save_log(SAVE_LOG_NIVEL_ERROR, "save_game: fallo el reemplazo final.");
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
        __save_log(SAVE_LOG_NIVEL_ERROR, "__save_read_raw: JSON corrupto en " + _ruta);
        return undefined;
    }

    return _parseado;
}


/// @function __save_load_envelope(_ruta)
/// @desc    Lee, valida y verifica el checksum de un sobre en una ruta dada,
///          y devuelve `datos` ya DESENVUELTO (struct/array usable, no el
///          texto JSON interno). La usan tanto `load_game_raw()` (sobre el
///          save principal) como `load_game_recover()` (sobre cada backup):
///          es el único sitio donde vive la lógica de verificación. Uso interno.
/// @param   {String} _ruta
/// @returns {Struct|Undefined}  El sobre con `.datos` ya desenvuelto, o
///                              `undefined` si no hay nada válido.
function __save_load_envelope(_ruta) {
    var _sobre = __save_read_raw(_ruta);

    if (!is_struct(_sobre))                { return undefined; }
    if (!struct_exists(_sobre, "version")) { return undefined; }
    if (!struct_exists(_sobre, "datos"))   { return undefined; }

    if (!__save_envelope_checksum_ok(_sobre)) {
        __save_log(SAVE_LOG_NIVEL_ERROR, "__save_load_envelope: checksum no coincide en " + _ruta + ", se rechaza.");
        return undefined;
    }

    if (is_string(_sobre.datos)) {
        // Formato con checksum: `datos` es el JSON de los datos reales, tal
        // cual se escribió. Ahora que ya se verificó, se parsea de verdad.
        try {
            _sobre.datos = json_parse(_sobre.datos);
        } catch (_e) {
            __save_log(SAVE_LOG_NIVEL_ERROR, "__save_load_envelope: el JSON interno de datos esta corrupto en " + _ruta);
            return undefined;
        }
    }
    // Si `datos` NO era un string, es un guardado del formato anterior a esta
    // verificación (struct/array directo): se acepta tal cual.

    return _sobre;
}


/// @function load_game_raw(_slot)
/// @desc    Carga el sobre completo (versión + fecha + datos), verificando su
///          checksum si lo trae. `datos` siempre vuelve como struct/array
///          usable: el formato interno de verificación es un detalle de este
///          script, no algo que el resto del juego necesite conocer.
/// @param   {String} _slot
/// @returns {Struct|Undefined}  El sobre, o `undefined` si no hay nada válido
///                              o la integridad no coincide.
function load_game_raw(_slot) {
    return __save_load_envelope(save_get_path(_slot));
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


/// @function load_game_recover(_slot, _validador)
/// @desc    Como `load_game_safe()`, pero si el save principal del slot no
///          existe, no pasa el checksum o no pasa el validador, prueba las
///          copias de seguridad rotativas (la más reciente primero) antes de
///          rendirse. Úsala en la pantalla de "cargar partida" en vez de
///          `load_game()` cuando quieras la red de seguridad completa.
///          ⚠️ No restaura automáticamente el backup como save principal:
///          solo te devuelve los datos utilizables. Si quieres que el
///          siguiente `save_game()` parta de ahí, guárdalo tú explícitamente.
/// @param   {String}   _slot
/// @param   {Function} _validador  Opcional. Igual que en `load_game_safe()`.
/// @returns {Struct|Array|Undefined}
function load_game_recover(_slot, _validador = undefined) {
    var _datos = load_game_safe(_slot, _validador);
    if (!is_undefined(_datos)) { return _datos; }

    __save_log(SAVE_LOG_NIVEL_ERROR,
        "load_game_recover: '" + string(_slot) + "' no es válido, probando copias de seguridad...");

    var _n;
    for (_n = 1; _n <= SAVE_BACKUP_COUNT; _n++) {
        var _ruta_bak = save_backup_path(_slot, _n);
        if (!file_exists(_ruta_bak)) { continue; }

        var _sobre = __save_load_envelope(_ruta_bak);
        if (!is_struct(_sobre)) { continue; }

        var _candidato = _sobre.datos;
        if (is_method(_validador) && !_validador(_candidato)) { continue; }

        __save_log(SAVE_LOG_NIVEL_ERROR, "load_game_recover: recuperado desde " + _ruta_bak);
        return _candidato;
    }

    __save_log(SAVE_LOG_NIVEL_ERROR, "load_game_recover: no se encontró ninguna copia usable para '" + string(_slot) + "'.");
    return undefined;
}


/// @function save_get_meta(_slot)
/// @desc    Devuelve version, fecha y los metadatos opcionales de save_game()
///          (zona, tiempo jugado, porcentaje...) SIN que el resto del juego
///          tenga que leer `datos`. Ideal para pintar la pantalla de "elige
///          partida" — ver 13 · 05, componente n) Ranura de guardado.
/// @param   {String} _slot
/// @returns {Struct|Undefined}  { version, fecha, meta } o `undefined`. `meta`
///                              es `undefined` si el guardado no la trae (por
///                              ejemplo, un guardado hecho antes de adoptar
///                              este campo, o sin `_meta` en `save_game()`).
///
/// ⚠️ DEVUELVE EL SOBRE, NO LOS METADATOS. Lo que guardaste vive UN NIVEL MÁS
///    ABAJO, en `.meta`. Es el fallo silencioso de esta función: leer
///    `_ficha.nivel` compila, pasa validar-proyecto.py, y la pantalla de
///    "elige partida" muestra los mismos valores por defecto en TODAS las
///    ranuras, siempre. Lo sufrió un agente construyendo un juego real
///    (_indice/auditorias/r12-prueba-plataformas.md §1.5).
///
///    var _ficha = save_get_meta("ranura1");
///    if (is_struct(_ficha) && is_struct(_ficha.meta)) {
///        var _m = _ficha.meta;                       // <- AQUI estan tus datos
///        draw_text(x, y,  _m.zona + "  " + string(_m.porcentaje) + "%");
///        draw_text(x, y2, "Guardado: " + _ficha.fecha);   // fecha y version
///    } else {                                             // van en el sobre
///        draw_text(x, y, "Ranura vacia");
///    }
function save_get_meta(_slot) {
    var _sobre = load_game_raw(_slot);
    if (!is_struct(_sobre)) { return undefined; }

    return {
        version : _sobre.version,
        fecha   : struct_exists(_sobre, "fecha") ? _sobre.fecha : "desconocida",
        meta    : struct_exists(_sobre, "meta")  ? _sobre.meta  : undefined
    };
}


/// @function save_thumbnail_path(_slot)
/// @desc    Ruta del archivo PNG de la miniatura de un slot. Uso interno, pero
///          pública por si necesitas comprobarla tú mismo con `file_exists()`.
/// @param   {String} _slot
/// @returns {String}
function save_thumbnail_path(_slot) {
    return game_save_id + string(_slot) + "_miniatura.png";
}


/// @function save_thumbnail_capture(_slot, _x, _y, _w, _h)
/// @desc    Captura un trozo de la pantalla actual y lo guarda como la miniatura
///          de ese slot, con `screen_save_part()`. Llámala justo ANTES de
///          `save_game()` (con el juego todavía dibujado, no con el menú de
///          pausa ya encima): captura lo que se ve en ese instante, que es la
///          miniatura útil para "elige partida".
/// @param   {String} _slot
/// @param   {Real}   _x  Esquina superior izquierda del recorte, en pantalla.
/// @param   {Real}   _y
/// @param   {Real}   _w  Ancho del recorte.
/// @param   {Real}   _h  Alto del recorte.
/// @returns {Bool}   True si se pudo escribir el archivo.
function save_thumbnail_capture(_slot, _x, _y, _w, _h) {
    if (!save_ensure_dir()) { return false; }
    screen_save_part(save_thumbnail_path(_slot), _x, _y, _w, _h);
    return file_exists(save_thumbnail_path(_slot));
}


/// @function save_thumbnail_load(_slot)
/// @desc    Carga la miniatura de un slot como sprite, para dibujarla en la
///          ficha de la ranura. ⚠️ El sprite que devuelve NO se libera solo:
///          bórralo con `sprite_delete()` cuando dejes de necesitarlo (al
///          cambiar de pantalla, o al recargar la lista) — si no, cada
///          repintado de la lista de partidas deja una fuga de memoria.
/// @param   {String} _slot
/// @returns {Asset.GMSprite|Undefined}  El sprite, o `undefined` si esa ranura
///                                      no tiene miniatura.
function save_thumbnail_load(_slot) {
    var _ruta = save_thumbnail_path(_slot);
    if (!file_exists(_ruta)) { return undefined; }

    var _spr = sprite_add(_ruta, 1, false, false, 0, 0);
    if (!sprite_exists(_spr)) { return undefined; }

    return _spr;
}


/// @function save_thumbnail_delete(_slot)
/// @desc    Borra el archivo de miniatura de un slot, si existe. `delete_save()`
///          ya la llama sola; solo hace falta a mano si quieres limpiar la
///          miniatura sin borrar la partida.
/// @param   {String} _slot
/// @returns {Bool}  True si había algo que borrar.
function save_thumbnail_delete(_slot) {
    var _ruta = save_thumbnail_path(_slot);
    if (!file_exists(_ruta)) { return false; }
    file_delete(_ruta);
    return true;
}


/// @function delete_save(_slot)
/// @desc    Borra una partida. También limpia los temporales huérfanos que
///          haya podido dejar un intento de guardado fallido, y la miniatura
///          de la ranura si existe (save_thumbnail_capture()).
///          ⚠️ NO borra las copias de seguridad rotativas: quedan disponibles
///          para `load_game_recover()` aunque el slot principal se borre.
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

    save_thumbnail_delete(_slot);   // no hace nada si la ranura no tenía miniatura

    return _borrado;
}


/// @function save_list(_slots)
/// @desc    Devuelve la información de varios slots de una vez, para pintar un
///          menu de seleccion de partida.
/// @param   {Array<String>} _slots  Nombres de slot a consultar.
/// @returns {Array<Struct>}         Array de { slot, existe, versión, fecha, meta }.
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
            fecha   : is_struct(_meta) ? _meta.fecha   : "",
            meta    : is_struct(_meta) ? _meta.meta    : undefined
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
