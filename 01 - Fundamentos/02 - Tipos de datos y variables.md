# 02 · Tipos de datos y variables

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Data_Types.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Variables_And_Variable_Scope.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Variables/Constants.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Instance_Keywords.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Variable_Functions.htm>

---

## 1. Por qué existen los tipos de datos

Cuando creas una variable, la usas para **guardar información**. Cuando llamas a una función, esa función te **devuelve** información. Esa información puede venir en distintos *sabores*: puede ser un número, puede ser un texto, puede ser una lista de cosas. Cada sabor es un **tipo de dato**.

Puedes preguntarle a cualquier variable qué tipo tiene con `typeof()`.

```gml
var _x = 42;
show_debug_message(typeof(_x));        // "number"
show_debug_message(typeof("hola"));    // "string"
show_debug_message(typeof([1, 2, 3])); // "array"
show_debug_message(typeof({a: 1}));    // "struct"
show_debug_message(typeof(obj_player));// "ref"  ← ¡un handle!
```

> ⚠️ Verás que los assets (objetos, sprites…) devuelven `"ref"`, no `"number"`. Ese es el cambio fundamental de 2026 que se explica a fondo en el **tema 03**.

---

## 2. Los tipos de datos, uno a uno

### 2.1 Real (números)

Cualquier valor que no sea un string ni ninguno de los otros tipos: `124`, `45639.566546456`, `0`, `-45.5`.

- Se almacenan como **doble precisión de 64 bits** (o enteros; el compilador optimiza cuando puede, por ejemplo `0.0` pasa a entero `0`).
- En **HTML5** todos los reales son *doubles*.
- Con valores no enteros tendrás **errores de redondeo** propios de la aritmética de coma flotante. Nunca compares dos floats con `==`; usa un epsilon.

```gml
// ❌ Peligroso: los floats rara vez son exactamente iguales
if (0.1 + 0.2 == 0.3) { /* nunca entra */ }

// ✅ Correcto: compara con una tolerancia
var _epsilon = 0.0001;
if (abs((0.1 + 0.2) - 0.3) < _epsilon) { /* entra */ }
```

> **Nota:** aunque tus variables son double o int, al trabajar con **extensiones** pueden entrar otros formatos. Los compruebas con las funciones `is_*()`.

### 2.2 Boolean (bool)

Un valor que es `true` o `false`.

- GameMaker interpreta **≤ 0.5 como falso** y **> 0.5 como verdadero**.
- ⚠️ **No uses 1 y 0 para verdadero/falso.** Usa las constantes `true` y `false`. Si en el futuro GameMaker añade un tipo booleano real, tu código seguirá funcionando.
- Para convertir cualquier real a booleano implícito: `bool()`.

```gml
var _numero = 7;
var _como_bool = bool(_numero);   // true

// ❌ Mala costumbre
if (vidas) { ... }

// ✅ Explícito y legible
if (vidas > 0) { ... }
```

### 2.3 String (cadenas de texto)

Cualquier texto entre comillas dobles `"...`.

```gml
var _saludo = "Hola Mundo";
```

⚠️ **Las comillas simples `' '` NO se aceptan.**

#### Caracteres de escape

| Secuencia | Significado |
|---|---|
| `\n` | Nueva línea |
| `\r` | Retorno de carro (0x0d) |
| `\b` | Retroceso (0x08) |
| `\f` | Salto de página (0x0c) |
| `\t` | Tabulador horizontal (0x09) |
| `\v` | Tabulador vertical (0x0b) |
| `\\` | La propia barra invertida (0x5c) |
| `\a` | Alerta (0x07) |
| `\u[hex]` | Carácter Unicode |
| `\x[hex]` | Carácter hexadecimal |
| `\[octal]` | Carácter Unicode octal |

```gml
var _frase = "Me dijo: \"Hola\", y se fue.\nY yo me quedé\taquí.";
```

> ⚠️ Los strings soportan `\f` y `\v`, pero eso **no** significa que el renderizado los respete: al dibujar texto pueden ignorarse.

> ⚠️ **Trampa con Unicode:** GameMaker interpreta *todos* los dígitos que siguen a `\u`. Para «áa» debes escribir `"\u00e2\a"`, `"\u00e2\u61"` o `"\u00e2" + "a"`. Si escribes `"\u00e2a"` obtendrás el carácter `ส` (porque se convierte en `\ue2a`).

