# 04 · Structs y constructores (POO en GML)

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Structs.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Structs/Static_Structs.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Functions/Static_Variables.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Language_Features/new.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Language_Features/delete.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Method_Variables.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Variable_Functions.htm>

---

## 1. Qué es un struct y por qué debería importarte

Un **struct** es una variable que contiene una **colección de otras variables**. A veces se le llama «objeto ligero» (*lightweight object*).

Las variables pueden ser de **cualquier tipo de dato** y se guardan **sin orden particular**. Puedes leerlas y escribirlas tras la declaración, y puedes **añadir variables nuevas** después de haber creado el struct.

```gml
mi_struct =
{
    a : 20,
    b : "Hola Mundo"
};
```

### El struct vs el objeto: la diferencia que importa

| | Struct | Instancia de objeto |
|---|---|---|
| Cómo se crea | `new Constructor()`, literal `{}`, o devuelto por una función | `instance_create_layer()` / `instance_create_depth()` |
| ¿Tiene eventos? | ❌ **No** | ✅ Sí |
| ¿GameMaker los ejecuta solos? | ❌ No. Tienes que llamarlos tú | ✅ Sí, cada step |
| ¿Tiene variables `static`? | ✅ Sí | ❌ No |
| Coste | Mínimo (solo memoria) | Mayor (participa en el game loop) |
| Sprite / dibujo | ❌ No | ✅ Sí |

> ⚠️ **Cuidado con las Object Variables:** no son el equivalente de las variables `static`. No pertenecen al objeto: son **valores por defecto** que se copian a cada instancia antes de que corra el Create.

**¿Cuándo usar struct y cuándo objeto?**

- ¿Necesita dibujarse, colisionar, o reaccionar por sí solo al paso del tiempo? → **Objeto**.
- ¿Son datos puros, configuración, un inventario, un estado, un sistema? → **Struct**.

---

## 2. Crear structs

### 2.1 Struct literal

```gml
mi_struct =
{
    a : 10,
    b : "Hola Mundo",
    c : int64(5),
    d : _xx + 50,              // puede usar expresiones
    e : function(a, b)         // puede contener métodos
        {
            return a + b;
        },
    f : [10, 20, 30, 40, 50],  // puede contener arrays
    g : image_index            // y variables del ámbito que lo define
};
```

Struct vacío:
```gml
mi_struct = {};
```

### ⚠️ La regla de los dos lados de los dos puntos

Esta es la trampa número uno con los struct literales:

> **Todo lo que está a la IZQUIERDA de `:` es una variable DEL STRUCT.**
> **Todo lo que está a la DERECHA se evalúa en el ámbito de quien define el struct.**

```gml
mi_struct =
{
    x : x,      // ← la x de la izquierda es la del struct
    y : y       // ← la y de la derecha es la de la INSTANCIA que define el struct
};
```

**Consecuencia:** no puedes usar variables del struct para definir otras dentro del mismo literal.

```gml
// ❌ ERROR
mi_struct =
{
    a : 10,
    b : 10,
    c : a + b     // a y b se buscan en el ámbito EXTERIOR, no en el struct
};
```

Si necesitas eso, usa un constructor (sección 4) o asígnalo después:

```gml
// ✅
mi_struct = { a : 10, b : 10 };
mi_struct.c = mi_struct.a + mi_struct.b;
```

### 2.2 Shorthand (atajo) cuando el nombre coincide

Si inicializas una variable del struct con una variable **del mismo nombre** del ámbito exterior, puedes omitir el valor:

```gml
var a = 12;
b = 14;

// En vez de esto:
mi_struct = { a : a, b : b, c : 101 };

// Puedes escribir esto:
mi_struct = { a, b, c : 101 };
```

Ambos dan como resultado `mi_struct.a == 12` y `mi_struct.b == 14`.

---

## 3. Acceder a las variables

### 3.1 Notación de punto

