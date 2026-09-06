# 11 — Arcade y juegos de un botón

> **Dificultad:** básica
> El mejor laboratorio de *game feel* que existe: con un solo input, cada
> imperfección en la sensación se nota inmediatamente.

---

## 1. Visión general

Un arcade clásico se juega en sesiones de 30 segundos a 3 minutos. El objetivo
no es contar una historia: es que el jugador diga "otra vez" y meta otra moneda
metafórica.

**Lo que define al género:**

- **Reglas explicables en una frase.** "No toques las paredes", "salta cuando
  toque", "no dejes caer la pelota".
- **Dificultad que crece sola**, sin contenido nuevo.
- **Una puntuación** que da medida de habilidad y algo con lo que competir.
- **Sesiones cortas** con reinicio instantáneo (menos de 1 segundo).

**Referencias hechas en GameMaker:** *Downwell*, *Super Hexagon* (Terry
Cavanagh), *VVVVVV* (Terry Cavanagh, GameMaker), *Nuclear Throne*,
*Space Rocks* (el proyecto de iniciación clásico de GameMaker), *Pac-Man*
(el tutorial oficial *Space Rocks* es básicamente Asteroids).

**Subgéneros:**

| Subgénero | Input | Ritmo |
|---|---|---|
| *One-button* puro | Pulsar/un pulsar | Variable (Downwell) |
| *Endless runner* | Salto | Constante y creciente |
| *Score attack* | Complejo, sesión corta | Explosivo |
| *High score chase* | Variable | Reinicio instantáneo |
| *Wave survival* | Movimiento + disparo | Por oleadas |

---

## 2. Arquitectura recomendada

### Jerarquía de objetos

```
objPlayer
objObstacle        (padre: todo lo que mata)
├── objSpike
├── objWall
└── objMovingBlock
objPickup          (monedas, puntos)
objSpawner         (genera obstáculos; la dificultad vive aquí)
objScore           (puntuación, multiplicador, combo)
objCamera
objDifficulty      (curva de dificultad por tiempo/puntuación)
```

### Rooms

