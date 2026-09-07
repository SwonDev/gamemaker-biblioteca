# 12 · Strings en GML

> Referencia exhaustiva de **GameMaker LTS 2026** (IDE 2026.0.0.16 · Runtime 2026.0.0.23).

> Todas las firmas han sido verificadas contra el manual oficial LTS.

---

## ⚠ Lo primero: los índices de los strings empiezan en 1

Esta es la trampa número uno al trabajar con strings en GML. **Todo lo demás en
GameMaker es base 0** (arrays, listas, grids…), pero **las posiciones de los strings
empiezan en 1**:

```gml
var _s = "GameMaker";
string_length(_s);       // 9
string_char_at(_s, 1);   // "G"  <- el primer carácter está en 1
string_char_at(_s, 0);   // ""   <- 0 NO es válido
```

---

## Novedades de 2026

### Template strings `$"..."`

GameMaker LTS 2026 introduce los **template strings**: basta con prefijar la cadena con
`$` e interpolar expresiones GML entre llaves `{}`.

```gml
var _mundo = "Tierra";
var _t = $"Hola {_mundo}!";               // "Hola Tierra!"
var _c = $"5 * pi^3 + 37.84 = {5 * power(pi, 3) + 37.84094}";
```

- Todo lo que va entre `{ }` se ejecuta como **GML normal**.
- El editor resalta ese código y **Feather** lo comprueba en busca de errores.
- Para escribir una llave literal se escapa con una barra: `\{`.
- Se puede partir en varias líneas **solo dentro de las llaves**; los saltos de línea
  del texto deben escribirse con `\n`.

```gml
// Se puede partir en varias líneas SOLO dentro de las llaves ({ }):
var _a = $"Este es el \n{
    5 + 37
}\nmétodo de partir un template";
```

### `string_ext()`

Complemento de `string()` que recibe los valores en un **array**, lo que resuelve el
caso de los formatos con número variable de argumentos.

```gml
var _valores = ["Adrián", 42, true];
var _s = string_ext("Nombre: {0}, edad: {1}, activo: {2}", _valores);
```

### `toString()` en structs e instancias

Cuando pasas un **struct** o una **instancia** a `string`, `string_ext`,
`show_debug_message` o `show_debug_message_ext`, GameMaker llama a su método
`toString()` si lo tiene definido.

```gml
// En una instancia
toString = function()
{
    return string("Soy la instancia con ID {0}", id);
}

string(self);   // llama a toString()
string(id);     // NO lo llama: imprime "ref <id>"
```

> Los **arrays** se convierten a string automáticamente, sin necesidad de `toString()`.
> Para dibujar, basta con pasar la referencia a `draw_text()`, que convierte solo.

---

## Secuencias de escape

| Secuencia | Significado |
| --- | --- |
| `\n` | Salto de línea |
| `\r` | Retorno de carro (0x0d) |
| `\b` | Retroceso (0x08) |
| `\f` | Salto de página (0x0c) |
| `\t` | Tabulación horizontal (0x09) |
| `\v` | Tabulación vertical (0x0b) |
| `\\` | La propia barra invertida (0x5c) |
| `\a` | Alerta (0x07) |
| `\u[hex]` | Carácter Unicode |
| `\x[hex]` | Carácter con código hexadecimal |
| `\[octal]` | Carácter Unicode en octal |

> **Ojo:** los strings soportan `\f`, `\v`, etc., pero eso no significa que al **dibujar**
> se respeten: esos caracteres pueden ignorarse.

### Strings multilínea con `@`

```gml
var _texto = @"Este string tiene
saltos de línea
reales";
```

Los literales con `@` **no procesan secuencias de escape**: el contenido se guarda
literalmente. Para incluir comillas hay que concatenar.

---

## Crear strings


### `string(value_or_format [, value1, value2, ...])`

- **Devuelve:** String
- **Qué hace:** Crea un string a partir de cualquier tipo de datos. Con un solo argumento lo convierte directamente; con varios, el primero actúa como **cadena de formato** y los marcadores `{0}`, `{1}`, `{2}`… se sustituyen por los valores siguientes.
- **Ejemplo:**

*Ejemplo 1*


```gml
draw_text(100, 100, "Score: " + string(score) + " / Health: " + string(health));
```

*Ejemplo 2*


```gml
draw_text(100, 100, string("Score: {0} / Health: {1}", score, health));
```

