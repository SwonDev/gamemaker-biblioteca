# 14 · Arrays en GML

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23).

> Todas las firmas han sido verificadas contra el manual oficial LTS.

---

## Arrays: el tipo de datos recomendado en 2026

Los **arrays** son la estructura de datos por defecto en el GML moderno. A diferencia de
las estructuras DS, **se recolectan automáticamente**, así que no hay que destruirlos.

```gml
// Crear
var _nombres = ["Ana", "Luis", "Marta"];
var _vacio   = array_create(10, 0);

// Leer y escribir
var _primero = _nombres[0];
_nombres[0] = "Beatriz";

// Añadir y quitar
array_push(_nombres, "Pedro");
var _ultimo = array_pop(_nombres);
```

> Los índices de los arrays empiezan en **0**, al contrario que los strings, que empiezan en 1.

### Funciones que devuelven un array nuevo frente a las que modifican

Esta distinción es la fuente de errores más común con arrays:

| Devuelven un array **nuevo** | Modifican el array **original** |
| --- | --- |
| `array_reverse` | `array_reverse_ext` |
| `array_shuffle` | `array_shuffle_ext` |
| `array_filter` | `array_filter_ext` |
| `array_map` | `array_map_ext` |
| `array_unique` | `array_unique_ext` |
| `array_concat`, `array_union`, `array_intersection` | `array_push`, `array_pop`, `array_shift`, `array_insert`, `array_delete`, `array_set`, `array_copy`, `array_sort`, `array_resize` |

```gml
var _a = [3, 1, 2];
var _b = array_reverse(_a);   // _b = [2, 1, 3]; _a sigue siendo [3, 1, 2]
array_reverse_ext(_a);        // ahora _a = [2, 1, 3]
```

---

## Métodos de retorno (callbacks)

Las funciones avanzadas reciben una función que GameMaker ejecuta por cada elemento.
**Siempre le pasa dos argumentos**:

1. El **valor** del elemento.
2. El **índice** del elemento.

```gml
var _a = ["apple", "banana", "coconut"];

var _tiene_apple = array_any(_a, function(_val, _ind)
{
    return _val == "apple";
});
```

Cuando la función solo debe devolver `true` o `false`, se llama **predicado**.

### `offset` y `length`: recorrer solo una parte

Casi todas las funciones avanzadas aceptan `offset` y `length` para acotar el recorrido:

- **`offset`** es el índice (base 0) por el que se empieza. Puede ser **negativo**, en cuyo
  caso cuenta desde el final: `-1` es el último elemento.
- **`length`** es cuántos elementos se recorren. Si es **negativo**, el recorrido va
  **hacia atrás**. Puedes usar `infinity` / `-infinity` para ir hasta el final o el principio.

```gml
var _a = [0, 1, 2, 3, 4, 5, 6, 7];

array_foreach(_a, fn, 3, 3);    // recorre 3, 4, 5
array_foreach(_a, fn, 3, -3);   // recorre 3, 2, 1
array_foreach(_a, fn, -1, 2);   // recorre 7 (offset -1 clamped al último)
```

> Si la función devuelve una versión modificada del array, **solo** se devuelven los
> elementos sobre los que se ha operado, en el orden del recorrido. El resto se descarta.

---

## Funciones básicas


### `array_create(size, [value])`

- **Devuelve:** Array
- **Qué hace:** Crea un array del tamaño indicado. Si pasas un segundo argumento, **todas** las posiciones se rellenan con ese valor; si no, se rellenan con `0`.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
instance_array = array_create(100, noone);
```

*Ejemplo 2: crear un array 2D con todos los elementos inicializados a un valor simple*


```gml
the_array = array_create(100);

var i = 0;
repeat(100)
{
    the_array[i++] = array_create(100, "the_value");
}
```

```gml
the_array = array_create(100, array_create(100, "the_value"));
```

- **Notas:** ⚠ Si rellenas con un **struct o un array**, todas las posiciones compartirán la **misma referencia**. Usa `array_create_ext` con una función que cree uno nuevo en cada posición.

### `array_length(array)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el número de elementos del array.
- **Ejemplo:**

