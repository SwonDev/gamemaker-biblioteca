# 06 · Curso de GML en vídeo (español) — transcripción estructurada

> **Fuente:** [*Introducción Completa al Lenguaje de programación Game Maker 2024*](https://youtu.be/UneMzjBKODs)
> de [Altair_AML](https://www.youtube.com/channel/UCMP5XWWzhJ_A6DPNKNfQVOw) · **52 min 49 s** · 21-03-2024.
>
> Es **la mejor clase de GML que existe en español**. Aquí está transcrita, reordenada en
> capítulos y con el código escrito, para que puedas leerla sin ver el vídeo — y para que un
> agente pueda consultarla.
>
> ⚠️ **Anotaciones de 2026 marcadas con 🔺.** El vídeo es de 2024: donde algo ha cambiado en
> LTS 2026, se dice y se enlaza a la página correspondiente de esta biblioteca.

---

## Cómo está montado el curso

El autor crea un proyecto vacío con **un solo objeto** y va probando todo en su evento
**Create**, saltando a **Step** o **Draw** cuando hace falta. No hay sprites ni assets: es
puro lenguaje.

> 💡 **Consejo del autor, y buen consejo:** cuando GameMaker te pregunte si quieres GML Code o
> GML Visual, **elige código desde el principio**. Pasar de visual a código después cuesta más
> que aprender código directamente.

**Índice**

| # | Bloque | Minuto |
|---|---|---|
| 1 | [Comentarios](#1-comentarios) | 02:00 |
| 2 | [Variables: los seis tipos](#2-variables-los-seis-tipos) | 03:00 |
| 3 | [Arrays](#3-arrays) | 09:00 |
| 4 | [Structs](#4-structs) | 12:00 |
| 5 | [Dónde se declara cada variable](#5-dónde-se-declara-cada-variable) | 14:00 |
| 6 | [Condiciones: `if` y operadores](#6-condiciones-if-y-operadores) | 16:00 |
| 7 | [`else` y `else if`](#7-else-y-else-if) | 22:00 |
| 8 | [`switch`](#8-switch) | 24:00 |
| 9 | [`with` y `other`](#9-with-y-other) | 25:30 |
| 10 | [Ciclos: `repeat`, `for`, `while`, `do until`](#10-ciclos) | 28:00 |
| 11 | [`break`, `continue`, `exit`](#11-break-continue-y-exit) | 36:00 |
| 12 | [Funciones](#12-funciones) | 39:00 |
| 13 | [Métodos y `return`](#13-métodos-y-return) | 48:00 |
| 14 | [`show_debug_message`](#14-show_debug_message) | 51:00 |

---

## 1. Comentarios

**[02:00]** Lo primero que el autor considera importante en GML: **los comentarios**.

> *«Si tú no divides un poco tu código, no lo ordenas, no nombras "esta parte del código es un
> inventario", va a ser muy complicado que un día dejes tu proyecto una semana y vuelvas.»*

```gml
// Comentario de una línea

/*
   Comentario
   de varias líneas
*/
```

📖 Más sobre estilo y organización en
[`05 - Referencia/04 · Convenciones y estilo GML`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md).

---

## 2. Variables: los seis tipos

**[03:00]** *«Una variable, en términos muy simples, es un dato que tú escribes y que almacena
un tipo de dato: numérico, un texto, verdadero o falso. También puede guardar funciones.»*

El editor las **colorea por tipo**, y ese color es la forma rápida de saber qué es cada cosa.

### 2.1 · Variable de instancia (azul)

```gml
objeto = 0;
```

Vive en **todo el objeto**: la declaras en un evento y la puedes leer en cualquier otro evento
del mismo objeto. También se puede llamar desde otros objetos.

### 2.2 · Variable local (amarilla) — `var`

```gml
var _objeto = 0;
```

**Solo existe en el evento (o la función) donde la declaras.** Si la creas en el Create y la
intentas usar en el Step, no está: se creará otra distinta.

> 🔺 **Convención de 2026:** las locales se nombran con guion bajo delante (`var _objeto`).
> El vídeo no lo hace; hazlo tú. Ver [`05 - Referencia/04`](../05%20-%20Referencia/04%20-%20Convenciones%20y%20estilo%20GML.md).

### 2.3 · Variable global — `global.`

```gml
global.vida = 100;
```

*«Como su nombre indica, tiene alcance global: se puede usar en cualquier objeto, en cualquier
script, en cualquier parte del código.»*

> *«No tengan miedo de usar variables globales, no es que gasten una infinidad de memoria.»*
> Normalmente se usan para **datos del proyecto y ficheros de guardado**.

### 2.4 · Constante — `#macro`

```gml
#macro CAM_VIEW_X    camera_get_view_x(view_camera[0])
#macro VELOCIDAD_MAX 8
```

**Se escriben en MAYÚSCULAS** por convención, para no confundirlas con variables normales. Su
valor **no cambia**. Se usan para números que repites mucho.

### 2.5 · Variable incorporada de instancia (verde)

`x`, `y`, `image_index`, `sprite_index`, `depth`… Las crea GameMaker en cada instancia y
**controlan un aspecto del objeto**. Casi todas se pueden modificar.

```gml
x = 100;              // mueve la instancia
image_blend = c_red;  // la tiñe de rojo
```

📖 Las 210 variables incorporadas están listadas en
[`08 - Referencia GML completa/_API del runtime/API-variables.md`](../08%20-%20Referencia%20GML%20completa/_API%20del%20runtime/API-variables.md).

### 2.6 · Variable estática — `static`

```gml
function contar()
{
    static _n = 0;   // solo se inicializa la PRIMERA vez
    _n += 1;
    return _n;
}
```

**Solo se puede declarar dentro de una función.** La diferencia con una local: una `var` vuelve
a valer 0 cada vez que se ejecuta la función; una `static` **conserva su valor** entre
llamadas.

> *«Si esta es una variable estática y vale 0, y aquí tú dices "ahora quiero que sea 50",
> cuando dé la vuelta de nuevo ya no va a ser 0, va a ser 50.»*

---

## 3. Arrays

**[09:00]** *«Es como la primera variable que hicimos, pero puede almacenar muchos más datos.»*

```gml
var _inventario = [];                 // vacío
var _inventario = ["espada", "escudo", "poción"];
```

Se usan para **inventarios, menús complejos** y todo lo que necesite guardar muchos datos.

### Arrays + ciclos: el ejemplo del vídeo

```gml
var _datos = [];

for (var i = 0; i < 10; i++)
{
    _datos[i] = irandom(10);   // un número aleatorio de 0 a 10 en cada posición
}
```

> *«El ciclo se va a ejecutar 10 veces y en cada ejecución va a soltar un número distinto. Si
> no, tendrías que crear objeto A, objeto B… sería un lío.»*

📖 Las 41 funciones de array en
[`08 - Referencia GML completa/14 · Arrays`](../08%20-%20Referencia%20GML%20completa/14%20-%20Arrays.md).

---

## 4. Structs

**[12:00]** *«Los structs son como una combinación entre un array y una variable normal.»*

```gml
equipamiento =
{
    item   : "espada",
    dinero : 1000,
    danio  : 25,
};
```

Dos diferencias clave con un array, y el autor las señala bien:

1. **Dentro del struct se usan dos puntos `:`, no el igual `=`.**
2. **Los datos tienen nombre**, así que buscarlos es mucho más fácil que con índices numéricos.

Se leen con el punto:

```gml
show_debug_message(equipamiento.item);   // "espada"
equipamiento.dinero += 500;
```

> *«También se puede meter un array dentro del struct, y otro struct dentro del struct. Y
> también funciones. Es una muy buena forma de almacenar datos.»*

> 🔺 **Lo que el vídeo deja fuera:** los **constructores** (`function Cosa() constructor {}`),
> la herencia con `:` y `static` dentro de constructores. El propio autor lo dice: *«aún me
> faltó hablar de los constructores, eso da para un vídeo aparte»*. Ese vídeo no existe.
> **Está cubierto aquí:** [`01 - Fundamentos/04 · Structs y constructores (POO en GML)`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md).

---

## 5. Dónde se declara cada variable

**[14:00]** Esta es la parte más práctica del vídeo. Regla resumida:

| Tipo | Dónde declararla | Por qué |
|---|---|---|
| Instancia (azul) | **Create** | Si la declaras en Step se reinicia en cada paso del juego |
| Local (`var`, amarilla) | Cualquier evento, ciclos, funciones | Solo vive ahí |
| Global (`global.`) | Un **asset de script**, o el Create de un controlador | Para que exista antes que nadie |
| Macro (`#macro`) | Un **asset de script** | Igual que las globales |
| Incorporada (verde) | Ya existe | Solo se modifica |
| Arrays y structs | **Create**, o una vez dentro de una función | Igual que las de instancia |

> ⚠️ **El error clásico:** declarar en el evento **Step**. *«El Step se ejecuta en cada paso del
> juego, entonces la variable nunca va a cambiar su valor, o si lo cambia va a volver al mismo
> valor con el que se declaró.»*

📖 [`01 - Fundamentos/06 · Eventos y ciclo del juego`](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md).

---

## 6. Condiciones: `if` y operadores

**[16:00]** *«Una condición es como una pregunta que le vamos a hacer al programa.»*

```gml
if (objeto == 0)
{
    // se ejecuta solo si la pregunta es cierta
}
```

### Operadores

| Operador | Significado | Nota del vídeo |
|---|---|---|
| `==` o `=` | Igual | *«Es lo mismo si lo dejamos así o así»* 🔺 usa siempre `==` para comparar |
| `>=` `<=` `>` `<` | Mayor o igual, menor o igual, mayor, menor | Los matemáticos básicos |
| `&&` (`and`) | **Ambas** condiciones ciertas | |
| `\|\|` (`or`) | **Cualquiera** de las dos | |
| `^^` (`xor`) | Una cierta **y** la otra falsa | *«No lo he ocupado mucho, pero es muy bueno»* |
| `!` | Negación | `if (!espada)` es lo mismo que `if (espada == false)` |
| `+ - * /` | Aritméticos | |

```gml
if (objeto == 0 && _objeto == 0) { }   // las dos
if (objeto == 1 || _objeto == 0) { }   // cualquiera
if (!espada) { }                       // si espada es falso
```

> 💡 **Consejo importante del autor:** *«Usen paréntesis. Si hacen muchos cálculos es probable
> que el programa no entienda muy bien cuál es el orden de ejecución.»*

```gml
resultado = ((a + b) * c) / d;   // sin ambigüedad
```

---

## 7. `else` y `else if`

**[22:00]**

```gml
if (equipamiento.espada == true)
{
    // se ejecuta si es verdadero
}
else
{
    // se ejecuta en cualquier otro caso
}
```

Y encadenando preguntas:

```gml
if (equipamiento.dinero >= 1000)      { /* … */ }
else if (equipamiento.dinero >= 100)  { /* … */ }
else                                   { /* … */ }
```

> *«No tengan miedo de usar muchas condiciones `if`, muchas `else if`. Con el tiempo van a
> decir "uy, aquí me iría mejor un `switch`". Eso lo van a ir aprendiendo.»*

---

## 8. `switch`

**[24:00]** *«Es parecido a `if`, pero te ayuda a ordenar más el código.»*

```gml
switch (equipamiento.dinero)
{
    case 100:  /* … */ break;
    case 500:  /* … */ break;
    case 1000: /* … */ break;
    default:   /* si ninguno coincide */ break;
}
```

> *«Sería mucho más rápido que hacer `if`, `else`, `else if`, muchísimo más rápido.»*
> 🔺 **Matiz honesto:** el propio autor duda de la parte de rendimiento (*«de esto no estoy
> seguro, no les voy a mentir»*). Y hace bien: la razón real para usar `switch` es la
> **legibilidad** cuando comparas una misma expresión contra muchos valores, no la velocidad.

> ⚠️ **No olvides el `break`.** Sin él, la ejecución cae al siguiente `case`.

---

## 9. `with` y `other`

**[25:30]** *«Lo que hace `with` es entrar en ese objeto, y todo lo que escribas ahí es como si
estuvieras dentro de ese objeto.»*

```gml
with (obj_enemigo)
{
    hp -= 10;          // hp de CADA enemigo
    instance_destroy();
}
```

Dentro de un `with` —o de un evento de colisión— **`other` es el objeto desde el que llamaste**:

```gml
with (obj_enemigo)
{
    x = other.x;   // other.x es la x de quien ejecutó el with
}
```

> *«Sé que es un poco complicado. Recomiendo repasar con la guía de GameMaker: su documentación
> está muy pero muy bien explicada.»*

> 🔺 **Sobre el manual en español**, el autor añade algo que esta biblioteca ha verificado:
> *«También está en español. No estoy seguro si la traducción la hicieron con IA porque siento
> que hay algunas palabras erróneas; por eso recomendaría leerlo en inglés.»*
> **Tenía razón a medias**: la traducción oficial es humana pero está **al 86 %** y data de
> 2021-2022. Los detalles y el manual completo en ambos idiomas están en
> [`09 - Manual oficial`](../09%20-%20Manual%20oficial/README.md).

📖 [`01 - Fundamentos/09 · Instancias, objetos y herencia`](../01%20-%20Fundamentos/09%20-%20Instancias%2C%20objetos%20y%20herencia.md).

---

## 10. Ciclos

**[28:00]** *«Un ciclo es una ejecución del código que se ejecuta muchas veces.»*

El autor los ordena por cuánto los usa: **`for` > `repeat` > `while` > `do until`**.

### 10.1 · `repeat` — el más sencillo

```gml
repeat (50)
{
    instance_create_layer(x, y, "Instances", obj_particula);
}
```

*«El código se va a ejecutar el número de veces que dice ahí. Lo bueno es que acorta mucho el
código.»* Es el que **menos errores** permite cometer.

### 10.2 · `for` — el más útil

```gml
for (var i = 0; i < 50; i++)
{
    // …
}
```

**El ejemplo bueno del vídeo: dibujar una columna de inventario.**

```gml
for (var i = 0; i < 10; i++)
{
    draw_sprite(spr_item, 0, x, y + (16 * i));
}
```

> *«El primer ciclo dibuja el sprite en la posición `y`, en el siguiente lo multiplica por 1,
> así que 16 píxeles más abajo, después por 2, 32 píxeles más abajo… Me dibuja una columna de
> todos los sprites con separaciones de una manera muy fácil.»*

> ⚠️ **La advertencia sincera del autor:** *«A mí me ocurrieron cinco pantallazos azules por
> usar mal este ciclo.»* El peligro es una condición que **nunca se cumple** → ciclo infinito.
> Si te pasa: administrador de tareas y cerrar. No rompe nada.

### 10.3 · `while`

```gml
while (condicion)
{
    // se ejecuta mientras la condición sea cierta
}
```

Mismo riesgo de ciclo infinito. Úsalo solo cuando no sepas de antemano cuántas vueltas hacen falta.

### 10.4 · `do … until`

```gml
do
{
    // …
}
until (condicion);
```

> *«Nunca he visto a nadie usando este ciclo. Yo tampoco lo he usado nunca.»*
> 🔺 Sí tiene un caso propio: cuando el cuerpo **debe ejecutarse al menos una vez** antes de
> comprobar la condición.

📖 Recetas donde los ciclos son imprescindibles:
[`04 - Recetas por género/05 · Roguelike y generación procedural`](../04%20-%20Recetas%20por%20g%C3%A9nero/05%20-%20Roguelike%20y%20generaci%C3%B3n%20procedural.md).

---

## 11. `break`, `continue` y `exit`

**[36:00]**

| Palabra | Qué hace |
|---|---|
| `break` | **Rompe** el ciclo por completo. También cierra un `case` de `switch` |
| `continue` | **Salta el resto de esta vuelta** y pasa a la siguiente. No rompe el ciclo |
| `exit` | **Deja de ejecutar el resto del evento o la función** |

```gml
for (var i = 0; i < 100; i++)
{
    if (equipamiento.espada == true) break;      // sale del ciclo
    if (i == 25)                     continue;   // salta a i = 26
    instance_create_layer(x, y, "Instances", obj_arma);
}
```

```gml
// En un evento Step
if (equipamiento.dinero == 1000) exit;
// nada de lo que haya debajo se ejecuta
```

> *«Los ciclos son indispensables para un buen orden en el proyecto. Para hacer menús es casi
> imposible hacerlos sin ciclos. O puede que hagas un menú, pero muy básico. Si quieres un
> inventario ya va a ser casi imposible.»*

---

## 12. Funciones

**[39:00]** *«Una función se puede definir como un comando que le das a la computadora.
Supongamos que tiene dos argumentos, A y B, y quiero que los sume: le digo "súmame estos
valores" y me devuelve la suma.»*

### Las funciones incorporadas

*«En GameMaker hay muchas, un listado enorme. Tendría que hacer un vídeo de 10 horas para
explicarlas todas.»*

> 🔺 **Son exactamente 2 357.** Están todas catalogadas, con firma y tipo de retorno, en
> [`08 - Referencia GML completa/_API del runtime/API-funciones.md`](../08%20-%20Referencia%20GML%20completa/_API%20del%20runtime/API-funciones.md).
> Y para comprobar una concreta: `python3 "_indice/buscar.py" instance_create_layer`.

Las que el autor destaca como más usadas:

```gml
instance_place(x, y, obj_pared);                       // ¿hay algo en esa posición?
instance_create_layer(x, y, "Instances", obj_bala);    // crear
instance_destroy();                                    // destruir
```

> **Lo más importante que dice de las funciones:** *«El 90-95 % de las funciones te van a
> devolver un dato. Es muy recomendable al 100 % que lean bien qué devuelve cada función,
> porque ahí es donde radican muchos errores.»*

Y señala que **Feather** te lo muestra al pasar el ratón por encima, sin salir del editor.

### Crear tus propias funciones

```gml
function crear_arma(_nombre, _danio, _tipo)
{
    return instance_create_layer(x, y, "Instances", obj_arma,
    {
        nombre : _nombre,
        danio  : _danio,
        tipo   : _tipo,
    });
}
```

El último argumento de `instance_create_layer` es **un struct de variables** que se crean en la
instancia nueva en el momento de crearla, sin tener que declararlas en el objeto.

Y se usa así:

```gml
crear_arma("Espada corta", 25, "corte");
```

> *«Si ocurre algún bug tú dices "este bug está en la función que crea armas", vas a esa
> función y solo a esa función. Es una de las ventajas, por eso es muy importante usar
> funciones.»*

### Argumentos por defecto

```gml
function crear_arma(_nombre = "", _danio = 1, _tipo = "corte")
{
    // si no pasas un argumento, se usa el valor por defecto
}
```

### Dónde se declaran

- En un **asset de script** o en el **Create** de un objeto → disponible para todos los objetos.

> *«En las funciones es donde más vas a usar las variables locales, porque ahí solo las va a
> leer la función. Si creas una variable normal es posible que la cree para el objeto, y puede
> que haya errores.»*

📖 [`01 - Fundamentos/07 · Funciones, métodos y ámbito`](../01%20-%20Fundamentos/07%20-%20Funciones%2C%20m%C3%A9todos%20y%20%C3%A1mbito.md).

---

## 13. Métodos y `return`

**[48:00]** Si quieres una función que **solo sirva para un objeto**, eso es un **método**:

```gml
// En el Create del objeto
crear = function()
{
    // solo tiene alcance en este objeto
};
```

```gml
crear();   // se llama así
```

### `return`

```gml
function crear_arma()
{
    var _id = instance_create_layer(x, y, "Instances", obj_arma);
    return _id;        // devuelve el handle del arma creada
}

var _arma = crear_arma();   // y aquí lo recoges
```

> *«Puedes usar una variable local, te va a devolver la ID y además va a crear ese objeto.»*

---

## 14. `show_debug_message`

**[51:00]** La función que más vas a usar para depurar:

```gml
show_debug_message("mensaje");
show_debug_message(equipamiento.dinero);
show_debug_message($"vida = {vida}, x = {x}");   // 🔺 plantillas de cadena, GML moderno
```

Lo que imprimas aparece en la ventana **Output** del IDE.

> *«Se usa mucho para buscar bugs. Si dices "no sé qué está pasando aquí, no sé qué me está
> devolviendo esta variable", usas esta función y revisas.»*

📖 [`01 - Fundamentos/15 · Depuración y rendimiento`](../01%20-%20Fundamentos/15%20-%20Depuraci%C3%B3n%20y%20rendimiento.md)
y, para el Debug Overlay completo, `python3 "_indice/buscar.py" --listar dbg_`.

---

## Lo que el vídeo NO cubre (y dónde está)

| Tema | El autor dice | Dónde está en esta biblioteca |
|---|---|---|
| **Constructores** | *«Da para un vídeo aparte»* — que no se hizo | [`01 - Fundamentos/04`](../01%20-%20Fundamentos/04%20-%20Structs%20y%20constructores%20%28POO%20en%20GML%29.md) |
| **Handles** (el cambio de 2026) | No existía en 2024 | [`01 - Fundamentos/03`](../01%20-%20Fundamentos/03%20-%20Handles%20-%20el%20cambio%20clave%20de%202026.md) 🔴 |
| **`delta_time`** y time sources | — | [`01 - Fundamentos/06`](../01%20-%20Fundamentos/06%20-%20Eventos%20y%20ciclo%20del%20juego.md) |
| **UI Layers y Flexpanels** | No existían | [`02 - Novedades 2026/04`](../02%20-%20Novedades%202026/04%20-%20UI%20Layers%20y%20Flexpanels.md) |
| **Buses y efectos de audio** | No existían | [`02 - Novedades 2026/07`](../02%20-%20Novedades%202026/07%20-%20Audio%20-%20buses%20y%20efectos.md) |
| **Partículas nuevas** | No existían | [`02 - Novedades 2026/05`](../02%20-%20Novedades%202026/05%20-%20Sistema%20de%20part%C3%ADculas%20nuevo.md) |
| **Colisiones y movimiento** | Fuera del alcance | [`01 - Fundamentos/08`](../01%20-%20Fundamentos/08%20-%20Movimiento%20y%20colisiones.md) |
| **Cámaras** | Fuera del alcance | [`01 - Fundamentos/10`](../01%20-%20Fundamentos/10%20-%20Rooms%2C%20capas%2C%20c%C3%A1maras%20y%20viewports.md) |

---

## Los otros vídeos del mismo autor

Continúan donde este acaba, y también están en español:

| Vídeo | Duración | Qué cubre |
|---|---:|---|
| [Introducción a los EVENTOS](https://youtu.be/tPUNtpHVFSw) | 16:17 | Create, Step, Draw, Alarm, Collision y su orden |
| [Interfaz General](https://youtu.be/KRJhX4YgcHo) | 17:08 | Recorrido por el IDE |
| [¿Qué son los Structs?](https://youtu.be/gzRbXITRS9Q) | 3:49 | Repaso rápido de structs |
| [Mejora tu proyecto con INPUT](https://youtu.be/mcJ86swsjNE) | 11:00 | Integrar la librería **Input** |
| [Diálogos con Scribble](https://youtu.be/rxsPzpbBv74) | 7:23 | Integrar **Scribble** |
| [Approach, un script indispensable](https://youtu.be/niwwb1zd3vg) | 2:00 | La función `approach` |

Detalle completo en [`02 · Altair_AML — GameMaker 2024`](./02%20-%20Altair%20AML%20-%20GameMaker%202024.md).

---

## Método de esta transcripción

Los subtítulos originales en español se descargaron con
`yt-dlp --write-auto-subs --sub-langs es-orig`, se limpiaron y se reordenaron en capítulos.
**Las citas entre comillas son literales del autor**; el código está reescrito por esta
biblioteca (el vídeo lo teclea en pantalla y los subtítulos no lo recogen), verificado
función por función contra `_indice/buscar.py`. Las marcas 🔺 son anotaciones nuestras de 2026.
