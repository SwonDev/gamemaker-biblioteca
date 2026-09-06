# 31 · DragoniteSpam — Dibujar sprites

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 19 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=Jo6yQLVmGXA> |
| **Duración** | 33 min 12 s |
| **Publicado** | 31 de mayo de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | evento Draw, `draw_self()`, `draw_sprite()`, `draw_sprite_ext()`, `draw_sprite_stretched()`, `draw_sprite_part()`, `draw_sprite_tiled()`, `draw_sprite_general()` |

> «En lo que a mí respecta, **aquí es donde empieza la verdadera diversión** en
> GameMaker.»

## Índice de contenido

1. Qué significa «dibujar» en informática
2. El evento Draw y cuándo se ejecuta
3. Nada de lógica de juego en el Draw
4. Por qué tu personaje desaparece
5. `draw_self()`
6. Las variables `image_*`
7. `draw_sprite()`
8. `draw_sprite_ext()`
9. Color: por qué el neutro es blanco
10. Alfa: transparencia de 0 a 1
11. `draw_sprite_stretched()` y el origen
12. `draw_sprite_part()`, `draw_sprite_tiled()` y `draw_sprite_general()`
13. Ejemplo completo: personalización de personaje por capas

---

## 1. Qué significa «dibujar» en informática

> En gráficos por ordenador, cuando alguien dice la palabra **dibujar**, se refiere al
> **proceso de poner una imagen en pantalla**.

Hasta ahora hemos puesto gráficos en pantalla de varias formas:

- Creando **tile maps** en el editor de rooms.
- Añadiendo **sprites como assets** en una capa de assets.
- Asignando sprites a una instancia mediante `sprite_index`.

Ahora vamos a **no usar nada de eso** y hacerlo todo **por código**.

---

## 2. El evento Draw y cuándo se ejecuta

Añade un **evento Draw** (clic derecho en la lista de eventos → Add Event → Draw).

Hay varios eventos Draw; el que nos importa es **el primero de la lista**, el **Draw**
principal. (Draw GUI es para interfaces y tiene su propio vídeo; los demás son
especializados.)

Como el Step, **se ejecuta cada fotograma**, pero con matices:

| Situación | Qué pasa con el Draw |
|---|---|
| La casilla **Visible** está desmarcada | El Draw **se salta por completo** |
| Hay **varios viewports** activos | El Draw se ejecuta **una vez por cada viewport** |

Poner un objeto invisible sirve tanto para objetos de juego que el jugador no debe ver
como para objetos que **gestionan tareas en segundo plano** sin representación visual.

Con cuatro jugadores en pantalla dividida, el Draw de cada instancia corre **cuatro veces
por fotograma**.

---

## 3. Nada de lógica de juego en el Draw

> **Por ese motivo, evita meter lógica de juego en el Draw**: posición del jugador,
> movimiento, colisiones… Eso va en el **Step**. En el Draw, **solo código visual**.

No es una regla absoluta —te puedes saltar la distinción—, pero:

> Si no mantienes el código organizado así, **te complicarás mucho la vida más adelante**.

---

## 4. Por qué tu personaje desaparece

Si ejecutas el juego **con el evento Draw vacío**, el personaje **desaparece**.

Sigue existiendo (la cámara se mueve con WASD y su Step corre), pero no tiene
representación visual. El motivo:

> **Toda instancia de GameMaker tiene un evento Draw por defecto** que simplemente dibuja el
> sprite en su `sprite_index`, `image_index`, `image_xscale`, etc.
>
> **En cuanto creas tu propio evento Draw, ese comportamiento se sobrescribe.** A partir de
> ahí, renderizar tu personaje es cosa tuya.

---

## 5. `draw_self()`

Si quieres invocar el dibujado por defecto:

```gml
draw_self();
```

Hace básicamente lo que haría GameMaker: dibuja `sprite_index`, `image_index`,
`image_xscale`, `image_yscale`, rotación y alguna variable más.

> El autor lo llama una «mención honorífica»: no es de las funciones más interesantes, pero
> merece la pena conocerla.

---

## 6. Las variables `image_*`

Son variables que **toda instancia trae automáticamente** y que se usan al dibujar:

