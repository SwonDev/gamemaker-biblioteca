# 05 — Roguelike y generación procedural

> **Dificultad:** avanzada
> Aquí el juego deja de ser algo que **diseñas** y pasa a ser algo que
> **programas para que se diseñe solo**. Cambia por completo la forma de
> pensar.

---

## 1. Visión general

Un roguelike se define por la tensión entre dos fuerzas:

- **La muerte permanente** hace que cada decisión importe.
- **La generación procedural** hace que cada partida sea distinta.

Si solo tienes muerte permanente, el juego se memoriza y deja de ser
interesante (permadeath sobre contenido fijo =speedrun). Si solo tienes
generación procedural, no hay tensión (nada se pierde). El género vive en la
intersección.

**Definición clásica (Berlin Interpretation, 2008):**

| Rasgo | Obligatorio |
|---|---|
| Generación procedural de entornos | ✔ |
| Muerte permanente | ✔ |
| Por turnos | ✔ |
| Rejilla (grid) | ✔ |
| No modalidad (un mundo, no pantallas) | ✔ |
| Complejidad / profundidad de sistemas | ✔ |
| Recursos limitados (hambre, antorchas) | ✔ |
| *Hack'n'slash* (combate como medio, no fin) | ✔ |
| Exploración y descubrimiento | ✔ |

Los *roguelites* modernos (Hades, Dead Cells, Slay the Spire) relajan "por
turnos" y "rejilla" y añaden **meta-progresión**: mueres, pero desbloqueas
algo permanente. Es la evolución comercial del género.

**Referencias hechas en GameMaker:** *Nuclear Throne*, *Enter the Gungeon*,
*Downwell*, *TowerClimb* (el roguelike de plataformas más puro que existe).

---

## 2. Arquitectura recomendada

### Separación radical entre generación y presentación

```
GENERACIÓN (pura, sin objetos)
└── array 2D de enteros: grid[y][x] = TILE_WALL | TILE_FLOOR | ...

PRESENTACIÓN (lee la grid y la dibuja)
├── tilemap (estático, una sola vez al generar)
└── instancias (enemigos, cofres, escaleras) creadas según la grid
```

**Nunca generes instancias directamente.** Genera números, y después crea
instancias a partir de los números. Es la diferencia entre un generador que
puedes testear, guardar y reproducir, y uno que no.

### Jerarquía de objetos

```
objDungeonGen        (controller: genera la grid una vez, luego se destruye)
objTilemapRenderer   (pinta la grid en un tilemap)
objEntity            (padre: posición en grid + movimiento por turnos)
├── objPlayer
└── objEnemy
objItem
objStairs
objGame              (persistente: semilla, run info, meta-progresión)
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `DungeonGrid` | Array 2D + operaciones (get, set, carve, conectar) |
| `Room` | Un rectángulo generado (x, y, w, h, tipo) |
| `LootTable` | Tabla de botín con pesos, con `roll()` |
| `RunState` | Estado de la partida actual: semilla, piso, oro, inventario |
| `MetaProgress` | Desbloqueos permanentes entre partidas |

---

## 3. El bucle central (core loop)

```
┌─ Al crear la room ───────────────────────────────────────┐
│ 1. Fijar semilla: random_set_seed(global.run.seed)       │
│ 2. Generar la grid (BSP / random walk / salas)           │
│ 3. Validar la grid (¿todas las salas conectadas?)        │
│    → si no, regenerar con semilla + 1                    │
│ 4. Pintar tiles en el tilemap                            │
│ 5. Colocar: jugador (sala inicial), escaleras (lejos),   │
│    enemigos, cofres                                      │
└──────────────────────────────────────────────────────────┘
┌─ Step (por turnos) ──────────────────────────────────────┐
│ 6. Esperar input del jugador                             │
│ 7. Calcular FOV desde la posición del jugador            │
│ 8. Actualizar el "recuerdo" del mapa (explorado)         │
│ 9. Ejecutar el turno del jugador                         │
│ 10. Ejecutar los turnos de TODOS los enemigos            │
│ 11. Resolver daños, muertes, drops (LootTable.roll())    │
│ 12. Comprobar muerte del jugador → fin de run            │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 RNG con semilla

```gml
random_set_seed(_semilla);   // fija la secuencia
var _v = irandom(100);       // reproducible
var _s = random_get_seed();  // puedes guardar el estado y continuar
```

**Reglas:**

1. **Guarda la semilla, no el resultado.** Un save de un roguelike es la
   semilla + las acciones del jugador. Con eso reproduces la partida entera.
2. **Usa RNGs separados para cosas distintas.** Si el combate consume números
   aleatorios, la generación del siguiente piso cambia según cuántos golpes
   diste. Usa un generador propio por sistema (ver código) o una semilla
   derivada por piso: `seed_piso = seed_run + (piso * 7919)`.
3. **`randomize()` una sola vez al arrancar el juego**, nunca en mitad de una
   partida.

### 4.2 Generación de mazmorras

Tres algoritmos, de menor a mayor complejidad:

| Algoritmo | Resultado | Dificultad | Uso |
|---|---|---|---|
| **Random walk (drunkard)** | Cuevas orgánicas, irregulares | Muy baja | Cuevas, minas |
| **BSP** | Salas rectangulares conectadas | Media | Mazmorras clásicas, castillos |
| **Celular (autómata)** | Cuevas suaves y naturales | Media | Cavernas grandes |
| **Wave Function Collapse** | Nivel con reglas de adyacencia | Alta | Niveles temáticos muy controlados |

**BSP en corto:** divides el rectángulo recursivamente por la mitad, y en
cada hoja colocas una sala más pequeña. Luego conectas salas hermanas con
corredores en L. Garantiza salas sin solaparse y una conectividad en árbol.

**Random walk en corto:** un "borracho" parte del centro y camina aleatoria-
mente, excavando suelo a su paso. Con 40-50 % del área objetivo obtienes
cuevas convincentes. Riesgo: puede dejar zonas aisladas. Siempre valida.

### 4.3 Validación: el paso que todos olvidan

Un generador que produce mazmorras incompletas un 5 % de las veces es un
generador roto. Tras generar, **comprueba** y regenera si hace falta:

```gml
// Flood fill desde el punto de inicio
// ¿Se alcanza el objetivo? ¿Se alcanzan todas las salas?
// Si no → regenerar con otra semilla
```

### 4.4 Campo de visión (FOV)

El FOV más usado en roguelikes es **raycasting simétrico**: lanzas N rayos
(360 para precisión total) desde el jugador y marcas lo que ve cada uno hasta
chocar con un muro.

Alternativa más barata y muy usada: **shadowcasting** recursivo por octantes.
Es más rápido y no tiene artefactos, pero es bastante más código.

Para la mayoría de proyectos, raycasting con 180-360 rayos es más que
suficiente y se entiende de un vistazo.

### 4.5 Explorado vs visible

Dos grids paralelas:

| Grid | Significado | Se dibuja |
|---|---|---|
| `visible[]` | Lo que ves AHORA | Con color completo |
| `explored[]` | Lo que has visto ALGUNA VEZ | Atenuado (gris oscuro) |

Es lo que hace que el mapa se "revele" progresivamente y que el jugador pueda
planificar rutas.

### 4.6 Tablas de loot ponderadas

La estructura más flexible: una tabla con entradas `{ peso, id, min, max }`.
El peso determina la probabilidad relativa.

```gml
table = [
    { peso: 50, id: "potion",   min: 1, max: 3 },
    { peso: 20, id: "gold",     min: 10, max: 50 },
    { peso:  8, id: "iron_sword" },
    { peso:  2, id: "legendary" }
];
```

Suma de pesos = 80. Probabilidad de legendario = 2/80 = 2,5 %.

### 4.7 Muerte permanente y meta-progresión

La muerte permanente pura genera abandono. Casi todos los roguelikes
comerciales añaden **meta-progresión**: al morir, el oro acumulado desbloquea
armas, personajes o mejoras permanentes.

Estructura: dos capas de persistencia.

| Capa | Se borra al morir | Se guarda en |
|---|---|---|
| `RunState` (inventario, nivel, piso actual) | Sí | Memoria |
| `MetaProgress` (desbloqueos, récords) | No | Disco |

---

## 5. Código base

### 5.0 Generador aleatorio propio (independiente del global)

```gml
// ---------------------------------------------------------------------------
// scr_rng
// ---------------------------------------------------------------------------

/// @func RNG(_semilla)
/// @desc Generador congruencial lineal propio.
///       Imprescindible para que el combate no altere la generación del nivel.
function RNG(_semilla) constructor
{
    state = (_semilla == undefined) ? 12345 : _semilla;

    // Constantes de Numerical Recipes (funciona bien en 32 bits)
    a = 1664525;
    c = 1013904223;
    m = power(2, 32);

    /// @desc Siguiente entero de 32 bits.
    next = function()
    {
        state = (a * state + c) mod m;
        return state;
    };

    /// @desc Float en [0, 1)
    float = function() { return next() / m; };

    /// @desc Entero en [0, _max] inclusive
    int = function(_max) { return floor(float() * (_max + 1)); };

    /// @desc Entero en [_min, _max] inclusive
    range = function(_min, _max)
    {
        return _min + floor(float() * (_max - _min + 1));
    };

    /// @desc true con probabilidad _p (0..1)
    chance = function(_p) { return float() < _p; };

    /// @desc Elige un elemento al azar de un array
    pick = function(_array)
    {
        if (array_length(_array) == 0) return undefined;
        return _array[int(array_length(_array) - 1)];
    };

    /// @desc Fisher-Yates: baraja el array IN PLACE
    shuffle = function(_array)
    {
        var _n = array_length(_array);
        for (var _i = _n - 1; _i > 0; _i--)
        {
            var _j = int(_i);
            var _tmp = _array[_i];
            _array[_i] = _array[_j];
            _array[_j] = _tmp;
        }
        return _array;
    };
}
```

### 5.1 Grid de mazmorra

```gml
// ---------------------------------------------------------------------------
// scr_dungeon_grid
// ---------------------------------------------------------------------------

enum Tile { Void, Floor, Wall, Door, StairsDown, StairsUp, Water, Chest }

/// @func DungeonGrid(_ancho, _alto, _tile_por_defecto)
function DungeonGrid(_ancho, _alto, _tile_por_defecto) constructor
{
    ancho = _ancho;
    alto  = _alto;
    por_defecto = (_tile_por_defecto == undefined) ? Tile.Void : _tile_por_defecto;

    celdas = [];
    for (var _y = 0; _y < _alto; _y++)
    {
        var _fila = [];
        for (var _x = 0; _x < _ancho; _x++)
        {
            array_push(_fila, por_defecto);
        }
        array_push(celdas, _fila);
    }

    /// @desc Lee una celda. Fuera de rango → Void.
    get = function(_x, _y)
    {
        if (_x < 0 || _y < 0 || _x >= ancho || _y >= alto) return Tile.Void;
        return celdas[_y][_x];
    };

    set = function(_x, _y, _valor)
    {
        if (_x < 0 || _y < 0 || _x >= ancho || _y >= alto) return false;
        celdas[_y][_x] = _valor;
        return true;
    };

    fill = function(_valor)
    {
        for (var _y = 0; _y < alto; _y++)
            for (var _x = 0; _x < ancho; _x++)
                celdas[_y][_x] = _valor;
    };

    /// @desc ¿Es una celda por la que se puede andar?
    es_suelo = function(_x, _y)
    {
        var _t = get(_x, _y);
        return (_t == Tile.Floor) || (_t == Tile.Door) ||
               (_t == Tile.StairsDown) || (_t == Tile.StairsUp) ||
               (_t == Tile.Chest);
    };

    /// @desc ¿Bloquea la visión?
    opaco = function(_x, _y)
    {
        var _t = get(_x, _y);
        return (_t == Tile.Void) || (_t == Tile.Wall);
    };

    /// @desc Cuenta celdas de un tipo
    contar = function(_tipo)
    {
        var _n = 0;
        for (var _y = 0; _y < alto; _y++)
            for (var _x = 0; _x < ancho; _x++)
                if (celdas[_y][_x] == _tipo) _n++;
        return _n;
    };

    /// @desc Vecinos sólidos en 8 direcciones (para autotiling y paredes)
    vecinos_opacos = function(_x, _y)
    {
        var _n = 0;
        for (var _dy = -1; _dy <= 1; _dy++)
            for (var _dx = -1; _dx <= 1; _dx++)
            {
                if (_dx == 0 && _dy == 0) continue;
                if (opaco(_x + _dx, _y + _dy)) _n++;
            }
        return _n;
    };
}
```

