# 33 · DragoniteSpam — Dibujar texto

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 21 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=MRGBrKoQJ3g> |
| **Duración** | 18 min 52 s |
| **Publicado** | 4 de julio de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `draw_text()`, `draw_text_ext()`, `draw_text_transformed()`, `draw_text_color()`, `draw_set_halign()`, `draw_set_valign()` |

## Índice de contenido

1. `draw_text()`
2. Por qué el texto se ve pixelado
3. Color del texto
4. `draw_text_color()`: un color por esquina
5. `draw_text_ext()`: ajuste de línea
6. `draw_text_transformed()`: escala y rotación
7. La familia completa de funciones
8. Alineación: `draw_set_halign()` y `draw_set_valign()`
9. Dónde se dibuja: mundo frente a pantalla
10. Sobre Scribble y no sobreingenierizar

---

## 1. `draw_text()`

```gml
draw_text(x, y, cadena);
```

Tres argumentos: una coordenada **X**, una **Y** y la **cadena de texto** a dibujar.

```gml
draw_text(x, y - 100, "Hace calor hoy, ¿verdad?");
```

Esto dibuja el texto **flotando sobre la cabeza del jugador**.

---

## 2. Por qué el texto se ve pixelado

Es el primer problema que notarás, y es importante entenderlo.

> **Cuando dibujas texto, GameMaker NO está renderizando una fuente como lo haría Microsoft
> Word.**

Lo que hace es:

> **Coger tu fuente y convertirla en un montón de sprites diminutos, uno por cada letra o
> glifo.** Luego dibuja esos pequeños sprites en cadena.

Consecuencia:

> Si tu cámara tiene **zoom, escalado, rotación o cualquier transformación** que haga que los
> sprites no se dibujen **1:1** con la resolución de la pantalla, **el texto aparecerá
> pixelado, con dientes de sierra o distorsionado**.

¿Por qué no pasa lo mismo con tus sprites de pixel art?

> Porque si tus sprites están bien hechos y usas **escalado entero**, los píxeles se ven
> grandes y gruesos —que es justo lo que buscas— y **no notas distorsión**.

Pero con el texto **suele desearse suavidad**, así que los artefactos de escalado **sí se
notan**.

El autor, para el vídeo, simplemente **desactiva la cámara con zoom** para que el texto no
se distorsione.

---

## 3. Color del texto

Igual que con las formas, tienes `draw_set_color()`:

```gml
draw_set_color(c_red);
draw_text(x, y - 100, "Hace calor hoy, ¿verdad?");
draw_set_color(c_white);   // Restablecer: recuerda que es GLOBAL
```

Otras formas de definir colores:

- **`make_color_rgb(r, g, b)`**: a partir de valores RGB.
- **`make_color_hsv(h, s, v)`**: a partir de tono, saturación y valor.
- Un **literal hexadecimal**: por ejemplo `0x6666FF` (un azul claro / morado).

---

## 4. `draw_text_color()`: un color por esquina

```gml
draw_text_color(x, y, cadena, c1, c2, c3, c4, alpha);
```

Admite **cuatro colores** y **un alfa**.

> **El orden es el mismo que en `draw_sprite_general()`: en sentido HORARIO.**

| Argumento | Posición |
|---|---|
| `c1` | Superior **izquierda** |
| `c2` | Superior **derecha** |
| `c3` | Inferior **derecha** |
| `c4` | Inferior **izquierda** |

```gml
draw_text_color(x, y - 100, "Hace calor hoy",
                c_red, c_red, c_yellow, c_yellow, 1);
```

Resultado: **rojo arriba y amarillo abajo**, con degradado.

> El **alfa es global**: un único valor que se aplica a las cuatro esquinas.

---

## 5. `draw_text_ext()`: ajuste de línea

Si dibujas un texto largo, **se sale de la pantalla en una sola línea**. Para que salte de
línea:

```gml
draw_text_ext(x, y, cadena, sep, w);
```