| Variable | Efecto |
|---|---|
| `sprite_index` | Qué sprite se dibuja |
| `image_index` | Qué fotograma |
| `image_xscale` / `image_yscale` | Escalado |
| `image_angle` | Rotación |
| `image_blend` | Color de mezcla |
| `image_alpha` | Transparencia |

Son comodísimas para arrancar rápido sin escribir código repetitivo. Pero:

> **También son algo que hay que «desaprender»** cuando empiezas a dibujar por tu cuenta,
> porque hacen cosas «detrás de las cortinas» que pueden despistar al principio.

`x` e `y` también se usan al dibujar, pero representan la posición de la instancia y sirven
para mucho más.

---

## 7. `draw_sprite()`

```gml
draw_sprite(sprite, subimg, x, y);
```

Cuatro argumentos: el **sprite**, el **subimage** (fotograma), y las coordenadas **X** e
**Y**.

```gml
draw_sprite(spr_character, 0, x, y);
```

Con valores fijos obtienes **un sprite estático**: no se anima ni se voltea.

Si en su lugar usas las variables de la instancia:

```gml
draw_sprite(sprite_index, image_index, x, y);
```

recuperas la animación (porque `image_index` avanza solo), pero **no** el volteo al mirar
a izquierda/derecha, porque nada en ese código lo provoca.

---

## 8. `draw_sprite_ext()`

La función «extendida» añade **cinco argumentos más**:

```gml
draw_sprite_ext(sprite, subimg, x, y, xscale, yscale, rot, colour, alpha);
```

| Argumento | Significado |
|---|---|
| `xscale` / `yscale` | Escalado; `1` = normal, `-1` = **volteo horizontal** |
| `rot` | Rotación en **grados**, en sentido **antihorario** |
| `colour` | Color de mezcla; **`c_white`** = sin mezcla |
| `alpha` | Transparencia; **`1`** = opaco, `0` = invisible |

```gml
draw_sprite_ext(sprite_index, image_index, x, y,
                image_xscale, image_yscale,
                image_angle, c_white, 1);
```

Esto es, **en esencia, lo que hace `draw_self()` por dentro**.

Puedes no usar las variables integradas y pasar las tuyas: para escalar ×2 en vertical,
rotar 90°, teñir de rojo o poner alfa 0,5.

---

## 9. Color: por qué el neutro es blanco

> **Puede resultar contraintuitivo, pero el color por defecto es el blanco.**

La razón es matemática: el color de mezcla se **multiplica** por el color del sprite.

- El **blanco** es el **elemento neutro multiplicativo** del color: cualquier color × blanco
  = ese color.
- El **negro** es el «cero»: cualquier color × negro = negro.

Además:

- GameMaker trae **muchas constantes** `c_*` (`c_red`, `c_lime`, `c_orange`…). El manual
  las lista con su **valor decimal** (el autor preferiría hexadecimal).
- Puedes insertar un **código hexadecimal** directamente: rojo = `0xFF0000`.
- Hay funciones para crear colores a partir de valores RGB.

> **No es un tinte ni un cambio de tono: es una mezcla multiplicativa.** Si has jugado con
> la mezcla multiplicativa en Photoshop, te sonará.

---

## 10. Alfa: transparencia de 0 a 1

En GameMaker (y en gráficos por ordenador en general), la transparencia es un **factor de
multiplicación**:

| Valor | Significado |
|---|---|
| `1` | 100 % opaco |
| `0,5` | 50 % transparente |
| `0` | Invisible |

> El autor advierte: la transparencia se complica cuando entran en juego **el orden de
> dibujado** y la superposición de sprites transparentes. Tema para otro día.

---

## 11. `draw_sprite_stretched()` y el origen

```gml
draw_sprite_stretched(sprite, subimg, x, y, w, h);
```

En lugar de una escala, le das **un ancho y un alto** concretos: es como dibujar un
rectángulo y rellenarlo con la textura del sprite.

```gml
draw_sprite_stretched(sprite_index, image_index, x, y, 100, 100);
```

> **No es lo habitual para personajes** (se nota al pasar del sprite quieto al de correr, si
> tienen tamaños distintos). Es más típico para **interfaz de usuario**.

### ⚠️ Importante: el origen

