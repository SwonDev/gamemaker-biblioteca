# 08 · Plataformas estilo Megaman X — apuntes técnicos

> **Fuente:** serie *Megaman X Tutorial* (6 partes, 2022-2023) de
> [Altair_AML](https://www.youtube.com/@Altair_AML) · GameMaker 2022.
>
> | # | Vídeo | Duración | Qué enseña |
> |---|---|---:|---|
> | 1 | [Físicas básicas](https://youtu.be/2LRKvF5C6iw) | 19:09 | Colisión por ejes, rampas, plataformas atravesables |
> | 2 | [Wall jump, escaleras y slide](https://youtu.be/uiUe-szy53Q) | 14:16 | Los tres movimientos insignia |
> | 3 | [Cambio de sprites + sonido](https://youtu.be/4-NfzClhBJQ) | 10:14 | Máquina de estados de animación |
> | 4 | [X-Buster](https://youtu.be/zNOLaiAyXgg) | 9:40 | Disparo, carga y sprites de ataque |
> | 5 | [Dash](https://youtu.be/AcImiGbQaow) | 7:20 | Sistema de habilidades y doble pulsación |
> | 6 | [Daño e intro](https://youtu.be/e1jeJAU0cQY) | 11:54 | Daño, invulnerabilidad, muerte, HUD |
>
> **Esto no es una transcripción.** Son apuntes propios: se explica **la técnica** y el código
> está **reescrito y verificado para LTS 2026**, con las correcciones marcadas 🔺. Para seguir
> la clase tal cual —y para descargar el pack de sprites del autor— ve a los vídeos.

---

## Por qué esta serie importa

Es **el único plataformas completo explicado en español paso a paso** que se ha encontrado, y
el patrón que enseña —*colisión resuelta eje por eje contra objetos sólidos*— es el que usa la
mayoría de los plataformas 2D de precisión. Si vas a hacer un plataformas en GameMaker,
empieza por aquí y no por `move_and_collide`.

**Ojo:** el autor avisa él mismo de que no es un experto y de que hay código mejorable. Estos
apuntes recogen la técnica **ya depurada**, no sus primeras versiones (en la parte 2 él mismo
retira el objeto `rampa_back` de la parte 1: aquí ya no aparece).

---

## 1 · El núcleo: colisión por ejes

### La idea

No uses `speed`/`direction` ni el motor de físicas. Lleva **tu propia velocidad** en dos
variables (`_hsp`, `_vsp`), y **resuelve cada eje por separado**: primero mueves en X y
corriges, después mueves en Y y corriges. Así nunca te quedas encajado en una esquina.

### El truco del `bbox`

El origen del sprite casi nunca está en el borde de la máscara. Si al pegarte a un bloque usas
solo `bbox_right`, quedas descolocado tantos píxeles como haya entre el origen y la máscara.
Por eso se precalcula la distancia origen→máscara y se suma al reposicionar:

```gml
/// Step — al principio
var _bx = x - bbox_left;    // distancia del origen al borde izquierdo de la máscara
var _by = y - bbox_top;     // distancia del origen al borde superior
```

### Create

```gml
/// obj_player · Create
grav        = 0.3;      // aceleración de caída por frame
grav_max    = 8;        // velocidad de caída máxima (velocidad terminal)
jump_power  = 6.5;      // impulso vertical del salto
spd         = 0.4;      // aceleración horizontal
spd_max     = 2.2;      // velocidad horizontal máxima

hsp = 0;                // velocidad horizontal actual
vsp = 0;                // velocidad vertical actual

depth = -10;
mask_index = spr_player_mask;   // una máscara única para TODOS los estados
```

> 🔺 **2026:** usa una **única máscara de colisión** para el personaje (`mask_index`) en lugar
> de dejar que cada sprite aporte la suya. Si la máscara cambia de tamaño entre la animación de
> correr y la de agacharse, las correcciones de posición dejan de cuadrar y el personaje vibra.

### `approach()` — el helper que se usa en todas partes

Lleva un valor hacia otro a una velocidad fija, sin pasarse. Es el script que el autor dedica
un vídeo entero a defender ([*Approach*](https://youtu.be/niwwb1zd3vg), 2:46), y con razón:
sustituye a media docena de `if` en aceleración, gravedad y frenado.

```gml
/// scr_approach(valor, objetivo, cantidad) → real
function approach(_valor, _objetivo, _cantidad) {
    if (_valor < _objetivo) return min(_valor + _cantidad, _objetivo);
    else                    return max(_valor - _cantidad, _objetivo);
}
```

> 🔺 **2026:** en LTS 2026 esto ya existe de serie como
> [`lerp`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Maths_And_Numbers/Number_Functions/lerp.md)
> para interpolación proporcional, pero **no** es lo mismo: `lerp` se acerca cada vez más
> despacio, `approach` avanza a paso constante y **llega**. Para gravedad y frenado quieres
> `approach`. Mantenlo.

### Detectar suelo, incluidas las plataformas atravesables

Una plataforma de tipo *one-way* (`obj_across`) solo colisiona si vienes **desde arriba**. La
comprobación no es «¿hay una plataforma debajo?» sino «¿hay una plataforma debajo **cuyo borde
superior esté por debajo de mis pies**?»:

```gml
/// scr_suelo(dist) → bool · ¿hay suelo a `dist` píxeles por debajo?
function suelo(_dist) {
    // bloque macizo o rampa: colisión siempre
    if (place_meeting(x, y + _dist, obj_bloque)) return true;
    if (place_meeting(x, y + _dist, obj_rampa))  return true;

    // plataforma atravesable: solo si venimos de arriba
    var _hay = false;
    with (instance_place(x, y + _dist, obj_across)) {
        if (other.bbox_bottom <= bbox_top) _hay = true;
    }
    return _hay;
}
```

> 💡 **Por qué `with` + `instance_place`:** `instance_place` devuelve **qué** instancia estorba,
> y `with` te mete dentro de ella para poder leer *su* `bbox_top` comparándolo con el
> `bbox_bottom` del jugador (`other`). Con `place_meeting` a secas solo sabrías que hay algo.

### Salto y gravedad

```gml
/// Step
var _kd = keyboard_check(vk_right) - keyboard_check(vk_left);  // -1, 0 o 1
var _kj = keyboard_check_pressed(vk_space);
var _kj_rel = keyboard_check_released(vk_space);

// --- salto ---
if (_kj && vsp >= -1 && suelo(1)) vsp = -jump_power;

// salto de altura variable: al soltar, se corta el impulso
if (_kj_rel && vsp < -1) vsp = 0;

// --- gravedad ---
if (!suelo(1)) vsp = approach(vsp, grav_max, grav);
```

> 💡 **El corte del salto** (`_kj_rel`) es lo que da el «salto con peso» de Megaman: mantener
> pulsado salta alto, un toque salta bajo. Son dos líneas y cambian por completo el tacto.

### El truco de `_kd`: un `if` en lugar de cuatro

`keyboard_check` devuelve 1 o 0, así que `derecha - izquierda` da **-1, 0 o 1** de una tacada,
y las dos teclas a la vez se cancelan solas. Después multiplicas por la velocidad máxima:

```gml
if (_kd != 0) hsp = approach(hsp, spd_max * _kd, spd);
else          hsp = approach(hsp, 0, spd);       // frenado
```

### Colisión horizontal

```gml
if (place_meeting(x + hsp, y, obj_bloque)) {
    with (instance_place(x + hsp, y, obj_bloque)) {
        if (other.hsp > 0) other.x = bbox_left  - (other.x - other.bbox_right) - 1;
        else               other.x = bbox_right + (other.x - other.bbox_left)  + 1;
    }
    hsp = 0;
}
x += hsp;
```

### Colisión vertical

```gml
if (vsp > 0 && suelo(vsp)) {          // cayendo: buscamos suelo
    while (!suelo(1)) y += 1;         // bajar hasta tocar
    vsp = 0;
} else if (vsp < 0 && place_meeting(x, y + vsp, obj_bloque)) {  // subiendo: techo
    with (instance_place(x, y + vsp, obj_bloque)) {
        other.y = bbox_bottom + (other.y - other.bbox_top) + 1;
    }
    vsp = 0;
}
y += vsp;
```

### Rampas

Las rampas son el punto delicado. El patrón es: **si estás dentro de la rampa, sube hasta
salir; si estás justo encima, baja hasta apoyarte.** Se resuelve con dos `while` de 1 píxel:

```gml
if (vsp >= 0 && place_meeting(x, y, obj_rampa)) {
    while (place_meeting(x, y, obj_rampa)) y -= 1;   // salir por arriba
    vsp = 0;
}
```

> 🔺 **2026:** desde 2023 GameMaker admite **colisiones con decimales**
> (`place_meeting(x, y + 0.1, ...)`), lo que permite afinar mucho la detección en rampas. El
> autor lo aprovecha. Sigue siendo válido en LTS 2026 y es la forma recomendada.

### Cuando todo falla: escapar de un atasco

Si con velocidades altas el personaje acaba encajado dentro de un bloque, la solución robusta
es **buscar en espiral la posición libre más cercana** y teletransportarlo ahí. Es la red de
seguridad que el autor añade en la parte 2 y que le permite borrar el parche `rampa_back`:

```gml
/// scr_escapar(radio_max) · saca al jugador del sólido más cercano
function escapar(_radio_max = 32) {
    if (!place_meeting(x, y, obj_bloque)) return true;
    for (var _r = 1; _r <= _radio_max; _r++) {
        for (var _a = 0; _a < 360; _a += 15) {
            var _nx = x + lengthdir_x(_r, _a);
            var _ny = y + lengthdir_y(_r, _a);
            if (!place_meeting(_nx, _ny, obj_bloque)) {
                x = _nx; y = _ny;
                return true;
            }
        }
    }
    return false;   // no había hueco: mejor saberlo que fallar en silencio
}
```

> 💡 **Lección general, no solo de plataformas:** cuando un sistema de colisión tiene un caso
> límite raro, a menudo sale más barato **una función de recuperación** que intentar que el
> caso no ocurra nunca.

---

## 2 · Los tres movimientos de Megaman X

Los tres funcionan igual: **una variable de estado que bloquea el código normal**. Antes de
aplicar gravedad, movimiento lateral o salto, se comprueba que no haya un estado activo.

### Slide (deslizarse por la pared)

```gml
/// Create
slide      = false;
slide_wait = 0;      // frames antes de empezar a resbalar
muro_dir   = 0;      // 0 = muro a la derecha, 180 = a la izquierda

/// Step — antes de la gravedad
if (!slide) vsp = approach(vsp, grav_max, grav);   // la gravedad se bloquea

// activar: cayendo, con muro al lado y pulsando HACIA el muro
if (!slide && vsp > 0 && !suelo(1)) {
    var _muro_der = place_meeting(x + 1, y, obj_bloque) && _kd > 0;
    var _muro_izq = place_meeting(x - 1, y, obj_bloque) && _kd < 0;
    if (_muro_der ^^ _muro_izq) {          // XOR: uno u otro, nunca los dos
        slide      = true;
        vsp        = 0;
        slide_wait = 0;
        muro_dir   = _muro_der ? 0 : 180;
        image_xscale = (muro_dir == 0) ? 1 : -1;
    }
}
```

> 💡 **`^^` es XOR lógico** y aquí es exactamente lo que quieres: si hubiera muro a los dos
> lados (un pasillo de un bloque de ancho), no debe activarse.
>
> 💡 **`?:` es el operador ternario**, forma corta de `if/else` para asignar un valor.

Salir del estado en cuanto deje de tener sentido: no hay muro, tocas suelo, o sueltas la tecla.

### Wall jump

Es un estado **con dos tiempos**: primero el personaje se queda pegado un instante, después
sale despedido en diagonal hacia el lado contrario.

```gml
/// Create
wall      = false;
wall_tmr  = 0;
wall_wait = 4;     // frames pegado a la pared antes de saltar
wall_push = 12;    // frames de empuje hacia el lado opuesto
wall_power = 7;

/// Step
if (_kj && !wall && !suelo(1) && (place_meeting(x+1, y, obj_bloque) || place_meeting(x-1, y, obj_bloque))) {
    slide = false;  wall = true;  wall_tmr = 0;  vsp = 0;
}

if (wall) {
    wall_tmr++;
    if (wall_tmr >= wall_wait) {
        vsp = -wall_power;
        hsp = (muro_dir == 0) ? -spd_max : spd_max;   // empuje al lado opuesto
    }
    if (wall_tmr > wall_wait + wall_push) {
        wall = false;  wall_tmr = 0;
        // si ya no mantienes salto, se corta la subida (igual que el salto normal)
        if (!keyboard_check(vk_space)) vsp = 0;
    }
}
```

### Escaleras

Es el más largo de los tres porque tiene **animaciones de entrada y de salida** durante las que
no aceptas input. Se controla con temporizadores: mientras `lad_tmr != 0`, el movimiento
vertical no se ejecuta.

Detalles que hacen que se sienta bien:
- Al agarrarte, el personaje se **centra en el eje X de la escalera** (`with (escalera) other.x = x;`).
- Se coloca un objeto invisible tipo plataforma en lo alto de la escalera, para poder **pisarla
  por arriba** y para detectar que pulsas «abajo» y quieres bajar por ella.
- `image_speed = 0` cuando dejas de moverte: la animación de trepar se **congela**, no sigue
  sola. Es un detalle pequeño que se nota muchísimo.
- Salidas: llegar arriba (con animación), pulsar salto, o que se acabe la escalera.

---

## 3 · Máquina de estados de animación

Este es el patrón más reutilizable de toda la serie, sirva o no para un Megaman.

### El problema

Si asignas `sprite_index` cada frame, la animación **nunca avanza**: se reinicia sola. Hay que
cambiar el sprite **solo cuando el estado cambia de verdad**.

### La solución

```gml
/// Create
estado = "";

/// scr_set_estado(nombre) · cambia el sprite una sola vez por transición
function set_estado(_nuevo) {
    if (estado == _nuevo) exit;      // ← la guarda que lo hace todo funcionar
    estado = _nuevo;
    image_index = 0;
    image_speed = 1;

    switch (_nuevo) {
        case "stand":  sprite_index = spr_x_stand;  break;
        case "walk":   sprite_index = spr_x_walk;   break;
        case "jump":   sprite_index = spr_x_jump;   break;
        case "fall":   sprite_index = spr_x_fall;   break;
        case "land":   sprite_index = spr_x_land;   audio_play_sound(snd_land, 1, false); break;
        case "slide":  sprite_index = spr_x_slide;  audio_play_sound(snd_wall, 1, false); break;
    }
}
```

Y en el Step, una cadena de prioridad de arriba abajo:

```gml
if (estado_habilidad == none) {
    if (suelo(1)) {
        if (hsp == 0) set_estado("stand");
        else          set_estado("walk");
    } else {
        if (vsp < 0) set_estado("jump");
        else         set_estado("fall");
    }
}
```

### El evento Animation End

El evento **Animation End** decide qué pasa cuando una animación termina. Es lo que distingue
animaciones en bucle (caminar) de animaciones de un solo uso (aterrizar, saltar):

```gml
/// obj_player · Animation End
switch (sprite_index) {
    case spr_x_land:                        // aterrizar encadena con estar quieto
        set_estado("stand");
        break;

    case spr_x_jump:                        // saltar se congela en el último frame
    case spr_x_slide:
        image_speed = 0;
        image_index = image_number - 1;
        break;

    case spr_x_stand:                       // parpadeo: vuelve al frame 0
        image_index = 0;
        image_speed = 0;
        break;
}
```

> 🔺 **2026:** el evento sigue llamándose **Animation End** y funciona igual. Consulta
> [la página del manual en español](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Object_Properties/Object_Events.md).

### Sprites de ataque «encajados»

Los sprites de disparo de Megaman X son los normales con el brazo levantado, **con los mismos
fotogramas**. Para que al disparar mientras caminas no se reinicie la animación, se cambia el
sprite **conservando `image_index`**:

```gml
function actualizar_sprite() {
    var _idx = image_index;          // guardar el fotograma actual
    set_estado_forzado(estado);      // recalcular sprite según `atacando`
    image_index = _idx;              // restaurarlo
}
```

---

## 4 · Sistema de habilidades (dash) con constructores

En la parte 5 el código da un salto de calidad: en vez de una variable booleana por habilidad,
se usa **un enum de habilidad activa + un struct de bloqueos**.

```gml
/// Create
enum SKILL { NINGUNA, DASH, FLOTAR }

skill       = SKILL.NINGUNA;
skill_timer = 0;

// qué se bloquea mientras dure la habilidad
bloqueo = {
    gravedad : false,
    ataque   : false,
    hmov     : false,
    teclas   : false
};

function skill_limpiar() {
    skill        = SKILL.NINGUNA;
    skill_timer  = 0;
    bloqueo.gravedad = false;
    bloqueo.ataque   = false;
    bloqueo.hmov     = false;
    bloqueo.teclas   = false;
}
```

Y en el Step, un único `switch`:

```gml
switch (skill) {
    case SKILL.DASH:
        skill_timer++;
        bloqueo.hmov = true;
        if (skill_timer == 1)  hsp = spd_max * 2.5 * image_xscale;
        if (skill_timer >= 30) skill_limpiar();
        break;
}
```

> 💡 **Por qué esto escala:** añadir una habilidad nueva = un valor en el `enum` + un `case`.
> No tocas nada más. El propio autor reconoce que no es una máquina de estados canónica y
> recomienda montarla bien si te ves con ganas; el consejo es bueno, pero **este patrón
> intermedio ya te lleva muy lejos** y es mucho más fácil de leer que quince booleanos.

### Detectar doble pulsación con un constructor

Para activar el dash con «derecha, derecha» hace falta recordar la pulsación anterior. Un
constructor lo encapsula limpiamente:

```gml
/// Create
function DoblePulsacion(_tecla, _ventana = 15) constructor {
    tecla   = _tecla;
    ventana = _ventana;    // frames de margen entre las dos pulsaciones
    timer   = 0;

    static comprobar = function() {
        if (timer > 0) timer--;
        if (keyboard_check_pressed(tecla)) {
            if (timer > 0) { timer = 0; return true; }
            timer = ventana;
        }
        return false;
    };
}

dash_der = new DoblePulsacion(vk_right);
dash_izq = new DoblePulsacion(vk_left);

/// Step
if (dash_der.comprobar() || dash_izq.comprobar()) skill = SKILL.DASH;
```

> 🔺 **2026:** `static` dentro de un constructor es la forma correcta y eficiente de declarar
> métodos: la función se guarda **una sola vez** y la comparten todas las instancias del
> struct. Ver
> [Structs](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Overview/Structs.md).

---

## 5 · Daño, invulnerabilidad y muerte

### Recibir daño

```gml
/// Step — al final
var _enemigo = collision_rectangle(bbox_left, bbox_top, bbox_right, bbox_bottom,
                                   obj_enemigo_padre, false, true);
if (_enemigo != noone && !invulnerable && !danado) {
    global.hp -= _enemigo.dano;
    danado = true;
    dano_timer = 0;
    audio_play_sound(snd_dano, 5, false);
    limpiar_teclas();                    // suelta todos los inputs
    hsp = -image_xscale * 2;             // retroceso hacia atrás
    vsp = -3;                            // saltito característico
}
```

> 💡 **`collision_rectangle` frente a un evento Collision:** te devuelve **qué** te ha dado y
> puedes leerle el `dano`. Con el evento Collision necesitarías un evento por cada tipo de
> enemigo. Usa un **objeto padre** (`obj_enemigo_padre`) y una sola comprobación.

### Parpadeo de invulnerabilidad

```gml
if (invulnerable) {
    inv_timer++;
    image_alpha = (inv_timer div 3) % 2;    // ← parpadeo cada 3 frames
    if (inv_timer > 90) { invulnerable = false; inv_timer = 0; image_alpha = 1; }
}
```

> 💡 `(t div 3) % 2` alterna 0 y 1 cada 3 frames. Es más barato y más legible que un `if` con
> una alarma, y ajustas la velocidad del parpadeo cambiando un número.

### Muerte por fases con un temporizador

En lugar de alarmas encadenadas, **un contador y un `switch` de hitos**. Todo el guion de la
muerte se lee de un vistazo y se ajusta cambiando números:

```gml
if (global.hp <= 0) {
    muerte_timer++;
    switch (muerte_timer) {
        case 1:   set_estado("muerte"); limpiar_todo();  break;
        case 50:  audio_play_sound(snd_muerte, 10, false);
                  image_alpha = 0;
                  explosion_radial(x, y, 16);            break;
        case 90:  layer_sequence_create("Efectos", x, y, seq_fundido); break;
        case 150: global.hp = global.hp_max;
                  room_restart();                        break;
    }
    exit;                        // ← corta el resto del Step
}
```

> 💡 **`exit`** para el evento entero ahí mismo. Es lo que evita tener que envolver los 300
> renglones anteriores en un `if (!muerto)`.

### Partículas en espiral (muerte de Megaman)

```gml
function explosion_radial(_x, _y, _n) {
    var _paso = 360 / _n;
    for (var _i = 0; _i < _n; _i++) {
        var _p = instance_create_layer(_x, _y, "Efectos", obj_particula);
        _p.direction = _i * _paso;
        _p.speed     = 3;
    }
}
```

### HUD con Nine Slice

La barra de vida se dibuja con **Nine Slice** (el marco se estira sin deformarse) y las líneas
de energía con un `for`:

```gml
/// obj_hud · Draw GUI
draw_sprite_stretched(spr_hud_marco, 0, 16, 16, 24, 96);
for (var _i = 0; _i < global.hp; _i++) {
    draw_sprite(spr_hud_barra, 0, 20, 100 - _i * 4);
}
```

> 🔺 **2026:** Nine Slice se configura en el **editor de sprites**, no por código. Ver
> [Nine Slices](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sprite_Properties/Nine_Slices.md).
> Y dibuja siempre el HUD en **Draw GUI**, nunca en Draw: así no le afecta la cámara.

---

## Lo que se puede reutilizar tal cual

| Pieza | Sirve para | Sección |
|---|---|---|
| `approach()` | cualquier aceleración, frenado o gravedad | [1](#1--el-núcleo-colisión-por-ejes) |
| Colisión por ejes + `bbox` | **cualquier** plataformas o cenital 2D | [1](#1--el-núcleo-colisión-por-ejes) |
| `escapar()` en espiral | red de seguridad de cualquier sistema de colisión | [1](#1--el-núcleo-colisión-por-ejes) |
| `set_estado()` con guarda | **cualquier** animación de personaje | [3](#3--máquina-de-estados-de-animación) |
| `enum` + struct de bloqueos | cualquier sistema de habilidades | [4](#4--sistema-de-habilidades-dash-con-constructores) |
| `DoblePulsacion` | dash, combos, atajos | [4](#4--sistema-de-habilidades-dash-con-constructores) |
| Muerte por hitos | cualquier secuencia con guion | [5](#5--daño-invulnerabilidad-y-muerte) |

---

## Qué revisar antes de usarlo en 2026

1. **Handles frente a IDs numéricos.** La serie es de 2022. En LTS 2026 los recursos son
   *handles*, no enteros: no compares con `< 0` ni hagas aritmética con ellos. Ver
   [02 - Novedades 2026](../02%20-%20Novedades%202026/).
2. **`instance_create_layer` necesita que la capa exista** en todas las rooms donde se use.
3. **Comprueba cada función** con `python3 "_indice/buscar.py" <nombre>` antes de darla por
   buena: el código de los vídeos está escrito a mano y en pantalla se lee mal.

---

Fuente original: canal [Altair_AML](https://www.youtube.com/@Altair_AML). El pack de sprites y
el proyecto completo están enlazados en la descripción de cada vídeo.
