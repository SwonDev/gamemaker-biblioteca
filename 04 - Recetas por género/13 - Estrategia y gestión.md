# 13 — Estrategia y gestión

> **Dificultad:** avanzada
> El género con más UI por metro cuadrado. Aquí es donde las **UI Layers y los
> Flex Panels** de GameMaker 2026 dejan de ser una novedad y se vuelven
> imprescindibles.

---

## 1. Visión general

Un juego de estrategia le pide al jugador que tome **muchas decisiones con
información incompleta** y que gestione varios frentes a la vez. El reto técnico
no es la IA: es presentar información sin abrumar.

**Lo que define al género:**

- **Control indirecto**: das órdenes, no mueves avatares.
- **Economía simultánea a la acción**: produces mientras combates.
- **Información asimétrica** (niebla de guerra, exploración).
- **Interfaz densa**: recursos, minimapa, cola de producción, panel de
  selección, tecnologías.

**Referencias:** *Command & Conquer*, *StarCraft*, *Age of Empires*,
*They Are Billions* (el mejor RTS moderno en 2D), *Northgard*, *Rimworld*
(gestión sin combate directo). GameMaker es viable para RTS de escala media y
excelente para juegos de gestión tipo *Rimworld* o *Frostpunk*.

**Subgéneros:**

| Subgénero | Escala | Foco |
|---|---|---|
| RTS clásico | 50-200 unidades | Tacto y economía |
| *Tower defense* | ver receta 08 | Estático |
| 4X (Civilization) | Imperios, turnos | Largo plazo |
| Gestión / *colony sim* | 5-30 agentes | Simulación y cuidado |
| *Grand strategy* | Mapas enormes | Política y economía |
| Autobattler | Combate automático | Construcción de *build* |

---

## 2. Arquitectura recomendada

### Jerarquía de objetos

```
objEntity            (padre: posición, vida, seleccionable)
├── objUnit          (padre de unidades)
│   ├── objUnitWorker
│   └── objUnitSoldier
├── objBuilding
└── objResource
objSelection         (rectángulo de selección, grupo seleccionado)
objOrderHandler      (traduce clics en órdenes)
objResourceManager   (almacén global de recursos)
objProductionQueue   (cola de producción por edificio)
objFogOfWar          (niebla de guerra)
objMinimap
objCommandCard       (UI: acciones de la selección)
objUILayer           (controller de las UI Layers)
objGame              (persistente)
```

### Rooms y capas

```
rm_rts_01
├── Terrain           (tilemap)
├── TerrainOverlay    (recursos, decoración)
├── Entities          (unidades y edificios)
├── Fog               (niebla de guerra, superficie)
└── [UI Folder]       ← UI Layer global, compartida entre rooms
    ├── ui_hud        (recursos, minimapa)
    ├── ui_selection  (panel de la unidad seleccionada)
    └── ui_menu       (menús modales)
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `Order` | Una orden: tipo, objetivo, posición, prioridad |
| `UnitDef` | Definición de unidad: vida, velocidad, coste, daño |
| `ResourcePool` | Recursos del jugador con capacidad |
| `ProductionItem` | Elemento en cola: qué produce, tiempo restante |
| `SelectionGroup` | Conjunto de unidades seleccionadas |

---

## 3. El bucle central (core loop)

```
┌─ Begin Step ─────────────────────────────────────────────┐
│ 1. Leer input: clic, arrastre de selección, teclas       │
└──────────────────────────────────────────────────────────┘
┌─ Step ───────────────────────────────────────────────────┐
│ 2. Procesar órdenes nuevas (mover, atacar, construir)    │
│ 3. Para cada unidad: ejecutar su orden actual            │
│    - mover: seguir el path (mp_grid / flujo)             │
│    - atacar: acercarse y atacar                          │
│    - recolectar: ir al recurso, volver al depósito        │
│ 4. Resolver combate                                      │
│ 5. Cola de producción: avanzar, completar, spawnear      │
│ 6. Economía: sumar recursos por tick                     │
│ 7. Niebla de guerra: recalcular visión                   │
│ 8. IA del enemigo                                        │
│ 9. UI: actualizar paneles (solo si cambió algo)          │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 Grid y movimiento de formación

Para RTS, `mp_grid` individual por unidad no escala bien con 100 unidades.
Alternativas:

| Técnica | Cuándo |
|---|---|
| `mp_grid_path` por unidad | Menos de 30 unidades |
| **Path compartido + offsets** | Grupos: calculas un path y cada unidad sigue con un pequeño desfase |
| **Campo de flujo** (*flow field*) | Cientos de unidades hacia el mismo destino |

El campo de flujo es la solución profesional: un array 2D donde cada celda
apunta hacia el destino. Se calcula una vez con BFS y todas las unidades lo
leen. Coste O(celdas) una vez, en vez de O(unidades × celdas).

### 4.2 Selección

Tres niveles, todos necesarios:

| Input | Acción |
|---|---|
| Clic | Seleccionar una unidad |
| Arrastre (rectángulo) | Seleccionar todas las que queden dentro |
| Doble clic / Ctrl+A | Seleccionar todas del mismo tipo en pantalla |
| Shift + clic | Añadir a la selección |

**Regla:** al dar una orden a un grupo, las unidades deben **distribuirse en
formación** alrededor del destino, no amontonarse en un punto. Una formación en
espiral o en rejilla alrededor del destino es suficiente.

### 4.3 Órdenes

Una orden es un struct. Tenerlas como datos permite colas de órdenes
(Shift + clic encadena) y cancelación limpia.

```gml
orden = {
    tipo: "mover",          // o "atacar" | "recolectar" | "construir" | "patrullar"
    x: 0, y: 0,
    objetivo: noone,        // instance id si "atacar"/"recolectar"; noone si solo apunta a un punto
    completada: false
};
```

**La cola de órdenes con Shift es la característica que distingue a un RTS
usable de un prototipo.** Es barata de implementar si las órdenes son structs.

### 4.4 Niebla de guerra

Dos niveles, igual que en la receta 05:

| Nivel | Qué ves |
|---|---|
| **Visible** | Unidades enemigas en tiempo real |
| **Explorado** | Terreno recordado, sin unidades |
| **Desconocido** | Negro |

En un RTS añade un tercer estado importante: **unidad recordada**. Si un
edificio enemigo estaba ahí y desapareció, el jugador debe ver "aquí había
algo" hasta que vuelva a mirar.

### 4.5 Economía y cola de producción

```gml
recursos = { mineral: 400, energia: 120, poblacion: 8 };
poblacion_max = 20;
```

La cola de producción es un array por edificio:

```gml
cola = [
    { id: "soldado", tiempo_restante: 120, tiempo_total: 180 },
    { id: "soldado", tiempo_restante: 180, tiempo_total: 180 }
];
```

**Detalle de calidad:** cobra los recursos **al encolar**, no al completar.
Así el jugador entiende por qué no puede encolar más.

### 4.6 IA de estrategia

Un RTS no necesita una IA brillante por unidad: necesita una **IA de
decisiones a nivel estratégico**. La estructura típica es un árbol de
utilidad:

```
cada N segundos:
    evaluar: ¿tengo suficientes recolectores?  → producir worker
    evaluar: ¿me están atacando?               → defender
    evaluar: ¿tengo ejército suficiente?       → atacar
    evaluar: ¿voy sobrado de recursos?         → expandir
```

Cada evaluación devuelve una puntuación y se ejecuta la más alta. Es simple,
robusto y produce un comportamiento que parece inteligente.

### 4.7 UI Layers y Flex Panels (GameMaker 2026)

Esta es la novedad relevante de 2026 para este género. Las **UI Layers** son:

- Una carpeta global ("UI Folder") compartida por **todas** las rooms.
- Cada UI Layer contiene **Flex Panels**, que son nodos con layout flex
  (como CSS Flexbox).
- Se controlan en runtime con las funciones `flexpanel_*`.
- Se activan y desactivan con `layer_set_visible()`.

**Ventaja frente a dibujar el HUD a mano con `draw_*`:** el layout es
declarativo y responsivo. Un panel con `justify_content` y `padding` se
recoloca solo al cambiar la resolución.

Funciones verificadas en el manual:

```gml
var _nodo = layer_get_flexpanel_node("ui_hud");        // nodo raíz de la capa
var _nuevo = flexpanel_create_node({ ... });           // crear nodo desde struct/JSON
flexpanel_node_insert_child(_raiz, _nuevo, _indice);   // añadir hijo
flexpanel_calculate_layout(_raiz, _ancho, _alto, _dir);// recalcular
var _s = flexpanel_node_get_struct(_nodo);             // leer como struct
var _hijo = flexpanel_node_get_child(_nodo, "nombre"); // por índice o nombre
flexpanel_node_style_set_justify_content(_nodo, _justify);
flexpanel_node_style_set_flex_direction(_nodo, _flex_direction);
flexpanel_node_style_set_gap(_nodo, _gutter, _size);
flexpanel_node_style_set_padding(_nodo, _edge, _size, [_unit]);
flexpanel_node_style_set_position(_nodo, _edge, _value, _unit);
```

> ⚠️ **Aviso:** el sistema Flex Panel es grande. Antes de usarlo en serio,
> abre la sección "Flex Panel Functions" del manual y revisa la lista completa
> de constantes (`flexpanel_justify_*`, `flexpanel_align_*`,
> `flexpanel_direction_*`, `flexpanel_unit_*`). Las firmas de arriba están
> verificadas; las constantes concretas debes confirmarlas ahí.

---

## 5. Código base

### 5.0 Selección

```gml
// ---------------------------------------------------------------------------
// objSelection — Create
// ---------------------------------------------------------------------------
seleccionadas = [];

// Rectángulo de selección (arrastre)
arrastrando   = false;
rect_x1 = 0; rect_y1 = 0;
rect_x2 = 0; rect_y2 = 0;
```

```gml
// ---------------------------------------------------------------------------
// objSelection — Step
// ---------------------------------------------------------------------------
// --- Empezar el arrastre --------------------------------------------------------
if (mouse_check_button_pressed(mb_left) && !punto_sobre_ui(mouse_x, mouse_y))
{
    arrastrando = true;
    rect_x1 = mouse_x;
    rect_y1 = mouse_y;
}

// --- Actualizar el rectángulo ----------------------------------------------------
if (arrastrando)
{
    rect_x2 = mouse_x;
    rect_y2 = mouse_y;

    if (mouse_check_button_released(mb_left))
    {
        arrastrando = false;
        finalizar_seleccion();
    }
}

// --- Clic derecho: dar orden -------------------------------------------------------
if (mouse_check_button_pressed(mb_right) && array_length(seleccionadas) > 0)
{
    dar_orden_a_seleccion(mouse_x, mouse_y);
}
```

