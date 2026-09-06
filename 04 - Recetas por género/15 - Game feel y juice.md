# 15 — Game feel y juice

> **Dificultad:** media · **Receta transversal, léela mientras haces las demás**
> El *game feel* es la diferencia entre un juego que funciona y un juego que
> apetece jugar. No es decoración: es el canal por el que el jugador recibe
> información sobre lo que acaba de pasar.

---

## 1. Visión general

Cada acción del jugador debe generar una **respuesta en capas**. Cuando
disparas a un enemigo en un juego bien hecho, en ~300 ms ocurren siete cosas:

1. La bala impacta (partículas de chispas).
2. El enemigo parpadea en blanco (flash).
3. El enemigo retrocede (*knockback*).
4. El sprite del enemigo se aplasta (*squash*).
5. La pantalla tiembla (*screen shake*).
6. Suena un golpe seco, con pitch aleatorio.
7. El juego se congela 3 frames (*hit stop*).

Ninguna de esas siete cosas por separado es impresionante. Las siete a la vez,
en 300 ms, son las que hacen que el cerebro diga "esto pega".

**El principio rector:** el feedback no es adorno, es **información**. El
*hit stop* le dice al jugador "este golpe importó". El *screen shake* le dice
"esto fue grande". El *knockback* le dice "lo estás empujando". Si un efecto
no comunica nada, quítalo.

**Referencias:** *Celeste* (hit stop + squash), *Nuclear Throne* (shake
brutal), *Katana ZERO* (freeze frames + tiempo bala), *Downwell* (squash
extremo), *Enter the Gungeon* (partículas por todas partes), *Mario* (juice
clásico: anticipación en el salto, *squash* al aterrizar).

---

## 2. Arquitectura recomendada

### Principio: una única fuente de efectos

No repartas el código de efectos por veinte objetos. Centralízalo en un
controller al que cualquier objeto puede llamar:

```
objTime               (hit stop, time scale, congelación)
objCamera             (shake, zoom, offset, follow)
objFx                 (partículas, flashes, texto flotante, impactos)
objTweenManager       (actualiza todos los tweens activos)
```

### Jerarquía de efectos

```
objFx (persistente, sin sprite)
├── partículas por tipo (chispas, humo, sangre, polvo, confeti)
├── flashes de pantalla (color + alfa)
├── screen shake  → delega en objCamera
└── floating text (números de daño, "+100")
```

### Structs

| Struct | Responsabilidad |
|---|---|
| `Tween` | Una animación: propiedad, origen, destino, duración, curva |
| `Ease` | Funciones de interpolación puras |
| `ShakeDef` | Configuración de un shake (magnitud, duración, curva, frecuencia) |
| `FxPreset` | Un efecto compuesto reutilizable ("golpe débil", "explosión") |

---

## 3. El bucle central (core loop)

```
┌─ objTime — Begin Step (el PRIMERO que se ejecuta) ────────┐
│ 1. global.hit_stop--   (si > 0, el mundo está congelado)  │
│ 2. global.time_scale se aplica a todo lo que se mueve     │
└───────────────────────────────────────────────────────────┘
┌─ Begin Step de entidades ─────────────────────────────────┐
│ 3. if (global.hit_stop > 0) exit;   ← congelación total   │
└───────────────────────────────────────────────────────────┘
┌─ objTweenManager — Step ──────────────────────────────────┐
│ 4. Actualizar todos los tweens activos, aplicar a su dueño│
└───────────────────────────────────────────────────────────┘
┌─ objFx — Step ────────────────────────────────────────────┐
│ 5. Actualizar partículas, flashes, textos flotantes       │
└───────────────────────────────────────────────────────────┘
┌─ End Step ────────────────────────────────────────────────┐
│ 6. objCamera: calcular offset de shake y aplicar          │
└───────────────────────────────────────────────────────────┘
┌─ Draw GUI ────────────────────────────────────────────────┐
│ 7. Flashes de pantalla, viñeta, texto flotante en GUI     │
└───────────────────────────────────────────────────────────┘
```

> **Por qué `objTime` va en Begin Step:** el *hit stop* debe decidirse antes
> de que cualquier objeto haya movido un píxel. Si lo haces en el Step normal,
> el orden de instancias decide quién se congela y quién no, y obtienes
> comportamientos irreproducibles.

---

## 4. Sistemas clave

### 4.1 Screen shake

Tres niveles de calidad, de peor a mejor:

```gml
// ❌ Nivel 1: ruido puro. Funciona, pero "vibra" como un móvil.
x_offset = irandom_range(-mag, mag);

// ⚠️ Nivel 2: ruido con decaimiento lineal. Mejor, pero todavía es "ruido".
mag -= mag / duration;

// ✅ Nivel 3: ruido Perlin/o seno aleatorio + decaimiento exponencial
//    + trauma al cuadrado. Es el estándar de la industria (Squirrel Eiserloh).
var _amount = trauma * trauma;          // cuadrático: los golpes pequeños
                                        // apenas se notan y los grandes mucho
x_offset = max_offset * _amount * (noise(t) - 0.5) * 2;
trauma   -= decay_rate;
```

La clave está en `trauma²`: hace que el shake sea **perceptiblemente
proporcional**. Un golpe flojo da un temblor casi imperceptible; una explosión
da un temblor violento, sin cambiar ninguna constante.

### 4.2 Hit stop / freeze frames

Congelar el juego 2‑8 frames en el momento del impacto. Es la técnica con
mayor impacto por línea de código de todo este documento.

| Duración | Efecto percibido |
|---|---|
| 0 frames | Golpe "de plástico" |
| 2‑3 frames | Golpe con peso |
| 5‑8 frames | Golpe letal / remate |
| > 15 frames | Molesto, rompe el ritmo |

**Regla de oro:** nunca congeles más de 8 frames salvo en un remate final.

Implementación: es tentador usar un `exit` global, pero eso congela también la
UI y los efectos. Mejor: congela **solo las entidades de gameplay**, no el
sistema de efectos ni la cámara.

### 4.3 Squash & stretch

El personaje se deforma conservando volumen: si se aplasta en Y, se ensancha
en X. Es la técnica de animación más antigua que existe (Disney, 1930) y
sigue funcionando.

| Momento | Deformación |
|---|---|
| Antes de saltar | Squash vertical (se "carga") |
| Al despegar | Stretch vertical |
| En el aire | Forma neutra |
| Al aterrizar | Squash horizontal (impacto) + polvo |
| Al recibir daño | Squash + flash + knockback |

**Requisito:** el origen del sprite debe estar en la **base** (Bottom Centre),
no en el centro. Si no, al aplastarse el personaje parece levitar.

### 4.4 Easing / tweening

Un *tween* interpola una propiedad entre dos valores con una curva. Las cuatro
curvas que necesitas el 95 % de las veces:

| Curva | Sensación | Uso |
|---|---|---|
| `linear` | Robótica | Barras de progreso |
| `ease_out_quad` | Rápida al principio, suave al final | Movimiento de UI |
| `ease_out_back` | Pasa un poco y vuelve ("pop") | Botones, menús |
| `ease_out_elastic` | Rebote elástico | Recogida de objetos, daño |

**Error clásico:** usar solo `lerp(a, b, 0.1)`. Es un *ease out* exponencial
disfrazado y va bien para seguir al jugador, pero no sirve para animaciones
con duración definida porque nunca llega exactamente al destino.

### 4.5 Knockback

Empujar al enemigo (y al jugador) en la dirección del golpe. Tres parámetros:

- `magnitud` — cuánto empuja (3‑8 px típico)
- `decaimiento` — qué rápido se frena (0.15‑0.30)
- `hitstun` — cuánto tiempo pierde el control el enemigo

El *hitstun* es más importante que la magnitud: sin él, el enemigo sigue
atacando mientras vuela hacia atrás y el knockback no se percibe como
"castigo".

### 4.6 Partículas

Dos sistemas, elige según el caso:

| Sistema | Cuándo | Ventaja |
|---|---|---|
| **Partículas nativas** (`part_system_*`) | Humo, fuego, chispas masivas (miles) | Van por GPU, casi gratis |
| **Partículas propias con structs** | Pocas partículas con lógica (sangre que mancha, trozos de enemigo) | Control total |

### 4.7 Feedback audiovisual en capas

Un mismo evento debe tener respuesta en **varios canales**:

```
Impacto de espada
├── Visual: chispas + flash blanco en el sprite + squash del enemigo
├── Espacial: knockback de 4 px + hitstun de 12 frames
├── Global: screen shake trauma 0.25 + hit stop 4 frames
├── Auditivo: golpe seco, pitch aleatorio ±10 %
└── Numérico: "-12" flotante que sube y se desvanece
```

La regla de los **tres canales mínimos** (visual + espacial + auditivo) es
la que evita que el juego se sienta "sordo".

### 4.8 Anticipación y recuperación

Tomado de la animación clásica:

- **Anticipación**: antes de la acción, un movimiento contrario pequeño.
  El jugador se agacha antes de saltar; el jefe se echa atrás antes de embestir.
