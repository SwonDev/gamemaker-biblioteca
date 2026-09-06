# 06 — Metroidvania

> **Dificultad:** avanzada
> Es el examen final de las recetas anteriores: plataformas (01) + estado
> persistente (04) + salas conectadas (05). Si las tres te salen, esta sale
> sola.

---

## 1. Visión general

Un metroidvania es un mundo **único, interconectado y cerrado**, donde el
progreso se mide en **habilidades que abren zonas**, no en niveles.

La estructura fundamental es el **gate**: un obstáculo que no puedes cruzar
hasta tener la habilidad X. Detrás del gate hay una zona nueva; en esa zona
nueva hay la habilidad Y; la habilidad Y abre un gate en la zona inicial. Ese
bucle cerrado es el corazón del género.

**La regla de diseño más importante:** cada habilidad nueva debe recontextualizar
el mundo que ya has recorrido. Si consigues el doble salto y no puedes volver
a ningún sitio que recuerdes, has desperdiciado la habilidad.

**Lo que define al género:**

- Un mapa continuo, no niveles sueltos.
- Habilidades = llaves (doble salto, dash, agarre, nadar, romper suelo).
- *Backtracking* gratificante: volver es rápido porque hay atajos.
- Guardado en puntos concretos (sala de guardado / *save rooms*).

**Referencias hechas en GameMaker:** *Hollow Knight* (Unity), pero en
GameMaker: *Timespinner*, *Ori* no; sí: *Axiom Verge* (hecho en un motor
propio del autor), *Chasm*, *Wonder Boy*, *Bloodstained: Curse of the Moon*.
GameMaker tiene una larga tradición de acción-aventura; el tutorial oficial
**Make A Sprawling Adventure Game** cubre exactamente esta estructura.

---

## 2. Arquitectura recomendada

### Rooms conectadas vs room gigante

| Enfoque | Ventaja | Inconveniente | Cuándo |
|---|---|---|---|
| **Muchas rooms con transiciones** | Fácil de editar, carga rápido | Hay que gestionar dónde apareces al entrar | **Recomendado para empezar** |
| **Una room gigante** | Continuidad total | Rooms de 20000×20000 px son imposibles de editar y lentas | Solo con *chunking* |

Usa el primer enfoque: cada pantalla es una room, y las transiciones son
objetos en los bordes.

### El identificador único de sala

Todo el metroidvania depende de poder nombrar cada sala:

```gml
global.room_id = "caverna_03";   // NO uses room_get_name(room) directamente
```

¿Por qué no `room_get_name()`? Porque si renombras la room en el IDE, todos
los saves se rompen. Usa un ID propio que no cambies nunca.

### Jerarquía de objetos

```
objPlayer
objSolid / objPlatform / objPlatformMoving   (de la receta 01)
objTransitionZone      (borde de pantalla → cambia de room)
objAbilityPickup       (otorga una habilidad)
objGate                (bloquea hasta tener la habilidad)
├─ objGateDoor         (puerta con llave)
├─ objGateBreakable    (se rompe con un golpe cargado)
└─ objGateSwitch       (interruptor que abre puertas a distancia)
objSavePoint
objEnemy / objBoss
objMinimap             (UI)
objWorldState          (persistente: TODO el estado del mundo)
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `WorldState` | Habilidades, puertas abiertas, cofres, jefes, salas visitadas |
| `RoomExit` | Un borde de salida: hacia qué room, en qué posición |
| `MinimapRoom` | Un rectángulo del minimapa con su estado (visitada/oscura) |

---

## 3. El bucle central (core loop)

```
┌─ Al entrar en una room ──────────────────────────────────┐
│ 1. Leer el ID de la room                                 │
│ 2. Restaurar el estado: ¿qué cofres ya se abrieron?      │
│    ¿qué puertas están abiertas? ¿qué enemigos únicos      │
│    ya murieron?                                          │
│ 3. Colocar al jugador en la entrada correcta             │
│ 4. Marcar la sala como visitada (para el minimapa)       │
└──────────────────────────────────────────────────────────┘
┌─ Step ───────────────────────────────────────────────────┐
│ 5. Plataformas: movimiento, salto, habilidades           │
│ 6. Comprobar triggers: ¿tocas un pickup? ¿un gate?       │
│ 7. Combate                                               │
│ 8. ¿Tocas un borde de transición? → cambiar de room      │
│ 9. Minimap: dibujar salas conocidas                      │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 Transiciones entre rooms

