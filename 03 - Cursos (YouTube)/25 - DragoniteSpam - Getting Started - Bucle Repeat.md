# 25 · DragoniteSpam — El bucle `repeat`

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 13 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=k29BLrJ2OYk> |
| **Duración** | 5 min 53 s |
| **Publicado** | 14 de marzo de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `repeat` |

Primero de los cuatro vídeos sobre bucles. Empieza por lo más básico.

## Índice de contenido

1. Por qué los bucles definen a un lenguaje moderno
2. El problema: repetir una acción varias veces
3. La sintaxis de `repeat`
4. El número de repeticiones puede ser una variable
5. Para qué sirve en juegos reales
6. Limitaciones de `repeat`

---

## 1. Por qué los bucles definen a un lenguaje moderno

> El concepto de bucle es **algo bastante fundamental** en los lenguajes de programación
> modernos. De hecho, es una de las pocas cosas que **definen** un lenguaje moderno, en el
> sentido de que lo hacen **Turing completo**: teóricamente puede calcular cualquier cosa,
> si tienes suficiente memoria y tiempo.

---

## 2. El problema: repetir una acción varias veces

Partimos del ejemplo anterior: al pulsar espacio se genera un espantapájaros en una
posición aleatoria dentro de un cuadrado de 50 × 50 alrededor del jugador.

Ahora queremos generar **cinco** a la vez. Hay básicamente dos caminos:

1. **Copiar y pegar** el código cinco veces.
2. Escribirlo **una** vez y meterlo en un **bucle**.

> «Si la idea de copiar y pegar código un montón de veces te suena a dolor de cabeza, **tu
> intuición es correcta**».

Hay casos muy simples en los que te puedes escapar copiando y pegando, pero **casi siempre
querrás un bucle**.

(Y el autor descarta una tercera vía: «si vas a usar **recursión** para algo así, lo estás
haciendo mal».)

---

## 3. La sintaxis de `repeat`

Se parece a un `if`: donde el `if` lleva la palabra `if` seguida de una condición entre
paréntesis, el bucle lleva la palabra **`repeat`** seguida del **número de repeticiones**.

```gml
if (keyboard_check_pressed(vk_space))
{
    repeat (5)
    {
        var _xx = x + random_range(-25, 25);
        var _yy = y + random_range(-25, 25);
        instance_create_layer(_xx, _yy, "Instances", obj_scarecrow);
    }
}
```

Es **un bloque de código que indica que la acción se va a llevar a cabo un número concreto
de veces**.

> Los bucles `repeat` son **realmente simples**: te permiten ejecutar una acción **un número
> exacto de veces**.

---

## 4. El número de repeticiones puede ser una variable

No tiene por qué ser un literal como 5 o 10. Puede ser **una variable** o **un cálculo**.

```gml
var _scarecrow_count = irandom_range(3, 8);

repeat (_scarecrow_count)
{
    var _xx = x + random_range(-25, 25);
    var _yy = y + random_range(-25, 25);
    instance_create_layer(_xx, _yy, "Instances", obj_scarecrow);
}
```

Ahora cada pulsación genera **entre 3 y 8** espantapájaros.

---

## 5. Para qué sirve en juegos reales

El autor anima a pensar en usos concretos:

- Un **bullet hell**: disparar un montón de balas delante o alrededor del jugador.
- Generar **un número determinado de enemigos** en posiciones aleatorias que el jugador
  deba eliminar.

> **Los bucles están por todas partes en los juegos**, y `repeat` es la forma más básica de
> hacerlo en GameMaker.

---

## 6. Limitaciones de `repeat`

> Precisamente por su simplicidad, `repeat` es **algo más limitado** que las otras formas de
> bucle que ofrece GameMaker.

Los siguientes vídeos de la serie cubren esas alternativas y las posibilidades extra que dan.

---

## Puntos clave

1. Un bucle ejecuta código **varias veces** sin duplicarlo.
2. **`repeat (n) { … }`** ejecuta el bloque **exactamente n veces**.
3. **n puede ser una variable** o una expresión calculada.
4. Es la forma más simple de bucle en GameMaker.
5. Usos típicos: **rociar balas**, **generar grupos de enemigos**, efectos de partículas.
6. Es el bucle **más limitado**: para más control existen `while`, `for` y `do/until`.

---

## Ejercicio propuesto

> **Objetivo:** sustituir código duplicado por un bucle y comprobar el valor de un contador
> dinámico.

1. Partiendo del ejemplo de los espantapájaros, escribe **a mano** (copiando y pegando) el
   código que genera cinco de ellos en posiciones aleatorias. Cuenta cuántas líneas ocupa.
2. Reescribe lo mismo con `repeat (5)`. Compara: ¿cuántas líneas menos? ¿Qué pasa si ahora
   quieres veinte espantapájaros?
3. Cambia el literal por una variable `_count` y asígnale un valor fijo. Comprueba que
   funciona igual.
4. Usa `irandom_range(3, 8)` para el número de repeticiones y ejecuta diez veces. Anota
   cuántos espantapájaros salen cada vez.

**Parte de diseño**

5. Imagina un **disparo en abanico**: cinco balas con ángulos espaciados. Intenta
   implementarlo con `repeat`, usando una variable que vayas incrementando dentro del
   bucle para calcular el ángulo.
6. Ahora imagina que quieres **seguir generando** enemigos **hasta** que haya diez en la
   room. Intenta hacerlo con `repeat`… y comprueba que **no puedes**: `repeat` necesita
   saber el número por adelantado.

**Reto extra:** ese último punto es exactamente la limitación de la que habla el autor.
Anota por qué `repeat` no sirve cuando **no sabes de antemano** cuántas veces necesitas
repetir, y qué información extra necesitaría el bucle para poder hacerlo. Es la puerta de
entrada al bucle `while`.
