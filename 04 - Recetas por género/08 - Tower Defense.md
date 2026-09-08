# 08 — Tower Defense

> **Dificultad:** media
> Es la mejor receta para aprender **pathfinding** de verdad, y para entender
> por qué un algoritmo que funciona puede arruinar un juego si lo dejas
> demasiado expuesto.

---

## 1. Visión general

Un tower defense es un puzle de optimización con presión temporal: colocas
torres estáticas para destruir enemigos que recorren un camino fijo.

**Lo que define al género:**

- **El camino es el puzle.** Al colocar una torre puedes bloquear ruta, y si el
  juego lo permite, el jugador construye un laberinto (maze TD). Si no, el
  camino es fijo (fixed-path TD). Esa decisión define todo el diseño.
- **La economía es una decisión de diseño, no un número.** Cada euro gastado en
  una torre es un euro que no tienes para la siguiente oleada.
- **El conocimiento del jugador es la recompensa.** La primera partida pierdes;
  la tercera ya sabes qué torre va contra qué.

**Referencias hechas en GameMaker:** *Kingdom Rush* (Flash), *Bloons TD*,
*Defense Grid*, *BTD6*. GameMaker tiene una **plantilla oficial de Tower
Defence** (IDE → New → Game → Template) que cubre la estructura completa.

**Subgéneros:**

| Subgénero | Rasgo | Dificultad técnica |
|---|---|---|
| *Fixed path* | Camino fijo, torres en parcelas | Baja |
| *Maze / open field* | Las torres bloquean y crean el laberinto | Media (recalcular paths) |
| *Reverse TD* | Tú envías tropas contra torres | Alta |
| *Tower offense* | Torres móviles que avanzan | Media |

---

## 2. Arquitectura recomendada

### Jerarquía de objetos

```
objGrid                (controller: grid lógica, mp_grid, paths)
objTowerBase           (padre: coste, rango, cadencia, targeting)
├── objTowerArrow      (disparo simple, daño bajo)
├── objTowerCannon     (daño en área, cadencia lenta)
├── objTowerFrost      (ralentiza, no mata)
└── objTowerLaser      (daño continuo, cadencia rápida)
objEnemyBase           (padre: vida, velocidad, recompensa)
├── objEnemyFast
├── objEnemyTank
└── objEnemyBoss
objProjectile          (pool — ver receta 03)
objWaveManager         (oleadas desde structs)
objBuildManager        (colocación, preview, validación)
objEconomy             (oro, intereses, venta de torres)
```

### Capas

```
rm_td_01
├── Floor              (tilemap del terreno)
├── Path               (tilemap del camino)
├── Towers             (torres colocadas)
├── Enemies            (enemigos)
├── Projectiles
└── UI                 (HUD: oro, vidas, oleada, tienda)
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `TowerDef` | Definición de torre: coste, rango, daño, cadencia, tipo |
| `EnemyDef` | Definición de enemigo: vida, velocidad, recompensa, resistencias |
| `WaveDef` | Oleada: grupos de enemigos con tiempos |
| `PathResult` | Un camino calculado + su validez |

---

## 3. El bucle central (core loop)

```
┌─ Al colocar una torre ───────────────────────────────────┐
│ 1. Validar: ¿hay oro? ¿celda libre?                      │
│ 2. ¿Modo maze? → ¿bloquea el camino por completo?        │
│    → si bloquea, RECHAZAR la colocación                  │
│ 3. Colocar, cobrar, añadir al mp_grid como obstáculo     │
│ 4. Recalcular los paths de TODOS los enemigos activos    │
└──────────────────────────────────────────────────────────┘
┌─ Step ───────────────────────────────────────────────────┐
│ 5. objWaveManager: ¿toca spawnear?                       │
│ 6. Para cada enemigo: seguir su path                     │
│ 7. Para cada torre: buscar objetivo → disparar           │
│ 8. Para cada proyectil: mover → colisionar → daño        │
│ 9. Enemigos que llegan al final: restar vidas            │
│ 10. Enemigos muertos: dar oro                            │
│ 11. ¿Oleada terminada? → siguiente / victoria            │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 Grid y coordenadas

Todo en el juego se expresa en celdas; los píxeles se calculan al final.

```gml
CELL = 32;   // píxeles por celda
grid_x = x div CELL;
pixel_x = grid_x * CELL + (CELL * 0.5);
```

Mantén la grid lógica en un array 2D propio (como en la receta 05) para
saber qué hay en cada celda, y usa `mp_grid` **solo** para el pathfinding.

### 4.2 Pathfinding con `mp_grid` (A*)

GameMaker trae A* integrado. La firma verificada es:

```gml
mp_grid_create(left, top, hcells, vcells, cellwidth, cellheight);
mp_grid_path(id, path, xstart, ystart, xgoal, ygoal, allowdiag);
```

Flujo correcto:

1. Crear el `mp_grid` **una vez** al iniciar el nivel.
2. Marcar como prohibidas las celdas de torre: `mp_grid_add_cell`.
3. Calcular el path desde el spawn hasta el objetivo con `mp_grid_path()`.
4. Devolver `false` si no hay camino → la colocación es inválida.

