# 12 — Carreras y vehículos

> **Dificultad:** media‑avanzada
> El género más olvidado en los tutoriales de GameMaker y uno de los más
> gratificantes, porque el *game feel* del vehículo ES el juego.

---

## 1. Visión general

En un juego de carreras el jugador no controla un personaje: controla un
**sistema de inercia**. Cada decisión (frenar, girar, acelerar) tarda en
producir efecto, y esa latencia es exactamente lo que hace que conducir se
sienta bien.

**Lo que define al género:**

- **El vehículo tiene masa.** No cambia de dirección instantáneamente.
- **La trazada importa**: frenar antes de la curva, acelerar en la salida.
- **El ritmo lo marca el circuito**, no el jugador. El jugador se adapta a él.
- **Los rivales son el contenido.** Sin IA convincente, una carrera es un
  contrarreloj.

**Referencias:** *Micro Machines* (el referente del arcade top-down en 2D),
*Super Sprint*, *Mario Kart* (SNES, Mode 7), *Rocket League* (3D),
*Death Rally*. En GameMaker, el top-down arcade es la opción natural: la
vista cenital evita tener que simular perspectiva.

**Subgéneros:**

| Subgénero | Vista | Física |
|---|---|---|
| Arcade top-down | Cenital | Simplificada, muy permisiva |
| Arcade con pseudo-3D | Detrás del coche | proyección tipo Mode 7 |
| *Kart* | Detrás | Muy arcade, con ítems |
| Simulación | Detrás / cockpit | Neumáticos, suspensión, aerodinámica |
| *Rally* | Detrás | Superficies con agarre variable |

---

## 2. Arquitectura recomendada

### Jerarquía de objetos

```
objVehicle           (padre: física compartida)
├── objPlayerCar
└── objAICar
objTrack             (controller: waypoints, checkpoints, vueltas)
objWaypoint          (punto de la trazada)
objCheckpoint        (línea de control)
objTerrainZone       (zona con agarre distinto: hierba, gravilla, hielo)
objPickup            (turbo, monedas)
objRaceManager       (cuenta atrás, clasificación, fin de carrera)
objCamera
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `VehicleConfig` | Aceleración, frenado, giro, agarre, masa |
| `RaceState` | Vueltas, tiempos, clasificación |
| `AILine` | La trazada que sigue un rival |
| `LapTime` | Tiempo por vuelta y mejor vuelta |

---

## 3. El bucle central (core loop)

```
┌─ Begin Step ─────────────────────────────────────────────┐
│ 1. Leer input (acelerar, frenar, girar, freno de mano)   │
└──────────────────────────────────────────────────────────┘
┌─ Step ───────────────────────────────────────────────────┐
│ 2. Determinar el agarre según el terreno bajo el coche     │
│ 3. Aplicar aceleración / frenado a lo largo del eje        │
│ 4. Girar: la dirección depende de la velocidad             │
│ 5. Separar la velocidad en LONGITUDINAL y LATERAL          │
│ 6. Aplicar resistencia al deslizamiento lateral (agarre)   │
│ 7. Recomponer y mover con colisión                        │
│ 8. Deriva: ¿el ángulo de deslizamiento supera el umbral?   │
│ 9. Checkpoints: ¿pasó por el siguiente? ¿completó vuelta?  │
│ 10. Actualizar clasificación                              │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Sistemas clave

### 4.1 Física arcade vs simulación

**Arcade (recomendada para empezar).** El modelo se basa en dos vectores:

```
velocidad_longitudinal  → a lo largo del morro del coche
velocidad_lateral       → perpendicular (el deslizamiento)
```

Cada frame:
1. El input modifica la velocidad longitudinal (acelera / frena).
2. El giro rota el morro, **sin** rotar la velocidad.
3. El deslizamiento lateral se reduce según el agarre.
4. Se recomponen ambos vectores y se mueve.

Ese desfase entre "hacia dónde apunta el coche" y "hacia dónde va" es **la
deriva**, y es la clave de la sensación.

**Simulación.** Modelas neumáticos con curvas de fuerza lateral, suspensión
con muelles, transferencia de peso, aerodinámica. Es otro mundo. No lo hagas
hasta que el arcade te salga perfecto.

### 4.2 El parámetro que decide la sensación: la reducción lateral

```gml
vel_lateral *= factor_agarre;   // 0.0 = hielo, 0.95 = raíles
```

| `factor_agarre` | Sensación |
|---|---|
| 0.98 | Raíles; el coche va donde apunta. Muy fácil. |
| 0.90 | Arcade clásico; algo de inercia |
| 0.80 | Deriva fácil; requiere contravolante |
| 0.60 | Muy resbaladizo; hielo |

Empieza en 0.90 y ajusta.

### 4.3 Giro dependiente de la velocidad

Un coche parado no gira. Un coche muy rápido gira poco (o vuelca). Modela la
tasa de giro como una curva:

```gml
tasa_giro = giro_max * (1 - exp(-velocidad / velocidad_referencia));
```

Con eso, a poca velocidad giras despacio (poco recorrido) y a media velocidad
es donde más giras. Es lo que hace que aparcar sea posible y que a 200 km/h
no puedas hacer un trompo instantáneo.

### 4.4 Terreno

Zonas con agarre y resistencia distintos:

| Superficie | Agarre | Resistencia | Efecto |
|---|---|---|---|
| Asfalto | 1.0 | 1.0 | Referencia |
| Hierba | 0.6 | 2.5 | Frena y ensucia el paso |
| Gravilla | 0.75 | 1.6 | Desliza |
| Hielo | 0.25 | 0.9 | Casi sin control |
| *Boost pad* | 1.0 | 0.0 | Acelera |

Implementación: una grid de terreno o zonas rectangulares. Para top-down,
lo más eficiente es un tilemap de terreno consultado con
`tilemap_get_at_pixel()`.

### 4.5 IA de rivales

La IA de carreras tiene tres niveles de calidad:

| Nivel | Cómo | Resultado |
|---|---|---|
| **Básica** | Seguir waypoints con *steering* | Va por el centro, aburrido |
| **Buena** | Waypoints + anticipación (frenar antes de curva) | Compite bien |
| **Excelente** | Trazada óptima + *rubber banding* controlado | Divertido y justo |

La pieza clave es la **anticipación**: la IA mira 2-3 waypoints por delante y
reduce la velocidad si la curva que viene es cerrada.

### 4.6 *Rubber banding*

Los rivales se aceleran si van muy por detrás y se frenan si van muy por
delante. Es polémico pero necesario en arcade: sin él, el jugador bueno gana
por 30 segundos y el malo pierde por 30.

```gml
// Sutil: nunca más de ±15 % de la velocidad
var _diferencia = distancia_jugador - distancia_ia;
var _ajuste = clamp(_diferencia / 2000, -0.15, 0.15);
velocidad_maxima_ia = velocidad_base * (1 + _ajuste);
```

### 4.7 Checkpoints y vueltas

Un array de checkpoints en orden. El coche debe pasarlos en secuencia: así
evitas que corte el circuito.

```gml
siguiente_checkpoint = 0;
// Al tocar el checkpoint con índice == siguiente_checkpoint → avanzar
// Al pasar el último → vuelta++ y siguiente_checkpoint = 0
```

Guarda el tiempo de cada vuelta y la mejor. El orden de clasificación es:
vueltas completadas (desc) → último checkpoint (desc) → distancia al
siguiente checkpoint (asc).

---

## 5. Código base

### 5.0 Configuración del vehículo

```gml
// ---------------------------------------------------------------------------
// scr_vehicle_config
// ---------------------------------------------------------------------------

/// @func VehicleConfig(
///          _aceleracion, _frenado, _vel_max, _giro_max, _agarre, _resistencia)
function VehicleConfig(
    _aceleracion, _frenado, _vel_max, _giro_max, _agarre, _resistencia
) constructor
{
    // --- Longitudinal ---
    aceleracion = _aceleracion;     // px/frame² a tope
    frenado     = _frenado;         // px/frame² al frenar
    vel_max     = _vel_max;         // px/frame
    vel_max_reversa = _vel_max * 0.35;

    // --- Dirección ---
    giro_max    = _giro_max;        // grados/frame a la velocidad óptima
    vel_ref_giro = _vel_max * 0.55; // velocidad de máxima capacidad de giro

    // --- Agarre y rozamiento ---
    agarre      = _agarre;          // 0..1: cuánto se reduce la velocidad lateral
    resistencia = _resistencia;     // frenado natural por frame (0.02 típico)
    resistencia_lateral = 0.92;     // rozamiento lateral (deriva)

    // --- Deriva ---
    umbral_deriva = 3.5;            // vel_lateral mínima para "derivar"
    freno_mano_factor = 0.35;       // el freno de mano reduce el agarre
}
```

### 5.1 Física del vehículo (arcade)

```gml
// ---------------------------------------------------------------------------
// objVehicle — Create
// ---------------------------------------------------------------------------
config = new VehicleConfig(0.28, 0.42, 9.0, 3.2, 0.90, 0.015);

vel_x = 0;
vel_y = 0;

angulo = 0;              // hacia dónde apunta el morro
velocidad = 0;           // velocidad escalar (solo lectura, para la UI)

derivando = false;
freno_mano = false;

// Terreno actual
agarre_terreno    = 1.0;
resistencia_terreno = 1.0;
```

