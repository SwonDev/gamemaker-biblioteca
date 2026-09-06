# 42 · Cámaras y resolución II — intermedio (la cámara por código)

> **Serie:** GameMaker — Cameras & Resolution 2026 (PixelatedPope)
> **Vídeo:** 2 de 4 · Nivel **intermedio**

| | |
|---|---|
| **Canal** | PixelatedPope |
| **URL** | <https://www.youtube.com/watch?v=Bbxa7MVKipo> |
| **Duración** | 26 min 0 s |
| **Publicado** | 13 de diciembre de 2025 |
| **Nivel** | Intermedio |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | `view_enabled`, `view_visible`, `view_camera`, `camera_set_view_size`, `camera_set_view_target`, `camera_set_view_pos`, `camera_get_view_*`, `window_set_size`, `surface_resize`, `display_set_gui_size`, `display_get_width/height`, `lerp`, `clamp`, `frac`, `floor` |

El capítulo más importante de la serie. Aquí se construye **el sistema de cámara que
usarás en casi cualquier proyecto real**, y de paso se explica **cómo renderiza GameMaker
por dentro**: los cuatro elementos que de verdad importan.

El punto de partida es una crítica honesta al sistema del capítulo anterior:

> «En el vídeo anterior configuramos la ventana y la cámara del juego usando los ajustes
> de view en el inspector de la room. Y aunque eso sin duda hace el trabajo, **está muy lejos
> de ser la solución perfecta.**»

## Índice de contenido

1. Cuatro problemas del sistema de la parte 1
2. Problema 4 en detalle: el *temblor* de subpíxel
3. Cómo renderiza GameMaker: los cuatro elementos que importan
4. La room de inicialización y el objeto cámara persistente
5. La resolución base: por qué no partir del tamaño de la ventana
6. Calcular el tamaño de la ventana que cabe en el monitor
7. La trampa de la barra de título y `frac()`
8. Superficie de aplicación: rejilla estricta frente a subpíxeles
9. El tamaño de la GUI
10. Evento Room Start: activar el view por código
11. Por qué `camera_set_view_target(noone)` es obligatorio
12. Evento End Step: centrar la cámara en el jugador
13. Suavizado con `lerp()`
14. Mantener la cámara dentro de la room con `clamp()`
15. Depurar con `display_write_all_specs`
16. Los dos scripts para cuando activas subpíxeles

---

## 1. Cuatro problemas del sistema de la parte 1

### Problema 1 — Es tedioso

> «Soy vago y no quiero tener que hacer esto cada vez que creo una room.»

Hay que abrir los ajustes de view, marcar las mismas casillas y meter los mismos números
en **cada room**. Y si decides cambiar el tamaño de la cámara, toca recorrer **todas** las
rooms actualizando ajustes.

Un sistema ideal permitiría **no volver a entrar nunca** en esos ajustes.

### Problema 2 — Siempre clavado al objetivo

El ajuste *object following* es muy rígido. Aunque le des algo de borde, sigue
persiguiendo de forma brusca cuando el objeto sale de él.

> «Hoy en día es **muy raro** tener una cámara tan tiesa en un juego 2D.»

### Problema 3 — Encerrado en la room

Con *object following*, **la cámara no puede salir de la room. No es posible.** Si haces
un *infinite runner* o un simulador espacial, directamente no puedes usarlo: la cámara
acabará chocando con el borde de la room, por muy grande que la hagas.

### Problema 4 — El temblor de subpíxel

Este es el más complicado, y el más difícil de diagnosticar si no lo conoces.

Imagina un objeto de **un solo píxel** en una room con una rejilla de píxeles de fondo:
cada cuadrado es un píxel del juego. La cámara mide **5 × 5** y el viewport está a
**1000 × 1000**. GameMaker lo ha escalado todo: cada píxel del juego se dibuja como un
cuadrado de **200 × 200** en la ventana.

Eso significa que, a velocidades muy bajas, **se nota la diferencia** entre una X de
`128`, `128.1` o `128.2`.

