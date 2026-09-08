# 04 — RPG / Action RPG

> **Dificultad:** media‑avanzada
> Es el primer género donde el **estado persistente** manda. Ya no basta con
> que el juego funcione en una room: tiene que recordar.

---

## 1. Visión general

Un RPG es un juego de **números que crecen**. El jugador hace cosas, los
números suben, y el crecimiento de esos números es la recompensa. Todo lo
demás (historia, exploración, combate) es el vehículo.

**Lo que define al género:**

- **Progresión medible**: nivel, experiencia, estadísticas, equipo.
- **Estado persistente**: lo que haces en la room 3 afecta a la room 12.
- **Contenido dirigido por datos**: 200 objetos, 50 enemigos, 30 quests.
  Si los escribes en código, el proyecto muere.
- **El jugador toma decisiones de construcción** (*build*): cómo repartir
  puntos, qué equipo llevar.

**Referencias hechas en GameMaker:** *Undertale*, *Hyper Light Drifter*,
*Deltarune*, *Lisa*, *OMORI*, *Sea of Stars* (no, ese es Unity). GameMaker es
uno de los motores históricos del RPG indie: la guía oficial lo cita
explícitamente.

**Subgéneros:**

| Subgénero | Combate | Exploración | Referencia |
|---|---|---|---|
| JRPG por turnos | Por turnos, menús | Top-down, tile based | Final Fantasy, Undertale |
| Action RPG | Tiempo real | Top-down o plataformas | Diablo, Hyper Light Drifter |
| Táctico por turnos | Por turnos en grid | Grid | Final Fantasy Tactics |
| *Dungeon crawler* | Por turnos | Primera persona en rejilla | Wizardry |

---

## 2. Arquitectura recomendada

### La regla de oro: datos separados de lógica

```
datafiles/
├── items.json          ← TODOS los objetos del juego
├── enemies.json        ← TODOS los enemigos
├── quests.json         ← TODAS las misiones
└── dialogue.json       ← TODOS los diálogos
```

Cuando el contenido vive en JSON, puedes cambiar el balance sin recompilar,
traducir el juego sin tocar código, y dejar que un diseñador (o tú mismo
dentro de seis meses) edite el juego sin miedo.

### Jerarquía de objetos

```
objEntity            (padre: stats, daño, muerte)
├── objPlayer
├── objNPC           (sin combate, con diálogo)
├── objEnemy         (padre de enemigos)
│   └── objEnemyBoss
├── objChest
└── objInteractable  (puertas, carteles, transiciones)

objBattleManager     (solo en combate por turnos)
objDialogue          (caja de diálogo, persistente)
objQuestLog
objInventoryUI
objGame              (persistente: estado global del mundo)
objCamera
```

### Rooms

```
rm_town_01           (pueblo: NPCs, tienda, sin combate)
rm_dungeon_01        (mazmorra: enemigos, cofres)
rm_battle            (sala de combate por turnos — solo JRPG)
rm_worldmap          (mapa del mundo a gran escala)
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `Stats` | Fuerza, defensa, velocidad... con modificadores de equipo |
| `Inventory` | Array de pila `{ item_id, cantidad }` |
| `Equipment` | Slots: arma, armadura, accesorio |
| `Quest` | Estado de una misión: pasos, progreso, recompensas |
| `DialogueNode` | Un nodo de conversación con opciones ramificadas |
| `SaveGame` | Serialización completa del estado del mundo |

---

## 3. El bucle central (core loop)

```
┌─ Begin Step ─────────────────────────────────────────────┐
│ 1. Input del jugador                                     │
└──────────────────────────────────────────────────────────┘
┌─ Step ───────────────────────────────────────────────────┐
│ 2. Movimiento (grid en JRPG, libre en Action RPG)        │
│ 3. Interacción: ¿se pulsó "usar" delante de algo?        │
│ 4. Si encuentro aleatorio (JRPG) → ir a rm_battle        │
│ 5. Actualizar enemigos / IA                              │
│ 6. Actual quests (comprobar condiciones de paso)         │
│ 7. Actualizar diálogo activo                             │
│ 8. HUD: vida, mana, minimapa                             │
└──────────────────────────────────────────────────────────┘
┌─ End Step ───────────────────────────────────────────────┐
│ 9. Cámara                                                │
└──────────────────────────────────────────────────────────┘
```

**En combate por turnos el bucle es distinto** — es una máquina de estados
que espera input:

```
turno_jugador → elegir acción → resolver → turno_enemigo → resolver
   ↑                                                            │
   └──────────────────── comprobar fin ←───────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 Stats con modificadores

Hay dos formas de calcular las estadísticas finales y **la segunda es la
correcta**:

```gml
// ❌ Modificar la base al equipar: pierdes el valor original al desequipar.
stats.attack += espada.bonus;

// ✅ Base + suma de modificadores: se recalcula siempre.
stats.get_attack = function() {
    return stats.attack_base + equipo.suma("attack") + buffs.attack;
};
```

Recalcular en vez de acumular elimina toda una familia de bugs: stats que no
vuelven a su valor, dobles equipamientos, objetos que se pierden.

### 4.2 Curvas de experiencia

La fórmula más usada en la industria es potencial:

```gml
function xp_needed(_level)
{
    return floor(base * power(_level, exponente));
}
```

| Exponente | Sensación | Uso |
|---|---|---|
| 1.0 | Lineal, constante | Juegos cortos |
| 1.5 | Curva suave | Estándar (Pokémon-ish) |
| 2.0 | Curva dura | RPGs largos |
| 2.5+ | Muro artificial | MMOs / gacha |

**Regla de diseño:** el tiempo para subir de nivel debe crecer, pero el
**poder por hora** debe mantenerse constante o el jugador siente que se
estanca.

### 4.3 Inventario

Un inventario es un array de pilas. Nunca guardes 30 entradas de "poción";
guarda una con `cantidad = 30`.

```gml
inventory = [
    { item_id: "potion",    cantidad: 12 },
    { item_id: "iron_sword", cantidad: 1 }
];
```

Las claves son **IDs de texto**, no índices numéricos. Si insertas un objeto
nuevo en medio del JSON, los saves antiguos siguen funcionando.

### 4.4 Combate por turnos vs acción

| Aspecto | Por turnos | Acción |
|---|---|---|
| Implementación | Más fácil (máquina de estados) | Más difícil (colisiones, hitboxes) |
| Arte requerido | Menos animaciones | Muchas más |
| Balance | Predecible, controlable | Difícil de afinar |
| Accesibilidad | Alta (sin presión de tiempo) | Menor |
| **Recomendación** | **Empieza aquí** | Pasa a ello después |

El tutorial oficial de RPG ofrece **ambas** versiones del combate con
proyectos descargables. Empieza por turnos: la máquina de estados que
construyas te servirá también para el diálogo y para los menús.

### 4.5 Diálogos ramificados

Un diálogo es un **grafo de nodos**. Cada nodo tiene texto, retrato y una
lista de opciones; cada opción apunta a otro nodo. Con structs es trivial:

```gml
node = {
    speaker: "María",
    portrait: sprMaria,
    text: "¿Vas a ayudarme?",
    choices: [
        { text: "Sí",        next: "maria_ayuda" },
        { text: "No",        next: "maria_rechazo" },
        { text: "Quizá...",  next: "maria_duda",
          condition: function() { return global.flags.habla_con_pedro; } }
    ]
};
```

