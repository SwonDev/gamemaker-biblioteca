# 07 · Funciones, métodos y ámbito

> **Fuentes:**
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Script_Functions.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Method_Variables.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Functions/Static_Variables.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Overview/Variables_And_Variable_Scope.htm>
> - <https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/Variable_Functions/Variable_Functions.htm>

---

## 1. Las dos sintaxis (y por qué importan)

En GML puedes definir una función de dos formas:

```gml
// FORMA A — script function
function nombre(param1, param2)
{
    // ...
}
```

```gml
// FORMA B — method variable
nombre = function(param1, param2)
{
    // ...
}
```

### La diferencia, según el manual

| | Forma A (`function nombre()`) | Forma B (`nombre = function()`) |
|---|---|---|
| Ámbito | **Global** (si está en un Script asset) | Global, pero como **method variable** |
| Índice de script | ✅ Se le asigna uno (**handle** de script) | ❌ No |
| `typeof()` devuelve | `"ref"` | `"method"` |
| Requiere prefijo `global.` | ❌ No (el compilador la reconoce) | ✅ Sí, si la referencias desde fuera |
| ¿Está ligada (*bound*)? | ❌ No (es «unbound») | ✅ Sí, al ámbito donde se definió |

> ⚠️ **Si defines la función dentro del evento de un objeto**, la forma A **NO** la hace global: solo estará disponible en el contexto de esa instancia.

### Regla práctica

- **En un Script asset** → usa la **Forma A**. Es una función global de verdad.
- **Dentro de un struct o una instancia** → usa la **Forma B**. Es un método ligado.
- **Para constructores con herencia** → **obligatoriamente** la Forma A (ver tema 04).

---

## 2. Script assets: el contenedor

Un **Script asset** es un contenedor de una o más funciones que escribes tú.

### Por qué usarlos

- Tienes un bloque de código que usas en **más de un sitio**.
- Quieres **modularidad**: agrupar funciones por categoría (por ejemplo `Colisiones`, `IA_Enemigos`, `Utilidades`).
- Cambias la función una vez y **todos** los objetos recogen el cambio.

> 💡 **El nombre del script es INDEPENDIENTE de las funciones que contiene.** Puedes llamar al script `IA_Enemigos` y meter dentro `ia_pos_objetivo()`, `ia_nivel_alerta()`, `ia_estado()`. O puedes poner una función por script si prefieres verlas listadas en el Asset Browser.

### ⚠️ Los scripts se compilan al inicio del todo

> *«scripts are parsed on a **global** level and will be compiled at the very start of the game»*

Tres consecuencias importantísimas:

**1. Las variables declaradas FUERA de una función son GLOBALES.**

```gml
// Script: scr_config
function Foo() { /* ... */ }
blah = 10;                 // ← esto es global.blah
function Bar() { /* ... */ }

// Para leerla necesitas el prefijo:
valor = global.blah;
```

> 💡 **Recomendación:** escribe siempre `global.` explícitamente para evitar sustos.

**2. Los scripts son el lugar ideal para macros, enums y variables globales** porque se crean antes de que el juego empiece a correr:

```gml
/// Script: scr_config
/// @description Inicializa constantes y estado global

global.puntuacion = 0;
global.vidas      = 3;
global.pausa      = false;

enum ColorArcoiris
{
    ROJO, NARANJA, AMARILLO, VERDE, AZUL, INDIGO, VIOLETA
}

#macro NUM_ARMAS 3
#macro ARMA_PISTOLA 0
#macro ARMA_BOMBA   1
#macro ARMA_CUCHILLO 2
```

**3. Si quieres inicializar variables de INSTANCIA desde un script, envuélvelas en una función:**

```gml
/// @function        init_enemigo()
/// @description     Inicializa variables de instancia del enemigo
function init_enemigo()
{
    vida = 100;
    dano = 5;
    mana = 50;
}
```

Y la llamas desde el Create del objeto.

### ⚠️ Los scripts vacíos no existen

Si un script está **completamente vacío**, **no se carga** en el juego compilado y referenciarlo crashea el juego.

> Con solo un comentario dentro, ya se incluye.

### ⚠️ Script name ≠ function

