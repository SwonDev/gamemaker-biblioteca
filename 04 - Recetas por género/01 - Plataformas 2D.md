# 01 — Plataformas 2D

> **Dificultad:** básica · **Empieza aquí**
> Es el género que mejor enseña *game feel*, porque todo el peso del juego
> recae en cuatro números: velocidad horizontal, gravedad, altura de salto y
> tiempo de aceleración.

---

## 1. Visión general

Un plataformas se define por una sola relación: **el jugador contra la
gravedad**. Todo lo demás (enemigos, púas, monedas, jefes) es decorado sobre
esa relación. Si el salto se siente bien, el juego funciona aunque el arte sea
provisional; si el salto se siente mal, ningún arte lo salva.

**Lo que define al género:**

- El eje vertical es el protagonista: caer es el estado por defecto.
- La precisión importa más que la velocidad (Celeste, Meat Boy) o al revés
  (Sonic, Rayman). Esa decisión es lo primero que debes tomar.
- El jugador necesita **agencia en el aire**: cuanto más control tenga mientras
  cae, más justo percibe el juego.

**Referencias hechas en GameMaker:** *Celeste*, *Hyper Light Drifter*,
*Undertale* (las secciones de puzles de plataformas), *Nuclear Throne*,
*Downwell*, *TowerFall*, *Risk of Rain*, *Katana ZERO*.
El tutorial oficial *Make Your First Platformer in GameMaker* construye
exactamente este tipo de juego en ~15 minutos.

**Subgéneros y cómo cambian el diseño:**

| Subgénero | Gravedad | Control aéreo | Cámara |
|---|---|---|---|
| Preciso (Celeste) | Alta | Muy alto | Deadzone amplia, *look-ahead* |
| Velocidad (Sonic) | Media | Medio | Muy adelantada, rápida |
| *Runner* infinito | Fija | Solo salto | Fija, el mundo se mueve |
| Exploración (Metroid) | Baja | Alto | Deadzone + *room transitions* |

---

## 2. Arquitectura recomendada

### Jerarquía de objetos

```
objEntity            (padre: ApplyGravity, ApplyMovement — sin sprite)
├── objPlayer        (hijo: input + estados + cámara)
└── objEnemy         (padre de enemigos)
    ├── objEnemyWalker
    └── objEnemyFlyer

objSolid             (colisión total; invisible si usas tiles para el arte)
objPlatform          (one-way: solo colisiona al caer)
objPlatformMoving    (mueve al jugador con ella)
objHazard            (púas, lava — daño al contacto)
objCheckpoint
objCoin / objPickup

objCamera            (persistente, controla la view)
objGame              (persistente, controla el estado global)
```

**Por qué herencia aquí:** el movimiento y la gravedad son idénticos para
jugador y enemigos. Si lo duplicas en dos objetos, cualquier ajuste de
gravedad se convierte en dos cambios que olvidarás sincronizar.

### Rooms y capas

```
rm_level_01
├── Background       (capa de fondo, parallax)
├── Tiles_Collision  (tilemap — el arte)
├── Instances        (objetos: jugador, enemigos, púas)
├── Entities         (capa lógica, sin dibujar)
└── Foreground       (decoración delante)
```

> **Regla de oro:** el tilemap es **arte**, no física. La física la lleva
> `objSolid`, que es invisible y se pinta en la room cubriendo los tiles.
> Es lo que recomienda el tutorial oficial y evita dolores de cabeza con
> tilesets de formas irregulares.

### Structs que vas a usar

| Struct | Responsabilidad |
|---|---|
| `PlayerStats` | Vida, monedas, habilidades desbloqueadas, persistencia |
| `InputState` | Lectura cruda de teclado/mando, normalizada |
| `TweenHandle` | Animaciones de squash & stretch, flashes de daño |

---

## 3. El bucle central (core loop)

Orden **exacto** de ejecución en un frame. El orden importa: si lees el input
después de moverte, el jugador reacciona un frame tarde y se nota.

