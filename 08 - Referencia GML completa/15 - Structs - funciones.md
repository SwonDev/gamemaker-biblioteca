# 15 · Structs y funciones de variables en GML

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23).

> Todas las firmas han sido verificadas contra el manual oficial LTS.

---

## Structs: la estructura de datos recomendada en 2026

Un **struct** es un contenedor de variables que se crea en tiempo de ejecución, se
pasa **por referencia** y lo recolecta el recolector de basura automáticamente. En el
GML moderno sustituye a los `ds_map`.

```gml
// Sintaxis literal
var _jugador =
{
    nombre: "Adrián",
    vidas: 3,
    puntos: 0
};

// Acceso con punto
_jugador.vidas -= 1;

// Acceso dinámico (estructura del propio struct)
_jugador[$ "vidas"] -= 1;
variable_struct_set(_jugador, "vidas", 2);
```

> **Nota:** el accessor de struct es `[$ ...]` (dólar + corchetes). Permite usar el
> nombre de la variable como una expresión cualquiera.

---

## Constructores

Un **constructor** es una función declarada con la palabra clave `constructor` que se
invoca con `new`. Permite crear structs con una forma definida y con métodos propios.

```gml
function Enemigo(_nombre, _vida) constructor
{
    nombre = _nombre;
    vida   = _vida;
    vida_max = _vida;

    recibir_daño = function(_cantidad)
    {
        vida = max(0, vida - _cantidad);
        return vida <= 0;
    };

    static contador = 0;      // miembro estático: compartido por todos
}

var _orco = new Enemigo("Orco", 100);
_orco.recibir_daño(30);

show_debug_message(instanceof(_orco));         // "Enemigo"
show_debug_message(is_instanceof(_orco, Enemigo)); // true
```

### Puntos clave de los constructores

- Los **métodos** definidos dentro del constructor pertenecen al struct.
- Los miembros `static` viven en el **struct estático**, compartido por todas las
  instancias del constructor. No aparecen en `struct_get_names`.
- `instanceof()` devuelve el nombre del constructor; `is_instanceof()` comprueba si un
  struct es de un tipo dado.

---

## Herencia entre structs

GML no tiene `extends` para structs, pero se puede simular con `static_set` o
encadenando constructores:

```gml
function Jefe(_nombre, _vida) constructor
{
    // hereda todo lo de Enemigo
    var _base = new Enemigo(_nombre, _vida);
    static_set(_base, static_get(Enemigo));

    furia = 1.5;
    return _base;
}
```

---

## Serializar structs con constructores

`json_stringify` guarda los datos, pero **no** el constructor. Para reconstruir el
struct con sus métodos, usa el parámetro `filter_func` de `json_parse` o vuelve a
instanciar el constructor a mano.

```gml
// Guardar
var _datos =
{
    nombre: _jugador.nombre,
    nivel:  _jugador.nivel,
    puntos: _jugador.puntos
};
var _json = json_stringify(_datos, true);

// Cargar
var _cargado = json_parse(_json);
```

Para conservar el tipo, la técnica habitual es guardar el nombre del constructor y
reconstruirlo al cargar:

```gml
function guardar(_struct)
{
    return json_stringify(
    {
        tipo: instanceof(_struct),
        datos: _struct
    });
}

function cargar(_json)
{
    var _o = json_parse(_json);
    var _ctor = asset_get_index(_o.tipo);   // el constructor debe ser global
    var _nuevo = new _ctor();
    var _nombres = struct_get_names(_o.datos);
    array_foreach(_nombres, function(_n, _i)
    {
        _nuevo[$ _n] = _o.datos[$ _n];
    });
    return _nuevo;
}
```

---

## Funciones de struct


### `struct_exists(struct, name)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el struct contiene una variable con ese nombre.
- **Ejemplo:**

```gml
if !struct_exists(mystruct, "shields")
{
    mystruct.shields = 0;
}
```

### `struct_get(struct, name)`

