# 44 · Cámaras y resolución IV — experto (la capa GUI, dibujar en una caja, filtrado bilineal y el mito del escalado perfecto)

> **Serie:** GameMaker — Cameras & Resolution 2026 (PixelatedPope)
> **Vídeo:** 4 de 4 · Nivel **experto** · **FIN DE LA SERIE**

| | |
|---|---|
| **Canal** | PixelatedPope |
| **URL** | <https://www.youtube.com/watch?v=Jl5KxYRXCW8> |
| **Duración** | 20 min 22 s |
| **Publicado** | 3 de enero de 2026 |
| **Nivel** | Experto |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | evento Draw GUI, `draw_sprite_ext`, `application_surface_draw_enable`, evento Post Draw, `draw_surface_stretched`, `gpu_set_blendenable`, `surface_get_width/height`, `window_get_width/height`, shaders y uniforms |

## Índice de contenido

1. Bienvenido a aguas profundas
2. Si tu juego no es pixel art, puedes saltarte casi todo esto
3. Qué es realmente la «capa» GUI: no hay capa
4. El tamaño de la GUI es solo una escala
5. Celeste y la GUI más grande que el view
6. La GUI no puede desactivar los subpíxeles
7. Undertale: por qué la versión de PS4 se ve distinta
8. Dibujar tu juego en una caja, paso a paso
9. El misterio de las sombras que se oscurecen
10. Lo que rompe dibujar en una caja: la GUI, el ratón y las UI layers
11. La alternativa: usar la GUI como máscara
12. Sonic Mania y el filtrado bilineal
13. Aplicar el filtrado: evento Draw GUI Begin + shader
14. Los cuatro uniforms del shader
15. Keystone: la biblioteca de código abierto del autor
16. El mito del escalado perfecto con relación de aspecto dinámica
17. Dunking sobre mi yo del pasado: Surface Book 2
18. El OnePlus 8 y el 2297: un número primo
19. La conclusión práctica: diseña para 1080p

---

## 1. Bienvenido a aguas profundas

El vídeo arranca con una de las mejores advertencias que vas a encontrar en un tutorial:

> «Bienvenido al último vídeo de mi serie de tutoriales de cámaras y resolución. En este
> punto, **estamos en lo más hondo**. Más allá de aquí **no hay soluciones perfectas. No hay
> respuestas correctas. No hay procesos ni procedimientos infalibles.** Hemos entrado en el
> reino de **las opiniones y las conjeturas**.»

Y una matización sobre el formato:

> «Voy a enseñarte a hacer un par de cosas, pero esto es **mucho menos un tutorial y mucho
> más una charla tipo GDC**.```

---

## 2. Si tu juego no es pixel art, puedes saltarte casi todo esto

> «Si tu juego **no** es pixel art, la inmensa mayoría de este vídeo **realmente no te va a
> aplicar**. Has decidido jugar en modo fácil y no necesitas preocuparte tanto por cómo tu
> juego se estira y escala en distintas pantallas. **Enhorabuena.**»

Este capítulo va dirigido a quien esté haciendo **un juego de pixel art** y le preocupe
cómo se verá en monitores de resoluciones distintas.

---

## 3. Qué es realmente la «capa» GUI: no hay capa

Antes de cruzar el umbral, toca entender bien los eventos GUI.

> «Los eventos GUI son **un poco raros**. A menudo decimos *capa GUI*, pero **eso no es
> correcto**. No hay ninguna capa. **Ni siquiera hay una superficie.**»

Todo lo que dibujas en tus eventos GUI se dibuja **esencialmente directo en la ventana del
juego**.

---

## 4. El tamaño de la GUI es solo una escala

> «El tamaño de la GUI **simplemente determina la escala a la que se dibuja todo**.»

El ejemplo del autor:

- Tamaño de ventana: **500 × 500**.
- Tamaño de GUI: **100 × 100**.
- Resultado: al dibujar, **todo se escala automáticamente cinco veces**.

En su proyecto de ejemplo, la ventana mide **1600 × 900** y la escala de la GUI es **5x**.

> «Esto es típico de un juego de pixel art. **Dimensionas tu GUI para que coincida con tu
> view**, y tu interfaz tiene una densidad de píxel consistente.»

---

## 5. Celeste y la GUI más grande que el view

> «Puedes romper esta regla, sin embargo. Un juego como **Celeste** tiene un tamaño de GUI
> **mucho más grande** que su tamaño de view. Funciona bien porque **la interfaz tiene un
> estilo de arte completamente distinto** al del juego del fondo. Se ve fantástico, pero
> hay que hacerlo con cuidado.»

Eso sí, tiene una consecuencia que casi nadie anticipa:

> «Si haces eso, ten en cuenta que **tu escala mínima de ventana ya no es 1**. Ahora es
> **la escala de tu GUI**.»

---

## 6. La GUI no puede desactivar los subpíxeles

Esta es la demostración más interesante del bloque. El autor cambia el `draw_sprite` de un
evento Draw GUI por un `draw_sprite_ext` que dibuja al personaje **a un quinto de su
tamaño normal**:

```gml
// Draw GUI event de obj_player (demostración)
draw_sprite_ext(sprite_index, image_index,
                x, y,
                0.2, 0.2,   // escala: 1/5 del tamaño normal
                0,
                c_white, 1);