- **Acción**: el movimiento rápido en sí.
- **Recuperación**: vuelta a la pose neutra, más lenta que la acción.

En un juego, la anticipación es lo que hace que los ataques sean **esquivables
y justos**. Sin anticipación, el jugador solo puede reaccionar por reflejos.

---

## 5. Código base

### 5.0 Sistema de tiempo: hit stop y time scale

```gml
// ---------------------------------------------------------------------------
// objTime — Create (poner en la room, depth muy negativo para ir primero)
// ---------------------------------------------------------------------------
global.hit_stop   = 0;      // frames de congelación restantes
global.time_scale = 1.0;    // 1.0 = normal · 0.2 = tiempo bala · 2.0 = rápido
global.game_freeze = false; // congelación total (pausa, muerte, transición)
```

```gml
// ---------------------------------------------------------------------------
// objTime — Begin Step
// ---------------------------------------------------------------------------
if (global.hit_stop > 0) global.hit_stop--;

// El time_scale vuelve a 1 poco a poco (para salidas suaves del tiempo bala)
global.time_scale = lerp(global.time_scale, 1.0, 0.05);
if (abs(global.time_scale - 1.0) < 0.01) global.time_scale = 1.0;
```

```gml
// ---------------------------------------------------------------------------
// scr_time — API pública
// ---------------------------------------------------------------------------

/// @func hit_stop(_frames)
/// @desc Congela el gameplay durante N frames. 3-6 frames es el rango útil.
function hit_stop(_frames)
{
    global.hit_stop = max(global.hit_stop, _frames);
}

/// @func time_slow(_escala, _duracion_frames)
/// @desc Ralentiza el tiempo (tiempo bala). _escala típica: 0.2 - 0.4.
function time_slow(_escala, _duracion_frames)
{
    global.time_scale = _escala;
    // El retorno a 1.0 es automático por el lerp de objTime
}

/// @func time_is_frozen()
/// @desc true si el gameplay debe estar congelado este frame.
function time_is_frozen()
{
    return (global.hit_stop > 0) || global.game_freeze;
}

/// @func time_delta()
/// @desc Multiplicador que cualquier movimiento debe aplicar.
function time_delta()
{
    return time_is_frozen() ? 0 : global.time_scale;
}
```

Uso en las entidades:

```gml
// objPlayer / objEnemy — Step
var _dt = time_delta();
if (_dt == 0) exit;                 // congelado: ni te mueves ni animas

vel_y += GRAVITY * _dt;
x += vel_x * _dt;
y += vel_y * _dt;
```

> **Truco:** aplica `_dt` al movimiento pero **no** al shake ni a las
> partículas. Que el mundo se congele y las chispas sigan volando es
> exactamente lo que hace que el freeze se perciba como un impacto.

### 5.1 Cámara con shake por trauma

```gml
// ---------------------------------------------------------------------------
// objCamera — Create
// ---------------------------------------------------------------------------
cam = view_camera[0];

// Seguimiento
cam_x = x;
cam_y = y;
cam_follow_smooth = 0.12;

// Zoom
cam_zoom        = 1.0;
cam_zoom_target = 1.0;
cam_zoom_smooth = 0.10;

// --- Shake por trauma ---
trauma       = 0;      // 0..1
trauma_decay = 0.028;  // trauma que se pierde por frame
shake_max_px = 14;     // desplazamiento máximo en píxeles
shake_max_rot = 0.6;   // rotación máxima en grados (sutil: menos de 1°)
shake_time   = 0;      // reloj interno para el ruido

// Offset resultante
shake_ox = 0;
shake_oy = 0;
shake_rot = 0;

/// @func camera_add_trauma(_cantidad)
/// @desc Añade trauma (0..1). Se acumula, con tope en 1.
function camera_add_trauma(_cantidad)
{
    trauma = clamp(trauma + _cantidad, 0, 1);
}

/// @func camera_shake(_cantidad)
/// @desc Alias legible: golpe débil 0.15, normal 0.3, explosión 0.6+.
function camera_shake(_cantidad)
{
    camera_add_trauma(_cantidad);
}

/// @func camera_punch(_direccion, _fuerza)
/// @desc Desplazamiento direccional: la cámara se va hacia el golpe y vuelve.
function camera_punch(_direccion, _fuerza)
{
    punch_dir  = _direccion;
    punch_mag  = _fuerza;
    punch_time = 1.0;
}
punch_dir  = 0;
punch_mag  = 0;
punch_time = 0;
```

```gml
// ---------------------------------------------------------------------------
// objCamera — End Step
// ---------------------------------------------------------------------------
var _vw_base = camera_get_view_width(cam);
var _vh_base = camera_get_view_height(cam);

// --- 1. Zoom (cambia el tamaño de la view) ----------------------------------
cam_zoom = lerp(cam_zoom, cam_zoom_target, cam_zoom_smooth);
var _vw = _vw_base / cam_zoom;
var _vh = _vh_base / cam_zoom;
camera_set_view_size(cam, round(_vw), round(_vh));

// --- 2. Seguimiento del objetivo -------------------------------------------
if (instance_exists(objPlayer))
{
    cam_x = lerp(cam_x, objPlayer.x, cam_follow_smooth);
    cam_y = lerp(cam_y, objPlayer.y, cam_follow_smooth);
}

// --- 3. Shake ---------------------------------------------------------------
shake_ox  = 0;
shake_oy  = 0;
shake_rot = 0;

if (trauma > 0)
{
    shake_time += 1;

    // Cuadrático: proporción percibida correcta
    var _amount = trauma * trauma;

    // Ruido pseudo-aleatorio suave (suma de senos con frecuencias distintas)
    var _n1 = sin(shake_time * 1.7) * 0.5 + sin(shake_time * 3.3) * 0.3
                                          + sin(shake_time * 7.1) * 0.2;
    var _n2 = cos(shake_time * 1.9) * 0.5 + cos(shake_time * 4.1) * 0.3
                                          + cos(shake_time * 8.3) * 0.2;
    var _n3 = sin(shake_time * 2.3) * 0.6 + sin(shake_time * 5.7) * 0.4;

    shake_ox  = _n1 * shake_max_px  * _amount;
    shake_oy  = _n2 * shake_max_px  * _amount;
    shake_rot = _n3 * shake_max_rot * _amount;

    trauma = max(0, trauma - trauma_decay);
}

// --- 4. Punch direccional ---------------------------------------------------
if (punch_time > 0)
{
    var _p = punch_time * punch_time;           // decaimiento cuadrático
    var _px = lengthdir_x(punch_mag * _p, punch_dir);
    var _py = lengthdir_y(punch_mag * _p, punch_dir);
    shake_ox += _px;
    shake_oy += _py;
    punch_time -= 0.08;
}

// --- 5. Aplicar -------------------------------------------------------------
var _final_x = cam_x + shake_ox;
var _final_y = cam_y + shake_oy;

// Clamp a la room (antes del shake, para no salirte en los bordes)
_final_x = clamp(_final_x, _vw * 0.5, max(_vw * 0.5, room_width  - _vw * 0.5));
_final_y = clamp(_final_y, _vh * 0.5, max(_vh * 0.5, room_height - _vh * 0.5));

camera_set_view_pos(cam, round(_final_x - _vw * 0.5),
                         round(_final_y - _vh * 0.5));

if (shake_rot != 0) camera_set_view_angle(cam, shake_rot);
else                camera_set_view_angle(cam, 0);
```

### 5.2 Tween helper con structs

```gml
// ---------------------------------------------------------------------------
// scr_tween — sistema de tweens con structs
// ---------------------------------------------------------------------------

/// @func Ease()
/// @desc Funciones puras de interpolación: entrada 0..1 → salida 0..1.
///       `static` para que no se dupliquen en cada instancia del struct.
function Ease() constructor
{
    static linear = function(_t) { return _t; };

    static in_quad   = function(_t) { return _t * _t; };
    static out_quad  = function(_t) { return 1 - (1 - _t) * (1 - _t); };
    static inout_quad = function(_t)
    {
        return (_t < 0.5) ? (2 * _t * _t)
                          : (1 - power(-2 * _t + 2, 2) * 0.5);
    };

    static out_cubic = function(_t) { return 1 - power(1 - _t, 3); };
    static in_cubic  = function(_t) { return _t * _t * _t; };

    static out_back = function(_t)
    {
        var _c1 = 1.70158;
        var _c3 = _c1 + 1;
        return 1 + (_c3 * power(_t - 1, 3)) + (_c1 * power(_t - 1, 2));
    };

    static out_elastic = function(_t)
    {
        if (_t == 0) return 0;
        if (_t == 1) return 1;
        var _c4 = (2 * pi) / 3;
        return power(2, -10 * _t) * sin((_t * 10 - 0.75) * _c4) + 1;
    };

    static out_bounce = function(_t)
    {
        var _n1 = 7.5625;
        var _d1 = 2.75;
        if (_t < 1 / _d1)       return _n1 * _t * _t;
        if (_t < 2 / _d1)       { _t -= 1.5 / _d1; return _n1*_t*_t + 0.75; }
        if (_t < 2.5 / _d1)     { _t -= 2.25 / _d1; return _n1*_t*_t + 0.9375; }
        _t -= 2.625 / _d1;
        return _n1 * _t * _t + 0.984375;
    };

    static out_expo = function(_t)
    {
        return (_t == 1) ? 1 : (1 - power(2, -10 * _t));
    };
}

global.Ease = new Ease();
```