```gml
// ---------------------------------------------------------------------------
// objSelection — finalizar_seleccion()
// ---------------------------------------------------------------------------
function finalizar_seleccion()
{
    var _x1 = min(rect_x1, rect_x2);
    var _y1 = min(rect_y1, rect_y2);
    var _x2 = max(rect_x1, rect_x2);
    var _y2 = max(rect_y1, rect_y2);

    // ¿Fue un clic (sin apenas arrastre) o un rectángulo real?
    var _es_clic = (abs(_x2 - _x1) < 5) && (abs(_y2 - _y1) < 5);

    if (!keyboard_check(vk_shift))
    {
        limpiar_seleccion();
    }

    if (_es_clic)
    {
        // Seleccionar la unidad bajo el cursor
        var _u = instance_position(rect_x1, rect_y1, objUnit);
        if (_u != noone) anadir_a_seleccion(_u);
    }
    else
    {
        // Seleccionar todas las unidades dentro del rectángulo
        // (en coordenadas de ROOM, no de pantalla: las propias de la vista)
        var _vx = camera_get_view_x(view_camera[0]);
        var _vy = camera_get_view_y(view_camera[0]);

        with (objUnit)
        {
            if (x >= _x1 + _vx && x <= _x2 + _vx &&
                y >= _y1 + _vy && y <= _y2 + _vy)
            {
                other.anadir_a_seleccion(id);
            }
        }
    }

    // Feedback sonoro
    if (array_length(seleccionadas) > 0)
    {
        audio_play_sound(sndSelect, 8, false);
    }
}

function anadir_a_seleccion(_unidad)
{
    if (!array_contains(seleccionadas, _unidad))
    {
        array_push(seleccionadas, _unidad);
        _unidad.seleccionada = true;
    }
}

function limpiar_seleccion()
{
    for (var _i = 0; _i < array_length(seleccionadas); _i++)
    {
        if (instance_exists(seleccionadas[_i]))
        {
            seleccionadas[_i].seleccionada = false;
        }
    }
    array_resize(seleccionadas, 0);
}

/// @func punto_sobre_ui(_x, _y)
/// @desc true si el punto está sobre el HUD: evita seleccionar "a través" de él.
function punto_sobre_ui(_x, _y)
{
    var _altura_hud = 90;
    return (_y > display_get_gui_height() - _altura_hud);
}
```

```gml
// ---------------------------------------------------------------------------
// objSelection — Draw GUI (el rectángulo de selección)
// ---------------------------------------------------------------------------
if (!arrastrando) exit;

var _x1 = min(rect_x1, rect_x2);
var _y1 = min(rect_y1, rect_y2);
var _x2 = max(rect_x1, rect_x2);
var _y2 = max(rect_y1, rect_y2);

draw_set_alpha(0.15);
draw_set_color(c_lime);
draw_rectangle(_x1, _y1, _x2, _y2, false);

draw_set_alpha(1);
draw_rectangle(_x1, _y1, _x2, _y2, true);
```

### 5.1 Órdenes

```gml
// ---------------------------------------------------------------------------
// scr_orders
// ---------------------------------------------------------------------------

/// @func Order(_tipo, _x, _y, _objetivo)
function Order(_tipo, _x, _y, _objetivo) constructor
{
    tipo     = _tipo;       // "mover" | "atacar" | "recolectar" | "construir"
    x        = _x;
    y        = _y;
    objetivo = (_objetivo == undefined) ? noone : _objetivo;
    completada = false;
}

/// @func dar_orden_a_seleccion(_x, _y)
/// @desc Asigna la orden a todas las unidades seleccionadas, en formación.
function dar_orden_a_seleccion(_x, _y)
{
    var _vx = camera_get_view_x(view_camera[0]);
    var _vy = camera_get_view_y(view_camera[0]);

    var _dest_x = _x + _vx;
    var _dest_y = _y + _vy;

    // ¿Hay un enemigo bajo el cursor? Entonces la orden es atacar.
    var _enemigo = instance_position(_dest_x, _dest_y, objEntity);
    var _tipo = "mover";
    var _objetivo = noone;

    if (_enemigo != noone && _enemigo.equipo != 0)
    {
        _tipo = "atacar";
        _objetivo = _enemigo;
    }

    // --- Formación: espiral alrededor del destino ---------------------------------
    var _n = array_length(objSelection.seleccionadas);
    var _radio = 12;
    var _por_anillo = 6;

    for (var _i = 0; _i < _n; _i++)
    {
        var _u = objSelection.seleccionadas[_i];
        if (!instance_exists(_u)) continue;

        // Posición en la espiral
        var _anillo = floor(_i / _por_anillo);
        var _pos_en_anillo = _i mod _por_anillo;
        var _angulo = (_pos_en_anillo / _por_anillo) * 360;

        var _off_x = lengthdir_x(_radio * (_anillo + 1), _angulo);
        var _off_y = lengthdir_y(_radio * (_anillo + 1), _angulo);

        var _orden = new Order(_tipo, _dest_x + _off_x, _dest_y + _off_y,
                               _objetivo);

        if (keyboard_check(vk_shift))
        {
            // Shift: encolar en vez de reemplazar
            array_push(_u.cola_ordenes, _orden);
        }
        else
        {
            // Sin Shift: reemplazar la cola
            array_resize(_u.cola_ordenes, 0);
            array_push(_u.cola_ordenes, _orden);
            _u.orden_actual = 0;
        }
    }

    // Marcador visual de la orden (un círculo que se desvanece)
    with (instance_create_depth(_dest_x, _dest_y, -9000, objOrderMarker))
    {
        es_ataque = (_tipo == "atacar");
    }

    audio_play_sound(sndOrder, 8, false);
}
```

### 5.2 Unidad ejecutando órdenes

```gml
// ---------------------------------------------------------------------------
// objUnit — Create
// ---------------------------------------------------------------------------
cola_ordenes  = [];
orden_actual  = 0;

velocidad     = 2.0;
rango_ataque  = 40;
dano          = 8;
cadencia      = 45;
cooldown      = 0;

seleccionada  = false;
equipo        = 0;

// Path
path_actual   = noone;

/// @func orden_activa()
function orden_activa()
{
    if (orden_actual >= array_length(cola_ordenes)) return undefined;
    return cola_ordenes[orden_actual];
}
```

