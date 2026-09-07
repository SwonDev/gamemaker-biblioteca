# 22 · Físicas con Box2D

> El motor de física integrado de GameMaker. Para puzzles físicos tipo *Angry Birds*, cajas que
> se apilan y ruedan, vehículos con ruedas, cuerdas, ragdolls. **No es para un plataformas
> normal** — eso se hace mejor a mano ([01 · Plataformas 2D](./01%20-%20Plataformas%202D.md)).
> También cubre el patrón *colocar y simular* (estilo *Besiege*): piezas que el jugador coloca
> en frío sobre una rejilla y que solo cobran física de golpe al pulsar «Simular» (§7).
>
> **Hueco de receta detectado:** las 100 funciones `physics_*` estaban catalogadas, pero sin
> una guía que enseñara a montar el mundo, crear fixtures y usar joints. Este documento lo cierra.

---

## La decisión que va antes que el código

**No mezcles física con movimiento manual.** Un objeto es de física **o** lo mueves tú con
`x`/`y`/`hspeed` — nunca las dos cosas. En cuanto activas la física en un objeto:

- Su posición la controla el motor: usas `phy_position_x`, no `x`.
- Lo mueves con **fuerzas e impulsos**, no asignando velocidad.
- `move_and_collide`, `place_meeting` y compañía **dejan de aplicar** como los conoces.

```
¿Tu juego necesita objetos que rueden, reboten, se apilen, cuelguen o choquen
de forma realista entre sí?
├─ SÍ  → Box2D. Este documento.
└─ NO  → movimiento a mano. Es más simple y más controlable.
         Ver 01 - Plataformas 2D, 02 - Top-Down.
```

> 🔺 **Un plataformas con física suele salir peor.** El salto «flotante», el control «resbaladizo»
> y los bugs de pared son casi inevitables con Box2D. Los plataformas buenos usan movimiento
> manual con colisión por ejes. Reserva la física para cuando la simulación *es* el juego.

---

## 1 · Activar el mundo y el objeto

**El mundo** vive en la sala: en las **Room Settings → Physics**, marca «Room is Physics
World» y ajusta la gravedad, o por código:

```gml
/// obj_control · Create — configurar el mundo físico
physics_world_gravity(0, 10);          // gravedad hacia abajo (y positivo = abajo)
// physics_world_gravity(0, 0);        // cenital sin gravedad (mesa de billar)
```

**El objeto:** en su Inspector, pestaña **Physics**, marca «Uses Physics». Ahí defines densidad,
restitución (rebote), fricción y la forma de colisión (la *fixture*) visualmente. Todo eso
también se puede hacer por código si generas objetos en runtime:

```gml
/// obj_caja · Create — definir la fixture por código
var _fix = physics_fixture_create();
physics_fixture_set_box_shape(_fix, sprite_width / 2, sprite_height / 2);  // media anchura/altura
physics_fixture_set_density(_fix, 0.5);       // masa: 0 = estática (suelo, paredes)
physics_fixture_set_restitution(_fix, 0.3);   // rebote: 0 = plomo, 1 = pelota loca
physics_fixture_set_friction(_fix, 0.4);      // rozamiento al deslizar
physics_fixture_bind(_fix, id);               // atar la fixture a esta instancia
physics_fixture_delete(_fix);                 // la plantilla ya no hace falta tras el bind
```

> 🔺 **Densidad 0 = objeto estático.** El suelo, las paredes y las plataformas fijas se marcan
> con densidad 0: existen, chocan, pero no se mueven ni caen. Todo lo que debe moverse necesita
> densidad > 0.
>
> 💡 **`physics_world_create(scale)`** solo hace falta si NO usas el mundo de la sala. El `scale`
> es cuántos píxeles equivalen a un metro de Box2D (típico: 0.1). Con el mundo de la sala,
> GameMaker lo gestiona por ti.

---

## 2 · Mover objetos de física: fuerzas e impulsos

```gml
/// empujar de forma continua (viento, propulsor): FUERZA
physics_apply_force(phy_position_x, phy_position_y, 0, -50);   // empuje hacia arriba

/// un golpe instantáneo (salto, disparo, explosión): IMPULSO
physics_apply_impulse(phy_position_x, phy_position_y, 0, -80); // salto de un golpe

/// impulso local (relativo a la rotación del objeto: un coche que acelera hacia donde mira)
physics_apply_local_impulse(0, 0, 0, -motor);
```