Y aquí viene lo interesante: la cámara está configurada para seguir ese píxel **sin
borde**, así que esperarías que lo mantuviera perfectamente centrado.

> «Pero eso **no está pasando**. Eso es porque **la posición de la cámara, al usar object
> following, se bloquea automáticamente a un número entero**. Así que hasta que mi objeto
> no se ha movido un número entero, no lo sigue.»

Al mantener pulsada la flecha derecha, **la cámara parece dar saltos para alcanzarte**.

> «Obviamente he exagerado este problema para demostrarlo, pero es **muy probable** que
> ocurra en tu juego si tu ventana es más grande que tu cámara, y lo notarás tú y lo
> notará el jugador.»

La solución más fácil: **no usar object following** y controlar la cámara por código,
donde la posición no está limitada a enteros.

---

## 2. Cómo renderiza GameMaker: los cuatro elementos que importan

> «Lo he etiquetado como intermedio, y para mí eso significa que podemos meternos en
> material técnico.»

### La cadena completa

```
   ROOM
     └── VIEWPORT (hay 8; usaremos solo 1, el 0)
              └── CÁMARA  (no la tocaremos directamente)
                       └── VIEW  ← el importante
                                └── APPLICATION SURFACE
                                             └── WINDOW
                                                  └── GUI
```

**La room.** Contiene ocho viewports, pero solo usaremos uno.

**El viewport.** Tiene una cámara asignada por defecto, así que **no necesitas crear ni
asignar cámaras** en la mayoría de los casos.

> «Pero **la cámara en sí no es realmente importante**. No vamos a hacer nada con ella
> directamente. Lo importante es **el view que hay dentro de la cámara.**»

**El view.** Controla **el área de tu room que el jugador puede ver**. Mover el view cambia
hacia dónde mira la cámara; redimensionarlo **cambia el zoom**. Todo lo que el view ve se
dibuja en la **application surface**.

**La application surface.** «Hablararemos más de este tipo en detalle luego. **Es súper
importante.**»

**La window.** Mientras el juego corre **siempre hay una ventana**. Incluso en pantalla
completa, sigues estando en una ventana del tamaño de la pantalla. Por defecto, GameMaker
dibuja la application surface **escalada proporcionalmente para que quepa en la ventana**.

> Si la application surface y la ventana **no comparten relación de aspecto**, eso da como
> resultado **barras negras**.

**La GUI.** GameMaker dibuja todo lo de tus eventos GUI **estirado** para que encaje en
las dimensiones de la application surface. Si tu GUI no está bien dimensionada, **se
aplasta y se estira**.

### La conclusión práctica

> «Cuando hablemos de configurar todo esto por código, **solo nos vamos a ocupar de cuatro
> cosas**: la ventana, la application surface, el view y la GUI.»

Y aquí está la clave que explica por qué es tan confuso traducir lo de la parte 1 a
código:

> «**No vamos a usar ninguna función que trate con viewports.** Así que probablemente
> entiendas por qué traducir lo que hicimos en los ajustes de la room a código es
> *extra* confuso.»

Lo que hacías en **viewport properties** se convierte en **window + application surface**.
Lo que hacías en **camera properties** y **object following** se convierte en **view**.

> **Nota:** todo se complica si intentas pantalla dividida con varios viewports activos.
> Eso daría para su propio vídeo. Lo de aquí es para juegos **sin pantalla dividida**, con
> **un solo viewport visible**.

---

## 3. La room de inicialización y el objeto cámara persistente

Primer paso: añadir una room nueva.

> «Siempre tengo **una room de inicialización** que sirve de lugar para crear objetos
> controlador persistentes y dejar el juego listo para jugar.»

Se llama `room_init` y se marca como **room de arranque**. Nada de esa room importa salvo
una cosa:

> «El tamaño de la room determinará **el tamaño inicial de la ventana**, que debería estar
> en pantalla solo una fracción de segundo. Yo suelo ponerlo bastante pequeño. Vamos a
> usar **100 × 100** por ahora.```

Después creamos el objeto controlador persistente: **`obj_camera`**, marcado como
**persistente** y colocado en la room de inicialización.

> «Este objeto va a ser responsable de hacer todo lo que hacíamos en los ajustes de la
> room, y más.»

---

## 4. La resolución base: por qué no partir del tamaño de la ventana

En la parte 1 empezamos por fijar el tamaño de la ventana y derivar de ahí el view. Aquí
el autor **invierte el orden**, y la razón es de peso:

> «El tamaño de la ventana de tu juego **puede cambiar**. Incluso solo alternar entre
> pantalla completa y modo ventana cambia el tamaño de tu ventana. Y dar al jugador la
> opción de elegir una escala de ventana es **súper común**. Así que basar la resolución
> de tu juego en algo que cambia tan fácilmente **no es una gran idea**.»

En su lugar, se parte de **la resolución de monitor y televisor más común: 1920 × 1080**.

```gml
// Create event de obj_camera
// ─────────────────────────────────────────────────────────────
// Resolución base: partimos de 1920x1080 y dividimos por un
// número entero. El resultado es el tamaño que usaremos para
// diseñar el juego entero (rooms, arte, enemigos...).
// ─────────────────────────────────────────────────────────────
base_width  = 1920 / 6;   // = 320
base_height = 1080 / 6;   // = 180
```

> «Si tu juego es pixel art, divídelo por un **número entero**: 2, 3, 4, etc. **Diseñarás
> tu juego basándote en este resultado.**»

Y una advertencia de producción importante:

> «Puedes cambiarlo más adelante, pero querrás **fijarlo bastante pronto**, porque
> cambiarlo al final del desarrollo puede tener consecuencias.»

El arte del proyecto de ejemplo es pixel art muy pequeño, así que divide entre 6 y
obtiene **320 × 180**: exactamente la resolución del curso principal.

---

## 5. Calcular el tamaño de la ventana que cabe en el monitor

De momento asumimos que **no** arrancas en pantalla completa. Hay dos cosas que hay que
tener en cuenta:

1. La ventana debe tener **la misma relación de aspecto** que el view, para evitar barras
   negras.
2. La ventana debe **caber en el monitor actual**. Si la ventana más la barra de título es
   demasiado ancha o alta para la resolución del monitor, Windows la aplastará.

Para lo primero, convertimos el tamaño de la ventana en **un escalar** que multiplica
nuestro tamaño base. Para lo segundo, necesitamos saber cuánto cabe.

```gml
// Create event de obj_camera (continuación)
// ─────────────────────────────────────────────────────────────
// ¿Cuántas veces cabe nuestra altura base en la altura del
// monitor? Lo mismo para la anchura.
// ─────────────────────────────────────────────────────────────
var _max_height_scale = display_get_height() / base_height;
var _max_width_scale  = display_get_width()  / base_width;
```

---

## 6. La trampa de la barra de título y `frac()`

Aquí está el detalle que casi todo el mundo pasa por alto:

> «Si la escala de ventana que hemos calculado es **un número entero**, eso significa que
> la altura base escala perfectamente a la resolución vertical del monitor. Y si ponemos
> nuestra ventana a esa altura, **no estamos teniendo en cuenta la barra de título**. Y
> Windows se va a enfadar.»

La solución es detectar ese caso con **`frac()`**, que devuelve **lo que hay después del
punto decimal**. Si devuelve `0`, el número era entero y hay que bajar un escalón.

```gml
// ─────────────────────────────────────────────────────────────
// Si la escala de altura es un número entero, la ventana ocuparía
// exactamente toda la altura del monitor y NO dejaría sitio a la
// barra de título. Windows la aplastaría. Le restamos 1.
// ─────────────────────────────────────────────────────────────
if (frac(_max_height_scale) == 0)
{
    _max_height_scale -= 1;
}
```

> «No necesitamos preocuparnos de lo mismo para la anchura. En la mayoría de los casos, el
> ancho de la ventana puede llegar hasta el ancho exacto de tu pantalla.```

Después elegimos **el menor** de los dos valores, y si el juego es pixel art lo
redondeamos hacia abajo para garantizar enteros.

