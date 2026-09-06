# 13 · DragoniteSpam — Primeros pasos con GameMaker (2025/2026)

> **Serie:** Getting Started with GameMaker — DragoniteSpam
> **Vídeo:** 1 de 26 de la playlist oficial

| | |
|---|---|
| **Canal** | DragoniteSpam (Michael) |
| **URL** | <https://www.youtube.com/watch?v=bX3uF7oDDA4> |
| **Duración** | 22 min 35 s |
| **Publicado** | 30 de octubre de 2025 |
| **Nivel** | Principiante absoluto |
| **Motor** | GameMaker 2024.14 (a la espera de LTS 2026) |
| **Código GML** | Ninguno (capítulo de orientación) |

Primer vídeo de la serie de iniciación de **DragoniteSpam**, uno de los creadores
recomendados oficialmente por GameMaker. Es el complemento ideal al curso principal:
mientras la serie de Sky LaRell Anderson te lleva de cero a publicar, esta te explica el
**porqué** de cada cosa y cubre muchos temas con más profundidad.

## Índice de contenido

1. Descargar e instalar
2. Requisitos: GameMaker es ligero
3. LTS: qué significa y cuándo usarlo
4. Crear el proyecto: la trampa del pixel art
5. GML Code frente a GML Visual
6. Recorrido por el IDE: menú y barra de herramientas
7. El manual oficial
8. No necesitas cuenta (casi nunca)
9. Plataformas de destino
10. Ventanas de salida
11. El navegador de recursos y el inspector
12. Convenciones de nombres
13. Sprites: el editor de imagen y los subimages
14. Objetos, sprites asignados y eventos
15. El editor de rooms: poner algo en pantalla
16. Cómo continuar la serie

---

## 1. Descargar e instalar

**GameMaker es gratis.** Solo tienes que pagar a YoYo Games si quieres **vender** tu
juego. Es así de sencillo.

Se descarga desde **gamemaker.io**, en la sección de descargas. Hay versiones para
**Windows**, **macOS** y **Linux**.

> **Sobre Linux:** oficialmente solo se soporta **Ubuntu**. Puedes probar suerte con
> otras distribuciones… «a veces funciona y a veces explota espectacularmente».

También existe en **Steam** y es básicamente el mismo producto, pero el autor evita
esa vía para no añadir complicaciones.

---

## 2. Requisitos: GameMaker es ligero

> GameMaker no se parece en nada a Unreal Engine o Unity. Está más cerca de
> **RPG Maker o Godot** en cuanto a consumo de recursos.

Funciona en prácticamente cualquier equipo:

- CPU de **doble núcleo** o mejor.
- **No necesita tarjeta gráfica** dedicada: va perfecto con gráfica integrada.
- No necesita mucha memoria.

El único consejo general del autor: **instálalo en un disco de estado sólido (SSD)** y
no en uno mecánico. Afecta sobre todo al tiempo que tarda en arrancar.

Su propio equipo es un PC «de lo más normalito» de 2019-2020: un **Ryzen 5 3500** y una
**GTX 1070**.

La primera vez que lo ejecutes verás una pantalla de bienvenida y una barra de progreso
mientras GameMaker **instala sus herramientas de compilación**. Después arrancará mucho
más rápido.

---

## 3. LTS: qué significa y cuándo usarlo

**LTS** son las siglas de *Long Term Support* (soporte a largo plazo). Es una versión
del motor que:

- **No debería cambiar** en varios años.
- Se supone que está **prácticamente libre de errores**.
- Puedes contar con que funciona.

En el momento de grabar el vídeo, la versión actual era **GameMaker 2024.14** y la LTS
vigente tenía ya **tres años**, por lo que le faltaban muchas de las funciones más
recientes. El autor **no la recomendaba**.

> **LTS 2026** estaba prevista para alrededor de **enero de 2026**. Es la que merece la
> pena usar si quieres una versión estable y que no cambie constantemente.

*(Nota: efectivamente, GameMaker LTS 2026 se publicó en 2026 y es la versión estable
actual, IDE 2026.0.0.16 / Runtime 2026.0.0.23.)*

---

## 4. Crear el proyecto: la trampa del pixel art

En la pantalla de inicio verás material de aprendizaje, un asistente de primera
configuración y la lista de proyectos recientes. El autor cierra el asistente y lo hace
a mano.

Al pulsar **New** se elige el tipo de proyecto:

| Tipo | Interés |
|---|---|
| **Game** | El que nos importa |
| Live Wallpaper | Otros productos de Opera (empresa matriz) |
| Game Strip | Ídem |

