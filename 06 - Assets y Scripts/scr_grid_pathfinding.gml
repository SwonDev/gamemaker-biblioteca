// ============================================================================
// scr_grid_pathfinding.gml
// Pathfinding en rejilla. Dos implementaciones:
//
//   1. `Grid`      -> envoltorio sobre `mp_grid_*` (rápido, C++, sin costes
//                     por celda). Usa A* internamente. Es la que usarás casi
//                     siempre: torres de un tower defense, enemigos de un RPG,
//                     unidades de un RTS.
//
//   2. `GridPonderado` -> A* escrito en GML puro CON COSTE POR CELDA. Para
//                     cuando unas celdas cuesten más que otras (barro, agua,
//                     carretera). `mp_grid` no soporta costes: si los
//                     necesitas, usa este.
//
// Funciones nativas usadas (verificadas con gm-cli manual read):
//   mp_grid_create, mp_grid_destroy, mp_grid_add_instances, mp_grid_add_cell,
//   mp_grid_add_rectangle, mp_grid_clear_all, mp_grid_clear_cell,
//   mp_grid_clear_rectangle, mp_grid_get_cell, mp_grid_path, mp_grid_draw,
//   path_add, path_delete, path_clear_points, path_add_point,
//   path_get_number, path_get_point_x, path_get_point_y, path_get_length,
//   ds_priority_create, ds_priority_add, ds_priority_delete_min,
//   ds_priority_size, ds_priority_empty, ds_priority_destroy
//
// Dependencias: ninguna.
//
// USO RAPIDO (mp_grid)
//   // En el Create de obj_game:
//   grid = new Grid(32);                       // celdas de 32x32
//   grid.add_object(obj_wall);                 // marca los muros
//   grid.add_object(obj_torre);
//
//   // Para que un enemigo persiga al jugador:
//   var _ruta = grid.find_path(x, y, obj_player.x, obj_player.y);
//   if (_ruta != noone) {
//       path_start(_ruta, 3, path_action_stop, false);
//   }
//
//   // ⚠️ `find_path` crea un path DINAMICO con `path_add()`.
//   //    Tienes que destruirlo con `path_delete()` cuando deje de servirte,
//   //    o tendras una fuga de memoria.
//
//   // En el Clean Up de obj_game:
//   grid.destroy();
//
// USO RAPIDO (A* con costes)
//   grid2 = new GridPonderado(32);
//   grid2.set_coste(5, 3, 4);      // esa celda cuesta 4 en vez de 1
//   var _pts = grid2.buscar(0, 0, 10, 8);   // array de {x, y} en píxeles
// ============================================================================


// ===========================================================================
// PARTE 1 · Envoltorio sobre mp_grid
// ===========================================================================

