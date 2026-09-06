# 05 · Arrays y estructuras de datos

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Arrays.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Array_Functions.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Data_Structures/Data_Structures.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Accessors.htm>

---

## 0. La recomendación oficial primero

Antes de aprender las estructuras de datos, lee esto del manual:

> ⚠️ *«It is recommended to use **arrays** and **structs** over DS lists and maps, as they now have similar functionality, are easier to use and are **garbage collected automatically**.»*

**Traducción:** en 2026, DS lists y DS maps siguen existiendo y funcionando, pero **GameMaker recomienda arrays y structs**. Son más fáciles, tienen funciones equivalentes y —lo más importante— **se limpian solos**.

| | Arrays / Structs | Estructuras de datos (DS) |
|---|---|---|
| Limpieza de memoria | ✅ **Automática** (garbage collector) | ❌ Manual (`ds_*_destroy()`) |
| Riesgo de memory leak | Bajo | Alto si te olvidas de destruir |
| Sintaxis | Limpia (`a[0]`, `s.campo`) | Verbosa (`ds_list_find_value(l, 0)`) |
| Funcionalidad | Equivalente en casi todo | Algunas cosas únicas |
| Serialización JSON | ✅ Nativa | ⚠️ Parcial (`json_encode` para list/maps) |

**¿Cuándo siguen siendo útiles las DS?** Principalmente para **DS grids** (si haces cosas de grilla muy intensivas) y **DS priority queues** (no tienen equivalente directo en arrays).

---

## 1. Arrays

Un array es una variable que guarda **múltiples valores** en una «lista».

```gml
numeros = [0, 1, 2, 3, 4, 5];
frutas  = ["Manzanas", "Naranjas", "Mangos"];
```

Se accede por un **entero que empieza en 0**:

```gml
primera_fruta  = frutas[0];
segunda_fruta  = frutas[1];
```

> ⚠️ **Los arrays SIEMPRE empiezan en 0 y los índices nunca pueden ser negativos.**

### 1.1 Crear arrays

```gml
// Vacío: le dices a GameMaker "esto es un array"
mi_array = [];

// Con tamaño fijo y valor inicial
mi_array = array_create(5, 0);       // [0, 0, 0, 0, 0]

// Con valores conocidos
mi_array = ["Steve", 36, "Calle Falsa 123"];
```

> ⚠️ **Si accedes a una posición de un array vacío, obtienes un error.**

#### ¿Cómo inicializar eficientemente?

Si inicializas con un bucle, hazlo **hacia atrás**:

```gml
// ✅ Óptimo: reserva memoria del tamaño exacto de una vez
var i = 9;
repeat (10)
{
    array[i] = 0;
    i -= 1;
}
```

```gml
// ⚠️ Menos óptimo: realoca memoria 10 veces (una por cada elemento)
for (var i = 0; i < 10; i++)
{
    array[i] = 0;
}
```

Para arrays pequeños la diferencia es despreciable; para los grandes, importa.

> ⚠️ **Excepción: HTML5.** En ese target debes inicializar **en orden ascendente** desde 0.

> 💡 En la práctica, usa `array_create()`: ya está optimizado.

### 1.2 Límites del array

```gml
mi_array = array_create(5, 0);
var _v = mi_array[6];   // ❌ CRASH
```
Cinco posiciones (0-4); pedir la 6 (índice 5) o superior revienta el juego.

### 1.3 Arrays multidimensionales

Un array 2D es **un array dentro de otro array**.

```gml
array[0][0] = 0;
array[0][1] = 1;
array[0][2] = 2;

array[1][0] = 3;
array[1][1] = 4;
array[1][2] = 5;
```

Inicialización anidada en una sola sentencia:

```gml
tabla =
[
    ["Manzana", 10, 2],
    ["Naranja",  5, 2],
    ["Mango",   15, 4]
];
```

Puedes tener 3, 4 o más dimensiones:

```gml
array[0][0][0] = 1;      // 3D
array[0][0][0][0] = 1;   // 4D
```

**Cada dimensión puede tener distinta longitud:**

```gml
array[0][0] = 1;   // array[0] tiene 2 slots
array[0][1] = 2;
array[1][0] = "uno";    // array[1] tiene 4 slots
array[1][1] = "dos";
array[1][2] = "tres";
array[1][3] = "cuatro";
array[2][0] = "1";      // array[2] tiene 3 slots
array[2][1] = "2";
array[2][2] = "3";
```

