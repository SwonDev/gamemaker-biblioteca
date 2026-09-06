# 11 · Animaciones y conjuntos de baldosas (tile sets)

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 11 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=WaSRE8_r3U8> |
| **Duración** | 23 min 44 s |
| **Publicado** | 31 de enero de 2026 |
| **Nivel** | Intermedio |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `image_xscale`, `image_speed`, `image_index`, `sprite_index`, `layer_tilemap_get_id` |

Dos técnicas que dan el salto de «prototipo» a «juego con pinta profesional»:
**animar sprites según el estado del personaje** y **sustituir los bloques por un
conjunto de baldosas** que se conecta automáticamente.

## Índice de contenido

1. Preparativos y atajos de prueba
2. Los tres sprites del saltador
3. El origen Bottom Center
4. El truco del sprite de salto
5. Recortar el lienzo al contenido real
6. Fijar la máscara de colisión
7. `image_xscale`: voltear el personaje
8. `image_speed`, `image_index` y `sprite_index`
9. El sistema de prioridades de animación
10. Depurar el apex del salto
11. Crear el conjunto de baldosas
12. Autotiling de 47 baldosas
13. Dibujar con baldosas en la room
14. Colisiones contra el tile map
15. Aplicarlo también a los enemigos

---

## 1. Preparativos y atajos de prueba

Todo este capítulo se hace en el **juego de plataformas**. Antes de empezar, el autor
cambia las entradas a **A y D** para izquierda/derecha y **W** para saltar.

> El motivo es puramente práctico: así puede probar con la **mano izquierda** mientras
> usa el ratón con la derecha para abrir y cerrar el juego.

---

## 2. Los tres sprites del saltador

El autor ha preparado tres sprites «rudimentarios» a propósito: **no importa que sean
feos**, solo sirven para enseñar a animar.

| Sprite | Contenido | FPS |
|---|---|---|
| **`sJumperStill`** | 2 fotogramas: de pie y «respirando» agachándose | **3** |
| **`sJumperRun`** | 2 fotogramas con brazos y piernas moviéndose | **10** |
| **`sJumperJump`** | Copia de `sJumperRun` | **0** |

Con FPS 3, el sprite quieto produce un efecto de **respiración pesada** muy convincente
con solo dos fotogramas.

---

## 3. El origen Bottom Center

Los tres sprites usan origen **Bottom Center**. Las dos razones:

- **Center (centrado horizontal):** necesario para poder **voltear** el personaje a
  izquierda y derecha de forma simétrica.
- **Bottom (abajo):** en un plataformas se colocan los personajes **a ras de suelo**.
  Es la buena práctica habitual.

---

## 4. El truco del sprite de salto

Para el salto no hace falta dibujar nada nuevo:

1. **Duplica `sJumperRun`** y llámalo `sJumperJump`.
2. Déjalo **exactamente igual**, pero pon el **FPS a 0**.

¿Por qué funciona? Porque al detener la animación:

- El **fotograma 0** parece que el personaje **se impulsa desde el suelo**.
- El **fotograma 1** parece que está **aterrizando**.

Luego elegiremos uno u otro según si sube o baja. Dos estados por el precio de un
sprite.

---

## 5. Recortar el lienzo al contenido real

Al dibujar, el autor dejó píxeles vacíos a los lados. Cuenta:

- **2 píxeles sin usar a la izquierda y 2 a la derecha** → se pueden quitar **4 de
  ancho**.
- Ningún fotograma toca el borde superior → se puede quitar **1 de alto**.

El lienzo pasa de **20 × 40** a **16 × 39**.

---

## 6. Fijar la máscara de colisión

Problema: si el objeto usa *Same as Sprite*, **cada vez que cambies el sprite cambia
también su máscara de colisión**, y eso rompe las colisiones del plataformas.

Solución: dedicar un sprite exclusivo a la máscara.

1. El sprite `sJumper` se queda como **rectángulo sólido de 16 × 39**, relleno de un
   color chillón.