```gml
/// @func Tween(_target, _propiedad, _desde, _hasta, _duracion, _ease, _on_end)
/// @desc Una animación de una propiedad de una instancia o struct.
/// @param {Id.Instance|Struct} _target  Dueño de la propiedad
/// @param {String}             _propiedad Nombre de la variable a animar
function Tween(
    _target, _propiedad, _desde, _hasta, _duracion, _ease, _on_end
) constructor
{
    target    = _target;
    propiedad = _propiedad;
    desde     = _desde;
    hasta     = _hasta;
    duracion  = max(1, _duracion);
    ease      = (_ease == undefined) ? global.Ease.out_quad : _ease;
    on_end    = (_on_end == undefined) ? undefined : _on_end;

    tiempo    = 0;
    finished  = false;
    // El tween se autodestruye con su dueño: si el target muere, paramos.
    kill_on_target_dead = true;

    /// @desc Avanza un frame y escribe el valor en el target.
    update = function()
    {
        if (finished) return;

        // Dueño muerto → cancelar sin error
        if (kill_on_target_dead &&
            is_numeric(target) && !instance_exists(target))
        {
            finished = true;
            return;
        }

        tiempo++;
        var _t = clamp(tiempo / duracion, 0, 1);
        var _v = lerp(desde, hasta, ease(_t));

        // Escritura dinámica: funciona igual en instancias y en structs
        if (is_struct(target))
        {
            target[$ propiedad] = _v;
        }
        else if (instance_exists(target))
        {
            variable_instance_set(target, propiedad, _v);
        }

        if (_t >= 1)
        {
            finished = true;
            if (on_end != undefined) on_end();
        }
    };

    /// @desc Cancela el tween sin ejecutar on_end.
    cancel = function()
    {
        finished = true;
    };
}
```

```gml
// ---------------------------------------------------------------------------
// objTweenManager — Create (un solo objeto en la room)
// ---------------------------------------------------------------------------
tweens = [];

/// @func tween_to(_target, _prop, _hasta, _duracion, _ease, _on_end)
/// @desc Crea un tween desde el valor ACTUAL de la propiedad hasta _hasta.
function tween_to(_target, _prop, _hasta, _duracion, _ease, _on_end)
{
    var _desde = 0;

    if (is_struct(_target))
    {
        if (variable_struct_exists(_target, _prop)) _desde = _target[$ _prop];
    }
    else if (instance_exists(_target))
    {
        _desde = variable_instance_get(_target, _prop);
    }

    var _t = new Tween(_target, _prop, _desde, _hasta, _duracion, _ease, _on_end);
    array_push(objTweenManager.tweens, _t);
    return _t;
}

/// @func tween_cancel_all(_target)
function tween_cancel_all(_target)
{
    with (objTweenManager)
    {
        var _len = array_length(tweens);
        for (var _i = 0; _i < _len; _i++)
        {
            if (tweens[_i].target == _target) tweens[_i].cancel();
        }
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objTweenManager — Step
// ---------------------------------------------------------------------------
var _len = array_length(tweens);

for (var _i = _len - 1; _i >= 0; _i--)
{
    var _t = tweens[_i];
    _t.update();

    if (_t.finished)
    {
        array_delete(tweens, _i, 1);
    }
}
```

```gml
// ---------------------------------------------------------------------------
// objTweenManager — Room End / Destroy
// ---------------------------------------------------------------------------
array_resize(tweens, 0);
```

**Uso típico:**

```gml
// Menú que entra con rebote
tween_to(self, "menu_y", 200, 40, global.Ease.out_back);

// Barra de vida que baja suave
tween_to(self, "hp_display", hp, 20, global.Ease.out_cubic);

// Botón que hace "pop" al pulsarse
tween_to(self, "button_scale", 0.9, 8, global.Ease.out_quad, function()
{
    tween_to(self, "button_scale", 1.0, 12, global.Ease.out_elastic);
});

// Fade a negro y cambio de room
tween_to(objTransition, "fade_alpha", 1, 30, global.Ease.out_quad, function()
{
    room_goto(rm_next);
});
```

### 5.3 Squash & stretch reusable

```gml
// ---------------------------------------------------------------------------
// scr_squash
// ---------------------------------------------------------------------------

/// @func squash_stretch(_obj, _x, _y, _duracion)
/// @desc Aplica una deformación y la relaja con un tween hasta (1, 1).
///       _x > 1 = más ancho · _y > 1 = más alto
function squash_stretch(_obj, _x, _y, _duracion)
{
    _obj.squash_x = _x;
    _obj.squash_y = _y;

    tween_to(_obj, "squash_x", 1, _duracion, global.Ease.out_elastic);
    tween_to(_obj, "squash_y", 1, _duracion, global.Ease.out_elastic);
}

/// @func squash_preset(_obj, _tipo)
/// @desc Presets listos para los momentos más comunes.
function squash_preset(_obj, _tipo)
{
    switch (_tipo)
    {
        case "jump":      squash_stretch(_obj, 0.75, 1.30, 22); break;
        case "land":      squash_stretch(_obj, 1.35, 0.70, 20); break;
        case "hit":       squash_stretch(_obj, 1.25, 0.80, 14); break;
        case "death":     squash_stretch(_obj, 1.60, 0.45, 30); break;
        case "pickup":    squash_stretch(_obj, 0.80, 1.25, 18); break;
        case "anticipate":squash_stretch(_obj, 1.20, 0.85, 10); break;
    }
}
```

```gml
// ---------------------------------------------------------------------------
// Draw de cualquier entidad con squash
// ---------------------------------------------------------------------------
// Requiere que el sprite tenga el origen en Bottom Centre.
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

### 5.4 Knockback

```gml
// ---------------------------------------------------------------------------
// scr_knockback
// ---------------------------------------------------------------------------

/// @func apply_knockback(_obj, _dir, _fuerza, _hitstun)
/// @desc Empuja a _obj en _dir y le quita el control _hitstun frames.
function apply_knockback(_obj, _dir, _fuerza, _hitstun)
{
    if (!instance_exists(_obj)) return;

    with (_obj)
    {
        vel_x += lengthdir_x(_fuerza, _dir);
        vel_y += lengthdir_y(_fuerza, _dir);

        // El hitstun es lo que hace que el knockback SE NOTE
        hitstun = max(hitstun, _hitstun);

        // Frenado por defecto para que el empuje se disipe solo
        knockback_decay = 0.18;
    }
}
```

```gml
// En el Step de la entidad, ANTES de mover:
if (hitstun > 0)
{
    hitstun--;
    // Durante el hitstun no hay control de input: solo inercia
    vel_x = lerp(vel_x, 0, knockback_decay);
    vel_y = lerp(vel_y, 0, knockback_decay);
    // ...y NO procesar input
}
```

### 5.5 Partículas nativas

```gml
// ---------------------------------------------------------------------------
// objFx — Create (persistente, sin sprite)
// ---------------------------------------------------------------------------
ps = part_system_create_layer("Effects", true);
part_system_depth(ps, -100);

// --- Tipo: chispas de impacto ---
pt_spark = part_type_create();
part_type_shape(pt_spark, pt_shape_spark);
part_type_size(pt_spark, 0.15, 0.35, -0.004, 0);
part_type_scale(pt_spark, 1, 1);
part_type_speed(pt_spark, 2, 6, -0.15, 0);
part_type_direction(pt_spark, 0, 359, 0, 0);
part_type_gravity(pt_spark, 0.12, 270);
part_type_orientation(pt_spark, 0, 359, 0, 0, true);
part_type_colour1(pt_spark, c_yellow);
part_type_alpha2(pt_spark, 1, 0);
part_type_life(pt_spark, 12, 26);

// --- Tipo: humo ---
pt_smoke = part_type_create();
part_type_shape(pt_smoke, pt_shape_smoke);
part_type_size(pt_smoke, 0.4, 1.1, 0.008, 0);
part_type_speed(pt_smoke, 0.3, 1.0, -0.02, 0);
part_type_direction(pt_smoke, 60, 120, 0, 0);
part_type_gravity(pt_smoke, -0.02, 90);
part_type_colour1(pt_smoke, c_gray);
part_type_alpha2(pt_smoke, 0.5, 0);
part_type_life(pt_smoke, 40, 80);