- **Notas:** Los marcadores de formato son `{0}`, `{1}`, `{2}`… y funcionan con cualquier tipo de datos, incluidos structs y arrays.

### `string_ext(value_or_format, values)`

- **Devuelve:** String
- **Qué hace:** Igual que `string`, pero los valores a insertar se pasan en un **array** en lugar de como argumentos sueltos. Es la opción ideal cuando el número de valores es dinámico.
- **Ejemplo:**

```gml
numbers = [59, 23, 656, 8, 54];
array_sort(numbers, true);

var _str = string_ext("The three lowest numbers are: {0}, {1} and {2}", numbers);
```

- **Notas:** Equivalente a `string(fmt_valores...)` pero con los valores en un array: `string_ext("Hola {0}", ["mundo"])`.

---

## Longitud y códigos de carácter


### `string_length(string)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el número de **caracteres** del string. Recuerda que en GameMaker las posiciones de los strings empiezan en **1**, así que el último carácter está en `string_length(str)`. Si necesitas bytes, usa `string_byte_length`.
- **Ejemplo:**

```gml
if (string_length(name) > 10)
{
    name = string_copy(name, 1, 10);
}
```

- **Notas:** Las posiciones de los strings en GameMaker empiezan en **1**.

### `string_byte_length(string)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el número de **bytes** del string. Al estar almacenados en UTF-8, no coincide con el número de caracteres cuando hay acentos, eñes o emoji.
- **Ejemplo:**

```gml
bytesize = string_byte_length("Hello World");
```

- **Notas:** Un string con «á» ocupa 2 bytes pero 1 carácter. Usa `string_length` si quieres caracteres.

### `ansi_char(val)`

- **Devuelve:** String (Single character)
- **Qué hace:** Devuelve un string con el carácter correspondiente al **byte** indicado. No está pensado para mostrarse en pantalla, sino para guardarlo en disco al codificar datos.
- **Ejemplo:**

```gml
var str1 = ansi_char($EF);
var str2 = ansi_char($BB);
var str3 = ansi_char($BF);
file_text_write_string(global.saveFile, str1 + str2 + str3);
```

- **Notas:** No está pensado para mostrarse por pantalla, sino para guardar datos codificados.

### `chr(val)`

- **Devuelve:** String
- **Qué hace:** Devuelve un string con el carácter correspondiente al **código Unicode** indicado. El glifo real depende del juego de caracteres de la fuente de dibujo activa.
- **Ejemplo:**

```gml
mystring = chr(53) + chr(48);
```

- **Notas:** El glifo depende del juego de caracteres de la fuente activa; si no hay fuente definida se usa el juego por defecto.

### `ord(string)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el valor **Unicode (UTF-8)** del primer carácter del string. Se usa muchísimo junto con `keyboard_check` y `keyboard_lastchar`.
- **Ejemplo:**

```gml
if (keyboard_check(ord("W")))
{
    y -= 4;
}
```

- **Notas:** Con las funciones `keyboard_check*` el string de entrada solo puede tener un carácter.

### `string_char_at(str, index)`

- **Devuelve:** String
- **Qué hace:** Devuelve el carácter que ocupa la posición indicada. Los índices empiezan en **1**. Si no hay carácter en esa posición devuelve un string vacío `""`.
- **Ejemplo:**

```gml
str1 = "Hello World";
str2 = string_char_at(str1, 7);
```

- **Notas:** Los índices empiezan en **1**, al contrario que los arrays, que empiezan en 0.

### `string_ord_at(str, index)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **código Unicode** del carácter que ocupa la posición indicada. Los índices empiezan en **1**.
- **Ejemplo:**

```gml
str = "Hello World";
char_code = string_ord_at(str, 7);
```

- **Notas:** Los índices empiezan en **1**.

### `string_byte_at(str, index)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el valor **byte crudo** que ocupa la posición indicada del string.
- **Ejemplo:**

```gml
newbyte = string_byte_at("Hello World", 5);
```

- **Notas:** Trabaja con bytes UTF-8, no con caracteres. Para caracteres usa `string_char_at`.

### `string_set_byte_at(str, pos, byte)`

- **Devuelve:** String
- **Qué hace:** Escribe un byte directamente en la posición indicada (según UTF-8) y devuelve una **copia** del string modificada. **Es extremadamente lenta**: úsala solo si no hay alternativa.
- **Ejemplo:**

