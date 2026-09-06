# 41 · Cámaras y resolución I — principiante (sin escribir código)

> **Serie:** GameMaker — Cameras & Resolution 2026 (PixelatedPope)
> **Vídeo:** 1 de 4 · Nivel **principiante**

| | |
|---|---|
| **Canal** | PixelatedPope |
| **URL** | <https://www.youtube.com/watch?v=gWaPZQiB9RQ> |
| **Duración** | 10 min 26 s |
| **Publicado** | 13 de diciembre de 2025 |
| **Nivel** | Principiante |
| **Motor** | GameMaker LTS 2026 |
| **Código GML** | Ninguno (todo se hace desde el inspector de la room) |

Este capítulo abre una serie de cuatro vídeos que cubre **el tema que más dudas genera en
GameMaker**: cómo conseguir que tu juego se vea bien en pantalla. Los capítulos **07**
(curso principal) y **20** (DragoniteSpam) te enseñan a poner una cámara en marcha; aquí
vas a entender **por qué** los números que pones importan, y qué ajustes de Windows
deciden si tu pixel art se ve nítido o borroso.

La premisa del autor es deliberadamente modesta:

> «¿Es el mejor sistema de cámara del mundo? No. Pero si acabas de empezar en el
> desarrollo de juegos, **es un punto de partida estupendo**.»

## Índice de contenido

1. Antes de la cámara: los ajustes de la plataforma Windows
2. Interpolar colores entre píxeles: el ajuste que arruina el pixel art
3. Permitir redimensionar la ventana: por qué conviene dejarlo apagado
4. Ventana sin bordes y opciones de escalado
5. El tamaño de la room no debe controlar el tamaño de la ventana
6. Activar viewports y cámaras desde el inspector
7. Viewport properties: el tamaño de tu ventana
8. Trampas del tamaño del viewport
9. Camera properties: cuánta room se ve (el zoom)
10. La relación de aspecto y la regla de dividir por el mismo número
11. Object Following: que la cámara persiga al jugador
12. Los bordes: la caja invisible antes de que la cámara se mueva
13. Lo que tendrás que repetir en cada room nueva

---

## 1. Antes de la cámara: los ajustes de la plataforma Windows

El vídeo empieza por donde casi nadie empieza: **la configuración de la plataforma**.
Antes de tocar una sola cámara, abre el **icono de engranaje** junto al botón de ejecutar
y entra en **Windows platform settings**.

> «Puedes leer para qué sirve cada una en el manual, hay un enlace en la descripción,
> pero vamos a hablar rápido de las importantes.»

Son cuatro ajustes, y tres de ellos conviene dejarlos como están.

---

## 2. Interpolar colores entre píxeles: el ajuste que arruina el pixel art

**Interpolate colors between pixels** es «la grande», en palabras del autor, y la razón
principal por la que entramos aquí.

Cuando está activada, esta opción **difumina los colores entre píxeles**. Si tu juego usa
pixel art con bordes duros, el resultado es un pegote borroso. Si tu arte es dibujado a
mano o en alta definición, en cambio, puedes dejarla activada sin problema.

| Tipo de arte | Recomendación |
|---|---|
| Pixel art con bordes duros | **Desmarcar** |
| Dibujo a mano o HD | Mantener marcada |

En el tutorial se desmarca, porque el proyecto de ejemplo es pixel art.

---

## 3. Permitir redimensionar la ventana: por qué conviene dejarlo apagado

**Allow window resize** permite al jugador arrastrar las esquinas de la ventana para
cambiar su tamaño, y habilita el botón de maximizar.

> «Recomiendo mucho que **mantengas esto desactivado** si eres nuevo en GameMaker. Es una
> opción bastante inusual de darle al jugador y requiere **un poco de código** para
> gestionarla bien.»

No es que esté mal: es que gestionar el redimensionado libre exige trabajo extra que no
tiene sentido asumir en tu primer proyecto.

---

## 4. Ventana sin bordes y opciones de escalado

**Borderless window** controla si la ventana tiene borde y barra de título. Si la
desactivas, **el jugador no podrá mover la ventana por su escritorio**, lo cual es
molesto. Se deja apagada.

**Las opciones de escalado** controlan cómo GameMaker estira tu juego para rellenar la
ventana.

> «Siempre querrás dejarlo en **keep aspect ratio**. Hay muy pocas razones para usar
> *full scale*, y solo deberías cambiarlo si sabes lo que haces.»

Con *keep aspect ratio*, si la proporción de tu juego y la de la ventana no coinciden,
aparecen **barras negras**. Con *full scale*, la imagen se deforma. La primera siempre es
preferible.

---

## 5. El tamaño de la room no debe controlar el tamaño de la ventana

El proyecto de ejemplo tiene tiles y un personaje que se mueve. Lo que importa está en el
**inspector**: el tamaño por defecto de la room es **1366 × 768**.

Si ejecutas el juego tal cual, la ventana que aparece mide **1366 × 768 más la altura de
la barra de título**. Podrías cambiar el tamaño de la room para controlar la ventana, pero:

> «No es una buena idea. **No quieres verte obligado a hacer tus niveles del mismo tamaño
> que tu ventana.**»

La solución correcta es **independizar el tamaño de la room del tamaño de la ventana**,
que es justo lo que hacen los viewports.

---

## 6. Activar viewports y cámaras desde el inspector

Cerca del final del inspector de la room está la sección **Viewports and Cameras**.
Despliégala:

1. Marca **Enable Viewports**.
2. Despliega **Viewport 0**.
3. Marca la casilla **Visible**.

Verás aparecer un **borde blanco** alrededor de la room: es la región que la cámara ve.

Hay tres grupos de opciones, y el autor las aborda empezando por la del medio:

- **Camera properties** → qué se ve de la room.
- **Viewport properties** → qué tamaño tiene la ventana.
- **Object Following** → a quién sigue la cámara.

---

## 7. Viewport properties: el tamaño de tu ventana

> «Ignora las casillas X e Y, probablemente nunca las necesites. En su lugar, cambia el
> **width** y el **height** básicamente.»

Ponlos a **1280 × 720**, una resolución panorámica muy común, y obtendrás **una ventana de
exactamente 1280 × 720**.

Así de simple: **si quieres controlar el tamaño de la ventana de tu juego, el ancho y el
alto del viewport lo hacen.**

---

## 8. Trampas del tamaño del viewport

Dos advertencias importantes.

**Solo funciona en la primera room.** Si tu juego tiene varias rooms y estás en una que
no tiene el **icono de la casita** al lado, las propiedades del viewport **no hacen nada**.

**No lo pongas al tamaño de tu monitor.** Si tu monitor es 1920 × 1080, no pongas el
viewport a 1920 × 1080. El tamaño del viewport es **el contenido** de tu ventana, y la
barra de título **se suma por encima**. Windows no permite una ventana cuya altura total
supere la altura de la resolución, así que **aplastará tu ventana** para dejar sitio a la
barra, y se verá mal.

---

## 9. Camera properties: cuánta room se ve (el zoom)

Tras ajustar la ventana, el resultado es decepcionante:

> «Incluso esto no se ve muy bien. La cámara está demasiado alejada y, aunque cuesta
> verlo, hay una ligera distorsión de píxeles. Quiero acercar y quiero que los píxeles
> sean perfectos.»

Las **Camera properties** controlan qué es visible:

- **Width y Height** → cuánto de la room se ve a la vez.
- **X e Y** → mueven la cámara para mostrar otras zonas (casi nunca los tocarás por aquí).

Si pones **100 × 100**, el rectángulo blanco del editor se encoge.

> «Cuanto más pequeño sea ese rectángulo, **más cerca** se sentirá tu juego. Y cuanto más
> grande, más lejos.»

Pero al ejecutar, el resultado es horrible: demasiado cerca y **todo estirado**.

---

## 10. La relación de aspecto y la regla de dividir por el mismo número

¿Cómo elegir un tamaño que se vea bien? Hay que elegir uno con **la misma relación de
aspecto** que la ventana.

La relación de aspecto es, básicamente, **la anchura dividida por la altura**:

| Resolución | Cálculo | Relación |
|---|---|---|
| 1920 × 1080 | 1920 / 1080 | 1,777… |
| 1280 × 720 | 1280 / 720 | 1,777… |

Tienen la misma relación de aspecto. Y la forma más fácil de obtener un tamaño con la
misma relación que tu ventana es **dividir la anchura y la altura por el mismo número**.

Probando con **2**:

```
1280 / 2 = 640
 720 / 2 = 360

 640 / 360 = 1,777…   ✅ la misma relación de aspecto
```

Al ejecutar, se ve mucho mejor: sin distorsión, aunque quizá todavía algo lejos.

Probando con **3**, aparece el primer problema real:

```
1280 / 3 = 426,666…
 720 / 3 = 240        ✅ entera
```

> «En ese caso probablemente no queramos usar 3. **Realmente queremos que las dimensiones
> de la cámara usen números enteros.** Además, ni siquiera puedes escribir decimales en
> las propiedades de la cámara.»

Así que se sube a **4**:

```
1280 / 4 = 320
 720 / 4 = 180
```

Que es, por cierto, **exactamente la resolución que se usa en el curso principal**
(capítulo 02). Al ejecutar, se ve bien.

La regla general:

> «Cuanto más alto sea el número por el que dividas el tamaño de la ventana, **más cerca**
> estará tu juego. Y cuanto más bajo, más lejos. Depende de ti decidir.»

Si tu juego es pixel art, **trabaja siempre con números enteros**. Si usa sprites suaves
dibujados a mano, no hace falta tanta precisión.

---

## 11. Object Following: que la cámara persiga al jugador

Último paso: que la cámara siga al personaje. En el grupo **Object Following**, haz clic
en el botón que dice **no object** y selecciona tu objeto jugador.

> «Es poco probable que necesites tocar los valores de **horizontal speed** y **vertical
> speed**, así que ignóralos.»

Lo que sí importa son los **bordes**:

- **Horizontal border**
- **Vertical border**

