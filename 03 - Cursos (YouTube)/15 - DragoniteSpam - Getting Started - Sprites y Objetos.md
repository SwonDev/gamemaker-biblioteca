# 15 · DragoniteSpam — Sprites y objetos

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 3 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=3XGmn9EgzmU> |
| **Duración** | 28 min 43 s |
| **Publicado** | 13 de diciembre de 2025 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `image_xscale`, `image_yscale`, `image_speed`, `image_index`, `sprite_index`, `xprevious`/`yprevious`, `sprite_width` |

Hasta ahora nuestro personaje era una cara sonriente. En gamedev, a eso se le llama
**«programmer art»**: la jerga para «lo que sale cuando le pides un dibujo a alguien que
no es artista». Este capítulo lo arregla.

## Índice de contenido

1. De dónde sacar sprites
2. Importar sprites: arrastrar y soltar
3. Hojas de animación: *Convert to Frames* y el sufijo `_strip`
4. El editor de sprites de GameMaker
5. Velocidad de animación (FPS)
6. El origen del sprite
7. Ajustes avanzados: texturas, máscara y *nine slice*
8. Escalar con `image_xscale` e `image_yscale`
9. Mirar a izquierda y derecha
10. `image_speed` e `image_index`
11. `sprite_index`: cambiar de sprite
12. Por qué el origen importa al voltear y rotar
13. Sprites de correr e idle
14. `xprevious` e `yprevious`
15. Otras variables `image_*` y `sprite_*`

---

## 1. De dónde sacar sprites

El editor de sprites de GameMaker es «una versión algo más avanzada de Microsoft
Paint». Cumple su función para **gráficos temporales**, pero para arte de verdad lo
normal es:

- Software dedicado de pixel art: **Aseprite**.
- Software de pintura: **Krita**, Photoshop…
- **itch.io**: una web orientada al desarrollo indie donde puedes alojar, vender o
  regalar juegos… y también **distribuir assets** (colecciones de sprites, a menudo
  gratis).

---

## 2. Importar sprites: arrastrar y soltar

Hay **tres o cuatro formas** de meter un sprite en GameMaker:

1. **Arrastrarlo desde el explorador de archivos** hasta el IDE (lo más rápido).
2. Botón **Import** en el sprite → abre un buscador de archivos.
3. Dentro del editor de sprites: **Import images** → el mismo buscador.
4. …y se puede **exportar a PNG** si quieres ir en la otra dirección.

---

## 3. Hojas de animación: *Convert to Frames* y el sufijo `_strip`

Es habitual que una animación venga como **una sola imagen con todos los fotogramas en
fila**. Al importarla entra como un único sprite, que no es lo que queremos. Hay dos
soluciones.

### A) Utilidad *Convert to Frames*

En el editor de sprites: **Convert to Frames**. Pide:

| Campo | Ejemplo |
|---|---|
| Number of frames | 4 |
| Number of frames per row | 4 |
| Frame width | 32 |
| Frame height | 32 |
| Offsets / padding | opcional |

Al pulsar **Convert**, la imagen se parte en **cuatro subimages** que GameMaker
reconoce como fotogramas de la misma animación.

### B) El sufijo mágico `_strip`

> Si al archivo le añades el sufijo **`_strip4`** antes de importarlo, GameMaker lo
> **trocea automáticamente** en cuatro subimages sin que tengas que hacer nada más.

Es comodísimo, porque lo normal es recibir las animaciones como secuencia lineal y no
como archivos separados.

**Condición:** todos los fotogramas deben tener **el mismo tamaño**. Una imagen de
128 px de ancho no se puede partir en 6 fotogramas iguales: GameMaker te avisará de que
no puede dividirla (la importará, pero sin trocear).

> **32 × 32** es un tamaño extremadamente común para sprites de personaje en GameMaker.
> Puedes subir si quieres más resolución, o bajar si buscas un aspecto tipo Game Boy
> original.

---

## 4. El editor de sprites de GameMaker

El editor es bastante básico. Si has usado cualquier programa de imagen, sabrás qué hace
casi todo.

> Si el sprite tiene varios fotogramas, abajo verás una **línea de tiempo** que puedes
> arrastrar, y un botón de **play** para reproducir la animación.

