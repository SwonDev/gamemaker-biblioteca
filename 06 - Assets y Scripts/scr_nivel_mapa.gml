// ============================================================================
// scr_nivel_mapa.gml
// El nivel como mapa de texto: validar, construir y autotile.
//
// POR QUÉ LO NECESITAS
//   Un agente de IA no puede abrir el editor de salas, y colocar las
//   instancias una a una con `ROOM INSTANCE CREATE` cuesta una llamada de
//   `resourcetool` por bloque: un nivel modesto son 1 400 llamadas, y cada
//   retoque del diseño las repite todas. La salida es dejar la sala vacía y
//   describir el nivel en texto:
//
//       "########################"
//       "#@.....o...........o..!#"
//       "#####...====...#####...##"
//
//   La receta completa —con las medidas del ahorro y los tres sitios donde
//   puede vivir el mapa— está en 04 · 58. Este script es esa receta ya
//   generalizada, compilada y sin nada específico de un juego dentro.
//
// QUÉ RESUELVE QUE LA RECETA DEJABA EN TUS MANOS
//   · La leyenda decide qué es sólido. La receta compara con "#"; aquí el
//     carácter puede ser cualquiera, porque lo que manda es `solido: true`.
//   · Los papeles («dónde empieza el jugador», «dónde se sale») son un campo
//     de la leyenda, no dos caracteres fijos.
//   · `nivel_mapa_construir()` VALIDA antes de crear nada, y si el mapa está mal
//     no crea NADA. Un nivel a medio construir es peor que ninguno.
//   · La clave estable de 04 · 58 §5 la pone él en cada instancia, así que el
//     guardado no depende del orden de recorrido.
//   · Fuera del mapa cuenta como sólido O como vacío, a elección: es la única
//     diferencia real entre el autotile de 04 · 58 §6 y el de 13 · 07 §5 bis,
//     y hasta ahora había que saberlo de memoria.
//
// Funciones nativas usadas (verificadas con buscar.py / gm-cli manual read):
//   array_length, array_push, string_length, string_char_at, string_pos,
//   string_split, string_replace_all, string_trim, string, struct_exists,
//   struct_get, struct_set, struct_get_names, is_struct, is_array, is_string,
//   is_real, is_callable, instance_create_layer, layer_exists, object_exists,
//   show_debug_message, show_error
//
// Dependencias: ninguna.
//
// USO RÁPIDO
//   // En el Create de obj_nivel:
//   leyenda = {
//       "#" : { objeto: obj_solido,     solido: true  },
//       "=" : { objeto: obj_plataforma, solido: false },
//       "o" : { objeto: obj_moneda,     solido: false },
//       "@" : { objeto: noone,          papel:  "aparicion" },
//       "!" : { objeto: obj_salida,     papel:  "salida" }
//   };
//
//   var _r = nivel_mapa_construir(mi_mapa_del_nivel(global.nivel), leyenda,
//                                 { celda: 16, capa: "Instances", nombre: "n1" });
//
//   instance_create_layer(_r.aparicion_x, _r.aparicion_y, "Instances", obj_jugador);
//
// POR QUÉ LAS FUNCIONES SE LLAMAN `nivel_mapa_*` Y LAS VARIABLES `nivel_*`
//   No es capricho: **una función global y una variable de instancia no pueden
//   llamarse igual**. Si las dos se llaman `nivel_clave`, la asignación
//   `_inst.nivel_clave = _clave` funciona y `variable_instance_exists()` dice
//   que la variable está ahí — pero al leer el nombre desnudo dentro del
//   objeto, `if (nivel_clave == ...)`, GameMaker devuelve **la función**, no el
//   valor. Sin error, sin aviso: la comparación es siempre falsa.
//   Se descubrió ejecutando el banco de pruebas de este mismo script, no
//   compilándolo — compilaba perfectamente. Está contado en 05 · 04 §2 bis.
//
//   La regla que sale de ahí y que este script cumple:
//     · funciones            -> `nivel_mapa_…`
//     · variables de instancia -> `nivel_…` (nivel_col, nivel_fila, nivel_clave,
//                                 nivel_char)
//   Ningún nombre aparece en las dos listas.
//
// NOTA SOBRE «FALLAR RUIDOSAMENTE»
//   Cuando el mapa está mal, este script escribe el problema en el log Y llama
//   a `show_error()`. Pero NO se apoya en que `show_error()` cierre el juego:
//   el manual de LTS 2026 dice literalmente que su segundo argumento
//   («abort») está ahí solo por compatibilidad y no tiene efecto, y que la
//   función es «for debug use only». Por eso la garantía de verdad es otra:
//   con el mapa mal, `nivel_mapa_construir()` devuelve sin crear ni una instancia.
//   Pase lo que pase con el diálogo, no arranca un nivel a medias.
// ============================================================================


