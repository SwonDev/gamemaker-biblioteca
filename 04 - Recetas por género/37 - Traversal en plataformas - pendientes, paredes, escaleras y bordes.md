# 37 — Traversal en plataformas: pendientes, paredes, escaleras y bordes

> **Dificultad:** media-alta · **Extiende** [`04 · 01 — Plataformas 2D`](./01%20-%20Plataformas%202D.md)
> Este documento **no es un plataformas nuevo**: es la caja de herramientas de *traversal*
> (moverse por el espacio) que le falta al `objPlayer` de `04·01` para dejar de sentirse como
> una demo — pendientes de verdad, paredes, bordes, escaleras, cuerdas y agua. **No repite**
> el movimiento base, la gravedad, el coyote time, el jump buffer, las plataformas one-way ni
> las móviles: todo eso ya está resuelto en `04·01 §4-§5` y aquí se **reutiliza tal cual**.

---

## 1 · Visión general

Un plataformas se nota "barato" no por el arte, sino por lo que el jugador **no puede hacer**
contra el escenario: resbalar en vez de teletransportarse sobre una rampa, colgarse de un
saliente en vez de rebotar contra él, que un salto que rozó la esquina de un hueco cuente como
acierto. Son detalles de fricción entre el cuerpo del jugador y la geometría del nivel — por
eso "traversal" es su propio tema de diseño, separado de saltar y correr.

**Lo que añade esta receta, todo enganchado al `objPlayer` y a la `enum PlayerState` de
`04·01 §5.1` y `§5.5`:**

| Sistema | Qué resuelve | Sección |
|---|---|---|
| Pendientes de verdad | Ángulo máximo escalable, no despegar en cada cresta, heightmap por tile | 3.1 |
| Wall slide / wall jump | Detección de pared, frenado al deslizar, salto con *lockout*, anti-escalada | 3.2 |
| Wall run | Correr un tramo corto por una pared vertical | 3.3 |
| Corrección de esquina | El empujón de 1-4 px que hace que un salto "raspado" cuente | 3.4 |
| Agarre de bordes (*ledge grab*) | Colgarse de un saliente, subir o soltarse | 3.5 |
| Agacharse | Cambio de `mask_index` sin atravesar techos | 3.6 |
| Escaleras | Entrar/salir, ignorar gravedad, bajar desde una one-way | 3.7 |
| Cuerdas y lianas | Balanceo sobre la simulación de Verlet que ya existe en la biblioteca | 3.8 |
| Nadar | Gravedad reducida, brazada, aliento | 3.9 |
| Empuje de cajas por rejilla | Variante *sokoban*, con deshacer | 3.10 |

**Lo que NO cubre y dónde está:** movimiento horizontal, gravedad asimétrica, coyote time, jump
buffer, salto variable y `move_and_collide()` básico → `04·01 §4.1-§4.6`. Plataformas one-way y
móviles → `04·01 §4.7-§4.8, §5.4, §5.8`. Cámara → `04·01 §4.9, §5.7`. Doble salto y dash →
[`04·06 §5.4`](./06%20-%20Metroidvania.md). Hitboxes de combate → [`04·30`](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md).
Elegir la FORMA de la máscara de colisión → [`01·08 §4`](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md).

---

## 2 · Arquitectura y método

### 2.1 Un jugador, muchos estados: el orden de comprobación importa

Con nueve sistemas nuevos, varias condiciones pueden ser ciertas a la vez (estás en el agua Y
hay una escalera ahí mismo). Sin un orden fijo, el jugador "parpadea" entre estados cada frame.
Usa esta prioridad, de más a menos exclusiva — la primera condición que se cumpla gana y las
demás ni se comprueban ese frame:

```
1. hurt                     (ya existe en 04·01 — nada la interrumpe)
2. swim   (en_agua)         → el agua anula suelo, paredes y escaleras
3. climb  (escalera/cuerda) → solo fuera del agua
4. hang   (borde agarrado)  → solo en el aire, y solo si no estás ya trepando
5. slide  (pared)           → solo en el aire, y solo si no hay un borde que agarrar
6. crouch                   → solo en el suelo
7. idle / run / jump / fall (la base de 04·01, sin cambios)
```

Esto **no** es una función nueva: es el orden en el que **tú** escribes los `if` que llaman a
`player_state_set()` a lo largo del Step. Respétalo y las transiciones dejan de competir entre
sí.

### 2.2 Extender el enum y el switch de 04·01 §5.5

No hay una segunda `enum PlayerState` ni una segunda `function player_state_set()`: GameMaker no
permite declarar la misma función dos veces en un proyecto. Lo que sigue son los **añadidos**
que insertas en el código que ya tienes.

```gml
// ---------------------------------------------------------------------------
// scr_player_states — AMPLIACIÓN de 04·01 §5.5.
// ---------------------------------------------------------------------------

// 1) El enum: los estados nuevos SIEMPRE al final. Si alguna vez serializas
//    `state` como número (un replay, netcode, una demo grabada), reordenar el
//    enum cambia el valor numérico de cada estado y rompe esa serialización.
//    Sustituye tu línea por esta:
enum PlayerState { idle, run, jump, fall, hurt, crouch, slide, hang, climb, swim }

// 2) Dentro de player_state_set(_new), en el switch (_new) que ya tienes,
//    añade estos casos (no toques los que ya existen):
        case PlayerState.slide: squash_x = 1.10; squash_y = 0.90; break;
        case PlayerState.hang:  vel_x = 0; vel_y = 0;              break;
        case PlayerState.climb: vel_x = 0; vel_y = 0;              break;
        case PlayerState.swim:  squash_x = 1.05; squash_y = 0.95;  break;

// 3) Dentro de update_player_state(), en el switch (state), añade:
        case PlayerState.crouch:
            if (!on_ground) { mask_index = sprPlayerMask; player_state_set(PlayerState.fall); }
            break;

        case PlayerState.slide:
            if (on_ground)          player_state_set(PlayerState.idle);
            else if (wall_dir == 0) player_state_set(PlayerState.fall);
            break;

        case PlayerState.hang:
            break;   // las salidas (subir/soltar) están en 3.5: cambian el estado ellas mismas

        case PlayerState.climb:
            break;   // las salidas (soltar/saltar) están en 3.7 y 3.8

        case PlayerState.swim:
            if (!en_agua) player_state_set(PlayerState.fall);
            break;

// 4) Dentro de apply_state_sprite(), en el switch (state), añade:
        case PlayerState.crouch: _spr = sprPlayerCrouch;    break;
        case PlayerState.slide:  _spr = sprPlayerWallSlide; break;
        case PlayerState.hang:   _spr = sprPlayerHang;      break;
        case PlayerState.climb:  _spr = sprPlayerClimb;     break;
        case PlayerState.swim:   _spr = sprPlayerSwim;      break;
```