```gml
// ─────────────────────────────────────────────────────────────
// Nos quedamos con la escala más restrictiva de las dos.
// ─────────────────────────────────────────────────────────────
window_scale = min(_max_width_scale, _max_height_scale);

// En pixel art queremos multiplicadores ENTEROS: 1x, 2x, 3x...
window_scale = floor(window_scale);

// Y por fin fijamos el tamaño de la ventana.
window_set_size(base_width * window_scale, base_height * window_scale);
```

---

## 7. Superficie de aplicación: rejilla estricta frente a subpíxeles

Este es el bloque que el autor recomienda **probar de las dos formas**:

```gml
// ─────────────────────────────────────────────────────────────
// OPCIÓN A — rejilla de píxel estricta.
// Todo se dibuja a la resolución base y luego se escala.
// Los píxeles encajan perfectamente entre sí, como en una
// videoconsola antigua.
// ─────────────────────────────────────────────────────────────
surface_resize(application_surface, base_width, base_height);

// ─────────────────────────────────────────────────────────────
// OPCIÓN B — subpíxeles activados.
// La superficie de aplicación se renderiza a la resolución de la
// ventana, así que el desplazamiento, el escalado y la rotación
// son mucho más suaves. El juego se renderiza a MÁS resolución.
// ─────────────────────────────────────────────────────────────
surface_resize(application_surface,
               base_width  * window_scale,
               base_height * window_scale);
```

> «Vamos a escribir la línea siguiente **dos veces** y comentar una cada vez, para que
> puedas experimentar y ver cuál te gusta más para tu juego.»

La comparación honesta del autor:

| | Ventaja | Inconveniente |
|---|---|---|
| **Rejilla estricta** | Píxeles perfectos, estética retro impecable | El movimiento puede verse a saltos |
| **Subpíxeles** | Desplaza, escala y rota con mucha suavidad | Se renderiza a más resolución; pueden aparecer artefactos |

> «Es **puramente preferencia personal** para tu proyecto, y ambos tienen pros y contras.»

---

## 8. El tamaño de la GUI

```gml
// ─────────────────────────────────────────────────────────────
// La GUI se estira para encajar en la superficie de aplicación.
// Si no le damos un tamaño con la misma relación de aspecto,
// se verá deformada.
// ─────────────────────────────────────────────────────────────
display_set_gui_size(base_width, base_height);
```

> «No me voy a meter mucho en cómo funciona la capa GUI en este vídeo, pero al menos
> necesitamos fijar su tamaño para que, cuando empieces a usarla, **no esté estirada ni
> distorsionada**.»

Como casi todo aquí, se reduce a darle **un tamaño que comparta relación de aspecto** con
el view y la application surface.

---

## 9. Evento Room Start: activar el view por código

Lo último que hace el Create es saltar a la room real del juego:

```gml
// Create event de obj_camera (final)
// ─────────────────────────────────────────────────────────────
// Solo lo pongo aquí porque no tengo un objeto gestor de juego
// más veterano que controle este tipo de cosas. Probablemente
// NO debería ser responsabilidad de tu objeto cámara.
// ─────────────────────────────────────────────────────────────
room_goto(rm_game);
```

Y ahora el **Room Start**, que sustituye las dos casillas que marcamos en la parte 1:

```gml
// Room Start event de obj_camera
// ─────────────────────────────────────────────────────────────
// Equivale a marcar "Enable Viewports" en el inspector.
view_enabled = true;

// Equivale a marcar "Visible" dentro del grupo Viewport 0.
view_visible[0] = true;

// Si el view está activo y visible, debería tener el tamaño
// correcto. view_camera nos da acceso a la cámara asignada a un
// viewport concreto. Como no hacemos pantalla dividida, SIEMPRE
// usaremos view_camera[0].
camera_set_view_size(view_camera[0], base_width, base_height);
```

---

## 10. Por qué `camera_set_view_target(noone)` es obligatorio

Esta línea **no es técnicamente necesaria**, pero evita un error muy común:

```gml
// ─────────────────────────────────────────────────────────────
// Si ya tenías rooms configuradas con "object following" en el
// inspector, lo resetamos por código para que no tengas que ir
// room por room desactivándolo a mano.
// ─────────────────────────────────────────────────────────────
camera_set_view_target(view_camera[0], noone);
```

> «Si mantienes el objetivo de *object following* puesto en los ajustes de la room e
> intentas posicionar tu cámara a mano por código, como vamos a hacer, **puedes causar
> problemas bastante raros**. **Asegúrate de no saltarte este paso.**```

También conviene **resetear los ajustes del viewport** a sus valores por defecto:

```gml
// ─────────────────────────────────────────────────────────────
// Si habías tocado la posición o el tamaño del viewport en el
// inspector (sobre todo si lo pusiste a 0x0), nada funcionará
// bien. Lo reseteamos. Fuera de preparar pantalla dividida, esta
// es la única vez que tocaremos el viewport.
// ─────────────────────────────────────────────────────────────
view_xport[0]      = 0;
view_yport[0]      = 0;
view_wport[0]      = window_get_width();
view_hport[0]      = window_get_height();
```

---

## 11. Evento End Step: centrar la cámara en el jugador

¿Por qué **End Step** y no Step?

> «Porque asumimos que el objeto al que tu cámara quiere seguir **está actualizando su
> posición en el evento Step**. Definitivamente no queremos que la cámara se coloque para
> mirar a un objeto y que luego ese objeto se mueva.»

Primero, no podemos seguir a un jugador que no existe:

```gml
// End Step event de obj_camera
// ─────────────────────────────────────────────────────────────
// No podemos seguir al jugador si el jugador no existe.
if (!instance_exists(obj_player)) exit;
```

El intento ingenuo falla, y es **el error número uno** al empezar con cámaras por código:

```gml
// ─────────────────────────────────────────────────────────────
// ¡ESTO NO FUNCIONA! camera_set_view_pos NO recibe el
// CENTRO del view: recibe la esquina SUPERIOR IZQUIERDA.
// ─────────────────────────────────────────────────────────────
camera_set_view_pos(view_camera[0], obj_player.x, obj_player.y);
```

> «Oh, claro. Desafortunadamente es un poco más complicado que eso. Cuando usas
> `camera_set_view_pos`, **no estamos fijando la posición del view a partir de su
> centro, sino de su esquina superior izquierda.**»

Así que hay que hacer un poco de matemáticas. Y ojo con qué dimensiones usar:

```gml
// ─────────────────────────────────────────────────────────────
// No queremos usar base_width / base_height aquí: SIEMPRE las
// dimensiones ACTUALES del view. Es más importante si añades
// zoom, pero sigue siendo una buena práctica.
// ─────────────────────────────────────────────────────────────
var _view_width  = camera_get_view_width(view_camera[0]);
var _view_height = camera_get_view_height(view_camera[0]);

// Restamos la mitad del ancho y la mitad del alto para obtener
// la esquina superior izquierda que centra al jugador.
var _target_x = obj_player.x - (_view_width  / 2);
var _target_y = obj_player.y - (_view_height / 2);

camera_set_view_pos(view_camera[0], _target_x, _target_y);
```

Con esto, el jugador queda **perfectamente centrado**.

---

## 12. Suavizado con `lerp()`

Pero, ¿no se estaba quejando el autor de que *object following* dejaba la cámara clavada?
Sí. Y conviene arreglarlo… salvo en un caso:

> «Hay situaciones en las que dejarlo así **tiene sentido**. Si tu juego usa **puntería con
> ratón**, una cámara suave significa que la puntería del jugador puede cambiar incluso
> cuando no mueve el ratón ni el personaje. **El movimiento de la cámara por sí solo altera
> su puntería**, lo cual puede ser molesto.»

Para suavizar, **`lerp()`**:

> «Si no conoces `lerp`, tiene un montón de usos increíbles y probablemente es **una de mis
> funciones integradas favoritas** de GameMaker. La vamos a usar hoy para mover un valor
> hacia un valor objetivo **en un porcentaje de la distancia restante cada step**.»

```gml
// ─────────────────────────────────────────────────────────────
// Posición ACTUAL de la cámara.
var _current_x = camera_get_view_x(view_camera[0]);
var _current_y = camera_get_view_y(view_camera[0]);