/// @function nivel_mapa_opciones(_personal)
/// @desc     Opciones por defecto, mezcladas con las que tú pases. Todas las
///           funciones de este script aceptan un struct PARCIAL y lo pasan por
///           aquí, así que puedes escribir `{ celda: 24 }` y olvidarte del resto.
/// @param    {Struct} _personal  Solo las opciones que quieras cambiar.
/// @returns  {Struct}
function nivel_mapa_opciones(_personal = undefined)
{
    // Si ya viene mezclado, se devuelve tal cual. Sin esto, `nivel_mapa_enterrada()`
    // reconstruiría el struct de opciones nueve veces por casilla — decenas de
    // miles de structs en un nivel mediano, todos idénticos y todos tirados.
    if (is_struct(_personal) && struct_exists(_personal, "__nivel_op")) return _personal;

    var _op = {
        // Marca interna: "este struct ya pasó por aquí". No la toques.
        __nivel_op: true,

        // Píxeles por casilla. Debe coincidir con el tamaño del sprite del bloque.
        celda: 16,

        // Capa de instancias donde se crea todo. Una leyenda puede sobreescribirla
        // por carácter con `capa: "Otra_capa"`.
        capa: "Instances",

        // Caracteres que significan "aquí no hay nada". Por defecto punto y espacio.
        aire: ". ",

        // Prefijo de la clave estable (04 · 58 §5). Ponle el nombre del nivel.
        nombre: "n",

        // Qué hay más allá del borde del mapa, para el autotile y para saber si
        // una casilla está enterrada:
        //   true  -> sólido. El borde de la roca NO se dibuja con contorno.
        //            Es lo que quieres si el nivel continúa fuera de cámara (04 · 58 §6).
        //   false -> vacío. El borde SÍ se remata. Es lo que quiere un mapa que
        //            se ve entero, como los de 13 · 07 §5 bis.
        fuera_es_solido: true,

        // No instanciar una casilla sólida rodeada de sólidos por los ocho lados:
        // no se ve y no colisiona. Ahorra entre el 30 % y el 65 % de las instancias.
        // PONLO A false si el jugador puede excavar: al romper la de fuera, la de
        // dentro tendría que existir.
        saltar_enterradas: true,

        // Asignar `image_index` = bitmask de 4 vecinos a cada instancia sólida.
        // Requiere que el sprite tenga las 16 sub-imágenes en el orden N=1,E=2,S=4,O=8.
        autotile: false,

        // Validar antes de construir. Déjalo en true salvo que ya hayas validado.
        validar: true,

        // function(_caracter, _clave, _col, _fila) -> Bool. Devuelve true para NO
        // crear esa casilla. Es donde se filtran los coleccionables ya recogidos.
        omitir: undefined,

        // function(_texto, _problemas) -> void. Qué hacer cuando el mapa está mal.
        // Por defecto: escribirlo en el log y abrir el diálogo de `show_error()`.
        // Dale el tuyo para llevarlo a tu propia pantalla de error — o para poder
        // PROBAR el fallo, que con un diálogo modal delante no se puede.
        al_fallar: undefined,

        // Cuántas veces tiene que aparecer cada papel. Si lo pasas, lo REEMPLAZA
        // entero: incluye también los papeles que quieras conservar.
        exige: {
            aparicion: { min: 1, max: 1 },
            salida:    { min: 1, max: infinity }
        }
    };

    if (is_struct(_personal))
    {
        var _claves = struct_get_names(_personal);
        for (var _i = 0; _i < array_length(_claves); _i++)
        {
            struct_set(_op, _claves[_i], struct_get(_personal, _claves[_i]));
        }
    }

    return _op;
}