```

El resultado:

> «¿Has visto eso? **Es perfecto.** Es pequeño, sí, pero **no ha perdido ni un solo píxel
> de detalle**.»

La objeción obvia es que eso funciona porque tiene **subpíxeles activados**. Y el autor la
anticipa:

> «**Tienes media razón.** Tengo subpíxeles activados y esto funcionaría ahora mismo en el
> evento draw normal. Pero **incluso si los desactivara** y la app surface estuviera
> dimensionada al mismo tamaño que el view, **esto seguiría funcionando**. Eso es porque
> **no puedes desactivar los subpíxeles para la GUI**. No es posible por defecto.»

La consecuencia práctica es importante:

> «Si estás intentando mantener una **rejilla de píxel retro estricta**, puedes usar los
> eventos GUI, pero **ten cuidado de no hacer ningún escalado ni rotación en tu interfaz**,
> o la ilusión de tu estética puede resquebrajarse.»

---

## 7. Undertale: por qué la versión de PS4 se ve distinta

> «No podemos hablar de hacer un juego en GameMaker sin mencionar **Undertale**, ¿verdad?»

Si has jugado Undertale en PS4 o PS5, puede que el juego te haya parecido «un poco
distinto». ¿Por qué?

- La resolución por defecto de Undertale es **640 × 480**.
- Las consolas se juegan normalmente en televisores.
- Los televisores son muy típicamente **1920 × 1080**.

La cuenta:

```
1080 / 480 = 2,25
```

> «**No es un número entero, no va a escalar perfectamente.**»

Esto es lo que se ve en un monitor de 1920 × 1080 a pantalla completa en PC, con una
rejilla superpuesta para evidenciarlo: un desastre de píxeles desiguales.

> «¿Se ve bien? Sí, claro. Estoy seguro de que muchísima gente en PC jugó a pantalla
> completa a 1080p y no se quejó. El estilo de arte de Undertale **simplemente funciona**,
> incluso cuando las cosas están un poco mal.»

Pero alguien, en el caso de PS4, decidió que no se veía lo bastante bien y que había que
**renderizar el juego entero en una caja**. Eso permitía escalar el juego **perfectamente a
2x**, hasta **1280 × 960**.

---

## 8. Dibujar tu juego en una caja, paso a paso

Si quieres hacer lo mismo —preferir una caja negra con escalado perfecto antes que rellenar
la ventana— esto es lo que hay que hacer.

**Paso 1.** Cambiar el tamaño base a **640 × 480**.

**Paso 2.** En la función que alterna la pantalla completa, **desactivar el dibujado
automático de la superficie de aplicación** al entrar en pantalla completa, y reactivarlo
al volver a modo ventana:

```gml
/// @desc Alterna entre pantalla completa y modo ventana.
function toggle_fullscreen()
{
    window_set_fullscreen(!window_get_fullscreen());

    if (window_get_fullscreen())
    {
        // ──────────────────────────────────────────────────────
        // Desactivamos el dibujado automático: a partir de ahora
        // NOSOTROS dibujamos la superficie de aplicación.
        // ──────────────────────────────────────────────────────
        application_surface_draw_enable(false);
    }
    else
    {
        application_surface_draw_enable(true);
    }
}
```

> «Si ejecutáramos el juego ahora y cambiáramos a pantalla completa, **no veríamos nuestro
> juego**. Desactivar el dibujado automático de la app surface significa que **necesitamos
> dibujarla a mano** en la ventana.**

**Paso 3.** Dibujarla en el evento **Post Draw**:

```gml
// Post Draw event de obj_camera
// ─────────────────────────────────────────────────────────────
// Si no estamos en pantalla completa, GameMaker ya dibuja la
// superficie automáticamente: nos vamos.
// ─────────────────────────────────────────────────────────────
if (!window_get_fullscreen()) exit;

