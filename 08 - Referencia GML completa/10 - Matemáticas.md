# 10 · Matemáticas y números en GML

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23).

> Todas las firmas de esta página han sido verificadas contra el manual oficial LTS.

---

## Antes de empezar: dos advertencias importantes

### Los reales son doble precisión
En GameMaker los números reales son **doble precisión** (salvo en HTML5, donde también lo son).
La precisión de un cálculo **no es idéntica** en todas las plataformas, así que comparar
directamente dos reales es una fuente clásica de errores:

```gml
// ❌ PELIGROSO: image_index podría valer 1.0000002 y no entrar nunca
if (image_index == 1) { /* ... */ }

// ✅ CORRECTO
if (floor(image_index) == 1) { /* ... */ }
```

Para comparar reales con margen de error usa las funciones de épsilon
(`math_set_epsilon` / `math_get_epsilon`).

### Orden de evaluación
En los targets que usan el **YoYo Compiler (YYC)** todas las expresiones se evalúan de
**izquierda a derecha**; en el resto de plataformas, de **derecha a izquierda**. Por eso
esto da resultados distintos según la plataforma:

```gml
val = max(num, ++num, num++);   // ❌ ambiguo, evitar
```

Usa siempre paréntesis para hacer explícito el orden de evaluación.

---

## Redondeo y truncamiento

### `abs(val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el valor absoluto del argumento. Si el valor es positivo se queda igual; si es negativo se multiplica por -1 para volverlo positivo.
- **Ejemplo:**

```gml
x += abs(x - mouse_x);
```

### `sign(n)`

- **Devuelve:** Real
- **Qué hace:** Indica el signo de un número: devuelve `1` si es positivo, `-1` si es negativo y `0` si es cero. Por ejemplo `sign(458)` devuelve `1`, `sign(-5)` devuelve `-1` y `sign(0)` devuelve `0`.
- **Ejemplo:**

```gml
y += sign(y - mouse_y);
```

- **Notas:** `sign(NaN)` devuelve siempre `-1`.

### `ceil(val)`

- **Devuelve:** Real
- **Qué hace:** Redondea un número real **hacia arriba** al entero más cercano. Cuidado con el error clásico: `ceil(random(5))` puede devolver `0`, porque `random()` devuelve `0.0` inclusive.
- **Ejemplo:**

```gml
val = ceil( 3.4 );
```

- **Notas:** `ceil()` siempre redondea hacia el infinito positivo, incluso con negativos: `ceil(-2.3)` devuelve `-2`.

### `floor(n)`

- **Devuelve:** Real
- **Qué hace:** Redondea un número real **hacia abajo** al entero más cercano, sin importar la parte decimal. `floor(5.99999)` devuelve `5`, igual que `floor(5.2)` o `floor(5.6457)`.
- **Ejemplo:**

```gml
val = floor( 3.9 );
```

### `round(n)`

- **Devuelve:** Real
- **Qué hace:** Redondea un número real al entero más cercano, hacia arriba o hacia abajo. En el caso especial de un semi-entero exacto (1.5, 17.5, -2.5…) redondea al valor par más cercano (redondeo del banquero), de modo que `round(2.5)` da `2` y `round(3.5)` da `4`.
- **Ejemplo:**

```gml
score += round(hp / 5);
```

### `frac(n)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la parte fraccionaria de `n`, es decir, lo que hay detrás de la coma decimal, conservando el signo. `frac(3.125)` devuelve `0.125` y `frac(-6.921)` devuelve `-0.921`.
- **Ejemplo:**

```gml
val = frac(3.4);
```

### `clamp(val, min, max)`

- **Devuelve:** Real
- **Qué hace:** Mantiene un valor dentro de un rango: nunca será menor que `min` ni mayor que `max`. Es la forma idiomática de limitar velocidades, vidas o cualquier magnitud.
- **Ejemplo:**

```gml
speed = clamp(speed, 1, 10);
```

---

## Raíces, potencias y logaritmos

### `sqrt(val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la raíz cuadrada del número indicado. Es la operación inversa a elevar al cuadrado: `sqrt(25)` devuelve `5`.
- **Ejemplo:**

```gml
num = sqrt(val);
```

### `sqr(val)`