/// @function nivel_mapa_filas_de_cadena(_texto)
/// @desc     Parte un bloque de texto en filas. Acepta finales de línea de
///           Windows y de Unix, y descarta las líneas vacías del principio y
///           del final (las que deja un heredoc o un archivo con salto final).
///           NO recorta espacios dentro de la fila: un espacio es aire y cuenta.
/// @param    {String} _texto
/// @returns  {Array<String>}
function nivel_mapa_filas_de_cadena(_texto)
{
    if (!is_string(_texto)) return [];

    var _normalizado = string_replace_all(_texto, "\r\n", "\n");
    _normalizado     = string_replace_all(_normalizado, "\r", "\n");

    var _brutas = string_split(_normalizado, "\n", false);
    var _filas  = [];

    // Recorta solo por los extremos: una fila vacía EN MEDIO del mapa es un
    // error de verdad y tiene que llegar hasta la validación.
    var _ini = 0;
    var _fin = array_length(_brutas) - 1;
    while (_ini <= _fin && string_trim(_brutas[_ini]) == "") _ini++;
    while (_fin >= _ini && string_trim(_brutas[_fin]) == "") _fin--;

    for (var _i = _ini; _i <= _fin; _i++) array_push(_filas, _brutas[_i]);

    return _filas;
}


/// @function nivel_mapa_char(_filas, _col, _fila)
/// @desc     El carácter de una casilla, o "" si cae fuera del mapa.
///           Ojo: también devuelve "" si la fila es más corta que las demás,
///           que es justo lo que `nivel_mapa_validar()` detecta antes de llegar aquí.
/// @param    {Array<String>} _filas
/// @param    {Real} _col
/// @param    {Real} _fila
/// @returns  {String}
function nivel_mapa_char(_filas, _col, _fila)
{
    if (_fila < 0 || _fila >= array_length(_filas)) return "";
    var _f = _filas[_fila];
    if (_col < 0 || _col >= string_length(_f)) return "";
    return string_char_at(_f, _col + 1);
}


/// @function nivel_mapa_es_aire(_caracter, _opciones)
/// @desc     true si ese carácter significa "aquí no hay nada".
/// @param    {String} _caracter
/// @param    {Struct} _opciones
/// @returns  {Bool}
function nivel_mapa_es_aire(_caracter, _opciones = undefined)
{
    if (_caracter == "") return true;
    var _op = nivel_mapa_opciones(_opciones);
    return (string_pos(_caracter, _op.aire) > 0);
}


/// @function nivel_mapa_es_solido(_filas, _leyenda, _col, _fila, _opciones)
/// @desc     true si esa casilla es sólida según la leyenda. Fuera del mapa
///           depende de `fuera_es_solido` — lee su comentario en las opciones,
///           porque es la diferencia entre un borde con contorno y uno sin él.
/// @returns  {Bool}
function nivel_mapa_es_solido(_filas, _leyenda, _col, _fila, _opciones = undefined)
{
    var _op = nivel_mapa_opciones(_opciones);
    var _c  = nivel_mapa_char(_filas, _col, _fila);

    if (_c == "") return _op.fuera_es_solido;
    if (!struct_exists(_leyenda, _c)) return false;

    var _entrada = _leyenda[$ _c];
    if (!is_struct(_entrada)) return false;

    return (struct_exists(_entrada, "solido") && _entrada.solido == true);
}


