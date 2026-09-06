# 14 · DragoniteSpam — Los fundamentos del código

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 2 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=_oKYg3VWgOo> |
| **Duración** | 26 min 47 s |
| **Publicado** | 25 de noviembre de 2025 |
| **Nivel** | Principiante absoluto (sin conocimientos previos de programación) |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | variables, operadores, funciones, `if`/`else`, strings, `keyboard_check`, `ord()` |

«Hoy vamos a aprender sobre código. Y voy a empezar desde el principio mismo. Si nunca
has programado en ningún lenguaje, no te preocupes: lo haremos paso a paso.»

## Índice de contenido

1. Aprender un lenguaje nuevo no es empezar de cero
2. Expresiones y variables
3. El punto y coma
4. Operadores matemáticos y orden de operaciones
5. Abreviaturas: `+=`, `-=`, `++`, `--`
6. Funciones
7. Valores especiales: `pi`, `infinity`, `true`, `false`
8. Sentencias y control de flujo: `if`, `else`
9. Cadenas de texto (strings)
10. El evento Step y sus tres variantes
11. Variables integradas: `x`, `y`, `mouse_x`, `mouse_y`
12. Seguir al ratón
13. Leer el teclado: `keyboard_check()` y compañía
14. El sistema de coordenadas de GameMaker
15. El truco de la resta de booleanos
16. Teclas de letra: la función `ord()`

---

## 1. Aprender un lenguaje nuevo no es empezar de cero

> Aprender un lenguaje de programación nuevo se parece mucho más a pasar del **español
> al portugués** que del español al **cantonés**.

Salvo excepciones muy raras, **todos los lenguajes se parecen y tienen la misma
anatomía**. Así que si ya has tocado JavaScript (el más parecido a GML), Python, Lua o
C/C++, gran parte de esto te resultará familiar. Y si no, no importa.

---

## 2. Expresiones y variables

Un programa de ordenador —juego o no— es **una serie de instrucciones paso a paso** que
se siguen para que ocurra algo interesante. No hace falta ser un genio de las
matemáticas, pero si sobreviviste a una clase de álgebra, mucho de esto te sonará.

La unidad más pequeña de código con significado es una **expresión**: un fragmento de
código que **representa un valor**.

```gml
player_health = 10;
```

- `player_health` es una **variable**.
- La variable contiene el valor `10`.
- Más adelante podemos consultarla, cambiarla, compararla, o comprobar si es `<= 0` para
  que el jugador caiga muerto.

También puedes referenciar una variable dentro de otra asignación:

```gml
max_player_health = 10;
current_player_health = max_player_health;   // Ahora vale 10
```

---

## 3. El punto y coma

El `;` es como **el punto de una frase**: le indica al ordenador que la línea ha
terminado.

> **Estrictamente no es necesario** en la mayoría de sitios de GameMaker, pero el autor
> recomienda ponerlo siempre: hay **situaciones raras en las que omitirlo resulta
> ambiguo**, y eso puede producir errores difíciles de ver si no prestas atención.

---

## 4. Operadores matemáticos y orden de operaciones

Los cuatro operadores aritméticos atómicos:

```gml
+   suma
-   resta
*   multiplicación
/   division
```

Y se pueden encadenar en expresiones tan complejas como quieras.

> **Cuida el orden de operaciones.** Las subexpresiones entre paréntesis se evalúan
> primero.

```gml
(10 + 20) / 2   // 30 / 2 = 15
10 + 20 / 2     // 10 + 10 = 20
```

---

## 5. Abreviaturas: `+=`, `-=`, `++`, `--`

Puedes asignar y referenciar la misma variable en una sola expresión:

```gml
current_player_health = current_player_health - 1;   // Baja de 10 a 9
```

Como esto es muy común, existen atajos:

| Forma larga | Abreviatura |
|---|---|
| `x = x + 1` | `x += 1` |
| `x = x - 1` | `x -= 1` |
| `x = x * 2` | `x *= 2` |
| `x = x / 2` | `x /= 2` |

Y para el caso concreto de sumar o restar **exactamente 1**:

```gml
current_player_health++;   // Suma 1
current_player_health--;   // Resta 1
```

> Existe la forma **prefija** (`++variable`), y la verás en código de otras personas. Si
> estás empezando, **no te preocupes por ella**: usa siempre la **postfija**
> (`variable++`).

