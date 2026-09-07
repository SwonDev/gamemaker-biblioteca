# 07 — Puzzle / Match-3

> **Dificultad:** media
> Es la receta que te enseña a separar **lógica** de **vista**. El tablero es
> un array de números; los sprites son solo una forma de dibujarlo.

---

## 1. Visión general

Un puzzle de Match-3 (Candy Crush, Bejeweled, Puzzle Quest) es un ejercicio de
**máquina de estados sobre una matriz**, con una capa de animación encima que
tiene que mentir de forma convincente.

El error número uno es intentar implementarlo con instancias: una instancia
por ficha. Funciona hasta que necesitas buscar matches, y entonces descubres
que recorrer instancias por posición es lento, frágil y difícil de testear.

**Lo que define al género:**

- Un tablero de fichas con tipos.
- Intercambiar dos fichas adyacentes para formar 3 o más en línea.
- Las fichas eliminadas caen y se rellenan, provocando **cascadas**.
- Las cascadas son la principal fuente de satisfacción (y de puntuación).

**Referencias hechas en GameMaker:** *Bejeweled* (el original), *Candy Crush
Saga*, *Puzzle Quest*, *10000000*, *You Must Build A Boat*. GameMaker tiene
una **plantilla oficial de Match 3** (IDE → New → Game → Template) que es la
referencia más directa que existe.

**Subgéneros y variantes:**

| Variante | Rasgo |
|---|---|
| Clásico por turnos | Sin límite de tiempo (Bejeweled) |
| Con movimientos limitados | N movimientos para un objetivo (Candy Crush) |
| Con tiempo | Contrarreloj |
| *Tile-matching* competitivo | Vs. otro jugador (Puzzle Fighter) |
| Con combate | Las matches hacen daño (Puzzle Quest) |

---

## 2. Arquitectura recomendada

### La separación clave: modelo / vista

```
MODELO (puro, testeable, sin sprites)
└── Board: array 2D de enteros
    ├── grid[y][x]  → tipo de ficha (0 = vacío)
    └── operaciones: find_matches, apply_gravity, refill

VISTA (lee el modelo y lo dibuja)
└── objTile por celda, que solo sabe:
    ├── qué celda del modelo representa
    └── hacia qué posición de pantalla debe interpolarse
```

**Regla de oro:** la lógica **nunca** pregunta a las instancias. Las instancias
leen la lógica.

### Jerarquía de objetos

```
objBoard            (controller: dueño del modelo, orquesta los estados)
objTile             (una ficha: representa una celda, se anima)
objInputHandler     (detecta el arrastre / clic)
objScorePopup       (texto flotante de puntuación)
objParticleBurst    (explosión al eliminar fichas)
```

### Estados del tablero