Cada borde de la pantalla es un `objTransitionZone`. Al tocarlo:

1. Guarda hacia qué room vas y con qué ID de entrada.
2. Haz fade a negro.
3. `room_goto()`.
4. En la nueva room, busca el `objSpawnPoint` con ese ID y coloca al jugador.

**El ID de entrada es lo que hace que funcione.** Sin él, entras siempre en el
mismo sitio y el mundo deja de tener sentido espacial.

### 4.2 Habilidades desbloqueables

Una habilidad es tres cosas a la vez:

1. **Una flag** (`can_double_jump = true`).
2. **Una mecánica** (el jugador puede saltar dos veces).
3. **Una llave** (el gate de doble salto se abre).

Guárdalas como un struct con claves de texto: así el save es legible y puedes
comprobarlas por nombre desde el editor de rooms.

### 4.3 Gates

Un gate es un objeto con una condición y un comportamiento al cumplirla.
La implementación más flexible:

```gml
gate = {
    requiere: "doble_salto",
    modo: "bloquea" | "abre" | "desaparece"
};
```

Si el jugador tiene la habilidad, el gate se abre. Si no, muestra un
indicador sutil ("aquí necesitas algo"). **Nunca digas "necesitas doble
salto"**: el jugador debe deducirlo. Eso es diseño, no código.

### 4.4 Estado del mundo

Todo lo que el jugador puede alterar permanente se guarda:

| Categoría | Ejemplo de clave |
|---|---|
| Habilidades | `"doble_salto"`, `"dash"`, `"agarre"` |
| Puertas abiertas | `"puerta_bosque_norte"` |
| Cofres abiertos | `"cofre_cueva_02_a"` |
| Enemigos únicos muertos | `"jefe_guardian"` |
| Interruptores activados | `"interruptor_templo_01"` |
| Salas visitadas | `"cueva_03"` |

La clave es **global y descriptiva**. `global.world.flags[$ "cofre_cueva_02_a"]`.

### 4.5 Minimap

El minimapa se construye con datos, no con capturas de pantalla:

- Cada sala tiene un rectángulo (x, y, w, h) en coordenadas del mapa.
- Se dibuja gris si está visitada, más oscuro si solo se conoce de oído,
  y no se dibuja si nunca se ha entrado.
- Las puertas se dibujan como líneas en los bordes compartidos.

Guarda esos rectángulos en un struct global indexado por ID de sala.

---

## 5. Código base

### 5.0 Estado del mundo