2. Origen **Bottom Center**.
3. Máscara de colisión: **Full Image** (que ocupe toda la imagen).
4. En `oJumper`, en **Collision Mask**, deja de estar en *Same as Sprite* y
   selecciona explícitamente **`sJumper`**.

> Así, aunque en pantalla se muestre `sJumperStill`, `sJumperRun` o `sJumperJump`,
> **la máscara es siempre la misma**.

---

## 7. `image_xscale`: voltear el personaje

**Nueva región `ANIMATE ME` en el Step de `oJumper`:**

```gml
#region ANIMAR
// --- Orientar en la dirección correcta ---
if (hsp != 0)
{
    image_xscale = sign(hsp);
}
```

`image_xscale` escala el sprite horizontalmente:

| Valor | Efecto |
|---|---|
| `1` | Tamaño normal |
| `2` | El doble de ancho |
| **negativo** | **Voltea el sprite en su eje horizontal** |

Como el origen es **Bottom Center**, el volteo ocurre sobre ese punto y el personaje
simplemente **mira hacia el otro lado**.

`sign(hsp)` da `1` si vamos a la derecha y `-1` si vamos a la izquierda: perfecto.

---

## 8. `image_speed`, `image_index` y `sprite_index`

| Variable | Significado |
|---|---|
| `sprite_index` | **Qué sprite** se está mostrando |
| `image_speed` | Velocidad de animación como **porcentaje** del FPS del sprite |
| `image_index` | **Qué fotograma** se muestra |

> `image_speed` es un **porcentaje**, no una velocidad absoluta. `1` = 100 % de los FPS
> del sprite; `0.5` = 50 %. Si el sprite va a 3 FPS y pones `image_speed = 0.33`, se
> animará a **1 fotograma por segundo**.

Detalle crítico: como el sprite de salto necesita `image_speed = 0` (quieto), **cada vez
que volvamos a un sprite animado hay que devolver `image_speed` a 1**.

---

## 9. El sistema de prioridades de animación

```gml
// --- Cambiar sprites ---
if ((hsp == 0) && (vsp == 0))
{
    // Prioridad más alta: quieto
    image_speed = 1;
    sprite_index = sJumperStill;
}
else if (vsp != 0)
{
    // Saltando o cayendo
    sprite_index = sJumperJump;
    image_speed = 0;            // Este sprite NO se anima

    if (vsp < 0)
    {
        image_index = 0;        // Subiendo: impulsándose
    }
    else
    {
        image_index = 1;        // Cayendo: aterrizando
    }
}
else
{
    // Tercera prioridad: corriendo
    image_speed = 1;
    sprite_index = sJumperRun;
}
```

La lógica es una **cascada de prioridades**:

1. **¿Sin movimiento ninguno?** → quieto (respirando).
2. **¿Movimiento vertical?** → saltando o cayendo (y se elige el fotograma según el
   signo de `vsp`).
3. **Si no,** tiene que ser movimiento horizontal → corriendo.

> Fíjate en que la tercera rama no necesita comprobar nada: por descarte, **sabemos**
> que hay movimiento y que no es vertical.

---

## 10. Depurar el apex del salto

Al probar aparece un fallo sutil:

> **En el punto más alto del salto, `vsp` llega a 0 durante un instante.** En ese
> fotograma la primera condición se cumple y el personaje **parpadea** mostrando el
> sprite de correr.

La solución es añadir una comprobación más: solo mostramos el sprite de «quieto» si
**además** estamos en el suelo.

```gml
if ((hsp == 0) && (vsp == 0) && _on_ground)
```

> El autor se desvía de sus propios apuntes para arreglarlo en directo, y anota el
> cambio para futuras versiones del tutorial. Es un ejemplo perfecto de **depurar lo que
> ves**, no lo que esperabas ver.

---

## 11. Crear el conjunto de baldosas

Un **tile set** permite tener muros, suelos y techos que **se conectan entre sí
automáticamente**, en vez de depender de bloques sueltos.

1. Importa el sprite **`sTiles`** (el autor lo facilita para descargar). Parece
   confuso al principio: **cada cuadrado es una pieza distinta** del sistema de muros.
