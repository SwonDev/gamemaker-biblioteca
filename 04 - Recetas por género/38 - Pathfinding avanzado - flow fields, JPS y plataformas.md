# 38 · Pathfinding avanzado — flow fields, JPS y plataformas

> Lo que se queda corto cuando `Grid`/`GridPonderado` (`06/scr_grid_pathfinding.gml`) dejan de
> alcanzar: cientos de unidades hacia el mismo sitio, rejillas grandes y abiertas, y el género
> donde una rejilla ni siquiera es el modelo correcto — el plataformas. No repite lo básico de
> A*: para eso está [08 · Tower Defense](./08%20-%20Tower%20Defense.md) (`mp_grid`) y
> `06/scr_grid_pathfinding.gml` (`GridPonderado`). Tampoco repite el movimiento: para eso está
> [23 · IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md).

---

## 1 · Visión general

Cuatro problemas concretos, cada uno con una técnica que lo resuelve y que **no** está en
`06/scr_grid_pathfinding.gml`:

| Problema | Técnica | Coste | Dónde está |
|---|---|---|---|
| Cientos de unidades van al MISMO destino | **Campo de flujo** (*flow field*) | O(celdas) una vez, O(1) por unidad y frame | §3 |
| Rejilla grande, muy abierta, coste uniforme | **Jump Point Search** (JPS) | Salta decenas de celdas idénticas de un tirón | §4 |
| El nivel es un plataformas: no hay "celda libre = paso válido" | **Grafo de plataformas** | Precomputado una vez al cargar el nivel | §5 |
| La ruta de una rejilla sale en escalera | **Suavizado + steering** | Una pasada lineal sobre la ruta ya calculada | §6 |

```
┌─────────────────────────────────────────────────────────────────────┐
│ ¿Cuántas unidades comparten destino AHORA MISMO?                    │
│   1 a ~30, cada una a su sitio  → Grid / GridPonderado (ya existen)  │
│   Cientos, al MISMO sitio       → Campo de flujo (§3)                │
├─────────────────────────────────────────────────────────────────────┤
│ ¿La rejilla es grande (>100×100) y mayormente abierta?               │
│   Sí, coste uniforme            → JPS sobre GridPonderado (§4)       │
│   No (pesos por celda de verdad) → GridPonderado.buscar() (A*)       │
├─────────────────────────────────────────────────────────────────────┤
│ ¿El movimiento incluye saltar entre plataformas?                     │
│   Sí                            → Grafo de plataformas (§5)          │
├─────────────────────────────────────────────────────────────────────┤
│ ¿La ruta resultante se ve en escalera / se mueve a tirones?          │
│   Sí                            → Suavizar + Arrive (§6)             │
└─────────────────────────────────────────────────────────────────────┘
```

> 🔺 Ninguna de las cuatro sustituye a `Grid`/`GridPonderado`: son ampliaciones para casos que
> se salen de su rango. Si `mp_grid_path` ya te resuelve el juego, quédate ahí — es la opción
> más barata y ya está escrita, probada y compilando en `06/scr_grid_pathfinding.gml`.

---

## 2 · Campo de flujo (*flow field*)

### 2.1 · La idea: un BFS, no un A* por unidad

[13 · Estrategia y gestión §4.1 y §8.1](./13%20-%20Estrategia%20y%20gestión.md) menciona el
campo de flujo dos veces como "la solución profesional" para RTS con cientos de unidades, sin
darlo. Aquí está.

Un `mp_grid_path` por unidad y por frame es O(unidades × celdas): con 100 unidades es
literalmente 100 búsquedas A* idénticas hacia el mismo punto. El campo de flujo invierte el
problema: en vez de que cada unidad pregunte "¿cómo llego?", **se calcula UNA vez, para toda la
rejilla, hacia dónde hay que moverse desde cada celda** para llegar al destino por el camino más
corto. Después, cada unidad solo consulta su celda — una lectura de array, sin buscar nada.

El algoritmo es una **búsqueda en anchura (BFS) desde el destino hacia fuera**: la distancia en
número de pasos crece en anillos concéntricos, y cada celda guarda de qué vecino la descubrió
—que es, mirado al revés, hacia dónde tiene que ir una unidad que esté ahí—. BFS (no Dijkstra)
porque el coste de moverse es uniforme: 1 por celda. Si tu terreno tiene coste por celda de
verdad (barro, agua), el campo de flujo no es la herramienta — usa `GridPonderado.buscar()` por
unidad, o acepta la aproximación de tratar el terreno caro como "más lento de cruzar" en el
movimiento, no en la búsqueda.

### 2.2 · Cuándo recalcular (y cuándo NO)

| Evento | ¿Recalcular? | Por qué |
|---|---|---|
| Cambia el destino (nueva orden de movimiento, nuevo punto de reunión) | **Sí**, una vez | El campo entero depende de hacia dónde apunta |
| Se coloca o destruye un obstáculo (edificio, torre, muro) | **Sí**, una vez, después del cambio | Las rutas alrededor del obstáculo cambian |
| Una unidad se mueve | **No** | Todas las unidades comparten el mismo campo; nada que recalcular por unidad |
| Cada frame, "por si acaso" | **No** | Deshace la ventaja entera: vuelves a pagar el BFS completo 60 veces por segundo |
| El mapa es grande (>150×150) y el destino cambia a menudo | Con cuidado | Usa un flag `sucio` y recalcula una vez por lote de órdenes, no una vez por clic |
| Hay varios destinos frecuentes (puntos de reunión de un RTS) | Cachea un campo por destino | Recalcular cuesta lo mismo la primera vez; si el destino se repite, no vuelvas a pagarlo |

> 💡 **La garantía del campo de flujo es "una búsqueda para todas las unidades".** El error más
> caro es romper esa garantía sin darse cuenta: si acabas llamando a `recalcular()` una vez por
> unidad o una vez por frame, has vuelto a pagar el coste de un A* por unidad, solo que peor
> escrito.

### 2.3 · Código: `FlowField`