- **Devuelve:** Real
- **Qué hace:** Multiplica un número por sí mismo, es decir, devuelve su cuadrado. `sqr(5)` devuelve `25` porque `5*5 = 25`.
- **Ejemplo:**

```gml
score += sqr(dmg);
```

### `power(x, n)`

- **Devuelve:** Real
- **Qué hace:** Devuelve `x` elevado a `n`, es decir, `x` multiplicado por sí mismo `n` veces. `power(5, 3)` devuelve `125`, lo mismo que `5*5*5`.
- **Ejemplo:**

```gml
score += power(dmg, 3);
```

- **Notas:** El valor `x` no puede ser negativo si `n` no es entero: `power(-5, 0.5)` da `NaN`.

### `exp(n)`

- **Devuelve:** Real
- **Qué hace:** Equivale a `power(e, n)`, donde `e` es el número de Euler (aproximadamente 2,718281828). Responde a «cuánto crecimiento obtengo tras `n` unidades de tiempo con un 100 % de crecimiento continuo».
- **Ejemplo:**

```gml
val = exp(2);
```

### `ln(n)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el logaritmo natural (base `e`) del valor dado. Indica el tiempo necesario para alcanzar un determinado nivel de crecimiento continuo.
- **Ejemplo:**

```gml
alarm[0] = ln(age) * game_get_speed(gamespeed_fps);
```

### `log2(n)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el logaritmo en base 2 del número dado, es decir, cuántos doses hay que multiplicar para obtener `n`. Uso típico: calcular cuántos bits hacen falta para representar un número.
- **Ejemplo:**

```gml
colourbits = floor(log2(colour)) + 1;
```

### `log10(n)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el logaritmo en base 10 del número dado, es decir, cuántos dieces hay que multiplicar para obtener `n`.
- **Ejemplo:**

```gml
logval = log10(num);
```

### `logn(n, val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el logaritmo en base `n` del valor `val`. Es igual que `log2` y `log10`, pero con la base que tú indiques.
- **Ejemplo:**

```gml
logval = logn(5, num);
```

---

## Mínimos, máximos, media e interpolación

### `min(val1, val2, ... max_val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **mínimo** de los valores que le pases. Acepta tantos argumentos como quieras, aunque más argumentos significan un análisis más lento. `min(12, 96, 32, 75)` devuelve `12`.
- **Ejemplo:**

```gml
x = min(x, room_width);
```

- **Notas:** El número de argumentos afecta al rendimiento: con muchos valores, mejor recorrer un array.

### `max(val1, val2, ... max_val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **máximo** de los valores que le pases. Acepta tantos argumentos como quieras, aunque más argumentos significan un análisis más lento. `max(12, 96, 32, 75)` devuelve `96`.
- **Ejemplo:**

```gml
x = max(x, 0);
```

- **Notas:** El número de argumentos afecta al rendimiento: con muchos valores, mejor recorrer un array.

### `mean(val1, val2, ... max_val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la **media aritmética** de los valores indicados: los suma todos y los divide por su cantidad. `mean(2, 6, 9, 32)` devuelve `12,25`.
- **Ejemplo:**

```gml
xmiddle = mean(obj_player1.x, obj_player2.x, obj_player3.x);
ymiddle = mean(obj_player1.y, obj_player2.y, obj_player3.y);
```

### `median(val1, val2, ... max_val)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la **mediana** de los valores indicados: el valor central, o el mayor de los dos valores centrales si el número de argumentos es par.
- **Ejemplo:**

```gml
x = median(0, x, room_width);
y = median(0, y, room_height);
```

- **Notas:** A diferencia de `mean`, la mediana es robusta frente a valores extremos (outliers).

### `lerp(a, b, amt)`

- **Devuelve:** Real
- **Qué hace:** Interpolación lineal: devuelve el valor que corresponde a la posición `amt` entre `a` y `b`. `lerp(0, 10, 0.5)` devuelve `5`. Si `amt` sale de 0…1, la función **extrapola**.
- **Ejemplo:**

```gml
var _gamespeed = game_get_speed(gamespeed_fps);
xx = lerp(x, x + hspeed, _gamespeed);
yy = lerp(y, y + vspeed, _gamespeed);
```

---

## Precisión en comparaciones

### `math_set_epsilon(epsilon)`