```gml
mi_struct =
{
    a : 20,
    b : "Hola Mundo"
};

mi_string = mi_struct.b + string(mi_struct.a);
mi_struct.a += 1;
mi_struct.b = mi_struct.a + 20;
```

### 3.2 Structs anidados

```gml
mi_struct =
{
    a : { aa : "Esto es un ejemplo" },
    b : { bb : "Y otro más" }
};

var _str = mi_struct.a.aa + " " + mi_struct.b.bb;
```

### 3.3 Con `with()`

Cambia el scope al struct:

```gml
with (mi_struct)
{
    a += other.x;    // `other` es quien ejecuta el bloque (la instancia)
}
```

### 3.4 Con el accessor `[$ ]`

Permite acceder por **nombre en string** (lectura y escritura):

```gml
var _valor = mi_struct[$ "x"];      // leer
mi_struct[$ "x"] = 200;             // escribir (crea la variable si no existe)
```

Devuelve `undefined` si la variable no existe.

> 💡 **Rendimiento:** si vas a acceder mucho por nombre, es más rápido obtener el **hash** una vez y usar las funciones por hash:
> ```gml
> var _hash = variable_get_hash("vida");
> struct_set_from_hash(mi_struct, _hash, 100);
> var _v = struct_get_from_hash(mi_struct, _hash);
> ```

### 3.5 Los accessors se pueden encadenar

```gml
var _poder = _frutas[$ "mangos"][0][$ "poder_curacion"];
```

Esto es muchísimo más limpio que la versión con funciones:

```gml
// Equivalente, pero mucho más feo
var _array = struct_get(_frutas, "mangos");
var _props = _array[0];
var _poder = struct_get(_props, "poder_curacion");
```

---

## 4. Constructores: structs con «molde»

Un struct literal está bien para datos sueltos. Para crear **muchos structs con la misma forma**, usas un **constructor**.

### Sintaxis

```gml
function Vector2(_x, _y) constructor
{
    x = _x;
    y = _y;

    static Add = function(_vec2)
    {
        x += _vec2.x;
        y += _vec2.y;
    }
}
```

También con sintaxis de method variable (aunque para herencia hay restricción, ver 4.3):

```gml
Vector2 = function(_x, _y) constructor
{
    x = _x;
    y = _y;

    static Add = function(_vec2)
    {
        x += _vec2.x;
        y += _vec2.y;
    }
}
```

### Uso: `new`

```gml
v2 = new Vector2(10, 10);
```

`v2` ahora contiene un struct con `x`, `y` y el método estático `Add`.

> ⚠️ **No puedes llamar a un constructor sin `new`**: lanza un error fatal.
> La única excepción: llamarlo con `script_execute()` o `script_execute_ext()` sobre un struct ya creado.

### Argumentos opcionales

```gml
function Vector2(_x = 0, _y = 0) constructor
{
    x = _x;
    y = _y;
}

var _vacio = new Vector2();   // x=0, y=0
```

---

## 4.3 Herencia: el operador `:`

Los constructores soportan **herencia simple** (un solo padre).

```gml
function Vector3(_x, _y, _z) : Vector2(_x, _y) constructor
{
    z = _z;

    static Add = function(_vec3)
    {
        x += _vec3.x;
        y += _vec3.y;
        z += _vec3.z;
    }
}
```

**Cómo funciona:**
1. Se ejecuta **primero** el constructor padre (`Vector2`), con los argumentos que le pasas.
2. Después se ejecuta el constructor hijo (`Vector3`).
3. El hijo hereda las variables del padre y añade las suyas.

> ⚠️ **Restricción importante:** con herencia **NO puedes usar la sintaxis de method variable** (`Vector3 = function(...) : Padre(...) constructor`). Solo funciona la sintaxis de **script function** (`function Vector3(...) : Padre(...) constructor`).

### Pasar valores fijos al padre

```gml
function item(danio) constructor
{
    mi_danio = danio;
}

function espada_basica() : item(10) constructor {}

var _espada = new espada_basica();
show_debug_message(_espada.mi_danio);   // 10
```