```gml
for (var i = 0; i < array_length(a); ++i)
{
    a[i] = -1;
}
```

### `array_resize(array_index, new_size)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Cambia el tamaño del array. Si lo agrandas, las posiciones nuevas se rellenan con `0`; si lo encoges, se descartan los elementos sobrantes.
- **Ejemplo:**

```gml
if (array_length(a) > 10)
{
    array_resize(a, 10);
}
```

### `array_get(variable, index)`

- **Devuelve:** Cualquiera (Any valid data type that an array can hold)
- **Qué hace:** Devuelve el valor que ocupa la posición indicada. Equivale a `array[index]`.
- **Ejemplo:**

```gml
for (var i = 0; i < 10; ++i)
{
    show_debug_message(array_get(my_array, i));
}
```

### `array_set(variable, index, value)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Escribe un valor en la posición indicada del array. Equivale a `array[index] = valor`. **Modifica el array** y no devuelve nada.
- **Ejemplo:**

```gml
for (var i = 0; i < 10; ++i)
{
    array_set(score_array, i, i*100);
}
```

### `array_first(array)`

- **Devuelve:** Cualquiera (Any valid data type that an array can hold) or undefined if the array is empty
- **Qué hace:** Devuelve el **primer** elemento del array, o `undefined` si está vacío. No lo elimina.
- **Ejemplo:**

```gml
var _first_added_enemy = array_first(enemies);

with (_first_added_enemy)
{
    show_debug_message(string(id) + " is the first enemy in the array.");
}
```

- **Notas:** Devuelve `undefined` si el array está vacío.

### `array_last(array)`

- **Devuelve:** Cualquiera (Any valid data type that an array can hold) or undefined if the array is empty
- **Qué hace:** Devuelve el **último** elemento del array, o `undefined` si está vacío. No lo elimina.
- **Ejemplo:**

```gml
var _last_added_enemy = array_last(enemies);

with (_last_added_enemy)
{
    show_debug_message(string(id) + " is the last enemy in the array.");
}
```

- **Notas:** Devuelve `undefined` si el array está vacío.

### `array_push(variable, value, [value], [value], [etc...])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Añade uno o más valores al **final** del array, aumentando su longitud. Es el equivalente al `push` de otros lenguajes.
- **Ejemplo:**

```gml
array_push(score_array, obj_Player1.scr, obj_Player2.scr, obj_Player3.scr, obj_Player4.scr);
```

### `array_pop(array)`

- **Devuelve:** Cualquiera or undefined
- **Qué hace:** Saca y devuelve el **último** elemento del array, reduciendo su longitud en 1. Devuelve `undefined` si el array está vacío.
- **Ejemplo:**

```gml
var _lastscore = array_pop(score_array);
draw_text(32, 32, "Last Score = " + string(_lastscore));
```

- **Notas:** Devuelve `undefined` si el array está vacío.

### `array_shift(array)`

- **Devuelve:** Cualquiera (the type of the removed first array element)
- **Qué hace:** Saca y devuelve el **primer** elemento del array, desplazando los demás. Devuelve `undefined` si está vacío.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _array = ["A", "B", "C"];
repeat(2)
{
    array_shift(_array);
}
show_debug_message(_array);
```

*Ejemplo 2: cola con array_shift y array_push*


```gml
var _queue = [];
var _incoming = ["S", "O", "M", "E", " ", "L", "E", "T", "T", "E", "R", "S"];
MAX_QUEUE_LENGTH = 4;
var _len = array_length(_incoming), i = 0;
repeat(_len)
{
    array_push(_queue, _incoming[i]);
    if (array_length(_queue) > MAX_QUEUE_LENGTH)
    {
        array_shift(_queue);
    }
    i++;
}
```

*Ejemplo 3: rotar un array*


```gml
var _array = ["F", "O", "R", "E", "V", "E", "R"];
repeat(10)
{
    array_push(_array, array_shift(_array));
    show_debug_message(_array);
}
```

- **Notas:** Devuelve `undefined` si el array está vacío.

### `array_insert(variable, index, value, [value], [value], [etc...])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Inserta uno o más valores en la posición indicada, desplazando los elementos siguientes hacia el final.
- **Ejemplo:**