> **`draw_sprite()` y `draw_sprite_ext()` respetan el origen del sprite.**
>
> Pero **algunas funciones avanzadas, como `draw_sprite_stretched()`, NO lo hacen**:
> asumen que el origen está **arriba a la izquierda**.

Si necesitas compensarlo, tendrás que **hacer la aritmética tú mismo** para desplazar las
coordenadas.

---

## 12. `draw_sprite_part()`, `draw_sprite_tiled()` y `draw_sprite_general()`

| Función | Para qué |
|---|---|
| **`draw_sprite_part()`** | Dibujar **solo una porción** del sprite. Más típico de interfaz que de personajes |
| **`draw_sprite_part_ext()`** | Lo mismo, más color y alfa |
| **`draw_sprite_tiled()`** | **Repetir el sprite en mosaico** para rellenar una zona |
| **`draw_sprite_tiled_ext()`** | Lo mismo, más color y alfa |
| **`draw_sprite_general()`** | **El abuelo de todas**: combina casi todo lo anterior |

### `draw_sprite_general()`

Permite especificar:

- Una **porción** del sprite (como `draw_sprite_part`).
- El escalado **X** e **Y** (como `draw_sprite_ext`).
- Un color **para cada esquina** (superior izquierda, superior derecha, inferior derecha,
  inferior izquierda).
- El **alfa**.

> El autor echa de menos poder dar un alfa distinto a cada esquina, pero reconoce que la
> función ya llega muy lejos: para eso, mejor un **shader**.

---

## 13. Ejemplo completo: personalización de personaje por capas

El autor construye un sistema de **personalización de personaje** con sprites de su juego
*Wizard Ducks in the Lost Hat*: un pato mago con sombrero morado.

Ha separado el personaje en **capas**:

| Sprite | Qué es |
|---|---|
| `spr_duck_still_body` / `spr_duck_walk_body` | El cuerpo (quieto / andando) |
| `spr_duck_still_hat` / `spr_duck_walk_hat` | El sombrero |
| `spr_duck_still_staff` / `spr_duck_walk_staff` | El bastón mágico |
| `spr_duck_still_staff_wing` / `spr_duck_walk_staff_wing` | El ala que va **encima** del bastón |

### Create event

```gml
// ¿Qué capas lleva puestas?
has_hat = false;
has_staff = false;

// Sprites de cada capa (variables propias, no integradas)
sprite_index_hat = spr_duck_still_hat;
sprite_index_staff = spr_duck_still_staff;
sprite_index_staff_wing = spr_duck_still_staff_wing;
```

### Step event: conmutar con F1-F4

```gml
if (keyboard_check(vk_f1)) { has_hat = true;  }
if (keyboard_check(vk_f2)) { has_hat = false; }
if (keyboard_check(vk_f3)) { has_staff = true;  }
if (keyboard_check(vk_f4)) { has_staff = false; }
```

Cuando el personaje anda, también se cambian los sprites de las capas a sus versiones
`walk`.

### Draw event

```gml
// El bastón se dibuja ANTES que el cuerpo, para que quede DETRÁS
if (has_staff)
{
    draw_sprite_ext(sprite_index_staff, image_index, x, y,
                    image_xscale, image_yscale, 0, c_white, 1);
}

// El cuerpo
draw_sprite_ext(sprite_index, image_index, x, y,
                image_xscale, image_yscale, 0, c_white, 1);

// El ala va ENCIMA del bastón para que parezca que lo sujetas
if (has_staff)
{
    draw_sprite_ext(sprite_index_staff_wing, image_index, x, y,
                    image_xscale, image_yscale, 0, c_white, 1);
}

// El sombrero, arriba de todo
if (has_hat)
{
    draw_sprite_ext(sprite_index_hat, image_index, x, y,
                    image_xscale, image_yscale, 0, c_white, 1);
}
```

### Dos claves del sistema

1. **Todos los sprites están dibujados a la misma escala y con el origen en el mismo
   sitio.** Por eso no hay que alinear nada: al superponerlos encajan directamente.
   > Así es como conviene preparar los sprites para un creador de personajes.
2. **Los fotogramas están sincronizados**: el fotograma 5 del sombrero corresponde al
   fotograma 5 del cuerpo. Como todas las capas usan el **mismo `image_index`**, salen
   sincronizadas automáticamente.

