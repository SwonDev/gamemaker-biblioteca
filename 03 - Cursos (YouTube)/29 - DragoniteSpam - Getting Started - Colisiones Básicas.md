# 29 · DragoniteSpam — Colisiones básicas

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 17 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=jdp_2yCdQPg> |
| **Duración** | 23 min 34 s |
| **Publicado** | 18 de abril de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `place_meeting()`, `abs()`, `sign()`, `repeat` |

El capítulo más importante de la serie junto con el de Git. Aquí se construye, desde cero y
paso a paso, **el sistema de colisiones que hay detrás de casi cualquier juego de
GameMaker**.

## Índice de contenido

1. Por qué usar cuadrados de colores
2. La casilla *Solid*: no la uses
3. Los eventos de colisión: útiles pero limitados
4. Guardar el movimiento potencial
5. `place_meeting()`
6. Primer problema: no puedes deslizarte por la pared
7. Segundo problema: el movimiento no es divisible
8. La solución: comprobar píxel a píxel
9. `abs()` para las distancias negativas
10. `sign()` para la dirección
11. ¿Es lento comprobar en bucle?
12. Microoptimizaciones que no importan
13. El chiste recurrente de la comunidad
14. `move_and_collide()`

---

## 1. Por qué usar cuadrados de colores

Para este capítulo el autor **abandona** el proyecto con tiles y animaciones y usa un
proyecto mínimo lleno de **cuadrados de colores**.

El motivo es serio:

> Cuando trabajas con colisiones, tener gráficos bonitos que se animan de distintas formas
> **estorba** y dificulta ver qué estás haciendo.

Si tu sprite de correr tiene varios fotogramas, cuesta distinguir si el personaje está
realmente tocando un objeto o si le falta o le sobra un píxel.

> **Práctica estándar de la industria:** desde el desarrollador solitario hasta los juegos
> AAA, **cuando alguien trabaja o prueba un sistema de colisiones, sustituye todos sus
> gráficos por geometría de colores sólidos.**

---

## 2. La casilla *Solid*: no la uses

Al abrir un objeto verás una casilla **Solid**.

> **Es algo que prácticamente nunca deberías usar.**

Es un sistema que intenta que **GameMaker gestione las colisiones por ti**. Suena bien,
pero tiene dos problemas graves:

1. **Hace una única cosa**. Si quieres un control específico sobre tus colisiones, no te
   sirve.
2. **No funciona si manipulas las coordenadas del objeto tú mismo.** Solo funciona si usas
   `hspeed` y `vspeed`.

Y sobre `hspeed`/`vspeed`, el autor es contundente: es otro sistema que GameMaker intenta
gestionar por ti y **generalmente no es buena idea**, porque **te quita el control** y, si
no te gusta lo que hace por defecto, **no hay nada que puedas hacer**.

---

## 3. Los eventos de colisión: útiles pero limitados

Otra vía es el **evento Collision**: añades un evento que ocurre cuando dos objetos se
tocan.

```gml
// Evento Collision con obj_solid
x = 0;
y = 0;   // Algo dramático para verlo: teletransporte a la esquina
```

Esto **es mejor que la casilla Solid**, porque no modifica tu posición por ti: solo
dispara un evento donde escribes tu código.

Pero tiene problemas:

- Cuando tienes **muchos eventos**, se vuelve difícil de gestionar.
- **Pierdes el control de cuándo ocurre.** Puede que necesites gestionar las colisiones en
  un punto concreto, **entre medias de otro código** del Step.

> Conclusión del autor: **borramos el evento de colisión y lo hacemos nosotros por
> código.**

---

## 4. Guardar el movimiento potencial

En lugar de modificar `x` e `y` directamente al pulsar las teclas, **guarda el movimiento
en variables** y aplícalo al final:

```gml
var _move_x = 0;
var _move_y = 0;

if (keyboard_check(vk_right)) { _move_x += 4; }
if (keyboard_check(vk_left))  { _move_x -= 4; }
if (keyboard_check(vk_up))    { _move_y -= 4; }
if (keyboard_check(vk_down))  { _move_y += 4; }

x += _move_x;
y += _move_y;
```

Hace exactamente lo mismo, pero ahora:

> **Podemos comprobar el destino potencial ANTES de movernos.** Si hay una colisión allí,
> simplemente no nos movemos.

---

## 5. `place_meeting()`

```gml
place_meeting(x, y, obj);
```

Toma tres argumentos: una coordenada **X**, una **Y** y un **tipo de objeto**. Devuelve
**verdadero o falso** según si hay colisión en esa posición.

```gml
if (place_meeting(x + _move_x, y + _move_y, obj_solid))
{
    // Algo hay ahí: no nos movemos
}
else
{
    // Camino libre
    x += _move_x;
    y += _move_y;
}
```

(También puedes invertirlo con `if (!place_meeting(...))`; el autor lo escribe así porque
le gusta que el código se parezca a cómo lo está explicando en voz alta.)