- **Devuelve:** Cualquiera (any data type) or undefined (if the named variable does not exist)
- **Qué hace:** Devuelve el valor de la variable indicada del struct, o `undefined` si no existe. Es la alternativa dinámica al acceso con punto.
- **Ejemplo:**

```gml
if (struct_exists(mystruct, "shields"))
{
    var ss = struct_get(mystruct, "shields");
}
else
{
    var ss = -1;
}
```

- **Notas:** El compilador sustituye el nombre de la variable por su hash cuando detecta que es constante en tiempo de compilación, así que el acceso dinámico suele ser innecesario.

### `struct_set(struct, name, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Establece el valor de una variable del struct, **creándola si no existe**.
- **Ejemplo:**

```gml
if (!struct_exists(mystruct, "shields"))
{
    struct_set(mystruct, "shields", 0);
}
```

### `struct_remove(struct, name)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Elimina la variable indicada del struct.
- **Ejemplo:**

```gml
if (struct_exists(mystruct, "shields"))
{
    struct_remove(mystruct, "shields");
}
```

### `struct_get_names(struct)`

- **Devuelve:** Array (each entry is a String)
- **Qué hace:** Devuelve un **array de strings** con los nombres de todas las variables del struct. Es la forma de recorrer un struct dinámicamente.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _my_struct = {a: 7, str: "a string"};

var _arr_names = struct_get_names(_my_struct);
show_debug_message("Variables for struct: " + string(_arr_names));

var _str = "", _len = array_length(_arr_names);
for (var i = 0; i < _len; i++)
{
    _str = _arr_names[i] + ":" + string(struct_get(_my_struct, _arr_names[i]));
    show_debug_message(_str);
}
```

*Ejemplo 2: incluir variables estáticas*


```gml
function vec3(_x, _y, _z) constructor
{
    x = _x;
    y = _y;
    z = _z;

    static add = function(_vec2)
    {
        x += _vec2.x;
        y += _vec2.y;
        z += _vec2.z;
    };
    static dot = function(_vec2)
    {
        return dot_product_3d(x, y, z, _vec2.x, _vec2.y, _vec2.z);
    };
};
var _v1 = new vec3(100, 20, 0);

var _arr_names = struct_get_names(_v1), _arr_names_static = struct_get_names(static_get(_v1));
var _arr_names_all = array_concat(_arr_names, _arr_names_static);
show_debug_message($"Variable names for struct (including static): {_arr_names_all}");
```

- **Notas:** El orden de los nombres **no está garantizado**: no asumas que coincide con el de declaración.

### `struct_names_count(struct_id)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántas variables tiene el struct.
- **Ejemplo:**

```gml
var _num = struct_names_count(mystruct);
show_debug_message("Struct Variables = " + string(_num));
```

### `struct_foreach(struct, func)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Ejecuta una función por cada variable del struct. La función recibe `(nombre, valor)`.
- **Ejemplo:**

```gml
var _inventory = {apples: 17, bananas: 261, oranges: 2, lemons: 5};
struct_foreach(_inventory, function(_name, _value)
{
    show_debug_message($"{_name}: {_value}");
});
```

- **Notas:** La función de retorno recibe `(nombre, valor)` por cada variable.

---

## Acceso por hash (optimización)


### `variable_get_hash(name)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **hash** numérico de un nombre de variable, para usarlo con las funciones `*_from_hash`.
- **Ejemplo:**

```gml
var _the_struct = {a: 77, b: 88, c: 99};
var _varname = choose("a", "b", "c");
var _hash = variable_get_hash(_varname);
var _value = struct_get_from_hash(_the_struct, _hash);
```

### `struct_get_from_hash(struct, hash)`

- **Devuelve:** Cualquiera
- **Qué hace:** Igual que `struct_get`, pero usando el **hash** numérico del nombre en lugar del nombre. Es más rápido si repites el acceso muchas veces.
- **Ejemplo:**

```gml
var _the_struct = {a: 77, b: 88, c: 99};
var _hash = variable_get_hash("a");
var _value = struct_get_from_hash(_the_struct, _hash);
```