// Nos movemos un 20% de la distancia restante cada step.
var _final_x = lerp(_current_x, _target_x, 0.2);
var _final_y = lerp(_current_y, _target_y, 0.2);

camera_set_view_pos(view_camera[0], _final_x, _final_y);
```

### Qué hace exactamente ese 0,2

Imagina una línea: la posición actual a la izquierda (**200**) y la objetivo a la derecha
(**250**). Pides a `lerp` el valor que está **al 20 %** del camino: **210**.

- La cámara se mueve de 200 a 210 este step: **10 píxeles** a la derecha.
- Pero conforme se acerca, **la distancia que recorre cada step se hace más y más
  pequeña**, así que la cámara **parece frenar gradualmente** al acercarse.

> «Es un efecto muy bonito que verás en muchísimos juegos.»

---

## 13. Mantener la cámara dentro de la room con `clamp()`

Último paso. De nuevo, hay casos donde no lo querrás, pero **lo normal es quererlo**.

```gml
// ─────────────────────────────────────────────────────────────
// clamp() restringe un número a un rango.
// ─────────────────────────────────────────────────────────────
_target_x = clamp(_target_x, 0, room_width  - _view_width);
_target_y = clamp(_target_y, 0, room_height - _view_height);
```

El razonamiento paso a paso del autor es instructivo, porque comete el mismo error dos
veces a propósito:

1. El límite inferior es **0** (una posición de view menor que 0 está fuera de la room, a
   la izquierda).
2. El límite superior… en principio **el ancho de la room**. Funciona en el borde
   izquierdo, pero al llegar al derecho se sale.
3. Claro: `_target_x` es **la esquina superior izquierda** del view. Hay que **restar el
   ancho del view** al ancho de la room para que el borde derecho no se salga.

El código completo y ordenado del End Step queda así:

```gml
// ══════════════════════════════════════════════════════════════
// End Step event de obj_camera — VERSIÓN COMPLETA
// ══════════════════════════════════════════════════════════════

// 1. Sin jugador no hay cámara.
if (!instance_exists(obj_player)) exit;

// 2. Dimensiones ACTUALES del view (no las de la resolución base).
var _view_width  = camera_get_view_width(view_camera[0]);
var _view_height = camera_get_view_height(view_camera[0]);

// 3. Esquina superior izquierda que centraría al jugador.
var _target_x = obj_player.x - (_view_width  / 2);
var _target_y = obj_player.y - (_view_height / 2);

// 4. Suavizado: 20% de la distancia restante cada step.
_target_x = lerp(camera_get_view_x(view_camera[0]), _target_x, 0.2);
_target_y = lerp(camera_get_view_y(view_camera[0]), _target_y, 0.2);

// 5. La cámara no sale de la room. Restamos el tamaño del view
//    porque trabajamos con la esquina superior izquierda.
_target_x = clamp(_target_x, 0, room_width  - _view_width);
_target_y = clamp(_target_y, 0, room_height - _view_height);

// 6. Aplicamos.
camera_set_view_pos(view_camera[0], _target_x, _target_y);
```

> «Y ahí lo tienes. La cámara sigue al jugador suavemente, está encerrada en la room y
> todo está escalado perfectamente y se ve nítido.```

---

## 14. Depurar con `display_write_all_specs`

> «A estas alturas es posible que, mientras metías tus propios números y experimentabas, te
> hayas encontrado con **problemas raros de renderizado**. Puede que tu juego no escale
> bien, que las cosas se distorsionen, que **hileras de píxeles se dupliquen o
> desaparezcan**, algo va mal y no sabes qué.»

Si preguntaras en el servidor de Discord de GameMaker, el autor te lanzaría este script:

```gml
// Draw GUI event de obj_camera
display_write_all_specs();
```