```gml
// ---------------------------------------------------------------------------
// objUnit — Step
// ---------------------------------------------------------------------------
if (cooldown > 0) cooldown--;

var _orden = orden_activa();

if (_orden == undefined)
{
    // Sin órdenes: quedarse quieto
    if (path_actual != noone) { path_end(); path_actual = noone; }
}
else
{
    switch (_orden.tipo)
    {
        case "mover":
        case "atacar":
            // ¿Ya está en el destino o en rango del objetivo?
            var _listo = false;

            if (_orden.tipo == "atacar" && instance_exists(_orden.objetivo))
            {
                _listo = point_distance(x, y, _orden.objetivo.x, _orden.objetivo.y)
                         <= rango_ataque;

                if (_listo && cooldown <= 0)
                {
                    _orden.objetivo.hp -= dano;
                    cooldown = cadencia;

                    fx_impact(x, y, point_direction(x, y,
                              _orden.objetivo.x, _orden.objetivo.y), 0.5);
                }
            }
            else if (_orden.tipo == "mover")
            {
                _listo = point_distance(x, y, _orden.x, _orden.y) < 6;
            }

            if (_listo)
            {
                if (_orden.tipo == "mover" || !instance_exists(_orden.objetivo))
                {
                    // Orden completada: pasar a la siguiente
                    orden_actual++;
                    path_end();
                    path_actual = noone;
                }
            }
            else
            {
                // Moverse hacia el objetivo
                mover_hacia(_orden.tipo == "atacar" && instance_exists(_orden.objetivo)
                            ? _orden.objetivo.x : _orden.x,
                            _orden.tipo == "atacar" && instance_exists(_orden.objetivo)
                            ? _orden.objetivo.y : _orden.y);
            }
            break;

        case "recolectar":
            // Ir al recurso → volver al depósito → repetir
            ejecutar_recoleccion(_orden);
            break;
    }
}

// --- Muerte ------------------------------------------------------------------------
if (hp <= 0)
{
    fx_explosion(x, y, 0.7);
    audio_play_sound(sndUnitDie, 6, false);
    instance_destroy();
}
```

```gml
// ---------------------------------------------------------------------------
// objUnit — mover_hacia()
// ---------------------------------------------------------------------------

/// @func mover_hacia(_x, _y)
/// @desc Recalcula el path solo si hace falta (no cada frame).
function mover_hacia(_x, _y)
{
    // Recalcular cada 30 frames o si no hay path: es el compromiso correcto
    // entre respuesta y coste.
    if (path_actual != noone && (global.frame_count mod 30 != 0)) return;

    var _grid = objGrid.mp;

    if (path_actual == noone) path_actual = path_add();

    var _ok = mp_grid_path(_grid, path_actual, x, y, _x, _y, true);

    if (_ok)
    {
        path_start(path_actual, velocidad, path_action_stop, false);
        path_speed = velocidad;
    }
    else
    {
        // Sin path posible: moverse en línea recta (puede quedarse atascado
        // contra un muro, pero es mejor que no hacer nada)
        var _dir = point_direction(x, y, _x, _y);
        x += lengthdir_x(velocidad, _dir);
        y += lengthdir_y(velocidad, _dir);
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objUnit — Destroy (¡liberar el path!)
// ---------------------------------------------------------------------------
if (path_actual != noone && path_exists(path_actual))
{
    path_end();
    path_delete(path_actual);
    path_actual = noone;
}
```

### 5.3 Recursos y cola de producción

```gml
// ---------------------------------------------------------------------------
// scr_economy
// ---------------------------------------------------------------------------

/// @func ResourcePool()
function ResourcePool() constructor
{
    recursos = {
        mineral:  400,
        energia:  120,
        comida:   200
    };

    poblacion     = 6;
    poblacion_max = 20;

    tiene = function(_recurso, _cantidad)
    {
        if (!variable_struct_exists(recursos, _recurso)) return false;
        return recursos[$ _recurso] >= _cantidad;
    };

    gastar = function(_recurso, _cantidad)
    {
        if (!tiene(_recurso, _cantidad)) return false;
        recursos[$ _recurso] -= _cantidad;
        return true;
    };

    ganar = function(_recurso, _cantidad)
    {
        if (!variable_struct_exists(recursos, _recurso))
        {
            recursos[$ _recurso] = 0;
        }
        recursos[$ _recurso] += _cantidad;
    };

    /// @desc ¿Hay hueco de población para N unidades?
    hay_poblacion = function(_n)
    {
        return (poblacion + _n) <= poblacion_max;
    };

    usar_poblacion = function(_n)
    {
        if (!hay_poblacion(_n)) return false;
        poblacion += _n;
        return true;
    };

    liberar_poblacion = function(_n)
    {
        poblacion = max(0, poblacion - _n);
    };

    serialize = function()
    {
        return { recursos: recursos, poblacion: poblacion,
                 poblacion_max: poblacion_max };
    };

    static deserialize = function(_d)
    {
        var _p = new ResourcePool();
        _p.recursos      = _d.recursos;
        _p.poblacion     = _d.poblacion;
        _p.poblacion_max = _d.poblacion_max;
        return _p;
    };
}

/// @func UnitDef(_id, _hp, _velocidad, _dano, _coste, _coste_poblacion, _tiempo_produccion, _sprite)
function UnitDef(_id, _hp, _velocidad, _dano, _coste, _coste_poblacion, _tiempo_produccion, _sprite) constructor
{
    id                 = _id;
    hp                 = _hp;
    velocidad          = _velocidad;
    dano               = _dano;
    coste              = _coste;              // struct { mineral, energia, comida }
    coste_poblacion    = _coste_poblacion;
    tiempo_produccion  = _tiempo_produccion;   // frames en cola (§5.3)
    sprite             = _sprite;
}

/// @func units_init()
/// @desc Rellena `global.unit_defs` — sin esto, `encolar()` (más abajo) lee una
///       global que no existe y encolar la primera unidad revienta.
function units_init()
{
    global.unit_defs = {};
    global.unit_defs.worker  = new UnitDef("worker",  20, 2.4, 0, { mineral: 50 }, 1, 180, sprUnitWorker);
    global.unit_defs.soldier = new UnitDef("soldier", 60, 2.0, 8, { mineral: 80, energia: 20 }, 1, 300, sprUnitSoldier);
}
```

```gml
// ---------------------------------------------------------------------------
// objResourceManager — Create (persistente, va primero en la room — ver la
// jerarquía de §2: "objResourceManager (almacén global de recursos)")
// ---------------------------------------------------------------------------
// encolar() (§5.3) lee global.recursos y global.unit_defs, objBuilding — Step
// (§5.3) también lee global.unit_defs, y evaluar_expandir() (§5.5) lee
// global.recursos_enemigo. Ninguna de las tres se crea sola: si este objeto no
// va primero en la room, la primera orden de construir revienta con
// "variable global no definida".
global.recursos         = new ResourcePool();   // economía del jugador humano
global.recursos_enemigo = new ResourcePool();   // economía SEPARADA de la IA (§5.5) —
                                                 // nunca compartas el mismo ResourcePool
units_init();                                   // rellena global.unit_defs (arriba)
```