**Fuerza vs impulso**, la diferencia que confunde a todo el mundo:

| | Fuerza | Impulso |
|---|---|---|
| Efecto | Gradual, acumulativo cada step | Instantáneo, de golpe |
| Para qué | Propulsión continua, viento, motor | Saltos, disparos, explosiones |
| Dónde | En Step (mientras se mantiene) | Una vez, en el evento del golpe |

```gml
/// leer y usar el estado físico — SIEMPRE con phy_*, nunca con x/y/speed
if (keyboard_check(vk_right)) physics_apply_force(phy_position_x, phy_position_y, 30, 0);

// la velocidad actual, para limitarla
if (abs(phy_linear_velocity_x) > VELOCIDAD_MAX) {
    phy_linear_velocity_x = sign(phy_linear_velocity_x) * VELOCIDAD_MAX;
}
```

> ⚠️ **`x` e `y` son de solo lectura útiles en física** (reflejan la posición), pero para MOVER
> usa fuerzas/impulsos o, en casos concretos, asigna `phy_position_x`. Asignar `x` directamente
> pelea con el motor y produce saltos y tembleques.

---

## 3 · Las variables `phy_*` que vas a usar

De las 78 disponibles, estas son el día a día:

| Variable | Qué es |
|---|---|
| `phy_position_x` / `phy_position_y` | Posición que controla el motor |
| `phy_linear_velocity_x` / `_y` | Velocidad lineal (leer/limitar) |
| `phy_speed` | Módulo de la velocidad |
| `phy_angular_velocity` | Velocidad de giro |
| `phy_rotation` | Ángulo actual (grados) |
| `phy_fixed_rotation` | `true` = no gira nunca (personajes que no deben volcar) |
| `phy_linear_damping` | Rozamiento con el "aire": frena solo |
| `phy_active` | `false` = congelar este cuerpo sin borrarlo |

```gml
/// un personaje de física que no debe volcar como una caja
phy_fixed_rotation = true;    // en el Create
```

> 💡 **`phy_fixed_rotation = true` es el ajuste que hace jugable a un personaje de física.**
> Sin él, tu héroe rueda por el suelo como un barril. Con él, se mantiene de pie.

---

## 4 · Joints: cuerdas, ruedas, puentes

Los *joints* (juntas) unen dos cuerpos. Son lo que separa "cajas que caen" de un juego físico
de verdad.

```gml
/// RUEDA de un coche: revolute (giro alrededor de un punto)
rueda = physics_joint_revolute_create(
    id, obj_rueda,                    // los dos cuerpos
    obj_rueda.phy_position_x, obj_rueda.phy_position_y,  // punto de anclaje (el eje)
    0, 0, false,                      // sin límite de ángulo
    2000, -motor_velocidad, true,     // par máximo, velocidad, motor activado
    false);                           // ¿colisionan entre sí los dos cuerpos?

/// CUERDA / cadena: eslabones unidos con distance joints
for (var _i = 1; _i < array_length(eslabones); _i++) {
    physics_joint_distance_create(eslabones[_i-1], eslabones[_i],
        eslabones[_i-1].phy_position_x, eslabones[_i-1].phy_position_y,
        eslabones[_i].phy_position_x, eslabones[_i].phy_position_y, false);
}

/// PLATAFORMA / ascensor: prismatic (desliza en un eje)
ascensor = physics_joint_prismatic_create(obj_ancla, obj_plataforma,
    obj_plataforma.phy_position_x, obj_plataforma.phy_position_y,
    0, 1,                             // eje de deslizamiento: vertical
    0, 200, true,                     // límites min/max, ¿con límite?
    500, 40, true, false);            // fuerza motor, velocidad, motor, colisión
```

📘 **Las firmas completas de los joints son largas**: `python3 _indice/buscar.py physics_joint_revolute_create`
te da la firma exacta con todos sus argumentos antes de escribir la llamada.

> 🔺 **El orden de los argumentos de los joints es largo y fácil de equivocar.** Antes de
> escribir uno, `python3 _indice/buscar.py physics_joint_prismatic_create` para tener la firma
> delante. Son de los sitios donde más se inventa código.