```
┌─ Begin Step ─────────────────────────────────────────────┐
│ 1. Leer input (teclado + mando)                          │
│ 2. Pegarse a plataforma móvil (aplicar delta)            │
└──────────────────────────────────────────────────────────┘
┌─ Step ───────────────────────────────────────────────────┐
│ 3. Timers: coyote, jump buffer                           │
│ 4. Calcular velocidad horizontal (aceleración + fricción)│
│ 5. Aplicar gravedad a vel_y                              │
│ 6. Salto: ¿hay buffer y hay coyote/ground? → vel_y = -J  │
│ 7. Salto variable: si suelta y vel_y < 0 → recortar      │
│ 8. move_and_collide(vel_x, vel_y, objSolid, ...)         │
│ 9. Resolver plataformas one-way                          │
│ 10. Actualizar flag on_ground                            │
│ 11. Máquina de estados (idle/run/jump/fall)              │
│ 12. Actualizar sprite según estado                       │
└──────────────────────────────────────────────────────────┘
┌─ End Step ───────────────────────────────────────────────┐
│ 13. Cámara: deadzone + look-ahead + shake                │
└──────────────────────────────────────────────────────────┘
┌─ Draw ───────────────────────────────────────────────────┐
│ 14. draw_self() con squash & stretch aplicado            │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 Movimiento horizontal: aceleración y fricción

No asignes la velocidad directamente. Interpola hacia el objetivo: la
aceleración es lo que hace que el personaje "pese".

```gml
// Dos líneas que cambian por completo el tacto
vel_x = lerp(vel_x, _target_x, ACCEL_GROUND);   // en suelo
vel_x = lerp(vel_x, _target_x, ACCEL_AIR);      // en el aire
```

- `ACCEL_GROUND ≈ 0.25` → respuesta rápida y precisa (Celeste, Mario).
- `ACCEL_GROUND ≈ 0.06` → personaje pesado con inercia (Sonic, Meat Boy).
- `ACCEL_AIR` **menor** que `ACCEL_GROUND` para que el aire se sienta distinto.

### 4.2 Gravedad asimétrica

La gravedad al subir y al bajar **no debe ser igual**. Si al caer es más
fuerte, el salto se siente "pesado" arriba y "rápido" abajo, que es lo que
percibimos como un salto con fuerza.

```gml
if (vel_y < 0 && !key_jump_held) grav = GRAV_RISE_FAST;   // suelta el botón
else if (vel_y < 0)              grav = GRAV_RISE;        // subiendo
else                             grav = GRAV_FALL;        // cayendo
```

### 4.3 Coyote time

**Problema:** el jugador sale corriendo de un borde y pulsa salto 2 frames
después. Técnicamente ya no está en el suelo. Sin coyote time, el salto no
sale y el jugador culpa al juego.

**Solución:** un pequeño margen (típicamente 6‑10 frames) durante el cual el
juego *finge* que sigues en el suelo.

```gml
if (on_ground) coyote_timer = COYOTE_FRAMES;
else           coyote_timer--;
```

### 4.4 Jump buffering

**Problema:** el jugador pulsa salto 3 frames antes de aterrizar. Sin buffer,
ese input se pierde.

**Solución:** recuerda la pulsación unos frames y consúmela al aterrizar.

```gml
if (key_jump_pressed) buffer_timer = BUFFER_FRAMES;
else                  buffer_timer--;

if (buffer_timer > 0 && coyote_timer > 0) { saltar(); buffer_timer = 0; coyote_timer = 0; }
```

> Coyote time y jump buffer son las dos técnicas con mejor
> relación esfuerzo/resultado de todo el desarrollo de juegos. Son 8 líneas
> de código y transforman la percepción de justicia del juego.

### 4.5 Salto variable

Mantener el botón = salto alto. Soltarlo = salto corto. Es la base del control
aéreo. Hay dos formas de implementarlo y **la segunda es mejor**:

```gml
// ❌ Regular: cortar la velocidad al 50%. Se siente abrupto.
if (!key_jump_held && vel_y < 0) vel_y *= 0.5;