2. **FPS:** 0. **Origen:** arriba-izquierda (da igual).
3. Crea el grupo **`Tile Sets`** y dentro un nuevo **Tile Set** llamado **`tTiles`**.
4. Selecciona el sprite `sTiles`.
5. Ajusta el tamaño de baldosa al del dibujo: **20 × 20**.

---

## 12. Autotiling de 47 baldosas

1. Ve a **Autotiling** → **Add a new 47 tile set**.
2. Aparecerá un cuadro rojo: hay que **asignar cada baldosa** a su función.
3. Empieza por la **Z** de la esquina inferior derecha y continúa en orden:
   **A1, A2, A3, A4, A5, A6, A7…**

Reglas:

- **Haz clic una sola vez en cada baldosa**, en orden.
- Si te equivocas, usa el icono de la **papelera** y vuelve a empezar. No pasa nada.
- Puedes cambiar el nombre del autotile o dejarlo como está.

> **Plantilla de ayuda:** el autor incluye un sprite alternativo,
> **`tiles_grid_template`**, con **letras y números** dibujados. Cambiando el sprite del
> tile set a esa plantilla verás exactamente **qué hace cada casilla** (por ejemplo, F6
> es el cuadrado aislado; E6 es una esquina que conecta con un lateral derecho vertical
> o con una base horizontal).

Lo mejor: **puedes cambiar el sprite en cualquier momento sin perder la configuración
de autotiling**.

---

## 13. Dibujar con baldosas en la room

1. Selecciona la capa **`Collisions`**, haz `Shift` + arrastrar para seleccionarlo todo
   y **bórralo**.
2. Añade una capa nueva de tipo **Tile Layer** llamada **`Tiles`**, colocada **al
   fondo de todas**.
3. Donde pone *No Tile Set*, elige `tTiles`.
4. En **Libraries**, selecciona tu biblioteca de autotiling.
5. **Clic izquierdo** para dibujar; **clic derecho** para borrar.

Al dibujar una línea verás que **el sistema sabe automáticamente** qué pieza corresponde
a cada posición: esquinas, rectas, uniones… Dibuja un recinto alrededor de toda la room
y luego añade plataformas y nivel.

---

## 14. Colisiones contra el tile map

Usar baldosas en lugar de objetos tiene una ventaja de rendimiento:

> **Los tile sets no ejecutan código. Los objetos sí.** Por eso, si solo necesitas
> colisión, es más inteligente usar un tile set: **consume menos memoria**.

**En el Create de `oPlayer`:**

```gml
// Obtenemos el id del tile map de la capa "Tiles"
collision_tile = layer_tilemap_get_id("Tiles");

// Lista de todo aquello con lo que queremos chocar
all_collisions = [collision_tile];
```

`layer_tilemap_get_id()` devuelve el identificador del tile map que has pintado en la
capa indicada.

Después, en el código de colisiones, **sustituye `oBlock` por la variable
`all_collisions`** en las cuatro comprobaciones (las dos del `if` y las dos del
`while`, tanto horizontal como vertical):

```gml
if (place_meeting(x + hsp, y, all_collisions))
{
    var _one_pixel = sign(hsp);

    while (!place_meeting(x + _one_pixel, y, all_collisions))
    {
        x += _one_pixel;
    }

    hsp = 0;
}
x += hsp;
```

Y lo mismo para el eje vertical.

> Guardar las colisiones en un **array** (`[ ... ]`) tiene una gran ventaja: si más
> adelante quieres añadir más cosas con las que chocar, **solo tienes que tocar una
> línea**.

---

## 15. Aplicarlo también a los enemigos

1. Copia las dos líneas del Create en el **Create de `oEnemy`**.
2. Añade `oEnemy` a la lista para que **sigan chocando entre sí**:

```gml
collision_tile = layer_tilemap_get_id("Tiles");
all_collisions = [collision_tile, oEnemy];
```

3. En el **Step de `oEnemy`**, sustituye `[oBlock, oEnemy]` por **`all_collisions`** en
   todas las comprobaciones.

Ahora los enemigos colisionan correctamente contra el tile map y entre ellos.

---

## Puntos clave

