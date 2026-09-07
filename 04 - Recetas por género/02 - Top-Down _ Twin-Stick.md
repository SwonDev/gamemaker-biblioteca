# 02 — Top-Down / Twin-Stick

> **Dificultad:** básica
> Si vienes de la receta 01, el 80 % del código te sirve igual. Lo que cambia
> es el significado del eje Y: deja de ser gravedad y pasa a ser profundidad.

---

## 1. Visión general

En un top-down la cámara mira desde arriba y los dos ejes son equivalentes.
Esa aparente simplicidad esconde tres problemas nuevos que no existían en
plataformas:

1. **La diagonal rápida** — pulsar dos teclas a la vez debe dar la misma
   velocidad que pulsar una.
2. **El orden de dibujado** — quien está más abajo en la pantalla tapa a quien
   está más arriba.
3. **La puntería** — el personaje mira a un sitio y se mueve hacia otro.

**Lo que define al género:**

- Movimiento libre en 360° (8 direcciones discretas o analógico completo).
- Separación entre "hacia dónde me muevo" y "hacia dónde apunto".
- Espacio legible: el jugador debe ver las amenazas antes de que le toquen.

**Referencias hechas en GameMaker:** *Enter the Gungeon*, *Nuclear Throne*,
*Hyper Light Drifter*, *Undertale* (exploración), *Forager* (top-down de
gestión), *Hotline Miami* (top-down táctico), *Death Road to Canada*.

**Subgéneros:**

| Subgénero | Cámara | Combate | Ejemplo |
|---|---|---|---|
| Aventura / exploración | Sigue al jugador, suave | Cuerpo a cuerpo | Hyper Light Drifter |
| *Twin-stick shooter* | Sigue + *look-ahead* | A distancia, 360° | Nuclear Throne |
| *Roguelite* de salas | Fija por sala | Mixto | Enter the Gungeon |
| Táctico / sigilo | Libre, alejada | Uno contra muchos | Hotline Miami |

---

## 2. Arquitectura recomendada

### Jerarquía de objetos

```
objEntity            (padre: movimiento + colisión + vida)
├── objPlayer
├── objEnemy         (padre de enemigos)
│   ├── objEnemyMelee    (persigue y ataca al contacto)
│   ├── objEnemyRanged   (mantiene distancia, dispara)
│   └── objEnemyBoss
└── objNPC

objSolid             (árboles, muros, rocas)
objBullet            (pool — ver sección 5.5)
objBulletEnemy
objItem              (recogible, se acerca al jugador)
objDepthSorter       (controller que reordena depths)
objCamera
```

### Capas y depth

```
rm_arena
├── Floor            (tilemap de suelo)
├── Shadows          (capa de sombras proyectadas)
├── DepthSort        (capa de instancias ordenadas por Y)
│   ├── objSolid
│   ├── objEntity
│   └── objItem
├── Overlay          (lluvia, polvo)
└── UI               (HUD — mejor como UI Layer, ver receta 13)
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `WeaponDef` | Daño, cadencia, dispersión, sprites, sonido |
| `PlayerStats` | Vida, munición, velocidad, mejoras |
| `RoomBounds` | Límites de la cámara |

---

## 3. El bucle central (core loop)

```
┌─ Begin Step ────────────────────────────────────────────┐
│ 1. Leer input: movimiento (stick izq.) + apuntado (der.) │
│ 2. Normalizar el vector de movimiento                    │
└──────────────────────────────────────────────────────────┘
┌─ Step ──────────────────────────────────────────────────┐
│ 3. Calcular vel_x / vel_y con aceleración                │
│ 4. move_and_collide(vel_x, vel_y, objSolid)              │
│ 5. Actualizar ángulo de apuntado (aim_dir)               │
│ 6. Arma: cooldown, disparar → pedir bala al pool         │
│ 7. Actualizar todas las balas (movimiento + colisión)    │
│ 8. IA de enemigos                                        │
│ 9. Resolver daño                                         │
│ 10. depth = -bbox_bottom  (orden de dibujado)            │
│ 11. Actualizar sprite según movimiento + aim             │
└──────────────────────────────────────────────────────────┘
┌─ End Step ──────────────────────────────────────────────┐
│ 12. Cámara (seguimiento + look-ahead del ratón + shake)  │
└──────────────────────────────────────────────────────────┘
```

> **Por qué `depth` se actualiza en el Step y no en el Draw:** el Draw es
> demasiado tarde. GameMaker ya ha decidido el orden de dibujado cuando llega
> al evento Draw de la primera instancia.

---

## 4. Sistemas clave

### 4.1 Movimiento en 8 direcciones

```gml
var _ix = _right - _left;
var _iy = _down  - _up;