- **Notas:** Obtén el hash una vez con `variable_get_hash` y reutilízalo en bucles intensivos.

### `struct_set_from_hash(struct, hash, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Igual que `struct_set`, pero con el **hash** numérico del nombre.
- **Ejemplo:**

```gml
point = {x: 200, y: 100};
hash_x = variable_get_hash("x");
repeat(1000)
{
    struct_set_from_hash(point, hash_x, random(room_width));
}
```

- **Notas:** Obtén el hash una vez con `variable_get_hash` y reutilízalo.

### `struct_exists_from_hash(struct, hash)`

- **Devuelve:** Booleano
- **Qué hace:** Igual que `struct_exists`, pero con el **hash** numérico del nombre.
- **Ejemplo:**

```gml
var _point1 = {x: 5, y: 10};
var _point2 = {x: 5, y: 10, z: 100};
var _hash = variable_get_hash("z");
var _var_exists1 = struct_exists_from_hash(_point1, _hash);
var _var_exists2 = struct_exists_from_hash(_point2, _hash);
show_debug_message($"_point1 has a z: {_var_exists1}");
show_debug_message($"_point2 has a z: {_var_exists2}");
```

- **Notas:** Obtén el hash una vez con `variable_get_hash` y reutilízalo.

### `struct_remove_from_hash(struct, hash)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Igual que `struct_remove`, pero con el **hash** numérico del nombre.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _hash = variable_get_hash("my_first_var");
var _struct =
{
    my_first_var: 398043,
    my_second_var: "Hello!"
};
struct_remove_from_hash(_struct, _hash);

var _arr_names = struct_get_names(_struct);
array_foreach(_arr_names, show_debug_message);
```

*Ejemplo 2: eliminación optimizada de la misma variable en muchos elementos*


```gml
randomise();

arr_party_stats =
[
    {hp: 100, mp: 100},
    {hp: 100, mp: 100},
    {hp: 89, mp: 70}
];
var _to_remove = choose("hp", "mp");
var _hash = variable_get_hash(_to_remove);

var i = 0, _num = array_length(arr_party_stats);
repeat(_num)
{
    struct_remove_from_hash(arr_party_stats[i++], _hash);
}
```

- **Notas:** Obtén el hash una vez con `variable_get_hash` y reutilízalo.

---

## Constructores, herencia y estáticos


### `instanceof(struct_id)`

- **Devuelve:** String or undefined
- **Qué hace:** Devuelve el **nombre del constructor** con el que se creó el struct, como string, o `undefined` si no se creó con un constructor.
- **Ejemplo:**

```gml
function init_struct(_a, _b, _c) constructor
{
    a = _a;
    b = _b;
    c = _c;
}
```

```gml
mystruct = new init_struct(10, 100, "Hello World");
```

```gml
var _name = instanceof(mystruct);
if (is_string(_name))
{
    show_debug_message(_name);
}
```

- **Notas:** Devuelve `undefined` para structs creados con la sintaxis literal `{...}`; solo devuelve nombre si se crearon con un constructor.

### `is_instanceof(struct, constructor)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el struct fue creado con el **constructor** indicado (o con uno que herede de él). Es la forma recomendada de comprobar el tipo de un struct.
- **Ejemplo:**

```gml
function item() constructor {}

function potion() : item() constructor {}

function enemy() constructor {}

var _potion = new potion();

show_debug_message(is_instanceof(_potion, potion)); // true (1)
show_debug_message(is_instanceof(_potion, item)); // true (1)
show_debug_message(is_instanceof(_potion, enemy)); // false (0)
```

- **Notas:** Es la forma correcta de preguntar «¿este struct es un `Enemigo`?», más robusta que comparar con `instanceof`.

### `static_get(struct_or_func_name)`

- **Devuelve:** Struct or undefined (for the root struct)
- **Qué hace:** Devuelve el **struct estático** del struct o función indicada. Los miembros `static` viven ahí, no en la instancia del struct.
- **Ejemplo:**

*Ejemplo 1*