```
rm_arcade          (una sola room, se reinicia con room_restart())
rm_menu
rm_game_over       (puntuación, récord, botón de reintentar)
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `ScoreState` | Puntos, multiplicador, combo, récords |
| `DifficultyCurve` | Qué parámetro cambia en qué momento |
| `SpawnerConfig` | Qué spawnea, cada cuánto, con qué variación |

---

## 3. El bucle central (core loop)

```
┌─ Begin Step ─────────────────────────────────────────────┐
│ 1. Leer el input (un solo botón)                          │
└──────────────────────────────────────────────────────────┘
┌─ Step ───────────────────────────────────────────────────┐
│ 2. objDifficulty: avanzar el reloj, ajustar parámetros    │
│ 3. objSpawner: ¿toca spawnear? (según la dificultad)      │
│ 4. Movimiento del jugador                                 │
│ 5. Mover obstáculos hacia el jugador (o el jugador avanza)│
│ 6. Colisiones: muerte / recogida                          │
│ 7. objScore: combo, multiplicador, puntos por supervivencia│
│ 8. Culling de lo que sale de pantalla                     │
│ 9. ¿Murió? → game over en menos de 1 segundo              │
└──────────────────────────────────────────────────────────┘
┌─ End Step ───────────────────────────────────────────────┐
│ 10. Cámara: seguimiento + shake                           │
└──────────────────────────────────────────────────────────┘
```

**La regla del reinicio instantáneo:** desde que mueres hasta que vuelves a
controlar al personaje deben pasar menos de 60 frames. Si tardas más, el
jugador se va.

---

## 4. Sistemas clave

### 4.1 Un botón, muchas acciones

Con un solo input tienes muchas más acciones de las que parece:

| Contexto | Acción |
|---|---|
| En el suelo | Saltar |
| En el aire | Doble salto / caída rápida |
| En la pared | Salto desde la pared |
| Sobre un enemigo | Rebote / pisotón |
| Mantenido | Cargar / planear |
| Doble pulsación rápida | Dash |
| Sin pulsar | Caer más rápido (gravedad alta) |

La gracia del género es que **el mismo botón hace cosas distintas según el
contexto**, y el jugador lo descubre solo.

### 4.2 Dificultad progresiva

Nunca aumentes la velocidad linealmente: es aburrido al principio e imposible
al final. Usa una curva y **varía los parámetros por separado**:

```gml
// Los tres ejes de la dificultad en un arcade:
velocidad_juego = base + (tiempo * 0.0008);     // más rápido
intervalo_spawn = max(20, 90 - (tiempo * 0.01)); // más obstáculos
complejidad     = min(4, floor(puntuacion / 500)); // patrones más duros
```

**Introduce variedad, no solo más velocidad.** Cada 30 segundos, cambia el
tipo de obstáculo dominante. Eso mantiene la novedad sin subir la dificultad
real.

### 4.3 Puntuación y multiplicadores

Tres fuentes de puntos que deben coexistir:

| Fuente | Ritmo | Para qué |
|---|---|---|
| **Supervivencia** | Constante | Recompensa aguantar |
| **Riesgo** | Por接近 | Recompensa jugar al límite |
| **Combo** | Por cadena | Recompensa la habilidad sostenida |

El combo es el más importante: **el multiplicador debe decaer con el tiempo**,
no solo al fallar. Así el jugador tiene que seguir actuando para mantenerlo.

### 4.4 *Near miss*: recompensar el riesgo

La técnica más elegante del arcade moderno: si pasas muy cerca de un obstáculo
sin tocarlo, ganas puntos extra. Convierte el "casi me mato" de frustración en
recompensa.

```gml
if (distancia < umbral_near_miss)
{
    sumar_puntos(10 * multiplicador);
    fx_floating_text(x, y, "¡CERCA!", c_orange);
    // Tiempo bala de 5 frames: se siente espectacular
    time_slow(0.35, 12);
}
```

### 4.5 High scores

Dos niveles:

1. **Local** — un array de 10 entradas en disco.
2. **Online** — requiere backend; no lo hagas hasta que el juego esté terminado.

Para el local, guarda nombre + puntuación + fecha. Y **permite al jugador
escribir su nombre** con un teclado virtual simple: ese detalle multiplica el
apego.

### 4.6 Juice: la lista mínima

De la receta 15, lo que un arcade necesita obligatoriamente:

| Efecto | Cuándo |
|---|---|
| Screen shake | Al morir, al romper algo, en *near miss* |
| Hit stop | Al recoger, al romper, al chocar |
| Partículas | Cada muerte, cada recogida |
| Squash & stretch | Saltar, aterrizar, morir |
| Flash | Al recibir daño, al hacer combo |
| Texto flotante | Cada punto ganado |
| Rastro | Al moverse rápido |

### 4.7 Muerte legible

Cuando mueres, el jugador tiene que entender **por qué**. Tres pasos:

1. Congelar el juego 20-30 frames.
2. Resaltar visualmente el objeto que te mató (zoom o flash).
3. Mostrar la puntuación y el récord.

---

## 5. Código base

### 5.0 Puntuación y combo

```gml
// ---------------------------------------------------------------------------
// scr_arcade_score
// ---------------------------------------------------------------------------