Este es un error clásico:

```gml
function llamada_indirecta(func, arg)
{
    func(arg);
}

llamada_indirecta(miscript, arg);   // ❌ FALLA
```

¿Por qué? Porque `miscript` es el **índice del asset** (un número), no la función. Si el índice es `4`, estás haciendo `4(arg)`, que no tiene sentido.

**Dos soluciones:**

```gml
// Solución 1: convertir a método antes de pasarlo
llamada_indirecta(method(undefined, miscript), arg);

// Solución 2: usar script_execute dentro
function llamada_indirecta(func, arg)
{
    script_execute(func, arg);
}
llamada_indirecta(miscript, arg);
```

### HTML5: `gmcallback_`

Si desarrollas para Web, prefija con `gmcallback_` las funciones que no quieres que se ofusquen (para poder usarlas desde JavaScript):

```gml
function gmcallback_crear_boton()
{
    // no se ofusca: accesible desde extensiones JS
}
```

> 💡 **Sin ese prefijo no hay forma de llamarla desde JavaScript**, porque el compilador
> renombra las funciones y el nombre nuevo no es predecible.
>
> 📄 El mecanismo completo —crear la extensión `.js`, los tipos que se pueden pasar, y qué
> **no** se puede hacer en web— está en
> [17 · Interoperabilidad con la web (HTML5)](../04%20-%20Recetas%20por%20género/17%20-%20Interoperabilidad%20con%20la%20web%20%28HTML5%29.md).

---

## 3. Parámetros y argumentos

### Parámetros con nombre

```gml
function mover(spd, dir)
{
    speed     = spd;
    direction = dir;
}

var _dir = point_direction(x, y, mouse_x, mouse_y);
mover(4, _dir);
```

Los parámetros están disponibles como **variables locales** dentro de la función.

### Argumentos por índice

También puedes acceder con `argument0`, `argument1`, … o con el array `argument[0]`, `argument[1]`, …:

```gml
function imprimir()
{
    var _str = "";
    for (var i = 0; i < argument_count; i++)
    {
        _str += string(argument[i]);
    }
    show_debug_message(_str);
}

imprimir("Jugador : ", current_time, " : ", id, " : disparó");
```

`argument_count` te da el número de argumentos pasados → **permite funciones con número variable de argumentos**.

> ⚠️ **No puedes usar el accessor `@` con el array `argument[n]`.**

### Argumentos opcionales

Si un argumento no se pasa, vale `undefined`. Puedes comprobarlo o darle un **valor por defecto**:

```gml
function mover(spd, dir = 90)
{
    speed     = spd;
    direction = dir;
}

mover(4);        // dir = 90 (hacia arriba)
```

> 💡 **Puedes omitir argumentos intermedios** y se rellenan con `undefined` (o su valor por defecto):
> ```gml
> mi_func(0,,,1);                          // equivalente a:
> mi_func(0, undefined, undefined, 1);
> ```

### ⚠️ Los valores por defecto pueden ser EXPRESIONES

Y aquí está la parte potente: el valor por defecto puede ser una **expresión completa** que llame a funciones, use variables, etc.

```gml
function log(texto = "Log", objeto = object_index,
             tiempo = date_datetime_string(date_current_datetime()))
{
    var _s = "[" + string(tiempo) + "] ";
    _s += object_get_name(objeto) + ": ";
    _s += texto;
    show_debug_message(_s);
}
```

> ⚠️ **La expresión solo se ejecuta si el argumento NO se proporciona.** Si lo pasas, no se evalúa (útil para valores por defecto costosos).

```
log();
// → [09-Jun-21 12:34:37 PM] Object1: Log

log("Jugador disparó", obj_player, 10);
// → [10] obj_player: Jugador disparó
```

---

## 4. Valor de retorno

```gml
return <expresión>;
```

> ⚠️ **La ejecución de la función TERMINA en el `return`.** Todo el código posterior no se ejecuta.

```gml
/// @function        calc_cuadrado(valor)
/// @param {Real} valor  El valor al que calcular el cuadrado
/// @description     Devuelve el cuadrado, o 0 si no es un real
function calc_cuadrado(valor)
{
    if (!is_real(valor))
    {
        return 0;      // salida temprana
    }

    return (valor * valor);
}
```