// ✅ Mejor: subir la gravedad mientras sueltas. Se siente natural.
if (!key_jump_held && vel_y < 0) grav = GRAV_RISE_FAST;
```

### 4.6 `move_and_collide()` — la función central

Firma verificada en el manual oficial:

```gml
move_and_collide(hspd, vspd, obj, [iterations], [xoffset], [yoffset], [max_x], [max_y]);
```

| Argumento | Default | Qué hace |
|---|---|---|
| `hspd` | — | Píxeles a mover en X este frame |
| `vspd` | — | Píxeles a mover en Y este frame |
| `obj` | — | Objeto (o array de objetos) contra el que colisionar |
| `iterations` | `4` | Sub-pasos hasta llegar al destino. Más = más preciso, más caro |
| `xoffset` / `yoffset` | `0` | Dirección alternativa al chocar. `0` = perpendicular al movimiento |
| `max_x` / `max_y` | `-1` | Límite de desplazamiento por eje. `-1` = sin límite |

**Por qué importan los dos últimos:** si no limitas `max_x`, al deslizarte por
una pendiente la componente vertical se reconvierte en horizontal y el
personaje *acelera* al bajar rampas. El tutorial oficial lo resuelve así:

```gml
move_and_collide(vel_x, vel_y, objSolid, 4, 0, 0, MOVE_SPEED_MAX, -1);
```

`move_and_collide()` **ya gestiona pendientes** (slopes) por ti, siempre que
el sprite del suelo tenga la máscara de colisión en "Rectangle with Rotation".

### 4.7 Plataformas de un sentido (one-way)

`move_and_collide()` no las soporta de forma nativa. Se resuelven con una
corrección manual **después** de moverte: solo colisionan si estabas cayendo y
tus pies venían de arriba.

### 4.8 Plataformas móviles

El jugador debe viajar con la plataforma. El patrón correcto es guardar la
referencia y aplicar el *delta* de movimiento de la plataforma en **Begin
Step**, antes de calcular nada más.

> Una plataforma móvil en eje vertical **es** un ascensor: mismo código de §5.8, sin cambios,
> solo con `move_dy`/`y_min`/`y_max` en vez de los horizontales. Se nombra aquí explícitamente
> porque el otro caso de "ascensor" de la biblioteca —el *joint* prismático de Box2D en
> [`04 · 22`](./22%20-%20Físicas%20con%20Box2D.md), línea 154— sí lleva la palabra en el
> comentario, y este caso manual (mucho más habitual en un plataformas 2D sin motor de físicas)
> no la llevaba: sin esta nota, buscar "ascensor" en la biblioteca solo encontraba el caso Box2D.

### 4.9 Cámara con deadzone

> 🔺 **Antes de escribir el primer `window_set_size()`, decide la escala.** Quien monta una
> cámara está a un paso de fijar la resolución, y hacerlo a ojo da una escala **no entera** —con
> lo que unos píxeles del arte miden dos y otros tres, y el movimiento «hierve». La receta, con
> `escala_entera_maxima()` y `aplicar_resolucion()` ya escritas, está en
> [`13 · 03 §1.6`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/03%20-%20Pixel%20art%20y%20resolución.md#16-lo-mínimo-que-necesitas-para-que-la-escala-sea-entera).
> Este enlace existe porque un agente montó la resolución a ojo (480×270 en una ventana de
> 1280×720: escala 2,67×) y no llegó a ese documento hasta el final, pensando que «pixel art»
> era cosa de artistas.

Perseguir al jugador con `lerp` directo es cómodo pero produce dos problemas:
la cámara se mueve con cada micro-movimiento (mareo) y siempre va por detrás.
La solución de los juegos profesionales tiene tres piezas:

1. **Deadzone**: una caja en el centro de la pantalla. Si el jugador está
   dentro, la cámara no se mueve.
2. **Look-ahead**: la cámara se adelanta en la dirección de la mirada, para
   que veas hacia dónde vas.
3. **Suavizado**: `lerp` sobre el objetivo ya calculado, no sobre el jugador.

---

## 5. Código base

### 5.0 Configuración global (`scr_config`)

> ⚠️ Si tu proyecto ya sigue la arquitectura de
> [`13 · 06` §3.12](<../13 - Diseño y producción de videojuegos/06 - Arquitectura de un proyecto GameMaker.md#312-macros-enums-y-configs-del-ide>)
> («un solo script `scr_config` con TODAS las constantes»), fusiona este bloque con el suyo en
> vez de tener dos — `13 · 06` remite aquí para `COYOTE_FRAMES` a propósito, para no acabar con
> dos valores distintos del mismo macro.

```gml
// ---------------------------------------------------------------------------
// scr_config — constantes de juego. Se ejecuta una sola vez al arrancar.
// ---------------------------------------------------------------------------
#macro TILE_SIZE 16

// Movimiento horizontal
#macro MOVE_SPEED_MAX   4.0   // píxeles por frame
#macro ACCEL_GROUND     0.25  // 0..1 → qué fracción del objetivo se gana/frame
#macro ACCEL_AIR        0.15
#macro FRICTION_GROUND  0.30
#macro FRICTION_AIR     0.08

// Salto y gravedad
#macro JUMP_SPEED       11.0  // velocidad inicial al saltar (negativa hacia arriba)
#macro GRAV_RISE        0.45  // subiendo, botón mantenido
#macro GRAV_RISE_FAST   0.90  // subiendo, botón soltado (salto variable)
#macro GRAV_FALL        0.62  // cayendo (más que GRAV_RISE → salto con peso)
#macro VELY_TERMINAL    14.0  // velocidad máxima de caída

// Técnicas de sensación
#macro COYOTE_FRAMES    8
#macro BUFFER_FRAMES    8
#macro JUMP_CUT_FACTOR  0.45

// Cámara
#macro CAM_DEADZONE_W   48
#macro CAM_DEADZONE_H   32
#macro CAM_LOOKAHEAD    32
#macro CAM_SMOOTH       0.12

global.game_paused = false;
```

### 5.1 `objPlayer` — Create

```gml
// ---------------------------------------------------------------------------
// objPlayer — Create
// ---------------------------------------------------------------------------
// Velocidades (NO uses speed/hspeed/vspeed: son built-ins con efectos secundarios)
vel_x = 0;
vel_y = 0;