/// @func ScoreState()
/// @desc Puntuación, multiplicador y combo con decaimiento.
function ScoreState() constructor
{
    puntos        = 0;
    multiplicador = 1.0;
    multiplicador_max = 8.0;

    combo         = 0;
    combo_timer   = 0;
    combo_duracion = 120;      // frames antes de que el combo decaiga

    monedas       = 0;
    near_misses   = 0;

    /// @desc Actualiza un frame: decae el combo si no hay acción.
    update = function()
    {
        if (combo > 0)
        {
            combo_timer--;

            if (combo_timer <= 0)
            {
                // El combo decae: esto obliga a seguir actuando
                combo = 0;
                multiplicador = 1.0;
            }
        }
    };

    /// @desc Suma un evento de puntuación.
    add = function(_base)
    {
        combo++;
        combo_timer = combo_duracion;

        // El multiplicador sube con el combo, con tope
        multiplicador = min(multiplicador_max, 1.0 + floor(combo / 5) * 0.5);

        var _ganados = round(_base * multiplicador);
        puntos += _ganados;

        return _ganados;
    };

    /// @desc Puntos por supervivencia (por frame).
    add_survival = function(_por_frame)
    {
        puntos += _por_frame * multiplicador;
    };

    /// @desc Rompe el combo (morir, o fallar).
    romper_combo = function()
    {
        combo = 0;
        combo_timer = 0;
        multiplicador = 1.0;
    };

    /// @desc Progreso 0..1 del combo (para la barra del HUD).
    combo_progreso = function()
    {
        if (combo <= 0) return 0;
        return clamp(combo_timer / combo_duracion, 0, 1);
    };

    serialize = function()
    {
        return {
            puntos: puntos, monedas: monedas, near_misses: near_misses
        };
    };
}

/// @func high_scores_cargar()
function high_scores_cargar()
{
    // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
    // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
    // 14 - Persistencia y archivos.md §1.
    var _path = game_save_id + "arcade_scores.json";
    global.high_scores = [];

    if (!file_exists(_path))
    {
        // Récords por defecto: el jugador necesita algo que batir
        for (var _i = 0; _i < 10; _i++)
        {
            array_push(global.high_scores, {
                name: "CPU", score: (10 - _i) * 100
            });
        }
        return;
    }

    var _f = file_text_open_read(_path);
    var _json = file_text_read_string(_f);
    file_text_close(_f);

    var _d = json_parse(_json);
    if (variable_struct_exists(_d, "scores")) global.high_scores = _d.scores;
}

/// @func high_scores_guardar()
function high_scores_guardar()
{
    var _data = { scores: global.high_scores };

    var _f = file_text_open_write(game_save_id + "arcade_scores.json");
    file_text_write_string(_f, json_stringify(_data));
    file_text_close(_f);
}

/// @func high_score_submit(_puntos, _nombre)
/// @desc Devuelve la posición conseguida (0-9) o -1 si no entra.
function high_score_submit(_puntos, _nombre)
{
    var _scores = global.high_scores;

    // ¿Entra en el top 10?
    if (array_length(_scores) >= 10 && _puntos <= _scores[9].score) return -1;

    array_push(_scores, { name: _nombre, score: _puntos });

    array_sort(_scores, function(_a, _b)
    {
        return (_a.score > _b.score) ? -1 : 1;
    });

    if (array_length(_scores) > 10) array_resize(_scores, 10);

    high_scores_guardar();

    // Devolver la posición
    for (var _i = 0; _i < array_length(_scores); _i++)
    {
        if (_scores[_i].score == _puntos && _scores[_i].name == _nombre) return _i;
    }
    return -1;
}
```

### 5.1 Curva de dificultad

```gml
// ---------------------------------------------------------------------------
// scr_difficulty
// ---------------------------------------------------------------------------