### 2.3 Variables nuevas del Create

Todas las variables que usan las secciones siguientes, en un único bloque para copiar una vez
(van **después** de las de `04·01 §5.1`):

```gml
// ---------------------------------------------------------------------------
// objPlayer — Create (AÑADIDOS de esta receta)
// ---------------------------------------------------------------------------
// Pendientes (3.1)
ground_angle  = 0;                                    // grados; 0 = suelo llano
tilemap_suelo = layer_tilemap_get_id("Tiles_Collision");

// Wall slide / wall jump / wall run (3.2, 3.3)
wall_dir       = 0;          // -1 izquierda, 1 derecha, 0 ninguna
wall_stamina   = WALL_STAMINA_MAX;
wall_last_id   = noone;
wall_jump_lock = 0;
wallrun_timer  = WALLRUN_FRAMES_MAX;

// Escaleras y cuerdas (3.7, 3.8)
en_cuerda = noone;

// Nadar (3.9)
tilemap_agua = layer_tilemap_get_id("Tiles_Agua");
en_agua      = false;
aliento      = AIRE_MAX;
```

Y las constantes, junto a las de `04·01 §5.0` (`scr_config`):

```gml
// ---------------------------------------------------------------------------
// scr_config — AÑADIDOS de esta receta
// ---------------------------------------------------------------------------
// Pendientes
#macro SLOPE_ANGLE_MAX     50     // grados; por encima se trata como pared, no como rampa
#macro SLOPE_SNAP_UP       4      // px de "escalón" que se sube de golpe
#macro GROUND_SNAP_MIN     6      // ventana mínima de pegado al suelo, aunque vel_x = 0

// Wall slide / wall jump / wall run
#macro WALL_CHECK_DIST       2
#macro WALL_SLIDE_SPEED_MAX  1.5
#macro WALL_STAMINA_MAX      45   // frames de agarre antes de que resbales solo
#macro WALL_JUMP_SPEED_X     4.5
#macro WALL_JUMP_SPEED_Y     10.5
#macro WALL_JUMP_LOCK_FRAMES 10
#macro WALLRUN_FRAMES_MAX    24
#macro WALLRUN_FALL_MAX      0.8

// Corrección de esquina
#macro CORNER_CORRECTION_PX  4

// Agarre de bordes
#macro LEDGE_OFFSET_X  10
#macro LEDGE_OFFSET_Y  18

// Escaleras
#macro LADDER_SPEED  2.5

// Nadar
#macro AIRE_MAX           600   // 10 s a 60 fps
#macro AIRE_RECUPERACION  4
#macro SWIM_GRAVITY       0.10
#macro SWIM_FALL_MAX      1.4
#macro SWIM_STROKE_SPEED  2.2
#macro SWIM_SPEED_MAX     2.0
```

### 2.4 Dónde entra cada sistema en el bucle de 04·01 §3

El bucle central de `04·01 §3` tiene 12 pasos numerados. Esta tabla dice dónde se engancha cada
sistema nuevo — así cada sección de más abajo solo habla de su propia lógica, no de fontanería:

| Sistema | Se inserta... |
|---|---|
| Agacharse (3.6) | Junto al paso 1 (input), antes de leer el resto |
| Pendientes (3.1) | Entre el paso 3 (horizontal) y el paso 5 (gravedad) |
| Wall slide / wall jump (3.2) | Detección entre el paso 3 y el 5; el salto amplía el paso 4 |
| Wall run (3.3) | Junto al bloque de wall slide |
| Corrección de esquina (3.4) | Justo después del paso 6 (`move_and_collide`), antes de anular `vel_y` |
| Agarre de bordes (3.5) | Dentro del `case PlayerState.fall` del paso 11 (`update_player_state`) |
| Escaleras (3.7) | Antes del paso 3: si `state == PlayerState.climb`, sustituye los pasos 3-10 |
| Cuerdas (3.8) | Antes del paso 3: si `en_cuerda != noone`, el objeto Cuerda controla `x`/`y` y el resto del Step se salta con `exit` |
| Nadar (3.9) | Sustituye el paso 5 (gravedad) mientras `state == PlayerState.swim` |
| Empuje por rejilla (3.10) | Modo de control alternativo: sustituye el Step entero en rooms de puzle |

---

## 3 · Sistemas y su código

### 3.1 Pendientes de verdad

**Lo que ya hace `move_and_collide()` sin que hagas nada.** El manual oficial lo dice de forma
explícita: *"Permite que la instancia se mueva al recorrer pendientes o escalones pequeños que,
de otro modo, le impedirían avanzar"* — siempre que la máscara del suelo esté en modo
*"Rectangle with Rotation"* (`04·01 §4.6`). Para rampas suaves de un par de grados esto basta y
sobra.

**Lo que NO hace:** no te da un ángulo (`image_angle` sigue en 0), no te frena al subir ni te
acelera al bajar, y sobre todo **no te pega al suelo**: si vas rápido y la pendiente baja más
deprisa que tu gravedad por frame, sales volando en cada cresta como si hubiera un escalón
invisible. Eso solo se arregla con una comprobación explícita cada frame — un *sensor de
suelo*, en vocabulario de la Sonic Physics Guide.

**El truco de fondo: velocidad "de suelo", no horizontal.** La Sonic Physics Guide separa la
velocidad en dos capas: mientras estás en el suelo, no llevas cuenta de `X Speed`/`Y Speed` por
separado, sino de una única `Ground Speed` a lo largo de la pendiente; `X Speed`/`Y Speed` se
*derivan* de ella cada frame:

```
X Speed = Ground Speed * cos(Ground Angle)
Y Speed = Ground Speed * -sin(Ground Angle)
```

En GML esto es literalmente `lengthdir_x`/`lengthdir_y`: `lengthdir_y(len, dir)` ya lleva el
signo negativo del seno incorporado, así que la fórmula de arriba es, sin tocar nada,
`lengthdir_x(ground_speed, angulo)` y `lengthdir_y(ground_speed, angulo)`.

**El heightmap por tile (estilo Sonic).** Para pendientes reales (no solo la rotación automática
de la máscara) se guarda, por cada tile de rampa, un **array de 16 alturas** (una por columna de
píxel) más su ángulo — es la técnica descrita en *SPG: Solid Tiles §Height Array*. Un tile vacío
o totalmente sólido no necesita entrada: se resuelve con la colisión normal.