```gml
// ---------------------------------------------------------------------------
// objVehicle — Step
// ---------------------------------------------------------------------------
// --- 1. Leer el terreno ----------------------------------------------------------
leer_terreno();

// --- 2. Input ----------------------------------------------------------------------
var _acel = 0;
var _freno = 0;
var _giro = 0;

with (objPlayerCar)
{
    _acel  = keyboard_check(vk_up)    || keyboard_check(ord("W"));
    _freno = keyboard_check(vk_down)  || keyboard_check(ord("S"));
    _giro  = (keyboard_check(vk_right) || keyboard_check(ord("D")))
           - (keyboard_check(vk_left)  || keyboard_check(ord("A")));
    freno_mano = keyboard_check(vk_space);
}

// --- 3. Descomponer la velocidad en LONGITUDINAL y LATERAL -----------------------------
// Este es el corazón del modelo arcade.
var _cos_a = dcos(angulo);
var _sin_a = dsin(angulo);

// Eje longitudinal: hacia donde apunta el morro
var _long_x =  _cos_a;
var _long_y = -_sin_a;      // - porque en pantalla Y crece hacia abajo

// Eje lateral: 90° respecto al longitudinal
var _lat_x =  _sin_a;
var _lat_y =  _cos_a;

var _v_long = dot_product(vel_x, vel_y, _long_x, _long_y);
var _v_lat  = dot_product(vel_x, vel_y, _lat_x,  _lat_y);

// --- 4. Aceleración y frenado sobre el eje LONGITUDINAL ------------------------------
if (_acel)
{
    _v_long += config.aceleracion * agarre_terreno;
}
if (_freno)
{
    if (_v_long > 0.2)
    {
        _v_long -= config.frenado * agarre_terreno;
    }
    else
    {
        // Marcha atrás
        _v_long -= config.aceleracion * 0.5;
    }
}

// Limitar
_v_long = clamp(_v_long, -config.vel_max_reversa,
                          config.vel_max * resistencia_terreno);

// --- 5. Resistencia al avance (rozamiento) -----------------------------------------------
_v_long *= (1 - config.resistencia);

// --- 6. Giro ---------------------------------------------------------------------------------
// La capacidad de giro depende de la velocidad: parado no giras; muy rápido, poco.
var _vel_abs = abs(_v_long);
var _capacidad = 1 - exp(-_vel_abs / config.vel_ref_giro);

// Si vas marcha atrás, el giro se invierte
var _sentido = (_v_long < -0.1) ? -1 : 1;

angulo += _giro * config.giro_max * _capacidad * _sentido;

// --- 7. Agarre lateral: reducir el deslizamiento ----------------------------------------
var _agarre_efectivo = config.agarre * agarre_terreno;
if (freno_mano) _agarre_efectivo *= config.freno_mano_factor;

_v_lat *= (1 - _agarre_efectivo * 0.5) * config.resistencia_lateral;

// --- 8. Deriva --------------------------------------------------------------------------------
derivando = (abs(_v_lat) > config.umbral_deriva);

if (derivando && _vel_abs > 2)
{
    // Partículas de humo de los neumáticos
    if (global.frame_count mod 2 == 0)
    {
        part_particles_create(objFx.ps, x, y, objFx.pt_smoke, 1);
    }
    // Sonido de derrape con pitch según la intensidad
    if (!audio_is_playing(sndSkid)) global.skid_sound = audio_play_sound(sndSkid, 5, true);
    audio_sound_pitch(global.skid_sound, 0.9 + (abs(_v_lat) * 0.05));
}
else if (audio_is_playing(global.skid_sound))
{
    audio_stop_sound(global.skid_sound);
}

// --- 9. Recomponer el vector de velocidad y mover --------------------------------------
vel_x = (_long_x * _v_long) + (_lat_x * _v_lat);
vel_y = (_long_y * _v_long) + (_lat_y * _v_lat);

velocidad = point_distance(0, 0, vel_x, vel_y);

// --- 10. Colisión con el circuito ------------------------------------------------------------
var _anterior_x = x;
var _anterior_y = y;

move_and_collide(vel_x, vel_y, objWall, 4, 0, 0, config.vel_max, -1);

// ¿Chocó? Perder velocidad y rebotar un poco
if (abs(x - _anterior_x) + abs(y - _anterior_y) <
    abs(vel_x) + abs(vel_y) - 0.5)
{
    // Impacto: reducir la velocidad un 40 % y dar feedback
    vel_x *= 0.6;
    vel_y *= 0.6;
    camera_shake(0.18);
    audio_play_sound(sndBump, 8, false);
}

// --- 11. Sprite ----------------------------------------------------------------------------
image_angle = angulo;
depth = -y;
```

```gml
// ---------------------------------------------------------------------------
// scr_math_helpers
// ---------------------------------------------------------------------------

// NOTA: dot_product() es una función NATIVA de GameMaker.
// Firma: dot_product(x1, y1, x2, y2) → producto escalar de dos vectores 2D.
// No la redefinas: duplicar una función integrada es un error de compilación.
// La usamos directamente para descomponer la velocidad en los ejes
// longitudinal y lateral del vehículo:
//
//   var _v_long = dot_product(vel_x, vel_y, _long_x, _long_y);
//   var _v_lat  = dot_product(vel_x, vel_y, _lat_x,  _lat_y);
//
// Otras funciones nativas de álgebra vectorial que conviene conocer:
//   dot_product_3d(x1, y1, z1, x2, y2, z2)
//   point_distance_3d(...)  ·  angle_difference(dest, src)
```

### 5.1 bis · El motor del vehículo: sonido

El derrape de arriba ya usa `audio_sound_pitch` con un parámetro continuo (la velocidad lateral);
el motor es el caso canónico de la misma técnica, y se reutiliza en cualquier maquinaria: un
ventilador, una nave, una cinta transportadora. Dos formas de resolverlo, de más simple a más
realista.

**Opción A — un bucle con el tono siguiendo las revoluciones.** Un único sonido de motor en
bucle, cuyo `pitch` sube con la velocidad. Barata y suficiente para un arcade:

```gml
// objVehicle — Create
snd_motor_voz = audio_play_sound(sndMotor, 8, true);

// objVehicle — Step, después del bloque de física de §5.1 (ya tienes `_vel_abs` y `velocidad`)
// De 0,7 (ralentí) a 2,2 (a fondo): el rango que "suena a motor" sin desafinar hasta el chillido
var _revoluciones = clamp(velocidad / config.vel_max, 0, 1);
audio_sound_pitch(snd_motor_voz, lerp(0.7, 2.2, _revoluciones));
audio_sound_gain(snd_motor_voz, lerp(0.5, 1, _revoluciones), 0);   // también sube el volumen

// objVehicle — Clean Up
audio_stop_sound(snd_motor_voz);
```