```gml
// ---------------------------------------------------------------------------
// scr_world_state
// ---------------------------------------------------------------------------

/// @func WorldState()
/// @desc TODO el estado persistente del mundo del metroidvania.
function WorldState() constructor
{
    // --- Habilidades del jugador ---
    habilidades = {
        doble_salto: false,
        dash:        false,
        agarre:      false,       // agarrarse a paredes
        nadar:       false,
        golpe_carga: false        // romper bloques
    };

    // --- Eventos del mundo (clave → true) ---
    flags = {};

    // --- Salas visitadas ---
    salas_visitadas = {};

    // --- Posición de guardado ---
    save_room   = "";
    save_x      = 0;
    save_y      = 0;
    save_hp     = 0;

    /// @desc ¿Tiene el jugador esta habilidad?
    tiene = function(_habilidad)
    {
        if (!variable_struct_exists(habilidades, _habilidad)) return false;
        return habilidades[$ _habilidad];
    };

    /// @desc Otorga una habilidad permanentemente.
    otorgar = function(_habilidad)
    {
        if (!variable_struct_exists(habilidades, _habilidad))
        {
            show_debug_message("Habilidad inexistente: " + _habilidad);
            return false;
        }

        habilidades[$ _habilidad] = true;
        flags[$ "hab_" + _habilidad] = true;

        // Feedback: el jugador debe SABER que tiene algo nuevo
        ability_unlock_fx(_habilidad);
        return true;
    };

    /// @desc Marca un evento del mundo como ocurrido.
    set_flag = function(_clave, _valor)
    {
        flags[$ _clave] = (_valor == undefined) ? true : _valor;
    };

    get_flag = function(_clave)
    {
        if (!variable_struct_exists(flags, _clave)) return false;
        return flags[$ _clave];
    };

    visitar_sala = function(_room_id)
    {
        salas_visitadas[$ _room_id] = true;
    };

    sala_conocida = function(_room_id)
    {
        return variable_struct_exists(salas_visitadas, _room_id);
    };

    /// @desc Guarda el punto de respawn.
    guardar_punto = function(_room_id, _x, _y, _hp)
    {
        save_room = _room_id;
        save_x    = _x;
        save_y    = _y;
        save_hp   = (_hp == undefined) ? global.player_stats.hp : _hp;

        save_to_disk();
    };

    serialize = function()
    {
        return {
            habilidades: habilidades,
            flags: flags,
            salas_visitadas: salas_visitadas,
            save_room: save_room,
            save_x: save_x,
            save_y: save_y,
            save_hp: save_hp
        };
    };

    static deserialize = function(_d)
    {
        var _w = new WorldState();

        // Copiar habilidad por habilidad: si añades una nueva, los saves
        // antiguos siguen cargando (las nuevas quedan en false).
        var _keys = variable_struct_get_names(_d.habilidades);
        for (var _i = 0; _i < array_length(_keys); _i++)
        {
            _w.habilidades[$ _keys[_i]] = _d.habilidades[$ _keys[_i]];
        }

        _w.flags           = _d.flags;
        _w.salas_visitadas = _d.salas_visitadas;
        _w.save_room       = _d.save_room;
        _w.save_x          = _d.save_x;
        _w.save_y          = _d.save_y;
        _w.save_hp         = _d.save_hp;

        return _w;
    };
}

/// @func save_to_disk()
function save_to_disk()
{
    var _data = {
        version: 1,
        world:   global.world.serialize(),
        stats:   global.player_stats.serialize()
    };

    // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
    // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
    // 14 - Persistencia y archivos.md §1.
    var _f = file_text_open_write(game_save_id + "mvsave.json");
    file_text_write_string(_f, json_stringify(_data));
    file_text_close(_f);
}

/// @func load_from_disk()
function load_from_disk()
{
    var _path = game_save_id + "mvsave.json";
    if (!file_exists(_path)) return false;

    var _f = file_text_open_read(_path);
    var _d = json_parse(file_text_read_string(_f));
    file_text_close(_f);

    global.world        = WorldState.deserialize(_d.world);
    global.player_stats = Stats.deserialize(_d.stats);

    return true;
}
```

### 5.1 Transiciones entre rooms

```gml
// ---------------------------------------------------------------------------
// objTransitionZone — Create
// ---------------------------------------------------------------------------
// Colocar en los bordes de la room. Variable de instancia (en el editor):
//   target_room   → room a la que va
//   target_entry  → ID del objSpawnPoint en la room destino
//   direction     → "left" | "right" | "up" | "down"

target_room  = rm_start;
target_entry = "default";
direction    = "right";
```

```gml
// ---------------------------------------------------------------------------
// objTransitionZone — Step
// ---------------------------------------------------------------------------
if (!instance_exists(objPlayer)) exit;
if (objPlayer.transicionando) exit;

if (place_meeting(x, y, objPlayer))
{
    objPlayer.transicionando = true;

    // Fade a negro y cambio de room
    objTransition.fade_out(function()
    {
        global.pending_entry = target_entry;
        room_goto(target_room);
    });
}
```

```gml
// ---------------------------------------------------------------------------
// objSpawnPoint — Create (colocar en cada entrada de cada room)
// ---------------------------------------------------------------------------
// Variable de instancia en el editor: entry_id
entry_id = "default";
visible  = false;
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Room Start  (se ejecuta al entrar en CUALQUIER room)
// ---------------------------------------------------------------------------
var _id_buscado = (global.pending_entry == "") ? "default" : global.pending_entry;

var _spawn = noone;
with (objSpawnPoint)
{
    if (entry_id == _id_buscado) { _spawn = id; break; }
}

// Si no se encuentra, usar el primero que haya
if (_spawn == noone)
{
    _spawn = instance_find(objSpawnPoint, 0);
}

if (_spawn != noone)
{
    x = _spawn.x;
    y = _spawn.y;
}

// Resetear variables de salto para no "aterrizar" con velocidad rara
vel_x = 0;
vel_y = 0;
transicionando = false;

// Registrar la sala como visitada
global.world.visitar_sala(global.room_id);

// Restaurar el estado de la sala (cofres, puertas, enemigos únicos)
room_apply_world_state();
```