**Coste:** `mp_grid_path()` es caro. No lo llames por frame por enemigo.
Calcúlalo **una vez** y compártelo, o recálcalo solo cuando cambie el grid.

### 4.3 La trampa del maze TD: la regla de no bloquear

Si permites construir laberintos, el jugador puede cerrar el camino por
completo. Dos soluciones:

| Solución | Cómo | Consecuencia |
|---|---|---|
| **Validación estricta** | Al colocar torre, comprueba que sigue existiendo un path para TODOS los enemigos activos y para el spawn | Seguro, pero O(n) paths por colocación |
| **Bloqueo parcial** | No permitas cerrar el último hueco: deja siempre al menos un camino | Rápido, pero el jugador lo nota arbitrario |

La validación estricta es la correcta. Con menos de 50 enemigos activos,
recalcular todos los paths al colocar una torre es un pico de un frame:
aceptable porque es una acción del jugador, no algo que pase 60 veces por
segundo.

### 4.4 Targeting de torres

Las cuatro políticas clásicas, y todas deben estar disponibles:

| Política | Elige | Cuándo es óptima |
|---|---|---|
| **First** | El más avanzado en el camino | Torres de daño alto, cadencia lenta |
| **Last** | El más atrasado | Evita que se escape el rezagado |
| **Strongest** | El de más vida | Torres de daño en área |
| **Closest** | El más cercano a la torre | Torres de corto alcance |

**Detalle importante:** elige por "avanzado en el camino", no por distancia
euclídea. Un enemigo cerca de la torre puede estar muy lejos del final.

### 4.5 Proyectiles vs hitscan

| Tipo | Ventaja | Uso |
|---|---|---|
| **Proyectil** | Se puede esquivar, se ve venir, permite *homing* | Cañones, catapultas |
| **Hitscan** (daño instantáneo) | Imposible de fallar, barato | Láseres, torretas rápidas |

Usa proyectiles con **homing** (persecución suave) para que no fallen nunca
pero se sigan viendo. Un proyectil que falla siempre frustra.

### 4.6 Economía

La economía es el sistema que hace que un TD sea interesante o plano:

| Mecánica | Efecto |
|---|---|
| **Oro por muerte** | Base |
| **Oro por oleada** | Permite planificar |
| **Intereses** (% del oro acumulado) | Premia no gastar → decisiones reales |
| **Venta con descuento** | Permite corregir errores (típicamente 70 %) |
| **Torres que generan oro** | Riesgo: ocupan parcela que no defiende |

### 4.7 Oleadas desde datos

Igual que en la receta 03: structs, no código.

---

## 5. Código base

### 5.0 Configuración

```gml
// ---------------------------------------------------------------------------
// scr_td_config
// ---------------------------------------------------------------------------
#macro CELL         32
#macro GRID_W       24
#macro GRID_H       18

#macro TD_VIDAS_INICIALES 20
#macro ORO_INICIAL     150
```

### 5.1 La grid lógica

```gml
// ---------------------------------------------------------------------------
// scr_td_grid
// ---------------------------------------------------------------------------

enum Celda { Vacia, Camino, Torre,Spawn, Objetivo, Bloqueada }

/// @func TDGrid()
function TDGrid() constructor
{
    celdas = [];
    for (var _x = 0; _x < GRID_W; _x++)
    {
        var _col = [];
        for (var _y = 0; _y < GRID_H; _y++)
        {
            array_push(_col, {
                tipo: Celda.Vacia,
                torre: noone
            });
        }
        array_push(celdas, _col);
    }

    // mp_grid para el pathfinding (se crea UNA vez)
    mp = mp_grid_create(0, 0, GRID_W, GRID_H, CELL, CELL);
    mp_grid_clear_all(mp);

    get = function(_x, _y)
    {
        if (_x < 0 || _y < 0 || _x >= GRID_W || _y >= GRID_H) return undefined;
        return celdas[_x][_y];
    };

    es_libre = function(_x, _y)
    {
        var _c = get(_x, _y);
        if (_c == undefined) return false;
        return (_c.tipo == Celda.Vacia);
    };

    colocar_torre = function(_x, _y, _torre)
    {
        celdas[_x][_y].tipo  = Celda.Torre;
        celdas[_x][_y].torre = _torre;

        // Marcar como obstáculo en el mp_grid
        mp_grid_add_cell(mp, _x, _y);
    };

    quitar_torre = function(_x, _y)
    {
        celdas[_x][_y].tipo  = Celda.Vacia;
        celdas[_x][_y].torre = noone;

        mp_grid_clear_cell(mp, _x, _y);
    };

    /// @desc Calcula un path. Devuelve el path o noone si no hay camino.
    calcular_path = function(_desde_x, _desde_y, _hasta_x, _hasta_y)
    {
        var _path = path_add();

        var _ok = mp_grid_path(
            mp, _path,
            _desde_x * CELL + (CELL * 0.5),
            _desde_y * CELL + (CELL * 0.5),
            _hasta_x * CELL + (CELL * 0.5),
            _hasta_y * CELL + (CELL * 0.5),
            false            // sin diagonales: caminos más legibles
        );

        if (!_ok)
        {
            path_delete(_path);
            return noone;
        }
        return _path;
    };

    /// @desc ¿Sigue habiendo camino desde el spawn hasta el objetivo?
    hay_camino = function(_spawn_x, _spawn_y, _obj_x, _obj_y)
    {
        var _p = calcular_path(_spawn_x, _spawn_y, _obj_x, _obj_y);
        if (_p == noone) return false;

        path_delete(_p);
        return true;
    };

    destroy = function()
    {
        mp_grid_destroy(mp);
    };
}
```