Después aparecen las plantillas. Hay dos opciones de juego en blanco:

- **Blank game**
- **Blank pixel game**

> **Diferencia:** hay **un único ajuste** que afecta a cómo se escalan los gráficos al
> dibujarse en pantalla, y **tiende a estropear el pixel art**.

Es tan habitual que la gente llegue al subreddit, al Discord o al foro quejándose de que
su pixel art se ve fatal sin saber por qué, que el autor tiene «cierta cuenta pendiente»
con YoYo Games por no ponerlo como opción por defecto, sabiendo que la mayoría usa
GameMaker para pixel art.

- Si vas a hacer **pixel art** (alrededor del 90 % de la gente), elige **Blank pixel
  game**.
- Puedes cambiar el ajuste en cualquier momento desde **Game Options**.
- Por lo demás, **no hay ninguna otra diferencia**.

Elige también el lenguaje de script: **GML Code**.

---

## 5. GML Code frente a GML Visual

> «Ojalá GML Visual fuera mejor. Sería muy útil tener un sistema de scripting visual
> realmente bueno… pero desafortunadamente no lo es.»

No parece que vaya a mejorar a corto plazo, así que se usa **GML Code**.

El autor anima a no tenerle miedo al código:

- **GML** es bastante parecido a **JavaScript**.
- Y si no has programado nunca, no pasa nada: se llega.

Al pulsar **Let's Go**, GameMaker crea el proyecto y muestra la **pestaña de bienvenida**
(*Welcome*), que hace un recorrido por el IDE. Puedes cerrarla con la **X** o con
**clic central** sobre la pestaña.

---

## 6. Recorrido por el IDE: menú y barra de herramientas

**IDE** = *Integrated Development Environment* (entorno de desarrollo integrado).

### Barra de menús (arriba a la izquierda)

Menús tradicionales: **File** (guardar, abrir, nuevo proyecto…), herramientas y
acciones.

### Barra de iconos

Botones de acceso rápido: **Home** (cerrar proyecto y volver al inicio), **New
project**, **Open project**, **Save project**, **Build executable**.

Los **cuatro botones más usados** de toda la barra:

| Botón | Función |
|---|---|
| **Debug** | Ejecutar con depurador |
| **Run** | Ejecutar el juego |
| **Stop** | Detenerlo |
| **Clean** | Limpiar la caché del compilador |

> **F5** es el atajo de teclado de **Run**. Si pasas un tiempo haciendo esto, te
> cansarás de mover el ratón hasta el botón: **F5 se convertirá en tu mejor amigo.**

Después vienen **Game Options** (ajustes del juego, incluido el del pixel art) y el icono
de ayuda.

---

## 7. El manual oficial

Desde el menú **Help → Open manual** se abre la documentación oficial.

> La documentación de GameMaker es **bastante buena en general**. Algunas páginas están
> incompletas, pero **si querías un «libro de texto» de GameMaker, esto es lo más
> parecido que vas a encontrar**.

El autor recomienda usar el **manual online**, porque se actualiza periódicamente. Y
añade que mucha gente se lo lee de cabo a rabo y le saca mucho valor.

---

## 8. No necesitas cuenta (casi nunca)

Puedes iniciar sesión con una cuenta de **Opera** (la empresa propietaria de GameMaker,
sí, la del navegador) o con una cuenta antigua de GameMaker.

- Puedes usar **aproximadamente el 95 % del motor sin iniciar sesión**.
- Solo importa de verdad cuando quieras **distribuir** tu juego.
- El autor graba toda la serie **sin iniciar sesión**, en parte por principios y en
  parte porque no se acuerda de su contraseña.

---

## 9. Plataformas de destino

Al pulsar el botón de **target** verás las plataformas disponibles. Sin iniciar sesión
siempre tendrás dos:

| Plataforma | Qué es |
|---|---|
| **gx.games** | Juego web, al estilo de los viejos juegos de Flash |
| **Test** | La plataforma por defecto de tu sistema (Windows, Linux…) |

Si inicias sesión tendrás muchas más: otros sistemas operativos, móvil y varias
consolas (si tienes cuenta de desarrollador).

Junto a eso hay una pegatina con la versión actual del **IDE** y del **runtime** (las
herramientas de compilación).

---

## 10. Ventanas de salida

Abajo hay varias pestañas de salida:

| Pestaña | Contenido |
|---|---|
| **Output** | Mensajes de estado al ejecutar el juego (la más útil) |
| **Search Results** | Resultados de búsqueda |
| **Compile Errors** | Errores de compilación |