/// @function Grid(_tamano_celda, _ancho, _alto, _izq, _arr)
/// @desc    Constructor. Crea una rejilla de navegacion con `mp_grid_create()`.
/// @param   {Real} _tamano_celda  Pixeles de lado de cada celda.
/// @param   {Real} _ancho         Ancho de la rejilla en píxeles. Si se omite,
///                                se usa `room_width`.
/// @param   {Real} _alto          Alto de la rejilla en píxeles. Si se omite,
///                                se usa `room_height`.
/// @param   {Real} _izq           Esquina superior izquierda X (por defecto 0).
/// @param   {Real} _arr           Esquina superior izquierda Y (por defecto 0).
function Grid(_tamano_celda, _ancho = -1, _alto = -1, _izq = 0, _arr = 0) constructor {
    celda = max(_tamano_celda, 1);
    izq   = _izq;
    arr   = _arr;
    ancho = (_ancho <= 0) ? room_width  : _ancho;
    alto  = (_alto  <= 0) ? room_height : _alto;

    columnas = ceil(ancho / celda);
    filas    = ceil(alto  / celda);

    // Trampa de unidades: `_ancho`/`_alto` van en PÍXELES, y `set_coste()`,
    // `bloquear()` y `buscar()` en CELDAS. Pasar el número de columnas donde van
    // los píxeles deja una rejilla de 1x1 que no da error: simplemente no
    // encuentra ninguna ruta, nunca, y parece que el pathfinding está roto.
    // Ninguna rejilla real es de una sola celda, así que decirlo aquí no molesta
    // a nadie y ahorra la tarde de buscarlo.
    if (columnas < 2 || filas < 2) {
        show_debug_message("Grid: la rejilla ha salido de " + string(columnas) + "x" + string(filas)
            + " celdas. ¿Pasaste columnas y filas donde van PÍXELES? "
            + "Con celda de " + string(celda) + " px, para " + string(columnas) + " columnas "
            + "hay que pasar " + string(columnas * celda) + ".");
    }

    // `mp_grid_create` devuelve un índice que HAY QUE DESTRUIR con
    // `mp_grid_destroy`: no lo limpia el recolector de basura.
    id_mp = mp_grid_create(izq, arr, columnas, filas, celda, celda);

    /// @desc Marca todas las instancias de un objeto como obstaculo.
    /// @param {Asset.GMObject} _obj   Objeto a marcar.
    /// @param {Bool} _prec            Usar colisión precisa (más lento, más exacto).
    static add_object = function(_obj, _prec = false) {
        mp_grid_add_instances(id_mp, _obj, _prec);
    };

    /// @desc Marca una celda concreta como bloqueada.
    /// @param {Real} _col  Columna.
    /// @param {Real} _fil  Fila.
    static add_cell = function(_col, _fil) {
        if (_col < 0 || _fil < 0 || _col >= columnas || _fil >= filas) { return; }
        mp_grid_add_cell(id_mp, _col, _fil);
    };

    /// @desc Marca una region rectangular (en PIXELES) como bloqueada.
    /// @param {Real} _x1
    /// @param {Real} _y1
    /// @param {Real} _x2
    /// @param {Real} _y2
    static add_rect = function(_x1, _y1, _x2, _y2) {
        mp_grid_add_rectangle(id_mp, _x1, _y1, _x2, _y2);
    };

    /// @desc Libera una celda.
    /// @param {Real} _col  Columna.
    /// @param {Real} _fil  Fila.
    static clear_cell = function(_col, _fil) {
        if (_col < 0 || _fil < 0 || _col >= columnas || _fil >= filas) { return; }
        mp_grid_clear_cell(id_mp, _col, _fil);
    };

    /// @desc Libera toda la rejilla. Llamalo si el mapa cambia por completo.
    static clear_all = function() {
        mp_grid_clear_all(id_mp);
    };

    /// @desc Consulta si una celda está bloqueada.
    /// @param {Real} _col  Columna.
    /// @param {Real} _fil  Fila.
    /// @returns {Real}     -1 si está bloqueada (o fuera de rango), 0 si libre.
    static get_cell = function(_col, _fil) {
        if (_col < 0 || _fil < 0 || _col >= columnas || _fil >= filas) { return -1; }
        return mp_grid_get_cell(id_mp, _col, _fil);
    };

    /// @desc Convierte una celda a coordenadas de PIXELES (su centro).
    /// @param {Real} _col
    /// @param {Real} _fil
    /// @returns {Struct}  { x, y }
    static cell_to_px = function(_col, _fil) {
        return {
            x : izq + _col * celda + celda / 2,
            y : arr  + _fil * celda + celda / 2
        };
    };

    /// @desc Convierte píxeles a celda.
    /// @param {Real} _x
    /// @param {Real} _y
    /// @returns {Struct}  { col, fil }
    static px_to_cell = function(_x, _y) {
        return {
            col : floor((_x - izq) / celda),
            fil : floor((_y - arr)  / celda)
        };
    };

    /// @desc Calcula una ruta entre dos puntos en PIXELES.
    ///       ⚠️ Devuelve un path DINAMICO creado con `path_add()`: destrúyelo
    ///       con `path_delete()` cuando dejes de usarlo.
    /// @param {Real} _x1  Origen X.
    /// @param {Real} _y1  Origen Y.
    /// @param {Real} _x2  Destino X.
    /// @param {Real} _y2  Destino Y.
    /// @param {Bool} _diagonal  Permitir movimiento en diagonal.
    /// @returns {Id.Path|Constant.Noone}  El path, o `noone` si no hay ruta.
    static find_path = function(_x1, _y1, _x2, _y2, _diagonal = true) {
        var _ruta = path_add();

        var _ok = mp_grid_path(id_mp, _ruta, _x1, _y1, _x2, _y2, _diagonal);

        if (!_ok) {
            path_delete(_ruta);
            return noone;
        }
        return _ruta;
    };

    /// @desc Igual que `find_path` pero devolviendo la ruta como ARRAY de
    ///       puntos { x, y } en píxeles. No crea paths: no hay que limpiar
    ///       nada. Mas comodo si mueves la unidad tu mismo.
    /// @param {Real} _x1
    /// @param {Real} _y1
    /// @param {Real} _x2
    /// @param {Real} _y2
    /// @param {Bool} _diagonal
    /// @returns {Array<Struct>}  Array de { x, y }, vacío si no hay ruta.
    static find_points = function(_x1, _y1, _x2, _y2, _diagonal = true) {
        var _ruta = path_add();
        var _puntos = [];

        if (mp_grid_path(id_mp, _ruta, _x1, _y1, _x2, _y2, _diagonal)) {
            var _n = path_get_number(_ruta);
            var _i;
            for (_i = 0; _i < _n; _i++) {
                array_push(_puntos, {
                    x : path_get_point_x(_ruta, _i),
                    y : path_get_point_y(_ruta, _i)
                });
            }
        }

        // Siempre destruimos el path temporal, haya o no haya ruta.
        path_delete(_ruta);
        return _puntos;
    };

    /// @desc Longitud de la rejilla en píxeles. Para depurar.
    /// @returns {String}  Descripción legible.
    static info = function() {
        return "Grid " + string(columnas) + "x" + string(filas) +
               " (celda " + string(celda) + "px)";
    };

    /// @desc Dibuja la rejilla. LLAMALO EN UN EVENTO DRAW.
    static draw_debug = function() {
        mp_grid_draw(id_mp);
    };

    /// @desc Destruye la rejilla y libera su memoria. LLAMALO EN CLEAN UP.
    static destroy = function() {
        mp_grid_destroy(id_mp);
    };
}