> Si tu función **no tiene `return`** y compruebas su resultado, obtendrás `undefined`.

---

## 5. Method variables (métodos)

Un **method variable** es una variable a la que has asignado una función. Se «liga» (*bind*) a una instancia o struct.

### Sintaxis

```gml
// Recomendada para métodos
nombre = function(param1, param2)
{
    // ...
}
```

Dentro de un **struct literal** se usa `:` en vez de `=`:

```gml
struct =
{
    func : function(param1, param2)
    {
        // ...
    }
}
```

### Los tres ámbitos

```gml
// LOCAL
var _debug = function(mensaje)
{
    show_debug_message(mensaje);
}

// INSTANCIA
hacer_mates = function(v1, v2, v3)
{
    return (v1 * v2) - v3;
}

// GLOBAL
global.dist = function(_x1, _y1, _x2, _y2)
{
    return point_distance(_x1, _y1, _x2, _y2);
}
```

### ⚠️ Dónde está la variable vs dónde está ligada la función

> *«While the variable will be in the chosen scope, the actual function will be bound to the scope that it was initially defined in.»*

```gml
// En un Script (global, "unbound")
function crear_metodo()
{
    return function()      // ← esta función se liga a quien llame a crear_metodo()
    {
        show_debug_message($"Soy {object_get_name(object_index)}");
    };
}

// En el Create de obj_enemigo
mi_metodo = crear_metodo();   // ← ligada a la instancia de obj_enemigo
```

Aunque la función se definió en un script global, al crearla desde una instancia queda **ligada a esa instancia**.

### `self` dentro de un método

Durante la ejecución del método, **`self` apunta siempre a la instancia o struct al que está ligado**, sin importar desde dónde lo llames. Y todas las variables se leen y escriben en ese ámbito.

```gml
// Create de obj_enemigo
saludar = function()
{
    show_debug_message($"Hola, soy {nombre}");   // lee `nombre` del ENEMIGO
}

// Desde el jugador:
var _enemigo = instance_nearest(x, y, obj_enemigo);
_enemigo.saludar();   // lee el nombre del ENEMIGO, no del jugador
```

Puedes cambiar ese enlace con `method()` (ver sección 9).

### ✅ Nota útil sobre disponibilidad

Una función definida con **sintaxis de script function dentro de un evento de objeto** está disponible para sus instancias **durante toda su vida**, aunque ese evento no se haya ejecutado nunca.

```gml
// Definida en el evento Alarm 0
function auxiliar() { /* ... */ }

// Se puede llamar desde el Create, aunque Alarm 0 no llegue a ejecutarse
```

### Sobrescribir métodos

```gml
// Create de obj_padre
saludar = function() { show_debug_message("¡Soy el padre!"); }

// Create de obj_hijo
event_inherited();
saludar = function() { show_debug_message("¡Soy el hijo!"); }
// Todas las llamadas a saludar() en obj_hijo imprimen "¡Soy el hijo!"
```

### Argumentos opcionales en métodos

```gml
crear_adjunto = function(_adjunto, _x = x, _y = y)
{
    return instance_create_layer(_x, _y, layer, _adjunto);
}

crear_adjunto(obj_espada);          // usa x e y de la instancia
crear_adjunto(obj_espada, 100, 50); // posición explícita
```

### Los métodos SON structs (con una excepción)

Internamente, GameMaker guarda los métodos como structs que contienen:
- la referencia a la función de script a llamar,
- el struct o instancia al que está ligado.

Puedes acceder a ambos:

```gml
var _f = method_get_index(mi_metodo);   // la función de script
var _s = method_get_self(mi_metodo);    // la instancia/struct ligado
```

> **En la práctica esto es irrelevante**: llamas al método como función y lo pasas a otras funciones. Pero importa en un caso: la funcionalidad de static struct está **desactivada** en los method structs, para que `static_get()` sobre un método te devuelva el static de la función que hay detrás. Y `static_set()` sobre un método **no hace nada**.

---

## 6. `static` en funciones

Una variable `static` se define **la primera vez que se llama a la función** y mantiene su valor desde entonces. Solo se puede cambiar desde dentro de la función original.