### 1.4 Eliminar arrays

El recolector de basura limpia los arrays que pierden sus referencias automáticamente.

```gml
a = undefined;   // prioriza la limpieza: el GC lo recoge en el siguiente ciclo
```

> ⚠️ **Ojo con esto:** si el array guarda referencias a recursos dinámicos (sistemas de partículas, buffers, estructuras de datos), **esos sí debes destruirlos a mano** antes de borrar el array, destruir la instancia o terminar la room.

---

## 2. Arrays como argumentos: el cambio de comportamiento

### El comportamiento ACTUAL (2026)

Los arrays se pasan **por referencia** y **modificarlos dentro de la función modifica el original**:

```gml
modificar_array = function(array)
{
    array[0] = 2;
    array[1] = 4;
    array[2] = 6;
}

mi_array = [100, 4, 214];
modificar_array(mi_array);
show_debug_message(mi_array);   // [2, 4, 6]  ← ¡el original cambió!
```

### El comportamiento ANTIGUO (Copy on Write) — DEPRECADO

En versiones anteriores, modificar el array dentro de la función creaba una **copia temporal**. Para que el cambio se aplicara tenías dos opciones:

```gml
// Opción 1: devolver el array y reasignarlo
mi_array = [1, 2, 4, 8, 16];
mi_array = hacer_algo(mi_array);

function hacer_algo(array)
{
    array[1] = 200;
    return array;
}

// Opción 2: usar el accessor @
function hacer_algo(array)
{
    array[@ 1] = 200;   // modifica el array referenciado directamente
}
```

> ⚠️ **Copy on Write está deprecado.** Solo se activa si habilitas explícitamente **«Enable Copy on Write behaviour for Arrays»** en las *General Game Options*.
>
> Si está desactivado (por defecto y recomendado), **el accessor `@` no es necesario**.
> Si está activado, `@` te permite desactivarlo puntualmente para una sentencia concreta.

**En resumen:** escribe código para el comportamiento nuevo. No uses `@` salvo que sepas que vas a activar Copy on Write.

---

## 3. Accessors (operadores de acceso corto)

Los accessors te permiten acceder a estructuras de datos y structs con una sintaxis parecida a la de los arrays.

| Tipo | Accessor | Sintaxis |
|---|---|---|
| DS List | `\|` | `lista[\| indice]` |
| DS Map | `?` | `mapa[? clave]` |
| DS Grid | `#` | `grid[# xpos, ypos]` |
| Struct | `$` | `struct[$ "nombre"]` |
| Array | `@` | `array[@ i]` — **solo con Copy on Write activado** |

### Ejemplos

```gml
// DS List
ds = ds_list_create();
var _i = 0;
repeat (10)
{
    ds[| _i++] = irandom(9);
}
var _valor = ds[| 5];
```

> ⚠️ Si asignas un índice **mayor** que el tamaño de la lista, la lista **se expande** e inicializa las posiciones intermedias a `0`.
> Si lees fuera de rango, obtienes `undefined`.

```gml
// DS Map (la clave puede ser de CUALQUIER tipo, incluso un struct)
ds = ds_map_create();
ds[? "Nombre"]   = "Hamish";
ds[? "Empresa"]  = "MacSeweeny Games";
ds[? "Juego"]    = "Catch The Haggis";

var _v = ds[? "Nombre"];   // undefined si la clave no existe
```

```gml
// DS Grid
ds = ds_grid_create(10, 10);
ds_grid_clear(ds, 0);
ds[# 3, 4] = 1;
var _v = ds[# mouse_x div 16, mouse_y div 16];
```

```gml
// Struct
var _vida = struct[$ "vida"];
struct[$ "puntuacion"] = 100;   // crea la variable si no existe
```

### Encadenar accessors (la gran ventaja)

```gml
var _poder = _frutas[$ "mangos"][0][$ "poder_curacion"];

// Más ejemplos del manual:
var _a = datos[? "listas"][| 0][# 0, 0];
datos[| 0][10] = 100;
datos[0][| 10][# 3, 4][? "clave"] = "hola mundo";
```

Esto hace que los bucles (`for`) sobre estructuras anidadas sean muchísimo más legibles.

---

## 4. Funciones de arrays

### 4.1 Básicas