/// @func DifficultyCurve()
/// @desc Ajusta los parámetros del juego según el tiempo y la puntuación.
function DifficultyCurve() constructor
{
    tiempo_frames = 0;

    // --- Parámetros actuales (los lee el spawner) ---
    velocidad_juego   = 4.0;
    intervalo_spawn   = 90;     // frames entre obstáculos
    nivel_patron      = 0;      // 0..4: qué tan complejos son los patrones
    velocidad_obstaculo = 3.0;

    // --- Límites ---
    vel_max          = 11.0;
    intervalo_min    = 22;

    update = function(_puntuacion)
    {
        tiempo_frames++;

        var _t = tiempo_frames;
        var _p = (_puntuacion == undefined) ? 0 : _puntuacion;

        // --- Velocidad: crecimiento con curva suave (raíz cuadrada) ----------
        // Lineal es aburrido al principio e imposible al final.
        // La raíz crece rápido al principio y se frena después.
        velocidad_juego = min(vel_max, 4.0 + (sqrt(_t) * 0.055));

        // --- Intervalo de spawn: decrece hasta un mínimo ----------------------
        intervalo_spawn = max(intervalo_min, 90 - (_t * 0.012));

        // --- Complejidad de patrones: escalonada por puntuación ---------------
        nivel_patron = min(4, floor(_p / 400));

        // --- Velocidad de los obstáculos ----------------------------------------
        velocidad_obstaculo = 3.0 + (sqrt(_t) * 0.030);
    };

    reset = function()
    {
        tiempo_frames = 0;
        velocidad_juego = 4.0;
        intervalo_spawn = 90;
        nivel_patron    = 0;
        velocidad_obstaculo = 3.0;
    };

    /// @desc Minutos y segundos transcurridos (para el HUD).
    tiempo_texto = function()
    {
        var _segundos_totales = tiempo_frames / game_get_speed(gamespeed_fps);
        var _min = floor(_segundos_totales / 60);
        var _seg = floor(_segundos_totales mod 60);
        return string(_min) + ":" + string_format(_seg, 2, 0);
    };
}
```

### 5.2 Spawner con patrones por nivel

```gml
// ---------------------------------------------------------------------------
// objSpawner — Create
// ---------------------------------------------------------------------------
dificultad = new DifficultyCurve();
timer      = 0;
```

```gml
// ---------------------------------------------------------------------------
// objSpawner — Step
// ---------------------------------------------------------------------------
dificultad.update(objScore.score_state.puntos);

timer++;

if (timer >= dificultad.intervalo_spawn)
{
    timer = 0;
    spawnear_patron(dificultad.nivel_patron);
}
```

```gml
// ---------------------------------------------------------------------------
// objSpawner — patrones
// ---------------------------------------------------------------------------

/// @func spawnear_patron(_nivel)
/// @desc Cada nivel de complejidad añade un patrón nuevo a la bolsa.
function spawnear_patron(_nivel)
{
    var _y = room_height;

    switch (irandom(_nivel))
    {
        case 0:   // Un obstáculo simple
            crear_obstaculo(irandom_range(60, room_width - 60), _y);
            break;

        case 1:   // Dos obstáculos con hueco
            var _hueco = irandom_range(50, room_width - 110);
            crear_obstaculo(_hueco, _y);
            crear_obstaculo(_hueco + 60, _y);
            break;

        case 2:   // Línea de tres con hueco central
            var _centro = room_width * 0.5 + irandom_range(-70, 70);
            crear_obstaculo(_centro - 70, _y);
            crear_obstaculo(_centro, _y);
            crear_obstaculo(_centro + 70, _y);
            break;

        case 3:   // Zigzag: obstáculos escalonados
            for (var _i = 0; _i < 4; _i++)
            {
                crear_obstaculo(100 + (_i * 60), _y + (_i * 40));
            }
            break;

        case 4:   // Muro con un hueco estrecho
            var _h = irandom_range(40, room_width - 100);
            for (var _x = 0; _x < room_width; _x += 30)
            {
                if (abs(_x - _h) < 45) continue;    // el hueco
                crear_obstaculo(_x, _y);
            }
            break;
    }

    // Monedas de vez en cuando: dan un objetivo secundario
    if (irandom(3) == 0)
    {
        instance_create_layer(irandom_range(60, room_width - 60),
                              room_height, "Instances", objPickup);
    }
}

/// @func crear_obstaculo(_x, _y)
function crear_obstaculo(_x, _y)
{
    var _o = instance_create_layer(_x, _y, "Instances", objObstacle);
    _o.velocidad = dificultad.velocidad_obstaculo;
    return _o;
}
```

### 5.3 Jugador de un botón

```gml
// ---------------------------------------------------------------------------
// objPlayer — Create
// ---------------------------------------------------------------------------
vel_y    = 0;
vel_x    = 0;
vel_x_max = 5.0;

GRAVEDAD       = 0.55;
FUERZA_SALTO   = 11.0;
GRAVEDAD_CAIDA = 0.85;     // más alta: caer rápido al soltar

