# 39 · GameMaker oficial — Tu primer plataformas en 15 minutos

> **Fuente:** canal oficial de GameMaker
> **Vídeo:** How to Make a Video Game in 15 Minutes! | GameMaker Platformer Tutorial

| | |
|---|---|
| **Canal** | **GameMaker** (oficial) |
| **Presenta** | Gelex (desarrollador de *Donut County*, *Starboy Advent* y *Moonleap*) |
| **URL** | <https://www.youtube.com/watch?v=a9f4QdHGM4k> |
| **Duración** | 14 min 38 s |
| **Publicado** | 12 de septiembre de 2024 |
| **Nivel** | Principiante absoluto |
| **Motor** | GameMaker (GML Code) |
| **Blog asociado** | <https://gamemaker.io/en/tutorials/your-first-platformer> |

El tutorial oficial en vídeo del canal de GameMaker. Es la vía más corta para tener **un
juego jugable de principio a fin**, y el complemento perfecto al curso principal: aquí se
usa **`move_and_collide()`** (que vimos en el capítulo 30) en lugar de las colisiones
manuales, lo que reduce el código a la mínima expresión.

## Índice de contenido

1. Quién presenta el tutorial
2. Sprites, objetos y rooms: los tres pilares
3. Crear los sprites
4. El punto de origen
5. Crear los objetos
6. La room y su tamaño
7. Navegar por el espacio de trabajo
8. El evento Create: ventana, variables
9. El evento Step: movimiento
10. `move_and_collide()`
11. Gravedad y salto
12. Colisiones con la bandera y los pinchos
13. Fondo, efectos y capas
14. Duplicar rooms para crear niveles

---

## 1. Quién presenta el tutorial

**Gelex**, que usa GameMaker desde niño y ha desarrollado:

- **Donut County**
- **Starboy Advent**
- **Moonleap**, ganador del *Notice Me Game Jam* y después convertido en un juego completo.

---

## 2. Sprites, objetos y rooms: los tres pilares

El presentador pide que te centres en el **navegador de recursos** (a la derecha), donde
estarán todos los recursos del juego. Para este proyecto solo usaremos tres:

| Recurso | Qué es |
|---|---|
| **Sprites** | Las **imágenes** del juego: tu personaje, enemigos, objetos e incluso el fondo |
| **Objects** | Aquí va el **código**: qué pasa cuando el personaje toca un enemigo, recoge un objeto, pasa de nivel… |
| **Rooms** | Los **niveles**: aquí colocas los objetos (el suelo por donde caminará el personaje, dónde estarán enemigos y objetos…) |

> Puedes borrar las carpetas que no vayas a usar.

---

## 3. Crear los sprites

Varias formas de crearlos; la del tutorial:

```
Clic en el espacio vacío → Assets → Create Sprite
```

El primero se llama **`s_player`**.

> «Puedes llamarlo como quieras, pero yo suelo usar `s_player` para el sprite del
> jugador.»

Se puede dibujar dentro de GameMaker (recomendado) o usar **Import** con sprites ya
preparados, como hace él en el vídeo.

Sigue creando:

- **`s_flag`** — la meta del nivel.
- Sprites para el suelo y los pinchos.

> Para trabajar en un asset, **haz doble clic** sobre él. Válido para todos los recursos.

---

## 4. El punto de origen

Al fondo verás el **Origin Point**, puesto a `0, 0`, lo que significa la **esquina superior
izquierda**.

> El tutorial avisa de que esto se va a cambiar (para poder rotar y alinear bien los
> sprites).

---

## 5. Crear los objetos

Se crea **un objeto por cada sprite**:

| Objeto | Sprite |
|---|---|
| **`o_player`** | `s_player` |
| **`o_solid`** | el suelo |
| **`o_flag`** | la bandera |
| **`o_spike`** | los pinchos |

> El panel de la derecha del objeto son los **eventos**: ahí va el código, lo que ocurre
> cuando el objeto se crea, se destruye, al final del juego, etc.

---

## 6. La room y su tamaño

Al hacer doble clic en `Room1` aparece una **rejilla negra**: tu nivel.

> Si arrastras un objeto y se ve pequeño, es **porque la room es muy grande**.

Solución: selecciona la room en el navegador de recursos y cambia su tamaño en los **ajustes
de la room** (abajo a la izquierda). El tutorial usa **320 × 180**.