> `obj_solid` **no tiene código**: solo existe, con su sprite. Eso basta.

### Qué hace exactamente

Cuando ejecutas `place_meeting()` dentro de una instancia, GameMaker toma **el objeto que
está ejecutando el código** y pregunta:

> *«Si este objeto se moviera a esta nueva posición, ¿habría colisión?»*

---

## 6. Primer problema: no puedes deslizarte por la pared

Si te mueves en diagonal contra un muro, **no puedes deslizarte** por él ni rodear la
esquina.

**Causa:** estamos comprobando **X e Y a la vez**. Con derecha + arriba pulsadas, se
comprueba la posición diagonal; si hay colisión ahí, **se bloquea todo**, aunque solo uno
de los dos ejes estuviera ocupado.

> GameMaker **no separa** el movimiento horizontal del vertical por ti.

**Solución: dos comprobaciones separadas.**

```gml
// Eje X por separado
if (!place_meeting(x + _move_x, y, obj_solid))
{
    x += _move_x;
}

// Eje Y por separado
if (!place_meeting(x, y + _move_y, obj_solid))
{
    y += _move_y;
}
```

Ahora sí: al chocar contra una pared, **puedes deslizarte** a lo largo de ella. Y funciona
viniendo desde cualquier dirección.

---

## 7. Segundo problema: el movimiento no es divisible

Este es más sutil y no se ve a simple vista.

Supón:

- El jugador está en `x = 128`.
- La pared está en `x = 320`.
- Distancia: **192 píxeles**.
- Velocidad: **4 píxeles por paso**.

Como **192 es divisible por 4**, llegas a la pared en **exactamente 48 fotogramas** y
quedas pegado a ella.

> ¿Y si la velocidad fuera **5**? ¿Y si la pared estuviera a una distancia **no divisible**
> por tu velocidad?

El autor lo demuestra: cambiando a `keyboard_check_pressed` y velocidad **16**, el
personaje encaja perfecto. Pero con velocidad **20**:

> Si intento moverme 20 píxeles, el juego comprueba la colisión **a 20 píxeles de
> distancia**, ve que hay colisión y **me impide acercarme más**, aunque quede un hueco
> entre yo y la pared.

---

## 8. La solución: comprobar píxel a píxel

En lugar de comprobar de golpe a la distancia de movimiento, **comprueba de uno en uno**:

```gml
// Eje X, píxel a píxel
repeat (abs(_move_x))
{
    if (!place_meeting(x + sign(_move_x), y, obj_solid))
    {
        x += sign(_move_x);
    }
}
```

Así, si te quedan 3 píxeles libres y tu velocidad es 20, **avanzas esos 3** y te quedas
pegado a la pared.

Y lo mismo en el eje Y:

```gml
repeat (abs(_move_y))
{
    if (!place_meeting(x, y + sign(_move_y), obj_solid))
    {
        y += sign(_move_y);
    }
}
```

---

## 9. `abs()` para las distancias negativas

**Problema:** `repeat(-20)` no tiene sentido. Si vas hacia la izquierda, `_move_x` es
negativo.

**Solución:** **`abs()`**, el **valor absoluto**: la magnitud de un número **sin signo**.

- `abs(20)` = 20
- `abs(-20)` = 20

Así el bucle se ejecuta el número correcto de veces **en cualquier dirección**.

---

## 10. `sign()` para la dirección

**`sign()`** devuelve **1**, **0** o **−1** según si el número es mayor, igual o menor que
cero.

> **No lo confundas con `sin()`** (seno, la función trigonométrica). Aquí hablamos del
> **signo**: más o menos.

- `sign(20)` = **1**
- `sign(-20)` = **−1**

Con esto, el mismo código sirve para ambos sentidos:

```gml
repeat (abs(_move_x))
{
    if (!place_meeting(x + sign(_move_x), y, obj_solid))
    {
        x += sign(_move_x);
    }
}
```

Ahora funciona **independientemente** de tu velocidad, de la distancia y de si es
divisible.

---

## 11. ¿Es lento comprobar en bucle?

> **Respuesta corta: no.**

Respuesta larga:

> El sistema de colisiones de GameMaker está **muy bien optimizado**. Aunque tengas muchos
> objetos en la room haciendo comprobaciones, el sistema **es lo bastante inteligente para
> comprobar solo lo que está en las inmediaciones** del objeto.

No recorre todos los objetos de la room cada vez.

> **Excepción:** la exportación a **HTML5**. Que es «solo una de las muchas razones por las
> que no nos gusta hablar de la exportación HTML5 de GameMaker».

---

## 12. Microoptimizaciones que no importan

Es tentador «limpiar» el código: estamos evaluando `sign(_move_x)` varias veces dentro del
bucle cuando siempre da el mismo número.