```gml
function counter()
{
    static count = 0;
    return count ++;
}

repeat (10) counter()

// Get static struct of counter()
var _static_counter = static_get(counter);

// Both of these read the same variable
show_debug_message(counter.count); // 10
show_debug_message(_static_counter.count); // 10
```

*Ejemplo 2: subir por la cadena de estáticos*


```gml
function item() constructor
{
    static hello = function()
    {
        show_debug_message("Hello World!");
    }
}
function potion() : item() constructor {}

my_potion = new potion();
var _static_potion = static_get(my_potion);
var _static_parent = static_get(_static_potion);
_static_parent.hello();
```

- **Notas:** Los miembros `static` **no** se copian al clonar ni aparecen en `struct_get_names`.

### `static_set(struct, static_struct)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Reemplaza el struct estático del struct indicado por otro. Es la base para simular herencia entre structs.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _potion = json_parse(_json_string);

show_debug_message(is_instanceof(_potion, potion)); // false (0)

var _static_potion = static_get(potion);
static_set(_potion, _static_potion);

show_debug_message(is_instanceof(_potion, potion)); // true (1)
```

*Ejemplo 2: asignar un struct estático a un struct de datos puro*


```gml
function vec2(_x, _y) constructor
{
    x = _x;
    y = _y;

    static add = function(_vecb)
    {
        x += _vecb.x;
        y += _vecb.y;
    }

    // ...
}

var _a = new vec2(10, 10);
var _b = {x: 4, y: 9};

static_set(_b, static_get(vec2));

_b.add(_a);

show_debug_message(_b);
```

- **Notas:** Permite construir cadenas de herencia a mano; úsalo con cuidado.

### `variable_clone(value, [depth])`

- **Devuelve:** Cualquiera
- **Qué hace:** Devuelve una **copia profunda** del valor, incluidos structs y arrays anidados. El parámetro `depth` limita cuántos niveles se copian.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _the_original = {a: "some text", b: [1, 2, 3, 4, 5], c: 6};
var _the_clone = variable_clone(_the_original);
```

*Ejemplo 2: clonar métodos*


```gml
the_struct =
{
    my_value: 12,
    my_method: function() { show_debug_message($"My value is: {my_value}"); }
}

the_new_struct = variable_clone(the_struct);
the_new_struct.my_value = 24;

the_struct.my_method();
the_new_struct.my_method();
```

*Ejemplo 3: profundidad del clonado*


```gml
array = [["a", "b", "c"], ["d", "e", "f"], {"g": "g", "h": "h", "i": "i"}];
copy0 = variable_clone(array, 0);
copy1 = variable_clone(array, 1);

array[0][0] = "g";
array[0][1] = "m";

array[2][$"h"] = "m";
array[2][$"i"] = "l";

show_debug_message(array);
show_debug_message(copy0);
show_debug_message(copy1);
```

- **Notas:** Sin `depth` (o con un valor negativo) copia todos los niveles. Con `depth = 1` solo copia el nivel superior.

---

## Variables de instancia


### `variable_instance_exists(instance_id, name)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la instancia indicada tiene una variable con ese nombre.
- **Ejemplo:**

```gml
if (!variable_instance_exists(id, "shields"))
{
    shields = 0;
}
```

### `variable_instance_get(instance_id, name)`

- **Devuelve:** Cualquiera (any data type) or undefined (if the named variable does not exist)
- **Qué hace:** Devuelve el valor de una variable de la instancia indicada, o `undefined` si no existe.
- **Ejemplo:**

```gml
if (variable_instance_exists(id, "shields"))
{
    var ss = variable_instance_get(id, "shields");
}
else
{
    var ss = -1;
}
```

- **Notas:** Devuelve `undefined` si la variable no existe. Para distinguir «no existe» de «vale undefined» usa antes `variable_instance_exists`.

### `variable_instance_set(instance_id, name, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Establece el valor de una variable de la instancia indicada, creándola si no existe.
- **Ejemplo:**

```gml
if (!variable_instance_exists(id, "shields"))
{
    variable_instance_set(id, "shields", 0);
}
```