Después ajusta el zoom y coloca los objetos arrastrándolos con `Alt`.

> La rejilla por defecto puede resultar demasiado grande; el presentador la cambia a
> **16 × 16**.

---

## 7. Navegar por el espacio de trabajo

Para moverte por el espacio de trabajo se usa el **botón central del ratón**.

---

## 8. El evento Create: ventana, variables

Añade un evento **Create** (se ejecuta en cuanto el objeto se crea, es decir, al abrirse el
juego).

> Si aparece una ventana preguntando entre **GML Code** y **GML Visual**, elige **GML
> Code**. No se usa el lenguaje visual.

```gml
// Create event de o_player

// Tamaño de la ventana del juego: quiero 720p
window_set_size(960, 540);

// Velocidad horizontal y vertical
xsp = 0;
ysp = 0;
```

Dos ideas clave:

- **`window_set_size()`** es una función integrada de GameMaker. Si no sabes cómo funciona,
  **haz clic con el botón central** sobre ella.
- Una **variable** es algo a lo que pones nombre para **guardar un valor y usarlo después**.
  Por ejemplo, `coins` para las monedas recogidas, o `health` para la vida.

---

## 9. El evento Step: movimiento

El **Step**, a diferencia del Create, ocurre **cada fotograma**. Ahí va el movimiento.

```gml
// Step event de o_player

if (keyboard_check(vk_left))
{
    xsp = -1;
}

if (keyboard_check(vk_right))
{
    xsp = +1;
}
```

### Por qué `xsp` e `ysp`

Representan la **velocidad de las coordenadas X e Y** del objeto:

- Pulsar izquierda **disminuye X**.
- Pulsar derecha **aumenta X**.

Si en la room haces doble clic en el personaje verás sus valores **X** e **Y**:

- Arriba del todo a la izquierda: `x = 0`, `y = 0`.
- Bajarlo aumenta **Y**.
- Moverlo a la derecha aumenta **X**; a la izquierda, la disminuye.

> **El nivel es como un plano cartesiano, y en el código manipulamos las coordenadas para
> mover al personaje.**

---

## 10. `move_and_collide()`

```gml
move_and_collide(xsp, ysp, o_solid);
```

> Es una función de GameMaker que permite al personaje **moverse y colisionar con el
> suelo**.

Es exactamente la función que DragoniteSpam analiza a fondo en el capítulo 30, usada aquí
en su forma más simple.

Al ejecutar: la ventana ya es más grande y **el personaje se mueve**… pero no salta y
flota, porque todavía no hay gravedad.

---

## 11. Gravedad y salto

La gravedad se implementa **aplicando una fuerza vertical que empuja al personaje hacia
abajo** mientras no esté pisando suelo. Cuando está en el suelo, la velocidad vertical es 0.

```gml
xsp = 0;   // Si no pulsas izquierda ni derecha, quieto

// Gravedad
ysp += 0.1;

// ¿Estamos en el suelo?
if (place_meeting(x, y + 1, o_solid))
{
    ysp = 0;   // Velocidad vertical a cero

    // Solo se puede saltar tocando el suelo
    if (keyboard_check_pressed(vk_up))
    {
        ysp = -2;
    }
}
```

Claves:

- **`ysp += 0.1`** empuja hacia abajo cada fotograma.
- **`place_meeting(x, y + 1, o_solid)`** comprueba si hay suelo **un píxel por debajo**.
  El tutorial insiste: **haz clic central sobre la función** para leer su explicación.
- Al estar en el suelo, `ysp = 0` y se permite el salto.
- **`ysp = -2`** es el salto (negativo = hacia arriba).

> «Mirad eso: **ya casi es un juego**.»

---

## 12. Colisiones con la bandera y los pinchos

```gml
// Colisión con la bandera: pasar al siguiente nivel
if (place_meeting(x, y, o_flag))
{
    room_goto_next();
}

// Colisión con los pinchos: reiniciar la room
if (place_meeting(x, y, o_spike))
{
    room_restart();
}
```

| Función | Efecto |
|---|---|
| **`room_goto_next()`** | Va a la **siguiente room de la lista** |
| **`room_restart()`** | **Reinicia la room** actual |

> Un **comentario** (`// …`) **no lo lee GameMaker**: es solo para ti.

Al ejecutar, todo funciona… **hasta que llegas al final y el juego falla**, porque
**todavía no existe una room siguiente**.

---

## 13. Fondo, efectos y capas