- **Devuelve:** Real
- **Qué hace:** Ajusta el valor **épsilon** que usa GameMaker para comparar números reales. El épsilon decide si dos números con errores de redondeo se consideran «suficientemente iguales». El valor por defecto es `0.00001`.
- **Ejemplo:**

```gml
math_set_epsilon(0.0001);
```

### `math_get_epsilon()`

- **Devuelve:** Real
- **Qué hace:** Devuelve el valor épsilon actual utilizado en las comparaciones de números reales. Por defecto es `0.00001`.
- **Ejemplo:**

```gml
var e = math_get_epsilon();
if (e != 0.000001)
{
    math_set_epsilon(0.000001);
}
```

---

## Números aleatorios

### `choose(val0, val1, val2... max_val)`

- **Devuelve:** Cualquiera (One of the given arguments)
- **Qué hace:** Elige al azar **uno de los argumentos** que le pases. Es ideal cuando los valores no son numéricos o no están en un rango ordenado. `choose("rojo", "verde", "azul")` devuelve uno de los tres.
- **Ejemplo:**

```gml
sprite_index = choose(spr_cactus, spr_flower, spr_tree, spr_shrub);
hp = choose(5, 8, 15, 32, 40);
name = choose("John", "Steven", "Graham", "Jack", "Emily", "Tina", "Jill", "Helen");
```

### `random(n)`

- **Devuelve:** Real
- **Qué hace:** Devuelve un número decimal aleatorio entre `0.0` (inclusive) y el límite superior indicado (inclusive). `random(100)` puede devolver `22.56473`.
- **Ejemplo:**

```gml
if (random(10) >= 9)
{
    score += 100;
}
```

### `random_range(n1, n2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve un número decimal aleatorio entre el límite inferior y el superior, ambos inclusive. `random_range(20, 50)` devuelve un valor entre `20.00` y `50.00`.
- **Ejemplo:**

```gml
score += random_range(500, 600);
```

### `irandom(n)`

- **Devuelve:** Real
- **Qué hace:** Devuelve un número **entero** aleatorio entre `0` y `n`, ambos inclusive. `irandom(9)` devuelve un valor de 0 a 9.
- **Ejemplo:**

```gml
if (irandom(9) == 1)
{
    score += 100;
}
```

### `irandom_range(n1, n2)`

- **Devuelve:** Real
- **Qué hace:** Devuelve un número **entero** aleatorio dentro del rango dado, ambos extremos inclusive.
- **Ejemplo:**

```gml
score += irandom_range(500, 600);
```

### `random_set_seed(val, [fix_range_bug])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Fija la **semilla** que usa GameMaker para generar números aleatorios. Al fijar la semilla se «fuerza» el resultado de todos los eventos aleatorios, lo que permite reproducir una partida concreta (muy útil para depurar y para generación procedural reproducible).
- **Ejemplo:**

```gml
if (debug)
{
    random_set_seed(1, true);
}
```

- **Notas:** Tras fijar la semilla, todas las llamadas a `random`, `irandom`, `choose`, etc. producirán la misma secuencia. Es la base de la generación procedural reproducible.

### `random_get_seed()`

- **Devuelve:** Real
- **Qué hace:** Devuelve la semilla actual usada para generar números aleatorios. Puedes guardarla para reproducir más tarde la misma serie de valores.
- **Ejemplo:**

```gml
ini_open("Save.ini")
ini_write_real("Levels", string(level), random_get_seed());
ini_close();
```

### `randomise()`

- **Devuelve:** Real (unsigned 32 bit value)
- **Qué hace:** Fija la semilla a un valor aleatorio, de modo que cada ejecución del juego produce secuencias distintas. Escríbela también `randomize`.
- **Ejemplo:**

```gml
randomise();
```

- **Notas:** GameMaker arranca siempre con la **misma** semilla para facilitar la depuración. Llama a `randomise()` al inicio si quieres que cada partida sea distinta.

---

## Conversión de tipos

### `real(string)`

- **Devuelve:** Real
- **Qué hace:** Convierte un valor en un número real. Con strings tiene en cuenta números, signos menos, puntos decimales y notación exponencial; cualquier otro carácter (como letras) provoca un error.
- **Ejemplo:**