```gml
// ============================================================================
// scr_flow_field.gml (o pégalo al final de scr_grid_pathfinding.gml)
//
// Campo de flujo: UN BFS desde el destino calcula, para TODA la rejilla,
// hacia qué celda vecina moverse. Coste O(celdas) una vez; O(1) por unidad y
// frame después. Es la técnica que 04/13 §4.1 y §8.1 recomiendan sin darla.
//
// SOLO sirve con coste uniforme (transitable = 1, bloqueado = -1). Si
// necesitas coste por celda (barro, agua), usa `GridPonderado` en su lugar.
//
// Funciones nativas usadas (verificadas con `buscar.py`):
//   ds_queue_create, ds_queue_enqueue, ds_queue_dequeue, ds_queue_empty,
//   ds_queue_destroy, array_create, array_resize, array_length, array_push,
//   floor, ceil, max, point_distance, draw_line
//
// USO RAPIDO
//   // Al cargar el nivel:
//   global.campo = new FlowField(32);
//   global.campo.bloquear_objeto(obj_muro);
//   global.campo.recalcular_px(punto_reunion.x, punto_reunion.y);
//
//   // Step de cada unidad (cientos de ellas, sin coste extra):
//   if (!global.campo.llegado(x, y)) {
//       var _dir = global.campo.vector_en(x, y);
//       x += _dir.x * velocidad;
//       y += _dir.y * velocidad;
//   }
//
//   // Cuando se coloque/destruya un edificio:
//   global.campo.bloquear_objeto(obj_edificio_nuevo);
//   global.campo.recalcular_px(punto_reunion.x, punto_reunion.y);   // UNA vez
// ============================================================================

/// @function FlowField(_tamano_celda, _ancho, _alto, _izq, _arr)
/// @desc    Campo de flujo sobre una rejilla uniforme. Misma convención de
///          columnas/filas/celda que `Grid` y `GridPonderado`
///          (`06/scr_grid_pathfinding.gml`): se puede levantar sobre el mismo
///          plano de coordenadas sin traducir nada.
/// @param   {Real} _tamano_celda  Píxeles de lado de cada celda.
/// @param   {Real} _ancho         Ancho en píxeles (por defecto room_width).
/// @param   {Real} _alto          Alto en píxeles (por defecto room_height).
/// @param   {Real} _izq           Origen X.
/// @param   {Real} _arr           Origen Y.
function FlowField(_tamano_celda, _ancho = -1, _alto = -1, _izq = 0, _arr = 0) constructor {
    celda    = max(_tamano_celda, 1);
    izq      = _izq;
    arr      = _arr;
    ancho    = (_ancho <= 0) ? room_width  : _ancho;
    alto     = (_alto  <= 0) ? room_height : _alto;
    columnas = ceil(ancho / celda);
    filas    = ceil(alto  / celda);

    var _total = columnas * filas;
    bloqueada   = array_create(_total, false);
    distancia   = array_create(_total, -1);   // -1 = sin datos / inalcanzable
    direccion   = array_create(_total, -1);   // índice en _DC/_DF, o -1
    destino_col = -1;
    destino_fil = -1;
    sucio       = true;   // hay que recalcular antes de fiarse del campo

    // 8 direcciones ordenadas en PARES opuestos consecutivos: (0,1) (2,3)
    // (4,5) (6,7). `_OPUESTO[i]` es el índice de la dirección contraria a `i`.
    static _DC = [ 1,-1, 0, 0, 1,-1, 1,-1];
    static _DF = [ 0, 0, 1,-1, 1,-1,-1, 1];
    static _OPUESTO = [1, 0, 3, 2, 5, 4, 7, 6];

    /// @desc Marca o despeja una celda como obstáculo. Ensucia el campo: no
    ///       recalcula solo. Llama a `recalcular()` cuando termines de tocar
    ///       el mapa (una vez, no celda a celda).
    /// @param {Real} _col
    /// @param {Real} _fil
    /// @param {Bool} [_bloq]  True para bloquear, false para despejar.
    static bloquear = function(_col, _fil, _bloq = true) {
        if (_col < 0 || _fil < 0 || _col >= columnas || _fil >= filas) { return; }
        bloqueada[_fil * columnas + _col] = _bloq;
        sucio = true;
    };

    /// @desc Marca todas las instancias de un objeto como obstáculo. Es el
    ///       equivalente de `Grid.add_object()` para el campo de flujo: no
    ///       hay una función nativa que lo haga, así que se recorre a mano.
    /// @param {Asset.GMObject} _obj
    static bloquear_objeto = function(_obj) {
        var _campo = self;   // dentro del `with`, `self` pasa a ser cada instancia de _obj
        with (_obj) {
            var _c1 = floor((bbox_left   - _campo.izq)  / _campo.celda);
            var _c2 = floor((bbox_right  - _campo.izq)  / _campo.celda);
            var _f1 = floor((bbox_top    - _campo.arr)  / _campo.celda);
            var _f2 = floor((bbox_bottom - _campo.arr)  / _campo.celda);
            for (var _f = _f1; _f <= _f2; _f++) {
                for (var _c = _c1; _c <= _c2; _c++) {
                    _campo.bloquear(_c, _f);
                }
            }
        }
    };

    /// @desc Recalcula el campo entero con BFS desde (_col,_fil). Llámalo
    ///       solo cuando cambie el DESTINO o los obstáculos — nunca por
    ///       frame ni por unidad (ver §2.2).
    /// @param {Real} _col
    /// @param {Real} _fil
    /// @returns {Bool}  false si el destino está bloqueado o fuera de rango.
    static recalcular = function(_col, _fil) {
        if (_col < 0 || _fil < 0 || _col >= columnas || _fil >= filas) { return false; }
        if (bloqueada[_fil * columnas + _col]) { return false; }

        destino_col = _col;
        destino_fil = _fil;

        var _total = columnas * filas;
        array_resize(distancia, _total);
        array_resize(direccion, _total);
        for (var _i = 0; _i < _total; _i++) { distancia[_i] = -1; direccion[_i] = -1; }

        var _cola   = ds_queue_create();
        var _inicio = _fil * columnas + _col;
        distancia[_inicio] = 0;
        ds_queue_enqueue(_cola, _inicio);

        while (!ds_queue_empty(_cola)) {
            var _actual = ds_queue_dequeue(_cola);
            var _c = _actual mod columnas;
            var _f = _actual div columnas;

            for (var _i = 0; _i < 8; _i++) {
                var _cv = _c + _DC[_i];
                var _fv = _f + _DF[_i];
                if (_cv < 0 || _fv < 0 || _cv >= columnas || _fv >= filas) { continue; }

                var _iv = _fv * columnas + _cv;
                if (bloqueada[_iv] || distancia[_iv] != -1) { continue; }

                // Sin corte de esquina: en diagonal, los DOS ortogonales
                // tienen que estar libres (misma regla que
                // `GridPonderado.buscar()`).
                if (_DC[_i] != 0 && _DF[_i] != 0) {
                    var _io1 = _f * columnas + _cv;
                    var _io2 = _fv * columnas + _c;
                    if (bloqueada[_io1] || bloqueada[_io2]) { continue; }
                }

                distancia[_iv] = distancia[_actual] + 1;
                // La celda descubierta apunta HACIA QUIEN LA DESCUBRIÓ, que
                // está un paso más cerca del destino: dirección opuesta a la
                // que usamos para llegar a ella.
                direccion[_iv] = _OPUESTO[_i];
                ds_queue_enqueue(_cola, _iv);
            }
        }

        ds_queue_destroy(_cola);
        sucio = false;
        return true;
    };

    /// @desc Atajo: recalcula dando el destino en PIXELES.
    /// @param {Real} _x
    /// @param {Real} _y
    /// @returns {Bool}
    static recalcular_px = function(_x, _y) {
        var _c = floor((_x - izq) / celda);
        var _f = floor((_y - arr) / celda);
        return recalcular(_c, _f);
    };

    /// @desc Vector de movimiento normalizado para la celda que contiene
    ///       (_x,_y). `{x:0, y:0}` si no hay datos (fuera de rango, celda
    ///       bloqueada o inalcanzable) o si ya es la celda destino.
    /// @param {Real} _x
    /// @param {Real} _y
    /// @returns {Struct}  { x, y }
    static vector_en = function(_x, _y) {
        var _col = floor((_x - izq) / celda);
        var _fil = floor((_y - arr) / celda);
        if (_col < 0 || _fil < 0 || _col >= columnas || _fil >= filas) { return { x: 0, y: 0 }; }

        var _i = _fil * columnas + _col;
        if (direccion[_i] == -1) { return { x: 0, y: 0 }; }

        var _dc = _DC[direccion[_i]];
        var _df = _DF[direccion[_i]];
        var _len = point_distance(0, 0, _dc, _df);   // 1 o raíz de 2
        return { x: _dc / _len, y: _df / _len };
    };

    /// @desc ¿La celda de (_x,_y) es ya la celda destino?
    /// @param {Real} _x
    /// @param {Real} _y
    /// @returns {Bool}
    static llegado = function(_x, _y) {
        var _col = floor((_x - izq) / celda);
        var _fil = floor((_y - arr) / celda);
        return (_col == destino_col && _fil == destino_fil);
    };

    /// @desc Dibuja una flecha por celda con la dirección del campo.
    ///       LLAMALO EN UN EVENTO DRAW. Solo para depurar: barato de más en
    ///       rejillas grandes si lo dejas encendido en producción.
    static draw_debug = function() {
        for (var _f = 0; _f < filas; _f++) {
            for (var _c = 0; _c < columnas; _c++) {
                var _i = _f * columnas + _c;
                if (direccion[_i] == -1) { continue; }
                var _cx = izq + _c * celda + celda / 2;
                var _cy = arr + _f * celda + celda / 2;
                var _dc = _DC[direccion[_i]];
                var _df = _DF[direccion[_i]];
                draw_line(_cx, _cy, _cx + _dc * celda * 0.35, _cy + _df * celda * 0.35);
            }
        }
    };
}
```

### 2.4 · Uso desde una unidad