```gml
// ---------------------------------------------------------------------------
// objBuilding — Create (cola de producción)
// ---------------------------------------------------------------------------
cola = [];       // array de { id, tiempo_restante, tiempo_total }

/// @func encolar(_unidad_id)
function encolar(_unidad_id)
{
    var _def = global.unit_defs[$ _unidad_id];
    if (_def == undefined) return false;

    // --- Comprobar recursos y población ANTES de cobrar ---------------------------
    var _nombres = variable_struct_get_names(_def.coste);

    for (var _i = 0; _i < array_length(_nombres); _i++)
    {
        var _rec = _nombres[_i];
        if (!global.recursos.tiene(_rec, _def.coste[$ _rec]))
        {
            fx_floating_text(x, y - 20, "Falta " + _rec, c_red);
            audio_play_sound(sndError, 6, false);
            return false;
        }
    }

    if (!global.recursos.hay_poblacion(_def.coste_poblacion))
    {
        fx_floating_text(x, y - 20, "Población máxima", c_red);
        audio_play_sound(sndError, 6, false);
        return false;
    }

    // --- Cobrar AHORA (al encolar), no al completar ---------------------------------
    for (var _i = 0; _i < array_length(_nombres); _i++)
    {
        var _rec = _nombres[_i];
        global.recursos.gastar(_rec, _def.coste[$ _rec]);
    }
    global.recursos.usar_poblacion(_def.coste_poblacion);

    // --- Añadir a la cola ---------------------------------------------------------------
    array_push(cola, {
        id: _unidad_id,
        tiempo_restante: _def.tiempo_produccion,
        tiempo_total:    _def.tiempo_produccion
    });

    return true;
}
```

```gml
// ---------------------------------------------------------------------------
// objBuilding — Step (avanzar la cola)
// ---------------------------------------------------------------------------
if (array_length(cola) > 0)
{
    var _item = cola[0];

    _item.tiempo_restante--;

    if (_item.tiempo_restante <= 0)
    {
        // --- Completar: spawnear la unidad -------------------------------------------
        var _def = global.unit_defs[$ _item.id];

        var _u = instance_create_depth(
            x + lengthdir_x(40, irandom(359)),
            y + lengthdir_y(40, irandom(359)),
            -y, objUnit);

        _u.sprite_index = _def.sprite;
        _u.velocidad    = _def.velocidad;
        _u.hp           = _def.hp;
        _u.dano         = _def.dano;
        _u.equipo       = equipo;

        array_delete(cola, 0, 1);

        audio_play_sound(sndUnitReady, 8, false);
        fx_floating_text(x, y - 20, "¡Listo!", c_lime);
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objBuilding — Draw GUI (barra de progreso de la cola)
// ---------------------------------------------------------------------------
if (array_length(cola) == 0) exit;

var _vx = camera_get_view_x(view_camera[0]);
var _vy = camera_get_view_y(view_camera[0]);

var _px = x - _vx;
var _py = y - _vy - 30;

// Barra del elemento en producción
var _item = cola[0];
var _progreso = 1 - (_item.tiempo_restante / _item.tiempo_total);

draw_set_color(c_black);
draw_rectangle(_px - 20, _py, _px + 20, _py + 6, false);
draw_set_color(c_lime);
draw_rectangle(_px - 20, _py, _px - 20 + (40 * _progreso), _py + 6, false);

// Indicadores del resto de la cola
draw_set_color(c_gray);
for (var _i = 1; _i < array_length(cola); _i++)
{
    draw_rectangle(_px - 18 + (_i * 4), _py + 9, _px - 16 + (_i * 4), _py + 13, false);
}
```

### 5.4 Niebla de guerra

```gml
// ---------------------------------------------------------------------------
// scr_fog_of_war
// ---------------------------------------------------------------------------

#macro FOG_CELL 16
#macro FOG_NONE 0       // desconocido
#macro FOG_EXPLORED 1   // recordado
#macro FOG_VISIBLE 2    // visible ahora

/// @func FogOfWar(_ancho_celdas, _alto_celdas)
function FogOfWar(_ancho_celdas, _alto_celdas) constructor
{
    ancho = _ancho_celdas;
    alto  = _alto_celdas;

    celdas = [];
    for (var _y = 0; _y < alto; _y++)
    {
        var _fila = [];
        for (var _x = 0; _x < ancho; _x++) array_push(_fila, FOG_NONE);
        array_push(celdas, _fila);
    }

    /// @desc Marca como visible un círculo alrededor de un punto.
    revelar = function(_px, _py, _radio_px)
    {
        var _radio_celdas = ceil(_radio_px / FOG_CELL);
        var _cx = floor(_px / FOG_CELL);
        var _cy = floor(_py / FOG_CELL);

        for (var _dy = -_radio_celdas; _dy <= _radio_celdas; _dy++)
        {
            for (var _dx = -_radio_celdas; _dx <= _radio_celdas; _dx++)
            {
                if ((_dx * _dx) + (_dy * _dy) > (_radio_celdas * _radio_celdas)) continue;

                var _x = _cx + _dx;
                var _y = _cy + _dy;

                if (_x < 0 || _y < 0 || _x >= ancho || _y >= alto) continue;

                celdas[_y][_x] = FOG_VISIBLE;
            }
        }
    };

    /// @desc Al final del frame: lo visible pasa a ser solo recordado.
    ///       Se llama DESPUÉS de dibujar.
    envejecer = function()
    {
        for (var _y = 0; _y < alto; _y++)
            for (var _x = 0; _x < ancho; _x++)
            {
                if (celdas[_y][_x] == FOG_VISIBLE) celdas[_y][_x] = FOG_EXPLORED;
            }
    };

    get = function(_px, _py)
    {
        var _x = floor(_px / FOG_CELL);
        var _y = floor(_py / FOG_CELL);
        if (_x < 0 || _y < 0 || _x >= ancho || _y >= alto) return FOG_NONE;
        return celdas[_y][_x];
    };

    es_visible = function(_px, _py) { return get(_px, _py) == FOG_VISIBLE; };
    es_conocido = function(_px, _py) { return get(_px, _py) >= FOG_EXPLORED; };
}
```