> ⚠️ **Un solo `pitch` no distingue acelerar de ir a velocidad de crucero.** El motor de un coche
> real suena distinto pisando el acelerador que soltándolo a la misma velocidad (efecto de
> retención). Si te hace falta esa diferencia, súmale un `lerp` extra sobre `_acel` a la ganancia;
> para la mayoría de arcades no compensa la complejidad.

**Opción B — tres capas con crossfade por velocidad.** Más fiel y más caro de producir (tres
tomas grabadas o sintetizadas en vez de una), pero evita el «efecto disco rayado acelerado» de
estirar un único *pitch* en un rango muy amplio: ralentí, medio y alto suenan todas al mismo
tono real, y lo que cambia es cuál se oye.

```gml
// objVehicle — Create
motor = {
    ralenti : audio_play_sound(sndMotorRalenti, 8, true),
    medio   : audio_play_sound(sndMotorMedio,   8, true),
    alto    : audio_play_sound(sndMotorAlto,    8, true),
};
audio_sound_gain(motor.ralenti, 1, 0);
audio_sound_gain(motor.medio,   0, 0);
audio_sound_gain(motor.alto,    0, 0);

// objVehicle — Step, después del bloque de física de §5.1
var _revoluciones = clamp(velocidad / config.vel_max, 0, 1);   // 0 = parado, 1 = a fondo
// Crossfade en dos tramos: ralentí→medio hasta el 50 %, medio→alto el resto. 150 ms de fundido:
// más que eso y el cambio de capa se nota como un "escalón" al acelerar a fondo.
var _g_ralenti = clamp(1 - _revoluciones * 2,        0, 1);
var _g_medio   = clamp(1 - abs(_revoluciones - 0.5) * 2, 0, 1);
var _g_alto    = clamp((_revoluciones - 0.5) * 2,    0, 1);
audio_sound_gain(motor.ralenti, _g_ralenti, 150);
audio_sound_gain(motor.medio,   _g_medio,   150);
audio_sound_gain(motor.alto,    _g_alto,    150);

// objVehicle — Clean Up
audio_stop_sound(motor.ralenti);  audio_stop_sound(motor.medio);  audio_stop_sound(motor.alto);
```

> 💡 **Las tres capas se lanzan TODAS en bucle desde el Create**, exactamente como en el *vertical
> layering* de [04 · 26](./26%20-%20Música%20adaptativa%20por%20capas.md): solo cambias su
> ganancia, nunca las paras y las vuelves a lanzar, o se desincronizan entre sí igual que las
> capas de una pista.

### 5.2 Terreno

> ⚠️ **`leer_terreno()` va DENTRO del `Create` de `objVehicle` (añádela al bloque de §2,
> no la dejes en el `Step` ni suelta).** Lee `x`/`y` de `self`, así que no puede vivir en
> un script sin un `with (objVehicle)` — pero SÍ puede vivir en un evento, porque
> `objPlayerCar` y `objAICar` son hijos de `objVehicle` (§2) y su `Create` llama a
> `event_inherited()` (ver el de `objAICar` más abajo): eso la registra como variable de
> instancia del propio coche, no solo del padre, y ya queda disponible en TODOS sus
> eventos posteriores — Step incluido. Si la declaras en el `Step` de `objVehicle` en vez
> del `Create`, deja de heredarse (ningún `objAICar`/`objPlayerCar` llama a
> `event_inherited()` en su propio `Step`) y revienta con
> `Variable X.leer_terreno(...) not set before reading it`.

```gml
// ---------------------------------------------------------------------------
// objVehicle — Create (añadir) — leer_terreno()
// ---------------------------------------------------------------------------
function leer_terreno()
{
    var _tile = tilemap_get_at_pixel(objTrack.tilemap_terreno, x, y);

    // Índices de tile según tu tileset de terreno.
    // Ajusta los números a tu proyecto.
    switch (_tile)
    {
        case 0:                             // fuera del circuito / hierba
            agarre_terreno      = 0.60;
            resistencia_terreno = 0.45;
            break;

        case 1:                             // asfalto
            agarre_terreno      = 1.00;
            resistencia_terreno = 1.00;
            break;

        case 2:                             // gravilla
            agarre_terreno      = 0.75;
            resistencia_terreno = 0.70;
            break;

        case 3:                             // hielo
            agarre_terreno      = 0.25;
            resistencia_terreno = 0.95;
            break;

        case 4:                             // boost pad: se gestiona aparte
            agarre_terreno      = 1.00;
            resistencia_terreno = 1.00;
            aplicar_boost();
            break;

        default:
            agarre_terreno      = 0.70;
            resistencia_terreno = 0.80;
    }
}

/// @func aplicar_boost()
function aplicar_boost()
{
    if (turbo_cooldown > 0) return;

    // Impulso en la dirección del morro
    var _impulso = 4.5;
    vel_x += dcos(angulo)  * _impulso;
    vel_y += -dsin(angulo) * _impulso;

    turbo_cooldown = 60;

    // Juice
    camera_shake(0.25);
    time_slow(0.75, 10);
    audio_play_sound(sndBoost, 10, false);
    part_particles_create(objFx.ps, x, y, objFx.pt_spark, 20);
}
```

