# 26 · DragoniteSpam — El bucle `while`

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 14 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=CqifE5jYbOA> |
| **Duración** | 11 min 1 s |
| **Publicado** | 14 de marzo de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `while`, `instance_number()`, bucles infinitos |

El bucle `repeat` hace exactamente lo que dice, pero **precisamente por su simplicidad es
poco flexible**. El bucle `while` es la alternativa general.

## Índice de contenido

1. Qué cambia respecto a `repeat`
2. `instance_number()`: contar instancias
3. Un límite máximo de instancias
4. Reescribir `repeat` como `while`: el contador de bucle
5. El bucle prototípico de la informática
6. El infame bucle infinito
7. Un bucle ocurre TODO DE GOLPE
8. Lo que `while` no puede hacer

---

## 1. Qué cambia respecto a `repeat`

En lugar de tomar **un número fijo de repeticiones**, `while` toma **una condición
verdadero/falso** y **sigue ejecutándose mientras esa condición sea verdadera**.

```gml
while (condición)
{
    // código
}
```

---

## 2. `instance_number()`: contar instancias

GameMaker tiene varias funciones para obtener información sobre las instancias. Una de
ellas es:

```gml
instance_number(obj);
```

> Devuelve **cuántas instancias de ese objeto existen actualmente en la room**.

---

## 3. Un límite máximo de instancias

Imagina que quieres un **máximo de 20 espantapájaros** en el mundo:

```gml
var _max_scarecrows = 20;

while (instance_number(obj_scarecrow) < _max_scarecrows)
{
    var _xx = x + random_range(-25, 25);
    var _yy = y + random_range(-25, 25);
    instance_create_layer(_xx, _yy, "Instances", obj_scarecrow);
}
```

Comportamiento:

- La primera vez que pulsas espacio **se generan los 20** alrededor del jugador.
- Después, **no se genera ninguno más**, porque ya hay 20.
- Si colocas algunos espantapájaros **a mano** en la room antes de empezar,
  `instance_number()` los cuenta y el bucle **solo genera los que falten**.

### `repeat` frente a `while` en el mismo caso

| Bucle | Comportamiento |
|---|---|
| `repeat(10)` | Genera **exactamente 10** monstruos |
| `while (instance_number(...) < 10)` | Genera **hasta 10**, contando los que ya hubiera |

Podrías hacer mates para conseguir lo mismo con `repeat`, pero:

> **No hay una forma correcta** de hacerlo. Hay muchas maneras de conseguir lo mismo.

---

## 4. Reescribir `repeat` como `while`: el contador de bucle

El autor lo construye desde cero para que se vea el mecanismo interno:

```gml
var _max_scarecrows = 10;
var _current_scarecrows = 0;

while (_current_scarecrows < _max_scarecrows)
{
    var _xx = x + random_range(-25, 25);
    var _yy = y + random_range(-25, 25);
    instance_create_layer(_xx, _yy, "Instances", obj_scarecrow);

    _current_scarecrows++;
}
```

### Cuidado: sin incrementar el contador, bucle infinito

> Como **ninguno de los dos valores cambia** dentro del bucle, si no incrementas
> `_current_scarecrows` tendrás un **bucle infinito**.

Para evitarlo, se incrementa al final de cada iteración (con `++` o `+= 1`).

---

## 5. El bucle prototípico de la informática

> Lo que acabamos de escribir es **el bucle arquetípico** de la programación.

De hecho:

- El `repeat` de GameMaker es, internamente, **un atajo** de exactamente esto: tiene un
  **contador de bucle** y un **número de iteraciones**, y va llevando la cuenta hasta que el
  contador supera ese número.
- En los primeros días de los lenguajes de programación, **los bucles se parecían a esto**.
  Los bucles `for` y otras estructuras más sofisticadas **se añadieron a C más tarde**.

> Al contrario que `repeat`, esto hace que `while` sea **infinitamente flexible**: es el
> bucle **más de propósito general** del lenguaje.

---

## 6. El infame bucle infinito

El más simple:

```gml
while (true)
{
    // …
}
```

Por definición, la condición **nunca será falsa**.

> Si lo ejecutas y pulsas espacio, **el juego se congela**. La animación se detiene, no
> responde a WASD, porque está generando espantapájaros sin fin. El autor tiene que
> **forzar la detención** con el botón de *stop*.