### 5.2 Definiciones de torre

```gml
// ---------------------------------------------------------------------------
// scr_towers
// ---------------------------------------------------------------------------

enum TargetMode { first, last, strongest, closest }
enum DamageType { fisico, area, hielo, laser }

/// @func TowerDef(_id, _nombre, _coste, _rango, _dano, _cadencia, _tipo_dano)
function TowerDef(
    _id, _nombre, _coste, _rango, _dano, _cadencia, _tipo_dano
) constructor
{
    id         = _id;
    nombre     = _nombre;
    coste      = _coste;
    rango      = _rango;        // en píxeles
    dano       = _dano;
    cadencia   = _cadencia;     // frames entre disparos
    tipo_dano  = _tipo_dano;

    sprite        = sprTowerArrow;
    sprite_proy   = sprArrow;
    vel_proy      = 8;
    radio_area    = 0;          // solo para tipo_dano == area
    factor_lentitud = 1.0;      // solo para hielo (0.5 = mitad de velocidad)
    duracion_lentitud = 0;

    // Mejoras: array de { coste, rango+, dano+, cadencia- }
    mejoras = [];

    /// @desc Coste total acumulado tras N mejoras
    coste_total = function(_nivel)
    {
        var _t = coste;
        for (var _i = 0; _i < _nivel && _i < array_length(mejoras); _i++)
        {
            _t += mejoras[_i].coste;
        }
        return _t;
    };

    /// @desc Valor de venta (70 % de lo invertido)
    valor_venta = function(_nivel)
    {
        return floor(coste_total(_nivel) * 0.7);
    };

    /// @desc Devuelve un struct con las stats efectivas en _nivel.
    stats_en = function(_nivel)
    {
        var _s = {
            rango:    rango,
            dano:     dano,
            cadencia: cadencia
        };

        for (var _i = 0; _i < _nivel && _i < array_length(mejoras); _i++)
        {
            var _m = mejoras[_i];
            if (variable_struct_exists(_m, "rango"))    _s.rango    += _m.rango;
            if (variable_struct_exists(_m, "dano"))     _s.dano     += _m.dano;
            if (variable_struct_exists(_m, "cadencia")) _s.cadencia -= _m.cadencia;
        }

        _s.cadencia = max(1, _s.cadencia);
        return _s;
    };
}

/// @func towers_init()
function towers_init()
{
    global.tower_defs = {};

    var _arrow = new TowerDef("arrow", "Torre de flechas", 60, 110, 12, 30,
                              DamageType.fisico);
    _arrow.sprite      = sprTowerArrow;
    _arrow.sprite_proy = sprArrow;
    _arrow.vel_proy    = 9;
    _arrow.mejoras = [
        { coste: 50, dano: 8,  rango: 15 },
        { coste: 80, dano: 12, rango: 20, cadencia: 4 }
    ];
    global.tower_defs.arrow = _arrow;

    var _cannon = new TowerDef("cannon", "Cañón", 120, 95, 30, 90,
                               DamageType.area);
    _cannon.sprite      = sprTowerCannon;
    _cannon.sprite_proy = sprCannonball;
    _cannon.vel_proy    = 5;
    _cannon.radio_area  = 40;
    _cannon.mejoras = [
        { coste: 110, dano: 20, radio_area: 10 },
        { coste: 180, dano: 30, radio_area: 15, cadencia: 15 }
    ];
    global.tower_defs.cannon = _cannon;

    var _frost = new TowerDef("frost", "Torre de hielo", 90, 100, 4, 45,
                              DamageType.hielo);
    _frost.sprite            = sprTowerFrost;
    _frost.sprite_proy       = sprShard;
    _frost.vel_proy          = 7;
    _frost.factor_lentitud   = 0.55;
    _frost.duracion_lentitud = 90;
    _frost.mejoras = [
        { coste: 80,  rango: 20, factor_lentitud: -0.10 },
        { coste: 140, rango: 25, duracion_lentitud: 40 }
    ];
    global.tower_defs.frost = _frost;

    var _laser = new TowerDef("laser", "Láser", 200, 140, 6, 6,
                              DamageType.laser);
    _laser.sprite = sprTowerLaser;
    _laser.mejoras = [
        { coste: 160, dano: 5, rango: 25 },
        { coste: 260, dano: 8, rango: 30, cadencia: 1 }
    ];
    global.tower_defs.laser = _laser;
}
```

### 5.3 Torre: targeting y disparo

