# 30 · DragoniteSpam — `move_and_collide()`

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 18 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=MSQSj3qUEhw> |
| **Duración** | 19 min 12 s |
| **Publicado** | 3 de mayo de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `move_and_collide()` |

GameMaker incluye una función que hace **casi todo** el trabajo del capítulo anterior en
una sola línea. Este vídeo la desmenuza: sus argumentos, su comportamiento y,
sobre todo, **cuándo no sirve**.

## Índice de contenido

1. Por qué merece la pena seguir sabiendo hacerlo a mano
2. Los argumentos obligatorios
3. Qué puede recibir como objeto
4. El número de iteraciones
5. El problema de las esquinas y los decimales
6. Evitación de obstáculos (*collision avoidance*)
7. `xoffset` e `yoffset`
8. Saltarse argumentos opcionales
9. Límites máximos de movimiento
10. Cuándo `move_and_collide()` no sirve

---

## 1. Por qué merece la pena seguir sabiendo hacerlo a mano

Aunque `move_and_collide()` cubra la mayoría de tus necesidades:

1. **Hay situaciones donde no funciona** y tendrás que escribir tu propia solución, que
   probablemente se parecerá a la del capítulo anterior.
2. **Si hace algo que no esperas** —y pasa—, conocer los fundamentos te ayudará a
   diagnosticarlo y arreglarlo.

---

## 2. Los argumentos obligatorios

```gml
move_and_collide(dx, dy, obj);
```

Los **tres primeros son obligatorios**; el resto son opcionales.

| Argumento | Significado |
|---|---|
| **`dx`** | El movimiento que quieres intentar en el eje X este paso |
| **`dy`** | El movimiento que quieres intentar en el eje Y este paso |
| **`obj`** | Con qué quieres colisionar |

`dx`/`dy` se pueden interpretar como **la diferencia** de posición, o como **la distancia**
que quieres recorrer (o como las `dx`/`dy` del cálculo, si vienes de ahí). En la práctica:
**el movimiento que intentas hacer este paso**.

```gml
move_and_collide(_move_x, _move_y, obj_solid);
```

Con esa sola línea ya funciona: chocas contra los muros y te detienes.

---

## 3. Qué puede recibir como objeto

Igual que la mayoría de funciones de colisión de GameMaker, acepta varias cosas:

- Un **tile map element**.
- Un **objeto** de GameMaker.
- Una **instancia** concreta.
- La constante **`all`**.
- Un **array** con combinaciones de todo lo anterior.

En el vídeo se usa `obj_solid` para mantener la coherencia con el capítulo anterior.

---

## 4. El número de iteraciones

Nuestro código a mano recorría la distancia **de píxel en píxel**. `move_and_collide()`
**enfoca el problema al revés**:

> En lugar de avanzar de uno en uno hasta el destino, **da un número determinado de pasos
> hacia el destino**.

- El valor **por defecto es 4**.
- Con velocidad 4 y 4 iteraciones, cada paso es de **exactamente 1 píxel** (coincide
  casualmente con el ejemplo anterior).
- Con velocidad **6** y 4 iteraciones, cada paso sería de **1,5 píxeles**.

GameMaker **permite** comprobar colisiones con números fraccionarios, pero:

> Si estás empezando, probablemente te recomendaría **evitar** la detección de colisiones
> con números fraccionarios.

Puedes subir la resolución (por ejemplo a **10 iteraciones**) si necesitas más precisión.

> **Recomendación del autor:** mantén el número de iteraciones **igual a la distancia que
> intentas mover**. Si tu velocidad es 4, usa 4. Si es 8, usa 8.

---

## 5. El problema de las esquinas y los decimales

Al moverte en diagonal contra una esquina, puedes quedarte **como a un píxel** del muro,
sin llegar a alinearte con él.

Explicación del autor:

- Si te mueves en diagonal, tu desplazamiento real es **la hipotenusa** del triángulo.
- Con lados de 4 y 4, la hipotenusa es ≈ **5,6**.
- **5,6 no es entero** y **no divide de forma exacta entre 4 iteraciones**.
- Resultado: puede quedarte un error de una fracción minúscula de píxel.

Soluciones:

1. **Asegurarte de que la distancia total sea entera**: redondear tu velocidad total,
   normalizar el vector, etc.
2. **Aumentar el número de iteraciones**: con pasos más finos, **el error baja tanto que no
   se aprecia a simple vista**. El autor se queda en 10.

---

## 6. Evitación de obstáculos (*collision avoidance*)

Aquí `move_and_collide()` hace algo que **nuestro código a mano no hacía**.

El autor coloca un obstáculo minúsculo (un cuadrado de **2 × 2**):

- Con el código propio: **no puedes pasarlo**, aunque sea diminuto. Solo compruebas si hay
  solapamiento.
- Con `move_and_collide()`: **lo rodeas**. Te desvías un poco y sigues.

> «No es imposible programar esto tú mismo, pero es **más trabajo** y es de esas cosas que
> **no me parecen divertidas de hacer**.»

### El límite de lo que puedes rodear

Si el obstáculo es más grande (por ejemplo **8 × 8**), **ya no puedes rodearlo**.

> **El tamaño del obstáculo que puedes esquivar es proporcional a la magnitud de tu
> movimiento**: si te mueves más rápido, puedes rodear obstáculos mayores.

---

## 7. `xoffset` e `yoffset`

Estos dos argumentos sirven para **personalizar cuánto puedes esquivar**.

> El autor cree que son, en esencia, **el producto cruzado 2D de tu vector de movimiento**.

Su consejo:

> Si no te manejas con vectores perpendiculares y productos cruzados, **déjalos en sus
> valores por defecto**. Suelen ser suficientes.

