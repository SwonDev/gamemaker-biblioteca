# 22 · DragoniteSpam — Generar números aleatorios

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 10 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=emEYWHkvHuU> |
| **Duración** | 18 min 0 s |
| **Publicado** | 18 de febrero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `random()`, `random_range()`, `irandom()`, `irandom_range()`, `choose()`, `randomise()`, `random_set_seed()`, `random_get_seed()` |

## Índice de contenido

1. `random()`: de 0 al valor indicado
2. `random_range()`: entre dos valores
3. Decimales frente a enteros: `irandom` e `irandom_range`
4. Aplicarlo a la escala
5. `choose()`: la función infravalorada
6. `choose()` devuelve lo que le des
7. El problema: siempre la misma secuencia
8. PRNG y la semilla (*seed*)
9. Por qué el IDE repite la semilla a propósito
10. `randomise()`, `randomize()`, `random_set_seed()` y `random_get_seed()`
11. Otras funciones misceláneas

---

## 1. `random()`: de 0 al valor indicado

La forma más simple. Devuelve un número aleatorio **entre 0 y el valor que le pases**.

```gml
var _spawn_x = random(100);
var _spawn_y = random(100);

instance_create_layer(_spawn_x, _spawn_y, "Instances", obj_scarecrow);
```

Con esto, los espantapájaros aparecen **en un cuadrado de 100 × 100** en la esquina de la
room, en vez de a los pies del jugador.

> Limitación: solo va de 0 al valor. Para un rango arbitrario hay que hacer mates… o usar
> otra función.

---

## 2. `random_range()`: entre dos valores

```gml
var _spawn_x = random_range(100, 500);
var _spawn_y = random_range(100, 300);
```

Devuelve un valor **entre los dos números** que le des.

> Al repetirlo muchas veces, verás zonas más o menos densas al principio, pero **a la larga
> se iguala**. Es la naturaleza de la generación de números aleatorios.

---

## 3. Decimales frente a enteros: `irandom` e `irandom_range`

`random()` y `random_range()` devuelven **números con decimales** (números de coma
flotante). Puedes obtener `175.4` o `253.17`.

Si quieres un **entero**, tienes dos caminos:

1. Redondear tú: `floor()`, `ceil()` o `round()`.
2. Usar las variantes **i**: **`irandom()`** e **`irandom_range()`**, donde la **i**
   significa **integer** (entero).

> Visualmente casi nunca notarás la diferencia entre colocar algo en `x = 153.75` y en
> `x = 153`, así que el autor lo demuestra con otra propiedad.

---

## 4. Aplicarlo a la escala

```gml
var _nuevo = instance_create_layer(x, y, "Instances", obj_scarecrow);

var _escala = random_range(1, 3);
_nuevo.image_xscale = _escala;
_nuevo.image_yscale = _escala;   // Misma escala en X e Y: lo contrario se vería raro
```

Con `random_range` obtienes **un espectro continuo**: espantapájaros de todos los tamaños
imaginables entre 1 y 3.

Con `irandom_range` solo obtienes **1, 2 o 3**: variedades pequeña, mediana y grande.

---

## 5. `choose()`: la función infravalorada

> «Creo que es una función muy **infravalorada** en GameMaker. Me gusta mucho.»

Elige **un valor al azar** de entre los que le pases:

```gml
choose(10, 20)              // La mitad de las veces 10, la mitad 20
choose(10, 20, 30, 40, 50)  // Uno de los cinco, con igual probabilidad
```

Acepta **tantos argumentos como quieras**: en informática se llama función **variádica**.

Es ideal para resultados **discretos**: un lanzamiento de moneda, una opción entre
varias…

### Ejemplo: rotación aleatoria

```gml
var _nuevo = instance_create_layer(x, y, "Instances", obj_scarecrow);
_nuevo.image_angle = choose(0, 90, 180, 270);
```

Los espantapájaros aparecen de pie, boca abajo o de lado. Puedes añadir todos los valores
que quieras.

---

## 6. `choose()` devuelve lo que le des

`choose()` devuelve **exactamente el tipo de dato que le pases**, así que funciona con
cualquier cosa, no solo números:

```gml
var _nombre = choose("Alfa", "Bravo", "Charlie", "Delta", "Echo");
```

Y también con **recursos de GameMaker**, sprites, arrays… prácticamente cualquier cosa.

> «Hay mil formas de elegir un valor al azar de una lista, pero me gusta `choose()` porque
> **mantiene las cosas simples**».

---

## 7. El problema: siempre la misma secuencia

El autor ejecuta el juego **varias veces seguidas** y pide que se fijen en la secuencia de
rotaciones:

```
Noroeste, sureste, sureste, suroeste, norte…
Noroeste, sureste, sureste, suroeste, norte…
Noroeste, sureste, sureste, suroeste, norte…
```

> **Se genera exactamente la misma secuencia de números aleatorios en cada ejecución.**

Y esto **no es un fallo**: es deliberado.

---

## 8. PRNG y la semilla (*seed*)

### La aleatoriedad real es difícil

Existe hardware de generación aleatoria real, con aplicaciones en criptografía. El ejemplo
más famoso que cita el autor:

> **Cloudflare** tiene una cámara apuntando a **una pared de lámparas de lava** y usa el
> ruido del vídeo para generar números aleatorios.

Obviamente, eso es «bastante excesivo para casi cualquier videojuego».

### PRNG

Para juegos se usa **generación de números pseudoaleatorios** (**PRNG**), porque
«generación pseudoaleatoria» tiene demasiadas sílabas.

Cómo funcionan:

1. Parten de una condición inicial: la **semilla** (*seed*), un número largo (128 bits, 512
   bits… según el algoritmo).