/// @function nivel_mapa_enterrada(_filas, _leyenda, _col, _fila, _opciones)
/// @desc     true si la casilla es sólida y sus ocho vecinas también: no se ve
///           y no colisiona con nada, así que crear su instancia es gasto puro.
/// @returns  {Bool}
function nivel_mapa_enterrada(_filas, _leyenda, _col, _fila, _opciones = undefined)
{
    var _op = nivel_mapa_opciones(_opciones);
    if (!nivel_mapa_es_solido(_filas, _leyenda, _col, _fila, _op)) return false;

    for (var _dy = -1; _dy <= 1; _dy++)
    {
        for (var _dx = -1; _dx <= 1; _dx++)
        {
            if (_dx == 0 && _dy == 0) continue;
            if (!nivel_mapa_es_solido(_filas, _leyenda, _col + _dx, _fila + _dy, _op)) return false;
        }
    }

    return true;
}


/// @function nivel_mapa_bitmask(_filas, _leyenda, _col, _fila, _opciones)
/// @desc     Bitmask de los 4 vecinos ortogonales: N=1, E=2, S=4, O=8.
///           Devuelve 0..15, listo para usar como `image_index` si ordenas las
///           16 sub-imágenes del sprite en ese mismo orden — sin tabla de
///           traducción y sin switch (13 · 07 §5 bis lo explica en detalle).
/// @returns  {Real} 0..15
function nivel_mapa_bitmask(_filas, _leyenda, _col, _fila, _opciones = undefined)
{
    var _op = nivel_mapa_opciones(_opciones);
    var _m  = 0;

    if (nivel_mapa_es_solido(_filas, _leyenda, _col,     _fila - 1, _op)) _m |= 1;   // N
    if (nivel_mapa_es_solido(_filas, _leyenda, _col + 1, _fila,     _op)) _m |= 2;   // E
    if (nivel_mapa_es_solido(_filas, _leyenda, _col,     _fila + 1, _op)) _m |= 4;   // S
    if (nivel_mapa_es_solido(_filas, _leyenda, _col - 1, _fila,     _op)) _m |= 8;   // O

    return _m;
}


/// @function nivel_mapa_clave(_nombre, _col, _fila)
/// @desc     Clave estable de una casilla, para el guardado. NO uses el orden
///           de recorrido: insertar una moneda en mitad del mapa desplaza el
///           índice de todas las siguientes y una partida guardada creerá que
///           recogió otras (04 · 58 §5). La posición no se desplaza nunca.
/// @returns  {String}  p. ej. "n1_x34_y12"
function nivel_mapa_clave(_nombre, _col, _fila)
{
    return string(_nombre) + "_x" + string(_col) + "_y" + string(_fila);
}