### `variable_instance_get_names(instance_id/global)`

- **Devuelve:** Array (each entry is a string)
- **Qué hace:** Devuelve un array con los nombres de todas las variables de la instancia (o del ámbito `global`).
- **Ejemplo:**

```gml
var str = "";
var array = variable_instance_get_names(id);
show_debug_message("Variables for " + object_get_name(object_index) + string(id));
for (var i = 0; i < array_length(array); i++)
{
    str = array[i] + ":" + string(variable_instance_get(id, array[i]));
    show_debug_message(str);
}
```

### `variable_instance_names_count(instance_id)`

- **Devuelve:** Real (the number of variables or -1 if invalid instance ID)
- **Qué hace:** Devuelve cuántas variables tiene la instancia, o `-1` si el id no es válido.
- **Ejemplo:**

```gml
ins_player = instance_create_depth(0, 0, 0, obj_player);
var _num = variable_instance_names_count(ins_player);
show_debug_message($"The player instance has {_num} variables.");
```

- **Notas:** Devuelve `-1` si el id de instancia no es válido.

---

## Variables globales


### `variable_global_exists(name)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si existe una variable global con ese nombre.
- **Ejemplo:**

```gml
if (!variable_global_exists("enemy_num"))
{
    global.enemy_num = instance_number(obj_Enemey_Parent);
}
```

### `variable_global_get(name)`

- **Devuelve:** Cualquiera (any data type) or undefined (if the named variable does not exist)
- **Qué hace:** Devuelve el valor de una variable global, o `undefined` si no existe.
- **Ejemplo:**

```gml
if (variable_global_exists("enemy_num"))
{
    show_debug_message("enemy_num = " + string(variable_global_get("enemy_num")));
}
```

- **Notas:** Devuelve `undefined` si la variable no existe.

### `variable_global_set(name, val)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Establece el valor de una variable global, creándola si no existe.
- **Ejemplo:**

```gml
if (!variable_global_exists("enemy_num"))
{
    variable_global_set("enemy_num", 0);
}
```

---

## Métodos (method variables)


### `method(struct_ref_or_instance_id, func)`

- **Devuelve:** Método
- **Qué hace:** Crea un **método**: una función ligada a un struct o instancia concreta, de modo que dentro de ella `self` apunta a ese ámbito. Es la base de la programación orientada a objetos en GML.
- **Ejemplo:**

```gml
var _inst = instance_position(mouse_x, mouse_y, obj_enemy);
if (instance_exists(_inst))
{
    enemy_func = method(_inst, enemy_ai);
}
```

- **Notas:** Si le pasas `undefined` como ámbito, obtienes una función global.

### `method_get_self(method)`

- **Devuelve:** Object Instance, Struct, or undefined
- **Qué hace:** Devuelve el ámbito (struct o instancia) al que está ligado el método, o `undefined` si es una función global.
- **Ejemplo:**

```gml
var _self = method_get_self(light_properties);
show_debug_message(string(_self));
```

### `method_get_index(method)`

- **Devuelve:** Script Function
- **Qué hace:** Devuelve la **función índice** subyacente del método, es decir, la función sin ligar a ningún ámbito.
- **Ejemplo:**

```gml
var _index = method_get_index(light_setup);
if (_index != undefined)
{
    show_debug_message(script_get_name(_index));
}
```

### `method_call(method, [array_args], [offset], [num_args])`

- **Devuelve:** Cualquiera (the type returned by the method)
- **Qué hace:** Llama al método pasándole los argumentos como un **array**. Permite invocar métodos construidos dinámicamente.
- **Ejemplo:**

```gml
struct_with_a_method =
{
    show_message: function(message)
    {
        show_debug_message("The message is: {0}", message);
    }
}
var _method = struct_with_a_method.show_message;
method_call(_method, ["Hello World!"]);
```

- **Notas:** Los argumentos se pasan como array: `method_call(_m, [1, 2, 3])`.

### `script_execute(scr, arg0, arg1, arg2, etc.)`