```gml
var _t_str = string_digits(input_str);
age = real(_t_str);
```

- **Notas:** Úsala también para convertir el resultado de `json_parse` o de lecturas de fichero antes de operar con él.

### `int64(val)`

- **Devuelve:** int64 (signed 64-bit integer)
- **Qué hace:** Convierte el valor dado en un **entero de 64 bits con signo**. El valor de entrada debe ser real, string, `int64`, `int32` o `ptr`; cualquier otra cosa hace que el juego se cierre con un error.
- **Ejemplo:**

```gml
steam_handle = int64(global.fileReadString);
```

- **Notas:** Comprueba antes con `is_int64` o `is_real` si no estás seguro del tipo, porque un tipo no válido cierra el juego.

### `ptr(n)`

- **Devuelve:** Pointer
- **Qué hace:** Convierte el valor dado en un **puntero**. El valor de entrada debe ser real, string, `int64`, `int32` o `ptr`; cualquier otra cosa hace que el juego se cierre con un error.
- **Ejemplo:**

```gml
if (!is_ptr(val))
{
    val = ptr(application_surface);
}
```

- **Notas:** Comprueba antes con `is_ptr` si no estás seguro del tipo, porque un tipo no válido cierra el juego.

### `bool(n)`

- **Devuelve:** Booleano
- **Qué hace:** Convierte el valor dado en un **booleano**: devuelve `true` si el valor es mayor que `0.5`, y `false` en caso contrario.
- **Ejemplo:**

```gml
if (!is_bool(val))
{
    val = bool(val);
}
```

- **Notas:** Recuerda que en GML cualquier valor >= 1 ya se evalúa como `true` y cualquier valor < 1 como `false`, así que rara vez necesitas convertir.

---

## Comprobación de tipos (is_*)

### `is_real(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la variable contiene un número real (simple, doble o entero).
- **Ejemplo:**

```gml
if (is_real(val))
{
    score += val;
}
```

### `is_string(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la variable contiene un string.
- **Ejemplo:**

```gml
if (is_string(val))
{
    name = "Player: " + val;
}
```

### `is_array(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la variable contiene un array.
- **Ejemplo:**

```gml
if (is_array(a))
{
    a = -1;
}
```

### `is_struct(val)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el valor es un struct. Ojo: las **method variables** también devuelven `true`, mientras que las instancias de objeto devuelven `false`.
- **Ejemplo:**

```gml
if (is_struct(a))
{
    delete(a);
}
```

### `is_method(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la variable es una **method variable**. Si lo que quieres es saber si algo se puede invocar, usa mejor `is_callable`.
- **Ejemplo:**

```gml
if is_method(get_vec)
{
    show_debug_message("Method variable!");
}
```

### `is_callable(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el argumento se puede **invocar**: es decir, si es un método o si apunta al índice de una función (built-in, Script Function o constructor).
- **Ejemplo:**

```gml
function my_function()
{
    return random(10);
}
my_method = function()
{
    return "Hello World!";
}

show_debug_message(is_callable(my_function));
show_debug_message(is_callable(my_method));
show_debug_message(is_callable(draw_text));
```

### `is_handle(val)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el valor es un **handle**.
- **Ejemplo:**

```gml
var _handle = sprite_index;

var _is_handle = is_handle(_handle);
var _is_handle_text = _is_handle ? "holds" : "doesn't hold";

show_debug_message($"The variable _handle {_is_handle_text} a handle!");
```

### `is_numeric(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la variable contiene un valor numérico: `real`, `int32`, `int64` o `bool`.
- **Ejemplo:**

```gml
if (is_numeric(val))
{
    current_val += val;
}
```

### `is_bool(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la variable contiene un booleano (`true` o `false`).
- **Ejemplo:**

```gml
if (is_bool(val))
{
    global.Sound = val;
}
else
{
    global.Sound = true;
}
```

### `is_int32(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la variable contiene un **entero de 32 bits**.
- **Ejemplo:**

```gml
if (!is_int32(val))
{
    show_debug_message("Not a 32 bit integer!");
}
```

### `is_int64(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la variable contiene un **entero de 64 bits**.
- **Ejemplo:**

```gml
if (!is_int64(val))
{
    show_debug_message("Not a 64bit integer!");
}
```