// ─────────────────────────────────────────────────────────────
// OJO: el sistema de coordenadas de Post Draw es el de la
// VENTANA del juego. El (0,0) es la esquina superior izquierda
// de la ventana, INCLUYENDO las barras negras. Hay que usar las
// dimensiones de la ventana para centrar la superficie.
// ─────────────────────────────────────────────────────────────
var _surface_width  = surface_get_width(application_surface);
var _surface_height = surface_get_height(application_surface);

var _x = (window_get_width()  - _surface_width)  / 2;
var _y = (window_get_height() - _surface_height) / 2;

draw_surface_stretched(application_surface, _x, _y,
                       _surface_width, _surface_height);
```

> «Ya escalamos nuestra app surface apropiadamente, así que no tenemos que hacer nada más.»

El resultado funciona: escalado perfecto dentro de una caja. Incluso se puede dibujar una
imagen de fondo o un color detrás.

---

## 9. El misterio de las sombras que se oscurecen

> «Pero puede que estés notando algo raro. De hecho, hay **dos problemas**. Uno lo podemos
> arreglar fácil y **el otro no**.»

El primero: mira la sombra debajo de los arbustos al alternar entre ventana y pantalla
completa. **¿Se oscurece en pantalla completa?**

> «Esto es algo con lo que tenemos que lidiar cuando **dibujamos a mano la superficie de
> aplicación**. Es cómo los píxeles de una superficie que son **semi-transparentes** se
> mezclan con el objetivo de dibujado, la ventana. **Es fácil de arreglar, pero sinceramente
> un poco difícil de explicarme.**»

El autor se ríe de sí mismo:

> «Seguro que hay algún **nerd en los comentarios** que lo explicará mejor que yo.»

La solución es desactivar la mezcla (*blending*) justo alrededor del dibujado:

```gml
// Post Draw event de obj_camera (versión corregida)
if (!window_get_fullscreen()) exit;

var _surface_width  = surface_get_width(application_surface);
var _surface_height = surface_get_height(application_surface);

var _x = (window_get_width()  - _surface_width)  / 2;
var _y = (window_get_height() - _surface_height) / 2;

// ─────────────────────────────────────────────────────────────
// Sin esto, los píxeles semi-transparentes se oscurecen al
// mezclarse con la ventana.
// ─────────────────────────────────────────────────────────────
gpu_set_blendenable(false);

draw_surface_stretched(application_surface, _x, _y,
                       _surface_width, _surface_height);