en_suelo  = false;
saltos    = 0;
saltos_max = 2;

pulsado   = false;
pulsado_prev = false;

// Rastro
rastro = [];
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Step
// ---------------------------------------------------------------------------
// --- 1. Un solo input ---------------------------------------------------------
var _cualquier_tecla = keyboard_check(vk_space)
                    || keyboard_check(vk_up)
                    || keyboard_check(ord("Z"))
                    || mouse_check_button(mb_left);

pulsado_prev = pulsado;
pulsado      = _cualquier_tecla;

var _pulso_ahora = (pulsado && !pulsado_prev);

// --- 2. Salto (con doble salto) -----------------------------------------------
if (_pulso_ahora && saltos < saltos_max)
{
    vel_y = -FUERZA_SALTO;
    saltos++;

    // Juice de salto
    squash_preset(self, "jump");
    fx_dust_land(x, bbox_bottom);

    var _s = audio_play_sound(sndJump, 8, false);
    audio_sound_pitch(_s, 1.0 + (saltos * 0.15));    // el 2.º salto suena distinto
}

// --- 3. Gravedad variable: soltar = caer rápido ---------------------------------
// Esta es la mecánica que hace que un botón se sienta expresivo.
vel_y += pulsado ? GRAVEDAD : GRAVEDAD_CAIDA;
vel_y = min(vel_y, 14);

// --- 4. Movimiento horizontal automático (endless runner) ------------------------
vel_x = lerp(vel_x, vel_x_max, 0.05);

// --- 5. Mover -------------------------------------------------------------------
y += vel_y;
x += vel_x;

// --- 6. Suelo ----------------------------------------------------------------------
if (y >= SUELO_Y)
{
    y = SUELO_Y;
    vel_y = 0;
    saltos = 0;

    if (!en_suelo)
    {
        // Aterrizaje
        squash_preset(self, "land");
        fx_dust_land(x, y);
        camera_shake(0.06);
        audio_play_sound(sndLand, 6, false);
    }
    en_suelo = true;
}
else
{
    en_suelo = false;
}

// --- 7. Rastro -----------------------------------------------------------------------
if (global.frame_count mod 3 == 0)
{
    array_push(rastro, { x: x, y: y, vida: 16 });
}
for (var _i = array_length(rastro) - 1; _i >= 0; _i--)
{
    rastro[_i].vida--;
    if (rastro[_i].vida <= 0) array_delete(rastro, _i, 1);
}
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Draw
// ---------------------------------------------------------------------------
// --- Rastro (detrás) -------------------------------------------------------------
for (var _i = 0; _i < array_length(rastro); _i++)
{
    var _r = rastro[_i];
    draw_sprite_ext(sprite_index, image_index, _r.x, _r.y,
                    1, 1, 0, c_white, (_r.vida / 16) * 0.35);
}

// --- Personaje -----------------------------------------------------------------------
draw_sprite_ext(sprite_index, image_index, x, y,
                image_xscale * squash_x, image_yscale * squash_y,
                image_angle, image_blend, image_alpha);
```

### 5.4 Near miss

```gml
// ---------------------------------------------------------------------------
// objObstacle — Step
// ---------------------------------------------------------------------------
y -= velocidad;     // sube hacia el jugador

// Culling
if (y < -64) { instance_destroy(); exit; }

// --- Colisión mortal ---------------------------------------------------------------
if (place_meeting(x, y, objPlayer))
{
    // Morir
    game_over();
    exit;
}

// --- Near miss: ¿pasó muy cerca sin tocar? -----------------------------------------
var _dist = point_distance(x, y, objPlayer.x, objPlayer.y);