```gml
// ---------------------------------------------------------------------------
// scr_slope_heightmap — perfil de alturas por tile (Height Array, estilo Sonic)
// ---------------------------------------------------------------------------

/// @func slope_heightmap_registrar(_indice_tile, _alturas, _angulo)
/// @desc Asocia un tile de rampa con su perfil de alturas.
/// @param {Real}  _indice_tile  Índice del tile en el tile set (Room Editor, o
///                              `tile_get_index(tilemap_get(tm, cx, cy))` en debug).
/// @param {Array<Real>} _alturas  16 valores (0..16), izquierda→derecha, la
///                                altura de suelo en cada columna del tile.
/// @param {Real}  _angulo       Ángulo en grados de la superficie que dibuja ese perfil.
function slope_heightmap_registrar(_indice_tile, _alturas, _angulo)
{
    if (!variable_global_exists("slope_heightmap")) global.slope_heightmap = {};
    global.slope_heightmap[$ string(_indice_tile)] = { alturas: _alturas, angulo: _angulo };
}

/// @func pendiente_datos(_indice_tile)
/// @desc `undefined` si el tile no es una rampa registrada — el accesor `[$ ]`
///       de un struct devuelve `undefined` para una clave que no existe, no da
///       error (a diferencia de leer un array fuera de rango, que SÍ lo da).
function pendiente_datos(_indice_tile)
{
    if (!variable_global_exists("slope_heightmap")) return undefined;
    return global.slope_heightmap[$ string(_indice_tile)];
}

/// @func pendiente_bajo_punto(_tilemap, _px, _py)
/// @desc Busca la superficie de una rampa bajo el punto dado.
/// @returns {Struct|Undefined} { y: <mundo>, angulo } o `undefined` si esa
///          columna de tile no es una rampa (tile plano, sólido o vacío).
function pendiente_bajo_punto(_tilemap, _px, _py)
{
    var _tw = tilemap_get_tile_width(_tilemap);
    var _th = tilemap_get_tile_height(_tilemap);

    var _celda_x = tilemap_get_cell_x_at_pixel(_tilemap, _px, _py);
    var _celda_y = tilemap_get_cell_y_at_pixel(_tilemap, _px, _py);

    var _dato   = tilemap_get(_tilemap, _celda_x, _celda_y);
    var _indice = tile_get_index(_dato);
    var _perfil = pendiente_datos(_indice);
    if (is_undefined(_perfil)) return undefined;

    var _columna = clamp(floor(_px) - floor(_celda_x * _tw), 0, _tw - 1);
    var _altura  = _perfil.alturas[_columna];
    if (_altura <= 0) return undefined;      // columna vacía dentro del propio tile

    return { y: (_celda_y * _th) + (_th - _altura), angulo: _perfil.angulo };
}

// Ejemplo de registro (los índices son los de TU tile set, no un símbolo del runtime):
slope_heightmap_registrar(TILE_RAMPA_45,      [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], 45);
slope_heightmap_registrar(TILE_RAMPA_22_BAJA, [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7],       22.5);
slope_heightmap_registrar(TILE_RAMPA_22_ALTA, [7,7,8,8,9,9,10,10,11,11,12,12,13,13,14,14], 22.5);
```

**Ángulo máximo, pegado al suelo en bajada y `image_angle`, todo en una función:**

```gml
// ---------------------------------------------------------------------------
// objPlayer — resolver_pendiente(). Llamar entre el paso 3 y el paso 5 (ver 2.4).
// ---------------------------------------------------------------------------
function resolver_pendiente()
{
    if (vel_y < 0) return;   // subiendo (saltando): la pendiente no pinta nada

    // La ventana de "pegado" crece con la velocidad — igual que en SPG: Slope
    // Collision, donde el límite positivo es min(abs(X Speed) + 4, 14). Aquí se
    // adapta a la escala de velocidades de 04·01 (MOVE_SPEED_MAX = 4).
    var _rango_abajo = max(abs(vel_x) + 4, GROUND_SNAP_MIN);
    var _suelo = pendiente_bajo_punto(tilemap_suelo, x, bbox_bottom);

    if (is_undefined(_suelo))
    {
        if (on_ground) ground_angle = 0;   // suelo llano o aire: sin pendiente
        return;
    }

    var _distancia = _suelo.y - bbox_bottom;   // + = superficie debajo · - = ya solapando

    if (_distancia < -SLOPE_SNAP_UP || _distancia > _rango_abajo) return;   // demasiado lejos
    if (abs(_suelo.angulo) > SLOPE_ANGLE_MAX) return;                      // es pared, no rampa

    // Ground Speed: reproyecta la velocidad horizontal ya calculada (paso 3,
    // aceleración/fricción sin tocar) sobre la pendiente encontrada.
    var _ground_speed = vel_x / dcos(_suelo.angulo);
    vel_x = lengthdir_x(_ground_speed, _suelo.angulo);
    vel_y = lengthdir_y(_ground_speed, _suelo.angulo);

    y            += _distancia;         // snap: pega los pies a la superficie
    ground_angle  = _suelo.angulo;
    on_ground     = true;
}
```

```gml
// objPlayer — Draw (añadido: inclinar el sprite con la pendiente)
// draw_sprite_ext() de 04·01 §5.6 ya recibe `image_angle` como parámetro — solo
// hace falta escribirlo. El origen del sprite en "Bottom Centre" (ya exigido
// para el squash & stretch) hace que la rotación pivote sobre los pies.
image_angle = on_ground ? ground_angle : 0;
```

> ⚠️ Esta técnica cubre rampas normales de un plataformas (hasta `SLOPE_ANGLE_MAX`). No
> reproduce la colisión de 360° con paredes y techos de un Sonic real (correr por un rizo) —
> eso es un sistema de sensores por cuadrante bastante más grande y queda fuera de esta receta.

### 3.2 Wall slide y wall jump

Detección con margen, frenado al deslizar, salto con *lockout* de input y un límite de aguante
para que no se pueda escalar la misma pared para siempre — la estructura está adaptada de
`Player.cs` de *Celeste* (`WallJumpCheck`/`WallJump`, líneas 1731-1780; ver Fuentes), con los
números reescalados a las constantes de `04·01 §5.0`.