// Estado de suelo
on_ground      = false;
coyote_timer   = 0;
buffer_timer   = 0;
was_on_ground  = false;

// Plataformas
riding          = noone;        // instancia de objPlatformMoving que pisamos
riding_prev_x   = 0;
riding_prev_y   = 0;

// Máquina de estados (definida más abajo)
state       = PlayerState.idle;
state_timer = 0;

// Solo visual
facing      = 1;                // 1 = derecha, -1 = izquierda
squash_x    = 1;
squash_y    = 1;

// Stats del jugador (ver sección 6)
stats = new PlayerStats();
```

### 5.2 `objPlayer` — Begin Step

```gml
// ---------------------------------------------------------------------------
// objPlayer — Begin Step
// ---------------------------------------------------------------------------
// 1) Viajar con la plataforma móvil ANTES de cualquier otra cuenta.
if (instance_exists(riding))
{
    x += (riding.x - riding_prev_x);
    y += (riding.y - riding_prev_y);
    riding_prev_x = riding.x;
    riding_prev_y = riding.y;
}
else
{
    riding = noone;
}
```

### 5.3 `objPlayer` — Step

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step
// ---------------------------------------------------------------------------
if (global.game_paused) exit;

// --- 1. Input ---------------------------------------------------------------
var _left  = keyboard_check(vk_left)  || keyboard_check(ord("A"));
var _right = keyboard_check(vk_right) || keyboard_check(ord("D"));
var _jump_pressed = keyboard_check_pressed(vk_space)
                 || keyboard_check_pressed(vk_up)
                 || keyboard_check_pressed(ord("W"));
var _jump_held = keyboard_check(vk_space) || keyboard_check(vk_up) || keyboard_check(ord("W"));

// Soporte de mando (opcional, no interfiere con teclado)
if (gamepad_is_connected(0))
{
    var _gx = gamepad_axis_value(0, gp_axislh);
    if (abs(_gx) > 0.25) { _left = (_gx < 0); _right = (_gx > 0); }
    if (gamepad_button_check_pressed(0, gp_face1)) _jump_pressed = true;
    _jump_held = _jump_held || gamepad_button_check(0, gp_face1);
}

var _input_x = _right - _left;   // -1, 0 o 1

// --- 2. Timers de sensación -------------------------------------------------
if (on_ground) coyote_timer = COYOTE_FRAMES;
else           coyote_timer--;

if (_jump_pressed) buffer_timer = BUFFER_FRAMES;
else               buffer_timer--;

// --- 3. Movimiento horizontal -----------------------------------------------
var _target_x = _input_x * MOVE_SPEED_MAX;
var _accel = on_ground ? ACCEL_GROUND : ACCEL_AIR;

if (_input_x != 0)
{
    vel_x = lerp(vel_x, _target_x, _accel);
    facing = _input_x;
}
else
{
    var _fric = on_ground ? FRICTION_GROUND : FRICTION_AIR;
    vel_x = lerp(vel_x, 0, _fric);
    if (abs(vel_x) < 0.05) vel_x = 0;   // evita el deslizamiento infinito del lerp
}

// --- 4. Salto (buffer + coyote) ---------------------------------------------
if (buffer_timer > 0 && coyote_timer > 0)
{
    vel_y       = -JUMP_SPEED;
    buffer_timer = 0;
    coyote_timer = 0;
    on_ground    = false;

    // Squash de anticipación → se resuelve en el Draw
    squash_x = 0.75;
    squash_y = 1.30;
}

// --- 5. Salto variable + gravedad asimétrica --------------------------------
var _grav;
if      (vel_y < 0 && !_jump_held) _grav = GRAV_RISE_FAST;   // soltó el botón
else if (vel_y < 0)                _grav = GRAV_RISE;        // subiendo
else                               _grav = GRAV_FALL;       // cayendo

vel_y = min(vel_y + _grav, VELY_TERMINAL);

// --- 6. Colisión y movimiento -----------------------------------------------
was_on_ground = on_ground;

var _hit = move_and_collide(vel_x, vel_y, objSolid, 4, 0, 0, MOVE_SPEED_MAX, -1);

// move_and_collide devuelve un array [instancia_eje_x, instancia_eje_y] o undefined
if (is_array(_hit))
{
    if (!is_undefined(_hit[0]) && instance_exists(_hit[0])) vel_x = 0;
    if (!is_undefined(_hit[1]) && instance_exists(_hit[1]))
    {
        if (vel_y > 0 && is_undefined(_hit[1])) {}      // cayendo y nada debajo
        if (vel_y > 0) {}                                // placeholder
        if (_hit[1] != noone && vel_y > 0)
        {
            // Aterrizaje: stretch de impacto
            if (!was_on_ground) { squash_x = 1.35; squash_y = 0.70; }
        }
        vel_y = 0;
    }
}

// --- 7. Plataformas de un sentido -------------------------------------------
resolve_one_way();

// --- 8. Actualizar flag de suelo --------------------------------------------
on_ground = place_meeting(x, y + 1, objSolid) || place_meeting_on_way(x, y + 1);

// --- 9. Detectar plataforma móvil bajo los pies -----------------------------
var _under = instance_position(x, bbox_bottom + 2, objPlatformMoving);
if (_under != noone && on_ground)
{
    if (riding != _under) { riding = _under; }
    riding_prev_x = riding.x;
    riding_prev_y = riding.y;
}
else if (!instance_exists(riding))
{
    riding = noone;
}

// --- 10. Máquina de estados -------------------------------------------------
state_timer++;
update_player_state();

// --- 11. Sprite ---------------------------------------------------------------
image_xscale = facing;
apply_state_sprite();

// --- 12. Relajar el squash hacia 1 (hacia la forma neutra) ------------------
squash_x = lerp(squash_x, 1, 0.20);
squash_y = lerp(squash_y, 1, 0.20);
```