// --- Tipo: sangre / trozos ---
pt_blood = part_type_create();
part_type_shape(pt_blood, pt_shape_pixel);
part_type_size(pt_blood, 0.10, 0.25, 0, 0);
part_type_speed(pt_blood, 3, 8, -0.25, 0);
part_type_direction(pt_blood, 0, 359, 0, 0);
part_type_gravity(pt_blood, 0.35, 270);
part_type_colour1(pt_blood, c_red);
part_type_alpha1(pt_blood, 1);
part_type_life(pt_blood, 20, 45);

// --- Tipo: polvo al aterrizar ---
pt_dust = part_type_create();
part_type_shape(pt_dust, pt_shape_cloud);
part_type_size(pt_dust, 0.25, 0.6, 0.01, 0);
part_type_speed(pt_dust, 0.5, 1.8, -0.06, 0);
part_type_direction(pt_dust, 0, 180, 0, 0);   // hacia los lados
part_type_gravity(pt_dust, 0.02, 270);
part_type_colour1(pt_dust, c_ltgray);
part_type_alpha2(pt_dust, 0.6, 0);
part_type_life(pt_dust, 18, 34);
```

```gml
// ---------------------------------------------------------------------------
// objFx — Destroy (¡obligatorio! los part_type no se liberan solos)
// ---------------------------------------------------------------------------
part_type_destroy(pt_spark);
part_type_destroy(pt_smoke);
part_type_destroy(pt_blood);
part_type_destroy(pt_dust);
part_system_destroy(ps);
```

```gml
// ---------------------------------------------------------------------------
// scr_fx — API de efectos
// ---------------------------------------------------------------------------

/// @func fx_impact(_x, _y, _dir, _intensidad)
/// @desc Chispas en abanico en la dirección contraria al golpe.
function fx_impact(_x, _y, _dir, _intensidad)
{
    var _count = 6 + round(_intensidad * 10);
    part_type_direction(objFx.pt_spark,
                        _dir - 35, _dir + 35, 0, 0);
    part_particles_create(objFx.ps, _x, _y, objFx.pt_spark, _count);
}

/// @func fx_dust_land(_x, _y)
function fx_dust_land(_x, _y)
{
    part_particles_create(objFx.ps, _x, _y, objFx.pt_dust, 10);
}

/// @func fx_explosion(_x, _y, _escala)
function fx_explosion(_x, _y, _escala)
{
    part_particles_create(objFx.ps, _x, _y, objFx.pt_spark, 30 * _escala);
    part_particles_create(objFx.ps, _x, _y, objFx.pt_smoke, 12 * _escala);

    camera_shake(0.35 * _escala);
    hit_stop(3);
}
```

### 5.6 Flash de impacto y texto flotante

```gml
// ---------------------------------------------------------------------------
// scr_fx_overlay
// ---------------------------------------------------------------------------

/// @func fx_flash(_color, _alfa, _frames)
/// @desc Full-screen flash. Úsalo con alfa baja (0.1-0.3) o marea al jugador.
function fx_flash(_color, _alfa, _frames)
{
    with (objFx)
    {
        flash_color = _color;
        flash_alpha = _alfa;
        flash_max   = _frames;
        flash_timer = _frames;
    }
}
```

```gml
// objFx — Draw GUI (encima de todo)
if (flash_timer > 0)
{
    var _a = (flash_timer / flash_max) * flash_alpha;
    draw_set_alpha(_a);
    draw_set_color(flash_color);
    draw_rectangle(0, 0, display_get_gui_width(), display_get_gui_height(), false);
    draw_set_alpha(1);
    flash_timer--;
}
```

```gml
/// @func fx_floating_text(_x, _y, _texto, _color)
/// @desc Número de daño / "+100" que sube y se desvanece.
function fx_floating_text(_x, _y, _texto, _color)
{
    with (instance_create_layer(_x, _y, "Effects", objFloatingText))
    {
        texto       = _texto;
        text_color  = (_color == undefined) ? c_white : _color;
        vy          = -1.2;
        life        = 50;
        life_max    = 50;

        // Pop de entrada
        pop_scale = 0.2;
        tween_to(self, "pop_scale", 1.0, 12, global.Ease.out_back);
    }
}
```

```gml
// objFloatingText — Create
texto      = "";
text_color = c_white;
vy         = -1.2;
life       = 50;
life_max   = 50;
pop_scale  = 1;

// objFloatingText — Step
y += vy;
vy = lerp(vy, 0, 0.12);
life--;
if (life <= 0) instance_destroy();

// objFloatingText — Draw
var _t = life / life_max;
draw_set_alpha((_t > 0.7) ? 1 : (_t / 0.7));
draw_set_color(c_black);
draw_set_halign(fa_center);
draw_text_transformed(x + 1, y + 1, texto, pop_scale, pop_scale, 0);   // sombra
draw_set_color(text_color);
draw_text_transformed(x, y, texto, pop_scale, pop_scale, 0);
draw_set_alpha(1);
draw_set_halign(fa_left);
```

### 5.6 bis · Dibujar el `hit_flash` (las tres vías)

`hit_complete()` (§5.7) fija `_v.hit_flash = 8` con el comentario «(shader o `image_blend`)»,
pero ese flash nunca se dibuja en ninguna parte de esta receta ni de las que lo copian — el
efecto de daño más universal del género se queda a medias. Aquí están las tres formas de
pintarlo, de más simple a más precisa. Las tres asumen que el objeto ya declara
`hit_flash = 0;` en su Create (como hacen `02 · Top-Down` y `03 · Shoot 'em up`); añade también
`hit_flash_max = 8;` junto a esa línea — el mismo valor que usa `hit_complete()`.

**Vía 1 — `image_blend` no sirve por sí solo, pero `gpu_set_fog` sí (silueta blanca sólida,
sin shaders).** `image_blend` **multiplica** el color del sprite: pintar con `c_white` no
cambia nada (multiplicar por blanco es la identidad), así que un flash de daño necesita algo
más. `gpu_set_fog` fuerza el color de niebla sobre todo lo dibujado mientras está activo,
ignorando la textura — con `start = end` (o un rango que cubra 0), el sprite sale teñido al
100 % del color de niebla, alfa intacto. Es el truco real que usa código descargado de la
biblioteca para forzar un color sólido (`11 - Código descargado/librerias/utilidades/HelpfulGMLScripts/draw_sprite_solid_color.gml`
y `.../_Maybe Not that great/Hooks/use_flash.gml`, ambos con el mismo patrón):

```gml
// Draw — silueta blanca sólida mientras hit_flash > 0
if (hit_flash > 0)
{
    gpu_set_fog(true, c_white, -16000, 16000);
    draw_self();
    gpu_set_fog(false, 0, 0, 0);
}
else
{
    draw_self();
}
```

**Vía 2 — shader con uniform `u_flash` (control preciso, interpola en vez de todo-o-nada).**
Sigue la misma anatomía que los shaders de `08 · 06`: vertex shader de paso estándar, fragment
shader con un `mix()` entre el color original y blanco puro. A diferencia de la niebla, aquí
puedes animar la intensidad con cualquier curva, no solo mostrar/ocultar:

```glsl
// sh_hit_flash.vsh — el vertex shader de paso estándar de la biblioteca (ver 08 · 06 §Anatomía)
attribute vec3 in_Position;
attribute vec4 in_Colour;
attribute vec2 in_TextureCoord;

varying vec2 v_vTexcoord;
varying vec4 v_vColour;

void main()
{
    vec4 object_space_pos = vec4(in_Position.x, in_Position.y, in_Position.z, 1.0);
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;
    v_vColour   = in_Colour;
    v_vTexcoord = in_TextureCoord;
}
```

```glsl
// sh_hit_flash.fsh
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

// 0 = color normal, 1 = blanco sólido
uniform float u_flash;

void main()
{
    vec4 color_base = texture2D(gm_BaseTexture, v_vTexcoord) * v_vColour;
    vec3 resultado  = mix(color_base.rgb, vec3(1.0), u_flash);
    gl_FragColor = vec4(resultado, color_base.a);   // el alfa nunca se toca: conserva la silueta
}
```

```gml
// Create
u_flash = shader_get_uniform(sh_hit_flash, "u_flash");

// Draw
if (hit_flash > 0)
{
    shader_set(sh_hit_flash);
    shader_set_uniform_f(u_flash, hit_flash / hit_flash_max);
    draw_self();
    shader_reset();
}
else
{
    draw_self();
}
```

**Vía 3 — sprite blanco aditivo encima (sin shaders, más barato que la niebla, pero solo
refuerza brillo).** Dibuja el sprite normal y, encima, una segunda pasada con `bm_add` teñida
de blanco: suma luz en vez de sustituir el color, así que en sprites muy oscuros hace falta más
alfa para notarse, pero evita cambiar el estado de niebla:

```gml
// Draw
draw_self();
if (hit_flash > 0)
{
    gpu_set_blendmode(bm_add);
    draw_sprite_ext(sprite_index, image_index, x, y,
                    image_xscale, image_yscale, image_angle,
                    c_white, hit_flash / hit_flash_max);
    gpu_set_blendmode(bm_normal);
}
```