```
IDLE        → esperando input del jugador
SWAPPING    → animando el intercambio de dos fichas
CHECKING    → buscando matches en el modelo
CLEARING    → animando la eliminación
FALLING     → animando la caída y el rellenado
             → vuelve a CHECKING (cascada)
SHUFFLING   → no hay movimientos posibles: barajar
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `Board` | Array 2D + toda la lógica pura del puzzle |
| `Match` | Un grupo de celdas que forman una línea |
| `SwapResult` | Resultado de un intercambio: válido, matches, cascadas |

---

## 3. El bucle central (core loop)

```
┌─ Step de objBoard (máquina de estados) ──────────────────┐
│ IDLE                                                      │
│   → el jugador selecciona e intercambia dos fichas        │
│   → estado = SWAPPING                                     │
├──────────────────────────────────────────────────────────┤
│ SWAPPING                                                  │
│   → animar (12 frames)                                    │
│   → al terminar: intercambiar en el MODELO                │
│   → estado = CHECKING                                     │
├──────────────────────────────────────────────────────────┤
│ CHECKING                                                  │
│   → matches = board.find_matches()                        │
│   → si hay matches: estado = CLEARING                     │
│   → si NO: deshacer el intercambio, volver a IDLE         │
├──────────────────────────────────────────────────────────┤
│ CLEARING                                                  │
│   → dar puntos, spawnear partículas                       │
│   → poner las celdas a 0 en el MODELO                     │
│   → estado = FALLING                                      │
├──────────────────────────────────────────────────────────┤
│ FALLING                                                   │
│   → board.apply_gravity()  (el modelo ya está resuelto)   │
│   → board.refill()                                        │
│   → animar la caída de las vistas                         │
│   → al terminar: cascada++ ; estado = CHECKING            │
└──────────────────────────────────────────────────────────┘
```

**Nota crítica:** `apply_gravity()` y `refill()` operan **inmediatamente** sobre
el modelo. La animación de caída es solo visual: las vistas interpolan hacia
la posición que el modelo ya decidió. Si intentas animar la caída y resolver la
gravedad a la vez, el código se vuelve intratable.

---

## 4. Sistemas clave

### 4.1 Representación del tablero

```gml
// grid[columna][fila] — elige UNA y sé consistente
grid[x][y] = tipo;   // 0 = vacío, 1..N = tipos de ficha
```

Yo uso `grid[x][y]` (columna primero) porque es como se indexa visualmente
(x = columna). Lo importante es no mezclar.

Guarda también el array de vistas alineado: `tiles[x][y]` → instancia.

### 4.2 Detección de matches

Dos pasadas: horizontal y vertical. Para cada celda, cuenta cuántas fichas
iguales hay consecutivas hacia la derecha / hacia abajo. Si ≥ 3, es match.

```gml
// Horizontal
for (var _x = 0; _x < ancho; _x++)
{
    for (var _y = 0; _y < alto; _y++)
    {
        var _tipo = grid[_x][_y];
        if (_tipo == 0) continue;
        var _cuenta = 1;
        while (_x + _cuenta < ancho && grid[_x + _cuenta][_y] == _tipo) _cuenta++;
        if (_cuenta >= 3) {
            // registrar match
        }
    }
}
```

**Cuidado con las coincidencias superpuestas:** una línea de 5 en horizontal
que además forma parte de una cruz. La solución estándar es usar un set de
"a eliminar" (una grid booleana) y marcar en vez de insertar en una lista. Así
una celda en forma de T se marca una sola vez.

### 4.3 Cascadas

Tras limpiar, la gravedad mueve fichas hacia abajo y el hueco superior se
rellena con fichas nuevas. Eso puede generar matches nuevos: es una cascada.

Cada nivel de cascada multiplica la puntuación (x1, x2, x3...). Las cascadas
largas son el momento de mayor placer del género y deben celebrarse:
partículas extra, sonido ascendente, texto "¡CASCADA x4!".

### 4.4 Gravedad

```gml
// Para cada columna, de abajo arriba: bajar fichas
for x:
    escribir_y = alto - 1
    for y = alto-1 → 0:
        if grid[x][y] != 0:
            grid[x][escribir_y] = grid[x][y]
            if escribir_y != y: grid[x][y] = 0
            escribir_y--
```

### 4.5 Detección de "sin movimientos"

Antes de que el jugador se quede atascado, comprueba si existe algún
intercambio válido. El algoritmo directo: prueba los 4 intercambios posibles
de cada celda (derecha y abajo bastan, por simetría), comprueba si generan
match, y deshace.

Es O(n²) pero con tableros de 8×8 son ~200 comprobaciones: instantáneo.

### 4.6 Shuffle

Si no hay movimientos, baraja. Pero **no barajes cambiando los sprites**:
baraja el array de tipos, y luego reasigna a las vistas. Y comprueba después
que el shuffle **no** genera matches gratis (sería regalar puntos) ni deja el
tablero sin movimientos otra vez.

### 4.7 Animación de piezas

Las vistas necesitan tres animaciones:

| Animación | Duración | Curva |
|---|---|---|
| Intercambio | 12 frames | `ease_inout_quad` |
| Intercambio inválido (ida y vuelta) | 20 frames | `ease_out_back` |
| Caída | proporcional a la distancia | `ease_out_quad` |
| Eliminación (encoger) | 10 frames | `ease_in_quad` |

Usa el sistema de `Tween` de la receta 15.

---

## 5. Código base

### 5.0 El modelo: `Board`

```gml
// ---------------------------------------------------------------------------
// scr_board
// ---------------------------------------------------------------------------

#macro VACIO 0

