# 28 · DragoniteSpam — El bucle `do / until`

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 16 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=mvNO5OeQKwE> |
| **Duración** | 6 min 15 s |
| **Publicado** | 4 de abril de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `do { … } until (…)` |

Último de los cuatro vídeos sobre bucles, y el más raro de todos.

## Índice de contenido

1. Recorrido por lo visto hasta ahora
2. Qué es `do / until`
3. La trampa: copiar la misma condición no da el mismo resultado
4. Cómo hacerlo equivalente a `while`
5. La diferencia real: se ejecuta al menos una vez
6. Por qué casi nunca lo usarás
7. `do / until` frente a `do / while` de otros lenguajes

---

## 1. Recorrido por lo visto hasta ahora

| Bucle | Qué hace |
|---|---|
| **`repeat`** | Repite una acción **un número concreto de veces** |
| **`while`** | Repite **mientras** la condición sea verdadera (se comprueba **al principio**) |
| **`for`** | Igual que `while`, pero con las tres partes en una sola línea |
| **`do / until`** | **El inverso** de `while` (se comprueba **al final**) |

---

## 2. Qué es `do / until`

Es **básicamente el inverso del bucle `while`**:

- En `while`, la condición está **al principio** y el bloque se ejecuta **mientras se
  cumpla**.
- En `do / until`, la condición está **al final** y el bloque se ejecuta **hasta que se
  cumpla**.

```gml
do
{
    // código
}
until (condición);
```

`do` es una **palabra clave nueva** que no se usa en ningún otro sitio de GML.

---

## 3. La trampa: copiar la misma condición no da el mismo resultado

Si copias la condición del `while` tal cual:

```gml
// Antes (while): genera 10
while (_current_scarecrows < _max_scarecrows)
{
    // …generar…
    _current_scarecrows++;
}

// Después (do/until): genera solo 1
do
{
    // …generar…
    _current_scarecrows++;
}
until (_current_scarecrows < _max_scarecrows);
```

> El autor propone **pausar el vídeo** y pensar por qué antes de seguir.

La explicación:

- `_current_scarecrows` empieza en **0**.
- Se genera **un** espantapájaros y el contador pasa a **1**.
- Se comprueba: **¿1 < 10?** → **sí** → y como es `until`, **se detiene**.

Resultado: **solo un** espantapájaros en vez de diez.

Porque `until` **para cuando la condición se cumple**, al contrario que `while`, que
**continúa mientras se cumple**.

---

## 4. Cómo hacerlo equivalente a `while`

Hay que **invertir la condición**:

```gml
do
{
    // …generar…
    _current_scarecrows++;
}
until (_current_scarecrows >= _max_scarecrows);
```

Ahora sí: se detiene cuando el contador alcanza el máximo, y genera **10** espantapájaros.

---

## 5. La diferencia real: se ejecuta al menos una vez

> Aunque ahora el resultado sea el mismo, **sigue sin ser completamente equivalente** a un
> `while`.

La clave está en **cuándo se comprueba la condición**:

| Bucle | Cuándo comprueba | Consecuencia |
|---|---|---|
| **`while`** | **Al principio** | El código **puede no ejecutarse nunca** |
| **`do / until`** | **Al final** | El código **siempre se ejecuta al menos una vez** |

### Demostración con un caso límite

Con `_max_scarecrows = 0`:

**Con `while`:**

```gml
while (_current_scarecrows < _max_scarecrows)   // 0 < 0 → falso
```

> No se genera **ningún** espantapájaros: el código **nunca llega a ejecutarse**.

**Con `do / until`:**

```gml
do
{
    // …generar…                                 // Se genera UNO
    _current_scarecrows++;                       // Ahora vale 1
}
until (_current_scarecrows >= _max_scarecrows);  // 1 >= 0 → verdadero → parar
```

> Se genera **un** espantapájaros, porque se genera **antes** de comprobar la condición.

---

## 6. Por qué casi nunca lo usarás

> «Este es, probablemente, el aspecto concreto que hace que `do / until` **no sea útil la
> mayoría de las veces**.»

Claro que hay casos donde quieres **hacer algo una vez y luego parar**:

- Generar enemigos, pero **siempre al menos uno**.
- Leer un archivo: lees una línea y **si está vacía**, paras.

Pero el número de veces que eso es el comportamiento deseado es **mucho menor** que las
veces que quieres un bucle normal. Y casi siempre es **posible y más simple** escribirlo
con un `while`.

---

## 7. `do / until` frente a `do / while` de otros lenguajes

En otros lenguajes de programación existe **`do / while`**, que funciona igual que el
`while` normal (el autor bromea con que es «como voz pasiva en lugar de voz activa»).

En GameMaker es **`do / until`**.

> Aun así, forma parte de GML, y puesto que está disponible en el lenguaje, **merece la pena
> saber qué hace**, aunque no planees volver a usarlo nunca.

---

## Puntos clave

1. **`do { … } until (condición)`** comprueba la condición **al final**.
2. **Para cuando la condición se CUMPLE** (al contrario que `while`, que continúa mientras
   se cumple).
3. Para que sea equivalente a un `while` hay que **invertir la condición** (`<` pasa a
   `>=`).
4. **Aunque lo iguales, no es idéntico**: el bloque de `do / until` **se ejecuta siempre al
   menos una vez**.
5. Con un máximo de 0, `while` genera **0** elementos y `do / until` genera **1**.
6. **Es el bucle más raro** de GameMaker y de casi cualquier lenguaje.
7. Casi siempre es más simple escribirlo con `while`.
8. En otros lenguajes existe `do / while`; en GameMaker, **`do / until`**.

---

## Ejercicio propuesto

> **Objetivo:** entender de verdad la diferencia semántica entre comprobar antes y comprobar
> después.

1. Escribe el bucle finito con `while` (máximo 10, contador, incremento) y verifica que
   genera 10 espantapájaros.
2. Cópialo tal cual a un `do / until` **sin cambiar la condición**. **Antes de ejecutarlo,
   anota cuántos esperas que salgan.** Después ejecútalo y comprueba que sale **solo 1**.
3. Explica por escrito el recorrido del contador en ambos casos.
4. Invierte la condición a `>=` y comprueba que ahora genera 10.

**Parte del caso límite (la importante)**

5. Pon `_max_scarecrows = 0` y ejecuta la versión **`while`**. ¿Cuántos espantapájaros
   salen? (Deberían ser cero.)
6. Pon `_max_scarecrows = 0` y ejecuta la versión **`do / until`**. ¿Cuántos salen?
   (Debería salir uno.)
7. Explica con tus palabras por qué difieren, y en qué punto exacto se comprueba la
   condición en cada caso.

**Reto extra:** busca en tu propio código (o invéntalo) un caso donde **necesites**
garantizar que el bloque se ejecute al menos una vez. Un buen ejemplo es el que da el
autor: generar enemigos para que el jugador pelee, pero **siempre al menos uno**,
independientemente de los límites. Implementa las dos versiones (`while` con una
comprobación previa, frente a `do / until`) y decide cuál te parece más legible.