Al ejecutar aparece un montón de información: **para cada fila ves el elemento, su relación
de aspecto y cuánto se está escalando respecto a su elemento padre.**

### Cómo leerlo

El autor hace la demostración cambiando el tamaño base a **300 × 200** a propósito:

```
monitor    1920 x 1080   aspect 1,78
window      ...          aspect 1,5
app surface ...          aspect 1,5
view        ...          aspect 1,5
gui         ...          aspect 1,5
```

> «Solo con mirar esos números sé que **voy a tener barras negras en pantalla completa**,
> porque la pantalla y la app surface **no comparten relación de aspecto**. Pero como todo
> lo que va de la ventana hacia abajo **sí** la comparte, y no estoy en pantalla completa,
> todo se renderiza perfectamente.```

Y la regla de oro para pixel art:

> «Si tu juego usa pixel art, **esos valores de escala deberían ser todos números enteros**.»

El autor recomienda dejar esta información visible en pantalla durante el desarrollo:

> «Si tienes problemas y lo que cubro en esta serie no te ayuda a entenderlos y resolverlos,
> **tener esa información disponible cuando preguntes en el Discord va a ayudar mucho**.»

---

## 15. Los dos scripts para cuando activas subpíxeles

### Líneas negras entre tiles

> «A veces verás un problema extraño en el que parecen aparecer **como líneas negras entre
> tiles** o en el borde de sprites que no deberían estar ahí. Suele pasar mientras la cámara
> se mueve.»

La solución del autor es sustituir **todos** los usos de `camera_set_view_pos` por su
script `camera_set_view_pos_subpixel`. Se usa exactamente igual:

```gml
// Antes:
camera_set_view_pos(view_camera[0], _target_x, _target_y);

// Después (si ves líneas negras entre tiles):
camera_set_view_pos_subpixel(view_camera[0], _target_x, _target_y);
```

> «No puedo garantizar que resuelva todos estos problemas, pero he visto que ayuda.»

### Objetos que tiemblan en posiciones decimales

El segundo problema: objetos dejados en **posiciones no enteras** que parecen «moverese y
temblar un poquito» al arrastrar el view.

Para eso existe `draw_self_extended_subpixel`.

- `draw_self_extended` es una versión de `draw_sprite_ext` con **todos los argumentos ya
  rellenados** con las variables integradas correspondientes: `sprite_index`,
  `image_index`, `x`, `y`, etc.
- La variante `_subpixel` **añade matemáticas basadas en la escala del view a la
  superficie de aplicación** y **redondea la posición de dibujado**.

> «Eso deja menos en manos de los dioses de la aritmética en coma flotante y te da una
> imagen más coherente mientras la cámara se mueve.```

Ambos scripts están en el repositorio *helpful scripts* del autor en GitHub.

---

## 16. Qué experimentar antes de pasar al capítulo siguiente

El autor cierra con una lista de pruebas concretas:

1. Cambia el **0,2** del `lerp`. ¿Qué pasa con **0,1**? ¿Y con **0,5**? ¿Y con **1**?
2. Vuelve al Create y prueba a dividir 1920 y 1080 por **otros números**.
3. Si tu juego **no** es pixel art, prueba con números **no enteros**.
4. Alterna las dos líneas de `surface_resize` y compara.

---

## Puntos clave

1. El sistema del inspector tiene **cuatro problemas**: tedio, seguimiento rígido,
   imposibilidad de salir de la room y **temblor de subpíxel**.
2. El temblor de subpíxel ocurre porque **object following bloquea la posición de la
   cámara a números enteros**.
3. Solo importan **cuatro elementos**: **ventana**, **application surface**, **view** y
   **GUI**. Las funciones de *viewport* casi no se usan.
4. La **room de inicialización** fija el tamaño inicial de la ventana; suele ser pequeña
   (100 × 100).
5. La **resolución base** se deriva de **1920 × 1080 dividido entre un entero**, no del
   tamaño de la ventana, porque **la ventana cambia**.
6. Usa **`frac()`** para detectar si la escala es entera y **restar 1** para dejar sitio a
   la barra de título.