gpu_set_blendenable(true);
```

> «Ahí lo tienes. Eso se ve bien. **Un problema resuelto.**»

---

## 10. Lo que rompe dibujar en una caja: la GUI, el ratón y las UI layers

El segundo problema es el que **no** se puede arreglar.

> «¿Pero qué pasa con nuestra información de pantalla? Ya no está en la esquina superior
> izquierda del juego. **Está flotando por encima.** ¿Qué está pasando?»

La causa:

> «**La GUI dibuja basándose en donde GameMaker dibujaría normalmente la superficie de
> aplicación.** Así que cuando dices «no, la voy a dibujar yo donde quiero», **no hay forma
> de decirle a GameMaker que la estás dibujando en otro sitio**. Por eso la GUI no va a
> alinearse con tu nuevo juego en una caja.»

Y no es lo único que se rompe:

> «Si planeas usar **interacciones de ratón** en tu juego, las funciones `mouse_x` y
> `mouse_y` **también dejarán de funcionar**. Así que si quieres dibujar tu juego en una
> caja y usar las funciones de ratón integradas, **lo tienes bastante crudo**.»

Lo mismo aplica a quien quiera emular los RPG antiguos, con la interfaz a un lado y el
juego renderizado en una especie de marco.

> «**Cada vez** que quieras dibujar a mano la superficie de aplicación en un sitio distinto
> de donde la dibujaría GameMaker, **rompes la GUI, rompes la interacción del ratón y rompes
> las UI layers**.»

### Lo que sí se puede hacer

> «Una solución posible es construir tu juego como he descrito en los vídeos anteriores, con
> la app surface dibujándose de forma normal y automática, y luego **dibujar la interfaz
> encima de todo como una máscara**. Así tu cámara está técnicamente mostrando más de lo
> que realmente quieres, pero **usas la GUI para ocultar lo que no quieres mostrar**. Después
> ajustas qué significa para tu cámara estar centrada en algo.»

### Y la esperanza de futuro

> «Dicho todo esto, he enviado una **solicitud de funcionalidad formal** para permitirnos
> definir el rectángulo que usan la superficie de aplicación, las variables de ratón, la
> UI layer y la GUI para alinearse. Así que si la conseguimos en algún momento del futuro,
> puedes apostar a que publicaré un tutorial nuevo. **Mientras tanto, tiendo a recomendar no
> hacerlo.**»

---

## 11. Sonic Mania y el filtrado bilineal

> «Puede que te haya convencido de no dibujar tu juego en una caja, pero sigues sin estar
> contento con cómo se ve en pantalla completa en algunas pantallas. Es totalmente
> comprensible.»

Entonces hay otra opción. El ejemplo:

> «Puede que hayas oído hablar de un jueguecillo llamado **Sonic Mania**. Es un juego que se
> apoya mucho en su estética de pixel art retro auténtica. Busca parecer un juego antiguo
> de Sega Genesis, y ha recibido **elogios unánimes** por esos gráficos. ¿Pero son
> perfectos?»

La cuenta:

```
Resolución nativa de Sonic Mania: 424 x 240
1080 / 240 = 4,5
```

> «**No es un número entero, no escala perfectamente.** ¿Cómo consiguió Sonic Mania elogios
> universales por sus gráficos de pixel art sin escalar perfectamente a la resolución de
> pantalla más común que existe? **Filtrado bilineal.**»

### Qué hace

> «El filtrado bilineal es **un método de reescalar pixel art con más cuidado**. Es un método
> de reescalado súper común, y hay un montón de recursos por ahí que te darán una
> explicación técnica más precisa de cómo funciona. Yo estoy más preocupado por **los
> resultados**.»

Y los resultados:

> «Cuando estás a resolución completa, en la mayoría de los casos es **casi imposible ver
> que se está produciendo ningún desenfoque**. Todo se ve nítido. Añade a la ecuación
> movimiento a 60 fps y **ningún jugador casual lo notará nunca**.

### Cuándo funciona y cuándo no

> «Claro, esto depende del factor de escala. **4,5x probablemente se vería bien en
> movimiento a 60 fps** para empezar. Una vez que pasas de **3x**, cualquier distorsión va a
> ser súper menor en casi cualquier juego. Pero si fuera **1,5x o 2,5x**, el resultado podría
> no ser tan limpio.»

La advertencia final del autor:

> «Así que si haces tu juego a una resolución maldita como **1280 × 720**, no estoy seguro
> de que ni siquiera un filtro bilineal te salve.»

---

## 12. Aplicar el filtrado: evento Draw GUI Begin + shader

**Paso 1.** Cambiar el tamaño base a **424 × 240**.

**Paso 2.** Seguir desactivando el dibujado automático de la superficie de aplicación en
pantalla completa, porque vamos a dibujarla con un shader.

**Paso 3.** Cambiar el evento donde dibujamos la superficie: de **Post Draw** a
**Draw GUI Begin**.

> «Para ahorrarnos hacer más matemáticas, vamos a cambiar el evento en el que dibujamos la
> superficie de aplicación de Post Draw a **Draw GUI Begin**. Eso nos permitirá aprovechar
> que, **incluso cuando la app surface no se dibuja automáticamente, la GUI sigue
> posicionada en la ventana donde la app surface debería dibujarse**.»

**Paso 4.** Necesitamos un shader. El autor no lo escribe para el tutorial: usa uno escrito
por **Mino** para su asset *better scaling*, con permiso para redistribuirlo como parte de
una herramienta de código abierto.

Con el shader en el proyecto, el evento queda así:

```gml
// Draw GUI Begin event de obj_camera
// ─────────────────────────────────────────────────────────────
// Si no estamos en pantalla completa, no hacemos nada.
// ─────────────────────────────────────────────────────────────
if (!window_get_fullscreen()) exit;