1. **Origen Bottom Center** en personajes de plataformas: permite voltear y asentarlos
   en el suelo.
2. **Duplica el sprite de correr y ponle FPS 0** para obtener gratis los fotogramas de
   «impulsarse» y «aterrizar».
3. **Fija la máscara de colisión a un sprite propio**, nunca *Same as Sprite*, si vas a
   cambiar de sprite durante el juego.
4. **`image_xscale = sign(hsp)`** voltea el personaje horizontalmente.
5. **`image_speed` es un porcentaje** de los FPS del sprite: `1` = 100 %, `0` = detenido.
6. **Vuelve a poner `image_speed = 1`** al cambiar a un sprite animado.
7. **Prioridades en cascada**: quieto → salto/caída → correr. Cada rama descarta las
   anteriores.
8. **Cuidado con el apex del salto:** `vsp` pasa por 0. Añade `&& _on_ground`.
9. **El autotiling de 47 baldosas** se asigna haciendo clic en orden; usa la plantilla
   con letras para entender cada pieza.
10. **Puedes cambiar el sprite del tile set sin perder la configuración.**
11. **`layer_tilemap_get_id("capa")`** da el id del tile map para usarlo en colisiones.
12. **Guarda las colisiones en un array**: cambias un solo sitio y afecta a todo.
13. **Los tile sets no ejecutan código**: son más ligeros que los objetos para
    colisiones estáticas.

---

## Ejercicio propuesto

> **Objetivo:** animar al personaje según su estado y migrar las colisiones del juego a
> un tile set.

**Parte A — Animaciones**

1. Cambia las entradas a **A / D** y **W** para poder probar cómodamente.
2. Dibuja `sJumperStill` (2 fotogramas, FPS 3) y `sJumperRun` (2 fotogramas, FPS 10),
   ambos con origen **Bottom Center**. No hace falta que sean bonitos.
3. **Duplica `sJumperRun`** como `sJumperJump` y ponle **FPS 0**.
4. Cuenta los píxeles vacíos de tus sprites y **recorta el lienzo** al contenido real.
5. Deja `sJumper` como rectángulo sólido con máscara **Full Image** y origen Bottom
   Center, y fíjalo como máscara de `oJumper`.
6. Implementa la región `ANIMAR` con `image_xscale = sign(hsp)`.
7. Implementa la cascada de prioridades con `image_speed`, `sprite_index` e
   `image_index`.
8. Comprueba los cuatro estados: quieto, corriendo, subiendo (fotograma 0) y cayendo
   (fotograma 1).

**Parte B — Depuración**

9. Salta y observa el **apex**: ¿parpadea el personaje? Si es así, añade
   `&& _on_ground` a la condición de «quieto» y comprueba que se arregla.
10. Explica por qué `vsp` llega a valer 0 en el punto más alto del salto.

**Parte C — Tile set**

11. Descarga el sprite de baldosas del autor y créalo como `sTiles` (FPS 0).
12. Crea el grupo `Tile Sets` y el tile set `tTiles` con tamaño **20 × 20**.
13. Crea el **autotiling de 47 baldosas** y asígnalas en orden. Si te pierdes, cambia
    el sprite a `tiles_grid_template` para ver las coordenadas.
14. Borra el contenido de la capa `Collisions` y crea la capa de baldosas `Tiles` al
    fondo.
15. Dibuja un recinto completo alrededor de la room con clic izquierdo, y borra con
    clic derecho donde te equivoques.

**Parte D — Colisiones**

16. Añade `collision_tile` y `all_collisions` al Create de `oPlayer`.
17. Sustituye `oBlock` por `all_collisions` en las **cuatro** comprobaciones de cada eje.
18. Deja algunos bloques `oBlock` sueltos: siguen sirviendo para que los puedas
    destruir. Comprueba que chocas con ambos.
19. Repite el proceso en `oEnemy`, añadiendo `oEnemy` a su propio array.

**Reto extra:** añade un tercer elemento a `all_collisions` (por ejemplo un objeto
puerta `oPuerta`) **sin tocar el código de colisiones**. Comprueba que funciona y
explica por qué el array hace que esto sea posible.