/// @func Board(_ancho, _alto, _num_tipos)
/// @desc Modelo puro del tablero. NO tiene sprites ni instancias.
function Board(_ancho, _alto, _num_tipos) constructor
{
    ancho     = _ancho;
    alto      = _alto;
    num_tipos = _num_tipos;

    grid = [];
    for (var _x = 0; _x < _ancho; _x++)
    {
        var _col = [];
        for (var _y = 0; _y < _alto; _y++) array_push(_col, VACIO);
        array_push(grid, _col);
    }

    /// @desc Rellena el tablero evitando matches iniciales.
    generar_inicial = function()
    {
        for (var _x = 0; _x < ancho; _x++)
        {
            for (var _y = 0; _y < alto; _y++)
            {
                var _intentos = 0;
                var _tipo;

                // Repetir hasta que no forme match con lo ya colocado
                do
                {
                    _tipo = irandom_range(1, num_tipos);
                    _intentos++;
                }
                until (!formaria_match(_x, _y, _tipo) || _intentos > 50);

                grid[_x][_y] = _tipo;
            }
        }
    };

    /// @desc ¿Poner _tipo en (x,y) formaría un match inmediato?
    ///       Solo mira hacia atrás (izquierda y arriba): lo ya colocado.
    formaria_match = function(_x, _y, _tipo)
    {
        // Dos a la izquierda iguales → match horizontal de 3
        if (_x >= 2 && grid[_x-1][_y] == _tipo && grid[_x-2][_y] == _tipo) return true;
        // Dos arriba iguales → match vertical de 3
        if (_y >= 2 && grid[_x][_y-1] == _tipo && grid[_x][_y-2] == _tipo) return true;
        return false;
    };

    get = function(_x, _y)
    {
        if (_x < 0 || _y < 0 || _x >= ancho || _y >= alto) return VACIO;
        return grid[_x][_y];
    };

    set = function(_x, _y, _valor)
    {
        if (_x < 0 || _y < 0 || _x >= ancho || _y >= alto) return false;
        grid[_x][_y] = _valor;
        return true;
    };

    /// @desc Intercambia dos celdas del modelo.
    swap = function(_x1, _y1, _x2, _y2)
    {
        var _t = grid[_x1][_y1];
        grid[_x1][_y1] = grid[_x2][_y2];
        grid[_x2][_y2] = _t;
    };

    /// @desc Encuentra TODOS los matches. Devuelve una grid booleana de
    ///       "a eliminar" más la lista de grupos encontrados.
    find_matches = function()
    {
        // Grid de marcado: evita contar dos veces una celda en forma de T/L
        var _marcar = [];
        for (var _x = 0; _x < ancho; _x++)
        {
            var _col = [];
            for (var _y = 0; _y < alto; _y++) array_push(_col, false);
            array_push(_marcar, _col);
        }

        var _grupos = [];

        // --- Horizontales ---------------------------------------------------
        for (var _y = 0; _y < alto; _y++)
        {
            var _x = 0;
            while (_x < ancho)
            {
                var _tipo = get(_x, _y);
                if (_tipo == VACIO) { _x++; continue; }

                var _longitud = 1;
                while (get(_x + _longitud, _y) == _tipo) _longitud++;

                if (_longitud >= 3)
                {
                    var _grupo = [];
                    for (var _i = 0; _i < _longitud; _i++)
                    {
                        _marcar[_x + _i][_y] = true;
                        array_push(_grupo, { x: _x + _i, y: _y });
                    }
                    array_push(_grupos, {
                        celdas: _grupo, tipo: _tipo,
                        direccion: "h", longitud: _longitud
                    });
                }
                _x += _longitud;
            }
        }

        // --- Verticales -----------------------------------------------------
        for (var _x = 0; _x < ancho; _x++)
        {
            var _y = 0;
            while (_y < alto)
            {
                var _tipo = get(_x, _y);
                if (_tipo == VACIO) { _y++; continue; }

                var _longitud = 1;
                while (get(_x, _y + _longitud) == _tipo) _longitud++;

                if (_longitud >= 3)
                {
                    var _grupo = [];
                    for (var _i = 0; _i < _longitud; _i++)
                    {
                        _marcar[_x][_y + _i] = true;
                        array_push(_grupo, { x: _x, y: _y + _i });
                    }
                    array_push(_grupos, {
                        celdas: _grupo, tipo: _tipo,
                        direccion: "v", longitud: _longitud
                    });
                }
                _y += _longitud;
            }
        }

        // --- Recoger las celdas marcadas -------------------------------------
        var _celdas = [];
        for (var _x = 0; _x < ancho; _x++)
            for (var _y = 0; _y < alto; _y++)
                if (_marcar[_x][_y]) array_push(_celdas, { x: _x, y: _y });

        return {
            celdas: _celdas,        // todas las celdas a eliminar (sin duplicados)
            grupos: _grupos,        // para detectar combos de 4, 5, forma de T...
            count:  array_length(_celdas)
        };
    };

    /// @desc Elimina las celdas dadas (las pone a VACIO).
    clear_cells = function(_celdas)
    {
        for (var _i = 0; _i < array_length(_celdas); _i++)
        {
            set(_celdas[_i].x, _celdas[_i].y, VACIO);
        }
    };

    /// @desc Aplica gravedad. Devuelve la lista de movimientos
    ///       { desde_x, desde_y, x, y } para que la vista los anime.
    apply_gravity = function()
    {
        var _movimientos = [];

        for (var _x = 0; _x < ancho; _x++)
        {
            var _escribir_y = alto - 1;

            for (var _y = alto - 1; _y >= 0; _y--)
            {
                if (grid[_x][_y] == VACIO) continue;

                if (_escribir_y != _y)
                {
                    // Mover hacia abajo
                    grid[_x][_escribir_y] = grid[_x][_y];
                    grid[_x][_y] = VACIO;

                    array_push(_movimientos, {
                        desde_x: _x, desde_y: _y,
                        x: _x,    y: _escribir_y
                    });
                }
                _escribir_y--;
            }
        }

        return _movimientos;
    };

    /// @devuelve array de { x, y, tipo } con las fichas nuevas creadas arriba
    refill = function()
    {
        var _nuevas = [];

        for (var _x = 0; _x < ancho; _x++)
        {
            for (var _y = 0; _y < alto; _y++)
            {
                if (grid[_x][_y] != VACIO) continue;

                grid[_x][_y] = irandom_range(1, num_tipos);
                array_push(_nuevas, { x: _x, y: _y, tipo: grid[_x][_y] });
            }
        }

        return _nuevas;
    };

    /// @desc ¿Existe algún intercambio que produzca un match?
    tiene_movimientos = function()
    {
        for (var _x = 0; _x < ancho; _x++)
        {
            for (var _y = 0; _y < alto; _y++)
            {
                // Solo derecha y abajo: por simetría cubre todos los casos
                if (_x < ancho - 1 && swap_produce_match(_x, _y, _x + 1, _y)) return true;
                if (_y < alto  - 1 && swap_produce_match(_x, _y, _x, _y + 1)) return true;
            }
        }
        return false;
    };

    /// @desc Comprueba un intercambio hipotético y lo deshace.
    swap_produce_match = function(_x1, _y1, _x2, _y2)
    {
        swap(_x1, _y1, _x2, _y2);

        // Comprobación directa y barata: ¿alguna de las dos celdas forma línea?
        var _hay = forma_linea_en(_x1, _y1) || forma_linea_en(_x2, _y2);

        swap(_x1, _y1, _x2, _y2);   // deshacer SIEMPRE
        return _hay;
    };

    /// @desc ¿La celda (x,y) es parte de una línea de 3 o más?
    forma_linea_en = function(_x, _y)
    {
        var _tipo = get(_x, _y);
        if (_tipo == VACIO) return false;

        // Horizontal: contar iguales a izquierda y derecha
        var _h = 1;
        var _i = _x - 1; while (get(_i, _y) == _tipo) { _h++; _i--; }
        _i = _x + 1;     while (get(_i, _y) == _tipo) { _h++; _i++; }
        if (_h >= 3) return true;

        // Vertical
        var _v = 1;
        _i = _y - 1; while (get(_x, _i) == _tipo) { _v++; _i--; }
        _i = _y + 1; while (get(_x, _i) == _tipo) { _v++; _i++; }

        return (_v >= 3);
    };

    /// @desc Baraja los tipos hasta que haya movimientos y no haya matches.
    shuffle = function()
    {
        var _intentos = 0;

        do
        {
            // Recoger todos los tipos
            var _tipos = [];
            for (var _x = 0; _x < ancho; _x++)
                for (var _y = 0; _y < alto; _y++)
                    array_push(_tipos, grid[_x][_y]);

            // Fisher-Yates
            for (var _i = array_length(_tipos) - 1; _i > 0; _i--)
            {
                var _j = irandom(_i);
                var _t = _tipos[_i];
                _tipos[_i] = _tipos[_j];
                _tipos[_j] = _t;
            }

            // Redistribuir
            var _k = 0;
            for (var _x = 0; _x < ancho; _x++)
                for (var _y = 0; _y < alto; _y++)
                {
                    grid[_x][_y] = _tipos[_k];
                    _k++;
                }

            _intentos++;

        } until ((find_matches().count == 0 && tiene_movimientos()) || _intentos > 100);

        return (_intentos <= 100);
    };
}
```

### 5.1 La vista: `objTile`

```gml
// ---------------------------------------------------------------------------
// objTile — Create
// ---------------------------------------------------------------------------
// Variables que fija objBoard al crearla:
grid_x = 0;
grid_y = 0;
tipo   = 1;