Las demás son más especializadas y se verán más adelante.

---

## 11. El navegador de recursos y el inspector

A la derecha está el **asset browser** (navegador de recursos).

- Incluye una barra de **Quick Access** abierta por defecto que el autor recomienda
  **plegar**: suele ser mejor uso del espacio otra cosa. Es útil en proyectos grandes
  para marcar favoritos.
- Al crear un proyecto desde cero, el único recurso es **`Room1`**.

### Rooms

> Las **rooms** son básicamente los **niveles** de GameMaker: los escenarios donde vive
> todo lo que ves cuando el juego está en marcha.

A la izquierda está el **inspector**, que muestra las propiedades de lo que tengas
seleccionado: el tamaño de la room, por ejemplo, y otros ajustes avanzados.

### Tipos de recurso

Clic derecho en el navegador → **Create** da acceso a todos. Los más importantes:

| Recurso | Qué es |
|---|---|
| **Objects** | Una **entidad del juego que hace cosas** y a la que le pueden pasar cosas (el jugador, por ejemplo) |
| **Sprites** | Prácticamente **todos los recursos gráficos** del juego |
| Rooms | Los niveles |

También hay fuentes, scripts, shaders y más, pero al principio te moverás sobre todo
entre rooms, objetos y sprites.

### Grupos

Puedes crear **grupos**, que son básicamente **carpetas**, y organizar como quieras
(por ejemplo, `Player Stuff`).

---

## 12. Convenciones de nombres

> Las tradiciones de nomenclatura en GameMaker son «un tema de acalorado debate».

La convención **más común**:

| Tipo | Ejemplo |
|---|---|
| Objeto | `obj_player` |
| Sprite | `spr_player` |
| Room | `rm_level1` |

Otras variantes: usar mayúsculas en vez de guion bajo (`objPlayer`), o abreviaturas de
una sola letra (`oPlayer`).

> **No importa cuál uses.** GameMaker **no impone ninguna guía de estilo**. Lo único que
> importa es que **tú seas capaz de encontrar lo que buscas**.

---

## 13. Sprites: el editor de imagen y los subimages

Para dar contenido a un sprite, pulsa **Edit Image**. Se abre un editor de imagen
sencillo. El autor dibuja un relleno amarillo con una cara sonriente: ese será el
jugador.

Si ya tienes un sprite hecho, usa **Import** para cargarlo desde tu disco.

### Subimages

> Los sprites pueden contener **varias imágenes**. Se usa sobre todo para
> **animación**.

En el editor, el botón **+** añade imágenes al sprite. El autor añade una segunda con
relleno azul y una cara triste, y luego la elimina.

También puedes **importar una secuencia** de sprites de una vez.

---

## 14. Objetos, sprites asignados y eventos

Cada objeto puede tener **un sprite asignado**. La forma más cómoda es **arrastrar el
sprite desde el navegador de recursos** hasta la casilla correspondiente del objeto.

### La ventana de eventos

Los **eventos** son cosas que le ocurren al objeto y que este procesa. Pulsa **Add
Event** (o clic derecho dentro de la ventana) y verás la lista completa. Los más
cotidianos:

| Evento | Cuándo se ejecuta |
|---|---|
| **Create** | Cuando el objeto se crea |
| **Step** | **Cada fotograma** del juego; para código que se ejecuta continuamente |

Al añadir el primer evento, GameMaker vuelve a preguntar si quieres **GML Code** o
**GML Visual** (aunque ya lo elegiste al crear el proyecto). Elige **GML Code** y marca
**«don't ever ask again»**.

Se abre un editor de texto donde escribirás **gran parte del código de tu juego**.

---

## 15. El editor de rooms: poner algo en pantalla

Abre el editor de rooms: verás una **cuadrícula**, y puedes hacer zoom y desplazarte.
Si has usado algún editor de imágenes, los controles te resultarán familiares.

### Capas

Las rooms tienen **capas** de distintos tipos:

- **Background layer:** un color de relleno sólido.
- **Instance layer:** viene por defecto; aquí viven las instancias.

Para añadir una instancia, **arrastra el objeto desde el navegador de recursos hasta el
editor de la room**.

> El autor recuerda lo malo que era esto en versiones antiguas (él empezó en 2011). Con
> la versión moderna (2016-2017) el editor de rooms se renovó por completo y se quedó
> flipando: «¿o sea que puedo hacer esto y ya está?».

### Objetos frente a instancias