```gml
// ---------------------------------------------------------------------------
// objVehicle — Create (añadir)
// ---------------------------------------------------------------------------
turbo_cooldown = 0;

// ---------------------------------------------------------------------------
// objVehicle — Step (añadir al principio)
// ---------------------------------------------------------------------------
if (turbo_cooldown > 0) turbo_cooldown--;
```

### 5.3 Circuito con waypoints y checkpoints

```gml
// ---------------------------------------------------------------------------
// objTrack — Create
// ---------------------------------------------------------------------------
// Tilemap de terreno
tilemap_terreno = layer_tilemap_get_id(layer_get_id("Tiles_Terrain"));

// Waypoints: la trazada. Se colocan con objetos en la room.
waypoints = [];
with (objWaypoint)
{
    array_push(other.waypoints, { x: x, y: y, indice: waypoint_index });
}

// Ordenar por índice (por si el orden de creación no coincide)
array_sort(waypoints, function(_a, _b)
{
    return (_a.indice < _b.indice) ? -1 : ((_a.indice > _b.indice) ? 1 : 0);
});

// Checkpoints: subconjunto de los waypoints que hay que pasar en orden
checkpoints = [];
with (objCheckpoint)
{
    array_push(other.checkpoints, { x: x, y: y, indice: checkpoint_index });
}
array_sort(checkpoints, function(_a, _b)
{
    return (_a.indice < _b.indice) ? -1 : ((_a.indice > _b.indice) ? 1 : 0);
});

total_vueltas = 3;

show_debug_message("Circuito: " + string(array_length(waypoints)) +
                   " waypoints, " + string(array_length(checkpoints)) +
                   " checkpoints");
```

```gml
// ---------------------------------------------------------------------------
// objVehicle — Create (añadir)
// ---------------------------------------------------------------------------
siguiente_checkpoint = 0;
vuelta_actual        = 1;
vuelta_inicio_frames = 0;
tiempos_vueltas      = [];
mejor_vuelta         = -1;
terminado            = false;
distancia_recorrida  = 0;
```

```gml
// ---------------------------------------------------------------------------
// objVehicle — Step (checkpoints y vueltas)
// ---------------------------------------------------------------------------
if (!terminado && array_length(objTrack.checkpoints) > 0)
{
    var _cp = objTrack.checkpoints[siguiente_checkpoint];

    // ¿Está lo bastante cerca del checkpoint que toca?
    if (point_distance(x, y, _cp.x, _cp.y) < 64)
    {
        siguiente_checkpoint++;

        if (siguiente_checkpoint >= array_length(objTrack.checkpoints))
        {
            // --- Vuelta completada ---------------------------------------------------
            siguiente_checkpoint = 0;

            var _frames_vuelta = global.frame_count - vuelta_inicio_frames;
            array_push(tiempos_vueltas, _frames_vuelta);

            if (mejor_vuelta < 0 || _frames_vuelta < mejor_vuelta)
            {
                mejor_vuelta = _frames_vuelta;
            }

            vuelta_inicio_frames = global.frame_count;

            if (vuelta_actual >= objTrack.total_vueltas)
            {
                terminado = true;
                on_carrera_terminada();
            }
            else
            {
                vuelta_actual++;

                // Feedback: es importante que el jugador note que avanza
                fx_floating_text(x, y - 30,
                                 "VUELTA " + string(vuelta_actual) + " / " +
                                 string(objTrack.total_vueltas), c_yellow);
                audio_play_sound(sndLap, 10, false);
            }
        }
        else
        {
            // Checkpoint intermedio: sonido corto
            audio_play_sound(sndCheckpoint, 6, false);
        }
    }
}

// Distancia recorrida (para desempatar clasificaciones)
distancia_recorrida += point_distance(0, 0, vel_x, vel_y);
```

```gml
// ---------------------------------------------------------------------------
// scr_race_time
// ---------------------------------------------------------------------------

/// @func frames_a_tiempo(_frames)
/// @devuelve "1:23.45"
function frames_a_tiempo(_frames)
{
    var _fps = game_get_speed(gamespeed_fps);
    var _segundos_totales = _frames / _fps;

    var _minutos = floor(_segundos_totales / 60);
    var _segundos = floor(_segundos_totales mod 60);
    var _centesimas = floor((_segundos_totales * 100) mod 100);

    return string(_minutos) + ":" +
           string_format(_segundos, 2, 0) + "." +
           string_format(_centesimas, 2, 0);
}
```

### 5.4 IA de rivales

```gml
// ---------------------------------------------------------------------------
// objAICar — Create
// ---------------------------------------------------------------------------
event_inherited();

config = new VehicleConfig(0.26, 0.40, 8.6, 3.0, 0.90, 0.015);

// Waypoint al que se dirige
waypoint_objetivo = 1;

// Personalidad: varía entre rivales
agresividad   = random_range(0.85, 1.05);    // multiplicador de velocidad
precision     = random_range(0.80, 0.98);    // cuánto se desvía de la trazada

// Anticipación
velocidad_objetivo = config.vel_max;
```