```gml
/// Create de la unidad — nada que crear: el campo es global y compartido.

/// Step de la unidad — O(1), sin importar cuántas unidades lo compartan.
if (!global.campo.llegado(x, y)) {
    var _dir = global.campo.vector_en(x, y);
    x += _dir.x * velocidad_unidad;
    y += _dir.y * velocidad_unidad;
}
```

> 🔺 **El movimiento discreto celda-a-celda se nota entre celdas grandes.** Si las unidades
> "tiemblan" al cruzar el borde de una celda, mezcla el vector de la celda actual con el de la
> celda hacia la que te mueves (`lerp` entre los dos `vector_en()`), o usa una celda más pequeña.
> No hace falta suavizar la ruta como en §6: el campo de flujo no produce una ruta discreta, es
> un vector continuo por posición.

---

## 3 · Jump Point Search sobre `GridPonderado`

### 3.1 · El problema que resuelve

A* expande una celda a la vez. En una rejilla grande y mayormente abierta (un mapa exterior, una
arena), la mayoría de esas celdas son idénticas: no hay ninguna razón para pararse en cada una.
**Jump Point Search** (JPS) es una poda de A*: en vez de expandir el vecino inmediato, "salta" en
línea recta hasta el primer punto donde ocurre algo interesante — un **vecino forzado** (un
obstáculo al lado que obliga a decidir), el destino, o un callejón sin salida. En una rejilla
abierta de 200×200 eso puede significar saltar 40 celdas de un tirón donde A* habría expandido
las 40 una a una.

