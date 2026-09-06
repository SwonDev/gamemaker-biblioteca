# 09 — Survival y crafting

> **Dificultad:** avanzada
> El género que más te exige como ingeniero: mundos grandes, muchos sistemas que
> interactúan, y guardado de cantidades industriales de estado.

---

## 1. Visión general

Un survival se define por un bucle de **escasez → trabajo → alivio temporal**.
Si el jugador nunca pasa hambre, no hay supervivencia. Si el trabajo no alivia
la escasez, no hay progreso.

**Lo que define al género:**

- **Necesidades que se degradan** (hambre, sed, frío, sueño, cordura).
- **Recolección y crafteo**: el mundo da materiales, el jugador los convierte
  en herramientas, las herramientas dan mejores materiales.
- **Un mundo que sigue existiendo** cuando no estás (o al menos que lo parece).
- **La muerte tiene coste real** pero casi nunca es permanente total.

**Referencias hechas en GameMaker:** *Don't Starve* (Klei, hecho con un motor
propio pero su diseño es el canon), *Minecraft* (no GM), *Terraria* (no GM).
GameMaker tiene una **plantilla oficial Survivor** (IDE → New → Game →
Template) que cubre la variante *bullet-heaven*, y la comunidad ha hecho
muchos survival tipo *Forager*.

**Subgéneros:**

| Subgénero | Foco |
|---|---|
| Supervivencia pura | Necesidades y clima |
| *Crafting sandbox* | Construir sin presión |
| *Base defense* | Supervivencia + oleadas nocturnas |
| *Bullet heaven* (Vampire Survivors) | Oleadas automáticas, builds |
| *Farming sim* | Supervivencia sin amenaza (Stardew) |

---

## 2. Arquitectura recomendada

### Jerarquía de objetos

```
objPlayer
objResourceNode      (árbol, roca, mineral, arbusto)
├── objTree
├── objRock
└── objBush
objItemDrop          (lo que suelta un nodo al romperse)
objCraftingStation   (fogata, banco de trabajo, fragua)
objStructure         (padre de construcciones)
├── objWall
├── objFloor
├── objStorageChest
└── objBed
objNeeds             (controller: hambre, sed, temperatura)
objTimeOfDay         (ciclo día/noche)
objChunkManager      (carga/descarga de regiones)
objWorldGen          (genera el mundo por chunks)
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `Inventory` | Pilas de objetos con capacidad (reutiliza la receta 04) |
| `Recipe` | Ingredientes → producto, con estación requerida |
| `Needs` | Necesidades con tasas de degradación |
| `Chunk` | Una región del mundo: tiles + entidades serializadas |
| `WorldData` | Semilla, chunks modificados, estructuras colocadas |

---

## 3. El bucle central (core loop)

```
┌─ Begin Step ─────────────────────────────────────────────┐
│ 1. objTimeOfDay: avanzar el reloj, actualizar la luz      │
│ 2. objNeeds: degradar hambre/sed/calor según la actividad │
└──────────────────────────────────────────────────────────┘
┌─ Step ───────────────────────────────────────────────────┐
│ 3. Movimiento del jugador                                 │
│ 4. Interacción: ¿golpear nodo? ¿usar estación? ¿construir?│
│ 5. objChunkManager: cargar chunks cercanos, descargar     │
│    los lejanos (serializando su estado)                   │
│ 6. Actualizar estructuras (cultivos que crecen, fuego)    │
│ 7. IA de criaturas                                        │
│ 8. Comprobar necesidades críticas → daño al jugador       │
│ 9. HUD: inventario, barras de necesidades, reloj          │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 Recolección

Un nodo de recurso tiene: vida (golpes necesarios), herramienta requerida,
tabla de drops.

```gml
nodo = {
    hp: 3,
    herramienta: "hacha",
    drops: LootTable([...]),
    respawn_frames: 3600     // opcional
};
```

La clave del *feel*: cada golpe debe dar feedback inmediato (sacudida del
sprite, partículas del color del material, sonido) y el nodo debe **mostrar**
su desgaste (cambios de sprite, grietas).

### 4.2 Inventario por pila

Reutiliza el `Inventory` de la receta 04. Para un survival añade:

- **Capacidad por pila** (madera apila 99, herramientas no apilan).
- **Peso** (opcional; añade decisiones de qué llevar).
- **Durabilidad** en herramientas.

### 4.3 Recetas de crafteo

Una receta es: lista de ingredientes + producto + estación requerida.

```gml
receta = {
    id: "hacha_piedra",
    estacion: "banco",          // o "" para crafteo a mano
    ingredientes: { madera: 5, piedra: 3 },
    producto: { id: "hacha_piedra", cantidad: 1 },
    tiempo: 60                  // frames (0 = instantáneo)
};
```

**Comprobación eficiente:** tener una función `puede_craftear()` que no
modifique nada, y `craftear()` que sí consuma. Nunca consumas primero y
compruebes después.

### 4.4 Necesidades

Cada necesidad es un valor 0-100 que baja con el tiempo a una tasa que
depende de la actividad:

```gml
hambre -= tasa_base * multiplicador_actividad * dt;
```