### 5.4 Plataformas one-way

```gml
// ---------------------------------------------------------------------------
// scr_platform_oneway — funciones auxiliares
// ---------------------------------------------------------------------------

/// @func resolve_one_way()
/// @desc Corrige la posición si el jugador aterriza sobre una plataforma one-way.
///       Debe llamarse DESPUÉS de move_and_collide() y SOLO si vel_y > 0.
function resolve_one_way()
{
    if (vel_y <= 0) exit;                    // subiendo o quieto: ignorar

    var _feet_prev = bbox_bottom - vel_y - 1; // dónde estaban los pies antes
    var _feet_now  = bbox_bottom;             // dónde están ahora

    var _inst = collision_rectangle(
        bbox_left,  _feet_prev,
        bbox_right, _feet_now,
        objPlatform, false, true
    );

    if (_inst != noone)
    {
        // Los pies han cruzado el borde superior de la plataforma → aterrizar
        y   -= (bbox_bottom - _inst.bbox_top);
        vel_y    = 0;
        on_ground = true;

        if (!was_on_ground) { squash_x = 1.35; squash_y = 0.70; }
    }
}

/// @func place_meeting_on_way(_x, _y)
/// @desc place_meeting() restringido a plataformas one-way.
function place_meeting_on_way(_x, _y)
{
    return place_meeting(_x, _y, objPlatform);
}
```

> **Aviso:** `objPlatform` no debe pasarse a `move_and_collide()`. Si lo haces,
> el jugador colisionará con ella desde abajo y desde los lados. La colisión
> se resuelve **solo** con `resolve_one_way()`.

### 5.5 Máquina de estados

```gml
// ---------------------------------------------------------------------------
// scr_player_states — máquina de estados por función (sin librerías externas)
// ---------------------------------------------------------------------------
enum PlayerState { idle, run, jump, fall, hurt }

/// @desc Cambia de estado reseteando el temporizador y ejecutando el enter.
function player_state_set(_new)
{
    if (state == _new) exit;

    state       = _new;
    state_timer = 0;

    switch (_new)
    {
        case PlayerState.jump: squash_x = 0.80; squash_y = 1.25; break;
        case PlayerState.fall: squash_x = 1.05; squash_y = 0.95; break;
        case PlayerState.hurt: vel_x = -facing * 4; vel_y = -5;  break;
    }
}

/// @desc Lógica por-frame de la máquina de estados.
function update_player_state()
{
    switch (state)
    {
        case PlayerState.idle:
            if (!on_ground)   player_state_set(PlayerState.fall);
            else if (abs(vel_x) > 0.3) player_state_set(PlayerState.run);
            break;

        case PlayerState.run:
            if (!on_ground)   player_state_set(PlayerState.fall);
            else if (abs(vel_x) <= 0.3) player_state_set(PlayerState.idle);
            break;

        case PlayerState.jump:
            if (vel_y >= 0) player_state_set(PlayerState.fall);
            break;

        case PlayerState.fall:
            if (on_ground)
            {
                player_state_set(abs(vel_x) > 0.3 ? PlayerState.run
                                                  : PlayerState.idle);
            }
            break;

        case PlayerState.hurt:
            // Invulnerable unos frames, luego volver a la neutral
            if (state_timer > 24) player_state_set(PlayerState.idle);
            break;
    }
}

/// @desc Asigna el sprite correspondiente al estado activo.
function apply_state_sprite()
{
    var _spr = sprite_index;

    switch (state)
    {
        case PlayerState.idle: _spr = sprPlayerIdle; break;
        case PlayerState.run:  _spr = sprPlayerRun;  break;
        case PlayerState.jump: _spr = sprPlayerJump; break;
        case PlayerState.fall: _spr = sprPlayerFall; break;
        case PlayerState.hurt: _spr = sprPlayerHurt; break;
    }

    if (sprite_index != _spr)
    {
        sprite_index = _spr;
        image_index  = 0;
    }

    // La velocidad de animación de la carrera depende de la velocidad real
    image_speed = (state == PlayerState.run)
        ? 0.15 + (abs(vel_x) / MOVE_SPEED_MAX) * 0.35
        : 1;
}
```