```gml
// ---------------------------------------------------------------------------
// objTowerBase — Create
// ---------------------------------------------------------------------------
def     = global.tower_defs.arrow;
nivel   = 0;

cooldown     = 0;
target       = noone;
target_mode  = TargetMode.first;

grid_x = 0;
grid_y = 0;

angulo = 0;          // hacia dónde apunta la torreta

/// @func torre_stats()
function torre_stats() { return def.stats_en(nivel); }
```

```gml
// ---------------------------------------------------------------------------
// objTowerBase — Step
// ---------------------------------------------------------------------------
var _stats = torre_stats();

cooldown--;

// --- Buscar objetivo ---------------------------------------------------------
// Si el actual murió o salió de rango, buscar otro
if (target != noone && (!instance_exists(target) ||
    point_distance(x, y, target.x, target.y) > _stats.rango))
{
    target = noone;
}

if (target == noone)
{
    target = buscar_objetivo(_stats.rango, target_mode);
}

// --- Apuntar (interpolado: la torreta no debe girar de golpe) -----------------
if (target != noone && instance_exists(target))
{
    var _dir_objetivo = point_direction(x, y, target.x, target.y);
    var _diff = angle_difference(_dir_objetivo, angulo);
    angulo += _diff * 0.25;
}

// --- Disparar -----------------------------------------------------------------
if (target != noone && instance_exists(target) && cooldown <= 0)
{
    disparar(target, _stats);
    cooldown = _stats.cadencia;
}
```

```gml
// ---------------------------------------------------------------------------
// objTowerBase — targeting
// ---------------------------------------------------------------------------

/// @func buscar_objetivo(_rango, _modo)
/// @desc Devuelve el enemigo que cumpla la política elegida.
function buscar_objetivo(_rango, _modo)
{
    var _mejor = noone;
    var _mejor_valor = -999999;

    with (objEnemyBase)
    {
        var _d = point_distance(other.x, other.y, x, y);
        if (_d > _rango) continue;

        var _valor = 0;

        switch (_modo)
        {
            case TargetMode.first:
                // "First" = más avanzado en el camino = mayor índice de waypoint
                _valor = path_index_progreso;
                break;

            case TargetMode.last:
                _valor = -path_index_progreso;
                break;

            case TargetMode.strongest:
                _valor = hp;
                break;

            case TargetMode.closest:
                _valor = -_d;
                break;
        }

        if (_valor > _mejor_valor)
        {
            _mejor_valor = _valor;
            _mejor = id;
        }
    }

    return _mejor;
}
```

```gml
// ---------------------------------------------------------------------------
// objTowerBase — disparar
// ---------------------------------------------------------------------------

function disparar(_objetivo, _stats)
{
    switch (def.tipo_dano)
    {
        case DamageType.laser:
            // Hitscan: daño instantáneo + línea de láser
            _objetivo.hp -= _stats.dano;

            with (instance_create_depth(x, y, -50, objLaserBeam))
            {
                x1 = other.x; y1 = other.y;
                x2 = _objetivo.x; y2 = _objetivo.y;
                vida = 6;
            }

            audio_play_sound(sndLaser, 6, false);
            break;

        default:
            // Proyectil con homing
            var _p = instance_create_depth(x, y - 8, -40, objProjectile);
            _p.target   = _objetivo;
            _p.velocidad = def.vel_proy;
            _p.dano     = _stats.dano;
            _p.sprite_index = def.sprite_proy;
            _p.tipo_dano    = def.tipo_dano;
            _p.radio_area   = def.radio_area;
            _p.factor_lentitud   = def.factor_lentitud;
            _p.duracion_lentitud = def.duracion_lentitud;
            break;
    }

    // Juice: retroceso de la torreta
    squash_preset(self, "hit");
    audio_play_sound(sndShoot, 8, false);
}
```

### 5.4 Proyectil con homing

```gml
// ---------------------------------------------------------------------------
// objProjectile — Create
// ---------------------------------------------------------------------------
target      = noone;
velocidad   = 8;
dano        = 10;
tipo_dano   = DamageType.fisico;
radio_area  = 0;

factor_lentitud   = 1.0;
duracion_lentitud = 0;

direccion_actual = 0;
```

```gml
// ---------------------------------------------------------------------------
// objProjectile — Step
// ---------------------------------------------------------------------------
// Si el objetivo murió, seguir recto y desaparecer
if (target != noone && !instance_exists(target)) target = noone;

if (target != noone)
{
    // Homing suave: girar hacia el objetivo con un límite de giro
    var _dir_objetivo = point_direction(x, y, target.x, target.y);
    var _diff = angle_difference(_dir_objetivo, direccion_actual);
    direccion_actual += clamp(_diff, -12, 12);
}
else
{
    // Sin objetivo: seguir en línea recta
}

x += lengthdir_x(velocidad, direccion_actual);
y += lengthdir_y(velocidad, direccion_actual);

image_angle = direccion_actual;

// Fuera de la room
if (x < 0 || y < 0 || x > room_width || y > room_height)
{
    instance_destroy();
    exit;
}

// ¿Impactó?
if (target != noone && instance_exists(target) &&
    point_distance(x, y, target.x, target.y) < 10)
{
    impactar(target);
}
```