### 5.2 Restaurar el estado de la sala al entrar

Esta es la función que hace que el mundo se sienta **persistente**: entrar en
una sala por segunda vez debe mostrar lo que dejaste.

```gml
// ---------------------------------------------------------------------------
// scr_room_state
// ---------------------------------------------------------------------------

/// @func room_apply_world_state()
/// @desc Aplica el estado guardado a TODOS los objetos de la sala actual.
function room_apply_world_state()
{
    var _room_id = global.room_id;

    // --- Cofres ya abiertos → destruirlos y dejarlos abiertos ----------------
    with (objChest)
    {
        var _clave = _room_id + "_cofre_" + string(chest_index);
        if (global.world.get_flag(_clave))
        {
            abierto = true;
            sprite_index = sprChestOpen;
        }
    }

    // --- Puertas ya abiertas --------------------------------------------------
    with (objGate)
    {
        var _clave = _room_id + "_puerta_" + string(gate_index);
        if (global.world.get_flag(_clave))
        {
            instance_destroy();
        }
    }

    // --- Enemigos únicos ya derrotados ----------------------------------------
    with (objEnemyUnique)
    {
        var _clave = "enemigo_" + unique_id;
        if (global.world.get_flag(_clave))
        {
            instance_destroy();
        }
    }

    // --- Interruptores ya activados -------------------------------------------
    with (objSwitch)
    {
        var _clave = _room_id + "_interruptor_" + string(switch_index);
        if (global.world.get_flag(_clave))
        {
            activado = true;
            image_index = 1;
        }
    }

    // --- Pickups ya recogidos --------------------------------------------------
    with (objAbilityPickup)
    {
        if (global.world.tiene(ability_id))
        {
            instance_destroy();
        }
    }
}
```

### 5.3 Pickups de habilidad

```gml
// ---------------------------------------------------------------------------
// objAbilityPickup — Create
// ---------------------------------------------------------------------------
// Variable de instancia en el editor: ability_id  ("doble_salto", "dash"...)
ability_id = "doble_salto";

// Efecto de flotar
bob_base_y = y;
bob_t = 0;
```

```gml
// ---------------------------------------------------------------------------
// objAbilityPickup — Step
// ---------------------------------------------------------------------------
bob_t += 0.05;
y = bob_base_y + sin(bob_t) * 3;

// Brillo pulsante
image_alpha = 0.8 + sin(bob_t * 2) * 0.2;

if (place_meeting(x, y, objPlayer))
{
    global.world.otorgar(ability_id);
    global.world.set_flag(_room_id_pickup_key());
    instance_destroy();
}

function _room_id_pickup_key()
{
    return global.room_id + "_pickup_" + ability_id;
}
```

```gml
// ---------------------------------------------------------------------------
// objAbilityPickup — Destroy (si no se recogió, guardar que sigue ahí)
// ---------------------------------------------------------------------------
// Nada: si no se recogió, el flag no se marca y volverá a aparecer. Correcto.
```

```gml
// ---------------------------------------------------------------------------
// scr_ability_unlock
// ---------------------------------------------------------------------------

/// @func ability_unlock_fx(_habilidad)
/// @desc Secuencia de desbloqueo: congela el juego, muestra la habilidad.
function ability_unlock_fx(_habilidad)
{
    // 1. Congelar el gameplay
    global.game_freeze = true;

    // 2. Time slow para la animación
    time_slow(0.25, 120);

    // 3. Zoom de cámara
    objCamera.cam_zoom_target = 1.6;

    // 4. Explosión de luz
    fx_explosion(objPlayer.x, objPlayer.y, 0.6);
    fx_flash(c_white, 0.7, 20);

    // 5. Partículas ascendentes
    part_particles_create(objFx.ps, objPlayer.x, objPlayer.y, objFx.pt_spark, 60);

    // 6. Sonido
    audio_play_sound(sndAbilityGet, 10, false);

    // 7. Mostrar el panel de habilidad y devolver el control
    with (instance_create_depth(0, 0, -10000, objAbilityPanel))
    {
        habilidad = _habilidad;
        on_close = function()
        {
            global.game_freeze = false;
            objCamera.cam_zoom_target = 1.0;
        };
    }
}
```

### 5.4 Habilidades en el jugador