> **Debate en la comunidad:** «¿vale la pena siquiera que GameMaker tenga editor de
> sprites?». El autor **defiende su existencia** porque es útil para dibujar cosas
> rápidas de vez en cuando, pero no llega a decir que sea «un buen editor de imágenes».

En la práctica, autorizarás el arte en software externo y solo lo traerás a GameMaker.

---

## 5. Velocidad de animación (FPS)

El valor por defecto es **30 FPS**, que suele ser demasiado rápido. Para una animación
de *idle* de cuatro fotogramas, el autor prueba 10, 8 y se queda en **6 FPS**.

Esto afecta directamente a cómo se reproduce la animación en el juego.

---

## 6. El origen del sprite

> El **origen del sprite** define el punto **desde el que se dibuja** el sprite cuando lo
> asignas a un objeto o lo dibujas manualmente.

- Por defecto, GameMaker lo pone en la **esquina superior izquierda**.
- Lo habitual es **middle center** o **bottom center**.
- **Para personajes, la tradición es bottom center.**

El origen afecta a tres cosas:

1. Dónde se dibuja el sprite respecto a la posición del objeto.
2. El **punto de rotación** si lo rotas.
3. El **punto de escalado** si lo escalas.

Se puede cambiar de tres maneras: arrastrando la cruz en el editor, escribiendo las
coordenadas, o con el **desplegable de la esquina superior derecha**.

---

## 7. Ajustes avanzados: texturas, máscara y *nine slice*

| Ajuste | Para qué sirve |
|---|---|
| **Advanced texture settings** | Cómo se organizan los sprites al compilar. Solo importa si tienes **muchísimos** sprites |
| **Collision mask** | Detección de colisiones (tema de otro vídeo) |
| **Nine slice** | Para sprites de interfaz que se estiran y repiten de forma controlada. Muy divertido, pero no toca ahora |

---

## 8. Escalar con `image_xscale` e `image_yscale`

Un sprite de 32 × 32 **no se escala solo** al ejecutar el juego. Para agrandarlo:

```gml
// Create event
image_xscale = 4;
image_yscale = 4;
```

El valor por defecto es `1`. Con `2`, el sprite se dibuja al doble de tamaño.

> **⚠️ Aviso importante:** «Si llegas al punto de plantearte poner el `image_xscale` e
> `image_yscale` de **todos** los objetos a 4, eso es señal de que deberías estar
> trabajando con los ajustes de **cámara y viewport** para hacer zoom sobre tu mundo.»

Escalar objeto a objeto es un parche; la cámara es la solución correcta.

---

## 9. Mirar a izquierda y derecha

Truco sencillísimo y muy usado: **escala horizontal negativa**.

```gml
// Step event, junto al movimiento
if (keyboard_check(ord("D")))
{
    x += 4;
    image_xscale = 4;      // Mirando a la derecha
}

if (keyboard_check(ord("A")))
{
    x -= 4;
    image_xscale = -4;     // Espejado horizontal
}
```

> Es «la forma rápida y sucia» de cambiar de dirección. **Parece demasiado simple para
> funcionar en un juego real, pero muchísimos juegos lo hacen.**
>
> Si el sprite se limita a reflejarse horizontalmente, **no tiene sentido** tener
> sprites, animaciones o nada por separado para izquierda y derecha.

---

## 10. `image_speed` e `image_index`

### `image_speed`

Es un **multiplicador** de la velocidad definida en el editor de sprites:

| Valor | Efecto |
|---|---|
| `1` | La velocidad del editor (por ejemplo 6 FPS → 183 ms por fotograma) |
| `2` | El doble de rápido |
| `0.5` | La mitad de rápido |
| `0` | **No se anima** |

### `image_index`

Es el **índice del fotograma que se está dibujando**. GameMaker lo incrementa solo cada
step según `image_speed` y la velocidad del editor. Puedes **leerlo y también fijarlo**
para mostrar un fotograma concreto.

### Patrón: animar solo al moverse

Fija `image_speed = 0` **al principio del Step** y vuelve a ponerlo a `1` dentro de
cada comprobación de movimiento:

```gml
// Step event
image_speed = 0;   // Por defecto, quieto

if (keyboard_check(ord("D"))) { x += 4; image_xscale =  4; image_speed = 1; }
if (keyboard_check(ord("A"))) { x -= 4; image_xscale = -4; image_speed = 1; }
if (keyboard_check(ord("W"))) { y -= 4; image_speed = 1; }
if (keyboard_check(ord("S"))) { y += 4; image_speed = 1; }
```

Alternativas que menciona el autor:

- Encadenar todo en un `if / else if / else` y que el **`else` final** ponga
  `image_speed = 0`.
- Reiniciar también `image_index` al parar, para volver al primer fotograma (lo deja
  como ejercicio).

---

## 11. `sprite_index`: cambiar de sprite

`sprite_index` **no contiene un número**: contiene una **referencia al recurso de
sprite**.

> Los assets de GameMaker (sprites, objetos, rooms…) se pueden tratar como **valores**
> dentro de expresiones.

```gml
if (keyboard_check_pressed(vk_tab))
{
    sprite_index = spr_player;   // ¡Cambiamos de sprite!
}

if (keyboard_check_pressed(vk_space))
{
    sprite_index = spr_character;   // Volvemos
}
```

---

## 12. Por qué el origen importa al voltear y rotar

Con el origen en la **esquina superior izquierda**, al voltear el personaje con
`image_xscale` negativo verás que **«salta» de sitio**.

La razón: el objeto sigue en su posición (la esquina), pero el sprite se dibuja con
escala negativa, así que **se refleja alrededor de esa esquina** y se desplaza
visiblemente.

> Por eso es útil poner el origen **en el centro** (o abajo-centro): así el volteo ocurre
> **en el sitio**.

Y lo mismo para **rotar**: si vas a rotar un sprite, pon el origen en **middle center**
para que gire sobre su centro.

---

## 13. Sprites de correr e idle

El autor descarga también una hoja de animación de **correr** de seis fotogramas:

1. Renombra el archivo añadiendo **`_strip6`** para que GameMaker la trocee sola.
2. Le pone el origen en **bottom center**.
3. Ajusta el **FPS a 10**.

Después, en el Step, en lugar de tocar `image_speed`, cambia directamente el sprite:

```gml
if (keyboard_check(ord("D"))) { x += 4; image_xscale =  4; sprite_index = spr_character_run; }
if (keyboard_check(ord("A"))) { x -= 4; image_xscale = -4; sprite_index = spr_character_run; }
```

El problema: **al parar no vuelve al sprite de idle**. Hay que añadir una comprobación
final.

---

## 14. `xprevious` e `yprevious`

GameMaker **no tiene** una variable que te diga directamente «¿se ha movido este
objeto este fotograma?», pero sí tiene:

- **`xprevious`** — la posición X en el fotograma anterior.
- **`yprevious`** — la posición Y en el fotograma anterior.

> El autor confiesa que es **lo que suele acabar usando** para saber si un objeto se ha
> movido desde el fotograma anterior. «Parece demasiado simple para funcionar en un juego
> de verdad, pero honestamente funciona casi siempre, salvo que estés haciendo algo muy
> raro con el movimiento.»

### Dos usos

**¿Se ha movido?**

```gml
if ((xprevious != x) || (yprevious != y))
{
    // El objeto se ha movido este fotograma
}
```

**¿Está quieto? (para volver al sprite de idle)**

```gml
if ((x == xprevious) && (y == yprevious))
{
    sprite_index = spr_character;   // Volver al idle
}
```

> **Corrección en directo:** el autor escribe primero la versión con `!=` y `||`, se da
> cuenta del error y lo corrige a `==` con `&&`. Para comprobar que **NO** se ha movido,
> hay que usar **igualdades** y **AND**: si X no ha cambiado **y** Y tampoco, está quieto.

---

## 15. Otras variables `image_*` y `sprite_*`

Si escribes `image_` en el editor, verás todas las variables integradas relacionadas:

| Variable | Significado |
|---|---|
| `image_alpha` | Transparencia con la que se dibuja |
| `image_blend` | Color de tinte |
| `image_number` | **Número de fotogramas** del sprite actual |
| `image_angle` | **Rotación** en grados |
| `image_index` | Fotograma actual |
| `image_speed` | Multiplicador de velocidad |
| `image_xscale` / `image_yscale` | Escalado |