#### Strings multilínea

Prefijo `@`:

```gml
var _texto = @"Este string tiene
saltos de línea
reales";
```

Los literales con `@` **no procesan caracteres de escape**: `@"Hello\World"` guarda la barra literalmente. Con `@` sí se permiten comillas simples `' '`.

> 💡 El carácter Unicode **9647** (`▯`) se usa para sustituir glifos que no existen en tu fuente. Si escribes `90°` y tu fuente no tiene el símbolo de grado, verás `90▯`.

#### Template strings (¡muy recomendables!)

Prefijo `$` y expresiones entre `{}`. Todo lo que hay dentro de las llaves se ejecuta como GML normal.

```gml
var _mundo = "Tierra";
var _t = $"Hola {_mundo}!";
// Equivale a: string("Hola {0}!", _mundo)

var _calc = $"Resultado: {5 * power(pi, 3) + 37.84094}";

// Escapa las llaves con \ si las quieres literales
var _literal = $"Usa \{llaves\} para interpolar";
```

El editor resalta el GML de dentro y **Feather** lo analiza en busca de errores.

> ⚠️ **¡Las posiciones en los strings empiezan en 1!** El primer carácter es la posición `1`, no la `0`. Es la excepción en GameMaker: todo lo demás es *zero-based*.

### 2.4 Arrays

Tipo especial que guarda múltiples valores. Se **pasan por referencia**.

> **Cambio importantísimo:** en versiones antiguas, modificar un array dentro de una función creaba una **copia** (*Copy on Write*). **Eso está deprecado.** En 2026, modificar el array dentro de la función modifica el original. La opción *Enable Copy on Write behaviour for Arrays* existe en las Game Options, pero está **desactivada por defecto y se recomienda dejarla así**.
>
> Detalle completo en el **tema 05**.

### 2.5 Structs

Estructura ligera que actúa como contenedor de variables de cualquier tipo. Se **pasan por referencia**. Es la base de la «POO» en GML.

> Detalle completo en el **tema 04**.

### 2.6 Method variables (métodos)

Una variable a la que has asignado una función. Se usa exactamente igual que una función del runtime.

> Detalle completo en el **tema 07**.

### 2.7 int64

Entero de 64 bits. Se crea con `int64()` pasándole un real, o al leer un `buffer_u64`.

```gml
var _grande = int64(9223372036854775807);
```

Cosas que debes saber:
- Úsalo donde se requiera estrictamente un entero de 64 bits, o para **bit-shifting** cuando necesitas las 64 posiciones.
- **Cualquier operación bitwise devuelve un int64**, incluso si los operandos no lo son.
- **Las divisiones de int64 devuelven enteros**: `int64(5) / int64(2)` → `2`.
- ⚠️ **Los valores de `enum` se guardan como int64**, así que `is_real()` sobre un enum devuelve `false`. Usa `is_int64()`.
- Las referencias a estructuras de datos y assets también se almacenan como int64 (32 bits de tipo + 32 bits de ID). Eso es exactamente un **handle** → tema 03.

### 2.8 Handle (¡el gran cambio de 2026!)

Referencia a un recurso: estructuras de datos, assets, instancias, funciones de script, partículas, buffers, surfaces, time sources, capas y tilemaps, flex panels, y referencias creadas con `ref_create()`.

> Tema completo en **03 - Handles**.

### 2.9 Pointer (puntero)

Apunta a una posición de memoria. **No puedes hacer operaciones con él** en GameMaker. Solo sirve para funciones muy concretas, como obtener la dirección de una textura o de un buffer.

```gml
var _tex = sprite_get_texture(spr_player, 0);   // devuelve un pointer
var _ptr = buffer_get_address(_buff);           // devuelve un pointer
```

Constantes asociadas:

| Constante | Significado |
|---|---|
| `pointer_null` | El puntero no apunta a nada con sentido (equivalente a `NULL` en C++ / `null` en C#). **Es falsy.** |
| `pointer_invalid` | El valor no es un puntero válido |

Para convertir: `ptr()`. Para comprobar: `is_ptr()`.

### 2.10 Enum

Te permite crear tu propio tipo de datos limitado, con una lista de valores constantes. **Global**, y no necesita el prefijo `global.`.

```gml
enum Arcoiris
{
    ROJO,       // 0
    NARANJA,    // 1
    AMARILLO,   // 2
    VERDE,      // 3
    AZUL,       // 4
    INDIGO,     // 5
    VIOLETA     // 6
}
```

Puedes asignar valores explícitos, e incluso **expresiones con enums definidos antes**:

```gml
enum Prueba { VAL = 10 }

enum Arcoiris
{
    ROJO    = 5,
    NARANJA = 5 * 2,
    AMARILLO = 15,
    VERDE   = 20,
    AZUL    = 25,
    INDIGO  = 30,
    VIOLETA = 35 * Prueba.VAL
}
```

Se accede con notación de punto:

```gml
var _v = Arcoiris.VERDE * Arcoiris.ROJO;   // 20 * 5 = 100
```

**Reglas:**
- Solo **enteros** o expresiones que evalúen a entero.
- Solo puedes referenciar enums creados **antes**.
- No puedes usar variables ni funciones propias: tiene que poder evaluarse en tiempo de compilación.
- No puedes modificar sus valores después.
- ⚠️ Se guardan como **int64**, así que `is_real()` devuelve `false`.

### 2.11 Undefined

Valor «nulo». Se devuelve cuando una expresión es sintácticamente correcta pero no tiene un valor correcto que devolver.

```gml
var _valor = ds_map_find_value(mi_mapa, "clave");
if (is_undefined(_valor))
{
    show_debug_message("¡La clave no existe!");
}
```

También es el valor por defecto de un **argumento opcional** no pasado, y lo que devuelve una función sin `return`.

### 2.12 NaN («Not a Number»)

Se devuelve cuando el compilador no puede evaluar una operación como número: `0/0`, o la raíz cuadrada de un negativo.

⚠️ **NaN no es igual a sí mismo**: `NaN == NaN` devuelve `false`.

```gml
show_debug_message(array_equals([NaN], [NaN]));  // 0 (false)
```

Comprueba con `is_nan()`.

### 2.13 Infinity

Número considerado infinito, como dividir un float entre cero: `1.0/0`.

A diferencia de NaN, **infinity sí es igual a sí mismo**: `infinity == infinity` → `true`. Comprueba con `is_infinity()`.

### 2.14 Any

No es un tipo real: aparece en el manual para indicar que una función **acepta cualquier tipo** o **puede devolver cualquiera**.

### 2.15 Booleanos especiales y keywords de instancia

| Keyword | Valor legacy |
|---|---|
| `self` | -1 |
| `other` | -2 |
| `all` | -3 |
| `noone` | -4 |

> ⚠️ **Nunca uses los valores numéricos directos.** Usa siempre los nombres.
>
> Esta tabla de valores legacy importa más de lo que parece: si pasas a `with()` un handle con valor `-1` esperando que no haga nada, en realidad se ejecutará sobre `self`. Ver tema 03.

---

## 3. Guijarros en el camino: literales con guion bajo

Puedes usar `_` como separador visual en literales numéricos. **El compilador los ignora:**

```gml
var _entero  = 100_000_000;          // = 100000000
var _decimal = 3_141.59;             // = 3141.59
var _hex     = 0xDEAD_BEEF;          // = 0xDEADBEEF
var _binario = 0b01101000_01101001;  // = 0b0110100001101001
```

---

## 4. Literales hexadecimales y binarios

### Hexadecimal

Dos formatos equivalentes: `$abcd` y `0xabcd`.

```gml
11406    → $2c8e   / 0x2c8e
16777215 → $ffffff / 0xffffff
```

⚠️ **Cuidado con `#`:** un valor hexadecimal que empieza con almohadilla se interpreta como **color CSS en formato #RRGGBB**, y **no** equivale al mismo valor con `$` o `0x`.

```gml
$2c8edd != #2c8edd
```
Para que sean iguales hay que intercambiar los dos primeros y los dos últimos caracteres:
```gml
$2c8edd == #dd8e2c
```

### Binario

Prefijo `0b`:

```gml
var _seis = 0b0010 | 0b0100;   // 0b0110 = 6
```

---

## 5. Ámbito de variables (scope) — el tema que más bugs genera

Toda variable pertenece a un **scope**. El scope determina **qué variables son accesibles** desde el código que se está ejecutando en ese momento.

**El scope se decide por dónde defines la variable por primera vez.**

### Los cinco ámbitos

| Ámbito | Cómo se crea | Cuánto vive |
|---|---|---|
| **Instance** (por defecto) | Asignar en un evento de objeto: `velocidad = 4;` | Mientras viva la instancia |
| **Local** | `var _velocidad = 4;` | Hasta el final del evento o la llamada a la función |
| **Global** | `global.puntuacion = 0;` | Toda la partida |
| **Static** | `static contador = 0;` dentro de una función | Se inicializa en la primera llamada; persiste |
| **Struct** | Dentro de un struct: `mi_struct.campo = 1;` | Mientras el struct tenga referencias |

### Reglas de visibilidad durante un evento de objeto

- Las **globales y constantes** siempre están disponibles.
- Las **variables de instancia** están disponibles mientras estás en el scope de esa instancia.
- Las **variables de struct** mientras estás en el scope de ese struct.
- Las **static** de una función mientras esa función se ejecuta.
- Las **locales** inicializadas en el evento o llamada actual, solo hasta que termina.

### Cambiar de scope: punto y `with`

```gml
// 1. El operador punto: "la variable b del ámbito a"
otra_instancia.vida -= 10;
global.puntuacion += 100;

// 2. La sentencia with: "ejecuta esto en el ámbito de a"
with (obj_enemigo)
{
    vida -= 10;              // se aplica a CADA enemigo
    if (vida <= 0)
    {
        instance_destroy();  // se destruye ese enemigo concreto
    }
}
```

Tanto con el punto como con `with`, `a` puede ser **una instancia o un struct**. También puedes usar los keywords (`self`, `other`, `all`, `noone`) o `global`.

### Nombres reservados (no puedes usarlos)

```
player_avatar_sprite   player_avatar_url
player_id              player_local
player_name            player_type
player_user_id         player_prefs
managed
```

### Reglas de nomenclatura

- Empieza por **letra o guion bajo** `_`.
- Solo letras, números y `_`.
- Máximo **64 caracteres**.

```gml
pez, foo_bar, num1, _str    // ✅ válidos
6pez, foo bar, *num         // ❌ inválidos
```

> ⚠️ **No puedes usar el nombre de un asset** como variable, salvo que especifiques ámbito: `self.MiScript = 5;` sí funciona (define el scope explícitamente).

### Asignación

```gml
<variable> = <expresión>;
```

También se acepta `:=` (poco habitual). Operadores compuestos:

```gml
a += b;   a -= b;   a *= b;   a /= b;
a |= b;   a &= b;   a ^= b;
a++;      a--;
```

❌ **No puedes encadenar asignaciones:**
```gml
a = b = c = 4;   // ERROR
```
```gml
a = 4; b = 4; c = 4;   // ✅
```

---

## 6. Constantes: `#macro` vs `enum`

Ambas son **globales** y **no requieren** el prefijo `global.`.
A diferencia de las variables globales, **no se pueden cambiar** tras declararse.

### Cuando usar cada una

| | `#macro` | `enum` |
|---|---|---|
| Guarda | Cualquier **expresión** (o un valor simple) | Una **lista de enteros** |
| Tipo | Cualquiera: número, string, llamada a función | Solo int64 |
| Uso típico | Un valor suelto, un atajo a una expresión | Estados, categorías, IDs |

### `#macro` — sintaxis (¡muy estricta!)

```gml
#macro NOMBRE valor
```

❌ **NO** uses `=` ni `;`:
```gml
#macro TOTAL_ARMAS = 10;   // ❌ inválido
#macro TOTAL_ARMAS 10      // ✅
```

⚠️ Se recomienda definirlos en un **Script asset, fuera de cualquier función**. Poner `#macro` dentro de sentencias o literales (por ejemplo dentro de un array) puede provocar errores de sintaxis en el IDE.

#### Macros con expresiones

```gml
// Un macro puede ser una expresión: se reevalúa en cada uso
#macro COLOR_ALEATORIO make_colour_hsv(irandom(255), 255, 255)
image_blend = COLOR_ALEATORIO;   // color distinto cada vez

// Saltos de línea con \ (solo cosmético)
#macro SALUDO show_debug_message("Hola" + \
string(nombre_jugador) + \
", ¿qué tal?");
```

#### Macros por configuración (muy potente)

Puedes sobreescribir un macro para una **Configuration** concreta:

```gml
#macro ID_ANUNCIOS ""
#macro Android:ID_ANUNCIOS "com.miempresa.juego.google"
#macro iOS:ID_ANUNCIOS     "com.miempresa.juego.appstore"
#macro DemoVersion:ID_ANUNCIOS ""
```

Formato: `nombreConfig:NOMBRE_MACRO valor`, **sin espacios** alrededor de los dos puntos. Las configuraciones hijas **heredan** los overrides del padre.

### Constantes integradas

| Constante | Descripción |
|---|---|
| `pointer_null` | Puntero que no apunta a nada con sentido. **Falsy.** |
| `pointer_invalid` | No es un puntero válido |
| `undefined` | Sin valor correcto que devolver. **Falsy.** |
| `NaN` | Resultado no representable como número (`0/0`) |
| `infinity` | Infinito (`1.0/0`) |
| `true` | 1 (en realidad: **≥ 1** evalúa a verdadero) |
| `false` | 0 (en realidad: **≤ 0** evalúa a falso) |
| `pi` | 3.141592653589793… |

---

## 7. Conversión de tipos

| De → A | Función | Notas |
|---|---|---|
| Cualquiera → bool | `bool(v)` | Implícito: ≤0.5 falso, >0.5 verdadero |
| Cualquiera → número | `real(v)` | En un handle devuelve el **índice** del recurso |
| Cualquiera → int64 | `int64(v)` | En un handle devuelve el **índice** |
| Cualquiera → string | `string(v)` | En un handle devuelve `"ref <tipo> <id>"` |
| Cualquiera → puntero | `ptr(v)` | |
| String → handle | `handle_parse(s)` | Formato `"ref <tipo> <id>"` o `"ref <tipo> <nombre>"`; `undefined` si está mal formado |

### Funciones de comprobación

Todas toman **un único argumento** (el valor a comprobar) y devuelven un booleano — no son
llamadas de cero argumentos pese a como se suelen citar por su nombre:

`is_string(v)` · `is_real(v)` · `is_numeric(v)` · `is_bool(v)` · `is_array(v)` · `is_struct(v)` ·
`is_method(v)` · `is_callable(v)` · `is_ptr(v)` · `is_int32(v)` · `is_int64(v)` ·
`is_undefined(v)` · `is_nan(v)` · `is_infinity(v)` · `is_handle(v)`

> ⚠️ **`is_struct()` devuelve `false` para una instancia de objeto.** Lo dice el manual —*«object
> instances will return false»*— y es fácil de olvidar porque una instancia se usa con la misma
> sintaxis de punto que un struct. Un `id` de instancia es un **handle**, no un struct.
>
> **Lo caro no es el dato, es cómo se manifiesta.** Medido en un proyecto real: una función de
> comprobación empezaba con `if (!is_struct(gestor)) { exit; }` sobre un id de instancia, así
> que **salía por la puerta de atrás sin imprimir nada** — ni un ✓, ni un ✗, ni un aviso. La
> comprobación existía, se llamaba, y no comprobaba nada.
>
> **Una comprobación que no se ejecuta y no lo dice es peor que no tenerla**, porque su
> silencio se lee como aprobado. Solo se descubrió porque quien la escribió esperaba una línea
> concreta en la salida y no apareció.
>
> Para una instancia, la guarda es **`instance_exists()`**. Y si una función puede recibir las
> dos cosas, compruébalas por separado y **haz que el caso «no era ninguna de las dos» diga
> algo**, en vez de salir callando.


```gml
// Ejemplo: validar la entrada de un archivo de guardado
function cargar_guardado(_ruta)
{
    if (!file_exists(_ruta)) { return undefined; }

    var _json = json_parse(_json_texto);

    if (!is_struct(_json))          { return undefined; }
    if (!struct_exists(_json, "version")) { return undefined; }
    if (!is_real(_json.version))    { return undefined; }

    return _json;
}
```

---

## 8. Valor vs referencia (la distinción que decide si tu bug existe)

Esta es probablemente la fuente de bugs número 1 para quien empieza.

| Tipo | Se pasa por |
|---|---|
| real, bool, string, int64, pointer | **Valor** (se copia) |
| array | **Referencia** (con matices, ver tema 05) |
| struct | **Referencia** |
| method | **Referencia** |
| handle | **Referencia** (es un int64 con significado) |

```gml
// --- POR VALOR ---
var _a = 10;
var _b = _a;
_b = 20;
show_debug_message(_a);   // 10 ← _a no cambió

// --- POR REFERENCIA ---
var _s1 = { vida: 100 };
var _s2 = _s1;            // _s2 apunta al MISMO struct
_s2.vida = 50;
show_debug_message(_s1.vida);   // 50 ← ¡_s1 también cambió!
```

**Consecuencia práctica:** si quieres una copia independiente de un struct, necesitas `variable_clone()` (copia profunda) o copiar campo a campo.

```gml
var _original = { vida: 100, nombre: "Goblin", inventario: ["espada"] };
var _copia    = variable_clone(_original);   // copia profunda

_copia.vida = 1;
show_debug_message(_original.vida);   // 100 ← intacto
```

> Más detalles en <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Values_And_References.htm>

---

## 9. Tabla resumen

| Tipo | `typeof()` devuelve | Literal de ejemplo | Se pasa por | Comprobar con |
|---|---|---|---|---|
| Real | `"number"` | `3.14`, `42` | Valor | `is_real()` |
| Bool | `"bool"` | `true`, `false` | Valor | `is_bool()` |
| String | `"string"` | `"hola"` | Valor | `is_string()` |
| int64 | `"int64"` | `int64(5)` | Valor | `is_int64()` |
| Array | `"array"` | `[1, 2, 3]` | Referencia | `is_array()` |
| Struct | `"struct"` | `{a: 1}` | Referencia | `is_struct()` |
| Method | `"method"` | `function() {}` | Referencia | `is_method()` |
| Handle / ref | `"ref"` | `obj_player`, `surf` | Referencia | `is_handle()` |
| Pointer | `"pointer"` | `pointer_null` | Valor | `is_ptr()` |
| Undefined | `"undefined"` | `undefined` | Valor | `is_undefined()` |
| NaN | `"number"` | `NaN` | Valor | `is_nan()` |
| Infinity | `"number"` | `infinity` | Valor | `is_infinity()` |

### Ámbitos en una tabla

| Ámbito | Sintaxis | Visible desde | Vive hasta |
|---|---|---|---|
| Local | `var _x = 1;` | Solo ese evento / llamada | Fin del evento / llamada |
| Instancia | `x = 1;` | Esa instancia | Fin de la instancia |
| Global | `global.x = 1;` | Todo el juego | Fin de la partida |
| Static | `static x = 1;` | La función que lo define (y sus structs) | Primera llamada → para siempre |
| Struct | `s.x = 1;` | Quien tenga el struct | Sin referencias (GC) |

---

## Ejercicio mental para fijar conceptos

Imagina que modelas un arma. ¿Qué tipo eliges para cada cosa?

```gml
// Las categorías fijas → enum (enteros con nombre, inmutables)
enum Rareza { COMUN, RARA, EPICA, LEGENDARIA }

// Un valor de configuración suelto → macro
#macro DANO_CRITICO_MULTIPLICADOR 2.5

// El arma en sí → struct (datos agrupados, por referencia)
function Arma(_nombre, _dano, _rareza) constructor
{
    nombre = _nombre;      // string
    dano   = _dano;        // real
    rareza = _rareza;      // enum (int64)
    nivel  = 1;            // real

    // Un método: comportamiento ligado al dato
    static atacar = function(_objetivo)
    {
        var _dano_total = dano * nivel;
        if (irandom(9) == 0) { _dano_total *= DANO_CRITICO_MULTIPLICADOR; }
        _objetivo.vida -= _dano_total;
    }
}

var _espada = new Arma("Espada oxidada", 12, Rareza.COMUN);
```

**Por qué así:** el enum te protege de escribir `"comun"` mal en un sitio; el macro te da un punto único de ajuste de balance; el struct agrupa datos + comportamiento sin el peso de un objeto con eventos; y el método `static` se crea **una sola vez** para todas las armas en vez de una copia por arma.