### 5.6 `objPlayer` — Draw (squash & stretch)

```gml
// ---------------------------------------------------------------------------
// objPlayer — Draw
// ---------------------------------------------------------------------------
// Squash & stretch conservando el volumen: si X baja, Y sube.
// El origen del sprite debe estar en "Bottom Centre" para que el
// personaje no se hunda en el suelo al aplastarse.
draw_sprite_ext(
    sprite_index, image_index,
    x, y,
    image_xscale * squash_x,
    image_yscale * squash_y,
    image_angle,
    image_blend,
    image_alpha
);
```

### 5.7 `objCamera` — deadzone + look-ahead + shake

> ⚠️ **Shake básico, no la firma canónica.** La biblioteca tiene UNA sola
> `camera_shake(_cantidad)` (modelo de trauma, un argumento) en
> [`04 · 15` §5.1](./15%20-%20Game%20feel%20y%20juice.md#5-código-base); si tu
> proyecto también usa esa receta (recomendado en cuanto pase de prototipo),
> **no definas `camera_shake()` aquí**: GameMaker no permite dos funciones con
> el mismo nombre en el mismo proyecto, y las dos firmas son incompatibles
> (dos argumentos y un modelo de acumulado-con-decaimiento, contra un
> argumento y trauma al cuadrado). El shake de abajo se llama
> `camera_shake_basico()` — dos argumentos, sin dependencias — para poder
> convivir con la canónica sin colisionar.

```gml
// ---------------------------------------------------------------------------
// objCamera — Create (un único objeto persistente en la room)
// ---------------------------------------------------------------------------
cam = view_camera[0];
cam_target_x = x;
cam_target_y = y;

// Shake básico (independiente del modelo de trauma de 04 · 15 §5.1)
shake_mag    = 0;
shake_frames = 0;

// Inicializar centrado sobre el jugador
if (instance_exists(objPlayer))
{
    cam_target_x = objPlayer.x;
    cam_target_y = objPlayer.y;
}

/// @func camera_shake_basico(_magnitud, _frames)
/// @desc Shake independiente, solo para este objCamera si NO usas 04 · 15.
///       Si usas game feel/juice, usa camera_shake(_cantidad) de 04 · 15 §5.1
///       en su lugar y borra esta función.
function camera_shake_basico(_magnitud, _frames)
{
    shake_mag    = max(shake_mag, _magnitud);
    shake_frames = max(shake_frames, _frames);
}
```

```gml
// ---------------------------------------------------------------------------
// objCamera — End Step  (debe ir en End Step: se ejecuta DESPUÉS de moverse)
// ---------------------------------------------------------------------------
if (!instance_exists(objPlayer)) exit;

var _vw = camera_get_view_width(cam);
var _vh = camera_get_view_height(cam);

// --- 1. Look-ahead: anticipar hacia dónde mira el jugador -------------------
var _look = clamp(objPlayer.vel_x / MOVE_SPEED_MAX, -1, 1) * CAM_LOOKAHEAD;

// --- 2. Deadzone ------------------------------------------------------------
// Solo empujamos el objetivo cuando el jugador sale de la caja central.
var _px = objPlayer.x + _look;
var _py = objPlayer.y;

var _dz_left   = cam_target_x - CAM_DEADZONE_W * 0.5;
var _dz_right  = cam_target_x + CAM_DEADZONE_W * 0.5;
var _dz_top    = cam_target_y - CAM_DEADZONE_H * 0.5;
var _dz_bottom = cam_target_y + CAM_DEADZONE_H * 0.5;

if (_px < _dz_left)   cam_target_x -= (_dz_left   - _px);
if (_px > _dz_right)  cam_target_x += (_px        - _dz_right);
if (_py < _dz_top)    cam_target_y -= (_dz_top    - _py);
if (_py > _dz_bottom) cam_target_y += (_py        - _dz_bottom);

// --- 3. Limitar a los bordes de la room ------------------------------------
cam_target_x = clamp(cam_target_x, _vw * 0.5, room_width  - _vw * 0.5);
cam_target_y = clamp(cam_target_y, _vh * 0.5, room_height - _vh * 0.5);

// --- 4. Suavizado -----------------------------------------------------------
var _cx = lerp(camera_get_view_x(cam), cam_target_x - _vw * 0.5, CAM_SMOOTH);
var _cy = lerp(camera_get_view_y(cam), cam_target_y - _vh * 0.5, CAM_SMOOTH);

// --- 5. Shake (ruido aleatorio, decreciente) --------------------------------
if (shake_frames > 0)
{
    var _decay = shake_frames / max(shake_frames, 1);
    var _off_x = irandom_range(-shake_mag, shake_mag);
    var _off_y = irandom_range(-shake_mag, shake_mag);
    _cx += _off_x;
    _cy += _off_y;

    shake_frames--;
    if (shake_frames <= 0) shake_mag = 0;
}

camera_set_view_pos(cam, round(_cx), round(_cy));
```

> `round()` en la posición final es importante: sin él, la cámara baila en
> posiciones sub-píxel y los tiles del fondo parpadean.

### 5.8 `objPlatformMoving` — plataforma móvil

```gml
// ---------------------------------------------------------------------------
// objPlatformMoving — Create
// ---------------------------------------------------------------------------
// Se mueve por un path o por velocidad constante. Con path es más fácil:
path_start(pathPlat, SPEED, path_action_reverse, true);
```

```gml
// ---------------------------------------------------------------------------
// objPlatformMoving — Step (si no usas paths, mueve a mano)
// ---------------------------------------------------------------------------
x += move_dx;
y += move_dy;

// Invertir en los extremos
if (x < x_min || x > x_max) move_dx *= -1;
if (y < y_min || y > y_max) move_dy *= -1;
```

---

## 6. Gestión del estado del jugador

El estado del jugador va en un **struct**, no en variables sueltas del objeto.
Razón: cuando el jugador cambia de room, el objeto se destruye; el struct
puede vivir en un `global` y sobrevivir.

```gml
// ---------------------------------------------------------------------------
// scr_player_stats — constructor del estado persistente del jugador
// ---------------------------------------------------------------------------
function PlayerStats() constructor
{
    // --- Vitales ---
    hp          = 5;
    hp_max      = 5;
    invuln_time = 0;      // frames restantes de invulnerabilidad

    // --- Progresión ---
    coins       = 0;
    deaths      = 0;
    level       = 1;
    xp          = 0;

    // --- Habilidades desbloqueadas (para un metroidvania) ---
    can_double_jump  = false;
    can_dash         = false;
    can_wall_jump    = false;

    // --- Posición de respawn ---
    spawn_x = 0;
    spawn_y = 0;
    spawn_room = noone;

    /// @desc Aplica daño. Devuelve true si el golpe entra.
    take_damage = function(_amount)
    {
        if (invuln_time > 0) return false;

        hp -= _amount;
        invuln_time = 60;         // 1 segundo a 60 fps

        if (hp <= 0) { hp = 0; return true; }
        return true;
    };

    /// @desc Decrementa la invulnerabilidad. Llamar una vez por frame.
    tick = function()
    {
        if (invuln_time > 0) invuln_time--;
    };

    /// @desc Guarda el punto de respawn.
    set_spawn = function(_x, _y, _room)
    {
        spawn_x    = _x;
        spawn_y    = _y;
        spawn_room = (_room == noone) ? room : _room;
    };

    heal = function(_amount)
    {
        hp = min(hp + _amount, hp_max);
    };

    /// @desc Serializa a un struct plano, listo para json_stringify().
    serialize = function()
    {
        return {
            hp:               hp,
            hp_max:           hp_max,
            coins:            coins,
            deaths:           deaths,
            level:            level,
            xp:               xp,
            can_double_jump:  can_double_jump,
            can_dash:         can_dash,
            can_wall_jump:    can_wall_jump,
            spawn_x:          spawn_x,
            spawn_y:          spawn_y,
            spawn_room:       (spawn_room == noone) ? -1 : room_get_name(spawn_room)
        };
    };

    /// @desc Reconstruye desde un struct cargado de JSON.
    static deserialize = function(_data)
    {
        var _s = new PlayerStats();
        _s.hp             = _data[$ "hp"];
        _s.hp_max         = _data[$ "hp_max"];
        _s.coins          = _data[$ "coins"];
        _s.deaths         = _data[$ "deaths"];
        _s.level          = _data[$ "level"];
        _s.xp             = _data[$ "xp"];
        _s.can_double_jump = _data[$ "can_double_jump"];
        _s.can_dash        = _data[$ "can_dash"];
        _s.can_wall_jump   = _data[$ "can_wall_jump"];
        _s.spawn_x        = _data[$ "spawn_x"];
        _s.spawn_y        = _data[$ "spawn_y"];

        var _room_name = _data[$ "spawn_room"];
        _s.spawn_room = (_room_name == -1) ? noone : asset_get_index(_room_name);

        return _s;
    };
}
```

Uso global (en `objGame`, persistente):

```gml
// objGame — Create
if (!variable_global_exists("player_stats"))
{
    global.player_stats = new PlayerStats();
}
```

Y en el jugador:

```gml
// objPlayer — Create, sustituyendo `stats = new PlayerStats();`
stats = global.player_stats;

// objPlayer — Step
stats.tick();
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Usar `speed`/`vspeed`/`gravity` built-ins | El personaje se mueve sin que tú lo pidas; `gravity` sigue aplicándose en rooms nuevas | Usa variables propias: `vel_x`, `vel_y`, `grav` |
| Detectar suelo con `place_meeting(x, y+1, obj)` justo tras moverte | Falsos negativos en pendientes | Llama a `move_and_collide()` y comprueba `on_ground` **al final** del Step |
| No limitar `max_x` en `move_and_collide()` | El personaje acelera al deslizarse por pendientes | Pasa `MOVE_SPEED_MAX` en el argumento 7 |
| Aplicar `lerp` sin corte en cero | El personaje nunca se detiene del todo | `if (abs(vel_x) < 0.05) vel_x = 0;` |
| Gravedad igual al subir y al bajar | El salto se siente plano y "de globo" | Usa `GRAV_RISE`, `GRAV_FALL` y `GRAV_RISE_FAST` |
| Leer input en el Step después de mover | Un frame de latencia perceptible | Lee el input en **Begin Step** o al inicio del Step, siempre antes de mover |
| Dibujar la cámara en el Step | La cámara va un frame por detrás del jugador | Mueve la cámara en **End Step** |
| No redondear la posición de la cámara | Los tiles de fondo parpadean | `round()` en `camera_set_view_pos()` |
| Poner `objPlatform` en `move_and_collide()` | El jugador choca con la plataforma desde abajo | One-way solo en `resolve_one_way()` |
| Crear el jugador en cada room sin persistencia | Las monedas y la vida se resetean al cambiar de nivel | Guarda `global.player_stats` y haz `objGame` persistente |
| Origen del sprite en el centro | El personaje flota o se hunde al aplastarse | Origen en **Bottom Centre** para el squash & stretch |
| Colisión precisa en tiles cuadrados | Coste altísimo de CPU en rooms grandes | Máscara "Rectangle" y objetos `objSolid` invisibles estirados |

---

## 8. Cómo escalarlo

Orden recomendado de incorporación de mecánicas:

1. **Doble salto** — una variable `jumps_left` y resetearla al aterrizar.
   Es la mecánica más rentable del plataformas.
2. **Dash** — estado nuevo con `state_timer`: fija `vel_x` a un valor alto,
   ignora la gravedad durante N frames y deja un rastro de partículas.
3. **Wall slide / wall jump** — detecta `place_meeting(x ± 1, y, objSolid)`;
   limita `vel_y` mientras estás pegado y permite impulsarte en diagonal.
4. **Enemigos** — reutiliza `objEntity` como padre. Añade `objEnemyWalker` que
   invierte dirección al detectar un borde (`!place_meeting(x + facing*8, y+1, objSolid)`).
5. **Daño y respawn** — `stats.take_damage()`, transición a `PlayerState.hurt`,
   respawn en `stats.spawn_x/spawn_y`.
6. **Rooms encadenadas** — `room_goto_next()` con un objeto `objTransition`
   persistente que haga fade a negro.
7. **Checkpoints** — `objCheckpoint` con `stats.set_spawn()`.
8. **Tilemaps de colisión** — migra de `objSolid` invisible a
   `tilemap_get_at_pixel()` cuando el nivel tenga miles de celdas (ver receta 05).
9. **Cinemáticas** — secuencias con `TweenHandle` sobre la cámara.

**Cuándo pasar a otra receta:** cuando tengas doble salto + dash + un enemigo
que te mata, ya tienes el 60 % de la destreza técnica que necesita un
metroidvania. Salta entonces a la receta 06.

---

## 9. Fuentes

- **Make Your First Platformer in GameMaker** (Gurpreet S. Matharoo / Gus, 5 ene 2025) —
  https://gamemaker.io/tutorials/your-first-platformer
- **How To Make Platformer Movement In GameMaker** (Gurpreet S. Matharoo, 26 jun 2023) —
  https://gamemaker.io/tutorials/easy-platformer
- **How To Move And Collide In GameMaker** (Gurpreet S. Matharoo, 30 jun 2023) —
  https://gamemaker.io/tutorials/easy-move-collide
- **Ultimate Guide To Collision Functions** (tutorial oficial) —
  https://gamemaker.io/tutorials/collision-functions
- Manual oficial — `move_and_collide` —
  https://manual.gamemaker.io/monthly/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement_And_Collisions/move_and_collide.htm
- Manual oficial — Movimiento y colisiones —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement_And_Collisions.htm
- Manual oficial — Cámaras y viewports —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Cameras_And_Display/Cameras_And_Viewports.htm
- Manual oficial — Construcciones de lenguaje (`enum`, `constructor`, `static`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Language_Features.htm