### Orden de dibujado

El bastón dibujado **antes** que el cuerpo queda **detrás**; dibujado después, parecería
pegado al pico. El ala va **después** del cuerpo para tapar el bastón y que parezca que lo
sujetas.

> El autor reconoce que el código tiene **duplicación** (copiar y pegar) y que hay formas
> mejores de arquitectarlo. Lo deja para vídeos posteriores sobre gestión de datos y
> «cosas que puedes hacer para no pegarte un tiro en el pie más adelante».

---

## Puntos clave

1. **«Dibujar» = poner una imagen en pantalla.**
2. El evento **Draw** corre cada fotograma, **se salta si el objeto es invisible** y **se
   repite por cada viewport activo**.
3. **Nada de lógica de juego en el Draw**: eso va en el Step.
4. **Crear un Draw sobrescribe el dibujado por defecto** y tu objeto desaparece.
5. **`draw_self()`** invoca el dibujado por defecto.
6. **`draw_sprite(sprite, subimg, x, y)`**: cuatro argumentos.
7. **`draw_sprite_ext(..., xscale, yscale, rot, colour, alpha)`**: nueve argumentos.
8. **Blanco = sin mezcla de color** (elemento neutro multiplicativo).
9. **Rotación en grados, en sentido antihorario.** **Alfa de 0 a 1.**
10. **`draw_sprite_stretched()` NO respeta el origen**: asume arriba-izquierda.
11. **`draw_sprite_general()`** es la más completa (porción, escala, color por esquina).
12. Para personalización por capas: **origen y escala idénticos + fotogramas sincronizados
    + mismo `image_index`**.
13. **El orden de dibujado determina qué queda delante.**

---

## Ejercicio propuesto

> **Objetivo:** sustituir el dibujado automático por el tuyo propio y montar un personaje
> por capas.

**Parte A — El evento Draw**

1. Añade un evento **Draw** vacío y ejecuta. Comprueba que tu personaje **desaparece** pero
   sigue existiendo (la cámara lo sigue).
2. Añade `draw_self();` y comprueba que vuelve a verse como antes.
3. Sustitúyelo por:
   ```gml
   draw_sprite(spr_character, 0, x, y);
   ```
   Comprueba que se ve **estático**: sin animación ni volteo.
4. Cambia a `draw_sprite(sprite_index, image_index, x, y);` y comprueba que **se anima**
   pero **no se voltea**.

**Parte B — `draw_sprite_ext`**

5. Pasa a la versión extendida usando `image_xscale`, `image_yscale`, `image_angle`,
   `c_white` y `1`. Comprueba que ya se voltea.
6. Fija `image_yscale` a 2 y observa el estiramiento vertical.
7. Rota 90° y comprueba el sentido **antihorario**.
8. Prueba `c_red`, luego un código hexadecimal propio, y observa la **mezcla
   multiplicativa** (no un tinte).
9. Pon alfa `0.5` y comprueba el efecto fantasma.

**Parte C — Funciones especializadas**

10. Usa `draw_sprite_stretched()` para que el sprite ocupe 100 × 100. Fíjate en que **no
    respeta el origen** y calcula a mano el desplazamiento para compensarlo.
11. Usa `draw_sprite_tiled()` para rellenar la pantalla de personajes.

**Parte D — El proyecto (personalización)**

12. Consigue o dibuja un personaje en **tres capas** (cuerpo, sombrero, accesorio) con
    **el mismo tamaño y el mismo origen**, y con fotogramas sincronizados.
13. Crea las variables `has_hat` y `has_staff`, y conmutarlas con F1-F4.
14. En el Draw, dibuja cada capa con `draw_sprite_ext()` y el **mismo `image_index`**.
15. **Experimenta con el orden:** dibuja el accesorio antes y después del cuerpo y observa
    la diferencia. Decide el orden correcto para que parezca que lo sujetas.

**Reto extra:** el autor admite que su código tiene mucha duplicación. Reescríbelo usando
un **array de capas** y un bucle `for` que las recorra todas. Es el primer paso hacia la
«gestión de datos» que él promete para vídeos posteriores.