| Función | Qué hace |
|---|---|
| `array_create(tamaño, [valor])` | Crea un array de tamaño fijo |
| `array_copy(dest, d_ind, orig, o_ind, longitud)` | Copia un rango |
| `array_equals(a1, a2)` | ¿Son iguales? |
| `array_get(a, ind)` / `array_set(a, ind, v)` | Leer / escribir por función |
| `array_push(a, v...)` | Añade al **final** (acepta varios) |
| `array_pop(a)` | Quita y devuelve el **último** |
| `array_shift(a)` | Quita y devuelve el **primero** |
| `array_insert(a, ind, v...)` | Inserta en una posición |
| `array_delete(a, ind, cantidad)` | Borra un rango |
| `array_get_index(a, v)` | Índice de un valor (o -1) |
| `array_contains(a, v)` | ¿Contiene ese valor? |
| `array_sort(a, funcion)` | Ordena (con función comparadora) |
| `array_reverse(a)` | Invierte el orden |
| `array_shuffle(a)` | Baraja aleatoriamente |
| `array_length(a)` | Número de elementos |
| `array_resize(a, nuevo_tam)` | Cambia el tamaño |
| `array_first(a)` / `array_last(a)` | Primero / último elemento |

> ⚠️ `array_length_1d`, `array_length_2d` y `array_height_2d` están **DEPRECADAS**. Usa `array_length()`.

### 4.2 Avanzadas (funcional)

| Función | Qué hace |
|---|---|
| `array_find_index(a, predicado)` | Índice del primero que cumple |
| `array_any(a, predicado)` | ¿Alguno cumple? |
| `array_all(a, predicado)` | ¿Todos cumplen? |
| `array_foreach(a, funcion)` | Ejecuta algo por cada elemento |
| `array_reduce(a, funcion, [inicial])` | Reduce a un único valor |
| `array_concat(a1, a2, ...)` | Concatena arrays |
| `array_union(...)`, `array_intersection(...)` | Operaciones de conjuntos |
| `array_filter(a, predicado)` | Filtra (devuelve copia) |
| `array_map(a, funcion)` | Transforma (devuelve copia) |
| `array_unique(a)` | Elimina duplicados |

### 4.3 Extendidas (`_ext`)

`array_create_ext`, `array_filter_ext`, `array_map_ext`, `array_unique_ext`, `array_reverse_ext`, `array_shuffle_ext`

> **Diferencia clave:** las versiones `_ext` modifican **el array original** en vez de devolver una copia. Úsalas cuando trabajes con arrays grandes y quieras evitar la copia.

---

## 5. Métodos callback, predicados, offset y longitud

### Callback

Un callback es un **método** que le pasas a la función del array. GameMaker lo ejecuta por cada elemento pasándole **dos argumentos**:

1. El **valor** del elemento.
2. El **índice** del elemento.

```gml
array_foreach(mi_array, function(_valor, _indice)
{
    show_debug_message($"[{_indice}] = {_valor}");
});
```

### Predicado

Un callback que solo devuelve `true` o `false`. Indica si un elemento **cumple una condición**.

```gml
var _array = ["manzana", "banana", "coco", "pitahaya"];

var _tiene_manzana = array_any(_array, function(_val, _ind)
{
    return _val == "manzana";
});

show_debug_message(_tiene_manzana);   // 1 (true)
```

### Offset y longitud (recorrer solo una parte)

La mayoría de las funciones avanzadas aceptan dos parámetros extra:

**Offset** — índice (base 0) donde empieza la operación.
- Puede ser **negativo**: `-1` es el último elemento, `-2` el penúltimo…
- Se **limita** (clamp) entre 0 y el último elemento.

**Longitud** — cuántos elementos se procesan desde el offset.
- Puede ser **negativa**, y entonces la operación va **hacia atrás**.
- `infinity` llega hasta el final; `-infinity` hasta el principio.

```gml
var _a = [10, 20, 30, 40, 50, 60];

// offset 3, longitud 3 → elementos 3, 4, 5
// offset 3, longitud -3 → elementos 3, 2, 1
```

> ⚠️ Si la función devuelve una versión modificada, **solo devuelve los elementos sobre los que operó**. El resto se descarta.
>
> ⚠️ Todas las funciones con offset avisan por consola si intentas acceder fuera de rango.

### Ejemplos prácticos