```gml
contador = function()
{
    static num = 0;
    return num++;
}

repeat (10) { show_debug_message(contador()); }
// → 0 1 2 3 4 5 6 7 8 9
```

> ⚠️ **No puedes declarar `static` fuera de una función.**
> ⚠️ **No puedes leer un static de una función que nunca se ha llamado** → error y crash.

Más detalles y su uso en constructores: **tema 04**.

---

## 7. Closures (clausuras)

Una **closure** es una función que «recuerda» las variables del ámbito donde se creó, incluso después de que ese ámbito haya terminado.

```gml
function crear_contador()
{
    var _cuenta = 0;   // variable LOCAL de crear_contador

    return function()
    {
        _cuenta++;     // ← la función interna la "captura"
        return _cuenta;
    }
}

var _c1 = crear_contador();
show_debug_message(_c1());   // 1
show_debug_message(_c1());   // 2
show_debug_message(_c1());   // 3

var _c2 = crear_contador();  // contador INDEPENDIENTE
show_debug_message(_c2());   // 1
```

**¿Para qué sirve en un juego?** Para crear comportamientos parametrizados:

```gml
/// @desc Devuelve un método que aplica daño de un tipo concreto
function crear_aplicador_danio(_tipo, _multiplicador)
{
    return function(_objetivo, _base)
    {
        var _total = _base * _multiplicador;
        if (_objetivo.resistencias[$ _tipo] != undefined)
        {
            _total *= (1 - _objetivo.resistencias[$ _tipo]);
        }
        _objetivo.vida -= _total;
    }
}

// Uso
aplicar_fuego  = crear_aplicador_danio("fuego",  1.5);
aplicar_hielo  = crear_aplicador_danio("hielo",  0.8);

aplicar_fuego(obj_enemigo, 20);
```

> ⚠️ Recuerda: mientras guardes la closure, las variables capturadas **no se liberan**. Ten cuidado con closures que capturan structs o arrays grandes.

---

## 8. `script_execute()` y `script_execute_ext()`

Llaman a una función de script por su referencia.

```gml
script_execute(indice_o_funcion, arg0, arg1, ...);
script_execute_ext(indice_o_funcion, array_args, [offset], [num_args]);
```

```gml
// Directa
script_execute(mi_funcion, 10, "hola");

// Con array de argumentos (útil cuando no sabes cuántos hay)
var _args = [10, "hola", true];
script_execute_ext(mi_funcion, _args);
```

**Caso de uso real: llamar a un constructor sobre un struct ya existente.**

```gml
// ⚠️ Recuerda: NO puedes llamar a un constructor sin `new`...
// ...salvo con script_execute sobre un struct ya creado
var _struct = {};
script_execute(Arma, _struct);   // aplica el constructor Arma a _struct
```

---

## 9. `method()` y compañía

### `method(indice, instancia_o_struct)`

Crea un nuevo método ligando una función a un ámbito concreto.

```gml
var _metodo = method(mi_funcion_global, otra_instancia);
_metodo();   // se ejecuta con self == otra_instancia
```

Úsalo cuando quieras:
- Reutilizar una función global en el contexto de otra instancia.
- Pasar una función de script como callback ligado a algo.

```gml
// Pasar un script como callback (solución al problema de la sección 2)
llamada_indirecta(method(undefined, miscript), arg);
```

> `method(undefined, f)` crea un método **sin ligar** (unbound).

### Tabla de funciones de método

| Función | Qué devuelve |
|---|---|
| `is_method(v)` | ¿Es un método? |
| `method(f, obj)` | Un método ligado |
| `method_get_self(m)` | La instancia/struct al que está ligado (`undefined` si no está ligado) |
| `method_get_index(m)` | La función de script detrás del método |
| `method_call(m, args)` | Llama al método con un array de argumentos |

```gml
// Ejemplo: depurar el enlace de un método
if (is_method(mi_metodo))
{
    var _ligado_a = method_get_self(mi_metodo);
    show_debug_message($"Ligado a: {_ligado_a}");
}
```

---

## 10. Recursión

Una función que se llama a sí misma. **Necesita una condición de salida** o desbordarás la pila.