### 5.2 Generador BSP

```gml
// ---------------------------------------------------------------------------
// scr_dungeon_bsp
// ---------------------------------------------------------------------------

/// @func BSPNode(_x, _y, _w, _h)
function BSPNode(_x, _y, _w, _h) constructor
{
    x = _x; y = _y; w = _w; h = _h;
    izq = noone;
    der = noone;
    sala = noone;     // { x, y, w, h }

    es_hoja = function() { return (izq == noone) && (der == noone); };
}

/// @func dungeon_generate_bsp(_ancho, _alto, _rng, _profundidad)
/// @desc Genera una mazmorra con división binaria del espacio.
function dungeon_generate_bsp(_ancho, _alto, _rng, _profundidad)
{
    var _grid = new DungeonGrid(_ancho, _alto, Tile.Void);

    // --- 1. Dividir recursivamente -------------------------------------------
    var _raiz = new BSPNode(1, 1, _ancho - 2, _alto - 2);
    var _pendientes = [_raiz];
    var _nivel = 0;

    while (array_length(_pendientes) > 0 && _nivel < _profundidad)
    {
        var _siguientes = [];

        for (var _i = 0; _i < array_length(_pendientes); _i++)
        {
            var _n = _pendientes[_i];

            // ¿Dividir este nodo? Solo si es suficientemente grande
            var _min_size = 8;
            if (_n.w <= _min_size * 2 && _n.h <= _min_size * 2) continue;
            if (!_rng.chance(0.85)) continue;    // algo de variedad

            var _horizontal = false;
            if (_n.w / _n.h > 1.25)      _horizontal = true;   // muy ancho → corte vertical
            else if (_n.h / _n.w > 1.25) _horizontal = false;  // muy alto → corte horizontal
            else                          _horizontal = _rng.chance(0.5);

            if (_horizontal)
            {
                // Corte vertical: dos mitades izquierda/derecha
                var _split = _rng.range(floor(_n.w * 0.35), floor(_n.w * 0.65));
                _n.izq = new BSPNode(_n.x, _n.y, _split, _n.h);
                _n.der = new BSPNode(_n.x + _split, _n.y, _n.w - _split, _n.h);
            }
            else
            {
                // Corte horizontal: dos mitades arriba/abajo
                var _split = _rng.range(floor(_n.h * 0.35), floor(_n.h * 0.65));
                _n.izq = new BSPNode(_n.x, _n.y, _n.w, _split);
                _n.der = new BSPNode(_n.x, _n.y + _split, _n.w, _n.h - _split);
            }

            array_push(_siguientes, _n.izq);
            array_push(_siguientes, _n.der);
        }

        _pendientes = _siguientes;
        _nivel++;
    }

    // --- 2. Crear una sala en cada hoja ---------------------------------------
    var _salas = [];
    var _pila = [_raiz];

    while (array_length(_pila) > 0)
    {
        var _n = array_pop(_pila);

        if (_n.es_hoja())
        {
            var _sw = _rng.range(floor(_n.w * 0.5), floor(_n.w * 0.85));
            var _sh = _rng.range(floor(_n.h * 0.5), floor(_n.h * 0.85));
            var _sx = _n.x + _rng.range(0, max(0, _n.w - _sw - 1));
            var _sy = _n.y + _rng.range(0, max(0, _n.h - _sh - 1));

            _n.sala = { x: _sx, y: _sy, w: _sw, h: _sh };
            array_push(_salas, _n.sala);

            // Excavar
            for (var _y = _sy; _y < _sy + _sh; _y++)
                for (var _x = _sx; _x < _sx + _sw; _x++)
                    _grid.set(_x, _y, Tile.Floor);
        }
        else
        {
            if (_n.izq != noone) array_push(_pila, _n.izq);
            if (_n.der != noone) array_push(_pila, _n.der);
        }
    }

    // --- 3. Conectar salas con corredores en L --------------------------------
    for (var _i = 1; _i < array_length(_salas); _i++)
    {
        var _a = _salas[_i - 1];
        var _b = _salas[_i];

        var _ax = _a.x + floor(_a.w * 0.5);
        var _ay = _a.y + floor(_a.h * 0.5);
        var _bx = _b.x + floor(_b.w * 0.5);
        var _by = _b.y + floor(_b.h * 0.5);

        // Corredor en L: primero horizontal, luego vertical (o al revés)
        if (_rng.chance(0.5))
        {
            cavar_h(_grid, _ax, _bx, _ay);
            cavar_v(_grid, _ay, _by, _bx);
        }
        else
        {
            cavar_v(_grid, _ay, _by, _ax);
            cavar_h(_grid, _ax, _bx, _by);
        }
    }

    return { grid: _grid, salas: _salas };
}

/// @func cavar_h(_grid, _x1, _x2, _y)
function cavar_h(_grid, _x1, _x2, _y)
{
    var _min = min(_x1, _x2);
    var _max = max(_x1, _x2);
    for (var _x = _min; _x <= _max; _x++)
    {
        if (_grid.get(_x, _y) == Tile.Void) _grid.set(_x, _y, Tile.Floor);
    }
}

/// @func cavar_v(_grid, _y1, _y2, _x)
function cavar_v(_grid, _y1, _y2, _x)
{
    var _min = min(_y1, _y2);
    var _max = max(_y1, _y2);
    for (var _y = _min; _y <= _max; _y++)
    {
        if (_grid.get(_x, _y) == Tile.Void) _grid.set(_x, _y, Tile.Floor);
    }
}
```

### 5.3 Generador random walk (cuevas)