- **Devuelve:** Cualquiera (Will depend on the return value from the script/function being called)
- **Qué hace:** Ejecuta una **Script Function** por su índice o nombre, pasándole argumentos. Es el mecanismo antiguo: en código nuevo es mejor llamar a la función directamente o usar `method_call`.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
script_execute(choose(move_up, move_down, move_left, move_right), irandom(5));
```

*Ejemplo 2: llamar a una función constructora*


```gml
function StructA() constructor
{
    a = 1;
    b = 2;
    c = "Hello";
}
function StructB() constructor
{
    d = 3;
    e = 4;
    f = "!";
}

the_struct = {};
with(the_struct)
{
    script_execute(StructA);
    script_execute(StructB);
}
show_debug_message($"{instanceof(the_struct)} -> {the_struct}");
```

- **Notas:** **Heredada.** En GML moderno puedes guardar funciones en variables y llamarlas directamente; reserva `script_execute` para código antiguo o para scripts referenciados por nombre.

---

## Referencias y handles


### `ref_create(dbgrefOrStruct, dbgrefOrIndex[, index])`

- **Devuelve:** Reference
- **Qué hace:** Crea una **referencia depurable** a una variable de un struct o instancia. Es lo que consumen los controles del *Debug Overlay* (`dbg_slider`, `dbg_watch`, …) para leer y modificar variables en caliente.
- **Ejemplo:**

*Ejemplo 1: referencia básica a una variable de instancia*


```gml
text = "This is some text";
ref_to_text = ref_create(self, "text");
```

*Ejemplo 2: referencia básica a un índice de array*


```gml
array = [1, 2, 3, 4, 5];
ref_to_index = ref_create(self, "array", 2);
```

*Ejemplo 3: referencia compleja*


```gml
the_struct = {a: "text", b: 485};
ref_to_struct = ref_create(self, "the_struct");
ref_to_struct_var = ref_create(ref_to_struct, "a");
```

*Ejemplo 4: referencia compleja a un array*


```gml
array = [3, 4, 1, 7, 8, 2];
index = 4;
ref_to_array = ref_create(self, "array");
ref_to_index = ref_create(self, "index");
ref_to_array_at_index = ref_create(ref_to_array, ref_to_index);
```

- **Notas:** Las variables referenciadas **deben** vivir en un struct o en una instancia: las variables locales (`var`) no pueden mostrarse en el *Debug Overlay*.

### `handle_parse(value_string)`

- **Devuelve:** Handle (or undefined in case of an invalid handle type or an incorrectly formatted string)
- **Qué hace:** Interpreta un string para crear una referencia de tipo **handle**. El formato es `"ref <tipo> <id>"` o `"ref <tipo> <nombre>"`.
- **Ejemplo:**

```gml
sprite = spr_player;
handle_as_string = string(sprite);
handle_from_string = handle_parse(handle_as_string);

show_debug_message($"{sprite} ({typeof(sprite)})");
show_debug_message($"{handle_as_string} ({typeof(handle_as_string)})");
show_debug_message($"{handle_from_string} ({typeof(handle_from_string)})");
```

```gml
ref sprite spr_player (ref)
ref sprite spr_player (string)
ref sprite spr_player (ref)
```

- **Notas:** Devuelve `undefined` si el tipo de handle no es válido o el string está mal formado.

---

## JSON


### `json_stringify(val, [pretty_print], [filter_func])`

- **Devuelve:** String
- **Qué hace:** Convierte un struct o array en un **string JSON**. Con `pretty_print` activado, el resultado sale indentado. Es la función moderna para serializar.
- **Ejemplo:**

*Ejemplo 1*


```gml
var _contents =
{
    version : "1.0.0",
    data:
    {
        coins : 4,
        mana : 15,
        playername : "Gurpreet",
        items :
        [
            ITEM.SWORD,
            ITEM.BOW,
            ITEM.GUITAR
        ]
    }
};

