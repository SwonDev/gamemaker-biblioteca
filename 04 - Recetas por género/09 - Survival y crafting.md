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
objWorldGrid         (controller: rejilla de ocupación de construcciones, §5.3)
objWorldGen          (genera el mundo por chunks)
```

Como `objNeeds`, `objTimeOfDay`, `objChunkManager` y `objWorldGrid` son *controllers*
singleton, colócalos una sola vez en la room inicial (o instáncialos desde `obj_game` ·
Create), igual que ya haces con los otros tres.

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
- **Peso** (opcional; añade decisiones de qué llevar). Implementado en
  [04 · 04 §5.2](./04%20-%20RPG%20_%20Action%20RPG.md#52-inventario-y-equipamiento)
  (`inventory_peso_total()`, `peso_maximo`, penalización de velocidad).
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

> ⚠️ Esta receta declara `estacion` y `tiempo` pero, tal como marca el informe de auditoría de
> esta biblioteca (r3-2026-09-06, tema 22 y 23), `puede_craftear()`/`craftear()` (§5.1) **nunca
> comprueban ninguno de los dos campos**: la comprobación de proximidad y la cola no-instantánea
> son código nuevo, no un bug de los que ya existen. §5.7-§5.10 conectan estación, tiempo,
> descubrimiento de recetas y el árbol de dependencias que faltaban.

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

### 4.8 Contenedores externos

`objStorageChest` aparece en la jerarquía de §2 pero, tal como marca el informe de auditoría de
esta biblioteca (r3-2026-09-06, tema 5), nunca llega a implementarse: en `04 · 06 §4.4` un cofre
es solo un booleano «abierto/cerrado», sin inventario propio. Un contenedor de verdad necesita
tres piezas que un ítem tirado en el suelo no tiene: **capacidad propia** (no comparte la del
jugador), **persistencia** (si el jugador lo llena y se aleja, el contenido sigue ahí al volver)
y una **UI de dos paneles** (inventario del jugador a un lado, del cofre al otro). El código está
en §5.6.

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
    sueno   = 100;
    cordura = 100;

    // Tasas de degradación por frame (a 60 fps)
    // Valores típicos: un día completo = 1200 frames → ~0.05/frame para
    // vaciarse en algo más de medio día.
    tasa_hambre  = 0.030;
    tasa_sed     = 0.045;
    tasa_sueno   = 0.018;
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
        sueno  = max(0, sueno  - (tasa_sueno));

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
    dano_por_frame = function()
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
        if (sueno  < 15) _m *= 0.60;
        return _m;
    };

    /// @desc ¿Alguna necesidad está en zona crítica? (para la UI)
    alguna_critica = function()
    {
        return (hambre < 20) || (sed < 20) || (calor < 20) ||
               (sueno < 15) || (cordura < 20);
    };

    consumir = function(_item_efecto)
    {
        if (variable_struct_exists(_item_efecto, "hambre")) hambre = min(100, hambre + _item_efecto.hambre);
        if (variable_struct_exists(_item_efecto, "sed"))    sed    = min(100, sed    + _item_efecto.sed);
        if (variable_struct_exists(_item_efecto, "calor"))  calor  = min(100, calor  + _item_efecto.calor);
        if (variable_struct_exists(_item_efecto, "sueno"))  sueno  = min(100, sueno  + _item_efecto.sueno);
    };

    serialize = function()
    {
        return { hambre: hambre, sed: sed, calor: calor,
                 sueno: sueno, cordura: cordura };
    };

    static deserialize = function(_d)
    {
        var _n = new Needs();
        _n.hambre  = _d.hambre;
        _n.sed     = _d.sed;
        _n.calor   = _d.calor;
        _n.sueno   = _d.sueno;
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
// objResourceNode — golpear(_dano, _herramienta)
// ---------------------------------------------------------------------------
function golpear(_dano, _herramienta)
{
    // ¿La herramienta es adecuada? Si no, daño reducido
    var _eficacia = 1.0;

    if (herramienta != "")
    {
        if (_herramienta == herramienta)          _eficacia = 2.0;
        else if (_herramienta != "")              _eficacia = 0.5;
        else                                       _eficacia = 0.3;   // a mano
    }

    hp -= _dano * _eficacia;
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
// (el objeto `objWorldGrid` — jerarquía en §2, Create al final de este
// apartado — es la única fuente de verdad sobre qué celda está libre) y
// `point_distance()` (función del runtime, verificada con `buscar.py`)
// para el rango de colocación.
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
// objWorldGrid — Create
// ---------------------------------------------------------------------------
// ⚠️ Corregido (informe r3-99-cierre §3.1): la versión anterior definía esto
// como `function WorldGrid() constructor { ... }` y nunca lo instanciaba en
// ningún sitio — `objBuildManager` llamaba a `objWorldGrid.ocupada()` contra
// un objeto que no existía en la jerarquía ni tenía Create, así que la
// receta no compilaba/ejecutaba tal cual estaba escrita.
//
// La corrección lo convierte en objeto: `objWorldGrid` (añadido a la
// jerarquía en §2) es un controller *singleton* — igual que `objChunkManager`
// unas líneas más abajo, mismo patrón — cuyo Create define directamente estas
// variables y funciones de instancia. Así las llamadas que ya usan este
// documento y `04 · 51` (`objWorldGrid.ocupada()/.ocupar()/.liberar()`,
// `objWorldGrid.celdas`) siguen funcionando sin tocar ni una: son variables
// reales de la instancia, no de un struct aparte que nadie crea.
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

/// @desc Serializar (solo las ocupadas: eficiente). No se usa para el save
/// principal — ver §6, `objWorldGrid` no se guarda aparte — pero queda
/// disponible para depuración o para un sistema que sí quiera un volcado
/// plano de la rejilla.
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

/// @desc Vacía la rejilla. La usa `survival_load()` (§6) antes de que
/// `cargar_chunk()` (§5.4) la repueble sola según van entrando los chunks.
vaciar = function()
{
    celdas = {};
};
```