// Sin normalizar: la diagonal va √2 veces más rápido (≈1,41x). MAL.
vel_x = _ix * speed;
vel_y = _iy * speed;
```

### 4.2 Normalización de diagonales

Hay tres formas de resolverlo. La tercera es la mejor.

```gml
// ❌ Opción A: dividir por √2 siempre.
// Falso: rompe si _ix y _iy no son ±1exactos (mando analógico).
vel_x = (_ix * SPEED) / 1.4142;

// ⚠️ Opción B: point_direction + lengthdir. Correcto pero crea un vector
// unitario incluso con entrada mínima → el mando arranca "de golpe".
var _dir = point_direction(0, 0, _ix, _iy);
vel_x = lengthdir_x(SPEED, _dir);

// ✅ Opción C: normalizar si la magnitud supera el círculo unitario.
var _mag = point_distance(0, 0, _ix, _iy);
if (_mag > 1)
{
    _ix /= _mag;
    _iy /= _mag;
}
vel_x = _ix * SPEED;
vel_y = _iy * SPEED;
```

La opción C es la correcta porque respeta la magnitud analógica del stick:
si empujas el stick a la mitad, el personaje va a la mitad de velocidad.

### 4.3 Rotación hacia el ratón

```gml
aim_dir = point_direction(x, y, mouse_x, mouse_y);
image_angle = aim_dir;
```

Con mando (twin-stick de verdad):

```gml
var _ax = gamepad_axis_value(0, gp_axisrx);
var _ay = gamepad_axis_value(0, gp_axisry);
if (point_distance(0, 0, _ax, _ay) > 0.3)   // zona muerta
{
    aim_dir = point_direction(0, 0, _ax, _ay);
}
```

**Zona muerta obligatoria:** los sticks analógicos nunca devuelven 0 exacto.
Sin zona muerta el personaje rota solo.

### 4.4 Depth sorting por Y

La técnica clásica: cuanto más abajo en la pantalla (mayor `y`), menor `depth`
(se dibuja antes, queda detrás).

```gml
// En el End Step de cada entidad:
depth = -bbox_bottom;
```

**Por qué `bbox_bottom` y no `y`:** con `y`, dos objetos con el origen en
distinto sitio (una mesa alta y una rata) se ordenan mal. `bbox_bottom` es el
punto de contacto real con el suelo, que es lo que el ojo usa para juzgar
profundidad.

**Alternativa para scenes con miles de instancias:** un único objeto
`objDepthSorter` que, una vez por frame, recoge las instancias de una capa,
las ordena y las reasigna. Es más rápido que N escrituras de `depth` porque
evita reordenar la lista de instancias N veces.

### 4.5 Colisión

`move_and_collide()` funciona igual que en plataformas. La diferencia es que
aquí querrás **deslizar** por las paredes en vez de pararte en seco: con
`xoffset`/`yoffset` a `0` (default) ya lo hace por ti.

Para detección de balas contra paredes usa `place_meeting` o, mejor,
`collision_line` si la bala va muy rápido (evita que atraviese muros finos).

### 4.6 Disparo y cadencia

Nunca uses `alarm` para la cadencia de fuego si quieres armas configurables.
Un contador en frames es más flexible:

```gml
fire_cooldown--;
if (fire_cooldown <= 0 && mouse_check_button(mb_left))
{
    fire_cooldown = weapon.cooldown_frames;
    // disparar
}
```

---

## 5. Código base

### 5.0 Definición de arma con structs

```gml
// ---------------------------------------------------------------------------
// scr_weapons
// ---------------------------------------------------------------------------

