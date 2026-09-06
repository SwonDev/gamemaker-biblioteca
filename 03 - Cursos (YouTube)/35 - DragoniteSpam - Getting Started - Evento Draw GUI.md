# 35 · DragoniteSpam — El evento Draw GUI

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 23 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=8U2hWR6VwUM> |
| **Duración** | 15 min 2 s |
| **Publicado** | 8 de julio de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | evento Draw GUI, `display_get_gui_width()`, `display_get_gui_height()`, `display_set_gui_maximize()` |

## Índice de contenido

1. El problema: todo se dibuja relativo al mundo
2. Qué es el evento Draw GUI
3. Dos propiedades clave
4. Primer uso: texto fijo en pantalla
5. Qué suele ir en la capa GUI
6. Anclar elementos a los bordes
7. `display_get_gui_width()` y `display_get_gui_height()`
8. `window_get_width()` no es lo mismo
9. Escalar la GUI
10. Desplazar la GUI
11. Aviso sobre las UI layers

---

## 1. El problema: todo se dibuja relativo al mundo

Hasta ahora, todo lo que hemos dibujado está:

- **Relativo al jugador** (por ejemplo, texto flotando sobre su cabeza), o
- en **una posición fija del mundo**, que se queda atrás en cuanto la cámara se mueve.

Lo que **no** teníamos era una forma de dibujar algo **fijo en la ventana del juego**.

---

## 2. Qué es el evento Draw GUI

**GUI** = *Graphical User Interface* (interfaz gráfica de usuario).

Se añade como cualquier otro evento: **Add Event → Draw → Draw GUI**, justo debajo del
Draw normal.

> El autor se desmarca explícitamente: **este vídeo NO trata el sistema nuevo de *UI
> layers*** (capas de interfaz), añadido hace cosa de un año. Lo hará en el futuro, porque:
>
> - Son **mucho más complicadas** y requieren bastante más configuración.
> - Tienen «alguna que otra carencia» que las hace **irritantes** a veces.
>
> El evento Draw GUI, en cambio, **hace una sola cosa y la hace muy bien**.

---

## 3. Dos propiedades clave

### A) Se dibuja DESPUÉS de todo

> El Draw GUI ocurre **después** de que todos los objetos hayan ejecutado su Draw normal.

Por tanto:

> **Nada dibujado en un Draw normal puede tapar algo dibujado en Draw GUI** (salvo que
> consigas romper GameMaker de forma espectacular, cosa que el autor reconoce haber
> hecho).

### B) Ignora la cámara

> **Por defecto ignora cualquier escalado, zoom o transformación de la cámara.**

Si tu cámara tiene zoom (típico en pixel art), lo que dibujes en Draw GUI se dibuja **1:1
con la rejilla de píxeles de tu monitor**, en lugar de ampliarse con la cámara.

Esto es útil por dos motivos:

1. **Estética:** puedes tener la cámara muy ampliada y, aun así, la interfaz a resolución
   completa.
2. **Resoluciones:** si el jugador usa 720p, 1080p, 1440p o 4K, **no tienes que hacer nada
   especial** para que los elementos de interfaz escalen con el tamaño de la pantalla.

---

## 4. Primer uso: texto fijo en pantalla

Corta el texto que dibujabas en el Draw normal y pégalo en el **Draw GUI**, con
coordenadas fijas:

```gml
draw_set_halign(fa_left);
draw_set_valign(fa_top);
draw_text(32, 32, "Hace calor hoy, ¿verdad?");
```

Las coordenadas **(32, 32)** corresponden a la esquina superior izquierda, porque:

> En gráficos por ordenador, el punto **(0, 0)** suele ser la **esquina superior
> izquierda**.

Ahora el texto está **anclado arriba a la izquierda**, sin importar dónde vaya el jugador ni
dónde esté la cámara.

---

## 5. Qué suele ir en la capa GUI

Puedes dibujar **cualquier cosa**: sprites, texto, formas…

Lo más habitual:

| Elemento | Por qué |
|---|---|
| **Texto** | Muy común |
| **Barras de vida** | Deben seguir en pantalla |
| **Cajas de diálogo** | Al hablar con un NPC |
| Iconos, contadores, minimapas… | |

### Ejemplo: una barra de vida con corazones

El autor añade un sprite de corazón hecho en MS Paint «en cinco segundos» y dibuja diez:

```gml
draw_set_halign(fa_left);
draw_set_valign(fa_top);

for (var i = 0; i < 10; i++)
{
    draw_sprite(spr_health, 0, 32 + (i * 20), 32);
}
```

Si solo quieres dibujar en la esquina superior izquierda, **puedes escribir las coordenadas
directamente**: se interpretan relativas al origen de la pantalla.

---

## 6. Anclar elementos a los bordes

Para el lado contrario de la pantalla podrías hacer:

```gml
draw_set_halign(fa_right);
draw_text(1280 - 32, 32, " derecha");
```

**Problema:** si cambias el tamaño de la ventana a 1600 × 900, el texto se queda **flotando
en medio** de la pantalla, ya sin anclarse a la derecha.

---

## 7. `display_get_gui_width()` y `display_get_gui_height()`

La solución es **no escribir nunca el tamaño a mano**:

```gml
display_get_gui_width();
display_get_gui_height();
```

> Devuelven **el ancho y el alto de la GUI en píxeles**.

```gml
draw_set_halign(fa_right);
draw_text(display_get_gui_width() - 32, 32, " derecha");
```

Ahora da igual que la ventana mida 1280, 1600 o cualquier otra cosa: **el texto siempre
queda anclado al lado derecho**.

Lo mejor:

> **`display_get_gui_width()` y `..._height()` se adaptan automáticamente si escalas la
> GUI.** No tendrás que dividir ni multiplicar por ningún número.