```gml
// ---------------------------------------------------------------------------
// objAICar — Step
// ---------------------------------------------------------------------------
leer_terreno();

// --- 1. Waypoint objetivo -------------------------------------------------------------
var _wps = objTrack.waypoints;
if (array_length(_wps) < 2) exit;

var _wp = _wps[waypoint_objetivo mod array_length(_wps)];

// ¿Ya lo alcanzó?
if (point_distance(x, y, _wp.x, _wp.y) < 56)
{
    waypoint_objetivo = (waypoint_objetivo + 1) mod array_length(_wps);
    _wp = _wps[waypoint_objetivo];
}

// --- 2. ANTICIPACIÓN: mirar 2 waypoints por delante -----------------------------------
// Esto es lo que separa a una IA que compite de una que solo sigue una línea.
var _wp_adelante = _wps[(waypoint_objetivo + 2) mod array_length(_wps)];

var _dir_actual  = point_direction(x, y, _wp.x, _wp.y);
var _dir_adelante = point_direction(_wp.x, _wp.y, _wp_adelante.x, _wp_adelante.y);

// ¿Cuánto cambia la dirección? Mucho = curva cerrada = hay que frenar
var _curvatura = abs(angle_difference(_dir_adelante, _dir_actual));

// Ajustar la velocidad objetivo según la curvatura
velocidad_objetivo = config.vel_max * agresividad *
                     lerp(1.0, 0.45, clamp(_curvatura / 90, 0, 1));

// --- 3. Rubber banding sutil ---------------------------------------------------------------
var _jugador = instance_find(objPlayerCar, 0);
if (_jugador != noone)
{
    var _diff_dist = _jugador.distancia_recorrida - distancia_recorrida;
    var _ajuste = clamp(_diff_dist / 2500, -0.12, 0.12);
    velocidad_objetivo *= (1 + _ajuste);
}

// --- 4. Calcular el input equivalente ----------------------------------------------------
var _direccion_deseada = point_direction(x, y, _wp.x, _wp.y);

// Girar hacia el objetivo
var _diff_angulo = angle_difference(_direccion_deseada, angulo);
var _giro = clamp(_diff_angulo / 12, -1, 1);

// Acelerar o frenar según la velocidad objetivo
var _vel_actual = point_distance(0, 0, vel_x, vel_y);
var _acel  = (_vel_actual < velocidad_objetivo) ? 1 : 0;
var _freno = (_vel_actual > velocidad_objetivo * 1.15) ? 1 : 0;

// --- 5. Aplicar la misma física que al jugador ------------------------------------
// Descomposición longitudinal / lateral (idéntica a objVehicle)
var _long_x =  dcos(angulo);
var _long_y = -dsin(angulo);
var _lat_x  =  dsin(angulo);
var _lat_y  =  dcos(angulo);

var _v_long = dot_product(vel_x, vel_y, _long_x, _long_y);
var _v_lat  = dot_product(vel_x, vel_y, _lat_x,  _lat_y);

if (_acel)  _v_long += config.aceleracion * agarre_terreno;
if (_freno) _v_long -= config.frenado * agarre_terreno;

_v_long = clamp(_v_long, -config.vel_max_reversa, config.vel_max * resistencia_terreno);
_v_long *= (1 - config.resistencia);

// Giro
var _capacidad = 1 - exp(-abs(_v_long) / config.vel_ref_giro);
angulo += _giro * config.giro_max * _capacidad;

// Agarre lateral
_v_lat *= (1 - (config.agarre * agarre_terreno) * 0.5) * config.resistencia_lateral;

// Recomponer y mover
vel_x = (_long_x * _v_long) + (_lat_x * _v_lat);
vel_y = (_long_y * _v_long) + (_lat_y * _v_lat);

move_and_collide(vel_x, vel_y, objWall, 4, 0, 0, config.vel_max, -1);

image_angle = angulo;
depth = -y;

distancia_recorrida += point_distance(0, 0, vel_x, vel_y);
```

### 5.5 Clasificación

```gml
// ---------------------------------------------------------------------------
// objRaceManager — Create
// ---------------------------------------------------------------------------
clasificacion = [];
cuenta_atras   = 180;      // 3 segundos
carrera_empezada = false;
```

```gml
// ---------------------------------------------------------------------------
// objRaceManager — Step
// ---------------------------------------------------------------------------
// --- Cuenta atrás ------------------------------------------------------------------
if (!carrera_empezada)
{
    cuenta_atras--;

    if (cuenta_atras == 120) audio_play_sound(sndCount, 10, false);
    if (cuenta_atras == 60)  audio_play_sound(sndCount, 10, false);

    if (cuenta_atras <= 0)
    {
        carrera_empezada = true;
        audio_play_sound(sndGo, 10, false);

        global.frame_count = 0;
        with (objVehicle) vuelta_inicio_frames = 0;
    }
    exit;
}

// --- Recalcular la clasificación cada 15 frames -----------------------------------
if (global.frame_count mod 15 == 0)
{
    recalcular_clasificacion();
}
```