/// @func WeaponDef(_nombre, _daño, _cadencia, _velocidad, _dispersion, _balas)
function WeaponDef(
    _nombre, _daño, _cadencia, _velocidad, _dispersion, _balas
) constructor
{
    nombre          = _nombre;
    damage          = _daño;
    cooldown_frames = _cadencia;
    bullet_speed    = _velocidad;
    spread_deg      = _dispersion;   // dispersión total en grados
    bullets_per_shot = _balas;
    sprite_bullet   = sprBullet;
    auto            = false;         // ¿fuego automático al mantener?
    knockback       = 2;

    /// @desc Devuelve un array de ángulos, uno por bala de la ráfaga.
    get_angles = function(_base_dir)
    {
        var _out = [];
        var _half = spread_deg * 0.5;

        if (bullets_per_shot <= 1)
        {
            var _jitter = random_range(-_half, _half);
            array_push(_out, _base_dir + _jitter);
            return _out;
        }

        var _step = spread_deg / (bullets_per_shot - 1);
        for (var _i = 0; _i < bullets_per_shot; _i++)
        {
            array_push(_out, _base_dir - _half + (_step * _i));
        }
        return _out;
    };
}

// Catálogo global
global.weapons = {
    pistol: new WeaponDef("Pistola",     10, 18, 10,  3, 1),
    shotgun:new WeaponDef("Escopeta",     7, 45,  9, 28, 6),
    smg:    new WeaponDef("Subfusil",     5,  5, 12, 12, 1),
    rifle:  new WeaponDef("Rifle",       25, 30, 16,  1, 1)
};
global.weapons.smg.auto = true;
```

### 5.1 `objPlayer` — Create

```gml
// ---------------------------------------------------------------------------
// objPlayer — Create
// ---------------------------------------------------------------------------
vel_x = 0;
vel_y = 0;

SPEED       = 3.4;
ACCEL       = 0.28;
FRICTION    = 0.25;

aim_dir     = 0;
facing      = 1;

weapon      = global.weapons.pistol;
fire_cooldown = 0;

// Vida e invulnerabilidad
hp          = 100;
hp_max      = 100;
invuln_time = 0;