// ─────────────────────────────────────────────────────────────
// Antes de dibujar, hay que fijar los cuatro uniforms.
// ─────────────────────────────────────────────────────────────
var _surface_width  = surface_get_width(application_surface);
var _surface_height = surface_get_height(application_surface);

// Ratio entre la ventana y la superficie de aplicación.
var _scale_x = window_get_width()  / _surface_width;
var _scale_y = window_get_height() / _surface_height;

shader_set(shd_bilinear);

// Los uniforms de "bitmap" se refieren a la superficie que vamos
// a dibujar: en este caso, la app surface.
shader_set_uniform_f(shader_get_uniform(shd_bilinear, "u_bitmap_width"),  _surface_width);
shader_set_uniform_f(shader_get_uniform(shd_bilinear, "u_bitmap_height"), _surface_height);

// Los uniforms de "scale" son la proporción ventana / app surface.
shader_set_uniform_f(shader_get_uniform(shd_bilinear, "u_scale_x"), _scale_x);
shader_set_uniform_f(shader_get_uniform(shd_bilinear, "u_scale_y"), _scale_y);

// ─────────────────────────────────────────────────────────────
// Seguimos necesitando los toggles de blending.
// ─────────────────────────────────────────────────────────────
gpu_set_blendenable(false);

// Como estamos en el evento GUI, basta con estirar la superficie
// a las dimensiones de la GUI.
draw_surface_stretched(application_surface, 0, 0,
                       display_get_gui_width(),
                       display_get_gui_height());

gpu_set_blendenable(true);

