# 32 · DragoniteSpam — Dibujar formas

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 20 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=LZdJGf1kPOE> |
| **Duración** | 10 min 43 s |
| **Publicado** | 31 de mayo de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `draw_rectangle`, `draw_circle`, `draw_ellipse`, `draw_triangle`, `draw_roundrect`, `draw_set_color`, `draw_line`, `draw_line_width`, `draw_point`, `draw_arrow` |

> «Dibujar sprites es algo que usarás bastante a menudo, pero también puedes dibujar
> **formas genéricas**, o *primitivas* como se las conoce.»

## Índice de contenido

1. Las funciones de formas
2. `draw_rectangle()`
3. Formas relativas al objeto
4. `draw_circle()`, `draw_triangle()` y `draw_ellipse()`
5. `draw_set_color()` es GLOBAL
6. Versiones con color por esquina o vértice
7. `draw_roundrect()` y su radio de curva
8. Funciones que el autor olvidó mencionar
9. ¿Para qué sirve realmente?
10. Formas personalizadas: las primitivas

---

## 1. Las funciones de formas

GameMaker ofrece bastantes:

| Función | Forma |
|---|---|
| **`draw_rectangle()`** | Rectángulo |
| **`draw_circle()`** | Círculo |
| **`draw_ellipse()`** | Elipse |
| **`draw_triangle()`** | Triángulo |
| **`draw_roundrect()`** | Rectángulo con esquinas redondeadas |

El autor no las repasa todas porque hay muchísimas.

---

## 2. `draw_rectangle()`

```gml
draw_rectangle(x1, y1, x2, y2, outline);
```

Cinco argumentos:

| Argumento | Significado |
|---|---|
| `x1`, `y1` | Esquina **superior izquierda** |
| `x2`, `y2` | Esquina **inferior derecha** |
| `outline` | `true` = **solo contorno**; `false` = **relleno** |

```gml
draw_self();   // Para seguir viendo al personaje

draw_rectangle(50, 50, 200, 100, false);
```

> Es básicamente coger la herramienta de rectángulo de Paint y pintar un rectángulo sobre
> la imagen.

---

## 3. Formas relativas al objeto

En lugar de coordenadas fijas, puedes dibujar **relativo al jugador**. Por ejemplo, un
rectángulo **sobre su cabeza**:

```gml
draw_rectangle(x - 20, y - 100, x + 20, y - 80, false);
```

Ahora el rectángulo blanco **sigue al jugador** por la pantalla.

> «¿De qué sirve esto? Ni idea. Pero eso no nos va a detener.»

---

## 4. `draw_circle()`, `draw_triangle()` y `draw_ellipse()`

| Función | Argumentos |
|---|---|
| **`draw_circle(x, y, radius, outline)`** | Un centro (**x**, **y**) y un **radio** |
| **`draw_triangle(x1,y1, x2,y2, x3,y3, outline)`** | **Tres puntos** (seis números) más el contorno |
| **`draw_ellipse(x1,y1, x2,y2, outline)`** | Igual que el rectángulo, pero dibuja una **elipse** estirada para rellenarlo |

Es la definición natural de cada figura: los círculos se definen por centro y radio, los
triángulos por tres vértices.

---

## 5. `draw_set_color()` es GLOBAL

Por defecto todo se dibuja en **blanco**, que es el color de dibujo por defecto de
GameMaker.

```gml
draw_set_color(c_orange);   // o draw_set_colour(), para quien prefiera el inglés británico
```

> **⚠️ MUY IMPORTANTE:** «Este es un ajuste **global**. Esto también afectará a otras
> formas y, a veces, a otras cosas que intentes dibujar después. **El texto también se ve
> afectado** por este ajuste global.»

Por eso:

> **Cuando termines, restablece el color** a `c_white` o al que uses por defecto.

---

## 6. Versiones con color por esquina o vértice

Existen variantes de las funciones que aceptan colores:

```gml
draw_rectangle_color(x1, y1, x2, y2, c_tl, c_tr, c_br, c_bl, outline);
```

Cuatro argumentos más, uno **para cada esquina** (superior izquierda, superior derecha,
inferior derecha, inferior izquierda).

- Si las cuatro son iguales, obtienes un color plano.
- Si son distintas, **el color se mezcla por toda la forma**: útil para **degradados**.

También hay versiones para las demás figuras:

| Función | Comportamiento del color |
|---|---|
| `draw_circle_color()` | Color para el **centro** y para el **exterior**: el círculo se desvanece desde el radio |
| `draw_ellipse_color()` | Lo mismo |
| `draw_triangle_color()` | Un color **por vértice** |
| `draw_roundrect_color()` | Sorprendentemente, **no** es un color por esquina: se comporta como los círculos (color interior y exterior) |

---

## 7. `draw_roundrect()` y su radio de curva

Para un rectángulo con esquinas redondeadas:

```gml
draw_roundrect(x1, y1, x2, y2, outline);
```

Y la versión extendida permite afinar **el radio de las curvas**:

```gml
draw_roundrect_ext(x1, y1, x2, y2, xrad, yrad, outline);
```

- **`xrad`**: radio horizontal de la curva.
- **`yrad`**: radio vertical.