// Efectos
hit_flash   = 0;    // frames de parpadeo blanco al recibir daño
```

> 💡 **`hit_flash` solo cuenta frames: hay que dibujarlo.** Las tres vías (shader con
> uniform, `image_blend` + `gpu_set_fog`, sprite blanco aditivo) están en
> [04 · 15 — Game feel y juice §5.6 bis](./15%20-%20Game%20feel%20y%20juice.md#56-bis--dibujar-el-hit_flash-las-tres-v%C3%ADas).
> Sin ese paso, la variable se decrementa y no se ve nada.

### 5.2 `objPlayer` — Step

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step
// ---------------------------------------------------------------------------
// --- 1. Input de movimiento (teclado + mando) -------------------------------
var _ix = 0;
var _iy = 0;

_ix += keyboard_check(ord("D")) || keyboard_check(vk_right) ? 1 : 0;
_ix -= keyboard_check(ord("A")) || keyboard_check(vk_left)  ? 1 : 0;
_iy += keyboard_check(ord("S")) || keyboard_check(vk_down)  ? 1 : 0;
_iy -= keyboard_check(ord("W")) || keyboard_check(vk_up)    ? 1 : 0;

if (gamepad_is_connected(0))
{
    var _gx = gamepad_axis_value(0, gp_axislh);
    var _gy = gamepad_axis_value(0, gp_axislv);
    if (abs(_gx) > 0.2) _ix = _gx;
    if (abs(_gy) > 0.2) _iy = _gy;
}

// --- 2. Normalizar la diagonal ---------------------------------------------
var _mag = point_distance(0, 0, _ix, _iy);
if (_mag > 1)
{
    _ix /= _mag;
    _iy /= _mag;
}

// --- 3. Aceleración / fricción ---------------------------------------------
if (_ix != 0 || _iy != 0)
{
    vel_x = lerp(vel_x, _ix * SPEED, ACCEL);
    vel_y = lerp(vel_y, _iy * SPEED, ACCEL);
}
else
{
    vel_x = lerp(vel_x, 0, FRICTION);
    vel_y = lerp(vel_y, 0, FRICTION);
    if (abs(vel_x) < 0.05) vel_x = 0;
    if (abs(vel_y) < 0.05) vel_y = 0;
}

// --- 4. Mover con colisión --------------------------------------------------
move_and_collide(vel_x, vel_y, objSolid, 4, 0, 0, SPEED, SPEED);

// --- 5. Apuntado -------------------------------------------------------------
// El ratón tiene prioridad; si se mueve el stick derecho, manda el stick.
var _ax = 0, _ay = 0;
if (gamepad_is_connected(0))
{
    _ax = gamepad_axis_value(0, gp_axisrx);
    _ay = gamepad_axis_value(0, gp_axisry);
}

if (point_distance(0, 0, _ax, _ay) > 0.3)
{
    aim_dir = point_direction(0, 0, _ax, _ay);
}
else if (_mag > 0.1 || true)
{
    aim_dir = point_direction(x, y, mouse_x, mouse_y);
}

// --- 6. Disparo --------------------------------------------------------------
fire_cooldown--;

var _shooting = weapon.auto
    ? mouse_check_button(mb_left)
    : mouse_check_button_pressed(mb_left);

if (gamepad_is_connected(0))
{
    _shooting = weapon.auto
        ? gamepad_button_check(0, gp_shoulderrb)
        : gamepad_button_check_pressed(0, gp_shoulderrb);
}

if (_shooting && fire_cooldown <= 0)
{
    fire_weapon(aim_dir);
    fire_cooldown = weapon.cooldown_frames;
}

// --- 7. Mirada y profundidad -------------------------------------------------
facing = (aim_dir > 90 && aim_dir < 270) ? -1 : 1;
image_xscale = facing;
depth = -bbox_bottom;

// --- 8. Temporizadores -------------------------------------------------------
if (invuln_time > 0) invuln_time--;
if (hit_flash   > 0) hit_flash--;
```

### 5.3 Disparar

```gml
// ---------------------------------------------------------------------------
// scr_player_combat
// ---------------------------------------------------------------------------

/// @func fire_weapon(_dir)
/// @desc Crea las balas de la ráfaga actual desde el cañón del arma.
function fire_weapon(_dir)
{
    var _angles = weapon.get_angles(_dir);
    var _count  = array_length(_angles);

    // Punto de salida: el extremo del arma
    var _muzzle_x = x + lengthdir_x(14, _dir);
    var _muzzle_y = y + lengthdir_y(14, _dir);

    for (var _i = 0; _i < _count; _i++)
    {
        var _b = bullet_pool_get();
        if (_b == noone) break;

        with (_b)
        {
            x            = _muzzle_x;
            y            = _muzzle_y;
            direction    = _angles[_i];
            speed        = other.weapon.bullet_speed;
            damage       = other.weapon.damage;
            owner        = other.id;
            sprite_index = other.weapon.sprite_bullet;
            active       = true;
            life_frames  = 180;
        }
    }

    // Retroceso: empuja al jugador en dirección contraria (sensación de peso)
    vel_x -= lengthdir_x(weapon.knockback * 0.3, _dir);
    vel_y -= lengthdir_y(weapon.knockback * 0.3, _dir);

    // Juice: flash en el cañón + shake corto
    with (instance_create_layer(_muzzle_x, _muzzle_y, "Effects", objMuzzleFlash))
    {
        image_angle = _dir;
    }
    objCamera.camera_shake(1.2, 4);
}

/// @func take_damage(_cantidad, _origen_x, _origen_y)
function take_damage(_cantidad, _origen_x, _origen_y)
{
    if (invuln_time > 0) return false;

    hp          -= _cantidad;
    invuln_time  = 45;
    hit_flash    = 8;

    // Knockback desde el origen del golpe
    var _kb_dir = point_direction(_origen_x, _origen_y, x, y);
    vel_x += lengthdir_x(6, _kb_dir);
    vel_y += lengthdir_y(6, _kb_dir);

    objCamera.camera_shake(4, 10);

    if (hp <= 0)
    {
        hp = 0;
        instance_destroy();
        room_restart();   // sustituir por una pantalla de muerte real
    }
    return true;
}
```