### Cómo se crea por accidente

Casi nunca escribirás `while (true)` a propósito. Lo normal es que sea un **accidente**:

```gml
_scarecrows--;   // El contador BAJA en vez de subir: nunca alcanza el máximo
```

> **Ten mucho cuidado con esto.** Hay muchas formas de crear bucles infinitos sin querer.

Y lo peor:

> **El juego no te mostrará un error amigable explicándote qué pasó. Simplemente se
> congelará y dejará de funcionar.**

Si tienes suerte, el sistema operativo te mostrará el icono de «no responde».

---

## 7. Un bucle ocurre TODO DE GOLPE

Este es un error conceptual muy común:

> **Todo el bucle ocurre de una vez, inmediatamente.** Todas las iteraciones se ejecutan
> **antes de que se ejecute la siguiente línea de código** que haya después del bucle.

Algunas personas asumen que un `while` hará algo **continuamente, cada fotograma**. **No.**

> **No puedes usar un bucle para generar 10 espantapájaros a lo largo de 10 fotogramas**, o
> de 10 segundos. Así no funciona.

Para hacer cosas **a lo largo del tiempo** hay otros mecanismos (que se verán más
adelante).

### El motivo de fondo

> El código se ejecuta **en el orden que tú le indicas**. Actualmente **no existe** en
> GameMaker un comando `defer`, ni `await`, ni estructuras de control asíncrono. Podría
> haberlas en el futuro, pero hoy no están.

---

## 8. Lo que `while` no puede hacer

Resumen de límites:

- **No** reparte el trabajo en el tiempo: ocurre todo en el mismo fotograma.
- Si la condición nunca cambia, **se congela el juego**.

---

## Puntos clave

1. **`while (condición)`** se ejecuta **mientras** la condición sea verdadera.
2. **`instance_number(obj)`** devuelve cuántas instancias hay en la room.
3. Permite límites del tipo «**hasta** N instancias», que `repeat` no puede expresar.
4. **El contador de bucle** es el patrón clásico: inicializar, comprobar, incrementar.
5. **El bucle infinito es el peligro número uno**: el juego se congela **sin mensaje de
   error**.
6. `while` es el bucle **más general y flexible** del lenguaje.
7. **Un bucle se ejecuta completo en un solo fotograma**: no sirve para repartir trabajo en
   el tiempo.
8. GameMaker **no tiene** `await`, `defer` ni control asíncrono.

---

## Ejercicio propuesto

> **Objetivo:** usar `while` para un límite dinámico y experimentar (con cuidado) con un
> bucle infinito.

**Parte A — Límite dinámico**

1. Crea la variable `_max_scarecrows = 20`.
2. Implementa el bucle `while (instance_number(obj_scarecrow) < _max_scarecrows)` que genera
   espantapájaros alrededor del jugador.
3. Ejecuta y pulsa espacio una vez: ¿cuántos aparecen? Pulsa varias veces más: ¿qué pasa?
4. **Coloca 3 espantapájaros a mano en la room** y vuelve a pulsar espacio. Cuenta cuántos
   se generan y comprueba que solo son **los que faltaban**.

**Parte B — El contador**

5. Reescribe el mismo comportamiento con un contador explícito
   (`_current_scarecrows = 0`, condición, `_current_scarecrows++`).
6. **Comenta la línea del incremento** y ejecuta. **Ten preparado el botón de stop.**
   Observa la congelación y pulsa *stop*.
7. Descomenta la línea y comprueba que vuelve a funcionar.

**Parte C — El fallo sutil**

8. Cambia `_current_scarecrows++` por `_current_scarecrows--`. Ejecuta y observa que
   **también** se congela, aunque de forma menos obvia. Explica por qué.

**Reto extra:** antes de ejecutar el siguiente código, **predice** el resultado leyéndolo
línea a línea (es el ejercicio que propone el autor):

```gml
for (var i = 0; i < 10; i++)
{
    instance_create_layer(x + 15 * i, y - 15 * i, "Instances", obj_scarecrow);
}
```

Anota qué patrón esperas y compruébalo después. Predecir código antes de ejecutarlo es una
de las habilidades que más rápido te hará mejorar.