```gml
// ---------------------------------------------------------------------------
// objProjectile — impactar
// ---------------------------------------------------------------------------
function impactar(_enemigo)
{
    switch (tipo_dano)
    {
        case DamageType.area:
            // Daño en área: todos los enemigos dentro del radio
            var _n = 0;
            with (objEnemyBase)
            {
                if (point_distance(_enemigo.x, _enemigo.y, x, y) <= other.radio_area)
                {
                    hp -= other.dano;
                    _n++;
                }
            }

            // Explosión visual
            with (instance_create_depth(_enemigo.x, _enemigo.y, -30, objExplosion))
            {
                image_xscale = other.radio_area / 32;
                image_yscale = image_xscale;
            }
            camera_shake(0.15);
            break;

        case DamageType.hielo:
            _enemigo.hp -= dano;
            _enemigo.aplicar_lentitud(factor_lentitud, duracion_lentitud);

            with (instance_create_depth(_enemigo.x, _enemigo.y, -30, objFrostBurst))
            {
                image_angle = random(360);
            }
            break;

        default:
            _enemigo.hp -= dano;

            // Chispas
            part_particles_create(objFx.ps, x, y, objFx.pt_spark, 5);
            break;
    }

    audio_play_sound(sndImpact, 6, false);
    instance_destroy();
}
```

### 5.4 bis Definiciones de enemigo

```gml
// ---------------------------------------------------------------------------
// scr_enemies
// ---------------------------------------------------------------------------

/// @func EnemyDef(_id, _hp, _velocidad, _recompensa, _sprite)
function EnemyDef(_id, _hp, _velocidad, _recompensa, _sprite) constructor
{
    id         = _id;
    hp         = _hp;
    velocidad  = _velocidad;
    recompensa = _recompensa;
    sprite     = _sprite;
}

/// @func enemies_init()
/// @desc Rellena `global.enemy_defs` — sin esto, `objEnemyBase — Create` (§5.5) lee una
///       global que no existe y el juego revienta en el primer spawn.
function enemies_init()
{
    global.enemy_defs = {};
    global.enemy_defs.grunt = new EnemyDef("grunt", 30,  1.4, 10,  sprEnemyGrunt);
    global.enemy_defs.fast  = new EnemyDef("fast",  18,  2.6, 8,   sprEnemyFast);
    global.enemy_defs.tank  = new EnemyDef("tank",  140, 0.8, 25,  sprEnemyTank);
    global.enemy_defs.boss  = new EnemyDef("boss",  900, 0.6, 150, sprEnemyBoss);
}
```

### 5.5 Enemigo siguiendo un path

```gml
// ---------------------------------------------------------------------------
// objEnemyBase — Create
// ---------------------------------------------------------------------------
// Variables que fija el spawner: spawn_enemigo() (§5.8) ya pasa def_id por el
// var_struct de instance_create_depth, ANTES de este Create — ??= respeta ese
// valor y solo pone "grunt" por defecto si a esta instancia nunca se le fijó
// (p. ej. colocada a mano en el Room Editor).
def_id ??= "grunt";
hp      = 30;
hp_max  = 30;
velocidad_base = 1.4;
recompensa     = 10;

path_seguido = noone;
path_index_progreso = 0;

factor_lentitud   = 1.0;
lentitud_timer    = 0;

// Aplicar la definición
var _def = global.enemy_defs[$ def_id];
if (_def != undefined)
{
    hp             = _def.hp;
    hp_max         = _def.hp;
    velocidad_base = _def.velocidad;
    recompensa     = _def.recompensa;
    sprite_index   = _def.sprite;
}

/// @func aplicar_lentitud(_factor, _duracion)
function aplicar_lentitud(_factor, _duracion)
{
    // No acumular: se queda con la más fuerte
    factor_lentitud   = min(factor_lentitud, _factor);
    lentitud_timer    = max(lentitud_timer, _duracion);
}

/// @func enemigo_set_path(_path)
function enemigo_set_path(_path)
{
    if (path_seguido != noone && path_exists(path_seguido))
    {
        path_delete(path_seguido);
    }

    path_seguido = _path;

    if (_path != noone)
    {
        path_start(_path, velocidad_base * factor_lentitud,
                   path_action_stop, false);
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objEnemyBase — Step
// ---------------------------------------------------------------------------
if (lentitud_timer > 0)
{
    lentitud_timer--;
    if (lentitud_timer <= 0) factor_lentitud = 1.0;

    // Actualizar la velocidad del path cuando cambia la lentitud
    path_speed = velocidad_base * factor_lentitud;
}

// "First targeting": cuánto ha avanzado en el path.
// path_position va de 0 a 1 a lo largo del path.
path_index_progreso = (path_seguido != noone) ? (path_position * 1000) : 0;

// Barra de vida encima
// (dibujada en el Draw)

// --- ¿Llegó al final? ---------------------------------------------------------
if (path_seguido != noone && path_position >= 1)
{
    // Restar vida al jugador
    global.vidas -= 1;
    camera_shake(0.30);
    audio_play_sound(sndLeak, 10, false);

    if (global.vidas <= 0) global.derrota = true;

    instance_destroy();
    exit;
}

// --- ¿Murió? -------------------------------------------------------------------
if (hp <= 0)
{
    global.oro += recompensa;
    global.enemigos_muertos++;

    fx_floating_text(x, y - 10, "+" + string(recompensa), c_yellow);
    instance_create_depth(x, y, -20, objDeathPoof);
    audio_play_sound(sndEnemyDie, 6, false);

    instance_destroy();
}
```