```gml
var _inventario = ["espada", "pocion", "escudo", "pocion", "llave"];

// ¿Tengo pociones?
var _tengo = array_contains(_inventario, "pocion");   // true

// Cuántas pociones (con reduce)
var _total = array_reduce(_inventario, function(_acum, _val, _ind)
{
    return _acum + (_val == "pocion" ? 1 : 0);
}, 0);

// Quitar todas las pociones
var _sin_pociones = array_filter(_inventario, function(_val, _ind)
{
    return _val != "pocion";
});

// Sin duplicados
var _unicos = array_unique(_inventario);

// Ordenar de mayor a menor
var _nums = [3, 1, 4, 1, 5, 9, 2, 6];
array_sort(_nums, function(_a, _b)
{
    return _b - _a;   // negativo si _a va antes
});
```

---

## 6. Estructuras de datos (DS)

### Regla universal

Todas funcionan igual:
1. **Creas** la estructura y guardas la referencia en una variable.
2. Usas esa referencia en las llamadas.
3. La **destruyes** cuando terminas.

> ⚠️ *«As with all dynamic resources, data structures take up memory and so should **always** be destroyed when no longer needed to prevent memory leaks which will slow down and eventually crash your game.»*

### 6.1 DS Lists

Lista ordenada. Acceso por índice.

```gml
var _l = ds_list_create();
ds_list_add(_l, "espada", "escudo", "pocion");
var _primero = ds_list_find_value(_l, 0);   // "espada"
var _tam = ds_list_size(_l);                // 3

// Con accessor (más limpio)
_l[| 0] = "espada oxidada";

ds_list_destroy(_l);
_l = -1;
```

**Cuándo usarla:** cuando necesitas insertar/borrar en medio con frecuencia y el orden importa. En casi todo lo demás, un array es mejor.

### 6.2 DS Maps

Pares clave → valor. La **clave puede ser de cualquier tipo** (incluido un struct).

```gml
var _m = ds_map_create();
_m[? "vida"]    = 100;
_m[? "nombre"]  = "Goblin";
_m[? "nivel"]   = 5;

var _vida = _m[? "vida"];   // undefined si no existe

ds_map_destroy(_m);
_m = -1;
```

**Cuándo usarla:** datos con claves dinámicas (que no sabes de antemano). Si las claves son fijas, **un struct es mejor**.

### 6.3 DS Grids

Una cuadrícula 2D de tamaño fijo.

```gml
var _g = ds_grid_create(10, 10);
ds_grid_clear(_g, 0);
_g[# 3, 4] = 1;

var _ancho  = ds_grid_width(_g);
var _alto   = ds_grid_height(_g);

ds_grid_destroy(_g);
_g = -1;
```

**Cuándo usarla:** mapas de tiles lógicos, pathfinding en grid, sistemas de niebla de guerra. Aquí **sí** tiene ventajas reales sobre un array 2D (funciones de búsqueda, redimensionado, operaciones por región).

### 6.4 DS Stacks — LIFO

*Last In, First Out*. Como una pila de platos.

```gml
var _s = ds_stack_create();
ds_stack_push(_s, "estado_menu");
ds_stack_push(_s, "estado_juego");

var _actual = ds_stack_pop(_s);   // "estado_juego"
var _tope   = ds_stack_top(_s);   // "estado_menu" (mira sin sacar)

ds_stack_destroy(_s);
_s = -1;
```

**Cuándo usarla:** deshacer/rehacer, máquinas de estados anidadas, navegación hacia atrás.

### 6.5 DS Queues — FIFO

*First In, First Out*. Como una cola del supermercado.

```gml
var _q = ds_queue_create();
ds_queue_enqueue(_q, "mensaje_1");
ds_queue_enqueue(_q, "mensaje_2");

var _siguiente = ds_queue_dequeue(_q);   // "mensaje_1"

ds_queue_destroy(_q);
_q = -1;
```

**Cuándo usarla:** colas de mensajes, sistemas de diálogo, procesamiento por turnos, colas de eventos.

### 6.6 DS Priority Queues

Cada elemento tiene una **prioridad**; sale primero el de mayor prioridad.

```gml
var _pq = ds_priority_create();
ds_priority_add(_pq, "curarse",  1);
ds_priority_add(_pq, "huir",    10);
ds_priority_add(_pq, "atacar",   5);

var _primero = ds_priority_delete_max(_pq);   // "huir" (prioridad 10)

ds_priority_destroy(_pq);
_pq = -1;
```