---

## 8. `window_get_width()` no es lo mismo

Mención honorífica a:

```gml
window_get_width();
window_get_height();
```

> Estas dos **no tienen que ver directamente con la GUI**.

A menudo el tamaño de la ventana **coincide** con el de la GUI, pero **no tiene por qué**.

> Verás a mucha gente usar `window_get_width()` y `display_get_gui_width()`
> **indistintamente**, y **casi siempre se puede salir con la suya**… pero **ten presente
> que hay una distinción**.

---

## 9. Escalar la GUI

```gml
display_set_gui_maximize(xscale, yscale);
```

El autor lo demuestra condicionándolo a una tecla:

```gml
if (keyboard_check(vk_space))
{
    display_set_gui_maximize(2, 2);   // Interfaz al doble de tamaño
}
else
{
    display_set_gui_maximize(-1, -1); // Reset a 1:1. ⚠️ Sin argumentos NO resetea: maximiza a toda la ventana
}
```

Notas:

- Los argumentos **X** e **Y** son **opcionales**: llamarla sin argumentos **restablece la
  escala a 1**.
- También puedes decirlo explícitamente: `display_set_gui_maximize(1, 1);`.
- **No tienes que tocar nada más**: las coordenadas siguen funcionando igual porque
  `display_get_gui_width()` / `..._height()` **se adaptan solas**.

### Cuándo tiene sentido

> Si el jugador juega a **4K** (3840 × 2160) y no quieres que la interfaz se vea
> diminuta, puedes ampliarla para que equivalga a una interfaz de 1080p.

---

## 10. Desplazar la GUI

`display_set_gui_maximize()` admite **un tercer y cuarto argumento**: desplazamiento
horizontal y vertical.

```gml
display_set_gui_maximize(1, 1, 64, 32);   // Desplaza la interfaz
```

Es **menos útil** que la escala, pero tiene un caso claro:

> Si quieres dar soporte a **monitores ultraanchos** sin estirar toda la ventana, puedes
> **centrar la interfaz** para que el jugador no tenga que girar la cabeza a un lado para
> ver su barra de vida.

---

## 11. Aviso sobre las UI layers

Recordatorio del autor: las **UI layers** (capas de interfaz) son un sistema **más nuevo y
más complejo**, con algunas carencias. El evento Draw GUI **hace una cosa y la hace muy
bien**, y para empezar es la opción recomendable.

---

## Puntos clave

1. El **Draw GUI** dibuja relativo a la **ventana**, no al mundo.
2. Se ejecuta **después** de todos los Draw normales: **nada lo tapa**.
3. **Ignora el zoom y las transformaciones de la cámara** por defecto.
4. Ideal para **texto, barras de vida, cajas de diálogo** e interfaces en general.
5. Usa **`display_get_gui_width()` / `..._height()`** para anclar a los bordes: **nunca
   escribas el tamaño a mano**.
6. **`window_get_width()`** no es lo mismo que `display_get_gui_width()`.
7. **`display_set_gui_maximize(escalaX, escalaY)`** escala la interfaz; **con `(-1, -1)` la
   restablece**. ⚠️ El vídeo dice «sin argumentos», pero el manual es explícito: llamarla sin
   argumentos la **maximiza** a toda la ventana (escala para ajustarse al área completa). Ver
   `09 - Manual oficial/manual-lts-2026-es/GameMaker_Language/GML_Reference/Cameras_And_Display/display_set_gui_maximise.md`.
8. Admite además **desplazamiento X e Y**, útil en monitores ultraanchos.
9. **No necesitas recalcular coordenadas** al escalar: las funciones de tamaño se adaptan.
10. Las **UI layers** son más complejas y con carencias: mejor Draw GUI al principio.

---

## Ejercicio propuesto

> **Objetivo:** montar una interfaz que se mantenga anclada con cualquier tamaño de ventana
> y cualquier zoom de cámara.

**Parte A — Texto fijo**

1. Activa una cámara con zoom en tu room (por ejemplo 360 × 180 ampliada a la ventana).
2. Dibuja un texto en el **Draw normal** con coordenadas fijas del mundo. Comprueba que **se
   queda atrás** cuando el jugador se mueve.
3. Muévelo al evento **Draw GUI** con coordenadas (32, 32). Comprueba que ahora está **fijo
   en la esquina**.
4. Comprueba también que **no sale ampliado** por el zoom de la cámara.

**Parte B — Anclajes**

5. Ancla un elemento arriba a la izquierda con coordenadas fijas.
6. Intenta anclarlo **a la derecha** escribiendo a mano el ancho de tu ventana. Después
   **cambia el tamaño de la ventana** y comprueba que se descuadra.
7. Sustitúyelo por `display_get_gui_width() - 32` y comprueba que ahora **siempre** queda
   anclado, a cualquier resolución.
8. Haz lo mismo abajo con `display_get_gui_height()`.

**Parte C — Barra de vida**

9. Dibuja (o consigue) un sprite de corazón.
10. Con un bucle `for`, dibuja diez corazones en la esquina superior izquierda, espaciados.
11. Haz que el número de corazones dependa de una variable de vida del jugador.

**Parte D — Escalado**

12. Añade `display_set_gui_maximize(2, 2);` al mantener una tecla, y `display_set_gui_maximize(-1, -1)`
    al soltarla.
13. Comprueba que la interfaz crece **sin que tengas que recalcular ninguna coordenada**.
14. Añade un desplazamiento con los argumentos tercero y cuarto y observa el efecto.

**Reto extra:** compara `window_get_width()` con `display_get_gui_width()` **antes y
después** de escalar la GUI con `display_set_gui_maximize(2, 2)`. Muestra ambos valores en
pantalla y explica por qué dejan de coincidir.