| Necesidad | Se vacía al | Al llegar a 0 |
|---|---|---|
| Hambre | Comer | Daño lento + penalización de velocidad |
| Sed | Beber | Daño rápido |
| Calor | Fuego, ropa, refugio | Daño en zonas frías / de noche |
| Sueño | Dormir | Visión reducida, alucinaciones |

**La regla de diseño:** una necesidad al 0 debe **molestar**, no matar
instantáneamente. El jugador necesita margen para reaccionar.

### 4.5 Construcción

Sistema de *ghost preview*: el jugador ve la estructura en transparente,
verde si es válida y roja si no. Validez = terreno adecuado + sin solaparse +
materiales suficientes.

Al colocar, la estructura se añade a una grid de construcción (para que nada
se solape) y se guarda en el estado del mundo.

### 4.6 Chunking

Un mundo grande no cabe entero en memoria. Divídelo en chunks de N×N tiles
(típicamente 16×16 o 32×32):

| Estado | Qué hay en memoria |
|---|---|
| **Cargado** | Instancias activas + tilemap |
| **Serializado** | Solo un struct con los cambios |
| **No generado** | Nada; se genera al acercarse |

**Regla fundamental:** guarda **solo las diferencias** (diff) respecto a lo
que genera el generador procedural. Con la semilla, el chunk se regenera
igual; solo necesitas recordar que el jugador taló ese árbol.

```gml
chunk_diff = {
    tiles_modificados: { "12,7": 3, "12,8": 3 },
    nodos_talados: ["tree_0042", "rock_0017"],
    estructuras: [ {...}, {...} ]
};
```

Uso de `instance_deactivate_region` y `instance_activate_region`:

```gml
instance_deactivate_region(x1, y1, w, h, inside, notme);
instance_activate_region(left, top, width, height, inside);
```

### 4.7 Ciclo día/noche

Un valor 0-1 que recorre el día. Controla:

- Luz ambiente (una superficie oscura con alfa variable).
- Temperatura (más frío de noche).
- Spawn de criaturas (hostiles de noche).

---

## 5. Código base

### 5.0 Necesidades

```gml
// ---------------------------------------------------------------------------
// scr_needs
// ---------------------------------------------------------------------------

/// @func Needs()
/// @desc Necesidades del jugador con degradación por actividad.
function Needs() constructor
{
    // Todas 0..100
    hambre  = 100;
    sed     = 100;
    calor   = 100;
    sueño   = 100;
    cordura = 100;

    // Tasas de degradación por frame (a 60 fps)
    // Valores típicos: un día completo = 1200 frames → ~0.05/frame para
    // vaciarse en algo más de medio día.
    tasa_hambre  = 0.030;
    tasa_sed     = 0.045;
    tasa_sueño   = 0.018;
    tasa_cordura = 0.008;

    // Multiplicadores por actividad
    mult_actividad = 1.0;    // 1.0 quieto, 2.0 corriendo, 2.5 talando
    mult_clima     = 1.0;    // frío → la temperatura baja más rápido

    /// @desc Actualiza un frame.
    update = function(_actividad, _temperatura)
    {
        mult_actividad = (_actividad == undefined) ? 1.0 : _actividad;

        hambre = max(0, hambre - (tasa_hambre  * mult_actividad));
        sed    = max(0, sed    - (tasa_sed     * mult_actividad));
        sueño  = max(0, sueño  - (tasa_sueño));

        // El calor depende de la temperatura exterior
        if (_temperatura != undefined)
        {
            if (_temperatura < 0.3)
            {
                // Hace frío: pierdes calor
                calor = max(0, calor - (0.05 * (0.3 - _temperatura) * 3));
            }
            else if (_temperatura > 0.7)
            {
                // Hace calor: pierdes "calor" también (es deshidratación)
                calor = max(0, calor - (0.03 * (_temperatura - 0.7) * 3));
            }
            else
            {
                // Temperatura confortable: se recupera despacio
                calor = min(100, calor + 0.08);
            }
        }

        // La cordura cae de noche y con necesidades bajas
        var _penalizacion = 1.0;
        if (hambre < 20 || sed < 20) _penalizacion += 1.5;
        if (global.es_de_noche)      _penalizacion += 1.0;

        cordura = max(0, cordura - (tasa_cordura * _penalizacion));
    };

    /// @desc Devuelve el daño por frame que debe recibir el jugador.
    daño_por_frame = function()
    {
        var _d = 0;
        if (sed     <= 0) _d += 0.05;
        if (hambre  <= 0) _d += 0.03;
        if (calor   <= 0) _d += 0.04;
        return _d;
    };

    /// @desc Multiplicador de velocidad según las necesidades.
    multiplicador_velocidad = function()
    {
        var _m = 1.0;
        if (hambre < 25) _m *= 0.75;
        if (sed    < 25) _m *= 0.70;
        if (sueño  < 15) _m *= 0.60;
        return _m;
    };

    /// @desc ¿Alguna necesidad está en zona crítica? (para la UI)
    alguna_critica = function()
    {
        return (hambre < 20) || (sed < 20) || (calor < 20) ||
               (sueño < 15) || (cordura < 20);
    };

    consumir = function(_item_efecto)
    {
        if (variable_struct_exists(_item_efecto, "hambre")) hambre = min(100, hambre + _item_efecto.hambre);
        if (variable_struct_exists(_item_efecto, "sed"))    sed    = min(100, sed    + _item_efecto.sed);
        if (variable_struct_exists(_item_efecto, "calor"))  calor  = min(100, calor  + _item_efecto.calor);
        if (variable_struct_exists(_item_efecto, "sueño"))  sueño  = min(100, sueño  + _item_efecto.sueño);
    };

    serialize = function()
    {
        return { hambre: hambre, sed: sed, calor: calor,
                 sueño: sueño, cordura: cordura };
    };

    static deserialize = function(_d)
    {
        var _n = new Needs();
        _n.hambre  = _d.hambre;
        _n.sed     = _d.sed;
        _n.calor   = _d.calor;
        _n.sueño   = _d.sueño;
        _n.cordura = _d.cordura;
        return _n;
    };
}
```