```gml
// ---------------------------------------------------------------------------
// objPlayer — Create (añadidos del metroidvania)
// ---------------------------------------------------------------------------
jumps_left       = 0;
jumps_max        = 1;
dash_disponible  = false;
dash_timer       = 0;
dash_cooldown    = 0;
agarrado         = false;

// ---------------------------------------------------------------------------
// objPlayer — Step (habilidades, integrado con la receta 01)
// ---------------------------------------------------------------------------
// --- Leer habilidades del mundo -----------------------------------------------
jumps_max       = global.world.tiene("doble_salto") ? 2 : 1;
puede_dash      = global.world.tiene("dash");
puede_agarrar   = global.world.tiene("agarre");

// --- Resetear saltos al aterrizar ---------------------------------------------
if (on_ground)
{
    jumps_left = jumps_max;
    dash_disponible = puede_dash;
}

// --- Doble salto ---------------------------------------------------------------
if (buffer_timer > 0 && !on_ground && jumps_left > 0)
{
    vel_y = -JUMP_SPEED * 0.92;      // el segundo salto es algo más flojo
    jumps_left--;
    buffer_timer = 0;
    squash_preset(self, "jump");
    fx_dust_land(x, y + 8);
}

// --- Dash -----------------------------------------------------------------------
dash_cooldown--;
if (dash_cooldown < 0) dash_cooldown = 0;

if (keyboard_check_pressed(vk_shift) && puede_dash &&
    dash_disponible && dash_cooldown == 0)
{
    dash_timer      = 12;
    dash_disponible = false;
    dash_cooldown   = 30;

    // Dirección: hacia donde mira, o la última dirección pulsada
    var _ddir = (_input_x != 0) ? (_input_x > 0 ? 0 : 180)
                                : ((facing > 0) ? 0 : 180);

    vel_x = lengthdir_x(DASH_SPEED, _ddir);
    vel_y = 0;

    // Juice: rastro + shake suave
    squash_preset(self, "hit");
    camera_shake(0.12);
    audio_play_sound(sndDash, 8, false);
}

// Durante el dash: sin gravedad y con invulnerabilidad
if (dash_timer > 0)
{
    dash_timer--;
    invulnerable = true;

    // Rastro: dibujar el sprite con alfa cada 2 frames
    if (dash_timer mod 2 == 0)
    {
        with (instance_create_layer(x, y, "Effects", objAfterimage))
        {
            sprite_index = other.sprite_index;
            image_index  = other.image_index;
            image_xscale = other.image_xscale;
        }
    }
}
else if (dash_timer == 0)
{
    invulnerable = false;
}
```

```gml
// ---------------------------------------------------------------------------
// objAfterimage — Create / Step (rastro del dash)
// ---------------------------------------------------------------------------
// Create
image_alpha = 0.6;
life = 14;

// Step
image_alpha -= 0.045;
life--;
if (life <= 0 || image_alpha <= 0) instance_destroy();
```

### 5.5 Gates

```gml
// ---------------------------------------------------------------------------
// objGate — Create
// ---------------------------------------------------------------------------
// Variables de instancia (editor):
//   requiere     → "doble_salto" | "dash" | "llave_roja" | ...
//   modo         → "bloquea" (sólido hasta tenerla) | "desaparece"
//   gate_index   → número único dentro de la sala
requiere   = "doble_salto";
modo       = "bloquea";
gate_index = 0;

sprite_index = sprGateDefault;
```

```gml
// ---------------------------------------------------------------------------
// objGate — Step
// ---------------------------------------------------------------------------
var _clave = global.room_id + "_puerta_" + string(gate_index);

// Si ya se abrió antes, desaparecer (el código de entrada de sala ya lo
// destruyó, pero esto cubre el caso de abrirlo EN VIVO)
if (global.world.get_flag(_clave))
{
    instance_destroy();
    exit;
}

if (global.world.tiene(requiere) || global.world.get_flag(requiere))
{
    abrir();
}

// ---------------------------------------------------------------------------
// objGate — abrir()
// ---------------------------------------------------------------------------
function abrir()
{
    var _clave = global.room_id + "_puerta_" + string(gate_index);
    global.world.set_flag(_clave);

    if (modo == "desaparece")
    {
        // Animación de apertura y destrucción
        instance_create_layer(x, y, "Effects", objGateOpenFx);
        instance_destroy();
    }
    else
    {
        // Cambiar a sprite abierto y dejar de ser sólido
        sprite_index = sprGateOpen;
        solido = false;
    }

    camera_shake(0.25);
    audio_play_sound(sndGateOpen, 10, false);
    save_to_disk();      // autoguardado al abrir un camino nuevo
}
```