Controlan **lo cerca que tiene que llegar el jugador al borde de la pantalla** antes de
que la cámara empiece a seguirlo.

---

## 12. Los bordes: la caja invisible antes de que la cámara se mueva

Con los bordes pequeños, el jugador puede moverse bastante antes de que la cámara
reaccione. Al acercarse al borde, la cámara arranca y **solo se detiene al llegar al borde
de la room**.

> «Cuanto más grandes hagamos estos bordes, **más pequeña es la caja** en la que nuestro
> objeto puede moverse antes de que la cámara empiece a moverse.»

Con un borde de **64 píxeles**, la caja es mucho más pequeña: el personaje apenas puede
subir o bajar sin arrastrar la cámara.

Y si quieres la cámara **clavada** al personaje:

> «Podemos poner el borde en un número muy alto como **9999**, y eso mantendrá al
> personaje perfectamente centrado hasta que la cámara llegue al borde de la room.»

El autor lo deja clavado para el resto de la serie.

---

## 13. Lo que tendrás que repetir en cada room nueva

Aquí está la gran pega del sistema, y el motivo por el que existe la parte 2:

> «Lo último que hay que recordar es que **cada vez que añades una room nueva** a tu
> juego, tienes que volver a pasar por casi todo esto otra vez.»

Activar viewports. Hacer visible el viewport 0. Poner las camera properties al mismo ancho
y alto que tus otras rooms. Volver a configurar el object following.

> «No lo olvides o causará problemas.»

Con esto tienes **el tamaño de ventana que quieres, el tamaño de cámara que quieres, y
sigue al objeto que quieres**.

---

## Puntos clave

1. **Interpolate colors between pixels** se **desmarca** para pixel art y se mantiene para
   arte HD o dibujado a mano.
2. **Allow window resize** conviene dejarlo **desactivado**: gestionarlo bien requiere
   código.
3. Las opciones de escalado van siempre en **keep aspect ratio**.
4. **No uses el tamaño de la room** para controlar el tamaño de la ventana.
5. **Viewport properties** (ancho y alto) = **el tamaño de la ventana**.
6. El viewport solo tiene efecto en **la primera room** (la del icono de la casita).
7. **Nunca** pongas el viewport al tamaño exacto de tu monitor: la barra de título se suma
   y Windows aplastará la ventana.
8. **Camera properties** (ancho y alto) = **cuánta room se ve**: más pequeño es más cerca.
9. La cámara debe tener **la misma relación de aspecto** que la ventana.
10. Para conseguirlo, **divide el ancho y el alto de la ventana por el mismo número**
    entero.
11. **Object Following** con un borde de **9999** deja al personaje clavado en el centro.
12. Hay que repetir **toda** la configuración en **cada room nueva**.

---

## Ejercicio propuesto

> **Objetivo:** configurar una cámara correcta desde cero y entender la relación entre el
> tamaño de la ventana y el tamaño de la cámara.

1. Crea un proyecto nuevo con un sprite de jugador, un objeto que se mueva con las flechas
   y una room más grande que la ventana (por ejemplo **2000 × 1500**).
2. Abre el **icono de engranaje → Windows platform settings** y **desmarca**
   *Interpolate colors between pixels*. Comprueba que *Allow window resize* está apagado y
   que el escalado está en *keep aspect ratio*.
3. Activa **Enable Viewports** y **Visible** en el viewport 0.
4. Pon las **Viewport properties** a **1280 × 720**. Ejecuta: la ventana mide exactamente
   eso.
5. Pon las **Camera properties** a **100 × 100**. Ejecuta. Describe con tus palabras qué
   le pasa a la imagen y por qué.
6. Ahora aplica la regla del vídeo: divide 1280 y 720 entre **2** y pon **640 × 360**.
   Ejecuta y comprueba que la distorsión desaparece.
7. Repite con **3** (`426,66 × 240`). Fíjate en que **no puedes escribir decimales** en el
   campo. Anota qué harías en este caso.
8. Repite con **4** (**320 × 180**) y con **6** (**213,33 × 120**). ¿Cuál te gusta más para
   tu arte? ¿Cuáles han dado números enteros?

**Parte de seguimiento**

9. Asigna **Object Following** a tu objeto jugador y deja los bordes en su valor por
   defecto. Muévete y observa cuánto tardas en «empujar» la cámara.
10. Pon el borde horizontal a **64** y ejecuta. Describe cómo cambia la sensación.
11. Pon ambos bordes a **9999**. El personaje queda clavado en el centro. Muévete hasta el
    borde de la room y comprueba que la cámara **se detiene** al llegar.
12. Crea **una segunda room** igual y ejecuta el juego entrando en ella **sin configurar
    nada**. Comprueba qué ocurre y explica por qué este sistema se vuelve tedioso en
    proyectos con muchos niveles.

**Reto extra:** calcula qué tamaño de cámara necesitarías si tu ventana fuera
**1920 × 1080** y quisieras un zoom equivalente al de dividir entre 4. Escribe la cuenta
completa y verifica que la relación de aspecto sigue siendo 1,777…