**Cuándo usarla:** **pathfinding A\*** (es su uso clásico), IA con prioridades, sistemas de eventos ordenados por urgencia. **No tiene equivalente directo en arrays.**

### 6.7 Funciones generales

```gml
ds_exists(indice, tipo);       // ¿Existe?
ds_set_precision(precision);   // para evitar errores de redondeo
```

---

## 7. Copiar: superficial vs profundo

### Arrays

```gml
var _a = [1, 2, 3];
var _b = _a;            // ❌ NO es una copia: es la misma referencia
_b[0] = 99;
show_debug_message(_a[0]);   // 99
```

**Copia superficial de un array:**

```gml
var _copia = array_create(array_length(_a));
array_copy(_copia, 0, _a, 0, array_length(_a));
```

**Copia profunda (structs y arrays anidados incluidos):**

```gml
var _copia = variable_clone(_a);
```

### Structs

```gml
var _s1 = { vida: 100, items: ["espada"] };
var _s2 = variable_clone(_s1);   // copia profunda

_s2.items[0] = "hacha";
show_debug_message(_s1.items[0]);   // "espada" ← intacto
```

### Estructuras de datos

```gml
ds_list_copy(dest, orig);
ds_map_copy(dest, orig);
ds_grid_copy(dest, orig);
```

> ⚠️ Estas copias son de un nivel: los valores que sean a su vez estructuras de datos **se copian como referencias**, no en profundidad.

---

## 8. Serialización (guardar y cargar)

### Arrays y structs → JSON

```gml
var _datos =
{
    version : "1.0.0",
    datos   :
    {
        monedas    : 4,
        mana       : 15,
        nombre     : "Gurpreet",
        items      : [ITEM.ESPADA, ITEM.ARCO, ITEM.GUITARRA]
    }
};

var _json = json_stringify(_datos);          // sin formato
var _json_bonito = json_stringify(_datos, true);  // con indentación
```

```gml
var _cargado = json_parse(_json);
show_debug_message(_cargado.datos.monedas);   // 4
```

### Lo que debes saber de la serialización

- ⚠️ **El orden de las variables del struct no está garantizado.**
- ⚠️ Los assets y estructuras de datos **no** se serializan con su contenido: se guarda la **referencia** (handle). Al parsear se reconvierten en referencias de runtime.
- ⚠️ Eso **no sirve entre sesiones del juego**: los índices se reciclan. Los assets se guardan **por nombre**, así que el enlace sobrevive mientras no cambies el nombre del asset.
- `null` en JSON se parsea como `undefined`.
- Profundidad máxima de anidamiento al parsear: **128**.
- Parsear algo inválido (no string, o JSON malformado) lanza una **excepción**.
- Para serializar **DS lists y DS maps**, usa `json_encode()`.
- Puedes pasar una **función filtro** a ambas: `function(clave, valor) -> nuevo_valor`.
- Puedes desactivar la reconversión de strings a referencias con el tercer argumento de `json_parse()`:

```gml
var _datos = json_parse(_json, undefined, true);   // inhibit_string_convert
```

### Estructuras de datos → JSON

```gml
var _json = json_encode(mi_ds_map);
```

> `json_encode()` está pensado específicamente para DS lists y DS maps.

### Guardar a archivo

```gml
// GUARDAR
function guardar_partida(_ruta, _datos)
{
    var _json = json_stringify(_datos, true);
    var _buff = buffer_create(string_byte_length(_json) + 1, buffer_grow, 1);
    buffer_write(_buff, buffer_string, _json);
    buffer_save(_buff, _ruta);
    buffer_delete(_buff);
}

// CARGAR
function cargar_partida(_ruta)
{
    if (!file_exists(_ruta)) { return undefined; }

    var _buff = buffer_load(_ruta);
    var _json = buffer_read(_buff, buffer_string);
    buffer_delete(_buff);

    return json_parse(_json);
}
```

---

## 9. Tabla comparativa