---

## 6. Funciones

Las funciones de GameMaker se parecen a las de la clase de matemáticas:

| Función | Qué hace |
|---|---|
| `sign()` | Signo de un número |
| `cos()` | Coseno |
| `sqrt()` | Raíz cuadrada |
| `log2()`, `log10()`, `logn()` | Logaritmos |
| `round()` | Redondear |
| `ceil()` | Redondear **hacia arriba** |
| `floor()` | Redondear **hacia abajo** |

Se llaman escribiendo el nombre, un par de paréntesis y los **argumentos** dentro:

```gml
current_player_health = sqrt(max_player_health);
```

Y se pueden **encadenar**: la salida de una se convierte en la entrada de la siguiente.

```gml
current_player_health = floor(sqrt(max_player_health));
```

Y formar parte de expresiones más grandes:

```gml
current_player_health = floor(sqrt(max_player_health)) + 5;
```

> Además de las matemáticas puras, hay **muchísimas funciones más** centradas en el
> juego: crear instancias, leer el teclado…

---

## 7. Valores especiales: `pi`, `infinity`, `true`, `false`

| Constante | Valor |
|---|---|
| `pi` | 3,141592653… |
| `infinity` | El concepto de infinito (puede ser positivo o negativo) |
| `true` | Equivale literalmente a **1** |
| `false` | Equivale literalmente a **0** |

> `true` y `false` son **literalmente** 1 y 0, pero **conceptualmente** representan
> valores de lógica binaria.

---

## 8. Sentencias y control de flujo: `if`, `else`

Una **sentencia** es una línea de código que **no representa necesariamente un valor**.

La más común es `if`:

```gml
if (current_player_health < 0)
{
    // Código para que el jugador muera
}
```

Dentro de los paréntesis va una **expresión lógica** (no aritmética) que se resuelve a
verdadero o falso. Operadores lógicos:

| Operador | Significado |
|---|---|
| `<` | menor que |
| `>` | mayor que |
| `>=` | mayor o igual |
| `<=` | menor o igual |
| `==` | igual (comparación) |
| `!=` | distinto |

Todo el código entre las **llaves** solo se ejecuta si la condición es verdadera.

### `else` y `else if`

```gml
if (current_player_health == 0)
{
    // Caer muerto
}
else if (current_player_health <= 5)
{
    // Esa música molesta de «poca vida» tipo Pokémon
}
else
{
    // Seguir vivo  ← el comodín final
}
```

Puedes encadenar tantos `else if` como quieras, y el `else` final actúa como **cajón de
sastre**.

Todo esto en conjunto se llama **control de flujo**. (La otra gran pata del control de
flujo son los **bucles**, que se verán más adelante.)

---

## 9. Cadenas de texto (strings)

Además de números, una variable puede guardar **texto**: es lo que se llama una
**cadena** o *string*.

```gml
player_name = "Michael";
```

> **El texto debe ir entre comillas dobles.** Si lo escribes sin ellas, GameMaker no
> sabrá qué hacer con él y **el juego se cerrará de golpe**.

Hay muchísimas funciones para manipular cadenas, igual que las hay para números. En los
juegos se maneja texto constantemente.

---

## 10. El evento Step y sus tres variantes

El evento **Step** ocurre **cada fotograma** del juego. Si quieres que algo ocurra de
forma continua, ponlo ahí.

En realidad hay **tres** eventos Step:

| Evento | Cuándo |
|---|---|
| **Begin Step** | **Antes** de que los demás objetos ejecuten su Step |
| **Step** | El normal |
| **End Step** | **Después** de que los demás objetos ejecuten su Step |

Sirven para cuando necesitas que tu lógica ocurra antes o después que la del resto. Para
un ejemplo pequeño basta con el Step normal.

---

## 11. Variables integradas: `x`, `y`, `mouse_x`, `mouse_y`

GameMaker tiene un puñado de variables integradas. Algunas pertenecen a cada instancia:

| Variable | Contenido |
|---|---|
| `x`, `y` | Posición del objeto en pantalla |
| `sprite_index` | El sprite asignado al objeto |
| `image_index` | El subimage (fotograma) concreto dentro del sprite |
| `mouse_x`, `mouse_y` | Posición del **cursor del ratón en el mundo del juego** |