La espada básica **siempre** hace 10 de daño, porque ese valor se lo pasa al padre sin importar los argumentos propios.

### ⚠️ Los valores por defecto del hijo sobrescriben al padre

```gml
function padre(valor = 10) constructor
{
    show_debug_message(valor);   // imprime 20
}

function hijo(valor = 20) : padre(valor) constructor
{
    show_debug_message(valor);   // imprime 20
}

var _h = new hijo();
```

Ambos imprimen `20`, porque el hijo fijó el valor por defecto en 20 y ese mismo valor se lo pasa al padre.

---

## 5. Comprobar herencia: `is_instanceof()`

```gml
function item() constructor {}
function pocion() : item() constructor {}
function enemigo() constructor {}

var _pocion = new pocion();

show_debug_message(is_instanceof(_pocion, pocion));   // 1 (true)
show_debug_message(is_instanceof(_pocion, item));     // 1 (true)
show_debug_message(is_instanceof(_pocion, enemigo));  // 0 (false)
```

**La lógica:** «una poción ES un objeto», así que devuelve `true` para ambos. Pero **«un objeto NO es una poción»**: si creas `new item()`, `is_instanceof(_item, pocion)` devuelve `false`.

Para obtener el nombre del constructor de un struct concreto: `instanceof()`.

```gml
show_debug_message(instanceof(_pocion));   // el constructor con el que se creó
```

---

## 6. `static`: variables y métodos compartidos

### 6.1 Variables static

Una variable `static` se define **la primera vez que se llama a la función** y **mantiene su valor** a partir de entonces. Solo se puede cambiar desde dentro de la función que la contiene.

```gml
contador = function()
{
    static num = 0;
    return num++;
}

repeat (10)
{
    show_debug_message(contador());
}
// Salida: 0 1 2 3 4 5 6 7 8 9
```

Sin `static`, imprimiría `0` diez veces.

> ⚠️ **No puedes declarar `static` fuera de una función.**

### 6.2 Static en constructores: compartido, NO duplicado

Esta es la clave económica de los structs:

> Las variables `static` de un constructor se inicializan **una sola vez para ese constructor**, y **no se duplican** por cada struct creado.

```gml
function arma() constructor
{
    static numero_de_armas = 0;
    numero_de_armas++;
}

var _arma1 = new arma();
var _arma2 = new arma();

show_debug_message(_arma1.numero_de_armas);   // 2
```

Con 1000 armas creadas, **solo existe una** variable `numero_de_armas` y **una** copia de cada método `static`.

### 6.3 Static methods: por qué importan

```gml
function Vector2(_x, _y) constructor
{
    x = _x;
    y = _y;

    static Add = function(_otro)     // ← static: se crea UNA vez
    {
        x += _otro.x;
        y += _otro.y;
    }
}
```

Sin `static`, cada `new Vector2()` crearía **una nueva función** en memoria. Con `static`, todas las instancias comparten la misma.

> **Regla:** los métodos de un constructor deberían ser `static` **siempre**, salvo que necesites que cada struct tenga su propia versión (por ejemplo, para sobreescribirlo por instancia).

### 6.4 Acceder a los static desde fuera

```gml
function arma() constructor
{
    static numero_de_armas = 0;
    numero_de_armas++;
}

var _a1 = new arma();
var _a2 = new arma();

show_debug_message(arma.numero_de_armas);   // desde el constructor
show_debug_message(_a1.numero_de_armas);    // desde un struct
show_debug_message(_a2.numero_de_armas);    // los tres imprimen lo mismo
```

> ⚠️ **No puedes leer un static de una función que nunca se ha llamado.** Las static se inicializan en la **primera llamada**; intentarlo antes da error y crashea el juego.

### 6.5 Orden de inicialización

Las static se inicializan **antes** del cuerpo de la función, la primera vez que se llama:

```gml
function prueba_static()
{
    show_debug_message(variable_estatica);   // ✅ funciona (aunque esté abajo)
    static variable_estatica = 1000;
}
```

> ⚠️ Funciona, pero **Feather** mostrará un aviso **GM2043**. No lo hagas.

**Consecuencia importante:** no puedes tener statics **condicionales**.

```gml
function f()
{
    if (false)
    {
        static x = 10;   // ❌ Se inicializa igualmente, siempre existe
    }
}
```

### 6.6 Orden con herencia

Las static del **hijo** solo se inicializan cuando el constructor **padre ha terminado por completo**:

```gml
function padre() constructor
{
    static valor = 10;
    show_debug_message(valor);   // imprime 10
}

function hijo() : padre() constructor
{
    static valor = 20;
    show_debug_message(valor);   // imprime 20
}

var _h = new hijo();
// Salida:
// 10   ← del padre
// 20   ← del hijo
```

Cada constructor tiene **su propio** `valor`, porque las static pertenecen al constructor donde se definen.

---

## 7. El Static Struct y la Static Chain (nivel intermedio-avanzado)

### Todo función tiene un static struct

Sus variables `static` viven en un struct que puedes recuperar con `static_get()`:

```gml
function contador()
{
    static cuenta = 0;
    return cuenta++;
}

repeat (10) contador();

var _static_contador = static_get(contador);

show_debug_message(contador.cuenta);          // 10
show_debug_message(_static_contador.cuenta);  // 10  ← la MISMA variable
```

### La cadena estática (Static Chain)

Con herencia, los static structs forman una **cadena** donde cada hijo enlaza con su padre:

```
static_get(hijo)  →  static_hijo
static_get(static_hijo)  →  static_padre   (== static_get(padre))
static_get(static_padre)  →  static raíz
static_get(static raíz)   →  undefined
```

Todos los constructores **sin padre** comparten el mismo struct raíz, que es el que define el `toString` por defecto.

```gml
function item() constructor {}
function pocion() : item() constructor {}

var _p = new pocion();
var _static_pocion = static_get(pocion);

show_debug_message(static_get(item) == static_get(_static_pocion));   // 1 (true)
```

### Cómo el punto resuelve un nombre

Cuando escribes `struct.variable`:

1. Busca una variable **no static** con ese nombre en el struct → si está, la devuelve.
2. Si no, recorre la **static chain**: primero el static struct actual, luego el del padre, y así hacia atrás.
3. Si no la encuentra en ningún sitio → **error**.

```gml
function raiz() constructor
{
    static show = function() { show_debug_message("raiz"); }
}

function hijo() : raiz() constructor {}

function hijo_con_static() : raiz() constructor
{
    static show = function() { show_debug_message("hijo_con_static"); }
}

function hijo_con_func() : raiz() constructor
{
    show = function() { show_debug_message("hijo_con_func"); }
}

var c1 = new hijo();              c1.show();  // "raiz"
var c2 = new hijo_con_static();   c2.show();  // "hijo_con_static"
var c3 = new hijo_con_func();     c3.show();  // "hijo_con_func"
```

### Acceder al static/método del PADRE desde el hijo

```gml
function padre() constructor
{
    static init = function() { show_debug_message("¿Init del padre?"); }
}

function hijo() : padre() constructor
{
    static init = function()
    {
        var _static       = static_get(self);
        var _static_padre = static_get(_static);
        _static_padre.init();          // llama al init() del padre

        show_debug_message("¡Init del hijo!");
    }
}
```

### `static_set()` — aplicación de constructores en desserialización

Su uso recomendado es al **cargar structs desde JSON**: los structs de JSON no pertenecen a ningún constructor, pero puedes «aplicarles» uno.

```gml
var _pocion = json_parse(_json_string);
show_debug_message(is_instanceof(_pocion, pocion));   // 0 (false)

var _static_pocion = static_get(pocion);
static_set(_pocion, _static_pocion);

show_debug_message(is_instanceof(_pocion, pocion));   // 1 (true)
```