> ⚠️ JPS es un algoritmo publicado (Harabor y Grastien, "Online Graph Pruning for Pathfinding on
> Grid Maps", 2011): el concepto y sus reglas de poda son de dominio público y muy citados en la
> literatura de *pathfinding* para juegos. Esta sesión no tenía acceso al paper original
> (WebSearch agotado) ni a un banco de pruebas para validar la implementación de abajo casilla
> por casilla: está escrita a partir de las reglas de poda estándar y **compila**, pero
> **verifica su comportamiento a ojo con un `draw_debug` o unos cuantos casos de prueba antes de
> confiar en ella en producción** — un bug de poda en JPS no rompe la compilación, produce una
> ruta subóptima o, en el peor caso, no encuentra una ruta que sí existe.

### 3.2 · La condición que no puedes saltarte: coste uniforme

La poda de JPS asume que **toda celda transitable cuesta lo mismo** (normalmente 1, `sqrt(2)` en
diagonal). La prueba de "vecino forzado" es válida precisamente porque, si todas las celdas
cuestan igual, saltarse las intermedias no cambia el coste total del camino. En cuanto una celda
cuesta 4 y la de al lado cuesta 1, esa garantía desaparece: JPS podría saltar por encima de la
casilla barata que en realidad hacía el camino más corto.

**Regla práctica:** si tu `GridPonderado` tiene celdas con `coste != 1` de verdad (no solo
bloqueado/libre), no uses JPS — usa `GridPonderado.buscar()` (Dijkstra/A* normal, ya escrito y
verificado). JPS es exclusivamente para el caso "libre cuesta 1, bloqueado es intransitable",
que sigue siendo el caso más común en rejillas grandes y abiertas.

### 3.3 · Código: `GridJPS`

`GridJPS` **no duplica la rejilla**: recibe una `GridPonderado` ya creada
(`06/scr_grid_pathfinding.gml`) y añade el algoritmo de búsqueda por encima, leyendo su
`costes` para saber qué está bloqueado.

```gml
// ============================================================================
// scr_grid_jps.gml
//
// Jump Point Search sobre una GridPonderado ya creada (06/scr_grid_pathfinding.gml).
// SOLO válido con coste uniforme: ver §3.2. Con pesos de verdad, usa
// `GridPonderado.buscar()`.
//
// Funciones nativas usadas (verificadas con `buscar.py`):
//   ds_priority_create, ds_priority_add, ds_priority_delete_min,
//   ds_priority_empty, ds_priority_destroy, array_create, array_length,
//   array_push, is_undefined, sign, abs, max, point_distance
//
// USO RAPIDO
//   var _grid = new GridPonderado(32);
//   _grid.bloquear(5, 3);
//   var _jps = new GridJPS(_grid);
//   var _ruta = _jps.buscar(0, 0, 40, 30);        // en CELDAS
//   var _ruta_px = _jps.buscar_px(x, y, obj_jugador.x, obj_jugador.y);
// ============================================================================

/// @func __jps_transitable(_grid, _c, _f)
/// @desc ¿Es transitable la celda? Fuera de rango cuenta como bloqueada.
/// @param {Struct.GridPonderado} _grid
/// @param {Real} _c
/// @param {Real} _f
/// @return {Bool}
function __jps_transitable(_grid, _c, _f)
{
    if (_c < 0 || _f < 0 || _c >= _grid.columnas || _f >= _grid.filas) { return false; }
    return (_grid.costes[_f][_c] >= 0);
}

/// @func __jps_saltar(_grid, _c, _f, _dc, _df, _c2, _f2)
/// @desc Avanza en línea recta desde (_c,_f) en dirección (_dc,_df) hasta el
///       siguiente "punto de salto": el destino, un vecino forzado, o
///       ninguno (callejón sin salida). Función libre (no un método de
///       struct) para que la recursión del caso diagonal sea una llamada
///       normal, sin depender de cómo resuelve GameMaker una llamada de un
///       método a sí mismo.
/// @param {Struct.GridPonderado} _grid
/// @param {Real} _c   Columna de salida.
/// @param {Real} _f   Fila de salida.
/// @param {Real} _dc  Paso en columnas (-1, 0 o 1).
/// @param {Real} _df  Paso en filas (-1, 0 o 1).
/// @param {Real} _c2  Columna del destino (para poder pararse si es él).
/// @param {Real} _f2  Fila del destino.
/// @return {Struct|Undefined}  { col, fil } del punto de salto, o undefined.
function __jps_saltar(_grid, _c, _f, _dc, _df, _c2, _f2)
{
    var _x = _c, _y = _f;

    while (true)
    {
        _x += _dc;
        _y += _df;

        if (!__jps_transitable(_grid, _x, _y)) { return undefined; }
        if (_x == _c2 && _y == _f2) { return { col: _x, fil: _y }; }

        if (_dc != 0 && _df != 0)
        {
            // Diagonal: vecino forzado si el ortogonal está bloqueado pero
            // la casilla "en diagonal desde ahí" está libre.
            if ((__jps_transitable(_grid, _x - _dc, _y + _df) && !__jps_transitable(_grid, _x - _dc, _y)) ||
                (__jps_transitable(_grid, _x + _dc, _y - _df) && !__jps_transitable(_grid, _x, _y - _df)))
            {
                return { col: _x, fil: _y };
            }
            // Los dos ortogonales bloqueados: no se puede cortar la esquina.
            if (!__jps_transitable(_grid, _x - _dc, _y) && !__jps_transitable(_grid, _x, _y - _df))
            {
                return undefined;
            }
            // Sub-saltos por los dos ejes rectos: si cualquiera encuentra un
            // punto de salto, (_x,_y) también lo es.
            if (!is_undefined(__jps_saltar(_grid, _x, _y, _dc, 0, _c2, _f2))) { return { col: _x, fil: _y }; }
            if (!is_undefined(__jps_saltar(_grid, _x, _y, 0, _df, _c2, _f2))) { return { col: _x, fil: _y }; }
        }
        else if (_dc != 0)
        {
            // Horizontal: vecino forzado arriba/abajo.
            if ((__jps_transitable(_grid, _x + _dc, _y + 1) && !__jps_transitable(_grid, _x, _y + 1)) ||
                (__jps_transitable(_grid, _x + _dc, _y - 1) && !__jps_transitable(_grid, _x, _y - 1)))
            {
                return { col: _x, fil: _y };
            }
        }
        else
        {
            // Vertical: vecino forzado izquierda/derecha.
            if ((__jps_transitable(_grid, _x + 1, _y + _df) && !__jps_transitable(_grid, _x + 1, _y)) ||
                (__jps_transitable(_grid, _x - 1, _y + _df) && !__jps_transitable(_grid, _x - 1, _y)))
            {
                return { col: _x, fil: _y };
            }
        }
        // Ni forzado ni destino: seguir en línea recta (vuelve a empezar
        // el `while`, que es la versión iterativa de "seguir saltando").
    }
}

/// @func __jps_vecinos_podados(_grid, _c, _f, _pc, _pf, _diagonal)
/// @desc Direcciones a explorar desde (_c,_f). Sin padre (nodo de salida):
///       todas las transitables. Con padre: solo las "naturales" más las
///       "forzadas" por el padre — la poda que hace rápido a JPS.
/// @param {Struct.GridPonderado} _grid
/// @param {Real} _c
/// @param {Real} _f
/// @param {Real|Undefined} _pc  Columna del padre, o undefined si es el origen.
/// @param {Real|Undefined} _pf  Fila del padre.
/// @param {Bool} _diagonal
/// @return {Array<Struct>}  Array de { dc, df }.
function __jps_vecinos_podados(_grid, _c, _f, _pc, _pf, _diagonal)
{
    var _dirs = [];

    if (is_undefined(_pc))
    {
        var _dc8 = [ 1,-1, 0, 0, 1,-1, 1,-1];
        var _df8 = [ 0, 0, 1,-1, 1,-1,-1, 1];
        var _max = _diagonal ? 8 : 4;
        for (var _i = 0; _i < _max; _i++)
        {
            if (__jps_transitable(_grid, _c + _dc8[_i], _f + _df8[_i]))
            {
                array_push(_dirs, { dc: _dc8[_i], df: _df8[_i] });
            }
        }
        return _dirs;
    }

    var _dx = sign(_c - _pc);
    var _dy = sign(_f - _pf);

    if (_dx != 0 && _dy != 0)
    {
        if (__jps_transitable(_grid, _c, _f + _dy)) { array_push(_dirs, { dc: 0, df: _dy }); }
        if (__jps_transitable(_grid, _c + _dx, _f)) { array_push(_dirs, { dc: _dx, df: 0 }); }
        if (__jps_transitable(_grid, _c + _dx, _f + _dy)) { array_push(_dirs, { dc: _dx, df: _dy }); }
        if (!__jps_transitable(_grid, _c - _dx, _f) && __jps_transitable(_grid, _c, _f + _dy))
        {
            array_push(_dirs, { dc: -_dx, df: _dy });
        }
        if (!__jps_transitable(_grid, _c, _f - _dy) && __jps_transitable(_grid, _c + _dx, _f))
        {
            array_push(_dirs, { dc: _dx, df: -_dy });
        }
    }
    else if (_dx != 0)
    {
        if (__jps_transitable(_grid, _c + _dx, _f)) { array_push(_dirs, { dc: _dx, df: 0 }); }
        if (!__jps_transitable(_grid, _c, _f + 1) && __jps_transitable(_grid, _c + _dx, _f + 1))
        {
            array_push(_dirs, { dc: _dx, df: 1 });
        }
        if (!__jps_transitable(_grid, _c, _f - 1) && __jps_transitable(_grid, _c + _dx, _f - 1))
        {
            array_push(_dirs, { dc: _dx, df: -1 });
        }
    }
    else
    {
        if (__jps_transitable(_grid, _c, _f + _dy)) { array_push(_dirs, { dc: 0, df: _dy }); }
        if (!__jps_transitable(_grid, _c + 1, _f) && __jps_transitable(_grid, _c + 1, _f + _dy))
        {
            array_push(_dirs, { dc: 1, df: _dy });
        }
        if (!__jps_transitable(_grid, _c - 1, _f) && __jps_transitable(_grid, _c - 1, _f + _dy))
        {
            array_push(_dirs, { dc: -1, df: _dy });
        }
    }

    return _dirs;
}

/// @function GridJPS(_grid, _diagonal)
/// @desc    Jump Point Search sobre una `GridPonderado` YA CREADA (ver §3.2:
///          solo válido con coste uniforme). Mismo formato de entrada/salida
///          que `GridPonderado.buscar()`: se pueden intercambiar.
/// @param   {Struct.GridPonderado} _grid
/// @param   {Bool} [_diagonal]  Permitir diagonales (por defecto true).
function GridJPS(_grid, _diagonal = true) constructor {
    grid     = _grid;
    diagonal = _diagonal;

    /// @desc Busca la ruta más corta entre dos CELDAS.
    /// @param {Real} _c1
    /// @param {Real} _f1
    /// @param {Real} _c2
    /// @param {Real} _f2
    /// @returns {Array<Struct>}  Array de { x, y } en PIXELES, vacío si no hay ruta.
    static buscar = function(_c1, _f1, _c2, _f2) {
        var _resultado = [];

        if (!__jps_transitable(grid, _c1, _f1) || !__jps_transitable(grid, _c2, _f2)) { return _resultado; }
        if (_c1 == _c2 && _f1 == _f2) {
            array_push(_resultado, grid.cell_to_px(_c1, _f1));
            return _resultado;
        }

        var _total   = grid.columnas * grid.filas;
        var _g       = array_create(_total, -1);
        var _padre   = array_create(_total, -1);
        var _cerrado = array_create(_total, false);
        var _abiertos = ds_priority_create();

        var _inicio  = _f1 * grid.columnas + _c1;
        var _destino = _f2 * grid.columnas + _c2;
        _g[_inicio] = 0;

        var _h0 = diagonal ? max(abs(_c1 - _c2), abs(_f1 - _f2)) : (abs(_c1 - _c2) + abs(_f1 - _f2));
        ds_priority_add(_abiertos, _inicio, _h0);

        var _encontrado = false;

        while (!ds_priority_empty(_abiertos)) {
            var _actual = ds_priority_delete_min(_abiertos);
            if (_actual == _destino) { _encontrado = true; break; }
            if (_cerrado[_actual]) { continue; }
            _cerrado[_actual] = true;

            var _col_a = _actual mod grid.columnas;
            var _fil_a = _actual div grid.columnas;

            var _hay_padre = (_padre[_actual] != -1);
            var _pc = _hay_padre ? (_padre[_actual] mod grid.columnas) : undefined;
            var _pf = _hay_padre ? (_padre[_actual] div grid.columnas) : undefined;

            var _dirs = __jps_vecinos_podados(grid, _col_a, _fil_a, _pc, _pf, diagonal);

            for (var _i = 0; _i < array_length(_dirs); _i++) {
                var _salto = __jps_saltar(grid, _col_a, _fil_a, _dirs[_i].dc, _dirs[_i].df, _c2, _f2);
                if (is_undefined(_salto)) { continue; }

                var _indice_v = _salto.fil * grid.columnas + _salto.col;
                if (_cerrado[_indice_v]) { continue; }

                // Distancia REAL saltada (varias celdas de golpe), no 1.
                var _paso = point_distance(_col_a, _fil_a, _salto.col, _salto.fil);
                var _nuevo_g = _g[_actual] + _paso;

                if (_g[_indice_v] == -1 || _nuevo_g < _g[_indice_v]) {
                    _g[_indice_v]     = _nuevo_g;
                    _padre[_indice_v] = _actual;
                    var _h = diagonal
                        ? max(abs(_salto.col - _c2), abs(_salto.fil - _f2))
                        : (abs(_salto.col - _c2) + abs(_salto.fil - _f2));
                    ds_priority_add(_abiertos, _indice_v, _nuevo_g + _h);
                }
            }
        }

        ds_priority_destroy(_abiertos);
        if (!_encontrado) { return _resultado; }

        // Reconstrucción: entre dos puntos de salto puede haber varias
        // celdas intermedias en línea recta. Se rellenan para que el
        // resultado tenga el mismo formato "una celda, un punto" que
        // `GridPonderado.buscar()`.
        var _cadena = [];
        var _nodo = _destino;
        while (_nodo != -1) { array_push(_cadena, _nodo); _nodo = _padre[_nodo]; }

        for (var _k = array_length(_cadena) - 1; _k > 0; _k--) {
            var _de = _cadena[_k];
            var _a  = _cadena[_k - 1];
            var _dc_ = _de mod grid.columnas, _df_ = _de div grid.columnas;
            var _ac  = _a  mod grid.columnas, _af  = _a  div grid.columnas;
            var _pasos = max(abs(_ac - _dc_), abs(_af - _df_));
            var _sx = sign(_ac - _dc_), _sy = sign(_af - _df_);
            for (var _p = 0; _p < _pasos; _p++) {
                array_push(_resultado, grid.cell_to_px(_dc_ + _sx * _p, _df_ + _sy * _p));
            }
        }
        array_push(_resultado, grid.cell_to_px(_c2, _f2));

        return _resultado;
    };

    /// @desc Atajo: busca dando las coordenadas en PIXELES.
    /// @param {Real} _x1
    /// @param {Real} _y1
    /// @param {Real} _x2
    /// @param {Real} _y2
    /// @returns {Array<Struct>}
    static buscar_px = function(_x1, _y1, _x2, _y2) {
        var _a = grid.px_to_cell(_x1, _y1);
        var _b = grid.px_to_cell(_x2, _y2);
        return buscar(_a.col, _a.fil, _b.col, _b.fil);
    };
}
```

### 3.4 · Cuándo usarlo (y cuándo no)

| Situación | ¿JPS? |
|---|---|
| Rejilla grande (>100×100), pocos obstáculos, coste uniforme | Sí — es donde más gana |
| Rejilla pequeña (<40×40) | No merece la pena: `GridPonderado.buscar()` ya es instantáneo |
| Coste por celda real (barro, agua, carretera) | **No** — usa `GridPonderado.buscar()` (§3.2) |
| Rejilla llena de obstáculos pequeños y repartidos | JPS pierde ventaja: cada casilla se convierte en vecino forzado y apenas se salta nada |
| Necesitas la ruta óptima garantizada y tienes tiempo de sobra por frame | `GridPonderado.buscar()`: menos código, misma garantía de optimalidad, sin la superficie de bugs de una poda hecha a mano |

---

## 4 · Pathfinding en plataformas

### 4.1 · Por qué `mp_grid` no sirve aquí

`mp_grid`/`GridPonderado` asumen que **"celda libre" es sinónimo de "paso válido"**: si la celda
de al lado no está bloqueada, puedes entrar en ella. En un plataformas eso es falso: moverse no
es entrar en la celda de al lado, es **una parábola con velocidad horizontal y gravedad**, y
"libre" no basta — hace falta que el arco de salto llegue físicamente hasta ahí. Una rejilla no
tiene manera de representar "puedo saltar este hueco de 96 px pero no uno de 160", ni "puedo
caer 200 px sin morir pero no subir esa altura de un salto".

La solución estándar es no usar una rejilla: un **grafo** donde los nodos son sitios donde te
puedes parar (los extremos de las plataformas) y las aristas son las tres acciones que conectan
dos nodos: **caminar** (dentro de la misma plataforma), **saltar** (con impulso) y **caer** (sin
impulso, solo gravedad). El grafo asume plataformas **de un sentido** (igual que
[04 · 01 §4.7](./01%20-%20Plataformas%202D.md)): un salto puede pasar por debajo de otra
plataforma sin chocar contra ella. Si tu nivel tiene plataformas sólidas por los cuatro lados
(no solo de un sentido), añade tú una comprobación extra de "techo" al simular el arco (§4.3): el
grafo tal como está aquí no la incluye.

> ⚠️ El diseño de este grafo es propio de la biblioteca: no reproduce un algoritmo publicado
> concreto (a diferencia de JPS en §3), es una construcción directa a partir de la física de
> salto que ya usa [04 · 01](./01%20-%20Plataformas%202D.md). Verifícalo con `draw_debug()`
> (§4.4) sobre tu nivel real antes de confiar en él para IA de combate o de sigilo.

### 4.2 · El grafo de plataformas: nodos y tres tipos de arista

Cada plataforma se representa como `{ x1, y, x2 }` (borde izquierdo, altura de la superficie,
borde derecho — `x1 < x2`). Por cada plataforma se crean dos nodos, uno por extremo. Las
aristas:

| Tipo | Cuándo se genera | Coste |
|---|---|---|
| **Caminar** | Los dos extremos de la MISMA plataforma | Distancia entre extremos |
| **Saltar** | Lanzando el arco de salto (§4.3) desde un extremo hacia fuera, aterriza en OTRA plataforma | Frames simulados hasta el aterrizaje |
| **Caer** | Igual que saltar, pero con velocidad vertical inicial 0 (te sales del borde caminando) | Frames simulados hasta el aterrizaje |

Cada extremo solo lanza el arco **hacia fuera** de su propia plataforma (el extremo izquierdo
prueba hacia la izquierda, el derecho hacia la derecha): no tiene sentido "saltar" dentro de la
plataforma en la que ya estás, eso es caminar. Si necesitas una plataforma con más de dos puntos
de salida (una plataforma larga con un hueco en el medio, o una forma en U), añade más entradas
al array de plataformas — el algoritmo no asume que solo hay dos nodos por plataforma real,
asume dos nodos por **entrada** del array.

### 4.3 · Simular el arco de salto

En vez de resolver la parábola con una fórmula cerrada (complicada aquí porque
[04 · 01 §4.2](./01%20-%20Plataformas%202D.md) usa **gravedad asimétrica**: distinta subiendo
que bajando), se simula el salto **frame a frame, exactamente como lo mueve el jugador de
verdad**: así el grafo predice solo saltos que el jugador puede completar de verdad, con las
mismas constantes (`JUMP_SPEED`, `GRAV_RISE`, `GRAV_FALL`, `VELY_TERMINAL` de
[04 · 01 §5.0](./01%20-%20Plataformas%202D.md)).

```gml
/// @func simular_arco_salto(_vx, _v_salto, _grav_subida, _grav_bajada, _v_terminal, _pasos_max)
/// @desc Traza un salto frame a frame con gravedad asimétrica, igual que
///       04·01 §5.3 (gravedad aplicada a la velocidad ANTES de mover). Sirve
///       tanto para "saltar" (con _v_salto > 0) como para "caer" (_v_salto = 0).
/// @param {Real} _vx            Velocidad horizontal CONSTANTE (px/frame).
///                              Aproximación: 04·01 acelera hasta ahí con
///                              `lerp`, así que el arco real llega un poco
///                              menos lejos en el primer tramo. Compénsalo
///                              con un margen de seguridad (§4.4).
/// @param {Real} _v_salto       Velocidad vertical de despegue (positiva).
/// @param {Real} _grav_subida   Gravedad mientras la velocidad vertical < 0
///                              (subiendo). `GRAV_RISE` de 04·01.
/// @param {Real} _grav_bajada   Gravedad mientras >= 0 (bajando). `GRAV_FALL`.
/// @param {Real} _v_terminal    Velocidad de caída máxima. `VELY_TERMINAL`.
/// @param {Real} [_pasos_max]   Frames máximos a simular (corta un salto que
///                              no aterriza nunca, p. ej. hacia un abismo).
/// @return {Array<Struct>}  Array de offsets {x, y} relativos al despegue,
///          uno por frame simulado.
function simular_arco_salto(_vx, _v_salto, _grav_subida, _grav_bajada, _v_terminal, _pasos_max = 180)
{
    var _arco = [];
    var _x = 0, _y = 0;
    var _vy = -_v_salto;

    for (var _i = 0; _i < _pasos_max; _i++)
    {
        _vy = min(_vy + ((_vy < 0) ? _grav_subida : _grav_bajada), _v_terminal);
        _x += _vx;
        _y += _vy;
        array_push(_arco, { x: _x, y: _y });
    }

    return _arco;
}
```

### 4.4 · Código: `GrafoPlataformas`

```gml
// ============================================================================
// scr_grafo_plataformas.gml
//
// Grafo de navegación para un plataformas: nodos en los extremos de cada
// plataforma, aristas "caminar"/"saltar"/"caer" generadas simulando el arco
// de salto real del juego (§4.3). `mp_grid` no puede resolver esto (§4.1).
//
// Funciones nativas usadas (verificadas con `buscar.py`):
//   array_create, array_length, array_push, array_resize, point_distance,
//   ds_priority_create, ds_priority_add, ds_priority_delete_min,
//   ds_priority_empty, ds_priority_destroy, abs, min, max, sign
//
// USO RAPIDO
//   var _plataformas = [
//       { x1: 0,   x2: 200, y: 400 },
//       { x1: 280, x2: 420, y: 340 },   // hueco de 80 px, algo más alta
//       { x1: 500, x2: 700, y: 400 },
//   ];
//   grafo = new GrafoPlataformas(_plataformas);
//   grafo.generar(MOVE_SPEED_MAX, JUMP_SPEED, GRAV_RISE, GRAV_FALL, VELY_TERMINAL);
//
//   var _ruta = grafo.buscar_camino(0, 4);   // índices de NODO, no de plataforma
// ============================================================================

/// @function GrafoPlataformas(_plataformas, _margen_aterrizaje)
/// @desc    Red de navegación para pathfinding en un plataformas.
/// @param   {Array<Struct>} _plataformas  Array de { x1, x2, y }, x1 < x2.
///          `y` es la altura de la SUPERFICIE (donde se para el personaje).
/// @param   {Real} [_margen_aterrizaje]   Píxeles de margen en cada extremo
///          al aceptar un aterrizaje — ponlo a medio ancho del personaje
///          para que la IA no "resbale" del borde nada más aterrizar.
function GrafoPlataformas(_plataformas, _margen_aterrizaje = 8) constructor {
    plataformas       = _plataformas;
    margen_aterrizaje = _margen_aterrizaje;
    nodos      = [];   // { x, y, plataforma: índice en `plataformas` }
    aristas    = [];   // { desde, hasta: índices en `nodos`, tipo, coste }
    adyacencia = [];   // adyacencia[nodo] = array de índices en `aristas`

    for (var _p = 0; _p < array_length(plataformas); _p++) {
        var _pl = plataformas[_p];
        array_push(nodos, { x: _pl.x1, y: _pl.y, plataforma: _p });   // extremo izquierdo
        array_push(nodos, { x: _pl.x2, y: _pl.y, plataforma: _p });   // extremo derecho
    }

    /// @desc Aristas "caminar": los dos extremos de la MISMA plataforma, en
    ///       los dos sentidos.
    static _generar_caminar = function() {
        for (var _p = 0; _p < array_length(plataformas); _p++) {
            var _izq = _p * 2, _der = _p * 2 + 1;
            var _d = point_distance(nodos[_izq].x, nodos[_izq].y, nodos[_der].x, nodos[_der].y);
            array_push(aristas, { desde: _izq, hasta: _der, tipo: "caminar", coste: _d });
            array_push(aristas, { desde: _der, hasta: _izq, tipo: "caminar", coste: _d });
        }
    };

    /// @desc Lanza un arco (salto o caída) desde el nodo `_i` en la dirección
    ///       `_signo` (1 = derecha, -1 = izquierda) y añade una arista al
    ///       PRIMER aterrizaje válido.
    /// @param {Real} _i      Índice del nodo de salida.
    /// @param {Real} _signo  1 = derecha, -1 = izquierda.
    /// @param {Array<Struct>} _arco  Offsets de `simular_arco_salto()`.
    /// @param {String} _tipo "saltar" o "caer" (solo para depurar/dibujar).
    static _lanzar_arco = function(_i, _signo, _arco, _tipo) {
        var _n = nodos[_i];

        for (var _f = 0; _f < array_length(_arco); _f++) {
            var _px = _n.x + _arco[_f].x * _signo;
            var _py = _n.y + _arco[_f].y;

            for (var _p = 0; _p < array_length(plataformas); _p++) {
                if (_p == _n.plataforma) { continue; }   // no aterrizamos en la propia

                var _pl = plataformas[_p];
                if (_py >= _pl.y
                    && _px >= _pl.x1 + margen_aterrizaje
                    && _px <= _pl.x2 - margen_aterrizaje) {
                    var _destino = (abs(_px - _pl.x1) < abs(_px - _pl.x2)) ? (_p * 2) : (_p * 2 + 1);
                    array_push(aristas, {
                        desde: _i, hasta: _destino, tipo: _tipo,
                        coste: _f + point_distance(_px, _py, nodos[_destino].x, nodos[_destino].y) * 0.1
                    });
                    return true;
                }
            }
        }
        return false;   // no aterriza en _pasos_max frames: se descarta (hueco imposible)
    };

    /// @desc Reconstruye la lista de adyacencia a partir de `aristas`.
    static _reindexar = function() {
        adyacencia = array_create(array_length(nodos));
        for (var _i = 0; _i < array_length(adyacencia); _i++) { adyacencia[_i] = []; }
        for (var _e = 0; _e < array_length(aristas); _e++) {
            array_push(adyacencia[aristas[_e].desde], _e);
        }
    };

    /// @desc Genera TODAS las aristas. Llámalo una vez al cargar el nivel (o
    ///       cuando cambie el LAYOUT de plataformas: nunca por frame).
    /// @param {Real} _vx           `MOVE_SPEED_MAX` de 04·01 (con margen: ver §4.5).
    /// @param {Real} _v_salto      `JUMP_SPEED` de 04·01.
    /// @param {Real} _grav_subida  `GRAV_RISE` de 04·01.
    /// @param {Real} _grav_bajada  `GRAV_FALL` de 04·01.
    /// @param {Real} _v_terminal   `VELY_TERMINAL` de 04·01.
    static generar = function(_vx, _v_salto, _grav_subida, _grav_bajada, _v_terminal) {
        aristas = [];
        _generar_caminar();

        var _arco_salto = simular_arco_salto(_vx, _v_salto, _grav_subida, _grav_bajada, _v_terminal);
        var _arco_caida = simular_arco_salto(_vx, 0,        _grav_bajada, _grav_bajada, _v_terminal);

        for (var _p = 0; _p < array_length(plataformas); _p++) {
            var _izq = _p * 2, _der = _p * 2 + 1;
            _lanzar_arco(_izq, -1, _arco_salto, "saltar");
            _lanzar_arco(_izq, -1, _arco_caida, "caer");
            _lanzar_arco(_der,  1, _arco_salto, "saltar");
            _lanzar_arco(_der,  1, _arco_caida, "caer");
        }

        _reindexar();
    };

    /// @desc A* sobre el grafo. Mismo patrón que `GridPonderado.buscar()`
    ///       (`ds_priority`), sobre otro espacio de búsqueda.
    /// @param {Real} _nodo_origen
    /// @param {Real} _nodo_destino
    /// @returns {Array<Struct>}  Array de ARISTAS en orden (cada una dice su
    ///          `tipo` y el nodo `hasta`), o [] si no hay ruta.
    static buscar_camino = function(_nodo_origen, _nodo_destino) {
        var _n = array_length(nodos);
        var _g            = array_create(_n, -1);
        var _padre_arista = array_create(_n, -1);
        var _cerrado      = array_create(_n, false);
        var _abiertos = ds_priority_create();

        _g[_nodo_origen] = 0;
        ds_priority_add(_abiertos, _nodo_origen, point_distance(
            nodos[_nodo_origen].x, nodos[_nodo_origen].y,
            nodos[_nodo_destino].x, nodos[_nodo_destino].y));

        var _encontrado = false;
        while (!ds_priority_empty(_abiertos)) {
            var _actual = ds_priority_delete_min(_abiertos);
            if (_actual == _nodo_destino) { _encontrado = true; break; }
            if (_cerrado[_actual]) { continue; }
            _cerrado[_actual] = true;

            var _salientes = adyacencia[_actual];
            for (var _k = 0; _k < array_length(_salientes); _k++) {
                var _e = _salientes[_k];
                var _v = aristas[_e].hasta;
                if (_cerrado[_v]) { continue; }

                var _nuevo_g = _g[_actual] + aristas[_e].coste;
                if (_g[_v] == -1 || _nuevo_g < _g[_v]) {
                    _g[_v] = _nuevo_g;
                    _padre_arista[_v] = _e;
                    var _h = point_distance(nodos[_v].x, nodos[_v].y,
                                             nodos[_nodo_destino].x, nodos[_nodo_destino].y);
                    ds_priority_add(_abiertos, _v, _nuevo_g + _h);
                }
            }
        }

        ds_priority_destroy(_abiertos);

        var _out = [];
        if (!_encontrado) { return _out; }

        var _invertida = [];
        var _nodo = _nodo_destino;
        while (_nodo != _nodo_origen) {
            var _e = _padre_arista[_nodo];
            array_push(_invertida, aristas[_e]);
            _nodo = aristas[_e].desde;
        }
        for (var _k = array_length(_invertida) - 1; _k >= 0; _k--) { array_push(_out, _invertida[_k]); }
        return _out;
    };

    /// @desc Dibuja nodos y aristas. LLAMALO EN UN EVENTO DRAW mientras
    ///       ajustas el nivel: es la manera de comprobar a ojo que el grafo
    ///       generado se parece a lo que un jugador puede hacer de verdad.
    static draw_debug = function() {
        for (var _e = 0; _e < array_length(aristas); _e++) {
            var _a = aristas[_e];
            var _o = nodos[_a.desde], _d = nodos[_a.hasta];
            draw_set_color(_a.tipo == "caminar" ? c_lime : (_a.tipo == "saltar" ? c_yellow : c_aqua));
            draw_line(_o.x, _o.y, _d.x, _d.y);
        }
        draw_set_color(c_white);
        for (var _n = 0; _n < array_length(nodos); _n++) {
            draw_circle(nodos[_n].x, nodos[_n].y, 3, false);
        }
    };
}
```

> 🔺 Este grafo asume que **cada extremo salta hacia fuera de su propia plataforma**: el
> izquierdo prueba solo hacia la izquierda, el derecho solo hacia la derecha. Es la razón por la
> que no hace falta comprobar "¿el aterrizaje es la plataforma de la que salgo?" con más cuidado:
> la geometría lo impide sola (el arco solo se aleja del borde de salida, nunca vuelve a entrar
> en el rango `[x1,x2]` de su propia plataforma).

### 4.5 · Seguir la ruta

`buscar_camino()` devuelve una lista de aristas con su `tipo` y su nodo `hasta`. El pegamento con
el movimiento real es una máquina de estados sencilla — reutiliza
[`scr_state_machine`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) y el `Step` de
[04 · 01 §5.3](./01%20-%20Plataformas%202D.md), no los repitas:

```gml
/// Create de la unidad con IA
ruta = grafo.buscar_camino(nodo_actual, nodo_objetivo);
ruta_i = 0;

/// Step de la unidad — boceto: sustitúyelo por tu propia máquina de estados
if (ruta_i < array_length(ruta)) {
    var _arista = ruta[ruta_i];
    var _obj    = grafo.nodos[_arista.hasta];
    var _hacia  = sign(_obj.x - x);

    switch (_arista.tipo) {
        case "caminar":
            vel_x = _hacia * MOVE_SPEED_MAX;
            break;
        case "saltar":
            vel_x = _hacia * MOVE_SPEED_MAX;
            if (on_ground) { vel_y = -JUMP_SPEED; }   // el resto lo hace 04·01 §5.3
            break;
        case "caer":
            vel_x = _hacia * MOVE_SPEED_MAX;          // camina hasta salirse del borde: cae sola
            break;
    }

    if (point_distance(x, y, _obj.x, _obj.y) < 8) { ruta_i++; }
}
```

`vel_x`/`vel_y` los consume el mismo bloque de `move_and_collide` de
[04 · 01 §5.3](./01%20-%20Plataformas%202D.md): el grafo decide **hacia dónde**, la física de
siempre decide **cómo se mueve de verdad**. No hace falta (ni conviene) reimplementar la
colisión aquí.

---

## 5 · Suavizado de rutas y seguimiento con steering

### 5.1 · El problema: una ruta de rejilla es una escalera

`GridPonderado.buscar()`, `mp_grid_path` y el campo de flujo devuelven una ruta **centro de
celda a centro de celda**. Sobre una rejilla con diagonales de por medio, eso produce zig-zags
visibles incluso cuando la línea recta real está completamente libre — el defecto clásico que
delata "esto sigue una rejilla" en vez de moverse con naturalidad.

### 5.2 · *String pulling* con `collision_line`

La solución estándar es *string pulling*: desde un punto ancla, comprobar hasta qué punto más
lejano de la ruta se puede ir **en línea recta** sin cruzar un obstáculo, saltarse todos los
intermedios, y repetir desde ahí. Usa `collision_line`, con los mismos límites que documenta
[13 · 13 §6.8](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md#68--collision_line-cuándo-basta-y-cuándo-no):
solo ve **instancias**, no tilemaps.

```gml
/// @func suavizar_ruta(_puntos, _obj_pared)
/// @desc "String pulling": reduce una ruta en escalera a sus vértices reales
///       probando, desde cada ancla, el punto más lejano visible en línea
///       recta. Es una simplificación GREEDY (se para en el primer punto
///       bloqueado): no siempre encuentra el atajo más largo posible en
///       mapas muy cóncavos, pero SIEMPRE produce una ruta válida — nunca
///       atraviesa pared — y muchísimo más corta que la original.
/// @param {Array<Struct>} _puntos     Ruta de `find_points`/`buscar`/flow field.
/// @param {Asset.GMObject} _obj_pared Objeto sólido a evitar.
/// @return {Array<Struct>}
function suavizar_ruta(_puntos, _obj_pared)
{
    var _n = array_length(_puntos);
    if (_n <= 2) { return _puntos; }

    var _resultado = [_puntos[0]];
    var _ancla = 0;

    while (_ancla < _n - 1)
    {
        var _lejos = _ancla + 1;

        for (var _i = _ancla + 2; _i < _n; _i++)
        {
            var _libre = (collision_line(_puntos[_ancla].x, _puntos[_ancla].y,
                                          _puntos[_i].x, _puntos[_i].y,
                                          _obj_pared, false, true) == noone);
            if (_libre) { _lejos = _i; } else { break; }
        }

        array_push(_resultado, _puntos[_lejos]);
        _ancla = _lejos;
    }

    return _resultado;
}
```

> ⚠️ Si tu nivel usa un **tilemap** en vez de instancias sólidas, `collision_line` no lo ve
> ([13 · 13 §6.8](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md)).
> Sustituye la comprobación de "libre" por un muestreo de `tilemap_get_at_pixel` a pasos fijos a
> lo largo del segmento, o por `cortan_segmentos` (13 · 13 §6.5) si tienes las paredes
> vectorizadas.

### 5.3 · Seguimiento con Arrive

No se repite aquí el movimiento: **Arrive** ya está en
[23 · IA de enemigos y steering behaviors §2](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md#2--arrive--frenar-al-llegar-no-orbitar-el-objetivo)
(`llegar_a()`). El único pegamento nuevo es recorrer la ruta suavizada, waypoint a waypoint:

```gml
/// Create
ruta   = suavizar_ruta(grid.find_points(x, y, obj_jugador.x, obj_jugador.y), obj_pared);
ruta_i = 0;

/// Step — sigue la ruta suavizada con Arrive (23 · IA de enemigos §2), sin
///        redefinir `llegar_a`: ya existe.
if (ruta_i < array_length(ruta)) {
    var _wp = ruta[ruta_i];
    llegar_a(_wp.x, _wp.y, velocidad, 24);
    if (point_distance(x, y, _wp.x, _wp.y) < 6) { ruta_i++; }
}
```

> 💡 **Arrive en el último waypoint evita el "vibrado" sobre el destino** que ya explica
> [23 · IA de enemigos §2](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md#2--arrive--frenar-al-llegar-no-orbitar-el-objetivo);
> en los waypoints intermedios no hace falta frenar — usar `ir_hacia()` (seek) para todos menos
> el último es más natural y no cuesta nada extra.

---

## 6 · Checklist

- [ ] ¿Sabes cuántas unidades comparten destino a la vez? Decenas o cientos → campo de flujo
      (§2), no A* por unidad.
- [ ] ¿La rejilla es grande, abierta y de coste uniforme? Prueba JPS (§3) antes de optimizar A*
      a mano. ¿Tiene pesos por celda de verdad? Entonces JPS NO — `GridPonderado.buscar()`.
- [ ] ¿Es un plataformas? No uses `mp_grid`: construye el grafo de plataformas (§4) una vez al
      cargar el nivel.
- [ ] ¿Recalculas el campo de flujo / el grafo solo cuando cambia el destino o el mapa, nunca por
      frame ni por unidad?
- [ ] ¿Suavizas la ruta de rejilla (§5) antes de que la siga la unidad? Una escalera sin suavizar
      se nota, sobre todo en cámara cercana.
- [ ] ¿Destruyes SIEMPRE `ds_queue`/`ds_priority` tras la búsqueda, incluso si el bucle corta con
      `break`?
- [ ] ¿Has mirado el grafo de plataformas con `draw_debug()` sobre tu nivel real antes de confiar
      en la IA que lo usa?

---

## 7 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Recalcular el campo de flujo cada frame | Los FPS son tan malos como con A* por unidad | Recalcula solo al cambiar destino/mapa; usa el flag `sucio` |
| JPS sobre una `GridPonderado` con pesos de verdad | Rutas rápidas pero MALAS: ignoran el barro/agua | Usa `GridPonderado.buscar()` (A* normal) si hay coste por celda |
| Simular el arco de salto con velocidad de aceleración en vez de la máxima | El grafo cree que el personaje llega más lejos de lo que llega de verdad | Usa `MOVE_SPEED_MAX` y añade margen de seguridad al validar aterrizajes |
| Sin margen en el aterrizaje del grafo de plataformas | La IA "resbala" del borde nada más aterrizar | `margen_aterrizaje` ≈ medio ancho del personaje |
| Lanzar el arco hacia dentro de la propia plataforma | Aristas absurdas o bucles | Cada extremo lanza SOLO hacia fuera (izquierdo → izquierda, derecho → derecha) |
| No destruir `ds_queue`/`ds_priority` tras la búsqueda | Fuga de memoria progresiva | `ds_queue_destroy()`/`ds_priority_destroy()` siempre, incluso al cortar con `break` |
| Suavizar con `collision_line` contra un objeto sin instancias | Devuelve `noone` siempre: "suaviza" en línea recta a través de paredes | Comprueba que `_obj_pared` tiene instancias, o usa el muestreo con tilemap (§5.2) |
| No liberar los `path_add()` que crea `Grid.find_path()` al mezclarlo con estas técnicas | Fuga de memoria (ver el aviso de `06/scr_grid_pathfinding.gml`) | `path_delete()` en el Clean Up, o usa `find_points`/las técnicas de este documento, que no crean paths |

---

## 8 · Cómo escalarlo

1. **Varios campos de flujo cacheados** por destino frecuente (puntos de reunión de un RTS): no
   recalcules el mismo destino dos veces.
2. **Jerárquico (HPA*)** para mapas enormes: combina un campo de flujo/JPS "macro" entre zonas
   grandes con `GridPonderado` "micro" dentro de cada zona. Fuera del alcance de este documento.
3. **Más tipos de arista en el grafo de plataformas**: paredes escalables
   ([04 · 37 §3.2](./37%20-%20Traversal%20en%20plataformas%20-%20pendientes,%20paredes,%20escaleras%20y%20bordes.md#32-wall-slide-y-wall-jump)
   wall jump), cuerdas y escaleras ([04 · 37 §3.7-3.8](./37%20-%20Traversal%20en%20plataformas%20-%20pendientes,%20paredes,%20escaleras%20y%20bordes.md)) —
   cada una es una tercera/cuarta función `_lanzar_*` con su propia forma de arco.
4. **Nodos intermedios** en plataformas largas para rutas que no siempre van de punta a punta.
5. **Depuración visual permanente** tras una tecla de debug: `draw_debug()` en las tres
   estructuras antes de confiar en ellas en producción — un bug de pathfinding se ve al
   instante con la ruta dibujada encima y es carísimo de encontrar solo leyendo código.

---

## Ver también

- [`06 - Assets y Scripts/scr_grid_pathfinding.gml`](../06%20-%20Assets%20y%20Scripts/scr_grid_pathfinding.gml) — `Grid` y `GridPonderado`: la base sobre la que se apoya todo este documento
- [08 · Tower Defense](./08%20-%20Tower%20Defense.md) — A* básico con `mp_grid`, sin lo avanzado de aquí
- [13 · Estrategia y gestión](./13%20-%20Estrategia%20y%20gestión.md) — menciona el campo de flujo en §4.1 y §8.1; aquí está desarrollado
- [23 · IA de enemigos y steering behaviors](./23%20-%20IA%20de%20enemigos%20y%20steering%20behaviors.md) — Seek/Arrive/Flocking: el movimiento que sigue a estas rutas
- [01 · Plataformas 2D](./01%20-%20Plataformas%202D.md) — física de salto (`JUMP_SPEED`, `GRAV_RISE`/`GRAV_FALL`) que alimenta el grafo de plataformas, y `move_and_collide`
- [37 · Traversal en plataformas](./37%20-%20Traversal%20en%20plataformas%20-%20pendientes,%20paredes,%20escaleras%20y%20bordes.md) — wall jump, ledge grab, escaleras: movimientos que el grafo de §4 no modela
- [13 · Matemáticas aplicadas al juego §6](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md) — geometría de colisión: `collision_line`, distancia punto-segmento, intersección de segmentos
- [`06 - Assets y Scripts/scr_state_machine.gml`](../06%20-%20Assets%20y%20Scripts/scr_state_machine.gml) — el pegamento entre "qué arista toca ahora" y el movimiento real

---

## 9 · Fuentes

- Manual oficial — **DS Priority Queues** (`ds_priority_create`, `ds_priority_add`,
  `ds_priority_delete_min`, `ds_priority_empty`, `ds_priority_destroy`) — espejo local
  `09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Data_Structures/DS_Priority_Queues/`,
  consultado 2026-09-06 —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Data_Structures/DS_Priority_Queues/ds_priority_create.htm
- Manual oficial — **DS Queues** (`ds_queue_create`, `ds_queue_enqueue`, `ds_queue_dequeue`,
  `ds_queue_empty`, `ds_queue_destroy`) — espejo local
  `09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Data_Structures/DS_Queues/`,
  consultado 2026-09-06 —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Data_Structures/DS_Queues/ds_queue_create.htm
- Manual oficial — **`collision_line`** — espejo local
  `09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/collision_line.md`,
  consultado 2026-09-06 —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/collision_line.htm
- Manual oficial — **`move_and_collide`** (traducción propia de la biblioteca; la oficial en
  español no cubre esta página) — espejo local
  `09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement/move_and_collide.md`,
  consultado 2026-09-06 —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement/move_and_collide.htm
- ⚠️ **Jump Point Search** (concepto y reglas de poda): Harabor, D. y Grastien, A., "Online
  Graph Pruning for Pathfinding on Grid Maps" (AAAI 2011). Algoritmo de dominio público y muy
  citado en la literatura de *pathfinding* para juegos; esta sesión no tuvo acceso al paper
  original (WebSearch agotado) para verificar la implementación de §3.3 línea a línea contra él
  — verifica el comportamiento en tu propio mapa antes de confiar en la poda a ciegas.
  Sin URL: no se abrió ninguna en esta sesión.
  Se sí abrieron `06 - Assets y Scripts/scr_grid_pathfinding.gml` (`GridPonderado`, base de
  `GridJPS`) y `04 - Recetas por género/01 - Plataformas 2D.md` (física de salto, base del grafo
  de plataformas), ambos código y prosa propios de esta biblioteca.
- ⚠️ El **grafo de plataformas** (§4) es diseño propio de esta biblioteca, construido a partir de
  la física de salto ya documentada en 04·01: no reproduce un algoritmo publicado concreto ni una
  fuente externa abierta en esta sesión.