/// @function nivel_mapa_validar(_filas, _leyenda, _opciones)
/// @desc     Comprueba todo lo que rompe un nivel EN SILENCIO. Devuelve un
///           array vacío si está bien, o una lista de problemas legibles.
///           Llámalo tú solo si vas a construir a mano: `nivel_mapa_construir()`
///           ya lo llama por su cuenta.
/// @param    {Array<String>} _filas
/// @param    {Struct} _leyenda
/// @param    {Struct} _opciones
/// @returns  {Array<String>}
function nivel_mapa_validar(_filas, _leyenda, _opciones = undefined)
{
    var _op        = nivel_mapa_opciones(_opciones);
    var _problemas = [];

    if (!is_array(_filas))
    {
        array_push(_problemas, "el mapa no es un array de cadenas");
        return _problemas;
    }
    if (!is_struct(_leyenda))
    {
        array_push(_problemas, "la leyenda no es un struct");
        return _problemas;
    }

    // --- La leyenda, antes que el mapa -------------------------------------
    // Un objeto mal escrito en la leyenda no falla al compilar: falla al crear
    // la primera instancia, con el nivel a medio construir.
    var _claves = struct_get_names(_leyenda);
    for (var _i = 0; _i < array_length(_claves); _i++)
    {
        var _k = _claves[_i];
        if (string_length(_k) != 1)
        {
            array_push(_problemas, "la clave «" + string(_k) + "» de la leyenda no es un solo carácter");
            continue;
        }
        var _e = _leyenda[$ _k];
        if (!is_struct(_e))
        {
            array_push(_problemas, "la entrada «" + _k + "» de la leyenda no es un struct");
            continue;
        }
        if (struct_exists(_e, "objeto") && _e.objeto != noone && !is_undefined(_e.objeto))
        {
            if (!object_exists(_e.objeto))
                array_push(_problemas, "el objeto de la entrada «" + _k + "» no existe");
        }
        if (nivel_mapa_es_aire(_k, _op))
            array_push(_problemas, "«" + _k + "» está en la leyenda y también en `aire`: no se creará nunca");
    }

    // --- La capa tiene que existir en ESTA sala ------------------------------
    if (!layer_exists(_op.capa))
        array_push(_problemas, "la capa «" + string(_op.capa) + "» no existe en esta sala");

    // --- El mapa -------------------------------------------------------------
    var _alto = array_length(_filas);
    if (_alto == 0)
    {
        array_push(_problemas, "el mapa no tiene ni una fila");
        return _problemas;
    }

    var _ancho   = string_length(_filas[0]);
    var _cuentas = {};

    for (var _y = 0; _y < _alto; _y++)
    {
        // Una fila corta desplaza TODO lo que hay debajo, y es el error más
        // común al editar el mapa a mano. No da error: da un nivel torcido.
        if (string_length(_filas[_y]) != _ancho)
        {
            array_push(_problemas, "la fila " + string(_y) + " mide "
                + string(string_length(_filas[_y])) + " y la primera mide " + string(_ancho));
        }

        for (var _x = 0; _x < string_length(_filas[_y]); _x++)
        {
            var _c = string_char_at(_filas[_y], _x + 1);
            if (nivel_mapa_es_aire(_c, _op)) continue;

            // Un carácter sin leyenda se ignoraría en silencio: ni error, ni bloque.
            if (!struct_exists(_leyenda, _c))
            {
                array_push(_problemas, "carácter «" + _c + "» sin leyenda, en "
                    + string(_x) + "," + string(_y));
                continue;
            }

            var _entrada = _leyenda[$ _c];
            if (is_struct(_entrada) && struct_exists(_entrada, "papel"))
            {
                var _papel = _entrada.papel;
                var _n     = struct_exists(_cuentas, _papel) ? struct_get(_cuentas, _papel) : 0;
                struct_set(_cuentas, _papel, _n + 1);
            }
        }
    }

    // --- Los papeles obligatorios -------------------------------------------
    if (is_struct(_op.exige))
    {
        var _papeles = struct_get_names(_op.exige);
        for (var _p = 0; _p < array_length(_papeles); _p++)
        {
            var _papel = _papeles[_p];
            var _regla = struct_get(_op.exige, _papel);
            var _veces = struct_exists(_cuentas, _papel) ? struct_get(_cuentas, _papel) : 0;

            var _min = (is_struct(_regla) && struct_exists(_regla, "min")) ? _regla.min : 0;
            var _max = (is_struct(_regla) && struct_exists(_regla, "max")) ? _regla.max : infinity;

            if (_veces < _min || _veces > _max)
            {
                array_push(_problemas, "el papel «" + string(_papel) + "» aparece "
                    + string(_veces) + " veces y debe aparecer entre "
                    + string(_min) + " y " + string(_max));
            }
        }
    }

    return _problemas;
}