// Posición objetivo en píxeles
target_x = x;
target_y = y;

// Animación de eliminación
muriendo = false;
```

```gml
// ---------------------------------------------------------------------------
// objTile — Step
// ---------------------------------------------------------------------------
// Interpolar hacia la posición objetivo.
// La caída usa una aceleración suave, no lerp constante: se ve más natural.
x = lerp(x, target_x, 0.25);
y = lerp(y, target_y, 0.25);

if (muriendo && image_xscale > 0.05)
{
    image_xscale = lerp(image_xscale, 0, 0.30);
    image_yscale = image_xscale;
    image_alpha  = image_xscale;
}
```

```gml
// ---------------------------------------------------------------------------
// objTile — Draw
// ---------------------------------------------------------------------------
draw_sprite_ext(sprTiles, tipo - 1, x, y,
                image_xscale, image_yscale, 0, c_white, image_alpha);
```

### 5.2 `objBoard` — la máquina de estados

```gml
// ---------------------------------------------------------------------------
// objBoard — Create
// ---------------------------------------------------------------------------
enum BoardState { idle, swapping, checking, clearing, falling, shuffling }

ANCHO     = 8;
ALTO      = 8;
NUM_TIPOS = 6;
TILE      = 48;

ORIGEN_X = 64;
ORIGEN_Y = 64;