Ahora `_pocion` es una instancia de `pocion`, tiene sus static y sus métodos.

> ⚠️ `static_set()` **no hace nada** sobre un *method struct*: los métodos son structs internamente, pero su funcionalidad de static está desactivada para que puedas acceder directamente al static de la función que hay detrás.

---

## 8. `delete` y el recolector de basura

```gml
delete mi_struct;
```

Elimina **esa referencia** concreta al struct. Si era la última, el recolector de basura lo liberará en su siguiente iteración.

**No es estrictamente necesario** (el GC lo hace solo cuando no quedan referencias), pero **prioriza** la liberación: es buena práctica llamarlo para liberar memoria rápido y de forma eficiente.

```gml
// Create event
mi_struct =
{
    pos_x : x,
    pos_y : y,
    contador : 1000
};

// Clean Up event
delete mi_struct;
```

> ⚠️ `delete` solo funciona con **variables**, no con expresiones.

### Cómo funciona el GC con los structs

El recolector de GameMaker es **generacional** e **incremental**:

- Los objetos nuevos nacen en la generación 0 y «envejecen» hacia generaciones superiores.
- Las generaciones antiguas se comprueban con menos frecuencia.
- La limpieza se reparte entre múltiples frames para evitar picos de CPU.

Puedes ajustar el tiempo que el GC dedica por frame:

```gml
gc_target_frame_time(1);   // en milisegundos
```

> ⚠️ **Ojo:** surfaces, estructuras de datos, buffers y otros recursos dinámicos **NO** los recoge el GC: tienen sus propias funciones `*_destroy()` / `*_free()` / `*_delete()`. Si algo tiene función de destrucción, límpialo tú.

---

## 9. `toString()`: structs que se depuran solos

Por defecto, `show_debug_message()` sobre un struct imprime su contenido. Puedes personalizarlo añadiendo un método llamado `toString`:

```gml
mi_struct =
{
    a : 20,
    b : "Hola Mundo",

    toString : function()
    {
        return "Este struct dice " + b + ", " + string(a) + " veces!";
    }
}

show_debug_message(mi_struct);
// → Este struct dice Hola Mundo, 20 veces!
```

Funciona también con `string()` y con `draw_text()`:

```gml
var _str = string(mi_struct);
draw_text(32, 32, _str);

draw_text(32, 64, mi_struct);   // conversión automática
```

> ⚠️ **Con instancias** hay un matiz: `string(self)` llama a `toString()`, pero `string(id)` **no** — imprime `"ref <id>"`. Igual con los IDs devueltos por `instance_create_*()`.

Los **arrays** se convierten automáticamente, sin necesidad de `toString`.

---

## 10. `method()`: reenlazar un método

Un método creado en una instancia o struct queda **ligado** (*bound*) a ella: durante su ejecución, `self` apunta siempre a esa instancia o struct, sin importar desde dónde lo llames.

Puedes cambiar ese enlace con `method()`:

```gml
method(indice_o_funcion, instancia_o_struct)
```

```gml
var _metodo_para_otro = method(mi_funcion, otra_instancia);
_metodo_para_otro();   // se ejecuta con self == otra_instancia
```

### Funciones auxiliares

| Función | Qué hace |
|---|---|
| `is_method(v)` | ¿Es un método? |
| `method(f, obj)` | Crea/reenlaza un método |
| `method_get_self(m)` | Devuelve la instancia/struct al que está ligado |
| `method_get_index(m)` | Devuelve la función de script que hay detrás |
| `method_call(m, args)` | Llama al método pasándole argumentos |

> Los **script functions** (definidos con `function nombre() {}` en un Script) **no están ligados** a ningún contexto: su `method_get_self()` devuelve `undefined` hasta que los reenlazas con `method()`.

---

## 11. Structs vs Instancias: cuándo usar cada uno