```gml
// ---------------------------------------------------------------------------
// objFogOfWar — Create
// ---------------------------------------------------------------------------
fog = new FogOfWar(ceil(room_width / FOG_CELL), ceil(room_height / FOG_CELL));
depth = -5000;    // por encima del terreno, por debajo de la UI

// Superficie para dibujar la niebla con suavizado
surf = -1;
```

```gml
// ---------------------------------------------------------------------------
// objFogOfWar — End Step
// ---------------------------------------------------------------------------
// Revelar alrededor de cada unidad y edificio propios
with (objEntity)
{
    if (equipo == 0)
    {
        other.fog.revelar(x, y, rango_vision);
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objFogOfWar — Draw
// ---------------------------------------------------------------------------
// Dibujar la niebla: negro total en lo desconocido,
// sombra en lo recordado, nada en lo visible.
for (var _cy = 0; _cy < fog.alto; _cy++)
{
    for (var _cx = 0; _cx < fog.ancho; _cx++)
    {
        var _estado = fog.celdas[_cy][_cx];
        if (_estado == FOG_VISIBLE) continue;

        var _px = _cx * FOG_CELL;
        var _py = _cy * FOG_CELL;

        draw_set_alpha(_estado == FOG_NONE ? 1.0 : 0.55);
        draw_set_color(c_black);
        draw_rectangle(_px, _py, _px + FOG_CELL, _py + FOG_CELL, false);
    }
}
draw_set_alpha(1);

// Envejecer: lo de este frame pasa a "recordado"
fog.envejecer();
```

### 5.5 IA estratégica por utilidad

```gml
// ---------------------------------------------------------------------------
// objEnemyAI — Create
// ---------------------------------------------------------------------------
// Decide cada 2 segundos (120 frames), no cada frame.
intervalo_decision = 120;
timer              = 0;
accion_actual      = "expandir";
```

```gml
// ---------------------------------------------------------------------------
// objEnemyAI — Step
// ---------------------------------------------------------------------------
timer++;
if (timer < intervalo_decision) exit;
timer = 0;

// --- Evaluar todas las acciones, ejecutar la de mayor puntuación -----------------
var _opciones = [];

array_push(_opciones, {
    nombre: "recolectar",
    puntuacion: evaluar_recolectar(),
    ejecutar: function() { producir_workers(2); }
});

array_push(_opciones, {
    nombre: "defender",
    puntuacion: evaluar_defender(),
    ejecutar: function() { defender_base(); }
});

array_push(_opciones, {
    nombre: "atacar",
    puntuacion: evaluar_atacar(),
    ejecutar: function() { lanzar_ataque(); }
});

array_push(_opciones, {
    nombre: "expandir",
    puntuacion: evaluar_expandir(),
    ejecutar: function() { construir_edificio(); }
});

// Ordenar por puntuación descendente
array_sort(_opciones, function(_a, _b)
{
    return (_a.puntuacion > _b.puntuacion) ? -1 : 1;
});

// Ejecutar la mejor (si supera un umbral mínimo)
if (_opciones[0].puntuacion > 0.15)
{
    accion_actual = _opciones[0].nombre;
    _opciones[0].ejecutar();
}
```

```gml
// ---------------------------------------------------------------------------
// objEnemyAI — evaluadores
// ---------------------------------------------------------------------------

/// @desc ¿Cuántos workers hay en proporción a los soldados?
function evaluar_recolectar()
{
    var _workers = contar_unidades(objUnitWorker, 1);
    var _ideal = 8;

    return (_workers < _ideal) ? (1 - (_workers / _ideal)) : 0;
}

/// @desc ¿Hay enemigos cerca de mi base?
function evaluar_defender()
{
    var _amenaza = 0;

    var _base = instance_find(objBuilding, 0);
    if (_base == noone) return 0;

    with (objUnit)
    {
        if (equipo == 0 && point_distance(x, y, _base.x, _base.y) < 350)
        {
            _amenaza += 0.3;
        }
    }

    return clamp(_amenaza, 0, 1);
}

/// @desc ¿Tengo ejército suficiente para atacar?
function evaluar_atacar()
{
    var _soldados = contar_unidades(objUnitSoldier, 1);
    if (_soldados < 6) return 0;

    return clamp((_soldados - 6) / 14, 0, 1);
}

/// @desc ¿Me sobran recursos?
function evaluar_expandir()
{
    var _r = global.recursos_enemigo;
    if (_r == undefined) return 0;

    var _exceso = (_r.recursos.mineral > 600) ? 0.8 : 0.15;
    return _exceso;
}

/// @func contar_unidades(_obj, _equipo)
function contar_unidades(_obj, _equipo)
{
    var _n = 0;
    with (_obj) if (equipo == other._equipo || equipo == _equipo) _n++;
    return _n;
}
```

### 5.6 UI con UI Layers y Flex Panels

```gml
// ---------------------------------------------------------------------------
// objUILayer — Create
// ---------------------------------------------------------------------------
// Las UI Layers viven en la carpeta global "UI Folder" y se comparten
// entre todas las rooms. Puedes activarlas/desactivarlas por nombre.

nodo_hud        = layer_get_flexpanel_node("ui_hud");
nodo_seleccion  = layer_get_flexpanel_node("ui_selection");
nodo_menu       = layer_get_flexpanel_node("ui_menu");

// Empezar con el menú oculto
layer_set_visible("ui_menu", false);
```