```gml
/// @desc Factorial recursivo (clásico de libro, no lo uses en producción)
function factorial(_n)
{
    if (_n <= 1) { return 1; }      // caso base ← OBLIGATORIO
    return _n * factorial(_n - 1);
}
```

**Caso de uso real en juegos: recorrer estructuras jerárquicas.**

```gml
/// @desc Cuenta todos los nodos de un árbol de UI
function contar_nodos(_nodo)
{
    var _total = 1;   // me cuento a mí

    var _hijos = _nodo.hijos;
    for (var i = 0; i < array_length(_hijos); i++)
    {
        _total += contar_nodos(_hijos[i]);
    }

    return _total;
}
```

> ⚠️ **Cuidado con la profundidad.** Cada llamada recursiva consume pila. Para recorridos muy profundos (miles de niveles), usa un bucle con una pila explícita (`ds_stack` o un array).

---

## 11. `with()` en profundidad

`with()` cambia el scope: *«ejecuta las siguientes líneas en el ámbito de X»*.

```gml
with (obj_enemigo)
{
    vida -= 10;                        // se aplica a CADA enemigo
    if (vida <= 0) { instance_destroy(); }
}
```

### Reglas importantes

- `X` puede ser: un **objeto** (todas sus instancias), una **instancia** concreta, un **struct**, o los keywords `all`, `other`, `self`, `noone`.
- Dentro del bloque, **`other`** es quien ejecuta el `with()`.

```gml
// En el jugador
with (instance_nearest(x, y, obj_enemigo))
{
    // `other` es el JUGADOR
    other.vida -= danio_contacto;   // el enemigo daña al jugador
}
```

- ⚠️ **Comprueba siempre el handle antes de `with()`.** Pasar `-1` ejecuta el bloque sobre `self` (porque `-1` es el valor legacy de `self`). Ver **tema 03**.

```gml
var _e = instance_nearest(x, y, obj_enemigo);
if (_e != noone)          // ✅ imprescindible
{
    with (_e) { vida -= 10; }
}
```

### El orden de ejecución dentro de `with(objeto)`

No está garantizado. Si necesitas orden, recorre las instancias tú:

```gml
// Orden por distancia al jugador
var _lista = [];
with (obj_enemigo)
{
    array_push(_lista, { inst: self, dist: point_distance(x, y, obj_jugador.x, obj_jugador.y) });
}
array_sort(_lista, function(_a, _b) { return _a.dist - _b.dist; });

for (var i = 0; i < array_length(_lista); i++)
{
    with (_lista[i].inst) { /* procesar en orden */ }
}
```

---

## 12. JSDoc y Feather

**Feather** es el analizador estático de GML. Lee tus comentarios JSDoc para entender los tipos y ayudarte.

### Forma recomendada

```gml
/// @function         registrar_danio(objetivo, cantidad)
/// @param {Id.Instance} objetivo  La instancia que recibe el daño
/// @param {Real}        cantidad  Puntos de daño
/// @description      Aplica daño a un objetivo y dispara efectos.
function registrar_danio(objetivo, cantidad)
{
    objetivo.vida -= cantidad;
}
```

### Etiquetas principales

| Etiqueta | Para qué |
|---|---|
| `@function` / `@func` | Declara la función y su firma |
| `@param {Tipo} nombre` | Documenta un parámetro |
| `@return` / `@returns` | Documenta el valor de retorno |
| `@description` / `@desc` | Descripción general |
| `@deprecated` | Marca la función como obsoleta |
| `@ignore` | Le dice a Feather que lo ignore |
| `@context` | Indica el ámbito esperado de la función |
| `@pure` | Indica que es una función pura (sin efectos secundarios) |
| `@self` | Indica a qué debe estar ligada |
| `@hint` | Pista para el autocompletado |

### Tipos que reconoce Feather

```
Real, String, Bool, Array, Struct, Id.Instance, Asset.GMObject,
Asset.GMSprite, Constant.IdDSList, Function, Any, ...
```

### Por qué molestarse

- **Autocompletado** correcto en el editor.
- **Detección de errores antes de compilar** (pasar un sprite donde va un objeto).
- **Avisos GM####**: por ejemplo **GM2043** si accedes a un `static` antes de su línea de inicialización.

