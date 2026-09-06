# 05 · Ratón y menús

> **Serie:** The Only GameMaker Tutorial You Need in 2026
> **Capítulo:** 5 de 12

| | |
|---|---|
| **Canal** | Sky LaRell Anderson |
| **Autor** | Dr. Skyler Lel Anderson |
| **URL** | <https://www.youtube.com/watch?v=tJ8bAGPiZRY> |
| **Duración** | 40 min 6 s |
| **Publicado** | 25 de enero de 2026 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `draw_rectangle`, `draw_text`, `draw_set_*`, `distance_to_point`, `mouse_check_button_pressed`, `instance_create_layer`, `with`, `other`, `instance_destroy` |

Capítulo fundamental: aprendemos a **dibujar** por código, a **detectar el ratón**, a
trabajar con **fuentes** y con **objetos padre e hijo**. Y en la sección avanzada
construimos un sistema de **fundido a negro** entre habitaciones.

## Índice de contenido

1. La room del título
2. El sprite del botón y las máscaras de colisión
3. El evento Draw y `draw_self()`
4. Dibujar el rectángulo del botón
5. Colores integrados y `draw_set_color()`
6. Detectar el ratón: `distance_to_point()`
7. Cadenas de texto y saltos de línea
8. Alinear el texto y crear una fuente
9. Hacer que el botón funcione: `mouse_check_button_pressed()`
10. Objetos padre e hijo: herencia
11. Práctica avanzada: fundido de salida (`oFadeOut`)
12. Práctica avanzada: fundido de entrada (`oFadeIn`)

---

## 1. La room del título

Crea una room nueva (`clic derecho → Create → Room`, o el atajo `Alt + R`) llamada
`rTitle`, de **480 × 270**, con la rejilla de instancias a **10 × 10**.

> Fíjate en el hábito del autor: **solo crea recursos de un tipo dentro del grupo de
> ese tipo**.

En el Creation Code de `rSplash`, apunta a `rTitle`. Al ejecutar verás una pantalla
negra: es nuestra room de título, todavía vacía.

Vamos a crear **dos botones**: uno que lleve al juego vista cenital y otro al
plataformas.

---

## 2. El sprite del botón y las máscaras de colisión

Crea **`sButton`** de **120 × 50**, relleno de color sólido, FPS 0, origen **Middle
Center**. Crea el objeto **`oButton`** y asígnale el sprite.

### La máscara de colisión

En el objeto verás el apartado **Collision Mask**, que por defecto dice *Same as
Sprite*.

> **Concepto clave:** `place_meeting()` no comprueba si el **arte** se solapa, sino si
> lo hacen las **máscaras de colisión**. Y las dos cosas pueden ser distintas.

Si abres el sprite puedes ver y editar su máscara: puede ser **toda la imagen**, un
rectángulo manual, o *automática*. Si en `oButton` cambias la opción a un sprite
concreto, la máscara será siempre esa aunque en código cambies el sprite del objeto.

> Siempre que tengas problemas de colisión, **revisa primero la máscara de colisión**.

Coloca el botón en el centro de la room. El centro horizontal de 480 es **240**:
muévelo hasta que la coordenada `x` de la parte inferior indique 240.

---

## 3. El evento Draw y `draw_self()`

Añade a `oButton` un evento **Draw → Draw**.

> **Cuidado:** en cuanto creas un evento Draw, este **sustituye** el dibujado por
> defecto. Si lo dejas vacío, **el sprite deja de verse**.

Para seguir dibujando el sprite asignado, llama explícitamente a:

```gml
draw_self();
```

En nuestro caso **no** la usaremos: el sprite solo sirve como **máscara de colisión**
y como guía visual de tamaño y posición en el editor.

### Orden de dibujado

El evento Draw funciona como el Step: **se ejecuta de arriba abajo**. Pero con una
diferencia crucial:

> **Todo lo que dibujes después queda ENCIMA de lo dibujado antes.**

Es la base para construir HUD e interfaces por capas. El autor lo demuestra moviendo
`draw_self()` al final del evento: el sprite tapa la esquina inferior derecha del
rectángulo blanco.

---

## 4. Dibujar el rectángulo del botón

`draw_rectangle()` necesita **cinco argumentos**: la esquina superior izquierda
(`x1`, `y1`), la esquina inferior derecha (`x2`, `y2`) y si queremos solo el contorno.

Como el origen del sprite es **Middle Center**, hay que calcular las esquinas a
partir del centro:

```gml
// --- Cosas del rectángulo del botón ---
var _w = sprite_width  / 2;   // Mitad del ancho del sprite
var _h = sprite_height / 2;   // Mitad del alto del sprite

var _x1 = x - _w;   // Esquina superior izquierda
var _y1 = y - _h;
var _x2 = x + _w;   // Esquina inferior derecha
var _y2 = y + _h;

draw_set_color(c_white);
draw_rectangle(_x1, _y1, _x2, _y2, true);   // true = solo contorno
```

`sprite_width` y `sprite_height` son **propiedades integradas** que devuelven las
dimensiones del sprite asignado al objeto.

> Para saber los argumentos de cualquier función, **pasa el ratón por encima** o haz
> **clic central** para abrir el manual completo con ejemplos.

---

## 5. Colores integrados y `draw_set_color()`

Los colores integrados (`c_white`, `c_black`, `c_red`…) son ideales para prototipar.
Haz clic central sobre `c_white` para ver **la lista completa**.

Para crear colores propios existen funciones como:

- `make_color_hsv(hue, saturation, value)`
- `make_color_rgb(red, green, blue)`
- `merge_color(color1, color2, amount)`

### Advertencia importante

```gml
draw_set_color(c_white);
```

> **Todo lo que se dibuje a partir de esta línea usará ese color.** Y los eventos Draw
> afectan **a todo el juego**: si no vuelves a fijar el color en otros objetos, sus
> formas saldrán blancas también.

Por eso la regla es: **fija siempre explícitamente cada ajuste antes de dibujar cada
cosa**.

---

## 6. Detectar el ratón: `distance_to_point()`

**En el Create de `oButton`:**

```gml
hover = false;   // ¿El ratón está encima del botón?
```

**En el Step:**

```gml
if (distance_to_point(mouse_x, mouse_y) <= 0)
{
    hover = true;    // Estamos encima
}
else
{
    hover = false;
}
```

`distance_to_point(x, y)` mide la distancia desde el **borde de la máscara de
colisión** hasta un punto:

- **0** → justo en el borde.
- **Negativo** → dentro.
- **Positivo** → fuera.

`mouse_x` y `mouse_y` son propiedades integradas: GameMaker **siempre** sabe dónde
está el ratón en la ventana del juego.

Ahora, en el Draw, sustituye el `true` fijo por la variable:

```gml
draw_rectangle(_x1, _y1, _x2, _y2, hover);
```

Resultado: **contorno** cuando el ratón está encima, **relleno** cuando no.

---

## 7. Cadenas de texto y saltos de línea

**En el Create**, añade una variable de tipo **string** (cadena):

```gml
text = "button text";
```

Un *string* guarda **caracteres de texto**, no números. Sin las comillas, GameMaker
buscaría una **variable** llamada `button`.

### Salto de línea dentro de una cadena

```gml
text = "button text\nhere";
```

La barra invertida seguida de `n` (**`\n`**) inserta un **salto de línea**. Ojo: es
la barra **invertida**, no la normal que usamos en las URLs.

**En el Draw, al final** (para que el texto quede encima del rectángulo):

```gml
// --- Cosas del texto ---
if (!hover)
{
    draw_set_color(c_black);   // Relleno: texto negro
}
else
{
    draw_set_color(c_white);   // Contorno: texto blanco
}

draw_text(x, y, text);
```

`draw_text()` toma tres argumentos: `x`, `y` y la cadena a dibujar.

---

## 8. Alinear el texto y crear una fuente

Por defecto el texto se dibuja alineado **arriba-izquierda** desde el punto dado.
Para centrarlo:

```gml
draw_set_halign(fa_center);   // Alineación horizontal
draw_set_valign(fa_middle);   // Alineación vertical
```

| Alineación | Opciones |
|---|---|
| Horizontal (`halign`) | `fa_left`, `fa_center`, `fa_right` |
| Vertical (`valign`) | `fa_top`, `fa_middle`, `fa_bottom` |

Es lo mismo que alinear texto en Word o Google Docs.

### Crear una fuente

1. Crea el grupo **`Fonts`**.
2. Clic derecho → **Create → Font** → llámala `fDefault`.
3. En el desplegable verás **todas las fuentes instaladas en tu ordenador**.

> Las fuentes son **archivos instalados en el sistema**. GameMaker consulta qué
> fuentes hay disponibles en tu máquina. Puedes descargar e instalar más.