> 💡 **Cuál elegir**: la niebla (vía 1) es la más barata y la más honesta con el pixel art — una
> silueta blanca sólida instantánea, sin dependencias de shader. El shader (vía 2) es la única
> que interpola de verdad y la que escala mejor si ya usas shaders en el resto del juego. El
> aditivo (vía 3) es el más simple de las tres pero el más débil sobre sprites oscuros.

### 5.7 El "golpe completo": una función que lo junta todo

```gml
// ---------------------------------------------------------------------------
// scr_hit_complete
// ---------------------------------------------------------------------------

/// @func hit_complete(_atacante, _victima, _daño, _direccion)
/// @desc Aplica un golpe CON TODAS LAS CAPAS DE FEEDBACK.
///       Es la función que debes llamar cada vez que algo recibe daño.
/// @param {Id.Instance} _victima    Quién recibe
/// @param {Real}        _daño       Cuánto
/// @param {Real}        _direccion  Ángulo del golpe (hacia dónde empuja)
function hit_complete(_victima, _daño, _direccion)
{
    if (!instance_exists(_victima)) return;

    var _v = _victima;

    // --- 1. Daño --------------------------------------------------------------
    _v.hp -= _daño;

    // --- 2. Flash en el sprite (shader o image_blend) -------------------------
    _v.hit_flash = 8;

    // --- 3. Knockback + hitstun -----------------------------------------------
    apply_knockback(_v, _direccion, 4.5, 12);

    // --- 4. Squash -------------------------------------------------------------
    squash_preset(_v, "hit");

    // --- 5. Partículas ---------------------------------------------------------
    fx_impact(_v.x, _v.y, _direccion + 180, 1.0);

    // --- 6. Hit stop (proporcional al daño) ------------------------------------
    hit_stop(clamp(round(_daño * 0.25), 1, 8));

    // --- 7. Screen shake (proporcional al daño) ---------------------------------
    camera_shake(clamp(_daño * 0.012, 0.08, 0.45));

    // --- 8. Audio con pitch aleatorio -------------------------------------------
    var _snd = audio_play_sound(sndHit, 10, false);
    audio_sound_pitch(_snd, random_range(0.90, 1.10));

    // --- 9. Número flotante ------------------------------------------------------
    fx_floating_text(_v.x, _v.y - 16, string(_daño), c_yellow);

    // --- 10. Muerte ---------------------------------------------------------------
    if (_v.hp <= 0)
    {
        _v.hp = 0;
        fx_explosion(_v.x, _v.y, 1.0);
        squash_preset(_v, "death");
        instance_destroy(_v);
    }
}
```

### 5.8 Anticipación en un ataque enemigo

```gml
// ---------------------------------------------------------------------------
// Ataque del jefe con ANTICIPACIÓN (lo que lo hace justo y esquivable)
// ---------------------------------------------------------------------------
enum BossAttackState { idle, anticipate, strike, recover }

// Create
attack_state = BossAttackState.idle;
attack_timer = 0;

// --- Constantes de timing (en frames) ---
ANTICIPATE_FRAMES = 30;   // medio segundo de aviso: esquivable
STRIKE_FRAMES     = 8;    // el golpe en sí: rápido
RECOVER_FRAMES    = 40;   // vulnerable: la ventana de castigo del jugador

// Step
switch (attack_state)
{
    case BossAttackState.idle:
        attack_timer++;
        if (attack_timer > 90)
        {
            attack_state = BossAttackState.anticipate;
            attack_timer = 0;
            squash_preset(self, "anticipate");
        }
        break;

    case BossAttackState.anticipate:
        attack_timer++;
        // El telegraph: el sprite se tiñe de rojo y tiembla
        image_blend = merge_color(c_white, c_red, attack_timer / ANTICIPATE_FRAMES);
        x = x_base + sin(attack_timer * 1.2) * 2;

        if (attack_timer >= ANTICIPATE_FRAMES)
        {
            attack_state = BossAttackState.strike;
            attack_timer = 0;
            image_blend = c_white;
        }
        break;

    case BossAttackState.strike:
        attack_timer++;
        if (attack_timer == 1)     // el golpe ocurre en el frame 1
        {
            // Embiste hacia el jugador
            var _dir = point_direction(x, y, objPlayer.x, objPlayer.y);
            vel_x = lengthdir_x(12, _dir);
            vel_y = lengthdir_y(12, _dir);
        }
        if (attack_timer >= STRIKE_FRAMES)
        {
            attack_state = BossAttackState.recover;
            attack_timer = 0;
        }
        break;

    case BossAttackState.recover:
        attack_timer++;
        vel_x = lerp(vel_x, 0, 0.15);
        vel_y = lerp(vel_y, 0, 0.15);
        // Aquí el jugador puede castigar: el jefe está indefenso
        if (attack_timer >= RECOVER_FRAMES)
        {
            attack_state = BossAttackState.idle;
            attack_timer = 0;
        }
        break;
}
```

---

## 6. Gestión del estado del jugador

El *game feel* también tiene estado persistente: preferencias del jugador.

```gml
// ---------------------------------------------------------------------------
// scr_feel_settings
// ---------------------------------------------------------------------------

/// @func FeelSettings()
/// @desc Preferencias de accesibilidad y sensación. Guárdalas en disco.
///       El 20 % de los jugadores desactiva el screen shake. Respétalo.
function FeelSettings() constructor
{
    shake_enabled    = true;
    shake_intensity  = 1.0;    // multiplicador 0..1
    hitstop_enabled  = true;
    flash_enabled    = true;   // CRÍTICO: reducirlo para fotosensibilidad
    particles_level  = 1.0;    // multiplicador 0..1
    camera_smoothing = true;

    /// @desc Aplica la configuración al sistema de cámara y efectos.
    apply = function()
    {
        with (objCamera)
        {
            shake_max_px = (other.shake_enabled ? 14 : 0) * other.shake_intensity;
            shake_max_rot = (other.shake_enabled ? 0.6 : 0) * other.shake_intensity;
            cam_follow_smooth = other.camera_smoothing ? 0.12 : 1.0;
        }
    };

    serialize = function()
    {
        return {
            shake_enabled:    shake_enabled,
            shake_intensity:  shake_intensity,
            hitstop_enabled:  hitstop_enabled,
            flash_enabled:    flash_enabled,
            particles_level:  particles_level,
            camera_smoothing: camera_smoothing
        };
    };

    save = function()
    {
        // ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
        // es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
        // 14 - Persistencia y archivos.md §1.
        var _f = file_text_open_write(game_save_id + "settings.json");
        file_text_write_string(_f, json_stringify(serialize()));
        file_text_close(_f);
    };

    load = function()
    {
        var _path = game_save_id + "settings.json";
        if (!file_exists(_path)) return;

        var _f = file_text_open_read(_path);
        var _d = json_parse(file_text_read_string(_f));
        file_text_close(_f);

        shake_enabled    = _d[$ "shake_enabled"];
        shake_intensity  = _d[$ "shake_intensity"];
        hitstop_enabled  = _d[$ "hitstop_enabled"];
        flash_enabled    = _d[$ "flash_enabled"];
        particles_level  = _d[$ "particles_level"];
        camera_smoothing = _d[$ "camera_smoothing"];
    };
}
```

Y envolver las llamadas:

```gml
/// @func camera_shake(_cantidad)  — versión que respeta la configuración
function camera_shake(_cantidad)
{
    if (!global.feel.shake_enabled) return;
    camera_add_trauma(_cantidad * global.feel.shake_intensity);
}

/// @func hit_stop(_frames) — versión que respeta la configuración
function hit_stop(_frames)
{
    if (!global.feel.hitstop_enabled) return;
    global.hit_stop = max(global.hit_stop, _frames);
}
```

---

## 7. Errores clásicos y cómo evitarlos

| Error | Síntoma | Solución |
|---|---|---|
| Shake lineal en vez de cuadrático | Cualquier golpe tiembla igual | `trauma * trauma` |
| Shake con ruido puro de `irandom` | Vibra como un móvil, no como un impacto | Suma de senos con distintas frecuencias |
| Rotación de cámara exagerada | Marea al jugador en 10 segundos | Máximo 0.5°‑1° |
| Hit stop de más de 10 frames | El juego se siente roto, no contundente | 1‑8 frames, y solo en golpes importantes |
| Congelar también la UI | El HUD se congela y se percibe como un *bug* | Congela solo entidades de gameplay |
| Squash con origen centrado | El personaje flota al aplastarse | Origen del sprite en **Bottom Centre** |
| Usar `lerp` para animaciones con duración | Nunca llega al valor final; se acumula el error | Usa el sistema de `Tween` con `_t` normalizado |
| No destruir los `part_type` | Fuga de memoria: los tipos no se liberan solos | `part_type_destroy()` en el Destroy de `objFx` |
| Un `part_system` por objeto | Cientos de sistemas = rendimiento hundido | Un único sistema global en `objFx` |
| Tweens que apuntan a instancias destruidas | Error de "variable no existe" aleatorio | El `Tween.update()` comprueba `instance_exists` y se cancela |
| No limpiar tweens al cambiar de room | Tweens apuntando a IDs reciclados de otros objetos | `array_resize(tweens, 0)` en Room End |
| Feedback solo visual | El juego se siente "sordo" | Mínimo tres canales: visual + espacial + auditivo |
| Ataques sin anticipación | El jugador siente que muere por azar | 20‑40 frames de telegraph antes de cada golpe |