### 5.6 Recalcular paths al colocar una torre

```gml
// ---------------------------------------------------------------------------
// scr_td_paths
// ---------------------------------------------------------------------------

/// @func td_recalcular_paths()
/// @desc Tras colocar o quitar una torre, recalcula el path de cada enemigo.
///       Es la función crítica del modo maze.
function td_recalcular_paths()
{
    var _grid = objGrid.grid;

    // --- 1. Path canónico desde el spawn --------------------------------------
    var _path_spawn = _grid.calcular_path(
        objGrid.spawn_x, objGrid.spawn_y,
        objGrid.objetivo_x, objGrid.objetivo_y);

    if (_path_spawn == noone)
    {
        // No hay camino: no debería pasar porque se validó antes, pero por si
        // acaso, no tocamos nada.
        return false;
    }

    // --- 2. Recalcular cada enemigo --------------------------------------------
    // Optimización: los enemigos en el MISMO tramo comparten path.
    // Para menos de 50 enemigos, recalcular uno a uno es aceptable.
    with (objEnemyBase)
    {
        // ¿Dónde está este enemigo, en qué celda?
        var _cx = x div CELL;
        var _cy = y div CELL;

        var _nuevo = _grid.calcular_path(_cx, _cy,
            objGrid.objetivo_x, objGrid.objetivo_y);

        if (_nuevo != noone)
        {
            // Mantener el progreso aproximado: reanudar desde donde iba
            var _progreso = (path_seguido != noone) ? path_position : 0;
            enemigo_set_path(_nuevo);
            path_position = _progreso;
        }
        // Si no hay camino desde su celda (lo han encerrado), dejarle el viejo
    }

    path_delete(_path_spawn);
    return true;
}

/// @func td_puede_colocar(_grid_x, _grid_y)
/// @desc ¿Se puede colocar una torre aquí sin bloquear el camino?
function td_puede_colocar(_grid_x, _grid_y)
{
    var _grid = objGrid.grid;

    if (!_grid.es_libre(_grid_x, _grid_y)) return false;

    // Simular: añadir la celda, comprobar, quitarla
    _grid.colocar_torre(_grid_x, _grid_y, noone);

    var _ok = _grid.hay_camino(
        objGrid.spawn_x, objGrid.spawn_y,
        objGrid.objetivo_x, objGrid.objetivo_y);

    _grid.quitar_torre(_grid_x, _grid_y);

    return _ok;
}
```

### 5.7 Colocación de torres

```gml
// ---------------------------------------------------------------------------
// objBuildManager — Create
// ---------------------------------------------------------------------------
torre_seleccionada = "arrow";
preview_valido     = false;
```

```gml
// ---------------------------------------------------------------------------
// objBuildManager — Step
// ---------------------------------------------------------------------------
var _gx = mouse_x div CELL;
var _gy = mouse_y div CELL;

var _def = global.tower_defs[$ torre_seleccionada];

preview_valido = (_def != undefined)
    && td_puede_colocar(_gx, _gy)
    && (global.oro >= _def.coste)
    && (_gx >= 0 && _gy >= 0 && _gx < GRID_W && _gy < GRID_H);

// --- Colocar al hacer clic -----------------------------------------------------
if (mouse_check_button_pressed(mb_left) && preview_valido)
{
    var _px = _gx * CELL + (CELL * 0.5);
    var _py = _gy * CELL + (CELL * 0.5);

    var _torre = instance_create_depth(_px, _py, -_gy * 10, objTowerBase);
    _torre.def    = _def;
    _torre.grid_x = _gx;
    _torre.grid_y = _gy;
    _torre.depth  = -_py;

    objGrid.grid.colocar_torre(_gx, _gy, _torre);

    global.oro -= _def.coste;

    // Recalcular caminos: la parte cara pero necesaria
    td_recalcular_paths();

    audio_play_sound(sndBuild, 10, false);
    squash_preset(_torre, "pickup");
}
```

```gml
// ---------------------------------------------------------------------------
// objBuildManager — Draw
// ---------------------------------------------------------------------------
if (torre_seleccionada == "") exit;

var _gx = mouse_x div CELL;
var _gy = mouse_y div CELL;
var _px = _gx * CELL + (CELL * 0.5);
var _py = _gy * CELL + (CELL * 0.5);

var _def = global.tower_defs[$ torre_seleccionada];
if (_def == undefined) exit;

// Círculo de rango
draw_set_alpha(0.25);
draw_set_color(preview_valido ? c_green : c_red);
draw_circle(_px, _py, _def.rango, true);
draw_set_alpha(1);

// Sprite fantasma de la torre
draw_sprite_ext(_def.sprite, 0, _px, _py, 1, 1, 0,
                preview_valido ? c_white : c_red, 0.65);
```

### 5.8 Oleadas desde structs