### 5.6 Puerta con llave

```gml
// ---------------------------------------------------------------------------
// objGateDoor — Collision con objPlayer
// ---------------------------------------------------------------------------
var _clave = global.room_id + "_puerta_" + string(gate_index);
if (global.world.get_flag(_clave)) exit;

// ¿Tiene el jugador la llave?
if (variable_struct_exists(global.player_keys, key_id) &&
    global.player_keys[$ key_id] > 0)
{
    global.player_keys[$ key_id]--;
    global.world.set_flag(_clave);
    instance_destroy();

    audio_play_sound(sndDoorUnlock, 10, false);
    fx_flash(c_white, 0.15, 6);
    save_to_disk();
}
else
{
    // Feedback: la puerta se sacude. NO digas "necesitas la llave roja";
    // el jugador debe deducirlo.
    x_offset_shake = 4;
}
```

### 5.7 Puntos de guardado

```gml
// ---------------------------------------------------------------------------
// objSavePoint — Create
// ---------------------------------------------------------------------------
sprite_index = sprSavePoint;
activo = false;
```

```gml
// ---------------------------------------------------------------------------
// objSavePoint — Step
// ---------------------------------------------------------------------------
if (place_meeting(x, y, objPlayer))
{
    if (!activo)
    {
        activo = true;
        image_index = 1;

        global.world.guardar_punto(global.room_id, x, y);
        global.player_stats.hp = global.player_stats.hp_max;   // curar

        // Feedback suave: un chasquido y un brillo
        audio_play_sound(sndSave, 10, false);
        fx_floating_text(x, y - 20, "Guardado", c_white);
        fx_flash(c_white, 0.10, 8);
    }
}
else if (activo && !place_meeting(x, y, objPlayer))
{
    activo = false;
    image_index = 0;
}
```

```gml
// ---------------------------------------------------------------------------
// scr_respawn
// ---------------------------------------------------------------------------

/// @func player_respawn()
/// @desc Devuelve al jugador al último punto de guardado.
function player_respawn()
{
    var _w = global.world;

    if (_w.save_room == "")
    {
        // Sin punto de guardado: reiniciar desde el inicio
        global.player_stats.hp = global.player_stats.hp_max;
        room_goto(rm_start);
        return;
    }

    global.player_stats.hp = max(1, _w.save_hp);
    global.pending_entry   = "default";

    var _room = asset_get_index(_w.save_room);
    if (_room != -1)
    {
        room_goto(_room);
    }
    else
    {
        show_debug_message("Room de guardado inexistente: " + _w.save_room);
        room_goto(rm_start);
    }
}
```

### 5.8 Minimap

```gml
// ---------------------------------------------------------------------------
// scr_minimap — definición del mapa (datos, no capturas)
// ---------------------------------------------------------------------------

/// @func minimap_init()
/// @desc Define las salas: posición y tamaño en coordenadas de mapa.
///       Las coordenadas son "celdas del mapa", no píxeles.
function minimap_init()
{
    global.minimap_rooms = {

        //                    x,  y,  w,  h
        caverna_inicio:  { x: 5, y: 8, w: 2, h: 1 },
        caverna_02:      { x: 7, y: 8, w: 1, h: 1 },
        caverna_03:      { x: 8, y: 8, w: 2, h: 2 },
        caverna_pozo:    { x: 8, y: 10, w: 1, h: 2 },
        bosque_01:       { x: 10, y: 7, w: 2, h: 1 },
        bosque_02:       { x: 12, y: 7, w: 1, h: 1 },
        templo_entrada:  { x: 13, y: 6, w: 2, h: 2 },
        templo_santuario:{ x: 15, y: 6, w: 1, h: 2 }
    };

    // Conexiones: para dibujar los pasillos entre salas
    global.minimap_links = [
        ["caverna_inicio", "caverna_02"],
        ["caverna_02", "caverna_03"],
        ["caverna_03", "caverna_pozo"],
        ["caverna_03", "bosque_01"],
        ["bosque_01", "bosque_02"],
        ["bosque_02", "templo_entrada"],
        ["templo_entrada", "templo_santuario"]
    ];
}
```