El autor recomienda **Pixel Emulator**, una fuente pixel de muy baja resolución que
usa en su juego de Steam *Snapshot Spirit Live!*. Antes era de pago; tras el
fallecimiento de su creador, la familia la ofrece **gratis**. Aun así, él tiene
**la licencia descargada** para poder demostrar sus derechos de uso.

Ajustes recomendados para pixel art:

- **Tamaño 8** (esa fuente solo funciona bien a ciertos tamaños).
- **Anti-aliasing DESACTIVADO**: el anti-aliasing difumina los bordes, y en pixel art
  no lo queremos.

El autor recomienda el sitio web **font.com** para buscar fuentes y consultar sus
licencias (*100% free*, *free for personal use*, de pago…).

Finalmente, en el Draw:

```gml
draw_set_font(fDefault);
```

---

## 9. Hacer que el botón funcione

Las habitaciones también se pueden guardar en variables. **En el Create:**

```gml
where_to_go = rGame;   // El destino del botón
```

**En el Step, dentro del bloque de `hover`:**

```gml
if (distance_to_point(mouse_x, mouse_y) <= 0)
{
    hover = true;

    if (mouse_check_button_pressed(mb_any))
    {
        room_goto(where_to_go);
    }
}
else
{
    hover = false;
}
```

### Constantes de ratón

| Constante | Significado |
|---|---|
| `mb_left` | Botón izquierdo |
| `mb_right` | Botón derecho |
| `mb_middle` | Botón central |
| `mb_any` | **Cualquier** botón |

Igual que con el teclado, existe `mouse_check_button()` (mantenido) y
`mouse_check_button_pressed()` (solo el fotograma del clic).

> El autor prefiere **`mb_any`**: si alguien juega con un trackpad y hace clic
> derecho por error, el botón sigue respondiendo.

---

## 10. Objetos padre e hijo: herencia

Podrías duplicar el botón con `Ctrl + D` y cambiarle el destino… pero hay algo mejor.

> Un **objeto hijo** hereda **todo el código y las cualidades** de su padre, y puedes
> ajustar solo un par de cosas. Es la forma ideal de tener un sistema de botones por
> defecto y crear tantos botones como quieras como hijos.

### Cómo se hace

1. Borra el botón de la room.
2. Crea el objeto **`oButtonGame`** y en el apartado **Parent** elige `oButton`.
3. Verás que el código aparece **con un icono de candado**: es el código del padre, y
   **no se puede editar desde el hijo**.
4. **Asígnale el sprite `sButton`** (el evento Draw usa el sprite del hijo, así que lo
   necesita para saber el tamaño).
5. Arrastra `oButtonGame` a la room hasta `x = 240`.

Funciona exactamente igual: ha heredado todo.

### Override frente a Inherit

Si haces clic derecho sobre un evento heredado verás dos opciones:

| Opción | Qué hace |
|---|---|
| **Override Event** | **Ignora** el código del padre y usa solo lo que escribas |
| **Inherit Event** | Te da el código en blanco **más la llamada `event_inherited()`** |

`event_inherited()` **copia aquí el código del padre**, en el punto donde la pongas.
Como GameMaker ejecuta de arriba abajo:

- Escribe **antes** de `event_inherited()` → se ejecuta antes que el código del padre.
- Escribe **después** → **sobrescribes** lo que el padre haya hecho.

**Create event de `oButtonGame` (con Inherit Event):**

```gml
event_inherited();          // Todo lo que hace el padre

where_to_go = rGame;        // Redundante pero explícito
text = "top\ndown game";    // Cambiamos SOLO el texto
```

Ahora **duplica** `oButtonGame` con `Ctrl + D` como `oButtonPlatformer` y cambia:

```gml
event_inherited();

where_to_go = rPlatformer;
text = "platformer\ngame";
```

Arrástralo debajo del primero. Ya tienes un menú con dos botones funcionales que
comparten **una sola** implementación.

---

## 11. Práctica avanzada: fundido de salida (`oFadeOut`)

> Sección avanzada: si lo prefieres, mira y continúa con el siguiente capítulo.

En lugar de saltar en seco de una habitación a otra, haremos un **fundido a negro**.

### Preparar las capas

En **todas** las rooms visitables (`rGame`, `rPlatformer`, `rTitle`), añade una capa
de instancias llamada **`Fade`** y **arrástrala arriba del todo**, para que el fundido
tape todo lo demás. No hace falta en `rSplash`, porque de ahí se sale
instantáneamente.