```gml
str = string_set_byte_at("hello", 2, 97);
```

- **Notas:** ⚠ Esta función es **increíblemente lenta**. Evítala en bucles y en el Step.

---

## Búsqueda e información


### `string_pos(substr, str)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la posición (empezando por 1) de la primera aparición del substring dentro del string, buscando desde el principio. Devuelve `0` si no lo encuentra.
- **Ejemplo:**

```gml
if (string_pos(",", text) != 0)
{
    string_insert(name, text, string_pos(",", text));
}
```

- **Notas:** Devuelve `0` si no encuentra el substring, no `-1`.

### `string_pos_ext(substr, str, start_pos)`

- **Devuelve:** Real
- **Qué hace:** Igual que `string_pos`, pero empieza a buscar **hacia delante** desde la posición `start_pos` que indiques.
- **Ejemplo:**

```gml
if (string_pos_ext(",", text, 20) != 0)
{
    string_insert(name, text, string_pos_ext(",", text, 20));
}
```

- **Notas:** Devuelve `0` si no encuentra el substring.

### `string_last_pos(substr, str)`

- **Devuelve:** Real
- **Qué hace:** Devuelve la posición de la primera aparición del substring buscando **desde el final** hacia el principio. Devuelve `0` si no lo encuentra.
- **Ejemplo:**

```gml
if (string_last_pos(",", text) != 0)
{
    string_insert(name, text, string_last_pos(",", text));
}
```

- **Notas:** Devuelve `0` si no encuentra el substring.

### `string_last_pos_ext(substr, str, start_pos)`

- **Devuelve:** Real
- **Qué hace:** Igual que `string_last_pos`, pero empieza a buscar **hacia atrás** desde la posición `start_pos` que indiques.
- **Ejemplo:**

```gml
if (string_last_pos_ext(",", text, 20) != 0)
{
    string_insert(name, text, string_last_pos_ext(",", text, 20));
}
```

- **Notas:** Devuelve `0` si no encuentra el substring.

### `string_starts_with(str, substr)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el string **empieza** por el substring dado.
- **Ejemplo:**

```gml
var _message = "Hello world";
if string_starts_with(_message, "Hello")
{
    show_debug_message("Greeting successful!");
}
```

### `string_ends_with(str, substr)`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el string **termina** por el substring dado.
- **Ejemplo:**

```gml
var _message = "Hello World.";
if string_ends_with(_message, ".") || string_ends_with(_message, "?") || string_ends_with(_message, "!")
{
    show_debug_message("The message is a valid sentence.");
}
```

### `string_count(substr, str)`

- **Devuelve:** Real
- **Qué hace:** Devuelve cuántas veces aparece el substring dentro del string.
- **Ejemplo:**

```gml
str1 = "Hello World";
ocount = string_count( "o", str1 );
```

---

## Manipulación


### `string_copy(str, index, count)`

- **Devuelve:** String
- **Qué hace:** Devuelve una **copia** de la parte del string comprendida entre las posiciones `index` y `index + count` (ambas empezando en 1).
- **Ejemplo:**

```gml
name = keyboard_string;
if (string_length(name) > 15)
{
    keyboard_string = string_copy(name, 1, 15);
}
```

### `string_delete(str, index, count)`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string con la parte indicada **eliminada**. El string original no se modifica.
- **Ejemplo:**

*Ejemplo 1: uso básico*


```gml
str = "Helloo World";
str = string_delete(str, 5, 1);
```

*Ejemplo 2: índice y recuento negativos*


```gml
str = "One, two, three, four!";

str = string_delete(str, -2, -6);
show_debug_message(str);
```

### `string_insert(substr, str, index)`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string con el substring **insertado** en la posición indicada.
- **Ejemplo:**

```gml
str2 = string_insert(username, "Hello, , how are you?", 8);
```

### `string_lower(string)`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string con todas las letras en **minúsculas**.
- **Ejemplo:**

```gml
str1 = "Hello World";
str2 = string_lower(str1);
```

### `string_upper(string)`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string con todas las letras en **mayúsculas**.
- **Ejemplo:**

```gml
str1 = "Hello World";
str2 = string_upper(str1);
```

### `string_repeat(str, count)`

- **Devuelve:** String
- **Qué hace:** Devuelve un string formado por el string original repetido el número de veces indicado.
- **Ejemplo:**