board = new Board(ANCHO, ALTO, NUM_TIPOS);
board.generar_inicial();

state       = BoardState.idle;
state_timer = 0;

// Cascada actual (para el multiplicador)
cascada       = 0;
puntuacion    = 0;
movimientos   = 30;      // límite de movimientos (0 = sin límite)

// Intercambio en curso
swap_a = noone;
swap_b = noone;

// Array de vistas: tiles[x][y]
tiles = [];
recrear_vistas();

/// @func recrear_vistas()
function recrear_vistas()
{
    // Limpiar las viejas
    for (var _x = 0; _x < ANCHO; _x++)
    {
        if (!is_array(tiles) || _x >= array_length(tiles)) continue;
        for (var _y = 0; _y < ALTO; _y++)
        {
            if (_y < array_length(tiles[_x]) && instance_exists(tiles[_x][_y]))
            {
                instance_destroy(tiles[_x][_y]);
            }
        }
    }

    tiles = [];
    for (var _x = 0; _x < ANCHO; _x++)
    {
        var _col = [];
        for (var _y = 0; _y < ALTO; _y++)
        {
            var _t = instance_create_depth(
                ORIGEN_X + _x * TILE + (TILE * 0.5),
                ORIGEN_Y + _y * TILE + (TILE * 0.5),
                0, objTile);

            _t.grid_x = _x;
            _t.grid_y = _y;
            _t.tipo   = board.get(_x, _y);
            _t.target_x = _t.x;
            _t.target_y = _t.y;

            array_push(_col, _t);
        }
        array_push(tiles, _col);
    }
}

/// @func pix_x(_grid_x)
function pix_x(_grid_x) { return ORIGEN_X + _grid_x * TILE + (TILE * 0.5); }

/// @func pix_y(_grid_y)
function pix_y(_grid_y) { return ORIGEN_Y + _grid_y * TILE + (TILE * 0.5); }
```

```gml
// ---------------------------------------------------------------------------
// objBoard — Step
// ---------------------------------------------------------------------------
state_timer++;

switch (state)
{
    case BoardState.idle:
        // El input se gestiona en el evento Mouse (ver más abajo)
        break;

    case BoardState.swapping:
        if (state_timer >= 12)
        {
            // Aplicar el intercambio al MODELO
            board.swap(swap_a.grid_x, swap_a.grid_y,
                       swap_b.grid_x, swap_b.grid_y);

            // Actualizar las referencias en el array de vistas
            tiles[swap_a.grid_x][swap_a.grid_y] = swap_b;
            tiles[swap_b.grid_x][swap_b.grid_y] = swap_a;

            // Intercambiar las coordenadas lógicas de las vistas
            var _tx = swap_a.grid_x, _ty = swap_a.grid_y;
            swap_a.grid_x = swap_b.grid_x; swap_a.grid_y = swap_b.grid_y;
            swap_b.grid_x = _tx;           swap_b.grid_y = _ty;

            set_state(BoardState.checking);
        }
        break;

    case BoardState.checking:
        var _matches = board.find_matches();

        if (_matches.count > 0)
        {
            cascada++;
            resolver_matches(_matches);
            set_state(BoardState.clearing);
        }
        else if (cascada > 0)
        {
            // Fin de la cascada: volver a la espera
            cascada = 0;

            if (movimientos > 0)
            {
                movimientos--;
                if (movimientos <= 0) final_partida();
            }

            if (!board.tiene_movimientos())
            {
                set_state(BoardState.shuffling);
            }
            else
            {
                set_state(BoardState.idle);
            }
        }
        else
        {
            // El intercambio NO produjo match: deshacerlo
            deshacer_swap();
        }
        break;

    case BoardState.clearing:
        if (state_timer >= 12)
        {
            // Caída: el modelo se resuelve YA, la vista lo anima después
            var _movs = board.apply_gravity();
            var _nuevas = board.refill();

            aplicar_movimientos_vista(_movs, _nuevas);

            set_state(BoardState.falling);
        }
        break;

    case BoardState.falling:
        if (state_timer >= 16)
        {
            set_state(BoardState.checking);
        }
        break;

    case BoardState.shuffling:
        if (state_timer >= 25)
        {
            board.shuffle();
            sincronizar_vistas();
            set_state(BoardState.idle);
        }
        break;
}

function set_state(_nuevo)
{
    state       = _nuevo;
    state_timer = 0;
}
```

```gml
// ---------------------------------------------------------------------------
// objBoard — resolver matches
// ---------------------------------------------------------------------------