| Necesitas… | Usa |
|---|---|
| Dibujar un sprite | Instancia |
| Colisiones | Instancia |
| Reaccionar a eventos del motor | Instancia |
| Un ítem del inventario | Struct |
| Configuración / balance del juego | Struct |
| Un estado de máquina de estados | Struct |
| Un nodo de pathfinding | Struct |
| Datos de guardado (JSON) | Struct |
| Miles de elementos sin dibujo | Struct |

---

## 12. Ejemplos prácticos

### Ejemplo A: Sistema de entidades con herencia

```gml
/// @desc Constructor base para cualquier entidad con vida
function Entidad(_vida_max) constructor
{
    vida_max = _vida_max;
    vida     = _vida_max;
    muerto   = false;

    static recibir_danio = function(_cantidad)
    {
        vida -= _cantidad;
        if (vida <= 0)
        {
            vida   = 0;
            muerto = true;
            al_morir();
        }
    }

    static curar = function(_cantidad)
    {
        vida = min(vida + _cantidad, vida_max);
    }

    static al_morir = function()
    {
        show_debug_message("Una entidad ha muerto");
    }

    static get_porcentaje_vida = function()
    {
        return vida / vida_max;
    }
}

/// @desc Un enemigo: hereda de Entidad y añade daño de contacto
function Enemigo(_vida_max, _danio) : Entidad(_vida_max) constructor
{
    danio_contacto = _danio;

    // Sobrescribimos el comportamiento del padre
    static al_morir = function()
    {
        show_debug_message("Enemigo derrotado");
    }
}

// Uso
var _slime = new Enemigo(30, 5);
_slime.recibir_danio(10);
show_debug_message(_slime.vida);                      // 20
show_debug_message(_slime.get_porcentaje_vida());     // 0.66...
show_debug_message(is_instanceof(_slime, Entidad));   // 1
```

### Ejemplo B: Inventario con structs

```gml
/// @desc Un slot del inventario
function SlotInventario(_item, _cantidad = 1) constructor
{
    item     = _item;
    cantidad = _cantidad;

    static agregar = function(_n = 1)
    {
        cantidad += _n;
    }

    static quitar = function(_n = 1)
    {
        cantidad -= _n;
        if (cantidad <= 0)
        {
            cantidad = 0;
            item = undefined;
        }
    }

    static esta_vacio = function()
    {
        return is_undefined(item) || cantidad <= 0;
    }
}

/// @desc El inventario completo
function Inventario(_tamano = 20) constructor
{
    slots = array_create(_tamano, undefined);

    static agregar_item = function(_item, _cantidad = 1)
    {
        // 1. ¿Hay un slot con este item que pueda apilar?
        for (var i = 0; i < array_length(slots); i++)
        {
            var _slot = slots[i];
            if (!is_undefined(_slot) && _slot.item == _item)
            {
                _slot.agregar(_cantidad);
                return true;
            }
        }

        // 2. Si no, buscamos un hueco libre
        for (var i = 0; i < array_length(slots); i++)
        {
            if (is_undefined(slots[i]))
            {
                slots[i] = new SlotInventario(_item, _cantidad);
                return true;
            }
        }

        return false;   // inventario lleno
    }

    static contar_item = function(_item)
    {
        var _total = 0;
        for (var i = 0; i < array_length(slots); i++)
        {
            var _slot = slots[i];
            if (!is_undefined(_slot) && _slot.item == _item)
            {
                _total += _slot.cantidad;
            }
        }
        return _total;
    }

    // Serialización para guardar partida
    static a_json = function()
    {
        var _datos = [];
        for (var i = 0; i < array_length(slots); i++)
        {
            var _slot = slots[i];
            if (is_undefined(_slot)) continue;

            array_push(_datos, {
                item     : _slot.item,
                cantidad : _slot.cantidad
            });
        }
        return json_stringify(_datos);
    }
}

// Uso
var _inv = new Inventario(10);
_inv.agregar_item("pocion", 3);
_inv.agregar_item("pocion", 2);
show_debug_message(_inv.contar_item("pocion"));   // 5
```