### 4.6 Tilemaps para mapas grandes

Para un RPG, el mapa es un tilemap. La colisión se consulta por tile, no por
objeto: mil veces más barato y más fácil de editar.

```gml
// Crear la capa de colisión una vez
var _lay = layer_get_id("Tiles_Collision");
tilemap_colision = layer_tilemap_get_id(_lay);

// Consultar si una celda es sólida
var _tile = tilemap_get_at_pixel(tilemap_colision, _x, _y);
var _solido = (_tile != 0);   // tile 0 = vacío
```

### 4.7 Save / load

`json_stringify()` convierte structs y arrays a texto. `json_parse()` lo
devuelve. Es todo lo que necesitas, con tres advertencias:

1. **Las funciones (métodos) NO se serializan.** Un struct con métodos pierde
   el comportamiento. Solución: serializa una copia plana (método
   `serialize()`), como en la receta 01.
2. **Los IDs de instancia no son estables** entre sesiones. Guarda posiciones
   y tipos, no referencias.
3. **Guarda un número de versión.** Cuando cambies la estructura del save,
   ese número te permite migrar en vez de romper.

---

## 5. Código base

### 5.0 Estadísticas

```gml
// ---------------------------------------------------------------------------
// scr_stats
// ---------------------------------------------------------------------------

/// @func Stats(_vida, _ataque, _defensa, _velocidad)
function Stats(_vida, _ataque, _defensa, _velocidad) constructor
{
    // --- Valores base (nunca se modifican al equipar) ---
    hp_base       = _vida;
    attack_base   = _ataque;
    defense_base  = _defensa;
    speed_base    = _velocidad;

    // --- Derivados actuales ---
    hp        = _vida;
    hp_max    = _vida;
    mp        = 20;
    mp_max    = 20;

    // --- Modificadores temporales (buffs / debuffs) ---
    mods = {
        attack:  0,
        defense: 0,
        speed:   0
    };

    /// @desc Devuelve la suma de modificadores de equipo.
    ///       `equipment` es un struct con slots { weapon, armor, accessory }
    get_equip_bonus = function(_stat_name)
    {
        var _total = 0;
        if (!variable_global_exists("equipment")) return 0;

        var _eq = global.equipment;
        var _slots = ["weapon", "armor", "accessory"];

        for (var _i = 0; _i < array_length(_slots); _i++)
        {
            var _slot = _slots[_i];
            var _item = _eq[$ _slot];
            if (_item == noone || _item == undefined) continue;

            var _def = item_get_def(_item.item_id);
            if (_def != undefined && variable_struct_exists(_def, "bonuses"))
            {
                var _b = _def.bonuses;
                if (variable_struct_exists(_b, _stat_name))
                {
                    _total += _b[$ _stat_name];
                }
            }
        }
        return _total;
    };

    /// @desc Valor final de una estadística.
    get = function(_stat_name)
    {
        var _base = 0;
        switch (_stat_name)
        {
            case "hp":      _base = hp_base;      break;
            case "attack":  _base = attack_base;  break;
            case "defense": _base = defense_base; break;
            case "speed":   _base = speed_base;   break;
        }
        var _mod = variable_struct_exists(mods, _stat_name) ? mods[$ _stat_name] : 0;
        return _base + _mod + get_equip_bonus(_stat_name);
    };

    /// @desc Recalcula hp_max tras cambiar de equipo/nivel.
    refresh = function()
    {
        var _new_max = get("hp");
        // Ajustar hp proporcionalmente para no curar ni matar al cambiar
        var _ratio = (hp_max > 0) ? (hp / hp_max) : 1;
        hp_max = _new_max;
        hp     = clamp(round(hp_max * _ratio), 1, hp_max);
    };

    /// @desc Aplica daño con mitigación por defensa.
    take_damage = function(_cantidad, _defensa_objetivo)
    {
        var _mitigado = max(1, _cantidad - (_defensa_objetivo * 0.5));
        hp = max(0, hp - round(_mitigado));
        return round(_mitigado);
    };

    /// @desc Fórmula de daño base.
    ///       La división por 2 evita que la defensa anule el ataque.
    calcular_dano = function(_stats_atacante, _stats_defensor)
    {
        var _atk = _stats_atacante.get("attack");
        var _def = _stats_defensor.get("defense");
        var _variacion = random_range(0.90, 1.10);
        return max(1, round((_atk - (_def * 0.5)) * _variacion));
    };

    serialize = function()
    {
        return {
            hp_base: hp_base, attack_base: attack_base,
            defense_base: defense_base, speed_base: speed_base,
            hp: hp, hp_max: hp_max, mp: mp, mp_max: mp_max,
            mods: mods
        };
    };

    static deserialize = function(_d)
    {
        var _s = new Stats(_d.hp_base, _d.attack_base, _d.defense_base, _d.speed_base);
        _s.hp     = _d.hp;
        _s.hp_max = _d.hp_max;
        _s.mp     = _d.mp;
        _s.mp_max = _d.mp_max;
        _s.mods   = _d.mods;
        return _s;
    };
}
```

### 5.1 Niveles y curva de experiencia

```gml
// ---------------------------------------------------------------------------
// scr_progression
// ---------------------------------------------------------------------------

/// @func Progression()
/// @desc Nivel, experiencia y puntos de estadística.
function Progression() constructor
{
    level       = 1;
    xp          = 0;
    stat_points = 0;
    skill_points = 0;

    // Parámetros de la curva: xp_total(L) = floor(base * L^exponente)
    curve_base      = 100;
    curve_exponent  = 1.5;

    /// @desc Experiencia TOTAL acumulada necesaria para alcanzar _nivel.
    xp_for_level = function(_nivel)
    {
        if (_nivel <= 1) return 0;
        return floor(curve_base * power(_nivel - 1, curve_exponent));
    };

    /// @desc Experiencia que falta para el siguiente nivel.
    xp_to_next = function()
    {
        return xp_for_level(level + 1) - xp;
    };

    /// @desc Progreso 0..1 dentro del nivel actual (para la barra del HUD).
    xp_progress = function()
    {
        var _actual = xp_for_level(level);
        var _siguiente = xp_for_level(level + 1);
        if (_siguiente <= _actual) return 1;
        return clamp((xp - _actual) / (_siguiente - _actual), 0, 1);
    };

    /// @desc Añade experiencia. Devuelve cuántos niveles ha subido.
    add_xp = function(_cantidad)
    {
        xp += _cantidad;

        var _subidos = 0;
        while (xp >= xp_for_level(level + 1))
        {
            level_up();
            _subidos++;
            if (level >= 99) break;      // tope de seguridad anti-bucle
        }
        return _subidos;
    };

    /// @desc Sube un nivel y reparte puntos.
    level_up = function()
    {
        level++;
        stat_points  += 3;
        skill_points += 1;

        // Crecimiento automático de stats base
        var _s = global.player_stats;
        _s.hp_base      += 8;
        _s.attack_base  += 3;
        _s.defense_base += 2;
        _s.speed_base   += 1;

        // Curar al subir de nivel (convención del género)
        _s.hp = _s.hp_max = _s.get("hp");

        // Feedback
        fx_floating_text(objPlayer.x, objPlayer.y - 24, "¡NIVEL " + string(level) + "!",
                         c_yellow);
        audio_play_sound(sndLevelUp, 10, false);

        return level;
    };

    /// @desc Gasta un punto de estadística.
    spend_point = function(_stat_name)
    {
        if (stat_points <= 0) return false;

        var _s = global.player_stats;
        switch (_stat_name)
        {
            case "hp":      _s.hp_base      += 10; break;
            case "attack":  _s.attack_base  += 4;  break;
            case "defense": _s.defense_base += 3;  break;
            case "speed":   _s.speed_base   += 2;  break;
            default: return false;
        }

        stat_points--;
        _s.refresh();
        return true;
    };

    serialize = function()
    {
        return {
            level: level, xp: xp,
            stat_points: stat_points, skill_points: skill_points,
            curve_base: curve_base, curve_exponent: curve_exponent
        };
    };

    static deserialize = function(_d)
    {
        var _p = new Progression();
        _p.level = _d.level;
        _p.xp = _d.xp;
        _p.stat_points = _d.stat_points;
        _p.skill_points = _d.skill_points;
        return _p;
    };
}
```