---

## 8. Cómo escalarlo

1. **Presets de efectos compuestos** — define `FxPreset` con nombre
   ("golpe_débil", "crítico", "explosión", "curación") y llámalos por nombre
   en vez de repetir los diez pasos.
2. **Shaders de impacto** — un shader de *white flash* es más barato y más
   vistoso que cambiar `image_blend`. Pasa un uniform `u_flash` de 0 a 1 con
   un tween.
3. **Cámara cinemática** — durante un remate: zoom a 1.4, `time_slow(0.25)`,
   shake, y vuelta. El sistema ya está preparado.
4. **Audio dinámico** — capas de música que entran y salen con la intensidad
   del combate (`audio_sound_gain` con tweens).
5. **Rastro (trail)** — guarda las últimas N posiciones en un array y dibuja
   el sprite con alfa decreciente. Es de las técnicas más rentables que existen.
6. **Partículas GPU** — para fuego o humo masivo, usa el sistema nativo con
   `part_system_create_layer` y deja que la GPU las dibuje.
7. **Juice condicional** — reduce el juice en oleadas de muchos enemigos para
   que los golpes importantes sigan destacando. El juice es **contraste**, no
   cantidad absoluta.

**La prueba definitiva:** graba 5 segundos de tu juego, quita el sonido y míralo.
Si no puedes decir cuándo un golpe ha sido importante, te falta *game feel*.

Cuatro de los puntos anteriores se quedan en una línea porque merecen su propio desarrollo.
Van a continuación, en el mismo orden en que aparecen arriba.

### 8.1 Estela de cinta (trail de espada): ya resuelta, no la dupliques