### El objeto `oFadeOut`

**Create event:**

```gml
a = 0;                 // Alfa: 0 = invisible, 1 = completamente visible
rate = 0.025;          // Cuánto cambia la opacidad cada fotograma
target_room = noone;   // A qué room iremos (todavía sin asignar)
```

`noone` es la palabra clave para «una variable que guarda un recurso, pero sin
recurso asignado todavía».

**Step event:**

```gml
if (a < 1)
{
    a += rate;              // ¿Todavía no opaco? Sigue oscureciendo
}
else
{
    room_goto(target_room); // Ya opaco: cambia de room
}
```

**Draw event:**

```gml
draw_set_color(c_black);
draw_set_alpha(a);

// Rectángulo que cubre la room entera
draw_rectangle(0, 0, room_width, room_height, false);

draw_set_alpha(1);   // ¡IMPRESCINDIBLE!
```

> **⚠️ Advertencia crítica:** `draw_set_alpha()` afecta a **todo** el juego, igual que
> el color. Si te olvidas de devolverlo a **1**, **todo el juego se volverá
> invisible**. Siempre que manipules el alfa, **restablécelo a 1 al terminar**.

`room_width` y `room_height` son propiedades integradas con las dimensiones de la
room (480 y 270).

> El autor reconoce que este sistema es **poco elegante** (en sus juegos usa uno con
> scripts parametrizables), pero es **el más simple** de entender cuando empiezas.

### Crear el fundido desde el botón

Sustituye `room_goto(where_to_go)` en el Step de **`oButton`** (el padre) por:

```gml
// Solo lo creamos si no existe ya (así no se duplica al seguir haciendo clic)
if (!instance_exists(oFadeOut))
{
    var _fade = instance_create_layer(0, 0, "Fade", oFadeOut);

    with (_fade)
    {
        target_room = other.where_to_go;
    }
}
```

#### `instance_create_layer()`

```gml
instance_create_layer(x, y, "nombre_capa", objeto);
```

Es **la función para crear instancias por código**, y la usarás constantemente. Aquí
la posición da igual, porque el fundido cubre la room entera.

Devuelve el **id de la instancia** creada, que guardamos en `_fade` para poder
manipularla.

#### `with()` y `other`

```gml
with (_fade)
{
    target_room = other.where_to_go;
}
```

`with()` ejecuta el código **como si viniera del propio objeto indicado**. Por eso
podemos escribir `target_room` a secas, aunque esa variable pertenezca a `oFadeOut`.

Dentro de un bloque `with()`, la palabra **`other`** se refiere a **la instancia que
está ejecutando el código original** (nuestro botón). Por eso `other.where_to_go`
lee la variable del botón.

> Si escribieras `where_to_go` sin más dentro del `with()`, **el juego se cerraría de
> golpe**: `oFadeOut` no tiene esa variable declarada.

**Forma alternativa**, usando el punto para acceder a variables de una instancia:

```gml
var _fade = instance_create_layer(0, 0, "Fade", oFadeOut);
_fade.target_room = where_to_go;
```

El autor prefiere `with()` porque le resulta más claro, pero ambas son válidas.

---

## 12. Práctica avanzada: fundido de entrada (`oFadeIn`)

Duplica `oFadeOut` como **`oFadeIn`** y cámbialo:

**Create event:**

```gml
a = 1;          // Empieza opaco (pantalla en negro)
rate = 0.025;
// Ya no necesita target_room
```

**Step event:**

```gml
if (a > 0)
{
    a -= rate;          // ¿Todavía visible? Sigue aclarando
}
else
{
    instance_destroy(); // Ya invisible: destrúyete
}
```

**El Draw event se queda exactamente igual**, porque solo lee la variable `a`, que es
el Step quien la manipula.

`instance_destroy()` elimina la instancia que ejecuta el código. Junto con
`instance_create_layer()`, son las dos funciones de creación y destrucción que usarás
sin parar.

### Activar el fundido de entrada

En el **Creation Code de cada room** que visite el jugador:

```gml
instance_create_layer(0, 0, "Fade", oFadeIn);
```

Y listo: cada habitación se desvanece desde el negro al entrar, y se oscurece al
salir.

---

## Puntos clave

1. **`place_meeting()` comprueba la máscara de colisión, no el arte.** Revísala
   siempre ante problemas de colisión.
2. **Crear un evento Draw sustituye el dibujado por defecto.** Usa `draw_self()` si
   quieres conservar el sprite.