### 5.2 Inventario y equipamiento

```gml
// ---------------------------------------------------------------------------
// scr_inventory
// ---------------------------------------------------------------------------

/// @func Inventory(_capacidad)
function Inventory(_capacidad) constructor
{
    slots     = [];        // array de { item_id, cantidad }
    capacidad = (_capacidad == undefined) ? 20 : _capacidad;
    oro       = 0;

    /// @desc Añade una cantidad de un objeto. Apila si ya existe.
    add = function(_item_id, _cantidad)
    {
        var _def = item_get_def(_item_id);
        if (_def == undefined)
        {
            show_debug_message("Objeto inexistente: " + string(_item_id));
            return false;
        }

        _cantidad = (_cantidad == undefined) ? 1 : _cantidad;

        // Si apila, buscar una pila existente
        if (_def.stackable)
        {
            var _len = array_length(slots);
            for (var _i = 0; _i < _len; _i++)
            {
                if (slots[_i].item_id == _item_id)
                {
                    slots[_i].cantidad += _cantidad;
                    return true;
                }
            }
        }

        // Pila nueva
        if (array_length(slots) >= capacidad) return false;

        array_push(slots, { item_id: _item_id, cantidad: _cantidad });
        return true;
    };

    /// @desc Quita una cantidad. Devuelve true si se pudo.
    remove = function(_item_id, _cantidad)
    {
        _cantidad = (_cantidad == undefined) ? 1 : _cantidad;

        var _len = array_length(slots);
        for (var _i = 0; _i < _len; _i++)
        {
            if (slots[_i].item_id == _item_id)
            {
                slots[_i].cantidad -= _cantidad;

                if (slots[_i].cantidad <= 0)
                {
                    array_delete(slots, _i, 1);
                }
                return true;
            }
        }
        return false;
    };

    count = function(_item_id)
    {
        var _len = array_length(slots);
        for (var _i = 0; _i < _len; _i++)
        {
            if (slots[_i].item_id == _item_id) return slots[_i].cantidad;
        }
        return 0;
    };

    has = function(_item_id, _cantidad)
    {
        return count(_item_id) >= ((_cantidad == undefined) ? 1 : _cantidad);
    };

    serialize = function()
    {
        return { slots: slots, capacidad: capacidad, oro: oro };
    };

    static deserialize = function(_d)
    {
        var _inv = new Inventory(_d.capacidad);
        _inv.slots = _d.slots;
        _inv.oro   = _d.oro;
        return _inv;
    };
}
```

```gml
/// @func Equipment()
/// @desc Slots de equipamiento. Guarda { item_id } para poder reconstruirlo.
function Equipment() constructor
{
    weapon    = noone;
    armor     = noone;
    accessory = noone;

    /// @desc Equipa un objeto desde el inventario. Devuelve el anterior.
    equip = function(_item_id)
    {
        var _def = item_get_def(_item_id);
        if (_def == undefined) return noone;
        if (!variable_struct_exists(_def, "slot")) return noone;

        var _slot = _def.slot;
        if (!variable_struct_exists(self, _slot)) return noone;

        var _anterior = self[$ _slot];

        // Devolver el objeto anterior al inventario
        if (_anterior != noone)
        {
            global.inventory.add(_anterior.item_id, 1);
        }

        self[$ _slot] = { item_id: _item_id };
        global.inventory.remove(_item_id, 1);

        global.player_stats.refresh();
        return _anterior;
    };

    unequip = function(_slot)
    {
        var _actual = self[$ _slot];
        if (_actual == noone) return false;

        global.inventory.add(_actual.item_id, 1);
        self[$ _slot] = noone;
        global.player_stats.refresh();
        return true;
    };

    serialize = function()
    {
        return {
            weapon:    (weapon    == noone) ? -1 : weapon.item_id,
            armor:     (armor     == noone) ? -1 : armor.item_id,
            accessory: (accessory == noone) ? -1 : accessory.item_id
        };
    };

    static deserialize = function(_d)
    {
        var _e = new Equipment();
        if (_d.weapon    != -1) _e.weapon    = { item_id: _d.weapon };
        if (_d.armor     != -1) _e.armor     = { item_id: _d.armor };
        if (_d.accessory != -1) _e.accessory = { item_id: _d.accessory };
        return _e;
    };
}
```

**Peso y capacidad de carga** (informe de auditoría r3-2026-09-06, tema 3: mencionado en
`04 · 09 §4.2` como «opcional», sin campo ni fórmula en ningún sitio de la biblioteca). Se añade
como funciones sueltas alrededor de `Inventory` de arriba, **sin tocar su constructor**: así
cualquier código existente que llama a `new Inventory(_capacidad)` sigue compilando igual.