shader_reset();
```

> «Si tienes una configuración inusual puede que tengas que pensar un poco más esta lógica,
> pero para este proyecto, y espero que para la mayoría, **es tan simple como esto**.»

### La valoración honesta del autor

> «Y sí, se ve bastante bien. Seré el primero en admitir que el arte que estoy usando para
> este proyecto de ejemplo **no es exactamente ideal** para demostrar lo bien que queda esto.
> Un proyecto con pixel art **más detallado** se beneficiará mucho más de un filtro
> bilineal.»

Y el consejo de cuándo hacerlo:

> «Te aconsejaría que **esperes a tener un problema visual que quieras suavizar** antes de
> tomarte la molestia de montar esto.»

---

## 13. Keystone: la biblioteca de código abierto del autor

> «Como he mencionado hace un momento, estoy trabajando en una biblioteca de código abierto
> que intenta hacer todo esto automáticamente. Se llama **Keystone** y, al grabar esto,
> **todavía está bastante al principio del desarrollo**. No hay documentación, y desde luego
> no está probada a fondo.»

Lo que soporta:

- Filtrado bilineal.
- Dibujar el juego en una caja, **pero con herramientas para lidiar con lo que se rompe**:
  soporte de ratón y GUI desalineada.

Lo que **no** soporta:

- **UI layers.**

Y la motivación personal:

> «Si alguna vez conseguimos esa solicitud de funcionalidad que he mencionado antes,
> probablemente podría reducir la cantidad de código del sistema en un **75 %**.»

---

## 14. El mito del escalado perfecto con relación de aspecto dinámica

Llegamos a la parte polémica.

> «Por fin es hora de hablar de algo que quizá sea un **poco controvertido**. Hablemos de
> **escalar perfectamente a cualquier resolución de pantalla sin usar ningún tipo de truco
> de shader**, también conocido como *escalado pixel perfect con soporte de relación de
> aspecto dinámica*.»

El autor se refiere a **su propia serie antigua**, *Resolution and Aspect Ratio
Management*, donde afirmaba tener un proceso matemático sencillo para escalar un juego de
pixel art perfectamente a cualquier resolución de monitor.

Y su valoración actual es tajante:

> «**El proceso descrito en ese vídeo es defectuoso. No funciona para todas las
> resoluciones.**»

Lo gracioso, añade, es que **ni siquiera funcionaba para un portátil que él tenía** cuando
hizo esos tutoriales.

---

## 15. Dunking sobre mi yo del pasado: Surface Book 2

El proceso antiguo partía de una resolución panorámica de SNES como tamaño base:
**512 × 288**. Vamos a ver cómo se comporta con un monitor de **3000 × 2000**:

```
1) 3000 / 512 = 5,859375
2) Redondeamos hacia arriba a 6, porque es el cambio más pequeño
   respecto al tamaño deseado.
3) Dividimos la resolución horizontal de la pantalla para obtener
   la anchura del view:
   3000 / 6 = 500          ✅ entero
4) Dividimos la resolución vertical de la pantalla entre 6 para
   obtener la altura del view:
   2000 / 6 = 333,333…     ❌ NO es entero