El punto 5 («Rastro (trail): guarda las últimas N posiciones en un array...») se queda en la
idea. La receta completa — el historial de **dos puntos por fotograma**, `draw_primitive_begin`
con `pr_trianglestrip`, ancho y alfa decrecientes hacia la cola, y la variante con textura vía
`draw_primitive_begin_texture` para un degradado de color en vez de un color plano — ya está
escrita, verificada y lista para copiar en
[04 · 39 §3.9.1](./39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md#391-trail-de-espada-con-draw_primitive).
Es *el* trail de espada: cópialo tal cual.

Esa misma sección distingue el trail de primitivas del *afterimage* por sprites completos (ya
resuelto en [04 · 06 §5.4](./06%20-%20Metroidvania.md#54-habilidades-en-el-jugador) y enlazado
desde [04 · 39 §3.9.4](./39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md#394-afterimage-ya-existe-no-lo-dupliques))
y del trail de partículas para proyectiles
([04 · 39 §3.9.2](./39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md#392-trail-de-proyectil-con-part_system_global_space)):
tres técnicas que compiten por el mismo nombre y resuelven necesidades distintas. Elige por lo
que necesitas leer — silueta completa, trazo continuo o estela de luz —, no por cuál
encontraste primero.

### 8.2 Permanence: sangre, casquillos y quemaduras persistentes: ya resuelta

El punto de «sangre que mancha» tampoco se desarrollaba aquí. *Permanence* — el término que usan
Nijman y Jonasson en «Juice it or lose it» para las marcas que un impacto deja mucho después de
que el impacto termine — ya tiene receta completa en
[04 · 39 §3.10](./39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md#310-decals-y-marcas-persistentes):
una surface del tamaño de la room, el patrón de recreación tras `surface_exists()` falso (las
surfaces se pierden al minimizar o cambiar de resolución), el presupuesto de VRAM (~8,3 MB en
1920×1080 con el formato por defecto), el límite de decals activos y el desvanecimiento por
antigüedad, y agujeros de bala con rotación aleatoria. No la reproduzcas aquí: es la misma
`obj_gestor_decals` la que quieres, tanto si la sangre viene de tu sistema de combate como si
viene de cualquier otro.

### 8.3 Zoom punch y retroceso de cámara

`objCamera` (§5.1) ya declara `cam_zoom` / `cam_zoom_target` / `cam_zoom_smooth` y ya tiene
`camera_punch()` para un desplazamiento direccional que se va y vuelve — pero ninguno de los
dos se llama desde ningún sitio de este documento. El *zoom punch* (un acercamiento brusco que
vuelve solo) es la pieza que falta para que esos campos dejen de ser infraestructura muerta, y
la clave de un buen *zoom punch* es que **use el mismo número que el shake**: un golpe grande
debe temblar Y acercar a la vez, no dos sistemas desincronizados con su propia noción de
«grande».

```gml
// ---------------------------------------------------------------------------
// objCamera — ampliar el Create de §5.1 con el estado del zoom punch
// ---------------------------------------------------------------------------
zoom_base       = 1.0;    // el zoom "de reposo" al que siempre vuelve
zoom_punch_t    = 0;      // 0 = en reposo, 1 = justo en el pico del punch

/// @func zoom_punch(_fuerza)
/// @desc Acerca la cámara de golpe y la deja volver sola. _fuerza es la MISMA magnitud
///       0..1 que le pasas a camera_shake(): así un golpe "grande" siempre lo es en los
///       dos sistemas a la vez, sin tener que ajustar dos números por separado.
function zoom_punch(_fuerza)
{
    zoom_punch_t = max(zoom_punch_t, clamp(_fuerza, 0, 1));
}
```

```gml
// ---------------------------------------------------------------------------
// objCamera — End Step de §5.1, bloque "1. Zoom": sustituye cam_zoom_target fijo
// por la contribución del punch, ENCIMA de cualquier zoom que ya tuvieras puesto
// (una mira, un modo foto...). No reemplaza ese bloque: se SUMA justo antes de él.
// ---------------------------------------------------------------------------
if (zoom_punch_t > 0)
{
    zoom_punch_t = max(0, zoom_punch_t - 0.045);      // decae solo, sin temporizador aparte
}
cam_zoom_target = zoom_base + zoom_punch_t * 0.35;    // 0.35 = hasta un 35% más cerca en el pico
```

Uso en `hit_complete()` (§5.7), junto al paso 7 de screen shake — la variable ya existe ahí,
solo se reutiliza en una línea más, y el retroceso de cámara al disparar reutiliza
`camera_punch()` sin necesitar una función nueva (dispara hacia atrás de la dirección del
disparo, `_direccion_disparo + 180`):

```gml
// --- 7. Screen shake + zoom punch (proporcionales al MISMO daño) ------------
var _trauma = clamp(_daño * 0.012, 0.08, 0.45);
camera_shake(_trauma);
zoom_punch(_trauma);

// --- Retroceso al disparar (en obj_arma, no en hit_complete): -----------------
// camera_punch(_direccion_disparo + 180, 3);
```

> ⚠️ **`scr_camera.gml`** (en `06 - Assets y Scripts/`) es un sistema de cámara **distinto** al
> `objCamera` de este documento — más simple, sin trauma ni zoom — y no lo tiene ni lo necesita
> para lo que resuelve (deadzone, look-ahead, límites de sala). Si tu proyecto usa
> `scr_camera.gml`, este `zoom_punch()` no se aplica tal cual: la idea (un `zoom_target` que
> sube con el golpe y decae solo) es portable, pero tendrías que añadir tú los campos de zoom a
> ese script, que hoy no los tiene.
>
> 💡 **`camera_punch()` para el disparo, `zoom_punch()` para el impacto recibido.** Son las dos
> mitades de la misma idea de cámara reactiva: la que dispara retrocede un poco, la que recibe
> el golpe se acerca un poco. Combínalas en un arma con reculada fuerte: `camera_punch()` en
> quien dispara y `camera_shake()` + `zoom_punch()` en quien recibe.

### 8.4 Vibración del mando: la quinta capa de feedback

La regla de los **tres canales mínimos** (§4.7: visual + espacial + auditivo) puede ampliarse a
cuatro con la cámara (shake + zoom punch, §8.3) y a **cinco** con el mando. El toggle/slider
obligatorio por accesibilidad y el pulso con decaimiento que nunca se queda encendido ya están
resueltos —no los repitas— en
[04 · 27 §4.1](./27%20-%20Accesibilidad.md#41--el-slider-de-vibración-no-es-opcional-es-la-pauta-basic)
(`haptics_iniciar()`, `haptics_pulso(_slot, _fuerza, _duracion_pasos)`, con
`global.a11y.haptics` como el slider). Lo que falta aquí es la parte de *game feel*: **cuánto**
vibra cada tipo de golpe.

| Tipo de golpe | Fuerza (0-1) | Duración (frames a 60 fps) |
|---|---|---|
| Golpe débil | 0.15 | 6 |
| Golpe normal | 0.35 | 10 |
| Golpe crítico | 0.65 | 16 |
| Explosión / impacto grande | 0.90 | 22 |
| El jugador recibe daño | 0.50 | 14 |

```gml
// --- Añadir a hit_complete() (§5.7), junto al resto de capas del golpe --------
// Requiere haptics_iniciar() llamado una vez al arrancar la partida (04 · 27 §4.1).
haptics_pulso(0, clamp(_daño * 0.03, 0.15, 0.90), clamp(round(_daño * 0.5), 6, 22));
```

La tabla y la línea de arriba son la única pieza nueva: la magnitud sale del mismo `_daño` que
ya alimenta el hit stop y el screen shake de `hit_complete()`, así que las cinco capas —
partículas, flash, knockback, shake/zoom, y ahora vibración— escalan juntas con un solo número.

> ⚠️ **No la actives por defecto en explosiones consecutivas.** `haptics_pulso()` ya reemplaza
> el pulso anterior en vez de sumarlo (04 · 27 §4.1 lo avisa: «nunca reactives la vibración sin
> dejar que decaiga antes»), pero si tu juego dispara `hit_complete()` muchas veces por segundo
> en oleadas, aplica el mismo «juice condicional» del punto 7 de este §8: reduce la fuerza de la
> vibración cuando hay más de N golpes simultáneos, igual que reduces las partículas.

---

## 8bis. La recompensa y el fracaso

Todo lo anterior en este documento sabe hacer sentir un golpe. Le falta la otra mitad del bucle
de *feedback*: la biblioteca no tenía, hasta este apartado, ninguna coreografía para un premio
ni para un fracaso que no se sintiera como un castigo. Es el hueco que señala
[Celia Hodent, *The Gamer's Brain*](https://www.celiahodent.com/) al hablar de los bucles de
recompensa, y el reverso del *juice* de combate: si el golpe comunica «esto ha pasado», la
recompensa debe comunicar «esto ha merecido la pena» y el fracaso «esto no es el final».

### 8bis.1 La coreografía de una recompensa

Cuatro tiempos, siempre en el mismo orden:

1. **Parón corto.** Un instante de silencio antes de que pase nada — el equivalente del
   *anticipation* de §4.8 aplicado a un premio en vez de a un golpe.
2. **Sonido ascendente** mientras el número sube, con el *pitch* subiendo con él: la misma
   sensación de "cha-ching" acumulándose.
3. **El número entra con `global.Ease.out_back`** (§5.2): un pequeño rebote al llegar, nunca un
   `lerp` plano que se desliza sin acento.
4. **Pausa antes de devolver el control.** El jugador necesita un instante para LEER lo que ha
   ganado antes de que el juego siga. Cortar esto de golpe es la forma más rápida de que una
   recompensa no se sienta como recompensa.

```gml
// ---------------------------------------------------------------------------
// scr_recompensa — la coreografía en cuatro tiempos
// Verificado: variable_global_exists, is_undefined, floor, array_push, array_delete,
//             array_length, audio_play_sound, audio_sound_pitch (audio ya verificado en §5.7)
// Reutiliza global.game_freeze (§5.0) y tween_to/global.Ease.out_back (§5.2)
// ---------------------------------------------------------------------------

enum RecompensaFase { PARON, CONTEO, PAUSA, CERRADA }

/// @func recompensa_mostrar(_titulo, _valor)
/// @desc Dispara la coreografía completa. Usa global.game_freeze (congelación total, ya
///       pensada para esto), NO hit_stop: hit_stop es para golpes de unos pocos frames,
///       una recompensa dura más y es deliberada, no un impacto.
function recompensa_mostrar(_titulo, _valor)
{
    global.game_freeze = true;
    global.__recompensa = {
        titulo: _titulo, valor_final: _valor, valor_mostrado: 0,
        ticks_dados: 0, fase: RecompensaFase.PARON, reloj: 0,
    };
    audio_play_sound(snd_recompensa_whoosh, 10, false);     // el sonido ascendente de entrada
}

/// @func recompensa_actualizar()  — Step, SIEMPRE (aunque global.game_freeze esté activo:
///                                  esta lógica es la excepción que tiene que seguir corriendo)
function recompensa_actualizar()
{
    if (!variable_global_exists("__recompensa") || is_undefined(global.__recompensa)) return;
    var _r = global.__recompensa;
    _r.reloj++;

    switch (_r.fase)
    {
        case RecompensaFase.PARON:                    // 1. el parón: 12 frames de nada
            if (_r.reloj >= 12)
            {
                _r.fase = RecompensaFase.CONTEO;
                _r.reloj = 0;
                tween_to(_r, "valor_mostrado", _r.valor_final, 30, global.Ease.out_back);
            }
            break;

        case RecompensaFase.CONTEO:                   // 2 y 3. sonido ascendente + ease out back
            var _progreso = (_r.valor_final == 0) ? 1 : (_r.valor_mostrado / _r.valor_final);
            if (floor(_progreso * 10) > _r.ticks_dados)
            {
                _r.ticks_dados = floor(_progreso * 10);
                var _snd = audio_play_sound(snd_recompensa_tic, 10, false);
                audio_sound_pitch(_snd, 0.9 + _progreso * 0.6);      // de 0.9x a 1.5x
            }
            if (_r.reloj >= 30) { _r.fase = RecompensaFase.PAUSA; _r.reloj = 0; }
            break;

        case RecompensaFase.PAUSA:                    // 4. pausa antes de devolver el control
            if (_r.reloj >= 40)                        // ~0,66 s a 60 fps: se lee, no se sufre
            {
                _r.fase = RecompensaFase.CERRADA;
                global.game_freeze = false;
            }
            break;

        case RecompensaFase.CERRADA:
            global.__recompensa = undefined;
            recompensa_siguiente();                    // ¿hay otra esperando su turno?
            break;
    }
}

/// @func recompensa_encolar(_titulo, _valor)
/// @desc Como recompensa_mostrar(), pero si ya hay una en pantalla espera su turno. Evita
///       que "subes de nivel" y "nueva habilidad" se pisen (carga cognitiva: solo una cosa
///       legible a la vez, 13 · 05 §1.7).
function recompensa_encolar(_titulo, _valor)
{
    if (!variable_global_exists("__recompensa_cola")) global.__recompensa_cola = [];
    array_push(global.__recompensa_cola, { titulo: _titulo, valor: _valor });
    if (!variable_global_exists("__recompensa") || is_undefined(global.__recompensa))
    {
        recompensa_siguiente();
    }
}

/// @func recompensa_siguiente()
function recompensa_siguiente()
{
    if (!variable_global_exists("__recompensa_cola")
    || array_length(global.__recompensa_cola) == 0) return;

    var _r = global.__recompensa_cola[0];
    array_delete(global.__recompensa_cola, 0, 1);
    recompensa_mostrar(_r.titulo, _r.valor);
}
```

> 💡 **El dibujo no está aquí a propósito.** El número que tiembla y el panel que lo enseña ya
> tienen componente en
> [13 · 05 §3.5h](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/05%20-%20UI%20y%20UX%20de%20juego.md#h-marcador-y-temporizador)
> (`marcador_dibujar()`): pásale `global.__recompensa.valor_mostrado` y listo. Este documento
> resuelve el CUÁNDO (la coreografía); 13 · 05 resuelve el CÓMO se ve.

### 8bis.2 Subida de nivel y desbloqueo

La curva de XP y niveles (la matemática) está en
[13 · 13](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/13%20-%20Matemáticas%20aplicadas%20al%20juego.md)
y en [04 · 04 §5.1](./04%20-%20RPG%20_%20Action%20RPG.md#51-niveles-y-curva-de-experiencia).
Cruzar el umbral es la misma coreografía de arriba, con más volumen:

```gml
/// @func jugador_subir_nivel(_nivel_nuevo, _habilidad_nueva)
/// @desc _habilidad_nueva: "" si el nivel no desbloquea nada.
function jugador_subir_nivel(_nivel_nuevo, _habilidad_nueva)
{
    camera_shake(0.25);                  // el "impacto" de cruzar el umbral (§5.1)
    fx_impact(x, y, 90, 1.2);            // ráfaga de partículas hacia arriba (§5.5)
    recompensa_encolar($"¡Nivel {_nivel_nuevo}!", _nivel_nuevo);

    if (_habilidad_nueva != "")
    {
        // en cola, no encima: la regla de "una cosa legible a la vez" de §8bis.1
        recompensa_encolar($"Nueva habilidad: {_habilidad_nueva}", 0);
    }
}
```

### 8bis.3 Pantalla de resultados

Una pantalla de resultados que aparece ya rellena no se lee, se ignora. La regla es cantar una
fila detrás de otra, nunca todas a la vez — y dejar que el jugador se la salte si ya la ha visto.

```gml
// ---------------------------------------------------------------------------
// scr_resultados
// Verificado: array_length, audio_play_sound, audio_sound_pitch
// ---------------------------------------------------------------------------

/// @func ResultadoStat(_etiqueta, _valor_final)
/// @desc Una fila de la pantalla de resultados. Sube desde 0 con un tic por paso.
function ResultadoStat(_etiqueta, _valor_final) constructor
{
    etiqueta       = _etiqueta;
    valor_final    = _valor_final;
    valor_mostrado = 0;
    terminado      = (_valor_final == 0);
}

/// @func resultados_nuevo(_filas)
/// @desc _filas: array de ResultadoStat, EN EL ORDEN en que deben cantarse.
function resultados_nuevo(_filas)
{
    return { filas: _filas, fila_actual: 0, reloj: 0 };
}

/// @func resultados_actualizar(_r)  — Step
function resultados_actualizar(_r)
{
    if (_r.fila_actual >= array_length(_r.filas)) return;      // ya se cantaron todas

    var _f = _r.filas[_r.fila_actual];
    if (_f.terminado) { _r.fila_actual++; return; }            // las de valor 0 no esperan

    _r.reloj++;
    if (_r.reloj mod 2 == 0)                                    // un paso cada 2 frames
    {
        _f.valor_mostrado++;
        var _snd = audio_play_sound(snd_recompensa_tic, 5, false);
        audio_sound_pitch(_snd, 1 + (_f.valor_mostrado / _f.valor_final) * 0.3);
    }
    if (_f.valor_mostrado >= _f.valor_final)
    {
        _f.terminado    = true;
        _r.fila_actual += 1;
        _r.reloj        = 0;
    }
}

/// @func resultados_saltar(_r)
/// @desc El jugador puede pedir el total de golpe. Cantar cada número es bonito la
///       primera vez que se ve la pantalla, no la vigésima: nunca se lo niegues.
function resultados_saltar(_r)
{
    for (var _i = 0; _i < array_length(_r.filas); _i++)
    {
        _r.filas[_i].valor_mostrado = _r.filas[_i].valor_final;
        _r.filas[_i].terminado      = true;
    }
    _r.fila_actual = array_length(_r.filas);
}

/// @func resultados_terminados(_r)
/// @desc El botón «Continuar» solo se activa cuando esto es true — si sale antes, el
///       jugador se pierde su propia puntuación.
function resultados_terminados(_r)
{
    return _r.fila_actual >= array_length(_r.filas);
}
```

### 8bis.4 El fracaso sin humillar

El reverso. `player_respawn()` en
[04 · 06 §5.7](./06%20-%20Metroidvania.md#57-puntos-de-guardado) ya resuelve «reaparecer donde
estaba» — es genérico, no exclusivo de metroidvania — y
[13 · 12 §6.8](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/12%20-%20Diseño%20narrativo%20y%20diálogos.md#68-saltar-la-cinemática-siempre-y-la-segunda-vez-sola)
ya resuelve «no repetir la cinemática» (la misma regla del salto de cinemática aplicada al
bucle de morir y reintentar, no solo al de avanzar la historia). Lo que falta es medir el coste
del reintento y vigilar el texto.

```gml
// ---------------------------------------------------------------------------
// scr_reintento — medir la fricción del fracaso en vez de darla por buena
// Verificado: get_timer, variable_global_exists, show_debug_message
// ---------------------------------------------------------------------------

/// @func reintento_iniciar()
/// @desc Llama a esto en el frame EXACTO en que el jugador pierde el control (muerte,
///       caída al vacío). Es el instante 0 del cronómetro de fricción de reintento.
function reintento_iniciar()
{
    global.__reintento_t0 = get_timer();
}

/// @func reintento_terminar()
/// @desc Llama a esto en el frame en que el jugador YA puede moverse otra vez (después del
///       fundido de entrada, no antes). Devuelve el coste real en segundos: mídelo, no lo
///       estimes (la telemetría general está en 13 · 10).
function reintento_terminar()
{
    if (!variable_global_exists("__reintento_t0")) return 0;
    var _segundos = (get_timer() - global.__reintento_t0) / 1000000;
    show_debug_message($"Coste de reintento: {_segundos} s");     // cámbialo por tu telemetría real
    return _segundos;
}
```

```gml
// Uso:
// obj_jugador — al morir
reintento_iniciar();
player_respawn();                        // 04 · 06 §5.7

// obj_jugador — Step, hasta que el fundido de entrada termine (04 · 00 §2)
if (esperando_control && !global.fundiendo)
{
    esperando_control = false;
    reintento_terminar();
}
```

> 💡 **El objetivo de referencia son 1-3 segundos** desde que el jugador pierde el control
> hasta que lo recupera — el punto de referencia que hicieron populares *Celeste* y
> *Super Meat Boy*. Si `reintento_terminar()` devuelve sistemáticamente más que eso, ahí está
> tu fricción, medida y no supuesta.

**El texto tampoco es neutral.** La misma información puede culpar al jugador o no decir nada:

| Mal (culpa al jugador) | Mejor (sin culpa) |
|---|---|
| «Has fallado.» | «Casi lo tenías.» |
| «GAME OVER» en rojo, con parón largo antes de reintentar | Vuelta rápida al punto de control, sin cartel que se recree |
| «Inténtalo de nuevo, presta más atención» | Silencio — el silencio no culpa a nadie |
| Repetir el diálogo o la cinemática del jefe en cada intento | Solo la primera vez (§6.8, arriba) |
| Contador de muertes en pantalla, siempre visible | El contador existe para tu telemetría (13 · 10), no tiene por qué mirarlo el jugador |

> ⚠️ **No hay receta de GML para el texto.** Esto es diseño de contenido, no código: la
> comprobación es leer en voz alta el mensaje de fracaso de tu juego y preguntarte si se lo
> dirías a alguien a la cara.

---

## 9. Fuentes

- Manual oficial — Sistema de partículas (`part_system_create`,
  `part_type_create`, `part_particles_create`, `part_emitter_burst`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Particles/Particle_Systems.htm
- Manual oficial — Cámaras (`camera_set_view_pos`, `camera_set_view_angle`,
  `camera_set_view_size`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Cameras_And_Display/Cameras_And_Viewports.htm
- Manual oficial — `draw_sprite_ext`, `draw_text_transformed`,
  `draw_set_alpha` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Drawing/Drawing_And_Alpha_Blending.htm
- Manual oficial — Audio (`audio_play_sound`, `audio_sound_pitch`,
  `audio_sound_gain`) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Audio/Audio.htm
- Manual oficial — `variable_instance_set` / `variable_struct_exists` —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions.htm
- Manual oficial — Structs, `static` y constructores —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Structs.htm
- Manual oficial — `gpu_set_fog` (la vía sin shaders del `hit_flash`, §5.6 bis) —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Drawing/GPU_Control/gpu_set_fog.htm
- Manual oficial — `shader_get_uniform` / `shader_set_uniform_f` (la vía con shader del
  `hit_flash`, §5.6 bis) —
  https://manual.gamemaker.io/lts/es/GameMaker_Language/GML_Reference/Asset_Management/Shaders/shader_set_uniform_f.htm
- Código real descargado (`11 - Código descargado/librerias/utilidades/HelpfulGMLScripts/`,
  `draw_sprite_solid_color.gml` y `_Maybe Not that great/Hooks/use_flash.gml`) — confirma en la
  práctica el truco de `gpu_set_fog` para forzar un color sólido, usado en §5.6 bis
- **How To Optimise Your Games** (tutorial oficial) —
  https://gamemaker.io/tutorials/how-to-optimise-your-games
- **Post-Processing FX** de FoxyOfJungle (bloom, aberración cromática,
  *color grading*) — recomendado en la guía oficial de inicio
- **How to Get Started with GameMaker in 2026** (sección de extensiones
  recomendadas) — https://gamemaker.io/tutorials/get-started-gamemaker-2026
- Manual oficial — `get_timer` (medir el coste de reintento, §8bis.4) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Maths_And_Numbers/Date_And_Time/get_timer.htm
- Manual oficial — `gamepad_set_vibration`, `gamepad_is_supported`, `gamepad_is_connected`
  (base de `haptics_pulso()`, ya verificados y citados en
  [04 · 27](./27%20-%20Accesibilidad.md), reutilizados en §8.4) —
  https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Game_Input/GamePad_Input/gamepad_set_vibration.htm
- Celia Hodent, sitio oficial — abierto el 2026-09-06, confirma la autoría de *The Gamer's
  Brain* citada en §8bis — https://www.celiahodent.com/
- ⚠️ **Martin Jonasson y Petri Purho, «Juice it or lose it», GDC Europe 2012** (grabación en
  YouTube: *"Juice it or lose it - a talk by Martin Jonasson & Petri Purho"*) y **Jan Willem
  Nijman (Vlambeer), «The Art of Screenshake», GDC 2016**: citadas por nombre en §8.2 y §8bis
  (permanence, juice) porque ya estaban asumidas en el resto del documento (§1, «Referencias»),
  pero no se ha vuelto a abrir la charla ni GDC Vault en esta sesión — GDC Vault no se puede
  rastrear (ver `_indice/auditorias/BRIEF-redactor.md`). Sin URL verificada en vivo.