### `is_ptr(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si la variable contiene un **puntero**.
- **Ejemplo:**

```gml
if (!is_ptr(val))
{
    show_debug_message("Not a valid texture!");
}
```

### `is_undefined(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el valor es exactamente `undefined`.
- **Ejemplo:**

```gml
var _val = ds_map_find_value(map, 13);
if (is_undefined(_val))
{
    show_debug_message("Map entry does not exist!");
}
```

### `is_nan(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el valor es `NaN` (not a number).
- **Ejemplo:**

```gml
if (is_nan(global.value))
{
    show_debug_message("Value is not a number");
}
```

### `is_infinity(n)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el valor es **infinito**.
- **Ejemplo:**

```gml
if (is_infinity(global.value))
{
    show_debug_message("Value is infinite!");
}
```

---

## Introspección y hashes

### `typeof(variable)`

- **Devuelve:** String (see table above)
- **Qué hace:** Devuelve el tipo de datos de la variable como string: `"number"`, `"string"`, `"array"`, `"struct"`, `"method"`, `"int32"`, `"int64"`, `"bool"`, `"pointer"`, `"undefined"`, `"ref"` o el nombre de un asset.
- **Ejemplo:**

```gml
var _str = typeof(global.ExtensionInput);
show_debug_message(" global.ExtensionInput is a " + _str);
```

- **Notas:** Para structs creados con un constructor devuelve `"struct"`; usa `instanceof` si quieres el nombre del constructor.

### `nameof(name)`

- **Devuelve:** String
- **Qué hace:** Devuelve el **nombre** del identificador que le pases, como string. Sirve para nombres de assets, de variables, de structs, etc. Es la operación inversa a `asset_get_index`.
- **Ejemplo:**

```gml
show_debug_message("About to reveal internal names...");

show_debug_message($"The enemy object is called: {nameof(obj_enemy)}");
show_debug_message($"{pi} is a special value, it is called {nameof(pi)}.");
show_debug_message($"The function to create a ds_list is called: {nameof(ds_list_create)}, or even: {nameof(ds_list_create())}");

var _a = 77, _b = 66;
var _c = _a + _b;
show_debug_message($"The sum of {nameof(_a)} and {nameof(_b)} is {nameof(_c)}, or, using their values: {_a} + {_b} = {_c}");
```

- **Notas:** Es muy útil para depurar y para serializar structs sin escribir los nombres a mano.

### `variable_get_hash(name)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **hash** numérico de un nombre de variable. Ese hash se puede usar con `struct_get_from_hash` y `struct_set_from_hash`.
- **Ejemplo:**

```gml
var _the_struct = {a: 77, b: 88, c: 99};
var _varname = choose("a", "b", "c");
var _hash = variable_get_hash(_varname);
var _value = struct_get_from_hash(_the_struct, _hash);
```

- **Notas:** El compilador ya sustituye automáticamente por el hash los nombres de variable que detecta como constantes en tiempo de compilación, así que rara vez necesitas llamarla a mano.

### `handle_parse(value_string)`

- **Devuelve:** Handle (or undefined in case of an invalid handle type or an incorrectly formatted string)
- **Qué hace:** Interpreta un string para crear una referencia de tipo **handle**. Un handle se representa como `"ref <tipo> <id>"` o `"ref <tipo> <nombre>"`.
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

## Funciones que NO existen en GML (verificado)

Durante la elaboración de esta referencia se comprobó que las siguientes funciones,
que circulan por tutoriales y foros, **no están documentadas en el manual LTS 2026**
y por tanto no deben usarse:

| Nombre | Alternativa real |
| --- | --- |
| `percent_chance(n)` | `random(100) < n` o `irandom(99) < n` |
| `int64_to_string(v)` | `string(v)` |
| `randomize()` | Existe como **alias** de `randomise()`, pero no tiene página propia: usa `randomise()`. |
| `lerp_2d()` | No existe. Usa `lerp()` dos veces, una por eje. |
| `sleep()` | No existe en GML. Usa *time sources* o un temporizador manual. |

---

## Fuentes

- [GML Code Reference — GameMaker LTS 2026](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/GML_Reference.htm)
- Verificación de cada firma con `gm-cli manual read "<función>"` y contra el manual LTS (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