```gml
// ---------------------------------------------------------------------------
// objRaceManager — recalcular_clasificacion()
// ---------------------------------------------------------------------------
function recalcular_clasificacion()
{
    // Recoger todos los vehículos
    var _vehiculos = [];
    with (objVehicle) array_push(_vehiculos, id);

    // Ordenar por: vueltas (desc) → checkpoint (desc) →
    //              distancia al siguiente checkpoint (asc)
    array_sort(_vehiculos, function(_a, _b)
    {
        // 1. Vueltas completadas
        if (_a.vuelta_actual != _b.vuelta_actual)
        {
            return (_a.vuelta_actual > _b.vuelta_actual) ? -1 : 1;
        }

        // 2. Checkpoint alcanzado
        if (_a.siguiente_checkpoint != _b.siguiente_checkpoint)
        {
            return (_a.siguiente_checkpoint > _b.siguiente_checkpoint) ? -1 : 1;
        }

        // 3. Distancia al siguiente checkpoint (el más cerca va delante)
        var _da = distancia_a_checkpoint(_a);
        var _db = distancia_a_checkpoint(_b);
        return (_da < _db) ? -1 : 1;
    });

    // Asignar posiciones
    for (var _i = 0; _i < array_length(_vehiculos); _i++)
    {
        _vehiculos[_i].posicion = _i + 1;
    }

    clasificacion = _vehiculos;
}

/// @func distancia_a_checkpoint(_vehiculo)
function distancia_a_checkpoint(_vehiculo)
{
    var _cps = objTrack.checkpoints;
    if (array_length(_cps) == 0) return 0;

    var _cp = _cps[_vehiculo.siguiente_checkpoint mod array_length(_cps)];
    return point_distance(_vehiculo.x, _vehiculo.y, _cp.x, _cp.y);
}
```

### 5.6 Cámara para carreras

```gml
// ---------------------------------------------------------------------------
// objCamera — Create
// ---------------------------------------------------------------------------
cam = view_camera[0];
cam_x = x;
cam_y = y;

// La cámara se adelanta en la dirección de la marcha: esencial en carreras
lookahead_dist = 90;
suavizado      = 0.10;

// Zoom dinámico con la velocidad: más rápido = más lejos ves
zoom_base  = 1.0;
zoom_actual = 1.0;
```

```gml
// ---------------------------------------------------------------------------
// objCamera — End Step
// ---------------------------------------------------------------------------
if (!instance_exists(objPlayerCar)) exit;

var _coche = objPlayerCar;
var _vw_base = camera_get_view_width(cam);
var _vh_base = camera_get_view_height(cam);

// --- 1. Zoom según la velocidad -------------------------------------------------------
var _ratio = clamp(_coche.velocidad / _coche.config.vel_max, 0, 1);
var _zoom_objetivo = zoom_base * lerp(1.0, 0.82, _ratio);
zoom_actual = lerp(zoom_actual, _zoom_objetivo, 0.05);

var _vw = _vw_base / zoom_actual;
var _vh = _vh_base / zoom_actual;
camera_set_view_size(cam, round(_vw), round(_vh));

// --- 2. Look-ahead: mirar hacia donde va el coche --------------------------------------
var _lx = lengthdir_x(lookahead_dist * _ratio, _coche.angulo);
var _ly = lengthdir_y(lookahead_dist * _ratio, _coche.angulo);

var _tx = _coche.x + _lx;
var _ty = _coche.y + _ly;

// --- 3. Seguimiento suave ---------------------------------------------------------------
cam_x = lerp(cam_x, _tx, suavizado);
cam_y = lerp(cam_y, _ty, suavizado);

// --- 4. Clamp a la room ---------------------------------------------------------------------
cam_x = clamp(cam_x, _vw * 0.5, max(_vw * 0.5, room_width  - _vw * 0.5));
cam_y = clamp(cam_y, _vh * 0.5, max(_vh * 0.5, room_height - _vh * 0.5));

camera_set_view_pos(cam, round(cam_x - _vw * 0.5), round(cam_y - _vh * 0.5));
```

---

## 6. Gestión del estado del jugador