```gml
str1 = "Hello World";
str2 = string_repeat(str1, 3);
```

### `string_replace(str, substr, newstr)`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string en la que la **primera** aparición del substring se sustituye por el string de reemplazo.
- **Ejemplo:**

```gml
str1 = "Hello Earth";
str2 = string_replace(str1, "Earth", "World");
```

### `string_replace_all(str, substr, newstr)`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string en la que **todas** las apariciones del substring se sustituyen por el string de reemplazo.
- **Ejemplo:**

```gml
str1 = "Hexxo Worxd";
str2 = string_replace_all(str1, "x", "l");
```

### `string_digits(string)`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string que contiene **solo los dígitos** numéricos, eliminando todo lo demás.
- **Ejemplo:**

```gml
var t_str = string_digits(input_str);
age = real(t_str);
```

- **Notas:** Solo conserva los dígitos del 0 al 9.

### `string_letters(string)`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string que contiene **solo las letras**, eliminando todo lo demás.
- **Ejemplo:**

```gml
username = string_letters(username);
```

- **Notas:** Solo conserva caracteres alfabéticos.

### `string_lettersdigits(string)`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string que contiene **solo letras y dígitos**, eliminando todo lo demás.
- **Ejemplo:**

```gml
if (string_length(password) > string_length(string_lettersdigits(password)))
{
    draw_text(32,32, "Invalid Password! Only Letters and numbers please!");
}
```

- **Notas:** Conserva letras y dígitos; descarta espacios, signos de puntuación y todo lo demás.

### `string_format(val, total, dec)`

- **Devuelve:** String
- **Qué hace:** Devuelve el número dado convertido a string con un número fijo de **decimales** y de **posiciones enteras** rellenas con ceros. Es la forma de mostrar puntuaciones o cronómetros con formato estable.
- **Ejemplo:**

```gml
str1 = string_format(1234, 8, 0);
str2 = string_format(pi, 1, 10);
str3 = string_format(pi, 5, 5);
```

- **Notas:** `string_format(pi, 1, 3)` da `"3.142"`: 1 cifra entera y 3 decimales.

### `string_hash_to_newline(string)`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string en la que todos los caracteres almohadilla `#` se sustituyen por **saltos de línea**. Pensada para los diálogos clásicos de RPG.
- **Ejemplo:**

```gml
var str = string_hash_to_newline("Hello#World");
draw_text(32, 32, str);
```

- **Notas:** El carácter `#` se sustituye por un salto de línea; no confundir con un carácter de comentario.

---

## Recorte (trim)


### `string_trim(str, [substr])`

- **Devuelve:** String
- **Qué hace:** Devuelve una copia del string sin los **espacios en blanco** ni del principio ni del final. Si pasas un array de strings como segundo argumento, recorta cualquiera de esos substrings en ambos extremos.
- **Ejemplo:**

*Ejemplo 1: (Trimming Spaces)*


```gml
clean_string = string_trim("     Text somewhere in the middle.    ");
```

*Ejemplo 2: (Trimming Newlines)*


```gml
var _string_from_literal = @"
The first line
is followed by the second line
";
clean_string = string_trim(_string_literal);
```

*Ejemplo 3: (Using An Array)*


```gml
var _string = "ThisThis is an object I love"
var _remove = ["This", "is", "love"]
var _trimmed = string_trim(_string, _remove);

show_debug_message(_trimmed) // Prints " is an object I "
```

- **Notas:** Sin segundo argumento recorta espacios en blanco (`White-space Characters`). Con array, recorta esos substrings.

### `string_trim_start(str, [substr])`

- **Devuelve:** String
- **Qué hace:** Igual que `string_trim`, pero recorta solo el **principio** (la izquierda) del string.
- **Ejemplo:**

*Ejemplo 1*


```gml
var _string_with_a_bit_of_everything = "     \t\t\t\tHello World";
var _trimmed_string = string_trim_start(_string_with_a_bit_of_everything);
show_debug_message(_trimmed_string);
```

*Ejemplo 2: (Using An Array)*


```gml
var _string = "ThisThis is an object I love"
var _remove = ["This", "is", "love"]
var _trimmed = string_trim_start(_string, _remove);

show_debug_message(_trimmed) // Prints " is an object I love"
```

### `string_trim_end(str, [substr])`