---

> 🔺 **Leer y ajustar un joint en marcha:** cada tipo de junta expone sus propiedades como
> **constantes accessor** `phy_joint_*` (25 en total): `phy_joint_angle`, `phy_joint_length`,
> `phy_joint_max_motor_torque`, `phy_joint_motor_speed`, `phy_joint_translation`… Se leen y
> escriben con `physics_joint_get_value(joint, phy_joint_angle)` y
> `physics_joint_set_value(joint, phy_joint_motor_speed, 50)`. La lista completa:
> `python3 _indice/buscar.py --listar phy_joint`.

## 5 · Colisiones de física

Las colisiones se detectan en el evento **Collision** normal, pero la respuesta (el rebote, el
empuje) la calcula el motor solo. Tú solo reaccionas a lo que **significa** la colisión:

```gml
/// obj_pelota · Collision con obj_diana
// el rebote ya lo hizo Box2D; aquí solo la lógica del juego
puntos += 10;
audio_play_sound(snd_impacto, 5, false);
instance_destroy(other);
```

```gml
/// ¿hay algo físico en un punto, sin evento de colisión? (raycast simple)
if (physics_test_overlap(mouse_x, mouse_y, 0, obj_caja)) {
    // el ratón está sobre una caja física
}
```

> 💡 **Filtrar qué colisiona con qué** (bandos, "que el torso y el brazo del mismo ragdoll no
> choquen entre sí", capas de física) no es cosa de este documento: ya está resuelto con
> `physics_fixture_set_collision_group()` en
> [01 · 08 — Movimiento y colisiones §6 bis](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md#6-bis-bandos-y-capas-de-colisión),
> con el ejemplo completo del ragdoll. No lo dupliques aquí: esa sección es la fuente.

---

## 6 · Partículas de fluido: agua, humo, polvo (44 funciones que casi nadie usa)

Box2D no solo hace cuerpos rígidos: trae un **sistema de partículas de fluido** —agua que
salpica y llena huecos, polvo, lodo, humo elástico—. Son 44 funciones `physics_particle_*` que
el manual documenta pero casi ningún tutorial toca. Viven en el **mismo mundo físico** que las
fixtures, así que las partículas chocan con tus cuerpos rígidos.

```gml
/// Create — ajustes globales del sistema de partículas
physics_particle_set_radius(3);        // tamaño de cada partícula (en píxeles del mundo)
physics_particle_set_max_count(2000);  // techo: más = más bonito pero más lento
physics_particle_set_density(1);
physics_particle_set_damping(0.5);     // cuánto se frenan (viscosidad del medio)
```

```gml
/// soltar una gota de AGUA en un punto (un chorro, una fuga)
physics_particle_create(phy_particle_flag_water,
    mouse_x, mouse_y,          // posición
    0, 5,                       // velocidad inicial (cae)
    c_aqua, 0.8,                // color y alfa
    1);                         // categoría (para filtrar colisiones)
```

**El comportamiento lo eligen los flags** —esta es la clave del sistema—:

| Flag | Se comporta como |
|---|---|
| `phy_particle_flag_water` | Agua: fluye, llena huecos, salpica |
| `phy_particle_flag_viscous` | Viscoso: lodo, miel, lava lenta |
| `phy_particle_flag_powder` | Polvo/arena: se apila, no fluye |
| `phy_particle_flag_elastic` | Elástico: gelatina, se deforma y recupera |
| `phy_particle_flag_spring` | Muelle: las partículas se atraen entre sí |
| `phy_particle_flag_tensile` | Tensión superficial: gotas que se mantienen juntas |
| `phy_particle_flag_wall` | Estáticas: no se mueven (barreras de fluido) |
| `phy_particle_flag_colourmixing` | Los colores se mezclan al tocarse |

```gml
// combinar flags con | para efectos ricos: lava viscosa que mezcla color
var _lava = phy_particle_flag_viscous | phy_particle_flag_colourmixing;
physics_particle_create(_lava, x, y, 0, 0, c_orange, 1, 1);
```

**Grupos** — para crear un bloque de fluido de golpe (un charco, un depósito lleno):

```gml
physics_particle_group_begin(phy_particle_flag_water, 0,
    400, 100, 0, 0, 0, 0, c_blue, 0.7, 1, 1);
physics_particle_group_box(64, 32);    // rellena un rectángulo de fluido
physics_particle_group_end();
```

**Dibujarlas** — en el evento Draw:

```gml
/// dibuja todas las partículas de la categoría 1 con un sprite de gota
physics_particle_draw(0, 1, spr_gota, 0);
// o con transformación (escala/color) para más control:
physics_particle_draw_ext(0, 1, spr_gota, 0, 1, 1, 0, c_white, 1);
```

> ⚠️ **El sistema de partículas de fluido es CARO.** Cada partícula es una simulación física.
> `physics_particle_set_max_count` es tu freno: 500-2000 va bien; 20.000 arrastra hasta un PC
> potente. Y `physics_particle_delete_region_box/circle` para limpiar las que salen de pantalla.
>
> 🔺 **Requiere que la sala sea un mundo físico** (§1), igual que las fixtures. Sin mundo físico
> activo, `physics_particle_create` no hace nada.
>
> 💡 **No confundir con el sistema de partículas normal** (`part_*`, [Novedades 05](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20part%C3%ADculas%20nuevo.md)):
> ese es visual, barato, y no colisiona con nada. `physics_particle_*` es simulación de fluido
> real que choca con el mundo. Usa `part_*` para chispas y humo decorativo; `physics_particle_*`
> solo cuando el fluido **es** una mecánica (un puzzle de agua, lava que te mata).

---

## 7 · Sandbox de física / contraption builder

Todo lo anterior asume que las fixtures y los joints se crean **una vez**, en el `Create` de
un objeto que ya existe en la sala. Hay un patrón distinto — el de juegos como *Besiege*, donde
el jugador **construye** antes de jugar: coloca piezas en una rejilla en tiempo de diseño, sin
que la gravedad las toque, guarda esa construcción, y solo al pulsar «Simular» cobra vida de
golpe como un cuerpo físico completo con sus joints.

```
DISEÑO (sin física, solo datos)  →  GUARDAR (JSON)  →  SIMULAR (instanciar + fixtures + joints)
        ↑                                                              │
        └──────────────────────  DESHACER (destruir instancias)  ──────┘
```

> ⚠️ No se ha podido abrir ninguna fuente sobre *Besiege* en esta sesión — la red no responde
> (falla incluso la resolución DNS, con y sin `curl`, y `WebFetch`; WebSearch está agotado). Se
> nombra solo como referencia de diseño ampliamente conocida del género; no se cita ningún dato
> concreto (estudio, fecha, cifras) que no se haya verificado en vivo.

### 7.1 · Catálogo de piezas: forma + joint, como datos

Cada pieza colocable es un **dato**, no una instancia: qué objeto la representa, su forma de
fixture y con qué tipo de joint se conecta a la pieza vecina. Los tres joints son los mismos de
**[§4 · Joints: cuerdas, ruedas, puentes](#4--joints-cuerdas-ruedas-puentes)** de este mismo
documento — no se repiten aquí sus firmas completas; siguen siendo largas y fáciles de
equivocar, así que antes de tocarlas: `python3 _indice/buscar.py physics_joint_revolute_create`.

```gml
/// función de apoyo — el catálogo de piezas del taller
function taller_catalogo_piezas() {
    return [
        { id: "viga",   objeto: obj_pieza_viga,   forma: "caja",    ancho: 64, alto: 16,
          densidad: 0.8, junta: "revolute" },   // eslabón rígido que puede girar en el punto de unión
        { id: "rueda",  objeto: obj_pieza_rueda,  forma: "circulo", radio: 16,
          densidad: 0.6, junta: "revolute" },   // rueda: gira libre sobre su eje, §4
        { id: "cuerda", objeto: obj_pieza_cuerda, forma: "caja",    ancho: 8,  alto: 32,
          densidad: 0.3, junta: "distance" },   // eslabón de cadena, §4
        { id: "piston", objeto: obj_pieza_piston, forma: "caja",    ancho: 48, alto: 16,
          densidad: 1.0, junta: "prismatic" },  // desliza en un eje, §4
    ];
}

/// función de apoyo — buscar un tipo del catálogo por su id
function taller_tipo_de(_id) {
    for (var _i = 0; _i < array_length(catalogo); _i++) {
        if (catalogo[_i].id == _id) return catalogo[_i];
    }
    return undefined;
}
```

### 7.2 · Modo diseño: colocar en rejilla sin física activa

La rejilla de ocupación (celda ocupada/libre, fantasma que se dibuja bajo el ratón) **ya está
resuelta** en
[04 · 09 — Survival y crafting §5.3](./09%20-%20Survival%20y%20crafting.md#53-construcción-con-ghost-preview)
con `objWorldGrid`: un struct sparse `"x,y" → dato`, con `ocupada()`/`ocupar()`/`liberar()`. No
se duplica aquí ese mecanismo; solo se adapta a lo que este patrón necesita de más: cada celda
tiene que recordar **de qué tipo de pieza es**, para poder decidir el joint al simular — no le
basta con saber que está ocupada.

```gml
/// obj_taller · Create — el estado del taller: catálogo + rejilla de diseño
#macro TALLER_CELDA 64              // tamaño de cada celda, en píxeles

catalogo           = taller_catalogo_piezas();  // §7.1
pieza_elegida       = 0;             // índice en el catálogo (lo cambia la UI de selección)
celdas              = {};            // "gx,gy" → { tipo, gx, gy } — solo datos, cero instancias
modo_simulando      = false;
instancias_fisicas  = [];            // se rellena al simular; sirve para deshacer (§7.4)

taller_clave = function(_gx, _gy) {
    return string(_gx) + "," + string(_gy);
};
```

```gml
/// obj_taller · Step — colocar/quitar piezas mientras se diseña
if (modo_simulando) exit;    // en simulación no se coloca: la física manda

if (mouse_check_button_pressed(mb_left)) {
    var _gx = mouse_x div TALLER_CELDA;
    var _gy = mouse_y div TALLER_CELDA;
    var _clave = taller_clave(_gx, _gy);

    if (!variable_struct_exists(celdas, _clave)) {
        celdas[$ _clave] = { tipo: catalogo[pieza_elegida].id, gx: _gx, gy: _gy };
    }
}

if (mouse_check_button_pressed(mb_right)) {
    var _clave = taller_clave(mouse_x div TALLER_CELDA, mouse_y div TALLER_CELDA);
    if (variable_struct_exists(celdas, _clave)) variable_struct_remove(celdas, _clave);
}
```

```gml
/// obj_taller · Draw — piezas en modo diseño: fantasmas, NUNCA cuerpos físicos
if (modo_simulando) exit;

var _claves = variable_struct_get_names(celdas);
for (var _i = 0; _i < array_length(_claves); _i++) {
    var _pieza = celdas[$ _claves[_i]];
    var _tipo  = taller_tipo_de(_pieza.tipo);

    draw_sprite_ext(_tipo.objeto.sprite_index, 0,
        _pieza.gx * TALLER_CELDA + TALLER_CELDA * 0.5,
        _pieza.gy * TALLER_CELDA + TALLER_CELDA * 0.5,
        1, 1, 0, c_white, 0.5);    // alfa 0.5: es un preview, todavía no existe de verdad
}
```

> 🔺 **La gracia del modo diseño es que nada de esto toca `physics_*`.** Mientras `celdas` sea
> solo datos y el dibujo sea `draw_sprite_ext` sobre un fantasma, la construcción a medio hacer
> no puede desplomarse por gravedad ni empujarse a sí misma. La física no existe hasta §7.4.

### 7.3 · Serializar la construcción: solo datos, nunca instancias

Mismo espíritu que el resto de la biblioteca para persistencia
([01 · 14 — Persistencia y archivos §8](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#8-json-la-opción-recomendada-en-2026))
y que `objWorldGrid.serialize()` en la receta de survival: se guarda **la forma de recrear la
construcción**, no una referencia viva a nada. `celdas` ya es un struct de structs planos —
`json_stringify` lo serializa entero de un golpe.

```gml
/// construccion_guardar() — vuelca `celdas` a un array plano y lo guarda en JSON
function construccion_guardar(_nombre_archivo) {
    var _piezas = [];
    var _claves = variable_struct_get_names(celdas);
    for (var _i = 0; _i < array_length(_claves); _i++) {
        array_push(_piezas, celdas[$ _claves[_i]]);
    }

    var _json = json_stringify({ piezas: _piezas }, true);   // true = con indentación

    var _buffer = buffer_create(string_byte_length(_json) + 1, buffer_fixed, 1);
    buffer_write(_buffer, buffer_string, _json);   // buffer_string: incluye el nulo final
    buffer_save(_buffer, _nombre_archivo);
    buffer_delete(_buffer);
}

/// construccion_cargar() — reconstruye `celdas` desde el JSON guardado
function construccion_cargar(_nombre_archivo) {
    if (!file_exists(_nombre_archivo)) return false;

    var _buffer = buffer_load(_nombre_archivo);
    var _json   = buffer_read(_buffer, buffer_string);
    buffer_delete(_buffer);

    var _datos = json_parse(_json);

    celdas = {};
    for (var _i = 0; _i < array_length(_datos.piezas); _i++) {
        var _pieza = _datos.piezas[_i];
        celdas[$ taller_clave(_pieza.gx, _pieza.gy)] = _pieza;
    }
    return true;
}
```

> ⚠️ **Guarda antes de simular, no después.** Si la construcción vuelca al simular (una torre
> mal apoyada, un motor que se embala) y no la guardaste, la pierdes: no hay vuelta atrás a un
> estado que nunca se escribió a disco. Ver «Las trampas» más abajo.

### 7.4 · Botón «Simular»: instanciar de golpe, activar física, crear joints

Al pulsar «Simular» se recorre `celdas` **dos veces**: una para instanciar cada pieza y darle su
fixture (mismo trío `physics_fixture_create` / `physics_fixture_bind` / `physics_fixture_delete`
de **[§1 · Activar el mundo y el objeto](#1--activar-el-mundo-y-el-objeto)**), y una segunda para
crear los joints entre vecinos — **tienen que existir las dos fixtures antes de unirlas con un
joint**, así que el orden de los dos bucles no es opcional.

```gml
/// obj_taller · función de apoyo — decide el joint según el tipo de pieza
/// (firmas completas en §4; aquí solo se elige CUÁL usar y con qué anclaje)
function taller_conectar(_instancia_a, _instancia_b, _tipo_junta) {
    var _anchor_x = (_instancia_a.phy_position_x + _instancia_b.phy_position_x) / 2;
    var _anchor_y = (_instancia_a.phy_position_y + _instancia_b.phy_position_y) / 2;

    if (_tipo_junta == "revolute") {
        physics_joint_revolute_create(_instancia_a, _instancia_b, _anchor_x, _anchor_y,
            0, 0, false, 0, 0, false, false);
    } else if (_tipo_junta == "distance") {
        physics_joint_distance_create(_instancia_a, _instancia_b,
            _instancia_a.phy_position_x, _instancia_a.phy_position_y,
            _instancia_b.phy_position_x, _instancia_b.phy_position_y, false);
    } else if (_tipo_junta == "prismatic") {
        physics_joint_prismatic_create(_instancia_a, _instancia_b, _anchor_x, _anchor_y,
            0, 1, 0, TALLER_CELDA, true, 500, 0, false, false);
    }
}

/// obj_taller · el botón «Simular»
function taller_simular() {
    if (modo_simulando) return;

    var _capa   = layer_get_id("Instancias");
    var _claves = variable_struct_get_names(celdas);
    var _mapa_instancias = {};   // "gx,gy" → instancia recién creada, para enlazar joints

    // 1) instanciar cada pieza y darle fixture: SIN esto, no hay cuerpo que enlazar
    for (var _i = 0; _i < array_length(_claves); _i++) {
        var _clave = _claves[_i];
        var _pieza = celdas[$ _clave];
        var _tipo  = taller_tipo_de(_pieza.tipo);

        var _wx = _pieza.gx * TALLER_CELDA + TALLER_CELDA * 0.5;
        var _wy = _pieza.gy * TALLER_CELDA + TALLER_CELDA * 0.5;
        var _inst = instance_create_layer(_wx, _wy, _capa, _tipo.objeto);

        var _fix = physics_fixture_create();
        if (_tipo.forma == "caja") {
            physics_fixture_set_box_shape(_fix, _tipo.ancho / 2, _tipo.alto / 2);
        } else {
            physics_fixture_set_circle_shape(_fix, _tipo.radio);
        }
        physics_fixture_set_density(_fix, _tipo.densidad);
        physics_fixture_set_restitution(_fix, 0.1);
        physics_fixture_set_friction(_fix, 0.4);
        physics_fixture_bind(_fix, _inst);
        physics_fixture_delete(_fix);   // la plantilla ya no hace falta, §1

        _mapa_instancias[$ _clave] = _inst;
        array_push(instancias_fisicas, _inst);
    }

    // 2) AHORA que todas las fixtures existen, enlazar cada pieza con su vecina
    for (var _i = 0; _i < array_length(_claves); _i++) {
        var _clave  = _claves[_i];
        var _pieza  = celdas[$ _clave];
        var _tipo   = taller_tipo_de(_pieza.tipo);
        var _inst_a = _mapa_instancias[$ _clave];

        var _vecino_derecha = taller_clave(_pieza.gx + 1, _pieza.gy);
        if (variable_struct_exists(_mapa_instancias, _vecino_derecha)) {
            taller_conectar(_inst_a, _mapa_instancias[$ _vecino_derecha], _tipo.junta);
        }

        var _vecino_abajo = taller_clave(_pieza.gx, _pieza.gy + 1);
        if (variable_struct_exists(_mapa_instancias, _vecino_abajo)) {
            taller_conectar(_inst_a, _mapa_instancias[$ _vecino_abajo], _tipo.junta);
        }
    }

    modo_simulando = true;
}
```

### 7.5 · Deshacer: volver al modo diseño

`celdas` nunca se toca durante la simulación — es el plano, no la máquina—, así que deshacer es
solo destruir lo que se instanció y bajar la bandera. El fantasma del §7.2 vuelve a dibujarse
exactamente como estaba, sin restaurar nada a mano.

```gml
/// obj_taller · el botón «Deshacer» — destruir la simulación, volver al plano
function taller_deshacer() {
    if (!modo_simulando) return;

    for (var _i = 0; _i < array_length(instancias_fisicas); _i++) {
        if (instance_exists(instancias_fisicas[_i])) instance_destroy(instancias_fisicas[_i]);
    }
    instancias_fisicas = [];
    modo_simulando = false;
}
```

> 💡 **Reiniciar de golpe** (probar la misma construcción otra vez desde cero) es
> `taller_deshacer()` seguido de `taller_simular()`: como `celdas` no cambió, la segunda
> simulación instancia exactamente las mismas piezas en las mismas celdas.

---

## Las trampas

| Trampa | Consecuencia |
|---|---|
| Mezclar física con `x`/`y`/`hspeed` manual | Saltos, tembleques, bugs imposibles |
| Densidad > 0 en el suelo | El suelo se cae |
| Olvidar `phy_fixed_rotation` en el personaje | Rueda como un barril |
| Asignar velocidad en vez de impulso | Movimiento que ignora la masa |
| Inventar el orden de argumentos de un joint | El joint no hace lo que crees |
| Usar Box2D para un plataformas normal | Control resbaladizo, salto flotante |
| No hacer `physics_fixture_delete` tras el bind | Fuga de memoria de fixtures |
| Simular sin haber serializado antes (§7.3) | Si la construcción vuelca, se pierde: no hay a qué volver |
| Crear los joints antes de que existan las dos fixtures (§7.4) | El joint no engancha nada, o crashea |

---

## Ver también

- [01 · Plataformas 2D](./01%20-%20Plataformas%202D.md) — cuándo NO usar física (movimiento manual)
- [08 · Movimiento y colisiones](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) — la colisión por ejes, la alternativa a la física
- [09 · Survival y crafting §5.3](./09%20-%20Survival%20y%20crafting.md#53-construcción-con-ghost-preview) — la rejilla de ocupación con ghost preview que reutiliza §7.2
- [14 · Persistencia y archivos §8](../01%20-%20Fundamentos/14%20-%20Persistencia%20y%20archivos.md#8-json-la-opción-recomendada-en-2026) — `json_stringify`/`json_parse` a fondo, lo que usa §7.3
- El manual: `buscar.py physics_` lista las 100 funciones con sus firmas