### 5.1 Recetas de crafteo

```gml
// ---------------------------------------------------------------------------
// scr_crafting
// ---------------------------------------------------------------------------

/// @func Recipe(_id, _nombre, _estacion, _ingredientes, _producto, _tiempo)
function Recipe(_id, _nombre, _estacion, _ingredientes, _producto, _tiempo) constructor
{
    id           = _id;
    nombre       = _nombre;
    estacion     = _estacion;     // "" = a mano
    ingredientes = _ingredientes; // { madera: 5, piedra: 3 }
    producto     = _producto;     // { id: "hacha", cantidad: 1 }
    tiempo       = (_tiempo == undefined) ? 0 : _tiempo;

    /// @desc ¿Tiene el inventario los materiales? No modifica nada.
    puede_craftear = function(_inventario)
    {
        var _keys = variable_struct_get_names(ingredientes);

        for (var _i = 0; _i < array_length(_keys); _i++)
        {
            var _mat = _keys[_i];
            var _necesario = ingredientes[$ _mat];

            if (!_inventario.has(_mat, _necesario)) return false;
        }
        return true;
    };

    /// @desc Consume los materiales y devuelve el producto.
    craftear = function(_inventario)
    {
        if (!puede_craftear(_inventario)) return false;

        var _keys = variable_struct_get_names(ingredientes);
        for (var _i = 0; _i < array_length(_keys); _i++)
        {
            var _mat = _keys[_i];
            _inventario.remove(_mat, ingredientes[$ _mat]);
        }

        _inventario.add(producto.id, producto.cantidad);
        return true;
    };

    /// @desc Lista legible de materiales que faltan (para la UI).
    materiales_faltantes = function(_inventario)
    {
        var _faltan = [];
        var _keys = variable_struct_get_names(ingredientes);

        for (var _i = 0; _i < array_length(_keys); _i++)
        {
            var _mat = _keys[_i];
            var _necesario = ingredientes[$ _mat];
            var _tengo = _inventario.count(_mat);

            if (_tengo < _necesario)
            {
                array_push(_faltan, {
                    material:  _mat,
                    necesario: _necesario,
                    tengo:     _tengo
                });
            }
        }
        return _faltan;
    };
}

/// @func recipes_init()
function recipes_init()
{
    global.recipes = {};

    global.recipes.hacha_piedra = new Recipe(
        "hacha_piedra", "Hacha de piedra", "",
        { madera: 5, piedra: 3 },
        { id: "hacha_piedra", cantidad: 1 }, 0);

    global.recipes.pico_piedra = new Recipe(
        "pico_piedra", "Pico de piedra", "",
        { madera: 5, piedra: 5 },
        { id: "pico_piedra", cantidad: 1 }, 0);

    global.recipes.cuerda = new Recipe(
        "cuerda", "Cuerda", "",
        { fibra: 6 },
        { id: "cuerda", cantidad: 2 }, 0);

    global.recipes.fogata = new Recipe(
        "fogata", "Fogata", "",
        { madera: 10, piedra: 4 },
        { id: "fogata", cantidad: 1 }, 0);

    global.recipes.pared = new Recipe(
        "pared", "Pared de madera", "banco",
        { madera: 8 },
        { id: "pared", cantidad: 2 }, 30);

    global.recipes.cofre = new Recipe(
        "cofre", "Cofre", "banco",
        { madera: 20, cuerda: 2 },
        { id: "cofre", cantidad: 1 }, 60);

    global.recipes.hacha_hierro = new Recipe(
        "hacha_hierro", "Hacha de hierro", "fragua",
        { madera: 5, hierro: 8, cuerda: 1 },
        { id: "hacha_hierro", cantidad: 1 }, 120);
}

/// @func recipe_get(_id)
function recipe_get(_id)
{
    if (!variable_struct_exists(global.recipes, _id)) return undefined;
    return global.recipes[$ _id];
}
```

### 5.2 Nodo de recurso

```gml
// ---------------------------------------------------------------------------
// objResourceNode — Create
// ---------------------------------------------------------------------------
// Variables que fija el generador del mundo:
tipo_nodo    = "tree";
hp           = 5;
hp_max       = 5;
herramienta  = "";           // "" = con la mano, "hacha", "pico"...
drops        = [];           // array de { id, min, max, peso }
unique_id    = "";           // para recordar que ya se taló

// Solo visual
shake        = 0;
```