```gml
var _step_x = sign(_move_x);

repeat (abs(_move_x))
{
    if (!place_meeting(x + _step_x, y, obj_solid))
    {
        x += _step_x;
    }
}
```

> Puedes hacerlo si quieres, pero **no va a hacer tu juego más rápido ni más lento**.

El autor aprovecha para una pequeña diatriba:

> A la gente le gusta **microoptimizar** sus juegos de GameMaker: es el nombre de la
> categoría general de «hacer cambios en cosas que **no** están ralentizando tu juego».

---

## 13. El chiste recurrente de la comunidad

> «Si alguna vez te has encontrado con el chiste recurrente en la comunidad de GameMaker
> sobre **el código de colisiones de Shaun Spalding** (o como se haya llamado antes), en
> realidad **no es más que lo que ves en pantalla**.»

---

## 14. `move_and_collide()`

GameMaker tiene **muchísimas** funciones de colisión (tantas que el autor reconoce que
«casi es un problema»).

Una de las más recientes es **`move_and_collide()`**, que hace **parte de esta lógica por
ti**. Durante muchísimo tiempo, el código que acabamos de escribir **era** la forma
canónica de hacer colisiones en GameMaker.

> Es una función interesante y cómoda… **pero hay casos donde simplemente no funciona**
> (por ejemplo, en algunos juegos de plataformas 2D). Por eso **conviene saber hacerlo a
> mano de todos modos**.

---

## Puntos clave

1. **Sustituye tus gráficos por cuadrados de colores** para trabajar en colisiones: es
   práctica estándar de la industria.
2. **No uses la casilla *Solid*.** Solo funciona con `hspeed`/`vspeed` y te quita el
   control.
3. **Los eventos de colisión son útiles**, pero con muchos eventos se vuelven difíciles de
   gestionar y pierdes el control del momento exacto.
4. **Guarda el movimiento en variables** y aplícalo al final: así puedes comprobar el
   destino **antes** de moverte.
5. **`place_meeting(x, y, obj)`** responde «si estuviera ahí, ¿colisionaría?».
6. **Comprueba los ejes por separado** para poder deslizarte por las paredes.
7. **Comprueba píxel a píxel** si la distancia no es divisible por tu velocidad.
8. **`abs()`** para el número de iteraciones (magnitud sin signo).
9. **`sign()`** para la dirección (1 / 0 / −1). **No es `sin()`.**
10. **Comprobar en bucle NO es lento**: GameMaker optimiza y solo mira las inmediaciones
    (salvo en HTML5).
11. **No microoptimices**: cambiar cosas que no te están ralentizando no sirve de nada.
12. **`move_and_collide()`** existe y es cómoda, pero **no siempre sirve**.

---

## Ejercicio propuesto

> **Objetivo:** construir el sistema completo desde cero y **provocar** cada uno de los dos
> problemas para entender por qué hace falta cada pieza.

**Preparación**

1. Crea un proyecto mínimo: un objeto jugador (cuadrado) y un objeto `obj_solid`
   **sin código**, con un sprite de color distinto. Nada de gráficos bonitos.
2. Coloca muros formando un pequeño laberinto.

**Parte A — Movimiento potencial**

3. Implementa el movimiento guardando `_move_x` e `_move_y` y aplicándolos al final.
   Comprueba que te mueves igual que antes.
4. Añade el `place_meeting(x + _move_x, y + _move_y, obj_solid)` que bloquea el movimiento.
   Comprueba que no atraviesas las paredes.

**Parte B — El primer problema**

5. Pégate a una pared e intenta moverte **en diagonal contra ella** (por ejemplo derecha +
   arriba). Comprueba que **no puedes deslizarte**.
6. Explica por qué: estás comprobando X e Y **a la vez**.
7. Separa las comprobaciones por ejes y comprueba que ahora **sí** te deslizas.

**Parte C — El segundo problema (el sutil)**

8. Coloca el jugador a una distancia de la pared que **no sea divisible** por tu velocidad
   (por ejemplo, velocidad 20 y pared a 190 píxeles).
9. Comprueba que **te quedas separado** de la pared por un hueco. Mide ese hueco.
10. Implementa la comprobación **píxel a píxel** con `repeat` y comprueba que ahora quedas
    pegado.

**Parte D — Las dos direcciones**

11. Prueba a ir **hacia la izquierda**: el bucle no se ejecuta. Explica por qué
    (`repeat` con número negativo).
12. Añade **`abs()`** al número de iteraciones y **`sign()`** a la posición comprobada y al
    incremento.
13. Comprueba que funciona en las cuatro direcciones y con cualquier velocidad.

**Reto extra:** sustituye la comprobación por `move_and_collide(_move_x, _move_y,
obj_solid);` en una sola línea y compara el resultado con tu versión a mano. Anota una
diferencia que observes. Después vuelve a tu versión: saber cómo funciona por dentro es lo
que te permite arreglarla cuando la función integrada no basta.