*Ejemplo 1: insertar un solo valor*


```gml
array = [1, 2, 3, 5];
var _missing_value = 4;
array_insert(array, 3, _missing_value);
show_debug_message(array);
```

*Ejemplo 2: insertar varios valores*


```gml
var _array = ["G", "a", "k", "e", "r"];
array_insert(_array, 2, "m", "e", "M", "a");
show_debug_message(string_join_ext("", _array));
```

### `array_delete(array, index, number)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Elimina `number` elementos a partir de la posición `index`, reindexando el array.
- **Ejemplo:**

*Ejemplo 1: borrar los 5 primeros elementos*


```gml
var _score_array = [96, 77, 54, 89, 92, 93, 80, 12, 65, 71];
array_delete(_score_array, 0, 5);
```

*Ejemplo 2: borrar los 3 últimos elementos*


```gml
var _values = ["a", "b", "c", "d", "e", -1, -1, -1];
array_delete(_values, -1, -3);
```

*Ejemplo 3: borrar un rango*


```gml
var _array_with_undefined = [1, 2, 3, 4, 5, 6, undefined, undefined, undefined, 7, 8, 9];
array_delete(_array_with_undefined, 6, 3);
```

### `array_copy(dest, dest_index, src, src_index, length)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia `length` elementos del array de origen, empezando en `src_index`, dentro del array de destino a partir de `dest_index`. **Modifica el array de destino** y no devuelve nada.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
if (!array_equals(inventory_array, item_array))
{
    var _len = array_length(inventory_array);
    array_copy(item_array, 0, inventory_array, 0, _len);
}
```

*Ejemplo 2: longitud negativa*


```gml
var _a = [1, 2, 3, 4];
var _b = [5, 6, 7, 8];

array_copy(_a, 1, _b, -1, -2);
show_debug_message(_a);
```

*Ejemplo 3: ampliar el array de destino*


```gml
var _a = [-3, -2, -1];
var _b = [1, 2, 3];

array_copy(_a, 5, _b, 0, 3);
show_debug_message(_a);
```

### `array_equals(var1, var2)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si dos arrays tienen **el mismo contenido** y el mismo número de elementos.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _array1 = [1, 2, 3, 4, 5];
var _array2 = [1, 2, 5, 4, 3];

if (!array_equals(_array2, _array1))
{
    var _len = array_length(_array1);
    array_copy(_array2, 0, _array1, 0, _len);
}

show_debug_message(_array1);
show_debug_message(_array2);
```

*Ejemplo 2: arrays anidados y referencias*


```gml
var _the_struct = {a: 84, b: 38};

var _array1 = [_the_struct, 5, "hello", ["this", "that"]];
var _array2 = [_the_struct, 5, "hello", ["this", "that"]];
var _array3 = [{a: 84, b: 38}, 5, "hello", ["this", "that"]];