```gml
// ---------------------------------------------------------------------------
// scr_inventory_peso — extensión opcional sobre Inventory (arriba). No forma
// parte del constructor: asigna `peso_maximo` a la instancia tras crearla
// (o dentro de tu propio constructor si extiendes Inventory), y solo si lo
// asignas se aplica ningún límite.
// ---------------------------------------------------------------------------
// var _inv = new Inventory(20);
// _inv.peso_maximo = 60;             // opcional; sin asignar = sin límite de peso

/// @func inventory_peso_total(_inventario)
/// @desc Suma item_get_def(item_id).weight * cantidad de cada pila (§5.3). Un
///       ítem sin campo "weight" cuenta como peso 0: no rompe catálogos que
///       todavía no lo declaren.
/// @return {Real}
function inventory_peso_total(_inventario)
{
    var _total = 0;
    var _len   = array_length(_inventario.slots);

    for (var _i = 0; _i < _len; _i++)
    {
        var _slot = _inventario.slots[_i];
        var _def  = item_get_def(_slot.item_id);
        var _peso = (_def != undefined && variable_struct_exists(_def, "weight"))
            ? _def.weight : 0;

        _total += _peso * _slot.cantidad;
    }
    return _total;
}

/// @func inventory_add_con_peso(_inventario, _item_id, _cantidad)
/// @desc Envuelve Inventory.add() (arriba) SIN modificarla: si la instancia
///       tiene `peso_maximo` asignado, comprueba que añadir no lo supere
///       ANTES de delegar en add() — comprobar antes que efecto, como en
///       04 · 09 §5.1.
/// @return {Bool}
function inventory_add_con_peso(_inventario, _item_id, _cantidad)
{
    if (variable_struct_exists(_inventario, "peso_maximo")
        && _inventario.peso_maximo != undefined)
    {
        var _def  = item_get_def(_item_id);
        var _peso = (_def != undefined && variable_struct_exists(_def, "weight"))
            ? _def.weight : 0;

        if (inventory_peso_total(_inventario) + (_peso * _cantidad) > _inventario.peso_maximo)
        {
            return false;   // se pasaría del límite: no añade nada
        }
    }
    return _inventario.add(_item_id, _cantidad);
}

/// @func jugador_penalizacion_por_peso(_inventario, _fraccion_sobrecarga = 0.85)
/// @desc Multiplicador de velocidad según cuánto peso lleva el jugador. Por
///       debajo de `_fraccion_sobrecarga` de `peso_maximo` no hay
///       penalización; a partir de ahí baja de forma lineal hasta 0.4 al
///       llegar al 100 %. Sin `peso_maximo` asignado, siempre devuelve 1.0.
/// @return {Real} Multiplicador 0.4..1.0 para aplicar a `objPlayer.hspeed`/`vspeed`.
function jugador_penalizacion_por_peso(_inventario, _fraccion_sobrecarga = 0.85)
{
    if (!variable_struct_exists(_inventario, "peso_maximo")
        || _inventario.peso_maximo == undefined)
    {
        return 1.0;
    }

    var _fraccion = inventory_peso_total(_inventario) / _inventario.peso_maximo;
    if (_fraccion <= _fraccion_sobrecarga) return 1.0;

    var _exceso = (_fraccion - _fraccion_sobrecarga) / (1 - _fraccion_sobrecarga);   // 0..1
    return lerp(1.0, 0.4, clamp(_exceso, 0, 1));
}
```

### 5.3 Contenido en JSON

```json
// datafiles/items.json
[
  {
    "id": "potion",
    "name": "Poción",
    "description": "Restaura 50 puntos de vida.",
    "type": "consumable",
    "stackable": true,
    "icon": "sprIconPotion",
    "value": 25,
    "weight": 0.2,
    "effect": { "heal": 50 }
  },
  {
    "id": "iron_sword",
    "name": "Espada de hierro",
    "description": "Una espada simple pero fiable.",
    "type": "weapon",
    "stackable": false,
    "slot": "weapon",
    "icon": "sprIconSword",
    "value": 150,
    "weight": 4,
    "bonuses": { "attack": 12 }
  },
  {
    "id": "leather_armor",
    "name": "Armadura de cuero",
    "description": "Protección ligera.",
    "type": "armor",
    "stackable": false,
    "slot": "armor",
    "icon": "sprIconArmor",
    "value": 100,
    "weight": 6,
    "bonuses": { "defense": 7, "hp": 15 }
  }
]
```

> ⚠️ `"weight"` es una extensión de esta biblioteca (informe de auditoría r3-2026-09-06, tema 3),
> no un campo que exija el motor: `items_load()` de abajo no valida el JSON contra un esquema,
> así que un ítem que no lo declare simplemente pesa 0 en `inventory_peso_total()` (§5.2) —
> no hace falta añadirlo a todo tu catálogo de golpe, solo a lo que quieras que pese.

```gml
// ---------------------------------------------------------------------------
// scr_items — carga del catálogo
// ---------------------------------------------------------------------------

/// @func items_load()
/// @desc Carga items.json y construye un mapa id → definición.
function items_load()
{
    global.items = {};
    global.items_array = [];

    if (!file_exists("items.json"))
    {
        show_debug_message("ERROR: no se encuentra items.json");
        return;
    }

    var _f = file_text_open_read("items.json");
    var _json = "";
    while (!file_text_eof(_f))
    {
        _json += file_text_read_string(_f);
        file_text_readln(_f);
    }
    file_text_close(_f);

    var _data = json_parse(_json);

    var _len = array_length(_data);
    for (var _i = 0; _i < _len; _i++)
    {
        var _item = _data[_i];
        global.items[$ _item.id] = _item;
        array_push(global.items_array, _item);
    }

    show_debug_message("Objetos cargados: " + string(_len));
}

/// @func item_get_def(_item_id)
function item_get_def(_item_id)
{
    if (!variable_struct_exists(global.items, _item_id)) return undefined;
    return global.items[$ _item_id];
}
```

> **Recuerda registrar los archivos incluidos:** todo archivo en `datafiles/`
> debe aparecer en el `.yyp` del proyecto, o `file_exists()` devolverá `false`
> en el juego exportado.

### 5.4 Diálogos ramificados

```gml
// ---------------------------------------------------------------------------
// scr_dialogue
// ---------------------------------------------------------------------------

/// @func DialogueRunner(_grafo)
/// @desc Recorre un grafo de nodos de diálogo.
///       _grafo es un struct: { id_nodo: { speaker, portrait, text, choices } }
function DialogueRunner(_grafo) constructor
{
    grafo     = _grafo;
    nodo_actual = "";
    finalizado  = false;

    /// @desc Empieza por un nodo concreto.
    start = function(_nodo_id)
    {
        nodo_actual = _nodo_id;
        finalizado  = false;
    };

    /// @desc Nodo actual, o undefined si el diálogo terminó.
    current = function()
    {
        if (finalizado) return undefined;
        if (!variable_struct_exists(grafo, nodo_actual))
        {
            finalizado = true;
            return undefined;
        }
        return grafo[$ nodo_actual];
    };

    /// @desc Opciones VISIBLES del nodo actual (con condiciones evaluadas).
    choices = function()
    {
        var _n = current();
        if (_n == undefined) return [];
        if (!variable_struct_exists(_n, "choices")) return [];

        var _out = [];
        var _raw = _n.choices;

        for (var _i = 0; _i < array_length(_raw); _i++)
        {
            var _c = _raw[_i];

            // Evaluar condición si existe
            if (variable_struct_exists(_c, "condition"))
            {
                if (!_c.condition()) continue;
            }
            array_push(_out, _c);
        }
        return _out;
    };

    /// @desc Elige la opción _indice (dentro de las visibles).
    select = function(_indice)
    {
        var _opciones = choices();
        if (_indice < 0 || _indice >= array_length(_opciones)) return false;

        var _c = _opciones[_indice];

        // Ejecutar acción si la hay
        if (variable_struct_exists(_c, "action")) _c.action();

        if (variable_struct_exists(_c, "next") && _c.next != "")
        {
            nodo_actual = _c.next;
        }
        else
        {
            finalizado = true;
        }
        return true;
    };

    /// @desc Avanza (para nodos sin opciones, tipo visual novel).
    advance = function()
    {
        var _n = current();
        if (_n == undefined) return false;

        if (variable_struct_exists(_n, "next") && _n.next != "")
        {
            nodo_actual = _n.next;
            return true;
        }
        finalizado = true;
        return false;
    };
}
```

Ejemplo de grafo (puede vivir en JSON y cargarse con `json_parse`):