if (!near_miss_dado && _dist < 42 && y < objPlayer.y)
{
    near_miss_dado = true;

    var _ganados = objScore.score_state.add(15);
    objScore.score_state.near_misses++;

    fx_floating_text(objPlayer.x, objPlayer.y - 30, "¡CERCA! +" + string(_ganados),
                     c_orange);
    camera_shake(0.12);

    // Tiempo bala breve: es lo que hace que el momento se sienta épico
    time_slow(0.35, 14);
}
```

```gml
// ---------------------------------------------------------------------------
// objObstacle — Create
// ---------------------------------------------------------------------------
velocidad = 3.0;
near_miss_dado = false;
```

### 5.5 Muerte y reinicio instantáneo

```gml
// ---------------------------------------------------------------------------
// scr_arcade_gameover
// ---------------------------------------------------------------------------

/// @func game_over()
function game_over()
{
    if (global.muerto) exit;    // evitar doble muerte
    global.muerto = true;

    // --- 1. Congelar y ralentizar ------------------------------------------------
    global.game_freeze = true;
    time_slow(0.15, 40);

    // --- 2. Explosión y shake fuerte ----------------------------------------------
    fx_explosion(objPlayer.x, objPlayer.y, 1.4);
    camera_shake(0.85);
    hit_stop(8);
    fx_flash(c_red, 0.35, 12);

    // --- 3. Sonido -------------------------------------------------------------------
    audio_play_sound(sndDeath, 10, false);
    audio_stop_sound(global.musica_actual);

    // --- 4. Resaltar al asesino --------------------------------------------------------
    with (objObstacle)
    {
        if (place_meeting(x, y, objPlayer))
        {
            asesino = true;
            squash_preset(self, "death");
        }
    }

    // --- 5. Ir a la pantalla de resultados (menos de 1 segundo) ----------------------
    // alarm[0] = 45 frames ≈ 0,75 s
    objPlayer.alarm[0] = 45;
}
```

```gml
// ---------------------------------------------------------------------------
// objPlayer — Alarm 0
// ---------------------------------------------------------------------------
global.game_freeze = false;

// Ir a resultados con la puntuación
global.ultima_puntuacion = objScore.score_state.puntos;
room_goto(rm_game_over);
```

```gml
// ---------------------------------------------------------------------------
// rm_game_over → objResults — Create
// ---------------------------------------------------------------------------
puntuacion = global.ultima_puntuacion;
posicion   = -1;
nombre     = "";
escribiendo = false;

// ¿Entró en el top 10?
if (high_score_puede_entrar(puntuacion))
{
    escribiendo = true;
}

/// @func high_score_puede_entrar(_puntos)
function high_score_puede_entrar(_puntos)
{
    var _s = global.high_scores;
    if (array_length(_s) < 10) return true;
    return (_puntos > _s[array_length(_s) - 1].score);
}
```

```gml
// ---------------------------------------------------------------------------
// objResults — Step (teclado virtual minimalista)
// ---------------------------------------------------------------------------
if (!escribiendo)
{
    // ESPACIO o clic → reintentar
    if (keyboard_check_pressed(vk_space) || mouse_check_button_pressed(mb_left))
    {
        restart_game();
    }
    exit;
}

// Escribir nombre: A-Z, 0-9, retroceso
var _c = keyboard_lastchar;
if (_c != "" && string_length(nombre) < 8)
{
    var _mayus = string_upper(_c);
    if ((_mayus >= "A" && _mayus <= "Z") || (_mayus >= "0" && _mayus <= "9"))
    {
        nombre += _mayus;
        audio_play_sound(sndBlip, 5, false);
    }
    keyboard_clear(keyboard_lastkey);
}

if (keyboard_check_pressed(vk_backspace) && string_length(nombre) > 0)
{
    nombre = string_copy(nombre, 1, string_length(nombre) - 1);
}

if (keyboard_check_pressed(vk_enter) && string_length(nombre) > 0)
{
    posicion = high_score_submit(puntuacion, nombre);
    escribiendo = false;
}
```

```gml
// ---------------------------------------------------------------------------
// scr_restart
// ---------------------------------------------------------------------------