- **Devuelve:** String
- **Qué hace:** Igual que `string_trim`, pero recorta solo el **final** (la derecha) del string.
- **Ejemplo:**

*Ejemplo 1*


```gml
var _the_string = "A\nB\n\C\nD\n\n\n\n\n\n";
var _clean_string = string_trim_end(_the_string);
```

*Ejemplo 2: (Using An Array)*


```gml
var _string = "This is an object I lovelove"
var _remove = ["This", "I", "love"]
var _trimmed = string_trim_end(_string, _remove);

show_debug_message(_trimmed) // Prints "This is an object I "
```

---

## Dividir y unir


### `string_split(string, delimiter, [remove_empty], [max_splits])`

- **Devuelve:** Array
- **Qué hace:** Divide el string usando el delimitador indicado y devuelve un **array** con los fragmentos. El delimitador puede ser un carácter o una cadena de varios caracteres.
- **Ejemplo:**

*Ejemplo 1*


```gml
file_path = "C:/Users/someone/Documents/data.json";

var _path_parts = string_split(file_path, "/");

show_debug_message(_path_parts);

drive_name = _path_parts[0];
file_name = array_last(_path_parts);
```

*Ejemplo 2*


```gml
the_string = "abc|def||ghi|jkl|mno|pqrs|tuv|wxyz";
string_parts = string_split(the_string, "|", true, 5);

show_debug_message_ext("{0}, {1}, {2}, {3}, {4}", string_parts);
```

- **Notas:** Con `remove_empty = true` descarta los fragmentos vacíos; con `max_splits` limitas el número de cortes.

### `string_split_ext(string, delimiter_array, [remove_empty], [max_splits])`

- **Devuelve:** Array
- **Qué hace:** Igual que `string_split`, pero acepta un **array de delimitadores**: el string se corta en cuanto aparece cualquiera de ellos.
- **Ejemplo:**

```gml
words = string_split_ext("here,there;everywhere,and beyond", [",", ";"]);
```

- **Notas:** Muy útil para tokenizar: `string_split_ext(txt, [" ", ",", "."], true)`.

### `string_join(delimiter, value1 [, value2, ... max_val])`

- **Devuelve:** String
- **Qué hace:** Une las representaciones en string de todos los argumentos, insertando el delimitador entre cada uno. Los valores que no son strings se convierten automáticamente con `string`.
- **Ejemplo:**

```gml
countdown_message = string_join("... ", "Ready", "Set", "Go!");
```

### `string_join_ext(delimiter, values_array, [offset], [length])`

- **Devuelve:** String
- **Qué hace:** Une las representaciones en string de los elementos de un **array** (o de una parte de él), insertando el delimitador entre cada uno.
- **Ejemplo:**

*Ejemplo 1*


```gml
var _words = string_join_ext(" ", ["This", "example", "joins", "words"]);
```

*Ejemplo 2*


```gml
var _buffer = buffer_create(1, buffer_grow, 1);
var _text_lines = ["This", "file", "will", "have", "multiple", "lines"];
var _file_contents = string_join_ext("\r\n", _text_lines);
buffer_write(_buffer, buffer_text, _file_contents);
buffer_save(_buffer, save_dir + "/" + "text.txt");
buffer_delete(_buffer);
```

### `string_concat(value1 [, value2, ... max_val])`

- **Devuelve:** String
- **Qué hace:** Concatena las representaciones en string de todos los argumentos y devuelve el resultado. A diferencia de `string_join`, **no** inserta ningún separador.
- **Ejemplo:**

```gml
result = string_concat("W", "o", "r", "d", "s");
```

### `string_concat_ext(values_array, [offset], [length])`

- **Devuelve:** String
- **Qué hace:** Concatena las representaciones en string de los elementos de un array (o de una parte de él) y devuelve el resultado.
- **Ejemplo:**

```gml
var _some_letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"];
var _concat = string_concat_ext(_some_letters, -5, -3);
```

---

## Iteración


### `string_foreach(string, function, [pos], [length])`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Ejecuta una función de retorno (callback) **por cada carácter** del string. Puedes acotar el recorrido con `pos` y `length`; un `length` negativo recorre el string hacia atrás.
- **Ejemplo:**

*Ejemplo 1*


```gml
function debug_character(character, position)
{
    show_debug_message(character);
}

string_foreach("test", debug_character);
```

*Ejemplo 2*


