# 03 — Shoot 'em up (shmup)

> **Dificultad:** básica‑media
> Es la receta que te enseña a **dirigir el juego desde datos**. Aquí dejas de
> escribir "si el contador llega a 100, spawnea un enemigo" y empiezas a
> escribir tablas de oleadas.

---

## 1. Visión general

Un shmup es un juego de **memoria y reconocimiento de patrones**. El jugador
aprende una coreografía: entra tal enemigo por la izquierda, hay un hueco en
la cortina de balas a los dos segundos. Tu trabajo como diseñador es que esa
coreografía sea legible.

**Lo que define al género:**

- La pantalla se mueve sola; el jugador se mueve dentro de ella.
- Todo lo que aparece debe ser **predecible** (mismo sitio, mismo momento).
- El juego se estructura en **oleadas** y **jefes**, no en niveles continuos.
- La *hitbox* del jugador es más pequeña que su sprite (perdona errores).

**Referencias hechas en GameMaker:** *Touhou* (la referencia absoluta del
género, hecha con un motor propio pero imitable en GM), *Ikaruga*,
*Hyper Light Drifter* no aplica; sí: *Freedom Star*, *Sine Mora*.

**Subgéneros:**

| Subgénero | Rasgo | Dificultad de implementar |
|---|---|---|
| *Vertical scrolling* (tate) | Scroll vertical, pantalla alta | Baja |
| *Horizontal scrolling* (yoko) | Scroll lateral | Baja |
| *Bullet hell* / danmaku | Cientos de balas, hitbox pequeña | Media |
| *Cute'em up* | Enemigos simpáticos, menos balas | Baja |
| *Run and gun* (Contra) | Plataformas + disparo | Alta (mezcla con receta 01) |

---

## 2. Arquitectura recomendada

### Jerarquía de objetos

```
objEnemyBase         (padre: hp, daño al morir, flash de impacto)
├── objEnemyGrunt    (enemigo básico: entra, dispara, sale)
├── objEnemyTurret   (estático, dispara en patrón)
├── objEnemyZigzag   (movimiento en S)
└── objBoss          (máquina de estados compleja)

objPlayer            (nave del jugador)
objBulletPlayer      (pool)
objBulletEnemy       (pool — pueden ser MILES)
objPowerUp
objWaveDirector      (lee la tabla de oleadas y spawnea)
objCamera            (scroll + shake)
objGame
```

### Rooms y capas

```
rm_stage_1
├── Background_Far    (layer_vspeed baja  → parallax lento)
├── Background_Near   (layer_vspeed alta  → parallax rápido)
├── Instances         (jugador, enemigos, balas)
└── UI                (HUD: vidas, bombas, puntuación)
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `WaveDef` | Una oleada: qué enemigos, dónde, cuándo, en qué formación |
| `SpawnEntry` | Una entrada individual de la oleada |
| `FormationDef` | Forma geométrica de entrada (línea, V, círculo) |
| `BossPhase` | Fase de un jefe: patrón, duración, vida hasta cambiar |
| `BulletPattern` | Generador de balas: anillo, espiral, abanico |

---

## 3. El bucle central (core loop)

```
┌─ Begin Step ─────────────────────────────────────────────┐
│ 1. Input del jugador + disparo automático                │
└──────────────────────────────────────────────────────────┘
┌─ Step ───────────────────────────────────────────────────┐
│ 2. Scroll: mover capas de fondo (layer_vspeed)           │
│ 3. objWaveDirector: avanzar el reloj de la oleada        │
│    → si toca, spawnear entradas pendientes               │
│ 4. Movimiento del jugador (con límites de pantalla)      │
│ 5. Actualizar enemigos (movimiento por path/ patrón)     │
│ 6. Actualizar TODAS las balas (pool activas)             │
│ 7. Colisiones: bala↔enemigo, bala↔jugador, cuerpo↔cuerpo │
│ 8. Resolver muertes: explosiones, drops, puntuación      │
│ 9. Comprobar fin de oleada → ¿siguiente? ¿jefe?          │
└──────────────────────────────────────────────────────────┘
┌─ End Step ───────────────────────────────────────────────┐
│ 10. Culling: desactivar lo que sale de pantalla          │
│ 11. Cámara: shake                                        │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 Scroll: dos enfoques

**A. La cámara se mueve** (mundo grande, cámara pequeña). Úsalo si el nivel
mide más de 10 pantallas.

```gml
// objCamera — Step
cam_y -= SCROLL_SPEED;
camera_set_view_pos(cam, camera_get_view_x(cam), cam_y);
```

**B. Las capas de fondo se mueven** (mundo del tamaño de la pantalla). Más
simple y más habitual en shmups clásicos.

```gml
// Create de objBackground
layer_vspeed(layer_get_id("Background_Far"),  0.5);
layer_vspeed(layer_get_id("Background_Near"), 2.0);
layer_hspeed(layer_get_id("Background_Far"),  0);
```

El parallax sale gratis: cada capa a su velocidad.

### 4.2 Oleadas dirigidas por datos

**El error clásico es escribir las oleadas en código.** En cuanto quieras
ajustar el ritmo, estarás editando lógica. Define las oleadas como structs:

```gml
wave = new WaveDef([
    new SpawnEntry(60,  objEnemyGrunt,  80,  -32, Formation.line_h, 5, 24),
    new SpawnEntry(120, objEnemyZigzag, 200, -32, Formation.line_v, 3, 28),
    new SpawnEntry(300, objEnemyTurret, 160, -32, Formation.arc,    5, 40)
]);
```

Ventajas inmediatas: puedes serializarlas a JSON, editarlas en una hoja de
cálculo, generarlas proceduralmente y hacer *replays*.