```gml
// ---------------------------------------------------------------------------
// objMinimap — Draw GUI
// ---------------------------------------------------------------------------
var _cell = 4;               // píxeles por celda del mapa
var _ox = 12;                // origen en pantalla
var _oy = 12;

var _salas = global.minimap_rooms;
var _nombres = variable_struct_get_names(_salas);

// --- Primero los enlaces (debajo de las salas) --------------------------------
draw_set_color(c_dkgray);
for (var _i = 0; _i < array_length(global.minimap_links); _i++)
{
    var _a = global.minimap_links[_i][0];
    var _b = global.minimap_links[_i][1];

    if (!global.world.sala_conocida(_a) || !global.world.sala_conocida(_b)) continue;

    var _ra = _salas[$ _a];
    var _rb = _salas[$ _b];

    draw_line(_ox + (_ra.x + _ra.w * 0.5) * _cell,
              _oy + (_ra.y + _ra.h * 0.5) * _cell,
              _ox + (_rb.x + _rb.w * 0.5) * _cell,
              _oy + (_rb.y + _rb.h * 0.5) * _cell);
}

// --- Después las salas ----------------------------------------------------------
for (var _i = 0; _i < array_length(_nombres); _i++)
{
    var _id = _nombres[_i];
    if (!global.world.sala_conocida(_id)) continue;

    var _r = _salas[$ _id];
    var _px = _ox + _r.x * _cell;
    var _py = _oy + _r.y * _cell;
    var _pw = _r.w * _cell;
    var _ph = _r.h * _cell;

    if (_id == global.room_id)
    {
        draw_set_color(c_yellow);      // sala actual
        draw_rectangle(_px, _py, _px + _pw, _py + _ph, false);
    }
    else
    {
        draw_set_color(c_gray);        // visitada
        draw_rectangle(_px, _py, _px + _pw, _py + _ph, false);
    }
}

draw_set_color(c_white);
```

---

## 6. Gestión del estado del jugador

```gml
// ---------------------------------------------------------------------------
// objWorldState — Create (PERSISTENTE, se crea una sola vez)
// ---------------------------------------------------------------------------
if (variable_global_exists("world_ready")) exit;

global.world_ready = true;

// --- Intentar cargar partida ---
if (!load_from_disk())
{
    global.world = new WorldState();
    global.player_stats = new Stats(80, 10, 5, 10);
    show_debug_message("Partida nueva creada.");
}
else
{
    show_debug_message("Partida cargada.");
}

global.player_keys = {};     // { llave_roja: 2, llave_azul: 0 }
global.pending_entry = "";
global.room_id = "";

minimap_init();
```

```gml
// ---------------------------------------------------------------------------
// objRoomMarker — Create  (UNO por room, invisible)
// ---------------------------------------------------------------------------
// Variable de instancia en el editor: room_identifier
global.room_id = room_identifier;
instance_destroy();     // no necesita seguir existiendo
```

> **Truco:** pon un `objRoomMarker` en cada room con la variable
> `room_identifier` rellenada en el editor. Es la forma más cómoda de dar un
> ID estable a cada sala sin depender del nombre del recurso.