var _json_string = json_stringify(_contents);
```

```gml
{ "data": { "items": [ 0.0, 1.0, 2.0 ], "coins": 4.0, "mana": 15.0, "playername": "Gurpreet" }, "version": "1.0.0" }
```

*Ejemplo 2: impresión formateada*


```gml
var _contents =
{
    version: "1.0.0",
    data:
    {
        coins : 5,
        mana : 0,
        playername : "Bart",
        items :
        [
            ITEM.SWORD,
            ITEM.BOW,
            ITEM.PIANO
        ]
    }
}
var _json_string = json_stringify(_contents, true);
```

```gml
{
  "data":{
    "mana":0.0,
    "playername":"Bart",
    "items":[
      0,
      1,
      2
    ],
    "coins":5.0
  },
  "version":"1.0.0"
}
```

*Ejemplo 3: función de filtro*


```gml
var data =
{
    x: 5.2344,
    y: 10.601,
    last_clicked: undefined,
    values :  [ 2000.1, 30.56, undefined, { slot : 10, skin : undefined } ]
}

var json = json_stringify(data, true, function(key, value)
{
    if (is_real(value)) return round(value);
    if (is_undefined(value)) return 0;
    return value;
});

show_debug_message(json);
```

- **Notas:** Acepta un tercer argumento `filter_func` para decidir qué claves se serializan.

### `json_parse(json, [filter_func], [inhibit_string_convert])`

- **Devuelve:** Struct or Array
- **Qué hace:** Convierte un string JSON en un **struct o array**. Es la función moderna para deserializar, y la única que reconstruye structs con constructores.
- **Ejemplo:**

*Ejemplo 1*


```gml
var json = "{\"myObj\": { \"apples\":10, \"oranges\":12, \"potatoes\":100000, \"avocados\":0 }, \"myArray\":[0, 1, 2, 2, 4, 0, 1, 5, 1]}";

var data = json_parse(json);
show_debug_message(data);
```

```gml
var data = json_parse(json);

// Check if the struct has myObj variable
if (struct_exists(data, "myObj"))
{
    // Check if it's a struct
    if (is_struct(data.myObj))
    {
        // Print all struct members to the log
        var _names = struct_get_names(data.myObj);
        var _str = "";
        for (var i = 0; i < array_length(_names); i++)
        {
            _str = _names[i] + ": " + string(struct_get(data.myObj, _names[i]));
            show_debug_message(_str);
        }
    }
}

// Check if the struct has myArray variable
if (struct_exists(data, "myArray"))
{
    // Check if it's an array
    if (is_array(data.myArray))
    {
        show_debug_message(data.myArray);
    }
}
```

```gml
oranges: 12
potatoes: 100000
avocados: 0
apples: 10
[ 0,1,2,2,4,0,1,5,1 ]
```

*Ejemplo 2: función de filtro*


```gml
var json = "{\"myObj\": { \"apples\":10, \"oranges\":12, \"potatoes\":100000, \"avocados\":0 }, \"myArray\":[0, 1, 2, 2, 4, 0, 1, 5, 1]}";

var data = json_parse(json, function (key, value)
{
    show_debug_message($"Key: {key}, Value: {value}");
    return value;
});
```

```gml
Key: apples, Value: 10
Key: oranges, Value: 12
Key: potatoes, Value: 100000
Key: avocados, Value: 0
Key: myObj, Value: { apples : 10, oranges : 12, potatoes : 100000, avocados : 0 }
Key: 8, Value: 1
Key: 7, Value: 5
Key: 6, Value: 1
Key: 5, Value: 0
Key: 4, Value: 4
Key: 3, Value: 2
Key: 2, Value: 2
Key: 1, Value: 1
Key: 0, Value: 0
Key: myArray, Value: [ 0,1,2,2,4,0,1,5,1 ]
Key: , Value: { myObj : { apples : 10, oranges : 12, potatoes : 100000, avocados : 0 }, myArray : [ 0,1,2,2,4,0,1,5,1 ] }
```

*Ejemplo 3: sobrescribir valores*


```gml
var json = "{\"prices\": [2, 5, 1, 2, 4, 5]}";