> «Algo que me oiréis decir mucho en esta serie es que **en GameMaker suele haber como
> cinco formas distintas de hacer lo mismo**.»

Por ejemplo, para leer la posición del ratón también existen las funciones
`window_mouse_get_x()` y `window_mouse_get_y()`, que devuelven la posición en otro
sistema de referencia. El autor las ignora por ahora para mantenerlo simple.

---

## 12. Seguir al ratón

```gml
x = mouse_x;
y = mouse_y;
```

Con esas dos líneas en el Step, el objeto **sigue al cursor por la pantalla**.

> Ya tenemos **interactividad**, que es una de las cosas que separan a los juegos de
> casi cualquier otro medio.

---

## 13. Leer el teclado: `keyboard_check()` y compañía

Hay tres funciones según lo que necesites:

| Función | Devuelve verdadero si… |
|---|---|
| `keyboard_check(tecla)` | La tecla **está pulsada** (mantenida) |
| `keyboard_check_pressed(tecla)` | La tecla **se acaba de pulsar** en este fotograma |
| `keyboard_check_released(tecla)` | La tecla **se acaba de soltar** en este fotograma |

Las tres reciben el **código de tecla**. Los códigos llevan el prefijo **`vk_`**
(*virtual keyboard*, como se llaman en la documentación del sistema operativo):
`vk_backspace`, `vk_control`, `vk_enter`, `vk_escape`, las teclas de función, y por
supuesto `vk_right`, `vk_left`, `vk_up`, `vk_down`.

```gml
if (keyboard_check(vk_right) == true)
{
    x += 2;
}
```

Y lo mismo para las otras tres direcciones:

```gml
if (keyboard_check(vk_right)) { x += 2; }
if (keyboard_check(vk_left))  { x -= 2; }
if (keyboard_check(vk_up))    { y -= 2; }
if (keyboard_check(vk_down))  { y += 2; }
```

---

## 14. El sistema de coordenadas de GameMaker

> Si visualizas un sistema de coordenadas como en clase de matemáticas, puede que el eje
> vertical te parezca **al revés**.

En matemáticas el origen (0,0) está **abajo a la izquierda**, así que subir en el eje Y
te lleva hacia la parte superior de la página.

**En ordenadores está invertido**, y el motivo es cultural:

> El inglés se lee **de izquierda a derecha y de arriba abajo**, así que el origen (0,0)
> está en la **esquina superior izquierda**. Por tanto, **aumentar Y te mueve hacia
> ABAJO** por la pantalla.

Otros motores pueden aplicar una transformación para invertirlo. **GameMaker no lo
hace.** Y en gráficos por ordenador, lo habitual es que el (0,0) sea arriba-izquierda.

---

## 15. El truco de la resta de booleanos

Como `keyboard_check()` devuelve `true`/`false` y en GameMaker eso equivale a **1** y
**0**, mucha gente escribe el movimiento así:

```gml
movement_x = keyboard_check(vk_right) - keyboard_check(vk_left);
movement_y = keyboard_check(vk_down)  - keyboard_check(vk_up);

x += movement_x;
y += movement_y;
```

Cómo se razona:

| Teclas | Cuenta | Resultado |
|---|---|---|
| Derecha pulsada | 1 − 0 | **+1** → derecha |
| Izquierda pulsada | 0 − 1 | **−1** → izquierda |
| Ninguna / ambas | 0 − 0 / 1 − 1 | **0** → quieto |

Funciona, aunque te mueves a **la mitad de velocidad** que antes.

> **La opinión del autor:** «Tiene un aspecto bastante ridículo… y hay quien finge que
> escribir código raro es intrínsecamente mejor que escribirlo de forma larga y aburrida.
> **Yo os recomendaría no hacer caso a esa gente y escribir lo que tenga sentido para
> vosotros.**»

---

## 16. Teclas de letra: la función `ord()`

Si repasas la lista de constantes `vk_`, notarás una ausencia sospechosa: **no hay
constantes para las letras del teclado**.

Para comprobar si se pulsa una letra hay que usar **`ord()`**:

```gml
keyboard_check(ord("A"))
```

`ord()` recibe la letra **como cadena** (entre comillas dobles) y devuelve su **código
ASCII**, que es el mismo tipo de identificador que usan las constantes `vk_`.

### Las dos trampas