function resolver_matches(_matches)
{
    // --- Puntuación con multiplicador de cascada ------------------------------
    var _base = 10;
    var _mult = cascada;

    // Bonus por grupos grandes
    for (var _i = 0; _i < array_length(_matches.grupos); _i++)
    {
        var _g = _matches.grupos[_i];
        var _bonus = 1.0;

        if      (_g.longitud >= 5) _bonus = 2.5;
        else if (_g.longitud == 4) _bonus = 1.5;

        // Punto central del grupo, para el popup
        var _px = 0, _py = 0;
        for (var _j = 0; _j < array_length(_g.celdas); _j++)
        {
            _px += _g.celdas[_j].x;
            _py += _g.celdas[_j].y;
        }
        _px /= array_length(_g.celdas);
        _py /= array_length(_g.celdas);

        var _puntos = round(_base * _g.longitud * _bonus * _mult);
        puntuacion += _puntos;

        fx_floating_text(pix_x(_px), pix_y(_py), string(_puntos), c_yellow);
    }

    // --- Feedback audiovisual --------------------------------------------------
    camera_shake(clamp(0.05 * cascada, 0.05, 0.30));
    audio_play_sound(sndMatch, 10, false);

    // Sonido ascendente con la cascada (muy satisfactorio)
    var _s = audio_play_sound(sndCascade, 8, false);
    audio_sound_pitch(_s, 1.0 + (cascada * 0.12));

    if (cascada >= 3)
    {
        fx_floating_text(room_width * 0.5, 80,
                         "¡CASCADA x" + string(cascada) + "!", c_orange);
    }

    // --- Eliminar en el modelo y marcar las vistas ------------------------------
    board.clear_cells(_matches.celdas);

    for (var _i = 0; _i < array_length(_matches.celdas); _i++)
    {
        var _c = _matches.celdas[_i];
        var _t = tiles[_c.x][_c.y];

        if (instance_exists(_t))
        {
            _t.muriendo = true;

            // Partículas del color de la ficha
            part_particles_create(objFx.ps, _t.x, _t.y, objFx.pt_spark, 8);

            // La vista se destruirá al terminar de encoger
            with (_t) { alarm[0] = 12; }
        }
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objBoard — aplicar movimientos a la vista
// ---------------------------------------------------------------------------

function aplicar_movimientos_vista(_movs, _nuevas)
{
    // --- 1. Fichas existentes que caen -----------------------------------------
    for (var _i = 0; _i < array_length(_movs); _i++)
    {
        var _m = _movs[_i];
        var _t = tiles[_m.desde_x][_m.desde_y];

        if (!instance_exists(_t)) continue;

        // Actualizar el array de vistas
        tiles[_m.x][_m.y] = _t;
        tiles[_m.desde_x][_m.desde_y] = noone;

        _t.grid_x  = _m.x;
        _t.grid_y  = _m.y;
        _t.target_x = pix_x(_m.x);
        _t.target_y = pix_y(_m.y);
    }

    // --- 2. Fichas nuevas: crearlas ARRIBA del tablero y que caigan -------------
    for (var _i = 0; _i < array_length(_nuevas); _i++)
    {
        var _n = _nuevas[_i];

        var _t = instance_create_depth(
            pix_x(_n.x),
            pix_y(_n.y) - (TILE * (_n.y + 2)),   // empieza más arriba
            0, objTile);

        _t.grid_x   = _n.x;
        _t.grid_y   = _n.y;
        _t.tipo     = _n.tipo;
        _t.target_x = pix_x(_n.x);
        _t.target_y = pix_y(_n.y);

        tiles[_n.x][_n.y] = _t;
    }
}

/// @func sincronizar_vistas()
/// @desc Tras un shuffle, reasignar tipos y posiciones a todas las vistas.
function sincronizar_vistas()
{
    for (var _x = 0; _x < ANCHO; _x++)
        for (var _y = 0; _y < ALTO; _y++)
        {
            var _t = tiles[_x][_y];
            if (!instance_exists(_t)) continue;

            _t.tipo      = board.get(_x, _y);
            _t.grid_x    = _x;
            _t.grid_y    = _y;
            _t.target_x  = pix_x(_x);
            _t.target_y  = pix_y(_y);
            _t.muriendo  = false;
            _t.image_xscale = 1;
            _t.image_yscale = 1;
            _t.image_alpha  = 1;
        }
}
```

### 5.3 Input: seleccionar e intercambiar

```gml
// ---------------------------------------------------------------------------
// objBoard — Mouse (Left Pressed)
// ---------------------------------------------------------------------------
if (state != BoardState.idle) exit;

var _gx = floor((mouse_x - ORIGEN_X) / TILE);
var _gy = floor((mouse_y - ORIGEN_Y) / TILE);

if (_gx < 0 || _gy < 0 || _gx >= ANCHO || _gy >= ALTO) exit;

if (seleccion == noone)
{
    seleccion = tiles[_gx][_gy];
    seleccion.image_alpha = 0.6;      // resaltar
}
else
{
    // ¿Es adyacente a la selección?
    var _dx = abs(_gx - seleccion.grid_x);
    var _dy = abs(_gy - seleccion.grid_y);

    if ((_dx == 1 && _dy == 0) || (_dx == 0 && _dy == 1))
    {
        // Intercambio válido
        swap_a = seleccion;
        swap_b = tiles[_gx][_gy];

        swap_a.image_alpha = 1;

        // Animar el intercambio en la vista
        swap_a.target_x = pix_x(swap_b.grid_x);
        swap_a.target_y = pix_y(swap_b.grid_y);
        swap_b.target_x = pix_x(swap_a.grid_x);
        swap_b.target_y = pix_y(swap_a.grid_y);

        seleccion = noone;
        set_state(BoardState.swapping);
    }
    else
    {
        // No adyacente: cambiar la selección
        seleccion.image_alpha = 1;
        seleccion = tiles[_gx][_gy];
        seleccion.image_alpha = 0.6;
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objBoard — deshacer un intercambio inválido
// ---------------------------------------------------------------------------
function deshacer_swap()
{
    if (swap_a == noone || swap_b == noone) { set_state(BoardState.idle); return; }

    // Volver a intercambiar las coordenadas lógicas
    var _tx = swap_a.grid_x, _ty = swap_a.grid_y;
    swap_a.grid_x = swap_b.grid_x; swap_a.grid_y = swap_b.grid_y;
    swap_b.grid_x = _tx;           swap_b.grid_y = _ty;

    tiles[swap_a.grid_x][swap_a.grid_y] = swap_a;
    tiles[swap_b.grid_x][swap_b.grid_y] = swap_b;

    // Animar la vuelta
    swap_a.target_x = pix_x(swap_a.grid_x);
    swap_a.target_y = pix_y(swap_a.grid_y);
    swap_b.target_x = pix_x(swap_b.grid_x);
    swap_b.target_y = pix_y(swap_b.grid_y);

    // Feedback: sonido de error sutil
    audio_play_sound(sndNoMatch, 6, false);

    swap_a = noone;
    swap_b = noone;
    set_state(BoardState.idle);
}
```

```gml
// ---------------------------------------------------------------------------
// objBoard — Create (añadir esto)
// ---------------------------------------------------------------------------
seleccion = noone;
```

```gml
// ---------------------------------------------------------------------------
// objTile — Alarm 0 (destruir tras encoger)
// ---------------------------------------------------------------------------
instance_destroy();
```

### 5.4 Puntuación y fin de partida

```gml
// ---------------------------------------------------------------------------
// scr_match3_score
// ---------------------------------------------------------------------------

/// @func final_partida()
function final_partida()
{
    global.game_over = true;

    // Guardar high score
    if (puntuacion > global.high_score)
    {
        global.high_score = puntuacion;
        // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
        // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
        // 14 - Persistencia y archivos.md §1.
        var _f = file_text_open_write(game_save_id + "m3_high.txt");
        file_text_write_string(_f, string(global.high_score));
        file_text_close(_f);
    }

    // Panel de resultados
    instance_create_depth(0, 0, -1000, objResultsPanel);
}

/// @func match3_cargar_high_score()
function match3_cargar_high_score()
{
    var _path = game_save_id + "m3_high.txt";
    if (file_exists(_path))
    {
        var _f = file_text_open_read(_path);
        global.high_score = real(file_text_read_string(_f));
        file_text_close(_f);
    }
    else
    {
        global.high_score = 0;
    }
}
```

---

## 6. Gestión del estado del jugador

```gml
// ---------------------------------------------------------------------------
// scr_match3_state
// ---------------------------------------------------------------------------

/// @func Match3State()
/// @desc Progreso del jugador entre partidas.
function Match3State() constructor
{
    puntuacion_total = 0;
    mejor_puntuacion = 0;
    nivel            = 1;
    movimientos_extra = 0;
    powerups = {
        bomba:     2,     // elimina una ficha y sus vecinas
        rayo:      1,     // elimina toda una fila
        shuffle:   1      // baraja el tablero
    };

    // Objetivos del nivel: { tipo_ficha: cantidad_a_eliminar }
    objetivos = {};
    progreso_objetivos = {};

    /// @desc Registra fichas eliminadas de un tipo para los objetivos.
    registrar_eliminadas = function(_tipo, _cantidad)
    {
        if (!variable_struct_exists(objetivos, string(_tipo))) return;

        var _k = string(_tipo);
        if (!variable_struct_exists(progreso_objetivos, _k))
        {
            progreso_objetivos[$ _k] = 0;
        }

        progreso_objetivos[$ _k] += _cantidad;
    };

    objetivos_cumplidos = function()
    {
        var _keys = variable_struct_get_names(objetivos);
        for (var _i = 0; _i < array_length(_keys); _i++)
        {
            var _k = _keys[_i];
            var _necesario = objetivos[$ _k];
            var _llevo = variable_struct_exists(progreso_objetivos, _k)
                ? progreso_objetivos[$ _k] : 0;

            if (_llevo < _necesario) return false;
        }
        return true;
    };

    usar_powerup = function(_id)
    {
        if (!variable_struct_exists(powerups, _id)) return false;
        if (powerups[$ _id] <= 0) return false;

        powerups[$ _id]--;
        return true;
    };

    serialize = function()
    {
        return {
            puntuacion_total: puntuacion_total,
            mejor_puntuacion: mejor_puntuacion,
            nivel: nivel,
            powerups: powerups,
            objetivos: objetivos,
            progreso_objetivos: progreso_objetivos
        };
    };

    static deserialize = function(_d)
    {
        var _s = new Match3State();
        _s.puntuacion_total   = _d.puntuacion_total;
        _s.mejor_puntuacion   = _d.mejor_puntuacion;
        _s.nivel              = _d.nivel;
        _s.powerups           = _d.powerups;
        _s.objetivos          = _d.objetivos;
        _s.progreso_objetivos = _d.progreso_objetivos;
        return _s;
    };
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Implementar el tablero con instancias | Búsqueda de matches lentísima y frágil | Modelo en array 2D; las vistas solo dibujan |
| Animar la caída y resolver la gravedad a la vez | Código imposible de depurar | Resuelve el modelo YA; la vista interpola |
| Insertar celdas en una lista sin deduplicar | Una celda en forma de T se elimina dos veces y da puntos dobles | Grid booleana de marcado |
| Generar el tablero inicial al azar sin filtro | Empiezas con matches ya hechos y puntos gratis | `generar_inicial()` que evita matches |
| No comprobar "sin movimientos" | El jugador se queda atascado para siempre | `tiene_movimientos()` tras cada cascada |
| `shuffle()` que genera matches gratis | Regalas puntos sin que el jugador haga nada | Repite el shuffle hasta que no haya matches |
| Intercambiar las referencias de `tiles[][]` mal | Las vistas apuntan a celdas equivocadas tras el swap | Intercambia en el array **y** en `grid_x/grid_y` |
| Destruir las vistas inmediatamente al limpiar | Las fichas desaparecen de golpe: sin sensación | `muriendo = true` → encoger → destruir con alarm |
| `lerp` constante para la caída | Las fichas "flotan" en vez de caer | Acelera: `lerp` con factor creciente o `ease_in_quad` |
| Permitir input durante las cascadas | El jugador rompe el estado del tablero | `state != idle → exit` en el input |
| Alto Score guardado como string sin `real()` | Comparaciones de texto: "900" > "1000" | `real()` al leer |

---

## 8. Cómo escalarlo

1. **Fichas especiales** — al hacer match de 4 creas una "bomba"; de 5 una
   "bomba de color"; en forma de L una "bomba cruz". Es la mecánica que
   diferencia Candy Crush de Bejeweled.
2. **Objetivos de nivel** — "elimina 20 rojas y 15 azules en 25 movimientos".
   Ya tienes el struct `objetivos` preparado.
3. **Obstáculos** — celdas bloqueadas, hielo que hay que romper dos veces,
   fichas que no caen.
4. **Tableros de formas irregulares** — una grid con celdas marcadas como
   "fuera del tablero" en vez de un rectángulo perfecto.
5. **Modo contrarreloj** — sustituye el límite de movimientos por tiempo.
6. **Combate por match** (Puzzle Quest) — cada match hace daño a un enemigo;
   los matches de 4 dan turno extra.
7. **Tabla de clasificación online** — ver receta 14.
8. **Editor de niveles** — los objetivos son structs, así que serializarlos a
   JSON y construir un editor es directo.

**Cuándo pasar a otra receta:** el patrón "modelo en arrays + vista que
interpola" es exactamente el que necesitas para la estrategia (receta 13) y
para el survival con inventario (receta 09).

---

## 9. Fuentes

- **Plantilla oficial Match 3** del IDE (New → Game → Template) — juego
  completo comentado, la referencia más directa
- **Plantilla oficial Card Game** del IDE (New → Game → Template) — patrones
  de tablero y mano reutilizables
- Manual oficial — Funciones de array (`array_push`, `array_delete`,
  `array_length`, `array_create`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm
- Manual oficial — `instance_create_depth`, `instance_exists` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Instances.htm
- Manual oficial — Eventos de ratón y `mouse_x` / `mouse_y` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/Mouse_Input.htm
- Manual oficial — `audio_sound_pitch`, `audio_play_sound` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio.htm
- Receta propia: **15 — Game feel y juice** (sistema de `Tween`, partículas,
  texto flotante, shake)
- Receta propia: **05 — Roguelike** (Fisher-Yates, grids 2D)