```gml
// ---------------------------------------------------------------------------
// scr_mv_save — guardado manual / automático
// ---------------------------------------------------------------------------

/// @func mv_save_game(_slot)
function mv_save_game(_slot)
{
    _slot = (_slot == undefined) ? 0 : _slot;

    var _data = {
        version: 2,
        slot:    _slot,
        fecha:   date_datetime_string(date_current_datetime()),
        room_id: global.room_id,
        world:   global.world.serialize(),
        stats:   global.player_stats.serialize(),
        keys:    global.player_keys,
        playtime: global.playtime_frames
    };

    // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
    // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
    // 14 - Persistencia y archivos.md §1.
    var _f = file_text_open_write(game_save_id + "mv_slot" + string(_slot) + ".json");
    file_text_write_string(_f, json_stringify(_data, true));
    file_text_close(_f);

    return true;
}

/// @func mv_load_game(_slot)
function mv_load_game(_slot)
{
    _slot = (_slot == undefined) ? 0 : _slot;

    var _path = game_save_id + "mv_slot" + string(_slot) + ".json";
    if (!file_exists(_path)) return false;

    var _f = file_text_open_read(_path);
    var _d = json_parse(file_text_read_string(_f));
    file_text_close(_f);

    global.world        = WorldState.deserialize(_d.world);
    global.player_stats = Stats.deserialize(_d.stats);
    global.player_keys  = _d.keys;
    global.playtime_frames = _d.playtime;

    var _room = asset_get_index(_d.room_id);
    room_goto((_room != -1) ? _room : rm_start);

    return true;
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Usar `room_get_name(room)` como ID de sala | Renombrar una room en el IDE rompe todos los saves | ID propio estable (`objRoomMarker`) |
| Entrar siempre por el mismo sitio | El mundo pierde coherencia espacial | `objSpawnPoint` con `entry_id` y `global.pending_entry` |
| No restaurar el estado de la sala al volver | Los cofres reaparecen, los jefes reviven | `room_apply_world_state()` en Room Start |
| Guardar el estado solo al guardar la partida | Mueres y pierdes 20 minutos de progreso | Autoguardado en eventos clave (abrir puerta, recoger habilidad) |
| Transición sin protección de reentrada | Se dispara 30 veces durante el fade | Flag `transicionando` en el jugador |
| Habilidad que no abre nada | El jugador siente que no ha ganado nada | Cada habilidad debe abrir mínimo 2 zonas, una en terreno conocido |
| Gate que dice "necesitas doble salto" | Mata el descubrimiento | Solo feedback visual de "bloqueado" |
| Destruir el gate sin marcar el flag | Vuelve a aparecer cerrado al reentrar | `set_flag()` antes de `instance_destroy()` |
| Serializar `habilidades` como struct completo | Al añadir una habilidad nueva, los saves antiguos la ponen en `undefined` | Copiar clave por clave (ver `deserialize`) |
| Zoom de cámara sin restaurar | Tras el desbloqueo de habilidad te quedas con zoom 1.6 | `on_close` que devuelve `cam_zoom_target` a 1.0 |
| Minimap hardcodeado en coordenadas de píxel | Imposible de reordenar el mapa | Celdas del mapa + factor `_cell` |
| No guardar la posición del jugador al entrar en sala | Al morir reapareces lejísimos | `guardar_punto()` en cada `objSavePoint` |

---

## 8. Cómo escalarlo

1. **Más habilidades con mecánica real** — agarre a paredes, nado, transformación
   en algo pequeño, romper suelos con un golpe cargado.
2. **Atajos** — puertas de un solo sentido que conectan zonas lejanas. Es lo
   que convierte el *backtracking* de tedioso en rápido.
3. **Árbol de habilidades** — en vez de habilidades lineales, permite elegir
   orden. Multiplica la rejugabilidad.
4. **Sistema de mapa con anotaciones** — el jugador pone chinchetas en el
   minimapa (Hollow Knight lo hizo famoso).
5. **Salas de jefe con arena cerrada** — puertas que se cierran al entrar,
   como en la receta 03.
6. **Economía** — monedas de los enemigos + tienda en los puntos de guardado.
7. **Fast travel** — teletransporte entre puntos de guardado desbloqueable.
8. **New Game+** — conservas habilidades pero con enemigos más fuertes. Como
   el `WorldState` es un struct, es trivial: cámbiale los multiplicadores.

**Cuándo pasar a otra receta:** un metroidvania es, en la práctica, el
proyecto más completo que puedes hacer en 2D. Si llegas aquí y lo terminas,
ya no necesitas más recetas: necesitas terminar un juego.

---

## 9. Fuentes

- **Make A Sprawling Adventure Game** (tutorial oficial, GML Code) —
  https://gamemaker.io/tutorials/little-town-gamemaker-tutorial
- **Hero's Trail** (tutorial oficial de acción-aventura en GML Visual) —
  https://gamemaker.io/tutorials/heros-trail-dnd-2
- **Make Your First Platformer in GameMaker** (base de movimiento) —
  https://gamemaker.io/tutorials/your-first-platformer
- **How To Make Platformer Movement In GameMaker** —
  https://gamemaker.io/tutorials/easy-platformer
- Manual oficial — Rooms: `room_goto`, Room Start, `asset_get_index` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms.htm
- Manual oficial — `file_text_open_write` / `json_stringify` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling.htm
- Manual oficial — `variable_struct_get_names`, `variable_struct_exists` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions.htm
- Manual oficial — Cámaras (`camera_set_view_pos`, `camera_set_view_size`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Cameras_And_Display/Cameras_And_Viewports.htm