```gml
// ---------------------------------------------------------------------------
// objPlayer — detectar_pared(). Llamar entre el paso 3 y el paso 5 (ver 2.4).
// ---------------------------------------------------------------------------
function detectar_pared()
{
    if (on_ground) return 0;

    var _hay_der = place_meeting(x + WALL_CHECK_DIST, y, objSolid);
    var _hay_izq = place_meeting(x - WALL_CHECK_DIST, y, objSolid);

    if (_hay_der && !_hay_izq) return 1;
    if (_hay_izq && !_hay_der) return -1;
    return 0;
}
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step, fragmento NUEVO (wall slide). Va justo después de
// resolver_pendiente() y detectar_pared(), antes del paso 5 (gravedad).
// ---------------------------------------------------------------------------
wall_dir = detectar_pared();

var _empuja_pared = (wall_dir != 0) && (sign(_input_x) == wall_dir);

if (_empuja_pared && vel_y > 0 && wall_stamina > 0)
{
    if (state != PlayerState.slide) player_state_set(PlayerState.slide);

    vel_y = min(vel_y, WALL_SLIDE_SPEED_MAX);   // frena la caída, no la detiene del todo

    // Anti-escalada: agarrarte a la MISMA pared no rellena el aguante. Solo se
    // recupera tocando suelo o agarrando una pared distinta (ver más abajo).
    var _pared_actual = instance_place(x + wall_dir * WALL_CHECK_DIST, y, objSolid);
    if (_pared_actual != wall_last_id)
    {
        wall_stamina = WALL_STAMINA_MAX;
        wall_last_id = _pared_actual;
    }
    else
    {
        wall_stamina -= 1;
    }
}
else if (on_ground)
{
    wall_stamina = WALL_STAMINA_MAX;
    wall_last_id = noone;
}
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step. AMPLÍA el paso 4 de 04·01 §5.3: añade esta rama ANTES del
// "if (buffer_timer > 0 && coyote_timer > 0)" que ya tienes (el salto normal
// sigue exactamente igual, sin tocarlo, como rama `else if`).
// ---------------------------------------------------------------------------
if (buffer_timer > 0 && wall_dir != 0 && !on_ground)
{
    vel_x = -wall_dir * WALL_JUMP_SPEED_X;
    vel_y = -WALL_JUMP_SPEED_Y;
    buffer_timer   = 0;
    wall_jump_lock = WALL_JUMP_LOCK_FRAMES;   // ver más abajo: ignora el input hacia la pared
    wall_dir       = 0;

    squash_x = 0.75; squash_y = 1.30;
    player_state_set(PlayerState.jump);
}
// else if (buffer_timer > 0 && coyote_timer > 0) { ...salto normal, sin cambios... }
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step. AMPLÍA el paso 1/3 de 04·01 §5.3: justo después de leer
// `_input_x` y antes de usarlo para la aceleración, el lockout lo sustituye.
// ---------------------------------------------------------------------------
if (wall_jump_lock > 0)
{
    wall_jump_lock--;
    _input_x = sign(vel_x);   // conserva el impulso de salida; ignora el mando un momento
}
```

> **Por qué el *lockout* importa:** sin él, mantener pulsado hacia la pared cancela el salto en
> el mismo frame en que sales de ella — el jugador nunca llega a despegarse. `WALL_JUMP_LOCK_FRAMES`
> (10 frames ≈ 0,16 s a 60 fps, el mismo orden de magnitud que `WallJumpForceTime` en Celeste)
> le da tiempo al impulso horizontal de sacarte del alcance de la pared antes de que el input
> vuelva a mandar.

### 3.3 Wall run

Una variante de nicho: correr un tramo corto por una pared vertical mientras se mantiene la
dirección hacia ella, con gravedad reducida durante un número de frames que solo se recarga al
tocar suelo (para que no sea infinito).

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step, junto al bloque de wall slide (3.2). Requiere apuntar
// hacia la pared, ir cayendo y no haber agotado el temporizador.
// ---------------------------------------------------------------------------
var _puede_wallrun = !on_ground && wall_dir == 0 && wallrun_timer > 0
                   && vel_y >= 0 && sign(_input_x) == facing
                   && place_meeting(x + facing * WALL_CHECK_DIST, y, objSolid);

if (_puede_wallrun)
{
    vel_y = min(vel_y, WALLRUN_FALL_MAX);
    wallrun_timer--;
}

if (on_ground) wallrun_timer = WALLRUN_FRAMES_MAX;
```

> ⚠️ A diferencia de 3.1 y 3.2, esta sección **no** está verificada contra una fuente primaria
> abierta en esta sesión (la referencia habitual es *Ori and the Blind Forest* / *Katana ZERO*,
> práctica de género, no un repositorio consultado). Trátala como punto de partida, no como
> receta cerrada.

### 3.4 Corrección de esquina (*corner correction*)

El empujón de unos pocos píxeles que evita que un salto que roza el borde de un hueco de tu
mismo ancho se sienta como una pared invisible. Adaptado de `Player.cs` de *Celeste*
(`UpwardCornerCorrection`, constante `= 4`, y el bucle de corrección en torno a las líneas
2587-2609; ver Fuentes): al chocar contra un techo mientras subes, se prueban desplazamientos
laterales de 1 a `CORNER_CORRECTION_PX` píxeles antes de aceptar el choque.

```gml
// ---------------------------------------------------------------------------
// objPlayer — corregir_esquina(). Llamar en el paso 6 de 04·01 §5.3, justo
// después de move_and_collide() y ANTES de poner vel_y = 0 por el impacto en Y.
// ---------------------------------------------------------------------------
/// @func corregir_esquina(_hubo_impacto_y)
/// @param {Bool} _hubo_impacto_y  true si move_and_collide() detectó choque vertical.
/// @returns {Bool} true si se corrigió la posición (no hace falta anular vel_y).
function corregir_esquina(_hubo_impacto_y)
{
    if (!_hubo_impacto_y || vel_y >= 0) return false;   // solo al chocar SUBIENDO

    var _dir = sign(vel_x);
    if (_dir == 0) _dir = 1;

    // Primero en la dirección en la que ya te mueves...
    for (var _i = 1; _i <= CORNER_CORRECTION_PX; _i++)
    {
        if (!place_meeting(x + _dir * _i, y - 1, objSolid))
        {
            x += _dir * _i;
            y -= 1;
            return true;
        }
    }
    // ...y si no cuela, en la contraria (cubre el caso vel_x == 0).
    for (var _i = 1; _i <= CORNER_CORRECTION_PX; _i++)
    {
        if (!place_meeting(x - _dir * _i, y - 1, objSolid))
        {
            x -= _dir * _i;
            y -= 1;
            return true;
        }
    }
    return false;
}
```

```gml
// objPlayer — Step, paso 6 de 04·01 §5.3, con la corrección insertada:
var _hit = move_and_collide(vel_x, vel_y, objSolid, 4, 0, 0, MOVE_SPEED_MAX, -1);