Y del lado del sprite:

| Variable | Contenido |
|---|---|
| `sprite_width` / `sprite_height` | Tamaño del sprite asignado |
| `sprite_xoffset` / `sprite_yoffset` | Posición del origen |

> **Son de solo lectura**: no puedes asignarles un valor. Para estirar el sprite usa
> `image_xscale` / `image_yscale`.

Detalle muy útil: **tienen en cuenta la escala**. Un sprite de 32 × 32 con
`image_xscale = 4` da `sprite_width = 128`.

---

## Puntos clave

1. **«Programmer art»** es la jerga para el arte hecho por quien no es artista.
2. **Arrastra los sprites** desde el explorador de archivos al IDE para importarlos.
3. **Usa el sufijo `_stripN`** para que GameMaker trocee hojas de animación
   automáticamente; o la utilidad **Convert to Frames**.
4. Los fotogramas deben tener **todos el mismo tamaño**.
5. **Origen bottom center para personajes**; **middle center** si vas a rotar.
6. **`image_xscale` / `image_yscale`** escalan. Si necesitas escalarlo todo, usa la
   **cámara y el viewport**, no esto.
7. **`image_xscale` negativo** refleja el sprite: es la forma estándar de mirar a
   izquierda/derecha.
8. **`image_speed` es un multiplicador** del FPS del editor. `0` detiene la animación.
9. **`image_index`** es el fotograma actual y puedes fijarlo.
10. **`sprite_index` guarda una referencia al recurso**, no un número.
11. **`xprevious` / `yprevious`** permiten saber si un objeto se ha movido.
12. **`sprite_width` y compañía son de solo lectura** y **ya incluyen la escala**.

---

## Ejercicio propuesto

> **Objetivo:** montar un personaje animado que mire a los lados, corra al moverse y
> vuelva a su animación de idle al parar.

**Parte A — Importar**

1. Descarga un pack de sprites gratuito de **itch.io** (busca uno con animaciones de
   *idle* y *run*).
2. Arrastra la hoja de *idle* al IDE y comprueba que entra como una sola imagen.
3. Renombra el archivo añadiendo **`_strip4`** (o el número de fotogramas que tenga) y
   vuelve a importarlo. Comprueba que se trocea sola.
4. Haz lo mismo con la hoja de *run*, usando `_strip6`.
5. **Prueba el error:** renombra uno a `_strip7` con una imagen que no sea divisible y
   lee el aviso.

**Parte B — Ajustes**

6. Pon el origen de ambos sprites en **bottom center**.
7. Ajusta el FPS del *idle* a **6** y el del *run* a **10**. Usa el botón de *play* para
   comprobarlo.
8. Asigna el sprite de *idle* a `obj_player` arrastrándolo desde el navegador de
   recursos.

**Parte C — Escala y dirección**

9. En el Create, pon `image_xscale = 4;` e `image_yscale = 4;`.
10. En el Step, añade el movimiento WASD y haz que **A** ponga `image_xscale = -4` y
    **D** ponga `image_xscale = 4`.
11. Comprueba que el personaje mira hacia el lado correcto.

**Parte D — Animación**

12. Deja el origen en **top-left** a propósito y observa cómo el personaje **salta de
    sitio** al voltear. Vuelve a ponerlo en bottom-center y comprueba la diferencia.
13. Fija `image_speed = 0` al principio del Step y `image_speed = 1` en cada
    comprobación de movimiento.
14. Cambia a `sprite_index = spr_character_run` al moverse.
15. Añade la comprobación final con `xprevious` / `yprevious` para volver al *idle* al
    parar. **Cuidado con usar `==` y `&&`.**
16. *Tarea del autor:* haz que al parar también se reinicie `image_index` a 0, para que
    la animación siempre empiece por el primer fotograma.

**Reto extra:** muestra por pantalla el valor de `sprite_width` con `show_debug_message`
y comprueba que con `image_xscale = 4` un sprite de 32 × 32 reporta **128**. Explica por
qué eso es útil para calcular colisiones.