### 5.4 `objBullet` (sin pool)

```gml
// ---------------------------------------------------------------------------
// objBullet — Create
// ---------------------------------------------------------------------------
damage      = 1;
owner       = noone;
life_frames = 180;
active      = true;

// ---------------------------------------------------------------------------
// objBullet — Step
// ---------------------------------------------------------------------------
life_frames--;
if (life_frames <= 0) { bullet_pool_return(id); exit; }

// Colisión con paredes: usa collision_line para no atravesar muros finos
if (collision_line(x, y, x + lengthdir_x(speed, direction),
                         y + lengthdir_y(speed, direction), objSolid, false, true))
{
    bullet_pool_return(id);
    exit;
}

// Colisión con objetivos
var _target = (owner == objPlayer.id) ? objEnemy : objPlayer;
var _hit = instance_place(x, y, _target);
if (_hit != noone)
{
    with (_hit)
    {
        take_damage(other.damage, other.x, other.y);
    }
    with (instance_create_layer(x, y, "Effects", objImpact))
    {
        image_angle = other.direction + 180;
    }
    bullet_pool_return(id);
}
```

### 5.5 Object pooling de balas

Crear y destruir cientos de instancias por segundo genera picos de GC y
tirones. Un *pool* recicla instancias: las "destruidas" se desactivan y se
reutilizan.

```gml
// ---------------------------------------------------------------------------
// scr_bullet_pool — pool global de balas
// ---------------------------------------------------------------------------

/// @func bullet_pool_init(_cantidad)
/// @desc Pre-crea el pool. Llamar una vez en objGame → Create.
function bullet_pool_init(_cantidad)
{
    global.bullet_pool = [];

    for (var _i = 0; _i < _cantidad; _i++)
    {
        var _b = instance_create_layer(0, 0, "Effects", objBullet);
        _b.active = false;
        _b.visible = false;
        array_push(global.bullet_pool, _b);
    }
}

/// @func bullet_pool_get()
/// @desc Devuelve una bala inactiva o noone si el pool está agotado.
function bullet_pool_get()
{
    var _pool = global.bullet_pool;
    var _len  = array_length(_pool);

    for (var _i = 0; _i < _len; _i++)
    {
        var _b = _pool[_i];
        if (_b != noone && instance_exists(_b) && !_b.active)
        {
            _b.visible = true;
            return _b;
        }
    }

    // Pool agotado: crecer dinámicamente en vez de fallar en silencio
    var _nb = instance_create_layer(0, 0, "Effects", objBullet);
    array_push(_pool, _nb);
    return _nb;
}

/// @func bullet_pool_return(_bala)
/// @desc Devuelve la bala al pool (la desactiva, no la destruye).
function bullet_pool_return(_bala)
{
    _bala.active      = false;
    _bala.visible     = false;
    _bala.speed       = 0;
    _bala.x           = -1000;
    _bala.y           = -1000;
}
```

> **Regla:** en un pool, **nunca** llames a `instance_destroy()`. Si lo haces,
> el array guarda IDs muertos y `instance_exists()` empieza a fallar en cadena.

### 5.6 `objDepthSorter` — orden eficiente