> 💡 **Feather también analiza las expresiones dentro de los template strings** `$"...{ }"`.

---

## 13. Errores típicos y cómo evitarlos

### ❌ Olvidar que `argument[n]` no acepta `@`

```gml
function f()
{
    argument[@ 0] = 5;   // ❌ ERROR
}
```

### ❌ Creer que los argumentos son por referencia

```gml
function duplicar(_x)
{
    _x *= 2;      // afecta a la COPIA local
}

var _n = 5;
duplicar(_n);
show_debug_message(_n);   // 5 ← no cambió

// Solución: devolver
function duplicar(_x) { return _x * 2; }
_n = duplicar(_n);
```

> ⚠️ **Excepción:** arrays y structs **sí** se pasan por referencia (ver tema 05).

### ❌ Variables que «se escapan» al ámbito de la instancia

```gml
function calcular()
{
    resultado = 10;    // ❌ Sin `var`: crea una variable de INSTANCIA
}

// ✅
function calcular()
{
    var _resultado = 10;
    return _resultado;
}
```

### ❌ Usar `global.` innecesariamente en scripts para variables que quieres locales

```gml
// En un script, a nivel raíz:
contador = 0;    // ← es global.contador, no una local
```

### ❌ Pasar el nombre de un script como si fuera la función

```gml
MiScript(5);          // ✅ si el script se llama igual que la función
ejecutar(MiScript);   // ❌ pasas el ÍNDICE, no la función
ejecutar(method(undefined, MiScript));  // ✅
```

---

## 14. Plantilla de script bien formado

```gml
/// @function         aplicar_danio(objetivo, cantidad, tipo)
/// @param {Id.Instance} objetivo   Instancia que recibe el daño
/// @param {Real}        cantidad   Puntos de daño base
/// @param {String}      tipo       "fisico" | "fuego" | "hielo" | "veneno"
/// @return {Real}                  Daño efectivo aplicado
/// @description      Aplica daño considerando resistencias. Devuelve el daño real.
///                   Si el objetivo muere, dispara su callback al_morir().
/// @pure false
function aplicar_danio(objetivo, cantidad, tipo = "fisico")
{
    // Validación defensiva
    if (objetivo == noone)          { return 0; }
    if (!instance_exists(objetivo)) { return 0; }

    with (objetivo)
    {
        // Resistencia: 0 = inmune, 0.5 = mitad de daño
        var _resistencia = variable_instance_exists(id, "resistencias")
            ? (resistencias[$ tipo] ?? 0)
            : 0;

        var _dano_real = cantidad * (1 - clamp(_resistencia, 0, 1));
        vida -= _dano_real;

        if (vida <= 0)
        {
            vida = 0;
            al_morir();
        }

        return _dano_real;
    }
}
```

**Por qué está bien:**
- JSDoc completo → Feather te ayuda.
- Validación defensiva de handles (`!= noone`, `instance_exists`).
- Argumento opcional con valor por defecto sensato.
- `with()` para operar en el ámbito del objetivo.
- Devuelve información útil al llamador.
- Usa `??` (nullish) para un fallback limpio.

---

## Resumen

| Concepto | Regla |
|---|---|
| `function nombre()` en Script | Función global, con índice de script. **La recomendada para scripts.** |
| `nombre = function()` | Method variable, ligada al ámbito. **La recomendada para structs/instancias.** |
| Constructores con herencia | **Solo** sintaxis `function nombre()` |
| Argumentos | `argument0..N`, `argument[n]`, `argument_count` |
| Opcionales | `param = valor` (puede ser una **expresión** que se evalúa solo si falta) |
| `return` | Termina la ejecución ahí mismo |
| `static` | Se inicializa en la primera llamada y persiste |
| `method(f, obj)` | Reenlaza una función a otro ámbito |
| `script_execute` | Llama por referencia (y permite aplicar constructores) |
| `with(x)` | Cambia el scope; `other` es el llamador. **Comprueba `noone` antes.** |
| Feather / JSDoc | Documenta con `/// @param` para autocompletado y detección de errores |