```gml
// ---------------------------------------------------------------------------
// objUILayer — Room Start (recalcular el layout al cambiar de resolución)
// ---------------------------------------------------------------------------
var _w = display_get_gui_width();
var _h = display_get_gui_height();

if (nodo_hud != -1)
{
    flexpanel_calculate_layout(nodo_hud, _w, _h, 0);
}
if (nodo_seleccion != -1)
{
    flexpanel_calculate_layout(nodo_seleccion, _w, _h, 0);
}
```

```gml
// ---------------------------------------------------------------------------
// objUILayer — construir un panel de recursos en runtime
// ---------------------------------------------------------------------------

/// @func ui_crear_fila_recurso(_nombre, _icono, _valor_inicial)
/// @desc Crea un nodo Flex Panel nuevo y lo inserta en el HUD.
///       Útil cuando los recursos son dinámicos (mods, contenido nuevo).
function ui_crear_fila_recurso(_nombre, _icono, _valor_inicial)
{
    if (nodo_hud == -1) return noone;

    // Crear el nodo a partir de un struct (o de JSON)
    var _nodo = flexpanel_create_node({
        name: "recurso_" + _nombre,
        width: "auto",
        height: 24,
        flexDirection: "row",
        alignItems: "center",
        gap: 6
    });

    // Estilo: se puede ajustar con las funciones dedicadas
    flexpanel_node_style_set_flex_direction(_nodo, 0);   // 0 = fila
    flexpanel_node_style_set_gap(_nodo, 0, 6);
    flexpanel_node_style_set_padding(_nodo, 0, 4);

    // Insertar al final del HUD
    var _num_hijos = 0;
    while (flexpanel_node_get_child(nodo_hud, _num_hijos) != -1) _num_hijos++;

    flexpanel_node_insert_child(nodo_hud, _nodo, _num_hijos);

    // Recalcular para que aparezca en su sitio
    flexpanel_calculate_layout(nodo_hud,
        display_get_gui_width(), display_get_gui_height(), 0);

    return _nodo;
}

/// @func ui_leer_layout(_nodo)
/// @devuelve el struct del nodo para inspeccionar su posición calculada.
function ui_leer_layout(_nodo)
{
    return flexpanel_node_get_struct(_nodo);
}
```

```gml
// ---------------------------------------------------------------------------
// objUILayer — alternar un panel modal
// ---------------------------------------------------------------------------

/// @func ui_toggle_menu()
function ui_toggle_menu()
{
    var _visible = layer_get_visible("ui_menu");
    layer_set_visible("ui_menu", !_visible);
}
```

> **Nota:** para la mayoría de proyectos, la forma práctica de trabajar es
> **diseñar los Flex Panels en el editor de rooms** (arrastrando elementos a la
> UI Layer) y usar las funciones `flexpanel_*` solo para lo dinámico. Crear
> todo por código es posible pero mucho más trabajoso.

### 5.7 HUD tradicional (alternativa sin UI Layers)

Si prefieres no usar UI Layers todavía, el HUD clásico sigue funcionando:

```gml
// ---------------------------------------------------------------------------
// objHUD — Draw GUI
// ---------------------------------------------------------------------------
var _gw = display_get_gui_width();
var _gh = display_get_gui_height();
var _hud_h = 90;

// --- Fondo del HUD ---------------------------------------------------------------
draw_set_alpha(0.85);
draw_set_color(c_black);
draw_rectangle(0, _gh - _hud_h, _gw, _gh, false);
draw_set_alpha(1);

// --- Recursos ------------------------------------------------------------------------
draw_set_font(fntHUD);
draw_set_color(c_white);

var _x = 16;
var _nombres = variable_struct_get_names(global.recursos.recursos);

for (var _i = 0; _i < array_length(_nombres); _i++)
{
    var _rec = _nombres[_i];
    var _valor = global.recursos.recursos[$ _rec];

    draw_text(_x, _gh - _hud_h + 12, string_upper(_rec) + ":");
    draw_set_color(c_yellow);
    draw_text(_x + 10 + string_width(string_upper(_rec) + ":"),
              _gh - _hud_h + 12, string(_valor));
    draw_set_color(c_white);

    _x += 130;
}

// --- Población ---------------------------------------------------------------------------
draw_text(16, _gh - _hud_h + 40,
          "POB: " + string(global.recursos.poblacion) + " / " +
          string(global.recursos.poblacion_max));

// --- Selección -----------------------------------------------------------------------------
var _sel = objSelection.seleccionadas;

if (array_length(_sel) > 0)
{
    draw_set_color(c_lime);
    draw_text(16, _gh - _hud_h + 64,
              "SELECCIÓN: " + string(array_length(_sel)) + " unidades");
}

// --- Minimap (esquina inferior derecha) ---------------------------------------------------
var _mm_w = 160;
var _mm_h = 120;
var _mm_x = _gw - _mm_w - 12;
var _mm_y = _gh - _hud_h - _mm_h - 12;

draw_set_color(c_black);
draw_rectangle(_mm_x, _mm_y, _mm_x + _mm_w, _mm_y + _mm_h, false);
draw_set_color(c_gray);
draw_rectangle(_mm_x, _mm_y, _mm_x + _mm_w, _mm_y + _mm_h, true);

// Puntos de las unidades en el minimapa
var _escala_x = _mm_w / room_width;
var _escala_y = _mm_h / room_height;

with (objEntity)
{
    var _px = _mm_x + (x * _escala_x);
    var _py = _mm_y + (y * _escala_y);

    draw_set_color((equipo == 0) ? c_lime : c_red);
    draw_rectangle(_px - 1, _py - 1, _px + 1, _py + 1, false);
}

// Rectángulo de la vista actual
var _vx = camera_get_view_x(view_camera[0]) * _escala_x;
var _vy = camera_get_view_y(view_camera[0]) * _escala_y;
var _vw = camera_get_view_width(view_camera[0]) * _escala_x;
var _vh = camera_get_view_height(view_camera[0]) * _escala_y;

draw_set_color(c_white);
draw_rectangle(_mm_x + _vx, _mm_y + _vy,
               _mm_x + _vx + _vw, _mm_y + _vy + _vh, true);
```