2. Aplican operaciones matemáticas simples: multiplicaciones, sumas, potencias,
   desplazamientos de bits…
3. **Revuelven** el número de forma que sea suficientemente distinto del anterior y no se
   pueda detectar un patrón fácilmente.

El algoritmo que usa GameMaker actualmente es **Well 512a**.

---

## 9. Por qué el IDE repite la semilla a propósito

> Cuando ejecutas el juego desde el IDE (botón *play* o **F5**), GameMaker **empieza
> siempre con la misma semilla**.

Suena raro, pero tiene un motivo muy bueno:

> Si estás probando y hay un bug relacionado con un resultado aleatorio —imagina que el
> juego solo falla cuando el jugador saca un 1 natural en un D20—, así es **mucho más fácil
> reproducir las condiciones** que provocaron el fallo y depurarlo.

Cuando **compilas el juego como ejecutable** independiente, GameMaker sí fija la semilla a
valores realmente aleatorios, y cada partida es distinta.

---

## 10. `randomise()`, `randomize()`, `random_set_seed()` y `random_get_seed()`

Si quieres aleatoriedad real **también desde el IDE**, llama a esta función al iniciar el
juego:

```gml
randomise();   // o randomize(), para quien prefiera el inglés americano
```

Se puede poner en el **Create**, en **Room Start** o en **Game Start**: en cualquier sitio
donde el juego esté arrancando.

> El autor bromea con que habría esperado menos polémica en este punto, pero ha visto
> **varias guerras de comentarios** en la comunidad sobre cuál de las dos variantes usar.

Además:

| Función | Qué hace |
|---|---|
| `randomise()` / `randomize()` | Aleatoriza la semilla |
| `random_set_seed(valor)` | Fija **tú** la semilla |
| `random_get_seed()` | Devuelve la semilla actual |

### Para qué sirve fijar la semilla

Muchos juegos de **generación procedural** —el más famoso, **Minecraft**— dejan al jugador
elegir la semilla. Así, si genera un mundo que le gusta, puede **guardar la semilla y
compartirla** con sus amigos.

> Nota del autor: como Well 512a tiene una semilla interna de **512 bits**, es posible que
> `random_get_seed()` **no devuelva la semilla completa**, lo que puede ser un problema si
> quieres restaurar el estado del generador.

---

## 11. Otras funciones misceláneas

También existe **`move_random()`**, que mueve un objeto a una posición aleatoria de la
room. El autor reconoce que **no es muy fan** de ella.

---

## Puntos clave

1. **`random(n)`** → entre 0 y n. **`random_range(a, b)`** → entre a y b. Ambos con
   **decimales**.
2. **`irandom()`** e **`irandom_range()`** → lo mismo pero **enteros** (la **i** =
   *integer*).
3. **`choose(a, b, c…)`** elige uno al azar; acepta **cuantos argumentos quieras**
   (variádica).
4. **`choose()` devuelve el mismo tipo que le des**: números, cadenas, sprites, arrays…
5. **El IDE usa siempre la misma semilla**, y es **a propósito**, para poder reproducir
   bugs aleatorios.
6. **Los ejecutables compilados sí aleatorizan la semilla.**
7. Llama a **`randomise()`** al iniciar si quieres variar también desde el IDE.
8. GameMaker usa el algoritmo **Well 512a**.
9. **`random_set_seed()`** permite semillas compartibles, como en Minecraft.
10. La aleatoriedad real (hardware, lámparas de lava de Cloudflare) es innecesaria para
    juegos.

---

## Ejercicio propuesto

> **Objetivo:** entender la diferencia entre aleatoriedad continua y discreta, y comprobar
> en tus propias carnes el comportamiento de la semilla.

**Parte A — Rangos**

1. En el Step del jugador, crea espantapájaros con `random(100)` en X e Y. Comprueba que
   salen en un cuadrado de 100 × 100.
2. Cambia a `random_range(100, 500)` en X y `random_range(100, 300)` en Y. Comprueba que
   rellenan un rectángulo.
3. Genera 200 espantapájaros y observa las zonas más y menos densas. Reflexiona sobre si
   «parece» realmente aleatorio.

**Parte B — Enteros frente a decimales**

4. Guarda la instancia creada y aplícale una **escala aleatoria**:
   ```gml
   var _n = instance_create_layer(x, y, "Instances", obj_scarecrow);
   var _e = random_range(1, 3);
   _n.image_xscale = _e;
   _n.image_yscale = _e;
   ```
5. Comprueba que obtienes un **espectro continuo** de tamaños.
6. Cambia a `irandom_range(1, 3)` y comprueba que solo salen **tres tamaños**.

**Parte C — `choose()`**

7. Comenta la escala y añade una rotación aleatoria con `choose(0, 90, 180, 270)`.
8. Añade más valores posibles a `choose()` y comprueba el resultado.
9. Usa `choose()` con **cadenas** para asignar un nombre aleatorio, y muéstralo con
   `show_debug_message()`.

**Parte D — La semilla (la parte importante)**

10. **Sin** llamar a `randomise()`, ejecuta el juego **tres veces** y anota la secuencia de
    rotaciones de los cinco primeros espantapájaros. Comprueba que **es idéntica** las tres
    veces.
11. Añade `randomise();` en el **Create** del jugador (o en Game Start) y repite la prueba.
    Ahora **cada ejecución debe ser distinta**.
12. Fija una semilla concreta con `random_set_seed(12345);` y comprueba que la secuencia
    vuelve a ser **repetible**.

**Reto extra:** implementa un sistema de **semilla compartible**: muestra la semilla en
pantalla con `random_get_seed()`, y permite al jugador introducir una semilla al iniciar
para regenerar exactamente el mismo «mundo» de espantapájaros. Explica por qué esto es la
base de la generación procedural tipo Minecraft.