```gml
global.dialogo_posadero = {
    inicio: {
        speaker: "Posadero",
        portrait: sprPosadero,
        text: "¡Bienvenido! ¿Qué vas a tomar?",
        choices: [
            { text: "Una cerveza (10 oros)",
              next: "cerveza",
              condition: function() { return global.inventory.oro >= 10; },
              action:  function()
              {
                  global.inventory.oro -= 10;
                  global.player_stats.hp = global.player_stats.hp_max;
              } },
            { text: "¿Sabes algo de la mazmorra?", next: "mazmorra" },
            { text: "Nada, gracias.", next: "" }
        ]
    },
    cerveza: {
        speaker: "Posadero",
        portrait: sprPosadero,
        text: "¡Ahí va! Te veías con mal color.",
        next: "inicio"
    },
    mazmorra: {
        speaker: "Posadero",
        portrait: sprPosadero,
        text: "No vayas. El último que entró no volvió...",
        action: function() { global.flags.sabe_mazmorra = true; },
        next: "inicio"
    }
};
```

### 5.5 Caja de diálogo con efecto de máquina de escribir

```gml
// ---------------------------------------------------------------------------
// objDialogue — Create
// ---------------------------------------------------------------------------
runner        = noone;
texto_mostrado = "";
char_index    = 0;
char_speed    = 0.75;          // caracteres por frame
nodo          = undefined;
opcion_sel    = 0;
depth         = -9000;
```

```gml
// ---------------------------------------------------------------------------
// objDialogue — Step
// ---------------------------------------------------------------------------
if (runner == noone) exit;

var _n = runner.current();
if (_n == undefined)
{
    instance_destroy();
    exit;
}

// ¿Cambió de nodo? Reiniciar el "typing"
if (nodo != _n)
{
    nodo           = _n;
    texto_mostrado = "";
    char_index     = 0;
    opcion_sel     = 0;
}

// Efecto de máquina de escribir
if (char_index < string_length(nodo.text))
{
    char_index    += char_speed;
    texto_mostrado = string_copy(nodo.text, 1, floor(char_index));

    // Sonido de tecla cada 3 caracteres
    if (floor(char_index) mod 3 == 0 && char_speed > 0)
    {
        audio_play_sound(sndBlip, 5, false);
    }
}
else
{
    texto_mostrado = nodo.text;
}

// Navegación de opciones
var _opciones = runner.choices();
if (array_length(_opciones) > 0 && char_index >= string_length(nodo.text))
{
    if (keyboard_check_pressed(vk_down)) opcion_sel++;
    if (keyboard_check_pressed(vk_up))   opcion_sel--;
    opcion_sel = (opcion_sel + array_length(_opciones)) mod array_length(_opciones);
}

// Confirmar
if (keyboard_check_pressed(vk_space) || keyboard_check_pressed(ord("Z")))
{
    if (char_index < string_length(nodo.text))
    {
        char_index = string_length(nodo.text);   // saltar el typing
    }
    else if (array_length(_opciones) > 0)
    {
        runner.select(opcion_sel);
    }
    else
    {
        runner.advance();
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objDialogue — Draw GUI
// ---------------------------------------------------------------------------
if (runner == noone || nodo == undefined) exit;

var _gw = display_get_gui_width();
var _gh = display_get_gui_height();
var _box_h = 110;
var _box_y = _gh - _box_h - 12;

// Caja
draw_set_alpha(0.90);
draw_set_color(c_black);
draw_rectangle(12, _box_y, _gw - 12, _box_y + _box_h, false);
draw_set_alpha(1);
draw_set_color(c_white);
draw_rectangle(12, _box_y, _gw - 12, _box_y + _box_h, true);

// Retrato
if (variable_struct_exists(nodo, "portrait"))
{
    draw_sprite(nodo.portrait, 0, 30, _box_y + 10);
}

// Nombre
draw_set_font(fntName);
draw_set_color(c_yellow);
draw_text(90, _box_y + 12, nodo.speaker + ":");

// Texto
draw_set_font(fntDialogue);
draw_set_color(c_white);
draw_text_ext(90, _box_y + 38, texto_mostrado, 20, _gw - 130);

// Opciones (solo cuando el texto terminó)
if (char_index >= string_length(nodo.text))
{
    var _opciones = runner.choices();
    for (var _i = 0; _i < array_length(_opciones); _i++)
    {
        var _y = _box_y + 14 + (_i * 22);
        var _sel = (_i == opcion_sel);

        if (_sel) draw_text(110, _y, "> " + _opciones[_i].text);
        else      draw_text(118, _y, _opciones[_i].text);
    }
}
```

### 5.6 Combate por turnos

> 👉 Esto es el **mínimo viable**: siempre ataca a `enemigos[0]`, sin selección de objetivo, sin
> habilidades ni efectos de estado, sin dibujar el menú. El sistema completo — orden de turnos
> por iniciativa y por ATB con la cola visible, selección de objetivo con cursor, habilidades y
> hechizos con coste enganchados al motor de daño y estados de
> [04 · 32](./32%20-%20Sistema%20de%20daño%20y%20efectos%20de%20estado.md), el menú de batalla
> completo (comando → submenú → objetivo → confirmación → retroceso) y la mitad táctica en
> rejilla (movimiento por coste, línea de tiro, terreno y altura) — vive en
> [04 · 35 — Combate por turnos y táctico en rejilla](./35%20-%20Combate%20por%20turnos%20y%20táctico%20en%20rejilla.md).
> **No uses las dos a la vez:** ambas declaran `enum BattleState` y `objBattleManager` — en
> cuanto adoptes `04 · 35`, borra el `enum BattleState` de aquí (GameMaker no permite dos con el
> mismo nombre) y sustituye este `objBattleManager` por el suyo.