show_debug_message($"_array1 equals _array2: {array_equals(_array1, _array2)}");
show_debug_message($"_array1 equals _array3: {array_equals(_array1, _array3)}");
```

### `array_get_index(array, value, [offset], [length])`

- **Devuelve:** Real (the index of the first occurrence of the value if found or -1 if it isn't found)
- **Qué hace:** Devuelve el índice de la **primera** aparición del valor, o `-1` si no está.
- **Ejemplo:**

*Ejemplo 1*


```gml
var _array = array_create(100, 1);
_array[7] = 13;
var _index = array_get_index(_array, 13);
show_debug_message("The value 13 was found at index {0}", _index);
```

*Ejemplo 2*


```gml
var _array = ["a", "b", "c", "d", "e", "d", "c", "b", "a"];
var _pos1 = array_get_index(_array, "d");                 // 3
var _pos2 = array_get_index(_array, "d", 6);              // -1
var _pos3 = array_get_index(_array, "d", -1, -infinity);  // 5
```

- **Notas:** Devuelve `-1` si no lo encuentra.

### `array_contains(array, value, [offset], [length])`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el array **contiene** el valor indicado.
- **Ejemplo:**

*Ejemplo 1*


```gml
var _digits_decimal = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
var _contains = array_contains(_digits_decimal, 3);
show_debug_message("The array contains the digit 3: {0}", _contains);
```

*Ejemplo 2: array of arrays*


```gml
var _a = [0, 1, 2];
var _b = _a;
var _array_of_arrays =
[
    [
        "this", "that", "another thing"
    ],
    _a
];
show_debug_message(array_contains(_array_of_arrays, _a));
show_debug_message(array_contains(_array_of_arrays, _b));
show_debug_message(array_contains(_array_of_arrays, [0, 1, 2]));
show_debug_message(array_contains(_array_of_arrays, ["this", "that", "another thing"]));
```

### `array_contains_ext(array, values, [matchAll], [offset], [length])`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el array contiene los valores de un **array de búsqueda**. Con `matchAll = true` exige que estén todos; con `false`, basta con uno.
- **Ejemplo:**

*Ejemplo 1: comprobar si alguno de los valores dados está en un array*


```gml
hand = ["1", "1", "4", "J", "J", "Q", "7", "10", "K", "8", "7", "8", "5"];
var _high_cards = ["A", "K", "Q", "J"];
var _any_high_cards = array_contains_ext(hand, _high_cards);
show_debug_message(_any_high_cards);
```

*Ejemplo 2: comprobar si todos los valores están en un array*


```gml
inputs = ["left", "right", "left", "left", "up", "down", "right"];
var _required_inputs = ["left", "left", "left"];
var _input_valid = array_contains_ext(inputs, _required_inputs, true);
show_debug_message(_input_valid);
```

### `array_sort(variable, sorttype_or_function)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Ordena el array. El segundo argumento puede ser `true` (ascendente), `false` (descendente) o una **función de comparación** propia. **Modifica el array**.
- **Ejemplo:**

```gml
var _a = [10, 9, 8, 7, 6, 5];

array_sort(_a, function(current, next)
{
    return current - next;
});
```

```gml
var _xx, _yy, _a;

for (var i = 0; i < 10; i++)
{
    _xx = irandom(room_width);
    _yy = irandom(room_height);
    _a[i] = instance_create_layer(_xx, _yy, layer, obj_Bullet);
}

show_debug_message(_a);

var _f = function(inst1, inst2)
{
    return inst1.x - inst2.x;
}

array_sort(_a, _f);
show_debug_message(_a);
```

```gml
[ ref instance 100002,ref instance 100003,ref instance 100004,ref instance 100005,ref instance 100006,ref instance 100007,ref instance 100008,ref instance 100009,ref instance 100010,ref instance 100011 ]
```

```gml
[ ref instance 100009,ref instance 100011,ref instance 100007,ref instance 100002,ref instance 100006,ref instance 100004,ref instance 100008,ref instance 100010,ref instance 100003,ref instance 100005 ]
```

- **Notas:** Con función propia, debe devolver un número negativo, cero o positivo, como el `sort` clásico. Las funciones `_ext` de esta sección no existen para `sort`.

### `array_reverse(array, [offset], [length])`

- **Devuelve:** Array
- **Qué hace:** Devuelve un array **nuevo** con los elementos en orden inverso. El array original no se modifica.
- **Ejemplo:**

```gml
countdown = [5, 4, 3, 2, 1, 0];

countdown_reverse = array_reverse(countdown);
```

- **Notas:** Devuelve un array **nuevo**; para modificar en sitio usa `array_reverse_ext`.

### `array_shuffle(array, [offset], [length])`

- **Devuelve:** Array
- **Qué hace:** Devuelve un array **nuevo** con los elementos mezclados aleatoriamente. El array original no se modifica.
- **Ejemplo:**

```gml
var _array = ["Everyday", "I", "'m", "shuffling"];
var _array_shuffled = array_shuffle(_array);
show_debug_message(_array_shuffled);
```

- **Notas:** Devuelve un array **nuevo**; para modificar en sitio usa `array_shuffle_ext`.

---

## Funciones avanzadas (con callback)


### `array_find_index(array, function, [offset], [length])`

- **Devuelve:** Real (the index of the first element found or -1 if nothing was found)
- **Qué hace:** Devuelve el índice del **primer elemento** para el que la función predicado devuelve `true`, o `-1` si ninguno cumple la condición.
- **Ejemplo:**