/// @function nivel_mapa_construir(_filas, _leyenda, _opciones)
/// @desc     Instancia el mapa. Valida primero; si el mapa está mal, avisa y
///           NO crea nada (ver la nota sobre «fallar ruidosamente» arriba).
/// @param    {Array<String>} _filas
/// @param    {Struct} _leyenda
/// @param    {Struct} _opciones
/// @returns  {Struct}  {
///               ancho, alto, creadas, saltadas,
///               aparicion_x, aparicion_y, hay_aparicion,
///               papeles,      // struct: papel -> array de { x, y, col, fila, inst }
///               problemas     // array vacío si todo fue bien
///           }
function nivel_mapa_construir(_filas, _leyenda, _opciones = undefined)
{
    var _op  = nivel_mapa_opciones(_opciones);
    var _res = {
        ancho: 0, alto: 0, creadas: 0, saltadas: 0,
        aparicion_x: 0, aparicion_y: 0, hay_aparicion: false,
        papeles: {}, problemas: []
    };

    if (_op.validar)
    {
        _res.problemas = nivel_mapa_validar(_filas, _leyenda, _op);
        if (array_length(_res.problemas) > 0)
        {
            var _texto = "MAPA MAL FORMADO («" + string(_op.nombre) + "»):";
            for (var _i = 0; _i < array_length(_res.problemas); _i++)
            {
                _texto += "\n· " + _res.problemas[_i];
            }

            if (is_callable(_op.al_fallar))
            {
                _op.al_fallar(_texto, _res.problemas);
            }
            else
            {
                show_debug_message(_texto);
                show_error(_texto, true);
            }

            return _res;    // sin construir NADA: un nivel a medias es peor que ninguno
        }
    }

    _res.alto  = array_length(_filas);
    _res.ancho = (_res.alto > 0) ? string_length(_filas[0]) : 0;

    for (var _y = 0; _y < _res.alto; _y++)
    {
        var _fila = _filas[_y];

        for (var _x = 0; _x < string_length(_fila); _x++)
        {
            var _c = string_char_at(_fila, _x + 1);
            if (nivel_mapa_es_aire(_c, _op)) continue;
            if (!struct_exists(_leyenda, _c)) continue;   // ya avisó nivel_mapa_validar()

            var _entrada = _leyenda[$ _c];
            var _px      = _x * _op.celda;
            var _py      = _y * _op.celda;
            var _clave   = nivel_mapa_clave(_op.nombre, _x, _y);

            // El filtro del proyecto: coleccionables ya recogidos, puertas ya
            // abiertas, enemigos ya derrotados en esta partida...
            if (is_callable(_op.omitir) && _op.omitir(_c, _clave, _x, _y)) continue;

            // Roca enterrada: invisible e intocable. No se salta si el objeto
            // tiene un papel — un punto de aparición enterrado sigue haciendo falta.
            if (_op.saltar_enterradas
                && !struct_exists(_entrada, "papel")
                && nivel_mapa_enterrada(_filas, _leyenda, _x, _y, _op))
            {
                _res.saltadas++;
                continue;
            }

            var _inst   = noone;
            var _objeto = struct_exists(_entrada, "objeto") ? _entrada.objeto : noone;

            if (_objeto != noone && !is_undefined(_objeto))
            {
                var _capa = struct_exists(_entrada, "capa") ? _entrada.capa : _op.capa;
                _inst = instance_create_layer(_px, _py, _capa, _objeto);

                // Todo lo que una instancia necesita saber de su casilla, y que
                // si no se lo das aquí acaba recalculándose mal en otra parte.
                _inst.nivel_col   = _x;
                _inst.nivel_fila  = _y;
                _inst.nivel_clave = _clave;
                _inst.nivel_char  = _c;

                if (_op.autotile && nivel_mapa_es_solido(_filas, _leyenda, _x, _y, _op))
                    _inst.image_index = nivel_mapa_bitmask(_filas, _leyenda, _x, _y, _op);

                _res.creadas++;
            }

            if (struct_exists(_entrada, "papel"))
            {
                var _papel = _entrada.papel;
                if (!struct_exists(_res.papeles, _papel)) struct_set(_res.papeles, _papel, []);
                array_push(struct_get(_res.papeles, _papel),
                    { x: _px, y: _py, col: _x, fila: _y, inst: _inst });

                if (_papel == "aparicion" && !_res.hay_aparicion)
                {
                    _res.aparicion_x   = _px;
                    _res.aparicion_y   = _py;
                    _res.hay_aparicion = true;
                }
            }
        }
    }

    return _res;
}