/// @func restart_game()
/// @desc Reinicio completo e instantáneo.
function restart_game()
{
    global.muerto = false;
    global.hit_stop = 0;
    global.game_freeze = false;
    global.time_scale = 1.0;

    if (instance_exists(objScore)) objScore.score_state = new ScoreState();
    if (instance_exists(objSpawner)) objSpawner.dificultad.reset();

    // Limpiar todos los obstáculos
    with (objObstacle) instance_destroy();
    with (objPickup)   instance_destroy();

    room_restart();
}
```

### 5.6 HUD de arcade

```gml
// ---------------------------------------------------------------------------
// objHUD — Draw GUI
// ---------------------------------------------------------------------------
var _gw = display_get_gui_width();
var _s  = objScore.score_state;

// --- Puntuación -------------------------------------------------------------------
draw_set_font(fntArcadeBig);
draw_set_halign(fa_right);
draw_set_color(c_white);
draw_text(_gw - 20, 16, string(_s.puntos));
draw_set_halign(fa_left);

// --- Multiplicador (con "pop" cuando cambia) ---------------------------------------
if (_s.multiplicador > 1.0)
{
    draw_set_font(fntArcadeMed);
    draw_set_color(c_yellow);
    draw_text(_gw - 20, 52, "x" + string_format(_s.multiplicador, 1, 1));
}

// --- Barra de combo ----------------------------------------------------------------------
if (_s.combo > 0)
{
    var _barra_w = 180;
    var _progreso = _s.combo_progreso();

    draw_set_color(c_black);
    draw_rectangle(20, 16, 20 + _barra_w, 30, false);

    // Verde → amarillo → rojo según se agota
    var _color = merge_color(c_red, c_green, _progreso);
    draw_set_color(_color);
    draw_rectangle(20, 16, 20 + (_barra_w * _progreso), 30, false);

    draw_set_color(c_white);
    draw_set_font(fntArcadeSmall);
    draw_text(20, 34, "COMBO " + string(_s.combo));
}

// --- Récord -----------------------------------------------------------------------------
draw_set_font(fntArcadeSmall);
draw_set_color(c_gray);
draw_text(20, 56, "RÉCORD: " + string(global.high_scores[0].score));
```

---

## 6. Gestión del estado del jugador

```gml
// ---------------------------------------------------------------------------
// scr_arcade_meta
// ---------------------------------------------------------------------------