### 4.3 Formaciones

Una formación recibe (índice, total, x base, y base) y devuelve la posición
de ese miembro. Es una función pura: facilísima de testear.

### 4.4 Patrones de balas (danmaku)

Los tres patrones base con los que se construye casi todo:

| Patrón | Fórmula | Uso |
|---|---|---|
| **Anillo** | `dir = i * (360 / n) + offset` | Ataque radial, fácil de esquivar hacia fuera |
| **Abanico** | `dir = base - half + step * i` | Ataque dirigido al jugador |
| **Espiral** | `dir += incremento_cada_frame` | Presión constante, obliga a moverse |

El cuarto patrón, el que hace que un shmup se sienta "vivo", es la
**combinación temporizada**: un anillo cada 30 frames mientras la nave se
mueve en seno.

### 4.5 Object pooling: obligatorio

Un *bullet hell* puede tener 2000 balas simultáneas. Crear y destruir
instancias a ese ritmo provoca tirones de recolección de basura.

Dos reglas:

1. Pre-crea el pool al iniciar el nivel (500–2000 según el juego).
2. Nunca llames a `instance_destroy()` sobre una bala del pool.

Además: **desactiva** las balas fuera de pantalla en vez de destruirlas, y
vuelve a activarlas si la cámara retrocede.

```gml
// Culling barato en el End Step de objBulletEnemy
var _v = camera_get_view_y(view_camera[0]);
if (y > _v + camera_get_view_height(view_camera[0]) + 64) bullet_return();
```

### 4.6 Jefes con máquina de estados

Un jefe bueno tiene **fases**, y cada fase tiene **patrones con duración**. La
estructura mínima es:

```gml
BossPhase = {
    pattern:  funcion_patron,
    duration: 300,          // frames
    hp_threshold: 0.66      // cambia de fase al bajar de este % de vida
}
```

Cuando la vida cruza el umbral, el jefe hace una transición (explosión,
invulnerabilidad breve, cambio de paleta) y pasa a la siguiente fase. Esa
transición es lo que hace que el jugador *sienta* que está avanzando.

### 4.7 Patrones con hueco de seguridad

Un anillo de balas instantáneo y completo es matemáticamente imposible de
esquivar: la sección 7 de este documento ya lo marca como error clásico. Aquí
se formaliza la solución, y se cierran dos huecos más del mismo problema
(*bullet hell* avanzado): la bala que **muta a mitad de vuelo** y el
**patrón compuesto**.

**El hueco garantizado.** No basta con dejar un hueco fijo: si siempre está
en el mismo sitio (arriba, por ejemplo), el jugador aprende a plantarse ahí y
el patrón deja de suponer ningún reto. La solución barata es rotar el hueco
con el mismo `_offset` que ya usas para variar el anillo entre llamadas:

```gml
// ---------------------------------------------------------------------------
// scr_bullet_patterns — extensión con hueco garantizado
// ---------------------------------------------------------------------------

/// @func pattern_ring_con_hueco(_x, _y, _count, _speed, _offset, _hueco_deg, _sprite)
/// @desc Como pattern_ring (§5.5), pero deja un hueco de _hueco_deg grados
///       sin balas. El hueco vive entre (offset + cubre) y (offset + 360): si
///       _offset avanza en cada llamada, el hueco se desplaza y el jugador no
///       puede vivir siempre en el mismo sitio de la pantalla.
function pattern_ring_con_hueco(_x, _y, _count, _speed, _offset, _hueco_deg, _sprite)
{
    var _cubre = 360 - _hueco_deg;
    var _step  = _cubre / _count;

    for (var _i = 0; _i < _count; _i++)
    {
        bullet_enemy_spawn(_x, _y, _offset + (_i * _step), _speed, _sprite, 1);
    }
}
```

**La bala que muta a mitad de vuelo.** En vez de tocar el `objBulletEnemy`
base (§5.4), una función envoltorio añade el estado de mutación por encima
del pool: GameMaker permite crear variables de instancia nuevas en caliente,
así que no hace falta declarar nada en el `Create` del pool para que esto
funcione.

```gml
/// @func bullet_enemy_spawn_mutante(_x, _y, _dir, _speed, _sprite, _muta_en_frame)
/// @desc Envuelve bullet_enemy_spawn() (§5.4): la bala nace igual, pero a los
///       _muta_en_frame frames de vida gira hacia el jugador y acelera UNA
///       vez. Es la "curva de bala" que rompe la lectura de trayectoria recta.
function bullet_enemy_spawn_mutante(_x, _y, _dir, _speed, _sprite, _muta_en_frame)
{
    var _b = bullet_enemy_spawn(_x, _y, _dir, _speed, _sprite, 1);
    if (_b == noone) return noone;

    with (_b)
    {
        muta_en_frame = _muta_en_frame;
        ya_muto       = false;
        frames_vivida = 0;
    }
    return _b;
}
```

Esto exige un chequeo adicional al final del Step de `objBulletEnemy` (§5.4),
después de la comprobación de colisión con el jugador:

```gml
// ---------------------------------------------------------------------------
// objBulletEnemy — Step (añadir al final, tras la comprobación de colisión)
// ---------------------------------------------------------------------------
if (variable_instance_exists(id, "muta_en_frame"))
{
    frames_vivida++;

    if (!ya_muto && frames_vivida >= muta_en_frame)
    {
        ya_muto   = true;
        direction = point_direction(x, y, objPlayer.x, objPlayer.y);
        speed    *= 1.6;
    }
}
```

`variable_instance_exists()` evita tocar el `Create` del pool: una bala
normal nunca tiene `muta_en_frame` y este bloque no hace nada por ella.