// ===========================================================================
// PARTE 2 · A* en GML puro con coste por celda
// ===========================================================================

/// @function GridPonderado(_tamano_celda, _ancho, _alto, _izq, _arr)
/// @desc    Rejilla de navegacion con coste por celda. Usala cuando unas
///          celdas deban ser "más caras" que otras (barro, agua, carretera).
///          Es más lenta que `mp_grid`: solo para rejillas pequenas o
///          recalculos puntuales.
/// @param   {Real} _tamano_celda  Pixeles de lado de la celda.
/// @param   {Real} _ancho         Ancho en píxeles (por defecto room_width).
/// @param   {Real} _alto          Alto en píxeles (por defecto room_height).
/// @param   {Real} _izq           Origen X.
/// @param   {Real} _arr           Origen Y.
function GridPonderado(_tamano_celda, _ancho = -1, _alto = -1, _izq = 0, _arr = 0) constructor {
    celda    = max(_tamano_celda, 1);
    izq      = _izq;
    arr      = _arr;
    ancho    = (_ancho <= 0) ? room_width  : _ancho;
    alto     = (_alto  <= 0) ? room_height : _alto;
    columnas = ceil(ancho / celda);
    filas    = ceil(alto  / celda);

    // Trampa de unidades: `_ancho`/`_alto` van en PÍXELES, y `set_coste()`,
    // `bloquear()` y `buscar()` en CELDAS. Pasar el número de columnas donde van
    // los píxeles deja una rejilla de 1x1 que no da error: simplemente no
    // encuentra ninguna ruta, nunca, y parece que el pathfinding está roto.
    // Ninguna rejilla real es de una sola celda, así que decirlo aquí no molesta
    // a nadie y ahorra la tarde de buscarlo.
    if (columnas < 2 || filas < 2) {
        show_debug_message("GridPonderado: la rejilla ha salido de " + string(columnas) + "x" + string(filas)
            + " celdas. ¿Pasaste columnas y filas donde van PÍXELES? "
            + "Con celda de " + string(celda) + " px, para " + string(columnas) + " columnas "
            + "hay que pasar " + string(columnas * celda) + ".");
    }

    // costes[fila][columna] = coste de entrar en esa celda.
    // -1 significa "intransitable".
    costes = [];
    var _f, _c;
    for (_f = 0; _f < filas; _f++) {
        var _fila = [];
        for (_c = 0; _c < columnas; _c++) {
            array_push(_fila, 1);
        }
        array_push(costes, _fila);
    }

    /// @desc Define el coste de entrar en una celda.
    /// @param {Real} _col   Columna.
    /// @param {Real} _fil   Fila.
    /// @param {Real} _coste Coste (>= 1). Usa -1 para hacerla intransitable.
    static set_coste = function(_col, _fil, _coste) {
        if (_col < 0 || _fil < 0 || _col >= columnas || _fil >= filas) { return; }
        costes[_fil][_col] = _coste;
    };

    /// @desc Coste de una celda, o -1 si está fuera de rango.
    /// @param {Real} _col
    /// @param {Real} _fil
    /// @returns {Real}
    static get_coste = function(_col, _fil) {
        if (_col < 0 || _fil < 0 || _col >= columnas || _fil >= filas) { return -1; }
        return costes[_fil][_col];
    };

    /// @desc Marca una celda como intransitable.
    /// @param {Real} _col
    /// @param {Real} _fil
    static bloquear = function(_col, _fil) {
        set_coste(_col, _fil, -1);
    };

    /// @desc Convierte píxeles a celda.
    /// @param {Real} _x
    /// @param {Real} _y
    /// @returns {Struct}  { col, fil }
    static px_to_cell = function(_x, _y) {
        return {
            col : floor((_x - izq) / celda),
            fil : floor((_y - arr)  / celda)
        };
    };

    /// @desc Convierte una celda a píxeles (centro).
    /// @param {Real} _col
    /// @param {Real} _fil
    /// @returns {Struct}  { x, y }
    static cell_to_px = function(_col, _fil) {
        return {
            x : izq + _col * celda + celda / 2,
            y : arr  + _fil * celda + celda / 2
        };
    };

    /// @desc Busca la ruta más barata entre dos celdas con A*.
    /// @param {Real} _c1  Columna de origen.
    /// @param {Real} _f1  Fila de origen.
    /// @param {Real} _c2  Columna de destino.
    /// @param {Real} _f2  Fila de destino.
    /// @param {Bool} _diagonal  Permitir diagonales.
    /// @returns {Array<Struct>}  Array de { x, y } en PIXELES, del origen al
    ///          destino. Vacio si no hay ruta.
    static buscar = function(_c1, _f1, _c2, _f2, _diagonal = true) {
        var _resultado = [];

        // Validaciones de entrada: un destino fuera del mapa o bloqueado
        // no tiene ruta posible.
        if (_c1 < 0 || _f1 < 0 || _c1 >= columnas || _f1 >= filas) { return _resultado; }
        if (_c2 < 0 || _f2 < 0 || _c2 >= columnas || _f2 >= filas) { return _resultado; }
        if (costes[_f2][_c2] < 0) { return _resultado; }

        // Caso trivial.
        if (_c1 == _c2 && _f1 == _f2) {
            array_push(_resultado, cell_to_px(_c1, _f1));
            return _resultado;
        }

        var _total = columnas * filas;

        // Usamos un array plano: índice = fil * columnas + col.
        var _g      = array_create(_total, -1);   // coste acumulado desde el origen
        var _padre  = array_create(_total, -1);   // de donde venimos
        var _cerrado = array_create(_total, false);

        var _abiertos = ds_priority_create();

        var _inicio = _f1 * columnas + _c1;
        _g[_inicio] = 0;

        // La prioridad es f = g + h. La heurística es la distancia de
        // Chebyshev (la correcta cuando se permiten diagonales de coste 1).
        // Se calcula en línea en vez de con una función auxiliar: las
        // funciones anidadas que capturan variables locales son fragiles en
        // GML y aquí no compensa el riesgo.
        var _dx0 = abs(_c1 - _c2);
        var _dy0 = abs(_f1 - _f2);
        var _h0 = (_diagonal) ? max(_dx0, _dy0) : (_dx0 + _dy0);

        ds_priority_add(_abiertos, _inicio, _h0);

        var _encontrado = false;
        var _destino = _f2 * columnas + _c2;

        // Los 4 o 8 vecinos. Con 8, el orden importa poco: A* ya elige.
        var _dc = [ 1, -1,  0,  0,  1,  1, -1, -1 ];
        var _df = [ 0,  0,  1, -1,  1, -1,  1, -1 ];
        var _max_vecinos = _diagonal ? 8 : 4;

        while (!ds_priority_empty(_abiertos)) {
            var _actual = ds_priority_delete_min(_abiertos);

            if (_actual == _destino) { _encontrado = true; break; }
            if (_cerrado[_actual]) { continue; }
            _cerrado[_actual] = true;

            var _col_a = _actual mod columnas;
            var _fil_a = _actual div columnas;

            var _i;
            for (_i = 0; _i < _max_vecinos; _i++) {
                var _cv = _col_a + _dc[_i];
                var _fv = _fil_a + _df[_i];

                if (_cv < 0 || _fv < 0 || _cv >= columnas || _fv >= filas) { continue; }

                var _indice_v = _fv * columnas + _cv;
                if (_cerrado[_indice_v]) { continue; }

                var _coste = costes[_fv][_cv];
                if (_coste < 0) { continue; }   // intransitable

                // En diagonal, "coste" la raiz de 2: evita que el camino en
                // zigzag salga más barato que la diagonal real.
                var _paso = (_i >= 4) ? (_coste * 1.4142) : _coste;
                var _nuevo_g = _g[_actual] + _paso;

                if (_g[_indice_v] == -1 || _nuevo_g < _g[_indice_v]) {
                    _g[_indice_v]     = _nuevo_g;
                    _padre[_indice_v] = _actual;

                    // Heuristica del vecino (distancia de Chebyshev, o de
                    // Manhattan si no hay diagonales).
                    var _dxv = abs(_cv - _c2);
                    var _dyv = abs(_fv - _f2);
                    var _hv = (_diagonal) ? max(_dxv, _dyv) : (_dxv + _dyv);

                    ds_priority_add(_abiertos, _indice_v, _nuevo_g + _hv);
                }
            }
        }

        ds_priority_destroy(_abiertos);

        if (!_encontrado) { return _resultado; }

        // Reconstruimos la ruta desde el destino hacia el origen y le damos
        // la vuelta al final.
        var _invertida = [];
        var _nodo = _destino;
        while (_nodo != -1) {
            var _c = _nodo mod columnas;
            var _f = _nodo div columnas;
            array_push(_invertida, cell_to_px(_c, _f));
            _nodo = _padre[_nodo];
        }

        var _j;
        for (_j = array_length(_invertida) - 1; _j >= 0; _j--) {
            array_push(_resultado, _invertida[_j]);
        }

        return _resultado;
    };

    /// @desc Atajo: busca la ruta dando las coordenadas en PIXELES.
    /// @param {Real} _x1
    /// @param {Real} _y1
    /// @param {Real} _x2
    /// @param {Real} _y2
    /// @param {Bool} _diagonal
    /// @returns {Array<Struct>}
    static buscar_px = function(_x1, _y1, _x2, _y2, _diagonal = true) {
        var _a = px_to_cell(_x1, _y1);
        var _b = px_to_cell(_x2, _y2);
        return buscar(_a.col, _a.fil, _b.col, _b.fil, _diagonal);
    };

    /// @desc Pinta la rejilla con el coste de cada celda. LLAMALO EN DRAW.
    ///       Rojo = intransitable, amarillo = caro, verde = normal.
    static draw_debug = function() {
        var _c_previo = draw_get_color();
        var _a_previo = draw_get_alpha();

        var _f, _c;
        for (_f = 0; _f < filas; _f++) {
            for (_c = 0; _c < columnas; _c++) {
                var _coste = costes[_f][_c];

                if (_coste < 0)      { draw_set_color(c_red); }
                else if (_coste > 1) { draw_set_color(c_yellow); }
                else                 { draw_set_color(c_lime); }

                draw_set_alpha(0.25);
                draw_rectangle(
                    izq + _c * celda, arr + _f * celda,
                    izq + _c * celda + celda - 1, arr + _f * celda + celda - 1,
                    false
                );
            }
        }

        draw_set_color(_c_previo);
        draw_set_alpha(_a_previo);
    };
}