```gml
// ---------------------------------------------------------------------------
// scr_waves_td
// ---------------------------------------------------------------------------

/// @func TDGroup(_enemigo, _cantidad, _retardo, _intervalo)
function TDGroup(_enemigo, _cantidad, _retardo, _intervalo) constructor
{
    enemigo   = _enemigo;
    cantidad  = _cantidad;
    retardo   = _retardo;      // frames antes del primero
    intervalo = _intervalo;    // frames entre cada uno
    spawneados = 0;
    timer     = 0;
}

/// @func TDWave(_grupos, _recompensa)
function TDWave(_grupos, _recompensa) constructor
{
    grupos     = _grupos;
    recompensa = (_recompensa == undefined) ? 50 : _recompensa;
    terminada  = false;

    reset = function()
    {
        terminada = false;
        for (var _i = 0; _i < array_length(grupos); _i++)
        {
            grupos[_i].spawneados = 0;
            grupos[_i].timer = 0;
        }
    };

    update = function()
    {
        var _todos = true;

        for (var _i = 0; _i < array_length(grupos); _i++)
        {
            var _g = grupos[_i];
            if (_g.spawneados >= _g.cantidad) continue;

            _todos = false;
            _g.timer++;

            // El primero sale tras "retardo"; los demás cada "intervalo"
            var _toca = (_g.spawneados == 0)
                ? (_g.timer >= _g.retardo)
                : (_g.timer >= _g.intervalo);

            if (_toca)
            {
                spawn_enemigo(_g.enemigo);
                _g.spawneados++;
                _g.timer = 0;
            }
        }

        terminada = _todos;
    };
}

/// @func waves_td_build()
function waves_td_build()
{
    return [
        new TDWave([ new TDGroup("grunt", 8, 30, 45) ], 40),
        new TDWave([ new TDGroup("grunt", 12, 30, 38) ], 50),
        new TDWave([
            new TDGroup("fast", 6, 30, 35),
            new TDGroup("grunt", 8, 120, 50)
        ], 70),
        new TDWave([
            new TDGroup("tank", 2, 30, 120),
            new TDGroup("grunt", 10, 90, 40)
        ], 100),
        new TDWave([ new TDGroup("boss", 1, 60, 0) ], 300)
    ];
}
```

```gml
// ---------------------------------------------------------------------------
// objWaveManager — Create / Step
// ---------------------------------------------------------------------------
// Create
waves      = waves_td_build();
wave_index = 0;
wave       = waves[wave_index];
wave.reset();
entre_oleadas = 0;
auto_iniciar  = false;

// Step
if (wave == noone) exit;

if (!wave.terminada)
{
    wave.update();
}
else if (instance_number(objEnemyBase) == 0)
{
    // Oleada completada
    global.oro += wave.recompensa;
    fx_floating_text(room_width * 0.5, 120,
                     "¡Oleada " + string(wave_index + 1) + " completada! +" +
                     string(wave.recompensa), c_green);

    wave_index++;

    if (wave_index >= array_length(waves))
    {
        global.victoria = true;
        wave = noone;
    }
    else
    {
        wave = waves[wave_index];
        wave.reset();
    }
}
```

```gml
// ---------------------------------------------------------------------------
// scr_spawn_enemy
// ---------------------------------------------------------------------------

/// @func spawn_enemigo(_def_id)
function spawn_enemigo(_def_id)
{
    var _px = objGrid.spawn_x * CELL + (CELL * 0.5);
    var _py = objGrid.spawn_y * CELL + (CELL * 0.5);

    // def_id va en el var_struct, no asignado después: objEnemyBase — Create (§5.5)
    // aplica la definición DURANTE su propio Create, así que fijarlo tras crear la
    // instancia llegaría tarde y todo enemigo saldría con las stats de "grunt".
    var _e = instance_create_depth(_px, _py, -_py, objEnemyBase, { def_id: _def_id });

    // Calcular su path desde el spawn
    var _path = objGrid.grid.calcular_path(
        objGrid.spawn_x, objGrid.spawn_y,
        objGrid.objetivo_x, objGrid.objetivo_y);

    if (_path != noone)
    {
        _e.enemigo_set_path(_path);
    }
    else
    {
        show_debug_message("ERROR: no hay camino desde el spawn");
    }

    return _e;
}
```

---

## 6. Gestión del estado del jugador

