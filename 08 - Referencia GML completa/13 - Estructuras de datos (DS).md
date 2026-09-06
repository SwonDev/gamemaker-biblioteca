# 13 · Estructuras de datos (DS) en GML

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23).

> Todas las firmas han sido verificadas contra el manual oficial LTS.

---

## ⚠ Advertencia importante de 2026

El propio manual de GameMaker lo dice textualmente:

> «Se recomienda usar **arrays** y **structs** en lugar de las DS lists y los DS maps,
> porque ya tienen una funcionalidad similar, son más fáciles de usar y se recolectan
> automáticamente.»

Las estructuras DS siguen siendo perfectamente válidas y están completamente soportadas,
pero en **código nuevo** la recomendación es:

| Necesitas… | Usa en 2026 | En lugar de |
| --- | --- | --- |
| Una secuencia ordenada | **Array** (`array_push`, `array_sort`…) | `ds_list` |
| Pares clave → valor | **Struct** (`{clave: valor}`) | `ds_map` |
| Una rejilla 2D | **Array de arrays** | `ds_grid` |
| Una pila | **Array** con `array_push` / `array_pop` | `ds_stack` |
| Una cola | **Array** con `array_push` / `array_shift` | `ds_queue` |
| Una cola con prioridad | Array + `array_sort` | `ds_priority` |

### Los tres puntos críticos de las DS

1. **Hay que destruirlas a mano.** El recolector de basura de GameMaker **no** libera las
   estructuras DS. Si no llamas a `ds_*_destroy`, tu juego acabará consumiendo memoria
   hasta ralentizarse y cerrarse.
2. **Usa enteros como índices.** Todos los índices no enteros se truncan con `floor`.
3. **Tras destruirlas, pon la variable a `-1`** para no usar un id inválido.

```gml
// Create
inventario = ds_list_create();

// ... usar la lista ...

// Cleanup (¡imprescindible!)
if (ds_exists(inventario, ds_type_list))
{
    ds_list_destroy(inventario);
    inventario = -1;
}
```

> En objetos, el evento **Clean Up** es el sitio adecuado para destruir las DS, porque se
> ejecuta también cuando la instancia se elimina por `instance_destroy()` o al cambiar de
> room.

---

## Accessors (accesos directos)

GameMaker ofrece una sintaxis abreviada para leer y escribir en las DS sin llamar a
funciones. Se llaman **accessors** y son mucho más legibles:

| Estructura | Accessor | Ejemplo de lectura | Equivale a |
| --- | --- | --- | --- |
| DS list | `\|` | `valor = lista[\| 3]` | `ds_list_find_value(lista, 3)` |
| DS map | `?` | `valor = mapa[? "vidas"]` | `ds_map_find_value(mapa, "vidas")` |
| DS grid | `#` | `v = grid[# 2, 5]` | `ds_grid_get(grid, 2, 5)` |

```gml
// Escribir y leer con accessors
inventario[| 0] = "espada";
vidas = datos[? "vidas"];
grid[# 3, 4] = 1;
```

> **Nota:** las DS **stacks**, **queues** y **priority queues** **no tienen accessor**.
> Para ellas hay que usar siempre las funciones.

---

## Funciones generales de DS


### `ds_exists(ind, type)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si existe una estructura de datos del tipo indicado (`ds_type_list`, `ds_type_map`, `ds_type_grid`, `ds_type_stack`, `ds_type_queue`, `ds_type_priority`) con ese id.
- **Ejemplo:**

```gml
if (!ds_exists(ai_grid, ds_type_grid))
{
    ai_grid = ds_grid_create(room_width / 32, room_height / 32);
}
```

- **Notas:** Muy útil para comprobar si un id sigue siendo válido antes de usarlo tras destruir la estructura.

### `ds_set_precision(prec)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Ajusta la precisión con la que se comparan los valores al ordenar o buscar en estructuras de datos. Por defecto el épsilon es `0.0000001`; súbelo si los resultados de `ds_list_sort` o `ds_grid_sort` te dan sorpresas por errores de redondeo.
- **Ejemplo:**

```gml
ds_set_precision(0.0001);
```

- **Notas:** Afecta a la comparación interna de valores, no a cómo se guardan.

---

## DS Lists — listas


### `ds_list_create()`

- **Devuelve:** DS List
- **Qué hace:** Crea una lista DS vacía y devuelve su **id** (un entero). Ese id es el que usarás en todas las demás funciones de la lista.
- **Ejemplo:**

```gml
list = ds_list_create();
```

### `ds_list_destroy(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Destruye la lista y **libera su memoria**. Es obligatorio llamarla cuando ya no la necesites, porque las DS **no** las recolecta el recolector de basura.
- **Ejemplo:**

```gml
if (lives == 0)
{
    ds_list_destroy(AI_list);
    AI_list = -1;
    room_goto(rm_Menu);
}
```

### `ds_list_clear(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Vacía la lista por completo. La lista sigue existiendo, pero con tamaño 0.
- **Ejemplo:**

```gml
if (count == 15) && (!ds_list_empty(command_list))
{
    ds_list_clear(command_list);
    alarm[0] = game_get_speed(gamespeed_fps);
    ai_count = 0;
}
```

### `ds_list_empty(id)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la lista está vacía (tamaño 0).
- **Ejemplo:**

```gml
if (count == 15 && !ds_list_empty(command_list))
{
    ds_list_clear(command_list);
    alarm[0] = game_get_speed(gamespeed_fps);
    count = 0;
}
```

### `ds_list_size(id)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el número de elementos de la lista.
- **Ejemplo:**

```gml
if (!ds_list_empty(control_list))
{
    num = ds_list_size(control_list);
}
```

### `ds_list_add(id, val1 [, val2, ... max_val])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Añade uno o más valores al **final** de la lista. Devuelve el nuevo tamaño.
- **Ejemplo:**

```gml
ds_list_add(sc_list, score);
```

### `ds_list_set(id, pos, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Reemplaza el valor que ocupa la posición indicada. Las posiciones empiezan en **0**.
- **Ejemplo:**

```gml
list = ds_list_create();

ds_list_add(list, 71, 77, 46);

ds_list_set(list, 2, 33);
```

### `ds_list_insert(id, pos, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Inserta un valor en la posición indicada, desplazando los elementos siguientes hacia el final.
- **Ejemplo:**

```gml
ds_list_insert(list, 9, score);
```

### `ds_list_replace(id, pos, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Reemplaza el valor de la posición indicada. A diferencia de `ds_list_set`, devuelve `true` o `false` según se haya podido hacer.
- **Ejemplo:**

```gml
ds_list_replace(n_list, 3, name);
```

### `ds_list_delete(id, pos)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Elimina el elemento que ocupa la posición indicada y **reindexa** los siguientes. Las posiciones empiezan en 0.
- **Ejemplo:**

```gml
if (ds_list_size(sc_list) > 10)
{
    while (ds_list_size(sc_list) > 10)
    {
        ds_list_delete(sc_list, 0);
    }
}
```

- **Notas:** Al eliminar, los elementos posteriores se desplazan: los índices cambian.

### `ds_list_find_index(id, val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la posición de la **primera** aparición del valor, o `-1` si no está. Las posiciones empiezan en 0.
- **Ejemplo:**

```gml
pos = ds_list_find_index(list, "Player1");
```

- **Notas:** Devuelve `-1` si no encuentra el valor, no `undefined`.

### `ds_list_find_value(id, pos)`

- **Devuelve:** Cualquiera or undefined
- **Qué hace:** Devuelve el valor que ocupa la posición indicada, o `undefined` si la posición no existe. Equivale al acceso con `|`.
- **Ejemplo:**

```gml
val = ds_list_find_value(list, ds_list_size(list) - 1);
```

- **Notas:** Devuelve `undefined` si la posición no existe.

### `ds_list_shuffle(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Mezcla aleatoriamente el orden de los elementos de la lista.
- **Ejemplo:**

```gml
if (restart)
{
    ds_list_shuffle(card_list);
}
```

### `ds_list_sort(id, ascend)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Ordena la lista de forma **ascendente** (`true`) o descendente (`false`). Los valores se ordenan como números o como strings según su tipo.
- **Ejemplo:**

```gml
if (newgame)
{
    ds_list_sort(name_list, true);
}
```

- **Notas:** Ordena comparando como números si puede; si los valores son strings, los ordena alfabéticamente.

### `ds_list_copy(destination, source)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia el contenido de la lista de origen en la lista de destino, sobrescribiendo lo que hubiera.
- **Ejemplo:**

```gml
if (!ds_list_empty(main_list))
{
    old_list = ds_list_create();
    ds_list_copy(old_list, main_list);
    ds_list_clear(main_list);
}
```

### `ds_list_read(id, str [, legacy])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Carga el contenido de la lista desde un string previamente generado con `ds_list_write`. Devuelve `true` si ha funcionado.
- **Ejemplo:**

```gml
list = ds_list_create();
ini_open("save.ini");
var str = ini_read_string("Lists", "0", "");
if (str != "")
{
    ds_list_read(list, str);
}
ini_close();
```

### `ds_list_write(id)`

- **Devuelve:** String
- **Qué hace:** Serializa la lista a un **string** que puedes guardar en disco. Se usa junto con `ds_list_read`.
- **Ejemplo:**

```gml
ini_open("save.ini");
var str = ds_list_write(list);
ini_write_string("Lists", "0", str);
ds_list_clear(list);
ini_close();
```

### `ds_list_mark_as_list(id, pos)`

- **Devuelve:** DS List or -1 (if it fails)
- **Qué hace:** Marca la posición indicada como contenedora de **otra lista**, para que se destruya automáticamente con la lista padre y se codifique bien en JSON.
- **Ejemplo:**

```gml
var j_list = ds_list_create();

var sub_list = ds_list_create();

ds_list_add(sub_list, health);

ds_list_add(sub_list, lives);

ds_list_add(sub_list, score);

ds_list_add(j_list, sub_list);

ds_list_mark_as_list(j_list, 0);
```

### `ds_list_mark_as_map(id, pos)`

- **Devuelve:** DS Map or -1 (if it fails)
- **Qué hace:** Marca la posición indicada como contenedora de un **mapa**, con los mismos efectos que `ds_list_mark_as_list`.
- **Ejemplo:**

```gml
var sub_map = ds_map_create();

ds_map_add(sub_map, "player", player_array);

ds_map_add(sub_map, "enemy", enemy_array);

ds_list_add(j_list, sub_map);

ds_list_mark_as_map(j_list, 0);
```

### `ds_list_is_list(id, pos)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la posición indicada está marcada como lista.
- **Ejemplo:**

```gml
var size = ds_list_size(ships);
for (var i = 0; i < size; i++)
{
    if (ds_list_is_list(ships, i))
    {
        ds_list_destroy(ships[| i]);
    }
}
ds_list_destroy(ships);
```

### `ds_list_is_map(id, pos)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la posición indicada está marcada como mapa.
- **Ejemplo:**

```gml
var size = ds_list_size(ships);
for (var i = 0; i < size; i++)
{
    if (ds_list_is_map(ships, i))
    {
        ds_map_destroy(ships[| i]);
    }
}
ds_list_destroy(ships);
```

---

## DS Maps — mapas clave → valor


### `ds_map_create()`

- **Devuelve:** DS Map
- **Qué hace:** Crea un mapa DS vacío y devuelve su id. Un mapa guarda pares **clave → valor**.
- **Ejemplo:**

```gml
inventory = ds_map_create();
```

### `ds_map_destroy(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Destruye el mapa y libera su memoria. **Obligatorio** al terminar: los mapas no se recolectan solos.
- **Ejemplo:**

```gml
ds_map_destroy(inventory);
inventory = -1;
```

### `ds_map_clear(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Elimina todos los pares del mapa, dejándolo vacío pero válido.
- **Ejemplo:**

```gml
if (global.new_game)
{
    ds_map_clear(inventory);
}
```

### `ds_map_empty(id)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el mapa está vacío.
- **Ejemplo:**

```gml
if (ds_map_empty(inventory))
{
    weight = 0;
}
```

### `ds_map_size(id)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el número de pares clave → valor del mapa.
- **Ejemplo:**

```gml
if (ds_map_size(inventory) > 49)
{
    full = true;
}
```

### `ds_map_add(id, key, val)`

- **Devuelve:** Booleano
- **Qué hace:** Añade un par clave → valor al mapa. Si la clave ya existe, no la sobrescribe.
- **Ejemplo:**

```gml
inventory = ds_map_create();
ds_map_add(inventory, "hp potion", 1);
ds_map_add(inventory, "gold", 100);
```

- **Notas:** Si la clave ya existe, `ds_map_add` **no** la sobrescribe. Usa `ds_map_set` para eso.

### `ds_map_set(id, key, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Establece el valor de una clave, **creándola si no existe**. Es la forma recomendada de escribir en un mapa.
- **Ejemplo:**

```gml
struct_key = {a: 10, b: "Some text"};


map_key_value_pairs = ds_map_create();

ds_map_set(map_key_value_pairs, "score", "the value belonging to the string key");

ds_map_set(map_key_value_pairs, 8, "The value belonging to the real number key");

ds_map_set(map_key_value_pairs, struct_key, "The value for the struct key");


show_debug_message(map_key_value_pairs[? "score"]);

show_debug_message(map_key_value_pairs[? 8]);

show_debug_message(map_key_value_pairs[? struct_key]);
```

### `ds_map_replace( id, key, val )`

- **Devuelve:** Booleano
- **Qué hace:** Reemplaza el valor de una clave existente. Si la clave no existe, no hace nada.
- **Ejemplo:**

```gml
ds_map_replace(inventory, "torso", 55);
```

### `ds_map_delete(id, key)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Elimina la clave indicada del mapa. Opcionalmente devuelve su valor antes de borrarla.
- **Ejemplo:**

```gml
ds_map_delete(inventory, "shield");
```

### `ds_map_exists(id, key)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el mapa contiene la clave indicada.
- **Ejemplo:**

```gml
if (!ds_map_exists(inventory, "potions"))
{
    ds_map_add(inventory, "potions", 1);
}
```

### `ds_map_find_value(id, key)`

- **Devuelve:** Cualquiera or undefined
- **Qué hace:** Devuelve el valor asociado a la clave, o `undefined` si no existe. Equivale al acceso con `?`.
- **Ejemplo:**

```gml
amount = ds_map_find_value(inventory, "food");
```

```gml
amount = inventory[? "food"];
```

### `ds_map_find_first(id)`

- **Devuelve:** Cualquiera or undefined
- **Qué hace:** Devuelve la **primera** clave del mapa. Sirve para iniciar un recorrido con `ds_map_find_next`.
- **Ejemplo:**

```gml
var size = ds_map_size(inventory) ;
var key = ds_map_find_first(inventory);
for (var i = 0; i < size; i++)
{
    if (key != "gold")
    {
        key = ds_map_find_next(inventory, key);
    }
    else break;
}
```

- **Notas:** El orden de un mapa **no es predecible**: no asumas que coincide con el orden de inserción. Para recorrer de forma fiable usa `ds_map_keys_to_array`.

### `ds_map_find_last(id)`

- **Devuelve:** Cualquiera or undefined
- **Qué hace:** Devuelve la **última** clave del mapa. Sirve para iniciar un recorrido inverso con `ds_map_find_previous`.
- **Ejemplo:**

```gml
var size = ds_map_size(inventory);
var key = ds_map_find_last(inventory);
for (var i = size; i > 0; i--)
{
    if (key != "gold")
    {
        key = ds_map_find_previous(inventory, key);
    }
    else break;
}
```

- **Notas:** El orden de un mapa no es predecible.

### `ds_map_find_next(id, key)`

- **Devuelve:** Cualquiera or undefined
- **Qué hace:** Devuelve la clave **siguiente** a la indicada, o `undefined` si no hay más.
- **Ejemplo:**

```gml
var _size = ds_map_size(inventory);
var _key = ds_map_find_first(inventory);
for (var i = 0; i < _size; i++)
{
    if (_key == "gold")
    {
        break;
    }

    _key = ds_map_find_next(inventory, _key);
}
```

- **Notas:** El orden de un mapa no es predecible; úsalo solo para recorrer todos los pares, no para obtener un orden concreto.

### `ds_map_find_previous(id, key)`

- **Devuelve:** Cualquiera or undefined
- **Qué hace:** Devuelve la clave **anterior** a la indicada, o `undefined` si no hay más.
- **Ejemplo:**

```gml
var _size = ds_map_size(inventory) - 1;
var _key = ds_map_find_last(inventory);
for (var i = _size; i > 0; i--)
{
    if (_key != "gold")
    {
        _key = ds_map_find_previous(inventory, _key);
    }
    else break;
}
```

- **Notas:** El orden de un mapa no es predecible.

### `ds_map_keys_to_array(id, [array])`

- **Devuelve:** Array
- **Qué hace:** Devuelve un **array** con todas las claves del mapa. Es la forma cómoda de recorrerlo en 2026.
- **Ejemplo:**

```gml
map_keys = ds_map_keys_to_array(inventory);
```

- **Notas:** Es la forma moderna y predecible de recorrer un mapa.

### `ds_map_values_to_array(id, [array])`

- **Devuelve:** Array
- **Qué hace:** Devuelve un **array** con todos los valores del mapa.
- **Ejemplo:**

```gml
var _values = ds_map_values_to_array(lvl_score);
var _total = 0;
var _length = array_length(_values);

for (var i = 0; i < _length; i ++)
{
    _total += _values[i];
}

draw_text(32, 32, "Total score for all levels: " + string(_total));
```

### `ds_map_copy(destination, source)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia el contenido del mapa de origen en el de destino.
- **Ejemplo:**

```gml
inventory_2 = ds_map_create();
ds_map_copy(inventory_2, inventory_1);
```

### `ds_map_read(id, str, [legacy])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Carga el mapa desde un string generado con `ds_map_write`. Devuelve `true` si ha funcionado.
- **Ejemplo:**

```gml
inventory = ds_map_create();
ini_open("map.ini");
var _t_string = ini_read_string("Saved", "0", "");
if (_t_string != "")
{
    ds_map_read(inventory, _t_string);
}
ini_close();
```

### `ds_map_write(id)`

- **Devuelve:** String
- **Qué hace:** Serializa el mapa a un string guardable en disco.
- **Ejemplo:**

```gml
ini_open("map.ini");
var _t_string = ds_map_write(inventory);
ini_write_string("Saved", "0", _t_string);
ini_close();
```

### `ds_map_secure_save(map, filename)`

- **Devuelve:** Booleano
- **Qué hace:** Guarda el mapa **ofuscado** en una ubicación segura de la plataforma, en un formato que impide transferir el fichero entre dispositivos.
- **Ejemplo:**

```gml
ds_map_secure_save(purchase_map, "p_data.dat");
```

- **Notas:** El fichero resultante **no se puede transferir entre dispositivos**: es deliberado, para evitar trampas.

### `ds_map_secure_save_buffer(map, buffer)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Guarda el mapa ofuscado dentro del **buffer** indicado.
- **Ejemplo:**

```gml
buff = buffer_create(128, buffer_grow, 4);
var _map = ds_map_create();
ds_map_add(_map, "bob", "ajob");
ds_map_add(_map, "money", 10);
ds_map_secure_save_buffer(_map, buff);
ds_map_destroy(_map);
```

### `ds_map_secure_load(filename)`

- **Devuelve:** DS Map
- **Qué hace:** Carga un mapa guardado con `ds_map_secure_save`. Devuelve el id del mapa, o `undefined` si falla.
- **Ejemplo:**

```gml
p_map = ds_map_secure_load("p_data.dat");
```

- **Notas:** Devuelve `undefined` si el fichero no existe o está corrupto.

### `ds_map_secure_load_buffer(buffer)`

- **Devuelve:** DS Map or -1 in case the data couldn't be read correctly from the buffer
- **Qué hace:** Carga un mapa ofuscado desde un buffer.
- **Ejemplo:**

```gml
var _buff = buffer_load("save.dat");
map = ds_map_secure_load_buffer(_buff);
buffer_delete(_buff);
```

### `ds_map_add_list(id, key, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Añade una **lista DS** como valor de una clave, marcándola para que se destruya con el mapa y se codifique bien en JSON.
- **Ejemplo:**

```gml
var j_list = ds_list_create();

ds_list_add(j_list, health);

ds_list_add(j_list, lives);

ds_list_add(j_list, score);

var j_map = ds_map_create();

ds_map_add_list(j_map, "list", j_list);

var j = json_encode(j_map);

ds_map_destroy(j_map);
```

- **Notas:** Solo tiene sentido para JSON: los mapas y listas anidados **no** se leen correctamente si se escriben a disco de otra forma.

### `ds_map_add_map(id, key, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Añade un **mapa DS** como valor de una clave, con el mismo marcado automático.
- **Ejemplo:**

```gml
var j_map = ds_map_create();

var j_list = ds_list_create();

var sub_map = ds_map_create();

ds_map_add_list(sub_map, "list", j_list);

ds_map_add(sub_map, "array", j_array);

ds_map_add_map(j_map, "map", sub_map);

var j = json_encode(j_map);

ds_map_destroy(j_map);
```

- **Notas:** Solo tiene sentido para JSON.

### `ds_map_replace_list(id, key, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Reemplaza el valor de una clave por una lista DS marcada.
- **Ejemplo:**

```gml
var j_list = ds_list_create();

ds_list_add(j_list, health);

ds_list_add(j_list, lives);

ds_list_add(j_list, score);

ds_map_replace_list(j_map, "list", j_list);

var j = json_encode(j_map);

ds_list_destroy(j_list);
```

### `ds_map_replace_map(id, key, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Reemplaza el valor de una clave por un mapa DS marcado.
- **Ejemplo:**

```gml
var temp_map = ds_map_create();

ds_map_add_list(temp_map, "list", j_list);

ds_map_add(temp_map, "array", j_array);

ds_map_replace_map(j_map, "maps", temp_map);

var j = json_encode(j_map);

ds_map_destroy(temp_map);
```

### `ds_map_is_list(id, key)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el valor de la clave está marcado como lista.
- **Ejemplo:**

```gml
var size = ds_map_size(inventory);
var key = ds_map_find_first(inventory);
for (var i = 0; i < size; i++)
{
    if (ds_map_is_list(inventory, key))
    {
        ds_list_destroy(inventory[? key]);
    }

    key = ds_map_find_next(inventory, key);
}

ds_map_destroy(inventory);
```

### `ds_map_is_map(id, key)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el valor de la clave está marcado como mapa.
- **Ejemplo:**

```gml
var size = ds_map_size(inventory);
var key = ds_map_find_first(inventory);
for (var i = 0; i < size; i++)
{
    if (ds_map_is_map(inventory, key))
    {
        ds_map_destroy(inventory[? key]);
    }
    key = ds_map_find_next(inventory, key);
}
ds_map_destroy(inventory);
```

---

## DS Grids — rejillas 2D


### `ds_grid_create(w, h)`

- **Devuelve:** DS Grid
- **Qué hace:** Crea una grid (rejilla 2D) del ancho y alto indicados y devuelve su id.
- **Ejemplo:**

```gml
mygrid = ds_grid_create(10, 10);
```

### `ds_grid_destroy(index)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Destruye la grid y libera su memoria. **Obligatorio** al terminar.
- **Ejemplo:**

```gml
if (lives == 0)
{
    ds_grid_destroy(Wall_Grid);
    Wall_Grid = -1;
    room_goto(rm_Menu);
}
```

### `ds_grid_width(index)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el ancho (número de columnas) de la grid.
- **Ejemplo:**

```gml
for (var i = 0; i < ds_grid_width(grid); ++i)
{
    for (var j = 0; j < ds_grid_height(grid); ++j)
    {
        if (ds_grid_get(grid, i, j) == 1)
        {
            instance_create_layer(i * 32, j * 32, "Walls", obj_Wall);
        }
    }
}
```

### `ds_grid_height(index)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el alto (número de filas) de la grid.
- **Ejemplo:**

```gml
for (var i = 0; i < ds_grid_width(grid); ++i)
{
    for (var j = 0; j < ds_grid_height(grid); ++j)
    {
        if (ds_grid_get(grid, i, j) == 1)
        {
            instance_create_Layer(i * 32, j * 32, "Walls", obj_Wall);
        }
    }
}
```

### `ds_grid_resize(index, w, h)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Cambia el tamaño de la grid conservando los valores que siguen dentro de los nuevos límites.
- **Ejemplo:**

```gml
ds_grid_resize(global.Grid, room_width / 32, room_height / 32);
ds_grid_clear(global.Grid, -1)
```

### `ds_grid_clear(index, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Pone **todas** las celdas de la grid al valor indicado.
- **Ejemplo:**

```gml
ds_grid_resize(global.Grid, room_width / 32, room_height / 32);
ds_grid_clear(global.Grid, -1)
```

### `ds_grid_set(index, x, y, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Escribe un valor en la celda `(x, y)`. Equivale al acceso con `#`.
- **Ejemplo:**

```gml
grid = ds_grid_create(5, 5);
var i = 0;
var j = 0;

repeat (ds_grid_width(grid))
{
    repeat (ds_grid_height(grid))
    {
        ds_grid_set(grid, i, j, irandom(9));
        j += 1;
    }

    j = 0;
    i += 1;
}
```

### `ds_grid_get(index, x, y)`

- **Devuelve:** Cualquiera
- **Qué hace:** Lee el valor de la celda `(x, y)`. Equivale al acceso con `#`.
- **Ejemplo:**

```gml
var xx = irandom(ds_grid_width(grid) - 1);
var yy = irandom(ds_grid_height(grid) - 1);
val = ds_grid_get(grid, xx, yy)
```

### `ds_grid_set_region(index, x1, y1, x2, y2, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Escribe el mismo valor en una región rectangular de la grid.
- **Ejemplo:**

```gml
ds_grid_set_region(grid, 5, 5, 10, 10, 99);
```

### `ds_grid_set_disk(index, xm, ym, r, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Escribe el mismo valor en las celdas que caen dentro de un **disco** (círculo) de centro y radio dados.
- **Ejemplo:**

```gml
ds_grid_set_disk(grid, ds_grid_width(grid) div 2, ds_grid_height(grid) div 2, 5, -4)
```

### `ds_grid_set_grid_region(index, source, x1, y1, x2, y2, xpos, ypos)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia una región de otra grid dentro de esta, en la posición indicada.
- **Ejemplo:**

```gml
ds_grid_set_grid_region(grid, t_grid, 0, 0, 5, 5, 10, 10)
```

### `ds_grid_add(index, x, y, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Suma un valor a la celda `(x, y)`.
- **Ejemplo:**

```gml
ds_grid_add(grid, 5, 5, 6);
```

### `ds_grid_add_region(index, x1, y1, x2, y2, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Suma un valor a todas las celdas de una región rectangular.
- **Ejemplo:**

```gml
ds_grid_add_region(grid, 2, 4, 5, 5, ".");
```

### `ds_grid_add_disk(index, xm, ym, r, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Suma un valor a todas las celdas dentro de un disco.
- **Ejemplo:**

```gml
ds_grid_add_disk(grid, 7, 6, 5, 2);
```

### `ds_grid_add_grid_region(index, source, x1, y1, x2, y2, xpos, ypos)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Suma, celda a celda, una región de otra grid.
- **Ejemplo:**

```gml
ds_grid_add_grid_region(grid, grid, 0, 0, 1, 5, 2, 0);
```

### `ds_grid_multiply(index, x, y, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Multiplica la celda `(x, y)` por el valor indicado.
- **Ejemplo:**

```gml
ds_grid_multiply(mygrid, 5, 5, 2);
```

### `ds_grid_multiply_region(index, x1, y1, x2, y2, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Multiplica todas las celdas de una región rectangular por un valor.
- **Ejemplo:**

```gml
ds_grid_multiply_region(mygrid, 5, 5, 10, 10, 2);
```

### `ds_grid_multiply_disk(index, xm, ym, r, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Multiplica todas las celdas dentro de un disco por un valor.
- **Ejemplo:**

```gml
ds_grid_multiply_disk(mygrid, 5, 5, 5, 2);
```

### `ds_grid_multiply_grid_region(index, source, x1, y1, x2, y2, xpos, ypos)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Multiplica, celda a celda, por una región de otra grid.
- **Ejemplo:**

```gml
ds_grid_multiply_grid_region(mygrid, mygrid, 0, 0, 5, 5, 0, 0);
```

### `ds_grid_shuffle(index)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Mezcla aleatoriamente el contenido de la grid (o de una región).
- **Ejemplo:**

```gml
ds_grid_shuffle(grid);
```

### `ds_grid_sort(index, column, ascending)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Ordena una columna de la grid y reordena las filas completas con ella.
- **Ejemplo:**

```gml
ds_grid_sort(grid, 3, false);
```

- **Notas:** Ordena por la columna indicada y arrastra las filas completas, como harías en una hoja de cálculo.

### `ds_grid_get_sum(index, x1, y1, x2, y2)`

- **Devuelve:** Real or String
- **Qué hace:** Devuelve la **suma** de los valores de una región rectangular.
- **Ejemplo:**

```gml
val = ds_grid_get_sum(grid, 0, 0, 5, 5)
```

### `ds_grid_get_mean(index, x1, y1, x2, y2)`

- **Devuelve:** Real or String
- **Qué hace:** Devuelve la **media** de los valores de una región rectangular.
- **Ejemplo:**

```gml
val = ds_grid_get_mean(grid, 0, 0, 5, 5)
```

### `ds_grid_get_max(index, x1, y1, x2, y2)`

- **Devuelve:** Real or String
- **Qué hace:** Devuelve el valor **máximo** de una región rectangular.
- **Ejemplo:**

```gml
val = ds_grid_get_max(grid, 0, 0, 5, 5)
```

### `ds_grid_get_min(index, x1, y1, x2, y2)`

- **Devuelve:** Real or String
- **Qué hace:** Devuelve el valor **mínimo** de una región rectangular.
- **Ejemplo:**

```gml
val = ds_grid_get_min(grid, 0, 0, 5, 5)
```

### `ds_grid_get_disk_sum(index, xm, ym, r)`

- **Devuelve:** Real or String
- **Qué hace:** Devuelve la **suma** de los valores dentro de un disco.
- **Ejemplo:**

```gml
val = ds_grid_get_disk_sum(grid, 5, 5, 2)
```

### `ds_grid_get_disk_mean(index, xm, ym, r)`

- **Devuelve:** Real or String
- **Qué hace:** Devuelve la **media** de los valores dentro de un disco.
- **Ejemplo:**

```gml
val = ds_grid_get_disk_mean(grid, 5, 5, 2)
```

### `ds_grid_get_disk_max(index, xm, ym, r)`

- **Devuelve:** Real or String
- **Qué hace:** Devuelve el valor **máximo** dentro de un disco.
- **Ejemplo:**

```gml
val = ds_grid_get_disk_max(grid, 5, 5, 2)
```

### `ds_grid_get_disk_min(index, xm, ym, r)`

- **Devuelve:** Real or String
- **Qué hace:** Devuelve el valor **mínimo** dentro de un disco.
- **Ejemplo:**

```gml
val = ds_grid_get_disk_min(grid, 5, 5, 2)
```

### `ds_grid_value_exists(index, x1, y1, x2, y2, val)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el valor buscado existe en alguna celda de la región indicada.
- **Ejemplo:**

```gml
if (ds_grid_value_exists(grid, 0, 1, 5, 6, val))
{
    xpos = ds_grid_value_x(grid, 0, 1, 5, 6, val);
    ypos = ds_grid_value_y(grid, 0, 1, 5, 6, val);
}
```

### `ds_grid_value_x(index, x1, y1, x2, y2, val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la coordenada **x** de la celda donde aparece el valor buscado.
- **Ejemplo:**

```gml
if (ds_grid_value_exists(grid, 0, 1, 5, 6, val))
{
    xpos = ds_grid_value_x(grid, 0, 1, 5, 6, val);
    ypos = ds_grid_value_y(grid, 0, 1, 5, 6, val);
}
```

### `ds_grid_value_y(index, x1, y1, x2, y2, val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la coordenada **y** de la celda donde aparece el valor buscado.
- **Ejemplo:**

```gml
if (ds_grid_value_exists(grid, 0, 1, 5, 6, val))
{
    xpos = ds_grid_value_x(grid, 0, 1, 5, 6, val);
    ypos = ds_grid_value_y(grid, 0, 1, 5, 6, val);
}
```

### `ds_grid_value_disk_exists(index, xm, ym, r, val)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el valor buscado existe dentro de un disco.
- **Ejemplo:**

```gml
if (ds_grid_value_disk_exists(grid, 5, 5, 5, val))
{
    xpos = ds_grid_value_disk_x(grid, 5, 5, 5, val);
    ypos = ds_grid_value_disk_y(grid, 5, 5, 5, val);
}
```

### `ds_grid_value_disk_x(index, xm, ym, r, val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la coordenada **x** del valor buscado dentro de un disco.
- **Ejemplo:**

```gml
if (ds_grid_value_disk_exists(grid, 5, 5, 5, val))
{
    xpos = ds_grid_value_disk_x(grid, 5, 5, 5, val);
    ypos = ds_grid_value_disk_y(grid, 5, 5, 5, val);
}
```

### `ds_grid_value_disk_y(index, xm, ym, r, val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la coordenada **y** del valor buscado dentro de un disco.
- **Ejemplo:**

```gml
if (ds_grid_value_disk_exists(grid, 5, 5, 5, val))
{
    xpos = ds_grid_value_disk_x(grid, 5, 5, 5, val);
    ypos = ds_grid_value_disk_y(grid, 5, 5, 5, val);
}
```

### `ds_grid_copy(destination, source)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia el contenido de la grid de origen en la de destino.
- **Ejemplo:**

```gml
n_grid = ds_grid_create(1, 1);
ds_grid_copy(n_grid, a_grid);
ds_grid_clear(a_grid, -1)
```

### `ds_grid_read(index, string [, legacy])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Carga la grid desde un string generado con `ds_grid_write`.
- **Ejemplo:**

```gml
grid = ds_grid_create(room_width div 32, room_height div 32);
ini_open("Save.ini");
ds_grid_read(grid, ini_read_string("Save", "0", ""));
ini_close();
```

### `ds_grid_write(index)`

- **Devuelve:** String
- **Qué hace:** Serializa la grid a un string guardable en disco.
- **Ejemplo:**

```gml
ini_open("Save.ini");
ini_write_string("Save", "0", ds_grid_write(mygrid));
ini_close()
```

---

## DS Stacks — pilas (LIFO)


### `ds_stack_create()`

- **Devuelve:** DS Stack
- **Qué hace:** Crea una pila vacía y devuelve su id. Funciona como **LIFO** (lo último que entra es lo primero que sale).
- **Ejemplo:**

```gml
stack = ds_stack_create();
```

### `ds_stack_destroy(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Destruye la pila y libera su memoria. **Obligatorio** al terminar.
- **Ejemplo:**

```gml
if (lives == 0)
{
    ds_stack_destroy(AI_stack);
    AI_stack = -1;
    room_goto(rm_Menu);
}
```

### `ds_stack_clear(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Vacía la pila por completo.
- **Ejemplo:**

```gml
if (ai_count = 15 && !ds_stack_empty(AI_stack))
{
    ds_stack_clear(AI_stack);
    alarm[0] = game_get_speed(gamespeed_fps);
    ai_count = 0;
}
```

### `ds_stack_empty(id)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la pila está vacía.
- **Ejemplo:**

```gml
if (ai_count == 15 && !ds_stack_empty(AI_stack))
{
    ds_stack_clear(AI_stack);
    alarm[0] = game_get_speed(gamespeed_fps);
    ai_count = 0;
}
```

### `ds_stack_size(id)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el número de elementos apilados.
- **Ejemplo:**

```gml
if (!ds_stack_empty(control_stack))
{
    num = ds_stack_size(control_stack);
}
```

### `ds_stack_push(id, val [, val2, ...])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Apila un valor en la cima de la pila.
- **Ejemplo:**

```gml
move_stack = ds_stack_create();

ds_stack_push(move_stack, x, y, x, y + 200, x + 200, y + 200, x + 200, y);
```

### `ds_stack_pop(id)`

- **Devuelve:** Cualquiera (Data type value that is stored in the stack) or undefined
- **Qué hace:** Saca y devuelve el valor de la cima de la pila.
- **Ejemplo:**

```gml
if (!ds_stack_empty(move_stack))
{
    var xx = ds_stack_pop(move_stack);
    var yy = ds_stack_pop(move_stack);
    move_towards_point(xx, yy, 4);
}
```

### `ds_stack_top(id)`

- **Devuelve:** Cualquiera (Data type value that is stored in the stack) or undefined
- **Qué hace:** Devuelve el valor de la cima **sin sacarlo**.
- **Ejemplo:**

```gml
num = ds_stack_top(control_stack);
```

### `ds_stack_copy(destination, source)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia el contenido de la pila de origen en la de destino.
- **Ejemplo:**

```gml
with (instance_create_layer(x, y, "Enemies", obj_Enemy))
{
    stack = ds_stack_create();
    ds_stack_copy(stack, other.stack);
}
```

### `ds_stack_read(id, str [, legacy])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Carga la pila desde un string generado con `ds_stack_write`.
- **Ejemplo:**

```gml
stack = ds_stack_create();
ini_open("save.ini");
var str = ini_read_string("Stacks", "0", "");
if (str != "")
{
    ds_stack_read(stack, str);
}
ini_close();
```

### `ds_stack_write(id)`

- **Devuelve:** String
- **Qué hace:** Serializa la pila a un string guardable en disco.
- **Ejemplo:**

```gml
ini_open("save.ini");

var str = ds_stack_write(stack);

ini_write_string("Stacks", "0", str);

ds_stack_clear(stack);

ini_close();
```

---

## DS Queues — colas (FIFO)


### `ds_queue_create()`

- **Devuelve:** DS Queue
- **Qué hace:** Crea una cola vacía y devuelve su id. Funciona como **FIFO** (lo primero que entra es lo primero que sale).
- **Ejemplo:**

```gml
queue = ds_queue_create();
```

### `ds_queue_destroy(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Destruye la cola y libera su memoria. **Obligatorio** al terminar.
- **Ejemplo:**

```gml
if (lives == 0)
{
    ds_queue_destroy(AI_queue);
    AI_queue = -1;
    room_goto(rm_Menu);
}
```

### `ds_queue_clear(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Vacía la cola por completo.
- **Ejemplo:**

```gml
if (count = 15 && !ds_queue_empty(command_queue))
{
    ds_queue_clear(command_queue);
    alarm[0] = game_get_speed(gamespeed_fps);
    ai_count = 0;
}
```

### `ds_queue_empty(id)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la cola está vacía.
- **Ejemplo:**

```gml
if (count == 15) && (!ds_queue_empty(command_queue))
{
    ds_queue_clear(command_queue);
    alarm[0] = game_get_speed(gamespeed_fps);
    ai_count = 0;
}
```

### `ds_queue_size(id)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el número de elementos en cola.
- **Ejemplo:**

```gml
if (!ds_queue_empty(control_queue))
{
    num = ds_queue_size(control_queue);
}
```

### `ds_queue_enqueue(id, val [, val2, ... val15])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Añade un valor al **final** de la cola.
- **Ejemplo:**

```gml
move_queue = ds_queue_create();
ds_queue_enqueue(move_queue, x + 200);
ds_queue_enqueue(move_queue, y);
ds_queue_enqueue(move_queue, x + 200);
ds_queue_enqueue(move_queue, y + 200);
ds_queue_enqueue(move_queue, x);
ds_queue_enqueue(move_queue, y + 200);
ds_queue_enqueue(move_queue, x);
ds_queue_enqueue(move_queue, y);
```

### `ds_queue_dequeue(id)`

- **Devuelve:** Cualquiera (Data type value stored in the queue) or undefined
- **Qué hace:** Saca y devuelve el valor de la **cabeza** de la cola.
- **Ejemplo:**

```gml
if (!ds_queue_empty(move_queue))
{
    var xx = ds_queue_dequeue(move_queue);
    var yy = ds_queue_dequeue(move_queue);
    move_towards_point(xx, yy, 4);
}
```

### `ds_queue_head(id)`

- **Devuelve:** Cualquiera (Data type value stored in the queue)
- **Qué hace:** Devuelve el valor de la cabeza **sin sacarlo**.
- **Ejemplo:**

```gml
num = ds_queue_head(control_queue);
```

### `ds_queue_tail(id)`

- **Devuelve:** Cualquiera (Data type value stored in the queue)
- **Qué hace:** Devuelve el valor de la cola **sin sacarlo**.
- **Ejemplo:**

```gml
num = ds_queue_tail(control_queue);
```

### `ds_queue_copy(destination, source)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia el contenido de la cola de origen en la de destino.
- **Ejemplo:**

```gml
with (instance_create_layer(x, y, "Enemies", obj_Enemy))
{
    queue = ds_queue_create();
    ds_queue_copy(queue, other.queue);
}
```

### `ds_queue_read(id, str [, legacy])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Carga la cola desde un string generado con `ds_queue_write`.
- **Ejemplo:**

```gml
queue = ds_queue_create();
ini_open("save.ini");
var str = ini_read_string("Queues", "0", "");
if (str != "")
{
    ds_queue_read(queue, str);
}
ini_close();
```

### `ds_queue_write(id)`

- **Devuelve:** String
- **Qué hace:** Serializa la cola a un string guardable en disco.
- **Ejemplo:**

```gml
ini_open("save.ini");

var str =ds_queue_write(queue);

ini_write_string("Queues", "0", str);

ds_queue_clear(queue);

ini_close();
```

---

## DS Priority Queues — colas con prioridad


### `ds_priority_create()`

- **Devuelve:** DS Priority
- **Qué hace:** Crea una cola con prioridad vacía y devuelve su id. Los valores se ordenan por su **prioridad** (un número real).
- **Ejemplo:**

```gml
p_queue = ds_priority_create();
```

### `ds_priority_destroy(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Destruye la cola con prioridad y libera su memoria. **Obligatorio** al terminar.
- **Ejemplo:**

```gml
if (lives == 0)
{
    ds_priority_destroy(AI_queue);
    AI_queue = -1;
    room_goto(rm_Menu);
}
```

### `ds_priority_clear(id)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Vacía la cola con prioridad por completo.
- **Ejemplo:**

```gml
if (count == 15 && !ds_priority_empty(command_queue))
{
    ds_priority_clear(command_queue);
    alarm[0] = game_get_speed(gamespeed_fps);
    ai_count = 0;
}
```

### `ds_priority_empty(id)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la cola con prioridad está vacía.
- **Ejemplo:**

```gml
if (count == 15 && !ds_priority_empty(command_queue))
{
    ds_priority_clear(command_queue);
    alarm[0] = game_get_speed(gamespeed_fps);
    ai_count = 0;
}
```

### `ds_priority_size(id)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el número de valores almacenados.
- **Ejemplo:**

```gml
if (!ds_priority_empty(control_priority))
{
    num = ds_priority_size(control_priority);
}
```

### `ds_priority_add(id, val, priority)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Añade un valor con la prioridad indicada.
- **Ejemplo:**

```gml
ds_priority_add(ai_priority, AI_Search, 5);
```

- **Notas:** La prioridad siempre es un número real.

### `ds_priority_change_priority(id, val, priority)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Cambia la prioridad de un valor ya almacenado.
- **Ejemplo:**

```gml
if (global.Game_Time < 1000)
{
    ds_priority_change_priority(ai_priority, AI_Search, 1);
}
```

### `ds_priority_find_max(id)`

- **Devuelve:** Cualquiera (Data type stored in the priority)
- **Qué hace:** Devuelve el valor con la prioridad **más alta**, sin sacarlo.
- **Ejemplo:**

```gml
if (ai_move)
{
    script_execute(ds_priority_find_max(ai_priority));
}
```

### `ds_priority_find_min(id)`

- **Devuelve:** Cualquiera (Data type stored in the priority)
- **Qué hace:** Devuelve el valor con la prioridad **más baja**, sin sacarlo.
- **Ejemplo:**

```gml
if (ai_move)
{
    script_execute(ds_priority_find_min(ai_priority));
}
```

### `ds_priority_find_priority(id, val)`

- **Devuelve:** Real or undefined
- **Qué hace:** Devuelve la **prioridad** asociada a un valor.
- **Ejemplo:**

```gml
p = ds_priority_find_priority(ai_priority, "intelligence");
```

### `ds_priority_delete_max(id)`

- **Devuelve:** Cualquiera (Data type stored in the priority)
- **Qué hace:** Saca y devuelve el valor con la prioridad **más alta**.
- **Ejemplo:**

```gml
if (ai_move)
{
    script_execute(ds_priority_delete_max(ai_priority));
}
```

### `ds_priority_delete_min(id)`

- **Devuelve:** Cualquiera (Data type stored in the priority)
- **Qué hace:** Saca y devuelve el valor con la prioridad **más baja**.
- **Ejemplo:**

```gml
if (ai_move)
{
    script_execute(ds_priority_delete_min(ai_priority));
}
```

### `ds_priority_delete_value(id,val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Elimina el valor indicado de la cola, sea cual sea su prioridad.
- **Ejemplo:**

```gml
if (ai_move == false)
{
    ds_priority_delete_value(ai_priority, AI_Move);
}
```

- **Notas:** Elimina la **primera** coincidencia del valor.

### `ds_priority_copy(destination, source)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia el contenido de la cola de origen en la de destino.
- **Ejemplo:**

```gml
with (instance_create_layer(x, y, "Enemies", obj_Enemy))
{
    p_queue = ds_priority_create();
    ds_priority_copy(p_queue, other.p_queue);
}
```

### `ds_priority_read(id, str, [legacy])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Carga la cola con prioridad desde un string generado con `ds_priority_write`.
- **Ejemplo:**

```gml
p_queue = ds_priority_create();
ini_open("save.ini");
var str = ini_read_string("P_Queues", "0", "");
if (str != "")
{
    ds_priority_read(p_queue, str);
}
ini_close();
```

### `ds_priority_write(id)`

- **Devuelve:** String
- **Qué hace:** Serializa la cola con prioridad a un string guardable en disco.
- **Ejemplo:**

```gml
var str;

ini_open("save.ini");

str = ds_priority_write(p_queue);

ini_write_string("P_Queues", "0", str);

ds_priority_clear(p_queue);

ini_close();
```

---

## Receta: serializar y deserializar

Todas las DS tienen un par de funciones `_read` / `_write` que permiten guardarlas
como un simple string:

```gml
// Guardar
// ⚠️ game_save_id, NO working_directory: en una build exportada working_directory
// es de solo lectura y la escritura falla en silencio. Detalle: 01 - Fundamentos/
// 14 - Persistencia y archivos.md §1.
var _f = file_text_open_write(game_save_id + "inventario.sav");
file_text_write_string(_f, ds_list_write(inventario));
file_text_close(_f);

// Cargar
if (file_exists(game_save_id + "inventario.sav"))
{
    var _f = file_text_open_read(game_save_id + "inventario.sav");
    ds_list_read(inventario, file_text_read_string(_f));
    file_text_close(_f);
}
```

---

## Receta: recorrer un mapa de forma fiable

El orden interno de un `ds_map` **no es predecible**, así que la forma correcta de
recorrerlo en código moderno es convertir sus claves a un array:

```gml
var _claves = ds_map_keys_to_array(datos);
var _n = array_length(_claves);

for (var i = 0; i < _n; i++)
{
    var _clave = _claves[i];
    show_debug_message($"{_clave} = {datos[? _clave]}");
}
```

---

## Equivalencia DS ↔ código moderno

| DS | Array / Struct equivalente |
| --- | --- |
| `ds_list_create()` | `var _lista = [];` |
| `ds_list_add(l, v)` | `array_push(_lista, v);` |
| `ds_list_delete(l, i)` | `array_delete(_lista, i, 1);` |
| `ds_list_find_index(l, v)` | `array_get_index(_lista, v);` |
| `ds_list_size(l)` | `array_length(_lista);` |
| `ds_map_create()` | `var _mapa = {};` |
| `ds_map_set(m, k, v)` | `_mapa[$ k] = v;` |
| `ds_map_find_value(m, k)` | `variable_struct_get(_mapa, k);` |
| `ds_map_keys_to_array(m)` | `struct_get_names(_mapa);` |
| `ds_*_destroy(id)` | *nada: se recolecta solo* |

---

## Fuentes

- [GML Code Reference — GameMaker LTS 2026](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/GML_Reference.htm)
- [Data Structures (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Data_Structures/Data_Structures.htm)
- [Accessors (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Accessors.htm)
- Verificación de cada firma con `gm-cli manual read "<función>"` y contra el manual LTS (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