1. **Es obligatorio usar `ord()`.** No vale `keyboard_check("A")`.
2. **La letra debe ir en MAYÚSCULA.** `ord("a")` en minúscula **no funciona**.

### Movimiento con WASD

```gml
if (keyboard_check(ord("D"))) { x += 2; }   // Derecha
if (keyboard_check(ord("A"))) { x -= 2; }   // Izquierda
if (keyboard_check(ord("W"))) { y -= 2; }   // Arriba
if (keyboard_check(ord("S"))) { y += 2; }   // Abajo
```

### Combinar WASD y flechas

Puedes unir ambas comprobaciones en una sola condición:

```gml
if (keyboard_check(ord("D")) || keyboard_check(vk_right)) { x += 2; }
if (keyboard_check(ord("A")) || keyboard_check(vk_left))  { x -= 2; }
if (keyboard_check(ord("W")) || keyboard_check(vk_up))    { y -= 2; }
if (keyboard_check(ord("S")) || keyboard_check(vk_down))  { y += 2; }
```

Así el jugador puede usar **tanto WASD como las flechas**.

---

## Puntos clave

1. **Aprender un lenguaje nuevo es fácil** si ya conoces otro: es como español →
   portugués, no español → cantonés.
2. Una **expresión** representa un valor; una **variable** lo guarda.
3. **Pon siempre el punto y coma**, aunque no sea obligatorio.
4. **Cuida el orden de operaciones**: los paréntesis se evalúan primero.
5. **`+=`, `-=`, `*=`, `/=`** y **`++`, `--`** son atajos. Usa la forma **postfija**.
6. Las **funciones** se encadenan: la salida de una es la entrada de la siguiente.
7. **`true`/`false` son literalmente 1 y 0.**
8. **Los strings van entre comillas dobles**; sin ellas, el juego falla.
9. El evento **Step** corre cada fotograma. **Begin Step** y **End Step** existen para
   controlar el orden relativo entre objetos.
10. **En GameMaker el origen (0,0) es la esquina superior izquierda** y **aumentar Y
    baja por la pantalla**.
11. **`keyboard_check`** (mantenida), **`_pressed`** (al pulsar), **`_released`** (al
    soltar).
12. **No hay constantes `vk_` para las letras**: usa **`ord("A")`**.
13. **`ord()` exige mayúsculas** y una cadena.
14. **Escribe el código que tenga sentido para ti.** El código «ingenioso» no es mejor.

---

## Ejercicio propuesto

> **Objetivo:** interiorizar los fundamentos escribiendo el movimiento de tres formas
> distintas y entendiendo las diferencias.

**Parte A — Fundamentos sobre el papel**

1. Sin ejecutar nada, escribe en el Create y calcula a mano el resultado:
   ```gml
   max_player_health = 10;
   current_player_health = (max_player_health + 20) / 2;
   other_value = max_player_health + 20 / 2;
   ```
   ¿Cuánto vale cada una? Explica la diferencia.

2. Escribe una cadena de `if / else if / else` que clasifique la vida del jugador en
   tres estados: muerto (`<= 0`), en peligro (`<= 5`) y sano.

**Parte B — Seguir al ratón**

3. En el **Step** de `obj_player`, escribe `x = mouse_x;` e `y = mouse_y;`. Ejecuta con
   **F5** y comprueba que el objeto sigue al cursor.

**Parte C — Movimiento con flechas**

4. Sustituye el código anterior por los cuatro `if` con `keyboard_check(vk_right)`,
   `vk_left`, `vk_up` y `vk_down`, moviendo 2 píxeles.
5. Comprueba que **arriba** es `y -= 2` y **abajo** es `y += 2`. Si te sale al revés,
   repasa el apartado del sistema de coordenadas.

**Parte D — El truco y las letras**

6. Reescribe el movimiento con el truco de la resta de booleanos. Comprueba que te
   mueves a **la mitad de velocidad** y explica por qué.
7. Pasa el movimiento a **WASD** con `ord()`. Prueba a propósito `ord("a")` en minúscula
   y comprueba que **no funciona**.
8. Combina **WASD y flechas** en una sola condición con `||`.

**Reto extra:** escribe `player_name = Michael;` **sin comillas** en el Create y
ejecuta. Observa el fallo y lee el mensaje de error. Después pon las comillas. Entender
los mensajes de error es la mitad de aprender a programar.