**Patrón compuesto.** El cuarto ingrediente de A6 es combinar dos patrones ya
verificados en la misma llamada, con roles distintos — uno de presión
constante, otro dirigido:

```gml
// Anillo con hueco (presión constante, esquivable rodeando) + abanico
// dirigido (obliga a moverse en el momento exacto). Dos llamadas, cada una
// ya verificada por separado.
pattern_ring_con_hueco(x, y, 20, 2.2, _offset, 40, sprBulletEnemy);
pattern_aimed(x, y + 16, objPlayer.x, objPlayer.y, 3, 20, 3.4);
```

---

## 5. Código base

### 5.0 Constantes y enumeraciones

```gml
// ---------------------------------------------------------------------------
// scr_shmup_config
// ---------------------------------------------------------------------------
#macro PLAYER_SPEED      5.0
#macro PLAYER_FIRE_RATE  6      // frames entre disparos
#macro SCROLL_SPEED      2.0
#macro POOL_BULLET_ENEMY 1200
#macro POOL_BULLET_PLAYER 200

// Zonas "fuera de pantalla" para spawneo/desactivado
#macro SPAWN_MARGIN 48
#macro CULL_MARGIN  96
```

### 5.1 Formaciones

```gml
// ---------------------------------------------------------------------------
// scr_formations
// ---------------------------------------------------------------------------

/// @func Formation()
/// @desc Funciones puras: (indice, total, x, y) → {x, y}
function Formation() constructor
{
    /// Línea horizontal centrada en x
    static line_h = function(_i, _total, _x, _y, _spacing)
    {
        var _offset = (_i - (_total - 1) * 0.5) * _spacing;
        return { x: _x + _offset, y: _y };
    };

    /// Línea vertical escalonada en y
    static line_v = function(_i, _total, _x, _y, _spacing)
    {
        return { x: _x, y: _y - (_i * _spacing) };
    };

    /// Arco: los extremos más retrasados
    static arc = function(_i, _total, _x, _y, _spacing)
    {
        var _t     = (_total <= 1) ? 0.5 : (_i / (_total - 1));
        var _angle = lerp(-60, 60, _t);
        return { x: _x + lengthdir_x(_spacing * 2, _angle + 90),
                 y: _y - abs(lengthdir_y(_spacing, _angle)) };
    };

    /// V invertida (formación clásica de aviones)
    static vee = function(_i, _total, _x, _y, _spacing)
    {
        var _dist = abs(_i - (_total - 1) * 0.5);
        return { x: _x + (_i - (_total - 1) * 0.5) * _spacing,
                 y: _y - _dist * (_spacing * 0.6) };
    };

    /// Círculo completo
    static ring = function(_i, _total, _x, _y, _spacing)
    {
        var _angle = (_i / _total) * 360;
        var _r     = _spacing * 2;
        return { x: _x + lengthdir_x(_r, _angle),
                 y: _y + lengthdir_y(_r, _angle) };
    };
}

global.Formation = new Formation();
```

### 5.2 Definición de oleadas

```gml
// ---------------------------------------------------------------------------
// scr_waves
// ---------------------------------------------------------------------------

/// @func SpawnEntry(_frame, _obj, _x, _y, _formation, _count, _spacing)
function SpawnEntry(
    _frame, _obj, _x, _y, _formation, _count, _spacing
) constructor
{
    frame     = _frame;      // frame de la oleada en el que aparece
    obj       = _obj;        // índice de objeto a crear
    base_x    = _x;
    base_y    = _y;
    formation = _formation;  // función (i, total, x, y, spacing) → {x,y}
    count     = _count;
    spacing   = _spacing;
    spawned   = false;
}

/// @func WaveDef(_entries)
function WaveDef(_entries) constructor
{
    entries  = _entries;
    frame    = 0;
    finished = false;

    reset = function()
    {
        frame    = 0;
        finished = false;
        var _len = array_length(entries);
        for (var _i = 0; _i < _len; _i++) entries[_i].spawned = false;
    };

    /// @desc Avanza un frame y spawnea lo que toque.
    update = function()
    {
        frame++;

        var _len    = array_length(entries);
        var _all    = true;

        for (var _i = 0; _i < _len; _i++)
        {
            var _e = entries[_i];
            if (_e.spawned) continue;

            if (frame >= _e.frame)
            {
                spawn_formation(_e);
                _e.spawned = true;
            }
            _all = _all && _e.spawned;
        }

        finished = _all;
    };
}

/// @func spawn_formation(_entry)
/// @desc Instancia todos los miembros de una entrada de oleada.
function spawn_formation(_entry)
{
    for (var _i = 0; _i < _entry.count; _i++)
    {
        var _pos = _entry.formation(_i, _entry.count,
                                    _entry.base_x, _entry.base_y,
                                    _entry.spacing);

        instance_create_layer(_pos.x, _pos.y, "Instances", _entry.obj);
    }
}

/// @func wave_build_stage_01()
/// @desc Construye el array de oleadas del nivel 1.
function wave_build_stage_01()
{
    var _f = global.Formation;

    return [
        new WaveDef([
            new SpawnEntry(30,  objEnemyGrunt, 160, -40, _f.line_h, 5, 28),
            new SpawnEntry(120, objEnemyGrunt,  80, -40, _f.line_h, 4, 28)
        ]),
        new WaveDef([
            new SpawnEntry(40,  objEnemyZigzag, 240, -40, _f.line_v, 4, 34),
            new SpawnEntry(140, objEnemyZigzag,  80, -40, _f.line_v, 4, 34)
        ]),
        new WaveDef([
            new SpawnEntry(60, objEnemyTurret, 160, 60, _f.arc, 5, 32),
            new SpawnEntry(200, objEnemyGrunt, 160, -40, _f.vee, 7, 26)
        ])
    ];
}
```