3. **En el Draw, lo último que dibujas queda encima.**
4. **`draw_set_color()` afecta a todo el juego.** Fija siempre los ajustes antes de
   dibujar cada cosa.
5. **`distance_to_point(mouse_x, mouse_y) <= 0`** → el ratón está encima (0 = borde,
   negativo = dentro).
6. **`\n`** inserta un salto de línea en una cadena; **las comillas** hacen que sea
   texto y no una variable.
7. **`draw_set_halign(fa_center)` + `draw_set_valign(fa_middle)`** centran el texto.
8. **Las fuentes son archivos instalados en tu ordenador.** Desactiva el
   anti-aliasing para pixel art y **comprueba siempre la licencia**.
9. **`mouse_check_button_pressed(mb_any)`** detecta el clic; `mb_any` perdona clics
   con el botón «equivocado».
10. **Los objetos hijo heredan todo del padre.** Con `event_inherited()` puedes
    ejecutar antes o después del código heredado.
11. **`instance_create_layer(x, y, "capa", objeto)`** crea instancias y devuelve su
    id. **`instance_destroy()`** las elimina.
12. **`with()`** ejecuta código como si viniera de otro objeto; **`other`** es la
    instancia que llama.
13. **`draw_set_alpha()` es peligroso**: si no lo devuelves a 1, **todo el juego se
    vuelve invisible**.

---

## Ejercicio propuesto

> **Objetivo:** construir un menú completo con botones reutilizables mediante
> herencia, y rematarlo con fundidos.

**Parte A — Un botón funcional**

1. Crea `rTitle` (480 × 270, rejilla 10 × 10) y apunta `rSplash` a ella.
2. Crea `sButton` (120 × 50, origen **Middle Center**) y `oButton`.
3. Coloca el botón en `x = 240`. **Antes de seguir**, abre `sButton` y cambia su
   máscara de colisión a mano; comprueba cómo cambia la zona sensible al ratón.
   Vuelve a dejarla en *automática*.
4. Añade el evento **Draw** y dibuja el rectángulo con las cuatro esquinas
   calculadas desde `sprite_width` / `sprite_height`.
5. Añade `hover = false` al Create y la detección con `distance_to_point()` en el
   Step. El rectángulo debe ser **contorno** con el ratón encima y **relleno** si no.
6. Añade `text = "button text\nhere"` y dibújalo con el color cambiando según
   `hover`.
7. Centra el texto con `draw_set_halign(fa_center)` y `draw_set_valign(fa_middle)`.

**Parte B — Fuentes**

8. Crea el grupo `Fonts` y una fuente `fDefault`. Prueba al menos tres tipografías
   instaladas en tu Mac y elige una. Desactiva el anti-aliasing.
9. Aplica la fuente con `draw_set_font(fDefault)`.

**Parte C — Herencia**

10. Añade `where_to_go = rGame` al Create de `oButton` y el clic con
    `mouse_check_button_pressed(mb_any)`.
11. Crea `oButtonGame` como **hijo** de `oButton`, con **Inherit Event** en el Create,
    y cambia solo `text` y `where_to_go`.
12. Duplícalo como `oButtonPlatformer`. Coloca ambos en la room, uno bajo el otro.
13. Comprueba que cada uno lleva a su habitación.

**Parte D — Fundidos (avanzado)**

14. Añade la capa `Fade` **arriba del todo** en `rTitle`, `rGame` y `rPlatformer`.
15. Crea `oFadeOut` con `a`, `rate` y `target_room`; su Step oscurece y luego salta de
    room; su Draw pinta un rectángulo negro del tamaño de la room **y devuelve el alfa
    a 1**.
16. Sustituye el `room_goto()` del botón por la creación de `oFadeOut` con
    `instance_create_layer()` y `with()` + `other`.
17. **Comprueba el error a propósito:** escribe `where_to_go` sin `other.` dentro del
    `with()` y observa cómo el juego se cierra. Arréglalo.
18. Crea `oFadeIn` (duplicando), con `a = 1` y `instance_destroy()` al terminar.
19. Añade `instance_create_layer(0, 0, "Fade", oFadeIn);` al Creation Code de las tres
    rooms.

**Reto extra:** comenta la línea `draw_set_alpha(1);` del Draw de `oFadeOut` y
ejecuta el juego. Describe con tus palabras qué ves y por qué. Es la forma más rápida
de entender por qué esa línea no es opcional.