```gml
// ---------------------------------------------------------------------------
// objBattleManager — Create
// ---------------------------------------------------------------------------
enum BattleState { intro, player_turn, enemy_turn, resolving, victory, defeat }

state       = BattleState.intro;
state_timer = 0;

enemigos   = [];
acciones_pendientes = [];
indice_accion = 0;

menu_index   = 0;
menu_options = ["Atacar", "Objeto", "Defender", "Huir"];

// ---------------------------------------------------------------------------
// objBattleManager — Step
// ---------------------------------------------------------------------------
state_timer++;

switch (state)
{
    case BattleState.intro:
        if (state_timer > 40) set_state(BattleState.player_turn);
        break;

    case BattleState.player_turn:
        // Navegar el menú
        if (keyboard_check_pressed(vk_down)) menu_index = (menu_index + 1) mod 4;
        if (keyboard_check_pressed(vk_up))   menu_index = (menu_index + 3) mod 4;

        if (keyboard_check_pressed(vk_space) || keyboard_check_pressed(ord("Z")))
        {
            ejecutar_accion_jugador(menu_index);
        }
        break;

    case BattleState.enemy_turn:
        // Las acciones enemigas se encolaron al entrar en este estado
        if (indice_accion >= array_length(acciones_pendientes))
        {
            set_state(BattleState.player_turn);
            break;
        }

        if (state_timer > 40)   // pausa dramática entre golpes
        {
            resolver_accion(acciones_pendientes[indice_accion]);
            indice_accion++;
            state_timer = 0;
        }
        break;

    case BattleState.victory:
        if (state_timer > 90)
        {
            // Repartir experiencia y volver al mapa
            var _xp = 0;
            for (var _i = 0; _i < array_length(enemigos); _i++)
            {
                _xp += enemigos[_i].xp_value;
            }
            global.progression.add_xp(_xp);
            room_goto(global.return_room);
        }
        break;

    case BattleState.defeat:
        if (state_timer > 90) room_goto(rm_game_over);
        break;
}

// ---------------------------------------------------------------------------
// objBattleManager — lógica
// ---------------------------------------------------------------------------

function set_state(_nuevo)
{
    state       = _nuevo;
    state_timer = 0;

    if (_nuevo == BattleState.enemy_turn)
    {
        // Encolar las acciones de todos los enemigos vivos
        acciones_pendientes = [];
        indice_accion = 0;

        for (var _i = 0; _i < array_length(enemigos); _i++)
        {
            var _e = enemigos[_i];
            if (_e == noone || !instance_exists(_e)) continue;

            array_push(acciones_pendientes, {
                tipo:   "atacar",
                origen: _e,
                objetivo: objPlayer
            });
        }
        // Si no quedan enemigos, victoria
        if (array_length(acciones_pendientes) == 0) set_state(BattleState.victory);
    }
}

function ejecutar_accion_jugador(_indice)
{
    switch (_indice)
    {
        case 0:   // Atacar
            var _objetivo = enemigos[0];
            if (_objetivo == noone || !instance_exists(_objetivo))
            {
                set_state(BattleState.victory);
                return;
            }

            var _dano = global.player_stats.calcular_dano(
                global.player_stats, _objetivo.stats);

            _objetivo.stats.hp -= _dano;
            hit_complete(_objetivo, _dano, 0);

            if (_objetivo.stats.hp <= 0)
            {
                instance_destroy(_objetivo);
                comprobar_fin();
                return;
            }
            break;

        case 1:   // Objeto
            if (global.inventory.has("potion"))
            {
                global.inventory.remove("potion", 1);
                global.player_stats.hp = min(
                    global.player_stats.hp + 50,
                    global.player_stats.hp_max);
            }
            break;

        case 2:   // Defender: reduce el daño recibido este turno
            global.player_stats.mods.defense += 10;
            break;

        case 3:   // Huir
            if (irandom(1) == 1) room_goto(global.return_room);
            break;
    }

    set_state(BattleState.enemy_turn);
}

function resolver_accion(_accion)
{
    if (_accion.tipo == "atacar")
    {
        if (!instance_exists(_accion.origen)) return;

        var _dano = _accion.origen.stats.calcular_dano(
            _accion.origen.stats, global.player_stats);

        global.player_stats.hp -= _dano;
        hit_complete(objPlayer, _dano, 0);

        if (global.player_stats.hp <= 0)
        {
            global.player_stats.hp = 0;
            set_state(BattleState.defeat);
        }
    }
}

function comprobar_fin()
{
    // ¿Queda algún enemigo vivo?
    var _vivos = 0;
    for (var _i = 0; _i < array_length(enemigos); _i++)
    {
        if (enemigos[_i] != noone && instance_exists(enemigos[_i])) _vivos++;
    }

    if (_vivos == 0) set_state(BattleState.victory);
}
```

### 5.7 Movimiento por rejilla con tilemap de colisión

```gml
// ---------------------------------------------------------------------------
// objPlayer — Create (movimiento por rejilla, estilo JRPG)
// ---------------------------------------------------------------------------
TILE = 32;
grid_x = x div TILE;
grid_y = y div TILE;

moviendo   = false;
tween_t    = 0;
duracion_mov = 12;      // frames por casilla
vel_paso   = 0.12;      // multiplicador: bajar al correr

var _lay = layer_get_id("Tiles_Collision");
tilemap_colision = layer_tilemap_get_id(_lay);
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step
// ---------------------------------------------------------------------------
if (moviendo)
{
    tween_t++;
    var _t = clamp(tween_t / duracion_mov, 0, 1);

    x = lerp(x_from, x_to, _t);
    y = lerp(y_from, y_to, _t);

    if (_t >= 1)
    {
        moviendo = false;
        grid_x = x div TILE;
        grid_y = y div TILE;

        // Encuentro aleatorio en hierba alta
        if (tile_es_hierba(x, y) && random(1) < 0.04)
        {
            iniciar_combate();
        }
    }
    exit;
}

// --- Input: una casilla por pulsación ---------------------------------------
var _dx = 0, _dy = 0;

if (keyboard_check(vk_left)  || keyboard_check(ord("A"))) _dx = -1;
else if (keyboard_check(vk_right) || keyboard_check(ord("D"))) _dx = 1;
else if (keyboard_check(vk_up)    || keyboard_check(ord("W"))) _dy = -1;
else if (keyboard_check(vk_down)  || keyboard_check(ord("S"))) _dy = 1;

// Correr con Shift
duracion_mov = keyboard_check(vk_shift) ? 6 : 12;

if (_dx != 0 || _dy != 0)
{
    var _nx = grid_x + _dx;
    var _ny = grid_y + _dy;

    if (!celda_solida(_nx, _ny))
    {
        x_from = x;  y_from = y;
        x_to   = _nx * TILE + (TILE * 0.5);
        y_to   = _ny * TILE + (TILE * 0.5);
        moviendo = true;
        tween_t  = 0;

        facing = (_dx != 0) ? _dx : facing;
    }
}
```

```gml
// ---------------------------------------------------------------------------
// scr_tilemap_helpers
// ---------------------------------------------------------------------------

/// @func celda_solida(_grid_x, _grid_y)
/// @desc Consulta el tilemap de colisión en coordenadas de rejilla.
function celda_solida(_grid_x, _grid_y)
{
    var _px = _grid_x * TILE + (TILE * 0.5);
    var _py = _grid_y * TILE + (TILE * 0.5);

    var _tile = tilemap_get_at_pixel(objPlayer.tilemap_colision, _px, _py);

    // tile 0 = vacío; cualquier otro = sólido
    return (_tile != 0);
}

/// @func tile_es_hierba(_x, _y)
function tile_es_hierba(_x, _y)
{
    var _lay = layer_get_id("Tiles_Encounters");
    if (_lay == -1) return false;

    var _map = layer_tilemap_get_id(_lay);
    return (tilemap_get_at_pixel(_map, _x, _y) != 0);
}
```

### 5.8 Save / load completo

> Usa el estándar de la biblioteca —
> [`scr_save_load.gml`](<../06 - Assets y Scripts/scr_save_load.gml>) — para el guardado en sí
> (escritura atómica, checksum, copias de seguridad rotativas, versión de esquema).
> **No redefinas `save_game`/`load_game`/`delete_save` ni `#macro SAVE_VERSION`**: ya existen ahí
> y los reutilizan [`13 · 06`](<../13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md>)
> (arquitectura de cualquier proyecto) y [`04 · 54`](./54%20-%20Metajuego%20transversal%20-%20logros%2C%20galer%C3%ADa%2C%20speedrun%20y%20espectador.md)
> (metajuego). Lo propio del RPG —qué structs entran en `_datos`, cómo se reconstruyen y la
> vuelta a la room guardada— vive en las funciones de abajo, que **extienden** el estándar en vez
> de duplicarlo.