```gml
// ---------------------------------------------------------------------------
// objDepthSorter — End Step (un único objeto en la room)
// ---------------------------------------------------------------------------
// Reordena todas las entidades de una sola pasada.
// Más barato que N asignaciones de depth dispersas.

var _list = ds_list_create();

with (objEntity)
{
    ds_list_add(_list, id);
}
with (objSolid)
{
    ds_list_add(_list, id);
}

// Ordenar por bbox_bottom descendente: los de más abajo primero
ds_list_sort(_list, false);   // requiere que los ids sean comparables...

ds_list_destroy(_list);
```

> ⚠️ El fragmento anterior es ilustrativo del *problema*: ordenar por ID no
> ordena por Y. La implementación correcta usa una **grid** auxiliar o un
> array de structs `{inst, y}` ordenado con `array_sort()`. Ver versión
> correcta abajo.

```gml
// ---------------------------------------------------------------------------
// objDepthSorter — End Step  (versión correcta con array_sort)
// ---------------------------------------------------------------------------
depth_items = [];

with (objEntity) array_push(depth_items, { inst: id, order: bbox_bottom });
with (objSolid)  array_push(depth_items, { inst: id, order: bbox_bottom });
with (objItem)   array_push(depth_items, { inst: id, order: bbox_bottom });

// array_sort(variable, sorttype_or_function) — verificado en el manual
array_sort(depth_items, function(_a, _b)
{
    return (_a.order < _b.order) ? -1 : ((_a.order > _b.order) ? 1 : 0);
});

var _len = array_length(depth_items);
for (var _i = 0; _i < _len; _i++)
{
    var _entry = depth_items[_i];
    if (instance_exists(_entry.inst))
    {
        _entry.inst.depth = -_i;
    }
}
```

### 5.7 `objCamera` — seguimiento con look-ahead hacia el ratón

```gml
// ---------------------------------------------------------------------------
// objCamera — Create
// ---------------------------------------------------------------------------
cam = view_camera[0];
cam_x = x;
cam_y = y;
shake_mag    = 0;
shake_frames = 0;

function camera_shake(_magnitud, _frames)
{
    shake_mag    = max(shake_mag, _magnitud);
    shake_frames = max(shake_frames, _frames);
}
```

```gml
// ---------------------------------------------------------------------------
// objCamera — End Step
// ---------------------------------------------------------------------------
if (!instance_exists(objPlayer)) exit;

var _vw = camera_get_view_width(cam);
var _vh = camera_get_view_height(cam);

// Objetivo: mitad de camino entre el jugador y el ratón.
// Así el jugador ve hacia donde dispara sin perder de vista al personaje.
var _tx = lerp(objPlayer.x, mouse_x, 0.25);
var _ty = lerp(objPlayer.y, mouse_y, 0.25);

cam_x = lerp(cam_x, _tx, 0.14);
cam_y = lerp(cam_y, _ty, 0.14);

// Limitar a la room
cam_x = clamp(cam_x, _vw * 0.5, max(_vw * 0.5, room_width  - _vw * 0.5));
cam_y = clamp(cam_y, _vh * 0.5, max(_vh * 0.5, room_height - _vh * 0.5));

var _ox = 0, _oy = 0;
if (shake_frames > 0)
{
    _ox = irandom_range(-shake_mag, shake_mag);
    _oy = irandom_range(-shake_mag, shake_mag);
    shake_frames--;
    if (shake_frames <= 0) shake_mag = 0;
}

camera_set_view_pos(cam, round(cam_x - _vw * 0.5 + _ox),
                         round(cam_y - _vh * 0.5 + _oy));
```

### 5.8 Enemigo cuerpo a cuerpo