if (is_array(_hit))
{
    if (!is_undefined(_hit[0]) && instance_exists(_hit[0])) vel_x = 0;

    if (!is_undefined(_hit[1]) && instance_exists(_hit[1]))
    {
        if (!corregir_esquina(true))   // NUEVO: intenta la corrección antes de frenar
        {
            if (_hit[1] != noone && vel_y > 0 && !was_on_ground) { squash_x = 1.35; squash_y = 0.70; }
            vel_y = 0;
        }
    }
}
```

### 3.5 Agarre de bordes (*ledge grab*)

Dos sensores, como pide el diseño clásico: uno comprueba que la **mano** tiene sitio (no hay
sólido justo delante y arriba), el otro que hay **pared** justo debajo de esa mano — eso es lo
que distingue "hay un borde agarrable" de "hay un hueco en el que meter la mano".

```gml
// ---------------------------------------------------------------------------
// objPlayer — detectar_borde(). Solo tiene sentido cayendo (o cerca del ápice
// del salto: vel_y >= -1), nunca subiendo con fuerza.
// ---------------------------------------------------------------------------
/// @returns {Struct|Undefined} { pared, borde_y } o `undefined` si no hay borde.
function detectar_borde()
{
    if (on_ground || vel_y < -1) return undefined;

    var _mano_x = x + facing * LEDGE_OFFSET_X;
    var _mano_y = bbox_top + LEDGE_OFFSET_Y;

    if (place_meeting(_mano_x, _mano_y, objSolid)) return undefined;   // la mano chocaría: no hay hueco

    var _pared = instance_place(_mano_x, _mano_y + TILE_SIZE, objSolid);
    if (_pared == noone) return undefined;                            // nada debajo: es un hueco, no un borde

    return { pared: _pared, borde_y: _pared.bbox_top };
}
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — dentro del case PlayerState.fall de update_player_state()
// (04·01 §5.5, paso 11 del bucle). Añade esta comprobación AL PRINCIPIO del
// case, antes de la que ya existe para aterrizar.
// ---------------------------------------------------------------------------
        case PlayerState.fall:
            var _borde = detectar_borde();
            if (!is_undefined(_borde) && puede_agarrar)      // puede_agarrar: ver 04·06 §5.4
            {
                var _halfwidth = bbox_right - x;              // asume máscara simétrica
                y = _borde.borde_y - LEDGE_OFFSET_Y;
                x = (facing == 1) ? (_borde.pared.bbox_left - _halfwidth)
                                   : (_borde.pared.bbox_right + _halfwidth);
                player_state_set(PlayerState.hang);
                break;
            }
            if (on_ground)   // ...aquí sigue tal cual el aterrizaje que ya tenías
            {
                player_state_set(abs(vel_x) > 0.3 ? PlayerState.run : PlayerState.idle);
            }
            break;
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step, fragmento NUEVO: qué hacer colgado (case PlayerState.hang
// de update_player_state, ver 2.2). Sustituye TODO el bucle de movimiento
// (pasos 3-10 de 04·01 §5.3) mientras estés en este estado.
// ---------------------------------------------------------------------------
if (state == PlayerState.hang)
{
    vel_x = 0; vel_y = 0;

    if (_jump_pressed || keyboard_check_pressed(vk_up) || keyboard_check_pressed(ord("W")))
    {
        y -= LEDGE_OFFSET_Y + 2;      // sacar los pies del hueco...
        x += facing * 4;              // ...y ponerlos sobre la plataforma
        player_state_set(PlayerState.idle);
    }
    else if (keyboard_check_pressed(vk_down) || _input_x == -facing)
    {
        player_state_set(PlayerState.fall);   // soltarse a propósito
    }

    apply_state_sprite();
    exit;   // no ejecutes el resto del Step: estás colgado, no cayendo
}
```

> ⚠️ El diseño de los dos sensores es práctica estándar del género (*Prince of Persia*,
> *Hollow Knight*), pero esta implementación concreta no está copiada de ningún repositorio
> abierto en esta sesión — es una traducción a GML del patrón, no una cita textual. Cierra el
> hueco que dejaban `puede_agarrar`/`agarrado` en [`04·06 §5.4`](./06%20-%20Metroidvania.md),
> declarados ahí pero sin comportamiento.

### 3.6 Agacharse

Cambio de `mask_index` con comprobación de techo **antes** de levantarse — el error clásico es
levantarte primero y descubrir que estabas bajo una plataforma, momento en el que ya estás medio
dentro de ella.

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step, junto al paso 1 (input) de 04·01 §5.3.
// ---------------------------------------------------------------------------
var _pide_agachar = keyboard_check(vk_down) || keyboard_check(ord("S"));

if (_pide_agachar && on_ground && state != PlayerState.crouch)
{
    player_state_set(PlayerState.crouch);
    mask_index = sprPlayerCrouchMask;
}
else if (!_pide_agachar && state == PlayerState.crouch)
{
    mask_index = sprPlayerMask;                 // prueba con la máscara de pie...

    if (place_meeting(x, y, objSolid))
    {
        mask_index = sprPlayerCrouchMask;       // ...hay techo encima: sigue agachado
    }
    else
    {
        player_state_set(abs(vel_x) > 0.3 ? PlayerState.run : PlayerState.idle);
    }
}
```

> `sprPlayerMask` y `sprPlayerCrouchMask` son sprites dedicados a la máscara (no al dibujado),
> siguiendo la recomendación de máscara **fija** para el jugador que ya está en
> [`13·04 §3.9`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/04%20-%20Animación%20de%20sprites,%20Sequences%20y%20Animation%20Curves.md).
> No cambies `mask_index` al sprite de animación actual: si el fotograma de "agacharse" tiene un
> píxel más alto que otro, la máscara "respira" con la animación y las colisiones se vuelven
> inconsistentes.

### 3.7 Escaleras

Estado propio: ignora la gravedad, centra al jugador en la columna de la escalera, y permite
bajar a través de una plataforma one-way que esté justo encima (el caso típico de una escalera
que arranca en la planta de abajo, justo bajo el borde de una plataforma).

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step, antes del paso 3 de 04·01 §5.3. `objLadder` es una franja
// invisible de la anchura de la escalera, sin colisión sólida (no se pasa
// a move_and_collide: sirve solo para detectar "estás dentro de una").
// ---------------------------------------------------------------------------
var _en_escalera  = place_meeting(x, y, objLadder);
var _quiere_subir = keyboard_check(vk_up)   || keyboard_check(ord("W"));
var _quiere_bajar = keyboard_check(vk_down) || keyboard_check(ord("S"));

if (_en_escalera && (_quiere_subir || _quiere_bajar) && state != PlayerState.climb)
{
    player_state_set(PlayerState.climb);
    x = round(x / TILE_SIZE) * TILE_SIZE + TILE_SIZE * 0.5;   // centrar en la columna
}

if (state == PlayerState.climb)
{
    if (!_en_escalera)
    {
        player_state_set(PlayerState.fall);
    }
    else if (buffer_timer > 0)
    {
        // Saltar te suelta de la escalera con un pequeño impulso, en cualquier dirección.
        vel_y = -JUMP_SPEED * 0.7;
        buffer_timer = 0;
        player_state_set(PlayerState.fall);
    }
    else
    {
        vel_x     = 0;
        vel_y     = (_quiere_subir - _quiere_bajar) * LADDER_SPEED;
        on_ground = place_meeting(x, y + 1, objSolid) || place_meeting_on_way(x, y + 1);

        // Bajar desde una plataforma one-way justo encima de la escalera: la
        // atraviesas un par de píxeles en vez de quedarte flotando sobre ella.
        // (Útil también como "drop-through" general para one-ways: reutilízalo
        // fuera de las escaleras si tu diseño lo pide.)
        if (on_ground && _quiere_bajar
            && place_meeting(x, y + 1, objPlatform) && !place_meeting(x, y + 1, objSolid))
        {
            y += 2;
            on_ground = false;
        }

        y += vel_y;
    }

    apply_state_sprite();
    exit;   // en la escalera no hay gravedad ni move_and_collide: te sales del Step aquí
}
```

### 3.8 Cuerdas y lianas

La simulación (puntos y varillas de Verlet) **ya existe** en
[`13·08 §6.3`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/08%20-%20Físicas%20a%20mano%20y%20fluidos.md) —
`cuerda_nueva()`, `verlet_integrar()`, `verlet_relajar()`. No se reimplementa aquí: solo se añade
el enganche del jugador (agarrar, empujar la cuerda con el input, soltarse con impulso).

```gml
// ---------------------------------------------------------------------------
// objRope — Create. Usa scr_verlet de 13·08 §6.1-§6.3.
// ---------------------------------------------------------------------------
cuerda           = cuerda_nueva(x, y, 14, 8);   // { puntos, varillas }, primer punto anclado
jugador_agarrado = noone;
```

```gml
// ---------------------------------------------------------------------------
// objRope — Step. El orden integrar → relajar es el que exige 13·08 §6.2.
// ---------------------------------------------------------------------------
verlet_integrar(cuerda.puntos, 0.5, 0.99);
verlet_relajar(cuerda.varillas, 6);

if (jugador_agarrado != noone)
{
    var _mano = array_last(cuerda.puntos);

    _mano.px += jugador_agarrado.vel_x * 0.3;   // el jugador empuja la cuerda al balancearse

    jugador_agarrado.x = _mano.px;              // ...y la cuerda arrastra al jugador
    jugador_agarrado.y = _mano.py;
}
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step, antes del paso 3 de 04·01 §5.3.
// ---------------------------------------------------------------------------
if (en_cuerda == noone && _jump_pressed)
{
    var _c = instance_place(x, y, objRope);
    if (_c != noone) { en_cuerda = _c; _c.jugador_agarrado = self; }
}
else if (en_cuerda != noone)
{
    if (_jump_pressed)
    {
        en_cuerda.jugador_agarrado = noone;
        en_cuerda = noone;
        vel_x = _input_x * MOVE_SPEED_MAX * 1.2;   // sales despedido con el impulso del balanceo
        vel_y = -JUMP_SPEED * 0.6;
        player_state_set(PlayerState.fall);
    }
    else
    {
        exit;   // mientras estés agarrado, la posición la lleva objRope, no move_and_collide
    }
}
```

> ⚠️ El enganche jugador-cuerda es diseño propio de esta receta, sin fuente externa abierta.
> La física de Verlet en sí (§6.3 de `13·08`) sí está verificada: Thomas Jakobsen, *Advanced
> Character Physics* (GDC 2001), citada en las Fuentes de aquel documento.

### 3.9 Nadar

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step, SUSTITUYE el paso 5 (gravedad) de 04·01 §5.3 mientras
// estés en el agua. `tilemap_agua` es una capa de tiles dedicada: usa un
// índice de tile QUE NO SEA 0, porque un tile vacío también vale 0 — con el
// índice 0 la comprobación `> 0` no distinguiría agua de aire (ver 01·10 §4).
// ---------------------------------------------------------------------------
en_agua = tilemap_get_at_pixel(tilemap_agua, x, y) > 0;

if (en_agua && state != PlayerState.swim)      player_state_set(PlayerState.swim);
else if (!en_agua && state == PlayerState.swim) player_state_set(PlayerState.fall);

if (state == PlayerState.swim)
{
    aliento = max(aliento - 1, 0);
    if (aliento <= 0 && (state_timer mod 60 == 0)) stats.take_damage(1);   // reutiliza 04·01 §6

    if (_jump_pressed) vel_y = -SWIM_STROKE_SPEED;                  // brazada: impulso hacia arriba
    else                vel_y = min(vel_y + SWIM_GRAVITY, SWIM_FALL_MAX);

    vel_x = lerp(vel_x, _input_x * SWIM_SPEED_MAX, ACCEL_AIR);
}
else
{
    aliento = min(aliento + AIRE_RECUPERACION, AIRE_MAX);
}
```

> ⚠️ Gravedad reducida, brazada y aliento son diseño de género estándar (*Metroid*, *Ecco the
> Dolphin*), sin una fuente externa concreta abierta en esta sesión. La parte SÍ verificada
> contra el manual es la detección de agua con `tilemap_get_at_pixel()` y el aviso del índice 0
> (manual oficial, página de la función — ver Fuentes).

### 3.10 Empuje de cajas por rejilla (con deshacer)

`04·01 §8` ya resuelve el empuje **libre** (continuo, a media velocidad). Esta es la variante
*sokoban*: movimiento discreto de una casilla por pulsación, con una pila de deshacer — lo que
pide un puzle de cajas, no un plataformas de acción.

```gml
// ---------------------------------------------------------------------------
// objPlayerGrid — Create. Modo de control alternativo para rooms de puzle:
// no comparte Step con el objPlayer analógico de 04·01.
// ---------------------------------------------------------------------------
grid_x    = x div TILE_SIZE;
grid_y    = y div TILE_SIZE;
historial = [];   // pila de deshacer: [{jugador:{gx,gy}, caja:{inst,gx,gy}|undefined}, ...]
```

```gml
// ---------------------------------------------------------------------------
// objPlayerGrid — funciones de movimiento por rejilla
// ---------------------------------------------------------------------------
/// @func rejilla_mover(_dx, _dy)
/// @desc Mueve una casilla y empuja una caja si la hay. `_dx`/`_dy` en {-1,0,1}.
/// @returns {Bool} true si el movimiento se realizó.
function rejilla_mover(_dx, _dy)
{
    var _destino_x = grid_x + _dx;
    var _destino_y = grid_y + _dy;
    var _wx = _destino_x * TILE_SIZE;
    var _wy = _destino_y * TILE_SIZE;

    if (place_meeting(_wx, _wy, objSolid)) return false;

    var _caja = instance_place(_wx, _wy, objBox);
    var _registro = { jugador: { gx: grid_x, gy: grid_y }, caja: undefined };

    if (_caja != noone)
    {
        var _caja_wx = _wx + _dx * TILE_SIZE;
        var _caja_wy = _wy + _dy * TILE_SIZE;

        if (place_meeting(_caja_wx, _caja_wy, objSolid))        return false;   // caja contra pared
        if (instance_place(_caja_wx, _caja_wy, objBox) != noone) return false;  // dos cajas en fila

        _registro.caja = { inst: _caja, gx: _caja.grid_x, gy: _caja.grid_y };

        _caja.grid_x = _destino_x + _dx;
        _caja.grid_y = _destino_y + _dy;
        _caja.x      = _caja_wx;
        _caja.y      = _caja_wy;
    }

    array_push(historial, _registro);

    grid_x = _destino_x;
    grid_y = _destino_y;
    x = _wx;
    y = _wy;
    return true;
}

/// @func rejilla_deshacer()
/// @desc Revierte el último movimiento (jugador y, si empujó una, la caja).
function rejilla_deshacer()
{
    if (array_length(historial) == 0) return;

    var _r = array_pop(historial);

    grid_x = _r.jugador.gx;
    grid_y = _r.jugador.gy;
    x = grid_x * TILE_SIZE;
    y = grid_y * TILE_SIZE;

    if (!is_undefined(_r.caja) && instance_exists(_r.caja.inst))
    {
        _r.caja.inst.grid_x = _r.caja.gx;
        _r.caja.inst.grid_y = _r.caja.gy;
        _r.caja.inst.x      = _r.caja.gx * TILE_SIZE;
        _r.caja.inst.y      = _r.caja.gy * TILE_SIZE;
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objPlayerGrid — Step. Un movimiento por pulsación, nunca por frame.
// ---------------------------------------------------------------------------
if (keyboard_check_pressed(ord("Z"))) rejilla_deshacer();

var _dx = keyboard_check_pressed(vk_right) - keyboard_check_pressed(vk_left);
var _dy = keyboard_check_pressed(vk_down)  - keyboard_check_pressed(vk_up);

if (_dx != 0 || _dy != 0) rejilla_mover(_dx, _dy);
```

> ⚠️ El diseño de casillas + deshacer es la regla estándar del género sokoban (*Baba Is You*,
> PuzzleScript), no una cita de un repositorio concreto abierto en esta sesión.

---

## 4 · Checklist

- [ ] El enum `PlayerState` tiene los estados nuevos **al final**, nunca insertados en medio.
- [ ] `tilemap_suelo` (y `tilemap_agua`, si nadas) se obtienen en el Create con `layer_tilemap_get_id()`, no cada frame.
- [ ] El tile marcador de agua **no** usa el índice `0` del tile set.
- [ ] `resolver_pendiente()` se llama **antes** de aplicar gravedad y **después** de la aceleración horizontal.
- [ ] `SLOPE_ANGLE_MAX` está por debajo de 90° con margen: una pendiente casi vertical debe tratarse como pared, no como rampa fallida.
- [ ] `wall_dir` solo se activa en el aire (`on_ground == false`): en el suelo, `place_meeting()` a los lados detectaría paredes que no son "de escalar".
- [ ] El *lockout* del wall jump (`wall_jump_lock`) sobrescribe `_input_x` **antes** del paso de aceleración, no después.
- [ ] `wall_stamina` se resetea al tocar suelo **y** al agarrar una pared con un `id` distinto — nunca al seguir en la misma.
- [ ] `corregir_esquina()` solo actúa si `vel_y < 0` (subiendo): nunca al aterrizar.
- [ ] Los sensores de `detectar_borde()` usan `LEDGE_OFFSET_X/Y` coherentes con el tamaño real del sprite — pruébalos con `draw_rectangle` en modo debug antes de confiar en ellos a ciegas.
- [ ] `mask_index` se cambia a un sprite de máscara **dedicado**, nunca al sprite de animación actual.
- [ ] Al agacharte, el techo se comprueba con la máscara de PIE antes de levantarte, no después.
- [ ] El estado `climb`/`hang`/rejilla hace `exit` para no ejecutar `move_and_collide()` ese frame.
- [ ] `objPlatform` (one-way) y `objSolid` nunca se mezclan en la misma llamada a `move_and_collide()` — sigue valiendo el aviso de `04·01 §5.4`.
- [ ] `python3 _indice/validar-codigo-gml.py` y `python3 _indice/verificar-enlaces.py "04 - Recetas por género"` en 0 antes de dar esto por cerrado.

---

## 5 · Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Registrar el heightmap con un array de longitud distinta a `tilemap_get_tile_width()` | `pendiente_bajo_punto()` lee fuera de rango y el juego se cae | El array de `slope_heightmap_registrar()` debe tener exactamente `_tw` valores |
| Llamar a `resolver_pendiente()` DESPUÉS de `move_and_collide()` | El jugador se atasca al pie de cada rampa | Va **antes**: reproyecta `vel_x`/`vel_y` para que `move_and_collide()` reciba ya el vector correcto |
| Detectar pared con `place_meeting()` en el suelo también | El personaje entra en wall slide al caminar junto a una columna | `detectar_pared()` empieza con `if (on_ground) return 0;` |
| No resetear `wall_stamina` al cambiar de pared | El jugador nunca puede volver a deslizar tras agotarla una vez | Compara el `id` de la pared actual contra `wall_last_id` |
| Corrección de esquina activa también al caer | El jugador se cuela por huecos que no debería | `corregir_esquina()` exige `vel_y < 0` (subiendo) |
| Sensores de borde demasiado anchos | Te "enganchas" a bordes a los que no llegabas visualmente | Dibuja `LEDGE_OFFSET_X/Y` con `draw_rectangle()` en un modo debug y ajusta a ojo |
| Cambiar `mask_index` al sprite de animación en vez de a uno fijo | La máscara "respira" con la animación; colisiones inconsistentes frame a frame | Sprite de máscara dedicado, como en `13·04 §3.9` |
| Tile de agua en el índice `0` del tile set | `tilemap_get_at_pixel() > 0` nunca detecta el agua | Usa cualquier índice distinto de 0 para el tile marcador |
| Mover al jugador por rejilla cada frame en vez de por pulsación | El sokoban se vuelve ilegible: la caja "patina" varias casillas | `keyboard_check_pressed()`, nunca `keyboard_check()`, para `rejilla_mover()` |
| Olvidar el `exit` en los estados climb/hang/rejilla | `move_and_collide()` se sigue ejecutando y pelea contra la posición fijada a mano | Cierra esos bloques con `exit` antes de los pasos 6-10 del bucle base |

---

## Ver también

- [`04 · 01 — Plataformas 2D`](./01%20-%20Plataformas%202D.md) — el `objPlayer` y la máquina de
  estados que esta receta extiende (§4.6-§4.9, §5.1-§5.8): movimiento base, coyote time, jump
  buffer, one-way y plataformas móviles.
- [`04 · 06 — Metroidvania`](./06%20-%20Metroidvania.md) §5.4 — doble salto, dash, y los flags
  `puede_agarrar`/`agarrado` que esta receta implementa por fin.
- [`04 · 30 — Combate cuerpo a cuerpo`](./30%20-%20Combate%20cuerpo%20a%20cuerpo%20-%20hitboxes,%20hurtboxes%20y%20combos.md) —
  por qué el jugador necesita una máscara de movimiento fija, separada de la hurtbox.
- [`01 · 08 — Movimiento y colisiones`](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) —
  `place_meeting`, `move_and_collide`, y cómo elegir la forma de la máscara de colisión.
- [`01 · 10 — Rooms, capas, cámaras y viewports`](../01%20-%20Fundamentos/10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md) §4 —
  el «blob» de datos de tile, `tile_get_index`, y colisión con tile maps.
- [`13 · 08 — Físicas a mano y fluidos`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/08%20-%20Físicas%20a%20mano%20y%20fluidos.md) §6 —
  la simulación de Verlet completa (`cuerda_nueva`, `verlet_integrar`, `verlet_relajar`) que
  `3.8` reutiliza sin reimplementar.
- [`13 · 13 — Matemáticas aplicadas al juego`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md) §6.7 —
  AABB frente a OBB, para cuando la máscara rectangular de la pared deje de bastar.
- [`13 · 02 — Diseño de niveles`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/02%20-%20Diseño%20de%20niveles.md) §3.11 —
  cómo medir en código las métricas de salto reales del jugador, antes de fijar `SLOPE_ANGLE_MAX`
  o `LEDGE_OFFSET_Y` a ojo.

---

## Fuentes

Todas consultadas el 2026-09-06.

- **Manual oficial — `move_and_collide`** — cita verificada: *"Permite que la instancia se mueva
  al recorrer pendientes o escalones pequeños que, de otro modo, le impedirían avanzar."*
  <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement/move_and_collide.htm>
- **Manual oficial — `mask_index`** —
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Instance_Variables/mask_index.htm>
- **Manual oficial — `tilemap_get_at_pixel`** — confirma el aviso del índice 0: *"puede crear
  'mapas de colisión' de tiles utilizando un tile en el índice 1... y comprobar 1 o 0 (un tile
  vacío)"*. <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers/tilemap_get_at_pixel.htm>
- **Manual oficial — Arrays (`GML_Overview/Arrays.md`)** — confirma que leer un array fuera de
  rango **da error** (a diferencia del accesor de struct `[$ ]`, que devuelve `undefined`).
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Overview/Arrays.htm>
- **Manual oficial — Accessors (`GML_Overview/Accessors.md`)** — confirma el comportamiento de
  `struct[$ "clave"]` para una clave inexistente.
  <https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Overview/Accessors.htm>
- **Sonic Physics Guide — *Slope Physics* (Slopes Part 2)** — `Ground Speed`, la fórmula
  `X Speed = Ground Speed·cos(Ground Angle)`, `Y Speed = Ground Speed·-sin(Ground Angle)`, y el
  *Slope Factor*. Consultado vía Internet Archive (el sitio en vivo bloquea el acceso automático
  con un reto anti-bot Anubis): <https://web.archive.org/web/20231225001912/https://info.sonicretro.org/SPG:Slope_Physics>
  (original: <https://info.sonicretro.org/SPG:Slope_Physics>).
- **Sonic Physics Guide — *Solid Tiles* (Terrain Part 1)** — el *Height Array*: 16 valores de
  altura por tile, la técnica detrás de `slope_heightmap_registrar()`. Vía Internet Archive:
  <https://web.archive.org/web/2023/https://info.sonicretro.org/SPG:Solid_Tiles>
  (original: <https://info.sonicretro.org/SPG:Solid_Tiles>).
- **Sonic Physics Guide — *Slope Collision* §Ground Sensors (Grounded)** — la ventana de
  "pegado" al suelo dependiente de la velocidad (`min(abs(X Speed) + 4, 14)`), origen de
  `_rango_abajo` en `resolver_pendiente()`. Vía Internet Archive:
  <https://web.archive.org/web/2023/https://info.sonicretro.org/SPG:Slope_Collision>
  (original: <https://info.sonicretro.org/SPG:Slope_Collision>).
- **Celeste — `Source/Player/Player.cs`**, Maddy Thorson / Noel Berry — código fuente publicado
  por los propios autores. Consultado el fichero completo vía
  <https://raw.githubusercontent.com/NoelFB/Celeste/master/Source/Player/Player.cs>
  (repositorio: <https://github.com/NoelFB/Celeste>). Usado como **referencia de técnica**, no
  copiado: `UpwardCornerCorrection` (constante, línea 53) y el bucle de corrección de esquina
  (líneas ~2587-2609) para `3.4`; `WallJumpCheck`/`WallJump` (líneas 1731-1780) para la
  distancia de comprobación de pared, el *lockout* de input (`forceMoveXTimer`/`WallJumpForceTime`)
  y el reseteo del temporizador de deslizamiento en `3.2`. Los valores numéricos de esta receta
  están reescalados a las constantes propias de `04·01 §5.0`, no son los píxeles/subpíxeles
  originales de Celeste.