```gml
// ---------------------------------------------------------------------------
// scr_rpg_save — construye/aplica el struct de datos del RPG y se lo entrega
// al estándar de la biblioteca (06/scr_save_load.gml). NO reimplementa
// escritura de archivo, checksum ni backups: eso ya está resuelto ahí.
// ---------------------------------------------------------------------------

#macro RPG_SLOT_PARTIDA "partida"   // un solo slot; usa otro nombre por hueco si añades varios

/// @func rpg_recolectar_datos()
/// @desc Junta todo el estado del RPG en un struct plano, listo para
///       save_game(). Si tu juego también guarda logros/PB (04 · 54), añade
///       esos campos a ESTE mismo struct antes de llamar a save_game(): una
///       sola llamada, un solo archivo por slot (ver 04 · 54 §2.4).
/// @returns {Struct}
function rpg_recolectar_datos()
{
    return {
        room_name:   room_get_name(room),
        player_x:    objPlayer.x,
        player_y:    objPlayer.y,

        stats:       global.player_stats.serialize(),
        progression: global.progression.serialize(),
        inventory:   global.inventory.serialize(),
        equipment:   global.equipment.serialize(),

        flags:       global.flags,
        quests:      global.quest_log.serialize(),
        defeated:    global.enemigos_derrotados,
        opened:      global.cofres_abiertos,
        playtime:    global.playtime_frames
    };
}

/// @func rpg_aplicar_datos(_data)
/// @desc Reconstruye el estado del juego a partir de un struct ya cargado
///       (con `load_game()` del estándar) y va a la room guardada.
/// @param {Struct} _data
function rpg_aplicar_datos(_data)
{
    global.player_stats = Stats.deserialize(_data.stats);
    global.progression  = Progression.deserialize(_data.progression);
    global.inventory    = Inventory.deserialize(_data.inventory);
    global.equipment    = Equipment.deserialize(_data.equipment);

    global.flags               = _data.flags;
    global.enemigos_derrotados = _data.defeated;
    global.cofres_abiertos     = _data.opened;
    global.playtime_frames     = _data.playtime;
    global.quest_log           = QuestLog.deserialize(_data.quests);

    global.player_stats.refresh();

    // Ir a la room guardada y colocar al jugador
    var _room = asset_get_index(_data.room_name);
    if (_room != -1)
    {
        global.pending_player_x = _data.player_x;
        global.pending_player_y = _data.player_y;
        room_goto(_room);
    }
}

/// @func rpg_guardar(_slot)
/// @desc Guarda la partida en el slot dado con el estándar `save_game()`
///       (scr_save_load.gml): escritura atómica, checksum y backup rotativo
///       ya resueltos ahí.
/// @param {String} _slot
/// @returns {Bool}
function rpg_guardar(_slot = RPG_SLOT_PARTIDA)
{
    var _ok = save_game(_slot, rpg_recolectar_datos());
    if (_ok)
    {
        show_debug_message("Partida guardada en '" + string(_slot) + "'.");
    }
    return _ok;
}

/// @func rpg_cargar(_slot)
/// @desc Carga el slot dado con `load_game()` del estándar (que ya aplica la
///       migración de esquema vía `global.save_migrar` si hace falta) y
///       reconstruye el estado del RPG. Devuelve true si tuvo éxito.
/// @param {String} _slot
/// @returns {Bool}
function rpg_cargar(_slot = RPG_SLOT_PARTIDA)
{
    var _data = load_game(_slot);
    if (!is_struct(_data))
    {
        show_debug_message("No hay partida guardada en '" + string(_slot) + "'.");
        return false;
    }

    rpg_aplicar_datos(_data);
    return true;
}

/// @func rpg_migrar_datos(_datos, _version_vieja)
/// @desc Hook de migración que espera el estándar: engánchalo con
///       `global.save_migrar = rpg_migrar_datos;` en el Create de objGame
///       (ver §6 más abajo). `load_game()` lo llama solo cuando la versión
///       guardada es más antigua que `SAVE_VERSION` (de scr_save_load.gml):
///       no hace falta comprobar la versión a mano ni redefinir el macro.
/// @param {Struct} _datos
/// @param {Real}   _version_vieja
/// @returns {Struct}
function rpg_migrar_datos(_datos, _version_vieja)
{
    // Ejemplo: una versión anterior de tu juego no guardaba "equipment"
    if (!variable_struct_exists(_datos, "equipment"))
    {
        _datos.equipment = { weapon: -1, armor: -1, accessory: -1 };
    }
    return _datos;
}

/// @func rpg_borrar_partida(_slot)
function rpg_borrar_partida(_slot = RPG_SLOT_PARTIDA)
{
    delete_save(_slot);
}
```

---

## 6. Gestión del estado del jugador

El estado completo del jugador, centralizado:

```gml
// ---------------------------------------------------------------------------
// objGame — Create (marcado como PERSISTENTE)
// ---------------------------------------------------------------------------

// Solo inicializar la primera vez
if (variable_global_exists("game_initialized")) exit;

global.game_initialized = true;

// --- Guardado: hook de migración que espera el estándar (scr_save_load.gml) ---
global.save_migrar = rpg_migrar_datos;      // §5.8 más arriba

// --- Sistemas ---
global.player_stats = new Stats(60, 12, 6, 10);
global.progression  = new Progression();
global.inventory    = new Inventory(24);
global.equipment    = new Equipment();

// --- Estado del mundo ---
global.flags = {};                  // eventos: flags.habla_con_rey = true
global.enemigos_derrotados = [];    // ids únicos de enemigos únicos
global.cofres_abiertos     = {};    // "rm_dungeon_01_chest2" = true
global.playtime_frames     = 0;

// --- Quests ---
global.quest_log = new QuestLog();

// --- Navegación ---
global.return_room = room;          // a qué room volver tras un combate
global.pending_player_x = -1;
global.pending_player_y = -1;

// --- Cargar catálogos ---
items_load();
quests_load();
```

### Quests

