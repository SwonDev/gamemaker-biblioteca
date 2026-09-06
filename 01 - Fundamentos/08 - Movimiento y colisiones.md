# 08 · Movimiento y colisiones

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement/Movement.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/Collisions.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/Collision_Compatibility_Mode.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Movement/move_and_collide.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Instances/Instance_Variables/collision_space.htm>
> - `gm-cli manual read "place_meeting"` / `"instance_place"`

---

## 1. Dos formas de mover una instancia

GameMaker te permite mover de dos maneras fundamentalmente distintas:

| Enfoque | Variables / funciones | Cuándo usarlo |
|---|---|---|
| **Posición directa** | `x`, `y` | Control total, plataformas, tilemaps, `move_and_collide()` |
| **Vector velocidad** | `speed`, `direction`, `hspeed`, `vspeed`, `gravity`, `friction` | Movimiento balístico, proyectiles, juegos tipo *Asteroids* |

### Variables integradas de movimiento

```gml
direction          // ángulo en grados (0 = derecha, 90 = arriba, 270 = abajo)
speed              // píxeles por step
hspeed / vspeed    // componentes horizontal y vertical
gravity            // aceleración constante por step
gravity_direction  // dirección de la gravedad (270 = abajo)
friction           // deceleración por step
```

```gml
// Movimiento tipo Asteroids
direction = image_angle;
speed = 6;
friction = 0.05;

// Propulsión (en Step si se pulsa Arriba)
if (keyboard_check(vk_up))
{
    motion_add(image_angle, 0.2);
}
```

### Variables de posición

```gml
x, y                // posición actual
xprevious, yprevious// posición en el step anterior
xstart, ystart      // posición inicial al crearse
```

### Funciones de movimiento

```
motion_add(dir, velocidad)      // añade al vector actual
motion_set(dir, velocidad)      // fija el vector
move_towards_point(x, y, vel)   // moverse hacia un punto
move_bounce_all(adv)            // rebotar contra todo
move_bounce_solid(adv)          // rebotar contra sólidos
move_contact_all(dir, maxdist)  // moverse hasta tocar algo
move_contact_solid(dir, maxdist)
move_outside_all(dir, maxdist)  // salir de una colisión
move_outside_solid(dir, maxdist)
move_random(hsnap, vsnap)       // posición aleatoria
move_snap(hsnap, vsnap)         // ajustar a rejilla
move_wrap(horiz, vert, margen)  // envolver por los bordes
place_snapped(hsnap, vsnap)     // ¿está ajustado a rejilla?
move_and_collide(...)           // ← la "estrella" moderna
```

> ⚠️ Muchas de estas funciones dependen del concepto de **solid**, un sistema legacy. Para proyectos nuevos, prefiere las funciones de colisión explícitas.

---

## 2. `move_and_collide()` — la función moderna

```gml
move_and_collide(dx, dy, obj, [num_iteraciones], [xoff], [yoff], [max_x_move], [max_y_move])
```

Mueve la instancia la distancia dada en X e Y, **evitando** el objeto o tilemap indicado. Permite **subir pendientes y pequeños escalones** que de otro modo bloquearían el movimiento.

**Devuelve un array** con los handles de las instancias y tilemaps con los que ha colisionado.

### Argumentos

| Argumento | Tipo | Descripción |
|---|---|---|
| `dx` | Real | Distancia a mover en X |
| `dy` | Real | Distancia a mover en Y |
| `obj` | Object / Instance / Tile Map ID / **Array** | Qué evitar. Acepta `all`, `other`, tilemaps y **arrays combinándolos** |
| `num_iteraciones` | Real (opc.) | Pasos a dar. Por defecto **4** |
| `xoff` | Real (opc.) | Dirección X alternativa al colisionar. `0` = comportamiento por defecto (perpendicular) |
| `yoff` | Real (opc.) | Dirección Y alternativa |
| `max_x_move` | Real (opc.) | Distancia máxima en X. `-1` = sin límite (por defecto) |
| `max_y_move` | Real (opc.) | Distancia máxima en Y. `-1` = sin límite |

### Cómo funciona por dentro

1. Divide el movimiento en `num_iteraciones` pasos.
2. En cada paso mueve `point_distance(0,0,dx,dy) / num_iteraciones` píxeles.
3. Comprueba colisiones.
4. Si encuentra una, **intenta rodearla** moviéndose en perpendicular (o hacia `xoff`/`yoff`).
5. Ese movimiento de rodeo **también cuenta como iteración**.

> ⚠️ **No devuelve todas las colisiones posibles**, solo las que afectaron al movimiento hasta que no hicieron falta más comprobaciones. Para todas, usa `instance_place_list()`.

> 💡 **Usa la máscara de colisión del sprite** de la instancia (o `mask_index`).

### Ejemplo 1: movimiento básico

```gml
move_and_collide(8, 0, all);
// Mueve 8px a la derecha evitando CUALQUIER instancia. 4 iteraciones por defecto.
```

### Ejemplo 2: recoger las instancias con las que chocas

```gml
var _colisiones = move_and_collide(vel_x, vel_y, obj_terreno);

for (var i = 0; i < array_length(_colisiones); i++)
{
    var _colisionador = _colisiones[i];
    with (_colisionador)
    {
        show_debug_message("Colisión con instancia {0}", id);
    }
}
```

### Ejemplo 3: contra un tilemap

```gml
// Create event (solo una vez)
tilemap = layer_tilemap_get_id("Tiles_1");

// Step event
move_and_collide(8, 0, tilemap);
```

### Ejemplo 4: combinando objetos y tilemaps

```gml
// Create
var _tilemap = layer_tilemap_get_id("Tiles_1");
objetos_solidos = [obj_pared, obj_caja, _tilemap];

// Step
move_and_collide(vel_x, vel_y, objetos_solidos);
```

### Ejemplo 5: evitar el bug clásico de los plataformas

```gml
// ⚠️ Sin max_y_move, al aterrizar la gravedad se suma a la velocidad
//    horizontal y el personaje "acelera" un frame.
vel_y += gravedad;

move_and_collide(
    vel_x, vel_y,
    [obj_suelo, tilemap_suelo],
    4,          // iteraciones
    0, 0,       // sin dirección alternativa
    -1,         // sin límite en X
    abs(vel_x)  // ← en Y no nos movemos más que en X: evita el bug
);
```

---

## 3. Comprobar colisiones

### 3.1 Contra objetos: `place_meeting()`

```gml
place_meeting(x, y, obj)
```

Comprueba una posición buscando colisión, usando la máscara de la instancia que ejecuta el código.

> Conceptualmente: **mueve la instancia a la nueva posición, comprueba, vuelve y te dice si había colisión.**

**Devuelve:** `Boolean`

```gml
// Step event
if (!place_meeting(x + 4, y, obj_roca))
{
    x += 4;
}
```

> Funciona con colisiones precisas **solo si ambas** partes tienen marcada la opción «precise». Si no, se usa la bounding box.

> 💡 Si necesitas el ID de la instancia con la que chocas, usa `instance_place()`.

### 3.2 Contra múltiples objetos

Dos formas:

**A. Con un objeto padre (recomendado)**

```gml
// Creas obj_solido como padre de obj_roca y obj_arbusto
if (!place_meeting(x + 4, y, obj_solido)) { x += 4; }
```

**B. Con un array**

```gml
if (!place_meeting(x + 4, y, [obj_roca, obj_arbusto])) { x += 4; }
```

> 💡 El manual recomienda el método del **padre**: lo reutilizas en muchas llamadas sin tener que mantener un array sincronizado.

### 3.3 Obtener la instancia: `instance_place()`

```gml
instance_place(x, y, obj)
```

Igual que `place_meeting()` pero **devuelve el handle** de la instancia encontrada (o el Tile Map Element ID), o **`noone`** si no hay nada.

```gml
var _inst = instance_place(x, y, obj_enemigo);
if (_inst != noone)          // ✅ SIEMPRE compara contra noone
{
    hp -= _inst.dmg;
    instance_destroy(_inst);
}
```

> ⚠️ `place_meeting()` es **ligeramente más rápida**. Úsala si no necesitas el handle.

> ⚠️ **No uses el valor de retorno como booleano.** Un tilemap con ID `0` es un valor válido que evaluaría como `false`.

### 3.4 Contra tilemaps

```gml
// Create
tilemap = layer_tilemap_get_id("TileLayer");

// Step
if (!place_meeting(x + 4, y, tilemap)) { x += 4; }
```

**Requisitos imprescindibles:**

1. Las colisiones contra tilemaps usan la **máscara de colisión del sprite del tile set** (se configura en el Sprite Editor).
2. ⚠️ Un tilemap **sin tile set asignado** (o con un tile set sin sprite) **no funciona**: siempre devuelve `false`.
3. ⚠️ La opción **«Disable Source Sprite Export»** del tile set debe estar **DESACTIVADA**, porque se necesita el sprite para la comprobación.

### 3.5 Funciones de colisión simple

| Función | Devuelve |
|---|---|
| `place_empty(x, y)` | ¿Está libre de CUALQUIER instancia? |
| `place_free(x, y)` | ¿Está libre de instancias **sólidas**? |
| `place_meeting(x, y, obj)` | ¿Colisiono con `obj` ahí? |
| `position_empty(x, y)` | ¿Hay algo en ese punto? (usa punto, no máscara) |
| `position_meeting(x, y, obj)` | ¿Hay una instancia de `obj` en ese punto? |
| `position_change(x, y, obj, perf)` | Mueve a la posición si está libre |
| `position_destroy(x, y)` | Destruye instancias en ese punto |
| `instance_place(x, y, obj)` | Handle de la instancia en esa posición |
| `instance_place_list(x, y, obj, lista, ordered)` | Rellena una lista con **todas** |
| `instance_position(x, y, obj)` | Handle en un **punto** (sin máscara) |
| `instance_position_list(...)` | Lista con todas en un punto |

---

## 4. Máscaras, bounding boxes y el cambio de 2022.1

### Qué máscara se usa

La instancia usa la máscara de colisión de su `sprite_index`, a menos que le asignes otra con `mask_index`.

Esa máscara se:
- **escala** por `image_xscale` e `image_yscale`,
- **rota** por `image_angle`.

### Elegir la forma de la máscara

En el Sprite Editor, además del **modo** del cuadro delimitador (Automático, Imagen completa,
Manual), eliges el **tipo** de máscara. La forma no es una decisión estética: cada tipo cuesta
más que el anterior a la hora de resolver colisiones.

| Tipo (Sprite Editor) | Constante en `sprite_collision_mask()` | Coste relativo | Úsala para |
|---|---|---|---|
| **Rectangle** | `bboxkind_rectangular` | El más barato: un test de rectángulos alineados a ejes | Balas, ítems, la mayoría de plataformas y enemigos simples |
| **Rectangle With Rotation** | *(solo desde el editor; la función no la admite — ver abajo)* | Más lento que Rectangle, más barato que Precise | Naves, proyectiles o vehículos que giran y necesitan que su caja gire con `image_angle` |
| **Ellipse** | `bboxkind_ellipse` | Más lento que Rectangle With Rotation | Objetos redondos donde las esquinas de un rectángulo darían falsos positivos |
| **Diamond** | `bboxkind_diamond` | Más lento y con más sobrecarga de CPU que Ellipse | Siluetas en rombo (tiles isométricos) |
| **Precise** | `bboxkind_precise` | El más caro de los "normales": sigue el contorno alfa del sprite (una máscara compuesta de todas las subimágenes) | Hitboxes ajustadas al dibujo (jefes, sprites con huecos grandes) cuando el coste es asumible |
| **Precise per frame** (`sepmasks = true`) | `bboxkind_precise` + `sepmasks` | **El más caro de todos**: una máscara distinta por cada subimagen | Casos muy puntuales; evítalo si te vale una máscara compuesta |

> ⚠️ El propio manual lo dice sin rodeos: siempre que dos instancias se encuentran y ambas
> tienen máscara válida, se comprueba **el cuadro delimitador Y la máscara** — y esa segunda
> comprobación es la que cuesta. Usa **Rectangle** salvo que de verdad lo necesites.
> 📘 [Sprites — el editor](../09%20-%20Manual%20oficial/manual-lts-2026-es/The_Asset_Editors/Sprites.md).

**Fijar la máscara desde código: `sprite_collision_mask()`**

```gml
sprite_collision_mask(ind, sepmasks, bboxmode, bbleft, bbtop, bbright, bbbottom, kind, tolerance)
```

Cambia en tiempo de ejecución la máscara de un sprite ya cargado (típicamente uno traído con
`sprite_add()` o `sprite_duplicate()`).

```gml
// Sprite cargado dinámicamente: máscara precisa, una por subimagen,
// cuadro delimitador automático (bboxmode = 0)
spr_enemigo_din = sprite_add("enemigo.png", 8, true, true, 0, 0);
sprite_collision_mask(spr_enemigo_din, true, 0, 0, 0, 0, 0, bboxkind_precise, 0);
```

> ⚠️ **Limitación documentada por el manual: no admite «Rectangle With Rotation».** Los tipos
> que puedes fijar por código son `bboxkind_rectangular`, `bboxkind_ellipse`,
> `bboxkind_diamond`, `bboxkind_precise` y `bboxkind_spine` (este último, para sprites Spine).
> Una caja rectangular que rote con `image_angle` **solo se configura a mano en el Sprite
> Editor**. Para un sprite cargado en tiempo de ejecución que necesite esa forma, la alternativa
> es `bboxkind_precise` (más caro) o comprobar tú mismo un rectángulo rotado con el teorema de
> los ejes separadores, ya escrito en
> [13 · 13 §6.7 «AABB frente a OBB»](../13%20-%20Dise%C3%B1o%20y%20producci%C3%B3n%20de%20videojuegos/13%20-%20Matem%C3%A1ticas%20aplicadas%20al%20juego.md).
>
> ⚠️ Solo funciona sobre sprites **añadidos o duplicados** (`sprite_add()`, `sprite_duplicate()`),
> nunca directamente sobre un sprite ya existente del proyecto; y solo con sprites de mapa de
> bits (no funciona con sprites SWF ni Spine/JSON).
>
> 📘 [`sprite_collision_mask`](../09%20-%20Manual%20oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Asset_Management/Sprites/Sprite_Manipulation/sprite_collision_mask.md).

### La bounding box

La bounding box es el rectángulo que rodea la **bounding box transformada** de la máscara.

> ⚠️ No es el rectángulo alineado a ejes alrededor de la máscara, sino el rectángulo alrededor de la bounding box de la máscara **ya transformada**.

Se accede con las variables:
```gml
bbox_left   bbox_right
bbox_top    bbox_bottom
```

### ⚠️ Cambio de 2022.1: bounding boxes INCLUSIVAS y sin redondear

| | Sistema LEGACY | Sistema ACTUAL (2026) |
|---|---|---|
| Coordenadas | **Redondeadas a enteros** | Sin redondear, **tal cual** |
| Bordes inferior/derecho | **Exclusivos**: máscara 16×16 → de (0,0) a (15,15) | **Inclusivos**: de (0.0, 0.0) a (16.0, 16.0) |

**Consecuencia:** la bounding box siempre se extiende **1 píxel más allá** de su esquina inferior derecha respecto a la bounding box del sprite.

```gml
// Un sprite cuadrado de 16x16:
sprite_get_bbox_right(spr) → 15.0   // el píxel 16, contando desde 0
bbox_right                → 16      // + la X de la instancia
```

### Cómo se cuenta el solapamiento

Las comprobaciones se hacen **en coordenadas de room**. A nivel de píxel, **cuenta como solapamiento cuando se cubre el CENTRO de ese píxel**.

```gml
// Para colisionar con una bounding box de (0.0,0.0) a (16.0,16.0),
// tu máscara debe tocar el área entre (0.5, 0.5) y (15.5, 15.5)
```

> ⚠️ **Excepciones donde NO hace falta cubrir el centro del píxel:**
> - Forma contra forma: `rectangle_in_rectangle()` y similares.
> - Forma contra una máscara que no es de instancia: `collision_rectangle()` contra tilemaps.
> - `collision_point()` y `collision_line()`: se comprueban **en cualquier parte** del píxel. Un punto en `(15.99, 15.99)` da `true`; en `(16.0, 16.0)`, `false`.

> ⚠️ **Con vistas que amplían** una porción de la room, algunos píxeles de la room cubren varios del viewport. Pueden parecer solapados visualmente sin estarlo en coordenadas de room.

### Rotación: la regla de los dos sprites

> En una colisión entre dos instancias, la comprobación de bounding box alineada a ejes **solo** se hace si **AMBOS** sprites tienen máscara «Rectangle».
> Si uno usa «Rectangle With Rotation» o «Precise», **ambas** bounding boxes se tratan como rotadas.

### Collision Compatibility Mode

Si tu proyecto es anterior a 2022.1 y las colisiones se comportan raro, puedes activar **«Collision Compatibility Mode»** en las *General Game Options* para volver al sistema legacy.

> ⚠️ Es un parche, no una solución. El manual recomienda **probar y actualizar tu código** al sistema nuevo, que es más preciso y lógico.
>
> En proyectos nuevos, **no hace falta activarlo**.

---

## 5. Colisiones avanzadas

Todas comparten tres argumentos comunes:

| Argumento | Qué es |
|---|---|
| `obj` | El objeto a comprobar. Puede ser un ID de instancia, un tipo de objeto, o `all`. **Si es un padre, incluye a todos sus hijos.** |
| `prec` | `true` para colisiones precisas (solo si la máscara está marcada como «precise»; más costoso). `false` usa bounding box. |
| `notme` | `true` para excluirse a sí mismo de la comprobación. |

> ⚠️ Si hay **múltiples** instancias en el área, solo se devuelve **una**, y **puede ser cualquiera** de ellas.

```
collision_circle        collision_circle_list
collision_ellipse       collision_ellipse_list
collision_line          collision_line_list
collision_point         collision_point_list
collision_rectangle     collision_rectangle_list
```

```gml
// ¿Hay un enemigo a menos de 80px?
var _e = collision_circle(x, y, 80, obj_enemigo, false, true);
if (_e != noone)
{
    show_debug_message($"Enemigo detectado: {_e}");
}

// Todas las instancias en una línea (ataque de espada)
var _lista = ds_list_create();
var _n = collision_line_list(x, y, x + 40, y, obj_enemigo, false, true, _lista, true);

for (var i = 0; i < _n; i++)
{
    with (_lista[| i]) { vida -= 10; }
}
ds_list_destroy(_lista);
```

### Colisiones SIN máscara (para cuando no hay sprite)

```
point_in_rectangle     point_in_triangle      point_in_circle
rectangle_in_rectangle rectangle_in_triangle  rectangle_in_circle
```

```gml
// Ratón sobre un botón dibujado a mano (sin sprite)
if (point_in_rectangle(mouse_x, mouse_y, x, y, x + 120, y + 40))
{
    // hover
}
```

> Estas funciones **no** requieren cubrir el centro del píxel.

---

## 6. El collision space (novedad 2024.14)

Cada instancia pertenece a un **espacio de colisión**, y **solo puede colisionar con instancias de su mismo espacio**.

```gml
collision_space   // variable de solo lectura
```

Valores posibles:

| Constante | Significado | Valor |
|---|---|---|
| `colspace.room` | No está en capas UI | 0 |
| `colspace.ui_view` | Capa UI con «Game View» = «Viewports» | 1 |
| `colspace.ui_display` | Capa UI con «Game View» = «Display» | 2 |

**Consecuencias:**
- Una instancia en una capa **Display UI** no puede colisionar con las de una capa de room ni de una capa **Viewport UI**.
- Esto afecta **tanto a los eventos de colisión como a las funciones de colisión**.
- También afecta a las funciones de **desactivación de instancias**: por defecto solo activan/desactivan las del mismo espacio.

```gml
// Activa solo las instancias desactivadas de MI mismo espacio
instance_activate_all(collision_space);

// Activar explícitamente las del espacio de la room
instance_activate_all(colspace.room);
```

---

## 6 bis. Bandos y capas de colisión

Cuando el juego crece, «con qué colisiono» deja de ser una única lista y pasa a ser una
**matriz**: el jugador bloquea con el mundo pero no con sus propias balas; los proyectiles
enemigos dañan al jugador pero no a otros enemigos; los triggers no bloquean a nadie. Sin un
patrón, esto degenera en comprobaciones sueltas y contradictorias repartidas por todo el
proyecto.

### La matriz «quién colisiona con quién»

Ejemplo con seis bandos típicos de un shooter top-down:

| Bando ↓ / colisiona con → | Mundo | Jugador | Enemigo | Proy. aliado | Proy. enemigo | Trigger |
|---|---|---|---|---|---|---|
| **Jugador** | Bloquea | — | Recibe daño | — | Recibe daño | Activa |
| **Enemigo** | Bloquea | Inflige daño | — (opcional) | Recibe daño | — | — |
| **Proyectil aliado** | Se destruye | — | Inflige daño | — | — | — |
| **Proyectil enemigo** | Se destruye | Inflige daño | — | — | — | — |
| **Trigger** | — | — | — | — | — | — |

«—» significa que **no se comprueba esa pareja**: ni falta hace, y comprobarla es tiempo de CPU
tirado. La matriz es el diseño; el código de abajo es su traducción directa.

### Con objetos padre y arrays en `move_and_collide` / `place_meeting`

Un padre por bando, y **un array por instancia con lo que ese bando necesita comprobar** — no
hace falta más estructura que la que ya usa este documento en §2 y §3.2:

```gml
// ═══ Objetos padre (uno por bando; sin código propio, solo agrupan) ═══
// obj_bando_mundo        ← obj_pared, obj_plataforma, obj_caja
// obj_bando_jugador      ← obj_jugador
// obj_bando_enemigo      ← obj_enemigo_bala, obj_enemigo_melee
// obj_bando_proy_aliado  ← obj_bala_jugador
// obj_bando_proy_enemigo ← obj_bala_enemigo
// obj_bando_trigger      ← obj_checkpoint, obj_zona_evento

// ─── obj_jugador · Create ───
// Solo el mundo me bloquea el movimiento
solidos = [obj_bando_mundo];

// ─── obj_jugador · Step ───
move_and_collide(vel_x, vel_y, solidos);

// Enemigos y balas enemigas SÍ me hacen daño, pero no bloquean mi movimiento
var _amenaza = instance_place(x, y, obj_bando_enemigo);
if (_amenaza == noone) { _amenaza = instance_place(x, y, obj_bando_proy_enemigo); }
if (_amenaza != noone) { with (_amenaza) { instance_destroy(); } vida -= 10; }

// ─── obj_bala_jugador · Create ───
solidos = [obj_bando_mundo];

// ─── obj_bala_jugador · Step ───
var _col = move_and_collide(vel_x, vel_y, solidos);
if (array_length(_col) > 0) { instance_destroy(); exit; }   // choca con el mundo: desaparece

var _blanco = instance_place(x, y, obj_bando_enemigo);
if (_blanco != noone)
{
    with (_blanco) { vida -= other.dano; }
    instance_destroy();
}
```

> 💡 Es el mismo patrón del **padre recomendado** de §3.2, aplicado a bandos en vez de a tipos
> de terreno: cada bando es un padre, cada instancia decide contra qué padres comprueba.

### La variante de máscara de bits (muchos bandos)

Con seis bandos, seis arrays por instancia son manejables. Con quince (facciones, alianzas
cambiantes, distintos tipos de trigger…), mantener un array por bando y sincronizarlo cuando
cambia una alianza es frágil. La alternativa es una **máscara de bits**: cada bando es una
potencia de dos, y cada instancia guarda **con qué bandos reacciona** como un único entero.

```gml
// ═══ Un macro por bando: una potencia de dos cada uno ═══
#macro BANDO_MUNDO           (1 << 0)   // 1
#macro BANDO_JUGADOR         (1 << 1)   // 2
#macro BANDO_ENEMIGO         (1 << 2)   // 4
#macro BANDO_PROY_ALIADO     (1 << 3)   // 8
#macro BANDO_PROY_ENEMIGO    (1 << 4)   // 16
#macro BANDO_TRIGGER         (1 << 5)   // 32

// ─── obj_bala_enemigo · Create ───
bando         = BANDO_PROY_ENEMIGO;              // qué SOY
mascara_dano  = BANDO_MUNDO | BANDO_JUGADOR;     // con qué bandos reacciono

// ─── obj_bala_enemigo · Step ───
// obj_colisionable es el padre común de TODO lo que participa en el sistema de bandos
var _lista = ds_list_create();
var _n = instance_place_list(x, y, obj_colisionable, _lista, false);

for (var i = 0; i < _n; i++)
{
    var _otro = _lista[| i];
    if ((_otro.bando & mascara_dano) != 0)      // ¿el bando del otro está en mi máscara?
    {
        if (_otro.bando == BANDO_JUGADOR) { with (_otro) { vida -= 10; } }
        instance_destroy();
        break;
    }
}
ds_list_destroy(_lista);
```

> ⚠️ La máscara de bits **no sustituye** a `place_meeting()` / `move_and_collide()`: sigues
> necesitando una comprobación de posición (aquí, `instance_place_list()` contra el padre
> común) para saber QUÉ instancias están ahí. El `&` de la máscara decide, **entre las que ya
> están ahí**, cuáles importan. Es un filtro posterior a la comprobación geométrica, no un
> sustituto de ella.
>
> 💡 Con 32 bandos posibles (`1 << 31`) sobra para cualquier proyecto realista. Si necesitas
> más, agrupa bandos afines bajo el mismo bit.

### Cuándo el `collision_space` de §6 NO es la respuesta

El `collision_space` (§6) separa **capas UI de la room**: es un interruptor de todo o nada,
pensado para que el HUD no colisione con el mundo. **No sirve** para las relaciones finas de la
tabla de arriba (jugador sí, aliado no): para eso están los objetos padre o la máscara de bits,
no un espacio de colisión distinto.

### Filtrado de colisiones en Box2D: `physics_fixture_set_collision_group()`

Si el objeto tiene las físicas activadas (§7), la matriz de bandos de arriba **no aplica**: las
instancias con física dejan de usar máscara y bounding box, así que `place_meeting()` e
`instance_place()` no garantizan funcionar sobre ellas (ya avisado en §7). Box2D tiene su
propio mecanismo, más limitado que la matriz de arriba: **grupos de colisión**.

```gml
physics_fixture_set_collision_group(fixture, group)
```

- `group` es un entero entre **-32 768 y 32 767**.
- Dos fixtures con el **mismo grupo positivo** *siempre* colisionan entre sí.
- Dos fixtures con el **mismo grupo negativo** *nunca* colisionan entre sí.
- `0` (por defecto) es «sin grupo»: se aplican las reglas normales de colisión física.

```gml
// Los eslabones de un ragdoll no deben chocar entre sí
var _fix_torso = physics_fixture_create();
physics_fixture_set_collision_group(_fix_torso, -1);

var _fix_brazo = physics_fixture_create();
physics_fixture_set_collision_group(_fix_brazo, -1);   // mismo grupo negativo: nunca chocan entre sí
```

> ⚠️ **No es un sistema de categorías y máscaras como el Box2D "de libro"** (category bits /
> mask bits): GameMaker solo expone el **grupo de colisión**, que fuerza «siempre» o «nunca»
> entre miembros del mismo grupo; para el resto de parejas se aplican las reglas normales de
> forma y densidad. Detalle de fixtures y respuesta física en
> [04 · 22 §5 «Colisiones de física»](../04%20-%20Recetas%20por%20g%C3%A9nero/22%20-%20F%C3%ADsicas%20con%20Box2D.md).
>
> ⚠️ El propio manual pide moderación: **mantén el número de grupos al mínimo**, porque
> calcular colisiones basadas en grupos es más caro que la comprobación normal.

---

## 7. Físicas (Physics) como alternativa

Si activas las físicas del objeto, las instancias dejan de usar la mayoría de variables integradas y **ya no usan la máscara ni la bounding box**: usan **fixtures**.

> ⚠️ Las funciones de colisión normales **no garantizan funcionar** con instancias con físicas activadas.

Funciones específicas:

```gml
physics_test_overlap(x, y, angulo, todos)   // ¿los fixtures se solapan?
physics_raycast(x1, y1, x2, y2, ...)       // raycast contra fixtures
```

| | Colisiones estándar | Físicas (fixtures) |
|---|---|---|
| Basado en | Máscara del sprite | **Fixtures** (formas de colisión físicas) |
| Control | Tú mueves y compruebas | El motor simula |
| Curva de aprendizaje | Baja | Media-alta |
| Ideal para | Plataformas, top-down, tilemaps | Puzzle físicos, ragdolls, simulación |
| Variables | `x`, `y`, `hspeed`… | `phy_position_x`, `phy_linear_velocity`… |

> ⚠️ **Al desactivar una instancia con físicas, sus fixtures SIGUEN interactuando** con la simulación. Para eso usa `phy_active = false`.

> ⚠️ **No se recomienda `instance_change()` con físicas**: las propiedades físicas **no se transfieren** a la nueva instancia.

---

## 8. Ejemplo completo: personaje que se mueve y colisiona

### Versión A: top-down con `move_and_collide()`

```gml
// ═══════════ obj_jugador ═══════════

// ─────────── CREATE EVENT ───────────
velocidad      = 3.2;
vel_x          = 0;
vel_y          = 0;

// Cacheamos el tilemap: solo lo buscamos una vez
tilemap_suelo  = layer_tilemap_get_id("Tiles_Colision");

// ─────────── STEP EVENT ───────────
// 1. Leer la intención del jugador
var _izq = keyboard_check(ord("A")) || keyboard_check(vk_left);
var _der = keyboard_check(ord("D")) || keyboard_check(vk_right);
var _arr = keyboard_check(ord("W")) || keyboard_check(vk_up);
var _aba = keyboard_check(ord("S")) || keyboard_check(vk_down);

var _dx = _der - _izq;
var _dy = _aba - _arr;

// 2. Normalizar el vector para no ir más rápido en diagonal
if (_dx != 0 || _dy != 0)
{
    var _longitud = point_distance(0, 0, _dx, _dy);
    _dx /= _longitud;
    _dy /= _longitud;
}

// 3. Aplicar velocidad
vel_x = _dx * velocidad;
vel_y = _dy * velocidad;

// 4. Animación según la dirección
if (vel_x != 0 || vel_y != 0)
{
    direction = point_direction(0, 0, vel_x, vel_y);
    if (direction >= 45 && direction < 135)      { sprite_index = spr_player_arriba; }
    else if (direction >= 135 && direction < 225){ sprite_index = spr_player_izquierda; }
    else if (direction >= 225 && direction < 315){ sprite_index = spr_player_abajo; }
    else                                          { sprite_index = spr_player_derecha; }
}
else
{
    image_speed = 0;
    image_index = 0;
}

// 5. Mover comprobando colisiones contra tilemap Y objetos sólidos
var _colisiones = move_and_collide(
    vel_x, vel_y,
    [obj_pared, obj_caja, tilemap_suelo],
    4      // iteraciones
);

// 6. Reaccionar a lo que hemos tocado
if (array_length(_colisiones) > 0)
{
    for (var i = 0; i < array_length(_colisiones); i++)
    {
        var _col = _colisiones[i];

        // ¿Es una instancia o un tilemap?
        if (is_handle(_col) && instance_exists(_col))
        {
            var _es_empujable = (object_get_parent(_col.object_index) == obj_empujable);
            if (_es_empujable)
            {
                with (_col)
                {
                    move_and_collide(other.vel_x * 0.5, other.vel_y * 0.5,
                                     [obj_pared, other.tilemap_suelo]);
                }
            }
        }
    }
}
```

### Versión B: plataformas con gravedad

```gml
// ═══════════ obj_jugador_plataformas ═══════════

// ─────────── CREATE EVENT ───────────
vel_x     = 0;
vel_y     = 0;
gravedad  = 0.5;
vel_salto = -11;
vel_correr = 4;
en_suelo  = false;
coyote    = 0;         // "coyote time": perdón al saltar tras salir del borde
COYOTE_MAX = 6;

tilemap_suelo = layer_tilemap_get_id("Tiles_Colision");

// ─────────── STEP EVENT ───────────
// 1. Entrada horizontal
var _dir = keyboard_check(vk_right) - keyboard_check(vk_left);
vel_x = _dir * vel_correr;

// 2. Gravedad
vel_y += gravedad;
vel_y = min(vel_y, 12);        // terminal velocity

// 3. ¿Estoy en el suelo?
en_suelo = place_meeting(x, y + 1, [obj_suelo, tilemap_suelo]);

if (en_suelo)
{
    coyote = COYOTE_MAX;
}
else
{
    coyote--;
}

// 4. Salto (con coyote time)
if (keyboard_check_pressed(vk_space) && coyote > 0)
{
    vel_y = vel_salto;
    coyote = 0;
}

// 5. Salto variable: sueltas antes = salto más corto
if (!keyboard_check(vk_space) && vel_y < 0)
{
    vel_y *= 0.6;
}

// 6. Mover y colisionar
//    max_y_move evita el bug de "acelerar un frame al aterrizar"
var _col = move_and_collide(
    vel_x, vel_y,
    [obj_suelo, tilemap_suelo],
    4,
    0, 0,
    -1,
    abs(vel_x)
);

// 7. Si chocamos verticalmente, anulamos la velocidad Y
if (array_length(_col) > 0 && vel_y != 0)
{
    // Comprobamos si el impacto fue arriba o abajo
    if (vel_y > 0 && place_meeting(x, y + 1, [obj_suelo, tilemap_suelo]))
    {
        vel_y = 0;      // aterrizaje
    }
    else if (vel_y < 0)
    {
        vel_y = 0;      // techo
    }
}

// 8. Sprite según estado
if (!en_suelo)
{
    sprite_index = (vel_y < 0) ? spr_saltando : spr_cayendo;
}
else if (_dir != 0)
{
    sprite_index = spr_corriendo;
    image_xscale = _dir;
}
else
{
    sprite_index = spr_idle;
}
```

### Versión C: movimiento con delta time (independiente del FPS)

```gml
// Step event
var _dt = delta_time / 1000000;   // segundos transcurridos

// velocidad en PÍXELES POR SEGUNDO
var _vel = 180 * _dt;

var _dx = (keyboard_check(vk_right) - keyboard_check(vk_left)) * _vel;
var _dy = (keyboard_check(vk_down)  - keyboard_check(vk_up))   * _vel;

move_and_collide(_dx, _dy, [obj_pared, tilemap_suelo]);
```

---

## 9. Errores típicos

### ❌ Usar el retorno de `instance_place()` como booleano

```gml
if (instance_place(x, y, obj_enemigo)) { ... }   // ❌ Un tilemap con ID 0 daría false

// ✅
var _i = instance_place(x, y, obj_enemigo);
if (_i != noone) { ... }
```

### ❌ No comprobar `noone` antes de `with()`

```gml
with (instance_place(x, y, obj_enemigo)) { vida -= 10; }   // ❌ actúa sobre self si no hay nada

// ✅
var _e = instance_place(x, y, obj_enemigo);
if (_e != noone) { with (_e) { vida -= 10; } }
```

### ❌ Olvidar la máscara de colisión

Si una instancia no tiene sprite (o su sprite tiene la máscara en «nothing»), **no se detecta ninguna colisión**, aunque esté dibujando algo.

### ❌ Colisiones que «no funcionan» con tilemaps

Repasa la checklist:
- ¿El tile set tiene sprite asignado?
- ¿«Disable Source Sprite Export» está **desactivado**?
- ¿El sprite del tile set tiene una máscara de colisión válida?

### ❌ `move_and_collide()` devuelve menos colisiones de las esperadas

Es por diseño: devuelve las que afectaron al movimiento. Usa `instance_place_list()` para tener todas.

### ❌ Creer que la velocidad en diagonal es igual

```gml
// ❌ Vas un 41% más rápido en diagonal
vel_x = _dx * 3;
vel_y = _dy * 3;

// ✅ Normaliza
var _len = point_distance(0, 0, _dx, _dy);
if (_len > 0) { _dx /= _len; _dy /= _len; }
vel_x = _dx * 3;
vel_y = _dy * 3;
```

---

## Resumen

1. **`move_and_collide()`** es la función moderna: sube pendientes, acepta arrays y tilemaps, y devuelve las colisiones.
2. **`place_meeting()`** para «¿puedo ir ahí?»; **`instance_place()`** si necesitas el handle.
3. Los argumentos `obj` aceptan **objetos, instancias, tilemaps, `all`, `other` y arrays que los combinen**.
4. Las **bounding boxes son inclusivas** y sin redondear desde 2022.1. Existe *Collision Compatibility Mode* como parche, no como solución.
5. El solapamiento cuenta **cuando se cubre el centro del píxel** — con excepciones (`collision_point`, `collision_line`, forma contra forma).
6. Existe el **collision space** (`colspace.room` / `ui_view` / `ui_display`): no puedes colisionar entre espacios distintos.
7. Para proyectos serios: **normaliza el vector diagonal** y considera **delta time** si tu juego va a correr en máquinas muy distintas.
8. Las **físicas (fixtures)** son otra bestia: si las activas, usa `physics_test_overlap()` y `physics_raycast()`.
