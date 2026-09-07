# 09 · Instancias, objetos y herencia

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Instances/Instances.htm>
> - <https://manual.gamemaker.io/lts/en/The_Asset_Editors/Object_Properties/Parent_Objects.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Instances/Deactivating_Instances/Deactivating_Instances.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Instances/instance_change.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Instances/instance_id_get.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Asset_Management/Instances/Instance_Variables/collision_space.htm>
> - `gm-cli manual read "instance_create_layer"` / `"instance_create_depth"`
> - Blog oficial de GameMaker, *How to optimise your games in GameMaker* (§8: instancias vs partículas/asset layers)

---

## 1. Objeto vs instancia: la distinción fundacional

> **Un objeto es el plano. Una instancia es la casa construida.**

| | Objeto | Instancia |
|---|---|---|
| Dónde vive | En el **Asset Browser** | En una **room** |
| Cuántos hay | Uno (el asset) | Muchos |
| Se coloca en la room | ❌ No | ✅ Sí |
| Tiene variables propias | ❌ (solo *Object Variables* por defecto) | ✅ Sí |
| Tiene eventos | ✅ Define cuáles | ✅ Los ejecuta |
| Se destruye | ❌ | ✅ |

> ⚠️ **«Objetos e instancias no son lo mismo y cada uno tiene su propio conjunto de funciones.»**

```gml
obj_enemigo               // el OBJETO (asset) — un handle
instance_create_layer(...) // devuelve la INSTANCIA — otro handle
```

### Las Object Variables NO son variables del objeto

Merece repetirlo (ya apareció en los temas 01 y 04):

> Las *Object Variables* del editor **no** pertenecen al objeto. Son **valores por defecto** que se asignan a las instancias creadas desde ese objeto **antes** de que corra el Create.

---

## 2. Crear instancias

Cuatro formas:

### A. Arrastrando al Room Editor
Para contenido estático de nivel.

### B. En runtime (lo normal)

```gml
instance_create_layer(x, y, capa, obj, [var_struct])
instance_create_depth(x, y, depth, obj, [var_struct])
```

| Argumento | Tipo | Descripción |
|---|---|---|
| `x`, `y` | Real | Posición |
| `capa` | Layer o String | Handle de capa **o su nombre como string** (p. ej. `"Instances"`) |
| `depth` | Real | Profundidad. **Menor = más cerca de la cámara** |
| `obj` | Object Asset | El objeto a instanciar |
| `var_struct` | Struct (**opcional**) | Variables a asignar a la instancia nueva |

**Devuelven:** el handle (`id`) de la nueva instancia.

> ⚠️ **Ambas llaman al Create Event de la instancia antes de continuar** con el código del evento que las llamó.

```gml
var _bala = instance_create_layer(x, y, "Instances", obj_bala);
with (_bala)
{
    speed     = other.velocidad_disparo;
    direction = other.image_angle;
}
```

#### ⚠️ La diferencia oculta de `instance_create_depth()`

Crea una **capa gestionada automáticamente** por GameMaker (porque todas las instancias tienen que estar en una capa). Consecuencias:

- **No puedes acceder a esa capa.**
- La variable `layer` de la instancia contendrá un **handle inválido (-1)**.

```gml
var _i = instance_create_depth(100, 100, -100, obj_enemigo);
show_debug_message(_i.layer);   // -1  ← capa gestionada, inaccesible
```

> 💡 **Por eso se recomienda `instance_create_layer()`**: mantienes el control de las capas, que es lo que estructura el dibujado.

#### El argumento `var_struct` (muy útil)

Te permite inicializar variables sin necesidad de un `with()` posterior. Las variables se asignan **antes** del Create:

```gml
var _bala = instance_create_layer(x, y, "Instances", obj_bala,
{
    velocidad : 12,
    dano      : 25,
    owner     : id,
    direccion : image_angle
});
```

En el Create de `obj_bala`:

```gml
// Estas variables YA existen porque vinieron en var_struct
// Pero conviene tener valores por defecto por si creas la instancia sin struct
velocidad = variable_instance_exists(id, "velocidad") ? velocidad : 8;
dano      = variable_instance_exists(id, "dano")      ? dano      : 10;
```

### C. Añadirla a una Sequence

Se crea en el Sequence Editor y se coloca en la room (por editor o por código).

### D. Añadirla a OTRA room

```gml
room_instance_add(room, x, y, obj);
```

> ⚠️ Las funciones de **modificar rooms** nunca deben ejecutarse desde dentro de la room que quieres cambiar. Ejecútalas desde otra room.
> ⚠️ Los cambios hechos así son **permanentes** durante toda la ejecución del juego, incluso si llamas a `room_restart()`. Solo cerrar y reabrir el juego los resetea.

---

## 3. ID vs handle de instancia

### La confusión típica

Durante años, el `id` de una instancia era un número (`100001`, `100002`…). Ahora es un **handle**.

```gml
var _e = instance_create_layer(0, 0, "Instances", obj_enemigo);

show_debug_message(typeof(_e));   // "ref"
show_debug_message(_e);           // ref instance 100234
show_debug_message(is_handle(_e));// 1
```

### La regla de comparación

> El valor inválido para un handle de instancia es **`noone`** (que vale `-4`).

```gml
if (_e != noone) { /* la instancia existe */ }
```

> ⚠️ **Nunca uses `if (_e)`, `if (_e > 0)` ni `if (_e != 0)`.** Compara siempre contra `noone`.

### `id` vs `object_index` vs `self`

| Expresión | Qué es |
|---|---|
| `id` | El handle **único** de esta instancia concreta |
| `object_index` | El handle del **objeto** (asset) del que viene |
| `self` | La instancia que ejecuta el código actual |
| `other` | La instancia/struct que ejecutó el `with()` |

```gml
show_debug_message($"Soy la instancia {id} del objeto {object_get_name(object_index)}");
```

### Los keywords, en tabla

| Keyword | Valor legacy | Significado |
|---|---|---|
| `self` | -1 | La instancia/struct actual |
| `other` | -2 | Quien invocó el `with()` |
| `all` | -3 | Todas las instancias |
| `noone` | -4 | Ninguna instancia |

> ⚠️ **Nunca uses los números directamente.** Y recuerda la trampa: `with(-1)` **NO se salta**, se ejecuta sobre `self`. Ver **tema 03**.

---

## 4. Destruir instancias

```gml
instance_destroy();           // se destruye a sí misma
instance_destroy(id);         // destruye esa instancia
instance_destroy(obj, ejecutar_eventos);  // todas las de ese objeto
```

> ⚠️ **La instancia no desaparece instantáneamente.** Se ejecutan **Destroy → Clean Up → y luego termina el evento actual**. Si después de `instance_destroy()` tu código usa recursos que limpiaste en Clean Up, tendrás errores.

```gml
// ❌ Peligroso
instance_destroy();
show_debug_message(mi_lista[| 0]);   // si Clean Up destruyó mi_lista → ERROR

// ✅ Añade `exit` o reorganiza
instance_destroy();
exit;
```

---

## 5. `with()` y `other`

`with()` cambia el ámbito de ejecución.

```gml
with (obj_enemigo)
{
    // `self` es CADA enemigo, uno por uno
    vida -= 10;

    // `other` es quien llamó al with()
    other.puntuacion += 5;
}
```

### Lo que acepta

- Un **objeto** (todas sus instancias, **incluidos los hijos**).
- Una **instancia** concreta.
- Un **struct**.
- Los keywords `all`, `other`, `self`, `noone`.

### > ⚠️ Comprueba SIEMPRE el handle

```gml
var _e = instance_nearest(x, y, obj_enemigo);
if (_e != noone)          // ← obligatorio
{
    with (_e) { vida -= 10; }
}
```

### El orden NO está garantizado

Si necesitas orden, recorre tú (ejemplo en el tema 07).

---

## 6. Funciones de instancias

### Generales

| Función | Qué hace |
|---|---|
| `instance_create_layer` / `instance_create_depth` | Crear |
| `instance_destroy` | Destruir |
| `instance_exists(obj)` | ¿Existe alguna? |
| `instance_find(obj, n)` | La enésima instancia (por orden de creación) |
| `instance_number(obj)` | Cuántas hay |
| `instance_nearest(x, y, obj)` | La más cercana |
| `instance_furthest(x, y, obj)` | La más lejana |
| `instance_place` / `instance_place_list` | Colisión por máscara |
| `instance_position` / `instance_position_list` | Colisión por punto |
| `instance_id_get(indice)` | La instancia n del listado global |
| `instance_change` | ⚠️ **DEPRECADA** (ver sección 9) |
| `instance_copy(realizar_eventos)` | Copia la instancia actual |

### Globales

```gml
instance_id      // ARRAY con los handles de TODAS las instancias activas
instance_count   // Cuántas instancias activas hay
```

```gml
// Recorrer TODAS las instancias de la room
for (var i = 0; i < instance_count; i++)
{
    var _id_temp = instance_id_get(i);
    with (_id_temp)
    {
        speed += 0.1;
    }
}
```

> 💡 Para la mayoría de los casos, `with (all)` es más limpio:
> ```gml
> with (all) { speed += 0.1; }
> ```

### Alarmas

```gml
alarm[0..11]       // array integrado
alarm_get(indice)
alarm_set(indice, valor)
```

---

## 7. Herencia de objetos (Parent Objects)

### Qué es

Un objeto puede tener un **padre**. Entonces es un objeto **hijo** y comparte código, acciones y eventos con el padre. Eso es **herencia**.

Se configura con el botón **Parent** en el Object Editor.

### Por qué es tan útil: tres patrones

#### Patrón 1: agrupar para colisiones

Tienes un jugador y **cuatro** objetos enemigo. Sin herencia: cuatro eventos de colisión. **Con herencia: uno.**

```
obj_enemigo (padre, sin código)
 ├── obj_slime
 ├── obj_esqueleto
 ├── obj_caballero
 └── obj_ogro
```

```gml
// Un solo evento de colisión en el jugador: obj_jugador ↔ obj_enemigo
with (other)
{
    instance_destroy();
}
vidas--;
```

> 💡 **El objeto padre no necesita tener eventos ni código.** Puede ser solo una etiqueta.

#### Patrón 2: compartir comportamiento, variar apariencia

Un padre con **toda** la lógica; diez hijos **sin código**, cada uno con su sprite.

```
obj_enemigo_base  (toda la IA)
 ├── obj_enemigo_azul    (sprite azul)
 ├── obj_enemigo_rojo    (sprite rojo)
 └── obj_enemigo_verde   (sprite verde)
```

#### Patrón 3: mezclar y sobreescribir («mix and match»)

Padre con la mayoría de eventos; el hijo redefine **solo** los que cambian.

```
obj_monster (padre: vida, disparo, daño al jugador)
 └── obj_monster_vertical (sobreescribe el evento Step: se mueve arriba/abajo)
```

### Cómo funciona la sobreescritura

- Si el hijo tiene código en un evento, ese código se ejecuta **en lugar del del padre**.
- Si quieres **ambos**, llama a `event_inherited()`.

```gml
// Step del hijo
event_inherited();      // ejecuta el Step del PADRE
// ...y luego el código propio del hijo
```

En el IDE: clic derecho sobre un evento heredado → **Inherit** (te abre el editor con `event_inherited()` ya puesto) u **Override** (sin llamada al padre).

> 💡 Desde el editor de código: clic derecho → **Go To Object** para saltar al padre, o **Open Inherited Event** para ver el código del padre.

### Las funciones también respetan la herencia

Cuando apuntas a un padre, **se incluyen todos sus hijos**:

```gml
instance_number(obj_enemigo);           // cuenta padre + todos los hijos
instance_position(x, y, obj_enemigo);   // busca en padre e hijos
with (obj_enemigo) { ... }              // afecta a padre e hijos
```

### Las variables también

> *«if I set the enemy 1 speed to 10, then the enemy 2 speed will also go to ten as it is a child object of enemy 1.»*

### Jerarquías de varios niveles

Los padres pueden tener padres:

```
obj_entidad          (nivel 1)
 └── obj_personaje   (nivel 2)
      └── obj_jugador (nivel 3)
```

> ⚠️ No puedes crear ciclos (A padre de B, B padre de A).

### Buena práctica

> *«It is generally considered good practice in most cases to create one base parent object and have this base object contain all the default behaviour but never use an instance of it in the game.»*

Es decir: **crea un padre base con el comportamiento por defecto y nunca lo instancies.** Usa solo los hijos, y el padre solo para colisiones, referencias y agrupación.

### Cómo comprobar la herencia en código

```gml
// ¿De qué objeto viene esta instancia?
if (object_get_parent(other.object_index) == obj_enemigo) { ... }

// ¿Es este objeto descendiente de otro?
if (object_is_ancestor(obj_slime, obj_enemigo)) { ... }
```

---

## 8. Cuándo NO usar una instancia

Todo lo anterior en este documento asume que lo que quieres crear necesita ser una instancia:
eventos propios, colisión, un `id` con el que referirte a ella. Pero **no todo lo que aparece en
pantalla necesita eso**, y las fuentes oficiales de GameMaker lo señalan como uno de los errores
de rendimiento más comunes: *"people frequently fall into using objects when they should use
particle systems, data structures, or asset layers instead"* (blog oficial de GameMaker, *How to
optimise your games in GameMaker*). Esta sección compara el coste real de una instancia frente a
sus tres alternativas para elementos **puramente visuales o estáticos**.

### Qué paga una instancia que no pagan sus alternativas

Cada instancia activa, tenga o no código en sus eventos, arrastra:

- **Un `id`** (handle) que el motor mantiene vivo y resoluble mientras la instancia exista.
- **Entrada en las listas de colisión** de su objeto — aunque el evento Collision esté vacío o
  no exista, la instancia sigue teniendo bounding box/máscara calculada
  ([`01 · 08 §4`](./08%20-%20Movimiento%20y%20colisiones.md#4-elegir-la-forma-de-la-máscara)).
- **Paso por Step y Draw** del motor en cada frame, aunque tus propios eventos estén vacíos —
  hay un coste de comprobación por instancia antes de decidir que no hay nada que ejecutar.
- **Sus propias variables de instancia** (`x`, `y`, `image_index`, `depth`…), reservadas por
  instancia, no compartidas.

Ninguna de las tres alternativas de abajo carga con **todo** eso: cada una recorta justo la
parte que un elemento decorativo o estático no necesita.

### Alternativa 1 — Sistema de partículas nativo (efecto visual, sin colisión, vive y muere solo)

Cuando lo único que hace el "objeto" es aparecer, animarse y desaparecer —chispas, humo, hojas
cayendo, un destello de impacto— un sistema de partículas nativo (`part_system_create_layer()`,
`part_type_create()`, `part_emitter_create()`, todas verificadas y ya desarrolladas con recetas
completas en
[`04 · 39 — VFX, diseño y catálogo de efectos`](../04%20-%20Recetas%20por%20género/39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md);
no se repite el catálogo aquí) resuelve lo mismo sin crear ni una sola instancia:

```gml
// ❌ Una instancia por chispa: cada una con id, colisión y sus propios eventos
for (var _i = 0; _i < 20; _i++)
{
    instance_create_layer(x, y, "Effects", obj_chispa);
}

// ✅ Un sistema de partículas: cientos de "chispas" sin ninguna instancia
var _ps = part_system_create_layer("Effects", true);
var _pt = part_type_create();
part_type_sprite(_pt, spr_chispa, false, false, false);
part_type_life(_pt, 15, 30);
part_type_speed(_pt, 1, 3, 0, 0);
part_particles_create(_ps, x, y, _pt, 20);   // las 20 "chispas" de golpe
```

El sistema de partículas gestiona internamente el equivalente a miles de "instancias" con una
estructura de datos contigua, no con el aparato completo de instancia de GameMaker — es el mismo
principio de Data Locality que mide
[`13 · 23 §3.4`](../13%20-%20Diseño%20y%20producción%20de%20videojuegos/23%20-%20Catálogo%20de%20patrones%20en%20GML.md#34-data-locality-—-medido-no-folclore),
aplicado por el propio motor. A cambio, **pierdes** colisión, eventos individuales y control fino
por partícula — si necesitas que una "chispa" concreta reaccione a algo, no es candidata a
partícula.

### Alternativa 2 — Asset layer (decoración estática que nunca cambia)

Un árbol de fondo, un cartel, un charco decorativo: si **nunca** se mueve, no colisiona y no
tiene lógica propia, no hace falta ni una instancia ni un sistema de partículas — es un
**elemento de capa**, colocado con `layer_sprite_create()` o directamente desde el editor de
rooms como *Asset Layer*.

```gml
// ❌ Una instancia solo para que un sprite se quede quieto en un sitio
instance_create_layer(400, 220, "Decoracion", obj_arbol_decorativo);
// obj_arbol_decorativo no tiene ni un evento con código: pura decoración

// ✅ Elemento de asset layer: mismo resultado visual, cero instancias
layer_sprite_create("Decoracion", 400, 220, spr_arbol);
```

Esto es exactamente lo que la propia biblioteca ya recomienda para fondos con scroll
(`layer_background_create()`, cubierto en
[`01 · 10 §3`](./10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md#3-capas-layers)) y para
elementos colocados desde el editor: si lo arrastraste al Room Editor como *Asset Layer* en vez
de como instancia, GameMaker ya no le da ninguna de las cargas de la lista de arriba.

### Alternativa 3 — Tile/tilemap (elementos repetitivos de nivel)

Paredes, suelos, decoración que se repite en rejilla: un **tile** no es una instancia ni un
asset layer suelto — es una celda dentro de un `tilemap`, la estructura más barata de las tres
para elementos repetitivos. Ya cubierto en detalle (`tilemap_set`, colisión con tile maps,
capas de tile) en
[`01 · 10 §4`](./10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md#4-tile-maps-y-tile-sets);
la regla de esta sección es simplemente **cuál elegir primero**:

```gml
// ❌ 200 instancias de obj_pared, una por celda de un muro de piedra
// ✅ Un tilemap de 200 celdas con el mismo sprite de piedra, sin ninguna instancia
```

### Tabla de decisión

| Necesito… | Uso… |
|---|---|
| Colisión, `id`, eventos propios, algo que reacciona | **Instancia** |
| Un efecto visual que nace, se anima y muere solo, sin colisión | **Sistema de partículas** (`part_system_create_layer`) — [`04 · 39`](../04%20-%20Recetas%20por%20género/39%20-%20VFX%20-%20diseño%20y%20catálogo%20de%20efectos.md) |
| Decoración estática que nunca se mueve ni colisiona | **Asset layer** (`layer_sprite_create`/`layer_background_create`) — [`01 · 10 §3`](./10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md#3-capas-layers) |
| Elementos repetitivos de nivel en rejilla (suelo, paredes) | **Tilemap** — [`01 · 10 §4`](./10%20-%20Rooms,%20capas,%20cámaras%20y%20viewports.md#4-tile-maps-y-tile-sets) |
| Sí necesito instancia, pero crear/destruir muchas es el cuello de botella | **Object Pool** — [`06/scr_pool.gml`](../06%20-%20Assets%20y%20Scripts/scr_pool.gml), reutiliza en vez de crear/destruir |

> 💡 **La pregunta que decide todo:** ¿esta "cosa" necesita reaccionar a algo (colisión, input,
> su propio Step) en algún momento de su vida? Si la respuesta es no, no es una instancia — es
> una de las otras tres. Si la respuesta es sí pero crear/destruirla muchas veces por partida
> pesa, sigue siendo instancia, pero pooleada (`06/scr_pool.gml`).

Símbolos verificados con `python3 _indice/buscar.py`: `part_system_create_layer`,
`part_type_create`, `part_emitter_create`, `part_type_sprite`, `part_type_life`,
`part_type_speed`, `part_particles_create`, `layer_sprite_create`, `layer_background_create`.

---

## 9. Activar y desactivar instancias

**Desactivar** una instancia significa que **deja de procesar ninguno de sus eventos**, aunque sigue existiendo en el juego.

### ⚠️ Advertencias críticas

1. **Una instancia desactivada no se puede manipular** de ninguna forma hasta que se reactive. Técnicamente deja de existir salvo como puntero en el proceso de desactivación.
2. ⚠️ **Una instancia persistente desactivada NO se mueve a la siguiente room** salvo que la reactives antes. Efectivamente, se borra del juego.
3. ⚠️ **La activación/desactivación NO es instantánea.** No se considera activa/inactiva hasta el **final del evento** en que se llamó la función.
4. ⚠️ **No uses estas funciones en eventos de dibujado**: puede causar comportamientos inesperados.
5. ⚠️ **No las uses todos los steps**: puede causar problemas de rendimiento. Mejor en una alarma cada pocos steps, o cuando la cámara cambie de posición.
6. ⚠️ Si desactivas en el *room start* (Room Creation Code o Create de una instancia), **todas las instancias del Room Editor seguirán ejecutando su Create** antes de desactivarse.
7. ⚠️ **Desactivar una instancia con físicas NO detiene sus fixtures.** Usa `phy_active = false`.

### Cómo acceder a una instancia desactivada

**No** puedes usar `with()`. Solo acceso directo por su ID:

```gml
valor = inst.variable;   // ✅ única forma
```

### Funciones

```
instance_deactivate_all(activar_padres_objetos)
instance_deactivate_object(obj)
instance_deactivate_region(left, top, width, height, inside, activar_padres)
instance_deactivate_layer(capa)

instance_activate_all()
instance_activate_object(obj)
instance_activate_region(left, top, width, height, inside)
instance_activate_layer(capa)
```

### 🆕 El argumento de «collision space» (2024.14+)

**Por defecto, las funciones de activación/desactivación solo afectan a instancias del mismo espacio de colisión que la instancia que llama.**

```gml
// Solo activa las de MI espacio
instance_activate_all();

// Activa explícitamente las del espacio de la room
instance_activate_all(colspace.room);

// Activa las de una capa UI de viewport
instance_activate_all(colspace.ui_view);
```

Valores:

| Constante | Significado |
|---|---|
| `colspace.room` | No está en capas UI |
| `colspace.ui_view` | Capa UI con «Game View» = Viewports |
| `colspace.ui_display` | Capa UI con «Game View» = Display |

```gml
// Ejemplo típico: activar enemigos solo cerca de la cámara
instance_deactivate_all(colspace.room);

var _cam = view_camera[0];
var _vx = camera_get_view_x(_cam);
var _vy = camera_get_view_y(_cam);
var _vw = camera_get_view_width(_cam);
var _vh = camera_get_view_height(_cam);

var _margen = 128;
instance_activate_region(
    _vx - _margen, _vy - _margen,
    _vw + _margen * 2, _vh + _margen * 2,
    true
);
```

> 💡 Este es el **patrón de optimización clásico**: desactivas todo lo que está fuera de cámara y reactivas solo lo visible. Ponlo en una alarma que se dispare cada 10-15 steps, **no** en el Step.

---

## 10. ⚠️ `instance_change()` está DEPRECADA

> **WARNING** *«Starting with GameMaker 2024.14, this function is deprecated and can only be used if "Allow instance_change" under Deprecated Behaviours is enabled. It is recommended to instead use `instance_destroy()` and `instance_create_layer()` (or `instance_create_depth()`) to replace an existing instance with an instance of a new object.»*

### Qué hacía

```gml
instance_change(obj, realizar_eventos)
```

Cambiaba una instancia por otra de un objeto distinto, decidiendo si ejecutar los eventos Destroy/Clean Up de la original y el Create de la nueva.

| Argumento | Descripción |
|---|---|
| `obj` | El objeto al que cambiar |
| `perf` | `true` = ejecuta Destroy/Clean Up y Create; `false` = los omite (mantiene las propiedades) |

### ⚠️ Problemas que tenía

1. **No puedes hacer nada más con esa instancia hasta el siguiente step.** Acceder a sus variables (por ejemplo `obj_Cambiado.x`) no funciona.
2. **No transfiere las propiedades físicas** a la nueva instancia.
3. Está **deprecada desde 2024.14**: solo funciona si activas «Allow instance_change» en las Game Options, sección *Deprecated Behaviours*.

### ✅ El reemplazo recomendado

```gml
// ───────── ANTES ─────────
if (keyboard_check(vk_enter))
{
    instance_change(obj_jugador_nadando, false);
    exit;
}
```

```gml
// ───────── DESPUÉS ─────────
if (keyboard_check(vk_enter))
{
    // 1. Capturamos el estado que queremos conservar
    var _estado =
    {
        x          : x,
        y          : y,
        layer_id   : layer,
        vida       : vida,
        inventario : inventario
    };

    // 2. Destruimos la instancia actual
    instance_destroy();

    // 3. Creamos la nueva en la MISMA capa, pasándole el estado
    var _nuevo = instance_create_layer(_estado.x, _estado.y,
                                        _estado.layer_id,
                                        obj_jugador_nadando,
                                        _estado);

    // 4. Si algo más necesitaba la referencia, la devolvemos
    return _nuevo;
}
```

Ventajas: control total, funciona con físicas (si transfieres lo que necesites), y no depende de un comportamiento deprecado.

---

## 11. `instance_copy()`

Copia la instancia que ejecuta el código, devolviendo el handle de la nueva.

```gml
instance_copy(realizar_eventos);
```

```gml
// Create de la copia: ejecuta el Create o no
var _clon = instance_copy(true);
with (_clon)
{
    x += 48;
    image_blend = c_red;
}
```

---

## 12. Instancias persistentes

```gml
persistent = true;
```

La instancia **sobrevive al cambio de room**. Ideal para el jugador, el HUD o el controlador de juego.

⚠️ **Cuidado con:**
- **Duplicados:** si colocas el objeto en varias rooms, se acumulan las instancias. Solución: créalo una sola vez en la primera room y que sea persistente.
- **Desactivación:** una instancia persistente desactivada **no pasa** a la siguiente room.
- **Room Start:** se ejecuta también para las persistentes.

```gml
// Create de obj_game (persistente) — patrón singleton
if (instance_number(obj_game) > 1)
{
    instance_destroy();   // ya existía: me destruyo
    exit;
}

persistent = true;
global.puntuacion = 0;
```

---

## 13. Ejemplo completo: sistema de enemigos con herencia

```
obj_entidad          (padre base: nunca se instancia)
 └── obj_enemigo     (padre: IA común)
      ├── obj_slime
      ├── obj_murcielago
      └── obj_jefe
```

```gml
// ═══════════ obj_entidad (Create) — PADRE BASE ═══════════
vida_max = 1;
vida     = 1;
muerto   = false;

function recibir_danio(_cantidad)
{
    vida -= _cantidad;
    if (vida <= 0)
    {
        vida   = 0;
        muerto = true;
        al_morir();
    }
}

function al_morir()
{
    instance_destroy();
}

// ═══════════ obj_enemigo (Create) — HIJO ═══════════
event_inherited();              // hereda vida, recibir_danio, al_morir

vida_max   = 30;
vida       = vida_max;
danio      = 5;
velocidad  = 1.5;
objetivo   = noone;
rango      = 200;

// ═══════════ obj_enemigo (Step) ═══════════
// Buscar al jugador si está a rango
objetivo = instance_nearest(x, y, obj_jugador);

if (objetivo != noone)
{
    var _dist = point_distance(x, y, objetivo.x, objetivo.y);

    if (_dist <= rango)
    {
        // Perseguir
        var _dir = point_direction(x, y, objetivo.x, objetivo.y);
        var _dx  = lengthdir_x(velocidad, _dir);
        var _dy  = lengthdir_y(velocidad, _dir);

        move_and_collide(_dx, _dy, [obj_pared, tilemap_suelo]);

        // Atacar al contacto
        if (_dist < 24)
        {
            objetivo.recibir_danio(danio);
        }
    }
}

// ═══════════ obj_jefe (Create) — NIETO ═══════════
event_inherited();              // hereda de obj_enemigo

vida_max  = 300;
vida      = vida_max;
danio     = 25;
velocidad = 0.8;
rango     = 400;

// ═══════════ obj_jefe (Step) — sobreescribe el del padre ═══════════
// No llamamos a event_inherited(): comportamiento completamente distinto
objetivo = instance_nearest(x, y, obj_jugador);

if (objetivo != noone)
{
    // El jefe carga en lugar de perseguir suavemente
    if (point_distance(x, y, objetivo.x, objetivo.y) > 80)
    {
        move_towards_point(objetivo.x, objetivo.y, velocidad * 2);
    }
    else
    {
        speed = 0;
        // ...lógica de ataque especial...
    }
}

// ═══════════ obj_jefe (al_morir sobreescrito) ═══════════
// Necesitamos el efecto del padre Y el nuestro
// (como es una función, no un evento, la llamamos explícitamente)
```

```gml
// ═══════════ En el jugador: UNA sola colisión con el PADRE ═══════════
// Evento de colisión: obj_jugador ↔ obj_enemigo
// Se dispara para obj_slime, obj_murcielago Y obj_jefe (todos son hijos)

if (invulnerable <= 0)
{
    recibir_danio(other.danio);
    invulnerable = 30;

    // Empujón
    var _dir = point_direction(other.x, other.y, x, y);
    move_and_collide(lengthdir_x(8, _dir), lengthdir_y(8, _dir), obj_pared);
}

// ═══════════ Y en cualquier sitio: contar TODOS los enemigos ═══════════
var _total = instance_number(obj_enemigo);   // incluye slime, murciélago y jefe
show_debug_message($"Quedan {_total} enemigos");
```

**Por qué funciona:** gracias a la herencia, **un solo evento de colisión** cubre los tres tipos de enemigo, y `instance_number(obj_enemigo)` los cuenta todos sin enumerarlos.

---

## Resumen

1. **Objeto = plano; instancia = cosa viva en la room.**
2. `instance_create_layer()` es preferible a `instance_create_depth()`: la de depth crea una capa gestionada **inaccesible** (`layer == -1`).
3. El `id` de una instancia es un **handle**. Compáralo contra **`noone`**, nunca contra `0`.
4. `instance_destroy()` no elimina al instante: **Destroy → Clean Up → termina el evento**. Cuidado con el código posterior.
5. **La herencia de objetos** te da agrupación para colisiones, compartición de comportamiento y sobreescritura selectiva con `event_inherited()`.
6. **Crea un padre base y nunca lo instancies**: úsalo solo como etiqueta.
7. **Si no necesita colisión, `id` ni eventos propios, no es una instancia**: un efecto visual que nace y muere solo es un sistema de partículas, decoración estática es un asset layer, y elementos repetitivos de nivel son un tilemap.
8. **Desactivar** instancias es una gran optimización, pero hazlo en una alarma, no en el Step, y recuerda el argumento de **collision space**.
9. ⚠️ **`instance_change()` está deprecada desde 2024.14.** Usa `instance_destroy()` + `instance_create_layer()` pasando un struct con el estado.