/// @func ArcadeMeta()
/// @desc Progresión entre partidas de un arcade.
function ArcadeMeta() constructor
{
    partidas_jugadas = 0;
    mejor_puntuacion = 0;
    tiempo_total_frames = 0;
    monedas_totales  = 0;
    logros = {};

    /// @desc Registra el final de una partida.
    registrar_partida = function(_score_state, _frames)
    {
        partidas_jugadas++;
        tiempo_total_frames += _frames;
        monedas_totales += _score_state.monedas;

        if (_score_state.puntos > mejor_puntuacion)
        {
            mejor_puntuacion = _score_state.puntos;
        }

        // --- Logros ---------------------------------------------------------------
        if (_score_state.puntos >= 10000) desbloquear("diez_mil");
        if (_score_state.combo_max >= 30)  desbloquear("combo_30");
        if (_score_state.near_misses >= 50) desbloquear("temerario");
        if (partidas_jugadas >= 100)       desbloquear("cien_partidas");

        guardar();
    };

    desbloquear = function(_id)
    {
        if (variable_struct_exists(logros, _id)) return false;

        logros[$ _id] = true;

        // Notificación
        fx_floating_text(display_get_gui_width() * 0.5, 100,
                         "¡LOGRO: " + _id + "!", c_yellow);
        audio_play_sound(sndAchievement, 10, false);
        return true;
    };

    tiene = function(_id)
    {
        return variable_struct_exists(logros, _id);
    };

    guardar = function()
    {
        var _data = {
            partidas_jugadas: partidas_jugadas,
            mejor_puntuacion: mejor_puntuacion,
            tiempo_total_frames: tiempo_total_frames,
            monedas_totales: monedas_totales,
            logros: logros
        };

        // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
        // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
        // 14 - Persistencia y archivos.md §1.
        var _f = file_text_open_write(game_save_id + "arcade_meta.json");
        file_text_write_string(_f, json_stringify(_data));
        file_text_close(_f);
    };

    cargar = function()
    {
        var _path = game_save_id + "arcade_meta.json";
        if (!file_exists(_path)) return;

        var _f = file_text_open_read(_path);
        var _d = json_parse(file_text_read_string(_f));
        file_text_close(_f);

        partidas_jugadas    = _d.partidas_jugadas;
        mejor_puntuacion    = _d.mejor_puntuacion;
        tiempo_total_frames = _d.tiempo_total_frames;
        monedas_totales     = _d.monedas_totales;
        logros              = _d.logros;
    };
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Dificultad que crece linealmente | Aburrido 30 s, imposible a los 2 min | Crecimiento con `sqrt()`; ajusta ejes por separado |
| Solo subir la velocidad | El juego se vuelve repetitivo | Añade patrones nuevos cada cierto tiempo |
| Reinicio lento (más de 2 s) | El jugador cierra el juego | Menos de 60 frames hasta volver a controlar |
| Muerte sin explicación | El jugador se frustra y culpa al juego | Resalta al asesino + pausa antes del game over |
| Puntuación sin multiplicador | No hay razón para arriesgarse | Combo con decaimiento temporal |
| Combo que solo se rompe al fallar | Se puede "farmeear" quieto | Decaimiento por tiempo |
| Sin *near miss* | Casi morir es solo frustración | Puntos + tiempo bala al pasar cerca |
| Récords sin nombre del jugador | Nadie siente el récord como suyo | Teclado virtual para 3-8 caracteres |
| Tabla de récords vacía al principio | No hay objetivo que batir | Rellena con récords "CPU" por defecto |
| Guardar el récord como string | "900" > "1000" al comparar | `real()` al leer, o guarda JSON con números |
| Doble muerte (dos colisiones en un frame) | Se suman dos game overs | Flag `global.muerto` |
| `keyboard_lastchar` sin limpiar | Se repite la letra 60 veces por segundo | `keyboard_clear()` tras procesar |

---

## 8. Cómo escalarlo

1. **Más patrones de obstáculos** — la variedad es el contenido de un arcade.
   Apunta a 15-20 patrones repartidos en 5 niveles de dificultad.
2. **Power-ups temporales** — imán, escudo, tiempo lento. Dan picos de poder
   que rompen la monotonía.
3. **Misiones diarias** — "consigue 3 near misses en una partida". Da una
   razón para volver mañana.
4. **Desbloqueos cosméticos** — skins compradas con monedas.
5. **Tabla de clasificación online** — ver receta 14. Hazlo al final.
6. **Modo práctica** — empiezas en el minuto 2 para practicar la parte difícil.
7. **Replay de la mejor partida** — graba el input; como el juego es
   determinista si fijas la semilla, sale casi gratis.

**Cuándo pasar a otra receta:** los sistemas de puntuación y dificultad que
has montado aquí son directamente reutilizables en el shmup (receta 03) y en
el supervivencia (receta 09).

---

## 9. Fuentes

- **Make Your Own Arcade Space Shooter** (tutorial oficial, GML Code y GML
  Visual) — el proyecto "Space Rocks" moderno —
  https://gamemaker.io/tutorials/make-arcade-space-shooter
- **How To Move And Collide In GameMaker** —
  https://gamemaker.io/tutorials/easy-move-collide
- **How To Optimise Your Games** (tutorial oficial) —
  https://gamemaker.io/tutorials/how-to-optimise-your-games
- Manual oficial — Teclado (`keyboard_check`, `keyboard_check_pressed`,
  `keyboard_lastchar`, `keyboard_clear`, `keyboard_lastkey`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/Keyboard_Input.htm
- Manual oficial — `array_sort`, `array_resize`, `array_delete` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm
- Manual oficial — `game_get_speed(gamespeed_fps)` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/General_Game_Control.htm
- Manual oficial — `room_restart`, `merge_color`, `string_format` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference.htm
- Receta propia: **15 — Game feel y juice** (shake, hit stop, squash, tweens,
  partículas, texto flotante)