```gml
// ---------------------------------------------------------------------------
// scr_quests
// ---------------------------------------------------------------------------

/// @func QuestLog()
function QuestLog() constructor
{
    activas    = [];      // ids de misiones en curso
    completadas = {};     // id → true

    /// @desc Acepta una misión si no está ya activa ni completada.
    accept = function(_quest_id)
    {
        if (is_complete(_quest_id)) return false;
        if (is_active(_quest_id))   return false;

        array_push(activas, {
            id:       _quest_id,
            paso:     0,
            progreso: 0,
            objetivo: quest_get_objetivo(_quest_id, 0)
        });

        fx_quest_notification("Nueva misión: " + quest_get_nombre(_quest_id));
        return true;
    };

    is_active = function(_quest_id)
    {
        var _len = array_length(activas);
        for (var _i = 0; _i < _len; _i++)
        {
            if (activas[_i].id == _quest_id) return true;
        }
        return false;
    };

    is_complete = function(_quest_id)
    {
        return variable_struct_exists(completadas, _quest_id);
    };

    /// @desc Notifica que ocurrió un evento (matar, recoger, hablar).
    ///       Las misiones avanzan solas si el evento coincide con su paso.
    notify = function(_tipo_evento, _target_id, _cantidad)
    {
        _cantidad = (_cantidad == undefined) ? 1 : _cantidad;

        var _len = array_length(activas);
        for (var _i = 0; _i < _len; _i++)
        {
            var _q = activas[_i];
            var _paso = quest_get_paso(_q.id, _q.paso);
            if (_paso == undefined) continue;

            if (_paso.tipo == _tipo_evento && _paso.target == _target_id)
            {
                _q.progreso += _cantidad;

                if (_q.progreso >= _paso.cantidad)
                {
                    avanzar_paso(_q);
                }
            }
        }
    };

    avanzar_paso = function(_q)
    {
        _q.paso++;
        _q.progreso = 0;

        if (_q.paso >= quest_get_total_pasos(_q.id))
        {
            completar(_q.id);
        }
        else
        {
            _q.objetivo = quest_get_objetivo(_q.id, _q.paso);
            fx_quest_notification("Objetivo actualizado");
        }
    };

    completar = function(_quest_id)
    {
        completadas[$ _quest_id] = true;

        // Quitar de activas
        var _len = array_length(activas);
        for (var _i = _len - 1; _i >= 0; _i--)
        {
            if (activas[_i].id == _quest_id) array_delete(activas, _i, 1);
        }

        // Recompensas
        var _def = quest_get_def(_quest_id);
        if (_def != undefined && variable_struct_exists(_def, "rewards"))
        {
            var _r = _def.rewards;
            if (variable_struct_exists(_r, "xp"))   global.progression.add_xp(_r.xp);
            if (variable_struct_exists(_r, "oro"))  global.inventory.oro += _r.oro;
            if (variable_struct_exists(_r, "items"))
            {
                var _items = _r.items;
                var _keys = variable_struct_get_names(_items);
                for (var _k = 0; _k < array_length(_keys); _k++)
                {
                    global.inventory.add(_keys[_k], _items[$ _keys[_k]]);
                }
            }
        }

        fx_quest_notification("¡Misión completada!");
    };

    serialize = function()
    {
        return { activas: activas, completadas: completadas };
    };

    static deserialize = function(_d)
    {
        var _q = new QuestLog();
        _q.activas     = _d.activas;
        _q.completadas = _d.completadas;
        return _q;
    };
}
```

```gml
// Ejemplo de quest en JSON (datafiles/quests.json)
/*
{
  "ratos_bodega": {
    "nombre": "Ratas en la bodega",
    "pasos": [
      { "tipo": "matar",  "target": "rata_gigante", "cantidad": 5,
        "texto": "Mata 5 ratas gigantes" },
      { "tipo": "hablar", "target": "posadero", "cantidad": 1,
        "texto": "Vuelve con el posadero" }
    ],
    "rewards": { "xp": 150, "oro": 75, "items": { "potion": 3 } }
  }
}
*/
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Modificar la stat base al equipar | Al desequipar, la estadística queda mal para siempre | Base + suma de modificadores, recalculada |
| Inventario con IDs numéricos | Insertar un objeto nuevo rompe los saves antiguos | IDs de texto estables |
| Contenido hardcodeado en código | 50 objetos = 500 líneas imposibles de mantener | JSON + catálogo global |
| No registrar los archivos en el `.yyp` | Los JSON no se encuentran en el build exportado | Revisa el `.yyp` tras añadir `datafiles/` |
| Serializar structs CON métodos | Los métodos se pierden; el save carga roto | Método `serialize()` que devuelve un struct plano |
| Sin versión en el save | No puedes migrar; los jugadores pierden la partida | `SAVE_VERSION` (de `scr_save_load.gml`) + `global.save_migrar` (aquí, `rpg_migrar_datos()`) |
| Guardar IDs de instancia | Al recargar, apuntan a otra cosa o a nada | Guarda posiciones y tipos, no referencias |
| `json_parse` sobre JSON con comentarios | Falla en silencio o da undefined | Nada de comentarios en los JSON de datos |
| `variable_struct_exists` contra clave inexistente en save viejo | Crash al cargar | Comprueba siempre antes de leer |
| Curva de XP mal ajustada | Nivel 1→2 en 10 s, nivel 20→21 en 3 h | Revisa la tabla de XP antes de diseñar contenido |
| Diálogo escrito en `if`/`else` anidados | 3 personajes = infierno de mantenimiento | Grafo de nodos con structs |
| Combate por turnos sin estados | Los turnos se solapan y se resuelven dos veces | Máquina de estados estricta |
| No limpiar `objBattleManager` entre combates | Combates fantasma acumulados | Destrúyelo al salir de `rm_battle` |

---

## 8. Cómo escalarlo

1. **Habilidades y magia** — un array de skills con coste de MP, y un menú
   que las lista. Reutiliza el grafo de diálogo para el menú.
2. **Tienda** — reutiliza el inventario: dos `Inventory` (cliente y stock) y
   una UI de intercambio.
3. **Equipo con *set bonuses*** — si llevas 3 piezas del mismo set, bonus
   extra. Encaja en el sistema de modificadores.
4. **Mapa del mundo** — una room aparte con tiles a escala mayor y colisiones
   simplificadas; al entrar en un tile de ciudad, `room_goto()`.
5. **Transiciones entre rooms** — `objTransition` persistente con fade,
   guardando `global.pending_player_x/y` para colocar al jugador al entrar.
6. **Bestiario / diario de misiones** — UI Layers con Flex Panels (ver
   receta 13) alimentados desde structs.
7. **Localización** — como los textos viven en JSON, tener `items_es.json` e
   `items_en.json` es casi gratis.
8. **Autosave** — cada cambio de room, llama a `rpg_guardar()` en background.

**Cuándo pasar a otra receta:** cuando tu RPG tiene inventario, equipo,
diálogos ramificados y save/load, tienes la base para el roguelike (receta 05)
y el metroidvania (receta 06). De hecho, un metroidvania es un RPG con
plataformas.

---

## 9. Fuentes

- **Make Your Own Role-Playing Game** (serie oficial de 5 partes: movimiento y
  enemigos, combate en tiempo real **o** por turnos, subida de nivel y stats,
  cajas de diálogo, remate del juego; con proyectos descargables) —
  https://gamemaker.io/tutorials/how-to-make-an-rpg
- **Make A Sprawling Adventure Game** (tutorial oficial, GML Code) —
  https://gamemaker.io/tutorials/little-town-gamemaker-tutorial
- **Hero's Trail** (tutorial oficial de acción-aventura, GML Visual) —
  https://gamemaker.io/tutorials/heros-trail-dnd-2
- Manual oficial — Tilemap layers (`layer_tilemap_get_id`,
  `tilemap_get_at_pixel`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers.htm
- Manual oficial — `json_stringify` / `json_parse` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling/Encoding_And_Hashing.htm
- Manual oficial — `file_text_open_write`, `file_text_open_read`,
  `file_exists`, `game_save_id` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling/File_Handling.htm
- Manual oficial — Structs y `variable_struct_exists` /
  `variable_struct_get_names` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Structs.htm
- Manual oficial — `draw_text_ext`, `string_copy`, `string_length` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Text.htm
- Plantillas oficiales del IDE (New → Game → Template): Platformer, Card Game,
  Match 3, Tower Defence, Survivor, Arcade Shooter