Para que no se vea tan feo, se crea un sprite de fondo `s_back` (blanco y gris):

1. Clic en la room → **Layers** → elige la **capa de fondo** (*background layer*).
2. En *Background*, selecciona un **sprite**.
3. Márcalo para que se **repita horizontal y verticalmente**.
4. Puedes cambiar el **color** del sprite.
5. Abajo hay **Filters and Effects**: efectos ya hechos que puedes aplicar a la capa.

> El presentador añade el efecto **underwater** («¿por qué no?»), y anima a probarlos.

---

## 14. Duplicar rooms para crear niveles

```
Clic derecho sobre la room existente → Duplicate
```

La renombra a `Room2`, añade más pinchos, coloca la bandera, cambia el fondo… y repite el
proceso para tener varios niveles.

> «Muchas de las cosas que he hecho aquí no son las más optimizadas, pero las he hecho de la
> forma más simple y comprensible posible.»

---

## Puntos clave

1. Tres pilares: **sprites** (imágenes), **objetos** (código) y **rooms** (niveles).
2. **Un objeto por cada sprite** que necesite comportamiento.
3. Room pequeña (**320 × 180**) y rejilla de colocación (**16 × 16**).
4. **`window_set_size()`** fija el tamaño de la ventana.
5. **`xsp` / `ysp`** son las velocidades de las coordenadas X e Y.
6. **`move_and_collide(xsp, ysp, o_solid)`** resuelve movimiento y colisión en una línea.
7. **Gravedad = sumar a `ysp`** cada fotograma.
8. **`place_meeting(x, y + 1, o_solid)`** detecta el suelo un píxel por debajo.
9. **`room_goto_next()`** y **`room_restart()`** para avanzar y reiniciar.
10. Las capas de fondo admiten **sprite repetido, color y efectos**.
11. **Duplica rooms** para crear niveles nuevos rápidamente.
12. Clic central sobre cualquier función abre **su documentación**.

---

## Ejercicio propuesto

> **Objetivo:** tener un plataformas completo y jugable con el mínimo código posible, y
> comparar este enfoque con el de colisiones manuales.

**Parte A — El proyecto base**

1. Crea un proyecto en blanco (plantilla **Blank pixel game** si vas a hacer pixel art).
2. Crea cuatro sprites: jugador, suelo, bandera y pinchos. Dibújalos tú.
3. Crea los cuatro objetos y asígnales sus sprites.
4. Pon la room a **320 × 180** y la rejilla a **16 × 16**.
5. Coloca suelo, pinchos, bandera y jugador con `Alt`.
6. **Antes de seguir, cambia el origen** de tus sprites a **bottom center** y comprueba cómo
   mejora el alineado con el suelo.

**Parte B — El código**

7. En el **Create** de `o_player`, añade `window_set_size(960, 540);`, `xsp = 0;` e
   `ysp = 0;`.
8. En el **Step**, añade el movimiento izquierda/derecha con `keyboard_check`.
9. Añade `move_and_collide(xsp, ysp, o_solid);`. Ejecuta y comprueba que te mueves y chocas.
10. Añade la gravedad (`ysp += 0.1`) y la detección de suelo con `place_meeting(x, y + 1,
    o_solid)`.
11. Añade el salto dentro de la comprobación de suelo.
12. Añade las colisiones con bandera (`room_goto_next`) y pinchos (`room_restart`).

**Parte C — Rematar**

13. Crea `s_back`, ponlo en la capa de fondo con repetición horizontal y vertical, y cámbiale
    el color.
14. Prueba al menos dos efectos de la sección *Filters and Effects*.
15. **Duplica la room** tres veces y diseña tres niveles distintos. Comprueba que ahora sí
    puedes llegar al final sin que el juego falle.

**Reto extra (muy recomendable):** reescribe el movimiento **sin** `move_and_collide()`,
usando el sistema de colisiones manual del capítulo 29 (`place_meeting` + bucle píxel a
píxel + `abs()` + `sign()`). Compara:

- Cuántas líneas necesita cada versión.
- En qué se nota la diferencia al jugar (deslizarse por las paredes, esquinas, precisión).

Después decide cuál usarías en un plataformas real y por qué. El propio DragoniteSpam
advierte en el capítulo 30 de que **`move_and_collide()` tiene problemas precisamente en
plataformas 2D**, así que tu respuesta dice mucho de lo que has aprendido.