```gml
var _f = function(_element, _index)
{
    return (_element > 0);
}

var _array = [-1, -8, -2, -4, 0, 3, 8, 7, 5];
var _index = array_find_index(_array, _f);
```

- **Notas:** Devuelve `-1` si ningún elemento cumple la condición.

### `array_any(array, function, [offset], [length])`

- **Devuelve:** Booleano (true if there is any element in the array for which the predicate returns true, false if there isn't any)
- **Qué hace:** Indica si **al menos un** elemento del array cumple el predicado. Es la forma declarativa de `array_contains` cuando la condición no es una simple igualdad.
- **Ejemplo:**

```gml
var _array =
[
    "apple",
    "banana",
    "coconut",
    "dragonfruit"
]

var _contains_apple = array_any(_array, function(_val, _ind)
{
    return _val == "apple"
});

show_debug_message(_contains_apple); // prints 1 (true)
```

### `array_all(array, function, [offset], [length])`

- **Devuelve:** Booleano (whether the function returned true for all elements in the array or range)
- **Qué hace:** Indica si **todos** los elementos del array cumplen el predicado.
- **Ejemplo:**

```gml
function is_even(element, index)
{
    return (element mod 2 == 0);
}
values = [2, 4, 8, 10, 12, 14, 18, 22, 46];
var all_elements_are_even = array_all(values, is_even);
```

### `array_foreach(array, function, [offset], [length])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Ejecuta una función por **cada elemento** del array. No devuelve nada: se usa por sus efectos secundarios.
- **Ejemplo:**

```gml
var _array =
[
    { x: 4,  y: 5  },
    { x: 12, y: 8  },
    { x: 75, y: 23 }
];

var _set_x_to_index = function(_element, _index)
{
    _element.x = _index;
}

array_foreach(_array, _set_x_to_index);
```

### `array_reduce(array, function, [init], [offset], [length])`

- **Devuelve:** Cualquiera
- **Qué hace:** Reduce el array a un **único valor** aplicando una función acumuladora. El parámetro `init` fija el valor inicial del acumulador.
- **Ejemplo:**

```gml
var _array = [2, 1, 3, 4, 5];

var _min_value = function(_previous, _current, _index)
{
    return min(_previous, _current);
}

var _value = array_reduce(_array, _min_value);
```

- **Notas:** Sin `init`, el acumulador arranca con el primer elemento del array.

### `array_concat(array0, array1, [array2, ... array_n])`

- **Devuelve:** Array (new array with all arrays concatenated)
- **Qué hace:** Devuelve un array nuevo con **todos** los elementos de los arrays que le pases, en el orden indicado. No elimina duplicados.
- **Ejemplo:**

```gml
array_1 = [1, 2, 3];
array_2 = [4, 5, 6];
array_3 = [7, 8, 9];
new_array = array_concat(array_1, array_2, array_3);
```

- **Notas:** A diferencia de `array_union`, **no** elimina duplicados.

### `array_union(array0, [array1, ... array_n])`

- **Devuelve:** Array (the union of the provided arrays)
- **Qué hace:** Devuelve la **unión** de los arrays: todos los elementos, sin duplicados.
- **Ejemplo:**

```gml
a1 = [1, 2, 3, 4, 5];
a2 = [3, 4, 5, 6, 7, 8];
a3 = [5, 6, 7, 8, 9, 10, 11];

a4 = array_union(a1, a2, a3);
```

### `array_intersection(array0, [array1, ... array_n])`

- **Devuelve:** Array (the intersection of the provided arrays)
- **Qué hace:** Devuelve la **intersección** de los arrays: solo los elementos que aparecen en todos ellos.
- **Ejemplo:**

```gml
var _array1 = [1, 1, 2, 7, 12];
var _array2 = [1, 2, 4, 5, 7];
var _array3 = [1, 4, 5, 7];

var _array_intersection = array_intersection(_array1, _array2, _array3);
```

### `array_filter(array, function, [offset], [length])`

- **Devuelve:** Array
- **Qué hace:** Devuelve un array **nuevo** con solo los elementos que cumplen el predicado. El array original no se modifica.
- **Ejemplo:**

```gml
function passed_the_test(element, index)
{
    return element >= 50;
}

scores = [0, 15, 4, 78, 96, 65, 49];
passed = array_filter(scores, passed_the_test);
```

- **Notas:** Devuelve un array **nuevo**; para modificar en sitio usa `array_filter_ext`.

### `array_map(array, function, [offset], [length])`

- **Devuelve:** Array
- **Qué hace:** Devuelve un array **nuevo** con el resultado de aplicar la función a cada elemento. El array original no se modifica.
- **Ejemplo:**

```gml
var _numbers = [1, 2, 3, 4, 5];

var _double = function (_element, _index)
{
    return _element * 2;
}

var _numbers_doubled = array_map(_numbers, _double);
```

- **Notas:** Devuelve un array **nuevo**; para modificar en sitio usa `array_map_ext`.

### `array_unique(array, [offset], [length])`

- **Devuelve:** Array
- **Qué hace:** Devuelve un array **nuevo** sin elementos duplicados. El array original no se modifica.
- **Ejemplo:**

```gml
var _values = ["rock", "paper", "scissors", "rock", "rock", "scissors", "paper", "scissors"];
var _values_unique = array_unique(_values);
```

- **Notas:** Devuelve un array **nuevo**; para modificar en sitio usa `array_unique_ext`.

### `array_copy_while(array, function, [offset], [length])`

- **Devuelve:** Array
- **Qué hace:** Copia elementos a un array nuevo **mientras** el predicado devuelva `true`, y se detiene en cuanto devuelve `false`. A diferencia de `array_filter`, no recorre todo el array.
- **Ejemplo:**

```gml
array = ["1", "2", "3", "STOP", "4", "5", "6", "STOP", "7", "8", "9"];
array_up_to_stop = array_copy_while(array, function(element, index)
{
    return (element != "STOP");
}, -1, -infinity);
```

- **Notas:** Se detiene en el primer `false`: es más eficiente que `array_filter` si buscas un prefijo.

---

## Variantes `_ext` (modifican el array original)


### `array_create_ext(size, function)`

- **Devuelve:** Array
- **Qué hace:** Crea un array del tamaño indicado llamando a una función de retorno por cada índice, y guardando en cada posición lo que devuelva. Ideal para crear arrays de structs sin que todas las posiciones compartan la misma referencia.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _f = function(_index)
{
    return _index + 1;
}
array = array_create_ext(100, _f);
show_debug_message(array);
```

*Ejemplo 2: array de structs*


```gml
create_point = function()
{
    return {x: 0, y: 0};
}
array = array_create_ext(10, create_point);
```

- **Notas:** Es la solución al problema de `array_create` con structs: `array_create_ext(10, function() { return {x: 0, y: 0}; })`.

### `array_filter_ext(array, function, [offset], [length])`

- **Devuelve:** Real (the number of valid elements in the array)
- **Qué hace:** Igual que `array_filter`, pero **modifica el array original** en lugar de devolver uno nuevo, y devuelve el número de elementos válidos.
- **Ejemplo:**

```gml
var _is_even = function(_element, _index) {
    return (_element mod 2) == 0;
}

var _values = [1, 2, 3, 4, 5, 6, 7, 8, 9];
var _valid_elements = array_filter_ext(_values, _is_even, -2, -infinity);
```

### `array_map_ext(array, function, [offset], [length])`

- **Devuelve:** Real (the number of valid elements in the array)
- **Qué hace:** Igual que `array_map`, pero **modifica el array original** en lugar de devolver uno nuevo, y devuelve el número de elementos válidos.
- **Ejemplo:**

```gml
var _values = [7, 4, 11, 9, 12, 21, 17, 1, 2, 3];
elements = array_map_ext(_values, sqr, 2, 5);
```

### `array_unique_ext(array, [offset], [length])`

- **Devuelve:** Real (the number of valid elements in the array)
- **Qué hace:** Igual que `array_unique`, pero **modifica el array original** en lugar de devolver uno nuevo, y devuelve el número de elementos válidos.
- **Ejemplo:**

```gml
values = [1, 1, 2, 3, 4, 5, 5, 6, 7, 8, 8];
valid_values = array_unique_ext(array);
```

### `array_reverse_ext(array, [offset], [length])`

- **Devuelve:** Real (the number of valid elements in the array)
- **Qué hace:** Igual que `array_reverse`, pero **modifica el array original** en lugar de devolver uno nuevo, y devuelve el número de elementos válidos.
- **Ejemplo:**

```gml
values = [1, 2, 3, 4, 8, 7, 6, 5];

array_reverse_ext(values, -4, 4);
```

### `array_shuffle_ext(array, [offset], [length])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Igual que `array_shuffle`, pero **modifica el array original** en lugar de devolver uno nuevo.
- **Ejemplo:**

```gml
var _numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
array_shuffle_ext(_numbers);
show_debug_message(_numbers);
```

---

## Obsoletas (arrays 2D antiguos)


### `array_length_1d(array_index)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la longitud de un array unidimensional. **Obsoleta**: usa `array_length`.
- **Ejemplo:**

```gml
for (var i = array_length_1d(a) - 1; i > -1; i--)
{
    a[i] = -1;
}
```

- **Notas:** **Obsoleta.** Usa `array_length`, que funciona igual en arrays 1D.

### `array_length_2d(array_index, n)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la longitud de la fila `n` de un array 2D. **Obsoleta**: en GML moderno los arrays 2D son arrays de arrays.
- **Ejemplo:**

```gml
for (var i = 0; i < array_height_2d(a); ++i)
{
    for (var j = 0; j < array_length_2d(a, i); ++j)
    {
        a[i, j] = -1;
    }
}
```

- **Notas:** **Obsoleta.** Los arrays 2D modernos son arrays de arrays: usa `array_length(_a[i])`.

### `array_height_2d(array_index)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el número de filas de un array 2D. **Obsoleta**: en GML moderno los arrays 2D son arrays de arrays.
- **Ejemplo:**

```gml
for (var i = 0; i < array_height_2d(a); ++i)
{
    for (var j = 0; j < array_length_2d(a, i); ++j)
    {
        a[i, j] = -1;
    }
}
```

- **Notas:** **Obsoleta.** Los arrays 2D modernos son arrays de arrays: usa `array_length(_a)`.

---

## Receta: array de structs (el error clásico)

```gml
// ❌ MAL: las 10 posiciones comparten el MISMO struct
var _puntos = array_create(10, {x: 0, y: 0});
_puntos[0].x = 5;   // ¡cambia también _puntos[1].x, _puntos[2].x, ...!

// ✅ BIEN: cada posición recibe un struct nuevo
var _puntos = array_create_ext(10, function(_i)
{
    return {x: 0, y: 0};
});
_puntos[0].x = 5;   // solo cambia el primero
```

## Receta: ordenar con una función propia

```gml
var _jugadores =
[
    {nombre: "Ana",  puntos: 120},
    {nombre: "Luis", puntos: 340},
    {nombre: "Marta", puntos: 210}
];

array_sort(_jugadores, function(_a, _b)
{
    return _a.puntos - _b.puntos;   // negativo, cero o positivo
});
```

## Receta: filtrar, transformar y reducir

```gml
var _n = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

var _pares   = array_filter(_n, function(_v, _i) { return _v mod 2 == 0; });
var _doblado = array_map(_n,    function(_v, _i) { return _v * 2; });
var _suma    = array_reduce(_n, function(_acc, _v, _i) { return _acc + _v; }, 0);
```

---

## Funciones de array que NO existen en GML

| Nombre | Alternativa real |
| --- | --- |
| `array_flip()` | `array_reverse()` |
| `array_join()` | `array_concat()` |
| `array_sort_ext()` | No existe. `array_sort` ya modifica el array. |
| `array_resize_ext()` | No existe. |

---

## Fuentes

- [GML Code Reference — GameMaker LTS 2026](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/GML_Reference.htm)
- [Array Functions (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm)
- [Arrays (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Arrays.htm)
- Verificación de cada firma con `gm-cli manual read "<función>"` y contra el manual LTS (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