```gml
// ---------------------------------------------------------------------------
// scr_dungeon_walk
// ---------------------------------------------------------------------------

/// @func dungeon_generate_walk(_ancho, _alto, _rng, _cobertura)
/// @desc Excava una cueva con el algoritmo del borracho.
/// @param {Real} _cobertura Fracción del área a excavar (0.35 - 0.55)
function dungeon_generate_walk(_ancho, _alto, _rng, _cobertura)
{
    var _grid = new DungeonGrid(_ancho, _alto, Tile.Void);

    var _objetivo = floor(_ancho * _alto * _cobertura);
    var _actual   = 0;

    // Empezar en el centro
    var _x = floor(_ancho * 0.5);
    var _y = floor(_alto  * 0.5);

    // Dirección inicial aleatoria
    var _dir = _rng.int(3);   // 0=arriba 1=derecha 2=abajo 3=izquierda
    var _persistencia = 0.75; // probabilidad de seguir en la misma dirección

    var _intentos = 0;
    var _max_intentos = _objetivo * 60;   // salvaguarda anti-bucle infinito

    while (_actual < _objetivo && _intentos < _max_intentos)
    {
        _intentos++;

        // Excavar si está en rango y no era ya suelo
        if (_grid.get(_x, _y) != Tile.Floor && _x > 0 && _y > 0 &&
            _x < _ancho - 1 && _y < _alto - 1)
        {
            _grid.set(_x, _y, Tile.Floor);
            _actual++;
        }

        // Cambiar de dirección con cierta probabilidad
        if (_rng.float() > _persistencia) _dir = _rng.int(3);

        switch (_dir)
        {
            case 0: _y--; break;
            case 1: _x++; break;
            case 2: _y++; break;
            case 3: _x--; break;
        }

        // Rebotar en los bordes
        _x = clamp(_x, 1, _ancho - 2);
        _y = clamp(_y, 1, _alto  - 2);
    }

    return { grid: _grid, salas: [] };
}
```

### 5.4 Validación por flood fill

```gml
// ---------------------------------------------------------------------------
// scr_dungeon_validate
// ---------------------------------------------------------------------------

/// @func dungeon_flood_fill(_grid, _x_inicio, _y_inicio)
/// @desc Devuelve un array 2D de booleanos con las celdas alcanzables.
function dungeon_flood_fill(_grid, _x_inicio, _y_inicio)
{
    var _alcanzado = [];
    for (var _y = 0; _y < _grid.alto; _y++)
    {
        var _fila = [];
        for (var _x = 0; _x < _grid.ancho; _x++) array_push(_fila, false);
        array_push(_alcanzado, _fila);
    }

    if (!_grid.es_suelo(_x_inicio, _y_inicio)) return _alcanzado;

    var _cola = [[_x_inicio, _y_inicio]];
    _alcanzado[_y_inicio][_x_inicio] = true;

    while (array_length(_cola) > 0)
    {
        var _celda = array_pop(_cola);
        var _cx = _celda[0];
        var _cy = _celda[1];

        // 4-vecinos
        var _vecinos = [[_cx+1,_cy], [_cx-1,_cy], [_cx,_cy+1], [_cx,_cy-1]];

        for (var _i = 0; _i < 4; _i++)
        {
            var _nx = _vecinos[_i][0];
            var _ny = _vecinos[_i][1];

            if (_nx < 0 || _ny < 0 || _nx >= _grid.ancho || _ny >= _grid.alto) continue;
            if (_alcanzado[_ny][_nx]) continue;
            if (!_grid.es_suelo(_nx, _ny)) continue;

            _alcanzado[_ny][_nx] = true;
            array_push(_cola, [_nx, _ny]);
        }
    }

    return _alcanzado;
}

/// @func dungeon_es_valida(_grid, _x_inicio, _y_inicio)
/// @desc true si TODO el suelo generado es alcanzable desde el inicio.
function dungeon_es_valida(_grid, _x_inicio, _y_inicio)
{
    var _alcanzado = dungeon_flood_fill(_grid, _x_inicio, _y_inicio);

    var _suelo_total = _grid.contar(Tile.Floor);
    var _alcanzado_total = 0;

    for (var _y = 0; _y < _grid.alto; _y++)
        for (var _x = 0; _x < _grid.ancho; _x++)
            if (_alcanzado[_y][_x]) _alcanzado_total++;

    // Margen del 98 %: permite rincones de 1-2 celdas sin invalidar
    return (_alcanzado_total >= _suelo_total * 0.98);
}

/// @func dungeon_generate_valid(_ancho, _alto, _semilla, _tipo)
/// @desc Genera, valida y regenera hasta obtener una mazmorra jugable.
function dungeon_generate_valid(_ancho, _alto, _semilla, _tipo)
{
    var _intentos = 0;
    var _resultado = noone;

    while (_intentos < 30)
    {
        // Cada intento usa una semilla distinta pero derivada de la original
        var _rng = new RNG(_semilla + (_intentos * 7919));

        if (_tipo == "walk")
        {
            _resultado = dungeon_generate_walk(_ancho, _alto, _rng, 0.45);
        }
        else
        {
            _resultado = dungeon_generate_bsp(_ancho, _alto, _rng, 5);
        }

        // Encontrar el punto de inicio: primer suelo de la esquina superior izq.
        var _inicio = dungeon_encontrar_inicio(_resultado.grid);

        if (_inicio != noone &&
            dungeon_es_valida(_resultado.grid, _inicio[0], _inicio[1]))
        {
            _resultado.inicio = _inicio;
            _resultado.intentos = _intentos + 1;
            return _resultado;
        }

        _intentos++;
    }

    show_debug_message("AVISO: no se generó una mazmorra válida en 30 intentos");
    _resultado.inicio = dungeon_encontrar_inicio(_resultado.grid);
    return _resultado;
}

/// @func dungeon_encontrar_inicio(_grid)
/// @desc Busca la primera celda de suelo escaneando desde arriba-izquierda.
function dungeon_encontrar_inicio(_grid)
{
    for (var _y = 0; _y < _grid.alto; _y++)
        for (var _x = 0; _x < _grid.ancho; _x++)
            if (_grid.es_suelo(_x, _y)) return [_x, _y];
    return noone;
}
```