> La distinción entre un **objeto** y una **instancia** de un objeto es bastante
> importante, y la serie volverá sobre ella muchas veces.

Además, no solo los objetos tienen propiedades: **las instancias dentro de una room
también pueden tener las suyas**, que verás en el inspector al seleccionarlas.

### El «hola mundo» de los juegos

Ejecuta con **Build → Run**, con el botón de *play* o con **F5**. Aparecerá una ventana
con tu cara sonriente en medio de la room. No hace nada ni se mueve, porque aún no hay
código.

> Pero eso es esencialmente **el «hola mundo» de los juegos**: conseguir que algo
> aparezca en pantalla.

---

## 16. Cómo continuar la serie

El autor lleva años haciendo vídeos de GameMaker, unos muy accesibles y otros bastante
más complejos (sobre todo de 3D).

Su consejo: **ve paso a paso** y no te lances directamente a lo complicado.

Para ayudarte a orientarte, **las miniaturas de sus vídeos están codificadas por
colores**:

| Color | Contenido |
|---|---|
| **Rojo** | Normalmente cosas de **3D** |
| **Gris / plateado** | Funciones **beta** añadidas recientemente al motor |

Esta serie de iniciación tiene su propio color, así que de un vistazo sabrás qué
vídeos pertenecen a qué categoría (iniciación, avanzado, *lets plays*…). Y por supuesto
están **recopilados en una lista de reproducción** para verlos en orden.

---

## Puntos clave

1. **GameMaker es gratis** salvo que quieras vender el juego.
2. **Es muy ligero:** funciona con doble núcleo, gráfica integrada y poca memoria. Mejor
   en SSD.
3. **LTS** = versión estable que no cambia en años. La **LTS 2026** es la recomendable.
4. **Si haces pixel art, elige la plantilla «Blank pixel game»**: evita el escalado que
   lo estropea.
5. **Usa GML Code, no GML Visual.**
6. **La documentación oficial es excelente**: es lo más parecido a un libro de texto del
   motor.
7. **F5 ejecuta el juego.** Será tu atajo más usado.
8. **No hace falta iniciar sesión** para el 95 % del motor.
9. **Rooms = niveles. Objects = entidades que hacen cosas. Sprites = gráficos.**
10. **Usa grupos (carpetas)** para organizar.
11. **No hay convención de nombres obligatoria**: elige una y sé constante.
12. **Los sprites pueden tener varios subimages** para animación.
13. **Arrastra objetos desde el navegador de recursos al editor de rooms** para colocar
    instancias.
14. **Objeto ≠ instancia.** La serie insistirá en esto.

---

## Ejercicio propuesto

> **Objetivo:** reproducir el «hola mundo» y dejar el proyecto bien configurado desde el
> principio.

1. Descarga GameMaker desde **gamemaker.io** e instálalo. Comprueba qué versión de IDE
   y runtime aparece en la pegatina de la esquina.
2. Crea un proyecto nuevo de tipo **Game** con la plantilla **Blank pixel game** y
   lenguaje **GML Code**. Ponle un nombre con la convención `tutorial AAMMDD V1`.
3. Cierra la pestaña de bienvenida y la barra de **Quick Access**.
4. Abre **Help → Open manual** y navega cinco minutos por la documentación. Localiza la
   página de `place_meeting` leyendo el índice, sin usar el buscador.
5. Crea el grupo `Sprites` y dentro un sprite `spr_player`. Dibuja algo con **Edit
   Image** (un círculo amarillo con ojos vale).
6. Añade **un segundo subimage** con el botón `+`, comprueba que aparecen dos
   fotogramas, y después bórralo.
7. Crea el grupo `Objects` y el objeto `obj_player`. **Arrastra** el sprite desde el
   navegador de recursos hasta su casilla de sprite.
8. Añade un evento **Create** y, cuando pregunte, elige **GML Code** y marca «don't ever
   ask again».
9. Abre `Room1` y arrastra `obj_player` al centro.
10. Ejecuta con **F5** (no con el ratón). Repítelo hasta que el atajo te salga solo.
11. Comprueba las tres pestañas de salida: **Output**, **Search Results** y **Compile
    Errors**.
12. Abre **Game Options** y localiza el ajuste de escalado de gráficos que diferencia
    las dos plantillas de juego en blanco. Anota dónde está.

**Reto extra:** sin iniciar sesión, pulsa el botón de **target** y anota qué plataformas
ves disponibles. Explica con tus palabras en qué situación concretas necesitarías iniciar
sesión.