```gml
// ---------------------------------------------------------------------------
// objResourceNode — Step
// ---------------------------------------------------------------------------
if (shake > 0)
{
    shake--;
    x = x_base + irandom_range(-2, 2);
}
else
{
    x = x_base;
}
```

```gml
// ---------------------------------------------------------------------------
// objResourceNode — golpear(_daño, _herramienta)
// ---------------------------------------------------------------------------
function golpear(_daño, _herramienta)
{
    // ¿La herramienta es adecuada? Si no, daño reducido
    var _eficacia = 1.0;

    if (herramienta != "")
    {
        if (_herramienta == herramienta)          _eficacia = 2.0;
        else if (_herramienta != "")              _eficacia = 0.5;
        else                                       _eficacia = 0.3;   // a mano
    }

    hp -= _daño * _eficacia;
    shake = 6;

    // Feedback por capas
    squash_preset(self, "hit");
    part_particles_create(objFx.ps, x, y - 8, objFx.pt_blood, 4);

    var _s = audio_play_sound(sndChop, 8, false);
    audio_sound_pitch(_s, random_range(0.92, 1.08));

    if (_eficacia < 1.0)
    {
        fx_floating_text(x, y - 20, "Herramienta incorrecta", c_gray);
    }

    // ¿Se rompió?
    if (hp <= 0)
    {
        romper();
    }
    else
    {
        // Mostrar desgaste: cambiar de sprite según la vida restante
        var _fraccion = hp / hp_max;
        image_index = (_fraccion > 0.66) ? 0 : ((_fraccion > 0.33) ? 1 : 2);
    }
}

function romper()
{
    // --- Drops -----------------------------------------------------------------
    for (var _i = 0; _i < array_length(drops); _i++)
    {
        var _d = drops[_i];
        var _cantidad = irandom_range(_d.min, _d.max);

        for (var _j = 0; _j < _cantidad; _j++)
        {
            var _item = instance_create_layer(
                x + irandom_range(-12, 12),
                y + irandom_range(-6, 6),
                "Items", objItemDrop);

            _item.item_id = _d.id;

            // Pequeño impulso para que se vean salir
            _item.hspeed_init = random_range(-1.2, 1.2);
            _item.vspeed_init = random_range(-2.2, -0.8);
        }
    }

    // --- Registrar que se taló (para el chunk diff) -----------------------------
    if (unique_id != "")
    {
        objChunkManager.registrar_nodo_talado(unique_id);
    }

    // --- Feedback ---------------------------------------------------------------
    part_particles_create(objFx.ps, x, y, objFx.pt_dust, 14);
    camera_shake(0.12);
    audio_play_sound(sndTreeFall, 10, false);

    instance_destroy();
}
```

### 5.3 Construcción con ghost preview

```gml
// ---------------------------------------------------------------------------
// objBuildManager — Create
// ---------------------------------------------------------------------------
modo_construccion = false;
estructura_id     = "";
ghost_valido      = false;

#macro RANGO_CONSTRUCCION (CELL * 5)   // el jugador debe estar cerca de donde construye

// ---------------------------------------------------------------------------
// objBuildManager — Step
// ---------------------------------------------------------------------------
if (!modo_construccion) exit;

var _gx = (mouse_x div CELL) * CELL;
var _gy = (mouse_y div CELL) * CELL;
var _grid_x = _gx div CELL;
var _grid_y = _gy div CELL;

var _receta = recipe_get(estructura_id);

// ⚠️ Corregido (informe r3-2026-09-06, tema 56): la versión anterior de esta
// comprobación llamaba a `celda_construible()` y `punto_en_rango()`, dos
// funciones que no se definían en ningún sitio de este documento — quien
// copiara el snippet tal cual se encontraba con un error de "función no
// definida" al compilar. Además, el comentario de más abajo prometía "sin
// solaparse" pero nunca consultaba la rejilla de ocupación, así que dos
// estructuras podían colocarse en la misma celda. Las dos funciones
// inventadas se sustituyen por lo que YA existe: `objWorldGrid.ocupada()`
// (el struct `WorldGrid` de más abajo, verificado, es la única fuente de
// verdad sobre qué celda está libre) y `point_distance()` (función del
// runtime, verificada con `buscar.py`) para el rango de colocación.
ghost_valido = (_receta != undefined)
    && _receta.puede_craftear(global.inventory)
    && !objWorldGrid.ocupada(_grid_x, _grid_y)
    && point_distance(objPlayer.x, objPlayer.y, _gx, _gy) <= RANGO_CONSTRUCCION;

// --- Colocar ---------------------------------------------------------------------
if (mouse_check_button_pressed(mb_left) && ghost_valido)
{
    _receta.craftear(global.inventory);

    var _s = instance_create_depth(_gx + CELL * 0.5, _gy + CELL * 0.5,
                                   -_gy, objStructure);
    _s.tipo_estructura = estructura_id;
    _s.grid_x = _gx div CELL;
    _s.grid_y = _gy div CELL;

    // Registrar en la grid de construcción
    objWorldGrid.ocupar(_s.grid_x, _s.grid_y, _s);

    // Registrar en el chunk
    objChunkManager.registrar_estructura(_s);

    audio_play_sound(sndBuild, 10, false);
    squash_preset(_s, "pickup");

    modo_construccion = false;
}

// --- Cancelar con clic derecho / Escape ------------------------------------------
if (mouse_check_button_pressed(mb_right) || keyboard_check_pressed(vk_escape))
{
    modo_construccion = false;
}
```