Dos argumentos nuevos:

| Argumento | Significado |
|---|---|
| **`sep`** | La **altura de línea** |
| **`w`** | El **ancho en píxeles** tras el cual el texto se parte a la línea siguiente |

```gml
draw_text_ext(x, y - 100, _texto_largo, -1, 400);
```

### Sobre la altura de línea

- Ponlo a **`-1`** para usar la altura por defecto (proporcional al tamaño de la fuente).
- El autor opina que **casi nunca merece la pena tocarlo**: el valor por defecto es
  correcto en la inmensa mayoría de los casos.
- Pero puedes hacerlo: un valor bajo (10) **apelotona** el texto; uno alto (30) lo
  **espacia** más.

---

## 6. `draw_text_transformed()`: escala y rotación

```gml
draw_text_transformed(x, y, cadena, xscale, yscale, angle);
```

Permite **escalar** y **rotar** el texto.

```gml
draw_text_transformed(x, y - 100, "Hola", 2, 2, 0);      // El doble de grande
draw_text_transformed(x, y - 100, "Hola", 1, 3, 0);      // Estirado en vertical
draw_text_transformed(x, y - 100, "Hola", 1, 1, 60);     // Rotado 60°
```

> **Aviso:** al escalar vuelven **los artefactos** de los que hablábamos. `draw_text_transformed`
> con escalado **no suele quedar bien** por sí solo.

La rotación se aplica **respecto al punto origen** donde estás dibujando el texto.

---

## 7. La familia completa de funciones

Existen combinaciones para casi todo:

| Función | Añade |
|---|---|
| `draw_text()` | — |
| `draw_text_color()` | Color por esquina |
| `draw_text_ext()` | Ajuste de línea |
| `draw_text_ext_color()` | Ajuste + color |
| `draw_text_transformed()` | Escala y rotación |
| `draw_text_transformed_color()` | Transformación + color |
| `draw_text_ext_transformed()` | Ajuste + transformación |
| `draw_text_ext_transformed_color()` | Todo junto |

> El autor reconoce que **esta forma de diseñar la API no le entusiasma**, y que «no creo
> que a la mayoría de la gente le encante». En el futuro de GameMaker quieren abandonar
> este enfoque, pero va para largo.

---

## 8. Alineación: `draw_set_halign()` y `draw_set_valign()`

Por defecto el texto se alinea **arriba-izquierda** respecto al punto que le des.

Para cambiarlo:

```gml
draw_set_halign(fa_center);   // Horizontal
draw_set_valign(fa_top);      // Vertical
```

| Función | Opciones |
|---|---|
| **`draw_set_halign()`** | `fa_left`, `fa_center`, `fa_right` |
| **`draw_set_valign()`** | `fa_top`, `fa_middle`, `fa_bottom` |

El autor lo demuestra dibujando **un círculo rojo** justo en el punto de dibujado, para que
se vea dónde está el origen:

```gml
draw_set_color(c_red);
draw_circle(x, y - 100, 8, true);   // Punto de referencia
draw_set_color(c_white);
```

> Con **centrado horizontal** y **arriba** en vertical, el texto sobre la cabeza del
> personaje queda estéticamente bien.

Estas funciones **siguen aplicándose** aunque uses las variantes transformadas.

---

## 9. Dónde se dibuja: mundo frente a pantalla

Todo lo anterior se dibuja **en una posición del mundo**, relativa al jugador o a
coordenadas fijas de la room.

Pero si tienes una **cámara que sigue al jugador**, es muy posible que quieras que el texto
**se dibuje siempre en el mismo sitio de la pantalla**, siguiendo la ventana del juego y no
al personaje.

> Para eso GameMaker tiene todo un sistema: **la capa GUI**. Y es el tema del siguiente
> vídeo.

---

## 10. Sobre Scribble y no sobreingenierizar

> «Una de las realidades de la vida si participas en la comunidad de GameMaker: en cuanto
> usas una función `draw_text`, **en unos cinco segundos** aparece alguien diciendo
> *«¿por qué no usas Scribble?»*.»