---

## 6. Gestión del estado del jugador

```gml
// ---------------------------------------------------------------------------
// scr_strategy_state
// ---------------------------------------------------------------------------

/// @func StrategyState()
/// @desc Estado completo de una partida de estrategia.
function StrategyState() constructor
{
    recursos    = new ResourcePool();
    unidades    = [];
    edificios   = [];
    tecnologias = {};        // { blindaje_mejorado: true }

    // Progreso
    mision      = 1;
    tiempo_frames = 0;
    bajas_propias = 0;
    bajas_enemigas = 0;

    /// @desc Registra la muerte de una unidad.
    registrar_baja = function(_equipo)
    {
        if (_equipo == 0) bajas_propias++;
        else              bajas_enemigas++;
    };

    ratio_bajas = function()
    {
        if (bajas_propias == 0) return bajas_enemigas;
        return bajas_enemigas / bajas_propias;
    };

    /// @desc Serializa solo el ESENCIAL: las unidades se reconstruyen
    ///       guardando tipo + posición, no la instancia.
    serialize = function()
    {
        var _unidades_out = [];
        for (var _i = 0; _i < array_length(unidades); _i++)
        {
            var _u = unidades[_i];
            if (!instance_exists(_u)) continue;

            array_push(_unidades_out, {
                tipo: _u.tipo_id,
                x: _u.x, y: _u.y,
                hp: _u.hp,
                equipo: _u.equipo
            });
        }

        var _edificios_out = [];
        for (var _i = 0; _i < array_length(edificios); _i++)
        {
            var _b = edificios[_i];
            if (!instance_exists(_b)) continue;

            array_push(_edificios_out, {
                tipo: _b.tipo_id,
                x: _b.x, y: _b.y,
                hp: _b.hp,
                cola: _b.cola
            });
        }

        return {
            recursos: recursos.serialize(),
            unidades: _unidades_out,
            edificios: _edificios_out,
            tecnologias: tecnologias,
            mision: mision,
            tiempo_frames: tiempo_frames
        };
    };
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Un `mp_grid_path` por unidad y por frame | 100 unidades = 100 paths/frame = 5 fps | Recalcular cada 30 frames; o campo de flujo |
| No liberar los paths al destruir unidades | Fuga de memoria | `path_delete()` en el evento Destroy |
| Selección en coordenadas de pantalla | Seleccionas unidades que no están donde apuntas | Convierte con `camera_get_view_x/y` |
| Clic sobre el HUD que selecciona unidades | El HUD se vuelve "transparente" al input | `punto_sobre_ui()` antes de procesar |
| Todas las unidades al mismo punto | Se empujan y se atascan | Formación en espiral alrededor del destino |
| Órdenes sin cola | No puedes encadenar movimientos | Array de órdenes + Shift para encolar |
| Cobrar recursos al completar la producción | No sabes por qué no puedes producir más | Cobrar al encolar |
| Niebla de guerra que no envejece | Todo lo que viste sigue "visible" | `envejecer()` al final del frame |
| Niebla por píxel | Lentísimo | Niebla por celda de 16 px |
| IA que decide cada frame | Impredecible y caro | Decidir cada 120 frames |
| IA sin umbral mínimo | Hace cosas sin sentido con puntuación 0.01 | Umbral de 0.15 antes de ejecutar |
| Redefinir `array_contains` | Error de compilación: ya es nativa | Usa la nativa |
| Serializar instancias en el save | Al cargar, todo roto | Guarda tipo + posición, recrea después |
| Recalcular el layout de Flex Panels cada frame | Coste innecesario | Solo al cambiar resolución o al insertar nodos |

---

## 8. Cómo escalarlo

1. **Campo de flujo** para cientos de unidades: BFS desde el destino hasta
   todas las celdas, y cada unidad lee la dirección de su celda.
2. **Árbol de tecnologías** — nodos con prerequisitos, desbloqueables con
   recursos. Reutiliza el patrón de `flags` del metroidvania (receta 06).
3. **Formaciones** — línea, cuña, círculo. Cambia los offsets de destino según
   la formación elegida.
4. **Niebla suave** — interpola la visibilidad por celda para que no se vean
   bloques cuadrados.
5. **Modo *replay*** — graba las órdenes con su timestamp; el juego es
   determinista si fijas la semilla.
6. **Multijugador** — ver receta 14. Es el santo grial del RTS y el más difícil.
7. **Editor de mapas** — los mapas son tilemaps + listas de entidades: ambos
   serializables a JSON.
8. **Modo campaña** — misiones con condiciones de victoria como structs.

**Cuándo pasar a otra receta:** si has llegado aquí y funciona, ya eres capaz
de montar cualquier cosa en GameMaker. Lo que te falta es terminar un proyecto,
no aprender más técnicas.

---

## 9. Fuentes

- Manual oficial — **UI Layers** —
  https://manual.gamemaker.io/lts/en/The_Asset_Editors/Editor_Room_UI_Layers.htm
- Manual oficial — **Flex Panel Functions** (`layer_get_flexpanel_node`,
  `flexpanel_create_node`, `flexpanel_node_insert_child`,
  `flexpanel_calculate_layout`, `flexpanel_node_get_struct`,
  `flexpanel_node_get_child`, `flexpanel_node_style_set_*`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/UI_Layers.htm
- Manual oficial — MP Grids (`mp_grid_path`, `mp_grid_create`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Motion_Planning.htm
- Manual oficial — Paths (`path_add`, `path_start`, `path_delete`, `path_end`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Paths.htm
- Manual oficial — `layer_set_visible`, `layer_get_visible` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/General_Layer_Functions.htm
- Manual oficial — `array_contains`, `array_sort`, `array_delete`,
  `array_resize` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm
- Manual oficial — `string_upper`, `string_width` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/Strings.htm
- Receta propia: **08 — Tower Defense** (grids, pathfinding, economía)
- Receta propia: **05 — Roguelike** (FOV, flood fill, grids 2D)