```

> «**No es un número entero. No va a escalar perfectamente. Lo siento.**»

Y remata:

> «Puede que digas «quizá hay otra solución». Y quizá la haya. Pero déjame enseñarte **otro
> problema** con el que me encontré hace unos cuatro años mientras buscaba una solución
> mejor, y que me convenció de **dejar de intentar** soportar relaciones de aspecto
> dinámicas y todas las resoluciones de monitor que puedan existir.»

---

## 16. El OnePlus 8 y el 2297: un número primo

La conclusión sobre qué hace falta para escalar perfectamente:

> «Para conseguir un escalado pixel perfect sin barras negras, necesitas poder **encontrar
> un tamaño de view que sea un múltiplo entero de la resolución del monitor**. Es decir:
> divides la resolución del monitor entre el tamaño del view y obtienes un número entero
> como 2, 3, 4…»

Y entonces presenta su teléfono, el **OnePlus 8**:

- La hoja de especificaciones dice que su resolución en horizontal es **2400 × 1080**.
- Pero al pedir la resolución desde GameMaker con `display_get_width()`, obtiene un ancho de
  pantalla de **2297**.

> «**Eso es un número primo.** No puedes dividir ese número entre nada que no sea él mismo o
> 1 y obtener un número entero. **No hay forma de escalar ningún juego de pixel art a esa
> resolución de forma perfecta. Es literalmente imposible.**»

¿Por qué reporta 2297 cuando debería ser 2400?

> «Ni idea. Hablé con **Russell K**, el jefe de GameMaker, y teorizó que podría ser **algo
> raro del DPI**, una **zona de dibujo segura**, o alguna otra cosa específica de Android.
> Pero realmente **no hay nada que GameMaker pueda hacer aquí**. Si Android le dice a
> GameMaker que la resolución es un número primo, **tenemos que usarla**.»

---

## 17. La conclusión práctica: diseña para 1080p

Este hallazgo le hizo replantearse las prioridades:

> «En un juego 3D, soportar cualquier resolución y cualquier relación de aspecto es tan
> simple como cambiar la relación de aspecto de tu cámara y tu resolución interna. Incluso
> si no está escalado perfectamente, **¿a quién le importa? Nadie lo va a notar.** Pero para
> un juego 2D de pixel art, si requiere tanto trabajo, **¿vale la pena el esfuerzo?**»

Y las preguntas que propone hacerse:

> «¿Hay reseñas de grandes juegos de pixel art donde la gente se queje de que no rellena su
> monitor ultra-wide? Y si las hay, **¿vale la pena contentar a esa gente?**»

La respuesta que se da:

> «Al final, **si has hecho un juego bueno, la gente estará demasiado ocupada disfrutándolo
> como para preocuparse por las barras negras o una distorsión de píxel menor**. Y si tu
> juego es lo bastante popular como para que **un pequeño subconjunto de tus jugadores te
> suplique soporte ultra-wide**, vaya, **qué problema tan fantástico tener**.»

Y la recomendación final, que enlaza con todo lo anterior:

> «Por eso **mi enfoque actual es diseñar para 1920 × 1080 y no preocuparme de nada más
> hasta que tenga un cliente que pague suplicándome cambios**. Deberías preguntarte:
> **¿habría vendido más Undertale si…?**»

---

## Puntos clave

1. Más allá de este punto **no hay soluciones perfectas**, solo opiniones y conjeturas.
2. Si tu juego **no es pixel art**, casi todo este capítulo no te aplica.
3. **No existe una «capa GUI»**: no hay capa ni superficie. Todo se dibuja **directo en la
   ventana**.
4. El tamaño de la GUI es **solo una escala**.
5. Lo habitual es que la GUI tenga **el mismo tamaño que el view**; Celeste es la excepción
   y, si lo haces, **tu escala mínima de ventana pasa a ser la de la GUI**.
6. **No puedes desactivar los subpíxeles en la GUI**: evita escalar y rotar en tu interfaz
   si buscas una rejilla retro estricta.
7. Undertale en PS4 se renderiza **en una caja** para escalar perfectamente a 2x.
8. Para dibujar en una caja: `application_surface_draw_enable(false)` y dibujar la
   superficie a mano en **Post Draw**.
9. En **Post Draw** el sistema de coordenadas es el de la **ventana**, incluidas las barras
   negras.
10. Hay que rodear el dibujado con `gpu_set_blendenable(false/true)` para que los píxeles
    semi-transparentes no se oscurezcan.
11. Dibujar en una caja **rompe la GUI, `mouse_x`/`mouse_y` y las UI layers**. El autor
    **recomienda no hacerlo**.
12. **Sonic Mania** no escala perfectamente (4,5x) y aun así recibe elogios: usa **filtrado
    bilineal**.
13. El filtrado bilineal funciona bien **por encima de 3x**; con 1,5x o 2,5x puede no quedar
    limpio.
14. Para aplicarlo, dibuja la superficie en **Draw GUI Begin** con un shader y **cuatro
    uniforms**: ancho/alto del bitmap y escala en X/Y.
15. **El escalado pixel perfect con relación de aspecto dinámica es imposible** en general.
16. El proceso de la serie antigua del autor **falla en 3000 × 2000** con base 512 × 288.
17. Su **OnePlus 8** reporta un ancho de pantalla de **2297**, un **número primo**: ningún
    juego de pixel art puede escalar perfectamente a esa resolución.
18. El consejo final: **diseña para 1920 × 1080** y no te preocupes por lo demás hasta que
    un cliente de pago te lo pida.

---

## Ejercicio propuesto

> **Objetivo:** entender los límites reales del escalado en GameMaker y saber diagnosticar
> qué opción conviene a tu proyecto.

**Parte A — La GUI**

1. Añade un evento **Draw GUI** a tu objeto jugador con un `draw_sprite` sencillo.
   Comprueba que aparece **del mismo tamaño** que el dibujado normal, y explica por qué
   teniendo en cuenta la escala de tu GUI.
2. Cámbialo por un `draw_sprite_ext` con escala **0,2**. Comprueba que **no pierde detalle**.
3. Ahora **desactiva los subpíxeles** (vuelve a la opción de rejilla estricta del
   `surface_resize` del capítulo 42) y repite la prueba. Explica por qué **sigue
   funcionando**.
4. Añade una **rotación** a ese mismo `draw_sprite_ext` con la rejilla estricta activa.
   Describe cómo se resquebraja la ilusión retro y Conclusiona si usarías la GUI para tu
   interfaz.
5. Investiga qué pasaría si pusieras tu GUI al **doble de tamaño** que tu view: ¿cuál sería
   ahora tu escala mínima de ventana?

**Parte B — Dibujar en una caja**

6. Cambia tu tamaño base a **640 × 480** y ejecuta en pantalla completa. Calcula
   `1080 / 480` y describe la distorsión.
7. Implementa `application_surface_draw_enable(false)` en la función de pantalla completa y
   ejecuta. **Confirma que el juego desaparece** y explica por qué.
8. Dibuja la superficie a mano en **Post Draw**. Verifica que ahora sí aparece, centrada y
   escalada a 2x.
9. **Antes** de añadir los toggles de blending, busca zonas semi-transparentes en tu arte y
   compáralas entre modo ventana y pantalla completa.
10. Añade `gpu_set_blendenable(false/true)` y comprueba que el problema desaparece.
11. Añade `display_write_all_specs()` y observa dónde se dibuja. **Explica con tus palabras
    por qué la GUI deja de alinearse.**
    > ⚠️ **`display_write_all_specs()` NO es una función del runtime** — no está ni en
    > `GmlSpec.xml` ni en `fnames` ni en el manual de LTS 2026 (comprobado el 09-09-2026). Es un
    > script del autor del curso. Si sigues el ejercicio sin tenerlo, el juego compila y revienta
    > al ejecutarse (Trampa 4). Sustitúyelo por tus propios `show_debug_message()` con
    > `display_get_width()`, `display_get_gui_width()` y `camera_get_view_width(view_camera[0])`,
    > que sí existen.
12. Añade a tu juego un objeto que siga al ratón con `mouse_x` / `mouse_y`. Comprueba que
    **deja de funcionar** al dibujar en una caja.

**Parte C — Filtrado bilineal**

13. Cambia tu tamaño base a **424 × 240** y calcula `1080 / 240`. Anota el resultado.
14. Mueve el dibujado de la superficie de **Post Draw** a **Draw GUI Begin**. Comprueba que
    ahora **no necesitas calcular el centrado** a mano, y explica por qué.
15. Si consigues un shader de escalado bilineal, aplícalo con sus cuatro uniforms y compara
    el resultado con el escalado duro. Si no, documenta **qué** uniforms necesitaría y para
    qué sirve cada uno.

**Parte D — El mito del escalado perfecto**

16. Reproduce la cuenta del apartado 15 con los datos de **tu propio monitor** y tu tamaño
    base. ¿Obtienes enteros en X e Y?
17. Prueba con al menos **tres resoluciones** distintas (por ejemplo 1366 × 768,
    2560 × 1440 y 3440 × 1440) y anota en cuáles falla el proceso.
18. Investiga si puedes encontrar algún dispositivo cuyo `display_get_width()` devuelva un
    valor **primo**. Si lo encuentras, documenta el modelo y el número.

**Reto extra — decisión de diseño**

El autor propone diseñar para **1920 × 1080** y no preocuparse por lo demás, y remata con
«¿habría vendido más Undertale si…?». Escribe **media página** con tu propia decisión
razonada para un juego concreto que tengas en mente:

- ¿Tu juego es pixel art o no?
- ¿Qué tamaño base eliges y por qué?
- ¿Vas a dibujar en una caja, aplicar filtrado bilineal, o ninguna de las dos?
- ¿En qué momento te plantearías invertir tiempo en soportar otras resoluciones?

Justifica cada respuesta con los criterios de este capítulo, no con preferencias personales.