```gml
// ---------------------------------------------------------------------------
// objEnemyMelee — Create
// ---------------------------------------------------------------------------
vel_x = 0;
vel_y = 0;
SPEED     = 1.6;
hp        = 30;
damage    = 12;
attack_range  = 22;
attack_cooldown = 0;
hit_flash = 0;

// ---------------------------------------------------------------------------
// objEnemyMelee — Step
// ---------------------------------------------------------------------------
attack_cooldown--;
if (hit_flash > 0) hit_flash--;

if (!instance_exists(objPlayer)) exit;

var _dist = point_distance(x, y, objPlayer.x, objPlayer.y);

if (_dist > attack_range)
{
    // Perseguir
    var _dir = point_direction(x, y, objPlayer.x, objPlayer.y);
    vel_x = lerp(vel_x, lengthdir_x(SPEED, _dir), 0.10);
    vel_y = lerp(vel_y, lengthdir_y(SPEED, _dir), 0.10);
}
else
{
    // Atacar
    vel_x = lerp(vel_x, 0, 0.25);
    vel_y = lerp(vel_y, 0, 0.25);

    if (attack_cooldown <= 0)
    {
        attack_cooldown = 45;
        objPlayer.take_damage(damage, x, y);
    }
}

move_and_collide(vel_x, vel_y, objSolid, 4, 0, 0, SPEED, SPEED);
depth = -bbox_bottom;
```

---

## 6. Gestión del estado del jugador

```gml
// ---------------------------------------------------------------------------
// scr_player_state_topdown
// ---------------------------------------------------------------------------

/// @func PlayerStateTopDown()
/// @desc Estado persistente del jugador en un top-down con progresión.
function PlayerStateTopDown() constructor
{
    hp        = 100;
    hp_max    = 100;
    speed_lvl = 1;          // nivel de mejora de velocidad
    damage_lvl = 1;         // nivel de mejora de daño

    ammo      = {};         // { pistol: -1 (infinita), shotgun: 40, ... }
    unlocked  = ["pistol"]; // armas desbloqueadas
    current_weapon = "pistol";

    keys      = 0;
    coins     = 0;
    rooms_cleared = 0;

    /// @desc Aplica un multiplicador de daño según el nivel de mejora.
    get_damage_multiplier = function()
    {
        return 1 + (damage_lvl - 1) * 0.15;
    };

    /// @desc Comprueba si el jugador tiene munición de un arma concreta.
    has_ammo = function(_weapon_name)
    {
        if (!variable_struct_exists(ammo, _weapon_name)) return false;
        var _a = ammo[$ _weapon_name];
        return (_a == -1) || (_a > 0);     // -1 = infinita
    };

    consume_ammo = function(_weapon_name)
    {
        if (!variable_struct_exists(ammo, _weapon_name)) return;
        var _a = ammo[$ _weapon_name];
        if (_a > 0) ammo[$ _weapon_name] = _a - 1;
    };

    unlock = function(_weapon_name, _starting_ammo)
    {
        if (!array_contains(unlocked, _weapon_name))
        {
            array_push(unlocked, _weapon_name);
        }
        ammo[$ _weapon_name] = _starting_ammo;
    };

    serialize = function()
    {
        return {
            hp: hp, hp_max: hp_max,
            speed_lvl: speed_lvl, damage_lvl: damage_lvl,
            ammo: ammo, unlocked: unlocked,
            current_weapon: current_weapon,
            keys: keys, coins: coins
        };
    };
}

// NOTA: array_contains() es una función NATIVA de GameMaker desde 2024.
// Firma: array_contains(array, value, [offset], [length])
// No la redefinas: duplicar una función integrada es un error de compilación.
```

Persistencia entre rooms con `objGame` (marcado como *persistent*):