```gml
function debug_extended(character, position)
{
    show_debug_message("{0}: {1}", position, character);
}

string_foreach("1234567890", debug_extended, -1, -infinity);
```

- **Notas:** El callback recibe `(carácter, índice)`. Con `length` negativo itera hacia atrás.

---

## Medidas para dibujo


### `string_width(string)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **ancho en píxeles** que ocuparía el string al dibujarlo con la fuente activa. Es esencial para centrar texto.
- **Ejemplo:**

```gml
var ww = string_width(str_Name + " ");
draw_text(32, 32, str_Name);
draw_text(32 + ww, 32, "has won the game!");
```

- **Notas:** Depende de la fuente activa en el momento de la llamada con `draw_set_font`.

### `string_width_ext(string, sep, w)`

- **Devuelve:** Real
- **Qué hace:** Igual que `string_width`, pero tiene en cuenta el espaciado entre caracteres (`sep`) y la anchura máxima de línea (`w`) que produce saltos de línea automáticos.
- **Ejemplo:**

```gml
var ww = string_width_ext(str_Story_Text[1], -1, 100);
draw_text_ext(32, 32, str_Story_Text[1], -1, 100);
draw_text_ext(32 + ww, 32, str_Story_Text[2], -1, 100);
```

- **Notas:** Si `w` es -1 no se fuerza ningún salto de línea automático.

### `string_height(string)`

- **Devuelve:** Real
- **Qué hace:** Devuelve el **alto en píxeles** que ocuparía el string al dibujarlo con la fuente activa.
- **Ejemplo:**

```gml
var hh = string_height("ABCDEFGHIJKLMNOPQRSTUVWXYZ");
draw_text(32, 32, string(score));
draw_text(32, 32 + hh, string(lives));
```

### `string_height_ext(string, sep, w)`

- **Devuelve:** Real
- **Qué hace:** Igual que `string_height`, pero tiene en cuenta el espaciado entre líneas y los saltos de línea automáticos provocados por el ancho máximo.
- **Ejemplo:**

```gml
var hh = string_height_ext(str_Story_Text[1], -1, 100);
draw_text_ext(32, 32, str_Story_Text[1], -1, 100);
draw_text_ext(32, 32 + hh, str_Story_Text[2], -1, 100);
```

---

## Portapapeles


### `clipboard_has_text()`

- **Devuelve:** Booleano
- **Qué hace:** Indica si el portapapeles contiene texto.
- **Ejemplo:**

```gml
if (clipboard_has_text())
{
    str = clipboard_get_text();
    clipboard_set_text("");
}
```

- **Notas:** Soportado en Windows, Ubuntu, macOS, Android, iOS, HTML5 y Opera GX. En HTML5 el portapapeles no siempre está disponible.

### `clipboard_get_text()`

- **Devuelve:** String
- **Qué hace:** Devuelve el texto del portapapeles, o un string vacío `""` si no hay nada.
- **Ejemplo:**

```gml
if (clipboard_has_text())
{
    str = clipboard_get_text();
    clipboard_set_text("");
}
```

- **Notas:** Soportado en Windows, Ubuntu, macOS, Android, iOS, HTML5 y Opera GX.

### `clipboard_set_text(string)`

- **Devuelve:** N/A (no devuelve nada)
- **Qué hace:** Copia el string indicado al portapapeles. Pásale `""` para vaciarlo.
- **Ejemplo:**

```gml
if (clipboard_has_text())
{
    str = clipboard_get_text();
    clipboard_set_text("");
}
```

- **Notas:** Soportado en Windows, Ubuntu, macOS, Android, iOS, HTML5 y Opera GX.

---

## Funciones de string que NO existen en GML

| Nombre | Alternativa real |
| --- | --- |
| `string_contains()` | `string_pos(sub, str) > 0` |
| `string_reverse()` | No existe: recorre el string con `string_foreach` y reconstrúyelo |
| `string_replace_first()` | `string_replace()` ya solo reemplaza la primera |
| `string_is_empty()` | `str == ""` |

---

## Fuentes

- [GML Code Reference — GameMaker LTS 2026](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/GML_Reference.htm)
- [Strings (LTS)](https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Strings/Strings.htm)
- Verificación de cada firma con `gm-cli manual read "<función>"` y contra el manual LTS (IDE 2026.0.0.16 / Runtime 2026.0.0.23).