var data = json_parse(json, function (key, value)
{
    return is_real(value) ? value * 1000 : value;
});

show_debug_message(data);
```

```gml
{ prices : [ 2000,5000,1000,2000,4000,5000 ] }
```

- **Notas:** Acepta un `filter_func` para transformar valores al leer, y `inhibit_string_convert` para evitar conversiones automáticas de tipos.

### `json_encode(map, [prettify])`

- **Devuelve:** String
- **Qué hace:** Convierte un **DS map** en un string JSON. **Función heredada**: en código nuevo usa `json_stringify`.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
var _hiscore_map, _json;
_hiscore_map = ds_map_create();
for (var i = 0; i < 10; i++)
{
    ds_map_add(_hiscore_map, name[i], score[i]);
}
_json = json_encode(_hiscore_map);
ds_map_destroy(_hiscore_map);

post_request_id = http_post_string($"http://www.angusgames.com/game?game_id={global.game_id}", _json);
```

*Ejemplo 2: jerarquía de tipos de datos mixtos*


```gml
var _map = ds_map_create();
var _list = ds_list_create();

ds_map_add_list(_map, "seasoning", _list);
ds_list_add(_list, "pepper", "salt", "thyme");

_map[? "greeting"] = {parts: ["Hello", "World!"], separator: ", "};
_map[? "food"] = ["bread", "coconut", "mango"];

var _json = json_encode(_map, true);
// ds_map_destroy(_map);

show_debug_message(_json);
```

- **Notas:** Solo funciona con **DS maps**. Para structs usa `json_stringify`.

### `json_decode(string)`

- **Devuelve:** DS Map
- **Qué hace:** Convierte un string JSON en un **DS map** que hay que destruir a mano. **Función heredada**: en código nuevo usa `json_parse`.
- **Ejemplo:**

```gml
var resultMap = json_decode(requestResult);
var list = ds_map_find_value(resultMap, "default");
var size = ds_list_size(list);
for (var n = 0; n < ds_list_size(list); n++)
{
    var map = ds_list_find_value(list, n);
    var curr = ds_map_find_first(map);
    while (is_string(curr))
    {
        global.Name[n] = ds_map_find_value(map, "name");
        curr = ds_map_find_next(map, curr);
    }
}
ds_map_destroy(resultMap);
```

- **Notas:** Devuelve un **DS map**: recuerda destruirlo con `ds_map_destroy` o tendrás una fuga de memoria.

---

## Structs vs. DS maps

| Operación | Struct (2026) | DS map (heredado) |
| --- | --- | --- |
| Crear | `var _s = {};` | `ds_map_create()` |
| Escribir | `_s.clave = v;` | `ds_map_set(m, "clave", v);` |
| Leer | `_s.clave` | `ds_map_find_value(m, "clave")` |
| Borrar | `struct_remove(_s, "clave")` | `ds_map_delete(m, "clave")` |
| Recorrer | `struct_get_names(_s)` | `ds_map_keys_to_array(m)` |
| Destruir | *automático* | `ds_map_destroy(m)` **obligatorio** |
| Constructor | `new MiTipo()` | no existe |
| Herencia | `static_get` / `static_set` | no existe |

---

## Funciones de struct que NO existen en GML

| Nombre | Alternativa real |
| --- | --- |
| `struct_has()` | `struct_exists()` |
| `struct_clear()` | `struct_foreach` + `struct_remove`, o crear un struct nuevo |
| `struct_copy()` | `variable_clone()` |
| `struct_create()` | Sintaxis literal `{}` o `new Constructor()` |

---

## Fuentes

- [GML Code Reference — GameMaker LTS 2026](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/GML_Reference.htm)
- [Variable Functions (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Variable_Functions.htm)
- [Structs & Constructors (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Structs.htm)
- [Method Variables (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Method_Variables.htm)
- [Guide To Using JSON (LTS)](https://manual.gamemaker.io/lts/en/Additional_Information/Guide_To_Using_JSON.htm)
- Verificación de cada firma con `gm-cli manual read "<función>"` y contra el manual LTS (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