### 5.3 `objWaveDirector`

```gml
// ---------------------------------------------------------------------------
// objWaveDirector — Create
// ---------------------------------------------------------------------------
waves      = wave_build_stage_01();
wave_index = 0;
wave       = waves[wave_index];
wave.reset();

state = "running";       // "running" | "clearing" | "boss" | "stage_clear"
clear_delay = 0;
```

```gml
// ---------------------------------------------------------------------------
// objWaveDirector — Step
// ---------------------------------------------------------------------------
switch (state)
{
    case "running":
        wave.update();

        if (wave.finished && instance_number(objEnemyBase) == 0)
        {
            clear_delay = 90;
            state = "clearing";
        }
        break;

    case "clearing":
        clear_delay--;
        if (clear_delay <= 0)
        {
            wave_index++;
            if (wave_index >= array_length(waves))
            {
                // Fin de oleadas: aparece el jefe
                state = "boss";
                instance_create_layer(160, -80, "Instances", objBoss);
            }
            else
            {
                wave = waves[wave_index];
                wave.reset();
                state = "running";
            }
        }
        break;

    case "boss":
        if (!instance_exists(objBoss))
        {
            state = "stage_clear";
        }
        break;

    case "stage_clear":
        // Aquí: pantalla de resultados, siguiente nivel...
        break;
}
```

### 5.4 Pool de balas enemigas

```gml
// ---------------------------------------------------------------------------
// scr_bullet_pool_enemy
// ---------------------------------------------------------------------------

/// @func bullet_enemy_init()
function bullet_enemy_init()
{
    global.pool_enemy = array_create(POOL_BULLET_ENEMY);

    for (var _i = 0; _i < POOL_BULLET_ENEMY; _i++)
    {
        var _b = instance_create_layer(-100, -100, "Instances", objBulletEnemy);
        _b.active = false;
        _b.visible = false;
        global.pool_enemy[_i] = _b;
    }
    global.pool_enemy_cursor = 0;
}

/// @func bullet_enemy_spawn(_x, _y, _dir, _speed, _sprite, _damage)
/// @desc Activa la siguiente bala libre del pool (búsqueda circular).
function bullet_enemy_spawn(_x, _y, _dir, _speed, _sprite, _damage)
{
    var _pool = global.pool_enemy;
    var _len  = array_length(_pool);

    // Búsqueda circular desde el último cursor: O(1) amortizado
    for (var _tries = 0; _tries < _len; _tries++)
    {
        global.pool_enemy_cursor = (global.pool_enemy_cursor + 1) % _len;
        var _b = _pool[global.pool_enemy_cursor];

        if (_b != noone && instance_exists(_b) && !_b.active)
        {
            _b.active       = true;
            _b.visible      = true;
            _b.x            = _x;
            _b.y            = _y;
            _b.direction    = _dir;
            _b.speed        = _speed;
            _b.sprite_index = (_sprite == undefined) ? sprBulletEnemy : _sprite;
            _b.damage       = (_damage == undefined) ? 1 : _damage;
            _b.life_frames  = 600;
            _b.image_index  = 0;
            return _b;
        }
    }
    return noone;   // pool agotado
}

/// @func bullet_enemy_release(_bala)
function bullet_enemy_release(_bala)
{
    _bala.active   = false;
    _bala.visible  = false;
    _bala.speed    = 0;
    _bala.x        = -100;
    _bala.y        = -100;
}
```

```gml
// ---------------------------------------------------------------------------
// objBulletEnemy — Step
// ---------------------------------------------------------------------------
if (!active) exit;

life_frames--;
if (life_frames <= 0) { bullet_enemy_release(id); exit; }

// Culling: fuera de la vista → devolver al pool
var _cam = view_camera[0];
var _top = camera_get_view_y(_cam);
var _bot = _top + camera_get_view_height(_cam);
var _lft = camera_get_view_x(_cam);
var _rgt = _lft + camera_get_view_width(_cam);

if (y < _top - CULL_MARGIN || y > _bot + CULL_MARGIN ||
    x < _lft - CULL_MARGIN || x > _rgt + CULL_MARGIN)
{
    bullet_enemy_release(id);
    exit;
}

// Colisión con el jugador (hitbox más pequeña que el sprite: 6 px de radio)
if (point_in_circle(objPlayer.x, objPlayer.y, x, y, 6 + sprite_width * 0.5))
{
    objPlayer.take_hit(damage);
    bullet_enemy_release(id);
}
```

### 5.5 Patrones de balas