7. `surface_resize` tiene **dos modos**: rejilla estricta o subpíxeles. Es preferencia
   personal.
8. `view_enabled = true` y `view_visible[0] = true` sustituyen a las dos casillas del
   inspector.
9. **`camera_set_view_target(view_camera[0], noone)` es obligatorio** si alguna room tiene
   *object following* configurado.
10. El seguimiento va en el **End Step**, nunca en el Step.
11. `camera_set_view_pos()` recibe la **esquina superior izquierda**, no el centro:
    hay que restar la mitad del view.
12. Usa las dimensiones **actuales** del view, no las de la resolución base.
13. `lerp(actual, objetivo, 0.2)` produce el frenado progresivo característico.
14. `clamp()` necesita **`room_width - view_width`** como límite superior, no
    `room_width`.
15. `display_write_all_specs()` es la herramienta de diagnóstico: **todos los valores de
    escala deberían ser enteros** en pixel art.

---

## Ejercicio propuesto

> **Objetivo:** montar el sistema completo de cámara por código y comprobar cada decisión
> con `display_write_all_specs`.

1. Crea una **room de inicialización** de 100 × 100, márcala como room de arranque y
   coloca en ella un objeto `obj_camera` **persistente**.
2. En el **Create** de `obj_camera`, define `base_width = 1920 / 6` y
   `base_height = 1080 / 6`. Comprueba que valen **320** y **180**.
3. Calcula `_max_height_scale` y `_max_width_scale` con `display_get_height()` y
   `display_get_width()`. Imprime ambos valores con `show_debug_message`.
4. Añade la comprobación de `frac()`. **Antes** de añadirla, fija a mano la ventana a la
   altura completa del monitor y describe qué hace Windows con ella.
5. Calcula `window_scale` con `min()` y `floor()`, y aplica `window_set_size()`.
6. Escribe las dos versiones de `surface_resize`, deja activa la primera y ejecuta.
7. Añade `display_set_gui_size(base_width, base_height)` y `room_goto(rm_game)`.

**Parte de la cámara**

8. En el **Room Start**, activa `view_enabled`, `view_visible[0]` y fija el tamaño del view
   con `camera_set_view_size`.
9. Añade `camera_set_view_target(view_camera[0], noone)`. Para comprobar por qué importa:
   **ve al inspector de la room, asigna un objeto a object following y ejecuta**. Describe
   el comportamiento errático. Después quita la línea de código y vuelve a probar.
10. En el **End Step**, empieza solo con
    `camera_set_view_pos(view_camera[0], obj_player.x, obj_player.y)`. Ejecuta y
    explica **dónde** acaba el jugador en pantalla y por qué.
11. Corrígelo restando la mitad del view. Comprueba que queda centrado.
12. Añade el `lerp` con `0.2`. Prueba después con `0.05`, `0.5` y `1`. Anota qué sensación
    da cada uno y en qué caso **dejarías la cámara clavada** a propósito.
13. Añade el `clamp` **primero con `room_width` a secas**. Comprueba que el borde derecho
    falla. Corrígelo restando el ancho del view.

**Parte de diagnóstico**

14. Añade `display_write_all_specs()` en el Draw GUI. Comprueba que **todos** los valores
    de escala son enteros.
15. Cambia el tamaño base a **300 × 200** y ejecuta. Anota qué elementos comparten relación
    de aspecto y cuáles no, y predice **dónde** verás barras negras antes de poner el juego
    en pantalla completa.
16. Activa la versión de **subpíxeles** del `surface_resize` y busca líneas negras entre
    tiles mientras la cámara se mueve. Si las ves, investiga cómo aplicar
    `camera_set_view_pos_subpixel` en sustitución de la función estándar.

**Reto extra:** el autor pone `room_goto()` dentro de `obj_camera` y avisa de que
«probablemente no debería ser responsabilidad de tu objeto cámara». Diseña dónde pondrías
esa lógica en un proyecto real y qué objeto se encargaría de ella. Justifica la respuesta.