```gml
// objGame — Create
if (!variable_global_exists("player_state"))
{
    global.player_state = new PlayerStateTopDown();
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| No normalizar la diagonal | Moverse en diagonal es un 41 % más rápido | Divide por la magnitud si `_mag > 1` |
| Dividir siempre por √2 | Con mando analógico, el movimiento mínimo se amplifica a velocidad máxima | Normaliza **solo** si la magnitud supera 1 |
| Sin zona muerta en el stick | El personaje rota o se mueve solo | Ignora el stick por debajo de `0.2`–`0.3` |
| `depth = -y` con orígenes distintos | Objetos altos se dibujan mal delante de los bajos | Usa `depth = -bbox_bottom` |
| Actualizar `depth` en el Draw | No tiene efecto: la lista de dibujado ya está ordenada | Hazlo en el **Step** |
| `instance_destroy()` en balas con pool | El array del pool se llena de IDs muertos y `instance_exists()` falla | Nunca destruyas: desactiva y devuelve |
| Cadencia con `alarm[0]` fijo | No puedes cambiar de arma sin reescribir el código | Usa un contador `fire_cooldown` y `weapon.cooldown_frames` |
| Bala rápida que atraviesa muros | A 16 px/frame, un muro de 8 px se salta | Usa `collision_line()` entre la posición actual y la siguiente |
| Recoger items con `place_meeting` | Recoges un objeto que ya se destruyó ese frame | Usa `instance_place()` y comprueba `!= noone` |
| Ratón en coordenadas de GUI | La puntería se desplaza con la cámara | Usa `mouse_x`/`mouse_y` (room) y **no** `device_mouse_x_to_gui()` |
| Disparar desde `x`,`y` | La bala sale del centro del personaje y parece que sale del ombligo | Punto de salida con `lengthdir_*` desde el cañón |
| Cámara con `lerp` fijo sin clamp | La cámara se sale de la room en los bordes | `clamp()` siempre tras el `lerp` |

---

## 8. Cómo escalarlo

1. **Variedad de armas** — el struct `WeaponDef` ya está preparado. Añade
   `sprite_bullet`, `knockback`, `auto`, `bullets_per_shot`.
2. **Salas cerradas** — al entrar en una sala, activa un `objDoor` que se
   cierra, spawnea oleadas y se abre al limpiar. Es la estructura de Gungeon.
3. **Enemigos con rangos** — `objEnemyRanged` mantiene distancia: si
   `point_distance < 120`, se aleja; si `> 200`, se acerca; si no, dispara.
4. **Sombras proyectadas** — dibuja el sprite con `draw_sprite_ext` y
   `image_yscale` negativo y alfa baja, antes que el personaje.
5. **Iluminación 2D** — superficie negra con "agujeros" radiales usando
   `gpu_set_blendmode(bm_subtract)`.
6. **Tile collisions** — para mapas grandes, migra a `tilemap_get_at_pixel()`
   (ver receta 05).
7. **Minimapa** — comparte código con la receta 06.
8. **Local co-op** — segundo jugador con `objPlayer2`, cámara que encuadra
   ambos. Para que cada jugador tenga sus propias teclas/botones (no solo su propio mando),
   el punto de partida es
   [25 · Menú de opciones §5.8](./25%20-%20Menú%20de%20opciones%20y%20ajustes.md#58-perfiles-de-input-por-jugador-local-co-op) —
   un `global.controles_jugador[n]` en vez de un único `global.controles`.

**Cuándo pasar a otra receta:** cuando tengas 3 armas, 2 tipos de enemigo y
una sala que se cierra, estás listo para la receta 03 (shmup), que formaliza
lo que aquí has hecho a mano.

---

## 9. Fuentes

- Manual oficial — `move_and_collide` —
  https://manual.gamemaker.io/monthly/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement_And_Collisions/move_and_collide.htm
- Manual oficial — Funciones de array (`array_push`, `array_sort`, `array_length`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm
- Manual oficial — `collision_line` / `instance_place` / `place_meeting` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions.htm
- Manual oficial — `point_direction`, `lengthdir_x`, `point_distance` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Angles_And_Distance.htm
- Manual oficial — Gamepad / `gamepad_axis_value` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/GamePad_Input.htm
- Manual oficial — Structs y constructores —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Structs.htm
- **How To Optimise Your Games** (tutorial oficial) —
  https://gamemaker.io/tutorials/how-to-optimise-your-games
- **Make Your Own Arcade Space Shooter** (tutorial oficial, aplica el mismo
  patrón de disparo) — https://gamemaker.io/tutorials/make-arcade-space-shooter