| Característica | Array | Struct | DS List | DS Map | DS Grid | DS Stack | DS Queue | DS Priority Q |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **GC automático** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Acceso por índice | ✅ | ❌ | ✅ | ❌ | ✅ (x,y) | ❌ | ❌ | ❌ |
| Acceso por clave | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Tamaño dinámico | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| Insertar en medio | ✅ | — | ✅ | — | — | — | — | — |
| Ordenado | ✅ | ❌ | ✅ | ❌ | ✅ | LIFO | FIFO | Prioridad |
| Acceso aleatorio rápido | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Serializa a JSON nativo | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ | ❌ | ❌ |
| Recomendado en 2026 | ⭐ | ⭐ | ➖ | ➖ | ✅ | ➖ | ➖ | ✅ |

**Leyenda:** ⭐ recomendado · ✅ útil con ventajas reales · ➖ mejor con array/struct · ❌ no aplica

---

## 10. Guía de decisión: ¿qué uso?

```
¿Necesito guardar una colección de cosas?
│
├─ ¿Las claves son nombres fijos y conocidos?      → STRUCT
├─ ¿Las claves son dinámicas/variables?            → DS MAP (o struct + [$ ])
├─ ¿Es una lista ordenada, accedo por índice?      → ARRAY
├─ ¿Inserto/borro mucho en medio de la lista?      → DS LIST
├─ ¿Es una cuadrícula / mapa de tiles lógico?      → DS GRID
├─ ¿Necesito deshacer / navegar hacia atrás?       → DS STACK
├─ ¿Proceso en orden de llegada?                   → DS QUEUE
├─ ¿Proceso por prioridad (A*, IA)?                → DS PRIORITY QUEUE
└─ ¿Necesito que se limpie solo?                   → ARRAY o STRUCT
```

---

## 11. Ejemplo completo: spawn de enemigos (patrón clásico)

Este es el ejemplo del manual, y muestra por qué un array 2D ahorra muchísimo código:

```gml
// ─── Create event del objeto controlador ───
// Inicializamos de atrás hacia delante (óptimo)
enemigo[3][2] = 448;            // y
enemigo[3][1] = 32;             // x
enemigo[3][0] = obj_slime;      // objeto

enemigo[2][2] = 448;
enemigo[2][1] = 608;
enemigo[2][0] = obj_esqueleto;

enemigo[1][2] = 32;
enemigo[1][1] = 608;
enemigo[1][0] = obj_caballero;

enemigo[0][2] = 32;
enemigo[0][1] = 32;
enemigo[0][0] = obj_ogro;

// ─── Alarm o evento de pulsación de tecla ───
var i = irandom(3);   // 0 a 3 inclusive
instance_create_layer(enemigo[i][1], enemigo[i][2], "Enemy_Layer", enemigo[i][0]);
```

**Por qué es mejor:** generas un enemigo aleatorio con **dos líneas**, en vez de un `if/else` o un `switch` gigante. Y si quieres cambiar una coordenada, la cambias **en un solo sitio** en el Create, no repartida por el código.

### Versión moderna con structs (más legible)

```gml
// ─── Create event ───
puntos_spawn =
[
    { objeto: obj_ogro,       x:  32, y:  32 },
    { objeto: obj_caballero,  x: 608, y:  32 },
    { objeto: obj_esqueleto,  x: 608, y: 448 },
    { objeto: obj_slime,      x:  32, y: 448 }
];

// ─── Uso ───
var _punto = puntos_spawn[irandom(array_length(puntos_spawn) - 1)];
instance_create_layer(_punto.x, _punto.y, "Enemy_Layer", _punto.objeto);
```

La versión con structs es **autodocumentada**: lees `_punto.x` y sabes qué es, sin recordar si la `x` era el índice 1 o el 2.

---

## Resumen

1. **Arrays y structs son la recomendación oficial en 2026.** Se limpian solos.
2. Los arrays van **por referencia** y modificarlos dentro de una función **modifica el original**. Copy on Write está deprecado.
3. Los **accessors** (`|`, `?`, `#`, `$`) hacen el código muchísimo más legible, y se pueden **encadenar**.
4. Las funciones `array_*` cubren casi todo: `push`, `pop`, `insert`, `delete`, `sort`, `filter`, `map`, `reduce`, `unique`…
5. Las versiones **`_ext`** modifican el array original en vez de copiar.
6. **DS grids** y **DS priority queues** son los dos casos donde las estructuras de datos siguen brillando.
7. Si usas estructuras de datos: **destrúyelas siempre** y resetea la variable a `-1`.
8. **`variable_clone()`** es tu amigo para copias profundas.