### 5.4 Chunking

> `global.tilemap_terreno` (usado más abajo en `cargar_chunk()`, y reutilizado tal cual por
> `04 · 51` §5) es el ID de la capa de tiles del terreno de la room activa — **no lo crea este
> script**: obtenlo con `layer_tilemap_get_id()` en el `Room Start` de tu room de mundo:
> `global.tilemap_terreno = layer_tilemap_get_id(layer_get_id("Tiles_Terreno"));` (ajusta el
> nombre de capa al tuyo).

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

    anadir_estructura = function(_tipo, _x, _y)
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
    chunk_get(_cx, _cy).anadir_estructura(_struct.tipo_estructura,
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

        // ⚠️ Sin esto, una estructura que vuelve a entrar en pantalla (chunk
        // descargado y recargado, o partida recién cargada) recrea la
        // instancia pero deja su celda libre en objWorldGrid: dos jugadores
        // — o el mismo, después de un load — podrían construir encima.
        objWorldGrid.ocupar(_s.grid_x, _s.grid_y, _s);
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
    global.survival.needs.sueno = 100;   // Needs vive DENTRO de SurvivalState (§6) —
                                          // no hay (ni debe haber) un global.needs suelto
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

### 5.6 Contenedores: objStorageChest

```gml
// ---------------------------------------------------------------------------
// objStorageChest — Create
// ---------------------------------------------------------------------------
// Reutiliza Inventory (04 · 04 §5.2): cada cofre tiene SU PROPIA instancia,
// separada de global.inventory (el inventario del jugador).
inventario = new Inventory(30);   // capacidad propia del cofre, no la del jugador
abierto    = false;
```

```gml
// ---------------------------------------------------------------------------
// objStorageChest — Step
// ---------------------------------------------------------------------------
if (!abierto)
{
    if (keyboard_check_pressed(ord("E"))
        && point_distance(objPlayer.x, objPlayer.y, x, y) <= RANGO_CONSTRUCCION)
    {
        abierto = true;
    }
}
else if (keyboard_check_pressed(vk_escape) || keyboard_check_pressed(ord("E")))
{
    abierto = false;
}
```

```gml
// ---------------------------------------------------------------------------
// objStorageChest — transferir_a_cofre(_item_id, _cantidad) / transferir_a_jugador(...)
// ---------------------------------------------------------------------------

/// @desc Mueve del inventario del jugador AL cofre. No mueve nada si no hay
///       suficiente cantidad: comprobación antes que efecto, como en §5.1.
function transferir_a_cofre(_item_id, _cantidad)
{
    if (!global.inventory.has(_item_id, _cantidad)) return false;
    if (!inventario.add(_item_id, _cantidad))       return false;   // el cofre está lleno
    global.inventory.remove(_item_id, _cantidad);
    return true;
}

/// @desc Mueve del cofre AL jugador.
function transferir_a_jugador(_item_id, _cantidad)
{
    if (!inventario.has(_item_id, _cantidad))       return false;
    if (!global.inventory.add(_item_id, _cantidad)) return false;   // el jugador va lleno
    inventario.remove(_item_id, _cantidad);
    return true;
}
```

```gml
// ---------------------------------------------------------------------------
// objStorageChest — Draw GUI (dos paneles: jugador a la izquierda, cofre a la derecha)
// ---------------------------------------------------------------------------
if (!abierto) exit;

var _px = display_get_gui_width() * 0.5 - 220;
var _py = 60;

draw_set_color(c_black);
draw_rectangle(_px,       _py, _px + 200, _py + 260, false);   // panel jugador
draw_rectangle(_px + 240, _py, _px + 440, _py + 260, false);   // panel cofre
draw_set_color(c_white);
draw_text(_px,       _py - 16, "Inventario");
draw_text(_px + 240, _py - 16, "Cofre");

var _fila = 0;
for (var _i = 0; _i < array_length(global.inventory.slots); _i++)
{
    var _s = global.inventory.slots[_i];
    draw_text(_px + 8, _py + 8 + _fila * 16, _s.item_id + " x" + string(_s.cantidad));
    _fila++;
}

_fila = 0;
for (var _i = 0; _i < array_length(inventario.slots); _i++)
{
    var _s = inventario.slots[_i];
    draw_text(_px + 248, _py + 8 + _fila * 16, _s.item_id + " x" + string(_s.cantidad));
    _fila++;
}
```

> 💡 Este panel es deliberadamente mínimo: **listas de texto**, sin arrastrar-y-soltar. Para
> drag-and-drop real entre los dos paneles, reutiliza la máquina de 3 estados de
> [13 · 05 §e](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md)
> — sus funciones `inventario_coger()`/`inventario_soltar()` ya resuelven el caso general; lo
> único que cambia aquí es a cuál de los dos `Inventory` (jugador o `inventario` del cofre)
> apunta el destino del soltar.

> ⚠️ **Esta receta NO conecta todavía el contenido del cofre con el chunk diff de §5.4.**
> `ChunkData.anadir_estructura()` solo guarda `{ tipo, x, y }`, sin sitio para el inventario del
> cofre. Mientras el chunk siga cargado no hay pérdida real: `descargar_chunk()` (§5.4) desactiva
> `objEnemy` y `objItemDrop`, pero no `objStorageChest`, así que la instancia (y su `inventario`)
> sigue viva en memoria. El riesgo aparece al **guardar y volver a cargar la partida entera**: tal
> cual, el contenido del cofre no sobrevive. Para persistirlo de verdad, añade un parámetro
> opcional a `anadir_estructura(_tipo, _x, _y, _estado = undefined)` y guarda ahí
> `inventario.serialize()`; en `cargar_chunk()`, justo después de crear la instancia, `if
> (_e.estado != undefined) { _s.inventario = Inventory.deserialize(_e.estado); }`. No se aplica
> aquí para no reescribir §5.4 mientras otro agente puede estar editándolo en paralelo — el
> patrón es el mismo que ya usa `SurvivalState` en §6 para serializar structs anidados.

### 5.7 Crafteo: estaciones y descubrimiento de recetas

```gml
// ---------------------------------------------------------------------------
// scr_crafting_estaciones — tema 22 del informe de auditoría: craftear() y
// puede_craftear() (§5.1) declaran `estacion` en la receta pero nunca la
// comprueban. Verificado: point_distance e instance_nearest, ya en uso en
// §5.3 y en el resto de esta biblioteca.
// ---------------------------------------------------------------------------

#macro RANGO_ESTACION (CELL * 2)

/// @func estacion_cercana(_tipo_estacion, _x, _y)
/// @desc "" (crafteo a mano) siempre cuenta como estación válida: no hace
///       falta buscar nada.
/// @return {Bool}
function estacion_cercana(_tipo_estacion, _x, _y)
{
    if (_tipo_estacion == "") return true;

    var _inst = instance_nearest(_x, _y, objCraftingStation);
    if (_inst == noone)              return false;
    if (_inst.tipo != _tipo_estacion) return false;

    return point_distance(_x, _y, _inst.x, _inst.y) <= RANGO_ESTACION;
}

/// @func puede_craftear_aqui(_receta, _inventario, _x, _y)
/// @desc Envuelve Recipe.puede_craftear() (§5.1) SIN tocarla: añade la
///       comprobación de estación que faltaba sin romper las llamadas que ya
///       usan puede_craftear() a secas en otro sitio.
function puede_craftear_aqui(_receta, _inventario, _x, _y)
{
    return _receta.puede_craftear(_inventario)
        && estacion_cercana(_receta.estacion, _x, _y);
}
```

```gml
// ---------------------------------------------------------------------------
// scr_crafting_descubrimiento — tema 21: recipes_init() (§5.1) carga TODAS
// las recetas en global.recipes sin ningún filtro de desbloqueo; el jugador
// las tiene todas disponibles desde el segundo 1.
// ---------------------------------------------------------------------------

/// @func recetas_desbloqueadas_init(_iniciales)
/// @param {Array<String>} _iniciales  Recetas que el jugador conoce desde el principio.
function recetas_desbloqueadas_init(_iniciales)
{
    global.recetas_desbloqueadas = {};
    for (var _i = 0; _i < array_length(_iniciales); _i++)
    {
        global.recetas_desbloqueadas[$ _iniciales[_i]] = true;
    }
}

/// @func receta_desbloquear(_id)
/// @desc Llámala al leer un blueprint (ver item_usar_blueprint() más abajo,
///       la idea que §8 de este documento ya apuntaba sin implementar) o al
///       cumplir la condición que decidas (nivel, misión, NPC).
function receta_desbloquear(_id)
{
    global.recetas_desbloqueadas[$ _id] = true;
}

/// @func receta_esta_desbloqueada(_id)
function receta_esta_desbloqueada(_id)
{
    return variable_struct_exists(global.recetas_desbloqueadas, _id);
}

/// @func recetas_disponibles()
/// @desc Para la UI de crafteo: solo lo que el jugador ya conoce, no el
///       catálogo entero de global.recipes.
function recetas_disponibles()
{
    var _out = [];
    var _ids = variable_struct_get_names(global.recetas_desbloqueadas);
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _r = recipe_get(_ids[_i]);
        if (_r != undefined) array_push(_out, _r);
    }
    return _out;
}

/// @func item_usar_blueprint(_inventario, _item_id, _receta_id)
/// @desc Consume un objeto "blueprint_xxx" del inventario y desbloquea la
///       receta que enseña. `_item_id` debe existir en items.json (04 · 04
///       §5.3) con el `type` que decidas (p. ej. "blueprint").
function item_usar_blueprint(_inventario, _item_id, _receta_id)
{
    if (!_inventario.has(_item_id, 1)) return false;
    _inventario.remove(_item_id, 1);
    receta_desbloquear(_receta_id);
    return true;
}
```

### 5.8 Crafteo: colas y lotes con cancelación

```gml
// ---------------------------------------------------------------------------
// objCraftingStation — cola de crafteo con lotes y cancelación (temas 23 y
// 24). Mismo patrón que la cola de producción de 04 · 13 §5.3 (objBuilding),
// adaptado de "producir unidades" a "craftear objetos": un array con
// { receta_id, tiempo_restante, tiempo_total }, un elemento activo a la vez.
// ---------------------------------------------------------------------------

// objCraftingStation — Create
tipo = "banco";     // "banco", "fragua"... — el mismo valor que Recipe.estacion
cola  = [];         // array de { receta_id, tiempo_restante, tiempo_total }
```

```gml
/// @func crafteo_encolar(_receta_id, _veces, _inventario)
/// @desc Cobra los materiales de las _veces repeticiones AL ENCOLAR (igual que
///       04 · 13 §5.3): si a mitad de cola faltan materiales para la unidad 3
///       de 5, las 1 y 2 ya se cobraron y se quedan en la cola.
/// @return {Real} Cuántas repeticiones se encolaron de verdad (puede ser
///                menos que _veces si los materiales no llegaban para todas).
function crafteo_encolar(_receta_id, _veces, _inventario)
{
    var _receta = recipe_get(_receta_id);
    if (_receta == undefined) return 0;

    var _encoladas = 0;
    for (var _i = 0; _i < _veces; _i++)
    {
        if (!_receta.puede_craftear(_inventario)) break;   // sin materiales: para aquí

        var _keys = variable_struct_get_names(_receta.ingredientes);
        for (var _k = 0; _k < array_length(_keys); _k++)
        {
            _inventario.remove(_keys[_k], _receta.ingredientes[$ _keys[_k]]);
        }

        array_push(cola, {
            receta_id:       _receta_id,
            tiempo_restante: max(1, _receta.tiempo),   // 0 = instantáneo → 1 frame mínimo
            tiempo_total:    max(1, _receta.tiempo)
        });
        _encoladas++;
    }
    return _encoladas;
}

/// @func crafteo_cancelar(_indice, _inventario)
/// @desc Reembolsa los materiales de ESE elemento de la cola y lo retira. El
///       que esté en curso (índice 0) también se reembolsa: perder tiempo de
///       cola al cancelar es aceptable, perder materiales no.
function crafteo_cancelar(_indice, _inventario)
{
    if (_indice < 0 || _indice >= array_length(cola)) return false;

    var _receta = recipe_get(cola[_indice].receta_id);
    var _keys = variable_struct_get_names(_receta.ingredientes);
    for (var _k = 0; _k < array_length(_keys); _k++)
    {
        _inventario.add(_keys[_k], _receta.ingredientes[$ _keys[_k]]);
    }

    array_delete(cola, _indice, 1);
    return true;
}
```

```gml
// objCraftingStation — Step (avanza SOLO el elemento 0, igual que 04 · 13 §5.3)
if (array_length(cola) > 0)
{
    cola[0].tiempo_restante--;

    if (cola[0].tiempo_restante <= 0)
    {
        var _receta = recipe_get(cola[0].receta_id);
        global.inventory.add(_receta.producto.id, _receta.producto.cantidad);
        array_delete(cola, 0, 1);
        audio_play_sound(sndCraftDone, 8, false);
    }
}
```

### 5.9 Árbol de dependencias de recetas

```gml
// ---------------------------------------------------------------------------
// scr_crafting_arbol — tema 20: la dependencia entre recetas (cuerda → cofre)
// es implícita por clave compartida, sin validación ni forma de dibujarla. Se
// resuelve construyendo el MISMO grafo que espera 13 · 16 §3.2 y reutilizando
// SUS funciones arbol_detectar_ciclos()/arbol_nodos_alcanzables() tal cual —
// no se reescriben aquí: hace falta scr_arbol_validar de 13 · 16 §3.2 en el
// proyecto. Verificado: variable_struct_get_names, variable_struct_exists,
// array_push, ya en uso en el resto de este documento.
// ---------------------------------------------------------------------------

/// @func recetas_construir_grafo()
/// @desc Construye un grafo { nodos, raices } con la MISMA forma que espera
///       13 · 16 §3.2: cada receta es un nodo; es hijo de otra receta si uno
///       de sus ingredientes es el `producto.id` de esa otra receta.
/// @returns {Struct} Pásalo directo a arbol_validar()/arbol_nodos_alcanzables().
function recetas_construir_grafo()
{
    var _ids = variable_struct_get_names(global.recipes);

    // Índice producto → receta que lo fabrica (una receta = un producto, aquí)
    var _producto_a_receta = {};
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _r = global.recipes[$ _ids[_i]];
        _producto_a_receta[$ _r.producto.id] = _ids[_i];
    }

    var _nodos = {};
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        _nodos[$ _ids[_i]] = { prerrequisitos: [], hijos: [] };
    }

    var _raices = [];
    for (var _i = 0; _i < array_length(_ids); _i++)
    {
        var _id   = _ids[_i];
        var _r    = global.recipes[$ _id];
        var _mats = variable_struct_get_names(_r.ingredientes);

        var _tiene_padre_craftable = false;
        for (var _m = 0; _m < array_length(_mats); _m++)
        {
            var _mat = _mats[_m];
            if (!variable_struct_exists(_producto_a_receta, _mat)) continue;   // materia prima, no receta

            var _padre_id = _producto_a_receta[$ _mat];
            array_push(_nodos[$ _id].prerrequisitos, _padre_id);
            array_push(_nodos[$ _padre_id].hijos, _id);
            _tiene_padre_craftable = true;
        }

        if (!_tiene_padre_craftable) array_push(_raices, _id);
    }

    return { nodos: _nodos, raices: _raices };
}
```

> 💡 **`PrerrequisitoModo` (13 · 16 §3.1, `enum PrerrequisitoModo { Y, O }`) no tiene ambigüedad
> aquí.** `arbol_nodos_alcanzables()` de 13 · 16 §3.2 comprueba `_hijo.modo` para decidir si basta
> un prerrequisito (`O`) o hacen falta todos (`Y`); una receta que declara `{ madera: 5, cuerda: 2
> }` siempre necesita AMBOS materiales, así que el grafo de recetas es **siempre modo `Y`** —
> añade `modo: PrerrequisitoModo.Y` a cada nodo de `_nodos` si vas a reutilizar esa función tal
> cual.

### 5.10 Subproductos y fallos de fabricación

```gml
// ---------------------------------------------------------------------------
// scr_crafting_fallos — tema 25: sin probabilidad de fallo ni subproductos.
// Se añade como una VARIANTE de Recipe.craftear() (§5.1), no una reescritura:
// craftear() sigue existiendo tal cual para las recetas que no fallan nunca.
// Verificado: random(n).
// ---------------------------------------------------------------------------

/// @func craftear_con_riesgo(_receta, _inventario, _prob_fallo, _subproducto = undefined)
/// @param {Struct.Recipe} _receta
/// @param {Struct}        _inventario
/// @param {Real}          _prob_fallo    0..1. 0 se comporta como craftear() normal.
/// @param {Struct}        _subproducto   { id, cantidad } opcional; se entrega SIEMPRE
///                                       que se consuman materiales, falle o no la
///                                       receta (viruta, cenizas, chatarra...).
/// @return {Struct} { exito, subproducto_entregado }
function craftear_con_riesgo(_receta, _inventario, _prob_fallo, _subproducto = undefined)
{
    if (!_receta.puede_craftear(_inventario))
    {
        return { exito: false, subproducto_entregado: false };
    }

    var _keys = variable_struct_get_names(_receta.ingredientes);
    for (var _i = 0; _i < array_length(_keys); _i++)
    {
        _inventario.remove(_keys[_i], _receta.ingredientes[$ _keys[_i]]);
    }

    var _fallo = (random(1) < _prob_fallo);

    if (!_fallo)
    {
        _inventario.add(_receta.producto.id, _receta.producto.cantidad);
    }

    if (_subproducto != undefined)
    {
        _inventario.add(_subproducto.id, _subproducto.cantidad);
    }

    return { exito: !_fallo, subproducto_entregado: (_subproducto != undefined) };
}
```

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

    // `objWorldGrid` NO se serializa aparte: cada estructura ya viaja dentro
    // de `_c.serialize()` (campo `estructuras` de `ChunkData`, §5.4), y
    // `cargar_chunk()` reconstruye la ocupación sola al recrear las
    // instancias — ver el comentario en `survival_load()`, abajo.

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

    // Vaciar la rejilla de ocupación: no hace falta restaurarla a mano,
    // `cargar_chunk()` (§5.4) llama a `objWorldGrid.ocupar()` por cada
    // estructura según van entrando los chunks del jugador — igual que las
    // instancias de `objStructure` tampoco se recrean aquí, sino al vuelo.
    // Llama a `survival_load()` ANTES de que `objChunkManager` empiece a
    // recorrer su Step (p.ej. desde el Create de `obj_game`), para que no
    // queden chunks ya activados con instancias de una partida anterior.
    objWorldGrid.vaciar();

    return true;
}
```

> 🔴 **`survival_load()` revienta si es la primera llamada del proceso que toca `SurvivalState`,
> `ChunkData` o `Inventory`.** Los tres son `static deserialize` (arriba, `04 · 04 §5.2` para
> `Inventory`): ese método no existe como miembro accesible hasta que `new SurvivalState()`,
> `new ChunkData()`/`new Inventory()` se han ejecutado al menos una vez EN ESTE PROCESO — no
> antes, no "en general". Causa raíz completa, confirmada contra el manual oficial, en
> [`04 · 04` §5.2](./04%20-%20RPG%20_%20Action%20RPG.md#52-inventario-y-equipamiento). Cébalos
> de forma incondicional, ANTES de decidir si hay partida guardada o no — el mismo patrón que
> usa `04 · 04 §6` (`objGame::Create`):
> ```gml
> /// obj_game · Create — antes de comprobar file_exists() en survival_load()
> new SurvivalState();
> new ChunkData(0, 0);       // ajusta los argumentos a la firma real de tu ChunkData
> new Inventory(30);         // 04 · 04 §5.2 — descártala si tu partida nueva ya crea la suya
> ```

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
| Construcción sin grid de ocupación | Dos estructuras en la misma celda | `objWorldGrid` (celdas por clave "x,y", §2 y §5.3) |
| Recrear una estructura en `cargar_chunk()` sin re-ocupar la rejilla | Tras descargar/recargar un chunk (o cargar partida), se puede construir encima de algo que ya existe | `objWorldGrid.ocupar()` en el mismo punto donde se recrea la instancia (§5.4) |
| Durabilidad que no se guarda | Al cargar, todas las herramientas nuevas | Inclúyela en `serialize()` |
| Recalcular chunks cada frame | Coste brutal | Cada 30 frames, o al cruzar el límite de chunk |
| `string_split` con separador que no aparece | Devuelve el string entero: eso es correcto, pero no lo asumas de más de 2 partes | Documenta el formato "x,y" y respétalo |
| Craftear sin comprobar la estación | Se fabrica una fragua al lado de una fogata | `puede_craftear_aqui()` (§5.7), no `puede_craftear()` a secas |
| Cobrar materiales al completar la cola, no al encolar | Un lote de 5 se queda a medias y el jugador no sabe cuántos pagó | `crafteo_encolar()` (§5.8) cobra cada repetición en el momento de encolarla |
| Cofre sin `Inventory` propia | Comparte capacidad con el jugador, o pierde el contenido al descargar el chunk | `objStorageChest.inventario` (§5.6) es una instancia aparte, con su propio `serialize()` |

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
   convierte la exploración en progreso. Ya implementado en §5.7
   (`item_usar_blueprint()`, sobre el desbloqueo de `recetas_desbloqueadas`).

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