```gml
// ---------------------------------------------------------------------------
// objBuildManager — Draw
// ---------------------------------------------------------------------------
if (!modo_construccion) exit;

var _gx = (mouse_x div CELL) * CELL;
var _gy = (mouse_y div CELL) * CELL;

var _spr = estructura_sprite(estructura_id);
if (_spr == noone) exit;

draw_sprite_ext(_spr, 0, _gx + CELL * 0.5, _gy + CELL * 0.5, 1, 1, 0,
                ghost_valido ? c_green : c_red, 0.6);

// Cuadrícula de ayuda
draw_set_alpha(0.2);
draw_set_color(ghost_valido ? c_green : c_red);
draw_rectangle(_gx, _gy, _gx + CELL, _gy + CELL, true);
draw_set_alpha(1);
```

```gml
// ---------------------------------------------------------------------------
// scr_world_grid
// ---------------------------------------------------------------------------

/// @func WorldGrid()
/// @desc Grid de ocupación de construcciones. Evita solapes.
function WorldGrid() constructor
{
    celdas = {};    // "x,y" → instancia (sparse: solo las ocupadas)

    clave = function(_x, _y) { return string(_x) + "," + string(_y); };

    ocupada = function(_x, _y)
    {
        return variable_struct_exists(celdas, clave(_x, _y));
    };

    ocupar = function(_x, _y, _inst)
    {
        celdas[$ clave(_x, _y)] = _inst;
    };

    liberar = function(_x, _y)
    {
        var _k = clave(_x, _y);
        if (variable_struct_exists(celdas, _k))
        {
            variable_struct_remove(celdas, _k);
        }
    };

    /// @desc Serializar (solo las ocupadas: eficiente)
    serialize = function()
    {
        var _out = [];
        var _keys = variable_struct_get_names(celdas);

        for (var _i = 0; _i < array_length(_keys); _i++)
        {
            var _k = _keys[_i];
            var _s = celdas[$ _k];

            if (!instance_exists(_s)) continue;

            array_push(_out, {
                tipo: _s.tipo_estructura,
                x: _s.grid_x,
                y: _s.grid_y
            });
        }
        return _out;
    };
}
```

### 5.4 Chunking

```gml
// ---------------------------------------------------------------------------
// scr_chunking
// ---------------------------------------------------------------------------

#macro CHUNK_TILES 16        // tiles por lado del chunk
#macro CHUNK_PX    (CHUNK_TILES * CELL)
#macro RADIO_CARGA 2         // chunks cargados a cada lado del jugador

/// @func ChunkData(_cx, _cy)
/// @diff Solo guarda las DIFERENCIAS respecto a lo que genera el mundo.
function ChunkData(_cx, _cy) constructor
{
    cx = _cx;
    cy = _cy;

    tiles_modificados = {};   // "x,y" → tile_id
    nodos_talados     = [];   // unique_ids
    estructuras       = [];   // { tipo, x, y }
    items_en_suelo    = [];   // { id, x, y }

    modificar_tile = function(_x, _y, _tile)
    {
        tiles_modificados[$ (string(_x) + "," + string(_y))] = _tile;
    };

    talar_nodo = function(_unique_id)
    {
        array_push(nodos_talados, _unique_id);
    };

    añadir_estructura = function(_tipo, _x, _y)
    {
        array_push(estructuras, { tipo: _tipo, x: _x, y: _y });
    };

    esta_vacio = function()
    {
        return (struct_names_count(tiles_modificados) == 0)
            && (array_length(nodos_talados) == 0)
            && (array_length(estructuras)   == 0)
            && (array_length(items_en_suelo) == 0);
    };

    serialize = function()
    {
        return {
            cx: cx, cy: cy,
            tiles: tiles_modificados,
            talados: nodos_talados,
            estructuras: estructuras,
            items: items_en_suelo
        };
    };

    static deserialize = function(_d)
    {
        var _c = new ChunkData(_d.cx, _d.cy);
        _c.tiles_modificados = _d.tiles;
        _c.nodos_talados     = _d.talados;
        _c.estructuras       = _d.estructuras;
        _c.items_en_suelo    = _d.items;
        return _c;
    };
}
```