```gml
// ---------------------------------------------------------------------------
// scr_td_state
// ---------------------------------------------------------------------------

/// @func TDState()
/// @desc Economía, vidas y progresión de la partida.
function TDState() constructor
{
    oro          = ORO_INICIAL;
    vidas        = TD_VIDAS_INICIALES;
    oleada       = 0;
    enemigos_muertos = 0;
    torres_colocadas = 0;
    oro_gastado  = 0;

    derrota = false;
    victoria = false;

    // Intereses: premia guardar oro
    interes_porcentaje = 0.02;   // 2 % por oleada
    interes_tope       = 25;     // máximo que puedes ganar por oleada

    /// @desc Se llama al terminar cada oleada.
    fin_de_oleada = function()
    {
        var _interes = min(floor(oro * interes_porcentaje), interes_tope);
        oro += _interes;
        oleada++;
        return _interes;
    };

    gastar = function(_cantidad)
    {
        if (oro < _cantidad) return false;
        oro -= _cantidad;
        oro_gastado += _cantidad;
        return true;
    };

    ganar = function(_cantidad)
    {
        oro += _cantidad;
    };

    perder_vida = function(_cantidad)
    {
        vidas -= (_cantidad == undefined) ? 1 : _cantidad;
        if (vidas <= 0)
        {
            vidas = 0;
            derrota = true;
        }
    };

    /// @desc Estadísticas para la pantalla de resultados.
    serialize = function()
    {
        return {
            oro: oro, vidas: vidas, oleada: oleada,
            enemigos_muertos: enemigos_muertos,
            torres_colocadas: torres_colocadas,
            oro_gastado: oro_gastado,
            victoria: victoria, derrota: derrota
        };
    };
}

// --- Uso global ----------------------------------------------------------------
// objGame — Create (persistente)
towers_init();     // rellena global.tower_defs (§5.2) — sin esto, colocar una torre revienta
enemies_init();    // rellena global.enemy_defs (§5.4 bis) — sin esto, el primer spawn revienta
global.td = new TDState();
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Permitir cerrar el camino por completo | Los enemigos desaparecen o se quedan quietos | `td_puede_colocar()` validando antes de colocar |
| `mp_grid_path()` por frame por enemigo | El juego va a 10 fps con 30 enemigos | Calcula el path una vez; recalcula solo al cambiar el grid |
| No liberar los paths (`path_delete`) | Fuga de memoria: cada path ocupa memoria | `path_delete()` al destruir el enemigo y al recalcular |
| `path_add()` sin comprobar el resultado | Paths huérfanos si `mp_grid_path` falla | Comprueba `!= noone` y borra si falla |
| Targeting por distancia para "first" | La torre dispara al que está cerca pero va primero otro | Usa el progreso en el path (`path_position`) |
| Proyectiles sin homing que siempre fallan | El jugador culpa al juego | Homing suave o hitscan |
| Lentitud que se acumula infinitamente | El enemigo se queda congelado para siempre | `min()` para no acumular; timer que la resetea |
| No recalcular el path tras quitar una torre | Los enemigos dan la vuelta larga sin motivo | `td_recalcular_paths()` también al vender |
| Diagonales en el path | Los enemigos "cortan" esquinas y se salen del camino | `allowdiag = false` |
| Recalcular paths durante la oleada sin control | Pico de lag justo al colocar | Es aceptable (es input del jugador), pero muestra un indicador de carga si tarda |
| Vender una torre sin devolver la celda al `mp_grid` | La celda sigue bloqueada para siempre | `mp_grid_clear_cell()` en `quitar_torre()` |
| Oleadas definidas en código | Imposible ajustar la dificultad sin recompilar | Structs `TDWave` / `TDGroup` |

---

## 8. Cómo escalarlo

1. **Más tipos de torre** — el struct `TowerDef` ya soporta mejoras. Añade
   torres de veneno (daño por segundo), de oro, de buff a torres vecinas.
2. **Resistencias de enemigos** — `resistencias: { area: 0.5, hielo: 0 }`.
   Multiplica el daño recibido por tipo.
3. **Múltiples caminos** — dos spawns. Duplica la complejidad del pathfinding
   y obliga al jugador a dividir defensas.
4. **Enemigos que atacan torres** — cambia por completo el género: las torres
   pasan a tener vida y a poder ser destruidas.
5. **Habilidades del jugador** — un rayo global con cooldown, o congelar el
   tiempo 5 segundos.
6. **Modo infinito con escalado** — dificultad que crece por oleada:
   `hp *= 1.15^oleada`. Sencillo y efectivo.
7. **Previsualización de la ruta** — dibuja el path calculado para que el
   jugador vea hacia dónde van a ir los enemigos antes de construir.
8. **Mapas con altura / puentes** — el pathfinding se complica, pero con
   `mp_grid` sigue siendo manejable marcando celdas inaccesibles.

**Cuándo pasar a otra receta:** si dominas `mp_grid` y las oleadas desde
datos, la estrategia (receta 13) te resultará familiar: la mitad del trabajo
(grid + pathfinding + selección) ya lo tienes hecho.

---

## 9. Fuentes

- **Plantilla oficial Tower Defence** del IDE (New → Game → Template) — juego
  completo comentado
- Manual oficial — Motion Planning / MP Grids (`mp_grid_create`,
  `mp_grid_path`, `mp_grid_add_cell`, `mp_grid_clear_cell`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Motion_Planning.htm
- Manual oficial — Paths (`path_add`, `path_start`, `path_position`,
  `path_speed`, `path_delete`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Paths.htm
- Manual oficial — `angle_difference`, `point_distance`, `lengthdir_x` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Angles_And_Distance.htm
- Manual oficial — `instance_number`, `instance_create_depth` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Instances.htm
- Manual oficial — `draw_circle`, `draw_set_alpha` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Basic_Forms.htm
- Receta propia: **03 — Shoot 'em up** (oleadas desde datos, pooling)
- Receta propia: **05 — Roguelike** (grids 2D)