```gml
// ---------------------------------------------------------------------------
// scr_bullet_patterns
// ---------------------------------------------------------------------------

/// @func pattern_ring(_x, _y, _count, _speed, _offset, _sprite)
function pattern_ring(_x, _y, _count, _speed, _offset, _sprite)
{
    var _step = 360 / _count;
    for (var _i = 0; _i < _count; _i++)
    {
        bullet_enemy_spawn(_x, _y, _offset + (_i * _step), _speed, _sprite, 1);
    }
}

/// @func pattern_fan(_x, _y, _base_dir, _count, _spread, _speed, _sprite)
function pattern_fan(_x, _y, _base_dir, _count, _spread, _speed, _sprite)
{
    if (_count <= 1)
    {
        bullet_enemy_spawn(_x, _y, _base_dir, _speed, _sprite, 1);
        return;
    }

    var _half = _spread * 0.5;
    var _step = _spread / (_count - 1);

    for (var _i = 0; _i < _count; _i++)
    {
        bullet_enemy_spawn(_x, _y,
            _base_dir - _half + (_i * _step), _speed, _sprite, 1);
    }
}

/// @func pattern_spiral_step(_x, _y, _angle_ref, _arms, _speed, _sprite)
/// @desc Un "paso" de espiral. Llamar cada frame incrementando _angle_ref.
function pattern_spiral_step(_x, _y, _angle_ref, _arms, _speed, _sprite)
{
    var _step = 360 / _arms;
    for (var _i = 0; _i < _arms; _i++)
    {
        bullet_enemy_spawn(_x, _y, _angle_ref + (_i * _step), _speed, _sprite, 1);
    }
}

/// @func pattern_aimed(_x, _y, _target_x, _target_y, _count, _spread, _speed)
function pattern_aimed(_x, _y, _target_x, _target_y, _count, _spread, _speed)
{
    var _dir = point_direction(_x, _y, _target_x, _target_y);
    pattern_fan(_x, _y, _dir, _count, _spread, _speed, sprBulletEnemy);
}
```

### 5.6 Enemigo básico

```gml
// ---------------------------------------------------------------------------
// objEnemyBase — Create
// ---------------------------------------------------------------------------
hp        = 3;
score_value = 100;
hit_flash = 0;
drop_chance = 0.15;

// ---------------------------------------------------------------------------
// objEnemyBase — Step
// ---------------------------------------------------------------------------
if (hit_flash > 0) hit_flash--;

// Culling si sale por abajo (en un shmup, lo que se va se va)
if (y > camera_get_view_y(view_camera[0]) + camera_get_view_height(view_camera[0]) + CULL_MARGIN)
{
    instance_destroy();
    exit;
}

// ---------------------------------------------------------------------------
// objEnemyBase — colisión con bala del jugador (en objBulletPlayer)
// ---------------------------------------------------------------------------
// Se resuelve desde la bala (ver objBulletPlayer más abajo)

// ---------------------------------------------------------------------------
// objEnemyBase — Destroy
// ---------------------------------------------------------------------------
// Explosión + puntuación + drop
instance_create_layer(x, y, "Effects", objExplosion);
objGame.add_score(score_value);

if (random(1) < drop_chance)
{
    instance_create_layer(x, y, "Instances", objPowerUp);
}
```