- El valor por defecto es **0**.
- Con 0, GameMaker hace su comportamiento estándar.

---

## 8. Saltarse argumentos opcionales

Si quieres pasar un argumento posterior sin rellenar los anteriores:

```gml
move_and_collide(_move_x, _move_y, obj_solid, 10, , );
```

> **Feather** (el comprobador de sintaxis) se quejará, pero **funciona**. El autor lo
> considera **un bug del comprobador de sintaxis**.

Alternativas más limpias: escribir el valor por defecto (**0**) o usar **`undefined`**.

---

## 9. Límites máximos de movimiento

Los dos últimos argumentos fijan **la distancia máxima** que puedes mover en X y en Y en
un paso.

¿Para qué sirve, si ya tienes `dx` y `dy`?

> Porque al **rodear un obstáculo**, puedes acabar moviendo **más** de lo que pediste en uno
> de los ejes.

Ejemplo del autor: si tu movimiento es `dx = 0`, `dy = 4`, pero rodeas una piedra,
tendrás que desplazarte **2 píxeles en X**, más de los 0 solicitados.

- Por defecto **no hay límite**.
- Si fijas `max_x = _move_x` y `max_y = _move_y`, **no podrás desviarte** para rodear
  obstáculos.

> **⚠️ El autor cree que la documentación está equivocada aquí.** Dice que «si el valor es
> ≤ 0 no se realiza limitación», pero él ha comprobado que **poner 0 hace que no te puedas
> mover**. Para que no haya límite, recomienda usar **−1**. Lo tiene apuntado para
> reportarlo.

Caso de uso del propio manual: en un **plataformas**, si caes muy rápido y aterrizas con
fuerza, parte del impulso podría transferirse a la horizontal. Un límite superior evita
eso.

---

## 10. Cuándo `move_and_collide()` no sirve

El autor cierra con los casos en que **no merece la pena** pelearse con la función:

### A) Plataformas de un solo sentido (*one-way platforms*)

El comportamiento correcto depende de si el jugador **sube o baja**:

- Si **sube**, debe poder atravesarlas.
- Si **baja**, debe detenerse.

> Puedes «hackearlo» siendo muy específico con el objeto contra el que compruebas, pero
> **entonces ya no merece la pena**.

### B) Sólidos condicionales

Si tienes un muro que normalmente es sólido **pero puede volverse transparente** según
alguna condición o propiedad del objeto:

> `move_and_collide()` **no es elegante** para gestionar eso. Otra vez: puedes hackearlo,
> pero **¿no sería mejor escribir tu propio código de colisiones? Probablemente**.

---

## Puntos clave

1. **`move_and_collide(dx, dy, obj)`** hace casi todo el trabajo en una línea.
2. Acepta tile maps, objetos, instancias, `all` o **arrays**.
3. **Iteraciones por defecto: 4.** Auméntalo si necesitas más precisión; mantenlo igual a tu
   velocidad si puedes.
4. **Cuidado con los decimales**: pueden dejarte desalineado una fracción de píxel en las
   esquinas.
5. **Rodea obstáculos pequeños automáticamente**; el tamaño que puede esquivar depende de tu
   velocidad.
6. **`xoffset` / `yoffset`** ajustan la evitación; mejor dejarlos por defecto.
7. Puedes **saltar argumentos opcionales** con comas vacías (o `0` / `undefined`).
8. **Los límites de movimiento** evitan desvíos al rodear obstáculos.
9. **No sirve para plataformas de un solo sentido** ni para **sólidos condicionales**.
10. **Aprende a hacerlo a mano igualmente**: es lo que te salva cuando la función no basta.

---

## Ejercicio propuesto

> **Objetivo:** comparar tu sistema manual con la función integrada y encontrar sus
> límites.

**Parte A — La línea única**

1. Comenta tu código de colisiones del capítulo anterior.
2. Escribe `move_and_collide(_move_x, _move_y, obj_solid);`.
3. Comprueba que puedes chocar contra los muros y deslizarte por ellos.

**Parte B — Las iteraciones**

4. Deja las iteraciones por defecto (4) y pon tu velocidad a **6**. Calcula cuánto mide
   cada paso (6 / 4 = 1,5).
5. Muévete en diagonal contra una esquina y intenta reproducir el **desajuste de un píxel**
   del que habla el autor.
6. Sube las iteraciones a **10** y comprueba si el desajuste desaparece a simple vista.
7. Prueba con iteraciones = **tu velocidad** y observa el resultado.

**Parte C — Rodear obstáculos**

8. Crea un objeto obstáculo con un sprite de **2 × 2** y colócalo en medio del camino.
   Comprueba que `move_and_collide()` **te permite rodearlo**.
9. Vuelve a tu **código manual** y comprueba que **no puedes** pasarlo.
10. Cambia el sprite del obstáculo a **8 × 8** y comprueba que ahora la función **tampoco**
    te deja rodearlo.
11. Aumenta tu velocidad y comprueba si puedes rodear obstáculos mayores.

**Parte D — Los límites**

12. Añade los dos últimos argumentos iguales a tu movimiento:
    ```gml
    move_and_collide(_move_x, _move_y, obj_solid, 10, 0, 0, _move_x, _move_y);
    ```
    Comprueba que **ya no puedes rodear** el obstáculo pequeño.
13. **Comprueba la documentación por ti mismo:** pon `0` en esos dos argumentos y observa
    qué pasa. Después pon `−1`. ¿Concuerda con lo que dice el manual?

**Reto extra:** intenta implementar una **plataforma de un solo sentido** con
`move_and_collide()`. Cuando veas lo incómodo que resulta, escríbela con tu propio sistema
de colisiones. Es exactamente la conclusión del autor: hay casos en los que la función no
basta, y por eso merece la pena haber aprendido el sistema manual.