### 5.5 Pintar la grid en un tilemap

```gml
// ---------------------------------------------------------------------------
// objTilemapRenderer — Create
// ---------------------------------------------------------------------------
// La grid se pinta UNA SOLA VEZ. Después, el tilemap es estático:
// es lo más rápido que hay para renderizar un suelo.

var _lay = layer_get_id("Tiles_Dungeon");
tilemap = layer_tilemap_get_id(_lay);

// Índices de tile dentro del tileset (ajusta a tu tileset)
// En GameMaker, tile 0 = vacío, y cada tile del set tiene un índice propio.
TILE_FLOOR_IDX = 1;
TILE_WALL_IDX  = 2;

pintar_grid(global.dungeon.grid);

// ---------------------------------------------------------------------------
// objTilemapRenderer — funciones
// ---------------------------------------------------------------------------

function pintar_grid(_grid)
{
    for (var _y = 0; _y < _grid.alto; _y++)
    {
        for (var _x = 0; _x < _grid.ancho; _x++)
        {
            var _t = _grid.get(_x, _y);
            var _idx = 0;   // 0 = nada dibujado

            if (_t == Tile.Floor || _t == Tile.Door ||
                _t == Tile.StairsDown || _t == Tile.StairsUp ||
                _t == Tile.Chest)
            {
                _idx = TILE_FLOOR_IDX;
            }
            else
            {
                // Solo pintar muro si toca suelo (evita pintar el vacío lejano)
                if (_grid.vecinos_opacos(_x, _y) < 8) _idx = TILE_WALL_IDX;
            }

            tilemap_set(tilemap, _idx, _x, _y);
        }
    }
}

/// @func grid_to_pixel_x(_grid_x)
function grid_to_pixel_x(_grid_x) { return _grid_x * TILE_SIZE; }

/// @func grid_to_pixel_y(_grid_y)
function grid_to_pixel_y(_grid_y) { return _grid_y * TILE_SIZE; }
```

### 5.6 Campo de visión por raycasting

```gml
// ---------------------------------------------------------------------------
// scr_fov
// ---------------------------------------------------------------------------

/// @func fov_compute(_grid, _px, _py, _radio, _rayos)
/// @desc Devuelve un array 2D de booleanos: celdas visibles ahora.
/// @param {Real} _rayos Cuántos rayos lanzar (180 va bien; 360 es preciso)
function fov_compute(_grid, _px, _py, _radio, _rayos)
{
    var _visible = [];
    for (var _y = 0; _y < _grid.alto; _y++)
    {
        var _fila = [];
        for (var _x = 0; _x < _grid.ancho; _x++) array_push(_fila, false);
        array_push(_visible, _fila);
    }

    // El origen siempre es visible
    if (_px >= 0 && _py >= 0 && _px < _grid.ancho && _py < _grid.alto)
    {
        _visible[_py][_px] = true;
    }

    // Centro de la celda de origen (+0.5 para que los rayos salgan del centro)
    var _ox = _px + 0.5;
    var _oy = _py + 0.5;

    for (var _i = 0; _i < _rayos; _i++)
    {
        var _angulo = (_i / _rayos) * 360;
        var _dx = dcos(_angulo);
        var _dy = -dsin(_angulo);        // - porque en pantalla Y crece hacia abajo

        // Marchar por el rayo en pasos pequeños
        var _rx = _ox;
        var _ry = _oy;

        for (var _paso = 0; _paso < _radio * 4; _paso++)
        {
            _rx += _dx * 0.25;
            _ry += _dy * 0.25;

            var _cx = floor(_rx);
            var _cy = floor(_ry);

            // Fuera del mapa: parar este rayo
            if (_cx < 0 || _cy < 0 || _cx >= _grid.ancho || _cy >= _grid.alto) break;

            // Fuera de rango de visión
            if (point_distance(_ox, _oy, _rx, _ry) > _radio) break;

            _visible[_cy][_cx] = true;

            // Chocamos con algo opaco → el rayo se detiene
            if (_grid.opaco(_cx, _cy)) break;
        }
    }

    return _visible;
}

/// @desc Ejemplo de uso: combinar visible + explorado
function fov_actualizar()
{
    var _grid = global.dungeon.grid;
    var _px = objPlayer.grid_x;
    var _py = objPlayer.grid_y;

    global.fov_visible = fov_compute(_grid, _px, _py, 8, 240);

    // Marcar como explorado todo lo que ahora es visible
    for (var _y = 0; _y < _grid.alto; _y++)
        for (var _x = 0; _x < _grid.ancho; _x++)
            if (global.fov_visible[_y][_x]) global.fov_explorado[_y][_x] = true;
}
```

```gml
// ---------------------------------------------------------------------------
// Renderizar el FOV: enmascarar lo no visible
// ---------------------------------------------------------------------------
// La forma más eficiente es pintar una capa oscura sobre todo
// y "agujerearla" donde hay visión.

// objFovRenderer — Draw (depth por encima del tilemap, debajo de las entidades)
var _ts = TILE_SIZE;

for (var _y = 0; _y < global.dungeon.grid.alto; _y++)
{
    for (var _x = 0; _x < global.dungeon.grid.ancho; _x++)
    {
        var _px = _x * _ts;
        var _py = _y * _ts;

        if (global.fov_visible[_y][_x])
        {
            continue;                          // completamente iluminado
        }
        else if (global.fov_explorado[_y][_x])
        {
            draw_set_alpha(0.55);              // recordado: atenuado
            draw_set_color(c_black);
            draw_rectangle(_px, _py, _px + _ts, _py + _ts, false);
            draw_set_alpha(1);
        }
        else
        {
            draw_set_color(c_black);           // desconocido: negro total
            draw_rectangle(_px, _py, _px + _ts, _py + _ts, false);
        }
    }
}
```

### 5.7 Tablas de loot ponderadas

```gml
// ---------------------------------------------------------------------------
// scr_loot
// ---------------------------------------------------------------------------

/// @func LootTable(_entradas)
/// @desc _entradas: array de { peso, id, min, max, condicion }
function LootTable(_entradas) constructor
{
    entradas = _entradas;

    /// @desc Suma total de pesos (solo de las entradas válidas ahora mismo).
    peso_total = function()
    {
        var _t = 0;
        for (var _i = 0; _i < array_length(entradas); _i++)
        {
            var _e = entradas[_i];
            if (variable_struct_exists(_e, "condicion") && !_e.condicion()) continue;
            _t += _e.peso;
        }
        return _t;
    };

    /// @desc Devuelve una entrada elegida proporcionalmente a su peso.
    roll = function(_rng)
    {
        if (_rng == undefined) _rng = global.rng_loot;

        var _total = peso_total();
        if (_total <= 0) return undefined;

        var _tirada = _rng.float() * _total;
        var _acumulado = 0;

        for (var _i = 0; _i < array_length(entradas); _i++)
        {
            var _e = entradas[_i];

            if (variable_struct_exists(_e, "condicion") && !_e.condicion()) continue;

            _acumulado += _e.peso;
            if (_tirada <= _acumulado) return _e;
        }

        // Red de seguridad por errores de redondeo
        return entradas[array_length(entradas) - 1];
    };

    /// @desc Hace _veces tiradas y devuelve un array de { id, cantidad }
    roll_multi = function(_veces, _rng)
    {
        var _out = [];

        for (var _i = 0; _i < _veces; _i++)
        {
            var _e = roll(_rng);
            if (_e == undefined) continue;

            var _min = variable_struct_exists(_e, "min") ? _e.min : 1;
            var _max = variable_struct_exists(_e, "max") ? _e.max : 1;
            var _r = (_rng == undefined) ? global.rng_loot : _rng;

            array_push(_out, {
                id:       _e.id,
                cantidad: (_min == _max) ? _min : _r.range(_min, _max)
            });
        }
        return _out;
    };
}

// --- Catálogo global de tablas -----------------------------------------------
function loot_tables_init()
{
    global.loot_tables = {

        // Botín de enemigo común
        comun: new LootTable([
            { peso: 45, id: "nada",       min: 0, max: 0 },
            { peso: 30, id: "oro",        min: 3,  max: 18 },
            { peso: 18, id: "potion",     min: 1,  max: 2 },
            { peso:  6, id: "iron_sword" },
            { peso:  1, id: "anillo_poder" }
        ]),

        // Cofre: siempre da algo
        cofre: new LootTable([
            { peso: 40, id: "oro",        min: 20, max: 70 },
            { peso: 25, id: "potion",     min: 2,  max: 5 },
            { peso: 20, id: "equipo",     min: 1,  max: 1 },
            { peso: 12, id: "pergamino",  min: 1,  max: 2 },
            { peso:  3, id: "legendario" }
        ]),

        // Jefe: garantiza algo bueno
        jefe: new LootTable([
            { peso: 50, id: "equipo_raro" },
            { peso: 30, id: "oro",        min: 100, max: 300 },
            { peso: 15, id: "pocion_max", min: 1,   max: 2 },
            { peso:  5, id: "legendario" }
        ])
    };
}
```

### 5.8 Run state y meta-progresión

```gml
// ---------------------------------------------------------------------------
// scr_run_state
// ---------------------------------------------------------------------------

/// @func RunState(_semilla)
/// @desc Estado de la partida actual. Se BORRA al morir.
function RunState(_semilla) constructor
{
    semilla = (_semilla == undefined) ? irandom(999999999) : _semilla;
    piso    = 1;
    oro     = 0;
    turnos  = 0;

    hp        = 20;
    hp_max    = 20;
    inventario = [];
    equipo    = noone;

    /// @desc Semilla derivada para el piso actual.
    ///       Así, el mismo piso siempre genera igual aunque el combate haya
    ///       consumido números aleatorios.
    semilla_piso = function()
    {
        return semilla + (piso * 7919);
    };

    siguiente_piso = function()
    {
        piso++;
        turnos = 0;
        // Pequeña curación al bajar de piso (recompensa por progresar)
        hp = min(hp + floor(hp_max * 0.25), hp_max);
    };

    morir = function()
    {
        // Notificar a la meta-progresión antes de desaparecer
        global.meta.registrar_muerte(self);
        global.run = noone;
    };
}

/// @func MetaProgress()
/// @desc Progresión entre partidas. NUNCA se borra. Persiste en disco.
function MetaProgress() constructor
{
    muertes        = 0;
    piso_maximo    = 0;
    oro_total      = 0;
    desbloqueos    = {};      // "espada_vengativa" = true
    logros         = {};

    /// @desc Registra el final de una partida y aplica desbloqueos.
    registrar_muerte = function(_run)
    {
        muertes++;
        oro_total += _run.oro;

        if (_run.piso > piso_maximo) piso_maximo = _run.piso;

        // Desbloqueos por hitos
        if (_run.piso >= 5 && !variable_struct_exists(desbloqueos, "espada_vengativa"))
        {
            desbloqueos.espada_vengativa = true;
            desbloqueo_notificar("Espada vengativa");
        }
        if (muertes >= 10 && !variable_struct_exists(desbloqueos, "clase_brujo"))
        {
            desbloqueos.clase_brujo = true;
            desbloqueo_notificar("Clase: Brujo");
        }

        guardar();
    };

    tiene = function(_id)
    {
        return variable_struct_exists(desbloqueos, _id);
    };

    guardar = function()
    {
        var _data = {
            muertes: muertes, piso_maximo: piso_maximo,
            oro_total: oro_total, desbloqueos: desbloqueos, logros: logros
        };
        // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
        // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
        // 14 - Persistencia y archivos.md §1.
        var _f = file_text_open_write(game_save_id + "meta.json");
        file_text_write_string(_f, json_stringify(_data));
        file_text_close(_f);
    };

    cargar = function()
    {
        var _path = game_save_id + "meta.json";
        if (!file_exists(_path)) return;

        var _f = file_text_open_read(_path);
        var _d = json_parse(file_text_read_string(_f));
        file_text_close(_f);

        muertes     = _d.muertes;
        piso_maximo = _d.piso_maximo;
        oro_total   = _d.oro_total;
        desbloqueos = _d.desbloqueos;
        logros      = _d.logros;
    };
}

/// @func desbloqueo_notificar(_nombre)
function desbloqueo_notificar(_nombre)
{
    show_debug_message("¡Desbloqueado: " + _nombre + "!");
    // Aquí: UI de notificación
}
```

### 5.9 Arranque de una partida

```gml
// ---------------------------------------------------------------------------
// objGame — Create (persistente)
// ---------------------------------------------------------------------------
if (variable_global_exists("game_boot_done")) exit;
global.game_boot_done = true;

randomize();     // UNA sola vez en toda la vida del proceso

global.meta = new MetaProgress();
global.meta.cargar();

loot_tables_init();

// RNG separados: el combate no contamina la generación
global.rng_nivel = new RNG(0);
global.rng_loot  = new RNG(0);
global.rng_combate = new RNG(0);
```

> ⚠️ **`run_nueva()`, `generar_piso()` y `poblar_piso()` van en un script, no en este
> `Create`.** Ninguna de las tres toca una variable de instancia — solo `global.*` y
> parámetros — así que no hay ninguna razón para que dependan de `objGame`. Y sí hay una
> razón real para que revienten si se quedan aquí: `generar_piso()` se vuelve a llamar
> más abajo desde `scr_save_run` (al cargar una partida guardada), un script — no
> `objGame` — y una `function nombre() {...}` declarada dentro de un evento solo la
> puede llamar sin cualificar la instancia donde se declaró. Mismo mecanismo que
> [`04 · 19` §1](./19%20-%20Programación%20rítmica%20%28juegos%20de%20ritmo%29.md#1--el-conductor).

```gml
// scr_dungeon_run.gml

/// @func run_nueva(_semilla)
function run_nueva(_semilla)
{
    global.run = new RunState(_semilla);

    global.rng_nivel   = new RNG(global.run.semilla_piso());
    global.rng_loot    = new RNG(global.run.semilla_piso() + 101);
    global.rng_combate = new RNG(global.run.semilla_piso() + 202);

    generar_piso();
}

/// @func generar_piso()
function generar_piso()
{
    // Regenerar los RNG de nivel con la semilla del piso actual
    global.rng_nivel = new RNG(global.run.semilla_piso());

    var _ancho = 48;
    var _alto  = 36;

    // Alternar estilos: los pisos pares son cuevas, los impares mazmorras
    var _tipo = (global.run.piso mod 2 == 0) ? "walk" : "bsp";

    global.dungeon = dungeon_generate_valid(
        _ancho, _alto, global.run.semilla_piso(), _tipo);

    // Grids de visión
    global.fov_visible = [];
    global.fov_explorado = [];
    for (var _y = 0; _y < _alto; _y++)
    {
        var _fila_v = [], _fila_e = [];
        for (var _x = 0; _x < _ancho; _x++)
        {
            array_push(_fila_v, false);
            array_push(_fila_e, false);
        }
        array_push(global.fov_visible,   _fila_v);
        array_push(global.fov_explorado, _fila_e);
    }

    // Poblar: escaleras lejos del inicio, enemigos, cofres
    poblar_piso();
}

/// @func poblar_piso()
function poblar_piso()
{
    var _grid   = global.dungeon.grid;
    var _inicio = global.dungeon.inicio;

    // --- Escaleras: la celda de suelo más lejana al inicio -------------------
    var _mejor_x = _inicio[0], _mejor_y = _inicio[1], _mejor_d = 0;

    for (var _y = 0; _y < _grid.alto; _y++)
        for (var _x = 0; _x < _grid.ancho; _x++)
        {
            if (!_grid.es_suelo(_x, _y)) continue;
            var _d = point_distance(_inicio[0], _inicio[1], _x, _y);
            if (_d > _mejor_d) { _mejor_d = _d; _mejor_x = _x; _mejor_y = _y; }
        }

    _grid.set(_mejor_x, _mejor_y, Tile.StairsDown);

    // --- Enemigos: densidad según la profundidad ------------------------------
    var _n_enemigos = 6 + (global.run.piso * 2);
    var _colocados  = 0;
    var _intentos   = 0;

    while (_colocados < _n_enemigos && _intentos < 500)
    {
        _intentos++;

        var _x = global.rng_nivel.int(_grid.ancho - 1);
        var _y = global.rng_nivel.int(_grid.alto  - 1);

        if (_grid.get(_x, _y) != Tile.Floor) continue;
        if (point_distance(_inicio[0], _inicio[1], _x, _y) < 6) continue;  // no spawnear encima

        instance_create_layer(_x * TILE_SIZE, _y * TILE_SIZE, "Entities", objEnemy);
        _colocados++;
    }

    // --- Cofres ----------------------------------------------------------------
    var _n_cofres = 1 + floor(global.run.piso * 0.5);
    _colocados = 0;
    _intentos  = 0;

    while (_colocados < _n_cofres && _intentos < 500)
    {
        _intentos++;
        var _x = global.rng_nivel.int(_grid.ancho - 1);
        var _y = global.rng_nivel.int(_grid.alto  - 1);

        if (_grid.get(_x, _y) != Tile.Floor) continue;

        _grid.set(_x, _y, Tile.Chest);
        instance_create_layer(_x * TILE_SIZE, _y * TILE_SIZE, "Entities", objChest);
        _colocados++;
    }
}
```

---

## 6. Gestión del estado del jugador

En un roguelike el jugador tiene **tres** estados simultáneos. Confundirlos es
la fuente número uno de bugs.

```gml
// ---------------------------------------------------------------------------
// Separación de estado en un roguelike
// ---------------------------------------------------------------------------

// 1) ESTADO DE RUN — vive solo esta partida. Se pierde al morir.
global.run = new RunState();          // hp, oro, inventario, piso
global.player_stats = {               // derivado de la run
    hp:     global.run.hp,
    hp_max: global.run.hp_max
};

// 2) ESTADO DE PISO — se regenera en cada piso
global.dungeon       = {};            // grid + salas + inicio
global.fov_visible   = [];            // qué ves ahora
global.fov_explorado = [];            // qué has visto

// 3) META-ESTADO — permanente, en disco
global.meta = new MetaProgress();     // desbloqueos, récords, logros
```

```gml
// ---------------------------------------------------------------------------
// scr_save_run — guardar una partida EN CURSO de roguelike
// ---------------------------------------------------------------------------

/// @func save_run()
/// @desc Guarda semilla + acciones. No guarda el mapa: se regenera.
function save_run()
{
    var _data = {
        version:  2,
        run: {
            semilla:     global.run.semilla,
            piso:        global.run.piso,
            oro:         global.run.oro,
            hp:          global.run.hp,
            hp_max:      global.run.hp_max,
            inventario:  global.run.inventario,
            turnos:      global.run.turnos
        },
        // Posición dentro del piso (para restaurar al jugador)
        pos: { x: objPlayer.grid_x, y: objPlayer.grid_y }
    };

    // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
    // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
    // 14 - Persistencia y archivos.md §1.
    var _f = file_text_open_write(game_save_id + "run_save.json");
    file_text_write_string(_f, json_stringify(_data));
    file_text_close(_f);
}

/// @func load_run()
/// @desc Reconstruye la run y regenera el piso a partir de la semilla.
function load_run()
{
    var _path = game_save_id + "run_save.json";
    if (!file_exists(_path)) return false;

    var _f = file_text_open_read(_path);
    var _d = json_parse(file_text_read_string(_f));
    file_text_close(_f);

    global.run = new RunState(_d.run.semilla);
    global.run.piso       = _d.run.piso;
    global.run.oro        = _d.run.oro;
    global.run.hp         = _d.run.hp;
    global.run.hp_max     = _d.run.hp_max;
    global.run.inventario = _d.run.inventario;
    global.run.turnos     = _d.run.turnos;

    generar_piso();     // el mapa se regenera idéntico: misma semilla

    // Colocar al jugador donde estaba
    global.pending_grid_x = _d.pos.x;
    global.pending_grid_y = _d.pos.y;

    return true;
}
```

> La belleza de guardar la semilla: un save de roguelike ocupa 500 bytes,
> no 5 MB. El mapa no se guarda, se **recalcula**.

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| No validar la mazmorra generada | Un 5 % de partidas son injugables: las escaleras están incomunicadas | Flood fill + regenerar si falla |
| Generar instancias directamente | Imposible de guardar, testear o reproducir | Genera una grid de números; crea instancias después |
| Usar el RNG global para todo | El número de golpes que diste cambia la mazmorra siguiente | RNG propio por sistema (`RNG` struct) o semillas derivadas |
| `randomize()` en cada room | La semilla se pierde; nada es reproducible | `randomize()` una sola vez al arrancar |
| Semilla derivada con `seed + piso` | Pisos correlacionados (patrones que se repiten) | Multiplica por un primo: `seed + piso * 7919` |
| Sin límite de intentos en el walk | Bucle infinito si la cobertura es inalcanzable | Contador de intentos con tope |
| FOV con pocos rayos | Huecos negros en las esquinas | 180 rayos mínimo; 360 para mapas pequeños |
| Recalcular el FOV cada frame de animación | Coste brutal en mapas grandes | Recalcular **solo** cuando el jugador cambia de celda |
| Tabla de loot con pesos absolutos | Añadir un objeto obliga a recalcular todos los pesos | Pesos relativos; el total se calcula en `roll()` |
| `roll()` sin red de seguridad | Errores de redondeo devuelven `undefined` y crashea | Devolver la última entrada si la tirada se pasa |
| Pintar el tilemap entero incluyendo el vacío | Miles de tiles inútiles | Solo pinta muros que toquen suelo |
| Guardar el mapa en el save | Saves gigantes e incompatibles entre versiones | Guarda la semilla y regenera |

---

## 8. Cómo escalarlo

1. **Más algoritmos de generación** — autómata celular para cuevas grandes,
   WFC para niveles temáticos con reglas.
2. **Salas prefabricadas** (*vaults*) — diseña 20 salas a mano y que el
   generador inserte 2-3 por piso. Es la técnica que usan Spelunky y Binding
   of Isaac: proceduralidad con contenido con autoría.
3. **Generación de encuentros** — en vez de colocar enemigos al azar, genera
   "situaciones": una sala con tres arqueros en alto y un cofre cerrado.
4. **Curva de dificultad** — una tabla por piso que define: densidad de
   enemigos, tipos permitidos, tabla de loot, número de salas.
5. **FOV por shadowcasting** — cuando el mapa pase de 80×80, el raycasting
   se queda corto.
6. **Pathfinding A\*** — los enemigos necesitan perseguirte por la mazmorra.
   Implementa A* sobre la grid (ver receta 08 para la variante con `mp_grid`).
7. **Hambre / antorcha** — recursos que se agotan con los turnos. Es lo que
   convierte un roguelike de "explorar todo" en "gestionar el riesgo".
8. **Modo *daily run*** — semilla del día (derivada de la fecha) y tabla de
   clasificación online. Todos juegan el mismo mapa.

**Cuándo pasar a otra receta:** el patrón grid → generar → validar → poblar
es exactamente el que usa el tower defense (grid + pathfinding) y el
metroidvania (salas prefabricadas conectadas).

---

## 9. Fuentes

- Manual oficial — `random_set_seed` / `random_get_seed` / `randomize` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Random_Functions.htm
- Manual oficial — Tilemap layers (`tilemap_set`, `tilemap_get_at_pixel`,
  `layer_tilemap_get_id`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers.htm
- Manual oficial — `json_stringify` / `json_parse` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling/Encoding_And_Hashing.htm
- Manual oficial — `point_distance`, `dcos`, `dsin` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Angles_And_Distance.htm
- Berlin Interpretation (definición canónica de roguelike, 2008)
- **How To Optimise Your Games** (tutorial oficial: arrays vs estructuras de
  datos, coste de instancias) —
  https://gamemaker.io/tutorials/how-to-optimise-your-games
- **GMRoomLoader** de Gleb Tsereteli (rooms infinitas y carga por regiones) —
  recomendado en la guía oficial de inicio
- Plantilla oficial **Survivor** del IDE (New → Game → Template)