```gml
// ---------------------------------------------------------------------------
// scr_race_state
// ---------------------------------------------------------------------------

/// @func RaceState()
/// @desc Progreso del jugador entre carreras: desbloqueos y récords.
function RaceState() constructor
{
    circuitos_desbloqueados = ["circuito_1"];
    mejores_tiempos = {};     // { circuito_1: frames, ... }
    coches_desbloqueados = ["coche_base"];
    coche_actual = "coche_base";

    victorias = 0;
    carreras  = 0;
    podios    = 0;

    /// @desc Registra el final de una carrera.
    registrar = function(_circuito, _posicion, _tiempo_total, _mejor_vuelta)
    {
        carreras++;

        if (_posicion == 1) victorias++;
        if (_posicion <= 3) podios++;

        // Mejor tiempo del circuito
        if (!variable_struct_exists(mejores_tiempos, _circuito) ||
            _tiempo_total < mejores_tiempos[$ _circuito])
        {
            mejores_tiempos[$ _circuito] = _tiempo_total;
        }

        // Desbloquear el siguiente circuito al quedar en el podio
        if (_posicion <= 3)
        {
            desbloquear_siguiente(_circuito);
        }

        guardar();
    };

    desbloquear_siguiente = function(_circuito)
    {
        var _indice = array_find_index(circuitos_desbloqueados, _circuito);
        // (array_find_index no existe como nativo: usar bucle propio)
        var _pos = -1;
        for (var _i = 0; _i < array_length(circuitos_desbloqueados); _i++)
        {
            if (circuitos_desbloqueados[_i] == _circuito) { _pos = _i; break; }
        }

        var _siguiente = "circuito_" + string(_pos + 2);

        if (!array_contains(circuitos_desbloqueados, _siguiente))
        {
            array_push(circuitos_desbloqueados, _siguiente);
            show_debug_message("¡Circuito desbloqueado: " + _siguiente + "!");
        }
    };

    guardar = function()
    {
        var _data = {
            circuitos_desbloqueados: circuitos_desbloqueados,
            mejores_tiempos: mejores_tiempos,
            coches_desbloqueados: coches_desbloqueados,
            coche_actual: coche_actual,
            victorias: victorias,
            carreras: carreras,
            podios: podios
        };

        // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
        // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
        // 14 - Persistencia y archivos.md §1.
        var _f = file_text_open_write(game_save_id + "race_state.json");
        file_text_write_string(_f, json_stringify(_data));
        file_text_close(_f);
    };

    cargar = function()
    {
        var _path = game_save_id + "race_state.json";
        if (!file_exists(_path)) return;

        var _f = file_text_open_read(_path);
        var _d = json_parse(file_text_read_string(_f));
        file_text_close(_f);

        circuitos_desbloqueados = _d.circuitos_desbloqueados;
        mejores_tiempos         = _d.mejores_tiempos;
        coches_desbloqueados    = _d.coches_desbloqueados;
        coche_actual            = _d.coche_actual;
        victorias               = _d.victorias;
        carreras                = _d.carreras;
        podios                  = _d.podios;
    };
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Girar cambiando directamente el vector de velocidad | El coche va como un tanque sobre raíles; no hay deriva | Descomposición longitudinal/lateral |
| No descomponer la velocidad | El coche se desliza eternamente hacia un lado | Reduce la componente lateral cada frame |
| Giro constante sin depender de la velocidad | Puedes hacer trompos parado | `1 - exp(-vel / vel_ref)` |
| Gravedad/rozamiento nulo | El coche nunca frena | Resistencia ~0.015-0.03 por frame |
| Checkpoints solo en la meta | El jugador puede cortar el circuito | Array de checkpoints en secuencia |
| Sin cronómetro por vuelta | No hay sensación de mejora | `tiempos_vueltas` + `mejor_vuelta` |
| IA que sigue waypoints sin anticipación | Frena tarde y se sale en las curvas | Mirar 2-3 waypoints por delante |
| *Rubber banding* demasiado agresivo | Se nota que la IA hace trampas | Tope de ±12-15 % |
| Cámara centrada en el coche | No ves lo que viene | *Look-ahead* proporcional a la velocidad |
| Zoom fijo | A alta velocidad no te da tiempo a reaccionar | Zoom out según la velocidad |
| Recalcular la clasificación cada frame | Coste innecesario | Cada 15 frames |
| `move_and_collide` sin detectar el choque | El coche choca y sigue igual de rápido | Compara la posición prevista con la real |
| Deriva sin feedback | No sabes cuándo estás derrapando | Humo + sonido + shake |
| Motor con volumen fijo, sin `pitch` variable | El coche parece flotar; no se nota si acelera o va a tope | Bucle con `pitch` por revoluciones, o tres capas con crossfade (§5.1 bis) |

---

## 8. Cómo escalarlo

1. **Más superficies** — barro, nieve, agua (con *splash* y pérdida de control).
2. **Turbo y ítems** — *boost pads*, cajas de ítems estilo Mario Kart.
3. **Daño y reparación** — los golpes degradan el coche.
4. **Setup del vehículo** — ajustar agarre / velocidad / aceleración. Da
   profundidad sin trabajo extra.
5. **Modo contrarreloj con *ghosts*** — graba la posición del coche cada frame
   y reprodúcela como un fantasma semitransparente. Es adictivo y barato.
6. **Multijugador local en pantalla partida** — dos viewports con
   `camera_set_view_pos` sobre `view_camera[0]` y `[1]`.
7. **Pseudo-3D** — proyección en perspectiva del circuito (técnica Mode 7).
   Es el paso natural si quieres pasar del top-down.
8. **Editor de circuitos** — colocas waypoints en el editor y exportas a JSON.

**Cuándo pasar a otra receta:** el modelo de física longitudinal/lateral que
has montado sirve para cualquier vehículo: naves con inercia, barcos, incluso
personajes con impulso.

---

## 9. Fuentes

- Manual oficial — `move_and_collide` —
  https://manual.gamemaker.io/monthly/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement_And_Collisions/move_and_collide.htm
- Manual oficial — Ángulos y distancia (`point_direction`, `point_distance`,
  `lengthdir_x`, `angle_difference`, `dcos`, `dsin`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Angles_And_Distance.htm
- Manual oficial — Tilemaps (`layer_tilemap_get_id`, `tilemap_get_at_pixel`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Rooms/Tile_Map_Layers.htm
- Manual oficial — `array_sort`, `array_contains`, `array_push` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm
- Manual oficial — Cámaras (`camera_set_view_pos`, `camera_set_view_size`,
  `camera_get_view_width`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Cameras_And_Display/Cameras_And_Viewports.htm
- Manual oficial — Audio (`audio_is_playing`, `audio_sound_pitch`,
  `audio_stop_sound`, `audio_sound_gain`, `audio_play_sound`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio.htm
- Manual oficial — `game_get_speed(gamespeed_fps)` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/General_Game_Control.htm
- Receta propia: **15 — Game feel y juice** (shake, tiempo bala, partículas)