Con `xrad = 3` e `yrad = 10` verás una curva **mucho más gradual en vertical que en
horizontal**. Es una forma fácil de conseguir esquinas «suavizadas» a medida.

---

## 8. Funciones que el autor olvidó mencionar

El propio autor añade un apéndice «desde el futuro»:

| Función | Utilidad |
|---|---|
| **`draw_line()`** | «Definitivamente útil de vez en cuando» |
| **`draw_line_width()`** | Una línea **con grosor**: «le doy bastante uso algunas veces» |
| **`draw_arrow()`** | «Supongo…» |
| **`draw_point()`** | «Básicamente nunca es útil, salvo que estés escribiendo un renderizador por software» |

> «Una vez que entiendes **una** de las funciones de dibujo, ya las entiendes todas», así
> que no entra en más detalle.

---

## 9. ¿Para qué sirve realmente?

El autor es honesto:

> «Probablemente **no** vayas a dibujar formas primitivas muy a menudo.»

Dónde sí tienen uso:

- **Interfaz de usuario**: dibujar un rectángulo con degradado como elemento de UI.
- **Depuración** (el uso principal para él): visualizar la **caja de colisión** de un objeto
  dibujando un rectángulo o un círculo en su posición.

> «Personalmente, creo que uso las funciones de formas **más para depurar que para nada
> más**. Pero forman parte de GameMaker y tienen sus usos.»

---

## 10. Formas personalizadas: las primitivas

Si necesitas un **hexágono**, una **estrella** o cualquier geometría irregular que no cubra
ninguna función integrada:

> Es posible, pero requiere el sistema de **primitivas de dibujo** más avanzado, que
> básicamente significa **trazar cada vértice de la forma a mano con matemáticas**.

Queda fuera del alcance de este vídeo, pero conviene saber que existe.

---

## Puntos clave

1. GameMaker permite dibujar **formas primitivas** además de sprites.
2. **`draw_rectangle(x1, y1, x2, y2, outline)`**: dos esquinas y si es solo contorno.
3. **`draw_circle(x, y, radio, outline)`**: centro y radio.
4. **`draw_triangle()`**: tres vértices. **`draw_ellipse()`**: como el rectángulo, pero
   elíptica.
5. Puedes dibujar **relativo al objeto** usando `x` e `y`.
6. **`draw_set_color()` es GLOBAL**: afecta a todo lo que dibujes después, **incluido el
   texto**. Restablécelo siempre.
7. Las versiones `_color` permiten **un color por esquina o vértice**: sirven para
   degradados.
8. **`draw_roundrect_ext()`** controla el radio de las esquinas en X e Y por separado.
9. **`draw_line()` y `draw_line_width()`** son las más útiles del grupo «olvidadas».
10. Su uso principal real es la **depuración**: visualizar cajas de colisión.
11. Para formas personalizadas existe el sistema de **primitivas** (más avanzado).

---

## Ejercicio propuesto

> **Objetivo:** dominar las formas y, sobre todo, usarlas para **ver** lo que hace tu
> sistema de colisiones.

**Parte A — Formas básicas**

1. En el Draw de tu jugador, pon primero `draw_self();` y después dibuja un rectángulo
   relleno en una posición fija de la room.
2. Cámbialo a `outline = true` y observa la diferencia.
3. Hazlo **relativo al jugador** (por ejemplo sobre su cabeza) y comprueba que lo sigue.
4. Dibuja un **círculo** con centro en el jugador y radio 40.
5. Dibuja un **triángulo** y una **elipse** con los argumentos que quieras.

**Parte B — El peligro del color global**

6. Añade `draw_set_color(c_orange);` antes de una forma y comprueba que se pinta naranja.
7. **Añade después un `draw_text()` cualquiera** y comprueba que **el texto también sale
   naranja**. Este es el aviso importante del autor.
8. Restablece con `draw_set_color(c_white);` al final y verifica que todo vuelve a la
   normalidad.

**Parte C — Degradados y esquinas**

9. Usa `draw_rectangle_color()` con cuatro colores distintos en las esquinas y observa el
   degradado.
10. Usa `draw_circle_color()` con un color en el centro y otro en el exterior.
11. Usa `draw_roundrect_ext()` con `xrad = 3` e `yrad = 20` y describe cómo queda la curva.

**Parte D — El uso que de verdad importa**

12. **Visualiza tu caja de colisión.** En el Draw de tu objeto sólido, dibuja un rectángulo
    de contorno que coincida con su máscara de colisión:
    ```gml
    draw_set_color(c_red);
    draw_rectangle(bbox_left, bbox_top, bbox_right, bbox_bottom, true);
    draw_set_color(c_white);
    ```
13. Ejecuta y comprueba que el rectángulo encaja con el sprite. Si no encaja, revisa la
    **máscara de colisión** del sprite.
14. Haz lo mismo con el jugador en verde, y juega: **verás exactamente cuándo dos cajas se
    tocan**, que es la mejor forma de entender `place_meeting()`.

**Reto extra:** implementa una **barra de vida** con `draw_rectangle_color()`: un rectángulo
de fondo oscuro y otro encima cuyo ancho dependa de la vida. Es el uso de interfaz más
habitual de estas funciones, y te servirá hasta que uses `draw_healthbar()`.