> 💡 **`hit_flash` solo cuenta frames: hay que dibujarlo.** Las tres vías (shader con
> uniform, `image_blend` + `gpu_set_fog`, sprite blanco aditivo) están en
> [04 · 15 — Game feel y juice §5.6 bis](./15%20-%20Game%20feel%20y%20juice.md#56-bis--dibujar-el-hit_flash-las-tres-v%C3%ADas).
> Sin ese paso, la variable se decrementa y no se ve nada.

```gml
// ---------------------------------------------------------------------------
// objEnemyGrunt — Create
// ---------------------------------------------------------------------------
event_inherited();
hp = 3;
score_value = 100;
vel_y = 1.4;
fire_cooldown = 0;

// ---------------------------------------------------------------------------
// objEnemyGrunt — Step
// ---------------------------------------------------------------------------
event_inherited();

// Entra en pantalla y luego se desplaza en seno
y += vel_y;
if (y > 60) x += sin(current_time * 0.003) * 0.8;

fire_cooldown--;
if (fire_cooldown <= 0 && y > 0)
{
    fire_cooldown = 90 + irandom(60);
    pattern_aimed(x, y + 8, objPlayer.x, objPlayer.y, 1, 0, 3.2);
}
```

```gml
// ---------------------------------------------------------------------------
// objEnemyZigzag — Step
// ---------------------------------------------------------------------------
event_inherited();

y += 2.0;
x += lengthdir_x(2.4, 90 + sin(y * 0.05) * 70);
```

### 5.7 Jefe con fases

```gml
// ---------------------------------------------------------------------------
// objBoss — Create
// ---------------------------------------------------------------------------
hp     = 300;
hp_max = 300;

invulnerable = false;
hit_flash    = 0;

// Reloj de patrón
pattern_timer = 0;
spiral_angle  = 0;

// Posición de entrada
target_y = 80;

// --- Definición de fases ---
phases = [
    {   // Fase 1: anillos lentos + disparo dirigido
        hp_threshold: 1.00,
        duration:     0,      // 0 = hasta que baje de hp_threshold
        on_enter: function(_boss)
        {
            _boss.pattern_timer = 0;
        },
        on_update: function(_boss)
        {
            _boss.pattern_timer++;

            if (_boss.pattern_timer % 70 == 0)
            {
                pattern_ring(_boss.x, _boss.y, 18, 2.0, _boss.pattern_timer,
                             sprBulletEnemy);
            }
            if (_boss.pattern_timer % 130 == 0)
            {
                pattern_aimed(_boss.x, _boss.y + 16,
                              objPlayer.x, objPlayer.y, 5, 40, 3.0);
            }
        }
    },
    {   // Fase 2: espiral de 4 brazos
        hp_threshold: 0.66,
        duration:     0,
        on_enter: function(_boss)
        {
            _boss.pattern_timer = 0;
            _boss.spiral_angle  = 0;
        },
        on_update: function(_boss)
        {
            _boss.pattern_timer++;

            if (_boss.pattern_timer % 5 == 0)
            {
                _boss.spiral_angle += 11;
                pattern_spiral_step(_boss.x, _boss.y, _boss.spiral_angle,
                                    4, 2.6, sprBulletEnemy);
            }
        }
    },
    {   // Fase 3: desesperación — todo a la vez
        hp_threshold: 0.33,
        duration:     0,
        on_enter: function(_boss)
        {
            _boss.pattern_timer = 0;
        },
        on_update: function(_boss)
        {
            _boss.pattern_timer++;

            if (_boss.pattern_timer % 45 == 0)
            {
                pattern_ring(_boss.x, _boss.y, 24, 2.2, _boss.pattern_timer,
                             sprBulletEnemy);
            }
            if (_boss.pattern_timer % 7 == 0)
            {
                _boss.spiral_angle += 9;
                pattern_spiral_step(_boss.x, _boss.y, _boss.spiral_angle,
                                    3, 3.0, sprBulletEnemy);
            }
            if (_boss.pattern_timer % 100 == 0)
            {
                pattern_aimed(_boss.x, _boss.y + 16,
                              objPlayer.x, objPlayer.y, 9, 70, 3.4);
            }
        }
    }
];

phase_index = 0;
phases[phase_index].on_enter(self);
```

```gml
// ---------------------------------------------------------------------------
// objBoss — Step
// ---------------------------------------------------------------------------
if (hit_flash > 0) hit_flash--;

// Entrada en escena
y = lerp(y, target_y, 0.02);

// Movimiento lateral
x = 160 + sin(current_time * 0.001) * 90;

// --- Comprobar cambio de fase ---
var _ratio = hp / hp_max;
var _next  = phase_index + 1;

if (_next < array_length(phases) && _ratio <= phases[_next].hp_threshold)
{
    phase_index = _next;
    pattern_timer = 0;

    // Transición: invulnerable + shake + limpia las balas en pantalla
    invulnerable = true;
    objCamera.camera_shake(6, 20);
    with (objBulletEnemy) if (active) bullet_enemy_release(id);

    phases[phase_index].on_enter(self);

    // Volver vulnerable tras 40 frames
    alarm[0] = 40;
}

// --- Ejecutar la fase actual ---
phases[phase_index].on_update(self);
```

```gml
// ---------------------------------------------------------------------------
// objBoss — Alarm 0
// ---------------------------------------------------------------------------
invulnerable = false;
```

```gml
// ---------------------------------------------------------------------------
// objBoss — Destroy
// ---------------------------------------------------------------------------
// Explosión grande en cadena
repeat (12)
{
    with (instance_create_layer(
        x + irandom_range(-40, 40), y + irandom_range(-30, 30),
        "Effects", objExplosion))
    {
        delay = irandom(30);
    }
}
objCamera.camera_shake(10, 45);
objGame.add_score(10000);
with (objBulletEnemy) if (active) bullet_enemy_release(id);
```

### 5.8 Jugador

```gml
// ---------------------------------------------------------------------------
// objPlayer — Create
// ---------------------------------------------------------------------------
vel_x = 0;
vel_y = 0;
SPEED = PLAYER_SPEED;
fire_cooldown = 0;
power_level  = 1;     // 1..3 → más balas
lives        = 3;
bombs        = 2;
invuln_time  = 0;
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step
// ---------------------------------------------------------------------------
if (invuln_time > 0) invuln_time--;

// --- Input con normalización -----------------------------------------------
var _ix = keyboard_check(vk_right) - keyboard_check(vk_left);
var _iy = keyboard_check(vk_down)  - keyboard_check(vk_up);

var _mag = point_distance(0, 0, _ix, _iy);
if (_mag > 1) { _ix /= _mag; _iy /= _mag; }

vel_x = lerp(vel_x, _ix * SPEED, 0.35);
vel_y = lerp(vel_y, _iy * SPEED, 0.35);

x += vel_x;
y += vel_y;

// --- Limitar a la vista -----------------------------------------------------
var _cam = view_camera[0];
var _pad = 8;
x = clamp(x, camera_get_view_x(_cam) + _pad,
             camera_get_view_x(_cam) + camera_get_view_width(_cam) - _pad);
y = clamp(y, camera_get_view_y(_cam) + _pad,
             camera_get_view_y(_cam) + camera_get_view_height(_cam) - _pad);

// --- Disparo automático -----------------------------------------------------
fire_cooldown--;
if ((keyboard_check(vk_space) || keyboard_check(ord("Z"))) && fire_cooldown <= 0)
{
    fire_cooldown = PLAYER_FIRE_RATE;
    player_shoot();
}
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — disparo según nivel de poder
// ---------------------------------------------------------------------------
function player_shoot()
{
    switch (power_level)
    {
        case 1:
            bullet_player_spawn(x, y - 12, 270, 9, 1);
            break;

        case 2:
            bullet_player_spawn(x - 5, y - 12, 270, 9, 1);
            bullet_player_spawn(x + 5, y - 12, 270, 9, 1);
            break;

        case 3:
            bullet_player_spawn(x,      y - 14, 270, 10, 2);
            bullet_player_spawn(x - 7,  y - 10, 275, 9,  1);
            bullet_player_spawn(x + 7,  y - 10, 265, 9,  1);
            break;
    }
}

/// @func take_hit(_dano)
function take_hit(_dano)
{
    if (invuln_time > 0) return false;

    lives--;
    power_level = max(1, power_level - 1);
    invuln_time = 120;

    objCamera.camera_shake(6, 20);
    instance_create_layer(x, y, "Effects", objExplosion);

    // Limpia las balas cercanas (bomba de emergencia gratuita)
    with (objBulletEnemy)
    {
        if (active && point_distance(x, y, other.x, other.y) < 90)
        {
            bullet_enemy_release(id);
        }
    }

    if (lives <= 0)
    {
        instance_destroy();
        // game over
    }
    return true;
}
```

### 5.9 Bombas y *grazing*

Dos mecánicas que hoy solo viven como ideas sueltas en §8 "Cómo escalarlo": la
bomba como **recurso** (no solo la limpieza gratuita de balas cercanas que ya
hace `take_hit()` arriba) y el *grazing* — rozar una bala sin que llegue a
tocar la *hitbox* letal suma puntos. Es, en palabras de la propia receta, "la
mecánica que convierte un shmup difícil en un shmup adictivo".

**Grazing.** El jugador ya tiene una *hitbox* letal de 6 px de radio (§5.4).
El anillo de *grazing* es un segundo radio, más generoso, alrededor de esa
misma *hitbox*: cruzarlo sin llegar al letal cuenta como roce.

```gml
// ---------------------------------------------------------------------------
// scr_shmup_config — macros nuevas para grazing y bombas
// ---------------------------------------------------------------------------
#macro GRAZE_RING_PX          18   // anillo exterior a la hitbox letal
#macro GRAZE_SCORE_PER_HIT    10
#macro GRAZE_METER_MAX       100   // roces necesarios para ganar una bomba
#macro BOMB_MAX                5
#macro BOMB_INVULN_FRAMES     90
#macro BOMB_SCORE_PER_BULLET   5
```

```gml
// ---------------------------------------------------------------------------
// objBulletEnemy — Step (añadir junto a la comprobación de colisión letal,
// §5.4 — ANTES de bullet_enemy_release(), para no comprobar una bala ya
// devuelta al pool)
// ---------------------------------------------------------------------------
if (!variable_instance_exists(id, "en_grazing")) en_grazing = false;

var _radio_letal    = 6 + sprite_width * 0.5;
var _radio_grazing  = _radio_letal + GRAZE_RING_PX;
var _d_jugador      = point_distance(objPlayer.x, objPlayer.y, x, y);

if (_d_jugador > _radio_letal && _d_jugador <= _radio_grazing)
{
    if (!en_grazing)             // primera vez que entra en el anillo: UN roce
    {
        en_grazing = true;
        graze_registrar();
    }
}
else if (_d_jugador > _radio_grazing)
{
    en_grazing = false;          // ha salido del anillo: puede volver a rozar
}
```

> 💡 `en_grazing` se inicializa con `variable_instance_exists()` en vez de en
> el `Create` del pool (§5.4): así no hace falta tocar esa sección, y el pool
> sigue funcionando igual para quien no use *grazing*. El estado se
> "autolimpia" solo: al reciclarse, la bala reaparece lejos del jugador y el
> primer chequeo del frame siguiente ya la marca fuera del anillo.

```gml
// ---------------------------------------------------------------------------
// scr_shmup_bomb_y_grazing
// ---------------------------------------------------------------------------

/// @func bomb_otorgar(_cantidad)
/// @desc Añade bombas al stock del jugador, sin pasar de BOMB_MAX. Llamar
///       desde la colisión con un power-up de bomba, o desde el medidor de
///       grazing al llenarse (abajo).
function bomb_otorgar(_cantidad)
{
    objPlayer.bombs = min(objPlayer.bombs + _cantidad, BOMB_MAX);
}

/// @func graze_registrar()
/// @desc Registra un roce (bala en el anillo de grazing, no en el impacto
///       letal): suma puntos y alimenta el medidor que recompensa con una
///       bomba extra al llenarse. El contador vive en objGame, junto al
///       resto del estado de partida (§6).
function graze_registrar()
{
    if (!variable_instance_exists(objGame, "graze_count"))
    {
        objGame.graze_count = 0;
        objGame.graze_meter = 0;
    }

    objGame.graze_count++;
    objGame.graze_meter = min(objGame.graze_meter + 1, GRAZE_METER_MAX);
    objGame.add_score(GRAZE_SCORE_PER_HIT);

    if (objGame.graze_meter >= GRAZE_METER_MAX)
    {
        objGame.graze_meter = 0;
        bomb_otorgar(1);
    }
}

/// @func bomb_usar()
/// @desc Consume una bomba: invulnerabilidad temporal, limpia TODAS las
///       balas enemigas activas en pantalla convirtiéndolas en puntos, y deja
///       el camino libre para el flash de pantalla. false si no hay bombas.
function bomb_usar()
{
    if (objPlayer.bombs <= 0) return false;

    objPlayer.bombs--;
    objPlayer.invuln_time = max(objPlayer.invuln_time, BOMB_INVULN_FRAMES);

    var _convertidas = 0;
    with (objBulletEnemy)
    {
        if (active)
        {
            bullet_enemy_release(id);
            _convertidas++;
        }
    }

    objGame.add_score(_convertidas * BOMB_SCORE_PER_BULLET);
    objCamera.camera_shake(8, BOMB_INVULN_FRAMES);
    instance_create_layer(objPlayer.x, objPlayer.y, "Effects", objBombFlash);

    return true;
}
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step (añadir junto al disparo automático, §5.8)
// ---------------------------------------------------------------------------
if (keyboard_check_pressed(ord("X")))
{
    bomb_usar();
}
```

> ⚠️ **La invulnerabilidad de la bomba sale gratis.** `bomb_usar()` solo pone
> `invuln_time` al mínimo de `BOMB_INVULN_FRAMES`; `take_hit()` (§5.8) ya
> comprueba `invuln_time > 0` antes de restar una vida, así que no hace falta
> tocar esa función para que la invulnerabilidad de la bomba funcione.
> `objBombFlash` no está definido en esta receta: es un efecto de pantalla
> completa como `objExplosion`, con el mismo patrón de `delay` que ya usa la
> explosión del jefe (§5.7).

---

## 6. Gestión del estado del jugador

```gml
// ---------------------------------------------------------------------------
// scr_shmup_state
// ---------------------------------------------------------------------------

/// @func ShmupState()
/// @desc Progreso del jugador: vidas, poder, puntuación, high scores.
function ShmupState() constructor
{
    lives       = 3;
    bombs       = 2;
    power_level = 1;
    score       = 0;
    // La tabla de récords se guarda en disco (ver abajo)
    high_scores = [];       // array de { name, score, date }

    /// @desc Suma puntos respetando el multiplicador por nivel de poder.
    add_score = function(_points)
    {
        score += _points * power_level;
    };

    subir_poder = function()
    {
        power_level = min(3, power_level + 1);
    };

    /// @desc Guarda la puntuación si entra en el top 10.
    submit_score = function(_name)
    {
        array_push(high_scores, {
            name:  _name,
            score: score,
            date:  date_datetime_string(date_current_datetime())
        });

        array_sort(high_scores, function(_a, _b)
        {
            return (_a.score > _b.score) ? -1 : 1;
        });

        if (array_length(high_scores) > 10)
        {
            array_resize(high_scores, 10);
        }

        save_high_scores();
    };

    save_high_scores = function()
    {
        var _data = { scores: high_scores };
        var _json = json_stringify(_data);
        // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
        // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
        // 14 - Persistencia y archivos.md §1.
        var _f = file_text_open_write(game_save_id + "highscores.json");
        file_text_write_string(_f, _json);
        file_text_close(_f);
    };

    load_high_scores = function()
    {
        var _path = game_save_id + "highscores.json";
        if (!file_exists(_path)) return;

        var _f = file_text_open_read(_path);
        var _json = file_text_read_string(_f);
        file_text_close(_f);

        var _data = json_parse(_json);
        if (struct_exists(_data, "scores")) high_scores = _data.scores;
    };
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Escribir oleadas en código | Cada ajuste de ritmo obliga a tocar lógica | Structs `WaveDef` + `SpawnEntry` |
| `instance_destroy()` en balas del pool | Tirones de framerate y IDs muertos en el array | Devuelve siempre al pool |
| Pool demasiado pequeño | Las balas "no salen" en el pico de un jefe | Crece dinámicamente o dimensiona con margen (prueba la peor fase) |
| Sin *culling* de balas | 2000 balas actualizándose fuera de pantalla | Desactiva por bounds de cámara en el Step |
| *Hitbox* del jugador = sprite completo | El juego es imposible; el jugador no ve por qué muere | Círculo de 4‑6 px de radio en el centro de la nave |
| Patrones sin *telegraph* | El jugador siente que muere por azar | Antes de cada ataque: un frame de carga, un sonido, un cambio de color |
| Anillo de balas instantáneo sin huecos | Muerte inevitable | Deja un hueco (gap) en el anillo y ralentiza la velocidad |
| Spawnear enemigos dentro de la vista | Aparecen "de la nada" encima del jugador | Spawnea siempre fuera de la vista, con margen |
| Colisión de bala contra bala | Coste O(n²) brutal | No la implementes salvo que sea mecánica central (Ikaruga) |
| Json con structs que tienen métodos | `json_stringify()` ignora las funciones y pierdes datos | Serializa a un struct plano (ver `serialize()` de la receta 01) |
| Scroll con `layer_vspeed` y `room_height` infinito | El fondo se corta | Usa `draw_sprite_tiled()` en un Draw de fondo para scroll infinito |

---

## 8. Cómo escalarlo

1. **Más patrones** — añade *lasser* (rayo que avisa y luego dispara),
   balas que rebotan, balas que se aceleran, balas que se dividen.
2. **Editor de oleadas** — como las oleadas son structs, puedes serializarlas
   a JSON y construir una herramienta dentro del propio GameMaker con UI Layers
   (ver receta 13).
3. **Sistema de bombas** — `objBomb` que limpia la pantalla, hace daño masivo
   y deja invulnerabilidad breve.
4. **Grazing** — rozar balas (sin morir) suma puntos. Es la mecánica que
   convierte un shmup difícil en un shmup adictivo.
5. **Power-ups con significado** — "options" (naves satélite que disparan),
   escudo de 3 golpes, velocidad lenta al mantener shift.
6. **Múltiples rutas de nivel** — según la puntuación, vas a la ruta A o B.
7. **Modo *score attack*** — tabla de récords online (ver receta 14).
8. **Replays** — graba el input por frame y reprodúcelo. Como las oleadas son
   deterministas si fijas la semilla, sale casi gratis.

**Cuándo pasar a otra receta:** el patrón
"datos → director → spawner" que has aprendido aquí es exactamente el que
necesitas para el RPG (oleadas = encuentros), el roguelike (oleadas = salas) y
el tower defense (oleadas = waves). Ya lo tienes.

---

## 9. Fuentes

- **Make Your Own Arcade Space Shooter** (tutorial oficial, GML Code y GML Visual) —
  https://gamemaker.io/tutorials/make-arcade-space-shooter
- **How To Optimise Your Games** (tutorial oficial; cubre pooling y culling) —
  https://gamemaker.io/tutorials/how-to-optimise-your-games
- **Ultimate Guide To Collision Functions** (tutorial oficial) —
  https://gamemaker.io/tutorials/collision-functions
- Manual oficial — Funciones de capa (`layer_vspeed`, `layer_hspeed`, `layer_get_id`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/General_Layer_Functions.htm
- Manual oficial — `instance_number`, `instance_create_layer` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Instances.htm
- Manual oficial — `point_in_circle`, `point_distance`, `lengthdir_x` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions.htm
- Manual oficial — `json_stringify` / `json_parse` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/File_Handling/Encoding_And_Hashing.htm
- Manual oficial — `array_sort`, `array_resize`, `array_create` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm
