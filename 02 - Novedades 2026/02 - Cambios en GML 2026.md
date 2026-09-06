# Cambios en GML en 2026 (LTS 2026.0)

> El archivo más importante de esta carpeta. Si vienes de LTS 2022 o de 2024.x, **lee esto antes de compilar nada**.
> Todo lo que aparece aquí está verificado contra el manual LTS oficial.

---

## 1. Handles: el cambio crítico

### 1.1 Qué es un handle

Antes, un "recurso" en GML era simplemente un número: `spr_player` valía `0`, `obj_enemy` valía `3`, una DS list creada valía `0`, etc. Eran números indistinguibles entre sí.

Ahora, esos recursos se representan con **handles** (manejadores): un **entero de 64 bits** donde:

- los **primeros 32 bits** guardan información del **tipo** de recurso;
- los **siguientes 32 bits** guardan el **índice** del recurso.

Es decir: **el handle lleva el tipo pegado**. `typeof()` sobre un handle devuelve `"ref"` (referencia).

### 1.2 Qué cosas son handles

Según la página *Data Types* del manual:

- **Data Structures** (ds_list, ds_map, ds_grid, ds_stack, ds_queue, ds_priority)
- **Assets**: Objects, Sprites, Rooms, Fonts, Sounds, Sequences, etc.
- **Instancias de objeto** (Object Instances)
- **Script Functions**
- **Particle System Instances**, **Particle Emitters**, **Particle Types**
- **Buffers**, **Vertex Buffers** y **Vertex Formats**
- **Surfaces**
  - *Excepción*: `surface_get_target()` y `surface_get_target_depth()` **no** devuelven handle, devuelven índice.
- Referencias creadas con `ref_create()`
- **Time Sources**
- **Room Layers** y **Tile Maps**
- **Flex Panels**

### 1.3 Obtener e inicializar handles

Obtienes un handle al crear un recurso con una función `*_create()` o al referenciar un recurso existente.

```gml
// Create Event

// Handles de assets: basta con nombrarlos
mi_sprite    = spr_player;      // handle a un Sprite
mi_objeto    = obj_enemigo;     // handle a un Object

// Handles de estructuras creadas en runtime
lista        = ds_list_create();     // handle a DS List
mapa         = ds_map_create();      // handle a DS Map
buffer       = buffer_create(256, buffer_fixed, 1); // handle a Buffer
superficie   = surface_create(512, 512);            // handle a Surface

// Handles de instancias: usar noone como valor inválido
enemigo      = noone;

// Handles de capas / tilemaps
capa         = layer_get_id("Suelo");
tilemap      = layer_tilemap_get_id(capa);
```

**Buenas prácticas del manual:**

- Inicializa siempre la variable que va a guardar un handle a su valor inválido: **`noone` (-4)** para instancias, **`-1`** para todo lo demás.
- Tras destruir un recurso, **resetea** la variable a `-1` (o `noone` si era instancia). Motivo: los índices **se reciclan**. Si destruyes una DS List con índice 0 y creas otra, la nueva tendrá índice 0 y tu variable "vieja" apuntará a una lista viva que no es la tuya.

```gml
// Clean Up Event
if (ds_exists(lista, ds_type_list))
{
    ds_list_destroy(lista);
}
lista = -1;   // imprescindible: el índice se recicla
```

### 1.4 Comprobación de tipos en argumentos de funciones

La información de tipo del handle se usa para **validar que pasas el recurso correcto**.

```gml
// ANTES (2022 y anteriores): compilaba y en runtime pasaban cosas raras
var _lista = ds_list_create();
ds_map_add(_lista, "clave", 10);   // colabas una DS List en una función de DS Map

// AHORA (2026): error. La función detecta que el handle no es de DS Map.
ds_map_add(_lista, "clave", 10);   // ✗ error de tipo
```

> ⚠️ **Matiz importante del manual:** por compatibilidad heredada, estas funciones **siguen aceptando números simples**. Si pasas `2` a una función de DS Map, buscará el DS Map con ID 2. Por tanto: **pasa siempre el handle devuelto por `*_create()`**, nunca un número.

### 1.5 Por qué ya NO puedes incrementar un ID de asset

Este es el patrón que **rompe** en 2026:

```gml
// ✗ ANTES: truco clásico para recorrer "todos los sprites"
for (var i = 0; i < sprite_get_number(spr_player); i++)
{
    var _spr = spr_player + i;   // ✗ aritmética sobre un handle → NO permitido
    draw_sprite(_spr, 0, x, y);
}

// ✗ ANTES: "dame el objeto siguiente en el orden interno"
var _siguiente = obj_enemigo + 1;   // ✗ error
```

Por qué se prohíbe: el orden interno de los assets puede cambiar en cualquier momento (al añadir, borrar o reordenar), así que ese código nunca fue fiable. Ahora, además, el handle no es un número "recorrible".

**Alternativas correctas en 2026:**

```gml
// Opción A: estructura de datos explícita (la recomendada)
global.enemigos = [obj_slime, obj_murcielago, obj_golem];

// Opción B: recorrer por nombre con asset_get_ids()
var _todos = asset_get_ids(asset_object);
for (var i = 0; i < array_length(_todos); i++)
{
    var _obj = _todos[i];
    if (object_is_ancestor(_obj, obj_enemigo))
    {
        show_debug_message($"Enemigo: {object_get_name(_obj)}");
    }
}

// Opción C: tags
var _con_tag = asset_get_ids(asset_sprite);   // + filtrar por asset_get_tags()
```

Regla mental: **si necesitas "el siguiente asset", ya no lo pidas por aritmética; mantenlo en un array, un enum o unos tags.**

### 1.6 JSON y serialización de handles

El sistema JSON se ha actualizado para serializar y parsear handles correctamente. Esto es vital si guardabas partidas.

```gml
// Guardar: los handles se serializan de forma meaningful
var _save =
{
    nivel:      rm_bosque,       // handle a Room
    sprite:     spr_heroe,       // handle a Sprite
    inventario: global.inventario
};

var _json = json_stringify(_save);
// El handle aparece serializado con su representación de referencia

// Cargar
var _cargado = json_parse(_json);
room_goto(_cargado.nivel);   // funciona: se ha reconstruido el handle
```

> ⚠️ **Cuidado con partidas antiguas.** Si tus saves de versiones previas guardaban IDs **numéricos** de assets, al parsearlos ahora obtendrás números, no handles. Hay una opción en **Deprecated Behaviours** (Game Options) para el comportamiento antiguo de parseo de JSON, pero la solución limpia es **migrar los saves**: guarda el *nombre* del asset (`room_get_name()` / `sprite_get_name()`) y resuélvelo al cargar con `asset_get_index()`.

```gml
// Migración robusta: guarda nombres, no handles crudos
var _save = { nivel_nombre: room_get_name(room) };
// ...
var _cargado = json_parse(_json);
var _rm = asset_get_index(_cargado.nivel_nombre);
if (_rm != -1) room_goto(_rm);
```

### 1.7 Strings, números e invalidación

Del manual:

| Operación | Resultado |
|---|---|
| `string(handle)` | `"ref <tipo> <id>"` o `"ref <tipo> <nombre>"`, p. ej. `"ref ds_list 1"`, `"ref sprite spr_player"` |
| `real(handle)` / `int64(handle)` | el **número de índice** (reciclable, ver 1.3) |
| Imprimir un handle | se convierte implícitamente a su representación en string |
| `handle_parse(str)` | convierte `"ref <tipo> <id>"` / `"ref <tipo> <nombre>"` de vuelta a handle |

```gml
sprite = spr_player;
handle_como_string = string(sprite);            // "ref sprite spr_player"
handle_desde_string = handle_parse(handle_como_string);

show_debug_message($"{sprite} ({typeof(sprite)})");
// ref sprite spr_player (ref)

show_debug_message($"{handle_como_string} ({typeof(handle_como_string)})");
// ref sprite spr_player (string)

show_debug_message($"{handle_desde_string} ({typeof(handle_desde_string)})");
// ref sprite spr_player (ref)
```

**Un handle inválido** tiene índice `-1`, o `-4` (`noone`) si es de instancia. Todos los handles se pueden comparar contra su valor inválido:

```gml
if (handle != -1)    { /* recurso válido */ }
if (handle != noone) { /* instancia válida */ }
```

### 1.8 Funciones nuevas de handles

| Función | Qué hace |
|---|---|
| `is_handle(val)` | Devuelve `true` si el valor es un handle |
| `handle_parse(value_string)` | Parsea un string `"ref <tipo> <id>"` y devuelve el handle (o `undefined` si el tipo es inválido o el string está mal formado) |
| `ref_create(...)` | Crea una referencia explícita (handle) |
| `int64(val)` | Convierte a entero de 64 bits (los handles se almacenan como int64) |
| `is_int64(val)` | Comprueba si un valor es int64 |

```gml
// Comprobar si una variable guarda un handle
var _h = sprite_index;
var _es = is_handle(_h);

show_debug_message($"La variable {(_es ? "guarda" : "no guarda")} un handle");
```

> **Nota sobre nomenclatura:** el manual documenta `is_handle()` y `handle_parse()`. No existe una función `handle_type()` documentada en la sección *Data Type Functions*; para inspeccionar el tipo usa `typeof()` (devuelve `"ref"` para cualquier handle) o el propio string del handle, que incluye el nombre del tipo.

---

## 2. Template strings y `string_ext()`

### 2.1 Template strings (`$"..."`)

Prefijando un literal de string con `$`, lo que haya entre `{}` se ejecuta como **GML normal** y su resultado se inserta en el string.

```gml
var _mundo = "Tierra";
var _t = $"Hola {_mundo}!";
// Equivale a: string("Hola {0}!", _mundo)
```

Reglas verificadas en el manual:

- **Todo lo que está entre llaves es GML**: puedes poner expresiones arbitrarias.
  ```gml
  var _t = $"El resultado es {5 * power(pi, 3) + 37.84094}";
  ```
- El editor **resalta** el código dentro de las llaves como GML, y **Feather lo analiza** igual que al resto del código.
  ```gml
  var _arr = [1, 2, 3, 4];
  var _a = $"El primero es {_arr[| 0]}";
  // GM1028 - Accessor is intended for type of 'Id.DsList' but 'Array<Real>' appears instead.
  ```
- Para usar llaves **literales**, escápalas con barra invertida: `\{`.
- Puedes partir un template **en varias líneas, pero solo dentro de las partes de expresión**; los saltos de línea del texto literal hay que meterlos con caracteres de escape.

```gml
// ✓ Correcto
var _a = $"Esta es la \n{
valid
}\nforma de partir un template";

// ✗ Incorrecto: parte el texto literal
var _b = $"Esta es la 
{invalido}
forma de partir un template";
```

### 2.2 `string()` con formato

`string()` acepta un *format string* con marcadores `{0}`, `{1}`, … y los valores como argumentos extra:

```gml
// ANTES: concatenación ilegible
show_debug_message("Vida: " + string(hp) + "/" + string(hp_max) + " | Nivel " + string(nivel));

// AHORA (2026)
show_debug_message(string("Vida: {0}/{1} | Nivel {2}", hp, hp_max, nivel));
// o, mejor todavía:
show_debug_message($"Vida: {hp}/{hp_max} | Nivel {nivel}");
```

### 2.3 `string_ext()`

Igual que `string()`, pero los valores se pasan como **array** en el segundo argumento. Útil cuando ya tienes los datos en un array.

```gml
numbers = [59, 23, 656, 8, 54];
array_sort(numbers, true);

var _str = string_ext("Los tres menores son: {0}, {1} y {2}", numbers);
// "Los tres menores son: 8, 23 y 54"
```

Firma: `string_ext(value_or_format, values)` → devuelve `String`.

---

## 3. Otras novedades de strings

Además de los templates, la sección de Strings del manual LTS incluye muchas funciones de manipulación que conviene conocer porque evitan escribir helpers a mano:

| Categoría | Funciones |
|---|---|
| Búsqueda | `string_pos`, `string_pos_ext`, `string_last_pos`, `string_last_pos_ext`, `string_starts_with`, `string_ends_with`, `string_count` |
| Recorte | `string_trim`, `string_trim_start`, `string_trim_end` |
| Split / Join | `string_split`, `string_split_ext`, `string_join`, `string_join_ext`, `string_concat`, `string_concat_ext` |
| Iteración | `string_foreach` |
| Bytes / caracteres | `string_byte_at`, `string_byte_length`, `string_set_byte_at`, `string_char_at`, `string_ord_at` |

### 3.1 `toString()`

Si pasas un **struct** o una **instancia** a `string()`, `string_ext()`, `show_debug_message()` o `show_debug_message_ext()`, se llamará a su método `toString()` si lo tiene.

```gml
// En una instancia
toString = function()
{
    return string("Soy la instancia con ID {0}", id);
}
```

```gml
string(self);   // llama a toString(), si existe
string(id);     // imprime "ref <id>" — pasar el ID NO llama a toString()
```

Los **arrays** se convierten automáticamente sin necesidad de `toString()`.

También puedes pasar una referencia directamente a `draw_text()` y se convertirá sola:

```gml
draw_text(0, 0, self);
```

---

## 4. Nuevas funciones de structs

Lista completa de la sección *Struct Functions* del manual LTS:

| Función | Uso |
|---|---|
| `struct_exists` / `struct_get` / `struct_set` / `struct_remove` | CRUD básico por nombre |
| `struct_get_names` / `struct_names_count` | introspección |
| `struct_foreach` | iterar pares clave/valor |
| `struct_get_from_hash` / `struct_set_from_hash` / `struct_exists_from_hash` / `struct_remove_from_hash` | acceso por hash (optimización) |
| `variable_get_hash` | obtener el hash de un nombre |
| `variable_clone` | clon profundo de un valor/struct |
| `is_instanceof` / `instanceof` | comprobar herencia de constructores |
| `static_get` / `static_set` | acceder al "static" de un struct |

> **Nota de optimización del manual:** el compilador sustituye los nombres de miembro por su **hash** en tiempo de compilación cuando detecta que el nombre es constante. Por eso existen las variantes `*_from_hash`: si vas a acceder miles de veces por frame, calcula el hash una vez con `variable_get_hash()` y usa las funciones `*_from_hash`.

```gml
// Acceso normal
var _vida = struct_get(datos, "vida");

// Acceso optimizado por hash en un bucle caliente
var _h = variable_get_hash("vida");
for (var i = 0; i < 10000; i++)
{
    var _v = struct_get_from_hash(datos[i], _h);
}
```

```gml
// Iterar un struct
struct_foreach(datos, function(_valor, _clave)
{
    show_debug_message($"{_clave} = {_valor}");
});
```

---

## 5. Funciones de arrays

El manual LTS documenta tres niveles:

**Básicas:** `array_create`, `array_copy`, `array_equals`, `array_get`, `array_set`, `array_push`, `array_pop`, `array_shift`, `array_insert`, `array_delete`, `array_get_index`, `array_contains`, `array_contains_ext`, `array_sort`, `array_reverse`, `array_shuffle`, `array_length`, `array_resize`, `array_first`, `array_last`.

**Avanzadas (funcionales):** `array_find_index`, `array_any`, `array_all`, `array_foreach`, `array_reduce`, `array_concat`, `array_union`, `array_intersection`, `array_filter`, `array_map`, `array_unique`, `array_copy_while`.

**Extendidas (modifican el array original en vez de copiar):** `array_create_ext`, `array_filter_ext`, `array_map_ext`, `array_unique_ext`, `array_reverse_ext`, `array_shuffle_ext`.

### 5.1 Métodos callback

Las funciones avanzadas reciben un **método callback** al que GameMaker pasa dos argumentos:

1. el **valor** del elemento;
2. el **índice** del elemento.

Cuando el callback solo devuelve true/false, se llama **predicate**.

```gml
var _frutas = ["manzana", "platano", "coco", "pitaya"];

var _hay_manzana = array_any(_frutas, function(_val, _ind)
{
    return _val == "manzana";
});

show_debug_message(_hay_manzana);   // 1 (true)
```

### 5.2 Offset y length

La mayoría de las avanzadas admiten `offset` y `length`:

- **offset**: índice 0-based donde empieza. Puede ser **negativo** (`-1` = último). Se **clampea** entre 0 y el último elemento.
- **length**: número de elementos a recorrer desde el offset. Puede ser **negativo**, y entonces se recorre **hacia atrás**. `infinity` / `-infinity` llegan al final / al principio.

```gml
var _a = [10, 20, 30, 40, 50, 60];

// Desde el índice 3, tres elementos hacia delante → [40, 50, 60]
var _adelante = array_filter(_a, function(_v, _i) { return _v > 35; }, 3, 3);

// Desde el índice 3, tres elementos hacia atrás → recorre 3, 2, 1
var _atras = array_filter(_a, function(_v, _i) { return true; }, 3, -3);
```

> Si la función devuelve una copia modificada, **solo** devuelve los elementos sobre los que operó: el resto se descarta.

---

## 6. Cambios en colisiones

### 6.1 Bounding boxes más precisos

| | Sistema antiguo | Sistema nuevo (2026) |
|---|---|---|
| Coordenadas de bbox | **redondeadas a enteros** | **sin redondear**, se usan tal cual |
| Extremos | **exclusivos** (excluyen borde inferior y derecho) | **inclusivos** |
| Máscara de 16×16 | de (0, 0) a (15, 15) | de (0.0, 0.0) a (16.0, 16.0) |

Consecuencias prácticas:

- Las colisiones con posiciones/escalas **en coma flotante** ahora se comportan como esperas; antes siempre se redondeaba y había desajuste entre lo renderizado y lo comprobado.
- **`bbox_right` de un sprite cuadrado de 16×16 es 16**, mientras que `sprite_get_bbox_right()` devuelve 15. Es intencional (el bbox inclusivo se extiende un píxel más allá).

```gml
// Un sprite de 16x16 en x = 100
show_debug_message($"bbox_left={bbox_left} bbox_right={bbox_right}");
// bbox_left=100 bbox_right=116   (no 115)

show_debug_message(sprite_get_bbox_right(sprite_index));
// 15   (offset del borde derecho dentro del sprite)
```

### 6.2 Regla del centro del píxel

Para que dos **bounding boxes** se consideren en colisión, deben solaparse. A nivel de píxel, cuenta como solape **cuando se cubre el centro del píxel**.

```gml
// bbox de (0.0, 0.0) a (16.0, 16.0)
// tu máscara debe tocar el área entre (0.5, 0.5) y (15.5, 15.5)
```

Excepciones (no requieren cubrir el centro del píxel):

- forma contra forma: `rectangle_in_rectangle()`, etc.
- forma contra una máscara que **no** es de instancia, p. ej. **Tile Maps** con `collision_rectangle()`
- `collision_point()` y `collision_line()` (pueden comprobar en cualquier punto dentro del píxel)

### 6.3 Collision Compatibility Mode

Si al migrar un proyecto las colisiones se comportan raro, **activa primero** `General Game Options > Collision Compatibility Mode` para volver al sistema antiguo. Úsalo como parche de migración, no como destino: el manual recomienda adaptar el código.

En proyectos nuevos no hace falta activarlo.

### 6.4 Tile Maps y arrays en funciones de colisión

Todas las funciones de colisión que aceptan objeto/instancia aceptan ahora también:

- un **array** con varios objetos (mezclables entre sí);
- un **Tile Map Element ID**;
- **ambos mezclados** en el mismo array.

```gml
// Create Event
tilemap = layer_tilemap_get_id("Tiles_Solidos");

// Step Event

// ANTES: solo un objeto, y para tiles habías que hacer trampas
if (!place_meeting(x + 4, y, obj_roca)) { x += 4; }

// AHORA (2026): arrays y tilemaps en la misma llamada
if (!place_meeting(x + 4, y, [obj_roca, obj_arbusto, tilemap]))
{
    x += 4;
}
```

Cosas que debes saber al usar tiles:

- La colisión contra un Tile Map usa la **máscara de colisión del sprite del Tile Set**. Si el Tile Map no tiene Tile Set o el Tile Set no tiene sprite, **siempre devuelve false**.
- En el editor del Tile Set, **"Disable Source Sprite Export" debe estar desmarcado**, o no hay sprite que usar para colisionar.
- ⚠️ Funciones como `instance_place()` o `collision_circle()` **pueden devolver `0`** si el Tile Map encontrado tiene ID 0. **No uses el valor de retorno como booleano**: compara contra `noone`.

```gml
// ✗ MAL: un tilemap con ID 0 se evalúa como false
var _hit = collision_rectangle(x1, y1, x2, y2, tilemap, false, false);
if (_hit) { /* esto no se ejecuta si colisionó con el tilemap 0 */ }

// ✓ BIEN
if (_hit != noone)
{
    // hubo colisión
}
```

El manual recomienda usar **herencia (parent objects)** en lugar de arrays cuando repites la misma comprobación en varios sitios: es más limpio y no hay que mantener el array.

---

## 7. Descarte automático de assets + `gml_pragma("MarkTagAsUsed")`

### 7.1 El comportamiento nuevo

El compilador **descarta automáticamente** todos los assets que no estén referenciados directamente (usados en un Room, en una Sequence o referenciados en código).

Dónde: se puede desactivar en **General Game Options** (opción "Automatically remove unused assets when compiling").

Problema: si cargas assets dinámicamente (por nombre, desde Included Files, por DLC…), el compilador no ve la referencia y **se los lleva por delante**.

### 7.2 Solución: `MarkTagAsUsed`

```gml
// En cualquier script del proyecto (el pragma se procesa antes de compilar,
// así que da igual dónde esté colocado)

gml_pragma("MarkTagAsUsed", "dinamico");

// Se pueden marcar varios tags de una vez:
gml_pragma("MarkTagAsUsed", "dlc", "personajes", "niveles_extra");
```

Después, en el Asset Browser, **asigna el tag** a todos los assets que cargas en runtime. Esos assets siempre estarán en el paquete final.

### 7.3 Pragma relacionado: `MarkUILayerAsUsed`

```gml
// Asegura que una UI layer de un Prefab llegue al proyecto principal al exportar
gml_pragma("MarkUILayerAsUsed", "Mi UILayer");
```

> ⚠️ El objeto que llama a este pragma **no debe estar** en la UI layer que marcas, o tendrás dos instancias al arrastrar el prefab a una capa de instancias.

---

## 8. Sección "Deprecated Behaviours" en Game Options

Nueva sección en **General Game Options** que permite reactivar comportamientos antiguos que han cambiado o quedado deprecados. Según el blog oficial y los release notes, incluye (entre otros):

- `instance_change()` y `position_change()` (comportamiento antiguo)
- el **cambio de colisiones** descrito en la sección 6
- los **cambios de parseo de JSON**
- **conversión string → number**
- tratamiento de **`other`**
- **errores estrictos de audio**

Los release notes lo describen como «opciones nuevas para activar comportamientos heredados de varios cambios hechos en 2024.8 y posteriores».

Usa esto como **puente de migración**, no como configuración permanente: son comportamientos que GameMaker ha cambiado deliberadamente.

---

## 9. Literales numéricos: binarios, guiones bajos y colores CSS

### 9.1 Literales binarios

Prefijo `0b`:

```gml
var _seis = 0b0010 | 0b0100;   // 0b0110 → 6
```

### 9.2 Guiones bajos en literales

Los guiones bajos se **ignoran al compilar** y solo sirven como separador visual. Funcionan en reales, hexadecimales y binarios:

```gml
var _entero = 100_000_000;              // 100000000
var _flotan = 3_141.59;                 // 3141.59
var _hex    = 0xDEAD_BEEF;              // 0xDEADBEEF
var _bin    = 0b01101000_01101001;      // 0b0110100001101001
```

### 9.3 Hexadecimal y colores CSS

- Formatos clásicos: `$abcd` y `0xabcd`.
- Formato con `#`: pensado para **colores CSS en `#RRGGBB`**, y **no equivale** al mismo valor con `$`.

```gml
$2c8edd != #2c8edd      // ojo: NO son iguales

$2c8edd == #dd8e2c      // hay que intercambiar los pares de bytes
```

> Nota del manual: al escribir hex en un **array literal** hay que dejar un espacio entre `[` y `#`, o el parser falla.
> ```gml
> var _cols = [ #ff0000, #00ff00 ];   // espacio necesario
> ```

---

## 10. Cheatsheet ANTES vs DESPUÉS

| Concepto | ANTES | AHORA (2026) |
|---|---|---|
| IDs de assets | números recorribles | **handles** con tipo; no se pueden incrementar |
| Pasar recurso equivocado | pasaba desapercibido | **error de tipo** |
| Guardar assets en JSON | guardabas el número | `json_stringify`/`json_parse` manejan handles; para saves, guarda el **nombre** |
| Inicializar handle | `0` o `-1` según humor | `-1`, y **`noone` para instancias** |
| Destruir recurso | te olvidabas de limpiar | resetea a `-1`/`noone` (índices **reciclables**) |
| Formatear strings | concatenación con `+` | `$"..."` o `string()` / `string_ext()` |
| Colisiones múltiples | solo parent objects | **arrays** con objetos y **tilemaps** mezclados |
| bbox | redondeados, exclusivos | precisos, **inclusivos** |
| Assets sin referenciar | se incluían | **se descartan**; usa `MarkTagAsUsed` |
| Números grandes ilegibles | `100000000` | `100_000_000` |

---

## Fuentes

- Data Types (Handles, int64, literales) — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Data_Types.htm
- `is_handle()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/is_handle.htm
- `handle_parse()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/handle.htm
- Variable Functions (structs y tipos) — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Variable_Functions.htm
- Array Functions — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm
- Strings (template strings, toString) — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/Strings.htm
- `string_ext()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/string_ext.htm
- Collisions — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/Collisions.htm
- Collision Compatibility Mode — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Movement_And_Collisions/Collisions/Collision_Compatibility_Mode.htm
- `gml_pragma()` — https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/OS_And_Compiler/gml_pragma.htm
- Blog LTS 2026.0 — https://gamemaker.io/en/blog/lts-2026-release
- Release notes 2026.0.0 — https://releases.gamemaker.io/release-notes/2026/0