### Ejemplo C: Sistema de datos / configuración balanceada

```gml
/// @desc Tabla de datos de armas (se crea UNA vez, al inicio)
function DatosArmas() constructor
{
    static armas = {};

    static registrar = function(_id, _nombre, _danio, _velocidad, _sprite)
    {
        armas[$ _id] = {
            id        : _id,
            nombre    : _nombre,
            danio     : _danio,
            velocidad : _velocidad,
            sprite    : _sprite
        };
    }

    static obtener = function(_id)
    {
        if (!struct_exists(armas, _id)) { return undefined; }
        return armas[$ _id];
    }

    static todos_los_ids = function()
    {
        return struct_get_names(armas);
    }
}

// En un Script de configuración (scope global)
global.datos_armas = new DatosArmas();
with (global.datos_armas)
{
    registrar("espada_corta", "Espada corta", 10, 1.0, spr_espada_corta);
    registrar("hacha_guerra", "Hacha de guerra", 25, 0.6, spr_hacha);
    registrar("daga_rapida",  "Daga rápida",     6,  1.8, spr_daga);
}

// Consulta desde cualquier parte
var _datos = global.datos_armas.obtener("hacha_guerra");
show_debug_message(_datos.nombre);   // "Hacha de guerra"
```

> Fíjate en el patrón: **`static armas`** se crea una sola vez y se comparte; el acceso por string usa el accessor `[$ ]`. Y `with (global.datos_armas)` te permite registrar sin repetir el prefijo.

---

## 13. Funciones útiles para structs

| Función | Qué hace |
|---|---|
| `struct_exists(s, "nombre")` | ¿Existe esa variable? |
| `struct_get(s, "nombre")` | Lee una variable por nombre |
| `struct_set(s, "nombre", valor)` | Escribe una variable por nombre |
| `struct_remove(s, "nombre")` | Elimina una variable |
| `struct_get_names(s)` | Array con los nombres de las variables |
| `struct_names_count(s)` | Cuántas variables tiene |
| `struct_foreach(s, funcion)` | Itera sobre las variables |
| `is_instanceof(s, constructor)` | ¿Pertenece a ese constructor o hereda de él? |
| `instanceof(s)` | Devuelve el constructor con el que se creó |
| `static_get(f)` | El static struct de una función/constructor |
| `static_set(s, static_struct)` | Cambia el static struct de un struct |
| `variable_clone(v)` | Copia profunda (structs y arrays incluidos) |
| `variable_get_hash("nombre")` | Hash de un nombre (para acceso rápido) |
| `struct_get_from_hash(s, hash)` | Lee por hash |
| `struct_set_from_hash(s, hash, v)` | Escribe por hash |
| `struct_exists_from_hash(s, hash)` | Comprueba por hash |
| `struct_remove_from_hash(s, hash)` | Elimina por hash |

> 💡 **Optimización del compilador:** el compilador sustituye los nombres de variables en estas funciones por su **hash** cuando detecta que el nombre es una constante en tiempo de compilación. Es decir, `struct_get(s, "vida")` es tan rápido como la versión con hash.

---

## Resumen

1. Un **struct** es un contenedor de variables, ligero y **por referencia**.
2. Los **constructores** (`function X() constructor` + `new X()`) te dan structs con molde y métodos.
3. **Herencia** con `:` — pero solo con sintaxis de script function, no de method variable.
4. **`static`** = compartido entre todos los structs del constructor. Úsalo siempre para los métodos.
5. `is_instanceof()` te dice si un struct «es» de un tipo (incluida la herencia).
6. **`delete`** prioriza la liberación; el GC hace el resto.
7. `static_get()` / `static_set()` te dan acceso a la cadena estática (clave para desserializar JSON).
8. `toString()` hace que tus structs se depuren solos.