**Scribble** es una extensión de GameMaker estupenda para dibujar texto que cubre muchas
carencias de las funciones integradas:

- Cambiar el color **en mitad de una línea**.
- Efectos: texto tembloroso, arcoíris, ondulado…

La postura del autor:

> Creo que muchos veteranos **dramatizan** lo malas que son las funciones integradas. **Si
> hace todo lo que necesitas, está bien.**
>
> «Siempre defenderé no sobreingenierizar soluciones que no necesitas.»

Si te topas con una limitación real, adelante: existen alternativas. Pero **no te sientas
presionado** a complicar tu proyecto si no lo necesitas.

---

## Puntos clave

1. **`draw_text(x, y, cadena)`**: tres argumentos.
2. **GameMaker NO renderiza fuentes de verdad**: convierte cada glifo en un sprite diminuto.
3. Por eso **el escalado y la rotación producen artefactos** visibles en el texto.
4. **`draw_set_color()`** colorea el texto… y **todo lo demás**: restablécelo siempre.
5. **`draw_text_color()`** da un color por esquina **en sentido horario**; el alfa es
   global.
6. **`draw_text_ext(x, y, cadena, sep, w)`**: `sep` = altura de línea (**−1** = por
   defecto), `w` = ancho de ajuste.
7. **`draw_text_transformed()`** escala y rota.
8. Existen **combinaciones** de todas las variantes.
9. **`draw_set_halign()`** y **`draw_set_valign()`** con `fa_*`.
10. Para texto fijo en pantalla con cámara, usa la **capa GUI**.
11. **No sobreingenierices**: las funciones integradas bastan para la mayoría de los casos.

---

## Ejercicio propuesto

> **Objetivo:** dominar el texto dibujado y comprobar en directo el problema del escalado.

**Parte A — Lo básico**

1. Dibuja un texto sobre la cabeza del jugador con `draw_text(x, y - 100, "Hola");`.
2. **Si tienes la cámara con zoom**, observa los dientes de sierra. Desactiva el zoom de la
   cámara y comprueba que desaparecen.
3. Explica con tus palabras por qué ocurre (pista: glifos convertidos en sprites).

**Parte B — Color**

4. Cambia el color con `draw_set_color(c_red)`. Después añade un `draw_text()` más abajo
   **sin** restablecer el color y comprueba que **también sale rojo**.
5. Restablece con `draw_set_color(c_white)`.
6. Prueba `make_color_rgb()`, `make_color_hsv()` y un literal hexadecimal propio.

**Parte C — Degradados**

7. Usa `draw_text_color()` con rojo arriba y amarillo abajo.
8. Comprueba el orden de las esquinas poniendo cuatro colores distintos (rojo, verde, azul,
   amarillo) y confirmando que c1 = arriba-izquierda y que avanza en sentido horario.

**Parte D — Ajuste y transformación**

9. Escribe un párrafo largo y comprueba que se sale de la pantalla en una línea.
10. Usa `draw_text_ext(..., -1, 400)` y comprueba el ajuste.
11. Pruea alturas de línea de 10, −1 y 30 y describe la diferencia.
12. Usa `draw_text_transformed()` con escala 2×2 y rotación 60°, y **observa cómo vuelven
    los artefactos**.

**Parte E — Alineación**

13. Dibuja un círculo rojo pequeño en el punto exacto donde dibujas el texto, para ver el
    origen.
14. Prueba las nueve combinaciones de `halign` × `valign` y anota cuál queda mejor para un
    texto sobre la cabeza del personaje.

**Reto extra:** dibuja un **marcador de puntuación** en la esquina superior izquierda
usando coordenadas fijas de la room, y ejecuta el juego **con la cámara siguiendo al
jugador**. Comprueba que el marcador **se queda atrás** y desaparece. Ese es exactamente el
problema que resuelve la **capa GUI** del siguiente capítulo.