```gml
// ---------------------------------------------------------------------------
// objChunkManager — Create
// ---------------------------------------------------------------------------
chunks = {};              // "cx,cy" → ChunkData
chunks_cargados = {};     // "cx,cy" → true

chunk_key = function(_cx, _cy) { return string(_cx) + "," + string(_cy); };

/// @func chunk_get(_cx, _cy)
chunk_get = function(_cx, _cy)
{
    var _k = chunk_key(_cx, _cy);
    if (!variable_struct_exists(chunks, _k))
    {
        chunks[$ _k] = new ChunkData(_cx, _cy);
    }
    return chunks[$ _k];
};

/// @func registrar_nodo_talado(_unique_id)
registrar_nodo_talado = function(_unique_id)
{
    var _cx = other.x div CHUNK_PX;
    var _cy = other.y div CHUNK_PX;
    chunk_get(_cx, _cy).talar_nodo(_unique_id);
};

/// @func registrar_estructura(_struct)
registrar_estructura = function(_struct)
{
    var _cx = _struct.x div CHUNK_PX;
    var _cy = _struct.y div CHUNK_PX;
    chunk_get(_cx, _cy).añadir_estructura(_struct.tipo_estructura,
                                          _struct.grid_x, _struct.grid_y);
};
```

```gml
// ---------------------------------------------------------------------------
// objChunkManager — Step (cada 30 frames, no cada frame)
// ---------------------------------------------------------------------------
if (global.frame_count mod 30 != 0) exit;

var _pcx = objPlayer.x div CHUNK_PX;
var _pcy = objPlayer.y div CHUNK_PX;

// --- 1. Descargar los chunks que salieron del radio -------------------------
var _cargados = variable_struct_get_names(chunks_cargados);

for (var _i = 0; _i < array_length(_cargados); _i++)
{
    var _k = _cargados[_i];
    var _pos = string_split(_k, ",");
    var _cx = real(_pos[0]);
    var _cy = real(_pos[1]);

    if (abs(_cx - _pcx) > RADIO_CARGA || abs(_cy - _pcy) > RADIO_CARGA)
    {
        descargar_chunk(_cx, _cy);
        variable_struct_remove(chunks_cargados, _k);
    }
}

// --- 2. Cargar los chunks que entraron en el radio ---------------------------
for (var _dy = -RADIO_CARGA; _dy <= RADIO_CARGA; _dy++)
{
    for (var _dx = -RADIO_CARGA; _dx <= RADIO_CARGA; _dx++)
    {
        var _cx = _pcx + _dx;
        var _cy = _pcy + _dy;
        var _k  = chunk_key(_cx, _cy);

        if (!variable_struct_exists(chunks_cargados, _k))
        {
            cargar_chunk(_cx, _cy);
            chunks_cargados[$ _k] = true;
        }
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objChunkManager — cargar / descargar
// ---------------------------------------------------------------------------

/// @func cargar_chunk(_cx, _cy)
/// @desc Genera el terreno y aplica el diff guardado.
function cargar_chunk(_cx, _cy)
{
    var _px = _cx * CHUNK_PX;
    var _py = _cy * CHUNK_PX;

    // --- a) Generar el terreno a partir de la semilla del mundo ----------------
    //     Usamos un RNG derivado de la semilla + coordenadas del chunk:
    //     así el chunk siempre se regenera IGUAL.
    var _rng = new RNG(global.world_seed + (_cx * 73856093) ^ (_cy * 19349663));
    generar_terreno_chunk(_cx, _cy, _rng);

    // --- b) Aplicar las modificaciones guardadas -------------------------------
    var _datos = chunk_get(_cx, _cy);

    // Tiles modificados
    var _tiles = variable_struct_get_names(_datos.tiles_modificados);
    for (var _i = 0; _i < array_length(_tiles); _i++)
    {
        var _pos = string_split(_tiles[_i], ",");
        tilemap_set(global.tilemap_terreno,
                    _datos.tiles_modificados[$ _tiles[_i]],
                    real(_pos[0]), real(_pos[1]));
    }

    // Estructuras
    for (var _i = 0; _i < array_length(_datos.estructuras); _i++)
    {
        var _e = _datos.estructuras[_i];
        var _s = instance_create_depth(
            _e.x * CELL + (CELL * 0.5), _e.y * CELL + (CELL * 0.5),
            -_e.y * CELL, objStructure);
        _s.tipo_estructura = _e.tipo;
        _s.grid_x = _e.x;
        _s.grid_y = _e.y;
    }

    // --- c) Activar las instancias de esta región --------------------------------
    instance_activate_region(_px, _py, CHUNK_PX, CHUNK_PX, true);
}

/// @func descargar_chunk(_cx, _cy)
/// @desc Desactiva las instancias. El estado YA está en el ChunkData.
function descargar_chunk(_cx, _cy)
{
    var _px = _cx * CHUNK_PX;
    var _py = _cy * CHUNK_PX;

    // Los nodos de recurso NO se desactivan: su estado está en el diff.
    // Solo desactivamos enemigos y drops, que son prescindibles.
    with (objEnemy)
    {
        if (x >= _px && x < _px + CHUNK_PX &&
            y >= _py && y < _py + CHUNK_PX)
        {
            instance_deactivate_object(id);
        }
    }

    with (objItemDrop)
    {
        if (x >= _px && x < _px + CHUNK_PX &&
            y >= _py && y < _py + CHUNK_PX)
        {
            instance_deactivate_object(id);
        }
    }
}

/// @func string_split(_str, _separador)
/// @desc Divide un string por un separador. Devuelve un array.
function string_split(_str, _separador)
{
    var _out = [];
    var _actual = "";
    var _len = string_length(_str);

    for (var _i = 1; _i <= _len; _i++)
    {
        var _c = string_char_at(_str, _i);

        if (_c == _separador)
        {
            array_push(_out, _actual);
            _actual = "";
        }
        else
        {
            _actual += _c;
        }
    }

    array_push(_out, _actual);
    return _out;
}
```

### 5.5 Ciclo día/noche

```gml
// ---------------------------------------------------------------------------
// objTimeOfDay — Create
// ---------------------------------------------------------------------------
dia           = 1;
tiempo        = 0.30;      // 0 = medianoche, 0.5 = mediodía
duracion_dia  = 1800;      // frames (30 s a 60 fps → muy rápido;
                           // sube a 18000 para un ciclo real)

// ---------------------------------------------------------------------------
// objTimeOfDay — Step
// ---------------------------------------------------------------------------
tiempo += 1 / duracion_dia;

if (tiempo >= 1)
{
    tiempo -= 1;
    dia++;

    // Al amanecer: curar penalizaciones, registrar el día
    global.needs.sueño = 100;
    objChunkManager.registrar_nuevo_dia();
}

global.es_de_noche = (tiempo < 0.22) || (tiempo > 0.78);

// Temperatura: más frío de noche
global.temperatura = 0.5 + (sin((tiempo - 0.25) * 2 * pi) * 0.5);
```

```gml
// ---------------------------------------------------------------------------
// objTimeOfDay — Draw GUI (capa de oscuridad)
// ---------------------------------------------------------------------------
// Nivel de oscuridad: 0 de día, 0.75 en el punto más oscuro de la noche
var _distancia_al_mediodia = abs(tiempo - 0.5) * 2;   // 0 mediodía, 1 medianoche
var _oscuridad = clamp((_distancia_al_mediodia - 0.45) / 0.55, 0, 1) * 0.78;

if (_oscuridad > 0.01)
{
    draw_set_alpha(_oscuridad);
    draw_set_color(c_navy);
    draw_rectangle(0, 0, display_get_gui_width(), display_get_gui_height(), false);
    draw_set_alpha(1);
}
```

> 💡 Esto oscurece la pantalla, pero no la tiñe: a mediodía y a medianoche el único cambio es
> cuánto se ve, no de qué color. Para una rampa de color real (amanecer cálido → mediodía
> neutro → atardecer cálido → noche azulada) que además tiña las luces del sistema de
> [24 · Iluminación 2D](./24%20-%20Iluminación%202D.md), ver
> [24 · Iluminación 2D §6 — Ciclo día/noche con rampa de color](./24%20-%20Iluminación%202D.md#6--ciclo-díanoche-con-rampa-de-color),
> que reutiliza este mismo `tiempo` de `objTimeOfDay`.

---

## 6. Gestión del estado del jugador

```gml
// ---------------------------------------------------------------------------
// scr_survival_state
// ---------------------------------------------------------------------------

/// @func SurvivalState()
function SurvivalState() constructor
{
    needs    = new Needs();
    dias_vividos = 1;
    muertes  = 0;

    // Herramienta equipada y su durabilidad
    herramienta_equipada = "";
    durabilidad          = 100;

    /// @desc Usa la herramienta. Devuelve false si se rompió.
    usar_herramienta = function(_cantidad)
    {
        if (herramienta_equipada == "") return true;

        durabilidad -= (_cantidad == undefined) ? 1 : _cantidad;

        if (durabilidad <= 0)
        {
            global.inventory.remove(herramienta_equipada, 1);
            herramienta_equipada = "";
            durabilidad = 100;
            audio_play_sound(sndToolBreak, 10, false);
            fx_floating_text(objPlayer.x, objPlayer.y - 24,
                             "¡Se rompió!", c_red);
            return false;
        }
        return true;
    };

    equipar = function(_item_id)
    {
        var _def = item_get_def(_item_id);
        if (_def == undefined) return false;
        if (_def.type != "tool") return false;

        herramienta_equipada = _item_id;
        durabilidad = 100;
        return true;
    };

    serialize = function()
    {
        return {
            needs: needs.serialize(),
            dias_vividos: dias_vividos,
            muertes: muertes,
            herramienta_equipada: herramienta_equipada,
            durabilidad: durabilidad,
            inventario: global.inventory.serialize()
        };
    };

    static deserialize = function(_d)
    {
        var _s = new SurvivalState();
        _s.needs        = Needs.deserialize(_d.needs);
        _s.dias_vividos = _d.dias_vividos;
        _s.muertes      = _d.muertes;
        _s.herramienta_equipada = _d.herramienta_equipada;
        _s.durabilidad  = _d.durabilidad;
        global.inventory = Inventory.deserialize(_d.inventario);
        return _s;
    };
}
```

```gml
// ---------------------------------------------------------------------------
// scr_survival_save
// ---------------------------------------------------------------------------

/// @func survival_save()
/// @desc Guarda: semilla + jugador + diffs de chunks (solo los no vacíos).
function survival_save()
{
    var _data = {
        version: 2,
        world_seed: global.world_seed,
        jugador: {
            x: objPlayer.x, y: objPlayer.y,
            estado: global.survival.serialize()
        },
        tiempo: { dia: objTimeOfDay.dia, tiempo: objTimeOfDay.tiempo },
        chunks: []
    };

    // Solo los chunks con cambios: esto mantiene el save pequeño
    var _keys = variable_struct_get_names(objChunkManager.chunks);
    for (var _i = 0; _i < array_length(_keys); _i++)
    {
        var _c = objChunkManager.chunks[$ _keys[_i]];
        if (!_c.esta_vacio()) array_push(_data.chunks, _c.serialize());
    }

    // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
    // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
    // 14 - Persistencia y archivos.md §1.
    var _f = file_text_open_write(game_save_id + "survival_save.json");
    file_text_write_string(_f, json_stringify(_data));
    file_text_close(_f);

    show_debug_message("Guardado. Chunks con cambios: " +
                       string(array_length(_data.chunks)));
}

/// @func survival_load()
function survival_load()
{
    var _path = game_save_id + "survival_save.json";
    if (!file_exists(_path)) return false;

    var _f = file_text_open_read(_path);
    var _d = json_parse(file_text_read_string(_f));
    file_text_close(_f);

    global.world_seed = _d.world_seed;
    global.survival   = SurvivalState.deserialize(_d.jugador.estado);

    objTimeOfDay.dia    = _d.tiempo.dia;
    objTimeOfDay.tiempo = _d.tiempo.tiempo;

    // Reconstruir los diffs de chunks
    objChunkManager.chunks = {};
    for (var _i = 0; _i < array_length(_d.chunks); _i++)
    {
        var _c = ChunkData.deserialize(_d.chunks[_i]);
        objChunkManager.chunks[$ objChunkManager.chunk_key(_c.cx, _c.cy)] = _c;
    }

    return true;
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Guardar todo el mapa en cada chunk | Saves de 50 MB y lentos | Solo el diff respecto al generador |
| Generar el chunk con el RNG global | El chunk cambia según lo que hayas hecho antes | RNG derivado de `seed + coords` |
| `instance_deactivate_region` sobre el jugador | El jugador deja de existir | Pasa `notme = true` o exclúyelo explícitamente |
| Desactivar instancias sin guardar su estado | Al volver, los recursos reaparecen | El estado vive en `ChunkData`, no en la instancia |
| Necesidades que matan en 2 minutos | El jugador no puede explorar nada | Tasa ~0.03/frame; una necesidad al 0 molesta antes de matar |
| Crafteo que consume antes de comprobar | Pierdes materiales al fallar | `puede_craftear()` separado de `craftear()` |
| Receta que no devuelve materiales al fallar | El jugador pierde recursos por un error de UI | Nunca consumas si `puede_craftear()` es false |
| Construcción sin grid de ocupación | Dos estructuras en la misma celda | `WorldGrid` con clave "x,y" |
| Durabilidad que no se guarda | Al cargar, todas las herramientas nuevas | Inclúyela en `serialize()` |
| Recalcular chunks cada frame | Coste brutal | Cada 30 frames, o al cruzar el límite de chunk |
| `string_split` con separador que no aparece | Devuelve el string entero: eso es correcto, pero no lo asumas de más de 2 partes | Documenta el formato "x,y" y respétalo |

---

## 8. Cómo escalarlo

1. **Más necesidades** — oxígeno bajo el agua, cordura con alucinaciones
   visuales, enfermedad por comida cruda.
2. **Cultivos** — plantar, regar, esperar días. Añade una dimensión temporal
   que casa muy bien con el ciclo día/noche.
3. **Criaturas con ecosistema** — herbívoros que huyen, depredadores que
   cazan herbívoros. Es la diferencia entre Don't Starve y un survival básico.
4. **Estaciones** — cada 15 días cambia: invierno (más frío, menos comida),
   verano (incendios, sequía).
5. **Mapa del mundo con biomas** — ruido Perlin para temperatura y humedad;
   bioma = f(temperatura, humedad).
6. **Multijugador cooperativo** — ver receta 14.
7. **Sistema de *blueprints*** — planos que consumes para aprender recetas;
   convierte la exploración en progreso.

**Cuándo pasar a otra receta:** si consigues que el chunking funcione, tienes
la técnica que separa un prototipo de un juego de verdad. Es la más transferible
de toda esta biblioteca.

---

## 9. Fuentes

- **Plantilla oficial Survivor** del IDE (New → Game → Template) — variante
  *bullet heaven*, muy útil para el manejo de oleadas masivas
- Manual oficial — `instance_deactivate_region`, `instance_activate_region`,
  `instance_deactivate_object` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Instances/instance_deactivate_region.htm
- Manual oficial — Tilemaps (`tilemap_set`, `tilemap_get_at_pixel`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers.htm
- Manual oficial — `string_split` (GameMaker 2024+), `string_char_at`,
  `string_length` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/Strings.htm
- Manual oficial — `variable_struct_get_names`, `variable_struct_remove` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions.htm
- Manual oficial — `json_stringify`, `file_text_open_write` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling.htm
- Receta propia: **04 — RPG** (inventario, equipamiento, save/load)
- Receta propia: **05 — Roguelike** (RNG propio, Fisher-Yates, grids)
- Receta propia: **15 — Game feel** (partículas, shake, squash, texto flotante)
